# 留档：rule_editor 镜像超时改造的四例验牙（r220 / 受管根 R816）。
# 零副作用：只 monkeypatch 抛 TimeoutExpired，不真跑 45 分钟的 -Fix。
# 用法: python 05-exec/r220_mirror_teeth.py
# -*- coding: utf-8 -*-
# rule_editor 镜像超时改造的验牙：只测分支，不真跑 -Fix（零副作用）
import importlib.util as U
import io, os, subprocess, sys, contextlib
T = r'C:/Users/37533/AppData/Local/Temp/'
ED = r'D:/global_skills/A-memory-start/references/rule_editor.py'
out = []
# 1) 语法编译（本会话立的规矩：验语法必用 -m py_compile，不是包字符串）
r = subprocess.run([sys.executable, '-m', 'py_compile', ED],
                     capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=200)
out.append('py_compile rc=%d %s' % (r.returncode, (r.stdout or r.stderr or '').strip()[:90]))
# 2) 载入模块
os.environ['FENJUE_MIRROR_TIMEOUT'] = '1'   # 强制任何真子进程超时
sp = U.spec_from_file_location('re_ed', ED)
m = U.module_from_spec(sp)
av = sys.argv
sys.argv = ['rule_editor']
try:
    sp.loader.exec_module(m)
finally:
    sys.argv = av
out.append('载入成功 = %s | MIRROR_TIMEOUT_S = %s' % (hasattr(m, 'MIRROR_TIMEOUT_S'), getattr(m, 'MIRROR_TIMEOUT_S', None)))
out.append('无残留 timeout=180 = %s' % ('timeout=180' not in io.open(ED, encoding='utf-8').read()) )
# 3) 只读检查超时 -> 必须 True（不阻塞）+ 措辞含『状态未知』、不含『请手动』
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    v = m._mirror_check_only()
cap = buf.getvalue()
out.append('只读检查超时 -> 返回 %s | 含状态未知=%s | 含请手动=%s' % (
    v, ('状态未知' in cap), ('请手动' in cap)))
out.append('   实印: ' + ' '.join(cap.split())[:120])
ok_check = (v is True and '状态未知' in cap and '请手动' not in cap)
# 4) -Fix 超时 -> 必须 False（真失败，不谎报成功）+ 不含『请手动』；用 monkeypatch 不真跑
orig = m.subprocess.run
class TE(Exception):
    pass
def boom(*a, **k):
    raise m.subprocess.TimeoutExpired(cmd='x', timeout=1)
m.subprocess.run = boom
buf2 = io.StringIO()
try:
    with contextlib.redirect_stdout(buf2):
        f = m.run_mirror_fix()
finally:
    m.subprocess.run = orig
cap2 = buf2.getvalue()
out.append('Fix 超时 -> 返回 %s（须 False）| 含无需人工=%s | 含请手动=%s' % (
    f, ('无需人工' in cap2), ('请手动' in cap2)))
out.append('   实印: ' + ' '.join(cap2.split())[:120])
ok_fix = (f is False and '请手动' not in cap2)
# 5) 反向对照：超时阈值若设大，只读检查应真跑 ps1（不超时则走 returncode 分支）
os.environ['FENJUE_MIRROR_TIMEOUT'] = '5'
sp2 = U.spec_from_file_location('re_ed2', ED)
m2 = U.module_from_spec(sp2)
sys.argv = ['rule_editor']
try:
    sp2.loader.exec_module(m2)
finally:
    sys.argv = av
out.append('阈值可覆盖生效（5s 载入）= %s' % (m2.MIRROR_TIMEOUT_S == 5))
allok = r.returncode == 0 and ok_check and ok_fix and m2.MIRROR_TIMEOUT_S == 5
out.append('')
out.append('验牙四例齐 = %s' % allok)
io.open(T + 'mirrorteeth.txt', 'w', encoding='utf-8').write(chr(10).join(out))
print('WROTE', allok)