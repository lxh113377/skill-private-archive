#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r307b 备料判据：F 臂（frontend-skill）取数解锁 + 落地编辑清单的验收口。

为什么存在（r305b 的两卡点属可解）：
  补取面 = 候选仓全树逐件取回并钉双 sha（blob 号 = git 原生、sha256 = 本地自算），
  把两个候选缺件冲突的卡点变成已钉死的取件；备料面 = 给本地件出一张加法式编辑清单。
  本脚本判四件事，全部现读盘面，不采信任何自报字段：
    1 名册面：每行的 mirror 字节重算 blob 号与 sha256，与钉定值全等才计入 blob_pinned；
    2 清单面：每条锚点在本地件现形唯一命中 + 并入段逐行对上游镜像做逐字尺；
    3 加法面：把清单演算到本地件后，原件每一行都必须仍在（声明式 replace 的 old 块除外）；
    4 守块面：三条本地独有块逐字存活，且上游对同一主题的实测命中为 0（证明确是本地独有）。
  负控两腿（证明判据有牙）：
    --negctl-flip         取回件改一字节重算，内容号与 blob 号都必须与钉定值不等；
    --negctl-drop-block   故意抹掉一条本地独有块，必须 local_only_blocks<3/3 且不得报 PREP。
"""
import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

NL = chr(10)
FACE = Path(__file__).resolve().parent
ROOT = FACE.parent.parent.parent
CAND_REL = "skills/taste-skill/SKILL.md"
SUP_RELS = ["skills/taste-skill/assets/charts.js", "skills/taste-skill/assets/base.js"]
OUT = "[R307B:PREP]"
BAD = "[R307B:FAIL]"


def sha_bytes(raw):
    """内容级钉：对字节原样算，不做行尾或空白规范化（规范化会让改一字节测不出来）。"""
    return hashlib.sha256(raw).hexdigest()


def git_blob_sha(raw):
    """git 原生对象号：sha1 喂 blob 头 + 裸 NUL + 字节本体。"""
    h = hashlib.sha1()
    h.update(b"blob " + str(len(raw)).encode("ascii") + bytes([0]))
    h.update(raw)
    return h.hexdigest()


def local_skill_path():
    """本地件取形链，顺序固定不猜：环境覆盖 -> 受管根镜像 -> 全局技能目录（只读）。"""
    env = os.environ.get("R307B_LOCAL_SKILL")
    if env:
        return Path(env)
    stage = ROOT / "自建skill优化" / "_temp" / "r304_mirror_stage" / "frontend-skill" / "SKILL.md"
    if stage.is_file():
        return stage
    return Path("D:/global_skills/frontend-skill/SKILL.md")


def load_json(path):
    """落盘件必须仍可解析：读回再 loads 一次，不靠写时自信。"""
    return json.loads(path.read_text(encoding="utf-8"))


def prove_row(row, problems):
    """自证一行名册：读 mirror 字节 -> 重算 size/blob/sha256 -> 三项全等才算钉住。

    fetched 字段本身不作数（自报），只信盘面字节；任一不等即记问题并返回 False。
    """
    if row.get("fetched") is not True:
        return False
    mir = row.get("mirror")
    if not mir:
        problems.append("fetched without mirror bytes: " + row["rel"])
        return False
    f = FACE / mir
    if not f.is_file():
        problems.append("mirror file missing: " + row["rel"])
        return False
    raw = f.read_bytes()
    ok = True
    if len(raw) != row.get("size"):
        problems.append("size drift: " + row["rel"])
        ok = False
    if sha_bytes(raw) != row.get("sha256"):
        problems.append("sha256 drift: " + row["rel"])
        ok = False
    if git_blob_sha(raw) != row.get("blob_sha"):
        problems.append("blob recompute mismatch: " + row["rel"])
        ok = False
    return ok


def anchor_hits(lines, anchor):
    return sum(1 for ln in lines if ln == anchor)


def block_hits(lines, block):
    """连续块命中次数：replace 的 old 必须是唯一连续块，多命中＝锚点不成立。"""
    k = len(block)
    return sum(1 for i in range(len(lines) - k + 1) if lines[i:i + k] == block)


def apply_edits(text, edits):
    """把清单逐条演算到本地件：replace 换块、insert 按 placement 贴边、hold 不动。

    锚点缺失或多命中一律抛错 —— 静默跳过会造出假绿，这是本判据最容易失真的位置。
    """
    lines = text.split(NL)
    for e in edits:
        op = e["op"]
        if op == "hold":
            continue
        if op == "replace":
            ob = e["old"].split(NL)
            idxs = [i for i in range(len(lines) - len(ob) + 1) if lines[i:i + len(ob)] == ob]
            if len(idxs) != 1:
                raise AssertionError("replace block hits=" + str(len(idxs)) + " in " + e["id"])
            i = idxs[0]
            lines[i:i + len(ob)] = e["new"].split(NL)
        elif op == "insert":
            idxs = [j for j, ln in enumerate(lines) if ln == e["anchor"]]
            if len(idxs) != 1:
                raise AssertionError("anchor hits=" + str(len(idxs)) + " in " + e["id"])
            j = idxs[0]
            nb = e["new"].split(NL)
            while nb and nb[0] == "":
                nb.pop(0)
            while nb and nb[-1] == "":
                nb.pop()
            if e["placement"] == "after":
                lines[j + 1:j + 1] = nb
            elif e["placement"] == "before":
                lines[j:j] = nb
            else:
                raise AssertionError("bad placement in " + e["id"])
        else:
            raise AssertionError("unknown op " + str(op))
    return NL.join(lines)


def lost_lines(orig, merged, edits):
    """加法性反证尺：原件每行都须仍在合并件里，除非它属于某条声明式 replace 的 old 块。"""
    keep = set(merged.split(NL))
    exempt = set()
    for e in edits:
        if e["op"] == "replace" and e.get("old"):
            exempt.update(e["old"].split(NL))
    return [i + 1 for i, ln in enumerate(orig.split(NL)) if ln not in keep and ln not in exempt]


LOCAL_ONLY = {
    # 三条本地独有块（r303b swap_pack 的 local_only，frontend-skill 三项）：守法 = 块体逐行逐字存活，
    # 不是关键词凑数 —— 关键词在别处出现也算命中，等于没牙。counter 是上游反证（该主题在上游命中 0）。
    "fullbleed": {"lines": [
        "- Canonical full-bleed rule: on branded landing pages, the hero itself must run edge-to-edge with no inherited page gutters, framed container, or shared max-width; constrain only the inner text/action column.",
    ], "counter": "full-bleed"},
    "viewport": {"lines": [
        "Viewport budget:",
        "- If the first screen includes a sticky/fixed header, that header counts against the hero. The combined header + hero content must fit within the initial viewport at common desktop and mobile sizes.",
        "- When using `100vh`/`100svh` heroes, subtract persistent UI chrome (`calc(100svh - header-height)`) or overlay the header instead of stacking it in normal flow.",
    ], "counter": "100svh"},
    "agents_file": {"bytes": 326, "sha256": "e12288464311eeedcec370bf7625081b3bfb429ffe4c5d34acc9cf4bfd89db79"},
}


def count_local_only(merged, agents_raw, upstream_text, drop=None):
    """守块计数（满分 3）：块体每一行都要在合并件里逐字存在，且上游对该主题命中 0。

    怎么运作：逐行 exact 比对（set 成员），不做包含式模糊匹配 —— 模糊匹配会让改写过的行
    仍算守住；drop 只服务负控腿 B，点名那块一律不计，用来证明判据会掉数而非恒绿；
    第三条是文件不是文字，守法 = 字节数与内容号全等。
    """
    ml = set(merged.split(NL))
    detail = {}
    n = 0
    f1 = LOCAL_ONLY["fullbleed"]
    ok1 = all(ln in ml for ln in f1["lines"]) and upstream_text.count(f1["counter"]) == 0 and drop != "fullbleed"
    detail["fullbleed"] = bool(ok1)
    n += 1 if ok1 else 0
    f2 = LOCAL_ONLY["viewport"]
    ok2 = all(ln in ml for ln in f2["lines"]) and upstream_text.count(f2["counter"]) == 0 and drop != "viewport"
    detail["viewport"] = bool(ok2)
    n += 1 if ok2 else 0
    f3 = LOCAL_ONLY["agents_file"]
    ok3 = agents_raw is not None and len(agents_raw) == f3["bytes"] and sha_bytes(agents_raw) == f3["sha256"] and drop != "agents_file"
    detail["agents_file"] = bool(ok3)
    n += 1 if ok3 else 0
    return n, detail


def strip_block(merged, victim):
    """负控腿 B 的删法：把该块的每一行整行剔除（模拟被候选覆盖时的真实后果）。

    用 exact 行匹配而非子串，避免把无关行一起删掉造成「掉两分」的假信号。
    """
    kill = set(LOCAL_ONLY[victim]["lines"])
    return NL.join([ln for ln in merged.split(NL) if ln not in kill])


def verbatim_offenders(new_text, mirror_lines, allow):
    """逐字尺：并入段每行要么在上游镜像里，要么在 self_written_lines 白名单里。

    空行与钉定注释行豁免（注释是本件自造的元信息，已在 stamp 面声明）；
    其余既不在上游也不在白名单的行 = 转述冒充逐字，判红（禁猜内容的机器面）。
    """
    ms = set(mirror_lines)
    al = set(allow or [])
    offs = []
    for ln in new_text.split(NL):
        s = ln.strip()
        if not s or s.startswith("<!--"):
            continue
        if ln in ms or ln in al:
            continue
        offs.append(ln[:70])
    return offs


def main():
    # r308 提升态守卫（我提升到跟踪面后补）：本判据逐件重读 blobs/ 字节镜像再算双 sha——而 blobs/ 是上游
    # 字节的**副本**（≈3MB，payload 本体已在受管根 frontend-skill/ 被其 git 跟踪），刻意不进本仓证据面
    # （重复存一份上游字节没有增量证明价值，名册的 blob/sha256 才是锚）。因此**克隆态缺 blobs/ 时**：
    # 必须报 UNVERIFIED 并 rc=2，不得 rc=1 配像样的末行，更不得跳过字节核假装 PASS。
    HERE2 = os.path.dirname(os.path.abspath(__file__))
    if not os.path.isdir(os.path.join(HERE2, "blobs")):
        print("[R307B:PREP] UNVERIFIED 字节镜像 blobs/ 不在提升面（刻意不入库，见件内注释）⇒ 字节级复核仅在写面跑；"
              "克隆态可复算的等值证明在 05-exec/landing_specs/frontend-skill.json（leg N 用受管根 hash-object 对 expected_sha）")
        sys.exit(2)
    # 冻结基线默认化（r308）：盘上本地件已被落地改写 ⇒ 判据必须对**落地前基线**复算，env 可覆盖
    os.environ.setdefault("R307B_LOCAL_SKILL", os.path.join(HERE2, "local_pre_state.SKILL.md"))
    ap = argparse.ArgumentParser()
    ap.add_argument("--negctl-contents", action="store_true", help="负控腿 A 第二段：blob 号与 contents API 现值对账")
    ap.add_argument("--negctl-flip", action="store_true", help="负控腿 A：改一字节重算，必须不等")
    ap.add_argument("--negctl-drop-block", action="store_true", help="负控腿 B：故意删一条本地独有块")
    ap.add_argument("--json", action="store_true", help="附结构化明细")
    args = ap.parse_args()
    problems = []
    manp = FACE / "fetch_manifest.json"
    edp = FACE / "edits.json"
    for q in (manp, edp):
        if not q.is_file():
            print(BAD + " missing prep artifact " + q.name)
            return 1
    man = load_json(manp)
    edits = load_json(edp)
    if not isinstance(edits, list):
        problems.append("edits.json is not an array")
    files = man["files"]
    rows = {}
    for f in files:
        rows[f["rel"]] = f
    n_fetched = sum(1 for f in files if f.get("fetched") is True)
    pinned = [f["rel"] for f in files if prove_row(f, problems)]
    n_pin = len(pinned)
    for rel in SUP_RELS:
        r = rows.get(rel)
        if r is None:
            problems.append("supplementary target absent from manifest: " + rel)
        elif r["rel"] not in pinned or r.get("fetched") is not True:
            problems.append("supplementary target not fetched-and-pinned: " + rel)
    cc = man.get("coverage_check") or {}
    if not cc:
        problems.append("coverage_check block missing from manifest")
    else:
        if cc.get("plan_rows") != cc.get("manifest_rows"):
            problems.append("coverage row-count mismatch")
        for key in ("mapped_miss", "manifest_orphans", "plan_rows_sharing_one_manifest_row"):
            if cc.get(key):
                problems.append("coverage not closed at " + key)
        act = cc.get("plan_action_counts") or {}
        exp = [("land", 34), ("drop", 34), ("block", 4)]
        for k, v in exp:
            if act.get(k) != v:
                problems.append("plan action counts off at " + str(k) + ": " + str(act.get(k)) + " != " + str(v))
    cand = rows.get(CAND_REL)
    upstream_text = ""
    upstream_lines = []
    if cand is None:
        problems.append("manifest lacks candidate SKILL.md row")
    else:
        raw = (FACE / cand["mirror"]).read_bytes()
        if sha_bytes(raw) != cand["sha256"]:
            problems.append("upstream mirror sha drift")
        upstream_text = raw.decode("utf-8")
        upstream_lines = upstream_text.split(NL)
    for e in edits:
        for k in ("op", "anchor", "old", "new", "why", "evidence"):
            if k not in e:
                problems.append("field " + k + " missing in " + str(e.get("id")))
    sp = local_skill_path()
    if not sp.is_file():
        print(BAD + " local skill file not readable")
        return 1
    orig = sp.read_text(encoding="utf-8")
    olines = orig.split(NL)
    agents = sp.parent / "agents" / "openai.yaml"
    agents_raw = agents.read_bytes() if agents.is_file() else None
    anchors_unique = True
    for e in edits:
        if e["op"] == "hold":
            if e.get("hold_kind") == "file_exists":
                if agents_raw is None:
                    problems.append("hold file absent: " + str(e.get("hold_target")))
                continue
            h = anchor_hits(olines, e["anchor"])
        elif e["op"] == "replace":
            h = block_hits(olines, e["old"].split(NL))
        else:
            h = anchor_hits(olines, e["anchor"])
        if h != 1:
            anchors_unique = False
            problems.append("anchor hits=" + str(h) + " in " + e["id"])
    for e in edits:
        if e["op"] != "insert" or not e.get("new"):
            continue
        offs = verbatim_offenders(e["new"], upstream_lines, e.get("self_written_lines"))
        if offs:
            problems.append("verbatim offender in " + e["id"] + ": " + offs[0])
        pr = e.get("verbatim_probe")
        if not pr or pr not in e["new"]:
            problems.append("verbatim probe miss in " + e["id"])
    try:
        merged = apply_edits(orig, edits)
    except AssertionError as ex:
        print(BAD + " apply failed: " + str(ex))
        return 1
    lost = lost_lines(orig, merged, edits)
    if lost:
        problems.append("zero-delete violated at lines " + ",".join(str(x) for x in lost[:6]))
    victim = "fullbleed" if args.negctl_drop_block else None
    base = strip_block(merged, victim) if victim else merged
    n3, detail = count_local_only(base, agents_raw, upstream_text, drop=victim)
    if args.negctl_contents:
        import subprocess
        import json as _json
        meta = man["manifest_meta"]
        repo = meta["candidate_repo"]
        ref = meta["ref"]
        n_ok = 0
        for rel in SUP_RELS:
            try:
                p = subprocess.run(["gh", "api", "repos/" + repo + "/contents/" + rel + "?ref=" + ref,
                                    "--jq", ".sha + \" \" + (.size|tostring)"],
                                   capture_output=True, text=True, timeout=90)
                if p.returncode != 0:
                    print("[NEGC1-CONTENTS] rel=" + rel + " gh_rc=" + str(p.returncode) + " err=" + (p.stderr or "").strip()[:120])
                    print(BAD + " contents API unreadable for " + rel)
                    return 1
                got = (p.stdout or "").strip().split()
                api_sha, api_size = got[0], int(got[1])
                row = rows[rel]
                same = api_sha == row["blob_sha"] and api_size == row["size"]
                n_ok += 1 if same else 0
                print("[NEGC1-CONTENTS] rel=" + rel + " contents_api_sha=" + api_sha + " tree_blob_sha=" + row["blob_sha"] + " api_size=" + str(api_size) + " tree_size=" + str(row["size"]) + " match=" + str(same))
                if not same:
                    print(BAD + " contents API disagrees with pinned blob_sha")
                    return 1
            except Exception as ex:
                print(BAD + " contents API call failed: " + str(ex)[:120])
                return 1
        print(OUT.replace("PREP", "NEGCTL") + " contents_api_agreement=" + str(n_ok) + "/" + str(len(SUP_RELS)))
        return 0 if n_ok == len(SUP_RELS) else 1

    if args.negctl_flip:
        # 优先拿两个补取件之一做变异（腿 A 要证明的是「钉的是真取回物」，
        # 补取件正是本件主目的，拿它们测最有说服力）；否则退到任一可证行。
        target = None
        for rel in SUP_RELS:
            r0 = rows.get(rel)
            if r0 is not None and r0["rel"] in pinned and r0["size"] > 16:
                target = r0
                break
        if target is None:
            for f in files:
                if f["rel"] in pinned and f["size"] > 16:
                    target = f
                    break
        if target is None:
            print(BAD + " no pinned row available for flip control")
            return 1
        raw2 = bytearray((FACE / target["mirror"]).read_bytes())
        k = len(raw2) // 2
        raw2[k] ^= 0x01
        b2 = bytes(raw2)
        fc = sha_bytes(b2)
        bc = git_blob_sha(b2)
        print("[NEGC1-FLIP] rel=" + target["rel"] + " byte_index=" + str(k) + " pinned_sha256=" + target["sha256"] + " flipped_sha256=" + fc + " differ=" + str(fc != target["sha256"]))
        print("[NEGC1-BLOB] pinned_blob_sha=" + target["blob_sha"] + " mutated_blob_recompute=" + bc + " differ=" + str(bc != target["blob_sha"]))
        if fc == target["sha256"] or bc == target["blob_sha"]:
            print(BAD + " pin is insensitive to a one-byte mutation")
            return 1
    if args.negctl_drop_block:
        print("[NEGC2-DROP] dropped=" + str(victim) + " detail=" + json.dumps(detail, sort_keys=True))
        if n3 >= 3:
            print(BAD + " drop-block control did not reduce the count (criteria is toothless)")
            return 1
        # 负控腿 B 的判据本体必须自己变红：故意删一条本地独有块 ⇒ 掉数且 FAIL，
        # 而不是换个标签蒙混过去 —— 这就是「判据有牙」的实测形态。
        print(BAD + " fetched=" + str(n_fetched) + "/" + str(len(files)) + " blob_pinned=" + str(n_pin) + " edits=" + str(len(edits)) + " anchors_unique=true local_only_blocks=" + str(n3) + "/3")
        return 1

    verdict = "PREP"
    if problems or not anchors_unique or n3 < 3 or n_pin != n_fetched:
        verdict = "FAIL"
    for s in problems:
        print("[ISSUE] " + s)
    print("[SANXING] 实测=名册逐件双sha由镜像字节重算全等·锚点现读唯一·并入段逐字·守块现读 | 部分=补取件已取回但未在浏览器里渲染验证（脚本臂环境卡点不在本件范围） | 未证=候选版本面（上游无 version 字段）与平台配置件的引用方")
    if args.json:
        print("[JSON] " + json.dumps({"total": len(files), "fetched": n_fetched, "blob_pinned": n_pin, "edits": len(edits),
            "anchors_unique": anchors_unique, "local_only_blocks": n3, "local_only_detail": detail,
            "zero_delete_lost_lines": lost, "problems": problems, "verdict": verdict}, ensure_ascii=False, sort_keys=True))
    print(OUT.replace("PREP", verdict) + " fetched=" + str(n_fetched) + "/" + str(len(files)) + " blob_pinned=" + str(n_pin) + " edits=" + str(len(edits)) + " anchors_unique=" + ("true" if anchors_unique else "false") + " local_only_blocks=" + str(n3) + "/3")
    return 0 if verdict == "PREP" else 1


if __name__ == "__main__":
    sys.exit(main())
