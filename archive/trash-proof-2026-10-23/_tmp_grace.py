# -*- coding: utf-8 -*-
# 验 grace_for：标题段优先 / 无标题段退全文 / R194-2 自身不再被【P0 引用劫持
import sys
sys.path.insert(0, '05-exec')
import importlib
m = importlib.import_module('r38_debt_aging')
C = chr(65306)
cases = [
    ('P0 老式方括号', '- [ ] x' + C + ' 【P0·下轮首推】 正文', 2),
    ('P1 圆括号标题', '- [ ] **R194-1（r194 登记，P1·已落地）**' + C + ' 正文', 4),
    ('P2 圆括号标题', '- [ ] **R193-1（r193 登记，P2·已落地）**' + C + ' 正文', 8),
    ('R194-2 自劫持', '- [ ] **R194-2（r194 登记，P2）**' + C + ' 宽限识别只认「【P0」形态', 8),
    ('无P级', '- [ ] 某待办' + C + ' 无优先级', 2),
    ('标题无冒号整条扫', '- [ ] **R999-1（r999 登记，P1）** 正文', 4),
    ('P2 且正文含 P0 干扰', '- [ ] **R8-1（r8 登记，P2）**' + C + ' 见【P0·旧例】', 8),
]
bad = 0
for name, text, want in cases:
    got = m.grace_for(text)
    ok = (got == want)
    bad += (0 if ok else 1)
    print('  %s %-24s want=%d got=%d %s' % ('OK ' if ok else 'XX ', name, want, got, '' if ok else '<<<'))
print('不符 =', bad)