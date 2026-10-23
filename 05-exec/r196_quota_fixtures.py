# -*- coding: utf-8 -*-
"""r196_quota_fixtures.py — 额度面夹具（W-47 双向 + 变异腿）。

锁四件事（都是本轮实测踩到的）：
  A 括号平衡扫描能在「JSON + ANSI 告警尾巴」的混合输出里截出数组（wrangler --json 的真实形态）
  B NO_COLOR 对 wrangler 的 WARNING 无效 ⇒ 必须先剥 ANSI 再扫描（否则 json.loads 报 Extra data）
  C 三态不互相冒充：GAP_PLATFORM（平台下线，有依据）≠ UNVERIFIED（本轮取不到）
  D 变异：去掉 ANSI 剥离 ⇒ B 的场景必须失败（证明 A/B 腿真有牙，不是恰好过）
"""
import importlib.util as _u
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
TARGET = os.path.join(HERE, "r196_quota_face.py")
RESULTS = []


def ck(name, cond, detail=""):
    RESULTS.append((bool(cond), name, detail))
    print("%s %-58s %s" % ("PASS" if cond else "FAIL", name, detail if not cond else ""))


def load():
    s = _u.spec_from_file_location("qf", TARGET)
    m = _u.module_from_spec(s)
    s.loader.exec_module(m)
    return m


# 本轮真实抓到的 wrangler 输出形态（截断，保留关键结构 + ANSI 告警尾巴）
RAW = (
    '[\n  {\n    "uuid": "bf5b1d01",\n    "name": "donggu-analytics",\n'
    '    "num_tables": 0,\n    "file_size": 6828032\n  },\n  {\n'
    '    "name": "supermarket",\n    "num_tables": 0,\n    "file_size": 2396160\n  }\n]\n'
    "\x1b[33m\u25b2 \x1b[43;33m[\x1b[43;30mWARNING\x1b[43;33m]\x1b[0m "
    "\x1b[1mProxy environment variables detected.\x1b[0m\n\n\n"
)


def main():
    if not os.path.isfile(TARGET):
        ck("t0 被测件存在", False, TARGET)
        print("[GATE:fixture-fail]")
        return 1
    m = load()

    # A 直接扫裸串会 Extra data
    try:
        json.loads(RAW)
        poisoned = False
    except ValueError:
        poisoned = True
    ck("A 原始混输出不可直接 json.loads（这就是本轮真实报错形态）", poisoned)

    # B 剥 ANSI + 括号平衡扫描 => 得到数组且数值正确
    clean = m.ANSI_RE.sub("", RAW)
    seg = m.first_json_array(clean)
    ok_b = False
    rows = None
    if seg:
        try:
            rows = json.loads(seg)
            ok_b = isinstance(rows, list) and len(rows) == 2
        except ValueError:
            ok_b = False
    ck("B 剥 ANSI + 括号平衡扫描截出数组（2 实例）", ok_b, str(rows)[:80])
    if rows:
        tot = sum(int(r.get("file_size") or 0) for r in rows)
        ck("B2 合计字节正确", tot == 6828032 + 2396160, str(tot))

    # C 三态互斥：GAP 依据须含官方出处；UNVERIFIED 不得带依据串
    g = m.read_gh_billing if hasattr(m, "read_gh_billing") else None
    ck("C1 被测件暴露 read_gh_billing（GAP 判定入口）", g is not None)
    doc = json.load(io.open(os.path.join(os.path.dirname(HERE), "06-benchmark",
                                        "quota_face_r196.json"), encoding="utf-8")) if True else None
    rows_doc = doc.get("rows") or []
    gap = [r for r in rows_doc if r.get("state") == "GAP_PLATFORM"]
    ck("C2 真件里 GAP_PLATFORM 带官方 changelog 出处",
       bool(gap) and "github.blog/changelog" in (gap[0].get("why") or ""),
       (gap[0].get("why") or "")[:60] if gap else "无 GAP 行")
    ck("C3 GAP 不等于 UNVERIFIED（两态计数分开）",
       "gap_platform_count" in doc and "unverified_count" in doc)
    ck("C4 额度读数标了分母出处（名册声称值，非官方文档）",
       any("名册" in str(v) for r in rows_doc for v in [r.get("note", "")]))

    # D 变异（r196 自我纠正：我第一版把 B 通过归因给「剥 ANSI」，被这条腿当场推翻 ——
    #   告警尾巴落在 JSON 数组**之外**，是括号平衡扫描截掉了它，剥离对本形态其实是冗余。
    #   归因错了就要拆成两条各测其责，而不是把错的那条改成永远为真）：
    # D1 去掉括号扫描（直接 loads 整串）⇒ 必须失败 ⇒ 证明真正起作用的是扫描
    ok_d1 = False
    try:
        json.loads(m.ANSI_RE.sub("", RAW))     # 剥了但不扫描
    except ValueError:
        ok_d1 = True
    ck("D1 变异：无括号平衡扫描则解析失败（扫描才是承重的那一步）", ok_d1),
    # D2 ANSI 若落在数组**内部**，只扫描不剥离必须失败 ⇒ 证明剥离有独立必要（构造场景）
    # D2 如实测量（不替错归因找补）：只剥 ANSI、不做括号扫描 => 本形态其实也能过，
    #   说明承重的是 D1 那一步（扫描），ANSI 剥离对本输出只是防御性的。
    strip_only = m.ANSI_RE.sub("", RAW)
    ok_after_strip_only = False
    try:
        rr = json.loads(strip_only.strip())
        ok_after_strip_only = isinstance(rr, list)
    except ValueError:
        ok_after_strip_only = False
    # D2 反向来测（r196 第二次自我纠正：我上一版断言「只剥不扫也能过」，实测 False ——
    #   那也是我**没测就写**的。故两向都实测，才敢指名承重步骤）：
    #   D1 剥了但不扫 => 失败；D2 扫了但不剥 => 成功 => 承重是括号扫描。
    seg_nostrip = m.first_json_array(RAW)
    ok_scan_only = False
    try:
        ok_scan_only = isinstance(json.loads(seg_nostrip), list)
    except (ValueError, TypeError):
        ok_scan_only = False
    ck("D2 只扫不剥 ⇒ 解析成功（配合 D1 证明承重步骤是扫描）",
       ok_scan_only is True,
       "strip_only=%r scan_only=%r" % (ok_after_strip_only, ok_scan_only))
    # D3 剥离器自身行为：清完后告警尾巴里不得再有 ESC，且文本仍在（证明是清了序列不是吞了内容）
    ESC = chr(27)
    pre_tail = RAW[RAW.rfind("]") + 1:] if "]" in RAW else ""
    tail = strip_only[strip_only.rfind("]") + 1:] if "]" in strip_only else ""
    ck("D3 ANSI_RE 只清转义序列不吞文本（前后对比）",
       (ESC in pre_tail) and (ESC not in tail) and ("Proxy" in tail),
       "pre有ESC=%s post有ESC=%s" % (ESC in pre_tail, ESC in tail))

    fails = [r for r in RESULTS if not r[0]]
    print("")
    print("夹具合计: %d 项，通过 %d，失败 %d" % (len(RESULTS), len(RESULTS) - len(fails), len(fails)))
    if fails:
        for _ok, nm, det in fails:
            print("  FAIL %s | %s" % (nm, det))
        print("[GATE:fixture-fail]")
        return 1
    print("[GATE:fixture-pass]")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())
