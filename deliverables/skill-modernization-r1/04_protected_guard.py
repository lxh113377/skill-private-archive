# -*- coding: utf-8 -*-
"""04_protected_guard.py -- 迁移前置检查：注册表保护件禁替换（captain 2026-11-07 立）。

为什么存在：t4 首版把 A-skill-manager（_my-skills/registry.json 的 protected_skills）
排进 P0 并计划用 affaan-m/ECC 替换。该件是「所有技能增删改查唯一入口」（21 技能融合体），
替换它等于拆掉技能体系管控中枢 —— 属「原有业务逻辑受破坏」，违需求6。
本判据把「查注册表保护名单」从人工核对变成机器闸：命中即红，禁止进入替换批次。

三态退出码（与 run_gates 同口径）：0 CLEAN（无保护件在替换批次）/ 1 VIOLATION（命中）/
2 UNVERIFIED（注册表或批次件取不到 —— 不得把「取不到」读成「没命中」）。
"""
import argparse, io, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REGISTRY = "D:/global_skills/_my-skills/registry.json"
BATCHES = os.path.join(HERE, "04_migration_batches.json")


def load_protected(path):
    """读保护名单；文件缺失/不可析 => 返回 None 交调用方判 UNVERIFIED（不静默当空名单）。"""
    try:
        d = json.load(io.open(path, encoding="utf-8"))
    except Exception as e:
        return None, str(e)
    return sorted((d.get("protected_skills") or {}).keys()), None


def collect_batches(obj):
    """收集所有「计划替换」的 slug；holds/gaps/low_keep/exclude 不算替换面。"""
    out = []
    for key in ("P0", "P1", "P2"):
        for x in obj.get(key) or []:
            out.append(x.get("slug") if isinstance(x, dict) else x)
    return [s for s in out if s]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", default=REGISTRY)
    ap.add_argument("--batches", default=BATCHES)
    ap.add_argument("--negative-control", action="store_true",
                    help="注入保护件到替换批次，断言判据必须报红（证有牙）")
    a = ap.parse_args()

    prot, err = load_protected(a.registry)
    if prot is None:
        print("[PROTGUARD:UNVERIFIED] 注册表不可读: " + str(err))
        return 2
    try:
        b = json.load(io.open(a.batches, encoding="utf-8"))
    except Exception as e:
        print("[PROTGUARD:UNVERIFIED] 批次件不可读: " + str(e))
        return 2

    slugs = collect_batches(b)
    if a.negative_control:
        # 负控：故意把保护件塞进替换面，判据必须报红；不改真件，只改内存副本。
        if not prot:
            print("[PROTGUARD:UNVERIFIED] 保护名单为空，负控无对象")
            return 2
        slugs = slugs + [prot[0]]

    hit = [s for s in slugs if s in prot]
    print("[PROTGUARD] registry=" + a.registry)
    print("[PROTGUARD] protected=" + str(prot))
    print("[PROTGUARD] replacement_scope_n=" + str(len(slugs)))
    if a.negative_control:
        if hit:
            print("[NEGCTRL:RED] 注入保护件 " + str(hit) + " 后判据报红（符合预期）")
            return 0
        print("[NEGCTRL:FAIL] 注入保护件后仍未见红 —— 判据无牙")
        return 1
    if hit:
        print("[PROTGUARD:VIOLATION] 保护件出现在替换批次: " + str(hit))
        print("  处置：移入 protected_hold，改为经 rule_editor.py 自建增量升级，禁替换")
        return 1
    print("[PROTGUARD:CLEAN] 替换批次内无注册表保护件")
    return 0


if __name__ == "__main__":
    sys.exit(main())