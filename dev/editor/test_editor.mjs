// Made by Claude (2026-10-20). Checks the built editor in Edge (headless, its own profile): it loads without errors,
// autocorrect and formatting work, Word and PDF files are written, and a Word file opens back with its content.
import http from 'node:http';
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright-core';
import { Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell } from 'docx';

const here = dirname(fileURLToPath(import.meta.url));
const page_html = readFileSync(join(here, '..', '..', 'assets', 'html', 'claude_documents.html'));
const outDir = join(here, 'test_out');
mkdirSync(outDir, { recursive: true });

// A Word file made here to open in the editor.
const sample = await Packer.toBuffer(new Document({ sections: [{ children: [
  new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun('Quarterly plan')] }),
  new Paragraph({ children: [new TextRun({ text: 'Bold start', bold: true }), new TextRun(' then plain text.')] }),
  new Table({ rows: [new TableRow({ children: [new TableCell({ children: [new Paragraph('A1')] }), new TableCell({ children: [new Paragraph('B1')] })] })] }),
] }] }));

const saved = [];
const server = http.createServer((req, res) => {
  if (req.url.startsWith('/editor')) { res.writeHead(200, { 'Content-Type': 'text/html' }); return res.end(page_html); }
  if (req.url === '/files/uploaded/sample.docx') { res.writeHead(200); return res.end(sample); }
  if (req.url === '/api/files/save' && req.method === 'POST') {
    let body = '';
    req.on('data', (c) => (body += c));
    req.on('end', () => {
      const j = JSON.parse(body);
      writeFileSync(join(outDir, j.name), Buffer.from(j.b64, 'base64'));
      saved.push({ name: j.name, replace: j.replace, bytes: Buffer.from(j.b64, 'base64').length });
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ name: j.name }));
    });
    return;
  }
  res.writeHead(404); res.end();
});
await new Promise((ok) => server.listen(0, '127.0.0.1', ok));
const base = `http://127.0.0.1:${server.address().port}`;

const exe = ['C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe', 'C:/Program Files/Microsoft/Edge/Application/msedge.exe'].find(existsSync);
const browser = await chromium.launch({ executablePath: exe, headless: true });
const page = await browser.newPage({ viewport: { width: 1280, height: 900 }, deviceScaleFactor: 2 });
const errors = [];
page.on('pageerror', (e) => errors.push('pageerror: ' + e.message));
page.on('console', (m) => { if (m.type() === 'error') errors.push('console: ' + m.text()); });

const report = {};
await page.goto(base + '/editor');
await page.waitForSelector('.ProseMirror');
await page.click('.ProseMirror');
await page.keyboard.type('teh plan is ready. i think it works. dont worry -- it is fine.');
report.autocorrect = await page.$eval('.ProseMirror', (e) => e.innerText);
await page.keyboard.press('Enter');
await page.keyboard.type('/table');
await page.waitForTimeout(300);
report.slashMenu = await page.$$eval('.menu [cmdk-item]', (els) => els.map((e) => e.innerText.replace(/\s+/g, ' ').trim()));
await page.keyboard.press('Enter');
await page.waitForTimeout(200);
report.tableCells = await page.$$eval('.ProseMirror td, .ProseMirror th', (e) => e.length);
report.iconFontLoaded = await page.evaluate(async () => { await document.fonts.ready; return document.fonts.check('20px Symbols'); });
await page.screenshot({ path: join(outDir, 'editor.png') });

// Word and PDF out.
await page.click('button[aria-label="Export"]');
await page.click('.drop button:nth-child(1)');
await page.waitForTimeout(2500);
await page.click('button[aria-label="Export"]');
await page.click('.drop button:nth-child(2)');
await page.waitForTimeout(6000);
report.saved = saved;

// A Word file in.
await page.goto(base + '/editor?file=/files/uploaded/sample.docx&name=sample.docx');
await page.waitForFunction(() => document.querySelector('.ProseMirror')?.innerText.includes('Quarterly'), null, { timeout: 15000 });
report.opened = await page.$eval('.ProseMirror', (e) => e.innerHTML.slice(0, 400));
report.name = await page.$eval('input.name', (e) => e.value);
await page.screenshot({ path: join(outDir, 'opened.png') });
report.errors = errors;
console.log(JSON.stringify(report, null, 1));
await browser.close();
server.close();
