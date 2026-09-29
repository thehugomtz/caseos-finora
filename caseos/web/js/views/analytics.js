// Analytics — the existing Business Exploration Workspace, reused. Analytics → Hugo: visual, interactive, narrative.
// Analytics → COS: accepted claims become findings and canonical EvidenceTables with full data lineage.
import { h, mount as put, autosize } from "../core/dom.js";
import { api } from "../core/api.js";
import { icon } from "../core/icons.js";
import { app } from "../app.js";
import { idTag, statusChip, btn, empty, toast, tabs, ago, confirmDialog } from "../ui/components.js";
import { renderVisual } from "../charts/kit.js";

export async function mount(root, param) {
  if (param && param.startsWith("INV-")) return runView(root, param);
  let tab = param === "workspace" ? "workspace" : "runs";
  const body = h("div");
  const paint = async () => {
    const d = await api.cget("/analytics");
    const ws = d.workspace;
    app.crumbs(["Analytics"]);
    const ta = autosize(h("textarea", { placeholder: "Pregunta cuantitativa para el workspace. «¿Dónde se concentra la caída del monto por cliente: industria, cosecha o tamaño de entrada?»" }));
    put(body,
      h("div.head", h("div", h("div.eyebrow", "Analytics Agent · Business Exploration Workspace (reutilizado)"), h("h1.title", "Analytics"),
        h("p.lede", "El agente investigador del workspace existente — capa semántica, catálogo de análisis, registro de evidencia y validador — dentro de CaseOS. Para ti: gráficas y narrativa. Para el COS: tablas canónicas con linaje.")),
        h("div.actions", ws.available ? h("span.chip.good", "workspace montado") : h("span.chip.bad", "workspace no disponible"),
          ws.git_head ? h("span.small.faint", `finora-eda @ ${ws.git_head}`) : null)),
      tabs([{ id: "runs", label: "Investigaciones", count: d.runs.length }, { id: "ask", label: "Nueva pregunta" }, { id: "workspace", label: "Workspace completo" }], tab, t => { tab = t; paint(); }),
      tab === "ask" ? h("div.panel.pad.glow", h("div.eyebrow.accent", "Pregunta cuantitativa · investigación en vivo"), h("div.qbox", { style: { marginTop: "10px" } }, ta),
        h("p.small.muted", "Corre el investigador del workspace (5–18 min, ≈US$1–2 de uso equivalente en tu suscripción). Cada cifra sale de evidencia registrada; el resultado llega como research R- con findings propuestos."),
        h("div.row", h("span.spacer"), btn("Lanzar en el workspace", { variant: "primary", icon: "send", onClick: async () => {
          const q = ta.value.trim();
          if (q.length < 8) return toast("Escribe la pregunta", "err");
          const ok = await confirmDialog({ title: "Investigación en vivo", text: "Consume tu plan (≈US$1–2 equivalente) y tarda varios minutos. ¿Lanzarla?", confirmLabel: "Lanzar" });
          if (!ok) return;
          try { const out = await api.cpost("/research", { question: q, route: { specialty: "analytics", intensity: "analytics" }, force: true }); toast(`${out.research.id} en el workspace`, "agent"); app.go("#/research/" + out.research.id); }
          catch (e) { toast(e.message, "err"); }
        } }))) : null,
      tab === "runs" ? (d.runs.length ? h("div.grid2.runs", d.runs.map(r => h("div.panel.pad", { style: { cursor: "pointer" }, on: { click: () => app.go("#/analytics/" + r.id) } },
        h("div.row.between", h("span.mono.small.faint", r.id), h("span.row", r.caso_id ? h("span.chip.human", r.caso_id) : null, r.source === "golden" ? h("span.chip.accent", "dorada") : null, statusChip(r.status === "publicada" ? "completed" : r.status === "error" ? "failed" : "running"))),
        h("div", { style: { fontSize: "15.5px", fontWeight: 560, margin: "10px 0 6px", lineHeight: 1.4 } }, r.headline || r.pregunta),
        h("div.small.muted.clamp2", r.pregunta),
        h("div.row.wrap.mt", h("span.chip", `${r.claims} afirmaciones validadas`), h("span.chip", `${r.visuals} visuales`), r.linked.length ? h("span.row", { style: { gap: "4px" } }, r.linked.slice(0, 4).map(x => idTag(x))) : h("span.small.faint", "sin enlazar al caso"),
          r.finished_ms ? h("span.small.faint", ago(new Date(r.finished_ms).toISOString())) : null)))) : empty("Sin investigaciones", ws.note || "Lanza una pregunta.")) : null,
      tab === "workspace" ? (ws.ui ? h("div.panel.flush", { style: { height: "calc(100vh - 280px)", minHeight: "520px" } }, h("iframe", { src: ws.ui, style: { width: "100%", height: "100%", border: 0, borderRadius: "16px", background: "#f3f5fa" }, title: "Business Exploration Workspace" }))
        : empty("Workspace no disponible", "Enlaza el workspace en case.yaml › workspace.")) : null);
  };
  put(root, body);
  await paint();
  return { update: tab === "workspace" ? null : paint };
}

async function runView(root, inv) {
  const d = await api.cget(`/analytics/runs/${inv}`);
  app.crumbs([h("a", { href: "#/analytics" }, "Analytics"), inv]);
  const visByClaim = Object.fromEntries((d.visuals || []).map(v => [v.claim_id, v]));
  const promote = async c => {
    const out = await api.cpost(`/analytics/runs/${inv}/claims/${c.id}/promote`);
    toast(`${c.id} → ${out.finding.id} (propuesto)`, "ok");
    await app.refresh();
    return out.finding;
  };
  const rc = d.respuesta_caso;
  const claimRow = c => h("div.finding",
    h("div.row.between", h("div.row", h("span.mono.small.faint", c.id), h("span.chip.ghost", c.estado), h("span.chip.ghost", c.tipo)), c.promoted ? idTag(c.promoted) : null),
    h("div.hl", c.texto),
    visByClaim[c.id] ? (() => { const w = h("div.viz", h("div.legend"), h("div.chart")); requestAnimationFrame(() => renderVisual(w.querySelector(".chart"), visByClaim[c.id].spec, w.querySelector(".legend"))); return w; })() : null,
    h("div.small.faint", "Evidencia: " + (c.apoyo || []).join(", ")),
    h("div.row.wrap", c.promoted ? btn("Abrir finding", { sm: true, variant: "ghost", onClick: () => app.openEntity(c.promoted) }) : btn("Promote to finding", { sm: true, icon: "plus", onClick: async () => { await promote(c); root.replaceChildren(); runView(root, inv); } }),
      btn("Send to COS as table", { sm: true, icon: "orbit", onClick: async () => { const f = c.promoted ? { id: c.promoted } : await promote(c); const out = await api.action(f.id, "send_to_cos"); toast(`${f.id} → tabla ${out.table} · COS evaluando impacto`, "agent"); await app.refresh(); root.replaceChildren(); runView(root, inv); } })));
  put(root,
    h("div.head", h("div", { style: { maxWidth: "980px" } }, h("div.row", h("span.eyebrow", "Investigación del workspace"), h("span.mono.small.faint", inv), d.caso_id ? h("span.chip.human", d.caso_id) : null),
      h("h1.title", { style: { fontFamily: "var(--serif)", fontWeight: 450 } }, d.headline || d.pregunta), h("p.lede", d.pregunta)),
      h("div.actions", btn("Volver", { icon: "back", variant: "ghost", onClick: () => app.go("#/analytics") }))),
    d.answer ? h("div.panel.pad.glow", h("div.eyebrow.accent", "Respuesta"), h("div.answer", { style: { marginTop: "8px", fontSize: "19px" } }, d.answer)) : null,
    rc ? h("div.grid3.mt", h("div.bucket.hc", h("h4", "Qué podemos concluir"), h("ul", (rc.interpretacion_permitida || []).map(x => h("li", x.texto)))),
      h("div.bucket.un", h("h4", "Qué no podemos concluir"), h("ul", (rc.no_podemos_concluir || []).map(x => h("li", x.texto)).concat((rc.limites_del_brief || []).map(x => h("li", x))))),
      h("div.bucket.pl", h("h4", "Preguntas abiertas"), h("ul", (rc.preguntas_abiertas || []).map(x => h("li", x))))) : null,
    (d.hallazgos || []).length ? h("div.mt2", h("h2.sec.mb", "Hallazgos"), h("div.stack", d.hallazgos.map(hz => h("div.panel.pad", h("div", { style: { fontWeight: 600, fontSize: "15px" } }, hz.titular || hz.pregunta),
      hz.interpretacion ? h("p.prose", hz.interpretacion) : null, hz.implicacion ? h("p.small.muted", "Implicación: " + hz.implicacion) : null)))) : null,
    h("div.mt2", h("h2.sec.mb", `Afirmaciones validadas · ${d.claims.length}`, h("span.small.faint", "solo estas pueden volverse evidencia del caso")), h("div.stack", d.claims.map(claimRow))),
    (d.limites || []).length ? h("div.mt2", h("h2.sec.mb", "Límites"), h("ul.prose", d.limites.map(l => h("li", l.texto)))) : null,
    (d.proximas_preguntas || []).length ? h("div.mt2", h("h2.sec.mb", "Seguimientos posibles"), h("div.list", d.proximas_preguntas.map(q => h("div.item", { style: { gridTemplateColumns: "1fr auto" } }, h("div.t", q),
      btn("Preguntar", { sm: true, variant: "ghost", onClick: () => app.go("#/research?q=" + encodeURIComponent(q)) }))))) : null,
    h("div.small.faint.mt2", `Modelo ${d.modelo || "—"} · data ${d.data_version || "—"} · brain ${d.brain_version || "—"}`));
  return {};
}
