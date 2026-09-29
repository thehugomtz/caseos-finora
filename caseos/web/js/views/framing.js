// Framing — conversation with the Framer (thinking partner) + the live framing board. Hugo approves the framing.
import { h, mount as put, autosize } from "../core/dom.js";
import { api } from "../core/api.js";
import { icon } from "../core/icons.js";
import { app } from "../app.js";
import { idTag, review, kindChip, statusChip, btn, empty, seg, tabs, toast, thinking, lensChip, hhmm, confirmDialog, KIND_LABEL, STATUS_LABEL } from "../ui/components.js";

const MODES = [
  { id: "organize", label: "Organize", hint: "Ayúdame a ordenar lo que estoy pensando." },
  { id: "advise", label: "Advise", hint: "Ahora dime cómo lo abordarías (2–3 alternativas, lentes C-level)." },
  { id: "challenge", label: "Challenge", hint: "Ahora intenta romper esto (supuestos, contraargumento, evidencia que lo invalidaría)." },
];
const LEDGER = [["FACT", "Hechos"], ["OBSERVATION", "Observaciones"], ["USER_INTUITION", "Intuiciones"], ["ASSUMPTION", "Supuestos"],
  ["HYPOTHESIS", "Hipótesis"], ["QUESTION", "Preguntas"], ["PROPOSAL", "Propuestas"], ["UNKNOWN", "Desconocidos"]];

export async function mount(root) {
  let mode = sessionStorage.getItem("caseos.framer.mode") || "organize";
  let tab = "HYPOTHESIS";
  let data = null;
  const stream = h("div.stream");
  const board = h("div.stack.lg.board");
  const head = h("div");
  const ta = autosize(h("textarea", { placeholder: "Suelta lo que estás pensando, como lo dirías. «Creo que están metiendo más leads pero esa madre no está convirtiendo…»" }));
  const pre = sessionStorage.getItem("caseos.framer.prefill");
  if (pre) { ta.value = pre; sessionStorage.removeItem("caseos.framer.prefill"); }
  const modeBox = h("div");
  const hint = h("div.small.muted");
  const send = async () => {
    const msg = ta.value.trim();
    if (!msg) return;
    ta.value = "";
    ta.dispatchEvent(new Event("input"));
    try { await api.cpost("/framer", { message: msg, mode }); await paint(); } catch (e) { toast(e.message, "err"); ta.value = msg; }
  };
  ta.addEventListener("keydown", e => { if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) send(); });
  const paintMode = () => {
    put(modeBox, seg(MODES, mode, m => { mode = m; sessionStorage.setItem("caseos.framer.mode", m); paintMode(); }));
    hint.textContent = MODES.find(m => m.id === mode).hint;
  };
  paintMode();

  const paint = async () => {
    data = await api.cget("/framing");
    const fr = data.framing, ph = data.phase;
    app.crumbs(["Framing"]);
    put(head, h("div.head",
      h("div", h("div.eyebrow", `02 · Framing · Framer = thinking partner, no consultor sabelotodo`), h("h1.title", "Framing"),
        h("p.lede", "Organiza lo que piensas en tu idioma. El Framer separa hechos de intuiciones, conserva tus palabras junto a la versión estructurada y solo avanza cuando tú apruebas.")),
      h("div.actions", statusChip(ph.status), ph.ready_count ? h("span.small.muted", `v${ph.ready_count} aprobada`) : null,
        ph.ready_count ? btn("Reabrir", { icon: "undo", variant: "ghost", onClick: () => app.reopenPhase("framing") }) : null,
        btn(ph.status === "ready" ? "Framing aprobado" : "Approve Framing · Mark Ready", { variant: "human", human: true, disabled: ph.status === "ready", onClick: () => app.markReady("framing") }))));
    paintStream();
    paintBoard();
  };

  const paintStream = () => {
    const conv = data.conversation;
    put(stream, conv.length ? conv.map(turnView) : h("div.empty", h("b", "Empieza por lo que tienes en la cabeza"), "No tiene que estar ordenado. El Framer captura, clasifica y te devuelve la estructura."));
    requestAnimationFrame(() => { stream.scrollTop = stream.scrollHeight; });
  };

  const turnView = t => {
    const hugo = h("div.turn.turn-h", h("div.who.hugo", `Hugo · ${t.mode} · ${hhmm(t.ts)}`), h("div.bubble", h("div.voice", { style: { fontSize: "15.5px" } }, t.message)));
    let fr;
    if (t.status === "done") {
      const cap = [...(t.created || []), ...(t.updated || [])];
      fr = h("div.turn.turn-f",
        h("div.who", "Framer", h("span.faint", hhmm(t.finished_at)), (t.advisors || []).map(a => lensChip(a.lens)), t.skills ? h("span.faint", `${t.skills.length} skills`) : null),
        h("div.bubble",
          h("div.reply", t.reply),
          t.alternatives && t.alternatives.length ? h("div.stack", { style: { marginTop: "12px" } }, t.alternatives.map((a, i) =>
            h("div.frame", h("div.row", h("span.kind.PROPOSAL", String.fromCharCode(65 + i)), h("span.n", a.name)), h("div.small", a.approach),
              h("div.small.muted", `Gana cuando: ${a.when_it_wins}`), a.cost ? h("div.small.faint", `Costo: ${a.cost}`) : null))) : null,
          t.challenge && (t.challenge.strongest_counterargument || (t.challenge.hidden_assumptions || []).length) ? challengeView(t.challenge) : null,
          (t.advisors || []).length ? h("div.stack", { style: { marginTop: "10px", gap: "6px" } }, t.advisors.map(a => h("div.small", lensChip(a.lens), " ", h("span.muted", a.contribution || a.why)))) : null,
          cap.length ? h("div.captured", h("div.eyebrow", `Capturado · ${cap.length}`), cap.map(id => {
            const e = app.byId[id] || {};
            return h("div.ci", idTag(id), e.type === "note" ? kindChip(e.kind) : h("span.kind." + ({ hypothesis: "HYPOTHESIS", question: "QUESTION", decision: "DECISION" }[e.type] || "OBSERVATION"), ({ hypothesis: "Hipótesis", question: "Pregunta", decision: "Decisión" }[e.type]) || ""), h("span.x.clamp2", e.title || ""));
          })) : null,
          (t.corrections || []).map(c => h("div.corr", "⚑ Guarda epistémica: " + c)),
          (t.next_steps || []).length ? h("div.small.muted", { style: { marginTop: "10px" } }, "Siguiente: " + t.next_steps.join(" · ")) : null,
          t.language && t.language.introduced_terms && t.language.introduced_terms.length ? h("div.small.faint", { style: { marginTop: "6px" } }, "Términos introducidos: " + t.language.introduced_terms.map(x => `${x.term} (${x.plain})`).join("; ")) : null));
    } else if (t.status === "failed") {
      fr = h("div.turn.turn-f", h("div.who", "Framer"), h("div.bubble", { style: { borderColor: "rgba(255,107,118,.35)" } }, h("div.small", "No pude responder: " + (t.error || "error")),
        h("div.small.muted", "Tu mensaje quedó guardado; puedes reintentar."), h("div.mt", btn("Reintentar", { sm: true, icon: "refresh", onClick: async () => { await api.cpost(`/framer/${t.turn_id}/retry`); await paint(); } }))));
    } else {
      fr = h("div.turn.turn-f", h("div.who", "Framer"), h("div.bubble", h("div.row", thinking(), h("span.small.muted", t.status === "running" ? "pensando con " + ((t.skills || []).map(s => s.id).join(" · ") || "sus skills") : "en cola"))));
    }
    return h("div.stack", { style: { gap: "12px" } }, hugo, fr);
  };

  const challengeView = c => h("div.panel.tight.alert", { style: { marginTop: "12px" } }, h("div.eyebrow", { style: { color: "#ff9aa2" } }, "Challenge · executive mentor"),
    h("div.challenge", [["Supuestos ocultos", h("ul.prose", (c.hidden_assumptions || []).map(x => h("li", x)))], ["Contraargumento más fuerte", c.strongest_counterargument],
      ["Explicación alternativa", c.alternative_explanation], ["Evidencia que lo invalidaría", h("ul.prose", (c.invalidating_evidence || []).map(x => h("li", x)))],
      ["Claim de mayor riesgo", c.highest_risk_claim]].filter(r => r[1] && (typeof r[1] !== "string" || r[1].trim())).map(([k, v]) => h("div.c", h("div.k", k), h("div", v)))));

  const paintBoard = () => {
    const fr = data.framing;
    const eq = h("div.eq", { contentEditable: "true", spellcheck: "false", on: { blur: async e => {
      const v = e.target.textContent.trim();
      if (v && v !== fr.executive_question) { await api.cpatch("/framing", { executive_question: v }); toast("Pregunta ejecutiva actualizada (versionada)", "ok"); await paint(); }
    } } }, fr.executive_question || "¿Qué están tratando de decidir o entender los ejecutivos?");
    const led = fr.ledger || {};
    const rows = tab === "HYPOTHESIS" ? fr.hypotheses : tab === "QUESTION" ? fr.open_questions : (led[tab] || []);
    const counts = Object.fromEntries(LEDGER.map(([k]) => [k, k === "HYPOTHESIS" ? fr.hypotheses.length : k === "QUESTION" ? fr.open_questions.length : (led[k] || []).length]));
    put(board,
      h("div.panel.pad.glow", h("div.row.between", h("div.eyebrow.accent", "Executive question"), h("span.small.faint", "editable · se versiona")), h("div", { style: { marginTop: "10px" } }, eq),
        fr.executive_question_note ? h("div.small.faint", { style: { marginTop: "8px" } }, fr.executive_question_note) : null),
      fr.dual && fr.dual.length ? h("div.panel.flush", h("div.phead", h("h2.sec", "Lo que Hugo piensa ↔ interpretación estructurada", h("span.count", String(fr.dual.length)))),
        h("div", fr.dual.slice(0, 7).map(d => h("div.dualrow", { on: { click: () => app.openEntity(d.id) } },
          h("div", { style: { padding: "12px 16px", background: "rgba(233,196,106,.04)", borderRight: "1px solid var(--line)" } }, h("div.row", { style: { marginBottom: "6px" } }, idTag(d.id), d.verbatim === false ? h("span.faint.small", "paráfrasis") : null), h("div.voice", { style: { fontSize: "15px" } }, d.hugo_wording)),
          h("div", { style: { padding: "12px 16px" } }, h("div.small", { style: { color: "var(--ink)" } }, d.structured)))))) : null,
      h("div.panel.flush", h("div", { style: { padding: "6px 14px 0" } }, tabs(LEDGER.map(([k, l]) => ({ id: k, label: l, count: counts[k] })), tab, k => { tab = k; paintBoard(); })),
        h("div", { style: { padding: "0 14px 14px" } }, rows.length ? h("div.ledger", rows.map(r => h("div.lrow", { on: { click: () => app.openEntity(r.id) } },
          r.type === "note" ? kindChip(r.kind) : h("span", idTag(r.id, { alias: r.alias })),
          h("div", h("div.x", r.text), r.falsifier ? h("div.f", "Se debilita si: " + r.falsifier) : null, r.hugo_wording && r.type !== "note" ? h("div.f.serif", { style: { fontStyle: "italic" } }, "“" + r.hugo_wording + "”") : null),
          h("div.row", r.type === "note" ? idTag(r.id) : null, r.status && r.type !== "note" && r.status !== "open" && r.status !== "active" ? statusChip(r.status) : null, review(r.review, r.stale))))) : empty(`Sin ${LEDGER.find(x => x[0] === tab)[1].toLowerCase()}`, "Aparecen aquí cuando el Framer los captura."))),
      h("div.grid2",
        h("div.panel.pad", h("h3.sub", "Frames candidatos"), (fr.candidate_frames || []).length ? h("div.stack", fr.candidate_frames.map(f =>
          h("div.frame" + (f.chosen ? ".chosen" : ""), h("div.row.between", h("span.n", f.name), btn(f.chosen ? "Elegido" : "Elegir", { sm: true, variant: f.chosen ? "human" : "ghost", human: f.chosen,
            onClick: async () => { await api.cpatch("/framing", { choose_frame: f.name }); await paint(); } })), h("div.small.muted", f.description), f.when_it_wins ? h("div.small.faint", f.when_it_wins) : null))) : empty("Sin frames todavía", "Pide Advise al Framer.")),
        h("div.panel.pad", h("h3.sub", "Storyline inicial (provisional)"), (fr.initial_storyline || []).length ? h("div.storyline", fr.initial_storyline.map(s => h("div", h("span", s)))) : empty("Sin storyline todavía"))),
      h("div.panel.pad", h("div.row.between", h("h3.sub", "Research necesario"), h("span.small.faint", "incertidumbres que importan, no temas")),
        (fr.research_needed || []).length ? h("div.list", fr.research_needed.map(r => h("div.item", { style: { gridTemplateColumns: "1fr auto" } },
          h("div.body", h("div.t", r.question), h("div.m", r.why ? h("span", r.why) : null, (r.links || []).slice(0, 4).map(i => idTag(i)))),
          r.status === "sent" ? h("span.row", h("span.chip.agent", "enviado"), r.research_id ? idTag(r.research_id) : null)
            : btn("Enviar a Research", { sm: true, icon: "send", onClick: async () => { const out = await api.cpost(`/framing/research-needed/${r.id}/send`); toast(`${out.research.id} → ${out.launched ? "en cola" : "espera tu decisión"}`, out.launched ? "agent" : "info"); await paint(); } })))) : empty("Nada pendiente")),
      h("div.grid2",
        listPanel("Decisiones necesarias", fr.decisions_needed, "decisions_needed"),
        listPanel("Lo que no debemos afirmar todavía", fr.should_not_claim, "should_not_claim")),
      (fr.stress_test || []).length ? h("details.panel.pad", h("summary", { style: { cursor: "pointer" } }, h("span.sub", { style: { fontWeight: 600 } }, `Stress test del framing (${fr.stress_test.length} puntos)`)),
        h("div.stack", { style: { marginTop: "12px" } }, fr.stress_test.map(p => h("div", h("div", { style: { fontWeight: 560 } }, `${p.n}. ${p.point}`), h("div.small.muted", p.risk), h("div.small", "→ " + p.resolution))))) : null,
      h("div.grid2",
        listPanel("Notas de lenguaje", fr.language_notes, "language_notes"),
        h("div.panel.pad", h("h3.sub", "Perfil de lenguaje observado"), languageView(data.language))));
  };

  const listPanel = (title, items, key) => h("div.panel.pad", h("h3.sub", title), (items || []).length ? h("ul.prose", { style: { margin: 0 } }, items.map((x, i) => h("li", x,
    h("button.btn.ghost.sm", { type: "button", title: "Quitar", style: { marginLeft: "6px", height: "20px", padding: "0 6px" }, on: { click: async () => { await api.cpatch("/framing", { remove: { list: key, index: i } }); await paint(); } } }, "×")))) : h("div.small.muted", "—"));

  put(root, head, h("div.split",
    h("div.convo", h("div.row.between.mb", modeBox, h("span.small.faint", "⌘↵ para enviar")), hint, stream,
      h("div.composer", ta, h("div.bar2", h("span.small.faint", "El Framer responde en tu registro y separa hecho · intuición · hipótesis · pregunta"), h("span.spacer"),
        btn("Enviar", { variant: "primary", icon: "send", onClick: send })))),
    h("div", { style: { minWidth: 0 } }, board)));
  hint.style.margin = "0 0 10px";
  await paint();
  const onJob = ev => { if ((ev.job.kind === "framer_turn" || ev.job.agent === "framer") && ["running", "skills"].includes(ev.event.kind)) paint(); };
  app.on("job", onJob);
  return { update: paint, destroy: () => { app.listeners.job = (app.listeners.job || []).filter(f => f !== onJob); } };
}

function languageView(lang) {
  const o = (lang || {}).observed || {};
  return h("div.stack", { style: { gap: "8px" } },
    h("div.small", h("span.muted", "Registro: "), o.register || "—"), h("div.small", h("span.muted", "Nivel técnico: "), o.technical_level || "—"),
    h("div.small", h("span.muted", "Formalidad: "), o.formality || "—"),
    (o.preserved_terms || []).length ? h("div.row.wrap", { style: { gap: "6px" } }, o.preserved_terms.slice(-18).map(t => h("span.chip.human", t))) : null,
    h("div.small.faint", `primary: ${lang.primary} · preserve_user_vocabulary: ${lang.preserve_user_vocabulary} · avoid_unnecessary_jargon: ${lang.avoid_unnecessary_jargon}`));
}
