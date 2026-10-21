# -*- coding: utf-8 -*-
# r149_derived_freshness.py -- 派生件新鲜度转诊面（第 56 门，#47 落地）。
#
# 存在理由（r148 一手，r149 定位）：第 11 类（语料语言不匹配）源侧已修
#   （gsap frontmatter 补中文，受管根 b6b784d6），生产面翻绿的唯一残因 = BGE 派生件未重建。
#   r149 核验发现：陈旧检测在归属方早已存在且校准良好 ——
#   焚诀 eval/derivative_watch.stale_sources() 以编码产物(npy)mtime 为基准，
#   现算点名 source=gsap lag=7339.3s（190 件里只报这 1 条，其 docstring 明说
#   避开 45 个正常编辑件误报的陷阱）；它还在焚诀 pre-commit 第 7 闸活链里。
#   但本仓看不到它：R148-4 挂着等重建，重建发生的当天没有任何常驻面会自动发现。
#
# 解法 = 转诊（不造轮子、不代跑）：只读 import 归属方的权威函数，把读数引入本仓门禁。
#   红线合规：对 eval/ 仅 import 调用，零写入；重建动作仍归归属方（R269）。
#
# 判定语义（#35 分级：别人的活不连坐成我的红）：
#   stale_sources() 返回 None（取不到数）=> UNVERIFIED rc=2（R247，禁读成新鲜）
#   返回 []（全新鲜）=> PASS rc=0，class_11_closed=True（终判闭环日=本面转绿日）
#   返回含 gsap => PASS rc=0 + 非阻断告警，stale_gsap=True（转办线未闭环，如实显示）
#   返回不含 gsap 的其他过期 => PASS rc=0 告警，本仓转办线视为已闭环（不连坐他人漂移）
#
# 反向验证（#32 三态）：现源点名 gsap / touch mtime 后不报 / 空源 UNVERIFIED。
#
# 用法: python 05-exec/r149_derived_freshness.py [--json 06-benchmark/derived_freshness_r149_2026-10-21.json]
# 退出码: 0 采集面可用（含告警态） / 2 输入面不可用
import argparse
import importlib
import io
import json
import os
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
EVAL_DIR = r'C:/Users/37533/Desktop/workspace/焚诀/eval'
# r151：selftest 内部要调 main() 取六态读数，用护栏防自递归。
# （用可变容器而非 global 名，避开「global 先于使用」的语法约束）
_SELF = {'on': False}


def load_stale_fn():
    if not os.path.isdir(EVAL_DIR):
        return None, 'eval 目录不存在' 
    sys.path.insert(0, EVAL_DIR)
    try:
        m = importlib.import_module('derivative_watch')
        fn = getattr(m, 'stale_sources', None)
        if fn is None:
            return None, '归属方无 stale_sources（函数改名/删除 => 转诊断链）'
        return fn, 'ok'
    except Exception as e:
        return None, 'import 失败: %r' % (e,)
    finally:
        try:
            sys.path.remove(EVAL_DIR)
        except ValueError:
            pass




# ── r151 常驻反向验证（第 56 门自身的「判据的判据」腿）────────────────────────
# 存在理由（r151 一手，#32 第四形态的新变体）：r149 的六态注入只 print 出 want 串，
#   从未与 got 比对（探针里 allok 变量算完没用于退出），且「只含他人漂移」那条腿
#   根本没断言 class_11_closed ⇒ 「反向验证六态全对」是**无牙的读数**，连坐 bug 因此活过了验证。
#   修法不是再写一个 _temp 探针，是把断言做进门脚本本体并常驻复跑：任一腿 want≠got ⇒ rc=1。

def relay_shape_check(stale):
    # r151 归属方返回面的形状守卫：返回漂移描述串 = 不可信；返回 None = 口径可用。
    if not isinstance(stale, list):
        return '返回值类型 %s 非 list（对方改口径）' % type(stale).__name__
    for i, h in enumerate(stale):
        if not isinstance(h, dict):
            return '第 %d 项类型 %s 非 dict（对方改口径）' % (i, type(h).__name__)
        if 'source' not in h:
            return "条目缺 'source' 键（实际键 %s）——按名过滤会落空，禁读成闭环" % (sorted(h.keys()),)
    return None

def _six_states():
    gsap = [{'source': 'gsap', 'artifact': 'bge_fullbody_embeddings.npy', 'lag_s': 7339.3}]
    others = [{'source': 'blender-pipeline', 'artifact': 'x.npy', 'lag_s': 12.0}]
    return [
        # (名称, 注入返回值, 抛异常, 判据不可达, want_rc, want_stale_gsap, want_others, want_closed)
        ('S1 现源含gsap', gsap, False, False, 0, True, 0, False),
        ('S2 全新鲜[]', [], False, False, 0, False, 0, True),
        ('S3 只他人漂移(#35不连坐)', others, False, False, 0, False, 1, True),
        ('S4 归属None取不到数', None, False, False, 2, None, None, None),
        ('S5 归属函数抛异常', None, True, False, 2, None, None, None),
        ('S6 判据不可达', None, False, True, 2, None, None, None),
        # r151 改造3：口径形状漂移两腿（对方改字段名/改返回类型 ⇒ UNVERIFIED，禁假闭环）
        ('S7 对方改字段名source→slug', [{'slug': 'gsap', 'lag_s': 7339.3}], False, False, 2, None, None, None),
        ('S8 对方改返回类型 list[str]', ['gsap', 'xlsx'], False, False, 2, None, None, None),
    ]


def _one_state(ret, raises, loadfail):
    """在临时目录跑一次 main()，返回 (rc, face 或 None)。不碰 eval、不碰受管根。"""
    import contextlib
    import tempfile

    global load_stale_fn
    real = load_stale_fn
    if loadfail:
        load_stale_fn = lambda: (None, 'injected-unreachable')
    else:
        def fake():
            if raises:
                raise RuntimeError('injected-boom')
            return ret
        load_stale_fn = lambda: (fake, 'injected')
    d = tempfile.mkdtemp()
    outj = os.path.join(d, 'o.json')
    real_argv = sys.argv
    sys.argv = ['r149_selftest', '--json', outj]
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            rc = main()
        face = None
        if os.path.isfile(outj):
            face = json.loads(io.open(outj, encoding='utf-8-sig').read()).get('face')
        return rc, face, buf.getvalue()
    finally:
        sys.argv = real_argv
        load_stale_fn = real


def selftest():
    quiet = _SELF['on']
    if not quiet:
        print('[FRESH-D] 反向验证（%d 态 want⇄got 逐腿断言）：' % len(_six_states()))
    bad = 0
    for nm, ret, raises, loadfail, wrc, wgsap, woth, wclo in _six_states():
        rc, face, out = _one_state(ret, raises, loadfail)
        g = (face.get('stale_gsap'), face.get('others_n'), face.get('class_11_closed')) if face else (None, None, None)
        want = (wgsap, woth, wclo)
        ok = (rc == wrc) and (g == want if wrc == 0 else face is None)
        # S4/S5/S6 额外断言：UNVERIFIED 态禁落 face（不落快照才不会被下游读成新鲜）
        if not ok:
            bad += 1
        if quiet and ok:
            continue
        print('  %s %-26s rc=%d(got)/%d(want) face=%s want=%s'
              % ('PASS' if ok else 'FAIL', nm, rc, wrc,
                 g if wrc == 0 else '(no-json)', want if wrc == 0 else '(no-json)'))
    if bad:
        print('[FRESH-D:SELFTEST-FAIL] 失配 %d 腿 —— 判据无牙则其读数不可信（#32）' % bad)
        return 1
    if not quiet:
        print('[FRESH-D:SELFTEST-PASS] %d/%d 全对（含 S3 不连坐腿 + S7/S8 口径漂移腿）' % (len(_six_states()), len(_six_states())))
    return 0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', dest='out')
    ap.add_argument('--selftest', action='store_true',
                    help='r151 常驻反向验证：六态逐腿 want⇄got 断言，任一不符 rc=1')
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    # r151：真实读数前先自证判据有牙（#32）——
    #   无牙判据读出来的 0 不可信，故牙齿失败即本门 FAIL，不再出读数。
    if not _SELF['on']:
        _SELF['on'] = True
        try:
            if selftest() != 0:
                print('[FRESH-D] 反向验证失配 ⇒ 本门读数不可信，不出真实态')
                return 1
        finally:
            _SELF['on'] = False
    fn, note = load_stale_fn()
    if fn is None:
        print('[FRESH-D] UNVERIFIED 归属方判据不可达: %s' % note)
        return 2
    try:
        stale = fn()
    except Exception as e:
        print('[FRESH-D] UNVERIFIED 归属函数调用异常: %r' % (e,))
        return 2
    if stale is None:
        print('[FRESH-D] UNVERIFIED 取不到可比对象（R247 禁读成新鲜）')
        return 2
    # r151 改造3：归属方**口径形状守卫**（#47 第②件的落地形态）。
    #   量化坐实（_temp/r151_relay_shape_probe.py）：对方把 'source' 改名为 'slug' 时，
    #   gsap 其实仍陈旧，但旧实现读成 stale_gsap=False / class_11_closed=True 且 rc=0 ——
    #   这是**假闭环**：把「读不到这个字段」洗成「这个靶已新鲜」，正是 R247 禁的那一类。
    #   返回结构从 list[dict] 变成 list[str]/dict 时旧实现直接 AttributeError 裸崩（不 UNVERIFIED）。
    #   正解 = 不认识的面 ⇒ UNVERIFIED rc=2，绝不出闭环读数。
    shape = relay_shape_check(stale)
    if shape:
        print('[FRESH-D] UNVERIFIED 归属方口径形状漂移：%s（R247 禁读成新鲜/禁判闭环）' % shape)
        return 2
    gsap = [h for h in stale if h.get('source') == 'gsap'] or None
    others = [h for h in stale if h.get('source') != 'gsap']
    # r151 根治（#35 分级）：本仓转办线的终判**只看 gsap 这一条靶**是否转新鲜；
    # 他人陈旧单列 others_n 作告警，**不连坐**本仓闭环。旧式 (not gsap) and (not others)
    # 与本文件头部注释及门表 covers 的「他人漂移不连坐」直接矛盾：r151 真实态（gsap 已重建、
    # 面上剩 2 件他人陈旧）被读成 class_11_closed=False，即「已闭环判成未闭环」。
    closed = not gsap
    face = {
        'stale_n': len(stale),
        'stale_gsap': bool(gsap),
        'stale_gsap_lag_s': (gsap[0].get('lag_s') if gsap else None),
        # lag 键改名不影响闭环判定（判据只看 source==gsap），但 lag 读数会静默变 None ⇒ 显形
        'lag_field_missing': bool(gsap) and ('lag_s' not in gsap[0]),
        'others_n': len(others),
        'class_11_closed': closed,
        'closed_scope': 'class_11_closed 只看 source==gsap（r151/#35 不连坐）；others_n 为归属方他人陈旧，单列告警',
        'relay': '只读 import 归属方 stale_sources；重建动作归焚诀侧（R269）',
        'closed_reading': '第 11 类生产终判闭环的机器读数 = stale_gsap 由 True 转 False 当天',
    }
    doc = {
        'schema': 'derived-freshness-r149-v1',
        'cmd': 'python 05-exec/r149_derived_freshness.py --json <out>',
        'face': face,
        'rows': stale,
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M'),
    }
    if args.out:
        with io.open(args.out, 'w', encoding='utf-8', newline=chr(10)) as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
    print('[FRESH-D] 过期 %d 件 | gsap=%s（lag=%s s）| 第 11 类生产终判 %s | 他人漂移不连坐 %d 件'
          % (face['stale_n'], '待重建' if face['stale_gsap'] else '已转新鲜',
             face['stale_gsap_lag_s'], '闭环' if face['class_11_closed'] else '未闭环', face['others_n']))
    if face['others_n']:
        print('[FRESH-D] 告警（不判红）归属方他人陈旧 %d 件，重建动作归焚诀侧（R269）' % face['others_n'])
    for h in stale[:5]:
        print('  STALE %s -> %s lag=%.0fs' % (h.get('source'), h.get('artifact'), h.get('lag_s', 0)))
    if args.out:
        print('[FRESH-D] JSON -> %s' % args.out)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())