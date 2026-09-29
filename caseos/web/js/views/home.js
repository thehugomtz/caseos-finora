// Home — current state, not vanity metrics: where the case is, what waits for Hugo's judgment, what agents are doing.
import { h, mount } from "../core/dom.js";
import { api } from "../core/api.js";
import { icon } from "../core/icons.js";
import { app } from "../app.js";
import { idTag, statusChip, btn, empty, hhmm, ago, STATUS_LABEL, PHASE_LABEL } from "../ui/components.js";

const PHASE_VIEW = { briefing: "#/briefing", framing: "#/framing", research: "#/research", synthesis: "#/cos", story: "#/story", slides: "#/slides" };

export async function mount_(root) {
  const body = h("div");
  const paint = async () => {
    const [room, act, conv] = await Promise.all([api.cget("/cos/room"), api.cget("/activity?limit=40"), api.cget("/framing").then(r => r.conversation).catch(() => [])]);
    const s = app.summary, m = s.meta, hl = room.health;
    const cur = hl.phases.find(p => p.id === hl.phase) || hl.phases[0];
    const nba = room.next_best_actions[0];
    const lastMaterial = act.activity.find(a => a.material && a.actor !== "system");
    const claimsPct = hl.claims_total ? Math.round(100 * hl.claims_supported / hl.claims_total) : 0;
    app.crumbs(["Home"]);
    mount(body,
      h("div.head",
        h("div", h("div.eyebrow", `${m.client || "Caso"} · ${(m.audience || []).join(" · ")}`), h("h1.title", m.title || m.name),
          h("p.lede", m.objective || "")),
        h("div.actions", btn("⌘K Buscar", { variant: "ghost", onClick: () => document.dispatchEvent(new KeyboardEvent("keydown", { key: "k", metaKey: true })) }),
          btn("Demo mode", { icon: "demo", onClick: () => app.startDemo() }))),
      // continue where you left off
      h("div.split",
        h("div.panel.pad.glow", h("div.eyebrow.accent", "Continúa donde lo dejaste"),
          h("div", { style: { margin: "10px 0 4px", fontSize: "22px", fontWeight: 600, letterSpacing: "-.015em" } }, `${cur.n} · ${cur.label}`),
          h("div.row", statusChip(cur.status), h("span.small.muted", cur.ready_at ? `Ready ${ago(cur.ready_at)}` : cur.unlocked ? "desbloqueada" : "bloqueada hasta cerrar la fase anterior")),
          nba ? h("div", { style: { marginTop: "18px", paddingTop: "14px", borderTop: "1px solid var(--line)" } }, h("div.eyebrow", "Siguiente mejor acción · COS"),
            h("div", { style: { fontSize: "15.5px", fontWeight: 560, margin: "6px 0 4px" } }, nba.title), h("div.small.muted", nba.why),
            h("div.row.mt", actionButton(nba), btn(`Ver las ${room.next_best_actions.length}`, { variant: "ghost", onClick: () => app.go("#/cos") }))) : null,
          lastMaterial ? h("div.small.faint.mt", `Último cambio material: ${lastMaterial.summary} · ${ago(lastMaterial.ts)}`) : null),
        h("div.panel.pad", h("div.eyebrow", "Story readiness"),
          h("div.row", { style: { alignItems: "baseline", gap: "10px", marginTop: "10px" } }, h("span", { style: { fontSize: "40px", fontWeight: 620, letterSpacing: "-.03em" } }, hl.claims_total ? `${claimsPct}%` : "—"),
            h("span.muted", hl.claims_total ? `${hl.claims_supported} de ${hl.claims_total} claims con evidencia aceptada y cifras en tabla` : "Todavía no hay claims: la story empieza cuando el COS arma el Story Package")),
          h("div.bar", h("i", { style: { width: claimsPct + "%" } })),
          h("div.grid2.mt", stat("Evidencia aceptada", hl.evidence_accepted, `${hl.evidence_proposed} por revisar`, "#/research"),
            stat("Tablas canónicas", hl.tables_accepted, "aceptadas para slides", "#/artifacts/evidence"),
            stat("Research por revisar", hl.research_review, `${hl.research_running} en curso · ${hl.research_blocked} bloqueadas`, "#/research"),
            stat("Esperan tu decisión", hl.decisions_open + hl.alerts_open, `${hl.decisions_open} decisiones · ${hl.alerts_open} alertas`, "#/cos")))),
      // phases
      h("div.mt2", h("div.row.between.mb", h("h2.sec", "Fases del caso"), h("span.small.muted", "Solo Hugo marca Ready · reabrir calcula el radio de impacto primero")),
        h("div.phases", hl.phases.map(p => h("div.phase." + p.status + (p.id === hl.phase ? ".current" : "") + (!p.unlocked && p.status === "not_started" ? ".locked" : ""),
          { on: { click: () => app.go(PHASE_VIEW[p.id]) } }, h("div.n", p.n), h("div.l", PHASE_LABEL[p.id] === "Chief of Staff" ? "Synthesis" : p.label),
          h("div.s", h("span.pdot." + p.status), STATUS_LABEL[p.status], p.ready_count ? h("span.faint", `· v${p.ready_count}`) : null))))),
      h("div.grid3.mt2",
        h("div.panel.flush", h("div.phead", h("h2.sec", "Decisiones abiertas", h("span.count", String(room.decisions_open.length + room.alerts.length)))),
          h("div.pbody", room.alerts.length || room.decisions_open.length ? h("div.list", room.alerts.slice(0, 4).map(x => row(x.id, x.title || x.text, x.severity === "high" ? "alta" : x.severity)),
            room.decisions_open.slice(0, 5).map(d => row(d.id, d.text, "por confirmar"))) : empty("Nada espera tu decisión", "Las alertas del COS y las decisiones propuestas aparecen aquí."))),
        h("div.panel.flush", h("div.phead", h("h2.sec", "Preguntas abiertas", h("span.count", String(room.open_questions.length)))),
          h("div.pbody", room.open_questions.length ? h("div.list", room.open_questions.slice(0, 6).map(q => row(q.id, q.text, q.alias))) : empty("Sin preguntas abiertas"))),
        h("div.panel.flush", h("div.phead", h("h2.sec", "Research en curso y por revisar")),
          h("div.pbody", h("div.list", room.research_queue.filter(r => ["queued", "running", "failed"].includes(r.status) || (r.status === "completed" && r.review === "proposed")).slice(0, 6)
            .map(r => row(r.id, r.question, r.status === "completed" ? "por revisar" : STATUS_LABEL[r.status], () => app.go("#/research/" + r.id))))))),
      h("div.split.mt2",
        h("div.panel.flush", h("div.phead", h("h2.sec", "Claims que necesitan evidencia")),
          h("div.pbody", room.current_story.claims.filter(c => c.strength.level !== "supported").length
            ? h("div.list", room.current_story.claims.filter(c => c.strength.level !== "supported").slice(0, 6).map(c => row(c.id, c.text, c.strength.level)))
            : empty(room.current_story.claims.length ? "Todos los claims tienen soporte" : "Aún no hay claims", room.current_story.claims.length ? "" : "Se crean al preparar el Story Package."))),
        h("div.panel.flush", h("div.phead", h("h2.sec", "Actividad reciente de agentes"), btn("Trace completo", { sm: true, variant: "ghost", onClick: () => app.toggleTrace() })),
          h("div.pbody", h("div.stack", { style: { gap: "2px" } }, act.activity.slice(0, 9).map(a => h("div.tline" + (a.material ? ".material" : ""), { style: { gridTemplateColumns: "48px 110px 1fr", fontFamily: "var(--mono)", fontSize: "12px" } },
            h("span.ts", hhmm(a.ts)), h("span.ac." + (a.actor === "hugo" ? "hugo" : "agent"), a.actor === "hugo" ? "Hugo" : a.actor), h("span.su", a.summary))))))));
  };
  mount(root, body);
  await paint();
  return { update: paint };
}
export { mount_ as mount };

function stat(k, v, n, go) {
  return h("div", { style: { cursor: "pointer" }, on: { click: () => app.go(go) } }, h("div.small.muted", k), h("div", { style: { fontSize: "24px", fontWeight: 600, letterSpacing: "-.02em" } }, String(v)), h("div.small.faint", n));
}
function row(id, text, side, onClick) {
  return h("div.item", { style: { gridTemplateColumns: "auto 1fr auto" }, on: { click: onClick || (() => app.openEntity(id)) } }, idTag(id), h("div.body", h("div.t.clamp2", text || "")), side ? h("span.chip.ghost", side) : h("span"));
}
function actionButton(a) {
  const k = (a.action || {}).kind;
  if (k === "mark_ready") return btn(`Mark ${PHASE_LABEL[a.action.phase]} Ready`, { variant: "human", human: true, onClick: () => app.markReady(a.action.phase) });
  if (k === "open") return btn("Abrir " + a.action.id, { variant: "primary", icon: "arrow", onClick: () => a.action.id.startsWith("R-") ? app.go("#/research/" + a.action.id) : app.openEntity(a.action.id) });
  if (k === "research_needed") return btn("Ir a Framing", { variant: "primary", icon: "arrow", onClick: () => app.go("#/framing") });
  if (k === "story_package") return btn("Ir a Story", { variant: "primary", icon: "arrow", onClick: () => app.go("#/story") });
  if (k === "cos_ask") return btn("Preguntar al COS", { variant: "primary", icon: "arrow", onClick: () => app.go("#/cos") });
  return btn("Ver", { onClick: () => app.go("#/cos") });
}
