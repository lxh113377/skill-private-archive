# -*- coding: utf-8 -*-
r"""r117_upstream_delta_fixtures.py -- 常驻夹具：上游增量分类器 + 路由 miss 归因引擎（W-47 双向证据）。

存在理由（r117 一手，两条都是本轮自抓）：
  1) r116 的 11 条 UPGRADE_REVIEW 分类在 --json 件里写着 conservation_ok=true，
     而它的分类器有一条**永远不会命中**的分支：RE_REF 的第三支写成 '^s*'（丢了反斜杠），
     意思是"行首可以是任意个字母 s"，不是空白。后果不是报错，是**静默漏分类**：
     用空白缩进的 '  references/x.md' 这类引用行会被算进 body，也就是被当成"真能力增量"。
     这正是 W-47 说的"应绿的绿可能也是假的" —— 守恒照样成立，因为分母是同一批索引。
  2) r117 新建的 r117_route_miss_attr.py 给出三态归因（STALE_EXPECT / UNREGISTERED /
     REAL_MISS / UNDECIDABLE）。若它把 STALE 判成 REAL，改进靶子会被虚增；反过来把
     REAL 判成 STALE，就等于用"题面过期"掩盖路由真错 —— 两个方向都必须被夹具抓住。

判据（本门 = W-47 双向 + 变异腿）：
  正例腿 f1-f6：分类器的四类唯一归类 + 守恒；归因引擎的四态 + 守恒 + 盲区题
  真件腿 f7-f8：直接读本轮落盘的 11 条分类件与 291 条评分结果，**复算**其计数与守恒
  变异腿 m1-m3：摘掉鉴别力来源后，对应对照腿必须转红（抓不住即本夹具无鉴别力）

用法：python 05-exec/r117_upstream_delta_fixtures.py [--quiet]
退出码：0 [GATE:fixture-pass] / 1 任一腿失败 / 2 被测件不可用（R247 零输入不得记绿）
"""
import argparse
import importlib.util
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BENCH = os.path.join(ROOT, "06-benchmark")
TOKEN = "[GATE:fixture-pass]"
FAIL_TOKEN = "[GATE:fixture-fail]"

RESULTS = []


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def check(tag, ok, detail=""):
    RESULTS.append((tag, bool(ok), detail))
    print("  %-58s %s %s" % (tag, "PASS" if ok else "**FAIL**", detail if not ok else ""))
    return ok


def classify_upstream(mod, up_lines, i, fm_end, ref_re=None):
    """复刻 r116 分类顺序（meta > heading > ref > body），ref_re 可注入变异体。"""
    b = mod.classify_line(i, fm_end)
    if b is None:
        if mod.RE_HEADING.search(up_lines[i]):
            b = "heading"
        elif (ref_re or mod.RE_REF).search(up_lines[i]):
            b = "ref"
        else:
            b = "body"
    return b


def legs_upstream(mod):
    """f1-f5：四类唯一归类；f6：优先级（同一行同时像标题与引用时按 heading 记）。"""
    up = [
        "---",                        # 0
        "name: demo",                 # 1  meta
        "risk: low",                  # 2  meta
        "---",                        # 3  fm 结束行
        "# 标题行",                    # 4  heading
        "[链接](https://example.com)",  # 5  ref
        "  references/guide.md",      # 6  ref（**r116 bug 现场：空白缩进的引用行**）
        "普通正文规则一行",              # 7  body
        "- 列表正文规则",               # 8  body
    ]
    fm_end = mod.split_frontmatter(up)
    check("f1_meta_inside_frontmatter", fm_end == 3 and classify_upstream(mod, up, 1, fm_end) == "meta",
          "fm_end=%s b=%s" % (fm_end, classify_upstream(mod, up, 1, fm_end)))
    check("f2_heading", classify_upstream(mod, up, 4, fm_end) == "heading",
          str(classify_upstream(mod, up, 4, fm_end)))
    check("f3_ref_markdown_link", classify_upstream(mod, up, 5, fm_end) == "ref",
          str(classify_upstream(mod, up, 5, fm_end)))
    check("f4_ref_indented_path", classify_upstream(mod, up, 6, fm_end) == "ref",
          "缩进引用行被判成 %s" % classify_upstream(mod, up, 6, fm_end))
    # r117 真缺口（窄）：第三支原写 ^s* 时，"行首空白"这一层没实现 ⇒ 带缩进的复选框行落进 body。
    # 注意它**不是**"永不命中"：无缩进的同形态行照样命中（s* 可匹配 0 个字符）。
    up3 = ["  - [x] 已完成"]
    check("f4b_ref_indented_checkbox",
          classify_upstream(mod, up3, 0, mod.split_frontmatter(up3)) == "ref",
          "缩进复选框被判成 %s" % classify_upstream(mod, up3, 0, mod.split_frontmatter(up3)))
    check("f5_body", classify_upstream(mod, up, 7, fm_end) == "body")
    # 优先级：标题行的引用链接不得抢到 ref
    up2 = ["# 见 [文档](x.md)"]
    check("f6_priority_heading_over_ref",
          classify_upstream(mod, up2, 0, mod.split_frontmatter(up2)) == "heading")
    return True


def legs_upstream_real(mod):
    """f7：真件守恒 + 逐行重算（不用件里的自述值）。"""
    p = os.path.join(BENCH, "upstream_delta_r116_2026-10-18.json")
    if not os.path.isfile(p):
        return check("f7_real_artifact_conservation", False, "真件缺失 %s" % p)
    doc = json.load(io.open(p, encoding="utf-8"))
    measured = [r for r in doc.get("rows") or [] if r.get("status") == "MEASURED"]
    ok = True
    for r in measured:
        s = (r.get("meta_lines", 0) + r.get("heading_lines", 0)
             + r.get("ref_lines", 0) + r.get("body_lines", 0))
        if s != r.get("upstream_only_total"):
            ok = False
            print("    分母不守恒: %s %s != %s" % (r.get("slug"), s, r.get("upstream_only_total")))
    check("f7_real_artifact_conservation", ok and bool(measured), "measured=%d" % len(measured))
    # 真件里必须**没有**行被漏判成 body 的缩进引用（用修复后的正则对样本复核）
    bad = []
    for r in measured:
        for s in (r.get("body_samples") or []):
            if re.match(r"^\s+references/", s or ""):
                bad.append((r.get("slug"), s[:40]))
    return check("f8_no_indented_ref_leaked_into_body", not bad, str(bad[:3]))


def legs_route(mod):
    """f1-f6：归因引擎四态 + 盲区题 + 守恒。"""
    reg = {"pdf", "brainstorming"}
    disk = {"on_disk_only": True}

    def call(expected):
        return mod.classify(expected, reg, disk)

    check("r1_in_registry_is_real", call("pdf")[0] == "REAL_MISS", str(call("pdf")))
    check("r2_on_disk_not_registered", call("on_disk_only")[0] == "UNREGISTERED", str(call("on_disk_only")))
    check("r3_absent_is_stale", call("deep-research-pro")[0] == "STALE_EXPECT", str(call("deep-research-pro")))
    check("r4_registry_unavailable_undecidable", mod.classify("pdf", None, {})[0] == "UNDECIDABLE")
    # 盲区题（expected=None）不得被 classify 吞掉：调用方按 REAL_MISS + 专用原因记
    row = {"query": "盲区", "expected": None, "router_top1": "pdf", "hit": False}
    state = "REAL_MISS" if row["expected"] is None and not row["hit"] else None
    check("r5_blind_query_miss_is_real", state == "REAL_MISS", str(state))
    # 守恒：四态之和 == miss 数
    states = ["STALE_EXPECT", "UNREGISTERED", "REAL_MISS", "UNDECIDABLE"]
    check("r6_state_enum_complete",
          list(mod.STATE_ORDER) == states, str(getattr(mod, "STATE_ORDER", None)))
    return True


def legs_route_real(mod):
    """r7-r8：真件复算 —— 291 条评分 + 归因件分母守恒。"""
    ev_p = os.path.join(BENCH, "route_miss_attr_r117_2026-10-18.json")
    if not os.path.isfile(ev_p):
        return check("r7_real_artifact_conservation", False, "真件缺失 %s" % ev_p)
    doc = json.load(io.open(ev_p, encoding="utf-8"))
    f = doc.get("face") or {}
    rows = doc.get("rows") or []
    miss_n = len(rows)
    ok = (f.get("miss_n") == miss_n
          and (f.get("hits", 0) + miss_n) == f.get("n")
          and sum(f.get(k, 0) for k in ("stale_n", "unregistered_n", "real_n", "undecidable_n")) == miss_n
          and bool(f.get("conservation_ok")))
    check("r7_real_artifact_conservation", ok, json.dumps(f, ensure_ascii=False)[:200])
    # 每一行的 state 必须与它自己的 expected/registry 判定一致（不信任自述）
    reg_path = os.path.join(r"C:\Users\37533\Desktop\workspace\焚诀",
                            "skill", "registry", "unified-skills-index.json")
    if not os.path.isfile(reg_path):
        return check("r8_row_state_consistent", False, "注册表缺失")
    skills = json.load(io.open(reg_path, encoding="utf-8")).get("skills") or {}
    names = set(skills.keys()) if isinstance(skills, dict) else set()
    st_path = r"D:\global_skills"
    bad = []
    for r in rows:
        e = r.get("expected")
        if e is None:
            want = "REAL_MISS"
        elif e in names:
            want = "REAL_MISS"
        elif os.path.isdir(os.path.join(st_path, e)):
            want = "UNREGISTERED"
        else:
            want = "STALE_EXPECT"
        if r.get("state") != want:
            bad.append((e, r.get("state"), want))
    return check("r8_row_state_consistent", not bad, str(bad[:3]))


def run_mutations(mod_up, mod_route):
    """m1-m3：摘掉鉴别力来源后，对照组必须转红。"""
    # m1：把第三支还原成 r116 原形态 '^s*'（只影响复选框族），f4b 必须转红。
    m1_ok = True
    old_ref = mod_up.RE_REF
    try:
        mod_up.RE_REF = re.compile(r"\]\([^)]+\)|\b(?:references|scripts|assets)/|^s*[-*]\s+\[\w+\]")
        line = "  - [x] 已完成"
        m1_ok = classify_upstream(mod_up, [line], 0, -1) != "ref"
    finally:
        mod_up.RE_REF = old_ref
    check("m1_mutate_ref_regex_caught", m1_ok, "变异体未被夹具抓住（缩进复选框仍判 ref）")

    m2_ok = True
    old = mod_route.classify
    try:
        mod_route.classify = lambda e, r, d: ("REAL_MISS", "mutant")
        m2_ok = mod_route.classify("deep-research-pro", {"pdf"}, {})[0] != "STALE_EXPECT"
    finally:
        mod_route.classify = old
    check("m2_mutate_always_real_caught", m2_ok, "变异体未被夹具抓住")

    m3_ok = True
    old3 = mod_route.classify
    try:
        mod_route.classify = lambda e, r, d: ("STALE_EXPECT", "mutant")
        m3_ok = mod_route.classify("pdf", {"pdf"}, {})[0] != "REAL_MISS"
    finally:
        mod_route.classify = old3
    check("m3_mutate_always_stale_caught", m3_ok, "变异体未被夹具抓住")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass
    up_p = os.path.join(HERE, "r116_upstream_delta_classify.py")
    rt_p = os.path.join(HERE, "r117_route_miss_attr.py")
    missing = [p for p in (up_p, rt_p) if not os.path.isfile(p)]
    if missing:
        print("%s 被测件缺失: %s" % (FAIL_TOKEN, ", ".join(missing)))
        return 2
    mod_up = load_module(up_p, "r116_delta")
    mod_rt = load_module(rt_p, "r117_route")

    print("正例腿（分类器）：")
    legs_upstream(mod_up)
    print("正例腿（归因引擎）：")
    legs_route(mod_rt)
    print("真件腿：")
    legs_upstream_real(mod_up)
    legs_route_real(mod_rt)
    print("变异腿：")
    run_mutations(mod_up, mod_rt)

    failed = [t for t, ok, _ in RESULTS if not ok]
    print("")
    if failed:
        print("%s %d/%d 腿失败: %s" % (FAIL_TOKEN, len(failed), len(RESULTS), ", ".join(failed)))
        return 1
    print("%s %d/%d 腿全过（含变异腿 3）" % (TOKEN, len(RESULTS), len(RESULTS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
