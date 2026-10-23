# 07-next-steps.part171.md

<!-- 本卷为 07-next-steps.part164.md 的延续 -->

- [x] **R182-1（r182 登记，P2）** **hub 的 CF 镜像自动同步卡在外部凭据（CF API token）—— workflow 已落、只缺 secret**： 【r182 裁决=降级（转长期看守）｜**按 r175 教训用降级、不用挂账**（挂账增 DEFERRED 会爆棘轮）。这是**外部凭据缺口**（#29 明确允许报告的两类之一），非本机可自动化项：实测三条堵死了所有免凭据通路（hub secrets=0、无 org、登录态 403 code 9109 不能铸 token）。⚠️ 本条的「待办」只剩一步人工，且**我做完了所有能做的前置**：workflow 已入库并验证为惰性成功（run 39908415458），凭据到位即自动生效。到期判据 = hub 的 CF Production 的 commit 跟着最新 push 走（含 workflow 文件的那次 push 之后，若 token 已配，Source 应变为该次 sha）。】
  已落地（可复算）：`.github/workflows/cf-mirror.yml` 推入 `lxh113377/global-memory-hub`（commit `03acb8d`），
  实测 run `39908415458` **success**：告警步 success + 部署链 5 步 **skipped** ⇒ 无 token 时惰性且显式，
  凭据一到位即自动生效、无需改文件。两条铁律已内置：Source 锚到 `github.sha`（修 r178 孤儿根因）、
  部署后打不存在路径验真 404（DEPLOY.md ⑤）。
  ⚠️ **卡点 = 外部凭据缺口**（#29 允许报告的两类之一），三条实测：
    ① hub 仓 `gh api repos/.../actions/secrets` **total = 0**（对照 supermarket-web 有 `CLOUDFLARE_API_TOKEN`，updated 2026-08-27）；
    ② **无 org**（`gh api user/orgs` 空）⇒ 无 org 级 secret 共享路径；
    ③ 现有 wrangler 登录态**无权铸 token**：`GET /user/tokens` 与 `/user/tokens/permission_groups` 均 **403 code 9109**。
  ⇒ 需要外部动作：在 CF Dashboard 建 API token（账号 Pages:Edit）→ 配成 hub 仓的 `CLOUDFLARE_API_TOKEN` secret。
  同模式先例已在其自有仓验证：`supermarket-web/.github/workflows/ci.yml` L453-490。
  取值：`gh api repos/lxh113377/global-memory-hub/actions/secrets --jq .total_count`。

- [x] **R170-1（r170 登记，P2，到期 r172）** **账龄尺 OVERDUE 4 条全部属并行会话的 r166 系列，非我的在途（只登记不代裁）**。 【r170 裁决=降级（转长期看守）｜本条不是待办而是**归属登记**：4 条 OVERDUE 全是并行会话 r166 系列（记忆卷体量治理一族），按 R269 不擅动、不代裁。转长期看守的理由 = 它们的处置需要并行会话自己按「人工按段落边界拆卷」执行，我代做会与其写盘竞态（本仓已有此类教训：并行拆卷期间我跑门禁被 317 个未提交件干扰）。到期后若仍在，只需复算一次归属是否变化，不必动手。】
