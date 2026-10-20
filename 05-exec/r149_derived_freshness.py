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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', dest='out')
    args = ap.parse_args()
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
    gsap = [h for h in stale if h.get('source') == 'gsap'] or None
    others = [h for h in stale if h.get('source') != 'gsap']
    closed = (not gsap) and (not others)
    face = {
        'stale_n': len(stale),
        'stale_gsap': bool(gsap),
        'stale_gsap_lag_s': (gsap[0].get('lag_s') if gsap else None),
        'others_n': len(others),
        'class_11_closed': closed,
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
    print('[FRESH-D] 过期 %d 件 | gsap=%s（lag=%s s）| 第 11 类生产终判 %s'
          % (face['stale_n'], '待重建' if face['stale_gsap'] else '已闭环',
             face['stale_gsap_lag_s'], '闭环' if face['class_11_closed'] else '未闭环'))
    for h in stale[:5]:
        print('  STALE %s -> %s lag=%.0fs' % (h.get('source'), h.get('artifact'), h.get('lag_s', 0)))
    if args.out:
        print('[FRESH-D] JSON -> %s' % args.out)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())