/* ==========================================================================
   html-slide-renderer · primitives.js
   Low-level composition primitives for executive slides. NOT templates.

   A slide registers drawing code with P.draw('S03', (s, P) => { ... }).
   `s` is a Slide context bound to <main class="slide" data-slide="S03">.
   Everything is drawn in canvas coordinates (1920x1080). HTML text for words,
   SVG for geometry. Connectors/brackets/callouts are anchored to the REAL
   layout boxes of elements, measured after web fonts load, so they never
   drift when text wraps.

   Lifecycle: DOMContentLoaded -> fit -> fonts loaded -> draw fns (in order)
   -> declarative <x-connect>/<x-bracket>/<x-callout> -> window.__slideReady.
   Errors are collected in window.__slideErrors (the QA probe reports them).
   ========================================================================== */
(function (global) {
  'use strict';
  const SVGNS = 'http://www.w3.org/2000/svg';
  const TOKENS = ['ink', 'ink-2', 'ink-3', 'ink-4', 'ink-5', 'accent', 'accent-2', 'accent-soft', 'accent-ink',
    'accent-text', 'neg', 'pos', 'rule', 'bg', 'surface', 'highlight'];
  const LW = { hair: 1.5, thin: 2, med: 3, bold: 5, heavy: 8 };
  const ANCHORS = {
    tl: [0, 0], tc: [0.5, 0], tr: [1, 0],
    ml: [0, 0.5], mc: [0.5, 0.5], mr: [1, 0.5],
    bl: [0, 1], bc: [0.5, 1], br: [1, 1],
  };
  const errors = (global.__slideErrors = global.__slideErrors || []);
  const report = (e, id) => { errors.push({ slide: id || null, message: String(e && e.message || e) }); console.error('[primitives]', id || '', e); };

  /* ---------------- value helpers ---------------- */
  const color = (v) => {
    if (v == null || v === false || v === 'none') return 'none';
    if (v === 'transparent' || v === 'currentColor') return v;
    return TOKENS.includes(v) ? `var(--${v})` : v;
  };
  const lw = (v) => (v == null ? 2 : typeof v === 'number' ? v : (LW[v] ?? parseFloat(v)));
  const dashArray = (v, w) => {
    if (!v || v === 'none' || v === 'solid') return null;
    if (v === 'dot') return `0 ${Math.max(6, w * 3.2)}`;
    if (v === 'dash') return `${w * 5} ${w * 4}`;
    if (v === 'longdash') return `${w * 10} ${w * 6}`;
    return String(v);
  };
  const r2 = (n) => Math.round(n * 100) / 100;
  const pt = (p) => `${r2(p[0])},${r2(p[1])}`;

  /* ---------------- geometry ---------------- */
  const geo = {
    lerp: (a, b, t) => a + (b - a) * t,
    mid: (p, q) => [(p[0] + q[0]) / 2, (p[1] + q[1]) / 2],
    dist: (p, q) => Math.hypot(q[0] - p[0], q[1] - p[1]),
    /** 0deg = 12 o'clock, clockwise. */
    polar(cx, cy, r, deg) { const a = (deg - 90) * Math.PI / 180; return [cx + r * Math.cos(a), cy + r * Math.sin(a)]; },
    /** n points evenly around a circle, starting at startDeg. */
    around(n, cx, cy, r, startDeg = 0, sweep = 360) {
      const step = sweep >= 360 ? 360 / n : sweep / Math.max(1, n - 1);
      return Array.from({ length: n }, (_, i) => geo.polar(cx, cy, r, startDeg + i * step));
    },
    /** n centers evenly spaced between a and b (inclusive ends when inset=0). */
    distribute(n, a, b, inset = 0) {
      if (n === 1) return [(a + b) / 2];
      const s = (b - a - 2 * inset) / (n - 1);
      return Array.from({ length: n }, (_, i) => a + inset + i * s);
    },
    circle(cx, cy, r) { return `M${r2(cx - r)},${r2(cy)} a${r},${r} 0 1,0 ${r * 2},0 a${r},${r} 0 1,0 ${-r * 2},0`; },
    /** open arc from a0 to a1 degrees (clockwise if a1>a0). */
    arc(cx, cy, r, a0, a1) {
      const p0 = geo.polar(cx, cy, r, a0), p1 = geo.polar(cx, cy, r, a1);
      const large = Math.abs(a1 - a0) > 180 ? 1 : 0, sweep = a1 > a0 ? 1 : 0;
      return `M${pt(p0)} A${r},${r} 0 ${large} ${sweep} ${pt(p1)}`;
    },
    /** donut sector between radii r0<r1 and angles a0<a1 (degrees, clockwise). */
    ring(cx, cy, r0, r1, a0 = 0, a1 = 360) {
      if (a1 - a0 >= 359.99) return `${geo.circle(cx, cy, r1)} ${r0 > 0 ? geo.circle(cx, cy, r0) : ''}`;
      const o0 = geo.polar(cx, cy, r1, a0), o1 = geo.polar(cx, cy, r1, a1);
      const i1 = geo.polar(cx, cy, r0, a1), i0 = geo.polar(cx, cy, r0, a0);
      const large = a1 - a0 > 180 ? 1 : 0;
      if (r0 <= 0) return `M${cx},${cy} L${pt(o0)} A${r1},${r1} 0 ${large} 1 ${pt(o1)} Z`;
      return `M${pt(o0)} A${r1},${r1} 0 ${large} 1 ${pt(o1)} L${pt(i1)} A${r0},${r0} 0 ${large} 0 ${pt(i0)} Z`;
    },
    /** polyline with rounded corners (radius clamped to half of each segment). */
    rounded(points, r = 12) {
      if (points.length < 3 || !r) return 'M' + points.map(pt).join(' L');
      let d = `M${pt(points[0])}`;
      for (let i = 1; i < points.length - 1; i++) {
        const p0 = points[i - 1], p1 = points[i], p2 = points[i + 1];
        const v0 = [p1[0] - p0[0], p1[1] - p0[1]], v1 = [p2[0] - p1[0], p2[1] - p1[1]];
        const l0 = Math.hypot(...v0), l1 = Math.hypot(...v1);
        const rr = Math.min(r, l0 / 2, l1 / 2);
        const a = [p1[0] - v0[0] / l0 * rr, p1[1] - v0[1] / l0 * rr];
        const b = [p1[0] + v1[0] / l1 * rr, p1[1] + v1[1] / l1 * rr];
        d += ` L${pt(a)} Q${pt(p1)} ${pt(b)}`;
      }
      return d + ` L${pt(points[points.length - 1])}`;
    },
    /** trapezoid centered on cx (funnel stage): top width wt, bottom width wb. */
    trapezoid(cx, y, wt, wb, h) {
      return `M${r2(cx - wt / 2)},${y} L${r2(cx + wt / 2)},${y} L${r2(cx + wb / 2)},${y + h} L${r2(cx - wb / 2)},${y + h} Z`;
    },
    /** process chevron. Use sparingly: a sequence is usually better as a line with stages. */
    chevron(x, y, w, h, notch = 24, first = false) {
      const n = notch;
      return `M${x},${y} L${x + w - n},${y} L${x + w},${y + h / 2} L${x + w - n},${y + h} L${x},${y + h}` + (first ? ' Z' : ` L${x + n},${y + h / 2} Z`);
    },
    /** vertical curly brace from y0 to y1 at x; dir 'right' points its tip to +x. */
    brace(x, y0, y1, depth = 18, dir = 'right') {
      const s = dir === 'right' ? 1 : -1, q = depth / 2 * s, d = depth * s, ym = (y0 + y1) / 2;
      const k = Math.min(Math.abs(q), (y1 - y0) / 4);
      return `M${x},${y0} Q${x + q},${y0} ${x + q},${y0 + k} L${x + q},${ym - k} Q${x + q},${ym} ${x + d},${ym} ` +
        `Q${x + q},${ym} ${x + q},${ym + k} L${x + q},${y1 - k} Q${x + q},${y1} ${x},${y1}`;
    },
    /** horizontal curly brace from x0 to x1 at y; dir 'down' points its tip to +y. */
    braceH(x0, x1, y, depth = 18, dir = 'down') {
      const s = dir === 'down' ? 1 : -1, q = depth / 2 * s, d = depth * s, xm = (x0 + x1) / 2;
      const k = Math.min(Math.abs(q), (x1 - x0) / 4);
      return `M${x0},${y} Q${x0},${y + q} ${x0 + k},${y + q} L${xm - k},${y + q} Q${xm},${y + q} ${xm},${y + d} ` +
        `Q${xm},${y + q} ${xm + k},${y + q} L${x1 - k},${y + q} Q${x1},${y + q} ${x1},${y}`;
    },
  };

  /* ---------------- 12-column grid helpers ---------------- */
  const grid = {
    col: (k) => 112 + 144 * (k - 1),               // x where column k starts (1..12)
    colEnd: (k) => 112 + 144 * (k - 1) + 112,      // x where column k ends
    span: (a, b) => ({ x: 112 + 144 * (a - 1), w: 144 * (b - a) + 112 }),
  };

  /* ---------------- number formatting ---------------- */
  const fmt = (v, o = {}) => {
    const { d = 0, prefix = '', suffix = '', sign = false, locale = 'es-MX' } = o;
    const s = Math.abs(v).toLocaleString(locale, { minimumFractionDigits: d, maximumFractionDigits: d });
    const sg = v < 0 ? '−' : (sign && v > 0 ? '+' : '');
    return `${sg}${prefix}${s}${suffix}`;
  };

  /* ---------------- minimal line glyphs (only when they ENCODE meaning) ---------------- */
  const GLYPHS = {
    check: 'M5 12.5 L10 17 L19 7', cross: 'M6 6 L18 18 M18 6 L6 18', plus: 'M12 5 V19 M5 12 H19', minus: 'M5 12 H19',
    arrow: 'M4 12 H19 M13 6 L19 12 L13 18', warn: 'M12 3 L22 20 H2 Z M12 9 V14 M12 17 V17.2',
    person: 'M12 11 a4 4 0 1 0 0-8 a4 4 0 1 0 0 8 M4 21 c0-4.4 3.6-7 8-7 s8 2.6 8 7',
    team: 'M9 10 a3.2 3.2 0 1 0 0-6.4 a3.2 3.2 0 1 0 0 6.4 M2.5 20 c0-3.6 2.9-6 6.5-6 s6.5 2.4 6.5 6 M16 10 a2.6 2.6 0 1 0 0-5.2 M17.5 13.6 c2.4.5 4 2.5 4 5.4',
    doc: 'M6 3 H14 L19 8 V21 H6 Z M14 3 V8 H19 M9 13 H16 M9 17 H16',
    db: 'M4 6 c0-1.7 3.6-3 8-3 s8 1.3 8 3 v12 c0 1.7-3.6 3-8 3 s-8-1.3-8-3 Z M4 6 c0 1.7 3.6 3 8 3 s8-1.3 8-3 M4 12 c0 1.7 3.6 3 8 3 s8-1.3 8-3',
    gear: 'M12 15.5 a3.5 3.5 0 1 0 0-7 a3.5 3.5 0 1 0 0 7 M12 2 V5 M12 19 V22 M2 12 H5 M19 12 H22 M4.9 4.9 L7 7 M17 17 L19.1 19.1 M4.9 19.1 L7 17 M17 7 L19.1 4.9',
    clock: 'M12 21 a9 9 0 1 0 0-18 a9 9 0 1 0 0 18 M12 7 V12 L15.5 14',
    target: 'M12 21 a9 9 0 1 0 0-18 a9 9 0 1 0 0 18 M12 16.5 a4.5 4.5 0 1 0 0-9 a4.5 4.5 0 1 0 0 9 M12 12.6 a.6 .6 0 1 0 0-1.2',
  };

  /* ========================================================================
     Slide context
     ======================================================================== */
  class Slide {
    constructor(root) { this.root = root; this.id = root.dataset.slide; this._layers = {}; }

    get scale() { const r = this.root.getBoundingClientRect(); return (r.width / this.root.offsetWidth) || 1; }
    q(sel) { return typeof sel === 'string' ? this.root.querySelector(sel) : sel; }
    qa(sel) { return [...this.root.querySelectorAll(sel)]; }

    /** Layout box of an element (or a point [x,y]) in canvas coordinates. */
    box(target, pad = 0) {
      if (Array.isArray(target) && typeof target[0] === 'number') {
        const [x, y] = target; return { x, y, w: 0, h: 0, l: x, t: y, r: x, b: y, cx: x, cy: y, point: true };
      }
      const e = this.q(target);
      if (!e) throw new Error(`element not found: ${target}`);
      const R = this.root.getBoundingClientRect(), r = e.getBoundingClientRect(), s = this.scale;
      const x = (r.left - R.left) / s - pad, y = (r.top - R.top) / s - pad, w = r.width / s + 2 * pad, h = r.height / s + 2 * pad;
      return { x, y, w, h, l: x, t: y, r: x + w, b: y + h, cx: x + w / 2, cy: y + h / 2 };
    }
    /** Union box of several targets (selectors, elements or points). */
    union(targets, pad = 0) {
      const list = typeof targets === 'string' ? targets.split(',').map((t) => t.trim()) : targets;
      const bs = list.flatMap((t) => (typeof t === 'string' && !t.startsWith('#') && !t.startsWith('[') ? this.qa(t) : [t])).map((t) => this.box(t));
      const l = Math.min(...bs.map((b) => b.l)) - pad, t = Math.min(...bs.map((b) => b.t)) - pad;
      const r = Math.max(...bs.map((b) => b.r)) + pad, b = Math.max(...bs.map((b) => b.b)) + pad;
      return { x: l, y: t, w: r - l, h: b - t, l, t, r, b, cx: (l + r) / 2, cy: (t + b) / 2 };
    }

    /** Full-canvas SVG layer. 'main' sits under HTML text (z 1); {below:true} z 0; {above:true} z 5. */
    layer(name = 'main', o = {}) {
      if (this._layers[name]) return this._layers[name];
      let svg = this.root.querySelector(`svg.layer[data-layer="${name}"]`);
      if (!svg) {
        svg = document.createElementNS(SVGNS, 'svg');
        svg.setAttribute('class', `layer${o.below ? ' below' : ''}${o.above ? ' above' : ''}`);
        svg.setAttribute('viewBox', '0 0 1920 1080');
        svg.setAttribute('data-layer', name);
        svg.setAttribute('aria-hidden', 'true');
        o.below ? this.root.prepend(svg) : this.root.appendChild(svg);
      }
      return (this._layers[name] = svg);
    }
    group(o = {}) { const g = document.createElementNS(SVGNS, 'g'); if (o.id) g.id = o.id; if (o.cls) g.setAttribute('class', o.cls); this.layer(o.layer, o).appendChild(g); return g; }

    _el(tag, attrs, o = {}) {
      const e = document.createElementNS(SVGNS, tag);
      for (const [k, v] of Object.entries(attrs)) if (v != null && v !== false) e.setAttribute(k, v);
      (o.parent || this.layer(o.layer || 'main', o)).appendChild(e);
      return e;
    }
    _style(e, o = {}, def = {}) {
      const stroke = o.stroke ?? o.tone ?? def.stroke, fill = o.fill ?? def.fill, w = lw(o.w ?? def.w);
      e.setAttribute('fill', color(fill ?? 'none'));
      e.setAttribute('stroke', color(stroke ?? 'none'));
      if (stroke && stroke !== 'none') {
        e.setAttribute('stroke-width', w);
        const da = dashArray(o.dash, w); if (da) e.setAttribute('stroke-dasharray', da);
        e.setAttribute('stroke-linecap', o.cap || 'round'); e.setAttribute('stroke-linejoin', 'round');
      }
      if (o.opacity != null) e.setAttribute('opacity', o.opacity);
      if (o.fillOpacity != null) e.setAttribute('fill-opacity', o.fillOpacity);
      if (o.cls) e.setAttribute('class', o.cls);
      if (o.id) e.setAttribute('id', o.id);
      if (o.focal) e.setAttribute('data-focal', '');
      if (o.role) e.setAttribute('data-role', o.role);
      return e;
    }

    /* ---------- shapes (SVG) ---------- */
    path(d, o = {}) { const p = this._style(this._el('path', { d }, o), o, { stroke: 'ink', w: 2 }); this._arrows(p, o); return p; }
    line(x1, y1, x2, y2, o = {}) { return this.path(`M${r2(x1)},${r2(y1)} L${r2(x2)},${r2(y2)}`, o); }
    polyline(points, o = {}) { return this.path(geo.rounded(points, o.radius ?? 0), o); }
    circle(cx, cy, r, o = {}) { return this._style(this._el('circle', { cx: r2(cx), cy: r2(cy), r }, o), o, { fill: 'ink' }); }
    dot(x, y, o = {}) { return this.circle(x, y, o.r ?? 6, { fill: o.fill ?? o.tone ?? 'ink', ...o, stroke: o.stroke ?? null }); }
    rect(x, y, w, h, o = {}) { return this._style(this._el('rect', { x: r2(x), y: r2(y), width: r2(Math.max(0, w)), height: r2(Math.max(0, h)), rx: o.r ?? null }, o), o, { fill: 'ink-5' }); }
    poly(points, o = {}) { return this._style(this._el('polygon', { points: points.map(pt).join(' ') }, o), o, { fill: 'ink-5' }); }
    ring(cx, cy, r0, r1, a0, a1, o = {}) { return this._style(this._el('path', { d: geo.ring(cx, cy, r0, r1, a0, a1), 'fill-rule': 'evenodd' }, o), o, { fill: 'ink-5' }); }
    /** SVG text, only for short labels that must live inside geometry. Prefer label() for anything that wraps. */
    text(x, y, str, o = {}) {
      const t = this._el('text', {
        x: r2(x), y: r2(y), 'text-anchor': o.anchor || 'start', 'dominant-baseline': o.baseline || 'middle',
        'font-family': o.font === 'display' ? 'var(--font-display)' : o.font === 'mono' ? 'var(--font-mono)' : 'var(--font-text)',
        'font-size': o.size || 22, 'font-weight': o.weight || 500, 'letter-spacing': o.tracking || null,
      }, o);
      t.textContent = str; this._style(t, { ...o, stroke: null }, { fill: o.fill ?? o.tone ?? 'ink' });
      return t;
    }
    glyph(name, x, y, o = {}) {
      const size = o.size || 32, g = this._el('g', { transform: `translate(${r2(x - size / 2)},${r2(y - size / 2)}) scale(${size / 24})` }, o);
      const p = document.createElementNS(SVGNS, 'path'); p.setAttribute('d', GLYPHS[name] || GLYPHS.plus); g.appendChild(p);
      this._style(p, { ...o, w: (o.w ?? 1.8) }, { stroke: o.tone || 'ink' }); p.setAttribute('vector-effect', 'non-scaling-stroke');
      g.setAttribute('data-role', 'glyph');
      return g;
    }
    image(src, x, y, w, h, o = {}) {
      const img = document.createElement('img'); img.src = src; img.alt = o.alt || '';
      Object.assign(img.style, { position: 'absolute', left: x + 'px', top: y + 'px', width: w + 'px', height: h + 'px', objectFit: o.fit || 'cover', zIndex: 2 });
      if (o.grayscale) img.style.filter = 'grayscale(1)';
      this.root.appendChild(img); return img;
    }

    /* ---------- text (HTML, wraps, measurable by QA) ---------- */
    /** Place HTML text at (x,y). anchor: tl tc tr ml mc mr bl bc br. w: fixed width (enables wrapping). */
    label(x, y, html, o = {}) {
      const d = document.createElement(o.tag || 'div');
      d.className = `prim-label ${o.cls ?? 'label'}${o.knockout ? ' knockout' : ''}`;
      d.innerHTML = html;
      const [ax, ay] = ANCHORS[o.anchor || 'tl'] || ANCHORS.tl;
      Object.assign(d.style, { left: r2(x) + 'px', top: r2(y) + 'px', transform: `translate(${-ax * 100}%, ${-ay * 100}%)` });
      if (o.w) d.style.width = o.w + 'px'; else d.style.whiteSpace = 'nowrap';
      d.style.textAlign = o.align || (ax === 0.5 ? 'center' : ax === 1 ? 'right' : 'left');
      if (o.color) d.style.color = color(o.color);
      if (o.size) d.style.fontSize = typeof o.size === 'number' ? o.size + 'px' : o.size;
      if (o.weight) d.style.fontWeight = o.weight;
      if (o.style) Object.assign(d.style, o.style);
      if (o.id) d.id = o.id;
      if (o.focal) d.dataset.focal = '';
      if (o.role) d.dataset.role = o.role;
      (o.parent ? this.q(o.parent) : this.root).appendChild(d);
      return d;
    }

    /* ---------- arrows ---------- */
    _arrows(p, o) {
      const a = o.arrow; if (!a || a === 'none') return;
      if (a === 'end' || a === 'both') this._head(p, 'end', o);
      if (a === 'start' || a === 'both') this._head(p, 'start', o);
    }
    _head(p, at, o = {}) {
      const L = p.getTotalLength(); if (!L) return;
      const w = lw(o.w ?? 2), size = o.headSize ?? Math.max(11, w * 4.2);
      const tip = p.getPointAtLength(at === 'end' ? L : 0);
      const back = p.getPointAtLength(at === 'end' ? Math.max(0, L - Math.min(size, L)) : Math.min(L, Math.min(size, L)));
      const ang = Math.atan2(tip.y - back.y, tip.x - back.x), spread = o.headStyle === 'open' ? 0.52 : 0.40;
      const p1 = [tip.x - size * Math.cos(ang - spread), tip.y - size * Math.sin(ang - spread)];
      const p2 = [tip.x - size * Math.cos(ang + spread), tip.y - size * Math.sin(ang + spread)];
      const col = o.stroke ?? o.tone ?? 'ink';
      if (o.headStyle === 'open') this.path(`M${pt(p1)} L${r2(tip.x)},${r2(tip.y)} L${pt(p2)}`, { stroke: col, w, layer: o.layer });
      else this.poly([p1, [tip.x, tip.y], p2], { fill: col, stroke: col, w: 1, layer: o.layer });
    }

    /* ---------- connectors ---------- */
    _side(b, side, at = 0.5, gap = 0) {
      switch (side) {
        case 'right': return [b.r + gap, b.t + b.h * at];
        case 'left': return [b.l - gap, b.t + b.h * at];
        case 'top': return [b.l + b.w * at, b.t - gap];
        case 'bottom': return [b.l + b.w * at, b.b + gap];
        default: return [b.cx, b.cy];
      }
    }
    /**
     * Connect two elements/points. route: straight | elbow | curve | arc.
     * Options: fromSide/toSide (auto|left|right|top|bottom|center), fromAt/toAt (0..1 along side),
     * gap, bend, mid (elbow turn coordinate), radius, arrow (end|start|both|none), tone, w, dash,
     * label, labelAt, labelDx, labelDy, labelCls, labelW, knockout.
     */
    connect(from, to, o = {}) {
      const A = this.box(from, o.pad ?? 0), B = this.box(to, o.pad ?? 0);
      let fs = o.fromSide || 'auto', ts = o.toSide || 'auto';
      if (fs === 'auto' || ts === 'auto') {
        const dx = B.cx - A.cx, dy = B.cy - A.cy;
        const horiz = Math.abs(dx) - (A.w + B.w) / 4 > Math.abs(dy) - (A.h + B.h) / 4;
        if (fs === 'auto') fs = A.point ? 'center' : horiz ? (dx > 0 ? 'right' : 'left') : (dy > 0 ? 'bottom' : 'top');
        if (ts === 'auto') ts = B.point ? 'center' : horiz ? (dx > 0 ? 'left' : 'right') : (dy > 0 ? 'top' : 'bottom');
      }
      const gap = o.gap ?? 10;
      const p0 = this._side(A, fs, o.fromAt ?? 0.5, A.point ? 0 : gap);
      const p1 = this._side(B, ts, o.toAt ?? 0.5, B.point ? 0 : gap);
      const N = { right: [1, 0], left: [-1, 0], top: [0, -1], bottom: [0, 1], center: [0, 0] };
      const n0 = N[fs] || [0, 0], n1 = N[ts] || [0, 0];
      const route = o.route || 'curve';
      let d;
      if (route === 'straight') d = `M${pt(p0)} L${pt(p1)}`;
      else if (route === 'elbow') {
        const H0 = fs === 'left' || fs === 'right', H1 = ts === 'left' || ts === 'right';
        let pts;
        if (H0 && H1) { const mx = o.mid ?? (p0[0] + p1[0]) / 2; pts = [p0, [mx, p0[1]], [mx, p1[1]], p1]; }
        else if (!H0 && !H1) { const my = o.mid ?? (p0[1] + p1[1]) / 2; pts = [p0, [p0[0], my], [p1[0], my], p1]; }
        else if (H0) pts = [p0, [p1[0], p0[1]], p1];
        else pts = [p0, [p0[0], p1[1]], p1];
        d = geo.rounded(pts, o.radius ?? 14);
      } else if (route === 'arc') {
        const m = geo.mid(p0, p1), L = geo.dist(p0, p1), k = (o.bend ?? 0.25) * L;
        const nx = -(p1[1] - p0[1]) / L, ny = (p1[0] - p0[0]) / L;
        d = `M${pt(p0)} Q${r2(m[0] + nx * k)},${r2(m[1] + ny * k)} ${pt(p1)}`;
      } else {
        const L = geo.dist(p0, p1), k = (o.bend ?? 0.45) * L;
        d = `M${pt(p0)} C${r2(p0[0] + n0[0] * k)},${r2(p0[1] + n0[1] * k)} ${r2(p1[0] + n1[0] * k)},${r2(p1[1] + n1[1] * k)} ${pt(p1)}`;
      }
      const path = this.path(d, {
        stroke: o.tone ?? o.stroke ?? 'ink-3', w: o.w ?? 2, dash: o.dash, layer: o.layer, id: o.id, opacity: o.opacity,
        cls: 'prim-line', arrow: o.arrow ?? 'end', headSize: o.headSize, headStyle: o.headStyle, role: o.role || 'connector',
      });
      if (o.dotStart) this.dot(p0[0], p0[1], { r: o.dotR ?? 5, fill: o.tone ?? 'ink-3', layer: o.layer });
      if (o.label) this._pathLabel(path, o.label, o);
      return path;
    }
    _pathLabel(path, html, o) {
      const L = path.getTotalLength(), q = path.getPointAtLength(L * (o.labelAt ?? 0.5));
      return this.label(q.x + (o.labelDx ?? 0), q.y + (o.labelDy ?? 0), html, {
        anchor: o.labelAnchor || 'mc', cls: o.labelCls || 'label-sm', knockout: o.knockout ?? true, w: o.labelW, role: 'connector-label',
      });
    }

    /* ---------- brackets ---------- */
    /** Bracket spanning the union of targets. side: right|left|top|bottom. style: curly|square|line. */
    bracket(targets, o = {}) {
      const U = this.union(targets), side = o.side || 'right', off = o.offset ?? 20, depth = o.depth ?? 18, st = o.style || 'curly';
      let d, tip, anchor;
      if (side === 'right' || side === 'left') {
        const s = side === 'right' ? 1 : -1, x = side === 'right' ? U.r + off : U.l - off;
        d = st === 'curly' ? geo.brace(x, U.t, U.b, depth, side)
          : st === 'square' ? `M${x},${U.t} h${s * depth / 2} V${U.b} h${-s * depth / 2} M${x + s * depth / 2},${U.cy} h${s * depth / 2}`
          : `M${x + s * depth / 2},${U.t} V${U.b}`;
        tip = [x + s * depth, U.cy]; anchor = side === 'right' ? 'ml' : 'mr';
      } else {
        const s = side === 'bottom' ? 1 : -1, y = side === 'bottom' ? U.b + off : U.t - off;
        d = st === 'curly' ? geo.braceH(U.l, U.r, y, depth, side === 'bottom' ? 'down' : 'up')
          : st === 'square' ? `M${U.l},${y} v${s * depth / 2} H${U.r} v${-s * depth / 2} M${U.cx},${y + s * depth / 2} v${s * depth / 2}`
          : `M${U.l},${y + s * depth / 2} H${U.r}`;
        tip = [U.cx, y + s * depth]; anchor = side === 'bottom' ? 'tc' : 'bc';
      }
      const p = this.path(d, { stroke: o.tone ?? 'ink-3', w: o.w ?? 2, layer: o.layer, role: 'bracket' });
      if (o.label) {
        const g = o.labelGap ?? 14, dx = side === 'right' ? g : side === 'left' ? -g : 0, dy = side === 'bottom' ? g : side === 'top' ? -g : 0;
        this.label(tip[0] + dx, tip[1] + dy, o.label, { anchor, w: o.labelW, cls: o.labelCls || 'annotation', role: 'bracket-label' });
      }
      return p;
    }

    /* ---------- callouts ---------- */
    /** Annotation text at `at` with a leader line to `target` (element or [x,y]). */
    callout(o) {
      const T = this.box(o.target), tp = o.targetSide ? this._side(T, o.targetSide, o.targetAt ?? 0.5, 0) : [T.cx, T.cy];
      const lab = this.label(o.at[0], o.at[1], o.text, { anchor: o.anchor || 'tl', w: o.w, cls: o.cls || 'annotation', role: 'callout', id: o.id, focal: o.focal });
      if (o.leader === false) return lab;
      const LB = this.box(lab), g = o.gap ?? 10;
      const sx = Math.max(LB.l - g, Math.min(tp[0], LB.r + g)), sy = Math.max(LB.t - g, Math.min(tp[1], LB.b + g));
      let start = [sx, sy];
      if (tp[0] > LB.l && tp[0] < LB.r) start = [tp[0], tp[1] < LB.t ? LB.t - g : LB.b + g];
      else if (tp[1] > LB.t && tp[1] < LB.b) start = [tp[0] < LB.l ? LB.l - g : LB.r + g, tp[1]];
      const pts = o.elbow ? [start, [tp[0], start[1]], tp] : [start, tp];
      this.polyline(pts, { stroke: o.tone ?? 'ink-3', w: o.lw ?? 1.5, radius: 8, layer: o.layer, role: 'leader' });
      if (o.dot !== false) this.dot(tp[0], tp[1], { r: o.dotR ?? 5, fill: o.tone ?? 'ink', layer: o.layer });
      return lab;
    }

    /* ---------- charts ---------- */
    chart(area) { return new Chart(this, area); }
  }

  /* ========================================================================
     Chart kit: scales + marks. Compose; do not expect a finished chart.
     ======================================================================== */
  const niceTicks = (a, b, n = 5) => {
    const span = b - a, step0 = Math.pow(10, Math.floor(Math.log10(span / n))), err = span / n / step0;
    const step = step0 * (err >= 7.5 ? 10 : err >= 3.5 ? 5 : err >= 1.5 ? 2 : 1);
    const out = []; for (let v = Math.ceil(a / step) * step; v <= b + 1e-9; v += step) out.push(+v.toFixed(10)); return out;
  };
  class Chart {
    constructor(s, { x, y, w, h }) { this.s = s; this.x = x; this.y = y; this.w = w; this.h = h; this.r = x + w; this.b = y + h; }
    /** Linear scale. axis 'y' maps domain to [bottom, top]; 'x' to [left, right]. */
    linear(domain, o = {}) {
      const [d0, d1] = domain, [r0, r1] = o.range || (o.axis === 'x' ? [this.x, this.r] : [this.b, this.y]);
      const f = (v) => r0 + (v - d0) / (d1 - d0) * (r1 - r0);
      f.domain = domain; f.range = [r0, r1]; f.ticks = (n) => niceTicks(d0, d1, n); f.px = (dv) => Math.abs(dv / (d1 - d0) * (r1 - r0));
      return f;
    }
    /** Band scale: f(key) = band start, f.bw = bandwidth, f.center(key). */
    band(keys, o = {}) {
      const [r0, r1] = o.range || (o.axis === 'y' ? [this.y, this.b] : [this.x, this.r]);
      const pad = o.padding ?? 0.3, outer = o.outer ?? 0.1, n = keys.length;
      const step = (r1 - r0) / (n - pad + 2 * outer), bw = step * (1 - pad);
      const f = (k) => r0 + step * outer + keys.indexOf(k) * step;
      f.bw = bw; f.step = step; f.keys = keys; f.center = (k) => f(k) + bw / 2;
      return f;
    }
    gridY(y, ticks, o = {}) { for (const t of ticks) this.s.line(this.x, y(t), this.r, y(t), { stroke: o.tone ?? 'rule', w: o.w ?? 1, dash: o.dash, layer: o.layer, role: 'grid' }); }
    gridX(x, ticks, o = {}) { for (const t of ticks) this.s.line(x(t), this.y, x(t), this.b, { stroke: o.tone ?? 'rule', w: o.w ?? 1, dash: o.dash, layer: o.layer, role: 'grid' }); }
    axisX(x, o = {}) {
      const y = o.y ?? this.b;
      if (o.line !== false) this.s.line(this.x, y, this.r, y, { stroke: o.tone ?? 'ink-4', w: o.w ?? 1.5, role: 'axis' });
      const keys = o.keys || x.keys || o.ticks || [];
      for (const k of keys) {
        const cx = x.center ? x.center(k) : x(k);
        this.s.label(cx, y + (o.offset ?? 14), o.format ? o.format(k) : k, { anchor: 'tc', cls: o.cls || 'label-sm', w: o.labelW, role: 'axis-label' });
      }
    }
    axisY(y, ticks, o = {}) {
      const x = o.x ?? this.x;
      if (o.line) this.s.line(x, this.y, x, this.b, { stroke: o.tone ?? 'ink-4', w: 1.5, role: 'axis' });
      for (const t of ticks) this.s.label(x - (o.offset ?? 14), y(t), o.format ? o.format(t) : t, { anchor: 'mr', cls: o.cls || 'label-sm', role: 'axis-label' });
    }
    /** Bars. orient 'v' (x=band, y=linear) or 'h' (y=band, x=linear). tone may be a function(d). */
    bars(data, o) {
      const tone = (d) => (typeof o.tone === 'function' ? o.tone(d) : o.tone ?? 'ink-4');
      return data.map((d) => {
        const k = o.key(d), v = o.value(d), base = o.base ? o.base(d) : 0;
        let e;
        if (o.orient === 'h') {
          const y = o.y(k), x0 = o.x(Math.min(base, base + v)), x1 = o.x(Math.max(base, base + v));
          e = this.s.rect(x0, y, x1 - x0, o.y.bw, { fill: tone(d), r: o.r, role: 'bar', focal: o.focal?.(d) });
          if (o.label) this.s.label(x1 + 12, y + o.y.bw / 2, o.label(d), { anchor: 'ml', cls: o.labelCls || 'label', role: 'value-label' });
        } else {
          const x = o.x(k), y0 = o.y(Math.max(base, base + v)), y1 = o.y(Math.min(base, base + v));
          e = this.s.rect(x, y0, o.x.bw, y1 - y0, { fill: tone(d), r: o.r, role: 'bar', focal: o.focal?.(d) });
          if (o.label) this.s.label(x + o.x.bw / 2, y0 - 10, o.label(d), { anchor: 'bc', cls: o.labelCls || 'label', role: 'value-label' });
        }
        return e;
      });
    }
    line(data, o) {
      const pts = data.map((d) => [o.x(d), o.y(d)]);
      const p = this.s.polyline(pts, { stroke: o.tone ?? 'ink', w: o.w ?? 3, dash: o.dash, radius: o.radius ?? 0, role: 'series' });
      if (o.dots) pts.forEach((q) => this.s.dot(q[0], q[1], { r: o.dotR ?? 6, fill: o.tone ?? 'ink' }));
      return { path: p, points: pts };
    }
    area(data, o) {
      const top = data.map((d) => [o.x(d), o.y(d)]), bot = data.map((d) => [o.x(d), o.y0 ? o.y0(d) : this.b]).reverse();
      return this.s.poly([...top, ...bot], { fill: o.tone ?? 'accent-soft', opacity: o.opacity, role: 'area' });
    }
    /**
     * Waterfall / bridge. steps: [{k, v, total?:true, tone?, label?}]. Totals are drawn from 0;
     * deltas float from the running total. Returns [{k, x, y0, y1, top, bottom, el}] for annotation.
     */
    waterfall(steps, o) {
      let run = 0; const out = [];
      for (const st of steps) {
        const from = st.total ? 0 : run, to = st.total ? (st.v ?? run) : run + st.v;
        const top = Math.max(from, to), bottom = Math.min(from, to);
        const x = o.x(st.k), yt = o.y(top), yb = o.y(bottom);
        const tone = st.tone ?? (st.total ? (o.totalTone ?? 'ink') : st.v < 0 ? (o.negTone ?? 'ink-4') : (o.posTone ?? 'ink-4'));
        const el = st.outline   // potential / paper value: outline, not solid ink
          ? this.s.rect(x + 1, yt + 1, o.x.bw - 2, Math.max(1, yb - yt) - 2, { fill: st.outlineFill ?? 'bg', stroke: tone, w: st.outlineW ?? 2, role: 'total-bar', focal: st.focal })
          : this.s.rect(x, yt, o.x.bw, Math.max(1, yb - yt), { fill: tone, fillOpacity: st.opacity, role: st.total ? 'total-bar' : 'delta-bar', focal: st.focal });
        out.push({ k: st.k, x, cx: x + o.x.bw / 2, w: o.x.bw, top: yt, bottom: yb, from, to, el, step: st });
        run = to;
      }
      if (o.connectors !== false) {
        for (let i = 0; i < out.length - 1; i++) {
          const a = out[i], b = out[i + 1], yv = o.y(a.to);
          this.s.line(a.x + a.w, yv, b.x, yv, { stroke: o.connectorTone ?? 'ink-4', w: 1, dash: o.connectorDash ?? null, role: 'bridge' }); // solid: dashes mean target/future
        }
      }
      return out;
    }
    refLine(v, scale, o = {}) {
      const horiz = o.orient !== 'v', c = scale(v);
      const p = horiz ? this.s.line(this.x, c, this.r, c, { stroke: o.tone ?? 'ink-3', w: o.w ?? 1.5, dash: o.dash ?? 'dash', role: 'ref' })
        : this.s.line(c, this.y, c, this.b, { stroke: o.tone ?? 'ink-3', w: o.w ?? 1.5, dash: o.dash ?? 'dash', role: 'ref' });
      if (o.label) horiz ? this.s.label(this.r, c - 8, o.label, { anchor: 'br', cls: o.cls || 'label-sm' }) : this.s.label(c + 8, this.y, o.label, { anchor: 'tl', cls: o.cls || 'label-sm' });
      return p;
    }
    annotate(x, y, text, o = {}) { return this.s.callout({ target: [x, y], at: [x + (o.dx ?? 40), y + (o.dy ?? -60)], text, ...o }); }
  }

  /* ========================================================================
     Declarative primitives: <x-connect>, <x-bracket>, <x-callout>
     ======================================================================== */
  const camel = (s) => s.replace(/-([a-z])/g, (_, c) => c.toUpperCase());
  const parseVal = (v) => (v === '' ? true : v === 'true' ? true : v === 'false' ? false : /^-?\d+(\.\d+)?$/.test(v) ? parseFloat(v) : v);
  const parseTarget = (v) => { const m = /^(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)$/.exec(String(v).trim()); return m ? [parseFloat(m[1]), parseFloat(m[2])] : v; };
  const attrs = (n, skip = []) => Object.fromEntries([...n.attributes].filter((a) => !skip.includes(a.name)).map((a) => [camel(a.name), parseVal(a.value)]));
  function declarative(s) {
    s.qa('x-connect').forEach((n) => { const a = attrs(n, ['from', 'to']); if (n.innerHTML.trim() && !a.label) a.label = n.innerHTML.trim(); s.connect(parseTarget(n.getAttribute('from')), parseTarget(n.getAttribute('to')), a); });
    s.qa('x-bracket').forEach((n) => { const a = attrs(n, ['targets']); if (n.innerHTML.trim() && !a.label) a.label = n.innerHTML.trim(); s.bracket(n.getAttribute('targets'), a); });
    s.qa('x-callout').forEach((n) => { const a = attrs(n, ['target', 'at']); s.callout({ ...a, target: parseTarget(n.getAttribute('target')), at: parseTarget(n.getAttribute('at')), text: n.innerHTML.trim() }); });
  }

  /* ========================================================================
     Lifecycle
     ======================================================================== */
  const queue = [];
  function fit() {
    const roots = document.querySelectorAll('.slide[data-slide]');
    if (roots.length !== 1 || document.documentElement.dataset.mode === 'deck') return;
    const root = roots[0], s = Math.min(innerWidth / 1920, innerHeight / 1080);
    Object.assign(root.style, { position: 'absolute', left: `${(innerWidth - 1920 * s) / 2}px`, top: `${(innerHeight - 1080 * s) / 2}px`, transform: s === 1 ? '' : `scale(${s})` });
  }
  async function loadFonts() {
    const cs = getComputedStyle(document.documentElement), jobs = [];
    const fams = ['--font-display', '--font-text', '--font-mono'].map((v) => cs.getPropertyValue(v).split(',')[0].trim()).filter(Boolean);
    for (const f of new Set(fams)) for (const w of [300, 400, 500, 600, 700, 800]) for (const st of ['normal', 'italic']) jobs.push(document.fonts.load(`${st} ${w} 24px ${f}`).catch(() => {}));
    await Promise.all(jobs); await document.fonts.ready;
  }
  const frame = () => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
  async function boot() {
    fit(); addEventListener('resize', fit);
    try { await Promise.race([loadFonts(), new Promise((r) => setTimeout(r, 8000))]); } catch (e) { report(e); }
    await frame();
    const roots = [...document.querySelectorAll('.slide[data-slide]')];
    for (const root of roots) {
      const s = new Slide(root);
      for (const job of queue) {
        if (job.id ? job.id !== s.id : roots.length > 1) continue;
        try { await job.fn(s, P); } catch (e) { report(e, s.id); }
      }
      try { declarative(s); } catch (e) { report(e, s.id); }
      const pg = root.querySelector('.footer .page'); if (pg && !pg.textContent.trim() && root.dataset.page) pg.textContent = root.dataset.page;
    }
    await frame();
    document.documentElement.dataset.ready = '1';
    global.__slideReady = true;
    document.dispatchEvent(new CustomEvent('slides:ready'));
  }

  const P = {
    /** Register drawing code for a slide id (or a function alone in single-slide files). */
    draw(id, fn) { if (typeof id === 'function') { fn = id; id = null; } queue.push({ id, fn }); },
    geo, grid, fmt, color, niceTicks, GLYPHS, Slide, version: '1.0.0',
  };
  global.P = P;
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})(window);
