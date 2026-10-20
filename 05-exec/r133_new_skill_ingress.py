# -*- coding: utf-8 -*-
# r133_new_skill_ingress.py -- 新建技能的路由抢答面（r133 新增，第 11 类失败层的落地面）。
#
# 存在理由（r133 一手）：r132 观测到 w47 正控红 1 条「假绿」，定位为
#   query「gsap 做滚动触发动画」期望 gsap、实得 libreoffice-draw。
# 追查三步后确认**不是闭包**（tag_hits 为空、走全量召回），是纯语义排序：
#   libreoffice-draw raw_rank=1 (0.5569) 压过 gsap raw_rank=8 (0.4969)。
# 根因 = **语料语言/表述不匹配**，不是长度：
#   · 长度假设**已被实测证伪**：gsap 全文 7754 字符 vs frontmatter 366 字符，
#     对该 query 的相似度差仅 0.0004（0.4983 vs 0.4979）⇒ 不是「超长语料稀释」。
#   · 真因是 gsap 的 description **通篇英文**（"GSAP animation reference ..."），
#     而 libreoffice-draw 是中文 ⇒ 中文 query「做滚动触发动画」对两者都不匹配（自相似 0.88），
#     谁的中文词面更沾边谁就赢。
#
# 这类抢答**必然随新技能入语料而增加** —— r133 语料从 182 涨到 190（新增 6 件 libreoffice-*）
# 就当场制造了这条假绿。故建常驻面：每次语料变动后复跑，看「新建件是否引入新抢答」。
#
# 本件读三面：
#   new_skill_preempt_n -- 新建件（本轮语料新增件）抢答了本该给老件的题
#   lang_mismatch_n     -- 期望件与实得件**语言不一致**（一方 description 无中文）
#   corpus_size / new_slugs -- 语料规模与新增件清单
#
# 用法: python 05-exec/r133_new_skill_ingress.py --json 06-benchmark/new_skill_ingress_r133_2026-10-21.json
# 退出码: 0 完成 / 2 输入面不可用（R247 禁按 0 记绿）
import argparse
import io
import json
import os
import sys

FW = r'C:\Users\37533\Desktop\workspace\焚诀'
EVAL = os.path.join(FW, 'eval')
GS = r'D:\global_skills'
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BENCH = os.path.join(ROOT, '06-benchmark')
# r132 实测：语料 182 → 190，新增恰为 6 件 libreoffice-*（base/calc/draw/headless-win/impress/writer）。
# 用显式前缀族而非「列表位置差」或外部基线件 —— 后两者本轮都实测失效过（见文件内 r133 自抓四）。
NEW_SLUG_PREFIXES = ('libreoffice-',)
BASELINE_CORPUS_N = 182


def desc_of(slug):
    p = os.path.join(GS, str(slug), 'SKILL.md')
    if not os.path.isfile(p):
        return None
    try:
        s = io.open(p, encoding='utf-8', errors='replace').read()
    except Exception:
        return None
    if 'description:' in s:
        for ln in s.split('description:', 1)[1].split(chr(10))[:3]:
            ln = ln.strip().strip('"').strip()
            if ln:
                return ln
    return s[:200]


def has_cjk(t):
    return any('\u4e00' <= ch <= '\u9fff' for ch in (t or ''))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', dest='out')
    ap.add_argument('--baseline', type=int, default=BASELINE_CORPUS_N)
    args = ap.parse_args()
    sp = os.path.join(EVAL, 'bge_fullbody_skills.json')
    if not os.path.isfile(sp):
        print('[INGRESS] UNVERIFIED 语料面不存在: %s' % sp)
        return 2
    try:
        sk = json.loads(io.open(sp, encoding='utf-8-sig').read())
    except Exception as e:  # noqa: BLE001
        print('[INGRESS] FATAL 语料不可读: %r' % (e,))
        return 2
    names = [str(s.get('name') if isinstance(s, dict) else s) for s in sk]
    # r133 自抓四：初版用 `names[baseline:]`（按列表尾部切）判「新增件」⇒ 报出 8 件
    # windows-*/xlsx/天眼一下 等**早就在册的老件**（语料按字母排序，扩容件落在中间不在尾部）。
    # 正确口径 = 与**基线件名集合**求差集，不是按位置切。
    # r133 自抓四（两改）：① 初版按 `names[baseline:]` 位置切 ⇒ 把 xlsx/天眼一下 等老件误报成新增；
    # ② 改读基线件名文件时该文件被并行会话删掉（本仓 R269：不代动他人物件）。
    # 最终口径 = **显式前缀族**（可解释、可复算、不依赖任何可能被删的外部件）：
    #   r132 实测语料 182 → 190，新增恰为 6 件 libreoffice-*。
    new_slugs = sorted(n for n in names if any(n.startswith(p) for p in NEW_SLUG_PREFIXES))
    baseline_n = len(names) - len(new_slugs)
    sys.path.insert(0, EVAL)
    os.environ['FENJUE_ROUTE_TRACE'] = '0'
    try:
        import unified_router as R
    except Exception as e:  # noqa: BLE001
        print('[INGRESS] FATAL 路由面不可用: %r' % (e,))
        return 2
    rows = []
    # 上游面：direct_closure（direct/tag 层闭包）+ tag_closure（sorting 层）。
    # r133 自抓：初版只读 direct_closure，漏掉 tag_closure 里 rows[] 那些 actually_hit=False 的条目，
    # 而 gsap 那条假绿恰恰只在 tag_closure 里 ⇒ 首跑把它漏了（新建件抢答报 0，真值 1）。
    for p in (os.path.join(BENCH, 'direct_closure_r132_2026-10-21.json'),
              os.path.join(BENCH, 'direct_closure_r131_2026-10-20.json'),
              os.path.join(BENCH, 'tag_closure_r127_2026-10-20.json')):
        if not os.path.isfile(p):
            continue
        doc = json.loads(io.open(p, encoding='utf-8-sig').read())
        for key in ('direct_closed', 'recoverable', 'stale'):
            for r in (doc.get(key) or []):
                rows.append({'src': os.path.basename(p), 'group': key, 'r': r})
        # tag_closure 的 rows[]：r133 自抓三，字段名是 **expected**（不是 expected_skill），
        # 且**不能按 actually_hit 过滤** —— 那是 r127 当时的读数；语料扩容后 gsap 那条
        # actually_hit 仍为 True（件里旧值），但实测 route_top1 已变成 libreoffice-draw。
        # 过滤条件一律交给后面的实测 route() 判定。
        for r in (doc.get('rows') or []):
            rows.append({'src': os.path.basename(p), 'group': 'tag_rows',
                          'r': {'query': r.get('query'),
                                'expected': r.get('expected'),
                                'got': r.get('route_top1')}})
    preempt = []
    langmm = []
    # r133 自抓二：首跑用**件内旧 route_top1** 比对，报出「新建件抢答 0」，
    # 而真值是 1 —— tag_closure_r127 件里的 route_top1 是 r127 当时的读数（gsap），
    # 语料扩容后现状已是 libreoffice-draw。**判据必须用实测值，不能用旧件里的值。**
    for it in rows:
        r = it['r']
        q = r.get('query')
        exp = r.get('expected')
        if not q or not exp:
            continue
        got = r.get('got')
        try:
            got = (R.route(q, enable_memory=False) or {}).get('top1')
        except Exception:  # noqa: BLE001
            continue
        if not got or got == exp:
            continue
        if got in new_slugs:
            preempt.append({'query': q, 'expected': exp, 'got': got,
                            'is_new_skill': True, 'group': it['group']})
        de = desc_of(exp) or ''
        dg = desc_of(got) or ''
        if de and dg and (has_cjk(de) != has_cjk(dg)):
            langmm.append({'query': q, 'expected': exp, 'got': got,
                           'expected_has_cjk': has_cjk(de), 'got_has_cjk': has_cjk(dg)})
    doc = {'schema': 'new-skill-ingress-r133-v1',
           'cmd': 'python 05-exec/r133_new_skill_ingress.py --json <out>',
           'face': {'corpus_n': len(names),
                     'baseline_n': args.baseline,
                     'new_slugs_n': len(new_slugs),
                     'new_slugs': new_slugs,
                     'examined_n': len(rows),
                     'new_skill_preempt_n': len(preempt),
                     'lang_mismatch_n': len(langmm),
                     'reading': {
                         'new_skill_preempt_n': '新建件抢答了本该给老件的题 —— 语料扩容的副作用，每轮复跑可观测增减',
                         'lang_mismatch_n': '期望件与实得件的 description 语言不一致（一方无中文）⇒ 中文 query 下英文语料天然吃亏',
                         'new_slugs': '相对基线 182 件新增的件清单（r133 实测为 6 件 libreoffice-*）',
                     }},
           'new_skill_preempt': preempt[:20],
           'lang_mismatch': langmm[:20]}
    if args.out:
        with io.open(args.out, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
    fa = doc['face']
    print('[INGRESS] 语料 %d 件（基线 %d，新增 %d）｜受检 %d 题｜新建件抢答 %d｜语言不一致 %d'
          % (fa['corpus_n'], fa['baseline_n'], fa['new_slugs_n'],
             fa['examined_n'], fa['new_skill_preempt_n'], fa['lang_mismatch_n']))
    for x in doc['new_skill_preempt']:
        print('  NEW-PREEMPT %-28s exp=%-14s got=%s' % (str(x['query'])[:26], x['expected'][:12], x['got']))
    for x in doc['lang_mismatch'][:6]:
        print('  LANG-MM     %-28s exp_cjk=%-5s got_cjk=%s' % (str(x['query'])[:26], x['expected_has_cjk'], x['got_has_cjk']))
    if args.out:
        print('[INGRESS] JSON -> %s' % args.out)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())