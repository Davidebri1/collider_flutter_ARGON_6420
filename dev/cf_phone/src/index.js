// Made by Claude (2026-10-21). GET /<key> forwards to Collider's current address, key included.
// POST /set with "Authorization: Key <key>" and {"url": "https://....trycloudflare.com"} records a new address.
function same(a, b) {
  if (!a || !b || a.length !== b.length) return false;
  let d = 0;
  for (let i = 0; i < a.length; i++) d |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return d === 0;
}

export default {
  async fetch(request, env) {
    const key = env.PHONE_KEY || '';
    const url = new URL(request.url);
    if (request.method === 'POST' && url.pathname === '/set') {
      if (!same(request.headers.get('Authorization') || '', 'Key ' + key)) return new Response('', { status: 403 });
      let b;
      try { b = await request.json(); } catch { return new Response('', { status: 400 }); }
      // Collider online (Hugging Face) is the link's home (Claude, 2026-10-23); a PC's tunnel only fills in without it.
      const ONLINE = /^https:\/\/[a-z0-9-]+\.(hf\.space|onrender\.com)$/;
      const hosted = ONLINE.test(b.url || '');
      if (!hosted && !/^https:\/\/[a-z0-9-]+\.trycloudflare\.com$/.test(b.url || '')) return new Response('', { status: 400 });
      const now = (await env.COLLIDER_PHONE.get('target')) || '';
      if (!hosted && ONLINE.test(now)) return new Response('{"ok":true,"kept":"online"}', { headers: { 'Content-Type': 'application/json' } });
      await env.COLLIDER_PHONE.put('target', b.url);
      return new Response('{"ok":true}', { headers: { 'Content-Type': 'application/json' } });
    }
    if (request.method === 'GET' && same(url.pathname.slice(1), key)) {
      const target = await env.COLLIDER_PHONE.get('target');
      if (!target) return new Response('', { status: 503 });
      return new Response('', { status: 302, headers: { Location: target + '/?k=' + encodeURIComponent(key), 'Cache-Control': 'no-store' } });
    }
    return new Response('', { status: 404 });
  },
  // Every ten minutes: a visit to Collider online, so a host that rests when unused never rests (Claude, 2026-10-23).
  async scheduled(event, env, ctx) {
    const target = await env.COLLIDER_PHONE.get('target');
    if (target && !/trycloudflare/.test(target)) ctx.waitUntil(fetch(target + '/', { method: 'HEAD' }).catch(() => {}));
  },
};
