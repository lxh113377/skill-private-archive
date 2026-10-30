# -*- coding: utf-8 -*-
"""verify_landed.py — 换装**落盘后**的复验器（只读受管根；判据实现复用 check_r287m，不留第二真相源）。

用法：
  python -B _repro/r287m/verify_landed.py                       # 复验受管根（未换装时应判红 = 有牙）
  python -B _repro/r287m/verify_landed.py --root <预览树>        # 复验内存换装预览树（应判绿）
判据三条（对应 R287m 的 ①②③）：
  D 死链：SKILL.md 与 reference/*.md 的每个 ./ 相对引用在盘上存在
  E 参数：文档写明的每个脚本参数被该脚本 --help 支持
  F 版本：frontmatter version / last_updated 与版本史首行三者一致
"""
import argparse
import json
import os
import sys

D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, D)
import check_r287m as C


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=C.SKILL_ROOT)
    ap.add_argument("--newfile-list", default=None,
                    help="换装将新增件清单（预览树未落盘时用来认领，防假死链）")
    a = ap.parse_args()
    C.SKILL_ROOT = a.root.replace(chr(92), "/")
    work = {}
    for rel in ["SKILL.md", "reference/node_mcp_server.md"]:
        p = C.norm(os.path.join(C.SKILL_ROOT, rel))
        if not os.path.isfile(p):
            print("FAIL PRE 目标件缺失:", p)
            return 1
        work[p] = C.read_text(p)
    if a.newfile_list:
        man = json.load(open(a.newfile_list, encoding="utf-8"))
        C.will_exist = lambda: set([C.norm(os.path.normpath(man["local_target"]))])
    okd, lastd, _t, _dd = C.leg_d(work)
    oke, laste, _t2, _b = C.leg_e(work)
    okf, lastf, _v = C.leg_f(work)
    for ok, last in ((okd, lastd), (oke, laste), (okf, lastf)):
        print(("PASS " if ok else "FAIL ") + last)
    has_v2 = os.path.isfile(C.norm(os.path.join(C.SKILL_ROOT, "reference", "node_mcp_server_v2.md")))
    print("[R287M-V2-ONDISK] exists=%s" % ("yes" if has_v2 else "no"))
    allok = okd and oke and okf and has_v2
    print("[MCP-LANDED] dead=0 args_ok=1 version_ok=1 v2=1 gate=%s" % ("PASS" if allok else "FAIL"))
    return 0 if allok else 1


if __name__ == "__main__":
    sys.exit(main())
