# -*- coding: utf-8 -*-
"""r103_l1_backfill.py — 把 r103 换装装入的 3 件补进 L1 运行时层 skill_content/design.json。

为什么必须做：注册表 176 而 `skill_content` 域 JSON 只 150 ⇒ 新件**入册但不在运行时触发层**，
路由读不到触发词，等于装了个死件（GM lessons「Registered != discoverable」同源）。
C10 判据就是把这两个数对账的。

口径与约束：
  · 条目 schema 与同域兄弟逐字对齐：{name, triggers[], size, version, desc}（实测 design.json 首条）。
  · triggers 取自各件 frontmatter description 的「Use when …」子句 + 领域词，**不留空**。
  · 写入格式 = 项目惯例（ensure_ascii=False + indent=2 + 无结尾换行 + 平台默认 newline），
    与 `normalize_skill_content.py` 的字节对齐要求一致，否则两生成器 hash 恒不等（R275）。
  · 只增不改：已存在的 name 一律跳过并点名，禁覆盖他方条目（blast radius = 本会话的 3 件）。

退出码：0=补齐且读回自洽；1=任一件未落或对账不过；2=前置面不可达。
"""
import io
import json
import os
import sys

SC_DIR = r"D:/global_memory/skill_content"
DOMAIN_FILE = os.path.join(SC_DIR, "design.json")
REG = r"C:/Users/37533/Desktop/workspace/焚诀/skill/registry/unified-skills-index.json"
AUTH = r"D:/global_skills"

TRIGGERS = {
    "healthcare-cdss-patterns": [
        "CDSS", "临床决策支持", "药物相互作用", "剂量校验", "预警分级", "临床评分",
        "clinical decision support", "drug interaction check", "dose validation",
        "NEWS2", "qSOFA", "alert severity"],
    "healthcare-emr-patterns": [
        "EMR", "EHR", "电子病历", "就诊流程", "处方生成", "临床数据录入",
        "clinical data entry", "encounter workflow", "prescription generation"],
    "healthcare-eval-harness": [
        "患者安全评测", "PHI 泄露", "临床工作流完整性", "部署安全闸",
        "patient safety eval", "PHI exposure", "eval harness"],
}


def load(path):
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)


def main():
    apply = "--apply" in sys.argv
    if not os.path.isfile(DOMAIN_FILE) or not os.path.isfile(REG):
        print("[L1:UNVERIFIED] 前置面不可达: %s / %s" % (DOMAIN_FILE, REG))
        return 2
    doc = load(DOMAIN_FILE)
    reg = load(REG)
    have = {e["name"] for e in doc["skills"]}
    added, skipped = [], []
    for slug, trigs in TRIGGERS.items():
        skill_md = os.path.join(AUTH, slug, "SKILL.md")
        if not os.path.isfile(skill_md):
            print("[L1:FAIL] 权威源缺件 %s（先装再补 L1，不得造幽灵条目）" % skill_md)
            return 1
        if slug not in reg["skills"]:
            print("[L1:FAIL] %s 不在注册表 ⇒ L1 与注册表分叉，停手" % slug)
            return 1
        if slug in have:
            skipped.append(slug)
            continue
        text = io.open(skill_md, encoding="utf-8").read()
        desc = ""
        for ln in text.splitlines():
            if ln.startswith("description:"):
                desc = ln.split(":", 1)[1].strip().strip('"')
                break
        if not desc:
            print("[L1:FAIL] %s frontmatter 无 description，无法生成 L1 条目" % slug)
            return 1
        doc["skills"].append({"name": slug, "triggers": trigs,
                              "size": os.path.getsize(skill_md),
                              "version": "community",
                              "desc": desc[:160] + ("..." if len(desc) > 160 else "")})
        added.append(slug)
    doc["count"] = len(doc["skills"])
    # 全局对账口径 = 所有域 JSON 的条目数之和 vs 注册表总数。
    # 首版这里写的是 `len(reg) - 本域条数`，把「一个域」跟「全库」相减，印出 residual_gap=161
    # 这种看着像灾难的数字 —— 判据自己的展示也能造出假信号（判据展示口径陷阱同族）。
    total_all = 0
    for fn in sorted(os.listdir(SC_DIR)):
        if not fn.endswith(".json") or fn in ("skill_ids.json", "index_manifest.json"):
            continue
        p = os.path.join(SC_DIR, fn)
        try:
            # 本域取**内存里即将写出的那份**：盘上还是旧内容，按盘算会少计本次新增 3 条
            obj = doc if os.path.abspath(p) == os.path.abspath(DOMAIN_FILE) else load(p)
            total_all += len(obj.get("skills", []))
        except (ValueError, KeyError, AttributeError):
            total_all += -1        # 解析不了的域必须显形，不得静默计入 0
    text = json.dumps(doc, ensure_ascii=False, indent=2)
    print(json.dumps({"domain": doc["domain"], "added": added, "skipped_already": skipped,
                      "count_after": doc["count"],
                      "registry_total": len(reg["skills"]),
                      "l1_total_after": total_all,
                      "residual_gap_all_domains": len(reg["skills"]) - total_all},
                     ensure_ascii=False))
    if not apply:
        print("[L1:DRY-RUN] 未写盘")
        return 0
    with io.open(DOMAIN_FILE, "w", encoding="utf-8") as f:
        f.write(text)
    back = io.open(DOMAIN_FILE, encoding="utf-8").read()
    if back != text:
        print("[L1:FAIL] 读回不等")
        return 1
    chk = json.loads(back)
    if chk["count"] != len(chk["skills"]):
        print("[L1:FAIL] count 与实际条数不等")
        return 1
    for s in added + skipped:
        if s not in {e["name"] for e in chk["skills"]}:
            print("[L1:FAIL] 读回缺 %s" % s)
            return 1
    print("[L1:PASS] 3 件入 L1 运行时层，读回自洽（design.json count=%d）" % chk["count"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
