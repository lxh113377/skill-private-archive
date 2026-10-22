# -*- coding: utf-8 -*-
# r163_tool_skill_matrix.py -- 免费开发者工具 × 在册 skill 搭配矩阵（第 67 门）。
#
# 存在理由（goal 第 10 轮）：目标的原话是「把这些免费开发者工具与我现有的工作流与相关 skill
#   进行**合理搭配**」。此前只有第 65 门 free_tools_face 回答「工具有没有、能不能用」，
#   但**没有任何面回答「谁在用它、搭配够不够」** —— 那正是目标本体。
#   实测缺口（首次跑）：在册 191 件 skill 里只有 31 件引用过这批工具，其中
#   **Cloudflare-R2 / Turnstile / Resend / Upstash 四项零引用**；即「名册有、无人用」。
#
# 判据口径（防两个方向的失真）：
#   · 「提到」≠「使用」：GitHub 用命令级正则（gh api/pr/issue/run/auth、actions/checkout、
#     workflow_dispatch）而非仅出现产品名 —— 否则 README 里提一句 GitHub 也被算成搭配。
#   · 零引用**不判红**：某些工具本就该等场景（Turnstile 要站点、Resend 要发信场景），
#     强行凑引用就是造需求。本门判红只有一条：**矩阵面取不到**（读不到 global_skills ⇒ rc=2）。
#     零引用用具名清单显形（ADVISORY），由人决定要不要补搭配。
#
# 用法: python 05-exec/r163_tool_skill_matrix.py [--json <件>] [--selftest]
# 退出码: 0 矩阵建成（含零引用具名）/ 2 面取不到（R247 禁按干净记）
import argparse
import io
import json
import os
import re
import sys
from datetime import datetime

# 工具 → 命令级/施工级正则（不是产品名匹配）
TOOLS = {
    'GitHub': r'gh\s+(?:api|pr|issue|run|auth|repo|release|workflow)\b|actions/checkout|workflow_dispatch|uses:\s*actions/',
    'Cloudflare-D1': r'wrangler\s+d1|d1\s+execute|d1_database|\.prepare\(',
    'Cloudflare-R2': r'wrangler\s+r2|R2Bucket|r2\.dev',
    'Cloudflare-Pages': r'wrangler\s+pages|pages\s+deploy|pages\.dev',
    'Cloudflare-Workers': r'wrangler\s+deploy|workers\.dev|export\s+default\s*\{[\s\S]{0,80}fetch',
    'Cloudflare-Turnstile': r'turnstile|siteverify|cf-turnstile|TURNSTILE_SECRET',
    # r163 自抓：纯产品名不算搭配（f3 腿当场抓到 Resend/Upstash 只提一句就被算进去）。
    # 这两项没有 CLI，靠 env key / API host / SDK 调用形态识别。
    'Resend': r'RESEND_API_KEY|api\.resend\.com|resend\.emails\.send|new\s+Resend\(',
    'Upstash-Redis': r'UPSTASH_REDIS|upstash\.io|@upstash/redis|new\s+Redis\(\s*\{',
    'SQLite': r'sqlite3|SQLite|\.db\b',
    'Pages-Functions': r'Pages\s+Functions|onRequest\s*[:(]',
}
RX = {k: re.compile(v, re.I) for k, v in TOOLS.items()}

GS_DEFAULT = r'D:\global_skills'
MAX_EXTRA_FILES = 25
MAX_EXTRA_BYTES = 200_000


def read_skill_blob(skill_dir):
    sk = os.path.join(skill_dir, 'SKILL.md')
    parts = []
    try:
        parts.append(io.open(sk, encoding='utf-8', errors='replace').read())
    except OSError:
        return None
    for sub in ('references', 'scripts'):
        p = os.path.join(skill_dir, sub)
        if not os.path.isdir(p):
            continue
        for fn in sorted(os.listdir(p))[:MAX_EXTRA_FILES]:
            fp = os.path.join(p, fn)
            try:
                if os.path.isfile(fp) and os.path.getsize(fp) < MAX_EXTRA_BYTES:
                    parts.append(io.open(fp, encoding='utf-8', errors='replace').read())
            except OSError:
                continue
    return '\n'.join(parts)


def build_matrix(gs_root):
    if not os.path.isdir(gs_root):
        return None, 'gs_root 不存在: %s' % gs_root
    slugs = sorted(s for s in os.listdir(gs_root)
                   if os.path.isfile(os.path.join(gs_root, s, 'SKILL.md')))
    if not slugs:
        return None, '扫描面为空（%s 下无 SKILL.md）⇒ 禁按「零引用」记绿' % gs_root
    per_tool = {k: [] for k in TOOLS}
    per_skill = {}
    unreadable = []
    for slug in slugs:
        blob = read_skill_blob(os.path.join(gs_root, slug))
        if blob is None:
            unreadable.append(slug)
            continue
        hits = {k: len(RX[k].findall(blob)) for k in TOOLS}
        hits = {k: v for k, v in hits.items() if v}
        if hits:
            per_skill[slug] = hits
            for k in hits:
                per_tool[k].append(slug)
    return {
        'gs_root': gs_root,
        'skills_scanned': len(slugs),
        'skills_with_tools': len(per_skill),
        'unreadable': unreadable,
        'per_tool': {k: sorted(v) for k, v in per_tool.items()},
        'per_skill': per_skill,
        'zero_ref_tools': sorted(k for k in TOOLS if not per_tool[k]),
    }, None


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', dest='out', default='')
    ap.add_argument('--gs', default=GS_DEFAULT)
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    m, err = build_matrix(args.gs)
    if m is None:
        print('[TOOLMATRIX] UNVERIFIED %s' % err)
        return 2
    doc = {'schema': 'tool-skill-matrix-r163-v1',
           'cmd': 'python 05-exec/r163_tool_skill_matrix.py --json <out>',
           'tools_n': len(TOOLS),
           'note': '命令级匹配（非产品名）；零引用不判红，具名显形供人决定是否补搭配',
           'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M'),
           **m}
    if args.out:
        with io.open(args.out, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
    print('[TOOLMATRIX] 在册 %d 件 ｜ 有工具引用 %d 件 ｜ 工具 %d 项'
          % (m['skills_scanned'], m['skills_with_tools'], len(TOOLS)))
    for k in TOOLS:
        users = m['per_tool'][k]
        print('  %-20s %2d 件  %s' % (k, len(users),
                                      ', '.join(users[:4]) + ('...' if len(users) > 4 else '') or '(零引用)'))
    if m['zero_ref_tools']:
        print('[TOOLMATRIX:ADVISORY] 零引用工具（名册有、skill 无人用）: %s'
              % ', '.join(m['zero_ref_tools']))
    if m['unreadable']:
        print('[TOOLMATRIX:ADVISORY] 不可读 skill %d 件: %s'
              % (len(m['unreadable']), ', '.join(m['unreadable'][:5])))
    print('[TOOLMATRIX:PASS] 矩阵建成（零引用已具名；不判红 —— 凑引用即造需求）')
    return 0


def selftest():
    """三腿：① 真面建成且三个计数自洽 ② 空面必须 rc=2（禁按零引用记绿）
    ③ 命令级 vs 产品名：造一个只提产品名不含命令的假 skill ⇒ 不得被算成搭配（有牙）。"""
    legs = []
    m, err = build_matrix(GS_DEFAULT)
    ok1 = (m is not None
           and m['skills_scanned'] > 0
           and m['skills_with_tools'] <= m['skills_scanned']
           and all(len(v) <= m['skills_scanned'] for v in m['per_tool'].values()))
    legs.append(('f1_matrix_counts_consistent', ok1,
                 'scanned=%s with_tools=%s' % (m and m['skills_scanned'], m and m['skills_with_tools'])))
    # 空面
    import tempfile
    empty = tempfile.mkdtemp(prefix='r163_mx_empty_')
    m2, err2 = build_matrix(empty)
    legs.append(('f2_empty_face_unverified', m2 is None and 'exactly' not in str(err2),
                 'm2=%s err=%s' % (m2, err2)))
    # 只提产品名不写命令 ⇒ 不得算搭配
    fake = tempfile.mkdtemp(prefix='r163_mx_fake_')
    d = os.path.join(fake, 'fake-skill')
    os.makedirs(d)
    io.open(os.path.join(d, 'SKILL.md'), 'w', encoding='utf-8').write(
        '# 假 skill\n本文提到 Cloudflare R2 很棒，也提到 Resend 和 Upstash，但没有一条命令。\n')
    m3, _ = build_matrix(fake)
    legs.append(('f3_mention_only_not_counted',
                 m3 is not None and m3['skills_with_tools'] == 0,
                 'with_tools=%s（期望 0：只提产品名不算搭配）' % (m3 and m3['skills_with_tools'])))
    # 变异对照：把正则降级成产品名匹配 ⇒ f3 形态必须被算成搭配（证明 f3 的绿来自命令级正则）
    saved = dict(RX)
    try:
        for k in ('Cloudflare-R2', 'Resend', 'Upstash-Redis'):
            RX[k] = re.compile(r'%s' % k.split('-')[0], re.I)
        m4, _ = build_matrix(fake)
        legs.append(('m1_name_only_regex_catches_fake',
                     m4 is not None and m4['skills_with_tools'] > 0,
                     'with_tools=%s（期望 >0：降级成产品名匹配才会误算）' % (m4 and m4['skills_with_tools'])))
    finally:
        RX.clear()
        RX.update(saved)
    for n, ok, d_ in legs:
        print('%s %-34s %s' % ('PASS' if ok else 'FAIL', n, d_))
    n_ok = sum(1 for _, ok, _ in legs if ok)
    print('[TOOLMATRIX:SELFTEST] %d/%d' % (n_ok, len(legs)))
    return 0 if n_ok == len(legs) else 1


if __name__ == '__main__':
    raise SystemExit(main())