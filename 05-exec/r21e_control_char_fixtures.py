# -*- coding: utf-8 -*-
r"""r21e_control_char_fixtures.py — 「控制字符扫描器」夹具（TDD：先看红，再实现被测件）。

为什么要有它：本轮同一天内**四轮**踩中同一个坑（反斜杠被解析成退格符，产出肉眼不可见的 0x08，
把「用户命令绝对优先」这条铁律自己的权威源路径变成 grep 不到的死路径）。规则型解法（写进 lessons）
已被证伪 —— 我自己写着教训的条目自身又中了同一个坑。按 A-get-memory Step 2.7「可复用性唯一标准」，
唯一能拦住下一个会话的是**每次动手前必跑的机器扫描**。

被测对象：`05-exec/control_char_scan.py`，契约：
    ALLOWED = {0x09, 0x0a, 0x0d}                     # 制表/换行/回车不算脏
    find_control(text: str) -> list[(offset, code)]
    scan_paths(paths: list[str]) -> list[finding]    # finding = {"path","count","codes":[..]}
    main(argv) -> int                                # 0 干净 / 1 有脏项 / 2 无有效输入面（R247）
"""
import importlib.util
import io
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = HERE / "control_char_scan.py"
R = []


def ck(name, cond, detail=""):
    R.append(bool(cond))
    print("%s %-58s %s" % ("PASS" if cond else "FAIL", name, detail if not cond else ""))


def load(alias="ccs"):
    spec = importlib.util.spec_from_file_location(alias, str(TARGET))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def tmpfile(content, name="sample.md", binary=False):
    d = tempfile.mkdtemp(prefix="ccs_")
    p = os.path.join(d, name)
    with open(p, "wb") as f:
        f.write(content.encode("utf-8") if not binary else content)
    return p


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    if not TARGET.exists():
        print("FAIL RED 前置：被测件不存在 %s" % TARGET)
        return 1
    m = load()
    BS, ESC, NUL, SOH = chr(8), chr(27), chr(0), chr(1)
    LF, CR, TAB = chr(10), chr(13), chr(9)

    # ── 层 a：判据已知答案 ────────────────────────────────────────
    ck("a01 干净文本 0 命中", m.find_control("正常中文 和 反斜杠字面 " + chr(92) + "b") == [])
    ck("a02 换行/回车/制表符不算脏", m.find_control("a" + LF + "b" + CR + "c" + TAB) == [])
    ck("a03 退格符被抓到且给偏移", m.find_control("ab" + BS + "cd") == [(2, 8)])
    ck("a04 ESC 序列（ANSI 色码）被抓到", [c for _o, c in m.find_control("x" + ESC + "[31m")] == [27])
    ck("a05 多字符逐个报（不合并计数）", len(m.find_control(BS + ESC + SOH)) == 3)
    ck("a06 零字符也算脏（NUL）", m.find_control("a" + NUL) == [(1, 0)])
    ck("a08 DEL(0x7f) 也算脏（本仓源码实测出现过真 DEL，原定义只查 <0x20 会漏）",
       m.find_control("a" + chr(127)) == [(1, 127)])
    ck("a07 偏移是字符下标（供人直接定位）",
       m.find_control("中文" + BS)[0][0] == 2)

    # ── 层 b：真实接线（文件面）──────────────────────────────────
    good = tmpfile("正常内容" + LF)
    bad = tmpfile("坏内容" + BS + "在这里" + LF, name="bad.md")
    bins = tmpfile(b"\x7fELF" + b"\x00\x01\x02", name="bin.md", binary=True)
    res = m.scan_paths([good, bad])
    ck("b01 干净文件不报", os.path.getsize(good) > 0 and good not in [x["path"] for x in res], str(res))
    ck("b02 脏文件报 1 次且含码位", any(x["codes"] == [8] for x in res), str(res))
    ck("b03 finding 带可跳转路径", all(os.path.isabs(x["path"]) for x in res))
    ck("b04 二进制文件跳过并计入 skipped（不静默丢弃）",
       m.scan_paths([bins])[0].get("skipped") is True or m.scan_paths([bins]) == [],
       str(m.scan_paths([bins])))
    p1 = subprocess.run([sys.executable, str(TARGET), good], capture_output=True, text=True)
    ck("b05 CLI 干净 → exit 0 且打印标记行",
       p1.returncode == 0 and "[CTRL:CLEAN]" in (p1.stdout or ""), str(p1.returncode) + (p1.stdout or "")[:80])
    p2 = subprocess.run([sys.executable, str(TARGET), bad], capture_output=True, text=True)
    ck("b06 CLI 有脏 → exit 1 且打印 CTRL-DIRTY", p2.returncode == 1 and "[CTRL:DIRTY]" in (p2.stdout or ""),
       str(p2.returncode) + (p2.stdout or "")[:80])
    p3 = subprocess.run([sys.executable, str(TARGET), os.path.join(HERE, "__no_dir__")],
                        capture_output=True, text=True)
    ck("b07 输入面为空/不存在 → exit 2（判据面为空不得判过，R247）",
       p3.returncode == 2 and "[CTRL:EMPTY]" in (p3.stdout or ""), str(p3.returncode))
    d = tempfile.mkdtemp(prefix="ccs_dir_")
    io.open(os.path.join(d, "x.md"), "w", encoding="utf-8").write("目录里" + BS)
    p4 = subprocess.run([sys.executable, str(TARGET), d], capture_output=True, text=True)
    ck("b08 传目录会递归（默认 md/py 面）", p4.returncode == 1 and "x.md" in (p4.stdout or ""),
       (p4.stdout or "")[:100])
    p5 = subprocess.run([sys.executable, str(TARGET), "--json", bad], capture_output=True, text=True)
    ok5 = False
    try:
        import json
        j = json.loads((p5.stdout or "").strip().splitlines()[-1])
        ok5 = j["dirty"][0]["codes"] == [8]
    except Exception as e:
        ok5 = False
    ck("b09 --json 机器可读且 codes 正确", ok5, (p5.stdout or "")[:100])
    ck("b10 扫描器自身源码必须零控制符（自反可证）",
       m.find_control(io.open(str(TARGET), encoding="utf-8-sig").read()) == [])

    # ── 变异对照：把判据改坏，夹具必须变红 ─────────────────────────
    src = io.open(str(TARGET), encoding="utf-8").read()
    BS = chr(8)
    muts = [
        ("允许集吞掉退格符（0x08 变合法）", "0x09, 0x0a, 0x0d", "0x08, 0x09, 0x0a, 0x0d",
         lambda mm: mm.find_control("a" + BS) == []),
        ("判据被掏空（命中不收集）", "out.append", "pass  #",
         lambda mm: mm.find_control("a" + BS) == []),
        ("空输入面被当放行（治 R247 静默绿）", "return 2", "return 0", None),
    ]
    flipped = 0
    for name, bad_s, good_s, probe in muts:
        if bad_s not in src:
            ck("变异锚点在位：%s" % name, False, "锚点失配，变异未生效")
            continue
        fd, mp = tempfile.mkstemp(suffix=".py", prefix="ccs_mut_")
        os.close(fd)
        io.open(mp, "w", encoding="utf-8").write(src.replace(bad_s, good_s, 1))
        try:
            if probe is None:
                rc = subprocess.run([sys.executable, mp, os.path.join(HERE, "__no_dir__")],
                                    capture_output=True).returncode
                changed = rc == 0
            else:
                changed = probe(load_spec(mp, "ccs_mut"))
            flipped += bool(changed)
            ck("变异被拦：%s" % name, changed)
        except Exception as e:
            flipped += 1
            ck("变异被拦：%s" % name, True, "变异后直接不可用 %s" % type(e).__name__)
        finally:
            os.unlink(mp)
    ck("变异组 3/3 全部使结论改变（对照组 = 层 a/b 全绿）", flipped == 3, "%d/3" % flipped)

    print("-" * 70)
    bad_n = R.count(False)
    print("%s r21e 控制字符扫描夹具 %d/%d" % ("[GATE:fixture-pass]" if not bad_n else "[GATE:fixture-fail]",
                                            R.count(True), len(R)))
    return 0 if not bad_n else 1


def load_spec(path, alias):
    spec = importlib.util.spec_from_file_location(alias, path)
    mo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mo)
    return mo


if __name__ == "__main__":
    raise SystemExit(main())
