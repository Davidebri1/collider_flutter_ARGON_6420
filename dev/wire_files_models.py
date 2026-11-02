# Made by Claude (2026-10-20). One-time edit: Files remembers which model made each generated file.
import os
root = os.path.join(os.path.dirname(__file__), "..")


def edit(rel, pairs):
    p = os.path.join(root, rel)
    s = open(p, encoding="utf-8").read()
    for a, b in pairs:
        if s.count(a) != 1:
            raise SystemExit(f"{rel}: expected one of {a!r}, found {s.count(a)}")
        s = s.replace(a, b)
    open(p, "w", encoding="utf-8", newline="").write(s)


edit("tools/collider_files.py", [
    ("    def listing(self):\n        out = {}\n",
     "    # Which model made each generated file, kept beside the folders (not in them) so it is never listed.\n"
     "    def _models_path(self):\n"
     "        return os.path.join(self.root, \".models.json\")\n\n"
     "    def _models(self):\n"
     "        try:\n"
     "            return json.load(open(self._models_path(), encoding=\"utf-8\"))\n"
     "        except Exception:\n"
     "            return {}\n\n"
     "    def _remember(self, name, model):\n"
     "        if not model:\n"
     "            return\n"
     "        m = self._models()\n"
     "        m[name] = model\n"
     "        tmp = self._models_path() + \".tmp\"\n"
     "        with open(tmp, \"w\", encoding=\"utf-8\") as f:\n"
     "            json.dump(m, f, indent=1)\n"
     "        os.replace(tmp, self._models_path())\n\n"
     "    @staticmethod\n"
     "    def _guess(name, labels):\n"
     "        \"\"\"Files saved before the model was recorded carry its name: \\\"<model> - ...\\\" or \\\"... - <model>.md\\\".\"\"\"\n"
     "        stem = os.path.splitext(name)[0]\n"
     "        for lab in sorted(labels, key=len, reverse=True):\n"
     "            if stem.startswith(lab + \" - \") or stem.endswith(\" - \" + lab):\n"
     "                return lab\n"
     "        return \"\"\n\n"
     "    def listing(self, labels=()):\n"
     "        out = {}\n"
     "        made_by = self._models()\n"),
    ("            for n in os.listdir(d):\n                p = os.path.join(d, n)\n                if os.path.isfile(p):\n",
     "            for n in os.listdir(d):\n                p = os.path.join(d, n)\n                if os.path.isfile(p) and not n.startswith(\".\") and n.lower() != \"desktop.ini\":\n"),
    ("\"kind\": self.kind(n), \"url\": f\"/files/{s}/{urllib.request.quote(n)}\"})",
     "\"kind\": self.kind(n), \"url\": f\"/files/{s}/{urllib.request.quote(n)}\",\n"
     "                                 \"model\": (made_by.get(n) or self._guess(n, labels)) if s == \"generated\" else \"\"})"),
    ("    def save_generated(self, name, text):\n        p = self.unique_path(\"generated\", name)\n        with open(p, \"w\", encoding=\"utf-8\") as f:\n            f.write(text)\n        return os.path.basename(p)\n",
     "    def save_generated(self, name, text, model=\"\"):\n        p = self.unique_path(\"generated\", name)\n        with open(p, \"w\", encoding=\"utf-8\") as f:\n            f.write(text)\n"
     "        self._remember(os.path.basename(p), model)\n        return os.path.basename(p)\n"),
    ("    def save_bytes(self, name, b64, replace=\"\"):\n        p = self._target(name, replace)\n        with open(p, \"wb\") as f:\n            f.write(base64.b64decode(b64))\n        return os.path.basename(p)\n",
     "    def save_bytes(self, name, b64, replace=\"\", model=\"\"):\n        p = self._target(name, replace)\n        with open(p, \"wb\") as f:\n            f.write(base64.b64decode(b64))\n"
     "        self._remember(os.path.basename(p), model)\n        return os.path.basename(p)\n"),
    ("    def print_pdf(self, name, html, replace=\"\"):", "    def print_pdf(self, name, html, replace=\"\", model=\"\"):"),
    ("            shutil.copyfile(out, p)\n        return os.path.basename(p)\n",
     "            shutil.copyfile(out, p)\n        self._remember(os.path.basename(p), model)\n        return os.path.basename(p)\n"),
])

edit("tools/collider_server.py", [
    ("            return self._json(FILES.listing())", "            return self._json(FILES.listing(list(LABEL.values())))"),
    ("report_text(r[\"text\"], job.get(\"sources\")))", "report_text(r[\"text\"], job.get(\"sources\")), LABEL.get(mid, mid))"),
    ("FILES.save_generated(b.get(\"name\", \"note.md\"), b.get(\"text\", \"\"))", "FILES.save_generated(b.get(\"name\", \"note.md\"), b.get(\"text\", \"\"), b.get(\"model\", \"\"))"),
    # Documents' own saves are grouped under Documents, the app that made them.
    ("FILES.save_bytes(b.get(\"name\", \"document.docx\"), b.get(\"b64\", \"\"), b.get(\"replace\", \"\"))",
     "FILES.save_bytes(b.get(\"name\", \"document.docx\"), b.get(\"b64\", \"\"), b.get(\"replace\", \"\"), \"Documents\")"),
    ("FILES.print_pdf(b.get(\"name\", \"document.pdf\"), b.get(\"html\", \"\"), b.get(\"replace\", \"\"))",
     "FILES.print_pdf(b.get(\"name\", \"document.pdf\"), b.get(\"html\", \"\"), b.get(\"replace\", \"\"), \"Documents\")"),
])
print("ok")
