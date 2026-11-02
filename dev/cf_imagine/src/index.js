// Made by Claude (2026-10-21). Makes one picture with a Workers AI model and returns it as PNG/JPEG bytes.
// POST JSON {model, prompt, width, height, seed, steps, references: [base64...]} with header "Authorization: Key <COLLIDER_KEY>".
// FLUX.2 models take their input as form data (references as input_image_0..3); the others take JSON.
function b64ToBytes(b64) {
  const bin = atob(b64);
  const bytes = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  return bytes;
}

export default {
  async fetch(request, env) {
    if (request.method !== 'POST') return new Response('', { status: 405 });
    const auth = request.headers.get('Authorization') || '';
    if (!env.COLLIDER_KEY || auth !== 'Key ' + env.COLLIDER_KEY) return new Response('', { status: 403 });
    let b;
    try { b = await request.json(); } catch { return new Response('bad json', { status: 400 }); }
    const model = b.model || '@cf/black-forest-labs/flux-2-klein-4b';
    try {
      let out;
      if (model.includes('flux-2')) {
        const form = new FormData();
        form.append('prompt', String(b.prompt || ''));
        if (b.width) form.append('width', String(b.width));
        if (b.height) form.append('height', String(b.height));
        if (b.seed !== undefined) form.append('seed', String(b.seed));
        if (b.steps && !model.includes('klein')) form.append('steps', String(b.steps));
        (b.references || []).slice(0, 4).forEach((r, i) => form.append('input_image_' + i, new Blob([b64ToBytes(r)])));
        const body = new Response(form);
        out = await env.AI.run(model, { multipart: { body: body.body, contentType: body.headers.get('content-type') } });
      } else {
        const input = { prompt: String(b.prompt || '') };
        // FLUX.1 schnell takes only the words and up to 8 steps; it refuses a size or seed. (Claude, 2026-10-21)
        const keys = model.includes('schnell') ? ['steps'] : ['width', 'height', 'seed', 'steps'];
        for (const k of keys) if (b[k] !== undefined) input[k] = b[k];
        if (model.includes('schnell')) input.steps = Math.min(Number(input.steps) || 8, 8);
        out = await env.AI.run(model, input);
      }
      if (out instanceof ReadableStream) return new Response(out, { headers: { 'Content-Type': 'image/png' } });
      const img = out && (out.image || (out.result && out.result.image));
      if (!img) return new Response(JSON.stringify({ error: 'no image' }), { status: 502 });
      const bytes = b64ToBytes(img);
      const type = bytes[0] === 0xff ? 'image/jpeg' : 'image/png';
      return new Response(bytes, { headers: { 'Content-Type': type } });
    } catch (e) {
      const msg = String((e && e.message) || e).slice(0, 300);
      // the day's free allowance used up: 429, so the app knows to try its next maker
      return new Response(JSON.stringify({ error: msg }), { status: msg.includes('4006') ? 429 : 502 });
    }
  },
};
