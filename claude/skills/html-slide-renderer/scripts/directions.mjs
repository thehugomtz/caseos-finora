#!/usr/bin/env node
// Visual-direction board: render the same preview slides (one data-heavy, one framework-heavy)
// under each candidate theme, so directions are compared on real content, not mood words.
//
//   node directions.mjs <deck-dir> [--themes editorial,modern,blueprint] [--chrome PATH]
// Preview slides live in <deck>/directions/preview/*.html and link ../../assets/theme.css.
// Output: directions/renders/<theme>-<NN>.png + directions/direction-board.png
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL, fileURLToPath } from 'node:url';
import { launch } from './lib/cdp.mjs';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const PROBE = fs.readFileSync(path.join(HERE, 'lib/qa-probe.js'), 'utf8');
const argv = process.argv.slice(2);
const opt = (n, d = null) => { const i = argv.indexOf(`--${n}`); return i >= 0 ? argv[i + 1] : d; };
const deck = path.resolve(argv.find((a, i) => !a.startsWith('--') && !(i > 0 && ['themes', 'chrome'].includes(argv[i - 1].slice(2)))) || '.');
const themes = opt('themes', 'editorial,modern,blueprint').split(',').map((t) => t.trim());
const prevDir = path.join(deck, 'directions/preview'), build = path.join(deck, 'directions/_build'), out = path.join(deck, 'directions/renders');
const previews = fs.readdirSync(prevDir).filter((f) => /\.html?$/.test(f)).sort();
if (!previews.length) throw new Error('no preview slides in directions/preview/');
fs.mkdirSync(out, { recursive: true });

const describe = (t) => {
  const css = fs.readFileSync(path.join(deck, 'assets/themes', `${t}.css`), 'utf8');
  const m = css.match(/\/\*\s*([^\n]+)\n([^*]*)/);
  const text = m ? m[2].replace(/\s+/g, ' ').trim() : '';
  const cut = text.length > 220 ? text.slice(0, text.lastIndexOf('.', 220) + 1 || 220) : text; // end on a sentence
  return { name: m ? m[1].trim() : t, blurb: cut };
};

const browser = await launch({ chrome: opt('chrome') || undefined });
try {
  const page = await browser.newPage({ width: 1920, height: 1080 });
  const rows = [];
  for (const t of themes) {
    const cells = [];
    for (const f of previews) {
      // generic asset paths first, then point theme.css at the candidate theme (order matters: no double rewrite)
      const src = fs.readFileSync(path.join(prevDir, f), 'utf8').replace(/\.\.\/\.\.\/assets\//g, '../../../assets/').replace(/\.\.\/\.\.\/\.\.\/assets\/theme\.css/g, `../../../assets/themes/${t}.css`);
      const tmp = path.join(build, t, f); fs.mkdirSync(path.dirname(tmp), { recursive: true }); fs.writeFileSync(tmp, src);
      await page.goto(pathToFileURL(tmp).href);
      await page.waitFor('window.__slideReady === true');
      await page.eval(PROBE);
      const qa = await page.eval('window.__qaProbe()');
      const png = path.join(out, `${t}-${f.replace(/\.html?$/, '')}.png`);
      fs.writeFileSync(png, await page.screenshot());
      const issues = (qa.slides[0]?.issues || []).filter((i) => i.level === 'error');
      for (const e of page.failed) issues.push({ code: `asset-failed ${path.basename(e.url || '')}` });
      for (const e of qa.drawErrors) issues.push({ code: `draw-error ${e.message}` });
      console.log(`${t.padEnd(12)} ${f}  ${issues.length ? issues.map((i) => '✖ ' + i.code).join(' ') : 'clean'}`);
      cells.push(path.relative(path.join(deck, 'directions'), png));
    }
    rows.push({ t, ...describe(t), cells });
  }
  const html = `<!doctype html><meta charset=utf-8><style>
    body{margin:0;padding:56px;background:#e6e7ea;font:400 20px/1.35 -apple-system,Inter,sans-serif;color:#1d1f23}
    h1{font:600 30px/1.2 -apple-system,Inter,sans-serif;margin:0 0 36px}
    .row{display:grid;grid-template-columns:300px repeat(${previews.length},1fr);gap:32px;margin-bottom:48px;align-items:start}
    .row h2{font:600 24px/1.2 -apple-system,Inter,sans-serif;margin:0 0 10px}.row p{margin:0;color:#555;font-size:18px}
    img{width:100%;display:block;box-shadow:0 0 0 1px rgba(0,0,0,.08)}
  </style><h1>Direcciones visuales · mismo contenido, tres sistemas</h1>` +
    rows.map((r, i) => `<div class=row><div><h2>${String.fromCharCode(65 + i)} · ${r.name.replace(/^Direction [A-Z] · /, '')}</h2><p>${r.blurb}</p></div>${r.cells.map((c) => `<img src="${c}">`).join('')}</div>`).join('');
  const board = path.join(deck, 'directions/direction-board.html');
  fs.writeFileSync(board, html);
  await page.viewport(1920, 1080);
  await page.goto(pathToFileURL(board).href);
  const h = await page.eval('document.documentElement.scrollHeight');
  await page.viewport(1920, h);
  fs.writeFileSync(path.join(deck, 'directions/direction-board.png'), await page.screenshot({ width: 1920, height: h }));
  console.log('→ directions/direction-board.png');
} finally { await browser.close(); }
