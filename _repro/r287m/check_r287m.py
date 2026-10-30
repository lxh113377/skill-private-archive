# -*- coding: utf-8 -*-
"""check_r287m.py — R287m mcp-builder 换装材料的自证判据（六条腿 + 四条负控）。

写面纪律：本件只读受管根 D:/global_skills 与 05-exec/06-benchmark，只在 _repro/r287m/ 写。
补丁一律在内存副本上重放（与 rule_editor._plan_patches 同口径），绝不落盘到受管根 ——
落盘是 Lead 经 rule_editor.py 的动作（红线 2）。

六条腿：
  A anchors  每个 old 必须是目标件原文的逐字切片且唯一命中（现场重算，不信 _verify 自报）
  B newfile  上游新增件与 GitHub blob 逐字节相等（git hash-object == gh api .sha）+ bytes/lines/sha 现核
  C license  r114 单源 classify_body + license_class；copyleft/weak/restricted/none/unknown => 不可并入
  D links    换装后每个 ./ 相对引用要么盘上存在，要么被 newfile_manifest 认领（防死链）
  E args     换装后文档写明的每个脚本参数被该脚本真实 --help 支持（缺依赖走 _help_of.py 打桩）
  F version  frontmatter version / last_updated 与版本史首行三者一致

负控（--neg，全部内存构造，用完不留副本）：
  anchor-absent  old 改一个字符      => A 必须判红并点名 id（不存在）
  anchor-multi   old 换成文中重复串   => A 必须判红并点名 id（不唯一）
  deadlink       新增件内链改成未写过的文件名 => D 必须判红
  argflag        塞一个脚本不认的参数        => E 必须判红

用法：python -B _repro/r287m/check_r287m.py [--only A|B|C|D|E|F] [--neg NAME]
退出码：0 全绿 / 1 任一判红（含负控该红却绿）。
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))            # 自建skill优化
SKILL_ROOT = "D:/global_skills/mcp-builder"
NEW_STAGED = os.path.join(HERE, "upstream_node_mcp_server_v2.md")
REPO = "anthropics/skills"
REF = "main"
UP_PATH = "skills/mcp-builder/reference/node_mcp_server_v2.md"
LF = chr(10)
FENCE = chr(96) * 3


def read_text(path):
    """逐字读取：newline="" 保住行尾原貌，切片才可能与盘上一字不差。"""
    with open(path, encoding="utf-8", newline="") as f:
        return f.read()


def jload(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as f:
        return json.load(f)


# -*- coding: utf-8 -*-
"""check_r287m.py 的 load_patch 替换版：结构自检 + 数组件逐字对账。

为什么加对账：Lead 真正喂给 rule_editor 的是 per-file 数组（patch_SKILL.md.json /
patch_node_mcp_server.md.json）。若有人手改拆分件而 patch.json 不动（或反之），
锚点断言就失真 => 必须机械证明两者 (id, old, new) 逐字同源且集合等价。
"""


def load_patch():
    """结构自检 + 数组件对账。

    认两种形态：dict（材料本体，含 hunks/_verify）与 list（纯数组）。
    断言：每项齐 id/target/old/new/_verify；_verify.assert 逐字为 text.count(old) == 1；
    每个数组件 patch_*.json 的 (id, old, new) 必须能在 hunks 里逐字找到，且 hunk 集合等价。
    """
    raw = jload("patch.json")
    if isinstance(raw, dict):
        items = raw["hunks"]
        v = raw.get("_verify")
        if not isinstance(v, dict):
            raise SystemExit("FATAL: patch.json 缺 _verify 段")
        if not v.get("all_pass"):
            raise SystemExit("FATAL: patch.json 自报 all_pass 非真")
        for row in v.get("rows", []):
            if row.get("count") != 1:
                raise SystemExit("FATAL: _verify.rows %s count=%r" % (row.get("id"), row.get("count")))
    else:
        items = raw
    if not isinstance(items, list) or not items:
        raise SystemExit("FATAL: patch.json 须含非空 hunks 数组")
    want = "text.count(old) == 1"
    for i, it in enumerate(items, 1):
        for k in ("id", "target", "old", "new", "_verify"):
            if k not in it:
                raise SystemExit("FATAL: 第 %d 项缺 %s" % (i, k))
        if it["_verify"].get("assert") != want:
            raise SystemExit("FATAL: 第 %d 项 _verify.assert 非 %s" % (i, want))
    import glob
    by_id = {}
    for it in items:
        by_id[it["id"]] = (it["old"], it["new"])
    seen = []
    files = sorted(glob.glob(os.path.join(HERE, "patch_*.json")))
    if not files:
        raise SystemExit("FATAL: 没有数组件 patch_*.json（rule_editor 一次只吃一个 --file）")
    for f in files:
        grp = jload(os.path.basename(f))
        if not isinstance(grp, list) or not grp:
            raise SystemExit("FATAL: 数组件须为非空数组: " + f)
        for it in grp:
            iid = it.get("id")
            if iid not in by_id:
                raise SystemExit("FATAL: 数组件 id 不在 patch.json: %s @ %s" % (iid, os.path.basename(f)))
            if (it.get("old"), it.get("new")) != by_id[iid]:
                raise SystemExit("FATAL: 数组件与 patch.json 漂移: %s" % iid)
            seen.append(iid)
    if sorted(seen) != sorted(by_id):
        raise SystemExit("FATAL: 数组件 hunk 集合与 patch.json 不等价 %s vs %s" % (
            ",".join(sorted(seen)), ",".join(sorted(by_id))))
    return items

def norm(p):
    return p.replace(chr(92), "/")


def replay(items):
    """rule_editor 同口径重放：顺序 find、未命中即失败、后续项可命中前项产生的新文本。

    Returns:
        originals: 目标 -> 盘上原文;  work: 目标 -> 换装后文本;  errs: 未命中清单
    """
    originals = {}
    work = {}
    errs = []
    for it in items:
        t = norm(it["target"])
        if t not in originals:
            originals[t] = read_text(t)
            work[t] = originals[t]
        n = work[t].count(it["old"])
        if n != 1:
            errs.append("%s: 顺序重放命中 %d 次 @ %s" % (it["id"], n, os.path.basename(t)))
            continue
        work[t] = work[t].replace(it["old"], it["new"], 1)
    return originals, work, errs


def leg_a(items, originals, errs, tag="ANCHORS"):
    """A：对**原文**逐条重算 count==1（不信任 _verify 自报）+ old/new 行尾对称（防半行粘连）。"""
    broken = []
    ok_n = 0
    for it in items:
        t = norm(it["target"])
        base = originals[t] if t in originals else read_text(t)
        n = base.count(it["old"])
        tail_ok = it["old"].endswith(LF) == it["new"].endswith(LF)
        if n != 1 or not tail_ok:
            broken.append("%s(count=%d,tail=%s)" % (it["id"], n, "ok" if tail_ok else "asym"))
        else:
            ok_n += 1
    if errs:
        broken.append("seq:" + errs[0])
    last = "[R287M-A-%s] hunks=%d old_unique=%d/%d broken=%s" % (
        tag, len(items), ok_n, len(items), ",".join(broken) if broken else "-")
    return (not broken) and (not errs), ok_n, len(items), last


def leg_b():
    """B：暂存新件 == 上游 blob（逐字节）。git hash-object 与 gh api .sha 同值才算证据。"""
    raw = open(NEW_STAGED, "rb").read()
    sha12 = hashlib.sha256(raw).hexdigest()[:12]
    blob = subprocess.run(["git", "hash-object", NEW_STAGED],
                          capture_output=True, text=True).stdout.strip()
    r = subprocess.run(["gh", "api", "repos/" + REPO + "/contents/" + UP_PATH + "?ref=" + REF,
                        "--jq", ".sha + \" \" + (.size|tostring)"], capture_output=True, text=True)
    parts = (r.stdout or "").strip().split()
    api_blob = parts[0] if parts else ""
    api_size = int(parts[1]) if len(parts) > 1 else -1
    man = jload("newfile_manifest.json")
    lines = raw.count(bytes([10]))
    ok = (blob == api_blob == man["api_blob_sha"] and len(raw) == man["bytes"] == api_size
          and sha12 == man["sha256_12"] and lines == man["lines"])
    last = "[R287M-B-NEWFILE] bytes=%d/%d/%d lines=%d sha=%s blob=%s api=%s equal=%s" % (
        len(raw), man["bytes"], api_size, lines, sha12, blob[:12], api_blob[:12],
        "yes" if blob == api_blob else "NO")
    return ok, sha12, last

def leg_c():
    """C：许可门现取 —— 调 05-exec/r114_replacement_scan 的单源 classify_body/license_class。

    档位落 copyleft / weak-copyleft / restricted / none / unknown => 结论必须写不可并入。
    与 numbers.json 快照逐项比对，读数漂移即判红（引用数字必须可复算，不接受记忆值）。
    """
    sys.path.insert(0, os.path.join(ROOT, "05-exec"))
    import r114_replacement_scan as R
    body = open(os.path.join(HERE, "_upstream_LICENSE.txt"), encoding="utf-8", errors="replace").read()
    spdx, cls, hits = R.classify_body(body.upper())
    cap = R.LICENSE_CAPS.get(cls)
    blocked = cls in ("copyleft", "weak-copyleft", "restricted", "none", "unknown")
    gate = "不可并入" if blocked else "可并入"
    num = jload("numbers.json")["license"]
    drift = (num["classify_body_spdx"] != spdx or num["classify_body_class"] != cls
             or num["cap"] != cap or num["license_body_restricted_hits"] != len(hits))
    ok = bool(spdx) and not blocked and not hits and not drift
    last = "[R287M-C-LICENSE] spdx=%s class=%s cap=%s hits=%d drift=%s gate=%s" % (
        spdx, cls, cap, len(hits), "yes" if drift else "no", gate)
    return ok, spdx, gate, last


LINK_RE = re.compile(r"\]\((\.[^)#]*?)(?:#[^)]*)?\)")


def corpus(work, neg=""):
    """换装后的文档面集合。

    被补丁改动的件用内存结果；其余 reference/*.md 用盘上原文；本次新增件用暂存副本
    （落盘后它在 reference/ 下，故 base 目录按落盘位置算，保证相对链接解析口径一致）。
    neg=deadlink 时把新增件内链换成一个从未写过的文件名 => 制造死链。
    """
    faces = []
    for p, t in work.items():
        faces.append((p, os.path.dirname(p), t))
    ref = os.path.join(SKILL_ROOT, "reference")
    for rel in sorted(os.listdir(ref)):
        p = norm(os.path.join(ref, rel))
        if p in work or not rel.endswith(".md"):
            continue
        faces.append((p, os.path.dirname(p), read_text(p)))
    v2p = norm(os.path.join(ref, "node_mcp_server_v2.md"))
    text = read_text(NEW_STAGED)
    if neg == "deadlink":
        text = text.replace("./node_mcp_server.md", "./node_mcp_server_UNWRITTEN_v9.md")
    faces.append((v2p, os.path.dirname(v2p), text))
    return faces


def will_exist():
    """本次换装落盘后才会存在的路径，只由 newfile_manifest.json 认领（清单外一律算死链）。"""
    man = jload("newfile_manifest.json")
    return set([norm(os.path.normpath(man["local_target"]))])


def leg_d(work, neg=""):
    """D：死链腿 —— 每个 ./ 相对引用要么盘上存在，要么被新增件清单认领。"""
    allow = will_exist()
    dead = []
    total = 0
    for src, base, text in corpus(work, neg):
        for m in LINK_RE.finditer(text):
            tgt = m.group(1)
            ap = norm(os.path.normpath(os.path.join(base, tgt)))
            total += 1
            if os.path.isfile(ap) or ap in allow:
                continue
            dead.append("%s->%s" % (os.path.basename(src), tgt))
    ok = bool(total) and not dead
    last = "[R287M-D-LINKS] links=%d dead=%d %s" % (
        total, len(dead), ",".join(dead[:3]) if dead else "-")
    return ok, last, total, len(dead)


def real_help(script):
    """真实 --help：受管 venv 无 anthropic/mcp，直接 --help 会在 import 期崩，
    故用 _help_of.py 打桩顶掉缺失依赖，拿到 argparse 的真 usage（不靠读源码猜）。"""
    cache_p = os.path.join(HERE, "help_cache.json")
    cache = jload("help_cache.json") if os.path.isfile(cache_p) else {}
    p = os.path.join(SKILL_ROOT, "scripts", script)
    mt = os.path.getmtime(p)
    if cache.get(script, {}).get("mtime") == mt:
        return cache[script]["usage"]
    r = subprocess.run([sys.executable, "-B", os.path.join(HERE, "_help_of.py"), p],
                       capture_output=True, text=True)
    usage = (r.stdout or "") + (r.stderr or "")
    cache[script] = {"mtime": mt, "usage": usage, "rc": r.returncode}
    with open(cache_p, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=1)
    return usage


def doc_calls(work, neg=""):
    """收集围栏代码块里的 python [scripts/]X.py <flags> 调用（反斜杠续行先合并）。

    只收 scripts/ 下真实存在的件：文档里的 python your_server.py --help 指用户自己写的
    服务器占位符，不是本件脚本；把它算进判据会让正跑假红、负控假绿。
    """
    calls = {}
    for name, _base, text in corpus(work, neg):
        blocks = []
        cur = []
        inb = False
        for ln in text.splitlines():
            if ln.startswith(FENCE):
                if inb:
                    blocks.append(LF.join(cur))
                cur = []
                inb = not inb
                continue
            if inb:
                cur.append(ln)
        if inb:
            blocks.append(LF.join(cur))
        for blk in blocks:
            merged = re.sub(r"\\" + LF + "[ ]*", " ", blk)
            for m in re.finditer(r"python +(?:scripts/)?([A-Za-z0-9_.-]+[.]py)([^" + LF + "]*)", merged):
                script = m.group(1)
                if not os.path.isfile(os.path.join(SKILL_ROOT, "scripts", script)):
                    continue
                d = calls.setdefault(script, {})
                for f in re.findall(r"(?<![\w-])(-{1,2}[A-Za-z][\w-]*)", m.group(2)):
                    d[f] = d.get(f, 0) + 1
    return calls


def leg_e(work, neg=""):
    """E：参数腿 —— 文档写的每个参数必须在该脚本 --help 的长参或短参名单里。"""
    calls = doc_calls(work, neg)
    if neg == "argflag":
        calls.setdefault("evaluation.py", {})["--totally-made-up-flag"] = 1
    bad = []
    total = 0
    for script in sorted(calls):
        usage = real_help(script)
        if "usage:" not in usage:
            bad.append(script + ":no-usage")
            continue
        longs = set(re.findall(r"(--[a-z][\w-]+)", usage))
        shorts = set(re.findall(r"(?:^|[\s(,])(-[A-Za-z])(?=[\s,)\]])", usage, re.M))
        for f in sorted(calls[script]):
            total += 1
            if f not in longs and f not in shorts:
                bad.append(script + " " + f)
    ok = total > 0 and not bad
    last = "[R287M-E-ARGS] scripts=%d flag-refs=%d unsupported=%d %s" % (
        len(calls), total, len(bad), ",".join(bad[:3]) if bad else "-")
    return ok, last, total, len(bad)

# 版本史行格式（本件生成）：- **1.1.0**（2026-10-30）— …
HIST_RE = re.compile(r"^- [*][*]([0-9][\w.]*)[*][*]\uFF08([0-9-]{8,})\uFF09", re.M)


def leg_f(work):
    """F：版本腿 —— frontmatter 的 version / last_updated 与版本史首行三者一致。

    根因（R271 判据 + r269 实测「版本行/历史行不齐」）：三处任一处漏改，下次会话就读到旧号。
    """
    text = None
    for p, t in work.items():
        if p.endswith("SKILL.md"):
            text = t
            break
    if text is None:
        return False, "[R287M-F-VERSION] SKILL.md 不在补丁目标里", "-"
    fm = re.match(r"---" + LF + r"(.*?)" + LF + r"---" + LF, text, re.S)
    if not fm:
        return False, "[R287M-F-VERSION] frontmatter-missing", "-"
    head = fm.group(1)
    v = re.search(r"^version:[ ]*([0-9][\w.]*)[ ]*$", head, re.M)
    lu = re.search(r"^last_updated:[ ]*([0-9-]{8,})[ ]*$", head, re.M)
    hist = HIST_RE.findall(text)
    ok = bool(v) and bool(lu) and bool(hist) and hist[0][0] == v.group(1) and hist[0][1] == lu.group(1)
    last = "[R287M-F-VERSION] fm=%s/%s hist=%s/%s rows=%d consistent=%s" % (
        v.group(1) if v else "-", lu.group(1) if lu else "-",
        hist[0][0] if hist else "-", hist[0][1] if hist else "-", len(hist),
        "yes" if ok else "NO")
    return ok, last, (v.group(1) if v else "-")


def apply_neg(items, neg):
    """负控①：anchor-absent 把一个 old 改一个字符；anchor-multi 把一个 old 换成文中重复串。

    只在内存改，绝不写盘；返回 (新列表, 被点名 id)。
    """
    out = [dict(it) for it in items]
    if neg == "anchor-absent":
        vid = "SKILL-STRUCTURE-PTR"
        for it in out:
            if it["id"] == vid:
                it["old"] = it["old"].replace("TypeScript Guide", "TypeScript Guidx")
        return out, vid
    if neg == "anchor-multi":
        vid = "NODE-V1-BANNER"
        import collections
        t = norm(os.path.join(SKILL_ROOT, "reference", "node_mcp_server.md"))
        cnt = collections.Counter(l + LF for l in read_text(t).splitlines())
        # 运行时挑盘上重复最多的非空行，不硬编码字串：首版硬编码 "## Overview"，
        # 实测该串在盘上只出现 1 次 => 负控恒绿（判据没牙）。现取才算证据。
        dup = max([(l, n) for l, n in cnt.items() if l.strip()], key=lambda x: x[1])
        for it in out:
            if it["id"] == vid:
                it["old"] = dup[0]
        return out, vid
    return out, ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", choices=list("ABCDEF"), default=None)
    ap.add_argument("--neg", default=None,
                    choices=["anchor-absent", "anchor-multi", "deadlink", "argflag"])
    a = ap.parse_args()
    items = load_patch()
    tag = "ANCHORS"
    victim = ""
    if a.neg in ("anchor-absent", "anchor-multi"):
        items, victim = apply_neg(items, a.neg)
        tag = "NEGCTL"
    originals, work, errs = replay(items)
    negd = a.neg if a.neg in ("deadlink", "argflag") else ""
    uniq = "-"
    sha12 = "0" * 12
    spdx = "-"
    res = []
    if a.only in (None, "A"):
        ok, n, tot, last = leg_a(items, originals, errs, tag)
        uniq = "%d/%d" % (n, tot)
        if a.neg in ("anchor-absent", "anchor-multi"):
            # 负控：A 判红（broken 非空且点名 victim）才是期望结果
            ok = (not ok) and (victim in last)
        res.append(("A", ok, last))
    if a.only in (None, "B"):
        ok, sha12, last = leg_b()
        res.append(("B", ok, last))
    if a.only in (None, "C"):
        ok, spdx, gate, last = leg_c()
        res.append(("C", ok, last))
    if a.only in (None, "D"):
        ok, last, _t, deadn = leg_d(work, negd)
        if negd == "deadlink":
            ok = (not ok) and deadn > 0
        res.append(("D", ok, last))
    if a.only in (None, "E"):
        ok, last, _t, badn = leg_e(work, negd)
        if negd == "argflag":
            ok = (not ok) and badn > 0
        res.append(("E", ok, last))
    if a.only in (None, "F"):
        ok, last, _v = leg_f(work)
        res.append(("F", ok, last))
    for name, ok, last in res:
        print(("PASS " if ok else "FAIL ") + name + " " + last)
    all_ok = all(bool(ok) for _n, ok, _l in res)
    if a.only:
        print("[MCP-PREP-SUB] only=%s ok=%s" % (a.only, "PASS" if all_ok else "FAIL"))
        return 0 if all_ok else 1
    if a.neg:
        print("[MCP-PREP-NEGCTL] %s teeth=%s" % (a.neg, "PROVEN-RED" if all_ok else "NO-TEETH"))
        return 0 if all_ok else 1
    print("[MCP-PREP] hunks=%d old_unique=%s upstream_sha=%s license=%s gate=%s" % (
        len(items), uniq, sha12, spdx, "PASS" if all_ok else "FAIL"))
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
