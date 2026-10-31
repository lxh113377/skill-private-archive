# r325a · 两份 landing spec（R324-2 兑现）

> 判据：`python -B _repro/r325a/check_r325a.py` ⇒ `[R325A:SPEC] specs=2 legs=10 unverified=4 teeth=pass`

## 1. 关键发现：`managed` 只是给 `git -C` 用的路径，**没有硬编码受管根检查**

读 `05-exec/landing_replay_check.py` 实现（逐行现核）：
- `:92 / :97 / :100 / :133 / :148 / :151 / :189 / :218 / :306 / :311` 全部是 `git(spec["managed"], [...])` 形态；
- 全文**没有**「managed 必须是 D:/global_skills」或等价断言（我 grep `global_skills` 只命中注释与文档串）。

⇒ 两份 spec 的 `managed` 指向**本项目仓**是合法的。这是本轮把「本仓工具件」纳入复算面的前提 —— 若不成立，
两份 spec 只能写降级件（结构不可达），价值大减。

## 2. 两份 spec 与逐腿读数

| spec | R 重放 | N 新增件 | P 指针 | V 版本 | M 镜像 | gate | rc |
|---|---|---|---|---|---|---|---|
| `r324_entry_reachability.json` | ok | **UNVERIFIED** | ok | **UNVERIFIED** | ok | UNVERIFIED | 2 |
| `r323a_gl1_targets.json` | ok | **UNVERIFIED** | ok | **UNVERIFIED** | ok | UNVERIFIED | 2 |

### 2.1 为什么 N 与 V 两条腿是 UNVERIFIED（都**结构化**，不是缺口）

| 腿 | 原因（file:line 依据） |
|---|---|
| **N**（新增件等值） | `landing_replay_check.py:166-174`：`want is None` 时会走「无等值锚点」分支 —— 要么给 `upstream.repo/path`（gh api 现取）、要么给 `expected_sha`（spec 存档）。两份 spec 的目标件都是**本仓自造件**（无上游同名文件），两者都给不出；给 `expected_sha` 等于把「我当下盘上这一版」钉成期望值 = 自我指证（r287 注入幽灵同族）⇒ **如实 UNVERIFIED**。 |
| **V**（版本） | `:211-213`：`spec.get("version")` 为空即 `UNVERIFIED ["spec 未给 version 期望"]`。本仓工具件（`05-exec/*.py`）**没有 frontmatter 版本行**（那是受管根 SKILL.md 的形态）⇒ 结构化不适用。 |

⇒ 这两条腿的 UNVERIFIED 是**判据正确地拒绝把「无法证明」读成「通过」**（R247）。若为了变绿去填 expected_sha 或编造 version 行，就是 r260 那类假绿。

## 3. 两份 spec 到底是什么（一句话各）

- `r324_entry_reachability.json`：给 r324 常驻的入口可达面判据一份复算入口。当前它证明的是「R/P/M 三腿可跑且干净」，N/V 结构化不可判 —— **这本身就把「常驻判据尚无完整复算面」这个事实显影了**。
- `r323a_gl1_targets.json`：给 G-L1 目标件门（**仍在 `_repro/r323a/`**）一份 spec。`bare_tokens` 含 `_repro/` ⇒ 若该件被任何入口引用，P 腿会当场显形。这件的存在意义 = **把「尚未常驻」的缺口钉成读数**，而不是假装它已常驻。

## 4. 部分实现（R324-2 的验收靶）

| 靶 | 状态 |
|---|---|
| 两份 spec 落盘且可被判据解析 | ✅ |
| `landing_replay_check.py --spec` 真跑并记录五腿 | ✅（两 spec 各一行 LANDING-CHECK，rc=2） |
| 未可达的腿如实标 UNVERIFIED 且具名原因 | ✅（N/V 两条，原因见 §2.1） |
| 全部腿 PASS | ❌ **结构性不可达**（本仓件无上游锚、无版本行）⇒ 附三 §3 第 3 条应改写 |

⚠️ 由此产生一条**规范修订建议**（不是本轮能做，登记）：附三 §3 第 3 条「须在 landing_specs 给一份 spec，使五腿全绿」这个验收口径**对「本仓工具件」不成立** ——
本仓工具件天然缺版本行与上游锚。正确写法应是「给一份 spec 且**每腿要么 PASS 要么有具名 UNVERIFIED 原因**」，
即把「全绿」改成「不许有沉默的腿」。这条修订已登记 R325-3。

## 5. 自证与负控

三条负控：`R325A_NEG=bare`（清空 bare_tokens ⇒ check 必须红）、`ghost`（new_files 指向不存在路径 ⇒ 判据 rc=2 UNVERIFIED）、`handedited`（该 spec 结构性 rc=2 而非假绿）。
