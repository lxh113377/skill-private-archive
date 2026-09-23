# 自建 skill 清单（三源交叉裁定 · v2）

> 生成：scan_all.py --stage scope（2026-09-22 重出；基数 = 注册表 151 条 = 磁盘实测，焚诀 verify C1 全等）
> 源：unified-skills-index.json + 在役端 platform-*.json（user_created_skills 并集）+ disk_manifest.json + 磁盘枚举 + git 首提交
> ⚠️ 本版**取代 v1**（2026-09-14，169 条时代）。v1 已原样归档至 `archive/scope-v1-169-2026-09-14/`（历史留痕不改写）。
> 覆盖：磁盘 150 个目录；已排除 `SKIP_DIRS`（`_my-skills` = 保护标记非任务型 skill、`hooks` 基建、`_trash`/`_temp`/`_bak`/`.git`/`.hermes`/`__pycache__`）→ 与注册表 151 条差 1（即 `_my-skills`）。
> 打分：registry user_created=true +5 | 命名域自建族 +3 | semver +2 | git 版本化提交 +2 | disk global_skills +1 | user_created=false -4 | LICENSE -3 | source=skillhub -3 | 官方元数据 -3 | openclaw_plugin -6
> ⚠️ 校正注（2026-09-23 r8）：上行打分说明与 `scan_all.py` 实现不符（历史版本文案未随代码更新）——实际 = disk **+2** / `unified:user_created=true` **+4** / `user_created=false` **不计分**（失真字段）/ 无 LICENSE-3 等负分项，市场信号命中即 **EXCLUDE(-100)**（见 `01-scan/scan_all.py:208-219`）；下次 `--apply` 重出时以代码生成文案为准
> 磁盘目录 150 → HIGH 51 / MID 26 / LOW 30 / EXCLUDE 43

## HIGH（51）

| skill | 分数 | 注册表uc | disk源 | 版本 | 关键证据 |
|---|---|---|---|---|---|
| `9b-lightworkflow` | 10 | True | global_skills | community | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=community; 命名域:9b-*; gitAdd=2026-09-21|chore(baseline): 建立 git 基线（A-projec... |
| `A-ask-questions` | 10 | True | global_skills | community | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=community; 命名域:A-*; gitAdd=2026-09-21|chore(baseline): 建立 git 基线（A-project... |
| `A-get-memory` | 12 | True | global_skills | 3.3.0 | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=3.3.0(semver); 命名域:A-*; gitAdd=2026-09-21|chore(baseline): 建立 git 基线（A-pro... |
| `A-java-problem` | 7 | False | global_skills | 1.2.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.2.0(semver); 命名域:A-*; gitAdd=2026-09-21|chore(baseline): 建立 gi... |
| `A-memory-start` | 12 | True | global_skills | 7.0.0 | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=7.0.0(semver); 命名域:A-*; gitAdd=2026-09-21|chore(baseline): 建立 git 基线（A-pro... |
| `A-project-better` | 7 | False | global_skills | 1.1.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.1.0(semver); 命名域:A-*; gitAdd=2026-09-21|chore(baseline): 建立 gi... |
| `A-project-handoff` | 12 | True | global_skills | 3.0.0 | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=3.0.0(semver); 命名域:A-*; gitAdd=2026-09-21|chore(baseline): 建立 git 基线（A-pro... |
| `A-prompt-better` | 10 | True | global_skills | community | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=community; 命名域:A-*; gitAdd=2026-09-21|chore(baseline): 建立 git 基线（A-project... |
| `A-skill-manager` | 11 | True | global_skills | 1.0.1 | disk:global_skills(本地原生); unified:user_created=true; source=user-created; version=1.0.1(semver); 命名域:A-*; gitAdd=2026-09-21|chore(baseline): 建立 git 基线（A-proj... |
| `audit-runner-safe-aggregate` | 12 | True | global_skills | 1.0.0 | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=1.0.0(semver); 命名域:audit-runner*; gitAdd=2026-09-21|chore(baseline): 建立 gi... |
| `bigfile-split` | 12 | True | global_skills | 1.2.1 | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=1.2.1(semver); 命名域:bigfile-split*; gitAdd=2026-09-21|chore(baseline): 建立 g... |
| `c-cleanup` | 12 | True | global_skills | 2.0.0 | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=2.0.0(semver); 命名域:c-cleanup*; gitAdd=2026-09-21|chore(baseline): 建立 git 基... |
| `chaoshi-admin-inline-edit` | 10 | True | global_skills | community | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=community; 命名域:chaoshi-*; gitAdd=2026-09-21|chore(baseline): 建立 git 基线（A-p... |
| `chaoshi-image-optimization` | 10 | True | global_skills | community | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=community; 命名域:chaoshi-*; gitAdd=2026-09-21|chore(baseline): 建立 git 基线（A-p... |
| `chaoshi-web-deploy` | 10 | True | global_skills | community | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=community; 命名域:chaoshi-*; gitAdd=2026-09-21|chore(baseline): 建立 git 基线（A-p... |
| `code-review` | 12 | True | global_skills | 1.0.0 | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=1.0.0(semver); 命名域:code-review*; gitAdd=2026-09-21|chore(baseline): 建立 git... |
| `cross-platform-agent-sync` | 7 | False | global_skills | 1.1.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.1.0(semver); 命名域:cross-platform-*; gitAdd=2026-09-21|chore(bas... |
| `dogfood` | 7 | False | global_skills | 1.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.0(semver); 命名域:dogfood*; gitAdd=2026-09-21|chore(baseline): 建立... |
| `fenjue-lessons-hitrate` | 10 | True | global_skills | community | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=community; 命名域:fenjue-*; gitAdd=2026-09-21|chore(baseline): 建立 git 基线（A-pr... |
| `fenjue-memory-audit` | 10 | True | global_skills | community | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=community; 命名域:fenjue-*; gitAdd=2026-09-21|chore(baseline): 建立 git 基线（A-pr... |
| `hermes-installer` | 10 | True | global_skills | community | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=community; 命名域:hermes-installer*; gitAdd=2026-09-21|chore(baseline): 建立 gi... |
| `ican-deploy` | 7 | False | global_skills | 1.0.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.0.0(semver); 命名域:ican-*; gitAdd=2026-09-21|chore(baseline): 建立... |
| `ican-frontend-design-system` | 7 | False | global_skills | 4.0.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=4.0.0(semver); 命名域:ican-*; gitAdd=2026-09-21|chore(baseline): 建立... |
| `oc-dispatch-exec-guard` | 12 | True | global_skills | 1.0 | disk:global_skills(本地原生); registry:user_created=true; source=user; version=1.0(semver); 命名域:oc-dispatch*; gitAdd=2026-09-21|chore(baseline): 建立 git 基线（A-proj... |
| `openclaw-dual-gate-quality-audit` | 12 | True | global_skills | 1.3.0 | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=1.3.0(semver); 命名域:openclaw-*; gitAdd=2026-09-21|chore(baseline): 建立 git 基... |
| `openclaw-fenjue-weekly` | 12 | True | global_skills | 2.0.0 | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=2.0.0(semver); 命名域:openclaw-*; gitAdd=2026-09-21|chore(baseline): 建立 git 基... |
| `openclaw-task-supervision` | 12 | True | global_skills | 1.3.0 | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=1.3.0(semver); 命名域:openclaw-*; gitAdd=2026-09-21|chore(baseline): 建立 git 基... |
| `prompt-consolidation` | 7 | False | global_skills | 2.1.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=2.1.0(semver); 命名域:prompt-*; gitAdd=2026-09-21|chore(baseline): ... |
| `prompt-system-audit` | 7 | False | global_skills | 1.3.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.3.0(semver); 命名域:prompt-*; gitAdd=2026-09-21|chore(baseline): ... |
| `static-site-batch-audit-fix` | 10 | True | global_skills | community | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=community; 命名域:static-site*; gitAdd=2026-09-21|chore(baseline): 建立 git 基线（... |
| `story-cover` | 7 | False | global_skills | 1.0.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.0.0(semver); 命名域:story-*; gitAdd=2026-09-21|chore(baseline): 建... |
| `story-deslop` | 7 | False | global_skills | 1.0.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.0.0(semver); 命名域:story-*; gitAdd=2026-09-21|chore(baseline): 建... |
| `story-import` | 7 | False | global_skills | 1.0.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.0.0(semver); 命名域:story-*; gitAdd=2026-09-21|chore(baseline): 建... |
| `story-long-analyze` | 7 | False | global_skills | 1.0.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.0.0(semver); 命名域:story-*; gitAdd=2026-09-21|chore(baseline): 建... |
| `story-long-write` | 7 | False | global_skills | 1.0.1 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.0.1(semver); 命名域:story-*; gitAdd=2026-09-21|chore(baseline): 建... |
| `story-review` | 7 | False | global_skills | 1.1.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.1.0(semver); 命名域:story-*; gitAdd=2026-09-21|chore(baseline): 建... |
| `story-scan` | 7 | False | global_skills | 1.0.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.0.0(semver); 命名域:story-*; gitAdd=2026-09-21|chore(baseline): 建... |
| `story-setup` | 7 | False | global_skills | 1.2.8 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.2.8(semver); 命名域:story-*; gitAdd=2026-09-21|chore(baseline): 建... |
| `story-short-analyze` | 7 | False | global_skills | 3.0.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=3.0.0(semver); 命名域:story-*; gitAdd=2026-09-21|chore(baseline): 建... |
| `story-short-write` | 7 | False | global_skills | 1.0.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.0.0(semver); 命名域:story-*; gitAdd=2026-09-21|chore(baseline): 建... |
| `vp-perspective-audit` | 7 | False | global_skills | 1.1.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.1.0(semver); 命名域:vp-perspective*; gitAdd=2026-09-21|chore(base... |
| `wb-git-commit-recipe` | 7 | False | global_skills | 1.1.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.1.0(semver); 命名域:wb-git-*; gitAdd=2026-09-21|chore(baseline): ... |
| `wechat-automation` | 7 | False | global_skills | 1.0.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.0.0(semver); 命名域:wechat-*; gitAdd=2026-09-21|chore(baseline): ... |
| `wechat-voice-transcription` | 10 | True | global_skills | community | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=community; 命名域:wechat-*; gitAdd=2026-09-21|chore(baseline): 建立 git 基线（A-pr... |
| `windows-bash-cli-interop-pitfalls` | 10 | True | global_skills | community | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=community; 命名域:windows-*; gitAdd=2026-09-21|chore(baseline): 建立 git 基线（A-p... |
| `windows-cli-utf8-wrapper` | 7 | False | global_skills | 1.0.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.0.0(semver); 命名域:windows-*; gitAdd=2026-09-21|chore(baseline):... |
| `windows-gitbash-chinese-path-pit` | 11 | True | global_skills | 1.0.0 | disk:global_skills(本地原生); unified:user_created=true; source=user-created; version=1.0.0(semver); 命名域:windows-*; gitAdd=2026-09-21|chore(baseline): 建立 git 基线（... |
| `windows-native-ocr` | 10 | True | global_skills | community | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=community; 命名域:windows-*; gitAdd=2026-09-21|chore(baseline): 建立 git 基线（A-p... |
| `workbuddy-mcp` | 7 | False | global_skills | 1.1.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.1.0(semver); 命名域:workbuddy-*; gitAdd=2026-09-21|chore(baseline... |
| `workflow-preflight-check` | 7 | False | global_skills | 1.0.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.0.0(semver); 命名域:workflow-*; gitAdd=2026-09-21|chore(baseline)... |
| `wps-knowledgebase` | 7 | False | global_skills | 2.0.3 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=2.0.3(semver); 命名域:wps-*; gitAdd=2026-09-21|chore(baseline): 建立 ... |

## MID（26）

| skill | 分数 | 注册表uc | disk源 | 版本 | 关键证据 |
|---|---|---|---|---|---|
| `agent-browser` | 4 | False | global_skills | 1.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.0(semver); gitAdd=2026-09-21|chore(baseline): 建立 git 基线（A-proj... |
| `audio-deliverable-pipeline` | 4 | False | global_skills | 1.0.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.0.0(semver); gitAdd=2026-09-21|chore(baseline): 建立 git 基线（A-pr... |
| `cloudbase-db-optimize` | 4 | False | global_skills | 1.0.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.0.0(semver); gitAdd=2026-09-21|chore(baseline): 建立 git 基线（A-pr... |
| `debugging-fixing` | 5 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; 命名域:debugging-fixing*; gitAdd=2026-09-21|chore(baseli... |
| `discover-agent-cli` | 4 | False | global_skills | 1.0.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.0.0(semver); gitAdd=2026-09-21|chore(baseline): 建立 git 基线（A-pr... |
| `hook-analyzer-skill` | 5 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; 命名域:hook-analyzer*; gitAdd=2026-09-21|chore(baseline)... |
| `html-to-docx-win-fix` | 4 | False | global_skills | 1.0.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.0.0(semver); gitAdd=2026-09-21|chore(baseline): 建立 git 基线（A-pr... |
| `local-asr` | 5 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; 命名域:local-*; gitAdd=无 |
| `local-computer-use` | 5 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; 命名域:local-*; gitAdd=无 |
| `local-img2img` | 5 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; 命名域:local-*; gitAdd=无 |
| `local-mineru` | 5 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; 命名域:local-*; gitAdd=无 |
| `local-ocr-npu` | 5 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; 命名域:local-*; gitAdd=无 |
| `local-realtime-translator` | 5 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; 命名域:local-*; gitAdd=无 |
| `local-screenshot-qa` | 5 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; 命名域:local-*; gitAdd=无 |
| `local-tts` | 5 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; 命名域:local-*; gitAdd=无 |
| `local-txt2img` | 5 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; 命名域:local-*; gitAdd=无 |
| `local-vram` | 5 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; 命名域:local-*; gitAdd=无 |
| `office-automation-pro` | 4 | False | global_skills | 1.0.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.0.0(semver); gitAdd=2026-09-21|chore(baseline): 建立 git 基线（A-pr... |
| `report-generator-skill` | 5 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; 命名域:report-generator*; gitAdd=2026-09-21|chore(baseli... |
| `shell-encoding-pitfalls` | 5 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; 命名域:shell-encoding*; gitAdd=2026-09-21|chore(baseline... |
| `testing` | 4 | False | global_skills | 1.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); version=1.0(semver); gitAdd=2026-09-21|chore(baseline): 建立 git 基线（A-project-handoff #20 自动... |
| `utf8-encoding-fix` | 5 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; 命名域:utf8-*; gitAdd=2026-09-21|chore(baseline): 建立 git... |
| `video-breakdown-skill` | 4 | False | global_skills | 1.0.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.0.0(semver); gitAdd=2026-09-21|chore(baseline): 建立 git 基线（A-pr... |
| `video-whisper-transcribe` | 4 | False | global_skills | 1.1.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.1.0(semver); gitAdd=2026-09-21|chore(baseline): 建立 git 基线（A-pr... |
| `win-toolchain-pitfalls` | 4 | False | global_skills | 1.0.1 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.0.1(semver); gitAdd=2026-09-21|chore(baseline): 建立 git 基线（A-pr... |
| `天眼一下` | 5 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; 命名域:天眼一下*; gitAdd=无 |

## LOW（30）

| skill | 分数 | 注册表uc | disk源 | 版本 | 关键证据 |
|---|---|---|---|---|---|
| `ai-video-homework-pipeline` | 2 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; gitAdd=2026-09-21|chore(baseline): 建立 git 基线（A-projec... |
| `brainstorming` | 2 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; gitAdd=无 |
| `browser-cdp` | 2 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; gitAdd=2026-09-21|chore(baseline): 建立 git 基线（A-projec... |
| `chart-visualization` | 2 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; gitAdd=无 |
| `coding-agent` | 2 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; gitAdd=2026-09-21|chore(baseline): 建立 git 基线（A-projec... |
| `consulting-analysis` | 2 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; gitAdd=2026-09-21|chore(baseline): 建立 git 基线（A-projec... |
| `data-analysis` | 2 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; gitAdd=2026-09-21|chore(baseline): 建立 git 基线（A-projec... |
| `data-visualization` | 2 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; gitAdd=2026-09-21|chore(baseline): 建立 git 基线（A-projec... |
| `defuddle` | 2 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; gitAdd=无 |
| `diagram-maker` | 2 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; gitAdd=2026-09-21|chore(baseline): 建立 git 基线（A-projec... |
| `doc-coauthoring` | 2 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; gitAdd=2026-09-21|chore(baseline): 建立 git 基线（A-projec... |
| `executing-plans` | 2 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; gitAdd=无 |
| `gsap` | 2 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; gitAdd=2026-09-21|chore(baseline): 建立 git 基线（A-projec... |
| `hyperframes` | 2 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; gitAdd=2026-09-21|chore(baseline): 建立 git 基线（A-projec... |
| `hyperframes-cli` | 2 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; gitAdd=2026-09-21|chore(baseline): 建立 git 基线（A-projec... |
| `hyperframes-media` | 2 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; gitAdd=2026-09-21|chore(baseline): 建立 git 基线（A-projec... |
| `hyperframes-registry` | 2 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; gitAdd=2026-09-21|chore(baseline): 建立 git 基线（A-projec... |
| `json-canvas` | 2 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; gitAdd=无 |
| `node-inspect-debugger` | 2 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; gitAdd=2026-09-21|chore(baseline): 建立 git 基线（A-projec... |
| `obsidian-bases` | 2 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; gitAdd=无 |
| `obsidian-cli` | 2 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; gitAdd=无 |
| `obsidian-markdown` | 2 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; gitAdd=无 |
| `pixelle-api-ensure` | 2 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; gitAdd=2026-09-21|chore(baseline): 建立 git 基线（A-projec... |
| `python-debugpy` | 2 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; gitAdd=2026-09-21|chore(baseline): 建立 git 基线（A-projec... |
| `refactoring` | 2 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; gitAdd=2026-09-21|chore(baseline): 建立 git 基线（A-projec... |
| `spike` | 2 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; gitAdd=2026-09-21|chore(baseline): 建立 git 基线（A-projec... |
| `story` | 2 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; gitAdd=2026-09-21|chore(baseline): 建立 git 基线（A-projec... |
| `test-driven-development` | 2 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; gitAdd=无 |
| `web-design-guidelines` | 2 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; gitAdd=2026-09-21|chore(baseline): 建立 git 基线（A-projec... |
| `writing-plans` | 2 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; gitAdd=无 |

## EXCLUDE（43）

| skill | 分数 | 注册表uc | disk源 | 版本 | 关键证据 |
|---|---|---|---|---|---|
| `algorithmic-art` | -100 | False | global_skills | 1.0 | LICENSE:LICENSE.txt(官方/市场包) |
| `brand-guidelines` | -100 | False | global_skills | community | LICENSE:LICENSE.txt(官方/市场包) |
| `byted-bp-cdn-pagesdeploy` | -100 | False | global_skills | community | source=skillhub(市场) |
| `byted-mediakit-shared` | -100 | False | global_skills | 1.0.0 | LICENSE:LICENSE(官方/市场包) |
| `byted-seedance-video-generate` | -100 | False | global_skills | community | LICENSE:LICENSE.txt(官方/市场包) |
| `byted-seedream-image-generate` | -100 | False | global_skills | community | LICENSE:LICENSE(官方/市场包) |
| `canvas-design` | -100 | False | global_skills | community | LICENSE:LICENSE.txt(官方/市场包) |
| `cloudbase__skillhub` | -100 | False | global_skills | community | source=skillhub(市场) |
| `computer-use-guidance-windows` | -100 | False | global_skills | 0.9.0 | .skill-metadata.yaml(官方元数据) |
| `docx` | -100 | False | global_skills | 2.0.0 | .skill-metadata.yaml(官方元数据) |
| `electron` | -100 | False | global_skills | 1.0 | 精读人工判定:市场/上游件 |
| `elon-musk-perspective` | -100 | False | global_skills | community | LICENSE:LICENSE(官方/市场包) |
| `figma` | -100 | False | global_skills | community | LICENSE:LICENSE.txt(官方/市场包) |
| `find-skills` | -100 | False | global_skills | 1.0.4 | .skill-metadata.yaml(官方元数据) |
| `first-principles-decomposer` | -100 | False | global_skills | community | _meta.json:发布元数据(市场件) |
| `frontend-design` | -100 | False | global_skills | community | LICENSE:LICENSE.txt(官方/市场包) |
| `frontend-skill` | -100 | False | global_skills | 1.0 | LICENSE:LICENSE.txt(官方/市场包) |
| `frontend-slides` | -100 | False | global_skills | community | LICENSE:LICENSE(官方/市场包) |
| `github` | -100 | False | global_skills | community | _meta.json:发布元数据(市场件) |
| `gstack` | -100 | False | global_skills | 1.1.0 | LICENSE:LICENSE(官方/市场包) |
| `html-ppt` | -100 | False | global_skills | community | LICENSE:LICENSE(官方/市场包) |
| `internal-comms` | -100 | False | global_skills | community | LICENSE:LICENSE.txt(官方/市场包) |
| `knowledge-capture` | -100 | False | global_skills | community | evaluations/(官方评测件) |
| `mcporter` | -1 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; homepage=http://mcporter.dev(外部来源); version=community; gitAdd=2026-09-21... |
| `meeting-intelligence` | -100 | False | global_skills | community | evaluations/(官方评测件) |
| `nano-pdf` | -1 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; homepage=https://pypi.org/project/nano-pdf/(外部来源); version=community; gi... |
| `notion-cli` | -100 | False | global_skills | community | LICENSE:LICENSE.md(官方/市场包) |
| `openai-whisper-api` | -1 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; homepage=https://platform.openai.com/docs/guides/speech-to-text(外部来源); v... |
| `oracle` | -1 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; homepage=https://askoracle.dev(外部来源); version=community; gitAdd=2026-09-... |
| `pdf` | -100 | False | global_skills | 1.0.1 | .skill-metadata.yaml(官方元数据) |
| `pptx` | -100 | False | global_skills | community | LICENSE:LICENSE.txt(官方/市场包) |
| `research-documentation` | -100 | False | global_skills | community | evaluations/(官方评测件) |
| `screenshot` | -100 | False | global_skills | 1.0 | LICENSE:LICENSE.txt(官方/市场包) |
| `shadcn` | -100 | False | global_skills | 1.0 | evals/evals.json(官方评测件) |
| `slides` | -100 | False | global_skills | community | LICENSE:LICENSE.txt(官方/市场包) |
| `spec-to-implementation` | -100 | False | global_skills | community | evaluations/(官方评测件) |
| `sq-cleanmgr-c` | -100 | False | global_skills | 1.2.0 | _meta.json:发布元数据(市场件) |
| `taskflow` | -100 | False | global_skills | community | 精读人工判定:市场/上游件 |
| `taskflow-inbox-triage` | -100 | False | global_skills | community | 精读人工判定:市场/上游件 |
| `theme-factory` | -100 | False | global_skills | community | LICENSE:LICENSE.txt(官方/市场包) |
| `ui-ux-pro-max` | -100 | False | global_skills | community | _meta.json:发布元数据(市场件) |
| `video-frames` | -1 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; homepage=https://ffmpeg.org(外部来源); version=community; gitAdd=2026-09-21|... |
| `xlsx` | -100 | False | global_skills | 1.0.1 | .skill-metadata.yaml(官方元数据) |

