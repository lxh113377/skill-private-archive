# -*- coding: utf-8 -*-
"""r29_rubric_calibre_fixtures.py - 层a 隔离桩：M2 双口径判据（frontmatter 兼容）自证。

R238 要求：函数层通过 != 接线层通过。本桩只证函数层；接线层由
`rubric_ab_compare.py` 真跑 + 'body' 口径与 r28 归档 JSON 逐列对账承担。
含反例：修口径不得把真实缺口洗成"已具备"。
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from skill_structure_rubric_scan import frontmatter_fields, rubric_hits  # noqa: E402

CASES = []


def case(name, text, body=None, both=None, fm=None, same=False):
    """fm: 期望 frontmatter_fields() 的精确返回；same: 期望两口径结果全等。"""
    CASES.append((name, text, body or {}, both or {}, fm, same))


case("fm_desc_only_when_to_use",
     '---\nname: x\ndescription: Use when 用户要改技能\n---\n# X\n随便写点东西\n',
     body={"when_to_use": False}, both={"when_to_use": True})

case("fm_locating_word_hits_overview",
     '---\nname: x\ndescription: 定位：把散落的技能收敛成一条流水线\n---\n正文\n',
     body={"overview": False}, both={"overview": True})

case("body_heading_still_hits",
     '---\nname: x\ndescription: 干活\n---\n## 验证\n- 必须贴实测输出\n',
     body={"verification": True}, both={"verification": True})

case("block_scalar_description",
     '---\nname: x\ndescription: |\n  这是多行说明\n  触发条件：用户说"跑一下"\n---\n正文无标题\n',
     body={"when_to_use": False}, both={"when_to_use": True})

case("yaml_list_triggers",
     '---\nname: x\ntriggers:\n  - 合并技能\n  - 上架\n---\n正文\n',
     fm={"name": "x", "triggers": "- 合并技能\n- 上架"})

case("no_frontmatter_body_equals_both",
     '# 只有正文\n## 常见托词\n- "太简单不用测"\n',
     body={"rationalizations": True}, both={"rationalizations": True},
     fm={}, same=True)

# 未闭合围栏：不得崩，且两口径必须一致（此时无 fm 可兜底）
case("unterminated_fence_degrades_to_body",
     '---\nname: x\ndescription: Use when 需要\n# 正文\n',
     fm={}, same=True)

# 反例：双口径不得把真实缺口洗成已具备
case("counterexample_real_gap_stays_false",
     '---\nname: x\ndescription: 一个数据处理技能\n---\n## 流程\n1. 读\n2. 写\n',
     body={"rationalizations": False, "verification": False, "red_flags": False},
     both={"rationalizations": False, "verification": False, "red_flags": False})

# 反例：fm 里没有触发/定位措辞时，不许凭空造出 overview/when_to_use 命中
case("counterexample_no_fm_no_false_positive",
     '---\nname: x\ndescription: 只做一件事\n---\n## 流程\n1. 执行\n',
     body={"overview": False, "when_to_use": False},
     both={"overview": False, "when_to_use": False})


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ok = fail = 0
    for name, text, eb, eo, fm, same in CASES:
        b = rubric_hits(text, calibre="body")
        o = rubric_hits(text, calibre="both")
        bad = []
        for k, v in eb.items():
            if b.get(k) != v:
                bad.append("body[%s]=%s!=%s" % (k, b.get(k), v))
        for k, v in eo.items():
            if o.get(k) != v:
                bad.append("both[%s]=%s!=%s" % (k, o.get(k), v))
        if fm is not None and frontmatter_fields(text) != fm:
            bad.append("fm=%r" % (frontmatter_fields(text),))
        if same and b != o:
            bad.append("calibres differ: %r vs %r" % (b, o))
        for k in b:
            if b[k] and not o[k]:
                bad.append("monotonic broken on %s" % k)
        if bad:
            fail += 1
            print("FAIL %-38s %s" % (name, "; ".join(bad)))
        else:
            ok += 1
            print("PASS %-38s body=%d/6 both=%d/6" % (
                name, sum(b.values()), sum(o.values())))
    print("\n层a: %d/%d 通过" % (ok, ok + fail))
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
