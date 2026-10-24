# 免费工具 x 工作流 x skill 搭配名册（生成物，勿手改）

生成命令：python 05-exec/r215_free_tool_roster.py --json <件>

## 依据面（五道判据当前读数）

| 判据 | 量什么 | 读数 |
|---|---|---|
| 163 | 工具在本机能不能跑 | 名册 10 项 |
| 93 | 每个工具是否至少被一个 skill 承载 | 工具 10 / 扫描 1718 卷 / 未承载 0 |
| 92 | 每轮入口会不会把话术派到写着答案的卷 | 判 8 / 缺口 0 |
> 依据面取值：163 见 free_tools_latest.json；93 见 tool_carrier_latest.json 与 tool_skill_matrix_probe.json；92 见 ingress_latest.json；88 见 recall_latest.json 与 route_truth_latest.json。再生命令见文件头。
| 88 | 窗口 / BGE 真值 / 任务语句三层 | 窗口 3、真值 2、任务 7 命中 4、缺口 5 |

## 逐工具搭配态

### GitHub - READY

- 承载面：317 个文件 / 100 个技能
    （取值：tool_skill_matrix_probe.json 的 tools[] 内 GitHub 项的 hit_files / skill_count）
- 守它的判据：163 + 87 + 93
- 工作流触点：A-project-handoff 的 git_autopush 钩子模板（本仓 post-commit 即其落地）+ 第 87 门读 autopush 末行 rc；私有仓分钟用满是已付代价
- 触点提及核验：A-project-handoff -> IN_SKILL_DESC
- 任务语句实测：
    - CI 红了 -> HIT_DIRECT（top1=ci-pipeline-debugging，期望件=ci-pipeline-debugging）
    - 钩子静默推送 -> HIT（top1=win-toolchain-pitfalls，期望件=win-toolchain-pitfalls）
    - Actions 分钟 -> HIT（top1=chaoshi-web-deploy，期望件=chaoshi-web-deploy）

### Cloudflare-D1 - READY

- 承载面：25 个文件 / 14 个技能
    （取值：tool_skill_matrix_probe.json 的 tools[] 内 Cloudflare-D1 项的 hit_files / skill_count）
- 守它的判据：163 + 88 任务层 + 93
- 工作流触点：A-memory-start 的 quickref 额度专章（r196_quota_face 现读行数/写入）+ chaoshi-web-deploy 的 d1 execute 部署链
- 触点提及核验：A-memory-start -> MENTIONS
- 触点提及核验：chaoshi-web-deploy -> IN_SKILL_DESC
- 任务语句实测：
    - D1 查额度 -> MISS（top1=wps-knowledgebase，期望件=A-memory-start）

### Cloudflare-R2 - GAP_SERVICE

- 承载面：25 个文件 / 14 个技能
    （取值：tool_skill_matrix_probe.json 的 tools[] 内 Cloudflare-R2 项的 hit_files / skill_count）
- 守它的判据：163 + 88 任务层 + 93
- 工作流触点：chaoshi-image-optimization 的 R2 外置专章（干跑读数 + 阻断现状）
- 触点提及核验：chaoshi-image-optimization -> IN_SKILL_DESC
- 任务语句实测：
    - R2 开桶 -> MISS（top1=libreoffice-headless-win，期望件=chaoshi-image-optimization）

### Cloudflare-Pages - READY

- 承载面：306 个文件 / 59 个技能
    （取值：tool_skill_matrix_probe.json 的 tools[] 内 Cloudflare-Pages 项的 hit_files / skill_count）
- 守它的判据：163 + 92 + 93
- 工作流触点：chaoshi-web-deploy 部署权威入口（direct_map 10 pattern，任务话术直连命中）
- 触点提及核验：chaoshi-web-deploy -> IN_SKILL_DESC
- 任务语句实测：
    - Pages 部署 -> HIT_DIRECT（top1=chaoshi-web-deploy，期望件=chaoshi-web-deploy）

### Cloudflare-Workers - READY

- 承载面：140 个文件 / 36 个技能
    （取值：tool_skill_matrix_probe.json 的 tools[] 内 Cloudflare-Workers 项的 hit_files / skill_count）
- 守它的判据：163 + 88 任务层 + 93
- 工作流触点：A-memory-start 的 quickref 额度专章（r199_workers_face 现读调用数）；跨 zone 聚合分母差异已写 §9.16
- 触点提及核验：A-memory-start -> MENTIONS
- 任务语句实测：
    - Workers 调用量 -> MISS（top1=chaoshi-image-optimization，期望件=A-memory-start）

### SQLite - READY

- 承载面：13 个文件 / 11 个技能
    （取值：tool_skill_matrix_probe.json 的 tools[] 内 SQLite 项的 hit_files / skill_count）
- 守它的判据：163 + 85 + 93
- 工作流触点：第 85 门用 SQLite 做门禁台账派生索引（读面与盲区均实测）
- 触点提及核验：本行未点名任何 skill = 纯散文，不可证伪（勿当已核）
- 任务语句实测：名册无对应条目（不编造）

### VS Code - READY

- 承载面：101 个文件 / 46 个技能
    （取值：tool_skill_matrix_probe.json 的 tools[] 内 VS Code 项的 hit_files / skill_count）
- 守它的判据：163 + 93
- 工作流触点：第 65 名册面本地探针（which + 非 0 字节 + 真跑 --version）
- 触点提及核验：本行未点名任何 skill = 纯散文，不可证伪（勿当已核）
- 任务语句实测：名册无对应条目（不编造）

### Cloudflare-Turnstile - READY

- 承载面：10 个文件 / 4 个技能
    （取值：tool_skill_matrix_probe.json 的 tools[] 内 Cloudflare-Turnstile 项的 hit_files / skill_count）
- 守它的判据：163 + 88 任务层(DISPUTED) + 93
- 工作流触点：曾在超市 web 全链接通，后按老大要求移除 = 决定而非待搭缺口
- 触点提及核验：本行未点名任何 skill = 纯散文，不可证伪（勿当已核）
- 任务语句实测：
    - Turnstile -> DISPUTED（top1=codebuddy-chat-web，期望件=chaoshi-image-optimization）

### Resend - GAP_CRED

- 承载面：6 个文件 / 2 个技能
    （取值：tool_skill_matrix_probe.json 的 tools[] 内 Resend 项的 hit_files / skill_count）
- 守它的判据：163 + 93
- 工作流触点：仅 HTTP API 无 CLI；凭据缺，尚未接入任何工作流
- 触点提及核验：本行未点名任何 skill = 纯散文，不可证伪（勿当已核）
- 任务语句实测：名册无对应条目（不编造）

### Upstash-Redis - GAP_CRED

- 承载面：42 个文件 / 22 个技能
    （取值：tool_skill_matrix_probe.json 的 tools[] 内 Upstash-Redis 项的 hit_files / skill_count）
- 守它的判据：163 + 93
- 工作流触点：仅 REST 无 CLI；凭据缺，尚未接入任何工作流
- 触点提及核验：本行未点名任何 skill = 纯散文，不可证伪（勿当已核）
- 任务语句实测：名册无对应条目（不编造）

