// Briefing — Hugo talks to the Briefer as freely as in Framing; the brief is built section by section and he approves
// each piece (or edits it, or discards the proposal). The data model of the case is chosen here, for real.
import { h, mount as put, autosize } from "../core/dom.js";
import { api } from "../core/api.js";
import { icon } from "../core/icons.js";
import { app } from "../app.js";
import { btn, empty, statusChip, toast, thinking, hhmm } from "../ui/components.js";

const BASIS = { hugo: ["dicho por ti", "human"], enunciado: ["del enunciado", "accent"], inferido: ["inferido por el agente", "warn"],
  "alta del caso": ["al crear el caso", "ghost"], "modelo de datos elegido por Hugo": ["del modelo de datos", "accent"] };

export async function mount(root) {
  let data = null;
  let editing = null;                                  // section key being edited inline
  const drafts = {};                                   // what Hugo is typing survives live repaints
  let focusNext = false;
  const head = h("div");
  const stream = h("div.stream");
  const right = h("div.stack.lg");
  const ta = autosize(h("textarea", { placeholder: "Cuéntame el caso como lo tengas en la cabeza, o pega el enunciado tal cual. «Quiero probar esto peloncito: el CFO tiene que entender…»" }));
  const send = async () => {
    const msg = ta.value.trim();
    if (!msg) return;
    ta.value = "";
    ta.dispatchEvent(new Event("input"));
    try { await api.cpost("/briefer", { message: msg }); await paint(); } catch (e) { toast(e.message, "err"); ta.value = msg; }
  };
  ta.addEventListener("keydown", e => { if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) send(); });

  const paint = async () => {
    data = await api.cget("/brief");
    const ph = data.phase, v = data.view, rd = data.readiness;
    app.crumbs(["Briefing"]);
    put(head, h("div.head",
      h("div", h("div.eyebrow", "01 · Briefing · el contrato del caso"), h("h1.title", (data.brief.title || "Brief")),
        h("p.lede", "Cuéntalo como lo piensas; el Briefer lo convierte en secciones y tú vas aprobando cada una. Lo aprobado es lo que leen todos los demás agentes.")),
      h("div.actions", statusChip(ph.status), ph.ready_count ? h("span.small.muted", `v${ph.ready_count} aprobada`) : null,
        ph.ready_count ? btn("Reabrir", { icon: "undo", variant: "ghost", onClick: () => app.reopenPhase("briefing") }) : null,
        btn(ph.status === "ready" ? "Brief aprobado" : "Mark Briefing Ready", { variant: "human", human: true, disabled: ph.status === "ready" || !rd.ok,
          title: rd.ok ? "" : rd.blockers.join(" · "), onClick: () => app.markReady("briefing") }))));
    paintStream();
    paintRight();
  };

  // ------------------------------------------------------------ conversation
  const paintStream = () => {
    const conv = data.conversation || [];
    put(stream, conv.length ? conv.map(turnView) : h("div.empty", h("b", "Empieza por donde quieras"),
      "Un objetivo a medias, a quién le vas a hablar, el enunciado pegado tal cual o tu reencuadre. El Briefer propone secciones; nada entra sin tu aprobación."));
    requestAnimationFrame(() => { stream.scrollTop = stream.scrollHeight; });
  };
  const turnView = t => {
    const hugo = h("div.turn.turn-h", h("div.who.hugo", `Hugo · ${hhmm(t.ts)}`), h("div.bubble", h("div.voice", { style: { fontSize: "15.5px", whiteSpace: "pre-wrap" } },
      t.message.length > 1400 ? t.message.slice(0, 1400) + "…" : t.message)));
    let b;
    if (t.status === "done") {
      b = h("div.turn.turn-f", h("div.who", "Briefer", h("span.faint", hhmm(t.finished_at)), t.skills ? h("span.faint", `${t.skills.length} skills`) : null),
        h("div.bubble", h("div.reply", t.reply),
          t.question ? h("div.bq", icon("spark"), h("span", t.question)) : null,
          (t.proposed || []).length ? h("div.captured", h("div.eyebrow", `Propuso · ${t.proposed.length}`), h("div.row.wrap", { style: { gap: "6px" } },
            t.proposed.map(k => h("button.chip.agent", { type: "button", style: { cursor: "pointer" }, on: { click: () => focusSection(k) } }, labelOf(k))))) : null,
          (t.corrections || []).map(c => h("div.corr", "⚑ " + c))));
    } else if (t.status === "failed") {
      b = h("div.turn.turn-f", h("div.who", "Briefer"), h("div.bubble", { style: { borderColor: "var(--bad-line)" } }, h("div.small", "No pude responder: " + (t.error || "error")),
        h("div.small.muted", "Tu mensaje quedó guardado; puedes reintentar."),
        h("div.mt", btn("Reintentar", { sm: true, icon: "refresh", onClick: async () => { await api.cpost(`/briefer/${t.turn_id}/retry`); await paint(); } }))));
    } else {
      b = h("div.turn.turn-f", h("div.who", "Briefer"), h("div.bubble", h("div.row", thinking(),
        h("span.small.muted", t.status === "running" ? "armando el brief con " + ((t.skills || []).map(s => s.id).join(" · ") || "sus skills") : "en cola"))));
    }
    return h("div.stack", { style: { gap: "12px" } }, hugo, b);
  };
  const labelOf = k => ((data.view.sections || []).find(s => s.key === k) || {}).label || k;
  const focusSection = k => { const el = document.getElementById("sec-" + k); if (el) { el.scrollIntoView({ behavior: "smooth", block: "center" }); el.classList.add("flash"); setTimeout(() => el.classList.remove("flash"), 1400); } };

  // ------------------------------------------------------------ brief sections
  const paintRight = () => {
    const v = data.view, p = v.progress, rd = data.readiness;
    const pend = v.sections.filter(s => s.pending);
    put(right,
      h("div.panel.pad", h("div.row.between.wrap",
        h("div", h("div.eyebrow", "Avance del brief"), h("div", { style: { fontSize: "22px", fontWeight: 620, marginTop: "4px" } }, `${p.approved} de ${p.total} secciones aprobadas`),
          h("div.small", { style: { marginTop: "2px", color: p.required_ok ? "var(--good-ink)" : "var(--warn-ink)" } },
            p.required_ok ? "Objetivo, audiencia y entregables aprobados: ya puedes marcar Ready." : "Para Mark Ready falta aprobar: " + p.required_missing.join(", ").toLowerCase() + ".")),
        pend.length ? btn(`Aprobar las ${pend.length} propuestas`, { variant: "human", human: true, icon: "check", onClick: async () => {
          await api.cpost("/brief/approve-all"); toast("Propuestas aprobadas", "ok"); await paint(); } }) : null),
        h("div.bar", h("i", { style: { width: `${Math.round(100 * p.approved / p.total)}%` } })),
        rd.warnings.length ? h("div.small.muted", { style: { marginTop: "10px" } }, rd.warnings.map(w => h("div", "· " + w))) : null),
      dataModelCard(),
      h("div.stack", v.sections.map(sectionCard)));
  };

  const valueView = (s, val) => {
    if (s.kind === "list") return (val || []).length ? h("ul.bl", val.map(x => h("li", x))) : null;
    if (!val) return null;
    return h("div.bt" + (s.verbatim ? ".verbatim" : ""), val);
  };

  const sectionCard = s => {
    const st = s.pending ? (s.state === "empty" ? "proposed" : "revision") : s.state;
    const chip = { empty: ["vacío", "ghost"], proposed: ["propuesta", "agent"], revision: ["revisión propuesta", "agent"], approved: ["aprobado", "good"], imported: ["importado", "ghost"] }[st];
    const card = h("div.bsec." + st, { id: "sec-" + s.key },
      h("div.row.between", h("div.row", h("span.bn", s.label), s.required ? h("span.chip.ghost", "requerido") : null, h(`span.chip.${chip[1]}`, chip[0])),
        editing === s.key ? null : h("div.row", { style: { gap: "4px" } },
          s.state !== "empty" || !s.pending ? btn(s.state === "empty" ? "Escribir" : "Editar", { sm: true, variant: "ghost", icon: "edit", onClick: () => { editing = s.key; focusNext = true; paintRight(); } }) : null)),
      editing === s.key ? editor(s, s.pending ? s.pending.value : s.value) : [
        s.state === "empty" && !s.pending ? h("div.small.faint", s.hint + " Cuéntaselo al Briefer o escríbelo tú.") : valueView(s, s.value),
        s.pending ? proposalView(s) : null,
        s.meta && s.meta.state === "approved" && s.meta.by ? h("div.small.faint", `Aprobado por ${s.meta.by === "hugo" ? "ti" : s.meta.by} · ${hhmm(s.meta.at)}`
          + (s.meta.version > 1 ? ` · v${s.meta.version}` : "") + (BASIS[s.meta.basis] ? ` · ${BASIS[s.meta.basis][0]}` : "")) : null]);
    return card;
  };

  const proposalView = s => {
    const p = s.pending, b = BASIS[p.basis] || [p.basis, "ghost"];
    return h("div.proposal",
      h("div.row.wrap", h("span.eyebrow.agent", p.revises ? "El Briefer propone cambiarlo" : "Propuesta del Briefer"), h(`span.chip.${b[1]}`, b[0])),
      valueView(s, p.value),
      p.hugo_wording ? h("div.small", h("span.muted", "Tus palabras: "), h("span.voice", { style: { fontSize: "14.5px" } }, p.hugo_wording)) : null,
      p.why ? h("div.small.muted", p.why) : null,
      h("div.row", { style: { gap: "6px", marginTop: "6px" } },
        btn("Aprobar", { sm: true, variant: "human", human: true, icon: "check", onClick: async () => { await api.cpost(`/brief/sections/${s.key}/approve`); await paint(); } }),
        btn("Editar y aprobar", { sm: true, icon: "edit", onClick: () => { editing = s.key; focusNext = true; paintRight(); } }),
        btn("Descartar", { sm: true, variant: "ghost", icon: "x", onClick: async () => { await api.cpost(`/brief/sections/${s.key}/discard`); await paint(); } })));
  };

  const editor = (s, val) => {
    const t = autosize(h("textarea", { placeholder: s.hint }));
    t.value = drafts[s.key] ?? (s.kind === "list" ? (val || []).join("\n") : (val || ""));
    t.addEventListener("input", () => { drafts[s.key] = t.value; });
    const wasFocused = document.activeElement && document.activeElement.closest && document.activeElement.closest("#sec-" + s.key);
    requestAnimationFrame(() => { t.dispatchEvent(new Event("input")); if (focusNext || wasFocused) { t.focus(); focusNext = false; } });
    return h("div.editor", t, h("div.small.faint", s.kind === "list" ? "Uno por línea. Al guardar queda aprobado por ti." : "Al guardar queda aprobado por ti."),
      h("div.row", { style: { gap: "6px" } },
        btn("Guardar", { sm: true, variant: "human", human: true, icon: "check", onClick: async () => {
          const value = s.kind === "list" ? t.value.split("\n").map(x => x.trim()).filter(Boolean) : t.value.trim();
          await api.cput(`/brief/sections/${s.key}`, { value }); editing = null; delete drafts[s.key]; toast(`${s.label} aprobado`, "ok"); await paint(); } }),
        btn("Cancelar", { sm: true, variant: "ghost", onClick: () => { editing = null; delete drafts[s.key]; paintRight(); } })));
  };

  // ------------------------------------------------------------ data model
  const dataModelCard = () => {
    const bound = data.data_model;
    if (bound && bound.available !== false) {
      return h("div.panel.pad.dmcard",
        h("div.row.between.wrap", h("div", h("div.eyebrow.accent", "Modelo de datos del caso"), h("div", { style: { fontSize: "17px", fontWeight: 620, marginTop: "4px" } }, bound.label),
          h("div.small.muted", bound.source)),
          h("div.row", btn("Explorar y consultar", { icon: "table", variant: "primary", onClick: () => app.go("#/data") }),
            btn("Quitar", { sm: true, variant: "ghost", onClick: async () => { await api.cdel("/datamodel"); toast("El caso ya no usa ese modelo", "info"); await paint(); } }))),
        layersView(bound), checksLine(bound));
    }
    const avail = (data.data_models || []);
    return h("div.panel.pad.dmcard",
      h("div.eyebrow.accent", "Modelo de datos del caso"),
      h("p.small.muted", { style: { margin: "6px 0 12px" } }, "Elige de dónde salen los datos. Queda enlazado al caso: Analytics lo consulta y tú puedes comprobar cualquier cifra contra él."),
      avail.length ? h("div.stack", avail.map(m => h("div.dmopt",
        h("div.row.between.wrap", h("div", h("div", { style: { fontWeight: 620 } }, m.label), h("div.small.muted", m.source)),
          m.available ? h("div.row", btn("Ver", { sm: true, variant: "ghost", icon: "eye", onClick: () => app.go("#/data/" + m.id) }),
            btn("Usar este modelo", { sm: true, variant: "human", human: true, icon: "check", onClick: async () => {
              await api.cpost("/datamodel", { model_id: m.id }); toast(`Modelo enlazado: ${m.label}`, "ok"); await paint(); } })) : h("span.chip.warn", "no disponible")),
        m.available ? [layersView(m), checksLine(m)] : h("div.small.muted", m.note || "")))) : empty("Sin modelos disponibles", "No encontré un workspace analítico junto a CaseOS."));
  };
  const layersView = m => h("div.layers", (m.layers || []).map((l, i) => [i ? h("span.larrow", "→") : null,
    h("div.layer", h("div.ln", l.label), h("div.small.muted", `${l.tables} ${l.tables === 1 ? "tabla" : "tablas"} · ${fmt(l.rows)} filas`))]));
  const checksLine = m => m.checks ? h("div.small", { style: { marginTop: "8px", color: m.checks.fail ? "var(--bad-ink)" : "var(--good-ink)" } },
    icon(m.checks.fail ? "x" : "check"), ` ${m.checks.ok}/${m.checks.total} checks de reconciliación entre capas`) : null;

  put(root, head, h("div.split",
    h("div.convo", h("div.row.between.mb", h("span.eyebrow.human", "Conversación con el Briefer"), h("span.small.faint", "⌘↵ para enviar")), stream,
      h("div.composer", ta, h("div.bar2", h("span.small.faint", "Propone secciones; tú apruebas cada una"), h("span.spacer"),
        btn("Enviar", { variant: "primary", icon: "send", onClick: send })))),
    h("div", { style: { minWidth: 0 } }, right)));
  await paint();
  const onJob = ev => { if (ev.job.kind === "briefer_turn" && ["running", "skills", "succeeded", "failed"].includes(ev.event.kind)) paint(); };
  app.on("job", onJob);
  return { update: paint, destroy: () => { app.listeners.job = (app.listeners.job || []).filter(f => f !== onJob); } };
}

const fmt = n => (n || 0).toLocaleString("es-MX").replace(/,/g, ".");
