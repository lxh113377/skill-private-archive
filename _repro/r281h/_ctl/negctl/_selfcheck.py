# -*- coding: ascii -*-
""""Self-verification (arm A, read-only): arm listdir, MASTER.md first 25 lines, _toolcount.txt.""""
import os, io
A = "C:/Users/37533/Desktop/workspace/skill焚诀/_temp/r281h/A"
print("ARM=" + A)
print("--- listdir ---")
for n in sorted(os.listdir(A)):
    p = os.path.join(A, n)
    print(("DIR  " if os.path.isdir(p) else "FILE %8d  ") % (0 if os.path.isdir(p) else os.path.getsize(p)) + n)
T = os.path.join(A, "design-system", "internal-data-dashboard")
print("--- design-system tree ---")
for root, dirs, fs in os.walk(T):
    for f in sorted(fs):
        print("%9d  %s" % (os.path.getsize(os.path.join(root, f)), os.path.join(root, f).replace(A + os.sep, "")))
print("--- MASTER.md first 25 lines ---")
with io.open(os.path.join(T, "MASTER.md"), "r", encoding="utf-8") as f:
    for i, ln in enumerate(f, 1):
        print("%3d| %s" % (i, ln.rstrip("\n")))
        if i >= 25:
            break
print("--- _toolcount.txt ---")
with io.open(os.path.join(A, "_toolcount.txt"), "r", encoding="utf-8") as f:
    print(repr(f.read()))
