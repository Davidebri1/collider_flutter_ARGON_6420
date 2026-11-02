"""Making pictures and videos. Made by Claude (2026-10-20); providers added 2026-10-21.

David, 20 Oct: "discover market should be wired to Fal"; 21 Oct, on which provider makes pictures: "All 3. Especially
a and c" (NVIDIA's FLUX and Cloudflare Workers AI first, fal kept). So a picture is asked of the providers in the
configuration's order (settings > imagine > providers), the first that answers makes it:
  Cloudflare  FLUX.2 klein 4B through David's own Worker (dev/cf_imagine), up to 1920 on the long side, free each day
              up to Cloudflare's daily allowance; takes up to four reference pictures.
  NVIDIA      FLUX.1 dev, up to 1344 on the long side, on the NVIDIA keys.
  fal         Grok Imagine, 2K, paid per picture ($0.08 at 2K medium, Oct 2026); videos only here.
A request may name its model ("Cloudflare:@cf/...", "NVIDIA:black-forest-labs/...", "fal:xai/..."), as the media chat
does; otherwise the order above is used. Everything made is saved in Files > Generated under the model that made it and
listed in data\\imagine.json, newest first.
"""
import base64, concurrent.futures as cf, io, json, os, random, re, threading, time, urllib.error, urllib.request, uuid

QUEUE = "https://queue.fal.run/"
NVIDIA_GENAI = "https://ai.api.nvidia.com/v1/genai/"
UA = {"User-Agent": "Collider/1.0"}

DEFAULTS = {
    "providers": ["Cloudflare", "NVIDIA", "fal"],
    "cloudflare_model": "@cf/black-forest-labs/flux-2-klein-4b",
    "nvidia_model": "black-forest-labs/flux.1-dev",
    "image_model": "xai/grok-imagine-image/v2.0/text-to-image",
    "motion_model": "xai/grok-imagine-video/v1.5/image-to-video",
    "video_model": "xai/grok-imagine-video/v1.5/text-to-video",
    "pictures": 4,
    "image_resolution": "2k",
    "image_quality": "medium",
    "aspect_ratio": "9:16",
    "video_resolution": "1080p",
    "video_seconds": 6,
    "poll_seconds": 2,
    "deadline_seconds": 600,
}

# Each model's own name, for Files > Generated and the media chat.
LABELS = {
    "@cf/black-forest-labs/flux-2-klein-4b": "FLUX.2 klein 4B",
    "@cf/black-forest-labs/flux-2-klein-9b": "FLUX.2 klein 9B",
    "@cf/black-forest-labs/flux-2-dev": "FLUX.2 dev",
    "@cf/black-forest-labs/flux-1-schnell": "FLUX.1 schnell",
    "black-forest-labs/flux.1-dev": "FLUX.1 dev",
    "xai/grok-imagine-image/v2.0/text-to-image": "Grok Imagine",
    "xai/grok-imagine-video/v1.5/image-to-video": "Grok Imagine Video",
    "xai/grok-imagine-video/v1.5/text-to-video": "Grok Imagine Video",
}

# Sizes per shape: Cloudflare's FLUX.2 takes any size to 1920; NVIDIA's FLUX.1 dev takes only these.
# Claude, 2026-10-23: the largest Cloudflare makes (2048 on a side; it refused 1440x2560 and 2160x3840 when tried). A
# 1152x2048 picture costs the same units as the 1080x1920 one it replaces (both are 12 tiles of 512).
CF_SIZE = {"9:16": (1152, 2048), "16:9": (2048, 1152), "1:1": (2048, 2048), "3:4": (1536, 2048), "4:3": (2048, 1536)}
NV_SIZE = {"9:16": (768, 1344), "16:9": (1344, 768), "1:1": (1024, 1024), "3:4": (896, 1152), "4:3": (1152, 896)}

_lock = threading.Lock()


def label(model):
    p, _, rest = model.partition(":")
    model = rest if p in ("Cloudflare", "NVIDIA", "fal") else model  # "Provider:model" ids (Claude, 2026-10-21)
    return LABELS.get(model) or model.split("/")[-1]


class Imagine:
    def __init__(self, data_dir, files, rows, settings):
        """files: collider_files.Files; rows(name): the configuration's rows with keys for a provider; settings(): the
        imagine lines."""
        self.path = os.path.join(data_dir, "imagine.json")
        self.files = files
        self.rows = rows
        self.settings = settings
        self._turn = {}

    # ---------------- the list ----------------
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
        """The picture models that can be used now (their provider has a key), in the configuration's order."""
        s = self._s()
        out = []
        for p in s["providers"]:
            if not self.rows(p):
                continue
            if p == "Cloudflare":
                ids = [m.strip() for m in (self.rows(p)[0].get("models") or s["cloudflare_model"]).split(",") if m.strip()]
            elif p == "NVIDIA":
                ids = [s["nvidia_model"]]
            else:
                ids = [s["image_model"]]
            out += [{"id": f"{p}:{m}", "label": label(m), "provider": p} for m in ids]
        return out

    def _s(self):
        return {**DEFAULTS, **(self.settings() or {})}

    # ---------------- making ----------------
    def start(self, text, kind="image", from_id=None, replace=None, model=None, references=None, aspect=None, count=None):
        """kind: image (pictures from words), video (a video from words), motion (a video from one of the pictures).
        references: Files paths ("source/name") of pictures to make from. replace: a making that failed, tried again."""
        if replace:
            self.remove(replace)
        text = (text or "").strip()
        source = None
        if kind == "motion":
            source = next((it for it in self.listing() if it["id"] == from_id), None)
            if not source or not source.get("media"):
                raise ValueError("no picture")
        elif not text:
            raise ValueError("no words")
        cid = uuid.uuid4().hex[:12]
        item = {"id": cid, "kind": kind, "text": text or (source or {}).get("text", ""), "status": "making",
                "created": time.time(), "from": from_id, "media": [], "model": model or "",
                "references": list(references or []), "aspect": aspect or "", "count": int(count or 0)}
        with _lock:
            items = self._load()
            items.insert(0, item)
            self._save(items)
        threading.Thread(target=self._run, args=(cid, item, source), daemon=True).start()
        return item

    def _key(self, provider):
        rs = self.rows(provider)
        if not rs:
            return None
        self._turn[provider] = (self._turn.get(provider, -1) + 1) % len(rs)
        return rs[self._turn[provider]]

    def _refs(self, item, small):
        """The reference pictures as base64, made smaller than small x small for models that need it."""
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

    def _run(self, cid, item, source):
        s = self._s()
        kind, text = item["kind"], item["text"]
        try:
            if kind != "image":
                found, model = self._fal_video(s, kind, text, source)
            else:
                # the chosen model first; if it cannot make them (its day's allowance used up, its service down), the
                # next makers in line, so a request still comes back with pictures (Claude, 2026-10-21)
                chosen = item.get("model") or ""
                order = ([chosen] if chosen else []) + [f"{p}:" for p in s["providers"] if not chosen.startswith(p + ":")]
                found, model, last = None, "", ""
                for choice in order:
                    provider, _, m = choice.partition(":")
                    try:
                        found, model = self._pictures(s, provider, m, item)
                        if found:
                            model = f"{provider}:{model}"  # kept as the id a retry picks (Claude, 2026-10-21)
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
                              "kind": "video" if ext.lower() in (".mp4", ".webm", ".mov") else "image",
                              "width": w, "height": h})
            self._update(cid, status="done", media=media, model=model, label=label(model))
        except Exception as e:
            self._update(cid, status="failed", error=str(e)[:160])

    # ---------------- providers ----------------
    @staticmethod
    def _some(one, n):
        """Makes n pictures at once and keeps those that came back; fails only when none did. (Claude, 2026-10-21)"""
        got, err, missed = [], None, 0
        with cf.ThreadPoolExecutor(n) as pool:
            for f in [pool.submit(one, i) for i in range(n)]:
                try:
                    got.append(f.result())
                except Exception as e:
                    err, missed = err or e, missed + 1
        for i in range(missed if got else 0):  # one more try each, one at a time, for those a busy service dropped
            try:
                got.append(one(i))
            except Exception:
                pass
        if not got and err:
            raise err
        return got

    def _pictures(self, s, provider, model, item):
        n = max(1, min(int(item.get("count") or s["pictures"]), 8))
        aspect = item.get("aspect") or s["aspect_ratio"]
        if provider == "Cloudflare":
            row = self._key("Cloudflare")
            if not row:
                return None, ""
            model = model or s["cloudflare_model"]
            w, h = CF_SIZE.get(aspect, CF_SIZE["9:16"])
            refs = self._refs(item, 512)

            def one(_):
                body = {"model": model, "prompt": item["text"], "width": w, "height": h, "seed": random.randint(1, 2**31 - 1),
                        "references": refs}
                req = urllib.request.Request(row["endpoint"], data=json.dumps(body).encode(), headers={
                    "Content-Type": "application/json", "Authorization": "Key " + row["key"].strip(), **UA})
                try:
                    with urllib.request.urlopen(req, timeout=180) as r:
                        data = r.read()
                        ext = ".jpg" if "jpeg" in (r.headers.get("Content-Type") or "") else ".png"
                except urllib.error.HTTPError as e:  # the Worker's own words say why
                    raise RuntimeError(f"{e.code} {e.read()[:160].decode('utf-8', 'replace')}")
                return data, ext, w, h, ""
            return self._some(one, n), model
        if provider == "NVIDIA":
            row = self._key("NVIDIA")
            if not row:
                return None, ""
            model = model or s["nvidia_model"]
            w, h = NV_SIZE.get(aspect, NV_SIZE["9:16"])

            def one(_):
                body = {"prompt": item["text"], "mode": "base", "cfg_scale": 3.5, "width": w, "height": h,
                        "seed": random.randint(1, 2**31 - 1), "steps": 50}
                req = urllib.request.Request(NVIDIA_GENAI + model, data=json.dumps(body).encode(), headers={
                    "Content-Type": "application/json", "Accept": "application/json",
                    "Authorization": "Bearer " + row["key"].strip(), **UA})
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
            model = model or s["image_model"]
            body = {"prompt": item["text"], "num_images": n, "resolution": s["image_resolution"],
                    "quality": s["image_quality"], "aspect_ratio": aspect, "output_format": "png"}
            out = self._fal(s, model, body, row["key"].strip())
            return [(self._get(i["url"]), os.path.splitext(i["url"].split("?")[0])[1] or ".png", i.get("width"), i.get("height"), i["url"])
                    for i in (out.get("images") or []) if i.get("url")], model
        return None, ""

    def _fal_video(self, s, kind, text, source):
        row = self._key("fal")
        if not row:
            raise RuntimeError("no fal key")
        if kind == "video":
            model = s["video_model"]
            body = {"prompt": text, "resolution": s["video_resolution"], "duration": int(s["video_seconds"]), "aspect_ratio": s["aspect_ratio"]}
        else:
            model = s["motion_model"]
            body = {"prompt": text or "", "image_url": source["media"][0].get("remote") or "",
                    "resolution": s["video_resolution"], "duration": int(s["video_seconds"])}
        out = self._fal(s, model, body, row["key"].strip())
        v = out.get("video") or {}
        if not v.get("url"):
            raise RuntimeError("no video")
        return [(self._get(v["url"]), ".mp4", v.get("width"), v.get("height"), v["url"])], model

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
        give_up = time.time() + float(s["deadline_seconds"])
        while True:
            st = call("GET", status_url)
            if st.get("status") == "COMPLETED":
                break
            if st.get("status") in ("FAILED", "ERROR") or time.time() > give_up:
                raise RuntimeError(st.get("status") or "timeout")
            time.sleep(float(s["poll_seconds"]))
        return call("GET", result_url)

    @staticmethod
    def _get(url):
        return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read()

    def remove(self, cid):
        """Takes a making off the list. Its files stay in Files > Generated."""
        with _lock:
            self._save([it for it in self._load() if it["id"] != cid])
