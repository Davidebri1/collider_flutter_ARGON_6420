// Made by Claude (2026-10-21). How much memory Collider's page holds on an iPhone-sized screen (3x pixels) after it
// settles: the JavaScript heap and the drawing engine's own memory (CanvasKit's WebAssembly heap).
// Usage: node mem_probe.mjs <port> [seconds]
import { chromium } from 'playwright-core';
import { existsSync } from 'node:fs';
const [port, secs = '25'] = process.argv.slice(2);
const exe = ['C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe', 'C:/Program Files/Microsoft/Edge/Application/msedge.exe'].find(existsSync);
const browser = await chromium.launch({ executablePath: exe, headless: true, args: ['--enable-precise-memory-info'] });
const ctx = await browser.newContext({ viewport: { width: 402, height: 874 }, deviceScaleFactor: 3, isMobile: true, hasTouch: true });
const page = await ctx.newPage();
const cdp = await ctx.newCDPSession(page);
await cdp.send('Performance.enable');
await page.goto(`http://127.0.0.1:${port}/`);
const mb = (n) => Math.round(n / 2 ** 20);
for (let t = 5; t <= Number(secs); t += 5) {
  await page.waitForTimeout(5000);
  const m = Object.fromEntries((await cdp.send('Performance.getMetrics')).metrics.map((x) => [x.name, x.value]));
  const wasm = await page.evaluate(() => (window.flutterCanvasKit && window.flutterCanvasKit.HEAPU8 ? window.flutterCanvasKit.HEAPU8.length : 0));
  console.log(`${t}s js ${mb(m.JSHeapUsedSize)} MB  canvaskit ${mb(wasm)} MB`);
}
await browser.close();
