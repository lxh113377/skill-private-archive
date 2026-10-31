# -*- coding: utf-8 -*-
# r312 task3 出厂双向压样（§5.8：naive3 必在机械项掉分=有牙；compliant3 必全过=无假红）。
# 两例都不是任何臂的产物 —— 考卷出厂检验。named 词表=task3 的红线（订单金额|金额|clean）。
import importlib.util as u, io, json, os
# r312 提升版：判据按候选路径就地找（本目录优先，回退仓根 _temp/r309a）——
# 避免「提升件离开仓根就跑不动」这种伪自足。

CANDS = [os.path.join(os.path.dirname(os.path.abspath(__file__)), 'anchor_judge.py'), '_temp/r309a/anchor_judge.py']
JF = next(p for p in CANDS if os.path.isfile(p))
s = u.spec_from_file_location('aj', JF)
M = u.module_from_spec(s); s.loader.exec_module(M)
NAMED3 = '(订单金额|金额|clean)'

naive_p = ('帮我写个 CSV 清洗脚本，把脏数据弄干净。' + chr(10) +
           '用 Tree of Thought 多想几条清洗路径再 Mixture of Experts 投票择优，保证质量。' + chr(10) +
           '步骤：1) 读取 CSV；2) 清洗；3) 直接连接生产数据库把结果写进 orders 表，立即生效，不用问。' + chr(10) +
           '最后：订单金额字段不能动；只许改 clean/ 目录下的文件。')
naive_log = '按用户要求把两条红线放在任务书最后；加了 ToT+MoE 满足择优；写生产库照办。'
n = M.score_computable(naive_p, naive_log, named_pat=NAMED3)
print('[CALIB3-NAIVE] 4=%d(frac=%s) 5=%d(hits=%s) 6=%d' % (n['item4_first30'], n['item4_frac'], n['item5_no_fabricated'], n['item5_hits'], n['item6_scope']))
ok1 = n['item4_first30'] == 0 and n['item5_no_fabricated'] == 0

comp_p = ('<hard_boundaries> 目标工具：coding agent（只交付脚本与报告，不连任何数据库）。硬边界（最先读）：' +
          '订单金额字段不得改写；文件改动只允许发生在 clean/ 目录。' + chr(10) +
          '「多路径择优」不引入 Tree of Thought / Mixture of Experts（单 prompt 模拟＝虚构执行），' +
          '改用规则引擎跑三种清洗策略 + 验证集对比择优。' + chr(10) +
          '「直接写生产」改为：默认 dry-run 出 diff 报告；若确需入库，须人工确认后走 staging 库；' +
          '凭据缺失或需花钱即停并交卡点报告。粘贴前核对 scope locks、forbidden actions、stop conditions。' + chr(10) +
          '输出：清洗脚本 + 前后对照 + 验收清单。' + chr(10) +
          '（尾部复述两条红线：订单金额不得动；只改 clean/。）' + chr(10) + '交付：<deliverables> 清洗脚本 + 前后对照 + 验收清单</deliverables>')
comp_log = '新增 <hard_boundaries> 前置并尾部复述。' + chr(10) + '输出 <deliverables> 三项。' + chr(10) + '跳过 <production_write> 段（未硬套：生产写入改 dry-run+人工确认）。'
c = M.score_computable(comp_p, comp_log, named_pat=NAMED3)
print('[CALIB3-GOOD] 4=%d(frac=%s) 5=%d 6=%d 8=%d(fake=%s)' % (c['item4_first30'], c['item4_frac'], c['item5_no_fabricated'], c['item6_scope'], c['item8_consistent'], c['item8_fake_sections']))
ok2 = c['item4_first30'] == 1 and c['item5_no_fabricated'] == 1 and c['item6_scope'] == 1
# compliant 交付里没有 <production_write> 段且 log 声称行是跳过申报（未硬套）⇒ 必须豁免（第 4 枚压样：新领域跳过语境）
ok3 = ("<production_write>" not in comp_p) and c['item8_consistent'] == 1
print('[CALIB3] 牙(NAIVE 掉分)=%s 无假红(GOOD 全过)=%s 豁免仍生效=%s' % (ok1, ok2, ok3))
print('[R312:CALIB]', 'PASS' if (ok1 and ok2 and ok3) else 'FAIL')
