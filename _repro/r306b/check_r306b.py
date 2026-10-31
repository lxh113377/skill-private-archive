# -*- coding: utf-8 -*-
"""check_r306b.py -- A-prompt-better 准入规格与回滚演练的自证脚本（r306b B1：只出规格与演练，未落地）。

判据面（每条都现算实跑，不采信任何自述；负控内建，证明判据有牙）：
  K 规格自洽   先 print sorted(keys) 再引用字段名；七个字段齐、补丁链可解析且每项含 id/old/new
  R 重放       落地前基线按链顺序重放 == HEAD 版（字节级；空链 = 该件未被改写的守卫）
  D 回滚演练   副本上 改 -> 验 -> 退 -> 与改前逐字全等（快照覆盖 / 基线重取 两条通道都跑）
  A 负控腿A    与当前文件不符的 old 去应用必须被拒（count=0 或 count!=1），不得静默跳过
  B 负控腿B    退回后 sha 必须等于改前；且两种假回滚必须不等于改前（相等即演练无牙，判红）
  V 版本       frontmatter 与版本史首行一致（形态取自本地件现形：Markdown 表格，非项目符号）
  P 裸指针     受影响件 HEAD 版不得含裸跨仓指针（同行绝对路径豁免单列为掩蔽面）
  M 镜像       required 根与权威源逐字节同 blob；observed 根只报状态不判红
末行：[R306B:SPEC] spec_ok=<bool> fields=<n> patches=<n> drill=revert_identical=<bool> pre_sha=<8> post_sha=<8>
字段口径：fields = 规格件顶层键数；patches = 该单补丁链 hunk 总数（补丁文件数在 K 腿明细里）。
退出码：0 全绿 / 1 有红 / 2 有 UNVERIFIED（禁把取不到当通过）。
用法：python -B _repro/r306b/check_r306b.py   （只读受管根；写面仅本目录 drill/ 下的副本）
"""
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys

NL = chr(10)
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SPEC_PATH = os.path.join(HERE, "A-prompt-better.json")
for _i, _a in enumerate(sys.argv[1:]):
    if _a == "--spec" and _i + 2 <= len(sys.argv[1:]):
        SPEC_PATH = sys.argv[_i + 2]   # 负控用：把判据指向一份被改坏的规格副本
DRILL = os.path.join(HERE, "drill")
COPY = os.path.join(DRILL, "A-prompt-better_SKILL.md")
SNAP = os.path.join(DRILL, "pre_snapshot.bin")
REQ_FIELDS = ["bare_tokens", "managed", "mirror_roots", "new_files", "replays", "skill", "version"]


def git(repo, args):
    # 受管根只读取证：所有 git 调用都带 -C，绝不 add/commit/checkout
    try:
        r = subprocess.run(["git", "-c", "core.quotepath=false", "-C", repo] + list(args),
                           capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=120)
    except Exception:
        return None
    return r.stdout if r.returncode == 0 else None


def shab(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def wt(path, text, newline=True):
    # newline=True 走 io.open(newline="") => 逐字节写出，不做行尾翻译（真回滚的前提）
    if newline:
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            f.write(text)
    else:
        with io.open(path, "w", encoding="utf-8") as f:  # 平台默认 => \n 被译成 \r\n，制造假回滚
            f.write(text)


def rd(path):
    if not os.path.isfile(path):
        return None
    with io.open(path, encoding="utf-8", newline="") as f:
        return f.read()


def replay(base, hunks):
    """与 landing_replay_check.replay 同语义：顺序 find；count=0 或 (count>1 且非幂等) 即拒，只替换第一处。"""
    t = base
    errs = []
    hits = []
    for h in hunks:
        c = t.count(h["old"])
        idem = h["old"] in h["new"]
        hits.append("%s=count%d%s" % (h.get("id", "?"), c, "(idem)" if idem else ""))
        if c == 0 or (c > 1 and not idem):
            errs.append("%s(count=%d)" % (h.get("id", "?"), c))
            continue
        t = t.replace(h["old"], h["new"], 1)
    return t, errs, hits


def load_chain(paths):
    hs = []
    for p in paths or []:
        full = p if os.path.isabs(p) else os.path.join(ROOT, p)
        if not os.path.isfile(full):
            return None, full
        hs += json.load(io.open(full, encoding="utf-8"))
    return hs, None


def leg_K(spec):
    missing = [k for k in REQ_FIELDS if k not in spec]
    if missing:
        return "BAD", ["规格缺字段 %s" % missing], 0, 0
    det = []
    nh = 0
    for tgt in (spec["replays"] or []) + (spec["new_files"] or []):
        if "target" not in tgt:
            return "BAD", ["target 缺失"], 0, 0
        ps = tgt.get("patches") or []
        hs, miss = load_chain(ps)
        if hs is None:
            return "UNVERIFIED", ["补丁件缺失 %s" % miss], 0, 0
        for h in hs:
            for k in ("id", "old", "new"):
                if k not in h:
                    return "BAD", ["补丁项缺键 %s (%s)" % (k, h.get("id"))], 0, 0
        nh += len(hs)
        det.append("%s patch_files=%d hunks=%d" % (tgt["target"], len(ps), len(hs)))
    det.append("fields=%d patches_hunks=%d" % (len(spec.keys()), nh))
    return "ok", det, len(spec.keys()), nh


def leg_R(spec, neg=""):
    det, bad, unver = [], [], []
    for i, tgt in enumerate(spec["replays"] or []):
        rel = tgt["target"]
        cur = git(spec["managed"], ["show", "HEAD:" + rel])
        base = git(spec["managed"], ["show", "%s:%s" % (tgt["base_ref"], rel)]) if cur is not None else None
        if cur is None or base is None:
            unver.append("%s:重放输入不可得" % rel)
            continue
        hs, miss = load_chain(tgt.get("patches"))
        if hs is None:
            unver.append("%s:补丁件缺失 %s" % (rel, miss))
            continue
        landed, errs, hits = replay(base, hs)
        det.append("%s base=%s hunks=%d %s" % (rel, tgt["base_ref"], len(hs), " ".join(hits)))
        bad += ["%s/%s" % (rel, e) for e in errs]
        cmp_cur = (cur[:-2] + "ZZ") if (neg == "hand-edited" and i == 0) else cur
        if landed != cmp_cur:
            bad.append("%s/REPLAY-MISMATCH" % rel)
    if bad:
        return "BAD", det + bad
    if unver:
        return "UNVERIFIED", det + unver
    return "ok", det


def leg_D(spec, neg=""):
    """改 -> 验 -> 退 -> 逐字全等，全在副本上做；受管根零改动。"""
    tgt = (spec["replays"] or [])[0]
    rel = tgt["target"]
    base = git(spec["managed"], ["show", "%s:%s" % (tgt["base_ref"], rel)])
    head = git(spec["managed"], ["show", "HEAD:" + rel])
    hs, miss = load_chain(tgt.get("patches"))
    if base is None or head is None or hs is None:
        return "UNVERIFIED", ["演练输入不可得 %s" % (miss or rel)], None
    os.makedirs(DRILL, exist_ok=True)
    wt(COPY, base)
    shutil.copyfile(COPY, SNAP)
    pre = shab(COPY)
    after, errs, _ = replay(rd(COPY), hs)
    if errs:
        return "BAD", ["改这一步就被拒：%s" % errs], None
    wt(COPY, after)
    post = shab(COPY)
    post_bytes = os.path.getsize(COPY)
    post_eq_head = rd(COPY) == head
    shutil.copyfile(SNAP, COPY)
    rev1 = shab(COPY)
    id1 = rd(COPY) == base
    wt(COPY, git(spec["managed"], ["show", "%s:%s" % (tgt["base_ref"], rel)]))
    rev2 = shab(COPY)
    id2 = rd(COPY) == base
    identical = (rev1 == pre and rev2 == pre and id1 and id2)
    # 假回滚必须报红：行尾翻译（写盘不做 newline 直通）与半链（只打前 n-1 个 hunk）
    fake_path = os.path.join(DRILL, "fake_revert_crlf.txt")
    wt(fake_path, base, newline=False)
    fake_crlf = shab(fake_path)
    half, _, _ = replay(base, hs[:-1])
    fake_half = hashlib.sha256(half.encode("utf-8")).hexdigest()
    teeth = (fake_crlf != pre and fake_half != pre)
    if neg == "fake-revert" and identical:
        return "BAD", ["负控 fake-revert：判据本该抓到行尾假回滚，却没抓到"], None
    det = ["pre=%s(%d) post=%s(%d) rev_snapshot=%s rev_refetch=%s" % (pre[:12], os.path.getsize(SNAP), post[:12], post_bytes, rev1[:12], rev2[:12]),
           "post==HEAD:%s revert==pre:%s 假回滚报红(行尾/半链):%s %s" % (post_eq_head, identical, fake_crlf != pre, fake_half != pre)]
    if not post_eq_head:
        return "BAD", det + ["post 不等于 HEAD => 演练没复现落地态"], None
    if not identical:
        return "BAD", det + ["退回与改前不逐字全等 => 那不是真回滚"], None
    if not teeth:
        return "BAD", det + ["假回滚未被报红 => 演练无牙"], None
    return "ok", det, {"pre": pre, "post": post, "rev1": rev1, "rev2": rev2, "identical": identical}


def leg_A(spec):
    """腿 A：与当前文件不符的 old 去应用，必须被拒。三形态各测一次。"""
    tgt = (spec["replays"] or [])[0]
    hs, miss = load_chain(tgt.get("patches"))
    base = git(spec["managed"], ["show", "%s:%s" % (tgt["base_ref"], tgt["target"])])
    cur = git(spec["managed"], ["show", "HEAD:" + tgt["target"]])
    if hs is None or base is None or cur is None:
        return "UNVERIFIED", ["负控输入不可得 %s" % (miss or tgt["target"])]
    a1 = replay(cur, hs)
    stale = json.loads(json.dumps(hs, ensure_ascii=False))
    stale[0]["old"] = stale[0]["old"].replace("1.3.0", "9.9.9", 1)
    a2 = replay(base, stale)
    a3 = replay(base, [{"id": "NEG-AMB", "old": NL + NL, "new": NL}])
    rej1 = len(a1[1]) == len(hs)
    det = ["A1 整链打到已落地文本上（每处 old 都与当前文件不符）：命中 %s 全 count=0 拒=%d/%d 静默跳过=%s"
           % (" ".join(a1[2]), len(a1[1]), len(hs), len(a1[1]) == 0),
           "A2 只篡改一处 old 的版本号：%s" % (a2[1] or "未拒=判据无牙"),
           "A3 歧义 old（连续两个换行，实测命中 177 处）：%s %s" % (a3[2][0], a3[1] or "未拒=判据无牙")]
    if a1[1] and a2[1] and a3[1]:
        return "ok", det
    return "BAD", det + ["腿 A 至少一形态未被拒"]


def leg_V(spec):
    v = spec.get("version")
    if not v:
        return "UNVERIFIED", ["spec 未给 version 期望"]
    txt = git(spec["managed"], ["show", "HEAD:" + v["target"]])
    if txt is None:
        return "UNVERIFIED", ["件取不到"]
    fm = {}
    for ln in txt.split(NL)[:60]:
        if (": " in ln) and not ln.startswith(" "):
            k = ln.split(": ", 1)[0]
            if k in (v["fm_key"], v.get("fm_date_key")):
                fm[k] = ln.split(": ", 1)[1].strip()
    rx = re.compile(v["history_row_regex"])
    rows = []
    for ln in txt.split(NL):
        m = rx.match(ln.strip())
        if m:
            rows.append((m.group(1), m.group(2)))
    bullet = [l for l in txt.split(NL) if l.startswith("- **")]
    if not rows:
        return "BAD", ["版本史表格首行取不到（形态与 spec 不符）"]
    hv, hd = rows[0]
    ok = (fm.get(v["fm_key"]) == v["expect"]) and (hv == v["expect"]) and (fm.get(v.get("fm_date_key")) == hd)
    det = ["fm=%s/%s hist=%s/%s want=%s 表行数=%d" % (fm.get(v["fm_key"]), fm.get(v.get("fm_date_key")), hv, hd, v["expect"], len(rows)),
           "工具形态差（登记不判红）：项目符号史行=%d，本件是表格 => 通用 leg_V 会 hist=None 判 BAD" % len(bullet)]
    return ("ok" if ok else "BAD"), det


def leg_P(spec):
    n = m = 0
    det = []
    for tgt in (spec["replays"] or []) + (spec["new_files"] or []):
        txt = git(spec["managed"], ["show", "HEAD:" + tgt["target"]])
        if txt is None:
            continue
        alltok = [x for x in txt.split(NL) if any(t in x for t in spec["bare_tokens"] or [])]
        masked = [x for x in alltok if ("C:/Users" in x or "D:/global" in x)]
        bare = [x for x in alltok if x not in masked]
        n += len(bare)
        m += len(masked)
        det.append("%s 裸指针=%d 掩蔽=%d" % (tgt["target"], len(bare), len(masked)))
    return ("ok" if n == 0 else "BAD"), ["bare=%d masked=%d" % (n, m)] + det


def leg_M(spec):
    paths = [t["target"] for t in (spec["replays"] or [])] + [f["target"] for f in (spec["new_files"] or [])]
    det, bad, unver = [], [], []
    checked = 0
    for rt in spec["mirror_roots"] or []:
        req = bool(rt.get("required"))
        tag = "REQUIRED" if req else "observed"
        if not os.path.isdir(rt["path"]):
            (unver if req else det).append(tag + " 根不存在 " + rt["path"])
            continue
        lag = []
        for rel in paths:
            srcp = os.path.join(spec["managed"], rel)
            mirp = os.path.join(rt["path"], rel)
            if not os.path.isfile(srcp):
                continue
            h1 = (git(spec["managed"], ["hash-object", rel]) or "").strip()
            h2 = ""
            if os.path.isfile(mirp):
                h2 = subprocess.run(["git", "hash-object", mirp], capture_output=True, text=True,
                                    encoding="utf-8", errors="replace", timeout=90).stdout.strip()
            if not (h1 and h2 and h1 == h2):
                lag.append("%s(%s)" % (rel, "缺失" if not h2 else "滞后"))
        if lag and req:
            bad.append("%s %s 落后 %d 项: %s" % (tag, rt["path"], len(lag), "; ".join(lag)))
        elif req:
            checked += 1
            det.append("%s %s 全同 lag=0" % (tag, os.path.basename(os.path.normpath(rt["path"]))))
        else:
            det.append("%s %s lag=%d（无端记载，不判红）" % (tag, os.path.basename(os.path.normpath(rt["path"])), len(lag)))
    if bad:
        return "BAD", bad + det
    if unver and not checked:
            return "UNVERIFIED", unver + det
    if unver:
        return "UNVERIFIED", unver + det
    return "ok", det or ["无可核 required 根"]


def main():
    spec = json.load(io.open(SPEC_PATH, encoding="utf-8"))
    print("sorted(keys) = %s" % json.dumps(sorted(spec.keys())))
    print("field_defs: fields=%d(顶层键数) patches=<下面 K 腿的 hunk 总数>" % len(spec.keys()))
    ks, kdet, nfields, npatches = leg_K(spec)
    legs = [("K spec", ks, kdet)]
    drill_stats = None
    for nm, fn in (("R replay", leg_R), ("D drill", leg_D), ("A legA", leg_A),
                   ("V version", leg_V), ("P pointer", leg_P), ("M mirror", leg_M)):
        r = fn(spec)
        legs.append((nm, r[0], r[1]))
        if nm == "D drill" and len(r) > 2 and isinstance(r[2], dict):
            drill_stats = r[2]   # leg_D 成功时才回传第三个元素（四枚 sha + identical）
    dd = drill_stats
    hard = [x[0] for x in legs if x[1] == "BAD"]
    unver = [x[0] for x in legs if x[1] == "UNVERIFIED"]
    for nm, st, det in legs:
        print("%-12s %-11s %s" % (nm, st, json.dumps([d for d in det if not isinstance(d, dict)], ensure_ascii=False)[:220]))
    spec_ok = (not hard) and (not unver) and dd is not None and bool(dd["identical"])
    gate = "FAIL" if hard else ("UNVERIFIED" if unver else "PASS")
    print("[gate] %s hard=%s unver=%s" % (gate, hard, unver))
    print("[R306B:SPEC] spec_ok=%s fields=%d patches=%d drill=revert_identical=%s pre_sha=%s post_sha=%s" % (
        json.dumps(bool(spec_ok)), nfields, npatches, json.dumps(bool(dd["identical"]) if dd else False),
        (dd["pre"][:8] if dd else "00000000"), (dd["post"][:8] if dd else "00000000")))
    return 1 if hard else (2 if unver else 0)


if __name__ == "__main__":
    sys.exit(main())
