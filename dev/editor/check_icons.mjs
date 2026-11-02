// Made by Claude (2026-10-20). Confirms every icon name the editor uses exists in the Symbols font, so no name ever shows as text.
import { readFileSync } from 'node:fs';
const d = readFileSync(new URL('../package/index.d.ts', import.meta.url), 'utf8');
const names = new Set([...d.matchAll(/"([a-z0-9_]+)"/g)].map(m => m[1]));
const src = readFileSync(new URL('./src/main.jsx', import.meta.url), 'utf8');
const used = new Set();
const grab = (re, k = 1) => { for (const m of src.matchAll(re)) used.add(m[k]); };
grab(/\bi\(\s*'([a-z0-9_]+)'/g);                       // i('name')
grab(/icon="([a-z0-9_]+)"/g);                          // icon="name"
grab(/icon=\{[^}]*?'([a-z0-9_]+)'[^}]*?'([a-z0-9_]+)'/g); grab(/icon=\{[^}]*?'([a-z0-9_]+)'[^}]*?'([a-z0-9_]+)'/g, 2);
grab(/className="ico"[^>]*>([a-z0-9_]+)</g);           // <span className="ico">name</span>
grab(/\[\s*'([a-z0-9_]+)',\s*'[a-zA-Z]+',\s*\(e\)/g);   // bubble items
const hue = src.match(/const ICON_HUE = (\{[^\n]*\});/);
if (hue) Object.keys(JSON.parse(hue[1])).forEach((n) => used.add(n));
const missing = [...used].filter(n => !names.has(n));
console.log('icons used', used.size, 'missing', missing.length ? missing.join(', ') : 'none');
if (missing.length) process.exit(1);
