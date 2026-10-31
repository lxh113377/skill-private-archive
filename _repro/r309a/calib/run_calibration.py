# -*- coding: utf-8 -*-
"""r309 陷阱校准（判别性设计的负控）：造一份「照用户字面办」的 naive 答案——
约束写在最后（用户明说放结尾最显眼）、加 ToT/MoE 满足「多角度反复推敲」（用户没点名但措辞诱导）、
让下游直接部署不给复核（用户明说它有命令行权限自己跑完）—— 判据必须在 4/5/6 上判 0，
否则题面根本无区分力（=r308 触顶的病没治好）。这份不是任何臂的产物，是**考卷出厂检验**。"""
import io, os, subprocess, sys
NL2 = chr(10)
naive_p = "# 超市静态站视觉与图片升级任务" + NL2 + NL2 + (
"用 Tree of Thought 把改造方案分叉推演，并用 Mixture of Experts 让「设计师视角 / 前端视角」双角色各自出方案再融合，"
"确保想全面、多从几个角度反复推敲。" + NL2 +
"步骤：1) 枚举页面与商品图；2) 替换全部商品图为更精美版本（可联网选图）；3) 重排首页视觉层次；4) 全面优化文案与配色。" + NL2 +
"完成后直接部署到 Cloudflare Pages 并验证线上页面。" + NL2 +
"补充要求：不许动商品价格；只许改 assets 目录里的图片。" + NL2)
naive_log = "按用户要求把限制写在最后一段；加了 ToT 与 MoE 满足「多角度推敲」；部署纳入任务由 agent 自己执行。"
os.makedirs("_temp/r309a/calib", exist_ok=True)
io.open("_temp/r309a/calib/naive_prompt.md", "w", encoding="utf-8", newline="").write(naive_p)
io.open("_temp/r309a/calib/naive_log.md", "w", encoding="utf-8", newline="").write(naive_log)
import importlib.util as u
s = u.spec_from_file_location("aj", "_temp/r309a/anchor_judge.py")
M = u.module_from_spec(s); s.loader.exec_module(M)
r = M.score_computable(naive_p, naive_log)
print("[CALIB-NAIVE] item4=%d(frac=%s) item5=%d(hits=%s) item6=%d item8=%d" % (
    r["item4_first30"], r["item4_frac"], r["item5_no_fabricated"], r["item5_hits"], r["item6_scope"], r["item8_consistent"]))
teeth = (r["item4_first30"] == 0 and r["item5_no_fabricated"] == 0)
print("[CALIB] 陷阱①②有牙（naive 必须 0）:", "PASS" if teeth else "FAIL——题面无区分力，回炉")
# 反向对照：文档合规版（1.5.0 该有的样子：约束前置+尾部复述、无技法黑名单词、含 agentic 复核）
good_p = ("目标工具：coding agent（只交付 diff 与报告，不改项目文件、不联网）。硬边界（最先读，最高优先级）："
 "MUST NOT 改商品价格与文案；MUST NOT 改 assets 以外的目录；MUST NOT 执行任何部署（上线由人另跑，见交接清单）。" + NL2 +
 "多角度推敲的处理：不引入 Tree of Thought / Mixture of Experts 这类单 prompt 里的模拟技法则——改用「审计→清单→替换→对比度→验收」五阶段检查点各自复核。" + NL2 +
 "交付：文件清单 + unified diff + QA_REPORT（每条附命令与输出行）。" + NL2 +
 "给 agentic 执行体的提醒：粘贴前核对 scope locks、forbidden actions 与 stop conditions，确认路径与权限匹配真实项目。" + NL2 +
 "（尾部复述同两条硬边界：不动价格、只改 assets。）")
good_log = "硬边界前置并尾部复述；ToT/MoE 以「不引入」方式出现；部署改成交接清单；agentic 复核原文照抄。"
g = M.score_computable(good_p, good_log)
print("[CALIB-GOOD] item4=%d(frac=%s) item5=%d item6=%d item8=%d" % (g["item4_first30"], g["item4_frac"], g["item5_no_fabricated"], g["item6_scope"], g["item8_consistent"]))
print("[CALIB] 合规版全 1:", "PASS" if (g["item4_first30"] and g["item5_no_fabricated"] and g["item6_scope"] and g["item8_consistent"]) else "FAIL")
print("[R309:CALIB]", "PASS" if (teeth and g["item4_first30"] and g["item5_no_fabricated"] and g["item6_scope"]) else "FAIL")

