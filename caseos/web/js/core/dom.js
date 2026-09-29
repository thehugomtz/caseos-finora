// Tiny hyperscript: h("div.panel.pad", {on: {click}}, "text", child, [children]) — no framework, no build step.
export function h(tag, props, ...children) {
  if (props && (typeof props !== "object" || props instanceof Node || Array.isArray(props))) { children.unshift(props); props = null; }
  const m = String(tag).match(/^([a-z0-9-]*)((?:[.#][\w-]+)*)$/i) || [null, String(tag), ""];
  const name = m[1] || "div";
  const parts = m[2].match(/[.#][\w-]+/g) || [];
  const classes = parts.filter(p => p[0] === ".").map(p => p.slice(1));
  const idPart = parts.find(p => p[0] === "#");
  const el = name === "svg" || name === "path" || name === "circle" || name === "line" || name === "rect" || name === "g" || name === "text" || name === "polyline"
    ? document.createElementNS("http://www.w3.org/2000/svg", name) : document.createElement(name);
  if (classes.length) el.setAttribute("class", classes.join(" "));
  if (idPart) el.id = idPart.slice(1);
  if (props) {
    for (const [k, v] of Object.entries(props)) {
      if (v === null || v === undefined || v === false) continue;
      if (k === "on") { for (const [ev, fn] of Object.entries(v)) el.addEventListener(ev, fn); }
      else if (k === "class") el.setAttribute("class", [el.getAttribute("class"), v].filter(Boolean).join(" "));
      else if (k === "style" && typeof v === "object") Object.assign(el.style, v);
      else if (k === "html") el.innerHTML = v;
      else if (k === "dataset") Object.assign(el.dataset, v);
      else if (k in el && !(el instanceof SVGElement) && typeof v !== "string") el[k] = v;
      else el.setAttribute(k, v === true ? "" : v);
    }
  }
  add(el, children);
  return el;
}

function add(el, children) {
  for (const c of children) {
    if (c === null || c === undefined || c === false) continue;
    if (Array.isArray(c)) add(el, c);
    else el.append(c instanceof Node ? c : document.createTextNode(String(c)));
  }
}

export const $ = (sel, root = document) => root.querySelector(sel);
export const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));
export function mount(el, ...children) { el.replaceChildren(); add(el, children); return el; }
export function debounce(fn, ms) { let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); }; }
export const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
export function autosize(ta) { const f = () => { ta.style.height = "auto"; ta.style.height = Math.min(ta.scrollHeight, 220) + "px"; }; ta.addEventListener("input", f); requestAnimationFrame(f); return ta; }
