# -*- coding: utf-8 -*-
"""landing_replay_check.py — 落地态校验的**通用工具**（R289-5 第⑦步的工具化，r292）。

为什么要有它（一手，r292 我对自己上一轮产物的批评）：05-exec/check_r291_landed.py 是为
security-audit **这一单**写死的 —— skill 名、基线 ref、补丁链、新件清单都在文件顶部。R261-7 还剩
两件要落，照那形态就得每单复制一份脚本；两份会漂移，而且「落地态判据」不再是可复用工序。这与本会话
反复批评的「为一次性事实写死」是同一族。本件只有一份，每一单是一个 **spec**（JSON）。

核心不变式（与 check_r291_landed 的 H 腿同算法，一字不差地复用其语义）：
    盘上文本 == 在落地前基线上按顺序重放该单全部补丁的结果。
它比「每个 new 都在盘上」强：漏打、多打、事后手改一个字符都会被抓；且补丁链中的**后续再补丁**
（本轮真发生：歧义补丁改写了前一笔的 new）天然被覆盖 —— 因为断言的是末端态。

四类腿：
  R replay        每个 target：base_ref 版重放 chain 后 == 盘上文本（缺输入即 UNVERIFIED，不判绿）
  N new-files     spec 声明的新件在位，且 git hash-object == 上游 blob sha（gh api 现取；取不到
                  退回 spec 里的 expected_sha 存档并标注来源；两者皆无 => UNVERIFIED）
  P pointer-clean 受管根内被改动的件不得含裸跨仓指针（_repro/ _temp/ 05-exec/ 而无绝对路径前缀）
  V version       frontmatter 与版本史首行一致（键名与期望值来自 spec，不猜）
末行：[LANDING-CHECK] spec=<name> replay=<ok|BAD|UNVERIFIED> new_files=<...> pointers=<n> version=<...> gate=PASS|FAIL|UNVERIFIED
退出码：0 全绿 / 1 硬红 / 2 有腿 UNVERIFIED（禁把取不到当通过，R247 与其第二形态）。

负控：--neg hand-edited（内存里把某 target 的盘上文本改一个字符 => R 必须判红）
      --neg fake-sha（把期望 blob sha 改一位 => N 必须判红）
      --neg mirror-stale（把首个受影响路径在**第一个 required 根**的 blob 视为未同步 => M 必须判红）
      --neg root-absent（模拟 required 根不可达 => M 必须 UNVERIFIED，不得读成已同步）
用法：python -B 05-exec/landing_replay_check.py --spec 05-exec/landing_specs/security-audit.json
"""
import argparse
import io
import json
import os
import re
import subprocess
import sys

NL = chr(10)
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TIME_KEYS = {"measured_at", "generated_at", "updated_at", "timestamp", "ts", "at", "date"}


def git(cwd, args, t=120):
    try:
        r = subprocess.run(["git", "-c", "core.quotepath=false", "-C", cwd] + args,
                           capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=t)
    except Exception:
        return None
    if r.returncode != 0:
        return None
    return (r.stdout or "")


def strip_time(x):
    if isinstance(x, dict):
        return dict((k, strip_time(v)) for k, v in x.items() if k not in TIME_KEYS)
    if isinstance(x, list):
        return [strip_time(v) for v in x]
    return x


def replay(base, hunks):
    """与 check_r291_landed.leg_h 同口径：顺序 find，命中数不为 1 即失败；幂等项（old 是 new 的子串）
    允许 old 出现多次，但仍只替换第一处 —— 与 rule_editor._plan_patches 的行为一致。"""
    errs = []
    t = base
    for h in hunks:
        c = t.count(h["old"])
        idem = h["old"] in h["new"]
        if c == 0 or (c > 1 and not idem):
            errs.append("%s(count=%d)" % (h.get("id", "?"), c))
            continue
        t = t.replace(h["old"], h["new"], 1)
    return t, errs


def load_chain(paths):
    hs = []
    for p in paths:
        full = p if os.path.isabs(p) else os.path.join(ROOT, p)
        if not os.path.isfile(full):
            return None, p
        hs += json.load(io.open(full, encoding="utf-8"))
    return hs, None


def leg_R(spec, neg=''):
    bad, det, unver = [], [], []
    for tgt in spec.get("replays") or []:
        rel = tgt["target"]
        cur = git(spec["managed"], ["show", "HEAD:" + rel])
        if cur is None:
            unver.append("%s:HEAD 版取不到" % rel)
            continue
        base_ref = tgt["base_ref"]
        if git(spec["managed"], ["cat-file", "-e", base_ref]) is None:
            unver.append("%s:baseline 不可读" % rel)
            continue
        base = git(spec["managed"], ["show", "%s:%s" % (base_ref, rel)])
        if base is None:
            unver.append("%s:baseline show 失败" % rel)
            continue
        hunks, miss = load_chain(tgt["patches"])
        if hunks is None:
            unver.append("%s:补丁件缺失 %s" % (rel, miss))
            continue
        landed, errs = replay(base, hunks)
        det.append("%s hunks=%d" % (rel, len(hunks)))
        bad += ["%s/%s" % (rel, e) for e in errs]
        cmp_cur = (cur[:-2] + "ZZ") if (neg == "hand-edited" and tgt is (spec["replays"][0])) else cur
        if landed != cmp_cur:
            ll, cl = landed.split(NL), cmp_cur.split(NL)
            first = next((i for i in range(min(len(ll), len(cl))) if ll[i] != cl[i]),
                         min(len(ll), len(cl)))
            bad.append("%s/REPLAY-MISMATCH@line%d" % (rel, first + 1))
    if unver and not bad:
        return "UNVERIFIED", (det + unver)
    return ("ok" if not bad else "BAD"), (det + bad + unver)


def leg_N(spec, neg=''):
    files = spec.get("new_files") or []
    if not files:
        return "ok", ["无新增件"]
    det, bad, unver = [], [], []
    replay_bad = set()
    for f in files:
        rel = f["target"]
        # 新增件也可能被后续补丁修正（本轮实测：吸收分卷落地后还要改指针）。
        # spec 给它挂了 patches 时，按同一条重放不变式校验，而不是只核 blob 等值。
        if f.get("patches"):
            cur = git(spec["managed"], ["show", "HEAD:" + rel])
            base = git(spec["managed"], ["show", "%s:%s" % (f["base_ref"], rel)]) if f.get("base_ref") else None
            hunks, miss = load_chain(f["patches"])
            if cur is None or base is None or hunks is None:
                unver.append("%s:重放输入不可得" % rel)
            else:
                landed, errs = replay(base, hunks)
                if errs:
                    bad.append("%s/%s" % (rel, errs[0]))
                    replay_bad.add(rel)
                elif landed != cur:
                    bad.append("%s/REPLAY-MISMATCH" % rel)
                    replay_bad.add(rel)
                else:
                    det.append("%s 重放一致 hunks=%d" % (rel, len(hunks)))
        if git(spec["managed"], ["cat-file", "-e", "HEAD:" + rel]) is None:
            bad.append("%s 不在受管根 HEAD" % rel)
            continue
        live = (git(spec["managed"], ["hash-object", rel]) or "").strip()
        want = None
        src = "none"
        up = f.get("upstream") or {}
        if up.get("repo") and up.get("path"):
            try:
                r = subprocess.run(["gh", "api", "repos/%s/contents/%s" % (up["repo"], up["path"]),
                                    "--jq", ".sha"], capture_output=True, text=True, timeout=120)
                got = (r.stdout or "").strip()
                if len(got) == 40:
                    want, src = got, "gh api (live)"
            except Exception:
                pass
        if want is None and f.get("expected_sha"):
            want, src = f["expected_sha"], "spec 存档"
        if want is None:
            # 本项目**自造**的件（如吸收分卷：由 blocks 逐字切片+头注组成）没有上游同名文件可锚。
            # 这类件若 spec 声明 no_upstream_anchor 且**重放已一致**，重放本身就是等值证明
            # —— 再要求上游 blob 就是把合法状态判成不可判（本轮实测踩到）。否则仍记 UNVERIFIED。
            if f.get("no_upstream_anchor") and f.get("patches") and rel not in replay_bad:
                det.append("%s 无上游锚点（自造件），以重放一致为等值证明" % rel)
                continue
            unver.append("%s:无等值锚点（上游取不到且 spec 未存档）" % rel)
            continue
        if neg == "fake-sha":
            want = want[:38] + ("ab" if not want.endswith("ab") else "cd")
        det.append("%s live=%s want=%s(来源 %s)" % (os.path.basename(rel), live[:12], (want or "")[:12], src))
        if live != want:
            bad.append("%s/BLOB-DIFFERS(%s)" % (rel, want[:12]))
    if unver and not bad:
        return "UNVERIFIED", (det + unver)
    return ("ok" if not bad else "BAD"), (bad or []) and (det + bad + unver) or det


def leg_P(spec):
    n, m, det = 0, 0, []          # m = 被同行绝对路径豁免的裸糖行数（R298-4 的「掩蔽面」可见性）
    for tgt in (spec.get("replays") or []) + (spec.get("new_files") or []):
        rel = tgt["target"]
        txt = git(spec["managed"], ["show", "HEAD:" + rel])
        if txt is None:
            continue
        # r303 落 R298-4：原写法把「同行含绝对路径」的裸糖行**静默**排除（掩蔽生产面实测 4 条），
        # 于是那 4 条既不算违规、也不出现在任何读数里 —— 缺陷不是「豁免」本身，而是「豁免不可见」。
        # 改法（保牙且不改变判定）：两个计数器分开跑，掩蔽数**照实显形**；
        #   · bare  = 未被豁免的裸糖行（口径与原来完全一致 ⇒ 判定语义不变，三个 spec 不会因此变红）
        #   · masked= 被绝对路径同行豁免的行（新增可见性，供人读；它是「可能被掩掉的违规」的候选面）
        # 不把 masked 计入 BAD 是刻意的：那会把别人的历史遗留算成本轮落地失败，而本条要治的是「看不见」。
        alltok = [x for x in txt.split(NL)
                  if any(t in x for t in spec.get("bare_tokens") or [])]
        masked = [x for x in alltok if ("C:/Users" in x or "D:/global" in x)]
        bare = [x for x in alltok if x not in masked]
        n += len(bare)
        m += len(masked)
        if bare or masked:
            det.append("%s 裸指针 %d 条（另 %d 条被同行绝对路径豁免=掩蔽面，须人读）"
                       % (rel, len(bare), len(masked)))
    return ("ok" if n == 0 else "BAD"), (["bare=%d" % n, "masked=%d" % m] + det)


def leg_V(spec):
    v = spec.get("version")
    if not v:
        return "UNVERIFIED", ["spec 未给 version 期望"]
    # 版本史行的识别不能靠「第一条 - **」：真实 SKILL.md 里那种加粗项比比皆是
    # （mcp-builder 实测命中的是 - **v2** (`@modelcontextprotocol/server`)，把工具判成 BAD）。
    # 优先在 Version history 小节内找；小节缺失时退到「形如 - **<版本>** (」且与 expect 同行”。
    hre = v.get("history_heading") or "## Version history"
    txt = git(spec["managed"], ["show", "HEAD:" + v["target"]])
    if txt is None:
        return "UNVERIFIED", ["件取不到"]
    fm_v = fm_d = hist_v = hist_d = None
    # r306 工具侧修（B1 实测缺陷上报）：三份既有模板件的版本史都是项目符号行（- **x.y.z** (日期)），
    # 但 A-prompt-better 的史是 Markdown 表格行（| V1.5.0 | 2026-10-31 | … |），本腿原来只认前者
    # ⇒ 对表格形态 hist=None 假红。修法按「判据不迁就工具、工具加形态分支」：
    #   spec 给了 history_form=markdown-table + history_row_regex 时，史行走**正则捕获组**
    #   （组1=版本、组2=日期）；不给则保持原项目符号路径（既有三 spec 行为零变化）。
    tform = (v.get("history_form") or "").strip()
    trow = v.get("history_row_regex")
    trow_c = re.compile(trow) if (tform == "markdown-table" and trow) else None
    in_hist = False
    for ln in txt.split(NL):
        if ln.startswith(v["fm_key"] + ": "):
            fm_v = ln.split(": ", 1)[1].strip()
        elif v.get("fm_date_key") and ln.startswith(v["fm_date_key"] + ": "):
            fm_d = ln.split(": ", 1)[1].strip()
        elif ln.strip().startswith("#"):
            in_hist = bool(hre) and ln.strip().startswith(hre)
        elif trow_c and (not hist_v) and in_hist and ln.startswith("|"):
            # 表格分支：整行按 spec 给的正则匹配（^\| 已含在正则里，行首再挡一次省扫描）
            mm = trow_c.match(ln)
            if mm:
                hist_v, hist_d = mm.group(1).strip(), mm.group(2).strip()
        elif (not hist_v) and in_hist and ln.startswith("- **"):
            # 括号两种写法都真实存在（本轮实测）：security-audit 用半角 - **2.1.0** (2026-10-30)，
            # mcp-builder 用全角 - **1.1.0**（2026-10-30）。只认半角会把后者判成 hist=None => 假红。
            seg = ln[4:]
            if "**" not in seg:
                continue
            hist_v = seg.split("**")[0].strip()
            rest = seg.split("**", 1)[1]
            for op, cl in (("(", ")"), (u"\uff08", u"\uff09")):
                if op in rest:
                    hist_d = rest.split(op, 1)[1].split(cl, 1)[0]
                    break
    if hist_v is None and not in_hist:
        return "UNVERIFIED", ["找不到版本史小节（spec 的 history_heading 需校正）"]
    ok = fm_v == v["expect"] and hist_v == v["expect"]
    if v.get("fm_date_key"):
        ok = ok and fm_d == hist_d
    return ("ok" if ok else "BAD"), ["fm=%s/%s hist=%s/%s want=%s" % (fm_v, fm_d, hist_v, hist_d,
                                                                      v["expect"])]




def leg_M(spec, neg=''):
    """M mirror-propagated：受管根源件与各物理副本必须逐字节同 blob。

    为什么是一条腿（一手，r292/r294）：落地只改 D:/global_skills，而副本根是物理复制的
    C:/Users/37533/.agents/skills。A 臂维6 实测 5/5 落地件滞后（我的 mcp-builder 落后 HEAD~5、
    security-audit 落后 HEAD~4）=> 「无兼容回归」若只看源件，对读到旧副本的端是空话。

    required / observed 分离（r295 一手，我上一轮的错被开场取证推翻后写进代码）：
    只有 spec 里带 evidence（文件:行 的端记载）的根才允许判红 —— 我 r294 曾断言「九端读的
    就是 .agents 那一个根」，而实测 ~/.dsh/skills 与 .config/opencode/skills 都直连权威源、
    另有 .claude/.codex 两个物理副本存在但无端记载。若把所有存在的目录都当 required，
    就是把「我猜谁在读它」写进判据，会把未知当缺陷。observed 根只报状态、绝不判红。
    根不存在或件缺失：required 记 UNVERIFIED、observed 记入明细（R247，不许读成已同步）。
    """
    roots = spec.get("mirror_roots")
    if not roots:
        old = spec.get("mirror_root")
        if old:
            roots = [{"path": old, "required": True, "evidence": "旧单根字段 mirror_root"}]
        else:
            return "UNVERIFIED", ["spec 未声明任何副本根（mirror_roots 缺失）"]
    paths = [t["target"] for t in (spec.get("replays") or [])] + \
            [f["target"] for f in (spec.get("new_files") or [])]
    if not paths:
        return "UNVERIFIED", ["spec 未列受影响路径"]
    bad, unver, det = [], [], []
    checked_required = 0
    for ri, rt in enumerate(roots):
        root = rt["path"]
        req = bool(rt.get("required"))
        tag = "REQUIRED" if req else "observed"
        if neg == "root-absent" and req:
            unver.append(root + "（负控：模拟 required 根缺失）")
            continue
        if not os.path.isdir(root):
            msg = root + " 根不存在"
            (unver if req else det).append(tag + " " + msg)
            continue
        lag, skip, match = [], 0, 0
        for rel in paths:
            srcp = os.path.join(spec["managed"], rel)
            mirp = os.path.join(root, rel)
            if not os.path.isfile(srcp):
                skip += 1
                continue
            h1 = (git(spec["managed"], ["hash-object", rel]) or "").strip()
            if os.path.isfile(mirp):
                h2 = subprocess.run(["git", "hash-object", mirp], capture_output=True,
                                        text=True, encoding="utf-8", errors="replace",
                                        timeout=90).stdout.strip()
            else:
                h2 = ""
            if neg == "mirror-stale" and ri == 0 and rel == paths[0]:
                h2 = "0" * 40   # 内存里模拟该根未同步：required 时 M 必须判红
            if h1 and h2 and h1 == h2:
                match += 1
            else:
                lag.append("%s(%s)" % (rel, "缺失" if not h2 else "滞后"))
        if lag and req:
            bad.append("%s %s 落后 %d 项: %s" % (tag, root, len(lag), "; ".join(lag)))
        elif req:
            checked_required += 1
            det.append("%s %s 全同 match=%d skip=%d | evidence=%s" % (
                tag, os.path.basename(os.path.normpath(root)), match, skip,
                str(rt.get("evidence") or "-")[:60]))
        else:
            det.append("%s %s lag=%d match=%d（无端记载，不判红）" % (
                tag, os.path.basename(os.path.normpath(root)), len(lag), match))
    if bad:
        return "BAD", bad + det
    if unver and not checked_required:
        return "UNVERIFIED", unver + det
    if unver:
        return "UNVERIFIED", unver + det
    return "ok", det or ["无可核 required 根"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True, help="落地单的描述件（05-exec/landing_specs/*.json）")
    ap.add_argument("--neg", default="")
    ap.add_argument("--json", dest="js")
    a = ap.parse_args()
    sp_path = a.spec if os.path.isabs(a.spec) else os.path.join(ROOT, a.spec)
    if not os.path.isfile(sp_path):
        print("[LANDING-CHECK] UNVERIFIED spec 不存在: %s" % sp_path)
        return 2
    KNOWN_NEG = {"", "hand-edited", "fake-sha", "mirror-stale", "root-absent"}
    if a.neg not in KNOWN_NEG:
        # 负控名写错 => 腿静默不触发 => 看起来「判据跑过且仍绿」，那是假负控（r294 一手踩到）。
        print("[LANDING-CHECK] UNVERIFIED 未知 --neg 值 %r（可用：%s）" % (a.neg, sorted(KNOWN_NEG)))
        return 2
    spec = json.load(io.open(sp_path, encoding="utf-8"))
    legs = []
    # 负控名必须与实现逐字一致：实现用 mirror-stale，我上一版注释与试跑都写成 mirror-staged
    # ⇒ 那次「负控」传的是不存在的名字、静默无操作，差点被我读成「M 腿没牙」。
    # 所以 main() 现在校验 --neg 取值：未知名字直接 rc=2，不给静默无操作的机会。
    for nm, fn in (("R replay", leg_R), ("N new-files", leg_N), ("P pointer-clean", leg_P),
                   ("V version", leg_V), ("M mirror", leg_M)):
        st, det = fn(spec, a.neg) if nm.startswith(("R", "N", "M")) else fn(spec)
        legs.append((nm, st, det))
    for nm, st, det in legs:
        print("%-18s %-12s %s" % (nm, st, "; ".join(str(x) for x in det)[:150]))
    hard = [x[0] for x in legs if x[1] == "BAD"]
    unver = [x[0] for x in legs if x[1] == "UNVERIFIED"]
    gate = "FAIL" if hard else ("UNVERIFIED" if unver else "PASS")
    print("[LANDING-CHECK] spec=%s %s gate=%s" % (
        spec.get("skill"), " ".join("%s=%s" % (x[0][0], x[1]) for x in legs), gate))
    if a.js:
        io.open(a.js, "w", encoding="utf-8").write(json.dumps(
            {"schema": "landing-replay-v1", "skill": spec.get("skill"), "spec": a.spec,
             "legs": [{"name": n, "state": s, "detail": d} for n, s, d in legs],
             "gate": gate}, ensure_ascii=False, indent=1))
    return 1 if hard else (2 if unver else 0)


if __name__ == "__main__":
    sys.exit(main())
