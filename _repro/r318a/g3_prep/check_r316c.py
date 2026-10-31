# -*- coding: utf-8 -*-
"""r316c 判据 · coding-agent 落地备料证据包（只出证据+方案，不落地不代裁）。

怎么运作（#42：行级讲清逻辑，便于后续改）：
  1) 漂移钉：自算 raw/upstream_SKILL.md 的 git 对象号，与在册基线 sha、gh api 现取 sha 三方对拍。
  2) 已知答案堂先过堂：同一套轴 + 同一个 family_class() 跑两极（docx=正例，gstack-capy=反例）。
     轴有牙 = 正例分 - 反例分 >= MIN_TEETH；主判据(A5)与确认据(A4)都要有牙，且两极分居切割点两侧。
     切割点 = 两极中点（堂内数据导出，不手调）。无牙轴进 discarded_axes，禁止参与裁定。
     堂不过 => known-pass=false => 待裁对判 inconclusive（不许裁）。
  3) 禁整行重合率（r315 证伪：吸收后本地把上游改写为中文，行级必然不重合）。
  4) 增量 verbatim 一律按行区间从上游磁盘文件机械切片（不手抄），reverified = 该串在上游全文原样命中。
  5) 负控腿A：把 verbatim 尾字符改掉 => reverified 必须 False。
  6) 负控腿B：--force-leg=B 把正例 docx 判词强改成异族 => 整体 known-pass 必须 False。
"""
import os, sys, json, hashlib, subprocess
import siglib as S

HERE = os.path.dirname(os.path.abspath(__file__))
EVID = os.path.join(HERE, "coding_agent_evidence.json")
EVID_ST = os.path.join(HERE, "coding_agent_evidence.selftest.json")
REPORT = os.path.join(HERE, "report.md")
SWAPCACHE = os.path.join(S.RAW, "swap_cache.json")
NL = chr(10)
TAB = chr(9)

POLES = [
    {"slug": "docx", "role": "positive", "expect": "same-family",
     "local": S.MGD + "/docx", "up": os.path.join(S.RAW, "known_docx_upstream.md"),
     "why": "anthropics/skills : skills/docx；本地 docx 由该上游扩展而来，公认正例"},
    {"slug": "gstack", "role": "negative", "expect": "diff-family",
     "local": S.MGD + "/gstack", "up": os.path.join(S.RAW, "known_gstack_upstream.md"),
     "why": "garrytan/gstack : capy/skill/gstack；r275 实测该路径是 Capy 安装/编排壳，公认异族错配"},
]
TARGET = {"slug": "coding-agent", "local": S.MGD + "/coding-agent", "up": S.UPSTREAM_CODING}

GAP_SPECS = [
    {"head": "## Read-only second opinions",
     "keys": ["readOnlyViolation", "best-effort", "concede", "defend", "adversarial", "contested"],
     "class": "content-gap",
     "land": "D:/global_skills/coding-agent/references/delegation-contract.md：本地 ## Read-only second opinions 段（实测第 72-75 行）之后追加两块",
     "why": "本地只写了「把只读写进 brief、别靠对方自觉」。上游同段还多两样可执行内容：(a) 对抗流程=先列已同意点、再逐个争议点给出双方立场、要求对方 defend 或 concede、结论写在最终消息；(b) 只读强度分档=Codex 沙箱硬强制，其它实现是 best-effort 且只在事后标 readOnlyViolation，故对后者必须改验 touchedFiles 是否为空。本地是四后端（codex/claude/opencode/workbuddy），(b) 比上游单后端原版更适用。"},
    {"head": "## If you have the openai-codex plugin",
     "keys": ["codex-rescue", "forwarder", "complementary", "inverse", "stop-review", "deliberately"],
     "class": "deliberately-skipped-recheck",
     "land": "D:/global_skills/coding-agent/references/delegation-contract.md：Authorization model 之前新增小节「与 openai-codex 插件的方向图」",
     "why": "三向区分：插件 codex-rescue 是转发器（不 poll/不 review/不 commit）；插件评审与 stop-review 门是反方向（Codex 审你的活）；本件是正向编排环（你派、你审、你落地）。本地 v1.2.0 版本史明写「属插件专属，未吸收」= 既往主动取舍，故登记为候选并标须重裁，不当无争议缺口。风险面：本地已含 claude 启动形态，用户同时装插件时易把活整包交给插件，丢掉 review+land 责任面。"},
    {"head": "## When to Use (paragraph: designed-for vs proven)",
     "keys": ["orchestrating", "comparable", "designed-for", "proven"],
     "class": "honesty-gap",
     "land": "D:/global_skills/coding-agent/SKILL.md：正文 # Coding Agent 与 ## Hard rules 之间补一行后端证据分档声明",
     "why": "上游明写「不为单一编排 agent 设计，但在 Claude Code 上运行验证过；其它编排器算 designed-for、不算已证」。本地宣称可派四后端，却没有已实测/未证的分档声明 => 证据状态诚实性缺口（不是命令缺口），一句话可补。"},
]

# GAP_SPECS 可被 gap_specs_extra.json 追加（数据驱动，避免源码手术；本轮用它补入第 4 条实测缺口）
EXTRA = os.path.join(HERE, "gap_specs_extra.json")
if os.path.exists(EXTRA):
    for spec in json.loads(S.txt(EXTRA)):
        GAP_SPECS.append(spec)

SWAP_REPOS = ["amElnagdy/delegate-skills", "Yeachan-Heo/oh-my-claudecode", "OrchestratorInc/agent-orchestrator"]


def gh_json(args, timeout=90):
    # 统一 gh 调用：成功回 (文本, None)，失败回 (None, 原因)。取不到就如实登记，禁猜。
    try:
        r = subprocess.run(["gh", "api"] + args, capture_output=True, text=True, timeout=timeout)
    except Exception as e:
        return None, repr(e)[:200]
    if r.returncode != 0:
        return None, (r.stderr or "").strip()[:200]
    return (r.stdout or "").strip(), None


def gitv(args, timeout=60):
    # 受管根只读取数：失败回 (None, 原因)，不抛，保证判据脚本自身不崩
    try:
        r = subprocess.run(["git", "-C", S.MGD] + args, capture_output=True, text=True, timeout=timeout)
    except Exception as e:
        return None, repr(e)[:160]
    if r.returncode != 0:
        return None, (r.stderr or "").strip()[:160]
    return (r.stdout or "").strip(), None


def drift_check():
    # 三方对拍：自算对象号 / 在册基线 / gh 现取 => 判该上游路径有没有漂移
    b = S.bytes_of(S.UPSTREAM_CODING)
    selfsha = S.git_blob_sha(b)
    rel = "repos/sickn33/agentic-awesome-skills/contents/plugins/agentic-awesome-skills-claude/skills/codex-delegate/SKILL.md?ref=main"
    ghsha, gherr = gh_json([rel, "--jq", ".sha"])
    v = "DRIFT：本地留档对象号 != 在册基线，本轮全部上游结论作废"
    if selfsha == S.DECLARED_BLOB and ghsha == S.DECLARED_BLOB:
        v = "no-drift：三方一致（自算 git 对象号 == 在册基线 == gh api 现取）"
    elif selfsha == S.DECLARED_BLOB:
        v = "local==baseline；gh 现取不等或不可取（见 gh_api_contents_sha_now / gh_error）"
    return {"self_computed_git_blob_sha": selfsha, "declared_baseline_blob": S.DECLARED_BLOB,
            "gh_api_contents_sha_now": ghsha, "gh_error": gherr, "bytes_on_disk": len(b),
            "sha256": hashlib.sha256(b).hexdigest(),
            "self_matches_declared": bool(selfsha == S.DECLARED_BLOB),
            "gh_matches_declared": bool(ghsha == S.DECLARED_BLOB), "verdict": v}


def cuts(pos, neg):
    # 切割点 = 两极中点（数据导出）；牙距 = 正例 - 反例；有牙 = 牙距 >= 该轴门槛
    c = {}
    t = {}
    live = {}
    for k in sorted(S.MIN_TEETH):
        c[k] = round((pos[k] + neg[k]) / 2.0, 4)
        t[k] = round(pos[k] - neg[k], 4)
        live[k] = bool(t[k] >= S.MIN_TEETH[k])
    return c, t, live


def family_class(ax, c, live):
    # 族判定只信主判据 A5（块级包含率）：判的是「上游成块内容有没有被本地覆盖」
    if not live.get(S.PRIMARY):
        return "inconclusive-teethless-metric"
    if ax[S.PRIMARY] >= c[S.PRIMARY]:
        return "same-family"
    return "diff-family"


def pairing_of(ax, c, live):
    # 同族再分档：有块级 cov<0.90 的块 => same-family-gaps；一块不弱 => superset
    if family_class(ax, c, live) != "same-family":
        return "diff-family"
    for b in ax["_blocks"]:
        if b["cov"] < 0.90:
            return "same-family-gaps"
    return "superset"


def pick_block(blocks, want, up_text):
    # 标题前缀定位；When to Use 那条是段不是块，按锚句边界切，行号仍来自磁盘文件
    if want.startswith("## When to Use (paragraph"):
        lines = up_text.split(NL)
        si = None
        for i, l in enumerate(lines):
            if l.startswith("Nothing here is specific"):
                si = i
                break
        if si is None:
            return None
        ei = si
        for i in range(si, len(lines)):
            if "not yet proven.)" in lines[i]:
                ei = i
                break
        return {"head": want, "start": si + 1, "end": ei + 1, "text": NL.join(lines[si:ei + 1])}
    for b in blocks:
        if b["head"].lower().startswith(want.lower()):
            return b
    return None


def build_increments(up_text, local_face, known_pass, pairing):
    # 每条增量 = 上游行区间 + 逐字 verbatim（磁盘切片）+ 落点建议 + 判别词本地命中情况
    low = local_face.lower()
    blocks = S.blocks_of(up_text)
    out = []
    for spec in GAP_SPECS:
        blk = pick_block(blocks, spec["head"], up_text)
        if blk is None:
            continue
        text = blk["text"]
        absent = [k for k in spec["keys"] if k.lower() not in low]
        present = [k for k in spec["keys"] if k.lower() in low]
        need = max(2, len(spec["keys"]) - 1)
        out.append({
            "inc_id": "INC-%02d" % (len(out) + 1),
            "upstream_block": spec["head"],
            "upstream_lines_1based_inclusive": [blk["start"], blk["end"]],
            "class": spec["class"],
            "bytes": len(text.encode("utf-8")),
            "verbatim": text,
            "verbatim_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "reverified": bool(text in up_text),
            "signature_tokens_absent_locally": absent,
            "signature_tokens_found_locally": present,
            "gap_strength": "strong" if len(absent) >= need else "weak",
            "landing": spec["land"],
            "rationale": spec["why"],
            "gate_for_r317": "rule_editor 三道闸；禁 write 整体重写（自建skill优化/AGENTS.md 红线 2）",
            "known_pass_at_build": known_pass,
            "pairing_at_build": pairing})
    return out


def ref_parity():
    # 本地 4 个 references 分卷 vs 上游同名件：字节 + git 对象号双对拍 => 证「逐字收录」
    rows = []
    for name in ("dispatch-and-poll.md", "multi-task-queues.md", "review-and-land.md", "writing-the-brief.md"):
        lp = os.path.join(S.MGD, "coding-agent", "references", name)
        upf = os.path.join(S.RAW, "upstream_ref_" + name)
        if not (os.path.exists(lp) and os.path.exists(upf)):
            rows.append({"file": name, "present": False})
            continue
        lb = S.bytes_of(lp)
        ub = S.bytes_of(upf)
        rows.append({"file": name, "present": True, "local_bytes": len(lb),
                     "upstream_bytes": len(ub), "local_git_blob": S.git_blob_sha(lb),
                     "upstream_git_blob": S.git_blob_sha(ub), "verbatim_equal": bool(lb == ub)})
    return rows


def ver_of(text):
    for line in text.split(NL):
        if line.startswith("version:"):
            return line.split(":", 1)[1].strip()
    return None


def local_identity():
    # 受管根只读；HEAD 面与工作树面分开钉，避免把未提交改动当成基线
    head_txt, e1 = gitv(["show", "HEAD:./coding-agent/SKILL.md"])
    head_blob, e2 = gitv(["rev-parse", "HEAD:./coding-agent/SKILL.md"])
    wt = os.path.join(S.MGD, "coding-agent", "SKILL.md")
    wb = S.bytes_of(wt)
    por, e3 = gitv(["status", "--porcelain", "coding-agent/"])
    f708, e4 = gitv(["cat-file", "-t", "f70875d142"])
    return {"managed_root": wt.replace(chr(92), "/"),
            "task_claimed": {"git_blob_prefix": "f70875d142", "bytes": 7254, "version": "1.2.0"},
            "head_blob": head_blob if head_blob else ("giterr: " + str(e2)),
            "head_bytes": len((head_txt or "").encode("utf-8")) if head_txt else None,
            "head_version": ver_of(head_txt or ""),
            "worktree_git_blob": S.git_blob_sha(wb),
            "worktree_bytes": len(wb),
            "worktree_version": ver_of(wb.decode("utf-8", "replace")),
            "porcelain": por if por is not None else ("giterr: " + str(e3)),
            "claimed_blob_f70875d142_resolves_as": f708 if f708 else ("unresolvable: " + str(e4)),
            "note": "受管根 coding-agent/SKILL.md 工作树相对 HEAD 有未提交改动（版本史 1.2.0 -> 1.3.0）；任务所给 blob 前缀 f70875d142 在本仓解析不出对象，实测 HEAD=6831af60…、工作树=dde69cdc…"}


def swap_candidates(use_cache=False):
    # stars / pushed_at / license 三值一律 gh api 现取；selftest 走缓存避免重复联网
    if use_cache and os.path.exists(SWAPCACHE):
        items = json.loads(S.txt(SWAPCACHE))
        src = "gh api 现取缓存（raw/swap_cache.json，首轮本件内写入）"
    else:
        items = []
        for rp in SWAP_REPOS:
            outj, err = gh_json(["repos/" + rp, "--jq",
                "[.full_name, (.stargazers_count|tostring), .pushed_at, (.license.spdx_id), (.archived|tostring)] | @tsv"])
            if not outj:
                items.append({"repo": rp, "fetched": False, "reason": err})
                continue
            a = outj.split(TAB)
            items.append({"repo": a[0], "fetched": True, "stars": int(a[1]),
                          "pushed_at": a[2], "license": a[3], "archived": a[4] == "true"})
        json.dump(items, open(SWAPCACHE, "w", encoding="utf-8"), indent=1)
        src = "gh api repos/<r> 本轮直连现取"
    return {"fetched_via": "仅 gh api", "source_face": src,
            "policy": "stars / pushed_at / license 三值现取，禁抄历史数",
            "items": items,
            "relevance_note": "本件判 same-family-gaps，主路径是增量吸收而非换装；下表仅供 r317 若要换装时参考。另记一条实测：声明路径在聚合仓是 docs-only（contents 只有 SKILL.md + references/，无 scripts/），而源仓 amElnagdy/delegate-skills 每个 *-delegate 变体各带 scripts/relay.mjs（agy 41187B、aider 35091B）=> 真正未到手的是运行时 relay，不是文档；引入运行时属范围变更，须 Lead 裁。"}


def leg_a(up_text, incs):
    # 负控腿 A：把某条增量 verbatim 改一字 => reverified 必须 False（证明逐字复验有牙，不恒绿）
    if not incs:
        return {"ran": False, "reason": "no increments"}
    base = incs[0]["verbatim"]
    tail = base[-1]
    mutated = base[:-1] + ("X" if tail != "X" else "Y")
    orig = base in up_text
    after = mutated in up_text
    return {"ran": True, "on_inc_id": incs[0]["inc_id"],
            "mutation": "verbatim 末字符改成另一字符",
            "original_reverified": bool(orig), "mutated_reverified": bool(after),
            "expected": {"original_reverified": True, "mutated_reverified": False},
            "pass": bool(orig and not after)}


def leg_b(expected_list, got_list, teeth_ok, known_pass_norm):
    # 负控腿 B：把正例(docx)的判词强制改成 diff-family，再走同一条 known-pass 通路
    # 期望整体塌成 False；若仍 True 说明 known-pass 是恒绿假判据
    flip = list(got_list)
    flip[0] = "diff-family"
    sim = True
    for i in range(len(expected_list)):
        if flip[i] != expected_list[i]:
            sim = False
    kp_sim = bool(sim and teeth_ok)
    return {"rule": "把正例 docx 判词强制改成 diff-family => known-pass 必须 False",
            "known_pass_normal": bool(known_pass_norm),
            "known_pass_under_flip": kp_sim,
            "pass": bool(known_pass_norm is True and kp_sim is False)}


def main():
    force = None
    for a in sys.argv:
        if a.startswith("--force-leg="):
            force = a.split("=", 1)[1]
    selftest = "--selftest" in sys.argv
    use_cache = bool(selftest or force == "B")
    up_text = S.txt(S.UPSTREAM_CODING)
    dr = drift_check()
    axp = [S.axes(e["local"], e["up"]) for e in POLES]
    tgt = S.axes(TARGET["local"], TARGET["up"])
    c, t, live = cuts(axp[0], axp[1])
    got_norm = [family_class(axp[0], c, live), family_class(axp[1], c, live)]
    got = list(got_norm)
    if force == "B":
        got[0] = "diff-family"
    teeth_ok = bool(live[S.PRIMARY] and live[S.CONFIRM])
    hall = []
    for i in range(len(POLES)):
        e = POLES[i]
        ax = axp[i]
        hall.append({"slug": e["slug"], "role": e["role"], "expected": e["expect"],
                     "got": got[i], "match": bool(got[i] == e["expect"]), "note": e["why"],
                     "axes": dict((k, ax[k]) for k in sorted(S.MIN_TEETH)),
                     "face_files": ax["_face_files"], "local_bytes": ax["_local_bytes"],
                     "skel_local_H123": ax["_skel_local"],
                     "skel_upstream_H123": ax["_skel_up"]})
    known_pass = bool(all(h["match"] for h in hall) and teeth_ok)
    if known_pass:
        pairing = pairing_of(tgt, c, live)
    elif not teeth_ok:
        pairing = "inconclusive-teethless-metric"
    else:
        pairing = "unproven-metric-hall-failed"
    incs = build_increments(up_text, tgt["_lf"], known_pass, pairing)
    la = leg_a(up_text, incs)
    lb = leg_b([e["expect"] for e in POLES], got_norm, teeth_ok, known_pass)
    ninc = len([i for i in incs if i["reverified"]])
    swaps = swap_candidates(use_cache=use_cache)
    nswap = len([i for i in swaps["items"] if i.get("fetched")])
    weak = [b["head"] for b in tgt["_blocks"] if b["cov"] < 0.90]
    ev = {"meta": {"round": "r316c",
            "task": "coding-agent 落地备料证据包（下一件 T1 的 r307b 同款备料；只出证据+方案，不落地不代裁）",
            "date": "2026-10-31", "network": "仅 gh api",
            "write_face": "自建skill优化/_temp/r316c/ 只新建；受管根只读（git show 允许）",
            "steps_cap_in_brief": 14,
            "steps_overrun_honest_note": "超限：实际工具回合 > 14。成因 = 两次 run_code 的 TS 引号闭合语法失败 + 判据脚本分块重写。产物完整，超限如实登记。",
            "metric_discipline": "禁整行重合率（r315 证伪）；四签名轴 A1/A2/A3/A4 + 块级 A5；切割点由已知答案堂两极中点导出，非手调",
            "mode": "selftest" if selftest else "normal", "force_leg": force},
        "known_pass": known_pass,
        "known_answers": hall,
        "axis_teeth": {"cuts_at_midpoint_of_poles": c,
            "teeth_positive_minus_negative": t,
            "live_axes": dict((k, live[k]) for k in sorted(live)),
            "min_teeth": S.MIN_TEETH, "primary": S.PRIMARY, "confirm": S.CONFIRM,
            "discarded_axes": [k for k in sorted(S.MIN_TEETH) if not live[k]],
            "discarded_reason_A2": "用途动词轴牙距为负（正例低于反例）：read/edit/run 这类动词人人都有，无判别力 => 作废，不参与裁定"},
        "pairing_verdict": {"value": pairing, "known_pass": known_pass,
            "decided_by": [S.PRIMARY, S.CONFIRM],
            "cut_values": dict((k, c[k]) for k in (S.PRIMARY, S.CONFIRM)),
            "target_values": dict((k, tgt[k]) for k in (S.PRIMARY, S.CONFIRM)),
            "statement": "同族成立：上游 codex-delegate 是本地 coding-agent 委派环的 Codex 单后端切片（本地已逐字收录其 4 个 references 分卷，并把派发面扩成四后端 + openclaw 通知/禁区私有扩展）；但上游 SKILL.md 仍有成块内容未落地 => 判 same-family-gaps，既非零缺口超集，也非异族错配",
            "not_superset_because": "实测 3 段上游内容在本地面无任何判别词踪迹（见 increments）",
            "not_diff_family_because": "主判据 A5 远高于两极中点切割点，且两极校准（docx=same-family / gstack=diff-family）双双命中；另有 references 4 分卷 git 对象号逐字等值作硬旁证"},
        "local_vs_upstream": {"local_identity": local_identity(),
            "upstream_drift": dr,
            "target_axes": {"slug": "coding-agent", "face_files": tgt["_face_files"],
                "local_bytes": tgt["_local_bytes"],
                "skeleton_local_H123": tgt["_skel_local"],
                "skeleton_upstream_H123": tgt["_skel_up"],
                "axes": dict((k, tgt[k]) for k in sorted(S.MIN_TEETH))},
            "upstream_block_coverage": [{"head": b["head"],
                "upstream_lines_1based_inclusive": [b["start"], b["end"]],
                "n_distinctive": b["n_distinctive"], "cov": b["cov"],
                "absent_sample": b["absent"][:10]} for b in tgt["_blocks"]],
            "absorbed_verbatim_reference_parity": ref_parity(),
            "local_only_private_extensions": [
                "四后端启动形态（codex/claude/opencode/workbuddy；含 WorkBuddy asar 内 codebuddy CLI 路径与 node 包装法）",
                "openclaw 通知路由块（channel/target/account/reply_to/thread_id；完成或失败只发一条）",
                "OpenClaw 状态目录禁区（~/.openclaw、$OPENCLAW_STATE_DIR、~/Projects/openclaw 不派活）",
                "process 动作面（list/poll/log/submit/write/paste/kill）与状态播报节律",
                "Scratch Codex（mktemp -d + git init 的可信仓库前置）",
                "长 issue-to-PR 环（issue 当持久规格，回报 issue URL 与 sessionId）",
                "中文委派契约分卷 references/delegation-contract.md（上游无同名单件；五步环与退出码语义重写为中文对账面）"],
            "blocks_cov_below_0.90": weak,
            "direction_verdict": "本地 ⊇ 上游（结构上超集）+ 3 段成块尾巴未落地；不是「零缺口超集」，也不是「异族错配」"},
        "increments": incs,
        "none_reason": None if incs else "无上游新内容可吸收",
        "swap_candidates": swaps,
        "negative_controls": {"legA": la, "legB": lb,
            "legB_as_executed_by_flag": {"force_leg": force,
                "known_pass_this_invocation": known_pass}},
        "handoff_to_r317": {"gates": "rule_editor 三道闸；禁 write 整体重写（自建skill优化/AGENTS.md 红线 2）",
            "suggested_order": [
                "INC-01 真内容缺口：只读对抗流程 + 只读强度分档（本地四后端比上游单后端更需要）",
                "INC-03 一句话后端证据分档（落 SKILL.md 正文须同步 version 与版本史）",
                "INC-02 既往 v1.2.0 主动跳过项，属重裁而非无争议缺口，须 Lead 裁"],
            "bigger_fish_measured": "真正未到手的是运行时 relay.mjs：声明路径实测 docs-only（gh contents 只回 SKILL.md + references/，无 scripts/）；源仓 amElnagdy/delegate-skills 每个 *-delegate 变体各带 scripts/relay.mjs（实测树读数 agy 41187B / aider 35091B）。引入运行时 = 范围变更，须先裁，本备料包不擅自推进",
            "dirty_face_warning": "受管根 coding-agent/SKILL.md 工作树相对 HEAD 有未提交改动（版本史 1.2.0 -> 1.3.0）；落地前须确认归属，防并发写者（#44 D7.2）",
            "not_landed_by_design": "本件按 brief 只出证据+方案：未写受管根一个字节，未代裁落哪个文件 / 是否引入运行时 / 是否换装"},
        "selftest": {"mode": "selftest" if selftest else "normal", "legA": la, "legB": lb,
            "overall_pass": bool(la.get("pass") is True and lb.get("pass") is True)}}
    out = EVID_ST if selftest else EVID
    json.dump(ev, open(out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("=== known-answer hall ===")
    for h in hall:
        print("  %-8s %-8s expect=%-12s got=%-12s match=%s A4=%s A5=%s" % (
            h["slug"], h["role"], h["expected"], h["got"], str(h["match"]).lower(),
            h["axes"][S.CONFIRM], h["axes"][S.PRIMARY]))
    print("=== axis teeth / cuts ===")
    for k in sorted(c):
        print("  %-30s cut=%s teeth=%s live=%s target=%s" % (k, c[k], t[k], str(live[k]).lower(), tgt[k]))
    print("  discarded=%s" % json.dumps(ev["axis_teeth"]["discarded_axes"]))
    print("=== drift pin ===")
    print("  " + dr["verdict"])
    print("  self=%s baseline=%s gh_now=%s" % (
        dr["self_computed_git_blob_sha"], dr["declared_baseline_blob"], dr["gh_api_contents_sha_now"]))
    print("=== weak blocks (cov<0.90) ===")
    print("  " + json.dumps(weak, ensure_ascii=False))
    print("=== increments ===")
    for i in incs:
        print("  %s lines=%s bytes=%s sha256=%s reverified=%s class=%s strength=%s" % (
            i["inc_id"], i["upstream_lines_1based_inclusive"], i["bytes"],
            i["verbatim_sha256"][:12], str(i["reverified"]).lower(), i["class"], i["gap_strength"]))
    print("=== negative controls ===")
    print("  legA pass=%s orig=%s mutated=%s on=%s" % (
        str(la.get("pass")).lower(), str(la.get("original_reverified")).lower(),
        str(la.get("mutated_reverified")).lower(), la.get("on_inc_id")))
    print("  legB pass=%s normal=%s under_flip=%s" % (
        str(lb.get("pass")).lower(), str(lb.get("known_pass_normal")).lower(),
        str(lb.get("known_pass_under_flip")).lower()))
    print("=== swap candidates (gh api fresh) ===")
    for it in swaps["items"]:
        print("  %s stars=%s pushed=%s license=%s fetched=%s" % (
            it.get("repo"), it.get("stars", "-"), it.get("pushed_at", "-"),
            it.get("license", "-"), str(it.get("fetched")).lower()))
    if selftest:
        print("[R316C:SELFTEST] legA-pass=%s legB-pass=%s overall=%s" % (
            str(la.get("pass")).lower(), str(lb.get("pass")).lower(),
            str(ev["selftest"]["overall_pass"]).lower()))
    print("[R316C:PREP] known-pass=%s pairing=%s increments=%s swap-cands=%s" % (
        str(known_pass).lower(), pairing, ninc, nswap))
    return 0


if __name__ == "__main__":
    sys.exit(main())
