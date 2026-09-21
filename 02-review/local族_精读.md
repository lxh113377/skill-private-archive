# local族精读审计卡（阶段2 第3批）· 本地 AI 能力族 10 个

> 生成：2026-09-14 | code-explorer 只读精读 | 体积/死链均实测
> 注：10 个 SKILL.md frontmatter 均无 `triggers:` 与 `version:`

| skill | 字节 | 超4KB | 门禁 | 职责 | 关键问题 |
|---|---|---|---|---|---|
| local-asr | 3.6KB | N | Y | 音视频离线转写 | [P2] 视频链路依赖 ffmpeg 未声明(requirements.txt 无此项) |
| local-computer-use | 4.81KB | Y | Y | 自然语言改 Windows 设置 | [P1] description:7 已含 GPU/内存 → 与 vram 双命中 |
| local-img2img | 2.64KB | N | Y | 源图+提示词图生图 | [P2] 与 tts/txt2img 的 requirements.txt 字节相同(468B×3) |
| local-mineru | 4.54KB | Y | Y | PDF/图→Markdown | [P1] :69-72 自封"任何 OCR 首选"与 ocr-npu 互斥无仲裁；**全族唯一有 footer 产物声明**(:60-65/:78-83) |
| local-ocr-npu | 2.31KB | N | Y | NPU 上图片 OCR | [P1] 与 mineru、screenshot-qa 三方抢"图片取字"无优先级表 |
| local-realtime-translator | 6.57KB | Y | Y | 麦克风实时同传+字幕 | [P1] 全族最重(50 资产，wheels 4.56MB+nltk 4.7MB)；内置 MeloTTS 与 local-tts 重复 |
| local-screenshot-qa | 4.69KB | Y | Y | 截图/屏幕读图问答 | [P1] 示例 :37「图里的文字」直接侵占 ocr-npu 场景 |
| local-tts | 5.35KB | Y | Y | 文本转语音/音色克隆 | [P2] 全族唯一无 bin/platform.exe |
| local-txt2img | 4.09KB | Y | Y | 纯文生图 | [P1] 与 img2img 描述互不排斥，"生成图片"双命中 |
| local-vram | 2.58KB | N | 脚本有/文档无 | 改 GPU 共享显存 | [P1] **文档与实现漂移**：SKILL.md 无 AIPC 门禁但 run.ps1:50-53 会硬退 |

## 🎯 合并决策：**不整体合并**（与直觉相反）

判据三条全不满足：
1. **共享启动流程**：8/10 确为同一套脚手架（`platform.exe` 376KB×9、`server-dog.py` 19.45KB×8、`install-env.ps1` 16.88KB×8、`get_gpu_mem.py` 11.32KB×8 字节完全一致）—— 但**只能共享代码，不能共享正文**：每个 info.json 各带 venv_name 与 2GB~10GB 模型清单，合并正文省不下任何下载与磁盘。
2. **常被同时加载**：不常。输入模态互斥（音频/麦克风/图片/PDF/系统指令），一次会话通常只用 1 个；合成 1 个总入口 = 每次命中都灌 10 套用法而只用 1/10，把"10 选 1"变成"加载 10 倍"。
3. **description 能覆盖**：不能。公共词（本地/离线/AIPC）已重复 10 次，合并后需塞 8 类模态触发词，且 3 组冲突（OCR 三方、图生成二方、显存 vs 系统设置）在单条 description 内无法自洽排序。

**具体建议（可执行）**
- **必合并 2 组**：`img2img` + `txt2img` → `local-image-gen`（已共用 venv `t2i-tts`、requirements 468B 三份完全相同、同 GenAI 管线、彼此 :75 互补）；`local-vram` → 并入 `local-computer-use`（vram 仅 1 个 2.32KB 注册表脚本，无模型无 venv）。
- **抽共享运行时** `_shared/local-runtime`（platform.exe / install-env.ps1 / server-dog.py / get_gpu_mem.py / model_download.py），可省 ~9 份重复；把 8 份逐字重复的「模型正在下载 → `--continue`」段抽成 `references/common-runtime.md`。
- **加薄路由 `local-router`（≈1KB）**：只做「本地/AIPC 意图 → 子 skill」分诊，并在其中**显式仲裁** OCR 三方与图生成二方优先级。
- **保留独立**：asr、realtime-translator、mineru、ocr-npu、screenshot-qa、tts（模态独立、模型独立、正文均 ≤6.6KB）。

## 共性结论

1. **同源脚手架复制 9 份 + 大资产随包**：platform.exe×9、server-dog.py×8、install-env.ps1×8；wheels（computer-use 4.19MB、translator 4.56MB）、nltk_data ~4.7MB、GenAI 二进制 ~10MB×2、asr tests ~5MB。
2. **闭环三件套集体缺失**：七步 0/10、triggers 0/10、footer 1/10、版本一致 0/10（frontmatter 均无 version）；**门禁 10/10 有**（唯一达标项）。
3. **触发冲突 3 组无仲裁**：OCR 三方（mineru:69-72 / ocr-npu:16-17 / screenshot-qa:37）、图生成二方（txt2img:4 / img2img:4）、显存二方（vram:4 / computer-use:7）。
4. **注册表元数据失真**：6/10 meta.json 的 `description` 退化为字面量 `"|"`；translator meta.json:8-11 `id=0`、`download_url` 空；`license:` 仅 4/10 有，且 10 个目录均无 LICENSE 文件。
