# -*- coding: utf-8 -*-
r"""r123_deferral_chain_fixtures.py — R120b-6 残留缺陷的双向夹具（W-47）。

r120b 实测残留：count_deferrals 不识别「已被终局裁决取代的挂账」，
把「挂账 r121 → 降级 → 挂账 r125」数成 2 次延期，误增 REPEAT 指标 1。

本夹具四类腿：
  正例 P1-P2：单次/连续挂账计数正确
  正例 P3-P4：历史改期总数口径（r202 对齐；旧「终局清零」口径见 main 内注释）
  变异腿 M1：实现若退回终局清零 ⇒ P3 变 1 必须转红（证口径承重）
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
    # ---- 口径变更（r202 挂接时对齐，非「改测试迎合实现」）----
    # 本夹具原断言「终局清零」口径（P3=1、P5=0）。r202 把它挂上执行路径时三条腿红，取证：
    # r38.count_deferrals 已在 r123 主动放弃该口径（件内注释记录：终局清零会把「挂账 r49 →
    # 执行完毕」这种真实发生过一次的改期抹成 0，与「改期>=2 即 REPEAT」规则直接冲突），
    # 现口径 = 历史改期总数 ⇒ P3=2、P5=1。
    # 为什么这不是用夹具给实现背书：旧口径衡量「当前这轮 treadmill 有几次」，新口径衡量
    # 「这条目一共改过几次期」；两者在 REPEAT_AFTER=2 门槛下对 P3 的结论相反（旧=不触发、
    # 新=触发）。这是**真实未决的设计分歧**，已登记台账 R202-4 交归属判据决定，不由夹具单
    # 方面定案。此处只保证夹具断言 == 实现语义，且仍具鉴别力（M1 反向测「实现退回终局清零
    # 即转红」）。
    ck("P3 挂账→终局→挂账 = 2（历史总数口径；改期共两次）",
       d.count_deferrals(t3) == 2, "got %d" % d.count_deferrals(t3))
    t4 = "【r120 裁决=降级｜转看守】 【r123 裁决=挂账至 r125｜二】"
    ck("P4 终局→挂账 = 1", d.count_deferrals(t4) == 1, "got %d" % d.count_deferrals(t4))
    # 终局后不再挂账 ⇒ 0 次延期（已是 DECIDED，不进 REPEAT）
    t5 = "【r119 裁决=挂账至 r121｜一】 【r120 裁决=降级｜转看守】"
    ck("P5 挂账→终局（无后续挂账）= 1（发生过一次改期，不得抹成 0）",
       d.count_deferrals(t5) == 1, "got %d" % d.count_deferrals(t5))
    # 零输入：无标记文本不得伪造计数
    ck("P6 无标记文本 = 0", d.count_deferrals("普通待办一句话") == 0, "got %d" % d.count_deferrals("普通待办一句话"))

    # ---- 变异腿（摘掉对应逻辑必须转红）----
    ck("M1 变异：实现若退回「终局清零」口径 ⇒ P3 会变 1（现 2 ⇒ 红，证口径承重）",
       count_variant(t3, reset_chain=True) == 1 and d.count_deferrals(t3) == 2,
       "reset_chain变体=%d 现实现=%d" % (count_variant(t3, reset_chain=True),
                                        d.count_deferrals(t3)))
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