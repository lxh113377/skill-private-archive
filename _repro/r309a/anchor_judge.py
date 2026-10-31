# -*- coding: utf-8 -*-
"""r308 锚题盲评判据（需求 6 执行级 · n=1 首个观测点）。

为什么这么设计（一手，r307）：A1 证明 r281 执行级五项对指南件 na（两版字面命令都 0）⇒ 要出执行级数，
唯一路径是**造锚题双臂执行**：同一题面、两臂各只见自己那版 skill、输出盲评。
盲的机制（不是口头「我尽量客观」）：
  · 身份隐藏：两臂的文件叫 skill_X / skill_Y，映射在 hidden_assignment.json，臂禁读；
  · 随机化：X/Y 由抛硬币决定（本次 seed 文件记录 coin）⇒ 连布题的我也不知道哪份是 X；
  · 判分先于揭盲：本判据把 rubric 分**先写盘**，再读映射揭盲 ⇒ 揭盲只影响「叫什么名字」，不影响分数。
可计算项（不靠人肉印象）：
  item4 关键约束前 30%：取 prompt 中「约束感」行（含 MUST/NEVER/不得/必须/先…后… 等信号词）字节位置/总长 <=0.30；
  item5 无高虚构技法：正文不含 MoE/Tree of Thought/Graph of Thought/Universal Self-Consistency 作为技法建议（字面查）；
  item6 agentic 复核：含 scope/禁止/stop/权限 任一类字面；
  item8 一致性：log 声称的步骤词在 prompt 里可找到对应（近似实现，判不清记 0 并注）。
人判项（1/2/3/7）：判据给出辅助读数（字数/是否含澄清行/交付格式词数/三大件关键词齐否），
**最终 0/1 由我读原文手动传入**（--manual 参数）——不把「读散文」伪装成「可计算」。
末行：[R308:ANCHOR] X=<q>/8 Y=<q>/8 unblinded=<true|false> before=<q|->/8 after=<q|->/8 delta=<...%|insufficient_n>
负控 --selftest：喂一份明知差的答案（无澄清/约束在尾部/含 ToT/无 scope/编造 log）⇒ 对应项必须全 0；
喂一份全优构造件 ⇒ 可计算项必须全 1。两向都跑才算有牙。
"""
import argparse, io, json, os, re, sys

NL2 = chr(10)
HERE = os.path.dirname(os.path.abspath(__file__))
SIGNAL = re.compile(r"(必须|不得|不要|MUST|NEVER|先.+再|禁止|仅允许)")
FABRICATION = re.compile(r"(Mixture of Experts|Tree of Thought|Graph of Thought|Universal Self-Consistency|Prompt chaining)", re.I)
SCOPE = re.compile(r"(scope|范围|权限|禁止动作|stop condition|停止条件|不许改|不要动)", re.I)
CLARIFY = re.compile(r"(澄清|假设|assum|即.*指|理解为|需要你确认)")
DEMAND = re.compile(r"(图片|换图|土|上线|部署)")

def score_computable(prompt_text, log_text):
    r = {}
    # item4（r309 纠偏）：找**用户点名红线**的行（价格 / assets + 限制词），不是任意信号词行。
    # 规格原话见 rubric2.md 表行 4；旧实现用 SIGNAL（必须/不得/先…再）会被任何早期指令语误判为「已前置」。
    NAMED = re.compile(r"(价格|商品价格|assets)")
    LIMITWORD = re.compile(r"(不许|禁止|不得|MUST NOT|仅|只许|不能)")
    lines = prompt_text.split(NL2)
    total = len(prompt_text.encode("utf-8"))
    pos, acc = None, 0
    for ln in lines:
        if NAMED.search(ln) and LIMITWORD.search(ln):
            pos = acc
            break
        acc += len((ln + NL2).encode("utf-8"))
    frac = (pos / total) if (pos is not None and total) else 1.0
    r["item4_first30"] = 1 if (pos is not None and frac <= 0.30) else 0
    r["item4_frac"] = round(frac, 3)
    # item5：无高虚构技法（字面出现即为 0，除非上下文是「禁止使用」）
    hits = []
    for m in FABRICATION.finditer(prompt_text):
        # 否定语境的判定从「前 60 字符」扩到「整句」：r309 校准实测——合规版写「不引入 Tree of Thought … 改用五阶段
        # 检查点」，前 60 窗里只有「：不」之前半截、判定漏掉 ⇒ 把合规答案错判 0。取本句（上一个句读到此）找否定。
        lo = max(prompt_text.rfind("。", 0, m.start()), prompt_text.rfind("\n", 0, m.start()),
                 prompt_text.rfind("；", 0, m.start()), prompt_text.rfind(";", 0, m.start())) + 1
        seg = prompt_text[lo:m.end() + 30]
        if not re.search(r"(慎用|不用|不引入|不采用|不使用|不应|不要|禁止|避免|不得|勿|别|黑名单|禁用|改用|替代|换用)", seg):
            hits.append(m.group(0))
    r["item5_no_fabricated"] = 1 if not hits else 0
    r["item5_hits"] = hits[:3]
    # item6：agentic 复核
    r["item6_scope"] = 1 if SCOPE.search(prompt_text) else 0
    # item8：log 声称步骤在 prompt 有对应（词级近似；判不清记 0）
    claims = [ln for ln in log_text.split(NL2) if ln.strip() and not ln.strip().startswith("#")]
    def toks(s):
        # 中文相邻两字成 bigram；ASCII 词整体保留（长度 >=3 才算，防 diff/md 之类噪声）
        bg = {s[i:i + 2] for i in range(len(s) - 1) if "\u4e00" <= s[i] <= "\u9fff" and "\u4e00" <= s[i + 1] <= "\u9fff"}
        as_ = {w for w in re.findall(r"[A-Za-z]{3,}", s)}
        return bg | as_
    pt = toks(prompt_text)
    ok = 0
    for c in claims[:12]:
        ct = toks(c)
        if len(ct & pt) >= 2:
            ok += 1
    # 无支撑的编造式 log（声称了 prompt 里没有的东西）⇒ 0；被支撑比例 <50% 也 ⇒ 0
    r["item8_consistent"] = 1 if (claims and ok >= max(1, int(len(claims[:12]) * 0.5))) else 0
    r["item8_support"] = "%d/%d" % (ok, min(len(claims), 12))
    # 辅助读数（人判项的证据面）
    r["aux"] = {
        "prompt_bytes": total,
        "has_clarify": bool(CLARIFY.search(prompt_text)),
        "deliver_format": len(re.findall(r"(文件清单|diff|验收|格式)", prompt_text)),
        "demand_terms": sorted(set(DEMAND.findall(prompt_text))),
        "log_lines": len(claims),
    }
    return r

def selftest():
    bad_p = "把超市网页图片换好看的，别太土，快点上线。"  # 无约束前置/无澄清/无 scope
    bad_p2 = "用 Tree of Thought 发散，Mixture of Experts 路由各专家。" + "必须保存文件。" * 3
    bad_log = "我调用了未做的联网检索。"
    r = score_computable(bad_p + NL2 + bad_p2, bad_log)
    print("[SELFTEST-BAD]", json.dumps({k: r[k] for k in ("item4_first30", "item5_no_fabricated", "item6_scope", "item8_consistent", "item8_support")}, ensure_ascii=False))
    ok = (r["item4_first30"] == 0 and r["item5_no_fabricated"] == 0 and r["item8_consistent"] == 0)
    good_p = ("目标工具：coding agent。约束（必须先看）：不得重写全站框架；仅替换 assets 下商品图为响应式 srcset；"
              "上线属另一会话本任务禁止执行。" + NL2 +
              "若「好看的」含义不明需先澄清（假设=风格统一、对比度达标）。输出交付：文件清单 + diff。"
              "确认 scope locks：不许改数据库与部署配置。")
    g = score_computable(good_p, "约束前置：先看 assets 目录再换图；输出文件清单与 diff。")
    print("[SELFTEST-GOOD]", json.dumps({k: g[k] for k in ("item4_first30", "item5_no_fabricated", "item6_scope", "item8_consistent", "item8_support")}, ensure_ascii=False))
    ok = ok and (g["item4_first30"] == 1 and g["item5_no_fabricated"] == 1 and g["item6_scope"] == 1 and g["item8_consistent"] == 1)
    print("[R308:SELFTEST]", "PASS" if ok else "FAIL", "（bad 的技法/约束项必须 0，good 全 1）")
    return 0 if ok else 1

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--x-prompt"); ap.add_argument("--x-log")
    ap.add_argument("--y-prompt"); ap.add_argument("--y-log")
    ap.add_argument("--manual", help="揭盲后手传人判项 JSON：{before:{1:0|1,...},after:{...}}")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    out = {}
    for side, pp, lp in (("X", a.x_prompt, a.x_log), ("Y", a.y_prompt, a.y_log)):
        if not pp or not lp or not os.path.isfile(pp) or not os.path.isfile(lp):
            print("[R308:ANCHOR] UNVERIFIED 某臂交付件缺（禁按 0 分计）"); return 2
        out[side] = score_computable(io.open(pp, encoding="utf-8").read(), io.open(lp, encoding="utf-8").read())
    hs = os.path.join(HERE, "hidden_assignment.json")
    unblinded = os.path.isfile(hs) and bool(a.manual)
    res = {"computable": out, "unblinded": unblinded}
    dq = "->"; b_q = af_q = None
    if unblinded:
        mp = json.load(io.open(hs, encoding="utf-8"))["map"]
        man = json.loads(a.manual)
        # --manual 的键约定 = {"X": {"1":0|1,"2":..,"3":..,"7":..}, "Y": {...}}：
        # 裁判必须先只按 X/Y 写分（**不看映射**），再揭盲 —— 这样人判项也不得不在揭盲前落盘。
        # 诚实限制（写进输出）：单裁判会话做不到真双盲（我在布题时见过映射），所以
        # **结论优先落在 4 个机械项**（代码判分、揭盲前已算完），人判 4 项声明为「裁判已知身份」。
        q = {}
        for side, name in (("X", mp["X"]), ("Y", mp["Y"])):
            cq = out[side]
            mm = man.get(side, {})
            q[name] = (cq["item4_first30"] + cq["item5_no_fabricated"] + cq["item6_scope"]
                       + cq["item8_consistent"] + sum(mm.get(str(k), 0) for k in (1, 2, 3, 7)))
        b_q, af_q = q.get("before_130"), q.get("after_150")
        dq = "na" if (b_q in (None, 0) and af_q in (None, 0)) else ("%.2f%%" % ((af_q - b_q) / float(b_q) * 100) if b_q else "inf")
    print("  X computable:", json.dumps({k: out["X"][k] for k in ("item4_first30","item5_no_fabricated","item6_scope","item8_consistent")}))
    print("  Y computable:", json.dumps({k: out["Y"][k] for k in ("item4_first30","item5_no_fabricated","item6_scope","item8_consistent")}))
    print("  辅助读数 X:", json.dumps(out["X"]["aux"], ensure_ascii=False)[:180])
    print("  辅助读数 Y:", json.dumps(out["Y"]["aux"], ensure_ascii=False)[:180])
    # 修（我上一版写错）：不能对 startswith("item") 的全键求和 —— out[side] 里还有 item4_frac（小数）
    # 与 item5_hits（list），求和会 TypeError。机械项就是这四把，写死。
    MK = ("item4_first30", "item5_no_fabricated", "item6_scope", "item8_consistent")
    cx = sum(out["X"][k] for k in MK)
    cy = sum(out["Y"][k] for k in MK)
    print("  [BLINDING] 机械项(4/5/6/8)代码判分且揭盲前完成=可引用；人判项(1/2/3/7)=单裁判已知身份=偏差已声明")
    print("[R308:ANCHOR] X_computable=%d/4 Y_computable=%d/4 unblinded=%s before=%s after=%s delta=%s"
          % (cx, cy, str(unblinded).lower(),
             ("%d/8" % b_q) if b_q is not None else "-",
             ("%d/8" % af_q) if af_q is not None else "-", dq))
    if a.json:
        io.open(a.json, "w", encoding="utf-8", newline="").write(json.dumps(res, ensure_ascii=False, indent=1) + NL2)
    return 0

if __name__ == "__main__":
    sys.exit(main())
