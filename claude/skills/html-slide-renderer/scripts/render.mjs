#!/usr/bin/env node
// Render every slide of a deck to PNG, run the in-page QA probe, measure ink/balance,
// check deck-level rhythm, and build a contact sheet. Zero dependencies (system Chrome via CDP).
//
//   node render.mjs <deck-dir> [--only 01,03] [--grid] [--no-contact] [--chrome PATH]
//   node render.mjs --file some/slide.html --out some/slide.png      (single file, e.g. direction previews)
//
// Outputs in <deck>/renders/: NN.png · thumbs/NN.png (480px, squint test) · contact-sheet.png ·
// qa.json (machine) · qa-summary.md (human). Exit code 0 unless rendering itself failed.
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL, fileURLToPath } from 'node:url';
import { launch } from './lib/cdp.mjs';
import { decodePNG, inkMetrics } from './lib/png.mjs';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const PROBE = fs.readFileSync(path.join(HERE, 'lib/qa-probe.js'), 'utf8');
const argv = process.argv.slice(2);
const flag = (n) => argv.includes(`--${n}`);
const opt = (n, d = null) => { const i = argv.indexOf(`--${n}`); return i >= 0 ? argv[i + 1] : d; };
const VALUED = new Set(['only', 'chrome', 'file', 'out']);
const positional = argv.filter((a, i) => !a.startsWith('--') && !(i > 0 && VALUED.has(argv[i - 1].slice(2))));

async function renderOne(page, file, { grid = false } = {}) {
  await page.goto(pathToFileURL(file).href);
  await page.waitFor('window.__slideReady === true', { timeout: 30000 });
  if (grid) await page.eval(`document.querySelectorAll('.slide').forEach(s => s.setAttribute('data-debug-grid',''))`);
  await page.eval(PROBE);
  const qa = await page.eval('window.__qaProbe()');
  const png = await page.screenshot();
  const thumb = await page.screenshot({ scale: 0.25 });
  return { qa, png, thumb, runtime: { exceptions: [...page.exceptions], consoleErrors: [...page.consoleErrors], failed: [...page.failed] } };
}

function levelIcon(l) { return l === 'error' ? '✖' : l === 'warn' ? '⚠' : 'ℹ'; }

async function main() {
  const single = opt('file');
  const browser = await launch({ chrome: opt('chrome') || undefined });
  try {
    const page = await browser.newPage({ width: 1920, height: 1080 });
    if (single) {
      const out = opt('out') || single.replace(/\.html?$/, '.png');
      const r = await renderOne(page, path.resolve(single), { grid: flag('grid') });
      fs.writeFileSync(out, r.png);
      const s = r.qa.slides[0] || { issues: [] };
      const issues = [...s.issues, ...r.qa.drawErrors.map((e) => ({ level: 'error', code: 'draw-error', msg: e.message }))];
      console.log(`${path.basename(out)}  words=${s.metrics?.words ?? '-'}  ` + (issues.filter((i) => i.level !== 'info').map((i) => `${levelIcon(i.level)} ${i.code}`).join('  ') || 'clean'));
      for (const i of issues.filter((i) => i.level !== 'info')) console.log(`   ${levelIcon(i.level)} ${i.msg}`);
      return;
    }

    const deck = path.resolve(positional[0] || '.');
    const slidesDir = path.join(deck, 'slides'), out = path.join(deck, 'renders');
    if (!fs.existsSync(slidesDir)) throw new Error(`No slides/ folder in ${deck}`);
    fs.mkdirSync(path.join(out, 'thumbs'), { recursive: true });
    const only = opt('only') ? opt('only').split(',').map((s) => s.trim()) : null;
    const files = fs.readdirSync(slidesDir).filter((f) => /\.html?$/.test(f)).sort()
      .filter((f) => !only || only.some((o) => f.startsWith(o)));
    const prev = fs.existsSync(path.join(out, 'qa.json')) ? JSON.parse(fs.readFileSync(path.join(out, 'qa.json'), 'utf8')) : { slides: [] };
    const results = [];

    for (const f of files) {
      const base = f.replace(/\.html?$/, '');
      const r = await renderOne(page, path.join(slidesDir, f), { grid: flag('grid') });
      fs.writeFileSync(path.join(out, `${base}.png`), r.png);
      fs.writeFileSync(path.join(out, 'thumbs', `${base}.png`), r.thumb);
      const s = r.qa.slides[0];
      if (!s) { results.push({ file: f, base, issues: [{ level: 'error', code: 'no-slide', msg: 'No .slide[data-slide] root found' }], metrics: {} }); continue; }
      const issues = [...s.issues];
      for (const e of r.qa.drawErrors) issues.push({ level: 'error', code: 'draw-error', msg: e.message });
      for (const e of r.runtime.exceptions) issues.push({ level: 'error', code: 'js-exception', msg: String(e).split('\n')[0] });
      for (const e of r.runtime.failed) issues.push({ level: 'error', code: 'asset-failed', msg: `${e.error}: ${e.url}` });
      const ink = inkMetrics(decodePNG(r.png));
      if (ink.inkPct > 34) issues.push({ level: 'warn', code: 'dense', msg: `Ink covers ${ink.inkPct}% of the canvas. Executive slides breathe; what can go?` });
      if (ink.inkPct < 3.5) issues.push({ level: 'info', code: 'sparse', msg: `Ink covers only ${ink.inkPct}% — fine for a statement slide, suspicious elsewhere.` });
      if (Math.abs(ink.balance.x) > 0.35 || Math.abs(ink.balance.y) > 0.35) issues.push({ level: 'info', code: 'balance', msg: `Visual weight is off-center (x ${ink.balance.x}, y ${ink.balance.y}). Intentional asymmetry or drift?` });
      results.push({ file: f, base, id: s.id, composition: s.composition, family: s.family, headline: s.headline, metrics: { ...s.metrics, ink }, issues });
      const e = issues.filter((i) => i.level === 'error').length, w = issues.filter((i) => i.level === 'warn').length;
      console.log(`${base}  ${String(s.id).padEnd(4)} ${String(s.composition || '?').padEnd(34)} words=${String(s.metrics.words).padStart(3)} ink=${String(ink.inkPct).padStart(4)}%  ${e ? `✖${e}` : ''} ${w ? `⚠${w}` : ''}${!e && !w ? 'clean' : ''}`);
    }

    // merge with previous results for slides not re-rendered (--only)
    const merged = [...prev.slides.filter((p) => !results.some((r) => r.base === p.base) && fs.existsSync(path.join(slidesDir, p.file))), ...results]
      .sort((a, b) => a.base.localeCompare(b.base));

    // ---------- deck-level checks ----------
    const deckIssues = [];
    const comps = merged.map((r) => r.composition || '?'), fams = merged.map((r) => r.family || r.composition || '?');
    for (let i = 1; i < merged.length; i++) {
      if (comps[i] !== '?' && comps[i] === comps[i - 1]) deckIssues.push({ level: 'warn', code: 'repeat-composition', msg: `${merged[i - 1].base}→${merged[i].base} repeat composition "${comps[i]}".` });
      else if (fams[i] !== '?' && fams[i] === fams[i - 1] && i > 1 && fams[i] === fams[i - 2]) deckIssues.push({ level: 'warn', code: 'repeat-family', msg: `Three consecutive slides from family "${fams[i]}" (${merged[i - 2].base}–${merged[i].base}).` });
    }
    const cardSlides = merged.filter((r) => (r.metrics.cardGroups || []).some((g) => g.kind !== 'stack'));
    if (cardSlides.length > 1) deckIssues.push({ level: 'error', code: 'deck-card-grids', msg: `${cardSlides.length} slides use card grids (${cardSlides.map((r) => r.base).join(', ')}). Max one per deck.` });
    const uniq = new Set(comps.filter((c) => c !== '?'));
    if (merged.length >= 4 && uniq.size < Math.ceil(merged.length * 0.6)) deckIssues.push({ level: 'warn', code: 'low-variety', msg: `Only ${uniq.size} distinct compositions across ${merged.length} slides.` });
    const hf = merged.map((r) => (r.metrics.fontSizes || [])[0]).filter(Boolean);
    const words = merged.map((r) => r.metrics.words || 0), avgW = words.reduce((a, b) => a + b, 0) / Math.max(1, words.length);
    merged.forEach((r) => { if (r.metrics.words > avgW * 2 && r.metrics.words > 60) deckIssues.push({ level: 'info', code: 'density-outlier', msg: `${r.base} carries ${r.metrics.words} words vs deck mean ${avgW.toFixed(0)}.` }); });
    const dense = merged.map((r) => (r.metrics.ink?.inkPct ?? 0) > 22);
    for (let i = 2; i < dense.length; i++) if (dense[i] && dense[i - 1] && dense[i - 2]) deckIssues.push({ level: 'info', code: 'no-breather', msg: `${merged[i - 2].base}–${merged[i].base}: three dense slides in a row. Consider a breather (statement, hero metric).` });

    const report = { deck: path.basename(deck), generated: new Date().toISOString(), slides: merged, deckIssues };
    fs.writeFileSync(path.join(out, 'qa.json'), JSON.stringify(report, null, 2));

    // ---------- human summary ----------
    let md = `# QA automático — ${report.deck}\n\n_Generado ${report.generated}. Renders en \`renders/\`, thumbnails en \`renders/thumbs/\`._\n\n`;
    md += `| # | Slide | Composición | Palabras | Tinta | ✖ | ⚠ |\n|---|---|---|---:|---:|---:|---:|\n`;
    for (const r of merged) md += `| ${r.base} | ${r.id ?? '-'} | ${r.composition ?? '-'} | ${r.metrics.words ?? '-'} | ${r.metrics.ink?.inkPct ?? '-'}% | ${r.issues.filter((i) => i.level === 'error').length} | ${r.issues.filter((i) => i.level === 'warn').length} |\n`;
    md += `\n## Nivel deck\n\n${deckIssues.length ? deckIssues.map((i) => `- ${levelIcon(i.level)} **${i.code}** — ${i.msg}`).join('\n') : '- Sin hallazgos automáticos.'}\n`;
    for (const r of merged) {
      md += `\n## ${r.base} · ${r.id ?? ''} — ${r.headline ? `“${r.headline}”` : ''}\n\n`;
      md += r.issues.length ? r.issues.map((i) => `- ${levelIcon(i.level)} **${i.code}** — ${i.msg}`).join('\n') + '\n' : '- Limpio.\n';
      const m = r.metrics;
      if (m.words != null) md += `\n<sub>palabras ${m.words}/${m.wordBudget} · bloques ${m.textBlocks} · tamaños ${m.fontSizes?.join('/')} · bordes ${m.borders} · focal ${m.focal ? `${m.focal.areaPct}% área, ${m.focal.fontPx}px` : '—'} · acento ×${m.accentUses} · bordes-izq ${m.leftEdges} · tinta ${m.ink?.inkPct}% · balance ${m.ink?.balance.x}/${m.ink?.balance.y}</sub>\n`;
    }
    fs.writeFileSync(path.join(out, 'qa-summary.md'), md);
    if (deckIssues.length) { console.log('\nDeck:'); deckIssues.forEach((i) => console.log(`  ${levelIcon(i.level)} ${i.msg}`)); }

    // ---------- contact sheet ----------
    if (!flag('no-contact')) {
      const n = merged.length, cols = n <= 4 ? 2 : n <= 9 ? 3 : n <= 16 ? 4 : 5, cw = Math.floor((1920 - 48 * (cols + 1)) / cols);
      const cells = merged.map((r) => {
        const e = r.issues.filter((i) => i.level === 'error').length, w = r.issues.filter((i) => i.level === 'warn').length;
        return `<figure><img src="${r.base}.png"><figcaption><b>${r.base}</b> ${r.composition ?? ''}<span>${r.metrics.words ?? '-'}w · ${r.metrics.ink?.inkPct ?? '-'}% ${e ? `<i class=e>✖${e}</i>` : ''} ${w ? `<i class=w>⚠${w}</i>` : ''}</span></figcaption></figure>`;
      }).join('');
      const html = `<!doctype html><meta charset=utf-8><style>
        body{margin:0;padding:48px;background:#e6e7ea;font:500 20px/1.3 -apple-system,Inter,sans-serif;color:#222}
        h1{font-size:26px;margin:0 0 32px;font-weight:600}h1 span{color:#777;font-weight:400}
        .g{display:grid;grid-template-columns:repeat(${cols},${cw}px);gap:48px}
        figure{margin:0}img{width:100%;display:block;box-shadow:0 1px 0 rgba(0,0,0,.08),0 0 0 1px rgba(0,0,0,.06)}
        figcaption{display:flex;justify-content:space-between;gap:12px;margin-top:10px;font-size:18px;color:#444}
        figcaption span{color:#777}i{font-style:normal;margin-left:6px}.e{color:#c0392b}.w{color:#b7791f}
      </style><h1>${report.deck} <span>· contact sheet · ${n} slides · ${new Date().toLocaleString('es-MX')}</span></h1><div class=g>${cells}</div>`;
      const sheet = path.join(out, 'contact-sheet.html');
      fs.writeFileSync(sheet, html);
      await page.goto(pathToFileURL(sheet).href);
      const h = await page.eval('document.documentElement.scrollHeight');
      await page.viewport(1920, h);
      fs.writeFileSync(path.join(out, 'contact-sheet.png'), await page.screenshot({ width: 1920, height: h }));
      await page.viewport(1920, 1080);
      console.log(`\ncontact sheet → ${path.relative(process.cwd(), path.join(out, 'contact-sheet.png'))}`);
    }
    console.log(`qa → ${path.relative(process.cwd(), path.join(out, 'qa-summary.md'))}`);
  } finally {
    await browser.close();
  }
}
main().catch((e) => { console.error('render failed:', e.message); process.exit(1); });
