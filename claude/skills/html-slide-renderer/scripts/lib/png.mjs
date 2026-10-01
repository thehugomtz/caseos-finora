// Tiny PNG decoder (8-bit, non-interlaced: exactly what Chrome screenshots produce)
// plus the image metrics the critic uses: ink coverage, spatial balance, pixel diff.
import zlib from 'node:zlib';

export function decodePNG(buf) {
  let pos = 8, width, height, depth, type; const idat = [];
  while (pos < buf.length) {
    const len = buf.readUInt32BE(pos), kind = buf.toString('ascii', pos + 4, pos + 8), data = buf.subarray(pos + 8, pos + 8 + len);
    if (kind === 'IHDR') { width = data.readUInt32BE(0); height = data.readUInt32BE(4); depth = data[8]; type = data[9]; if (data[12]) throw new Error('interlaced PNG'); }
    else if (kind === 'IDAT') idat.push(data);
    else if (kind === 'IEND') break;
    pos += 12 + len;
  }
  if (depth !== 8) throw new Error(`unsupported PNG bit depth ${depth}`);
  const bpp = { 0: 1, 2: 3, 4: 2, 6: 4 }[type];
  if (!bpp) throw new Error(`unsupported PNG color type ${type}`);
  const raw = zlib.inflateSync(Buffer.concat(idat)), stride = width * bpp, out = Buffer.alloc(width * height * 4);
  let prev = Buffer.alloc(stride), p = 0;
  for (let y = 0; y < height; y++) {
    const f = raw[p++], line = Buffer.from(raw.subarray(p, p + stride)); p += stride;
    for (let x = 0; x < stride; x++) {
      const a = x >= bpp ? line[x - bpp] : 0, b = prev[x], c = x >= bpp ? prev[x - bpp] : 0;
      let v = line[x];
      if (f === 1) v += a; else if (f === 2) v += b; else if (f === 3) v += (a + b) >> 1;
      else if (f === 4) { const pa = Math.abs(b - c), pb = Math.abs(a - c), pc = Math.abs(a + b - 2 * c); v += pa <= pb && pa <= pc ? a : pb <= pc ? b : c; }
      line[x] = v & 255;
    }
    for (let x = 0; x < width; x++) {
      const o = (y * width + x) * 4, i = x * bpp;
      if (bpp >= 3) { out[o] = line[i]; out[o + 1] = line[i + 1]; out[o + 2] = line[i + 2]; out[o + 3] = bpp === 4 ? line[i + 3] : 255; }
      else { out[o] = out[o + 1] = out[o + 2] = line[i]; out[o + 3] = bpp === 2 ? line[i + 1] : 255; }
    }
    prev = line;
  }
  return { width, height, data: out };
}

/** Background = dominant border color. Ink = pixels that differ from it. */
export function inkMetrics(img, { cols = 6, rows = 4, threshold = 30 } = {}) {
  const { width: W, height: H, data } = img, counts = new Map();
  const sample = (x, y) => { const o = (y * W + x) * 4; const k = ((data[o] >> 3) << 10) | ((data[o + 1] >> 3) << 5) | (data[o + 2] >> 3); counts.set(k, (counts.get(k) || 0) + 1); };
  for (let x = 0; x < W; x += 4) { sample(x, 2); sample(x, H - 3); }
  for (let y = 0; y < H; y += 4) { sample(2, y); sample(W - 3, y); }
  const bk = [...counts.entries()].sort((a, b) => b[1] - a[1])[0][0];
  const bg = [((bk >> 10) & 31) * 8 + 4, ((bk >> 5) & 31) * 8 + 4, (bk & 31) * 8 + 4];
  const cells = Array.from({ length: rows }, () => Array(cols).fill(0));
  let ink = 0, sx = 0, sy = 0;
  const step = 2; // subsample for speed
  for (let y = 0; y < H; y += step) for (let x = 0; x < W; x += step) {
    const o = (y * W + x) * 4;
    if (Math.max(Math.abs(data[o] - bg[0]), Math.abs(data[o + 1] - bg[1]), Math.abs(data[o + 2] - bg[2])) > threshold) {
      ink++; sx += x; sy += y; cells[Math.min(rows - 1, (y * rows / H) | 0)][Math.min(cols - 1, (x * cols / W) | 0)]++;
    }
  }
  const total = (W / step) * (H / step), perCell = total / (rows * cols);
  return {
    background: `rgb(${bg.join(',')})`,
    inkPct: +(100 * ink / total).toFixed(1),
    balance: ink ? { x: +((sx / ink) / W * 2 - 1).toFixed(2), y: +((sy / ink) / H * 2 - 1).toFixed(2) } : { x: 0, y: 0 },
    grid: cells.map((r) => r.map((c) => +(100 * c / perCell).toFixed(0))),
    emptyCells: cells.flat().filter((c) => c / perCell < 0.005).length,
  };
}

/** Fraction of pixels whose max channel difference exceeds threshold. */
export function diffPct(a, b, threshold = 40) {
  if (a.width !== b.width || a.height !== b.height) return 100;
  let n = 0;
  for (let i = 0; i < a.data.length; i += 4) {
    if (Math.max(Math.abs(a.data[i] - b.data[i]), Math.abs(a.data[i + 1] - b.data[i + 1]), Math.abs(a.data[i + 2] - b.data[i + 2])) > threshold) n++;
  }
  return +(100 * n / (a.width * a.height)).toFixed(3);
}
