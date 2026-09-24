# P1-1 description 双要素基线报告

> 生成：2026-09-24 08:56 ｜ 扫描根：`D:\global_skills` ｜ 工具：`05-exec/description_baseline_scan.py`（只读）
> 口径：anthropics/skills 官方 —— description = 触发第一信号，需「做什么 + 何时用」双要素；机器判定为启发式（触发标记词表 + 长度 ≥15），语义盲区见「已知盲区」。

## 总览

| 指标 | 值 |
|---|---|
| SKILL.md 总数 | 151 |
| frontmatter 解析错误 | 0 |
| 无/空 description | 0 |
| 含触发标记（何时用） | 98 |
| 双要素达标 | 98 |
| 长度 min/median/max | 23 / 233 / 1019 |

## 最短 Top10（优先整改候选）

| skill | 长度 | 触发标记 | description 摘录 |
|---|---|---|---|
| screenshot | 23 | ✗ | 桌面截图/窗口截屏/区域截取工具。桌面截图工具 |
| spike | 23 | ✗ | 跑一次性原型验证技术可行性。技术可行性原型验证 |
| testing | 23 | ✗ | 编写和运行测试验证代码正确性。测试编写运行引擎 |
| web-design-guidelines | 27 | ✗ | 审查UI代码是否符合Web界面规范。Web设计规范审查 |
| A-ask-questions | 29 | ✗ | 动手前需求澄清 — 越详细越好，执行中零确认。需求澄清引擎 |
| dogfood | 30 | ✗ | 系统化探索和测试本地Web应用 — 浏览器QA。应用探索测试 |
| workflow-preflight-check | 31 | ✗ | 多agent工作流预执行验证 — 模拟所有步骤预检。工作流预检 |
| debugging-fixing | 32 | ✗ | 诊断和修复bug/错误 — 系统化调试方法论。Bug诊断修复引擎 |
| taskflow | 32 | ✗ | 编排多步骤分离任务为持久TaskFlow作业。多步骤任务编排引擎 |
| A-memory-start | 33 | ✗ | 全局记忆入口加载 — 目录索引式按需加载全局记忆。全局记忆启动门禁 |

## 无触发标记（何时用缺失，53 条，前 20 按长度升序）

- **screenshot**（23字符）：桌面截图/窗口截屏/区域截取工具。桌面截图工具
- **spike**（23字符）：跑一次性原型验证技术可行性。技术可行性原型验证
- **testing**（23字符）：编写和运行测试验证代码正确性。测试编写运行引擎
- **web-design-guidelines**（27字符）：审查UI代码是否符合Web界面规范。Web设计规范审查
- **A-ask-questions**（29字符）：动手前需求澄清 — 越详细越好，执行中零确认。需求澄清引擎
- **dogfood**（30字符）：系统化探索和测试本地Web应用 — 浏览器QA。应用探索测试
- **workflow-preflight-check**（31字符）：多agent工作流预执行验证 — 模拟所有步骤预检。工作流预检
- **debugging-fixing**（32字符）：诊断和修复bug/错误 — 系统化调试方法论。Bug诊断修复引擎
- **taskflow**（32字符）：编排多步骤分离任务为持久TaskFlow作业。多步骤任务编排引擎
- **A-memory-start**（33字符）：全局记忆入口加载 — 目录索引式按需加载全局记忆。全局记忆启动门禁
- **prompt-system-audit**（34字符）：多agent提示词系统逻辑一致性审计 + 数据层验证。提示词系统审计
- **discover-agent-cli**（35字符）：发现Electron桌面应用中隐藏的CLI工具。发现桌面应用隐藏CLI
- **agent-browser**（36字符）：浏览器自动化CLI — AI agent时代浏览器操控。浏览器自动化工具
- **A-prompt-better**（39字符）：Prompt优化器 — 自动按业界最佳实践优化用户提示词。Prompt自动优化
- **diagram-maker**（39字符）：创建SVG/HTML/Excalidraw架构图/流程图/概念图。图表生成工具
- **windows-gitbash-chinese-path-pit**（39字符）：Git Bash调用Node系CLI的中文路径坑修复。Git Bash中文路径
- **utf8-encoding-fix**（40字符）：修复中文Windows下Write工具写入UTF-8乱码问题。UTF-8编码修复
- **wechat-automation**（41字符）：微信自动化 — 消息监听/提取/Agent开发。微信监听+消息提取+Agent开发
- **openclaw-task-supervision**（43字符）：控制OpenClaw执行任务 — 含监督+重试+结果验证。OpenClaw任务监督执行
- **wechat-voice-transcription**（44字符）：微信语音(.silk)转文字：pilk解码+ffmpeg补WAV头+whisper转写。

## 已知盲区

- 词表启发式：无触发标记 ≠ 无「何时用」语义（可能换了措辞）；命中标记亦可能是噪声。双要素达标数是**下界**，语义级复核（LLM 抽判）为后续门禁增补项。
- 「做什么」仅以长度 ≥15 近似，未做动词语义判定。

## 与路由命中率联动（待办）

- 门禁落地（焚诀 verify 新判据）待焚诀归属会话执行（本项目红线：焚诀 eval/ 只读）；
- 整改后复跑 `unified_router.py` 盲测对照，验证命中率改善（验收判据③）。
