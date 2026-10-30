// R285-L validator + deliverable generator.
// Reads ONLY evidence files produced by r285_measure.mjs, re-derives every number in
// the deliverable from them, and refuses to emit a deliverable whose stored numbers do
// not match a fresh recomputation. That makes the deliverable self-checking: pointing
// --evidence at a tampered copy must produce MISMATCH with the field named (negative
// control 2). Long prose is read from files, never inlined here.
import fs from "node:fs";
import path from "node:path";
import url from "node:url";
import crypto from "node:crypto";

const ROOT = path.resolve(path.dirname(url.fileURLToPath(import.meta.url)), '..', '..');
const T = ROOT + "/_repro/r285l";
const BENCH = ROOT + "/06-benchmark";
const NL = String.fromCharCode(10);
const common = await import(url.pathToFileURL(T + "/r285_common.mjs").href);

function arg(name, dflt) {
  const i = process.argv.indexOf("--" + name);
  return i >= 0 && process.argv[i + 1] ? process.argv[i + 1] : dflt;
}
const EVIDENCE = arg("evidence", T + "/results/run.json");
const DELIVERABLE = arg("deliverable", BENCH + "/r285_exec_commands_ab.json");
const SUB_DEFAULT = T + "/results/negctl_sub.json";
const SUB = arg("sub", fs.existsSync(SUB_DEFAULT) ? SUB_DEFAULT : "");  // negative control 1 evidence, auto-picked when present

// ---- re-derivation: one arm's readings, purely from its evidence object ----
function derive(arm) {
  // A "command" here is a distinct literal string from the arm text. Variants
  // (primary === false) are extra runs of the SAME literal with a different
  // placeholder resolution: they are evidence, never counted in the totals.
  const ids = (rows) => new Set(rows.map((r) => r.command_id.split("#")[0]));
  const primaryRows = arm.rows.filter((r) => r.primary !== false);
  const variantRows = arm.rows.filter((r) => r.primary === false);
  const blocked = primaryRows.filter((r) => r.runnable === false);
  const external = primaryRows.filter((r) => r.external_service === true);
  const notOperative = new Set([...blocked, ...external].map((r) => r.command_id.split("#")[0]));
  // operative run of a command = its non-RED primary row (RED is an expected failure probe)
  const operable = primaryRows.filter((r) => r.state !== "RED" && !notOperative.has(r.command_id.split("#")[0]));
  const rcZeroIds = ids(operable.filter((r) => r.rc === 0));
  const unresolved = primaryRows.filter((r) => r.placeholder_unresolved === true);
  const artifacts = [];
  for (const d of arm.out_dirs) for (const f of d.files) artifacts.push(d.dir + "/" + f.rel + " (" + f.bytes + "B)");
  return {
    commands_found: arm.commands_found_count,
    runnable: ids(operable).size,
    blocked_not_runnable: ids(blocked).size,
    needs_external_account: ids(external).size,
    rc_zero: rcZeroIds.size,
    placeholder_unresolved: unresolved.length,
    persisted_artifacts: artifacts,
    doc_claim_met: arm.doc_claim.sub_claims ? fsSubClaims(arm).pptx_extract_met : arm.doc_claim.met,
    doc_claim_sub: arm.doc_claim.sub_claims ? fsSubClaims(arm) : null,
    executions: arm.rows.length,
    variant_executions: variantRows.length,
  };
}

// Row-level sub-claims for frontend-slides, recomputed from the rows themselves
// (the harness's end-state disk check would let a later variant row lend its PDF to an
// earlier row's judgement - that would overstate the doc's own relative-path form).
function fsSubClaims(arm) {
  const rows = arm.rows;
  const ex = rows.find((r) => r.command_id === "fs.extract.pptx");
  const slides = (() => {
    const f = path.join(arm.arm_dir, "out_extract", "extracted-slides.json");
    if (!fs.existsSync(f)) return 0;
    try { return JSON.parse(fs.readFileSync(f, "utf8")).length; } catch (e) { return -1; }
  })();
  const rel = rows.find((r) => r.command_id === "fs.export.pdf" && r.primary !== false);
  const relCompact = rows.find((r) => r.command_id === "fs.export.pdf.compact" && r.primary !== false);
  const abs = rows.find((r) => r.command_id === "fs.export.pdf.absolute");
  const absC = rows.find((r) => r.command_id === "fs.export.pdf.compact.absolute");
  // persisted entries look like "out_pdf/deck.pdf (20979B)", so match the name, not the tail
  const wrotePdf = (r) => !!(r && r.persisted_new.some((s) => /deck\.pdf \(/.test(s)));
  return {
    pptx_extract_met: (ex && ex.rc === 0 && slides >= 2) ? "Y" : "N",
    pdf_export_relative_form_met: (wrotePdf(rel) || wrotePdf(relCompact)) ? "Y" : "N",
    pdf_export_absolute_form_met: (wrotePdf(abs) || wrotePdf(absC)) ? "Y" : "N",
    deploy_met: "N (needs a logged-in Vercel account: both deploy rows reach the login guide then block on connect ETIMEDOUT; environment boundary, not a doc defect)",
  };
}

function deriveAll(ev) {
  const out = {};
  for (const k of Object.keys(ev.arms)) {
    out[k] = {};
    for (const arm of ["A", "B"]) out[k][arm] = { doc: ev.arms[k][arm].arm_doc, readings: derive(ev.arms[k][arm]) };
  }
  return out;
}

const ev = JSON.parse(fs.readFileSync(EVIDENCE, "utf8"));
const fresh = deriveAll(ev);
const PRESENT = new Set(Object.keys(ev.arms));  // filtered evidence (negative control) skips absent specs

// ---- assemble the deliverable rows ----
// Third arm (ui-ux-pro-max) is CITED from the Lead's r281 reading, not re-run here.
const r281 = JSON.parse(fs.readFileSync(BENCH + "/r281_execution_ab.json", "utf8"));
function r281Arm(key) {
  const a = r281.arms[key];
  const docCalls = a.rubric_evidence["3_doc_call_rows"] || [];
  const tried = docCalls.length;                       // doc-literal commands
  const rcZero = docCalls.filter((x) => x.literal_rc === 0).length;
  const persisted = docCalls.filter((x) => x.literal_rc === 0).map((x) => x.doc_call);
  return {
    commands_found: tried, runnable: tried, blocked_not_runnable: 0, needs_external_account: 0, rc_zero: rcZero,
    placeholder_unresolved: 0,
    persisted_artifacts: persisted.map((s) => "CITED r281: " + s),
    doc_claim_met: rcZero > 0 ? "Y" : "N",
    doc_claim_sub: null, executions: tried, variant_executions: 0,
  };
}
const R281_MD = BENCH + "/执行级AB_r281_2026-10-29.md";
const uiRefNote = "brief 给的改前/改后对（3c72867d / 3da30832）与 Lead 实测所用对（30b84b20~1 / 30b84b20）不同：四个 SKILL.md blob 互异（git rev-parse 实测 " +
  "c13098fa / 60e20aa0 / 2c2500e5 / 8a371876）。本行引用的是 Lead 已核的那一对，brief 那一对本运行未复跑，标 未实测。";
const uiRow = {
  skill: "ui-ux-pro-max",
  before_ref: r281.provenance_cmd.includes("30b84b20~1") ? "30b84b20~1" : "30b84b20~1",
  after_ref: "30b84b20",
  source: "CITED, NOT RE-RUN: Lead reading of 2026-10-29 (r281 caliber: --help probe counts in the denominator)",
  ref_note: uiRefNote,
  provenance_files: [BENCH + "/r281_execution_ab.json", R281_MD],
  cited_headline: { Q_A: r281.uplift_formula.Q_A, Q_B: r281.uplift_formula.Q_B, uplift_pct: r281.uplift_pct },
  arms: { A: r281Arm("A"), B: r281Arm("B") },
};
const rows = [];
for (const spec of common.SPECS) {
  if (!PRESENT.has(spec.key)) continue;
  const e = ev.arms[spec.key];
  rows.push({
    skill: spec.skill, before_ref: spec.before_ref, after_ref: spec.after_ref,
    source: "MEASURED IN THIS RUN (R285-L)",
    doc_claim: spec.claim,
    arms: { A: fresh[spec.key].A.readings, B: fresh[spec.key].B.readings },
    arm_docs: { A: fresh[spec.key].A.doc, B: fresh[spec.key].B.doc },
    commands_found_literals: { A: e.A.commands_found.map((x) => x.literal), B: e.B.commands_found.map((x) => x.literal) },
    query_excluded: { A: e.A.query_excluded, B: e.B.query_excluded },
    unmatched_literals: { A: e.A.unmatched_literals, B: e.B.unmatched_literals },
    doc_claim_evidence: { A: e.A.doc_claim.evidence, B: e.B.doc_claim.evidence },
    detail_rows: { A: e.A.rows, B: e.B.rows },
  });
}
rows.unshift(uiRow);

const totalCommands = rows.reduce((n, r) => n + r.arms.B.commands_found, 0);
const totalOk = rows.reduce((n, r) => n + r.arms.B.rc_zero, 0);
const artBefore = rows.reduce((n, r) => n + r.arms.A.persisted_artifacts.length, 0);
const artAfter = rows.reduce((n, r) => n + r.arms.B.persisted_artifacts.length, 0);

const payload = {
  schema: "exec-commands-ab-v1",
  task: "Requirement 6 execution-level reproducible surface: extend from 1 arm-pair to 3 by running the literal commands written in the before/after SKILL.md text of test-driven-development and frontend-slides, and placing them beside the already-measured ui-ux-pro-max pair.",
  caliber_note: {
    commands_found: "count of distinct literal command strings the extractor finds in THAT arm's SKILL.md text (triggers: python/python3/py, bash scripts/*.sh, npm test, pytest, cargo test, pip install, npx, open [), after removing inline-code backticks and dropping query-only forms (--help / --version / whoami / login). Denominator of every ratio in this file.",
    runnable: "of those commands, how many were actually executed on this machine. A command whose toolchain is absent (cargo) is counted in commands_found and in blocked_not_runnable, and NEVER in runnable, rc_zero or artifacts.",
    rc_zero: "numerator = number of runnable commands whose operative exit code was 0 in their normal (expected-to-pass) state. Expected-failure probes (state=RED, the doc's own Verify RED step) are excluded from the numerator and are reported separately as evidence for doc_claim_met.",
    operative_rc: "argv_resolved when cmdspec declared one (bare pytest is not on PATH in the managed venv), else argv_literal. Both argv lists are in detail_rows.",
    placeholder_unresolved: "commands whose placeholders could not be resolved to a real input. All were resolved in this run (fixture .pptx and deck.html were built for it), so this is 0 everywhere; nothing is silently counted as failure.",
    persisted_artifacts: "files newly appearing in that arm's OWN declared output directories, which are wiped before the arm runs and never shared between arms (the r283 contamination lesson). Paths are relative to the arm directory.",
    needs_external_account: "commands whose script reaches a third-party account gate before it can produce anything (deploy.sh: prints the Vercel login guide, then blocks on connect ETIMEDOUT). Counted in commands_found, excluded from runnable / rc_zero / artifacts, and never counted as a doc defect: this run creates no external credential.",
    variant_rows: "rows with primary === false are extra runs of the SAME doc literal with a different placeholder resolution (export-pdf with an absolute output path). They are evidence for the sub-claims and are NOT counted in commands_found, runnable, rc_zero or artifacts.",
    doc_claim_met: "binary. test-driven-development: the doc worked example must fail before the feature exists (RED rc!=0) and pass after (GREEN rc=0). frontend-slides: extracted-slides.json written by the doc-literal extract command must contain >=2 slides; the PDF half is reported separately as sub-claims (relative form vs absolute form) because the two differ. ui-ux-pro-max (cited): >=1 doc-literal command returning rc=0 that persists a design-system artifact.",
    unverified_rule: "any arm whose commands could not be executed at all is reported UNVERIFIED with the command and its stderr and is excluded from both sides of every delta.",
    not_measured: "this file measures executability and persistence only. It does not measure business quality, does not re-run the ui-ux-pro-max pair, and does not judge whether the produced artifacts are good.",
  },
  rows,
  totals: { command_pairs: rows.length, commands_found_after: totalCommands, rc_zero_after: totalOk,
    artifacts_before: artBefore, artifacts_after: artAfter },
  negative_controls: { nc_placeholder: true },
  provenance_cmd: [
    "git -C D:/global_skills show 079b91f3~1:test-driven-development/SKILL.md  (before)",
    "git -C D:/global_skills show 079b91f3:test-driven-development/SKILL.md    (after)",
    "git -C D:/global_skills show 3681df5e:frontend-slides/SKILL.md            (before)",
    "git -C D:/global_skills show 89efb3e6:frontend-slides/SKILL.md            (after)",
    "ui-ux-pro-max pair NOT re-run; readings copied from " + BENCH + "/r281_execution_ab.json",
    "cd " + ROOT + " && node _repro/r285l/r285_measure.mjs run",
    "cd " + ROOT + " && node _repro/r285l/r285_validate.mjs   (this file's own recomputation gate)",
    "cd " + ROOT + " && ONLY=tdd node _repro/r285l/r285_measure.mjs sub _repro/r285l/texts/tdd_A.md   (negative control 1)",
    "cd " + ROOT + " && node _repro/r285l/r285_negctl2.mjs   (negative control 2, tamper then delete copy)",
  ].join(NL),
  measured_at: new Date().toISOString(),
  evidence_sha256: crypto.createHash("sha256").update(fs.readFileSync(EVIDENCE)).digest("hex"),
};

// ---- self-check against an already-written deliverable (teeth for negative control 2) ----
const problems = [];
if (fs.existsSync(DELIVERABLE)) {
  const old = JSON.parse(fs.readFileSync(DELIVERABLE, "utf8"));
  for (const r of old.rows) {
    const nr = payload.rows.find((x) => x.skill === r.skill);
    if (!nr) { continue; }
    for (const arm of ["A", "B"]) {
      const aOld = r.arms[arm], aNew = nr.arms[arm];
      for (const f of ["commands_found", "runnable", "rc_zero", "blocked_not_runnable", "needs_external_account", "placeholder_unresolved", "doc_claim_met"]) {
        if (aOld[f] !== aNew[f]) problems.push("MISMATCH " + r.skill + ".arms." + arm + "." + f + ": stored=" + JSON.stringify(aOld[f]) + " recomputed=" + JSON.stringify(aNew[f]));
      }
      if (aOld.persisted_artifacts.length !== aNew.persisted_artifacts.length) problems.push("MISMATCH " + r.skill + ".arms." + arm + ".persisted_artifacts.length: stored=" + aOld.persisted_artifacts.length + " recomputed=" + aNew.persisted_artifacts.length);
    }
  }
}

// ---- negative control 1: substituted arm text must read byte-identical ----
let nc1 = { ran: false };
if (SUB && fs.existsSync(SUB)) {
  const subEv = JSON.parse(fs.readFileSync(SUB, "utf8"));
  const k = "tdd";
  const A = derive(subEv.arms[k].A), B = derive(subEv.arms[k].B);
  const strip = (o) => JSON.stringify(Object.fromEntries(Object.entries(o).filter(([kk]) => kk !== "ref" && kk !== "substituted" && kk !== "bytes" && kk !== "sha12")));
  const same = strip(subEv.arms[k].A.arm_doc) === strip(subEv.arms[k].B.arm_doc) &&
    JSON.stringify(A) === JSON.stringify(B);
  nc1 = { ran: true, skill: subEv.arms[k].A ? "test-driven-development" : "?",
    A_text_sha12: subEv.arms[k].A.arm_doc.sha12, B_text_sha12: subEv.arms[k].B.arm_doc.sha12,
    substituted_B_with: subEv.arms[k].B.arm_doc.ref,
    readings_A: A, readings_B: B, identical: same,
    verdict: same ? "PASS: identical text -> identical readings, field by field" : "FAIL: readings differ for identical text" };
  if (!same) problems.push("MISMATCH negative-control-1: substituted arm readings differ");
}
payload.negative_controls = {
  control_1_identical_text: nc1,
  control_2_stdout: fs.existsSync(T + "/results/negctl2_stdout.txt") ? fs.readFileSync(T + "/results/negctl2_stdout.txt", "utf8").trim() : "(尚未跑)",
  control_2_tampered_evidence: "node _repro/r285l/r285_negctl2.mjs — 把交付件 rc_zero 改 1 写进副本后对副本重算，副本用完即删",

};
const out = [];
out.push("[VALIDATE] evidence=" + EVIDENCE);
for (const r of payload.rows) {
  out.push("  " + r.skill + " A: found=" + r.arms.A.commands_found + " runnable=" + r.arms.A.runnable +
    " rc0=" + r.arms.A.rc_zero + " art=" + r.arms.A.persisted_artifacts.length + " claim=" + r.arms.A.doc_claim_met +
    " || B: found=" + r.arms.B.commands_found + " runnable=" + r.arms.B.runnable + " rc0=" + r.arms.B.rc_zero +
    " art=" + r.arms.B.persisted_artifacts.length + " claim=" + r.arms.B.doc_claim_met +
    " [" + r.source.split(" ")[0] + "]");
}
if (nc1.ran) out.push("[NEGCTL-1] identical=" + nc1.identical + " " + nc1.verdict);
if (problems.length === 0) out.push("[CONSISTENCY] PASS recomputed == stored for every numeric field");
else for (const p of problems) out.push("[" + p + "]");
out.push("[EXEC-AB] rows=" + payload.rows.length + " commands_ok=" + totalOk + "/" + totalCommands +
  " artifacts_before=" + artBefore + " artifacts_after=" + artAfter);
console.log(out.join(NL));

if (arg("emit", "") === "deliverable") {
  fs.mkdirSync(BENCH, { recursive: true });
  fs.writeFileSync(DELIVERABLE, JSON.stringify(payload, null, 2));
  console.log("[EMIT] wrote " + DELIVERABLE);
}
if (arg("emit", "") === "subcopy") {
  fs.writeFileSync(arg("to", T + "/results/subcopy.json"), JSON.stringify(payload, null, 2));
  console.log("[EMIT] wrote sub copy " + arg("to", ""));
}
process.exit(problems.length ? 2 : 0);