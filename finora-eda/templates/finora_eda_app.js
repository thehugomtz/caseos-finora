/* Finora EDA workspace · zero-dependency SVG charts + section renderers.
   Data arrives in the global DATA object written by finora_eda.py. */
(function () {
"use strict";

const D = DATA;
const M = D.monthly;
const LAB = D.meta.labels;
const YM = D.meta.months;
const N = LAB.length;
const CS = D.meta.cleanStart;
const U = D.meta.spendUnit;
const FACT = D.facts;

/* ------------------------------------------------------------------ colours */
const css = getComputedStyle(document.documentElement);
const cv = n => css.getPropertyValue(n).trim();
const C = {
  s1: cv("--s1"), s2: cv("--s2"), s3: cv("--s3"), s4: cv("--s4"), s5: cv("--s5"), s6: cv("--s6"), s7: cv("--s7"), s8: cv("--s8"),
  ink: cv("--ink"), ink2: cv("--ink-2"), muted: cv("--muted"), de: cv("--de"), surface: "#ffffff",
  r150: cv("--r150"), r250: cv("--r250"), r300: cv("--r300"), r400: cv("--r400"), r500: cv("--r500"),
  r550: cv("--r550"), r650: cv("--r650"), r700: cv("--r700"),
};
const IND = D.industry.order;
const INDC = {};
IND.forEach((k, i) => { INDC[k] = [C.s1, C.s2, C.s3, C.s4, C.s5, C.s6][i]; });
const MOV = { New: C.s1, Expansion: C.s7, Reactivation: C.s3, Contraction: C.s4, Churn: C.s8 };
const YEARC = { 2022: C.r300, 2023: C.r500, 2024: C.r700 };
const SEQ = ["#f1f6fd", "#dce9fb", "#c3daf8", "#a6c8f4", "#86b6ef", "#62a0ea", "#3f89e2", "#2a78d6", "#2265bb", "#1b529c", "#15427f", "#0d366b"];
const RED = ["#f7eceb", "#f6d6d3", "#f1b6b0", "#ea918a", "#e26b64", "#d24a45", "#b33533", "#8e2826"];
const MID = "#eeede9";

/* ------------------------------------------------------------------ format */
const nf0 = new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 });
const MINUS = "−";
const ok = v => v !== null && v !== undefined && isFinite(v);
function compact(v, d) {
  const a = Math.abs(v), s = v < 0 ? MINUS : "";
  if (d === undefined) d = 1;
  if (a >= 1e9) return s + (a / 1e9).toFixed(d) + "B";
  if (a >= 1e6) return s + (a / 1e6).toFixed(d) + "M";
  if (a >= 1e3) return s + (a / 1e3).toFixed(d) + "K";
  return s + a.toFixed(0);
}
const f = {
  cop: v => ok(v) ? (v < 0 ? MINUS : "") + "COP " + compact(Math.abs(v)) : "–",
  cop2: v => ok(v) ? (v < 0 ? MINUS : "") + "COP " + compact(Math.abs(v), 2) : "–",
  copFull: v => ok(v) ? (v < 0 ? MINUS : "") + "COP " + nf0.format(Math.abs(v)) : "–",
  copSigned: v => ok(v) ? (v < 0 ? MINUS : "+") + "COP " + compact(Math.abs(v)) : "–",
  int: v => ok(v) ? (v < 0 ? MINUS : "") + nf0.format(Math.abs(Math.round(v))) : "–",
  pct: (v, d) => ok(v) ? (v < 0 ? MINUS : "") + (Math.abs(v) * 100).toFixed(d === undefined ? 1 : d) + "%" : "–",
  pct0: v => f.pct(v, 0),
  pctSigned: v => ok(v) ? (v < 0 ? MINUS : "+") + (Math.abs(v) * 100).toFixed(0) + "%" : "–",
  u: (v, d) => ok(v) ? (v < 0 ? MINUS : "") + Math.abs(v).toFixed(d === undefined ? 3 : d) + " " + U : "–",
  u2: v => f.u(v, 2),
  idx: v => ok(v) ? v.toFixed(0) : "–",
  r: v => ok(v) ? (v < 0 ? MINUS : "+") + Math.abs(v).toFixed(2) : "–",
  p: v => ok(v) ? (v < 0.001 ? "<0.001" : v.toFixed(3)) : "–",
  z: v => ok(v) ? (v < 0 ? MINUS : "+") + Math.abs(v).toFixed(2) : "–",
  num: (v, d) => ok(v) ? (v < 0 ? MINUS : "") + Math.abs(v).toFixed(d === undefined ? 2 : d) : "–",
  x: v => ok(v) ? v.toFixed(1) + "×" : "–",
};
function tickFormatter(kind, ticks) {
  const step = ticks.length > 1 ? Math.abs(ticks[1] - ticks[0]) : 1;
  const maxAbs = Math.max(...ticks.map(Math.abs));
  if (kind === "pct") {
    const d = Math.max(0, Math.min(2, -Math.floor(Math.log10(step * 100) + 1e-9)));
    return v => (v < 0 ? MINUS : "") + (Math.abs(v) * 100).toFixed(d) + "%";
  }
  if (kind === "cop" || kind === "int" || kind === "num" && maxAbs >= 1000) {
    const unit = maxAbs >= 1e9 ? 1e9 : maxAbs >= 1e6 ? 1e6 : maxAbs >= 1e3 ? 1e3 : 1;
    const suf = unit === 1e9 ? "B" : unit === 1e6 ? "M" : unit === 1e3 ? "K" : "";
    const d = unit === 1 ? 0 : Math.max(0, Math.min(2, -Math.floor(Math.log10(step / unit) + 1e-9)));
    if (kind === "int" && unit === 1) return v => (v < 0 ? MINUS : "") + nf0.format(Math.abs(v));
    return v => v === 0 ? "0" : (v < 0 ? MINUS : "") + (Math.abs(v) / unit).toFixed(d) + suf;
  }
  if (kind === "u" || kind === "num" || kind === "z") {
    const d = Math.max(0, Math.min(3, -Math.floor(Math.log10(step) + 1e-9)));
    return v => (v < 0 ? MINUS : "") + Math.abs(v).toFixed(d);
  }
  return v => (v < 0 ? MINUS : "") + nf0.format(Math.abs(v));
}

/* ------------------------------------------------------------------ dom helpers */
const NS = "http://www.w3.org/2000/svg";
function S(tag, attrs, parent) {
  const e = document.createElementNS(NS, tag);
  if (attrs) for (const k in attrs) { const v = attrs[k]; if (v !== null && v !== undefined && v !== false) e.setAttribute(k, v); }
  if (parent) parent.appendChild(e);
  return e;
}
function T(parent, x, y, text, cls, anchor, extra) {
  const t = S("text", Object.assign({ x: x, y: y, class: cls, "text-anchor": anchor || "start" }, extra || {}), parent);
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
  return (s, font) => { c.font = font || '10.5px "JetBrains Mono", ui-monospace, monospace'; return c.measureText(String(s)).width; };
})();
const SANS = '12px Inter, system-ui, sans-serif';
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const range = (a, b) => Array.from({ length: b - a }, (_, i) => a + i);
const monthIdx = ym => YM.indexOf(ym);
const mlab = ym => { const i = monthIdx(ym); return i >= 0 ? LAB[i] : ym; };
const sum = a => a.reduce((s, v) => s + (ok(v) ? v : 0), 0);

/* ------------------------------------------------------------------ scales */
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
const MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const isMonth = l => /^[A-Z][a-z]{2}-\d{2}$/.test(l);
function xTickList(labels, pw, mode) {
  const n = labels.length;
  if (!labels.length) return [];
  if (!labels.every(isMonth)) {
    const maxW = Math.max(...labels.map(l => measure(l))) + 10;
    const per = pw / n;
    let every = 1;
    while (per * every < maxW && every < n) every++;
    return labels.map((l, i) => (i % every === 0 ? { i: i, text: l } : null)).filter(Boolean);
  }
  const per = pw / Math.max(1, mode === "band" ? n : n - 1);
  const every = per >= 19 ? 3 : per >= 9.5 ? 6 : 12;
  const out = [];
  labels.forEach((l, i) => {
    const m = MON.indexOf(l.slice(0, 3));
    if (m % every === 0) out.push({ i: i, text: m === 0 ? l : l.slice(0, 3), strong: m === 0 });
  });
  return out;
}

/* ------------------------------------------------------------------ tooltip */
const tip = H("div", "fv-tip", document.body);
tip.setAttribute("role", "status");
tip.setAttribute("aria-live", "polite");
function tipShow(x, y, title, rows, note) {
  tip.replaceChildren();
  if (title) H("div", "fv-tip-title", tip, title);
  rows.forEach(r => {
    const row = H("div", "fv-tip-row", tip);
    const k = H("span", "fv-key " + (r.kind || "line"), row);
    if (r.color) k.style.background = r.color;
    if (r.wash) k.style.opacity = "0.35";
    H("span", "v", row, r.value);
    H("span", "l", row, r.label);
  });
  if (note) H("div", "fv-tip-note", tip, note);
  tip.classList.add("on");
  const pad = 14;
  const w = tip.offsetWidth, h = tip.offsetHeight;
  let left = x + pad, top = y + pad;
  if (left + w > window.innerWidth - 8) left = x - w - pad;
  if (top + h > window.innerHeight - 8) top = y - h - pad;
  tip.style.transform = "translate(" + Math.max(8, left) + "px," + Math.max(8, top) + "px)";
}
function tipHide() { tip.classList.remove("on"); }
window.addEventListener("scroll", tipHide, { passive: true });

/* ------------------------------------------------------------------ shared frame */
function yAxis(svg, o, ticks, fmt, ml, mt, pw, ph, Y) {
  ticks.forEach(t => {
    const y = Y(t);
    S("line", { x1: ml, x2: ml + pw, y1: y, y2: y, class: t === 0 ? "fv-base" : "fv-grid" }, svg);
    T(svg, ml - 8, y + 3.5, fmt(t), "fv-tick" + (o.ref && Math.abs(o.ref.value - t) < 1e-9 ? " strong" : ""), "end");
  });
}
function xAxis(svg, labels, X, mt, ph, pw, mode) {
  xTickList(labels, pw, mode).forEach(t => {
    T(svg, X(t.i), mt + ph + 17, t.text, "fv-tick" + (t.strong ? " strong" : ""), "middle");
  });
}
function shadesDraw(svg, shades, X, halfStep, mt, ph, mini) {
  (shades || []).forEach(sh => {
    const x0 = X(sh.from) - halfStep, x1 = X(sh.to) + halfStep;
    S("rect", { x: x0, y: mt, width: Math.max(0, x1 - x0), height: ph, class: "fv-shade" }, svg);
    if (sh.label && !mini) T(svg, x0 + 5, mt + 11, sh.label, "fv-shade-lab");
  });
}
function flagsDraw(svg, flags, X, mt, ph, mini) {
  (flags || []).forEach(fl => {
    const x = X(fl.i);
    S("line", { x1: x, x2: x, y1: mt, y2: mt + ph, class: "fv-flag" }, svg);
    if (fl.label && !mini) T(svg, x + 4, mt + 10, fl.label, "fv-flag-lab");
  });
}
function roundedBar(x, w, yTop, yBot, roundTop, roundBot) {
  const h = yBot - yTop;
  if (h <= 0) return "";
  const r = Math.min(4, w / 2, roundTop && roundBot ? h / 2 : h);
  const rt = roundTop ? r : 0, rb = roundBot ? r : 0;
  let d = "M" + x + "," + (yBot - rb);
  d += " L" + x + "," + (yTop + rt);
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
      const i = clamp(c < 0 ? (e.key === "ArrowRight" ? 0 : n - 1) : c + (e.key === "ArrowRight" ? 1 : -1), 0, n - 1);
      show(i, null);
    } else if (e.key === "Escape") hide();
  });
  svg.addEventListener("blur", hide);
}

/* ------------------------------------------------------------------ LINE */
function lineChart(el, o) {
  el.replaceChildren();
  const hidden = el._hidden || (el._hidden = new Set());
  const W = Math.max(240, el.clientWidth || 600);
  const Hh = o.height || 300;
  const mini = !!o.mini;
  const labels = o.labels;
  const n = labels.length;
  const mode = o.xMode || "point";
  const series = o.series.filter(s => !hidden.has(s.name));
  const bandOn = o.band && !hidden.has(o.band.name);
  let vals = [];
  series.forEach(s => s.values.forEach(v => { if (ok(v)) vals.push(v); }));
  if (bandOn) o.band.lower.concat(o.band.upper).forEach(v => { if (ok(v)) vals.push(v); });
  if (o.ref) vals.push(o.ref.value);
  if (!vals.length) vals = [0, 1];
  let lo = o.yMin !== undefined ? o.yMin : Math.min(...vals);
  let hi = o.yMax !== undefined ? o.yMax : Math.max(...vals);
  if (o.includeZero !== false && o.yMin === undefined) lo = Math.min(0, lo);
  const ticks = niceTicks(lo, hi, o.yTicks || (mini ? 3 : Hh < 220 ? 4 : 5));
  lo = ticks[0]; hi = ticks[ticks.length - 1];
  const fmt = o.fmt || f.int;
  const tf = o.tickFormat || tickFormatter(o.tickKind || "num", ticks);
  const ml = Math.max(...ticks.map(t => measure(tf(t)))) + 14;
  let endItems = [];
  const endFmt = o.endLabelFmt || (s => s.short || s.name);
  if (o.endLabels && !mini) {
    series.forEach(s => {
      let i = s.values.length - 1;
      while (i >= 0 && !ok(s.values[i])) i--;
      if (i >= 0) endItems.push({ s: s, i: i, text: endFmt(s, s.values[i]) });
    });
  }
  const mr = endItems.length ? Math.max(...endItems.map(e => measure(e.text, SANS))) + 26 : (mini ? 6 : 12);
  const mt = o.shades && o.shades.some(s => s.label) && !mini ? 20 : 10;
  const mb = 26;
  const pw = Math.max(40, W - ml - mr), ph = Hh - mt - mb;
  const X = mode === "band" ? (i => ml + (i + 0.5) * pw / n) : (i => ml + (n === 1 ? pw / 2 : i * pw / (n - 1)));
  const half = mode === "band" ? pw / n / 2 : (n > 1 ? pw / (n - 1) / 2 : pw / 2);
  const Y = v => mt + ph - (v - lo) / (hi - lo) * ph;
  const svg = S("svg", { width: W, height: Hh, viewBox: "0 0 " + W + " " + Hh, class: "fv-svg", role: "img", "aria-label": o.aria || "" }, el);
  shadesDraw(svg, o.shades, X, half, mt, ph, mini);
  yAxis(svg, o, ticks, tf, ml, mt, pw, ph, Y);
  if (o.ref && o.ref.value >= lo && o.ref.value <= hi) {
    S("line", { x1: ml, x2: ml + pw, y1: Y(o.ref.value), y2: Y(o.ref.value), class: "fv-ref" }, svg);
    if (o.ref.label && !mini) T(svg, ml + pw - 4, Y(o.ref.value) - 5, o.ref.label, "fv-flag-lab", "end");
  }
  xAxis(svg, labels, X, mt, ph, pw, mode);
  flagsDraw(svg, o.flags, X, mt, ph, mini);
  if (bandOn) {
    let d = "", seg = [];
    const flush = () => {
      if (seg.length > 1) {
        d += "M" + seg.map(i => X(i).toFixed(1) + "," + Y(o.band.upper[i]).toFixed(1)).join(" L");
        d += " L" + seg.slice().reverse().map(i => X(i).toFixed(1) + "," + Y(o.band.lower[i]).toFixed(1)).join(" L") + " Z ";
      }
      seg = [];
    };
    for (let i = 0; i < n; i++) { if (ok(o.band.lower[i]) && ok(o.band.upper[i])) seg.push(i); else flush(); }
    flush();
    S("path", { d: d, fill: o.band.color, "fill-opacity": 0.14, stroke: "none" }, svg);
  }
  series.forEach(s => {
    let d = "", pen = false;
    const iso = [];
    s.values.forEach((v, i) => {
      if (!ok(v)) { pen = false; return; }
      d += (pen ? "L" : "M") + X(i).toFixed(1) + "," + Y(v).toFixed(1);
      if (!pen && !ok(s.values[i + 1])) iso.push(i);
      pen = true;
    });
    if (s.area) {
      let a = "", seg = [];
      const flush = () => { if (seg.length > 1) a += "M" + X(seg[0]) + "," + Y(Math.max(lo, 0)) + " L" + seg.map(i => X(i).toFixed(1) + "," + Y(s.values[i]).toFixed(1)).join(" L") + " L" + X(seg[seg.length - 1]) + "," + Y(Math.max(lo, 0)) + " Z "; seg = []; };
      s.values.forEach((v, i) => { if (ok(v)) seg.push(i); else flush(); });
      flush();
      S("path", { d: a, fill: s.color, "fill-opacity": 0.10, stroke: "none" }, svg);
    }
    S("path", { d: d, fill: "none", stroke: s.color, "stroke-width": s.width || (mini ? 1.8 : 2), "stroke-linejoin": "round", "stroke-linecap": "round", opacity: s.opacity || 1 }, svg);
    iso.forEach(i => S("circle", { cx: X(i), cy: Y(s.values[i]), r: 2.5, fill: s.color }, svg));
    if (s.dots) s.values.forEach((v, i) => { if (ok(v)) S("circle", { cx: X(i), cy: Y(v), r: 3.2, fill: s.color, stroke: C.surface, "stroke-width": 1.5 }, svg); });
  });
  if (endItems.length) {
    endItems.forEach(e => { e.x = X(e.i); e.y = Y(e.s.values[e.i]); });
    endItems.sort((a, b) => a.y - b.y);
    const gap = 15;
    const ys = endItems.map(e => e.y);
    for (let k = 1; k < ys.length; k++) ys[k] = Math.max(ys[k], ys[k - 1] + gap);
    const bottom = mt + ph + 4;
    if (ys[ys.length - 1] > bottom) {
      const sh = ys[ys.length - 1] - bottom;
      for (let k = 0; k < ys.length; k++) ys[k] -= sh;
      for (let k = ys.length - 2; k >= 0; k--) ys[k] = Math.min(ys[k], ys[k + 1] - gap);
    }
    endItems.forEach((e, k) => {
      const lx = e.x + 9;
      if (Math.abs(ys[k] - e.y) > 2) S("path", { d: "M" + (e.x + 4) + "," + e.y + " L" + (lx + 1) + "," + ys[k], class: "fv-leader" }, svg);
      S("circle", { cx: e.x, cy: e.y, r: 3.6, fill: e.s.color, stroke: C.surface, "stroke-width": 2 }, svg);
      T(svg, lx + 5, ys[k] + 4, e.text, "fv-lab");
    });
  }
  // hover
  const cross = S("line", { class: "fv-cross", y1: mt, y2: mt + ph, visibility: "hidden" }, svg);
  const hd = series.map(s => S("circle", { r: 4.5, fill: s.color, stroke: C.surface, "stroke-width": 2, visibility: "hidden" }, svg));
  const hit = S("rect", { x: ml - half, y: mt, width: pw + 2 * half, height: ph, fill: "transparent" }, svg);
  let cur = -1;
  const idxAt = px => mode === "band" ? clamp(Math.floor((px - ml) / pw * n), 0, n - 1) : clamp(Math.round((px - ml) / pw * (n - 1)), 0, n - 1);
  function show(i, evt) {
    cur = i;
    const x = X(i);
    cross.setAttribute("x1", x); cross.setAttribute("x2", x); cross.setAttribute("visibility", "visible");
    const rows = [];
    series.forEach((s, k) => {
      const v = s.values[i];
      if (!ok(v)) { hd[k].setAttribute("visibility", "hidden"); return; }
      hd[k].setAttribute("cx", x); hd[k].setAttribute("cy", Y(v)); hd[k].setAttribute("visibility", "visible");
      rows.push({ color: s.color, kind: "line", label: s.name, value: s.tip ? s.tip(i, v) : (s.fmt || fmt)(v) });
    });
    if (bandOn && ok(o.band.lower[i])) rows.push({ color: o.band.color, kind: "rect", wash: true, label: o.band.name, value: fmt(o.band.lower[i]) + " – " + fmt(o.band.upper[i]) });
    if (o.extraRows) o.extraRows(i).forEach(r => rows.push(r));
    let cx, cy;
    if (evt) { cx = evt.clientX; cy = evt.clientY; } else { const r = svg.getBoundingClientRect(); cx = r.left + x; cy = r.top + mt + 8; }
    tipShow(cx, cy, o.tipTitle ? o.tipTitle(i) : labels[i], rows, o.tipNote ? o.tipNote(i) : null);
  }
  function hide() { cur = -1; cross.setAttribute("visibility", "hidden"); hd.forEach(h => h.setAttribute("visibility", "hidden")); tipHide(); }
  const move = e => { const r = svg.getBoundingClientRect(); show(idxAt(e.clientX - r.left), e); };
  hit.addEventListener("pointermove", move);
  hit.addEventListener("pointerdown", move);
  hit.addEventListener("pointerleave", hide);
  keyboard(svg, n, show, hide, () => cur);
  const cols = [{ key: "x", label: o.xTitle || (labels.every(isMonth) ? "Month" : "Period") }].concat(o.series.map((s, k) => ({ key: "s" + k, label: s.name, num: true })));
  if (o.band) cols.push({ key: "lo", label: o.band.name + " (low)", num: true }, { key: "hi", label: o.band.name + " (high)", num: true });
  const rows = labels.map((l, i) => {
    const r = { x: l };
    o.series.forEach((s, k) => { r["s" + k] = (s.fmt || fmt)(s.values[i]); });
    if (o.band) { r.lo = fmt(o.band.lower[i]); r.hi = fmt(o.band.upper[i]); }
    return r;
  });
  return { table: { cols: cols, rows: rows } };
}

/* ------------------------------------------------------------------ BARS */
function barChart(el, o) {
  el.replaceChildren();
  const hidden = el._hidden || (el._hidden = new Set());
  const W = Math.max(240, el.clientWidth || 600);
  const Hh = o.height || 300;
  const mini = !!o.mini;
  const labels = o.labels;
  const n = labels.length;
  const series = o.series.filter(s => !hidden.has(s.name));
  const lineOn = o.line && !hidden.has(o.line.name);
  let lo = 0, hi = 0;
  for (let i = 0; i < n; i++) {
    if (o.stacked) {
      let p = 0, q = 0;
      series.forEach(s => { const v = s.values[i]; if (ok(v)) { if (v > 0) p += v; else q += v; } });
      hi = Math.max(hi, p); lo = Math.min(lo, q);
    } else series.forEach(s => { const v = s.values[i]; if (ok(v)) { hi = Math.max(hi, v); lo = Math.min(lo, v); } });
  }
  if (lineOn) o.line.values.forEach(v => { if (ok(v)) { hi = Math.max(hi, v); lo = Math.min(lo, v); } });
  if (o.ref) hi = Math.max(hi, o.ref.value);
  if (o.yMax !== undefined) hi = o.yMax;
  if (o.yMin !== undefined) lo = o.yMin;
  if (hi === lo) hi = lo + 1;
  const ticks = niceTicks(lo, hi, o.yTicks || (mini ? 3 : Hh < 220 ? 4 : 5));
  lo = ticks[0]; hi = ticks[ticks.length - 1];
  const fmt = o.fmt || f.int;
  const tf = o.tickFormat || tickFormatter(o.tickKind || "num", ticks);
  const ml = Math.max(...ticks.map(t => measure(tf(t)))) + 14;
  const mr = mini ? 6 : 12;
  const mt = o.shades && o.shades.some(s => s.label) && !mini ? 20 : 10;
  const mb = 26;
  const pw = Math.max(40, W - ml - mr), ph = Hh - mt - mb;
  const step = pw / n;
  const X = i => ml + (i + 0.5) * step;
  const Y = v => mt + ph - (v - lo) / (hi - lo) * ph;
  const k = o.stacked ? 1 : Math.max(1, series.length);
  const maxBar = o.maxBar || 24;
  const groupW = o.stacked ? Math.min(maxBar, step * 0.72) : Math.min(maxBar * k + 2 * (k - 1), step * 0.82);
  const barW = o.stacked ? groupW : Math.max(1, (groupW - 2 * (k - 1)) / k);
  const svg = S("svg", { width: W, height: Hh, viewBox: "0 0 " + W + " " + Hh, class: "fv-svg", role: "img", "aria-label": o.aria || "" }, el);
  shadesDraw(svg, o.shades, X, step / 2, mt, ph, mini);
  yAxis(svg, o, ticks, tf, ml, mt, pw, ph, Y);
  xAxis(svg, labels, X, mt, ph, pw, "band");
  const wash = S("rect", { class: "fv-hband", y: mt, height: ph, width: step, visibility: "hidden" }, svg);
  const dim = new Set(o.dim || []);
  const g = S("g", null, svg);
  const base = Y(Math.max(lo, Math.min(0, hi)));
  for (let i = 0; i < n; i++) {
    const op = dim.has(i) ? 0.32 : 1;
    if (o.stacked) {
      const pos = [], neg = [];
      let up = 0, dn = 0;
      series.forEach(s => {
        const v = s.values[i];
        if (!ok(v) || v === 0) return;
        const col = s.colors ? s.colors[i] : s.color;
        if (v > 0) { pos.push({ a: up, b: up + v, col: col }); up += v; } else { neg.push({ a: dn, b: dn + v, col: col }); dn += v; }
      });
      const x = X(i) - groupW / 2;
      pos.forEach((sg, j) => {
        let top = Y(sg.b), bot = Y(sg.a);
        if (j < pos.length - 1) top += 1;
        if (j > 0) bot -= 1;
        if (bot - top < 0.6) return;
        S("path", { d: roundedBar(x, groupW, top, bot, j === pos.length - 1, false), fill: sg.col, opacity: op }, g);
      });
      neg.forEach((sg, j) => {
        let top = Y(sg.a), bot = Y(sg.b);
        if (j > 0) top += 1;
        if (j < neg.length - 1) bot -= 1;
        if (bot - top < 0.6) return;
        S("path", { d: roundedBar(x, groupW, top, bot, false, j === neg.length - 1), fill: sg.col, opacity: op }, g);
      });
    } else {
      series.forEach((s, j) => {
        const v = s.values[i];
        if (!ok(v)) return;
        const col = s.colors ? s.colors[i] : s.color;
        const x = X(i) - groupW / 2 + j * (barW + 2);
        if (v === 0) {
          if (o.zeroMarks) S("rect", { x: x + barW / 2 - 1, y: base - 3, width: 2, height: 3, fill: C.de }, g);
          return;
        }
        const y0 = Y(0), y1 = Y(v);
        if (v > 0) S("path", { d: roundedBar(x, barW, y1, y0, true, false), fill: col, opacity: op }, g);
        else S("path", { d: roundedBar(x, barW, y0, y1, false, true), fill: col, opacity: op }, g);
      });
    }
  }
  if (o.ref && o.ref.value <= hi && o.ref.value >= lo) {
    S("line", { x1: ml, x2: ml + pw, y1: Y(o.ref.value), y2: Y(o.ref.value), class: "fv-ref" }, svg);
    if (o.ref.label) T(svg, ml + pw - 2, Y(o.ref.value) - 4, o.ref.label, "fv-flag-lab", "end");
  }
  if (lineOn) {
    let d = "", pen = false;
    o.line.values.forEach((v, i) => { if (!ok(v)) { pen = false; return; } d += (pen ? "L" : "M") + X(i).toFixed(1) + "," + Y(v).toFixed(1); pen = true; });
    S("path", { d: d, fill: "none", stroke: o.line.color, "stroke-width": 2, "stroke-linejoin": "round", "stroke-linecap": "round" }, svg);
    if (!mini) o.line.values.forEach((v, i) => { if (ok(v)) S("circle", { cx: X(i), cy: Y(v), r: 2.6, fill: o.line.color, stroke: C.surface, "stroke-width": 1.4 }, svg); });
  }
  flagsDraw(svg, o.flags, X, mt, ph, mini);
  let cur = -1;
  function rowsAt(i) {
    if (o.tipRows) return o.tipRows(i);
    const rows = [];
    series.forEach(s => {
      const v = s.values[i];
      if (!ok(v) || (o.hideZero && v === 0)) return;
      rows.push({ color: s.colors ? s.colors[i] : s.color, kind: "rect", label: s.name, value: (s.fmt || fmt)(v) });
    });
    if (o.stacked && o.showTotal) rows.push({ kind: "none", label: o.totalLabel || "Total", value: fmt(sum(series.map(s => s.values[i]))) });
    if (lineOn && ok(o.line.values[i])) rows.push({ color: o.line.color, kind: "line", label: o.line.name, value: (o.line.fmt || fmt)(o.line.values[i]) });
    if (o.extraRows) o.extraRows(i).forEach(r => rows.push(r));
    return rows;
  }
  function show(i, evt) {
    cur = i;
    wash.setAttribute("x", ml + i * step); wash.setAttribute("visibility", "visible");
    let cx, cy;
    if (evt) { cx = evt.clientX; cy = evt.clientY; } else { const r = svg.getBoundingClientRect(); cx = r.left + X(i); cy = r.top + mt + 8; }
    const note = (dim.has(i) && o.dimNote) ? o.dimNote : (o.tipNote ? o.tipNote(i) : null);
    tipShow(cx, cy, o.tipTitle ? o.tipTitle(i) : labels[i], rowsAt(i), note);
  }
  function hide() { cur = -1; wash.setAttribute("visibility", "hidden"); tipHide(); }
  const hit = S("rect", { x: ml, y: mt, width: pw, height: ph, fill: "transparent" }, svg);
  const move = e => { const r = svg.getBoundingClientRect(); show(clamp(Math.floor((e.clientX - r.left - ml) / step), 0, n - 1), e); };
  hit.addEventListener("pointermove", move);
  hit.addEventListener("pointerdown", move);
  hit.addEventListener("pointerleave", hide);
  keyboard(svg, n, show, hide, () => cur);
  const cols = [{ key: "x", label: o.xTitle || (labels.every(isMonth) ? "Month" : "Period") }].concat(o.series.map((s, j) => ({ key: "s" + j, label: s.name, num: true })));
  if (o.line) cols.push({ key: "ln", label: o.line.name, num: true });
  const rows = labels.map((l, i) => {
    const r = { x: l };
    o.series.forEach((s, j) => { r["s" + j] = (s.tableFmt || s.fmt || fmt)(s.values[i]); });
    if (o.line) r.ln = (o.line.fmt || fmt)(o.line.values[i]);
    return r;
  });
  return { table: { cols: cols, rows: rows } };
}

/* ------------------------------------------------------------------ WATERFALL */
function waterfall(el, o) {
  el.replaceChildren();
  const W = Math.max(260, el.clientWidth || 600);
  const Hh = o.height || 300;
  const steps = o.steps;
  const n = steps.length;
  let run = 0;
  const bars = steps.map(s => {
    if (s.kind === "total") { run = s.value; return { a: null, b: s.value, s: s }; }
    const a = run; run += s.value; return { a: a, b: run, s: s };
  });
  const levels = bars.map(b => b.b).concat(bars.filter(b => b.a !== null).map(b => b.a));
  let lo = o.yMin !== undefined ? o.yMin : Math.min(0, ...levels);
  const hi = Math.max(...levels) * 1.0;
  const ticks = niceTicks(lo, hi, 5);
  lo = o.yMin !== undefined ? Math.max(ticks[0], o.yMin) : ticks[0];
  const top = ticks[ticks.length - 1];
  const tk = ticks.filter(t => t >= lo);
  const fmt = o.fmt || f.cop;
  const tf = o.tickFormat || tickFormatter(o.tickKind || "cop", tk);
  const ml = Math.max(...tk.map(t => measure(tf(t)))) + 16;
  const mt = 22, mb = 34, mr = 10;
  const pw = W - ml - mr, ph = Hh - mt - mb;
  const step = pw / n;
  const X = i => ml + (i + 0.5) * step;
  const Y = v => mt + ph - (v - lo) / (top - lo) * ph;
  const bw = Math.min(58, step * 0.56);
  const svg = S("svg", { width: W, height: Hh, viewBox: "0 0 " + W + " " + Hh, class: "fv-svg", role: "img" }, el);
  tk.forEach(t => { S("line", { x1: ml, x2: ml + pw, y1: Y(t), y2: Y(t), class: t === lo ? "fv-base" : "fv-grid" }, svg); T(svg, ml - 8, Y(t) + 3.5, tf(t), "fv-tick", "end"); });
  if (lo > 0) {
    const y = mt + ph;
    S("path", { d: "M" + (ml - 5) + "," + (y - 2) + " l10,-5 M" + (ml - 5) + "," + (y + 3) + " l10,-5", class: "fv-break" }, svg);
  }
  const wash = S("rect", { class: "fv-hband", y: mt, height: ph, width: step, visibility: "hidden" }, svg);
  bars.forEach((b, i) => {
    const x = X(i) - bw / 2;
    let y0, y1, up;
    if (b.a === null) { y0 = Y(lo); y1 = Y(b.b); up = true; }
    else { up = b.b >= b.a; y0 = Y(up ? b.a : b.b); y1 = Y(up ? b.b : b.a); }
    const topY = Math.min(y0, y1), botY = Math.max(y0, y1);
    const d = b.a === null ? roundedBar(x, bw, topY, botY, true, false) : roundedBar(x, bw, topY, botY, up, !up);
    S("path", { d: d, fill: b.s.color || C.s1 }, svg);
    const txt = b.a === null ? fmt(b.b) : (b.s.value >= 0 ? "+" : MINUS) + fmt(Math.abs(b.s.value)).replace(MINUS, "");
    const ly = b.a === null || up ? topY - 7 : botY + 14;
    T(svg, X(i), ly, txt, "fv-lab b", "middle");
    const labs = String(b.s.label).split("\n");
    labs.forEach((l, j) => T(svg, X(i), mt + ph + 16 + j * 12, l, "fv-tick" + (j === 0 ? " strong" : ""), "middle"));
    if (i < n - 1) {
      const lvl = Y(b.b);
      S("line", { x1: X(i) + bw / 2, x2: X(i + 1) - bw / 2, y1: lvl, y2: lvl, class: "fv-leader" }, svg);
    }
  });
  let cur = -1;
  function show(i, evt) {
    cur = i;
    wash.setAttribute("x", ml + i * step); wash.setAttribute("visibility", "visible");
    const b = bars[i];
    const rows = [{ color: b.s.color, kind: "rect", label: b.s.label.replace("\n", " "), value: b.a === null ? f.copFull(b.b) : (b.s.value >= 0 ? "+" : MINUS) + f.copFull(Math.abs(b.s.value)).replace(MINUS, "") }];
    if (b.a !== null) rows.push({ kind: "none", label: "running level", value: fmt(b.b) });
    if (b.s.extra) b.s.extra.forEach(r => rows.push(r));
    let cx, cy;
    if (evt) { cx = evt.clientX; cy = evt.clientY; } else { const r = svg.getBoundingClientRect(); cx = r.left + X(i); cy = r.top + mt; }
    tipShow(cx, cy, o.title || "Bridge", rows, b.s.note || null);
  }
  function hide() { cur = -1; wash.setAttribute("visibility", "hidden"); tipHide(); }
  const hit = S("rect", { x: ml, y: mt, width: pw, height: ph, fill: "transparent" }, svg);
  const move = e => { const r = svg.getBoundingClientRect(); show(clamp(Math.floor((e.clientX - r.left - ml) / step), 0, n - 1), e); };
  hit.addEventListener("pointermove", move);
  hit.addEventListener("pointerdown", move);
  hit.addEventListener("pointerleave", hide);
  keyboard(svg, n, show, hide, () => cur);
  return { table: { cols: [{ key: "a", label: "Step" }, { key: "b", label: "Value", num: true }, { key: "c", label: "Level after step", num: true }],
    rows: bars.map(b => ({ a: b.s.label.replace("\n", " "), b: f.copFull(b.a === null ? b.b : b.s.value), c: f.copFull(b.b) })) } };
}

/* ------------------------------------------------------------------ SCATTER */
function scatter(el, o) {
  el.replaceChildren();
  const W = Math.max(260, el.clientWidth || 600);
  const Hh = o.height || 320;
  const pts = o.points.filter(p => ok(p.x) && ok(p.y));
  const xs = pts.map(p => p.x), ys = pts.map(p => p.y);
  const padX = (Math.max(...xs) - Math.min(...xs)) * 0.06 || 1, padY = (Math.max(...ys) - Math.min(...ys)) * 0.08 || 1;
  const xt = niceTicks(Math.min(...xs) - padX, Math.max(...xs) + padX, 5);
  const yt = niceTicks(Math.min(...ys) - padY, Math.max(...ys) + padY, 5);
  const xfT = tickFormatter(o.xKind || "num", xt), yfT = tickFormatter(o.yKind || "num", yt);
  const ml = Math.max(...yt.map(t => measure(yfT(t)))) + 16;
  const mt = 16, mb = 44, mr = 14;
  const pw = W - ml - mr, ph = Hh - mt - mb;
  const X = v => ml + (v - xt[0]) / (xt[xt.length - 1] - xt[0]) * pw;
  const Y = v => mt + ph - (v - yt[0]) / (yt[yt.length - 1] - yt[0]) * ph;
  const svg = S("svg", { width: W, height: Hh, viewBox: "0 0 " + W + " " + Hh, class: "fv-svg", role: "img" }, el);
  yt.forEach(t => { S("line", { x1: ml, x2: ml + pw, y1: Y(t), y2: Y(t), class: t === 0 ? "fv-base" : "fv-grid" }, svg); T(svg, ml - 8, Y(t) + 3.5, yfT(t), "fv-tick", "end"); });
  xt.forEach(t => { S("line", { x1: X(t), x2: X(t), y1: mt, y2: mt + ph, class: t === 0 ? "fv-base" : "fv-grid" }, svg); T(svg, X(t), mt + ph + 16, xfT(t), "fv-tick", "middle"); });
  if (o.xTitle) T(svg, ml + pw / 2, Hh - 6, o.xTitle, "fv-axis-title", "middle");
  if (o.yTitle) T(svg, ml, mt - 4, o.yTitle, "fv-axis-title", "start");
  if (pts.length >= 3) {
    const mx = xs.reduce((a, b) => a + b, 0) / xs.length, my = ys.reduce((a, b) => a + b, 0) / ys.length;
    let sxy = 0, sxx = 0;
    pts.forEach(p => { sxy += (p.x - mx) * (p.y - my); sxx += (p.x - mx) * (p.x - mx); });
    const b = sxx ? sxy / sxx : 0, a = my - b * mx;
    const x0 = Math.min(...xs), x1 = Math.max(...xs);
    S("path", { d: "M" + X(x0) + "," + Y(a + b * x0) + " L" + X(x1) + "," + Y(a + b * x1), class: "fv-trend" }, svg);
  }
  const dots = pts.map(p => S("circle", { cx: X(p.x), cy: Y(p.y), r: 5.2, fill: p.color || o.color || C.s1, "fill-opacity": 0.82, stroke: C.surface, "stroke-width": 2 }, svg));
  const ring = S("circle", { r: 9, fill: "none", stroke: C.ink, "stroke-width": 1.4, visibility: "hidden" }, svg);
  let cur = -1;
  function show(i, evt) {
    cur = i;
    const p = pts[i];
    ring.setAttribute("cx", X(p.x)); ring.setAttribute("cy", Y(p.y)); ring.setAttribute("visibility", "visible");
    let cx, cy;
    if (evt) { cx = evt.clientX; cy = evt.clientY; } else { const r = svg.getBoundingClientRect(); cx = r.left + X(p.x); cy = r.top + Y(p.y); }
    tipShow(cx, cy, p.label, [
      { color: o.color || C.s1, kind: "dot", label: o.xName || "x", value: (o.xFmt || f.num)(p.x) },
      { kind: "none", label: o.yName || "y", value: (o.yFmt || f.num)(p.y) },
    ], p.note || null);
  }
  function hide() { cur = -1; ring.setAttribute("visibility", "hidden"); tipHide(); }
  const hit = S("rect", { x: ml, y: mt, width: pw, height: ph, fill: "transparent" }, svg);
  const move = e => {
    const r = svg.getBoundingClientRect();
    const px = e.clientX - r.left, py = e.clientY - r.top;
    let best = -1, bd = 32 * 32;
    pts.forEach((p, i) => { const d = (X(p.x) - px) ** 2 + (Y(p.y) - py) ** 2; if (d < bd) { bd = d; best = i; } });
    if (best >= 0) show(best, e); else hide();
  };
  hit.addEventListener("pointermove", move);
  hit.addEventListener("pointerdown", move);
  hit.addEventListener("pointerleave", hide);
  keyboard(svg, pts.length, show, hide, () => cur);
  return { table: { cols: [{ key: "l", label: "Outcome month" }, { key: "x", label: o.xName || "x", num: true }, { key: "y", label: o.yName || "y", num: true }],
    rows: pts.map(p => ({ l: p.label, x: (o.xFmt || f.num)(p.x), y: (o.yFmt || f.num)(p.y) })) } };
}

/* ------------------------------------------------------------------ HEATMAP */
function lerpHex(a, b, t) {
  const pa = [1, 3, 5].map(k => parseInt(a.slice(k, k + 2), 16)), pb = [1, 3, 5].map(k => parseInt(b.slice(k, k + 2), 16));
  return "#" + pa.map((v, k) => Math.round(v + (pb[k] - v) * t).toString(16).padStart(2, "0")).join("");
}
function rampColor(ramp, t) {
  t = clamp(t, 0, 1) * (ramp.length - 1);
  const i = Math.min(ramp.length - 2, Math.floor(t));
  return lerpHex(ramp[i], ramp[i + 1], t - i);
}
const seqColor = (v, lo, hi) => rampColor(SEQ, (v - lo) / (hi - lo));
function divColor(v) {
  if (!ok(v)) return null;
  if (Math.abs(v) < 0.05) return MID;
  return v > 0 ? rampColor([MID].concat(SEQ.slice(3)), v) : rampColor([MID].concat(RED.slice(1)), -v);
}
function lum(hex) {
  const c = [1, 3, 5].map(k => parseInt(hex.slice(k, k + 2), 16) / 255).map(v => v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4));
  return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
}
function heatmap(el, o) {
  el.replaceChildren();
  const W = Math.max(260, el.clientWidth || 600);
  const rows = o.rows, cols = o.cols;
  const labW = Math.max(...rows.map(r => measure(r, SANS))) + 14;
  const pw = W - labW - 6;
  const cw = pw / cols.length;
  const ch = o.cellH || 22;
  const topH = 20;
  const Hh = topH + rows.length * ch + 4;
  const svg = S("svg", { width: W, height: Hh, viewBox: "0 0 " + W + " " + Hh, class: "fv-svg", role: "img" }, el);
  const maxColW = Math.max(...cols.map(c => measure(c))) + 6;
  let every = 1;
  while (cw * every < maxColW) every++;
  const hl = new Set(o.highlightCols || []);
  const want = cols.map((c, j) => ({ j: j, c: c, w: measure(c) + 6, x: labW + (j + 0.5) * cw, hl: hl.has(j) }));
  const placed = [];
  want.filter(w => w.hl).concat(want.filter(w => !w.hl && w.j % every === 0)).forEach(w => {
    const a = w.x - w.w / 2, b = w.x + w.w / 2;
    if (placed.some(p => !(b < p[0] || a > p[1]))) return;
    placed.push([a, b]);
    T(svg, w.x, topH - 7, w.c, "fv-tick" + (w.hl ? " strong" : ""), "middle");
  });
  rows.forEach((r, i) => T(svg, labW - 10, topH + i * ch + ch / 2 + 4, r, "fv-lab" + (o.rowStrong && o.rowStrong(i) ? " b" : ""), "end"));
  const showText = o.text && cw >= (o.minTextW || 34) && ch >= 18;
  for (let i = 0; i < rows.length; i++) {
    for (let j = 0; j < cols.length; j++) {
      const v = o.values[i][j];
      if (!ok(v)) continue;
      const col = o.color(v);
      S("rect", { x: labW + j * cw + 1, y: topH + i * ch + 1, width: Math.max(1, cw - 2), height: ch - 2, rx: Math.min(4, cw / 4), fill: col }, svg);
      if (showText) T(svg, labW + (j + 0.5) * cw, topH + i * ch + ch / 2 + 3.5, o.text(v), "fv-cell-t", "middle", { fill: lum(col) < 0.33 ? "#ffffff" : C.ink, "font-weight": o.textStrong && o.textStrong(i, j) ? 700 : null });
    }
  }
  const sel = o.selected;
  if (sel) S("rect", { x: labW + sel[1] * cw + 0.5, y: topH + sel[0] * ch + 0.5, width: cw - 1, height: ch - 1, rx: 4, fill: "none", stroke: C.ink, "stroke-width": 2 }, svg);
  const ring = S("rect", { width: Math.max(2, cw - 1), height: ch - 1, rx: 4, fill: "none", stroke: C.ink, "stroke-width": 1.4, visibility: "hidden", "pointer-events": "none" }, svg);
  const hit = S("rect", { x: labW, y: topH, width: cols.length * cw, height: rows.length * ch, fill: "transparent", style: o.onPick ? "cursor:pointer" : null }, svg);
  let cur = [-1, -1];
  function show(i, j, evt) {
    const v = o.values[i] ? o.values[i][j] : null;
    if (!ok(v)) { hide(); return; }
    cur = [i, j];
    ring.setAttribute("x", labW + j * cw + 0.5); ring.setAttribute("y", topH + i * ch + 0.5); ring.setAttribute("visibility", "visible");
    const t = o.tip(i, j, v);
    let cx, cy;
    if (evt) { cx = evt.clientX; cy = evt.clientY; } else { const r = svg.getBoundingClientRect(); cx = r.left + labW + (j + 0.5) * cw; cy = r.top + topH + (i + 1) * ch; }
    tipShow(cx, cy, t.title, t.rows, t.note || null);
  }
  function hide() { ring.setAttribute("visibility", "hidden"); tipHide(); }
  const at = e => { const r = svg.getBoundingClientRect(); return [clamp(Math.floor((e.clientY - r.top - topH) / ch), 0, rows.length - 1), clamp(Math.floor((e.clientX - r.left - labW) / cw), 0, cols.length - 1)]; };
  hit.addEventListener("pointermove", e => { const p = at(e); show(p[0], p[1], e); });
  hit.addEventListener("pointerleave", hide);
  if (o.onPick) hit.addEventListener("click", e => { const p = at(e); o.onPick(p[0], p[1]); });
  svg.setAttribute("tabindex", "0");
  svg.addEventListener("keydown", e => {
    let [i, j] = cur[0] < 0 ? [0, 0] : cur;
    if (e.key === "ArrowRight") j++; else if (e.key === "ArrowLeft") j--; else if (e.key === "ArrowDown") i++; else if (e.key === "ArrowUp") i--;
    else if (e.key === "Enter" && o.onPick && cur[0] >= 0) { o.onPick(cur[0], cur[1]); return; }
    else if (e.key === "Escape") { hide(); return; } else return;
    e.preventDefault();
    show(clamp(i, 0, rows.length - 1), clamp(j, 0, cols.length - 1), null);
  });
  svg.addEventListener("blur", hide);
  const tcols = [{ key: "r", label: o.rowTitle || "Row" }].concat(cols.map((c, j) => ({ key: "c" + j, label: c, num: true })));
  const trows = rows.map((r, i) => { const x = { r: r }; cols.forEach((c, j) => { x["c" + j] = ok(o.values[i][j]) ? o.fmt(o.values[i][j]) : ""; }); return x; });
  return { table: { cols: tcols, rows: trows } };
}

/* ------------------------------------------------------------------ DOTS (dumbbell) */
function dots(el, o) {
  el.replaceChildren();
  const W = Math.max(260, el.clientWidth || 600);
  const rows = o.rows;
  const rh = o.rowH || 34;
  const labW = Math.max(...rows.map(r => measure(r, SANS))) + 16;
  const mt = 8, mb = 26, mr = 14;
  const Hh = mt + rows.length * rh + mb;
  let vals = [];
  o.series.forEach(s => s.values.forEach(v => { if (ok(v)) vals.push(v); }));
  const ticks = niceTicks(Math.min(0, ...vals), Math.max(...vals), 5);
  const tf = tickFormatter(o.tickKind || "cop", ticks);
  const pw = W - labW - mr;
  const X = v => labW + (v - ticks[0]) / (ticks[ticks.length - 1] - ticks[0]) * pw;
  const svg = S("svg", { width: W, height: Hh, viewBox: "0 0 " + W + " " + Hh, class: "fv-svg", role: "img" }, el);
  ticks.forEach(t => { S("line", { x1: X(t), x2: X(t), y1: mt, y2: mt + rows.length * rh, class: t === 0 ? "fv-base" : "fv-grid" }, svg); T(svg, X(t), mt + rows.length * rh + 17, tf(t), "fv-tick", "middle"); });
  const hits = [];
  rows.forEach((r, i) => {
    const y = mt + i * rh + rh / 2;
    T(svg, labW - 12, y + 4, r, "fv-lab", "end");
    const vs = o.series.map(s => s.values[i]).filter(ok);
    if (vs.length > 1) S("line", { x1: X(Math.min(...vs)), x2: X(Math.max(...vs)), y1: y, y2: y, stroke: C.de, "stroke-width": 2.5, "stroke-linecap": "round" }, svg);
    o.series.forEach((s, k) => {
      const v = s.values[i];
      if (!ok(v)) return;
      S("circle", { cx: X(v), cy: y, r: 6, fill: s.color, stroke: C.surface, "stroke-width": 2 }, svg);
      hits.push({ i: i, k: k, x: X(v), y: y, v: v });
    });
  });
  const ring = S("circle", { r: 10, fill: "none", stroke: C.ink, "stroke-width": 1.4, visibility: "hidden" }, svg);
  const hit = S("rect", { x: labW, y: mt, width: pw, height: rows.length * rh, fill: "transparent" }, svg);
  hit.addEventListener("pointermove", e => {
    const r = svg.getBoundingClientRect();
    const px = e.clientX - r.left, py = e.clientY - r.top;
    let best = null, bd = 30 * 30;
    hits.forEach(h => { const d = (h.x - px) ** 2 + (h.y - py) ** 2; if (d < bd) { bd = d; best = h; } });
    if (!best) { ring.setAttribute("visibility", "hidden"); tipHide(); return; }
    ring.setAttribute("cx", best.x); ring.setAttribute("cy", best.y); ring.setAttribute("visibility", "visible");
    const rowsTip = o.series.map(s => ({ color: s.color, kind: "dot", label: s.name, value: (o.fmt || f.cop)(s.values[best.i]) }));
    tipShow(e.clientX, e.clientY, rows[best.i], rowsTip, o.note ? o.note(best.i) : null);
  });
  hit.addEventListener("pointerleave", () => { ring.setAttribute("visibility", "hidden"); tipHide(); });
  return { table: { cols: [{ key: "r", label: o.rowTitle || "Row" }].concat(o.series.map((s, k) => ({ key: "s" + k, label: s.name, num: true }))),
    rows: rows.map((r, i) => { const x = { r: r }; o.series.forEach((s, k) => { x["s" + k] = (o.fmt || f.cop)(s.values[i]); }); return x; }) } };
}

/* ------------------------------------------------------------------ MULTIPLES */
function multiples(el, o) {
  el.replaceChildren();
  const W = el.clientWidth || 600;
  const cols = Math.max(1, Math.min(o.cols || 3, Math.floor(W / (o.minCellW || 250))));
  const grid = H("div", "mult", el);
  grid.style.gridTemplateColumns = "repeat(" + cols + ", minmax(0, 1fr))";
  let shared = {};
  if (o.sharedY) {
    let lo = Infinity, hi = -Infinity;
    o.items.forEach(it => (it.opts.series || []).forEach(s => s.values.forEach(v => { if (ok(v)) { lo = Math.min(lo, v); hi = Math.max(hi, v); } })));
    shared = { yMin: Math.min(0, lo), yMax: hi };
  }
  const tables = [];
  o.items.forEach(it => {
    const cell = H("div", "cell", grid);
    const t = H("div", "cell-t", cell, it.title);
    if (it.right) H("span", null, t, it.right);
    if (it.note !== undefined) H("div", "cell-n", cell, it.note);
    const c = H("div", "chart", cell);
    const fn = it.kind === "bars" ? barChart : lineChart;
    const res = fn(c, Object.assign({ height: o.height || 150, mini: true }, shared, it.opts));
    if (res && res.table) tables.push({ title: it.title, table: res.table });
  });
  return { tables: tables };
}

/* ------------------------------------------------------------------ SPARK */
function spark(el, values) {
  el.replaceChildren();
  const W = el.clientWidth || 200, Hh = 38;
  const pts = values.map((v, i) => ok(v) ? [i, v] : null).filter(Boolean);
  if (pts.length < 2) return;
  const lo = Math.min(...pts.map(p => p[1])), hi = Math.max(...pts.map(p => p[1]));
  const X = i => 2 + i / (values.length - 1) * (W - 8), Y = v => Hh - 4 - (hi === lo ? 0.5 : (v - lo) / (hi - lo)) * (Hh - 10);
  const svg = S("svg", { width: W, height: Hh, viewBox: "0 0 " + W + " " + Hh, "aria-hidden": "true" }, el);
  let d = "", pen = false;
  values.forEach((v, i) => { if (!ok(v)) { pen = false; return; } d += (pen ? "L" : "M") + X(i).toFixed(1) + "," + Y(v).toFixed(1); pen = true; });
  S("path", { d: d, fill: "none", stroke: C.de, "stroke-width": 1.6, "stroke-linejoin": "round" }, svg);
  const last = pts[pts.length - 1];
  S("circle", { cx: X(last[0]), cy: Y(last[1]), r: 3.4, fill: C.s1, stroke: C.surface, "stroke-width": 1.5 }, svg);
}

/* ------------------------------------------------------------------ LEGEND + TABLE */
function legend(card, items, el, target) {
  const lg = target || (card && card.querySelector(".legend"));
  if (!lg) return;
  lg.replaceChildren();
  items.forEach(it => {
    const b = H("button", null, lg);
    b.type = "button";
    const sw = H("span", "sw " + (it.kind || "rect"), b);
    sw.style.background = it.color;
    b.append(it.name);
    const toggle = el && it.toggle !== false;
    if (toggle) {
      const off = el._hidden && el._hidden.has(it.key || it.name);
      if (off) b.classList.add("off");
      b.setAttribute("aria-pressed", String(!off));
      b.title = "Show / hide";
      b.addEventListener("click", () => {
        const hs = el._hidden || (el._hidden = new Set());
        const key = it.key || it.name;
        if (hs.has(key)) hs.delete(key); else hs.add(key);
        el._render();
      });
    } else { b.disabled = true; b.style.cursor = "default"; }
  });
}
function table(container, cols, rows) {
  container.replaceChildren();
  const t = H("table", "tbl", container);
  const tr = H("tr", null, H("thead", null, t));
  cols.forEach(c => H("th", c.num ? "n" : null, tr, c.label));
  const tb = H("tbody", null, t);
  rows.forEach(r => {
    const row = H("tr", r._cls || null, tb);
    cols.forEach(c => {
      const v = r[c.key];
      const td = H("td", (c.num ? "n" : "") + (c.dim ? " dim" : ""), row);
      td.textContent = c.fmt ? c.fmt(v, r) : (v === null || v === undefined || v === "" ? "–" : v);
    });
  });
  return t;
}
function mergeTables(list) {
  // tables that share the same first column (e.g. the 34 months) become one wide table
  const groups = [];
  list.forEach(x => {
    const t = x.table;
    const key = t.cols[0].label + "::" + t.rows.map(r => r[t.cols[0].key]).join("|");
    let g = x.title ? groups.find(gg => gg.key === key && gg.titled) : null;
    if (!g) { g = { key: key, titled: !!x.title, items: [] }; groups.push(g); }
    g.items.push(x);
  });
  return groups.map(g => {
    if (g.items.length === 1) return { title: g.items[0].title, table: g.items[0].table };
    const first = g.items[0].table;
    const xk = first.cols[0].key;
    const cols = [first.cols[0]];
    const rows = first.rows.map(r => ({ [xk]: r[xk] }));
    const seen = {};
    g.items.forEach((x, k) => {
      x.table.cols.slice(1).forEach(c => {
        const vals = x.table.rows.map(r => r[c.key]).join("|");
        const shared = c.label !== x.title && g.items.some((y, j) => j !== k && y.table.cols.some(cc => cc.label === c.label && y.table.rows.map(r => r[cc.key]).join("|") === vals));
        if (shared && seen[c.label]) return;
        const key = "m" + k + "_" + c.key;
        const label = shared ? c.label : (x.table.cols.length === 2 ? x.title : x.title + " · " + c.label);
        if (shared) seen[c.label] = true;
        cols.push({ key: key, label: label, num: c.num });
        x.table.rows.forEach((r, i) => { rows[i][key] = r[c.key]; });
      });
    });
    return { title: null, table: { cols: cols, rows: rows } };
  });
}
function renderTableView(card) {
  const tv = card.querySelector(".table-view");
  if (!tv) return;
  tv.replaceChildren();
  const list = [];
  Object.values(card._tables || {}).forEach(res => {
    if (res.tables) res.tables.forEach(x => { if (x.table) list.push(x); });
    else if (res.table) list.push({ title: null, table: res.table });
  });
  mergeTables(list).forEach((g, k) => {
    if (g.title) { const h = H("div", "cell-t", tv, g.title); h.style.cssText = "padding:10px 10px 4px;font-size:12.5px;font-weight:600"; }
    const box = H("div", null, tv);
    table(box, g.table.cols, g.table.rows);
  });
}

/* ------------------------------------------------------------------ registry */
const REG = {};
const ro = new ResizeObserver(entries => {
  entries.forEach(en => {
    const el = en.target;
    const w = Math.round(en.contentRect.width);
    if (el._w !== undefined && Math.abs(el._w - w) < 2) return;
    el._w = w;
    if (el._ready) { cancelAnimationFrame(el._raf); el._raf = requestAnimationFrame(() => el._render()); }
  });
});
function mount(el) {
  const fn = REG[el.dataset.chart];
  if (!fn) { console.warn("chart not registered:", el.dataset.chart); return; }
  const card = el.closest(".card");
  el._render = () => {
    const res = fn(el, card) || {};
    if (card) {
      card._tables = card._tables || {};
      card._tables[el.dataset.chart] = res;
      if (card._tableOpen) renderTableView(card);
    }
  };
  el._render();
  el._ready = true;
  el._w = Math.round(el.clientWidth);
  ro.observe(el);
}
function rerender(name) { document.querySelectorAll('[data-chart="' + name + '"]').forEach(el => el._render && el._render()); }

/* ================================================================== CHARTS */
const cleanMask = arr => arr.map((v, i) => (i >= CS ? v : null));
const cutStart = monthIdx(FACT.cut_start_ym);
const cutEnd = monthIdx(FACT.cut_end_ym);
const CUT = [{ from: cutStart, to: cutEnd, label: "post-cut" }];

// ---------------- 01 data
REG.entrySignature = (el, card) => {
  const rows = D.entrySignature;
  const labels = rows.map(r => mlab(r.cohort));
  const vals = rows.map(r => r.share);
  const colors = rows.map((r, i) => (i === 0 ? C.s1 : C.de));
  legend(card, [{ name: "Feb-22 entries (flagged)", color: C.s1 }, { name: "Later cohorts", color: C.de }], null);
  return barChart(el, {
    labels: labels, series: [{ name: "Share with 2× first payment", values: vals, colors: colors, fmt: v => f.pct(v) }],
    fmt: v => f.pct(v), tickKind: "pct", height: 250, xTitle: "Cohort",
    tipRows: i => [{ color: colors[i], kind: "rect", label: "first payment = 2× second", value: f.pct(vals[i]) },
                   { kind: "none", label: "customers", value: rows[i].first_amount_2x_next + " of " + rows[i].new_customers }],
  });
};
REG.examples = el => multiples(el, {
  cols: 2, minCellW: 250, height: 132,
  items: D.examples.map(ex => ({
    title: "Customer " + ex.id, right: ex.industry, note: ex.caption, kind: "bars",
    opts: { labels: LAB, series: [{ name: "Paid amount", values: ex.amounts_cop, color: C.s1 }], fmt: f.cop, tickKind: "cop",
            zeroMarks: true, ref: { value: ex.usual_cop, label: "usual " + f.cop(ex.usual_cop) } },
  })),
});
REG.amountHist = el => {
  const h = D.amountHist;
  const labels = h.counts.map((c, i) => compact(h.edges[i], 0) + "–" + compact(h.edges[i + 1], 0));
  const tot = sum(h.counts);
  return barChart(el, {
    labels: labels, series: [{ name: "Customer-months", values: h.counts, color: C.s1 }], fmt: f.int, tickKind: "int", height: 250, xTitle: "COP band",
    tipTitle: i => "COP " + labels[i],
    tipRows: i => [{ color: C.s1, kind: "rect", label: "customer-months", value: f.int(h.counts[i]) }, { kind: "none", label: "share of positive rows", value: f.pct(h.counts[i] / tot) }],
  });
};
REG.smShares = (el, card) => {
  const tot = M.total_sm_spend;
  const s = [
    { name: "Team", values: M.team.map((v, i) => v / tot[i]), color: C.s1 },
    { name: "PayrollExpenses", values: M.payroll_expenses.map((v, i) => v / tot[i]), color: C.s2 },
    { name: "Freelance", values: M.freelance.map((v, i) => v / tot[i]), color: C.s3 },
  ];
  legend(card, s.map(x => ({ name: x.name, color: x.color, kind: "line" })), el);
  return lineChart(el, { labels: LAB, series: s, fmt: v => f.pct(v), tickKind: "pct", height: 250,
    shades: [{ from: monthIdx(FACT.team_break_ym), to: N - 1, label: "from " + FACT.team_break }],
    extraRows: i => [{ kind: "none", label: "Total S&M", value: f.u(tot[i]) }] });
};

// ---------------- 02 growth
REG.growthIndex = (el, card) => {
  const a0 = M.active_customers[0], m0 = M.total_paid_mrr_cop[0], r0 = M.mrr_per_active_customer_cop[0];
  const s = [
    { name: "Active customers", short: "Customers", values: M.active_customers.map(v => 100 * v / a0), color: C.s1, tip: (i, v) => f.idx(v) + " · " + f.int(M.active_customers[i]) },
    { name: "Paid MRR", short: "Paid MRR", values: M.total_paid_mrr_cop.map(v => 100 * v / m0), color: C.s2, tip: (i, v) => f.idx(v) + " · " + f.cop(M.total_paid_mrr_cop[i]) },
    { name: "MRR per active customer", short: "MRR / customer", values: M.mrr_per_active_customer_cop.map(v => 100 * v / r0), color: C.s7, tip: (i, v) => f.idx(v) + " · " + f.cop(M.mrr_per_active_customer_cop[i]) },
  ];
  legend(card, s.map(x => ({ name: x.name, color: x.color, kind: "line" })), el);
  return lineChart(el, { labels: LAB, series: s, fmt: f.idx, tickKind: "idx", height: 330, ref: { value: 100 },
    endLabels: true, endLabelFmt: (x, v) => x.short + " " + v.toFixed(0) });
};
REG.customerFlows = (el, card) => {
  const idx = range(1, N);
  const s = [
    { name: "New", values: idx.map(i => M.new_customers[i]), color: MOV.New },
    { name: "Reactivated", values: idx.map(i => M.reactivated_customers[i]), color: MOV.Reactivation },
    { name: "Churned (observed)", values: idx.map(i => -M.churned_customers[i]), color: MOV.Churn, fmt: v => f.int(Math.abs(v)) },
  ];
  const line = { name: "Net adds", values: idx.map(i => M.net_customer_adds[i]), color: C.ink };
  legend(card, s.map(x => ({ name: x.name, color: x.color })).concat([{ name: line.name, color: line.color, kind: "line" }]), el);
  return barChart(el, { labels: idx.map(i => LAB[i]), series: s, stacked: true, line: line, fmt: f.int, tickKind: "int", height: 310,
    dim: [0], dimNote: "Feb-22: includes suspected left-censoring spillover (excluded from rates).",
    extraRows: i => [{ kind: "none", label: "active customers", value: f.int(M.active_customers[i + 1]) }] });
};
REG.mrrLevel = (el, card) => {
  const s = [
    { name: "Paid MRR", values: M.total_paid_mrr_cop, color: C.s1 },
    { name: "3-month average", values: M.total_paid_mrr_cop_3m_avg, color: C.de, width: 2.6 },
  ];
  legend(card, s.map(x => ({ name: x.name, color: x.color, kind: "line" })), el);
  return lineChart(el, { labels: LAB, series: s, fmt: f.cop, tickKind: "cop", height: 310,
    extraRows: i => i > 0 ? [{ kind: "none", label: "vs previous month", value: f.pctSigned(M.total_paid_mrr_cop[i] / M.total_paid_mrr_cop[i - 1] - 1) }] : [] });
};

// ---------------- 03 monetization
REG.ticketMonthly = (el, card) => {
  const s = [
    { name: "Mean (New MRR ÷ new customers)", values: cleanMask(M.new_mrr_per_new_customer_cop), color: C.s1 },
    { name: "Median", values: cleanMask(M.median_new_customer_mrr_cop), color: C.s2 },
  ];
  const band = { name: "P25–P75", lower: cleanMask(M.p25_new_customer_mrr_cop), upper: cleanMask(M.p75_new_customer_mrr_cop), color: C.s2 };
  legend(card, s.map(x => ({ name: x.name, color: x.color, kind: "line" })).concat([{ name: "P25–P75", color: C.s2, kind: "rect wash" }]), el);
  return lineChart(el, { labels: LAB, series: s, band: band, fmt: f.cop, tickKind: "cop", height: 330,
    flags: [{ i: monthIdx(FACT.step_month_ym), label: "step · " + FACT.step_month }],
    extraRows: i => i >= CS ? [{ kind: "none", label: "new customers", value: f.int(M.new_customers[i]) }, { kind: "none", label: "P90", value: f.cop(M.p90_new_customer_mrr_cop[i]) }] : [],
    tipNote: i => i < CS ? "Not computed: " + (i === 0 ? "left-censored month" : "suspected spillover") : null });
};
REG.priceBands = (el, card) => {
  const b = D.ticket.bands;
  const nm = y => (y === 2022 ? "2022 (Mar–Dec)" : y === 2024 ? "2024 (Jan–Oct)" : String(y));
  const s = b.years.map((y, k) => ({ name: nm(y), values: b.shares[k], color: YEARC[y] }));
  legend(card, s.map(x => ({ name: x.name, color: x.color })), el);
  return barChart(el, { labels: b.labels, series: s, fmt: v => f.pct(v), tickKind: "pct", height: 290, xTitle: "First-month MRR band (COP)",
    tipTitle: i => "COP " + b.labels[i],
    tipRows: i => s.filter(x => !(el._hidden && el._hidden.has(x.name))).map(x => { const k = s.indexOf(x); return { color: x.color, kind: "rect", label: x.name, value: f.pct(x.values[i]) + " · " + b.counts[k][i] }; }) });
};
REG.vintageArpa = (el, card) => {
  const V = D.vintage;
  const order = [["Base (active Jan-22)", "Base", C.r250], ["2022 (Mar–Dec)", "2022", C.r400], ["2023", "2023", C.r550], ["2024", "2024", C.r700]];
  const s = order.map(o => ({ name: o[0], short: o[1], color: o[2], values: V[o[0]].arpa.map((v, i) => (V[o[0]].active[i] >= 30 ? v : null)),
    tip: (i, v) => f.cop(v) + " · " + f.int(V[o[0]].active[i]) + " cust." }));
  const co = { name: "Company average", short: "All", color: C.de, width: 1.6, values: M.mrr_per_active_customer_cop, tip: (i, v) => f.cop(v) };
  const all = s.concat([co]);
  legend(card, all.map(x => ({ name: x.name, color: x.color, kind: "line" })), el);
  return lineChart(el, { labels: LAB, series: all, fmt: f.cop, tickKind: "cop", height: 300, endLabels: true, endLabelFmt: (x, v) => x.short + " " + f.cop(v).replace("COP ", ""),
    tipNote: () => "Vintage shown once it has ≥ 30 active customers." });
};

// ---------------- 04 S&M
REG.smStack = (el, card) => {
  const s = [
    { name: "Demand Gen", values: M.demand_gen_spend, color: C.s1 },
    { name: "Sales / Acquisition capacity", values: M.sales_capacity_spend, color: C.s2 },
    { name: "Enablement", values: M.enablement_spend, color: C.s3 },
  ];
  legend(card, s.map(x => ({ name: x.name, color: x.color })), el);
  return barChart(el, { labels: LAB, series: s, stacked: true, fmt: v => f.u(v), tickKind: "u", height: 310, shades: CUT,
    showTotal: true, totalLabel: "Total S&M",
    extraRows: i => [{ kind: "none", label: "Total ex-Payroll", value: f.u(M.total_sm_ex_payroll[i]) }] });
};
REG.smComponents = el => {
  const comps = [
    ["PaidMedia", "paid_media", C.s1, "Demand Gen"], ["PublicidadNoWeb", "publicidad_no_web", C.s1, "Demand Gen"],
    ["Team", "team", C.s2, "Sales capacity"], ["PayrollExpenses", "payroll_expenses", C.s2, "Sales capacity"], ["Travel", "travel", C.s2, "Sales capacity"],
    ["SoftwareTools", "software_tools", C.s3, "Enablement"], ["Freelance", "freelance", C.s3, "Enablement"],
  ];
  const notes = {
    Team: "12.0% of total until " + FACT.team_fixed_until + ", flat after",
    PayrollExpenses: "negative in " + FACT.payroll_neg_n + " months",
    Freelance: "0 from " + FACT.freelance_zero_from + " (except " + FACT.freelance_exceptions + ")",
    PaidMedia: FACT.pm_drop + " peak-to-trough in 2023",
  };
  return multiples(el, { cols: 4, minCellW: 220, height: 140, items: comps.map(c => ({
    title: c[0], right: c[3], note: notes[c[0]] || "", kind: "bars",
    opts: { labels: LAB, series: [{ name: c[0], values: M[c[1]], color: c[2] }], fmt: v => f.u(v), tickKind: "u", shades: CUT },
  })) });
};
REG.alignedPanels = el => {
  const items = [
    ["Paid Media (u)", "bars", M.paid_media, C.s2, v => f.u(v), "u"], ["New customers", "bars", cleanMask(M.new_customers), C.s1, f.int, "int"],
    ["Demand Gen (u)", "bars", M.demand_gen_spend, C.s2, v => f.u(v), "u"], ["New MRR (COP)", "bars", cleanMask(M.new_mrr_cop), C.s1, f.cop, "cop"],
    ["Total S&M (u)", "bars", M.total_sm_spend, C.s2, v => f.u(v), "u"], ["Net customer adds", "bars", cleanMask(M.net_customer_adds), C.s1, f.int, "int"],
    ["Sales / Acquisition capacity (u)", "bars", M.sales_capacity_spend, C.s2, v => f.u(v), "u"], ["Total paid MRR (COP)", "line", M.total_paid_mrr_cop, C.s1, f.cop, "cop"],
  ];
  return multiples(el, { cols: 2, minCellW: 300, height: 128, items: items.map(it => ({
    title: it[0], kind: it[1],
    opts: { labels: LAB, xMode: "band", series: [{ name: it[0], values: it[2], color: it[3] }], fmt: it[4], tickKind: it[5], shades: CUT, includeZero: true },
  })) });
};
REG.indexOverlay = (el, card) => {
  const I = D.index;
  const s = [
    { name: "Total S&M", short: "Total S&M", values: I.total_sm_spend_t3m, color: C.s2 },
    { name: "New customers", short: "New customers", values: I.new_customers_t3m, color: C.s1 },
    { name: "New MRR", short: "New MRR", values: I.new_mrr_cop_t3m, color: C.s3 },
  ];
  legend(card, s.map(x => ({ name: x.name, color: x.color, kind: "line" })), el);
  return lineChart(el, { labels: LAB, series: s, fmt: f.idx, tickKind: "idx", height: 310, ref: { value: 100 },
    shades: CUT, endLabels: true, endLabelFmt: (x, v) => x.short + " " + v.toFixed(0) });
};
REG.efficiency = (el, card) => {
  const items = [
    ["Total S&M / new customer", "total_sm_per_new_customer", "u"], ["Demand Gen / new customer", "demand_gen_per_new_customer", "u"], ["Paid Media / new customer", "paid_media_per_new_customer", "u"],
    ["Total S&M / COP 1M New MRR", "total_sm_per_new_mrr_mm_cop", "u"], ["Demand Gen / COP 1M New MRR", "demand_gen_per_new_mrr_mm_cop", "u"], ["Paid Media / COP 1M New MRR", "paid_media_per_new_mrr_mm_cop", "u"],
  ];
  legend(card, [{ name: "Monthly ratio", color: C.s1 }, { name: "Trailing 3 months", color: C.ink, kind: "line" }], null);
  const res = multiples(el, { cols: 3, minCellW: 250, height: 150, items: items.map(it => ({
    title: it[0], right: U,
    kind: "bars",
    opts: { labels: LAB, series: [{ name: it[0], values: M[it[1]], color: C.s1 }], line: { name: "Trailing 3 months", values: M[it[1] + "_t3m"], color: C.ink },
            fmt: v => f.u(v, 3), tickKind: "u", shades: CUT,
            tipNote: i => M.efficiency_status[i] !== "ok" ? "Not computed: " + M.efficiency_status[i].replace(/_/g, " ") : null },
  })) });
  const inv = { title: "Inverses", table: { cols: [{ key: "m", label: "Month" }, { key: "a", label: "New customers per 1 u Total S&M", num: true }, { key: "b", label: "New MRR (COP) per 1 u Total S&M", num: true }, { key: "c", label: "New customers per 1 u Demand Gen", num: true }, { key: "d", label: "New MRR (COP) per 1 u Demand Gen", num: true }, { key: "s", label: "Status" }],
    rows: LAB.map((l, i) => ({ m: l, a: f.num(M.new_customers_per_sm_unit[i], 1), b: f.copFull(M.new_mrr_cop_per_sm_unit[i]), c: f.num(M.new_customers_per_demand_gen_unit[i], 1), d: f.copFull(M.new_mrr_cop_per_demand_gen_unit[i]), s: M.efficiency_status[i] })) } };
  res.tables.push(inv);
  return res;
};

// ---------------- 05 relationships
const corrState = { spend: "Total S&M", outcome: "New customers", lag: 0, transform: "Levels" };
function corrPairs(st) {
  const s = D.corr.spend[st.spend], o = D.corr.outcome[st.outcome], k = st.lag, out = [];
  for (let t = CS; t < N; t++) {
    if (st.transform === "Levels") { if (t - k < 0) continue; out.push({ t: t, x: s[t - k], y: o[t] }); }
    else { if (t - 1 < CS || t - k - 1 < 0) continue; out.push({ t: t, x: s[t - k] - s[t - k - 1], y: o[t] - o[t - 1] }); }
  }
  return out;
}
function corrRow(st) {
  const tr = st.transform === "Levels" ? "levels" : "mom_change";
  return D.corr.rows.find(r => r.spend === st.spend && r.outcome === st.outcome && r.lag_months === st.lag && r.transform === tr);
}
function corrHeadline(st, r) {
  const lagTxt = st.lag === 0 ? "the same month" : st.lag + (st.lag === 1 ? " month" : " months") + " earlier";
  const what = st.transform === "Levels" ? "" : " (month-over-month changes)";
  const out = st.outcome === "New MRR" ? "New MRR" : st.outcome.toLowerCase();
  if (r.pearson_p < 0.05 && r.pearson_r < 0) return "Higher " + st.spend + " " + lagTxt + " is associated with fewer " + out + what;
  if (r.pearson_p < 0.05 && r.pearson_r > 0) return "Higher " + st.spend + " " + lagTxt + " moves together with more " + out + what;
  return "No clear relationship observed between " + st.spend + " " + lagTxt + " and " + out + what;
}
function updateCorrText() {
  const r = corrRow(corrState);
  const pairs = corrPairs(corrState);
  if (r.n !== pairs.length) console.error("n mismatch", r.n, pairs.length);
  document.getElementById("scatterTitle").textContent = corrHeadline(corrState, r);
  document.getElementById("scatterSub").textContent = "Each dot is an outcome month (" + mlab(r.window.split("..")[0]) + " → " + mlab(r.window.split("..")[1]) + "). x = " + corrState.spend + " in t−" + corrState.lag + (corrState.transform === "Levels" ? "" : " (change vs previous month)") + ".";
  document.getElementById("lagTitle").textContent = corrState.spend + " (t−" + corrState.lag + ") and " + corrState.outcome + " (t), standardised";
  const st = document.getElementById("corrStats");
  st.replaceChildren();
  [["Pearson r", f.r(r.pearson_r), "p = " + f.p(r.pearson_p)], ["Spearman ρ", f.r(r.spearman_rho), "p = " + f.p(r.spearman_p)], ["Months (n)", String(r.n), corrState.transform === "Levels" ? "levels" : "MoM changes"]].forEach(x => {
    const d = H("div", "stat", st); H("div", "k", d, x[0]); H("div", "v", d, x[1]); H("div", "s", d, x[2]);
  });
}
REG.scatter = el => {
  const st = corrState;
  const pairs = corrPairs(st);
  const isMRR = st.outcome === "New MRR";
  const lev = st.transform === "Levels";
  return scatter(el, {
    points: pairs.map(p => ({ x: p.x, y: p.y, label: LAB[p.t] + (st.lag ? " · spend from " + LAB[p.t - st.lag] : "") })),
    xFmt: v => f.u(v), yFmt: isMRR ? f.cop : f.int, xKind: "u", yKind: isMRR ? "cop" : "int",
    xName: st.spend + " (t−" + st.lag + ")" + (lev ? "" : " Δ"), yName: st.outcome + (lev ? "" : " Δ"),
    xTitle: st.spend + " in t−" + st.lag + (lev ? " (u)" : ", change vs previous month (u)"),
    yTitle: st.outcome + (lev ? "" : " — change vs previous month") + (isMRR ? " (COP)" : ""), color: C.s1, height: 330,
  });
};
REG.lagSeries = (el, card) => {
  const st = corrState;
  const pairs = corrPairs(st);
  const z = a => { const m = a.reduce((s, v) => s + v, 0) / a.length; const sd = Math.sqrt(a.reduce((s, v) => s + (v - m) ** 2, 0) / (a.length - 1)) || 1; return a.map(v => (v - m) / sd); };
  const zx = z(pairs.map(p => p.x)), zy = z(pairs.map(p => p.y));
  const xs = new Array(N).fill(null), ys = new Array(N).fill(null);
  pairs.forEach((p, k) => { xs[p.t] = zx[k]; ys[p.t] = zy[k]; });
  const s = [
    { name: st.spend + " (t−" + st.lag + ")", values: xs, color: C.s2, tip: (i, v) => f.z(v) + " · " + f.u(pairs.find(p => p.t === i).x) },
    { name: st.outcome + " (t)", values: ys, color: C.s1, tip: (i, v) => f.z(v) + " · " + (st.outcome === "New MRR" ? f.cop : f.int)(pairs.find(p => p.t === i).y) },
  ];
  legend(card, s.map(x => ({ name: x.name, color: x.color, kind: "line" })), null);
  return lineChart(el, { labels: LAB, series: s, fmt: f.z, tickKind: "z", height: 330, includeZero: true });
};
function corrHeat(el, transform) {
  const combos = [];
  ["New customers", "New MRR"].forEach(o => ["Paid Media", "Demand Gen", "Total S&M"].forEach(s => combos.push([s, o])));
  const tr = transform === "Levels" ? "levels" : "mom_change";
  const find = (s, o, k) => D.corr.rows.find(r => r.spend === s && r.outcome === o && r.lag_months === k && r.transform === tr);
  const values = combos.map(c => [0, 1, 2, 3].map(k => find(c[0], c[1], k).pearson_r));
  let selected = null;
  if (corrState.transform === transform) selected = [combos.findIndex(c => c[0] === corrState.spend && c[1] === corrState.outcome), corrState.lag];
  return heatmap(el, {
    rows: combos.map(c => c[0] + " vs " + c[1]), cols: ["t", "t−1", "t−2", "t−3"], values: values, rowTitle: "Spend vs outcome",
    color: divColor, text: v => f.r(v), fmt: f.r, cellH: 34, minTextW: 30, selected: selected,
    textStrong: (i, j) => find(combos[i][0], combos[i][1], j).pearson_p < 0.05,
    tip: (i, j) => { const r = find(combos[i][0], combos[i][1], j); return { title: combos[i][0] + " (t−" + j + ") vs " + combos[i][1] + " (t)", rows: [
      { kind: "none", label: "Pearson r", value: f.r(r.pearson_r) + "  (p " + f.p(r.pearson_p) + ")" },
      { kind: "none", label: "Spearman ρ", value: f.r(r.spearman_rho) + "  (p " + f.p(r.spearman_p) + ")" },
      { kind: "none", label: "months", value: String(r.n) }], note: "Click to inspect in the scatter." }; },
    onPick: (i, j) => { setCorr({ spend: combos[i][0], outcome: combos[i][1], lag: j, transform: transform }); },
  });
}
REG.corrLevels = el => {
  const res = corrHeat(el, "Levels");
  const sens = D.corr.sens.filter(r => r.transform === "levels");
  res.tables = [{ title: "Levels (clean window)", table: res.table }, { title: "Sensitivity: levels including Feb-22", table: {
    cols: [{ key: "a", label: "Spend vs outcome" }, { key: "k", label: "Lag", num: true }, { key: "r", label: "Pearson r", num: true }, { key: "n", label: "n", num: true }],
    rows: sens.map(r => ({ a: r.spend + " vs " + r.outcome, k: r.lag_months, r: f.r(r.pearson_r), n: r.n })) } }];
  delete res.table;
  return res;
};
REG.corrMom = el => {
  const res = corrHeat(el, "MoM change");
  const all = D.corr.rows;
  res.tables = [{ title: "Month-over-month changes", table: res.table }, { title: "All correlations (clean window)", table: {
    cols: [{ key: "a", label: "Spend vs outcome" }, { key: "t", label: "Transform" }, { key: "k", label: "Lag", num: true }, { key: "n", label: "n", num: true },
           { key: "r", label: "Pearson r", num: true }, { key: "rp", label: "p", num: true }, { key: "s", label: "Spearman ρ", num: true }, { key: "sp", label: "p", num: true }],
    rows: all.map(r => ({ a: r.spend + " vs " + r.outcome, t: r.transform, k: r.lag_months, n: r.n, r: f.r(r.pearson_r), rp: f.p(r.pearson_p), s: f.r(r.spearman_rho), sp: f.p(r.spearman_p) })) } }];
  delete res.table;
  return res;
};
function setCorr(patch) {
  Object.assign(corrState, patch);
  document.querySelectorAll("#corrControls .seg").forEach(seg => {
    const key = seg.dataset.key;
    seg.querySelectorAll("button").forEach(b => {
      const val = key === "lag" ? Number(b.textContent) : b.textContent;
      b.setAttribute("aria-pressed", String(val === corrState[key]));
    });
  });
  updateCorrText();
  ["scatter", "lagSeries", "corrLevels", "corrMom"].forEach(rerender);
}

// ---------------- 06 industries
function shareBars(el, card, labels, getShare, getAbs, absFmt, height) {
  const s = IND.map(ind => ({ name: ind, values: getShare(ind), color: INDC[ind] }));
  legend(card, s.map(x => ({ name: x.name, color: x.color })), null);
  return barChart(el, { labels: labels, series: s, stacked: true, fmt: v => f.pct(v), tickKind: "pct", height: height || 290, yMin: 0, yMax: 1, maxBar: labels.length <= 8 ? 34 : 26,
    tipRows: i => IND.slice().reverse().map(ind => ({ color: INDC[ind], kind: "rect", label: ind, value: f.pct(getShare(ind)[i]) + " · " + absFmt(getAbs(ind)[i]) })) });
}
REG.mixActive = (el, card) => shareBars(el, card, LAB, ind => D.industry.monthly[ind].share_active_customers, ind => D.industry.monthly[ind].active_customers, f.int);
REG.mixMrr = (el, card) => shareBars(el, card, LAB, ind => D.industry.monthly[ind].share_mrr, ind => D.industry.monthly[ind].total_paid_mrr_cop, f.cop);
REG.mixNewHalf = (el, card) => shareBars(el, card, D.industry.halves, ind => D.industry.half[ind].share_new_customers, ind => D.industry.half[ind].new_customers, f.int);
REG.mixNewMrrHalf = (el, card) => shareBars(el, card, D.industry.halves, ind => D.industry.half[ind].share_new_mrr, ind => D.industry.half[ind].new_mrr_cop, f.cop);
function ticketInd(el, card, kind) {
  const Y = D.industry.year;
  const nm = y => (y === 2022 ? "2022 (Mar–Dec)" : y === 2024 ? "2024 (Jan–Oct)" : String(y));
  const s = [2022, 2023, 2024].map(y => ({ name: nm(y), color: YEARC[y], values: IND.map(ind => kind === "mean"
    ? (Y.find(r => r.year === y && r.industry === ind) || {}).new_mrr_per_new_customer_cop
    : D.decomp.medians[y][ind]) }));
  if (kind === "mean") legend(card, s.map(x => ({ name: x.name, color: x.color, kind: "dot" })), null);
  const counts = y => IND.map(ind => (Y.find(r => r.year === y && r.industry === ind) || {}).new_customers);
  const head = H("div", "cell-t", null, kind === "mean" ? "Mean" : "Median");
  const res = dots(el, { rows: IND, series: s, fmt: f.cop, tickKind: "cop", rowTitle: "Industry",
    note: i => "New customers: " + [2022, 2023, 2024].map(y => y + " " + counts(y)[i]).join(" · ") });
  el.prepend(head);
  res.tables = [{ title: kind === "mean" ? "Mean New MRR per new customer" : "Median first-month MRR", table: res.table }];
  delete res.table;
  return res;
}
REG.ticketIndMean = (el, card) => ticketInd(el, card, "mean");
REG.ticketIndMedian = (el, card) => ticketInd(el, card, "median");
REG.arpaIndustry = el => multiples(el, { cols: 3, minCellW: 250, height: 150, sharedY: true, items: IND.map(ind => ({
  title: ind, right: D.industry.en[ind] !== ind ? D.industry.en[ind] : "", kind: "line",
  opts: { labels: LAB, series: [
    { name: ind, values: D.industry.monthly[ind].mrr_per_active_customer_cop, color: INDC[ind] },
    { name: "Company", values: M.mrr_per_active_customer_cop, color: C.de, width: 1.5 }], fmt: f.cop, tickKind: "cop" },
})) });

// ---------------- 07 decomposition
REG.decompWaterfall = el => {
  const d = D.decomp.main["2022_2024"];
  return waterfall(el, { title: "2022 → 2024 entry ticket", height: 320, fmt: f.cop, steps: [
    { label: "2022\nMar–Dec", value: d.A0, kind: "total", color: C.de, extra: [{ kind: "none", label: "new customers", value: f.int(d.n0) }] },
    { label: "Industry\nmix", value: d.mix, kind: "delta", color: C.s2, note: "90% interval: " + f.cop(d.mix_ci90_lo) + " to " + f.cop(d.mix_ci90_hi) },
    { label: "Within\nindustries", value: d.within, kind: "delta", color: C.s1, note: "90% interval: " + f.cop(d.within_ci90_lo) + " to " + f.cop(d.within_ci90_hi) },
    { label: "2024\nJan–Oct", value: d.A1, kind: "total", color: C.de, extra: [{ kind: "none", label: "new customers", value: f.int(d.n1) }] },
  ] });
};
REG.decompEvolution = (el, card) => {
  const E = D.decomp.evolution;
  const s = [
    { name: "Within industries", values: E.map(e => e.within_cop), color: C.s1 },
    { name: "Industry mix", values: E.map(e => e.mix_cop), color: C.s2 },
  ];
  const line = { name: "Total gap vs 2022", values: E.map(e => e.gap_vs_2022_cop), color: C.ink };
  legend(card, s.map(x => ({ name: x.name, color: x.color })).concat([{ name: line.name, color: line.color, kind: "line" }]), el);
  return barChart(el, { labels: E.map(e => e.half), series: s, stacked: true, line: line, fmt: f.cop, tickKind: "cop", height: 320, maxBar: 34,
    extraRows: i => [{ kind: "none", label: "average ticket", value: f.cop(E[i].mean_m0_cop) }, { kind: "none", label: "median ticket", value: f.cop(E[i].median_m0_cop) }, { kind: "none", label: "new customers", value: f.int(E[i].n) }] });
};

// ---------------- 08 cohorts
const cohState = { metric: "Logo retention", gran: "Quarterly" };
const METRIC = {
  "Logo retention": { key: "logo", fmt: v => f.pct(v), sfmt: v => f.pct(v, 0), dom: [0.6, 1], kind: "pct", title: "Share of each cohort still paying, by months since first payment" },
  "Revenue retention vs M0": { key: "revenue", fmt: v => f.pct(v), sfmt: v => f.pct(v, 0), dom: [0.3, 1.1], kind: "pct", title: "Cohort MRR as a share of the same customers' M0 MRR" },
  "MRR per original customer": { key: "arpu", fmt: f.cop, dom: null, kind: "cop", title: "Cohort MRR divided by the customers observable at each month (COP)" },
};
function cohortRows() {
  const Q = D.cohorts.quarterly, Mo = D.cohorts.monthly;
  if (cohState.gran === "Quarterly") return Q.map(q => ({ label: q.cohort + (q.partial ? "*" : ""), size: q.size, data: q, obs: q.observable }));
  return Mo.map(m => ({ label: mlab(m.cohort) + (m.flag !== "clean" ? " ⚑" : ""), size: m.size, data: m, obs: null }));
}
function scaleLegend(target, dom, fmt, ramp) {
  target.replaceChildren();
  const wrap = H("div", null, target);
  wrap.style.cssText = "display:flex;align-items:center;gap:10px;font-size:11.5px;color:var(--muted)";
  H("span", null, wrap, fmt(dom[0]));
  const bar = H("span", null, wrap);
  bar.style.cssText = "width:180px;height:10px;border-radius:6px;background:linear-gradient(90deg," + ramp.join(",") + ")";
  H("span", null, wrap, fmt(dom[1]) + (cohState.metric === "Revenue retention vs M0" ? "+" : ""));
}
REG.cohortHeat = (el, card) => {
  const mt = METRIC[cohState.metric];
  const rows = cohortRows();
  const maxK = Math.max(...rows.map(r => r.data[mt.key].length));
  const cols = range(0, maxK).map(k => "M" + k);
  const values = rows.map(r => cols.map((c, k) => r.data[mt.key][k] === undefined ? null : r.data[mt.key][k]));
  let dom = mt.dom;
  if (!dom) { const vs = values.flat().filter(ok); dom = [Math.min(...vs), Math.max(...vs)]; }
  document.getElementById("cohortHeatTitle").textContent = cohState.metric + " · " + cohState.gran.toLowerCase() + " cohorts";
  document.getElementById("cohortHeatSub").textContent = mt.title + ". Rows = cohorts (n in tooltip); columns = months since first payment.";
  scaleLegend(document.getElementById("cohortScale"), dom, mt.sfmt || mt.fmt, SEQ);
  return heatmap(el, { rows: rows.map(r => r.label), cols: cols, values: values, rowTitle: "Cohort", color: v => seqColor(v, dom[0], dom[1]),
    text: cohState.gran === "Quarterly" ? (v => cohState.metric === "MRR per original customer" ? compact(v, 0) : (v * 100).toFixed(0)) : null,
    minTextW: 26, fmt: mt.fmt, cellH: cohState.gran === "Quarterly" ? 26 : 15, highlightCols: [1, 3, 6, 12, 24],
    tip: (i, j, v) => ({ title: rows[i].label + " · M" + j, rows: [
      { kind: "none", label: cohState.metric, value: mt.fmt(v) },
      { kind: "none", label: "cohort size", value: f.int(rows[i].size) }].concat(rows[i].obs ? [{ kind: "none", label: "observable at M" + j, value: f.int(rows[i].obs[j]) }] : []),
      note: rows[i].label.includes("⚑") ? "Flagged: suspected left-censoring spillover." : null }) });
};
REG.cohortCurves = (el, card) => {
  const mt = METRIC[cohState.metric];
  const Yr = D.cohorts.yearly;
  const cols = ["2022", "2023", "2024"].map(y => YEARC[y]);
  const maxK = Math.max(...Yr.map(y => y[mt.key].length));
  const labels = range(0, maxK).map(k => "M" + k);
  const s = Yr.map((y, i) => ({ name: y.cohort + " · n " + f.int(y.size), short: y.cohort.slice(0, 4), color: cols[i],
    values: labels.map((l, k) => (y.observable[k] >= 40 ? y[mt.key][k] : null)),
    tip: (k, v) => mt.fmt(v) + " · " + f.int(y.observable[k]) + " obs." }));
  document.getElementById("cohortCurveTitle").textContent = cohState.metric + " by acquisition year";
  legend(card, s.map(x => ({ name: x.name, color: x.color, kind: "line" })), el);
  return lineChart(el, { labels: labels, series: s, fmt: mt.fmt, tickKind: mt.kind, height: 300, includeZero: cohState.metric === "MRR per original customer",
    endLabels: true, endLabelFmt: (x, v) => x.short + " " + mt.fmt(v), xTitle: "Months since first payment" });
};
REG.baseCurves = (el, card) => {
  const B = D.cohorts.flagged.left_censored_base;
  const s = [
    { name: "Still paying (logo)", short: "Logo", values: B.logo_calendar, color: C.s1 },
    { name: "Jan-22 MRR retained (revenue)", short: "Revenue", values: B.revenue_calendar, color: C.s2 },
  ];
  legend(card, s.map(x => ({ name: x.name, color: x.color, kind: "line" })), el);
  return lineChart(el, { labels: LAB, series: s, fmt: v => f.pct(v), tickKind: "pct", height: 300, includeZero: false, ref: { value: 1 },
    endLabels: true, endLabelFmt: (x, v) => x.short + " " + f.pct(v, 0),
    extraRows: i => [{ kind: "none", label: "MRR of this group", value: f.cop(B.mrr_calendar_cop[i]) }] });
};
function setCoh(patch) {
  Object.assign(cohState, patch);
  document.querySelectorAll("#cohortControls .seg").forEach(seg => {
    const key = seg.dataset.key;
    seg.querySelectorAll("button").forEach(b => b.setAttribute("aria-pressed", String(b.textContent === cohState[key])));
  });
  ["cohortHeat", "cohortCurves"].forEach(rerender);
}

// ---------------- 09 movements
REG.bridgeMonthly = (el, card) => {
  const idx = range(1, N);
  const s = [
    { name: "New", values: idx.map(i => M.new_mrr_cop[i]), color: MOV.New },
    { name: "Expansion", values: idx.map(i => M.expansion_mrr_cop[i]), color: MOV.Expansion },
    { name: "Reactivation", values: idx.map(i => M.reactivation_mrr_cop[i]), color: MOV.Reactivation },
    { name: "Contraction", values: idx.map(i => M.contraction_mrr_cop[i]), color: MOV.Contraction },
    { name: "Churn", values: idx.map(i => M.churned_mrr_cop[i]), color: MOV.Churn },
  ];
  const line = { name: "Net change", values: idx.map(i => M.net_mrr_change_cop[i]), color: C.ink };
  legend(card, s.map(x => ({ name: x.name, color: x.color })).concat([{ name: line.name, color: line.color, kind: "line" }]), el);
  return barChart(el, { labels: idx.map(i => LAB[i]), series: s, stacked: true, line: line, fmt: f.cop, tickKind: "cop", height: 340,
    dim: [0], dimNote: "Feb-22: New MRR includes suspected spillover.",
    extraRows: i => [{ kind: "none", label: "MRR at month end", value: f.cop(M.total_paid_mrr_cop[i + 1]) }, { kind: "none", label: "bridge residual", value: "COP " + Math.abs(M.mrr_bridge_diff_cop[i + 1]).toFixed(2) }] });
};
REG.bridgeLast = el => {
  const b = D.bridge.last;
  const steps = [
    { label: mlab(b.from_month) + "\nMRR", value: b.opening_mrr_cop, kind: "total", color: C.de },
    { label: "New", value: b.new_mrr_cop, kind: "delta", color: MOV.New },
    { label: "Expansion", value: b.expansion_mrr_cop, kind: "delta", color: MOV.Expansion },
    { label: "Reactivation", value: b.reactivation_mrr_cop, kind: "delta", color: MOV.Reactivation },
    { label: "Contraction", value: b.contraction_mrr_cop, kind: "delta", color: MOV.Contraction },
    { label: "Churn", value: b.churned_mrr_cop, kind: "delta", color: MOV.Churn },
    { label: mlab(b.to_month) + "\nMRR", value: b.closing_mrr_cop, kind: "total", color: C.de },
  ];
  let run = 0, lo = Infinity, hi = -Infinity;
  steps.forEach(s => { if (s.kind === "total") run = s.value; else run += s.value; lo = Math.min(lo, run); hi = Math.max(hi, run); });
  const span = hi - lo;
  const yMin = niceTicks(lo - span * 0.9, hi, 5)[0];
  const st = document.getElementById("lastCheck");
  st.replaceChildren();
  [["Opening", f.cop2(b.opening_mrr_cop)], ["Net movements", f.copSigned(b.net_change_cop)], ["Closing", f.cop2(b.closing_mrr_cop)], ["Residual", "COP " + Math.abs(b.check_diff_cop).toFixed(2) + " ✓"]].forEach(x => {
    const d = H("div", "stat", st); H("div", "k", d, x[0]); H("div", "v", d, x[1]);
  });
  return waterfall(el, { steps: steps, yMin: Math.max(0, yMin), fmt: f.cop, height: 320, title: mlab(b.from_month) + " → " + mlab(b.to_month) });
};
REG.returnBuckets = (el, card) => {
  const mv = D.movements;
  const cols = [C.r700, C.r500, C.r400, C.r250, C.de];
  const tot = mv.returnCounts.map(r => sum(r));
  const s = mv.returnBuckets.map((b, j) => ({ name: b, values: mv.returnCounts.map((r, i) => r[j] / tot[i]), color: cols[j] }));
  legend(card, s.map(x => ({ name: x.name, color: x.color })), null);
  return barChart(el, { labels: mv.returnYears.map(String), series: s, stacked: true, yMin: 0, yMax: 1, fmt: v => f.pct(v), tickKind: "pct", height: 300, maxBar: 64, xTitle: "Year of churn",
    tipRows: i => s.slice().reverse().map((x, jj) => { const j = s.length - 1 - jj; return { color: x.color, kind: "rect", label: x.name, value: f.pct(x.values[i]) + " · " + mv.returnCounts[i][j] }; }),
    tipNote: i => tot[i] + " churn events in " + mv.returnYears[i] + (i === 0 ? " (from Feb-22)" : "") });
};
REG.smallAdjust = (el, card) => {
  const sm = D.movements.small;
  const halves = sm.map(r => r.half);
  const grid = D.movements.gridHalf;
  const s = [
    { name: "Expansion events < 10%", values: sm.map(r => r.expansion_small_share), color: MOV.Expansion, tip: (i, v) => f.pct(v, 0) + " · " + sm[i].expansion_small + " of " + sm[i].expansion_events },
    { name: "Contraction events < 10%", values: sm.map(r => r.contraction_small_share), color: MOV.Contraction, tip: (i, v) => f.pct(v, 0) + " · " + sm[i].contraction_small + " of " + sm[i].contraction_events },
    { name: "Customers paying off the COP 2,100 grid", values: halves.map(h => { const g = grid.find(x => x.half === h); return g ? 1 - g.share : null; }), color: C.s1 },
  ];
  legend(card, s.map(x => ({ name: x.name, color: x.color, kind: "line" })), el);
  return lineChart(el, { labels: halves, series: s.map(x => Object.assign({ dots: true }, x)), fmt: v => f.pct(v, 0), tickKind: "pct", height: 300, xTitle: "Half-year",
    extraRows: i => [{ kind: "none", label: "expansion MRR in small events", value: f.cop(sm[i].expansion_small_mrr_cop) + " of " + f.cop(sm[i].expansion_mrr_cop) }] });
};

/* ================================================================== TABLES (static) */
function buildTables() {
  const A = D.audit, at = A.transactions, ai = A.industry, as = A.sm, co = A.consistency;
  const yes = b => (b ? "yes" : "no");
  const auditRows = [
    { d: "Grain", t: "customer × month (snapshot)", i: "customer", s: "month" },
    { d: "Rows", t: f.int(at.rows) + " = " + f.int(at.customers) + " × " + at.months, i: f.int(ai.rows_read) + " read · " + f.int(ai.rows_valid) + " valid", s: String(as.rows) },
    { d: "Customers", t: f.int(at.customers), i: f.int(ai.unique_ids) + " (IDs " + ai.id_min + "–" + ai.id_max + ", contiguous: " + yes(ai.ids_contiguous_1_to_n) + ")", s: "–" },
    { d: "Time range", t: mlab(at.first_month) + " → " + mlab(at.last_month) + " (" + at.months + " months)", i: "–", s: mlab(as.first_month) + " → " + mlab(as.last_month) + " (" + as.months + ")" },
    { d: "Duplicates", t: at.duplicate_customer_month + " (ID, month) · " + at.duplicate_full_rows + " full rows", i: ai.duplicate_ids + " IDs", s: as.duplicate_months + " months" },
    { d: "Missing values", t: "0 (" + Object.values(at.empty_strings).reduce((a, b) => a + b, 0) + " empty strings)", i: ai.blank_rows + " fully blank row (removed)", s: String(as.missing_values) },
    { d: "Types raw → parsed", t: "text → int · month · float (exact to 1e-6)", i: "text → int · text", s: "text “$x.xxx” → float" },
    { d: "Zeros / negatives", t: f.int(at.zero_amount_rows) + " zero rows (" + f.pct(at.zero_share) + ") · " + at.negative_amounts + " negative", i: "–", s: "Freelance 0 in " + as.components.Freelance.zeros + " months · Payroll < 0 in " + as.components.PayrollExpenses.negatives },
    { d: "Obvious outliers", t: f.int(at.rows_above_iqr_fence) + " rows > Q3 + 3·IQR (" + at.customers_above_iqr_fence + " customers); max " + f.cop2(at.amount_max * D.meta.scaleToCop), i: "–", s: "Paid Media −71% in 3 months (2023)" },
    { d: "Decimal precision", t: Object.entries(at.decimal_places).map(e => e[0] + "d: " + f.int(e[1])).join(" · "), i: "–", s: "3 decimals" },
    { d: "Naming issues", t: "BOM in header · name says “Transactions”, grain is monthly", i: "BOM · “Cliente N” IDs · ES/EN headers", s: "BOM: " + yes(as.utf8_bom) + " · ES/EN component names" },
    { d: "Consistency", t: "IDs matched: " + f.pct(co.id_match_rate, 0), i: "IDs without transactions: " + co.industry_ids_without_tx.length, s: "Months identical to Transactions: " + yes(co.sm_months_equal_tx_months) },
  ];
  table(document.getElementById("auditTable"), [{ key: "d", label: "Check" }, { key: "t", label: "Transactions.csv" }, { key: "i", label: "Industry.csv" }, { key: "s", label: "S&M_spend.csv" }], auditRows);

  const comp = as.components;
  const g = [
    ["PaidMedia", "Demand Generation", "Media spend to generate demand", "–"],
    ["PublicidadNoWeb", "Demand Generation", "Offline / non-web advertising", "–"],
    ["Team", "Sales / Acquisition capacity", "People cost of the S&M team (assumed)", "12.0% of total until " + FACT.team_fixed_until],
    ["PayrollExpenses", "Sales / Acquisition capacity", "Payroll-related cost; may overlap Team", "negative in " + comp.PayrollExpenses.negatives + " months"],
    ["Travel", "Sales / Acquisition capacity", "Field / sales travel (assumed)", "–"],
    ["SoftwareTools", "Enablement / Support", "Tooling; may include non-S&M software", "–"],
    ["Freelance", "Enablement / Support", "External support (content, design, SDR?)", "0 in " + comp.Freelance.zeros + " months"],
  ];
  table(document.getElementById("smGroupTable"), [{ key: "c", label: "Component" }, { key: "g", label: "Analytical group" }, { key: "r", label: "Why (hypothesis)" }, { key: "mn", label: "Min", num: true }, { key: "mx", label: "Max", num: true }, { key: "a", label: "Anomaly" }],
    g.map(x => ({ c: x[0], g: x[1], r: x[2], mn: f.u(comp[x[0]].min), mx: f.u(comp[x[0]].max), a: x[3] })));

  const defs = [
    ["observed_amount", "Amount exactly as delivered in Transactions.csv (Finora units)."],
    ["paid_mrr_cop", "observed_amount × 10,000. Analytical definition; the field behaves like monthly collections."],
    ["active_customer", "paid_mrr_cop > 0 in the month."],
    ["previous_month_mrr · mrr_change", "Paid MRR in t−1 and curr − prev. Undefined in " + FACT.window_start + "."],
    ["first_positive_month · cohort_month", "First month with paid MRR > 0. " + FACT.window_start + " cohort = left-censored; Feb-22 = suspected spillover."],
    ["tenure_month", "Months since cohort month (M0 = first paying month); empty before it."],
    ["new_customer", "curr > 0 and never > 0 before. Not identifiable in " + FACT.window_start + "."],
    ["churned_customer", "prev > 0 and curr = 0 (observed churn — may be a pause or a missed payment)."],
    ["reactivated_customer", "curr > 0, prev = 0 and positive at some earlier month."],
    ["expanded_customer", "curr > prev > 0."],
    ["contracted_customer", "0 < curr < prev."],
    ["flat_customer", "curr = prev > 0 (exact, in micro-units)."],
    ["New / Expansion / Reactivation MRR", "curr for new and reactivated rows; curr − prev for expansions."],
    ["Contraction / Churned MRR", "curr − prev (negative) for contractions; −prev for churn. Bridge: ΔMRR = sum of the five."],
    ["MRR per active customer", "Total paid MRR ÷ active customers."],
    ["New MRR per new customer", "New MRR ÷ new customers (mean). Median and P25/P75/P90 over the same first amounts."],
    ["Logo churn rate", "Churned customers(t) ÷ active customers(t−1)."],
    ["Gross MRR churn rate", "Churned MRR(t) ÷ MRR(t−1). Expansion/contraction rates analogous."],
    ["Efficiency", "Spend (u) ÷ new customers, or ÷ New MRR in COP millions; T3M = trailing three-month sums."],
    ["Clean window", "Mar-22 → " + FACT.window_end + " for every flow-based metric (new customers, New MRR, rates, correlations, cohorts)."],
  ];
  const dt = table(document.getElementById("defsTable"), [{ key: "a", label: "Field / metric" }, { key: "b", label: "Definition" }], defs.map(x => ({ a: x[0], b: x[1] })));
  dt.classList.add("defs");

  const TB = D.ticket.byYear;
  const byY = y => TB.find(r => r.year === y);
  const tmetrics = [
    ["New customers (n)", "new_customers", f.int, false],
    ["M0 mean · requested metric", "m0_mean_cop", f.cop, true],
    ["M0 median", "m0_median_cop", f.cop, true],
    ["M0 P25", "m0_p25_cop", f.cop, true], ["M0 P75", "m0_p75_cop", f.cop, true], ["M0 P90", "m0_p90_cop", f.cop, true],
    ["M0 mean, winsorised at P99", "m0_winsor_mean_cop", f.cop, true],
    ["Early run-rate mean", "early_run_rate_mean_cop", f.cop, true],
    ["Early run-rate median", "early_run_rate_median_cop", f.cop, true],
    ["M1 mean (incl. zeros)", "m1_mean_cop", f.cop, true],
    ["Share with first-month spike (> 1.5× M1)", "share_first_month_spike", v => f.pct(v), false],
  ];
  table(document.getElementById("ticketTable"), [{ key: "m", label: "Metric" }, { key: "a", label: "2022 (Mar–Dec)", num: true }, { key: "b", label: "2023", num: true }, { key: "c", label: "2024 (Jan–Oct)", num: true }, { key: "d", label: "Δ 2022 → 2024", num: true }],
    tmetrics.map(x => ({ m: x[0], a: x[2](byY(2022)[x[1]]), b: x[2](byY(2023)[x[1]]), c: x[2](byY(2024)[x[1]]), d: x[3] ? f.pctSigned(byY(2024)[x[1]] / byY(2022)[x[1]] - 1) : "–" })));

  const E = D.efficiencyByYear;
  const eY = y => E.find(r => r.year === y);
  const em = [
    ["Total S&M / new customer", "total_sm_per_new_customer", v => f.u(v)], ["Demand Gen / new customer", "demand_gen_per_new_customer", v => f.u(v)], ["Paid Media / new customer", "paid_media_per_new_customer", v => f.u(v)],
    ["Total S&M / COP 1M New MRR", "total_sm_per_new_mrr_mm", v => f.u(v, 2)], ["Demand Gen / COP 1M New MRR", "demand_gen_per_new_mrr_mm", v => f.u(v, 2)], ["Paid Media / COP 1M New MRR", "paid_media_per_new_mrr_mm", v => f.u(v, 2)],
  ];
  const erows = em.map(x => ({ m: x[0], a: x[2](eY(2022)[x[1]]), b: x[2](eY(2023)[x[1]]), c: x[2](eY(2024)[x[1]]), d: f.pctSigned(eY(2024)[x[1]] / eY(2022)[x[1]] - 1) }));
  erows.push({ _cls: "sep", m: "New customers per 1 u Total S&M", a: f.num(1 / eY(2022).total_sm_per_new_customer, 1), b: f.num(1 / eY(2023).total_sm_per_new_customer, 1), c: f.num(1 / eY(2024).total_sm_per_new_customer, 1), d: f.pctSigned(eY(2022).total_sm_per_new_customer / eY(2024).total_sm_per_new_customer - 1) });
  erows.push({ m: "New MRR per 1 u Total S&M", a: f.cop(1e6 / eY(2022).total_sm_per_new_mrr_mm), b: f.cop(1e6 / eY(2023).total_sm_per_new_mrr_mm), c: f.cop(1e6 / eY(2024).total_sm_per_new_mrr_mm), d: f.pctSigned(eY(2022).total_sm_per_new_mrr_mm / eY(2024).total_sm_per_new_mrr_mm - 1) });
  table(document.getElementById("effTable"), [{ key: "m", label: "Ratio" }, { key: "a", label: "2022", num: true }, { key: "b", label: "2023", num: true }, { key: "c", label: "2024", num: true }, { key: "d", label: "Δ 22→24", num: true }], erows);

  const IY = D.industry.year;
  const irows = [];
  [2022, 2023, 2024].forEach((y, k) => IND.forEach((ind, j) => {
    const r = IY.find(x => x.year === y && x.industry === ind);
    irows.push({ _cls: j === 0 && k > 0 ? "sep" : null, y: j === 0 ? (y === 2022 ? "2022 (Mar–Dec)" : y === 2024 ? "2024 (Jan–Oct)" : "2023") : "", ind: ind,
      act: f.int(r.active_customers_end), sa: f.pct(r.share_active_end), mrr: f.cop(r.mrr_end_cop), sm: f.pct(r.share_mrr_end), arpa: f.cop(r.arpa_end_cop),
      nw: f.int(r.new_customers), sn: f.pct(r.share_new_customers), tk: f.cop(r.new_mrr_per_new_customer_cop), ch: f.pct(r.avg_monthly_logo_churn_rate), re: f.int(r.reactivated_customers),
      ex: f.cop(r.expansion_mrr_cop), co: f.cop(r.contraction_mrr_cop), cm: f.cop(r.churned_mrr_cop) });
  }));
  table(document.getElementById("industryTable"), [{ key: "y", label: "Year" }, { key: "ind", label: "Industry" }, { key: "act", label: "Active (end)", num: true }, { key: "sa", label: "% active", num: true },
    { key: "mrr", label: "MRR (end)", num: true }, { key: "sm", label: "% MRR", num: true }, { key: "arpa", label: "ARPA (end)", num: true }, { key: "nw", label: "New", num: true }, { key: "sn", label: "% new", num: true },
    { key: "tk", label: "New MRR / new", num: true }, { key: "ch", label: "Logo churn / mo", num: true }, { key: "re", label: "Reactivated", num: true }, { key: "ex", label: "Expansion MRR", num: true },
    { key: "co", label: "Contraction MRR", num: true }, { key: "cm", label: "Churned MRR", num: true }], irows);

  const DT = D.decomp.details["2022_2024"];
  const dtr = DT.map(r => ({ i: r.industry, n0: f.int(r.n0), n1: f.int(r.n1), s0: f.pct(r.share0), s1: f.pct(r.share1), a0: f.cop(r.mean0), a1: f.cop(r.mean1), mx: f.cop(r.mix_contribution), wi: f.cop(r.within_contribution) }));
  const dm = D.decomp.main["2022_2024"];
  dtr.push({ _cls: "sep", i: "Total", n0: f.int(dm.n0), n1: f.int(dm.n1), s0: "100%", s1: "100%", a0: f.cop(dm.A0), a1: f.cop(dm.A1), mx: f.cop(dm.mix), wi: f.cop(dm.within) });
  table(document.getElementById("decompIndTable"), [{ key: "i", label: "Industry" }, { key: "n0", label: "n 2022", num: true }, { key: "n1", label: "n 2024", num: true }, { key: "s0", label: "Share 2022", num: true }, { key: "s1", label: "Share 2024", num: true },
    { key: "a0", label: "Ticket 2022", num: true }, { key: "a1", label: "Ticket 2024", num: true }, { key: "mx", label: "Mix contribution", num: true }, { key: "wi", label: "Within contribution", num: true }], dtr);

  table(document.getElementById("decompRobustTable"), [{ key: "c", label: "Comparison" }, { key: "v", label: "Variant" }, { key: "a0", label: "From", num: true }, { key: "a1", label: "To", num: true }, { key: "d", label: "Δ", num: true },
    { key: "m", label: "Mix", num: true }, { key: "w", label: "Within", num: true }, { key: "ws", label: "Within share", num: true }, { key: "ci", label: "90% CI within share", num: true }, { key: "l", label: "Laspeyres mix / within / interaction", num: true }],
    D.decomp.robust.map((r, k) => ({ _cls: k > 0 && k % 3 === 0 ? "sep" : null, c: r.comparison, v: r.variant, a0: f.cop(r.A0), a1: f.cop(r.A1), d: f.copSigned(r.delta), m: f.copSigned(r.mix), w: f.copSigned(r.within),
      ws: Math.abs(r.delta) < 5000 ? "n/m" : f.pct(r.within_share, 0), ci: Math.abs(r.delta) < 5000 ? "n/m" : f.pct(r.within_share_ci90_lo, 0) + " – " + f.pct(r.within_share_ci90_hi, 0),
      l: f.cop(r.laspeyres_mix) + " / " + f.cop(r.laspeyres_within) + " / " + f.cop(r.laspeyres_interaction) })));

  const CSu = D.cohorts.summary;
  table(document.getElementById("cohortTable"), [{ key: "c", label: "Cohort" }, { key: "n", label: "Size", num: true }, { key: "m0", label: "M0 mean", num: true }, { key: "md", label: "M0 median", num: true },
    { key: "l1", label: "Logo M1", num: true }, { key: "l3", label: "Logo M3", num: true }, { key: "l6", label: "Logo M6", num: true }, { key: "l12", label: "Logo M12", num: true },
    { key: "r1", label: "Rev M1", num: true }, { key: "r3", label: "Rev M3", num: true }, { key: "r6", label: "Rev M6", num: true }, { key: "r12", label: "Rev M12", num: true }, { key: "e", label: "Expanding ≤ M6", num: true }],
    CSu.map(r => ({ c: r.cohort + (r.partial ? "*" : ""), n: f.int(r.size), m0: f.cop(r.m0_mean_cop), md: f.cop(r.m0_median_cop),
      l1: f.pct(r.logo_m1), l3: f.pct(r.logo_m3), l6: f.pct(r.logo_m6), l12: f.pct(r.logo_m12), r1: f.pct(r.revenue_m1), r3: f.pct(r.revenue_m3), r6: f.pct(r.revenue_m6), r12: f.pct(r.revenue_m12), e: f.pct(r.share_expanding_within_m6) })));

  const AB = D.bridge.annual;
  const per = r => mlab(r.period.split("..")[0]) + " → " + mlab(r.period.split("..")[1]);
  const abRows = [["Opening MRR", "opening_mrr_cop"], ["+ New", "new_mrr_cop"], ["+ Expansion", "expansion_mrr_cop"], ["+ Reactivation", "reactivation_mrr_cop"],
    ["Contraction", "contraction_mrr_cop"], ["Churn", "churned_mrr_cop"], ["Net change", "net_change_cop"], ["Closing MRR", "closing_mrr_cop"]].map((x, k) => {
    const r = { m: x[0], _cls: k === 6 ? "sep" : null };
    AB.forEach((a, j) => { r["p" + j] = f.cop(a[x[1]]); });
    return r;
  });
  const res = { m: "Residual (closing − opening − net)" };
  AB.forEach((a, j) => { res["p" + j] = "COP " + Math.abs(a.check_diff_cop).toFixed(2); });
  abRows.push(res);
  table(document.getElementById("annualBridgeTable"), [{ key: "m", label: "Component" }].concat(AB.map((a, j) => ({ key: "p" + j, label: per(a), num: true }))), abRows);

  table(document.getElementById("claimsTable"), [{ key: "i", label: "Check" }, { key: "c", label: "Claim" }, { key: "s", label: "Status" }],
    D.claims.map(c => ({ i: c.id, c: c.claim, s: c.verified ? "✓ verified" : "✗ failed" })));
  document.getElementById("hashes").textContent = Object.entries(D.meta.hashes).map(e => e[0] + " " + e[1]).join(" · ");
}

/* ================================================================== KPI sparks */
function buildSparks() {
  const map = {
    active: M.active_customers, mrr: M.total_paid_mrr_cop, arpa: M.mrr_per_active_customer_cop,
    new: cleanMask(M.new_customers_3m_avg), ticket: cleanMask(M.median_new_customer_mrr_cop), sm: M.total_sm_spend,
    churn: cleanMask(M.logo_churn_rate), back: cleanMask(M.share_churn_returning_next_month),
  };
  document.querySelectorAll("[data-spark]").forEach(el => {
    const draw = () => spark(el, map[el.dataset.spark] || []);
    draw();
    new ResizeObserver(draw).observe(el);
  });
}

/* ================================================================== controls, nav, table toggles */
function wireControls() {
  document.querySelectorAll("#corrControls .seg").forEach(seg => seg.querySelectorAll("button").forEach(b => {
    b.type = "button";
    b.addEventListener("click", () => { const key = seg.dataset.key; setCorr({ [key]: key === "lag" ? Number(b.textContent) : b.textContent }); });
  }));
  document.querySelectorAll("#cohortControls .seg").forEach(seg => seg.querySelectorAll("button").forEach(b => {
    b.type = "button";
    b.addEventListener("click", () => setCoh({ [seg.dataset.key]: b.textContent }));
  }));
  document.querySelectorAll(".tbtn").forEach(btn => btn.addEventListener("click", () => {
    const card = btn.closest(".card");
    const tv = card.querySelector(".table-view");
    const open = btn.getAttribute("aria-pressed") !== "true";
    btn.setAttribute("aria-pressed", String(open));
    card._tableOpen = open;
    tv.hidden = !open;
    if (open) renderTableView(card);
  }));
}
function wireNav() {
  const links = Array.from(document.querySelectorAll("#nav a"));
  const secs = links.map(a => document.querySelector(a.getAttribute("href")));
  const bar = document.getElementById("progress");
  let ticking = false;
  const update = () => {
    ticking = false;
    const y = window.scrollY + window.innerHeight * 0.28;
    let k = 0;
    secs.forEach((s, i) => { if (s && s.offsetTop <= y) k = i; });
    links.forEach((a, i) => a.classList.toggle("active", i === k));
    const act = links[k];
    if (act && window.innerWidth <= 1180) { const nav = document.getElementById("nav"); const l = act.offsetLeft - 20; if (Math.abs(nav.scrollLeft - l) > 40) nav.scrollTo({ left: l, behavior: "smooth" }); }
    const h = document.documentElement.scrollHeight - window.innerHeight;
    bar.style.width = (h > 0 ? (window.scrollY / h) * 100 : 0) + "%";
  };
  window.addEventListener("scroll", () => { if (!ticking) { ticking = true; requestAnimationFrame(update); } }, { passive: true });
  update();
}

function init() {
  buildTables();
  buildSparks();
  wireControls();
  updateCorrText();
  document.querySelectorAll("[data-chart]").forEach(mount);
  wireNav();
}
if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
