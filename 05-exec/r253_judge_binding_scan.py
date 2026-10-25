# -*- coding: utf-8 -*-
"""r253_judge_binding_scan.py - 判据绑定扫描：牙里引用的名字必须在该处确实绑定（r253 新建，只读 AST）。

存在理由（r253 一手，把 r252 的教训机械化）：r251 加的牙 r10 是空转的假绿 —— 它在 main() 求值却去够
  build() 的局部变量 src ⇒ NameError，而外包的 try/except Exception 把错误吞掉 ⇒ 集合恒空 ⇒ 永远 PASS。
  教训是「一条牙全过不算证据，必须能证明它真在执行」；本件把这句话变成可复跑的判据：

  判据 A（绑定）：凡 teeth_*.append(...) 里出现的 Name，必须在同一函数内、该行之前已绑定
    （赋值 / for 目标 / with as / except as / 导入 / 函数定义 / 参数 / 推导式目标 / 模块级全局 / 内建）。
  判据 B（吞异常）：若该 append 位于某个 try 体内，而该 try 的 except 体是 pass / 赋空容器 / continue，
    则未绑定会被静默吞成默认值 ⇒ 标 SILENT（最危险的一类）。

三态：无问题 ⇒ PASS(0)；有问题 ⇒ FAIL(1) 逐条 file:line 具名；不可析/无被扫件 ⇒ UNVERIFIED(2)。
用法: python 05-exec/r253_judge_binding_scan.py [--json <件>] [--file <额外被扫件，可多次>]
"""
import argparse
import ast
import builtins
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DEFAULT = ['r215_free_tool_roster.py', 'r237_roster_audit.py', 'r250_source_freshness_scan.py',
           'r199_struct_recount.py', 'r247_dup_policy_scan.py']


def _targets(node):
    out = set()
    if isinstance(node, ast.Name):
        out.add(node.id)
    elif isinstance(node, (ast.Tuple, ast.List)):
        for e in node.elts:
            out |= _targets(e)
    elif isinstance(node, ast.Starred):
        out |= _targets(node.value)
    return out


def _module_names(tree):
    out = set()
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for tg in node.targets:
                out |= _targets(tg)
        elif isinstance(node, ast.AnnAssign):
            out |= _targets(node.target)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            out.add(node.name)
        elif isinstance(node, ast.Import):
            for a in node.names:
                out.add((a.asname or a.name).split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            for a in node.names:
                out.add(a.asname or a.name)
    return out


def _bindings_in(stmts):
    '''收集一组语句里**任何位置**绑定的名字（r253 自抓：首版只认赋值，漏了 try 体内的 import 与推导式目标
    ⇒ 对 r215 的 `import json as _json` 与 `next(i for i, l in ...)` 报了两处假阳）。'''
    out = set()
    for st in stmts:
        for n in ast.walk(st):
            if isinstance(n, ast.Assign):
                for tg in n.targets:
                    out |= _targets(tg)
            elif isinstance(n, ast.AnnAssign):
                out |= _targets(n.target)
            elif isinstance(n, (ast.AugAssign, ast.For, ast.comprehension, ast.comprehension)):
                out |= _targets(getattr(n, 'target', None))
            elif isinstance(n, ast.withitem):
                out |= _targets(n.optional_vars)
            elif isinstance(n, ast.ExceptHandler) and n.name:
                out.add(n.name)
            elif isinstance(n, ast.Import):
                for a in n.names:
                    out.add((a.asname or a.name).split('.')[0])
            elif isinstance(n, ast.ImportFrom):
                for a in n.names:
                    out.add(a.asname or a.name)
            elif isinstance(n, ast.NamedExpr):
                out |= _targets(n.target)
            elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                out.add(n.name)
    return out


def _bound_before(func, lineno, module_names, params):
    names = set(module_names) | set(params) | set(dir(builtins))
    for node in ast.walk(func):
        if getattr(node, 'lineno', 10 ** 9) >= lineno:
            continue
        if isinstance(node, ast.Assign):
            for tg in node.targets:
                names |= _targets(tg)
        elif isinstance(node, ast.AnnAssign):
            names |= _targets(node.target)
        elif isinstance(node, (ast.AugAssign, ast.For, ast.comprehension)):
            names |= _targets(getattr(node, 'target', None))
        elif isinstance(node, ast.withitem):
            names |= _targets(node.optional_vars)
        elif isinstance(node, ast.ExceptHandler) and node.name:
            names.add(node.name)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, ast.Import):
            for a in node.names:
                names.add((a.asname or a.name).split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            for a in node.names:
                names.add(a.asname or a.name)
    return names


def _swallowing_try(tree):
    rows = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Try):
            continue
        swallow = False
        _DEFAULT_CALLS = ('set', 'list', 'dict', 'tuple', 'str', 'int', 'float', 'bool')
        for h in node.handlers:
            for st in h.body:
                if isinstance(st, (ast.Pass, ast.Continue)):
                    swallow = True
                elif isinstance(st, ast.Assign) and isinstance(st.value, (ast.List, ast.Tuple, ast.Dict, ast.Set, ast.Constant)):
                    swallow = True
                elif (isinstance(st, ast.Assign) and isinstance(st.value, ast.Call)
                      and isinstance(st.value.func, ast.Name) and st.value.func.id in _DEFAULT_CALLS):
                    # r253 自抓：坏版本的 except 体是 `_ft_gapcred = set()`（**调用**而非字面量）——
                    #   首版只认字面量 ⇒ 没认出这个「吞成默认值」，于是对已知坏版本报 PASS。
                    swallow = True
        if swallow and node.body:
            # r253 自抓：首版 lo 取「try 体首行」，而 Try 节点的 lineno 在它之前 ⇒ 包含判定永远为假。
            #   改为「Try 自己的行 到 其全体（含 finally/orelse/handlers）的最大行」。
            lo = node.lineno
            hi = lo
            for grp in (node.body, node.handlers, node.orelse, node.finalbody):
                for n in grp:
                    hi = max(hi, getattr(n, 'lineno', hi))
                    for sub in ast.walk(n):
                        hi = max(hi, getattr(sub, 'lineno', hi))
            rows.append((lo, hi))
    return rows


def _swallow_unbound(func, tree_mod, params, spans):
    '''判据 B 的主体（r253 自抓）：**吞异常 try 体内的未绑定名** —— 这类错误被 except 吞掉 ⇒ 静默空转。

    为什么必须扩到「try 体」而不是只看 teeth append：r252 那一手就是这样 —— NameError 出在 append
    **之前**的 `try: for _r in (src['roster']...)... except: pass` 里，而 append 的参数本身完全合法。
    （我首版只扫 append 参数 ⇒ 对已知坏版本报 PASS ⇒ 本扫描器自己没牙。）
    '''
    out = []
    for node in ast.walk(func):
        if not isinstance(node, ast.Try):
            continue
        # r253 自抓：区间判定只留一条判据（首版上面那条 any() 的写法把包含判定写反了）。
        in_span = any(lo <= node.lineno <= hi for lo, hi in spans)
        if not in_span:
            continue
        bound = _bound_before(func, node.lineno, tree_mod, params)
        # try 体内自己绑定的名字也算（顺序近似：整体并入，宁漏不误）
        bound |= _bindings_in(node.body)
        used = set()
        for st in node.body:
            for n2 in ast.walk(st):
                if isinstance(n2, ast.Name):
                    used.add(n2.id)
        unbound = sorted(used - bound)
        if unbound:
            out.append({'line': node.lineno, 'in_swallowing_try': True, 'unbound': unbound})
    return out


def scan_file(path):
    text = io.open(path, encoding='utf-8', errors='replace').read()
    tree = ast.parse(text)
    mod = _module_names(tree)
    spans = _swallowing_try(tree)
    problems = []
    for func in [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
        params = set(a.arg for a in func.args.args)
        for node in ast.walk(func):
            if not isinstance(node, ast.Call):
                continue
            f = node.func
            if not isinstance(f, ast.Attribute) or f.attr != 'append':
                continue
            obj = f.value
            if not (isinstance(obj, ast.Name) and obj.id.startswith('teeth')):
                continue
            bound = _bound_before(func, node.lineno, mod, params)
            used = set(n.id for n in ast.walk(node) if isinstance(n, ast.Name))
            unbound = sorted(used - bound)
            if unbound:
                silent = any(lo <= node.lineno <= hi for lo, hi in spans)
                problems.append({'file': os.path.basename(path), 'line': node.lineno,
                                 'teeth': obj.id, 'unbound': unbound,
                                 'silent_by_swallow': silent})
    # 判据 B：吞异常 try 体内的未绑定名（r253 自抓：首版漏了这条 ⇒ 对坏版本报 PASS）
    for func in [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
        params = set(a.arg for a in func.args.args)
        for pr in _swallow_unbound(func, mod, params, spans):
            problems.append({'file': os.path.basename(path), 'line': pr['line'],
                             'teeth': '(吞异常 try 体)', 'unbound': pr['unbound'],
                             'silent_by_swallow': True})
    return problems, len(mod)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', dest='out', default='')
    ap.add_argument('--file', action='append', default=[])
    args = ap.parse_args(argv)
    targets = list(DEFAULT) + list(args.file)
    allp = []
    scanned = []
    for name in targets:
        fp = name if os.path.isabs(name) else os.path.join(HERE, name)
        if not os.path.isfile(fp):
            continue
        try:
            probs, _n = scan_file(fp)
        except SyntaxError as e:
            print('[JUDGEBIND:UNVERIFIED] %s 不可析：%r' % (os.path.basename(fp), e))
            return 2
        except OSError as e:
            print('[JUDGEBIND:UNVERIFIED] %s 读不到：%r' % (os.path.basename(fp), e))
            return 2
        scanned.append(os.path.basename(fp))
        allp.extend(probs)
    if not scanned:
        print('[JUDGEBIND:UNVERIFIED] 一个被扫件都没读到（路径/面变了）⇒ 空面不得判绿')
        return 2
    doc = {'schema': 'judge-binding-scan-v1', 'readonly': True,
           'provenance_cmd': 'python 05-exec/r253_judge_binding_scan.py --json <件>',
           'files': scanned, 'problems': allp,
           'why': '判据 A：teeth_*.append 里的 Name 必须在该行前已绑定；判据 B：位于吞异常 try 内的未绑定会被静默吞成默认值 ⇒ SILENT（r252 的牙 r10 正是此形态）。'}
    if args.out:
        op = args.out if os.path.isabs(args.out) else os.path.join(ROOT, args.out)
        io.open(op, 'w', encoding='utf-8', newline=chr(10)).write(
            json.dumps(doc, ensure_ascii=False, indent=1))
    print('[JUDGEBIND] 扫 %d 件 ｜ 未绑定引用 %d 处' % (len(scanned), len(allp)))
    for pr in allp:
        print('  %s:%d %s 未绑定=%s%s' % (pr['file'], pr['line'], pr['teeth'], pr['unbound'],
                                          '  ← SILENT（吞异常掩盖）' if pr['silent_by_swallow'] else ''))
    if allp:
        print('[JUDGEBIND:FAIL] 有牙引用了未绑定名 ⇒ 该牙要么崩、要么被吞（r252 一手）')
        return 1
    print('[JUDGEBIND:PASS] 被扫各件的牙引用全部绑定在该行之前（无空转/无崩溃引用）')
    return 0


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
    sys.exit(main())