# -*- coding: utf-8 -*-
"""r215_fixtures.py - 名册牙 r10（两面具名不许互斥）的夹具（r252 新建）。

存在理由（r252 一手）：r251 我给名册加了牙 r10（第 65 门判 GAP_CRED ∧ 本册读面 MEASURED ⇒ 红）。
  但它是**空转的假绿**：牙在 main() 里求值，却去够 build() 的局部变量 src ⇒ NameError 被一个宽
  except 吞掉 ⇒ 集合恒为空 ⇒ 永远 PASS。我上轮用「改盘上件再跑」验证时也没咬住，
  当时把原因写成「并发竞态」—— 其实主因就是这个吞异常的 except。

  本夹具用**进程内构造输入**验证（r251 教训：对由门逐轮重写的共享产物做注入式变异不可靠）：
    t1  GAP_CRED + MEASURED            ⇒ 必须检出互斥
    t2  GAP_CRED + 读面 None           ⇒ 不算互斥（没那个读数面）
    t3  READY     + MEASURED           ⇒ 不算互斥（本来就一致）
    t4  变异对照：把判据的比较反过来 ⇒ t1 必须不再检出（证明夹具对它要测的判据有牙）
    t5  回归护栏：build() 必须把第 65 门行随 doc 交出（ft_rows/ft_src 在位）⇒ 防 r252 那个假绿复发

判据：全过 ⇒ [GATE:rosterfix-pass] rc=0；任一不过 ⇒ [GATE:rosterfix-fail] rc=1。
"""
import ast
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import r215_free_tool_roster as R

OK = []
BAD = []


def ck(name, cond, detail=''):
    (OK if cond else BAD).append(name)
    print('  %-56s %s %s' % (name, 'PASS' if cond else 'FAIL', str(detail)[:90]))


def main():
    src_path = os.path.join(HERE, 'r215_free_tool_roster.py')
    if not os.path.isfile(src_path):
        print('[GATE:rosterfix-fail] 被测件不存在');
        return 1
    items_gap_measured = [{'tool': 'X', 'read_state': 'MEASURED'}]
    rows_gap = [{'tool': 'X', 'state': 'GAP_CRED'}]
    rows_ready = [{'tool': 'X', 'state': 'READY'}]
    items_none = [{'tool': 'X', 'read_state': None}]

    r1 = R.faces_contradiction(items_gap_measured, rows_gap)
    ck('t1 GAP_CRED + MEASURED ⇒ 必须检出互斥', len(r1) == 1 and 'X' in r1[0], r1)
    r2 = R.faces_contradiction(items_none, rows_gap)
    ck('t2 GAP_CRED + 读面 None ⇒ 不算互斥', r2 == [], r2)
    r3 = R.faces_contradiction(items_gap_measured, rows_ready)
    ck('t3 READY + MEASURED ⇒ 不算互斥', r3 == [], r3)

    # t4：变异对照 —— 把判据源码里的相等比较反过来，重编译后 t1 不应再检出
    text = io.open(src_path, encoding='utf-8').read()
    fn_src = None
    tree = ast.parse(text)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == 'faces_contradiction':
            fn_src = ast.get_source_segment(text, node)
    if fn_src is None:
        ck('t4 变异对照：可取到判据本体源码', False, '未找到 faces_contradiction');
    else:
        mutant = fn_src.replace("== 'MEASURED'", "!= 'MEASURED'")
        ck('t4a 变异点可命中（判据本体确实含该比较）', mutant != fn_src)
        ns = {'__name__': 'mutant'}
        exec(compile(mutant, '<mutant>', 'exec'), ns)
        m1 = ns['faces_contradiction'](items_gap_measured, rows_gap)
        ck('t4b 变异后 t1 不再检出（证明夹具对它要测的判据有牙）', m1 == [], m1)

    # t5：回归护栏 —— build() 必须把第 65 门行随 doc 交出（防 r252 假绿复发）
    doc, err = R.build()
    ck('t5a build() 可跑（err 为空）', err is None, err)
    if doc:
        has_rows = isinstance(doc.get('ft_rows'), list)
        ck('t5b doc 随带第 65 门行（ft_rows 是 list）', has_rows,
           type(doc.get('ft_rows')).__name__)
        ck('t5c doc 随带源件名（ft_src 非 None）', doc.get('ft_src') is not None, doc.get('ft_src'))

    n = len(OK) + len(BAD)
    print('夹具合计: %d 项，通过 %d，失败 %d' % (n, len(OK), len(BAD)))
    if BAD:
        print('[GATE:rosterfix-fail]');
        return 1
    print('[GATE:rosterfix-pass]');
    return 0


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
    sys.exit(main())