# -*- coding: utf-8 -*-
r"""r21e_gate_patchgen3.py — 最后一处补丁：RE_EVID 允许裸版本号（V 前缀可选）。

实测起因：真实文件里版本行写作 `version: 10.70.0`（无 V 前缀）。形状层只收 `#版本行:Vx.y.z`
⇒ 老实人按文件里的原样引用反而被判「不合规」，而随手加个 V 就能过 ——**判据在奖励美化而不是奖励真实**。
放宽形状层的同时，可解析性（同批新增）会去文件里核对 token，因此净效果是**更严**而非更松。
"""
import io
import json
import sys

GATE = r"D:\global_skills\A-memory-start\references\upgrade_footer_gate.py"
OUT = r"C:\Users\37533\Desktop\workspace\自建skill优化\05-exec\r21e-patches\patch_gate3.json"
NL = chr(10)


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    src = io.open(GATE, encoding="utf-8").read()
    i = src.index("RE_EVID = re.compile(")
    j = src.index(NL, i)
    old = src[i:j]
    if "版本行:V?" in old:
        print("[SKIP] 已是可选 V 形态")
        return 0
    assert src.count(old) == 1
    new = old.replace("版本行:V", "版本行:V?")
    assert new != old
    io.open(OUT, "w", encoding="utf-8").write(json.dumps([{"old": old, "new": new}],
                                                         ensure_ascii=False, indent=1))
    print("[PATCHGEN3] old: %s" % old[:78])
    print("            new: %s" % new[:78])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
