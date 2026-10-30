// r291b execution-level A/B harness, single skill mcp-builder (requirement 6 reading face).
// Pure mechanics; every judgement is derived from the RAW rows it stores, and check_r291b.py
// re-derives them a second time from the same raw file:
//  1. arm text = git object in the read-only managed root D:/global_skills (negative control 1
//     substitutes a file instead); A = 79862372^ (= BASE e64c17d3, the last commit touching
//     mcp-builder/SKILL.md before the R312 re-outfit commit), B = 79862372;
//  2. the command set is whatever the TRACKED r285 extractor finds in THAT arm text, so
//     commands_found keeps the r285/r281 denominator and the reading stays comparable. Nothing
//     is hand picked: an extracted literal with no spec row stops the run, and a spec row the arm
//     text does not contain is skipped for that arm (that is how the B-only codemod row vanishes
//     when control 1 swaps the B text for the A text);
//  3. one operative argv per primary row (argv_resolved when declared, else argv_literal), hand
//     listed in r291_cmds.json; doc placeholders resolve to fixtures written BEFORE the row runs
//     so a fixture can never be counted as a produced artifact;
//  4. each arm runs in its own wiped tree and every rows output dirs are snapshotted immediately
//     before that row, so one arms leftovers cannot be counted for the other (r283 contamination);
//  5. aux rows (kind aux) are evidence only: counted=false, primary=false, never in
//     commands_found / runnable / rc_zero / artifacts (r285 variant_rows caliber).
import fs from "node:fs";
import path from "node:path";
import url from "node:url";
import crypto from "node:crypto";
import cp from "node:child_process";
const NL = String.fromCharCode(10);
// r299 移植：R285 是本仓已跟踪的兄弟目录（git ls-files _repro/r285l/ 命中），故按本文件位置派生，
// 不写死绝对路径 —— 写死等于把「谁的机器」编进判据。D285_OVERRIDE 只用于异布局机器显式指路。
const HERE_M = path.dirname(url.fileURLToPath(import.meta.url));
const R285 = process.env.D285_OVERRIDE
  || path.resolve(HERE_M, "..", "..", "r285l");
const common = await import(url.pathToFileURL(R285 + "/r285_common.mjs").href);
const TMP = path.resolve(path.dirname(url.fileURLToPath(import.meta.url)), "..");
const SKILL = "mcp-builder";
const REL = SKILL + "/SKILL.md";
const AFTER_REF = "79862372";
const BEFORE_REF = "79862372^";
const BASE_COMMIT = "e64c17d366d660764b3dd6faf3fcd80be887fec7";
const MODE = process.argv[2] || "run";
const SUB_FILE = process.argv[3] || "";
const TAG = MODE === "sub" ? "sub" : "run";
const SPEC285 = JSON.parse(fs.readFileSync(R285 + "/r285_cmds.json", "utf8"));
const CMD = JSON.parse(fs.readFileSync(TMP + "/harness/r291_cmds.json", "utf8"));
// ENV 必须是显式白名单：判据要可复现，不能把调用者的整个环境带进一次测量。
// r299 移植：家目录类变量原先写死我的用户名 ⇒ 改取本机 process.env，同机取到同样的值故读数不变。
// SystemRoot 保留常量，因为被测命令行需要它且在 Windows 上各处同值。
const ENV = { PATH: SPEC285.ENV_PATH, SystemRoot: process.env.SystemRoot || "C:/windows",
  APPDATA: process.env.APPDATA, LOCALAPPDATA: process.env.LOCALAPPDATA,
  USERPROFILE: process.env.USERPROFILE, HOME: process.env.HOME || process.env.USERPROFILE,
  TEMP: process.env.TEMP || process.env.LOCALAPPDATA + "/Temp",
  TMP: process.env.TMP || process.env.TEMP || process.env.LOCALAPPDATA + "/Temp",
  PYTHONIOENCODING: "utf8" };
const TOK = { "{NODE_EXE}": SPEC285.NODE_EXE, "{NPMCLI}": SPEC285.NPMCLI,
  "{NPXCLI}": SPEC285.NPXCLI, "{PY}": common.PY };
function fill(s) { let v = String(s); for (const k of Object.keys(TOK)) v = v.split(k).join(TOK[k]); return v; }
function sha(buf) { return crypto.createHash("sha256").update(buf).digest("hex"); }
function snap(dir) { const m = {}; for (const f of common.listFiles(dir)) m[f.rel] = f.bytes; return m; }
function fresh(before, dir) {
  const out = [];
  for (const f of common.listFiles(dir)) if (!(f.rel in before)) out.push({ rel: f.rel, bytes: f.bytes });
  return out.sort((a, b) => a.rel.localeCompare(b.rel));
}
function operative(row) { return row.argv_resolved || row.argv_literal; }

// --- port isolation between arms (R291-B2 fix; see the comment block above runRow) ---
const INSPECTOR_PORTS = [6274, 6275, 6276, 6277, 6278];
function pidImage(pid) {
  try {
    const o = cp.execFileSync("tasklist", ["/FI", "PID eq " + pid, "/NH"], { encoding: "utf8" });
    return o.split(NL).filter((x) => x.indexOf(" " + pid + " ") >= 0).join("");
  } catch (e) { return ""; }
}
function freePorts(tag) {
  // netstat gives TCP LISTENING sockets with owning pid; only node/python images we may have
  // orphaned are killed, and never our own process or its parents.
  const killed = []; const skipped = [];
  let text = "";
  try { text = cp.execFileSync("netstat", ["-ano", "-p", "TCP"], { encoding: "utf8", maxBuffer: 32 * 1024 * 1024 }); }
  catch (e) { return { tag: tag, error: String(e && e.code || e), killed: [], skipped: [] }; }
  const pids = new Set();
  for (const line of text.split(NL)) {
    if (line.indexOf("LISTENING") < 0) continue;
    const m = line.match(/:(\d+)\s+.*LISTENING\s+(\d+)\s*$/);
    if (!m) continue;
    if (INSPECTOR_PORTS.indexOf(parseInt(m[1], 10)) >= 0) pids.add(m[2]);
  }
  for (const pid of pids) {
    const img = pidImage(pid);
    const mine = String(pid) === String(process.pid);
    if (mine || !/node.exe|pythonw.exe|python.exe/i.test(img)) { skipped.push({ pid: pid, image: img.trim().slice(0, 40) }); continue; }
    let rc = null;
    try { cp.execFileSync("taskkill", ["/PID", pid, "/T", "/F"], { encoding: "utf8" }); rc = 0; } catch (e) { rc = String(e && e.status); }
    killed.push({ pid: pid, image: img.trim().slice(0, 40), taskkill_rc: rc });
  }
  return { tag: tag, killed: killed, skipped: skipped };
}
function armText(arm) {
  if (arm === "B" && SUB_FILE) {
    const buf = fs.readFileSync(SUB_FILE);
    return { ref: "SUBSTITUTED:" + path.basename(SUB_FILE), bytes: buf.length,
      sha12: sha(buf).slice(0, 12), text: buf.toString("utf8"), substituted: true };
  }
  const ref = arm === "A" ? BEFORE_REF : AFTER_REF;
  const buf = common.gitShowBuf(ref, REL);
  fs.writeFileSync(TMP + "/texts/" + TAG + "_" + arm + "_SKILL.md", buf);
  return { ref: ref, bytes: buf.length, sha12: sha(buf).slice(0, 12),
    text: buf.toString("utf8"), substituted: false };
}

function materialise(root) {
  fs.mkdirSync(TMP + "/texts", { recursive: true });
  common.wipeDir(root);
  for (const d of ["py_work", "codemod_proj"]) fs.mkdirSync(path.join(root, d), { recursive: true });
  const Q = String.fromCharCode(34);
  // fixture at the doc placeholder name, Python MCP-server shaped (written before any row runs)
  fs.writeFileSync(path.join(root, "py_work", "your_server.py"), [
    "from dataclasses import dataclass",
    "from typing import Any",
    "",
    "",
    "@dataclass",
    "class User:",
    "    id: str",
    "    name: str",
    "",
    "USERS = [User(" + Q + "u1" + Q + ", " + Q + "John Doe" + Q + "), User(" + Q + "u2" + Q + ", " + Q + "Johnny Appleseed" + Q + ")]",
    "",
    "",
    "def search_users(query: str, limit: int = 5) -> dict[str, Any]:",
    "    hits = [u.__dict__ for u in USERS if query.lower() in u.name.lower()][:limit]",
    "    return {" + Q + "users" + Q + ": hits, " + Q + "total" + Q + ": len(hits)}",
    "",
    "",
    "def get_user(user_id: str) -> dict[str, Any]:",
    "    for u in USERS:",
    "        if u.id == user_id:",
    "            return u.__dict__",
    "    raise KeyError(" + Q + "no such user" + Q + ")",
    ""].join("\n"));
  // v1-shaped project for the doc codemod `.` operand (B arm only)
  fs.writeFileSync(path.join(root, "codemod_proj", "package.json"), JSON.stringify({
    name: "r291-fixture", private: true, version: "0.0.0",
    dependencies: { "@modelcontextprotocol/sdk": "^1.0.0" } }, null, 2));
  fs.writeFileSync(path.join(root, "codemod_proj", "src_server.ts"), [
    "import { McpServer } from " + Q + "@modelcontextprotocol/sdk/server/mcp.js" + Q + ";",
    "import { StdioServerTransport } from " + Q + "@modelcontextprotocol/sdk/server/stdio.js" + Q + ";",
    "",
    "const server = new McpServer({ name: " + Q + "fixture" + Q + ", version: " + Q + "0.0.0" + Q + " });",
    "server.tool(" + Q + "add" + Q + ", { a: { type: " + Q + "number" + Q + " }, b: { type: " + Q + "number" + Q + " } },",
    "  async ({ a, b }) => ({ content: [{ type: " + Q + "text" + Q + ", text: String(a + b) }] }));",
    "",
    "export { server };", ""].join("\n"));
  return root;
}

function runRow(row, root) {
  const cwd = fill(row.cwd).split("{ARM}").join(root);
  fs.mkdirSync(cwd, { recursive: true });
  const argv = operative(row).map((a) => fill(a).split("{ARM}").join(root));
  const before = {};
  for (const d of row.output_dirs) before[d] = snap(path.join(root, d));
  const rewrite = row.predicate && row.predicate.rewrite_file
    ? path.join(cwd, row.predicate.rewrite_file) : null;
  const rb = rewrite && fs.existsSync(rewrite) ? fs.readFileSync(rewrite) : null;
  const r = common.runOne(argv, { cwd: cwd, timeout: row.timeout_ms, env: ENV });
  const ra = rewrite && fs.existsSync(rewrite) ? fs.readFileSync(rewrite) : null;
  const art = [];
  for (const d of row.output_dirs) for (const f of fresh(before[d], path.join(root, d))) art.push({ dir: d, rel: f.rel, bytes: f.bytes });
  const pred = {};
  if (row.predicate) {
    if (row.predicate.banner_substring) pred.banner = (r.stdout_tail || "").indexOf(row.predicate.banner_substring) >= 0;
    if (row.predicate.artifact_suffix) pred.artifact = art.some((f) => f.rel.endsWith(row.predicate.artifact_suffix));
    if (row.predicate.usage_substring) pred.usage = (r.stdout_tail || "").indexOf(row.predicate.usage_substring) >= 0;
    if (rewrite) {
      const txtA = ra ? ra.toString("utf8") : "";
      pred.gained = txtA.indexOf(row.predicate.must_gain) >= 0;
      pred.kept_away = txtA.indexOf(row.predicate.must_lose) < 0;
      pred.rewrite_met = pred.gained && pred.kept_away;
      pred.bytes_before = rb ? rb.length : null;
      pred.bytes_after = ra ? ra.length : null;
      pred.sha12_before = rb ? sha(rb).slice(0, 12) : null;
      pred.sha12_after = ra ? sha(ra).slice(0, 12) : null;
      const pj = path.join(cwd, "package.json");
      if (fs.existsSync(pj)) { const s = fs.readFileSync(pj).toString("utf8");
        pred.manifest_has_v2 = s.indexOf("@modelcontextprotocol/server") >= 0;
        pred.manifest_drops_v1 = s.indexOf("@modelcontextprotocol/sdk") < 0; }
    }
  }
  return { id: row.id, literal: row.literal, kind: row.kind,
    primary: row.kind !== "aux", counted: row.counted !== false,
    cwd: cwd, operative_argv: argv, argv_form: row.argv_resolved ? "resolved" : "literal",
    rc: r.rc, spawn_error: r.spawn_error, signal: r.signal,
    stdout_bytes: r.stdout_bytes, stderr_bytes: r.stderr_bytes,
    stdout_tail: (r.stdout_tail || "").slice(-500), stderr_tail: (r.stderr_tail || "").slice(-300),
    artifacts: art, predicate: pred, requires_rc_zero: row.requires_rc_zero === true,
    external_account: row.external_account === true, declared_runnable: row.runnable === true,
    placeholder_resolved: row.placeholder_resolved === true, timeout_ms: row.timeout_ms };
}

const out = { mode: MODE, skill: SKILL, rel: REL, before_ref: BEFORE_REF, after_ref: AFTER_REF,
  base_commit: BASE_COMMIT, arm_text: {}, raw_rows: {}, anti_cherry_pick: {}, port_cleanup: [] };
for (const arm of ["A", "B"]) {
  out.port_cleanup.push(freePorts("before_" + arm));
  const t = armText(arm);
  out.arm_text[arm] = t;
  const ex = common.extractCommands(t.text);
  const literals = ex.found.map((x) => x.literal);
  out.anti_cherry_pick[arm] = { extracted: literals, queries_dropped_by_r285_caliber: ex.queries.map((x) => x.literal),
    orphan_literals_without_spec_row: literals.filter((l) => !CMD.rows.some((r) => r.literal === l)) };
  if (out.anti_cherry_pick[arm].orphan_literals_without_spec_row.length) {
    throw new Error("ANTI-CHERRY-PICK " + arm + ": arm text yields a literal with no hand-listed row: " +
      out.anti_cherry_pick[arm].orphan_literals_without_spec_row.join(" ;; "));
  }
  const primary = CMD.rows.filter((r) => r.kind !== "aux" && r.arms.indexOf(arm) >= 0 && literals.indexOf(r.literal) >= 0);
  const aux = CMD.rows.filter((r) => r.kind === "aux" && r.arms.indexOf(arm) >= 0);
  const skipped = CMD.rows.filter((r) => r.kind !== "aux" && r.arms.indexOf(arm) >= 0 && literals.indexOf(r.literal) < 0).map((r) => r.id);
  const root = materialise(path.join(TMP, "work", TAG, SKILL + "_" + arm));
  const rows = [];
  for (const row of primary) rows.push(runRow(row, root));
  for (const row of aux) rows.push(runRow(row, root));
  out.raw_rows[arm] = { arm_dir_rel: "work/" + TAG + "/" + SKILL + "_" + arm,
    extracted_literals: literals, spec_rows_skipped_for_this_arm: skipped, rows: rows };
}
out.port_cleanup.push(freePorts("after_all_arms"));
fs.mkdirSync(TMP + "/harness/results", { recursive: true });
const rawPath = TMP + "/harness/results/" + TAG + "_raw.json";
fs.writeFileSync(rawPath, JSON.stringify(out, null, 1));
console.log("WROTE " + rawPath + " sha12=" + sha(fs.readFileSync(rawPath)).slice(0, 12));
for (const arm of ["A", "B"]) {
  const rr = out.raw_rows[arm];
  console.log("ARM " + arm + " text=" + out.arm_text[arm].sha12 + " found=" + rr.extracted_literals.length +
    " skipped=" + JSON.stringify(rr.spec_rows_skipped_for_this_arm));
  for (const row of rr.rows) console.log("   " + row.id + " " + row.argv_form + " rc=" + JSON.stringify(row.rc) +
    " sig=" + row.signal + " art=" + row.artifacts.length + " pred=" + JSON.stringify(row.predicate));
}
