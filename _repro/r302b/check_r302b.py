# -*- coding: utf-8 -*-
r'''r302b checker — 守恒 + 全序稳定性（同一输入连跑两次）。

判据末行固定：
[R302:PRIORITY] pairs=49 t1=<n> t2=<n> t3=<n> unknown=<n> invalid=13 sampled_sha=12 stable=<True|False>
stable 的定义：同一输入连跑两次，两次排名（slug, repo, rank）序列完全一致，且与已落盘件一致。
'''
import io, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_r302b as B


def main():
    rows1, order1 = B.build_rows()
    rows2, order2 = B.build_rows()
    seq1 = [(r['slug'], r['repo'], r['rank']) for r in order1]
    seq2 = [(r['slug'], r['repo'], r['rank']) for r in order2]
    two_runs = (seq1 == seq2)
    doc = json.load(io.open(HERE + '/priority.json', encoding='utf-8'))
    disk = [(r['slug'], r['repo'], r['rank']) for r in sorted(doc['rows'], key=lambda r: r['rank'])]
    same_disk = (disk == seq1)
    stable = bool(two_runs and same_disk)
    tiers = doc['tiers']
    t1 = tiers.get('T1', 0); t2 = tiers.get('T2', 0); t3 = tiers.get('T3', 0); uu = tiers.get('U', 0)
    pairs = len(doc['rows'])
    inv = doc.get('invalid_rows_n', len(doc.get('invalid_rows') or []))
    sha_n = doc.get('samples_sha_n', len(doc.get('samples_sha') or []))
    cons = ((t1 + t2 + t3 + uu) == pairs) and (sum(doc['state_counts'].values()) == pairs)
    checks = ['two_runs_identical=' + str(two_runs),
              'rank_matches_disk=' + str(same_disk),
              'conservation=' + str(bool(cons)),
              'rows_n=' + str(pairs),
              'state_counts_sum=' + str(sum(doc['state_counts'].values())),
              'invalid_n=' + str(inv),
              'samples_sha_n=' + str(sha_n)]
    for c in checks:
        print(c)
    ok = bool(stable and cons and pairs == 49 and inv == 13 and sha_n == 12)
    line = '[R302:PRIORITY] pairs=%d t1=%d t2=%d t3=%d unknown=%d invalid=%d sampled_sha=%d stable=%s' % (
        pairs, t1, t2, t3, uu, inv, sha_n, stable)
    sys.stdout.write(line)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
