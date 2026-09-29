// Story — the claims spine: every claim with its question, headline, answer, evidence and tables; validation that
// blocks unsupported claims and numbers without a table; Hugo's storyline guide (approved in Framing & Shaping) checked
// slide by slide against the evidence; the Story Package that goes to the Visual Storyteller.
import { h, mount as put } from "../core/dom.js";
import { api } from "../core/api.js";
import { app } from "../app.js";
import { idTag, statusChip, btn, empty, toast, thinking, ids, dataView, confirmDialog, tabs } from "../ui/components.js";
import { markdown } from "../ui/markdown.js";

export async function mount(root) {
  let tab = "spine";
  const body = h("div");
  const paint = async () => {
    const [d, sh] = await Promise.all([api.cget("/story"), api.cget("/shaping").catch(() => null)]);
    const pkg = d.package, ph = d.phase;
    const guide = sh ? sh.guion.filter(e => e.approved).map(e => e.approved) : [];
    const gmap = (pkg || {}).guion_map || [];
    const missing = gmap.filter(g => g.coverage === "missing").length;
    const running = app.running.filter(j => j.kind === "story_package");
    app.crumbs(["Story"]);
    const v = (pkg || {}).validation || {};
    put(body,
      h("div.head", h("div", h("div.eyebrow", "05 · Story · COS + Story Package"), h("h1.title", "Story"),
        h("p.lede", "Cada claim responde una pregunta de la audiencia, cita evidencia aceptada y trae sus cifras en tablas. Si un número no está en una tabla, no pasa.")),
        h("div.actions", statusChip(ph.status), running.length ? h("span.row", thinking(), h("span.small.muted", "El COS está armando el paquete")) : null,
          btn("Borrador con evidencia por revisar", { icon: "eye", variant: "ghost", disabled: !!running.length,
            title: "El COS arma la historia con la evidencia que aún no aceptas, para ver cómo quedaría; no se puede marcar Ready hasta que la aceptes",
            onClick: async () => {
              const ins = await confirmDialog({ eyebrow: "Borrador", title: "Ver cómo quedaría la historia",
                text: "El COS arma el Story Package siguiendo tu guion con la evidencia aceptada y la que todavía espera tu revisión. Cada claim que dependa de evidencia sin aceptar queda marcado; para marcar Ready tendrás que aceptarla (o rechazarla) en Research.",
                confirmLabel: "Armar el borrador", field: { label: "Instrucciones para el COS (opcional)", placeholder: "Audiencia, tono, qué no puede faltar…" } });
              if (ins === null) return;
              await api.cpost("/story/package", { instructions: ins === true ? "" : ins, draft: true }); toast("El COS está armando el borrador de la historia", "agent"); paint();
            } }),
          btn(pkg ? "Regenerar Story Package" : "Preparar Story Package", { icon: "spark", disabled: !!running.length, onClick: async () => {
            const ins = await confirmDialog({ title: pkg ? "Regenerar el Story Package" : "Preparar el Story Package", text: "El COS arma el paquete con la evidencia aceptada. Las keys de los claims se conservan entre versiones.", confirmLabel: "Preparar", field: { label: "Instrucciones para el COS (opcional)", placeholder: "Audiencia, tono, qué no puede faltar…" } });
            if (ins === null) return;
            await api.cpost("/story/package", { instructions: ins === true ? "" : ins }); toast("El COS está preparando el Story Package", "agent"); paint();
          } }),
          btn(ph.status === "ready" ? "Story aprobada" : "Mark Story Ready", { variant: "human", human: true, disabled: ph.status === "ready" || !pkg, onClick: () => app.markReady("story") }))),
      !pkg ? h("div.stack.lg", empty("Todavía no hay Story Package", guide.length ? "Cuando el caso esté maduro, el COS lo arma con la evidencia aceptada siguiendo tu guion." : "Cuando el caso esté maduro, el COS lo arma con la evidencia aceptada. Mientras, este es el storyline provisional del framing."),
        guide.length ? guionCoverage(null, guide) : storylineFromFraming(sh)) : h("div",
        h("div.panel.pad.glow", h("div.eyebrow.accent", "Governing thought"), h("div.gt", { style: { margin: "12px 0" } }, pkg.governing_thought),
          h("div.row.wrap", h("span.small.muted", "Audiencia:"), (pkg.audience || []).map(a => h("span.chip", a)), h("span.small.muted", "· v" + pkg.version),
            pkg.draft ? h("span.chip.human", "borrador") : null,
            (v.pending || []).length ? h("span.chip.human", `${v.pending.length} evidencia(s) esperan tu aceptación`) : null,
            v.ok ? h("span.chip.good", (v.pending || []).length ? "sin errores" : "paquete válido") : h("span.chip.bad", `${(v.errors || []).length} problema(s)`),
            (v.warnings || []).length ? h("span.chip.warn", `${v.warnings.length} aviso(s)`) : null),
          (v.pending || []).length ? h("div.small", { style: { marginTop: "10px", color: "var(--human-ink)" } },
            "Borrador: así quedaría la historia. Para marcar Ready acepta o rechaza en Research la evidencia que usa: ", ids(v.pending, 14)) : null,
          pkg.from_to && pkg.from_to.from ? h("div.grid2.mt", h("div", h("div.eyebrow", "Hoy creen"), h("div.small", { style: { marginTop: "4px" } }, pkg.from_to.from)), h("div", h("div.eyebrow", "Deben salir creyendo"), h("div.small", { style: { marginTop: "4px" } }, pkg.from_to.to))) : null),
        (v.errors || []).length || (v.warnings || []).length ? h("div.panel.pad.mt" + ((v.errors || []).length ? ".alert" : ""), h("div.eyebrow", "Validación del contrato"), h("ul.validation", (v.errors || []).map(e => h("li.e", "✖ " + e)), (v.warnings || []).map(w => h("li.w", "⚠ " + w))),
          h("div.row", btn("Revalidar", { sm: true, icon: "refresh", onClick: async () => { await api.cpost("/story/validate"); paint(); } }))) : null,
        h("div.mt2", tabs([{ id: "spine", label: "Claims", count: (pkg.claims || []).length },
          guide.length ? { id: "guion", label: missing ? `Guion · ${missing} sin evidencia` : "Guion · cobertura" } : null,
          { id: "doc", label: "current.md" }, { id: "yaml", label: "package.yaml" }].filter(Boolean), tab, t => { tab = t; paint(); })),
        tab === "spine" ? spine(pkg, d.claims) : tab === "guion" && guide.length ? guionCoverage(pkg, guide) : tab === "doc" ? h("div.paper", markdown(d.current_md)) : h("div.panel.pad.yaml", dataView(pkg))));
    body.querySelectorAll(".idref").forEach(x => x.addEventListener("click", () => app.openEntity(x.dataset.id)));
  };
  put(root, body);
  await paint();
  return { update: paint };
}

function spine(pkg, claims) {
  const byId = Object.fromEntries(claims.map(c => [c.id, c]));
  const sections = pkg.sections && pkg.sections.length ? pkg.sections : [{ name: "Claims", claim_ids: pkg.claims.map(c => c.claim_id) }];
  return h("div.stack.lg",
    (pkg.executive_questions || []).length ? h("div.panel.pad", h("div.eyebrow", "Preguntas de la audiencia"), h("div.stack.mt", pkg.executive_questions.map(q => h("div.row", q.id ? idTag(q.id) : null, h("span", q.text))))) : null,
    sections.map(s => h("div", h("div.row.between.mb", h("h2.sec", s.name), s.purpose ? h("span.small.muted", s.purpose) : null),
      h("div.spine", (s.claim_ids || []).map((cid, i) => { const c = pkg.claims.find(x => x.claim_id === cid); return c ? claimCard(c, byId[cid], i) : null; })))),
    (pkg.recommendations || []).length ? h("div.panel.pad", h("div.eyebrow.human", "Recomendaciones (condicionales)"), h("div.stack.mt", pkg.recommendations.map(r => h("div", h("div", r.text), h("div.small.muted", [r.type, r.condition ? "si " + r.condition : ""].filter(Boolean).join(" · ")))))) : null,
    h("div.grid2", h("div.panel.pad", h("div.eyebrow", "Candidatos a apéndice"), h("ul.prose", (pkg.appendix_candidates || []).map(a => h("li", h("b", a.title), " — ", a.why)))),
      h("div.panel.pad", h("div.eyebrow", "Preguntas sin resolver"), h("ul.prose", (pkg.unresolved_questions || []).map(q => h("li", q))))));
}

function claimCard(c, ent, i) {
  const s = (ent && ent.strength) || { level: c.strength };
  const lvl = s.level || "unsupported";
  return h("div.claim", h("div.node." + lvl, String(i + 1)),
    h("div.card",
      h("div.row.between", h("div.row.wrap", idTag(c.claim_id), h("span.chip.ghost", c.role_in_story), h("span.chip", "confianza " + c.confidence)),
        statusChip(lvl === "supported" ? "supported" : lvl === "weak" ? "weak" : lvl === "proposal" ? "proposed" : lvl === "pending" ? "pending" : "unsupported")),
      c.question ? h("div.q", c.question) : null,
      h("div.hl", c.headline),
      c.answer ? h("div.small", { style: { color: "var(--ink-2)", lineHeight: 1.55 } }, c.answer) : null,
      c.hugo_wording ? h("div.voice", { style: { fontSize: "14.5px" } }, c.hugo_wording) : null,
      h("div.row.wrap", h("span.small.muted", "Evidencia"), ids(c.evidence_ids, 6), h("span.small.muted", "· Tablas"), (c.table_ids || []).length ? ids(c.table_ids, 4) : h("span.chip.warn", "sin tabla")),
      s.unsupported_numbers && s.unsupported_numbers.length ? h("div.corr", "Cifras sin tabla: " + s.unsupported_numbers.join(", ")) : null,
      c.visual_intent ? h("div.small.muted", "Intención visual: " + c.visual_intent) : null,
      (c.limitations || []).length ? h("div.small.faint", "Límites: " + c.limitations.join(" · ")) : null,
      h("div.row", btn("Editar claim", { sm: true, variant: "ghost", onClick: () => editClaim(c) }), btn("Detalle", { sm: true, variant: "ghost", onClick: () => app.openEntity(c.claim_id) }))));
}

async function editClaim(c) {
  const hl = await confirmDialog({ title: `Editar ${c.claim_id}`, text: "Mejora la claridad sin borrar tu vocabulario. Se revalida contra las tablas.", confirmLabel: "Guardar", field: { label: "Titular", value: c.headline, required: true } });
  if (!hl || hl === true) return;
  try { const out = await api.action(c.claim_id, "update_story", { headline: hl }); toast(out.validation.ok ? "Claim actualizado · paquete válido" : "Claim actualizado · revisa la validación", out.validation.ok ? "ok" : "err"); await app.refresh(); }
  catch (e) { toast(e.message, "err"); }
}

// Hugo's guide, slide by slide: which claims cover it and whether the evidence is there. Without a package it is just
// the guide the COS will follow.
const COVERAGE = { covered: ["con evidencia", "good"], partial: ["evidencia parcial", "warn"], missing: ["sin evidencia", "bad"] };
function guionCoverage(pkg, guide) {
  const map = Object.fromEntries(((pkg || {}).guion_map || []).map(g => [g.slide_id, g]));
  const all = guide.flatMap(s => s.slides || []);
  const n = k => all.filter(sl => (map[sl.id] || {}).coverage === k).length;
  const unmapped = all.filter(sl => !map[sl.id]).length;
  return h("div.stack.lg",
    h("div.panel.pad", h("div.eyebrow.accent", pkg ? "Tu guion contra la evidencia" : "Tu guion · aprobado en Framing & Shaping"),
      pkg ? h("div.row.wrap", { style: { gap: "6px", margin: "10px 0" } }, h("span.chip.good", `${n("covered")} con evidencia`), h("span.chip.warn", `${n("partial")} parcial`),
        h("span.chip.bad", `${n("missing")} sin evidencia`), unmapped ? h("span.chip.ghost", `${unmapped} sin mapear`) : null) : null,
      h("div.small.muted", { style: { marginTop: pkg ? 0 : "6px" } }, "El COS arma el Story Package siguiendo este guion. Una lámina sin evidencia no se rellena: queda marcada y su pregunta pasa a «Preguntas sin resolver» para investigarla.")),
    guide.map(s => h("div.panel.pad", h("div.row.between.wrap", h("h2.sec", h("span.sid", s.id), s.title || "—"), s.purpose ? h("span.small.muted", s.purpose) : null),
      h("div.gcov", { style: { marginTop: "8px" } }, (s.slides || []).map(sl => {
        const g = map[sl.id];
        const c = g ? COVERAGE[g.coverage] || [g.coverage, "ghost"] : pkg ? ["sin mapear", "ghost"] : null;
        return h("div.gr", h("span.slid", sl.id),
          h("div", h("div", { style: { fontWeight: 600 } }, sl.title || "—"), sl.question ? h("div.small.muted", sl.question) : null,
            g && g.note ? h("div.small.faint", g.note) : null,
            g && (g.claim_ids || []).length ? h("div.row.wrap", { style: { gap: "4px", marginTop: "4px" } }, ids(g.claim_ids, 6)) : null),
          c ? h(`span.chip.${c[1]}`, c[0]) : h("span"));
      })))));
}

function storylineFromFraming(sh) {
  const legacy = (sh || {}).legacy_storyline || [];
  return h("div.panel.pad", h("div.eyebrow", "Storyline provisional (del framing)"),
    legacy.length ? h("div.storyline.mt", legacy.map(s => h("div", h("span", s)))) : h("div.small.muted.mt", "Sin guion todavía: apruébalo en Framing & Shaping."),
    h("div.small.faint.mt", "Se convierte en claims con evidencia cuando el COS prepara el Story Package."));
}
