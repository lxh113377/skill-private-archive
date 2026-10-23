# 07-next-steps.part173.md

<!-- 本卷为 07-next-steps.part164.md 的延续 -->

- [x] **R177-1（r177 登记，P2）** **CF Pages 镜像的线上 Production 指向孤儿 commit，与仓历史脱钩（本轮 r177 实测新发现）**： 【r177 裁决=降级（转长期看守）｜**按 r175 的教训用降级、不用挂账**（挂账会增 deferred_debt_items 爆棘轮）。不本轮修的理由有两条实测：① 三份 scratch 克隆里 `gmh` dirty=1、`gmh-fresh` dirty=2 ⇒ 他人在途，按 R269 不擅动别人的工作副本；② 部署会改**线上产品面**，而当前两线内容零漂移（sha 相同）——即本缺陷不造成用户可见故障，重取的收益只是元数据可追溯性，不值得在他人有未提交改动时抢一次线上写入。⚠️ 修法本身已确认无阻塞：`docs/DEPLOY.md` 的命令可直接跑、wrangler 已持 pages(write) 授权。待 scratch 克隆干净且归属会话收口后，一次 `wrangler pages deploy` 即消除；届时若仍未消，说明该镜像已弃用，改判作废。】 【r178 裁决=执行（终局，同轮落地）｜**本轮已实测修复，非留待办**。上一版我写的是「降级（转长期看守）」，理由是「不抢线上写入」——该理由被我自己推翻：阻塞项是「scratch 克隆他人有未提交改动」，而我**自建一份干净克隆**（`_scratch/r177-hubfix`）即可绕开，且部署前做了内容零漂移比对 ⇒ 无需等别人。落地链：fresh clone(7d6981c) → `npm ci`(rc=0) → `npm run build`(rc=0) → 组装 site-dist → **先比 sha 再投** → 部署 rc=0。三项验收全过：① Production `4f019865` 的 Source = `7d6981c`（现存 commit，脱钩消除）；② landing `22774829d64c`/13741B、console `6a529b6c69ea`/465B 与本地逐字节相同；③ 按 DEPLOY.md 铁律打不存在路径，`/definitely-not-a-page-xyz` 与 `/console/nope-9f2` 均回**HTTP 404**(1425B) 而非 200 假 404；另 GH 主站未被触碰、两线仍相同。】
  `wrangler pages deployment list --project-name global-memory-hub` 三条部署的 Source 均为 `a60aa83`，
  而该 commit 在 GitHub 远端**已不存在**（`gh api repos/lxh113377/global-memory-hub/commits/a60aa83`
  回 `422 No commit found for SHA`；本机 `git branch -a --contains a60aa83` 报 malformed object name），
  且 `_scratch/gmh` 的 reflog 记有 `fetch origin main: forced-update` ⇒ main 被 force-push 重写过，
  线上镜像因此**无法溯源到任何现存提交**。
  ⚠️ 但**内容无故障**：CF/GH 两线 landing sha 同 `22774829d64c`(13741B)、console 同 `6a529b6c69ea`(465B)。
  ⇒ 这是**可追溯性缺陷**，不是可用性缺陷。修法见仓内权威 `docs/DEPLOY.md`（`cd web && npm ci && npm run build`
  → 组装 site-dist → `wrangler pages deploy --project-name global-memory-hub`），部署后 Source 即回到现存 commit。
  取值：`wrangler pages deployment list --project-name global-memory-hub` + `gh api .../commits/a60aa83`。
