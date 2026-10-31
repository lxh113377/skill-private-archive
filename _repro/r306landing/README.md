# r306 首件换装落地证据包（A-prompt-better）

受管根两笔提交（git -C D:/global_skills log --oneline -2 现取）：
- 17cc0c81：转述并入（1.3.0→1.4.0，四区增量中文化 + 检查清单 +2 + 版本三连）
- f39eb3c0：逐字钉定升级（1.4.0→1.5.0，A1 六条编辑；每条增量带 upstream_blob_sha 742deafa… 定位器注释）

演算等价性：upgrade_expected_after.txt 的 sha256 前缀 == 落地后活体文件 sha 前缀（fac939d845fa，我实测逐字节）。
pre_state.txt = 任何改动之前（sha 前缀 01884cd1 / 675 行 / 1.3.0）；post_state_round1.txt = 第一笔后（de986705 / 685 行 / 1.4.0）。

校验面（全部现跑）：r36 [RESOLVE:OK] ｜棘轮 [RATCHET:PASS] ｜镜像 [GATE:mirror-pass]（.agents SAME）｜
rule_editor gates：global_skills violation=0（仅 C16/C29-C30 两条既有红）｜A1 判据对活体 GATE=PASS（increments 4/4、local_only 2/2）。

注册表滞后：我这次 bump 曾把本件推进滞后名单（16→我修→15）；同步走带备份的机械脚本（先例 d22437b，生产者无版本同步路径），
只同步本会话这一条；其余 15 条属他会话，未碰。

回滚：受管根 git revert 17cc0c81 f39eb3c0（两笔都在主线，ANCESTOR 检查过）；或逐笔 checkout 改前 sha。
