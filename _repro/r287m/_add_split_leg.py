# -*- coding: utf-8 -*-
"""_add_split_leg.py — 把 check_r287m 的 load_patch 换成带数组件对账的版本（只动 _temp）。"""
import io, os
D = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(D, "check_r287m.py")
src = io.open(p, encoding='utf-8', newline='').read()
new = io.open(os.path.join(D, '_new_load_patch.txt'), encoding='utf-8').read()
start = src.index('def load_patch():')
end = src.index('def norm(p):')
out = src[:start] + new.rstrip() + chr(10) * 2 + src[end:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
print('load_patch replaced', len(src), '->', len(out))
