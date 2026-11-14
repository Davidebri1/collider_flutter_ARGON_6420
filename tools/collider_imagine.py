# E.D. — Collider — Signed: Gemini 4 Argon (2026-10-24)
"""Making pictures for Discover Market.

Discover Market is strictly Images-Only per PRD 4 (R27, D2).
A picture is requested from the configured providers in priority order
(discover_market_image_generation > image_provider_priority_order):
  Cloudflare  FLUX.2 Klein 4B / Dev / Schnell through Collider's Worker (dev/cf_imagine), up to 2048px on the long side,
              free each day up to Cloudflare's daily allowance; takes up to four reference pictures.
  NVIDIA      FLUX.1 Dev, up to 1344px on the long side, on the NVIDIA keys.
  fal         2K high-resolution image generation ($0.08 at 2K medium).
Everything made is saved in Files > Generated under the model that made it and listed in data\\imagine.json, newest first.
"""
import base64, concurrent.futures as cf, io, json, os, random, re, threading, time, urllib.error, urllib.request, uuid

QUEUE = "https://queue.fal.run/"
NVIDIA_GENAI = "https://ai.api.nvidia.com/v1/genai/"
UA = {"User-Agent": "Collider/1.0"}

DEFAULTS = {
    "image_provider_priority_order": ["Cloudflare", "NVIDIA", "fal"],
    "cloudflare_flux_model_id": "@cf/black-forest-labs/flux-2-klein-4b",
    "nvidia_flux_model_id": "black-forest-labs/flux.1-dev",
    "fal_image_model_id": "xai/grok-imagine-image/v2.0/text-to-image",
    "default_images_per_prompt_count": 4,
    "default_image_aspect_ratio": "9:16",
    "fal_image_resolution_tier": "2k",
    "fal_image_quality_tier": "medium",
    "max_image_generation_wait_timeout_seconds": 600,
}

# Each model's display name for Files > Generated and Discover Market.
LABELS = {
    "@cf/black-forest-labs/flux-2-klein-4b": "FLUX.2 Klein 4B",
    "@cf/black-forest-labs/flux-2-klein-9b": "FLUX.2 Klein 9B",
    "@cf/black-forest-labs/flux-2-dev": "FLUX.2 Dev",
    "@cf/black-forest-labs/flux-1-schnell": "FLUX.1 Schnell",
    "black-forest-labs/flux.1-dev": "FLUX.1 Dev",
    "xai/grok-imagine-image/v2.0/text-to-image": "FLUX / Studio 2K",
}

CF_SIZE = {"9:16": (1152, 2048), "16:9": (2048, 1152), "1:1": (2048, 2048), "3:4": (1536, 2048), "4:3": (2048, 1536)}
NV_SIZE = {"9:16": (768, 1344), "16:9": (1344, 768), "1:1": (1024, 1024), "3:4": (896, 1152), "4:3": (1152, 896)}

_lock = threading.Lock()


def label(model):
    p, _, rest = model.partition(":")
    model = rest if p in ("Cloudflare", "NVIDIA", "fal") else model
    return LABELS.get(model) or model.split("/")[-1]


def normalize_imagine_settings(raw):
    raw = raw or {}
    return {
        "image_provider_priority_order": list(raw.get("image_provider_priority_order") or raw.get("providers") or DEFAULTS["image_provider_priority_order"]),
        "cloudflare_flux_model_id": str(raw.get("cloudflare_flux_model_id") or raw.get("cloudflare_model") or DEFAULTS["cloudflare_flux_model_id"]),
        "nvidia_flux_model_id": str(raw.get("nvidia_flux_model_id") or raw.get("nvidia_model") or DEFAULTS["nvidia_flux_model_id"]),
        "fal_image_model_id": str(raw.get("fal_image_model_id") or raw.get("image_model") or DEFAULTS["fal_image_model_id"]),
        "default_images_per_prompt_count": int(raw.get("default_images_per_prompt_count") or raw.get("pictures") or DEFAULTS["default_images_per_prompt_count"]),
        "default_image_aspect_ratio": str(raw.get("default_image_aspect_ratio") or raw.get("aspect_ratio") or DEFAULTS["default_image_aspect_ratio"]),
        "fal_image_resolution_tier": str(raw.get("fal_image_resolution_tier") or raw.get("image_resolution") or DEFAULTS["fal_image_resolution_tier"]),
        "fal_image_quality_tier": str(raw.get("fal_image_quality_tier") or raw.get("image_quality") or DEFAULTS["fal_image_quality_tier"]),
        "max_image_generation_wait_timeout_seconds": int(raw.get("max_image_generation_wait_timeout_seconds") or raw.get("deadline_seconds") or DEFAULTS["max_image_generation_wait_timeout_seconds"]),
    }


class Imagine:
    def __init__(self, data_dir, files, rows, settings):
        self.path = os.path.join(data_dir, "imagine.json")
        self.files = files
        self.rows = rows
        self.settings = settings
        self._turn = {}

    def _load(self):
        try:
            return json.load(open(self.path, encoding="utf-8"))
        except Exception:
            return []

    def _save(self, items):
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(items, f, indent=1)
        os.replace(tmp, self.path)

    def _update(self, cid, **changes):
        with _lock:
            items = self._load()
            for it in items:
                if it["id"] == cid:
                    it.update(changes)
            self._save(items)

    def listing(self):
        with _lock:
            return self._load()

    def models(self):
        """The picture models that can be used now (their provider has a key), in the configuration's priority order."""
        s = self._s()
        out = []
        for p in s["image_provider_priority_order"]:
            rs = self.rows(p)
            if not rs:
                continue
            if p == "Cloudflare":
                raw_m = rs[0].get("extra_model_ids") or rs[0].get("models") or s["cloudflare_flux_model_id"]
                ids = [m.strip() for m in raw_m.split(",") if m.strip()]
            elif p == "NVIDIA":
                ids = [s["nvidia_flux_model_id"]]
            else:
                ids = [s["fal_image_model_id"]]
            out += [{"id": f"{p}:{m}", "label": label(m), "provider": p} for m in ids]
        return out

    def _s(self):
        return normalize_imagine_settings(self.settings())

    def start(self, text, kind="image", from_id=None, replace=None, model=None, references=None, aspect=None, count=None):
        if replace:
            self.remove(replace)
        text = (text or "").strip()
        if not text:
            raise ValueError("no words")
        cid = uuid.uuid4().hex[:12]
        item = {"id": cid, "kind": "image", "text": text, "status": "making",
                "created": time.time(), "from": from_id, "media": [], "model": model or "",
                "references": list(references or []), "aspect": aspect or "", "count": int(count or 0)}
        with _lock:
            items = self._load()
            items.insert(0, item)
            self._save(items)
        threading.Thread(target=self._run, args=(cid, item), daemon=True).start()
        return item

    def _key(self, provider):
        rs = self.rows(provider)
        if not rs:
            return None
        self._turn[provider] = (self._turn.get(provider, -1) + 1) % len(rs)
        return rs[self._turn[provider]]

    def _refs(self, item, small):
        out = []
        for ref in item.get("references") or []:
            try:
                src, name = ref.split("/", 1)
                p = self.files.path_for(src, name)
                if not p:
                    continue
                from PIL import Image
                im = Image.open(p).convert("RGB")
                im.thumbnail((small - 1, small - 1))
                buf = io.BytesIO()
                im.save(buf, "JPEG", quality=92)
                out.append(base64.b64encode(buf.getvalue()).decode())
            except Exception as e:
                print("reference", ref, e)
        return out

    def _run(self, cid, item):
        s = self._s()
        text = item["text"]
        try:
            chosen = item.get("model") or ""
            order = ([chosen] if chosen else []) + [f"{p}:" for p in s["image_provider_priority_order"] if not chosen.startswith(p + ":")]
            found, model, last = None, "", ""
            for choice in order:
                provider, _, m = choice.partition(":")
                try:
                    found, model = self._pictures(s, provider, m, item)
                    if found:
                        model = f"{provider}:{model}"
                        break
                except Exception as e:
                    last = f"{provider}: {str(e)[:120]}"
                    print("pictures", last)
            if not found:
                raise RuntimeError(last or "no provider")
            media = []
            stem = re.sub(r"[^\w\- ]", "", text)[:48].strip() or "Picture"
            for n, (data, ext, w, h, remote) in enumerate(found):
                name = self.files.save_media(f"{stem}{'' if n == 0 else f' {n + 1}'}{ext}", data, label(model))
                media.append({"name": name, "url": f"/files/generated/{urllib.request.quote(name)}", "remote": remote,
                              "kind": "image", "width": w, "height": h})
            self._update(cid, status="done", media=media, model=model, label=label(model))
        except Exception as e:
            self._update(cid, status="failed", error=str(e)[:160])

    @staticmethod
    def _some(one, n):
        got, err, missed = [], None, 0
        with cf.ThreadPoolExecutor(n) as pool:
            for f in [pool.submit(one, i) for i in range(n)]:
                try:
                    got.append(f.result())
                except Exception as e:
                    err, missed = err or e, missed + 1
        for i in range(missed if got else 0):
            try:
                got.append(one(i))
            except Exception:
                pass
        if not got and err:
            raise err
        return got

    def _pictures(self, s, provider, model, item):
        n = max(1, min(int(item.get("count") or s["default_images_per_prompt_count"]), 8))
        aspect = item.get("aspect") or s["default_image_aspect_ratio"]
        if provider == "Cloudflare":
            row = self._key("Cloudflare")
            if not row:
                return None, ""
            ep = row.get("api_endpoint_url") or row.get("endpoint") or ""
            key = (row.get("api_key") or row.get("key") or "").strip()
            model = model or s["cloudflare_flux_model_id"]
            w, h = CF_SIZE.get(aspect, CF_SIZE["9:16"])
            refs = self._refs(item, 512)

            def one(_):
                body = {"model": model, "prompt": item["text"], "width": w, "height": h, "seed": random.randint(1, 2**31 - 1),
                        "references": refs}
                req = urllib.request.Request(ep, data=json.dumps(body).encode(), headers={
                    "Content-Type": "application/json", "Authorization": "Key " + key, **UA})
                try:
                    with urllib.request.urlopen(req, timeout=180) as r:
                        data = r.read()
                        ext = ".jpg" if "jpeg" in (r.headers.get("Content-Type") or "") else ".png"
                except urllib.error.HTTPError as e:
                    raise RuntimeError(f"{e.code} {e.read()[:160].decode('utf-8', 'replace')}")
                return data, ext, w, h, ""
            return self._some(one, n), model
        if provider == "NVIDIA":
            row = self._key("NVIDIA")
            if not row:
                return None, ""
            key = (row.get("api_key") or row.get("key") or "").strip()
            model = model or s["nvidia_flux_model_id"]
            w, h = NV_SIZE.get(aspect, NV_SIZE["9:16"])

            def one(_):
                body = {"prompt": item["text"], "mode": "base", "cfg_scale": 3.5, "width": w, "height": h,
                        "seed": random.randint(1, 2**31 - 1), "steps": 50}
                req = urllib.request.Request(NVIDIA_GENAI + model, data=json.dumps(body).encode(), headers={
                    "Content-Type": "application/json", "Accept": "application/json",
                    "Authorization": "Bearer " + key, **UA})
                with urllib.request.urlopen(req, timeout=180) as r:
                    art = (json.load(r).get("artifacts") or [{}])[0]
                if art.get("finishReason") not in (None, "SUCCESS"):
                    raise RuntimeError(art.get("finishReason"))
                return base64.b64decode(art["base64"]), ".jpg", w, h, ""
            return self._some(one, n), model
        if provider == "fal":
            row = self._key("fal")
            if not row:
                return None, ""
            key = (row.get("api_key") or row.get("key") or "").strip()
            model = model or s["fal_image_model_id"]
            body = {"prompt": item["text"], "num_images": n, "resolution": s["fal_image_resolution_tier"],
                    "quality": s["fal_image_quality_tier"], "aspect_ratio": aspect, "output_format": "png"}
            out = self._fal(s, model, body, key)
            return [(self._get(i["url"]), os.path.splitext(i["url"].split("?")[0])[1] or ".png", i.get("width"), i.get("height"), i["url"])
                    for i in (out.get("images") or []) if i.get("url")], model
        return None, ""

    def _fal(self, s, model, body, key):
        def call(method, url, b=None):
            req = urllib.request.Request(url, method=method, data=json.dumps(b).encode() if b is not None else None,
                                         headers={"Authorization": "Key " + key, "Content-Type": "application/json",
                                                  "Accept": "application/json", **UA})
            try:
                with urllib.request.urlopen(req, timeout=60) as r:
                    return json.loads(r.read() or b"{}")
            except urllib.error.HTTPError as e:
                detail = e.read()[:200].decode("utf-8", "ignore")
                raise RuntimeError(f"HTTP {e.code} {detail}")
        job = call("POST", QUEUE + model, body)
        status_url = job.get("status_url") or f"{QUEUE}{model}/requests/{job['request_id']}/status"
        result_url = job.get("response_url") or f"{QUEUE}{model}/requests/{job['request_id']}"
        give_up = time.time() + float(s["max_image_generation_wait_timeout_seconds"])
        while True:
            st = call("GET", status_url)
            if st.get("status") == "COMPLETED":
                break
            if st.get("status") in ("FAILED", "ERROR") or time.time() > give_up:
                raise RuntimeError(st.get("status") or "timeout")
            time.sleep(2.0)
        return call("GET", result_url)

    @staticmethod
    def _get(url):
        return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read()

    def remove(self, cid):
        with _lock:
            self._save([it for it in self._load() if it["id"] != cid])
