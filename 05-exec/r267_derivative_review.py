"""LOCAL_DERIVATIVE_REVIEW ladder (R265-2 / r267).

Why: r265 classified 3 skills as LOCAL_DERIVATIVE_REVIEW (the local file is an expanded rewrite
of upstream). For that class a wholesale follow-version would delete local work, so the only
honest question is "which upstream sections are WORTH merging". This script answers it per
section: it aligns both files by heading, reports exact-match percentage per section, and flags
candidates. Sections whose upstream text is not exact-matched must be judged by a human
annotation file; a missing annotation yields UNVERIFIED (never silently "nothing to merge").

Promoted from _temp/ to 05-exec/ (r267): a tracked artifact must not cite a gitignored script as
its reproduce command, otherwise that command is dead on a fresh clone (r260/r265 lesson).

Read-only on D:/global_skills; writes one JSON under 06-benchmark/.
"""
# -*- coding: utf-8 -*-
"""R265-2 / r266: LOCAL_DERIVATIVE_REVIEW 3 件「并入候选段」人读比对（只读）。

为什么写这一版：r265 只给出行级集合读数（62.8% / 40.0% / 40.0%），回答不了
「上游哪几段值得并入」。本脚本把两份 SKILL.md 按 markdown 标题切段，逐段算出
可机读的三组证据（exact 行重合 / 标题是否在本地 / 结构元素配平），再与人读判定
（_temp/r266_annotations.json）合并成 06-benchmark/r265_derivative_review.json。

怎么运作：
1) 只读 D:/global_skills/<slug>/SKILL.md 与 <upstream-dir>/<slug>/SKILL.md；不写受管根。
2) 行归一化与 r265 完全一致（strip + 丢空行），据此复算 upstream_only_n / local_only_n，
   并与 06-benchmark/r265_follow_version_feasibility.json 逐值比对；不一致即退出码 4。
3) 上游按标题切段（代码围栏内的 # 不算标题）；无标题文件按空行切伪段（grill-me 上游即 6 行 stub）。
4) 每段算：exact 命中行数、本地同基名标题是否存在、本地对应段行数与结构元素计数、
   同族兄弟件（references/*.md 等）里同基名标题与 exact 行命中数。
5) 人读判定按 heading 精确注入；缺判定 = UNVERIFIED_NO_JUDGMENT（退出码 4），不静默放行。
6) 负向对照：--break-slug 把某件上游路径指向不存在 ⇒ 该行 UNVERIFIED + 退出码 3；
   另两行仍须 OK（证明是按件隔离，不是整体失败）。
"""
import argparse
import io
import json
import os
import re
import sys
import time

SK_ROOT = "D:/global_skills"
FEAS = "06-benchmark/r265_follow_version_feasibility.json"
HEAD = re.compile(r"^(#{1,6})\s+(.*)$")
BULLET = re.compile(r"^[-*]\s+")
ORDERED = re.compile(r"^\d+\.\s")
PAREN = re.compile(r"\s*[（(][^）)]*[）)]\s*$")


def norm_lines(text):
    """与 r265 feasibility 同口径：strip 后丢空行。"""
    return [x.strip() for x in text.split("\n") if x.strip()]


def base_heading(h):
    """去掉尾部括注，小写化：让「The Iron Law（吸收上游…）」对上「The Iron Law」。"""
    h = PAREN.sub("", h.strip())
    return re.sub(r"\s+", " ", h).strip().casefold()


def _blocks(lines, start_idx, end_idx, label_prefix):
    """把一段无标题正文按空行切成伪段（保住 grill-me 那种 stub 的最后一行）。"""
    out, cur = [], []
    for i in range(start_idx, end_idx):
        if lines[i].strip():
            cur.append((i + 1, lines[i]))
        elif cur:
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    real = []
    for n, blk in enumerate(out, 1):
        real.append({"heading": "%s %d" % (label_prefix, n), "level": 0,
                     "start": blk[0][0], "end": blk[-1][0],
                     "body": [x[1] for x in blk], "pseudo": True})
    return real


def split_sections(text):
    """按标题切段；代码围栏内的 # 不算标题；无标题则按空行切伪段。行号 1-based。"""
    lines = text.split("\n")
    fence, heads = False, []
    for i, s in enumerate(lines):
        if s.strip().startswith("```"):
            fence = not fence
            continue
        if fence:
            continue
        m = HEAD.match(s)
        if m:
            heads.append((i, len(m.group(1)), m.group(2).strip()))
    fm_end = 0
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                fm_end = i + 1
                break
    out = []
    if fm_end:
        out.append({"heading": "(frontmatter)", "level": 0, "start": 1, "end": fm_end,
                    "body": lines[0:fm_end], "pseudo": True})
    heads = [h for h in heads if h[0] >= fm_end]
    if heads:
        if heads[0][0] > fm_end and any(x.strip() for x in lines[fm_end:heads[0][0]]):
            pre = lines[fm_end:heads[0][0]]
            out.append({"heading": "(preamble)", "level": 0, "start": fm_end + 1,
                        "end": heads[0][0], "body": pre, "pseudo": True})
        for k, (i, lvl, h) in enumerate(heads):
            end = heads[k + 1][0] if k + 1 < len(heads) else len(lines)
            out.append({"heading": h, "level": lvl, "start": i + 1, "end": end,
                        "body": lines[i:end], "pseudo": False})
    else:
        out.extend(_blocks(lines, fm_end, len(lines), "(no-heading block)"))
    return out


def structure(body):
    """结构元素计数：表格行 / bullet / 代码围栏 / 有序步骤。
    译写会保结构、丢字面，所以「结构配平」是判「已覆盖但换了语言」的机读旁证。"""
    return {"table_rows": len([x for x in body if x.strip().startswith("|")]),
            "bullets": len([x for x in body if BULLET.match(x.strip())]),
            "fences": len([x for x in body if x.strip().startswith("```")]),
            "ordered": len([x for x in body if ORDERED.match(x.strip())])}


def load_siblings(slug):
    """读同族兄弟件（references/*.md 等），用于判「是否已吸收到分卷」。"""
    d = os.path.join(SK_ROOT, slug)
    cands = []
    for root, _dirs, names in os.walk(d):
        for n in sorted(names):
            if not n.lower().endswith(".md"):
                continue
            p = os.path.join(root, n)
            if os.path.abspath(p) == os.path.abspath(os.path.join(d, "SKILL.md")):
                continue
            rel_scan = os.path.relpath(p, d).replace("\\", "/")
            if rel_scan.startswith("references/"):
                pri = 0          # 分卷/吸收件最该先扫，别被模板目录挤掉
            elif "/" not in rel_scan:
                pri = 1
            elif n.lower().startswith("readme"):
                pri = 2
            else:
                pri = 3
            try:
                if os.path.getsize(p) > 200000:
                    continue
            except OSError:
                continue
            cands.append((pri, rel_scan, p))
    cands.sort(key=lambda x: (x[0], x[1]))
    files = [p for _pri, _rel, p in cands[:150]]
    heads, lineset, scanned, texts = [], set(), [], []
    for p in files:
        try:
            t = io.open(p, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        rel = os.path.relpath(p, d).replace("\\", "/")
        scanned.append(rel)
        texts.append(t)
        for sec in split_sections(t):
            if sec["level"]:
                heads.append((base_heading(sec["heading"]), sec["heading"], rel, sec["start"]))
        for x in norm_lines(t):
            lineset.add(x)
    return heads, lineset, scanned, "\n".join(texts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--upstream-dir", default="_temp/r265_follow_all")
    ap.add_argument("--out", default="06-benchmark/r265_derivative_review.json")
    ap.add_argument("--annotations", default="_temp/r266_annotations.json")
    ap.add_argument("--break-slug", default=None)
    ap.add_argument("--inventory", action="store_true")
    a = ap.parse_args()

    feas = json.load(io.open(FEAS, encoding="utf-8"))
    targets = [r for r in feas["rows"] if r["relationship"] == "LOCAL_DERIVATIVE_REVIEW"]
    assert len(targets) == 3, "LOCAL_DERIVATIVE_REVIEW 应恰为 3 件，实测 %d" % len(targets)
    ann = {}
    if os.path.isfile(a.annotations):
        ann = json.load(io.open(a.annotations, encoding="utf-8"))

    rows, unverified, repro_fail, audits = [], {}, [], []
    for t in targets:
        slug = t["skill"]
        up_dir = a.upstream_dir
        if a.break_slug == slug:
            up_dir = os.path.join(a.upstream_dir, "__negctl_missing__")
        up_path = os.path.join(up_dir, slug, "SKILL.md")
        lo_path = os.path.join(SK_ROOT, slug, "SKILL.md")
        if not os.path.isfile(up_path):
            rows.append({"slug": slug, "upstream_repo": t["repo"],
                         "upstream_ref": t["upstream_ref"],
                         "upstream_path": up_path.replace("\\", "/"),
                         "local_path": lo_path.replace("\\", "/"),
                         "local_lines": t["local_lines"], "upstream_lines": t["upstream_lines"],
                         "upstream_only_n": t["upstream_only_n"], "local_only_n": t["local_only_n"],
                         "upstream_lines_in_local_pct": None, "r265_reproduced": None,
                         "sections": [], "sections_n": 0,
                         "local_only_sections": [], "local_only_sections_n": None,
                         "merge_candidates": [], "merge_candidates_n": 0,
                         "verify_after_merge": ann.get(slug, {}).get("verify_after_merge", []),
                         "sibling_files_scanned": [],
                         "no_merge_reason": "UNVERIFIED：上游文件缺失（%s），不得当成「无可并入」" % up_path,
                         "evidence_cmd": ann.get(slug, {}).get("evidence_cmd"),
                         "measured_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                         "state": "UNVERIFIED", "unverified_reason": "UPSTREAM_MISSING",
                         "retry_n": 0})
            unverified[slug] = "UPSTREAM_MISSING"
            print("[UNVERIFIED] %-30s 上游缺失 %s" % (slug, up_path.replace("\\", "/")))
            continue
        ut = io.open(up_path, encoding="utf-8", errors="replace").read()
        lt = io.open(lo_path, encoding="utf-8", errors="replace").read()
        ul, ll = norm_lines(ut), norm_lines(lt)
        lset, uset = set(ll), set(ul)
        up_only, lo_only = len(uset - lset), len(lset - uset)
        pct = round(100.0 * len(uset & lset) / max(1, len(uset)), 1)
        repro = (len(ll) == t["local_lines"] and len(ul) == t["upstream_lines"]
                 and up_only == t["upstream_only_n"] and lo_only == t["local_only_n"]
                 and pct == t["upstream_lines_in_local_pct"])
        if not repro:
            repro_fail.append(slug)
        lsecs = split_sections(lt)
        lby = {}
        for s in lsecs:
            if s["level"]:
                lby.setdefault(base_heading(s["heading"]), []).append(s)
        sib_heads, sib_lines, sib_scanned, sib_blob = load_siblings(slug)
        sib_by_base = {}
        for b, h, f, ln in sib_heads:
            sib_by_base.setdefault(b, []).append({"heading": h, "file": f, "line": ln})
        secs_out = []
        used_bases = set()
        for s in split_sections(ut):
            key = base_heading(s["heading"]) if s["level"] else s["heading"]
            body = [x for x in s["body"] if x.strip()]
            if s["level"]:
                body = body[1:]
            n = len(body)
            matched = len([x for x in body if x.strip() in lset])
            only = [x for x in body if x.strip() not in lset]
            sib_hit = len([x for x in only if x.strip() in sib_lines])
            cp, cpsrc = None, None
            if not s["level"]:
                # 伪段只在同类伪段里配对：frontmatter <-> frontmatter；无标题块不配，
                # 否则「整篇按行重叠找最像的段」会配出毫无关系的对应。
                if s["heading"] == "(frontmatter)":
                    fm = [c for c in lsecs if c["heading"] == "(frontmatter)"]
                    if fm:
                        cp, cpsrc = fm[0], "pseudo_frontmatter"
            elif key in lby:
                cp = min(lby[key], key=lambda c: abs(c["start"] - s["start"]))
                cpsrc = "heading"
                used_bases.add(key)
            elif n and matched:
                best, bestn = None, 0
                for c in lsecs:
                    if not c["level"]:
                        continue
                    cb = set(x.strip() for x in c["body"] if x.strip())
                    k = len([x for x in body if x.strip() in cb])
                    if k > bestn:
                        best, bestn = c, k
                if best is not None and bestn >= max(2, int(0.3 * n)):
                    cp, cpsrc = best, "line_overlap"
            cstruct, parity = None, None
            if cp is not None:
                cstruct = structure(cp["body"])
                parity = cstruct == structure(body)
            sec = {"heading": s["heading"],
                   "upstream_line_span": [s["start"], s["end"]],
                   "upstream_lines": n,
                   "exact_matched_lines": matched,
                   "exact_match_pct": round(100.0 * matched / max(1, n), 1) if n else 0.0,
                   "upstream_only_lines": len(only),
                   "sibling_exact_line_hits": sib_hit,
                   "heading_in_local": bool(s["level"] and key in lby),
                   "local_counterpart": (None if cp is None else {
                       "heading": cp["heading"], "line_span": [cp["start"], cp["end"]],
                       "lines": len([x for x in cp["body"] if x.strip()]),
                       "matched_by": cpsrc, "structure": cstruct}),
                   "structure_parity": parity,
                   "sibling_headings": sib_by_base.get(key, []) if s["level"] else []}
            entry = None
            if isinstance(ann, dict) and slug in ann:
                for e in ann[slug].get("sections", []):
                    if e.get("heading") == s["heading"]:
                        entry = e
                        break
            if n == 0:
                sec.update({"coverage_basis": "EMPTY", "why_not_overwrite": "纯标题段（无正文行）",
                            "worth_merging": False, "merge_priority": None,
                            "merge_reason": "无正文行，无可并入内容", "unverified": False,
                            "judgment_source": "auto_exact"})
            elif matched == n:
                sec.update({"coverage_basis": "EXACT_IDENTICAL",
                            "why_not_overwrite": "上游本段 %d 行在本地逐字命中（100%%），本地已是同文" % n,
                            "worth_merging": False, "merge_priority": None,
                            "merge_reason": "无增量：字面已完全一致", "unverified": False,
                            "judgment_source": "auto_exact"})
            elif entry:
                for k in ("coverage_basis", "why_not_overwrite", "worth_merging",
                          "merge_priority", "merge_reason", "unverified"):
                    sec[k] = entry.get(k)
                sec["judgment_source"] = "human"
                sec["evidence"] = entry.get("evidence", [])
                sec["assertions_ok"] = True
                for asrt in entry.get("assertions", []):
                    ok = True
                    kind = asrt.get("kind")
                    if kind == "heading_in_sibling":
                        ok = bool(sib_by_base.get(base_heading(asrt.get("heading", ""))))
                    elif kind == "structure_parity":
                        ok = parity is True
                    elif kind == "exact_pct_at_least":
                        ok = sec["exact_match_pct"] >= asrt.get("v", 0)
                    elif kind == "heading_in_local":
                        ok = sec["heading_in_local"] is True
                    elif kind == "sibling_line_hits_at_least":
                        ok = sib_hit >= asrt.get("v", 0)
                    elif kind == "substring_in_sibling":
                        ok = asrt.get("text", "") in sib_blob
                    if not ok:
                        sec["assertions_ok"] = False
                        sec["unverified"] = True
                        audits.append("%s :: %s :: assertion FAIL %s" % (slug, s["heading"], asrt))
            else:
                sec.update({"coverage_basis": "UNVERIFIED_NO_JUDGMENT",
                            "why_not_overwrite": "UNVERIFIED：本段尚未人读判定",
                            "worth_merging": None, "merge_priority": None,
                            "merge_reason": "UNVERIFIED：缺人读判定",
                            "unverified": True, "judgment_source": "missing"})
                unverified.setdefault(slug, "SECTION_NO_JUDGMENT")
            secs_out.append(sec)
        meta = ann.get(slug, {}) if isinstance(ann, dict) else {}
        tmap = meta.get("targets", {})
        cands = []
        for s in secs_out:
            if s.get("worth_merging") is True:
                cands.append({"heading": s["heading"],
                              "upstream_line_span": s["upstream_line_span"],
                              "merge_priority": s["merge_priority"],
                              "reason": s["merge_reason"],
                              "target": tmap.get(s["heading"], lo_path.replace("\\", "/"))})
        local_only_heads = [lby[k][0]["heading"] for k in lby if k not in used_bases]
        row = {"slug": slug, "upstream_repo": t["repo"], "upstream_ref": t["upstream_ref"],
               "upstream_path": up_path.replace("\\", "/"),
               "local_path": lo_path.replace("\\", "/"),
               "local_bytes": len(lt.encode("utf-8")),
               "upstream_bytes": len(ut.encode("utf-8")),
               "local_lines": len(ll), "upstream_lines": len(ul),
               "upstream_lines_in_local_pct": pct,
               "upstream_only_n": up_only, "local_only_n": lo_only,
               "r265_reproduced": repro,
               "sections": secs_out, "sections_n": len(secs_out),
               "local_only_sections_n": len(local_only_heads),
               "local_only_sections": local_only_heads,
               "merge_candidates": cands, "merge_candidates_n": len(cands),
               "no_merge_reason": meta.get("no_merge_reason"),
               "verify_after_merge": meta.get("verify_after_merge", []),
               "evidence_cmd": meta.get("evidence_cmd"),
               "sibling_files_scanned": sib_scanned,
               "measured_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
               "state": "UNVERIFIED" if (slug in unverified or any(x["unverified"] for x in secs_out)) else "OK"}
        if row["state"] == "UNVERIFIED":
            row["unverified_reason"] = unverified.get(slug, "SECTION_UNVERIFIED")
        rows.append(row)
        print("[%-12s] %-30s sec=%-3d cand=%-2d up_only=%-4d local_only=%-4d pct=%.1f r265=%s"
              % (row["state"], slug, row["sections_n"], row["merge_candidates_n"],
                 up_only, lo_only, pct, "OK" if repro else "MISMATCH"))
        for s in secs_out:
            print("    - %-56s up=%-3d exact=%-5.1f cand=%-5s %s"
                  % (s["heading"][:56], s["upstream_lines"], s["exact_match_pct"],
                     s["worth_merging"], s["coverage_basis"]))

    ok_rows = [r for r in rows if r["state"] == "OK"]
    doc = {"schema": "derivative-review-v1",
           "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
           "provenance_cmd": "export PYTHONPYCACHEPREFIX=/tmp/pycache_r266 && python _temp/r266_derivative_review.py",
           "face_in": "06-benchmark/r265_follow_version_feasibility.json (relationship=LOCAL_DERIVATIVE_REVIEW)",
           "rule": "只覆盖同名文件、不镜像目录；本件只产「哪些上游段落值得并入」候选清单，不改受管根",
           "targets_n": len(rows), "rows_ok_n": len(ok_rows),
           "rows_unverified_n": len(rows) - len(ok_rows),
           "upstream_dir": a.upstream_dir, "rows": rows}
    if a.inventory:
        print("ROWS_JSON_START")
        print(json.dumps(doc, ensure_ascii=False)[:1200])
        print("ROWS_JSON_END")
    else:
        io.open(a.out, "w", encoding="utf-8").write(
            json.dumps(doc, ensure_ascii=False, indent=1) + "\n")
        print("WROTE %s rows=%d ok=%d unverified=%d"
              % (a.out, len(rows), len(ok_rows), len(rows) - len(ok_rows)))
    for msg in audits:
        print("AUDIT " + msg)
    if repro_fail:
        print("REPRO_MISMATCH " + ",".join(repro_fail))
        return 4
    if any(r["state"] == "UNVERIFIED" for r in rows):
        return 3
    if any(s["judgment_source"] == "missing" for r in rows for s in r["sections"]):
        return 4
    return 0


if __name__ == "__main__":
    sys.exit(main())
