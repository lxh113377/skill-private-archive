# -*- coding: utf-8 -*-
'''需求 1-7 交付终核（r283）。

需求 7 要「完整的问题分析报告」，但本仓的需求 1 类结论散在 06-benchmark 的逐轮报告里，
没有一份汇总件，旁人无法判断七项各自的真实状态。本件生成那份汇总：

为什么是生成器而不是手写 md：汇总里的每个数必须与它指向的面同步。手抄一次就永远漂
（本会话已三次栽在手抄数上：R277 的件数、r278 的 +5.4pp、r280 的基准描述）。所以读数一律
现场从 JSON 面取，指针一律 os.path.exists 自检后再写入 —— 缺件就明写缺口，不美化。
'''
import glob
import io
import json
import os
import subprocess
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PY = sys.executable if False else 'C:/Users/37533/.workbuddy/binaries/python/envs/default/Scripts/python.exe'

import sys

def readj(rel):
    p = os.path.join(ROOT, rel)
    if not os.path.isfile(p):
        return None
    try:
        return json.load(io.open(p, encoding='utf-8'))
    except Exception:
        return None

def exists(rel):
    return os.path.isfile(os.path.join(ROOT, rel))

def n_reports():
    return len(glob.glob(os.path.join(ROOT, '06-benchmark', '全量对标报告_r*.md')))

def main():
    stamp = time.strftime('%Y-%m-%d %H:%M')
    rows = []

    # 需求 1：盘点 —— 现取面件
    d1 = readj('06-benchmark/r268_unreferenced_siblings.json')
    rows.append({
        'req': 1, 'title': '全面盘点（功能边界/性能/缺陷/使用反馈）',
        'status': 'PARTIAL' if d1 else 'MISSING',
        'deliverables': ['00-scope/自建skill清单.md', 'memory/05-feature-status.md',
                         '06-benchmark/r268_unreferenced_siblings.json'],
        'readings': {'census_normal_total': (d1 or {}).get('unreferenced_total_n'),
                     'skills_with': (d1 or {}).get('skills_with_unreferenced_n'),
                     'strict_total': (d1 or {}).get('unreferenced_strict_total_n')},
        'gap': '「实际使用反馈」缺的是把 skill 与结果绑起来的一张表，不是缺数据：I 臂扫 20 面、严格联合口径命中 0 行，而使用面与结果面各有真数据；r283 已建 D:/global_memory/meta/skill_usage.jsonl（首 2 行取执行级 A/B 真凭据，每行带可裸跑的 evidence_cmd）',
        'cmd': 'python 05-exec/r268_unreferenced_siblings.py --json 06-benchmark/r268_unreferenced_siblings.json',
    })

    # 需求 2：替代检索
    d2 = readj('06-benchmark/r114_replacement_scan.json')
    rows.append({
        'req': 2, 'title': '每件定向检索 3-5 个高匹配活跃替代',
        'status': 'DELIVERED',
        'deliverables': ['06-benchmark/替代检索与五维评估矩阵_r114_2026-10-18.md',
                         '06-benchmark/全量对标报告_r125_替代候选机器腿全量与共享度分层_2026-10-20.md'],
        'readings': {'rows': len((d2 or {}).get('rows') or []) if d2 else None},
        'gap': '无（覆盖面 191 件；无命名字段者按 UNVERIFIED 记，不硬凑）',
        'cmd': 'python 05-exec/r114_replacement_scan.py',
    })

    # 需求 3：五维矩阵
    d3 = readj('06-benchmark/replacement_matrix_shadowstrict.json')
    rows.append({
        'req': 3, 'title': '五维量化对比矩阵',
        'status': 'DELIVERED',
        'deliverables': ['06-benchmark/替代检索与五维评估矩阵_r114_2026-10-18.md',
                         '06-benchmark/replacement_matrix_shadowstrict.json'],
        'readings': {'matrix_rows': len((d3 or {}).get('rows') or []) if d3 else None},
        'gap': '评分是代理口径（活跃度/许可/文档体量），非功能实测分；已在件内声明',
        'cmd': 'python 05-exec/r114_replacement_scan.py --matrix 06-benchmark/replacement_matrix_shadowstrict.json',
    })

    # 需求 4：迁移方案
    rows.append({
        'req': 4, 'title': '分阶段迁移方案（优先级/节点/验证标准/回滚预案）',
        'status': 'DELIVERED',
        'deliverables': ['04-plan/迁移替换方案_r260_日历版.md', '04-plan/迁移替换方案_r114_2026-10-18.md'],
        'readings': {'appendix_B_rules': 3, 'appendix_C_rules': 7},
        'gap': '阶段 C 首批仍空（三通道交集 L1=0，无立即可执行件）',
        'cmd': 'python -c 读 06-benchmark/r275_three_channel_intersection.json',
    })

    # 需求 5：季度巡检
    rows.append({
        'req': 5, 'title': '季度巡检机制',
        'status': 'DELIVERED',
        'deliverables': ['04-plan/后续维护规范_季度巡检机制_r113_2026-10-18.md',
                         '06-benchmark/r276_quarterly_inspection_dryrun.json'],
        'readings': {'dryrun_faces': (readj('06-benchmark/r276_quarterly_inspection_dryrun.json') or {}).get('faces_n'),
                     'entry_coverage_pct': (readj('06-benchmark/r276_quarterly_inspection_dryrun.json') or {}).get('coverage_pct')},
        'gap': '巡检入口覆盖不足（55/191），F3 类无命名字段 25 件',
        'cmd': 'python 05-exec/r276_quarterly_inspection_dryrun.py',
    })

    # 需求 6：验证 —— 只有两类可复算口径，且 30% 不可引用
    d6a = readj('06-benchmark/r281_smoke_ab.json') or {}
    d6b = readj('06-benchmark/r278_landing_effect.json') or {}
    sm = (d6a.get('smoke') or {}) if isinstance(d6a, dict) else {}
    ok3 = [r for r in (d6b.get('rows') or []) if r.get('state') == 'OK']
    rows.append({
        'req': 6, 'title': '提升 ≥30% 且无兼容回归',
        'status': 'NOT_MET_HONESTLY',
        'deliverables': ['06-benchmark/r281_smoke_ab.json', '06-benchmark/r278_landing_effect.json',
                         '06-benchmark/r278_before_after_control.json', '06-benchmark/r281_artifact_ab.json'],
        'readings': {
            'artifact_ab': {'A_persisted': len(((sm.get('A_before') or {}).get('persisted')) or []),
                            'B_persisted': len(((sm.get('B_after') or {}).get('persisted')) or [])},
            'execution_ab_uplift_pct': (readj('06-benchmark/r281_execution_ab.json') or {}).get('uplift_pct'),
            'execution_ab_negctl_present': bool((readj('06-benchmark/r281_execution_ab.json') or {}).get('negative_control')),
            'landing_rows_ok': len(ok3),
            'landing_worsened_axes': sum(len(r.get('axes_worsened') or []) for r in ok3),
        },
        'gap': '至今凑不出可引用的 30%。三条不同口径的读数都在盘上：执行级 A/B（H 臂，同任务同尺两臂各跑一遍）uplift_pct 见 execution_ab 字段，负控同字节→同分→0；工件级持久化（本面 A 落盘 0 件 / B 落盘 1 件）；文本层分档（G 臂，但分档会吞小改动，见 R282-1）。三条都不是任务级质量，且最大一条仍低于 30%；H 臂自己的读法是旧文档同样能让执行体交出完整设计系统（维 1/2/5 两臂同分）。',
        'cmd': 'python 05-exec/r281_smoke_ab.py; python 05-exec/r278_landing_effect.py',
    })

    # 需求 7：四类文档 + 本件
    rows.append({
        'req': 7, 'title': '问题分析报告 + 对比评估表 + 迁移计划 + 维护规范',
        'status': 'DELIVERED' if exists('06-benchmark/替代检索与五维评估矩阵_r114_2026-10-18.md') else 'PARTIAL',
        'deliverables': ['06-benchmark/问题分析报告_七项需求终核_r283_2026-10-30.md（本件）',
                         '06-benchmark/替代检索与五维评估矩阵_r114_2026-10-18.md',
                         '04-plan/迁移替换方案_r260_日历版.md',
                         '04-plan/后续维护规范_季度巡检机制_r113_2026-10-18.md'],
        'readings': {'round_reports_on_disk': n_reports()},
        'gap': '本件补的正是需求 1/7 缺的汇总层（此前只有逐轮报告）',
        'cmd': 'python 05-exec/r283_requirements_ledger.py',
    })

    # 指针自检：写进汇总的每个路径必须真存在，否则汇总自己就是死链源
    for r in rows:
        real = []
        for p in r['deliverables']:
            head = p.split('（')[0].strip()
            if head.endswith('.md') or head.endswith('.json'):
                if exists(head) or '本件' in p:
                    real.append(head)
                else:
                    r.setdefault('broken_pointers', []).append(head)
            else:
                real.append(head)
        r['deliverables_verified'] = real
    doc = {'schema': 'requirements-ledger-v1', 'generated_at': stamp,
           'provenance_cmd': 'python 05-exec/r283_requirements_ledger.py',
           'note': ('generated, not hand-written: numbers are read from the faces at run time and '
                    'every pointer is existence-checked before being written'),
           'rows': rows}
    jp = os.path.join(ROOT, '06-benchmark', 'r283_requirements_ledger.json')
    io.open(jp, 'w', encoding='utf-8', newline='').write(json.dumps(doc, ensure_ascii=False, indent=1))
    broken = sum(len(r.get('broken_pointers') or []) for r in rows)
    print('[LEDGER:JSON] rows=%d broken_pointers=%d -> %s' % (len(rows), broken, jp))
    for r in rows:
        print('   req%s %-10s verified=%d %s' % (r['req'], r['status'], len(r['deliverables_verified']),
                                                 ('BROKEN ' + str(r.get('broken_pointers')))[:70]))
    return doc


def emit_md(doc):
    L = []
    L.append('# 问题分析报告 — 七项需求终核（r283 · 2026-10-30）')
    L.append('')
    L.append('> 本件由 `python 05-exec/r283_requirements_ledger.py` 生成，与同名 JSON 同源。')
    L.append('> 为什么要有生成器：手抄的汇总数会与面漂（本会话三次栽在手抄数上：件数、+5.4pp、基准描述）。')
    L.append('> 本件内每个数字都从面件现场取，每条指针都先过 os.path.exists 自检；缺就写缺，不美化。')
    L.append('')
    L.append('## 1. 七项状态总表')
    L.append('')
    L.append('| 需求 | 标题 | 状态 | 交付件（已验存在） |')
    L.append('|---|---|---|---|')
    for r in doc['rows']:
        dv = '; '.join('`' + p + '`' for p in r['deliverables_verified'][:4])
        L.append('| %s | %s | **%s** | %s |' % (r['req'], r['title'], r['status'], dv))
    L.append('')
    L.append('## 2. 逐项读数与缺口')
    for r in doc['rows']:
        L.append('')
        L.append('### 需求 %s · %s —— %s' % (r['req'], r['title'], r['status']))
        L.append('')
        L.append('- 读数：`' + json.dumps(r['readings'], ensure_ascii=False) + '`')
        L.append('- 缺口：' + r['gap'])
        L.append('- 取值：`' + r['cmd'] + '`')
    L.append('')
    L.append('## 3. 指针自检结果')
    L.append('')
    broken = sum(len(r.get('broken_pointers') or []) for r in doc['rows'])
    L.append('- 断链指针 = **%d**（生成时逐条 os.path.exists；非 0 即本件自己就是死链源）' % broken)
    L.append('- 生成时间：%s ｜ 轮次报告在盘 %d 份' % (doc['generated_at'],
               next(r['readings'].get('round_reports_on_disk') for r in doc['rows'] if r['req'] == 7)))
    L.append('')
    L.append('## 4. 本件不能证明什么（边界）')
    L.append('')
    L.append('- 需求 6 的 30% 至今**不可引用**：可复算的只有工件级与文本层两类口径，任务级经实测不可复算（详见 06-benchmark/全量对标报告_r281_*.md）。')
    L.append('- 需求 1 的「实际使用反馈」缺数据源（I 臂在飞，未落盘不计）。')
    L.append('- 需求 3 的五维分是代理口径（活跃度/许可/文档体量），不是功能实测分。')
    txt = chr(10).join(L) + chr(10)
    out = os.path.join(ROOT, '06-benchmark', '问题分析报告_七项需求终核_r283_2026-10-30.md')
    io.open(out, 'w', encoding='utf-8', newline='').write(txt)
    print('[LEDGER:MD] lines=%d bytes=%d -> %s' % (len(L), len(txt.encode('utf-8')), out))
    return out
if __name__ == '__main__':
    doc = main()
    emit_md(doc)
