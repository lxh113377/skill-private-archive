# -*- coding: utf-8 -*-
r"""r21c_fix_evidence.py — 修正本轮（r21c）自己刚写入的 footer 证据锚点格式。

背景: `upgrade_footer_gate.py` RE_EVID 只接受「绝对路径 + #版本行:Vx.y.z」或「#backup:<ID>」，
      本轮第二行写成 `...inject_ratchet_baseline.json#inject_union_bytes:86346` 被当场拦下（exit 1）。
纪律: 只改**本会话本轮自己刚写的那一行**（非历史留痕，不触 R241）；命中数 != 1 即停手不写。
"""
import io
import os
import sys

LOG = r"D:\global_memory\memory\2026-09-24.md"
OLD = (r"[升级建议] skill=fenjue-verify | 五问=过期指令 | 改法=转办前先复测归属方是否已自落 | "
       r"对照=已取(证据=实测其已自落 C31 台账 6 条，我方 r20b 让号件过期，改为自己还注入面欠账) | "
       r"状态=已闭环(证据=C:\Users\37533\Desktop\workspace\自建skill优化"
       r"\06-benchmark\inject_ratchet_baseline.json#inject_union_bytes:86346)")
NEW = (r"[升级建议] skill=fenjue-verify | 五问=过期指令 | 改法=转办前先复测归属方是否已自落 | "
       r"对照=已取(证据=实测其已自落 C31 台账 6 条，我方 r20b 让号件过期，改为自己还注入面欠账) | "
       r"状态=已闭环(证据=C:\Users\37533\Desktop\workspace\自建skill优化"
       r"\06-benchmark\inject_ratchet_baseline.json"
       r"#backup:A-memory-start.SKILL.md.20260924_214500_246348.bak)")


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    txt = io.open(LOG, encoding="utf-8-sig").read()
    n = txt.count(OLD)
    if n != 1:
        print("[GUARD] 命中 %d 条（期望 1）⇒ 停手不写" % n)
        return 1
    BK = r"D:\global_memory_archive\_trash\rule_backup\A-memory-start.SKILL.md.20260924_214500_246348.bak"
    if not os.path.isfile(BK):
        print("[GUARD] 引用的回滚件不存在 ⇒ 停手不写：%s" % BK)
        return 1
    with open(LOG, "wb") as f:
        f.write(txt.replace(OLD, NEW, 1).encode("utf-8"))
    back = io.open(LOG, encoding="utf-8-sig").read()
    print("[FIX] 写后读回 new=%d old=%d 回滚件存在=%s | %dB"
          % (back.count(NEW), back.count(OLD), os.path.isfile(BK), os.path.getsize(LOG)))
    return 0 if back.count(NEW) == 1 and back.count(OLD) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
