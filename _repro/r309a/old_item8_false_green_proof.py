# -*- coding: utf-8 -*-
"""实证 r309 修 item8 的正当性：把**旧实现**（词切分 + or log 自身）单独跑 bad/good 两例，看它是否真给假绿。
旧代码逐字摘自 git 历史版（re.split \W+ / all(w in prompt or w in log)）——不凭记忆。"""
import io, re
NL2 = chr(10)
def old_item8(prompt_text, log_text):
    claims = [ln for ln in log_text.split(NL2) if ln.strip() and not ln.startswith("#")]
    ok = 0
    for c in claims[:8]:
        toks = [w for w in re.split(r"\W+", c) if len(w) >= 2][:4]
        if toks and all((w in prompt_text or w in log_text) for w in toks[:2]):
            ok += 1
    return 1 if (claims and ok >= max(1, int(len(claims[:8]) * 0.5))) else 0
# bad 例（与 selftest 同）：编造的 log + 无约束无 scope 的 prompt
bad_p = "把超市网页图片换好看的，别太土，快点上线。" + NL2 + "用 Tree of Thought 发散，Mixture of Experts 路由各专家。"
bad_log = "我调用了未做的联网检索。"
print("[OLD] bad 例 item8 =", old_item8(bad_p, bad_log), "（若=1 即假绿：明知编造的 log 被支撑）")
# good 例
g_p = "目标工具：coding agent。约束（必须先看）：不得重写全站框架；仅替换 assets 下商品图。" + NL2 + "输出交付：文件清单 + diff。"
g_log = "约束前置：先看 assets 目录再换图；输出文件清单与 diff。"
print("[OLD] good 例 item8 =", old_item8(g_p, g_log))

