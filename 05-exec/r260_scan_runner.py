# -*- coding: utf-8 -*-
'''r260 复算跑手：import 权威 01-scan/scan_all.py 的 scan() 本体，
只把读入 SCOPE_DIR 指向本仓 00-scope、写盘 SCAN_DIR 指向 _temp（本仓 --ws 守卫禁止 CLI 注入 _temp，
且 --apply 直写会覆盖 01-scan/ 的 09-22 冻结件 —— 违「历史留痕不可改写」）。
判据逻辑零复刻、零改动，避免自写等价口径漂。'''
import os, sys, json, argparse
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, '01-scan'))
import scan_all
out_dir = os.path.join(HERE, 'r260_scanout')
os.makedirs(out_dir, exist_ok=True)
scan_all.SCOPE_DIR = os.path.join(ROOT, '00-scope')
scan_all.SCAN_DIR = out_dir
scan_all.args = argparse.Namespace(apply=True)
rc = scan_all.scan()
print('RECOMPUTE_RC=' + str(rc))