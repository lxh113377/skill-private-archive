# 02 - 仓库结构

> 本文件记录项目目录结构。sync 命令会自动更新此文件。
> 归档类型：快照（整体复制到归档）

<!-- SYNC_AUTO_GENERATED_START -->
```
├── .github/
│   ├── workflows/
│   │   └── gates.yml
│   └── dependabot.yml
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
│   ├── _r97_patches/
│   │   ├── new1.txt
│   │   ├── new2.txt
│   │   ├── new3.txt
│   │   ├── old1.txt
│   │   ├── old2.txt
│   │   ├── old3.txt
│   │   ├── README.md
│   │   ├── tail4.txt
│   │   └── tail5.txt
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
│   ├── r63-patches/
│   │   ├── aask_hist_new.txt
│   │   ├── aask_hist_old.txt
│   │   ├── aask_new.txt
│   │   ├── aask_old.txt
│   │   ├── ah1_new.txt
│   │   ├── ah1_old.txt
│   │   ├── ah2_new.txt
│   │   ├── ah2_old.txt
│   │   ├── ah3_new.txt
│   │   ├── ah3_old.txt
│   │   ├── ca_new.txt
│   │   ├── ca_old.txt
│   │   └── patch_r63_desc.json
│   ├── r99-patches/
│   │   └── README.md
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
│   ├── r100_finalize.py
│   ├── r101_finalize.py
│   ├── r101_patch.py
│   ├── r101_patch2.py
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
│   ├── r52_md_claim_face_scan.py
│   ├── r52_mdclaim_fixtures.py
│   ├── r53_handles_fixtures.py
│   ├── r54_refresh_fixtures.py
│   ├── r55_note_fixtures.py
│   ├── r55_rootface_fixtures.py
│   ├── r56_artifact_face_fixtures.py
│   ├── r56_budget_fixtures.py
│   ├── r56_conflict_triage.py
│   ├── r56_inject_face_breakdown.py
│   ├── r56_workflow_face.py
│   ├── r58_action_pin_fixtures.py
│   ├── r58_action_pin_guard.py
│   ├── r58_generator_coverage.py
│   ├── r58_py_syntax_guard.py
│   ├── r58_supply_chain_face.py
│   ├── r58_todo_shell_slim.py
│   ├── r59_retired_face.py
│   ├── r59_supply_roots.py
│   ├── r60_capability_roster.py
│   ├── r60_capability_roster_describe.py
│   ├── r60_retire_two.py
│   ├── r60_roster_fixtures.py
│   ├── r60_upstream_backfill.py
│   ├── r61_semantic_coverage.py
│   ├── r62_用户预授权决策记录_2026-09-30.md
│   ├── r63_description_audit.py
│   ├── r66_generator_gate_fixtures.py
│   ├── r67_input_pin_fixtures.py
│   ├── r67_input_pin_guard.py
│   ├── r96_gh_raw.json
│   ├── r96_retire_mirror.py
│   ├── r96_run_stdout.txt
│   ├── r96_twelve_face.py
│   ├── r97_retire_full_egress.py
│   ├── r99_local_face_probe.py
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
│   ├── roster_evidence/
│   │   ├── descriptions/
│   │   │   ├── addyosmani__agent-skills__api-and-interface-design.json
│   │   │   ├── addyosmani__agent-skills__browser-testing-with-devtools.json
│   │   │   ├── addyosmani__agent-skills__ci-cd-and-automation.json
│   │   │   ├── addyosmani__agent-skills__code-review-and-quality.json
│   │   │   ├── addyosmani__agent-skills__code-simplification.json
│   │   │   ├── addyosmani__agent-skills__constraint-driven-development.json
│   │   │   ├── addyosmani__agent-skills__context-engineering.json
│   │   │   ├── addyosmani__agent-skills__debugging-and-error-recovery.json
│   │   │   ├── addyosmani__agent-skills__deprecation-and-migration.json
│   │   │   ├── addyosmani__agent-skills__documentation-and-adrs.json
│   │   │   ├── addyosmani__agent-skills__doubt-driven-development.json
│   │   │   ├── addyosmani__agent-skills__frontend-ui-engineering.json
│   │   │   ├── addyosmani__agent-skills__git-workflow-and-versioning.json
│   │   │   ├── addyosmani__agent-skills__idea-refine.json
│   │   │   ├── addyosmani__agent-skills__incremental-implementation.json
│   │   │   ├── addyosmani__agent-skills__interview-me.json
│   │   │   ├── addyosmani__agent-skills__observability-and-instrumentation.json
│   │   │   ├── addyosmani__agent-skills__performance-optimization.json
│   │   │   ├── addyosmani__agent-skills__planning-and-task-breakdown.json
│   │   │   ├── addyosmani__agent-skills__security-and-hardening.json
│   │   │   ├── addyosmani__agent-skills__shipping-and-launch.json
│   │   │   ├── addyosmani__agent-skills__source-driven-development.json
│   │   │   ├── addyosmani__agent-skills__spec-driven-development.json
│   │   │   ├── addyosmani__agent-skills__using-agent-skills.json
│   │   │   ├── anthropics__skills__academy-guide.json
│   │   │   ├── anthropics__skills__claude-api.json
│   │   │   ├── anthropics__skills__discernment-nudge.json
│   │   │   ├── anthropics__skills__template.json
│   │   │   ├── anthropics__skills__web-artifacts-builder.json
│   │   │   ├── ayghri__i-have-adhd__i-have-adhd.json
│   │   │   ├── code-yeongyu__oh-my-openagent__ast-grep.json
│   │   │   ├── code-yeongyu__oh-my-openagent__codex-qa.json
│   │   │   ├── code-yeongyu__oh-my-openagent__coding-agent-sessions.json
│   │   │   ├── code-yeongyu__oh-my-openagent__comment-checker.json
│   │   │   ├── code-yeongyu__oh-my-openagent__dag-library.json
│   │   │   ├── code-yeongyu__oh-my-openagent__data-scientist.json
│   │   │   ├── code-yeongyu__oh-my-openagent__debugging.json
│   │   │   ├── code-yeongyu__oh-my-openagent__dev-browser.json
│   │   │   ├── code-yeongyu__oh-my-openagent__frontend.json
│   │   │   ├── code-yeongyu__oh-my-openagent__get-unpublished-changes.json
│   │   │   ├── code-yeongyu__oh-my-openagent__git-master.json
│   │   │   ├── code-yeongyu__oh-my-openagent__github-triage.json
│   │   │   ├── code-yeongyu__oh-my-openagent__give-me-tips.json
│   │   │   ├── code-yeongyu__oh-my-openagent__hyperplan.json
│   │   │   ├── code-yeongyu__oh-my-openagent__init-deep.json
│   │   │   ├── code-yeongyu__oh-my-openagent__lcx-contribute-bug-fix.json
│   │   │   ├── code-yeongyu__oh-my-openagent__lcx-doctor.json
│   │   │   ├── code-yeongyu__oh-my-openagent__lcx-report-bug.json
│   │   │   ├── code-yeongyu__oh-my-openagent__lsp-setup.json
│   │   │   ├── code-yeongyu__oh-my-openagent__lsp.json
│   │   │   ├── code-yeongyu__oh-my-openagent__mass-ulw.json
│   │   │   ├── code-yeongyu__oh-my-openagent__omomomo.json
│   │   │   ├── code-yeongyu__oh-my-openagent__onboarding.json
│   │   │   ├── code-yeongyu__oh-my-openagent__opencode-qa.json
│   │   │   ├── code-yeongyu__oh-my-openagent__pre-publish-review.json
│   │   │   ├── code-yeongyu__oh-my-openagent__programming.json
│   │   │   ├── code-yeongyu__oh-my-openagent__publish.json
│   │   │   ├── code-yeongyu__oh-my-openagent__refactor.json
│   │   │   ├── code-yeongyu__oh-my-openagent__remove-ai-slops.json
│   │   │   ├── code-yeongyu__oh-my-openagent__remove-deadcode.json
│   │   │   ├── code-yeongyu__oh-my-openagent__review-work.json
│   │   │   ├── code-yeongyu__oh-my-openagent__rules.json
│   │   │   ├── code-yeongyu__oh-my-openagent__security-research.json
│   │   │   ├── code-yeongyu__oh-my-openagent__senpi-qa.json
│   │   │   ├── code-yeongyu__oh-my-openagent__skill.json
│   │   │   ├── code-yeongyu__oh-my-openagent__teammode.json
│   │   │   ├── code-yeongyu__oh-my-openagent__tech-debt-audit.json
│   │   │   ├── code-yeongyu__oh-my-openagent__ultimate-browsing.json
│   │   │   ├── code-yeongyu__oh-my-openagent__ultrawork.json
│   │   │   ├── code-yeongyu__oh-my-openagent__ulw-execute.json
│   │   │   ├── code-yeongyu__oh-my-openagent__ulw-loop.json
│   │   │   ├── code-yeongyu__oh-my-openagent__ulw-plan.json
│   │   │   ├── code-yeongyu__oh-my-openagent__ulw-research.json
│   │   │   ├── code-yeongyu__oh-my-openagent__visual-qa.json
│   │   │   ├── code-yeongyu__oh-my-openagent__work-with-pr.json
│   │   │   ├── ComposioHQ__awesome-claude-skills__artifacts-builder.json
│   │   │   ├── ComposioHQ__awesome-claude-skills__changelog-generator.json
│   │   │   ├── ComposioHQ__awesome-claude-skills__competitive-ads-extractor.json
│   │   │   ├── ComposioHQ__awesome-claude-skills__connect-apps.json
│   │   │   ├── ComposioHQ__awesome-claude-skills__connect.json
│   │   │   ├── ComposioHQ__awesome-claude-skills__content-research-writer.json
│   │   │   ├── ComposioHQ__awesome-claude-skills__developer-growth-analysis.json
│   │   │   ├── ComposioHQ__awesome-claude-skills__domain-name-brainstormer.json
│   │   │   ├── ComposioHQ__awesome-claude-skills__file-organizer.json
│   │   │   ├── ComposioHQ__awesome-claude-skills__image-enhancer.json
│   │   │   ├── ComposioHQ__awesome-claude-skills__invoice-organizer.json
│   │   │   ├── ComposioHQ__awesome-claude-skills__langsmith-fetch.json
│   │   │   ├── ComposioHQ__awesome-claude-skills__lead-research-assistant.json
│   │   │   ├── ComposioHQ__awesome-claude-skills__meeting-insights-analyzer.json
│   │   │   ├── ComposioHQ__awesome-claude-skills__pptx.json
│   │   │   ├── ComposioHQ__awesome-claude-skills__raffle-winner-picker.json
│   │   │   ├── ComposioHQ__awesome-claude-skills__skill-share.json
│   │   │   ├── ComposioHQ__awesome-claude-skills__slack-gif-creator.json
│   │   │   ├── ComposioHQ__awesome-claude-skills__tailored-resume-generator.json
│   │   │   ├── ComposioHQ__awesome-claude-skills__template-skill.json
│   │   │   ├── ComposioHQ__awesome-claude-skills__twitter-algorithm-optimizer.json
│   │   │   ├── ComposioHQ__awesome-claude-skills__video-downloader.json
│   │   │   ├── ComposioHQ__awesome-claude-skills__webapp-testing.json
│   │   │   ├── Egonex-AI__Understand-Anything__understand-chat.json
│   │   │   ├── Egonex-AI__Understand-Anything__understand-dashboard.json
│   │   │   ├── Egonex-AI__Understand-Anything__understand-diff.json
│   │   │   ├── Egonex-AI__Understand-Anything__understand-domain.json
│   │   │   ├── Egonex-AI__Understand-Anything__understand-explain.json
│   │   │   ├── Egonex-AI__Understand-Anything__understand-figma.json
│   │   │   ├── Egonex-AI__Understand-Anything__understand-knowledge.json
│   │   │   ├── Egonex-AI__Understand-Anything__understand-onboard.json
│   │   │   ├── Egonex-AI__Understand-Anything__understand.json
│   │   │   ├── Imbad0202__academic-research-skills__academic-paper-reviewer.json
│   │   │   ├── Imbad0202__academic-research-skills__academic-paper.json
│   │   │   ├── Imbad0202__academic-research-skills__academic-pipeline.json
│   │   │   ├── Leonxlnx__taste-skill__brandkit.json
│   │   │   ├── Leonxlnx__taste-skill__brutalist-skill.json
│   │   │   ├── Leonxlnx__taste-skill__gpt-tasteskill.json
│   │   │   ├── Leonxlnx__taste-skill__image-to-code-skill.json
│   │   │   ├── Leonxlnx__taste-skill__imagegen-frontend-mobile.json
│   │   │   ├── Leonxlnx__taste-skill__imagegen-frontend-web.json
│   │   │   ├── Leonxlnx__taste-skill__minimalist-skill.json
│   │   │   ├── Leonxlnx__taste-skill__output-skill.json
│   │   │   ├── Leonxlnx__taste-skill__redesign-skill.json
│   │   │   ├── Leonxlnx__taste-skill__soft-skill.json
│   │   │   ├── Leonxlnx__taste-skill__stitch-skill.json
│   │   │   ├── Leonxlnx__taste-skill__taste-skill-v1.json
│   │   │   ├── Leonxlnx__taste-skill__taste-skill.json
│   │   │   ├── mattpocock__skills__ask-matt.json
│   │   │   ├── mattpocock__skills__claude-handoff.json
│   │   │   ├── mattpocock__skills__codebase-design.json
│   │   │   ├── mattpocock__skills__diagnosing-bugs.json
│   │   │   ├── mattpocock__skills__domain-modeling.json
│   │   │   ├── mattpocock__skills__git-guardrails-claude-code.json
│   │   │   ├── mattpocock__skills__grill-with-docs.json
│   │   │   ├── mattpocock__skills__grilling.json
│   │   │   ├── mattpocock__skills__implement-spec.json
│   │   │   ├── mattpocock__skills__implement.json
│   │   │   ├── mattpocock__skills__improve-codebase-architecture.json
│   │   │   ├── mattpocock__skills__loop-me.json
│   │   │   ├── mattpocock__skills__migrate-to-shoehorn.json
│   │   │   ├── mattpocock__skills__pr.json
│   │   │   ├── mattpocock__skills__prototype.json
│   │   │   ├── mattpocock__skills__research.json
│   │   │   ├── mattpocock__skills__retro.json
│   │   │   ├── mattpocock__skills__scaffold-exercises.json
│   │   │   ├── mattpocock__skills__setup-matt-pocock-skills.json
│   │   │   ├── mattpocock__skills__setup-ts-deep-modules.json
│   │   │   ├── mattpocock__skills__teach.json
│   │   │   ├── mattpocock__skills__to-questionnaire.json
│   │   │   ├── mattpocock__skills__to-spec.json
│   │   │   ├── mattpocock__skills__to-tickets.json
│   │   │   ├── mattpocock__skills__triage.json
│   │   │   ├── mattpocock__skills__wait-what.json
│   │   │   ├── mattpocock__skills__wayfinder.json
│   │   │   ├── mattpocock__skills__wizard.json
│   │   │   ├── mattpocock__skills__writing-beats.json
│   │   │   ├── mattpocock__skills__writing-for-agents.json
│   │   │   ├── mattpocock__skills__writing-fragments.json
│   │   │   ├── mattpocock__skills__writing-shape.json
│   │   │   ├── multica-ai__andrej-karpathy-skills__karpathy-guidelines.json
│   │   │   ├── mvanhorn__last30days-skill__last30days.json
│   │   │   ├── nextlevelbuilder__ui-ux-pro-max-skill__banner-design.json
│   │   │   ├── nextlevelbuilder__ui-ux-pro-max-skill__brand.json
│   │   │   ├── nextlevelbuilder__ui-ux-pro-max-skill__design-system.json
│   │   │   ├── nextlevelbuilder__ui-ux-pro-max-skill__design.json
│   │   │   ├── nextlevelbuilder__ui-ux-pro-max-skill__ui-styling.json
│   │   │   ├── thedotmack__claude-mem__agent-cost-report.json
│   │   │   ├── thedotmack__claude-mem__babysit.json
│   │   │   ├── thedotmack__claude-mem__ccs-align.json
│   │   │   ├── thedotmack__claude-mem__cloud-sync.json
│   │   │   ├── thedotmack__claude-mem__design-is.json
│   │   │   ├── thedotmack__claude-mem__do.json
│   │   │   ├── thedotmack__claude-mem__host-observer.json
│   │   │   ├── thedotmack__claude-mem__how-it-works.json
│   │   │   ├── thedotmack__claude-mem__install.json
│   │   │   ├── thedotmack__claude-mem__knowledge-agent.json
│   │   │   ├── thedotmack__claude-mem__learn-codebase.json
│   │   │   ├── thedotmack__claude-mem__make-plan.json
│   │   │   ├── thedotmack__claude-mem__mem-search.json
│   │   │   ├── thedotmack__claude-mem__mem-setup.json
│   │   │   ├── thedotmack__claude-mem__mode-creator.json
│   │   │   ├── thedotmack__claude-mem__oh-my-issues.json
│   │   │   ├── thedotmack__claude-mem__openclaw.json
│   │   │   ├── thedotmack__claude-mem__pathfinder.json
│   │   │   ├── thedotmack__claude-mem__smart-explore.json
│   │   │   ├── thedotmack__claude-mem__standup.json
│   │   │   ├── thedotmack__claude-mem__timeline-report.json
│   │   │   ├── thedotmack__claude-mem__version-bump.json
│   │   │   ├── thedotmack__claude-mem__weekly-digests.json
│   │   │   ├── thedotmack__claude-mem__what-the.json
│   │   │   └── thedotmack__claude-mem__wowerpoint.json
│   │   ├── addyosmani__agent-skills.json
│   │   ├── anthropics__skills.json
│   │   ├── ayghri__i-have-adhd.json
│   │   ├── code-yeongyu__oh-my-openagent.json
│   │   ├── ComposioHQ__awesome-claude-skills.json
│   │   ├── Egonex-AI__Understand-Anything.json
│   │   ├── Imbad0202__academic-research-skills.json
│   │   ├── Leonxlnx__taste-skill.json
│   │   ├── mattpocock__skills.json
│   │   ├── multica-ai__andrej-karpathy-skills.json
│   │   ├── mvanhorn__last30days-skill.json
│   │   ├── nextlevelbuilder__ui-ux-pro-max-skill.json
│   │   ├── thedotmack__claude-mem.json
│   │   └── VoltAgent__awesome-openclaw-skills.json
│   ├── attention_sim_raw_2026-09-24.json
│   ├── baseline_contract_check_2026-09-24.json
│   ├── capability_gap_r60_2026-09-30.json
│   ├── capability_roster_r60_2026-09-30.json
│   ├── catalog_attention_tax_2026-09-24.json
│   ├── catalog_attention_tax_r20_2026-09-24.json
│   ├── catalog_attention_tax_r59_2026-09-29.json
│   ├── ci_health_r32_2026-09-25.json
│   ├── ci_surface_r31_2026-09-25.json
│   ├── claim_truth_2026-09-24.json
│   ├── cmd_resolvability_r36_2026-09-25.json
│   ├── comparison.md
│   ├── cron_tasks_backup_2026-09-24.json
│   ├── cron_tasks_backup_v2_full_2026-09-24.json
│   ├── cumulative_drift_2026-09-24.json
│   ├── cumulative_drift_r59_2026-09-29.json
│   ├── cumulative_drift_r59b_2026-09-29.json
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
│   ├── debt_aging_r52_2026-09-25.json
│   ├── debt_aging_r53_2026-09-25.json
│   ├── debt_aging_r54_2026-09-25.json
│   ├── debt_aging_r55_2026-09-25.json
│   ├── debt_aging_r56_2026-09-25.json
│   ├── debt_aging_r59_2026-09-29.json
│   ├── debt_aging_r59b_2026-09-29.json
│   ├── debt_aging_r59c_2026-09-29.json
│   ├── debt_aging_r59d_2026-09-29.json
│   ├── debt_aging_r59e_2026-09-29.json
│   ├── debt_aging_r59f_2026-09-29.json
│   ├── debt_runs.jsonl
│   ├── desc_baseline_r97.json
│   ├── desc_baseline_r98.json
│   ├── description双要素基线_2026-09-24.md
│   ├── description基线_2026-09-24.json
│   ├── evidence_resolvability_measure.json
│   ├── freshness_r32_2026-09-25.json
│   ├── gate_run_r100.json
│   ├── gate_run_r101.json
│   ├── gate_run_r101b.json
│   ├── gate_run_r31_2026-09-25.json
│   ├── gate_run_r32_2026-09-25.json
│   ├── gate_run_r32_portable_2026-09-25.json
│   ├── gate_run_r99.json
│   ├── gate_run_r99b.json
│   ├── gate_run_r99c.json
│   ├── gate_runs.jsonl
│   ├── gate_runs_r55_2026-09-25.json
│   ├── gate_runs_r56_2026-09-25.json
│   ├── generator_coverage_r58_2026-09-26.json
│   ├── inject_face_breakdown_r52_2026-09-25.json
│   ├── inject_face_breakdown_r56_2026-09-25.json
│   ├── inject_ratchet_baseline.json
│   ├── input_pins.jsonl
│   ├── md_claim_face_r52_2026-09-25.json
│   ├── md_claim_face_r55_2026-09-25.json
│   ├── md_claim_face_r56_2026-09-25.json
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
│   ├── r62_evidence_2026-09-30.json
│   ├── r63_description_dual_2026-09-30.json
│   ├── r63_description_dual_2026-10-01.json
│   ├── r63_evidence_2026-09-30.json
│   ├── r77_evidence_2026-10-01.json
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
│   ├── semantic_coverage_r61_2026-09-30.json
│   ├── skill_structure_rubric_2026-09-24.json
│   ├── skill_structure_rubric_r29_2026-09-24.json
│   ├── skill_structure_rubric_r53_2026-09-25.json
│   ├── supply_chain_face_r58_2026-09-26.json
│   ├── takeover_R76-3_M-1_evidence_2026-10-01.json
│   ├── takeover_R76-3_M-1_onwrite.txt
│   ├── transmit_proposals.json
│   ├── twelve_face_r100_2026-10-02.json
│   ├── twelve_face_r101_2026-10-02.json
│   ├── twelve_face_r96_2026-10-01.json
│   ├── twelve_face_r99_2026-10-02.json
│   ├── username_context_r35_2026-09-25.json
│   ├── verification_anchor_robustness_r29_2026-09-24.json
│   ├── verification_anchor_robustness_r29b_2026-09-24.json
│   ├── verification_robustness_r30_2026-09-25.json
│   ├── w27_conflict_triage_r51_2026-09-25.json
│   ├── w27_conflict_triage_r56_2026-09-25.json
│   ├── workflow_face_r56_2026-09-25.json
│   ├── 全量对标报告_r100_名册派生与两件换装_2026-10-02.md
│   ├── 全量对标报告_r101_名册优质半边与同事实单尺_2026-10-02.md
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
│   ├── 全量对标报告_r52_md引用面两路对账与契约陈旧自检_2026-09-25.md
│   ├── 全量对标报告_r53_名字不等于新鲜度与句柄化引用落地_2026-09-25.md
│   ├── 全量对标报告_r54_指标再生预算与对手节律声明实测_2026-09-25.md
│   ├── 全量对标报告_r55_同一判据两输入面根因收口与对手副本策略实测_2026-09-25.md
│   ├── 全量对标报告_r56_声明要被机器校验_预算入契约与裁定件配生成器_2026-09-25.md
│   ├── 全量对标报告_r58_动作固定面与判据自身三处假通过_2026-09-26.md
│   ├── 全量对标报告_r59_根迁移致判据读死面与退役未移出_2026-09-29.md
│   ├── 全量对标报告_r60_能力覆盖名册差集_2026-09-30.md
│   ├── 全量对标报告_r61_八维结构化_2026-09-30.md
│   ├── 全量对标报告_r62_八维结构化_2026-09-30.md
│   ├── 全量对标报告_r63_红门修复与描述全量审计_2026-09-30.md
│   ├── 全量对标报告_r64_M2首批收口与在途产物入库_2026-09-30.md
│   ├── 全量对标报告_r65_M2范围裁定与自建面达标_2026-09-30.md
│   ├── 全量对标报告_r66_W46b生成器面接线判红_2026-09-30.md
│   ├── 全量对标报告_r67_R58-1仓外输入固定面本地面_2026-09-30.md
│   ├── 全量对标报告_r68_pin台账增量落账与跨轮趋势_2026-09-30.md
│   ├── 全量对标报告_r69_pin清单热度排序与继承链_2026-10-01.md
│   ├── 全量对标报告_r70_新面孔优先与热度滑动窗口_2026-10-01.md
│   ├── 全量对标报告_r71_热度时间窗与新面孔配额_2026-10-01.md
│   ├── 全量对标报告_r72_逐字重复触发自审与三处缺陷_2026-10-01.md
│   ├── 全量对标报告_r73_坏行行号与继承截断标记_2026-10-01.md
│   ├── 全量对标报告_r74_next跨批语义分歧收口_2026-10-01.md
│   ├── 全量对标报告_r76_存量09回填与头模板一致性判据_2026-10-01.md
│   ├── 全量对标报告_r77_八维结构化_2026-10-01.md
│   ├── 全量对标报告_r97_全出口退役与判据假阴性修正_2026-10-01.md
│   ├── 全量对标报告_r99_十二维补面与覆盖根修_2026-10-02.md
│   ├── 技能六段解剖基线_2026-09-24.md
│   ├── 目录注意力税基线_2026-09-24.md
│   ├── 目录注意力税基线_r20_2026-09-24.md
│   ├── 累积漂移基线_2026-09-24.md
│   ├── 自建skill体系全量对标分析报告.md
│   └── 计数断言基线_2026-09-24.md
├── .aiexclude
├── AGENTS.md
├── README.md
└── TODO.md
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
