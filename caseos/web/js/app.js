// CaseOS web app — shell, router, live state, and the global overlays (entity drawer, ⌘K palette, command bar,
// operational trace, Under the hood, Demo mode). Views live in ./views/*. No framework, no build step.
import { h, $, mount, debounce } from "./core/dom.js";
import { api, events } from "./core/api.js";
import { icon, brandMark } from "./core/icons.js";
import { markdown } from "./ui/markdown.js";
import { idTag, review, kindChip, statusChip, btn, toast, modal, confirmDialog, dataView, kv, ids, typeOf, TYPE_LABEL, STATUS_LABEL,
         PHASE_LABEL, hhmm, ago, empty } from "./ui/components.js";
import { renderVisual, renderEvidenceTable, refreshColors } from "./charts/kit.js";

export const app = {
  caseId: null, summary: null, entities: [], byId: {}, health: null, route: { view: "home", param: null }, current: null,
  running: [], listeners: {}, drawerId: null, demo: null,
  on(ev, fn) { (this.listeners[ev] ||= []).push(fn); },
  emit(ev, d) { (this.listeners[ev] || []).forEach(fn => { try { fn(d); } catch (e) { console.error(e); } }); },
};
window.caseos = app;

const VIEWS = {
  home: () => import("./views/home.js"), briefing: () => import("./views/briefing.js"), framing: () => import("./views/framing.js"),
  research: () => import("./views/research.js"), analytics: () => import("./views/analytics.js"), cos: () => import("./views/cos.js"),
  story: () => import("./views/story.js"), slides: () => import("./views/slides.js"), agents: () => import("./views/agents.js"),
  artifacts: () => import("./views/artifacts.js"),
};
const NAV = [
  { grp: null, items: [{ id: "home", label: "Home", icon: "home" }] },
  { grp: "Case", items: [
    { id: "briefing", label: "Briefing", icon: "brief", phase: "briefing", n: "01" },
    { id: "framing", label: "Framing", icon: "compass", phase: "framing", n: "02" },
    { id: "research", label: "Research", icon: "search", phase: "research", n: "03" },
    { id: "cos", label: "Chief of Staff", icon: "orbit", phase: "synthesis", n: "04" },
    { id: "story", label: "Story", icon: "story", phase: "story", n: "05" },
    { id: "slides", label: "Slides", icon: "slides", phase: "slides", n: "06" }] },
  { grp: "System", items: [
    { id: "analytics", label: "Analytics", icon: "chart" },
    { id: "agents", label: "Agents", icon: "agents" },
    { id: "artifacts", label: "Artifacts", icon: "files" }] },
];
const VIEW_AGENT = { framing: "framer", research: "router", analytics: "analytics", cos: "cos", story: "cos", slides: "visual_storyteller",
  briefing: "framer", home: "cos", agents: "cos", artifacts: "cos" };

/* ------------------------------------------------------------------ boot */
async function boot() {
  refreshColors();
  const root = document.getElementById("app");
  try { app.health = await api.get("/api/health"); } catch (e) { app.health = null; }
  const list = (await api.get("/api/cases")).cases;
  let saved = null;
  try { saved = localStorage.getItem("caseos.case"); } catch (e) { saved = null; }
  app.caseId = (list.find(c => c.id === saved) || list[0] || {}).id || null;
  api.c = app.caseId;
  mount(root, shell(list));
  if (!app.caseId) { newCaseDialog(); return; }
  await loadCase();
  startEvents();
  window.addEventListener("hashchange", route);
  route();
  document.addEventListener("keydown", globalKeys);
}

async function loadCase() {
  const [summary, state] = await Promise.all([api.cget(""), api.cget("/state")]);
  app.summary = summary;
  app.entities = state.entities;
  app.byId = Object.fromEntries(state.entities.map(e => [e.id, e]));
  app.running = summary.running || [];
  paintChrome();
}

let es = null;
function startEvents() {
  if (es) es.close();
  es = events(app.caseId, ev => {
    if (ev.kind === "activity") { traceAdd(ev.entry); refreshSoon(); }
    if (ev.kind === "job") {
      const j = ev.job;
      if (["succeeded", "failed", "interrupted"].includes(ev.event.kind)) {
        if (ev.event.kind === "succeeded") toast(`${j.title}: listo`, "ok");
        else toast(`${j.title}: ${ev.event.kind === "failed" ? "falló — la solicitud se conservó (reintentable)" : "interrumpido"}`, "err", 7000);
        refreshSoon();
      }
      app.emit("job", ev);
      updateLive(ev);
    }
  });
}
const refreshSoon = debounce(async () => { await loadCase(); if (app.current && app.current.update) app.current.update(); else rerender(); if (app.drawerId) openEntity(app.drawerId, true); }, 450);
app.refresh = async () => { await loadCase(); if (app.current && app.current.update) await app.current.update(); };

function updateLive(ev) {
  const j = ev.job;
  if (["queued", "running"].includes(ev.event.kind) || j.status === "running") { if (!app.running.find(x => x.id === j.id)) app.running.push({ ...j, status: "running" }); }
  if (["succeeded", "failed", "interrupted"].includes(ev.event.kind)) app.running = app.running.filter(x => x.id !== j.id);
  paintLive(ev);
}

/* ------------------------------------------------------------------ shell */
function shell(list) {
  const c = list.find(x => x.id === app.caseId) || {};
  return h("div.shell",
    h("aside.rail",
      h("div.brand", brandMark(), h("div.word", "CaseOS ", h("span", "· case room"))),
      h("button.case-switch", { type: "button", on: { click: caseMenu } }, h("span.k", "Caso"), h("span.n", h("span#case-name", c.name || "—"), icon("layers")), h("span.t#case-title", c.title || "")),
      h("nav.nav#nav", NAV.map(g => [g.grp ? h("div.grp", g.grp) : null, g.items.map(it => h("a", { href: "#/" + it.id, dataset: { view: it.id } },
        icon(it.icon), h("span", it.label), it.phase ? h("span.row", { style: { gap: "7px" } }, h("span.num", it.n), h("span.pdot", { dataset: { phase: it.phase } })) : h("span")))])),
      h("div.rail-foot",
        h("button#hood-btn", { type: "button", on: { click: toggleHood } }, icon("hood"), "Under the hood"),
        h("button", { type: "button", on: { click: startDemo } }, icon("demo"), "Demo mode"),
        h("div.auth", "Agentes: ", h("b", app.health ? app.health.auth.split(" (")[0] : "sin conexión")))),
    h("div.main",
      h("header.top",
        h("div.crumbs#crumbs"),
        h("label.cmdbar", icon("spark"), h("input#cmd", { placeholder: "Habla con CaseOS…  «Pregúntale a Measurement qué haría aquí»", autocomplete: "off",
          on: { keydown: e => { if (e.key === "Enter" && e.target.value.trim()) runCommand(e.target.value.trim()); } } }), h("span.kbd", "⌘K")),
        h("div.top-right", h("div.phasebar#phasebar"), h("button.live#live", { type: "button", on: { click: toggleTrace } }, h("span.beat"), h("span#live-t", "Agentes en reposo")))),
      h("main.view#view")),
    h("div.scrim#scrim", { on: { click: closeOverlays } }),
    h("aside.drawer#drawer"),
    h("aside.hood#hood"),
    h("div.trace#trace", h("div.box", h("div.th", h("div.row", h("span.eyebrow.agent", "Operational trace"), h("span.small.muted", "actividad de agentes y decisiones — no expone razonamiento privado")),
      btn("", { icon: "x", variant: "ghost", sm: true, onClick: toggleTrace })), h("div.tb#trace-b"))));
}

function paintChrome() {
  if (!app.summary) return;
  const m = app.summary.meta;
  $("#case-name").textContent = m.name || app.caseId;
  $("#case-title").textContent = m.title || "";
  const ph = Object.fromEntries(app.summary.phases.map(p => [p.id, p]));
  document.querySelectorAll(".pdot[data-phase]").forEach(d => { d.className = "pdot " + (ph[d.dataset.phase] || {}).status; d.title = STATUS_LABEL[(ph[d.dataset.phase] || {}).status] || ""; });
  mount($("#phasebar"), app.summary.phases.map(p => h("i", { class: p.status, title: `${p.n} ${p.label}: ${STATUS_LABEL[p.status]}` })));
  paintLive();
}
function paintLive(ev) {
  const live = $("#live");
  if (!live) return;
  const n = app.running.length;
  live.classList.toggle("on", n > 0);
  $("#live-t").textContent = n ? (n === 1 ? (app.running[0].title || "1 agente trabajando") : `${n} agentes trabajando`) : "Agentes en reposo";
  if (ev && ev.event && ev.event.summary && n) $("#live-t").textContent = ev.event.summary.slice(0, 60);
}

function crumbs(parts) {
  mount($("#crumbs"), h("span", app.summary ? app.summary.meta.name : ""), parts.map(p => [h("span.sep", "/"), typeof p === "string" ? h("b", p) : p]));
}
app.crumbs = crumbs;

/* ------------------------------------------------------------------ router */
async function route() {
  const hash = location.hash.replace(/^#\/?/, "") || "home";
  const [view, ...rest] = hash.split("/");
  const v = VIEWS[view] ? view : "home";
  app.route = { view: v, param: rest.length ? decodeURIComponent(rest.join("/")) : null };
  document.querySelectorAll("#nav a").forEach(a => a.classList.toggle("on", a.dataset.view === v));
  const container = $("#view");
  const mod = await VIEWS[v]();
  if (app.current && app.current.destroy) app.current.destroy();
  container.scrollTop = 0;
  const page = h("div.page");
  mount(container, page);
  try {
    app.current = await mod.mount(page, app.route.param) || {};
  } catch (e) {
    console.error(e);
    mount(page, empty("No se pudo cargar esta vista", e.message));
  }
  if (app.hoodOpen) paintHood();
  if (app.demo) demoSpot();
}
async function rerender() { await route(); }
app.go = hash => { if (location.hash === hash) route(); else location.hash = hash; };

/* ------------------------------------------------------------------ command layer */
async function runCommand(text) {
  const input = $("#cmd");
  input.disabled = true;
  try {
    const ctx = app.drawerId || (app.route.param && typeOf(app.route.param) ? app.route.param : null);
    const out = await api.cpost("/command", { text, context_id: ctx });
    input.value = "";
    await handleCommand(out);
  } catch (e) { toast(e.message, "err"); }
  finally { input.disabled = false; }
}
app.command = runCommand;

async function handleCommand(out) {
  const a = out.action || {};
  if (out.message) toast(out.message, a.job_id ? "agent" : "info", 6000);
  if (a.kind === "open" && a.id) openEntity(a.id);
  else if (a.kind === "open" && a.route) app.go(a.route);
  else if (a.kind === "confirm" && a.confirm === "mark_ready") markReady(a.phase);
  else if (a.kind === "confirm" && a.confirm === "reopen") reopenPhase(a.phase);
  else if (a.kind === "confirm" && a.confirm === "slides") app.go("#/slides");
}

/* ------------------------------------------------------------------ human gates */
export async function markReady(phase) {
  const rd = await api.cget(`/phases`).then(r => r.readiness[phase]);
  const detail = h("div.stack",
    rd.blockers.length ? h("div.panel.alert.tight", h("div.eyebrow", "Bloqueos"), h("ul.prose", rd.blockers.map(b => h("li", b)))) : null,
    rd.warnings.length ? h("div.panel.tight", h("div.eyebrow", "Para tu criterio"), h("ul.prose", rd.warnings.map(w => h("li", w)))) : null,
    h("p.small.muted", { style: { margin: 0 } }, "Al marcar Ready: snapshot del caso · artefacto aprobado versionado · brain.md actualizado · decisión registrada con fecha · se desbloquea la siguiente fase. La versión anterior se conserva."));
  if (!rd.ok) {
    modal({ eyebrow: "Human gate", title: `${PHASE_LABEL[phase]} todavía no puede marcarse Ready`, body: detail, actions: [{ label: "Entendido", variant: "primary" }] });
    return;
  }
  const note = await confirmDialog({ eyebrow: "Human gate · solo Hugo", title: `Marcar ${PHASE_LABEL[phase]} como Ready`, detail, human: true,
    confirmLabel: "Mark Ready", field: { label: "Nota para el registro (opcional)", placeholder: "Por qué está listo…" } });
  if (note === null) return;
  try {
    const r = await api.cpost(`/phases/${phase}/ready`, { note: note === true ? "" : note });
    toast(`${PHASE_LABEL[phase]} Ready (v${r.version}) · snapshot ${r.snapshot.split("/").pop()} · ${r.decision}`, "ok", 6000);
    await app.refresh();
  } catch (e) { toast(e.message, "err", 7000); }
}
export async function reopenPhase(phase) {
  const imp = await api.cget(`/phases/${phase}/impact`);
  const detail = h("div.stack",
    h("div.panel.tight", h("div.eyebrow.human", "Radio de impacto"), h("p", { style: { margin: "6px 0 10px", fontSize: "15px" } }, imp.headline),
      imp.lines.length ? h("div.stack", imp.lines.map(l => h("div.row.wrap", h("span.chip", `${l.count} ${l.label}`), l.accepted ? h("span.small.muted", `${l.accepted} aceptados`) : null, ids(l.ids, 10)))) : null,
      imp.later_ready_phases.length ? h("p.small.muted", `Fases que pasarán a needs_review: ${imp.later_ready_phases.map(p => PHASE_LABEL[p]).join(", ")}`) : null),
    h("p.small.muted", { style: { margin: 0 } }, "Nada se elimina: lo afectado queda marcado needs_review y la reapertura se registra como decisión."));
  const reason = await confirmDialog({ eyebrow: "Human gate · solo Hugo", title: `Reabrir ${PHASE_LABEL[phase]}`, detail, human: true, confirmLabel: "Reabrir",
    field: { label: "Razón (queda en el decision log)", required: true } });
  if (!reason) return;
  try { const r = await api.cpost(`/phases/${phase}/reopen`, { reason }); toast(`${PHASE_LABEL[phase]} reabierta · ${r.affected.length} elementos needs_review · ${r.decision}`, "ok", 6000); await app.refresh(); }
  catch (e) { toast(e.message, "err"); }
}
app.markReady = markReady;
app.reopenPhase = reopenPhase;

/* ------------------------------------------------------------------ entity drawer */
async function openEntity(id, silent) {
  app.drawerId = id;
  const d = $("#drawer");
  if (!silent) { d.classList.add("on"); $("#scrim").classList.add("on"); mount(d, h("div.dh", h("div.eyebrow", "Cargando " + id))); }
  let data;
  try { data = await api.cget(`/entities/${id}`); } catch (e) { mount(d, h("div.dh", h("div.eyebrow", id), h("p", e.message))); return; }
  if (app.drawerId !== id) return;
  const e = data.entity, t = e.type;
  const rv = (e.review || {}).state;
  const head = h("div.dh", btn("", { icon: "x", variant: "ghost", sm: true, onClick: closeOverlays }),
    h("div.row.wrap", idTag(e.id, { alias: e.alias, stale: !!e.stale }), h("span.eyebrow", TYPE_LABEL[t] || t), e.kind && t === "note" ? kindChip(e.kind) : null,
      e.status ? statusChip(e.status) : null, review(rv, !!e.stale), e.confidence ? h("span.chip", "confianza " + e.confidence) : null),
    h("div.big", titleOf(e)));
  const body = h("div.db", drawerBody(e, data), lineageBlock(data.lineage), actionBlock(e, data.actions), provenance(e, data.history));
  d.querySelector(".close");
  mount(d, head, body);
  body.querySelectorAll(".idref").forEach(x => x.addEventListener("click", () => openEntity(x.dataset.id)));
}
app.openEntity = openEntity;
export function titleOf(e) { return e.headline || e.statement || e.text || e.title || e.research_question || e.question || e.id; }

function dsec(title, ...children) { const kids = children.flat().filter(Boolean); return kids.length ? h("div.dsec", h("h4", title), kids) : null; }
function drawerBody(e, data) {
  const t = e.type;
  const out = [];
  if (e.hugo_wording) out.push(h("div.dual", h("div", h("div.h", "Hugo" + (e.verbatim === false ? " (paráfrasis)" : "")), h("div.v", e.hugo_wording)),
    h("div", h("div.h", "Interpretación estructurada"), h("div.s", e.structured || titleOf(e)))));
  if (e.stale) out.push(h("div.panel.tight", { style: { borderColor: "rgba(245,165,36,.35)" } }, h("div.eyebrow", { style: { color: "#ffc766" } }, "needs_review"), h("div.small", e.stale.reason)));
  if (t === "hypothesis") out.push(dsec("Hipótesis", kv([["Pregunta", e.question], ["Se debilita si", e.falsifier || h("span.chip.warn", "sin falsificador")],
    ["Explicación alternativa", e.alternative], ["Evidencia necesaria", e.evidence_needed], ["Capacidad", e.capacity], ["Prioridad", e.priority],
    ["Origen de la idea", (e.idea_origin || []).join(" · ")]])), e.assessed ? dsec("Evaluación del agente (pendiente de tu revisión)", h("div.row.wrap", h("span.chip.accent", e.assessed.state), h("span.small.muted", e.assessed.by)), h("p.prose", e.assessed.reading || "")) : null);
  if (t === "question") out.push(dsec("Pregunta", kv([["Tipo", e.kind], ["Audiencia", e.audience], ["Alcance", e.scope], ["Prioridad", e.priority], ["Por qué importa", e.why_it_matters],
    ["Método", e.method], ["Entregable", e.deliverable], ["Criterio de cierre", e.close_criteria], ["Respondida por", e.answered_by]])),
    e.do_not_conclude && e.do_not_conclude.length ? dsec("No concluir", h("ul.prose", e.do_not_conclude.map(x => h("li", x)))) : null);
  if (t === "research") out.push(dsec("Respuesta corta", h("p.prose", { style: { fontSize: "14.5px", color: "var(--ink)" } }, e.short_answer || "—"),
    btn("Abrir investigación completa", { icon: "arrow", sm: true, onClick: () => { closeOverlays(); app.go("#/research/" + e.id); } })));
  if (t === "finding") {
    if (e.visual) { const wrap = h("div.viz", e.visual_title ? h("div.vt", e.visual_title) : null, h("div.legend"), h("div.chart")); out.push(dsec("Visual", wrap)); requestAnimationFrame(() => renderVisual(wrap.querySelector(".chart"), e.visual, wrap.querySelector(".legend"))); }
    if (e.evidence_values && Object.keys(e.evidence_values).length) out.push(dsec("Evidencia", h("table.spec-table", h("tbody", Object.entries(e.evidence_values).map(([k, v]) => h("tr", h("td", (e.evidence_labels || {})[k] || k), h("td.n", String(v))))))));
    if (e.evidence_text) out.push(dsec("Evidencia", h("p.prose", e.evidence_text)));
    if (e.claims && e.claims.length) out.push(dsec("Claims y fuentes", e.claims.map(c => h("div.small", { style: { padding: "4px 0" } }, (c.unverified ? "⚠ " : "") + c.claim, h("span.faint", ` · ${c.source_id} · ${c.confidence}`)))));
    if (e.limitations && e.limitations.length) out.push(dsec("Limitaciones", h("ul.prose", e.limitations.map(x => h("li", x)))));
    (data.tables || []).forEach(tb => out.push(dsec(`Tabla canónica ${tb.id} · ${tb.table_key}`, tableBlock(tb))));
  }
  if (t === "table") out.push(dsec("Tabla canónica (contrato de datos)", tableBlock(e)), dsec("Linaje de datos", kv([["Fuente", (e.source || {}).system], ["Dataset", (e.source || {}).dataset],
    ["Transformación", e.transformation], ["Filtros", (e.filters || []).join("; ")], ["Periodo", e.period && (e.period.from || e.period.desde) ? `${e.period.from || e.period.desde} → ${e.period.to || e.period.hasta}` : ""],
    ["Grano", e.grain], ["Análisis", e.analysis_id], ["Visual preferido", e.preferred_visual], ["Creada", e.created_at]])),
    e.definitions && Object.keys(e.definitions).length ? dsec("Definiciones", kv(Object.entries(e.definitions))) : null,
    dsec("Limitaciones", h("ul.prose", (e.limitations || []).map(x => h("li", x)))), e.query ? dsec("Consulta", h("pre.raw", e.query)) : null);
  if (t === "decision") out.push(dsec("Decisión", kv([["Fecha", e.date], ["Contexto", e.context], ["Recomendación del agente", e.agent_recommendation], ["Elección de Hugo", e.user_choice],
    ["Razón", e.user_rationale], ["Impacto aguas abajo", e.downstream_impact], ["Tipo", e.kind], ["Reemplaza a", e.supersedes], ["Reemplazada por", e.superseded_by], ["Nota", e.confirm_note || e.superseded_note]])),
    e.options && Object.keys(e.options).length ? dsec("Opciones", kv(Object.entries(e.options))) : null,
    e.do_not_resurface && e.do_not_resurface.length ? dsec("No volver a proponer", h("ul.prose", e.do_not_resurface.map(x => h("li", x)))) : null);
  if (t === "claim") {
    const s = data.strength || {};
    out.push(dsec("Claim", kv([["Pregunta", e.question], ["Respuesta", e.answer], ["Rol", e.role_in_story], ["Confianza", e.confidence], ["Intención visual", e.visual_intent]])),
      dsec("Fuerza", h("div.row.wrap", statusChip(s.level === "supported" ? "supported" : s.level === "weak" ? "weak" : s.level === "proposal" ? "proposed" : "unsupported"),
        s.unsupported_numbers && s.unsupported_numbers.length ? h("span.chip.bad", "cifras sin tabla: " + s.unsupported_numbers.join(", ")) : null)),
      dsec("Limitaciones", h("ul.prose", (e.limitations || []).map(x => h("li", x)))));
  }
  if (t === "alert") out.push(dsec("Alerta del COS", h("p.prose", e.why || ""), kv([["Evidencia", e.source], ["Afecta a", e.target], ["Efecto", e.effect], ["Severidad", e.severity]])));
  if (t === "note") out.push(dsec("Idea", kv([["Tipo", e.kind], ["Base", e.basis], ["Reclasificada desde", e.reclassified_from]])));
  if (t === "slide") out.push(dsec("Slide", kv([["Deck", e.deck], ["Claim", e.claim_id], ["Composición", e.composition], ["Familia", e.family], ["QA", e.qa_verdict]])),
    e.render ? h("img", { src: `/case-files/${app.caseId}/decks/${e.render.split("/decks/")[1]}`, style: { width: "100%", borderRadius: "10px", border: "1px solid var(--line)" } }) : null);
  if (e.challenges && e.challenges.length) out.push(dsec("Challenges de Hugo", e.challenges.map(c => h("div.small", `${hhmm(c.at)} · ${c.text}`))));
  return out;
}
export function tableBlock(tb) {
  const wrap = h("div.stack", h("div.small.muted", tb.message || ""), h("div.legend"), h("div.chart"),
    h("details", h("summary.small.muted", { style: { cursor: "pointer" } }, `Ver tabla (${(tb.rows || []).length} filas)`),
      h("div.tablewrap", { style: { maxHeight: "260px", overflowY: "auto", marginTop: "8px" } }, h("table.tbl", h("thead", h("tr", (tb.columns || []).map(c => h("th", c)))),
        h("tbody", (tb.rows || []).slice(0, 200).map(r => h("tr", r.map(v => h("td", v === null ? "–" : String(v))))))))));
  requestAnimationFrame(() => renderEvidenceTable(wrap.querySelector(".chart"), tb, wrap.querySelector(".legend")));
  return wrap;
}
function lineageBlock(lg) {
  const order = ["question", "hypothesis", "note", "research", "finding", "table", "alert", "decision", "claim", "slide", "artifact"];
  const groups = order.filter(k => (lg.groups || {})[k] && lg.groups[k].length);
  if (!groups.length) return dsec("Linaje", h("div.small.muted", "Sin enlaces todavía."));
  return dsec("Linaje · Pregunta → Hipótesis → Research → Evidencia → Decisión → Claim → Slide",
    h("div.lineage", groups.map(k => h("div.lg", h("span.lab", TYPE_LABEL[k]), h("div.ids", lg.groups[k].slice(0, 14).map(x => idTag(x.id, { stale: x.stale, title: x.title })),
      lg.groups[k].length > 14 ? h("span.faint.small", "+" + (lg.groups[k].length - 14)) : null)))));
}
function actionBlock(e, actions) {
  if (!actions || !actions.length) return null;
  const run = async (a) => {
    let payload = {};
    if (a.id === "reject" || a.id === "revert") { const n = await confirmDialog({ title: `${a.label} ${e.id}`, confirmLabel: a.label, field: { label: "Razón (queda en el historial)", required: true } }); if (!n) return; payload.note = n; }
    if (a.id === "challenge") { const n = await confirmDialog({ title: `Challenge ${e.id}`, text: "¿Qué no te convence? El sistema buscará otra explicación.", confirmLabel: "Challenge", field: { label: "Tu objeción", required: true } }); if (!n) return; payload.note = n; }
    if (a.id === "follow_up") { const n = await confirmDialog({ title: `Seguimiento de ${e.id}`, confirmLabel: "Crear", field: { label: "Pregunta de seguimiento", required: true } }); if (!n) return; payload.question = n; }
    if (a.id === "research_deeper") { const n = await confirmDialog({ title: `Research deeper · ${e.id}`, text: "Sube un nivel de intensidad (L1→L2→L3).", confirmLabel: "Research deeper", field: { label: "Qué quieres profundizar (opcional)" } }); if (n === null) return; payload.note = n === true ? "" : n; }
    if (a.id === "confirm") { const n = await confirmDialog({ eyebrow: "Decisión · solo Hugo", title: `Confirmar ${e.id}`, text: e.title, human: true, confirmLabel: "Confirmar decisión", field: { label: "Razón (opcional)" } }); if (n === null) return; payload.note = n === true ? "" : n; }
    if (a.id === "resolve") { resolveAlert(e); return; }
    try {
      const out = await api.action(e.id, a.id, payload);
      const r = out.research || out.entity || out.table || out.finding;
      toast(`${a.label}: ${e.id}${r && r.id && r.id !== e.id ? " → " + r.id : ""}`, "ok");
      if (out.job_id || (out.launched)) toast("Un agente está trabajando en ello (mira el trace).", "agent");
      await app.refresh();
      if (r && r.id && r.id !== e.id && a.id !== "accept") openEntity(r.id); else openEntity(e.id, true);
    } catch (err) { toast(err.message, "err", 7000); }
  };
  const primary = ["accept", "confirm", "clear_stale"];
  return dsec("Acciones", h("div.row.wrap", actions.map(a => btn(a.label, { sm: true, variant: primary.includes(a.id) ? (a.id === "confirm" ? "human" : "primary") : a.id === "reject" || a.id === "revert" ? "danger" : "",
    human: a.id === "confirm", onClick: () => run(a) }))));
}
export async function resolveAlert(x) {
  const opts = (x.options || []).map(o => ({ key: o.key, label: o.label, c: o.consequence }));
  const all = opts.concat([{ key: "discuss", label: "Discutirlo con el Framer" }, { key: "research", label: "Investigar más" }, { key: "ignore", label: "Sin impacto material (ignorar)" }]);
  let picked = x.recommended || (opts[0] || {}).key;
  const list = h("div.stack");
  const paint = () => mount(list, all.map(o => h("div.frame" + (picked === o.key ? ".chosen" : ""), { style: { cursor: "pointer" }, on: { click: () => { picked = o.key; paint(); } } },
    h("div.row", h("span.kind.QUESTION", o.key), h("span.n", o.label), x.recommended === o.key ? h("span.chip.accent", "recomendación del COS") : null), o.c ? h("div.small.muted", o.c) : null)));
  paint();
  const why = h("textarea", { placeholder: "Por qué (queda en el decision log)" });
  modal({ eyebrow: "Decisión · solo Hugo", title: x.title || `Resolver ${x.id}`, body: h("div.stack", h("p.prose", x.why || ""), list, h("div.field", h("label", "Razón"), why)),
    actions: [{ label: "Cancelar", variant: "ghost" }, { label: "Decidir", variant: "human", human: true, onClick: async () => {
      try {
        const out = await api.action(x.id, "resolve", { choice: picked, note: why.value });
        toast(`Decisión ${out.decision} registrada`, "ok");
        if (out.research_prefill) app.go("#/research?q=" + encodeURIComponent(out.research_prefill.question));
        if (out.framer_prefill) { sessionStorage.setItem("caseos.framer.prefill", out.framer_prefill); app.go("#/framing"); }
        await app.refresh();
      } catch (e) { toast(e.message, "err"); return false; }
    } }] });
}
app.resolveAlert = resolveAlert;
function provenance(e, history) {
  const o = e.origin || {};
  return dsec("Origen y versiones", kv([["Creado por", o.actor], ["Fuente", o.source], ["Corrida", o.run_id], ["Nota", o.note], ["Creado", e.created_at], ["Versión", e.version]]),
    history && history.length ? h("div.history", history.map(v => h("div", `v${v.version} · ${hhmm(v.updated_at)} ${new Date(v.updated_at || Date.now()).toLocaleDateString("es")}`))) : null,
    h("div.small.faint", `Archivo: cases/${app.caseId}/…/${e.id}.yaml`));
}

function closeOverlays() {
  $("#drawer").classList.remove("on");
  $("#scrim").classList.remove("on");
  app.drawerId = null;
  if (app.hoodOpen) toggleHood();
}

/* ------------------------------------------------------------------ ⌘K palette */
let palEl = null;
function openPalette() {
  if (palEl) return;
  const input = h("input", { placeholder: "Busca findings, preguntas, decisiones, research, tablas… o escribe un comando" });
  const res = h("div.res");
  let items = [], sel = 0;
  const views = [["Home", "#/home"], ["Briefing", "#/briefing"], ["Framing", "#/framing"], ["Research", "#/research"], ["Analytics", "#/analytics"],
    ["Chief of Staff", "#/cos"], ["Story", "#/story"], ["Slides", "#/slides"], ["Agents", "#/agents"], ["Artifacts", "#/artifacts"], ["brain.md", "#/artifacts/brain.md"]];
  const paint = () => {
    mount(res, items.length ? null : h("div.g", "Sin resultados"), groupBy(items).map(([g, list]) => [h("div.g", g), list.map(it => {
      const i = items.indexOf(it);
      return h("div.r" + (i === sel ? ".on" : ""), { on: { mouseenter: () => { sel = i; paint(); }, click: () => choose(it) } },
        it.id ? idTag(it.id) : h("span.kind.PROPOSAL", it.tag || "→"), h("span.tt", it.title), h("span.h", it.hint || ""));
    })]));
  };
  const search = debounce(async () => {
    const q = input.value.trim();
    const r = await api.cget("/search?q=" + encodeURIComponent(q));
    const v = views.filter(([n]) => !q || n.toLowerCase().includes(q.toLowerCase())).map(([n, hsh]) => ({ g: "Ir a", title: n, hint: hsh, go: hsh, tag: "↵" }));
    items = [...r.results.map(x => ({ g: "Caso", id: x.id, title: x.title, hint: [x.alias, x.label].filter(Boolean).join(" · ") })),
      ...r.commands.map(c => ({ g: "Comandos", title: c.label, hint: c.hint, cmd: c, tag: "⌘" })), ...v].slice(0, 40);
    sel = 0;
    paint();
  }, 120);
  const choose = it => {
    close();
    if (it.id) openEntity(it.id);
    else if (it.go) app.go(it.go);
    else if (it.cmd) { const c = $("#cmd"); c.value = it.cmd.template; c.focus(); }
  };
  const close = closePalette;
  input.addEventListener("input", search);
  input.addEventListener("keydown", e => {
    if (e.key === "ArrowDown") { sel = Math.min(items.length - 1, sel + 1); paint(); e.preventDefault(); }
    else if (e.key === "ArrowUp") { sel = Math.max(0, sel - 1); paint(); e.preventDefault(); }
    else if (e.key === "Enter" && items[sel]) choose(items[sel]);
    else if (e.key === "Escape") { e.stopPropagation(); close(); }
  });
  palEl = h("div.palette", { on: { mousedown: e => { if (e.target === palEl) close(); } } }, h("div.box", input, res));
  document.body.append(palEl);
  input.focus();
  search();
}
function closePalette() { if (palEl) { palEl.remove(); palEl = null; } }
function groupBy(items) { const m = new Map(); items.forEach(i => { if (!m.has(i.g)) m.set(i.g, []); m.get(i.g).push(i); }); return [...m.entries()]; }
function globalKeys(e) {
  if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") { e.preventDefault(); openPalette(); }
  else if (e.key === "Escape" && palEl) closePalette();
  else if (e.key === "Escape" && !document.querySelector(".modal-wrap")) closeOverlays();
  else if (app.demo && !document.activeElement.matches("input, textarea") && (e.key === "ArrowRight" || e.key === "ArrowLeft")) demoStep(e.key === "ArrowRight" ? 1 : -1);
}

/* ------------------------------------------------------------------ operational trace */
const ACT_AGENTS = ["framer", "cos", "router", "analytics", "business_research", "measurement", "data_engineering", "visual_storyteller"];
function traceLine(a) {
  const cls = a.actor === "hugo" ? "hugo" : ACT_AGENTS.includes(a.actor) ? "agent" : "";
  const who = a.actor === "hugo" ? "Hugo" : a.actor;
  return h("div.tline" + (a.material ? ".material" : ""), h("span.ts", hhmm(a.ts)), h("span.ac." + (cls || "x"), who), h("span.su", a.summary));
}
function traceAdd(a) { const b = $("#trace-b"); if (b && $("#trace").classList.contains("on")) b.prepend(traceLine(a)); }
async function toggleTrace() {
  const t = $("#trace");
  const on = !t.classList.contains("on");
  t.classList.toggle("on", on);
  if (on) { const r = await api.cget("/activity?limit=120"); mount($("#trace-b"), r.activity.map(traceLine)); }
}
app.toggleTrace = toggleTrace;

/* ------------------------------------------------------------------ Under the hood */
async function toggleHood() {
  app.hoodOpen = !app.hoodOpen;
  $("#hood").classList.toggle("on", app.hoodOpen);
  $("#hood-btn").classList.toggle("on", app.hoodOpen);
  if (app.hoodOpen) paintHood();
}
async function paintHood() {
  const aid = VIEW_AGENT[app.route.view] || "cos";
  const hood = $("#hood");
  mount(hood, h("div.hh", h("div.eyebrow.accent", "Under the hood · arquitectura, no chain-of-thought"), h("div.row.between", h("h3", { style: { margin: "6px 0 0", fontSize: "19px" } }, "Cargando…"), btn("", { icon: "x", variant: "ghost", sm: true, onClick: toggleHood }))));
  const [card, runs] = await Promise.all([api.get("/api/agents/" + aid), api.cget(`/runs?agent=${aid === "router" ? "router" : aid}&limit=1`)]);
  let run = null;
  if (runs.runs.length) { try { run = await api.cget("/runs/" + runs.runs[0].run_id); } catch (e) { run = null; } }
  const sec = (k) => card.sections[k] ? h("div.prose", markdown(card.sections[k], { ids: false })) : null;
  mount(hood,
    h("div.hh", h("div.eyebrow.accent", "Under the hood · arquitectura, no chain-of-thought"),
      h("div.row.between", h("h3", { style: { margin: "6px 0 2px", fontSize: "20px" } }, card.name), btn("", { icon: "x", variant: "ghost", sm: true, onClick: toggleHood })),
      h("div.small.muted", `${card.title || card.short} · modelo ${card.model} · effort ${card.effort || "—"} · contrato ${card.doc_path}`)),
    h("div.hb",
      h("div.dsec", h("h4", "Comportamiento (System behavior)"), sec("System behavior")),
      h("div.dsec", h("h4", "Skills del agente"), h("div", card.skills.map(s => h("div.skillrow", h("span.mode." + s.binding.mode, s.binding.mode), h("span", s.id), h("span.faint.small", s.kind))))),
      run ? h("div.dsec", h("h4", `Última corrida · ${run.run_id}`), kv([["Propósito", run.purpose], ["Duración", Math.round((run.duration_ms || 0) / 1000) + " s"], ["Costo equivalente", run.cost_usd != null ? "US$" + Number(run.cost_usd).toFixed(3) : "—"],
        ["Autenticación", run.auth], ["Herramientas", (run.tools || []).join(", ") || "ninguna (salida estructurada)"]]),
        h("div.small", { style: { marginTop: "8px" } }, "Skills cargadas en esa corrida:"), h("div.row.wrap", (run.skills || []).map(s => h("span.chip" + (s.mode === "lens" ? ".accent" : s.mode === "challenge" ? ".bad" : ""), `${s.id} · ${s.mode}`))),
        run.system_prompt_text ? h("details", h("summary.small", { style: { cursor: "pointer", marginTop: "10px" } }, `Master prompt compuesto (${Math.round(run.system_prompt_text.length / 1000)}k caracteres)`), h("pre", run.system_prompt_text)) : null,
        run.schema ? h("details", h("summary.small", { style: { cursor: "pointer" } }, "Contrato de salida (JSON Schema)"), h("pre", JSON.stringify(run.schema, null, 1).slice(0, 6000))) : null)
        : h("div.dsec", h("h4", "Última corrida"), h("div.small.muted", "Este agente todavía no ha corrido en este caso.")),
      h("div.dsec", h("h4", "Herramientas"), sec("Tools")),
      h("div.dsec", h("h4", "Guardrails"), sec("Guardrails")),
      h("div.dsec", h("h4", "Contrato de entrada"), sec("Inputs")),
      h("div.dsec", h("h4", "Contrato de salida"), sec("Outputs")),
      h("div.dsec", h("h4", "Requiere aprobación de Hugo"), sec("User approval required")),
      h("div.dsec", h("h4", "Rutas de artefactos"), h("div.small.mono", `cases/${app.caseId}/audit/runs/ · audit/prompts/ · audit/activity.jsonl · ${card.doc_path}`))));
}
app.toggleHood = toggleHood;

/* ------------------------------------------------------------------ Demo mode */
const DEMO = [
  { r: "#/home", t: "CaseOS home", c: "Un caso, un estado. La fase actual, lo que espera mi juicio y lo que los agentes están haciendo — no métricas de vanidad.", s: ".phases" },
  { r: "#/agents", t: "Agent topology", c: "No es un chatbot con prompts distintos: Framer, COS, Research Router y especialistas sobre el mismo caso. Los rombos dorados son mis gates.", s: ".topo" },
  { r: "#/framing", t: "Framing conversation", c: "Le hablo como hablo. El Framer separa hechos, intuiciones, hipótesis y preguntas, y conserva mis palabras junto a la versión estructurada.", s: ".convo" },
  { r: "#/agents/framer", t: "Framer skills", c: "Core + dinámicas + challenge-only. Los advisors C-level son lentes que el Framer consulta; él conserva la síntesis.", s: ".agentcard" },
  { r: "#/framing", t: "Approved framing artifact", c: "El framing vivo es un artefacto: se aprueba con Mark Ready, se versiona y se congela en un snapshot.", s: ".board" },
  { r: "#/research", t: "Research queue", c: "Nada se investiga sin propósito de caso. Cada pregunta se rutea por intensidad (L1/L2/L3) y especialista.", s: ".rq" },
  { r: "#/research", t: "Specialist research", c: "Cada resultado termina en una síntesis para ESTE caso: respuesta corta, evidencia, fuentes calificadas, qué no sabemos y qué cambia en la historia.", s: ".rq" },
  { r: "#/analytics", t: "Analytics Workspace", c: "El workspace de exploración existente, reutilizado: investigaciones con gráficas para mí y tablas canónicas con linaje para el COS.", s: ".runs" },
  { r: "#/cos", t: "COS control room", c: "El Chief of Staff sabe qué pasa en todo el caso: next best actions, alertas de impacto con opciones, hipótesis y readiness. Recomienda; yo decido.", s: ".nbas" },
  { r: "#/artifacts/brain.md", t: "brain.md", c: "La memoria ejecutiva viva: se regenera ante cada cambio material. Solo lo relevante, con IDs.", s: ".paper" },
  { r: "#/artifacts/decisions", t: "Decision log", c: "Cada decisión material: contexto, opciones, recomendación del agente, mi elección y mi razón, impacto aguas abajo.", s: ".files" },
  { r: "#/story", t: "Story Package", c: "Claims con evidencia aceptada y cada cifra en una tabla. Si un número no está en una tabla, no pasa la validación.", s: ".spine" },
  { r: "#/slides", t: "Visual Storyteller", c: "El Story Package aprobado va al Executive Visual Storyteller existente — sus skills, su pipeline, su QA visual.", s: ".handoff" },
  { r: "#/slides", t: "Final HTML presentation", c: "El deck final, trazable: cada slide sabe qué claim prueba y de qué evidencia viene.", s: ".deckframe" },
];
function startDemo() { app.demo = { i: 0 }; paintDemo(); app.go(DEMO[0].r); }
function demoStep(d) { if (!app.demo) return; app.demo.i = Math.max(0, Math.min(DEMO.length - 1, app.demo.i + d)); paintDemo(); app.go(DEMO[app.demo.i].r); }
function paintDemo() {
  document.querySelector(".demo")?.remove();
  if (!app.demo) return;
  const s = DEMO[app.demo.i];
  document.body.append(h("div.demo", h("div.st", `Demo · ${app.demo.i + 1} / ${DEMO.length}`), h("div.ti", s.t), h("div.ca", s.c),
    h("div.nav2", h("div.dots", DEMO.map((_, i) => h("i" + (i === app.demo.i ? ".on" : "")))),
      btn("Anterior", { sm: true, variant: "ghost", onClick: () => demoStep(-1) }), btn(app.demo.i === DEMO.length - 1 ? "Terminar" : "Siguiente", { sm: true, variant: "human", onClick: () => app.demo.i === DEMO.length - 1 ? endDemo() : demoStep(1) }),
      btn("", { icon: "x", sm: true, variant: "ghost", onClick: endDemo }))));
}
function demoSpot() {
  document.querySelectorAll(".spot").forEach(x => x.classList.remove("spot"));
  const s = DEMO[app.demo.i];
  setTimeout(() => { const el = document.querySelector(s.s); if (el) { el.classList.add("spot"); el.scrollIntoView({ behavior: "smooth", block: "center" }); } }, 500);
}
function endDemo() { app.demo = null; document.querySelector(".demo")?.remove(); document.querySelectorAll(".spot").forEach(x => x.classList.remove("spot")); }
app.startDemo = startDemo;

/* ------------------------------------------------------------------ cases */
async function caseMenu() {
  const list = (await api.get("/api/cases")).cases;
  const body = h("div.stack", list.map(c => h("div.frame" + (c.id === app.caseId ? ".chosen" : ""), { style: { cursor: "pointer" }, on: { click: () => { switchCase(c.id); m.close(); } } },
    h("div.row.between", h("span.n", c.name), h("span.row", Object.values(c.phases).map(s => h("span.pdot." + s)))), h("div.small.muted", c.title || ""))),
    btn("Nuevo caso", { icon: "plus", onClick: () => { m.close(); newCaseDialog(); } }));
  const m = modal({ eyebrow: "Casos", title: "Cambiar de caso", body, actions: [{ label: "Cerrar", variant: "ghost" }] });
}
function switchCase(id) { try { localStorage.setItem("caseos.case", id); } catch (e) { /* private mode */ } location.hash = "#/home"; location.reload(); }
function newCaseDialog() {
  const f = {};
  const field = (k, label, opts = {}) => h("div.field", h("label", label), f[k] = h(opts.multi ? "textarea" : "input", { placeholder: opts.ph || "" }));
  modal({ eyebrow: "CaseOS", title: "Nuevo caso", body: h("div", h("p.small.muted", "CaseOS no está atado a Finora: cada caso tiene su brief, su framing, su estado y su memoria."),
    field("name", "Nombre del caso"), field("objective", "Objetivo (qué hay que decidir o entender)", { multi: true }), field("audience", "Audiencia (separada por comas)", { ph: "CEO, CFO" }),
    field("deliverables", "Entregables (separados por ;)"), field("brief", "Texto del brief (pégalo tal cual)", { multi: true })),
    actions: [{ label: "Cancelar", variant: "ghost" }, { label: "Crear caso", variant: "primary", onClick: async () => {
      try {
        const r = await api.post("/api/cases", { name: f.name.value.trim(), objective: f.objective.value.trim(), audience: f.audience.value.split(",").map(s => s.trim()).filter(Boolean),
          deliverables: f.deliverables.value.split(";").map(s => s.trim()).filter(Boolean), brief_text: f.brief.value });
        switchCase(r.id);
      } catch (e) { toast(e.message, "err"); return false; }
    } }] });
}
app.newCase = newCaseDialog;

boot().catch(e => { console.error(e); document.getElementById("app").textContent = "CaseOS no pudo arrancar: " + e.message; });
