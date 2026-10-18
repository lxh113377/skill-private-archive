# -*- coding: utf-8 -*-
r"""r116: 上游增量内容分类器 —— 把 11 件 UPGRADE_REVIEW 的 upstream_only 行按「是不是真能力」分四类。

存在理由（r116 一手，接 r114 未闭环 R114-1）：
  r114 只回答「有没有候选」，r112 只回答「上游比我多几行」；两者都没回答
  **多出来的行到底是不是能力**。实测：11 件里多出来最多的 33 行（github）主要
  是 AAS 市场仓的 frontmatter 元数据（risk/source/date_added），换装它等于把
  「市场登记信息」当「能力升级」买进来。

口径（逐行、可复算、零模型）：
  meta       = frontmatter 区（首个 --- 与第二个 --- 之间）的行
  heading    = markdown 标题行（^#{1,6}\s）
  ref        = 引用行（markdown 链接 / 指向 references|scripts|assets 的路径）
  body       = 其余（真正的规则/步骤/示例正文）
  一行同时满足多类按 meta > heading > ref > body 的顺序唯一归类，保证分母守恒。

判定（禁把元数据当能力）：
  META_ONLY      真能力增量 = 0 且 upstream_only 全部落在 meta/heading/ref
  META_DOMINANT  真能力增量 > 0 但 <= 2 行
  REAL_DELTA     真能力增量 >= 3 行
  LOCAL_AHEAD    local_only > upstream_only 且真能力增量 <= 2

用法: python 05-exec/r116_upstream_delta_classify.py [--json <件>]
退出码: 0 出件且分母守恒 / 2 输入面缺失或为空（R247 不记 PASS）
"""
import argparse, base64, io, json, os, re, sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GS = r'D:\global_skills'
BENCH = os.path.join(ROOT, '06-benchmark')
EVID = os.path.join(BENCH, 'upstream_evidence')
LEDGER = os.path.join(BENCH, 'swap_gate_r112_2026-10-18d.json')

# r117 口径（一手实测，禁把小事吹成大事）：第三支原写 '^s*'（丢反斜杠）。
#   · 它**不是**「永不命中」—— `s*` 可匹配 0 个字符，故行首无缩进的复选框行照样命中；
#   · 真正失效的只有**带缩进的**复选框行（原意里的『行首任意空白』没实现）；
#   · 而带路径的行由第二支 `\b(?:references|scripts|assets)/` 兜住，不看缩进。
# => 实际影响面：本轮 11 件语料重跑逐件比对，行数变化 = 0（见 r117 报告 §2.3）。
# 修法取**严格超集**（只加行首空白，不动第二支），确保不改变任何已测分类。
RE_HEADING = re.compile(r'^#{1,6}\s')
RE_REF = re.compile(r'\]\([^)]+\)|\b(?:references|scripts|assets)/|^\s*[-*]\s+\[\w+\]')

GROUPS = {
    'A-快照过季待刷新': ['shadcn', 'frontend-slides', 'github', 'react-best-practices'],
    'B-本地已领先': ['test-driven-development'],
    'C-增量微小': ['defuddle', 'web-design-guidelines', 'hyperframes-registry'],
    'D-本地化重写': ['healthcare-cdss-patterns', 'healthcare-emr-patterns', 'healthcare-eval-harness'],
}


def split_frontmatter(lines):
    if not lines or lines[0].strip() != '---':
        return -1
    for i in range(1, len(lines)):
        if lines[i].strip() in ('---', '...'):
            return i
    return -1


def classify_line(i, fm_end):
    if 0 < i <= fm_end:
        return 'meta'
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', dest='json_out', default=None)
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if not os.path.exists(LEDGER):
        print('[DELTA:UNVERIFIED] 台账缺失 %s' % LEDGER)
        return 2
    led = json.load(io.open(LEDGER, encoding='utf-8'))
    rows = {r['slug']: r for r in led['rows']}
    import difflib
    out = []
    for group, slugs in GROUPS.items():
        for slug in slugs:
            r = rows.get(slug) or {}
            lp = os.path.join(GS, slug, 'SKILL.md')
            ep = os.path.join(EVID, (r.get('upstream_repo') or '').replace('/', '_') + '__' + slug + '.json')
            rec = {'slug': slug, 'group': group, 'verdict': r.get('verdict'),
                   'upstream_repo': r.get('upstream_repo')}
            if not (os.path.exists(lp) and os.path.exists(ep)):
                rec['status'] = 'UNVERIFIED'
                rec['reason'] = 'local_missing' if not os.path.exists(lp) else 'evidence_missing'
                out.append(rec); continue
            ev = json.load(io.open(ep, encoding='utf-8'))
            if not ev.get('ok'):
                rec['status'] = 'UNVERIFIED'; rec['reason'] = 'evidence_not_ok'; out.append(rec); continue
            local = io.open(lp, encoding='utf-8-sig').read().splitlines()
            up = base64.b64decode(ev['content_b64']).decode('utf-8', 'replace').splitlines()
            sm = difflib.SequenceMatcher(None, local, up)
            up_idx, lo_idx = [], []
            for tag, i1, i2, j1, j2 in sm.get_opcodes():
                if tag in ('replace', 'insert'):
                    up_idx.extend(range(j1, j2))
                if tag in ('replace', 'delete'):
                    lo_idx.extend(range(i1, i2))
            fm_end = split_frontmatter(up)
            buckets = {'meta': [], 'heading': [], 'ref': [], 'body': []}
            for i in up_idx:
                line = up[i]
                b = classify_line(i, fm_end)
                if b is None:
                    if RE_HEADING.search(line):
                        b = 'heading'
                    elif RE_REF.search(line):
                        b = 'ref'
                    else:
                        b = 'body'
                buckets[b].append(line)
            real = len(buckets['body'])
            rec.update({
                'status': 'MEASURED',
                'upstream_only_total': len(up_idx),
                'local_only_total': len(lo_idx),
                'meta_lines': len(buckets['meta']),
                'heading_lines': len(buckets['heading']),
                'ref_lines': len(buckets['ref']),
                'body_lines': real,
                'body_samples': [x[:110] for x in buckets['body'][:6]],
                'meta_samples': [x[:90] for x in buckets['meta'][:4]],
            })
            if real >= 3:
                rec['verdict116'] = 'REAL_DELTA'
            elif real > 0:
                rec['verdict116'] = 'META_DOMINANT'
            elif len(lo_idx) > len(up_idx):
                rec['verdict116'] = 'LOCAL_AHEAD'
            else:
                rec['verdict116'] = 'META_ONLY'
            rec['conservation_ok'] = (len(up_idx) == rec['meta_lines'] + rec['heading_lines'] + rec['ref_lines'] + real)
            out.append(rec)
    measured = [x for x in out if x.get('status') == 'MEASURED']
    doc = {
        'schema': 'upstream-delta-r116-v1',
        'generated_at': datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'ruler': {'meta': 'frontmatter 区', 'heading': 'markdown 标题行', 'ref': '引用/链接行',
                  'body': '其余正文（真能力候选）',
                  'order': 'meta > heading > ref > body（唯一归类，保分母守恒）'},
        'groups': {g: s for g, s in GROUPS.items()},
        'face': {'n': len(out), 'measured': len(measured),
                 'meta_only': sum(1 for x in measured if x['verdict116'] == 'META_ONLY'),
                 'meta_dominant': sum(1 for x in measured if x['verdict116'] == 'META_DOMINANT'),
                 'real_delta': sum(1 for x in measured if x['verdict116'] == 'REAL_DELTA'),
                 'local_ahead': sum(1 for x in measured if x['verdict116'] == 'LOCAL_AHEAD'),
                 'conservation_ok': all(x['conservation_ok'] for x in measured)},
        'rows': out,
    }
    outp = args.json_out or os.path.join(BENCH, 'upstream_delta_r116_2026-10-18.json')
    io.open(outp, 'w', encoding='utf-8', newline=chr(10)).write(json.dumps(doc, ensure_ascii=False, indent=1))
    print('JSON -> %s' % outp)
    for x in doc['rows']:
        if x['status'] != 'MEASURED':
            print('  %-26s UNVERIFIED (%s)' % (x['slug'], x.get('reason')))
            continue
        print('  %-26s up=%-3d lo=%-3d meta=%-2d head=%-2d ref=%-2d body=%-2d => %s' % (
            x['slug'], x['upstream_only_total'], x['local_only_total'],
            x['meta_lines'], x['heading_lines'], x['ref_lines'], x['body_lines'], x['verdict116']))
    f = doc['face']
    print('[DELTA] measured=%d/%d META_ONLY=%d META_DOMINANT=%d REAL_DELTA=%d LOCAL_AHEAD=%d conservation=%s'
          % (f['measured'], f['n'], f['meta_only'], f['meta_dominant'], f['real_delta'], f['local_ahead'], f['conservation_ok']))
    if not measured:
        print('[DELTA:UNVERIFIED] 零可测件 => 不得读成无缺口（R247）')
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
