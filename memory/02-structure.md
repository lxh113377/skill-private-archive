# 02 - 仓库结构

> 本文件记录项目目录结构。sync 命令会自动更新此文件。
> 归档类型：快照（整体复制到归档）

<!-- SYNC_AUTO_GENERATED_START -->
```
├── .github/
│   └── workflows/
│       └── gates.yml
├── 00-scope/
│   ├── scope_result.json
│   ├── 注册表失真条目.md
│   └── 自建skill清单.md
├── 01-scan/
│   ├── attention_sim_20260922.txt
│   ├── content_snr_20260922.txt
│   ├── negative_tag_audit_20260922.txt
│   ├── README.md
│   ├── scan_all.py
│   ├── scan_report.md
│   └── scan_result.json
├── 02-review/
│   ├── A族_精读.md
│   ├── fenjue族_精读.md
│   ├── local族_精读.md
│   ├── skill审计族_精读.md
│   ├── story族_精读.md
│   └── 其他族_精读.md
├── 03-audit/
│   └── 自建skill优化审计报告.md
├── 04-plan/
│   ├── 剩余待办分类清单.md
│   ├── 实施计划.md
│   └── 工作流专项建议.md
├── 05-exec/
│   ├── B10-patches/
│   │   ├── patch_B10_build_registry.json
│   │   ├── patch_B10_legacy_domain.json
│   │   └── patch_B10_legacy_domain2.json
│   ├── B2-patches/
│   │   ├── ots.json
│   │   ├── ots2.json
│   │   └── wps.json
│   ├── B3-patches/
│   │   ├── patch_B3.json
│   │   ├── patch_B3b.json
│   │   ├── scorecard_after.json
│   │   └── scorecard_before.json
│   ├── B4-patches/
│   │   └── patch_B4.json
│   ├── B7-patches/
│   │   ├── patch_B7.json
│   │   └── patch_B7_m3.json
│   ├── D1-patches/
│   │   ├── d5_gap_note.txt
│   │   ├── p1.json
│   │   ├── p1_anchor.txt
│   │   ├── p1_inserted.txt
│   │   ├── p2_savepoint.json
│   │   ├── p3_projcmds.json
│   │   ├── p4_version.json
│   │   ├── p5_vh.json
│   │   ├── r3_footer.txt
│   │   └── README.md
│   ├── D4-patches/
│   │   ├── q1_handoff.json
│   │   ├── q2_audit.json
│   │   ├── q3_skillmd.json
│   │   ├── q4_disciplines.json
│   │   ├── q5_commands.json
│   │   └── q6_vh.json
│   ├── D5-patches/
│   │   ├── r1_skillmd.json
│   │   ├── r2_vh.json
│   │   └── r3_footer.txt
│   ├── mark_backup/
│   │   ├── 06-constraints.md.r51_163821.bak
│   │   ├── 07-next-steps.md.r46_144511.bak
│   │   ├── 07-next-steps.md.r46_144636.bak
│   │   ├── 07-next-steps.md.r47_150335.bak
│   │   ├── 07-next-steps.md.r47_150336.bak
│   │   ├── 07-next-steps.md.r47_150337.bak
│   │   ├── 07-next-steps.md.r47_150504.bak
│   │   ├── 07-next-steps.md.r48_151620.bak
│   │   ├── 07-next-steps.md.r49_153622.bak
│   │   ├── 07-next-steps.md.r49_154021.bak
│   │   ├── 07-next-steps.md.r49_154238.bak
│   │   ├── 07-next-steps.md.r49_154341.bak
│   │   ├── 07-next-steps.md.r49_register.bak
│   │   ├── 07-next-steps.md.r49_repair_154007.bak
│   │   ├── 07-next-steps.md.r50_161123.bak
│   │   ├── 07-next-steps.md.r51_163821.bak
│   │   └── 07-next-steps.md.r51_shrink.bak
│   ├── r19-patches/
│   │   ├── n1.txt
│   │   ├── n2.txt
│   │   ├── n3.txt
│   │   ├── o1.txt
│   │   ├── o2.txt
│   │   ├── o3.txt
│   │   ├── patch_contract.json
│   │   ├── patch_skillmd.json
│   │   └── patch_vhist.json
│   ├── R196-01-patches/
│   │   ├── patch-noise.json
│   │   ├── patch-savepoint.json
│   │   └── patch.json
│   ├── r20-patches/
│   │   ├── patch_agetmemory_applied.json
│   │   ├── patch_agetmemory_jig_clause.json
│   │   ├── patch_ruleeditor.json
│   │   ├── patch_skillmd2.json
│   │   ├── patch_vhist2.json
│   │   └── README_agetmemory_jig_clause.md
│   ├── r20b_fenjue_wiring/
│   │   └── README.md
│   ├── r21c-patches/
│   │   ├── patch_bump_skill.json
│   │   ├── patch_bump_vhist.json
│   │   └── patch_shrink.json
│   ├── r21e-patches/
│   │   ├── apply.txt
│   │   ├── dryrun.txt
│   │   ├── g2dry.txt
│   │   ├── g3.txt
│   │   ├── gate_apply.txt
│   │   ├── gate_apply2.txt
│   │   ├── gate_dry.txt
│   │   ├── gate_dry2.txt
│   │   ├── patch_gate.json
│   │   ├── patch_gate2.json
│   │   ├── patch_gate3.json
│   │   └── patch_nul.json
│   ├── R270-patches/
│   │   ├── q1_rule_editor.json
│   │   ├── q2_skillmd.json
│   │   └── q3_vh.json
│   ├── R271-patches/
│   │   ├── fix_truth_constants.json
│   │   ├── laoda_p0_to_p1.json
│   │   ├── laoda_substr_retry.json
│   │   ├── q_skillmd.json
│   │   ├── q_vh.json
│   │   └── repair_specs.json
│   ├── r29-patches/
│   │   ├── init_new.txt
│   │   ├── init_old.txt
│   │   ├── lc_new.txt
│   │   ├── lc_old.txt
│   │   ├── qv1_new.txt
│   │   ├── qv1_old.txt
│   │   ├── qv2_new.txt
│   │   ├── qv2_old.txt
│   │   ├── qv3_new.txt
│   │   └── qv3_old.txt
│   ├── r32-patches/
│   │   ├── new.txt
│   │   └── old.txt
│   ├── r37-patches/
│   │   ├── a_new.txt
│   │   ├── a_old.txt
│   │   ├── h_new.txt
│   │   ├── h_old.txt
│   │   ├── p1_new.txt
│   │   ├── p1_old.txt
│   │   ├── p2_new.txt
│   │   ├── p2_old.txt
│   │   ├── p3_new.txt
│   │   ├── p3_old.txt
│   │   ├── patch.json
│   │   ├── patch_am.json
│   │   ├── patch_hist.json
│   │   ├── patch_version.json
│   │   ├── u_new.txt
│   │   ├── u_old.txt
│   │   ├── v_new.txt
│   │   └── v_old.txt
│   ├── schemas/
│   │   └── r19/
│   │       └── baseline-contracts.json
│   ├── _lib.py
│   ├── apply_patches.py
│   ├── baseline_contract_scan.py
│   ├── catalog_attention_tax.py
│   ├── claim_truth_scan.py
│   ├── control_char_scan.py
│   ├── cumulative_drift_scan.py
│   ├── description_baseline_scan.py
│   ├── direct_map_dead_targets.json
│   ├── evidence_resolvability_measure.py
│   ├── memory_eval_run.py
│   ├── mimosa_fp_calibration_request_2026-09-24.md
│   ├── patch_r19_flow_legend_preserve.json
│   ├── plugin_skill_security_scan.py
│   ├── r19_baseline_contract_fixtures.py
│   ├── r19_endpoint_patchgen.py
│   ├── r19_feedback_append.py
│   ├── r19_fixture_mutation_check.py
│   ├── r19_flow_legend_stub.py
│   ├── r19_scan_fixtures.py
│   ├── r19b_footer_append.py
│   ├── r20_dirty_source_patchgen.py
│   ├── r20_dirty_source_stub.py
│   ├── r20_footer_append.py
│   ├── r20b_footer_append.py
│   ├── r20b_ratchet_fixtures.py
│   ├── r21c_fix_evidence.py
│   ├── r21c_footer_append.py
│   ├── r21c_shrink_skillmd_patchgen.py
│   ├── r21d_fix_own_entry.py
│   ├── r21d_footer_append.py
│   ├── r21d_lessons_land.py
│   ├── r21d_obsolete_fixtures.py
│   ├── r21d_rewrite_footer_script.py
│   ├── r21e_control_char_fixtures.py
│   ├── r21e_gate_patchgen.py
│   ├── r21e_gate_patchgen2.py
│   ├── r21e_gate_patchgen3.py
│   ├── r21e_gate_probe.py
│   ├── r21e_land2.py
│   ├── r21e_land3.py
│   ├── r21e_land4.py
│   ├── r21e_land_memory.py
│   ├── r21e_lesson51.py
│   ├── r21e_lesson52.py
│   ├── r21e_ratchet_attrib_fixtures.py
│   ├── R272b-boundary.json
│   ├── R272b-survey.json
│   ├── r29_rubric_calibre_fixtures.py
│   ├── r29_scope_filtered_queue.py
│   ├── r29_verification_anchor_robustness.py
│   ├── r29b_stage_07_line.py
│   ├── r30_section_robustness.py
│   ├── r31_ci_surface.py
│   ├── r31_landing_rationalizations.py
│   ├── r31_run_gates_fixtures.py
│   ├── r32_ci_health.py
│   ├── r32_freshness_fixtures.py
│   ├── r32_gate_freshness.py
│   ├── r33_release_governance.py
│   ├── r34_onwrite_fixtures.py
│   ├── r34_portability_surface.py
│   ├── r35_landing_username.py
│   ├── r35_tracked_empty.py
│   ├── r35_tracked_empty_fixtures.py
│   ├── r35_username_context_audit.py
│   ├── r36_cmd_resolvability.py
│   ├── r37_noise_tracked_stub.py
│   ├── r38_debt_aging.py
│   ├── r39_debt_ledger_fixtures.py
│   ├── r40_scan_inputs_fixtures.py
│   ├── r46_mark_verdict.py
│   ├── r46_mark_verdict_fixtures.py
│   ├── r49_face_fixtures.py
│   ├── r50_face_fixtures.py
│   ├── r51_retrieval_fixtures.py
│   ├── ratchet_gate.py
│   ├── README.md
│   ├── recycle_selftest.py
│   ├── repair_lines.py
│   ├── replay_own_lines_to_index.py
│   ├── rubric_ab_compare.py
│   ├── rule_conflict_scan.py
│   ├── run_gates.py
│   ├── selective_stage_by_marker.py
│   ├── skill_structure_rubric_scan.py
│   ├── transmit_obsolescence_check.py
│   ├── user_created_audit.json
│   ├── user_created_audit.py
│   ├── 性能瓶颈分析与优化方案.md
│   ├── 第10轮执行报告.md
│   ├── 第2轮执行报告.md
│   ├── 第3轮执行报告.md
│   └── 第9批_A-project-better-V1.3.0.md
├── 06-benchmark/
│   ├── ci_evidence/
│   │   ├── aas_ci.yml
│   │   ├── aas_repo-hygiene.yml
│   │   ├── aas_skill-review.yml
│   │   ├── addyosmani_test-plugin-install.yml
│   │   ├── mycelium_behavioral-install-eval.yml
│   │   ├── mycelium_personal-pii-scrub.yml
│   │   ├── mycelium_release-drift-heartbeat.yml
│   │   ├── mycelium_template-purity.yml
│   │   └── README.md
│   ├── attention_sim_raw_2026-09-24.json
│   ├── baseline_contract_check_2026-09-24.json
│   ├── catalog_attention_tax_2026-09-24.json
│   ├── catalog_attention_tax_r20_2026-09-24.json
│   ├── ci_health_r32_2026-09-25.json
│   ├── ci_surface_r31_2026-09-25.json
│   ├── claim_truth_2026-09-24.json
│   ├── cmd_resolvability_r36_2026-09-25.json
│   ├── comparison.md
│   ├── cron_tasks_backup_2026-09-24.json
│   ├── cron_tasks_backup_v2_full_2026-09-24.json
│   ├── cumulative_drift_2026-09-24.json
│   ├── debt_aging_r38_2026-09-25.json
│   ├── debt_aging_r39_2026-09-25.json
│   ├── debt_aging_r40_2026-09-25.json
│   ├── debt_aging_r41_2026-09-25.json
│   ├── debt_aging_r43_2026-09-25.json
│   ├── debt_aging_r44_2026-09-25.json
│   ├── debt_aging_r45_2026-09-25.json
│   ├── debt_aging_r46_2026-09-25.json
│   ├── debt_aging_r47_2026-09-25.json
│   ├── debt_aging_r48_2026-09-25.json
│   ├── debt_aging_r49_2026-09-25.json
│   ├── debt_aging_r50_2026-09-25.json
│   ├── debt_aging_r51_2026-09-25.json
│   ├── debt_runs.jsonl
│   ├── description双要素基线_2026-09-24.md
│   ├── description基线_2026-09-24.json
│   ├── evidence_resolvability_measure.json
│   ├── freshness_r32_2026-09-25.json
│   ├── gate_run_r31_2026-09-25.json
│   ├── gate_run_r32_2026-09-25.json
│   ├── gate_run_r32_portable_2026-09-25.json
│   ├── gate_runs.jsonl
│   ├── inject_ratchet_baseline.json
│   ├── memory_eval_scenarios_v1.json
│   ├── memory_eval基线_2026-09-24.md
│   ├── noise_falsepositive_r37_2026-09-25.json
│   ├── opponents_open_backlog_r51_2026-09-25.json
│   ├── opponents_workflow_face_r50_2026-09-25.json
│   ├── P0-1_hook机制层探底_2026-09-24.md
│   ├── P0-C_累积漂移复核第1批_2026-09-24.md
│   ├── P0-C_累积漂移复核第2批_2026-09-24.md
│   ├── plugin_skill_security_2026-09-24.json
│   ├── portability_r34_2026-09-25.json
│   ├── r31_section_robustness_2026-09-25.json
│   ├── r31_section_robustness_after_2026-09-25.json
│   ├── rationalizations_robustness_r30_2026-09-25.json
│   ├── rationalizations_robustness_r30b_2026-09-25.json
│   ├── release_governance_r33_2026-09-25.json
│   ├── rubric_ab_2026-09-24.json
│   ├── rubric_ab_r29_2026-09-24.json
│   ├── rule_conflict_scan_2026-09-24.json
│   ├── rule_conflict_scan_r40_2026-09-25.json
│   ├── rule_conflict_scan_r50_2026-09-25.json
│   ├── rule_conflict_scan_r51_2026-09-25.json
│   ├── rule_conflict基线_2026-09-24.md
│   ├── scope_filtered_queue_r29_2026-09-24.json
│   ├── skill_structure_rubric_2026-09-24.json
│   ├── skill_structure_rubric_r29_2026-09-24.json
│   ├── transmit_proposals.json
│   ├── username_context_r35_2026-09-25.json
│   ├── verification_anchor_robustness_r29_2026-09-24.json
│   ├── verification_anchor_robustness_r29b_2026-09-24.json
│   ├── verification_robustness_r30_2026-09-25.json
│   ├── w27_conflict_triage_r51_2026-09-25.json
│   ├── 全量对标报告_r18_2026-09-24.md
│   ├── 全量对标报告_r19_2026-09-24.md
│   ├── 全量对标报告_r20_插件面补口径_2026-09-24.md
│   ├── 全量对标报告_r21_重复轮次闸门_2026-09-24.md
│   ├── 全量对标报告_r27_2026-09-24.md
│   ├── 全量对标报告_r28_六段解剖AB_2026-09-24.md
│   ├── 全量对标报告_r29_双口径与范围过滤_2026-09-24.md
│   ├── 全量对标报告_r30_四档稳健性与反理性化首批_2026-09-25.md
│   ├── 全量对标报告_r31_自动化验收面_2026-09-25.md
│   ├── 全量对标报告_r32_CI有效性_2026-09-25.md
│   ├── 全量对标报告_r33_发布与治理面_2026-09-25.md
│   ├── 全量对标报告_r34_可移植性_2026-09-25.md
│   ├── 全量对标报告_r35_可移植性纵深_2026-09-25.md
│   ├── 全量对标报告_r36_引用可解析性_2026-09-25.md
│   ├── 全量对标报告_r37_门禁假阳性治理_2026-09-25.md
│   ├── 全量对标报告_r38_债务到期治理_2026-09-25.md
│   ├── 全量对标报告_r39_延期与终局分离_2026-09-25.md
│   ├── 全量对标报告_r40_延期看守与归属反转_2026-09-25.md
│   ├── 全量对标报告_r41_裁决时间序与结构归位_2026-09-25.md
│   ├── 全量对标报告_r42_反弹根因与延期treadmill_2026-09-25.md
│   ├── 全量对标报告_r43_反延期treadmill与分档宽限_2026-09-25.md
│   ├── 全量对标报告_r44_裁决完整性落地_2026-09-25.md
│   ├── 全量对标报告_r45_反降级免检与标记错位真因_2026-09-25.md
│   ├── 全量对标报告_r46_标记写入唯一入口_2026-09-25.md
│   ├── 全量对标报告_r47_无法定年盲区清零_2026-09-25.md
│   ├── 全量对标报告_r48_契约分代与归属可机检_2026-09-25.md
│   ├── 全量对标报告_r49_判据输入面五面自证与三处劫持根因修_2026-09-25.md
│   ├── 全量对标报告_r50_权威源扫描扩面与对手枚举面复核_2026-09-25.md
│   ├── 全量对标报告_r51_取数面两路对账与判据接线自失效_2026-09-25.md
│   ├── 技能六段解剖基线_2026-09-24.md
│   ├── 目录注意力税基线_2026-09-24.md
│   ├── 目录注意力税基线_r20_2026-09-24.md
│   ├── 累积漂移基线_2026-09-24.md
│   ├── 自建skill体系全量对标分析报告.md
│   └── 计数断言基线_2026-09-24.md
├── .aiexclude
├── AGENTS.md
├── README.md
├── TODO.md
└── 手动维护。agent
```
<!-- SYNC_AUTO_GENERATED_END -->

## 模块说明
<!-- 手动补充（2026-09-22 实测回填；本工作区无 src/ 与 tests/，目录按六阶段对齐） -->
- `00-scope/` — 阶段0 范围裁定：自建清单 + 注册表失真条目 + 原始打分数（`scope_result.json`）
- `01-scan/` — 阶段1 四维机器扫描：报告 + 结果 JSON + 重叠原始件 + **唯一可复跑脚本 `scan_all.py`**
- `02-review/` — 阶段2 全量精读：6 份族审计卡（A族 / fenjue / 审计族 / local / story / 其他）
- `03-audit/` — 阶段3 审计报告：四维结论 + P0/P1/P2 分级
- `04-plan/` — 阶段4 实施计划与阶段5 专项建议（含验证命令 + 回滚手段）
- `05-exec/` — 阶段4/5 **执行证据**：`README.md`（补丁索引）+ 2 份轮次报告 + 19 个 patch JSON
- `memory/` — handoff 8 文件 + 分卷 + `AGENTS.md`（P-1 绑定表）+ `archive/`（安全网，**当前为空**）
- `.codebuddy/` — 平台元数据（plans / 记忆），已在 `.gitignore` 内，不入库
