# -*- coding: utf-8 -*-
r"""r21e_gate_patchgen2.py — 第二道补丁：放宽形状层以接受裸版本号，并让可解析性优先于 V 前缀。

实测起因（夹具 r21e_gate_probe 首跑 3/5）：
  · 真实存在的版本号在 SKILL.md 里写作 `version: 3.5.1`（**无 V 前缀**），而 RE_EVID 只收 `#版本行:Vx.y.z`
    ⇒ 历史上 18 条「token 不在该文件内」里有一部分其实是**形状层过严**造成的假失败，不是虚构。
  · 于是判据顺序必须是：先确认「文件在不在」→ 再谈 token 形态；V 前缀只作可选。
  · 同时 fake_path 一例暴露：路径完全不存在时，若该路径不落在五个已知仓之内，会被判 SKIP 而放行
    ⇒ 收紧为：**只要形如绝对路径且不存在 = FAKE**（体系外豁免只保留给「存在但读不到/在第三方端点」）。
"""
import io
import json
import os
import sys

GATE = r"D:\global_skills\A-memory-start\references\upgrade_footer_gate.py"
OUT = r"C:\Users\37533\Desktop\workspace\自建skill优化\05-exec\r21e-patches\patch_gate2.json"
NL = chr(10)


def one(src, needle, label):
    n = src.count(needle)
    if n != 1:
        raise SystemExit("[GUARD] %s 命中 %d 次（期望 1）⇒ 停手" % (label, n))
    return needle


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    src = io.open(GATE, encoding="utf-8").read()
    patches = []

    # ① 形状层：V 前缀改为可选（裸版本号也认，交由可解析性判真伪）
    old_re = 'RE_EVID = re.compile(r"^[A-Za-z]:[\\\\/].+?#(?:版本行:V\\d+(?:\\.\\d+)*|backup:[\\w.\\-]+)$")'
    i = src.index("RE_EVID = re.compile(")
    j = src.index(NL, i)
    old_re = src[i:j]
    new_re = 'RE_EVID = re.compile(r"^[A-Za-z]:[\\\\/].+?#(?:版本行:V?\\d+(?:\\.\\d+)*|backup:[\\w.\\-]+)$")'
    patches.append({"old": one(src, old_re, "RE_EVID"), "new": new_re})

    # ② 未知根下的绝对路径若不存在 = FAKE（原来会 SKIP 放行）
    old_blk = ('    return ("FAKE", "证据路径不存在") if known else ("SKIP", "路径在本体系外，不判")')
    new_blk = ('    return ("FAKE", "证据路径不存在")' + NL +
               '    # 体系外豁免只留给「存在但读不到」；不存在一律 FAKE（绝对路径写不出=凭空引用）')
    patches.append({"old": one(src, old_blk, "FAKE 收紧"), "new": new_blk})
    old_known = ('    known = any(p.replace("\\\\", "/").lower().startswith(r.replace("\\\\", "/").lower() + "/")'
                 + NL + '                for r in RESOLVE_ROOTS)' + NL + '    return p, known')
    new_known = ('    return p, True                                     # 绝对路径：交给 isfile 判，known 不再参与放行')
    patches.append({"old": one(src, old_known, "known 变量"), "new": new_known})

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    io.open(OUT, "w", encoding="utf-8").write(json.dumps(patches, ensure_ascii=False, indent=1))
    for n, p in enumerate(patches, 1):
        assert chr(0) not in p["old"] + p["new"] and chr(8) not in p["old"] + p["new"]
        print("  #%d old %d → new %d" % (n, len(p["old"]), len(p["new"])))
    print("[PATCHGEN2] %d 处 → %s" % (len(patches), OUT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
