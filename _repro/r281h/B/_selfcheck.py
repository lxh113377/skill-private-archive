"""Arm B self-evidence: list arm dir, print MASTER.md lines 1-25, print _toolcount.txt."""
import os
ARM = os.path.dirname(os.path.abspath(__file__))
def main():
    print("== ARM DIR ==")
    for name in sorted(os.listdir(ARM)):
        full = os.path.join(ARM, name)
        kind = "DIR " if os.path.isdir(full) else "FILE"
        size = os.path.getsize(full) if os.path.isfile(full) else "-"
        print(kind, name, size, "bytes")
    print("== design-system TREE ==")
    root = os.path.join(ARM, "design-system")
    for dirpath, _dn, filenames in os.walk(root):
        for fn in sorted(filenames):
            fp = os.path.join(dirpath, fn)
            print(os.path.relpath(fp, ARM).replace(chr(92), "/"), os.path.getsize(fp), "bytes")
    master = os.path.join(root, "data-analytics-dashboard", "MASTER.md")
    print("== MASTER.md LINES 1-25 ==")
    with open(master, encoding="utf-8") as fh:
        ls = fh.readlines()
    for i, ln in enumerate(ls[:25], start=1):
        print(str(i).rjust(3) + " | " + ln.rstrip())
    print("== _toolcount.txt ==")
    with open(os.path.join(ARM, "_toolcount.txt"), encoding="utf-8") as fh:
        print(repr(fh.read().strip()))
if __name__ == "__main__":
    main()
