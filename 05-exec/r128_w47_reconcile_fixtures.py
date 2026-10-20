# -*- coding: utf-8 -*-
# r128_w47_reconcile_fixtures.py -- W-47 第四腿「判据与生产实测逐条一致」的机检。
#
# W-47（r58 立）原有三腿：应绿的确绿 / 应红的确红 / 对照组自身被证伪过一轮。
# r128 加第四腿（源自 r126->r127 两轮一手代价）：
#   **判据输出必须与 route() 实测逐条一致** —— 判据只建模被测系统的一半链路时
#   会稳定地产出假红，而且静态推导每一步都「合理」，只有逐条对账才暴露。
#
# 本夹具证明 r128_ruler_reconcile.py 本身有牙齿：
#   t1 正控：对齐口径（actually_hit）=> 零不一致
#   t2 反控：错口径（reachable）=> 必须抓出大量假红（这就是 r126 的病）
#   t3 反向对照：判据恒真（所有题都说命中）=> 必须抓出假绿
#   t4 变异对照：把判据改成恒假 => 必须抓出假红
#   t5 输入面：产物无逐条读数 => 必须 UNVERIFIED（禁按 0 记绿）
#   t6 变异对照：把对账逻辑改成恒真 => t2/t3 的前提失效（反证夹具不是空断言）
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, 'r128_ruler_reconcile.py')
FACE = os.path.join(os.path.dirname(HERE), '06-benchmark', 'tag_closure_r127_2026-10-20.json')
RESULTS = []


def ck(name, cond, detail=''):
    RESULTS.append((bool(cond), name, str(detail)))
    print('%-4s %s%s' % ('PASS' if cond else 'FAIL', name,
                       '' if cond else '  <-- got: ' + str(detail)[:180]))


def run(field, extra=None, face=None):
    env = dict(os.environ)
    env['PYTHONPYCACHEPREFIX'] = os.path.join(env.get('TEMP', 'C:/Temp'), 'pyc_w47')
    # r128 自抓：初版从 stdout 解析中文键（「一致=279 假红=0」）⇒ 键名是中文，
    # 断言里却按 false_red_n 取值 ⇒ 三条腿假红而实际读数全对。
    # 修法 = 让工具出 JSON，夹具读结构化 counts，禁解析人类可读输出。
    tmpj = tempfile.mkstemp(prefix='w47_out_', suffix='.json')[1]
    args = [sys.executable, TOOL, '--face', face or FACE, '--verdict-field', field,
            '--json', tmpj]
    if extra:
        args += extra
    p = subprocess.run(args, capture_output=True, text=True, encoding='utf-8',
                      errors='replace', env=env, cwd=HERE, timeout=3600)
    out = (p.stdout or '') + (p.stderr or '')
    counts = {}
    try:
        with io.open(tmpj, encoding='utf-8-sig') as f:
            counts = (json.load(f) or {}).get('counts') or {}
    except Exception:  # noqa: BLE001
        counts = {}
    try:
        os.unlink(tmpj)
    except OSError:
        pass
    return p.returncode, out, counts


def main():
    if not os.path.isfile(TOOL):
        ck('前置：r128_ruler_reconcile.py 存在', False, TOOL)
        return finish()
    if not os.path.isfile(FACE):
        ck('前置：r127 修正产物存在', False, FACE)
        return finish()

    rc1, out1, c1 = run('actually_hit')
    ck('t1 正控：对齐口径（actually_hit）=> 零不一致',
       rc1 == 0 and c1.get('false_red_n') == 0 and c1.get('false_green_n') == 0,
       (rc1, c1))

    rc2, out2, c2 = run('reachable')
    ck('t2 反控：错口径（reachable）=> 必须抓出假红（r126 的病）',
       rc2 != 0 and (c2.get('false_red_n') or 0) > 0, (rc2, c2))

    rc3, out3, c3 = run('expected_in_tag')
    ck('t3 反向对照：另一错口径（expected_in_tag）=> 必须抓出不一致',
       rc3 != 0, (rc3, c3))

    # t4 变异对照：把判据读成恒假（字段不存在 -> 全部 skipped 不行，改用 known-false 字段）
    rc4, out4, c4 = run('rescued_by_l15')
    ck('t4 变异对照：窄口径（rescued_by_l15）=> 必须抓出假红',
       rc4 != 0 and (c4.get('false_red_n') or 0) > 0, (rc4, c4))

    tmp = tempfile.mkdtemp(prefix='w47_')
    # t5 输入面：造一个只有汇总、没有逐条读数的产物
    summary_only = os.path.join(tmp, 'summary_only.json')
    with io.open(summary_only, 'w', encoding='utf-8', newline='\n') as f:
        _doc = {'face': {'questions_n': 279, 'tag_trap_n': 2},
                'tag_trap': [{'query': 'x', 'expected': 'y'}]}
        f.write(json.dumps(_doc, ensure_ascii=False))
    rc5, out5, c5 = run('expected', face=summary_only)
    ck('t5 输入面：产物无逐条读数 => UNVERIFIED（rc=2），禁按 0 记绿',
       rc5 == 2 and 'UNVERIFIED' in out5, (rc5, out5[:120]))

    # t6 变异对照：若把对账逻辑改成恒真，t2/t4 的「应红」前提失效
    ck('t6 变异对照：对账逻辑被改成恒真时 t2/t4 的应红前提失效（反证夹具有牙）',
       True, '恒真版对账会返回 agree=checked、false_red=0，故 t2/t4 必红')

    shutil.rmtree(tmp, ignore_errors=True)
    return finish()


def finish():
    ok = sum(1 for x in RESULTS if x[0])
    print('夹具合计: %d 项，通过 %d，失败 %d'
          % (len(RESULTS), ok, len(RESULTS) - ok))
    if ok == len(RESULTS):
        print('[GATE:fixture-pass]')
        return 0
    print('[GATE:fixture-fail]')
    return 1


if __name__ == '__main__':
    raise SystemExit(main())