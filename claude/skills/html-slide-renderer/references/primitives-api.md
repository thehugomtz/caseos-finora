# Primitives API (primitives.js v1)

All coordinates are canvas pixels (1920 × 1080). `s` is the slide context passed to
`P.draw('Sxx', (s, P) => { … })`. Drawing runs after web fonts load, in registration order,
then declarative `<x-…>` elements are processed, then `window.__slideReady = true`.

## Tones and weights

`tone` / `stroke` / `fill` accept a token name (`ink`, `ink-2`, `ink-3`, `ink-4`, `ink-5`,
`rule`, `bg`, `surface`, `accent`, `accent-text`, `accent-soft`, `accent-2`, `neg`, `pos`,
`highlight`) or any CSS color (avoid raw hex in slides). `w` accepts a number or
`hair (1.5) · thin (2) · med (3) · bold (5) · heavy (8)`. `dash`: `'dot' | 'dash' | 'longdash' | '8 6'`.

## Context

| Call | Returns / does |
|---|---|
| `s.root`, `s.id` | slide element, slide id |
| `s.q(sel)`, `s.qa(sel)` | query inside the slide |
| `s.box(target, pad=0)` | `{x,y,w,h,l,t,r,b,cx,cy}` of an element/selector or `[x,y]` point, in canvas px |
| `s.union('#a,#b,.c', pad)` | union box of several targets |
| `s.layer(name='main', {below, above})` | full-canvas SVG layer (main z=1 under HTML text; below z=0; above z=5) |
| `s.group({id, cls, layer})` | `<g>` in a layer |

## Text (HTML)

`s.label(x, y, html, opts)` → `<div>` absolutely positioned.
- `anchor`: `tl tc tr ml mc mr bl bc br` (which point of the label sits at x,y). Default `tl`.
- `w`: width in px (enables wrapping; without `w` the label does not wrap).
- `cls`: type role class (`label` default, `label-sm`, `annotation`, `body`, `lead`, `metric`, `caps`, …).
- `align`, `color` (token), `size` (px), `weight`, `style` (object), `id`, `focal`, `role`,
  `knockout` (background = slide bg, for labels sitting on lines), `parent` (selector).

## Shapes (SVG)

| Call | Notes |
|---|---|
| `s.line(x1,y1,x2,y2, o)` | `o.arrow: 'end'|'start'|'both'`, `headSize`, `headStyle:'open'` |
| `s.polyline(points, o)` | `o.radius` rounds corners; arrows as above |
| `s.path(d, o)` | any SVG path; arrows as above |
| `s.circle(cx,cy,r, o)` | default fill `ink`; `o.stroke` for rings |
| `s.dot(x,y, {r=6, fill})` | marker |
| `s.rect(x,y,w,h, o)` | `o.r` corner radius (keep 0 unless the direction uses radius) |
| `s.poly(points, o)` | polygon |
| `s.ring(cx,cy,r0,r1,a0,a1, o)` | donut sector, degrees clockwise from 12 o'clock; full ring when a1−a0 ≥ 360 |
| `s.text(x,y,str, {anchor:'start'|'middle'|'end', size, weight, font:'display'|'mono', fill})` | short SVG labels only |
| `s.glyph(name, x, y, {size, tone})` | `check cross plus minus arrow warn person team doc db gear clock target` — only when it encodes |
| `s.image(src, x, y, w, h, {fit, grayscale, alt})` | local assets only (`../assets/…`) |

Common style options: `stroke`/`tone`, `fill`, `w`, `dash`, `opacity`, `fillOpacity`, `cls`,
`id`, `focal`, `role`, `layer`.

## Relations

`s.connect(from, to, o)` — `from`/`to`: selector, element or `[x,y]`.
- `route`: `'curve'` (default, bezier leaving along side normals) · `'elbow'` (orthogonal with
  rounded corners; `mid` sets the turn coordinate; `radius`) · `'straight'` · `'arc'` (`bend`).
- `fromSide`/`toSide`: `auto|left|right|top|bottom|center`; `fromAt`/`toAt`: 0–1 along the side
  (spread several connectors landing on one element).
- `gap` (default 10) · `arrow` (`end` default) · `tone` (`ink-3` default) · `w` · `dash` ·
  `bend` · `dotStart` · `label`, `labelAt` (0–1), `labelDx/Dy`, `labelCls`, `labelW`, `knockout` (default true).

`s.bracket(targets, o)` — `side: right|left|top|bottom`, `style: curly|square|line`, `offset`,
`depth`, `label`, `labelW`, `labelCls` (`annotation` default), `tone`.

`s.callout({target, at:[x,y], text, anchor, w, cls, elbow, tone, dot, dotR, targetSide, leader})`
— annotation text at `at`, leader line from the nearest edge of the text to the target, dot at
the target. Returns the label element.

### Declarative (in HTML, processed after `P.draw`)

```html
<x-connect from="#s03-a" to="#s03-b" route="elbow" to-side="left" tone="accent" w="3" label="38% · 21 días"></x-connect>
<x-bracket targets="#s03-a,#s03-b,#s03-c" side="right" style="curly" label="Tres motions, una meta" label-w="260"></x-bracket>
<x-callout target="#s03-bar-q4" at="1380,300" w="360" elbow>Q4 concentra <b>45%</b> del crecimiento</x-callout>
```
Attributes are kebab-case versions of the JS options; numbers are parsed; `from="400,300"` is a point.

## Chart kit

```js
const c = s.chart({ x: 160, y: 300, w: 1100, h: 560 });           // plot area
const x = c.band(['A','B','C'], { padding: 0.35 });                // x(k)=band start, x.bw, x.center(k)
const y = c.linear([0, 1400]);                                     // y(v) → px (bottom→top); {axis:'x'} for horizontal
c.gridY(y, [0, 500, 1000], { tone: 'rule' });
c.axisX(x, { cls: 'label-sm' });                                   // baseline + centered labels
c.axisY(y, [0, 500, 1000], { format: v => P.fmt(v) });
c.bars(data, { key: d => d.k, value: d => d.v, x, y, tone: d => d.hot ? 'accent' : 'ink-4', label: d => P.fmt(d.v) });
c.bars(data, { orient: 'h', key, value, x: xLinear, y: yBand });   // horizontal / ranked
c.line(data, { x: d => x.center(d.k), y: d => y(d.v), tone: 'accent', w: 3, dots: true });
c.area(data, { x, y, y0, tone: 'accent-soft' });
const bars = c.waterfall([{k:'Potencial', v:1200, total:true, outline:true}, {k:'Fuga A', v:-310, tone:'accent', opacity:.45}, …,
             {k:'Capturado', total:true}], { x, y, totalTone: 'ink', negTone: 'ink-4', connectorDash: null });
             // step: tone · opacity · outline (potential value) · focal; returns [{k,x,cx,w,top,bottom,from,to,el,step}]
c.refLine(1000, y, { label: 'Meta' });
c.annotate(px, py, 'texto', { dx: 60, dy: -80, w: 300 });
```
`P.fmt(v, {d, prefix, suffix, sign})` formats numbers (es-MX, true minus sign). `P.niceTicks(a,b,n)`.

## Geometry (`P.geo`)

`polar(cx,cy,r,deg)` (0° = 12 o'clock, clockwise) · `around(n,cx,cy,r,start,sweep)` ·
`distribute(n,a,b,inset)` · `arc(cx,cy,r,a0,a1)` · `ring(cx,cy,r0,r1,a0,a1)` · `circle(cx,cy,r)` ·
`rounded(points, r)` · `trapezoid(cx,y,wTop,wBottom,h)` · `chevron(x,y,w,h,notch,first)` ·
`brace(x,y0,y1,depth,'right'|'left')` · `braceH(x0,x1,y,depth,'down'|'up')` · `lerp` · `mid` · `dist`.

## Grid (`P.grid`)

`col(k)` start x of column k (1–12) · `colEnd(k)` · `span(a,b) → {x, w}`.
