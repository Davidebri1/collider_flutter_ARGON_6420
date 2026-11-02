// Made by Claude (2026-10-23). Screenshots of Collider on an iPhone 16 Pro sized screen (402 x 874, 3x), one per address.
// Usage: node phone_shot.mjs <port> <name> <query> [<name> <query> ...]   e.g. node phone_shot.mjs 47801 rest "" zoom "zoom=1"
// Also says whether the page ran as WebAssembly.
import { chromium } from 'playwright-core';
import { existsSync } from 'node:fs';
const [port, ...pairs] = process.argv.slice(2);
const exe = ['C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe', 'C:/Program Files/Microsoft/Edge/Application/msedge.exe'].find(existsSync);
const browser = await chromium.launch({ executablePath: exe, headless: true });
for (let i = 0; i < pairs.length; i += 2) {
  const [name, q] = [pairs[i], pairs[i + 1] || ''];
  const ctx = await browser.newContext({ viewport: { width: 402, height: 874 }, deviceScaleFactor: 3, isMobile: true, hasTouch: true });
  const page = await ctx.newPage();
  const loaded = [];
  page.on('response', (r) => { const u = r.url(); if (/main\.dart\.(wasm|js|mjs)$/.test(u)) loaded.push(u.split('/').pop()); });
  await page.goto(`http://127.0.0.1:${port}/${q ? '?' + q : ''}`);
  await page.waitForTimeout(14000);
  await page.screenshot({ path: `test_out/${name}.png` });
  console.log(name, 'loaded:', loaded.join(','));
  await ctx.close();
}
await browser.close();
