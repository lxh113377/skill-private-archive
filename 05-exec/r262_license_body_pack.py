# -*- coding: utf-8 -*-
"""license body pack (R261-6, landed r262).

Why this file exists: the compat leg read only the GitHub license.spdx_id field, and that field
lies. Measured r261 (C2 human-read batch, reproduced with gh api): langgenius/dify reports
NOASSERTION while its LICENSE is a *modified* Apache 2.0 that additionally requires a commercial
licence for multi-tenant use; Imbad0202/academic-research-skills reports NOASSERTION while its
text is CC BY-NC 4.0. Those are exactly the repos that look usable and rank to rank0.

Why a TRACKED pack instead of relying on _temp cache: _temp/ is gitignored, so a clone would
have no body evidence and the score would silently fall back to the lying API field. That is the
third-generation always-red/unmeasurable trap I hit twice this session (gate 111 reproduce leg,
deadlink gate surface) - see 06-constraints.part20 D-A.

Single source: the rule lives in r114_replacement_scan.classify_body(). This script only fetches
and writes; it never re-implements classification (R260-5: read the implementation first).

Exit codes match run_gates: 0 wrote a pack / 1 no usable evidence / 2 input face missing.
"""
import base64
import io
import json
import os
import sys
import time
from hashlib import sha256

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import r114_replacement_scan as R

MATRIX = os.path.join(ROOT, "06-benchmark", "r261_matrix_licensed.json")
OUT = os.path.join(ROOT, "06-benchmark", "license_body_r262.json")


def targets_from(matrix_path):
    """Repos needing a body check = emitted candidates whose API field is NOASSERTION or empty.

    Those are precisely the shapes the two known lies came from. Repos whose field already says
    MIT/AGPL are not re-read here: it costs an API call and the field classifies them the same way
    the body would (verified on the 20-repo face below).
    """
    d = json.load(io.open(matrix_path, encoding="utf-8-sig"))
    return sorted({c["repo"] for r in d["rows"] for c in (r.get("candidates") or [])
                   if (c.get("license") or "").upper() in ("NOASSERTION", "")})


FACE_FILES = ["r261_matrix_licensed.json", "r262_matrix_bodied.json"]


def targets_union(root_dir=ROOT):
    """Union of NOASSERTION/empty-field repos across every matrix generation on disk.

    Why not just the current face: the pack is cumulative evidence. Building it from one face
    only would let a later run silently SHRINK it (repos that were in r261 but are gone from
    r262 would disappear), and those slots would then fall back to the lying API field with no
    red anywhere. Union + merge (below) keeps the evidence monotonic.
    """
    out = set()
    seen = []
    for name in FACE_FILES:
        p = os.path.join(root_dir, "06-benchmark", name)
        if not os.path.isfile(p):
            continue
        seen.append(name)
        try:
            out.update(targets_from(p))
        except Exception as exc:
            print("  [BODY-PACK] face %s unreadable: %r" % (name, exc))
    return sorted(out), seen

def build_pack(matrix_path=MATRIX, out_path=OUT, quiet=False):
    """Fetch bodies, classify via the single-source rule, write the tracked pack atomically."""
    if not os.path.isfile(matrix_path):
        print("[BODY-PACK:UNVERIFIED] matrix face missing: %s (R247)" % matrix_path)
        return 2
    tg, faces = targets_union()
    if not tg:
        print("[BODY-PACK:UNVERIFIED] NOASSERTION target face empty")
        return 2
    # Merge into the existing pack: already-fetched evidence is never dropped, and only repos
    # missing from the pack get fetched. Prevents a later matrix generation from silently
    # shrinking the pack and sending classified slots back to the API field.
    repos = {}
    if os.path.isfile(out_path):
        try:
            prev = json.load(io.open(out_path, encoding='utf-8-sig'))
            repos = dict(prev.get('repos') or {})
        except Exception as exc:
            print('  [BODY-PACK] existing pack unreadable: %r' % (exc,))
    todo = [x for x in tg if x not in repos]
    faces_j = ",".join(faces)
    print('  [BODY-PACK] union=%d already=%d to_fetch=%d faces=%s'
          % (len(tg), len(tg) - len(todo), len(todo), faces_j))
    for full in todo:
        o, e = R.gh(["api", "repos/%s/license" % full])
        time.sleep(R.CORE_SLEEP)
        if e:
            # "no body" stays explicit so the loader cannot read it as permissive.
            repos[full] = {"state": "UNAVAILABLE", "error": e[:120]}
            if not quiet:
                print("  %-44s UNAVAILABLE %s" % (full, e[:60]))
            continue
        try:
            ld = json.loads(o)
            blob = base64.b64decode(ld.get("content") or "")[:6144]
        except Exception as exc:
            repos[full] = {"state": "UNAVAILABLE", "error": "parse:%r" % (exc,)}
            continue
        up = blob.decode("utf-8-sig", "replace").upper()
        spdx_, cls, hits = R.classify_body(up)
        repos[full] = {"state": "OK", "license_body_class": cls,
                       "license_body_spdx": spdx_ or "",
                       "license_body_path": ld.get("path") or "",
                       "restricted_phrases": hits,
                       "sha8_head": sha256(blob).hexdigest()[:8],
                       "bytes_read": len(blob)}
        if not quiet:
            print("  %-44s %-9s %-26s %s" % (full, cls, spdx_ or "-", ",".join(hits)[:28]))
    n_ok = sum(1 for v in repos.values() if v.get("state") == "OK")
    if n_ok == 0:
        print("[BODY-PACK:FAIL] 0/%d 仓取到正文 ⇒ 不落盘空包（R247）" % len(repos))
        return 1
    doc = {"schema": "license-body-pack-v1",
           "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
           "provenance_cmd": "python 05-exec/r262_license_body_pack.py",
           "rule": "R261-6: API license.spdx_id lies for NOASSERTION repos; read the body",
           "classifier": "05-exec/r114_replacement_scan.py::classify_body (single source)",
           "matrix_face": os.path.relpath(matrix_path, ROOT),
           "targets_n": len(tg), "ok_n": n_ok, "faces": faces, "repos": repos}
    tmp = out_path + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, out_path)
    print("[BODY-PACK:OK] %d/%d 仓有正文证据 -> %s" % (
          n_ok, len(repos), os.path.relpath(out_path, ROOT)))
    return 0


def main():
    import argparse
    ap = argparse.ArgumentParser(prog="r262_license_body_pack.py")
    ap.add_argument("--matrix", default=MATRIX)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()
    return build_pack(a.matrix, a.out, a.quiet)


if __name__ == "__main__":
    sys.exit(main())
