# -*- coding: utf-8 -*-
# r163_debt_fresh_fixtures.py -- _lib.ensure_debt_fresh 状态机自证（R163-6 共用实现）。
#
# 存在理由（r163）：这段逻辑原先只活在 run_gates._ensure_debt_fresh（约 71 行），
#   单独直调 ratchet_gate / r55 / r56 夹具时形同不存在 ⇒ AGENTS 已知坑第 2 条本轮第 5 次踩。
#   r163 把它抽到 _lib 并把 runner 改成委托；本夹具证明抽库后**五种状态各自可判**，
#   且新增的 FUTURE-VOL 分叉不是装饰（旧式会把「基准不可能达成」白跑两趟 r38）。
#
# 全程在临时目录造景，不读写真仓（#25④ 同向：不在生产面上做冒烟测试）。
import argparse
import io
import json
import os
import shutil
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import _lib  # noqa: E402

RESULTS = []


def ck(name, cond, detail=''):
    RESULTS.append((bool(cond), name, detail))
    print('%s %-52s %s' % ('PASS' if cond else 'FAIL', name, detail if not cond else ''))


def make_repo(tmp, with_volume=True, with_artifact=True):
    """造一个最小仓：memory/07-next-steps.md + 可选 06-benchmark/debt_aging_r*.json。"""
    repo = tmp
    (repo / 'memory').mkdir(parents=True, exist_ok=True)
    (repo / '06-benchmark').mkdir(parents=True, exist_ok=True)
    if with_volume:
        (repo / 'memory' / '07-next-steps.md').write_text('- [ ] x\n', encoding='utf-8')
    if with_artifact:
        (repo / '06-benchmark' / 'debt_aging_r1.json').write_text('{}', encoding='utf-8')
    return repo


def touch(path, offset):
    t = time.time() + offset
    os.utime(path, (t, t))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", dest="out", default="",
                    help="逐腿读数落 JSON 快照（门表对账登记用；缺省只打印）")
    args = ap.parse_args(argv)
    base = Path(os.environ.get('TMP', str(ROOT / '_temp'))) / 'r163_debt_fresh_fx'
    # s6（r163 回归护栏）：ratchet 的前置腿提示**不得走 stdout** ——
    #   一手事故：我把它 print 成 stdout 首行，r123_range_attr_fixtures 的「取首个非空行当判定行」
    #   当即判 6 条腿全红（真回归）。机器读的通道不得掺人读提示。
    import subprocess as _sp
    rg = HERE / 'ratchet_gate.py'
    pr = _sp.run([sys.executable, str(rg), '--baseline',
                  str(ROOT / '06-benchmark' / 'inject_ratchet_baseline.json')],
                 capture_output=True, text=True, encoding='utf-8', errors='replace',
                 cwd=str(ROOT), timeout=300)
    so = (pr.stdout or '').splitlines()
    first_line = next((l.strip() for l in so if l.strip()), '')
    ck('s6 前置腿提示不算 stdout 首行（防再撞「首行当判定行」的夹具）',
       '[RATCHET] 前置腿' not in first_line,
       'stdout 首行=%r' % (first_line[:70],))

    shutil.rmtree(base, ignore_errors=True)
    base.mkdir(parents=True, exist_ok=True)

    # s1 NO-VOLUME：没有 07 卷
    r1 = base / 's1'
    make_repo(r1, with_volume=False)
    st, why = _lib.ensure_debt_fresh(str(r1), str(HERE))
    ck('s1 无 07 卷 => NO-VOLUME（不得判新鲜）', st == 'NO-VOLUME', '%s | %s' % (st, why))

    # s2 NO-ARTIFACT：有卷无件
    r2 = base / 's2'
    make_repo(r2, with_artifact=False)
    st, why = _lib.ensure_debt_fresh(str(r2), str(HERE))
    ck('s2 无账龄件 => NO-ARTIFACT', st == 'NO-ARTIFACT', '%s | %s' % (st, why))

    # s3 OK：件新于卷
    r3 = base / 's3'
    make_repo(r3)
    touch(r3 / 'memory' / '07-next-steps.md', -600)
    touch(r3 / '06-benchmark' / 'debt_aging_r1.json', 0)
    st, why = _lib.ensure_debt_fresh(str(r3), str(HERE))
    ck('s3 件新于卷 => OK（等界放行）', st == 'OK', '%s | %s' % (st, why))

    # s4 FUTURE-VOL：卷 mtime 在未来 => 基准不可能达成（本轮新增分叉）
    r4 = base / 's4'
    make_repo(r4)
    touch(r4 / 'memory' / '07-next-steps.md', 3600)
    touch(r4 / '06-benchmark' / 'debt_aging_r1.json', 0)
    t0 = time.time()
    st, why = _lib.ensure_debt_fresh(str(r4), str(HERE))
    cost = time.time() - t0
    ck('s4 卷 mtime 在未来 => FUTURE-VOL 且不白跑重生（耗时<3s）',
       st == 'FUTURE-VOL' and cost < 3.0, '%s | %.2fs | %s' % (st, cost, why))

    # s5 REGEN-FAILED：卷比件新、但 r38 不在 exec_dir ⇒ 重生调用失败须**具名**不得静默判 OK
    r5 = base / 's5'
    make_repo(r5)
    touch(r5 / '06-benchmark' / 'debt_aging_r1.json', -600)
    touch(r5 / 'memory' / '07-next-steps.md', -300)
    st, why = _lib.ensure_debt_fresh(str(r5), str(base / 'no_such_dir'))
    ck('s5 缺 r38 生成器 => REGEN-FAILED 具名（非 OK/非 STALE-REGEN 混淆）',
       st == 'REGEN-FAILED', '%s | %s' % (st, why))

    # m1 变异对照：把 FUTURE 护栏摘掉 ⇒ s4 必须退化成 STALE-REGEN（且明显更慢）
    src = (HERE / '_lib.py').read_text(encoding='utf-8')
    mut = base / 'mut'
    mut.mkdir()
    if '_future > FUTURE_TOLERANCE_SEC' in src:
        msrc = src.replace('    if _future > FUTURE_TOLERANCE_SEC:', '    if False:  # MUTATED')
        mlib = mut / '_lib.py'
        mlib.write_text(msrc, encoding='utf-8', newline='')
        r6 = base / 's6'
        make_repo(r6)
        touch(r6 / 'memory' / '07-next-steps.md', 3600)
        touch(r6 / '06-benchmark' / 'debt_aging_r1.json', 0)
        import importlib.util
        spec = importlib.util.spec_from_file_location('_lib_mut', str(mlib))
        mmod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mmod)
        stm, whym = mmod.ensure_debt_fresh(str(r6), str(HERE))
        ck('m1 变异对照：摘 FUTURE 护栏 => s4 形态退化为 STALE-REGEN（证明 s4 的绿来自护栏）',
           stm == 'STALE-REGEN', '%s | %s' % (stm, whym))
    else:
        ck('m1 变异对照：找不到 FUTURE 护栏锚点（实现已变，须同步更新变异体）', False, 'anchor missing')

    shutil.rmtree(base, ignore_errors=True)
    fails = [x for x in RESULTS if not x[0]]
    print('\n夹具合计: %d 项，通过 %d，失败 %d' % (len(RESULTS), len(RESULTS) - len(fails), len(fails)))
    print('[GATE:fixture-fail]' if fails else '[GATE:fixture-pass]')
    if args.out:
        doc = {'schema': 'debt-fresh-fixtures-r163-v1',
               'cmd': 'python 05-exec/r163_debt_fresh_fixtures.py --json <out>',
               'legs': [{'name': n, 'ok': ok, 'detail': d} for ok, n, d in RESULTS],
               'n_pass': len(RESULTS) - len(fails), 'n_total': len(RESULTS),
               'verdict': 'FAIL' if fails else 'PASS',
               'target': '05-exec/_lib.py::ensure_debt_fresh'}
        with io.open(args.out, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
        print('[GATE:fixture] JSON -> %s' % args.out)
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())