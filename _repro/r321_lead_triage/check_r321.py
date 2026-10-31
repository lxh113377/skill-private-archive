# -*- coding: utf-8 -*-
"""r321 入口补链批次表的自证判据。

设计理由：批次表给人读就得带数字，但带数字就有抄错风险（本仓 r260 已为同类问题立过
"报告不抄数"的规矩）。这里折中：数字留在表里，判据从普查 JSON 现算 + 直接解析表内文本比对，
抄错即红。三条负控证明判据有牙（改数 / 造 slug / 吞账都必须判红）。
"""
import argparse, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SCAN = os.path.join(REPO, "_repro", "r320a", "entry_census", "entry_scan.r320.json")
PLAN = os.path.join(REPO, "04-plan", "入口补链批次表_r321_2026-10-31.md")

BATCH = {
    "B1": ["ppt-master"],
    "B2": ["story-setup"],
    "B3": ["story-long-write"],
    "B4": ["story-short-analyze", "story-short-write", "story-review", "story-long-analyze",
           "story-import", "story-deslop", "story-scan", "story-cover"],
    "B5": ["hyperframes", "hyperframes-media", "hyperframes-registry"],
    "B6": ["data-analysis", "gstack", "ui-ux-pro-max", "diagram-maker", "agent-browser",
           "frontend-skill", "theme-factory"],
}


def is_noise(path):
    """不该补链的噪声类：字体许可文本 / 许可证与致谢 / 目录级 README / 下划线内部索引。"""
    fn = path.split("/")[-1].lower()
    if "ofl" in fn:
        return True
    for p in ("license", "licence", "copying", "authors", "credits", "credit"):
        if fn.startswith(p):
            return True
    if fn == "readme.md":
        return True
    if fn.startswith("_"):
        return True
    return False


def compute():
    """从普查 JSON 现算每批真补链文件数与 KB，另给守恒用的总量。"""
    d = json.load(open(SCAN, encoding="utf-8"))
    per = {}
    for r in d["per_skill"]:
        prose_n = prose_b = noise_n = 0
        for o in (r.get("orphans") or []):
            if is_noise(o["path"]):
                noise_n += 1
            else:
                prose_n += 1
                prose_b += int(o.get("bytes") or 0)
        per[r["slug"]] = (prose_n, prose_b, noise_n)
    out = {}
    for b, slugs in BATCH.items():
        f = kb = 0
        for s in slugs:
            if s not in per:
                raise SystemExit("[R321:BATCH] FAIL slug absent from census: " + s)
            f += per[s][0]
            kb += per[s][1]
        out[b] = (f, int(round(kb / 1024.0)))
    covered = set()
    for v in BATCH.values():
        covered |= set(v)
    uncovered = sorted(s for s in per if per[s][0] > 0 and s not in covered)
    noise_total = sum(v[2] for v in per.values())
    prose_total = sum(v[0] for v in per.values())
    return out, uncovered, d, prose_total, noise_total


def parse_table():
    """从批次表正文里抓 | B<n> | ... | 文件数 | KB | 两个数字，与现算值比对。"""
    rows = {}
    for line in open(PLAN, encoding="utf-8"):
        s = line.strip()
        if not s.startswith("| B"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) < 4:
            continue
        key = cells[0].split(" ")[0].strip("*")
        try:
            rows[key] = (int(cells[2]), int(cells[3]))
        except ValueError:
            raise SystemExit("[R321:BATCH] FAIL table row not numeric: " + key)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--neg", choices=["kb", "slug", "swallow"], default=None,
                    help="负控：改数 / 凭空造 slug / 吞账，三种都必须判红")
    a = ap.parse_args()
    exp, uncovered, d, prose_total, noise_total = compute()
    got = parse_table()
    if a.neg == "kb" and exp: 
        k = sorted(exp)[0]
        got[k] = (got[k][0], got[k][1] + 1)
    if a.neg == "slug":
        exp["B9"] = (1, 1)
        got["B9"] = (1, 1)
        uncovered = ["ghost-skill-not-in-census"]
    if a.neg == "swallow":
        noise_total = 0
    fail = []
    if sorted(exp) != sorted(got):
        fail.append("batch keys differ: exp=" + repr(sorted(exp)) + " got=" + repr(sorted(got)))
    for b in sorted(set(exp) & set(got)):
        if exp[b] != got[b]:
            fail.append("MISMATCH " + b + " recomputed=" + repr(exp[b]) + " table=" + repr(got[b]))
    if uncovered:
        fail.append("uncovered slugs with prose>0: " + ",".join(uncovered))
    if d["orphan_total"] != prose_total + noise_total:
        fail.append("conservation broken: orphan_total=" + str(d["orphan_total"]) +
                      " prose=" + str(prose_total) + " noise=" + str(noise_total))
    tf = sum(v[0] for v in exp.values())
    tk = sum(v[1] for v in exp.values())
    if a.neg:
        if fail:
            print("[R321:BATCH] NEG " + a.neg + " teeth=pass fails=" + str(len(fail)))
            return 0
        print("[R321:BATCH] NEG " + a.neg + " teeth=FAIL (恒绿判据不可信)")
        return 1
    for f in fail:
        print("FAIL " + f)
    if fail:
        print("[R321:BATCH] batches=" + str(len(exp)) + " files=" + str(tf) + " kb=" + str(tk) +
              " coverage=RED")
        return 1
    print("[R321:BATCH] batches=" + str(len(exp)) + " files=" + str(tf) + " kb=" + str(tk) +
          " coverage=ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
