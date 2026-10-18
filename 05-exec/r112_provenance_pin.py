# -*- coding: utf-8 -*-
r"""r112_provenance_pin.py — 把来源锚定结果落成 append-only pin 台账（内容寻址，R306）。

为什么单独一件：
  扫描（r112_provenance_scan.py）是「看」，pin 是「记」——记下来才能在下一轮回答
  「上游变没变」（否则每轮都要从零建身份，且无法判「变」）。
  台账只落本仓 06-benchmark/upstream_pins.jsonl，**绝不写受管根**（红线 1）。

写侧按 R306「内容寻址」：只有被测量的内容变了才追加，跑一趟不改盘；
同一 slug 的历史记录保留（append-only），最新一条为现值。

用法：
  python 05-exec/r112_provenance_pin.py --scan 06-benchmark/provenance_r112_<date>.json [--dry-run]
退出码：0 = 出账（含已是最新、无需追加）；2 = 扫描件缺失/不可读（UNVERIFIED）。
"""
import argparse
import io
import json
import os
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LEDGER = os.path.join(ROOT, "06-benchmark", "upstream_pins.jsonl")

CONTENT_KEYS = ("slug", "source_state", "identity", "local_sha256", "local_bytes", "local_dir_sha256")


def content_key(rec):
    return json.dumps({k: rec.get(k) for k in CONTENT_KEYS}, ensure_ascii=False, sort_keys=True)


def load_ledger():
    rows = []
    if not os.path.isfile(LEDGER):
        return rows
    for ln in io.open(LEDGER, encoding="utf-8-sig"):
        ln = ln.strip()
        if not ln:
            continue
        try:
            rows.append(json.loads(ln))
        except ValueError:
            continue
    return rows


def latest_by_slug(rows):
    out = {}
    for r in rows:
        if r.get("slug"):
            out[r["slug"]] = r
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", required=True)
    ap.add_argument("--ledger", default=LEDGER)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    sp = args.scan if os.path.isabs(args.scan) else os.path.join(ROOT, args.scan)
    if not os.path.isfile(sp):
        print("[PIN:UNVERIFIED] 扫描件缺失: %s" % sp)
        return 2
    try:
        scan = json.load(io.open(sp, encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        print("[PIN:UNVERIFIED] 扫描件不可读: %r" % (exc,))
        return 2

    rows = scan.get("rows") or []
    if not rows:
        print("[PIN:UNVERIFIED] 扫描面无行（零输入不得记绿，R247）")
        return 2

    existing = latest_by_slug(load_ledger())
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    new_recs, unchanged, skipped = [], 0, 0

    for r in rows:
        slug = r.get("slug")
        conf = r.get("confidence")
        if conf == "unknown":
            skipped += 1
            continue
        identity = None
        if conf == "declared":
            decl = r.get("declared") or {}
            identity = {"kind": "marketplace_declared", "meta": decl}
        elif conf == "self_built":
            # r113：自建裁定名册（HIGH/MID）件的答案是「本就没有上游」，不是「不知道」。
            # 这是有出处的结论（00-scope 用户裁定冻结件），不是猜——故可入册；
            # 但入册不等于送上游比对：r112_upstream_probe 只吃 inferred_upstreams，不碰本档。
            identity = {"kind": "self_built_no_upstream",
                        "authority": "00-scope/自建skill清单.md（HIGH/MID，用户裁定 v2）",
                        "same_source_proven": False}
        else:
            cands = r.get("inferred_upstreams") or []
            identity = {"kind": "github_name_inferred",
                        "candidates": [{"repo": c["repo"], "path": c["path"]} for c in cands[:5]],
                        "same_source_proven": False}
        rec = {
            "schema": "upstream-pins-v1",
            "slug": slug,
            "source_state": conf,
            "identity": identity,
            "local_sha256": r.get("local_sha256"),
            "local_bytes": r.get("local_bytes"),
            "local_dir_sha256": r.get("dir_manifest_sha256"),
            "registry_source": r.get("registry_source"),
            "at": now,
        }
        prev = existing.get(slug)
        if prev and content_key(prev) == content_key(rec):
            unchanged += 1
            continue
        fresh = prev is None
        rec["change"] = "new" if fresh else "identity_or_content_changed"
        new_recs.append(rec)

    if new_recs and not args.dry_run:
        os.makedirs(os.path.dirname(args.ledger), exist_ok=True)
        with io.open(args.ledger, "a", encoding="utf-8", newline="\n") as fh:
            for rec in new_recs:
                fh.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")

    total = len(rows)
    non_unknown = sum(1 for r in rows if r.get("confidence") != "unknown")
    print("台账：%s" % args.ledger)
    print("扫描面 %d 件 ｜ 有身份（declared+inferred+self_built）%d ｜ unknown 跳过 %d"
          % (total, non_unknown, skipped))
    print("本轮：新增/变更 %d ｜ 内容未变（不写盘）%d %s"
          % (len(new_recs), unchanged, "[DRY-RUN]" if args.dry_run else ""))
    if len(new_recs) + unchanged + skipped != total:
        print("[PIN:BROKEN] 新增+未变+跳过 != 总数")
        return 1
    print("[PIN:OK] 守恒 %d == %d" % (len(new_recs) + unchanged + skipped, total))
    return 0


if __name__ == "__main__":
    sys.exit(main())
