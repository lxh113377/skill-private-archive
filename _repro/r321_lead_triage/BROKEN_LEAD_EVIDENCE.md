# r321 · Lead 侧断链取证（与臂 B 并行、口径独立，收口时对齐）

动因：r320 台账把 10 条都写成「真断链」，但同时又称其为「占位名」——两个措辞互相矛盾，
必须用一手证据裁掉一个。以下每条都是本轮实跑读数（受管根 HEAD=e8f489ebcf788f9b4f258ab96bb6c3cf465c5b25）。

## 1. story 九件：断链轴把**命名方案说明**当成了路径指针

`story-cover/SKILL.md:47`（版本史表格行，逐字）：

```
| V1.0.1 | 2026-10-06 | **体量治理分卷**：主文件 1439 B 超过 12 KB soft limit，按章节将细节迁至 `references/split-NN.md`，主文件只留章节路由与指针（渐进式披露）。正文语义未改，仅迁移位置。 |
```

同件树内实际存在（`git ls-tree -r --name-only HEAD -- story-cover/references/` 过滤 split）：

```
story-cover/references/split-01.md .. split-05.md   (count=5)
```

`story-review/SKILL.md:186` 同形态（版本史行 + 树内 split-01..05.md 齐全）。

⇒ 判定：`NN` 是「命名为 split-两位数字.md」的**方案占位符**，出现在变更日志的散文里，
  不是入口指针。扫描器把这类 token 送进断链轴 ⇒ **假阳性**。
  旁证：`git cat-file -e HEAD:story-cover/references/split-NN.md` 必 rc=128（占位符不是文件），
  而 r320 台账正是拿这条 rc=128 当「真断链」的证据 —— **该证据对占位符形态恒真、零判别力**。

## 2. html-ppt 一条：真断链（与上面不同类）

```
git cat-file -e HEAD:html-ppt/examples/my-talk/index.html  => rc=128
git ls-tree -r --name-only HEAD -- html-ppt/examples/       => html-ppt/examples/demo-deck/index.html（仅此一文件）
```

⇒ 入口写了一个具名实例目录 `my-talk/`，树里只有 `demo-deck/`。这条不是占位符形态
  （不含 NN/{}/<> 任何占位标记），是真·指向不存在文件的断链。

## 3. 修正后的口径（待与臂 B 对齐）

| 轴 | r320 报 | Lead 现证 | 说明 |
|---|---|---|---|
| broken | 10 | **真 1 / 占位符假阳 9** | 待臂 B 的 10 条逐条读数确认或推翻 |

修法（不得放宽判据，只把形态分流）：断链轴在解析 token 后加一道占位符过滤——
命中 `NN` / `{}` / `<>` / `*` / `XXX` 类命名方案标记的，单列 `PLACEHOLDER_MENTIONED` 计数、
不进 broken 分母；且**保留**「同一入口既写了占位符又没给出任何一个真实文件的可枚举规则」这一
告警（否则真缺文件的件会被一起放过）。反例（必须仍判红）：html-ppt 那条无占位标记 ⇒ 仍进 broken。

## 4. 对 r320 台账措辞的校正（按 R241 只加注不改写原文）

r320 条目 `R320-2` 写的「10 条真断链（story 九件的 `references/split-NN.md` 占位名 + html-ppt 示例路径，
全部 git cat-file -e 复验 rc=128）」——**复验方法本身没错，错在把 rc=128 解释为「真断链」**：
对占位符形态 rc=128 是必然结果，不构成缺陷证据。引用该条须带「broken 含 9 条占位符假阳（r321 现证）」这一限定。

