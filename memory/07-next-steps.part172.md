# 07-next-steps.part172.md

<!-- 本卷为 07-next-steps.part164.md 的延续 -->

- [x] **R178-1（r178 登记，P2）** **hub 仓权威 `docs/DEPLOY.md` 的 CF 投放命令在 wrangler 4.151.2 下失效（照抄必失败）**： 【r178 裁决=降级（转长期看守）｜**不用挂账**（r175 的教训：挂账增 deferred_debt_items 会爆棘轮）。本条是**跨仓文档缺陷登记**，不属本仓可自动完成项：① 文件在 `lxh113377/global-memory-hub` 仓，按 R269 不擅改他人仓；② 该仓 push main 会触发 `pages.yml` 自动重部署，副作用越出本仓面，不该由我单方发起。修法已写死可直接照用（`wrangler pages deploy <dir> --project-name X --commit-hash <sha> --branch main`）。⚠️ 同时本仓自保已确认无需改动：`chaoshi-web-deploy` 的 `wrangler pages deploy dist` 形态本来就对。】
  原文第 ④ 步 `cd site-dist && wrangler pages deploy --project-name global-memory-hub` 实测 **rc=1**：
  `Must specify a directory of assets to deploy. Please specify the [<directory>] argument ...`。
  同段第 ③ 步提示的 `--production-branch` 也**不是** `pages deploy` 的有效参数（实测回吐帮助），
  它属于 `pages project create`。⇒ 文档写的是旧版形态，wrangler 4.x 必须把目录作为**位置参数**传。
  可用形态（本轮实测 rc=0）：`wrangler pages deploy site-dist --project-name global-memory-hub --commit-hash <sha> --branch main`。
  ⚠️ 归属：`DEPLOY.md` 在 **`lxh113377/global-memory-hub`** 仓内（非本仓、非受管根），我不擅改他人仓；
  且 push 到该仓 main 会触发 `pages.yml` 自动重部署（副作用跨面），故只登记不动手。
  本仓侧可自保：`chaoshi-web-deploy` 用的是 `wrangler pages deploy dist --project-name=…`（**已传目录**），形态正确无需改。
  取值：`_scratch/r177-hubfix/_dep2.txt`（rc=1 原文）与 `_dep3.txt`（rc=0 成功）。
