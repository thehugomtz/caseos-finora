/* ==========================================================================
   html-slide-renderer · deck.js
   Presentation runtime for index.html / presentation.html (<html data-mode="deck">).
   Keys: → / Space / PgDn next · ← / PgUp prev · Home/End · G overview · N notes
         F fullscreen · P print (one slide per page) · 1..9 + Enter jump.
   Progressive build: elements with data-build="n" appear at step n (deck mode only;
   renders and print always show everything).
   ========================================================================== */
(function () {
  'use strict';
  const css = `
  html[data-mode="deck"] body { display:block; background:#111316; overflow:hidden; }
  .deck-stage { position:fixed; inset:0; }
  .deck-stage > .slide { position:absolute !important; left:0; top:0; visibility:hidden; transform-origin:0 0; box-shadow:0 0 0 1px rgba(255,255,255,.04); }
  .deck-stage > .slide.is-current { visibility:visible; }
  html[data-view="overview"] .deck-stage { overflow:auto; }
  html[data-view="overview"] .deck-stage > .slide { visibility:visible; cursor:pointer; box-shadow:0 0 0 1px rgba(255,255,255,.12); }
  html[data-view="overview"] .deck-stage > .slide.is-current { box-shadow:0 0 0 6px #3d8bff; }
  .deck-stage [data-build].build-hidden { visibility:hidden !important; }
  .deck-ui { position:fixed; z-index:1000; font:500 13px/1.3 -apple-system, 'Inter', sans-serif; color:#aab2bf; }
  .deck-hud { right:16px; bottom:12px; letter-spacing:.04em; transition:opacity .4s; }
  .deck-hud.idle { opacity:0; }
  .deck-notes { left:0; right:0; bottom:0; height:0; overflow:auto; background:#1b1e23; border-top:1px solid #2a2f37; color:#dfe4ea;
    font:400 17px/1.5 -apple-system, 'Inter', sans-serif; padding:0 32px; box-sizing:border-box; }
  html[data-notes="on"] .deck-notes { height:var(--notes-h); padding:18px 32px; }
  .deck-notes h4 { margin:0 0 6px; font-size:12px; text-transform:uppercase; letter-spacing:.1em; color:#8c95a3; }
  @media print {
    html[data-mode="deck"] body { background:none; overflow:visible; }
    .deck-stage { position:static !important; overflow:visible !important; }
    .deck-stage > .slide { position:relative !important; visibility:visible !important; box-shadow:none !important; }
    .deck-stage [data-build].build-hidden { visibility:visible !important; }
  }`;
  const style = document.createElement('style'); style.textContent = css; document.head.appendChild(style);

  const H = document.documentElement;
  let slides = [], cur = 0, step = 0, jump = '';
  const hud = Object.assign(document.createElement('div'), { className: 'deck-ui deck-hud' });
  const notes = Object.assign(document.createElement('div'), { className: 'deck-ui deck-notes' });
  let idleT;
  const poke = () => { hud.classList.remove('idle'); clearTimeout(idleT); idleT = setTimeout(() => hud.classList.add('idle'), 1800); };

  const maxStep = (sl) => Math.max(0, ...[...sl.querySelectorAll('[data-build]')].map((e) => +e.dataset.build || 0));
  function applyBuild() {
    slides.forEach((sl, i) => sl.querySelectorAll('[data-build]').forEach((e) => {
      e.classList.toggle('build-hidden', i === cur && H.dataset.view !== 'overview' && (+e.dataset.build || 0) > step);
    }));
  }
  function layout() {
    const notesOn = H.dataset.notes === 'on', nh = notesOn ? Math.round(innerHeight * 0.26) : 0;
    H.style.setProperty('--notes-h', nh + 'px');
    if (H.dataset.view === 'overview') {
      const cols = innerWidth > 1600 ? 4 : innerWidth > 900 ? 3 : 2, gap = 24;
      const w = (innerWidth - gap * (cols + 1)) / cols, s = w / 1920;
      slides.forEach((sl, i) => {
        const c = i % cols, r = Math.floor(i / cols);
        Object.assign(sl.style, { left: `${gap + c * (w + gap)}px`, top: `${gap + r * (1080 * s + gap)}px`, transform: `scale(${s})` });
      });
      return;
    }
    const aw = innerWidth, ah = innerHeight - nh, s = Math.min(aw / 1920, ah / 1080);
    const left = (aw - 1920 * s) / 2, top = (ah - 1080 * s) / 2;
    slides.forEach((sl) => Object.assign(sl.style, { left: `${left}px`, top: `${top}px`, transform: `scale(${s})` }));
  }
  function show(i, st = 0) {
    cur = Math.max(0, Math.min(slides.length - 1, i)); step = st;
    slides.forEach((sl, k) => sl.classList.toggle('is-current', k === cur));
    applyBuild();
    hud.textContent = `${cur + 1} / ${slides.length}${maxStep(slides[cur]) ? `  ·  build ${step}/${maxStep(slides[cur])}` : ''}`;
    const n = slides[cur].querySelector('aside.notes');
    notes.innerHTML = `<h4>Notas · ${slides[cur].dataset.slide || cur + 1}</h4>` + (n ? n.innerHTML : '<em>Sin notas</em>');
    if (location.hash !== `#/${cur + 1}`) history.replaceState(null, '', `#/${cur + 1}`);
    poke();
  }
  function next() { if (step < maxStep(slides[cur])) show(cur, step + 1); else if (cur < slides.length - 1) show(cur + 1, 0); }
  function prev() { if (step > 0) show(cur, step - 1); else if (cur > 0) show(cur - 1, maxStep(slides[cur - 1])); }
  function toggle(attr, on, off = null) { if (H.dataset[attr] === on) { if (off) H.dataset[attr] = off; else delete H.dataset[attr]; } else H.dataset[attr] = on; layout(); applyBuild(); }

  function start() {
    slides = [...document.querySelectorAll('.deck-stage > .slide')];
    if (!slides.length) return;
    document.body.append(hud, notes);
    const m = /#\/(\d+)/.exec(location.hash);
    layout(); show(m ? +m[1] - 1 : 0);
    window.__deck = { show: (i) => show(i, maxStep(slides[i])), count: () => slides.length };
    addEventListener('resize', layout);
    addEventListener('mousemove', poke);
    slides.forEach((sl, i) => sl.addEventListener('click', () => { if (H.dataset.view === 'overview') { delete H.dataset.view; layout(); show(i); } }));
    addEventListener('keydown', (e) => {
      if (e.metaKey || e.ctrlKey || e.altKey) return;
      const k = e.key;
      if (/^\d$/.test(k)) { jump += k; return; }
      if (k === 'Enter' && jump) { show(+jump - 1); jump = ''; return; }
      jump = '';
      if (['ArrowRight', 'PageDown', ' '].includes(k)) { e.preventDefault(); next(); }
      else if (['ArrowLeft', 'PageUp'].includes(k)) { e.preventDefault(); prev(); }
      else if (k === 'Home') show(0); else if (k === 'End') show(slides.length - 1);
      else if (k === 'g' || k === 'G' || k === 'Escape') toggle('view', 'overview');
      else if (k === 'n' || k === 'N') toggle('notes', 'on');
      else if (k === 'f' || k === 'F') { document.fullscreenElement ? document.exitFullscreen() : H.requestFullscreen?.(); }
      else if (k === 'p' || k === 'P') window.print();
    });
    addEventListener('beforeprint', () => slides.forEach((sl) => sl.querySelectorAll('.build-hidden').forEach((e) => e.classList.remove('build-hidden'))));
    addEventListener('afterprint', applyBuild);
  }
  if (window.__slideReady) start(); else document.addEventListener('slides:ready', start);
})();
