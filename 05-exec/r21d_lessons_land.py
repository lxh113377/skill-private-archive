# -*- coding: utf-8 -*-
r"""r21d_lessons_land.py — r21d 反哺落盘（三处，逐处守卫 + 写后读回 R213）。

① 修一处控制字符缺陷：并行会话写进 r21 报告「作废注」的路径含 **0x08 退格符**
   （`core\x08ehavior_core.md`，本意 = `core\behavior_core.md`）——它在 markdown 里被写成 `\b`
   又被解释成退格，结果任何 grep/跳转都解析不到那条权威依据。属 Step 2.3.1「错误信息」类
   （格式错、非语义改写），按 R241 不动其余正文。
② lessons.part49：新建卷 + 本批条目（换卷理由 + 旧卷字节数 + 本批字节数，按 V4.30.0 卷首格式）。
③ lessons.part46：给「整点等间隔=机器排程指纹」那条的**闸门建议**挂 `superseded_by` 反向锚
   （§9.6 有向失效；part46 现 3,884B，锚点必须 <112B 才不破 4,096B 硬上限）。

红线：命中数 != 期望即停手不写；写完读回实证。
"""
import io
import os
import sys

WS = r"C:\Users\37533\Desktop\workspace\自建skill优化"
LS = r"D:\global_memory\lessons"
REPORT = os.path.join(WS, "06-benchmark", "全量对标报告_r21_重复轮次闸门_2026-09-24.md")
P49 = os.path.join(LS, "lessons.part49.md")
P46 = os.path.join(LS, "lessons.part46.md")
CAP = 4096

NEW49 = """# lessons.part49

> 2026-09-24 r21d 新建。换卷理由 = 旧卷 `lessons.part48.md` 现 **3,944B**（上限 4,096B），本批条目 **~1,250B**，追加即破硬上限 ⇒ 按 ≤4KB 规则换卷，条目零改写、零删除。

### [2026-09-24] 🔴 对标来的机制必须先过「用户价值函数」这一关，否则越确定越有害
trigger: 把闸门给我去掉，怎么还拦截我任务执行 | 机制引进,对标,幂等,重复指令
- **问题：** r21 把四家对手共有的「确定性拒绝重复工作」机制移植进来（`repeat_round_guard.py` + 7 条排程 instruction 接线），实测确实拦下了 3 轮重跑；**代价是拦掉了用户要的活**——同日 r25 用户否决、r26 明令彻底删除，受管根 `c9fd23f` 撤回台账行、`102650b` 删除工具与夹具，7 条 instruction 还原原文。
- **原因：** 对标只比了「对方有 / 我们没有」这一维，**没比「对方的价值函数和我们的对不对得上」**：对手是 CI（幂等 = 省钱），这里是**委托式研究任务**（重发 = 要再要一轮结果，算力是用户已买的）。同一机制在前者是收益、在后者是损失，而 fail-closed 形态还会把它伪装成「判据在正常工作」。
- **解法：** ① 引进任何"收敛/跳过/降格"类机制前先问一句：**这省的是谁的钱？被省掉的那次执行是不是正是用户要的？**；② 幂等只许用「原子替换 / 先备份再写」实现，禁止用「跳过执行」实现（权威 = `D:\\global_memory\\core\\behavior_core.md` #23）；③ 已入库的同类口径要**当场清实体**（脚本+夹具+接线+台账行四处一起撤），只加"不建议用"是拦不住下一个会话照抄的。
- **元：** 来源=自建skill优化 r21→r26 全周期（同型二次复发） | 版本=behavior_core V41+#23 | 置信度=0.7（用户两次明令） | 日期=2026-09-24 | 适用范围=记忆系统, 多agent, 门禁, 对标
"""

ANCHOR46 = "### [2026-09-24] 🟡 整点等间隔会话日志 = 机器排程指纹；跨项目同指令用 lessons_usage 反查"
MARK46 = "> ⛔ superseded_by: lessons.part49.md#r21d (闸门作废, behavior_core#23)\n"


def rd(p):
    return io.open(p, encoding="utf-8-sig").read()


def wr(p, t):
    with open(p, "wb") as f:
        f.write(t.encode("utf-8"))


def step1():
    t = rd(REPORT)
    bad = "core\x08ehavior_core.md"
    n = t.count(bad)
    if n != 1:
        print("[1/3 跳过] 退格符路径命中 %d 次（期望 1）⇒ 不改" % n)
        return None
    if "\x08" in t.replace(bad, ""):
        print("[1/3 跳过] 文件仍含其它退格符，先人工确认")
        return None
    wr(REPORT, t.replace(bad, "core\\behavior_core.md", 1))
    back = rd(REPORT)
    ok = "core\\behavior_core.md" in back and "\x08" not in back
    print("[1/3] 控制字符修复=%s（读回 0x08 残留=%d）" % (ok, back.count("\x08")))
    return ok


def step2():
    if os.path.exists(P49):
        have = rd(P49)
        print("[2/3 跳过] part49 已存在（%dB，本批条目 %d 条）"
              % (os.path.getsize(P49), have.count("### [")))
        return None
    est = len(NEW49.encode("utf-8"))
    if est > CAP:
        print("[2/3 停手] 新卷本身 %dB 已破 %dB ⇒ 拆批" % (est, CAP))
        return False
    wr(P49, NEW49)
    back = rd(P49)
    ok = os.path.getsize(P49) <= CAP and "superseded" not in back and back.count("### [") == 1
    print("[2/3] 新卷 lessons.part49.md 落盘=%s | %dB ≤%d | 条目数=%d"
          % (ok, os.path.getsize(P49), CAP, back.count("### [")))
    return ok


def step3():
    t = rd(P46)
    size = os.path.getsize(P46)
    if "superseded_by: lessons.part49.md" in t:
        print("[3/3 跳过] 反向锚已在位")
        return None
    if t.count(ANCHOR46) != 1:
        print("[3/3 停手] 目标条目锚点命中 %d 次（期望 1）" % t.count(ANCHOR46))
        return False
    i = t.index(ANCHOR46)
    j = t.index("\n", t.index("- **元：**", i)) + 1
    new = t[:j] + MARK46 + t[j:]
    if len(new.encode("utf-8")) > CAP:
        print("[3/3 停手] 加锚后 %dB > %dB ⇒ 改挂他处" % (len(new.encode("utf-8")), CAP))
        return False
    wr(P46, new)
    back = rd(P46)
    ok = MARK46.rstrip("\n") in back and os.path.getsize(P46) <= CAP
    print("[3/3] part46 反向锚落盘=%s | %dB（原 %dB）| 条目数不变=%s"
          % (ok, os.path.getsize(P46), size, back.count("### [") == t.count("### [")))
    return ok


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    rs = [step1(), step2(), step3()]
    bad = [r for r in rs if r is False]
    print("-" * 62)
    print("[LAND] 三处守卫全过=%s | 需人工介入=%d" % (not bad, len(bad)))
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
