/* Finora · workspace de exploración (Fase 1)
   Gráficas SVG sin dependencias, paleta de preguntas y panel de linaje "¿Cómo lo sabemos?".
   Los datos llegan en el objeto global DATA que escribe finora_eda.py.
   Formato es-CO: punto de miles, coma decimal, signo menos tipográfico, montos con palabras. */
(function () {
"use strict";

const D = DATA;
const M = D.monthly;
const LAB = D.meta.labels;        // ene-22 … oct-24
const YM = D.meta.months;         // 2022-01 … 2024-10
const N = LAB.length;
const CS = D.meta.cleanStart;     // primer mes de la ventana limpia de flujos (mar-22)
const U = D.meta.spendUnit;       // unidad reportada del gasto de S&M
const FACT = D.facts;
const BR = D.brain;
const VN = D.vintageNames;
const REDUCED = !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);
const $ = id => document.getElementById(id);

/* ------------------------------------------------------------------ colores */
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

/* ------------------------------------------------------------------ formato es-CO */
const MINUS = "−";
const ok = v => v !== null && v !== undefined && isFinite(v);
function num(v, d) {
  const s = Math.abs(v).toFixed(d || 0);
  const p = s.split(".");
  return p[0].replace(/\B(?=(\d{3})+(?!\d))/g, ".") + (p[1] ? "," + p[1] : "");
}
const sg = (v, s) => (v < 0 && /[1-9]/.test(s) ? MINUS : "") + s;
const plus = (v, s) => (v < 0 && /[1-9]/.test(s) ? MINUS : "+") + s;
const COP_U = [[1, ""], [1e3, " mil"], [1e6, " millones"], [1e9, " mil millones"]];
function copWords(v, d) {
  // montos en texto con palabras, sin K/M ambiguas: COP 97,0 millones · COP 57,8 mil
  if (!ok(v)) return "–";
  if (d === undefined) d = 1;
  const a = Math.abs(v);
  let k = a >= 1e9 ? 3 : a >= 1e6 ? 2 : a >= 1e3 ? 1 : 0;
  if (k === 0 && Math.round(a) >= 1000) k = 1;
  if (k > 0 && k < 3 && Number((a / COP_U[k][0]).toFixed(d)) >= 1000) k++;
  const body = k === 0 ? num(a, 0) : num(a / COP_U[k][0], d) + COP_U[k][1];
  return (v < 0 && /[1-9]/.test(body) ? MINUS : "") + "COP " + body;
}
const f = {
  cop: v => copWords(v, 1),
  cop2: v => copWords(v, 2),
  copShort: v => copWords(v, 1).replace("COP ", ""),
  copFull: v => ok(v) ? sg(v, num(Math.abs(v), 0)).replace(/^(−?)/, "$1COP ") : "–",
  copSigned: v => ok(v) ? (v < 0 ? MINUS : "+") + copWords(Math.abs(v), 1) : "–",
  int: v => ok(v) ? sg(v, num(Math.round(Math.abs(v)), 0)) : "–",
  pct: (v, d) => ok(v) ? sg(v, num(Math.abs(v) * 100, d === undefined ? 1 : d)) + "%" : "–",
  pct0: v => f.pct(v, 0),
  pctSigned: (v, d) => ok(v) ? plus(v, num(Math.abs(v) * 100, d || 0)) + "%" : "–",
  u: (v, d) => ok(v) ? sg(v, num(Math.abs(v), d === undefined ? 3 : d)) + " " + U : "–",
  u2: v => f.u(v, 2),
  idx: v => ok(v) ? sg(v, num(Math.abs(v), 0)) : "–",
  r: v => ok(v) ? plus(v, num(Math.abs(v), 2)) : "–",
  p: v => ok(v) ? (v < 0.001 ? "<0,001" : num(v, 3)) : "–",
  z: v => ok(v) ? plus(v, num(Math.abs(v), 2)) : "–",
  num: (v, d) => ok(v) ? sg(v, num(Math.abs(v), d === undefined ? 2 : d)) : "–",
  x: v => ok(v) ? num(v, 1) + "×" : "–",
};
// ejes: los ticks muestran números y la unidad va en el título del eje ("millones de COP")
function axisFmt(kind, ticks) {
  const step = ticks.length > 1 ? Math.abs(ticks[1] - ticks[0]) : 1;
  const maxAbs = Math.max(...ticks.map(Math.abs));
  const dec = s => Math.max(0, Math.min(3, -Math.floor(Math.log10(s) + 1e-9)));
  const plain = d => v => sg(v, num(Math.abs(v), d));
  if (kind === "pct") {
    const d = Math.min(2, dec(step * 100));
    return { f: v => sg(v, num(Math.abs(v) * 100, d)) + "%", unit: null, div: 1 };
  }
  if (kind === "cop") {
    const sc = maxAbs >= 1e9 ? [1e9, "miles de millones de COP"] : maxAbs >= 1e6 ? [1e6, "millones de COP"] : maxAbs >= 1e3 ? [1e3, "miles de COP"] : [1, "COP"];
    const d = Math.min(2, dec(step / sc[0]));
    return { f: v => (v === 0 ? "0" : sg(v, num(Math.abs(v) / sc[0], d))), unit: sc[1], div: sc[0] };
  }
  if (kind === "int") return { f: plain(0), unit: null, div: 1 };
  if (kind === "idx") return { f: plain(0), unit: "índice (base 100)", div: 1 };
  if (kind === "u") return { f: plain(dec(step)), unit: U + " (unidad reportada)", div: 1 };
  if (kind === "z") return { f: plain(dec(step)), unit: "puntaje z", div: 1 };
  return { f: plain(dec(step)), unit: null, div: 1 };
}

/* ------------------------------------------------------------------ DOM */
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
// texto con segmentos entre acentos graves → <code>
function rich(el, text) {
  String(text === undefined || text === null ? "" : text).split("`").forEach((part, i) => {
    if (!part) return;
    if (i % 2) H("code", null, el, part); else el.append(part);
  });
  return el;
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

/* ------------------------------------------------------------------ escalas y ejes */
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
    return labels.map((l, i) => (i % every === 0 ? { i: i, text: l } : null)).filter(Boolean);
  }
  const per = pw / Math.max(1, mode === "band" ? n : n - 1);
  const every = per >= 19 ? 3 : per >= 9.5 ? 6 : 12;
  const out = [];
  labels.forEach((l, i) => {
    const m = MESES.indexOf(l.slice(0, 3));
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

/* ------------------------------------------------------------------ marco común */
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
function unitDraw(svg, unit) { if (unit) T(svg, 0, 11, unit, "fv-unit", "start"); }
function shadesDraw(svg, shades, X, halfStep, mt, ph, mini) {
  (shades || []).forEach(sh => {
    const x0 = X(sh.from) - halfStep, x1 = X(sh.to) + halfStep;
    S("rect", { x: x0, y: mt, width: Math.max(0, x1 - x0), height: ph, class: "fv-shade" }, svg);
    if (sh.label && !mini) T(svg, x0 + 5, mt + 11, sh.label, "fv-shade-lab");
  });
}
// ventana censurada (ene–feb 22): se sombrea en las gráficas mensuales que dependen de flujos
function winIdx(labels) {
  if (!labels.length || !labels.every(isMonth)) return [];
  const out = [];
  labels.forEach((l, i) => { const k = LAB.indexOf(l); if (k >= 0 && k < CS) out.push(i); });
  return out;
}
function winDraw(svg, idx, X, halfStep, ml, mt, ph, mini) {
  if (!idx.length) return;
  const x0 = Math.max(ml, X(idx[0]) - halfStep), x1 = X(idx[idx.length - 1]) + halfStep;
  S("rect", { x: x0, y: mt, width: Math.max(0, x1 - x0), height: ph, class: "fv-win" }, svg);
  const lab = "censura";
  if (!mini && x1 - x0 >= measure(lab, '9.5px "JetBrains Mono", monospace') + 8) T(svg, (x0 + x1) / 2, mt + 10, lab, "fv-win-lab", "middle");
}
function winNote(label) {
  return LAB.indexOf(label) === 0
    ? "Fuera de la ventana limpia: " + LAB[0] + " está censurado (sin movimientos)."
    : "Fuera de la ventana limpia: " + label + " trae arrastre de la censura inicial.";
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
const firstCol = (o, labels) => o.xTitle || (labels.every(isMonth) ? "Mes" : "Periodo");

/* ------------------------------------------------------------------ LÍNEAS */
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
  const ax = axisFmt(o.tickKind || "num", ticks);
  const tf = o.tickFormat || ax.f;
  const unit = o.unit !== undefined ? o.unit : ax.unit;
  const ml = Math.max(...ticks.map(t => measure(tf(t)))) + 14;
  const endItems = [];
  const endFmt = o.endLabelFmt || (s => s.short || s.name);
  if (o.endLabels && !mini) {
    series.forEach(s => {
      let i = s.values.length - 1;
      while (i >= 0 && !ok(s.values[i])) i--;
      if (i >= 0) endItems.push({ s: s, i: i, text: endFmt(s, s.values[i]) });
    });
  }
  const mr = endItems.length ? Math.max(...endItems.map(e => measure(e.text, SANS))) + 26 : (mini ? 6 : 12);
  const mt = unit || (o.shades && o.shades.some(s => s.label) && !mini) ? 20 : 10;
  const mb = 26;
  const pw = Math.max(40, W - ml - mr), ph = Hh - mt - mb;
  const X = mode === "band" ? (i => ml + (i + 0.5) * pw / n) : (i => ml + (n === 1 ? pw / 2 : i * pw / (n - 1)));
  const half = mode === "band" ? pw / n / 2 : (n > 1 ? pw / (n - 1) / 2 : pw / 2);
  const Y = v => mt + ph - (v - lo) / (hi - lo) * ph;
  const svg = S("svg", { width: W, height: Hh, viewBox: "0 0 " + W + " " + Hh, class: "fv-svg", role: "img", "aria-label": o.aria || "" }, el);
  unitDraw(svg, unit);
  const win = o.win ? winIdx(labels) : [];
  winDraw(svg, win, X, half, ml, mt, ph, mini);
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
    const note = (o.tipNote ? o.tipNote(i) : null) || (win.includes(i) ? winNote(labels[i]) : null);
    tipShow(cx, cy, o.tipTitle ? o.tipTitle(i) : labels[i], rows, note);
  }
  function hide() { cur = -1; cross.setAttribute("visibility", "hidden"); hd.forEach(h => h.setAttribute("visibility", "hidden")); tipHide(); }
  const move = e => { const r = svg.getBoundingClientRect(); show(idxAt(e.clientX - r.left), e); };
  hit.addEventListener("pointermove", move);
  hit.addEventListener("pointerdown", move);
  hit.addEventListener("pointerleave", hide);
  keyboard(svg, n, show, hide, () => cur);
  const cols = [{ key: "x", label: firstCol(o, labels) }].concat(o.series.map((s, k) => ({ key: "s" + k, label: s.name, num: true })));
  if (o.band) cols.push({ key: "lo", label: o.band.name + " (inferior)", num: true }, { key: "hi", label: o.band.name + " (superior)", num: true });
  const rows = labels.map((l, i) => {
    const r = { x: l };
    o.series.forEach((s, k) => { r["s" + k] = (s.fmt || fmt)(s.values[i]); });
    if (o.band) { r.lo = fmt(o.band.lower[i]); r.hi = fmt(o.band.upper[i]); }
    return r;
  });
  return { table: { cols: cols, rows: rows } };
}

/* ------------------------------------------------------------------ BARRAS */
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
  const ax = axisFmt(o.tickKind || "num", ticks);
  const tf = o.tickFormat || ax.f;
  const unit = o.unit !== undefined ? o.unit : ax.unit;
  const ml = Math.max(...ticks.map(t => measure(tf(t)))) + 14;
  const mr = mini ? 6 : 12;
  const mt = unit || (mini && o.ref && o.ref.label) || (o.shades && o.shades.some(s => s.label) && !mini) ? 20 : 10;
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
  unitDraw(svg, unit);
  const win = o.win ? winIdx(labels) : [];
  winDraw(svg, win, X, step / 2, ml, mt, ph, mini);
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
      pos.forEach((sg2, j) => {
        let top = Y(sg2.b), bot = Y(sg2.a);
        if (j < pos.length - 1) top += 1;
        if (j > 0) bot -= 1;
        if (bot - top < 0.6) return;
        S("path", { d: roundedBar(x, groupW, top, bot, j === pos.length - 1, false), fill: sg2.col, opacity: op }, g);
      });
      neg.forEach((sg2, j) => {
        let top = Y(sg2.a), bot = Y(sg2.b);
        if (j > 0) top += 1;
        if (j < neg.length - 1) bot -= 1;
        if (bot - top < 0.6) return;
        S("path", { d: roundedBar(x, groupW, top, bot, false, j === neg.length - 1), fill: sg2.col, opacity: op }, g);
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
    if (o.ref.label && mini) {
      // en miniaturas la etiqueta va en la fila superior (junto a la unidad) para no taparse con las barras
      const w = measure(o.ref.label, '10px "JetBrains Mono", monospace');
      S("line", { x1: ml + pw - w - 20, x2: ml + pw - w - 7, y1: 7.5, y2: 7.5, class: "fv-ref" }, svg);
      T(svg, ml + pw, 11, o.ref.label, "fv-flag-lab", "end");
    } else if (o.ref.label) T(svg, ml + pw - 2, Y(o.ref.value) - 4, o.ref.label, "fv-flag-lab", "end");
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
    const note = (dim.has(i) && o.dimNote) ? o.dimNote : ((o.tipNote ? o.tipNote(i) : null) || (win.includes(i) ? winNote(labels[i]) : null));
    tipShow(cx, cy, o.tipTitle ? o.tipTitle(i) : labels[i], rowsAt(i), note);
  }
  function hide() { cur = -1; wash.setAttribute("visibility", "hidden"); tipHide(); }
  const hit = S("rect", { x: ml, y: mt, width: pw, height: ph, fill: "transparent" }, svg);
  const move = e => { const r = svg.getBoundingClientRect(); show(clamp(Math.floor((e.clientX - r.left - ml) / step), 0, n - 1), e); };
  hit.addEventListener("pointermove", move);
  hit.addEventListener("pointerdown", move);
  hit.addEventListener("pointerleave", hide);
  keyboard(svg, n, show, hide, () => cur);
  const cols = [{ key: "x", label: firstCol(o, labels) }].concat(o.series.map((s, j) => ({ key: "s" + j, label: s.name, num: true })));
  if (o.line) cols.push({ key: "ln", label: o.line.name, num: true });
  const rows = labels.map((l, i) => {
    const r = { x: l };
    o.series.forEach((s, j) => { r["s" + j] = (s.tableFmt || s.fmt || fmt)(s.values[i]); });
    if (o.line) r.ln = (o.line.fmt || fmt)(o.line.values[i]);
    return r;
  });
  return { table: { cols: cols, rows: rows } };
}

/* ------------------------------------------------------------------ CASCADA */
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
  const hi = Math.max(...levels);
  const ticks = niceTicks(lo, hi, 5);
  lo = o.yMin !== undefined ? Math.max(ticks[0], o.yMin) : ticks[0];
  const top = ticks[ticks.length - 1];
  const tk = ticks.filter(t => t >= lo);
  const ax = axisFmt("cop", tk);
  const tf = ax.f;
  // etiquetas de barra en la misma unidad del eje: 97,0 · +2,4
  const lab = v => num(Math.abs(v) / ax.div, ax.div > 1 ? 1 : 0);
  const ml = Math.max(...tk.map(t => measure(tf(t)))) + 16;
  const mt = 30, mb = 34, mr = 10;
  const pw = W - ml - mr, ph = Hh - mt - mb;
  const step = pw / n;
  const X = i => ml + (i + 0.5) * step;
  const Y = v => mt + ph - (v - lo) / (top - lo) * ph;
  const bw = Math.min(58, step * 0.56);
  // si alguna etiqueta no cabe en su columna, todas las que tienen versión corta la usan (p. ej. "Exp.")
  const useShort = steps.some(s => String(s.label).split("\n").some(l => measure(l) > step - 4));
  const svg = S("svg", { width: W, height: Hh, viewBox: "0 0 " + W + " " + Hh, class: "fv-svg", role: "img" }, el);
  unitDraw(svg, ax.unit);
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
    const txt = b.a === null ? lab(b.b) : (b.s.value >= 0 ? "+" : MINUS) + lab(b.s.value);
    const ly = b.a === null || up ? topY - 7 : botY + 14;
    T(svg, X(i), ly, txt, "fv-lab b", "middle");
    const labs = String(useShort && b.s.short ? b.s.short : b.s.label).split("\n");
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
    const rows = [{ color: b.s.color, kind: "rect", label: b.s.label.replace("\n", " "), value: b.a === null ? f.copFull(b.b) : (b.s.value >= 0 ? "+" : MINUS) + f.copFull(Math.abs(b.s.value)) }];
    if (b.a !== null) rows.push({ kind: "none", label: "nivel acumulado", value: f.cop(b.b) });
    if (b.s.extra) b.s.extra.forEach(r => rows.push(r));
    let cx, cy;
    if (evt) { cx = evt.clientX; cy = evt.clientY; } else { const r = svg.getBoundingClientRect(); cx = r.left + X(i); cy = r.top + mt; }
    tipShow(cx, cy, o.title || "Puente", rows, b.s.note || null);
  }
  function hide() { cur = -1; wash.setAttribute("visibility", "hidden"); tipHide(); }
  const hit = S("rect", { x: ml, y: mt, width: pw, height: ph, fill: "transparent" }, svg);
  const move = e => { const r = svg.getBoundingClientRect(); show(clamp(Math.floor((e.clientX - r.left - ml) / step), 0, n - 1), e); };
  hit.addEventListener("pointermove", move);
  hit.addEventListener("pointerdown", move);
  hit.addEventListener("pointerleave", hide);
  keyboard(svg, n, show, hide, () => cur);
  return { table: { cols: [{ key: "a", label: "Paso" }, { key: "b", label: "Valor", num: true }, { key: "c", label: "Nivel después del paso", num: true }],
    rows: bars.map(b => ({ a: b.s.label.replace("\n", " "), b: f.copFull(b.a === null ? b.b : b.s.value), c: f.copFull(b.b) })) } };
}

/* ------------------------------------------------------------------ DISPERSIÓN */
function scatter(el, o) {
  el.replaceChildren();
  const W = Math.max(260, el.clientWidth || 600);
  const Hh = o.height || 320;
  const pts = o.points.filter(p => ok(p.x) && ok(p.y));
  const xs = pts.map(p => p.x), ys = pts.map(p => p.y);
  const padX = (Math.max(...xs) - Math.min(...xs)) * 0.06 || 1, padY = (Math.max(...ys) - Math.min(...ys)) * 0.08 || 1;
  const xt = niceTicks(Math.min(...xs) - padX, Math.max(...xs) + padX, 5);
  const yt = niceTicks(Math.min(...ys) - padY, Math.max(...ys) + padY, 5);
  const xa = axisFmt(o.xKind || "num", xt), ya = axisFmt(o.yKind || "num", yt);
  const ml = Math.max(...yt.map(t => measure(ya.f(t)))) + 16;
  const mt = 18, mb = 44, mr = 14;
  const pw = W - ml - mr, ph = Hh - mt - mb;
  const X = v => ml + (v - xt[0]) / (xt[xt.length - 1] - xt[0]) * pw;
  const Y = v => mt + ph - (v - yt[0]) / (yt[yt.length - 1] - yt[0]) * ph;
  const svg = S("svg", { width: W, height: Hh, viewBox: "0 0 " + W + " " + Hh, class: "fv-svg", role: "img" }, el);
  yt.forEach(t => { S("line", { x1: ml, x2: ml + pw, y1: Y(t), y2: Y(t), class: t === 0 ? "fv-base" : "fv-grid" }, svg); T(svg, ml - 8, Y(t) + 3.5, ya.f(t), "fv-tick", "end"); });
  xt.forEach(t => { S("line", { x1: X(t), x2: X(t), y1: mt, y2: mt + ph, class: t === 0 ? "fv-base" : "fv-grid" }, svg); T(svg, X(t), mt + ph + 16, xa.f(t), "fv-tick", "middle"); });
  if (o.xTitle) T(svg, ml + pw / 2, Hh - 6, o.xTitle + (xa.unit ? " · " + xa.unit : ""), "fv-axis-title", "middle");
  if (o.yTitle) T(svg, 0, 11, o.yTitle + (ya.unit ? " · " + ya.unit : ""), "fv-axis-title", "start");
  if (pts.length >= 3) {
    const mx = xs.reduce((a, b) => a + b, 0) / xs.length, my = ys.reduce((a, b) => a + b, 0) / ys.length;
    let sxy = 0, sxx = 0;
    pts.forEach(p => { sxy += (p.x - mx) * (p.y - my); sxx += (p.x - mx) * (p.x - mx); });
    const b = sxx ? sxy / sxx : 0, a = my - b * mx;
    const x0 = Math.min(...xs), x1 = Math.max(...xs);
    S("path", { d: "M" + X(x0) + "," + Y(a + b * x0) + " L" + X(x1) + "," + Y(a + b * x1), class: "fv-trend" }, svg);
  }
  pts.forEach(p => S("circle", { cx: X(p.x), cy: Y(p.y), r: 5.2, fill: p.color || o.color || C.s1, "fill-opacity": 0.82, stroke: C.surface, "stroke-width": 2 }, svg));
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
  return { table: { cols: [{ key: "l", label: "Mes del resultado" }, { key: "x", label: o.xName || "x", num: true }, { key: "y", label: o.yName || "y", num: true }],
    rows: pts.map(p => ({ l: p.label, x: (o.xFmt || f.num)(p.x), y: (o.yFmt || f.num)(p.y) })) } };
}

/* ------------------------------------------------------------------ MAPA DE CALOR */
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
  if (sel && sel[0] >= 0) S("rect", { x: labW + sel[1] * cw + 0.5, y: topH + sel[0] * ch + 0.5, width: cw - 1, height: ch - 1, rx: 4, fill: "none", stroke: C.ink, "stroke-width": 2 }, svg);
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
  const tcols = [{ key: "r", label: o.rowTitle || "Fila" }].concat(cols.map((c, j) => ({ key: "c" + j, label: c, num: true })));
  const trows = rows.map((r, i) => { const x = { r: r }; cols.forEach((c, j) => { x["c" + j] = ok(o.values[i][j]) ? o.fmt(o.values[i][j]) : ""; }); return x; });
  return { table: { cols: tcols, rows: trows } };
}

/* ------------------------------------------------------------------ PUNTOS (mancuerna) */
function dots(el, o) {
  el.replaceChildren();
  const W = Math.max(260, el.clientWidth || 600);
  const rows = o.rows;
  const rh = o.rowH || 34;
  const labW = Math.max(...rows.map(r => measure(r, SANS))) + 16;
  const mt = 8, mb = 40, mr = 14;
  const Hh = mt + rows.length * rh + mb;
  let vals = [];
  o.series.forEach(s => s.values.forEach(v => { if (ok(v)) vals.push(v); }));
  const ticks = niceTicks(Math.min(0, ...vals), Math.max(...vals), 5);
  const ax = axisFmt(o.tickKind || "cop", ticks);
  const pw = W - labW - mr;
  const X = v => labW + (v - ticks[0]) / (ticks[ticks.length - 1] - ticks[0]) * pw;
  const svg = S("svg", { width: W, height: Hh, viewBox: "0 0 " + W + " " + Hh, class: "fv-svg", role: "img" }, el);
  ticks.forEach(t => { S("line", { x1: X(t), x2: X(t), y1: mt, y2: mt + rows.length * rh, class: t === 0 ? "fv-base" : "fv-grid" }, svg); T(svg, X(t), mt + rows.length * rh + 17, ax.f(t), "fv-tick", "middle"); });
  if (ax.unit) T(svg, labW + pw, mt + rows.length * rh + 33, ax.unit, "fv-unit", "end");
  if (o.ref !== undefined && o.ref >= ticks[0] && o.ref <= ticks[ticks.length - 1]) {
    S("line", { x1: X(o.ref), x2: X(o.ref), y1: mt, y2: mt + rows.length * rh, class: "fv-ref" }, svg);
    if (o.refLabel) T(svg, X(o.ref) + 4, mt + rows.length * rh + 33, o.refLabel, "fv-flag-lab", "start");
  }
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
  return { table: { cols: [{ key: "r", label: o.rowTitle || "Fila" }].concat(o.series.map((s, k) => ({ key: "s" + k, label: s.name, num: true }))),
    rows: rows.map((r, i) => { const x = { r: r }; o.series.forEach((s, k) => { x["s" + k] = (o.fmt || f.cop)(s.values[i]); }); return x; }) } };
}

/* ------------------------------------------------------------------ MÚLTIPLOS */
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
  const W = el.clientWidth || 200, Hh = el.clientHeight || 32;
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

/* ------------------------------------------------------------------ LEYENDA + TABLAS */
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
      b.title = "Mostrar / ocultar";
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
      if (c.node) { const nd = c.node(v, r); if (nd) td.appendChild(nd); return; }
      td.textContent = c.fmt ? c.fmt(v, r) : (v === null || v === undefined || v === "" ? "–" : v);
    });
  });
  return t;
}
function mergeTables(list) {
  // las tablas que comparten la primera columna (p. ej. los 34 meses) se unen en una sola tabla ancha
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
  mergeTables(list).forEach(g => {
    if (g.title) { const h = H("div", "cell-t", tv, g.title); h.style.cssText = "padding:10px 10px 4px;font-size:12.5px;font-weight:600"; }
    const box = H("div", null, tv);
    table(box, g.table.cols, g.table.rows);
  });
}

/* ------------------------------------------------------------------ registro de gráficas */
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
  if (!fn) { console.warn("gráfica sin registrar:", el.dataset.chart); return; }
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

/* ================================================================== GRÁFICAS */
const cleanMask = arr => arr.map((v, i) => (i >= CS ? v : null));
const CUT = [{ from: monthIdx(FACT.cut_start_ym), to: monthIdx(FACT.cut_end_ym), label: "tras el recorte" }];
const YNAME = y => (Number(y) === 2022 ? "2022 (mar–dic)" : Number(y) === 2024 ? "2024 (ene–oct)" : String(y));
const GRP = { dg: "Generación de demanda", sc: "Capacidad comercial", en: "Habilitación" };
const WIN_LEG = { name: "Fuera de la ventana limpia", color: "rgba(12,19,34,0.16)", toggle: false };

// ---------------- 01 datos
REG.entrySignature = (el, card) => {
  const rows = D.entrySignature;
  const labels = rows.map(r => mlab(r.cohort));
  const vals = rows.map(r => r.share);
  const colors = rows.map((r, i) => (i === 0 ? C.s1 : C.de));
  legend(card, [{ name: VN.feb, color: C.s1 }, { name: "Cohortes posteriores", color: C.de }], null);
  return barChart(el, {
    labels: labels, series: [{ name: "Primer pago = 2× el segundo", values: vals, colors: colors, fmt: v => f.pct(v) }],
    fmt: v => f.pct(v), tickKind: "pct", height: 250, xTitle: "Cohorte",
    tipRows: i => [{ color: colors[i], kind: "rect", label: "primer pago = 2× el segundo", value: f.pct(vals[i]) },
                   { kind: "none", label: "clientes", value: f.int(rows[i].first_amount_2x_next) + " de " + f.int(rows[i].new_customers) }],
  });
};
REG.examples = el => multiples(el, {
  cols: 2, minCellW: 250, height: 136,
  items: D.examples.map(ex => ({
    title: "Cliente " + ex.id, right: ex.industry, note: ex.caption, kind: "bars",
    opts: { labels: LAB, series: [{ name: "Monto pagado", values: ex.amounts_cop, color: C.s1 }], fmt: f.cop, tickKind: "cop",
            zeroMarks: true, ref: { value: ex.usual_cop, label: "usual " + f.cop(ex.usual_cop) } },
  })),
});
function shortCop(v) {
  if (v >= 1e6) return num(v / 1e6, v % 1e6 ? 1 : 0) + (v === 1e6 ? " millón" : " millones");
  if (v >= 1e3) return num(v / 1e3, 0) + " mil";
  return num(v, 0);
}
function bandLabel(a, b) {
  if (a >= 1e3 && b < 1e6) return num(a / 1e3, 0) + "–" + num(b / 1e3, 0) + " mil";
  if (a >= 1e6) return num(a / 1e6, 0) + "–" + num(b / 1e6, 0) + " millones";
  return shortCop(a) + "–" + shortCop(b);
}
REG.amountHist = el => {
  const h = D.amountHist;
  const labels = h.counts.map((c, i) => bandLabel(h.edges[i], h.edges[i + 1]));
  const tot = sum(h.counts);
  return barChart(el, {
    labels: labels, series: [{ name: "Meses-cliente", values: h.counts, color: C.s1 }], fmt: f.int, tickKind: "int", height: 250, xTitle: "Banda (COP)",
    tipTitle: i => "COP " + labels[i],
    tipRows: i => [{ color: C.s1, kind: "rect", label: "meses-cliente", value: f.int(h.counts[i]) }, { kind: "none", label: "de los meses con pago", value: f.pct(h.counts[i] / tot) }],
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
    shades: [{ from: monthIdx(FACT.team_break_ym), to: N - 1, label: "desde " + FACT.team_break }],
    extraRows: i => [{ kind: "none", label: "S&M total", value: f.u(tot[i]) }] });
};

// ---------------- 02 resultado
REG.growthIndex = (el, card) => {
  const a0 = M.active_customers[0], m0 = M.total_paid_mrr_cop[0], r0 = M.mrr_per_active_customer_cop[0];
  const s = [
    { name: "Clientes activos", short: "Clientes", values: M.active_customers.map(v => 100 * v / a0), color: C.s1, tip: (i, v) => f.idx(v) + " · " + f.int(M.active_customers[i]) },
    { name: "MRR pagado", short: "MRR pagado", values: M.total_paid_mrr_cop.map(v => 100 * v / m0), color: C.s2, tip: (i, v) => f.idx(v) + " · " + f.cop(M.total_paid_mrr_cop[i]) },
    { name: "MRR por cliente activo", short: "MRR / cliente", values: M.mrr_per_active_customer_cop.map(v => 100 * v / r0), color: C.s7, tip: (i, v) => f.idx(v) + " · " + f.cop(M.mrr_per_active_customer_cop[i]) },
  ];
  legend(card, s.map(x => ({ name: x.name, color: x.color, kind: "line" })), el);
  return lineChart(el, { labels: LAB, series: s, fmt: f.idx, tickKind: "idx", height: 330, ref: { value: 100 },
    endLabels: true, endLabelFmt: (x, v) => x.short + " " + num(v, 0) });
};
REG.customerFlows = (el, card) => {
  const idx = range(1, N);
  const s = [
    { name: "Altas", values: idx.map(i => M.new_customers[i]), color: MOV.New },
    { name: "Reactivaciones", values: idx.map(i => M.reactivated_customers[i]), color: MOV.Reactivation },
    { name: "Churn observado", values: idx.map(i => -M.churned_customers[i]), color: MOV.Churn, fmt: v => f.int(Math.abs(v)) },
  ];
  const line = { name: "Altas netas", values: idx.map(i => M.net_customer_adds[i]), color: C.ink };
  legend(card, s.map(x => ({ name: x.name, color: x.color })).concat([{ name: line.name, color: line.color, kind: "line" }, WIN_LEG]), el);
  return barChart(el, { labels: idx.map(i => LAB[i]), series: s, stacked: true, line: line, fmt: f.int, tickKind: "int", height: 310, win: true,
    dim: [0], dimNote: "feb-22: incluye arrastre de la censura inicial (se excluye de las tasas).",
    extraRows: i => [{ kind: "none", label: "clientes activos", value: f.int(M.active_customers[i + 1]) }] });
};
REG.mrrLevel = (el, card) => {
  const s = [
    { name: "MRR pagado", values: M.total_paid_mrr_cop, color: C.s1 },
    { name: "Promedio móvil de 3 meses", values: M.total_paid_mrr_cop_3m_avg, color: C.de, width: 2.6 },
  ];
  legend(card, s.map(x => ({ name: x.name, color: x.color, kind: "line" })), el);
  return lineChart(el, { labels: LAB, series: s, fmt: f.cop, tickKind: "cop", height: 310,
    extraRows: i => i > 0 ? [{ kind: "none", label: "vs mes anterior", value: f.pctSigned(M.total_paid_mrr_cop[i] / M.total_paid_mrr_cop[i - 1] - 1) }] : [] });
};

// ---------------- 03 ticket de entrada
REG.ticketMonthly = (el, card) => {
  const s = [
    { name: "Promedio (MRR nuevo ÷ altas)", values: cleanMask(M.new_mrr_per_new_customer_cop), color: C.s1 },
    { name: "Mediana", values: cleanMask(M.median_new_customer_mrr_cop), color: C.s2 },
  ];
  const band = { name: "P25–P75", lower: cleanMask(M.p25_new_customer_mrr_cop), upper: cleanMask(M.p75_new_customer_mrr_cop), color: C.s2 };
  legend(card, s.map(x => ({ name: x.name, color: x.color, kind: "line" })).concat([{ name: "P25–P75", color: C.s2, kind: "rect wash" }, WIN_LEG]), el);
  return lineChart(el, { labels: LAB, series: s, band: band, fmt: f.cop, tickKind: "cop", height: 330, win: true,
    flags: [{ i: monthIdx(FACT.step_month_ym), label: "escalón · " + FACT.step_month }],
    extraRows: i => i >= CS ? [{ kind: "none", label: "altas", value: f.int(M.new_customers[i]) }, { kind: "none", label: "P90", value: f.cop(M.p90_new_customer_mrr_cop[i]) }] : [],
    tipNote: i => i < CS ? "No se calcula: " + (i === 0 ? "mes censurado." : "arrastre de la censura inicial.") : null });
};
REG.priceBands = (el, card) => {
  const b = D.ticket.bands;
  const s = b.years.map((y, k) => ({ name: YNAME(y), values: b.shares[k], color: YEARC[y] }));
  legend(card, s.map(x => ({ name: x.name, color: x.color })), el);
  return barChart(el, { labels: b.labels, series: s, fmt: v => f.pct(v), tickKind: "pct", height: 290, xTitle: "Banda del ticket de entrada (COP)",
    tipTitle: i => "Banda " + b.labels[i] + " (COP)",
    tipRows: i => s.filter(x => !(el._hidden && el._hidden.has(x.name))).map(x => { const k = s.indexOf(x); return { color: x.color, kind: "rect", label: x.name, value: f.pct(x.values[i]) + " · " + f.int(b.counts[k][i]) + " altas" }; }) });
};
REG.vintageArpa = (el, card) => {
  const V = D.vintage;
  const order = [[VN.base, "Base", C.r250], [VN.v2022, "2022", C.r400], [VN.v2023, "2023", C.r550], [VN.v2024, "2024", C.r700]];
  const s = order.map(o => ({ name: o[0], short: o[1], color: o[2], values: V[o[0]].arpa.map((v, i) => (V[o[0]].active[i] >= 30 ? v : null)),
    tip: (i, v) => f.cop(v) + " · " + f.int(V[o[0]].active[i]) + " clientes" }));
  const co = { name: "Promedio de la empresa", short: "Todos", color: C.de, width: 1.6, values: M.mrr_per_active_customer_cop, tip: (i, v) => f.cop(v) };
  const all = s.concat([co]);
  legend(card, all.map(x => ({ name: x.name, color: x.color, kind: "line" })), el);
  return lineChart(el, { labels: LAB, series: all, fmt: f.cop, tickKind: "cop", height: 300, endLabels: true, endLabelFmt: (x, v) => x.short + " " + f.copShort(v),
    tipNote: () => "Cada cosecha aparece cuando tiene al menos 30 clientes activos." });
};

// ---------------- 04 inversión comercial
REG.smStack = (el, card) => {
  const s = [
    { name: GRP.dg, values: M.demand_gen_spend, color: C.s1 },
    { name: GRP.sc, values: M.sales_capacity_spend, color: C.s2 },
    { name: GRP.en, values: M.enablement_spend, color: C.s3 },
  ];
  legend(card, s.map(x => ({ name: x.name, color: x.color })), el);
  return barChart(el, { labels: LAB, series: s, stacked: true, fmt: v => f.u(v), tickKind: "u", height: 310, shades: CUT,
    showTotal: true, totalLabel: "S&M total",
    extraRows: i => [{ kind: "none", label: "S&M total sin PayrollExpenses", value: f.u(M.total_sm_ex_payroll[i]) }] });
};
REG.smComponents = el => {
  const comps = [
    ["PaidMedia", "paid_media", C.s1, GRP.dg], ["PublicidadNoWeb", "publicidad_no_web", C.s1, GRP.dg],
    ["Team", "team", C.s2, GRP.sc], ["PayrollExpenses", "payroll_expenses", C.s2, GRP.sc], ["Travel", "travel", C.s2, GRP.sc],
    ["SoftwareTools", "software_tools", C.s3, GRP.en], ["Freelance", "freelance", C.s3, GRP.en],
  ];
  const notes = {
    Team: "12,0% del total hasta " + FACT.team_fixed_until + "; plano después",
    PayrollExpenses: "negativo en " + FACT.payroll_neg_n + " meses",
    Freelance: "0 desde " + FACT.freelance_zero_from + " (excepto " + FACT.freelance_exceptions + ")",
    PaidMedia: FACT.pm_drop + " de pico a valle en 2023",
  };
  return multiples(el, { cols: 4, minCellW: 220, height: 150, items: comps.map(c => ({
    title: c[0], right: c[3], note: notes[c[0]] || "", kind: "bars",
    opts: { labels: LAB, series: [{ name: c[0], values: M[c[1]], color: c[2] }], fmt: v => f.u(v), tickKind: "u", shades: CUT },
  })) });
};
REG.alignedPanels = el => {
  const items = [
    ["Paid Media", "bars", M.paid_media, C.s2, v => f.u(v), "u", false], ["Altas", "bars", cleanMask(M.new_customers), C.s1, f.int, "int", true],
    [GRP.dg, "bars", M.demand_gen_spend, C.s2, v => f.u(v), "u", false], ["MRR nuevo", "bars", cleanMask(M.new_mrr_cop), C.s1, f.cop, "cop", true],
    ["S&M total", "bars", M.total_sm_spend, C.s2, v => f.u(v), "u", false], ["Altas netas", "bars", cleanMask(M.net_customer_adds), C.s1, f.int, "int", true],
    [GRP.sc, "bars", M.sales_capacity_spend, C.s2, v => f.u(v), "u", false], ["MRR pagado total", "line", M.total_paid_mrr_cop, C.s1, f.cop, "cop", false],
  ];
  return multiples(el, { cols: 2, minCellW: 300, height: 138, items: items.map(it => ({
    title: it[0], kind: it[1],
    opts: { labels: LAB, xMode: "band", series: [{ name: it[0], values: it[2], color: it[3] }], fmt: it[4], tickKind: it[5], shades: CUT, includeZero: true, win: it[6] },
  })) });
};
REG.indexOverlay = (el, card) => {
  const I = D.index;
  const s = [
    { name: "S&M total", short: "S&M total", values: I.total_sm_spend_t3m, color: C.s2 },
    { name: "Altas", short: "Altas", values: I.new_customers_t3m, color: C.s1 },
    { name: "MRR nuevo", short: "MRR nuevo", values: I.new_mrr_cop_t3m, color: C.s3 },
  ];
  legend(card, s.map(x => ({ name: x.name, color: x.color, kind: "line" })).concat([WIN_LEG]), el);
  return lineChart(el, { labels: LAB, series: s, fmt: f.idx, tickKind: "idx", height: 310, ref: { value: 100 }, win: true,
    shades: CUT, endLabels: true, endLabelFmt: (x, v) => x.short + " " + num(v, 0) });
};
const STATUS = {
  not_computable_new_customers_unidentifiable: "altas no identificables en el mes censurado",
  excluded_suspected_spillover: "arrastre de la censura inicial",
  undefined_zero_denominator: "denominador cero",
};
REG.efficiency = (el, card) => {
  const items = [
    ["S&M total / alta", "total_sm_per_new_customer"], ["Generación de demanda / alta", "demand_gen_per_new_customer"], ["Paid Media / alta", "paid_media_per_new_customer"],
    ["S&M total / COP 1 millón de MRR nuevo", "total_sm_per_new_mrr_mm_cop"], ["Generación de demanda / COP 1 millón de MRR nuevo", "demand_gen_per_new_mrr_mm_cop"], ["Paid Media / COP 1 millón de MRR nuevo", "paid_media_per_new_mrr_mm_cop"],
  ];
  legend(card, [{ name: "Razón mensual", color: C.s1 }, { name: "Últimos 3 meses", color: C.ink, kind: "line" }, WIN_LEG], null);
  const res = multiples(el, { cols: 3, minCellW: 250, height: 156, items: items.map(it => ({
    title: it[0], kind: "bars",
    opts: { labels: LAB, series: [{ name: it[0], values: M[it[1]], color: C.s1 }], line: { name: "Últimos 3 meses", values: M[it[1] + "_t3m"], color: C.ink },
            fmt: v => f.u(v, 3), tickKind: "u", shades: CUT, win: true,
            tipNote: i => M.efficiency_status[i] !== "ok" ? "No se calcula: " + (STATUS[M.efficiency_status[i]] || M.efficiency_status[i]) + "." : null },
  })) });
  const inv = { title: "Inversos", table: { cols: [{ key: "m", label: "Mes" }, { key: "a", label: "Altas por 1 u de S&M total", num: true }, { key: "b", label: "MRR nuevo por 1 u de S&M total", num: true }, { key: "c", label: "Altas por 1 u de generación de demanda", num: true }, { key: "d", label: "MRR nuevo por 1 u de generación de demanda", num: true }, { key: "s", label: "Estado" }],
    rows: LAB.map((l, i) => ({ m: l, a: f.num(M.new_customers_per_sm_unit[i], 1), b: f.copFull(M.new_mrr_cop_per_sm_unit[i]), c: f.num(M.new_customers_per_demand_gen_unit[i], 1), d: f.copFull(M.new_mrr_cop_per_demand_gen_unit[i]), s: M.efficiency_status[i] === "ok" ? "ok" : (STATUS[M.efficiency_status[i]] || M.efficiency_status[i]) })) } };
  res.tables.push(inv);
  return res;
};

// ---------------- 05 gasto y adquisición
const TRANSFORM = { "Niveles": "levels", "Cambio mes a mes": "mom_change" };
const TRANSFORM_ES = { levels: "Niveles", mom_change: "Cambio mes a mes" };
const SPEND_ART = { "Paid Media": "Paid Media", "Generación de demanda": "la generación de demanda", "S&M total": "el S&M total" };
const SPEND_MID = { "Paid Media": "Paid Media", "Generación de demanda": "generación de demanda", "S&M total": "S&M total" };
const SPEND_SHORT = { "Paid Media": "Paid Media", "Generación de demanda": "Gen. demanda", "S&M total": "S&M total" };
const OUT_ART = { "Altas": "las altas", "MRR nuevo": "el MRR nuevo" };
const OUT_MID = { "Altas": "altas", "MRR nuevo": "MRR nuevo" };
const corrState = { spend: "S&M total", outcome: "Altas", lag: 0, transform: "Niveles" };
function corrPairs(st) {
  const s = D.corr.spend[st.spend], o = D.corr.outcome[st.outcome], k = st.lag, out = [];
  for (let t = CS; t < N; t++) {
    if (st.transform === "Niveles") { if (t - k < 0) continue; out.push({ t: t, x: s[t - k], y: o[t] }); }
    else { if (t - 1 < CS || t - k - 1 < 0) continue; out.push({ t: t, x: s[t - k] - s[t - k - 1], y: o[t] - o[t - 1] }); }
  }
  return out;
}
function corrRow(st) {
  const tr = TRANSFORM[st.transform];
  return D.corr.rows.find(r => r.spend === st.spend && r.outcome === st.outcome && r.lag_months === st.lag && r.transform === tr);
}
function corrHeadline(st, r) {
  const lag = st.lag === 0 ? "en el mismo mes" : st.lag === 1 ? "1 mes antes" : st.lag + " meses antes";
  const what = st.transform === "Niveles" ? "" : " (cambios mes a mes)";
  if (r.pearson_p < 0.05 && r.pearson_r < 0) return "Más " + SPEND_MID[st.spend] + " " + lag + " se asocia con menos " + OUT_MID[st.outcome] + what;
  if (r.pearson_p < 0.05 && r.pearson_r > 0) return "Más " + SPEND_MID[st.spend] + " " + lag + " se mueve junto con más " + OUT_MID[st.outcome] + what;
  return "No se observa una relación clara entre " + SPEND_ART[st.spend] + " " + lag + " y " + OUT_ART[st.outcome] + what;
}
function updateCorrText() {
  const r = corrRow(corrState);
  const pairs = corrPairs(corrState);
  if (r.n !== pairs.length) console.error("n no coincide", r.n, pairs.length);
  const lev = corrState.transform === "Niveles";
  $("scatterTitle").textContent = corrHeadline(corrState, r);
  $("scatterSub").textContent = "Cada punto es un mes de resultado (" + mlab(r.window.split("..")[0]) + " → " + mlab(r.window.split("..")[1]) + "). x = " + corrState.spend + " en t−" + corrState.lag + (lev ? "" : " (cambio vs mes anterior)") + ".";
  $("lagTitle").textContent = corrState.spend + " (t−" + corrState.lag + ") y " + OUT_MID[corrState.outcome] + " (t), estandarizadas";
  const st = $("corrStats");
  st.replaceChildren();
  [["r de Pearson", f.r(r.pearson_r), "p = " + f.p(r.pearson_p)], ["ρ de Spearman", f.r(r.spearman_rho), "p = " + f.p(r.spearman_p)], ["Meses (n)", String(r.n), lev ? "niveles" : "cambios mes a mes"]].forEach(x => {
    const d = H("div", "stat", st); H("div", "k", d, x[0]); H("div", "v", d, x[1]); H("div", "s", d, x[2]);
  });
}
REG.scatter = el => {
  const st = corrState;
  const pairs = corrPairs(st);
  const isMRR = st.outcome === "MRR nuevo";
  const lev = st.transform === "Niveles";
  return scatter(el, {
    points: pairs.map(p => ({ x: p.x, y: p.y, label: LAB[p.t] + (st.lag ? " · gasto de " + LAB[p.t - st.lag] : "") })),
    xFmt: v => f.u(v), yFmt: isMRR ? f.cop : f.int, xKind: "u", yKind: isMRR ? "cop" : "int",
    xName: st.spend + " (t−" + st.lag + ")" + (lev ? "" : " Δ"), yName: st.outcome + (lev ? "" : " Δ"),
    xTitle: st.spend + " en t−" + st.lag + (lev ? "" : ", cambio vs mes anterior"),
    yTitle: st.outcome + (lev ? "" : ", cambio vs mes anterior"), color: C.s1, height: 330,
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
    { name: st.outcome + " (t)", values: ys, color: C.s1, tip: (i, v) => f.z(v) + " · " + (st.outcome === "MRR nuevo" ? f.cop : f.int)(pairs.find(p => p.t === i).y) },
  ];
  legend(card, s.map(x => ({ name: x.name, color: x.color, kind: "line" })).concat([WIN_LEG]), null);
  return lineChart(el, { labels: LAB, series: s, fmt: f.z, tickKind: "z", height: 330, includeZero: true, win: true });
};
function corrHeat(el, transform) {
  const combos = [];
  ["Altas", "MRR nuevo"].forEach(o => ["Paid Media", "Generación de demanda", "S&M total"].forEach(s => combos.push([s, o])));
  const tr = TRANSFORM[transform];
  const find = (s, o, k) => D.corr.rows.find(r => r.spend === s && r.outcome === o && r.lag_months === k && r.transform === tr);
  const values = combos.map(c => [0, 1, 2, 3].map(k => find(c[0], c[1], k).pearson_r));
  let selected = null;
  if (corrState.transform === transform) selected = [combos.findIndex(c => c[0] === corrState.spend && c[1] === corrState.outcome), corrState.lag];
  return heatmap(el, {
    rows: combos.map(c => SPEND_SHORT[c[0]] + " vs " + c[1]), cols: ["t", "t−1", "t−2", "t−3"], values: values, rowTitle: "Gasto vs resultado",
    color: divColor, text: v => f.r(v), fmt: f.r, cellH: 34, minTextW: 30, selected: selected,
    textStrong: (i, j) => find(combos[i][0], combos[i][1], j).pearson_p < 0.05,
    tip: (i, j) => { const r = find(combos[i][0], combos[i][1], j); return { title: combos[i][0] + " (t−" + j + ") vs " + combos[i][1] + " (t)", rows: [
      { kind: "none", label: "r de Pearson", value: f.r(r.pearson_r) + "  (p " + f.p(r.pearson_p) + ")" },
      { kind: "none", label: "ρ de Spearman", value: f.r(r.spearman_rho) + "  (p " + f.p(r.spearman_p) + ")" },
      { kind: "none", label: "meses", value: String(r.n) }], note: "Haz clic para inspeccionarla en la dispersión." }; },
    onPick: (i, j) => { setCorr({ spend: combos[i][0], outcome: combos[i][1], lag: j, transform: transform }); },
  });
}
REG.corrLevels = el => {
  const res = corrHeat(el, "Niveles");
  const sens = D.corr.sens.filter(r => r.transform === "levels");
  res.tables = [{ title: "Niveles (ventana limpia)", table: res.table }, { title: "Sensibilidad: niveles incluyendo feb-22", table: {
    cols: [{ key: "a", label: "Gasto vs resultado" }, { key: "k", label: "Rezago", num: true }, { key: "r", label: "r de Pearson", num: true }, { key: "n", label: "n", num: true }],
    rows: sens.map(r => ({ a: r.spend + " vs " + r.outcome, k: r.lag_months, r: f.r(r.pearson_r), n: r.n })) } }];
  delete res.table;
  return res;
};
REG.corrMom = el => {
  const res = corrHeat(el, "Cambio mes a mes");
  res.tables = [{ title: "Cambios mes a mes", table: res.table }, { title: "Todas las correlaciones (ventana limpia)", table: {
    cols: [{ key: "a", label: "Gasto vs resultado" }, { key: "t", label: "Transformación" }, { key: "k", label: "Rezago", num: true }, { key: "n", label: "n", num: true },
           { key: "r", label: "r de Pearson", num: true }, { key: "rp", label: "p", num: true }, { key: "s", label: "ρ de Spearman", num: true }, { key: "sp", label: "p", num: true }],
    rows: D.corr.rows.map(r => ({ a: r.spend + " vs " + r.outcome, t: TRANSFORM_ES[r.transform] || r.transform, k: r.lag_months, n: r.n, r: f.r(r.pearson_r), rp: f.p(r.pearson_p), s: f.r(r.spearman_rho), sp: f.p(r.spearman_p) })) } }];
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

// ---------------- 06 industrias
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
  const Yr = D.industry.year;
  const s = [2022, 2023, 2024].map(y => ({ name: YNAME(y), color: YEARC[y], values: IND.map(ind => kind === "mean"
    ? (Yr.find(r => r.year === y && r.industry === ind) || {}).new_mrr_per_new_customer_cop
    : D.decomp.medians[y][ind]) }));
  if (kind === "mean") legend(card, s.map(x => ({ name: x.name, color: x.color, kind: "dot" })), null);
  const counts = y => IND.map(ind => (Yr.find(r => r.year === y && r.industry === ind) || {}).new_customers);
  const head = H("div", "cell-t", null, kind === "mean" ? "Promedio" : "Mediana");
  const res = dots(el, { rows: IND, series: s, fmt: f.cop, tickKind: "cop", rowTitle: "Industria",
    note: i => "Altas: " + [2022, 2023, 2024].map(y => y + " " + f.int(counts(y)[i])).join(" · ") });
  el.prepend(head);
  res.tables = [{ title: kind === "mean" ? "Ticket de entrada promedio (MRR nuevo ÷ altas)" : "Ticket de entrada mediano (M0)", table: res.table }];
  delete res.table;
  return res;
}
REG.ticketIndMean = (el, card) => ticketInd(el, card, "mean");
REG.ticketIndMedian = (el, card) => ticketInd(el, card, "median");
REG.arpaIndustry = el => {
  const d22 = monthIdx("2022-12");
  return multiples(el, { cols: 3, minCellW: 250, height: 156, sharedY: true, items: IND.map(ind => {
    const a = D.industry.monthly[ind].mrr_per_active_customer_cop;
    return {
      title: ind, right: f.pctSigned(a[N - 1] / a[d22] - 1) + " vs " + LAB[d22], kind: "line",
      opts: { labels: LAB, series: [
        { name: ind, values: a, color: INDC[ind] },
        { name: "Empresa", values: M.mrr_per_active_customer_cop, color: C.de, width: 1.5 }], fmt: f.cop, tickKind: "cop" },
    };
  }) });
};

// ---------------- 07 mix vs. efecto dentro
REG.decompWaterfall = el => {
  const d = D.decomp.main["2022_2024"];
  return waterfall(el, { title: "Ticket de entrada 2022 → 2024", height: 320, fmt: f.cop, steps: [
    { label: "2022\nmar–dic", value: d.A0, kind: "total", color: C.de, extra: [{ kind: "none", label: "altas", value: f.int(d.n0) }] },
    { label: "Mix de\nindustrias", short: "Mix", value: d.mix, kind: "delta", color: C.s2, note: "Intervalo de 90%: " + f.cop(d.mix_ci90_lo) + " a " + f.cop(d.mix_ci90_hi) },
    { label: "Dentro de las\nindustrias", short: "Dentro", value: d.within, kind: "delta", color: C.s1, note: "Intervalo de 90%: " + f.cop(d.within_ci90_lo) + " a " + f.cop(d.within_ci90_hi) },
    { label: "2024\nene–oct", value: d.A1, kind: "total", color: C.de, extra: [{ kind: "none", label: "altas", value: f.int(d.n1) }] },
  ] });
};
REG.decompEvolution = (el, card) => {
  const E = D.decomp.evolution;
  const s = [
    { name: "Dentro de las industrias", values: E.map(e => e.within_cop), color: C.s1 },
    { name: "Mix de industrias", values: E.map(e => e.mix_cop), color: C.s2 },
  ];
  const line = { name: "Brecha total vs 2022", values: E.map(e => e.gap_vs_2022_cop), color: C.ink };
  legend(card, s.map(x => ({ name: x.name, color: x.color })).concat([{ name: line.name, color: line.color, kind: "line" }]), el);
  return barChart(el, { labels: E.map(e => e.half), series: s, stacked: true, line: line, fmt: f.cop, tickKind: "cop", height: 320, maxBar: 34, xTitle: "Semestre",
    extraRows: i => [{ kind: "none", label: "ticket promedio", value: f.cop(E[i].mean_m0_cop) }, { kind: "none", label: "ticket mediano", value: f.cop(E[i].median_m0_cop) }, { kind: "none", label: "altas", value: f.int(E[i].n) }] });
};

// ---------------- 08 cohortes
const REV = "Retención de ingreso vs M0";
const cohState = { metric: "Retención de logos", gran: "Trimestrales" };
const METRIC = {
  "Retención de logos": { key: "logo", fmt: v => f.pct(v), sfmt: v => f.pct(v, 0), dom: [0.6, 1], kind: "pct", title: "Porcentaje de cada cohorte que sigue pagando, por meses desde el primer pago" },
  [REV]: { key: "revenue", fmt: v => f.pct(v), sfmt: v => f.pct(v, 0), dom: [0.3, 1.1], kind: "pct", title: "MRR de la cohorte como porcentaje del MRR en M0 de esos mismos clientes" },
  "MRR por cliente original": { key: "arpu", fmt: f.cop, dom: null, kind: "cop", title: "MRR de la cohorte dividido entre los clientes observables en cada mes. Celdas en miles de COP" },
};
function cohortRows() {
  const Q = D.cohorts.quarterly, Mo = D.cohorts.monthly;
  if (cohState.gran === "Trimestrales") return Q.map(q => ({ label: q.cohort + (q.partial ? "*" : ""), size: q.size, data: q, obs: q.observable, y2022: String(q.cohort).startsWith("2022") }));
  return Mo.map(m => ({ label: mlab(m.cohort) + (m.flag !== "clean" ? " ⚑" : ""), size: m.size, data: m, obs: null, flagged: m.flag !== "clean", y2022: String(m.cohort).startsWith("2022") }));
}
function scaleLegend(target, dom, fmt, ramp) {
  target.replaceChildren();
  const wrap = H("div", null, target);
  wrap.style.cssText = "display:flex;align-items:center;gap:10px;font-size:11.5px;color:var(--muted)";
  H("span", null, wrap, fmt(dom[0]));
  const bar = H("span", null, wrap);
  bar.style.cssText = "width:180px;height:10px;border-radius:6px;background:linear-gradient(90deg," + ramp.join(",") + ")";
  H("span", null, wrap, fmt(dom[1]) + (cohState.metric === REV ? " o más" : ""));
}
REG.cohortHeat = (el, card) => {
  const mt = METRIC[cohState.metric];
  const rows = cohortRows();
  const maxK = Math.max(...rows.map(r => r.data[mt.key].length));
  const cols = range(0, maxK).map(k => "M" + k);
  const values = rows.map(r => cols.map((c, k) => r.data[mt.key][k] === undefined ? null : r.data[mt.key][k]));
  let dom = mt.dom;
  if (!dom) { const vs = values.flat().filter(ok); dom = [Math.min(...vs), Math.max(...vs)]; }
  const rev = cohState.metric === REV;
  $("cohortHeatTitle").textContent = cohState.metric + " · cohortes " + cohState.gran.toLowerCase();
  $("cohortHeatSub").textContent = mt.title + ". Filas = cohortes (n en el tooltip); columnas = meses desde el primer pago.";
  scaleLegend($("cohortScale"), dom, mt.sfmt || mt.fmt, SEQ);
  return heatmap(el, { rows: rows.map(r => r.label), cols: cols, values: values, rowTitle: "Cohorte", color: v => seqColor(v, dom[0], dom[1]),
    text: cohState.gran === "Trimestrales" ? (v => cohState.metric === "MRR por cliente original" ? num(v / 1e3, 0) : num(v * 100, 0)) : null,
    minTextW: 26, fmt: mt.fmt, cellH: cohState.gran === "Trimestrales" ? 26 : 15, highlightCols: [1, 3, 6, 12, 24],
    rowStrong: i => rev && rows[i].y2022,
    tip: (i, j, v) => ({ title: rows[i].label + " · M" + j, rows: [
      { kind: "none", label: cohState.metric, value: mt.fmt(v) },
      { kind: "none", label: "tamaño de la cohorte", value: f.int(rows[i].size) }].concat(rows[i].obs ? [{ kind: "none", label: "observables en M" + j, value: f.int(rows[i].obs[j]) }] : []),
      note: rows[i].flagged ? "Marcada: arrastre de la censura inicial."
        : (rev && rows[i].y2022 ? "Precaución: el M0 de 2022 incluye pagos iniciales grandes; esta retención se subestima." : null) }) });
};
REG.cohortCurves = (el, card) => {
  const mt = METRIC[cohState.metric];
  const Yr = D.cohorts.yearly;
  const maxK = Math.max(...Yr.map(y => y[mt.key].length));
  const labels = range(0, maxK).map(k => "M" + k);
  const s = Yr.map(y => ({ name: y.cohort + " · n " + f.int(y.size), short: y.cohort.slice(0, 4), color: YEARC[y.cohort.slice(0, 4)],
    values: labels.map((l, k) => (y.observable[k] >= 40 ? y[mt.key][k] : null)),
    tip: (k, v) => mt.fmt(v) + " · " + f.int(y.observable[k]) + " obs." }));
  $("cohortCurveTitle").textContent = cohState.metric + " por año de alta";
  legend(card, s.map(x => ({ name: x.name, color: x.color, kind: "line" })), el);
  return lineChart(el, { labels: labels, series: s, fmt: mt.fmt, tickKind: mt.kind, height: 300, includeZero: cohState.metric === "MRR por cliente original",
    endLabels: true, endLabelFmt: (x, v) => x.short + " " + (mt.kind === "cop" ? f.copShort(v) : mt.fmt(v)), xTitle: "Meses desde el primer pago",
    tipNote: () => cohState.metric === REV ? "Precaución: la curva de 2022 parte de un M0 con pagos iniciales grandes." : null });
};
REG.baseCurves = (el, card) => {
  const B = D.cohorts.flagged.left_censored_base;
  const s = [
    { name: "Sigue pagando (logos)", short: "Logos", values: B.logo_calendar, color: C.s1 },
    { name: "MRR de " + LAB[0] + " conservado (ingreso)", short: "Ingreso", values: B.revenue_calendar, color: C.s2 },
  ];
  legend(card, s.map(x => ({ name: x.name, color: x.color, kind: "line" })), el);
  return lineChart(el, { labels: LAB, series: s, fmt: v => f.pct(v), tickKind: "pct", height: 300, includeZero: false, ref: { value: 1 },
    endLabels: true, endLabelFmt: (x, v) => x.short + " " + f.pct(v, 0),
    extraRows: i => [{ kind: "none", label: "MRR de este grupo", value: f.cop(B.mrr_calendar_cop[i]) }] });
};
function togglePrec(cardId, on) {
  const top = document.querySelector("#" + cardId + " .card-top");
  if (!top) return;
  let t = top.querySelector("[data-dyn-prec]");
  if (on && !t) {
    let wrap = top.querySelector(".tags");
    if (!wrap) { wrap = H("span", "tags", top); top.querySelectorAll(":scope > .tag").forEach(x => wrap.appendChild(x)); }
    t = tagEl("Precaución");
    t.dataset.dynPrec = "1";
    wrap.appendChild(t);
  }
  if (!on && t) t.remove();
}
function setCoh(patch) {
  Object.assign(cohState, patch);
  document.querySelectorAll("#cohortControls .seg").forEach(seg => {
    const key = seg.dataset.key;
    seg.querySelectorAll("button").forEach(b => b.setAttribute("aria-pressed", String(b.textContent === cohState[key])));
  });
  const rev = cohState.metric === REV;
  $("cohortRevWarn").hidden = !rev;
  togglePrec("card-8-1", rev);
  togglePrec("card-8-2", rev);
  ["cohortHeat", "cohortCurves"].forEach(rerender);
}

// ---------------- 09 movimientos
const MOVN = { New: "Nuevo", Expansion: "Expansión", Reactivation: "Reactivación", Contraction: "Contracción", Churn: "Churn" };
const MOVS = { New: "Nuevo", Expansion: "Exp.", Reactivation: "React.", Contraction: "Contr.", Churn: "Churn" };
REG.bridgeMonthly = (el, card) => {
  const idx = range(1, N);
  const s = [
    { name: MOVN.New, values: idx.map(i => M.new_mrr_cop[i]), color: MOV.New },
    { name: MOVN.Expansion, values: idx.map(i => M.expansion_mrr_cop[i]), color: MOV.Expansion },
    { name: MOVN.Reactivation, values: idx.map(i => M.reactivation_mrr_cop[i]), color: MOV.Reactivation },
    { name: MOVN.Contraction, values: idx.map(i => M.contraction_mrr_cop[i]), color: MOV.Contraction },
    { name: MOVN.Churn, values: idx.map(i => M.churned_mrr_cop[i]), color: MOV.Churn },
  ];
  const line = { name: "Cambio neto", values: idx.map(i => M.net_mrr_change_cop[i]), color: C.ink };
  legend(card, s.map(x => ({ name: x.name, color: x.color })).concat([{ name: line.name, color: line.color, kind: "line" }, WIN_LEG]), el);
  return barChart(el, { labels: idx.map(i => LAB[i]), series: s, stacked: true, line: line, fmt: f.cop, tickKind: "cop", height: 340, win: true,
    dim: [0], dimNote: "feb-22: el MRR nuevo incluye arrastre de la censura inicial.",
    extraRows: i => [{ kind: "none", label: "MRR al cierre del mes", value: f.cop(M.total_paid_mrr_cop[i + 1]) }, { kind: "none", label: "residuo del puente", value: "COP " + num(Math.abs(M.mrr_bridge_diff_cop[i + 1]), 2) }] });
};
REG.bridgeLast = el => {
  const b = D.bridge.last;
  const steps = [
    { label: mlab(b.from_month) + "\nMRR", value: b.opening_mrr_cop, kind: "total", color: C.de },
    { label: MOVN.New, short: MOVS.New, value: b.new_mrr_cop, kind: "delta", color: MOV.New },
    { label: MOVN.Expansion, short: MOVS.Expansion, value: b.expansion_mrr_cop, kind: "delta", color: MOV.Expansion },
    { label: MOVN.Reactivation, short: MOVS.Reactivation, value: b.reactivation_mrr_cop, kind: "delta", color: MOV.Reactivation },
    { label: MOVN.Contraction, short: MOVS.Contraction, value: b.contraction_mrr_cop, kind: "delta", color: MOV.Contraction },
    { label: MOVN.Churn, short: MOVS.Churn, value: b.churned_mrr_cop, kind: "delta", color: MOV.Churn },
    { label: mlab(b.to_month) + "\nMRR", value: b.closing_mrr_cop, kind: "total", color: C.de },
  ];
  let run = 0, lo = Infinity, hi = -Infinity;
  steps.forEach(s => { if (s.kind === "total") run = s.value; else run += s.value; lo = Math.min(lo, run); hi = Math.max(hi, run); });
  const span = hi - lo;
  const yMin = niceTicks(lo - span * 0.9, hi, 5)[0];
  const st = $("lastCheck");
  st.replaceChildren();
  [["Apertura", f.cop2(b.opening_mrr_cop)], ["Movimientos netos", f.copSigned(b.net_change_cop)], ["Cierre", f.cop2(b.closing_mrr_cop)], ["Residuo", "COP " + num(Math.abs(b.check_diff_cop), 2) + " ✓"]].forEach(x => {
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
  return barChart(el, { labels: mv.returnYears.map(String), series: s, stacked: true, yMin: 0, yMax: 1, fmt: v => f.pct(v), tickKind: "pct", height: 300, maxBar: 64, xTitle: "Año del churn",
    tipRows: i => s.slice().reverse().map((x, jj) => { const j = s.length - 1 - jj; return { color: x.color, kind: "rect", label: x.name, value: f.pct(x.values[i]) + " · " + f.int(mv.returnCounts[i][j]) }; }),
    tipNote: i => f.int(tot[i]) + " churns en " + mv.returnYears[i] + (i === 0 ? " (desde feb-22)" : "") + "." });
};
REG.smallAdjust = (el, card) => {
  const sm = D.movements.small;
  const halves = sm.map(r => r.half);
  const grid = D.movements.gridHalf;
  const s = [
    { name: "Expansiones menores a 10%", values: sm.map(r => r.expansion_small_share), color: MOV.Expansion, tip: (i, v) => f.pct(v, 0) + " · " + f.int(sm[i].expansion_small) + " de " + f.int(sm[i].expansion_events) },
    { name: "Contracciones menores a 10%", values: sm.map(r => r.contraction_small_share), color: MOV.Contraction, tip: (i, v) => f.pct(v, 0) + " · " + f.int(sm[i].contraction_small) + " de " + f.int(sm[i].contraction_events) },
    { name: "Clientes que pagan fuera de la grilla de COP 2.100", values: halves.map(h => { const g = grid.find(x => x.half === h); return g ? 1 - g.share : null; }), color: C.s1 },
  ];
  legend(card, s.map(x => ({ name: x.name, color: x.color, kind: "line" })), el);
  return lineChart(el, { labels: halves, series: s.map(x => Object.assign({ dots: true }, x)), fmt: v => f.pct(v, 0), tickKind: "pct", height: 300, xTitle: "Semestre",
    extraRows: i => [{ kind: "none", label: "MRR de expansión en ajustes pequeños", value: f.cop(sm[i].expansion_small_mrr_cop) + " de " + f.cop(sm[i].expansion_mrr_cop) }] });
};

/* ================================================================== estados epistémicos */
const EST = {
  "Hecho observado": ["hecho", "✓"], "Evidencia fuerte": ["fuerte", "◆"], "Direccional": ["direc", "↗"], "Hipótesis": ["hipo", "~"],
  "No evaluable": ["noeval", "∅"], "Explorando": ["explo", "?"], "Precaución": ["prec", "!"], "Método": ["met", "i"],
};
function tagRaw(cls, icon, label) { const t = H("span", "tag " + cls); H("i", null, t, icon); t.append(label); return t; }
function tagEl(label) { const d = EST[label] || ["met", "i"]; return tagRaw(d[0], d[1], label); }

/* ================================================================== TABLAS (estáticas) */
function buildTables() {
  const A = D.audit, at = A.transactions, ai = A.industry, as = A.sm, co = A.consistency;
  const yes = b => (b ? "sí" : "no");
  const auditRows = [
    { d: "Grano", t: "cliente × mes (foto mensual)", i: "cliente", s: "mes" },
    { d: "Filas", t: f.int(at.rows) + " = " + f.int(at.customers) + " × " + at.months, i: f.int(ai.rows_read) + " leídas · " + f.int(ai.rows_valid) + " válidas", s: String(as.rows) },
    { d: "Clientes", t: f.int(at.customers), i: f.int(ai.unique_ids) + " (IDs " + ai.id_min + "–" + f.int(ai.id_max) + ", contiguos: " + yes(ai.ids_contiguous_1_to_n) + ")", s: "–" },
    { d: "Rango de fechas", t: mlab(at.first_month) + " → " + mlab(at.last_month) + " (" + at.months + " meses)", i: "–", s: mlab(as.first_month) + " → " + mlab(as.last_month) + " (" + as.months + " meses)" },
    { d: "Duplicados", t: at.duplicate_customer_month + " (ID, mes) · " + at.duplicate_full_rows + " filas completas", i: ai.duplicate_ids + " IDs", s: as.duplicate_months + " meses" },
    { d: "Valores faltantes", t: "0 (" + Object.values(at.empty_strings).reduce((a, b) => a + b, 0) + " textos vacíos)", i: ai.blank_rows + " fila completamente vacía (eliminada)", s: String(as.missing_values) },
    { d: "Tipos: crudo → leído", t: "texto → entero · mes · decimal (exacto a 1e-6)", i: "texto → entero · texto", s: "texto “$x.xxx” → decimal" },
    { d: "Ceros y negativos", t: f.int(at.zero_amount_rows) + " filas en cero (" + f.pct(at.zero_share) + ") · " + at.negative_amounts + " negativas", i: "–", s: "Freelance en 0 en " + as.components.Freelance.zeros + " meses · PayrollExpenses < 0 en " + as.components.PayrollExpenses.negatives },
    { d: "Valores extremos", t: f.int(at.rows_above_iqr_fence) + " filas > Q3 + 3·RIC (" + at.customers_above_iqr_fence + " clientes); máximo " + f.cop2(at.amount_max * D.meta.scaleToCop), i: "–", s: "Paid Media " + FACT.pm_drop + " de pico a valle (2023)" },
    { d: "Precisión decimal", t: Object.entries(at.decimal_places).map(e => e[0] + " dec.: " + f.int(e[1])).join(" · "), i: "–", s: as.value_format },
    { d: "Nombres", t: "BOM en el encabezado · se llama “Transactions” pero el grano es mensual", i: "BOM · IDs “Cliente N” · encabezados ES/EN", s: "BOM: " + yes(as.utf8_bom) + " · rubros en ES/EN" },
    { d: "Consistencia", t: "IDs cruzados: " + f.pct(co.id_match_rate, 0), i: "IDs sin transacciones: " + co.industry_ids_without_tx.length, s: "Meses idénticos a Transactions: " + yes(co.sm_months_equal_tx_months) },
  ];
  table($("auditTable"), [{ key: "d", label: "Revisión" }, { key: "t", label: "Transactions.csv" }, { key: "i", label: "Industry.csv" }, { key: "s", label: "S&M_spend.csv" }], auditRows);

  const comp = as.components;
  const g = [
    ["PaidMedia", GRP.dg, "Gasto en medios para generar demanda", "–"],
    ["PublicidadNoWeb", GRP.dg, "Publicidad fuera de la web", "–"],
    ["Team", GRP.sc, "Costo de personas del equipo de S&M (supuesto)", "12,0% del total hasta " + FACT.team_fixed_until],
    ["PayrollExpenses", GRP.sc, "Costo de nómina; puede traslaparse con Team", "negativo en " + comp.PayrollExpenses.negatives + " meses"],
    ["Travel", GRP.sc, "Viajes comerciales (supuesto)", "–"],
    ["SoftwareTools", GRP.en, "Herramientas; puede incluir software que no es de S&M", "–"],
    ["Freelance", GRP.en, "Apoyo externo (¿contenido, diseño, SDR?)", "0 en " + comp.Freelance.zeros + " meses"],
  ];
  table($("smGroupTable"), [{ key: "c", label: "Rubro" }, { key: "g", label: "Grupo analítico" }, { key: "r", label: "Por qué (hipótesis)" }, { key: "mn", label: "Mín.", num: true }, { key: "mx", label: "Máx.", num: true }, { key: "a", label: "Anomalía" }],
    g.map(x => ({ c: x[0], g: x[1], r: x[2], mn: f.u(comp[x[0]].min), mx: f.u(comp[x[0]].max), a: x[3] })));

  const VENT = { completa: "Completa · " + FACT.window_start + " → " + FACT.window_end, limpia: "Limpia · " + LAB[CS] + " → " + FACT.window_end };
  const dt = table($("defsTable"), [
    { key: "n", label: "Métrica", node: (v, r) => { const w = H("span"); H("b", null, w, v); H("br", null, w); H("code", null, w, r.id); return w; } },
    { key: "d", label: "Definición", node: v => rich(H("span"), v) },
    { key: "fo", label: "Fórmula", node: v => H("code", null, null, v) },
    { key: "v", label: "Ventana" },
    { key: "u", label: "Unidad" },
  ], Object.values(BR.metrics).map(m => ({ id: m.id, n: m.nombre, d: m.definicion, fo: m.formula, v: VENT[m.ventana] || m.ventana, u: m.unidad })));
  dt.classList.add("defs");

  const TB = D.ticket.byYear;
  const byY = y => TB.find(r => r.year === y);
  const tmetrics = [
    ["Altas (n)", "new_customers", f.int, false],
    ["M0 promedio · métrica pedida", "m0_mean_cop", f.cop, true],
    ["M0 mediana", "m0_median_cop", f.cop, true],
    ["M0 P25", "m0_p25_cop", f.cop, true], ["M0 P75", "m0_p75_cop", f.cop, true], ["M0 P90", "m0_p90_cop", f.cop, true],
    ["M0 promedio winsorizado en P99", "m0_winsor_mean_cop", f.cop, true],
    ["Run-rate temprano (promedio)", "early_run_rate_mean_cop", f.cop, true],
    ["Run-rate temprano (mediana)", "early_run_rate_median_cop", f.cop, true],
    ["M1 promedio (incluye ceros)", "m1_mean_cop", f.cop, true],
    ["% con pico en el primer mes (> 1,5× M1)", "share_first_month_spike", v => f.pct(v), false],
  ];
  table($("ticketTable"), [{ key: "m", label: "Métrica" }, { key: "a", label: YNAME(2022), num: true }, { key: "b", label: "2023", num: true }, { key: "c", label: YNAME(2024), num: true }, { key: "d", label: "Δ 2022 → 2024", num: true }],
    tmetrics.map(x => ({ m: x[0], a: x[2](byY(2022)[x[1]]), b: x[2](byY(2023)[x[1]]), c: x[2](byY(2024)[x[1]]), d: x[3] ? f.pctSigned(byY(2024)[x[1]] / byY(2022)[x[1]] - 1) : "–" })));

  const E = D.efficiencyByYear;
  const eY = y => E.find(r => r.year === y);
  const em = [
    ["S&M total / alta", "total_sm_per_new_customer", v => f.u(v)], ["Generación de demanda / alta", "demand_gen_per_new_customer", v => f.u(v)], ["Paid Media / alta", "paid_media_per_new_customer", v => f.u(v)],
    ["S&M total / COP 1 millón de MRR nuevo", "total_sm_per_new_mrr_mm", v => f.u(v, 2)], ["Generación de demanda / COP 1 millón de MRR nuevo", "demand_gen_per_new_mrr_mm", v => f.u(v, 2)], ["Paid Media / COP 1 millón de MRR nuevo", "paid_media_per_new_mrr_mm", v => f.u(v, 2)],
  ];
  const erows = em.map(x => ({ m: x[0], a: x[2](eY(2022)[x[1]]), b: x[2](eY(2023)[x[1]]), c: x[2](eY(2024)[x[1]]), d: f.pctSigned(eY(2024)[x[1]] / eY(2022)[x[1]] - 1) }));
  erows.push({ _cls: "sep", m: "Altas por 1 u de S&M total", a: f.num(1 / eY(2022).total_sm_per_new_customer, 1), b: f.num(1 / eY(2023).total_sm_per_new_customer, 1), c: f.num(1 / eY(2024).total_sm_per_new_customer, 1), d: f.pctSigned(eY(2022).total_sm_per_new_customer / eY(2024).total_sm_per_new_customer - 1) });
  erows.push({ m: "MRR nuevo por 1 u de S&M total", a: f.cop(1e6 / eY(2022).total_sm_per_new_mrr_mm), b: f.cop(1e6 / eY(2023).total_sm_per_new_mrr_mm), c: f.cop(1e6 / eY(2024).total_sm_per_new_mrr_mm), d: f.pctSigned(eY(2022).total_sm_per_new_mrr_mm / eY(2024).total_sm_per_new_mrr_mm - 1) });
  table($("effTable"), [{ key: "m", label: "Razón" }, { key: "a", label: "2022", num: true }, { key: "b", label: "2023", num: true }, { key: "c", label: "2024", num: true }, { key: "d", label: "Δ 22→24", num: true }], erows);

  const IY = D.industry.year;
  const irows = [];
  [2022, 2023, 2024].forEach((y, k) => IND.forEach((ind, j) => {
    const r = IY.find(x => x.year === y && x.industry === ind);
    irows.push({ _cls: j === 0 && k > 0 ? "sep" : null, y: j === 0 ? YNAME(y) : "", ind: ind,
      act: f.int(r.active_customers_end), sa: f.pct(r.share_active_end), mrr: f.cop(r.mrr_end_cop), sm: f.pct(r.share_mrr_end), arpa: f.cop(r.arpa_end_cop),
      nw: f.int(r.new_customers), sn: f.pct(r.share_new_customers), tk: f.cop(r.new_mrr_per_new_customer_cop), ch: f.pct(r.avg_monthly_logo_churn_rate), re: f.int(r.reactivated_customers),
      ex: f.cop(r.expansion_mrr_cop), co: f.cop(r.contraction_mrr_cop), cm: f.cop(r.churned_mrr_cop) });
  }));
  table($("industryTable"), [{ key: "y", label: "Año" }, { key: "ind", label: "Industria" }, { key: "act", label: "Activos (cierre)", num: true }, { key: "sa", label: "% activos", num: true },
    { key: "mrr", label: "MRR (cierre)", num: true }, { key: "sm", label: "% MRR", num: true }, { key: "arpa", label: "MRR / cliente (cierre)", num: true }, { key: "nw", label: "Altas", num: true }, { key: "sn", label: "% altas", num: true },
    { key: "tk", label: "Ticket de entrada", num: true }, { key: "ch", label: "Churn de logos / mes", num: true }, { key: "re", label: "Reactivaciones", num: true }, { key: "ex", label: "MRR de expansión", num: true },
    { key: "co", label: "MRR de contracción", num: true }, { key: "cm", label: "MRR de churn", num: true }], irows);

  const DT = D.decomp.details["2022_2024"];
  const dtr = DT.map(r => ({ i: r.industry, n0: f.int(r.n0), n1: f.int(r.n1), s0: f.pct(r.share0), s1: f.pct(r.share1), a0: f.cop(r.mean0), a1: f.cop(r.mean1), mx: f.cop(r.mix_contribution), wi: f.cop(r.within_contribution) }));
  const dm = D.decomp.main["2022_2024"];
  dtr.push({ _cls: "sep", i: "Total", n0: f.int(dm.n0), n1: f.int(dm.n1), s0: "100%", s1: "100%", a0: f.cop(dm.A0), a1: f.cop(dm.A1), mx: f.cop(dm.mix), wi: f.cop(dm.within) });
  table($("decompIndTable"), [{ key: "i", label: "Industria" }, { key: "n0", label: "n 2022", num: true }, { key: "n1", label: "n 2024", num: true }, { key: "s0", label: "% 2022", num: true }, { key: "s1", label: "% 2024", num: true },
    { key: "a0", label: "Ticket 2022", num: true }, { key: "a1", label: "Ticket 2024", num: true }, { key: "mx", label: "Contribución del mix", num: true }, { key: "wi", label: "Contribución dentro", num: true }], dtr);

  table($("decompRobustTable"), [{ key: "c", label: "Comparación" }, { key: "v", label: "Variante" }, { key: "a0", label: "Desde", num: true }, { key: "a1", label: "Hasta", num: true }, { key: "d", label: "Δ", num: true },
    { key: "m", label: "Mix", num: true }, { key: "w", label: "Dentro", num: true }, { key: "ws", label: "% dentro", num: true }, { key: "ci", label: "IC 90% de % dentro", num: true }, { key: "l", label: "Laspeyres: mix / dentro / interacción", num: true }],
    D.decomp.robust.map((r, k) => ({ _cls: k > 0 && k % 3 === 0 ? "sep" : null, c: r.comparison, v: r.variant, a0: f.cop(r.A0), a1: f.cop(r.A1), d: f.copSigned(r.delta), m: f.copSigned(r.mix), w: f.copSigned(r.within),
      ws: Math.abs(r.delta) < 5000 ? "n/s" : f.pct(r.within_share, 0), ci: Math.abs(r.delta) < 5000 ? "n/s" : f.pct(r.within_share_ci90_lo, 0) + " – " + f.pct(r.within_share_ci90_hi, 0),
      l: f.cop(r.laspeyres_mix) + " / " + f.cop(r.laspeyres_within) + " / " + f.cop(r.laspeyres_interaction) })));

  const CSu = D.cohorts.summary;
  table($("cohortTable"), [{ key: "c", label: "Cohorte" }, { key: "n", label: "Tamaño", num: true }, { key: "m0", label: "M0 promedio", num: true }, { key: "md", label: "M0 mediana", num: true },
    { key: "l1", label: "Logos M1", num: true }, { key: "l3", label: "Logos M3", num: true }, { key: "l6", label: "Logos M6", num: true }, { key: "l12", label: "Logos M12", num: true },
    { key: "r1", label: "Ingreso M1", num: true }, { key: "r3", label: "Ingreso M3", num: true }, { key: "r6", label: "Ingreso M6", num: true }, { key: "r12", label: "Ingreso M12", num: true }, { key: "e", label: "Con expansión ≤ M6", num: true }],
    CSu.map(r => ({ c: r.cohort + (r.partial ? "*" : ""), n: f.int(r.size), m0: f.cop(r.m0_mean_cop), md: f.cop(r.m0_median_cop),
      l1: f.pct(r.logo_m1), l3: f.pct(r.logo_m3), l6: f.pct(r.logo_m6), l12: f.pct(r.logo_m12), r1: f.pct(r.revenue_m1), r3: f.pct(r.revenue_m3), r6: f.pct(r.revenue_m6), r12: f.pct(r.revenue_m12), e: f.pct(r.share_expanding_within_m6) })));

  const AB = D.bridge.annual;
  const per = r => mlab(r.period.split("..")[0]) + " → " + mlab(r.period.split("..")[1]);
  const abRows = [["MRR de apertura", "opening_mrr_cop"], ["+ Nuevo", "new_mrr_cop"], ["+ Expansión", "expansion_mrr_cop"], ["+ Reactivación", "reactivation_mrr_cop"],
    ["Contracción", "contraction_mrr_cop"], ["Churn", "churned_mrr_cop"], ["Cambio neto", "net_change_cop"], ["MRR de cierre", "closing_mrr_cop"]].map((x, k) => {
    const r = { m: x[0], _cls: k === 6 ? "sep" : null };
    AB.forEach((a, j) => { r["p" + j] = f.cop(a[x[1]]); });
    return r;
  });
  const res = { m: "Residuo (cierre − apertura − neto)" };
  AB.forEach((a, j) => { res["p" + j] = "COP " + num(Math.abs(a.check_diff_cop), 2); });
  abRows.push(res);
  table($("annualBridgeTable"), [{ key: "m", label: "Componente" }].concat(AB.map((a, j) => ({ key: "p" + j, label: per(a), num: true }))), abRows);

  table($("claimsTable"), [
    { key: "i", label: "ID", node: v => H("code", null, null, v) },
    { key: "dm", label: "Dominio" },
    { key: "es", label: "Estado", node: v => tagEl(v) },
    { key: "c", label: "Afirmación", node: v => rich(H("span"), v) },
    { key: "s", label: "Verificación" },
  ], D.claims.map(c => ({ i: c.id, dm: c.dominio, es: c.estado, c: c.claim, s: c.verified ? "✓ verificada" : "✗ falló" })));

  const fq = $("finoraQuestions");
  BR.questionsFinora.forEach(q => rich(H("li", null, fq), q));
  $("hashes").textContent = Object.entries(D.meta.hashes).map(e => e[0] + " " + e[1]).join(" · ");
}

/* ================================================================== sparks del resumen */
function buildSparks() {
  const map = {
    active: M.active_customers, mrr: M.total_paid_mrr_cop, arpa: M.mrr_per_active_customer_cop,
    new: cleanMask(M.new_customers_3m_avg), ticket: cleanMask(M.median_new_customer_mrr_cop), sm: M.total_sm_spend,
    churn: cleanMask(M.logo_churn_rate), base: D.vintage[VN.base].arpa,
  };
  document.querySelectorAll("[data-spark]").forEach(el => {
    const draw = () => spark(el, map[el.dataset.spark] || []);
    draw();
    new ResizeObserver(draw).observe(el);
  });
}

/* ================================================================== navegación */
function flash(el) {
  if (REDUCED || !el.animate) return;
  el.animate([{ outline: "3px solid rgba(47,109,242,0.55)", outlineOffset: "3px" }, { outline: "3px solid rgba(47,109,242,0)", outlineOffset: "3px" }], { duration: 1600, easing: "ease-out" });
}
function goTo(sel) {
  const el = document.querySelector(sel);
  if (!el) return;
  el.scrollIntoView({ behavior: REDUCED ? "auto" : "smooth", block: "start" });
  try { history.replaceState(null, "", sel); } catch (e) { /* file:// sin historial */ }
  if (el.matches(".card, .dom-card")) setTimeout(() => flash(el), REDUCED ? 0 : 500);
}
function wireNav() {
  // la navegación está agrupada por dominio (orden distinto al del documento): se activa la sección visible
  const links = Array.from(document.querySelectorAll("#nav a"));
  const targets = links.map(a => document.querySelector(a.getAttribute("href")));
  const bar = $("progress");
  let ticking = false;
  const update = () => {
    ticking = false;
    const y = window.innerHeight * 0.28;
    let best = 0, bestTop = -Infinity;
    targets.forEach((s, i) => {
      if (!s) return;
      const top = s.getBoundingClientRect().top;
      if (top <= y && top > bestTop) { bestTop = top; best = i; }
    });
    links.forEach((a, i) => a.classList.toggle("active", i === best));
    const act = links[best];
    if (act && window.innerWidth <= 1180) {
      const nav = $("nav");
      const l = Math.max(0, act.getBoundingClientRect().left - nav.getBoundingClientRect().left + nav.scrollLeft - 20);
      if (Math.abs(nav.scrollLeft - l) > 40) nav.scrollTo({ left: l, behavior: REDUCED ? "auto" : "smooth" });
    }
    const h = document.documentElement.scrollHeight - window.innerHeight;
    bar.style.width = (h > 0 ? (window.scrollY / h) * 100 : 0) + "%";
  };
  window.addEventListener("scroll", () => { if (!ticking) { ticking = true; requestAnimationFrame(update); } }, { passive: true });
  window.addEventListener("resize", update);
  update();
}

/* ================================================================== buscador "¿Qué quieres entender?" */
const DOM_ORDER = ["Resultado", "Adquisición", "Retención", "Monetización de la base", "Inversión comercial"];
const pal = { open: false, items: [], sel: -1, back: null };
let drawerOpen = false, drawerBack = null;
const normTxt = s => String(s).normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
const matches = (hay, q) => { const h = normTxt(hay); return q.split(/\s+/).filter(Boolean).every(t => h.includes(t)); };
function sections() {
  return Array.from(document.querySelectorAll("main .section[id]")).filter(s => s.id !== "intro").map(s => {
    const k = s.querySelector(".kicker");
    const title = Array.from(k.childNodes).filter(n => n.nodeType === 3).map(n => n.textContent).join("").trim();
    return { id: s.id, num: k.querySelector(".num").textContent, title: title, q: (s.querySelector(".question") || {}).textContent || "" };
  });
}
function cardsInfo() {
  return Array.from(document.querySelectorAll("main .card[data-card]")).map(c => ({ key: c.dataset.card, id: c.id, title: (c.querySelector("h3") || {}).textContent || "" }));
}
function palSel(i) {
  pal.sel = pal.items.length ? clamp(i, 0, pal.items.length - 1) : -1;
  pal.items.forEach((it, k) => it.el.classList.toggle("sel", k === pal.sel));
  if (pal.sel >= 0) pal.items[pal.sel].el.scrollIntoView({ block: "nearest" });
}
function palList() {
  const raw = $("palInput").value.trim();
  const q = normTxt(raw);
  const body = $("palBody");
  body.replaceChildren();
  const items = [];
  const group = (name, arr, cls) => {
    if (!arr.length) return;
    H("div", "pal-grp" + (cls ? " " + cls : ""), body, name);
    arr.forEach(it => {
      const b = H("button", "pal-item" + (it.cls ? " " + it.cls : ""), body);
      b.type = "button";
      const t = H("span", "t", b);
      if (it.lead) { H("b", null, t, it.lead); t.append(" "); }
      t.append(it.text);
      if (it.dom) H("span", "dom", b, it.dom);
      if (it.badge) H("span", "b", b, it.badge);
      b.addEventListener("click", it.go);
      b.addEventListener("mousemove", () => { const k = items.indexOf(it); if (k !== pal.sel) palSel(k); });
      it.el = b;
      items.push(it);
    });
  };
  if (raw) {
    group("Tu pregunta", [{ lead: "Preguntar:", text: "«" + (raw.length > 110 ? raw.slice(0, 110) + "…" : raw) + "»", badge: "Enter ↵",
                            cls: "ask", go: () => askFree(raw) }]);
  } else {
    H("div", "pal-hint", body, LIVE && LIVE.libre
      ? "Escribe tu pregunta con tus palabras y pulsa Enter: el agente la investiga en vivo. O elige una frecuente."
      : "Escribe tu pregunta con tus palabras y pulsa Enter, o elige una frecuente.");
  }
  // con texto: coincidencias literales más las respuestas verificadas que el enrutador considera cercanas
  const golden = q ? [...new Set(BR.golden.filter(g => matches(g.pregunta + " " + g.dominio, q)).map(g => g.id)
                        .concat(routeQuestion(raw).filter(r => r.score >= 2).map(r => r.id)))].slice(0, 5).map(id => BR.golden.find(g => g.id === id))
                   : BR.golden.filter(g => g.destacada).sort((a, b) => DOM_ORDER.indexOf(a.dominio) - DOM_ORDER.indexOf(b.dominio));
  group(q ? "Respuestas verificadas relacionadas" : "Preguntas frecuentes del negocio",
        golden.map(g => ({ text: g.pregunta, dom: g.dominio, qid: g.id, go: () => { palClose(true); openAnswer(g.id); } })));
  if (NARR_ON && !q) group("Narrativa", [{ text: "Preparar narrativa: guarda piezas, profundiza y consolida una presentación", dom: "Asistida por IA",
                                           go: () => { palClose(true); openStudio(); } }]);
  group("Explorar por sección", sections().filter(s => !q || matches(s.num + " " + s.title + " " + s.q, q))
    .map(s => ({ text: s.num + " · " + s.title, cls: "sec", go: () => { palClose(true); goTo("#" + s.id); } })), "sub");
  if (q) group("Tarjetas", cardsInfo().filter(c => matches(c.key + " " + c.title, q)).slice(0, 8)
    .map(c => ({ text: c.title, badge: c.key, cls: "sec", go: () => { palClose(true); goTo("#" + c.id); } })), "sub");
  pal.items = items;
  // si el texto es una pregunta frecuente tal cual, Enter abre su respuesta verificada en vez de investigar de nuevo
  const bare = t => normTxt(t).replace(/[^a-z0-9ñ ]+/g, " ").replace(/\s+/g, " ").trim();
  const exact = q && BR.golden.find(g => bare(g.pregunta) === bare(raw));
  palSel(exact ? Math.max(0, items.findIndex(it => it.qid === exact.id)) : 0);
}
function palOpen(qid, trigger) {
  closeDrawer(true);
  if (qid) { openAnswer(qid); return; }
  pal.back = trigger || document.activeElement;
  pal.open = true;
  const p = $("palette");
  p.inert = false;
  p.classList.add("on");
  $("scrim").classList.add("on");
  $("palInput").value = "";
  palList();
  setTimeout(() => $("palInput").focus(), 0);
}
function palClose(keepFocus) {
  if (!pal.open) return;
  pal.open = false;
  const p = $("palette");
  p.classList.remove("on");
  p.inert = true;
  if (!drawerOpen) $("scrim").classList.remove("on");
  if (!keepFocus && pal.back && pal.back.focus) pal.back.focus();
}

/* ================================================================== panel "¿Cómo lo sabemos?" */
function openHow(key, trigger) {
  const info = BR.cards[key];
  if (!info) return;
  palClose(true);
  drawerBack = trigger || null;
  const card = document.querySelector('.card[data-card="' + key + '"]');
  $("drId").textContent = "tarjeta " + key;
  $("drTitle").textContent = card ? card.querySelector("h3").textContent : "";
  const body = $("drBody");
  body.replaceChildren();
  const sec = title => { const s = H("div", "dr-sec", body); H("h6", null, s, title); return s; };
  if (card) {
    const w = H("div", "tags", sec("Estado"));
    w.style.justifyContent = "flex-start";
    card.querySelectorAll(".card-top .tag").forEach(t => w.appendChild(t.cloneNode(true)));
  }
  rich(H("p", null, sec("Qué muestra")), info.muestra);
  if (info.claims && info.claims.length) {
    const s = sec("Afirmaciones verificadas en código");
    info.claims.forEach(id => {
      const c = D.claims.find(x => x.id === id);
      if (!c) return;
      const row = H("div", "dr-claim", s);
      row.appendChild(tagEl(c.estado));
      const t = H("div", null, row);
      H("span", "id", t, c.id + " · " + c.dominio + " · " + (c.verified ? "✓ verificada" : "✗ falló"));
      rich(t, c.claim);
      if (c.evidence && c.evidence.length) {
        const ev = H("span", "id", t, "Evidencia: " + c.evidence.map(k => k + " = " + FACT[k]).join(" · "));
        ev.style.marginTop = "4px";
      }
    });
  }
  if (info.metricas && info.metricas.length) {
    const s = sec("Métricas");
    info.metricas.forEach(id => {
      const m = BR.metrics[id];
      if (!m) return;
      const it = H("div", "dr-item", s);
      H("b", null, it, m.nombre);
      it.append(" ");
      H("code", null, it, m.id);
      rich(H("span", "f", it), m.definicion);
      const fx = H("span", "f m", it);
      fx.append("Fórmula: ");
      H("code", null, fx, m.formula);
      fx.append(" · ventana " + m.ventana + " · " + m.unidad);
    });
  }
  rich(H("p", null, sec("Cómo se calcula")), info.metodo);
  if (info.caveats && info.caveats.length) {
    const s = sec("Precauciones");
    info.caveats.forEach(id => {
      const iss = BR.issues[id];
      if (!iss) return;
      const it = H("div", "dr-item", s);
      const top = H("div", null, it);
      top.style.cssText = "display:flex;gap:8px;align-items:center;flex-wrap:wrap";
      top.appendChild(tagEl(iss.estado));
      rich(H("b", null, top), iss.titulo);
      rich(H("span", "f", it), iss.descripcion);
      const tr = H("span", "f m", it);
      tr.append("Tratamiento: ");
      rich(tr, iss.tratamiento);
    });
  }
  const s = sec("Fuente y código");
  rich(H("p", null, s), info.fuente);
  const cp = H("p", null, s);
  cp.style.marginTop = "6px";
  H("code", null, cp, info.codigo);
  drawerOpen = true;
  const dr = $("drawer");
  dr.inert = false;
  dr.classList.add("on");
  $("scrim").classList.add("on");
  body.scrollTop = 0;
  dr.querySelector("[data-close]").focus();
}
function closeDrawer(silent) {
  if (!drawerOpen) return;
  drawerOpen = false;
  const dr = $("drawer");
  dr.classList.remove("on");
  dr.inert = true;
  if (!pal.open) $("scrim").classList.remove("on");
  if (!silent && drawerBack && drawerBack.focus) drawerBack.focus();
}

/* ================================================================== respuesta primero · investigación · preguntas libres */
const LIVE = window.FINORA_LIVE || null;
const GOLDEN_INV = D.investigations || {};
const ANS = D.answers || { esencial: {}, secciones: {}, preguntas: {} };
const MISSING = BR.missing || {};
const HYP_TAG = { "Soportada": ["hecho", "✓"], "No soportada": ["noeval", "✕"], "Direccional": ["direc", "↗"], "No evaluable": ["noeval", "∅"],
                  "Pendiente": ["explo", "?"], "No evaluada por presupuesto": ["explo", "…"] };
const hypTag = (e, meta) => { const d = HYP_TAG[e] || ["met", "i"]; const t = tagRaw(d[0], d[1], e); if (meta) t.classList.add("meta"); return t; };
const metaTag = label => { const t = tagEl(label); t.classList.add("meta"); return t; };
const VFMT = { int: f.int, cop: f.cop, cop2: f.cop2, pct: v => f.pct(v), pct0: v => f.pct(v, 0), pct_signed: v => f.pctSigned(v),
               num1: v => f.num(v, 1), num2: v => f.num(v, 2), x: f.x, idx: f.idx, u: f.u2 };
const vfmt = (v, k) => (v === null || v === undefined ? "–" : typeof v === "string" ? v : (VFMT[k] || (x => f.num(x, 2)))(v));
const VKIND = { cop: "cop", cop2: "cop", pct: "pct", pct0: "pct", pct_signed: "pct", int: "int", idx: "idx", num1: "num", num2: "num", u: "u" };
const PAL = [C.s1, C.s2, C.s3, C.s4, C.s5, C.s6, C.s7, C.s8];
const STEPS = [["encuadre", "Entendiendo la pregunta"], ["hipotesis", "Planteando hipótesis"], ["evidencia", "Buscando evidencia"],
               ["validacion", "Evaluando hipótesis"], ["composicion", "Generando respuesta"], ["publicada", "Respuesta lista"]];
let INV = null, INV_EV = {}, invOpen = false, invBack = null, docMounted = [];

function btn(parent, label, cls, fn) {
  const b = H("button", "inv-btn" + (cls ? " " + cls : ""), parent, label);
  b.type = "button";
  b.addEventListener("click", fn);
  return b;
}
function setHash(h) { try { history.replaceState(null, "", h); } catch (e) { /* file:// */ } }

/* ---- contenedor de documento compartido (respuesta, investigación, análisis en vivo) */
function showDoc(kicker, statusNode) {
  if (!invOpen) invBack = document.activeElement;
  invOpen = true;
  const box = $("invdoc");
  box.hidden = false;
  document.body.style.overflow = "hidden";
  box.scrollTop = 0;
  docMounted.forEach(el => ro.unobserve(el));
  docMounted = [];
  $("invKicker").textContent = kicker;
  const st = $("invStatus");
  st.replaceChildren();
  if (statusNode) st.appendChild(statusNode);
  $("invLive").hidden = true;
  const b = $("invBody");
  b.replaceChildren();
  return b;
}
function closeInvestigation() {
  if (!invOpen) return;
  invOpen = false;
  $("invdoc").hidden = true;
  document.body.style.overflow = "";
  docMounted.forEach(el => ro.unobserve(el));
  docMounted = [];
  setHash("#snapshot");
  if (invBack && invBack.focus) invBack.focus();
}
function liveButton(label, fn) {
  const lb = $("invLive");
  lb.hidden = !LIVE;
  lb.disabled = false;
  lb.textContent = label;
  lb.onclick = fn;
}
function mountChart(parent, name) {
  // una gráfica del workspace (registro REG) dentro del documento
  const card = H("div", "card ans-visual", parent);
  H("div", "legend", card);
  const el = H("div", "chart", card);
  el.dataset.chart = name;
  requestAnimationFrame(() => { mount(el); docMounted.push(el); });
  return card;
}
function mountSpec(el, spec) {
  // una gráfica de la gramática visual del agente
  requestAnimationFrame(() => {
    el._render = () => renderVisual(el, spec);
    el._render();
    el._ready = true;
    el._w = Math.round(el.clientWidth);
    ro.observe(el);
    docMounted.push(el);
  });
}

function visualCard(parent, v, main) {
  // gramática visual del agente, o la gráfica de una tarjeta del workspace cuando la evidencia es canónica de la Fase 1
  const tarjeta = v.spec.tipo === "tarjeta";
  const w = H("div", main ? "card ans-visual" : tarjeta ? "card ans-visual flat" : "viz", parent);
  rich(H("div", main ? "viz-h" : "viz-t", w), v.titulo);
  H("div", "legend", w);
  const el = H("div", "chart", w);
  if (!tarjeta) { mountSpec(el, v.spec); return w; }
  const src = document.querySelector('main .card[data-card="' + v.spec.tarjeta + '"] .chart[data-chart]');
  if (!src) { el.textContent = "La tarjeta " + v.spec.tarjeta + " no está en este workspace."; return w; }
  el.dataset.chart = src.dataset.chart;
  requestAnimationFrame(() => { mount(el); docMounted.push(el); });
  const note = H("div", "viz-src", w, "Gráfica de la Fase 1 · ");
  const a = H("a", null, note, "tarjeta " + v.spec.tarjeta + " del workspace →");
  a.href = "#card-" + v.spec.tarjeta.replace(".", "-");
  a.addEventListener("click", e => { e.preventDefault(); closeInvestigation(); goTo(a.getAttribute("href")); });
  return w;
}

/* ---- respuesta primero en el workspace: portada y secciones */
function renderAnswers() {
  const es = ANS.esencial || {}, box = $("essential");
  if (box && es.que_pasa) {
    const row = (label, fill) => {
      const r = H("div", "ess-row", box);
      H("b", null, H("div", "ess-k", r), label);
      fill(H("div", "ess-t", r));
    };
    row("Qué está pasando", t => rich(t, es.que_pasa));
    row("Por qué creemos que pasa", t => { rich(t, es.por_que); t.appendChild(metaTag(es.por_que_estado)); });
    row("Qué todavía no sabemos", t => { rich(t, es.no_sabemos); t.appendChild(metaTag(es.no_sabemos_estado)); });
    row("Dónde profundizar", t => {
      const l = H("div", "ess-links", t);
      (es.profundizar || []).forEach(qid => {
        const g = BR.golden.find(x => x.id === qid);
        const bt = H("button", null, l, g ? g.pregunta : qid);
        bt.type = "button";
        bt.addEventListener("click", () => openAnswer(qid));
      });
      const ask = H("button", null, l, "Pregunta lo que quieras · ⌘K");
      ask.type = "button";
      ask.addEventListener("click", () => palOpen(null, ask));
    });
  }
  document.querySelectorAll(".answer[data-answer]").forEach(el => {
    const a = (ANS.secciones || {})[el.dataset.answer];
    if (!a) { el.remove(); return; }
    H("div", "answer-k", el, "Respuesta");
    rich(H("p", "answer-t", el), a.respuesta);
    const meta = H("div", "answer-meta", el);
    const lv = H("span", null, meta, "Nivel de evidencia ");
    lv.appendChild(metaTag(a.estado));
    if (a.lectura) {
      const target = "#card-" + a.lectura.tarjeta.replace(".", "-");
      const lk = H("a", null, meta, "Ver la evidencia ↓");
      lk.href = target;
      lk.addEventListener("click", e => { e.preventDefault(); goTo(target); });
      const card = document.querySelector('main .card[data-card="' + a.lectura.tarjeta + '"]');
      const foot = card && card.querySelector(".foot");
      if (foot) { const p = H("p", "lectura"); rich(p, a.lectura.texto); card.insertBefore(p, foot); }
    }
    const how = H("button", null, meta, "¿Cómo lo sabemos?");
    how.type = "button";
    const sq = el.closest(".section") && el.closest(".section").querySelector(".question");
    how.addEventListener("click", () => openAnswerLineage(Object.assign({}, a, { titular: sq ? sq.textContent.trim() : "" }), how));
    narButton(meta, () => pieceFromSection(el.dataset.answer, el));
  });
}
function phase1ClaimRows(parent, ids) {
  ids.forEach(id => {
    const c = D.claims.find(x => x.id === id);
    if (!c) return;
    const row = H("div", "dr-claim", parent);
    row.appendChild(tagEl(c.estado));
    const t = H("div", null, row);
    H("span", "id", t, c.id + " · " + c.dominio + " · " + (c.verified ? "✓ verificada en código" : "✗ falló"));
    rich(t, c.claim);
    if ((c.evidence || []).length) {
      const ev = H("span", "id", t, "Evidencia: " + c.evidence.map(k => k + " = " + FACT[k]).join(" · "));
      ev.style.marginTop = "4px";
    }
    const cards = Object.entries(BR.cards).filter(([, v]) => (v.claims || []).includes(id)).map(([k]) => k);
    if (cards.length) {
      const l = H("span", "id", t);
      l.style.marginTop = "4px";
      l.append("En el workspace: ");
      cards.forEach((k, i) => {
        const target = "#card-" + k.replace(".", "-");
        const a = H("a", null, l, "tarjeta " + k);
        a.href = target;
        a.addEventListener("click", e => { e.preventDefault(); closeDrawer(true); closeInvestigation(); goTo(target); });
        if (i < cards.length - 1) l.append(" · ");
      });
    }
  });
}
function openAnswerLineage(a, trigger) {
  openDrawerWith("respuesta", a.titular || a.respuesta, body => {
    const s = drSec(body, "Nivel de evidencia");
    const w = H("div", "tags", s);
    w.style.justifyContent = "flex-start";
    w.appendChild(tagEl(a.estado));
    phase1ClaimRows(drSec(body, "Afirmaciones verificadas en código"), a.claims || []);
    H("p", null, drSec(body, "Cómo se escribió"), "La respuesta se redactó sobre estas afirmaciones. El pipeline verifica que cada cifra venga de un cálculo, que cada afirmación exista y que el lenguaje no sea causal.");
  }, trigger);
}

/* ---- vista de respuesta (pregunta frecuente) */
function knowBlock(parent, cols) {
  const know = H("div", "know" + (cols.length === 2 ? " two" : cols.length === 1 ? " one" : ""), parent);
  cols.forEach(([title, fill]) => { const d = H("div", "kb", know); H("h4", null, d, title); fill(d); });
  return know;
}
const needList = ids => d => {
  const ul = H("ul", null, d);
  ids.forEach(m => {
    const x = typeof m === "string" ? { nombre: (MISSING[m] || {}).nombre || m, campos: (MISSING[m] || {}).campos_necesarios || [] } : m;
    const li = H("li", null, ul, x.nombre + " ");
    (x.campos || []).forEach(cf => { H("code", null, li, cf); li.append(" "); });
  });
};
const textList = items => d => { const ul = H("ul", null, d); items.forEach(t => rich(H("li", null, ul), t)); };
function renderAnswerView(b, qid, opts) {
  opts = opts || {};
  const a = (ANS.preguntas || {})[qid], g = BR.golden.find(x => x.id === qid);
  if (opts.banner) rich(H("div", "ans-banner", b), opts.banner);
  H("h1", "ans-q", b, g ? g.pregunta : qid);
  if (!a) { H("p", null, b, "Todavía no hay una respuesta verificada para esta pregunta."); return; }
  const noEval = a.estado === "No evaluable";
  const main = H("div", "ans-main", b);
  H("div", "answer-k", main, "Respuesta");
  rich(H("div", "ans-titular", main), a.titular);
  rich(H("p", "ans-text", main), a.respuesta);
  const meta = H("div", "ans-meta", main);
  H("span", null, meta, "Nivel de evidencia ").appendChild(metaTag(a.estado));
  H("span", null, meta, "Fuente: afirmaciones verificadas del workspace");
  const how = H("button", "inv", meta, "¿Cómo lo sabemos?");
  how.type = "button";
  how.addEventListener("click", () => openAnswerLineage(a, how));
  if (a.visual) {
    const card = mountChart(b, a.visual);
    const h = H("div", "viz-h");
    rich(h, a.visual_titulo || a.titular);
    card.prepend(h);
    if (a.lectura) rich(H("p", "lectura", card), a.lectura);
  }
  knowBlock(b, [
    [noEval ? "Lo que sí sabemos" : "Qué sabemos", textList(a.sabemos || [])],
    [noEval ? "Lo que no podemos saber con estos datos" : "Qué no sabemos todavía", textList(a.no_sabemos || [])],
    [noEval ? "Lo que necesitaríamos para responderlo" : "Qué necesitaríamos para saberlo", needList(a.necesitariamos || [])],
  ]);
  H("h2", "inv-h2", b, "Hallazgos que soportan esta respuesta");
  const cl = H("div", "claims-list", b);
  (a.claims || []).forEach(id => {
    const c = D.claims.find(x => x.id === id);
    if (!c) return;
    const r = H("div", "cl", cl);
    rich(H("span", null, r), c.claim);
    r.appendChild(metaTag(c.estado));
  });
  const acts = H("div", "ans-actions", b);
  const invId = a.investigacion || ((ANS.preguntas[a.relacionada] || {}).investigacion);
  if (invId && GOLDEN_INV[invId]) btn(acts, a.investigacion ? "Ver investigación completa →" : "Ver investigación relacionada →", "primary",
                                      () => openInvestigation(GOLDEN_INV[invId], { golden: true }));
  const sec = sections().find(s => s.id === a.seccion);
  if (sec) btn(acts, "Ir a " + sec.num + " · " + sec.title + " →", "", () => {
    closeInvestigation();
    goTo(a.tarjeta ? "#card-" + a.tarjeta.replace(".", "-") : "#" + sec.id);
  });
  if (LIVE) btn(acts, noEval ? "Investigar más →" : "Investigar en vivo", "", () => startLive(qid === "Q2" ? { pregunta_id: "Q2" } : { pregunta: g.pregunta }, g.pregunta));
  narButton(acts, () => pieceFromAnswer(qid), "inv-btn", "＋ Guardar en narrativa");
}
function openAnswer(qid, opts) {
  opts = opts || {};
  const a = (ANS.preguntas || {})[qid];
  if (a && a.investigacion && GOLDEN_INV[a.investigacion] && !opts.plain) {
    openInvestigation(GOLDEN_INV[a.investigacion], { golden: true, banner: opts.banner });
    return;
  }
  const b = showDoc("Respuesta · " + qid, a ? metaTag(a.estado) : null);
  setHash("#respuesta/" + qid);
  renderAnswerView(b, qid, opts);
  $("invBack").focus();
}

/* ---- preguntas libres: enrutador determinista (sin servidor) e investigación en vivo (con servidor) */
const STOP = new Set(("que cual cuales como para por porque pero con sin los las del de la el en un una unos unas lo le les se su sus al es son fue " +
  "ser esta este esto estos estas ese esa eso hay hace mas menos muy ya si no ni y me mi nos quiero saber puede pueden cuando donde " +
  "cuanto cuanta cuantos sobre entre desde hasta tiene tienen esta estan estamos pasa pasando hacer tenemos ahora sigue").split(" "));
const tokens = s => normTxt(s).split(/[^a-z0-9ñ&]+/).filter(t => t.length > 2 && !STOP.has(t));
function routeQuestion(text) {
  const toks = [...new Set(tokens(text))];
  const kwHit = (kw, t) => kw.some(k => k === t || (k.length > 4 && t.length > 4 && t.slice(0, 5) === k.slice(0, 5)));
  return BR.golden.map(g => {
    const kw = (((ANS.preguntas || {})[g.id] || {}).palabras_clave || []).map(normTxt);
    const qw = tokens(g.pregunta);
    let score = 0;
    const hits = [];
    toks.forEach(t => {
      const s = (kwHit(kw, t) ? 2 : 0) + (qw.includes(t) ? 1 : 0);
      if (s) { score += s; hits.push(t); }
    });
    return { id: g.id, pregunta: g.pregunta, score: score, hits: hits };
  }).sort((x, y) => y.score - x.score);
}
function askFree(text) {
  palClose(true);
  const routes = routeQuestion(text);
  if (LIVE && LIVE.libre) { startLive({ pregunta: text }, text, routes); return; }
  staticAnswer(text, routes);
}
function staticAnswer(text, routes) {
  const best = routes[0], matched = best && best.score >= 3;
  const b = showDoc("Tu pregunta", tagRaw("explo", "?", "Respuestas verificadas · sin servidor"));
  setHash("#pregunta");
  const q = H("div", "inv-frame", b);
  H("b", null, q, "Preguntaste: ");
  q.append(text.length > 400 ? text.slice(0, 400) + "…" : text);
  const steps = H("div", "live-steps", b);
  ["Entendiendo la pregunta", "Buscando respuestas verificadas", matched ? "Respuesta verificada encontrada" : "Sin respuesta verificada"]
    .forEach(l => H("div", "done", steps, "✓ " + l));
  H("p", "inv-frame", b, best && best.hits.length ? "Términos del negocio que reconocí: " + best.hits.slice(0, 10).join(", ") + "."
                                                  : "No reconocí términos del negocio en la pregunta.");
  if (matched) {
    renderAnswerView(b, best.id, { banner: "Esta es la respuesta verificada más cercana a tu pregunta. Este HTML no puede investigar preguntas nuevas; con el servidor local, Enter lanza una investigación del agente." });
  } else {
    H("h2", "inv-h2", b, "No tengo una respuesta verificada para esta pregunta");
    H("p", null, b, "Este HTML responde con lo que ya está verificado. Para investigar una pregunta nueva, abre el workspace con el servidor local y pulsa Enter.");
    const alt = routes.filter(r => r.score > 0).slice(0, 3);
    if (alt.length) {
      H("p", "inv-frame", b, "Lo más cercano que sí tiene respuesta:");
      const acts = H("div", "ans-actions", b);
      alt.forEach(r => btn(acts, r.pregunta, "", () => openAnswer(r.id)));
    }
  }
  $("invBack").focus();
}
let liveES = null;
async function startLive(body, pregunta, routes) {
  if (!LIVE) return;
  let r;
  try {
    r = await fetch(LIVE.api + "/investigations", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  } catch (err) { alert("No se pudo conectar con el servidor local."); return; }
  if (!r.ok) {
    const t = await r.json().catch(() => ({}));
    alert(r.status === 409 ? "Ya hay una investigación en curso; espera a que termine." : "Error " + r.status + ": " + (t.detail || ""));
    return;
  }
  const id = (await r.json()).id;
  liveShell(pregunta, routes || routeQuestion(pregunta));
  if (liveES) liveES.close();
  liveES = new EventSource(LIVE.api + "/investigations/" + id + "/stream");
  liveES.onmessage = m => onLiveEvent(JSON.parse(m.data), id);
  liveES.onerror = () => { if (liveES) liveES.close(); liveES = null; pollLive(id); };
}
function liveShell(pregunta, routes) {
  INV = { claims: {}, hipotesis: [], evidencia: [] };
  INV_EV = {};
  const b = showDoc("Analizando tu pregunta", tagRaw("explo", "?", "En curso"));
  setHash("#analizando");
  const lb = $("invLive");
  lb.hidden = false;
  lb.disabled = true;
  lb.textContent = "Investigando…";
  const k = H("div", "answer-k analyzing", b);
  H("span", "spinner", k);
  k.append("Analizando tu pregunta…");
  H("h1", "ans-q", b, pregunta.length > 300 ? pregunta.slice(0, 300) + "…" : pregunta);
  const steps = H("div", "live-steps", b);
  steps.id = "liveSteps";
  STEPS.forEach(([key, lab]) => { const d = H("div", null, steps, lab); d.dataset.k = key; });
  requestAnimationFrame(() => liveStep("encuadre"));
  H("p", "inv-frame", b, "El agente trabaja con las herramientas de Finora sobre tu sesión de Claude Code: primero registra hipótesis y qué esperaría ver, después reúne evidencia, y el validador acepta o rechaza cada afirmación. Suele tardar entre 3 y 10 minutos.");
  const frame = H("p", "inv-frame", b);
  frame.id = "liveFrame";
  const best = routes && routes[0];
  if (best && best.score >= 3 && (ANS.preguntas || {})[best.id]) {
    const a = ANS.preguntas[best.id];
    const box = H("div", "ans-main", b);
    box.style.marginTop = "6px";
    H("div", "answer-k", box, "Mientras tanto, esto ya está verificado");
    H("div", "dq muted", box, best.pregunta).style.fontSize = "12.5px";
    rich(H("div", "ans-titular", box), a.titular);
    rich(H("p", "ans-text", box), a.respuesta);
    H("span", "ans-meta", box, "Nivel de evidencia ").appendChild(metaTag(a.estado));
  }
  invSection(b, "1", "Hipótesis pre-registradas");
  const hy = H("div", null, b);
  hy.id = "liveHyp";
  H("p", "muted", hy, "Esperando el encuadre…");
  invSection(b, "2", "Afirmaciones aceptadas");
  H("div", null, b).id = "liveClaims";
  invSection(b, "3", "Bitácora en vivo");
  const feed = H("div", "live-feed", b);
  feed.id = "liveFeed";
  feed.setAttribute("aria-live", "polite");
}
function liveLine(text, cls) {
  const feed = $("liveFeed");
  if (!feed) return;
  const d = H("div", cls || null, feed, text);
  d.scrollIntoView({ block: "nearest" });
}
function liveStep(k) {
  const i = STEPS.findIndex(s => s[0] === k);
  document.querySelectorAll("#liveSteps div").forEach((d, j) => { d.classList.toggle("on", j === i); d.classList.toggle("done", j < i); });
}
async function pollLive(id) {
  for (let k = 0; k < 400; k++) {
    const d = await fetch(LIVE.api + "/investigations/" + id).then(x => x.json()).catch(() => null);
    if (d && (d.status === "publicada" || d.status === "error")) { openInvestigation(d); return; }
    await new Promise(res => setTimeout(res, 2000));
  }
}
function onLiveEvent(ev, id) {
  const d = ev.data || {}, t = "[" + f.num(ev.t / 1000, 1) + " s] ";
  if (ev.tipo === "estado") { liveStep(d.estado); liveLine(t + "estado → " + ((STEPS.find(s => s[0] === d.estado) || [])[1] || d.estado), "n"); }
  else if (ev.tipo === "sesion") liveLine(t + "sesión · " + d.autenticacion, "n");
  else if (ev.tipo === "encuadre") { const fr = $("liveFrame"); if (fr) { fr.replaceChildren(); H("b", null, fr, "Pregunta analítica: "); fr.append(d.pregunta_analitica + " · playbook " + d.playbook); } }
  else if (ev.tipo === "hipotesis") { const hy = $("liveHyp"); if (hy) { hy.replaceChildren(); hypList(hy, d.hipotesis); } }
  else if (ev.tipo === "tool") liveLine(t + "→ " + d.tool);
  else if (ev.tipo === "tool_error") liveLine(t + "✗ " + d.tool + ": " + d.error.slice(0, 220), "e");
  else if (ev.tipo === "evidencia") liveLine(t + "evidencia " + d.id + " · " + d.resumen);
  else if (ev.tipo === "claim") {
    liveLine(t + "✓ " + d.id + " [" + d.estado + "] " + d.texto, "c");
    const lc = $("liveClaims");
    if (lc) { const row = H("div", "claim-row", lc); rich(H("span", "txt sub", row), d.texto); row.appendChild(metaTag(d.estado)); }
  } else if (ev.tipo === "claim_rechazada") liveLine(t + "✗ afirmación rechazada: " + d.motivos.join("; ").slice(0, 260), "e");
  else if (ev.tipo === "visual") liveLine(t + "visual " + d.id + " (" + d.tipo + ") para " + d.claim_id);
  else if (ev.tipo === "nota") liveLine(t + "analista: " + d.texto, "n");
  else if (ev.tipo === "composicion") liveLine(t + "respuesta, intento " + d.intento + ": " + (d.errores.length ? d.errores.length + " correcciones del validador" : "aprobada"), d.errores.length ? "e" : "c");
  else if (ev.tipo === "final") {
    if (liveES) { liveES.close(); liveES = null; }
    fetch(LIVE.api + "/investigations/" + id).then(x => x.json()).then(doc => openInvestigation(doc));
  }
}

/* ---- gráficas del agente (gramática visual) */
function renderVisual(el, spec) {
  const fmt = v => vfmt(v, spec.formato), kind = VKIND[spec.formato] || "num";
  const series = (spec.series || []).map((s, i) => ({ name: s.nombre, values: s.valores, color: PAL[i % PAL.length] }));
  const lg = el.previousElementSibling && el.previousElementSibling.classList.contains("legend") ? el.previousElementSibling : null;
  if (lg) {
    const ci = spec.tipo === "puntos" && spec.referencia !== undefined;
    const items = ci ? [{ name: "Razón", color: C.s1, kind: "dot" }, { name: "Intervalo de 90%", color: C.de, kind: "line" }]
                     : series.map(s => ({ name: s.name, color: s.color, kind: spec.tipo === "linea" ? "line" : spec.tipo === "puntos" ? "dot" : "rect" }));
    if (items.length > 1) legend(null, items, null, lg); else lg.replaceChildren();
  }
  if (spec.tipo === "linea") return lineChart(el, { labels: spec.x, series: series, fmt: fmt, tickKind: kind, height: 260, includeZero: spec.formato !== "idx" });
  if (spec.tipo === "barras") {
    const stacked = !!spec.apiladas;
    return barChart(el, { labels: spec.x, series: series, stacked: stacked, fmt: fmt, tickKind: kind, height: 260, maxBar: 34,
                          yMin: stacked ? 0 : undefined, yMax: stacked && spec.formato === "pct" ? 1 : undefined });
  }
  if (spec.tipo === "cascada") {
    let k = 0;
    return waterfall(el, { height: 280, fmt: f.cop, title: "Descomposición", steps: spec.pasos.map(p => ({ label: p.etiqueta, short: p.corta, value: p.valor,
      kind: p.tipo === "total" ? "total" : "delta", color: p.tipo === "total" ? C.de : [C.s2, C.s1, C.s3][k++ % 3] })) });
  }
  if (spec.tipo === "puntos") {
    const ci = spec.referencia !== undefined;
    return dots(el, { rows: spec.filas, fmt: fmt, tickKind: kind, rowTitle: "", ref: spec.referencia,
                      refLabel: ci ? "= " + fmt(spec.referencia) : null,
                      series: spec.series.map((s, i) => ({ name: s.nombre, values: s.valores, color: ci ? [C.de, C.s1, C.de][i] || PAL[i] : PAL[i % PAL.length] })) });
  }
  if (spec.tipo === "datos") {
    el.replaceChildren();
    const box = H("div", "datagap", el);
    spec.filas.forEach(r => {
      const okRow = r.estado !== "No existe";
      const row = H("div", "dg " + (okRow ? "ok" : "no"), box);
      H("span", "ic", row, okRow ? "✓" : "✕");
      H("span", null, row, r.dato);
      H("span", "cf", row, okRow ? r.estado : r.campos);
    });
    return {};
  }
  if (spec.tipo === "kpi") { el.replaceChildren(); const d = H("div", "stat", el); H("div", "k", d, spec.etiqueta); H("div", "v", d, fmt(spec.valor)); return {}; }
  if (spec.tipo === "tabla") { el.replaceChildren(); evTable(el, spec.columnas, spec.filas, 40); return {}; }
  el.textContent = "Visualización no disponible.";
  return {};
}
function evTable(parent, cols, rows, max) {
  const w = H("div", "tablewrap", parent);
  table(w, cols.filter(c => c.id !== "_clave").map(c => ({ key: c.id, label: c.nombre, num: !!c.formato && c.formato !== "texto",
    fmt: v => (typeof v === "string" ? v : vfmt(v, c.formato || "num2")) })), rows.slice(0, max || 60));
  return w;
}
function invSection(parent, n, title) {
  const h = H("h2", "inv-h2", parent);
  H("span", "n", h, n);
  h.append(title);
}
function hypList(parent, hyps) {
  const list = H("div", "hyp-list", parent);
  hyps.forEach(h => {
    const row = H("div", "hyp" + (h.padre ? " child" : ""), list);
    H("span", "id", row, h.id);
    H("span", "q", row, h.pregunta);
    row.appendChild(hypTag(h.estado || "Pendiente", true));
    const sig = H("div", "sig", row);
    H("span", null, sig, "Se acepta si: ");
    sig.append((h.firma || {}).si_es_cierta || "–");
    H("span", null, sig, " · Se rechaza si: ");
    sig.append((h.firma || {}).si_es_falsa || "–");
    H("div", "why", row, (h.estado_motivo ? h.estado_motivo + " · " : "") +
      (h.agregada_despues_de_evidencia ? "agregada después de ver evidencia" : "registrada antes de ver evidencia"));
  });
  return list;
}
function claimRow(parent, c, sub) {
  if (!c) return;
  const row = H("div", "claim-row", parent);
  const b = H("button", "lk", row);
  b.type = "button";
  b.title = "¿Cómo lo sabemos?";
  rich(H("span", "txt" + (sub ? " sub" : ""), b), c.texto);
  b.addEventListener("click", () => openClaimLineage(c.id, b));
  row.appendChild(metaTag(c.estado));
}
function evLabel(e) {
  if (e.canonical) return "canónica de la Fase 1";
  if (e.kind === "metric") return ((e.result || {}).label || "métrica") + " · " + ({ month: "mensual", quarter: "trimestral", half: "semestral", year: "anual", total: "total" }[(e.params || {}).grano] || "mensual");
  if (e.kind === "sql") return "SQL ad hoc";
  return (e.variant || e.method || "").slice(0, 44);
}
function evChips(parent, claims) {
  const box = H("div", "ev-chips", parent);
  const seen = new Set();
  claims.forEach(c => [["apoyo", ""], ["en_contra", " contra"]].forEach(([k, cls]) => (c[k] || []).forEach(eid => {
    if (seen.has(eid)) return;
    seen.add(eid);
    const e = INV_EV[eid];
    const b = H("button", "ev-chip" + cls, box, eid + (e ? " · " + evLabel(e) : "") + (cls ? " · en contra" : ""));
    b.type = "button";
    b.addEventListener("click", () => openEvidenceLineage(eid, b));
  })));
}

/* ---- investigación: respuesta primero y "cómo llegamos" a demanda */
function openInvestigation(doc, opts) {
  opts = opts || {};
  INV = doc;
  INV_EV = {};
  (doc.evidencia || []).forEach(e => { INV_EV[e.id] = e; });
  const b = showDoc("Investigación" + (doc.pregunta_id ? " · " + doc.pregunta_id : "") + " · lente " + (doc.lente || "Finanzas"),
    doc.status === "publicada" ? tagRaw("hecho", "✓", opts.golden ? "Publicada · dorada" : "Publicada")
                               : tagRaw("prec", "!", doc.status === "error" ? "Error" : doc.status));
  setHash("#investigacion/" + (doc.pregunta_id || doc.id));
  if (LIVE) liveButton("Investigar en vivo", () => startLive(doc.pregunta_id === "Q2" ? { pregunta_id: "Q2" } : { pregunta: doc.pregunta }, doc.pregunta));
  renderInvestigation(b, doc, opts);
  $("invBack").focus();
}
function pickMainVisual(doc) {
  const N = doc.narrativa || {}, vis = doc.visuals || {};
  const exec = new Set((N.respuesta_ejecutiva || {}).claim_ids || []);
  const all = Object.values(vis).filter(v => v && v.spec && v.spec.tipo !== "datos");
  const inOrder = (N.hallazgos || []).map(h => (h.visual_ids || []).map(id => vis[id])).flat().filter(v => v && v.spec && v.spec.tipo !== "datos");
  return all.find(v => exec.has(v.claim_id)) || inOrder[0] || all[0] || null;
}
function renderInvestigation(b, doc, opts) {
  const claims = doc.claims || {}, N = doc.narrativa;
  if (opts.banner) rich(H("div", "ans-banner", b), opts.banner);
  if (NARR_ON && doc.contexto && NAR_RE.test(doc.contexto.narrativa_id || "")) {
    NST.current = doc.contexto.narrativa_id;
    const bn = H("div", "ans-banner", b, "Profundización desde tu narrativa: guarda aquí lo que te sirva con ＋ Narrativa. ");
    const back = H("button", "inv", bn, "← Volver a la narrativa");
    back.type = "button";
    back.addEventListener("click", () => openStudio(doc.contexto.narrativa_id));
  }
  H("h1", "ans-q", b, doc.pregunta);
  if (doc.error) H("div", "ans-banner", b, "La investigación terminó con error: " + doc.error);
  if (N) {
    const main = H("div", "ans-main", b);
    H("div", "answer-k", main, "Respuesta ejecutiva");
    if (N.respuesta_ejecutiva.titular) rich(H("div", "ans-titular", main), N.respuesta_ejecutiva.titular);
    rich(H("p", "ans-text", main), N.respuesta_ejecutiva.texto);
    const meta = H("div", "ans-meta", main);
    const lv = H("span", null, meta, "Nivel de evidencia ");
    [...new Set(N.respuesta_ejecutiva.claim_ids.map(id => (claims[id] || {}).estado).filter(Boolean))].forEach(s => { lv.appendChild(metaTag(s)); lv.append(" "); });
    H("span", null, meta, "Investigación del agente · " + Object.values(claims).filter(c => c.aceptada).length + " afirmaciones validadas");
    narButton(meta, () => pieceFromInvAnswer(doc));
    if (N.degradada) H("span", null, meta, "· composición sin texto libre");
    const hz = N.hallazgos || [];
    if (hz.length) {
      const dv = H("div", "drivers", b);
      hz.slice(0, 4).forEach(h => {
        const hyp = (doc.hipotesis || []).find(x => x.id === h.hipotesis_id);
        const c0 = claims[h.claim_ids[0]];
        const d = H("div", "driver", dv);
        if (hyp) d.appendChild(hypTag(hyp.estado, true));
        rich(H("div", "dt", d), h.titular || (c0 ? c0.texto : ""));
        H("div", "dq", d, h.pregunta);
        narButton(d, () => pieceFromFinding(doc, h), "inv nar-driver");
      });
    }
    const vmain = pickMainVisual(doc);
    if (vmain) {
      const card = visualCard(b, vmain, true);
      card.id = "invMainVisual";
      const hzv = hz.find(h => (h.visual_ids || []).includes(vmain.id));
      if (hzv && hzv.interpretacion) rich(H("p", "lectura", card), hzv.interpretacion);
    }
    const noeval = Object.values(claims).filter(c => c.aceptada && c.estado === "No evaluable");
    const need = [...new Set(noeval.flatMap(c => c.datos_faltantes || []))];
    const mainNoEval = N.respuesta_ejecutiva.claim_ids.some(id => (claims[id] || {}).estado === "No evaluable");
    if ((N.limites || []).length || need.length) {
      const cols = [];
      if (mainNoEval) cols.push(["Lo que sí sabemos", textList(Object.values(claims).filter(c => c.aceptada && c.estado !== "No evaluable").slice(0, 4).map(c => c.texto))]);
      cols.push([mainNoEval ? "Lo que no podemos saber con estos datos" : "Qué todavía no sabemos", textList((N.limites || []).map(l => l.texto))]);
      if (need.length) cols.push([mainNoEval ? "Lo que necesitaríamos para responderlo" : "Qué necesitaríamos para saberlo", needList(need)]);
      knowBlock(b, cols);
    }
    if ((N.proximas_preguntas || []).length) {
      H("h2", "inv-h2", b, "¿Dónde seguir?");
      const box = H("div", "inv-next", b);
      N.proximas_preguntas.forEach(q => {
        const bt = H("button", null, box, q);
        bt.type = "button";
        bt.addEventListener("click", () => { palOpen(null, bt); $("palInput").value = q; palList(); });
      });
    }
  }
  const vmainId = N ? (pickMainVisual(doc) || {}).id : null;
  const more = H("button", "inv-more", b, "Ver cómo llegamos a esta conclusión ↓");
  more.type = "button";
  const det = H("div", "inv-details", b);
  det.hidden = true;
  let built = false;
  const toggle = open => {
    det.hidden = !open;
    more.textContent = open ? "Ocultar cómo llegamos ↑" : "Ver cómo llegamos a esta conclusión ↓";
    if (open && !built) { built = true; renderDetails(det, doc, vmainId); }
  };
  more.addEventListener("click", () => toggle(det.hidden));
  if (!N) { toggle(true); more.remove(); }
}
function renderDetails(b, doc, mainId) {
  const claims = doc.claims || {}, N = doc.narrativa;
  if (doc.encuadre) {
    const p = H("p", "inv-frame", b);
    p.append("Encuadre: ");
    H("b", null, p, doc.encuadre.pregunta_analitica);
    p.append(" · Playbook: " + (doc.encuadre.playbook || doc.playbook_id) + " · Métricas: " + (doc.encuadre.metricas || []).join(", ") + " · Periodo: " + (doc.encuadre.periodo || "–"));
  }
  const acc = Object.values(claims).filter(c => c.aceptada);
  const meta = H("div", "inv-meta", b);
  const mi = (k, v) => { const s = H("span", null, meta); H("b", null, s, k + " "); s.append(v); };
  mi("Evidencias", String((doc.evidencia || []).length));
  mi("Afirmaciones", acc.length + " aceptadas · " + (Object.keys(claims).length - acc.length) + " rechazadas por el validador");
  mi("Presupuesto", (doc.presupuesto || {}).analisis_usado + " de 15 análisis");
  if (doc.hipotesis_registradas_ms !== null && doc.hipotesis_registradas_ms !== undefined) mi("Hipótesis", "registradas antes de la primera evidencia");
  invSection(b, "1", "Cómo descompusimos la pregunta");
  H("p", "inv-frame", b, "Cada hipótesis se registró con su criterio de aceptación y de rechazo antes de ver datos; el estado lo deriva el código desde las afirmaciones.");
  hypList(b, doc.hipotesis || []);
  if (N) {
    const shown = {};
    invSection(b, "2", "Hallazgos y evidencia");
    N.hallazgos.forEach((hz, i) => {
      const card = H("article", "card finding", b);
      const fq = H("div", "fq", card);
      H("span", "mono", fq, "Hallazgo " + (i + 1) + " · " + hz.hipotesis_id);
      const hyp = (doc.hipotesis || []).find(h => h.id === hz.hipotesis_id);
      if (hyp) fq.appendChild(hypTag(hyp.estado, true));
      fq.append(hz.pregunta);
      if (hz.titular) rich(H("div", "ans-titular", card), hz.titular).style.fontSize = "17px";
      hz.claim_ids.forEach((cid, j) => claimRow(card, claims[cid], j > 0));
      evChips(card, hz.claim_ids.map(id => claims[id]).filter(Boolean));
      (hz.visual_ids || []).forEach(vid => {
        const v = (doc.visuals || {})[vid];
        if (!v) return;
        // sin duplicar: la gráfica principal y las ya dibujadas en otro hallazgo se enlazan
        const first = vid === mainId ? "invMainVisual" : shown[vid];
        if (!first) { visualCard(card, v, false).id = "viz-" + vid; shown[vid] = "viz-" + vid; return; }
        const note = H("div", "viz-src", card);
        const a = H("a", null, note, vid === mainId ? "↑ Su gráfica es la principal de la investigación: ver arriba" : "↑ Misma gráfica que un hallazgo anterior: ver arriba");
        a.href = "#" + first;
        a.addEventListener("click", e => { e.preventDefault(); const t = $(first); if (t) t.scrollIntoView({ behavior: REDUCED ? "auto" : "smooth", block: "center" }); });
      });
      const prose = H("div", "prose", card);
      [["Qué significa", hz.interpretacion], ["Implicación", hz.implicacion], ["¿Por qué lo afirmamos?", hz.por_que]].forEach(([k, t]) => {
        if (!t) return;
        const p = H("div", null, prose);
        H("b", null, p, k + ". ");
        rich(p, t);
      });
      narButton(card, () => pieceFromFinding(doc, hz), "inv", "＋ Guardar este hallazgo en la narrativa");
    });
    if ((N.limites || []).length) {
      invSection(b, "3", "Lo que no podemos concluir");
      const box = H("div", "inv-blocks", b);
      N.limites.forEach(l => { const d = rich(H("div", "inv-block", box), l.texto); evChips(d, l.claim_ids.map(id => claims[id]).filter(Boolean)); });
    }
    if ((N.implicaciones || []).length) {
      invSection(b, "4", "Implicaciones");
      const box = H("div", "inv-blocks", b);
      N.implicaciones.forEach(l => rich(H("div", "inv-block", box), l.texto));
    }
  }
  const rejected = Object.values(claims).filter(c => !c.aceptada);
  invSection(b, "5", "Registro de análisis");
  H("p", "inv-frame", b, "Todo lo que se ejecutó, incluido lo descartado y lo que el validador rechazó. Es la defensa contra el cherry-picking.");
  const logRows = (doc.log || []).map(e => ({ n: e.n, t: f.num(e.t / 1000, 1) + " s", tool: e.tool,
    params: JSON.stringify(e.params).slice(0, 90), res: e.ok ? "ok" : "error", ev: (e.evidencias || []).join(" "),
    uso: e.ok === false ? (e.error || "").slice(0, 110) : (e.evidencias || []).length ? (e.usada ? "usada" : "descartada") : "–" }));
  const lw = H("div", "tablewrap", b);
  const lt = table(lw, [{ key: "n", label: "#", num: true }, { key: "t", label: "Tiempo", num: true }, { key: "tool", label: "Tool" },
    { key: "params", label: "Parámetros" }, { key: "res", label: "Resultado" }, { key: "ev", label: "Evidencias" }, { key: "uso", label: "Uso o motivo" }], logRows);
  lt.classList.add("inv-log");
  if (rejected.length) {
    H("p", "inv-frame", b, "Afirmaciones que el validador rechazó (" + rejected.length + "):").style.marginTop = "14px";
    const box = H("div", "inv-blocks", b);
    rejected.forEach(c => { const d = H("div", "inv-block", box); H("code", null, d, c.id); d.append(" " + (c.plantilla || "") + " → " + (c.motivos || []).join(" · ")); });
  }
  const foot = H("div", "inv-foot", b);
  const u = doc.uso || {};
  const cost = Object.keys(u).filter(k => k !== "autenticacion").map(k => (u[k] || {}).costo_equivalente_usd || 0).reduce((a, x) => a + x, 0);
  foot.textContent = "Modelo " + doc.modelo + " · " + (u.autenticacion || "") + " · datos " + doc.data_version + " · cerebro " + doc.brain_version +
    " · duración " + (doc.finished_ms && doc.started_ms ? f.num((doc.finished_ms - doc.started_ms) / 1000, 0) + " s" : "–") +
    (cost ? " · costo equivalente estimado en API: US$ " + f.num(cost, 2) + " (con suscripción no se cobra por token)" : "");
}

/* ---- linaje: afirmación → evidencia → método → consulta → fuente */
function openDrawerWith(kicker, title, fill, trigger) {
  palClose(true);
  drawerBack = trigger || null;
  $("drId").textContent = kicker;
  $("drTitle").textContent = title;
  const body = $("drBody");
  body.replaceChildren();
  fill(body);
  drawerOpen = true;
  const dr = $("drawer");
  dr.inert = false;
  dr.classList.add("on");
  $("scrim").classList.add("on");
  body.scrollTop = 0;
  dr.querySelector("[data-close]").focus();
}
function drSec(body, title) { const s = H("div", "dr-sec", body); H("h6", null, s, title); return s; }
function openClaimLineage(cid, trigger) {
  const c = INV.claims[cid];
  openDrawerWith("afirmación " + cid, c.texto || c.plantilla, body => {
    const s1 = drSec(body, "Estado");
    const w = H("div", "tags", s1);
    w.style.justifyContent = "flex-start";
    w.appendChild(tagEl(c.estado));
    (c.marcadores || []).forEach(m => w.appendChild(tagEl(m)));
    H("p", null, s1, "Propuesto por el agente: " + c.estado_propuesto + ". Tipo: " + c.tipo + ".").style.marginTop = "6px";
    (c.avisos || []).forEach(a => H("p", "muted", s1, "Validador: " + a).style.fontSize = "12px");
    const s2 = drSec(body, "Plantilla y cifras ligadas");
    H("div", "dr-pre", s2, c.plantilla);
    Object.entries(c.variables || {}).forEach(([k, ref]) => {
      const it = H("div", "dr-item", s2);
      H("code", null, it, "{" + k + "}");
      it.append(" ← ");
      const eid = ref.split(".")[0];
      const bt = H("button", "ev-chip", it, ref);
      bt.type = "button";
      bt.addEventListener("click", () => openEvidenceLineage(eid, bt));
    });
    const s3 = drSec(body, "Evidencia");
    evChips(s3, [c]);
    const s4 = drSec(body, "Hipótesis");
    (c.hipotesis || []).forEach(l => {
      const h = (INV.hipotesis || []).find(x => x.id === l.id);
      H("div", "dr-item", s4, l.id + " · " + (l.postura === "a_favor" ? "a favor" : "en contra") + (h ? " · " + h.pregunta : ""));
    });
    if ((c.caveats || []).length) {
      const s5 = drSec(body, "Precauciones");
      c.caveats.forEach(id => { const x = BR.issues[id]; const it = H("div", "dr-item", s5); rich(H("b", null, it), x ? x.titulo : id); if (x) rich(H("span", "f m", it), x.tratamiento); });
    }
    if ((c.datos_faltantes || []).length) H("p", null, drSec(body, "Datos que faltan"), c.datos_faltantes.join(", "));
  }, trigger);
}
function openEvidenceLineage(eid, trigger) {
  const e = INV_EV[eid];
  if (!e) return;
  openDrawerWith("evidencia " + eid, e.method + (e.variant ? " · " + e.variant : ""), body => {
    const tabs = H("div", "dr-tabs", body);
    const panes = {};
    ["Evidencia", "Método", "Consulta", "Fuente"].forEach((name, i) => {
      const bt = H("button", null, tabs, name);
      bt.type = "button";
      bt.setAttribute("aria-pressed", String(i === 0));
      panes[name] = H("div", null, body);
      panes[name].hidden = i !== 0;
      bt.addEventListener("click", () => {
        tabs.querySelectorAll("button").forEach(x => x.setAttribute("aria-pressed", String(x === bt)));
        Object.entries(panes).forEach(([k, p]) => { p.hidden = k !== name; });
      });
    });
    const r = e.result || {};
    const p1 = panes["Evidencia"];
    const s = drSec(p1, "Resumen");
    H("div", "dr-item", s, "Tool: " + e.tool + " · n: " + (e.n === null || e.n === undefined ? "–" : f.int(e.n)) + (e.marker ? " · " + e.marker : "") +
      (e.canonical ? " · canónica (Fase 1)" : "") + " · techo: " + e.ceiling);
    if (r.afirmacion) H("p", null, s, r.afirmacion);
    if (r.columnas && r.filas) evTable(drSec(p1, "Resultado"), r.columnas, r.filas, 40);
    if ((e.no_comparable || []).length) H("p", null, drSec(p1, "No comparables"), e.no_comparable.join(", "));
    const p2 = panes["Método"];
    H("p", null, drSec(p2, "Método"), e.method + (e.variant ? " · variante: " + e.variant : ""));
    if (Object.keys(e.robustness || {}).length) H("div", "dr-pre", drSec(p2, "Robustez"), JSON.stringify(e.robustness, null, 1));
    if ((r.notas || []).length) { const sn = drSec(p2, "Supuestos y notas"); r.notas.forEach(n => H("div", "dr-item", sn, n)); }
    if ((e.caveat_ids || []).length) { const sc = drSec(p2, "Precauciones"); e.caveat_ids.forEach(id => { const x = BR.issues[id]; rich(H("div", "dr-item", sc), x ? x.titulo : id); }); }
    const p3 = panes["Consulta"];
    if (e.query_text) H("div", "dr-pre", drSec(p3, e.kind === "analysis" ? "Análisis con parámetros" : "SQL"), e.query_text);
    H("div", "dr-pre", drSec(p3, "Parámetros"), JSON.stringify(e.params, null, 1));
    if (e.code) H("div", "dr-pre", drSec(p3, "Código"), e.code);
    const p4 = panes["Fuente"];
    const tables = [...new Set(((e.query_text || "") + " " + (e.code || "")).match(/mart\.\w+/g) || [])];
    H("p", null, drSec(p4, "Tablas del mart"), tables.length ? tables.join(", ") : (e.canonical ? "Registro de afirmaciones de la Fase 1 (brain/evidence/canonical_findings.yaml)" : "mart.customer_month"));
    H("p", null, drSec(p4, "Cadena de origen"), "mart ← finora_analytical_dataset.csv (pipeline de la Fase 1, con paridad exacta) ← Transactions.csv + Industry.csv");
    H("div", "dr-pre", drSec(p4, "Versiones"), "datos " + e.data_version + "\ncerebro " + e.brain_version + "\nresultado " + e.result_hash + "\nhuellas: " +
      Object.entries(D.meta.hashes).map(x => x[0] + " " + x[1]).join(" · "));
  }, trigger);
}

/* ================================================================== preparar narrativa (piezas, esqueleto, presentación) */
const NARR_ON = !!(LIVE && LIVE.narrativas);
const ROLES = ["Situación", "Hallazgo", "Implicación", "Decisión", "Acción"];
const AUDS = ["Mixta", "CEO", "CRO", "CFO"];
const NST = { list: [], current: null, doc: null };
const cut = (x, n) => (x.length > n ? x.slice(0, n).replace(/[\s,;:]+\S*$/, "") + "…" : x);
const NAR_RE = /^NAR-[0-9]{8}-[0-9]{6}-[0-9a-f]{4}$/;

async function napi(path, opts) {
  const r = await fetch(LIVE.api + "/narratives" + (path || ""), Object.assign({ headers: { "Content-Type": "application/json" } }, opts || {}));
  if (!r.ok) {
    const t = await r.json().catch(() => ({}));
    throw new Error(typeof t.detail === "string" ? t.detail : "Error " + r.status);
  }
  return r.json();
}
const post = body => ({ method: "POST", body: JSON.stringify(body || {}) });
const patch = body => ({ method: "PATCH", body: JSON.stringify(body) });
function toast(msg) {
  const t = H("div", "toast", document.body, msg);
  requestAnimationFrame(() => t.classList.add("on"));
  setTimeout(() => { t.classList.remove("on"); setTimeout(() => t.remove(), 300); }, 2600);
}
const stateTag = s => (!s ? null : EST[s] ? metaTag(s) : hypTag(s, true));
const tagLabel = el => (el ? Array.from(el.childNodes).filter(x => x.nodeType === 3).map(x => x.textContent).join("").trim() : "");

/* ---- piezas: fragmentos validados con su evidencia (texto, afirmaciones con cifras, gráfica e IDs) */
function canonClaims(ids) {
  return (ids || []).map(id => D.claims.find(c => c.id === id)).filter(Boolean).map(c => ({
    id: c.id, texto: c.claim, estado: c.estado,
    cifras: Object.fromEntries((c.evidence || []).map(k => [(c.etiquetas || {})[k] || k, String(FACT[k])])) }));
}
function cardVisual(key) {
  const card = document.querySelector('main .card[data-card="' + key + '"]');
  const ch = card && card.querySelector(".chart[data-chart]");
  return ch ? { tipo: "workspace", chart: ch.dataset.chart, tarjeta: key, titulo: (card.querySelector("h3") || {}).textContent || "" } : null;
}
function pieceFromAnswer(qid) {
  const a = ANS.preguntas[qid], g = BR.golden.find(x => x.id === qid);
  return { tipo: "respuesta", titulo: g ? g.pregunta : qid, texto: a.titular + " " + a.respuesta, estado: a.estado,
           afirmaciones: canonClaims(a.claims), fuente: { kind: "respuesta", ref: qid },
           visual: a.visual ? { tipo: "workspace", chart: a.visual, titulo: a.visual_titulo || a.titular } : null };
}
function pieceFromSection(sid, el) {
  const a = ANS.secciones[sid], sq = el.closest(".section") && el.closest(".section").querySelector(".question");
  return { tipo: "seccion", titulo: sq ? sq.textContent.trim() : sid, texto: a.respuesta, estado: a.estado,
           afirmaciones: canonClaims(a.claims), fuente: { kind: "seccion", ref: sid },
           visual: a.lectura ? cardVisual(a.lectura.tarjeta) : null };
}
function pieceFromCard(card) {
  const key = card.dataset.card, info = BR.cards[key] || {}, lect = card.querySelector(".lectura");
  return { tipo: "tarjeta", titulo: ((card.querySelector("h3") || {}).textContent || key).trim(),
           texto: [lect ? lect.textContent.trim() : "", info.muestra || ""].filter(Boolean).join(" "),
           estado: tagLabel(card.querySelector(".card-top .tag")), afirmaciones: canonClaims(info.claims),
           fuente: { kind: "tarjeta", ref: key }, visual: cardVisual(key) };
}
function pieceFromClaim(id) {
  const c = D.claims.find(x => x.id === id);
  const key = Object.keys(BR.cards).find(k => (BR.cards[k].claims || []).includes(id) && cardVisual(k));
  return { tipo: "afirmacion", titulo: c.claim, texto: c.claim, estado: c.estado, afirmaciones: canonClaims([id]),
           fuente: { kind: "afirmacion", ref: id }, visual: key ? cardVisual(key) : null };
}
function invVisual(doc, vid) {
  const v = (doc.visuals || {})[vid];
  if (!v) return null;
  if (v.spec.tipo === "tarjeta") { const cv = cardVisual(v.spec.tarjeta); return cv ? Object.assign(cv, { titulo: v.titulo }) : null; }
  return { tipo: "spec", spec: v.spec, titulo: v.titulo };
}
const invClaims = (doc, ids) => (ids || []).map(id => (doc.claims || {})[id]).filter(Boolean)
  .map(c => ({ id: c.id, texto: c.texto, estado: c.estado, cifras: {} }));
function pieceFromInvAnswer(doc) {
  const ra = doc.narrativa.respuesta_ejecutiva, vm = pickMainVisual(doc), cl = invClaims(doc, ra.claim_ids);
  return { tipo: "respuesta_inv", titulo: doc.pregunta.slice(0, 280), texto: (ra.titular ? ra.titular + ". " : "") + ra.texto,
           estado: cl.length ? cl[0].estado : "", afirmaciones: cl, fuente: { kind: "investigacion", ref: doc.id },
           visual: vm ? invVisual(doc, vm.id) : null };
}
function pieceFromFinding(doc, hz) {
  const hyp = (doc.hipotesis || []).find(h => h.id === hz.hipotesis_id);
  return { tipo: "hallazgo", titulo: hz.titular || hz.pregunta, texto: [hz.interpretacion, hz.implicacion].filter(Boolean).join(" "),
           estado: hyp ? hyp.estado : "", afirmaciones: invClaims(doc, hz.claim_ids),
           fuente: { kind: "investigacion", ref: doc.id, hallazgo: hz.hipotesis_id },
           visual: (hz.visual_ids || []).length ? invVisual(doc, hz.visual_ids[0]) : null };
}
function narButton(parent, makePiece, cls, label) {
  if (!NARR_ON) return null;
  const b = H("button", cls || "inv", parent, label || "＋ Narrativa");
  b.type = "button";
  b.title = "Guardar en una narrativa";
  b.addEventListener("click", e => { e.stopPropagation(); saveToNarrative(makePiece, b); });
  return b;
}

/* ---- guardar una pieza: narrativa, papel en la historia y para qué sirve */
function roleButtons(parent, initial, onPick) {
  const box = H("div", "nar-roles", parent);
  ROLES.forEach(r => {
    const b = H("button", "nar-pill" + (r === initial ? " on" : ""), box, r);
    b.type = "button";
    b.addEventListener("click", () => { box.querySelectorAll("button").forEach(x => x.classList.toggle("on", x === b)); onPick(r); });
  });
  return box;
}
async function saveToNarrative(makePiece, trigger) {
  try { NST.list = await napi(""); } catch (e) { alert("No se pudo leer las narrativas: " + e.message); return; }
  const piece = makePiece();
  let rol = piece.tipo === "nota" ? "Decisión" : "Hallazgo";
  openDrawerWith("guardar en narrativa", piece.titulo, body => {
    const f = H("div", "nar-form", body);
    const s1 = drSec(f, "Narrativa");
    const sel = H("select", "nar-in", s1);
    NST.list.forEach(n => { const o = H("option", null, sel, n.titulo + " · " + n.piezas + " piezas"); o.value = n.id; });
    H("option", null, sel, "＋ Nueva narrativa…").value = "__new";
    sel.value = NST.list.some(n => n.id === NST.current) ? NST.current : NST.list.length ? NST.list[0].id : "__new";
    const nt = H("input", "nar-in", s1);
    nt.placeholder = "Título de la nueva narrativa (p. ej. Caso CFO)";
    nt.hidden = sel.value !== "__new";
    sel.addEventListener("change", () => { nt.hidden = sel.value !== "__new"; if (!nt.hidden) nt.focus(); });
    roleButtons(drSec(f, "Papel en la historia"), rol, r => { rol = r; });
    const nota = H("textarea", "nar-in", drSec(f, "¿Para qué sirve? ¿Qué explica después?"));
    nota.rows = 3;
    nota.placeholder = "Ej.: explica por qué no podemos leer el puente de MRR como comportamiento del cliente.";
    const pv = drSec(f, "Qué se guarda");
    const top = H("div", "tags", pv);
    top.style.justifyContent = "flex-start";
    const st = stateTag(piece.estado);
    if (st) top.appendChild(st);
    H("span", "muted", top, (piece.afirmaciones || []).length + " afirmaciones verificadas · " + (piece.visual ? "con gráfica" : "sin gráfica"));
    rich(H("p", null, pv), (piece.texto || "").slice(0, 420) + ((piece.texto || "").length > 420 ? "…" : ""));
    const go = btn(f, "Guardar pieza", "primary", async () => {
      go.disabled = true;
      try {
        let nid = sel.value;
        if (nid === "__new") {
          if (!nt.value.trim()) { nt.focus(); go.disabled = false; return; }
          nid = (await napi("", post({ titulo: nt.value.trim() }))).id;
        }
        const doc = await napi("/" + nid + "/piezas", post(Object.assign({}, piece, { rol: rol, nota: nota.value })));
        NST.current = nid;
        NST.doc = doc;
        closeDrawer(true);
        toast("Guardado en «" + doc.titulo + "» como " + rol);
      } catch (e) { alert(e.message); go.disabled = false; }
    });
  }, trigger);
}

/* ---- sección "Preparar narrativa" */
async function openStudio(nid) {
  const b = showDoc("Preparar narrativa", tagRaw("explo", "✎", "Narrativa asistida por IA"));
  H("p", "muted", b, "Cargando narrativas…");
  try {
    NST.list = await napi("");
    if (nid && NAR_RE.test(nid)) NST.current = nid;
    if (!NST.list.some(n => n.id === NST.current)) NST.current = NST.list.length ? NST.list[0].id : null;
    NST.doc = NST.current ? await napi("/" + NST.current) : null;
  } catch (e) { b.replaceChildren(); H("p", null, b, "No se pudo abrir: " + e.message); return; }
  setHash(NST.current ? "#narrativa/" + NST.current : "#narrativas");
  renderStudio(b);
}
async function refreshStudio() {
  NST.list = await napi("");
  NST.doc = NST.current ? await napi("/" + NST.current) : null;
  renderStudio($("invBody"));
}
function busyLine(parent, text) {
  const k = H("div", "answer-k analyzing nar-busy", parent);
  H("span", "spinner", k);
  k.append(text);
  return k;
}
function renderStudio(b) {
  b.replaceChildren();
  H("h1", "ans-q", b, "Preparar narrativa");
  H("p", "inv-frame", b, "Guarda piezas desde cualquier parte del workspace con ＋ Narrativa, profundiza con el agente y consolida una presentación. " +
    "El agente solo usa lo que guardaste: cada cifra de una lámina viene de una pieza citada, y lo que falta queda como pendiente.");
  const bar = H("div", "nar-bar", b);
  NST.list.forEach(n => {
    const c = H("button", "nar-chip" + (n.id === NST.current ? " on" : ""), bar, n.titulo + " · " + n.piezas);
    c.type = "button";
    c.addEventListener("click", () => openStudio(n.id));
  });
  btn(bar, "＋ Nueva narrativa", "", () => newNarrativeForm());
  if (NST.list.length >= 2) btn(bar, "Unir narrativas", "", () => mergeForm());
  const d = NST.doc;
  if (!d) {
    H("p", null, b, "Todavía no hay narrativas. Crea una, o usa ＋ Narrativa en una respuesta, una tarjeta o un hallazgo.");
    return;
  }
  // encabezado
  const head = H("div", "ans-main nar-head", b);
  const g1 = H("div", "nar-grid", head);
  const f = (lab, el) => { const w = H("label", "nar-field", g1); H("span", null, w, lab); w.appendChild(el); return el; };
  const ti = f("Título", H("input", "nar-in")); ti.value = d.titulo;
  const au = f("Audiencia", H("select", "nar-in")); AUDS.forEach(a => { H("option", null, au, a).value = a; }); au.value = d.audiencia || "Mixta";
  const ob = f("Objetivo", H("input", "nar-in")); ob.value = d.objetivo || ""; ob.placeholder = "Qué tiene que entender o decidir la audiencia";
  const cl = H("label", "nar-field wide", head);
  H("span", null, cl, "Contexto");
  const cx = H("textarea", "nar-in", cl);
  cx.rows = 4;
  cx.value = d.contexto || "";
  cx.placeholder = "Contexto completo (opcional): pega el caso, un correo o tus notas. El agente propone el esqueleto de la historia a partir de aquí.";
  const acts = H("div", "ans-actions", head);
  btn(acts, "Guardar cambios", "", async () => {
    try { NST.doc = await napi("/" + d.id, patch({ titulo: ti.value, audiencia: au.value, objetivo: ob.value, contexto: cx.value })); toast("Narrativa guardada"); refreshStudio(); }
    catch (e) { alert(e.message); }
  });
  const sk = btn(acts, d.esqueleto ? "Rehacer esqueleto con el agente" : "Proponer esqueleto con el agente", "primary", async () => {
    sk.disabled = true;
    const line = busyLine(head, "El agente arma el esqueleto de la historia… (cerca de un minuto)");
    try {
      await napi("/" + d.id, patch({ titulo: ti.value, audiencia: au.value, objetivo: ob.value, contexto: cx.value }));
      NST.doc = await napi("/" + d.id + "/esqueleto", post());
      renderStudio(b);
    } catch (e) { line.remove(); sk.disabled = false; alert(e.message); }
  });
  const del = btn(acts, "Borrar narrativa", "", async () => {
    if (!confirm("¿Borrar la narrativa «" + d.titulo + "» y sus piezas? No se puede deshacer.")) return;
    try { await napi("/" + d.id, { method: "DELETE" }); NST.current = null; openStudio(); } catch (e) { alert(e.message); }
  });
  del.classList.add("danger");
  if (d.esqueleto) renderSkeleton(b, d);
  // piezas
  const hp = H("h2", "inv-h2", b, "Piezas guardadas (" + d.piezas.length + ")");
  hp.id = "narPieces";
  const tools = H("div", "ans-actions", b);
  btn(tools, "＋ Hechos verificados", "", () => factsPicker());
  btn(tools, "＋ Nota o decisión", "", () => noteForm());
  if (!d.piezas.length) H("p", "muted", b, "Aún no hay piezas. Usa ＋ Narrativa en cualquier respuesta, sección, tarjeta o hallazgo.");
  const list = H("div", "nar-list", b);
  d.piezas.forEach((p, i) => renderPiece(list, d, p, i));
  // presentación
  const fin = H("div", "ans-main nar-final", b);
  H("div", "answer-k", fin, "Presentación");
  H("p", "ans-text", fin, d.presentacion
    ? "Hay una presentación consolidada" + (d.presentacion.degradada ? " sin texto libre (el agente no pasó el validador)." : " y validada.") + " Puedes verla o volver a consolidarla con las piezas actuales."
    : "Cuando tengas las piezas, el agente arma las láminas con ellas. Tarda de uno a tres minutos y usa tu plan.");
  const fa = H("div", "ans-actions", fin);
  if (d.presentacion) btn(fa, "Ver presentación →", "primary", () => openDeck(d.id));
  const cb = btn(fa, d.presentacion ? "Volver a consolidar" : "Consolidar presentación", d.presentacion ? "" : "primary", async () => {
    cb.disabled = true;
    const line = busyLine(fin, "El agente arma la presentación con tus piezas… (de uno a tres minutos)");
    try { NST.doc = await napi("/" + d.id + "/consolidar", post()); openDeck(d.id); }
    catch (e) { line.remove(); cb.disabled = false; alert(e.message); }
  });
  if (!d.piezas.some(p => p.tipo !== "nota")) cb.disabled = true;
}
function renderPiece(list, d, p, i) {
  const row = H("article", "nar-piece", list);
  const top = H("div", "nar-ptop", row);
  const rs = H("select", "nar-role", top);
  ROLES.forEach(r => { H("option", null, rs, r).value = r; });
  rs.value = p.rol;
  rs.addEventListener("change", async () => { try { NST.doc = await napi("/" + d.id, patch({ piezas: [{ id: p.id, rol: rs.value }] })); } catch (e) { alert(e.message); } });
  const st = stateTag(p.estado);
  if (st) top.appendChild(st);
  H("span", "mono muted", top, { respuesta: "respuesta", seccion: "sección", tarjeta: "tarjeta", hallazgo: "hallazgo", respuesta_inv: "investigación", afirmacion: "hecho verificado", nota: "nota tuya" }[p.tipo] || p.tipo);
  H("span", "sp", top);
  const mv = (dir) => async () => {
    const ids = d.piezas.map(x => x.id), j = i + dir;
    if (j < 0 || j >= ids.length) return;
    [ids[i], ids[j]] = [ids[j], ids[i]];
    try { NST.doc = await napi("/" + d.id, patch({ orden: ids })); renderStudio($("invBody")); } catch (e) { alert(e.message); }
  };
  const up = btn(top, "↑", "nar-mini", mv(-1)); up.title = "Subir";
  const dn = btn(top, "↓", "nar-mini", mv(1)); dn.title = "Bajar";
  const rm = btn(top, "Quitar", "nar-mini", async () => {
    if (!confirm("¿Quitar esta pieza de la narrativa?")) return;
    try { NST.doc = await napi("/" + d.id + "/piezas/" + p.id, { method: "DELETE" }); refreshStudio(); } catch (e) { alert(e.message); }
  });
  rm.title = "Quitar de la narrativa";
  rich(H("div", "nar-ptitle", row), p.titulo);
  if (p.texto && p.texto !== p.titulo) rich(H("p", "nar-ptext", row), p.texto.length > 360 ? p.texto.slice(0, 360) + "…" : p.texto);
  const meta = H("div", "nar-pmeta", row);
  if ((p.afirmaciones || []).length) H("span", null, meta, p.afirmaciones.length + " afirmaciones verificadas");
  if (p.visual) H("span", null, meta, "con gráfica");
  if (p.fuente && p.fuente.kind) { const o = btn(meta, "Abrir fuente", "inv", () => openPieceSource(p)); o.classList.remove("inv-btn"); }
  const nota = H("textarea", "nar-in nar-note", row);
  nota.rows = 2;
  nota.value = p.nota || "";
  nota.placeholder = "¿Para qué sirve en la historia? ¿Qué explica después?";
  nota.addEventListener("change", async () => { try { NST.doc = await napi("/" + d.id, patch({ piezas: [{ id: p.id, nota: nota.value }] })); toast("Nota guardada"); } catch (e) { alert(e.message); } });
  if (p.tipo !== "nota" && LIVE && LIVE.libre) {
    const dp = H("div", "nar-deep", row);
    const q = H("input", "nar-in", dp);
    q.placeholder = "Profundizar: ¿qué quieres preguntar a partir de esta pieza?";
    const go = btn(dp, "Investigar", "", () => { if (q.value.trim()) deepen(p, q.value.trim()); else q.focus(); });
    q.addEventListener("keydown", e => { if (e.key === "Enter") go.click(); });
  }
}
function renderSkeleton(b, d) {
  const sk = d.esqueleto;
  H("h2", "inv-h2", b, "Esqueleto de la historia");
  if (sk.resumen) rich(H("p", "inv-frame", b), sk.resumen);
  const box = H("div", "nar-sk", b);
  const pieceById = Object.fromEntries(d.piezas.map(p => [p.id, p]));
  sk.secciones.forEach(s => {
    const c = H("div", "nar-sec", box);
    H("span", "nar-pill on", c, s.rol);
    rich(H("div", "nar-ptitle", c), s.mensaje);
    if ((s.preguntas || []).length) { const ul = H("ul", "nar-q", c); s.preguntas.forEach(q => rich(H("li", null, ul), q)); }
    if ((s.piezas || []).length) {
      const m = H("div", "nar-pmeta", c, "Piezas que ya sirven: ");
      m.append(s.piezas.map(id => (pieceById[id] ? cut(pieceById[id].titulo, 70) : id)).join(" · "));
    }
    (s.afirmaciones || []).forEach(id => {
      const cl = D.claims.find(x => x.id === id);
      if (!cl) return;
      const r = H("div", "nar-suggest", c);
      r.appendChild(metaTag(cl.estado));
      rich(H("span", null, r), cl.claim);
      const have = d.piezas.some(p => p.fuente && p.fuente.kind === "afirmacion" && p.fuente.ref === id);
      if (have) H("span", "mono muted", r, "ya guardado");
      else btn(r, "＋ Guardar", "nar-mini", async () => {
        try { NST.doc = await napi("/" + d.id + "/piezas", post(Object.assign(pieceFromClaim(id), { rol: s.rol, nota: "Sugerido por el esqueleto: " + s.mensaje }))); refreshStudio(); }
        catch (e) { alert(e.message); }
      });
    });
    (s.huecos || []).forEach(q => {
      const r = H("div", "nar-gap", c);
      H("span", "mono", r, "hueco");
      rich(H("span", null, r), q);
      if (LIVE && LIVE.libre) btn(r, "Investigar", "nar-mini", () => startLive({ pregunta: q, contexto: {
        titulo: s.mensaje, texto: ((d.objetivo || "") + " " + (d.contexto || "")).slice(0, 3000),
        nota: "Hueco del esqueleto (" + s.rol + ")", claim_ids: s.afirmaciones || [], narrativa_id: d.id } }, q));
    });
  });
}
function deepen(p, q) {
  const canon = (p.afirmaciones || []).map(a => a.id).filter(id => /^C-[A-Z]{3}-\d{2}$/.test(id));
  const texto = [p.texto].concat((p.afirmaciones || []).map(a => a.texto)).join(" ").slice(0, 3800);
  startLive({ pregunta: q, contexto: { titulo: p.titulo, texto: texto, nota: p.nota || "", claim_ids: canon, narrativa_id: NST.current, pieza_id: p.id } }, q);
}
async function openPieceSource(p) {
  const f = p.fuente || {};
  if (f.kind === "respuesta") return openAnswer(f.ref);
  if (f.kind === "seccion") { closeInvestigation(); return goTo("#" + f.ref); }
  if (f.kind === "tarjeta") { closeInvestigation(); return goTo("#card-" + String(f.ref).replace(".", "-")); }
  if (f.kind === "afirmacion") { const c = D.claims.find(x => x.id === f.ref); if (c) openAnswerLineage({ titular: c.claim, estado: c.estado, claims: [c.id] }, null); return; }
  if (f.kind === "investigacion") {
    const g = Object.values(GOLDEN_INV).find(x => x.id === f.ref);
    if (g) return openInvestigation(g, { golden: true });
    const d = await fetch(LIVE.api + "/investigations/" + f.ref).then(r => (r.ok ? r.json() : null)).catch(() => null);
    if (d) openInvestigation(d); else alert("No encontré esa investigación en este servidor.");
  }
}
function newNarrativeForm() {
  openDrawerWith("nueva narrativa", "Nueva narrativa", body => {
    const f = H("div", "nar-form", body);
    const t = H("input", "nar-in", drSec(f, "Título"));
    t.placeholder = "Ej.: Caso CFO · qué mide hoy el MRR";
    const a = H("select", "nar-in", drSec(f, "Audiencia"));
    AUDS.forEach(x => { H("option", null, a, x).value = x; });
    const o = H("input", "nar-in", drSec(f, "Objetivo (opcional)"));
    o.placeholder = "Qué tiene que entender o decidir la audiencia";
    const c = H("textarea", "nar-in", drSec(f, "Contexto completo (opcional)"));
    c.rows = 6;
    c.placeholder = "Pega el caso, un correo o tus notas. Luego el agente puede proponer el esqueleto de la historia.";
    const go = btn(f, "Crear narrativa", "primary", async () => {
      if (!t.value.trim()) { t.focus(); return; }
      go.disabled = true;
      try { const d = await napi("", post({ titulo: t.value, audiencia: a.value, objetivo: o.value, contexto: c.value })); closeDrawer(true); openStudio(d.id); }
      catch (e) { alert(e.message); go.disabled = false; }
    });
    setTimeout(() => t.focus(), 0);
  }, null);
}
function mergeForm() {
  openDrawerWith("unir narrativas", "Unir narrativas", body => {
    const f = H("div", "nar-form", body);
    H("p", null, drSec(f, "Cómo funciona"), "Crea una narrativa nueva con todas las piezas, sin duplicar la misma fuente y en el orden de la historia. Las originales no cambian.");
    const s = drSec(f, "Narrativas");
    const checks = NST.list.map(n => { const l = H("label", "nar-check", s); const c = H("input", null, l); c.type = "checkbox"; c.value = n.id; l.append(" " + n.titulo + " · " + n.piezas + " piezas"); return c; });
    const t = H("input", "nar-in", drSec(f, "Título de la narrativa unida"));
    t.placeholder = "Ej.: Historia para CEO, CRO y CFO";
    const go = btn(f, "Unir", "primary", async () => {
      const ids = checks.filter(c => c.checked).map(c => c.value);
      if (ids.length < 2) { alert("Elige al menos dos narrativas."); return; }
      go.disabled = true;
      try { const d = await napi("/merge", post({ ids: ids, titulo: t.value })); closeDrawer(true); openStudio(d.id); }
      catch (e) { alert(e.message); go.disabled = false; }
    });
  }, null);
}
function factsPicker() {
  const d = NST.doc;
  let rol = "Hallazgo";
  openDrawerWith("hechos verificados", "Agregar hechos verificados", body => {
    const f = H("div", "nar-form", body);
    roleButtons(drSec(f, "Papel en la historia"), rol, r => { rol = r; });
    const q = H("input", "nar-in", drSec(f, "Buscar"));
    q.placeholder = "churn, ticket, altas, cobro…";
    const list = H("div", "nar-facts", f);
    const draw = () => {
      list.replaceChildren();
      const t = normTxt(q.value.trim());
      D.claims.filter(c => !t || matches(c.claim + " " + c.dominio + " " + c.id, t)).forEach(c => {
        const r = H("div", "nar-suggest", list);
        r.appendChild(metaTag(c.estado));
        rich(H("span", null, r), c.claim);
        const have = d.piezas.some(p => p.fuente && p.fuente.kind === "afirmacion" && p.fuente.ref === c.id);
        if (have) { H("span", "mono muted", r, "ya está"); return; }
        const b = btn(r, "＋", "nar-mini", async () => {
          b.disabled = true;
          try { NST.doc = await napi("/" + d.id + "/piezas", post(Object.assign(pieceFromClaim(c.id), { rol: rol, nota: "" }))); b.textContent = "✓"; toast("Agregado como " + rol); renderStudio($("invBody")); }
          catch (e) { alert(e.message); b.disabled = false; }
        });
      });
    };
    q.addEventListener("input", draw);
    draw();
  }, null);
}
function noteForm() {
  const d = NST.doc;
  let rol = "Decisión";
  openDrawerWith("nota o decisión", "Nota o decisión propia", body => {
    const f = H("div", "nar-form", body);
    H("p", null, drSec(f, "Qué es"), "Una idea tuya (una decisión, una acción, una transición). Orienta la historia, pero no cuenta como evidencia: el agente no saca cifras de aquí.");
    roleButtons(drSec(f, "Papel en la historia"), rol, r => { rol = r; });
    const t = H("input", "nar-in", drSec(f, "Enunciado"));
    t.placeholder = "Ej.: Registrar los descuentos temporales antes de lanzarlos";
    const n = H("textarea", "nar-in", drSec(f, "Por qué o para qué"));
    n.rows = 3;
    const go = btn(f, "Guardar nota", "primary", async () => {
      if (!t.value.trim()) { t.focus(); return; }
      go.disabled = true;
      try { NST.doc = await napi("/" + d.id + "/piezas", post({ tipo: "nota", rol: rol, titulo: t.value, texto: "", nota: n.value })); closeDrawer(true); refreshStudio(); }
      catch (e) { alert(e.message); go.disabled = false; }
    });
  }, null);
}

/* ---- presentación en láminas web */
async function openDeck(nid) {
  let d = NST.doc && NST.doc.id === nid ? NST.doc : null;
  if (!d) { try { d = await napi("/" + nid); } catch (e) { alert(e.message); return; } }
  NST.doc = d;
  NST.current = d.id;
  const deck = d.presentacion;
  if (!deck) return openStudio(nid);
  const b = showDoc("Presentación · " + d.titulo, deck.degradada ? tagRaw("prec", "!", "Sin texto libre") : tagRaw("hecho", "✓", "Validada"));
  setHash("#presentacion/" + d.id);
  const tools = H("div", "ans-actions deck-tools", b);
  btn(tools, "← Volver a la narrativa", "", () => openStudio(d.id));
  btn(tools, "Imprimir o guardar PDF", "", () => { document.body.classList.add("print-deck"); window.print(); setTimeout(() => document.body.classList.remove("print-deck"), 800); });
  H("h1", "deck-title", b, deck.titulo);
  if (deck.subtitulo) rich(H("p", "deck-sub", b), deck.subtitulo);
  const pieces = Object.fromEntries(d.piezas.map(p => [p.id, p]));
  deck.laminas.forEach((s, i) => {
    const sl = H("section", "slide", b);
    const hd = H("div", "slide-head", sl);
    H("span", "nar-pill on", hd, s.rol);
    H("span", "mono muted", hd, (i + 1) + " / " + deck.laminas.length);
    rich(H("h2", "slide-t", sl), s.titulo);
    rich(H("p", "slide-m", sl), s.mensaje);
    const grid = H("div", "slide-grid" + (s.visual ? "" : " solo"), sl);
    if ((s.puntos || []).length) { const ul = H("ul", "slide-pts", grid); s.puntos.forEach(t => rich(H("li", null, ul), t)); }
    const vp = s.visual && pieces[s.visual];
    if (vp && vp.visual) {
      const v = vp.visual, box = H("div", "slide-viz", grid);
      if (v.tipo === "workspace") { const card = mountChart(box, v.chart); const h = H("div", "viz-h"); rich(h, v.titulo || ""); card.prepend(h); }
      else if (v.spec) visualCard(box, { titulo: v.titulo || "", spec: v.spec }, true);
    }
    const ev = H("div", "slide-ev", sl);
    H("span", "mono muted", ev, "Evidencia:");
    (s.piezas || []).forEach(id => {
      const p = pieces[id];
      if (!p) return;
      const c = H("button", "ev-chip", ev, cut(p.titulo, 70));
      c.type = "button";
      c.title = p.estado || "";
      c.addEventListener("click", () => openPieceSource(p));
    });
    if (s.notas) { const det = H("details", "slide-notes", sl); H("summary", null, det, "Notas del presentador"); rich(H("p", null, det), s.notas); }
  });
  if ((deck.pendientes || []).length) {
    H("h2", "inv-h2", b, "Pendientes: lo que la historia necesita y aún no tiene evidencia");
    const box = H("div", "inv-blocks deck-pend", b);
    deck.pendientes.forEach(q => {
      const r = H("div", "inv-block", box);
      H("span", "nar-pill on", r, q.rol);
      rich(H("span", null, r), " " + q.que_falta);
      if (q.pregunta && LIVE && LIVE.libre) btn(r, "Investigar: " + cut(q.pregunta, 160), "nar-mini", () => startLive({ pregunta: q.pregunta, contexto: {
        titulo: q.que_falta, texto: ((d.objetivo || "") + " " + (d.contexto || "")).slice(0, 3000), nota: "Pendiente de la presentación (" + q.rol + ")", claim_ids: [], narrativa_id: d.id } }, q.pregunta));
    });
  }
  const foot = H("div", "inv-foot", b);
  const tries = (deck.intentos || []).length;
  const own = (deck.uso || {}).costo_equivalente_usd || 0;
  const all = Object.values(d.uso || {}).reduce((a, x) => a + ((x && x.costo_equivalente_usd) || 0), 0);
  foot.textContent = (deck.degradada ? "El texto libre no pasó el validador en " + tries + " intentos: se muestran las piezas tal cual. "
    : "Validada: cada cifra de cada lámina está en las piezas que cita" + (tries > 1 ? " (aprobada en el intento " + tries + ")" : "") + ". ") +
    "Generada " + new Date(deck.generado_ms).toLocaleString("es-CO") +
    (own ? " · costo equivalente en API de esta presentación: US$ " + f.num(own, 2) : "") +
    (all ? " · de la narrativa completa: US$ " + f.num(all, 2) + " (con suscripción no se cobra por token)" : "");
  $("invBack").focus();
}

/* ================================================================== controles */
const isTyping = t => t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.isContentEditable);
function wireControls() {
  document.querySelectorAll("#corrControls .seg").forEach(seg => seg.querySelectorAll("button").forEach(b => {
    b.type = "button";
    b.addEventListener("click", () => { const key = seg.dataset.key; setCorr({ [key]: key === "lag" ? Number(b.textContent) : b.textContent }); });
  }));
  document.querySelectorAll("#cohortControls .seg").forEach(seg => seg.querySelectorAll("button").forEach(b => {
    b.type = "button";
    b.addEventListener("click", () => setCoh({ [seg.dataset.key]: b.textContent }));
  }));
  document.querySelectorAll(".tbtn:not(.how)").forEach(btn => btn.addEventListener("click", () => {
    const card = btn.closest(".card");
    const tv = card.querySelector(".table-view");
    if (!tv) return;
    const open = btn.getAttribute("aria-pressed") !== "true";
    btn.setAttribute("aria-pressed", String(open));
    btn.textContent = open ? "Ocultar datos" : "Ver datos";
    card._tableOpen = open;
    tv.hidden = !open;
    if (open) renderTableView(card);
  }));
  document.querySelectorAll(".tbtn.how").forEach(btn => btn.addEventListener("click", () => openHow(btn.dataset.how, btn)));
  document.querySelectorAll("[data-open-palette]").forEach(b => b.addEventListener("click", () => palOpen(null, b)));
  document.querySelectorAll(".inv[data-qid]").forEach(b => b.addEventListener("click", () => openAnswer(b.dataset.qid)));
  document.querySelectorAll("[data-close]").forEach(b => b.addEventListener("click", () => { palClose(); closeDrawer(); }));
  $("invBack").addEventListener("click", closeInvestigation);
  $("scrim").addEventListener("click", () => { palClose(); closeDrawer(); });
  const inp = $("palInput");
  inp.addEventListener("input", palList);
  inp.addEventListener("keydown", e => {
    if (e.key === "ArrowDown") { e.preventDefault(); palSel(pal.sel + 1); }
    else if (e.key === "ArrowUp") { e.preventDefault(); palSel(pal.sel - 1); }
    else if (e.key === "Enter" && pal.sel >= 0 && pal.items[pal.sel]) { e.preventDefault(); pal.items[pal.sel].go(); }
  });
  document.addEventListener("keydown", e => {
    if ((e.metaKey || e.ctrlKey) && !e.altKey && (e.key === "k" || e.key === "K")) { e.preventDefault(); if (pal.open) palClose(); else palOpen(); return; }
    if (e.key === "Escape") {
      if (pal.open) { e.preventDefault(); palClose(); } else if (drawerOpen) { e.preventDefault(); closeDrawer(); }
      else if (invOpen) { e.preventDefault(); closeInvestigation(); }
      return;
    }
    if (e.key === "/" && !pal.open && !drawerOpen && !isTyping(e.target) && !e.metaKey && !e.ctrlKey) { e.preventDefault(); palOpen(); }
  });
}

function init() {
  $("palette").inert = true;
  $("drawer").inert = true;
  buildTables();
  buildSparks();
  renderAnswers();
  wireControls();
  if (NARR_ON) {
    // acceso a "Preparar narrativa" y "＋ Narrativa" en cada tarjeta (después de wireControls: no son botones de datos)
    const ab = document.querySelector(".side .askbtn");
    if (ab) {
      const nb = document.createElement("button");
      nb.type = "button";
      nb.className = "askbtn nar-entry";
      H("span", "spark-ic", nb, "✎");
      H("span", "lbl", nb, "Preparar narrativa");
      nb.addEventListener("click", () => openStudio());
      ab.after(nb);
    }
    document.querySelectorAll("main .card[data-card] .foot .btns").forEach(bt => {
      const card = bt.closest(".card");
      narButton(bt, () => pieceFromCard(card), "tbtn nar", "＋ Narrativa");
    });
  }
  updateCorrText();
  document.querySelectorAll("[data-chart]").forEach(mount);
  wireNav();
  const m = location.hash.match(/^#(investigacion|respuesta)\/(Q\d)$/);
  const run = location.hash.match(/^#investigacion\/(INV-[0-9]{8}-[0-9]{6}-[0-9a-f]{4})$/);
  if (m && m[1] === "investigacion" && GOLDEN_INV[m[2]]) openInvestigation(GOLDEN_INV[m[2]], { golden: true });
  else if (m && m[1] === "respuesta" && (ANS.preguntas || {})[m[2]]) openAnswer(m[2]);
  else if (run && LIVE) fetch(LIVE.api + "/investigations/" + run[1]).then(r => (r.ok ? r.json() : null)).then(d => { if (d) openInvestigation(d); }).catch(() => {});
  else if (NARR_ON) {
    const nr = location.hash.match(/^#(narrativa|presentacion)\/(NAR-[0-9]{8}-[0-9]{6}-[0-9a-f]{4})$/);
    if (location.hash === "#narrativas") openStudio();
    else if (nr) (nr[1] === "presentacion" ? openDeck(nr[2]) : openStudio(nr[2]));
  }
}
if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
