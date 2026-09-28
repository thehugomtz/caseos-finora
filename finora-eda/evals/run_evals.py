"""Evaluaciones de la slice (arquitectura v1.2 §12, definición de terminado). No llaman al modelo.

    .venv/bin/python -m evals.run_evals

1. Capa SQL con paridad exacta contra la Fase 1.
2. Reglas de la capa semántica (ventana limpia, no comparables).
3. Validador: cifras a mano, cifras con letras, calificativos, lenguaje causal, techos de estado, No evaluable.
4. Guardas de SQL (solo lectura, solo mart).
5. Investigación dorada Q2: cobertura MECE, estados esperados, cero afirmaciones prohibidas y 100% de cifras
   recalculadas desde la evidencia guardada.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import yaml

from agent import semantic
from agent.config import BRAIN, GOLDEN
from agent.evidence import Evidence, Registry
from agent.tools import check_sql
from agent.validator import (PLAYBOOKS, causal_hits, number_words, qualifiers, stray_digits, validate_claim,
                             validate_composition, validate_hypotheses)
from agent.warehouse import build, connect_ro

RESULTS: list[tuple[str, bool, str]] = []


def check(name: str, cond: bool, detail: str = ""):
    RESULTS.append((name, bool(cond), detail))


def ev(reg: Registry, **kw) -> Evidence:
    base = dict(kind="metric", tool="query_metric", params={}, method="m", result={"valores": {}, "formatos": {}})
    base.update(kw)
    return reg.add(**base)


def sql_layer():
    with tempfile.TemporaryDirectory() as d:
        summary = build(Path(d) / "t.duckdb", verbose=False)
    check("SQL · paridad exacta contra la Fase 1", summary["pruebas_de_paridad"] >= 19, str(summary))


def semantic_rules():
    con = connect_ro()
    r = semantic.compile_and_run(con, "mrr_per_active_customer_cop")
    check("Semántica · MRR por cliente ene-22 = 92.839", round(r["valores"]["valor[2022-01]"]) == 92839)
    r = semantic.compile_and_run(con, "new_customers", compare="yoy", period={"from": "2023-01", "to": "2023-03"})
    check("Semántica · YoY de altas feb-23 vs feb-22 marcado como no comparable", "2023-02" in r["no_comparable"])
    r = semantic.compile_and_run(con, "new_customers", grain="year")
    check("Semántica · los flujos se recortan a la ventana limpia", "CV-VENTANA" in r["caveats"] and r["filas"][0]["meses"] == 10)
    try:
        semantic.compile_and_run(con, "total_sm_spend")
        check("Semántica · métrica fuera de alcance da error tipado", False)
    except semantic.MetricError:
        check("Semántica · métrica fuera de alcance da error tipado", True)


def validator_rules():
    reg = Registry()
    e1 = ev(reg, result={"valores": {"x": 0.97, "y": 0.03}, "formatos": {"x": "pct0", "y": "pct0"}}, ceiling="Hecho observado",
            tool="run_analysis", method="Shapley", variant="M0", kind="analysis", n=800)
    e2 = ev(reg, result={"valores": {"x": 0.96}, "formatos": {"x": "pct0"}}, ceiling="Hecho observado",
            tool="run_analysis", method="Shapley", variant="winsor", kind="analysis", n=800)
    e3 = ev(reg, result={"valores": {"r": -0.57}, "formatos": {"r": "num2"}}, ceiling="Hecho observado")
    e4 = ev(reg, result={"valores": {"variacion[2023-02]": -0.72}, "formatos": {}}, no_comparable=("2023-02",))
    hyp = {"H1", "H1.1"}
    base = {"tipo": "descriptivo", "estado_propuesto": "Hecho observado", "hipotesis": [{"id": "H1", "postura": "a_favor"}]}

    def v(**kw):
        return validate_claim({**base, **kw}, reg, hyp)

    check("Validador · rechaza cifras escritas a mano", not v(plantilla="Cayó 38% en el periodo.")["aceptada"])
    check("Validador · rechaza cifras escritas con letras", not v(plantilla="Bajó en las seis industrias ({x}).",
                                                                      variables={"x": f"{e1.id}.x"})["aceptada"])
    check("Validador · rechaza calificativos sin cifra", not v(plantilla="Bajó en casi todos los meses ({x}).",
                                                                   variables={"x": f"{e1.id}.x"})["aceptada"])
    for verb in ("causaron", "provocó", "generaron", "impulsaron", "debido a", "hizo que", "aumentará"):
        r = v(plantilla=f"El mix {verb} la caída de {{x}}.", variables={"x": f"{e1.id}.x"})
        check(f"Validador · rechaza lenguaje causal ('{verb}')", not r["aceptada"])
    r = v(plantilla="El mix explica {y} de la caída.", variables={"y": f"{e1.id}.y"})
    check("Validador · 'explica' fuera de descomposición se rechaza", not r["aceptada"])
    r = v(plantilla="El mix explica {y} de la caída.", variables={"y": f"{e1.id}.y"}, tipo="descomposicion")
    check("Validador · 'explica' en descomposición se acepta", r["aceptada"], str(r["motivos"]))
    r = v(plantilla="Gasto y altas se asocian con r = {r}.", variables={"r": f"{e3.id}.r"}, tipo="asociativo")
    check("Validador · asociación degradada a Direccional", r["estado"] == "Direccional", str(r))
    r = v(plantilla="Dentro explica {x}.", variables={"x": f"{e1.id}.x"}, tipo="descomposicion", estado_propuesto="Evidencia fuerte",
          apoyo=[e1.id, e2.id])
    check("Validador · Evidencia fuerte con dos variantes se acepta", r["estado"] == "Evidencia fuerte", str(r))
    r = v(plantilla="Dentro explica {x}.", variables={"x": f"{e1.id}.x"}, tipo="descomposicion", estado_propuesto="Evidencia fuerte")
    check("Validador · Evidencia fuerte con una sola evidencia se degrada", r["estado"] == "Hecho observado", str(r))
    r = v(plantilla="El YoY fue {v}.", variables={"v": f"{e4.id}.variacion[2023-02]"})
    check("Validador · rechaza ligar una comparación no comparable", not r["aceptada"])
    e5 = ev(reg, kind="sql", tool="run_sql", result={"valores": {"pct_recuperado[2024]": 4.0, "share[2024]": 1.08},
                                                     "formatos": {"pct_recuperado[2024]": "num2", "share[2024]": "pct0"}})
    r = v(plantilla="Vuelve al nivel previo {p} de la contracción.", variables={"p": f"{e5.id}.pct_recuperado[2024]|pct0"})
    check("Validador · rechaza una participación mayor a 100% fuera de una descomposición", not r["aceptada"], str(r.get("texto")))
    r = v(plantilla="Vuelve al nivel previo {p}% de la contracción.", variables={"p": f"{e5.id}.pct_recuperado[2024]|num1"})
    check("Validador · puntos porcentuales con num1 y % se aceptan", r["aceptada"], str(r["motivos"]))
    r = v(plantilla="La composición explica {s} del cambio.", variables={"s": f"{e5.id}.share[2024]"}, tipo="descomposicion")
    check("Validador · una descomposición puede asignar más de 100% del cambio", r["aceptada"], str(r["motivos"]))
    r = v(plantilla="No hay precios para separarlo.", estado_propuesto="No evaluable")
    check("Validador · No evaluable exige datos faltantes", not r["aceptada"])
    r = v(plantilla="No hay precios para separarlo.", estado_propuesto="No evaluable", datos_faltantes=["precios"])
    check("Validador · No evaluable con datos faltantes se acepta", r["aceptada"], str(r["motivos"]))
    errs = validate_hypotheses([{"id": "H1", "pregunta": "¿Entran más baratos?", "nodo": "entrada",
                                 "firma": {"si_es_cierta": "a", "si_es_falsa": ""}}])
    check("Validador · árbol sin firma y sin cobertura MECE se rechaza",
          any("firma" in e for e in errs) and any("identidad completa" in e for e in errs))
    claims = {"C-1": {"aceptada": True, "texto": "El mix explica 3% de la caída.", "tipo": "descomposicion"}}
    errs = validate_composition({"respuesta_ejecutiva": {"texto": "El mix explica 4% de la caída.", "claim_ids": ["C-1"]},
                                 "hallazgos": [], "limites": [], "implicaciones": [], "proximas_preguntas": []}, claims)
    check("Validador · la narrativa no puede traer cifras que no están en las afirmaciones", any("4" in e for e in errs))


def sql_guards():
    check("SQL · acepta SELECT sobre el mart", check_sql("SELECT vintage, COUNT(*) FROM mart.churn_events GROUP BY 1") is None)
    check("SQL · rechaza escritura", check_sql("DROP TABLE mart.customer_month") is not None)
    check("SQL · rechaza leer archivos", check_sql("SELECT * FROM read_csv('/etc/hosts')") is not None)
    check("SQL · rechaza tablas fuera del mart", check_sql("SELECT * FROM information_schema.tables") is not None)


def golden_q2():
    p = GOLDEN / "Q2.json"
    if not p.exists():
        check("Dorada Q2 · existe", False, "falta investigations/golden/Q2.json")
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    check("Dorada Q2 · publicada", d["status"] == "publicada", d.get("error") or "")
    hyps = d["hipotesis"]
    nodes = {h["nodo"] for h in hyps}
    pb = PLAYBOOKS["arpa_decline"]
    required = [n["id"] for n in pb["nodos"]] + [c["id"] for n in pb["nodos"] for c in n.get("hijos", [])]
    check("Dorada Q2 · el árbol cubre la identidad (entrada, mix, precio, dentro, salida)", all(r in nodes for r in required))
    check("Dorada Q2 · toda hipótesis en estado terminal", all(h["estado"] not in ("Pendiente",) for h in hyps),
          str([(h["id"], h["estado"]) for h in hyps]))
    by_node = {h["nodo"]: h["estado"] for h in hyps}
    check("Dorada Q2 · entrada soportada", by_node.get("entrada") == "Soportada", by_node.get("entrada", ""))
    check("Dorada Q2 · mix de industrias no soportado", by_node.get("entrada.mix_industria") == "No soportada")
    check("Dorada Q2 · precios y descuentos no evaluables", by_node.get("entrada.precio") == "No evaluable")
    first_ev = min((e["t"] for e in d["log"] if e["tool"] in ("query_metric", "run_sql", "run_analysis") and e["ok"]), default=None)
    check("Dorada Q2 · hipótesis registradas antes de la primera evidencia",
          d["hipotesis_registradas_ms"] is not None and first_ev is not None and d["hipotesis_registradas_ms"] <= first_ev)
    # 100% de cifras ligadas: se reconstruye el registro y se vuelve a validar cada afirmación aceptada
    reg = Registry()
    for e in d["evidencia"]:
        e = dict(e)
        for k in ("metric_ids", "caveat_ids", "no_comparable"):
            e[k] = tuple(e[k])
        reg.items[e["id"]] = Evidence(**e)
    hyp_ids = {h["id"] for h in hyps}
    accepted = [c for c in d["claims"].values() if c["aceptada"]]
    mismatch = []
    for c in accepted:
        r = validate_claim(c, reg, hyp_ids)
        if not r["aceptada"] or r["texto"] != c["texto"]:
            mismatch.append(c["id"])
    check("Dorada Q2 · 100% de cifras recalculadas desde la evidencia", not mismatch, str(mismatch))
    texts = [c["texto"] for c in accepted]
    n = d["narrativa"]
    texts += [n["respuesta_ejecutiva"]["texto"], n["respuesta_ejecutiva"].get("titular") or ""]
    texts += [h.get(k) or "" for h in n["hallazgos"] for k in ("titular", "interpretacion", "implicacion", "por_que")]
    texts += [b["texto"] for b in n["limites"] + n["implicaciones"]]
    bad = [t[:80] for t in texts if causal_hits(t, allow_explica=True)]
    check("Dorada Q2 · cero lenguaje causal", not bad, str(bad))
    bad = [c["id"] for c in accepted if stray_digits(c["plantilla"]) or number_words(c["plantilla"]) or qualifiers(c["plantilla"])]
    check("Dorada Q2 · ninguna plantilla con cifras a mano o calificativos", not bad, str(bad))
    errs = validate_composition(n, d["claims"]) if not n.get("degradada") else ["composición degradada"]
    check("Dorada Q2 · la narrativa pasa el validador", not errs, str(errs))
    orphan_v = [v["id"] for v in d["visuals"].values() if not d["claims"].get(v["claim_id"], {}).get("aceptada")]
    check("Dorada Q2 · toda gráfica tiene una afirmación aceptada", not orphan_v, str(orphan_v))
    orphan_c = [c["id"] for c in accepted if c["estado"] != "No evaluable" and not c["apoyo"]]
    check("Dorada Q2 · toda afirmación tiene evidencia", not orphan_c, str(orphan_c))
    # respuesta primero: titulares para leer en segundos, y toda conclusión con su visual
    sin_titular = ([] if n["respuesta_ejecutiva"].get("titular") else ["respuesta"]) + [h["hipotesis_id"] for h in n["hallazgos"] if not h.get("titular")]
    check("Dorada Q2 · respuesta y hallazgos con titular", not sin_titular, str(sin_titular))
    sin_visual = [h["hipotesis_id"] for h in n["hallazgos"] if not any(v in d["visuals"] for v in h.get("visual_ids") or [])]
    check("Dorada Q2 · todo hallazgo tiene su gráfica", not sin_visual, str(sin_visual))
    cards = yaml.safe_load((BRAIN / "evidence" / "workspace_cards.yaml").read_text(encoding="utf-8"))["cards"]
    forms = {"linea", "barras", "cascada", "puntos", "kpi", "tabla", "datos", "tarjeta"}
    bad_v = [v["id"] for v in d["visuals"].values() if v["spec"]["tipo"] not in forms or (v["spec"]["tipo"] == "tarjeta" and
             v["spec"].get("claim_fase1") not in (cards.get(v["spec"]["tarjeta"], {}).get("claims") or []))]
    check("Dorada Q2 · toda gráfica tiene una forma válida y su tarjeta existe", not bad_v, str(bad_v))


def narrative_rules():
    from agent import narrative as nar
    from agent.orchestrator import thread_context
    nar.NARRATIVES = Path(tempfile.mkdtemp())
    d = nar.create("Caso CFO", "CFO", "Separar comportamiento de decisiones")
    ok_piece = {"tipo": "afirmacion", "rol": "Hallazgo", "titulo": "Idas y vueltas", "texto": "Más de 20% se revierte.",
                "estado": "Hecho observado", "afirmaciones": [{"id": "C-DAT-06", "texto": "Más de 20%…", "estado": "Hecho observado",
                                                            "cifras": {"rt_share": "25,3%"}}],
                "visual": {"tipo": "workspace", "chart": "bridgeMonthly", "titulo": "Puente"}, "fuente": {"kind": "afirmacion", "ref": "C-DAT-06"}}
    d = nar.add_piece(d["id"], ok_piece)
    d = nar.add_piece(d["id"], {"tipo": "nota", "rol": "Decisión", "titulo": "Registrar descuentos antes de lanzarlos", "nota": "gobierno"})
    try:
        nar.add_piece(d["id"], {**ok_piece, "rol": "Conclusión"})
        bad_role = False
    except nar.NarrativeError:
        bad_role = True
    check("Narrativa · rechaza papeles fuera de Situación → Acción", bad_role)
    d = nar.update(d["id"], {"orden": ["P-02", "P-01"], "piezas": [{"id": "P-01", "nota": "explica el ruido"}]})
    check("Narrativa · reordena y edita notas", [x["id"] for x in d["piezas"]] == ["P-02", "P-01"] and d["piezas"][1]["nota"] == "explica el ruido")
    d2 = nar.create("Caso CRO", "CRO")
    nar.add_piece(d2["id"], ok_piece)
    m = nar.merge([d["id"], d2["id"]], "Historia")
    check("Narrativa · unir no duplica la misma fuente y ordena por papel",
          [x["rol"] for x in m["piezas"]] == ["Hallazgo", "Decisión"] and len(m["piezas"]) == 2, str([x["rol"] for x in m["piezas"]]))
    pieces = {x["id"]: x for x in m["piezas"]}
    good = {"titulo": "Qué mide hoy el MRR", "subtitulo": "", "pendientes": [], "laminas": [
        {"rol": "Hallazgo", "titulo": "Una cuarta parte se deshace: 25,3% vuelve al mes siguiente", "mensaje": "El monto mezcla cobro con negocio.",
         "puntos": [], "piezas": ["P-01"], "visual": "P-01", "notas": ""},
        {"rol": "Decisión", "titulo": "Registrar los descuentos antes de lanzarlos", "mensaje": "Registrar cada descuento temporal con su vencimiento.",
         "puntos": [], "piezas": ["P-02"], "visual": "", "notas": ""}]}
    check("Narrativa · una presentación respaldada pasa el validador", not nar.validate_story(good, pieces), str(nar.validate_story(good, pieces)))
    bad = {**good, "laminas": [{"rol": "Implicación", "titulo": "El 40% del churn es cobro", "mensaje": "Esto provocó errores.", "puntos": [],
                                "piezas": ["P-01"], "visual": "P-02", "notas": ""}]}
    errs = nar.validate_story(bad, pieces)
    check("Narrativa · rechaza cifras que no están en las piezas citadas", any("cifras" in e for e in errs))
    check("Narrativa · rechaza lenguaje causal en las láminas", any("causal" in e for e in errs))
    check("Narrativa · la gráfica debe venir de una pieza citada con gráfica", any("gráfica" in e for e in errs))
    check("Narrativa · implicaciones sin decisión del usuario van en condicional", any("condicional" in e for e in errs))
    nota_only = {**good, "laminas": [{**good["laminas"][1], "titulo": "Registrar el 25,3% del cobro"}]}
    check("Narrativa · las notas del usuario no cuentan como evidencia de cifras", any("cifras" in e for e in nar.validate_story(nota_only, pieces)))
    durable = {"id": "P-09", "tipo": "afirmacion", "rol": "Hallazgo", "titulo": "Churn observado vs durable", "texto": "", "nota": "",
               "afirmaciones": [{"id": "C-RET-03", "texto": "El churn durable es menor.", "estado": "Hecho observado",
                                 "cifras": {"churn_dur3_2022": "0,98%"}}], "fuente": {"kind": "afirmacion", "ref": "C-RET-03"}}
    lab_ok = {**good, "laminas": [{"rol": "Hallazgo", "titulo": "Solo 0,98% se va y no vuelve a pagar en 3 meses",
                                   "mensaje": "El churn durable es menor.", "puntos": [], "piezas": ["P-09"], "visual": "", "notas": ""}]}
    lab_bad = {**good, "laminas": [{**lab_ok["laminas"][0], "titulo": "Solo 0,98% se va y no vuelve a pagar en 6 meses"}]}
    check("Narrativa · la etiqueta de qué mide la cifra cuenta como evidencia (3 meses), otro horizonte no",
          not nar.validate_story(lab_ok, {"P-09": durable}) and any("cifras" in e for e in nar.validate_story(lab_bad, {"P-09": durable})),
          str(nar.validate_story(lab_ok, {"P-09": durable})))
    plan_ok = {"resumen": "El monto pagado mezcla fenómenos.", "secciones": [{"rol": "Hallazgo", "mensaje": "El monto no es MRR",
               "preguntas": ["¿Qué parte se deshace?"], "piezas": ["P-01"], "afirmaciones": ["C-DAT-06"], "huecos": ["¿Qué es amount?"]}]}
    check("Narrativa · un esqueleto sin cifras y con IDs válidos pasa", not nar.validate_plan(plan_ok, set(pieces)), str(nar.validate_plan(plan_ok, set(pieces))))
    plan_bad = {"resumen": "", "secciones": [{"rol": "Hallazgo", "mensaje": "El 25% se deshace", "preguntas": [], "piezas": ["P-09"],
                                              "afirmaciones": ["C-XXX-99"], "huecos": []}]}
    errs = nar.validate_plan(plan_bad, set(pieces))
    check("Narrativa · el esqueleto no lleva cifras ni IDs inventados", len(errs) >= 3, str(errs))
    fb = nar.fallback_deck(m)
    check("Narrativa · respaldo: una lámina por pieza (incluidas las decisiones del usuario) y pendientes solo donde no hay piezas",
          len(fb["laminas"]) == 2 and {q["rol"] for q in fb["pendientes"]} == {"Situación", "Implicación", "Acción"}, str(fb["pendientes"]))
    ctx = thread_context({"titulo": "x", "texto": "y", "claim_ids": ["C-DAT-06", "C-FAKE-01"]})
    check("Narrativa · el contexto del hilo es contexto, no evidencia, y solo pasa IDs canónicos",
          "no evidencia" in ctx and "C-DAT-06" in ctx and "C-FAKE-01" not in ctx)


def main() -> int:
    for fn in (sql_layer, semantic_rules, validator_rules, sql_guards, golden_q2, narrative_rules):
        try:
            fn()
        except Exception as e:  # noqa: BLE001
            check(f"{fn.__name__} · sin excepciones", False, f"{type(e).__name__}: {e}")
    ok = sum(1 for _, c, _ in RESULTS if c)
    for name, c, detail in RESULTS:
        print(("✓ " if c else "✗ ") + name + ("" if c or not detail else f"  → {detail[:300]}"))
    print(f"\n{ok}/{len(RESULTS)} evaluaciones aprobadas")
    return 0 if ok == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
