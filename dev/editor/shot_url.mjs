// Made by Claude (2026-10-20). Screenshot of one address in headless Edge (own profile): node shot_url.mjs <url> <name>
import { chromium } from 'playwright-core';
import { existsSync } from 'node:fs';
const [url, name] = process.argv.slice(2);
const exe = ['C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe', 'C:/Program Files/Microsoft/Edge/Application/msedge.exe'].find(existsSync);
const b = await chromium.launch({ executablePath: exe, headless: true });
const p = await b.newPage({ viewport: { width: 1100, height: 800 } });
await p.goto(url, { waitUntil: 'load', timeout: 40000 }).catch(() => {});
await p.waitForTimeout(5000);
await p.screenshot({ path: `test_out/${name}.png` });
console.log('ok', await p.evaluate(() => document.querySelectorAll('a[data-testid="result-title-a"], article[data-testid="result"], .result__a').length));
await b.close();
