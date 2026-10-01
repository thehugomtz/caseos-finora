#!/usr/bin/env node
// Scaffold a deck folder (never overwrites existing content unless --force).
//
//   node new-deck.mjs <deck-dir> --title "Título" [--direction editorial|modern|blueprint|path/to/theme.css]
//                     [--slides 5] [--lang es]
//   node new-deck.mjs <deck-dir> --update-assets     (refresh engine files; keeps theme.css and slides)
//   node new-deck.mjs <deck-dir> --set-direction modern   (switch assets/theme.css)
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const SKILL = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const argv = process.argv.slice(2);
const flag = (n) => argv.includes(`--${n}`);
const opt = (n, d = null) => { const i = argv.indexOf(`--${n}`); return i >= 0 ? argv[i + 1] : d; };
const VALUED = new Set(['title', 'direction', 'slides', 'lang', 'set-direction']);
const target = argv.find((a, i) => !a.startsWith('--') && !(i > 0 && VALUED.has(argv[i - 1].slice(2))));
if (!target) { console.error('usage: new-deck.mjs <deck-dir> --title "..." [--direction editorial] [--slides 5]'); process.exit(1); }
const deck = path.resolve(target), force = flag('force');
const w = (rel, content) => { const p = path.join(deck, rel); if (fs.existsSync(p) && !force) return false; fs.mkdirSync(path.dirname(p), { recursive: true }); fs.writeFileSync(p, content); return true; };
const cp = (from, to) => { fs.mkdirSync(path.dirname(to), { recursive: true }); fs.copyFileSync(from, to); };

function copyEngine() {
  for (const f of ['core.css', 'primitives.js', 'deck.js']) cp(path.join(SKILL, 'assets', f), path.join(deck, 'assets', f));
  for (const f of fs.readdirSync(path.join(SKILL, 'assets/fonts'))) cp(path.join(SKILL, 'assets/fonts', f), path.join(deck, 'assets/fonts', f));
  for (const f of fs.readdirSync(path.join(SKILL, 'assets/themes'))) {
    const to = path.join(deck, 'assets/themes', f);
    if (!fs.existsSync(to) || force || flag('update-assets')) cp(path.join(SKILL, 'assets/themes', f), to);
  }
}
function setDirection(dir) {
  const src = dir.endsWith('.css') ? path.resolve(dir) : path.join(deck, 'assets/themes', `${dir}.css`);
  if (!fs.existsSync(src)) throw new Error(`theme not found: ${src}`);
  cp(src, path.join(deck, 'assets/theme.css'));
  const metaP = path.join(deck, 'deck.json');
  if (fs.existsSync(metaP)) { const m = JSON.parse(fs.readFileSync(metaP, 'utf8')); m.direction = path.basename(src, '.css'); fs.writeFileSync(metaP, JSON.stringify(m, null, 2)); }
  console.log(`theme.css ← ${path.relative(deck, src)}`);
}

if (flag('update-assets')) { copyEngine(); console.log('engine assets refreshed (theme.css and slides untouched)'); process.exit(0); }
if (opt('set-direction')) { setDirection(opt('set-direction')); process.exit(0); }

const title = opt('title', path.basename(deck)), direction = opt('direction', 'editorial'), lang = opt('lang', 'es'), n = +opt('slides', 0);
for (const d of ['slides', 'renders', 'slide-specs', 'directions/preview', 'assets']) fs.mkdirSync(path.join(deck, d), { recursive: true });
copyEngine();
if (!fs.existsSync(path.join(deck, 'assets/theme.css')) || force) setDirection(direction);
w('deck.json', JSON.stringify({ title, lang, direction: direction.replace(/\.css$/, ''), created: new Date().toISOString().slice(0, 10) }, null, 2));

w('storyline.md', `# Storyline — ${title}\n\n> Producido por \`executive-storyline\`. No contiene diseño.\n\n## 1. Audiencia y decisión\n\n## 2. Governing thought\n\n## 3. Pirámide (key line)\n\n## 4. Secuencia y read-through de títulos\n\n## 5. Slide briefs (YAML)\n\n## 6. Lo que NO aparece (cortes) y apéndice\n\n## 7. Claims sin evidencia / preguntas abiertas\n`);
w('visual-direction.md', `# Dirección visual — ${title}\n\n> Producido por \`consulting-visual-director\` (modo dirección).\n\n## Referencias → reglas abstractas\n\n## Direcciones propuestas\n\n## Preview (data-heavy + framework-heavy)\n\n## Decisión\n`);
w('qa-report.md', `# QA — ${title}\n\n> Producido por \`slide-critic\`. El reporte automático vive en renders/qa-summary.md.\n`);

const tpl = fs.readFileSync(path.join(SKILL, 'assets/templates/slide.html'), 'utf8');
for (let i = 1; i <= n; i++) {
  const nn = String(i).padStart(2, '0'), id = `S${nn}`;
  const html = tpl.replaceAll('{{ID}}', id).replaceAll('{{id}}', id.toLowerCase()).replaceAll('{{PAGE}}', String(i)).replaceAll('{{BUDGET}}', '90')
    .replace(/\{\{[A-Z]+\}\}/g, '');
  w(`slides/${nn}.html`, html);
}
console.log(`deck ready → ${deck}\n  direction: ${direction}${n ? `\n  ${n} slide skeletons in slides/` : ''}\n  next: storyline.md → visual-direction.md → slide-specs/ → slides/ → render.mjs`);
