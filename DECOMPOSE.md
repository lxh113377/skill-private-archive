# DECOMPOSE · r337（R331-2 兑现：NOASSERTION 正文级覆盖 20→22 仓全量收口 + candidate_health 口径升级）

> 起点 722d76b（tag r336）｜goal 第 18 回合 ⇒ 轮号 r337（`R337-*` 领号前核零命中）。**卡先落**。

## 起点实测（本轮现取）
- gh auth status ⇒ github.com 已登录（抓取通道可用）。
- `replacement_matrix.json` 里 license=NOASSERTION **去重 = 22 仓**（r331 报的「86 件」是候选行数，22 仓是抓取面 ⇒ 抓取量可控，r331 的四倍量估算按行数算的、偏保守）。
- `r262_license_body_pack.py` 已有 `build_pack()`（targets_union + gh api + classify_body 单源）。r331-2 卡点「20→86 四倍量」经现核修正为「union 面是否已覆盖这 22 仓」。

## 本轮分解（W=2 ⇒ N=2）
| # | 件 | 判据 |
|---|---|---|
| 1 | 现跑 build_pack（或其 targets 对账）⇒ 22 仓正文级归类全覆盖、缺口具名 | pack `repos` ⊇ 22 仓；每仓 state=OK 或具名 FAIL |
| 2 | candidate_health 消费正文面：restricted 里 NOASSERTION 按 body 归类改判，restricted 数随之更新（禁自造分类器，复用 r114 classify_body 单源） | `[R331:HEALTH]` 新读数 + 与 body pack 对账 |

## 30 秒卡 8 问
① 互不引用 ≥2 ⇒ 是（抓取面 vs 判据消费面）。② ≥3 回合 ⇒ 是。③ ≥2 独立面 ⇒ 是。④ 过。
⑤ 发 0 臂：臂八连全灭在案 + 件1→件2 严格串行（件2 输入=件1 产物）。
skip_reason：严格串行（件2 吃件1 的 pack 产物，接口无法预固定——缺口仓集合要跑了才知道）。
