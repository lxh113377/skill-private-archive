# -*- coding: utf-8 -*-
r"""r21e_land3.py — r21e 收尾一次性落盘（五处，逐处守卫 + 写后读回 + 控制符自检）。

前置事实（实测，避免重复劳动）：07 缺 r21e 两条与 AGENTS 缺控制符扫描挂链（前一次脚本因自身
断言先失败而未写入）；`feedback-user-command-supreme.md` 22:5x 实测不在 GM 根、23:3x 复测已恢复
⇒ 原先准备写的"死引用"结论**不成立**，改为如实记录"当天被移动过一次"。
"""
import io
import os
import sys

WS = r"C:\Users\37533\Desktop\workspace\自建skill优化"
AG = WS + r"\memory\AGENTS.md"
N07 = WS + r"\memory\07-next-steps.md"
RPT = WS + r"\06-benchmark\全量对标报告_r19_2026-09-24.md"
P49 = r"D:\global_memory\lessons\lessons.part49.md"
P50 = r"D:\global_memory\lessons\lessons.part50.md"
LOG = r"D:\global_memory\memory\2026-09-24.md"
KEY = "session=qd-zijian-r21e-0924"
CAP = 4096
B = chr(96)
BSL = chr(92)


def rd(p):
    return io.open(p, encoding="utf-8-sig").read()


def wr(p, t):
    assert chr(8) not in t and chr(0) not in t and chr(127) not in t, "待写文本含控制符"
    with open(p, "wb") as f:
        f.write(t.encode("utf-8"))


def step_agents():
    t = rd(AG)
    chain = "python 05-exec/ratchet_gate.py"
    if "control_char_scan" in t:
        print("[AGENTS] 已挂链")
        return True
    assert t.count(chain) == 1, "链尾锚点命中 %d" % t.count(chain)
    t = t.replace(chain, chain + " && python 05-exec/control_char_scan.py .")
    t = t.replace("> 四条全 `[GATE:fixture-pass]`", "> 五条全 `[GATE:fixture-pass]`")
    note = ("> 第五条 " + B + "[CTRL:CLEAN]" + B + " = 全仓无非法控制符（C0 ∪ {0x7f DEL} 减制表/换行/回车）。"
            "它拦的是「肉眼看不见、但会让引用检索不到」这一类：实测当天四轮复现，含被修文件自身与受管根两处死引用。")
    lines = t.split("\n")
    idx = [i for i, l in enumerate(lines) if l.startswith("> 判据可信度本身由")]
    assert len(idx) == 1, "说明行锚点命中 %d" % len(idx)
    lines.insert(idx[0], note)
    wr(AG, "\n".join(lines))
    ok = "control_char_scan" in rd(AG) and "[CTRL:CLEAN]" in rd(AG)
    print("[AGENTS] 挂链+说明=%s" % ok)
    return ok


def step_07():
    s = rd(N07)
    a2 = "- [ ] **【P0 新立判据·r21d】**"
    assert s.count(a2) == 1, "插入锚点命中 %d" % s.count(a2)
    add = ("- [ ] **【r21e 控制符扫描（已挂必跑链第 5 条）】** " + B + "05-exec/control_char_scan.py" + B +
           " 脏集 = C0 ∪ {0x7f DEL} - 制表/换行/回车；跳二进制但如实登记 skipped；空输入面 exit 2（判据面为空不得判过）。"
           "夹具 " + B + "05-exec/r21e_control_char_fixtures.py" + B + " 22/22（红阶段先看红、变异 3/3 被拦）。"
           "**首跑抓到三处真缺陷**：我自己 " + B + "lessons.part49.md" + B + " 残留 2 个退格符（先前声称已清零，"
           "实为重写脚本从未执行 ⇒ **断言 ≠ 执行**）；受管根 " + B + "A-project-handoff/references/version-history.md" + B +
           " 第 38 行两个 NUL 把 " + B + "02-structure.md" + B + "/" + B + "03-tech-stack.md" + B + " 写成死引用"
           "（已 rule_editor 修复 5148d79 + 镜像单文件同源 37,333B）；判据自身漏 DEL，而 DEL 恰真出现在我源码里 ⇒ 定义扩展。"
           "取值：" + B + "python 05-exec/control_char_scan.py ." + B + "（期望 " + B + "[CTRL:CLEAN]" + B + "）。")
    add2 = ("- [ ] **【r21e 证据可解析性 + 归因抬基线】** " + B + "upgrade_footer_gate.py" + B + " 的 " + B + "RE_EVID" + B +
            " 原只校形状，形状合格却指不到东西的假锚照样放行。边界测量（" + B + "evidence_resolvability_measure.py" + B +
            "，近 3 日 97 条已闭环声明）：可解析 52 / 形状合规但解析不到 37（38.1%）/ 形状不合规 8。据此分三级："
            + B + "FAKE" + B + "（路径不存在、或 backup ID 在回滚目录与五仓 git 对象全无 ⇒ 阻断，仅 4/97 不可事后合理化）、"
            + B + "STALE" + B + "（文件在但版本 token 被后续提交推走 ⇒ 只告警，追溯拦人即误伤 18/97）、" + B + "SKIP" + B +
            "（体系外绝对路径 ⇒ 不判，防误伤第三方端点）；同时形状层 V 前缀改为可选（真实文件写的是裸值 "
            + B + "version: 10.70.0" + B + "，只收 V 前缀等于奖励美化而非真实）。夹具 " + B + "05-exec/r21e_gate_probe.py" + B +
            " 5/5（红阶段：伪造 backup 锚打补丁前 rc=0 放行、补丁后 rc=1）。配套 " + B + "ratchet_gate.py" + B +
            " 新增唯一合法上调通道 " + B + "--raise-baseline" + B + "（commit+path+delta+reason 四要素、delta 与实增逐字节相等、"
            "path 须在注入面成员内、commit 须能在该仓解析；无增长时拒绝抬，防刷账），并永久留账 " + B + "attributed_raises" + B +
            "；本轮实测用它接受 +447B（并行会话立 #23 所致，非本仓动作），基线 86,346→86,793。夹具 "
            + B + "05-exec/r21e_ratchet_attrib_fixtures.py" + B + " 16/16（含变异 4/4）。取值：" + B + "python 05-exec/ratchet_gate.py" + B +
            "（期望 " + B + "[RATCHET:PASS]" + B + " 且打印留账 1 条）。")
    note = ("**⚠️ 复测注（r21e 23:3x，原文一字未改）**：本行引用的 " + B + "feedback-user-command-supreme.md" + B +
            " 在 22:5x 实测一度不在 " + B + "D:" + BSL + "global_memory" + BSL + "` 根下（当时判定为死引用），"
            "23:3x 复测**已恢复且索引重新指向** ⇒ 死引用结论不成立，如实改记为「当天被移动过一次」；"
            "本行权威双存点（" + B + "core" + BSL + BSL + "behavior_core.md" + B + " #23 + 该 feedback 文件）现均可解析。")
    a3 = "幂等只许用「原子替换 / 先备份」实现，不得用跳过执行实现。"
    if s.count(a3) >= 1 and "复测注（r21e 23:3x" not in s:
        s = s.replace(a3, a3 + note, 1)
    s = s.replace(a2, add + "\n" + add2 + "\n" + a2, 1)
    wr(N07, s)
    b = rd(N07)
    ok = all(k in b for k in ["r21e 控制符扫描", "r21e 证据可解析性", "复测注（r21e 23:3x"])
    print("[07] 三条在位=%s | %dB" % (ok, len(b.encode("utf-8"))))
    return ok


def step_rpt():
    t = rd(RPT)
    if "## 14. r21e" in t:
        print("[报告] §14 已在位")
        return True
    add = """

## 14. r21e：把「已闭环」从一句承诺变成一条能跑的检查
三条方法论，全部由实测逼出来，不是设计出来的：

1. **判据必须能解析，不能只能匹配形状。** `RE_EVID` 那条正则只证明锚点**长得像**证据。测量结果
   （`06-benchmark/evidence_resolvability_measure.json`，近 3 日 97 条已闭环声明）：38.1% 解析不到，
   里面既有"引用了不存在的文件"，也有"backup ID 凭空写的"。于是分级必须按**可否事后合理化**划：
   路径/回滚件全无 = 阻断（4/97）；token 被后续提交推走 = 只告警（18/97 —— 声明当时可为真，追溯拦人就是误伤）。
   同时把形状层的 `V` 前缀改成可选：文件里写的是 `version: 10.70.0`，只收 `V10.70.0` 等于**奖励美化而非真实**。
2. **上调判据要有唯一通道，且必须留账。** 棘轮只降不升是对的，但本轮它被**外部合法增长**挡下：+447B 来自
   并行会话往 `behavior_core.md` 立 #23（用户明令）。既不放宽判据、也不 revert 他人动作、又不永久卡死自己，
   办法是开一条 `--raise-baseline`：四要素齐备 + delta 逐字节相等 + path 在注入面内 + commit 可在该仓解析，
   成功后写进 `attributed_raises`（条数与理由常驻可查），并拒绝"现状没长大也要抬"——否则账本会被当装饰刷。
3. **新判据要能反身扫自己。** 控制符扫描器上线后第一个抓到的就是我：`lessons.part49.md` 里 2 个退格符
   （我先前声称已清零，实为**重写脚本从未执行**），随后在受管根抓到 2 个 NUL 落在文件名首位
   （`02-structure.md`/`03-tech-stack.md` 变成 grep 不到的死引用）。它还暴露自己定义的洞：只查 `<0x20` 会漏
   DEL(0x7f)，而 DEL 恰好真的出现在我写的源码里 ⇒ 脏集扩为 C0 ∪ {0x7f} - 合法空白。

**边界（防借壳复活）**：本轮全部判据只约束**写法与落盘**，一律不得用于判定「本轮要不要干活」；
重复指令按 `behavior_core.md` #23 一律整跑。之所以特意写下这句：同一天里"把幂等做成跳过执行"已经犯过一次。

**对原始对标七维的回填**：这轮补的是「可扩展性」里最难的一项——**判据的可信度**本身。对标看到的
成熟项目（AAS 的 `--self-test`、ai-brain-starter 的 driftignore 带理由、superpowers 的 deterministic gate）
共同点不是"有门禁"，而是**门禁自己会被测**：夹具、变异、量误伤面。本仓这三样现在都有了。
"""
    wr(RPT, t.rstrip("\n") + add)
    b = rd(RPT)
    ok = "## 14. r21e" in b
    print("[报告] §14=%s | %dB" % (ok, len(b.encode("utf-8"))))
    return ok


def step_lessons():
    if os.path.exists(P50):
        print("[lessons] part50 已存在")
        return True
    sz = os.path.getsize(P49)
    entry = """# lessons.part50

> 2026-09-24 r21e 新建。换卷理由 = 旧卷 `lessons.part49.md` 现 **3,243B**（上限 4,096B），本批条目 **~1,180B**，追加即破硬上限 ⇒ 按 ≤4KB 规则换卷；part49 条目零改写零删除。

### [2026-09-24] 🔴 门禁只校验「证据长得像证据」，等于把自证交给运气
trigger: 97 条已闭环声明 38.1% 解析不到 | 写footer,门禁判据,锚点校验 | 记忆系统,门禁,python
- **问题：** 门禁要求 `绝对路径 + #版本行:Vx.y.z`，但**从不验证路径是否存在、token 是否在文件里**。近 3 日 97 条已闭环声明实测 37 条解析不到，含引用不存在的文件与凭空写的 backup ID
- **原因：** 形状校验只花一次正则，可解析性要读盘 + 查 git 对象，历史上一直只做前者；且形状层强制 `V` 前缀，而真实文件写的是裸值 `version: 10.70.0` ⇒ **诚实引用反被判不合规，加个 V 就过**（判据奖励美化而非真实）
- **解法：** ① 按"能否事后合理化"分三级：路径/回滚件全无 = 阻断（4/97）、token 被后续提交推走 = 只告警（18/97，追溯拦人即误伤）、体系外路径 = 不判；② 前缀改可选，真伪交给可解析性；③ 收严前先量误伤面（输出四类计数），按数据定阻断级别，不按感觉
- **元：** 来源=自建skill优化 r21e | 版本=upgrade_footer_gate 可解析性补丁 3466bb3 | 置信度=0.7（97 条实测样本） | 日期=2026-09-24 | 适用范围=记忆系统, 门禁, python, 多agent
"""
    if len(entry.encode("utf-8")) > CAP:
        print("[lessons 停手] 新卷超 4096B")
        return False
    wr(P50, entry)
    ok = os.path.getsize(P50) <= CAP and rd(P50).count("### [") == 1
    print("[lessons] part50=%s | %dB（旧卷 %dB 未动）" % (ok, os.path.getsize(P50), sz))
    return ok


def step_log():
    t = rd(LOG)
    if KEY in t:
        print("[GM] r21e 块已在位")
        return True
    blk = """
## 23:3x 自建skill优化 r21e（第六次标注驱动·把「已闭环」做成能跑的检查）
- 先复测自己：上一条两行标 `状态=已闭环`，但落点只是 lessons 与注释 = 自觉型，按 A-get-memory Step 2.7「下一个会话不做任何事还生效吗」判为未闭环 ⇒ 本轮补机器型。
- 四件落地：① `control_char_scan.py`（C0 ∪ {0x7f} - 制表换行回车，跳二进制但登记 skipped，空面 exit 2）挂进本仓必跑链第 5 条，夹具 22/22；② `upgrade_footer_gate.py` 证据可解析性（FAKE 阻断 / STALE 告警 / SKIP 不判）+ 形状层 V 前缀可选，夹具 5/5；③ `ratchet_gate.py` 唯一合法上调通道 `--raise-baseline`（四要素 + delta 逐字节相等 + path 在面内 + commit 可解析 + 无增长即拒）并永久留账，夹具 16/16（含变异 4/4）；④ 边界测量 `evidence_resolvability_measure.py`：近 3 日 97 条声明 = 可解析 52 / 形状合规但解析不到 37 / 形状不合规 8，**先量误伤面再决定阻断级别**。
- 新判据首跑全部反身抓到真缺陷：我自己 `lessons.part49.md` 2 个退格符（先前声称清零，实为重写脚本从未执行 ⇒ 断言 ≠ 执行）；受管根 `A-project-handoff/references/version-history.md` 第 38 行 2 个 NUL 把 `02-structure.md`/`03-tech-stack.md` 写成死引用（已修复 5148d79 + 镜像单文件同源 37,333B）；判据自身漏 DEL 而 DEL 真出现在我源码里 ⇒ 定义当场扩展。
- 棘轮被外部合法增长挡下并走通留账通道：+447B = 并行会话立 `behavior_core.md` #23（`055f9b5`）⇒ `基线 86,346→86,793，累计留账 1 条`，复跑 `[RATCHET:PASS]`。不放宽判据、不 revert 他人动作。
- 自我更正一处：原准备登记「`feedback-user-command-supreme.md` 是死引用」，23:3x 复测该文件**已恢复且索引重新指向** ⇒ 结论不成立，改记为"当天被移动过一次"（若当时直接落盘就是一条假记录）。
- 边界重申：本轮判据只约束**写法与落盘**，不得用于判定「本轮要不要干活」；重复指令按 #23 一律整跑。
- 门禁现状：`gates` = `mirror=fail noise=pass evolution=pass stub=pass`（mirror 唯一红项 = `A-get-memory\\SKILL.md`，本仓未触碰，R269 只登记）；焚诀 verify 32 PASS / 1 FAIL（其 index 面，外部）；本仓控制符全扫 0 命中。

【数据流假设】
来源: 三个夹具实跑（22/22、5/5、16/16，各含红阶段留痕与变异对照）+ 97 条历史声明的解析测量 + `git -C D:" + chr(92) + "global_memory cat-file -t 055f9b5` = commit + `os.path.getsize` 逐文件实测（26,593 / 37,333 / 3,243B）+ 受管根两笔提交 5148d79 / 3466bb3
流向: 测量 → 按「可否事后合理化」定分级 → 落判据（受管根走 rule_editor，本仓直写）→ 挂执行路径（必跑链第 5 条 + 每轮 footer 门禁）→ 回写 07 / 报告 §14 / lessons.part50 / 本日志 → 按文件白名单 add+commit 同串 → push → savepoint
结构: UTF-8 无 BOM；lessons 新卷卷首写换卷理由 + 旧卷字节数 + 本批字节数；棘轮基线新增 `attributed_raises`（commit/path/delta/reason/at/from_value/to_value）；footer [升级建议] 2 行，改法字段 15/22 字符均 ≤40，证据仅用 `#backup:<ID>` 合规形态
异常: 扫描器跳二进制但登记 skipped；空输入面 exit 2；无增长时拒绝归因上调；`A-get-memory` 与 `A-project-better` 多文件为他人在途（本仓未 add、未跑全局 -Fix）；本轮两次内联构造文本因引号/转义失败，全部改为脚本文件 + `chr()` 构造后归零

<!-- footer:begin session=qd-zijian-r21e-0924 ts=2026-09-24T23:40:00+08:00 -->
[skill清单] 本轮调用=2 个 (A-get-memory, A-project-handoff)
[升级建议] skill=A-get-memory | 五问=缺失步骤 | 改法=已闭环证据须可解析且先量误伤面 | 对照=已取(证据=97条实测37条解析不到；打补丁前伪造backup锚rc=0、补丁后rc=1，STALE 18条仅告警不误伤) | 状态=已闭环(证据=D:\\global_skills\\A-memory-start\\references\\upgrade_footer_gate.py#backup:A-memory-start.references.upgrade_footer_gate.py.20260924_231413_532936.bak)
[升级建议] skill=A-project-handoff | 五问=错误信息 | 改法=受管根文件名首位NUL清零并镜像同源 | 对照=已取(证据=该文件 0x00 由 2 处降为 0，两个文件名现均可 grep；镜像与源同哈希 37,333B) | 状态=已闭环(证据=D:\\global_skills\\A-project-handoff\\references\\version-history.md#backup:5148d79)
<!-- footer:end -->
"""
    wr(LOG, t.rstrip("\n") + "\n" + blk)
    b = rd(LOG)
    need = ["【数据流假设】", "来源:", "流向:", "结构:", "异常:", "[skill清单]", "[升级建议]", KEY]
    miss = [k for k in need if k not in b]
    print("[GM] 缺失=%s | %dB" % (miss or "-", os.path.getsize(LOG)))
    return not miss


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    rs = [("AGENTS", step_agents()), ("07", step_07()), ("报告", step_rpt()),
          ("lessons", step_lessons()), ("GM", step_log())]
    print("-" * 62)
    print("[LAND3] %s" % " | ".join("%s=%s" % (n, "OK" if v else "FAIL") for n, v in rs))
    return 0 if all(v for _n, v in rs) else 1


if __name__ == "__main__":
    raise SystemExit(main())
