# 四维扫描基线

> 目标 85 个（HIGH+MID 置信自建）

## 体积维度（SKILL.md > 4KB）

| skill | 字节 | 超4KB | references 文件数 |
|---|---|---|---|
| `chaoshi-web-deploy` | 39430 | ✅ | 0 |
| `story-import` | 36837 | ✅ | 6 |
| `A-memory-start` | 36557 | ✅ | 11 |
| `story-short-write` | 35725 | ✅ | 19 |
| `story-setup` | 35572 | ✅ | 10 |
| `story-review` | 35403 | ✅ | 8 |
| `openclaw-task-supervision` | 33721 | ✅ | 0 |
| `A-get-memory` | 31793 | ✅ | 9 |
| `prompt-system-audit` | 31734 | ✅ | 0 |
| `story-deslop` | 30146 | ✅ | 2 |
| `agent-browser` | 29055 | ✅ | 7 |
| `skill-manager` | 28864 | ✅ | 0 |
| `A-prompt-better` | 28676 | ✅ | 0 |
| `story-long-analyze` | 25853 | ✅ | 6 |
| `fenjue-routing-health-check` | 24555 | ✅ | 0 |
| `skills-security-check` | 21804 | ✅ | 0 |
| `openclaw-dual-gate-quality-audit` | 21571 | ✅ | 0 |
| `wps-knowledgebase` | 21325 | ✅ | 0 |
| `story-long-write` | 19862 | ✅ | 42 |
| `wechat-automation` | 18446 | ✅ | 0 |
| `data-layer-consistency-fix` | 18321 | ✅ | 0 |
| `story-short-analyze` | 17018 | ✅ | 20 |
| `ican-frontend-design-system` | 16712 | ✅ | 1 |
| `skill-defer-to-authority` | 16397 | ✅ | 0 |
| `prompt-consolidation` | 16131 | ✅ | 0 |
| `vp-perspective-audit` | 15325 | ✅ | 0 |
| `c-cleanup` | 15283 | ✅ | 0 |
| `story-cover` | 15034 | ✅ | 1 |
| `chaoshi-image-optimization` | 11445 | ✅ | 0 |
| `windows-cli-utf8-wrapper` | 11220 | ✅ | 0 |
| `skill-hitrate-improvement-pipeline` | 11042 | ✅ | 0 |
| `A-ask-questions` | 10739 | ✅ | 1 |
| `cross-platform-skill-sync` | 10278 | ✅ | 0 |
| `dogfood` | 10236 | ✅ | 1 |
| `workflow-preflight-check` | 9951 | ✅ | 0 |
| `fenjue-memory-audit` | 9737 | ✅ | 4 |
| `skill-routing-regeneration` | 9219 | ✅ | 0 |
| `天眼一下` | 9066 | ✅ | 0 |
| `9b-lightworkflow` | 8807 | ✅ | 0 |
| `skill-trigger-diagnosis` | 8687 | ✅ | 0 |
| `skill-hitrate-full-audit` | 8683 | ✅ | 0 |
| `skill-routing-test-driven-fix` | 8523 | ✅ | 0 |
| `discover-agent-cli` | 8506 | ✅ | 0 |
| `cloudbase-db-optimize` | 8364 | ✅ | 0 |
| `skill-merge` | 8132 | ✅ | 0 |
| `skill-drift-surgery` | 8089 | ✅ | 0 |
| `ican-deploy` | 7401 | ✅ | 0 |
| `A-java-problem` | 7094 | ✅ | 3 |
| `local-realtime-translator` | 6729 | ✅ | 0 |
| `windows-bash-cli-interop-pitfalls` | 6724 | ✅ | 0 |
| `wb-git-commit-recipe` | 6400 | ✅ | 0 |
| `chaoshi-admin-inline-edit` | 6220 | ✅ | 0 |
| `static-site-batch-audit-fix` | 5816 | ✅ | 0 |
| `video-whisper-transcribe` | 5725 | ✅ | 0 |
| `local-tts` | 5482 | ✅ | 0 |
| `audit-runner-safe-aggregate` | 5364 | ✅ | 0 |
| `local-computer-use` | 4923 | ✅ | 0 |
| `local-screenshot-qa` | 4798 | ✅ | 0 |
| `utf8-encoding-fix` | 4668 | ✅ | 0 |
| `local-mineru` | 4651 | ✅ | 0 |
| `windows-gitbash-chinese-path-pit` | 4530 | ✅ | 0 |
| `openclaw-fenjue-weekly` | 4325 | ✅ | 0 |
| `workbuddy-mcp` | 4262 | ✅ | 1 |
| `local-txt2img` | 4189 | ✅ | 0 |
| `skill-midtask-recheck` | 4118 | ✅ | 0 |
| `shell-encoding-pitfalls` | 4108 | ✅ | 0 |

## 触发维度（description 过短 <40 字 = 触发描述弱）

| skill | desc 长度 | 显式触发词段 | 有 version | 有 name |
|---|---|---|---|---|
| `prompt-system-audit` | 34 | 0 | True | True |
| `agent-browser` | 36 | 0 | True | True |
| `A-ask-questions` | 29 | 0 | True | True |
| `dogfood` | 30 | 0 | True | True |
| `windows-gitbash-chinese-path-pit` | 39 | 0 | True | True |
| `debugging-fixing` | 32 | 0 | True | True |
| `testing` | 23 | 0 | True | True |

## 死链 / 弃用平台名

| skill | 死链候选 | 弃用平台名 |
|---|---|---|
| `story-short-write` | - | Claude Code |
| `story-setup` | scripts/generate-codex-agents.py, scripts/sync-opencode.py | Claude Code |
| `story-review` | - | Claude Code |
| `openclaw-task-supervision` | - | QW , QoderWork |
| `A-get-memory` | scripts/trace_view.py | - |
| `prompt-system-audit` | - | QW  |
| `wps-knowledgebase` | references/workflow.md, scripts/run.js | Claude Code |
| `story-long-write` | - | Claude Code |
| `data-layer-consistency-fix` | - | Claude Code |
| `skill-defer-to-authority` | - | QClaw |
| `vp-perspective-audit` | - | QClaw, QW , QoderWork |
| `chaoshi-image-optimization` | - | QW  |
| `windows-cli-utf8-wrapper` | - | Claude Code |
| `skill-hitrate-full-audit` | - | QW  |
