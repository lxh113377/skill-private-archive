import url from 'node:url';
import fs from "node:fs";
import path from "node:path";
import cp from "node:child_process";
// Negative control 2, run end to end: copy the deliverable JSON, flip one rc_zero 0 -> 1
// in the copy, point the same validator at the copy, require it to print MISMATCH naming
// the field, then delete the copy. Nothing is left behind in any directory.
const ROOT = path.resolve(path.dirname(url.fileURLToPath(import.meta.url)), '..', '..');
const T = ROOT + "/_repro/r285l";
const BENCH = ROOT + "/06-benchmark";
const NL = String.fromCharCode(10);
const NODE = "C:/Program Files/nodejs/node.exe";
const DELIVERABLE = BENCH + "/r285_exec_commands_ab.json";
const EVIDENCE = T + "/results/run.json";
const COPY = T + "/results/negctl2_copy.json";
const d = JSON.parse(fs.readFileSync(DELIVERABLE, "utf8"));
const row = d.rows.find((r) => r.arms.B.rc_zero > 0);
if (!row) { console.log("[NEGCTL2] NO-ADJUSTABLE-ROW"); process.exit(1); }
const skill = row.skill;
const before = row.arms.B.rc_zero;
row.arms.B.rc_zero = before - 1;   // tamper: claim one fewer zero-rc command
fs.writeFileSync(COPY, JSON.stringify(d, null, 2));
const args = [T + "/r285_validate.mjs", "--evidence", EVIDENCE, "--deliverable", COPY, "--sub", T + "/results/negctl_sub.json"];
const r = cp.spawnSync(NODE, args, { encoding: "utf8", cwd: ROOT });
const outStr = String(r.stdout || "") + String(r.stderr || "");
const needle = "MISMATCH " + skill + ".arms.B.rc_zero";
const named = outStr.includes(needle);
const lines = outStr.split(NL).filter((x) => x.includes("MISMATCH") || x.startsWith("[CONSISTENCY]") || x.startsWith("[EXEC-AB]") || x.startsWith("[NEGCTL-1]"));
fs.unlinkSync(COPY);
const gone = !fs.existsSync(COPY);
console.log("[NEGCTL2] tampered field = " + skill + ".arms.B.rc_zero " + before + " -> " + (before - 1));
for (const l of lines) console.log("[NEGCTL2][validator] " + l);
console.log("[NEGCTL2] validator_exit=" + r.status + " named_field=" + (named ? "YES" : "NO") + " copy_deleted=" + (gone ? "YES" : "NO"));
console.log("[NEGCTL2] " + (named && r.status !== 0 && gone ? "PASS: teeth confirmed (MISMATCH named, non-zero exit, copy removed)" : "FAIL: ruler has no teeth"));
process.stdout.write("");