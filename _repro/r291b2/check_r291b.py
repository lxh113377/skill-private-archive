# -*- coding: utf-8 -*-
"""R291-B2 执行级 A/B 判据件（唯一判据：重算 + 自证 + 两腿负控）。

为什么长这样（逻辑走函数内行级注释，本段只说「为什么」）：
  1. 只读生证据，不读自己上一轮的结论：所有数字从 harness 落盘的
     harness/results/run_raw.json（每行的 rc / artifacts / predicate）现推，再与 out.json 里
     已写死的读数逐字段比对。交付件被手改必当场红 —— 负控 2 就是拿这条牙打的。
  2. 口径不是本件自立的：caliber_note 的基底文本在运行时直接取
     06-benchmark/r285_exec_commands_ab.json（对齐权威，逐字复用，不另立触发词），本件只覆盖
     mcp-builder 行特有的几条；commands_found 的分母来自受管的 r285 抽取器
     _repro/r285l/r285_common.mjs extractCommands（由 harness 调用）⇒ 与 r285 那 3 件同口径可比。
  3. 基准坑做成牙而不是抄表：改前/改后 = 受管根 D:/global_skills 的 79862372~1 与 79862372
     两版 mcp-builder/SKILL.md blob。每次校验都重跑 git 核 blob 与字节，并三方对拍：
     BASE（e64c17d3，最后一个真动该文件的提交）是否等于 ~1，他会话提交 079b91f3 有没有动过
     该文件（brief 点名的坑：动过则 ~1 不等于改前态）。
  4. 每次 emit 前重算全表并打 [PRE-EMIT]，落盘后再重算比对并打 [CONSISTENCY] PASS/FAIL；
     末行恒为 [EXEC-AB-B] rows=... commands_ok=.../... artifacts_before=... artifacts_after=...
  5. 写面纪律：只写 _repro/r291b2；_temp/r291b 一律只读（[RO-DRIFT] 腿按开工指纹复扫 sha，
     证明本轮没改、没改名、没删）；受管根只跑 git 只读子命令；不写仓内其它文件；禁 git 写；
     不跑 run_gates.py（第 114/115 门只扫 06-benchmark/*.json 的出处字段；本件 r299 起已入 _repro 跟踪面册）。

用法（绝对路径见 out.json 的 judge_invocation）：
  python -B check_r291b.py                 重算并校验已存在的 out.json（默认）
  python -B check_r291b.py --emit          由生证据重算写出 out.json，写完立刻再校一遍
  python -B check_r291b.py --negctl2       负控 2：篡改 rc_zero 写进副本重算，副本用完即删
期望末行：[EXEC-AB-B] rows=1 commands_ok=2/3 artifacts_before=1 artifacts_after=1
"""
import argparse
import hashlib
import io
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
# 两个「取值命令」里用的解释器路径（r299 移植）。本仓 AGENTS.md 规定首选 managed venv 的规范写法是
# %USERPROFILE%/.workbuddy/... ⇒ 用 ~ 展开而非写死用户名：同机展开后与旧字面量逐字相同（provenance
# 可解析性与历史读数都不变），异机自动指向那台机器自己的 managed venv。
PYEXE_DOC = os.path.expanduser("~/.workbuddy/binaries/python/envs/default/Scripts/python.exe")
# node 没有规范安装位置 ⇒ 先 which，取不到回落本机既有路径（宁可留一个可解析默认，不静默变空串）。
NODE_DOC = __import__("shutil").which("node") or "C:/Program Files/nodejs/node.exe"
NL = chr(10)
# 受管根 = 本项目全部判据的对象（与 _repro/r285l/r285_common.mjs 的 REPO 同一约定）。保留默认值
# 是因为历史读数以它为基准，口径不许随搬迁漂；换机时用 DSH_MANAGED_SKILLS 显式注入。
MANAGED = os.environ.get("DSH_MANAGED_SKILLS") or "D:/global_skills"
REL = "mcp-builder/SKILL.md"
BEFORE_REF = "79862372~1"
AFTER_REF = "79862372"
BASE_COMMIT = "e64c17d366d660764b3dd6faf3fcd80be887fec7"
XTOUCH_COMMIT = "079b91f3"
ROOT_SELF = os.path.dirname(os.path.dirname(HERE))
R285_FACE = os.path.join(ROOT_SELF, "06-benchmark", "r285_exec_commands_ab.json").replace(os.sep, "/")
# r299 搬迁修正（Lead 改的，理由见 out.json.readonly_check.relocated_note）：本件原写在 _temp/ 下，
# 只读原件目录就是同级 ../r291b；搬到 _repro/ 后同级不存在，故按候选顺序取第一个存在的目录。
# 两个候选都不存在（例如在干净 clone 里）时记 skipped 而非 problem —— 「拿不到样本」不等于「有人改了
# 只读面」（R247 的反向形态：不许把取不到判成违规）。真在位时必须照旧逐文件核 sha。
RO_CANDIDATES = [os.path.join(os.path.dirname(HERE), "r291b"),
                 os.path.join(os.path.dirname(os.path.dirname(HERE)), "_temp", "r291b")]
RO_DIR = next((p for p in RO_CANDIDATES if os.path.isdir(p)), RO_CANDIDATES[0])
EVIDENCE_DEFAULT = os.path.join(HERE, "harness", "results", "run_raw.json")
SUB_EVIDENCE_DEFAULT = os.path.join(HERE, "harness", "results", "sub_raw.json")
OUT_DEFAULT = os.path.join(HERE, "out.json")
CODEMOD_LIT = "npx @modelcontextprotocol/codemod@latest v1-to-v2"
PYC_LIT = "python -m py_compile your_server.py"
INSP_LIT = "npx @modelcontextprotocol/inspector"
NUM_FIELDS = ["commands_found", "runnable", "blocked_not_runnable", "needs_external_account",
              "rc_zero", "placeholder_unresolved", "doc_claim_met", "executions", "variant_executions"]


def caliber():
    # 基底逐字取 r285 面件（读不到就停，禁止凭记忆复述口径），再覆盖本行特有的形状说明。
    if not os.path.isfile(R285_FACE):
        raise SystemExit("[CALIBER] 对齐权威件缺失: " + R285_FACE)
    base = dict(json.loads(io.open(R285_FACE, encoding="utf-8").read())["caliber_note"])
    out = {}
    for k in base:
        out[k] = str(base[k])
    # order matters: stash the r285 original first, then overwrite with the mcp-builder claim
    r285_doc_claim = out["doc_claim_met"]
    out["doc_claim_met_r285_original"] = r285_doc_claim
    out["doc_claim_met"] = ("binary. mcp-builder A: the 3.2 Build and Test Python verify (" + PYC_LIT +
                            ") must return rc=0 and persist the compiled artifact. mcp-builder B: everything"
                            " A claims PLUS the B-only codemod literal (" + CODEMOD_LIT + ") must run rc=0 and"
                            " actually rewrite a v1-shaped project to v2 (source gained"
                            " @modelcontextprotocol/server, lost the v1 sdk server import, manifest swapped).")
    out["rc_zero"] = out["rc_zero"] + " In this row one never-exiting service row (the inspector) is excluded"
    out["blocked_not_runnable"] = ("commands_found items the machine could not execute (missing toolchain / ENOENT /"
                                   " declared runnable=false). Never in runnable, rc_zero or artifacts, and never"
                                   " counted as a doc defect.")
    out["needs_external_account"] = ("commands that reach a third-party account gate before producing anything."
                                     " Counted in commands_found, excluded from runnable / rc_zero / artifacts,"
                                     " and never counted as a doc defect: this run creates no external credential.")
    out["service_rows_never_exit"] = ("NEW in this row (r285 had no such shape): " + INSP_LIT +
                                      " is an interactive UI that by design never returns, so its operative rc is"
                                      " a timeout signal (SIGNAL:SIGTERM) on both arms. It counts in"
                                      " commands_found and runnable, is excluded from rc_zero by the cmdspec"
                                      " (requires_rc_zero=false), and its evidence is the start-up banner predicate."
                                      " That is what keeps this row from inflating the gain.")
    out["port_isolation"] = ("NEW: the surviving harness did not free the inspector ports between arms, so arm A"
                             " SIGTERM-leftover server made arm B read rc=1 with MCP Inspector PORT IS IN USE at"
                             " http://127.0.0.1:6274 - the r283 contamination one layer down (process, not"
                             " directory). The relocated harness kills only leftover node/python pids holding"
                             " 6274-6278 before each arm and records every kill in port_cleanup.")
    out["not_measured"] = ("executability and persistence only. This row does not measure the business quality of a"
                           " generated MCP server, does not judge whether the codemod output is idiomatic, and does"
                           " not re-run the r285 trio.")
    return out


def sha256(buf):
    return hashlib.sha256(buf).hexdigest()


def read_bytes(p):
    with io.open(p, "rb") as f:
        return f.read()


def git(args):
    # 只读取证：受管根上只跑 rev-parse / cat-file / show / log，绝不写
    p = subprocess.run(["git", "-C", MANAGED] + list(args), capture_output=True, timeout=90)
    return p.returncode, p.stdout.decode("utf-8", "replace").strip(), p.stderr.decode("utf-8", "replace").strip()


def ref_table():
    # 每个点都是现跑的：改前 ref、改后 ref、BASE 提交、他会话提交探针、现头、改后的直接父
    rows = []
    for point, ref, meaning in [
        ("before", BEFORE_REF, "brief 指定的改前 ref"),
        ("after", AFTER_REF, "R312 换装提交（改后）"),
        ("base_last_touch", BASE_COMMIT, "最后一个真动 mcp-builder/SKILL.md 的提交"),
        ("other_session_commit", XTOUCH_COMMIT, "他会话提交（079b91f3 坑位探针）"),
        ("head", "HEAD", "现头（证明改后无后续覆盖）"),
    ]:
        rc, out, err = git(["rev-parse", ref + ":" + REL])
        blob = out if rc == 0 else None
        size = None
        if blob:
            rc2, o2, e2 = git(["cat-file", "-s", blob])
            size = int(o2) if rc2 == 0 and o2.isdigit() else None
        rows.append({"point": point, "ref": ref, "meaning": meaning, "blob": blob, "bytes": size,
                     "git_rc": rc, "git_err": (err or "")[:120]})
    rc, out, e3 = git(["log", "--format=%H", "-8", "--", REL])
    hist = [x for x in out.split(NL) if x] if rc == 0 else []
    rc, par, e4 = git(["rev-parse", AFTER_REF + "^"])
    rows.append({"point": "after_first_parent", "ref": AFTER_REF + "^", "meaning": "改后提交的直接父（面外提交）",
                 "blob": None, "bytes": None, "git_rc": rc, "commit": par})
    return rows, hist


def blocked(row):
    # toolchain missing / declared not runnable -> blocked_not_runnable: in denominator,
    # never in runnable / rc_zero / artifacts, and never a doc defect.
    if row.get("declared_runnable") is False:
        return True
    se = str(row.get("spawn_error") or "")
    rc = row.get("rc")
    return se in ("ENOENT", "ENOEXEC") or rc in ("ENOENT", "ENOEXEC")


def derive(arm_ev):
    # one arm readings, derived only from evidence rows. primary+counted rows count;
    # aux/variant rows are evidence only and never enter any count.
    rows = [r for r in arm_ev["rows"] if r.get("primary") is not False and r.get("counted") is not False]
    variants = [r for r in arm_ev["rows"] if r.get("primary") is False]
    found = list(arm_ev["extracted_literals"])
    by = {}
    for r in rows:
        by[r["literal"]] = r
    ext = set(l for l, r in by.items() if r.get("external_account") is True)
    blk = set(l for l, r in by.items() if blocked(r) and r.get("external_account") is not True)
    # runnable = really executed, and not blocked by toolchain / external account gate
    run_ids = set(l for l, r in by.items() if not blocked(r) and r.get("external_account") is not True)
    # rc_zero counts only rows whose normal state must be 0; never-exiting service rows are
    # excluded by the cmdspec flag requires_rc_zero=false
    rc0 = set(l for l, r in by.items() if r.get("requires_rc_zero") is True and r.get("rc") == 0
              and r.get("external_account") is not True and not blocked(r))
    unresolved = set(l for l, r in by.items() if r.get("placeholder_resolved") is not True)
    arts = sorted(set(a["dir"] + "/" + a["rel"] + " (" + str(a["bytes"]) + "B)"
                      for r in rows for a in (r.get("artifacts") or [])))
    py = by.get(PYC_LIT)
    insp = by.get(INSP_LIT)
    code = by.get(CODEMOD_LIT)
    # doc claim face follows what THIS arm text actually declares
    a_met = bool(py and py.get("rc") == 0 and (py.get("predicate") or {}).get("artifact") is True)
    if code is None:
        met = a_met
        claim_face = "A: python verify only"
    else:
        pd = code.get("predicate") or {}
        met = bool(a_met and code.get("rc") == 0 and pd.get("rewrite_met") is True
                   and pd.get("manifest_has_v2") is True and pd.get("manifest_drops_v1") is True)
        claim_face = "B: python verify + B-only codemod rewrite"
    sub = {
        "claim_face": claim_face,
        "inspector_banner": bool((insp.get("predicate") or {}).get("banner")) if insp else None,
        "inspector_rc": insp.get("rc") if insp else None,
        "py_compile_rc": py.get("rc") if py else None,
        "pyc_persisted": bool((py or {}).get("artifacts")),
        "codemod_present_in_arm": code is not None,
        "codemod_rc": code.get("rc") if code else None,
        "codemod_rewrite_met": (code.get("predicate") or {}).get("rewrite_met") if code else None,
        "codemod_manifest_has_v2": (code.get("predicate") or {}).get("manifest_has_v2") if code else None,
        "codemod_manifest_drops_v1": (code.get("predicate") or {}).get("manifest_drops_v1") if code else None,
        "codemod_bytes_before": (code.get("predicate") or {}).get("bytes_before") if code else None,
        "codemod_bytes_after": (code.get("predicate") or {}).get("bytes_after") if code else None,
        "commands_found_literal_set": sorted(found),
    }
    return {
        "commands_found": len(found),
        "runnable": len(run_ids),
        "blocked_not_runnable": len(blk),
        "needs_external_account": len(ext),
        "rc_zero": len(rc0),
        "placeholder_unresolved": len(unresolved),
        "persisted_artifacts": arts,
        "doc_claim_met": "Y" if met else "N",
        "doc_claim_sub": sub,
        "executions": len(rows),
        "variant_executions": len(variants),
    }


def compare(stored, fresh, label, problems):
    # every number written into the deliverable must equal a fresh recomputation;
    # artifacts are compared by length AND by set so a swapped path cannot pass.
    for f in NUM_FIELDS:
        if f == "doc_claim_sub":
            continue
        if stored.get(f) != fresh.get(f):
            problems.append("MISMATCH " + label + "." + f + ": stored="
                            + json.dumps(stored.get(f), ensure_ascii=False)
                            + " recomputed=" + json.dumps(fresh.get(f), ensure_ascii=False))
    sa = stored.get("persisted_artifacts") or []
    fa = fresh.get("persisted_artifacts") or []
    if len(sa) != len(fa):
        problems.append("MISMATCH " + label + ".persisted_artifacts.length: stored=" + str(len(sa))
                        + " recomputed=" + str(len(fa)))
    elif sorted(sa) != sorted(fa):
        problems.append("MISMATCH " + label + ".persisted_artifacts.set")
    ss = stored.get("doc_claim_sub") or {}
    fsx = fresh.get("doc_claim_sub") or {}
    for k in sorted(set(list(ss.keys()) + list(fsx.keys()))):
        if ss.get(k) != fsx.get(k):
            problems.append("MISMATCH " + label + ".doc_claim_sub." + k + ": stored="
                            + json.dumps(ss.get(k), ensure_ascii=False)
                            + " recomputed=" + json.dumps(fsx.get(k), ensure_ascii=False))


def readonly_skipped():
    """只读原件目录不可得 => 本腿未验证（必须印出来，不能静默算过）。"""
    return not os.path.isdir(RO_DIR)


def readonly_drift():
    # rescan the surviving read-only dir against the fingerprint taken at run start,
    # so "I did not touch it" is a measurement and not a claim.
    fp_path = os.path.join(HERE, "harness", "_inputs_fingerprint.json")
    if not os.path.isdir(RO_DIR):
        # 见上：无样本 => 不判红也不判绿，由 readonly_skipped() 在输出里显式标 skipped
        return []
    if not os.path.isfile(fp_path):
        return ["MISMATCH readonly: fingerprint file absent"]
    fp = json.loads(io.open(fp_path, encoding="utf-8").read())["before"]
    problems = []
    for rel in sorted(fp):
        meta = fp[rel]
        p = os.path.join(RO_DIR, *rel.split("/"))
        if not os.path.isfile(p):
            problems.append("MISMATCH readonly.missing: " + rel)
            continue
        b = read_bytes(p)
        if len(b) != meta["size"] or sha256(b)[:12] != meta["sha12"]:
            problems.append("MISMATCH readonly.sha: " + rel + " stored=" + meta["sha12"]
                            + " now=" + sha256(b)[:12])
    return problems


# keys that MUST agree when both arms read the same text. inspector rc is deliberately
# excluded: it is a never-exiting service row, so its rc depends on timeout/port timing,
# not on the doc text (the surviving harness proved that by reading rc=1 for a port clash).
NC1_SUB_KEYS = ["claim_face", "inspector_banner", "py_compile_rc", "pyc_persisted",
                "codemod_present_in_arm", "commands_found_literal_set"]


def nc1(sub_ev):
    # negative control 1: substitute the B arm text with the A one -> readings must be equal
    # field by field, and the B-only codemod row must disappear on its own.
    a = derive(sub_ev["raw_rows"]["A"])
    b = derive(sub_ev["raw_rows"]["B"])
    same_num = all(a[f] == b[f] for f in NUM_FIELDS if f != "doc_claim_sub")
    same_art = sorted(a["persisted_artifacts"]) == sorted(b["persisted_artifacts"])
    sa = a["doc_claim_sub"]
    sb = b["doc_claim_sub"]
    same_sub = all(sa.get(k) == sb.get(k) for k in NC1_SUB_KEYS)
    same_text = sub_ev["arm_text"]["A"]["sha12"] == sub_ev["arm_text"]["B"]["sha12"]
    identical = bool(same_num and same_art and same_sub and same_text)
    diff = [f for f in NUM_FIELDS if f != "doc_claim_sub" and a[f] != b[f]]
    if not same_art:
        diff.append("persisted_artifacts")
    diff = diff + [k for k in NC1_SUB_KEYS if sa.get(k) != sb.get(k)]
    if not same_text:
        diff.append("arm_text.sha12")
    return {"ran": True, "mode": sub_ev.get("mode"),
            "A_text_sha12": sub_ev["arm_text"]["A"]["sha12"],
            "B_text_sha12": sub_ev["arm_text"]["B"]["sha12"],
            "substituted_B_with": sub_ev["arm_text"]["B"]["ref"],
            "B_text_source_bytes": sub_ev["arm_text"]["B"]["bytes"],
            "readings_A": a, "readings_B": b,
            "identical": identical, "differing_fields": diff,
            "inspector_rc_A": sa.get("inspector_rc"), "inspector_rc_B": sb.get("inspector_rc"),
            "B_spec_rows_skipped_for_this_arm": sub_ev["raw_rows"]["B"]["spec_rows_skipped_for_this_arm"],
            "verdict": "PASS: identical text -> identical readings, field by field"
                      if identical else "FAIL: readings differ for identical text"}


def build_payload(ev, evidence_path, sub_ev=None):
    # assemble the deliverable from raw evidence only; totals and the last line come from
    # the same recomputation, so the file can never advertise numbers it does not hold.
    A = derive(ev["raw_rows"]["A"])
    B = derive(ev["raw_rows"]["B"])
    tab, hist = ref_table()
    gt = {}
    for x in tab:
        gt[x["point"]] = x
    row = {
        "skill": ev["skill"],
        "before_ref": BEFORE_REF, "after_ref": AFTER_REF,
        "before_blob": gt["before"]["blob"], "after_blob": gt["after"]["blob"],
        "before_bytes": gt["before"]["bytes"], "after_bytes": gt["after"]["bytes"],
        "base_commit": ev["base_commit"],
        "source": "MEASURED IN THIS RUN (R291-B2, relocated write face _repro/r291b2)",
        "doc_claim": ("SKILL.md section 3.2 Build and Test declares an executable verify surface: "
                      + PYC_LIT + " for Python servers and " + INSP_LIT + " for both languages; the "
                      "after-face additionally declares the B-only codemod literal " + CODEMOD_LIT +
                      " that migrates a v1 project to the v2 package."),
        "ref_note": ("before/after face re-measured by git on every validation (see git_ref_face): "
                     + REL + " at 79862372~1 = " + str(gt["before"]["blob"])[:12] + " ( "
                     + str(gt["before"]["bytes"]) + "B) and at 79862372 = " + str(gt["after"]["blob"])[:12]
                     + " ( " + str(gt["after"]["bytes"]) + "B). The brief 079b91f3 class of foreign "
                     "commit measured: 079b91f3:" + REL + " = " + str(gt["other_session_commit"]["blob"])[:12]
                     + " == BASE e64c17d3 => that foreign commit did NOT touch this file, so ~1 is the true "
                     "before state. HEAD = " + str(gt["head"]["blob"])[:12] + " == after => nothing overwrote "
                     "it later. Direct parent of 79862372 is " + str(gt["after_first_parent"]["commit"])[:8]
                     + " (touches other faces, not this file); previous touch of this file is "
                     + (str(hist[1])[:8] if len(hist) > 1 else "?") + "."),
        "field_caliber_local": {
            "commands_found": ("A=2 B=3 from the tracked r285 extractor on THAT arm text (before-face has only "
                               "inspector + py_compile; the codemod literal exists only in the after-face) => the "
                               "gain face is the command surface the doc newly wrote, not a hand-picked one."),
            "rc_zero": ("A=1 B=2: only rows with requires_rc_zero=true and operative rc==0 (py_compile, plus the "
                        "codemod on B). The inspector is a never-exiting service, SIGNAL:SIGTERM on both arms => "
                        "excluded from the numerator by the cmdspec, see caliber_note.service_rows_never_exit."),
            "blocked_not_runnable": ("0: npx and the managed python are both on the harness PATH, so nothing was "
                                     "missing-toolchain; no toolchain gap is disguised as a doc defect."),
            "needs_external_account": ("0: none of the three rows reaches a third-party account gate; this run "
                                       "creates no credential and does not record a 0 gain for it."),
            "placeholder_unresolved": ("0: your_server.py resolved by a fixture written before the row runs; the "
                                       "codemod dot operand by a v1-shaped fixture project => a fixture is never a "
                                       "produced artifact."),
            "persisted_artifacts": ("one per arm: py_compile persists __pycache__/your_server.cpython-313.pyc in "
                                    "that arm s own py_work. The codemod edits in place and adds no file, so its "
                                    "effect is evidenced by the rewrite predicate plus the manifest swap, never by "
                                    "artifact counting."),
            "executions": "A=2 B=3 primary rows; no variant rows in this run (variant_executions=0).",
        },
        "arms": {"A": A, "B": B},
        "arm_text": {},
        "commands_found_literals": {},
        "query_excluded": {},
        "unmatched_literals": {},
        "spec_rows_skipped_for_this_arm": {},
        "anti_cherry_pick": ("every literal the extractor hits in an arm text must have a hand-listed argv row or "
                             "the harness throws and stops (unmatched=0 here); the built-in B-only row vanishes on its own"
                             " itself when negative control 1 swaps the text => readings are not hand picked."),
        "port_cleanup": ev.get("port_cleanup"),
        "detail_rows": {},
    }
    for k in ("A", "B"):
        row["arm_text"][k] = {"ref": ev["arm_text"][k]["ref"], "bytes": ev["arm_text"][k]["bytes"],
                              "sha12": ev["arm_text"][k]["sha12"],
                              "substituted": ev["arm_text"][k]["substituted"]}
        row["commands_found_literals"][k] = ev["raw_rows"][k]["extracted_literals"]
        row["query_excluded"][k] = ev["anti_cherry_pick"][k]["queries_dropped_by_r285_caliber"]
        row["unmatched_literals"][k] = ev["anti_cherry_pick"][k]["orphan_literals_without_spec_row"]
        row["spec_rows_skipped_for_this_arm"][k] = ev["raw_rows"][k]["spec_rows_skipped_for_this_arm"]
        row["detail_rows"][k] = ev["raw_rows"][k]["rows"]
    rows = [row]
    art_before = sum(len(r["arms"]["A"]["persisted_artifacts"]) for r in rows)
    art_after = sum(len(r["arms"]["B"]["persisted_artifacts"]) for r in rows)
    tot_found = sum(r["arms"]["B"]["commands_found"] for r in rows)
    tot_ok = sum(r["arms"]["B"]["rc_zero"] for r in rows)
    evb = read_bytes(evidence_path)
    ncs = {"control_1_identical_text": nc1(sub_ev) if sub_ev else {"ran": False}}
    if sub_ev is None and os.path.isfile(SUB_EVIDENCE_DEFAULT):
        ncs["control_1_identical_text"] = nc1(json.loads(io.open(SUB_EVIDENCE_DEFAULT, encoding="utf-8").read()))
    payload = {
        "schema": "exec-commands-ab-v1",
        "task": ("R291-B2 execution-level A/B (narrowed re-dispatch: only the judge and the readings were "
                 "missing). One row, skill mcp-builder: run the commands literally written in the before/after "
                 "SKILL.md; caliber copied from 06-benchmark/r285_exec_commands_ab.json."),
        "skill_set": ["mcp-builder"],
        "caliber_note": caliber(),
        "caliber_source": R285_FACE,
        "rows": rows,
        "git_ref_face": tab,
        "git_file_history": hist,
        "totals": {"command_pairs": len(rows), "commands_found_after": tot_found,
                   "rc_zero_after": tot_ok, "artifacts_before": art_before, "artifacts_after": art_after},
        "gain_reading": {"commands_found_delta": B["commands_found"] - A["commands_found"],
                         "rc_zero_delta": B["rc_zero"] - A["rc_zero"],
                         "artifacts_delta": len(B["persisted_artifacts"]) - len(A["persisted_artifacts"]),
                         "reading": ("the after-face adds one doc command surface (the B-only codemod), it runs "
                                     "rc=0 and really rewrites v1 to v2 => +1 rc_zero; artifact face stays level "
                                     "(1 vs 1). The inspector row is identical in shape on both arms and adds no "
                                     "gain.")},
        "evidence": {"path": evidence_path.replace(os.sep, "/"), "bytes": len(evb), "sha256": sha256(evb),
                     "produced_by": ("harness/r291_measure.mjs run, a byte-identical copy of the read-only "
                                     "_temp/r291b/harness script patched inside this write face"),
                     "harness_patch_note": ("two patches, both recorded: 1) before each arm, release 6274-6278 from "
                                            "node/python leftovers this harness itself orphaned (port_cleanup lists "
                                            "every kill); 2) drop PYTHONPYCACHEPREFIX so the .pyc lands back in the "
                                            "declared output dir - with the prefix it was redirected outside and "
                                            "persisted_artifacts read 0 for a command that does persist a file, which "
                                            "was a reading bug, not a doc gap. The read-only dir _temp/r291b was not "
                                            "touched; see readonly_check.")},
        "evidence_sha256": sha256(evb),
        "readonly_check": {"surviving_dir": RO_DIR.replace(os.sep, "/"),
                           "policy": "READ ONLY (no write, no rename, no delete)",
                           "drift": readonly_drift()},
        "comparability_with_r285": {
            "r285_face": R285_FACE, "same_field_names": True, "same_extractor": True,
            "same_extractor_path": "自建skill优化/_repro/r285l/r285_common.mjs",
            "notes": ("comparable because field names, semantics, the extractor and the three-way classification "
                      "(blocked_not_runnable and needs_external_account enter neither rc_zero nor a doc defect "
                      "nor a 0 gain) are the r285 ones, and all four faces run doc-literal commands and read rc "
                      "plus artifacts. Two shape differences must be stated to keep the comparison honest: "
                      "1) this row contains a never-exiting service command (inspector) which none of the r285 "
                      "three has, so it is excluded from rc_zero and evidenced by the banner; 2) the core gain "
                      "effect here is an in-place rewrite rather than new files, so it is judged by the rewrite "
                      "predicate plus the manifest swap, not by persisted_artifacts (the r285 ui-ux row is the "
                      "artifact type)."),
        },
        "provenance_cmd": NL.join([
            "git -C D:/global_skills rev-parse 79862372~1:mcp-builder/SKILL.md   (before blob, re-measured)",
            "git -C D:/global_skills rev-parse 79862372:mcp-builder/SKILL.md     (after blob, re-measured)",
            "git -C D:/global_skills rev-parse e64c17d3:mcp-builder/SKILL.md     (last real touch, re-measured)",
            "git -C D:/global_skills rev-parse 079b91f3:mcp-builder/SKILL.md     (foreign-commit trap probe)",
            "git -C D:/global_skills log --format=%H -8 -- mcp-builder/SKILL.md  (touch history)",
            "自建skill优化/_repro/r285l/r285_common.mjs            (r285 extractor + runOne, tracked)",
            "自建skill优化/_repro/r285l/r285_cmds.json             (r285 cmdspec contract, tracked)",
            "自建skill优化/06-benchmark/r285_exec_commands_ab.json (caliber authority, tracked)",
        ]),
        "run_face": {"write_face": HERE.replace(os.sep, "/"),
                     "deliverables": [OUT_DEFAULT.replace(os.sep, "/"),
                                      os.path.join(HERE, "check_r291b.py").replace(os.sep, "/"),
                                      os.path.join(HERE, "report.md").replace(os.sep, "/")],
                     "evidence_dir": os.path.join(HERE, "harness", "results").replace(os.sep, "/"),
                     "arm_dirs": {}, "read_only_face": RO_DIR.replace(os.sep, "/")},
        "run_face_note": ("write face moved to a brand new directory _repro/r291b2 so a possibly still alive process "
                          "from the previous round cannot fight this one over the same file; the surviving assets "
                          "_temp/r291b are read only. _temp/ is an any-depth .gitignore pattern, so nothing here is "
                          "registered: provenance_cmd therefore points only at repo-resolvable paths and the real "
                          "invocations (absolute) live in judge_invocation / nc1_invocation / nc2_invocation."),
        "judge_invocation": [
            "cd /d " + chr(34) + HERE + chr(34),
            chr(34) + PYEXE_DOC + chr(34)
            + " -B check_r291b.py",
        ],
        "nc1_invocation": [
            "cd /d " + chr(34) + HERE + chr(34),
            chr(34) + NODE_DOC + chr(34)
            + " harness/r291_measure.mjs sub " + chr(34) + os.path.join(HERE, "texts", "run_A_SKILL.md") + chr(34),
            chr(34) + PYEXE_DOC + chr(34)
            + " -B check_r291b.py --sub-evidence harness/results/sub_raw.json --emit",
        ],
        "nc2_invocation": [
            "cd /d " + chr(34) + HERE + chr(34),
            chr(34) + PYEXE_DOC + chr(34)
            + " -B check_r291b.py --negctl2",
        ],
        "measured_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "expected_last_line": ("[EXEC-AB-B] rows=" + str(len(rows)) + " commands_ok=" + str(tot_ok) + "/"
                               + str(tot_found) + " artifacts_before=" + str(art_before)
                               + " artifacts_after=" + str(art_after)),
        "negative_controls": ncs,
    }
    for k in ("A", "B"):
        payload["run_face"]["arm_dirs"][k] = ev["raw_rows"][k]["arm_dir_rel"]
    return payload


def read_table(obj):
    # human-readable recomputation print, straight from a payload/row structure
    lines = []
    for r in obj.get("rows", []):
        for arm in ("A", "B"):
            x = r["arms"][arm]
            lines.append("  " + str(r["skill"]) + " " + arm + ": found=" + str(x["commands_found"])
                         + " runnable=" + str(x["runnable"]) + " rc0=" + str(x["rc_zero"])
                         + " blocked=" + str(x["blocked_not_runnable"])
                         + " ext=" + str(x["needs_external_account"])
                         + " unresolved=" + str(x["placeholder_unresolved"])
                         + " art=" + str(len(x["persisted_artifacts"]))
                         + " claim=" + str(x["doc_claim_met"]) + " exec=" + str(x["executions"])
                         + " var=" + str(x["variant_executions"]) + "  artifacts="
                         + json.dumps(x["persisted_artifacts"], ensure_ascii=False))
        lines.append("  literals A=" + json.dumps(r["commands_found_literals"]["A"], ensure_ascii=False))
        lines.append("  literals B=" + json.dumps(r["commands_found_literals"]["B"], ensure_ascii=False))
    return lines


def validate(stored, fresh, problems):
    # the teeth. four faces are checked, all of them re-derived from raw evidence/git:
    #  (a) per-arm readings incl. the doc_claim_sub evidence keys and the artifact set,
    #  (b) the arm text sha (a substituted text must not read as the real one),
    #  (c) totals, (d) the before/after blob of the managed root (a silent base swap bites).
    fresh_gt = {}
    for x in fresh.get("git_ref_face", []):
        fresh_gt[x["point"]] = x
    for r in stored.get("rows", []):
        nr = None
        for x in fresh["rows"]:
            if x["skill"] == r["skill"]:
                nr = x
        if nr is None:
            problems.append("MISMATCH " + str(r["skill"]) + ".rows: no such row in the evidence")
            continue
        for arm in ("A", "B"):
            compare(r["arms"][arm], nr["arms"][arm], str(r["skill"]) + ".arms." + arm, problems)
            st = (r.get("arm_text") or {}).get(arm) or {}
            if st.get("sha12") != nr["arm_text"][arm]["sha12"]:
                problems.append("MISMATCH " + str(r["skill"]) + ".arm_text." + arm + ".sha12: stored="
                                + str(st.get("sha12")) + " recomputed=" + nr["arm_text"][arm]["sha12"])
        for key, point in (("before_blob", "before"), ("after_blob", "after")):
            if r.get(key) != fresh_gt[point]["blob"]:
                problems.append("MISMATCH " + str(r["skill"]) + "." + key + ": stored="
                                + str(r.get(key))[:12] + " recomputed=" + str(fresh_gt[point]["blob"])[:12])
    st_tot = stored.get("totals") or {}
    for k in fresh["totals"]:
        if st_tot.get(k) != fresh["totals"][k]:
            problems.append("MISMATCH totals." + k + ": stored=" + json.dumps(st_tot.get(k))
                            + " recomputed=" + json.dumps(fresh["totals"][k]))
    for p in readonly_drift():
        problems.append(p)
    return problems


def load_sub(a):
    # negative control 1 evidence: auto-picked when present, or forced by --sub-evidence
    sub_path = a.sub_evidence or SUB_EVIDENCE_DEFAULT
    if sub_path and os.path.isfile(sub_path):
        return json.loads(io.open(sub_path, encoding="utf-8").read())
    return None


def emit(a, ev):
    # before writing, recompute the whole table and diff it against the file about to be
    # replaced, so a re-run cannot quietly move an already published number.
    fresh = build_payload(ev, a.evidence, load_sub(a))
    print("[PRE-EMIT] recomputed from raw evidence before writing:")
    for ln in read_table(fresh):
        print(ln)
    if os.path.isfile(a.out):
        prev = json.loads(io.open(a.out, encoding="utf-8").read())
        problems = []
        validate(prev, fresh, problems)
        print("[PRE-EMIT][CONSISTENCY] " + ("PASS previous published == recomputed"
             if not problems else "FAIL previous differs, see MISMATCH lines below"))
        for p in problems:
            print("[" + p + "]")
    else:
        print("[PRE-EMIT][CONSISTENCY] first write, nothing to diff")
    tmp = a.out + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="") as f:
        json.dump(fresh, f, ensure_ascii=False, indent=1)
    os.replace(tmp, a.out)
    print("[EMIT] wrote " + a.out + " bytes=" + str(len(read_bytes(a.out))))
    return fresh


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--evidence", default=EVIDENCE_DEFAULT)
    ap.add_argument("--out", default=OUT_DEFAULT)
    ap.add_argument("--sub-evidence", default="")
    ap.add_argument("--emit", action="store_true", help="recompute from raw evidence and write out.json")
    ap.add_argument("--negctl2", action="store_true", help="tamper rc_zero in a copy, recompute, delete copy")
    a = ap.parse_args()
    if a.negctl2:
        return negctl2(a)
    if not os.path.isfile(a.evidence):
        print("[VALIDATE] raw evidence missing: " + a.evidence)
        print("[CONSISTENCY] FAIL")
        print("[EXEC-AB-B] rows=0 commands_ok=0/0 artifacts_before=0 artifacts_after=0")
        return 3
    ev = json.loads(io.open(a.evidence, encoding="utf-8").read())
    if a.emit:
        emit(a, ev)
    if not os.path.isfile(a.out):
        print("[VALIDATE] deliverable missing (run with --emit): " + a.out)
        print("[CONSISTENCY] FAIL")
        print("[EXEC-AB-B] rows=0 commands_ok=0/0 artifacts_before=0 artifacts_after=0")
        return 3
    stored = json.loads(io.open(a.out, encoding="utf-8").read())
    fresh = build_payload(ev, a.evidence, load_sub(a))
    problems = validate(stored, fresh, [])
    evb = read_bytes(a.evidence)
    if (stored.get("evidence") or {}).get("sha256") != sha256(evb):
        problems.append("MISMATCH evidence.sha256: stored="
                        + str((stored.get("evidence") or {}).get("sha256"))[:12]
                        + " recomputed=" + sha256(evb)[:12])
    lines = ["[VALIDATE] evidence=" + a.evidence, "[VALIDATE] out=" + a.out]
    lines = lines + read_table(stored)
    nc = (stored.get("negative_controls") or {}).get("control_1_identical_text") or {}
    if nc.get("ran"):
        lines.append("[NEGCTL-1] identical=" + str(nc.get("identical")) + " " + str(nc.get("verdict")))
        lines.append("[NEGCTL-1] B text=" + str(nc.get("B_text_sha12")) + " A text=" + str(nc.get("A_text_sha12"))
                     + " substituted_B_with=" + str(nc.get("substituted_B_with")))
        lines.append("[NEGCTL-1] B-only codemod row skipped after substitution: "
                     + json.dumps(nc.get("B_spec_rows_skipped_for_this_arm"), ensure_ascii=False)
                     + " differing_fields=" + json.dumps(nc.get("differing_fields"), ensure_ascii=False))
    else:
        lines.append("[NEGCTL-1] ran=False")
    gt = {}
    for x in fresh["git_ref_face"]:
        gt[x["point"]] = x
    lines.append("[GIT-BASE] before=" + str(gt["before"]["blob"])[:12] + "(" + str(gt["before"]["bytes"]) + "B)"
                 + " after=" + str(gt["after"]["blob"])[:12] + "(" + str(gt["after"]["bytes"]) + "B)"
                 + " BASE=" + str(gt["base_last_touch"]["blob"])[:12]
                 + " foreign_079b91f3=" + str(gt["other_session_commit"]["blob"])[:12]
                 + " HEAD=" + str(gt["head"]["blob"])[:12]
                 + " | before==BASE: " + str(gt["before"]["blob"] == gt["base_last_touch"]["blob"])
                 + " | after==HEAD: " + str(gt["after"]["blob"] == gt["head"]["blob"]))
    _skip = readonly_skipped()
    lines.append("[RO-DRIFT] read-only surviving dir rescanned: " + RO_DIR
                 + " problems=" + str(len(readonly_drift()))
                 + (" SKIPPED(dir absent, unverified)" if _skip else " verified"))
    if problems:
        lines.append("[CONSISTENCY] FAIL")
        for p in problems:
            lines.append("[" + p + "]")
    else:
        lines.append("[CONSISTENCY] PASS recomputed == stored for every numeric field, arm_text sha, "
                     + "git base face and read-only drift")
    tot = fresh["totals"]
    lines.append("[EXEC-AB-B] rows=" + str(tot["command_pairs"]) + " commands_ok="
                 + str(tot["rc_zero_after"]) + "/" + str(tot["commands_found_after"])
                 + " artifacts_before=" + str(tot["artifacts_before"])
                 + " artifacts_after=" + str(tot["artifacts_after"]))
    print(NL.join(lines))
    return 0 if not problems else 2


def negctl2(a):
    # negative control 2, the leg proving the judge has teeth: copy the real deliverable,
    # tamper ONE rc_zero by -1, recompute against the copy. Required outcome: a MISMATCH
    # naming that exact field, a non-zero exit, copy deleted, zero residue left behind.
    out = a.out if os.path.isfile(a.out) else OUT_DEFAULT
    stored = json.loads(io.open(out, encoding="utf-8").read())
    old = stored["rows"][0]["arms"]["B"]["rc_zero"]
    stored["rows"][0]["arms"]["B"]["rc_zero"] = old - 1
    copy = os.path.join(HERE, "harness", "results", "_negctl2_copy.json")
    with io.open(copy, "w", encoding="utf-8", newline="") as f:
        json.dump(stored, f, ensure_ascii=False, indent=1)
    print("[NEGCTL2] tampered field = mcp-builder.arms.B.rc_zero " + str(old) + " -> " + str(old - 1))
    p = subprocess.run([sys.executable, "-B", os.path.join(HERE, "check_r291b.py"),
                        "--out", copy, "--evidence", a.evidence], capture_output=True, timeout=300)
    text = p.stdout.decode("utf-8", "replace")
    for ln in text.split(NL):
        if ln.strip():
            print("[NEGCTL2][validator] " + ln)
    os.remove(copy)
    residue = [f for _root, _dirs, fs3 in os.walk(HERE) for f in fs3 if "negctl2" in f.lower()]
    named = "[MISMATCH mcp-builder.arms.B.rc_zero" in text
    deleted = not os.path.exists(copy)
    ok = (p.returncode != 0) and named and deleted and (len(residue) == 0)
    print("[NEGCTL2] validator_exit=" + str(p.returncode) + " named_field=" + ("YES" if named else "NO")
          + " copy_deleted=" + ("YES" if deleted else "NO") + " residue_hits=" + str(len(residue)))
    print("[NEGCTL2] " + ("PASS: teeth confirmed (MISMATCH named, non-zero exit, copy removed)"
                          if ok else "FAIL: negative control 2 did not bite"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
