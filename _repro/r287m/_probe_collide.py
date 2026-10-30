# -*- coding: utf-8 -*-
"""_probe_collide.py — 只读探测：补丁新增文本会不会触发 rule_editor 的编号预检（R231 fail-closed）。

为什么要探：版本史行里写了 R287m / ca45fc49 这类串，若被 RE_R_NUM 认成领号，
Lead 落盘时会被 --allow-collide 拦下（假失败）。本件只调 rule_editor 的正则与 _hist_numbers，
不写任何文件。
"""
import importlib.util, json, os
spec = importlib.util.spec_from_file_location("rule_editor", r"D:\global_skills\A-memory-start\references\rule_editor.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
items = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "patch.json"), encoding="utf-8"))
text = chr(10).join(it["new"] for it in items)
print("RE_R_NUM finds:", sorted(set(m.RE_R_NUM.findall(text))))
print("RE_V_NUM finds:", sorted(set(m.RE_V_NUM.findall(text))))
rset, vset = m._hist_numbers(text)
print("_hist_numbers 条目号 R:", sorted(rset), "V:", sorted(vset))
rows = m._hist_lines(text)
print("hist rows:", len(rows), [r[:48] for r in rows][:3])