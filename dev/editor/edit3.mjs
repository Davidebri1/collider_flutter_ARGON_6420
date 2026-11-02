// Made by Claude (2026-10-20). One-time edits: PDF written by the app with real text (Edge prints it), page-style
// kept in HTML files, names cut at a word, table header rows marked only when they are headers.
import { readFileSync, writeFileSync } from 'node:fs';
const f = new URL('./src/main.jsx', import.meta.url);
let s = readFileSync(f, 'utf8');
const rep = (a, b) => { if (!s.includes(a)) throw new Error('not found: ' + a); s = s.replace(a, b); };
rep("import css from './style.css';", "import css from './style.css';\nimport printCss from './print.css';");
rep("<title>${escapeHtml(title)}</title></head>", "<title>${escapeHtml(title)}</title><style>${printCss}</style></head>");
rep(`async function bytesFor(fmt, editor, pageEl, title) {`, `// Inside the app the PDF is printed by Edge on this computer: real, selectable text at full sharpness.
async function storePdf(name, editor, title, replace) {
  try {
    const r = await fetch('/api/files/pdf', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, html: fullHtml(editor, title), replace: replace || '' }),
    });
    if (r.ok) { const j = await r.json(); if (j.name) return j.name; }
  } catch (_) { /* not inside the app */ }
  return null;
}

async function bytesFor(fmt, editor, pageEl, title) {`);
rep(`      const buf = await bytesFor(as, editor, pageRef.current, t);
      const stored = await store(\`\${t}.\${as}\`, buf, savedAs.current[as]);`,
`      let stored = as === 'pdf' ? await storePdf(\`\${t}.pdf\`, editor, t, savedAs.current.pdf) : null;
      if (!stored) stored = await store(\`\${t}.\${as}\`, await bytesFor(as, editor, pageRef.current, t), savedAs.current[as]);`);
rep(`    const n = name.trim() || editor.getText().trim().split('\\n')[0].slice(0, 60).trim();`,
`    let n = name.trim();
    if (!n) {
      const line = editor.getText().trim().split('\\n')[0].trim();
      n = line.length <= 60 ? line : line.slice(0, 61).replace(/\\s+\\S*$/, '') || line.slice(0, 60);
      n = n.replace(/[.,;:!?\\s]+$/, '');
    }`);
writeFileSync(f, s);
const d = new URL('./src/to_docx.js', import.meta.url);
let t = readFileSync(d, 'utf8');
const a = "rows.push(new TableRow({ children: cells, tableHeader: (r.content || []).every((c) => c.type === 'tableHeader') }));";
if (!t.includes(a)) throw new Error('docx row');
t = t.replace(a, "const head = (r.content || []).length > 0 && r.content.every((c) => c.type === 'tableHeader');\n      rows.push(new TableRow(head ? { children: cells, tableHeader: true } : { children: cells }));");
writeFileSync(d, t);
const c = new URL('./src/style.css', import.meta.url);
let u = readFileSync(c, 'utf8');
u = u.replace('.name { flex: 1 1 160px; min-width: 120px; height: 32px; border: 0; border-radius: 10px; background: transparent;',
  '.name { flex: 1 1 160px; min-width: 120px; height: 32px; border: 0; border-radius: 10px; background: rgba(255,255,255,.06);');
writeFileSync(c, u);
console.log('ok');
