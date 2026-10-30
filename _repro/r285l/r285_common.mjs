import url from 'node:url';
import fs from "node:fs";
import path from "node:path";
import cp from "node:child_process";
import crypto from "node:crypto";

// R285-L shared layer: arm text fetch, literal command extraction, isolated run dirs.
// Mechanical only. No whitespace splitting of doc text: every argv below is hand listed.
const ROOT = path.resolve(path.dirname(url.fileURLToPath(import.meta.url)), '..', '..');
const T = ROOT + "/_repro/r285l";
export const WORK = T + "/work";
export const TEXTS = T + "/texts";
export const RES = T + "/results";
export const PY = "C:/Users/37533/.workbuddy/binaries/python/envs/default/Scripts/python.exe";
export const GB = "C:/Program Files/Git/bin/bash.exe";
export const REPO = "D:/global_skills";
export const NL = String.fromCharCode(10);
export const BT = String.fromCharCode(96);
export const SPECS = [
  { key: "tdd", skill: "test-driven-development", dir: "test-driven-development",
    rel: "test-driven-development/SKILL.md", before_ref: "079b91f3~1", after_ref: "079b91f3",
    claim: "Verify RED then Verify GREEN: the worked example test must fail before the feature exists and pass after it does." },
  { key: "fs", skill: "frontend-slides", dir: "frontend-slides",
    rel: "frontend-slides/SKILL.md", before_ref: "3681df5e", after_ref: "89efb3e6",
    claim: "Phase 4 declares PPTX extraction to slide titles, content summaries and image counts; Phase 6B declares an HTML to PDF deliverable." },
];

export function sha(buf) { return crypto.createHash("sha256").update(buf).digest("hex"); }
export function gitShowBuf(ref, rel) {
  return cp.execFileSync("git", ["-C", REPO, "show", ref + ":" + rel], { maxBuffer: 128 * 1024 * 1024 });
}
export function treeList(ref, dir) {
  const out = cp.execFileSync("git", ["-C", REPO, "ls-tree", "-r", "--name-only", ref, "--", dir],
    { encoding: "utf8", maxBuffer: 128 * 1024 * 1024 });
  return out.split(NL).filter(Boolean).map((x) => x.slice(dir.length + 1));
}
export function wipeDir(d) {
  fs.rmSync(d, { recursive: true, force: true });
  fs.mkdirSync(d, { recursive: true });
}
export function loadArm(spec, arm, overrideFile) {
  if (overrideFile) {
    const buf = fs.readFileSync(overrideFile);
    return { tag: "SUB_" + spec.key + "_" + arm, ref: "SUBSTITUTED:" + path.basename(overrideFile),
      bytes: buf.length, sha12: sha(buf).slice(0, 12), text: buf.toString("utf8"), substituted: true };
  }
  const ref = arm === "A" ? spec.before_ref : spec.after_ref;
  const buf = gitShowBuf(ref, spec.rel);
  fs.writeFileSync(path.join(TEXTS, spec.key + "_" + arm + ".md"), buf);
  return { tag: spec.key + "_" + arm, ref, bytes: buf.length, sha12: sha(buf).slice(0, 12),
    text: buf.toString("utf8"), substituted: false };
}

const TRIGS = ["python3", "python", "py", "bash scripts", "npm test", "pytest",
  "cargo test", "pip install", "npx", "open [", "uv run", "node scripts"].map((s) => s.replace(/[.*+?^${}()|[\]\\]/g, (c) => "\\" + c));
const TRIM_CUTS = [String.fromCharCode(96), "|", " (", "(", ",", ";", " —", " and ", " then", ")", ":", ". ", "{"];
function escRe(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, (c) => "\\" + c); }
function cutProse(s) {
  let best = s.length;
  for (const c of TRIM_CUTS) { const i = s.indexOf(c); if (i >= 0 && i < best) best = i; }
  return s.slice(0, best).replace(/\s+$/, "").replace(/[.,;:]+$/, "").trim();
}
export function extractCommands(textIn) {
  const text = textIn.split(String.fromCharCode(96)).join("");
  const lines = text.split(NL);
  const spans = [];
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].replace(/[`$]/g, " ");
    for (const t of TRIGS.map(escRe)) {
      const rx = new RegExp("(^|[^\\w.\\-/])(" + t + ")(?![\\w\\-])(\\s[^\\n]*)?", "g");
      let m;
      while ((m = rx.exec(line)) !== null) {
        const start = m.index + m[1].length;
        const raw = line.slice(start);
        const lit = cutProse(raw);
        if (lit.length > 2) spans.push({ literal: lit, line: i + 1, start, len: lit.length });
        rx.lastIndex = start + t.length;
      }
    }
  }
  // drop spans fully contained in a longer span on the same line
  const keep = spans.filter((s) => !spans.some((o) => o !== s && o.line === s.line &&
    o.start <= s.start && o.start + o.len >= s.start + s.len && o.len > s.len));
  const first = new Map();
  for (const s of keep) if (!first.has(s.literal)) first.set(s.literal, s.line);
  const all = [];
  for (const [literal, line] of first) all.push({ literal, line });
  all.sort((a, b) => a.line - b.line || a.literal.localeCompare(b.literal));
  const isQuery = (l) => /(^|\s)(--help|--version|-h)(\s|$)/.test(l) || l.endsWith("whoami") ||
    l.endsWith("vercel login");
  return { found: all.filter((x) => !isQuery(x.literal)),
    queries: all.filter((x) => isQuery(x.literal)) };
}
export function runOne(argv, opts) {
  const o = opts || {};
  const r = cp.spawnSync(argv[0], argv.slice(1), {
    cwd: o.cwd, timeout: o.timeout || 120000, encoding: "utf8", maxBuffer: 64 * 1024 * 1024,
    input: "", env: o.env || process.env, windowsVerbatimArguments: false,
  });
  const errCode = r.error ? (r.error.code || String(r.error.message)) : null;
  const outBuf = typeof r.stdout === "string" ? Buffer.from(r.stdout, "utf8") : (r.stdout || Buffer.alloc(0));
  const errBuf = typeof r.stderr === "string" ? Buffer.from(r.stderr, "utf8") : (r.stderr || Buffer.alloc(0));
  return {
    rc: errCode === "ENOENT" ? "ENOENT" : (r.signal ? "SIGNAL:" + r.signal : r.status),
    spawn_error: errCode, signal: r.signal || null,
    stdout_bytes: outBuf.length, stderr_bytes: errBuf.length,
    stdout_tail: outBuf.toString("utf8").slice(-1200),
    stderr_tail: errBuf.toString("utf8").slice(-1200),
  };
}
export function listFiles(dir) {
  const acc = [];
  if (!fs.existsSync(dir)) return acc;
  const walk = (d) => {
    for (const e of fs.readdirSync(d, { withFileTypes: true })) {
      const p = path.join(d, e.name);
      if (e.isDirectory()) walk(p);
      else acc.push({ rel: path.relative(dir, p).split(path.sep).join("/"),
        bytes: fs.statSync(p).size });
    }
  };
  walk(dir);
  return acc.sort((a, b) => a.rel.localeCompare(b.rel));
}