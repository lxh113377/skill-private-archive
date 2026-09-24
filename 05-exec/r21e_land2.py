# -*- coding: utf-8 -*-
r"""r21e_land2.py — r21e 收尾落盘（四处，逐处守卫 + 写后读回）。

① 07 P0：r21e 两条（证据可解析性判据 + 归因抬基线通道）
② 报告 §14：本轮的**方法论**结论（判据要能解析、上调要能归因、豁免要能计数）
③ lessons：part49 已 3,243B，本批 ~1,150B 会破 4,096B ⇒ 新建 part50（卷首写换卷理由）
④ GM 日志：r21e 轮次块 + footer（含两条 [升级建议]，全部用合规锚点形态）
"""
import io
import os
import sys

WS = r"C:\Users\37533\Desktop\workspace\自建skill优化"
N07 = WS + r"\memory\07-next-steps.md"
RPT = WS + r"\06-benchmark\全量对标报告_r19_2026-09-24.md"
LS_DIR = r"D:\global_memory\lessons"
P49 = LS_DIR + r"\lessons.part49.md"
P50 = LS_DIR + r"\lessons.part50.md"
LOG = r"D:\global_memory\memory\2026-09-24.md"
KEY = "session=qd-zijian-r21e-0924"
CAP = 4096
B = chr(96)      # 反引号
Q = chr(34)      # 双引号


def rd(p):
    return io.open(p, encoding="utf-8-sig").read()


def wr(p, t):
    with open(p, "wb") as f:
        f.write(t.encode("utf-8"))


def step07():
    s = rd(N07)
    if "r21e 证据可解析性与归因抬基线" in s:
        print("[07] 已在位，跳过")
        return True
    add = ("- [ ] **【r21e 证据可解析性与归因抬基线】** 把 r21d 那条 " + B + "已闭环须可解析" + B + " 做成机器型："
           "`upgrade_footer_gate.py` 的 " + B + "RE_EVID" + B + " 原只校**形状**，形状合格却指不到东西的假锚照样放行"
           "（实测近 3 日 97 条已闭环声明 38.1% 解析不到）。现分三级：" + B + "FAKE" + B + "（路径不存在 / backup ID 在回滚目录"
           "与五仓 git 对象全无 ⇒ 阻断，实测仅 4/97，不可事后合理化）、" + B + "STALE" + B + "（文件在但版本 token 被后续提交推走 ⇒ 只告警，"
           "追溯拦人即误伤 18/97）、" + B + "SKIP" + B + "（体系外绝对路径 ⇒ 不判，防误伤第三方端点）。同时把形状层 " + B + "V" + B +
           " 前缀改为可选 —— 真实文件里写的是裸值，原判据等于奖励美化而非真实。夹具 " + B + "05-exec/r21e_gate_probe.py" + B + " 5/5"
           "（先实跑红：伪造 backup 锚在打补丁前 rc=0 放行）。配套：棘轮新增**唯一合法的上调通道** " + B + "--raise-baseline" + B +
           "（须 commit+path+delta+reason 四要素且 delta 与实增逐字节相等、path 确在注入面内、commit 可在该仓解析），"
           "并永久留账 " + B + "attributed_raises" + B + "；本轮用该通道接受 +447B（并行会话立 #23 所致，非本仓动作），"
           "夹具 " + B + "05-exec/r21e_ratchet_attrib_fixtures.py" + B + " 16/16（含变异 4/4 被拦）。"
           "**取值**：" + B + "python 05-exec/ratchet_gate.py" + B + "（期望 " + B + "[RATCHET:PASS]" + B +
           " 且打印留账 1 条）；" + B + "python 05-exec/r21e_gate_probe.py" + B + "。")
    a2 = "- [ ] **【r21e 机器型补口·控制符 + 证据可解析】**"
    assert s.count(a2) == 1, "07 锚点命中 %d" % s.count(a2)
    s = s.replace(a2, add + "\n" + a2, 1)
    wr(N07, s)
    b = rd(N07)
    ok = "r21e 证据可解析性与归因抬基线" in b and b.count(chr(8)) == 0
    print("[07] 条目落盘=%s | %dB" % (ok, len(b.encode("utf-8"))))
    return ok


def step_rpt():
    t = rd(RPT)
    if "## 14. r21e" in t:
        print("[报告] §14 已在位，跳过")
        return True
    add = """

## 14. r21e：把「已闭环」从一句承诺变成一条能跑的检查
本轮的判定不是「又写了几个工具」，而是三条方法论，全部由实测逼出来：

1. **判据必须能解析，不能只能匹配形状。** `RE_EVID` 校验了三年不到的正则（绝对路径 + `#版本行:Vx.y.z`）
   只证明锚点**长得像**证据。测量 `06-benchmark/evidence_resolvability_measure.json`：近 3 日 97 条已闭环声明
   里 **38.1% 解析不到**。所以判据分级必须是：路径不存在 / 回滚件与 git 对象全无 = **阻断**（4/97，这类不可事后合理化）；
   文件在但版本 token 被后续提交推走 = **只告警**（18/97，声明当时可为真 —— 追溯拦人就是把误伤率写进门禁）。
   形状层同时把 `V` 前缀改为可选：文件里写的是 `version: 10.70.0`，只收 `V10.70.0` 等于**奖励美化而非真实**。
2. **上调判据要有唯一通道，且必须留账。** 棘轮「只降不升」是对的，但实测它被**外部合法增长**挡下：
   +447B 来自并行会话往 `behavior_core.md` 立 #23（用户明令的铁律）。既不放宽判据也不永久卡死自己的做法 =
   开一条 `--raise-baseline`：commit + path + delta + reason 四要素齐备，delta 与实增**逐字节相等**，
   path 确在注入面成员内，commit 能在该文件所属仓解析；写成功后进 `attributed_raises` 账本，**条数与理由常驻可查**。
   拒绝「无的放矢的抬」（现状没长大也给抬）—— 否则账本会被当成装饰刷条数。
3. **自反适用：新判据先扫自己。** 控制符扫描器上线后第一个抓到的就是我自己：`lessons.part49.md` 里
   2 个退格符（我先前声称"已清零"，实为**重写脚本从未执行**）；随后又在受管根
   `A-project-handoff/references/version-history.md` 抓到 2 个 **NUL**，位置正好在
   `02-structure.md` / `03-tech-stack.md` 的文件名首位 —— 即"引用它的文本文字检索不到它自己"。
   它还暴露了自己定义的洞：只查 `<0x20` 会漏 DEL(0x7f)，而 DEL 恰好真的出现在我写的源码里。

**边界（防止借壳复活）**：本轮全部判据只约束**写法与落盘**，一律不得用于判定「本轮要不要干活」；
重复指令按 `core\\behavior_core.md` #23 一律整跑。这条边界写进了新代码的注释与本仓 AGENTS.md，
因为同一天里我已经见过一次「把幂等做成了跳过执行」。
"""
    wr(RPT, t.rstrip("\n") + add)
    b = rd(RPT)
    ok = "## 14. r21e" in b and b.count(chr(8)) == 0
    print("[报告] §14 落盘=%s | %dB" % (ok, len(b.encode("utf-8"))))
    return ok


def step_lessons():
    if os.path.exists(P50):
        print("[lessons] part50 已存在，跳过")
        return True
    sz = os.path.getsize(P49)
    entry = """# lessons.part50

> 2026-09-24 r21e 新建。换卷理由 = 旧卷 `lessons.part49.md` 现 **3,243B**（上限 4,096B），本批条目 **~1,150B**，追加即破硬上限 ⇒ 按 ≤4KB 规则换卷；part49 条目零改写零删除。

### [2026-09-24] 🔴 门禁只校验「证据长得像证据」，等于把自证交给运气
trigger: 97 条已闭环声明 38.1% 解析不到 | 写footer,门禁判据,锚点校验 | 记忆系统,门禁,python
- **问题：** `upgrade_footer_gate.py` 用正则要求 `绝对路径 + #版本行:Vx.y.z`，但**从不验证路径是否存在、token 是否在文件里**。实测近 3 日 97 条已闭环声明 38.1% 解析不到（含引用根本不存在的文件、backup ID 凭空捏造）
- **原因：** 形状校验成本极低、可解析性校验要读盘与查 git，历史上一直只做前者；同时正则强制 `V` 前缀，而真实文件写的是裸值 `version: 10.70.0` ⇒ 诚实引用反被判不合规，加个 V 就过（**判据奖励美化**）
- **解法：** ① 分三级：路径不存在 / backup ID 全无 = 阻断；文件在但 token 被后续提交推走 = 只告警（追溯拦人即误伤）；体系外路径 = 不判；② 前缀改可选，真伪交给可解析性；③ 交付前必须先量误伤面（`05-exec/evidence_resolvability_measure.py` 输出四类计数），按数据决定阻断级别，不按感觉
- **元：** 来源=自建skill优化 r21e | 版本=upgrade_footer_gate @055f9b5后 | 置信度=0.7（97 条样本实测） | 日期=2026-09-24 | 适用范围=记忆系统, 门禁, python, 多agent
"""
    if len(entry.encode("utf-8")) > CAP:
        print("[lessons 停手] 新卷本身超 4096B")
        return False
    wr(P50, entry)
    b = rd(P50)
    ok = os.path.getsize(P50) <= CAP and b.count("### [") == 1 and b.count(chr(8)) == 0
    print("[lessons] part50 新建=%s | %dB | 旧卷 %dB 未动" % (ok, os.path.getsize(P50), sz))
    return ok


def step_log():
    t = rd(LOG)
    if KEY in t:
        print("[GM] r21e 块已在位，跳过")
        return True
    blk = """
## 23:3x 自建skill优化 r21e（第六次标注驱动·把「已闭环」做成能跑的检查）
- 复测自己上一条：两行都标 `状态=已闭环`，但落点是 lessons 与脚本注释 = **自觉型**。按 A-get-memory Step 2.7「下一个会话不做任何事还生效吗」判为未闭环 ⇒ 本轮补机器型。
- 机器型四件：① `control_char_scan.py`（C0 ∪ {0x7fDEL} - 制表换行回车；跳二进制但登记 skipped；空面 exit 2）挂进本仓必跑链第 5 条，夹具 **22/22**；② `upgrade_footer_gate.py` 新增证据可解析性（FAKE 阻断 / STALE 告警 / SKIP 不判）+ 形状层 V 前缀可选，夹具 **5/5**（红阶段实测伪造 backup 锚打补丁前 rc=0 放行）；③ `ratchet_gate.py` 新增 `--raise-baseline` 唯一合法上调通道（四要素 + delta 逐字节相等 + path 在面内 + commit 可解析）且永久留账，夹具 **16/16**（含变异 4/4）；④ 边界测量 `evidence_resolvability_measure.py`：近 3 日 97 条声明，可解析 52 / 形状合规但解析不到 37 / 形状不合规 8 —— **先量误伤面再决定阻断级别**，不凭感觉收严。
- 实测收益（全部由新判据自己抓到，非人工巡检）：本仓 `lessons.part49.md` 残留 2 个退格符（我先前称已清零，实为**重写脚本从未执行**）；受管根 `A-project-handoff/references/version-history.md` 第 38 行 2 个 NUL 把 `02-structure.md`/`03-tech-stack.md` 写成死引用（已 rule_editor 修复 + 镜像单文件同源 37,333B）；判据自身漏 DEL，而 DEL 真出现在我源码里 ⇒ 定义扩展。
- 棘轮被外部合法增长挡下：`inject_union_bytes` +447B 全部来自并行会话往 `behavior_core.md` 立 #23（`055f9b5`）。**不放宽判据、不 revert 他人动作**，改走留账通道：`[RATCHET:RAISED-ATTRIBUTED] 86,346→86,793，累计留账 1 条`，复跑 `[RATCHET:PASS]`。
- 门禁现状：`gates` = `mirror=fail noise=pass evolution=pass stub=pass`（mirror 唯一红项 = `A-get-memory\\SKILL.md`，本仓未触碰该文件，R269 只登记）；焚诀 verify = 32 PASS / 1 FAIL（其 C29 index 面，外部）；受管根提交 2 笔：`upgrade_footer_gate.py`（新增可解析性）+ `version-history.md`（NUL 修复）。

【数据流假设】
来源: 三个夹具的实跑输出（22/22、5/5、16/16，各含红阶段留痕与变异对照）+ `evidence_resolvability_measure.py` 对近 3 日 GM 日志的 97 条解析 + `git -C D:\\global_memory cat-file -t 055f9b5` = commit + `os.path.getsize` 逐文件实测（26,593 / 37,333 / 3,243B）
流向: 测量 → 决定分级（只有不可事后合理化的形态才阻断）→ 落判据（受管根经 rule_editor，本仓直写）→ 挂执行路径（本仓必跑链 + 每轮 footer 门禁）→ 回写 07 / 报告 §14 / lessons.part50 / 本日志 → 按文件白名单 commit + push → savepoint
结构: UTF-8 无 BOM；lessons 新卷 part50 卷首写换卷理由 + 旧卷字节数 + 本批字节数；棘轮基线新增 `attributed_raises` 数组（commit/path/delta/reason/at/from_value/to_value）；全部产物二进制复扫 0x08=0
异常: 扫描器二进制文件不判脏但登记 skipped（不静默丢弃）；空输入面 exit 2；棘轮无增长时拒绝归因上调（防刷账）；受管根 `A-get-memory/SKILL.md` 与 `A-project-better` 多文件为他人在途，本仓未 add 未 -Fix；本轮三次内联构造文本出错（引号/转义），全部改为**脚本文件 + chr() 构造**后归零

<!-- footer:begin session=qd-zijian-r21e-0924 ts=2026-09-24T23:35:00+08:00 -->
[skill清单] 本轮调用=2 个 (A-get-memory, A-project-handoff)
[升级建议] skill=A-get-memory | 五问=缺失步骤 | 改法=已闭环证据须可解析且先量误伤面 | 对照=已取(证据=97条实测38.1%解析不到；FAKE阻断仅4/97、STALE告警18/97两侧各实测；打补丁前伪造锚rc=0放行、补丁后=1) | 状态=已闭环(证据=D:\\global_skills\\A-memory-start\\references\\upgrade_footer_gate.py#backup:A-memory-start.references.upgrade_footer_gate.py.20260924_231413_532936.bak)
[升级建议] skill=A-project-handoff | 五问=错误信息 | 改法=受管根文件名首位NUL清零并镜像单文件同源 | 对照=已取(证据=扫描器实测该文件 0x00 由 2 处降为 0 且 02-structure.md/03-tech-stack.md 各可 grep；镜像与源 37333B 同哈希) | 状态=已闭环(证据=D:\\global_skills\\A-project-handoff\\references\\version-history.md#backup:5148d79)
<!-- footer:end -->
"""
    wr(LOG, t.rstrip("\n") + "\n" + blk)
    b = rd(LOG)
    need = ["【数据流假设】", "来源:", "流向:", "结构:", "异常:", "[skill清单]", "[升级建议]", KEY]
    miss = [k for k in need if k not in b]
    print("[GM] 读回缺失=%s | %dB" % (miss or "-", os.path.getsize(LOG)))
    return not miss


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    rs = [step07(), step_rpt(), step_lessons(), step_log()]
    print("-" * 60)
    print("[LAND2] 四处全过=%s" % all(rs))
    return 0 if all(rs) else 1


if __name__ == "__main__":
    raise SystemExit(main())
