// Made by Claude (2026-10-20). Writes the editor's document as a real Word file (.docx) in the browser:
// headings, text styles, colours, fonts and sizes, links, lists, checklists, quotes, code, tables, images, dividers.
import {
  Document, Packer, Paragraph, TextRun, ExternalHyperlink, HeadingLevel, AlignmentType, Table, TableRow, TableCell,
  WidthType, BorderStyle, ShadingType, ImageRun, LevelFormat,
} from 'docx';

const HEADINGS = { 1: HeadingLevel.HEADING_1, 2: HeadingLevel.HEADING_2, 3: HeadingLevel.HEADING_3,
  4: HeadingLevel.HEADING_4, 5: HeadingLevel.HEADING_5, 6: HeadingLevel.HEADING_6 };
const ALIGN = { left: AlignmentType.LEFT, center: AlignmentType.CENTER, right: AlignmentType.RIGHT, justify: AlignmentType.JUSTIFIED };
const LINE = { style: BorderStyle.SINGLE, size: 6, color: 'D1D1D6', space: 1 };
const MAX_W = 624; // the page's writing width in pixels (6.5 inches)

const hex = (c) => {
  if (!c) return undefined;
  if (/^#[0-9a-f]{6}$/i.test(c)) return c.slice(1).toUpperCase();
  if (/^#[0-9a-f]{3}$/i.test(c)) return c.slice(1).split('').map((x) => x + x).join('').toUpperCase();
  const m = c.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
  return m ? m.slice(1, 4).map((n) => (+n).toString(16).padStart(2, '0')).join('').toUpperCase() : undefined;
};

function runsOf(nodes, extra = {}) {
  const out = [];
  for (const n of nodes || []) {
    if (n.type === 'hardBreak') { out.push(new TextRun({ break: 1 })); continue; }
    if (n.type === 'image') { out.push(n); continue; }
    if (n.type !== 'text') continue;
    const o = { text: n.text, ...extra };
    let link = null;
    for (const m of n.marks || []) {
      const a = m.attrs || {};
      if (m.type === 'bold') o.bold = true;
      else if (m.type === 'italic') o.italics = true;
      else if (m.type === 'underline') o.underline = {};
      else if (m.type === 'strike') o.strike = true;
      else if (m.type === 'superscript') o.superScript = true;
      else if (m.type === 'subscript') o.subScript = true;
      else if (m.type === 'code') { o.font = 'Consolas'; o.shading = { type: ShadingType.CLEAR, fill: 'F2F2F7', color: 'auto' }; }
      else if (m.type === 'highlight') o.shading = { type: ShadingType.CLEAR, fill: hex(a.color) || 'FFF59D', color: 'auto' };
      else if (m.type === 'textStyle') {
        if (a.color) o.color = hex(a.color);
        if (a.fontFamily) o.font = a.fontFamily.split(',')[0].replace(/["']/g, '').trim();
        if (a.fontSize) o.size = Math.round(parseFloat(a.fontSize) * 1.5);
      } else if (m.type === 'link') link = a.href;
    }
    if (link) {
      out.push(new ExternalHyperlink({ link, children: [new TextRun({ ...o, color: o.color || '0563C1', underline: o.underline || {} })] }));
    } else out.push(new TextRun(o));
  }
  return out;
}

async function imageRun(src, attrs) {
  const img = await new Promise((ok, fail) => { const im = new Image(); im.onload = () => ok(im); im.onerror = fail; im.src = src; });
  let w = Number(attrs.width) || img.naturalWidth;
  let h = Number(attrs.height) || Math.round(w * img.naturalHeight / img.naturalWidth);
  if (w > MAX_W) { h = Math.round(h * MAX_W / w); w = MAX_W; }
  let type = (src.match(/^data:image\/(png|jpe?g|gif|bmp)/i) || [])[1];
  let data;
  if (type) {
    data = await (await fetch(src)).arrayBuffer();
    type = type.toLowerCase().replace('jpeg', 'jpg');
  } else {
    // Other picture kinds are drawn at twice their shown size and kept as PNG.
    const c = document.createElement('canvas');
    c.width = w * 2; c.height = h * 2;
    c.getContext('2d').drawImage(img, 0, 0, c.width, c.height);
    data = await (await fetch(c.toDataURL('image/png'))).arrayBuffer();
    type = 'png';
  }
  return new ImageRun({ type, data, transformation: { width: w, height: h } });
}

async function inline(nodes, extra) {
  const parts = runsOf(nodes, extra);
  const out = [];
  for (const p of parts) out.push(p && p.type === 'image' ? await imageRun(p.attrs.src, p.attrs) : p);
  return out;
}

class Writer {
  constructor() { this.listCount = 0; }

  async blocks(nodes, ctx = {}) {
    const out = [];
    for (const n of nodes || []) out.push(...await this.block(n, ctx));
    return out;
  }

  para(children, n, ctx, more = {}) {
    const a = n.attrs || {};
    return new Paragraph({
      children,
      alignment: ALIGN[a.textAlign],
      ...(ctx.quote ? { indent: { left: 360 }, border: { left: { style: BorderStyle.SINGLE, size: 18, color: 'D1D1D6', space: 10 } } } : {}),
      ...more,
    });
  }

  async block(n, ctx) {
    const a = n.attrs || {};
    switch (n.type) {
      case 'paragraph':
        return [this.para(await inline(n.content), n, ctx, ctx.list || {})];
      case 'heading':
        return [this.para(await inline(n.content), n, ctx, { heading: HEADINGS[a.level] || HeadingLevel.HEADING_1 })];
      case 'image':
        return [new Paragraph({ children: [await imageRun(a.src, a)], alignment: ALIGN[a.textAlign] })];
      case 'horizontalRule':
        return [new Paragraph({ children: [], border: { bottom: LINE } })];
      case 'codeBlock': {
        const lines = (n.content || []).map((t) => t.text || '').join('').split('\n');
        return lines.map((l) => new Paragraph({
          children: [new TextRun({ text: l || ' ', font: 'Consolas', size: 20 })],
          shading: { type: ShadingType.CLEAR, fill: 'F2F2F7', color: 'auto' }, spacing: { after: 0 },
        }));
      }
      case 'blockquote':
        return this.blocks(n.content, { ...ctx, quote: true });
      case 'bulletList':
      case 'orderedList':
      case 'taskList': {
        const level = ctx.level == null ? 0 : ctx.level + 1;
        const instance = n.type === 'orderedList' ? ++this.listCount : 0;
        const out = [];
        for (const item of n.content || []) {
          const [first, ...rest] = item.content || [];
          const list = n.type === 'bulletList' ? { numbering: { reference: 'bullets', level } }
            : n.type === 'orderedList' ? { numbering: { reference: 'numbers', level, instance } }
              : { indent: { left: 360 * (level + 1) } };
          if (first) {
            const runs = await inline(first.content);
            if (n.type === 'taskList') runs.unshift(new TextRun({ text: item.attrs?.checked ? '☑ ' : '☐ ' }));
            out.push(this.para(runs, first, ctx, list));
          }
          out.push(...await this.blocks(rest, { ...ctx, level }));
        }
        return out;
      }
      case 'table':
        return [await this.table(n), new Paragraph({ children: [] })];
      default:
        return n.content ? this.blocks(n.content, ctx) : [];
    }
  }

  async table(n) {
    const rows = [];
    for (const r of n.content || []) {
      const cells = [];
      for (const c of r.content || []) {
        const a = c.attrs || {};
        const kids = await this.blocks(c.content, {});
        cells.push(new TableCell({
          children: kids.length ? kids : [new Paragraph({ children: [] })],
          columnSpan: a.colspan > 1 ? a.colspan : undefined,
          rowSpan: a.rowspan > 1 ? a.rowspan : undefined,
          shading: c.type === 'tableHeader' ? { type: ShadingType.CLEAR, fill: 'F2F2F7', color: 'auto' } : undefined,
        }));
      }
      const head = (r.content || []).length > 0 && r.content.every((c) => c.type === 'tableHeader');
      rows.push(new TableRow(head ? { children: cells, tableHeader: true } : { children: cells }));
    }
    const B = { style: BorderStyle.SINGLE, size: 4, color: 'D1D1D6' };
    return new Table({ rows, width: { size: 100, type: WidthType.PERCENTAGE },
      borders: { top: B, bottom: B, left: B, right: B, insideHorizontal: B, insideVertical: B } });
  }
}

const levels = (fmt) => Array.from({ length: 9 }, (_, level) => ({
  level, format: fmt === 'bullet' ? LevelFormat.BULLET : [LevelFormat.DECIMAL, LevelFormat.LOWER_LETTER, LevelFormat.LOWER_ROMAN][level % 3],
  text: fmt === 'bullet' ? ['•', '◦', '▪'][level % 3] : `%${level + 1}.`,
  alignment: AlignmentType.LEFT,
  style: { paragraph: { indent: { left: 360 * (level + 1), hanging: 260 } } },
}));

export async function docxFromJson(json, title) {
  const children = await new Writer().blocks(json.content);
  const doc = new Document({
    title,
    creator: 'Collider',
    styles: { default: { document: { run: { font: 'Calibri', size: 24 } } } },
    numbering: { config: [{ reference: 'bullets', levels: levels('bullet') }, { reference: 'numbers', levels: levels('number') }] },
    sections: [{
      properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, bottom: 1440, left: 1260, right: 1260 } } },
      children: children.length ? children : [new Paragraph({ children: [] })],
    }],
  });
  return Packer.toBlob(doc);
}
