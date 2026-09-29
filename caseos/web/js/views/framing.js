// Framing & Shaping — conversation with the Framer (thinking partner) on the left; on the right, the Shaping document it
// builds with Hugo: problem, executive question, storyline guide (sections → slides), hypotheses, a research plan typed
// by agent, and the limits. The Framer proposes; Hugo approves, edits or discards each piece, and approves the whole
// document with Mark Ready. Approved research tasks show up in Research, ready to launch.
import { h, mount as put, autosize } from "../core/dom.js";
import { api } from "../core/api.js";
import { icon } from "../core/icons.js";
import { app } from "../app.js";
import { markdown } from "../ui/markdown.js";
import { idTag, review, kindChip, statusChip, btn, empty, seg, tabs, toast, thinking, lensChip, hhmm, modal, confirmDialog } from "../ui/components.js";

const MODES = [
  { id: "organize", label: "Organize", hint: "Ayúdame a ordenar lo que estoy pensando." },
  { id: "advise", label: "Advise", hint: "Ahora dime cómo lo abordarías (2–3 alternativas, lentes C-level)." },
  { id: "challenge", label: "Challenge", hint: "Ahora intenta romper esto (supuestos, contraargumento, evidencia que lo invalidaría)." },
];
const LEDGER = [["FACT", "Hechos"], ["OBSERVATION", "Observaciones"], ["USER_INTUITION", "Intuiciones"], ["ASSUMPTION", "Supuestos"],
  ["QUESTION", "Preguntas"], ["PROPOSAL", "Propuestas"], ["UNKNOWN", "Desconocidos"]];
const KIND_ICON = { data: "chart", research: "globe", measurement: "ruler", data_model: "db" };
const WORK_ICON = { propuesta: "spark", datos: "table", research: "globe" };
const STEP_ICON = { data: "db", research: "globe", proposal: "spark" };
const STATE = { empty: ["vacío", "ghost"], proposed: ["propuesta", "agent"], revision: ["cambio propuesto", "agent"], approved: ["aprobado", "good"],
  sent: ["en Research", "accent"] };
const K = k => encodeURIComponent(k);
const csv = v => String(v || "").split(/[,\n]/).map(x => x.trim()).filter(Boolean);
const lines = v => String(v || "").split("\n").map(x => x.trim()).filter(Boolean);
const domId = key => "sh-" + key.replace(":", "-").replace(/\./g, "_");

export async function mount(root) {
  let mode = sessionStorage.getItem("caseos.framer.mode") || "organize";
  let tab = "FACT";
  let data = null;
  let editing = null;                                   // shaping key being edited inline ("problem", "guion:S2", "plan:new"…)
  const drafts = {};                                    // what Hugo is typing survives live repaints
  let focusNext = null;                                 // data-f of the field to focus after the next repaint
  const opened = new Set(load("caseos.shaping.open", []));
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
    const ph = data.phase;
    app.crumbs(["Framing & Shaping"]);
    put(head, h("div.head",
      h("div", h("div.eyebrow", "02 · Framing & Shaping · el Framer piensa contigo; tú apruebas el documento"), h("h1.title", "Framing & Shaping"),
        h("p.lede", "Habla como piensas. El Framer separa hechos de intuiciones y va armando contigo el documento de Shaping: el problema, tu guion de la historia, las hipótesis y el plan de investigación por agente. Cada pieza entra solo cuando tú la apruebas.")),
      h("div.actions", statusChip(ph.status), ph.ready_count ? h("span.small.muted", `v${ph.ready_count} aprobada`) : null,
        ph.ready_count ? btn("Reabrir", { icon: "undo", variant: "ghost", onClick: () => app.reopenPhase("framing") }) : null,
        btn(ph.status === "ready" ? "Shaping aprobado" : "Aprobar Shaping · Mark Ready", { variant: "human", human: true, disabled: ph.status === "ready", onClick: () => app.markReady("framing") }))));
    paintStream();
    paintBoard();
  };

  // ------------------------------------------------------------ conversation
  const paintStream = () => {
    const conv = data.conversation;
    put(stream, conv.length ? conv.map(turnView) : h("div.empty", h("b", "Empieza por lo que tienes en la cabeza"), "No tiene que estar ordenado. El Framer captura, clasifica y te propone las piezas del documento."));
    requestAnimationFrame(() => { stream.scrollTop = stream.scrollHeight; });
  };

  const turnView = t => {
    const hugo = h("div.turn.turn-h", h("div.who.hugo", `Hugo · ${t.mode} · ${hhmm(t.ts)}`), h("div.bubble", h("div.voice", { style: { fontSize: "15.5px" } }, t.message)));
    let fr;
    if (t.status === "done") {
      const cap = [...(t.created || []), ...(t.updated || [])];
      const shp = t.shaping_proposed || [];
      fr = h("div.turn.turn-f",
        h("div.who", "Framer", h("span.faint", hhmm(t.finished_at)), (t.advisors || []).map(a => lensChip(a.lens)), t.skills ? h("span.faint", `${t.skills.length} skills`) : null),
        h("div.bubble",
          h("div.reply", t.reply),
          t.alternatives && t.alternatives.length ? h("div.stack", { style: { marginTop: "12px" } }, t.alternatives.map((a, i) =>
            h("div.frame", h("div.row", h("span.kind.PROPOSAL", String.fromCharCode(65 + i)), h("span.n", a.name)), h("div.small", a.approach),
              h("div.small.muted", `Gana cuando: ${a.when_it_wins}`), a.cost ? h("div.small.faint", `Costo: ${a.cost}`) : null))) : null,
          t.challenge && (t.challenge.strongest_counterargument || (t.challenge.hidden_assumptions || []).length) ? challengeView(t.challenge) : null,
          (t.advisors || []).length ? h("div.stack", { style: { marginTop: "10px", gap: "6px" } }, t.advisors.map(a => h("div.small", lensChip(a.lens), " ", h("span.muted", a.contribution || a.why)))) : null,
          shp.length ? h("div.captured", h("div.eyebrow", `Propuso para el documento · ${shp.length}`), h("div.row.wrap", { style: { gap: "6px" } },
            shp.map(k => h("button.chip.agent", { type: "button", style: { cursor: "pointer" }, on: { click: () => focusCard(k) } }, keyLabel(k))))) : null,
          cap.length ? h("div.captured", h("div.eyebrow", `Capturado · ${cap.length}`), cap.map(id => {
            const e = app.byId[id] || {};
            return h("div.ci", idTag(id), e.type === "note" ? kindChip(e.kind) : h("span.kind." + ({ hypothesis: "HYPOTHESIS", question: "QUESTION", decision: "DECISION" }[e.type] || "OBSERVATION"), ({ hypothesis: "Hipótesis", question: "Pregunta", decision: "Decisión" }[e.type]) || ""), h("span.x.clamp2", e.title || ""));
          })) : null,
          (t.corrections || []).map(c => h("div.corr", "⚑ Guarda epistémica: " + c)),
          (t.next_steps || []).length ? h("div.small.muted", { style: { marginTop: "10px" } }, "Siguiente: " + t.next_steps.join(" · ")) : null,
          t.language && t.language.introduced_terms && t.language.introduced_terms.length ? h("div.small.faint", { style: { marginTop: "6px" } }, "Términos introducidos: " + t.language.introduced_terms.map(x => `${x.term} (${x.plain})`).join("; ")) : null));
    } else if (t.status === "failed") {
      fr = h("div.turn.turn-f", h("div.who", "Framer"), h("div.bubble", { style: { borderColor: "var(--bad-line)" } }, h("div.small", "No pude responder: " + (t.error || "error")),
        h("div.small.muted", "Tu mensaje quedó guardado; puedes reintentar."), h("div.mt", btn("Reintentar", { sm: true, icon: "refresh", onClick: async () => { await api.cpost(`/framer/${t.turn_id}/retry`); await paint(); } }))));
    } else {
      fr = h("div.turn.turn-f", h("div.who", "Framer"), h("div.bubble", h("div.row", thinking(), h("span.small.muted", t.status === "running" ? "pensando con " + ((t.skills || []).map(s => s.id).join(" · ") || "sus skills") : "en cola"))));
    }
    return h("div.stack", { style: { gap: "12px" } }, hugo, fr);
  };

  const challengeView = c => h("div.panel.tight.alert", { style: { marginTop: "12px" } }, h("div.eyebrow", { style: { color: "var(--bad-ink)" } }, "Challenge · executive mentor"),
    h("div.challenge", [["Supuestos ocultos", h("ul.prose", (c.hidden_assumptions || []).map(x => h("li", x)))], ["Contraargumento más fuerte", c.strongest_counterargument],
      ["Explicación alternativa", c.alternative_explanation], ["Evidencia que lo invalidaría", h("ul.prose", (c.invalidating_evidence || []).map(x => h("li", x)))],
      ["Claim de mayor riesgo", c.highest_risk_claim]].filter(r => r[1] && (typeof r[1] !== "string" || r[1].trim())).map(([k, v]) => h("div.c", h("div.k", k), h("div", v)))));

  const keyLabel = k => {
    if (k === "problem") return "Problema";
    const [kind, id] = k.split(":");
    if (kind === "guion") { const e = (data.shaping.guion || []).find(x => x.key === k); const s = e && (e.approved || (e.pending || {}).value); return `Guion ${id}${s && s.title ? " · " + s.title : ""}`; }
    return `Tarea ${id}`;
  };
  const focusCard = k => { const el = document.getElementById(domId(k)); if (el) { el.scrollIntoView({ behavior: "smooth", block: "center" }); el.classList.add("flash"); setTimeout(() => el.classList.remove("flash"), 1400); } };

  // ------------------------------------------------------------ the Shaping document
  const paintBoard = () => {
    const act = document.activeElement;
    const keep = act && act.dataset && act.dataset.f && board.contains(act) ? { f: act.dataset.f, s: act.selectionStart, e: act.selectionEnd } : null;
    const fr = data.framing;
    put(board,
      docHead(),
      problemCard(),
      questionPanel(fr),
      guionPanel(),
      hypPanel(fr),
      planPanel(),
      h("div.grid2",
        listPanel("6 · Lo que no afirmamos todavía", fr.should_not_claim, "should_not_claim"),
        listPanel("7 · Decisiones necesarias", fr.decisions_needed, "decisions_needed")),
      listPanel("8 · Riesgos", fr.risks, "risks"),
      capturedPanel(fr),
      morePanel(fr));
    // an explicit target (a field just opened or added) wins over the field that had focus before the repaint
    const want = focusNext || (keep && keep.f);
    focusNext = null;
    if (want) {
      const el = board.querySelector(`[data-f="${CSS.escape(want)}"]`);
      if (el) { el.focus(); if (keep && keep.f === want) { try { el.setSelectionRange(keep.s, keep.e); } catch (e) { /* inputs without selection */ } } }
    }
  };

  const docHead = () => {
    const sh = data.shaping, p = sh.progress, rd = data.readiness, mg = sh.migratable || {};
    const step = (ok, label) => h("span.chip." + (ok ? "good" : "ghost"), ok ? icon("check") : null, label);
    const tasks = p.tasks_approved + p.tasks_sent;
    return h("div.panel.pad.shead",
      h("div.row.between.wrap", { style: { alignItems: "flex-start" } },
        h("div", h("div.eyebrow.accent", "Documento de Shaping"),
          h("div.shline", `${p.guion_sections} ${p.guion_sections === 1 ? "sección" : "secciones"} · ${p.slides} ${p.slides === 1 ? "lámina" : "láminas"} · ${tasks} ${tasks === 1 ? "tarea" : "tareas"} de investigación`),
          h("div.row.wrap", { style: { gap: "6px", marginTop: "10px" } },
            step(p.problem, "Problema"), step(!!data.framing.executive_question, "Pregunta ejecutiva"), step(p.guion_sections > 0, "Guion"),
            step((data.framing.hypotheses || []).length > 0, "Hipótesis"), step(tasks > 0, "Plan de investigación"))),
        h("div.row.wrap", { style: { gap: "6px" } },
          btn("Ver documento", { icon: "files", onClick: showDoc }),
          sh.pending ? btn(`Aprobar ${sh.pending === 1 ? "la propuesta" : `las ${sh.pending} propuestas`}`, { variant: "human", human: true, icon: "check", onClick: async () => {
            await api.cpost("/shaping/approve-all"); toast("Propuestas aprobadas", "ok"); await paint(); } }) : null)),
      rd.blockers.length || rd.warnings.length ? h("div.small", { style: { marginTop: "12px", display: "grid", gap: "2px" } },
        rd.blockers.map(b => h("div", { style: { color: "var(--warn-ink)" } }, "· " + b)), rd.warnings.map(w => h("div.muted", "· " + w))) : null,
      mg.guion || mg.plan ? migrateBanner(mg) : null);
  };

  const migrateBanner = mg => h("div.migrate",
    h("div", { style: { minWidth: 0 } }, h("div", { style: { fontWeight: 620 } }, "Trae lo que ya tenías"),
      h("div.small.muted", [mg.guion ? `Tu brief trae la estructura de la historia dentro de Entregables (${mg.guion} ${mg.guion === 1 ? "sección" : "secciones"}); aquí queda como Guion.` : null,
        mg.plan ? `El Framer dejó ${mg.plan} ${mg.plan === 1 ? "pregunta" : "preguntas"} de research necesario; aquí quedan como tareas con su agente.` : null,
        "Llega todo como propuesta: nada cambia hasta que lo apruebes."].filter(Boolean).join(" "))),
    btn("Traer como propuestas", { icon: "arrow", onClick: async () => {
      try {
        const out = await api.cpost("/shaping/migrate");
        toast(`${out.guion.length} sección(es) del guion y ${out.plan.length} tarea(s) propuestas` + (out.deliverables ? " · Entregables limpios propuestos en el Briefing" : ""), "agent", 6500);
        await paint();
      } catch (e) { toast(e.message, "err"); }
    } }));

  const showDoc = () => modal({ eyebrow: "Framing & Shaping · framing/current.md", title: "Documento de Shaping", wide: true,
    body: h("div.paper.docmodal", markdown(data.document || "")),
    actions: [{ label: "Abrir en Artifacts", variant: "ghost", onClick: () => app.go("#/artifacts/framing/current.md") }, { label: "Cerrar", variant: "primary" }] });

  // ------------------------------------------------------------ shared pieces
  const stateChip = st => h(`span.chip.${STATE[st][1]}`, STATE[st][0]);
  const metaLine = m => m && m.state === "approved" && m.by ? h("div.small.faint", `Aprobado por ${m.by === "hugo" ? "ti" : m.by} · ${hhmm(m.at)}` + (m.version > 1 ? ` · v${m.version}` : "")) : null;
  const source = p => p.by === "framer" ? "del Framer" : /brief/i.test(p.basis || "") ? "de tu brief" : /research necesario/i.test(p.basis || "") ? "del research necesario" : "";
  const proposalBox = (key, p, body) => h("div.proposal",
    h("div.row.wrap", h("span.eyebrow.agent", p.revises ? "Cambio propuesto" : "Propuesta"), source(p) ? h("span.chip.ghost", source(p)) : null),
    body,
    p.hugo_wording ? h("div.small", h("span.muted", "Tus palabras: "), h("span.voice", { style: { fontSize: "14.5px" } }, p.hugo_wording)) : null,
    p.why ? h("div.small.muted", p.why) : null,
    h("div.row", { style: { gap: "6px", marginTop: "6px" } },
      btn("Aprobar", { sm: true, variant: "human", human: true, icon: "check", onClick: async () => { await api.cpost(`/shaping/${K(key)}/approve`); await paint(); } }),
      btn("Editar y aprobar", { sm: true, icon: "edit", onClick: () => startEdit(key) }),
      btn("Descartar", { sm: true, variant: "ghost", icon: "x", onClick: async () => { await api.cpost(`/shaping/${K(key)}/discard`); await paint(); } })));
  const startEdit = key => {
    editing = key;
    focusNext = `${key}|${key === "problem" ? "statement" : key.startsWith("plan:") ? "question" : "title"}`;
    paintBoard();
  };
  const draft = (key, init) => (drafts[key] = drafts[key] || init());
  const field = (key, obj, prop, ph, multi, path) => {
    const el = multi ? autosize(h("textarea", { placeholder: ph, rows: 2 })) : h("input", { placeholder: ph });
    el.value = obj[prop] ?? "";
    el.dataset.f = `${key}|${path || prop}`;
    el.addEventListener("input", () => { obj[prop] = el.value; });
    return el;
  };
  const lab = (text, sub) => h("div.flab", text, sub ? h("span.faint", " · " + sub) : null);
  const saveRow = (key, build, what) => h("div.row", { style: { gap: "6px", marginTop: "4px" } },
    btn("Guardar y aprobar", { sm: true, variant: "human", human: true, icon: "check", onClick: async () => {
      try { await api.cput(`/shaping/${K(key)}`, build()); } catch (e) { toast(e.message, "err"); return; }
      editing = null; delete drafts[key]; toast(`${what} aprobado`, "ok"); await paint(); } }),
    btn("Cancelar", { sm: true, variant: "ghost", onClick: () => { editing = null; delete drafts[key]; paintBoard(); } }),
    h("span.small.faint", "Al guardar queda aprobado por ti."));
  const removeItem = async (key, what) => {
    const ok = await confirmDialog({ eyebrow: "Framing & Shaping", title: `Quitar ${what}`, text: "Sale del documento. La versión anterior del framing lo conserva.", confirmLabel: "Quitar", human: true });
    if (!ok) return;
    try { await api.cdel(`/shaping/${K(key)}`); toast("Quitado del documento", "ok"); await paint(); } catch (e) { toast(e.message, "err", 7000); }
  };
  const miniBtn = (label, title, onClick) => h("button.btn.ghost.sm.mini", { type: "button", title, on: { click: onClick } }, label);

  // ------------------------------------------------------------ 1 · problema
  const problemCard = () => {
    const e = data.shaping.problem, key = "problem";
    const st = e.pending ? (e.approved ? "revision" : "proposed") : e.approved ? "approved" : "empty";
    return h(`div.bsec.${st}${editing === key ? ".editing" : ""}`, { id: domId(key) },
      h("div.row.between", h("div.row", h("span.snum", "1"), h("span.bn", "Problema"), stateChip(st)),
        editing === key || st === "proposed" ? null : btn(e.approved ? "Editar" : "Escribir", { sm: true, variant: "ghost", icon: "edit", onClick: () => startEdit(key) })),
      editing === key ? problemEditor(e.pending ? e.pending.value : e.approved || {}) : [
        e.approved ? problemBody(e.approved) : e.pending ? null : h("div.small.faint", "Qué hay que entender o decidir, para quién, y qué queda fuera. Cuéntaselo al Framer o escríbelo tú."),
        e.pending ? proposalBox(key, e.pending, problemBody(e.pending.value)) : null,
        metaLine(e.meta)]);
  };
  const problemBody = p => h("div.stack", { style: { gap: "10px" } },
    p.statement ? h("div.pstate", p.statement) : null,
    p.situation ? h("div.small", h("span.flab.inline", "Situación"), p.situation) : null,
    p.why_it_matters ? h("div.small", h("span.flab.inline", "Por qué importa"), p.why_it_matters) : null,
    (p.in_scope || []).length || (p.out_of_scope || []).length ? h("div.grid2.scope",
      h("div", h("div.flab", "Dentro del alcance"), (p.in_scope || []).length ? h("ul.bl", p.in_scope.map(x => h("li", x))) : h("div.small.faint", "—")),
      h("div", h("div.flab", "Fuera del alcance · no-gos"), (p.out_of_scope || []).length ? h("ul.bl", p.out_of_scope.map(x => h("li", x))) : h("div.small.faint", "—"))) : null);
  const problemEditor = val => {
    const key = "problem";
    const d = draft(key, () => ({ statement: val.statement || "", situation: val.situation || "", why_it_matters: val.why_it_matters || "",
      in_scope: (val.in_scope || []).join("\n"), out_of_scope: (val.out_of_scope || []).join("\n") }));
    return h("div.editor.shaped",
      lab("Planteamiento"), field(key, d, "statement", "Una o dos frases: qué hay que entender o decidir, y para quién.", true),
      lab("Situación"), field(key, d, "situation", "Qué está pasando hoy, en tus palabras.", true),
      lab("Por qué importa"), field(key, d, "why_it_matters", "Qué se juega el negocio si no se resuelve.", true),
      h("div.grid2", h("div", lab("Dentro del alcance", "uno por línea"), field(key, d, "in_scope", "Lo que sí vamos a responder", true)),
        h("div", lab("Fuera del alcance", "uno por línea"), field(key, d, "out_of_scope", "No-gos y hoyos de conejo", true))),
      saveRow(key, () => ({ statement: d.statement.trim(), situation: d.situation.trim(), why_it_matters: d.why_it_matters.trim(),
        in_scope: lines(d.in_scope), out_of_scope: lines(d.out_of_scope) }), "Problema"));
  };

  // ------------------------------------------------------------ 2 · pregunta ejecutiva
  const questionPanel = fr => {
    const eq = h("div.eq", { contentEditable: "true", spellcheck: "false", on: { blur: async e => {
      const v = e.target.textContent.trim();
      if (v && v !== fr.executive_question) { await api.cpatch("/framing", { executive_question: v }); toast("Pregunta ejecutiva actualizada (versionada)", "ok"); await paint(); }
    } } }, fr.executive_question || "¿Qué están tratando de decidir o entender los ejecutivos?");
    return h("div.panel.pad.glow", h("div.row.between", h("div.row", h("span.snum", "2"), h("span.eyebrow.accent", "Pregunta ejecutiva")), h("span.small.faint", "editable · se versiona")),
      h("div", { style: { marginTop: "10px" } }, eq),
      fr.executive_question_note ? h("div.small.faint", { style: { marginTop: "8px" } }, fr.executive_question_note) : null);
  };

  // ------------------------------------------------------------ 3 · guion de la historia
  const guionPanel = () => {
    const secs = data.shaping.guion, legacy = data.shaping.legacy_storyline || [];
    return h("div.stack",
      h("div.row.between.wrap", h("h2.sec.row", h("span.snum", "3"), "Guion de la historia", h("span.count", String(secs.length))),
        editing === "guion:new" ? null : btn("Añadir sección", { sm: true, variant: "ghost", icon: "plus", onClick: () => startEdit("guion:new") })),
      h("div.small.muted", "Tu historia, sección por sección. Cada lámina dice qué pregunta responde y qué debe mostrar. El Chief of Staff arma el Story Package siguiendo este guion; si una lámina no tiene evidencia, la marca y la vuelve pregunta de research en vez de rellenarla."),
      secs.length || editing === "guion:new" ? null : h("div.bsec.empty", h("div.small.faint", "Sin guion todavía. Cuéntale al Framer cómo quieres contar la historia (secciones y láminas) o escríbela tú."),
        legacy.length ? h("div", h("div.flab", "Borrador anterior del Framer (no aprobado)"), h("div.storyline", legacy.map(s => h("div", h("span", s))))) : null),
      secs.map(guionCard),
      editing === "guion:new" ? h("div.bsec.editing", { id: domId("guion:new") }, h("div.row", h("span.bn", "Nueva sección")), sectionEditor("guion:new", { title: "", purpose: "", slides: [{}] })) : null);
  };
  const guionCard = e => {
    const sec = e.approved || e.pending.value;
    const st = e.pending ? (e.approved ? "revision" : "proposed") : "approved";
    return h(`div.bsec.${st}${editing === e.key ? ".editing" : ""}`, { id: domId(e.key) },
      h("div.row.between.wrap", h("div.row", h("span.sid", sec.id), h("span.bn", sec.title || "Sin título"), stateChip(st),
        h("span.small.faint", `${(sec.slides || []).length} ${(sec.slides || []).length === 1 ? "lámina" : "láminas"}`)),
        editing === e.key || !e.approved ? null : h("div.row", { style: { gap: "4px" } },
          btn("Editar", { sm: true, variant: "ghost", icon: "edit", onClick: () => startEdit(e.key) }),
          btn("Quitar", { sm: true, variant: "ghost", icon: "x", onClick: () => removeItem(e.key, `la sección ${sec.id} · ${sec.title}`) }))),
      editing === e.key ? sectionEditor(e.key, e.pending ? e.pending.value : e.approved) : [
        e.approved ? sectionBody(e.approved) : null,
        e.pending ? proposalBox(e.key, e.pending, sectionBody(e.pending.value)) : null,
        metaLine(e.meta)]);
  };
  const slideTasks = id => {
    const ts = (data.shaping.slide_tasks || {})[id] || [];
    return h("div.slt", ts.length ? ts.map(t => h(`button.chip.${t.status === "proposed" ? "agent" : t.status === "sent" ? "accent" : "good"}`,
      { type: "button", title: t.status === "proposed" ? "tarea propuesta" : t.status === "sent" ? "en Research" : "tarea aprobada",
        style: { cursor: "pointer" }, on: { click: () => focusCard("plan:" + t.id) } }, "→ " + t.id)) : h("span.chip.ghost", "sin tarea"));
  };
  const sectionBody = s => h("div.stack", { style: { gap: "8px" } },
    s.purpose ? h("div.small.muted", { style: { whiteSpace: "pre-line" } }, s.purpose) : null,
    (s.slides || []).length ? h("div.slides", s.slides.map(sl => h("div.slide.withtask",
      h("span.slid", sl.id),
      h("div", { style: { minWidth: 0 } },
        h("div.st", sl.title || "—"),
        sl.question ? h("div.sq", sl.question) : null,
        sl.intent && sl.intent !== sl.title ? h("div.si", h("span.flab.inline", "Debe mostrar"), sl.intent) : null,
        sl.notes ? h("div.sn", sl.notes) : null,
        (sl.links || []).length ? h("div.row.wrap", { style: { gap: "4px", marginTop: "4px" } }, sl.links.map(i => idTag(i))) : null),
      slideTasks(sl.id)))) : h("div.small.faint", "Sin láminas."));
  const sectionEditor = (key, val) => {
    const d = draft(key, () => ({ title: val.title || "", purpose: val.purpose || "",
      slides: (val.slides || []).map(s => ({ prev_id: s.id || "", title: s.title || "", question: s.question || "", intent: s.intent || "",
        notes: s.notes || "", links: (s.links || []).join(", ") })) }));
    const sid = key === "guion:new" ? "S·" : key.split(":")[1];
    // fields are addressed by position, so a move or a removal must not hand the caret to whichever slide lands there
    const settle = () => { if (document.activeElement && board.contains(document.activeElement)) document.activeElement.blur(); paintBoard(); };
    const move = (i, j) => { d.slides.splice(j, 0, d.slides.splice(i, 1)[0]); settle(); };
    const slideRow = (s, i) => h("div.eslide",
      h("div.row.between", h("span.slid", `${sid}.${i + 1}`), h("div.row", { style: { gap: "2px" } },
        i > 0 ? miniBtn("↑", "Subir", () => move(i, i - 1)) : null,
        i < d.slides.length - 1 ? miniBtn("↓", "Bajar", () => move(i, i + 1)) : null,
        miniBtn("×", "Quitar lámina", () => { d.slides.splice(i, 1); settle(); }))),
      field(key, s, "title", "Título de la lámina", false, `slides.${i}.title`),
      field(key, s, "question", "¿Qué pregunta responde?", false, `slides.${i}.question`),
      field(key, s, "intent", "Qué debe mostrar: el dato, la comparación, el mensaje", true, `slides.${i}.intent`),
      h("div.grid2", field(key, s, "notes", "Notas tuyas (opcional)", true, `slides.${i}.notes`),
        field(key, s, "links", "Enlaza H/Q (opcional): H-003, Q-002", false, `slides.${i}.links`)));
    return h("div.editor.shaped",
      lab("Título de la sección"), field(key, d, "title", "Overview, Growth, Revenue…", false),
      lab("Para qué está", "qué se lleva el CFO de esta parte"), field(key, d, "purpose", "Opcional", true),
      lab("Láminas", "en el orden en que se cuentan"),
      d.slides.map(slideRow),
      h("div", btn("Añadir lámina", { sm: true, variant: "ghost", icon: "plus", onClick: () => {
        d.slides.push({ title: "", question: "", intent: "", notes: "", links: "" }); focusNext = `${key}|slides.${d.slides.length - 1}.title`; paintBoard(); } })),
      saveRow(key, () => ({ title: d.title.trim(), purpose: d.purpose.trim(), slides: d.slides.map(s => ({ ...s, links: csv(s.links) })) }), "Guion"));
  };

  // ------------------------------------------------------------ 4 · hipótesis
  const hypPanel = fr => {
    const hs = fr.hypotheses || [];
    return h("div.panel.pad", h("div.row.between.wrap", h("h2.sec.row", h("span.snum", "4"), "Hipótesis", h("span.count", String(hs.length))),
      h("span.small.faint", "las captura el Framer · se prueban en Research")),
      hs.length ? h("div.ledger", { style: { marginTop: "8px" } }, hs.map(r => h("div.lrow", { on: { click: () => app.openEntity(r.id) } },
        h("span", idTag(r.id, { alias: r.alias })),
        h("div", h("div.x", r.text), r.falsifier ? h("div.f", "Se debilita si: " + r.falsifier) : null,
          r.hugo_wording ? h("div.f.serif", { style: { fontStyle: "italic" } }, "“" + r.hugo_wording + "”") : null),
        h("div.row", r.status && r.status !== "open" ? statusChip(r.status) : null, review(r.review, r.stale))))) : empty("Sin hipótesis todavía", "Cuéntale al Framer qué crees que está pasando."));
  };

  // ------------------------------------------------------------ 5 · plan de investigación
  const planPanel = () => {
    const tasks = data.shaping.plan;
    const ready = tasks.filter(t => t.approved && t.approved.status === "approved");
    const run = data.shaping.plan_run;
    const busy = run && ["pending", "running"].includes(run.status);
    const hasGuion = (data.shaping.guion || []).length > 0;
    return h("div.stack",
      h("div.row.between.wrap", h("h2.sec.row", h("span.snum", "5"), "Plan de investigación", h("span.count", String(tasks.length))),
        h("div.row", { style: { gap: "6px" } },
          busy ? null : btn(tasks.length ? "Rehacer el plan desde el guion" : "Armar el plan desde el guion", { sm: true, variant: tasks.length ? "ghost" : "primary",
            icon: "spark", disabled: !hasGuion, title: hasGuion ? "" : "Primero hace falta un guion", onClick: startPlan }),
          ready.length > 1 ? btn(`Lanzar las ${ready.length} aprobadas`, { sm: true, variant: "primary", icon: "send", onClick: sendAll }) : null,
          editing === "plan:new" ? null : btn("Añadir tarea", { sm: true, variant: "ghost", icon: "plus", onClick: () => startEdit("plan:new") }))),
      h("div.small.muted", "Cada pregunta de tu guion se vuelve una tarea: qué sale (una propuesta, datos o research externo), una respuesta de arranque escrita con el contexto del caso y lo que ya dijiste, y los pasos, incluido qué investigar en el modelo de datos. Las aprobadas aparecen en Research listas para lanzar; lanzarlas es tu clic."),
      planRun(run),
      tasks.length || editing === "plan:new" ? null : h("div.bsec.empty", h("div.small.faint", hasGuion ? "Sin tareas todavía. «Armar el plan desde el guion» convierte cada pregunta de tus láminas en una tarea." : "Sin tareas todavía. Cuando tengas guion, el Framer arma el plan desde sus preguntas; también puedes escribir una tarea.")),
      tasks.map(taskCard),
      editing === "plan:new" ? h("div.bsec.editing", { id: domId("plan:new") }, h("div.row", h("span.bn", "Nueva tarea")),
        taskEditor("plan:new", { question: "", work: "propuesta", kind: "measurement", intensity: "L2", why: "", links: [], slides: [], steps: [] })) : null);
  };
  const planRun = run => {
    if (!run) return null;
    if (["pending", "running"].includes(run.status)) return h("div.planrun.busy", h("div.row", thinking(),
      h("span", { style: { fontWeight: 560 } }, "El Framer está armando el plan desde tu guion"),
      h("span.small.muted", run.status === "running" ? "lee el caso, lo que dijiste y el modelo de datos · unos minutos" : "en cola")));
    if (run.status === "failed") return h("div.planrun.failed", h("div.small", "No se pudo armar el plan: " + (run.error || "error")),
      h("div.small.muted", "Nada cambió en el documento. Puedes volver a pedirlo."));
    const np = run.not_planned || [];
    return h("details.planrun", { open: opened.has("planrun"), on: { toggle: e => { e.target.open ? opened.add("planrun") : opened.delete("planrun"); save("caseos.shaping.open", [...opened]); } } },
      h("summary", h("span.small", h("b", `Plan del ${hhmm(run.finished_at)}`), ` · ${(run.proposed || []).length} tareas propuestas`
        + ((run.superseded || []).length ? ` · reemplazó ${run.superseded.length} propuesta(s) sin aprobar` : "")
        + ((run.corrections || []).length ? ` · ${run.corrections.length} corrección(es) de las guardas` : ""))),
      run.summary ? h("div.small", { style: { marginTop: "8px" } }, run.summary) : null,
      np.length ? h("div.small.muted", { style: { marginTop: "6px" } }, "Sin tarea a propósito: ", np.map(x => `${(x.slides || []).join(", ")} (${x.why})`).join(" · ")) : null,
      (run.corrections || []).map(c => h("div.corr", "⚑ " + c)));
  };
  const startPlan = async () => {
    const tasks = data.shaping.plan || [];
    const pend = tasks.filter(t => t.pending);
    if (pend.length) {
      const changes = pend.filter(t => t.approved).length;
      const ok = await confirmDialog({ eyebrow: "Framing & Shaping", title: "Rehacer el plan desde el guion",
        text: `Las ${pend.length} propuesta(s) del plan que no has aprobado${changes ? ` (${pend.length - changes} tareas nuevas y ${changes} cambios a tareas aprobadas)` : ""} se reemplazan por el plan nuevo; la versión anterior del framing las conserva. Lo que ya aprobaste no se toca: si el Framer quiere mejorar una tarea aprobada, te lo propone como cambio.`,
        confirmLabel: "Armar el plan" });
      if (!ok) return;
    }
    try { await api.cpost("/shaping/plan"); toast("El Framer está armando el plan desde tu guion", "agent"); await paint(); }
    catch (e) { toast(e.message, "err", 7000); }
  };
  const kindTag = k => { const m = data.shaping.kinds[k] || {}; return h(`span.chip.kind-${k}`, icon(KIND_ICON[k] || "globe"), m.label || k); };
  const workTag = w => h(`span.chip.work-${w}`, icon(WORK_ICON[w] || "spark"), ((data.shaping.work || {})[w] || {}).label || w);
  const tableChip = t => h("button.tbl-chip", { type: "button", title: "Ver la tabla en Datos",
    on: { click: () => app.go(`#/data/${(data.data_model || {}).id || "finora"}/${t}`) } }, t);
  const taskBody = t => {
    const m = data.shaping.kinds[t.kind] || {};
    const stepName = k => (data.shaping.step_kinds || {})[k] || k;
    return h("div.stack", { style: { gap: "8px" } },
      h("div.row.wrap", { style: { gap: "6px" } }, workTag(t.work || "propuesta"), h("span.small.muted", "lidera"), kindTag(t.kind),
        h("span.small.muted", m.agent || t.agent), t.intensity && t.intensity !== "analytics" ? h("span.chip.accent", t.intensity) : null,
        (t.slides || []).map(s => h("button.chip.ghost", { type: "button", title: "Ir a la lámina en el guion", style: { cursor: "pointer" },
          on: { click: () => focusCard("guion:" + s.split(".")[0]) } }, s))),
      h("div.tq", t.question),
      t.draft_answer ? h("div.draft", h("div.flab", "Respuesta de arranque", h("span.faint", " · propuesta del agente, a validar")), h("div.dt", t.draft_answer)) : null,
      (t.hugo_said || []).length ? h("div.said", h("div.flab", "Lo que ya dijiste"),
        t.hugo_said.map(x => h("div.sq2", h("span.voice", "“" + x.text + "”"), x.ref ? idTag(x.ref) : null))) : null,
      (t.steps || []).length ? h("div", h("div.flab", "Cómo se trabaja"), h("ol.stepl", t.steps.map(st => h("li",
        h(`span.sk.${st.kind}`, icon(STEP_ICON[st.kind] || "spark"), stepName(st.kind)), h("span.sw", st.what),
        (st.where || []).length ? h("span.where", st.where.map(tableChip)) : null)))) : null,
      t.why ? h("div.small.muted", h("span.flab.inline", "Por qué importa"), t.why) : null,
      (t.links || []).length ? h("div.row.wrap", { style: { gap: "4px" } }, h("span.small.faint", "Sirve a:"), t.links.map(i => idTag(i))) : null,
      (t.flags || []).map(f => h("div.corr", "⚑ " + f)));
  };
  const taskCard = e => {
    const t = e.approved || e.pending.value;
    const sent = e.approved && e.approved.status === "sent";
    const st = e.pending ? (e.approved ? "revision" : "proposed") : sent ? "sent" : "approved";
    const rid = sent ? e.approved.research_id : null;
    const r = rid ? app.byId[rid] : null;
    return h(`div.bsec.task.${st}${editing === e.key ? ".editing" : ""}`, { id: domId(e.key) },
      h("div.row.between.wrap", h("div.row", h("span.sid", t.id), stateChip(st)),
        editing === e.key ? null : sent ? h("div.row", { style: { gap: "6px" } }, r ? statusChip(r.status) : null,
          btn(`Ver ${rid}`, { sm: true, variant: "ghost", icon: "arrow", onClick: () => app.go("#/research/" + rid) }))
          : e.approved ? h("div.row", { style: { gap: "4px" } },
            btn("Lanzar", { sm: true, variant: "primary", icon: "send", onClick: () => sendTask(t.id) }),
            btn("Editar", { sm: true, variant: "ghost", icon: "edit", onClick: () => startEdit(e.key) }),
            btn("Quitar", { sm: true, variant: "ghost", icon: "x", onClick: () => removeItem(e.key, `la tarea ${t.id}`) })) : null),
      editing === e.key ? taskEditor(e.key, e.pending ? e.pending.value : e.approved) : [
        e.approved ? taskBody(e.approved) : null,
        e.pending ? proposalBox(e.key, e.pending, taskBody(e.pending.value)) : null,
        metaLine(e.meta)]);
  };
  const taskEditor = (key, val) => {
    const d = draft(key, () => ({ question: val.question || "", kind: val.kind || "research", work: val.work || "propuesta",
      intensity: val.intensity && val.intensity !== "analytics" ? val.intensity : "L2", why: val.why || "", draft_answer: val.draft_answer || "",
      steps: (val.steps || []).map(st => ({ kind: st.kind, what: st.what, where: (st.where || []).join(", ") })),
      hugo_said: val.hugo_said || [], links: (val.links || []).join(", "), slides: (val.slides || []).join(", ") }));
    const kinds = data.shaping.kinds;
    const dm = data.data_model;
    const settle = () => { if (document.activeElement && board.contains(document.activeElement)) document.activeElement.blur(); paintBoard(); };
    const stepRow = (st, i) => h("div.eslide",
      h("div.row.between", h("div.row.wrap", { style: { gap: "4px" } }, h("span.slid", `${i + 1}`),
        Object.entries(data.shaping.step_kinds || {}).map(([k, l]) => h("button.btn.sm" + (st.kind === k ? ".primary" : ".ghost"),
          { type: "button", on: { click: () => { st.kind = k; paintBoard(); } } }, icon(STEP_ICON[k]), l))),
        miniBtn("×", "Quitar paso", () => { d.steps.splice(i, 1); settle(); })),
      field(key, st, "what", st.kind === "data" ? "Qué buscar en el modelo (si no existe, dilo y nombra el proxy)" : st.kind === "research" ? "Qué buscar afuera y por qué" : "Qué se entrega", true, `steps.${i}.what`),
      st.kind === "data" ? field(key, st, "where", "Tablas: mart.new_customers, mart.customer_month", false, `steps.${i}.where`) : null);
    return h("div.editor.shaped",
      lab("Pregunta que hay que resolver"), field(key, d, "question", "¿Qué necesitamos saber para contar la historia con evidencia?", true),
      lab("Qué sale"),
      h("div.row.wrap", { style: { gap: "6px" } }, Object.entries(data.shaping.work || {}).map(([k, w]) =>
        h("button.btn.sm" + (d.work === k ? ".primary" : ".ghost"), { type: "button", title: w.hint, on: { click: () => { d.work = k; paintBoard(); } } }, icon(WORK_ICON[k]), w.label))),
      lab("Respuesta de arranque", "lo que respondemos hoy con el contexto; se valida al investigar"),
      field(key, d, "draft_answer", "Ej.: todo depende del punto de entrada: hay que segmentar por puerta y medir cada una en su orden…", true),
      lab("Cómo se trabaja", "pasos en orden"),
      d.steps.map(stepRow),
      h("div", btn("Añadir paso", { sm: true, variant: "ghost", icon: "plus", onClick: () => {
        d.steps.push({ kind: "data", what: "", where: "" }); focusNext = `${key}|steps.${d.steps.length - 1}.what`; paintBoard(); } })),
      lab("Quién la lidera"),
      h("div.row.wrap", { style: { gap: "6px" } }, Object.entries(kinds).map(([k, m]) =>
        h("button.btn.sm" + (d.kind === k ? ".primary" : ".ghost"), { type: "button", on: { click: () => { d.kind = k; paintBoard(); } } }, icon(KIND_ICON[k]), `${m.label} · ${m.agent}`))),
      d.kind === "data" ? h("div.small.muted", dm ? `Analytics la resuelve consultando el modelo de datos del caso: ${dm.label}.` : "Analytics necesita un modelo de datos: elígelo en Briefing.")
        : h("div.row.wrap", { style: { gap: "6px" } }, h("span.small.muted", "Intensidad:"),
          [["L1", "L1 · consulta rápida"], ["L2", "L2 · research de negocio"], ["L3", "L3 · deep research"]].map(([l, t]) =>
            h("button.btn.sm" + (d.intensity === l ? ".primary" : ".ghost"), { type: "button", on: { click: () => { d.intensity = l; paintBoard(); } } }, t))),
      lab("Por qué importa", "opcional"), field(key, d, "why", "Qué cambia en la historia según lo que salga", true),
      h("div.grid2", h("div", lab("Sirve a", "H / Q / D, opcional"), field(key, d, "links", "H-003, Q-002", false)),
        h("div", lab("Láminas del guion", "opcional"), field(key, d, "slides", "S2.3, S3.1", false))),
      saveRow(key, () => ({ question: d.question.trim(), work: d.work, kind: d.kind, intensity: d.intensity, why: d.why.trim(),
        draft_answer: d.draft_answer.trim(), hugo_said: d.hugo_said,
        steps: d.steps.filter(st => st.what.trim()).map(st => ({ kind: st.kind, what: st.what.trim(), where: csv(st.where) })),
        links: csv(d.links), slides: csv(d.slides) }), "Tarea"));
  };
  const sendTask = async id => {
    try {
      const out = await api.cpost(`/shaping/tasks/${K(id)}/send`);
      toast(`${id} → ${out.research_id} ${out.launched ? "en cola" : "creada"}`, "agent");
      await app.refresh(); await paint();
    } catch (e) { toast(e.message, "err", 7000); }
  };
  const sendAll = async () => {
    try {
      const out = await api.cpost("/shaping/tasks/send-all");
      toast(`${out.sent.length} tarea(s) lanzadas a Research`, "agent");
      await app.refresh(); await paint();
    } catch (e) { toast(e.message, "err", 7000); }
  };

  // ------------------------------------------------------------ 6–8 · límites, y el resto de lo capturado
  const listPanel = (title, items, key) => h("div.panel.pad", h("h3.sub", title), (items || []).length ? h("ul.prose", { style: { margin: 0 } }, items.map((x, i) => h("li", x,
    h("button.btn.ghost.sm", { type: "button", title: "Quitar", style: { marginLeft: "6px", height: "20px", padding: "0 6px" }, on: { click: async () => { await api.cpatch("/framing", { remove: { list: key, index: i } }); await paint(); } } }, "×")))) : h("div.small.muted", "—"));

  const fold = (id, title, ...kids) => h("details.panel.pad.fold", { open: opened.has(id), on: { toggle: e => {
    e.target.open ? opened.add(id) : opened.delete(id); save("caseos.shaping.open", [...opened]); } } },
    h("summary", h("span.sub", { style: { fontWeight: 600 } }, title)), h("div.stack", { style: { marginTop: "12px" } }, kids));

  const capturedPanel = fr => {
    const led = fr.ledger || {};
    const rows = tab === "QUESTION" ? fr.open_questions : (led[tab] || []);
    const counts = Object.fromEntries(LEDGER.map(([k]) => [k, k === "QUESTION" ? fr.open_questions.length : (led[k] || []).length]));
    const total = Object.values(counts).reduce((a, b) => a + b, 0);
    return fold("captured", `Todo lo capturado en la conversación · ${total}`,
      fr.dual && fr.dual.length ? h("div.panel.flush", h("div.phead", h("h2.sec", "Lo que Hugo piensa ↔ interpretación estructurada", h("span.count", String(fr.dual.length)))),
        h("div", fr.dual.slice(0, 7).map(d => h("div.dualrow", { on: { click: () => app.openEntity(d.id) } },
          h("div", { style: { padding: "12px 16px", background: "var(--human-soft)", borderRight: "1px solid var(--line)" } }, h("div.row", { style: { marginBottom: "6px" } }, idTag(d.id), d.verbatim === false ? h("span.faint.small", "paráfrasis") : null), h("div.voice", { style: { fontSize: "15px" } }, d.hugo_wording)),
          h("div", { style: { padding: "12px 16px" } }, h("div.small", { style: { color: "var(--ink)" } }, d.structured)))))) : null,
      h("div", tabs(LEDGER.map(([k, l]) => ({ id: k, label: l, count: counts[k] })), tab, k => { tab = k; paintBoard(); }),
        rows.length ? h("div.ledger", rows.map(r => h("div.lrow", { on: { click: () => app.openEntity(r.id) } },
          r.type === "note" ? kindChip(r.kind) : h("span", idTag(r.id, { alias: r.alias })),
          h("div", h("div.x", r.text), r.falsifier ? h("div.f", "Se debilita si: " + r.falsifier) : null, r.hugo_wording && r.type !== "note" ? h("div.f.serif", { style: { fontStyle: "italic" } }, "“" + r.hugo_wording + "”") : null),
          h("div.row", r.type === "note" ? idTag(r.id) : null, r.status && r.type !== "note" && r.status !== "open" && r.status !== "active" ? statusChip(r.status) : null, review(r.review, r.stale))))) : empty(`Sin ${LEDGER.find(x => x[0] === tab)[1].toLowerCase()}`, "Aparecen aquí cuando el Framer los captura.")));
  };

  const morePanel = fr => fold("more", "Más · frames candidatos, stress test y lenguaje",
    h("div.grid2",
      h("div", h("h3.sub", "Frames candidatos"), (fr.candidate_frames || []).length ? h("div.stack", fr.candidate_frames.map(f =>
        h("div.frame" + (f.chosen ? ".chosen" : ""), h("div.row.between", h("span.n", f.name), btn(f.chosen ? "Elegido" : "Elegir", { sm: true, variant: f.chosen ? "human" : "ghost", human: f.chosen,
          onClick: async () => { await api.cpatch("/framing", { choose_frame: f.name }); await paint(); } })), h("div.small.muted", f.description), f.when_it_wins ? h("div.small.faint", f.when_it_wins) : null))) : empty("Sin frames todavía", "Pide Advise al Framer.")),
      h("div", h("h3.sub", "Perfil de lenguaje observado"), languageView(data.language),
        (fr.language_notes || []).length ? h("div", { style: { marginTop: "12px" } }, h("h3.sub", "Notas de lenguaje"), h("ul.prose", { style: { margin: 0 } }, fr.language_notes.map(x => h("li", x)))) : null)),
    (fr.stress_test || []).length ? h("div", h("h3.sub", `Stress test del framing · ${fr.stress_test.length} puntos`),
      h("div.stack", fr.stress_test.map(p => h("div", h("div", { style: { fontWeight: 560 } }, `${p.n}. ${p.point}`), h("div.small.muted", p.risk), h("div.small", "→ " + p.resolution))))) : null);

  put(root, head, h("div.split",
    h("div.convo", h("div.row.between.mb", modeBox, h("span.small.faint", "⌘↵ para enviar")), hint, stream,
      h("div.composer", ta, h("div.bar2", h("span.small.faint", "Separa hecho · intuición · hipótesis · pregunta, y propone piezas del documento"), h("span.spacer"),
        btn("Enviar", { variant: "primary", icon: "send", onClick: send })))),
    h("div", { style: { minWidth: 0 } }, board)));
  hint.style.margin = "0 0 10px";
  await paint();
  const onJob = ev => { if ((ev.job.kind === "framer_turn" || ev.job.kind === "shaping_plan" || ev.job.agent === "framer") && ["running", "skills", "succeeded", "failed"].includes(ev.event.kind)) paint(); };
  app.on("job", onJob);
  return { update: paint, destroy: () => { app.listeners.job = (app.listeners.job || []).filter(f => f !== onJob); } };
}

function load(k, dflt) { try { return JSON.parse(sessionStorage.getItem(k)) || dflt; } catch (e) { return dflt; } }
function save(k, v) { try { sessionStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* private mode */ } }

function languageView(lang) {
  const o = (lang || {}).observed || {};
  return h("div.stack", { style: { gap: "8px" } },
    h("div.small", h("span.muted", "Registro: "), o.register || "—"), h("div.small", h("span.muted", "Nivel técnico: "), o.technical_level || "—"),
    h("div.small", h("span.muted", "Formalidad: "), o.formality || "—"),
    (o.preserved_terms || []).length ? h("div.row.wrap", { style: { gap: "6px" } }, o.preserved_terms.slice(-18).map(t => h("span.chip.human", t))) : null,
    h("div.small.faint", `primary: ${lang.primary} · preserve_user_vocabulary: ${lang.preserve_user_vocabulary} · avoid_unnecessary_jargon: ${lang.avoid_unnecessary_jargon}`));
}
