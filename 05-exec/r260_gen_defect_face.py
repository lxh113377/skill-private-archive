# -*- coding: utf-8 -*-
'''r260 需求1（全面盘点）机器面汇总件生成器（只读取证，产物写白名单面）。
所有数字来自本轮（2026-10-28）实跑读数，命令逐条记在 cmds 里以便复跑。'''
import json, io, os, subprocess, datetime, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if False else r'C:\Users\37533\Desktop\workspace\skill焚诀\自建skill优化'
GS = r'D:\global_skills'
scan = json.load(io.open(os.path.join(ROOT, '_temp/r260_scanout/scan_result.json'), encoding='utf-8'))['rows']
link = json.load(io.open(os.path.join(ROOT, '_temp/r260_link_audit.json'), encoding='utf-8'))
scope = json.load(io.open(os.path.join(ROOT, '00-scope/scope_result.json'), encoding='utf-8'))['rows']
conf = {r['skill']: r['conf'] for r in scope}
hm = sorted(k for k, v in conf.items() if v in ('HIGH', 'MID'))
top_dirs = sorted(d for d in os.listdir(GS) if os.path.isdir(os.path.join(GS, d)))
with_skillmd = sorted(d for d in top_dirs if os.path.isfile(os.path.join(GS, d, 'SKILL.md')))
import re
semver = re.compile(r'^\d+\.\d+')
ver = {}
for r in scan:
    raw = io.open(os.path.join(GS, r['skill'], 'SKILL.md'), encoding='utf-8-sig', errors='replace').read(4000)
    m = re.search(r'^version:\s*(.+)$', raw, re.M)
    ver[r['skill']] = (m.group(1).strip() if m else 'MISSING_KEY')
no_ver = sorted(k for k, v in ver.items() if v == 'MISSING_KEY')
nonsemi = sorted(k for k, v in ver.items() if v != 'MISSING_KEY' and not semver.match(v))
over = sorted(((r['size_b'], r['skill']) for r in scan), reverse=True)
out = {
    'schema': 'r260-inventory-defect-face-v1',
    'generated_at': datetime.datetime.now().isoformat(timespec='seconds'),
    'round': 'r260',
    'readonly': True,
    'disk_face': {
        'top_level_dirs': len(top_dirs),
        'dirs_with_skillmd': len(with_skillmd),
        'dirs_without_skillmd': [d for d in top_dirs if d not in set(with_skillmd)],
        'top_level_files': 8,
        'note': 'brief 所称 193 = 2026-10-28 前口径；本轮 ls -1 顶层条目含 8 个文件 ⇒ 目录 192；D:\\global_skills 实测不是 reparse point（fsutil 回 Error 4390）'
    },
    'self_made_scope': {
        'scope_rows_total': len(scope),
        'distribution': dict(collections.Counter(conf.values())),
        'HIGH_MID_N': len(hm),
        'IN_77_NOT_ON_DISK': [],
        'ON_DISK_NOT_IN_77': len(with_skillmd) - len(hm),
        'note_newer_than_freeze': '现行盘有 114 件不在 2026-09-22 冻结 scope 名单内（含 dingtalk-* 12 件等），扫描面 77 条为冻结名册现值，非盘面全量'
    },
    'defect_face_77': {
        'over_4kb': sum(1 for r in scan if r['over_4kb']),
        'size_bands': {'<=4096': sum(1 for s, n in over if s <= 4096), '4-8k': sum(1 for s, n in over if 4096 < s < 8192), '8-16k': sum(1 for s, n in over if 8192 <= s < 16384), '>16k': sum(1 for s, n in over if s >= 16384)},
        'largest_10': [{'skill': n, 'size_b': s} for s, n in over[:10]],
        'no_trigger_words': sum(1 for r in scan if not r['has_trigger_words']),
        'desc_short_lt40': sum(1 for r in scan if r['desc_short']),
        'missing_version_key': len(no_ver),
        'version_non_semver': len(nonsemi),
        'version_non_semver_list': nonsemi,
        'dead_ref_candidates': sum(1 for r in scan if r['dead_refs']),
        'dead_wildcard_candidates': sum(1 for r in scan if r['dead_wildcards']),
        'deprecated_platform_hits': sum(1 for r in scan if r['deprecated_platform_hits'])
    },
    'registry_face': {
        'registry_n': 191, 'disk_n': 191, 'ghosts': 0, 'unregistered': 0, 'version_behind_count': 11,
        'version_behind': [
            {'skill': 'data-analysis', 'registry': '1.2.0', 'disk': '1.4.0'},
            {'skill': 'debugging-fixing', 'registry': '2.14.6', 'disk': '2.14.9'},
            {'skill': 'frontend-slides', 'registry': '1.1.0', 'disk': '1.3.0'},
            {'skill': 'grill-me', 'registry': '1.0.0', 'disk': '1.2.0'},
            {'skill': 'hyperframes', 'registry': '1.4.0', 'disk': '1.7.0'},
            {'skill': 'hyperframes-media', 'registry': '1.5.0', 'disk': '1.7.0'},
            {'skill': 'ppt-master', 'registry': '1.0.0', 'disk': '1.1.0'},
            {'skill': 'story', 'registry': '1.0.0', 'disk': '1.1.0'},
            {'skill': 'story-deslop', 'registry': '1.1.0', 'disk': '1.2.0'},
            {'skill': 'story-setup', 'registry': '1.5.0', 'disk': '1.6.0'},
            {'skill': 'ui-ux-pro-max', 'registry': '1.4.0', 'disk': '1.5.0'}
        ],
        'note': '版本落后 11 件全部不在自建 77 名册内（均为市场/上游或灰区件），自建面版本登记无落后'
    },
    'link_integrity_face': {
        'scanned_md': link['scanned'], 'links': link['links'],
        'HARD': len(link['hard']), 'SOFT': len(link.get('soft', [])),
        'hard_detail': [{'skill': h['skill'], 'file': h['file'], 'line': h['line'], 'cited': h['cited'], 'why': h.get('why', '')} for h in link['hard']],
        'in_scope_77_hard': [h['skill'] for h in link['hard'] if h['skill'] in set(hm)]
    },
    'claim_truth_face': {'candidates': 1, 'detail': 'A-memory-start/SKILL.md:62 端数枚举缺 ds/mm（真值 9 端）'},
    'cmds': {
        'disk_count': "cd /d/global_skills && ls -1d */ | wc -l  => 192",
        # chr(36) 拼美元符：源码里写 \$ 不是合法转义（SyntaxWarning），且 shell 变量必须留在字符串内原样交付。
        'with_skillmd': "for d in */; do [ -f \"" + chr(36) + "d/SKILL.md\" ] && echo; done | wc -l  => 191",
        'quarterly': "python eval/skill_quarterly_inspect.py --skip-live  => registry_drift RED: 在册 191/在盘 191/ghost 0/未注册 0/版本落后 11；link_integrity RED",
        'link_audit': "python eval/skill_link_audit.py --skills-root D:\\global_skills --json  => HARD 6",
        'scan_defect': "python 05-exec/r260_scan_runner.py（import 01-scan/scan_all.py 的 scan() 本体，SCOPE_DIR 指 00-scope、SCAN_DIR 指 _temp）=> 超4KB 70 / 无触发词 55 / 死链 15 / 通配 2 / 弃用名 16",
        'contract': "python 05-exec/baseline_contract_scan.py --json ... => [CONTRACT:PASS] 557 份",
        'roster': "python 05-exec/r237_roster_audit.py --json ... => [ROSTER-AUDIT:FAIL] 漂移 3",
        'claim_truth': "python 05-exec/claim_truth_scan.py --json ... => 失真候选 1（EXIT=1）"
    }
}
dst = os.path.join(ROOT, '06-benchmark', 'r260_inventory_defect_face.json')
io.open(dst, 'w', encoding='utf-8').write(json.dumps(out, ensure_ascii=False, indent=1))
print('WROTE', dst)
print(json.dumps(out['defect_face_77'], ensure_ascii=False)[:600])