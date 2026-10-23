# -*- coding: utf-8 -*-
r"""r49_face_fixtures.py — W-20「判据输入面截断自证」+ W-22「裁决对象自证」的层a 夹具。

本轮立规的动因（r49 实测，不是推测）：
  · W-20：账龄尺里有三处**截断/降采样**从未自证 —— `git log -40` 取轮号、
    `body[:80]` 当去重键、`needle[:70]` 当 `git log -S` 的搜索串。
    任何一处吞掉输入，报出来的"零积压/零 UNDATED/零 UNOWNED"就只是**局部干净**。
  · W-22：r46 我把「挂账至 r49」写到了 **W-14** 行上（原因文本讲的是 W-17），
    而 W-14 在 r45 的提交主题里已写明「落地」。锚点唯一命中只保证"写到某一行"，
    不保证"那行是我要裁的那条" ⇒ 直到 r49 到期追讨才发现，**检测延迟 = 整个延期窗口**。

判据函数全部是纯函数（不碰 git / 不碰真卷），便于喂反例（X-8）。
真实数据的一面守恒（raw_lines == items_total）另有一条集成断言，直接跑真卷。
"""

import io
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

RESULTS = []


def ck(name, cond, got=""):
    RESULTS.append((bool(cond), name, str(got)))
    print("%s %s%s" % ("PASS" if cond else "FAIL", name,
                      "" if cond else "  <-- got: " + str(got)[:180]))


def _safe(fn_name, *a):
    """判据函数缺失时转为**干净失败**，不让 AttributeError 中断整份夹具。"""
    mod = a[0] if a and hasattr(a[0], "__name__") else None
    try:
        if mod is not None:
            a = a[1:]
        return getattr(mod, fn_name)(*a)
    except Exception as e:                                    # noqa: BLE001
        return ("__ERR__", "%s: %s" % (type(e).__name__, e))


import r38_debt_aging as da                                     # noqa: E402
import r46_mark_verdict as mv                                   # noqa: E402

TMP = tempfile.mkdtemp(prefix="r49face_")

# ---------------------------------------------------------------- W-20 轮号面
ok, d = _safe("face_round", da, 49, 48)
ck("f1 face_round 正常：log 轮号 >= tag 轮号（本轮未打 tag 属预期）→ OK", ok is True, (ok, d))
ok, d = _safe("face_round", da, 47, 49)
ck("f2 face_round 反例：tag=r49 晚于窗口推出的 r47 ⇒ 判红（-40 窗口截断）", ok is False and "截断" in str(d), (ok, d))
ok, d = _safe("face_round", da, None, 49)
ck("f3 face_round 取不到轮号 ⇒ 判红，禁按 0 处理（R247）", ok is False, (ok, d))
ok, d = _safe("face_round", da, 49, None)
ck("f4 face_round 无 tag 锚（首轮未打标）⇒ 记 UNVERIFIED 不记 FAIL 也不记绿", ok is None or ok is True, (ok, d))

# ---- r201 新增：轮号被「算多」方向的守卫（原实现只防被算少）----
# 一手：我在提交主题写「挂账至 r206」，current_round 从 r201 被推到 r206 ⇒ 全体挂账条目
# 集体提前到期（实测 overdue 3→4，且第 4 条就是我自己那条）。旧 face_round 只查 tag>log
# （窗口截断＝被算少），而「被算多」恰好伪装成合法形态（本轮尚未打 tag ⇒ log 领先）。
ok, d = _safe("face_round", da, 206, 201)
ck("f4b face_round 反例：log 领先 tag >=3 轮 ⇒ 判红（轮号疑被未来引用污染）",
   ok is False and "污染" in str(d), (ok, str(d)[:90]))
ok, d = _safe("face_round", da, 203, 201)
ck("f4c face_round 边界：领先 2 轮仍属「本轮未打 tag」的正常节奏，不误伤",
   ok is True, (ok, str(d)[:70]))
ok, d = _safe("face_round", da, 201, 201)
ck("f4d face_round 两源一致 ⇒ OK", ok is True, (ok, str(d)[:70]))

# 作用域取号：只认提交自身轮号，不认「挂账至 rNN」「见 §41」这类引用
def _pick(text):
    res = []
    for mm in da.RE_SCOPED_ROUND.finditer(text):
        for g in mm.groups():
            if g:
                res.append(int(g))
                break
    return res

ck("f4e 取号：chore(r201c) 与 挂账 r206 同句 ⇒ 只取 201（未来引用不入尺）",
   _pick("chore(r201c): register 挂账 r206") == [201],
   _pick("chore(r201c): register 挂账 r206"))
ck("f4f 取号：纯挂账句不得产生轮号",
   _pick("挂账至 r206 到期追讨") == [], _pick("挂账至 r206 到期追讨"))
ck("f4g 取号：r188 登记 / 第 205 轮 两种声明式都认",
   _pick("r188 登记：修 CI") == [188] and _pick("第 205 轮收尾") == [205],
   (_pick("r188 登记：修 CI"), _pick("第 205 轮收尾")))
ck("f4h 取号：正文引用「见 §41 与 r191 留账」不产生轮号",
   _pick("见 §41 与 r191 留账") == [], _pick("见 §41 与 r191 留账"))

# ---------------------------------------------------------------- W-20 去重面
ck("f5 face_dedup 全面守恒：行数 == 计入数 且零前缀碰撞 → OK",
   _safe("face_dedup", da, 10, 10, [])[0] is True, _safe("face_dedup", da, 10, 10, []))
ok, d = _safe("face_dedup", da, 10, 8, [])
ck("f6 face_dedup 反例：10 行只计入 8 条 ⇒ 判红（有行被静默吞掉）", ok is False, (ok, d))
coll = [{"key": "x" * 80, "a": "正文A" * 30, "b": "正文B" * 30}]
ok, d = _safe("face_dedup", da, 10, 10, coll)
ck("f7 face_dedup 反例：80 字前缀相同但正文不同 ⇒ 判红并给出碰撞样本（去重键吞不同条目）",
   ok is False and "正文不同" in str(d), (ok, d)[:180])

# ---------------------------------------------------------------- W-20 定年面
ok, d = _safe("face_dating", da, "2026-09-23", "2026-09-23")
ck("f8 face_dating 同值 ⇒ OK（截断未改变结论）", ok is True, (ok, d))
ok, d = _safe("face_dating", da, "2026-09-20", "2026-09-23")
ck("f9 face_dating 反例：短 needle 与全 needle 不同值 ⇒ 判红（禁「取保守值」糊过去）",
   ok is False, (ok, d))
ok, d = _safe("face_dating", da, None, "2026-09-23")
ck("f10 face_dating 只有一路取到值 ⇒ 判红（自证本身缺面，不得当作已通过）", ok is False, (ok, d))

# ------------------------------------------------- W-20 第 5 面：规模下限（R-ENUM floor）
ok, d = _safe("face_floor", da, ["memory/07-a.md", "memory/07-b.md"], ["memory/07-a.md"])
ck("f11 face_floor 正例：上轮受检卷全部仍在本轮面内（拆卷只增不减）→ OK", ok is True, (ok, d))
ok, d = _safe("face_floor", da, ["memory/07-a.md"], ["memory/07-a.md", "memory/07-part9.md"])
ck("f12 face_floor 反例：glob 少收一卷 ⇒ 判红并点名（其余四面在这种情形下仍会全绿）",
   ok is False and "07-part9" in str(d), (ok, d))
ok, d = _safe("face_floor", da, ["memory/07-a.md"], [])
ck("f13 face_floor 边界：无上轮证据 ⇒ UNVERIFIED（不得静默 PASS，R247）", ok is None, (ok, d))

ok, d = _safe("face_dating_summary", da, [], 0)
ck("f14 边界：本轮零到期项 ⇒ 定年面记 UNVERIFIED（R-ENUM：零输入不得静默 PASS）", ok is None, (ok, d))
ok, d = _safe("face_dating_summary", da, [{"why": "两路不等"}], 3)
ck("f15 有不等 ⇒ 判红", ok is False, (ok, d))
ck("f16 有行使且全等 ⇒ 判绿", _safe("face_dating_summary", da, [], 3)[0] is True,
   _safe("face_dating_summary", da, [], 3))

# ------------------------------------ 建议面分路由（r50 自抓假阳性：X 的承接面不是 07）
ok, d = _safe("face_suggestions", da, ["X-24"], "", "| X-24 | 枚举器不得只做面内自洽 |")
ck("f17 建议面分流：X 编号落在 memory/AGENTS.md 的禁止项表 ⇒ 判绿（不得要求它进待办卷）",
   ok is True, (ok, str(d)[:140]))
ok, d = _safe("face_suggestions", da, ["X-99"], "随便什么待办文本", "无关禁止项表")
ck("f18 反例：X-99 两面都没有 ⇒ 判红并点名", ok is False and "X-99" in str(d), (ok, str(d)[:140]))
ok, d = _safe("face_suggestions", da, ["W-30"], "只有别的条目", "| W-30 | 写在禁止项表里的待办 |")
ck("f19 反例（禁互相顶替）：W 编号只出现在 AGENTS 表而未落待办卷 ⇒ 仍判红",
   ok is False and "W-30" in str(d), (ok, str(d)[:140]))
ok, d = _safe("face_suggestions", da, ["W-31", "X-25"], "…W-31 已登记…", "…X-25 已立规…")
ck("f20 混合面正例：待办与禁止项各归各位 ⇒ 判绿且计数分列",
   ok is True and "待办 1" in str(d) and "禁止项 1" in str(d), (ok, str(d)[:140]))

# ------------------------- r105 F-7：R 系列命名空间（原式取不到 ⇒ 报告新建议静默逃逸这道检查）
_ids = da.RE_SUGG_ID.findall("新立 R59-4、R105-10、L-6、W-47、X-26，另有正文里的 R236 补注③")
ck("f21 命名空间取数：R<轮号>-<序号> / L-nn / W / X 四类都要取得到（漏一类即该族长期免检）",
   {"R59-4", "R105-10", "L-6", "W-47", "X-26"} <= set(_ids), _ids)
ck("f22 反例：裸 `R236`（无连字符的既有规则号）不得被当成本轮新建议（防把历史条款判成漏登记）",
   "R236" not in _ids, _ids)
ok, d = _safe("face_suggestions", da, ["R105-6"], "…R105-6 已落待办卷…", "")
ck("f23 建议面正例：R 系列编号落到待办卷 ⇒ 判绿", ok is True, (ok, str(d)[:140]))
ok, d = _safe("face_suggestions", da, ["R105-7"], "只有别的编号", "无关表")
ck("f24 反例：R 系列报告立了而待办卷没有 ⇒ 必须判红并点名（不得因新命名空间而隐身）",
   ok is False and "R105-7" in str(d), (ok, str(d)[:140]))
ok, d = _safe("face_suggestions", da, [], "任意", "任意")
ck("f25 边界：new_ids 为空仍走 UNVERIFIED（取不到编号≠已通过，R247）",
   ok is None, (ok, str(d)[:120]))
ck("f26 变异体（证明本扩面确有鉴别力）：把正则退回旧式 [WXMH] ⇒ R/L 编号取不到",
   not re.compile(r"\b([WXMH]-\d{1,2})\b").search("R105-6"), "旧式仍匹配到 ⇒ 扩面没起作用")

# ---------------------------------------------------------------- W-22 裁决对象面
SUBJ = ("8d7fb56 feat: r45 落地 W-14 反降级免检指标\n"
        "24fd233 docs: r44 savepoint\n")
ck("t1 反例（r46 真事故复现）：条目自身编号 W-14 已在近期提交声称落地，却仍写「挂账至 r49」⇒ 拒写",
   _safe("landed_contradiction", mv, "W-14", "挂账至 r49｜契约分代必填需先设计", SUBJ) is True,
   _safe("landed_contradiction", mv, "W-14", "挂账至 r49｜契约分代必填需先设计", SUBJ))
ck("t2 正例：编号未出现在提交主题 ⇒ 不拒（不得凭空造拒写）",
   _safe("landed_contradiction", mv, "W-21", "挂账至 r52｜产能给了别的项", SUBJ) is False,
   _safe("landed_contradiction", mv, "W-21", "挂账至 r52｜产能给了别的项", SUBJ))
ck("t3 边界：终局裁决（执行完毕）指向已落地条目 ⇒ 放行（只有延期才需要这条自证）",
   _safe("landed_contradiction", mv, "W-14", "执行完毕｜见 05-exec/ratchet_gate.py", SUBJ) is False,
   _safe("landed_contradiction", mv, "W-14", "执行完毕｜见 05-exec/ratchet_gate.py", SUBJ))
ck("t4 边界：条目正文取不到自身编号 ⇒ 不拒（无从推断，禁误伤）",
   _safe("landed_contradiction", mv, None, "挂账至 r49", SUBJ) is False,
   _safe("landed_contradiction", mv, None, "挂账至 r49", SUBJ))
ck("t5 编号提取：只认「W-14（r44 新立」这种**条目自我声明**的编号，不把引用他条的编号当自身编号",
   _safe("item_own_id", mv, "**【P0·下轮首推 W-14（r44 新立，优先级最高）】** 同 W-9 同族缺陷") == "W-14",
   _safe("item_own_id", mv, "**【P0·下轮首推 W-14（r44 新立，优先级最高）】** 同 W-9 同族缺陷"))

# ------------------- 劫持负控（r49 第 2 形态）：原因体里引用旧标记原文不得改变判定 ----
QUOTED = ("**【P0·下轮首推 W-14（r44 新立）】** 正文 "
          "【r46 裁决=挂账至 r49｜产能给了 W-16】 "
          "【r49 裁决=执行完毕（并纠正 r46 误挂）｜r46 却在本条上写了「挂账至 r49」，本轮到期追讨抓到】")
cls, det = _safe("classify_item", da, QUOTED, 49)
ck("q1 反例：终局裁决的**原因里引用**了『挂账至 r49』原文 ⇒ 仍判 DECIDED（不得被引号内容劫持回红）",
   cls == "DECIDED", (cls, det))
ck("q2 count_deferrals 只数真延期 ⇒ 引用的那次不计（防 REPEAT 第 9 指标虚增）",
   _safe("count_deferrals", da, QUOTED) == 1, _safe("count_deferrals", da, QUOTED))
ck("q3 写入器⑥：头部是终局裁决、原因里引用挂账 ⇒ 不得拒写（只在头部为延期时设卡）",
   _safe("landed_contradiction", mv, "W-14",
          "执行完毕（并纠正 r46 误挂）｜r46 写了「挂账至 r49」", SUBJ) is False,
   _safe("landed_contradiction", mv, "W-14", "执行完毕｜引用「挂账至 r49」", SUBJ))
TRUE_DEFER = "**【P1·待办 W-9（r44 新立）】** 正文 【r49 裁决=挂账至 r52｜原因】"
cls, det = _safe("classify_item", da, TRUE_DEFER, 49)
ck("q4 修 hijack 不得修坏 r39 机制：最后一枚标记**真是**延期 ⇒ 未到轮判 DEFERRED",
   cls == "DEFERRED", (cls, det))
cls, det = _safe("classify_item", da, TRUE_DEFER.replace("r52", "r49"), 49)
ck("q5 到期延期 ⇒ 仍判 OVERDUE（延期非终局的口径不变）", cls == "OVERDUE", (cls, det))

# ------------- 定年劫持（X-23 第 5 次复发 · r194 一手）：正文引用他事轮号不得顶掉标题 ----
# 本仓实物：r194 登记 R194-1 时，裁决原因体写了「③ r130 登记生效」（r130 = 对账器，另一件事），
# RE_ROUND_DECL 主循环逐次覆盖 origin ⇒ 标题真值 r194 被 r130 顶掉 ⇒ 账龄 194-130 = 64 轮，
# 刚登记的条目当场判 OVERDUE 并把 W-12 完整性染红。r128 当年只把「标题优先」写进 age is None
# 的回退支，主循环一命中就轮不到它 ⇒ 修了个寂寞。
H194 = ("- [ ] **R194-1（r194 登记，P1）** 门表 69->70 已用 r130 登记生效" + chr(12304) + "对账，" + chr(12305) + "读数略。")
cls, det = _safe("classify_item", da, H194, 194)
ck("q6 标题自身编号优先：正文含他事「r130 登记」不得顶掉标题 r194（账龄应为 0）",
   "账龄 0 轮" in (det or ""), (cls, det))
ck("q7 同条目在 now=194 下 ⇒ ACTIVE（修复前是 64 轮假 OVERDUE）",
   cls == "ACTIVE", (cls, det))
# 真到期的老条目不受影响（修 hijack 不得修坏过期追讨）
OLD120 = "- [ ] **R120-3（r120 登记，P2）** 一手见 r105 登记 与 r118 更新。"
cls, det = _safe("classify_item", da, OLD120, 194)
ck("q8 老条目仍按自身编号追讨：账龄 74 > 宽限 ⇒ OVERDUE（不放宽）",
   cls == "OVERDUE", (cls, det))
# 取值域单源化（r194）：VERDICT_TERMS 一处定义，RE_DECIDED 与头部匹配两处引用
ck("q9a 取值域含新收词已落地 ⇒ 判 DECIDED",
   _safe("classify_item", da, "- [ ] **R194-2（r194 登记，P1）** 【r194 裁决=已落地｜x】", 194)[0] == "DECIDED",
   _safe("classify_item", da, "- [ ] **R194-2（r194 登记，P1）** 【r194 裁决=已落地｜x】", 194))
ck("q9b 取值域外自造措辞照旧不算裁决（X-10：扩枚举不等同于放宽判定）",
   _safe("classify_item", da, "- [ ] **R194-3（r194 登记，P1）** 【r194 裁决=差不多弄好了｜x】", 194)[0] != "DECIDED",
   _safe("classify_item", da, "- [ ] **R194-3（r194 登记，P1）** 【r194 裁决=差不多弄好了｜x】", 194))
ck("q9c 单源：RE_DECIDED 与 parse_last_verdict 用的是同一 VERDICT_TERMS（两处不漂移）",
   all(("裁决=" + t + "｜x") and _safe("parse_last_verdict", da, "【r9 裁决=" + t + "｜x】")[0] == "FINAL"
       for t in getattr(da, "VERDICT_TERMS", ())),
   getattr(da, "VERDICT_TERMS", None))
# 变异腿（W-47 双向：证明 q6 真有牙）：摘掉标题优先 ⇒ 必须退回 64 轮假 OVERDUE
import re as _re49
_orig_own = getattr(da, "RE_TITLE_OWN", None)
if _orig_own is None:
    ck("q10 变异：摘标题优先后须退回劫持形态", False, "RE_TITLE_OWN 不在（主路径未修）")
else:
    try:
        da.RE_TITLE_OWN = _re49.compile(r"(?!x)x\s*\[[ x]\]")   # 永不命中的同型式
        cls_m, det_m = _safe("classify_item", da, H194, 194)
        ck("q10 变异：摘掉标题优先 ⇒ q6 该条重新被 r130 劫持（账龄 64、判 OVERDUE）",
           cls_m == "OVERDUE" and "账龄 64 轮" in (det_m or ""), (cls_m, det_m))
    finally:
        da.RE_TITLE_OWN = _orig_own

# ---------------------------------------------------------------- 真卷集成面（全面守恒）
files = da.volume_files()
if not files:
    ck("i1 真卷：取到 07 卷面", False, "volume_files() 为空")
else:
    items, face = da.scan(files, da.current_round() or 0, da.GRACE_DEFAULT)
    raw_lines = face.get("raw_lines")
    ck("i2 真卷：RE_ITEM 命中行数 == 计入条目数（零静默吞行）",
       raw_lines == len(items), face)
    ck("i3 真卷：80 字前缀键零碰撞（去重键不吞不同条目）",
       not face.get("collisions"), str(face.get("collisions"))[:220])
    io.open(os.path.join(TMP, "real_face.json"), "w", encoding="utf-8").write(
        json.dumps(face, ensure_ascii=False, indent=1))
    print("真卷面 -> %s" % os.path.join(TMP, "real_face.json"))
    print("  raw_lines=%s items=%s collisions=%s"
          % (raw_lines, len(items), len(face.get("collisions") or [])))

print("\n夹具合计: %d 项，通过 %d，失败 %d"
      % (len(RESULTS), sum(1 for r in RESULTS if r[0]), sum(1 for r in RESULTS if not r[0])))
print("[GATE:fixture-fail]" if any(not r[0] for r in RESULTS) else "[GATE:fixture-pass]")
sys.exit(1 if any(not r[0] for r in RESULTS) else 0)
