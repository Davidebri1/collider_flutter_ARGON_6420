// Made by Claude (2026-10-20). One-time edits to the editor source (kept as a record of what changed).
import { readFileSync, writeFileSync } from 'node:fs';
const f = new URL('./src/main.jsx', import.meta.url);
let s = readFileSync(f, 'utf8');
const rep = (a, b) => { if (!s.includes(a)) throw new Error('not found: ' + a); s = s.replace(a, b); };
rep("import HTMLtoDOCX from '@turbodocx/html-to-docx';", "import { docxFromJson } from './to_docx.js';");
rep(`  const out = await HTMLtoDOCX(fullHtml(editor, title), null, {
    title, table: { row: { cantSplit: true } }, font: 'Calibri', fontSize: 24, decodeUnicode: true,
  });
  return out instanceof Blob ? out.arrayBuffer() : out;`, `  return (await docxFromJson(editor.getJSON(), title)).arrayBuffer();`);
rep('TiptapImage, TaskList,', 'UpdatedImage, TaskList,');
rep('const Picture = TiptapImage.extend({', 'const Picture = UpdatedImage.extend({');
writeFileSync(f, s);
const b = new URL('./build.mjs', import.meta.url);
let t = readFileSync(b, 'utf8');
t = t.replace("loader: { '.css': 'text' },", "loader: { '.css': 'text', '.module.css': 'empty' },").replace("target: ['chrome110'],", "target: ['chrome120'],");
writeFileSync(b, t);
console.log('ok');
