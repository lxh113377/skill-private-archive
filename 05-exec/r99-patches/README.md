# r99 备好未落码的补丁（受管根在途 97 条，按 R269/铁律 4-5 不代改）

## P-1 A-skill-manager：准入与差集类判据必须先枚举「全部供给根」

**五问命中：** 缺失步骤（`governance.md §新增准入` / `§可移植性` 只约束单根可移植性，未要求差集判据声明覆盖根）。

**一手证据（本轮实测）：**
`05-exec/r96_twelve_face.py` 本地面原先只扫 `D:/global_skills`（171 一级技能），
把 `obra/superpowers` 的 `using-git-worktrees`、`dispatching-parallel-agents` 判成「对手独有、本地缺」；
实测二者在 `C:/Users/37533/.qoder-cn/plugins/cache/qoder-marketplace/superpowers/6.3.0/skills/` 已装着。
补根后（`installed_plugins_v2.json` 的 installPath 逐条 + realpath 去重，18 根）：superpowers 独有差集 **10 → 1**，
d1 并集 316（权威源一级 169 / 权威源全深度 221），插件根贡献 95 件 SKILL.md。
取值：`python 05-exec/r96_twelve_face.py --json 06-benchmark/twelve_face_r99_2026-10-02.json` 读 `local.coverage_roots`。

**要落的条文（建议，宿主确认后由归属会话改）：**

> 任何「本地 vs 对手」「差集」「覆盖率」类判据，动手前必须先枚举**本机全部技能供给根**
> （权威源树 + 镜像面 + 市场缓存根 + **平台插件根**），并在产物里逐根各出一行 `coverage_roots`
> （path/role/实到数）。分母必须满足不变式 `各根之和 == 去重后 + 跨根重复`；
> 去重按 `os.path.realpath`，禁按 `role:basename` 拼键（同名根互相覆盖会静默丢面）。
> 未声明覆盖根的差集结论一律判 `UNVERIFIED`，不得据此下「本地缺 X」或「换装 Y」。

**为什么与既有规则不重复：** `R20-2` 只管「预算/上限类门禁须自证覆盖根」，本轮是**差集类判据**这一半；
`r59_supply_roots.py` 量的是四根**计数**（权威/镜像/QD junction/市场缓存），不含插件根，且它不是判据而是报告件。

**验收判据（落地后须两侧都过）：**
1. 正例：`python 05-exec/r96_twelve_face.py --selftest` 见 `插件根被枚举且实到>0` + `各根之和==去重后+跨根重复` 两行 PASS。
2. 反例：临时把 `PLUGIN_INDEX` 指到不存在路径 → `coverage_root_notes` 必须显形 `plugin_index_missing:*`，
   且 `cross_root_duplicates` 腿仍绿（不得静默退化为单根口径却照打 matched）。

**回滚锚：** 本仓 `05-exec/r96_twelve_face.py`（已在 HEAD），受管根零改动。

## P-2 A-memory-start：`dag_precheck --require-mark` 与首个写盘同链

本轮**第一个写盘动作**（`05-exec/r99_local_face_probe.py`）未与 precheck 同链，属 V10.79.0 第二十六次同族破口，
已在 GM 当日日志 G8 块内自登记（`本次标识: 轮99`）。
链化需要改的是**门禁自身的形态**（把「要求先跑」变成「写盘动作本身带上游校验」），
按 r25 既定口径「没量过误报率的闸门不得拦任务」，未量前不擅改 ⇒ 本轮只登记，不虚报已闭环。
