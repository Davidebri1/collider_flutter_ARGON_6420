// Made by Claude (2026-10-20). Drives the built Collider app (served by the app's own server) in headless Edge with its
// own profile: loads it, performs the given steps, saves a screenshot after each. Usage:
//   node drive_app.mjs <port> '[["click",x,y],["wait",ms],["type","text"],["key","Enter"],["shot","name"]]'
import { chromium } from 'playwright-core';
import { existsSync, mkdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const out = join(here, 'test_out');
mkdirSync(out, { recursive: true });
const [port, stepsJson] = process.argv.slice(2);
const steps = JSON.parse(stepsJson || '[]');
const exe = ['C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe', 'C:/Program Files/Microsoft/Edge/Application/msedge.exe'].find(existsSync);
const browser = await chromium.launch({ executablePath: exe, headless: true, args: ['--use-fake-ui-for-media-stream', '--use-fake-device-for-media-stream'] });
// A phone by default (Claude, 2026-10-21; David: "we need proper mobile aspect ratio"): iPhone 16 Pro, 402 x 874 points,
// touch, no hover. PHONE=WxH picks another size; PHONE=desk gives the old 1280 x 800 window.
const size = (process.env.PHONE || '402x874');
const desk = size === 'desk';
const [vw, vh] = desk ? [1280, 800] : size.split('x').map(Number);
const ctx = await browser.newContext({ viewport: { width: vw, height: vh }, deviceScaleFactor: desk ? 1 : 2, isMobile: !desk, hasTouch: !desk,
  permissions: ['microphone', 'clipboard-read', 'clipboard-write'] });
const page = await ctx.newPage();
const errors = [];
page.on('pageerror', (e) => errors.push('pageerror: ' + e.message));
page.on('console', (m) => { if (m.type() === 'error') errors.push('console: ' + m.text().slice(0, 200)); });
page.on('frameattached', () => {});
await page.goto(`http://127.0.0.1:${port}/`);
await page.waitForTimeout(6000);
let n = 0;
for (const s of steps) {
  const [k, a, b] = s;
  if (k === 'click') { if (desk) await page.mouse.click(a, b); else await page.touchscreen.tap(a, b); }
  else if (k === 'swipe') { const [x0, y0, x1, y1] = [a, b, s[3], s[4]]; await page.mouse.move(x0, y0); await page.mouse.down(); await page.mouse.move(x1, y1, { steps: 12 }); await page.mouse.up(); }
  else if (k === 'move') await page.mouse.move(a, b, { steps: 6 });
  else if (k === 'down') { await page.mouse.move(a, b); await page.mouse.down(); }
  else if (k === 'up') await page.mouse.up();
  else if (k === 'wait') await page.waitForTimeout(a);
  else if (k === 'type') await page.keyboard.type(a, { delay: 20 });
  else if (k === 'key') await page.keyboard.press(a);
  else if (k === 'frameclick') { const f = page.frames().find((x) => x.url().includes(a)); await f.click(b); }
  else if (k === 'frametype') { const f = page.frames().find((x) => x.url().includes(a)); await f.click('.ProseMirror'); await f.keyboard?.type?.(b); await page.keyboard.type(b, { delay: 15 }); }
  else if (k === 'framehtml') { const f = page.frames().find((x) => x.url().includes(a)); console.log('frame', f ? f.url() : 'none', f ? (await f.$eval(b, (e) => e.innerText.slice(0, 300)).catch((e) => 'no ' + b)) : ''); }
  else if (k === 'shot') await page.screenshot({ path: join(out, (a || 'step' + ++n) + '.png') });
}
console.log('frames', page.frames().map((f) => f.url()).join(' | '));
console.log('errors', JSON.stringify(errors));
await browser.close();
