# P1-1 description 双要素基线报告

> 生成：2026-09-24 17:46 ｜ 扫描根：`D:\global_skills` ｜ 工具：`05-exec/description_baseline_scan.py`（只读）
> 口径：anthropics/skills 官方 —— description = 触发第一信号，需「做什么 + 何时用」双要素；机器判定为启发式（触发标记词表 + 长度 ≥15），语义盲区见「已知盲区」。

## 总览

| 指标 | 值 |
|---|---|
| SKILL.md 总数 | 166 |
| frontmatter 解析错误 | 0 |
| 无/空 description | 0 |
| 含触发标记（何时用） | 120 |
| 双要素达标 | 120 |
| 长度 min/median/max | 23 / 237 / 1019 |
| 超官方上限 1024 字符 | 0 |
| 流程入描述（anti-pattern） | 24 |

## 口径对账（r19 P1-C 分母统一登记）

- 口径对账: 本次纳入 166 | 磁盘 glob 167（junction 跳过 1: rag-eval | 解析错误 0）
- 焚诀注册表口径: count=167 / skills=167（fenjue-disk-manifest-v1, manifest 自洽, generated=2026-09-24T13:50:46）→ 与磁盘 glob 一致
- 取值命令: python "C:\Users\37533\Desktop\workspace\焚诀\eval\verify_truth_consistency.py"  # 取 C1 行

## 最短 Top10（优先整改候选）

| skill | 长度 | 触发标记 | description 摘录 |
|---|---|---|---|
| screenshot | 23 | ✗ | 桌面截图/窗口截屏/区域截取工具。桌面截图工具 |
| spike | 23 | ✗ | 跑一次性原型验证技术可行性。技术可行性原型验证 |
| testing | 23 | ✗ | 编写和运行测试验证代码正确性。测试编写运行引擎 |
| web-design-guidelines | 27 | ✗ | 审查UI代码是否符合Web界面规范。Web设计规范审查 |
| A-ask-questions | 29 | ✗ | 动手前需求澄清 — 越详细越好，执行中零确认。需求澄清引擎 |
| debugging-fixing | 32 | ✗ | 诊断和修复bug/错误 — 系统化调试方法论。Bug诊断修复引擎 |
| agent-browser | 36 | ✗ | 浏览器自动化CLI — AI agent时代浏览器操控。浏览器自动化工具 |
| diagram-maker | 39 | ✗ | 创建SVG/HTML/Excalidraw架构图/流程图/概念图。图表生成工具 |
| windows-gitbash-chinese-path-pit | 39 | ✗ | Git Bash调用Node系CLI的中文路径坑修复。Git Bash中文路径 |
| utf8-encoding-fix | 40 | ✗ | 修复中文Windows下Write工具写入UTF-8乱码问题。UTF-8编码修复 |

## 无触发标记（何时用缺失，46 条，前 20 按长度升序）

- **screenshot**（23字符）：桌面截图/窗口截屏/区域截取工具。桌面截图工具
- **spike**（23字符）：跑一次性原型验证技术可行性。技术可行性原型验证
- **testing**（23字符）：编写和运行测试验证代码正确性。测试编写运行引擎
- **web-design-guidelines**（27字符）：审查UI代码是否符合Web界面规范。Web设计规范审查
- **A-ask-questions**（29字符）：动手前需求澄清 — 越详细越好，执行中零确认。需求澄清引擎
- **debugging-fixing**（32字符）：诊断和修复bug/错误 — 系统化调试方法论。Bug诊断修复引擎
- **agent-browser**（36字符）：浏览器自动化CLI — AI agent时代浏览器操控。浏览器自动化工具
- **diagram-maker**（39字符）：创建SVG/HTML/Excalidraw架构图/流程图/概念图。图表生成工具
- **windows-gitbash-chinese-path-pit**（39字符）：Git Bash调用Node系CLI的中文路径坑修复。Git Bash中文路径
- **utf8-encoding-fix**（40字符）：修复中文Windows下Write工具写入UTF-8乱码问题。UTF-8编码修复
- **wechat-automation**（41字符）：微信自动化 — 消息监听/提取/Agent开发。微信监听+消息提取+Agent开发
- **openclaw-task-supervision**（43字符）：控制OpenClaw执行任务 — 含监督+重试+结果验证。OpenClaw任务监督执行
- **wechat-voice-transcription**（44字符）：微信语音(.silk)转文字：pilk解码+ffmpeg补WAV头+whisper转写。
- **taskflow-inbox-triage**（45字符）：TaskFlow收件箱分类示例 — 参考/教学用途，非生产。TaskFlow收件箱参考示例
- **windows-cli-utf8-wrapper**（46字符）：Python subprocess调用CLI工具的UTF-8安全包装。CLI UTF-8包装
- **shell-encoding-pitfalls**（47字符）：中文乱码/编码坑修复 — curl/Bash/sed CRLF/UTF-8。Shell编码修复
- **audit-runner-safe-aggregate**（48字符）：写聚合runner的安全判定范式 — 防全局any()掩盖单脚本失败。聚合runner反掩盖范式
- **oc-dispatch-exec-guard**（48字符）：OpenClaw CLI派发任务执行护栏 — 防止agent秒停0产出。openclaw派发护栏
- **python-debugpy**（48字符）：Python调试 — pdb/breakpoint/debugpy远程调试。Python调试工具
- **node-inspect-debugger**（52字符）：Node.js调试 — inspect/--inspect/CDP/heap分析。Node.js调试工具

## 流程入描述命中（24 条，anti-pattern 候选）

> 判据来源：addyosmani/agent-skills `docs/skill-anatomy.md`——「不要概述工作流；description 里出现流程步骤，agent 可能照摘要执行而不读正文」。

- **9b-lightworkflow**：hermes 中 qwen3.5:9b-agent 干杂活的轻量工作流（agent 能力增强包 + 项目轻记忆）。当用户在项目文件夹下用 hermes 拉起 9b 小模型干杂活（改
- **A-get-memory**：任务后经验反哺引擎。四维度反思+经验分类路由+已有Skill升级检查+漏用Skill审计(根因定位→自解→修复→验证闭环)+用户画像增量更新+项目经验总结(冷启动续接摘要)+技能自
- **A-java-problem**：Java 课程作业与练习总入口（龙虾自建，2026-09-07）。触发词：Java作业、Java练习、写个Java程序、javac、java编译运行报错、语法基础、面向对象/OOP
- **A-memory-start**：全局记忆入口加载 — 目录索引式按需加载全局记忆。全局记忆启动门禁 Directory-indexed on-demand global memory loader + 执行契约门
- **ai-video-homework-pipeline**：AI 视频作业流水线——图生视频 → TTS 配音 → 无版权算法配乐 → ASS 字幕 → ffmpeg 交叉溶解合成 → 像素级 QA。当用户要求"用 AI 生成视频并剪辑/加
- **algorithmic-art**：Creating algorithmic art using p5.js with seeded randomness and interactive parameter expl
- **audio-deliverable-pipeline**：音频交付流水线（语音旁白 / 主题音乐 / 可选 MP4）— 固化「local-tts 不可用 → edge-tts 降级 + lameenc 编码 + mutagen/波形双核验
- **bigfile-split**：拆分超大记忆/知识库markdown文件 — 按标题切块+原文件留索引。超大markdown拆分工具 Split oversized memory/knowledge-base f
- **byted-mediakit-shared**：1. mediakit-cli: 视频编辑 / 音频处理 / 加背景音乐 / 视频特效 / 动画效果 — supports audio/video processing, edit
- **chaoshi-web-deploy**：超市web部署唯一权威源（v3 新架构：Cloudflare Pages Functions + D1 + GitHub Pages 双前端）。任何 wrangler pages 
- **consulting-analysis**：研究报告/咨询分析:市场分析、消费者洞察、品牌与财务分析报告。Use this skill when the user requests to generate, create, 
- **cross-platform-agent-sync**：跨平台AI agent行为规则同步方法论。通过junction + 共享文件 + 平台启动文件引用实现"改一处N端响应"。覆盖在役端 WB/TR/CX/HM（OC 已退役 2026
- **discover-agent-cli**：发现Electron桌面应用中隐藏的CLI工具。发现桌面应用隐藏CLI 发现 Electron 桌面应用中隐藏的 CLI 工具。当需要调用某个桌面应用（如 WorkBuddy/TR
- **executing-plans**：（已弃用 / DEPRECATED）计划执行——本仓不再使用独立执行技能，执行控制统一由七步闭环第⑥步 + workflow_gate + flow 状态机承担。触发词：执行计划、
- **hyperframes-media**：Asset preprocessing for HyperFrames compositions — text-to-speech narration (Kokoro), audi
- **ican-frontend-design-system**：iCAN 门店 AI 管理智能体（Flask + Jinja + 单 CSS 原生前端）的 V4 设计体系与交付链。含「雾山青」令牌表（色彩/间距/字阶/圆角/高程/动效/图表分类
- **local-ocr-npu**：Local NPU OCR (本地NPU文字识别). Use this skill when the user wants to extract, recognize, or re
- **local-realtime-translator**：Intel Local Windows Realtime Speech Translator (本地实时语音翻译 / 同声传译). Use when the user wants 
- **sqlalchemy-loader-criteria-pitfalls**：SQLAlchemy 全局租户守卫（with_loader_criteria + do_orm_execute 行级过滤）的三个缓存/边界坑与排查法：闭包键丢失致跨租户绑定冻结、N
- **story-long-analyze**：长篇网文拆文。深度拆解爆款长篇小说的黄金三章、人设架构、爽点设计、节奏控制。单一深度拆解管道：跑完黄金三章（Stage 1）后产出快速预览报告并询问是否继续全量拆解，确认后从 St
- **ui-ux-pro-max**：UI/UX design intelligence and implementation guidance for building polished interfaces. Us
- **windows-bash-cli-interop-pitfalls**：Windows bash (Git Bash/MSYS2) 调用外部 CLI 或现代构建工具时的语法兼容坑合集。覆盖：bash extglob 吞 PowerShell $_ 变量
- **workflow-preflight-check**：多agent工作流预执行验证 — 模拟所有步骤预检。工作流预检 多agent工作流预执行验证（preflight check）。在实际执行pipeline前，逐项检查执行链完整性：
- **xlsx**：Excel表格(.xlsx/.xlsm/.csv)读写/编辑/修复。Use this skill any time a spreadsheet file is the primar

## 已知盲区

- 词表启发式：无触发标记 ≠ 无「何时用」语义（可能换了措辞）；命中标记亦可能是噪声。双要素达标数是**下界**，语义级复核（LLM 抽判）为后续门禁增补项。
- 「做什么」仅以长度 ≥15 近似，未做动词语义判定。
- 「流程入描述」为形态判定（编号/箭头链/冒号后步骤），命中≠违例，亦存在漏判（用自然语言概述步骤而不带编号/箭头）；须逐条人工裁定。

## 与路由命中率联动（待办）

- 门禁落地（焚诀 verify 新判据）待焚诀归属会话执行（本项目红线：焚诀 eval/ 只读）；
- 整改后复跑 `unified_router.py` 盲测对照，验证命中率改善（验收判据③）。
