# -*- coding: utf-8 -*-
'''r289_usage_coverage.py - 需求 1 的使用反馈第一次变成结论（不只是有表）。

为什么要单独算：r288 回填出 3110 行 / 47 个 skill，但 47 对 190 是覆盖率还是采样偏差，决定需求 2/4
的优先级能不能引用它。未使用不等于低价值（可能是新装件），用过也不等于高价值（可能只过一次）。
两侧都现读，并与三通道分层交叉（单独一边都不成立）。

口径：在册 = 受管根含 SKILL.md 的目录（现读，不抄硬编码数）；用过 = 出现在 skill_usage.jsonl 的
skill 字段（回填行 outcome=unknown 也算用过）；分层 = r275_three_channel_intersection 的 rows[].layer，
该件只覆盖有 .upstream 侧车的 55 件，分母与在册不同 ⇒ 交集才是可行动集。

两个分母都合法，必须并报（我第一版把它写成矩阵把镜像算进来了，那是我越权断言：红线 2 只规定
镜像只读，没说它不算目录）：dirs_total 194 / 含 SKILL.md 191 / 本面口径 190（排 _ 前缀）/ 矩阵面 191。
'''
import io
import json
import os
import time

SK = 'D:/global_skills'
TBL = 'D:/global_memory/meta/skill_usage.jsonl'
TIER = '06-benchmark/r275_three_channel_intersection.json'
OUT = '06-benchmark/r289_usage_coverage.json'


def registered():
    dirs = [n for n in sorted(os.listdir(SK)) if os.path.isdir(os.path.join(SK, n))]
    with_md = [n for n in dirs if os.path.isfile(os.path.join(SK, n, 'SKILL.md'))]
    face = [n for n in with_md if not n.startswith(('_', '.'))]
    # 第三个返回值给集合本身而不是 len：下面要用它算差异名，返回 int 会让调用方无法核对
    return set(face), dirs, with_md


def used_counts():
    counts = {}
    real = set()
    for ln in io.open(TBL, encoding='utf-8').read().splitlines():
        ln = ln.strip()
        if not ln:
            continue
        j = json.loads(ln)
        s = j.get('skill')
        if not s:
            continue
        counts[s] = counts.get(s, 0) + 1
        if j.get('outcome') and j.get('outcome') != 'unknown':
            real.add(s)
    return counts, real


def main():
    reg, dirs, with_md = registered()
    counts, real = used_counts()
    used_in_reg = dict((s, c) for s, c in counts.items() if s in reg)
    never = sorted(reg - set(counts))
    ghost = sorted(set(counts) - reg)
    tiers = {}
    if os.path.isfile(TIER):
        d = json.load(io.open(TIER, encoding='utf-8'))
        # 真字段名（现读得到，不是猜）：行键 skill、分层字段 layer
        for r in d.get('rows') or []:
            tiers[r.get('skill')] = r.get('layer')
    tsum = {}
    for slug, t in sorted(tiers.items()):
        tsum[t] = tsum.get(t, 0) + 1
    actionable = sorted([s for s in used_in_reg if s in tiers])
    top = sorted(((c, s) for s, c in used_in_reg.items()), reverse=True)[:10]
    doc = {}
    doc['schema'] = 'usage-coverage-v1'
    doc['generated_at'] = time.strftime('%Y-%m-%d %H:%M')
    doc['provenance_cmd'] = 'python 05-exec/r289_usage_coverage.py'
    doc['registered_skills'] = len(reg)
    doc['skills_seen_in_table'] = len(counts)
    doc['skills_in_registry_and_used'] = len(used_in_reg)
    doc['coverage_pct'] = round(100.0 * len(used_in_reg) / max(1, len(reg)), 2)
    doc['never_seen_n'] = len(never)
    # never_seen 必须给全量而不是样本：交叉计算（需求4 优先级池 x 使用面）若用截断样本，
    # 分母就是 12 而不是 143，任何命中率都失真。样本字段只留给人读，并改名标清样本量。
    doc['never_seen_all'] = never
    doc['never_seen_sample12'] = never[:12]
    doc['table_names_not_registered'] = ghost
    doc['rows_total'] = sum(counts.values())
    doc['top_used'] = top
    doc['skills_with_real_outcome'] = sorted(real)
    doc['tier_face_rows'] = len(tiers)
    doc['tier_distribution'] = tsum
    doc['actionable_both_axes'] = actionable
    doc['reading_rule'] = 'never_seen is not evidence of low value; it bounds what is judgeable, not rank'
    doc['denominators'] = {'dirs_total': len(dirs), 'dirs_with_skill_md': len(with_md),
                           'face_here_excl_underscore': len(reg),
                           'diff_named': sorted(set(with_md) - reg)}
    doc['denominator_note'] = ('all denominators are legitimate and reported side by side: this face excludes '
                              'underscore dirs because _my-skills is the read-only mirror (red line 2), while '
                              'the matrix face counts it; 194 dirs total, 191 carry a SKILL.md')
    tmp = OUT + '.tmp'
    io.open(tmp, 'w', encoding='utf-8', newline='').write(json.dumps(doc, ensure_ascii=False, indent=1))
    os.replace(tmp, OUT)
    print('[USAGE:COVERAGE] registry=%d used=%d coverage=%.2f%% never=%d ghost=%d tiers=%d actionable=%d' % (
          len(reg), len(used_in_reg), doc['coverage_pct'], len(never), len(ghost), len(tiers), len(actionable)))
    print('   denominators:', doc['denominators'])
    print('   top:', ', '.join('%s(%d)' % (s, c) for c, s in top[:6]))
    print('   real-outcome skills:', sorted(real), '| tiers:', tsum)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
