// R285-L measurement harness (v2). Pure mechanics:
//   1. arm text comes from git refs (or a substituted file for the negative control),
//   2. the command set is whatever the extractor finds in that text (never hand-picked),
//   3. argv for each command is hand listed in r285_cmds.json; placeholders are resolved to
//      real inputs there; nothing is ever produced by splitting doc text on whitespace,
//   4. each (skill, arm) gets its own directory tree, wiped before that arm runs, and the
//      declared output dirs are wiped again before each row, so one arm's leftovers can
//      never be counted as the other arm's artifacts (the r283 failure mode),
//   5. recorded per row: rc, stdout bytes, files newly appearing in the arm output dirs.
import fs from "node:fs";
import path from "node:path";
import url from "node:url";

const ROOT = path.resolve(path.dirname(url.fileURLToPath(import.meta.url)), '..', '..');
const T = ROOT + "/_repro/r285l";
const NL = String.fromCharCode(10);
const common = await import(url.pathToFileURL(T + "/r285_common.mjs").href);
const { SPECS, WORK, PY, GB, loadArm, extractCommands, gitShowBuf, wipeDir, listFiles, treeList, runOne } = common;

const MODE = process.argv[2] || "run";            // run | sub
const SUB_FILE = process.argv[3] || "";          // text substituted for the B arm in negative control 1
const OUT_NAME = MODE === "sub" ? "negctl_sub" : "run";

const SPEC = JSON.parse(fs.readFileSync(T + "/r285_cmds.json", "utf8"));
const CMDS = SPEC.rows;
const OUT_DIRS = { tdd: ["out_persist"], fs: ["out_extract", "out_pdf", "out_pdf_compact"] };

// Explicit env: process.env here has no PATH, and npm/npx/node must be reachable
// from inside the bash scripts too (export-pdf.sh runs npm install playwright).
const ENV = {
  PATH: SPEC.ENV_PATH,
  SystemRoot: "C:/windows",
  APPDATA: "C:/Users/37533/AppData/Roaming",
  LOCALAPPDATA: "C:/Users/37533/AppData/Local",
  USERPROFILE: "C:/Users/37533",
  HOME: "C:/Users/37533",
  TEMP: "C:/Users/37533/AppData/Local/Temp",
  TMP: "C:/Users/37533/AppData/Local/Temp",
  PYTHONIOENCODING: "utf-8",
  PYTHONPYCACHEPREFIX: T + "/pycache",
};

function fill(tok) {
  return String(tok)
    .split("{PY}").join(PY)
    .split("{GB}").join(GB)
    .split("{NODE_EXE}").join(SPEC.NODE_EXE)
    .split("{NPMCLI}").join(SPEC.NPMCLI)
    .split("{NPXCLI}").join(SPEC.NPXCLI);
}

function materialise(spec, arm) {
  const ref = arm === "A" ? spec.before_ref : spec.after_ref;
  const dir = path.join(WORK, MODE + "/" + spec.key + "_" + arm);
  wipeDir(dir);
  fs.mkdirSync(path.join(dir, "scripts"), { recursive: true });
  for (const f of treeList(ref, spec.dir)) {
    if (!f.startsWith("scripts/")) continue;
    const buf = gitShowBuf(ref, spec.dir + "/" + f);
    const dst = path.join(dir, f);
    fs.mkdirSync(path.dirname(dst), { recursive: true });
    fs.writeFileSync(dst, buf);
  }
  if (spec.key === "fs") {
    fs.copyFileSync(path.join(T, "fixtures", "lo_out", "fixture.pptx"), path.join(dir, "fixture.pptx"));
    fs.mkdirSync(path.join(dir, "my-deck"), { recursive: true });
    fs.copyFileSync(path.join(T, "fixtures", "deck.html"), path.join(dir, "my-deck", "index.html"));
  }
  if (spec.key === "tdd") {
    const sc = path.join(dir, "scaffold");
    fs.mkdirSync(path.join(sc, "path", "to"), { recursive: true });
    const Q = String.fromCharCode(34);
    fs.writeFileSync(path.join(sc, "package.json"), JSON.stringify({
      name: "r285-" + spec.key + "-" + arm, private: true,
      scripts: { test: "node --test path/to/test.test.ts" } }, null, 2));
    const green = ["function submitForm(data) {",
      "  if (!data.email || !String(data.email).trim()) {",
      "    return { error: " + Q + "Email required" + Q + " };",
      "  }",
      "  return { error: null };",
      "}",
      "module.exports = { submitForm };", ""].join(NL);
    const red = ["function submitForm(data) {",
      "  return { error: undefined }; // feature not implemented yet",
      "}",
      "module.exports = { submitForm };", ""].join(NL);
    fs.writeFileSync(path.join(sc, "form_green.js"), green);
    fs.writeFileSync(path.join(sc, "form_red.js"), red);
    fs.copyFileSync(path.join(sc, "form_red.js"), path.join(sc, "form.js"));
    fs.writeFileSync(path.join(sc, "path", "to", "test.test.ts"), [
      "const { test } = require(" + Q + "node:test" + Q + ");",
      "const assert = require(" + Q + "node:assert" + Q + ");",
      "const { submitForm } = require(" + Q + "../../form.js" + Q + ");",
      "test(" + Q + "rejects empty email" + Q + ", () => {",
      "  assert.strictEqual(submitForm({ email: " + Q + Q + " }).error, " + Q + "Email required" + Q + ");",
      "});", ""].join(NL));
    const spy = path.join(dir, "scaffold_py");
    fs.mkdirSync(spy, { recursive: true });
    fs.writeFileSync(path.join(spy, "form.py"), [
      "def submit_form(data):",
      "    if not str(data.get(" + Q + "email" + Q + ", " + Q + Q + ")).strip():",
      "        return { " + Q + "error" + Q + ": " + Q + "Email required" + Q + " }",
      "    return { " + Q + "error" + Q + ": None }", ""].join(NL));
    fs.writeFileSync(path.join(spy, "test_form.py"), [
      "from form import submit_form",
      "",
      "",
      "def test_rejects_empty_email():",
      "    assert submit_form({ " + Q + "email" + Q + ": " + Q + Q + " })[ " + Q + "error" + Q + "] == " + Q + "Email required" + Q + "", ""].join(NL));
  }
  return dir;
}

function runRow(row, armDir, spec, stateTag) {
  const argv = (row.argv_resolved || row.argv_literal).map((a) => fill(a).split("{ARM}").join(armDir));
  const cwd = fill(row.cwd).split("{ARM}").join(armDir);
  fs.mkdirSync(cwd, { recursive: true });
  if (spec.key === "tdd") {
    const sc = path.join(armDir, "scaffold");
    const src = stateTag === "RED" ? "form_red.js" : "form_green.js";
    fs.copyFileSync(path.join(sc, src), path.join(sc, "form.js"));
  }
  const outPaths = OUT_DIRS[spec.key].map((d) => path.join(armDir, d));
  const before = new Set();
  for (let i = 0; i < outPaths.length; i++) for (const f of listFiles(outPaths[i])) {
    before.add(OUT_DIRS[spec.key][i] + "/" + f.rel);  // key by dir+name so deck.pdf in two dirs counts as two artifacts
  }
  const attempts = [];
  let r = null;
  const maxAttempts = row.max_attempts || 1;
  for (let i = 0; i < maxAttempts; i++) {
    r = runOne(argv, { cwd, timeout: row.timeout_ms || 120000, env: ENV });
    attempts.push({ attempt: i + 1, rc: r.rc, spawn_error: r.spawn_error, stdout_bytes: r.stdout_bytes,
      stderr_tail: r.stderr_tail.slice(-300) });
    if (r.rc === 0) break;   // network-bound rows: operative rc is the first success
  }
  const fresh = [];
  for (const d of outPaths) for (const f of listFiles(d)) {
    const k = OUT_DIRS[spec.key][outPaths.indexOf(d)] + "/" + f.rel;
    if (before.has(k)) continue;
    fresh.push(k + " (" + f.bytes + "B)");
  }
  return {
    command_id: row.id + (stateTag ? "#" + stateTag : ""),
    doc_literal: row.literal,
    argv_hand_listed: row.argv_literal.map((a) => fill(a).split("{ARM}").join(armDir)),
    argv_resolved_used: row.argv_resolved ? argv : null,
    cwd: cwd,
    state: stateTag || null,
    primary: row.primary !== false,
    attempts: attempts,
    rc: r.rc,
    spawn_error: r.spawn_error,
    signal: r.signal,
    stdout_bytes: r.stdout_bytes,
    stderr_bytes: r.stderr_bytes,
    stdout_tail: r.stdout_tail.slice(-600),
    stderr_tail: r.stderr_tail.slice(-600),
    persisted_new: fresh,
    runnable: row.runnable === true,
    blocked_reason: row.runnable ? null : row.blocked_reason,
    external_service: row.external_service === true,
    placeholder_unresolved: row.placeholder_unresolved === true,
    resolve_note: row.resolve_note,
  };
}

function docClaim(spec, armDir, rows) {
  if (spec.key === "tdd") {
    const red = rows.find((x) => x.state === "RED");
    const green = rows.find((x) => x.state === "GREEN");
    const met = !!(red && green && red.rc !== 0 && green.rc === 0);
    return { claim: spec.claim, met: met ? "Y" : "N",
      evidence: "RED rc=" + (red ? red.rc : "n/a") + " / GREEN rc=" + (green ? green.rc : "n/a") +
        "; test body is the doc worked example (rejects empty email)" };
  }
  const ex = path.join(armDir, "out_extract", "extracted-slides.json");
  let n = 0;
  if (fs.existsSync(ex)) { try { n = JSON.parse(fs.readFileSync(ex, "utf8")).length; } catch (e) { n = -1; } }
  const pdf = path.join(armDir, "out_pdf", "deck.pdf");
  const pdfOk = fs.existsSync(pdf) && fs.statSync(pdf).size > 1000;
  const pdfC = path.join(armDir, "out_pdf_compact", "deck.pdf");
  const pdfCok = fs.existsSync(pdfC) && fs.statSync(pdfC).size > 1000;
  const pptMet = n >= 2;
  return { claim: spec.claim, met: pptMet ? "Y" : "N",
    sub_claims: { pptx_extract_met: pptMet ? "Y" : "N", pdf_export_met: (pdfOk || pdfCok) ? "Y" : "N",
      pdf_export_relative_form_met: pdfOk ? "Y" : "N" },
    evidence: "extracted-slides.json slides=" + n + "; out_pdf/deck.pdf=" + pdfOk +
      "; out_pdf_compact/deck.pdf=" + pdfCok +
      (pdfOk ? " size=" + fs.statSync(pdf).size + "B" : "") +
      (pdfCok ? " compact size=" + fs.statSync(pdfC).size + "B" : "") };
}

const ONLY = (process.env.ONLY || "").split(",").filter(Boolean);
const ACTIVE = ONLY.length ? SPECS.filter((s) => ONLY.includes(s.key)) : SPECS;
const results = { mode: MODE, env_path: SPEC.ENV_PATH, only: ONLY, arms: {} };
for (const spec of ACTIVE) {
  results.arms[spec.key] = {};
  for (const arm of ["A", "B"]) {
    const override = MODE === "sub" && arm === "B" ? SUB_FILE : "";
    const a = loadArm(spec, arm, override);
    const ex = extractCommands(a.text);
    const armDir = materialise(spec, arm);
    // declared output dirs are wiped exactly once per arm: the arm's own rows accumulate
    // into them, and nothing from another arm or an earlier run survives
    for (const d of OUT_DIRS[spec.key]) wipeDir(path.join(armDir, d));
    const foundLits = ex.found.map((x) => x.literal);
    const rows = [];
    // run in cmdspec order (playwright/chromium download first), only rows the text mentions
    for (const row of CMDS.filter((r) => r.skill === spec.skill)) {
      if (!foundLits.includes(row.literal)) continue;
      if (row.id === "tdd.npm.test.example") {
        rows.push(runRow(row, armDir, spec, "RED"));
        rows.push(runRow(row, armDir, spec, "GREEN"));
        continue;
      }
      rows.push(runRow(row, armDir, spec, null));
    }
    const unmatched = foundLits.filter((l) => !CMDS.some((r) => r.skill === spec.skill && r.literal === l));
    results.arms[spec.key][arm] = {
      arm_doc: { ref: a.ref, bytes: a.bytes, sha12: a.sha12, substituted: a.substituted === true },
      commands_found: ex.found.map((x) => ({ literal: x.literal, line: x.line })),
      commands_found_count: ex.found.length,
      query_excluded: ex.queries.map((x) => x.literal),
      rows: rows,
      unmatched_literals: unmatched,
      doc_claim: docClaim(spec, armDir, rows),
      out_dirs: OUT_DIRS[spec.key].map((d) => ({ dir: d, files: listFiles(path.join(armDir, d)) })),
      arm_dir: armDir,
    };
  }
}
fs.mkdirSync(T + "/results", { recursive: true });
fs.writeFileSync(T + "/results/" + OUT_NAME + ".json", JSON.stringify(results, null, 2));
const sum = [];
for (const spec of ACTIVE) for (const arm of ["A", "B"]) {
  const r = results.arms[spec.key][arm];
  const ok = r.rows.filter((x) => x.rc === 0).length;
  const art = r.out_dirs.reduce((n, d) => n + d.files.length, 0);
  sum.push(spec.key + "_" + arm + " found=" + r.commands_found_count + " rows=" + r.rows.length +
    " rc0=" + ok + " artifacts=" + art + " claim=" + r.doc_claim.met);
}
console.log("[MEASURE:" + MODE + "] " + sum.join(" | "));