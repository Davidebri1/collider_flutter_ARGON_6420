// Made by Claude (2026-10-20). Collider's document editor: Novel (Vercel's editor template, Tiptap underneath)
// with Word, PDF, Markdown, HTML and text in and out, spelling, autocorrect, formatting, tables and images.
import { createRoot } from 'react-dom/client';
import { useEffect, useRef, useState, useCallback } from 'react';
import {
  EditorRoot, EditorContent, EditorBubble, EditorBubbleItem, EditorCommand, EditorCommandItem, EditorCommandList,
  EditorCommandEmpty, useEditor, StarterKit, TiptapUnderline, TextStyle, Color, HighlightExtension, TiptapLink,
  UpdatedImage, TaskList, TaskItem, HorizontalRule, GlobalDragHandle, Command, renderItems, createSuggestionItems,
  handleCommandNavigation, ImageResizer, UploadImagesPlugin, createImageUpload, handleImagePaste, handleImageDrop,
} from 'novel';
import { Extension, textInputRule, InputRule } from '@tiptap/core';
import Typography from '@tiptap/extension-typography';
import TextAlign from '@tiptap/extension-text-align';
import Table from '@tiptap/extension-table';
import TableRow from '@tiptap/extension-table-row';
import TableHeader from '@tiptap/extension-table-header';
import TableCell from '@tiptap/extension-table-cell';
import Subscript from '@tiptap/extension-subscript';
import Superscript from '@tiptap/extension-superscript';
import FontFamily from '@tiptap/extension-font-family';
import mammoth from 'mammoth';
import { marked } from 'marked';
import TurndownService from 'turndown';
import { docxFromJson } from './to_docx.js';
import html2pdf from 'html2pdf.js';
import * as pdfjs from 'pdfjs-dist';
import workerSource from './pdf_worker_source.js';
import css from './style.css';
import printCss from './print.css';
import symbols from './symbols_font.js';

document.head.insertAdjacentHTML('beforeend', `<style>${css.replace('__SYMBOLS__', symbols)}</style>`);
pdfjs.GlobalWorkerOptions.workerSrc = URL.createObjectURL(new Blob([workerSource], { type: 'text/javascript' }));

// Apple system colours (dark appearance); each kind of tool keeps its own colour.
const HUE = { red: '#FF4245', orange: '#FF9230', yellow: '#FFD600', green: '#30D158', mint: '#00DAC3', teal: '#00D2E0',
  cyan: '#3CD3FE', blue: '#0091FF', indigo: '#6D7CFF', purple: '#DB34F2', pink: '#FF375F', gray: '#AEAEB2' };
const ICON_HUE = {"folder_open":"blue","save":"green","check":"green","ios_share":"blue","undo":"orange","redo":"orange","format_paragraph":"indigo","format_h1":"indigo","format_h2":"indigo","format_h3":"indigo","text_decrease":"teal","text_increase":"teal","format_bold":"pink","format_italic":"pink","format_underlined":"pink","strikethrough_s":"pink","superscript":"pink","subscript":"pink","format_clear":"gray","format_align_left":"cyan","format_align_center":"cyan","format_align_right":"cyan","format_align_justify":"cyan","format_list_bulleted":"mint","format_list_numbered":"mint","checklist":"mint","format_indent_decrease":"mint","format_indent_increase":"mint","format_quote":"yellow","code_blocks":"yellow","link":"blue","link_off":"blue","image":"orange","table":"green","horizontal_rule":"gray","add_row_below":"green","add_column_right":"green","cell_merge":"green","delete":"red","description":"blue","picture_as_pdf":"red"};
const i = (name, hue) => <span className="ico" style={{ color: HUE[hue || ICON_HUE[name]] || '#f2f2f7' }}>{name}</span>;

// ---- Autocorrect: common slips fixed as you type; Backspace right after a fix puts back what was typed. ----
const SLIPS = {
  teh: 'the', adn: 'and', taht: 'that', hte: 'the', wiht: 'with', recieve: 'receive', recieved: 'received',
  seperate: 'separate', definately: 'definitely', occured: 'occurred', occuring: 'occurring', untill: 'until',
  wich: 'which', becuase: 'because', thier: 'their', accomodate: 'accommodate', acheive: 'achieve',
  beleive: 'believe', enviroment: 'environment', goverment: 'government', tommorow: 'tomorrow', tomorow: 'tomorrow',
  wierd: 'weird', alot: 'a lot', begining: 'beginning', calender: 'calendar', concious: 'conscious',
  existance: 'existence', foriegn: 'foreign', freind: 'friend', grammer: 'grammar', independant: 'independent',
  knowlege: 'knowledge', neccessary: 'necessary', occassion: 'occasion', persistant: 'persistent', posession: 'possession',
  publically: 'publicly', reccomend: 'recommend', recomend: 'recommend', refered: 'referred', relevent: 'relevant',
  succesful: 'successful', supercede: 'supersede', truely: 'truly', wether: 'whether', youre: 'you’re',
  dont: 'don’t', didnt: 'didn’t', doesnt: 'doesn’t', isnt: 'isn’t', wasnt: 'wasn’t', arent: 'aren’t',
  couldnt: 'couldn’t', shouldnt: 'shouldn’t', wouldnt: 'wouldn’t', havent: 'haven’t', hasnt: 'hasn’t',
  thats: 'that’s', theyre: 'they’re', ive: 'I’ve', im: 'I’m', i: 'I', "i'm": 'I’m', 'i’m': 'I’m', "i'll": 'I’ll',
  'i’ll': 'I’ll', "i'd": 'I’d', 'i’d': 'I’d', "i've": 'I’ve', 'i’ve': 'I’ve',
};
const NOT_SENTENCE_END = /(?:^|\s)(?:e\.g|i\.e|a\.m|p\.m|etc|vs|mr|mrs|ms|dr|st|no|fig|approx|inc|ltd|jr|sr)\.\s+$/i;
const esc = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
const AutoCorrect = Extension.create({
  name: 'autoCorrect',
  addInputRules() {
    const rules = [];
    for (const [wrong, right] of Object.entries(SLIPS)) {
      const variants = [[wrong, right]];
      const cap = wrong[0].toUpperCase() + wrong.slice(1);
      if (cap !== wrong) variants.push([cap, right[0].toUpperCase() + right.slice(1)]);
      for (const [w, r] of variants) {
        if (w === r) continue;
        rules.push(textInputRule({ find: new RegExp(`(?:^|\\s)(${esc(w)})[\\s.,;:!?]$`), replace: r }));
      }
    }
    // A letter that starts a sentence becomes a capital.
    rules.push(new InputRule({
      find: /(?:^|[.!?]["”’)]?\s+)([a-z])$/,
      handler: ({ state, range, match }) => {
        const $from = state.selection.$from;
        if (match[0].length === 1) {
          if ($from.parentOffset !== 0) return null;
        } else {
          const before = state.doc.textBetween(Math.max($from.start(), range.to - 40), range.to, ' ', ' ');
          if (NOT_SENTENCE_END.test(before)) return null;
        }
        state.tr.insertText(match[1].toUpperCase(), range.from + match[0].length - 1, range.to);
      },
    }));
    return rules;
  },
});

// Text size steps for the larger and smaller buttons.
const SIZES = ['10px', '11px', '12px', '14px', '16px', '18px', '20px', '24px', '28px', '32px', '40px', '48px', '64px'];
const FontSize = Extension.create({
  name: 'fontSize',
  addGlobalAttributes() {
    return [{
      types: ['textStyle'],
      attributes: {
        fontSize: {
          default: null,
          parseHTML: (el) => el.style.fontSize || null,
          renderHTML: (a) => (a.fontSize ? { style: `font-size: ${a.fontSize}` } : {}),
        },
      },
    }];
  },
});

// ---- Reading files into the page ----
const extOf = (name) => (name.match(/\.([a-z0-9]+)$/i) || [, ''])[1].toLowerCase();
const baseOf = (name) => name.replace(/\.[a-z0-9]+$/i, '');
const escapeHtml = (s) => s.replace(/[&<>]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));

async function pdfToHtml(buf) {
  const doc = await pdfjs.getDocument({ data: buf }).promise;
  const out = [];
  for (let n = 1; n <= doc.numPages; n++) {
    const page = await doc.getPage(n);
    const tc = await page.getTextContent();
    const lines = [];
    for (const it of tc.items) {
      if (!('str' in it)) continue;
      const y = Math.round(it.transform[5]);
      const size = Math.round(Math.hypot(it.transform[2], it.transform[3]));
      const last = lines[lines.length - 1];
      if (last && Math.abs(last.y - y) <= 2) { last.text += it.str; last.size = Math.max(last.size, size); }
      else lines.push({ y, size, text: it.str });
    }
    const sizes = lines.map((l) => l.size).sort((a, b) => a - b);
    const body = sizes[Math.floor(sizes.length / 2)] || 12;
    let para = null, prevY = null;
    const flush = () => { if (para) { out.push(para.tag === 'p' ? `<p>${escapeHtml(para.text.trim())}</p>` : `<${para.tag}>${escapeHtml(para.text.trim())}</${para.tag}>`); para = null; } };
    for (const l of lines) {
      if (!l.text.trim()) { flush(); prevY = l.y; continue; }
      const tag = l.size >= body * 1.6 ? 'h1' : l.size >= body * 1.3 ? 'h2' : l.size >= body * 1.12 ? 'h3' : 'p';
      const gap = prevY == null ? 0 : prevY - l.y;
      if (!para || para.tag !== tag || gap > l.size * 1.8 || tag !== 'p') { flush(); para = { tag, text: l.text }; }
      else para.text += (para.text.endsWith('-') ? '' : ' ') + l.text;
      prevY = l.y;
    }
    flush();
  }
  return out.join('');
}

async function fileToHtml(name, buf) {
  const ext = extOf(name);
  if (ext === 'docx') {
    const r = await mammoth.convertToHtml({ arrayBuffer: buf }, { convertImage: mammoth.images.dataUri });
    return r.value;
  }
  if (ext === 'pdf') return pdfToHtml(buf);
  const text = new TextDecoder().decode(buf);
  if (ext === 'md' || ext === 'markdown') return marked.parse(text);
  if (ext === 'html' || ext === 'htm') return new DOMParser().parseFromString(text, 'text/html').body.innerHTML;
  return text.split(/\r?\n\r?\n/).map((p) => `<p>${escapeHtml(p).replace(/\r?\n/g, '<br>')}</p>`).join('');
}

// ---- Writing the page out ----
const toB64 = (buf) => {
  const bytes = new Uint8Array(buf);
  let s = '';
  for (let k = 0; k < bytes.length; k += 0x8000) s += String.fromCharCode.apply(null, bytes.subarray(k, k + 0x8000));
  return btoa(s);
};
const turndown = new TurndownService({ headingStyle: 'atx', codeBlockStyle: 'fenced', bulletListMarker: '-' });

function fullHtml(editor, title) {
  return `<!doctype html><html><head><meta charset="utf-8"><title>${escapeHtml(title)}</title><style>${printCss}</style></head><body>${editor.getHTML()}</body></html>`;
}

async function docxBytes(editor, title) {
  return (await docxFromJson(editor.getJSON(), title)).arrayBuffer();
}

async function pdfBytes(pageEl, title) {
  const clone = pageEl.cloneNode(true);
  clone.querySelectorAll('[contenteditable]').forEach((n) => n.removeAttribute('contenteditable'));
  clone.style.padding = '0 84px';
  clone.style.minHeight = '0';
  const holder = document.createElement('div');
  holder.className = 'pdfprint';
  holder.style.cssText = 'position:fixed;left:-10000px;top:0;width:816px';
  holder.appendChild(clone);
  document.body.appendChild(holder);
  try {
    const blob = await html2pdf().set({
      margin: [72, 0, 72, 0], filename: title + '.pdf', image: { type: 'jpeg', quality: 1 },
      html2canvas: { scale: 3, useCORS: true, backgroundColor: '#ffffff' },
      jsPDF: { unit: 'px', format: [816, 1056], hotfixes: ['px_scaling'] },
      pagebreak: { mode: ['css', 'legacy'], avoid: ['img', 'tr', 'pre', 'blockquote'] },
    }).from(clone).outputPdf('blob');
    return blob.arrayBuffer();
  } finally {
    holder.remove();
  }
}

// Inside the app the PDF is printed by Edge on this computer: real, selectable text at full sharpness.
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

async function bytesFor(fmt, editor, pageEl, title) {
  if (fmt === 'docx') return docxBytes(editor, title);
  if (fmt === 'pdf') return pdfBytes(pageEl, title);
  if (fmt === 'md') return new TextEncoder().encode(turndown.turndown(editor.getHTML()));
  if (fmt === 'html' || fmt === 'htm') return new TextEncoder().encode(fullHtml(editor, title));
  return new TextEncoder().encode(editor.getText({ blockSeparator: '\n\n' }));
}

// Saves into Collider's Files when the editor runs inside the app; elsewhere the browser downloads it.
async function store(name, buf, replace) {
  try {
    const r = await fetch('/api/files/save', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, b64: toB64(buf), replace: replace || '' }),
    });
    if (r.ok) { const j = await r.json(); if (j.name) return j.name; }
  } catch (_) { /* not inside the app */ }
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([buf]));
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 4000);
  return null;
}

// ---- Images: picked, pasted or dropped pictures are kept inside the document itself ----
const readAsDataUrl = (file) => new Promise((ok, fail) => {
  const r = new FileReader();
  r.onload = () => ok(r.result);
  r.onerror = fail;
  r.readAsDataURL(file);
});
const uploadFn = createImageUpload({
  onUpload: readAsDataUrl,
  validateFn: (file) => file.type.startsWith('image/'),
});
const Picture = UpdatedImage.extend({
  addProseMirrorPlugins() { return [UploadImagesPlugin({ imageClass: 'img-uploading' })]; },
}).configure({ allowBase64: true, inline: false });

// ---- The "/" menu ----
const pickImage = () => new Promise((ok) => {
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = 'image/*';
  input.onchange = () => ok(input.files?.[0] || null);
  input.click();
});
const insertPicture = async (editor) => {
  const file = await pickImage();
  if (file) uploadFn(file, editor.view, editor.view.state.selection.from);
};
const slashItems = createSuggestionItems([
  { title: 'Text', icon: i('format_paragraph'), searchTerms: ['p', 'paragraph'], command: ({ editor, range }) => editor.chain().focus().deleteRange(range).setNode('paragraph').run() },
  { title: 'Heading 1', icon: i('format_h1'), searchTerms: ['title', 'h1'], command: ({ editor, range }) => editor.chain().focus().deleteRange(range).setNode('heading', { level: 1 }).run() },
  { title: 'Heading 2', icon: i('format_h2'), searchTerms: ['subtitle', 'h2'], command: ({ editor, range }) => editor.chain().focus().deleteRange(range).setNode('heading', { level: 2 }).run() },
  { title: 'Heading 3', icon: i('format_h3'), searchTerms: ['h3'], command: ({ editor, range }) => editor.chain().focus().deleteRange(range).setNode('heading', { level: 3 }).run() },
  { title: 'Bullet list', icon: i('format_list_bulleted'), searchTerms: ['unordered', 'ul'], command: ({ editor, range }) => editor.chain().focus().deleteRange(range).toggleBulletList().run() },
  { title: 'Numbered list', icon: i('format_list_numbered'), searchTerms: ['ordered', 'ol'], command: ({ editor, range }) => editor.chain().focus().deleteRange(range).toggleOrderedList().run() },
  { title: 'Checklist', icon: i('checklist'), searchTerms: ['todo', 'task', 'check'], command: ({ editor, range }) => editor.chain().focus().deleteRange(range).toggleTaskList().run() },
  { title: 'Quote', icon: i('format_quote'), searchTerms: ['blockquote'], command: ({ editor, range }) => editor.chain().focus().deleteRange(range).setNode('paragraph').toggleBlockquote().run() },
  { title: 'Code', icon: i('code_blocks'), searchTerms: ['codeblock'], command: ({ editor, range }) => editor.chain().focus().deleteRange(range).toggleCodeBlock().run() },
  { title: 'Table', icon: i('table'), searchTerms: ['grid'], command: ({ editor, range }) => editor.chain().focus().deleteRange(range).insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run() },
  { title: 'Divider', icon: i('horizontal_rule'), searchTerms: ['line', 'hr', 'rule'], command: ({ editor, range }) => editor.chain().focus().deleteRange(range).setHorizontalRule().run() },
  { title: 'Image', icon: i('image'), searchTerms: ['photo', 'picture', 'media'], command: ({ editor, range }) => { editor.chain().focus().deleteRange(range).run(); insertPicture(editor); } },
]);

const extensions = [
  StarterKit.configure({
    horizontalRule: false,
    dropcursor: { color: '#0091ff', width: 3 },
    codeBlock: { HTMLAttributes: { spellcheck: 'false' } },
    code: { HTMLAttributes: { spellcheck: 'false' } },
  }),
  TiptapUnderline, TextStyle, Color, FontFamily, FontSize, HighlightExtension, Subscript, Superscript,
  TiptapLink.configure({ openOnClick: false, autolink: true, HTMLAttributes: { rel: 'noopener noreferrer' } }),
  Picture, TaskList, TaskItem.configure({ nested: true }), HorizontalRule,
  Typography, AutoCorrect, TextAlign.configure({ types: ['heading', 'paragraph'] }),
  Table.configure({ resizable: true }), TableRow, TableHeader, TableCell,
  GlobalDragHandle.configure({ dragHandleWidth: 18 }),
  Command.configure({ suggestion: { items: () => slashItems, render: renderItems } }),
];

const FONTS = [['', 'Segoe UI'], ['Calibri', 'Calibri'], ['Arial', 'Arial'], ['Helvetica', 'Helvetica'], ['Verdana', 'Verdana'],
  ['Georgia', 'Georgia'], ['Times New Roman', 'Times New Roman'], ['Garamond', 'Garamond'], ['Cambria', 'Cambria'],
  ['Courier New', 'Courier New'], ['Consolas', 'Consolas']];
const OPEN_TYPES = '.docx,.pdf,.md,.markdown,.html,.htm,.txt';
const SAVE_AS = new Set(['docx', 'pdf', 'md', 'html', 'htm', 'txt']);

// ---- The window ----
function Btn({ icon, hue, on, disabled, onClick, label, style }) {
  return (
    <button className={'btn' + (on ? ' on' : '')} disabled={disabled} aria-label={label} style={style}
      onMouseDown={(e) => e.preventDefault()} onClick={onClick}>{i(icon, hue)}</button>
  );
}

function sizeStep(editor, dir) {
  const cur = editor.getAttributes('textStyle').fontSize || '16px';
  let k = SIZES.findIndex((s) => parseFloat(s) >= parseFloat(cur));
  if (k < 0) k = SIZES.length - 1;
  if (parseFloat(SIZES[k]) !== parseFloat(cur) && dir < 0) k += 1;
  const next = SIZES[Math.max(0, Math.min(SIZES.length - 1, k + dir))];
  editor.chain().focus().setMark('textStyle', { fontSize: next }).run();
}

function Bar({ editor, name, setName, onOpen, onSave, onExport, saving, saved }) {
  const [, tick] = useState(0);
  const [linking, setLinking] = useState(false);
  const [href, setHref] = useState('');
  const [sharing, setSharing] = useState(false);
  useEffect(() => {
    if (!editor) return undefined;
    const f = () => tick((n) => n + 1);
    editor.on('transaction', f);
    return () => editor.off('transaction', f);
  }, [editor]);
  if (!editor) return <div className="bar" />;
  const c = () => editor.chain().focus();
  const is = (n, a) => editor.isActive(n, a);
  const color = editor.getAttributes('textStyle').color || '#1d1d1f';
  const mark = editor.getAttributes('highlight').color || '#ffd600';
  const font = editor.getAttributes('textStyle').fontFamily || '';
  const startLink = () => {
    if (is('link')) { c().extendMarkRange('link').unsetLink().run(); return; }
    setHref(editor.getAttributes('link').href || '');
    setLinking(true);
  };
  const applyLink = () => {
    const url = href.trim();
    if (url) c().extendMarkRange('link').setLink({ href: /^[a-z]+:/i.test(url) ? url : 'https://' + url }).run();
    setLinking(false);
  };
  return (
    <div className="bar">
      <Btn icon="folder_open" label="Open" onClick={onOpen} />
      <Btn icon={saved ? 'check' : 'save'} label="Save" disabled={saving} onClick={onSave} />
      <span className="menuwrap">
        <Btn icon="ios_share" label="Export" on={sharing} disabled={saving} onClick={() => setSharing((s) => !s)} />
        {sharing && (
          <div className="drop" onMouseLeave={() => setSharing(false)}>
            <button onClick={() => { setSharing(false); onExport('docx'); }}>{i('description')}<span>Word</span></button>
            <button onClick={() => { setSharing(false); onExport('pdf'); }}>{i('picture_as_pdf')}<span>PDF</span></button>
          </div>
        )}
      </span>
      <input className="name" value={name} onChange={(e) => setName(e.target.value)} spellCheck={false} aria-label="Name" />
      <span className="sep" />
      <Btn icon="undo" label="Undo" disabled={!editor.can().undo()} onClick={() => c().undo().run()} />
      <Btn icon="redo" label="Redo" disabled={!editor.can().redo()} onClick={() => c().redo().run()} />
      <span className="sep" />
      <Btn icon="format_paragraph" label="Text" on={is('paragraph')} onClick={() => c().setParagraph().run()} />
      <Btn icon="format_h1" label="Heading 1" on={is('heading', { level: 1 })} onClick={() => c().toggleHeading({ level: 1 }).run()} />
      <Btn icon="format_h2" label="Heading 2" on={is('heading', { level: 2 })} onClick={() => c().toggleHeading({ level: 2 }).run()} />
      <Btn icon="format_h3" label="Heading 3" on={is('heading', { level: 3 })} onClick={() => c().toggleHeading({ level: 3 }).run()} />
      <span className="sep" />
      <select className="pick" value={font} aria-label="Font" style={{ fontFamily: font || 'Segoe UI' }}
        onChange={(e) => (e.target.value ? c().setFontFamily(e.target.value).run() : c().unsetFontFamily().run())}>
        {FONTS.map(([v, l]) => <option key={l} value={v} style={{ fontFamily: v || 'Segoe UI' }}>{l}</option>)}
      </select>
      <Btn icon="text_decrease" label="Smaller" onClick={() => sizeStep(editor, -1)} />
      <Btn icon="text_increase" label="Larger" onClick={() => sizeStep(editor, 1)} />
      <span className="sep" />
      <Btn icon="format_bold" label="Bold" on={is('bold')} onClick={() => c().toggleBold().run()} />
      <Btn icon="format_italic" label="Italic" on={is('italic')} onClick={() => c().toggleItalic().run()} />
      <Btn icon="format_underlined" label="Underline" on={is('underline')} onClick={() => c().toggleUnderline().run()} />
      <Btn icon="strikethrough_s" label="Strikethrough" on={is('strike')} onClick={() => c().toggleStrike().run()} />
      <Btn icon="superscript" label="Superscript" on={is('superscript')} onClick={() => c().toggleSuperscript().run()} />
      <Btn icon="subscript" label="Subscript" on={is('subscript')} onClick={() => c().toggleSubscript().run()} />
      <span className="btn swatch">
        <span className="ico" style={{ color: color === '#1d1d1f' ? '#f2f2f7' : color }}>format_color_text</span>
        <input type="color" value={color} onChange={(e) => c().setColor(e.target.value).run()} aria-label="Text color" />
      </span>
      <span className="btn swatch">
        <span className="ico" style={{ color: mark }}>ink_highlighter</span>
        <input type="color" value={mark} onChange={(e) => c().setHighlight({ color: e.target.value }).run()} aria-label="Highlight" />
      </span>
      <Btn icon="format_clear" label="Clear formatting" onClick={() => c().unsetAllMarks().unsetTextAlign().run()} />
      <span className="sep" />
      <Btn icon="format_align_left" label="Align left" on={is({ textAlign: 'left' })} onClick={() => c().setTextAlign('left').run()} />
      <Btn icon="format_align_center" label="Center" on={is({ textAlign: 'center' })} onClick={() => c().setTextAlign('center').run()} />
      <Btn icon="format_align_right" label="Align right" on={is({ textAlign: 'right' })} onClick={() => c().setTextAlign('right').run()} />
      <Btn icon="format_align_justify" label="Justify" on={is({ textAlign: 'justify' })} onClick={() => c().setTextAlign('justify').run()} />
      <span className="sep" />
      <Btn icon="format_list_bulleted" label="Bullet list" on={is('bulletList')} onClick={() => c().toggleBulletList().run()} />
      <Btn icon="format_list_numbered" label="Numbered list" on={is('orderedList')} onClick={() => c().toggleOrderedList().run()} />
      <Btn icon="checklist" label="Checklist" on={is('taskList')} onClick={() => c().toggleTaskList().run()} />
      <Btn icon="format_indent_decrease" label="Outdent" disabled={!editor.can().liftListItem('listItem') && !editor.can().liftListItem('taskItem')}
        onClick={() => (editor.can().liftListItem('listItem') ? c().liftListItem('listItem').run() : c().liftListItem('taskItem').run())} />
      <Btn icon="format_indent_increase" label="Indent" disabled={!editor.can().sinkListItem('listItem') && !editor.can().sinkListItem('taskItem')}
        onClick={() => (editor.can().sinkListItem('listItem') ? c().sinkListItem('listItem').run() : c().sinkListItem('taskItem').run())} />
      <Btn icon="format_quote" label="Quote" on={is('blockquote')} onClick={() => c().toggleBlockquote().run()} />
      <Btn icon="code_blocks" label="Code" on={is('codeBlock')} onClick={() => c().toggleCodeBlock().run()} />
      <span className="sep" />
      <Btn icon={is('link') ? 'link_off' : 'link'} label="Link" on={linking} onClick={startLink} />
      {linking && (
        <input className="name link" autoFocus value={href} onChange={(e) => setHref(e.target.value)} aria-label="Link"
          onKeyDown={(e) => { if (e.key === 'Enter') applyLink(); if (e.key === 'Escape') setLinking(false); }} onBlur={applyLink} />
      )}
      <Btn icon="image" label="Image" onClick={() => insertPicture(editor)} />
      <Btn icon="table" label="Table" on={is('table')} onClick={() => c().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run()} />
      <Btn icon="horizontal_rule" label="Divider" onClick={() => c().setHorizontalRule().run()} />
      {is('table') && (
        <>
          <span className="sep" />
          <Btn icon="add_row_below" label="Add row" onClick={() => c().addRowAfter().run()} />
          <Btn icon="add_column_right" label="Add column" onClick={() => c().addColumnAfter().run()} />
          <Btn icon="table_rows" hue="red" label="Delete row" onClick={() => c().deleteRow().run()} />
          <Btn icon="view_column" hue="red" label="Delete column" onClick={() => c().deleteColumn().run()} />
          <Btn icon="cell_merge" label="Merge or split cells" onClick={() => c().mergeOrSplit().run()} />
          <Btn icon="delete" label="Delete table" onClick={() => c().deleteTable().run()} />
        </>
      )}
    </div>
  );
}

function Bubble() {
  const { editor } = useEditor();
  if (!editor) return null;
  const items = [
    ['format_bold', 'bold', (e) => e.chain().focus().toggleBold().run()],
    ['format_italic', 'italic', (e) => e.chain().focus().toggleItalic().run()],
    ['format_underlined', 'underline', (e) => e.chain().focus().toggleUnderline().run()],
    ['strikethrough_s', 'strike', (e) => e.chain().focus().toggleStrike().run()],
    ['ink_highlighter', 'highlight', (e) => e.chain().focus().toggleHighlight({ color: '#ffd600' }).run()],
    ['code', 'code', (e) => e.chain().focus().toggleCode().run()],
  ];
  return (
    <EditorBubble tippyOptions={{ placement: 'top' }} className="bubble">
      {items.map(([icon, mark, run]) => (
        <EditorBubbleItem key={icon} onSelect={run}>
          <button className={'btn' + (editor.isActive(mark) ? ' on' : '')} aria-label={mark}>{i(icon, icon === 'ink_highlighter' ? 'yellow' : icon === 'code' ? 'yellow' : undefined)}</button>
        </EditorBubbleItem>
      ))}
    </EditorBubble>
  );
}

function App() {
  const [editor, setEditor] = useState(null);
  const [name, setName] = useState('');
  const [fmt, setFmt] = useState('docx');
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const savedAs = useRef({});
  const pageRef = useRef(null);
  const picker = useRef(null);

  const load = useCallback(async (fileName, buf) => {
    if (!editor) return;
    const html = await fileToHtml(fileName, buf);
    editor.commands.setContent(html, false);
    editor.commands.focus('start');
    setName(baseOf(fileName));
    const ext = extOf(fileName);
    setFmt(SAVE_AS.has(ext) ? ext : 'docx');
    savedAs.current = {};
  }, [editor]);

  const openUrl = useCallback(async (url, fileName) => {
    const r = await fetch(url);
    if (!r.ok) return;
    await load(fileName || decodeURIComponent(url.split('/').pop() || ''), await r.arrayBuffer());
  }, [load]);

  // Opened from Files: ?file=<address>&name=<file name>; the app can also send a new file to an open editor.
  useEffect(() => {
    if (!editor) return undefined;
    const q = new URLSearchParams(location.search);
    if (q.get('file')) openUrl(q.get('file'), q.get('name'));
    const onMsg = (e) => { if (e.data && e.data.type === 'open' && e.data.url) openUrl(e.data.url, e.data.name); };
    addEventListener('message', onMsg);
    return () => removeEventListener('message', onMsg);
  }, [editor, openUrl]);

  const title = () => {
    let n = name.trim();
    if (!n) {
      const line = editor.getText().trim().split('\n')[0].trim();
      n = line.length <= 60 ? line : line.slice(0, 61).replace(/\s+\S*$/, '') || line.slice(0, 60);
      n = n.replace(/[.,;:!?\s]+$/, '');
    }
    return n.replace(/[<>:"/\\|?*\x00-\x1f]/g, '_') || 'document';
  };

  const write = useCallback(async (as) => {
    if (!editor || saving) return;
    setSaving(true);
    try {
      const t = title();
      let stored = as === 'pdf' ? await storePdf(`${t}.pdf`, editor, t, savedAs.current.pdf) : null;
      if (!stored) stored = await store(`${t}.${as}`, await bytesFor(as, editor, pageRef.current, t), savedAs.current[as]);
      if (stored) savedAs.current[as] = stored;
      setSaved(true);
      setTimeout(() => setSaved(false), 1600);
    } finally {
      setSaving(false);
    }
  }, [editor, saving, name]);

  useEffect(() => {
    const onKey = (e) => {
      if (!(e.ctrlKey || e.metaKey)) return;
      if (e.key === 's') { e.preventDefault(); write(fmt); }
      if (e.key === 'o') { e.preventDefault(); picker.current?.click(); }
    };
    addEventListener('keydown', onKey);
    return () => removeEventListener('keydown', onKey);
  }, [write, fmt]);

  const onPick = async (e) => {
    const f = e.target.files?.[0];
    e.target.value = '';
    if (f) await load(f.name, await f.arrayBuffer());
  };

  return (
    <div className="app">
      <input ref={picker} type="file" accept={OPEN_TYPES} hidden onChange={onPick} />
      <Bar editor={editor} name={name} setName={setName} saving={saving} saved={saved}
        onOpen={() => picker.current?.click()} onSave={() => write(fmt)} onExport={(as) => write(as)} />
      <div className="scroll">
        <div className="page" ref={pageRef}>
          <EditorRoot>
            <EditorContent
              extensions={extensions}
              immediatelyRender
              onCreate={({ editor: ed }) => setEditor(ed)}
              editorProps={{
                handleDOMEvents: { keydown: (_v, ev) => handleCommandNavigation(ev) },
                handlePaste: (view, ev) => handleImagePaste(view, ev, uploadFn),
                handleDrop: (view, ev, _s, moved) => handleImageDrop(view, ev, moved, uploadFn),
                attributes: { spellcheck: 'true', autocorrect: 'on', lang: 'en' },
              }}
              slotAfter={<ImageResizer />}
            >
              <EditorCommand className="menu">
                <EditorCommandEmpty />
                <EditorCommandList>
                  {slashItems.map((it) => (
                    <EditorCommandItem key={it.title} value={it.title} keywords={it.searchTerms}
                      onCommand={(v) => it.command(v)}>
                      {it.icon}<span className="t">{it.title}</span>
                    </EditorCommandItem>
                  ))}
                </EditorCommandList>
              </EditorCommand>
              <Bubble />
            </EditorContent>
          </EditorRoot>
        </div>
      </div>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />);
