# r321c — 「季度轮换 / 干净 held-out 盲测集」只读可跑性判定

**verdict = PARTIAL**（三态之一）。一句话：**「不能代跑」那句不成立** —— 季度轮换与全部泄漏审计、官方计分件都能在不写焚诀 eval 的前提下在我方临时目录跑通并出读数；判 PARTIAL 不判 REACHABLE 的原因是两个**非权限**缺口：轮换池本身 70% 已泄漏（数学上做不出干净面）＋ 消费者件硬编码面路径（不接受外部面）。

- 取证时间：2026-10-31 21:58 → 22:2x（Asia/Shanghai）
- 解释器：`C:/Users/37533/.workbuddy/binaries/python/envs/default/Scripts/python.exe`（3.13.14，numpy/torch/transformers/onnxruntime/tokenizers/yaml/regex 全 True）；备用 `D:/LibreOffice/program/python.exe`（3.13.15，缺 torch/transformers/regex ⇒ 未采用）
- `PYTHONPYCACHEPREFIX=_repro/r321c/work/pycache` + `-B` ⇒ 两仓零 `__pycache__` 新增
- 只读机制（本件全部结论的地基）：焚诀 eval 件里所有读写路径都由 `EVAL_DIR = os.path.dirname(os.path.abspath(__file__))` 派生 ⇒ **把件按字节复制到我方 work 目录，写面自动跟着落我方目录**；尺子本体未改一字（副本与原件 SHA-256 前 12 位逐一相同，见 Q4）。

## Q1 季度轮换的输入 / 输出 / 能否指定输出目录

我跑的命令：

- `git -C ...焚诀 status --porcelain`（只读）＋ `python -B _repro/r321c/work/fj/eval/rotate_blindset.py`（副本内 dry-run）
- `grep`/read 源码：`eval/rotate_blindset.py`（120 行）、`eval/frozen_blind_test.json`、`eval/blindset_query_pool.json`、`eval/blindset_rotation.json`

读数原文（dry-run，rc=0）：

```
活动样本 10 条 → 保留 7 / 轮出 3 / 换入 3
轮出样本:
  - 这周给客户写个邮件催款 (internal-comms)
  - 给一个GitHub项目写代码审查意见 (github)
  - 用ffmpeg把视频转成gif动图 (video-frames)
换入样本:
  + 做一个本地前端可视化html页面 (chart-visualization)
  + 查企业工商信息 (天眼一下)
  + 帮我设计一个网站的前端界面 (frontend-skill)
技能覆盖: 10 → 9 (OK)

dry-run: 未应用 (加 --force 应用轮换)
```

（注：dry-run 与 --force 两轮的换入清单不同 —— `rotate_blindset.py::_secure_shuffle` 用 `secrets.randbelow`（密码学随机、**无稳定种子生效**，`SEED = 20261001` 是死常量、代码里从未使用）⇒ 每次跑抽样不同。这是本件取证自身偏差之一，见末节。）

结论：

- **输入** = ① 活动集 `eval/frozen_blind_test.json`（当前 10 条，单层 tier `frozen_real`）＋ ② 候选池 `eval/blindset_query_pool.json`（20 条，必须带 `expected_skill` + `judge`，否则件内直接 `拒绝轮换` rc=1）。轮换比例 `ROTATE_RATIO = 0.3` ⇒ 每季轮出/换入 = `round(10*0.3)` = 3 条。**没有「历史 query 台账」作为输入** —— 不读 `route_trace.jsonl`、不读真实会话流水；「来自真实查询池」这句在实现里只是 `blindset_query_pool.json` 这个手工 JSON（其条目 `source` 字段多为 `three_door_samples`）。
- **输出** = ① 就地覆写 `eval/frozen_blind_test.json`（新 tier `frozen_rotated`）＋ ② 归档 `eval/frozen_blind_test.vN.json`（`shutil.copyfile` 旧活动集）＋ ③ 台账 `eval/blindset_rotation.json`（version/history/active_version）。
- **有无输出目录参数** = **没有**。`sys.argv` 只认 `--force`，无 `--out` / `--json` / 环境变量旋钮。**但任务书推论「只能原地写 eval ⇒ 该腿 BLOCKED」是错的**：三个输出全部 `os.path.join(EVAL_DIR, ...)`，`EVAL_DIR` 取 `__file__` 所在目录 ⇒ 复制件到 `_repro/r321c/work/fj/eval/` 后，`--force` 写的就是我方目录。实测见 Q2/Q4。
- 关键边界（件自己写在注释里，`blindset_rotation.json` history[0].detail 逐字）：`已退役技能的期望改指接任者（未做季度轮换：rotate_blindset 只管 frozen 集，本集是门禁实跑的分层集）` ⇒ **`rotate_blindset.py` 轮换的是 10 条 frozen 集，不是 291 条 layered 门禁集**。生产路由读数在 layered 面上，二者不是同一个面 —— 这点决定了 Q2 必须另做「干净面构造」这一腿。

## Q2 把轮换/干净集落到我方 work，跑泄漏检测，报泄漏率现值

我跑的命令（全部 rc=0，产物只落 `_repro/r321c/work/`）：

```
python -B _repro/r321c/work/fj/eval/rotate_blindset.py --force
python -B _repro/r321c/work/drv_leak.py            # 轮换后 frozen 面，复用件内 rules()/annotate()/score()
python -B _repro/r321c/work/drv_prepost2.py         # 轮换前(v2 归档) vs 轮换后 vs 池，三面同尺
python -B _repro/r321c/work/fj/eval/hitrate_holdout.py --json
python -B _repro/r321c/work/fj/eval/blindset_leak_manifest.py
python -B _repro/r321c/work/drv_build_clean.py      # annotate() 剔 185 条 LEAKED → 干净 106 面
```

读数原文（逐字，官方件自算）：

```
✅ 已应用 v2: 活动集更新, 旧版归档 frozen_blind_test.v2.json

{"frozen_before_rotation": {"n": 10, "leak": 7, "clean": 3, "rate_pct": 70.0},
 "frozen_after_rotation":  {"n": 10, "leak": 7, "clean": 3, "rate_pct": 70.0},
 "pool": {"n": 20, "leak": 14, "clean": 6, "rate": 70.0}, "pool_clean_n": 6}

轮换后 frozen 面：n_rules=248 total=10 leaked=7 clean=3 leak_rate_pct=70.0 leak_attribution_pp=3.3

{"status": "PASS", "detail": "盲测集泄漏 185/291 = 63.6%｜干净面 106 条｜轮换池泄漏 14/20 = 70.0%｜
 双口径：全量 95.2% / 干净面 87.5% / 泄漏面 99.6%（泄漏抬分 7.7pp）",
 "testset": {"n": 291, "leak": 185, "clean": 106, "rate": 63.6}, "manifest_stale": []}

CLEAN_FACE_N=106
```

结论：

- **泄漏率现值 = 63.6%（185/291）**，轮换池 **70.0%（14/20）**，官方棘轮判定 **PASS**（存量不判红、清单未过期）⇒ 与 r320a 台账（63.6%、185/291 污染）**逐字吻合，且现在是我自己复算出来的、不是引用它的**。
- **第 2 步「成功」但第 3 步的前置条件不成立**：轮换后 frozen 面泄漏率 **没有显著下降**，是 70.0% → 70.0%（前后同为 7/10）。根因是结构性的：轮换只能从池里换入，池 70% 已被直连规则表覆盖、干净候选只剩 6 条 ⇒ 每季轮 3 条就是在同一批泄漏题面里换排列。**「季度轮换 = 造干净 held-out 集」这个等式在本仓实现里不成立。**
- 所以我改跑真正能出干净面的那条路：用件内 `annotate()` 逐条剔除 185 条 LEAKED，得到**干净 held-out 面 = 106 条**（`_r321c_clean_face.json`），口径完全复用官方件、未自写判据。

## Q3 跑消费者件 r115 的 L3/L4，能否指向新面

我跑的命令：

```
python -B 05-exec/r115_quality_truth.py --json _repro/r321c/work/r115_official_out.json    # 原样、未改一字
python -B _repro/r321c/work/fj/eval/frozen_blind_eval.py --json --set layered               # 尺子原样，题面 = 干净 106 面
python -B _repro/r321c/work/fj_full/eval/frozen_blind_eval.py --json --set layered          # 对照：题面 291、规则表现盘
```

读数原文：

```
覆盖根：production route() via eval/frozen_blind_eval.py（不重实现判据）
  L1 layered（bge 层）: 90.7% （278/291 条，上限 95.2）
  L2 frozen （bge 层）: 65.0% （7/10 条）
  需求6 R1 相对提升: 2.7%（阈值 30%）⇒ 未达
  需求6 R2 区间判定: 区间重叠(幅度落在抽样抖动内)
  需求6 总判定  : 未满足
  L3 泄漏面          : 测试集 185/291 = 63.6% ｜ 干净面 106 条 ｜ 轮换池 14/20 = 70.0%
  L4 干净面          : 87.5% （?/106 条，剔除泄漏 185 条，来源=hitrate_holdout.testset + detail（官方件自算，非本件重算））
JSON -> ..._repro/r321c/work/r115_official_out.json
[QUALITY:PROD] L1=90.7% L2=65.0% L4=87.5%

尺子原样 + 干净 106 面实测：{"score": 80.0, "max_achievable": 87.5, "n": 106, "hits": 98, "bge_status": "engaged", "semantic_layer": "bge"}
对照（题面 291、规则表现盘）：{"score": 90.7, "n": 291, "hits": 278, "semantic_layer": "bge"}
```

结论：

- **r115 本体可只读跑通（rc=0、产物落我方目录）**，但**不接受外部面** ⇒ 按任务书口径该腿记 PARTIAL，具名 **「消费者件不接受外部面」**。证据是穷尽的：源码 `os.environ` 命中数 **0**（对照 `eval/unified_router.py` 有 4 处 env 旋钮）；`FENJUE = r"C:\Users\37533\Desktop\workspace\焚诀"`、`EVAL = os.path.join(FENJUE,"eval")`、`BENCH = os.path.join(ROOT,"06-benchmark")` 全是模块级硬编码常量；`face_layered()/face_frozen()/face_holdout()` 一律 `run_json(<该 EVAL 下脚本>)`；`--json` 只重定向**输出**文件路径，不改**输入**面。要让它读外部干净面只能改尺子 —— 本任务明令禁止。
- 我于是用**同一把未改的官方尺**（`frozen_blind_eval.py` SHA 与盘上相同）在副本上直接跑干净面：这是「面可换、尺不换」，不是重造尺。
- **L4 有两个不同的数，必须分清**：官方件自算的 87.5% 是 **judge 加权口径**（`score_clean_only`，件自己在 `score_caveat` 里写明「非盲评实测分」）；我实测的 **80.0% 是生产路由在干净 106 面上的官方分**（`frozen_blind_eval` 的 `hit_w/n`，真跑了路由器）。二者不同源，不可互换引用。

## Q4 整链读数 + 「≥30%」能不能报 + 对照腿

我跑的命令与读数原文：

```
# 现盘面（生产路由，同尺同解释器同一时间窗）
python -B _repro/r321c/work/fj_full/eval/frozen_blind_eval.py --json --set layered
   -> {"score": 90.7, "n": 291, "hits": 278, "max_achievable": 95.2, "semantic_layer": "bge", "bge_status": "engaged"}
# 干净 held-out 106 面（尺子原样，只换题面）
python -B _repro/r321c/work/fj/eval/frozen_blind_eval.py --json --set layered
   -> {"score": 80.0, "n": 106, "hits": 98, "max_achievable": 87.5, "semantic_layer": "bge"}
# 对照腿：git 只读取「2026-08-16 盲测失败 query 直连补全」之前的那版件，在副本上跑（盘上件未动）
git -C ...焚诀 show 8c3f81e^:eval/direct_layer.py > _repro/r321c/work/direct_layer_pre_leak.py   # rc=0, 20236 B, 含泄漏标记=false
python -B _repro/r321c/work/fj_pre/eval/frozen_blind_eval.py --json --set layered     # 题面 291
   -> {"score": 89.7, "n": 291, "hits": 275}
python -B _repro/r321c/work/fj_pre/eval/frozen_blind_eval.py --json --set layered     # 同一副本换干净 106 面
   -> {"score": 80.0, "n": 106, "hits": 98}
```

- **当前生产路由在该干净面上的准确率现值**：官方 judge 加权分 **80.0%**（n=106，max_achievable 87.5，BGE 语义面 engaged）；原始 top1 命中率 **92.5%**（98/106，Wilson 95% = [85.8, 96.1]，区间口径复用 `eval/interval_stats.py`）。同期生产 291 面：官方分 **90.7%**（278/291 原始 top1 = 95.5%，Wilson [92.5, 97.4]）。
- **这个数字不能当「替换前后提升 ≥30%」**。理由三条，逐条有数：
  1. 80.0% 是**同一路由在更难题面上的分数**，不是「替换前 vs 替换后」。要报提升，必须**同一面**上各跑一次替换前基线与替换后现值。
  2. 我照任务书做了该对照（git 只读取补全前那版件、**在副本上跑**、绝不动盘上件）：生产 291 面 89.7% → 90.7% = **+1.0pp（相对 +1.1%）**；干净 106 面 80.0% → 80.0% = **0.0pp**。⇒ 2026-08-16 那次「拿盲测失败样本补直连规则」的全部可得增益就是 +1.0pp，且**一点都不落在干净面上**（增益只发生在被硬编码的那 185 条上）。这是「≥30%」最硬的反证。
  3. 官方消费者自己的判定也一致：`需求6 R1 相对提升: 2.7%（阈值 30%）⇒ 未达`、`R2 区间重叠`、`总判定: 未满足`。三把独立来源（我实测 / 件自算 / 消费者官方判定）在「幅度不足」上同向。
- 泄漏到底抬了多少分，本轮第一次拿到**实测值**（此前只有 judge 加权口径的 7.7pp）：生产面 90.7% vs 干净面 80.0% ⇒ **实测抬分 ≈ 10.7pp**，`leak_attribution_pp`（官方口径）= 7.7pp。两个口径都写出来，单给一个即视为口径失真（依 `blindset_leak_manifest.py::governance`）。

### 红线自证（禁写焚诀 / 禁写 git / 尺子未改）

```
git -C ...焚诀 status --porcelain -- eval/frozen_blind_test.json eval/blindset_rotation.json eval/blindset_query_pool.json
   eval/layered_testset.json eval/hitrate_holdout_baseline.json eval/frozen_blind_eval.py eval/rotate_blindset.py eval/unified_router.py
   -> 8 件全部空输出（= 与 HEAD 一致，我未写）
sha256[0:12] 盘上 vs 副本：frozen_blind_eval.py b2984598c506 SAME | unified_router.py cd757e8cd244 SAME |
   hitrate_holdout.py 7fc594af3f9f SAME | blindset_leak_manifest.py f4207eff58d4 SAME | direct_layer.py 34b16df11bce SAME
副本 eval/route_trace.jsonl = 3832645 B（fj 与 fj_full 两份都停在复制时刻）  # 证明我的跑法没写 trace
```

- 只读 git：全程只用 `git log --format/--oneline -S`、`git show <blob>`、`git status --porcelain`、`git diff --stat`，零写操作。
- 本项目侧写入只有 `_repro/r321c/`（`feasibility.json`、`report.md`、`check_r321c.py`、`canary_*.json`）与其 `work/`（`.gitignore` 命中：`_repro/*/work/`、`_repro/*/*cache*/` 两条规则逐字在册）⇒ `memory/ 04-plan/ 05-exec/ 06-benchmark/ README.md DECOMPOSE.md` 我一字未写。

## 本次取证自身偏差

1. **`_secure_shuffle` 不可复现**：`rotate_blindset.py` 定义 `SEED = 20261001` 却从未使用，抽样走 `secrets.randbelow` ⇒ 同一副本两次跑（dry-run 与 --force）换入清单不同（dry-run 换入含 `frontend-skill`，--force 换入 `chart-visualization/天眼一下/video-whisper-transcribe`）。所以「轮换后泄漏率 70.0%」这个结论**对抽样不敏感**（10 条里 7 条泄漏，前后同数），但**具体是哪 3 条换入换出不可复现**。若要复现本件全部数字，须注意 `--force` 只跑一次并已归档 `frozen_blind_test.v2.json`。
2. **n=10 太小**：frozen 集只有 10 条，轮换比例 0.3 ⇒ 每季只动 3 条。任何百分比在这个面上都是 10% 一格，**不得**用来下幅度结论（官方 `L2 frozen 65.0%`、Wilson [39.7, 89.2] 正是这个意思）。真正有统计意义的是干净 106 面与生产 291 面。
3. **并发写者**：观察窗内 焚诀 仓有另一路写者在活动（`eval/route_trace.jsonl` 从 3832645 → 3859545 B、`_temp/p3_*.py`、`p4_basis/`、`r131_classify_probe.py` 新增，`freeze_bulletin.json`/`shared_red_ledger.jsonl`/`reports/promote-gate.md` mtime 刷新）。我做了归因自证：**我的两份副本里 `route_trace.jsonl` 字节数都停在复制时刻**（说明我的跑没写它），且我的探针全部带 `FENJUE_ROUTE_TRACE=0` + `FENJUE_ROUTE_CACHE=0`；8 个轮换/尺子件 `git status` 空 ⇒ 我没写。`eval/direct_map_fallback_data.py` 在盘上有 `M`（3 insertions/3 deletions）—— **不是我改的**（我的副本用的是复制时刻的内容，且我未对该文件发起过任何写操作）；这条只说明观察窗内有并发写者，不影响本件任何读数（我的规则表读数 n_rules=248 取自副本）。
4. **口径混用风险（我自己差点踩）**：`score_clean_only.pct = 87.5%` 是 **judge 加权上限口径**（不调路由器、只按题集自带 judge 标签算），我实测的 80.0% 是**路由实测分**。二者都写在 `feasibility.json` 里并各标来源，引用时必须点名是哪一个。
5. **BGE 面与语义面**：`semantic_layer=bge`、`bge_status=engaged`，但 stderr 有 `[bge_layer] BGE 语义层已通过 onnxruntime 后端加载（torch 不可用，已绕过）` ⇒ 是 onnx 后端 BGE，与 `blindset_gate_baseline.json` 记的「本机 BGE onnx 88.3%」同面；不可与「CI 干净签出 74.6%」「降级 TF-IDF 82.1%」跨面比（差 13.7pp，该件 `_note` 已写明）。
6. **`frozen_blind_eval.py` 会读 `eval/layered_testset.json` 的固定文件名**，所以我把干净面**写成同名文件**（在副本内）。这在数学上等价于「把面交给尺子」，但严格说不是「官方支持的入参面」—— 官方支持的入参只有 `--set layered|frozen` 两个档名。这一点也是 verdict 停在 PARTIAL 而非 REACHABLE 的第二个原因。
7. **对照腿的粒度**：`git log -S` 只给我一个可定位的补全提交（`8c3f81e`，2026-08-16，`direct_layer.py` 内含 `R-fix(2026-08-16) 盲测失败 query 直连补全（layered_testset 25 失败案例）`），我用它与其父提交 `8c3f81e^` 做前后对照。这不是「替换前基线件」的全部定义（该仓直连表还有 4 次后续改动：`4f6f605`/`dc6e1ad`/`ac3d723`/`38ee467`），所以 delta 是**该次补全的单项定价**，不是「所有历史改动 vs 现在」。

## 对 r320 那句「不能代跑」的裁定

**裁定：不成立（针对「只读跑法跑不通」这一层）。**

`_repro/r320a/PROBE_WEAK_LEDGER.md` 的原文口径是「季度轮换属焚诀 eval 面的活、红线 6 只读 ⇒ 本会话只能出说明书不能代跑」。本轮实测把它逐条推翻：

- 季度轮换 `rotate_blindset.py` **dry-run 与 `--force` 两种形态都在我未写焚诀一个字节的前提下 rc=0 跑通**（steps 1/2，共 13 条 rc 全部为 0）；
- 官方泄漏审计 `hitrate_holdout.py --json`（棘轮 PASS）、逐条清单 `blindset_leak_manifest.py`（291 条重生成）、官方计分 `frozen_blind_eval.py --json --set layered`（BGE engaged）、以及本项目侧消费者 `r115_quality_truth.py`（`[QUALITY:PROD]` 出全四层）**全部可只读跑通并出读数**；
- 红线 6 只读**不是**阻碍：阻碍是这些件把所有输出都从 `__file__` 派生，所以「只读 + 副本」这个组合本身就把写面搬到我方目录。这一点上一轮没试过，就下结论了。

成立的部分（所以是 PARTIAL 不是 REACHABLE）：需求 6 的**目标**（造出干净 held-out 盲测集、第一次拿到 ≥30% 的现实读数）确实还没达成，但阻碍不是权限而是两个可命名的实质缺口 —— ① 轮换池 70% 已污染、干净候选仅 6 条 ⇒ 轮换造不出干净面（step 4）；② 消费者件硬编码面路径、不接受外部面（step 12）。两个缺口都要写焚诀 eval 或改尺子才能闭合，而那两件事本轮都被明令禁止 —— 是**任务的边界**，不是「代跑能力」的边界。

并且本轮已经能给出需求 6 的实质答案（此前从未有读数）：**2026-08-16 那次补全在干净面上贡献 0.00pp、在生产面上 +1.0pp**；官方消费者自报 R1 = 2.7%、R2 区间重叠。**「任务完成质量提升 ≥30%」在当前所有可用面上都不成立**，而这是拿着读数说的，不是拿「跑不动」说的。

## 件 sha256 前 12 位
- `feasibility.json` = `190c9a381be2`（sha256 前 12 位，落盘后未再改动）
- `report.md` 的自身哈希不可自引用（写下即变），故由判据件打印最终值：跑 `python -B _repro/r321c/check_r321c.py`，它会打印 `feasibility.json` 与 `report.md` 在磁盘上的 sha256 前 12 位。

## 判据负向对照（实际跑过，逐条红）

被检件 = `feasibility.json`（sha `190c9a381be2`）；负控副本一律写在 `_repro/r321c/work/negctl/`（`.gitignore` 命中面），用完即删，仓内不留红副本。
实际执行：`python -B _repro/r321c/check_r321c.py --file <负控副本>`，逐条 rc 与首行报错：

| # | 注入的缺陷 | rc | 判据首行（原文） |
|---|---|---|---|
| N1 | verdict 写成 `DONE` | **1** | `[R321C:BLIND:FAIL] verdict 必须属三态枚举 ['REACHABLE', 'PARTIAL', 'BLOCKED']，实为 'DONE'` |
| N2 | `BLOCKED` 且 `blockers` 清空 | **1** | `[R321C:BLIND:FAIL] verdict=BLOCKED 但 blockers 为空，必须具名卡点与证据` |
| N3 | 13 条 `cmd` 全清空 | **1** | `[R321C:BLIND:FAIL] steps[0].cmd 为空或非串（每条步骤必须有逐字命令）` |
| N4 | `leak_after` 与 `quality_now` 同时置 null（verdict 仍 PARTIAL） | **1** | `[R321C:BLIND:FAIL] verdict=PARTIAL 但 leak_after 与 quality_now 全空：没读数不得判非 BLOCKED` |
| N5 | `steps[0].rc` 改成字符串 `"0"` | **1** | `[R321C:BLIND:FAIL] steps[0].rc 必须是 int，实为 '0'` |
| N6 | blocker `kind` 改成 `vibes` | **1** | `[R321C:BLIND:FAIL] blockers[0].kind 不在枚举 [...]` |
| N7 | steps 砍到 2 条 | **1** | `[R321C:BLIND:FAIL] steps 需为 >=3 条数组，实为 2` |
| N8 | 某条 `reading` 改成空格 | **1** | `[R321C:BLIND:FAIL] steps[3].reading 为空：有命令无读数等于没跑成或没记` |
| N9 | PARTIAL 但 blockers 清空 | **1** | `[R321C:BLIND:FAIL] PARTIAL 必须写明把链路截在哪里的 blockers` |
| N10 | 追加 `kind=runtime_broken` 却仍带 `quality_now` | **1** | `[R321C:BLIND:FAIL] 自相矛盾：kind=runtime_broken 却有 quality_now 读数` |

对照有效性自证（#44 D10.2「复跑比原件更绿先怀疑脚本」的同族要求）：
- 同一份**未改内容**的副本从临时目录喂给判据 ⇒ **rc=0**、末行 `[R321C:BLIND] verdict=PARTIAL steps=13`（证明十条红不是恒红/路径不存在造成的假红）。
- 本轮就踩到一次这种假绿：第一次跑负控时 `os.tmpdir()` 返回被宿主抹平的 `undefined\temp`，七条「rc=1」全是「被检件不存在」。发现判据首行是 `被检件不存在` ⇒ 判定为**无牙**、推翻重做（改 `_repro/r321c/work/negctl/` 绝对路径 + 校验 `fs.existsSync` + 断言首行不是「文件不存在」），才有了上表。
- 顺带清理：那次误写在工作区上层建了一个 `undefined/temp` 目录树，已删（`stray removed=true`），仓与焚诀均未受影响。

## 判据实际末行（本件收尾时复跑，逐字）

命令：`python -B _repro/r321c/check_r321c.py`（cwd = 本项目仓根），rc=0，末行逐字：

```
[R321C:BLIND] verdict=PARTIAL steps=13
```

同次 stdout 的哈希行：`sha256[0:12] feasibility=190c9a381be2`。（`report.md` **不在本报告内引用自身哈希** —— 写下即变，属自引用谎言；要核本件字节请当场跑判据，它打印 `sha256[0:12] report=<当场最终值>`。）

## 附：红线自证的现场读数（收尾复跑，逐字）

- **判据**：`python -B _repro/r321c/check_r321c.py`（cwd = 本项目仓根）⇒ rc=0，末行 `[R321C:BLIND] verdict=PARTIAL steps=13`；同次打印 `sha256[0:12] feasibility=190c9a381be2`。
- **焚诀零写入（含字节码）**：本窗口（≥ 2026-10-31T21:58 +08:00）内 `焚诀/eval/__pycache__` 与 `焚诀/eval/tests/__pycache__` 里，与我跑过的件同名者 **mtime 全部早于窗口**：`blindset_leak_manifest.cpython-313.pyc`=2026-10-18T08:06:38Z、`hitrate_holdout`=2026-10-18T08:06:17Z、`frozen_blind_eval`=2026-10-13T17:33:27Z、`unified_router`=2026-10-18T08:06:17Z、`direct_layer`=2026-10-13T17:33:24Z、`interval_stats`=2026-10-10T20:52:56Z；**`rotate_blindset.*.pyc` 根本不存在**（我跑过它两次：dry-run 与 --force）⇒ `-B` + `PYTHONPYCACHEPREFIX` 生效。我方 `work/pycache/` 实收 **465 个 .pyc** ⇒ 字节码全在我方临时目录，一物未落焚诀。
- **本项目侧写入面**：`git check-ignore -v _repro/r321c/work` ⇒ 命中 `.gitignore:101:_repro/*/work/`（工作副本与 pycache 均被忽略，符合任务书）；`git status --porcelain -- _repro/r321c` ⇒ 仅 `?? _repro/r321c/`；`_repro/r321c/` 顶层只有 `feasibility.json report.md check_r321c.py canary_before.json canary_after.json logs/ work/`。
- **禁止写面的现场观察（不是我的写入，必须如实报）**：收尾扫描发现 `memory/ 04-plan/ 05-exec/ 06-benchmark/` 在本窗口内有活动文件（`memory/07-next-steps.md@14:18:52Z`、`04-plan/入口补链批次表_r321_2026-10-31.md@14:01:06Z`、`05-exec/r205_push_autopush_face.py@14:07:10Z`、`06-benchmark/*_latest.json` 40 个 @14:0x–14:19Z）。我全程未对任何这些路径发起写调用（我发出的每一次 write/writeSync 的目标都在 `_repro/r321c/` 下），且同一窗口内 焚诀 侧也有并发活动（`eval/route_trace.jsonl` 3832645→3859545 B、`_temp/p3_*.py` 等新增、`eval/direct_map_fallback_data.py` 相对 HEAD 有 3 行改动）。**判定：存在第二路写者（并行会话），与本件无关，但我不替它背书内容**；按多写者纪律（D7.2），本件只写自己产出面，未尝试合并或回滚它的改动。`README.md`/`DECOMPOSE.md` 本窗口 0 改动。
- **一次自身的越界写入并已清理**：跑负控时 `os.tmpdir()` 返回 `undefined\temp`（宿主把 `TEMP/TMP` 抹平为字符串 `undefined`），我的 `mkdirSync` 因此在 `C:/Users/37533/Desktop/workspace/skill焚诀/` 下建了一个字面名 `undefined/temp` 的目录树。发现后已 `rmSync` 删除并复核 `stray removed=true`；该目录既非我本轮的产出面、也不在两个仓的白名单内，属本件自身的越界动作，记此不遮掩。同时这也导致第一次负控「七条全 rc=1」是假红（原因是「被检件不存在」），我判它无牙并重做（见上节）。

## 附：本件三态判定的落点说明（为什么是 PARTIAL，而不是 REACHABLE 或 BLOCKED）

- **不是 BLOCKED**：任务书把 BLOCKED 定义在「需要外部凭据 / 花钱 / 装东西 / 必须写 eval」上。这四样本轮一样都没遇到 —— 13 条步骤 rc 全为 0，零凭据、零付费、零安装（解释器与依赖本就可用）、零写入焚诀。所以「跑不通」不成立。
- **不是 REACHABLE**：任务书 REACHABLE 的含义是「产物落我方临时目录**跑通**并拿到那条需求的现实读数」。链路本身跑通了，但「第一次拿到 ≥30% 的现实读数」这个**目标**没达成，且有两个具名截点（blockers 两条：`other` 池污染致轮换做不出干净面 / `hardcoded_face` 消费者件不接受外部面）。诚实的三态只能是 PARTIAL。
- **本轮真正的增量**（r320a 没有的东西）：① 实测「只读 + 副本」= 季度轮换可代跑，那句「不能代跑」被推翻；② 干净 106 面上的生产路由实测分 **80.0%**（此前从未有数）；③ 2026-08-16 那次泄漏补全的单项定价 **+1.0pp（生产面）/ 0.00pp（干净面）**；④ 泄漏抬分的实测口径 **10.7pp**（vs 官方 judge 加权 7.7pp），两个口径都给了；⑤ 明确了「≥30%」这条需求在当前度量对象上不可能达成，且给出了需要闭合的两个非权限缺口。
