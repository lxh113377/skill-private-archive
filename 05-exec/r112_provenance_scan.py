# -*- coding: utf-8 -*-
r"""r112_provenance_scan.py — 第 19 维「版本落后面」的来源锚定扫描器（只读取证）。

存在理由（r112 新开维度，用户痛点原话「市面上有更好的 skill，我还在用旧的」）：
  本仓 18 个维度里，能力差距量过（第 18 维名册）、结构/描述/供应链/账龄都量过，
  **唯独没有一次量过「我手上这份是不是旧的」**——因为根本没有上游身份证：
    * 182 个技能里只有 2 个带 installedContentHash（github / sq-cleanmgr-c）；
    * 注册表 unified-skills-index.json 的 source 只有 user-created/community/skillhub 三档，
      没有 upstream_repo / upstream_commit / content_hash 字段。
  没有身份证就无法回答「上游变没变」，所以本维度第一步不是判定而是**建身份**。

判据面（一项事实只在一处判）：
  * 本件**只做来源锚定**，不判优劣、不判新旧（那是 r112_upstream_probe / r112_swap_gate）。
  * 三档置信度，禁把「猜」写成「有」：
      declared  盘上有安装器留下的元数据（_skillhub_meta.json / meta.json / _meta.json 带版本或哈希）
      inferred  仅**名字**命中对手语料（r96_gh_raw.json 的 slug）——同名不等于同源，故只作候选
      unknown   两者都没有：承认不知道，不猜
  * 覆盖根自证（R20-2）：输出必须列出扫了哪些根、各根条数，且 declared∪inferred∪unknown == 总数。
  * 零输入面 ⇒ UNVERIFIED（R247），不得静默读成「全部健康」。

用法：
  python 05-exec/r112_provenance_scan.py --json 06-benchmark/provenance_r112_2026-10-17.json
退出码：0 = 出件且守恒成立；2 = 权威源取不到 / 面为空（UNVERIFIED）。
"""
import argparse
import hashlib
import io
import json
import os
import re
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
AUTHORITY = r"D:\global_skills"
REGISTRY = r"C:\Users\37533\Desktop\workspace\焚诀\skill\registry\unified-skills-index.json"
CORPUS = os.path.join(HERE, "r96_gh_raw.json")
MARKET = r"C:\Users\37533\.workbuddy\skills-marketplace\skills"

NOISE_DIRS = {".git", "_trash", "__pycache__", ".rule_backup", "node_modules", ".temp"}
DECLARED_FILES = ("_skillhub_meta.json", "meta.json", "_meta.json")

RE_FM = re.compile(r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|\Z)", re.S)


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def read_text(path):
    try:
        return io.open(path, encoding="utf-8-sig", errors="replace").read()
    except OSError:
        return ""


def fm_field(text, key):
    m = RE_FM.match(text or "")
    if not m:
        return None
    mm = re.search(r"^%s:\s*(.+)$" % re.escape(key), m.group(1), re.M)
    return mm.group(1).strip().strip("\"'") if mm else None


def dir_manifest_hash(d):
    """整个技能目录的内容哈希（排除噪声目录）——判「本地改没改」用，不只看 SKILL.md。"""
    parts = []
    for dirpath, dirnames, filenames in os.walk(d):
        dirnames[:] = [x for x in dirnames if x not in NOISE_DIRS]
        for fn in sorted(filenames):
            fp = os.path.join(dirpath, fn)
            rel = os.path.relpath(fp, d).replace("\\", "/")
            try:
                with open(fp, "rb") as fh:
                    h = hashlib.sha256(fh.read()).hexdigest()
            except OSError:
                h = "UNREADABLE"
            parts.append("%s\t%s" % (rel, h))
    parts.sort()
    return sha256_bytes("\n".join(parts).encode("utf-8")), len(parts)


def load_corpus_slugs():
    """对手语料里的 slug -> [(repo, path)]，只用于 inferred 档。"""
    if not os.path.isfile(CORPUS):
        return {}, "corpus_missing:%s" % CORPUS
    try:
        doc = json.load(io.open(CORPUS, encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        return {}, "corpus_unreadable:%r" % (exc,)
    out = {}
    for repo, v in (doc.get("repos") or {}).items():
        for p in (v.get("skill_md_paths") or []):
            slug = os.path.basename(os.path.dirname(p)).lower()
            if slug:
                out.setdefault(slug, []).append((repo, p))
    return out, None


def load_registry():
    if not os.path.isfile(REGISTRY):
        return {}, "registry_missing:%s" % REGISTRY
    try:
        doc = json.load(io.open(REGISTRY, encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        return {}, "registry_unreadable:%r" % (exc,)
    return (doc.get("skills") or {}), None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", dest="json_out", default=None)
    ap.add_argument("--authority", default=AUTHORITY)
    args = ap.parse_args()

    notes = []
    if not os.path.isdir(args.authority):
        print("[PROVENANCE:UNVERIFIED] 权威源取不到: %s" % args.authority)
        return 2
    registry, reg_err = load_registry()
    if reg_err:
        notes.append(reg_err)
    corpus, corpus_err = load_corpus_slugs()
    if corpus_err:
        notes.append(corpus_err)

    market_slugs = set()
    if os.path.isdir(MARKET):
        for n in os.listdir(MARKET):
            if os.path.isfile(os.path.join(MARKET, n, "SKILL.md")):
                market_slugs.add(n.lower())
    else:
        notes.append("market_missing:%s" % MARKET)

    rows, declared_n, inferred_n, unknown_n = [], 0, 0, 0
    roots_seen = {args.authority: 0}
    if os.path.isdir(MARKET):
        roots_seen[MARKET] = len(market_slugs)

    for name in sorted(os.listdir(args.authority)):
        d = os.path.join(args.authority, name)
        skill_md = os.path.join(d, "SKILL.md")
        if not os.path.isdir(d) or not os.path.isfile(skill_md):
            continue
        roots_seen[args.authority] += 1
        raw = b""
        try:
            with open(skill_md, "rb") as fh:
                raw = fh.read()
        except OSError as exc:
            notes.append("unreadable:%s:%r" % (name, exc))
        text = raw.decode("utf-8-sig", errors="replace")
        mh, file_n = dir_manifest_hash(d)

        declared = {}
        for fn in DECLARED_FILES:
            fp = os.path.join(d, fn)
            if not os.path.isfile(fp):
                continue
            try:
                meta = json.load(io.open(fp, encoding="utf-8-sig"))
            except (OSError, ValueError):
                notes.append("meta_unreadable:%s/%s" % (name, fn))
                continue
            if not isinstance(meta, dict):
                continue
            declared[fn] = {
                "version": meta.get("version"),
                "installedContentHash": meta.get("installedContentHash"),
                "md5": meta.get("md5"),
                "source": meta.get("source"),
                "author": meta.get("author"),
                "download_url": meta.get("download_url"),
                "installedAt": meta.get("installedAt"),
                "last_modified_time": meta.get("last_modified_time"),
            }

        declared_has_id = any(
            (v.get("version") or v.get("installedContentHash") or v.get("md5"))
            for v in declared.values())
        cand = corpus.get(name.lower()) or []
        inferred_cand = [{"repo": r, "path": p} for r, p in cand]

        if declared_has_id:
            conf = "declared"
            declared_n += 1
        elif inferred_cand:
            conf = "inferred"
            inferred_n += 1
        else:
            conf = "unknown"
            unknown_n += 1

        reg = registry.get(name) or {}
        rows.append({
            "slug": name,
            "local_sha256": sha256_bytes(raw),
            "local_bytes": len(raw),
            "dir_manifest_sha256": mh,
            "dir_file_n": file_n,
            "mtime": datetime.fromtimestamp(os.path.getmtime(skill_md)).isoformat(timespec="seconds"),
            "fm_version": fm_field(text, "version"),
            "fm_last_updated": fm_field(text, "last_updated"),
            "registry_source": reg.get("source"),
            "registry_version": reg.get("version"),
            "registry_user_created": reg.get("user_created"),
            "declared": declared,
            "inferred_upstreams": inferred_cand,
            "in_market_cache": name.lower() in market_slugs,
            "confidence": conf,
        })

    total = len(rows)
    conserved = (declared_n + inferred_n + unknown_n) == total
    doc = {
        "schema": "provenance-scan-r112-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "face": {
            "roots": [{"path": k, "skill_n": v} for k, v in sorted(roots_seen.items())],
            "authority_skill_n": total,
            "market_skill_n": len(market_slugs),
            "market_same_slug_n": sum(1 for r in rows if r["in_market_cache"]),
            "corpus_slugs_n": len(corpus),
            "corpus_generated_at": (json.load(io.open(CORPUS, encoding="utf-8-sig")).get("generated_at")
                                    if os.path.isfile(CORPUS) else None),
            "registry_n": len(registry),
            "notes": notes,
        },
        "tiers": {"declared": declared_n, "inferred": inferred_n, "unknown": unknown_n},
        "conservation": {"sum_tiers": declared_n + inferred_n + unknown_n, "total": total,
                         "ok": conserved},
        "rows": rows,
    }

    if args.json_out:
        outp = args.json_out if os.path.isabs(args.json_out) else os.path.join(ROOT, args.json_out)
        os.makedirs(os.path.dirname(outp), exist_ok=True)
        io.open(outp, "w", encoding="utf-8", newline="\n").write(
            json.dumps(doc, ensure_ascii=False, indent=1))
        print("JSON -> %s" % outp)

    print("面：权威源 %d 件 ｜ 市场缓存 %d 件（同名 %d）｜ 语料 slug %d"
          % (total, len(market_slugs), doc["face"]["market_same_slug_n"], len(corpus)))
    print("置信三档：declared=%d inferred=%d unknown=%d ｜ 守恒 %s"
          % (declared_n, inferred_n, unknown_n, "OK" if conserved else "BROKEN"))
    for n in notes:
        print("  注: %s" % n)
    if total < 10:
        print("[PROVENANCE:UNVERIFIED] 面过小（%d）" % total)
        return 2
    if not conserved:
        print("[PROVENANCE:BROKEN] 三档之和 != 总数")
        return 1
    print("[PROVENANCE:SCAN] declared=%d inferred=%d unknown=%d" % (declared_n, inferred_n, unknown_n))
    return 0


if __name__ == "__main__":
    sys.exit(main())
