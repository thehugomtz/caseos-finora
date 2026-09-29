// Research Hub — the research plan approved in Framing & Shaping (tasks ready to launch, each with its agent), a free
// request with live routing preview (intensity · specialist · minimum skills · purpose check), the queue, and the
// result page (§41): question, short answer, findings, evidence, sources, alternatives,
// unknowns, case implication, story impact — with Accept / Challenge / Research deeper / Follow-up / Send to COS / Reject.
import { h, mount as put, debounce, autosize } from "../core/dom.js";
import { api } from "../core/api.js";
import { icon } from "../core/icons.js";
import { app, tableBlock } from "../app.js";
import { idTag, review, statusChip, btn, empty, toast, thinking, ids, hhmm, ago, confirmDialog, tabs, STATUS_LABEL } from "../ui/components.js";
import { renderVisual } from "../charts/kit.js";

const SPEC = { analytics: "Analytics", business: "Business Research", measurement: "Measurement", data_engineering: "Data Engineering" };
const SPEC_ICON = { analytics: "chart", business: "globe", measurement: "ruler", data_engineering: "db" };
const INT = { L1: "L1 · Lookup", L2: "L2 · Business research", L3: "L3 · Deep research", analytics: "Analytics" };

export async function mount(root, param) {
  if (param && /^R-\d+/.test(param)) return detail(root, param);
  return hub(root);
}

/* ------------------------------------------------------------------ hub */
async function hub(root) {
  let filter = "all";
  const q0 = new URLSearchParams(location.hash.split("?")[1] || "").get("q") || "";
  const ta = autosize(h("textarea", { placeholder: "¿Qué incertidumbre del caso quieres resolver? «¿Cómo medimos self-service + SQL directo + sales assisted sin forzar un funnel lineal?»" }));
  ta.value = q0;
  const preview = h("div.stack", { style: { gap: "10px", marginTop: "12px" } });
  const list = h("div");
  let route = null, links = [], override = {};
  const runPreview = debounce(async () => {
    const q = ta.value.trim();
    if (q.length < 8) { put(preview); return; }
    route = await api.cpost("/research/route", { question: q, links });
    paintPreview();
  }, 280);
  ta.addEventListener("input", runPreview);
  const paintPreview = () => {
    if (!route) return;
    const eff = { ...route, ...override };
    const p = route.purpose || {};
    put(preview,
      h("div.row.wrap", h("span.eyebrow.accent", "Ruta propuesta"), h("span.chip.accent", INT[eff.intensity] || eff.intensity),
        h("span.chip.agent", icon(SPEC_ICON[eff.specialty] || "globe"), SPEC[eff.specialty]),
        ((app.summary || {}).meta || {}).data_model && ["analytics", "measurement", "data_engineering"].includes(eff.specialty)
          ? h("span.chip.work-datos", icon("db"), "Investiga datos en el modelo · solo lectura") : null,
        (route.skills || []).map(s => h("span.chip", s.id)), h("span.small.faint", "· el Research Router confirma o ajusta al lanzar")),
      h("div.row.wrap", h("span.small.muted", "Cambiar:"),
        ["L1", "L2", "L3"].map(l => h("button.btn.sm" + (eff.intensity === l ? ".primary" : ".ghost"), { type: "button", on: { click: () => { override = { ...override, intensity: l, specialty: eff.specialty === "analytics" ? "business" : eff.specialty }; paintPreview(); } } }, l)),
        Object.entries(SPEC).map(([k, v]) => h("button.btn.sm" + (eff.specialty === k ? ".primary" : ".ghost"), { type: "button", on: { click: () => { override = { ...override, specialty: k, intensity: k === "analytics" ? "analytics" : (eff.intensity === "analytics" ? "L2" : eff.intensity) }; paintPreview(); } } }, v))),
      h("div.row.wrap", h("span.small.muted", "Propósito de caso:"),
        links.length ? links.map(i => h("span.row", { style: { gap: "4px" } }, idTag(i), h("button.btn.ghost.sm", { type: "button", style: { height: "20px", padding: "0 5px" }, on: { click: () => { links = links.filter(x => x !== i); runPreview(); } } }, "×"))) : null,
        (p.suggested || []).filter(i => !links.includes(i)).map(i => h("button.btn.sm.ghost", { type: "button", title: (app.byId[i] || {}).title, on: { click: () => { links.push(i); runPreview(); } } }, "+ " + i + (app.byId[i] && app.byId[i].alias ? ` (${app.byId[i].alias})` : ""))),
        !links.length ? h("span.chip.warn", "RESEARCH WITHOUT CASE PURPOSE — enlázala o decide") : h("span.chip.good", "mapeada al caso")),
      h("div.row", h("span.spacer"), !links.length ? btn("Investigar de todos modos", { variant: "ghost", onClick: () => launch(true) }) : null,
        btn("Lanzar investigación", { variant: "primary", icon: "send", disabled: !links.length, onClick: () => launch(false) })));
  };
  const launch = async force => {
    const q = ta.value.trim();
    try {
      const out = await api.cpost("/research", { question: q, links, route: Object.keys(override).length ? { ...override } : null, force });
      toast(`${out.research.id} ${out.launched ? "en cola → " + SPEC[out.research.specialty] : "creada (espera decisión)"}`, out.launched ? "agent" : "info");
      ta.value = ""; links = []; override = {}; route = null; put(preview);
      await app.refresh();
      app.go("#/research/" + out.research.id);
    } catch (e) { toast(e.message, "err"); }
  };
  const planBox = h("div");
  const paintPlan = async () => {
    const sh = await api.cget("/shaping");
    const approved = sh.plan.filter(e => e.approved);
    const proposed = sh.progress.tasks_proposed;
    if (!approved.length && !proposed) { put(planBox); return; }
    const ready = approved.filter(e => e.approved.status === "approved"), sent = approved.filter(e => e.approved.status === "sent");
    const launch1 = async id => {
      try { const out = await api.cpost(`/shaping/tasks/${encodeURIComponent(id)}/send`); toast(`${id} → ${out.research_id} ${out.launched ? "en cola" : "creada"}`, "agent"); await app.refresh(); await paint(); }
      catch (e) { toast(e.message, "err", 7000); }
    };
    const launchAll = async () => {
      try { const out = await api.cpost("/shaping/tasks/send-all"); toast(`${out.sent.length} tarea(s) lanzadas`, "agent"); await app.refresh(); await paint(); }
      catch (e) { toast(e.message, "err", 7000); }
    };
    const kindChip = t => h("span.chip.kind-" + t.kind, icon(SPEC_ICON[t.agent] || "globe"), `${(sh.kinds[t.kind] || {}).label || t.kind} · ${SPEC[t.agent] || t.agent}`);
    const workChip = t => h("span.chip.work-" + (t.work || "propuesta"), ((sh.work || {})[t.work || "propuesta"] || {}).label || t.work);
    const stepsLine = t => (t.steps || []).length ? h("div.small.muted", { style: { marginTop: "4px" } }, t.steps.map((st, i) =>
      `${i + 1}. ${(sh.step_kinds || {})[st.kind] || st.kind}${(st.where || []).length ? " (" + st.where.join(", ") + ")" : ""}`).join("  →  ")) : null;
    put(planBox, h("div.panel.pad.plan",
      h("div.row.between.wrap",
        h("div", h("div.eyebrow.accent", "Plan de investigación · aprobado en Framing & Shaping"),
          h("div.small.muted", { style: { marginTop: "4px" } }, [`${ready.length} por lanzar`, `${sent.length} ya en Research`,
            proposed ? `${proposed} propuesta(s) esperan tu aprobación en el documento` : null].filter(Boolean).join(" · "))),
        h("div.row", { style: { gap: "6px" } },
          btn("Ver en el documento", { sm: true, variant: "ghost", icon: "compass", onClick: () => app.go("#/framing") }),
          ready.length > 1 ? btn(`Lanzar las ${ready.length}`, { sm: true, variant: "primary", icon: "send", onClick: launchAll }) : null)),
      ready.length ? h("div.list", { style: { marginTop: "8px" } }, ready.map(e => { const t = e.approved;
        return h("div.item", { style: { gridTemplateColumns: "64px 1fr auto" } },
          h("span.sid", { style: { justifySelf: "start" } }, t.id),
          h("div.body", h("div.t", t.question), h("div.m", workChip(t), kindChip(t), t.intensity && t.intensity !== "analytics" ? h("span.chip.accent", t.intensity) : null,
            (t.links || []).map(i => idTag(i)), (t.slides || []).map(x => h("span.chip.ghost", x))),
            t.draft_answer ? h("div.small.clamp2", { style: { marginTop: "6px", color: "var(--ink-2)" } }, h("span.faint", "Arranque: "), t.draft_answer) : null,
            stepsLine(t)),
          h("div.side", btn("Lanzar", { sm: true, variant: "primary", icon: "send", onClick: () => launch1(t.id) }))); })) : null,
      sent.length ? h("div.row.wrap", { style: { gap: "6px", marginTop: "10px" } }, h("span.small.faint", "Ya en Research:"),
        sent.map(e => h("button.chip", { type: "button", style: { cursor: "pointer" }, on: { click: () => app.go("#/research/" + e.approved.research_id) } },
          `${e.approved.id} → ${e.approved.research_id}`))) : null));
  };
  const paint = async () => {
    paintPlan().catch(() => put(planBox));
    const room = await api.cget("/cos/room");
    const all = room.research_queue;
    const groups = {
      running: all.filter(r => ["queued", "running"].includes(r.status)), review: all.filter(r => r.status === "completed" && r.review === "proposed"),
      accepted: all.filter(r => r.review === "accepted"), blocked: all.filter(r => ["blocked", "failed", "draft"].includes(r.status)), rejected: all.filter(r => r.review === "rejected"),
    };
    const ph = room.health.phases.find(p => p.id === "research");
    app.crumbs(["Research"]);
    groups.proposals = all.filter(r => r.status === "completed" && r.specialty !== "analytics" && r.work !== "datos");
    const shown = filter === "all" ? all : groups[filter];
    put(list,
      tabs([{ id: "all", label: "Todo", count: all.length }, { id: "proposals", label: "Propuestas · cómo llegaron", count: groups.proposals.length },
        { id: "running", label: "En curso", count: groups.running.length }, { id: "review", label: "Por revisar", count: groups.review.length },
        { id: "accepted", label: "Aceptadas", count: groups.accepted.length }, { id: "blocked", label: "Bloqueadas / fallidas", count: groups.blocked.length },
        { id: "rejected", label: "Rechazadas", count: groups.rejected.length }], filter, f => { filter = f; paint(); }),
      filter === "proposals" ? proposalsBox() : shown.length ? h("div.list.rq", shown.map(r => h("div.item", { on: { click: () => app.go("#/research/" + r.id) } },
        h("div.row", { style: { paddingTop: "2px" } }, idTag(r.id, { alias: r.alias })),
        h("div.body", h("div.t", r.question), r.short_answer ? h("div.small.muted.clamp2", { style: { marginTop: "4px" } }, r.short_answer) : null,
          h("div.m", h("span.chip", icon(SPEC_ICON[r.specialty] || "globe"), SPEC[r.specialty] || r.specialty), r.intensity && r.intensity !== "analytics" ? h("span.chip.accent", r.intensity) : null,
            r.shaping_task ? h("span.chip.ghost", "plan " + r.shaping_task) : null, !r.purpose_ok ? h("span.chip.warn", "sin propósito") : null)),
        h("div.side", r.status === "running" || r.status === "queued" ? h("span.row", thinking(), statusChip(r.status)) : statusChip(r.status === "completed" ? (r.review === "proposed" ? "review" : r.review === "accepted" ? "completed" : "rejected") : r.status),
          review(r.review, r.stale))))) : empty("Nada aquí", "Lanza una tarea del plan de investigación o escribe una pregunta arriba."));
    put(headBox, h("div.head", h("div", h("div.eyebrow", "03 · Research Hub · Router → especialistas → síntesis para el caso"), h("h1.title", "Research"),
      h("p.lede", "No se investigan temas: se investigan incertidumbres que importan al caso. Cada solicitud se mapea a una pregunta, hipótesis, decisión o claim.")),
      h("div.actions", statusChip(ph.status), btn("Analytics workspace", { icon: "chart", onClick: () => app.go("#/analytics") }),
        btn(ph.status === "ready" ? "Research aprobado" : "Mark Research Ready", { variant: "human", human: true, disabled: ph.status === "ready", onClick: () => app.markReady("research") }))));
  };
  const proposalsBox = () => {
    const box = h("div.stack.lg", { style: { marginTop: "12px" } }, h("div.row", thinking(), h("span.small.muted", "Cargando el proceso de cada propuesta…")));
    api.cget("/research-proposals").then(({ proposals }) => {
      put(box, h("div.small.muted", "Cada propuesta, de la respuesta de arranque a lo que concluyó: cómo leyó el problema, qué revisó en orden (modelo de datos, búsquedas, lecturas), qué alternativas descartó y qué hizo el COS con el resultado. Es la traza operativa de la corrida, no el razonamiento interno del modelo."),
        proposals.length ? proposals.map(({ research: r, process: pr }) => h("div.panel.pad.propcard",
          h("div.row.between.wrap", h("div.row.wrap", idTag(r.id), r.shaping_task ? h("span.chip.ghost", r.shaping_task) : null,
            h("span.chip.work-" + ((r.task || {}).work || "propuesta"), WORK_LABEL[(r.task || {}).work] || "Propuesta"),
            h("span.chip", icon(SPEC_ICON[r.specialty] || "globe"), SPEC[r.specialty] || r.specialty), (r.slides || []).map(x => h("span.chip.ghost", "lámina " + x))),
            btn("Ver completo", { sm: true, variant: "ghost", icon: "arrow", onClick: () => app.go("#/research/" + r.id) })),
          h("div.propq", r.research_question), processLadder(r, pr, { compact: true }))) : empty("Todavía no hay propuestas terminadas", "Aparecen aquí cuando un especialista termina una tarea de propuesta."));
    }).catch(e => put(box, h("div.corr", "No pude cargar las propuestas: " + e.message)));
    return box;
  };
  const headBox = h("div");
  put(root, headBox, planBox,
    h("div.panel.pad.glow", { style: { marginTop: "16px" } }, h("div.eyebrow.accent", "Nueva investigación"), h("div.qbox", { style: { marginTop: "10px" } }, ta), preview),
    h("div.mt2", list));
  await paint();
  if (q0) runPreview();
  return { update: paint };
}

/* ------------------------------------------------------------------ detail */
async function detail(root, rid) {
  const paint = async () => {
    const d = await api.cget(`/entities/${rid}`);
    const r = d.entity;
    app.crumbs([h("a", { href: "#/research" }, "Research"), rid]);
    const rv = (r.review || {}).state;
    const running = ["queued", "running"].includes(r.status);
    const findings = d.findings_full || [];
    const sec = (title, ...kids) => { const k = kids.flat().filter(Boolean); return k.length ? h("div.mt2", h("h2.sec.mb", title), k) : null; };
    const aff = (r.affected_hypotheses || []).filter(a => a.id);
    const job = d.job;
    put(root,
      h("div.head", h("div", { style: { maxWidth: "940px" } },
        h("div.row.wrap", idTag(r.id, { alias: r.alias }), h("span.chip", icon(SPEC_ICON[r.specialty] || "globe"), SPEC[r.specialty] || r.specialty),
          r.intensity && r.intensity !== "analytics" ? h("span.chip.accent", INT[r.intensity]) : null, statusChip(r.status), review(rv, !!r.stale),
          (r.route || {}).source === "router" ? h("span.small.faint", "ruteada por el Research Router") : null),
        h("h1.title", { style: { fontFamily: "var(--serif)", fontWeight: 450, fontSize: "30px" } }, r.research_question),
        (() => { const w = r.worked_question || (r.route || {}).reformulated_question;
          return w && w !== r.research_question ? h("div.small.muted", { style: { marginTop: "-4px", maxWidth: "820px" } }, h("span.faint", "Cómo la trabajó el agente: "), w) : null; })(),
        h("div.row.wrap", h("span.small.muted", "Sirve a:"), ids((r.links || []).filter(i => /^[QHDC]-/.test(i)), 8),
          r.shaping_task ? h("button.chip.ghost", { type: "button", style: { cursor: "pointer" }, on: { click: () => app.go("#/framing") } }, `tarea ${r.shaping_task} del plan`) : null,
          (r.slides || []).map(x => h("span.chip.ghost", "lámina " + x)), !r.purpose_ok ? h("span.chip.warn", "RESEARCH WITHOUT CASE PURPOSE") : null)),
        h("div.actions", btn("Volver", { icon: "back", variant: "ghost", onClick: () => app.go("#/research") }))),
      r.task && (r.task.draft_answer || (r.task.steps || []).length) ? taskContext(r) : null,
      running ? h("div.panel.pad.agentwork", h("div.row", thinking(), h("span", { style: { fontWeight: 560 } }, r.status === "queued" ? "En cola" : "Investigando…"), h("span.small.muted", SPEC[r.specialty])),
        h("div.progress.mt", ((job || {}).progress || []).slice(-24).map(p => h("div", h("span.t", hhmm(p.t)), h("span", p.summary || p.kind + (p.phase ? " · " + p.phase : "") + (p.role ? " · " + p.role : "")))))) : null,
      r.status === "failed" ? h("div.panel.pad.alert", h("div.eyebrow", { style: { color: "var(--bad-ink)" } }, "La investigación falló"), h("p.prose", r.error || ""), h("div.small.muted", "La solicitud se conservó."),
        h("div.mt", btn("Reintentar", { icon: "refresh", onClick: async () => { await api.action(rid, "retry"); toast("Reintentando…", "agent"); paint(); } }))) : null,
      r.status === "draft" ? h("div.panel.pad", { style: { borderColor: "var(--warn-line)" } }, h("div.eyebrow", { style: { color: "var(--warn-ink)" } }, "RESEARCH WITHOUT CASE PURPOSE"), h("p.prose", r.purpose_note || ""),
        h("div.row", btn("Investigar de todos modos", { onClick: async () => { await api.action(rid, "retry"); paint(); } }))) : null,
      r.status === "blocked" ? h("div.panel.pad", { style: { borderColor: "var(--warn-line)" } }, h("div.eyebrow", { style: { color: "var(--warn-ink)" } }, "Bloqueada · no hay sustituto válido"),
        h("p.answer", { style: { fontSize: "19px", marginTop: "10px" } }, r.short_answer), h("p.small.muted", r.blocked_reason || ""),
        (r.missing_evidence || []).length ? h("table.spec-table.mt", h("thead", h("tr", h("th", "Evidencia que falta"), h("th", "Dónde podría estar"))),
          h("tbody", r.missing_evidence.map(m => h("tr", h("td", m.dato), h("td", m.fuente || "—"))))) : null) : null,
      r.short_answer && r.status === "completed" ? h("div.panel.pad.glow", h("div.eyebrow.accent", "Respuesta corta"), h("div.answer", { style: { marginTop: "10px" } }, r.short_answer),
        r.why_it_matters ? h("div.small.muted.mt", "Por qué importa: " + r.why_it_matters) : null) : null,
      r.status === "completed" && r.specialty !== "analytics" ? sec("Cómo llegó a esta propuesta", h("div.panel.pad", processLadder(r, d.process))) : null,
      sec(`Hallazgos clave · ${findings.length}`, findings.length ? h("div.stack", findings.map(f => findingCard(f, paint))) : null),
      (r.visuals || []).length ? sec("Visualizaciones del análisis", h("div.grid2", r.visuals.map(v => { const w = h("div.viz", h("div.vt.clamp3", v.title || ""), h("div.legend"), h("div.chart")); requestAnimationFrame(() => renderVisual(w.querySelector(".chart"), v.spec, w.querySelector(".legend"))); return w; }))) : null,
      (r.what_is_established || []).length || (r.what_remains_unknown || []).length ? sec("Qué sabemos y qué no",
        h("div.grid3", bucketList("Establecido", r.what_is_established, "hc"), bucketList("En disputa", r.what_is_contested, "co"), bucketList("Qué no sabemos / no podemos concluir", (r.what_remains_unknown || []).concat(r.cannot_claim || []), "un"))) : null,
      r.confidence_buckets && Object.values(r.confidence_buckets).some(x => x && x.length) ? sec("Confianza (deep research)", h("div.buckets", bucketList("High confidence", r.confidence_buckets.high_confidence, "hc"),
        bucketList("Plausible", r.confidence_buckets.plausible, "pl"), bucketList("Contested", r.confidence_buckets.contested, "co"), bucketList("Unknown", r.confidence_buckets.unknown, "un"))) : null,
      (r.alternative_explanations || []).length ? sec("Explicaciones alternativas", h("ul.prose", r.alternative_explanations.map(x => h("li", x)))) : null,
      specialistBlock(r),
      r.case_implication || aff.length || r.cos_assessment ? sec("Implicación para el caso e impacto en la historia",
        h("div.grid2", h("div.panel.pad", h("h3.sub", "Implicación para el caso"), h("p.prose", r.case_implication || "—"),
          r.changes_current_story ? h("div.row", h("span.small.muted", "¿Cambia la historia actual?"), h("span.chip" + ((r.changes_current_story.value || r.changes_current_story) === "yes" ? ".warn" : ""), String(r.changes_current_story.value || r.changes_current_story)), h("span.small.muted", r.changes_current_story.why || "")) : null,
          r.suggested_action ? h("div.small.mt", h("span.muted", "Acción sugerida: "), r.suggested_action) : null),
          h("div.panel.pad", h("h3.sub", "Hipótesis y claims afectados"), aff.length || (r.affected_claims || []).length ? h("div.stack", aff.concat(r.affected_claims || []).map(a => h("div.row.wrap", idTag(a.id, { alias: a.alias }),
            h("span.chip" + (/(fortalec|support|soport)/i.test(a.effect || a.state || "") ? ".good" : /(debil|weak|contra)/i.test(a.effect || a.state || "") ? ".warn" : ""), a.effect || a.state || ""), h("span.small.muted.clamp2", a.reading || a.why || "")))) : h("div.small.muted", "—"),
            r.cos_assessment ? h("div.answer-card.mt", h("div.eyebrow.accent", "Evaluación del COS"), h("div.small", r.cos_assessment.summary)) : null))) : null,
      (r.sources || []).length ? sec(`Fuentes · ${r.sources.length}`, h("div.panel.pad", r.validation && !r.validation.ok ? h("div.corr", { style: { marginBottom: "10px" } }, `⚑ ${r.validation.unverified_sources.length} fuente(s) no recuperadas en la corrida; sus claims bajaron a confianza baja.`) : null,
        r.sources.map(s => h("div.src", h("span.q." + (s.quality || "C"), s.quality || "?"), h("div", h("div", s.url ? h("a", { href: s.url, target: "_blank", rel: "noopener" }, s.title || s.url) : (s.title || s.path)),
          h("div.small.muted", [s.publisher, s.source_type || s.type, s.date].filter(Boolean).join(" · ")), s.note ? h("div.small.faint", s.note) : null),
          s.verified === false ? h("span.chip.bad", "no verificada") : s.verified ? h("span.chip.good", "verificada") : h("span"))))) : null,
      (r.claims || []).length ? sec("Claims con fuente (disciplina de evidencia)", h("table.spec-table", h("thead", h("tr", h("th", "Claim"), h("th", "Fuente"), h("th", "Tipo"), h("th", "Confianza"), h("th", "Frescura"), h("th", "Apoya / contradice"))),
        h("tbody", r.claims.map(c => h("tr", h("td", (c.unverified ? "⚠ " : "") + c.claim), h("td", c.source_id), h("td", c.source_type), h("td", c.confidence), h("td", c.freshness), h("td", c.supports_or_contests)))))) : null,
      r.peer_review ? sec("Peer review", h("div.grid2", bucketList("Riesgo de alucinación", r.peer_review.hallucination_risks, "co"), bucketList("Afirmaciones sin cita", r.peer_review.bare_assertions, "un"),
        bucketList("Corroborado", r.peer_review.corroborated, "hc"), bucketList("Contradicciones", r.peer_review.contradictions, "co")), h("p.small.muted", r.peer_review.verdict || "")) : null,
      (r.new_questions || []).length ? sec("Preguntas nuevas", h("div.list", r.new_questions.map(q => h("div.item", { style: { gridTemplateColumns: "1fr auto" } }, h("div.t", q),
        btn("Crear seguimiento", { sm: true, variant: "ghost", onClick: async () => { await api.action(rid, "follow_up", { question: q }); toast("Pregunta creada", "ok"); app.refresh(); } }))))) : null,
      (r.sql_runs || []).length ? sec(`Consultas al modelo de datos · ${r.sql_runs.length}`, h("div.panel.pad",
        h("div.small.muted", "Lo que el especialista consultó en solo lectura durante la corrida. Una cita del modelo solo cuenta si su consulta está aquí."),
        r.sql_runs.map(q => h("pre.sql", q)))) : null,
      r.workspace_run ? h("div.small.faint.mt2", `Investigación del workspace: ${r.workspace_run.run_id} · ${r.workspace_run.path}`) : null,
      (r.run_ids || []).length ? h("div.small.faint", `Corridas: ${r.run_ids.join(" · ")}`) : null,
      r.status === "completed" ? h("div.actionbar", d.actions.map(a => btn(a.label, { sm: false, variant: a.id === "accept" ? "primary" : a.id === "reject" ? "danger" : "", icon: { accept: "check", challenge: "flag", research_deeper: "search", follow_up: "plus", send_to_cos: "orbit", reject: "x" }[a.id],
        onClick: () => researchAction(r, a, paint) })), (r.sources || []).some(s => s.url) ? btn("Open sources", { icon: "link", onClick: () => r.sources.filter(s => s.url).slice(0, 5).forEach(s => window.open(s.url, "_blank", "noopener")) }) : null) : null);
  };
  await paint();
  // repaint for this research's own job, or when a COS assessment finishes — not for every job of the case
  const onJob = ev => { const e = app.byId[rid] || {}; if (ev.job.id === e.job_id || ["queued", "running"].includes(e.status)
    || (ev.job.kind === "cos_impact" && ["succeeded", "failed"].includes(ev.event.kind))) paint(); };
  app.on("job", onJob);
  return { update: paint, destroy: () => { app.listeners.job = (app.listeners.job || []).filter(f => f !== onJob); } };
}

const WORK_LABEL = { propuesta: "Investigación y propuesta", datos: "Investigar datos", research: "Research externo" };
const TRACE_ICON = { sql: "db", catalog: "table", search: "search", read: "link", tool: "bolt" };
const TRACE_VERB = { sql: "Consultó el modelo", catalog: "Catálogo", search: "Buscó", read: "Leyó", tool: "Usó" };
const clock = s => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
const dur = s => s >= 60 ? `${Math.round(s / 60)} min` : `${s} s`;
const pageOf = u => { try { const x = new URL(u); return x.hostname.replace(/^www\./, "") + (x.pathname.length > 1 ? x.pathname.replace(/\/$/, "") : ""); } catch (e) { return u; } };

// What the specialist did, in order: every query of the data model, search and reading, timed from when it started
// working. It is the operational trace of the run, not the model's private reasoning (never stored).
const OPEN_TRACES = new Set();          // a trace Hugo opened stays open when the page repaints with live events

function traceView(proc, key) {
  const runs = proc.runs || [];
  return h("details.tracebox", { open: OPEN_TRACES.has(key), on: { toggle: e => { e.target.open ? OPEN_TRACES.add(key) : OPEN_TRACES.delete(key); } } },
    h("summary", h("span.small", `Ver los ${proc.counts.total} pasos en orden`)),
    h("div.runsteps", runs.map(rn => [runs.length > 1 ? h("div.rh", rn.purpose || rn.role) : null,
      rn.steps.map(st => h(`div.rs.${st.kind}${st.error ? ".err" : ""}`, h("span.tt", clock(st.s)), icon(TRACE_ICON[st.kind] || "bolt"),
        h("span.tx", h("b", TRACE_VERB[st.kind] || st.kind), " ",
          st.kind === "search" ? `«${st.text}»` : st.kind === "read" ? h("a", { href: st.text, target: "_blank", rel: "noopener" }, pageOf(st.text))
            : st.kind === "catalog" ? "" : st.text,
          st.error ? h("span.faint", " · dio error y lo corrigió en el siguiente paso") : null)))])));
}

export function processLadder(r, proc, { compact = false } = {}) {
  const t = r.task || {}, sp = r.specialist || {};
  const m = sp.measurement, dm = sp.data_model;
  const interp = m ? m.problem_interpretation : dm ? dm.conceptual_model : r.why_it_matters;
  const chosen = m ? m.recommended_framework : null;
  const alts = m ? m.alternative_frameworks || [] : [];
  const unknown = (r.what_remains_unknown || []).slice(0, compact ? 2 : 4);
  const c = proc && proc.counts;
  const clamp = compact ? ".clamp3" : "";
  const rungs = [
    ["Arrancó de", t.draft_answer ? h("div.stack", { style: { gap: "4px" } }, h(`div.small${clamp}`, t.draft_answer),
      (t.hugo_said || []).length ? h("div.small.muted", "Con tus palabras: ", t.hugo_said.map(x => `“${x.text}”`).join(" · ")) : null)
      : h("div.small.faint", "Sin respuesta de arranque (la tarea es anterior al plan desde el guion).")],
    ["Leyó el problema como", interp ? h(`div.small${compact ? ".clamp3" : ""}`, { style: { whiteSpace: "pre-line" } }, interp) : null],
    ["Revisó", proc ? h("div.stack", { style: { gap: "4px" } },
      h("div.small", [c.sql ? `${c.sql} consultas al modelo` : null, c.catalog ? "el catálogo" : null, c.search ? `${c.search} búsquedas` : null,
        c.read ? `${c.read} lecturas` : null].filter(Boolean).join(" · ") + ` · ${dur(proc.work_s)} de trabajo` + (proc.cost_usd ? ` · US$${proc.cost_usd} equiv.` : "")),
      traceView(proc, r.id)) : h("div.small.faint", "Sin traza registrada.")],
    ["Pesó", alts.length || chosen ? h("div.stack", { style: { gap: "6px" } },
      alts.map(a => h("div.small", h("span.chip.ghost", "descartó"), " ", h("b", a.name),
        a.when_better ? " — mejor cuando " + a.when_better.replace(/^\s*cuando\s+/i, "") : "",
        a.tradeoff ? h("span.muted", " · costo: " + a.tradeoff) : null)),
      chosen ? h("div.small", h("span.chip.good", "eligió"), " ", h("b", chosen.name), chosen.why ? " — " + chosen.why : "") : null)
      : (r.alternative_explanations || []).length ? h("div.stack", { style: { gap: "4px" } }, h("div.small.muted", "Explicaciones alternativas que puso sobre la mesa:"),
        h("ul.bl", r.alternative_explanations.slice(0, compact ? 2 : 4).map(x => h("li.small", x)))) : null],
    ["Llegó a", h("div.stack", { style: { gap: "4px" } }, h(`div.small${clamp}`, r.short_answer),
      unknown.length ? h("div.small.muted", h("b", "Sigue sin saberse: "), unknown.join(" · ")) : null)],
    ["El COS", r.cos_assessment ? h(`div.small${clamp}`, r.cos_assessment.summary) : h("div.small.faint", "Sin evaluación del COS todavía.")],
  ].filter(x => x[1]);
  return h("ol.ladder", rungs.map(([k, v]) => h("li", h("div.lk", k), h("div.lv", v))));
}
const STEP_LABEL = { data: "Investigar datos en el modelo", research: "Research", proposal: "Proponer" };
const STEP_ICON = { data: "db", research: "globe", proposal: "spark" };

function taskContext(r) {
  const t = r.task;
  return h("div.panel.pad.taskctx", h("div.row.wrap", h("span.eyebrow.accent", `Tarea ${r.shaping_task || ""} del plan`), h("span.chip.work-" + (t.work || "propuesta"), WORK_LABEL[t.work] || t.work),
      (r.slides || []).map(x => h("span.chip.ghost", "lámina " + x)), h("span.small.faint", "aprobada en Framing & Shaping")),
    r.requested_via ? h("div.small.faint", { style: { marginTop: "6px" } }, "Lanzamiento: " + r.requested_via) : null,
    t.draft_answer ? h("div.draft", { style: { marginTop: "10px" } }, h("div.flab", "Respuesta de arranque", h("span.faint", " · la investigación la valida o la corrige")), h("div.dt", t.draft_answer)) : null,
    (t.hugo_said || []).length ? h("div.said", { style: { marginTop: "8px" } }, h("div.flab", "Lo que ya dijiste"), t.hugo_said.map(x => h("div.sq2", h("span.voice", "“" + x.text + "”"), x.ref ? idTag(x.ref) : null))) : null,
    (t.steps || []).length ? h("div", { style: { marginTop: "8px" } }, h("div.flab", "Cómo se trabaja"), h("ol.stepl", t.steps.map(st => h("li",
      h(`span.sk.${st.kind}`, icon(STEP_ICON[st.kind] || "spark"), STEP_LABEL[st.kind] || st.kind), h("span.sw", st.what),
      (st.where || []).length ? h("span.where", st.where.map(w => h("button.tbl-chip", { type: "button",
        on: { click: () => app.go(`#/data/${(((app.summary || {}).meta || {}).data_model || {}).id || "finora"}/${w}`) } }, w))) : null)))) : null);
}

async function researchAction(r, a, paint) {
  let payload = {};
  if (a.id === "reject") { const n = await confirmDialog({ title: `Reject ${r.id}`, confirmLabel: "Rechazar", field: { label: "Razón", required: true } }); if (!n) return; payload.note = n; }
  if (a.id === "challenge") { const n = await confirmDialog({ title: `Challenge ${r.id}`, text: "¿Qué no te convence? Se lanza una investigación que busca la explicación alternativa.", confirmLabel: "Challenge", field: { label: "Tu objeción", required: true } }); if (!n) return; payload.note = n; }
  if (a.id === "follow_up") { const n = await confirmDialog({ title: `Follow-up de ${r.id}`, confirmLabel: "Crear", field: { label: "Pregunta de seguimiento", required: true } }); if (!n) return; payload.question = n; }
  if (a.id === "research_deeper") { const n = await confirmDialog({ title: `Research deeper · ${r.id}`, text: "Sube un nivel de intensidad.", confirmLabel: "Research deeper", field: { label: "Qué profundizar (opcional)" } }); if (n === null) return; payload.note = n === true ? "" : n; }
  if (a.id === "accept") { const n = await confirmDialog({ eyebrow: "Tu juicio", title: `Aceptar ${r.id}`, text: "Se aceptan también sus findings propuestos; quedan como evidencia del caso.", confirmLabel: "Accept", field: { label: "Nota (opcional)" } }); if (n === null) return; payload.note = n === true ? "" : n; }
  try {
    const out = await api.action(r.id, a.id, payload);
    toast(`${a.label} · ${r.id}` + (out.research ? ` → ${out.research.id}` : "") + (out.job_id ? " · COS evaluando" : ""), out.job_id || out.launched ? "agent" : "ok");
    await app.refresh();
    if (out.research && out.research.id) app.go("#/research/" + out.research.id); else paint();
  } catch (e) { toast(e.message, "err", 7000); }
}

function findingCard(f, paint) {
  const rv = (f.review || {}).state;
  const card = h("div.finding",
    h("div.row.between", h("div.row.wrap", idTag(f.id, { alias: f.alias }), f.confidence ? h("span.chip", "confianza " + f.confidence) : null, f.epistemic_state ? h("span.chip.ghost", f.epistemic_state) : null, f.unverified ? h("span.chip.bad", "fuente sin verificar") : null),
      review(rv, !!f.stale)),
    h("div.hl", f.headline),
    f.evidence_text ? h("div.sub", h("span.k", "Evidencia"), h("span.small", f.evidence_text)) : null,
    (f.claims || []).length ? h("div.sub", h("span.k", "Fuentes"), h("span.small.muted", [...new Set(f.claims.map(c => `${c.source_id}${c.unverified ? " ⚠" : ""}`))].join(" · "))) : null,
    (f.limitations || []).length ? h("div.sub", h("span.k", "Límites"), h("span.small.muted", f.limitations.join(" · "))) : null,
    h("div.row.wrap", rv !== "accepted" ? btn("Accept", { sm: true, icon: "check", variant: "primary", onClick: async () => { await api.action(f.id, "accept"); toast(`${f.id} aceptado`, "ok"); await app.refresh(); paint(); } }) : null,
      btn("Challenge", { sm: true, icon: "flag", onClick: async () => { const n = await confirmDialog({ title: `Challenge ${f.id}`, confirmLabel: "Challenge", field: { label: "Tu objeción", required: true } }); if (!n) return; await api.action(f.id, "challenge", { note: n }); toast("El Framer lo va a intentar romper", "agent"); } }),
      f.kind === "analytics" ? btn("Send to COS as table", { sm: true, icon: "orbit", onClick: async () => { const out = await api.action(f.id, "send_to_cos"); toast(`${f.id} → tabla ${out.table || ""} · COS evaluando impacto`, "agent"); await app.refresh(); paint(); } })
        : btn("Send to COS", { sm: true, icon: "orbit", onClick: async () => { await api.action(f.id, "send_to_cos"); toast("COS evaluando impacto", "agent"); await app.refresh(); } }),
      btn("Detalle", { sm: true, variant: "ghost", onClick: () => app.openEntity(f.id) })));
  if (f.visual) { const w = h("div.viz", h("div.legend"), h("div.chart")); card.insertBefore(w, card.children[2]); requestAnimationFrame(() => renderVisual(w.querySelector(".chart"), f.visual, w.querySelector(".legend"))); }
  return card;
}

function bucketList(title, items, cls) {
  const xs = (items || []).filter(Boolean);
  return h("div.bucket." + cls, h("h4", title), xs.length ? h("ul", xs.map(x => h("li", typeof x === "string" ? x : JSON.stringify(x)))) : h("div.small.faint", "—"));
}

function specialistBlock(r) {
  const s = r.specialist || {};
  if (s.measurement) {
    const m = s.measurement;
    return h("div.mt2", h("h2.sec.mb", "Diseño de medición"),
      h("div.grid2", h("div.panel.pad", h("h3.sub", "Interpretación del problema"), h("p.prose", m.problem_interpretation), h("h3.sub", "Objetivo de medición"), h("p.prose", m.measurement_objective),
        h("h3.sub", "Decisión que habilita"), h("p.prose", m.decision_enabled)),
        h("div.panel.pad.glow", h("div.eyebrow.accent", "Framework recomendado"), h("div", { style: { fontSize: "18px", fontWeight: 600, margin: "8px 0" } }, (m.recommended_framework || {}).name),
          h("p.prose", (m.recommended_framework || {}).structure), h("p.small.muted", (m.recommended_framework || {}).why),
          (m.alternative_frameworks || []).map(a => h("div.frame", { style: { marginTop: "8px" } }, h("span.n", a.name), h("div.small.muted", `Mejor cuando: ${a.when_better}`), h("div.small.faint", `Trade-off: ${a.tradeoff}`))))),
      h("div.panel.flush.mt", h("div.phead", h("h2.sec", "Definiciones de métricas")), h("div.pbody", h("table.spec-table", h("thead", h("tr", h("th", "Métrica"), h("th", "Definición"), h("th", "Fórmula"), h("th", "Grano"), h("th", "Hito"))),
        h("tbody", (m.metric_definitions || []).map(d => h("tr", h("td", d.metric), h("td", d.definition), h("td.mono", d.formula), h("td", d.grain), h("td", d.milestone))))))),
      h("div.grid2.mt", h("div.panel.pad", h("h3.sub", "Eventos requeridos"), (m.required_events || []).map(e => h("div.small", { style: { padding: "5px 0", borderBottom: "1px solid var(--line)" } }, h("span.mono", { style: { color: "var(--accent-ink)" } }, e.event), " — ", e.trigger, h("span.faint", (e.properties || []).length ? ` · ${e.properties.join(", ")}` : "")))),
        h("div.panel.pad", h("h3.sub", "Dimensiones requeridas"), (m.required_dimensions || []).map(d => h("div.small", { style: { padding: "5px 0", borderBottom: "1px solid var(--line)" } }, h("span.mono", d.dimension), " — ", h("span.muted", d.why))))),
      h("div.grid2.mt", bucketList("Limitaciones", m.limitations, "un"), bucketList("Implicaciones de implementación", m.implementation_implications, "pl")));
  }
  if (s.data_model) {
    const m = s.data_model;
    return h("div.mt2", h("h2.sec.mb", "Modelo de datos"),
      h("div.panel.pad", h("h3.sub", "Modelo conceptual"), h("p.prose", m.conceptual_model), h("div.small", h("span.muted", "Grano: "), m.grain)),
      h("div.entity-map.mt", (m.entities || []).map(e => h("div.entity-box", h("div.en", e.name), h("div.small", e.description), h("div.eg", `grano: ${e.grain} · PK: ${e.primary_key}`)))),
      h("div.panel.flush.mt", h("div.phead", h("h2.sec", "Campos")), h("div.pbody", h("table.spec-table", h("thead", h("tr", h("th", "Entidad"), h("th", "Campo"), h("th", "Tipo"), h("th", "Definición"), h("th", "Ejemplo"))),
        h("tbody", (m.fields || []).map(f => h("tr", h("td", f.entity), h("td.mono", f.field), h("td", f.type), h("td", f.definition), h("td.mono", f.example))))))),
      h("div.grid2.mt", h("div.panel.pad", h("h3.sub", "Comportamiento temporal"), h("p.prose", m.temporal_behavior)),
        h("div.panel.pad", h("h3.sub", "Lógica de clasificación"), (m.classification_logic || []).map(c => h("div.small", { style: { padding: "5px 0", borderBottom: "1px solid var(--line)" } }, h("b", c.case), " → ", c.rule)))),
      (m.example_records || []).map(x => h("div.panel.flush.mt", h("div.phead", h("h2.sec", `Registros de ejemplo · ${x.entity}`)), h("div.pbody", h("table.spec-table", h("thead", h("tr", (x.columns || []).map(c => h("th", c)))),
        h("tbody", (x.rows || []).map(rw => h("tr", rw.map(v => h("td.mono", v))))))))),
      h("div.grid3.mt", bucketList("Casos borde", m.edge_cases, "co"), bucketList("Reglas de calidad de datos", m.data_quality_rules, "hc"), bucketList("Implementación", m.implementation_considerations, "pl")),
      (m.business_definitions || []).length ? h("div.panel.pad.mt", h("h3.sub", "Definiciones de negocio"), (m.business_definitions || []).map(d => h("div.small", { style: { padding: "4px 0" } }, h("b", d.term), " — ", d.definition))) : null);
  }
  return null;
}
