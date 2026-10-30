# -*- coding: utf-8 -*-
"""check_r290s.py — security-audit 换装材料（R289-5 第 1-4 步）的自证判据（七条腿 + 六负控）。

只读纪律：本件在任何模式（含 --neg、含不带 --dry）都**不写盘**、不改受管根（红线 2）。
补丁只在内存副本上按 rule_editor._plan_patches 同口径重放（rule_editor.py:1400-1422：
顺序 find、命中数不为 1 即失败、后续项可命中前项产生的新文本）。
--dry 只把需要外部取数的腿（git hash-object / node 跑 usage）换成 coords.json 存档的同源读数，
供离线自检；零写入性质不变。

七条腿：
  A anchors  每个 old 必须是目标件盘上原文的行对齐逐字切片且 count==1（现场重算，不信 _verify 自报）
  B verbatim 暂存校验器与上游 blob 逐字节等值（git hash-object == gh api .sha + size）；分卷逐字含 segments.json 每个上游行区间
  C license  许可门现取：05-exec/r114_replacement_scan.py 单源 classify_body / license_class / LICENSE_CAPS，并与 license_gate.md 存档读数对账
  D links    换装后面（SKILL.md / .upstream 的内存重放结果）与本目录两份 md 的每个相对 markdown 引用
             必须在虚拟 FS（受管根在盘件 ∪ 暂存新件）落地；解析复用 05-exec/r220_md_deadlink.py 的 scan_lines（围栏感知单源）
  E exec     文中写明的校验器调用形态与脚本真实 usage 一致（上游 usage 零 flag ⇒ 文档不得给该脚本写任何 flag）；且写明 Windows 实测限制
  F version  frontmatter version/last_updated、版本史首行、coords.json 三处一致；侧车吸收注内 sha == coords.head_sha
  G drift    两个数组件与 patch_material.json 的 (id, old, new) 逐字同源且集合等价（一个 --file 一份）

负控（--neg NAME，全部内存构造，用完不留副本）：
  anchor-absent  old 改一个字符               => A 判红并点名 id
  anchor-multi   old 换成盘上重复最多的行     => A 判红并点名 id
  deadlink       注入一条指向不存在文件的引用 => D 判红
  order          撤掉暂存新件认领（先补丁后建件）=> D 判红
  argflag        往调用行塞一个脚本不认的长参数 => E 判红
  drift          数组件 old 改一个字符         => G 判红并点名 id

用法：python -B _repro/r290s/check_r290s.py [--dry] [--only A|B|C|D|E|F|G] [--neg NAME]
末行：[SEC-AUDIT-PREP] hunks=<n> old_unique=<n>/<n> license=<spdx> gate=PASS|FAIL
退出码：0 全绿 / 1 任一判红（含负控该红却绿）/ 2 材料件不可读。
"""
import argparse
import collections
import hashlib
import importlib.util
import io
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SKILL = "D:/global_skills/security-audit"
UP = os.path.join(HERE, "upstream")
STAGE = os.path.join(HERE, "staging", "security-audit")
CJS_REL = "scripts/validate-coverage-ledger.cjs"
VOL_REL = "references/upstream-cloudflare-sec.md"
NL = chr(10)
TWO_DASH = chr(45) * 2


def read_text(path):
    """逐字读：newline 传空串保住原行尾，切片才可能与盘上一字不差。"""
    with io.open(path, encoding="utf-8", newline="") as f:
        return f.read()


def jload(name):
    return json.loads(read_text(os.path.join(HERE, name)))


def load_single(path_part, alias):
    """按路径加载仓内单源件：顶层只有常量与函数，main 在 __main__ 守卫内 ⇒ import 无副作用。"""
    mod = os.path.join(ROOT, path_part)
    if not os.path.exists(mod):
        raise SystemExit("FATAL: 单源判据不可读 " + mod)
    spec = importlib.util.spec_from_file_location(alias, mod)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def load_material():
    """缺件即退（零输入禁记绿，R247）。"""
    need = ("patch_material.json", "patch_local.json", "patch_upstream.json",
            "coords.json", "segments.json", "license_gate.md", "verifications.md")
    for n in need:
        if not os.path.exists(os.path.join(HERE, n)):
            raise SystemExit("FATAL: 材料件缺失 " + n)
    mat = jload("patch_material.json")
    comps = {}
    for c in mat["components"]:
        comps[c["file"]] = jload(c["file"])
    return mat, comps, jload("coords.json"), jload("segments.json")


def row_aligned(base, old):
    """old 必须等于 base 的某个整行区间：证明是逐字切片，不是手打拼接，也不含多余空行。"""
    if not old.endswith(NL) or (NL + NL + NL) in old:
        return False
    lines = base.split(NL)
    want = old.split(NL)[:-1]
    span = len(lines) - len(want) + 1
    for i in range(span):
        if lines[i:i + len(want)] == want:
            return True
    return False


def replay(items):
    """内存重放（rule_editor 同口径）。"""
    originals, work, errs = {}, {}, []
    for it in items:
        t = it["target"]
        if t not in originals:
            originals[t] = read_text(t)
            work[t] = originals[t]
        n = work[t].count(it["old"])
        if n != 1:
            errs.append(it["id"] + "(count=" + str(n) + ") @ " + os.path.basename(t))
            continue
        work[t] = work[t].replace(it["old"], it["new"], 1)
    return originals, work, errs

# ---- 七条腿 ---------------------------------------------------------------
def leg_a(items, neg):
    """A：逐 old 现场重算 count==1 + 行对齐切片 + old/new 行尾对称（不信任 _verify 自报）。

    neg=anchor-absent 把第一个 old 末位改一个字符；neg=anchor-multi 换成盘上重复最多的整行
    （运行时 Counter 现挑，不硬编码 —— 硬编码曾造成负控恒绿，r287m 教训）。
    """
    probe = [dict(x) for x in items]
    if neg == "anchor-absent":
        o = probe[0]["old"]
        probe[0]["old"] = o[:-2] + "Z" + o[-1]
    elif neg == "anchor-multi":
        base = read_text(probe[0]["target"])
        counter = collections.Counter(x for x in base.split(NL) if x.strip())
        dup = counter.most_common(1)[0][0]
        probe[0]["old"] = dup + NL
    originals, work, errs = replay(probe)
    broken = []
    ok_n = 0
    for src_it, pr in zip(items, probe):
        base = originals.get(src_it["target"]) or read_text(src_it["target"])
        n = base.count(pr["old"])
        aligned = row_aligned(base, pr["old"])
        tail_ok = pr["old"].endswith(NL) == pr["new"].endswith(NL)
        good = (n == 1 and aligned and tail_ok)
        if not good:
            tag = "count" + str(n) + "/align" + ("Y" if aligned else "N") + "/tail" + ("Y" if tail_ok else "N")
            broken.append(src_it["id"] + "(" + tag + ")")
        else:
            ok_n = ok_n + 1
    bad = bool(broken) or bool(errs)
    detail = ",".join(broken + errs) if bad else "-"
    last = ("[R290S-A-ANCHORS] hunks=" + str(len(items)) + " old_unique=" + str(ok_n) + "/"
            + str(len(items)) + " seq_errs=" + str(len(errs)) + " broken=" + detail)
    return (not bad), ok_n, len(items), last, work


def virtual_fs(claim_new):
    """D 腿落地面：受管根 security-audit 在盘件 ∪（暂存新件，claim_new=True 才认领）。

    claim_new=False 等价「先打补丁、后建新件」那一刻的盘 ⇒ 新指针必成死链（顺序约束的牙）。
    """
    rel = set()
    for dp, dn, fn in os.walk(SKILL):
        if (os.sep + ".git" + os.sep) in (dp + os.sep):
            continue
        for f in fn:
            rel.add(os.path.relpath(os.path.join(dp, f), SKILL).replace(os.sep, "/"))
    if claim_new:
        for dp, dn, fn in os.walk(STAGE):
            for f in fn:
                rel.add(os.path.relpath(os.path.join(dp, f), STAGE).replace(os.sep, "/"))
    return rel


def is_abs(u):
    """绝对路径 / URL 判定（含 :// 、以 / 开头、或盘符形式）。"""
    return ("://" in u) or u.startswith("/") or (len(u) > 1 and u[1] == ":")


def resolve(kind, key, files):
    """引用落地：skill 面以受管根为基准，here 面以 _repro/r290s 为基准，两者都兜底查仓根。"""
    if kind == "skill":
        return (key in files) or os.path.exists(os.path.join(SKILL, key))
    return (os.path.exists(os.path.join(HERE, key))
            or os.path.exists(os.path.join(ROOT, key))
            or (key in files)
            or os.path.exists(os.path.join(SKILL, key)))


def leg_d(work, neg):
    """D：换装后 SKILL.md / .upstream 与本目录两份 md 的相对引用必须落地。

    链接解析复用 05-exec/r220_md_deadlink.py 的 scan_lines（围栏感知 + 占位符跳过）：
    本件不重写正则 —— 两处口径漂移正是 R260-5 反对的。
    neg=order 撤掉暂存认领；neg=deadlink 注入一条本不存在的引用。
    """
    r220 = load_single(os.path.join("05-exec", "r220_md_deadlink.py"), "r220_ss")
    claim = (neg != "order")
    files = virtual_fs(claim)
    sk_md = SKILL + "/SKILL.md"
    docs = []
    for path in (sk_md, SKILL + "/.upstream"):
        txt = work.get(path) or read_text(path)
        if neg == "deadlink" and path == sk_md:
            txt = txt + NL + "[ghost](./nope_r290s_unwritten.md)" + NL
        docs.append(("skill", path, txt))
    for name in ("license_gate.md", "verifications.md"):
        txt = read_text(os.path.join(HERE, name))
        if neg == "deadlink" and name == "verifications.md":
            txt = txt + NL + "[ghost](./nope_r290s_unwritten.md)" + NL
        docs.append(("here", name, txt))
    dead = []
    total = 0
    for kind, src_name, txt in docs:
        for lineno, target in r220.scan_lines(txt):
            u = target.split("#")[0].split("?")[0].strip()
            if not u or u in ("URL", "url") or "<" in u or ">" in u:
                continue
            total = total + 1
            key = u.replace("./", "")
            if ("://" in u) or u.startswith(("http:", "https:", "mailto:", "data:", "//")):
                continue
            if is_abs(u):
                if not os.path.exists(u):
                    dead.append(kind + ":" + src_name + ":" + str(lineno) + "->" + u)
                continue
            if not resolve(kind, key, files):
                dead.append(kind + ":" + src_name + ":" + str(lineno) + "->" + u)
    last = ("[R290S-D-LINKS] claim_new=" + ("Y" if claim else "N") + " links=" + str(total)
            + " dead=" + str(len(dead)) + " detail=" + (";".join(dead[:6]) if dead else "-"))
    return (not dead), len(dead), last

def leg_b(segments, coords, dry):
    """B：暂存新件逐字节等值 + 分卷逐字含每个上游行区间。

    等值判据 = git hash-object(暂存件) == gh api .sha（blob 口径）且字节数 == api .size。
    dry 改用 coords.json 里存档的同源读数（同一条命令产生，非手抄）。
    """
    cjs_stage = os.path.join(STAGE, CJS_REL)
    vol_stage = os.path.join(STAGE, VOL_REL)
    if not (os.path.exists(cjs_stage) and os.path.exists(vol_stage)):
        miss = " staged_missing cjs=" + str(os.path.exists(cjs_stage)) + " vol=" + str(os.path.exists(vol_stage))
        return False, 0, "[R290S-B-VERBATIM]" + miss
    ev = coords["verbatim_evidence"]
    api_sha = ev["cjs_api_sha"]
    api_size = ev["cjs_size"]
    mode = "dry"
    local_hash = ev["cjs_git_hash_object"]
    if not dry:
        mode = "live"
        local_hash = subprocess.run(["git", "hash-object", cjs_stage], capture_output=True, text=True).stdout.strip()
    size = os.path.getsize(cjs_stage)
    same_blob = (local_hash == api_sha and size == api_size)
    UL = read_text(os.path.join(UP, "SKILL.md")).split(NL)
    vol = read_text(vol_stage)
    miss = []
    for s in segments:
        seg_txt = NL.join(UL[s["a"] - 1:s["b"]]) + NL
        if seg_txt not in vol:
            miss.append(s["id"] + "(L" + str(s["a"]) + "-" + str(s["b"]) + ")")
    ok = same_blob and not miss
    last = "[R290S-B-VERBATIM] mode=" + mode + " cjs=" + str(size) + "B blob=" + local_hash[:12]
    last = last + " api=" + api_sha[:12] + " equal=" + ("Y" if same_blob else "N")
    last = last + " slices=" + str(len(segments)) + " missing=" + (",".join(miss) if miss else "-")
    last = last + " vol=" + str(os.path.getsize(vol_stage)) + "B"
    return ok, len(segments), last


def leg_c(coords):
    """C：许可门现取（单源 classify_body / license_class / LICENSE_CAPS）并与 license_gate.md 对账。

    档位落 copyleft / weak-copyleft / restricted / none / unknown，或命中受限措辞，或存在 risky 件
    ⇒ 判 MUST_NOT_MERGE。对账防「文档写 MIT 而现算不是」这种读数漂移。
    """
    m = load_single(os.path.join("05-exec", "r114_replacement_scan.py"), "r114_ss")
    lic = read_text(os.path.join(UP, "LICENSE"))
    spdx, body_class, hits = m.classify_body(lic.upper())
    api = coords["upstream"]["license_spdx"]
    final = m.license_class(api, body_class)
    cap = m.LICENSE_CAPS.get(final)
    md = read_text(os.path.join(HERE, "license_gate.md"))
    want = "spdx=" + str(spdx) + " class=" + str(final) + " cap=" + str(cap)
    md_ok = want in md
    risky = coords.get("license_risky_files") or []
    ok = (spdx == "MIT" and final == "permissive" and cap == 5 and not hits and not risky and md_ok)
    verdict = "MAY_MERGE" if ok else "MUST_NOT_MERGE"
    last = "[R290S-C-LICENSE] api=" + str(api) + " body=" + str(spdx) + " class=" + str(final)
    last = last + " cap=" + str(cap) + " restricted_hits=" + str(len(hits))
    last = last + " md_reconcile=" + ("Y" if md_ok else "N") + " verdict=" + verdict
    return ok, str(spdx), last

def usage_of(dry):
    """校验器真实 usage 文本：live = 直接 node 跑该零依赖 .cjs；dry = coords.json 存档读数。"""
    ev = jload("coords.json")["verbatim_evidence"]
    if dry:
        return ev["cjs_usage_zero_arg"], "dry"
    r = subprocess.run(["node", os.path.join(STAGE, CJS_REL)], capture_output=True, text=True)
    txt = ((r.stderr or "") + (r.stdout or "")).strip()
    return txt, "live_rc" + str(r.returncode)


def leg_e(work, neg, dry):
    """E：文档写明的**调用形态**必须与脚本真实 usage 一致，并声明 Windows 实测限制。

    口径（防假红/假绿）：
      · 只把行内 code span 里「首 token 是 node、且含脚本名」的串当调用形态；
      · 该脚本 usage 是零 flag（只吃一个位置参数）⇒ 调用形态里出现任何 --flag 即假参数；
      · 同一行含「无 / 不得 / 禁 / 反例 / 负控 / 不支持」的散文提及不计（我们**要**在负控里写反例）；
      · 面里必须出现 no-follow 限制声明：本机 node 实跑该脚本读不了任何输入（实测 rc=1），
        不写这层 ⇒ 文档会让人以为 Windows 上跑一遍就能验台账。
    """
    sk = work.get(SKILL + "/SKILL.md") or read_text(SKILL + "/SKILL.md")
    face = sk + NL + read_text(os.path.join(HERE, "verifications.md"))
    if neg == "argflag":
        face = face + NL + "用法：`node validate-coverage-ledger.cjs --check-coverage ledger.json`" + NL
    usage_txt, mode = usage_of(dry)
    base = "validate-coverage-ledger.cjs"
    span_re = re.compile(chr(96) + "+([^" + chr(96) + "]+)" + chr(96) + "+")
    marks = ("无", "不得", "禁", "反例", "负控", "不支持", "拒")
    calls = []
    bad_flag = []
    for line in face.split(NL):
        if base not in line:
            continue
        for span in span_re.findall(line):
            parts = span.strip().split()
            if parts and parts[0] == "node" and any(base in x for x in parts):
                calls.append(span.strip())
                prose = any(m in line for m in marks)
                for tok in parts:
                    if tok.startswith(TWO_DASH) and len(tok) > 2 and not prose:
                        bad_flag.append(tok)
    caveat = "no-follow" in face
    zero_flag_usage = ("Usage:" in usage_txt) and ("<path-to-coverage-ledger.json>" in usage_txt)
    ok = bool(calls) and bool(caveat) and not bad_flag and zero_flag_usage
    last = "[R290S-E-EXEC] mode=" + mode + " calls=" + str(len(calls)) + " usage_zero_flag=" + ("Y" if zero_flag_usage else "N")
    last = last + " bad_flags=" + str(len(bad_flag)) + " detail=" + (",".join(sorted(set(bad_flag))[:4]) if bad_flag else "-")
    last = last + " win_caveat=" + ("Y" if caveat else "N")
    return ok, len(calls), last

def leg_f(work, coords):
    """F：版本三处一致（frontmatter / 版本史首行 / coords）+ 侧车吸收注内 sha == coords.head_sha。"""
    sk = work.get(SKILL + "/SKILL.md") or read_text(SKILL + "/SKILL.md")
    side = work.get(SKILL + "/.upstream") or read_text(SKILL + "/.upstream")
    fm = ""
    fm_date = ""
    hist = ""
    hist_date = ""
    for line in sk.split(NL):
        if line.startswith("version: "):
            fm = line.split(": ", 1)[1].strip()
        elif line.startswith("last_updated: "):
            fm_date = line.split(": ", 1)[1].strip()
        elif (not hist) and line.startswith("- **") and ("** (" in line):
            hist = line.split("**")[1].strip()
            hist_date = line.split("(")[1].split(")")[0]
    want = coords["post_reskin"]["version"]
    want_date = coords["post_reskin"]["last_updated"]
    sha_ref = coords["upstream"]["head_sha"] in side
    ok = (fm == want and hist == want and fm_date == want_date and hist_date == want_date and sha_ref)
    last = "[R290S-F-VERSION] fm=" + str(fm) + "/" + str(fm_date) + " hist=" + str(hist) + "/" + str(hist_date)
    last = last + " coords=" + str(want) + "/" + str(want_date) + " sidecar_sha_ref=" + ("Y" if sha_ref else "N")
    return ok, fm, last


def leg_g(mat, comps, neg):
    """G：数组件与材料逐字同源（一个 --file 只吃一个目标件 ⇒ 必须两份、id 集合等价）。

    neg=drift 把 patch_local 首条 old 改一个字符 ⇒ 必须判红并点名 id。
    """
    by_id = {}
    for h in mat["hunks"]:
        by_id[h["id"]] = (h["old"], h["new"])
    errs = []
    seen = []
    for c in mat["components"]:
        items = comps[c["file"]]
        is_local = c["file"].endswith("patch_local.json")
        if is_local != (c["target"] == "security-audit/SKILL.md"):
            errs.append("组件与 target 不符: " + c["file"])
        for it in items:
            iid = it["id"]
            old = it["old"]
            if neg == "drift" and is_local and not seen:
                old = old[:-2] + "Q" + old[-1]
            if iid not in by_id:
                errs.append(iid + " 不在材料件 @ " + c["file"])
                continue
            if (old, it["new"]) != by_id[iid]:
                errs.append("DRIFT:" + iid + " @ " + c["file"])
            seen.append(iid)
    if sorted(seen) != sorted(by_id.keys()):
        errs.append("hunk 集合不等价")
    ok = not errs
    last = "[R290S-G-DRIFT] components=" + str(len(mat["components"])) + " ids=" + str(len(seen)) + "/" + str(len(by_id))
    last = last + " drift=" + (";".join(errs[:4]) if errs else "-")
    return ok, len(errs), last

# ---- 主流程 ---------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--dry", action="store_true", help="外部取数腿改用存档读数（仍零写入）")
    ap.add_argument("--only", default=None, help="只跑某条腿 A|B|C|D|E|F|G")
    ap.add_argument("--neg", default=None, help="负控：anchor-absent|anchor-multi|deadlink|order|argflag|drift")
    args = ap.parse_args()
    mat, comps, coords, segments = load_material()
    items = mat["hunks"]
    results = []
    ok_a, uniq, total, last_a, work = leg_a(items, args.neg)
    print(("PASS" if ok_a else "FAIL") + " A " + last_a)
    results.append(("A", ok_a))
    if args.only in (None, "B"):
        ok_b, nseg, last_b = leg_b(segments, coords, args.dry)
        print(("PASS" if ok_b else "FAIL") + " B " + last_b)
        results.append(("B", ok_b))
    spdx = "?"
    if args.only in (None, "C"):
        ok_c, spdx, last_c = leg_c(coords)
        print(("PASS" if ok_c else "FAIL") + " C " + last_c)
        results.append(("C", ok_c))
    if args.only in (None, "D"):
        ok_d, ndead, last_d = leg_d(work, args.neg)
        print(("PASS" if ok_d else "FAIL") + " D " + last_d)
        results.append(("D", ok_d))
    if args.only in (None, "E"):
        ok_e, ncalls, last_e = leg_e(work, args.neg, args.dry)
        print(("PASS" if ok_e else "FAIL") + " E " + last_e)
        results.append(("E", ok_e))
    if args.only in (None, "F"):
        ok_f, ver, last_f = leg_f(work, coords)
        print(("PASS" if ok_f else "FAIL") + " F " + last_f)
        results.append(("F", ok_f))
    if args.only in (None, "G"):
        ok_g, ndr, last_g = leg_g(mat, comps, args.neg)
        print(("PASS" if ok_g else "FAIL") + " G " + last_g)
        results.append(("G", ok_g))
    if args.only == "A":
        results = [("A", ok_a)]
    all_ok = all(x[1] for x in results)
    if args.neg:
        # 负控语义：这条腿必须判红才算「有牙」；判绿 = 负控失效 ⇒ 整体 FAIL
        teeth = not all_ok
        print("[R290S-NEGCTL] neg=" + args.neg + " leg_red=" + ("Y" if teeth else "N")
              + " meaning=" + ("has_teeth" if teeth else "CONST_GREEN_NO_TEETH"))
        all_ok = teeth
    summary = "[SEC-AUDIT-PREP] hunks=" + str(len(items)) + " old_unique=" + str(uniq) + "/" + str(total)
    summary = summary + " license=" + str(spdx) + " gate=" + ("PASS" if all_ok else "FAIL")
    print(summary)
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
