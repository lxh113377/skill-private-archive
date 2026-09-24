# -*- coding: utf-8 -*-
"""repeat_round_guard.py - r21 fail-closed pre-flight for auto-replayed identical prompts.

Why this exists (measured 2026-09-24, this repo alone):
  11 commits today, 9 of them 对标/benchmark rounds, 12,490 / 12,499 inserted lines (99.9%).
  The same 303-char prompt is injected on the hour by a scheduled Qoder session
  (log fingerprint: query_source="sdk", skip_initial_user_message=true, skip_slash_commands=true,
  on-the-hour starts sharing one PID, rotating cwd across projects: 超市web / 医 / 孝心联 / 本仓).
  Two sessions produced *divergent* "r20" artifacts within the same hour (19:06 vs 19:42)
  -> the loop does not only burn tokens, it forks concurrent work on one instruction.

Benchmark provenance for the mechanism (r18/r20 report lineage):
  * sickn33/agentic-awesome-skills - deterministic validation + fail-closed on unknown/ambiguous input
  * superpowers - repeated-work detection before doing the work again
  * addyosmani/agent-skills - "Verification is non-negotiable" (evidence, not vibes)

Semantics: exit 0 = FRESH/INCREMENT allowed ; exit 1 = DUPLICATE, full round forbidden.
Read-only. Never deletes anything; --record appends one line to memory/sessions/.
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    import _lib
except Exception:
    _lib = None

DEFAULT_PATTERN = r"对标|benchmark"
LESSONS_USAGE = Path(r"D:\global_memory\meta\lessons_usage.jsonl")


def git(repo, args):
    cmd = ["git", "-c", "core.quotepath=false", "-C", str(repo)] + args
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=120)
    except (subprocess.TimeoutExpired, OSError) as e:
        return None, str(e)
    if p.returncode != 0:
        return None, (p.stderr or p.stdout or "").strip()[:200]
    return p.stdout, None


def commit_rounds(repo, pattern, day):
    out, err = git(repo, ["log", "--since=%s 00:00" % day,
                          "--pretty=format:@@%h|%ad|%s", "--shortstat",
                          "--date=format:%H:%M"])
    if err:
        return None, err
    rx = re.compile(pattern)
    rounds, cur = [], None
    for ln in (out or "").splitlines():
        ln = ln.rstrip()
        if ln.startswith("@@"):
            parts = ln[1:].split("|", 2)
            if len(parts) != 3:
                continue
            cur = {"hash": parts[0], "time": parts[1], "subject": parts[2], "insertions": 0}
            rounds.append(cur)
        elif "insertion" in ln and cur is not None:
            m = re.search(r"(\d+) insertion", ln)
            if m:
                cur["insertions"] += int(m.group(1))
    bench = [r for r in rounds if rx.search(r["subject"])]
    return {"commits_today": len(rounds), "rounds": len(bench),
            "insertions_by_rounds": sum(r["insertions"] for r in bench),
            "last": bench[-1] if bench else None,
            "subjects": [r["time"] + " " + r["hash"] + " " + r["subject"][:56] for r in bench]}, None


def artifact_rounds(art_dir, day):
    d = Path(art_dir)
    if not d.is_dir():
        return {"exists": False}, None
    files = [p for p in d.iterdir() if p.is_file()
             and datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d") == day]
    return {"exists": True, "today_files": len(files), "files": sorted(p.name for p in files)[:12]}, None


def usage_hits(query, day):
    if not LESSONS_USAGE.is_file():
        return None
    key = re.sub(r"\s+", "", (query or ""))[:14]
    hits = []
    for ln in LESSONS_USAGE.read_text(encoding="utf-8", errors="replace").splitlines():
        ln = ln.strip()
        if not ln.startswith("{"):
            continue
        try:
            d = json.loads(ln)
        except Exception:
            continue
        q = re.sub(r"\s+", "", d.get("query") or "")
        if d.get("date") == day and key and key in q:
            hits.append(d.get("session"))
    return hits


def main():
    if _lib is not None:
        _lib.force_utf8_stdout()
    else:
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", required=True, help="本次要执行的指令原文")
    ap.add_argument("--repo", default=str(Path(__file__).resolve().parents[1]))
    ap.add_argument("--pattern", default=DEFAULT_PATTERN)
    ap.add_argument("--artifacts", default=None, help="产出目录（如 06-benchmark）")
    ap.add_argument("--threshold", type=int, default=2, help="当日同族轮次达到该值即判 DUPLICATE")
    ap.add_argument("--drift", action="store_true",
                    help="调用方已实测出真实漂移（上游数据/覆盖根变化）→ 允许 INCREMENT")
    ap.add_argument("--force", action="store_true", help="无视判定强行放行（须自担）")
    ap.add_argument("--record", action="store_true", help="把 verdict 追加到 memory/sessions/")
    args = ap.parse_args()

    day = datetime.now().strftime("%Y-%m-%d")
    repo = Path(args.repo)
    commits, err = commit_rounds(repo, args.pattern, day)
    if err:
        print("FAIL: git 取证失败(%s) → 无处可比，按 R247 拒绝放行" % err)
        return 2
    arts, _ = artifact_rounds(args.artifacts or (repo / "06-benchmark"), day)
    hits = usage_hits(args.query, day)

    rounds = commits["rounds"]
    sessions = sorted(set(hits or []))
    forked = len(sessions) >= 2
    if rounds >= args.threshold:
        verdict = "INCREMENT" if args.drift else "DUPLICATE"
    elif rounds >= 1:
        verdict = "THIN"
    else:
        verdict = "FRESH"
    allowed = verdict in ("FRESH", "THIN", "INCREMENT") or args.force

    print("=== 重复轮次闸门 (%s %s) ===" % (day, datetime.now().strftime("%H:%M")))
    print("同族提交: 当日 %d 轮 / 仓库总提交 %d ; 这些轮次新增 %s 行" % (
        rounds, commits["commits_today"], commits["insertions_by_rounds"]))
    print("产出目录: %s" % ("当日 %d 个文件" % arts["today_files"] if arts.get("exists") else "不存在"))
    print("同日同指令 session 记录: %d 个 %s%s" % (
        len(sessions), sessions[:6], "  <-- 多会话分叉" if forked else ""))
    for s in commits["subjects"][-4:]:
        print("   · %s" % s)
    print()
    print("判定: %s | 阈值 --threshold %d | 漂移 %s | 放行 %s" % (
        verdict, args.threshold, "已实测" if args.drift else "未见", "允许" if allowed else "禁止"))
    if verdict == "DUPLICATE":
        print("→ 禁止重跑全量轮。只允许：① 复跑既有计量工具做差值比对；② 补口径；③ 空转并记录一行。")
        print("→ 若本轮确有新证据，带 --drift 重新调用（须附实测命令与数字）。")

    rc = 0 if allowed else 1
    payload = {"date": day, "ts": datetime.now().strftime("%Y-%m-%d %H:%M"),
               "query_head": (args.query or "")[:60], "verdict": verdict, "allowed": allowed,
               "drift_flag": args.drift, "threshold": args.threshold,
               "commits": commits, "artifacts": arts, "same_day_sessions": sessions,
               "forked": forked, "exit_code": rc}
    if args.record:
        out = repo / "memory" / "sessions"
        out.mkdir(parents=True, exist_ok=True)
        with (out / "repeat-guard.jsonl").open("a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
        print("已追加: memory/sessions/repeat-guard.jsonl")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
