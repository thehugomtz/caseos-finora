"""Las tools de la slice, expuestas al agente como servidor MCP en proceso (Agent SDK).

Principios (arquitectura v1.2 §4): toda tool que calcula registra evidencia sola; devuelve resúmenes compactos;
los errores son tipados y traen pista; ninguna tool acepta cifras escritas por el agente como dato.
"""
from __future__ import annotations

import json
import re
import threading

import sqlglot
import yaml
from claude_agent_sdk import ToolAnnotations, create_sdk_mcp_server, tool
from sqlglot import exp

from . import analytics, semantic, visuals
from .config import ANALYSIS_BUDGET, BRAIN, MAX_TOOL_CALLS, SQL_ROW_LIMIT, SQL_TIMEOUT_S
from .render import fmt_value
from .state import Investigation, now_ms
from .validator import ISSUES, MISSING, PLAYBOOKS, norm, validate_claim, validate_hypotheses

SERVER = "finora"
TOOL_NAMES = ["brain_lookup", "search_evidence", "query_metric", "run_sql", "run_analysis",
              "upsert_hypotheses", "propose_claim", "propose_visual"]
ALLOWED_TOOLS = [f"mcp__{SERVER}__{n}" for n in TOOL_NAMES]
SQL_TABLES = {"customer_month", "monthly_metrics", "new_customers", "vintage_month", "churn_events", "sm_monthly"}
RO = ToolAnnotations(readOnlyHint=True, maxResultSizeChars=60_000)
RW = ToolAnnotations(readOnlyHint=False, maxResultSizeChars=60_000)


def _load(rel):
    return yaml.safe_load((BRAIN / rel).read_text(encoding="utf-8"))


METRICS = {m["id"]: m for m in _load("semantic/metrics.yaml")["metrics"]}
CANON = {h["id"]: h for h in _load("evidence/canonical_findings.yaml")["hallazgos"]}
EPISTEMIC = _load("guardrails/epistemic_rules.yaml")
GLOSSARY = _load("semantic/glossary_es.yaml")


def _ok(text: str) -> dict:
    return {"content": [{"type": "text", "text": text}]}


def _err(text: str) -> dict:
    return {"content": [{"type": "text", "text": "ERROR · " + text}], "is_error": True}


def table_text(cols, rows, max_rows=36) -> str:
    head = [c["nombre"] for c in cols]
    lines = [" | ".join(head)]
    shown = rows if len(rows) <= max_rows else rows[:6] + [None] + rows[-(max_rows - 7):]
    for r in shown:
        if r is None:
            lines.append(f"… ({len(rows) - max_rows + 1} filas omitidas) …")
            continue
        cells = []
        for c in cols:
            v = r.get(c["id"])
            cells.append(fmt_value(v, c.get("formato", "texto")) if not isinstance(v, str) else v)
        lines.append(" | ".join(cells))
    return "\n".join(lines)


def claves_text(ev, limit=60, only_scalars=False) -> str:
    vals, fmts = ev.result.get("valores", {}), ev.result.get("formatos", {})
    keys = [k for k in vals if not only_scalars or "[" not in k]
    shown = keys[:limit]
    labels = ev.result.get("etiquetas", {})
    body = "\n".join(f"  {ev.id}.{k} = {fmt_value(vals[k], fmts.get(k, 'texto'))}" + (f"  ({labels[k]})" if k in labels else "")
                     for k in shown)
    more = f"\n  … y {len(keys) - limit} claves más con el mismo patrón." if len(keys) > limit else ""
    return body + more


def make_server(inv: Investigation, con):
    """Crea el servidor MCP con las tools ligadas a una investigación y a una conexión de solo lectura."""

    def start(name: str, args: dict):
        inv.tool_calls += 1
        entry = {"n": len(inv.log) + 1, "t": now_ms() - inv.started_ms, "tool": name,
                 "params": args, "ok": None, "evidencias": [], "resumen": None, "error": None}
        inv.log.append(entry)
        inv.emit("tool", {"tool": name, "n": entry["n"], "params": args})
        return entry

    def fail(entry, msg: str) -> dict:
        entry["ok"], entry["error"] = False, msg
        inv.emit("tool_error", {"n": entry["n"], "tool": entry["tool"], "error": msg})
        return _err(msg)

    def guard_analysis(entry):
        if inv.tool_calls > MAX_TOOL_CALLS:
            return fail(entry, "Se alcanzó el tope de llamadas. Cierra la investigación con lo que tienes.")
        if not inv.hipotesis:
            return fail(entry, "Primero registra el árbol de hipótesis con sus firmas (upsert_hypotheses). "
                               "Pre-registrar evita buscar hasta encontrar apoyo.")
        if inv.budget_used >= ANALYSIS_BUDGET:
            return fail(entry, f"Presupuesto de análisis agotado ({ANALYSIS_BUDGET} llamadas). Cierra con lo que "
                               "tienes: propone afirmaciones y deja lo demás como pendiente.")
        inv.budget_used += 1
        inv.set_status("evidencia")
        return None

    def evidence_event(entry, ev, resumen):
        entry["evidencias"].append(ev.id)
        inv.emit("evidencia", {"id": ev.id, "tool": ev.tool, "metodo": ev.method, "variante": ev.variant,
                               "resumen": resumen, "marcador": ev.marker, "canonica": ev.canonical})

    # ------------------------------------------------------------------ brain_lookup
    @tool("brain_lookup", "Consulta el cerebro de negocio por ID o por tema: métricas del catálogo (p. ej. "
          "'mrr_per_active_customer_cop'), problemas de datos ('CV-AMOUNT-COBRO'), playbooks ('arpa_decline'), "
          "hallazgos canónicos ('C-MON-04'), 'missing_data', 'epistemic_rules' o 'glosario'. Solo lectura.",
          {"type": "object", "properties": {
              "ids": {"type": "array", "items": {"type": "string"}, "description": "IDs exactos a recuperar"},
              "tema": {"type": "string", "description": "Texto libre para buscar en métricas, problemas y hallazgos"}},
           "additionalProperties": False}, annotations=RO)
    async def brain_lookup(args):
        entry = start("brain_lookup", args)
        ids, tema = args.get("ids") or [], (args.get("tema") or "").strip()
        if not ids and not tema:
            return fail(entry, "Indica 'ids' o 'tema'.")
        out = []
        for i in ids:
            if i in METRICS:
                m = METRICS[i]
                out.append(f"[métrica {i}] {m['nombre']}: {m['definicion']} Fórmula: {m['formula']}. Grano: {m['grano']}. "
                           f"Unidad: {m['unidad']}. Ventana: {m['ventana']}. Precauciones: {', '.join(m.get('caveats', [])) or '—'}.")
            elif i in ISSUES:
                x = ISSUES[i]
                out.append(f"[problema {i}] {x['titulo']} ({x['estado']}). {x['descripcion']} Tratamiento: {x['tratamiento']}")
            elif i in PLAYBOOKS:
                out.append(f"[playbook {i}]\n" + yaml.safe_dump(PLAYBOOKS[i], allow_unicode=True, sort_keys=False))
            elif i in CANON:
                h = CANON[i]
                out.append(f"[hallazgo canónico {i}] ({h['estado']}) {h['afirmacion']} Evidencia: {h['evidencia']}")
            elif i == "missing_data":
                out.append("[datos faltantes] " + "; ".join(f"{k}: {v['nombre']}" for k, v in MISSING.items()))
            elif i == "epistemic_rules":
                out.append("[reglas epistémicas]\n" + yaml.safe_dump(EPISTEMIC, allow_unicode=True, sort_keys=False))
            elif i == "glosario":
                out.append("[glosario]\n" + yaml.safe_dump(GLOSSARY.get("terminos", {}), allow_unicode=True, sort_keys=False))
            else:
                out.append(f"[{i}] no existe en el cerebro.")
        if tema:
            toks = [t for t in norm(tema).split() if len(t) > 3]
            scored = []
            for i, m in METRICS.items():
                scored.append((sum(t in norm(m["nombre"] + " " + m["definicion"]) for t in toks), f"métrica {i}: {m['nombre']}"))
            for i, x in ISSUES.items():
                scored.append((sum(t in norm(x["titulo"] + " " + x["descripcion"]) for t in toks), f"problema {i}: {x['titulo']}"))
            for i, h in CANON.items():
                scored.append((sum(t in norm(h["afirmacion"]) for t in toks), f"hallazgo {i}: {h['afirmacion']}"))
            best = [s for sc, s in sorted(scored, key=lambda z: -z[0]) if sc > 0][:10]
            out.append("[resultados para '" + tema + "']\n" + ("\n".join(best) if best else "sin coincidencias"))
        text = "\n\n".join(out)[:7000]
        entry["ok"], entry["resumen"] = True, f"{len(ids)} IDs" + (f" · tema '{tema}'" if tema else "")
        return _ok(text)

    # ------------------------------------------------------------------ search_evidence
    @tool("search_evidence", "Busca evidencia canónica reutilizable (afirmaciones de la Fase 1 verificadas en código) "
          "por texto. Registra cada resultado como evidencia EC-… que puedes ligar en afirmaciones. Nivel 1 de la escalera.",
          {"type": "object", "properties": {
              "texto": {"type": "string", "description": "Qué buscas, en palabras"},
              "ids": {"type": "array", "items": {"type": "string"}, "description": "IDs canónicos exactos, p. ej. ['C-ADQ-05']"},
              "dominio": {"type": "string", "description": "Opcional: Resultado, Adquisición, Retención, Monetización de la base, Inversión comercial, Calidad de datos"}},
           "additionalProperties": False}, annotations=RO)
    async def search_evidence(args):
        entry = start("search_evidence", args)
        ids = [i for i in (args.get("ids") or [])]
        bad = [i for i in ids if i not in CANON]
        if bad:
            return fail(entry, f"IDs canónicos inexistentes {bad}. Revisa el índice del núcleo del cerebro.")
        toks = [t for t in norm(args.get("texto", "")).split() if len(t) > 3]
        if not ids and not toks:
            return fail(entry, "Indica 'texto' o 'ids'.")
        dom = norm(args.get("dominio") or "")
        scored = []
        for cid, h in CANON.items():
            s = sum(t in norm(h["afirmacion"]) for t in toks) + (2 if dom and dom in norm(h["dominio"]) else 0)
            if s > 0 and cid not in ids:
                scored.append((s, cid))
        scored.sort(key=lambda z: -z[0])
        out = []
        for cid in ids + [c for _, c in scored[:max(0, 6 - len(ids))]]:
            h = CANON[cid]
            ev = inv.registry.add(
                kind="canonical", tool="search_evidence", params={"claim_id": cid},
                method="Afirmación canónica verificada en código (Fase 1)", variant=None,
                query_text=None, code="finora_eda.py · check_claims() → brain/evidence/canonical_findings.yaml",
                result={"afirmacion": h["afirmacion"], "valores": dict(h["evidencia"]),
                        "formatos": {k: "texto" for k in h["evidencia"]}, "etiquetas": dict(h.get("etiquetas") or {}),
                        "columnas": [{"id": "clave", "nombre": "Dato"}, {"id": "que_mide", "nombre": "Qué mide"},
                                     {"id": "valor", "nombre": "Valor"}],
                        "filas": [{"clave": k, "que_mide": (h.get("etiquetas") or {}).get(k, ""), "valor": v}
                                  for k, v in h["evidencia"].items()], "notas": []},
                ceiling=h["estado"] if h["estado"] in ("Hecho observado", "Evidencia fuerte", "Direccional") else "Hipótesis",
                canonical=True, fixed_id="EC-" + cid[2:])
            evidence_event(entry, ev, h["afirmacion"])
            out.append(f"{ev.id} · {h['estado']} · {h['afirmacion']}\n" + claves_text(ev))
        entry["ok"] = True
        entry["resumen"] = f"{len(out)} hallazgos canónicos"
        return _ok("\n\n".join(out) if out else "Sin evidencia canónica para ese texto. Calcula con query_metric o run_analysis.")

    # ------------------------------------------------------------------ query_metric
    @tool("query_metric", "Calcula una métrica del catálogo con el grano, periodo, filtros, cortes y comparación que "
          "elijas. El código escribe el SQL y aplica las reglas de la métrica (ventana limpia, no comparables, "
          "precauciones). Nivel 2 de la escalera. Cuenta para el presupuesto de análisis.",
          {"type": "object", "properties": {
              "metric_id": {"type": "string", "enum": sorted(semantic.SPECS)},
              "grano": {"type": "string", "enum": list(semantic.GRAINS), "default": "month"},
              "periodo": {"type": "object", "properties": {"desde": {"type": "string", "pattern": "^20[0-9]{2}-[0-9]{2}$"},
                                                           "hasta": {"type": "string", "pattern": "^20[0-9]{2}-[0-9]{2}$"}},
                          "additionalProperties": False},
              "filtros": {"type": "object", "properties": {"industry": {"type": "array", "items": {"type": "string"}},
                                                           "vintage": {"type": "array", "items": {"type": "string"}}},
                          "additionalProperties": False},
              "cortes": {"type": "array", "items": {"type": "string", "enum": list(semantic.DIMS)}, "maxItems": 1},
              "comparacion": {"type": "string", "enum": list(semantic.COMPARES), "default": "none"}},
           "required": ["metric_id"], "additionalProperties": False}, annotations=RO)
    async def query_metric(args):
        entry = start("query_metric", args)
        g = guard_analysis(entry)
        if g:
            return g
        per = args.get("periodo") or {}
        try:
            res = semantic.compile_and_run(con, args["metric_id"], grain=args.get("grano", "month"),
                                           period={"from": per.get("desde", "2022-01"), "to": per.get("hasta", "2024-10")},
                                           filters=args.get("filtros"), group_by=args.get("cortes"),
                                           compare=args.get("comparacion", "none"), catalog=METRICS)
        except semantic.MetricError as e:
            inv.budget_used -= 1
            return fail(entry, str(e))
        ev = inv.registry.add(
            kind="metric", tool="query_metric", params=args, method=f"Métrica del catálogo · {res['label']}",
            variant=args.get("comparacion", "none"), query_text=res["sql"],
            code="agent/semantic.py · compile_and_run() sobre mart.customer_month",
            result={k: res[k] for k in ("columnas", "filas", "valores", "formatos", "notas", "label", "kind")},
            metric_ids=[args["metric_id"]], caveat_ids=res["caveats"], ceiling="Hecho observado",
            no_comparable=res["no_comparable"])
        resumen = f"{res['label']} · grano {args.get('grano', 'month')} · {len(res['filas'])} filas"
        evidence_event(entry, ev, resumen)
        entry["ok"], entry["resumen"] = True, resumen
        notas = ("\nNotas: " + " ".join(res["notas"])) if res["notas"] else ""
        cav = ("\nPrecauciones: " + ", ".join(res["caveats"])) if res["caveats"] else ""
        nc = ("\nNO COMPARABLES (no se pueden ligar): " + ", ".join(res["no_comparable"])) if res["no_comparable"] else ""
        return _ok(f"{ev.id} · {resumen}{notas}{cav}{nc}\n\n{table_text(res['columnas'], res['filas'])}\n\n"
                   f"Claves ligables (usa {ev.id}.<clave> en variables):\n{claves_text(ev)}")

    # ------------------------------------------------------------------ run_sql
    @tool("run_sql", "SQL de solo lectura sobre el mart (DuckDB) para combinar vistas o crear una nueva cuando "
          f"query_metric no alcanza. Tablas: {', '.join('mart.' + t for t in sorted(SQL_TABLES))}. Máximo "
          f"{SQL_ROW_LIMIT} filas. Nivel 3: el resultado lleva el marcador Cálculo ad hoc y techo Direccional.",
          {"type": "object", "properties": {"sql": {"type": "string"}, "proposito": {"type": "string"}},
           "required": ["sql", "proposito"], "additionalProperties": False}, annotations=RO)
    async def run_sql(args):
        entry = start("run_sql", args)
        g = guard_analysis(entry)
        if g:
            return g
        sql = args["sql"].strip().rstrip(";")
        problem = check_sql(sql)
        if problem:
            inv.budget_used -= 1
            return fail(entry, problem)
        timer = threading.Timer(SQL_TIMEOUT_S, con.interrupt)
        timer.start()
        try:
            df = con.execute(f"SELECT * FROM ({sql}) AS q LIMIT {SQL_ROW_LIMIT + 1}").df()
        except Exception as e:  # noqa: BLE001 - el error vuelve al agente como dato
            inv.budget_used -= 1
            return fail(entry, f"El SQL falló: {str(e)[:400]}")
        finally:
            timer.cancel()
        if len(df) > SQL_ROW_LIMIT:
            inv.budget_used -= 1
            return fail(entry, f"El resultado supera {SQL_ROW_LIMIT} filas: agrega o filtra.")
        cols = [{"id": c, "nombre": c, "formato": "num2" if df[c].dtype.kind == "f" else ("int" if df[c].dtype.kind in "iu" else "texto")}
                for c in df.columns]
        filas = json.loads(df.to_json(orient="records", force_ascii=False))
        valores, formatos = {}, {}
        first = df.columns[0]
        unique = df[first].is_unique
        for i, f in enumerate(filas):
            rk = str(f[first]) if unique else str(i)
            for c in cols[1:]:
                v = f.get(c["id"])
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    valores[f"{c['id']}[{rk}]"] = float(v)
                    formatos[f"{c['id']}[{rk}]"] = c["formato"]
        ev = inv.registry.add(
            kind="sql", tool="run_sql", params=args, method="SQL ad hoc de solo lectura", variant=None, query_text=sql,
            code="agent/tools.py · run_sql() con rol de solo lectura", ceiling="Direccional", marker="Cálculo ad hoc",
            result={"columnas": cols, "filas": filas, "valores": valores, "formatos": formatos,
                    "notas": ["Cálculo ad hoc: techo Direccional hasta reconciliarlo contra una métrica del catálogo."]},
            n=len(df))
        resumen = f"SQL ad hoc · {len(df)} filas · {args['proposito'][:80]}"
        evidence_event(entry, ev, resumen)
        entry["ok"], entry["resumen"] = True, resumen
        return _ok(f"{ev.id} · {resumen} · marcador Cálculo ad hoc (techo Direccional)\n\n{table_text(cols, filas)}\n\n"
                   f"Claves ligables:\n{claves_text(ev)}")

    # ------------------------------------------------------------------ run_analysis
    catalog_desc = "; ".join(f"{k}: {v['descripcion']} Parámetros: {v['params'] or 'ninguno'}" for k, v in analytics.CATALOG.items())

    @tool("run_analysis", "Ejecuta un análisis del catálogo cerrado. Cada variante queda como una evidencia distinta. "
          "Cuenta para el presupuesto de análisis. Catálogo: " + catalog_desc,
          {"type": "object", "properties": {"analysis_id": {"type": "string", "enum": list(analytics.CATALOG)},
                                            "params": {"type": "object"}},
           "required": ["analysis_id"], "additionalProperties": False}, annotations=RO)
    async def run_analysis(args):
        entry = start("run_analysis", args)
        g = guard_analysis(entry)
        if g:
            return g
        aid, params = args["analysis_id"], args.get("params") or {}
        try:
            payloads = analytics.run(con, aid, params)
        except analytics.AnalysisError as e:
            inv.budget_used -= 1
            return fail(entry, str(e))
        texts = []
        for p in payloads:
            ev = inv.registry.add(
                kind="analysis", tool="run_analysis", params={"analysis_id": aid, **p["params"]}, method=p["method"],
                variant=p["variant"], query_text=f"run_analysis('{aid}', {json.dumps(p['params'], ensure_ascii=False)})",
                code=p["code"], result={k: p[k] for k in ("columnas", "filas", "valores", "formatos", "notas")},
                caveat_ids=p["caveats"], n=p["n"], robustness=p["robustez"], ceiling="Hecho observado")
            resumen = f"{aid} · {p['variant']}"
            evidence_event(entry, ev, resumen)
            scal = claves_text(ev, only_scalars=True)
            texts.append(f"{ev.id} · {p['method']} · variante: {p['variant']} · n = {p['n']}\n"
                         f"Notas: {' '.join(p['notas'])}\nPrecauciones: {', '.join(p['caveats']) or '—'}\n"
                         f"Robustez: {json.dumps(p['robustez'], ensure_ascii=False)}\n\n"
                         f"{table_text(p['columnas'], p['filas'])}\n\nCifras principales:\n{scal or '  (ver tabla)'}\n"
                         f"Claves por fila con el patrón {ev.id}.<columna>[<fila>], p. ej.:\n{claves_text(ev, limit=8)}")
        entry["ok"], entry["resumen"] = True, f"{aid} · {len(payloads)} evidencia(s)"
        return _ok("\n\n———\n\n".join(texts))

    # ------------------------------------------------------------------ upsert_hypotheses
    @tool("upsert_hypotheses", "Registra el encuadre y el árbol MECE de hipótesis, cada una como pregunta, con su nodo "
          "del playbook y su firma esperada (qué veríamos si es cierta y si es falsa) ANTES de mirar resultados. "
          "Envía siempre el árbol completo. Las firmas no se pueden cambiar después de reunir evidencia; puedes agregar "
          "ramas nuevas. Los estados los deriva el código desde las afirmaciones.",
          {"type": "object", "properties": {
              "encuadre": {"type": "object", "properties": {
                  "pregunta_analitica": {"type": "string"}, "metricas": {"type": "array", "items": {"type": "string"}},
                  "periodo": {"type": "string"}, "segmentos": {"type": "array", "items": {"type": "string"}},
                  "playbook": {"type": "string"}}, "required": ["pregunta_analitica", "metricas", "periodo", "playbook"]},
              "hipotesis": {"type": "array", "minItems": 1, "items": {"type": "object", "properties": {
                  "id": {"type": "string"}, "padre": {"type": ["string", "null"]}, "pregunta": {"type": "string"},
                  "nodo": {"type": "string"},
                  "firma": {"type": "object", "properties": {"si_es_cierta": {"type": "string"}, "si_es_falsa": {"type": "string"}},
                            "required": ["si_es_cierta", "si_es_falsa"]},
                  "estado_propuesto": {"type": "string"}},
                  "required": ["id", "pregunta", "nodo", "firma"]}}},
           "required": ["hipotesis"], "additionalProperties": False}, annotations=RW)
    async def upsert_hypotheses(args):
        entry = start("upsert_hypotheses", args)
        items = args["hipotesis"]
        enc = args.get("encuadre")
        if not inv.hipotesis and not enc:
            return fail(entry, "El primer registro necesita el encuadre (pregunta analítica, métricas, periodo y playbook).")
        pb = (enc or inv.encuadre or {}).get("playbook", inv.playbook_id)
        errors = validate_hypotheses(items, pb)
        prev = {h["id"]: h for h in inv.hipotesis}
        gathered = any(e["tool"] in ("query_metric", "run_sql", "run_analysis") and e["ok"] for e in inv.log)
        missing = [hid for hid in prev if hid not in {h["id"] for h in items}]
        if missing:
            errors.append(f"No se pueden borrar hipótesis registradas {missing}: se muestran aunque se refuten.")
        for h in items:
            p = prev.get(h["id"])
            if p and gathered and p["firma"] != h["firma"]:
                errors.append(f"{h['id']}: la firma no se puede cambiar después de reunir evidencia.")
        if errors:
            return fail(entry, "Árbol rechazado:\n- " + "\n- ".join(errors))
        if enc:
            inv.encuadre = enc
            inv.playbook_id = pb
            inv.emit("encuadre", enc)
        t = now_ms() - inv.started_ms
        tree = []
        for h in items:
            p = prev.get(h["id"])
            tree.append({"id": h["id"], "padre": h.get("padre"), "pregunta": h["pregunta"], "nodo": h["nodo"],
                         "firma": h["firma"], "estado_propuesto": h.get("estado_propuesto"),
                         "registrada_t": p["registrada_t"] if p else t,
                         "agregada_despues_de_evidencia": p["agregada_despues_de_evidencia"] if p else gathered,
                         "estado": "Pendiente", "estado_motivo": ""})
        inv.hipotesis = tree
        if inv.hipotesis_registradas_ms is None:
            inv.hipotesis_registradas_ms = t
        inv.refresh_hypotheses()
        inv.set_status("hipotesis" if not gathered else inv.status)
        inv.emit("hipotesis", {"hipotesis": inv.hipotesis})
        entry["ok"], entry["resumen"] = True, f"{len(tree)} hipótesis"
        lines = [f"{h['id']} [{h['estado']}] {h['pregunta']} (nodo {h['nodo']})" for h in inv.hipotesis]
        return _ok("Árbol registrado. Estados derivados por el código:\n" + "\n".join(lines))

    # ------------------------------------------------------------------ propose_claim
    @tool("propose_claim", "Propone una afirmación ligada a evidencia. La plantilla va en español y NO lleva cifras: cada "
          "cifra es una variable {nombre} ligada a 'E-004.<clave>' (opcional '|formato': int, cop, cop2, pct, pct0, "
          "pct_signed, num1, num2, x). El validador confirma o degrada el estado y rechaza lenguaje causal. Tipos: "
          "descriptivo, comparativo, asociativo, descomposicion ('explica' solo en descomposicion).",
          {"type": "object", "properties": {
              "plantilla": {"type": "string"},
              "variables": {"type": "object", "additionalProperties": {"type": "string"}},
              "tipo": {"type": "string", "enum": ["descriptivo", "comparativo", "asociativo", "descomposicion"]},
              "estado_propuesto": {"type": "string", "enum": ["Hecho observado", "Evidencia fuerte", "Direccional", "Hipótesis", "No evaluable"]},
              "hipotesis": {"type": "array", "minItems": 1, "items": {"type": "object", "properties": {
                  "id": {"type": "string"}, "postura": {"type": "string", "enum": ["a_favor", "en_contra"]}},
                  "required": ["id", "postura"]}},
              "apoyo": {"type": "array", "items": {"type": "string"}},
              "en_contra": {"type": "array", "items": {"type": "string"}},
              "alcance": {"type": "string"},
              "caveats": {"type": "array", "items": {"type": "string"}},
              "datos_faltantes": {"type": "array", "items": {"type": "string"}},
              "fundamento": {"type": "string"}},
           "required": ["plantilla", "tipo", "estado_propuesto", "hipotesis"], "additionalProperties": False}, annotations=RW)
    async def propose_claim(args):
        entry = start("propose_claim", args)
        if not inv.hipotesis:
            return fail(entry, "Registra primero el árbol de hipótesis.")
        inv.set_status("validacion")
        res = validate_claim(args, inv.registry, {h["id"] for h in inv.hipotesis})
        cid = f"C-{len(inv.claims) + 1:03d}"
        rec = {"id": cid, **{k: args.get(k) for k in ("plantilla", "variables", "tipo", "estado_propuesto", "hipotesis",
                                                     "alcance", "datos_faltantes", "fundamento")}, **res}
        inv.claims[cid] = rec
        inv.refresh_hypotheses()
        if not res["aceptada"]:
            inv.emit("claim_rechazada", {"id": cid, "plantilla": args.get("plantilla"), "motivos": res["motivos"]})
            return fail(entry, f"{cid} rechazada:\n- " + "\n- ".join(res["motivos"]))
        entry["ok"], entry["resumen"] = True, f"{cid} · {res['estado']}"
        inv.emit("claim", {"id": cid, "texto": res["texto"], "estado": res["estado"], "tipo": args["tipo"],
                           "hipotesis": args["hipotesis"], "marcadores": res["marcadores"], "avisos": res["avisos"]})
        inv.emit("hipotesis", {"hipotesis": inv.hipotesis})
        hyp = "; ".join(f"{h['id']} → {h['estado']}" for h in inv.hipotesis)
        av = ("\nAvisos: " + " ".join(res["avisos"])) if res["avisos"] else ""
        return _ok(f"{cid} aceptada · estado {res['estado']}\nTexto: {res['texto']}{av}\n"
                   f"Precauciones: {', '.join(res['caveats']) or '—'}\nHipótesis: {hyp}")

    # ------------------------------------------------------------------ propose_visual
    @tool("propose_visual", "Pide la visualización de una afirmación aceptada. La forma la decide la gramática visual "
          "según la intención: " + "; ".join(f"{k} = {v}" for k, v in visuals.INTENTS.items()) + ". El título es el "
          "texto validado de la afirmación.",
          {"type": "object", "properties": {"claim_id": {"type": "string"},
                                            "intencion": {"type": "string", "enum": list(visuals.INTENTS)},
                                            "evidence_id": {"type": "string"}},
           "required": ["claim_id", "intencion", "evidence_id"], "additionalProperties": False}, annotations=RW)
    async def propose_visual(args):
        entry = start("propose_visual", args)
        c = inv.claims.get(args["claim_id"])
        if not c or not c.get("aceptada"):
            return fail(entry, f"La afirmación {args['claim_id']} no existe o fue rechazada.")
        if args["evidence_id"] not in (c["apoyo"] + c["en_contra"]):
            return fail(entry, f"{args['evidence_id']} no es evidencia de {args['claim_id']}. Usa una de {c['apoyo'] + c['en_contra']}.")
        ev = inv.registry.get(args["evidence_id"])
        try:
            spec = visuals.build(ev, args["intencion"])
        except visuals.VisualError as e:
            return fail(entry, str(e))
        vid = f"V-{len(inv.visuals) + 1:02d}"
        inv.visuals[vid] = {"id": vid, "claim_id": c["id"], "evidence_id": ev.id, "intencion": args["intencion"],
                            "titulo": c["texto"], "spec": spec}
        inv.emit("visual", {"id": vid, "claim_id": c["id"], "tipo": spec["tipo"]})
        entry["ok"], entry["resumen"] = True, f"{vid} · {spec['tipo']}"
        return _ok(f"{vid} creada · forma {spec['tipo']} · título: {c['texto']}")

    tools = [brain_lookup, search_evidence, query_metric, run_sql, run_analysis, upsert_hypotheses, propose_claim, propose_visual]
    return create_sdk_mcp_server(name=SERVER, version="1.0.0", tools=tools), {t.name: t for t in tools}


# ---------------------------------------------------------------------------- guardas de SQL
DENY_FUNCS = re.compile(r"\b(read_\w+|glob|sniff_csv|parquet_\w+|query_table|getenv|pragma_\w+|duckdb_\w+|install|load)\s*\(", re.I)


def check_sql(sql: str) -> str | None:
    try:
        stmts = [s for s in sqlglot.parse(sql, read="duckdb") if s is not None]
    except sqlglot.errors.ParseError as e:
        return f"El SQL no se pudo leer: {str(e)[:300]}"
    if len(stmts) != 1:
        return "Envía una sola consulta SELECT."
    st = stmts[0]
    if not isinstance(st, (exp.Select, exp.Union, exp.Intersect, exp.Except)):
        return "Solo se permiten consultas SELECT (el rol es de solo lectura)."
    for bad in (exp.Insert, exp.Update, exp.Delete, exp.Create, exp.Drop, exp.Alter, exp.Command):
        if st.find(bad):
            return "Solo se permiten consultas SELECT (el rol es de solo lectura)."
    if DENY_FUNCS.search(sql):
        return "Funciones de lectura de archivos o del sistema no permitidas: consulta solo tablas del mart."
    ctes = {c.alias_or_name for c in st.find_all(exp.CTE)}
    for t in st.find_all(exp.Table):
        name, db = t.name, t.db
        if name in ctes and not db:
            continue
        if db != "mart" or name not in SQL_TABLES:
            return f"Tabla no permitida '{t.sql()}'. Usa: {', '.join('mart.' + x for x in sorted(SQL_TABLES))}."
    return None
