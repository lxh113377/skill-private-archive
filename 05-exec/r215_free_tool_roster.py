# -*- coding: utf-8 -*-
'''r215_free_tool_roster.py - 免费工具 x 工作流 x skill 搭配名册（生成器，r215）。

为什么需要它：目标要的是把免费工具与工作流、相关 skill 合理搭配。五道门各量一个切面
（163 能不能跑 / 93 有没有 skill 承载 / 92 入口会不会派到写着答案的卷 / 88 召回 / 86 指针），
但没有任何产物把三者按工具拼在一起 —— 于是『某个工具搭到哪一步、还差什么、凭什么说差』只能
靠我在对话里临时回忆。本件把那份回忆变成可复算产物，且全部数字取自源证据件：缺任一源件即 rc=2
不出册（r214 我刚因按印象写分母产出过一条假发现，故此处禁手抄、禁按记忆补，R247）。
'''
import argparse
import glob
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
B = os.path.join(ROOT, '06-benchmark')
sys.path.insert(0, HERE)
import r214_tool_carrier_face as TF
import r215_claim_check as CC
import r215_gate_check as GC

SRC = {
    'roster': 'free_tools_latest.json',
    'patterns': 'tool_carrier_patterns.json',
    # 两把尺的权威源 = 第 67 门产物（per_tool 提到 / per_tool_exec 代码真调用）。
    # r216 自抓：我 r214 造的 tool_skill_matrix_probe 是它的弱化重造（只有「提到」一尺），
    # 故本件不再读自己那份 probe —— 避免第二真相源；按 glob 取最新且含 per_tool_exec 的 67 产物。
    'matrix*': 'tool_skill_matrix_r*.json',
    'truth': 'route_truth_latest.json',
    'ingress': 'ingress_latest.json',
    'recall': 'recall_latest.json',
    'carrier': 'tool_carrier_latest.json',
}

# 任务 -> 工具：从既有名册读，不另立第二份清单
TASK2TOOL = {
    'Pages 部署': 'Cloudflare-Pages',
    'D1 查额度': 'Cloudflare-D1',
    'R2 开桶': 'Cloudflare-R2',
    'Workers 调用量': 'Cloudflare-Workers',
    'Turnstile': 'Cloudflare-Turnstile',
    'Actions 分钟': 'GitHub',
    'CI 红了': 'GitHub',
    '钩子静默推送': 'GitHub',
    'Resend 发邮': 'Resend',
    'Upstash 限流': 'Upstash-Redis',
}

# 触点只写「已经在用的」，不写「打算怎么用」；缺证据的不填
TOUCH = {
    'GitHub': 'A-project-handoff 的 git_autopush 钩子模板（本仓 post-commit 即其落地）+ 第 87 门读 autopush 末行 rc；私有仓分钟用满是已付代价',
    'Cloudflare-D1': 'A-memory-start 的 quickref 额度专章（r196_quota_face 现读行数/写入）+ chaoshi-web-deploy 的 d1 execute 部署链',
    'Cloudflare-Pages': 'chaoshi-web-deploy 部署权威入口（direct_map 10 pattern，任务话术直连命中）',
    'Cloudflare-Workers': 'A-memory-start 的 quickref 额度专章（r199_workers_face 现读调用数）；跨 zone 聚合分母差异已写 §9.16',
    'Cloudflare-R2': 'chaoshi-image-optimization 的 R2 外置专章（干跑读数 + 阻断现状）',
    'Cloudflare-Turnstile': 'r163_turnstile_face 与 r163_turnstile_admin 曾全链接通，后按老大要求移除 = 决定而非待搭缺口',
    'SQLite': 'r203_ledger_index 用 SQLite 做门禁台账派生索引（读面与盲区均实测）',
    'VS Code': 'r163_free_tools_face 的 probe_vscode（which + 非 0 字节 + 真跑 --version）',
    'Resend': 'r163_tool_skill_matrix 已把它列入零引用核查面；仅 HTTP API 无 CLI，凭据缺 ⇒ 尚未接入任何工作流',
    'Upstash-Redis': 'r163_tool_skill_matrix 报其零引用（唯一 ADVISORY 项）；仅 REST 无 CLI，凭据缺 ⇒ 未接入',
}

GATES = {
    'GitHub': '163 + 87 + 93',
    'Cloudflare-D1': '163 + 88 任务层 + 93',
    'Cloudflare-Pages': '163 + 92 + 93',
    'Cloudflare-Workers': '163 + 88 任务层 + 93',
    'Cloudflare-R2': '163 + 88 任务层 + 93',
    'Cloudflare-Turnstile': '163 + 88 任务层(DISPUTED) + 93',
    'SQLite': '163 + 85 + 93',
    'VS Code': '163 + 93',
    'Resend': '163 + 93',
    'Upstash-Redis': '163 + 93',
}


def load(n):
    """n 含 * 时按 mtime 取最新一份（且必须是第 67 门产物：含 per_tool_exec）。

    返回 (数据, 实际文件名)。取不到返回 (None, n) —— 调用方据此 UNVERIFIED，
    不得退回去读我那份弱化 probe（第二真相源）。
    """
    def one(f):
        q = os.path.join(B, f)
        if not os.path.isfile(q):
            return None
        try:
            return json.load(io.open(q, encoding='utf-8'))
        except (OSError, ValueError):
            return None
    if '*' in n:
        fs = [f for f in sorted(glob.glob(os.path.join(B, n)), key=os.path.getmtime)
              if 'probe' not in os.path.basename(f)]
        for f in reversed(fs):
            v = one(os.path.basename(f))
            if isinstance(v, dict) and v.get('per_tool_exec') is not None:
                return v, os.path.basename(f)
        return None, n
    return one(n), n


def build():
    src = {}
    used = {}
    for k, fn in SRC.items():
        v, real = load(fn)
        if v is None:
            return None, '源件缺失或不可析：' + fn
        src[k.rstrip('*')] = v
        used[k.rstrip('*')] = real
    pat_map = {k.lower(): v for k, v in (src['patterns'].get('patterns') or {}).items()}
    skills = CC.all_skills()
    rows = src['roster'].get('rows') or []
    if not rows:
        return None, '名册 rows 为空 = 空面不得出册（R247）'
    # 两把尺直接用第 67 门产物（工具名两边一致，无需映射）；probe 那份已停读
    per_t = src['matrix'].get('per_tool') or {}
    per_e = src['matrix'].get('per_tool_exec') or {}
    tasks = src['truth'].get('tasks') or []
    items = []
    for r in rows:
        tool = r.get('tool')
        in67 = tool in per_t or tool in per_e
        linked = []
        for x in tasks:
            want = x.get('want')
            tk = x.get('task')
            if want and TASK2TOOL.get(tk) == tool:
                linked.append({'task': tk, 'outcome': x.get('outcome'),
                               'top1': x.get('top1'), 'skill': want})
        items.append({
            'tool': tool,
            'state': r.get('state'),
            # 两把尺（第 67 门口径）：提到 = 文档或代码出现该工具；可执行 = 代码真调用。
            # 关键：工具不在第 67 门名册时记 None，不记 0 —— 0 会把「它没被这道门量」
            # 冒充成「零提到」（R216-2 那处集合差正是此形，VS Code 就命中这一支）。
            'mention_skills': (sorted(per_t.get(tool)) if tool in per_t else None),
            'exec_skills': (sorted(per_e.get(tool)) if tool in per_e else None),
            'yardstick_absent': tool not in per_t and tool not in per_e,
            'gates': GATES.get(tool, ''),
            'touchpoint': TOUCH.get(tool, ''),
            'claims': (CC.claims_for(TOUCH.get(tool, ''),
                            pat_map.get(TF.norm(tool)) or [], skills)
                       + GC.claims_for(TOUCH.get(tool, ''),
                                         pat_map.get(TF.norm(tool)) or [])),
            'patterns_n': len(pat_map.get(TF.norm(tool)) or []),
            'tasks': linked,
        })
    c = src['carrier']
    i = src['ingress']
    rc = src['recall']
    gates = {
        'carrier': {'tools': c.get('tools'), 'vols': c.get('vols'),
                    'uncarried': len(c.get('gaps') or []), 'k5': c.get('k5_teeth')},
        'ingress': {'checked': i.get('checked'), 'gaps': len(i.get('gaps') or []),
                    'k5': i.get('k5')},
        'recall': {'window': rc.get('checked'), 'truth': rc.get('truth_judged'),
                   'task': rc.get('task_judged'), 'hits': rc.get('task_hits'),
                   'gaps': len(rc.get('gaps') or [])},
        # 两把尺的出处随读数一起落盘：源件名 + 该件生成时间 ⇒ 陈旧可见，不静默沿用旧矩阵
        'matrix_src': {'file': used.get('matrix'),
                       'generated_at': src['matrix'].get('generated_at'),
                       'cmd': src['matrix'].get('cmd')},
    }
    return {'items': items, 'gates_reading': gates}, None


def render_md(doc):
    L = []
    L.append('# 免费工具 x 工作流 x skill 搭配名册（生成物，勿手改）')
    L.append('')
    L.append('生成命令：python 05-exec/r215_free_tool_roster.py --json <件>')
    L.append('')
    g = doc['gates_reading']
    L.append('## 依据面（五道判据当前读数）')
    L.append('')
    L.append('| 判据 | 量什么 | 读数 |')
    L.append('|---|---|---|')
    L.append('| 163 | 工具在本机能不能跑 | 名册 %d 项 |' % len(doc['items']))
    L.append('| 93 | 每个工具是否至少被一个 skill 承载 | 工具 %s / 扫描 %s 卷 / 未承载 %s |' % (
        g['carrier']['tools'], g['carrier']['vols'], g['carrier']['uncarried']))
    L.append('| 92 | 每轮入口会不会把话术派到写着答案的卷 | 判 %s / 缺口 %s |' % (
        g['ingress']['checked'], g['ingress']['gaps']))
    L.append('> 依据面取值：163 见 free_tools_latest.json；93 见 tool_carrier_latest.json 与 '
             'tool_skill_matrix_probe.json；92 见 ingress_latest.json；88 见 recall_latest.json '
             '与 route_truth_latest.json。再生命令见文件头。')

    L.append('| 88 | 窗口 / BGE 真值 / 任务语句三层 | 窗口 %s、真值 %s、任务 %s 命中 %s、缺口 %s |' % (
        g['recall']['window'], g['recall']['truth'], g['recall']['task'],
        g['recall']['hits'], g['recall']['gaps']))
    L.append('')
    L.append('## 逐工具搭配态')
    L.append('')
    for it in doc['items']:
        L.append('### %s - %s' % (it['tool'], it['state']))
        L.append('')
        ms, es = it['mention_skills'], it['exec_skills']
        if it.get('yardstick_absent'):
            L.append('- 两把尺：该工具不在第 67 门名册内 = 未被量（None，不等于 0）')
        else:
            L.append('- 两把尺：提到 %d 件 ｜ 代码真调用 %d 件' % (len(ms or []), len(es or [])))
            L.append('    提到 = %s' % (', '.join(ms or []) or '无'))
            L.append('    可执行 = %s' % (', '.join(es or []) or '无'))
        L.append('    （取值：%s 的 per_tool / per_tool_exec[%s]；该件 generated_at=%s）' % (
            doc['gates_reading']['matrix_src'].get('file'), it['tool'],
            doc['gates_reading']['matrix_src'].get('generated_at')))
        L.append('- 守它的判据：' + it['gates'])
        L.append('- 工作流触点：' + it['touchpoint'])
        cs = it.get('claims') or []
        if cs:
            for c in cs:
                who = c.get('skill') or (str(c.get('gate_file')) + '（判据件）')
                L.append('- 触点在位核验（在位≠已接入）：%s -> %s' % (who, c['verdict']))
        else:
            L.append('- 触点在位核验（在位≠已接入）：本行未点名可核对象（勿当已核）')
        ts = it['tasks'] or []
        if ts:
            L.append('- 任务语句实测：')
            for x in ts:
                L.append('    - %s -> %s（top1=%s，期望件=%s）' % (
                    x['task'], x['outcome'], x['top1'], x['skill']))
        else:
            L.append('- 任务语句实测：名册无对应条目（不编造）')
        L.append('')
    return L


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', dest='out',
                    default='06-benchmark/free_tool_roster_latest.json')
    ap.add_argument('--md', dest='md',
                    default='06-benchmark/free_tool_roster_latest.md')
    args = ap.parse_args(argv)
    doc, err = build()
    if doc is None:
        print('[ROSTER:UNVERIFIED] ' + str(err) + ' = 不出册（R247 禁按旧记忆补面）')
        return 2
    NL = chr(10)
    op = args.out if os.path.isabs(args.out) else os.path.join(ROOT, args.out)
    mp = args.md if os.path.isabs(args.md) else os.path.join(ROOT, args.md)
    io.open(op, 'w', encoding='utf-8', newline=NL).write(json.dumps(
        {'schema': 'free-tool-roster-v1', 'readonly': True,
         'provenance_cmd': 'python 05-exec/r215_free_tool_roster.py --json <件>',
         **doc}, ensure_ascii=False, indent=1))
    txt = NL.join(render_md(doc)) + NL
    assert chr(13) not in txt, 'introduced CR'
    io.open(mp, 'w', encoding='utf-8', newline=NL).write(txt)
    print('[ROSTER:OK] %d 工具入册；未承载 %s；md %dB' % (
          len(doc['items']), doc['gates_reading']['carrier']['uncarried'],
          len(txt.encode('utf-8'))))
    return 0


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
    sys.exit(main())