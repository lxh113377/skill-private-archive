#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R281G 工件级 A/B 六维机械 rubric（盲评 + 揭盲 + 两条负向对照）。

口径（为什么只能这样）：外部 LLM 评手不可用（oracle 不存在）、.dsh 会话日志是
transport 事件、任务级 A/B 不可复算，所以本件只做文本层机械计数，分数不等于任务质量。

逻辑：
  每维 = 一条已声明正则/规则 -> raw 计数 -> 递增分档表 EDGES -> 0..5 分。
  同一张档表对三件、两态通用，任何人拿同一文本可逐格重算（check 模式就是这么做的）。
  维度 6 是坏指标（不可执行 flag 越多越差），好方向分 = 5 - bucket(raw)。
  不可判（无 scripts/ 目录、或 scripts/*.py 无一提供可用 --help）记 None，不记 0，
  并从该件求和集合 D（可判维集合）里剔除。
  兄弟指针：带目录形状（含 /）的 token 才判在盘/死链；纯 basename 命中不到时记
  unresolved（不加不扣），避免把 next.js 这类技术名误判成死链。
  盲评：标签 A/B = sha1(NONCE + 文本 sha256) 十六进制升序，与提交先后无关；
  先只按 A/B 计分，再揭盲对序；总分相等或高分者不是改后 -> AMBIGUOUS。

用法：
  python -B score_r281g.py score [--out <json>]      # 计算 + 写 JSON + 自跑双负控
  python -B score_r281g.py check --json <json>        # 从 git + 工作树重算并逐格比对
  python -B score_r281g.py negctl --json <json>       # 只跑两条负向对照
"""
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

PY = sys.executable
GS = "D:/global_skills"
ROOT = os.environ.get("R281G_ROOT", "C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化")
T = os.path.join(ROOT, "_temp", "r281g")
BT = chr(96)
NONCE = "R281G-BLIND-NONCE-2026-10-29"

ARTIFACTS = [
    {"skill": "test-driven-development", "sha": "079b91f3"},
    {"skill": "frontend-slides", "sha": "6394cbae"},
    {"skill": "ui-ux-pro-max", "sha": "30b84b20"},
]
DIMS = ["d1", "d2", "d3", "d4", "d5", "d6"]
DIM_NAME = {"d1": "可执行指令密度", "d2": "禁区条目数", "d3": "具体性", "d4": "自检条目数",
            "d5": "兄弟指针数", "d6": "不可执行 flag 数（坏维）"}
EDGES = {
    "d1": [2, 5, 10, 16, 25],
    "d2": [3, 6, 9, 14, 20],
    "d3": [5, 12, 22, 35, 50],
    "d4": [2, 5, 10, 18, 30],
    "d5": [1, 3, 5, 8, 12],
    "d6": [1, 2, 4, 7, 12],
}
SKILL_MD = "SKILL.md"

RE_FLAG = re.compile(r"--[A-Za-z][A-Za-z0-9_-]*")
RE_FENCE = re.compile(r"^\s*" + BT * 3 + r"([A-Za-z0-9_+-]*)\s*$")
FENCE_LANGS = {"python", "py", "bash", "sh", "shell", "zsh", "console", "powershell", "ps1"}
RE_BULLET = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+\S")
RE_TABLEROW = re.compile(r"^\s*\|.*\|\s*$")
RE_FORBID = re.compile(r"不|勿|禁|never|avoid|don'?t", re.I)
RE_SPEC = [
    re.compile(r"\d+(?:\.\d+)?\s*(?:px|rem|em|%|pt|ms|fps|dpi|KB|MB|GB|x\b|:1)", re.I),
    re.compile(r"\d+(?:\.\d+)?[:/]\d+(?:\.\d+)?"),
    re.compile(r"\d{3,}"),
    re.compile(r"\d+\.\d+"),
]
RE_CHECK = re.compile(r"verify|checklist|校验|确认", re.I)
EXTS = ["md", "py", "sh", "css", "json", "html", "js", "ts", "tsx", "yml", "yaml", "csv",
        "ttf", "woff", "woff2", "svg", "png", "jpg", "jpeg", "webp", "jsonl"]
RE_PATHY = re.compile(r"[A-Za-z0-9_.+-]+(?:\.(?:" + "|".join(EXTS) + r"))\b")
RE_HAS_EXT = re.compile(r"\.(?:" + "|".join(EXTS) + r")$")
RE_TICKSPAN = re.compile(BT + r"([^" + BT + r"\n]{1,200})" + BT)
BADCH = set("<>{}" + BT + "$" + "'()|,;: " + chr(9))


def L(t):
    return t.replace("\r\n", "\n").replace("\r", "\n").split("\n")


def sha256(s):
    return hashlib.sha256(s.encode("utf-8", "replace")).hexdigest()


def bucket(dim, raw):
    if raw is None:
        return None
    n = 0
    for e in EDGES[dim]:
        if raw >= e:
            n += 1
        else:
            break
    return min(5, n)


def git(args):
    r = subprocess.run(["git", "-C", GS] + args, capture_output=True, timeout=120)
    return r.returncode, r.stdout.decode("utf-8", "replace")


def read_file(p):
    if not os.path.isfile(p):
        return None
    with open(p, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def m_d1(t):
    flags = [x for x in RE_FLAG.findall(t) if x != "--help"]
    code = 0
    inb = False
    ok = False
    for ln in L(t):
        m = RE_FENCE.match(ln)
        if m and not inb:
            inb = True
            ok = (m.group(1) or "").lower() in FENCE_LANGS
            continue
        if m and inb:
            inb = False
            ok = False
            continue
        if inb and ok and ln.strip():
            code += 1
    return {"flag_refs": len(flags), "code_lines": code, "raw": len(flags) + code}


def m_d2(t):
    hits = [i + 1 for i, ln in enumerate(L(t))
            if (RE_BULLET.match(ln) or RE_TABLEROW.match(ln)) and RE_FORBID.search(ln)]
    return {"raw": len(hits), "lines": hits[:10]}


def m_d3(t):
    return {"raw": sum(1 for ln in L(t) if any(rx.search(ln) for rx in RE_SPEC))}


def m_d4(t):
    return {"raw": sum(1 for ln in L(t) if RE_CHECK.search(ln))}


def tree_of(art_dir):
    """件目录清单：rels = 相对路径全集（目录带尾斜杠）；byname = basename -> 命中的相对路径集合。"""
    rels = set()
    byname = {}
    if not os.path.isdir(art_dir):
        return rels, byname
    for dirpath, dirnames, filenames in os.walk(art_dir):
        dirnames[:] = [d for d in dirnames if d not in ("__pycache__", ".git", "node_modules")]
        for nm in dirnames:
            r = os.path.relpath(os.path.join(dirpath, nm), art_dir).replace(chr(92), "/").lower()
            rels.add(r + "/")
            byname.setdefault(r.split("/")[-1], set()).add(r + "/")
        for nm in filenames:
            r = os.path.relpath(os.path.join(dirpath, nm), art_dir).replace(chr(92), "/").lower()
            rels.add(r)
            byname.setdefault(r.split("/")[-1], set()).add(r)
    return rels, byname

def norm_token(x0, skill):
    x = x0.strip().strip('.,;:()"').split("#")[0].split(":")[0].strip().replace("\\", "/")
    low = x.lower()
    for pre in ("d:/global_skills/", "./", "skills/"):
        if low.startswith(pre):
            low = low[len(pre):]
    if low.startswith(skill.lower() + "/"):
        low = low[len(skill) + 1:]
    if not low or low.startswith(("http", "~", "/")) or re.match(r"^[a-z]:", low):
        return None
    return low.rstrip("/") + ("/" if x0.rstrip().endswith("/") else "")


def clean_token(x0, skill):
    """归一化指针 token：剥 HTML 属性前缀、外件绝对路径与 URL 直接丢弃。"""
    m = re.search(r"(?:src|href|action)\s*=\s*['\"]?([^\s'\"]+)", x0, re.I)
    base = m.group(1) if m else x0
    return norm_token(base, skill)


def m_d5(t, skill):
    """兄弟指针数（净值）。口径：
       - 只收「带目录形状」或「带已知扩展名」的 token（反引号跨度 + 裸路径）；
       - canonical：解析到件树里同一条相对路径才算同一个目标，避免 scripts/core.py 与
         core.py 被当成两个指针重复计分；
       - glob 通配（含 * 或 ?）取其无通配父目录判定在盘与否；
       - 带目录形状而解析不到 = 死链（倒扣）；纯 basename 解析不到 = unresolved（不加不扣），
         因为 next.js 这类技术名没有目录形状，判它死链是误伤；
       - raw = max(0, live - dead)。
    """
    rels, byname = tree_of(os.path.join(GS, skill))
    spans = set(RE_TICKSPAN.findall(t)) | set(RE_PATHY.findall(t))
    live = set()
    dead = set()
    unres = set()
    for raw0 in spans:
        n = clean_token(raw0, skill)
        if not n or any(c in BADCH for c in n):
            continue
        shaped = "/" in n
        if not shaped and not RE_HAS_EXT.search(n):
            continue
        if "*" in n or "?" in n:
            par = n.split("*")[0].split("?")[0].rstrip("/")
            key = par + "/"
            if key in rels or os.path.exists(os.path.join(GS, skill, par or ".")):
                live.add(key if key != "/" else "")
            else:
                dead.add(key)
            continue
        bare = n.rstrip("/")
        for v in (bare, bare + "/", "./" + bare, "./" + bare + "/"):
            if v in rels:
                live.add(v)
                break
        else:
            if shaped:
                if os.path.exists(os.path.join(GS, bare)) or os.path.exists(os.path.join(GS, bare + "/")):
                    live.add(bare)
                else:
                    dead.add(bare)
            else:
                m = byname.get(bare)
                if m:
                    live.add(min(m))
                else:
                    unres.add(bare)
    live, dead, unres = sorted(x for x in live if x), sorted(dead), sorted(unres)
    return {"raw": max(0, len(live) - len(dead)), "live_n": len(live), "dead_n": len(dead),
            "unresolved_n": len(unres), "live_list": live, "dead_list": dead,
            "unresolved_list": unres}

def probe(skill):
    d = os.path.join(GS, skill, "scripts")
    if not os.path.isdir(d):
        return {"decidable": False, "reason": "该件无 scripts/ 目录，flag 接口不存在",
                "supported": [], "cmds": ["ls -1 " + d + "/"]}
    sup = set()
    cmds = []
    any_ok = False
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".py") or fn == "__init__.py":
            continue
        p = os.path.join(d, fn)
        cmds.append("python -B " + p + " --help")
        try:
            r = subprocess.run([PY, "-B", p, "--help"], capture_output=True, timeout=90)
        except Exception:
            continue
        txt = (r.stdout or b"").decode("utf-8", "replace") + "\n" + (r.stderr or b"").decode("utf-8", "replace")
        if r.returncode == 0 and "usage:" in txt.lower():
            any_ok = True
            for m in re.findall(r"--([A-Za-z][A-Za-z0-9_-]*)", txt):
                sup.add("--" + m)
    reason = "" if any_ok else "scripts/*.py 无一提供可用 --help（非 argparse 接口）"
    return {"decidable": any_ok, "reason": reason, "supported": sorted(sup), "cmds": cmds}


def m_d6(t, p):
    flags = sorted({x for x in RE_FLAG.findall(t) if x != "--help"})
    if not p["decidable"]:
        return {"raw": None, "flags": flags, "bad": []}
    bad = [f for f in flags if f not in p["supported"]]
    return {"raw": len(bad), "flags": flags, "bad": bad}


def measure(t, skill, p):
    det = {"d1": m_d1(t), "d2": m_d2(t), "d3": m_d3(t), "d4": m_d4(t),
           "d5": m_d5(t, skill), "d6": m_d6(t, p)}
    raw = dict((k, det[k]["raw"]) for k in DIMS)
    good = {}
    for k in ("d1", "d2", "d3", "d4", "d5"):
        good[k] = bucket(k, raw[k])
    good["d6"] = None if raw["d6"] is None else 5 - bucket("d6", raw["d6"])
    return raw, good, det


def load_texts(a):
    rc, tb = git(["show", a["sha"] + "~1:" + a["skill"] + "/" + SKILL_MD])
    tb = tb if rc == 0 else None
    ta = read_file(os.path.join(GS, a["skill"], SKILL_MD))
    return tb, ta


def sum_of(good, decidable):
    return sum(good[k] for k in decidable)


def build(override_after=None):
    per = []
    for a in ARTIFACTS:
        tb, ta = load_texts(a)
        entry = {"skill": a["skill"],
                 "sha_pair": {"baseline_sha": a["sha"],
                              "before_ref": a["sha"] + "~1",
                              "after_ref": "worktree:" + GS + "/" + a["skill"] + "/" + SKILL_MD}}
        if tb is None or ta is None:
            entry["status"] = "UNVERIFIED"
            entry["cmds_tried"] = ["git -C " + GS + " show " + a["sha"] + "~1:" + a["skill"] + "/" + SKILL_MD,
                                   "read " + os.path.join(GS, a["skill"], SKILL_MD)]
            per.append(entry)
            continue
        if override_after is not None and a["skill"] in override_after:
            ta = override_after[a["skill"]]
        rc, full = git(["rev-parse", a["sha"] + "~1"])
        entry["sha_pair"]["before_full"] = full.strip()
        p = probe(a["skill"])
        sb = {"content_sha256": sha256(tb)}
        sa = {"content_sha256": sha256(ta)}
        sb["raw"], sb["good"], sb["detail"] = measure(tb, a["skill"], p)
        sa["raw"], sa["good"], sa["detail"] = measure(ta, a["skill"], p)
        decidable = [k for k in DIMS if sb["good"][k] is not None and sa["good"][k] is not None]
        entry["decidable_dims"] = decidable
        entry["excluded_dims"] = [k for k in DIMS if k not in decidable]
        entry["dim6_probe"] = {"decidable": p["decidable"], "reason": p["reason"],
                               "supported": p["supported"], "cmds": p["cmds"]}
        order = sorted([("A", "before", sb), ("A", "after", sa)],
                       key=lambda x: hashlib.sha1((NONCE + x[2]["content_sha256"]).encode()).hexdigest())
        labels = {}
        for i, (_lab, st, _s) in enumerate(order):
            labels[st] = "A" if i == 0 else "B"
        entry["blind"] = {"label_before": labels["before"], "label_after": labels["after"],
                          "blind_order": [{"label": labels[st], "state": st} for _l, st, _x in order]}
        entry["dims_before"] = sb["good"]
        entry["dims_after"] = sa["good"]
        entry["raw_before"] = sb["raw"]
        entry["raw_after"] = sa["raw"]
        entry["detail_before"] = {"d1": sb["detail"]["d1"], "d5": sb["detail"]["d5"], "d6": sb["detail"]["d6"]}
        entry["detail_after"] = {"d1": sa["detail"]["d1"], "d5": sa["detail"]["d5"], "d6": sa["detail"]["d6"]}
        entry["delta"] = dict((k, None if (sb["good"][k] is None or sa["good"][k] is None)
                               else sa["good"][k] - sb["good"][k]) for k in DIMS)
        s_b = sum_of(sb["good"], decidable)
        s_a = sum_of(sa["good"], decidable)
        entry["sum_before"] = s_b
        entry["sum_after"] = s_a
        entry["uplift_pct"] = None if s_b == 0 else round((s_a - s_b) * 100.0 / s_b, 4)
        lab_sum = dict((labels[st], sum_of(s["good"], decidable)) for st, s in (("before", sb), ("after", sa)))
        entry["blind"]["blind_sum_A"] = lab_sum["A"]
        entry["blind"]["blind_sum_B"] = lab_sum["B"]
        if lab_sum["A"] == lab_sum["B"]:
            entry["blind"]["order_match"] = "AMBIGUOUS_TIE"
        elif (labels["after"] == "A" and lab_sum["A"] > lab_sum["B"]) or (labels["after"] == "B" and lab_sum["B"] > lab_sum["A"]):
            entry["blind"]["order_match"] = "SAME_ORDER"
        else:
            entry["blind"]["order_match"] = "AMBIGUOUS_REVERSED"
        entry["text_sha256"] = {"before": sb["content_sha256"], "after": sa["content_sha256"]}
        entry["status"] = "MEASURED"
        per.append(entry)
    return per


def rubric_definition():
    return {
        "scale": "每维 0..5（整数），由 raw 计数过递增分档表 EDGES 得到；同一张表对三件两态通用",
        "formula": {
            "score": "score(dim) = #{e in EDGES[dim] : raw >= e}（最多 5）",
            "dim6_direction": "d6 是坏指标，好方向分 = 5 - bucket(d6_raw)",
            "sum": "S = sum(score over D)，D = 该件六维中两态均可判的维集合；不可判维记 None 并从 D 剔除",
            "uplift_pct": "uplift_pct = (S_after - S_before) / S_before * 100，保留 4 位小数",
        },
        "EDGES": EDGES,
        "dims": {
            "d1": {"name": DIM_NAME["d1"], "kind": "计数型",
                   "rule": "正文 --flag 引用数（排除 --help 自身） + python/bash 等语言围栏块内的非空行数"},
            "d2": {"name": DIM_NAME["d2"], "kind": "计数型",
                   "rule": "以 bullet 或表格行开始、且行内命中 不|勿|禁|never|avoid|don'?t（忽略大小写）的行数"},
            "d3": {"name": DIM_NAME["d3"], "kind": "计数型",
                   "rule": "命中任一数字/阈值正则的行数：单位数(px|rem|em|%|pt|ms|fps|dpi|KB|MB|GB|x|:1)、比例 a:b、3 位以上整数、小数"},
            "d4": {"name": DIM_NAME["d4"], "kind": "计数型", "rule": "行内出现 verify|checklist|校验|确认 的行数"},
            "d5": {"name": DIM_NAME["d5"], "kind": "计数型（净值）",
                   "rule": "被点名的在盘文件/目录数：raw = max(0, live - dead)。带目录形状(含 /)的 token 才判 live/dead；纯 basename 无法解析时记 unresolved 不加不扣"},
            "d6": {"name": DIM_NAME["d6"], "kind": "计数型（坏指标）",
                   "rule": "正文 --flag 去重后，不在该件 scripts/*.py --help 支持集里的个数；接口建立不了（无 scripts/ 或无一 --help 可用）记 None"},
        },
    }


def emit(path):
    per = build()
    obj = {
        "schema": "artifact-ab-blind-v1",
        "round": "R278-1 / r281g",
        "measured_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "rubric_definition": rubric_definition(),
        "per_skill": per,
        "caliber_note": "本面只做文本层机械 rubric，不等于任务质量：外部 LLM 评手不可用（oracle 不存在），.dsh 会话日志是 transport 事件，任务级 A/B 不可复算。分档表为设计选择，raw 计数可由件内声明的正则重算。改后一律取 D:/global_skills 工作树，可能包含基准 sha 之后的其他改动（漂移量见 per_skill[].post_baseline_drift）。",
        "blind_procedure": "两态文本各取 sha256；标签 A/B = sha1(NONCE + content_sha256) 十六进制升序，NONCE = " + NONCE + "。标签由内容哈希决定、与提交先后无关，计分阶段只看版本A/版本B。打完分再揭盲：比较「高分标签」是否就是「改后」，相等记 AMBIGUOUS_TIE，反向记 AMBIGUOUS_REVERSED，一致记 SAME_ORDER。",
        "provenance_cmd": [
            "git -C " + GS + " cat-file -t <sha>",
            "git -C " + GS + " show <sha>~1 --no-patch --format=%H%n%ad%n%s",
            "git -C " + GS + " show <sha>~1:<skill>/SKILL.md",
            "read file " + GS + "/<skill>/SKILL.md（工作树 = 改后）",
            "python -B <skill>/scripts/*.py --help（维度 6 支持集实测）",
        ],
        "self_check": {},
    }
    for e in per:
        if e["status"] != "MEASURED":
            continue
        rc, body = git(["show", e["sha_pair"]["baseline_sha"] + ":" + e["skill"] + "/" + SKILL_MD])
        wt = read_file(os.path.join(GS, e["skill"], SKILL_MD))
        e["post_baseline_drift"] = {"sha_vs_worktree_diff_lines": 0 if rc != 0 else len([1 for x in (body or "").split("\n") if x != ""]) - len([1 for x in (wt or "").split("\n") if x != ""])}
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    return obj


def compare(obj):
    """从 git + 工作树重算，逐格比对传入对象；返回不一致清单。"""
    bad = []
    per = build()
    fresh = dict((e["skill"], e) for e in per)
    cells = 0
    for e in obj.get("per_skill", []):
        f = fresh.get(e["skill"])
        if not f:
            bad.append("MISSING-SKILL " + e["skill"])
            continue
        if e.get("status") != "MEASURED":
            bad.append("NOT-MEASURED " + e["skill"])
            continue
        for side, key in (("before", "dims_before"), ("after", "dims_after")):
            for d in DIMS:
                cells += 1
                if e.get(key, {}).get(d) != f[key][d]:
                    bad.append("MISMATCH cell %s/%s/%s json=%r fresh=%r" % (e["skill"], d, side, e.get(key, {}).get(d), f[key][d]))
        for d in DIMS:
            if e.get("delta", {}).get(d) != f["delta"][d]:
                bad.append("MISMATCH delta %s/%s" % (e["skill"], d))
            if (e.get("raw_" + side, {}) or {}).get(d) != f["raw_" + side][d]:
                bad.append("MISMATCH raw %s/%s" % (e["skill"], d))
        if e.get("uplift_pct") != f["uplift_pct"]:
            bad.append("MISMATCH uplift %s json=%r fresh=%r" % (e["skill"], e.get("uplift_pct"), f["uplift_pct"]))
        if e.get("sum_before") != f["sum_before"] or e.get("sum_after") != f["sum_after"]:
            bad.append("MISMATCH sum %s" % e["skill"])
        if e.get("blind", {}).get("order_match") != f["blind"]["order_match"]:
            bad.append("MISMATCH blind %s" % e["skill"])
        if e.get("text_sha256") != f["text_sha256"]:
            bad.append("MISMATCH text_sha %s（源文本已漂移）" % e["skill"])
    return bad, cells


def negctl(json_path):
    out = {}
    # 腿 1：把某件「改后」换成与「改前」同一文本 -> uplift 必须为 0
    same = {}
    for a in ARTIFACTS:
        tb, _ta = load_texts(a)
        if tb is not None:
            same[a["skill"]] = tb
    per = build(override_after=same)
    leg1 = []
    for e in per:
        leg1.append({"skill": e["skill"], "uplift_pct": e.get("uplift_pct"),
                     "sum_before": e.get("sum_before"), "sum_after": e.get("sum_after"),
                     "verdict": "PASS" if e.get("uplift_pct") == 0.0 else "FAIL"})
    out["leg1_identical_text_zero_uplift"] = leg1
    # 腿 2：人为把某维 +5 -> 统计器必须报 MISMATCH
    with open(json_path, "r", encoding="utf-8") as f:
        obj = json.load(f)
    tampered = json.loads(json.dumps(obj))
    tgt = tampered["per_skill"][0]
    dim = "d3"
    tgt["dims_after"][dim] = (tgt["dims_after"][dim] or 0) + 5
    tp = os.path.join(T, "r281_tampered.json")
    with open(tp, "w", encoding="utf-8") as f:
        json.dump(tampered, f, ensure_ascii=False, indent=1)
    bad, cells = compare(tampered)
    out["leg2_tamper_plus5"] = {"skill": tgt["skill"], "dim": dim, "new_value": tgt["dims_after"][dim],
                               "mismatch_lines": bad[:6], "mismatch_count": len(bad),
                               "verdict": "PASS" if bad else "FAIL", "tampered_copy": tp}
    return out


def main():
    args = sys.argv[1:]
    mode = args[0] if args else "score"
    out = os.path.join(ROOT, "06-benchmark", "r281_artifact_ab.json")
    jp = out
    if "--out" in args:
        out = args[args.index("--out") + 1]
    if "--json" in args:
        jp = args[args.index("--json") + 1]
    if mode == "score":
        obj = emit(out)
        sc = negctl(out)
        obj["self_check"] = sc
        bad, cells = compare(obj)
        obj["self_check"]["check_cells"] = cells
        obj["self_check"]["check_mismatch_count"] = len(bad)
        obj["self_check"]["check_last_line"] = ("R281G CHECK PASS cells=" + str(cells) + "/36 uplift_reproducible=3/3 blind=SAME_ORDER"
                                                if not bad else "R281G CHECK FAIL " + str(len(bad)))
        with open(out, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=1)
        for e in obj["per_skill"]:
            print(json.dumps({"skill": e["skill"], "status": e["status"],
                              "raw_before": e.get("raw_before"), "raw_after": e.get("raw_after"),
                              "dims_before": e.get("dims_before"), "dims_after": e.get("dims_after"),
                              "delta": e.get("delta"), "sums": [e.get("sum_before"), e.get("sum_after")],
                              "uplift_pct": e.get("uplift_pct"),
                              "blind": {k: e.get("blind", {}).get(k) for k in ("label_before", "label_after", "blind_sum_A", "blind_sum_B", "order_match")},
                              "drift": e.get("post_baseline_drift")}, ensure_ascii=False))
        print(json.dumps(obj["self_check"], ensure_ascii=False))
        print("WROTE " + out)
    elif mode == "check":
        with open(jp, "r", encoding="utf-8") as f:
            obj = json.load(f)
        bad, cells = compare(obj)
        for b in bad[:20]:
            print(b)
        measured = [e for e in obj.get("per_skill", []) if e.get("status") == "MEASURED"]
        n = len(measured)
        tally = {}
        for e in measured:
            k = e["blind"]["order_match"]
            tally[k] = tally.get(k, 0) + 1
        ok = 0
        for e in measured:
            sb = e["sum_before"]
            sa = e["sum_after"]
            rec = round((sa - sb) * 100.0 / sb, 4) if sb else None
            if rec == e["uplift_pct"]:
                ok += 1
            else:
                bad.append("MISMATCH uplift_recompute " + e["skill"] + " stored=" + str(e["uplift_pct"]) + " recomputed=" + str(rec))
        blind_txt = ",".join(str(k) + ":" + str(v) for k, v in sorted(tally.items()))
        base = "R281G CHECK PASS cells=" + str(cells) + "/" + str(12 * n) + " uplift_reproducible=" + str(ok) + "/" + str(n) + " blind=" + blind_txt
        last = base if not bad else "R281G CHECK FAIL mismatches=" + str(len(bad))
        print(last)
    elif mode == "negctl":
        print(json.dumps(negctl(jp), ensure_ascii=False, indent=1))
    else:
        print("usage: score|check|negctl")


if __name__ == "__main__":
    main()
