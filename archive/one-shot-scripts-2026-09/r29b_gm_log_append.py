# -*- coding: utf-8 -*-
"""r29b_gm_log_append.py — 一次性：把「H1/H3 补做」条目 + footer 锚点块追加到当日 GM 日志。"""
import sys
from datetime import datetime
from pathlib import Path

LOG = Path(r"D:\global_memory\memory") / (datetime.now().strftime("%Y-%m-%d") + ".md")
sid = "r29b-h1h3-" + datetime.now().strftime("%H%M%S")
ts = datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")

body = """

## 第 29 轮 r29b（H1/H3 补做 · 由用户对「未闭环」行的标注触发）

- **推翻了自己一小时前写下的「被阻塞」判断**：r29 收尾时把 H1 记成"落点 `A-skill-manager/SKILL.md` 被并行会话占用，待窗口"。复测动作的真实落点才看清 —— 新建技能的规则不在壳文件里，而在 `assets/creator/init_skill.py`（骨架生成器）与 `references/lifecycle-create.md`（硬规则卷），**这两个文件当时都是干净的**，"壳被占用"根本不构成整件事的阻塞条件。
- **已落地（受管根 `afe0f13`，3 文件 32 行）**：新建技能正文强制三段 —— ① 反理性化表（借口 + 逐条反驳；写不出真实借口 = 还没摸清这技能会在哪儿出错）；② 验证（可执行判据 / 反例 / 未达成时的表述，三样都要）；③ 破坏性命令作用域守卫（删除/覆盖/移动必须限定作用域前缀，优先移入回收而非抹除）。依据 = 本系列实测最硬的缺口 rationalizations 13.9% vs addyosmani 96.0%（差 82.1pt，宽窄两口径差值 +0.0，无等价写法可兜底）。
- **机器型优先**：不只写规则文本 —— `init_skill.py` 生成的骨架实含三段（真跑取证），`quick_validate.py` 对缺段给提醒（提醒级不阻断，否则存量 167 项集体变红属越界改动）；顺手修 `skill_md.read_text()` 未指定编码在中文正文下抛 UnicodeDecodeError。
- **边界守住**：`SKILL.md` 与 `references/version-history.md` 仍是他人 in-flight（`M`），**未夹带**，故本轮**未升版本号**（升版必改该二文件），已在提交信息里写明并登记待其收口后一并升。
- 复验：py_compile PASS；校验器三侧（新骨架无提醒 / `canvas-design`+`code-review` 出提醒 / 退出码恒 0 无回归）；`check-skill-mirror -Fix` 后 `[GATE:mirror-pass] mismatch=0`；四门禁 `mirror=noise=evolution=stub=pass` 全绿（noise 本轮转绿，他人 GM 根文件已由其归属方处理）；焚诀 verify 32 PASS / 1 FAIL，唯一 FAIL 仍是开工前既存的他人 `C20`。
- **可复用判据（写给自己）**：把"某文件在途"当成"整件事被阻塞"之前，先查清动作的真实落点文件 —— 占用面往往只是壳。

<!-- footer:begin session=__SID__ ts=__TS__ -->
[skill清单] 本轮调用=2 个 (A-skill-manager, A-memory-start)
[升级建议] skill=A-skill-manager | 五问=缺失步骤 | 改法=新建技能模板强制三段含作用域守卫 | 对照=已取(证据=真跑生成骨架实含三段且校验器三侧行为符合预期，存量技能零变红) | 状态=已闭环(证据=D:\\global_skills\\A-skill-manager\\assets\\creator\\init_skill.py#backup:20260924_234957_122550)
<!-- footer:end -->
""".replace("__SID__", sid).replace("__TS__", ts)

with LOG.open("a", encoding="utf-8", newline="\n") as fh:
    fh.write(body)
print("APPENDED %dB -> %s" % (len(body.encode("utf-8")), LOG))
