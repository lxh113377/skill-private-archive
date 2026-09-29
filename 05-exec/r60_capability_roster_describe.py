# -*- coding: utf-8 -*-
r"""r60_capability_roster_describe.py — 第 18 维第二把尺：描述层名册差集（r60）.

存在理由（本轮一手实测）：第一把尺 r60_capability_roster.py 按 **slug 名** 归类，misc 盲区
36.4% 超阈 30% 被判 [ROSTER:BLIND]（rc=2）。根因不是数据少，是**对手的 slug 是隐喻短语**
（`babysit` / `doubt-driven-development` / `ast-grep` / `ccs-align`），名字面里没有类目词。
按本仓既有教训「抽取器失明要先用第二抽取器复算再下结论」，本件换**描述面**再量一次：
  1. 取对手 SKILL.md 的 frontmatter name+description（gh contents API，逐件留档）；
  2. 域归类改按 description 命中，重算盲区占比；
  3. 「本地有没有」不再按名字相等，而是按**本地 439 件的描述语料共享词数**排序，
     输出每条差距项的最近邻本地件与共享词数 —— **不设自动阈值**（R236 补注③：未测两侧
     边界值前不得把参数当判据），阈值交逐条裁定，判据只负责把排序与证据摆出来。

取值：`python 05-exec/r60_capability_roster_describe.py --json 06-benchmark/capability_gap_r60_2026-09-30.json`
退出码：0 = 描述面守恒成立 / 1 = 守恒或取数破 / 2 = 空面或描述面仍盲（UNVERIFIED）。
"""

import argparse
import base64
import io
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import r60_capability_roster as R          # noqa: E402  同源透镜，禁复制第二份分类表

ROSTER_JSON = os.path.join(ROOT, "06-benchmark", "capability_roster_r60_2026-09-30.json")
DESC_CACHE = os.path.join(ROOT, "06-benchmark", "roster_evidence", "descriptions")
LOCAL_ROOTS = [R.AUTHORITY, R.MARKETPLACE]
STOP = set("""the a an and or of to in for on with about using use used uses this that these those
from when while then than into over out up down as it its their they them your you we our not no
all any more most other such can will also via based its it's more
""".split())


def tokens(text):
    return {w for w in re.findall(r"[a-z][a-z0-9+.#/-]{3,}", (text or "").lower()) if w not in STOP}


def parse_desc(body):
    """Robust frontmatter description reader: handles quoted single line, folded '>' and
    literal '|' block scalars. The previous regex used re.S, so '.' crossed newlines and
    two opponent items parsed to the bare scalar marker ('>' / '>-') - an extractor blind
    spot, not a capability gap (feedback: text extractor blindness, re-check with a second
    extractor before concluding)."""
    lines = body.split("\n")
    for i, ln in enumerate(lines):
        m = re.match(r"^description:\s*(.*)$", ln)
        if not m:
            continue
        head = m.group(1).strip()
        if head and head[0] not in ">|":
            return head
        chunk = []
        for nxt in lines[i + 1:]:
            if nxt.strip() == "":
                if chunk:
                    break
                continue
            if not nxt[:1].isspace():
                break
            chunk.append(nxt.strip())
        return " ".join(chunk)
    return ""


def frontmatter(path):
    try:
        text = io.open(path, encoding="utf-8-sig", errors="replace").read(8000)
    except OSError:
        return None
    m = re.search(r"^---\s*\n(.*?)\n---", text, re.S)
    body = m.group(1) if m else text
    nm = re.search(r"^name:\s*(.+)$", body, re.M)
    desc = parse_desc(body) or body
    return {"name": (nm.group(1).strip() if nm else os.path.basename(os.path.dirname(path))),
            "description": re.sub(r"\s+", " ", desc)[:900]}


def gh_get(repo, slug):
    proc = subprocess.run(["gh", "api", "repos/%s/contents/%s/SKILL.md" % (repo, slug),
                           "--jq", ".content"], capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        raise RuntimeError("rc=%s %s" % (proc.returncode, proc.stderr.strip()[:160]))
    return base64.b64decode(proc.stdout.strip()).decode("utf-8", "replace")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", dest="out")
    ap.add_argument("--limit", type=int, default=0, help="只处理前 N 条差距项（0=全部）")
    ap.add_argument("--no-fetch", action="store_true")
    args = ap.parse_args()

    problems = []
    roster = json.loads(io.open(ROSTER_JSON, encoding="utf-8-sig").read())

    # ---- 本地描述语料（三供给根，唯一名去重）
    local = {}
    for root in LOCAL_ROOTS:
        if not os.path.isdir(root):
            problems.append("local root missing: %s" % root)
            continue
        for d in sorted(os.listdir(root)):
            p = os.path.join(root, d, "SKILL.md")
            if d.startswith(".") or not os.path.isfile(p):
                continue
            fm = frontmatter(p)
            if fm and d not in local:
                local[d] = fm
    if not local:
        sys.stderr.write("[GAP:UNVERIFIED] 本地描述语料为空，不得读成「对手全都有我们没有」\n")
        return 2
    local_tok = {k: tokens(v["name"] + " " + v["description"]) for k, v in local.items()}

    # ---- 差集条目 = 第一把尺的 opponent_only（唯一名），其归属仓从 roster 的 repos 反查
    want = {}
    for dom in roster["domains"]:
        for n in dom.get("opponent_only_sample") or []:
            want[n] = dom["domain"]
    # 全量差集需要重算（第一把尺只留 sample），用同源逻辑再取一次唯一名
    name_owner = {}
    for row in roster["repos"]:
        if row["tree_truncated"]:
            continue
        repo = row["repo"]
        ev = os.path.join(R.EVIDENCE_DIR, repo.replace("/", "__") + ".json")
        if not os.path.isfile(ev):
            problems.append("missing tree evidence for %s" % repo)
            continue
        blob = json.loads(io.open(ev, encoding="utf-8-sig").read())
        cats = R.detect_catalog_dirs(blob["slugs"])
        for s in blob["slugs"]:
            if os.path.dirname(s) in cats:
                continue
            name_owner.setdefault(os.path.basename(s.rstrip("/")), []).append(repo)
    opp_names = sorted(name_owner)
    gap_names = [n for n in opp_names if n not in local]
    if args.limit:
        gap_names = gap_names[: args.limit]

    os.makedirs(DESC_CACHE, exist_ok=True)
    items, desc_local = [], {}
    for n in gap_names:
        repo = sorted(set(name_owner[n]))[0]
        cache = os.path.join(DESC_CACHE, (repo.replace("/", "__") + "__" + n) + ".json")
        fm = None
        if os.path.isfile(cache):
            try:
                fm = json.loads(io.open(cache, encoding="utf-8-sig").read())
            except ValueError:
                fm = None
        if fm is None:
            if args.no_fetch:
                problems.append("no cached description for %s@%s" % (n, repo))
                continue
            ev = os.path.join(R.EVIDENCE_DIR, repo.replace("/", "__") + ".json")
            blob = json.loads(io.open(ev, encoding="utf-8-sig").read())
            full = [s for s in blob["slugs"] if os.path.basename(s.rstrip("/")) == n]
            if not full:
                problems.append("slug path not found %s@%s" % (n, repo))
                continue
            try:
                text = gh_get(repo, full[0])
            except Exception as e:                              # noqa: BLE001
                problems.append("fetch %s@%s failed: %s" % (n, repo, e))
                continue
            m = re.search(r"^---\s*\n(.*?)\n---", text, re.S)
            body = m.group(1) if m else text[:1500]
            fm = {"name": n, "repo": repo,
                  "description": (re.sub(r"\s+", " ", parse_desc(body)) or body.strip())[:600]}
            _atomic_write(cache, json.dumps(fm, ensure_ascii=False))
        d = tokens(fm["name"] + " " + fm["description"])
        suspect = len(fm["description"].strip()) < 40
        dom = R.domain_of(fm["description"]) if "misc" == want.get(n, "misc") else want.get(n, "misc")
        scored = sorted(((len(d & lt), k) for k, lt in local_tok.items()), reverse=True)[:3]
        items.append({"slug": n, "repo": fm.get("repo", repo), "domain_by_desc": dom,
                      "description": fm["description"][:300],
                      "desc_suspect": suspect,
                      "retrieval": ('gh api "repos/%s/git/trees/HEAD?recursive=1" --jq '
                                    '\'.tree[]|select(.path|endswith("SKILL.md"))|.path\' '
                                    '; gh api "repos/%s/contents/<path>/SKILL.md" -H '
                                    '"Accept: application/vnd.github.raw"  # %s'
                                    % (repo, repo, n)),
                      "nearest_local": [{"skill": k, "shared_tokens": sc} for sc, k in scored
                                        if sc > 0]})
        desc_local.setdefault(dom, 0)
        desc_local[dom] += 1

    blind2 = (len([i for i in items if i["domain_by_desc"] == "misc"]) / float(len(items))) if items else 1.0
    if not items:
        problems.append("no gap items fetched => empty face")

    doc = {"schema": "capability-gap-r60-v1",
           "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "readonly": True,
           "first_lens": {"artifact": os.path.basename(ROSTER_JSON),
                          "blind_share_misc": roster.get("blind_share_misc"),
                          "verdict_state": roster.get("verdict_state")},
           "claims_face": "对手 SKILL.md frontmatter description 面（600 字截断）；本地面 = 权威源+市场缓存根 "
                          "全部 SKILL.md 的 name+description；匹配度 = 共享英文词集基数，未设自动阈值",
           "counting_unit": "unique slug basename",
           "totals": {"gap_items": len(items), "opponent_unique": len(opp_names),
                      "local_corpus": len(local)},
           "blind_share_misc_desc": round(blind2, 4),
           "domains_desc": sorted(desc_local.items(), key=lambda kv: -kv[1]),
           "items": sorted(items, key=lambda x: -(x["nearest_local"][0]["shared_tokens"]
                                                  if x["nearest_local"] else 0)),
           "problems": problems,
           "note": "shared_tokens 低 = 本地无近邻 = 真差距候选；高 = 我们已有同能力，只是名字不同。"}
    print("第二把尺（描述面）｜ 差距项 %d ｜ 本地语料 %d ｜ 描述面 misc 盲区 %.1f%%"
          % (len(items), len(local), 100 * blind2))
    for it in doc["items"][:20]:
        nn = it["nearest_local"][0] if it["nearest_local"] else None
        print("  tok=%-3s %-34s <- %-30s %s"
              % (nn["shared_tokens"] if nn else 0, it["slug"][:34],
                 (nn["skill"] if nn else "-")[:30], it["description"][:60]))
    if problems:
        print("[GAP:FAIL] " + " ; ".join(problems))
        rc = 1
    elif blind2 > R.BLIND_LIMIT:
        print("[GAP:BLIND] 描述面仍超盲区阈 ⇒ 本维度只到 UNVERIFIED")
        rc = 2
    else:
        print("[GAP:PASS] 描述面盲区在阈内，逐条最近邻已排出")
        rc = 0
    if args.out:
        _atomic_write(args.out, json.dumps(doc, ensure_ascii=False, indent=1))
        print("证据件: %s" % args.out)
    return rc


def _atomic_write(path, text):
    tmp = path + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    os.replace(tmp, path)


if __name__ == "__main__":
    sys.exit(main())
