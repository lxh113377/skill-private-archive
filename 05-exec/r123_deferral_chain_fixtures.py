# -*- coding: utf-8 -*-
r"""r123_deferral_chain_fixtures.py — R120b-6 残留缺陷的双向夹具（W-47）。

r120b 实测残留：count_deferrals 不识别「已被终局裁决取代的挂账」，
把「挂账 r121 → 降级 → 挂账 r125」数成 2 次延期，误增 REPEAT 指标 1。

本夹具四类腿：
  正例 P1-P2：单次/连续挂账计数正确
  正例 P3-P4：终局中断延期链（清零前置挂账）
  变异腿 M1：把「终局清零」逻辑摘掉 ⇒ P3/P4 必须转红（证鉴别力来自该逻辑）
  变异腿 M2：把「只数头部」逻辑摘掉（改用全文扁平）⇒ P2 必须转红
"""
import io, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import r38_debt_aging as d  # noqa: E402

RESULTS = []


def ck(label, cond, detail=""):
    RESULTS.append((label, bool(cond), detail))


def count_variant(text, *, reset_chain=True, head_only=True):
    """带开关的 count_deferrals 复刻，用于变异腿证伪。"""
    if head_only:
        heads = [h.group(2).strip() for h in d.RE_MARK_HEAD.finditer(text or "")]
    else:
        # 真摘「只数头部」= 全文扁平数「挂账至 rNN」出现次数（原因体里的引用也算）
        return len(re.findall(r"挂账至\s*r\d{1,3}", text or ""))
    if not heads:
        return len(d.RE_DEFERRAL.findall(text or ""))
    active = heads
    if reset_chain:
        last_final = -1
        for i, h in enumerate(heads):
            if re.match(r"(执行|降级|作废|保留)", h):
                last_final = i
        active = heads[last_final + 1:]
    return sum(1 for h in active if re.match(r"挂账至\s*r\d{1,3}", h))


def main():
    # ---- 正例 ----
    t1 = "【r121 裁决=挂账至 r123｜到期未动】"
    ck("P1 单次挂账 = 1", d.count_deferrals(t1) == 1, "got %d" % d.count_deferrals(t1))
    t2 = "【r119 裁决=挂账至 r121｜一】 【r121 裁决=挂账至 r123｜二】"
    ck("P2 连续两次挂账 = 2", d.count_deferrals(t2) == 2, "got %d" % d.count_deferrals(t2))
    t3 = "【r119 裁决=挂账至 r121｜一】 【r120 裁决=降级｜转看守】 【r123 裁决=挂账至 r125｜二】"
    ck("P3 挂账→终局→挂账 = 1（终局清零）", d.count_deferrals(t3) == 1, "got %d" % d.count_deferrals(t3))
    t4 = "【r120 裁决=降级｜转看守】 【r123 裁决=挂账至 r125｜二】"
    ck("P4 终局→挂账 = 1", d.count_deferrals(t4) == 1, "got %d" % d.count_deferrals(t4))
    # 终局后不再挂账 ⇒ 0 次延期（已是 DECIDED，不进 REPEAT）
    t5 = "【r119 裁决=挂账至 r121｜一】 【r120 裁决=降级｜转看守】"
    ck("P5 挂账→终局（无后续挂账）= 0", d.count_deferrals(t5) == 0, "got %d" % d.count_deferrals(t5))
    # 零输入：无标记文本不得伪造计数
    ck("P6 无标记文本 = 0", d.count_deferrals("普通待办一句话") == 0, "got %d" % d.count_deferrals("普通待办一句话"))

    # ---- 变异腿（摘掉对应逻辑必须转红）----
    ck("M1 摘「终局清零」⇒ P3 应变 2（现为 1 ⇒ 红）",
       count_variant(t3, reset_chain=False) == 2 and d.count_deferrals(t3) == 1,
       "variant=%d actual=%d" % (count_variant(t3, reset_chain=False), d.count_deferrals(t3)))
    _m2 = "【r119 裁决=挂账至 r121｜引用旧标记挂账至 r99】 【r121 裁决=挂账至 r123｜二】"
    ck("M2 摘「只数头部」⇒ 全文扁平数应把原因体引用算进来（3 ≠ 现 2 ⇒ 红）",
       count_variant(_m2, head_only=False) == 3 and d.count_deferrals(_m2) == 2,
       "variant=%d actual=%d" % (count_variant(_m2, head_only=False), d.count_deferrals(_m2)))

    fails = [r for r in RESULTS if not r[1]]
    for label, ok, detail in RESULTS:
        print("%s %s%s" % ("PASS" if ok else "FAIL", label, ("  <- " + detail) if detail else ""))
    print("\n夹具合计: %d 项，通过 %d，失败 %d" % (len(RESULTS), len(RESULTS) - len(fails), len(fails)))
    print("[GATE:fixture-pass]" if not fails else "[GATE:fixture-fail]")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())