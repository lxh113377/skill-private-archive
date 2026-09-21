# 自建 skill 清单（三源交叉裁定）

> 生成：scan_all.py --stage scope | 源：unified-skills-index.json + platform-oc.json + disk_manifest.json + 磁盘枚举 + git 首提交
> 打分：registry user_created=true +5 | 命名域自建族 +3 | semver +2 | git 版本化提交 +2 | disk global_skills +1 | user_created=false -4 | LICENSE -3 | source=skillhub -3 | 官方元数据 -3 | openclaw_plugin -6
> 磁盘目录 169 → HIGH 67 / MID 23 / LOW 30 / EXCLUDE 49

## HIGH（67）

| skill | 分数 | 注册表uc | disk源 | 版本 | 关键证据 |
|---|---|---|---|---|---|
| `9b-lightworkflow` | 10 | True | global_skills | community | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=community; 命名域:9b-*; gitAdd=2026-08-16|feat: 入库13个真新skill(9b-lightworkflow... |
| `A-ask-questions` | 10 | True | global_skills | community | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=community; 命名域:A-*; gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 2026-07-22 收尾... |
| `A-get-memory` | 12 | True | global_skills | 3.3.0 | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=3.3.0(semver); 命名域:A-*; gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 2026-07-2... |
| `A-java-problem` | 7 | False | global_skills | 1.2.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.2.0(semver); 命名域:A-*; gitAdd=2026-09-08|docs(R219c): 五端→四端 全量收... |
| `A-memory-start` | 12 | True | global_skills | 7.0.0 | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=7.0.0(semver); 命名域:A-*; gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 2026-07-2... |
| `A-project-handoff` | 12 | True | global_skills | 3.0.0 | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=3.0.0(semver); 命名域:A-*; gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 2026-07-2... |
| `A-prompt-better` | 10 | True | global_skills | community | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=community; 命名域:A-*; gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 2026-07-22 收尾... |
| `audit-runner-safe-aggregate` | 12 | True | global_skills | 1.0.0 | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=1.0.0(semver); 命名域:audit-runner*; gitAdd=2026-07-22|chore: 初始化 skill 库仓库 +... |
| `bigfile-split` | 12 | True | global_skills | 1.2.1 | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=1.2.1(semver); 命名域:bigfile-split*; gitAdd=2026-07-22|chore: 初始化 skill 库仓库 ... |
| `c-cleanup` | 12 | True | global_skills | 2.0.0 | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=2.0.0(semver); 命名域:c-cleanup*; gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 20... |
| `chaoshi-admin-inline-edit` | 10 | True | global_skills | community | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=community; 命名域:chaoshi-*; gitAdd=2026-08-03|chore: 补录 28 个未跟踪技能目录 + 恢复 .gi... |
| `chaoshi-image-optimization` | 10 | True | global_skills | community | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=community; 命名域:chaoshi-*; gitAdd=2026-08-03|chore: 补录 28 个未跟踪技能目录 + 恢复 .gi... |
| `chaoshi-web-deploy` | 10 | True | global_skills | community | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=community; 命名域:chaoshi-*; gitAdd=2026-07-26|chaoshi-web-deploy v1.4.0: 补充 ... |
| `cloudbase-webapp-deploy-debug` | 10 | True | global_skills | community | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=community; 命名域:cloudbase-webapp*; gitAdd=2026-08-03|chore: 补录 28 个未跟踪技能目录 ... |
| `code-review` | 14 | True | global_skills | 1.0.0 | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=1.0.0(semver); 命名域:code-review*; gitAdd=2026-09-09|feat(skill): code-revie... |
| `cross-platform-agent-sync` | 7 | False | global_skills | 1.1.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.1.0(semver); 命名域:cross-platform-*; gitAdd=2026-07-22|chore: 初始... |
| `cross-platform-skill-sync` | 12 | True | global_skills | 1.0 | disk:global_skills(本地原生); registry:user_created=true; source=community; version=1.0(semver); 命名域:cross-platform-*; gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 2... |
| `data-layer-consistency-fix` | 7 | False | global_skills | 1.0.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.0.0(semver); 命名域:data-layer-*; gitAdd=2026-07-22|chore: 初始化 sk... |
| `dogfood` | 7 | False | global_skills | 1.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.0(semver); 命名域:dogfood*; gitAdd=2026-07-22|chore: 初始化 skill 库仓... |
| `embedding-index-alignment` | 10 | True | global_skills | community | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=community; 命名域:embedding-index*; gitAdd=2026-08-03|chore: 补录 28 个未跟踪技能目录 +... |
| `fenjue-advisor-scoring` | 12 | True | global_skills | 2.2.1 | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=2.2.1(semver); 命名域:fenjue-*; gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 2026... |
| `fenjue-cc-audit-cycle` | 7 | False | global_skills | 2.0.1 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=2.0.1(semver); 命名域:fenjue-*; gitAdd=2026-07-22|chore: 初始化 skill ... |
| `fenjue-lessons-hitrate` | 10 | True | global_skills | community | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=community; 命名域:fenjue-*; gitAdd=2026-08-03|chore: 补录 28 个未跟踪技能目录 + 恢复 .git... |
| `fenjue-memory-audit` | 10 | True | global_skills | community | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=community; 命名域:fenjue-*; gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 2026-07-... |
| `fenjue-routing-health-check` | 7 | False | global_skills | 2.1.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=2.1.0(semver); 命名域:fenjue-*; gitAdd=2026-07-22|chore: 初始化 skill ... |
| `hermes-installer` | 10 | True | global_skills | community | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=community; 命名域:hermes-installer*; gitAdd=2026-08-05|R178 升级轮: 大SKILL分卷(A-g... |
| `ican-frontend-design-system` | 7 | False | global_skills | 1.0.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.0.0(semver); 命名域:ican-*; gitAdd=2026-09-10|[rule_editor] feat(... |
| `oc-dispatch-exec-guard` | 12 | True | global_skills | 1.0 | disk:global_skills(本地原生); registry:user_created=true; source=user; version=1.0(semver); 命名域:oc-dispatch*; gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 2026-07-22... |
| `openclaw-dual-gate-quality-audit` | 12 | True | global_skills | 1.3.0 | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=1.3.0(semver); 命名域:openclaw-*; gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 20... |
| `openclaw-fenjue-weekly` | 12 | True | global_skills | 2.0.0 | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=2.0.0(semver); 命名域:openclaw-*; gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 20... |
| `openclaw-task-supervision` | 12 | True | global_skills | 1.3.0 | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=1.3.0(semver); 命名域:openclaw-*; gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 20... |
| `prompt-consolidation` | 7 | False | global_skills | 2.1.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=2.1.0(semver); 命名域:prompt-*; gitAdd=2026-07-22|chore: 初始化 skill ... |
| `prompt-system-audit` | 7 | False | global_skills | 1.3.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.3.0(semver); 命名域:prompt-*; gitAdd=2026-07-22|chore: 初始化 skill ... |
| `skill-defer-to-authority` | 7 | False | global_skills | 1.1.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.1.0(semver); 命名域:skill-*; gitAdd=2026-07-22|chore: 初始化 skill 库... |
| `skill-drift-surgery` | 12 | True | global_skills | 1.0.0 | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=1.0.0(semver); 命名域:skill-*; gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 2026-... |
| `skill-hitrate-full-audit` | 10 | True | global_skills | community | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=community; 命名域:skill-*; gitAdd=2026-08-03|chore: 补录 28 个未跟踪技能目录 + 恢复 .giti... |
| `skill-hitrate-improvement-pipeline` | 10 | True | global_skills | community | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=community; 命名域:skill-*; gitAdd=2026-08-03|chore: 补录 28 个未跟踪技能目录 + 恢复 .giti... |
| `skill-manager` | 10 | True | global_skills | community | disk:global_skills(本地原生); registry:user_created=true; source=community; version=community; 命名域:skill-*; gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 2026-07-22 收... |
| `skill-merge` | 12 | True | global_skills | 1.0.1 | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=1.0.1(semver); 命名域:skill-*; gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 2026-... |
| `skill-midtask-recheck` | 12 | True | global_skills | 1.0.0 | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=1.0.0(semver); 命名域:skill-*; gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 2026-... |
| `skill-routing-regeneration` | 10 | True | global_skills | community | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=community; 命名域:skill-*; gitAdd=2026-08-03|chore: 补录 28 个未跟踪技能目录 + 恢复 .giti... |
| `skill-routing-test-driven-fix` | 10 | True | global_skills | community | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=community; 命名域:skill-*; gitAdd=2026-08-03|chore: 补录 28 个未跟踪技能目录 + 恢复 .giti... |
| `skill-trigger-diagnosis` | 7 | False | global_skills | 1.0.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.0.0(semver); 命名域:skill-*; gitAdd=2026-07-22|chore: 初始化 skill 库... |
| `skills-security-check` | 10 | True | global_skills | community | disk:global_skills(本地原生); registry:user_created=true; source=community; version=community; 命名域:skills-security-check*; gitAdd=2026-07-22|chore: 初始化 skill 库仓库... |
| `static-site-batch-audit-fix` | 10 | True | global_skills | community | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=community; 命名域:static-site*; gitAdd=2026-08-03|chore: 补录 28 个未跟踪技能目录 + 恢复 ... |
| `story-cover` | 7 | False | global_skills | 1.0.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.0.0(semver); 命名域:story-*; gitAdd=2026-08-05|R178 升级轮: 大SKILL分卷... |
| `story-deslop` | 7 | False | global_skills | 1.0.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.0.0(semver); 命名域:story-*; gitAdd=2026-08-05|R178 升级轮: 大SKILL分卷... |
| `story-import` | 7 | False | global_skills | 1.0.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.0.0(semver); 命名域:story-*; gitAdd=2026-08-05|R178 升级轮: 大SKILL分卷... |
| `story-long-analyze` | 7 | False | global_skills | 1.0.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.0.0(semver); 命名域:story-*; gitAdd=2026-08-05|R178 升级轮: 大SKILL分卷... |
| `story-long-scan` | 7 | False | global_skills | 1.0.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.0.0(semver); 命名域:story-*; gitAdd=2026-08-05|R178 升级轮: 大SKILL分卷... |
| `story-long-write` | 7 | False | global_skills | 1.0.1 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.0.1(semver); 命名域:story-*; gitAdd=2026-08-05|R178 升级轮: 大SKILL分卷... |
| `story-review` | 7 | False | global_skills | 1.1.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.1.0(semver); 命名域:story-*; gitAdd=2026-08-05|R178 升级轮: 大SKILL分卷... |
| `story-setup` | 7 | False | global_skills | 1.2.8 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.2.8(semver); 命名域:story-*; gitAdd=2026-08-05|R178 升级轮: 大SKILL分卷... |
| `story-short-analyze` | 7 | False | global_skills | 3.0.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=3.0.0(semver); 命名域:story-*; gitAdd=2026-08-05|R178 升级轮: 大SKILL分卷... |
| `story-short-scan` | 7 | False | global_skills | 1.0.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.0.0(semver); 命名域:story-*; gitAdd=2026-08-05|R178 升级轮: 大SKILL分卷... |
| `story-short-write` | 7 | False | global_skills | 1.0.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.0.0(semver); 命名域:story-*; gitAdd=2026-08-05|R178 升级轮: 大SKILL分卷... |
| `vp-perspective-audit` | 7 | False | global_skills | 1.1.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.1.0(semver); 命名域:vp-perspective*; gitAdd=2026-07-22|chore: 初始化... |
| `wb-git-commit-recipe` | 9 | False | global_skills | 1.1.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.1.0(semver); 命名域:wb-git-*; gitAdd=2026-09-06|feat(skill): 新增 w... |
| `wechat-automation` | 7 | False | global_skills | 1.0.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.0.0(semver); 命名域:wechat-*; gitAdd=2026-07-22|chore: 初始化 skill ... |
| `wechat-voice-transcription` | 10 | True | global_skills | community | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=community; 命名域:wechat-*; gitAdd=2026-08-03|chore: 补录 28 个未跟踪技能目录 + 恢复 .git... |
| `windows-bash-cli-interop-pitfalls` | 10 | True | global_skills | community | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=community; 命名域:windows-*; gitAdd=2026-08-03|chore: 补录 28 个未跟踪技能目录 + 恢复 .gi... |
| `windows-cli-utf8-wrapper` | 7 | False | global_skills | 1.0.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.0.0(semver); 命名域:windows-*; gitAdd=2026-07-22|chore: 初始化 skill... |
| `windows-gitbash-chinese-path-pit` | 7 | False | global_skills | 1.0.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=user-created; version=1.0.0(semver); 命名域:windows-*; gitAdd=2026-07-22|chore: 初始化 sk... |
| `windows-native-ocr` | 10 | True | global_skills | community | disk:global_skills(本地原生); registry:user_created=true; source=user-created; version=community; 命名域:windows-*; gitAdd=2026-08-03|chore: 补录 28 个未跟踪技能目录 + 恢复 .gi... |
| `workbuddy-mcp` | 7 | False | global_skills | 1.1.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.1.0(semver); 命名域:workbuddy-*; gitAdd=2026-08-15|R198.4 + 技能库清理... |
| `workflow-preflight-check` | 7 | False | global_skills | 1.0.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.0.0(semver); 命名域:workflow-*; gitAdd=2026-07-22|chore: 初始化 skil... |
| `wps-knowledgebase` | 7 | False | global_skills | 2.0.3 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=2.0.3(semver); 命名域:wps-*; gitAdd=2026-08-15|R198.4 + 技能库清理: nois... |

## MID（23）

| skill | 分数 | 注册表uc | disk源 | 版本 | 关键证据 |
|---|---|---|---|---|---|
| `agent-browser` | 4 | False | global_skills | 1.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.0(semver); gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 2026-07-22... |
| `cloudbase-db-optimize` | 4 | False | global_skills | 1.0.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.0.0(semver); gitAdd=2026-08-15|R198.4 + 技能库清理: noise_lint 正则修正... |
| `debugging-fixing` | 5 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; 命名域:debugging-fixing*; gitAdd=2026-07-22|chore: 初始化 s... |
| `discover-agent-cli` | 4 | False | global_skills | 1.0.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.0.0(semver); gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 2026-07-... |
| `hook-analyzer-skill` | 5 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; 命名域:hook-analyzer*; gitAdd=2026-07-22|chore: 初始化 skil... |
| `ican-deploy` | 5 | None | None | None | disk:未登记(orphan,待人工); disk:global_skills(本地原生); 命名域:ican-*; gitAdd=2026-09-11|[rule_editor] 新增 ican-deploy：PythonAnywhere 免控制台部署通道 + 地址名册 + 坑清单 (ican-deploy/... |
| `local-asr` | 5 | None | None | None | disk:未登记(orphan,待人工); disk:global_skills(本地原生); 命名域:local-*; gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 2026-07-22 收尾硬门禁加固 |
| `local-computer-use` | 5 | None | None | None | disk:未登记(orphan,待人工); disk:global_skills(本地原生); 命名域:local-*; gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 2026-07-22 收尾硬门禁加固 |
| `local-img2img` | 5 | None | None | None | disk:未登记(orphan,待人工); disk:global_skills(本地原生); 命名域:local-*; gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 2026-07-22 收尾硬门禁加固 |
| `local-mineru` | 5 | None | None | None | disk:未登记(orphan,待人工); disk:global_skills(本地原生); 命名域:local-*; gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 2026-07-22 收尾硬门禁加固 |
| `local-ocr-npu` | 5 | None | None | None | disk:未登记(orphan,待人工); disk:global_skills(本地原生); 命名域:local-*; gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 2026-07-22 收尾硬门禁加固 |
| `local-realtime-translator` | 5 | None | None | None | disk:未登记(orphan,待人工); disk:global_skills(本地原生); 命名域:local-*; gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 2026-07-22 收尾硬门禁加固 |
| `local-screenshot-qa` | 5 | None | None | None | disk:未登记(orphan,待人工); disk:global_skills(本地原生); 命名域:local-*; gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 2026-07-22 收尾硬门禁加固 |
| `local-tts` | 5 | None | None | None | disk:未登记(orphan,待人工); disk:global_skills(本地原生); 命名域:local-*; gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 2026-07-22 收尾硬门禁加固 |
| `local-txt2img` | 5 | None | None | None | disk:未登记(orphan,待人工); disk:global_skills(本地原生); 命名域:local-*; gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 2026-07-22 收尾硬门禁加固 |
| `local-vram` | 5 | None | None | None | disk:未登记(orphan,待人工); disk:global_skills(本地原生); 命名域:local-*; gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 2026-07-22 收尾硬门禁加固 |
| `office-automation-pro` | 4 | False | global_skills | 1.0.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.0.0(semver); gitAdd=2026-08-15|R198.4 + 技能库清理: noise_lint 正则修正... |
| `report-generator-skill` | 5 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; 命名域:report-generator*; gitAdd=2026-07-22|chore: 初始化 s... |
| `shell-encoding-pitfalls` | 5 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; 命名域:shell-encoding*; gitAdd=2026-07-22|chore: 初始化 ski... |
| `testing` | 4 | False | global_skills | 1.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); version=1.0(semver); gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 2026-07-22 收尾硬门禁加固 |
| `utf8-encoding-fix` | 5 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; 命名域:utf8-*; gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + ... |
| `video-whisper-transcribe` | 4 | False | global_skills | 1.1.0 | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=1.1.0(semver); gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 2026-07-... |
| `天眼一下` | 5 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; 命名域:天眼一下*; gitAdd=无 |

## LOW（30）

| skill | 分数 | 注册表uc | disk源 | 版本 | 关键证据 |
|---|---|---|---|---|---|
| `brainstorming` | 2 | None | None | None | disk:未登记(orphan,待人工); disk:global_skills(本地原生); gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 2026-07-22 收尾硬门禁加固 |
| `browser-cdp` | 2 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; gitAdd=2026-08-05|R178 升级轮: 大SKILL分卷(A-get-memory/fen... |
| `chart-visualization` | 2 | None | None | None | disk:未登记(orphan,待人工); disk:global_skills(本地原生); gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 2026-07-22 收尾硬门禁加固 |
| `clawhub` | 2 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 2026-07-22 收... |
| `coding-agent` | 2 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 2026-07-22 收... |
| `consulting-analysis` | 2 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 2026-07-22 收... |
| `data-analysis` | 2 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 2026-07-22 收... |
| `data-visualization` | 2 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 2026-07-22 收... |
| `defuddle` | 2 | None | None | None | disk:未登记(orphan,待人工); disk:global_skills(本地原生); gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 2026-07-22 收尾硬门禁加固 |
| `diagram-maker` | 2 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 2026-07-22 收... |
| `doc-coauthoring` | 2 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 2026-07-22 收... |
| `executing-plans` | 2 | None | None | None | disk:未登记(orphan,待人工); disk:global_skills(本地原生); gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 2026-07-22 收尾硬门禁加固 |
| `gsap` | 2 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 2026-07-22 收... |
| `hyperframes` | 2 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 2026-07-22 收... |
| `hyperframes-cli` | 2 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 2026-07-22 收... |
| `hyperframes-media` | 2 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 2026-07-22 收... |
| `hyperframes-registry` | 2 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 2026-07-22 收... |
| `json-canvas` | 2 | None | None | None | disk:未登记(orphan,待人工); disk:global_skills(本地原生); gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 2026-07-22 收尾硬门禁加固 |
| `node-inspect-debugger` | 2 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 2026-07-22 收... |
| `obsidian-bases` | 2 | None | None | None | disk:未登记(orphan,待人工); disk:global_skills(本地原生); gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 2026-07-22 收尾硬门禁加固 |
| `obsidian-cli` | 2 | None | None | None | disk:未登记(orphan,待人工); disk:global_skills(本地原生); gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 2026-07-22 收尾硬门禁加固 |
| `obsidian-markdown` | 2 | None | None | None | disk:未登记(orphan,待人工); disk:global_skills(本地原生); gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 2026-07-22 收尾硬门禁加固 |
| `pixelle-api-ensure` | 2 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 2026-07-22 收... |
| `python-debugpy` | 2 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 2026-07-22 收... |
| `refactoring` | 2 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 2026-07-22 收... |
| `spike` | 2 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 2026-07-22 收... |
| `story` | 2 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; gitAdd=2026-08-05|R178 升级轮: 大SKILL分卷(A-get-memory/fen... |
| `test-driven-development` | 2 | None | None | None | disk:未登记(orphan,待人工); disk:global_skills(本地原生); gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 2026-07-22 收尾硬门禁加固 |
| `web-design-guidelines` | 2 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; version=community; gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 2026-07-22 收... |
| `writing-plans` | 2 | None | None | None | disk:未登记(orphan,待人工); disk:global_skills(本地原生); gitAdd=2026-07-22|chore: 初始化 skill 库仓库 + 2026-07-22 收尾硬门禁加固 |

## EXCLUDE（49）

| skill | 分数 | 注册表uc | disk源 | 版本 | 关键证据 |
|---|---|---|---|---|---|
| `algorithmic-art` | -100 | False | global_skills | 1.0 | LICENSE:LICENSE.txt(官方/市场包) |
| `brand-guidelines` | -100 | None | None | None | LICENSE:LICENSE.txt(官方/市场包) |
| `byted-bp-cdn-pagesdeploy` | -100 | False | global_skills | community | source=skillhub(市场) |
| `byted-mediakit-shared` | -100 | False | global_skills | 1.0.0 | LICENSE:LICENSE(官方/市场包) |
| `byted-seedance-video-generate` | -100 | False | global_skills | community | LICENSE:LICENSE.txt(官方/市场包) |
| `byted-seedream-image-generate` | -100 | False | global_skills | community | LICENSE:LICENSE(官方/市场包) |
| `canvas-design` | -100 | False | global_skills | community | LICENSE:LICENSE.txt(官方/市场包) |
| `cloudbase__skillhub` | -100 | False | global_skills | community | source=skillhub(市场) |
| `computer-use-guidance-windows` | -100 | False | global_skills | 0.9.0 | .skill-metadata.yaml(官方元数据) |
| `create-skill` | -100 | False | global_skills | 1.0.0 | .skill-metadata.yaml(官方元数据) |
| `deep-research-pro` | -100 | False | global_skills | 1.0.0 | _meta.json:发布元数据(市场件) |
| `docx` | -100 | False | global_skills | 2.0.0 | .skill-metadata.yaml(官方元数据) |
| `electron` | -100 | False | global_skills | 1.0 | 精读人工判定:市场/上游件 |
| `elon-musk-perspective` | -100 | False | global_skills | community | LICENSE:LICENSE(官方/市场包) |
| `figma` | -100 | None | None | None | LICENSE:LICENSE.txt(官方/市场包) |
| `find-skills` | -100 | False | global_skills | 1.0.4 | .skill-metadata.yaml(官方元数据) |
| `first-principles-decomposer` | -100 | False | global_skills | community | _meta.json:发布元数据(市场件) |
| `frontend-design` | -100 | None | None | None | LICENSE:LICENSE.txt(官方/市场包) |
| `frontend-skill` | -100 | False | global_skills | 1.0 | LICENSE:LICENSE.txt(官方/市场包) |
| `frontend-slides` | -100 | False | global_skills | community | LICENSE:LICENSE(官方/市场包) |
| `github` | -100 | False | global_skills | community | _meta.json:发布元数据(市场件) |
| `gstack` | -100 | False | global_skills | 1.1.0 | LICENSE:LICENSE(官方/市场包) |
| `html-ppt` | -100 | False | global_skills | community | LICENSE:LICENSE(官方/市场包) |
| `install-skill-dependency` | -100 | False | global_skills | 1.0.0 | .skill-metadata.yaml(官方元数据) |
| `internal-comms` | -100 | None | None | None | LICENSE:LICENSE.txt(官方/市场包) |
| `knowledge-capture` | -100 | None | None | None | evaluations/(官方评测件) |
| `mcporter` | -1 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; homepage=http://mcporter.dev(外部来源); version=community; gitAdd=2026-07-22... |
| `meeting-intelligence` | -100 | None | None | None | evaluations/(官方评测件) |
| `multi-search-engine` | -100 | False | global_skills | community | _meta.json:发布元数据(市场件) |
| `nano-pdf` | -1 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; homepage=https://pypi.org/project/nano-pdf/(外部来源); version=community; gi... |
| `notion-cli` | -100 | None | None | None | LICENSE:LICENSE.md(官方/市场包) |
| `openai-whisper-api` | -1 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; homepage=https://platform.openai.com/docs/guides/speech-to-text(外部来源); v... |
| `oracle` | -1 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; homepage=https://askoracle.dev(外部来源); version=community; gitAdd=2026-07-... |
| `pdf` | -100 | False | global_skills | 1.0.1 | .skill-metadata.yaml(官方元数据) |
| `pptx` | -100 | False | global_skills | community | LICENSE:LICENSE.txt(官方/市场包) |
| `research-documentation` | -100 | None | None | None | evaluations/(官方评测件) |
| `screenshot` | -100 | False | global_skills | 1.0 | LICENSE:LICENSE.txt(官方/市场包) |
| `shadcn` | -100 | False | global_skills | 1.0 | evals/evals.json(官方评测件) |
| `skill-creator` | -100 | False | global_skills | community | LICENSE:license.txt(官方/市场包) |
| `skill-install` | -100 | False | global_skills | community | 精读人工判定:市场/上游件 |
| `slides` | -100 | None | None | None | LICENSE:LICENSE.txt(官方/市场包) |
| `spec-to-implementation` | -100 | None | None | None | evaluations/(官方评测件) |
| `sq-cleanmgr-c` | -100 | False | global_skills | 1.2.0 | _meta.json:发布元数据(市场件) |
| `taskflow` | -100 | False | global_skills | community | 精读人工判定:市场/上游件 |
| `taskflow-inbox-triage` | -100 | False | global_skills | community | 精读人工判定:市场/上游件 |
| `theme-factory` | -100 | None | None | None | LICENSE:LICENSE.txt(官方/市场包) |
| `ui-ux-pro-max` | -100 | False | global_skills | community | _meta.json:发布元数据(市场件) |
| `video-frames` | -1 | False | global_skills | community | disk:global_skills(本地原生); registry:user_created=false(字段已失真,不计负分); source=community; homepage=https://ffmpeg.org(外部来源); version=community; gitAdd=2026-07-22|... |
| `xlsx` | -100 | False | global_skills | 1.0.1 | .skill-metadata.yaml(官方元数据) |

