# -*- coding: utf-8 -*-
'''r237_roster_audit.py - 名册四层独立复算审计（r237 新建，只读）。

为什么需要它：r215-r236 逐轮把名册做成四层可复算产物，但**每一层都是它自己那道门算的** ——
  名册只是把门的产物拼起来。谁也没验过「门算得对不对」。本件**不复用任何门内函数**：
  自己走盘、自己计数（只借 r163 的正则源 = 权威定义），把四层逐工具与名册对账。

  r237 首跑结果：10 个工具四层全对（漂移 0）。唯一「不一致」是 Pages-Functions —— 它在第 67 门尺里、
  但不在免费工具名册的 10 行里（TOOLS 11 键 vs 名册 10 行，两边分母不同的已知口径差，见台账 R216-2），
  故本件把「不在名册的工具」单列为 known_not_in_roster，不计入漂移。

判据（三态）：漂移 0 ⇒ PASS(0)；有漂移 ⇒ FAIL(1) 并逐工具印「复算值 != 名册值」；
  源件缺 / 面为空 ⇒ UNVERIFIED(2)（R247 禁按 0 记绿）。
用法: python 05-exec/r237_roster_audit.py [--json <件>]
'''
import argparse
import glob
import io
import json
import os
import re
import subprocess
import time
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
B = os.path.join(ROOT, '06-benchmark')
sys.path.insert(0, HERE)
from r163_tool_skill_matrix import TOOLS  # 只借正则源（权威定义）

GS = 'D:/global_skills'
CODE_EXT = ('.py', '.sh', '.ps1', '.mjs', '.js', '.ts', '.sql')
WEXTS = ('.py', '.sh', '.ps1', '.yml', '.yaml', '.js', '.ts', '.sql', '.toml')
# r242 自抓：本件原先**自带一份 EXCL/PROBE 副本** ⇒ r218 那边加了 r237 自己，这边没跟，
#   于是审计把自己算进 Turnstile 的命中（28!=25）而门算的是 25 —— 漂移假象由「两份策略副本」造成。
#   改为**策略单一来源**：排除名单与探针名单一律从第 94 门借（那是「谁算工作流面」的契约），
#   而本件保留独立的是**遍历 / 计数 / 取值算法**。
from r218_workflow_usage_face import EXCL, PROBE_HINT as PROBE
FMARKS = ('.git', 'SKILL.md')
SKIP = ('node_modules', '.git', 'dist', '.wrangler', 'archive', '__pycache__')


def layer1():
    '''skill 目录：提到件数 / 代码级件数（自走盘）'''
    men, exe = {}, {}
    for slug in sorted(os.listdir(GS)):
        sd = os.path.join(GS, slug)
        if not os.path.isfile(os.path.join(sd, 'SKILL.md')):
            continue
        try:
            blob = [io.open(os.path.join(sd, 'SKILL.md'), encoding='utf-8', errors='replace').read()]
        except OSError:
            continue
        code = []
        for sub in ('references', 'scripts'):
            d = os.path.join(sd, sub)
            if not os.path.isdir(d):
                continue
            for fn in sorted(os.listdir(d))[:25]:
                fp = os.path.join(d, fn)
                if not os.path.isfile(fp) or os.path.getsize(fp) >= 200000:
                    continue
                try:
                    txt = io.open(fp, encoding='utf-8', errors='replace').read()
                except OSError:
                    continue
                blob.append(txt)
                if fn.endswith(CODE_EXT):
                    code.append(txt)
        b = chr(10).join(blob)
        c = chr(10).join(code)
        for tool, pat in TOOLS.items():
            if re.search(pat, b, re.I):
                men.setdefault(tool, set()).add(slug)
            if c and re.search(pat, c, re.I):
                exe.setdefault(tool, set()).add(slug)
    return men, exe


def layer2():
    '''工作流面：排除探针件与写模式的件，逐工具真调用计数（自走盘）'''
    files = []
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = [d for d in dns if d not in ('.git', '__pycache__', '_trash', '_bak',
                                             'node_modules', '_temp', '06-benchmark',
                                             '07-archive', '.venv')]
        for f in fns:
            if not f.endswith(WEXTS):
                continue
            fp = os.path.join(dp, f)
            if os.path.basename(fp) in EXCL:
                continue
            if ((os.sep + 'hooks' + os.sep) in fp or '05-exec' in fp
                    or (os.sep + '.github') in fp):
                files.append(fp)
    res = {}
    for tool, pat in TOOLS.items():
        n = 0
        for fp in files:
            if any(h in os.path.basename(fp).lower() for h in PROBE):
                continue
            try:
                t = io.open(fp, encoding='utf-8', errors='replace').read()
            except OSError:
                continue
            n += len(re.findall(pat, t, re.I))
        res[tool] = n
    # r257：把「贡献真命中的件」一起交出去，供下面「只算跟踪件」的第二分母核对
    contrib = set()
    for tool, pat in TOOLS.items():
        for fp in files:
            if any(h in os.path.basename(fp).lower() for h in PROBE):
                continue
            try:
                t = io.open(fp, encoding='utf-8', errors='replace').read()
            except OSError:
                continue
            if re.search(pat, t, re.I):
                contrib.add(os.path.relpath(fp, ROOT).replace(os.sep, '/'))
    return res, len(files), contrib


def layer3():
    '''项目仓：剪掉嵌套 .git / 同目录 SKILL.md 的外来面，逐工具计数（自走盘）'''
    cand = sorted(glob.glob(os.path.join(B, 'tool_skill_matrix_r*.json')),
                  key=os.path.getmtime)
    mx = None
    for fp in reversed(cand):
        try:
            d = json.load(io.open(fp, encoding='utf-8'))
        except (OSError, ValueError):
            continue
        if d.get('third_face'):
            mx = d
            break
    if mx is None:
        return None, None
    roots = (mx.get('third_face') or {}).get('roots') or []
    res = {}
    for root in roots:
        for dp, dns, fns in os.walk(root):
            keep = []
            for d in dns:
                if d in SKIP:
                    continue
                sub = os.path.join(dp, d)
                if any(os.path.exists(os.path.join(sub, mk)) for mk in FMARKS):
                    continue
                keep.append(d)
            dns[:] = keep
            for f in fns:
                if not f.endswith(CODE_EXT):
                    continue
                fp = os.path.join(dp, f)
                try:
                    if os.path.getsize(fp) > 200000:
                        continue
                    t = io.open(fp, encoding='utf-8', errors='replace').read()
                except OSError:
                    continue
                for tool, pat in TOOLS.items():
                    n = len(re.findall(pat, t, re.I))
                    if n:
                        res[tool] = res.get(tool, 0) + n
    return res, roots


def layer5():
    '''第 5 层（用量）独立取值：**自己写一套路径解析**，不调 r215 的解析器。

    r240 补：r239 加了第 5 层用量，但没把它纳入独立复算 ⇒ 审计只覆盖前四层（这是我自己留的口子）。
    每加一层就必须能被独立复核，否则新增的那层只有它自己的实现背书。
    未登记用量的工具 ⇒ 期望 None（未量），不是 0。
    '''
    specs = {
        'Cloudflare-Workers': ('workers_quota_latest.json', ['row', 'invocations_month']),
        'Cloudflare-D1': ('quota_face_latest.json',
                         ['rows', 'cloudflare_d1', 'mib']),
        # r241：GitHub 用量源换成官方计费端点产物（与 r215 的 READ_FACE 同步改，见 §96）
        'GitHub': ('gh_billing_latest.json', ['minutes_total']),
        'Cloudflare-Pages': ('pages_http_latest.json', ['row', 'requests_total']),
        # r242：Turnstile 用量（官方数据集，参数名运行时自省）
        'Cloudflare-Turnstile': ('turnstile_usage_latest.json', ['count_total']),
        # r243：SQLite 本地体量（非额度）
        'SQLite': ('sqlite_usage_latest.json', ['size_mib']),
    }
    res = {}
    for tool, (art, path) in specs.items():
        fp = os.path.join(B, art)
        if not os.path.isfile(fp):
            res[tool] = ('MISSING', 'te artifact absent: ' + art)
            continue
        try:
            d = json.load(io.open(fp, encoding='utf-8'))
        except (OSError, ValueError):
            res[tool] = ('UNPARSABLE', art)
            continue
        cur = d
        i = 0
        ok = True
        while i < len(path):
            k = path[i]
            if k == 'rows':
                want = path[i + 1] if i + 1 < len(path) else None
                row = None
                for x in ((cur.get('rows') if isinstance(cur, dict) else None) or []):
                    if isinstance(x, dict) and x.get('tool') == want:
                        row = x
                        break
                if row is None:
                    ok = False
                    break
                cur = row
                i += 2
                continue
            if not isinstance(cur, dict) or k not in cur:
                ok = False
                break
            cur = cur[k]
            i += 1
        res[tool] = (cur if ok else 'PATH-MISS', art)
    return res


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', dest='out', default='')
    args = ap.parse_args(argv)
    rf = os.path.join(B, 'free_tool_roster_latest.json')
    if not os.path.isfile(rf):
        print('[ROSTER-AUDIT:UNVERIFIED] 名册件缺失 ⇒ 无可对账面（R247）')
        return 2
    if not os.path.isdir(GS):
        print('[ROSTER-AUDIT:UNVERIFIED] global_skills 面取不到 ⇒ 层1 无分母（R247）')
        return 2
    ros = json.load(io.open(rf, encoding='utf-8'))
    rost = {it['tool']: it for it in (ros.get('items') or [])}
    if not rost:
        print('[ROSTER-AUDIT:UNVERIFIED] 名册 items 为空 ⇒ 空面不得判对')
        return 2
    men, exe = layer1()
    wf, wface, wf_contrib = layer2()
    th, roots = layer3()
    us = layer5()
    if th is None:
        print('[ROSTER-AUDIT:UNVERIFIED] 取不到含 third_face 的矩阵件 ⇒ 层3 无分母（R247）')
        return 2
    # r257：第二分母 —— **只算 git 已跟踪件**。工作树里未跟踪的散落件若贡献了真命中，就是在本门面外灌数
    #   （我经常往 05-exec 写临时件）。实测 r257：两面各 265 件、逐工具全等、未跟踪贡献件 = 0。
    drift = []
    # r257：第二分母 —— 只算 git 已跟踪件（工作树里的未跟踪散落件若贡献真命中，就是本门面外灌数）。
    untracked_contrib = []
    tracked = None
    try:
        r_ = subprocess.run(['git', '-c', 'core.quotepath=false', 'ls-files'], cwd=ROOT,
                            capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=200)
        tracked = set(l.strip() for l in (r_.stdout or '').splitlines() if l.strip())
    except OSError as _e:
        # r257 自抓：首版这里写的是 `except Exception`，而本件**没 import subprocess** ⇒ NameError 被吞，
        #   判据静默失效（rc=1 却没有我期待的那行）。放宽的 except 又一次把判据变成了装饰品。
        #   现只吞 OSError（二进制缺失），其余如实上抛；取不到跟踪面则显式记一条，禁静默当「核对过了」。
        tracked = None
        drift.append('无法核对第二分母（git ls-files 失败：%s）⇒ 本项不得算核对过' % str(_e)[:60])
    if tracked is not None:
        untracked_contrib = sorted(wf_contrib - tracked)
    if untracked_contrib:
        drift.append('未跟踪件贡献了第②层真命中（工作树灌数）=%s' % untracked_contrib[:5])
    known = []
    for tool in sorted(TOOLS):
        if tool not in rost:
            known.append(tool)
            continue
        it = rost[tool]
        u = us.get(tool)
        a5 = it.get('usage_value')
        p5 = (None, 'no usage spec')
        if u is not None:
            p5 = (u[0], u[1]) if isinstance(u[0], (int, float)) else (None, str(u[0]))
        pairs = (
            ('层1提到', len(men.get(tool) or []), len(it.get('mention_skills') or [])),
            ('层1代码', len(exe.get(tool) or []), len(it.get('exec_skills') or [])),
            ('层2', wf.get(tool, 0), it.get('wf_real_hits') or 0),
            ('层3', th.get(tool, 0), it.get('third_hits') or 0),
            ('层5用量', (p5[0] if p5[0] is not None else None), a5),
        )
        # r259：把第⑤层的差异**具名成因** —— 它是活的网络读数，与「上一轮快照」比必然随时间漂，
        #   那不等于复算错了。首版一律写成「复算与名册不一致」，会把「读数过期」误报成「算错」（r249/r250 同族：
        #   差异必须带成因，否则排障指错方向）。
        _bad_l5 = [k for k, a, b in pairs if k == '层5用量' and a != b]
        _roster_age = None
        try:
            _art = os.path.join(B, 'free_tool_roster_latest.json')
            _d = json.load(io.open(_art, encoding='utf-8'))
            # r259 自抓：首版只看文件 mtime —— 克隆检出会把 mtime 重置成「刚刚」，于是陈旧快照看起来是新鲜读数。
            #   改为优先用件自带的 read_at（r259 起写入）；无 read_at（旧件）⇒ 视作无法判定 ⇒ 按「可能陈旧」具名。
            _ra = _d.get('read_at')
            if _ra:
                _roster_age = time.time() - __import__('datetime').datetime.fromisoformat(_ra).timestamp()
            else:
                _roster_age = None
        except (OSError, ValueError):
            _roster_age = None
        _stale = bool(_bad_l5) and (_roster_age is None or _roster_age > 900)   # 无 read_at 也算「可能陈旧」
        bad = ['%s %s!=%s%s' % (k, a, b, '（读数随时间变化，非复算错误）' if (k == '层5用量' and _stale) else '')
               for k, a, b in pairs if a != b]
        if bad:
            drift.append('%s: %s' % (tool, ' / '.join(bad)))
    doc = {'schema': 'roster-audit-v1', 'readonly': True,
           'provenance_cmd': 'python 05-exec/r237_roster_audit.py --json <件>',
           'roster_tools': len(rost), 'tools_in_matrix_only': known,
           'workflow_face_files': wface, 'third_roots': roots,
           'drift': drift,
           'layer5_usage': {k: (v[0], v[1]) for k, v in (us or {}).items()},
           'per_tool': {t: {'l1_mention': len(men.get(t) or []),
                            'l1_exec': len(exe.get(t) or []),
                            'l2': wf.get(t, 0), 'l3': th.get(t, 0)} for t in sorted(rost)}}
    if args.out:
        op = args.out if os.path.isabs(args.out) else os.path.join(ROOT, args.out)
        io.open(op, 'w', encoding='utf-8', newline=chr(10)).write(
            json.dumps(doc, ensure_ascii=False, indent=1))
    print('[ROSTER-AUDIT] 名册 %d 工具 / 工作流面 %d 件 / 项目仓 %d 个 / 用量面 %d 项' % (
        len(rost), wface, len(roots or []), len(us or {})))
    for t in known:
        print('  [已在第 67 门尺内、不在名册] %s（已知分母差，见台账 R216-2，不计漂移）' % t)
    for d in drift:
        print('  漂移: ' + d)
    if drift:
        print('[ROSTER-AUDIT:FAIL] 独立复算与名册不一致 %d 项' % len(drift))
        return 1
    print('[ROSTER-AUDIT:PASS] 五层逐工具独立复算与名册一致（漂移 0；只借正则源，其余全自走盘）')
    return 0


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
    sys.exit(main())