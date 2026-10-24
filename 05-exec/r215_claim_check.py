# -*- coding: utf-8 -*-
'''r215_claim_check.py — 触点断言的**下限**核验（r215，两次自我修正后的诚实版）。

演进（全部有据，写在台账 R215-2）：
  v1 触点栏是手写散文，全 (no ref) —— 没人能证伪我写的话；
  v2 加「skill 目录里 .md 是否命中该工具关键词」当核验，反证发现自己**咬不住错断言**：
     故意把 GitHub 的承载件写成 chaoshi-image-optimization，仍判通过 —— 因为中文技能正文
     里出现 github / actions 字样近乎恒真。「提到过」不等于「职责归它」。
  v3（本件）不假装能判对错，只把强度如实分级：
     IN_SKILL_DESC  该工具关键词出现在它的 SKILL.md description/标题层（职责声明层）
     MENTIONS       只在正文其它 .md 里被提到（弱证据，常见于顺带举例）
     NOT_MENTIONED  整个 skill 目录都没提到 —— 触点若声称它承载，即为强反证
     SKILL_ABSENT / NO_PATTERN  输入不可得，一律不折算成通过（R247）
  消费方必须按此上限措辞：写「提及核验」，不写「承载已证」。
'''
import io
import os
import re

GS = 'D:/global_skills'
SKIP_DIRS = ('__pycache__', '.git', '_bak')
_ALL = {}
_DESC = {}


def all_skills():
    try:
        return sorted(d for d in os.listdir(GS)
                    if os.path.isdir(os.path.join(GS, d)) and d not in SKIP_DIRS)
    except OSError:
        return []


def _texts(skill):
    if skill in _ALL:
        return _ALL[skill]
    root = os.path.join(GS, skill)
    if not os.path.isdir(root):
        _ALL[skill] = None
        _DESC[skill] = None
        return None
    buf = []
    desc = []
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in SKIP_DIRS]
        for f in fns:
            if f.endswith('.md'):
                try:
                    t = io.open(os.path.join(dp, f), encoding='utf-8',
                                errors='replace').read()
                except OSError:
                    continue
                buf.append(t.lower())
                if f == 'SKILL.md':
                    m = re.search(r'^description:\s*(.+)', t, re.M)
                    h = re.findall(r'^#{1,3}\s+(.+)$', t, re.M)
                    if m:
                        desc.append(m.group(1).lower())
                    desc.extend(x.lower() for x in h)
    _ALL[skill] = chr(10).join(buf)
    _DESC[skill] = chr(10).join(desc)
    return _ALL[skill]


def verify(skill, pats):
    t = _texts(skill)
    if t is None:
        return 'SKILL_ABSENT'
    if not pats:
        return 'NO_PATTERN'
    d = _DESC.get(skill) or ''
    if any(re.search(x, d, re.I) for x in pats):
        return 'IN_SKILL_DESC'
    if any(re.search(x, t, re.I) for x in pats):
        return 'MENTIONS'
    return 'NOT_MENTIONED'


def claims_for(text, pats, skills):
    low = (text or '').lower()
    out = []
    for sk in skills:
        if sk.lower() in low:
            out.append({'skill': sk, 'verdict': verify(sk, pats)})
    return out