# -*- coding: utf-8 -*-
r"""r319b A2/G4 - browse 逐条对账补齐件（gstack 改配的证据补全；不动尺、不改阈值）。

问题（r317 终裁留的口子）：G2 的 browse 备选对里 D5_trigger_face / D6_tool_command 两维弃权
（弃权=>该维不参与裁定，abstain=2 触发「>=2 abstaining gated dims -> unclear」），所以 browse
当时只能读 unclear、不许判同族。本件把 browse 的 triggers / allowed-tools / 命令面逐项抽出来，
与本地件（browse-QA 手册形态）逐条对账，再原口径复跑 G2 轴集，让三选一有逐条依据。

纪律（写死在代码里，不靠自觉）：
  1. 词表只用 G2 自己的（PURPOSE_VERBS / TRIG_ONLY / TOOL_NOUNS / FAMILIES），阈值一个不改；
     本件不新增词表去救任何弃权维度——弃权就照记弃权（G2 的诚实先例）。
  2. 对账用字面命中：browse 侧每个条目原串在本地入口件里找同一串。命中给两侧原文行+行号；
     不命中给「本地词元重合最高的一行」作最近对应物，重合为 0 就明说没有对应物。
     这是增量证据面，不参与改判据。
  3. verdict 由 G2 规则在 as-is 轴值上算出；已知答案堂（docx 正例 + gstack-capy 反例）+ 两条
     负控没过，就只出探针报告、不出 verdict 建议。

读面（只读）：D:/global_skills、_repro/r316b_lineage、_repro/r318a/g3_prep/siglib.py。
写面：只有 _temp/r319b/。网络：只 gh api 取 browse 件现值 blob sha，与 evidence 字节对钉。
末行：[R319G4:BROWSE] court=<pass|fail> verdict=<same-family|unclear|diff-family> matched-axes=<n>/6
"""
import datetime
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))            # -> 自建skill优化
REPRO = os.path.join(ROOT, "_repro")
G2_DIR = os.path.join(REPRO, "r316b_lineage")
EV = os.path.join(G2_DIR, "evidence")
SIGLIB_PATH = os.path.join(REPRO, "r318a", "g3_prep", "siglib.py")
SKILLS = os.environ.get("ZIJIAN_SKILLS_ROOT", "D:/global_skills")
OUTDIR = os.path.join(HERE, "ev")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# browse 件在 r316b 落盘时钉住的 git blob sha（本件用 evidence 字节复算 + gh api 现值双向对钉）
BROWSE_BLOB_PIN = "e5792ca58047608b52fee9aa0b94c50ec9419406"
BROWSE_TMPL_PIN = "0655b388acae9a91ee859afab60a93a637d4ddf1"
LOCAL_SHA_RECORDED_BY_R316B = "5c00c92e1160b6b1e0a6208a862681d9a57ee13f042f4613cc3ae79c9a598de1"
G2 = None                                                # adjudicate 里要用 G2.STOP，先占位


def load_mod(name, path):
    """把只读面的两个现成件当库用：G2 判据本体 + r316c 轴集（siglib）。
    不复制代码，避免同一判据出现两份可分叉的实现。"""
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def blob_sha(data):
    """自算 git blob 对象号，跟 gh api 报的 sha 对拍 => 钉住上游没漂移。"""
    h = hashlib.sha1()
    h.update(b"blob " + str(len(data)).encode() + b"\x00" + data)
    return h.hexdigest()


def git_show(repo, relpath):
    """受管根入口一律走 git show HEAD:（brief 指定）：拿到 LF 归一化字节，避开 CRLF 行数假差。"""
    p = subprocess.run(["git", "-C", repo, "show", "HEAD:" + relpath], capture_output=True, timeout=120)
    return None if p.returncode != 0 else p.stdout


def gh_blob_sha(repo, path):
    """唯一允许的联网动作：gh api contents 取 sha。gh 不可用就降级为只比 evidence 字节。"""
    cmd = "gh api repos/%s/contents/%s --jq .sha" % (repo, path)
    try:
        p = subprocess.run(["gh", "api", "repos/%s/contents/%s" % (repo, path), "--jq", ".sha"],
                           capture_output=True, timeout=180)
        if p.returncode != 0:
            p = subprocess.run(cmd, capture_output=True, shell=True, timeout=180)
        if p.returncode != 0:
            return {"gh": "error", "sha": None,
                    "detail": ((p.stderr or b"") + b"|" + (p.stdout or b"")).decode("utf-8", "replace")[:240]}
        return {"gh": "ok", "sha": p.stdout.decode().strip(), "detail": None}
    except Exception as exc:
        return {"gh": "unavailable", "sha": None, "detail": str(exc)[:200]}


# ---------------------------------------------------------------- ① browse 侧逐项抽取
def fm_list_items(text, key):
    """frontmatter 里 key: 下的缩进列表项，带行号（triggers / allowed-tools 都是这个形态）。"""
    lines = text.replace("\r\n", "\n").split("\n")
    for i, ln in enumerate(lines):
        if re.match(r"^" + key + r":[ ]*$", ln):
            out, j = [], i + 1
            while j < len(lines) and re.match(r"^[ ]+-\s+", lines[j]):
                out.append({"line": j + 1, "verbatim": lines[j].strip(),
                            "item": re.sub(r"^[ ]+-\s+", "", lines[j]).strip()})
                j += 1
            return out
        if re.match(r"^" + key + r":[ ]*\S", ln):        # 同行标量形态（非列表）也照抽
            return [{"line": i + 1, "verbatim": ln.strip(), "item": ln.split(":", 1)[1].strip()}]
    return []


def command_surface(text):
    """browse 的命令面 = 正文里可机械数出的四类串：$B 子命令 / aside CLI / aside API 函数 / gstack bin
    + slash 命令。全用正则现抽、不手写清单（手写清单=可被指为挑样本），去重后按 kind 分组。"""
    items, seen = [], set()

    def add(kind, tok, line):
        k = (kind, tok)
        if k in seen:
            return
        seen.add(k)
        items.append({"kind": kind, "token": tok, "line": line})

    for n, ln in enumerate(text.replace("\r\n", "\n").split("\n"), 1):
        for tok in re.findall(r"\$B\s+([a-z][a-z0-9_-]{2,})", ln):
            add("B-subcommand", tok, n)
        for tok in re.findall(r"\b(aside\s+(?:repl|exec))\b", ln):
            add("aside-cli", tok, n)
        for tok in re.findall(r"\b([A-Za-z][A-Za-z0-9_]{4,})\s*\(", ln):
            if tok not in ("function", "return", "console", "String", "JSON", "Buffer", "Promise", "printf"):
                add("aside-api-fn", tok, n)
        for tok in re.findall(r"\b(gstack-[a-z][a-z0-9-]{2,})\b", ln):
            add("gstack-bin", tok, n)
        for tok in re.findall(r"(?<![\w/.-])/([a-z][a-z0-9-]{3,})\b", ln):
            add("slash-command", "/" + tok, n)
    return items


# ---------------------------------------------------------------- ② 逐条对账
def literal_hits(item, text):
    """字面命中：item 原串出现在对方文本里（区分大小写），返回首个命中行号与该行原文。"""
    for n, ln in enumerate(text.replace("\r\n", "\n").split("\n"), 1):
        if item in ln:
            return {"hit": True, "line": n, "verbatim": ln.strip()[:300]}
    return {"hit": False, "line": None, "verbatim": None}


def nearest(text, item):
    """不命中时的「本地最近对应物」：词元重合最高的一行。词元=长度>=4 的小写词，停用词用 G2 自己的
    STOP（不引同义词表，纯机械），重合 0 就明确报无对应物。"""
    itoks = set(w for w in re.findall(r"[a-z]{4,}", item.lower()) if w not in G2.STOP)
    best = [0, None, None]
    for n, ln in enumerate(text.replace("\r\n", "\n").split("\n"), 1):
        ov = len(itoks & set(w for w in re.findall(r"[a-z]{4,}", ln.lower())))
        if ov > best[0]:
            best = [ov, n, ln.strip()[:300]]
    return {"overlap": best[0], "line": best[1], "verbatim": best[2]}


def main():
    global G2
    G2 = load_mod("g2check", os.path.join(G2_DIR, "check_r316b.py"))
    os.makedirs(OUTDIR, exist_ok=True)

    # ---- 本地入口件：git show HEAD:gstack/SKILL.md（受管根只读）
    raw = git_show(SKILLS, "gstack/SKILL.md")
    if raw is None:
        raw = open(os.path.join(SKILLS, "gstack", "SKILL.md"), "rb").read()
        local_source = "disk-fallback"
    else:
        local_source = "git show HEAD:gstack/SKILL.md"
    local_path = os.path.join(OUTDIR, "local_head_SKILL.md")
    with open(local_path, "wb") as fh:
        fh.write(raw)
    local_text = raw.decode("utf-8", "replace")
    local_sha256 = hashlib.sha256(raw).hexdigest()

    # ---- browse 件：evidence 字节复算 blob sha + gh api 现值对钉
    browse_bytes = open(os.path.join(EV, "gstack_browse_skill.md"), "rb").read()
    browse_text = browse_bytes.decode("utf-8", "replace")
    tmpl_bytes = open(os.path.join(EV, "gstack_browse_SKILL.md.tmpl"), "rb").read()
    tmpl_live = gh_blob_sha("garrytan/gstack", "browse/SKILL.md.tmpl")
    ev_blob = blob_sha(browse_bytes)
    ghres = gh_blob_sha("garrytan/gstack", "browse/SKILL.md")
    pin = {"evidence_blob_sha": ev_blob, "expected_pin": BROWSE_BLOB_PIN,
           "evidence_matches_pin": ev_blob == BROWSE_BLOB_PIN,
           "live_gh": ghres, "live_matches_evidence": (ghres.get("sha") == ev_blob) if ghres["gh"] == "ok" else None,
           "tmpl_evidence_blob_sha": blob_sha(tmpl_bytes), "tmpl_expected_pin": BROWSE_TMPL_PIN,
           "tmpl_matches_pin": blob_sha(tmpl_bytes) == BROWSE_TMPL_PIN,
           "tmpl_live_gh": tmpl_live,
           "tmpl_live_matches_evidence": (tmpl_live.get("sha") == blob_sha(tmpl_bytes)) if tmpl_live["gh"] == "ok" else None}

    # ---- 抽取 + 对账
    b_trig = fm_list_items(browse_text, "triggers")
    b_tools = fm_list_items(browse_text, "allowed-tools")
    surf = command_surface(browse_text)
    # 本地吸收卷：browse v2 的 Aside 面落在侧卷而不在入口件 —— 这是本件最关键的形态事实
    sidecar = os.path.join(SKILLS, "gstack", "references", "browse-v2-upstream.md")
    try:
        sidecar_text = open(sidecar, encoding="utf-8", errors="replace").read()
    except Exception as exc:
        sidecar_text = ""
        print("[!] 侧卷读不到:", exc)

    rows = []
    for grp_name, items in (("triggers", b_trig), ("allowed-tools", b_tools), ("command_face", surf)):
        for r in items:
            it = r.get("item") or r.get("token")
            entry = {"group": grp_name, "item": it, "kind": r.get("kind", "frontmatter"),
                     "browse_line": r["line"], "browse_verbatim": r.get("verbatim"),
                     "browse_context": browse_text.split("\n")[r["line"] - 1].strip()[:300],
                     "local_entry_hit": literal_hits(it, local_text),
                     "sidecar_hit": literal_hits(it, sidecar_text) if sidecar_text else {"hit": False}}
            if not entry["local_entry_hit"]["hit"]:
                entry["local_nearest"] = nearest(local_text, it)
            rows.append(entry)

    def summ(g):
        sel = [x for x in rows if x["group"] == g]
        return {"total": len(sel),
                "hit_in_local_entry": sum(1 for x in sel if x["local_entry_hit"]["hit"]),
                "hit_in_local_sidecar": sum(1 for x in sel if x["sidecar_hit"]["hit"]),
                "no_local_counterpart_at_all": sum(1 for x in sel if not x["local_entry_hit"]["hit"]
                                                  and x.get("local_nearest", {}).get("overlap", 0) == 0)}
    face_counts = dict((g, summ(g)) for g in ("triggers", "allowed-tools", "command_face"))
    kinds = {}
    for x in rows:
        if x["group"] != "command_face":
            continue
        k = kinds.setdefault(x["kind"], {"total": 0, "hit_in_local_entry": 0, "hit_in_local_sidecar": 0})
        k["total"] += 1
        k["hit_in_local_entry"] += 1 if x["local_entry_hit"]["hit"] else 0
        k["hit_in_local_sidecar"] += 1 if x["sidecar_hit"]["hit"] else 0

    # ---- ③ G2 轴集原口径复跑（零新词表、零阈值改动）
    sig = G2.signature
    loc_docx = sig(os.path.join(SKILLS, "docx", "SKILL.md"), "local:D:/global_skills/docx/SKILL.md")
    up_docx = sig(os.path.join(EV, "anthropic_docx.md"), "up:anthropics/skills:skills/docx/SKILL.md")
    up_pdf = sig(os.path.join(EV, "anthropic_pdf.md"), "neg:anthropics/skills:skills/pdf/SKILL.md")
    loc_gs = sig(local_path, "local:D:/global_skills/gstack/SKILL.md")
    capy = sig(os.path.join(EV, "gstack_capy_skill.md"), "declared:garrytan/gstack:capy/skill/gstack/SKILL.md")
    browse = sig(os.path.join(EV, "gstack_browse_skill.md"), "alt:garrytan/gstack:browse/SKILL.md")

    pos = G2.adjudicate(loc_docx, up_docx)
    neg = G2.adjudicate(loc_gs, capy)
    bsw = G2.adjudicate(loc_gs, browse)
    legA = G2.adjudicate(loc_docx, up_pdf)                     # 负控 A：同仓跨功能 => diff-family
    legB = G2.adjudicate(loc_docx, up_docx, cleared=True)      # 负控 B：清空词表 => unclear（防恒绿）
    court_pass = (pos["verdict"] == "same-family") and (neg["verdict"] == "diff-family")
    qualified = bool(court_pass and legA["verdict"] == "diff-family" and legB["verdict"] == "unclear")

    # 复跑不许把轴跑出漂移：逐维与 r316b 落盘值对账（只读该件）
    old = json.load(open(os.path.join(G2_DIR, "lineage.json"), encoding="utf-8"))
    old_browse = old["gstack_options"]["switch_browse"]
    old_capy = old["gstack_options"]["keep_capy"]
    AXIS6 = ["D3_h1_topic", "D4_purpose_verbs", "D5_trigger_face", "D6_tool_command",
             "S2_heading_topics", "S3_code_tokens"]
    drift = []
    for k in AXIS6 + ["D2_family", "S1_gen_parity"]:
        for tag, nowr, oldr in (("browse", bsw, old_browse), ("capy", neg, old_capy)):
            a, b = nowr["dims"][k], oldr["dims"][k]
            if json.dumps(a, sort_keys=True) != json.dumps(b, sort_keys=True):
                drift.append({"pair": tag, "dim": k, "now": a, "r316b": b})
    # 签名层也要一致：本件用 git show 的 LF 字节，r316b 用盘上 CRLF 字节 => 只比集合面不比 sha
    sig_drift = []
    for key in ("trigger", "tool", "purpose"):
        a = sorted(loc_gs[key])
        b = sorted(old["signatures"]["local:D:/global_skills/gstack/SKILL.md"][key])
        if a != b:
            sig_drift.append({"field": key, "now": a, "r316b": b})

    matched = sum(1 for k in AXIS6 if bsw["dims"][k]["inter"] >= 2)
    matched_neg = sum(1 for k in AXIS6 if neg["dims"][k]["inter"] >= 2)

    # ---- ③b 第二把尺独立读（r316c siglib A1-A5，同一段只读代码复用，不自写）
    siglib_vals = {}
    try:
        sg = load_mod("siglib_r316c", SIGLIB_PATH)
        single = os.path.join(OUTDIR, "face_single", "gstack")
        os.makedirs(single, exist_ok=True)
        with open(os.path.join(single, "SKILL.md"), "wb") as fh:
            fh.write(raw)
        browse_ev = os.path.join(EV, "gstack_browse_skill.md")
        pop = lambda d: dict((k, d[k]) for k in sg.MIN_TEETH)
        siglib_vals = {
            "local_entry_face_only_vs_browse": pop(sg.axes(single, browse_ev)),
            "local_package_face_whole_vs_browse": pop(sg.axes(os.path.join(SKILLS, "gstack"), browse_ev)),
            "local_package_face_whole_vs_capy": pop(sg.axes(os.path.join(SKILLS, "gstack"),
                                                            os.path.join(EV, "gstack_capy_skill.md"))),
            "court_positive_docx_vs_anthropic": pop(sg.axes(os.path.join(SKILLS, "docx"),
                                                            os.path.join(EV, "anthropic_docx.md"))),
            "teeth_gates": sg.MIN_TEETH, "primary": sg.PRIMARY, "confirm": sg.CONFIRM,
            "_circularity_note": "package face 含 references/browse-v2-upstream.md（受控吸收卷，正文逐字来自 browse v2.0.0）"
                                 "=> 对 browse 是循环证据，只作形态说明，不参与同族裁定；单文件面才是与 G2 可比的读法",
        }
    except Exception as exc:
        siglib_vals = {"error": "%s: %s" % (type(exc).__name__, str(exc)[:200])}

    # ---- ④ verdict：堂过才出；轴值 as-is，弃权不救
    verdict = bsw["verdict"] if qualified else "unclear"
    matched_list = [k for k in AXIS6 if bsw["dims"][k]["inter"] >= 2]
    abstain_dims = [k for k in AXIS6 if not bsw["dims"][k].get("usable", False)]
    local_sha_ok = local_sha256 == LOCAL_SHA_RECORDED_BY_R316B

    out = {
        "schema": "r319b-browse-reconcile-1",
        "task": "A2/G4（r319 派发）：gstack 改配的 browse 逐条对账补齐件",
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "discipline": {
            "vocab_source": "G2 原词表（PURPOSE_VERBS/TRIG_ONLY/TOOL_NOUNS/FAMILIES/STOP），本件零新增词表",
            "thresholds_changed": 0, "abstain_rule_unchanged": True,
            "no_new_vocab_then_retune": True,
            "reconciliation_is_evidence_not_gate": "字面对账只给增量证据，不参与改判据、不救弃权",
        },
        "provenance": {
            "local_source": local_source, "local_sha256": local_sha256,
            "local_matches_r316b_recorded_sha": local_sha_ok,
            "line_ending_note": "git show HEAD: 给 LF 归一化字节（与 r316b 落盘的 sha256 一致）；盘上 CRLF 是另一份表示，"
                                "git status 对 gstack/SKILL.md 无改动 => r317 R241 校正注里 643/644 行数之差即行尾口径，不是内容漂移",
            "browse_pin_crosscheck": pin,
            "sidecar_absorption_volume": {
                "path": "D:/global_skills/gstack/references/browse-v2-upstream.md",
                "bytes": len(sidecar_text.encode("utf-8")), "readable": bool(sidecar_text),
                "first_heading": sidecar_text.split("\n")[0].strip() if sidecar_text else None,
                "anchor_tail": sidecar_text.strip().split("\n")[-1][:300] if sidecar_text else None},
        },
        "extracted_browse_face": {
            "triggers_items": b_trig, "allowed_tools_items": b_tools,
            "command_surface_total": len(surf),
            "command_surface_by_kind": dict((k, sum(1 for x in surf if x["kind"] == k))
                                           for k in sorted(set(x["kind"] for x in surf))),
        },
        "reconciliation": rows,
        "reconciliation_summary": {"groups": face_counts, "command_face_by_kind": kinds,
                                   "rule": "命中=条目原串在本地件里逐字出现；不命中给 local_nearest（词元重合最高行）"},
        "axes_rerun_g2_asis": {
            "browse_pair": bsw, "capy_pair": neg, "docx_positive": pos,
            "negative_controls": {"legA_docx_vs_pdf": legA["verdict"], "legB_cleared_vocab": legB["verdict"]},
            "drift_vs_r316b_recorded_dims": drift,
            "local_signature_field_drift": sig_drift,
            "matched_axes_definition": "六条集合轴（D3 h1 / D4 purpose / D5 trigger / D6 tool / S2 heading / S3 code）中 |A∩B| >= 2 的条数",
            "matched_axes_browse": matched, "matched_axes_capy_negative_reference": matched_neg,
            "abstain_dims_browse": abstain_dims,
            "abstain_count_browse": bsw["abstain_count"],
        },
        "axes_rerun_siglib_r316c": siglib_vals,
        "court": {"rule": "docx 正例须 same-family 且 gstack<->capy 须 diff-family；两条负控（同仓跨功能=diff-family、"
                           "清空词表=unclear）同过才允许出 verdict",
                  "docx_positive": pos["verdict"], "gstack_capy_negative": neg["verdict"],
                  "negA": legA["verdict"], "negB": legB["verdict"],
                  "court_pass": court_pass, "qualified": qualified},
        "verdict": verdict,
        "verdict_reason": ("堂过；browse 对 D5_trigger_face / D6_tool_command 仍按原弃权规则记弃权"
                           "（abstain=%d => G2 规则给 %s）。字面对账的增量证据在 reconciliation_summary，"
                           "未用于放宽弃权规则。" % (bsw["abstain_count"], verdict)) if qualified
                          else "堂没过：本件只作探针报告，不发 verdict 建议",
        "three_options_increment": {
            "keep_current_classification": {
                "option": "维持归类（NOT_SAME_LINEAGE，不动 path）",
                "new_reads_from_this_pack": {
                    "capy_negative_reference": "diff-family（disproof=%d/5）" % neg["disproof_count"],
                    "browse_matched_axes": "%d/6" % matched,
                    "browse_abstain_dims": abstain_dims,
                    "command_face_literal_hit_in_entry": "%d/%d" % (
                        face_counts["command_face"]["hit_in_local_entry"], face_counts["command_face"]["total"])},
                "reading": "browse 的三样触发/工具签名在本地入口件里逐字命中数不足以填上弃权两维，同族主张仍拿不出 G2 认可的正面签名。"},
            "switch_browse_with_same_run_pin_rebuild": {
                "option": "改配 browse（必须同一次重建该对 pin）",
                "new_reads_from_this_pack": {
                    "allowed_tools_literal": "%d/%d 命中入口件" % (face_counts["allowed-tools"]["hit_in_local_entry"],
                                                                   face_counts["allowed-tools"]["total"]),
                    "triggers_literal_in_entry": "%d/%d" % (face_counts["triggers"]["hit_in_local_entry"],
                                                            face_counts["triggers"]["total"]),
                    "command_face_literal_in_sidecar": "%d/%d" % (face_counts["command_face"]["hit_in_local_sidecar"],
                                                                  face_counts["command_face"]["total"]),
                    "browse_gen_marker_parity": bsw["dims"]["S1_gen_parity"]["parity"],
                    "browse_family_dominant": bsw["dims"]["D2_family"]["dominant"]},
                "hard_constraint": "改 path 必须同一次重建该对 pin（旧 pin 11bd23cc 与新靶不可比），否则 compare_baseline 把改写本身读成 UPSTREAM_CHANGED",
                "blocked_by": "D5/D6 仍弃权 => G2 口径下 browse 读 unclear，进不了 same-family 正门；侧卷命中属受控吸收（循环证据），不许当同族签名用"},
            "no_upstream_anchor_precedent": {
                "option": "按 no_upstream_anchor 先例处置（无直系上游）",
                "new_reads_from_this_pack": {
                    "root_router_also_unclear": "见 r317 终裁第 3 条（本件未重跑该对，轴值直接引 r316b 落盘的 against_root_skillmd）",
                    "entry_is_reassembly": "入口件 = browse 的 headless $B 分支 + 根套件建议块（Development workflow skill suggestions）重组；"
                                           "Aside 分支不在入口件而在侧卷 => 无单一上游等于它",
                    "entry_vs_sidecar_split": "命令面字面命中：入口件 %d 条 / 侧卷 %d 条（共 %d 条）" % (
                        face_counts["command_face"]["hit_in_local_entry"],
                        face_counts["command_face"]["hit_in_local_sidecar"], face_counts["command_face"]["total"])}},
        },
        "last_line": "",
    }
    last = "[R319G4:BROWSE] court=%s verdict=%s matched-axes=%d/6" % (
        "pass" if qualified else "fail", verdict, matched)
    out["last_line"] = last
    with open(os.path.join(HERE, "browse_check.json"), "w", encoding="utf-8") as fh:
        fh.write(json.dumps(G2.jsonable(out), ensure_ascii=False, indent=1))

    print("LOCAL %s sha256=%s... 与 r316b 记录一致=%s" % (local_source, local_sha256[:12],
          local_sha_ok))
    print("BROWSE blob evidence=%s live=%s pin一致=%s 现值对钉=%s | tmpl pin=%s 现值=%s" % (
        ev_blob[:12], (ghres.get("sha") or ghres["gh"])[:12], pin["evidence_matches_pin"],
        pin["live_matches_evidence"], pin["tmpl_matches_pin"], pin["tmpl_live_matches_evidence"]))
    print("AXIS-RERUN browse : h1=%s dom=%s pur=%s trg=%s tool=%s head=%s code=%s cos=%s sem=%s abstain=%d disproof=%d/%d" % (
        bsw["dims"]["D3_h1_topic"]["containment"], bsw["dims"]["D2_family"]["same_dominant"],
        bsw["dims"]["D4_purpose_verbs"]["containment"], bsw["dims"]["D5_trigger_face"]["containment"],
        bsw["dims"]["D6_tool_command"]["containment"], bsw["dims"]["S2_heading_topics"]["containment"],
        bsw["dims"]["S3_code_tokens"]["containment"], bsw["dims"]["D2_family"]["cosine"],
        bsw["semantic_mean"], bsw["abstain_count"], bsw["disproof_count"], 5))
    print("DRIFT vs r316b: dims=%d local-sig-fields=%d %s" % (len(drift), len(sig_drift),
          "OK-identical" if not drift and not sig_drift else json.dumps(drift + sig_drift)[:500]))
    print("FACE triggers       : entry %d/%d | sidecar %d/%d | 无对应物 %d" % (
        face_counts["triggers"]["hit_in_local_entry"], face_counts["triggers"]["total"],
        face_counts["triggers"]["hit_in_local_sidecar"], face_counts["triggers"]["total"],
        face_counts["triggers"]["no_local_counterpart_at_all"]))
    print("FACE allowed-tools  : entry %d/%d | sidecar %d/%d | 无对应物 %d" % (
        face_counts["allowed-tools"]["hit_in_local_entry"], face_counts["allowed-tools"]["total"],
        face_counts["allowed-tools"]["hit_in_local_sidecar"], face_counts["allowed-tools"]["total"],
        face_counts["allowed-tools"]["no_local_counterpart_at_all"]))
    print("FACE command_surface: entry %d/%d | sidecar %d/%d | 无对应物 %d" % (
        face_counts["command_face"]["hit_in_local_entry"], face_counts["command_face"]["total"],
        face_counts["command_face"]["hit_in_local_sidecar"], face_counts["command_face"]["total"],
        face_counts["command_face"]["no_local_counterpart_at_all"]))
    for k in sorted(kinds):
        print("   %-16s total=%-3d entry=%-3d sidecar=%d" % (k, kinds[k]["total"],
              kinds[k]["hit_in_local_entry"], kinds[k]["hit_in_local_sidecar"]))
    if "error" not in siglib_vals:
        print("SIGLIB entry-only vs browse :", json.dumps(siglib_vals["local_entry_face_only_vs_browse"]))
        print("SIGLIB package vs browse    :", json.dumps(siglib_vals["local_package_face_whole_vs_browse"]))
        print("SIGLIB package vs capy      :", json.dumps(siglib_vals["local_package_face_whole_vs_capy"]))
        print("SIGLIB court+ docx          :", json.dumps(siglib_vals["court_positive_docx_vs_anthropic"]))
    else:
        print("SIGLIB ERROR:", siglib_vals["error"])
    print("COURT docx=%s gstack-capy=%s negA=%s negB=%s -> qualified=%s" % (
        pos["verdict"], neg["verdict"], legA["verdict"], legB["verdict"], str(qualified).lower()))
    print("MATCHED-AXES browse=%d/6 (capy 负参照=%d/6) 弃权维=%s" % (
        matched, matched_neg, abstain_dims))
    print(last)
    return 0 if qualified else 1


if __name__ == "__main__":
    sys.exit(main())
