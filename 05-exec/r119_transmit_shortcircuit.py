# -*- coding: utf-8 -*-
r'''r119_transmit_shortcircuit.py -- register transmit proposal #6: short-circuit layer misses belong to eval/.

r118 established failure-layer attribution: of the REAL_MISS items, those whose failure layer is
direct_route returning non-None (DIRECT_SHORT) / NONE (DIRECT_NONE) / unique tag hit (TAG_SHORT)
short-circuit BEFORE the recall layer, so swapping SKILL.md corpus cannot structurally reach them.
r119 re-ran: REAL_MISS 12 -> 8, short-circuit layer still 6 + 1 BGE that even oracle cannot flip.
'''
import glob
import io
import json
import os
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BENCH = os.path.join(ROOT, '06-benchmark')
PROPOSALS = os.path.join(BENCH, 'transmit_proposals.json')


def newest(pattern):
    cands = sorted(glob.glob(os.path.join(BENCH, pattern)))
    return cands[-1] if cands else None


def main():
    la = newest('layer_attr_r*.json')
    if not la:
        print('[TRANSMIT] UNVERIFIED no layer_attr artifact')
        return 2
    with io.open(la, encoding='utf-8') as f:
        d = json.load(f)
    rows = d.get('rows', [])
    short_rows = [r for r in rows
                  if r.get('layer') in ('DIRECT_SHORT', 'DIRECT_NONE', 'TAG_SHORT')]
    unreach_bge = [r for r in rows if r.get('layer') == 'BGE_RECALL'
                   and r.get('oracle') == 'UNREACHABLE_BY_CORPUS']
    if not short_rows and not unreach_bge:
        print('[TRANSMIT] UNVERIFIED short-circuit face empty')
        return 2

    named = []
    for r in short_rows:
        named.append({
            'expected': r['expected'], 'query': r['query'],
            'router_top1': r.get('router_top1'), 'layer': r['layer'],
            'direct_route': r.get('direct_route'),
            'tag_hits_n': r.get('tag_hits_n', 0),
            'oracle': r.get('oracle'),
        })
    for r in unreach_bge:
        named.append({
            'expected': r['expected'], 'query': r['query'],
            'router_top1': r.get('router_top1'), 'layer': r['layer'],
            'oracle': r.get('oracle'),
            'note': 'BGE_RECALL layer but oracle also cannot flip',
        })

    with io.open(PROPOSALS, encoding='utf-8') as f:
        doc = json.load(f)
    existing = set(p.get('pid') for p in doc.get('proposals', []))
    pid = 'route_miss_shortcircuit_layer'
    today = datetime.now().strftime('%Y-%m-%d')
    if pid in existing:
        print('[TRANSMIT] proposal already registered: %s' % pid)
        return 0
    why = ('r118 built failure-layer attribution: REAL_MISS items whose failure layer is '
           'direct_route non-None (DIRECT_SHORT) / NONE (DIRECT_NONE) / unique tag (TAG_SHORT) '
           'short-circuit before recall, so swapping SKILL.md corpus cannot structurally reach them. '
           'r119 re-ran: REAL_MISS 12 to 8, short-circuit layer still 6 plus 1 BGE item that even '
           'oracle cannot flip.')
    prop = {
        'pid': pid,
        'title': 'route miss short-circuit layer belongs to eval/; SKILL.md cannot reach it structurally',
        'target': '焚诀 eval/ (direct_layer.py / direct_map.json / build_skill_tags.py / unified_router.py)',
        'proposed_at': today,
        'keywords': ['direct', 'short-circuit', 'direct_map', 'tag', 'NONE', 'route', 'miss'],
        'why': why,
        'evidence': {
            'layer_attr_source': os.path.relpath(la, ROOT).replace(os.sep, '/'),
            'real_miss_n': d.get('conservation', {}).get('real_miss_n'),
            'layers': d.get('layers'),
            'oracle': d.get('oracle'),
            'items': named,
        },
        'redline': 'repo redline: 焚诀 eval/ read-only; register only, never edit eval files.',
    }
    doc.setdefault('proposals', []).append(prop)
    doc['updated'] = today
    tmp = PROPOSALS + '.tmp'
    with io.open(tmp, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    os.replace(tmp, PROPOSALS)
    with io.open(PROPOSALS, encoding='utf-8') as f:
        back = json.load(f)
    hit = [p for p in back.get('proposals', []) if p.get('pid') == pid]
    print('[TRANSMIT] registered pid=%s | readback hits=%d | total=%d'
          % (pid, len(hit), len(back.get('proposals', []))))
    for n in named:
        print('   %-24s %-13s %s -> %s' % (n['expected'], n['layer'], n['query'][:34], n['router_top1']))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())