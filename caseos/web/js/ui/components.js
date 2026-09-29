// Shared UI pieces: IDs with lineage color, review/status badges, epistemic chips, buttons, empty states,
// modals (confirm / prompt), toasts, tabs, segmented controls, YAML viewer, relative time.
import { h } from "../core/dom.js";
import { icon } from "../core/icons.js";
import { app } from "../app.js";

const TYPE = { Q: "question", H: "hypothesis", N: "note", R: "research", F: "finding", T: "table", D: "decision", X: "alert", C: "claim", S: "slide", A: "artifact" };
export const typeOf = id => TYPE[String(id || "").split("-")[0]] || null;
export const TYPE_LABEL = { question: "Pregunta", hypothesis: "Hipótesis", note: "Idea", research: "Research", finding: "Finding", table: "Tabla",
  decision: "Decisión", alert: "Alerta", claim: "Claim", slide: "Slide", artifact: "Artefacto" };
export const KIND_LABEL = { FACT: "Hecho", OBSERVATION: "Observación", USER_INTUITION: "Intuición de Hugo", ASSUMPTION: "Supuesto",
  HYPOTHESIS: "Hipótesis", QUESTION: "Pregunta", PROPOSAL: "Propuesta", DECISION: "Decisión", UNKNOWN: "Desconocido" };
export const STATUS_LABEL = { open: "abierta", supported: "soportada", weakened: "debilitada", contested: "en disputa", rejected: "rechazada",
  queued: "en cola", running: "en curso", completed: "completada", failed: "falló", blocked: "bloqueada", draft: "borrador", idle: "en reposo", waiting: "espera a Hugo", interrupted: "interrumpida", incomplete: "incompleto", prepared: "preparado", cancelled: "cancelada",
  proposed: "propuesta", active: "activa", superseded: "reemplazada", reverted: "revertida", resolved: "resuelta", dismissed: "descartada",
  answered: "respondida", parked: "aparcada", valid: "válida", invalid: "inválida", weak: "débil", unsupported: "sin soporte", passed: "pasó QA",
  rendered: "renderizada", escalated: "escalada", not_started: "sin iniciar", in_progress: "en curso", review: "por revisar", ready: "Ready",
  reopened: "reabierta", needs_review: "needs_review", pending: "espera tu aceptación" };
export const PHASE_LABEL = { briefing: "Briefing", framing: "Framing & Shaping", research: "Research", synthesis: "Chief of Staff", story: "Story", slides: "Slides" };

export function idTag(id, opts = {}) {
  const t = typeOf(id);
  const el = h("span.id", { title: opts.title || (TYPE_LABEL[t] || "") + " " + id, on: { click: e => { e.stopPropagation(); app.openEntity(id); } } },
    h("i", { style: { "--t": `var(--t-${t || "artifact"})` } }), id, opts.alias ? h("span.al", opts.alias) : null);
  if (opts.stale) el.classList.add("stale");
  return el;
}

export function review(state, stale) {
  if (stale) return h("span.rv.stale", "needs_review");
  const lab = { proposed: "propuesto", accepted: "aceptado", rejected: "rechazado" }[state] || state || "propuesto";
  return h(`span.rv.${state || "proposed"}`, lab);
}

export function kindChip(kind) { return h(`span.kind.${kind}`, KIND_LABEL[kind] || kind); }

export function statusChip(status, cls) {
  const map = { completed: "good", supported: "good", ready: "good", active: "human", resolved: "good", passed: "good", running: "agent", queued: "agent",
    in_progress: "accent", review: "human", failed: "bad", blocked: "warn", weakened: "warn", contested: "bad", reopened: "warn", needs_review: "warn",
    weak: "warn", unsupported: "bad", proposed: "", open: "", invalid: "bad", pending: "human" };
  return h(`span.chip.${cls || map[status] || "ghost"}`, STATUS_LABEL[status] || status || "—");
}

export function btn(label, opts = {}) {
  const b = h(`button.btn${opts.variant ? "." + opts.variant : ""}${opts.sm ? ".sm" : ""}`, { type: "button", title: opts.title || null, disabled: opts.disabled || null,
    on: { click: async e => { if (!opts.onClick) return; b.disabled = true; try { await opts.onClick(e); } finally { if (b.isConnected) b.disabled = !!opts.disabled; } } } },
    opts.icon ? icon(opts.icon) : null, opts.human ? h("span.diamond") : null, label);
  return b;
}

export function empty(title, text) { return h("div.empty", h("b", title), text || null); }
export function section(title, count, right) {
  return h("div.row.between.mb", h("h2.sec", title, count !== undefined && count !== null ? h("span.count", String(count)) : null), right || null);
}
export function thinking() { return h("span.thinking", h("i"), h("i"), h("i")); }
export function lensChip(l) { return h("span.lens", icon("eye"), "Lente " + ({ ceo: "CEO", cro: "CRO", cfo: "CFO", cpo: "CPO", cdo: "CDO" }[l] || l)); }

export function ago(iso) {
  if (!iso) return "";
  const s = (Date.now() - new Date(iso).getTime()) / 1000;
  if (s < 60) return "hace un momento";
  if (s < 3600) return `hace ${Math.round(s / 60)} min`;
  if (s < 86400) return `hace ${Math.round(s / 3600)} h`;
  return new Date(iso).toLocaleDateString("es", { day: "numeric", month: "short" });
}
export const hhmm = iso => iso ? new Date(iso).toLocaleTimeString("es", { hour: "2-digit", minute: "2-digit" }) : "";

/* ------------------------------------------------------------------ toasts */
export function toast(text, kind = "info", ms = 4200) {
  let box = document.querySelector(".toasts");
  if (!box) { box = h("div.toasts"); document.body.append(box); }
  const t = h(`div.toast.${kind}`, h("span.i"), h("div", text));
  box.append(t);
  setTimeout(() => { t.style.opacity = "0"; t.style.transition = "opacity .3s"; setTimeout(() => t.remove(), 320); }, ms);
}

/* ------------------------------------------------------------------ modals */
export function modal({ eyebrow, title, body, actions = [], wide = false, onClose }) {
  const wrap = h("div.modal-wrap");
  const close = () => { wrap.remove(); document.removeEventListener("keydown", esc); if (onClose) onClose(); };
  const esc = e => { if (e.key === "Escape") close(); };
  document.addEventListener("keydown", esc);
  const box = h("div.modal", { style: wide ? { width: "min(860px, 96vw)" } : null },
    eyebrow ? h("div.eyebrow", eyebrow) : null, title ? h("h3", title) : null, body,
    h("div.foot", actions.map(a => btn(a.label, { variant: a.variant, human: a.human, onClick: async () => { const r = a.onClick ? await a.onClick() : null; if (r !== false) close(); } }))));
  wrap.addEventListener("mousedown", e => { if (e.target === wrap) close(); });
  wrap.append(box);
  document.body.append(wrap);
  const first = box.querySelector("textarea, input");
  if (first) setTimeout(() => first.focus(), 30);
  return { close, box };
}

export function confirmDialog({ eyebrow, title, text, detail, confirmLabel = "Confirmar", human = false, field }) {
  return new Promise(resolve => {
    let input = null;
    const body = h("div.stack", text ? h("p.muted", { style: { margin: 0 } }, text) : null, detail || null,
      field ? h("div.field", h("label", field.label), input = h(field.multiline === false ? "input" : "textarea", { placeholder: field.placeholder || "", value: field.value || "" })) : null);
    modal({ eyebrow, title, body, onClose: () => resolve(null), actions: [
      { label: "Cancelar", variant: "ghost", onClick: () => resolve(null) },
      { label: confirmLabel, variant: human ? "human" : "primary", human, onClick: () => {
        const v = input ? input.value.trim() : true;
        if (field && field.required && !v) { input.focus(); input.style.borderColor = "var(--bad)"; return false; }
        resolve(input ? v : true);
      } }] });
  });
}

/* ------------------------------------------------------------------ tabs / segmented */
export function tabs(items, active, onPick) {
  return h("div.tabs", items.map(it => h("button" + (it.id === active ? ".on" : ""), { type: "button", on: { click: () => onPick(it.id) } }, it.label,
    it.count !== undefined ? h("span.count", String(it.count)) : null)));
}
export function seg(items, active, onPick) {
  return h("div.seg", items.map(it => h("button" + (it.id === active ? ".on" : ""), { type: "button", title: it.title || null, on: { click: () => onPick(it.id) } }, it.label)));
}

/* ------------------------------------------------------------------ YAML / JSON viewer */
export function dataView(v, depth = 0) {
  if (v === null || v === undefined) return h("span.s", "—");
  if (typeof v === "boolean") return h("span.b", String(v));
  if (typeof v === "number") return h("span.n", String(v));
  if (typeof v === "string") return h("span.s", v);
  if (Array.isArray(v)) {
    if (!v.length) return h("span.s", "[]");
    if (v.every(x => typeof x !== "object" || x === null) && v.join(", ").length < 90) return h("span.s", "[" + v.join(", ") + "]");
    return h("div.i", v.slice(0, 200).map(x => h("div.li", typeof x === "object" && x !== null ? dataView(x, depth + 1) : dataView(x, depth + 1))));
  }
  return h("div" + (depth ? ".i" : ""), Object.entries(v).map(([k, x]) =>
    typeof x === "object" && x !== null && (Array.isArray(x) ? x.some(y => typeof y === "object") || x.join(", ").length >= 90 : Object.keys(x).length)
      ? h("div", h("span.k", k + ":"), dataView(x, depth + 1))
      : h("div", h("span.k", k + ": "), dataView(x, depth + 1))));
}

export function kv(rows) {
  return h("dl.kv", rows.filter(r => r && r[1] !== undefined && r[1] !== null && r[1] !== "").map(([k, v]) => [h("dt", k), h("dd", v instanceof Node ? v : String(v))]));
}

export function ids(list, max = 12) {
  const arr = (list || []).filter(Boolean);
  return h("span.row.wrap", { style: { gap: "6px" } }, arr.slice(0, max).map(i => idTag(i)), arr.length > max ? h("span.faint.small", `+${arr.length - max}`) : null);
}
