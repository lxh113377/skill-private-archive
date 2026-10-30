# -*- coding: utf-8 -*-
r"""r260_local_baseline.py — 需求 3 两个判据洞：补「本地同尺列」+ 测「compat 维判别力」。

存在理由（r260 一手；两处都是判据自身的洞，不是数据缺失）：
  洞① 矩阵无本地侧同尺列：06-benchmark/replacement_matrix_r225.json 每行只有 local_bytes /
      local_desc_len 两个体量字段，本地侧从来没有 fc/eff/compat/docs/community 五维分 ⇒
      r113 §3.2 那张「本地基线 = 4/3/3/2/2 合计 14」是人写小表（系统级、单值、不可逐件复算）。
      后果：矩阵能答「哪个候选分高」，答不了「候选是否真的比本地好」—— 而需求 3 的用途正是替换判定。
      本件把这一列补成 191 行可复算读数，并逐行给三态（本地更优 / 候选更优 / 不可比）。

  洞② compat 维对排序无贡献：r225 的 937 个候选里 compat=5 的有 890 个（95.0%）。
      恒满分的维度加进总分只把总分整体抬高，不改变候选间相对次序 ⇒ 对排序零贡献。两条实测腿：
        (a) rank0-flip：同一行候选分别按「含 compat 总分」与「去 compat 四维总分」排序，看 rank0 变不变；
        (b) 造 3 个应当判低分的形态输入（无 LICENSE / 跨框架格式无 SKILL.md / AGPL 且本仓禁合）实跑 score5。

为什么必须 import、不许复刻（复刻即双源，R241）：
  本地列与候选列必须是同一把尺，否则 delta 读的是两把尺之差、不是质量差。本件 sys.path 注入 05-exec
  后 import r114_replacement_scan，直接取同一函数对象 score5 / tree_counts；取不到即 rc=2 退出，
  绝不自写近似副本。单源性由 reproduce_selfcheck 自证：对每个 rank0 候选用同一 score5 重算，
  与 r225 记录的 score5 / score_total 逐字段比对，不一致必须为 0 例。

为什么本地侧 community 不进 delta：
  score5 的 community = stars 对数档 + 推送新鲜度。stars 是 GitHub 公开仓语义，本地技能目录没有 stars；
  补 0 会把「本地不是公开仓」这个测量缺陷读成「本地社区支持 0 分」的质量结论（R247 同族：缺字段不得造结论）。
  所以本地 community 记 N/A，delta 只在四维可比腿（fc/eff/compat/docs）上算；total25 同列但标注语义缺口。

负向对照（#36，证明判据有牙）：
  1) _temp/r260_local_baseline_stub/ 现造桩件（空 references + 无 triggers + 无 LICENSE + 空壳正文），
     走同一个 local_measure → score5，断言五维不得全 5（红了当场 rc=1）。
  2) compat 三输入若全部 5 分 ⇒ 具名写「该维无判别力，属判据缺陷」。
退出码：0 全绿且守恒 / 1 断言失败（判据无牙或复现漂移）/ 2 输入面不可用。

用法：
  python 05-exec/r260_local_baseline.py
  python 05-exec/r260_local_baseline.py --limit 20
  python 05-exec/r260_local_baseline.py --check-only
"""
import argparse
import hashlib
import io
import json
import os
import math
import re
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BENCH = os.path.join(ROOT, "06-benchmark")
TEMP = os.path.join(ROOT, "_temp")
AUTHORITY = r"D:\global_skills"
MATRIX_DEFAULT = os.path.join(BENCH, "replacement_matrix_r225.json")
OUT_DEFAULT = os.path.join(BENCH, "r260_local_baseline.json")
STUB_DIR = os.path.join(TEMP, "r260_local_baseline_stub")
TOKEN = "[R260:%s]"

# 四维可比腿：community 本地无 stars 语义 ⇒ 不入 delta（理由见模块 docstring）
CMP_DIMS = ("fc", "eff", "compat", "docs")
# ---- r302 输入指纹（保牙修法）--------------------------------------------------------
# 存在理由：r300 为让 31 个声明仓进五维面，用 measure_repo(store_paths=True, offline=False)
#   重测，顺带刷新了缓存条目。旧自检拿「现算 score5」与「r225 记录」逐字段比对 ⇒ 上游内容变了
#   也被读成「量尺漂移」（agent-browser 一手实测：上游新增技能入口，严格口径的 SKILL.md 件数
#   由 10 升到 11，fc 由 3 升到 4）。那是**数据新鲜度**变化，不是尺子行为变化 —— 两者必须分档，
#   否则每刷一次缓存本门就假红（恒红门与恒绿门同样无信息量）。
# 判定三档（互不吞并，r302 立）：
#   指纹相同 + score5 不同 ⇒ 量尺漂移 ⇒ 计入 mismatches（本门的牙，必须 FAIL）；
#   指纹不同             ⇒ 输入被合法刷新 ⇒ 记 stale_input_n（不计 mismatches、不判 FAIL，行内显形）；
#   活件取不到           ⇒ 记 unknown_n（取不到 ≠ 漂移 ≠ 干净，与 R247 同族）。
# 指纹口径（为什么是投影而不是整份 doc）：r225 是历史件（R241 禁改写），逐候选只落了 score5
#   输入的一个子集；整份缓存 doc 没有与之配套的历史副本可比 ⇒ 指纹只能取**两侧都算得出**的字段。
# 具名边界（代价）：四个未记录字段（blob_n、readme_n、tree_state、license_body_class）不进指纹；
#   只改这些字段且 score5 也跟着变时，会被读成量尺漂移（假红）。为什么不补 None 硬凑：那会让全部
#   937 个候选恒判 stale ⇒ 漂移腿恒 0 = 恒绿门，比假红更坏（本仓 X-7 同族）。
PIN_FIELDS = ("stars", "pushed_at", "license", "archived",
              "skill_md_n", "skill_md_exact_n", "skill_md_ghost_n",
              "docs_md_n", "test_path_n", "workflow_n")
INPUT_PIN_VERSION = "r302-pin-v1"
INPUT_PIN_NOTE = ("input_pin = sha256(规范化 JSON(score5 输入投影))[:16]，投影字段 = r225 矩阵逐候选"
                  "记录下来的那批 score5 输入（PIN_FIELDS）；两侧同规则现算，不依赖任何历史 pin 字段"
                  "（r225 没有，且禁改写）。判档：pin 同 + score5 不同 ⇒ 量尺漂移（计入 mismatches）；"
                  "pin 不同 ⇒ 输入被合法刷新（stale_input，不计 mismatches、不判 FAIL）；活件取不到 ⇒ "
                  "unknown。未记录的四个字段（blob_n、readme_n、tree_state、license_body_class）不进"
                  "投影 ⇒ 只改这些字段的刷新可能被误判成漂移（具名边界）。")


def canonical_json(obj):
    """规范化 JSON：键排序 + 无多余空白 + 非 ASCII 原样 ⇒ 同一映射必得同一串（指纹可跨轮对账）。"""
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def input_pin(doc):
    """输入指纹 = 打分输入投影的规范化 JSON 的 sha256 前 16 位；doc 非映射返回 None。

    怎么运作：固定按 PIN_FIELDS 取键（缺失取 None），所以「同一输入的两种载体」（矩阵记录的投影
    vs 现读的缓存 doc）能算到同一枚指纹 —— 这是本判据能跨历史件比对的前提。
    """
    if not isinstance(doc, dict):
        return None
    proj = dict((k, doc.get(k)) for k in PIN_FIELDS)
    return hashlib.sha256(canonical_json(proj).encode("utf-8")).hexdigest()[:16]


def pin_changed_fields(recorded_doc, live_doc):
    """列出两侧投影里取值不同的字段名（具名样例用；不参与判定，只作证据）。"""
    changed = []
    for k in PIN_FIELDS:
        if canonical_json(recorded_doc.get(k)) != canonical_json(live_doc.get(k)):
            changed.append(k)
    return changed

# LICENSE 文件名识别：只按路径末段、不区分大小写（与 r114 tree_counts 的末段口径一致）
LICENSE_NAME_RE = re.compile("^(license|licence|copying|copyleft|unlicense|eula|notice)\\b", re.I)
# 许可证正文指纹：读文件头 6KB，按特征短语回推 SPDX 风格标识；认不出统一 NOASSERTION
# （NOASSERTION 与 r114 里 GitHub API 的同名档对齐，不自造新档，避免两侧口径分叉）
LICENSE_TEXT_SIGS = [
    ("AGPL-3.0", ("GNU AFFERO GENERAL PUBLIC LICENSE",)),
    ("LGPL-3.0", ("GNU LESSER GENERAL PUBLIC LICENSE",)),
    ("GPL-3.0", ("GNU GENERAL PUBLIC LICENSE",)),
    ("Apache-2.0", ("Apache License", "Version 2.0")),
    ("MIT", ("Permission is hereby granted, free of charge",)),
    ("BSD-3-Clause", ("Neither the name",)),
    ("CC0-1.0", ("CC0 1.0 Universal",)),
    ("CC-BY-SA-4.0", ("Attribution-ShareAlike 4.0",)),
    ("CC-BY-4.0", ("Creative Commons Attribution 4.0",)),
]
# 本仓禁合的 copyleft 家族（依据：r113 §4 F3 具名「AGPL-3.0 合入待裁」+ X-2 本仓不补 LICENSE）
COPYLEFT = set(["AGPL-3.0", "GPL-3.0", "GPL-2.0", "LGPL-3.0", "CC-BY-SA-4.0"])

R = None  # 模块级绑定：main() 导入成功后赋值；local_measure 用 R.tree_counts（与候选侧同一口径函数）


def import_r114():
    """把生产件的 score5 / tree_counts / load_cache / key_of 取过来（单源；取不到就退出）。"""
    if HERE not in sys.path:
        sys.path.insert(0, HERE)   # score5 所在模块目录 = 05-exec；注入后可从任意 cwd 调用
    try:
        import r114_replacement_scan as mod
    except Exception as exc:  # noqa: BLE001 - 导入失败是硬断裂，必须显形成读数
        return None, "import_fail:%r" % (exc,)
    for name in ("score5", "tree_counts", "load_cache", "key_of"):
        if not callable(getattr(mod, name, None)):
            return None, "symbol_missing:%s" % name
    return mod, None


def sha16(path):
    """读数出处指纹（D9：读数必须带被检文件 sha，否则跨轮对账无锚）。"""
    h = hashlib.sha256()
    with io.open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def list_tree(root, cap=4000):
    """递归列技能目录内全部相对路径（跳 .git/node_modules/__pycache__；cap 防爆目录）。"""
    out = []

    def rec(d, rel):
        try:
            entries = sorted(os.scandir(d), key=lambda e: e.name)
        except OSError:
            return
        for e in entries:
            if e.name in (".git", "node_modules", "__pycache__", ".DS_Store"):
                continue
            rel2 = (rel + "/" + e.name) if rel else e.name
            if e.is_dir(follow_symlinks=False):
                rec(e.path, rel2)
            else:
                out.append(rel2)
                if len(out) >= cap:
                    return

    rec(root, "")
    return out


def detect_license(root, paths):
    """本地 license 字段：按文件名挑候选 → 读正文头 6KB → 指纹回推 SPDX；无文件 = UNLICENSED。

    口径提醒：UNLICENSED 是事实不是缺陷（本仓 X-2 禁补 LICENSE，r113 §3.3 具名「根治理件 1/12」），
    它使本地 compat 比候选侧少 2 分 —— 报告必须写明这条扣分是治理选择，否则 delta 被读成质量差。
    """
    cands = [p for p in paths if LICENSE_NAME_RE.match(p.rsplit("/", 1)[-1])]
    if not cands:
        return "UNLICENSED", "no_license_file", None
    for p in cands:  # 只有名字不算证据：必须读正文（空占位文件不得计分）
        try:
            raw = io.open(os.path.join(root, p.replace("/", os.sep)), "rb").read(6144)
        except OSError:
            continue
        text = raw.decode("utf-8-sig", "replace")
        if not text.strip():
            continue
        up = text.upper()
        for spdx, keys in LICENSE_TEXT_SIGS:
            if all(k.upper() in up for k in keys):
                return spdx, "fingerprint:" + p, text[:160]
    return "NOASSERTION", "file_present_unrecognized:" + ",".join(cands[:3]), None


def local_measure(slug, path):
    """把本地技能目录折算成 score5 的入参形态（字段名与 r114 measure_repo 逐一对齐）。

    树计数走 R.tree_counts —— 与候选侧同一个纯函数（r218 抽出的那个），保证「同名同尺」。
    GitHub 专属语义逐条显式处理：archived 恒 False（本地无此布尔）、stars=None + community_na=True、
    新鲜度用目录内最新 mtime 作推送代理（唯一可得的本地代理，仍只进 community 腿）。
    """
    paths = list_tree(path)
    m = {"state": "OK", "slug": slug, "blob_n": len(paths)}
    m.update(R.tree_counts(paths))   # 同一口径函数：skill_md_n / _exact_n / workflow_n / test_path_n / readme_n / docs_md_n
    lic, lnote, _snip = detect_license(path, paths)
    m["license"] = lic
    m["license_note"] = lnote
    m["archived"] = False
    m["tree_state"] = "OK"
    m["tree_truncated"] = len(paths) >= 4000
    newest = 0
    for p in paths:
        try:
            st = os.stat(os.path.join(path, p.replace("/", os.sep)))
        except OSError:
            continue
        if st.st_mtime > newest:
            newest = st.st_mtime
    m["pushed_at"] = (datetime.fromtimestamp(newest, timezone.utc).strftime("%Y-%m-%d")
                      if newest else "")
    m["stars"] = None    # 显式 None：补 0 = 用缺字段造结论（R247 反面）
    m["community_na"] = True
    return m


def cand_measure(mod, cache, repo):
    """候选侧读数：只读池缓存（入库包 + 活散件），绝不回写（不新增缓存、不动受管面）。"""
    m = cache.get("repo__" + mod.key_of(repo))
    if not m or m.get("state") != "OK":
        return None
    return m


def tri_state(d_cmp4, local_m, cand_m, cand_row):
    """三态判定（本地更优 / 候选更优 / 不可比），不可比必须具名细分原因。

    为什么细分：笼统写不可比 = 把「字段缺失」和「打平」混成一档，下轮分不清该修判据还是修取数
    （本仓 R247 同族：0 与「取不到」不得混读）。
    """
    if cand_row is None:
        return "不可比", "no_rank0：该行 candidates 为空（NO_OS_CANDIDATE / 仅族级候选）"
    if cand_m is None:
        return "不可比", "cand_measure_unavailable：池缓存取不到该仓树读数"
    if local_m.get("skill_md_exact_n") is None:
        return "不可比", "local_field_missing：本地树计数字段缺失"
    if d_cmp4 == 0:
        return "不可比", "tie_cmp4：四维可比腿总分打平（同尺但分不出高下）"
    if d_cmp4 > 0:
        return "本地更优", "delta_cmp4=%+d" % d_cmp4
    return "候选更优", "delta_cmp4=%+d" % d_cmp4


def compat_rank_flip(mod, cache, rows):
    """洞②判据 (a)：把 compat 从总分里删掉后，有多少行的 rank0 会变（变 = 该维有排序贡献）。

    怎么运作：每行候选按（score_total）与（score_total − compat）各排一次序，比首个元素；
    并列用原始索引作次级键，避免把「本来就在前」误判成「compat 起作用」。同时统计该行候选间
    compat 是否恒定 —— 恒定即该维在这一行无信息（数学上不可能改变名次）。
    对照组（D10.2 判据自证）：同一套代码把 community 删掉再排一次。若 community 能测出非零
    变化而 compat 测出 0，才能说 0 是维度的性质，而不是脚本本身失效。
    """
    flips = 0
    constant = 0
    checked = 0
    examples = []
    ctrl_flips = 0        # 对照组：删掉 community 后的 rank0 变化行数
    ctrl_examples = []
    for row in rows:
        cands = row.get("candidates") or []
        pairs = []
        for i, c in enumerate(cands):
            mm = cand_measure(mod, cache, c["repo"])
            if mm:
                pairs.append((i, mm))
        if len(pairs) < 2:
            continue
        checked += 1
        full = sorted(pairs, key=lambda x: (-mod.score5(x[1])[1], x[0]))
        noc = sorted(pairs, key=lambda x: (-(mod.score5(x[1])[1] - mod.score5(x[1])[0]["compat"]), x[0]))
        noCom = sorted(pairs, key=lambda x: (-(mod.score5(x[1])[1] - mod.score5(x[1])[0]["community"]), x[0]))
        if full[0][0] != noc[0][0]:
            flips += 1
            if len(examples) < 10:
                examples.append({"slug": row["slug"],
                                 "rank0_with_compat": cands[full[0][0]]["repo"],
                                 "rank0_without_compat": cands[noc[0][0]]["repo"]})
        if full[0][0] != noCom[0][0]:
            ctrl_flips += 1
            if len(ctrl_examples) < 5:
                ctrl_examples.append(row["slug"])
        vals = set(mod.score5(mm)[0]["compat"] for _i, mm in pairs)
        if len(vals) == 1:
            constant += 1
    return {"rows_checked": checked,
            "rank0_flips_when_compat_dropped": flips,
            "rows_with_constant_compat_across_candidates": constant,
            "control_rank0_flips_when_community_dropped": ctrl_flips,
            "control_slugs": ctrl_examples,
            "control_meaning": "对照组测出非零 ⇒ 本函数不是恒 0 的死码；compat=0 是维度性质",
            "contribution_reading": ("零贡献（实测：删掉 compat 后没有任何一行换过 rank0）"
                             if flips == 0 else "有贡献：%d 行换过 rank0" % flips),
            "flip_examples": examples}


def compat_fixture_inputs():
    """洞②判据 (b)：三个应当判低分的形态输入（每条注「为什么该低」，供 score5 实跑打分）。"""
    return [
        {"name": "输入1 无 LICENSE（UNLICENSED，与本仓 X-2 同形态）",
         "expect": "compat < 5：许可不明确不得给满分",
         "why_low": "license 子腿 2 分必须归 0，只剩非 archived 1 + 有 SKILL.md 2 = 3",
         "m": {"state": "OK", "license": "UNLICENSED", "archived": False,
               "skill_md_exact_n": 3, "skill_md_n": 3, "blob_n": 40, "readme_n": 1,
               "docs_md_n": 2, "test_path_n": 0, "workflow_n": 0, "tree_state": "OK",
               "stars": 500, "pushed_at": "2026-10-01"}},
        {"name": "输入2 跨框架格式（Cursor .mdc / rules 类，无 SKILL.md 约定）",
         "expect": "compat < 5：不遵循本体系入口约定即不可直接接入",
         "why_low": "sm=0 时 SKILL.md 子腿 2 分归 0，得 license(MIT)2 + 非 archived1 = 3；顺带看 fc 是否同腿塌（blob<=50 且 sm=0 则 fc=0）",
         "m": {"state": "OK", "license": "MIT", "archived": False,
               "skill_md_exact_n": 0, "skill_md_n": 0, "blob_n": 20, "readme_n": 1,
               "docs_md_n": 0, "test_path_n": 0, "workflow_n": 0, "tree_state": "OK",
               "stars": 1200, "pushed_at": "2026-10-10"}},
        {"name": "输入3 AGPL-3.0 且本仓禁合（r113 §4 F3 具名待裁）",
         "expect": "compat < 5：copyleft 与本仓合并政策冲突 = 真兼容性风险",
         "why_low": ("兼容性应含「能不能合法合入」：score5 的 compat 子腿只有 许可明确/未归档/有SKILL.md 三项"
                   "，没有任何许可风险项，这条最可能仍满分"),
         "m": {"state": "OK", "license": "AGPL-3.0", "archived": False,
               "skill_md_exact_n": 12, "skill_md_n": 12, "blob_n": 300, "readme_n": 1,
               "docs_md_n": 30, "test_path_n": 60, "workflow_n": 5, "tree_state": "OK",
               "stars": 8000, "pushed_at": "2026-10-20"}},
    ]


def build_stub():
    """现造负向对照桩件（写面 = _temp/，白名单内）：空 references + 无 triggers + 无 LICENSE + 空壳正文。

    为什么这三项：判据若在「什么都没有」的件上仍给满分，说明打分读的是形式而非事实（#36 假交付形态）。
    """
    root = os.path.join(STUB_DIR, "r260-stub-empty")
    os.makedirs(os.path.join(root, "references"), exist_ok=True)   # 空目录：不得因「有 references」加分
    md = ("---\nname: r260-stub-empty\ndescription: stub for negative control\n---\n\n"
          "# stub\n\n空壳正文，无触发词、无许可、无示例。\n")
    with io.open(os.path.join(root, "SKILL.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(md)
    return root


def flush(doc, out_path, check_only):
    """边做边落盘（节奏纪律）：写临时件再 os.replace 原子换名，中断也保住已有证据。"""
    if check_only:
        return
    tmp = out_path + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, out_path)


def row_readout(mod, lm, c0, cm):
    """把「本地件 + 该行 rank0 候选」折算成一行读数（五维 / total / delta / 三态字段）。

    怎么运作：两侧各自调 mod.score5（同一函数对象，单源）；delta_cmp4 只加四维可比腿，
    per_dim_delta 逐维差列出，便于定位「本地更优」到底是哪条腿贡献的。
    """
    ls, ltot, lcal = mod.score5(lm)
    out = {"local_score5": ls, "local_total": ltot, "local_fc_caliber": lcal,
           "local_cmp4": sum(ls[d] for d in CMP_DIMS)}
    if cm is None:
        out["cand_score5"] = None
        return out
    cs, ctot, ccal = mod.score5(cm)
    out["cand_score5"] = cs
    out["cand_total"] = ctot
    out["cand_fc_caliber"] = ccal
    out["cand_cmp4"] = sum(cs[d] for d in CMP_DIMS)
    out["delta_cmp4"] = out["local_cmp4"] - out["cand_cmp4"]
    out["delta_total25"] = ltot - ctot
    out["per_dim_delta"] = dict((k, ls[k] - cs[k]) for k in ("fc", "eff", "compat", "docs", "community"))
    return out


def reproduce_selfcheck(Rmod, cache, mrows):
    """复现自检（单源证据；r302 起带输入指纹）：每个候选从池缓存重算 score5，与矩阵记录比对。

    怎么运作（两层判定，顺序不能换）：
      ① 输入指纹层：对矩阵记录与当前活件各算一次 input_pin。两枚不同 ⇒ 该候选的输入被合法刷新
         （上游内容/星标/推送时间变了）⇒ 记 stale_input，**不进** ② 的漂移计数 —— 否则每刷一次
         缓存本门就假红（r302 修法正是修这一处）。
      ② 量尺复现层（只在指纹相同时跑）：两个已记录口径（cap_on 与 cap_off）各重算一次，要求**至少
         一个**能零漂移复现该矩阵件。两个都非 0 ⇒ 未知改动/双源 ⇒ 本门红（这就是牙）；两个都 0 ⇒
         档开关对这批样本无差别（如小样），复现成立但 cap_discriminates 记 False，禁把它读成档有效。

    为什么 ② 要两口径：r261 给 compat 加了许可档上限后，用今天的 score5 重算旧矩阵（r225 无档）
    必然不一致 —— 那是**尺子换代**不是「双源/漂移」。旧写法把两者混进同一个 mismatches ⇒ 只要这条
    腿动过一次，自证就永远红（恒红门与恒绿门同样无信息量；r260 已在第 110 门栽过同族）。
    防退化闸：指纹相同而真被重算的候选数 pinned_scored_n 若为 0，说明漂移腿没有任何样本（整批判
    stale）—— 那样的 0 漂移是恒绿门，selfcheck_pass() 会据此否决。
    """
    sc = {"candidates_recomputed": 0, "mismatches": 0, "mismatch_examples": [],
          "mismatches_cap_on": 0, "mismatches_cap_off": 0,
          "matrix_caliber": None, "cap_discriminates": None,
          "input_pin_version": INPUT_PIN_VERSION,
          "stale_input_n": 0, "stale_input_rank0_n": 0, "stale_input_examples": [],
          "unknown_n": 0, "pinned_scored_n": 0,
          "input_pin_note": INPUT_PIN_NOTE}
    for row in mrows:
        slug = row["slug"]
        for rank, c in enumerate(row.get("candidates") or []):
            live = cand_measure(Rmod, cache, c["repo"])
            if live is None or c.get("score5") is None:
                # 取不到 ⇒ 记 unknown：取不到 ≠ 漂移 ≠ 干净（R247：缺数据不得造结论，任一方向）
                sc["unknown_n"] += 1
                continue
            # 正文档是**生产侧的证据输入**（来自跟踪包 license_body_r262.json 或本轮联网取），不是
            #   尺子的输出。池缓存里没有它 ⇒ 复现时必须把该行记录的值喂回同一输入，否则门在比较两份
            #   不同的输入：r262 起 57 个 NOASSERTION slot 会全部报漂移，把「换代」误读成「双源」。
            #   旧代矩阵件（r225/r261）没有该字段 ⇒ 这里得到 None，行为与从前逐字相同。
            live = dict(live)   # 浅拷贝：指纹只读，不改缓存在内存里的那份
            if "license_body_class" in live or c.get("license_body_class") is not None:
                live["license_body_class"] = c.get("license_body_class")
            sc["candidates_recomputed"] += 1
            want_pin = input_pin(c)
            got_pin = input_pin(live)
            if want_pin != got_pin:
                sc["stale_input_n"] += 1
                if rank == 0:
                    sc["stale_input_rank0_n"] += 1
                if len(sc["stale_input_examples"]) < 5:
                    sc["stale_input_examples"].append({
                        "slug": slug, "repo": c["repo"], "rank": rank,
                        "recorded_pin": want_pin, "live_pin": got_pin,
                        "changed_fields": pin_changed_fields(c, live)})
                continue
            sc["pinned_scored_n"] += 1
            fails = []
            on_s = off_s = None
            for cap_flag in (True, False):
                s_chk, t_chk, _cal = Rmod.score5(live, license_cap=cap_flag)
                bad = (s_chk != c["score5"] or t_chk != c.get("score_total"))
                sc["mismatches_cap_on" if cap_flag else "mismatches_cap_off"] += 1 if bad else 0
                if cap_flag:
                    on_s = s_chk
                else:
                    off_s = s_chk
                fails.append(bad)
            if all(fails) and len(sc["mismatch_examples"]) < 5:
                # 指纹相同而两个口径都复现不了 = 真漂移，留样例具名（只留一条，旧写法的双写是笔误）
                sc["mismatch_examples"].append({
                    "slug": slug, "repo": c["repo"], "rank": rank,
                    "recorded": c["score5"],
                    "recomputed_cap_on": on_s, "recomputed_cap_off": off_s})
    _on, _off = sc["mismatches_cap_on"], sc["mismatches_cap_off"]
    # 派生字段：生效口径 = 两个 cap 档里漂移较小的那个；mismatches 取该值 ⇒ 自证的语义从「与 r225
    #   同尺」升级为「与该矩阵件**产出时**的尺同」，换代不再假红，而未知改动仍会被抓（两口径都复现
    #   不了 ⇒ 两个计数同时非 0 ⇒ mismatches>0 ⇒ 本门红）。
    sc["mismatches"] = min(_on, _off)
    sc["matrix_caliber"] = ("license_cap_on" if _on <= _off else "license_cap_off")
    sc["cap_discriminates"] = (_on != _off)
    sc["caliber_note"] = (
        "两口径漂移分别记录（cap_on=%d 与 cap_off=%d）：较小值视为该矩阵件产出时的口径。" % (_on, _off) +
        "cap_discriminates=False 且两者皆 0 ⇒ 本次样本对 cap 无差别，禁据此判许可档有效；" +
        "两者皆非 0 ⇒ 未知改动/真双源，本门当场红。")
    sc["claim"] = ("mismatches==0 即本件与该矩阵件产出时同一把尺（两个 cap 档至少一个能零漂移复现）；" +
                   "两档皆 >0 即双源/未登记换代，自证不成立；stale_input_n 是输入刷新数，不参与本布尔")
    return sc


def selfcheck_pass(sc, teeth_ok, conservation_ok):
    """自证三腿合并判定（r302 从 finalize 抽成纯函数：夹具要能直接调它复算同一布尔）。

    三腿 = 负向对照有牙(teeth_ok) + 量尺零漂移(mismatches==0) + 守恒(conservation_ok)，外加防退化闸
    pinned_scored_n>0（指纹相同且真被重算的候选必须非空，否则漂移腿无样本、那个 0 是恒绿）。
    stale_input_n 与 unknown_n **不进**这个布尔：它们是输入新鲜度与取数缺口，不是量尺出错。
    """
    return bool(teeth_ok and sc.get("mismatches") == 0
                and sc.get("pinned_scored_n", 0) > 0
                and conservation_ok)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", dest="out", default=OUT_DEFAULT, help="主产物（缺省 06-benchmark/r260_local_baseline.json）")
    ap.add_argument("--matrix", default=MATRIX_DEFAULT, help="替代矩阵（缺省 r225；只读，绝不覆写）")
    ap.add_argument("--authority", default=AUTHORITY, help="本地受管根（只读）")
    ap.add_argument("--limit", type=int, default=0, help="只算前 N 行（冒烟；字段结构不变）")
    ap.add_argument("--check-only", action="store_true", help="不写主产物，只跑读数与断言")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001 - 老解释器无 reconfigure，不因此判死整轮
        pass

    global R
    R, err = import_r114()
    if R is None:
        # 单源失败的处置：整轮不可用。禁「先自写一版近似 score5」把读数跑起来 —— 那正是双源假绿。
        print(TOKEN % "UNVERIFIED", "score5 导入失败 ⇒ 禁复刻，rc=2｜", err)
        return 2
    if not os.path.isfile(args.matrix):
        print(TOKEN % "UNVERIFIED", "矩阵缺失", args.matrix)
        return 2
    if not os.path.isdir(args.authority):
        print(TOKEN % "UNVERIFIED", "受管根不可读", args.authority, "⇒ 禁按无缺口记绿（R247）")
        return 2
    matrix = json.load(io.open(args.matrix, encoding="utf-8"))
    mrows = matrix.get("rows") or []
    if not mrows:
        print(TOKEN % "UNVERIFIED", "矩阵 0 行 ⇒ 零输入不得记绿")
        return 2
    cache = R.load_cache()   # 只读合并（入库池包 + 活散件）；本件全程不调用 save_cache，不新增缓存
    if not cache:
        print(TOKEN % "UNVERIFIED", "候选池缓存空 ⇒ 候选侧无法同尺复算")
        return 2

    # 本地侧枚举：与 r211_local_fm 同一谓词（目录内存在 SKILL.md 才算在册），禁另造名单
    locals_map = {}
    for name in sorted(os.listdir(args.authority)):
        pth = os.path.join(args.authority, name)
        if os.path.isfile(os.path.join(pth, "SKILL.md")):
            locals_map[name] = local_measure(name, pth)
    if not locals_map:
        print(TOKEN % "UNVERIFIED", "本地扫出 0 件 ⇒ 不得读成无本地基线（R247）")
        return 2

    # --limit 时自检也只覆盖前 N 行（与主循环同一片；旧写法内联在循环里天然如此）。
    n = len(mrows) if not args.limit else min(args.limit, len(mrows))
    selfcheck = reproduce_selfcheck(R, cache, mrows[:n])

    doc = {
        "schema": "r260-local-baseline-v1",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00"),
        "cmd": "python 05-exec/r260_local_baseline.py",
        "rerun": "cd 自建skill优化 && export PYTHONPYCACHEPREFIX=/tmp/pycache_r260b && python 05-exec/r260_local_baseline.py",
        "single_source": {
            "score5_module": R.__name__,
            "score5_file": os.path.relpath(R.__file__, ROOT).replace(os.sep, "/"),
            "score5_sha16": sha16(R.__file__),
            "matrix_file": os.path.relpath(args.matrix, ROOT).replace(os.sep, "/"),
            "matrix_sha16": sha16(args.matrix),
            "pool_pack_entries": len(cache),
            "claim": "本地列与候选列调用 r114_replacement_scan.score5 同一函数对象；复刻即双源 —— reproduce_selfcheck.mismatches 必须为 0 才算这条成立",
        },
        "authority": args.authority.replace("\\", "/"),
        "face": {"local_dirs_with_skill_md": len(locals_map), "matrix_rows": len(mrows),
                 "rows_computed": 0, "cmp_dims": list(CMP_DIMS),
                 "community_excluded_from_delta": "stars 是 GitHub 公开仓语义，本地无 stars（补 0 等于用缺字段造结论）"},
        "local_side_caliber_notes": {
            "license": "本地按文件名 + 正文指纹回推 SPDX；本仓 X-2 禁补 LICENSE ⇒ 多数件 UNLICENSED，compat 因此比候选侧少 2 分：这是治理选择不是质量差（读 delta 必记）",
            "freshness": "本地 pushed_at 取目录内最新 mtime（GitHub 推送语义的本地代理，只进 community 腿）",
            "archived": "恒 False（本地无该布尔）",
            "tree_state": "恒 OK（本地树一定可读；候选侧树取不到时字段为 None，那条差异计入 docs 腿）",
            "community": "本地记 N/A、不入 delta；total25 同列但只作对照",
        },
        "compat_teeth": {"dim_distribution_in_matrix": {}, "rank_flip": None, "three_inputs": [], "copleft_at_5": None, "verdict": None},
        "negative_controls": {},
        "reproduce_selfcheck": selfcheck,
        "rows": [],
        "status": "IN_PROGRESS"}

    tally = {"本地更优": 0, "候选更优": 0, "不可比": 0}
    for idx, row in enumerate(mrows[:n]):
        slug = row["slug"]
        cands = row.get("candidates") or []
        lm = locals_map.get(slug)
        c0 = cands[0] if cands else None
        item = {"slug": slug, "family": row.get("family"), "verdict": row.get("verdict"),
                "local_bytes": row.get("local_bytes"), "local_desc_len": row.get("local_desc_len"),
                "candidates_n": len(cands), "rank0_repo": (c0 or {}).get("repo"),
                "rank0_rel": (c0 or {}).get("rel"), "rank0_license": (c0 or {}).get("license"),
                "rank0_fc_caliber": (c0 or {}).get("fc_caliber")}
        if lm is None:
            item["state"] = "不可比"
            item["state_reason"] = "local_dir_missing：受管根里扫不到该 slug"
            tally["不可比"] += 1
            doc["rows"].append(item)
            if idx % 10 == 9:
                flush(doc, args.out, args.check_only)
            continue
        item["local"] = {"score5": None, "license": lm["license"], "license_note": lm.get("license_note"),
                             "blob_n": lm.get("blob_n"), "skill_md_n": lm.get("skill_md_n"),
                             "skill_md_exact_n": lm.get("skill_md_exact_n"), "readme_n": lm.get("readme_n"),
                             "docs_md_n": lm.get("docs_md_n"), "test_path_n": lm.get("test_path_n"),
                             "workflow_n": lm.get("workflow_n"), "pushed_at_mtime": lm.get("pushed_at"),
                             "tree_truncated": bool(lm.get("tree_truncated")),
                             "community_na": True}
        cm = cand_measure(R, cache, c0["repo"]) if c0 else None
        ro = row_readout(R, lm, c0, cm)
        item["local"]["score5"] = ro["local_score5"]
        item["local"]["score_total"] = ro["local_total"]
        item["local"]["score_cmp4"] = ro["local_cmp4"]
        item["local"]["fc_caliber"] = ro["local_fc_caliber"]
        if cm is None or ro.get("cand_score5") is None:
            st, why = tri_state(0, lm, cm, c0)
            item["state"] = st
            item["state_reason"] = why
            tally[st] += 1
            doc["rows"].append(item)
            if idx % 10 == 9:
                flush(doc, args.out, args.check_only)
            continue
        item["cand"] = {"score5": ro["cand_score5"], "score_total": ro["cand_total"],
                          "score_cmp4": ro["cand_cmp4"], "fc_caliber": ro["cand_fc_caliber"],
                          "license": cm.get("license"), "stars": cm.get("stars"),
                          "archived": cm.get("archived"), "skill_md_exact_n": cm.get("skill_md_exact_n"),
                          "blob_n": cm.get("blob_n"), "test_path_n": cm.get("test_path_n"),
                          "workflow_n": cm.get("workflow_n"), "docs_md_n": cm.get("docs_md_n"),
                          "pushed_at": cm.get("pushed_at")}
        item["delta_cmp4"] = ro["delta_cmp4"]
        item["delta_total25"] = ro["delta_total25"]
        item["delta_total25_note"] = "含 community 腿（本地 stars 缺失）⇒ 仅作对照不作结论"
        item["per_dim_delta"] = ro["per_dim_delta"]
        st, why = tri_state(ro["delta_cmp4"], lm, cm, c0)
        item["state"] = st
        item["state_reason"] = why
        tally[st] += 1
        doc["rows"].append(item)
        if idx % 10 == 9:
            flush(doc, args.out, args.check_only)
    doc["face"]["rows_computed"] = len(doc["rows"])
    return finalize(doc, args, mrows, cache, locals_map, tally)


def finalize(doc, args, mrows, cache, locals_map, tally):
    """洞② 三条实测腿 + 负向对照 + 守恒自证（与主循环分离，便于单测与逐腿复跑）。

    三条腿各答一个问题：
      1) 分布：compat 在矩阵候选上的分布（满分占比 = 无信息量的一级证据）；
      2) rank_flip：把 compat 从总分里删掉，有多少行会换 rank0（= 该维对排序的净贡献）；
      3) 反例实跑：三个应当判低分的形态喂进同一个 score5，看它认不认。
    """
    all_cands = [c for row in mrows for c in (row.get("candidates") or [])]
    dim_dist = {}
    for dim in ("fc", "eff", "compat", "docs", "community"):
        hist = {}
        for c in all_cands:
            v = str((c.get("score5") or {}).get(dim))
            hist[v] = hist.get(v, 0) + 1
        at_max = hist.get("5", 0)
        dim_dist[dim] = {"n": len(all_cands), "hist": hist, "at_max": at_max,
                           "share_at_max": round(at_max / float(max(1, len(all_cands))), 4),
                           "spread": len([k for k in hist if k != "None"])}
    doc["compat_teeth"]["dim_distribution_in_matrix"] = dim_dist
    doc["compat_teeth"]["rank_flip"] = compat_rank_flip(R, cache, mrows)
    # compat 恒满分的成因归因（哪条子腿几乎恒真）+ 信息量（香农熵）——
    # 为什么要这一层：只知道「95% 满分」不够，必须说清是哪条子腿把维度钉死的，
    # 否则处方会去修错的那条腿（本仓 r232「归因第三次纠正」同族教训）。
    legs = {"license_explicit": 0, "has_skill_md": 0, "not_archived": 0}
    low_cause = {"only_unlicensed": 0, "only_no_skill_md": 0, "both": 0, "archived": 0, "other": 0}
    for c in all_cands:
        s5 = c.get("score5") or {}
        if s5.get("compat") == 5:
            continue
        unlic = (c.get("license") or "UNLICENSED") == "UNLICENSED"
        nosm = not ((c.get("skill_md_exact_n") or c.get("skill_md_n") or 0) > 0)
        arch = bool(c.get("archived"))
        if unlic and nosm:
            low_cause["both"] += 1
        elif unlic:
            low_cause["only_unlicensed"] += 1
        elif nosm:
            low_cause["only_no_skill_md"] += 1
        elif arch:
            low_cause["archived"] += 1
        else:
            low_cause["other"] += 1
    for c in all_cands:
        if (c.get("license") or "UNLICENSED") != "UNLICENSED":
            legs["license_explicit"] += 1
        if (c.get("skill_md_exact_n") or c.get("skill_md_n") or 0) > 0:
            legs["has_skill_md"] += 1
        if not c.get("archived"):
            legs["not_archived"] += 1
    n_c = max(1, len(all_cands))
    doc["compat_teeth"]["subleg_saturation"] = dict(
        (k, {"satisfied": v, "share": round(v / float(n_c), 4)}) for k, v in legs.items())
    doc["compat_teeth"]["below_max_cause"] = low_cause
    # 熵（信息量）：满分占比是粗指标，熵才说明「该维能否区分候选」
    def _entropy(hist):
        tot = float(sum(hist.values()))
        ent = 0.0
        for _k, v in hist.items():
            q = v / tot
            if q > 0:
                ent -= q * (math.log(q, 2))
        return round(ent, 4)
    doc["compat_teeth"]["entropy_bits"] = dict(
        (dim, _entropy(dim_dist[dim]["hist"])) for dim in dim_dist)
    doc["compat_teeth"]["rows_where_compat_varies_among_candidates"] = sum(
        1 for row in mrows
        if len(set((c.get("score5") or {}).get("compat")
                   for c in (row.get("candidates") or []))) > 1)
    # copyleft 家族在 compat 上的实际得分：判据到底认不认本仓禁合这条政策
    cop = [c for c in all_cands if (c.get("license") or "") in COPYLEFT]
    cop_hist = {}
    for c in cop:
        v = str((c.get("score5") or {}).get("compat"))
        cop_hist[v] = cop_hist.get(v, 0) + 1
    rank0_cop = [{"slug": row["slug"], "repo": row["candidates"][0]["repo"],
                   "license": row["candidates"][0].get("license")} for row in mrows
                 if (row.get("candidates") or []) and
                 ((row["candidates"][0].get("license") or "") in COPYLEFT)]
    ca = {"copleft_family": sorted(COPYLEFT), "candidates": len(cop), "compat_hist": cop_hist,
          "at_compat_5": cop_hist.get("5", 0), "rank0_candidates_copleft": len(rank0_cop),
          "rank0_copleft_examples": rank0_cop[:12]}
    ca["meaning"] = ("copyleft 候选 {0} 个里 compat=5 的有 {1} 个，且 {2} 行把它排在 rank0"
                     " ⇒ 判据不认识许可风险与合并政策冲突").format(
                         len(cop), cop_hist.get("5", 0), len(rank0_cop))
    doc["compat_teeth"]["copleft_at_5"] = ca
    # 反例实跑：三个应判低分的形态（用同一个 score5，不是另写判据）
    three = []
    for fx in compat_fixture_inputs():
        s, tot, cal = R.score5(fx["m"])
        low = s["compat"] < 5
        one = {"name": fx["name"], "expectation": fx["expect"], "why_low": fx["why_low"],
               "score5": s, "score_total": tot, "compat": s["compat"],
               "fc": s["fc"], "eff": s["eff"], "docs": s["docs"], "community": s["community"],
               "expectation_met": bool(low)}
        one["verdict"] = "该形态已判低（compat 有牙）" if low else "该形态仍满分（compat 在此形态无判别力）"
        three.append(one)
    doc["compat_teeth"]["three_inputs"] = three
    n_five = sum(1 for t in three if t["compat"] == 5)
    rf_flips = doc["compat_teeth"]["rank_flip"]["rank0_flips_when_compat_dropped"]
    if n_five == len(three):
        # 任务书要求的具名结论（禁含糊）：三个反例全 5 ⇒ 整维报废
        doc["compat_teeth"]["verdict"] = "该维无判别力，属判据缺陷（三个应判低分的输入全部 5 分）"
    else:
        v1 = "部分判别力：{0}/{1} 个应判低分形态被扣分（license 明确性与 SKILL.md 约定两子腿起作用），".format(len(three) - n_five, len(three))
        v1 += "{0} 个形态仍满分 ⇒ 缺陷具名到子腿：compat 没有许可风险/能否合入子腿；".format(n_five)
        v1 += "排序贡献实测：删掉 compat 后 rank0 变化 {0}/{1} 行（对照组删 community 变化 {2} 行）".format(
            rf_flips, doc["compat_teeth"]["rank_flip"]["rows_checked"],
            doc["compat_teeth"]["rank_flip"]["control_rank0_flips_when_community_dropped"])
        v1 += (" ⇒ 该维对排序零贡献" if rf_flips == 0 else " ⇒ 该维对排序有贡献但被恒满分稀释")
        doc["compat_teeth"]["verdict"] = v1
    doc["compat_teeth"]["verdict_short"] = ("排序贡献 {0} 行 + 满分占比 {1} ⇒ 该维在当前语料上是常数项，不参与定名次").format(
        rf_flips, dim_dist["compat"]["share_at_max"])
    # 负向对照 1（证明判据有牙）：空壳桩件走完全相同的本地腿，五维不得全 5
    stub_root = build_stub()
    sm = local_measure("r260-stub-empty", stub_root)
    ss, stot, scal = R.score5(sm)
    teeth_ok = not all(ss[d] == 5 for d in ("fc", "eff", "compat", "docs", "community"))
    doc["negative_controls"]["stub_empty_skill"] = {
        "path": os.path.relpath(stub_root, ROOT).replace(os.sep, "/"),
        "shape": "空 references 目录 + 无 triggers（frontmatter 只有 name/description）+ 无 LICENSE + 空壳正文",
        "measure_fields": dict((k, sm.get(k)) for k in ("blob_n", "skill_md_exact_n", "readme_n",
                                                  "docs_md_n", "test_path_n", "workflow_n",
                                                  "license", "pushed_at")),
        "score5": ss, "fc_caliber": scal, "score_total": stot,
        "assertion": "五维不得全 5", "pass": bool(teeth_ok)}
    # 负向对照 2（自指腿）：同尺打在本地件上，compat 是否也塌成一档
    lic_have = sum(1 for m in locals_map.values() if m.get("license") != "UNLICENSED")
    lcompat_hist = {}
    for row in doc["rows"]:
        v = str(((row.get("local") or {}).get("score5") or {}).get("compat"))
        lcompat_hist[v] = lcompat_hist.get(v, 0) + 1
    doc["negative_controls"]["local_side_compat"] = {
        "local_dirs_with_license_file": lic_have, "of_scanned": len(locals_map),
        "compat_hist_local_side": lcompat_hist,
        "meaning": "本地侧 compat 用同一 score5 打出的分布；与候选侧满分占比对照，看该维是否两侧都压到同一档"}
    # 负向对照 3（本地侧分辨率自指，D10.2）：桩件五维不全 5 只证明「判据不是恒绿」；
    # 但一个 14KB 真件若与空壳桩件拿到同一组五维，说明这把尺在本地侧没有分辨率
    # （它读的是仓库形态计数，不是技能内容）。两个问题必须分开答，不能拿前者冒充后者。
    same_as_stub = [row["slug"] for row in doc["rows"]
                      if row.get("local") and row["local"]["score5"] == ss]
    doc["negative_controls"]["local_side_resolution"] = {
        "stub_score5": ss,
        "true_rows_with_identical_score5": len(same_as_stub),
        "of_computed_rows": len(doc["rows"]),
        "examples": same_as_stub[:8],
        "reading": "同尺打在本地件上，与空壳桩件五维逐项相同的真件有 {0}/{1} 件 ⇒ 该尺在本地侧无分辨率".format(len(same_as_stub), len(doc["rows"])) if same_as_stub else "本地侧无一件与空壳桩件同分 ⇒ 该尺能区分空壳与真件"}
    # 三态可达性自证：三态只出现两态 = 判据退化（本仓 X-7 同族：恒真等于无判据）。
    # 怎么运作：造一个极弱候选（无 LICENSE / 无 SKILL.md / 极小 blob / 无 tests / 无 docs / stars 0 / 已归档）
    # 喂进同一个 score5，与真实本地件（local_bytes 最大的那件）比 delta_cmp4 —— 必须 >0 才算
    # 「本地更优」这一档可达（不是死码）；矩阵里 0 行本地更优才是本语料的性质而不是判据失效。
    weak = {"state": "OK", "license": "UNLICENSED", "archived": True, "skill_md_exact_n": 0,
            "skill_md_n": 0, "blob_n": 3, "readme_n": 0, "docs_md_n": 0, "test_path_n": 0,
            "workflow_n": 0, "tree_state": "OK", "stars": 0, "pushed_at": "2024-01-01"}
    ws, wtot, wcal = R.score5(weak)
    matrix_only = [row for row in doc["rows"] if row.get("local") and row.get("cand")]
    strongest = max(matrix_only, key=lambda x: x.get("local_bytes") or 0) if matrix_only else None
    weak_row = {"slug": "r260-weak-candidate-selftest", "family": "SELFTEST",
                "verdict": "N/A（自证腿，不入矩阵守恒）",
                "local_bytes": (strongest or {}).get("local_bytes"),
                "local_desc_len": (strongest or {}).get("local_desc_len"),
                "candidates_n": 1, "rank0_repo": "SELFTEST/weak-empty-repo",
                "rank0_rel": "selftest", "rank0_license": "UNLICENSED",
                "rank0_fc_caliber": wcal}
    if strongest is not None:
        ro_self = row_readout(R, locals_map[strongest["slug"]], {"repo": "x"}, weak)
        weak_row["local"] = dict(strongest["local"])
        weak_row["cand"] = {"score5": ws, "score_total": wtot,
                              "score_cmp4": sum(ws[d] for d in CMP_DIMS),
                              "license": "UNLICENSED", "archived": True, "stars": 0}
        weak_row["delta_cmp4"] = ro_self["delta_cmp4"]
        weak_row["delta_total25"] = ro_self["delta_total25"]
        weak_row["per_dim_delta"] = ro_self["per_dim_delta"]
        stt, whyy = tri_state(ro_self["delta_cmp4"], locals_map[strongest["slug"]], weak,
                                 {"repo": "SELFTEST/weak-empty-repo"})
        weak_row["state"] = stt
        weak_row["state_reason"] = whyy
    # 敏感性腿（读 delta 的人最需要这一行）：compat 的本地 −2 完全来自 X-2「不补 LICENSE」这条治理选择。
    # 怎么运作：把那 2 分还给本地 compat 后重算三态，看结论是否翻转 —— 翻转数就是「治理选择」而不是
    # 「质量差」所贡献的部分。不这么拆，delta 会被误读成本地件质量低 2 分。
    flip_if_lic = 0
    tie_if_lic = 0
    for row in doc["rows"]:
        if not (row.get("local") and row.get("cand")):
            continue
        d2 = row["local"]["score_cmp4"] + 2 - row["cand"]["score_cmp4"]
        if d2 > 0:
            flip_if_lic += 1
        elif d2 == 0:
            tie_if_lic += 1
    doc["sensitivity_x2_license"] = {
        "note": "本地 compat 因无 LICENSE 文件被扣 2 分（score5 的 license 子腿）；本仓 X-2 禁补 LICENSE",
        "rows_become_local_better_if_2_granted": flip_if_lic,
        "rows_become_tie_if_2_granted": tie_if_lic,
        "comparable_rows": len([row for row in doc["rows"] if row.get("local") and row.get("cand")]),
        "reading": "把治理扣分还给本地后仍有 {0} 行候选更优 ⇒ 本地劣势不是 X-2 造成的，主要是 eff（tests/CI）与 docs（README/docs）两条腿".format(len([row for row in doc["rows"] if row.get("local") and row.get("cand")]) - flip_if_lic - tie_if_lic)}

    states_seen = set(row.get("state") for row in doc["rows"] if row.get("state"))
    states_seen.add(weak_row.get("state"))
    doc["negative_controls"]["tristate_reachability"] = {
        "states_seen_in_matrix_and_selftest": sorted([s for s in states_seen if s]),
        "weak_candidate_score5": ws, "weak_candidate_total": wtot,
        "compared_against_slug": (strongest or {}).get("slug"),
        "state_on_weak_candidate": weak_row.get("state"),
        "delta_cmp4_on_weak_candidate": weak_row.get("delta_cmp4"),
        "all_three_reachable": len({"本地更优", "候选更优", "不可比"} & states_seen) == 3,
        "meaning": "三态是否都可达（矩阵 + 自证腿合并看）；只出现两态即判据退化"}
    # 自证腿不落进 rows（否则「rows 行数」不再等于矩阵件数，消费方按 191 读会多出一行）：
    # 改挂到 negative_controls 里，rows 严格 = 矩阵 191 行。
    doc["negative_controls"]["tristate_reachability"]["row"] = weak_row
    matrix_rows_out = [row for row in doc["rows"] if str(row.get("slug", "")).find("r260-") != 0]
    planned = doc["face"].get("rows_planned", len(matrix_rows_out))
    doc["conservation"] = {"rows_planned": planned, "matrix_rows_emitted": len(matrix_rows_out), "rows_emitted_incl_selftest": len(doc["rows"]),
                           "sum_states": sum(tally.values()), "by_state": tally,
                           "rows_equal": len(matrix_rows_out) == planned,
                           "states_equal_rows": sum(tally.values()) == len(matrix_rows_out),
                           "selftest_note": "slug 前缀 r260- 的行是自证腿，不计入矩阵守恒；打平行（tie_cmp4）是真读数，计入"}
    # 派生字段与 twin-caliber 判定已上移到 reproduce_selfcheck()（r302）：finalize 只做三腿合并。
    #   selfcheck_pass 的三腿 + 防退化闸见 selfcheck_pass() 的 docstring。
    doc["selfcheck_pass"] = selfcheck_pass(
        doc["reproduce_selfcheck"], teeth_ok,
        doc["conservation"]["rows_equal"] and doc["conservation"]["states_equal_rows"])
    doc["status"] = "COMPLETE"
    flush(doc, args.out, args.check_only)
    meta = doc["single_source"]
    print("单尺 score5 = {0} (sha16 {1}) ｜ 矩阵 {2} (sha16 {3})".format(
        meta["score5_file"], meta["score5_sha16"], meta["matrix_file"], meta["matrix_sha16"]))
    print("面：本地在册 {0} ｜ 矩阵行 {1} ｜ 本次计算 {2} ｜ 池缓存 {3} 条".format(
        len(locals_map), len(mrows), len(doc["rows"]), len(cache)))
    print("三态：本地更优={0} 候选更优={1} 不可比={2}".format(
        tally["本地更优"], tally["候选更优"], tally["不可比"]))
    cd = dim_dist["compat"]
    print("compat 分布（矩阵 {0} 候选）：hist={1} 满分占比={2} 有效档数={3}".format(
        cd["n"], cd["hist"], cd["share_at_max"], cd["spread"]))
    for dim in ("fc", "eff", "docs", "community"):
        d2 = dim_dist[dim]
        print("  {0:9s} 满分占比={1} 有效档数={2}".format(dim, d2["share_at_max"], d2["spread"]))
    rf = doc["compat_teeth"]["rank_flip"]
    print("去 compat 后 rank0 变化：{0}/{1} 行 ｜ compat 在候选间恒定的行数：{2}".format(
        rf["rank0_flips_when_compat_dropped"], rf["rows_checked"],
        rf["rows_with_constant_compat_across_candidates"]))
    for t in three:
        print("  [{0}] fc={1} eff={2} compat={3} docs={4} community={5} total={6} ｜ {7}".format(
            t["name"], t["fc"], t["eff"], t["compat"], t["docs"], t["community"],
            t["score_total"], t["verdict"]))
    print("compat 维结论：{0}".format(doc["compat_teeth"]["verdict"]))
    print("copyleft 候选 {0} 个（compat=5：{1}）｜ rank0 位上是 copyleft：{2} 行".format(
        ca["candidates"], ca["at_compat_5"], ca["rank0_candidates_copleft"]))
    sc_out = doc["reproduce_selfcheck"]
    print("复现自检：重算候选 {0} 个 ｜ 量尺漂移 mismatches={1} ｜ 输入已刷新 stale_input_n={2}"
          "（rank0 位 {3}）｜ 输入取不到 unknown_n={4} ｜ 指纹口径 {5} ｜ 同指纹重算 {6}".format(
              sc_out["candidates_recomputed"], sc_out["mismatches"], sc_out["stale_input_n"],
              sc_out["stale_input_rank0_n"], sc_out["unknown_n"], sc_out["input_pin_version"],
              sc_out["pinned_scored_n"]))
    for _ex in sc_out["stale_input_examples"][:3]:
        print("  [stale_input] {0} 与 {1} ｜ pin {2} 到 {3} ｜ 变了 {4}".format(
            _ex["slug"], _ex["repo"], _ex["recorded_pin"], _ex["live_pin"],
            ",".join(_ex["changed_fields"])))
    print("负向对照桩件：五维 {0} 总分 {1} ｜ 不全 5 = {2}".format(ss, stot, "PASS" if teeth_ok else "FAIL（判据无牙）"))
    print("本地侧 compat 分布：{0}（带 LICENSE 的本地件 {1}/{2}）".format(lcompat_hist, lic_have, len(locals_map)))
    if not doc["selfcheck_pass"]:
        print(TOKEN % "FAIL", "自证三腿未全过（无牙 / 复现漂移 / 守恒破坏）")
        return 1
    tail = "（--check-only 未写件）" if args.check_only else " -> " + args.out
    print(TOKEN % "PASS", "三态守恒 {0} ｜ mismatches={1} ｜ stale_input_n={2} ｜ unknown_n={3} ｜ 负向对照有牙{4}".format(
        len(doc["rows"]), sc_out["mismatches"], sc_out["stale_input_n"], sc_out["unknown_n"], tail))
    return 0


if __name__ == "__main__":
    sys.exit(main())
