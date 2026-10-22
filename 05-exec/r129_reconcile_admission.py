# -*- coding: utf-8 -*-
# r129_reconcile_admission.py — 新判据入库准入门（R128-2 落地）。
#
# 存在理由（r126 -> r128 三轮一手代价）：
#   r126 的可达性判定只建模 bge_recall 的第一次候选集构造，漏了 L1.5 兜底 union，
#   产出「79 题不可达 / 15 条 tag_trap」；报告与转办提案第 9 条都用了这些数字，
#   直到 r127 逐条对账才发现其中 45 条是假红，真闭包只有 2 条。
#   r128 已把「对账」做成机器（r128_ruler_reconcile.py，第 40 门），但没有卡入库：
#   判据照样能直接进 GATES 表、照样能出报告数字 => 同样的错还会再犯。
#
# 本件做什么（准入门，不是又一个分析器）：
#   只检**最近 N 轮新增**的、能产出逐条读数的判据脚本（git log 近 N 次提交里出现的 .py），
#   要求它们满足二选一：(1) 已入 run_gates 的 GATES 表 / 季度巡检；(2) 命名形态表明只读不判。
#
#   为什么只检新增（r129 第三次收窄）：全仓扫描会命中 33 条，其中绝大多数是**被 runner 间接调用**
#   的历史子件（r38_debt_aging 是 ratchet_gate 的指标源、claim_truth_scan 由 r19_scan_fixtures 调）——
#   静态判据追不动真实调用图，于是「扫全仓」这条路只会稳定产出假红（r129 已连撞三次：70 / 40 / 33）。
#   而真正需要卡住的是**新写的判据**：R128-2 的原话是「新判据首次落盘时就要对账」，
#   不是「历史 170 个脚本全部重新入册」。故口径 = git log 近 N 次提交新增/修改的脚本。
#   这是**按可判定性收窄判据面**，不是放宽：新增面若未入册仍判红。
#
# 用法: python 05-exec/r129_reconcile_admission.py [--json <件>]
# 退出码: 0 全合规 / 1 有未声明脚本 / 2 输入面不可用
import argparse
import io
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)   # r129 自抓：初版漏定义 ROOT，cwd=ROOT 抛 NameError 被 except 吞掉
                                 # => recent 静默退化成「全仓脚本集」=> 判据面意外放大到 170 个
                                 # （读数上表现为「近 N 次提交 = 170 个」，与 git 实测 8 个矛盾）。
RUNNER = os.path.join(HERE, 'run_gates.py')

EXEMPT_PATTERNS = [
    r'_probe\.py$',
    r'_face\.py$',
    r'_fixtures?\.py$',
    r'_ruler\.py$',
    r'_admission\.py$',
    r'_ledger_fixtures\.py$',
    r'f\d+_.*\.py$',
    # r129 五修（对账后剩下的 4 条逐条核实，全部是被**间接调用**的核心件，不是漏入册）：
    #   run_gates.py            = runner 本体（它是被检对象里最上游的一件）
    #   r38_debt_aging.py       = ratchet_gate 的 debt 三指标来源（由棘轮调用，不在 GATES 表直列）
    #   r113_quarterly_audit.py = 季度巡检本体（它调用别人，不是被调用方）
    #   r128_ruler_reconcile.py = 第 40 门的**被测件**（夹具调它，见 w47 fixtures t1-t4）
    # 显式列出而不是用命名通配：豁免必须可逐条解释（R269 同族的「登记不放宽判据」）。
    r'^run_gates\.py$',
    r'^r38_debt_aging\.py$',
    r'^r113_quarterly_audit\.py$',
    r'^r128_ruler_reconcile\.py$',
    r'_lib\.py$',
]

# r129 自抓（首跑即假红，与 r126 同族）：初版判据用「源码里出现 rows/items/detail 键名」
# 作标志 ⇒ 首跑 70 条未声明，而其中绝大多数只是局部变量名，根本不是判据产物。
# 根因同 r126：判据与被测系统不对账就上线。
# 收窄口径：**必须真的写出逐条读数文件**（--json 且落盘 rows/items/detail），
# 即源码同时具备「argparse --json」与「写出 rows/items/detail」两处，才算产读数脚本。
# 这仍不是完美判据（能静态看出是否 argparse），但已与真实情况对齐，可作准入门。
HAS_JSON_ARG = re.compile(r'--json')
WRITES_ROWS = re.compile(r"(rows|items)\s*['\"]?\s*\]?")


def looks_like_producer(src):
    if not HAS_JSON_ARG.search(src):
        return False
    return bool(WRITES_ROWS.search(src))
SCRIPT_RE = re.compile(r'.script.\s*:\s*.(.+?\.py).')
# r129 二修（第二次假红）：准入门只认「在 run_gates 的 GATES 表里」，但本仓有**两套入册面**——
# 一套是 GATES 表（逐轮必跑），另一套是季度巡检（r113_quarterly_audit.py 的 steps，按季跑）。
# 只认前者会把 r117_route_miss_attr / r126_tag_closure 等全部判红，而它们确实已入册。
# 修法：两套面都认（巡检面按脚本文件名出现在巡检源码里判定）。
QUARTERLY = os.path.join(HERE, 'r113_quarterly_audit.py')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', dest='out')
    # r131 补（门会抓你却没给你登记通道）：本门首跑就把 r131 新建的
    # r131_closure_layers.py / r131_direct_closure.py 判成 UNDECLARED，
    # 但工具没有 --record，只能改脚本名或手改台账 —— 「有牙齿但没钥匙」同样 unusable。
    ap.add_argument('--register', default='', help='把该脚本登记为「只读面豁免」（须带 --evidence 对账/夹具产物）')
    ap.add_argument('--evidence', default='', help='--register 的证据产物路径（必填，禁无证据登记）')
    REG = os.path.join(ROOT, '05-exec', '.read_face_registry.json')
    args = ap.parse_args()
    if not os.path.isfile(RUNNER):
        print('[ADMIT] UNVERIFIED runner 不存在: %s' % RUNNER)
        return 2
    runner_src = io.open(RUNNER, encoding='utf-8').read()
    registered = set(m.group(1) for m in SCRIPT_RE.finditer(runner_src))
    # --register 形态：把一个只读面脚本登记豁免（必须带真实证据产物）
    reg_path = REG
    reg = {}
    if os.path.isfile(reg_path):
        try:
            reg = json.loads(io.open(reg_path, encoding='utf-8').read()) or {}
        except Exception:
            reg = {}
    if args.register:
        if not args.evidence:
            print('[ADMIT] REFUSE --register 须同时给 --evidence（无证据的登记等于装饰）')
            return 1
        ev = args.evidence
        full = ev if os.path.isabs(ev) else os.path.join(ROOT, ev)
        if not os.path.isfile(full):
            print('[ADMIT] REFUSE 证据文件不存在: %s' % ev)
            return 1
        # r133 修真 bug：`--register` 收的键与检查时的文件名形态不一致
        # （我传 r133_new_skill_ingress，文件名是 r133_new_skill_ingress.py）
        # ⇒ 登记写了、检查永远不命中 ⇒ 报 UNDECLARED。r131 那次同症状被我误判成「并行会话干扰」，
        # 这次抓到根：键必须**归一到带 .py 的文件名形态**。
        key = args.register if args.register.endswith('.py') else (args.register + '.py')
        reg[key] = {'evidence': ev, 'registered_at': __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}
        with io.open(reg_path, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(reg, f, ensure_ascii=False, indent=1)
        print('[ADMIT] REGISTERED %s（证据 %s）' % (key, ev))
        return 0
    qsrc = io.open(QUARTERLY, encoding='utf-8').read() if os.path.isfile(QUARTERLY) else ''
    quarterly = set(m.group(1) for m in re.finditer(r'"(r\d+_[A-Za-z0-9_]+\.py)"', qsrc))
    print('[ADMIT] runner 已登记门脚本 %d 个 / 季度巡检已登记 %d 个' % (len(registered), len(quarterly)))
    scripts = sorted(f for f in os.listdir(HERE) if f.endswith('.py'))
    # 只检 git log 近 N 次提交里出现的脚本（新增面）
    try:
        import subprocess
        # r129 四修（本仓 git 版本下 --pretty=format: 仍回吐全部文件名，-n 与 --pretty 不同时生效；
        # 改用 `--format=`（空格式串）才真正只取近 N 次提交的文件名）
        # r163 修（分母口径 bug，X-24 同族）：本门自述只检「最近 N 轮**新增**的判据」，但 --name-only
        #   不带 --diff-filter 会把近 4 次提交里**被修改的历史件**一并拉进「新增面」⇒ 改一个 2026-09-24
        #   入库的老脚本也要它「首次入册」。实测触发：r163d 只给 17 个历史件换 gh 调用形态，
        #   本门即报 8 条 UNDECLARED（其首次入库提交 ef411af/78d9eb4/b71857f/73c2344/
        #   27664b4/effe8c2/8f88c50 全是 9 月历史件）。修法 = 取新增(A) 而非「碰过」；
        #   未跟踪面另算（r129 六修守的「刚写完未入库」窗口不受影响）。
        _g = subprocess.run(['git', 'log', '-n', '4', '--name-only', '--diff-filter=A',
                           '--format=', '--', '05-exec/'],
                           cwd=ROOT, capture_output=True, text=True, encoding='utf-8',
                           errors='replace', timeout=120)
        recent = set()
        for ln in (_g.stdout or '').splitlines():
            ln = ln.strip()
            if ln.startswith('05-exec/') and ln.endswith('.py'):
                recent.add(os.path.basename(ln))
    except Exception as _e:
        # r129 自抓：静默降级会把判据面悄悄放大（首版就是这么假红的）。
        # 降级必须**响亮**：打印原因，并按「取不到新增面 ⇒ 判 UNVERIFIED」处理，
        # 而不是悄悄扫全仓（R247：取不到真相源不得当作通过）。
        print('[ADMIT] UNVERIFIED 取不到新增面（git 调用失败: %r）' % (_e,))
        print('[ADMIT] 禁止降级为全仓扫描 —— 那会让判据面意外放大并稳定产出假红')
        if args.out:
            with io.open(args.out, 'w', encoding='utf-8', newline='\n') as fh:
                json.dump({'schema': 'reconcile-admission-r129-v1',
                           'state': 'UNVERIFIED',
                           'why': 'git log 调用失败：%r' % (_e,)},
                          fh, ensure_ascii=False, indent=1)
        return 2
    # r129 六修（反向验证抓到的缺口）：判据只看 git log 近 N 次提交 ⇒ **未提交的新脚本查不到**，
    # 而未提交正是「刚写完、还没进 GATES 表」这个最该卡的窗口（实测：造一个未跟踪的判据脚本，
    # 判据读数仍是 0 条 ⇒ 假绿）。修法 = 新增面 = git log 近 N 次 ∪ **未跟踪的 .py**。
    try:
        import subprocess as _sp
        _u = _sp.run(['git', 'ls-files', '--others', '--exclude-standard', '05-exec/'],
                     cwd=ROOT, capture_output=True, text=True, encoding='utf-8',
                     errors='replace', timeout=120)
        untracked = set(os.path.basename(l.strip()) for l in (_u.stdout or '').splitlines()
                        if l.strip().endswith('.py'))
    except Exception:
        untracked = set()
    recent = recent | untracked
    print('[ADMIT] 新增面 = git 近 4 次提交**新增(A)** %d 个 ∪ 未跟踪 %d 个（被修改的历史件不入面）'
          % (len(recent) - len(untracked), len(untracked)))
    exempt = re.compile('|'.join(EXEMPT_PATTERNS))
    unregistered = []
    examined = 0
    for f in scripts:
        if f not in recent:
            continue
        if f in registered:
            continue
        if f in quarterly:
            continue
        if exempt.search(f):
            continue
        if f in reg or (f[:-3] in reg if f.endswith('.py') else False):
            continue
        try:
            src = io.open(os.path.join(HERE, f), encoding='utf-8').read()
        except Exception:
            continue
        examined += 1
        if looks_like_producer(src):
            unregistered.append(f)
    doc = {'schema': 'reconcile-admission-r129-v1',
           'cmd': 'python 05-exec/r129_reconcile_admission.py --json <out>',
           'registered_gates_n': len(registered),
           'scripts_n': len(scripts),
           'examined_n': examined,
           'unregistered_producers': unregistered,
           'unregistered_n': len(unregistered)}
    if args.out:
        with io.open(args.out, 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(doc, fh, ensure_ascii=False, indent=1)
    print('[ADMIT] 脚本 %d / 已登记 %d / 受检 %d / 未声明的产读数脚本 %d'
          % (len(scripts), len(registered), examined, len(unregistered)))
    for f in unregistered:
        print('  UNDECLARED %s' % f)
    if args.out:
        print('[ADMIT] JSON -> %s' % args.out)
    return 1 if unregistered else 0


if __name__ == '__main__':
    raise SystemExit(main())