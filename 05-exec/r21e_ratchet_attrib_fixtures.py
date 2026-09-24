# -*- coding: utf-8 -*-
r"""r21e_ratchet_attrib_fixtures.py — 「带归因抬基线」夹具（TDD：先看红）。

被测对象：`05-exec/ratchet_gate.py` 新增
    attribute_raise(old_m: dict, new_m: dict, baseline: dict, attr: list) -> (ok, why)
      · ok=True 仅当：两处指标里唯一长大的那一项，其增量能被**一条归因记录完整解释**——
        attr 项含 {"commit","path","delta","reason"}，且 path 属于 inject 面清单、delta == 该项实际增量。
      · 否则 ok=False（保持阻断，禁止把"抬基线"变成随手动作）。
    CLI: --raise-baseline --commit <sha> --path <file> --reason "<一句话>"
      · 增量与 --delta 不符 / 缺 reason / path 不在面内 ⇒ exit 1 且不写盘
      · 成功 ⇒ 写基线并**永久留账** baseline["attributed_raises"] += {...}（可数、可复核）

夹具策略：不依赖真仓，全部用内存 dict + 临时基线文件；对照组必须绿（防"判据永不触发"）。
"""
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = HERE / "ratchet_gate.py"
R = []


def ck(name, cond, detail=""):
    R.append(bool(cond))
    print("%s %-58s %s" % ("PASS" if cond else "FAIL", name, detail if not cond else ""))


def load():
    spec = importlib.util.spec_from_file_location("rg2", str(TARGET))
    mo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mo)
    return mo


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    if not hasattr(load(), "attribute_raise"):
        print("FAIL RED 前置：ratchet_gate.py 尚无 attribute_raise()")
        return 1
    m = load()
    FACE = r"D:\global_memory\core\behavior_core.md"
    base = {"inject_union_bytes": 86346, "catalog_grand_chars": 45250}
    old = {"inject_union_bytes": 86793, "catalog_grand_chars": 45250}   # 只有一项长大 = +447
    good = [{"commit": "055f9b5", "path": FACE, "delta": 447, "reason": "立 #23 用户命令绝对优先"}]

    ck("① 增量被一条归因完整解释 → 放行", m.attribute_raise(old, base, good)[0] is True,
       str(m.attribute_raise(old, base, good)))
    ck("② 归因 delta 与实增不符 → 拒绝", not m.attribute_raise(old, base,
       [dict(good[0], delta=1)])[0])
    ck("③ path 不在该项可归因面内 → 拒绝", not m.attribute_raise(old, base,
       [dict(good[0], path=r"D:\elsewhere\x.md")])[0])
    ck("④ 缺 reason → 拒绝", not m.attribute_raise(old, base,
       [{"commit": "abc", "path": FACE, "delta": 447}])[0])
    ck("⑤ 无归因记录 → 拒绝（默认仍阻断）", not m.attribute_raise(old, base, [])[0])
    ck("⑥ 两项同时长大、只归因一项 → 拒绝", not m.attribute_raise(
       {"inject_union_bytes": 86793, "catalog_grand_chars": 45260}, base, good)[0])
    ck("⑦ 指标变小（合法下调）不需要归因", m.attribute_raise({"inject_union_bytes": 1, "catalog_grand_chars": 1},
                                                            base, [])[0] is True)

    # 层 b：真实接线（CLI 写基线 + 永久留账）
    d = tempfile.mkdtemp(prefix="rg_")
    bl = os.path.join(d, "bl.json")
    io.open(bl, "w", encoding="utf-8").write(json.dumps(
        {"schema": "zijian-inject-ratchet-v1", "metrics": base, "hard_caps": {"inject_union_bytes": 65536}}))
    p = subprocess.run([sys.executable, str(TARGET), "--baseline", bl, "--raise-baseline",
                        "--commit", "055f9b5", "--path", FACE, "--delta", "447",
                        "--reason", "立 #23 用户命令绝对优先（他仓合法增长）"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    j = json.loads(io.open(bl, encoding="utf-8").read())
    ck("b08 CLI 归因抬基线成功且写账", p.returncode == 0 and j["metrics"]["inject_union_bytes"] == 86793
       and len(j.get("attributed_raises", [])) == 1, (p.stdout or "")[:120])
    ck("b09 账目含 commit/path/delta/reason 四要素",
       set(j["attributed_raises"][0]) >= {"commit", "path", "delta", "reason"}, str(j["attributed_raises"][0])[:110])
    p2 = subprocess.run([sys.executable, str(TARGET), "--baseline", bl, "--raise-baseline",
                         "--commit", "deadbeef", "--path", FACE, "--delta", "99999",
                         "--reason", "随便"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    ck("b10 delta 不符 → exit 1 且不改基线不写账",
       p2.returncode == 1 and json.loads(io.open(bl, encoding="utf-8").read())["metrics"]["inject_union_bytes"] == 86793,
       (p2.stdout or "")[:110])
    p3 = subprocess.run([sys.executable, str(TARGET), "--baseline", bl], capture_output=True,
                        text=True, encoding="utf-8", errors="replace")
    ck("b11 抬后再跑：棘轮以内 → PASS 且打印历史归因条数", p3.returncode == 0 and "归因" in (p3.stdout or ""),
       (p3.stdout or "")[-120:])
    # ── 变异对照（判据类交付硬判据之②：把判据改坏，夹具必须变红）───────
    src = io.open(str(TARGET), encoding="utf-8").read()
    muts = [
        ("delta 相符校验失效", "if int(a.get(\"delta\") or -1) != delta:", "if False:"),
        ("注入面成员校验失效", "if rp not in inject_face():", "if False:"),
        ("必须恰好一条归因失效", "if len(cands) != 1:", "if False:"),
        ("多项增长拒绝失效", "if len(grows) > 1:", "if False:"),
    ]
    probes = [
        lambda mm: mm.attribute_raise(old, base, [dict(good[0], delta=1)])[0] is True,
        lambda mm: mm.attribute_raise(old, base,
                                      [dict(good[0], path=r"D:\elsewhere\x.md")])[0] is True,
        lambda mm: mm.attribute_raise(old, base, [])[0] is True,
        lambda mm: mm.attribute_raise({"inject_union_bytes": 86793, "catalog_grand_chars": 45260},
                                      base, good)[0] is True,
    ]
    flipped = 0
    for (name, bad_s, rep), probe in zip(muts, probes):
        if bad_s not in src:
            ck("变异锚点在位：%s" % name, False, "锚点失配（源码结构变了，夹具要跟着改）")
            continue
        fd, mp = tempfile.mkstemp(suffix=".py", prefix="rg_mut_")
        os.close(fd)
        io.open(mp, "w", encoding="utf-8").write(src.replace(bad_s, rep, 1))
        try:
            got = probe(load_spec(mp, "rg_mut"))
            flipped += bool(got)
            ck("变异被拦：%s" % name, got)
        except Exception as e:
            flipped += 1
            ck("变异被拦：%s" % name, True, "变异后不可用 %s" % type(e).__name__)
        finally:
            os.unlink(mp)
    ck("变异组 4/4 全部使结论改变（未变异对照组 = 上面 ①-⑦）", flipped == 4, "%d/4" % flipped)
    print("-" * 66)
    bad = R.count(False)
    print("%s r21e 归因抬基线夹具 %d/%d" % ("[GATE:fixture-pass]" if not bad else "[GATE:fixture-fail]",
                                          R.count(True), len(R)))
    return 0 if not bad else 1


if __name__ == "__main__":
    raise SystemExit(main())
