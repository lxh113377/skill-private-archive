# -*- coding: utf-8 -*-
r"""r21e_land4.py — 07 补一条外部在途导致契约门禁变红的待观察项（只登记不擅动）。"""
import io
import sys

N07 = r"C:\Users\37533\Desktop\workspace\自建skill优化\memory\07-next-steps.md"
B = chr(96)
ADD = ("- [ ] **【待观察·外部在途使本仓契约门禁变红（r21e 23:4x 实测）】** 必跑链第 3 条 " + B
       + "baseline_contract_scan.py" + B + " 现 " + B + "[CONTRACT:FAIL]" + B + "：并行会话（同日 r29 轮）把 " + B
       + "05-exec/skill_structure_rubric_scan.py" + B + " 的产物 schema 从 " + B + "skill-structure-rubric-v1" + B
       + " 升到 " + B + "-v2" + B + "，且该改动**尚未提交**（" + B + "git status" + B + " = " + B + " M" + B
       + "），但**已重生成了盘上产物** " + B + "06-benchmark/skill_structure_rubric_r29_2026-09-24.json" + B
       + "（schema=v2）⇒ 本仓契约（登记的是 v1）与产物当场对不上。同时 " + B + "r19_baseline_contract_fixtures.py" + B
       + " 层b 生效路径 exit 也红。**处置**：按 R269 不改对方脚本、不改契约凑绿（R263）；等其提交收口后由**归属方或下一轮**把契约 schema 一并升到 v2（一处改，夹具同批改），本条留账不销。"
       + "取值：" + B + "python 05-exec/baseline_contract_scan.py" + B + "（看 FAIL 行的文件名与 schema 实得值）+ " + B
       + "git status --porcelain | grep skill_structure" + B + "。\n")


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    s = io.open(N07, encoding="utf-8-sig").read()
    if "外部在途使本仓契约门禁变红" in s:
        print("[07] 已在位")
        return 0
    a2 = "- [ ] **【r21e 控制符扫描（已挂必跑链第 5 条）】**"
    assert s.count(a2) == 1, "锚点命中 %d" % s.count(a2)
    s = s.replace(a2, ADD + a2, 1)
    assert all(c not in s for c in (chr(8), chr(0), chr(127)))
    with open(N07, "wb") as f:
        f.write(s.encode("utf-8"))
    b = io.open(N07, encoding="utf-8-sig").read()
    print("[07] 待观察条在位=%s | %dB" % ("外部在途使本仓契约门禁变红" in b, len(b.encode("utf-8"))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
