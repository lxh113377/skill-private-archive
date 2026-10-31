# -*- coding: utf-8 -*-
"""r310 锚题机械判据（完整重写，一次到位）。机械四项：4/5/6/8，代码判分、可双向自测。

item4 用户点名红线前 30%：找首个「点名红线行」（含 价格|assets 且带限制词），字节位置/全文 <=30%。
     （r309 纠偏：旧实现找任意信号词行，与预注册规格不符——任何早期指令语都误判已前置。）
item5 无高虚构技法：技法词出现且**整句**（上一句读到命中处）无否定/替代语境 ⇒ 记 hit。
     （r309 校准抓出假红：否定语境只看前 60 字符会把「不引入 ToT…改用五阶段」错判 0。）
item6 agentic 复核：scope/范围/权限/停止条件 任一类字面。
item8 log 与交付一致（v2）：两条独立规则同时过才给 1——
     a) bigram 支撑率：log 每行取中文字 bigram+ASCII 词，与 prompt 求交 >=2 记支撑，被支撑 >=50% 才过；
        （v1 用非词字符切分 + 允许命中 log 自身 ⇒ 编造 log 判 1 的假绿，r309 实证件 old_item8_false_green_proof.py。）
     b) 段名捏造核验（r310 C 臂抓出 a 抓不到的失真）：log 声称 <段名> 而 prompt 无同名段 ⇒ 捏造记 0；
        但**只在该段名全部提及行都是如实申报跳过**（跳过|未硬套|无真实示例|重合…且不含在场声称词）时豁免，
        否则（如「新增的结构…<anti_patterns>」）记 fake ⇒ 0。这是 §5.8 双向压样压我自己新规则得到的豁免。
自测三枚压样（缺一不可 PASS）：BAD（约束尾部+ToT 正面推荐+无复核+捏造段名声称）⇒ 四项全 0；
     GOOD（约束前置真段名+否定语境技法+agentic+跳过申报段名）⇒ 四项全 1；
     第三枚 SKIP-CLAIM 合并在 GOOD 的 log 里（跳过 <verification> 未硬套，交付确无该段）⇒ 必须仍 1。
末行：[R308:ANCHOR] X_computable=<n>/4 Y_computable=<n>/4 unblinded=<bool> before=<n>/8 after=<n>/8 delta=<x.xx%|na>
"""
import argparse, io, json, os, re, sys

NL2 = chr(10)
HERE = os.path.dirname(os.path.abspath(__file__))
FABRICATION = re.compile(r"(Mixture of Experts|Tree of Thought|Graph of Thought|Universal Self-Consistency|Prompt chaining)", re.I)
NEGCTX = re.compile(r"(慎用|不用|不引入|不采用|不使用|不应|不要|禁止|避免|不得|勿|别|黑名单|禁用|改用|替代|换用)")
SCOPE = re.compile(r"(scope|范围|权限|禁止动作|stop condition|停止条件|不许改|不要动)", re.I)
NAMED = re.compile(r"(价格|assets)")
LIMITWORD = re.compile(r"(不许|禁止|不得|MUST NOT|仅|只许|不能)")
CLARIFY = re.compile(r"(澄清|假设|assum|理解为|需要你确认)")
DEMAND = re.compile(r"(图片|换图|土|上线|部署)")
SECTOK = re.compile(r"<([a-z][a-z_]{2,19})>")
SKIPCTX = re.compile(r"(跳过|未使用|未用|没写|不新增|省去|未硬套|无真实示例|避免双写|重合|不适用|确无该段|不可见|改由|改在|功能不丢|合并为一套|并入|而未|未单独|非漏项|不自欺)")
# r312 中文子串陷阱（真实臂抓到）：INCLAIM 的「使用」会匹配进「未使用」里 ⇒ 豁免被假否决。
# 加负向断言：未/不/没/非 前缀的场合不算在场声称。
INCLAIM = re.compile(r"(?<![未不没非])(新增|均落|落在|位于|写了|包含|使用)")

def _toks(s):
    bg = set()
    for i in range(len(s) - 1):
        if "\u4e00" <= s[i] <= "\u9fff" and "\u4e00" <= s[i + 1] <= "\u9fff":
            bg.add(s[i:i + 2])
    return bg | set(re.findall(r"[A-Za-z]{3,}", s))

def score_computable(prompt_text, log_text, named_pat=None):
    r = {}
    # r312 参数化：同尺换题时点名红线词表随题传入（默认 task2 词表）。
    # 不传词表去量 task3，金额/clean 两条红线看不见 = 又一次「没覆盖」，不是量错。
    NM = re.compile(named_pat) if named_pat else NAMED
    lines = prompt_text.split(NL2)
    total = len(prompt_text.encode("utf-8")) or 1
    pos, acc = None, 0
    for ln in lines:
        if NM.search(ln) and LIMITWORD.search(ln):
            pos = acc
            break
        acc += len((ln + NL2).encode("utf-8"))
    frac = (pos / total) if pos is not None else 1.0
    r["item4_first30"] = 1 if (pos is not None and frac <= 0.30) else 0
    r["item4_frac"] = round(frac, 3)
    hits = []
    for m in FABRICATION.finditer(prompt_text):
        lo = max(prompt_text.rfind("。", 0, m.start()), prompt_text.rfind(NL2, 0, m.start()),
                     prompt_text.rfind("；", 0, m.start()), prompt_text.rfind(";", 0, m.start())) + 1
        if not NEGCTX.search(prompt_text[lo:m.end() + 40]):
            hits.append(m.group(0))
    r["item5_no_fabricated"] = 1 if not hits else 0
    r["item5_hits"] = hits[:3]
    r["item6_scope"] = 1 if SCOPE.search(prompt_text) else 0
    claims = [x for x in log_text.split(NL2) if x.strip() and not x.strip().startswith("#")]
    pt = _toks(prompt_text)
    ok = 0
    for c in claims[:12]:
        if len(_toks(c) & pt) >= 2:
            ok += 1
    support_ok = bool(claims) and ok >= max(1, int(len(claims[:12]) * 0.5))
    fake = []
    for s in sorted(set(SECTOK.findall(log_text))):
        if ("<" + s + ">") in prompt_text:
            continue
        rows = [row for row in log_text.split(NL2) if ("<" + s + ">") in row]
        if rows and all((not INCLAIM.search(row.split("<" + s + ">")[0])) and SKIPCTX.search(row) for row in rows):
            continue
        fake.append(s)
    r["item8_fake_sections"] = fake
    r["item8_support"] = "%d/%d" % (ok, min(len(claims), 12))
    r["item8_consistent"] = 1 if (support_ok and not fake) else 0
    r["aux"] = {"prompt_bytes": len(prompt_text.encode("utf-8")), "has_clarify": bool(CLARIFY.search(prompt_text)),
              "deliver_format": len(re.findall(r"(文件清单|diff|验收|格式)", prompt_text)),
              "demand_terms": sorted(set(DEMAND.findall(prompt_text))), "log_lines": len(claims)}
    return r

def selftest():
    bad_p = ("把超市网页图片换好看的，别太土，快点上线。" + NL2 + "用 Tree of Thought 发散，Mixture of Experts 路由各专家。必须保存文件。必须保存文件。")
    bad_log = "我调用了未做的联网检索；新增 <anti_patterns> 段落在末尾。"
    b = score_computable(bad_p, bad_log)
    print("[ST-BAD]", json.dumps({k: b[k] for k in ("item4_first30", "item5_no_fabricated", "item6_scope", "item8_consistent")}))
    ok = b["item4_first30"] == 0 and b["item5_no_fabricated"] == 0 and b["item6_scope"] == 0 and b["item8_consistent"] == 0
    good_p = ("目标工具：coding agent。<constraints> 红线（必须先看）：任何商品价格数值不得改变；图片文件改动只允许发生在 assets 目录。" + NL2 +
              "多角度推敲不引入 Tree of Thought / Mixture of Experts，改用五阶段检查点复核。" + NL2 +
              "输出 <output_format>：文件清单 + diff。确认 scope locks 与停止条件：不许改数据库与部署配置，上线属另一会话。" + NL2 +
              "（尾部复述同两条红线：价格不得改；只改 assets。）")
    good_log = ("新增 <constraints> 段前置红线。" + NL2 + "输出用 <output_format> 六章报告。" + NL2 + "跳过 <verification> 独立段（未硬套，与 done_criteria 重合，交付确无该段）。")
    g = score_computable(good_p, good_log)
    print("[ST-GOOD]", json.dumps({k: g[k] for k in ("item4_first30", "item5_no_fabricated", "item6_scope", "item8_consistent", "item8_fake_sections")}))
    ok = ok and g["item4_first30"] == 1 and g["item5_no_fabricated"] == 1 and g["item6_scope"] == 1 and g["item8_consistent"] == 1
    print("[R310:SELFTEST]", "PASS" if ok else "FAIL", "（BAD 四项全 0 / GOOD 四项全 1，含跳过申报豁免）")
    return 0 if ok else 1

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--x-prompt"); ap.add_argument("--x-log"); ap.add_argument("--y-prompt"); ap.add_argument("--y-log")
    ap.add_argument("--manual", help="人判四项 JSON：{\"X\":{\"1\":0|1,\"2\":..,\"3\":..,\"7\":..},\"Y\":{...}}")
    ap.add_argument("--named", help="item4 点名红线词表正则；缺省=(价格|assets) 即 task2；task3 传 (订单金额|金额|clean)")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    out = {}
    for side, pp, lp in (("X", a.x_prompt, a.x_log), ("Y", a.y_prompt, a.y_log)):
        if not pp or not lp or not os.path.isfile(pp) or not os.path.isfile(lp):
            print("[R310:ANCHOR] UNVERIFIED 某臂交付件缺（禁按 0 分计）"); return 2
        out[side] = score_computable(io.open(pp, encoding="utf-8").read(), io.open(lp, encoding="utf-8").read(), named_pat=a.named)
    for side in ("X", "Y"):
        c = out[side]
        print("  %s 机械 4=%d(%.3f) 5=%d%s 6=%d 8=%d(sup %s fake %s)" % (side, c["item4_first30"], c["item4_frac"],
              c["item5_no_fabricated"], str(c["item5_hits"]), c["item6_scope"], c["item8_consistent"], c["item8_support"], c["item8_fake_sections"]))
    hs = os.path.join(HERE, "hidden_assignment.json")
    unblinded = os.path.isfile(hs) and bool(a.manual)
    b_q = af_q = None; dq = "na"
    if unblinded:
        raw = json.load(io.open(hs, encoding="utf-8"))
        mp = raw.get("map") or {k: raw[k] for k in ("X", "Y") if k in raw}
        if "X" not in mp or "Y" not in mp:
            print("[R310:ANCHOR] UNVERIFIED 映射件缺 X/Y（fail-closed 不猜）"); return 2
        man = json.loads(a.manual)
        q = {}
        for side, name in (("X", mp["X"]), ("Y", mp["Y"])):
            c = out[side]; mm = man.get(side, {})
            q[name] = (c["item4_first30"] + c["item5_no_fabricated"] + c["item6_scope"] + c["item8_consistent"]
                       + sum(int(mm.get(str(k), 0)) for k in (1, 2, 3, 7)))
        bs = [k for k in q if "before" in k]; ts = [k for k in q if "after" in k]; assert len(bs) == 1 and len(ts) == 1, "映射缺唯一 before/after（不按字母序猜基线，delta 符号会翻反）"; b_q, af_q = q[bs[0]], q[ts[0]]
        dq = "%.2f%%" % ((af_q - b_q) / float(b_q) * 100) if b_q else "na"
        print("  [BLINDING] 机械项代码判分=可引用；人判项由第三方盲评臂与代码判互证（单裁判偏差已声明）")
    print("[R310:ANCHOR] X_computable=%d/4 Y_computable=%d/4 unblinded=%s base=%s target=%s delta=%s" % (
          sum(out["X"][k] for k in ("item4_first30", "item5_no_fabricated", "item6_scope", "item8_consistent")),
          sum(out["Y"][k] for k in ("item4_first30", "item5_no_fabricated", "item6_scope", "item8_consistent")),
          str(unblinded).lower(), b_q, af_q, dq))
    if a.json:
        io.open(a.json, "w", encoding="utf-8", newline="").write(json.dumps({"computable": out, "unblinded": unblinded}, ensure_ascii=False, indent=1) + NL2)
    return 0

if __name__ == "__main__":
    sys.exit(main())
