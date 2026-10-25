# -*- coding: utf-8 -*-
r"""r230_tag_face.py — 只读看守「焚诀路由 Tag 层的有效匹配面」（r229 缺陷的长期判据）。

存在理由（r229 一手）：
  路由 L0.5 Tag 层的匹配**不遍历索引**，而遍历 `tag_layer.py` 里的手写清单 TAG_WEIGHT_TIERS：
      L58/64/71:  for tag in TAG_WEIGHT_TIERS.get('P0'/'P1'/'P2', []):
      L59/65/72:      if re.search(tag, query, ...):
      L60/66/73:          for sk in _tag_index.get(tag, []):   # ← 把清单项当索引用键
  该写法要求「清单项 == 索引键」，但实测：61 项里只有 31 项能命中索引，30 项空转；
  其中 P0 的 13 项全是正则字面量（\bexcel\b 等）——re.search 能命中问句，
  但 _tag_index.get(r"\bexcel\b") 查不到（索引里存的是 Excel/Notion/PDF）⇒ P0 整层零贡献。
  有效匹配面 = 31 / 469 = 6.6%。

  该缺陷在**焚诀仓**（产物与匹配逻辑都在 eval/），本仓红钱 6 定「焚诀 eval/ 只读不改」
  ⇒ 本仓不能代改，但**必须能持续看守**它（要求 5「长效巡检」的补强）：本件把
  「有效面 / 空转项 / P0 是否整层空转」钉成可复算读数，每季随巡检跑一次。

三态（禁静默）：
  [TAGFACE:PASS]       所有清单项都能命中索引，且 P0 有生效项 ⇒ 无空转
  [TAGFACE:EXPOSED]    dead_n > 0 或 P0 生效项为 0 ⇒ 缺陷在位（结论，不是本仓故障）
  [TAGFACE:UNVERIFIED] 输入面不可读 / 解析出 0 项 / 索引 0 键 ⇒ rc=2，禁读成「无空转」

口径红线：
  · 只读：不写焚诀仓任何文件；--tier / --index 可指夹具（自测用）；
  · 解析用**括号配对**而非非贪婪正则 —— r229 我首版用非贪婪正则，在嵌套字典处截断，
    得出「P0/P1/P2 各 1 项、与索引交集 0」的错结论，靠人工读源码才发现 ⇒ 解析器本身必须可证伪；
  · 「空转」定义 = 清单项在索引里不存在，**或**存在但值为空数组；两类都算，禁只算一类。

用法：python 05-exec/r230_tag_face.py [--tier 件] [--index 件] [--json 件] [--selftest] [--quiet]
退出码：0 PASS / 1 EXPOSED / 2 UNVERIFIED。
"""
import argparse
import io
import json
import os
import re
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
# 焚诀仓与本源**平级**：ROOT = <ws>/skill焚诀/自建skill优化 ⇒ 其 eval 在 <ws>/焚诀/eval
# （上两级再进「焚诀」；r230 首版少算一级，真跑直接 UNVERIFIED —— 判据 fail-closed 正确，
#   但路径是我写错的，靠「用真实数据跑一遍」当场抓出，见 X-18 同族教训）。
FENJUE_EVAL = os.path.join(os.path.dirname(os.path.dirname(ROOT)), "焚诀", "eval")
TOK_PASS = "[TAGFACE:PASS]"
TOK_EXP = "[TAGFACE:EXPOSED]"
TOK_UNV = "[TAGFACE:UNVERIFIED]"


def read_text(path):
    try:
        return io.open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return None


def _match_block(text, start_idx, open_ch, close_ch):
    """从 start_idx 处的开括号起做配对，返回 (内容, 结束下标)。字符串/注释内的括号不计。"""
    depth = 0
    i = start_idx
    in_str = None
    while i < len(text):
        ch = text[i]
        if in_str:
            if ch == "\\":
                i += 2
                continue
            if ch == in_str:
                in_str = None
        elif ch in "\"'":
            in_str = ch
        elif ch == "#":
            nl = text.find("\n", i)
            i = len(text) if nl < 0 else nl
            continue
        elif ch == open_ch:
            depth += 1
        elif ch == close_ch:
            depth -= 1
            if depth == 0:
                return text[start_idx + 1:i], i
        i += 1
    return None, -1


def _split_top_commas(s):
    """按顶层逗号切分（引号内与括号内的逗号不切）。"""
    out = []
    buf = []
    depth = 0
    in_str = None
    i = 0
    while i < len(s):
        ch = s[i]
        if in_str:
            if ch == "\\":
                buf.append(ch)
                if i + 1 < len(s):
                    buf.append(s[i + 1])
                i += 2
                continue
            if ch == in_str:
                in_str = None
            buf.append(ch)
        elif ch in "\"'":
            in_str = ch
            buf.append(ch)
        elif ch in "([{":
            depth += 1
            buf.append(ch)
        elif ch in ")]}":
            depth -= 1
            buf.append(ch)
        elif ch == "," and depth == 0:
            out.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
        i += 1
    if buf:
        out.append("".join(buf))
    return out

def parse_tiers(text):
    """括号配对解析 TAG_WEIGHT_TIERS → {P0:[...], P1:[...], P2:[...]}；失败返回 None。"""
    if not text:
        return None
    m = re.search(r"TAG_WEIGHT_TIERS\s*=\s*\{", text)
    if not m:
        return None
    brace = text.index("{", m.start())
    body, _ = _match_block(text, brace, "{", "}")
    if body is None:
        return None
    out = {}
    for tier in ("P0", "P1", "P2"):
        tm = re.search(r"['\"]" + tier + r"['\"]\s*:\s*\[", body)
        if not tm:
            out[tier] = []
            continue
        br = body.index("[", tm.start())
        inner, _ = _match_block(body, br, "[", "]")
        if inner is None:
            out[tier] = []
            continue
        terms = []
        # 按引号感知切分（r230 自测抓到的自身缺陷：原实现 inner.split(",") 会把
        # 「引号内含逗号」的项切成两半，如 "带,逗号" → '"带' + '逗号"'。
        # 判据自身的解析器必须可证伪，故按字符扫描、只切顶层逗号。）
        for tok in _split_top_commas(inner):
            t = tok.strip()
            if not t:
                continue
            if (t.startswith('r"') and t.endswith('"')) or (t.startswith("r'") and t.endswith("'")):
                t = t[2:-1].replace("\\\\", "\\")
            elif (t.startswith('"') and t.endswith('"')) or (t.startswith("'") and t.endswith("'")):
                t = t[1:-1]
            if t:
                terms.append(t)
        out[tier] = terms
    return out


def measure(tier_text, index_doc):
    """返回 (reading, state)。state ∈ PASS/EXPOSED/UNVERIFIED。"""
    tiers = parse_tiers(tier_text)
    if not tiers:
        return {"why": "清单解析失败或 0 项"}, "UNVERIFIED"
    all_terms = []
    for t in ("P0", "P1", "P2"):
        all_terms += [(t, x) for x in tiers.get(t, [])]
    if not all_terms:
        return {"why": "清单解析出 0 项"}, "UNVERIFIED"
    idx = (index_doc or {}).get("index") if isinstance(index_doc, dict) else None
    if not isinstance(idx, dict) or not idx:
        return {"why": "索引无 index 键或为空"}, "UNVERIFIED"
    live, dead = [], []
    for tier, term in all_terms:
        v = idx.get(term)
        if isinstance(v, list) and v:
            live.append((tier, term, len(v)))
        else:
            dead.append((tier, term, 0 if v is None else len(v or [])))
    p0_terms = [x for (t, x) in all_terms if t == "P0"]
    p0_live = [x for x in p0_terms if x in [d[1] for d in live]]
    reading = {
        "tier_n": len(all_terms),
        "tier_by_level": {t: len(tiers.get(t, [])) for t in ("P0", "P1", "P2")},
        "live_n": len(live),
        "dead_n": len(dead),
        "dead_terms": [d[1] for d in dead],
        "p0_n": len(p0_terms),
        "p0_live_n": len(p0_live),
        "p0_live_terms": p0_live,
        "index_n": len(idx),
        "effective_pct": round(100.0 * len(live) / len(all_terms), 1) if all_terms else 0.0,
        "index_coverage_pct": round(100.0 * len(live) / len(idx), 1) if idx else 0.0,
    }
    if not live:
        return reading, "EXPOSED"
    if dead or not p0_live:
        return reading, "EXPOSED"
    return reading, "PASS"


def selftest():
    ok = True

    def chk(name, cond, got=""):
        if cond:
            print("  [OK  ] " + name)
        else:
            print("  [FAIL] " + name + "  <-- " + str(got))
        return bool(cond)

    def mk(p0, p1, p2):
        def li(xs):
            return "[" + ", ".join('"' + x + '"' for x in xs) + "]"
        return "TAG_WEIGHT_TIERS = {\n    'P0': " + li(p0) + ",\n    'P1': " + li(p1) + ",\n    'P2': " + li(p2) + ",\n}\n"

    idx_ok = {"index": {"甲": ["s1"], "乙": ["s2"], "丙": ["s3"]}}
    r1, s1 = measure(mk(["甲"], ["乙"], ["丙"]), idx_ok)
    ok &= chk("正控：清单全命中 ⇒ PASS", s1 == "PASS" and r1["dead_n"] == 0, (s1, r1.get("dead_n")))
    r2, s2 = measure(mk(["甲"], ["乙", "缺"], ["丙"]), idx_ok)
    ok &= chk("变异：一项清单不在索引 ⇒ EXPOSED 且具名", s2 == "EXPOSED" and r2["dead_terms"] == ["缺"], (s2, r2.get("dead_terms")))
    r3, s3 = measure(mk(["\\bexcel\\b"], ["乙"], ["丙"]), idx_ok)
    ok &= chk("变异：P0 全为正则（索引里无此字面键）⇒ EXPOSED 且 p0_live_n=0",
              s3 == "EXPOSED" and r3["p0_live_n"] == 0, (s3, r3.get("p0_live_n")))
    r4, s4 = measure(mk(["甲"], ["乙"], ["丙"]), {"index": {}})
    ok &= chk("零输入：索引为空 ⇒ UNVERIFIED（禁读成无空转）", s4 == "UNVERIFIED", s4)
    r5, s5 = measure(None, idx_ok)
    ok &= chk("零输入：清单不可读 ⇒ UNVERIFIED", s5 == "UNVERIFIED", s5)
    r6, s6 = measure(mk(["甲"], [], []), idx_ok)
    ok &= chk("空数组值也算空转：索引键在但值为空 ⇒ EXPOSED",
              measure(mk(["甲"], ["空"], []), {"index": {"甲": ["s1"], "空": [], "乙": ["s2"]}})[1] == "EXPOSED")
    nested = "TAG_WEIGHT_TIERS = {\n  'P0': [\"甲\"],\n  'P1': [\"乙\"],\n}\nOTHER = {\"x\": [1,2,3]}\n"
    r7 = parse_tiers(nested)
    ok &= chk("解析器可证伪：嵌套/后续字典不污染（P0=1,P1=1）",
              r7 is not None and r7.get("P0") == ["甲"] and r7.get("P1") == ["乙"], r7)
    r8 = parse_tiers("TAG_WEIGHT_TIERS = {\n  'P0': [\"含#号\", \"带,逗号\"],\n}\n")
    ok &= chk("解析器不误切：引号内的 # 与 , 不破坏配对",
              r8 is not None and r8.get("P0") == ["含#号", "带,逗号"], r8)
    print("[TAGFACE:SELFTEST-" + ("PASS" if ok else "FAIL") + "]")
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="只读看守焚诀 Tag 层有效匹配面")
    ap.add_argument("--tier", default=os.path.join(FENJUE_EVAL, "tag_layer.py"))
    ap.add_argument("--index", dest="index_path", default=os.path.join(FENJUE_EVAL, "skill_tags.json"))
    ap.add_argument("--json", dest="out", default=None)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    if args.selftest:
        return selftest()
    tier_text = read_text(args.tier)
    idx_doc = None
    idx_text = read_text(args.index_path)
    if idx_text is not None:
        try:
            idx_doc = json.loads(idx_text)
        except ValueError:
            idx_doc = None
    reading, state = measure(tier_text, idx_doc)
    out = {
        "schema": "tag-face-r230-v1",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00"),
        "cmd": "python 05-exec/r230_tag_face.py",
        "inputs": {"tier": os.path.relpath(args.tier, ROOT).replace(os.sep, "/"),
                   "index": os.path.relpath(args.index_path, ROOT).replace(os.sep, "/")},
        "state": state, "reading": reading,
        "caveat": "本件只读焚诀仓（红线 6）；缺陷须由焚诀会话按 r229 建议修，本仓不代改。",
    }
    if not args.quiet:
        print("焚诀 Tag 层有效匹配面（清单 = " + out["inputs"]["tier"] + "）")
        if state == "UNVERIFIED":
            print("  " + str(reading.get("why", "输入不可用")))
        else:
            print("  清单项 " + str(reading["tier_n"]) + " ｜生效 " + str(reading["live_n"])
                  + " ｜空转 " + str(reading["dead_n"]) + "（清单面有效率 " + str(reading["effective_pct"])
                  + "% / 索引面覆盖率 " + str(reading["index_coverage_pct"]) + "%）")
            print("  P0 项 " + str(reading["p0_n"]) + " ｜P0 生效 " + str(reading["p0_live_n"]))
            if reading["dead_terms"]:
                print("  空转项（前 12）：" + ", ".join(reading["dead_terms"][:12]))
    if args.out:
        tmp = args.out + ".tmp"
        with io.open(tmp, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(out, fh, ensure_ascii=False, indent=1)
        os.replace(tmp, args.out)
        print("JSON -> " + os.path.relpath(args.out, ROOT))
    if state == "UNVERIFIED":
        print(TOK_UNV + " 输入面不可读/零项 ⇒ 不判，禁读成「无空转」")
        return 2
    if state == "EXPOSED":
        print(TOK_EXP + " 空转 " + str(reading["dead_n"]) + " 项、P0 生效 " + str(reading["p0_live_n"])
              + " 项 ⇒ 缺陷在位（归属焚诀仓，本仓只报不改）")
        return 1
    print(TOK_PASS + " 全部 " + str(reading["tier_n"]) + " 项均命中索引且 P0 有生效项")
    return 0


if __name__ == "__main__":
    sys.exit(main())
