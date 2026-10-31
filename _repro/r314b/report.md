# r314b — gstack 吸收证据包（季度扫描唯一 UPSTREAM_CHANGED 候选）

> 生产轮：r314 派发 · 现取时刻 2026-10-31T18:3x–19:0x+08（gh 实时通道）· 本件只供证据，**不代裁**。

## 1. 读数表

| 面 | 上游 capy/skill/gstack/SKILL.md | 本地受管根 gstack/SKILL.md（git show HEAD） | 三性标注 |
|---|---|---|---|
| blob sha | 8ef728bd161403ef862a76300259d32afc4c517e | 3d9592a92789f36cbbeb567676c715fa6f2533a0 | 真实：contents API / main 树 / 重取件 hash-object 三向一致；复算：check_r314b.py sha1 重算 |
| sha256 | 5a2c368e04d36d63b7229b81ffe0b8ec8487101b8d6d41525e2111297a3fedc4 | 5c00c92e1160b6b1e0a6208a862681d9a57ee13f042f4613cc3ae79c9a598de1 | 复算：判据脚本内 hashlib 重算 |
| bytes / lines | 21608 / 87 | 27307 / 643 | 真实：同一取法落盘后 wc -c |
| version | frontmatter **无** version（仅 name/description） | 1.3.0（last_updated 2026-10-27） | 时效：现读；映射缺口见 UNK-04 |
| license | MIT（gh repo.license 现取；LICENSE blob 35029511 size=1066） | frontmatter 无 license；侧车 LICENSE = MIT (Copyright (c) 2026 Garry Tan) | 真实：gh 现取 + 侧车首行亲读 |
| commit 钉 | 文件级最新 b6cb70ae（10-31T07:22:56Z, v1.91.355.0）；季档钉 99706a47（07:35:05Z，非文件级）；现仓库 HEAD 4f02cb57（10:23:41Z） | 文件级最新 3763f4dc（2026-10-27T11:21:52+08:00） | 时效：三 commit 并存，漂移风险 = UNK-01 |
| 季档锚点 | baseline 11bd23cc（17898B，对象库现验存在）→ 8ef728bd | baseline_local == current_local（local_changed=false） | 真实：audit_2026-10-31T0749Z.json 亲读；local 面 sha 差 = UNK-03 |

## 2. 逐块语义 diff 结论

- 双向切块（围栏内伪标题已滤除）：上游 = frontmatter + 10 节；本地 = frontmatter + 17 节。
- **复拉自检**：判据跑完后再次独立现拉（gh contents API + git show HEAD），两侧 sha256 与记录一致、31 个 verbatim 块按行区间重切逐字全等（evidence/recheck.txt）。
- **重合仅 3 行**（---、name: gstack、---）。上游 10 节全部进「增量清单」（absorb_evidence.json → increments，逐字 verbatim + 行区间）；本地 18 块全部进「本地独有清单」（local_only，行区间可指）。
- 上游件 = Capy 开局引导/准入协议（install --check trailer、GSTACK_LAUNCH、autoplan/ship DRIVER、Captain 批准链、pregate、host 适配、maintenance）；本地件 = Claude Code 生成版 browse QA 手册（命令参考/快照/断言/QA 流程）。两者功能异质 —— 「吸收」若成立等于把整个文件换成功能族，不是打补丁。该形态判断进 UNK-02（配对错位疑点，直配对象可能是上游 browse/SKILL.md e5792ca5）。

## 3. 不代裁声明

**本件不代裁值不值得吸收。** 增量清单证明上游在动的内容全在 Capy 宿主协议族；本地独有清单证明受管吸收（v1.2.0 browse v2.0.0）走的是另一条直系文件。要不要吸收、按哪条配对吸收、是否换 path_rule，由裁定方（季度巡检拍板面）决定。

## 4. 若吸收需过的既有门（现名册，未跑）

1. **landing spec 五腿**（口径源：06-benchmark 全量对标报告_r308，第五件行）：R 重放链==HEAD / N 在册件 blob 等值 / P bare=0 / V frontmatter version==Version history / M 镜像 match —— 跑法 python 05-exec/landing_replay_check.py --spec 05-exec/landing_specs/gstack.json，五腿全 ok 才 gate=PASS。
2. **回滚链**：吸收提交必须显式文件清单 + 可 revert；回退点 = 现 blob 3d9592a9（HEAD c5d8391d），再前一级 4d93fb31（v1.2.0 受控吸收轮）；季档 pin（11bd23cc→8ef728bd）不得被吸收件改写。
3. **当季入册义务**（04-plan 季度巡检机制 r113 规范）：吸收/不吸收裁决与 SHA 锚点入 2026Q4 version_scan 档 + 07 台账留痕；unknown 禁登记纪律照 UNK 清单走。

## 5. 判据与负控

```
C:/Users/37533/.workbuddy/binaries/python/envs/default/Scripts/python.exe -B 自建skill优化/_temp/r314b/check_r314b.py --selftest
```

期望末行：`[R314B:EVID] increments=10 local_only=18 upstream_blob=8ef728bd1614 verbatim_all_reverified=true unknown=6`，且前两行 NEG-A/NEG-B 均 PASS（腿A = INC-01 verbatim 末字符翻一个 ⇒ 复核必 false；腿B = 删一条 local_only ⇒ 计数必 -1）。

## 6. unknown（六条，见 JSON unknown）

UNK-01 commit 漂移 · UNK-02 配对错位疑点（capy 件 vs browse 件） · UNK-03 季档 local sha 与 blob sha256 不一致（疑 CRLF 工作区） · UNK-04 两套版本编号体系无映射 · UNK-05 基线→现值演变未逐 commit 展开 · UNK-06 侧车（captain.md/factory.md/install.sh）未逐字节对账。
## 7. 写面自证

- 本件新建仅 `自建skill优化/_temp/r314b/`（三件 + evidence/ 17 件取证快照）。临时中转目录已清理。
- 受管根 `D:/global_skills` 未写：HEAD 仍 `c5d8391dbea1ff16c666c2278d277a4bf09b37fb`、`HEAD:gstack/SKILL.md` 仍 `3d9592a9…`。`git status --porcelain -- gstack/` 现报 `M gstack/qa/templates/qa-report-template.md` —— **该 dirty 为会话前已存在**（本件对 gstack/ 只跑过 git show / rev-parse / log，全部只读），按 #40「会话前 dirty 不并入」登记，不代处理。
- 未跑 run_gates；未写 `D:/global_memory`（该仓 porcelain 610 行为其既有并发状态，本件零触碰）。
