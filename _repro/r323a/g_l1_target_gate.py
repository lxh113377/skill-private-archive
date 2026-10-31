#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""G-L1 目标件门判据（r323a）——把「受管根 git status --porcelain = 0 行」这条字面门
换成「目标入口件本体是否 CLEAN」，并机械化成三态 + 三条守恒/完整性断言。

为什么换尺（背景，不是猜测）：
  受管根实测 79 行 dirty，但「索引暂存 0 行」——75 行 M + 1 行 D 全在 worktree 侧，
  另有 3 行未跟踪。这些改动是他人在途的，本会话既不能提交、也不能还原；
  于是「全仓 0 行」在本会话的生命周期内永远不可能成立 ⇒ 它是恒红门，不是判据。
  真正决定「我这一笔能不能落盘」的是：**我要写的那一个入口件本体，有没有他人的在途改动**。

判据（必须 porcelain + pathspec 作用域，不能是全仓计数）：
    git -C <受管根> status --porcelain -- <slug>/SKILL.md
  输出为空 ⇒ 该件路径在索引与 worktree 两侧都无差异；非空 ⇒ 具名脏标记（M/A/D/?? 等）。

三态（禁把 unknown 读成 CLEAN）：
   can_land : CLEAN，且必须同时满足「文件在盘 ∧ git 认它被跟踪 ∧ porcelain 空」。
              「porcelain 空」单独不足以判 CLEAN——被 .gitignore 吞掉的件也回空输出。
   blocked  : DIRTY，带逐行脏标记（index 侧 X、worktree 侧 Y、或 ??）。
   unknown  : 件不存在 / git 读不到 / 忽略未跟踪 ⇒ UNVERIFIED，永不进 can_land。

断言（validate() 每次重算，供 --selftest 与 check_r323a.py 的负控注入使用）：
   A1 每件恰好落一态（桶成员与 items[].state 一致，且互不相交）
   A2 can_land + blocked + unknown == 目标件总数（守恒，且等于声明数）
   A3 blocked 每件至少一个具名脏标记，且标记取自 git porcelain 的合法字母集
   A4 can_land 每件不得带任何脏标记（否则「CLEAN」是假绿）
   A5 unknown 的理由必须具名，且 unknown 不得出现在 can_land
   A6 (可选) HEAD 等于 --expect-head；A7 (可选) 目标件全部出现在 --from-plan 解析出的名册里（同源）

--from-plan 的取数规则（禁另立名册）：只从批次表文本里取，取法三种，全部可复核：
   R1 反引号内的单段 slug（`ppt-master`），且受管根下确有同名目录；
   R2 「X 族……（a/b/c）」行：前缀取该行「X 族」的字面前缀，词干取括号内斜杠列表；
   R3 行内以 " / " 分隔的 slug 枚举（§7.2 的 DIRTY 名单就是这种形态）。
  任何一条解析不出（如「hyperframes 三件」这种只给件数的行）都记进 unresolved_rows，不臆造成员。
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone, timedelta

DEFAULT_ROOT = "D:/global_skills"
DEFAULT_GIT = "C:/Program Files/Git/bin/git.exe"
SCHEMA = "_r323a-gl1-target-gate-1"
ENTRY = "SKILL.md"                  # 目标入口件本体 = <slug>/SKILL.md（本门只管这一个文件）
SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")   # 单段 slug：无空格/斜杠/点/大写
ALLOWED_MARKS = set("MADRCUXB?!")   # git porcelain 的合法状态字母 + ?? 的 "?"


def which_git(explicit=None):
    """git 可执行文件：显式给 > 本机 Git for Windows 全路径 > PATH 里的 git。"""
    if explicit:
        return explicit
    if os.path.exists(DEFAULT_GIT):
        return DEFAULT_GIT
    return "git"


def run_git(git, root, args):
    """只读 git 调用；返回 (rc, stdout, stderr)。绝不在这里做任何写操作。"""
    cmd = [git, "-C", root] + list(args)
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=120)
    except Exception as exc:                      # 启动失败也当成「读不到」，不能当 CLEAN
        return 127, "", "%s: %s" % (type(exc).__name__, exc)
    out = (p.stdout or b"").decode("utf-8", "replace")
    err = (p.stderr or b"").decode("utf-8", "replace")
    return p.returncode, out, err


def sha256_12(path):
    """文件内容 SHA256 前 12 位（不存在返回空串）——读数一律带它，防「读数过期」。"""
    try:
        with open(path, "rb") as fh:
            return hashlib.sha256(fh.read()).hexdigest()[:12]
    except OSError:
        return ""


def parse_porcelain(text):
    """把 porcelain 行拆成 (index_marker, worktree_marker, path)。

    为什么拆两侧：` M` 与 `M ` 都是「脏」，但语义不同——前者改动在 worktree（可被
    `git add -A -- <path>` 一并 stage），后者已在索引里（提交就带走）。报告要能分辨。
    """
    rows = []
    for raw in text.splitlines():
        if not raw.strip():
            continue
        xy = raw[:2].ljust(2)
        path = raw[3:].strip()
        if xy == "??":                     # 未跟踪：git 用两个问号整体表示，没有 X/Y 之分
            rows.append({"line": raw.rstrip(), "index_marker": "?", "worktree_marker": "?",
                         "path": path, "markers": ["??"]})
            continue
        marks = [c for c in xy if c not in " "]
        rows.append({"line": raw.rstrip(), "index_marker": xy[0], "worktree_marker": xy[1],
                     "path": path, "markers": marks})
    return rows


def probe_one(slug, root, git):
    """单件判定。返回 (state, detail)；state ∈ {CLEAN, DIRTY, UNKNOWN}。

    判定顺序（fail-closed：任何一步读不到都往 UNKNOWN 掉，绝不往 CLEAN 掉）：
      1) git status --porcelain -- <slug>/SKILL.md 非空      ⇒ DIRTY（具名标记）
      2) git 调用失败 / 文件不在盘上                          ⇒ UNKNOWN
      3) porcelain 空，但 git 不认为该路径被跟踪（被 ignore） ⇒ UNKNOWN（空输出是假 CLEAN）
      4) 以上都过                                             ⇒ CLEAN
    """
    rel = "%s/%s" % (slug, ENTRY)
    rc, out, err = run_git(git, root, ["status", "--porcelain", "--", rel])
    if rc != 0:
        return "UNKNOWN", {"reason": "git_status_rc_%d" % rc, "stderr": err.strip()[:400],
                           "path": rel}
    rows = parse_porcelain(out)
    if rows:
        marks = sorted({m for r in rows for m in r["markers"]})
        return "DIRTY", {"path": rel, "rows": rows, "markers": marks,
                         "index_marker": " ".join(sorted({r["index_marker"] for r in rows})),
                         "worktree_marker": " ".join(sorted({r["worktree_marker"] for r in rows}))}

    full = os.path.join(root, rel)
    if not os.path.exists(full):
        return "UNKNOWN", {"reason": "missing_on_disk", "path": rel}

    # porcelain 为空只说明「没有差异」，不说明「git 认识这个路径」。
    # 被 .gitignore 命中的件同样回空输出 —— 必须再问一次 ls-files 才敢判 CLEAN。
    rc2, out2, err2 = run_git(git, root, ["ls-files", "--", rel])
    if rc2 != 0:
        return "UNKNOWN", {"reason": "git_ls_files_rc_%d" % rc2, "stderr": err2.strip()[:400],
                           "path": rel}
    if not out2.strip():
        return "UNKNOWN", {"reason": "not_tracked_porcelain_silent", "path": rel,
                           "note": "porcelain 空但 ls-files 空：被 ignore 或未跟踪，空输出是假 CLEAN"}

    # 空 porcelain 只证明「盘 ≠ 索引 ≠ HEAD 都不成立」，还差最后一环证据：
    # 索引 blob 与 HEAD blob 是否都是同一颗（这样 CLEAN 不是「没报错就放行」，
    # 而是「这份内容就是 HEAD 里那份」，任何人可以直接 rev-parse 复算）。
    rc3, out3, _err3 = run_git(git, root, ["rev-parse", "HEAD:" + rel])
    rc4, out4, _err4 = run_git(git, root, ["rev-parse", ":" + rel])
    head_blob = out3.strip()[:12] if rc3 == 0 else ""
    index_blob = out4.strip()[:12] if rc4 == 0 else ""
    if not head_blob or not index_blob:
        return "UNKNOWN", {"reason": "blob_unresolvable", "path": rel,
                           "note": "HEAD 或索引里取不到该路径的 blob（新增/未跟踪/被 ignore）"}
    if head_blob != index_blob:
        return "UNKNOWN", {"reason": "index_head_blob_mismatch", "path": rel,
                           "head_blob": head_blob, "index_blob": index_blob}

    return "CLEAN", {"path": rel, "rows": [], "markers": [],
                     "head_blob": head_blob, "index_blob": index_blob}


def split_repo_status(root, git):
    """全仓 porcelain 拆分：总行数 / 索引暂存行数 / worktree-only 行数 / 未跟踪行数。

    这就是「为什么全仓 0 行不可达」的实测账：报告要能复算 79 = 0 + 76 + 3。
    索引暂存行 = X 位非空且非 ?（即 M/A/D/R/C/U 出现在第一列）。
    """
    rc, out, err = run_git(git, root, ["status", "--porcelain"])
    rows = parse_porcelain(out)
    staged = [r for r in rows if r["index_marker"] not in (" ", "?")]
    untracked = [r for r in rows if r["index_marker"] == "?"]
    worktree_only = [r for r in rows if r["index_marker"] == " " and r["worktree_marker"] != " "]
    return {
        "rc": rc,
        "stderr": err.strip()[:400],
        "total": len(rows),
        "staged": len(staged),
        "worktree_only": len(worktree_only),
        "untracked": len(untracked),
        "sum_check": len(staged) + len(worktree_only) + len(untracked) == len(rows),
    }


def _disk_slugs(root):
    """受管根下现存的顶层目录名（只读目录列表，不递归）。"""
    try:
        return {n for n in os.listdir(root) if os.path.isdir(os.path.join(root, n))}
    except OSError:
        return set()


def parse_plan(plan_path, root):
    """从批次表里解析目标件名册（规则 R1/R2/R3 见文件头；不臆造成员）。

    每条命中都留 (line, rule, evidence)，这样「判据与计划件同源」可以被逐行复核，
    而不是靠一句「我抄过」。解析不出成员的行记入 unresolved_rows，由报告显式列出。
    """
    with open(plan_path, "r", encoding="utf-8-sig") as fh:
        text = fh.read()
    lines = text.splitlines()
    disk = _disk_slugs(root)
    found = {}          # slug -> [{"line":n,"rule":"R1","evidence":"..."}]
    unresolved = []     # 只给件数、不给名单的行（如「hyperframes 三件」）

    def add(slug, lineno, rule, evidence):
        # 只收「磁盘上确有同名目录」的 slug：解析器不许为闸门造件
        if not SLUG_RE.match(slug) or slug not in disk:
            return False
        found.setdefault(slug, []).append({"line": lineno, "rule": rule,
                                           "evidence": evidence.strip()[:160]})
        return True

    for lineno, line in enumerate(lines, 1):
        # 行分类：批次表的件行 / 正文里的列举 bullets。分类先做，解析才不会被
        # 别的表（P-1 缺陷表里的示例件、G-L5 回滚示例）把无关 slug 灌进名册。
        is_batch_row = bool(re.match(r"^\|\s*B\d+\s*\|", line))
        is_bullet = bool(re.match(r"^\s*(?:[-*])\s", line)) or line.startswith("> ")
        # R1：批次表行（§3 的 | B<n> | ...）里的反引号件名
        if is_batch_row:
            for tok in re.findall(r"`([^`]+)`", line):
                if SLUG_RE.match(tok):
                    add(tok, lineno, "R1", line)
        # R2：「<前缀> 族……（a/b/c）」：前缀与词干都来自本行字面，不跨行拼装
        if "族" in line:
            m_paren = re.search(r"（([a-z0-9\-/]+)）", line)
            m_pref = re.search(r"([a-z0-9]+)\s*族", line)
            if m_paren and m_pref and "/" in m_paren.group(1):
                prefix = m_pref.group(1) + "-"
                for stem in m_paren.group(1).split("/"):
                    add(prefix + stem.strip(), lineno, "R2", line)
        # R3：bullets 里的 " / " 件名枚举（§7.2 的 DIRTY 名单就是这种形态）
        if is_bullet and " / " in line:
            for tok in line.split(" / "):
                cand = tok.strip().strip("`|、,，。()（）*")
                for w in re.split(r"[\s|、,，。]+", cand):
                    if SLUG_RE.match(w) and w in disk:
                        add(w, lineno, "R3", line)

        # 记录「只给件数不给名单」的表行，作为未解析项申报（禁按件数猜成员）
        if re.search(r"`?[a-z0-9]+`?\s*(三|两|四|五|六|七|八|九|十)件", line):
            unresolved.append({"line": lineno, "evidence": line.strip()[:160],
                               "reason": "family_by_count_no_member_list"})

    roster = sorted(found)
    return {
        "path": plan_path,
        "sha256_12": sha256_12(plan_path),
        "lines": len(lines),
        "roster": roster,
        "roster_total": len(roster),
        "sources": {k: v for k, v in found.items()},
        "unresolved_rows": unresolved,
    }


def build(targets, root=DEFAULT_ROOT, git=None, plan=None, expect_head=None,
          require_head_pin=None):
    """跑一遍门：逐件三态 + 全仓拆分 + 断言。纯读，不写任何文件。

    未知 HEAD 也算一次断言（退路要求：HEAD 不符就停，禁拿工作树态冒充 HEAD）。
    """
    git = which_git(git)
    rc_head, head, err_head = run_git(git, root, ["rev-parse", "HEAD"])
    head = head.strip()
    rc_root, top, err_root = run_git(git, root, ["rev-parse", "--show-toplevel"])
    items = {}
    for slug in targets:
        state, detail = probe_one(slug, root, git)
        items[slug] = {"slug": slug, "state": state, **detail}

    can_land = [{"slug": s, "path": it["path"]} for s, it in items.items() if it["state"] == "CLEAN"]
    blocked = [{"slug": s, "path": it["path"], "markers": it.get("markers", []),
                "rows": it.get("rows", []), "index_marker": it.get("index_marker", ""),
                "worktree_marker": it.get("worktree_marker", "")}
               for s, it in items.items() if it["state"] == "DIRTY"]
    unknown = [{"slug": s, "path": it.get("path", ""), "reason": it.get("reason", "unknown"),
                "note": it.get("note", "")} for s, it in items.items() if it["state"] == "UNKNOWN"]

    result = {
        "schema": SCHEMA,
        "generated_at": datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds"),
        "managed_root": root,
        "git": git,
        "head": head,
        "head_rc": rc_head,
        "head_stderr": err_head.strip()[:400],
        "toplevel": top.strip(),
        "toplevel_rc": rc_root,
        "expect_head": expect_head,
        "require_head_pin": require_head_pin,
        "targets": list(targets),
        "items": items,
        "can_land": can_land,
        "blocked": blocked,
        "unknown": unknown,
        "counts": {"targets": len(targets), "can_land": len(can_land), "blocked": len(blocked),
                   "unknown": len(unknown)},
        "repo_status": split_repo_status(root, git),
        "plan": plan,
    }
    violations = validate(result)
    result["assertions"] = violations_to_table(result, violations)
    result["ok"] = not violations
    result["gate"] = "ok" if not violations else "fail"
    return result


def validate(result):
    """重算式断言：每条都从 result 本体重算，不做「构造时记账 ⇒ 事后自证」。

    返回违例列表（空 = 绿）。check_r323a.py 的负控就是往 result 里注水再调这里。
    """
    v = []
    items = result["items"]
    counts = result["counts"]

    # A1 每件恰好落一态：桶成员 === items 里同态的那些件，且桶之间不相交
    by_state = {s: sorted(k for k, it in items.items() if it["state"] == s)
                for s in ("CLEAN", "DIRTY", "UNKNOWN")}
    buckets = {"can_land": "CLEAN", "blocked": "DIRTY", "unknown": "UNKNOWN"}
    for bname, state in buckets.items():
        got = sorted(x["slug"] for x in result[bname])
        dup = [s for s in got if got.count(s) > 1]
        if dup:
            v.append("A1[partition] %s 有重复件 %s" % (bname, sorted(set(dup))))
        if got != by_state[state]:
            extra = sorted(set(got) - set(by_state[state]))
            missing = sorted(set(by_state[state]) - set(got))
            v.append("A1[partition] %s 桶成员与 items 状态不符：多=%s 缺=%s" % (bname, extra, missing))
    all_bucket_slugs = [x["slug"] for b in ("can_land", "blocked", "unknown") for x in result[b]]
    if len(all_bucket_slugs) != len(set(all_bucket_slugs)):
        v.append("A1[partition] 同一件出现在多个桶：%s"
                 % sorted({s for s in all_bucket_slugs if all_bucket_slugs.count(s) > 1}))

    # A2 守恒：三桶之和 == items 总数 == 声明数 == targets 列表长度
    ssum = counts["can_land"] + counts["blocked"] + counts["unknown"]
    for name, got, want in (("桶计数之和 vs items", ssum, len(items)),
                            ("声明 targets vs items", counts["targets"], len(items)),
                            ("声明 targets vs 参数列表", counts["targets"], len(result["targets"]))):
        if got != want:
            v.append("A2[conservation] %s 不等：%d != %d" % (name, got, want))
    if len(result["targets"]) == 0:
        v.append("A2[conservation] 目标件总数为 0（空名册不等于全绿）")

    # A3 blocked 每件必须具名脏标记，且标记只能来自 git porcelain 的合法字母集
    for it in result["blocked"]:
        marks = it.get("markers") or []
        if not marks:
            v.append("A3[markers] blocked 件 %s 无具名脏标记" % it["slug"])
            continue
        bad = [m for m in marks if not set(m) <= ALLOWED_MARKS]
        if bad:
            v.append("A3[markers] blocked 件 %s 含非法标记 %s" % (it["slug"], bad))
        if not it.get("rows"):
            v.append("A3[markers] blocked 件 %s 没有 porcelain 原始行（无法归属）" % it["slug"])

    # A4 can_land 每件不得带任何脏标记（否则是假绿）
    for it in result["can_land"]:
        if it.get("markers"):
            v.append("A4[clean] can_land 件 %s 带脏标记 %s" % (it["slug"], it["markers"]))
        st = items.get(it["slug"], {}).get("state")
        if st != "CLEAN":
            v.append("A4[clean] can_land 件 %s 的实测状态是 %s（假绿）" % (it["slug"], st))

    # A5 unknown 必须具名理由，且永不进 can_land
    for it in result["unknown"]:
        if not it.get("reason"):
            v.append("A5[unknown] %s 无归因理由" % it["slug"])
    clash = sorted({x["slug"] for x in result["unknown"]} & {x["slug"] for x in result["can_land"]})
    if clash:
        v.append("A5[unknown] unknown 件出现在 can_land：%s" % clash)

    # A6 HEAD 断言（退路：HEAD 不符即停，禁拿工作树未提交态冒充 HEAD）
    if result.get("head_rc") != 0:
        v.append("A6[head] git rev-parse HEAD 失败 rc=%s %s"
                 % (result.get("head_rc"), result.get("head_stderr", "")[:120]))
    exp = result.get("expect_head")
    if exp and result.get("head") != exp:
        v.append("A6[head] HEAD 不符：实测 %s != 期望 %s" % (result.get("head"), exp))
    if not result.get("head"):
        v.append("A6[head] HEAD 为空（受管根读不到）")
    pin = result.get("require_head_pin")
    if pin and result.get("head") != pin:
        v.append("A6[head] 快照窗口失效：实测 HEAD %s != 落盘时 pin %s"
                 "（受管根被别的会话推着走，本轮判据读数跨了两个快照）"
                 % (result.get("head"), pin))

    # A7 同源：目标件必须都能在批次表解析出的名册里找到（禁另立名册）
    plan = result.get("plan")
    if plan:
        roster = set(plan.get("roster") or [])
        outside = sorted(set(result["targets"]) - roster)
        if outside:
            v.append("A7[same-source] 目标件不在批次表名册里（另立名册）：%s" % outside)
        if plan.get("roster_total", 0) == 0:
            v.append("A7[same-source] 批次表解析出 0 个件（解析失效）")
    return v


def violations_to_table(result, violations):
    """把违例摊成逐条断言表（report/诊断要能点名哪一条腿红）。"""
    items = result["items"]
    table = {
        "partition": {"ok": not any(x.startswith("A1") for x in violations),
                      "detail": "每件恰好落一态：CLEAN=%d DIRTY=%d UNKNOWN=%d"
                                % (len(result["can_land"]), len(result["blocked"]), len(result["unknown"])),
                      "hits": [x for x in violations if x.startswith("A1")]},
        "conservation": {"ok": not any(x.startswith("A2") for x in violations),
                         "detail": "%d + %d + %d = %d vs targets=%d"
                                   % (result["counts"]["can_land"], result["counts"]["blocked"],
                                      result["counts"]["unknown"],
                                      result["counts"]["can_land"] + result["counts"]["blocked"] + result["counts"]["unknown"],
                                      result["counts"]["targets"]),
                         "hits": [x for x in violations if x.startswith("A2")]},
        "markers": {"ok": not any(x.startswith("A3") for x in violations),
                    "detail": "blocked 具名标记：%s"
                              % ", ".join("%s=%s" % (i["slug"], "/".join(i["markers"]))
                                          for i in result["blocked"]),
                    "hits": [x for x in violations if x.startswith("A3")]},
        "clean_has_no_mark": {"ok": not any(x.startswith("A4") for x in violations),
                              "hits": [x for x in violations if x.startswith("A4")]},
        "unknown_not_clean": {"ok": not any(x.startswith("A5") for x in violations),
                              "hits": [x for x in violations if x.startswith("A5")]},
        "head": {"ok": not any(x.startswith("A6") for x in violations),
                 "detail": "head=%s expect=%s" % (result.get("head"), result.get("expect_head")),
                 "hits": [x for x in violations if x.startswith("A6")]},
    }
    if result.get("plan"):
        table["same_source"] = {
            "ok": not any(x.startswith("A7") for x in violations),
            "detail": "计划名册 %d 件，被检目标 %d 件，目标 ⊆ 名册 = %s"
                      % (result["plan"].get("roster_total", 0), len(result["targets"]),
                         set(result["targets"]) <= set(result["plan"].get("roster") or [])),
            "plan_path": result["plan"].get("path"),
            "plan_sha256_12": result["plan"].get("sha256_12"),
            "unresolved_rows": len(result["plan"].get("unresolved_rows") or []),
            "hits": [x for x in violations if x.startswith("A7")],
        }
    return table


def summarize(result):
    """人读一行摘要（check 脚本与 report 都引用同一条口径）。"""
    c = result["counts"]
    return "[R323A:GL1] targets=%d clean=%d dirty=%d gate=%s" % (
        c["targets"], c["can_land"], c["blocked"], result["gate"])


def selftest():
    """不依赖受管根的纯逻辑自检：用合成 result 打三条腿，确认断言真有牙。

    这三条与 check_r323a.py 的真实负控互为独立实现（合成 vs 真跑），
    避免「判据脚本与它的负控同源同错」。
    """
    def fixture(states, declared=None, plan_roster=None):
        items = {s: {"slug": s, "state": st, "path": s + "/SKILL.md",
                     "markers": ["M"] if st == "DIRTY" else [],
                     "rows": [" M %s/SKILL.md" % s] if st == "DIRTY" else [],
                     "reason": "missing_on_disk" if st == "UNKNOWN" else ""}
                 for s, st in states.items()}
        r = {
            "targets": sorted(states), "items": items,
            "can_land": [{"slug": s, "path": s + "/SKILL.md"} for s, st in states.items() if st == "CLEAN"],
            "blocked": [{"slug": s, "path": s + "/SKILL.md", "markers": ["M"],
                         "rows": [" M %s/SKILL.md" % s]} for s, st in states.items() if st == "DIRTY"],
            "unknown": [{"slug": s, "path": s + "/SKILL.md", "reason": "missing_on_disk"}
                        for s, st in states.items() if st == "UNKNOWN"],
            "counts": {"targets": declared or len(states),
                       "can_land": sum(1 for v in states.values() if v == "CLEAN"),
                       "blocked": sum(1 for v in states.values() if v == "DIRTY"),
                       "unknown": sum(1 for v in states.values() if v == "UNKNOWN")},
            "head": "deadbeef", "head_rc": 0, "expect_head": "deadbeef",
            "plan": {"roster": plan_roster or sorted(states), "roster_total": len(plan_roster or states)},
        }
        return r

    cases = []
    cases.append(("baseline-clean", fixture({"a": "CLEAN", "b": "DIRTY"}), 0))
    r_bad = fixture({"a": "CLEAN", "b": "DIRTY"})
    r_bad["can_land"].append({"slug": "b", "path": "b/SKILL.md"})   # 把 DIRTY 塞进 can_land
    cases.append(("dirty-in-canland", r_bad, 1))
    r_short = fixture({"a": "CLEAN", "b": "DIRTY"}, declared=1)      # 件总数被改成 1
    cases.append(("conservation-broken", r_short, 1))
    r_noname = fixture({"a": "CLEAN", "b": "DIRTY"})
    r_noname["blocked"][0]["markers"] = []                          # 脏但不具名
    cases.append(("blocked-without-marker", r_noname, 1))
    r_out = fixture({"a": "CLEAN", "b": "DIRTY"}, plan_roster=["a"]) # 目标不在计划名册里
    cases.append(("target-outside-plan", r_out, 1))

    bad = 0
    for name, res, want_red in cases:
        v = validate(res)
        is_red = bool(v)
        ok = (is_red == bool(want_red))
        print("[selftest] %-24s red=%-5s want=%-5s %s" % (name, is_red, bool(want_red),
                                                          "OK" if ok else "FAIL"))

        if not ok:
            bad += 1
            for x in v:
                print("    hit: " + x)
    print("[selftest] %d/%d ok" % (len(cases) - bad, len(cases)))
    return 0 if bad == 0 else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="G-L1 目标件门：<slug>/SKILL.md 是否 CLEAN")
    ap.add_argument("--skill", action="append", default=[],
                    help="目标件 slug，可重复：--skill gstack --skill ppt-master")
    ap.add_argument("--skills", default="", help="逗号分隔的 slug 列表（与 --skill 等价）")
    ap.add_argument("--from-plan", default="", help="批次表路径：从中解析目标件名册并做同源断言")
    ap.add_argument("--json", default="", help="结果 JSON 落盘路径")
    ap.add_argument("--root", default=DEFAULT_ROOT, help="受管根（只读）")
    ap.add_argument("--git", default="", help="git 可执行文件")
    ap.add_argument("--expect-head", default="", help="期望 HEAD（不符即红）")
    ap.add_argument("--require-head-pin", default="",
                    help="落盘时记录的 HEAD pin（快照窗口断言：HEAD 变过即红）")
    ap.add_argument("--pin", action="store_true",
                    help="写 --json 时记录当前 HEAD 为 pin（重钉快照基线）")
    ap.add_argument("--selftest", action="store_true", help="纯逻辑自检（不碰受管根）")
    ap.add_argument("--quiet", action="store_true", help="只打末行摘要")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    targets = list(args.skill)
    if args.skills:
        targets += [s.strip() for s in args.skills.split(",") if s.strip()]
    targets = [t for t in dict.fromkeys(targets)]      # 去重且保序

    plan = parse_plan(args.from_plan, args.root) if args.from_plan else None
    if plan and not targets:
        # 没显式给件时，名册即计划名册（这才是「同源」的最强形态：不另立）
        targets = list(plan["roster"])

    if not targets:
        print("ERROR: 没有目标件（给 --skill 或 --from-plan）", file=sys.stderr)
        return 2

    result = build(targets, root=args.root, git=args.git, plan=plan,
                   expect_head=args.expect_head, require_head_pin=args.require_head_pin)
    if args.pin:
        result["head_pin"] = result["head"]
        result["head_pin_source"] = "cli --pin at %s" % result["generated_at"]
        result["assertions"]["head_pin"] = {
            "ok": True, "detail": "pin=%s（本次落盘基线；后续复跑用 --require-head-pin 校验）"
                                  % result["head_pin"]}

    if not args.quiet:
        print("root=%s head=%s" % (result["managed_root"], result["head"]))
        print("repo status: total=%d staged=%d worktree_only=%d untracked=%d (sum_ok=%s)"
              % (result["repo_status"]["total"], result["repo_status"]["staged"],
                 result["repo_status"]["worktree_only"], result["repo_status"]["untracked"],
                 result["repo_status"]["sum_check"]))
        print("can_land (%d): %s" % (len(result["can_land"]),
                                     ", ".join(x["slug"] for x in result["can_land"]) or "-"))
        print("blocked  (%d): %s" % (len(result["blocked"]),
                                     ", ".join("%s[%s]" % (x["slug"], "/".join(x["markers"]))
                                               for x in result["blocked"]) or "-"))
        print("unknown  (%d): %s" % (len(result["unknown"]),
                                     ", ".join("%s(%s)" % (x["slug"], x["reason"])
                                               for x in result["unknown"]) or "-"))
        if plan:
            print("plan=%s sha256_12=%s roster=%d targets_in_roster=%s unresolved_rows=%d"
                  % (plan["path"], plan["sha256_12"], plan["roster_total"],
                     set(targets) <= set(plan["roster"]), len(plan["unresolved_rows"])))
        for k, val in result["assertions"].items():
            print("assert %-20s ok=%s %s" % (k, val["ok"], val.get("detail", "")))
            for hit in val.get("hits", []):
                print("    hit: " + hit)

    if args.json:
        os.makedirs(os.path.dirname(os.path.abspath(args.json)), exist_ok=True)
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(result, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
        print("json=%s sha256_12=%s" % (args.json, sha256_12(args.json)))

    print(summarize(result))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
