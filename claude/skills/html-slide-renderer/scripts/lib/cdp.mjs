// Minimal Chrome DevTools Protocol client. Zero dependencies (Node >= 22: global WebSocket).
// Launches system Chrome/Chromium/Edge headless and exposes just what slide QA needs.
import { spawn, execSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

export function findChrome() {
  const env = process.env.CHROME_PATH || process.env.PUPPETEER_EXECUTABLE_PATH;
  if (env && fs.existsSync(env)) return env;
  const pf = process.env.PROGRAMFILES, pf86 = process.env['PROGRAMFILES(X86)'], lad = process.env.LOCALAPPDATA;
  const cands = {
    darwin: [
      '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
      '/Applications/Chromium.app/Contents/MacOS/Chromium',
      '/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary',
      '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
      '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser',
    ],
    linux: ['/usr/bin/google-chrome', '/usr/bin/google-chrome-stable', '/usr/bin/chromium', '/usr/bin/chromium-browser', '/snap/bin/chromium', '/usr/bin/microsoft-edge'],
    win32: [pf && `${pf}\\Google\\Chrome\\Application\\chrome.exe`, pf86 && `${pf86}\\Google\\Chrome\\Application\\chrome.exe`,
      lad && `${lad}\\Google\\Chrome\\Application\\chrome.exe`, pf86 && `${pf86}\\Microsoft\\Edge\\Application\\msedge.exe`],
  }[process.platform] || [];
  for (const c of cands) if (c && fs.existsSync(c)) return c;
  for (const bin of ['google-chrome', 'chromium', 'chromium-browser']) {
    try { const p = execSync(`command -v ${bin}`, { stdio: ['ignore', 'pipe', 'ignore'] }).toString().trim(); if (p) return p; } catch {}
  }
  const pw = path.join(os.homedir(), process.platform === 'darwin' ? 'Library/Caches/ms-playwright' : '.cache/ms-playwright');
  if (fs.existsSync(pw)) {
    for (const d of fs.readdirSync(pw).filter((d) => d.startsWith('chromium')).sort().reverse()) {
      const guess = process.platform === 'darwin'
        ? path.join(pw, d, 'chrome-mac/Chromium.app/Contents/MacOS/Chromium')
        : path.join(pw, d, 'chrome-linux/chrome');
      if (fs.existsSync(guess)) return guess;
    }
  }
  throw new Error('No Chrome/Chromium/Edge found. Install Chrome or set CHROME_PATH=/path/to/chrome');
}

class Conn {
  constructor(ws) {
    this.ws = ws; this.seq = 0; this.pending = new Map(); this.listeners = new Set();
    ws.onmessage = (ev) => {
      const msg = JSON.parse(typeof ev.data === 'string' ? ev.data : Buffer.from(ev.data).toString());
      if (msg.id && this.pending.has(msg.id)) {
        const { resolve, reject, method } = this.pending.get(msg.id); this.pending.delete(msg.id);
        msg.error ? reject(new Error(`${method}: ${msg.error.message}`)) : resolve(msg.result);
      } else if (msg.method) for (const l of this.listeners) l(msg);
    };
  }
  send(method, params = {}, sessionId) {
    const id = ++this.seq, payload = { id, method, params };
    if (sessionId) payload.sessionId = sessionId;
    this.ws.send(JSON.stringify(payload));
    return new Promise((resolve, reject) => this.pending.set(id, { resolve, reject, method }));
  }
  on(fn) { this.listeners.add(fn); return () => this.listeners.delete(fn); }
}

export class Page {
  constructor(conn, sessionId, targetId) {
    Object.assign(this, { conn, sid: sessionId, targetId, exceptions: [], consoleErrors: [], failed: [], _req: new Map(), _onload: null });
    this.off = conn.on((m) => {
      if (m.sessionId !== this.sid) return;
      const p = m.params;
      switch (m.method) {
        case 'Page.loadEventFired': this._onload?.(); break;
        case 'Runtime.exceptionThrown': this.exceptions.push(p.exceptionDetails.exception?.description || p.exceptionDetails.text); break;
        case 'Runtime.consoleAPICalled':
          if (p.type === 'error') this.consoleErrors.push(p.args.map((a) => a.value ?? a.description ?? '').join(' ')); break;
        case 'Network.requestWillBeSent': this._req.set(p.requestId, p.request.url); break;
        case 'Network.loadingFailed': if (!p.canceled) this.failed.push({ url: this._req.get(p.requestId), error: p.errorText }); break;
        case 'Network.responseReceived': if (p.response.status >= 400) this.failed.push({ url: p.response.url, error: `HTTP ${p.response.status}` }); break;
      }
    });
  }
  send(method, params) { return this.conn.send(method, params, this.sid); }
  async init({ width, height, dsf }) {
    await Promise.all([this.send('Page.enable'), this.send('Runtime.enable'), this.send('Network.enable')]);
    await this.viewport(width, height, dsf);
  }
  viewport(width, height, dsf = 1) { return this.send('Emulation.setDeviceMetricsOverride', { width, height, deviceScaleFactor: dsf, mobile: false }); }
  async goto(url, { timeout = 45000 } = {}) {
    this.exceptions.length = 0; this.consoleErrors.length = 0; this.failed.length = 0;
    const loaded = new Promise((res, rej) => { this._onload = res; setTimeout(() => rej(new Error(`load timeout: ${url}`)), timeout); });
    const r = await this.send('Page.navigate', { url });
    if (r.errorText) throw new Error(`navigate ${url}: ${r.errorText}`);
    await loaded;
  }
  async eval(expression) {
    const r = await this.send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true });
    if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description || r.exceptionDetails.text);
    return r.result.value;
  }
  async waitFor(expression, { timeout = 30000, interval = 100 } = {}) {
    const t0 = Date.now();
    while (Date.now() - t0 < timeout) {
      try { if (await this.eval(`!!(${expression})`)) return true; } catch {}
      await sleep(interval);
    }
    throw new Error(`waitFor timeout (${timeout}ms): ${expression}`);
  }
  async screenshot({ x = 0, y = 0, width = 1920, height = 1080, scale = 1 } = {}) {
    const r = await this.send('Page.captureScreenshot', { format: 'png', clip: { x, y, width, height, scale }, captureBeyondViewport: true });
    return Buffer.from(r.data, 'base64');
  }
  async pdf(opts = {}) {
    const r = await this.send('Page.printToPDF', { printBackground: true, preferCSSPageSize: true, ...opts });
    return Buffer.from(r.data, 'base64');
  }
  async close() { this.off(); try { await this.conn.send('Target.closeTarget', { targetId: this.targetId }); } catch {} }
}

export class Browser {
  constructor(conn, proc, userDir) { Object.assign(this, { conn, proc, userDir }); }
  async newPage({ width = 1920, height = 1080, dsf = 1 } = {}) {
    const { targetId } = await this.conn.send('Target.createTarget', { url: 'about:blank' });
    const { sessionId } = await this.conn.send('Target.attachToTarget', { targetId, flatten: true });
    const page = new Page(this.conn, sessionId, targetId);
    await page.init({ width, height, dsf });
    return page;
  }
  async close() {
    try { await Promise.race([this.conn.send('Browser.close'), sleep(3000)]); } catch {}
    try { this.proc.kill('SIGKILL'); } catch {}
    try { fs.rmSync(this.userDir, { recursive: true, force: true }); } catch {}
  }
}

export async function launch({ chrome } = {}) {
  const bin = chrome || findChrome();
  const userDir = fs.mkdtempSync(path.join(os.tmpdir(), 'slides-chrome-'));
  const args = ['--headless=new', '--remote-debugging-port=0', `--user-data-dir=${userDir}`, '--no-first-run',
    '--no-default-browser-check', '--disable-gpu', '--hide-scrollbars', '--force-color-profile=srgb',
    '--font-render-hinting=none', '--allow-file-access-from-files', '--disable-extensions', '--mute-audio',
    '--disable-background-networking', '--disable-component-update', '--disable-sync', '--disable-features=Translate',
    'about:blank'];
  const proc = spawn(bin, args, { stdio: ['ignore', 'ignore', 'pipe'] });
  const wsUrl = await new Promise((resolve, reject) => {
    let buf = '';
    const t = setTimeout(() => reject(new Error(`Chrome did not expose DevTools in 30s.\n${buf.slice(-1500)}`)), 30000);
    proc.stderr.on('data', (d) => { buf += d; const m = buf.match(/DevTools listening on (ws:\/\/\S+)/); if (m) { clearTimeout(t); resolve(m[1]); } });
    proc.on('exit', (code) => { clearTimeout(t); reject(new Error(`Chrome exited (${code}).\n${buf.slice(-1500)}`)); });
  });
  const ws = new WebSocket(wsUrl);
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = () => rej(new Error('WebSocket connection to Chrome failed')); });
  return new Browser(new Conn(ws), proc, userDir);
}
