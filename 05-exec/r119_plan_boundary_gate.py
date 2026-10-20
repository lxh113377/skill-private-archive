# -*- coding: utf-8 -*-
r'''r119_plan_boundary_gate.py -- 迁移方案必须承载「换装影响量」硬边界（r118 S-3 落地的机器门）。

r119b 改名记录：原文件名 r119_migration_guard.py 命中 A-project-handoff noise_lint 的
MIGRATION_NAME（`migration_`）二级扫描规则 ⇒ 被当作「迁移产物」判 VIOL。该件是**有意提交的
常驻门脚本**，不是迁移产物 ⇒ 按「修接线不改判据」改名（禁为凑绿去放宽 noise_lint，X-9 同族）。

存在理由：
  r118 实测换装对生产路由影响 0（47 变体），并立了硬边界 W-1：任何替换不得以「提升任务质量」
  为理由，除非先复跑 r118_swap_sim.py 给出该件专属正向 delta。但**那条边界只活在报告与方案的
  散文里** —— 没有任何判据在看「方案还在不在说这件事」。r119 把 W-1 从散文升级为结构判据：
  · 迁移方案必须含 W-1 段落（四个机器可查 token 全在）；
  · 方案必须含 r119 的实测加注（把 0 影响从「当时实测」更新为「当前复算仍成立」）；
  · 判据自身三态：缺 token ⇒ FAIL；文件缺失 ⇒ rc=2（UNVERIFIED，禁当绿）。

反「判据写完就宣布有效」（X-18）：本件自带正/反两向自证（--selftest），
  正例 = 现件（应 PASS）；反例 = 摘掉任一 token 的临时副本（应 FAIL）。零输入 ⇒ rc=2。
'''
import io
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PLAN = os.path.join(ROOT, '04-plan', '迁移替换方案_r114_2026-10-18.md')

# W-1 的四个机器可查 token（缺任一即判红：说明那条硬边界已从方案里消失）
REQUIRED_TOKENS = [
    'W-1',
    'r118_swap_sim.py',
    '正向 delta',
    '短路先于召回',
]
# r119 复算加注的 token（方案必须把 0 影响更新到「当前复算」而不停留在 r118 当时态）
REQUIRED_R119 = ['r119']


def check_text(text):
    """返回 (missing_w1, missing_r119)。空串 ⇒ 全部缺失（禁静默判过）。"""
    miss_w1 = [t for t in REQUIRED_TOKENS if t not in text]
    miss_r119 = [t for t in REQUIRED_R119 if t not in text]
    return miss_w1, miss_r119


def selftest():
    """双向自证（W-47）：正例现件应 PASS；反例（摘 token）应 FAIL。"""
    ok = True
    if not os.path.exists(PLAN):
        print('[SELFTEST] UNVERIFIED 方案件缺失: %s' % PLAN)
        return 2
    with io.open(PLAN, encoding='utf-8') as f:
        text = f.read()
    miss_w1, miss_r119 = check_text(text)
    if miss_w1 or miss_r119:
        print('[SELFTEST] FAIL 正例（现件）就缺 token: w1=%s r119=%s' % (miss_w1, miss_r119))
        ok = False
    else:
        print('[SELFTEST] PASS 正例：现件含 W-1 四 token + r119 加注')
    # 反例：把该 token 的**全部**出现从副本里摘掉 ⇒ 必须被抓住
    # （r119 自抓：首版只 replace 第一次，而 'W-1' 在方案里出现多次 ⇒ 反例照样绿，
    #   是夹具自己假鉴别力，不是判据有效 —— W-47「应红的红」必须真红）
    tok = REQUIRED_TOKENS[0]
    broken = text.replace(tok, 'XX_REMOVED_XX')
    b_w1, _ = check_text(broken)
    if tok in b_w1:
        print('[SELFTEST] PASS 反例：摘掉全部 %r 后本门判红（鉴别力成立）' % tok)
    else:
        print('[SELFTEST] FAIL 反例：摘掉全部 %r 后仍判绿 ⇒ 本门无鉴别力' % tok)
        ok = False
    print('[SELFTEST] %s' % ('PASS' if ok else 'FAIL'))
    return 0 if ok else 1


def main():
    if '--selftest' in sys.argv:
        return selftest()
    if not os.path.exists(PLAN):
        print('[MIGGUARD] UNVERIFIED 方案件缺失（禁当绿）: %s' % PLAN)
        return 2
    with io.open(PLAN, encoding='utf-8') as f:
        text = f.read()
    if not text.strip():
        print('[MIGGUARD] UNVERIFIED 方案件为空（禁当绿）')
        return 2
    miss_w1, miss_r119 = check_text(text)
    if miss_w1:
        print('[MIGGUARD:FAIL] 迁移方案缺 W-1 token: %s' % miss_w1)
        return 1
    if miss_r119:
        print('[MIGGUARD:FAIL] 迁移方案缺 r119 复算加注: %s' % miss_r119)
        return 1
    print('[MIGGUARD:PASS] W-1 四 token 在场 + r119 加注在场')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())