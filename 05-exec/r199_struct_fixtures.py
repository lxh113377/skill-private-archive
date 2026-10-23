# -*- coding: utf-8 -*-
# r199_struct_fixtures.py - 结构复算件的夹具（W-47 双向 + 变异腿）。
#
# 为什么必须有夹具：§41 的教训是「md_claim 每轮跑，但没有一门管标题被复制」，18 份副本
# 全绿过了 10 轮。新挂的门若没有夹具，就成了下一个「写了但没人验其牙齿」的判据 ——
# 正是 r32「写下靶子却六年没挂门」的老毛病换位置复发。
#
# 本夹具还锁住：代码语境排除是**精化不是放宽**。t8 专造「同一行既有行内代码举例、又有
# 正文粘连」的混合形态，要求计数为 1 —— 若排除逻辑按整行判断，就会把真损坏一起吞掉。
import importlib.util as _u
import os
import sys

NL = chr(10)
DOT = chr(12290)
BT = chr(96)
HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, 'r199_struct_recount.py')
RESULTS = []


def ck(name, cond, detail=''):
    RESULTS.append((bool(cond), name, detail))
    print('%s %-58s %s' % ('PASS' if cond else 'FAIL', name, detail if not cond else ''))


def load():
    spec = _u.spec_from_file_location('sr', TARGET)
    m = _u.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def build(parts):
    return NL.join(parts)


def main():
    if not os.path.isfile(TARGET):
        ck('t0 复算件存在', False, TARGET)
        print('[GATE:fixture-fail]')
        return 1
    m = load()
    ANCHOR = m.ANCHOR
    F3 = BT * 3

    base = build(['# 标题', '## 1. 一', '正文甲', ANCHOR, '- 件A', ''])
    r0 = m.recount(base)
    ck('t1 干净样本：锚=1、无重复、无粘连',
       r0['anchors'] == 1 and not r0['dup_heads'] and r0['glued'] == 0, r0)

    dup = base + NL + ANCHOR + NL + '## 34. 事故' + NL + base.replace('## 1. 一', '## 34. 事故')
    r1 = m.recount(dup)
    ck('t2 复制事故被检出（锚数与各标题重复计数与构造一致）',
       r1['anchors'] == 3 and r1['dup_heads'].get('34') == 2
       and r1['dup_heads'].get('9') == 3 and '1' not in r1['dup_heads'],
       (r1['anchors'], r1['dup_heads']))

    glued = build(['# x', '## 1. 一', DOT + '## 37. 被粘住的标题', '正文', ANCHOR, ''])
    ck('t3 正文粘连（句号后无空格）被计数', m.recount(glued)['glued'] == 1,
       m.recount(glued)['glued'])

    quoted = build(['# x', '> 引用：见' + DOT + '## 37. 引用行里的粘连', '正文', ANCHOR, ''])
    ck('t4 引用行内的 句号+## 也必须计数（真实事故 L1614 即此形态）',
       m.recount(quoted)['glued'] == 1, m.recount(quoted)['glued'])

    legit = build(['# x', '## 3. 三', '正文', '## 3b. 三之b', '正文', ANCHOR, ''])
    r4 = m.recount(legit)
    ck('t5 ## 3. 与 ## 3b. 属白名单（不误判复制）',
       r4['dup_heads'].get('3') == 2
       and all(k in m.LEGIT_DUP for k in r4['dup_heads']), r4['dup_heads'])

    inline = build(['# x', '## 1. 一',
                    '  例：' + BT + DOT + '## 37. 举例' + BT + ' 说明',
                    '正文', ANCHOR, ''])
    ck('t6 行内代码里的举例不计为粘连（避免误伤 §41.5 那种写法）',
       m.recount(inline)['glued'] == 0, m.recount(inline)['glued'])

    fence = build(['# x', '## 1. 一', F3, DOT + '## 37. 代码块内', F3, '正文', ANCHOR, ''])
    ck('t7 fenced 代码块内不计为粘连', m.recount(fence)['glued'] == 0,
       m.recount(fence)['glued'])

    mixed = build(['# x', '## 1. 一',
                   '  例：' + BT + DOT + '## 37. 举例' + BT + '，但这里' + DOT + '## 38. 真粘连',
                   '正文', ANCHOR, ''])
    ck('t8 混合行只排除 code span 内那处，正文粘连照抓（精化非放宽）',
       m.recount(mixed)['glued'] == 1, m.recount(mixed)['glued'])

    r9 = m.recount(inline, honor_code=False)
    ck('t9 变异：关掉代码排除 ⇒ t6 场景立即误报（证明该排除承重）',
       r9['glued'] == 1, r9['glued'])

    _old = m.DOT
    try:
        m.DOT = _old + ' '
        ck('t10 变异：检测串多一个空格即漏检 t3 场景',
           m.recount(glued)['glued'] == 0, m.recount(glued)['glued'])
    finally:
        m.DOT = _old

    real = m.recount(open(m.P, encoding='utf-8').read())
    bad = m.findings(real)
    ck('t11 当前真实报告通过复算（锚=1、无粘连、无非法重复）', not bad, bad)

    fails = [x for x in RESULTS if not x[0]]
    print('')
    print('夹具合计: %d 项，通过 %d，失败 %d' % (len(RESULTS), len(RESULTS) - len(fails), len(fails)))
    print('[GATE:fixture-fail]' if fails else '[GATE:fixture-pass]')
    return 1 if fails else 0


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
    sys.exit(main())