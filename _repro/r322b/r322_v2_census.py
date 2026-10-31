# -*- coding: utf-8 -*-
"""r322 v2 入口可达性普查 —— 三处口径修正（噪声白名单 / 占位符展开对树 / 嵌套闭包口径）。

为什么复用 check_r319a 的旧函数（import 同源）：R289-1 否决过静态复刻（零判别力）、
本仓 5.4 条写死「检查件必须 import 被检件的字段定义」⇒ 旧口径必须逐字节一致地复现，
v2 只做三处叠加修正，任何一处都能被 --closure/--json 现算出来。
三处修正（r321/r322 一手）：
  P-1 噪声白名单：OFL/LICENSE/README/_ 前缀 ⇒ 单独计数不进分母（72 件不该补链）
  P-2 占位符展开对树：NN/*/{} 形态按 glob 在该 slug 子树展开，命中≥1 ⇒ 剔出 broken 分母；
      命中 0 ⇒ 仍红（禁按形状豁免，反例 story-review/references/dispatch-NN.md）；
      html-ppt/examples/my-talk/index.html 是 new-deck.sh 运行产物 ⇒ GENERATED_OUTPUT_REF 桶（仍计 broken）。
  P-4 嵌套闭包：--closure nested 时同件所有 SKILL.md 都是入口（gstack 6/6 经嵌套可达）
"""
import argparse, fnmatch, io, json, os, re, subprocess, sys

OLD_DIR = r"C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化/_repro/r320a/entry_census"
sys.path.insert(0, OLD_DIR)
import check_r319a as old  # noqa: E402

BASELINE = r"C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化/_repro/r303a/absorption_baseline.json"

ROOT = "D:/global_skills"


def tree_clean(rev):
    """HEAD 全树 {path: bytes}。不复用 old.tree_at 的原因（一手）：旧件 git() 未带 -c core.quotepath=false，
    ls-tree 对非 ASCII 路径输出八进制引号形态（本仓 16509 条里 109 条），不 unquote 就整批丢中文文件；
    实测本 v2 首跑因此少 64 个孤儿（story-setup 32 + story-long-write 32），是 560 vs 624 的唯一差源。"""
    argv = ["git", "-c", "core.quotepath=false", "-C", ROOT, "ls-tree", "-r", "-l", rev]
    r = subprocess.run(argv, capture_output=True)
    out = {}
    for line in r.stdout.decode("utf-8", "replace").splitlines():
        if chr(9) not in line:
            continue
        meta, rest = line.split(chr(9), 1)
        parts = meta.split()
        if len(parts) != 4:
            continue
        size = parts[3]
        out[rest] = int(size) if size.isdigit() else 0
    return out

NOISE_RE = re.compile(
    r"(?:^|/)(?:[^/]*ofl[^/]*|licen[cs]e[^/]*|copying[^/]*|authors[^/]*|credits?[^/]*|readme\.md|_[^/]*)$", re.I)
PLACEHOLDER_RE = re.compile(r"(?:\bNN\b|\*|\{[^}]*\}|<[^>]*>|\$\{?[A-Za-z_]+\}?|\?[^/]*)")
GENOUT_HINTS = ("new-deck.sh", "scripts/new-deck", "my-talk")


def is_noise(path):
    """不该补链的噪声类（首版 624 里占 72 件；OFL 许可文本/目录README/_内部索引）。"""
    fn = path.rsplit("/", 1)[-1]
    return bool(NOISE_RE.search(path))


def expand_placeholder(slug, path, head_files):
    """占位符展开对树：把 NN/*/{} 形态当 glob 在本 slug 子树展开，命中任一真文件即视为「入口在引用一类文件」。"""
    prefix = slug + "/"
    pat = path if path.startswith(prefix) else prefix + path
    pat = pat.replace("NN", "*")
    hits = [f for f in head_files if f.startswith(prefix) and fnmatch.fnmatch(f, pat)]
    return hits


def genout(slug, path, entry_text):
    """GENERATED_OUTPUT_REF：入口写的路径是件内脚本的运行产物（静态口径下仍计 broken，只显影）。"""
    t = entry_text or ""
    if slug == "html-ppt" and "my-talk" in path and "new-deck" in t:
        return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--closure", choices=["top", "nested"], default="top")
    ap.add_argument("--json", dest="out")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        print("[V2:SELFTEST] noise_ofl=%s noise_readme=%s placeholder_NN=%s" % (
            is_noise("canvas-design/canvas-fonts/ArsenalSC-OFL.txt"),
            is_noise("ppt-master/scripts/README.md"),
            bool(PLACEHOLDER_RE.search("references/split-NN.md"))))
        return 0
    head_files = tree_clean("HEAD")
    bl = json.load(open(BASELINE, encoding="utf-8"))
    slugs = []
    for pr in bl["pairs"]:
        s = pr.get("slug")
        if s and s not in slugs:
            slugs.append(s)
    top_dirs = set(p.split("/")[0] for p in head_files if "/" in p)
    others = set(x.lower() for x in top_dirs if x not in slugs)
    up_names, up_dirs = old.upstream_excludes()
    per = []
    noise_n = noise_b = 0
    tot_br_real = tot_ph = tot_gen = tot_or_v2 = tot_or_top = 0
    for slug in slugs:
        text = old.entry_at("HEAD", slug) or ""
        # nested 口径：同件所有 SKILL.md 都当入口起点（结构可达口径；运行面裁决另有 r322a）
        entry_text = text
        if a.closure == "nested":
            extra = [f for f in head_files if f.startswith(slug + "/") and f.endswith("SKILL.md") and f != slug + "/SKILL.md"]
            for f in extra:
                entry_text += "\n" + (old.entry_at("HEAD", f[:-9]) or "")
        broken, orphans, drop, samples, nf = old.judge(slug, entry_text, head_files, up_names, up_dirs, others)
        br_real = ph_n = gen_n = 0
        orph_v2 = []
        noise_here = 0
        for pth, bts in orphans:
            if is_noise(pth):
                noise_here += 1
                noise_n += 1
                noise_b += bts
                continue
            orph_v2.append([pth, bts])
        for pth in list(broken):
            if PLACEHOLDER_RE.search(pth) and expand_placeholder(slug, pth, head_files):
                ph_n += 1
            elif genout(slug, pth, text):
                gen_n += 1
            else:
                br_real += 1
        tot_br_real += br_real
        tot_ph += ph_n
        tot_gen += gen_n
        tot_or_v2 += len(orph_v2)
        tot_or_top += len(orphans)
        per.append({"slug": slug, "broken": broken, "orphans": orphans,
                    "v2": {"broken_real": br_real, "placeholder": ph_n, "generated_output_ref": gen_n,
                           "orphans_prose": len(orph_v2), "orphans_noise": noise_here}})
    doc = {
        "schema": "r322-v2-census-1",
        "closure": a.closure,
        "slugs": len(slugs),
        "totals": {"broken_top": sum(len(p["broken"]) for p in per),
                   "orphans_top": tot_or_top,
                   "broken_real": tot_br_real, "placeholder": tot_ph, "generated_output_ref": tot_gen,
                   "orphans_v2_prose": tot_or_v2, "orphans_noise": noise_n, "noise_kb": int(round(noise_b / 1024.0))},
        "per": per,
    }
    if a.out:
        io.open(a.out, "w", encoding="utf-8").write(json.dumps(doc, ensure_ascii=False, indent=1))
    print("[V2:CENSUS] closure=%s broken_top=%d orphans_top=%d broken_real=%d placeholder=%d genout=%d orphans_prose=%d noise=%d" % (
        a.closure, sum(len(p["broken"]) for p in per), tot_or_top, tot_br_real, tot_ph, tot_gen, tot_or_v2, noise_n))
    return 0


if __name__ == "__main__":
    sys.exit(main())
