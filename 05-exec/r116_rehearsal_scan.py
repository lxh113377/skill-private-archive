# -*- coding: utf-8 -*-
"""r116: 定稿候选的本地侧复核（离线，零网络）——数据源=已入库的 upstream_evidence 快照。

判据与 C1-C6 的对应关系（本件只算**可用本地证据算的**那几条，缺证据的显式写 UNVERIFIED）：
  C1 分支齐全（真 skill 仓）：由 r114 矩阵的严格口径 skill_md_exact_n>0 给出（r226 起；旧字段 skill_md_n 仍并列入产物）
  C2 本地文件齐备：本地 SKILL.md + references 目录（引用可达性的静态前置）
  C3 协议面：本地 license / 上游 license 需人工+网络裁决 => 本件写 UNVERIFIED（不假装算过）
  C4 快照新鲜度：上游快照 last_commit_date 距今 <= 365 天
  C5 上游增量可枚举：本地 vs 快照 diff 的 upstream_only / local_only 行数（供合并窗口评估）
  C6 引用可达：本地 SKILL.md 内 markdown 链接指向的文件是否存在

输出：机读 JSON + 人读摘要。零网络、只读本地，不改任何 skill 文件。
"""
import json, io, os, re, sys, base64, hashlib, difflib
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GS = r'D:\global_skills'
BENCH = os.path.join(ROOT, '06-benchmark')
EVID = os.path.join(BENCH, 'upstream_evidence')
LEDGER = os.path.join(BENCH, 'swap_gate_r112_2026-10-18d.json')
MATRIX = os.path.join(BENCH, 'replacement_matrix_r114_2026-10-18.json')

# r116 定稿：11 件 UPGRADE_REVIEW 全量进入复核；分组只影响叙述，不影响是否被算
GROUPS = {
    'A-快照过季待刷新': ['shadcn', 'frontend-slides', 'github', 'react-best-practices'],
    'B-本地已领先': ['test-driven-development'],
    'C-增量微小': ['defuddle', 'web-design-guidelines', 'hyperframes-registry'],
    'D-本地化重写': ['healthcare-cdss-patterns', 'healthcare-emr-patterns', 'healthcare-eval-harness'],
}

MD_LINK = re.compile(r'\[[^\]]*\]\(([^)#\s]+)(?:#[^)]*)?\)')


def load_json(p):
    return json.load(io.open(p, encoding='utf-8'))


def ev_path(slug, repo):
    return os.path.join(EVID, repo.replace('/', '_') + '__' + slug + '.json')


def md_links(text):
    return [m.group(1) for m in MD_LINK.finditer(text)]


def main():
    led = load_json(LEDGER)
    rows = {r['slug']: r for r in led['rows']}
    matrix = load_json(MATRIX)
    mrows = {r['slug']: r for r in matrix['rows']}
    now = datetime.now(timezone.utc)
    out_rows = []
    for group, slugs in GROUPS.items():
        for slug in slugs:
            r = rows.get(slug) or {}
            mr = mrows.get(slug) or {}
            lp = os.path.join(GS, slug, 'SKILL.md')
            rec = {'slug': slug, 'group': group, 'verdict': r.get('verdict'),
                   'upstream_repo': r.get('upstream_repo'),
                   'upstream_path': r.get('upstream_path')}
            rec['local_exists'] = os.path.exists(lp)
            if not rec['local_exists']:
                rec['status'] = 'LOCAL_MISSING'
                out_rows.append(rec)
                continue
            raw = open(lp, 'rb').read()
            txt = raw.decode('utf-8-sig')
            rec['local_sha256'] = hashlib.sha256(raw).hexdigest()
            rec['local_bytes'] = len(raw)
            # C1 真 skill 仓（矩阵 skill_md_exact_n>0；r226 起严格口径，旧件缺 exact 时回退 skill_md_n）
            cands = [c for c in (mr.get('candidates') or []) if c.get('repo') == r.get('upstream_repo')]
            _e = cands[0].get('skill_md_exact_n') if cands else None
            _v = _e if _e is not None else (cands[0].get('skill_md_n') if cands else None)
            rec['c1_skill_repo'] = bool(cands and (_v or 0) > 0) if cands else None
            rec['c1_caliber'] = ('strict' if _e is not None else 'legacy_fallback') if cands else None
            # 快照
            p = ev_path(slug, r.get('upstream_repo') or '')
            rec['evidence_path'] = os.path.relpath(p, ROOT) if os.path.exists(p) else None
            if not os.path.exists(p):
                rec['status'] = 'NO_EVIDENCE'
                out_rows.append(rec)
                continue
            ev = load_json(p)
            if not ev.get('ok'):
                rec['status'] = 'EVIDENCE_UNVERIFIED'
                out_rows.append(rec)
                continue
            up = base64.b64decode(ev['content_b64']).decode('utf-8', 'replace')
            rec['upstream_sha256'] = ev.get('sha256')
            rec['upstream_bytes'] = len(up.encode('utf-8'))
            rec['upstream_last_commit_date'] = (ev.get('last_commit_date') or '')[:10]
            # C4 新鲜度 <= 365 天
            try:
                d = datetime.strptime(rec['upstream_last_commit_date'], '%Y-%m-%d').replace(tzinfo=timezone.utc)
                rec['c4_snapshot_age_days'] = (now - d).days
                rec['c4_fresh_365d'] = (now - d).days <= 365
            except Exception:
                rec['c4_snapshot_age_days'] = None
                rec['c4_fresh_365d'] = None
            # C5 行级增量
            ll, ul = txt.splitlines(), up.splitlines()
            sm = difflib.SequenceMatcher(None, ll, ul)
            up_only, lo_only = [], []
            for tag, i1, i2, j1, j2 in sm.get_opcodes():
                if tag in ('replace', 'insert'):
                    up_only.extend(ul[j1:j2])
                if tag in ('replace', 'delete'):
                    lo_only.extend(ll[i1:i2])
            rec['c5_upstream_only_lines'] = len(up_only)
            rec['c5_local_only_lines'] = len(lo_only)
            rec['c5_upstream_only_sample'] = [x[:110] for x in up_only[:6]]
            # C6 引用可达（只查本地相对路径链接，不查 http）
            links = [l for l in md_links(txt) if not l.startswith(('http://', 'https://', 'mailto:'))]
            miss = [l for l in links if not os.path.exists(os.path.join(GS, slug, l))]
            rec['c6_local_links_n'] = len(links)
            rec['c6_missing_links'] = miss[:8]
            rec['c6_ok'] = not miss
            rec['status'] = 'MEASURED'
            out_rows.append(rec)
    doc = {
        'schema': 'rehearsal-r116-v1',
        'generated_at': now.isoformat(timespec='seconds'),
        'ruler': {
            'C1': '真 skill 仓（r114 矩阵 skill_md_exact_n>0）',
            'C2': '本地文件齐备（SKILL.md 存在）',
            'C3': 'license 合规 —— UNVERIFIED（需网络+人工，本件不假装算过）',
            'C4': '上游快照 last_commit_date 距今 <= 365 天',
            'C5': '行级增量可枚举（upstream_only / local_only）',
            'C6': '本地相对链接可达（缺则列出）',
        },
        'face': {'n': len(out_rows), 'measured': sum(1 for x in out_rows if x['status'] == 'MEASURED')},
        'rows': out_rows,
    }
    out_p = os.path.join(BENCH, 'rehearsal_r116_2026-10-18.json')
    io.open(out_p, 'w', encoding='utf-8', newline='\n').write(json.dumps(doc, ensure_ascii=False, indent=1))
    print('JSON -> %s' % out_p)
    for x in out_rows:
        if x['status'] != 'MEASURED':
            print('  %-26s %s' % (x['slug'], x['status']))
            continue
        print('  %-26s age=%-4s fresh=%s up_only=%-3s local_only=%-3s links=%-2s linkok=%s c1=%s' % (
            x['slug'], x['c4_snapshot_age_days'], x['c4_fresh_365d'],
            x['c5_upstream_only_lines'], x['c5_local_only_lines'],
            x['c6_local_links_n'], x['c6_ok'], x['c1_skill_repo']))
    print('[REHEARSAL] measured=%d/%d' % (doc['face']['measured'], doc['face']['n']))
    return 0


if __name__ == '__main__':
    sys.exit(main())
