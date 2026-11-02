// Made by Claude (2026-10-23). Collider online's storage: GET and PUT /o/<name> on the R2 bucket collider-data.
// Answers only requests carrying the key (header X-Key) that matches the secret STORE_KEY.
export default {
  async fetch(req, env) {
    const key = req.headers.get("X-Key") || "";
    if (!env.STORE_KEY || key !== env.STORE_KEY) return new Response("", { status: 404 });
    const url = new URL(req.url);
    if (!url.pathname.startsWith("/o/")) return new Response("", { status: 404 });
    const name = decodeURIComponent(url.pathname.slice(3));
    if (!name) return new Response("", { status: 404 });
    if (req.method === "GET") {
      const obj = await env.STORE.get(name);
      if (!obj) return new Response("", { status: 404 });
      return new Response(obj.body, { headers: { "Content-Type": "application/octet-stream" } });
    }
    if (req.method === "PUT") {
      await env.STORE.put(name, req.body);
      return new Response("ok");
    }
    return new Response("", { status: 405 });
  },
};
