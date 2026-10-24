# -*- coding: utf-8 -*-
'''r215_gate_check.py — 触点点名的「本仓判据件」核验（r216 新增第四类可证伪面）。

r215 收尾时名册仍有 5 行标「纯散文不可证伪」：SQLite / VS Code / Turnstile / Resend / Upstash。
原因是它们的触点引用的是**本仓判据件**（r196_quota_face、r199_workers_face、r203_ledger_index、
r163 probe_vscode 等），而 r215_claim_check 只扫 D:/global_skills 下的 skill 目录 ⇒ 认不出来。

强度上限（与 r215 v3 同样的自律）：本模块只能证「该判据件在位、且其文本提到该工具」，
**不能证「该工具已接入工作流」**。探针在位与接入是两件事（Resend/Upstash 就是典型：
探针在位、凭据缺、未接入）。所以产物措辞固定为「判据件在位」，不得写成「已接入」。

三态：GATE_FILE_MENTIONS（在位且提到）/ GATE_FILE_SILENT（在位但没提到 ⇒ 强反证）/
NO_SUCH_FILE（点名了不存在的件 ⇒ 强反证）；无关键词一律 NO_PATTERN，不折算通过（R247）。
'''
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
_CACHE = {}
_NAMES = None


def stems():
    global _NAMES
    if _NAMES is None:
        try:
            _NAMES = sorted(f[:-3] for f in os.listdir(HERE) if f.endswith('.py'))
        except OSError:
            _NAMES = []
    return _NAMES


def _text(stem):
    if stem in _CACHE:
        return _CACHE[stem]
    p = os.path.join(HERE, stem + '.py')
    t = None
    if os.path.isfile(p):
        try:
            t = io.open(p, encoding='utf-8', errors='replace').read().lower()
        except OSError:
            t = None
    _CACHE[stem] = t
    return t


def verify(stem, pats):
    t = _text(stem)
    if t is None:
        return 'NO_SUCH_FILE'
    if not pats:
        return 'NO_PATTERN'
    return ('GATE_FILE_MENTIONS'
            if any(re.search(x, t, re.I) for x in pats) else 'GATE_FILE_SILENT')


def claims_for(text, pats):
    low = (text or '').lower()
    out = []
    for s in stems():
        if len(s) >= 8 and s.lower() in low:
            out.append({'gate_file': s, 'verdict': verify(s, pats)})
    return out