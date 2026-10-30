import os
D = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(D, "check_r287m.py")
src = open(p, encoding="utf-8", newline="").read()
q = chr(34)
start = src.index("    if neg == " + q + "anchor-multi" + q + ":")
end = src.index("    return out, vid" + chr(10), start) + len("    return out, vid" + chr(10))
new = open(os.path.join(D, "_neg_block.txt"), encoding="utf-8").read()
out = src[:start] + new + src[end:]
open(p, "w", encoding="utf-8", newline="").write(out)
print("spliced", len(src), "->", len(out))