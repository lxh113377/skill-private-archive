# 04_plan_check.py -- t4 分阶段迁移方案完整性判据
# 逻辑：抽出 markdown 中每个 # @rollback 代码块，逐条命令做语法与路径静态校验；
#       再校验每个 P0 四件套、批次覆盖、守恒与禁语；负控在内存删 P1 回滚块后必须报红。
# 只用 stdlib；负控只改内存副本，不写回任何文件。
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DELIV = os.path.dirname(HERE)
AUDIT = os.path.dirname(DELIV)
ROOT = os.path.dirname(AUDIT)
PLAN = os.path.join(HERE, "04_migration_plan.md")
BATCH = os.path.join(HERE, "04_migration_batches.json")

FORBIDDEN = ["请老大手动", "请手动", "手动操作", "请你点击", "请你操作", "人工点击"]
OK_PREFIX = ("&", "git ", "Test-Path", "Copy-Item", "powershell ", "python ",
             "Get-ChildItem", "cd ", "$env:", "$PY", "$RE", "Write-Output",
             "ForEach-Object", "foreach ", "Get-Content")
QUOTED = re.compile(chr(34) + "([^" + chr(34) + "]*)" + chr(34))

# 正文一致性闸门：t4 首版 / 半修正态残留的旧数字与旧名单，命中即判红（防正文自相矛盾却报绿）。
STALE_STRINGS = [
    "58 = P0 5 + P1 25 + P2 28",
    "58+11+8 = 77",
    "| HOLD（无 compat 正增益） | 8 |",
    "P1 25 件",
    "（25 件，priority_index 排名 6–30）",
    "## 5. P1 分批替换（25 件）",
    "8 件 HOLD（有真替代但无 compat 正增益）",
    "| A-skill-manager | HIGH | P0 |",
    "undo --file " + chr(34) + "D:/global_skills/A-skill-manager/SKILL.md" + chr(34),
    "priority_index 前 5",
    "P1 首批扩展** | 25 |",
    "8 HOLD 复评",
    "另含 8 件 HOLD 复评",
]


def read_text(p):
    with open(p, "r", encoding="utf-8") as f:
        return f.read()


def fenced_blocks(text):
    out = []
    cur = None
    for i, line in enumerate(text.split("\n"), 1):
        if line.strip().startswith("```"):
            if cur is None:
                cur = {"lang": line.strip(), "lines": [], "start": i}
            else:
                cur["end"] = i
                out.append(cur)
                cur = None
        elif cur is not None:
            cur["lines"].append((i, line))
    return out


def anchor_info(block_lines):
    for _, l in block_lines:
        if "# @rollback" in l:
            d = {}
            for part in l.strip().split():
                if "=" in part:
                    k, v = part.split("=", 1)
                    d[k] = v
            return d
    return {}


def rollback_blocks(text):
    return [b for b in fenced_blocks(text) if any("# @rollback" in l for _, l in b["lines"])]


def is_path(s):
    return (s.startswith("D:/") or s.startswith("C:/") or
            s.startswith("自建skill优化") or s.startswith("deliverables/") or
            s.startswith("_temp/") or s.startswith("05-exec/"))


def resolve(p):
    # 归档仓根是 git -C 的裸名；其余按 绝对路径 / 审计仓 / 工作区根 / 交付目录 四个基座试探
    if p == "自建skill优化":
        return AUDIT if os.path.isdir(AUDIT) else None
    for cand in (p, os.path.join(AUDIT, p), os.path.join(ROOT, p), os.path.join(HERE, p)):
        try:
            if os.path.exists(cand):
                return cand
        except OSError:
            pass
    return None


def exempt(p, is_dest):
    # 运行期产物：_temp 缓存、_trash/t4_ 备份、通配符、PowerShell 变量、json 输出
    if is_dest:
        return True
    if ("_temp/" in p or "_trash/t4_" in p or "*" in p or "$" in p or
            p.endswith(".json")):
        return True
    return False


def validate_line(line):
    errs = []
    if line.count(chr(34)) % 2 != 0:
        errs.append("引号不成对")
    if "<" in line or ">" in line:
        errs.append("含尖括号占位")
    for w in FORBIDDEN:
        if w in line:
            errs.append("禁语 " + w)
    s = line.strip()
    if not s.startswith(OK_PREFIX):
        errs.append("命令前缀不在白名单")
    qs = QUOTED.findall(line)
    for k, q in enumerate(qs):
        if not is_path(q):
            continue
        # Copy-Item 的第 2 个引号串是目标（输出），不要求事前存在
        dest = ("Copy-Item" in line) and (k == 1)
        if exempt(q, dest):
            continue
        if resolve(q) is None:
            errs.append("路径不存在 " + q)
    return errs


def print_stats(batch):
    d = batch["denominator"]
    c = batch["counts"]
    print("[STATS] HIGH=" + str(d["high"]) + " MID=" + str(d["mid"]) +
          " LOW=" + str(d["low"]) + " EXCLUDE=" + str(d["exclude"]) +
          " TOTAL=" + str(d["total"]))
    print("[STATS] replaceable=" + str(c["replaceable"]) + " P0=" + str(c["P0"]) +
          " P1=" + str(c["P1"]) + " P2=" + str(c["P2"]) +
          " gaps=" + str(c["gaps"]) + " holds=" + str(c["holds"]))
    ok = (c["P0"] + c["P1"] + c["P2"] == c["replaceable"] and
          c["replaceable"] + c["gaps"] + c["holds"] == d["high"] + d["mid"] and
          d["total"] == d["high"] + d["mid"] + d["low"] + d["exclude"])
    print("[STATS] conservation=" + ("PASS" if ok else "FAIL"))
    return ok


def evaluate(text, batch, verbose):
    failures = []
    blocks = rollback_blocks(text)
    infos = [anchor_info(b["lines"]) for b in blocks]
    labels = [d.get("BATCH", "") for d in infos]
    total_cmd = 0
    passed_cmd = 0
    for b in blocks:
        for lineno, line in b["lines"]:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            total_cmd += 1
            errs = validate_line(line)
            if errs:
                for e in errs:
                    failures.append("L" + str(lineno) + " " + e + " :: " + s[:120])
            else:
                passed_cmd += 1
    # 每个回滚块的八要素：tag 锚、git describe、区间 revert、两仓、双硬前提、可复跑验证
    need = [("undo", "undo --file"), ("trash", "_trash"),
            ("tag_anchor", "tag -l"), ("describe", "describe --tags"),
            ("revert_range", "..HEAD"), ("revert_cmd", "revert --no-edit"),
            ("source_repo", "D:/global_skills"), ("archive_repo", "自建skill优化"),
            ("revalidation", "04_plan_check.py")]
    for b in blocks:
        joined = "\n".join(l for _, l in b["lines"])
        for name, token in need:
            if token not in joined:
                failures.append("回滚块缺要素 " + name + " @" + str(anchor_info(b["lines"])))
    # 批次覆盖：P0 逐件 5 + P0-BATCH + P1 + P2
    for lab in ("P0-BATCH", "P1", "P2"):
        if lab not in labels:
            failures.append("缺批次回滚块 " + lab)
    if labels.count("P0") != 5:
        failures.append("P0 逐件回滚块数=" + str(labels.count("P0")) + " 期望 5")
    # 每个 P0 章节的 (a)(b)(c)(d) 四件套
    for i, item in enumerate(batch["P0"], 1):
        slug = item["slug"]
        marker = "### 4." + str(i) + " P0-" + str(i) + " `" + slug + "`"
        start = text.find(marker)
        if start < 0:
            failures.append("缺 P0 章节 " + marker)
            continue
        nxt = text.find("\n### ", start + len(marker))
        sec = text[start:(nxt if nxt > 0 else len(text))]
        for tag in ("(a)", "(b)", "(c)", "(d)"):
            if tag not in sec:
                failures.append(slug + " 缺 " + tag)
        for tok in ("rule_editor.py", "_trash", "tag -a r345", "describe --tags",
                    "revert --no-edit r345..HEAD", "run_gates.py",
                    "04_plan_check.py", "git -C"):
            if tok not in sec:
                failures.append(slug + " 缺要素 " + tok)
        if not any(d.get("SKILL", "") == slug and d.get("BATCH", "") == "P0" for d in infos):
            failures.append(slug + " 缺逐件 @rollback 标记")
    # 全文禁语 + git describe 字面（§3 G0 有双仓 git describe --tags 口径）
    # 全文禁语检查：允许否定语境（如「禁『请老大手动』」），只抓未加否定的实际措辞
    for w in FORBIDDEN:
        pos = 0
        while True:
            hit = text.find(w, pos)
            if hit < 0:
                break
            ctx = text[max(0, hit - 10):hit]
            negated = any(k in ctx for k in ("禁", "不得", "不含", "排除", "禁语", "全文无"))
            if not negated:
                failures.append("全文禁语 " + w + " @offset " + str(hit))
                break
            pos = hit + len(w)
    if "git describe" not in text:
        failures.append("全文缺 git describe 口径")
    # §10 门禁实测记录必须回填，禁止留下生成期占位（数字以 JSON 句柄为准）
    if "见 §10 回填" in text:
        failures.append("§10 门禁 verdict 未回填")
    if "_temp/t4_gates.json" not in text:
        failures.append("§10 缺门禁 JSON 句柄")
    if "FAIL=7 UNVERIFIED=2" not in text:
        failures.append("§10 缺 FAIL=7 UNVERIFIED=2 实测登记")
    # 正文一致性 ①：旧数字/旧名单黑名单，命中即判红（防半修正态假绿）
    for s in STALE_STRINGS:
        if s in text:
            failures.append("正文残留旧串 " + s)
    # 正文一致性 ②：§2.3 全量表的 disposition 列与批次数据对齐
    disp = {}
    for m in re.finditer(r"^\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*[^|]+\|\s*([^|]+?)\s*\|", text, re.M):
        disp[m.group(2).strip()] = m.group(3).strip()
    for it in batch["P0"]:
        if disp.get(it["slug"]) != "P0":
            failures.append("§2.3 表 " + it["slug"] + " disposition=" + str(disp.get(it["slug"])) + " 期望 P0")
    for it in batch["holds"]:
        if "protected" in it.get("reason", ""):
            if "PROTECTED_HOLD" not in disp.get(it["slug"], ""):
                failures.append("§2.3 表保护件 " + it["slug"] + " 未标 PROTECTED_HOLD")
    # 正文一致性 ③：P0-BATCH 回滚块 undo 名单恰等于 5 个 P0 slug 且不含保护件
    p0_expected = set(x["slug"] for x in batch["P0"])
    protected = set(x["slug"] for x in batch["holds"] if "protected" in x.get("reason", ""))
    bb = next((b for b in blocks if anchor_info(b["lines"]).get("BATCH") == "P0-BATCH"), None)
    if bb is None:
        failures.append("缺 P0-BATCH 回滚块")
    else:
        joined_bb = "\n".join(l for _, l in bb["lines"])
        got = set(re.findall(r"undo --file .D:/global_skills/([^/]+)/SKILL\.md.", joined_bb))
        if got != p0_expected:
            failures.append("P0-BATCH undo 名单不一致 got=" + str(sorted(got)) + " expected=" + str(sorted(p0_expected)))
        if got & protected:
            failures.append("P0-BATCH 回滚块含保护件 " + str(sorted(got & protected)))
    # 正文一致性 ④：守恒数字与 batches.json 对齐
    if "57 = P0 5 + P1 24 + P2 28" not in text:
        failures.append("正文缺 57 = P0 5 + P1 24 + P2 28")
    if "57+11+9 = 77" not in text:
        failures.append("正文缺 57+11+9 = 77")
    # 守恒
    if not print_stats(batch):
        failures.append("守恒 FAIL")
    print("[PLAN] file=" + PLAN)
    print("[PLAN] sha256=" + hashlib.sha256(text.encode("utf-8")).hexdigest()[:16])
    print("[PLAN] rollback_blocks=" + str(len(blocks)) + " labels=" + ",".join(labels))
    print("[ROLLBACK] 条数=" + str(total_cmd) + " 通过数=" + str(passed_cmd) +
          " 失败数=" + str(total_cmd - passed_cmd))
    if verbose:
        for b in blocks:
            print("  [BLOCK] " + json.dumps(anchor_info(b["lines"]), ensure_ascii=False) +
                  " lines=" + str(len(b["lines"])))
    return (len(failures) == 0), failures, {"blocks": len(blocks), "cmds": total_cmd, "passed": passed_cmd}


def main():
    text = read_text(PLAN)
    with open(BATCH, "r", encoding="utf-8") as f:
        batch = json.load(f)
    if "--stats" in sys.argv:
        ok = print_stats(batch)
        return 0 if ok else 1
    if "--negative-control-protected" in sys.argv:
        # 内存副本注入半修正态缺陷：把 P0-BATCH 的 chaoshi-web-deploy undo 换成注册表保护件。
        bad = "undo --file " + chr(34) + "D:/global_skills/A-skill-manager/SKILL.md" + chr(34)
        good = "undo --file " + chr(34) + "D:/global_skills/chaoshi-web-deploy/SKILL.md" + chr(34)
        mutated = text.replace(good, bad)
        if mutated == text:
            print("[NEGCTRL:ERROR] P0-BATCH 未找到 chaoshi-web-deploy undo 行")
            return 2
        ok, failures, st = evaluate(mutated, batch, False)
        if ok:
            print("[NEGCTRL:GREEN] P0-BATCH 注入保护件后判据仍绿，正文一致性门失效")
            return 1
        hit = [f for f in failures if "P0-BATCH" in f]
        if not hit:
            print("[NEGCTRL:GREEN] 仅旧串黑名单命中、P0-BATCH 一致性门未抓到，判据不充分")
            return 1
        print("[NEGCTRL:RED] P0-BATCH 注入保护件被正文一致性门检出（failures=" + str(len(failures)) + "，P0-BATCH 相关=" + str(len(hit)) + "）")
        return 0
    if "--negative-control" in sys.argv:
        target = None
        for b in rollback_blocks(text):
            if anchor_info(b["lines"]).get("BATCH") == "P1":
                target = b
                break
        if target is None:
            print("[NEGCTRL:ERROR] 找不到 P1 回滚块")
            return 2
        lines = text.split("\n")
        mutated = "\n".join(lines[:target["start"] - 1] + lines[target["end"]:])
        ok, failures, st = evaluate(mutated, batch, False)
        if ok:
            print("[NEGCTRL:GREEN] 删掉 P1 回滚块后判据仍绿，负控失效")
            return 1
        print("[NEGCTRL:RED] 删除 P1 回滚块被检出（failures=" + str(len(failures)) + "）")
        return 0
    ok, failures, st = evaluate(text, batch, True)
    if not ok:
        for f in failures[:40]:
            print("[FAIL] " + f)
        print("[PLAN:CHECK] FAIL failures=" + str(len(failures)))
        return 1
    print("[PLAN:CHECK] PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
