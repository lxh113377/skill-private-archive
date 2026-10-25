# -*- coding: utf-8 -*-
# r199_struct_recount.py - 复算本报告结构：重复二级标题 / 标题粘连 / 交付物锚数。
#
# 存在理由（r199 一手）：我用 t.replace(anchor, add + anchor) 未传 count，而「## 9. 交付物」
# 在文中有多个出现点，结果把 §34 整节复制成 18 份、锚也变 18 个。此后连续 10 轮全绿通过 ——
# md_claim_face 只管「数字有没有挂取值命令」，没有任何判据管「标题有没有被复制」。
# 本件把那件事变成可复算读数，并作为第 74 门 struct_recount_face 挂进门表（portable=True，
# CI 同轮也跑）：再复制出重复标题，本地与 CI 一起红。
#
# 粘连口径（两版之间被实测纠正过一次）：
#   ① 真损坏（L1614）形态是「正文或引用行里 全角句号紧跟 ## 标题」⇒ 必须计数，引用行也算；
#   ② 但 §41.5 用行内代码**举例**该形态时，匹配落在 code span 内 ⇒ 属误伤，须排除。
#   排除只针对代码语境（行内 code span / fenced 块 / 缩进块），正文粘连一律照抓 ——
#   这是精化不是放宽；夹具用变异腿锁住「关掉排除即误报、关掉检测即漏报」两面。
import collections
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
P = os.path.join(ROOT, '06-benchmark',
                 '全量对标报告_r163_免费工具可达性对账与gh空壳遮蔽_2026-10-22.md')
DOT = chr(12290)      # 全角句号
ANCHOR = '## 9. 交付物'
BT = chr(96)          # 反引号
FENCE = BT * 3
LEGIT_DUP = {'3'}     # ## 3. 与 ## 3b. 是两节，非复制


def code_span_mask(line):
    mask = [False] * len(line)
    delims = [i for i, c in enumerate(line) if c == BT]
    groups = []
    i = 0
    while i < len(delims):
        j = i
        while j + 1 < len(delims) and delims[j + 1] == delims[i] + 1:
            j += 1
        groups.append((delims[i], j - i + 1))
        i = j + 1
    k = 0
    while k < len(groups):
        start, ln = groups[k]
        m = k + 1
        while m < len(groups) and groups[m][1] != ln:
            m += 1
        if m >= len(groups):
            break
        end = groups[m][0]
        for x in range(start + ln, end):
            mask[x] = True
        k = m + 1
    return mask


def glued_count(lines, honor_code=True):
    n = 0
    in_fence = False
    pat = re.compile(DOT + '## [0-9]')
    for l in lines:
        st = l.strip()
        if st.startswith(FENCE):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if l.startswith('    ') or l.startswith(chr(9)):
            continue
        if st.startswith('##'):
            continue
        # 必须遍历该行**全部**匹配：只用 search() 取第一个，会在「同行先有行内代码举例、
        # 后有正文真粘连」时把真损坏一起吞掉 —— 夹具 t8（r199）正是这样抓出这个漏检的。
        mask = code_span_mask(l)
        for mm in pat.finditer(l):
            if honor_code and mask[mm.start()]:
                continue
            n += 1
    return n


def recount(text, honor_code=True):
    lines = text.split(chr(10))
    heads = []
    for l in lines:
        # r246 修（我自己的判据缺陷）：原来只吃 1–2 位数字 ⇒ `## 100.` 被截成「10」，与既有的
        #   `## 10.` 撞成「重复标题」而判红（实测：报告加第 100 节后本门 FAIL，报「二级标题 10 出现 2 次」）。
        #   本门目的是抓**被复制**的标题；100 与 10 不是复制。加宽到 1–4 位（真复制照旧判红，夹具补正反例）。
        mm = re.match('^## ([0-9]{1,4})[a-z]?', l)
        if mm:
            heads.append(mm.group(1))
    dup = {k: v for k, v in collections.Counter(heads).items() if v > 1}
    anchors = sum(1 for l in lines if l.strip() == ANCHOR)
    return {'lines': len(lines), 'bytes': len(text), 'anchors': anchors,
            'dup_heads': dup, 'glued': glued_count(lines, honor_code),
            'head_count': len(heads)}


def findings(r):
    bad = []
    if r['anchors'] != 1:
        bad.append('交付物锚应为 1，实为 %d（replace 无 count 的复制痕迹）' % r['anchors'])
    if r['glued']:
        bad.append('有 %d 处二级标题粘在正文行尾（写后自检漏判）' % r['glued'])
    for k, v in sorted(r['dup_heads'].items()):
        if k not in LEGIT_DUP:
            bad.append('二级标题 %s 出现 %d 次（非人工分节）' % (k, v))
    return bad


def main():
    if not os.path.isfile(P):
        print('[STRUCT:FAIL] 报告文件不存在：%s' % P)
        return 1
    r = recount(io.open(P, encoding='utf-8').read())
    print('=== 报告结构复算（r199）===')
    print('  行数=%d ｜字节=%d ｜二级标题=%d 个 ｜交付物锚=%d' % (
        r['lines'], r['bytes'], r['head_count'], r['anchors']))
    print('  重复标题=%s ｜粘连标题=%d' % (r['dup_heads'] or '(无)', r['glued']))
    bad = findings(r)
    for b in bad:
        print('  [STRUCT:FAIL] %s' % b)
    if bad:
        return 1
    print('  [STRUCT:PASS] 交付物锚唯一、无粘连、无异常重复标题')
    return 0


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
    sys.exit(main())