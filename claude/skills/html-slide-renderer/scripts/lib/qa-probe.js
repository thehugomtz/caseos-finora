/* In-page QA probe. Injected by render.mjs after window.__slideReady.
   window.__qaProbe() -> { slides: [ { id, composition, family, headline, metrics, issues[] } ], drawErrors }
   Levels: error = must fix before shipping · warn = critic must look · info = context.
   The probe measures; it does not judge taste. The critic (a model looking at the render) does. */
(function () {
  'use strict';
  const W = 1920, H = 1080;

  /* ---------- color ---------- */
  function parseColor(s) {
    if (!s || s === 'none' || s === 'transparent') return null;
    let m = s.match(/rgba?\(([^)]+)\)/);
    if (m) {
      const p = m[1].split(/[\s,/]+/).filter(Boolean).map((v) => (v.endsWith('%') ? parseFloat(v) / 100 : parseFloat(v)));
      return [p[0], p[1], p[2], p[3] == null ? 1 : p[3]];
    }
    m = s.match(/color\(srgb ([^)]+)\)/);
    if (m) { const p = m[1].split(/[\s/]+/).filter(Boolean).map(parseFloat); return [p[0] * 255, p[1] * 255, p[2] * 255, p[3] == null ? 1 : p[3]]; }
    return null;
  }
  const lin = (c) => { c /= 255; return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); };
  const lum = (c) => 0.2126 * lin(c[0]) + 0.7152 * lin(c[1]) + 0.0722 * lin(c[2]);
  const ratio = (a, b) => { const A = lum(a), B = lum(b); return (Math.max(A, B) + 0.05) / (Math.min(A, B) + 0.05); };
  const over = (fg, bg) => { const a = fg[3] ?? 1; return [fg[0] * a + bg[0] * (1 - a), fg[1] * a + bg[1] * (1 - a), fg[2] * a + bg[2] * (1 - a), 1]; };
  const hex = (c) => '#' + c.slice(0, 3).map((v) => Math.round(v).toString(16).padStart(2, '0')).join('');
  const sat = (c) => { const mx = Math.max(...c.slice(0, 3)), mn = Math.min(...c.slice(0, 3)); return mx === 0 ? 0 : (mx - mn) / mx; };
  const near = (a, b, tol = 10) => a && b && Math.abs(a[0] - b[0]) <= tol && Math.abs(a[1] - b[1]) <= tol && Math.abs(a[2] - b[2]) <= tol;
  const EMOJI = /\p{Extended_Pictographic}/u;
  const SHAPES = new Set(['rect', 'circle', 'ellipse', 'path', 'polygon', 'polyline', 'line']);

  function countLines(rects) {
    const rs = rects.filter((r) => r.width > 2 && r.height > 2).sort((a, b) => a.top - b.top), lines = [];
    for (const r of rs) {
      const c = r.top + r.height / 2, hit = lines.find((l) => c >= l.top && c <= l.bottom);
      if (hit) { hit.top = Math.min(hit.top, r.top); hit.bottom = Math.max(hit.bottom, r.bottom); } else lines.push({ top: r.top, bottom: r.bottom });
    }
    return lines.length;
  }

  function probeSlide(root) {
    const R = root.getBoundingClientRect(), scale = R.width / root.offsetWidth || 1;
    const rel = (r) => ({ x: (r.left - R.left) / scale, y: (r.top - R.top) / scale, w: r.width / scale, h: r.height / scale });
    const issues = [];
    const add = (level, code, msg, extra = {}) => issues.push({ level, code, msg, ...extra });
    const cs = (e) => getComputedStyle(e);
    const rootCS = cs(root);
    const bgRoot = parseColor(rootCS.backgroundColor) || [255, 255, 255, 1];
    const accent = parseColor(`rgb(${hexToRgb(rootCS.getPropertyValue('--accent'))})`);
    const snip = (t) => t.replace(/\s+/g, ' ').trim().slice(0, 70);
    const visible = (e) => (e.checkVisibility ? e.checkVisibility({ opacityProperty: true, visibilityProperty: true }) : true);
    const isAllowed = (e, what) => !!e.closest(`[data-qa-allow~="${what}"]`);

    /* ---------- 1. collect text ---------- */
    const owners = new Map();
    const tw = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, { acceptNode: (n) => (n.nodeValue.trim() ? 1 : 2) });
    while (tw.nextNode()) {
      const n = tw.currentNode, el = n.parentElement;
      if (!el || el.closest('script,style,.notes,[data-qa-ignore],x-connect,x-bracket,x-callout,template')) continue;
      if (!visible(el)) continue;
      const range = document.createRange(); range.selectNodeContents(n);
      const client = [...range.getClientRects()].filter((r) => r.width > 0.5 && r.height > 0.5);
      if (!client.length) continue;
      const owner = el.closest('text') || el;
      const o = owners.get(owner) || { el: owner, rects: [], client: [], text: '' };
      o.rects.push(...client.map(rel)); o.client.push(...client); o.text += ' ' + n.nodeValue;
      owners.set(owner, o);
    }
    const list = [...owners.values()];
    const inFooter = (e) => !!e.closest('.footer, .source, [data-role="source"]');
    for (const o of list) {
      const s = cs(o.el);
      o.isSvg = o.el instanceof SVGElement;
      let fs = parseFloat(s.fontSize);
      if (o.isSvg && o.el.getScreenCTM) { const m = o.el.getScreenCTM(); if (m) fs = fs * Math.hypot(m.a, m.b) / scale; }
      o.fs = fs; o.weight = parseInt(s.fontWeight, 10) || 400; o.family = s.fontFamily.split(',')[0].replace(/["']/g, '').trim();
      o.color = parseColor(o.isSvg ? s.fill : s.color);
      o.words = o.text.split(/\s+/).filter((w) => /[\p{L}\p{N}]/u.test(w)).length;
      o.footer = inFooter(o.el);
      o.box = rel(o.el.getBoundingClientRect());
    }
    const body = list.filter((o) => !o.footer);

    /* ---------- 2. canvas bounds + clipping + overflow ---------- */
    for (const o of list) for (const r of o.rects) {
      if (r.x < -1 || r.y < -1 || r.x + r.w > W + 1 || r.y + r.h > H + 1) { add('error', 'text-offcanvas', `Text outside the 1920x1080 canvas: "${snip(o.text)}"`, { box: r }); break; }
    }
    const blocks = new Set();
    for (const o of list) { let b = o.el; while (b !== root && !o.isSvg && cs(b).display.startsWith('inline')) b = b.parentElement; blocks.add(b); }
    for (const b of blocks) {
      if (b instanceof SVGElement || b === root) continue;
      const s = cs(b), dy = b.scrollHeight - b.clientHeight, dx = b.scrollWidth - b.clientWidth;
      const clips = /hidden|clip|auto|scroll/.test(s.overflow + s.overflowX + s.overflowY);
      if (s.textOverflow === 'ellipsis' && dx > 1) add('error', 'text-truncated', `Text truncated with ellipsis: "${snip(b.textContent)}"`);
      else if (clips && (dy > 2 || dx > 2)) add('error', 'text-clipped', `Text clipped by its container (${Math.max(dx, dy)}px hidden): "${snip(b.textContent)}"`);
      // auto-height boxes grow with their text, so any vertical excess means a fixed height (inline OR CSS) is too small
      // threshold relative to type size: tight line-height on display numbers (0.9) is intentional, not a spill
      else if (!clips && dy > Math.max(4, 0.35 * parseFloat(s.fontSize))) add('warn', 'text-spill', `Text spills ${dy}px below its fixed-height box: "${snip(b.textContent)}"`);
    }

    /* ---------- 3. text-on-text overlap ---------- */
    const shrink = (r) => ({ x: r.x, y: r.y + r.h * 0.18, w: r.w, h: r.h * 0.64 });
    const inter = (a, b) => Math.max(0, Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x)) * Math.max(0, Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y));
    const overlaps = [];
    for (let i = 0; i < list.length; i++) for (let j = i + 1; j < list.length; j++) {
      const A = list[i], B = list[j];
      if (A.el.contains(B.el) || B.el.contains(A.el)) continue;
      let hit = false;
      for (const ra of A.rects) { for (const rb of B.rects) { const a = shrink(ra), b = shrink(rb), x = inter(a, b); if (x > 30 && x > 0.15 * Math.min(a.w * a.h, b.w * b.h)) { hit = true; break; } } if (hit) break; }
      if (hit) overlaps.push(`"${snip(A.text).slice(0, 30)}" × "${snip(B.text).slice(0, 30)}"`);
    }
    overlaps.slice(0, 8).forEach((m) => add('error', 'text-overlap', `Text overlaps text: ${m}`));

    /* ---------- 4. legibility: size + contrast ---------- */
    const style = document.createElement('style'); style.textContent = '*{pointer-events:auto!important}'; document.head.appendChild(style);
    for (const o of list) {
      const min = o.footer ? 15 : 18;
      if (o.fs < min - 0.5) add(o.fs < 14 ? 'error' : 'warn', 'font-too-small', `${o.fs.toFixed(1)}px text (min ${min}px): "${snip(o.text)}"`);
      if (!o.color) continue;
      const c = o.client[0], x = c.left + c.width / 2, y = c.top + c.height / 2;
      let bg = null, unknown = false; const stack = [];
      for (const e of document.elementsFromPoint(x, y)) {
        if (e === o.el || o.el.contains(e)) continue;
        if (!root.contains(e) && e !== root) continue;
        const s = cs(e);
        if (e instanceof SVGElement) {
          if (!SHAPES.has(e.tagName)) continue;
          const f = parseColor(s.fill); if (!f || s.fill.startsWith('url')) continue;
          const a = (parseFloat(s.fillOpacity) || 1) * (parseFloat(s.opacity) || 1); stack.push([f[0], f[1], f[2], f[3] * a]);
        } else {
          if (e !== root && s.backgroundImage !== 'none' && !e.classList.contains('hl')) { unknown = true; break; }
          const f = parseColor(s.backgroundColor); if (f && f[3] > 0) stack.push([f[0], f[1], f[2], f[3] * (parseFloat(s.opacity) || 1)]);
        }
        if (stack.length && stack[stack.length - 1][3] >= 0.99) break;
        if (e === root) break;
      }
      if (unknown) { add('info', 'contrast-unknown', `Text over image/gradient, check contrast by eye: "${snip(o.text)}"`); continue; }
      bg = bgRoot; for (let k = stack.length - 1; k >= 0; k--) bg = over(stack[k], bg);
      const fg = over(o.color, bg), r = ratio(fg, bg), large = o.fs >= 36 || (o.fs >= 28 && o.weight >= 600);
      o.contrast = r;
      const need = large ? 3 : 4.5;
      if (r < need) add(r < need - 1.2 ? 'error' : 'warn', 'low-contrast', `Contrast ${r.toFixed(2)}:1 (needs ${need}) for "${snip(o.text)}" (${hex(fg)} on ${hex(bg)})`);
    }
    style.remove();

    /* ---------- 5. words + density ---------- */
    const words = body.reduce((a, o) => a + o.words, 0), wordsFooter = list.filter((o) => o.footer).reduce((a, o) => a + o.words, 0);
    const budget = +root.dataset.wordBudget || 90;
    if (words > budget * 1.5) add('error', 'too-many-words', `${words} words on canvas (budget ${budget}). Synthesize; move detail to speaker notes.`);
    else if (words > budget) add('warn', 'too-many-words', `${words} words on canvas (budget ${budget}).`);
    const blockWords = [...blocks].filter((b) => !(b instanceof SVGElement) && !inFooter(b)).map((b) => ({ b, w: b.textContent.split(/\s+/).filter((w) => /[\p{L}\p{N}]/u.test(w)).length }));
    const maxBlock = Math.max(0, ...blockWords.map((x) => x.w));
    blockWords.filter((x) => x.w > 45 && !x.b.querySelector('*:not(b):not(strong):not(em):not(i):not(span):not(br)')).slice(0, 3)
      .forEach((x) => add('warn', 'long-paragraph', `Paragraph of ${x.w} words — belongs in notes or needs synthesis: "${snip(x.b.textContent)}"`));
    const sizes = [...new Set(list.filter((o) => !o.el.closest('.unit')).map((o) => Math.round(o.fs)))].sort((a, b) => b - a);   // units are part of their number
    if (sizes.length > 7) add('warn', 'type-scale', `${sizes.length} distinct font sizes (${sizes.join(', ')}). Use the type scale.`);
    const families = [...new Set(list.map((o) => o.family))];
    if (families.length > 3) add('warn', 'font-families', `${families.length} font families: ${families.join(', ')}`);
    const textArea = list.reduce((a, o) => a + o.rects.reduce((s, r) => s + r.w * r.h, 0), 0) / (W * H) * 100;

    // hero numbers never wrap ("$910" / "M")
    for (const m of root.querySelectorAll('.metric')) {
      if (!visible(m)) continue;
      const rg = document.createRange(); rg.selectNodeContents(m);
      const lines = countLines([...rg.getClientRects()]);
      if (lines > 1) add('error', 'metric-wraps', `Hero number wraps onto ${lines} lines: "${snip(m.textContent)}". Give it room or white-space: nowrap.`);
    }

    /* ---------- 6. headline ---------- */
    const heads = [...root.querySelectorAll('.headline, .statement')].filter(visible);
    let headline = '', headLines = 0, headWords = 0;
    if (!heads.length) add('warn', 'no-headline', 'No .headline/.statement: every slide states its conclusion.');
    else {
      const h = heads[0]; headline = snip(h.textContent);
      const range = document.createRange(); range.selectNodeContents(h);
      headLines = countLines([...range.getClientRects()]);
      headWords = h.textContent.split(/\s+/).filter(Boolean).length;
      if (heads.filter((e) => e.classList.contains('headline')).length > 1) add('warn', 'multiple-headlines', 'More than one .headline: one idea per slide.');
      if (h.classList.contains('headline') && headLines > 2) add('warn', 'headline-long', `Headline wraps to ${headLines} lines (${headWords} words). Aim for ≤2 lines.`);
      if (headWords <= 4 && h.classList.contains('headline')) add('info', 'headline-topic', `Headline has ${headWords} words: is it a conclusion or a topic label?`);
    }

    /* ---------- 7. slop smells ---------- */
    const all = [...root.querySelectorAll('*')].filter((e) => e !== root && visible(e) && !e.closest('.notes,.footer,x-connect,x-bracket,x-callout'));
    let gradients = 0, shadows = 0, borders = 0, rounded = 0, icons = 0, emoji = 0;
    const surfaces = [];
    for (const e of all) {
      const s = cs(e), r = rel(e.getBoundingClientRect()), area = r.w * r.h;
      if (e instanceof SVGElement) {
        if ((e.getAttribute('fill') || '').startsWith('url') || (e.getAttribute('stroke') || '').startsWith('url')) gradients++;
        if (s.filter && s.filter !== 'none' && /drop-shadow/.test(s.filter)) shadows++;
        if (e.tagName === 'svg' && !e.classList.contains('layer') && r.w <= 80 && r.h <= 80 && !e.querySelector('text')) icons++;
        if (e.dataset && e.dataset.role === 'glyph') icons++;
        const closed = e.tagName === 'rect' || e.tagName === 'polygon' || (e.tagName === 'path' && /z\s*$/i.test(e.getAttribute('d') || ''));
        if (closed && area > 0.008 * W * H) {
          const f = parseColor(s.fill), hasFill = f && f[3] > 0 && !near(f, bgRoot, 3);
          if (hasFill && !['bar', 'total-bar', 'delta-bar', 'area'].includes(e.dataset.role)) surfaces.push({ e, r, svg: true, radius: +(e.getAttribute('rx') || 0) });
        }
        continue;
      }
      if (s.backgroundImage.includes('gradient') && !e.classList.contains('hl') && !isAllowed(e, 'gradient')) gradients++;
      if (s.boxShadow !== 'none' || /drop-shadow/.test(s.filter)) shadows++;
      const bw = ['Top', 'Right', 'Bottom', 'Left'].filter((k) => parseFloat(s[`border${k}Width`]) > 0 && (parseColor(s[`border${k}Color`]) || [0, 0, 0, 0])[3] > 0).length;
      if (bw) borders++;
      const bgc = parseColor(s.backgroundColor), filled = bgc && bgc[3] > 0.02 && !near(bgc, bgRoot, 3);
      const rad = parseFloat(s.borderTopLeftRadius) || 0;
      if (rad >= 12 && (filled || bw)) rounded++;
      if (e.tagName === 'IMG' && r.w <= 80 && r.h <= 80) icons++;
      if (/icon/i.test(e.className && e.className.baseVal === undefined ? e.className : '')) icons++;
      if ((filled || bw >= 3 || s.boxShadow !== 'none') && area > 0.008 * W * H && e.textContent.trim().split(/\s+/).length >= 3) surfaces.push({ e, r, svg: false, radius: rad });
    }
    for (const o of list) if (EMOJI.test(o.text)) emoji++;
    if (emoji) add('error', 'emoji', `${emoji} text blocks contain emoji. Executive slides encode meaning with position, scale and line — not emoji.`);
    if (gradients) add('warn', 'gradient', `${gradients} gradient fills. Gradients must encode data, not decorate.`);
    if (shadows) add('warn', 'shadow', `${shadows} shadows. Consulting slides separate with space and hairlines, not drop shadows.`);
    if (borders > 10) add('warn', 'border-inflation', `${borders} bordered elements. Can whitespace or alignment replace the boxes?`);
    if (rounded > 3) add('warn', 'rounded-boxes', `${rounded} rounded filled/bordered boxes: SaaS-dashboard language, not storytelling.`);
    if (icons > 3) add('warn', 'icons', `${icons} icon-like elements. Keep only icons that encode information.`);

    // bullets
    const lis = [...root.querySelectorAll('li')].filter(visible).length;
    const glyphBullets = [...blocks].filter((b) => b !== root && /^\s*[•·▪◦‣–-]\s/.test(b.textContent)).length;
    const bullets = lis + glyphBullets;
    if (bullets >= 4) add('warn', 'bullets', `${bullets} bullet items. Is there an order, hierarchy, flow or tension that should be drawn instead?`);

    // card grids: >=3 similar-size surfaces holding text, arranged as a row or a dense grid
    const centerIn = (o, r) => { const cx = o.box.x + o.box.w / 2, cy = o.box.y + o.box.h / 2; return cx > r.x && cx < r.x + r.w && cy > r.y && cy < r.y + r.h; };
    const cards = surfaces.filter((sf) => !sf.svg || list.reduce((a, o) => a + (centerIn(o, sf.r) ? o.words : 0), 0) >= 3);
    const clusterN = (vals, tol) => { const v = [...vals].sort((a, b) => a - b), c = []; for (const x of v) if (!c.length || x - c[c.length - 1] > tol) c.push(x); return c.length; };
    const cardGroups = [], used = new Set();
    for (let i = 0; i < cards.length; i++) {
      if (used.has(i)) continue;
      const a = cards[i], grp = [i];
      for (let j = i + 1; j < cards.length; j++) {
        if (used.has(j)) continue;
        const b = cards[j];
        if (a.e.contains(b.e) || b.e.contains(a.e)) continue;
        const simW = Math.abs(a.r.w - b.r.w) / Math.max(a.r.w, b.r.w) < 0.12, simH = Math.abs(a.r.h - b.r.h) / Math.max(a.r.h, b.r.h) < 0.12;
        if (simW && simH) grp.push(j);
      }
      if (grp.length < 3) continue;
      const g = grp.map((k) => cards[k]), rows = clusterN(g.map((c) => c.r.y), 16), cols = clusterN(g.map((c) => c.r.x), 16);
      const kind = rows === 1 && cols >= 3 ? 'row' : rows >= 2 && cols >= 2 && rows * cols <= g.length * 1.5 ? 'grid' : cols === 1 && rows >= 3 ? 'stack' : null;
      if (!kind) continue;
      grp.forEach((k) => used.add(k));
      cardGroups.push({ kind, count: g.length, allowed: g.every((c) => isAllowed(c.e, 'card-grid')), w: Math.round(a.r.w), h: Math.round(a.r.h) });
    }
    for (const g of cardGroups) {
      if (g.allowed) add('info', 'card-grid-allowed', `Card ${g.kind} of ${g.count} (${g.w}×${g.h}) explicitly allowed via data-qa-allow="card-grid".`);
      else if (g.kind === 'stack') add('warn', 'box-stack', `Vertical stack of ${g.count} identical text boxes (${g.w}×${g.h}). A layered architecture must show how layers relate; otherwise it is a list in boxes.`);
      else add('error', 'card-grid', `Card ${g.kind}: ${g.count} near-identical text boxes (${g.w}×${g.h}). Cards are a fallback, not a composition — is there an order, hierarchy, flow, magnitude or tension to draw?`);
    }

    /* ---------- 8. accent discipline ---------- */
    let accentUses = 0;
    if (accent) {
      for (const o of list) if (near(o.color, accent, 12)) accentUses++;
      for (const e of root.querySelectorAll('svg *')) {
        if (!SHAPES.has(e.tagName) || !visible(e)) continue;
        const s = cs(e); if (near(parseColor(s.fill), accent, 12) || near(parseColor(s.stroke), accent, 12)) accentUses++;
      }
      if (accentUses > 14) add('warn', 'accent-diluted', `Accent color used on ${accentUses} elements. The accent marks the insight; when everything is accented nothing is.`);
      if (accentUses === 0) add('info', 'accent-unused', 'Accent unused: is the focal point carried by scale/position alone? (fine if yes)');
    }

    /* ---------- 9. focal point ---------- */
    const focalEls = [...root.querySelectorAll('[data-focal]')].filter(visible);
    let focal = null;
    if (!focalEls.length) add('warn', 'no-focal', 'No element marked data-focal. Declare the focal point the eye must land on in <3s.');
    else {
      const f = focalEls[0], fr = rel(f.getBoundingClientRect());
      const fo = list.filter((o) => f === o.el || f.contains(o.el));
      const maxBody = Math.max(0, ...body.filter((o) => !o.el.closest('.headline,.statement,.kicker')).map((o) => o.fs));
      const fFs = Math.max(0, ...fo.map((o) => o.fs));
      const fs = cs(f), fc = parseColor(f instanceof SVGElement ? fs.fill : fs.color);
      focal = { count: focalEls.length, areaPct: +(fr.w * fr.h / (W * H) * 100).toFixed(1), fontPx: Math.round(fFs), maxBodyFontPx: Math.round(maxBody), accent: near(fc, accent, 12) || !!f.querySelector?.('[fill], .accent') };
      if (focalEls.length > 2) add('warn', 'many-focals', `${focalEls.length} focal points declared. One dominant idea per slide.`);
    }

    /* ---------- 10. alignment near-misses ---------- */
    // left edges of BLOCKS (an inline span that starts mid-line is not an alignment edge)
    const lefts = [...blocks].filter((b) => !(b instanceof SVGElement) && b !== root && !inFooter(b) && !['center', 'right'].includes(cs(b).textAlign))
      .map((b) => Math.round(rel(b.getBoundingClientRect()).x)).sort((a, b) => a - b);
    const edges = []; for (const x of lefts) if (!edges.length || x - edges[edges.length - 1] > 3) edges.push(x);
    const misses = []; for (let i = 1; i < edges.length; i++) if (edges[i] - edges[i - 1] <= 10) misses.push(`${edges[i - 1]}/${edges[i]}`);
    if (misses.length) add('warn', 'near-miss-alignment', `Left edges almost aligned but not: x=${misses.slice(0, 6).join(', ')}. Snap to one edge.`);

    /* ---------- 11. hygiene ---------- */
    const ids = [...root.querySelectorAll('[id]')].map((e) => e.id), dup = ids.filter((v, i) => ids.indexOf(v) !== i);
    if (dup.length) add('warn', 'duplicate-id', `Duplicate ids inside slide: ${[...new Set(dup)].join(', ')}`);
    [...root.querySelectorAll('img')].forEach((img) => { if (!img.complete || !img.naturalWidth) add('error', 'broken-image', `Broken image: ${img.getAttribute('src')}`); });
    if (!root.dataset.composition) add('info', 'no-composition', 'Slide lacks data-composition (needed for deck rhythm checks).');
    const shapes = [...root.querySelectorAll('svg *')].filter((e) => SHAPES.has(e.tagName) && !['grid', 'axis'].includes(e.dataset.role)).length;

    return {
      id: root.dataset.slide, composition: root.dataset.composition || null, family: root.dataset.family || null, headline,
      metrics: {
        words, wordBudget: budget, wordsFooter, textBlocks: blocks.size, maxBlockWords: maxBlock, textAreaPct: +textArea.toFixed(1),
        fontSizes: sizes, fontFamilies: families, headlineLines: headLines, headlineWords: headWords,
        bullets, gradients, shadows, borders, roundedBoxes: rounded, icons, emoji, cardGroups, accentUses, focal,
        leftEdges: edges.length, svgShapes: shapes,
      },
      issues,
    };
  }
  function hexToRgb(v) {
    v = (v || '').trim();
    if (v.startsWith('#')) { const h = v.length === 4 ? v.slice(1).split('').map((c) => c + c).join('') : v.slice(1, 7); return [0, 2, 4].map((i) => parseInt(h.slice(i, i + 2), 16)).join(','); }
    const m = v.match(/rgba?\(([^)]+)\)/); return m ? m[1].split(/[\s,/]+/).slice(0, 3).join(',') : '0,0,0';
  }
  window.__qaProbe = function () {
    return { slides: [...document.querySelectorAll('.slide[data-slide]')].map(probeSlide), drawErrors: window.__slideErrors || [] };
  };
})();
