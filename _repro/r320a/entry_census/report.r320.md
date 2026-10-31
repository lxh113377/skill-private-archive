# r319 A1b — 吸收件入口可达性全库巡检（新缺陷类「落盘未入口」系统首查）

- 受管根 D:/global_skills HEAD：`e8f489ebcf788f9b4f258ab96bb6c3cf465c5b25`
- 树来源：recon_rows(_recon_rows.json)，共 16509 条（复用前臂侦察件，未重跑 ls-tree、未重做侦察）
- 巡检面：absorption_baseline.json 在册吸收件 52 件（一手清单，非猜）
- 结果：`court=pass` broken=10 orphans=624 orphan_kb=4781（孤儿真字节合计 4895569 B）
- 缺入口（HEAD 无 <slug>/SKILL.md）：无

## 判据命令

```bash
export PYTHONPYCACHEPREFIX=/tmp/r319a_pyc
cd C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化/_temp/r319a
python -B check_r319a.py
```

期望末行：`[R319A:ENTRY] court=pass skills=52 broken=<n> orphans=<n> orphan_kb=<n>`

## 两极堂（判据自证 #44 D10.2 实测值）

| 极 | 用例 | broken | orphans | 文件数 | 判定 |
|---|---|---|---|---|---|
| 正例（已知答案） | `coding-agent@HEAD` | 0 | 0 | - | pass |
| 反例·孤儿轴 | `coding-agent@a0092c9c~1`（source=draft_rev） | 0 | 4 | 9 | pass |
| 反例·断链轴 | `html-ppt@HEAD`（source=substituted_current_state） | 1 | 15 | 227 | pass |

草稿反例值：`NEG_ORPHAN_CASE=('coding-agent', 'a0092c9c~1')`、`NEG_BROKEN_CANDIDATE=('frontend-skill', '0fcf7842~1')`。草稿值跑不通时改用哪一态，逐字见下面堂录（SUBSTITUTED / recent_commit 都已声明）。

```
POS coding-agent@HEAD broken=0 orphans=0 files=9 => pass
orphan TRY coding-agent@a0092c9c~1 broken=0 orphans=4 files=9
orphan USE coding-agent@a0092c9c~1 orphans=4 source=draft_rev
broken TRY frontend-skill@0fcf7842~1 broken=0 orphans=0 files=4
broken TRY frontend-skill@0fcf7842~1~1 broken=0 orphans=0 files=4
broken TRY frontend-skill@0fcf7842~1~2 broken=0 orphans=0 files=4
broken TRY frontend-skill@0fcf7842~1~3 broken=0 orphans=0 files=4
broken TRY frontend-skill@0fcf7842~1~4 broken=0 orphans=0 files=3
broken TRY coding-agent@e8f489ebc (recent commit) broken=0 orphans=0
broken TRY coding-agent@a0092c9c9 (recent commit) broken=0 orphans=0
broken TRY A-prompt-better@f39eb3c0d (recent commit) broken=0 orphans=0
broken TRY A-prompt-better@17cc0c811 (recent commit) broken=0 orphans=0
broken TRY A-prompt-better@3d3bb0a98 (recent commit) broken=0 orphans=0
broken TRY security-audit@221c548bf (recent commit) broken=0 orphans=0
broken TRY security-audit@a9a98ba69 (recent commit) broken=0 orphans=0
broken SUBSTITUTED html-ppt@HEAD broken=1 source=substituted_current_state（草稿 rev 与近史均未报出该轴，改用 HEAD 可复现缺陷态）
```

反例孤儿样本：`references/dispatch-and-poll.md`, `references/multi-task-queues.md`, `references/review-and-land.md`, `references/writing-the-brief.md`
反例断链样本：`examples/my-talk/index.html`

## 负控两腿（逐字读数）

- 腿A 孤儿腿有牙（取一个已判孤儿，把它的 basename 注入内存态入口正文重算；纯内存，不写真造对象）
  用例 slug=`ppt-master` 探针目标=`scripts/docs/svg-pipeline.md`
  base=171 → 注入后=170（判据要求 base-1）→ 同一入口第三次重算=171（判据要求回到 base，证明不恒绿也不抖动）⇒ pass
- 腿B 断链腿有牙（注入一个不存在目标须 +1；再把同一目标假造进内存路径集合须回原值，证明判据看树存在性而非名字形状）
  用例 slug=`coding-agent` 探针目标=`references/_neg_probe_r319a_missing.md`
  base=0 → 注入后=1（判据要求 base+1）→ 假造进内存树后=0（判据要求回到 base）⇒ pass

## 孤儿 top10（按 ls-tree -l 真字节）+ 每孤一句空转成本

| # | 件 / 路径 | 字节 | 空转成本（一句） |
|---|---|---|---|
| 1 | `ppt-master/scripts/docs/svg-pipeline.md` | 96720 | 已 git 落盘（字节在仓里）但入口不链：路由面每次加载 `ppt-master` 都读不到这 94.5 KB，吸收（翻译/适配/校对）产出 0 次被消费 = 纯空转 |
| 2 | `ppt-master/scripts/docs/svg-contract.md` | 57858 | 已 git 落盘（字节在仓里）但入口不链：路由面每次加载 `ppt-master` 都读不到这 56.5 KB，吸收（翻译/适配/校对）产出 0 次被消费 = 纯空转 |
| 3 | `ppt-master/scripts/docs/confirm_ui.md` | 56205 | 已 git 落盘（字节在仓里）但入口不链：路由面每次加载 `ppt-master` 都读不到这 54.9 KB，吸收（翻译/适配/校对）产出 0 次被消费 = 纯空转 |
| 4 | `ppt-master/references/executor-base.md` | 52613 | 已 git 落盘（字节在仓里）但入口不链：路由面每次加载 `ppt-master` 都读不到这 51.4 KB，吸收（翻译/适配/校对）产出 0 次被消费 = 纯空转 |
| 5 | `ppt-master/references/image-generator.md` | 45140 | 已 git 落盘（字节在仓里）但入口不链：路由面每次加载 `ppt-master` 都读不到这 44.1 KB，吸收（翻译/适配/校对）产出 0 次被消费 = 纯空转 |
| 6 | `ppt-master/references/strategist.md` | 38546 | 已 git 落盘（字节在仓里）但入口不链：路由面每次加载 `ppt-master` 都读不到这 37.6 KB，吸收（翻译/适配/校对）产出 0 次被消费 = 纯空转 |
| 7 | `ppt-master/references/svg-effects.md` | 36609 | 已 git 落盘（字节在仓里）但入口不链：路由面每次加载 `ppt-master` 都读不到这 35.8 KB，吸收（翻译/适配/校对）产出 0 次被消费 = 纯空转 |
| 8 | `story-long-write/references/anti-ai-writing.md` | 36483 | 已 git 落盘（字节在仓里）但入口不链：路由面每次加载 `story-long-write` 都读不到这 35.6 KB，吸收（翻译/适配/校对）产出 0 次被消费 = 纯空转 |
| 9 | `story-review/references/anti-ai-writing.md` | 36483 | 已 git 落盘（字节在仓里）但入口不链：路由面每次加载 `story-review` 都读不到这 35.6 KB，吸收（翻译/适配/校对）产出 0 次被消费 = 纯空转 |
| 10 | `story-setup/references/agent-references/anti-ai-writing.md` | 36483 | 已 git 落盘（字节在仓里）但入口不链：路由面每次加载 `story-setup` 都读不到这 35.6 KB，吸收（翻译/适配/校对）产出 0 次被消费 = 纯空转 |

其余 614 个孤儿逐条见 `entry_scan.json` 的 per_skill[].orphans。按件汇总：

| 件 | 孤儿数 | 孤儿字节 |
|---|---|---|
| `ppt-master` | 171 | 1568391 |
| `story-setup` | 132 | 1035408 |
| `story-long-write` | 96 | 939012 |
| `story-short-analyze` | 29 | 304987 |
| `story-short-write` | 26 | 226001 |
| `story-review` | 15 | 168457 |
| `canvas-design` | 27 | 118615 |
| `hyperframes` | 36 | 94117 |
| `story-long-analyze` | 11 | 90040 |
| `data-analysis` | 7 | 66539 |
| `story-import` | 12 | 61149 |
| `hyperframes-media` | 8 | 36622 |
| `gstack` | 6 | 33312 |
| `story-deslop` | 6 | 30225 |
| `ui-ux-pro-max` | 2 | 29177 |
| `diagram-maker` | 3 | 23673 |
| `html-ppt` | 15 | 15213 |
| `story-cover` | 2 | 13800 |
| `story-scan` | 5 | 12316 |
| `agent-browser` | 1 | 11191 |
| `frontend-skill` | 1 | 7420 |
| `theme-factory` | 10 | 5315 |
| `hyperframes-registry` | 3 | 4589 |

## 断链清单（全量）

- `html-ppt/examples/my-talk/index.html`：入口写着它，HEAD 树里没有（断链）
- `story-cover/references/split-NN.md`：入口写着它，HEAD 树里没有（断链）
- `story-deslop/references/split-NN.md`：入口写着它，HEAD 树里没有（断链）
- `story-import/references/split-NN.md`：入口写着它，HEAD 树里没有（断链）
- `story-long-analyze/references/split-NN.md`：入口写着它，HEAD 树里没有（断链）
- `story-long-write/references/split-NN.md`：入口写着它，HEAD 树里没有（断链）
- `story-review/references/split-NN.md`：入口写着它，HEAD 树里没有（断链）
- `story-setup/references/split-NN.md`：入口写着它，HEAD 树里没有（断链）
- `story-short-analyze/references/split-NN.md`：入口写着它，HEAD 树里没有（断链）
- `story-short-write/references/split-NN.md`：入口写着它，HEAD 树里没有（断链）

## 剔除直方图（入口正文 token 的去向，可审计；样本见 entry_scan.json 的 skip_samples）

```json
{
 "no_dir": 48866,
 "no_ext": 528,
 "empty": 383,
 "absolute": 1567,
 "ext_not_routable": 33,
 "outside_slug": 77,
 "url_scheme": 111,
 "upstream_mirror": 6,
 "repo_root_ref": 1,
 "parent_jump": 4,
 "outside_repo": 2
}
```

## 口径、边界与已知偏差

1. 只读纪律：全程只有 git rev-parse / git show / git ls-tree / git log；未读工作树任何入口外内容；写面仅本目录三件。
2. 断链口径：正文 token → norm（剔 URL、占位符 <x>/$VAR、..、绝对路径、无目录段、不可路由扩展）→ 剔上游镜像前缀（absorption_baseline.json 的 repo + upstream_path 一手数据）、别的 slug 跨件指针、仓外兄弟仓根 → 归位本 slug → 查 HEAD 树存在性。
3. 一处主动收紧（拿漏判换假阳性归零）：断链只在「本 slug 已存在的一级子目录」内判存在性；一级目录段整段写错的落 outside_slug 剔除，不进断链数。
4. 孤儿口径：本 slug 距根 >=2 段的 .md/.txt（references/ 及同类，递归含孙子目录），basename、去扩展名、原文小写子串三级兜底都不在入口名册 ⇒ 孤儿。第三级兜底必须有：path_tokens 把 CJK 当分隔符，不兜底会把中文文件名的真入链件系统性误判成孤儿。
5. 保守方向汇总：同目录散件的裸引用（只写 SKILL.md 这类无目录段 token）被 no_dir / outside_slug 剔除，不计断链；散文里提到某 md 文件名即算入链、不计孤儿。两个偏差都只会低估缺陷，不会凭空造缺陷。
6. 本次补完修掉的前臂缺陷两处：tree_at 的 docstring 三引号未闭合（SyntaxError，上一臂只交半成品的真实卡点）；新增 unquote 还原 109 条八进制引号路径（否则中文名被系统性误判）。

## 末行

```
[R319A:ENTRY] court=pass skills=52 broken=10 orphans=624 orphan_kb=4781
```
