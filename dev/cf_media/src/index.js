// Made by Claude (2026-10-21). Serves the wallpapers, live wallpapers and songs in the collider-themes store from
// Cloudflare's edge, with the instruction to keep them: a file never changes under its name, so a phone or PC that has
// fetched it once keeps it for a year and does not download it again. Video and songs answer byte ranges, which
// Safari needs to play them. (The store's own public address, r2.dev, is slow, limited and kept by no cache.)
// GET /<name as listed by collider-themes>
const KEEP = 'public, max-age=31536000, immutable';

export default {
  async fetch(request, env, ctx) {
    const cors = { 'Access-Control-Allow-Origin': '*', 'Access-Control-Expose-Headers': 'Content-Length, Content-Range, ETag' };
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: { ...cors, 'Access-Control-Allow-Methods': 'GET, HEAD, OPTIONS', 'Access-Control-Allow-Headers': '*' } });
    }
    if (request.method !== 'GET' && request.method !== 'HEAD') return new Response('', { status: 405, headers: cors });
    const key = decodeURIComponent(new URL(request.url).pathname.slice(1));
    if (!key) return new Response('', { status: 404, headers: cors });

    const ranged = request.headers.has('Range');
    const cache = caches.default;
    if (!ranged && request.method === 'GET') {
      const hit = await cache.match(request);
      if (hit) return hit;
    }
    const obj = request.method === 'HEAD'
      ? await env.BUCKET.head(key)
      : await env.BUCKET.get(key, { range: request.headers, onlyIf: request.headers });
    if (!obj) return new Response('', { status: 404, headers: cors });

    const headers = new Headers(cors);
    obj.writeHttpMetadata(headers);
    headers.set('ETag', obj.httpEtag);
    headers.set('Cache-Control', KEEP);
    headers.set('Accept-Ranges', 'bytes');
    if (request.method === 'HEAD') {
      headers.set('Content-Length', String(obj.size));
      return new Response(null, { headers });
    }
    if (!('body' in obj)) return new Response(null, { status: 304, headers });
    if (ranged && obj.range) {
      const off = obj.range.offset ?? 0;
      const len = obj.range.length ?? obj.size - off;
      headers.set('Content-Range', `bytes ${off}-${off + len - 1}/${obj.size}`);
      headers.set('Content-Length', String(len));
      return new Response(obj.body, { status: 206, headers });
    }
    headers.set('Content-Length', String(obj.size));
    const res = new Response(obj.body, { headers });
    if (obj.size < 100 * 1024 * 1024) ctx.waitUntil(cache.put(request, res.clone()));
    return res;
  },
};
