/* Chart kit — ported from the Business Exploration Workspace (finora-eda/templates/finora_eda_app.js):
   zero-dependency SVG line / bar / waterfall / scatter / dumbbell charts with crosshair tooltips, keyboard
   navigation and a table view, plus renderVisual(spec) for the workspace's visual grammar. Changes in the port:
   ES module, dark-theme tokens (dataviz-validated palette), Finora-specific window shading removed. es-CO formats. */

const css = () => getComputedStyle(document.documentElement);
const cv = n => css().getPropertyValue(n).trim();
export const C = {};
export function refreshColors() {
  Object.assign(C, { s1: cv("--s1"), s2: cv("--s2"), s3: cv("--s3"), s4: cv("--s4"), s5: cv("--s5"), s6: cv("--s6"), s7: cv("--s7"), s8: cv("--s8"),
    ink: cv("--ink"), ink2: cv("--ink-2"), muted: cv("--ink-3"), de: cv("--de"), surface: cv("--surface") || "#101218" });
}
refreshColors();
export const PAL = () => [C.s1, C.s2, C.s3, C.s4, C.s5, C.s6, C.s7, C.s8];

/* ------------------------------------------------------------------ es-CO formats */
const MINUS = "−";
export const ok = v => v !== null && v !== undefined && isFinite(v);
export function num(v, d) {
  const s = Math.abs(v).toFixed(d || 0);
  const p = s.split(".");
  return p[0].replace(/\B(?=(\d{3})+(?!\d))/g, ".") + (p[1] ? "," + p[1] : "");
}
const sg = (v, s) => (v < 0 && /[1-9]/.test(s) ? MINUS : "") + s;
const plus = (v, s) => (v < 0 && /[1-9]/.test(s) ? MINUS : "+") + s;
const COP_U = [[1, ""], [1e3, " mil"], [1e6, " millones"], [1e9, " mil millones"]];
export function copWords(v, d) {
  if (!ok(v)) return "–";
  if (d === undefined) d = 1;
  const a = Math.abs(v);
  let k = a >= 1e9 ? 3 : a >= 1e6 ? 2 : a >= 1e3 ? 1 : 0;
  if (k === 0 && Math.round(a) >= 1000) k = 1;
  if (k > 0 && k < 3 && Number((a / COP_U[k][0]).toFixed(d)) >= 1000) k++;
  const body = k === 0 ? num(a, 0) : num(a / COP_U[k][0], d) + COP_U[k][1];
  return (v < 0 && /[1-9]/.test(body) ? MINUS : "") + "COP " + body;
}
export const f = {
  cop: v => copWords(v, 1), cop2: v => copWords(v, 2),
  copFull: v => ok(v) ? sg(v, num(Math.abs(v), 0)).replace(/^(−?)/, "$1COP ") : "–",
  int: v => ok(v) ? sg(v, num(Math.round(Math.abs(v)), 0)) : "–",
  pct: (v, d) => ok(v) ? sg(v, num(Math.abs(v) * 100, d === undefined ? 1 : d)) + "%" : "–",
  pctSigned: (v, d) => ok(v) ? plus(v, num(Math.abs(v) * 100, d || 0)) + "%" : "–",
  idx: v => ok(v) ? sg(v, num(Math.abs(v), 0)) : "–",
  num: (v, d) => ok(v) ? sg(v, num(Math.abs(v), d === undefined ? 2 : d)) : "–",
  x: v => ok(v) ? num(v, 1) + "×" : "–",
};
function axisFmt(kind, ticks) {
  const step = ticks.length > 1 ? Math.abs(ticks[1] - ticks[0]) : 1;
  const maxAbs = Math.max(...ticks.map(Math.abs));
  const dec = s => Math.max(0, Math.min(3, -Math.floor(Math.log10(s) + 1e-9)));
  const plain = d => v => sg(v, num(Math.abs(v), d));
  if (kind === "pct") { const d = Math.min(2, dec(step * 100)); return { f: v => sg(v, num(Math.abs(v) * 100, d)) + "%", unit: null, div: 1 }; }
  if (kind === "cop") {
    const sc = maxAbs >= 1e9 ? [1e9, "miles de millones de COP"] : maxAbs >= 1e6 ? [1e6, "millones de COP"] : maxAbs >= 1e3 ? [1e3, "miles de COP"] : [1, "COP"];
    const d = Math.min(2, dec(step / sc[0]));
    return { f: v => (v === 0 ? "0" : sg(v, num(Math.abs(v) / sc[0], d))), unit: sc[1], div: sc[0] };
  }
  if (kind === "int") return { f: plain(0), unit: null, div: 1 };
  if (kind === "idx") return { f: plain(0), unit: "índice (base 100)", div: 1 };
  return { f: plain(dec(step)), unit: null, div: 1 };
}

/* ------------------------------------------------------------------ DOM helpers */
const NS = "http://www.w3.org/2000/svg";
function S(tag, attrs, parent) {
  const e = document.createElementNS(NS, tag);
  if (attrs) for (const k in attrs) { const v = attrs[k]; if (v !== null && v !== undefined && v !== false) e.setAttribute(k, v); }
  if (parent) parent.appendChild(e);
  return e;
}
function T(parent, x, y, text, cls, anchor, extra) {
  const t = S("text", Object.assign({ x, y, class: cls, "text-anchor": anchor || "start" }, extra || {}), parent);
  t.textContent = text;
  return t;
}
function H(tag, cls, parent, text) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text !== undefined && text !== null) e.textContent = text;
  if (parent) parent.appendChild(e);
  return e;
}
const measure = (function () {
  const c = document.createElement("canvas").getContext("2d");
  return (s, font) => { c.font = font || '10.5px "IBM Plex Mono", ui-monospace, monospace'; return c.measureText(String(s)).width; };
})();
const SANS = '12px Inter, system-ui, sans-serif';
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const sum = a => a.reduce((s, v) => s + (ok(v) ? v : 0), 0);

function niceTicks(lo, hi, count) {
  if (!ok(lo) || !ok(hi)) { lo = 0; hi = 1; }
  if (lo === hi) { const d = Math.abs(lo) || 1; lo -= d * 0.5; hi += d * 0.5; }
  const raw = (hi - lo) / Math.max(1, count);
  const mag = Math.pow(10, Math.floor(Math.log10(raw)));
  const e = raw / mag;
  const step = (e >= 7.5 ? 10 : e >= 3.5 ? 5 : e >= 1.5 ? 2 : 1) * mag;
  const a = Math.floor(lo / step + 1e-9) * step, b = Math.ceil(hi / step - 1e-9) * step;
  const out = [];
  for (let v = a; v <= b + step * 1e-6; v += step) out.push(+v.toPrecision(12));
  return out;
}
const MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"];
const isMonth = l => /^[a-z]{3}-\d{2}$/.test(l) && MESES.includes(l.slice(0, 3));
function xTickList(labels, pw, mode) {
  const n = labels.length;
  if (!n) return [];
  if (!labels.every(isMonth)) {
    const maxW = Math.max(...labels.map(l => measure(l))) + 10;
    const per = pw / n;
    let every = 1;
    while (per * every < maxW && every < n) every++;
    return labels.map((l, i) => (i % every === 0 ? { i, text: l } : null)).filter(Boolean);
  }
  const per = pw / Math.max(1, mode === "band" ? n : n - 1);
  const every = per >= 19 ? 3 : per >= 9.5 ? 6 : 12;
  const out = [];
  labels.forEach((l, i) => { const m = MESES.indexOf(l.slice(0, 3)); if (m % every === 0) out.push({ i, text: m === 0 ? l : l.slice(0, 3), strong: m === 0 }); });
  return out;
}

/* ------------------------------------------------------------------ tooltip */
let tip = null;
function tipEl() { if (!tip) { tip = H("div", "fv-tip", document.body); tip.setAttribute("role", "status"); } return tip; }
function tipShow(x, y, title, rows, note) {
  const t = tipEl();
  t.replaceChildren();
  if (title) H("div", "fv-tip-title", t, title);
  rows.forEach(r => {
    const row = H("div", "fv-tip-row", t);
    const k = H("span", "fv-key " + (r.kind || "line"), row);
    if (r.color) k.style.background = r.color;
    H("span", "v", row, r.value);
    H("span", "l", row, r.label);
  });
  if (note) H("div", "fv-tip-note", t, note);
  t.classList.add("on");
  const pad = 14, w = t.offsetWidth, hh = t.offsetHeight;
  let left = x + pad, top = y + pad;
  if (left + w > window.innerWidth - 8) left = x - w - pad;
  if (top + hh > window.innerHeight - 8) top = y - hh - pad;
  t.style.transform = "translate(" + Math.max(8, left) + "px," + Math.max(8, top) + "px)";
}
function tipHide() { if (tip) tip.classList.remove("on"); }
window.addEventListener("scroll", tipHide, { passive: true, capture: true });

function yAxis(svg, o, ticks, fmt, ml, mt, pw, ph, Y) {
  ticks.forEach(t => { const y = Y(t); S("line", { x1: ml, x2: ml + pw, y1: y, y2: y, class: t === 0 ? "fv-base" : "fv-grid" }, svg); T(svg, ml - 8, y + 3.5, fmt(t), "fv-tick", "end"); });
}
function xWrap(labels, pw) {
  const n = labels.length;
  if (!n || n > 8 || labels.every(isMonth)) return null;
  const per = pw / n - 6;
  if (Math.max(...labels.map(l => measure(l))) <= per) return null;
  return labels.map(l => {
    const lines = [];
    String(l).split(/\s+/).forEach(w => { const t = lines.length ? lines[lines.length - 1] + " " + w : w; if (lines.length && measure(t) <= per) lines[lines.length - 1] = t; else lines.push(w); });
    if (lines.length > 3) { lines.length = 3; lines[2] += "…"; }
    return lines;
  });
}
function xAxis(svg, labels, X, mt, ph, pw, mode, wrapped) {
  if (wrapped) {
    wrapped.forEach((lines, i) => { const t = T(svg, X(i), mt + ph + 17, "", "fv-tick", "middle"); lines.forEach((ln, k) => { const ts = S("tspan", { x: X(i), dy: k ? 12 : 0 }, t); ts.textContent = ln || " "; }); });
    return;
  }
  xTickList(labels, pw, mode).forEach(t => T(svg, X(t.i), mt + ph + 17, t.text, "fv-tick" + (t.strong ? " strong" : ""), "middle"));
}
function unitDraw(svg, unit) { if (unit) T(svg, 0, 11, unit, "fv-unit", "start"); }
function roundedBar(x, w, yTop, yBot, roundTop, roundBot) {
  const hh = yBot - yTop;
  if (hh <= 0) return "";
  const r = Math.min(4, w / 2, roundTop && roundBot ? hh / 2 : hh);
  const rt = roundTop ? r : 0, rb = roundBot ? r : 0;
  let d = "M" + x + "," + (yBot - rb) + " L" + x + "," + (yTop + rt);
  if (rt) d += " Q" + x + "," + yTop + " " + (x + rt) + "," + yTop;
  d += " L" + (x + w - rt) + "," + yTop;
  if (rt) d += " Q" + (x + w) + "," + yTop + " " + (x + w) + "," + (yTop + rt);
  d += " L" + (x + w) + "," + (yBot - rb);
  if (rb) d += " Q" + (x + w) + "," + yBot + " " + (x + w - rb) + "," + yBot;
  d += " L" + (x + rb) + "," + yBot;
  if (rb) d += " Q" + x + "," + yBot + " " + x + "," + (yBot - rb);
  return d + " Z";
}
function keyboard(svg, n, show, hide, getCur) {
  svg.setAttribute("tabindex", "0");
  svg.addEventListener("keydown", e => {
    if (e.key === "ArrowRight" || e.key === "ArrowLeft") {
      e.preventDefault();
      const c = getCur();
      show(clamp(c < 0 ? (e.key === "ArrowRight" ? 0 : n - 1) : c + (e.key === "ArrowRight" ? 1 : -1), 0, n - 1), null);
    } else if (e.key === "Escape") hide();
  });
  svg.addEventListener("blur", hide);
}

/* ------------------------------------------------------------------ LINE */
export function lineChart(el, o) {
  el.replaceChildren();
  const W = Math.max(240, el.clientWidth || 600), Hh = o.height || 280;
  const labels = o.labels, n = labels.length;
  const series = o.series;
  let vals = [];
  series.forEach(s => s.values.forEach(v => { if (ok(v)) vals.push(v); }));
  if (o.ref) vals.push(o.ref.value);
  if (!vals.length) vals = [0, 1];
  let lo = o.yMin !== undefined ? o.yMin : Math.min(...vals);
  let hi = o.yMax !== undefined ? o.yMax : Math.max(...vals);
  if (o.includeZero !== false && o.yMin === undefined) lo = Math.min(0, lo);
  const ticks = niceTicks(lo, hi, Hh < 220 ? 4 : 5);
  lo = ticks[0]; hi = ticks[ticks.length - 1];
  const fmt = o.fmt || f.int;
  const ax = axisFmt(o.tickKind || "num", ticks);
  const tf = ax.f, unit = o.unit !== undefined ? o.unit : ax.unit;
  const ml = Math.max(...ticks.map(t => measure(tf(t)))) + 14;
  const endItems = [];
  if (o.endLabels !== false && series.length <= 4) series.forEach(s => { let i = s.values.length - 1; while (i >= 0 && !ok(s.values[i])) i--; if (i >= 0) endItems.push({ s, i, text: s.short || s.name }); });
  const mr = endItems.length ? Math.min(180, Math.max(...endItems.map(e => measure(e.text, SANS))) + 26) : 12;
  const mt = unit ? 20 : 10, mb = 26;
  const pw = Math.max(40, W - ml - mr), ph = Hh - mt - mb;
  const X = i => ml + (n === 1 ? pw / 2 : i * pw / (n - 1));
  const half = n > 1 ? pw / (n - 1) / 2 : pw / 2;
  const Y = v => mt + ph - (v - lo) / (hi - lo) * ph;
  const svg = S("svg", { width: W, height: Hh, viewBox: "0 0 " + W + " " + Hh, class: "fv-svg", role: "img", "aria-label": o.aria || "" }, el);
  unitDraw(svg, unit);
  yAxis(svg, o, ticks, tf, ml, mt, pw, ph, Y);
  if (o.ref && o.ref.value >= lo && o.ref.value <= hi) S("line", { x1: ml, x2: ml + pw, y1: Y(o.ref.value), y2: Y(o.ref.value), class: "fv-ref" }, svg);
  xAxis(svg, labels, X, mt, ph, pw, "point");
  series.forEach(s => {
    let d = "", pen = false;
    s.values.forEach((v, i) => { if (!ok(v)) { pen = false; return; } d += (pen ? "L" : "M") + X(i).toFixed(1) + "," + Y(v).toFixed(1); pen = true; });
    S("path", { d, fill: "none", stroke: s.color, "stroke-width": 2, "stroke-linejoin": "round", "stroke-linecap": "round" }, svg);
    if (n <= 12) s.values.forEach((v, i) => { if (ok(v)) S("circle", { cx: X(i), cy: Y(v), r: 3.2, fill: s.color, stroke: C.surface, "stroke-width": 1.6 }, svg); });
  });
  if (endItems.length) {
    endItems.forEach(e => { e.x = X(e.i); e.y = Y(e.s.values[e.i]); });
    endItems.sort((a, b) => a.y - b.y);
    const ys = endItems.map(e => e.y);
    for (let k = 1; k < ys.length; k++) ys[k] = Math.max(ys[k], ys[k - 1] + 15);
    endItems.forEach((e, k) => {
      S("circle", { cx: e.x, cy: e.y, r: 3.8, fill: e.s.color, stroke: C.surface, "stroke-width": 2 }, svg);
      const txt = e.text.length > 26 ? e.text.slice(0, 25) + "…" : e.text;
      T(svg, e.x + 10, ys[k] + 4, txt, "fv-lab");
    });
  }
  const cross = S("line", { class: "fv-cross", y1: mt, y2: mt + ph, visibility: "hidden" }, svg);
  const hd = series.map(s => S("circle", { r: 4.5, fill: s.color, stroke: C.surface, "stroke-width": 2, visibility: "hidden" }, svg));
  const hit = S("rect", { x: ml - half, y: mt, width: pw + 2 * half, height: ph, fill: "transparent" }, svg);
  let cur = -1;
  const idxAt = px => clamp(Math.round((px - ml) / pw * (n - 1)), 0, n - 1);
  function show(i, evt) {
    cur = i;
    const x = X(i);
    cross.setAttribute("x1", x); cross.setAttribute("x2", x); cross.setAttribute("visibility", "visible");
    const rows = [];
    series.forEach((s, k) => {
      const v = s.values[i];
      if (!ok(v)) { hd[k].setAttribute("visibility", "hidden"); return; }
      hd[k].setAttribute("cx", x); hd[k].setAttribute("cy", Y(v)); hd[k].setAttribute("visibility", "visible");
      rows.push({ color: s.color, kind: "line", label: s.name, value: fmt(v) });
    });
    let cx, cy;
    if (evt) { cx = evt.clientX; cy = evt.clientY; } else { const r = svg.getBoundingClientRect(); cx = r.left + x; cy = r.top + mt + 8; }
    tipShow(cx, cy, labels[i], rows, null);
  }
  function hide() { cur = -1; cross.setAttribute("visibility", "hidden"); hd.forEach(x => x.setAttribute("visibility", "hidden")); tipHide(); }
  const move = e => { const r = svg.getBoundingClientRect(); show(idxAt(e.clientX - r.left), e); };
  hit.addEventListener("pointermove", move); hit.addEventListener("pointerdown", move); hit.addEventListener("pointerleave", hide);
  keyboard(svg, n, show, hide, () => cur);
  return {};
}

/* ------------------------------------------------------------------ BARS */
export function barChart(el, o) {
  el.replaceChildren();
  const W = Math.max(240, el.clientWidth || 600), Hh = o.height || 280;
  const labels = o.labels, n = labels.length, series = o.series;
  let lo = 0, hi = 0;
  for (let i = 0; i < n; i++) {
    if (o.stacked) { let p = 0, q = 0; series.forEach(s => { const v = s.values[i]; if (ok(v)) { if (v > 0) p += v; else q += v; } }); hi = Math.max(hi, p); lo = Math.min(lo, q); }
    else series.forEach(s => { const v = s.values[i]; if (ok(v)) { hi = Math.max(hi, v); lo = Math.min(lo, v); } });
  }
  if (o.yMax !== undefined) hi = o.yMax;
  if (o.yMin !== undefined) lo = o.yMin;
  if (hi === lo) hi = lo + 1;
  const ticks = niceTicks(lo, hi, Hh < 220 ? 4 : 5);
  lo = ticks[0]; hi = ticks[ticks.length - 1];
  const fmt = o.fmt || f.int;
  const ax = axisFmt(o.tickKind || "num", ticks);
  const tf = ax.f, unit = o.unit !== undefined ? o.unit : ax.unit;
  const ml = Math.max(...ticks.map(t => measure(tf(t)))) + 14;
  const mr = 12, mt = unit ? 20 : 10;
  const pw = Math.max(40, W - ml - mr);
  const wrapped = xWrap(labels, pw);
  const mb = 26 + (wrapped ? (Math.max(...wrapped.map(l => l.length)) - 1) * 12 : 0);
  const ph = Hh - mt - mb, step = pw / n;
  const X = i => ml + (i + 0.5) * step;
  const Y = v => mt + ph - (v - lo) / (hi - lo) * ph;
  const k = o.stacked ? 1 : Math.max(1, series.length);
  const maxBar = o.maxBar || 30;
  const groupW = o.stacked ? Math.min(maxBar, step * 0.72) : Math.min(maxBar * k + 2 * (k - 1), step * 0.82);
  const barW = o.stacked ? groupW : Math.max(1, (groupW - 2 * (k - 1)) / k);
  const svg = S("svg", { width: W, height: Hh, viewBox: "0 0 " + W + " " + Hh, class: "fv-svg", role: "img" }, el);
  unitDraw(svg, unit);
  yAxis(svg, o, ticks, tf, ml, mt, pw, ph, Y);
  xAxis(svg, labels, X, mt, ph, pw, "band", wrapped);
  const wash = S("rect", { class: "fv-hband", y: mt, height: ph, width: step, visibility: "hidden" }, svg);
  const g = S("g", null, svg);
  for (let i = 0; i < n; i++) {
    if (o.stacked) {
      const pos = []; let up = 0;
      series.forEach(s => { const v = s.values[i]; if (!ok(v) || v <= 0) return; pos.push({ a: up, b: up + v, col: s.color }); up += v; });
      const x = X(i) - groupW / 2;
      pos.forEach((sg2, j) => { let top = Y(sg2.b), bot = Y(sg2.a); if (j < pos.length - 1) top += 1; if (j > 0) bot -= 1; if (bot - top < 0.6) return; S("path", { d: roundedBar(x, groupW, top, bot, j === pos.length - 1, false), fill: sg2.col }, g); });
    } else {
      series.forEach((s, j) => {
        const v = s.values[i];
        if (!ok(v) || v === 0) return;
        const x = X(i) - groupW / 2 + j * (barW + 2);
        const y0 = Y(0), y1 = Y(v);
        S("path", { d: v > 0 ? roundedBar(x, barW, y1, y0, true, false) : roundedBar(x, barW, y0, y1, false, true), fill: s.colors ? s.colors[i] : s.color }, g);
      });
    }
  }
  let cur = -1;
  function show(i, evt) {
    cur = i;
    wash.setAttribute("x", ml + i * step); wash.setAttribute("visibility", "visible");
    const rows = [];
    series.forEach(s => { const v = s.values[i]; if (ok(v)) rows.push({ color: s.color, kind: "rect", label: s.name, value: fmt(v) }); });
    if (o.stacked && series.length > 1) rows.push({ kind: "none", label: "Total", value: fmt(sum(series.map(s => s.values[i]))) });
    let cx, cy;
    if (evt) { cx = evt.clientX; cy = evt.clientY; } else { const r = svg.getBoundingClientRect(); cx = r.left + X(i); cy = r.top + mt + 8; }
    tipShow(cx, cy, labels[i], rows, null);
  }
  function hide() { cur = -1; wash.setAttribute("visibility", "hidden"); tipHide(); }
  const hit = S("rect", { x: ml, y: mt, width: pw, height: ph, fill: "transparent" }, svg);
  const move = e => { const r = svg.getBoundingClientRect(); show(clamp(Math.floor((e.clientX - r.left - ml) / step), 0, n - 1), e); };
  hit.addEventListener("pointermove", move); hit.addEventListener("pointerdown", move); hit.addEventListener("pointerleave", hide);
  keyboard(svg, n, show, hide, () => cur);
  return {};
}

/* ------------------------------------------------------------------ WATERFALL */
export function waterfall(el, o) {
  el.replaceChildren();
  const W = Math.max(260, el.clientWidth || 600), Hh = o.height || 290;
  const steps = o.steps, n = steps.length;
  let run = 0;
  const bars = steps.map(s => { if (s.kind === "total") { run = s.value; return { a: null, b: s.value, s }; } const a = run; run += s.value; return { a, b: run, s }; });
  const levels = bars.map(b => b.b).concat(bars.filter(b => b.a !== null).map(b => b.a));
  let lo = Math.min(0, ...levels);
  const hi = Math.max(...levels);
  const ticks = niceTicks(lo, hi, 5);
  lo = ticks[0];
  const top = ticks[ticks.length - 1];
  const ax = axisFmt(o.kind || "cop", ticks);
  const lab = v => num(Math.abs(v) / ax.div, ax.div > 1 ? 1 : 0);
  const ml = Math.max(...ticks.map(t => measure(ax.f(t)))) + 16;
  const mt = 30, mb = 34, mr = 10;
  const pw = W - ml - mr, ph = Hh - mt - mb, step = pw / n;
  const X = i => ml + (i + 0.5) * step;
  const Y = v => mt + ph - (v - lo) / (top - lo) * ph;
  const bw = Math.min(58, step * 0.56);
  const useShort = steps.some(s => String(s.label).split("\n").some(l => measure(l) > step - 4));
  const svg = S("svg", { width: W, height: Hh, viewBox: "0 0 " + W + " " + Hh, class: "fv-svg", role: "img" }, el);
  unitDraw(svg, ax.unit);
  ticks.forEach(t => { S("line", { x1: ml, x2: ml + pw, y1: Y(t), y2: Y(t), class: t === lo ? "fv-base" : "fv-grid" }, svg); T(svg, ml - 8, Y(t) + 3.5, ax.f(t), "fv-tick", "end"); });
  const wash = S("rect", { class: "fv-hband", y: mt, height: ph, width: step, visibility: "hidden" }, svg);
  bars.forEach((b, i) => {
    const x = X(i) - bw / 2;
    let y0, y1, up;
    if (b.a === null) { y0 = Y(lo); y1 = Y(b.b); up = true; } else { up = b.b >= b.a; y0 = Y(up ? b.a : b.b); y1 = Y(up ? b.b : b.a); }
    const topY = Math.min(y0, y1), botY = Math.max(y0, y1);
    S("path", { d: b.a === null ? roundedBar(x, bw, topY, botY, true, false) : roundedBar(x, bw, topY, botY, up, !up), fill: b.s.color || C.s1 }, svg);
    T(svg, X(i), b.a === null || up ? topY - 7 : botY + 14, b.a === null ? lab(b.b) : (b.s.value >= 0 ? "+" : MINUS) + lab(b.s.value), "fv-lab b", "middle");
    String(useShort && b.s.short ? b.s.short : b.s.label).split("\n").forEach((l, j) => T(svg, X(i), mt + ph + 16 + j * 12, l, "fv-tick" + (j === 0 ? " strong" : ""), "middle"));
    if (i < n - 1) S("line", { x1: X(i) + bw / 2, x2: X(i + 1) - bw / 2, y1: Y(b.b), y2: Y(b.b), class: "fv-leader" }, svg);
  });
  let cur = -1;
  function show(i, evt) {
    cur = i;
    wash.setAttribute("x", ml + i * step); wash.setAttribute("visibility", "visible");
    const b = bars[i];
    const rows = [{ color: b.s.color, kind: "rect", label: String(b.s.label).replace("\n", " "), value: b.a === null ? f.copFull(b.b) : (b.s.value >= 0 ? "+" : MINUS) + f.copFull(Math.abs(b.s.value)) }];
    if (b.a !== null) rows.push({ kind: "none", label: "nivel acumulado", value: f.cop(b.b) });
    let cx, cy;
    if (evt) { cx = evt.clientX; cy = evt.clientY; } else { const r = svg.getBoundingClientRect(); cx = r.left + X(i); cy = r.top + mt; }
    tipShow(cx, cy, o.title || "Puente", rows, null);
  }
  function hide() { cur = -1; wash.setAttribute("visibility", "hidden"); tipHide(); }
  const hit = S("rect", { x: ml, y: mt, width: pw, height: ph, fill: "transparent" }, svg);
  const move = e => { const r = svg.getBoundingClientRect(); show(clamp(Math.floor((e.clientX - r.left - ml) / step), 0, n - 1), e); };
  hit.addEventListener("pointermove", move); hit.addEventListener("pointerdown", move); hit.addEventListener("pointerleave", hide);
  keyboard(svg, n, show, hide, () => cur);
  return {};
}

/* ------------------------------------------------------------------ SCATTER / BUBBLES */
export function scatter(el, o) {
  el.replaceChildren();
  const W = Math.max(260, el.clientWidth || 600), Hh = o.height || 320;
  const pts = o.points.filter(p => ok(p.x) && ok(p.y));
  if (!pts.length) { el.textContent = "Sin puntos para dibujar."; return {}; }
  const xs = pts.map(p => p.x), ys = pts.map(p => p.y);
  const bub = !!o.bubbles && pts.some(p => ok(p.size));
  const smax = bub ? Math.max(...pts.map(p => (ok(p.size) ? p.size : 0))) || 1 : 1;
  const rad = p => (bub ? 7 + Math.sqrt(Math.max(0, p.size || 0) / smax) * 21 : 5.2);
  const spanX = Math.max(...xs) - Math.min(...xs), spanY = Math.max(...ys) - Math.min(...ys);
  const padX = spanX * (bub ? 0.16 : 0.06) || Math.abs(xs[0] || 1) * 0.1 || 1, padY = spanY * (bub ? 0.22 : 0.08) || Math.abs(ys[0] || 1) * 0.1 || 1;
  const xt = niceTicks(Math.min(...xs) - padX, Math.max(...xs) + padX, 5), yt = niceTicks(Math.min(...ys) - padY, Math.max(...ys) + padY, 5);
  const xa = axisFmt(o.xKind || "num", xt), ya = axisFmt(o.yKind || "num", yt);
  const ml = Math.max(...yt.map(t => measure(ya.f(t)))) + 16, mt = 18, mb = 44, mr = 14;
  const pw = W - ml - mr, ph = Hh - mt - mb;
  const X = v => ml + (v - xt[0]) / (xt[xt.length - 1] - xt[0]) * pw;
  const Y = v => mt + ph - (v - yt[0]) / (yt[yt.length - 1] - yt[0]) * ph;
  const svg = S("svg", { width: W, height: Hh, viewBox: "0 0 " + W + " " + Hh, class: "fv-svg", role: "img" }, el);
  yt.forEach(t => { S("line", { x1: ml, x2: ml + pw, y1: Y(t), y2: Y(t), class: t === 0 ? "fv-base" : "fv-grid" }, svg); T(svg, ml - 8, Y(t) + 3.5, ya.f(t), "fv-tick", "end"); });
  xt.forEach(t => { S("line", { x1: X(t), x2: X(t), y1: mt, y2: mt + ph, class: t === 0 ? "fv-base" : "fv-grid" }, svg); T(svg, X(t), mt + ph + 16, xa.f(t), "fv-tick", "middle"); });
  if (o.xTitle) T(svg, ml + pw / 2, Hh - 6, o.xTitle + (xa.unit ? " · " + xa.unit : ""), "fv-axis-title", "middle");
  if (o.yTitle) T(svg, 0, 11, o.yTitle + (ya.unit ? " · " + ya.unit : ""), "fv-axis-title", "start");
  pts.map((p, i) => i).sort((a, b) => rad(pts[b]) - rad(pts[a])).forEach(i => {
    const p = pts[i];
    S("circle", { cx: X(p.x), cy: Y(p.y), r: rad(p), fill: p.color || o.color || C.s1, "fill-opacity": bub ? 0.55 : 0.85, stroke: C.surface, "stroke-width": 2 }, svg);
  });
  if (o.labels) pts.forEach(p => T(svg, X(p.x), Y(p.y) - rad(p) - 5, p.label, "fv-lab", "middle"));
  const ring = S("circle", { r: 9, fill: "none", stroke: C.ink, "stroke-width": 1.4, visibility: "hidden" }, svg);
  let cur = -1;
  function show(i, evt) {
    cur = i;
    const p = pts[i];
    ring.setAttribute("cx", X(p.x)); ring.setAttribute("cy", Y(p.y)); ring.setAttribute("r", rad(p) + 3.5); ring.setAttribute("visibility", "visible");
    let cx, cy;
    if (evt) { cx = evt.clientX; cy = evt.clientY; } else { const r = svg.getBoundingClientRect(); cx = r.left + X(p.x); cy = r.top + Y(p.y); }
    tipShow(cx, cy, p.label, [{ color: o.color || C.s1, kind: "dot", label: o.xName || "x", value: (o.xFmt || f.num)(p.x) }, { kind: "none", label: o.yName || "y", value: (o.yFmt || f.num)(p.y) }]
      .concat(bub ? [{ kind: "none", label: o.sizeName || "tamaño", value: (o.sizeFmt || f.num)(p.size) }] : []), null);
  }
  function hide() { cur = -1; ring.setAttribute("visibility", "hidden"); tipHide(); }
  const hit = S("rect", { x: ml, y: mt, width: pw, height: ph, fill: "transparent" }, svg);
  hit.addEventListener("pointermove", e => {
    const r = svg.getBoundingClientRect(), px = e.clientX - r.left, py = e.clientY - r.top;
    let best = -1, bd = Infinity;
    pts.forEach((p, i) => { const d = (X(p.x) - px) ** 2 + (Y(p.y) - py) ** 2; if (d < Math.max(32, rad(p) + 6) ** 2 && d < bd) { bd = d; best = i; } });
    if (best >= 0) show(best, e); else hide();
  });
  hit.addEventListener("pointerleave", hide);
  keyboard(svg, pts.length, show, hide, () => cur);
  return {};
}

/* ------------------------------------------------------------------ DOTS (dumbbell) */
export function dots(el, o) {
  el.replaceChildren();
  const W = Math.max(260, el.clientWidth || 600);
  const rows = o.rows, rh = o.rowH || 34;
  const labW = Math.min(260, Math.max(...rows.map(r => measure(r, SANS))) + 16);
  const mt = 8, mb = 40, mr = 14, Hh = mt + rows.length * rh + mb;
  let vals = [];
  o.series.forEach(s => s.values.forEach(v => { if (ok(v)) vals.push(v); }));
  const ticks = niceTicks(Math.min(0, ...vals), Math.max(...vals), 5);
  const ax = axisFmt(o.tickKind || "cop", ticks);
  const pw = W - labW - mr;
  const X = v => labW + (v - ticks[0]) / (ticks[ticks.length - 1] - ticks[0]) * pw;
  const svg = S("svg", { width: W, height: Hh, viewBox: "0 0 " + W + " " + Hh, class: "fv-svg", role: "img" }, el);
  ticks.forEach(t => { S("line", { x1: X(t), x2: X(t), y1: mt, y2: mt + rows.length * rh, class: t === 0 ? "fv-base" : "fv-grid" }, svg); T(svg, X(t), mt + rows.length * rh + 17, ax.f(t), "fv-tick", "middle"); });
  if (ax.unit) T(svg, labW + pw, mt + rows.length * rh + 33, ax.unit, "fv-unit", "end");
  if (o.ref !== undefined && o.ref >= ticks[0] && o.ref <= ticks[ticks.length - 1]) S("line", { x1: X(o.ref), x2: X(o.ref), y1: mt, y2: mt + rows.length * rh, class: "fv-ref" }, svg);
  const hits = [];
  rows.forEach((r, i) => {
    const y = mt + i * rh + rh / 2;
    const txt = measure(r, SANS) > labW - 14 ? r.slice(0, Math.floor(r.length * (labW - 20) / measure(r, SANS))) + "…" : r;
    T(svg, labW - 12, y + 4, txt, "fv-lab", "end");
    const vs = o.series.map(s => s.values[i]).filter(ok);
    if (vs.length > 1) S("line", { x1: X(Math.min(...vs)), x2: X(Math.max(...vs)), y1: y, y2: y, stroke: C.de, "stroke-width": 2.5, "stroke-linecap": "round" }, svg);
    o.series.forEach((s, k) => { const v = s.values[i]; if (!ok(v)) return; S("circle", { cx: X(v), cy: y, r: 6, fill: s.color, stroke: C.surface, "stroke-width": 2 }, svg); hits.push({ i, k, x: X(v), y, v }); });
  });
  const ring = S("circle", { r: 10, fill: "none", stroke: C.ink, "stroke-width": 1.4, visibility: "hidden" }, svg);
  const hit = S("rect", { x: labW, y: mt, width: pw, height: rows.length * rh, fill: "transparent" }, svg);
  hit.addEventListener("pointermove", e => {
    const r = svg.getBoundingClientRect(), px = e.clientX - r.left, py = e.clientY - r.top;
    let best = null, bd = 900;
    hits.forEach(hh => { const d = (hh.x - px) ** 2 + (hh.y - py) ** 2; if (d < bd) { bd = d; best = hh; } });
    if (!best) { ring.setAttribute("visibility", "hidden"); tipHide(); return; }
    ring.setAttribute("cx", best.x); ring.setAttribute("cy", best.y); ring.setAttribute("visibility", "visible");
    tipShow(e.clientX, e.clientY, rows[best.i], o.series.map(s => ({ color: s.color, kind: "dot", label: s.name, value: (o.fmt || f.cop)(s.values[best.i]) })), null);
  });
  hit.addEventListener("pointerleave", () => { ring.setAttribute("visibility", "hidden"); tipHide(); });
  return {};
}

/* ------------------------------------------------------------------ legend + table */
export function legend(target, items) {
  target.replaceChildren();
  if (items.length < 2) return;
  items.forEach(it => { const b = H("button", null, target); b.type = "button"; b.disabled = true; const sw = H("span", "sw " + (it.kind || "rect"), b); sw.style.background = it.color; b.append(it.name); });
}
export function table(container, cols, rows) {
  container.replaceChildren();
  const t = H("table", "tbl", container);
  const tr = H("tr", null, H("thead", null, t));
  cols.forEach(c => H("th", c.num ? "n" : null, tr, c.label));
  const tb = H("tbody", null, t);
  rows.forEach(r => { const row = H("tr", null, tb); cols.forEach(c => { const v = r[c.key]; H("td", c.num ? "n" : null, row, c.fmt ? c.fmt(v, r) : (v === null || v === undefined || v === "" ? "–" : v)); }); });
  return t;
}

/* ------------------------------------------------------------------ workspace visual grammar → chart */
const VFMT = { int: f.int, cop: f.cop, cop2: f.cop2, pct: v => f.pct(v), pct0: v => f.pct(v, 0), pct2: v => f.pct(v, 2), pct_signed: v => f.pctSigned(v),
  num1: v => f.num(v, 1), num2: v => f.num(v, 2), x: f.x, idx: f.idx };
export const vfmt = (v, k) => (v === null || v === undefined ? "–" : typeof v === "string" ? v : (VFMT[k] || (x => f.num(x, 2)))(v));
const VKIND = { cop: "cop", cop2: "cop", pct: "pct", pct0: "pct", pct2: "pct", pct_signed: "pct", int: "int", idx: "idx", num1: "num", num2: "num" };

export function renderVisual(el, spec, legendEl) {
  const fmt = v => vfmt(v, spec.formato), kind = VKIND[spec.formato] || "num";
  const P = PAL();
  const series = (spec.series || []).map((s, i) => ({ name: s.nombre, values: s.valores, color: P[i % P.length] }));
  if (legendEl) legend(legendEl, series.map(s => ({ name: s.name, color: s.color, kind: spec.tipo === "linea" ? "line" : spec.tipo === "puntos" ? "dot" : "rect" })));
  if (spec.tipo === "linea") return lineChart(el, { labels: spec.x, series, fmt, tickKind: kind, height: 260, includeZero: spec.formato !== "idx" });
  if (spec.tipo === "barras") return barChart(el, { labels: spec.x, series, stacked: !!spec.apiladas, fmt, tickKind: kind, height: 260, maxBar: 34, yMax: spec.apiladas && spec.formato === "pct" ? 1 : undefined });
  if (spec.tipo === "cascada") { let k = 0; return waterfall(el, { height: 280, title: "Descomposición", steps: spec.pasos.map(p => ({ label: p.etiqueta, short: p.corta, value: p.valor, kind: p.tipo === "total" ? "total" : "delta", color: p.tipo === "total" ? C.de : [C.s2, C.s1, C.s3][k++ % 3] })) }); }
  if (spec.tipo === "puntos") return dots(el, { rows: spec.filas, fmt, tickKind: kind, ref: spec.referencia, series: spec.series.map((s, i) => ({ name: s.nombre, values: s.valores, color: spec.referencia !== undefined ? [C.de, C.s1, C.de][i] || P[i] : P[i % P.length] })) });
  if (spec.tipo === "dispersion") {
    const ex = spec.ejes || {};
    return scatter(el, { points: spec.puntos.map(p => ({ x: p.x, y: p.y, size: p.tam, label: p.etiqueta })), bubbles: !!ex.tamano, labels: true,
      xFmt: v => vfmt(v, ex.x && ex.x.formato), yFmt: v => vfmt(v, ex.y && ex.y.formato), sizeFmt: ex.tamano ? v => vfmt(v, ex.tamano.formato) : null,
      xKind: VKIND[ex.x && ex.x.formato] || "num", yKind: VKIND[ex.y && ex.y.formato] || "num", xName: ex.x && ex.x.nombre, yName: ex.y && ex.y.nombre,
      sizeName: ex.tamano && ex.tamano.nombre, xTitle: ex.x && ex.x.nombre, yTitle: ex.y && ex.y.nombre, color: C.s1, height: 340 });
  }
  if (spec.tipo === "kpi") { el.replaceChildren(); const d = H("div", "stat", el); H("div", "k", d, spec.etiqueta); H("div", "v", d, fmt(spec.valor)); return {}; }
  if (spec.tipo === "tabla") { el.replaceChildren(); const w = H("div", "tablewrap", el); table(w, (spec.columnas || []).filter(c => c.id !== "_clave").map(c => ({ key: c.id, label: c.nombre, num: !!c.formato && c.formato !== "texto", fmt: v => (typeof v === "string" ? v : vfmt(v, c.formato || "num2")) })), (spec.filas || []).slice(0, 40)); return {}; }
  if (spec.tipo === "datos") { el.replaceChildren(); const box = H("div", "datagap", el); (spec.filas || []).forEach(r => { const okRow = r.estado !== "No existe"; const row = H("div", "dg " + (okRow ? "ok" : "no"), box); H("span", null, row, okRow ? "✓" : "✕"); H("span", null, row, r.dato); H("span", "cf", row, okRow ? r.estado : r.campos); }); return {}; }
  el.textContent = "Visualización no disponible en CaseOS (ábrela en el workspace).";
  return {};
}

/* evidence table (CaseOS EvidenceTable) → best chart for its preferred_visual; falls back to a table */
export function renderEvidenceTable(el, t, legendEl) {
  const cols = t.columns || [], rows = t.rows || [];
  const numericCols = cols.map((c, j) => rows.length && rows.every(r => typeof r[j] === "number" || r[j] === null)).map((v, j) => v ? j : -1).filter(j => j > 0);
  const labels = rows.map(r => String(r[0]));
  const unitOf = c => { const u = t.units && typeof t.units === "object" ? t.units[c] : t.units; return String(u || "").toLowerCase(); };
  const kindOf = c => { const u = unitOf(c); return u.includes("cop") ? "cop" : u.includes("percent") || u.includes("%") ? "num" : u.includes("client") ? "int" : "num"; };
  const fmtOf = c => { const k = kindOf(c); return k === "cop" ? f.cop : k === "int" ? f.int : (v => f.num(v, unitOf(c).includes("percent") ? 2 : 1) + (unitOf(c).includes("percent") ? "%" : "")); };
  const P = PAL();
  const pv = t.preferred_visual;
  if (!numericCols.length || pv === "table") {
    el.replaceChildren();
    const w = H("div", "tablewrap", el);
    table(w, cols.map((c, j) => ({ key: "c" + j, label: c, num: numericCols.includes(j) })), rows.map(r => Object.fromEntries(r.map((v, j) => ["c" + j, typeof v === "number" ? fmtOf(cols[j])(v) : v]))));
    return {};
  }
  if (pv === "waterfall" && rows.length && cols.length > 3) {
    const r0 = rows[rows.length - 1];
    const steps = cols.slice(1).map((c, j) => ({ label: c.replace(/_cop$/, "").replace(/_/g, " "), value: r0[j + 1], kind: /opening|closing/.test(c) ? "total" : "delta" }));
    const color = s => s.kind === "total" ? C.de : s.value >= 0 ? C.s1 : C.s2;
    return waterfall(el, { steps: steps.map(s => ({ ...s, color: color(s) })), height: 290, title: `${t.table_key} · ${labels[labels.length - 1]}` });
  }
  const pick = numericCols.slice(0, 3);
  const scales = pick.map(j => Math.max(...rows.map(r => Math.abs(r[j] || 0))));
  const same = scales.every(s => s / Math.max(...scales) > 0.05) && pick.every(j => kindOf(cols[j]) === kindOf(cols[pick[0]]));
  const use = same ? pick : [pick[pick.length - 1]];
  const series = use.map((j, i) => ({ name: cols[j].replace(/_/g, " "), values: rows.map(r => r[j]), color: P[i] }));
  if (legendEl) legend(legendEl, series.map(s => ({ name: s.name, color: s.color, kind: "line" })));
  const kind = kindOf(cols[use[0]]);
  if (pv === "bar" || pv === "stacked_bar" || rows.length <= 6) return barChart(el, { labels, series, fmt: fmtOf(cols[use[0]]), tickKind: kind === "int" ? "int" : kind, height: 250 });
  return lineChart(el, { labels, series, fmt: fmtOf(cols[use[0]]), tickKind: kind === "int" ? "int" : kind, height: 250 });
}
