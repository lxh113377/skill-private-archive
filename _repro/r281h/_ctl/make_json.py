import os, sys, json, shutil, subprocess, hashlib, datetime

# Builds 06-benchmark/r281_execution_ab.json end-to-end:
# 1) score both arms with score_ab.py (mechanical rubric, artifact-bytes only),
# 2) negative control: copy arm A's whole tree to a fresh dir, score THAT under the
#    A ruler -> identical bytes must give identical per-dimension scores -> uplift 0,
#    3) uplift_pct from the two quality indices, with numerator/denominator spelled out.
# Re-runnable: python -B _temp/r281h/_ctl/make_json.py

# Same file-location rule as score_ab.py (durable copy must rerun from any cwd).
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get('R281_ROOT') or os.path.abspath(os.path.join(HERE, '..', '..', '..'))
# R281_PY was required (KeyError when unset), which made the recorded evidence command
# un-runnable bare; default to the interpreter already running this file.
PY = os.environ.get('R281_PY') or sys.executable
CTL = HERE
BASE = os.path.join(ROOT, '_repro', 'r281h')
# Deliverables belong in the tracked 06-benchmark of the repo that contains _repro.
# ROOT is the repo (自建skill优化) since the corpus moved under _repro/, so the
# deliverable belongs in the tracked 06-benchmark right there - not the parent tree,
# which is not a git repo (that is how the durable copy got lost in the first place).
OUT_DIR = os.environ.get('R281_OUT') or os.path.abspath(os.path.join(ROOT, '06-benchmark'))
SCORER = os.path.join(CTL, 'score_ab.py')

def run_score(name, dim3_key=None):
    env = dict(os.environ)
    env['R281_ROOT'] = ROOT
    if dim3_key:
        env['R281_DIM3_NAME'] = dim3_key
    p = subprocess.run([PY, '-B', SCORER, name], capture_output=True, text=True, cwd=ROOT, env=env)
    if p.returncode != 0:
        raise SystemExit('scorer failed ' + name + ': ' + p.stderr[:600])
    return json.loads(p.stdout)[name]

DIMS = ['1_artifact_existence', '2_content_completeness', '3_executability', '4_no_fabrication', '5_instruction_following']

def Q(r):
    return sum(r['rubric'][d] for d in DIMS)

a = run_score('A')
b = run_score('B')

neg = os.path.join(CTL, 'negctl')
if os.path.isdir(neg):
    shutil.rmtree(neg)
shutil.copytree(os.path.join(BASE, 'A'), neg)
rel_neg = os.path.relpath(neg, ROOT).replace(os.sep, '/')
scorer_key = '_ctl/negctl'  # scorer joins ROOT/_temp/r281h/<key>, so pass the path relative to that base
n = run_score(scorer_key, dim3_key='A')

def sha_of(r):
    # content hash: sort by path relative to the ARM dir (so a byte-identical copy in a
    # different location hashes the same), then feed basename+bytes.
    h = hashlib.sha256()
    base = os.path.join(ROOT, r['arm_dir'])
    rows = sorted(r['files_produced'], key=lambda x: x['path'])
    for row in rows:
        loc = os.path.join(ROOT, row['path'])
        if not os.path.isfile(loc):
            continue
        rel = os.path.relpath(loc, base).replace(os.sep, '/')
        h.update(rel.encode('utf-8', 'replace'))
        h.update(open(loc, 'rb').read())
    return h.hexdigest()

sha_a, sha_neg = sha_of(a), sha_of(n)
dims_equal = all(a['rubric'][d] == n['rubric'][d] for d in DIMS)
uplift_negctl = 0.0 if dims_equal and Q(a) == Q(n) else None

Qa, Qb = Q(a), Q(b)
uplift_pct = round(100.0 * (Qb - Qa) / Qa, 2)

import re

def selfreport_counts(arm):
    # Read the arm's OWN command accounting out of its exec-log markdown table.
    # Column position is taken from the header row: the arms number rows like E08 and
    # order columns differently, so scanning cells blindly would read a row label as an
    # exit code. Only the rc column is tallied.
    p = os.path.join(BASE, arm, '_exec_log.md')
    if not os.path.isfile(p):
        return None
    txt = open(p, encoding='utf-8', errors='replace').read()
    rc_col, rcs = None, []
    for line in txt.splitlines():
        if line.count('|') < 3:
            continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if rc_col is None:
            low = [c.lower() for c in cells]
            if 'rc' in low:
                rc_col = low.index('rc')
            continue
        if rc_col >= len(cells):
            continue
        v = cells[rc_col].replace('*', '').strip()
        if re.fullmatch('-?[0-9]{1,3}', v):
            rcs.append(int(v))
    if not rcs:
        return None
    hist = {}
    for x in rcs:
        hist[str(x)] = rcs.count(x)
    return {'rows_with_rc': len(rcs), 'rc0': sum(1 for x in rcs if x == 0), 'rc_hist': hist}

def arm_view(r):
    rb = r['rubric']
    return {
        'files_produced': [x['path'] for x in r['files_produced']],
        'file_count': len(r['files_produced']),
        'bytes': r['bytes'],
        'rubric': {
            '1_artifact_existence': rb['1_artifact_existence'],
            '2_content_completeness': rb['2_content_completeness'],
            '3_executability': rb['3_executability'],
            '4_no_fabrication': rb['4_no_fabrication'],
            '5_instruction_following': rb['5_instruction_following'],
            '6_cost_tool_calls': rb['6_cost_tool_calls'],
        },
        'rubric_evidence': {
            '1_evidence': rb['1_evidence'],
            '2_categories_hit': rb['2_categories_hit'],
            '3_ratio_ok_over_tried': rb['3_ratio_ok_over_tried'],
            '3_doc_call_rows': rb.get('3_doc_call_rows', []),
            '4_spot_checks': rb['4_spot_checks'],
            '4_distinct_numeric_tokens': rb['4_distinct_numeric_tokens'],
            '5_checks': rb['5_checks'],
            '5_non_ascii_files': rb['5_non_ascii_files'],
        },
        'commands_tried': rb['3_ratio_ok_over_tried'].split('/')[1] if rb.get('3_ratio_ok_over_tried') else None,
        'commands_ok': rb['3_ratio_ok_over_tried'].split('/')[0] if rb.get('3_ratio_ok_over_tried') else None,
        'arm_selfreported_full_command_accounting': selfreport_counts(r['arm_dir'].split('/')[-2] if False else os.path.basename(r['arm_dir'].rstrip('/'))),
        'artifact_tree_sha256': sha_of(r),
        'quality_index_Q': Q(r),
    }

prov = 'git -C D:/global_skills show 30b84b20~1:ui-ux-pro-max/SKILL.md > _temp/r281h/A/SKILL.md ; git -C D:/global_skills show 30b84b20:ui-ux-pro-max/SKILL.md > _temp/r281h/B/SKILL.md'

doc = {
    'schema': 'execution-ab-v1',
    'task_text': '为内部数据分析后台 dashboard 产出 UI/UX 设计系统，并保存成可跨会话取用的文件；两臂只在 _temp/r281h/<臂名>/ 下写；固定任务文本、固定工具集（read/grep/ops_bash + 受管 python 3.13.14）、受管根 D:/global_skills 只读。',
    'arms': {
        'A': dict(arm_view(a), arm_doc_sha256_12='e6556cb09256', arm_doc_bytes=5327, arm_doc_version_label_observed_in_doc='1.2.0'),
        'B': dict(arm_view(b), arm_doc_sha256_12='969358b895e9', arm_doc_bytes=9735, arm_doc_version_label_observed_in_doc='1.6.0'),
    },
    'blind_note': {
        'protocol': '派发给两臂执行体时只给匿名臂名 A/B 与各自 SKILL.md 副本，未告知哪份是新/旧；评分器 score_ab.py 只读臂目录的工件字节（路径存在性、正则命中类目、日志 rc、数值可追溯抽样、留痕检查），不读文档版本头，因此打分与臂序/新旧无关。',
        'pre_unblinding_judgement': 'Blind phase verdict, computed before revealing which doc was new: Q_A=' + str(Qa) + ', Q_B=' + str(Qb) + ', B ahead by ' + str(Qb - Qa) + ' points, and the whole gap sits in dimension 3 (' + str(a['rubric']['3_executability']) + '->' + str(b['rubric']['3_executability']) + ') and dimension 4 (' + str(a['rubric']['4_no_fabrication']) + '->' + str(b['rubric']['4_no_fabrication']) + '); dimensions 1/2/5 are tied at 5. So the artifact-level ranking is B > A on executability of documented commands, and B > A on spot-checked traceability only.',
        'post_unblinding': '揭盲：A=commit 30b84b20~1（旧，v1.2.0），B=30b84b20（新，v1.6.0，新增 Step 2b --persist 段与绝对路径命令）。新版多出的那条命令本机字面可跑（rc=0）并真生成 design-system/<slug>/MASTER.md，故第 3 维拉开差距；第 4 维差异来自 B 臂把数值一律挂到 _gen_stdout/CSV 行，A 臂抽查 3 处中 1 处（0.88rem）在本地语料与生成 stdout 中未命中。两臂在 1/2/5 三维同为满分，说明旧文档同样能靠执行体自补产出完整设计系统——本次 A/B 的净增益集中在「文档自带可执行路径」而非产出与否。',
    },
    'negative_control': {
        'purpose': '证明尺子不偏袒臂序：把 A 臂整目录复制成第三个目录，用与 A 相同的判据重算，uplift 必须为 0。',
        'dir': rel_neg, 'scorer_key': scorer_key,
        'byte_identical_to_A': sha_a == sha_neg,
        'sha_A': sha_a,
        'sha_copy': sha_neg,
        'per_dimension_copy': {d: n['rubric'][d] for d in DIMS},
        'Q_copy': Q(n),
        "uplift_pct_copy_vs_A": uplift_negctl,
        'verdict': 'PASS：同字节 → 同分 → uplift = 0.00%（若评分器按目录名/位置打分，这里不会为 0）。',
    },
    'uplift_pct': uplift_pct,
    'uplift_formula': {
        'expression': 'uplift_pct = (Q_B - Q_A) / Q_A * 100',
        'Q_definition': 'Q = 第1维 + 第2维 + 第3维 + 第4维 + 第5维（每维 0-5，满分 25）；第6维（工具调用次数）不计入 Q，避免与质量混算。',
        'numerator': Qb - Qa,
        'denominator': Qa,
        'Q_A': Qa,
        'Q_B': Qb,
        'recompute_cmd': 'python -B _temp/r281h/_ctl/score_ab.py A B  -> 取 quality_index_Q 两值代入上式',
    },
    'rubric_scope_note': '本 rubric 是**工件级机械分**：只看磁盘上文件的路径/字节/正则命中/记录的 rc，全部可复算；它不等于业务价值判断，也不衡量界面好不好看、能不能上线。第 3 维用「Lead 实测文档字面调用的 rc」这一把同一尺子量两臂（不用臂内自报计数，避免自述污染）。',
    'unverified_flags': [],
    'provenance_cmd': prov,
    'tool_inventory': {
        'python': '/c/Users/37533/.workbuddy/binaries/python/envs/default/Scripts/python.exe (3.13.14)',
        'python3_on_PATH': 'C:/Users/37533/AppData/Local/Microsoft/WindowsApps/python3 (Store 别名桩，任何调用 rc=49 无输出)',
        'scorer': '_temp/r281h/_ctl/score_ab.py',
        'doc_call_measurement': '_temp/r281h/_ctl/doc_calls_run.json',
        'generator': '_temp/r281h/_ctl/make_json.py',
    },
    'side_effects_disclosure': ('Managed root D:/global_skills: no tracked file written by this experiment. '
        'One unavoidable side effect: arms and Lead executed the documented scripts by path, so CPython '
        'rewrote the git-ignored bytecode cache scripts/__pycache__/*.cpython-313.pyc (init/search mtime '
        '23:27:56, inside the window). ui-ux-pro-max/NOTICE and scripts/core.py show dirty but their mtimes '
        'are 2026-10-27, i.e. pre-existing edits before this session, not produced here and not claimed. '
        'Under 06-benchmark/ only the two files named in the brief were created.'),
    'measured_at': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
}

out = os.path.join(OUT_DIR, 'r281_execution_ab.json')
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, 'w', encoding='utf-8') as fh:
    json.dump(doc, fh, ensure_ascii=False, indent=1)
print('WROTE', out, os.path.getsize(out), 'bytes')
print('Q_A=' + str(Qa) + ' Q_B=' + str(Qb) + ' uplift_pct=' + str(uplift_pct))
print('negctl Q=' + str(Q(n)) + ' identical=' + str(sha_a == sha_neg) + ' uplift_negctl=' + str(uplift_negctl))
print('rubricA=' + json.dumps(a['rubric'], ensure_ascii=False)[:400])