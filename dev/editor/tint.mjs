// Made by Claude (2026-10-20). One-time edit: gives every editor icon its colour.
import { readFileSync, writeFileSync } from 'node:fs';
const f = new URL('./src/main.jsx', import.meta.url);
let s = readFileSync(f, 'utf8');
const H = { folder_open: 'blue', save: 'green', check: 'green', ios_share: 'blue', undo: 'orange', redo: 'orange',
  format_paragraph: 'indigo', format_h1: 'indigo', format_h2: 'indigo', format_h3: 'indigo', text_decrease: 'teal',
  text_increase: 'teal', format_bold: 'pink', format_italic: 'pink', format_underlined: 'pink', strikethrough_s: 'pink',
  superscript: 'pink', subscript: 'pink', format_clear: 'gray', format_align_left: 'cyan', format_align_center: 'cyan',
  format_align_right: 'cyan', format_align_justify: 'cyan', format_list_bulleted: 'mint', format_list_numbered: 'mint',
  checklist: 'mint', format_indent_decrease: 'mint', format_indent_increase: 'mint', format_quote: 'yellow',
  code_blocks: 'yellow', link: 'blue', link_off: 'blue', image: 'orange', table: 'green', horizontal_rule: 'gray',
  add_row_below: 'green', add_column_right: 'green', cell_merge: 'green', delete: 'red', description: 'blue',
  picture_as_pdf: 'red' };
const rep = (a, b) => { if (!s.includes(a)) throw new Error('not found: ' + a); s = s.replace(a, b); };
rep('<Btn icon="variable_remove" label="Delete row"', '<Btn icon="table_rows" hue="red" label="Delete row"');
rep('<Btn icon="view_column_2" label="Delete column"', '<Btn icon="view_column" hue="red" label="Delete column"');
rep(' title={label}', '');
s = s.replace(/<span className="btn swatch" title="[^"]*">/g, '<span className="btn swatch">');
rep('const i = (name) => <span className="ico">{name}</span>;',
  `// Apple system colours (dark appearance); each kind of tool keeps its own colour.
const HUE = { red: '#FF4245', orange: '#FF9230', yellow: '#FFD600', green: '#30D158', mint: '#00DAC3', teal: '#00D2E0',
  cyan: '#3CD3FE', blue: '#0091FF', indigo: '#6D7CFF', purple: '#DB34F2', pink: '#FF375F', gray: '#AEAEB2' };
const ICON_HUE = ${JSON.stringify(H)};
const i = (name, hue) => <span className="ico" style={{ color: HUE[hue || ICON_HUE[name]] || '#f2f2f7' }}>{name}</span>;`);
rep('function Btn({ icon, on, disabled, onClick, label, style }) {', 'function Btn({ icon, hue, on, disabled, onClick, label, style }) {');
rep('onClick={onClick}>{i(icon)}</button>', 'onClick={onClick}>{i(icon, hue)}</button>');
writeFileSync(f, s);
console.log('ok', s.includes('title='));
