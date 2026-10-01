#!/usr/bin/env node
// Assemble slides/NN.html into:
//   index.html         deck viewer that links assets/ (lightweight, for working)
//   presentation.html  single self-contained file: fonts (base64), CSS, JS, every slide inline
// then (default) verify fidelity — each slide in presentation.html is screenshotted and diffed
// against renders/NN.png — and (--pdf) print renders/deck.pdf (vector, one slide per page).
//
//   node bundle.mjs <deck-dir> [--pdf] [--no-verify] [--title "Deck title"] [--chrome PATH]
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { launch } from './lib/cdp.mjs';
import { decodePNG, diffPct } from './lib/png.mjs';

const argv = process.argv.slice(2);
const flag = (n) => argv.includes(`--${n}`);
const opt = (n, d = null) => { const i = argv.indexOf(`--${n}`); return i >= 0 ? argv[i + 1] : d; };
const VALUED = new Set(['title', 'chrome']);
const deck = path.resolve(argv.find((a, i) => !a.startsWith('--') && !(i > 0 && VALUED.has(argv[i - 1].slice(2)))) || '.');
const A = (p) => path.join(deck, 'assets', p);
const read = (p) => fs.readFileSync(p, 'utf8');
const esc = (s) => s.replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const warnings = [];

const meta = fs.existsSync(path.join(deck, 'deck.json')) ? JSON.parse(read(path.join(deck, 'deck.json'))) : {};
const title = opt('title') || meta.title || path.basename(deck);
const lang = meta.lang || 'es';
const files = fs.readdirSync(path.join(deck, 'slides')).filter((f) => /\.html?$/.test(f)).sort();
if (!files.length) throw new Error('no slides');

/* ---------- parse slides ---------- */
function balancedEnd(s, open) { let d = 0; for (let i = open; i < s.length; i++) { if (s[i] === '{') d++; else if (s[i] === '}' && --d === 0) return i + 1; } return s.length; }
function scopeCss(css, id) {
  const clean = css.replace(/\/\*[\s\S]*?\*\//g, '').trim();
  if (!clean) return '';
  const scoped = new RegExp(`^(main)?(\\.slide)?\\[data-slide=["']?${id}["']?\\]\\s*\\{`);
  // Already wrapped in [data-slide="ID"] { ... } (the skeleton does this) and nothing outside it?
  if (scoped.test(clean) && balancedEnd(clean, clean.indexOf('{')) >= clean.length - 1) return css;
  // Otherwise hoist non-nestable at-rules and wrap the rest.
  let body = clean, hoisted = '';
  for (const at of ['@keyframes', '@font-face', '@property', '@-webkit-keyframes']) {
    let i;
    while ((i = body.indexOf(at)) >= 0) { const e = balancedEnd(body, body.indexOf('{', i)); hoisted += body.slice(i, e) + '\n'; body = body.slice(0, i) + body.slice(e); }
  }
  body = body.replace(/(^|[},]\s*)(main)?\.slide(?![\w-])(\[data-slide=["']?\w+["']?\])?/g, '$1&');
  warnings.push(`${id}: slide CSS was not wrapped in [data-slide="${id}"] { } — auto-scoped (check the render).`);
  return `${hoisted}[data-slide="${id}"] {\n${body}\n}`;
}
const slides = files.map((f) => {
  const src = read(path.join(deck, 'slides', f));
  const mainM = src.match(/<main\b[^>]*class="[^"]*\bslide\b[^"]*"[^>]*>[\s\S]*<\/main>/i);
  if (!mainM) throw new Error(`${f}: no <main class="slide">`);
  const id = (mainM[0].match(/data-slide="([^"]+)"/) || [])[1] || f.replace(/\.html?$/, '');
  const head = src.slice(0, src.indexOf(mainM[0]));
  const styles = [...head.matchAll(/<style\b[^>]*>([\s\S]*?)<\/style>/gi)].map((m) => scopeCss(m[1], id)).join('\n');
  const after = src.slice(src.indexOf(mainM[0]) + mainM[0].length);
  const scripts = [...after.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/gi)].map((m) => {
    let js = m[1];
    if (/P\.draw\(\s*(\(|function|async)/.test(js)) { js = js.replace(/P\.draw\(\s*(?=\(|function|async)/g, `P.draw('${id}', `); warnings.push(`${id}: P.draw without slide id — rewritten.`); }
    return js;
  }).join('\n');
  const links = [...head.matchAll(/<link\b[^>]*href="([^"]+)"/gi)].map((m) => m[1]).filter((h) => !/assets\/(fonts\/fonts|core|theme)\.css$/.test(h) && !/^https?:/.test(h));
  if (links.length) warnings.push(`${id}: extra stylesheet(s) not bundled: ${links.join(', ')}`);
  const html = mainM[0].replace(/src="\.\.\/assets\//g, 'src="assets/');
  return { f, id, styles, scripts, html };
});
const dupIds = slides.map((s) => s.id).filter((v, i, a) => a.indexOf(v) !== i);
if (dupIds.length) throw new Error(`duplicate slide ids: ${dupIds.join(', ')}`);

/* ---------- fonts → base64 (only families actually referenced) ---------- */
const themeCss = read(A('theme.css')), coreCss = read(A('core.css'));
const used = (fam) => (themeCss + coreCss + slides.map((s) => s.styles).join('')).includes(fam);
function inlineFonts() {
  const css = read(A('fonts/fonts.css'));
  return css.split('\n').filter((l) => l.startsWith('@font-face')).filter((l) => used((l.match(/font-family:'([^']+)'/) || [])[1])).map((l) =>
    l.replace(/url\('([^']+)'\)/, (_, file) => `url(data:font/woff2;base64,${fs.readFileSync(A(`fonts/${file}`)).toString('base64')})`)).join('\n');
}
function inlineImages(html) {
  return html.replace(/(src|href)="(assets\/[^"]+\.(png|jpe?g|svg|webp|gif))"/g, (m, attr, p, ext) => {
    const file = path.join(deck, p); if (!fs.existsSync(file)) { warnings.push(`missing asset ${p}`); return m; }
    const mime = { png: 'image/png', jpg: 'image/jpeg', jpeg: 'image/jpeg', svg: 'image/svg+xml', webp: 'image/webp', gif: 'image/gif' }[ext];
    return `${attr}="data:${mime};base64,${fs.readFileSync(file).toString('base64')}"`;
  });
}

function build(inline) {
  const css = (tag, file) => (inline ? `<style>${file === 'fonts' ? inlineFonts() : read(A(file))}</style>` : `<link rel="stylesheet" href="assets/${file === 'fonts' ? 'fonts/fonts.css' : file}">`);
  const js = (file) => (inline ? `<script>${read(A(file))}</script>` : `<script src="assets/${file}"></script>`);
  const body = slides.map((s) => (inline ? inlineImages(s.html) : s.html)).join('\n');
  return `<!doctype html>
<html lang="${lang}" data-mode="deck">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(title)}</title>
${css('', 'fonts')}
${css('', 'core.css')}
${css('', 'theme.css')}
${slides.map((s) => (s.styles.trim() ? `<style data-for="${s.id}">${s.styles}</style>` : '')).join('\n')}
${js('primitives.js')}
</head>
<body>
<div class="deck-stage">
${body}
</div>
${slides.map((s) => (s.scripts.trim() ? `<script data-for="${s.id}">${s.scripts}</script>` : '')).join('\n')}
${js('deck.js')}
</body>
</html>
`;
}

fs.writeFileSync(path.join(deck, 'index.html'), build(false));
const pres = build(true);
fs.writeFileSync(path.join(deck, 'presentation.html'), pres);
console.log(`index.html + presentation.html (${(pres.length / 1024).toFixed(0)} KB, ${slides.length} slides)`);
warnings.forEach((w) => console.log('  ⚠', w));

/* ---------- verify fidelity + PDF ---------- */
if (!flag('no-verify') || flag('pdf')) {
  const browser = await launch({ chrome: opt('chrome') || undefined });
  try {
    const page = await browser.newPage({ width: 1920, height: 1080 });
    await page.goto(pathToFileURL(path.join(deck, 'presentation.html')).href);
    await page.waitFor('window.__slideReady === true && window.__deck', { timeout: 45000 });
    await page.eval(`(()=>{const s=document.createElement('style');s.textContent='.deck-ui{display:none!important}';document.head.appendChild(s)})()`);
    const errs = await page.eval('window.__slideErrors || []');
    errs.forEach((e) => console.log(`  ✖ draw error in bundle (${e.slide}): ${e.message}`));
    if (page.exceptions.length) page.exceptions.forEach((e) => console.log('  ✖ js exception:', String(e).split('\n')[0]));
    if (!flag('no-verify')) {
      const rows = [];
      for (let i = 0; i < slides.length; i++) {
        const ref = path.join(deck, 'renders', slides[i].f.replace(/\.html?$/, '.png'));
        await page.eval(`window.__deck.show(${i})`);
        await page.eval('new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))');
        const shot = await page.screenshot();
        if (!fs.existsSync(ref)) { rows.push(`${slides[i].id}: no reference render (run render.mjs first)`); continue; }
        const d = diffPct(decodePNG(shot), decodePNG(fs.readFileSync(ref)));
        rows.push(`${slides[i].id}: ${d}% pixels differ ${d > 0.5 ? '✖ bundle diverges from slide render' : '✓'}`);
      }
      console.log('fidelity (presentation.html vs renders/):'); rows.forEach((r) => console.log('  ' + r));
      fs.mkdirSync(path.join(deck, 'renders'), { recursive: true });
      fs.writeFileSync(path.join(deck, 'renders', 'bundle-fidelity.txt'), rows.join('\n') + '\n' + warnings.map((w) => 'warn: ' + w).join('\n'));
    }
    if (flag('pdf')) {
      const pdf = await page.pdf();
      fs.writeFileSync(path.join(deck, 'renders', 'deck.pdf'), pdf);
      console.log(`renders/deck.pdf (${(pdf.length / 1024).toFixed(0)} KB)`);
    }
  } finally { await browser.close(); }
}
