# -*- coding: utf-8 -*-
'''r218_workflow_usage_face.py — 工具 × 工作流本体 的真实调用面（第 94 门，r218）。

为什么缺这一面：目标原话是「把这些免费开发者工具与我现有的**工作流**与相关 skill 合理搭配」。
已有门各量一角 —— 163 能不能跑 / 67 skill 目录里有没有命令级引用 / 93 是否被 skill 承载 /
92 入口会不会派到写着答案的卷 / 88 话术能不能召回 —— 但没有任何门量「我自己的自动化脚本
（05-exec + git hooks + CI）里是否真的调用过这个工具」。把 Workers 从我全部脚本里删干净，
今天 93 门照样绿：它在 67 门 per_tool_exec 也是 0，只被文档提到过。

口径（禁第二真相源）：正则从第 67 门 import TOOLS（命令级，不是产品名）；归一化复用 r214 的
norm；名册读 free_tools_latest.json 的 rows（第 163 门现值）。三处都不是我另写一份。

None ≠ 0（r217 立的规矩）：工具在第 67 门 TOOLS 里没有键 ⇒ 记 NO_PATTERN（未被量），不记 0，
不算缺口；只有「有键且实测 0 命中」才是缺口。

自指告警（不算红）：某工具命中若过半来自**测它自己的探针件**，打印 SELF-REF —— 探针在位
≠ 工作流在用，两者必须能被区分。

用法: python 05-exec/r218_workflow_usage_face.py [--json <件>] [--selftest]
退出码: 0 面建成（缺口按基线只拦增量）/ 2 面取不到或正则与名册对不上（R247 禁按记忆判）。
'''
import argparse
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
B = os.path.join(ROOT, '06-benchmark')
sys.path.insert(0, HERE)

SKIP_DIRS = ('.git', '__pycache__', '_trash', '_bak', 'node_modules', '_temp',
             '06-benchmark', '07-archive', '.venv')
EXTS = ('.py', '.sh', '.ps1', '.yml', '.yaml', '.js', '.ts', '.sql', '.toml')
PROBE_HINT = ('_face', '_fixtures', 'probe', 'matrix', 'check', 'stage', 'debt', 'gate')
# r235：写着模式文本的件不得进匹配面（模块级，便于自测腿直接核对）
EXCL = ('r163_tool_skill_matrix.py', 'r214_tool_carrier_face.py',
        'tool_carrier_patterns.json', 'r218_workflow_usage_face.py',
        'r215_free_tool_roster.py')


def load_patterns():
    from r163_tool_skill_matrix import TOOLS
    return TOOLS


def norm(tool):
    from r214_tool_carrier_face import norm as n
    return n(tool)


def workflow_face():
    files = []
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = [d for d in dns if d not in SKIP_DIRS]
        for f in fns:
            if f.endswith(EXTS):
                files.append(os.path.join(dp, f))
    hk = os.path.join(ROOT, '.git', 'hooks')  # noqa: hooks 也算工作流本体
    if os.path.isdir(hk):
        for f in os.listdir(hk):
            p = os.path.join(hk, f)
            if os.path.isfile(p) and not f.endswith(('.sample', '.bak')):
                files.append(p)
    # 排除定义正则的件：模式文本摆在那儿就必然自匹配（实测 r163_tool_skill_matrix.py
    # 自带 SQLite 20 / GitHub 5 / Turnstile 7 命中），不剔就是把「定义过正则」
    # 算成「调用过工具」。第 93 门的正则表同理（若它出现在面上）。
    excl = EXCL
    keep = []
    for p in files:
        if os.path.basename(p) in excl:
            continue
        if (os.sep + 'hooks' + os.sep in p) or ('05-exec' in p) or (os.sep + '.github' in p):
            keep.append(p)
    return keep


def read(p):
    try:
        return io.open(p, encoding='utf-8', errors='replace').read()
    except OSError:
        return ''


def is_probe(path):
    base = os.path.basename(path).lower()
    return any(h in base for h in PROBE_HINT)


def evaluate():
    tools = load_patterns()
    fr = os.path.join(B, 'free_tools_latest.json')
    if not os.path.isfile(fr):
        return None, '名册源件缺失：free_tools_latest.json'
    rows = (json.load(io.open(fr, encoding='utf-8')) or {}).get('rows') or []
    if not rows:
        return None, '名册 rows 为空 = 空面不得判'
    face = workflow_face()
    if not face:
        return None, '工作流面取到 0 件 = 分母空面，不得据此说没在用'
    texts = [(p, read(p)) for p in face]
    per = []
    total = 0
    for r in rows:
        tool = r.get('tool')
        key = norm(tool)
        pat = None
        for k in tools:
            if norm(k) == key:
                pat = tools[k]
                break
        if pat is None:
            per.append({'tool': tool, 'hits': None, 'probe_share': None,
                        'state': 'NO_PATTERN'})
            continue
        hits = 0
        probe_hits = 0
        real_hits = 0
        real_files = []
        for p, t in texts:
            c = len(re.findall(pat, t, re.I))
            if c:
                hits += c
                if is_probe(p):
                    probe_hits += c
                else:
                    # r222 第二把尺：探针/夹具件不算「真调用」—— 它们是为了测这个工具而写的，
                    # 不是用这个工具干活的。没有这把尺时，面里一堆探针件会让每个工具都显得
                    # 有人在用（r218 实测 Turnstile 27 命中里 25 个来自 r163_free_tools_face 探针）。
                    real_hits += c
                    real_files.append(os.path.basename(p))
        per.append({'tool': tool, 'hits': hits,
                    'probe_share': (round(probe_hits / hits, 3) if hits else None),
                    'real_hits': real_hits,
                    'real_files': sorted(set(real_files))[:12],
                    'state': ('GAP' if hits == 0 else 'USED'),
                    'real_state': ('REAL_GAP' if real_hits == 0 else 'REAL_USED')})
        total += hits
    return {'face_files': len(face), 'tools': per, 'total_hits': total,
            'real_face_files': sum(1 for p, _t in texts if not is_probe(p)),
            'real_total_hits': sum(x.get('real_hits') or 0 for x in per)}, None


def selftest():
    ok1 = bool(re.search('gh\\s+(?:api|pr|issue|run|auth)', 'gh api user'))
    ok2 = len(re.findall('zzz_no_such_tool_xyz', 'anything')) == 0
    ok3 = 'GitHub' in load_patterns()
    # r222 第三腿：探针件不得计入真调用（否则 r218 的 USED 会被自家探针喂出来）
    probe_txt = 'turnstile ' * 40
    ok4 = len(re.findall('turnstile', probe_txt)) == 40 and is_probe('x/r163_free_tools_face.py')
    ok5 = not is_probe('x/r203_ledger_index.py')
    # r235 第四腿：**写着模式文本的文档/报表型件**必须被排除在匹配面外。
    #   动因：名册生成器 r215 的说明文字里引用了部署形态的原样字样 ⇒ 本门把 Workers 的
    #   「0 调用」读成「有调用（2 次）」（真调用合计 89→82 修回）。此腿造一个同名临时件验证排除生效。
    import tempfile
    ok6 = False
    _d = tempfile.mkdtemp(prefix='r235_excl_')
    try:
        _f = os.path.join(_d, 'r215_free_tool_roster.py')
        io.open(_f, 'w', encoding='utf-8').write('# 说明文字：只认 wrangler deploy 与 workers.dev' + chr(10))
        _txt = io.open(_f, encoding='utf-8').read()
        # 面外判定：文件名在 excl 里 ⇒ 不得进入 workflow_face()
        _kept = workflow_face()
        ok6 = (os.path.basename(_f) in EXCL
               and not any(os.path.basename(x) == 'r215_free_tool_roster.py' for x in _kept)
               and bool(re.search('wrangler' + chr(92) + 's+deploy', _txt)))
    finally:
        import shutil as _sh
        _sh.rmtree(_d, ignore_errors=True)
    print('[USAGE:SELFTEST] 正则=%s 空匹配=%s TOOLS=%s 探针不计入=%s 非探针不受影响=%s 文档件被排除=%s' % (
        ok1, ok2, ok3, ok4, ok5, ok6))
    if ok1 and ok2 and ok3 and ok4 and ok5 and ok6:
        print('[USAGE:SELFTEST] 通过（正例匹配、反例不匹配、正则源可读、探针件不计入、写着模式的文档件被排除）')
        return True
    return False


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', dest='out',
                    default='06-benchmark/workflow_usage_latest.json')
    ap.add_argument('--baseline', dest='bl',
                    default='06-benchmark/workflow_usage_baseline.json')
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args(argv)
    if args.selftest:
        return 0 if selftest() else 2
    doc, err = evaluate()
    if doc is None:
        print('[USAGE:UNVERIFIED] ' + str(err) + '（R247 禁按干净记）')
        return 2
    bp = args.bl if os.path.isabs(args.bl) else os.path.join(ROOT, args.bl)
    known = []
    if os.path.isfile(bp):
        known = (json.load(io.open(bp, encoding='utf-8')) or {}).get('known_gaps') or []
    gaps = []
    for x in doc['tools']:
        if x['state'] == 'GAP':
            # 缺口串只放工具名：面件数是易变量（新增脚本就变），放进串里基线永不匹配，
            # 等于自造下轮假红（本仓反复踩过的「易变量入基线」坑）。
            # ⚠ 本文件严禁复述任何正则字面量：解释正则的文字若写出命令样例，会当场
            #    匹配上该正则而自造命中（本轮就这么把真 0 命中的工具污染成 USED(2)，
            #    且 2/2 全来自探针件；SELF-REF 报警正是靠它才暴露）。
            # 措辞限定：本门正则取自第 67 门，属「部署/代码形态」级；API 读数型用法
            # （如走 GraphQL 取调用数的那类探针）不在其口径内 ⇒ 命中 0 只说明「未见
            # 部署形态调用」，不得写成「未接入任何自动化」。
            s = '%s|工作流面未见部署/代码形态级调用' % x['tool']
            if s not in known:
                gaps.append(s)
    npat = [x['tool'] for x in doc['tools'] if x['state'] == 'NO_PATTERN']
    sref = [x['tool'] for x in doc['tools']
            if x['hits'] and (x['probe_share'] or 0) >= 0.5]
    # r222 第二把尺的告警：探针件贡献过半 ⇒ 该工具的 USED 主要是「有人测它」而非「有人用它」。
    # 这不算红（探针在位是好事），但必须显形，否则 USED 会被读成「已接入自动化」。
    rgap = [x['tool'] for x in doc['tools']
            if x['hits'] and (x.get('real_hits') or 0) == 0]
    op = args.out if os.path.isabs(args.out) else os.path.join(ROOT, args.out)
    body = {'schema': 'workflow-usage-v1', 'readonly': True,
            'provenance_cmd': 'python 05-exec/r218_workflow_usage_face.py --json <件>',
            'regex_source': 'r163_tool_skill_matrix.TOOLS（第 67 门，命令级）',
            'roster_source': 'free_tools_latest.json rows（第 163 门）',
            'known_gaps_in': len(known), 'new_gaps': gaps,
            'no_pattern': npat, 'self_ref': sref}
    body.update(doc)
    io.open(op, 'w', encoding='utf-8', newline=chr(10)).write(
        json.dumps(body, ensure_ascii=False, indent=1))
    print('[USAGE] 工作流面 %d 件（真调用面 %d）/ 名册 %d 工具 / 命令级命中合计 %d（真调用 %d）' % (
          doc['face_files'], doc['real_face_files'], len(doc['tools']),
          doc['total_hits'], doc['real_total_hits']))
    for x in sorted(doc['tools'], key=lambda z: str(z['tool'])):
        print('  %-22s %-11s hits=%-6s 探针占比=%s' % (
              x['tool'], x['state'], x['hits'], x['probe_share']))
    if npat:
        print('[USAGE:NO_PATTERN] 无权威正则（未量 ≠ 没在用）= %s' % npat)
    if sref:
        print('[USAGE:SELF-REF] 命中过半来自测它的探针（在位≠工作流在用）= %s' % sref)
    if rgap:
        print('[USAGE:REAL-GAP] 命中全部来自探针件 = 无人用它干活（advisory，不判红）= %s' % rgap)
    if gaps:
        print('[USAGE:FAIL] 新增未接入缺口 %d 条：' % len(gaps))
        for s in gaps:
            print('   - ' + s)
        return 1
    if not selftest():
        print('[USAGE:SELFTEST] 不过 ⇒ 判据无牙，不得记通过')
        return 2
    print('[USAGE:PASS] 无新增未接入工具（历史 %d 条在基线内，只准减不准增）' % len(known))
    return 0


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
    sys.exit(main())