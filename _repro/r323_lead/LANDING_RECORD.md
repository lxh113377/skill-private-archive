# r323 landing 记录 · frontend-skill references 目录级取用规则（R289-5 八步留痕）

## 步骤逐条（每步都有实测读数）

| 步 | 内容 | 读数 |
|---|---|---|
| ① 坐标现读自判据 | 从 r322 v2 普查件取「可落盘目标」：5 个 CLEAN 件中只有 frontend-skill(1 条) 与 agent-browser(1 条) 是单件真孤儿 | `_repro/r322b/census_v2_top.json` per_skill |
| ② 许可门 | 无新增上游素材（只改本地入口正文）；本件上游 = Leonxlnx/taste-skill（MIT，见 `.upstream`） | 仅正文写入，无素材入库 |
| ③ old 逐字切片 + 现计数 | `## Version history` 在盘上 `count == 1`（`frontend-skill_old.txt` 18 字节） | `old_count = 1`（Python 现算） |
| ④ dry-run 全绿再写盘 | `rule_editor replace --dry-run` ⇒ 命中行 252、1 处全部可应用 | `rc=0`，`✅ 共 1 处全部可应用；未写盘未备份` |
| ⑤ 改后全文复读 | 新节 L252-264 在盘；Version history 仍在（出现次数 1）；版本三处一致（`version: 1.1.1` / `last_updated: 2026-11-01` / 版本史首条 1.1.1） | 逐行现读 |
| ⑥ 提交范围核验 + 回滚双前提 | `git show --stat HEAD` ⇒ 恰 1 件；`.bak` 存在；`git cat-file -e HEAD^:frontend-skill/SKILL.md` 通过 | `1 file changed, 16 insertions(+), 2 deletions(-)` |
| ⑦ 落地后判据仍可从仓内复算 | 复跑 v2 普查 ⇒ frontend-skill orphans `1 → 0`，全库 `624 → 623`，prose `552 → 551`，守恒 551+72=623 | `[V2:CENSUS] closure=top ... orphans_top=623 ... orphans_prose=551 noise=72` |
| ⑧ 素材与中间输出不入库 | 补丁 old/new 文本与日志落 `_repro/r323_lead/`（证据件）；`work/` 子目录被 `.gitignore:101` 命中 | 见提交清单 |

## 落地读数汇总（全部现取）

```
受管根 HEAD          feaeac98c0dd（本笔）
本笔改动             frontend-skill/SKILL.md  +16 −2（1 件）
孤儿效应             frontend-skill 1 → 0；全库 624 → 623（守恒 551 prose + 72 noise）
镜像                 [GATE:mirror-pass] missing=0 mismatch=0（补 1 件，他人零卷入；extra=98 为历史遗留警告级）
回滚                 .bak = D:/global_memory_archive/_trash/rule_backup/frontend-skill.SKILL.md.20261101_004232_763887.bak
                     git -C D:/global_skills revert feaeac98c0dd 亦可（HEAD^ 存在）
```

## 为什么本轮只落 1 件（不是漏做）

5 个 CLEAN 件里：
- `gstack`（6 孤儿）：5/6 由嵌套入口逐字引用、第 6 条被 8 处提到 ⇒ 补链零收益（r322 裁决）；
- `theme-factory`（10 孤儿）与 `ui-ux-pro-max`（2 孤儿）：全部是由入口已给出的目录级规则覆盖 ⇒ 逐条挂链是重复（r322 §7.1）；
- `agent-browser`（1 孤儿 = `references/commands.md`，293 行完整命令参考）：该件是 **3.0.0 薄壳**，L20-26 明写「完整命令/参数权威 = 上游随版指南 `skills get core --full`」；`commands.md` 最后改动 = 2026-09-21 建基线（早于薄壳化 10-20），且全受管根**零引用** ⇒ 它是**薄壳化残留的厚镜像件**，补链会重新引入漂移风险；正确处置是**剪枝**（删除或移入 `_trash`），但删件属破坏性动作、须双前提与评审，本轮**只登记不执行**（见台账 R323-2）。
- `frontend-skill`（1 孤儿）：唯一真该补的 ⇒ 本轮落它。
