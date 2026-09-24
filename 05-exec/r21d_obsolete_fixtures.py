# -*- coding: utf-8 -*-
r"""r21d_obsolete_fixtures.py — 「转办件过期检测」夹具（TDD：先看红，再实现被测件）。

为什么要有它：2026-09-24 r20b 我把三项判据转办给焚诀归属会话（C31′/C32′/C33′ 让号），
r21c 复测才发现归属方**已自落 C31/C32** ⇒ 我方转办件里的两项早已过期，若继续外推就是
让人做无用功（同日另一会话在同一台账留下同型判据：「教训未升格为条目 = 未闭环」）。
本夹具把「外推前先复测归属方是否已自落」从**自觉**变成**会拦人的东西**。

被测对象：`05-exec/transmit_obsolescence_check.py`，契约：
    parse_landed(verify_text: str) -> dict {C号: 判据标题}
    evaluate(proposals: list[dict], landed: dict, threshold=0.5, min_hits=2) -> list[dict]
      · proposal = {"pid", "title", "keywords": [str, ...]}
      · verdict ∈ {OBSOLETE, VALID, UNVERIFIED}
      · 命中定义：单条已落判据标题内出现的 keywords 条数 = hits
        hits >= min_hits 且 hits/len(keywords) >= threshold ⇒ 该判据覆盖此转办项
      · landed 为空 / keywords 为空 ⇒ UNVERIFIED（禁止把「取不到真相源」判成任何一种结论，R247）
    退出码：0 无过期项 / 1 有过期项（正在外推过期件 ⇒ 拦）/ 2 真相源或输入不可用
"""

import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = HERE / "transmit_obsolescence_check.py"
VERIFYSRC = Path(r"C:\Users\37533\Desktop\workspace\焚诀\eval\verify_truth_consistency.py")

R = []


def ck(name, cond, detail=""):
    R.append(bool(cond))
    print("%s %-58s %s" % ("PASS" if cond else "FAIL", name, detail if not cond else ""))


def load_src():
    if not TARGET.exists():
        return None
    return TARGET.read_text(encoding="utf-8")


def load_mod(src=None, alias="tob"):
    src = src if src is not None else load_src()
    if src is None:
        return None
    fd, tmp = tempfile.mkstemp(suffix=".py", prefix="tob_")
    os.close(fd)
    Path(tmp).write_text(src, encoding="utf-8")
    spec = importlib.util.spec_from_file_location(alias, tmp)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    os.unlink(tmp)
    return mod


def V(res, pid):
    for r in res:
        if r["pid"] == pid:
            return r["verdict"]
    return None


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    src = load_src()
    if src is None:
        print("FAIL RED 前置：被测件不存在 %s" % TARGET)
        return 1
    m = load_mod()

    # ── 层 a：已知答案 ──────────────────────────────────────────────
    landed = {
        "C25": "L1注入硬预算棘轮（P1E-2）",
        "C29": "index.md 与派生评分产物对账（P0-14）",
        "C30": "路由静态表目标存活与空洞棘轮（P1-17）",
        "C31": "L1注入预算归因台账（7-E）",
        "C32": "空基线已初始化台账（7-C）",
    }
    props = [
        {"pid": "P1", "title": "目录注意力税棘轮", "keywords": ["目录", "注意力", "棘轮"]},
        {"pid": "P2", "title": "注入区口径合一", "keywords": ["注入", "预算", "台账", "归因"]},
        {"pid": "P3", "title": "计数断言内容级门禁", "keywords": ["计数", "断言", "对账"]},
    ]
    res = m.evaluate(props, landed)
    ck("a01 单词巧合不误判（P1 只命中「棘轮」1 词 → VALID）", V(res, "P1") == "VALID", str(res))
    ck("a02 真实过期件被抓到（P2 → OBSOLETE）", V(res, "P2") == "OBSOLETE", str(res))
    ck("a03 同形词不同义不误判（P3 仅「对账」→ VALID）", V(res, "P3") == "VALID", str(res))
    # 实测校正：C25「L1注入硬预算棘轮」也含 2/4 词（注入、预算）⇒ 与 C31 同时入 matched。
    # 这是规则的**已知行为**（matched 列的是「所有覆盖者」，供人工复核；verdict 只取决于是否非空），
    # 不是缺陷。原断言写成「恰好等于 C31」是我对结论口径的预期错置 ⇒ 按 R263 改判据表达，不改数据。
    ck("a04 OBSOLETE 必带命中判据号（含精确覆盖者 C31，且不虚构）",
       "C31" in res[1]["matched"] and set(res[1]["matched"]) <= set(landed), str(res[1]))
    ck("a05 结论三态封闭", {r["verdict"] for r in res} <= {"OBSOLETE", "VALID", "UNVERIFIED"})

    ck("a06 landed 为空 → 全部 UNVERIFIED（禁把取不到当结论）",
       all(r["verdict"] == "UNVERIFIED" for r in m.evaluate(props, {})))
    ck("a07 keywords 为空 → UNVERIFIED",
       m.evaluate([{"pid": "X", "title": "t", "keywords": []}], landed)[0]["verdict"] == "UNVERIFIED")
    ck("a08 双词命中但占比不足阈值 → VALID",
       V(m.evaluate([{"pid": "Y", "title": "t", "keywords": ["注入", "预算", "评分", "端点", "路由"]}],
                    landed), "Y") == "VALID")
    ck("a09 阈值可放宽（threshold=0.4 时 a08 变 OBSOLETE）",
       V(m.evaluate([{"pid": "Y", "title": "t", "keywords": ["注入", "预算", "评分", "端点", "路由"]}],
                    landed, threshold=0.4), "Y") == "OBSOLETE")
    ck("a10 min_hits 生效（单关键词命中不算覆盖）",
       V(m.evaluate([{"pid": "Z", "title": "t", "keywords": ["归因"]}], landed), "Z") == "VALID")
    ck("a11 parse_landed 能解析真实注册面（≥10 条且含 C31）",
       len(m.parse_landed(VERIFYSRC.read_text(encoding="utf-8"))) >= 10
       and "C31" in m.parse_landed(VERIFYSRC.read_text(encoding="utf-8")))
    ck("a12 非注册面输入不抛异常（返回空 dict）", m.parse_landed("没有判据的文本") == {})
    ck("a13 输出必带 why 字段（可解释，供人工复核）",
       all(r.get("why") for r in res))
    ck("a14 pid 重复不互相覆盖（逐条独立判定）",
       len(m.evaluate([props[1], dict(props[1], pid="P2b")], landed)) == 2)

    # ── 层 b：真实接线 ─────────────────────────────────────────────
    prop_file = HERE.parent / "06-benchmark" / "transmit_proposals.json"
    ck("b01 转办登记表存在且 schema 正确",
       prop_file.exists() and json.loads(prop_file.read_text(encoding="utf-8"))["schema"]
       == "zijian-transmit-proposal-v1")
    if prop_file.exists():
        p = subprocess.run([sys.executable, str(TARGET), "--json"], capture_output=True,
                           text=True, encoding="utf-8", errors="replace")
        out = (p.stdout or "").strip()
        ck("b02 真跑退出码 1（存在过期项时必须拦）", p.returncode == 1, "rc=%s" % p.returncode)
        try:
            data = json.loads(out.splitlines()[-1])
            ck("b03 JSON 可解析且含 3 项结论", len(data["results"]) == 3, out[:120])
            ck("b04 真实结论与人工复测一致（注入区合一=OBSOLETE）",
               V(data["results"], "inject_union_merge") == "OBSOLETE", str(data["results"]))
        except Exception as e:
            ck("b03 JSON 可解析且含 3 项结论", False, repr(e))
        ck("b05 人读面打印标记行", "[TRANSMIT:" in out)
    # 真相源不可用 → 必须 exit 2（不得静默放行）
    bad = subprocess.run([sys.executable, str(TARGET), "--verify-src",
                          str(HERE / "__no_such_file__.py")], capture_output=True, text=True)
    ck("b06 真相源缺失 → exit 2（R247 不静默放行）", bad.returncode == 2, "rc=%s" % bad.returncode)

    # ── 变异对照（三条硬判据之②：把判据改坏，夹具必须变红）──────────
    # 灵敏度集：覆盖两个独立下限（min_hits 与占比阈值），否则任一旋钮被改坏都不会翻结论
    SENS = props + [
        {"pid": "Z", "title": "单词巧合", "keywords": ["归因"]},                      # hits=1, ratio=1.0
        {"pid": "Y5", "title": "多词低占比", "keywords": ["注入", "预算", "评分", "端点", "路由"]},  # hits=2, ratio=0.4
    ]
    base = {r["pid"]: r["verdict"] for r in m.evaluate(SENS, landed)}
    ck("a15 对照组：Z 与 Y5 均未判过期（两个下限各自生效）",
       base["Z"] == "VALID" and base["Y5"] == "VALID", str(base))

    def probe(mut):
        got = {r["pid"]: r["verdict"] for r in mut.evaluate(SENS, landed)}
        empty = {r["pid"]: r["verdict"] for r in mut.evaluate(SENS, {})}
        return got != base or set(empty.values()) & {"VALID", "OBSOLETE"}

    muts = {
        "min_hits 下限失效（2→1）": (r"min_hits: int = 2", "min_hits: int = 1"),
        "占比阈值失效（0.5→0.0）": (r"threshold: float = 0.5", "threshold: float = 0.0"),
        "空真相源被当无过期（治静默放行）": (r'return "UNVERIFIED"', 'return "VALID"'),
        "去掉 2 词下限（只按占比）": (r"hits >= min_hits", "hits >= 1"),
    }
    flipped = 0
    for name, (pat, rep) in muts.items():
        m2 = re.search(pat, src)
        if not m2:
            ck("变异锚点在位：%s" % name, False, "锚点失配，变异未生效")
            continue
        mutated = src[:m2.start()] + rep + src[m2.end():]
        try:
            got = probe(load_mod(mutated, alias="tob_mut"))
            flipped += bool(got)
            ck("变异被拦：%s" % name, got)
        except Exception as e:
            flipped += 1
            ck("变异被拦：%s" % name, True, "变异后夹具即报错 %s" % type(e).__name__)
    ck("变异组 4/4 全部使结论改变（未变异对照组见 a15）", flipped == 4, "%d/4" % flipped)

    print("-" * 70)
    bad_n = R.count(False)
    print("%s r21d 转办过期检测夹具 %d/%d" % ("[GATE:stub-pass]" if not bad_n else "[GATE:stub-fail]",
                                            R.count(True), len(R)))
    return 0 if not bad_n else 1


if __name__ == "__main__":
    raise SystemExit(main())
