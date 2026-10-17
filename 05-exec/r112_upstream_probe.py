# -*- coding: utf-8 -*-
r"""r112_upstream_probe.py — 第 19 维证据面：把「我这份 vs 上游那份」量成确定性事实（只读）。

为什么不用语义尺判新旧：
  r105（裸 token / IDF）与 r111（BGE 语义）两代近邻尺先后被自己的标定控制判死
  （区间重叠 ⇒ 无鉴别力），根因是跨语言语料上的「相似」不等于「同源」。
  本件改机制（R263 修判据不修数据）：**同源问题用内容寻址回答，不用相似度**——
  取上游同名件的原文，与本地做**规范化行集合**的包含关系判定：
      identical        逐字节相同
      same_content     行集合相同（只有行尾/空白差异）
      upstream_ahead   本地行集合 ⊆ 上游  ⇒ 上游是超集，升级不丢本地内容
      local_ahead      上游行集合 ⊆ 本地  ⇒ 本地已增强，禁止自动覆盖
      diverged         互不包含 ⇒ 人工比对
      unrelated        交集低于 MIN_OVERLAP（可能是恰好重名，非同源）
  这一步不依赖任何模型、可离线复算，且给出可逐行追溯的证据。

取数面：gh api repos/<repo>/contents/<path>（原文 base64）+ 该文件的最后提交
        repos/<repo>/commits?path=<path>&per_page=1。
  限流守卫：剩余 < MIN_RATE 时整轮 UNVERIFIED（禁静默漏）；取不到一律 UNVERIFIED（R247）。
  缓存：06-benchmark/upstream_evidence/ 下按 repo__slug.json，TTL 内复用（--refresh 强制重取）。

用法：
  python 05-exec/r112_upstream_probe.py --scan 06-benchmark/provenance_r112_<date>.json \
         --json 06-benchmark/upstream_r112_<date>.json
退出码：0 = 出件且守恒；1 = 守恒破坏；2 = 取数面不可达/限流不足（UNVERIFIED）。
"""
import argparse
import base64
import io
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
EVID = os.path.join(ROOT, "06-benchmark", "upstream_evidence")

MIN_RATE = 300
MIN_OVERLAP = 0.15
AUTHORITY = r"D:\global_skills"

try:
    from skill_structure_rubric_scan import rubric_hits
except Exception as exc:  # pragma: no cover
    rubric_hits = None
    _RUBRIC_ERR = repr(exc)
else:
    _RUBRIC_ERR = None


def gh_api(path):
    try:
        p = subprocess.run(["gh", "api", path], capture_output=True, text=True,
                           timeout=120, encoding="utf-8", errors="replace")
    except Exception as exc:
        return None, "exc:%r" % (exc,)
    if p.returncode != 0:
        return None, "rc=%d:%s" % (p.returncode, (p.stderr or "").strip()[:160])
    return p.stdout, None


def rate_remaining():
    out, err = gh_api("rate_limit")
    if err:
        return None, err
    try:
        return json.loads(out)["resources"]["core"]["remaining"], None
    except Exception as exc:
        return None, "parse:%r" % (exc,)


def norm_lines(text):
    return [ln.strip() for ln in text.replace("\r\n", "\n").replace("\r", "\n").split("\n") if ln.strip()]


def relation(local_bytes, local_text, up_bytes, up_text):
    if local_bytes == up_bytes:
        return "identical", {}
    lset, uset = set(norm_lines(local_text)), set(norm_lines(up_text))
    inter = lset & uset
    un = lset | uset
    stats = {"local_lines": len(lset), "upstream_lines": len(uset),
             "common": len(inter), "local_only": len(lset - uset),
             "upstream_only": len(uset - lset),
             "jaccard": round(len(inter) / len(un), 4) if un else 0.0}
    if lset == uset:
        return "same_content", stats
    if stats["jaccard"] < MIN_OVERLAP:
        return "unrelated", stats
    if lset <= uset:
        return "upstream_ahead", stats
    if uset <= lset:
        return "local_ahead", stats
    return "diverged", stats


def fetch_candidate(repo, path, slug, cache_dir, ttl_sec, refresh):
    cache_p = os.path.join(cache_dir, "%s__%s.json" % (repo.replace("/", "_"), slug))
    if os.path.isfile(cache_p) and not refresh:
        try:
            c = json.load(io.open(cache_p, encoding="utf-8-sig"))
            age = time.time() - c.get("fetched_epoch", 0)
            if age <= ttl_sec and c.get("ok"):
                c["from_cache"] = True
                return c
        except (OSError, ValueError):
            pass
    rec = {"repo": repo, "path": path, "slug": slug, "ok": False,
           "fetched_epoch": time.time(), "from_cache": False}
    out, err = gh_api("repos/%s/contents/%s" % (repo, path))
    if err:
        rec["error"] = err
    else:
        try:
            d = json.loads(out)
            raw = base64.b64decode(d["content"])
            rec.update({"ok": True, "sha256": __import__("hashlib").sha256(raw).hexdigest(),
                        "bytes": len(raw), "blob_sha": d.get("sha"),
                        "content_b64": base64.b64encode(raw).decode("ascii")})
        except Exception as exc:
            rec["error"] = "decode:%r" % (exc,)
    if rec.get("ok"):
        out2, err2 = gh_api("repos/%s/commits?path=%s&per_page=1" % (repo, path))
        if not err2:
            try:
                arr = json.loads(out2)
                if arr:
                    rec["last_commit_sha"] = arr[0].get("sha")
                    rec["last_commit_date"] = (arr[0].get("commit", {}).get("committer", {}) or {}).get("date")
                    rec["last_commit_msg"] = ((arr[0].get("commit", {}).get("message") or "").splitlines() or [""])[0][:120]
            except Exception as exc:
                rec["commit_error"] = "parse:%r" % (exc,)
        else:
            rec["commit_error"] = err2
    # r112 cache-guard（一手缺陷实测 2026-10-17 22:13）：原先无论成功与否都写缓存，一次网络 EOF
    # 就把 14KB 好件覆写成 280B 的 {ok:false,error:EOF}，随后 --offline 复算把「已升级」件读成
    # UNVERIFIED（ok_n 24→18）——取数失败不得销毁已有证据（与 R247「零输入不得当绿」互为反向）。
    # 处置：失败不覆盖已成功的缓存，只把失败痕迹记进侧车字段；成功照旧覆盖。
    os.makedirs(cache_dir, exist_ok=True)
    prev = None
    if os.path.isfile(cache_p):
        try:
            prev = json.load(io.open(cache_p, encoding="utf-8-sig"))
        except (OSError, ValueError):
            prev = None
    if not rec.get("ok") and isinstance(prev, dict) and prev.get("ok"):
        stale = dict(prev)
        stale["from_cache"] = True
        stale["cache_error"] = rec.get("error")
        stale["cache_error_epoch"] = rec.get("fetched_epoch")
        try:
            io.open(cache_p, "w", encoding="utf-8", newline="\n").write(
                json.dumps(stale, ensure_ascii=False, sort_keys=True))
        except OSError:
            pass
        stale["from_cache"] = False
        return stale
    try:
        io.open(cache_p, "w", encoding="utf-8", newline="\n").write(
            json.dumps(rec, ensure_ascii=False, sort_keys=True))
    except OSError:
        pass
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", required=True)
    ap.add_argument("--json", dest="json_out", default=None)
    ap.add_argument("--ttl-min", type=float, default=30.0)
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--offline", action="store_true", help="只用缓存，不联网")
    ap.add_argument("--max-candidates", type=int, default=3)
    args = ap.parse_args()

    sp = args.scan if os.path.isabs(args.scan) else os.path.join(ROOT, args.scan)
    if not os.path.isfile(sp):
        print("[UPSTREAM:UNVERIFIED] 扫描件缺失: %s" % sp)
        return 2
    scan = json.load(io.open(sp, encoding="utf-8-sig"))
    targets = [r for r in (scan.get("rows") or []) if r.get("inferred_upstreams")]
    if not targets:
        print("[UPSTREAM:UNVERIFIED] 无 inferred 目标（零输入不得记绿，R247）")
        return 2

    rate_note = None
    if not args.offline:
        rem, err = rate_remaining()
        if err or rem is None:
            print("[UPSTREAM:UNVERIFIED] 限流面取不到: %s" % (err or "none"))
            return 2
        rate_note = {"core_remaining": rem}
        if rem < MIN_RATE:
            print("[UPSTREAM:UNVERIFIED] 限流不足（remaining=%d < %d）" % (rem, MIN_RATE))
            return 2

    rows, n_api, n_cache = [], 0, 0
    for r in targets:
        slug = r["slug"]
        local_p = os.path.join(AUTHORITY, slug, "SKILL.md")
        try:
            with open(local_p, "rb") as fh:
                local_bytes = fh.read()
        except OSError as exc:
            rows.append({"slug": slug, "status": "UNVERIFIED", "reason": "local_unreadable:%r" % (exc,)})
            continue
        local_text = local_bytes.decode("utf-8-sig", errors="replace")

        chosen, tried = None, []
        for cand in (r.get("inferred_upstreams") or [])[:args.max_candidates]:
            repo, path = cand["repo"], cand["path"]
            if args.offline:
                cache_p = os.path.join(EVID, "%s__%s.json" % (repo.replace("/", "_"), slug))
                if not os.path.isfile(cache_p):
                    tried.append({"repo": repo, "path": path, "error": "offline_no_cache"})
                    continue
                c = json.load(io.open(cache_p, encoding="utf-8-sig"))
                c["from_cache"] = True
            else:
                c = fetch_candidate(repo, path, slug, EVID, args.ttl_min * 60.0, args.refresh)
            if c.get("from_cache"):
                n_cache += 1
            else:
                n_api += 1
            if not c.get("ok"):
                tried.append({"repo": repo, "path": path, "error": c.get("error")})
                continue
            up_bytes = base64.b64decode(c["content_b64"])
            up_text = up_bytes.decode("utf-8-sig", errors="replace")
            rel, stats = relation(local_bytes, local_text, up_bytes, up_text)
            tried.append({"repo": repo, "path": path, "relation": rel, "jaccard": stats.get("jaccard")})
            if rel != "unrelated":
                chosen = (c, up_text, rel, stats)
                break

        if chosen is None:
            rows.append({"slug": slug, "status": "UNVERIFIED", "candidates_tried": tried,
                         "reason": "无可识别同源候选（全部 unrelated 或取不到）"})
            continue
        c, up_text, rel, stats = chosen
        rub_l = rubric_hits(local_text) if rubric_hits else None
        rub_u = rubric_hits(up_text) if rubric_hits else None
        rows.append({
            "slug": slug, "status": "OK",
            "upstream_repo": c["repo"], "upstream_path": c["path"],
            "upstream_sha256": c.get("sha256"), "upstream_bytes": c.get("bytes"),
            "upstream_blob_sha": c.get("blob_sha"),
            "upstream_last_commit_sha": c.get("last_commit_sha"),
            "upstream_last_commit_date": c.get("last_commit_date"),
            "upstream_last_commit_msg": c.get("last_commit_msg"),
            "local_sha256": r.get("local_sha256"), "local_bytes": r.get("local_bytes"),
            "relation": rel, "stats": stats,
            "rubric_local": rub_l, "rubric_upstream": rub_u,
            "candidates_tried": tried,
            "evidence_source": "cache" if c.get("from_cache") else "api",
        })

    ok_n = sum(1 for x in rows if x["status"] == "OK")
    unver_n = len(rows) - ok_n
    rel_counts = {}
    for x in rows:
        if x["status"] == "OK":
            rel_counts[x["relation"]] = rel_counts.get(x["relation"], 0) + 1
    doc = {
        "schema": "upstream-probe-r112-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "face": {
            "scan_file": os.path.relpath(sp, ROOT).replace("\\", "/"),
            "targets_n": len(targets), "ok_n": ok_n, "unverified_n": unver_n,
            "api_calls": n_api, "cache_hits": n_cache,
            "rate": rate_note, "min_rate": MIN_RATE,
            "min_overlap": MIN_OVERLAP,
            "rubric_available": rubric_hits is not None, "rubric_err": _RUBRIC_ERR,
        },
        "relations": rel_counts,
        "conservation": {"ok_n + unverified_n": ok_n + unver_n, "targets_n": len(targets),
                         "ok": ok_n + unver_n == len(targets)},
        "rows": rows,
    }
    if args.json_out:
        outp = args.json_out if os.path.isabs(args.json_out) else os.path.join(ROOT, args.json_out)
        os.makedirs(os.path.dirname(outp), exist_ok=True)
        io.open(outp, "w", encoding="utf-8", newline="\n").write(
            json.dumps(doc, ensure_ascii=False, indent=1))
        print("JSON -> %s" % outp)

    print("目标 %d ｜ OK %d ｜ UNVERIFIED %d ｜ API 调用 %d ｜ 缓存命中 %d"
          % (len(targets), ok_n, unver_n, n_api, n_cache))
    print("关系分布：%s" % json.dumps(rel_counts, ensure_ascii=False))
    for x in rows:
        if x["status"] == "OK":
            print("  %-40s %-14s local_only=%-5s upstream_only=%-5s 上游最后提交 %s %s"
                  % (x["slug"], x["relation"], x["stats"].get("local_only"),
                     x["stats"].get("upstream_only"),
                     (x.get("upstream_last_commit_date") or "?")[:10],
                     (x.get("upstream_last_commit_msg") or "")[:60]))
        else:
            print("  %-40s UNVERIFIED %s" % (x["slug"], x.get("reason", "")))
    if not doc["conservation"]["ok"]:
        print("[UPSTREAM:BROKEN] 守恒破坏")
        return 1
    print("[UPSTREAM:PROBE] ok=%d unverified=%d" % (ok_n, unver_n))
    return 0


if __name__ == "__main__":
    sys.exit(main())
