// Briefing — the structured brief rendered as a document, its declared information gaps and its sources.
import { h, mount as put } from "../core/dom.js";
import { api } from "../core/api.js";
import { app } from "../app.js";
import { statusChip, btn, toast, modal } from "../ui/components.js";

export async function mount(root) {
  const body = h("div");
  const paint = async () => {
    const d = await api.cget("/brief");
    const b = d.brief, ph = d.phase;
    app.crumbs(["Briefing"]);
    const list = xs => (xs || []).length ? h("ul", (xs || []).map(x => h("li", typeof x === "string" ? x : (x.title || JSON.stringify(x))))) : h("p", h("em", "—"));
    put(body,
      h("div.head", h("div", h("div.eyebrow", "01 · Briefing"), h("h1.title", b.title || "Brief"), h("p.lede", b.client ? `${b.client}${b.company ? " · " + b.company : ""}` : "")),
        h("div.actions", statusChip(ph.status), ph.ready_count ? h("span.small.muted", `v${ph.ready_count}`) : null,
          ph.ready_count ? btn("Reabrir", { variant: "ghost", onClick: () => app.reopenPhase("briefing") }) : null,
          btn("Editar", { variant: "ghost", onClick: () => edit(b, paint) }),
          btn(ph.status === "ready" ? "Brief aprobado" : "Mark Briefing Ready", { variant: "human", human: true, disabled: ph.status === "ready", onClick: () => app.markReady("briefing") }))),
      (b.gaps || []).length ? h("div.panel.pad.mb", { style: { borderColor: "rgba(245,165,36,.3)" } }, h("div.eyebrow", { style: { color: "#ffc766" } }, "Vacíos de información declarados · no se rellenan con supuestos"),
        h("ul.prose", { style: { marginTop: "8px" } }, b.gaps.map(g => h("li", g)))) : null,
      h("div.paper",
        h("h1", "Brief"),
        h("h2", "Objetivo"), h("p", b.objective || "—"), (b.provenance || {}).objective ? h("p", h("em", "Fuente: " + b.provenance.objective)) : null,
        h("h2", "Audiencia"), h("p", (b.audience || []).join(" · ")), b.audience_note ? h("p", h("em", b.audience_note)) : null,
        h("h2", "Contexto"), h("p", b.context || "—"), (b.provenance || {}).context ? h("p", h("em", "Fuente: " + b.provenance.context)) : null,
        h("h2", "Entregables"), list(b.deliverables), h("h2", "Restricciones"), list(b.constraints),
        h("h2", "Datos disponibles"), list(b.data_available), h("h2", "Criterios de éxito"), list(b.success_criteria),
        b.brief_text ? [h("h2", "Texto del brief"), h("p", { style: { whiteSpace: "pre-wrap" } }, b.brief_text)] : null,
        h("h2", "Fuentes"), h("ul", (b.sources || []).map(s => h("li", s.path ? h("a", { href: `/case-files/${app.caseId}/sources/${s.path.split("/").pop()}`, target: "_blank" }, s.title) : s.title,
          s.origin ? h("span", { style: { color: "#6b6c73" } }, ` — ${s.origin}`) : null, s.note ? h("em", ` (${s.note})`) : null)))));
  };
  put(root, body);
  await paint();
  return { update: paint };
}

function edit(b, done) {
  const f = {};
  const field = (k, label, val, multi = true) => h("div.field", h("label", label), f[k] = h(multi ? "textarea" : "input", { value: val || "" }));
  const joinL = xs => (xs || []).map(x => typeof x === "string" ? x : x.title).join("\n");
  modal({ eyebrow: "Briefing", title: "Editar el brief", wide: true, body: h("div", field("objective", "Objetivo", b.objective), field("context", "Contexto", b.context),
    field("deliverables", "Entregables (uno por línea)", joinL(b.deliverables)), field("constraints", "Restricciones (una por línea)", joinL(b.constraints)),
    field("gaps", "Vacíos de información (uno por línea)", joinL(b.gaps))),
    actions: [{ label: "Cancelar", variant: "ghost" }, { label: "Guardar", variant: "primary", onClick: async () => {
      const lines = k => f[k].value.split("\n").map(s => s.trim()).filter(Boolean);
      await api.cpatch("/brief", { fields: { objective: f.objective.value.trim(), context: f.context.value.trim(), deliverables: lines("deliverables"), constraints: lines("constraints"), gaps: lines("gaps") } });
      toast("Brief actualizado", "ok");
      done();
    } }] });
}
