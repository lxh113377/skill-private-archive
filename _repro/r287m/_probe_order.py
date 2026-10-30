# -*- coding: utf-8 -*-
"""_probe_order.py — 实测「先打 SKILL.md 补丁、后建新件」这个错误顺序会判红（死链腿有牙）。

口径：内存重放全补丁 => 把 D 腿的新增件暂存副本从文档面里撤掉（等价于新件没落盘），
再看死链数。全程只读，不写受管根。
"""
import os, sys
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, D)
import check_r287m as C
items = C.load_patch()
orig, work, errs = C.replay(items)
ok1, last1, t1, d1 = C.leg_d(work)
print("WITH newfile  :", last1, "ok=", ok1)
# 撤掉新增件：令认领集为空（等价新件未落盘）
C.will_exist = lambda: set()
ok2, last2, t2, d2 = C.leg_d(work)
print("WITHOUT newfile:", last2, "ok=", ok2)
okf, lastf, _v = C.leg_f(work)
print("version leg   :", lastf)
assert d2 > d1, "FATAL: 死链腿对新增件缺失无反应（没牙）"
print("[R287M-ORDER] newfile-first proven: dead %d -> %d" % (d1, d2))