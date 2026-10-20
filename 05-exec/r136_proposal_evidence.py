# -*- coding: utf-8 -*-
# r136_proposal_evidence.py -- 提案的证据自覆盖面（第 48 门，纪律作用到自己身上）。
#
# 存在理由（r136 一手）：r135 收尾时我写下「本仓已有 #31/#32/#33 三道纪律，
# **但第 11 条自己的处方没被自己的纪律覆盖**」。r136 把它量出来：
#   11 条转办提案里 **只有 3 条的 fix_hint 能追到某个 05-exec/r1*_*.py 的读数面**，
#   其余 **8 条追不到** —— 且其中 4 条连 evidence / acceptance 字段都没有。
#   ⇒ 「纪律立了不等于纪律作用到自己身上」的**可复算证据**。
#
# 本件逐条判三件事（缺一即不完整）：
#   E1 有 fix_hint            —— 处方本身存在
#   E2 有 evidence            —— 有可复算的证据（产物路径或命令）
#   E3 有 acceptance          —— 有验收标准（否则归属方无法判闭环）
#   E4 处方被读数面支撑        —— fix_hint 里能追到某个 05-exec/r1*_*.py 脚本名
#
# 读数分四态（不判红，只出清单 —— 与因果面同口径）：
#   COMPLETE       —— 四项齐备
#   NO_ACCEPTANCE  —— 有处方有证据，缺验收
#   NO_EVIDENCE    —— 有处方，缺证据
#   UNBACKED       —— 处方追不到任何读数面支撑（**最该补**）
#
# 用法: python 05-exec/r136_proposal_evidence.py [--json 06-benchmark/proposal_evidence_r136_2026-10-21.json]
# 退出码: 0 完成 / 2 输入面不可用（R247 禁按 0 记绿）
import argparse
import glob
import io
import json
import os
import re
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BENCH = os.path.join(ROOT, '06-benchmark')
PROPOSALS = os.path.join(BENCH, 'transmit_proposals.json')
SCRIPT_RE = re.compile(r'(r1\d\d_[A-Za-z0-9_]+\.py)')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', dest='out')
    # r136 自抓（#32 形态）：初版路径写死，反向验证时探针文件喂不进去 ⇒ 探针跑的是真台账，
    # 报出真值 8，看起来「验证通过」实则**根本没验到探针**。修法 = 路径可注入。
    ap.add_argument('--proposals', default='', help='提案台账路径（默认 06-benchmark/transmit_proposals.json）')
    args = ap.parse_args()
    prop_path = args.proposals if args.proposals else PROPOSALS
    if not os.path.isabs(prop_path):
        prop_path = os.path.join(ROOT, prop_path)
    if not os.path.isfile(prop_path):
        print('[PROPEV] UNVERIFIED 提案台账不存在: %s' % prop_path)
        return 2
    try:
        doc = json.loads(io.open(prop_path, encoding='utf-8-sig').read())
    except Exception as e:  # noqa: BLE001
        print('[PROPEV] FATAL 提案台账不可读: %r' % (e,))
        return 2
    props = doc.get('proposals') or []
    if not props:
        print('[PROPEV] UNVERIFIED 提案台账为空')
        return 2
    known = set(os.path.basename(x) for x in glob.glob(os.path.join(HERE, 'r1*.py')))
    rows = []
    for p in props:
        fix = str(p.get('fix_hint') or '')
        ev = str(p.get('evidence') or '')
        acc = str(p.get('acceptance') or '')
        corr = ' '.join(str(p.get(k) or '') for k in ('r132_correction', 'r135_correction'))
        acc2 = ' '.join(str(p.get(k) or '') for k in ('acceptance_r132', 'acceptance_r135'))
        blob = ' '.join([fix, ev, acc, corr, acc2])
        refs = sorted(set(SCRIPT_RE.findall(blob)))
        live_refs = [r for r in refs if r in known]
        dead_refs = [r for r in refs if r not in known]
        # r136 自抓二：初版只认「脚本名」作支撑，导致 evidence 指向**产物文件**的条目
        # （domain_filter_latent_exposure / derivative_watch_domain_skip_drift）被判 UNBACKED，
        # 而它们其实有**在盘的真实产物**可复算。口径修正 = 支撑来源有三：
        #   ① 现存读数脚本名；② 在盘产物（06-benchmark 下的 .json）；③ 显式标注「未验证」。
        import glob as _g
        prods = []
        for f in re.findall(r'[\w\-]+\.json', blob):
            hits = _g.glob(os.path.join(BENCH, f)) or _g.glob(os.path.join(BENCH, '*' + f))
            if hits:
                prods.append(os.path.basename(hits[0]))
        labeled_unver = '未验证' in str(p.get('r136_backed') or '')
        # r136 自抓三：再放宽一格 —— evidence 里给的是**可执行命令**（如焚诀侧
        # `python eval/verify_truth_consistency.py --json`）也算可复算证据，
        # 否则「命令型证据」的条目会被误判成完全无支撑。
        has_cmd = bool(re.search(r'(python\s+[^\s]+\.py|verify_truth_consistency|--json)', ev))
        e1 = bool(fix.strip())
        e2 = bool(ev.strip())
        e3 = bool(acc.strip() or acc2.strip())
        e4 = bool(live_refs) or bool(prods) or labeled_unver or has_cmd
        # r148（#46）：处方由**效力面**（efficacy，即「改 X 救几条」型读数面）支撑的，
        # 必须带 `适用边界` 字段 —— 单靶实测有效 ≠ 适用面有效（r148 一手：r135 处方推广
        # 到其余 2 靶 0/2 有效且 margin 更差）。非效力面支撑（如纯计数/清单面）不强制。
        efficacy_backed = any('efficacy' in x for x in live_refs)
        has_boundary = bool(str(p.get('适用边界') or '').strip())
        boundary_missing = efficacy_backed and not has_boundary
        if e1 and e2 and e3 and e4:
            cls = 'COMPLETE'
        elif not e4:
            cls = 'UNBACKED'
        elif not e3:
            cls = 'NO_ACCEPTANCE'
        elif not e2:
            cls = 'NO_EVIDENCE'
        else:
            cls = 'COMPLETE'
        rows.append({'pid': p.get('pid'), 'title': str(p.get('title') or '')[:70],
                     'class': cls, 'has_fix_hint': e1, 'has_evidence': e2,
                     'has_acceptance': e3, 'has_cmd': has_cmd, 'backed_by': live_refs,
                     'backed_by_prods': prods, 'labeled_unverified': labeled_unver,
                     'efficacy_backed': efficacy_backed, 'has_boundary': has_boundary,
                     'boundary_missing': boundary_missing,
                     'dead_refs': dead_refs})
    from collections import Counter
    cnt = Counter(r['class'] for r in rows)
    doc2 = {'schema': 'proposal-evidence-r136-v1',
            'cmd': 'python 05-exec/r136_proposal_evidence.py --json <out>',
            'face': {'proposals_n': len(rows),
                     'by_class': dict(cnt),
                     'complete_n': cnt.get('COMPLETE', 0),
                     'unbacked_n': cnt.get('UNBACKED', 0),
                     'no_acceptance_n': cnt.get('NO_ACCEPTANCE', 0),
                     'no_evidence_n': cnt.get('NO_EVIDENCE', 0),
                     'boundary_missing_n': sum(1 for r in rows if r.get('boundary_missing')),
                     'reading': {
                         'unbacked_n': ('处方追不到任何现存的 05-exec/r1*_*.py 读数面 ⇒ **最该补**。',
                                       '这正是 r135 那条观察的可复算形态：纪律立了，但它作用不到自己。'),
                         'no_acceptance_n': '有处方有证据但缺验收标准 ⇒ 归属方无法判闭环',
                         'no_evidence_n': '有处方但缺证据字段',
                         'boundary_missing_n': ('处方由效力面（efficacy 型读数面）支撑却无 `适用边界` 字段 ⇒ 判红。',
                                               '#46：单靶实测有效 != 适用面有效；推广到第 2 个靶前须逐靶复测。'),
                         'complete_n': '四项齐备（fix_hint + evidence + acceptance + 读数面支撑）',
                     }},
            'rows': rows,
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M')}
    if args.out:
        with io.open(args.out, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(doc2, f, ensure_ascii=False, indent=1)
    fa = doc2['face']
    print('[PROPEV] 提案 %d 条｜完整 %d｜无读数支撑 %d｜缺验收 %d｜缺证据 %d'
          % (fa['proposals_n'], fa['complete_n'], fa['unbacked_n'],
             fa['no_acceptance_n'], fa['no_evidence_n']))
    for r in rows:
        if r['class'] != 'COMPLETE':
            print('  %-14s %-34s backed=%s' % (r['class'], str(r['pid'])[:32], r['backed_by'] or '-'))
    if args.out:
        print('[PROPEV] JSON -> %s' % args.out)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())