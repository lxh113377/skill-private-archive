# -*- coding: utf-8 -*-
"""r299_backfill_cache.py — 把 22 个「声明上游仓但不在 r114 缓存」的仓真量一遍。

为什么必须做而不是记 unmeasured：需求 3 要求候选进五维打分，而实测 declared_upstream_in_face
在 pad_only 13 件上是 0/13 ⇒ 「已知上游是谁，却没评估过它」。只记 unmeasured 就等于把这个缺口
原样留在账上。这里用 **r114 本体的 measure_repo**（含元数据、树计数、正文许可、save_cache），
不自己写取数 —— 复制口径即第二真相源（04-plan 5.4），而且它的 fc/compat 两维依赖
skill_md_exact_n 这种严格口径字段，我另写一份极可能算出不同分（r225 的坑）。

写缓存的边界说明（如实记）：CACHE_DIR 是 gitignored 的 _temp/r114_search_cache，且 save_cache
只按 key 追加、不覆写他人条目 ⇒ 对本仓其他会话是**增量可读**、不破坏既有读数（缓存命中路径
原样返回旧件，r184 实测）。这是取数、不是判定：判定仍在 r299_declared_inject.py 里做。
"""
import importlib.util
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SP = os.path.join(ROOT, "05-exec", "r114_replacement_scan.py")
_s = importlib.util.spec_from_file_location("r114", SP)
r114 = importlib.util.module_from_spec(_s)
_s.loader.exec_module(r114)

COL = json.load(io.open(os.path.join(HERE, "tree_paths.json"), encoding="utf-8"))
# 采集件的键就是 repo 名（值里没有 repo 字段 —— 我上一版按值取 x["repo"] 直接 KeyError，
# 那是我自己造的字段名，属猜标识符同一族）。
cache = r114.load_cache()
missing = [r for r in COL if not (cache.get("repo__" + r114.key_of(r)) or {}).get("state") == "OK"]
print("collected repos=%d  缓存里已 OK 的=%d  需补测=%d"
      % (len(COL), len(COL) - len(missing), len(missing)))
stats = {"api_calls": 0, "cache_hits": 0, "cache_miss": 0, "errors": []}
done = []
for repo in missing:
    m = r114.measure_repo(repo, cache, False, stats)     # offline=False：这正是要联网的一次
    st = (m or {}).get("state")
    print("  %-44s state=%-6s stars=%-7s exact=%-4s ghost=%-3s lic=%s"
          % (repo, st, (m or {}).get("stars"), (m or {}).get("skill_md_exact_n"),
             (m or {}).get("skill_md_ghost_n"), str((m or {}).get("license"))[:14]))
    if st == "OK":
        done.append(repo)
        cache["repo__" + r114.key_of(repo)] = m          # 供本轮判据立刻复用（save_cache 已落盘）
print("[BACKFILL] measured_ok=%d / %d  api_calls=%d errors=%d"
      % (len(done), len(missing), stats["api_calls"], len(stats["errors"])))
if stats["errors"]:
    for e in stats["errors"][:4]:
        print("   ERR", str(e)[:150])
json.dump({"missing_before": missing, "measured_ok": done, "api_calls": stats["api_calls"],
           "errors": stats["errors"][:10]},
          io.open(os.path.join(HERE, "backfill_report.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
sys.exit(0 if len(done) == len(missing) else 1)
