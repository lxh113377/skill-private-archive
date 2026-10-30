import url from 'node:url';
import fs from "node:fs";
import path from "node:path";
const ROOT = path.resolve(path.dirname(url.fileURLToPath(import.meta.url)), '..', '..');
const T = ROOT + "/_repro/r285l";
const BENCH = ROOT + "/06-benchmark";
const NL = String.fromCharCode(10);
const BT = String.fromCharCode(96);
const FENCE = BT + BT + BT;
function arg(n, d) { const i = process.argv.indexOf("--" + n); return i >= 0 && process.argv[i + 1] ? process.argv[i + 1] : d; }
const SRC = arg("json", BENCH + "/r285_exec_commands_ab.json");
const OUT = arg("out", BENCH + "/r285_exec_commands_ab.md");
const j = JSON.parse(fs.readFileSync(SRC, "utf8"));
const prose = {};
let curKey = null;
for (const line of fs.readFileSync(T + "/r285_md_prose.txt", "utf8").split(NL)) {
  const i = line.indexOf("::");
  if (i > 0 && /^[a-z_0-9]+$/.test(line.slice(0, i))) { curKey = line.slice(0, i); const v = line.slice(i + 2); prose[curKey] = prose[curKey] ? prose[curKey] + NL + v : v; continue; }
  if (curKey && line.trim()) prose[curKey] += NL + line;   // continuation lines belong to the key
}
const L = [];
const code = (s) => BT + s + BT;
const push = (s) => L.push(s);
push("# 需求 6 执行级可复算面 · 两态字面命令真跑 A/B（R285-L）· 2026-10-30");
push("");
push("> 结论标记：**已实测** —— test-driven-development 与 frontend-slides 两件本运行真跑，ui-ux-pro-max 一件引用 Lead 读数。");
push("");
push(prose.head);
push("");
push("## 1. 总表（三件并列）");
push("");
push("| 件 | 改前 ref | 改后 ref | 来源 | 臂 | 字面命令 | 实跑 | 工具链缺 | 需外部账号 | rc=0 | 占位未解 | 落盘件数 | 声明兑现 |");
push("|---|---|---|---|---|---|---|---|---|---|---|---|---|");
for (const r of j.rows) {
  for (const arm of ["A", "B"]) {
    const a = r.arms[arm];
    const nm = arm === "A" ? "**" + r.skill + "**" : "";
    push("| " + nm + " | " + (arm === "A" ? code(r.before_ref) : "") + " | " + (arm === "A" ? code(r.after_ref) : "") + " | " + (arm === "A" ? r.source : "") + " | " + arm + " | " + a.commands_found + " | " + a.runnable + " | " + a.blocked_not_runnable + " | " + (a.needs_external_account || 0) + " | **" + a.rc_zero + "** | " + a.placeholder_unresolved + " | " + a.persisted_artifacts.length + " | " + a.doc_claim_met + " |");
  }
}
push("");
const tot = "rows=" + j.rows.length + " commands_ok=" + j.totals.rc_zero_after + "/" + j.totals.commands_found_after + " artifacts_before=" + j.totals.artifacts_before + " artifacts_after=" + j.totals.artifacts_after;
push("三件汇总（与判据末行同形）：" + code(tot));
push("");
push(prose.reading);
push("");
push(prose.finding);
push("");
push("## 2. 口径（分子分母写死，与 JSON 的 caliber_note 同源）");
push("");
const cal = j.caliber_note;
const order = ["commands_found", "runnable", "rc_zero", "operative_rc", "needs_external_account", "variant_rows", "placeholder_unresolved", "persisted_artifacts", "doc_claim_met", "unverified_rule", "not_measured"];
for (const k of order) { if (cal[k]) push("- **" + k + "**：" + cal[k]); }
push("");
push("## 3. 逐件逐命令明细");
push("");
for (const r of j.rows) {
  push("### " + r.skill);
  push("");
  push("- 改前 " + code(r.before_ref) + " / 改后 " + code(r.after_ref) + "；来源：" + r.source);
  if (r.cited_headline) {
    push("- 引用读数（不在本件复算）：" + code("Q_A=" + r.cited_headline.Q_A + " Q_B=" + r.cited_headline.Q_B + " uplift=" + r.cited_headline.uplift_pct + "%") + "，出处 " + r.provenance_files.map((f) => code(path.basename(f))).join(" + "));
    if (r.ref_note) push("- ref 对账：" + r.ref_note);
  }
  if (r.doc_claim) push("- 本件机械判定的文档声明：" + r.doc_claim);
  if (r.arm_docs) push("- 臂文本：A " + code("sha12=" + r.arm_docs.A.sha12 + " / " + r.arm_docs.A.bytes + "B") + " ｜ B " + code("sha12=" + r.arm_docs.B.sha12 + " / " + r.arm_docs.B.bytes + "B"));
  if (r.query_excluded) push("- 查询型已排除（不进分母）：A " + JSON.stringify(r.query_excluded.A) + " ｜ B " + JSON.stringify(r.query_excluded.B));
  push("");
  if (!r.detail_rows) { push("> 引用行：本运行未复跑，逐条出处见 r281 两件（执行级AB_r281_2026-10-29.md 第 3 节维 3）。"); push(""); continue; }
  for (const arm of ["A", "B"]) {
    push("#### 臂 " + arm + " —— " + r.arms[arm].commands_found + " 条字面命令 / " + r.arms[arm].executions + " 次实跑（其中变体 " + (r.arms[arm].variant_executions || 0) + " 次）");
    push("");
    push("| # | 文中字面命令（状态） | 实跑 argv 尾段 | rc | stdout B | 新落盘 | 备注 |");
    push("|---|---|---|---|---|---|---|");
    r.detail_rows[arm].forEach((x, i) => {
      const av = (x.argv_resolved_used || x.argv_hand_listed).slice(-3).join(" ").split("|").join("/");
      const note = x.blocked_reason ? x.blocked_reason : (x.external_service ? "需外部账号（环境边界，非文档缺陷）" : (x.primary === false ? "变体：占位符改绝对路径" : ""));
      push("| " + (i + 1) + " | " + code(x.doc_literal) + "（" + (x.state || "normal") + "） | " + code(av.slice(-90)) + " | " + x.rc + (x.spawn_error ? "/" + x.spawn_error : "") + " | " + x.stdout_bytes + " | " + x.persisted_new.length + " | " + note + " |");
    });
    push("");
    const arts = r.arms[arm].persisted_artifacts;
    push("- 该臂声明输出目录新落盘：" + (arts.length ? arts.map((s) => code(s)).join(" ") : "无（这些命令只报告结果、不落工件）"));
    push("- 声明兑现：" + r.arms[arm].doc_claim_met + " —— " + (r.doc_claim_evidence ? r.doc_claim_evidence[arm] : ""));
    if (r.arms[arm].doc_claim_sub) push("- 子声明（逐项机械判定）：" + JSON.stringify(r.arms[arm].doc_claim_sub));
    push("");
  }
}
push("## 4. 负向对照（两条腿，都有实测输出）");
push("");
const nc = j.negative_controls.control_1_identical_text;
const leg1 = nc.ran ? "已实跑：把 test-driven-development 的 B 臂文本换成 A 臂那份 " + code(nc.substituted_B_with) + " 之后，两臂读数逐字相等 " + (nc.identical ? "**PASS**" : "**FAIL**") : "未跑";
push("**腿 1 · 同文必同读**：" + leg1);
push("");
push("臂 B 的 ref 写成 SUBSTITUTED 是显式说明它不再是 079b91f3。同一份文本必须给同一组读数；若这里不相等，说明尺子在按臂序或目录名打分，整表作废。");
push("");
if (nc.ran) {
  push("| 字段 | 臂 A（原改前文） | 臂 B（换成 A 那份） |");
  push("|---|---|---|");
  for (const k of Object.keys(nc.readings_A)) {
    const va = Array.isArray(nc.readings_A[k]) ? nc.readings_A[k].length : nc.readings_A[k];
    const vb = Array.isArray(nc.readings_B[k]) ? nc.readings_B[k].length : nc.readings_B[k];
    push("| " + k + " | " + JSON.stringify(va) + " | " + JSON.stringify(vb) + " |");
  }
  push("| 文本 sha12 | " + nc.A_text_sha12 + " | " + nc.B_text_sha12 + " |");
  push("");
}
push("**腿 2 · 改 rc 必报 MISMATCH**：把某条命令的 rc 由 0 改成 1 写进交付件 JSON 的临时副本，再用同一把尺对副本重算，校验器必须点名 MISMATCH 字段。实测 stdout（副本用完即删）：");
push("");
push(FENCE + "text");
push(j.negative_controls.control_2_stdout || "(未跑)");
push(FENCE);
push("");
push("## 5. 取文本、跑数与复算判据");
push("");
push(FENCE + "bash");
for (const line of String(j.provenance_cmd).split(NL)) push(line);
push(FENCE);
push("");
push("判据命令 = 重跑本件自己的脚本（不跑任何人的门），期望末行：");
push("");
push(FENCE + "text");
push("[EXEC-AB] " + tot);
push(FENCE);
push("");
push(prose.closing);
push("");
push("measured_at：" + j.measured_at + " ｜ 证据文件 sha256：" + j.evidence_sha256);
push("");
fs.writeFileSync(OUT, L.join(NL));
console.log("[MD] wrote " + OUT + " lines=" + L.length);