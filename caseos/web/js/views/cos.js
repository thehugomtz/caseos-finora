// Chief of Staff — control room. Case health, next best actions, impact alerts with options (Hugo decides),
// hypotheses, decisions, readiness, and "ask the COS" about the whole case.
import { h, mount as put, autosize } from "../core/dom.js";
import { api } from "../core/api.js";
import { icon } from "../core/icons.js";
import { app } from "../app.js";
import { idTag, statusChip, btn, empty, toast, thinking, ids, hhmm, ago, review, PHASE_LABEL, STATUS_LABEL } from "../ui/components.js";
import { markdown } from "../ui/markdown.js";

export async function mount(root) {
  const body = h("div");
  const ask = autosize(h("textarea", { placeholder: "Pregúntale al COS sobre el caso completo: «¿Qué falta para cerrar Growth?» · «¿Qué claims están más débiles?»" }));
  let asking = false;
  const doAsk = async () => {
    const q = ask.value.trim();
    if (!q) return;
    asking = true;
    ask.value = "";
    try { await api.cpost("/cos/ask", { question: q }); toast("El COS está revisando el caso", "agent"); } catch (e) { toast(e.message, "err"); asking = false; }
    paint();
  };
  ask.addEventListener("keydown", e => { if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) doAsk(); });
  const askBox = h("div.qbox", ask, h("div.row", h("span.small.faint", "⌘↵"), h("span.spacer"), btn("Preguntar al COS", { variant: "primary", icon: "orbit", onClick: doAsk })));
  const paint = async () => {
    const [room, conv] = await Promise.all([api.cget("/cos/room"), api.cget("/cos/conversation")]);
    const hl = room.health;
    const ph = hl.phases.find(p => p.id === "synthesis");
    const running = app.running.filter(j => j.agent === "cos");
    app.crumbs(["Chief of Staff"]);
    put(body,
      h("div.head", h("div", h("div.eyebrow", "04 · Synthesis · Case Chief of Staff"), h("h1.title", "Control room"),
        h("p.lede", "El COS no es el mejor analista: es quien sabe qué pasa en todo el caso. Detecta cuándo la evidencia nueva toca la historia, propone opciones y registra tus decisiones. Recomienda; tú decides.")),
        h("div.actions", statusChip(ph.status), running.length ? h("span.row", thinking(), h("span.small.muted", running[0].title)) : null,
          btn(ph.status === "ready" ? "Síntesis aprobada" : "Mark Synthesis Ready", { variant: "human", human: true, disabled: ph.status === "ready", onClick: () => app.markReady("synthesis") }))),
      h("div.metrics", metric("Fase actual", PHASE_LABEL[hl.phase], (hl.phases.find(p => p.id === hl.phase) || {}).status ? STATUS_LABEL[hl.phases.find(p => p.id === hl.phase).status] : ""),
        metric("Evidencia aceptada", hl.evidence_accepted, `${hl.evidence_proposed} findings por revisar · ${hl.tables_accepted} tablas`),
        metric("Story", hl.claims_total ? `${hl.claims_supported}/${hl.claims_total}` : "—", "claims con soporte"),
        metric("Esperan tu juicio", hl.alerts_open + hl.decisions_open, `${hl.alerts_open} alertas · ${hl.decisions_open} decisiones · ${hl.stale} needs_review`)),
      room.status_note ? h("div.panel.tight.mt", { style: { borderColor: "rgba(143,164,255,.22)" } }, h("div.row", h("span.eyebrow.accent", "Nota del COS"), h("span.small.faint", ago(room.status_note_at))), h("div.prose", { style: { marginTop: "6px" } }, room.status_note)) : null,
      h("div.split.mt2",
        h("div.stack.lg",
          h("div.panel.flush.nbas", h("div.phead", h("h2.sec", "Next best actions", h("span.count", String(room.next_best_actions.length))), h("span.small.faint", "reglas deterministas + COS; nada avanza solo")),
            h("div.pbody", room.next_best_actions.length ? room.next_best_actions.map(a => h("div.nba", h("span.n", String(a.n)), h("div", h("div.t", a.title), h("div.w", a.why), a.ids && a.ids.filter(x => x && /^[A-Z]-\d/.test(x)).length ? h("div.row.wrap", { style: { marginTop: "6px" } }, ids(a.ids.filter(x => x && /^[A-Z]-\d/.test(x)), 5)) : null),
              nbaButton(a))) : empty("Nada urgente", "El caso está al día."))),
          h("div", h("div.row.between.mb", h("h2.sec", "Alertas de impacto", h("span.count", String(room.alerts.length))), h("span.small.faint", "nueva evidencia que puede cambiar la historia")),
            room.alerts.length ? h("div.stack", room.alerts.map(alertCard)) : empty("Sin alertas abiertas", "Cuando llegue research nuevo, el COS evalúa si apoya, debilita o contradice hipótesis y claims.")),
          h("div.panel.pad", h("div.eyebrow.accent", "Pregúntale al COS"), h("div.mt", askBox),
            h("div.stack.mt", conv.conversation.slice().reverse().slice(0, 5).map(c => h("div.answer-card", h("div.small.muted", `${hhmm(c.ts)} · ${c.question}`),
              h("div.prose", { style: { color: "var(--ink)", marginTop: "6px" } }, markdown(c.answer)), c.referenced_ids.length ? h("div.row.wrap", ids(c.referenced_ids, 10)) : null))))),
        h("div.stack.lg",
          h("div.panel.pad", h("div.eyebrow", "Framing vigente"), h("div.serif", { style: { fontSize: "19px", lineHeight: 1.35, margin: "10px 0" } }, room.current_framing.executive_question || "—"),
            room.current_framing.frames.length ? h("div.row.wrap", room.current_framing.frames.map(f => h("span.chip.human", f.name))) : null),
          h("div.panel.pad", h("div.row.between", h("div.eyebrow", "Story vigente"), btn("Abrir Story", { sm: true, variant: "ghost", onClick: () => app.go("#/story") })),
            room.current_story.governing_thought ? h("div.serif", { style: { fontSize: "18px", margin: "10px 0" } }, room.current_story.governing_thought) : h("div.small.muted.mt", "Todavía no hay Story Package."),
            room.current_story.claims.length ? h("div.list", room.current_story.claims.map(c => h("div.item", { on: { click: () => app.openEntity(c.id) } }, idTag(c.id), h("div.body", h("div.t.clamp2", c.text)), statusChip(c.strength.level === "supported" ? "supported" : c.strength.level === "weak" ? "weak" : "unsupported")))) : null),
          h("div.panel.flush", h("div.phead", h("h2.sec", "Hipótesis activas", h("span.count", String(room.hypotheses.length)))),
            h("div.pbody", { style: { maxHeight: "440px", overflowY: "auto" } }, room.hypotheses.map(hy => h("div.hyp", { on: { click: () => app.openEntity(hy.id) } },
              h("div", h("div.row", idTag(hy.id, { alias: hy.alias, stale: hy.stale }), h("span.st." + hy.status, STATUS_LABEL[hy.status] || hy.status), hy.assessed ? h("span.chip.accent", "agente: " + hy.assessed.state) : null),
                h("div.small", { style: { marginTop: "6px", color: "var(--ink-2)" } }, hy.text)),
              h("div.small.faint", { style: { textAlign: "right" } }, `${hy.research.length} R · ${hy.findings.length} F`))))),
          h("div.panel.flush", h("div.phead", h("h2.sec", "Decisiones", h("span.count", String(room.decisions_open.length + room.decisions_recent.length))), btn("Decision log", { sm: true, variant: "ghost", onClick: () => app.go("#/artifacts/decisions") })),
            h("div.pbody", room.decisions_open.map(d => h("div.item", { on: { click: () => app.openEntity(d.id) } }, idTag(d.id), h("div.body", h("div.t.clamp2", d.text)), h("span.chip.human", "por confirmar"))),
              room.decisions_recent.slice(0, 5).map(d => h("div.item", { on: { click: () => app.openEntity(d.id) } }, idTag(d.id), h("div.body", h("div.t.clamp2", d.text)), h("span.small.faint", "activa"))))),
          h("div.panel.pad", h("div.eyebrow", "Readiness por fase"), h("div.stack.mt", Object.entries(room.readiness).map(([p, r]) => h("div",
            h("div.row.between", h("span", { style: { fontWeight: 560 } }, PHASE_LABEL[p]), r.ok ? h("span.chip.good", "puede marcarse Ready") : h("span.chip.warn", `${r.blockers.length} bloqueo(s)`)),
            r.blockers.concat(r.warnings).slice(0, 2).map(x => h("div.small.muted", "· " + x)))))))));
  };
  put(root, body);
  await paint();
  return { update: paint };
}

function metric(k, v, n) { return h("div.metric", h("div.k", k), h("div.v", String(v ?? "—")), n ? h("div.n", n) : null); }

function nbaButton(a) {
  const k = (a.action || {}).kind;
  if (k === "mark_ready") return btn("Mark Ready", { sm: true, variant: "human", human: true, onClick: () => app.markReady(a.action.phase) });
  if (k === "open") return btn("Abrir", { sm: true, onClick: () => a.action.id.startsWith("R-") ? app.go("#/research/" + a.action.id) : app.openEntity(a.action.id) });
  if (k === "research_needed") return btn("Framing", { sm: true, onClick: () => app.go("#/framing") });
  if (k === "story_package") return btn("Story", { sm: true, onClick: () => app.go("#/story") });
  return h("span");
}

function alertCard(x) {
  return h("div.alertcard." + (x.kind || ""),
    h("div.row.between", h("div.row.wrap", idTag(x.id), h("span.eyebrow", { style: { color: "#ff9aa2" } }, { contradiction: "Contradicción", weakening: "Debilita la historia", story_change: "Cambia la historia", framing_change: "Cambia el framing", new_hypothesis: "Nueva hipótesis", research_needed: "Requiere research", story_review: "Revisar claim" }[x.kind] || "Alerta"),
      x.severity ? h("span.chip." + (x.severity === "high" ? "bad" : "warn"), x.severity) : null), h("span.small.faint", x.source && x.target ? `${x.source} → ${x.target}` : "")),
    h("div", h("div.small.muted", "Nueva evidencia"), h("div", { style: { marginTop: "3px" } }, x.finding || "")),
    x.target ? h("div", h("div.small.muted", "Afecta a"), h("div.row", { style: { marginTop: "4px" } }, idTag(x.target), h("span.small", x.target_text || ""))) : null,
    h("div", h("div.small.muted", "Por qué"), h("div.small", { style: { marginTop: "3px" } }, x.why || "")),
    (x.options || []).length ? h("div.opts", x.options.map(o => h("div.opt" + (o.key === x.recommended ? ".rec" : ""), h("span.key", o.key), h("div", h("div", o.label), o.consequence ? h("div.c", o.consequence) : null),
      o.key === x.recommended ? h("span.chip.accent", "recomendada") : h("span")))) : null,
    x.recommended_why ? h("div.small.muted", "Recomendación del COS: " + x.recommended_why) : null,
    h("div.row.wrap", btn("Decidir", { variant: "human", human: true, onClick: () => app.resolveAlert(x) }),
      btn("Discuss", { variant: "ghost", onClick: async () => { await api.action(x.id, "resolve", { choice: "discuss" }); sessionStorage.setItem("caseos.framer.prefill", `El COS detectó: ${x.title}. ${x.why} ¿Cómo lo reencuadramos?`); app.go("#/framing"); } }),
      btn("Research", { variant: "ghost", onClick: () => app.go("#/research?q=" + encodeURIComponent("Profundizar: " + (x.finding || ""))) }),
      btn("Ignore", { variant: "ghost", onClick: () => app.resolveAlert({ ...x, recommended: "ignore" }) })));
}
