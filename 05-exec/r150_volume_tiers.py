# -*- coding: utf-8 -*-
# r150_volume_tiers.py -- 体量治理评估指标体系三层归口面（第 59 门候选）。
#
# 存在理由（r150 现状核验实测）：体量阈值有 60 个 key（volumegov.DEFAULT_BUDGET），
#   但**没有任何分层**：问「业务体量 / 资源承载体量 / 运营规模体量 各自的标尺是哪几个」，
#   只能逐个 key 猜。阈值散在一张扁平表里，等于指标体系没建立。
#
# 本件把 60 个 key 按**声明的归口表**分成三层，并断言：
#   ① 每个 key 必须被分到某一层（未分类 = 0）——上游加 key 时本面判红并把**未分类的 key 具名**
#      （不是静默忽略，X-24：分母静默变小而面内不变式照样全绿）；
#   ② 三层计数之和 == 阈值总数（各态之和 == 分母）。
#
# 三层口径（本件**声明**，可审计可改）：
#   T1 业务体量      —— 内容与知识规模（记忆卷 / 语料 / 技能文档 / 同族簇）
#   T2 资源承载体量  —— 注入面与存储承载（每轮注入字节 / 单件 / 目录 / 整仓 / 台账）
#   T3 运营规模体量  —— 轮次产物与自动化链（环比 / 台账龄期 / 缓存与备份 / 回收区 / 心跳）
#
# 用法:
#   python 05-exec/r150_volume_tiers.py                      # 现读归属方 --print-budget
#   python 05-exec/r150_volume_tiers.py --budget-file <件>   # 夹具/离线用
#   python 05-exec/r150_volume_tiers.py --json <件>
# 退出码: 0 全分类且计数自洽 / 1 有未分类 key / 2 阈值面取不到（UNVERIFIED，R247）
import argparse
import io
import json
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT_DEFAULT = os.path.dirname(HERE)
HANDOFF = r"D:\global_skills\A-project-handoff\scripts\handoff.py"

TIER_NAMES = {
    "T1": "业务体量（内容与知识规模）",
    "T2": "资源承载体量（注入面与存储承载）",
    "T3": "运营规模体量（轮次产物与自动化链）",
}

TIER_KEYS = {
    "T1": ["memory_md_max", "corpus_max", "skill_md_soft", "skill_md_heavy",
           "family_file_max", "family_bytes_max", "family_prefix_min", "family_scan_depth",
           "family_keep", "family_archive_dir", "family_apply_enabled", "family_apply_same_commit",
           "family_min_age_days", "family_rate_window_h", "family_rate_max_new"],
    "T2": ["shell_max", "root_doc_max", "artifact_max", "any_file_max", "dir_max", "repo_max",
           "ledger_max", "chain_ledger_max", "evicted_archive_max", "state_face_max",
           "state_max_bytes", "heartbeat_max_bytes", "nest_depth_max", "nest_path_len_max",
           "nest_repeat_max", "cache_dir_max", "cache_file_max", "cache_keep", "cache_cluster_scope"],
    "T3": ["growth_ratio", "snapshot_max_age_days", "heartbeat_max_age_days", "bak_keep",
           "bak_age_days", "cache_ttl_days", "cluster_over_cap_ttl_days", "cache_over_cap_streak_min",
           "max_freed_per_run", "max_moved_per_run", "purge_ttl_days", "urgent_cache_bytes",
           "urgent_ttl_days", "trash_max_age_days", "trash_red_age_days", "copy_proof_max_files",
           "copy_proof_full_cover_max", "jsonl_rotate_enabled", "jsonl_keep_rows", "jsonl_ttl_days",
           "chain_escalate_days", "findings_top_n", "findings_stale_days", "stale_red_days",
           "face_time_budget_ms", "auto_layers"],
}


def read_budget(path):
    t = io.open(path, encoding="utf-8-sig", errors="ignore").read()
    doc = json.loads(t)
    if isinstance(doc, dict) and isinstance(doc.get("budget"), dict):
        return doc["budget"], doc
    return doc, {"sources": ["inline budget object"]}


def fetch_budget(project):
    if not os.path.isfile(HANDOFF):
        return None, {"error": "handoff.py 不存在：%s" % HANDOFF}
    p = subprocess.run([os.sys.executable, HANDOFF, "volume", "--print-budget", "--project", project],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
    out = (p.stdout or "").strip()
    if not out:
        return None, {"error": "归属方 --print-budget 无输出（rc=%s）" % p.returncode}
    try:
        doc = json.loads(out)
    except Exception as e:
        return None, {"error": "阈值面不可解析：%s" % str(e)[:80]}
    return (doc.get("budget") or {}), doc


def build(project, budget_file=""):
    if budget_file:
        try:
            budget, doc = read_budget(budget_file)
        except Exception as e:
            budget, doc = None, {"error": "budget-file 不可解析：%s" % str(e)[:80]}
    else:
        budget, doc = fetch_budget(project)
    if not budget:
        return {"schema": "fj-gov-volume-tiers-v1", "budget_n": 0, "source_error": doc.get("error"),
                "tiers": {}, "unclassified": [], "total_n": 0}
    owner = {}
    for tier, keys in TIER_KEYS.items():
        for k in keys:
            owner[k] = tier
    unclassified = sorted(k for k in budget if k not in owner)
    tiers = {}
    for tier in sorted(TIER_KEYS):
        ks = [k for k in budget if owner.get(k) == tier]
        tiers[tier] = {"name": TIER_NAMES[tier], "n": len(ks), "keys": sorted(ks),
                       "values": dict((k, budget[k]) for k in sorted(ks))}
    return {
        "schema": "fj-gov-volume-tiers-v1",
        "budget_n": len(budget),
        "sources": (doc.get("sources") if isinstance(doc, dict) else None),
        "tiers": tiers,
        "unclassified": unclassified,
        "total_n": len(budget),
        "classified_n": len(budget) - len(unclassified),
        "coverage": round((len(budget) - len(unclassified)) / float(len(budget)), 4) if budget else 0.0,
        "source_error": None,
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=ROOT_DEFAULT)
    ap.add_argument("--budget-file", dest="bf", default="")
    ap.add_argument("--json", dest="out", default="")
    args = ap.parse_args(argv)
    doc = build(os.path.abspath(args.root), args.bf)
    if doc["budget_n"] == 0:
        print("[GOVTIER:UNVERIFIED] 阈值面取不到（%s）=> 不得按绿记（R247）" % doc.get("source_error"))
        if args.out:
            with io.open(args.out, "w", encoding="utf-8", newline="\n") as f:
                json.dump(doc, f, ensure_ascii=False, indent=1)
        return 2
    print("[GOVTIER] 阈值 key 总数 %d｜已分层 %d｜覆盖率 %.4f"
          % (doc["total_n"], doc["classified_n"], doc["coverage"]))
    for tier in sorted(doc["tiers"]):
        t = doc["tiers"][tier]
        print("  %s %-34s %d 项" % (tier, t["name"], t["n"]))
        print("       %s" % ", ".join(t["keys"][:10]) + (" ..." if t["n"] > 10 else ""))
    if doc["sources"]:
        print("[GOVTIER] 阈值来源：%s" % "; ".join(str(s) for s in doc["sources"])[:200])
    if doc["unclassified"]:
        print("[GOVTIER:FAIL] 未分类 key %d 个（上游加 key 必须被具名，禁静默忽略）：%s"
              % (len(doc["unclassified"]), ", ".join(doc["unclassified"])))
        rc = 1
    else:
        print("[GOVTIER:PASS] 全部分层且计数自洽（sum(tiers) == total == %d）" % doc["total_n"])
        rc = 0
    if args.out:
        with io.open(args.out, "w", encoding="utf-8", newline="\n") as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
        print("[GOVTIER] 留痕 %s" % args.out)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
