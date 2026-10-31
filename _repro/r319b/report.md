# r319b · A2/G4 — gstack 改配的 browse 逐条对账补齐件

> 终裁出处 = `_repro/r317a/LEAD_ADJUDICATION.md` 第 3 条（browse 当时触发/工具两维弃权判 unclear、不许判同族）。
> 本件只做三件事：① browse/SKILL.md 的 triggers/allowed-tools/命令面逐项抽出；② 与本地件逐条对账
> （命中给两侧原文行，不命中给本地最近对应物）；③ G2 轴集原口径复跑 + 先过已知答案堂，堂过才出 verdict。
> 尺子零改动：词表全用 r316b 现件（PURPOSE_VERBS/TRIG_ONLY/TOOL_NOUNS/FAMILIES/STOP），阈值 0 处修改，
> **没有为凑改配放宽弃权规则**（G2 诚实先例照守）。

## 0. 结论（堂过之后由 G2 as-is 规则给出）

```
[R319G4:BROWSE] court=pass verdict=unclear matched-axes=3/6
```

- **verdict=unclear —— 合格产出**（brief 判据纪律：对账后触发/工具两维仍 0 命中 ⇒ unclear 即合格）。
- 弃权维 = D5_trigger_face / D6_tool_command：browse 侧词表命中集仍为空（fm triggers 三条与 allowed-tools
  三条都不含 TRIG_ONLY 短语；正文内联码/CLI token 与 TOOL_NOUNS 交集为空），abstain=2 ⇒ G2 规则 floor=unclear。
- 字面对账的增量证据（下节）不改变这一读数：它证明的是「形态上像」，不是「G2 签名轴可用」。**不许**拿
  allowed-tools 3/3 逐字同块去顶替 D6（D6 量的是正文命令面，不是 frontmatter 声明；替换维度=动尺）。

## 1. 读面与钉（全部可复算）

| 件 | 钉 | 结果 |
|---|---|---|
| 本地入口 | `git show HEAD:gstack/SKILL.md`（受管根只读，HEAD=e8f489eb） | sha256=5c00c92e…，与 r316b 落盘记录**一致** |
| browse 件（evidence） | blob sha 复算 e5792ca5… | 与 gh api **现值逐字节一致**（live_matches_evidence=true，上游未漂移） |
| browse 件 tmpl | blob 0655b388… | evidence=现值，一致 |
| 行数口径 | git show 给 LF（644 行）；盘上 CRLF（643 行） | r317 R241 校正注的 643/644 之差=行尾口径，非内容漂移 |
| 侧卷 | `D:/global_skills/gstack/references/browse-v2-upstream.md`（324 行） | 标题逐字「受控吸收 garrytan/gstack/browse」 |

## 2. 逐项对账（124 条，全表在 browse_check.json `reconciliation`）

### 2.1 frontmatter triggers（browse 3 条 ⇒ 本地入口 0/3 命中）

| browse 条目（行号） | 本地入口 | 本地最近对应物（词元重合） |
|---|---|---|
| `- browse a page`（L7） | 不命中 | L7 description：…verify page state, take annotated screenshots…（ov=1） |
| `- open this url`（L8） | 不命中 | L103 Then offer to open the essay in their default browser:（ov=1） |
| `- take page screenshot`（L9） | 不命中 | L7 …take annotated screenshots…（ov=2，语义最近但非逐字） |

⇒ **这就是 D5 弃权的逐条实底**：browse 的触发面是「祈使句短语」形态，本地件触发语义写在 description 散文里
（"Use when you need to test a feature…"），两侧形态不互含 ⇒ TRIG_ONLY 命中集 browse 侧仍为空。**维持弃权，不救。**

### 2.2 allowed-tools（browse 3 条 ⇒ 本地入口 3/3 逐字命中）

`Bash` / `Read` / `AskUserQuestion` 三行在两侧 frontmatter 逐字同块（browse L11-13 ↔ 本地 L22-24）。
这是三方案「改配 browse」手里**最硬的一条新增字面证据**；但它落在 D1/D5 都不读的面上（D5 词表不含工具名，
D6 只读正文内联码），故轴值不变。

### 2.3 命令面（机械抽取 118 条：$B 子命令/aside CLI/aside API 函数/gstack bin/slash 命令）

| kind | 条数 | 命中入口件 | 命中侧卷 | 说明 |
|---|---|---|---|---|
| $B-subcommand | 15 | **15/15** | 15 | 全部命令名逐字在入口件 Command Reference（goto/snapshot/click/fill/console/…） |
| aside-cli | 2 | 0/2 | 2/2 | `aside repl`/`aside exec` 只活在侧卷（Aside 分支被搬进受控吸收卷，不在入口件） |
| aside-api-fn | 68 | 29/68 | 60/68 | 机械抽取含散文噪音（openTab/closeTab/annotatedScreenshot… 全 MISS） |
| gstack-bin | 9 | 1/9 | 4/9 | browse v2 preamble 的 gstack-skill-start/skill-end/learnings-log 族在本地**不存在**（侧卷卷首「整包回拉实测否决」正是为它） |
| slash-command | 24 | 9/24 | 18/24 | MISS 的 /scrape /benchmark /canary /pair-agent 等指向 browse 引用而本地无对应件 |
| **合计** | **118** | **54/118（45.8%）** | **99/118（83.9%）** | 入口件=headless $B 分支；Aside 分支在侧卷 |

42 条连「词元重合>0 的最近对应物」都没有（多为 Aside JS API 专有词：openTab、attachBrowserTab、ASIDE_DIR 形态）⇒
本地件对 browse 是**部分吸收**（headless 面逐字、Aside 面入侧卷、preamble bin 族整段缺失），不是全量重写。

## 3. 轴集原口径复跑（G2 dims + r316c siglib 双尺）

### 3.1 G2 六轴（browse 对 vs r316b 落盘值）**逐维 drift=0**；本地件三集合字段 drift=0

```
AXIS-RERUN browse : h1=0.0 dom=True pur=0.8 trg=None tool=None head=0.12 code=0.2338 cos=0.9449 sem=0.8 abstain=2 disproof=1/5
MATCHED-AXES browse=3/6 (capy 负参照=2/6) 弃权维=[D5_trigger_face, D6_tool_command]
```

matched-axes=3/6 的定义=六条集合轴中 |A∩B|≥2 的条数（D4 pur inter=4、S2 head inter=3、S3 code inter=36 过线；
D3/D5/D6 交集 0）。对照反例 capy=2/6 ⇒ browse 确实「更近」，但 G2 的 same_family_rule 要求 abstain≤1，
browse abstain=2 ⇒ 三选一里只能落 **unclear**。

### 3.2 siglib（r316c 现成件只读复用）双读法

| 读法 | A1 | A2 | A3 | A4 判别词包含 | A5 块级包含 |
|---|---|---|---|---|---|
| 入口件单文件 ↔ browse | .0874 | .6364 | .1531 | .4604 | .5123 |
| **整包**（含侧卷）↔ browse | .0751 | .74 | .1813 | **.9457** | **.9235** |
| 整包 ↔ capy（负参照） | .0181 | .5769 | .043 | .5061 | .5361 |
| 堂正例 docx ↔ anthropic | .0863 | .5484 | .1818 | .6994 | .7738 |

⚠ 整包面对 browse 的 A4/A5 逼近 1 是**循环证据**：侧卷正文就是从 browse 逐字抄的受控吸收卷——它证明的是
「我们吸过它」，不是「入口件血缘于它」。故本行只报告不参与裁定（与 G2 弃权读向一致）。单文件面
（A4=.4604）反而低于堂正例 docx（.6994），与 unclear 不矛盾。

## 4. 已知答案堂（先过堂才出 verdict）

- 本件内联复跑两极 + 双腿负控：`COURT docx=same-family gstack-capy=diff-family negA=diff-family negB=unclear -> qualified=true`。
- G2 原件 check 独立复跑（`--selftest`，输出落 `ev/r316b_court_rerun.json`）**逐字**：

```
COURT+ docx<->anthropic/docx  verdict=same-family sem=0.7857  abstain=0 gates=3/3 | h1=0.25 dom=True pur=0.8571 trg=1.0 tool=0.5 head=0.1667 code=0.3673 cos=0.9867
COURT- gstack<->capy          verdict=diff-family sem=0.6     abstain=2 gates=2/3 | h1=0.0 dom=False pur=0.6 trg=None tool=None head=0.0 code=0.0719 cos=0.7361
ALT1   gstack<->browse        verdict=unclear     sem=0.8     abstain=2 gates=3/3 | h1=0.0 dom=True pur=0.8 trg=None tool=None head=0.12 code=0.2338 cos=0.9449
ALT2   gstack<->root SKILL.md verdict=unclear     sem=None    abstain=3 gates=1/3 | h1=0.0 dom=True pur=None trg=None tool=None head=0.2727 code=0.2881 cos=0.9164
NEG-A docx-vs-pdf  : verdict=diff-family expect=diff-family PASS
NEG-B cleared-vocab: verdict=unclear       expect=unclear       PASS
COURT docx=True gstack-capy=True -> court_ok=True
VERDICT_SUGGESTION_ALLOWED=true (court AND both negative controls)
[R316G2:LINEAGE] known-pass=true gstack_pairing=diff-family browse-alternative=unclear
```

与 r317 终裁引用的堂读数逐字一致（含「browse-alternative=unclear」本身）。

## 5. 三方案的增量证据（本件新增读数，不带倾向）

1. **维持归类（NOT_SAME_LINEAGE，不动 path）**
   - 支持面：capy 反例仍 diff-family（disproof=4/5）；browse 两维弃权原样复现（drift=0）⇒ 同族主张
     在 G2 口径下依旧进不了正门。
   - 新增读数：命令面入口件字面命中 54/118；matched-axes 3/6。
2. **改配 browse（必须同一次重建该对 pin）**
   - 新增硬证：allowed-tools **3/3 逐字同块**；$B 子命令 **15/15 逐字**；gen-marker parity=true、dominant family 同侧
     （browser_qa↔browser_qa, cos=0.9449）；D4 pur=0.8。
   - 硬约束（r317 已入规）：改 path 不重建 pin ⇒ compare_baseline 把改写本身读成 UPSTREAM_CHANGED。
   - **本件新发现（pin 必须重建的直接实证）**：侧卷卷尾锚点记「browse/SKILL.md v2.0.0，**34,225B，
     sha256(前16)=f297416a27daa4c8**（fetch 2026-10-20）」；而 2026-10-31 evidence 与 gh 现值为 **34,206B，
     sha256(前16)=f3d90cd3e7c41ce5，blob=e5792ca5** ⇒ 上游 browse 件在吸收之后**已经漂了**（-19B），
     侧卷自身锚点已过期。改配若不同次重建 pin，读到的漂移一半来自上游本体。
   - 仍缺：D5/D6 正门（本件逐条对账确认两维按原规则**必须**继续弃权，Aside 专有词 42 条在本地全无对应物）。
3. **no_upstream_anchor 先例（无直系上游）**
   - 新增读数：入口件=「browse headless $B 分支（15/15 逐字）+ 根套件建议块（Development workflow skill
     suggestions，r317 第三答案对=unclear）+ 本地吸收卷指针」的**重组**；browse v2 preamble 的 bin 族 8/9 缺失
     ⇒ 没有任何单一上游件等于它。G2 三选一在 as-is 尺下给不出 same-family ⇒ 与第 3 方案读向自洽。

## 6. 纪律自证（判据有牙）

- 词表/阈值/弃权规则零改动（脚本内 `thresholds_changed: 0`；轴复跑 drift=0 即「没动尺」的机器证明）。
- 负控内联在本件判据里：legB 清空词表 ⇒ unclear（防恒绿）；legA 同仓跨功能 ⇒ diff-family（防字面凑绿）。
- 堂没过时代码路径=verdict 强制 unclear 且 `return 1`（本件堂过、实跑 rc=0；rc=1 分支在源码在位，未声称已实测触发——
  防恒绿的实跑证据是 legA/legB 两条负控在本件内联都执行过：legB 清空词表⇒unclear、legA 同仓跨功能⇒diff-family）。
- gh api 是 404 不是网络断：原因是 repo 参数写成 owner 单段（repos/garrytan/contents/…），修正为
  garrytan/gstack 后 live=e5792ca5 对上钉。**教训入表：gh 路径参数必须 owner/repo 整串。**

## 7. 复跑

```python
# 判据命令（仓根 自建skill优化/ 下）
python -B _temp/r319b/check_r319b.py
# 期望末行
# [R319G4:BROWSE] court=pass verdict=unclear matched-axes=3/6

# 堂复跑（G2 原件，输出只落本件 ev/，不写 _repro）
python -B _repro/r316b_lineage/check_r316b.py --selftest --out _temp/r319b/ev/r316b_court_rerun.json
# 期望末行
# [R316G2:LINEAGE] known-pass=true gstack_pairing=diff-family browse-alternative=unclear
```

写面自查：本件只新建 `_temp/r319b/`（check_r319b.py / browse_check.json / report.md / ev/）。
受管根与 `_repro` 全程只读；联网仅 gh api 两次（browse SKILL.md 与 SKILL.md.tmpl 的 contents sha）。
