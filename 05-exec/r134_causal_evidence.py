# -*- coding: utf-8 -*-
# r134_causal_evidence.py -- 因果结论的证据面（第 33 腿，R133-5 落地）。
#
# 存在理由（r133 自查出的缺口）：
#   #31（提案处方必先实测）管「处方」，#32（判据面三形态必实测）管「判据所读的面」——
#   但两者都**管不到结论层的推理**。r133 一手：
#     我推理「gsap 的 SKILL.md 有 7754 字符 ⇒ 会被压进固定长度 embedding 而稀释语义重心」，
#     写进工作稿；实测后差值只有 0.0004，**假设被自己的数据证伪**。
#     若没顺手测一下，它就会作为「根因」留在报告里 —— 这是第 5 次「我以为对，没量过」。
#
# r52_md_claim_face_scan.py 只判「数字有没有可复算命令」，**不判因果结论有没有实测支撑**。
# 本件补这一腿：把报告里的因果句（因为/所以/根因是/导致/说明…）逐条分类：
#   EVIDENCED   -- 同报告 ±N 行内有「取值：」命令或逐条读数表支撑（已实测）
#   INFERRED    -- 有因果表述但同报告内无实测支撑（**仅推理**）
#   FALSIFIED   -- 报告里同时存在「该假设被实测推翻」的证据（诚实记下了证伪）
#
# 关键设计（防判据自身假红，见 #32）：**INFERRED 不是红**，它是一份清单；
# 只有当报告把 INFERRED 写成「已实测」的口吻时才判问题面。
#
# 用法: python 05-exec/r134_causal_evidence.py --report <报告.md> [--json <件>]
# 退出码: 0 完成 / 2 输入面不可用（R247 禁按 0 记绿）
import argparse
import io
import json
import os
import re
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CAUSAL = re.compile(r'(因为|所以|根因是|根因|导致|说明|因此|由此可见|结论是|⇒)')
# r134 自抓二（反向验证第二次抓到）：初版 EVIDENCE 正则含「实测」二字，
# 而「我假设…被实测证伪」那句本身也含「实测」⇒ 纯推理句被同窗的证伪句「撑」成 EVIDENCED。
# 正解：**证据必须是可复算的东西**（取值命令 / 逐条读数表 / 复算），
# 「实测/证伪」这类**自我声明**不算证据 —— 声明可以撒谎，读数不会。
EVIDENCE = re.compile(r'(取值[：:]|`python|`pwsh|`Get-|`git |逐条读数|读数为|复算命令|实测读数|实测为\s*[0-9]|实测发现\s*[0-9])')
FALSIFY = re.compile(r'(被.*?证伪|已证伪|假设不成立|差仅|不成立)')
WINDOW = 14  # ±14 行内须有证据行（与 md_claim 的 ±12 同量级，取整）


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--report', required=True)
    ap.add_argument('--json', dest='out')
    ap.add_argument('--window', type=int, default=WINDOW)
    args = ap.parse_args()
    rp = args.report if os.path.isabs(args.report) else os.path.join(ROOT, args.report)
    # r134 自抓（#32 形态再次踩中）：runner 调脚本**不过 shell**，argv 里的 `*` 不会被展开
    # ⇒ 首跑报「报告不存在」UNVERIFIED。修法 = 工具自己支持 glob（并显式统计命中数）。
    if ('*' in rp or '?' in rp):
        import glob as _glob
        hits = sorted(_glob.glob(rp))
        if not hits:
            print('[CAUSAL] UNVERIFIED glob 无命中: %s' % args.report)
            return 2
        from collections import Counter as _C
        agg = _C()
        tot = {'causal': 0, 'evidenced': 0, 'inferred': 0, 'falsified': 0}
        for h in hits:
            lines_h = io.open(h, encoding='utf-8').read().split(chr(10))
            ev = [i for i, l in enumerate(lines_h) if EVIDENCE.search(l)]
            fa = [i for i, l in enumerate(lines_h) if FALSIFY.search(l)]
            c = e2 = i2 = f2 = 0
            for i, l in enumerate(lines_h):
                if not CAUSAL.search(l):
                    continue
                c += 1
                lo = max(0, i - args.window)
                hi = min(len(lines_h), i + args.window + 1)
                if FALSIFY.search(l):
                    f2 += 1
                elif any(lo <= j <= hi for j in ev):
                    e2 += 1
                else:
                    i2 += 1
            agg['EVIDENCED'] += e2
            agg['INFERRED'] += i2
            agg['FALSIFIED'] += f2
            tot['causal'] += c
            tot['evidenced'] += e2
            tot['inferred'] += i2
            tot['falsified'] += f2
        doc = {'schema': 'causal-evidence-r134-v1',
               'cmd': 'python 05-exec/r134_causal_evidence.py --report <glob>',
               'glob': args.report, 'reports_n': len(hits), 'window': args.window,
               'face': {'causal_lines_n': tot['causal'],
                        'evidenced_n': tot['evidenced'],
                        'inferred_n': tot['inferred'],
                        'falsified_n': tot['falsified'],
                        'reading': {
                            'inferred_n': '有因果表述但同报告 ±window 行内无可复算证据 = **仅推理**。不是红，是清单。',
                            'falsified_n': '本行自身记下了「该假设被实测推翻」—— 最诚实的写法，判为合规。',
                            'evidenced_n': '同报告 ±window 行内有取值命令 / 逐条读数 / 复算命令',
                        }},
               'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M')}
        if args.out:
            with io.open(args.out, 'w', encoding='utf-8', newline='\n') as f:
                json.dump(doc, f, ensure_ascii=False, indent=1)
        fa2 = doc['face']
        print('[CAUSAL] 报告 %d 份｜因果行 %d｜有实测支撑 %d｜仅推理 %d｜已记证伪 %d（±%d 行窗）'
              % (fa2['causal_lines_n'] and len(hits), fa2['causal_lines_n'],
                 fa2['evidenced_n'], fa2['inferred_n'], fa2['falsified_n'], args.window))
        if args.out:
            print('[CAUSAL] JSON -> %s' % args.out)
        return 0
    if not os.path.isfile(rp):
        print('[CAUSAL] UNVERIFIED 报告不存在: %s' % args.report)
        return 2
    try:
        lines = io.open(rp, encoding='utf-8').read().split(chr(10))
    except Exception as e:  # noqa: BLE001
        print('[CAUSAL] FATAL 报告不可读: %r' % (e,))
        return 2
    if not lines:
        print('[CAUSAL] UNVERIFIED 报告零行')
        return 2
    ev_lines = [i for i, l in enumerate(lines) if EVIDENCE.search(l)]
    fa_lines = [i for i, l in enumerate(lines) if FALSIFY.search(l)]
    rows = []
    for i, l in enumerate(lines):
        if not CAUSAL.search(l):
            continue
        lo = max(0, i - args.window)
        hi = min(len(lines), i + args.window + 1)
        near_ev = [j for j in ev_lines if lo <= j <= hi]
        near_fa = [j for j in fa_lines if lo <= j <= hi]
        # r134 自抓（反向验证抓到的）：初版判 FALSIFIED 的条件是「窗内有证伪行且在本行之后」，
        # 结果三条纯推理句全被判 FALSIFIED —— 因为本报告里**证伪句在后面**，窗内可见。
        # 正确口径：**只有本行自身**含证伪措辞才算 FALSIFIED（诚实地写下「我假设…被证伪」）；
        # 邻近的证伪行只能作为「作者知情」的旁证，不能改变本行的因果性质。
        if FALSIFY.search(l):
            cls = 'FALSIFIED'
        elif near_ev:
            cls = 'EVIDENCED'
        else:
            cls = 'INFERRED'
        rows.append({'line': i + 1, 'class': cls,
                     'text': l.strip()[:160],
                     'near_evidence': [j + 1 for j in near_ev[:3]],
                     'near_falsify': [j + 1 for j in near_fa[:3]]})
    from collections import Counter
    cnt = Counter(r['class'] for r in rows)
    doc = {'schema': 'causal-evidence-r134-v1',
           'cmd': 'python 05-exec/r134_causal_evidence.py --report <report> --json <out>',
           'report': os.path.basename(rp),
           'window': args.window,
           'face': {'causal_lines_n': len(rows),
                     'evidenced_n': cnt.get('EVIDENCED', 0),
                     'inferred_n': cnt.get('INFERRED', 0),
                     'falsified_n': cnt.get('FALSIFIED', 0),
                     'evidence_line_n': len(ev_lines),
                     'reading': {
                         'inferred_n': ('有因果表述但同报告 ±window 行内无实测支撑 = **仅推理**。',
                                        '这不是红，是清单：它们的正确处理是标注「未实测」或补一次实测。'),
                         'falsified_n': ('报告里同时记下了「该假设被实测推翻」—— 这类是最诚实的写法，',
                                         '判为合规（诚实记下证伪强于假装对）。'),
                         'evidenced_n': '同报告 ±window 行内有取值命令 / 逐条读数表支撑',
                     }},
           'inferred': [r for r in rows if r['class'] == 'INFERRED'][:40],
           'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M')}
    if args.out:
        with io.open(args.out, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
    fa = doc['face']
    print('[CAUSAL] 因果行 %d｜有实测支撑 %d｜仅推理 %d｜已记证伪 %d（±%d 行窗）'
          % (fa['causal_lines_n'], fa['evidenced_n'], fa['inferred_n'],
             fa['falsified_n'], args.window))
    for r in doc['inferred'][:6]:
        print('  INFERRED L%-4d %s' % (r['line'], r['text'][:80]))
    if args.out:
        print('[CAUSAL] JSON -> %s' % args.out)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())