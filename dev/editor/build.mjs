// Made by Claude (2026-10-20). Builds Collider's document editor into one HTML file the app shows in a pane:
// assets/html/claude_documents.html (scripts, styles and the PDF reader's worker all inside it).
import { build } from 'esbuild';
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const out = join(here, '..', '..', 'assets', 'html', 'claude_documents.html');
const worker = readFileSync(join(here, 'node_modules', 'pdfjs-dist', 'build', 'pdf.worker.min.mjs'), 'utf8');
writeFileSync(join(here, 'src', 'pdf_worker_source.js'), 'export default ' + JSON.stringify(worker) + ';\n');
// The icon font (Material Symbols Rounded) goes inside the page too, so the editor needs nothing from the network.
const symbols = readFileSync(join(here, '..', 'package', 'material-symbols-rounded.woff2')).toString('base64');
writeFileSync(join(here, 'src', 'symbols_font.js'), 'export default ' + JSON.stringify(symbols) + ';\n');

const r = await build({
  entryPoints: [join(here, 'src', 'main.jsx')],
  bundle: true,
  minify: true,
  format: 'iife',
  target: ['chrome120'],
  write: false,
  jsx: 'automatic',
  loader: { '.css': 'text', '.module.css': 'empty' },
  define: { 'process.env.NODE_ENV': '"production"', global: 'globalThis' },
  logLevel: 'warning',
});
const js = r.outputFiles[0].text.replace(/<\/script/gi, '<\\/script');
const html = `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Documents</title></head><body><div id="root"></div><script>${js}</script></body></html>`;
mkdirSync(dirname(out), { recursive: true });
writeFileSync(out, html);
console.log('wrote', out, Math.round(html.length / 1024), 'KB');
