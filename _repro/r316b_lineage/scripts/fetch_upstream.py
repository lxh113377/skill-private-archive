# -*- coding: utf-8 -*-
'''r316b evidence fetcher - gh api ONLY (per brief: network limited to gh api of these files).

Re-pulls the six upstream/counterpart SKILL.md files into ./evidence so the lineage judgement in
check_r316b.py can be recomputed from fresh bytes. Writes UTF-8 text; prints one line per file
with git blob sha + sha256 so a reader can detect drift against the run of 2026-10-31T19:3x+08.
'''
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EV = os.path.join(os.path.dirname(HERE), "evidence")

# (local filename, repo, path inside repo) - the 3 gstack-repo files + the 2 anthropics docx/pdf
TARGETS = [
    ("gstack_capy_skill.md", "garrytan/gstack", "capy/skill/gstack/SKILL.md"),
    ("gstack_browse_skill.md", "garrytan/gstack", "browse/SKILL.md"),
    ("gstack_root_skill.md", "garrytan/gstack", "SKILL.md"),
    ("anthropic_docx.md", "anthropics/skills", "skills/docx/SKILL.md"),
    ("anthropic_pdf.md", "anthropics/skills", "skills/pdf/SKILL.md"),
]


def fetch(repo, path):
    """gh api contents endpoint -> decoded text, plus the blob sha the API reports."""
    args = ["gh", "api", "repos/%s/contents/%s" % (repo, path), "--jq", ".content"]
    p = subprocess.run(args, capture_output=True, timeout=180)
    if p.returncode != 0:
        raise RuntimeError((p.stderr or b"").decode("utf-8", "replace")[:300])
    meta = json.loads(subprocess.run(args[:-2] + ["--jq", "{sha:.sha,size:.size}"],
                                     capture_output=True, timeout=180).stdout.decode())
    import base64
    return base64.b64decode(p.stdout.decode().strip()).decode("utf-8", "replace"), meta


def main():
    os.makedirs(EV, exist_ok=True)
    rows = []
    for name, repo, path in TARGETS:
        text, meta = fetch(repo, path)
        with open(os.path.join(EV, name), "w", encoding="utf-8") as fh:
            fh.write(text)
        rows.append({"file": name, "repo": repo, "path": path, "blob": meta.get("sha"),
                     "bytes": len(text.encode("utf-8")),
                     "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()})
        print("%s <- %s:%s blob=%s bytes=%s" % (name, repo, path, meta.get("sha"), len(text.encode("utf-8"))))
    with open(os.path.join(EV, "fetch_manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(rows, fh, ensure_ascii=False, indent=1)
    print("[R316G2:FETCH] files=%d manifest=evidence/fetch_manifest.json" % len(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())