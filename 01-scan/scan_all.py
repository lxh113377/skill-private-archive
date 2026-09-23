#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""自建 skill 范围裁定 + 四维扫描。

--stage scope : 阶段0 三源交叉裁定自建清单
--stage scan  : 阶段1 四维扫描（体积/触发/死链弃用/同族聚类）

默认 dry-run（只打印摘要），加 --apply 才写盘。
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys
from collections import OrderedDict

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "05-exec"))
from _lib import force_utf8_stdout, load_json  # noqa: E402

force_utf8_stdout()

GS = r"D:\global_skills"
REG_DIR = r"C:\Users\37533\Desktop\workspace\焚诀\skill\registry"
IDX = os.path.join(REG_DIR, "unified-skills-index.json")
POC = os.path.join(REG_DIR, "platform-oc.json")  # ⚠️ 2026-09-21 OC 退役后该文件已被删除（下方走在役端回落）
MANIFEST = os.path.join(REG_DIR, "disk_manifest.json")
WS = r"c:\Users\37533\Desktop\workspace\自建skill优化"
SCOPE_DIR = os.path.join(WS, "00-scope")
SCAN_DIR = os.path.join(WS, "01-scan")

SKIP_DIRS = {"_temp", "_trash", ".git", ".hermes", "hooks", "_my-skills", "__pycache__", "_bak"}

# 自建族前缀（命名域口径 + 用户澄清列举的族）
SELF_PREFIX = (
    "A-", "fenjue-", "skill-", "local-", "story-", "chaoshi-", "ican-", "windows-",
    "openclaw-", "9b-", "c-cleanup", "sq-", "data-layer-", "audit-runner", "bigfile-split",
    "wps-", "wechat-", "workflow-", "wb-git-", "workbuddy-", "prompt-", "utf8-",
    "shell-encoding", "embedding-index", "oc-dispatch", "static-site", "hermes-installer",
    "cloudbase-webapp", "vp-perspective", "taskflow", "天眼一下", "dogfood", "multi-search",
    "meeting-intelligence", "research-documentation", "spec-to-implementation",
    "knowledge-capture", "first-principles", "hook-analyzer", "install-skill-dependency",
    "report-generator", "cross-platform-", "skills-security-check", "code-review",
    "debugging-fixing", "prompt-consolidation",
)

# 白名单：虽有市场分发元数据，但属「在用且需自行维护」→ 豁免市场信号，判为自建
# 理由（2026-09-14）：local-* 的 meta.json 带 download_count/author/download_url（Intel 分发样例包格式），
#   但其身上的 4 个 P1 问题（OCR 三方触发冲突、vram 文档与实现漂移、meta description 退化为 "|"、
#   ffmpeg 依赖未声明）均需自行维护 → 归档为市场件会导致这些维护项失管。
KEEP_SELF = {"local-asr", "local-computer-use", "local-realtime-translator",
             "local-tts", "local-txt2img"}

# 市场/上游件人工判定（2026-09-14 阶段2 批4 精读结论）
# 收录原则：自动信号覆盖不到，但精读有硬证据（零中文/零个人路径/依附官方工具链/openclaw 运行时件）
# ⚠️ 反例（2026-09-14 实测）：`metadata.openclaw` 只表示「与 openclaw 兼容」，story-* 11 个
#    全部带该字段却是明确自建（中文正文+个人项目痕迹）→ 不可作为独立排除信号，故不在此列
MARKET_MANUAL = {"electron", "skill-install", "taskflow", "taskflow-inbox-triage"}

SEMVER_RE = re.compile(r"^\d+\.\d+")
VER_IN_MSG_RE = re.compile(r"V\d+\.\d+")
# 弃用平台口径（2026-09-14 用户裁决更新）：
#   CC(Claude Code) 弃用 2026-09-08 / QW·QoderWork 卸载 2026-08-01 / QClaw 弃用
#   ⚠️ HM(Hermes) 已于 2026-09-14 由用户确认「又下回来了」→ 移除弃用名单，HM 相关引用不再计为过时
DEPRECATED_PLATFORMS = ("QoderWork", r"\bQW\b", "QClaw", "Claude Code", r"\bCC\b")
# 2026-09-23 审计：原 "QW "（尾随空格）在 "OC/WB/QW/TC" 等语境漏报 → 改 \bQW\b；
# \bCC\b 在主循环单独用区分大小写匹配（小写 cc=抄送/变量名会误伤）


def git_first_adds():
    """一次性取全库 A 提交 → {rel_path: 'date|subject'}，保留首次出现。"""
    out = {}
    try:
        p = subprocess.run(
            ["git", "-c", "core.quotepath=off", "-C", GS, "log", "--diff-filter=A", "--reverse",
             "--format=@@%ad|%s", "--date=short", "--name-only"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
    except Exception as e:
        print(f"[warn] git 调用失败: {e}")
        return out
    if p.returncode != 0:
        print(f"[warn] git rc={p.returncode}: {p.stderr[:200]}")
        return out
    cur = None
    for line in p.stdout.splitlines():
        if line.startswith("@@"):
            cur = line[2:]
            continue
        line = line.strip()
        if line and cur is not None and line not in out:
            out[line] = cur
    return out


def triage():
    idx = load_json(IDX)
    man = load_json(MANIFEST)
    reg = idx.get("skills", {})
    # 口径(2026-09-23修)：OC已退役，platform-oc.json即使存在也不再作为自建源；
    # 在役端 = wb/tc/codex/hm/zc 五端并集（前版漏zc，已补；oc仅提示不纳入）。
    uc_list = set()
    for _pf in ("platform-wb.json", "platform-tc.json", "platform-codex.json", "platform-hm.json", "platform-zc.json"):
        _pp = os.path.join(REG_DIR, _pf)
        if os.path.exists(_pp):
            try:
                uc_list |= set(load_json(_pp).get("user_created_skills", []))
            except Exception as _e:
                print(f"[warn] {_pf} 读取失败: {_e}")
    uc_src = "在役端 platform-*[wb/tc/codex/hm/zc]"
    if os.path.exists(POC):
        print("[warn] platform-oc.json 已退役，仅提示不纳入（磁盘存在，已忽略）")
    man_map = {s["name"]: s for s in man.get("skills", [])}

    dirs = sorted(d for d in os.listdir(GS)
                  if os.path.isdir(os.path.join(GS, d)) and d not in SKIP_DIRS)
    adds = git_first_adds()
    # 性能(2026-09-23)：一次性缓存各目录文件名，替代循环内重复os.listdir/stat（输出不变）。
    _ls = {}
    for _d in dirs:
        try:
            _ls[_d] = set(os.listdir(os.path.join(GS, _d)))
        except Exception:
            _ls[_d] = set()
    print(f"[info] 磁盘 {len(dirs)} | 注册表 {len(reg)} | {uc_src} 自建 {len(uc_list)} "
          f"| disk_manifest {len(man_map)} | git A 提交文件 {len(adds)}")

    rows, distortion = [], []
    for d in dirs:
        e = reg.get(d)
        m = man_map.get(d)
        reasons, score = [], 0

        # —— 第一阶段：硬排除市场/官方信号（命中即 EXCLUDE）——
        disk_src = (m or {}).get("source")
        hard = None
        if disk_src == "openclaw_plugin":
            hard = "disk:openclaw_plugin(插件市场包)"
        elif disk_src is None:
            reasons.append("disk:未登记(orphan,待人工)")
        lic = [f for f in _ls.get(d, ()) if f.upper().startswith("LICENSE")]
        if lic and not hard:
            hard = f"LICENSE:{lic[0]}(官方/市场包)"
        if ".skill-metadata.yaml" in _ls.get(d, ()) and not hard:
            hard = ".skill-metadata.yaml(官方元数据)"
        if (e or {}).get("source") == "skillhub" and not hard:
            hard = "source=skillhub(市场)"

        # —— 市场/上游件信号（2026-09-14 精读实证补充：无 LICENSE 的市场包同样落在 D:\global_skills）——
        if not hard and d not in KEEP_SELF:
            mk = None
            for cand in ("_meta.json", "meta.json"):
                if cand not in _ls.get(d, ()):
                    continue
                mp2 = os.path.join(GS, d, cand)
                try:
                    with open(mp2, "r", encoding="utf-8-sig") as _mf:
                        mj = json.load(_mf)
                except Exception as _me:
                    # fail-open 会把损坏的市场包当「无市场信号」漏排除 → 至少留痕（2026-09-23 审计）
                    print(f"[warn] {d}/{cand} 解析失败（按无市场信号处理）: {_me}")
                    continue
                # 口径(2026-09-23修)：与05-exec/user_created_audit.py对齐——
                # ①大小写归一（audit原大小写敏感会漏检）；②嵌套键也查（原只查顶层）；
                # ③补download_url系（厂商分包常见）。只认强市场键，`slug`仍排除防误伤。
                _stack, _ks = [mj], set()
                while _stack:
                    _cur = _stack.pop()
                    if isinstance(_cur, dict):
                        _ks |= {str(k).lower() for k in _cur.keys()}
                        _stack.extend(_cur.values())
                    elif isinstance(_cur, list):
                        _stack.extend(_cur)
                if _ks & {"ownerid", "publishedat", "download_count", "downloadcount",
                          "download_url", "downloadurl"}:
                    mk = f"{cand}:发布元数据(市场件)"
                    break
            if not mk and os.path.exists(os.path.join(GS, d, "evals", "evals.json")):
                mk = "evals/evals.json(官方评测件)"
            if not mk and os.path.isdir(os.path.join(GS, d, "evaluations")):
                mk = "evaluations/(官方评测件)"
            if not mk:
                sp0 = os.path.join(GS, d, "SKILL.md")
                if os.path.exists(sp0):
                    head0 = open(sp0, "r", encoding="utf-8-sig", errors="replace").read(1200)
                    fm0 = re.search(r"^name:\s*(\S+)", head0, re.M)
                    if fm0 and fm0.group(1).startswith("notion-") and fm0.group(1) != d:
                        mk = f"frontmatter name=`{fm0.group(1)}`≠目录名(notion 市场件)"
            if not mk and d in MARKET_MANUAL:
                mk = "精读人工判定:市场/上游件"
            if mk:
                hard = mk

        if hard:
            rows.append(OrderedDict([
                ("skill", d), ("conf", "EXCLUDE"), ("score", -100),
                ("reg_uc", (e or {}).get("user_created")), ("disk_src", disk_src),
                ("domain", (e or {}).get("domain")), ("version", (e or {}).get("version")),
                ("evidence", [hard]),
            ]))
            continue

        reasons.append("disk:global_skills(本地原生)")
        score += 2

        reg_uc = (e or {}).get("user_created")
        if d in uc_list:
            reasons.append("registry:user_created=true")
            score += 5
        elif reg_uc:
            reasons.append("unified:user_created=true")
            score += 4
        elif e is not None:
            reasons.append("registry:user_created=false(字段已失真,不计负分)")

        src = (e or {}).get("source")
        if src:
            reasons.append(f"source={src}")

        # 第四源：frontmatter 的 homepage（外部来源 = 市场包强信号）
        sp = os.path.join(GS, d, "SKILL.md")
        fm_home = None
        if os.path.exists(sp):
            with open(sp, "r", encoding="utf-8-sig", errors="replace") as fh:
                head = fh.read(1500)
            mt = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", head, re.S)
            if mt:
                for line in mt.group(1).splitlines():
                    if line.startswith("homepage:"):
                        fm_home = line.split(":", 1)[1].strip()
        if fm_home:
            reasons.append(f"homepage={fm_home}(外部来源)")
            score -= 3

        ver = (e or {}).get("version") or (m or {}).get("version")
        if ver and SEMVER_RE.match(str(ver)):
            reasons.append(f"version={ver}(semver)")
            score += 2
        elif ver == "community":
            reasons.append("version=community")

        prefix_hit = next((p for p in SELF_PREFIX if d.startswith(p)), None)
        if prefix_hit:
            reasons.append(f"命名域:{prefix_hit}*")
            score += 3

        ga = adds.get(f"{d}/SKILL.md")
        if ga:
            reasons.append(f"gitAdd={ga}")
            if VER_IN_MSG_RE.search(ga):
                reasons.append("git:版本化提交")
                score += 2
        else:
            reasons.append("gitAdd=无")

        conf = "HIGH" if score >= 6 else "MID" if score >= 3 else "LOW" if score >= 0 else "EXCLUDE"
        rows.append(OrderedDict([
            ("skill", d), ("conf", conf), ("score", score),
            ("reg_uc", reg_uc), ("disk_src", disk_src),
            ("domain", (e or {}).get("domain")), ("version", ver),
            ("evidence", reasons),
        ]))
        # 失真：命名域判自建，但注册表标 false
        if prefix_hit and d not in uc_list and reg_uc is False:
            distortion.append(OrderedDict([
                ("skill", d), ("prefix", prefix_hit),
                ("reg_user_created", reg_uc), ("reg_source", src),
                ("disk_source", disk_src), ("version", ver),
            ]))

    by_conf = {}
    for r in rows:
        by_conf.setdefault(r["conf"], []).append(r["skill"])
    for k in ("HIGH", "MID", "LOW", "EXCLUDE"):
        print(f"[conf] {k}: {len(by_conf.get(k, []))}")
    print(f"[distortion] 命名域自建但注册表 false: {len(distortion)}")

    md = ["# 自建 skill 清单（三源交叉裁定 · v2）", "",
          f"> 生成：scan_all.py --stage scope（2026-09-22 重出；基数 = 注册表 {len(reg)} 条 = 磁盘实测，焚诀 verify C1 全等）",
          "> 源：unified-skills-index.json + 在役端 platform-*.json（user_created_skills 并集）+ disk_manifest.json + 磁盘枚举 + git 首提交",
          "> ⚠️ 本版**取代 v1**（2026-09-14，169 条时代）。v1 已原样归档至 `archive/scope-v1-169-2026-09-14/`（历史留痕不改写）。",
          f"> 覆盖：磁盘 {len(dirs)} 个目录；已排除 `SKIP_DIRS`（`_my-skills` = 保护标记非任务型 skill、`hooks` 基建、`_trash`/`_temp`/`_bak`/`.git`/`.hermes`/`__pycache__`）→ 与注册表 151 条差 1（即 `_my-skills`）。",
          "> 打分（2026-09-23 与代码对齐，原文案 disk+1/LICENSE-3 等与实现不符）：disk global_skills +2 | registry user_created=true +5 "
          "| unified user_created=true +4 | 命名域自建族 +3 | semver +2 | git 版本化提交 +2 | user_created=false 不计分(失真字段) | homepage 外部来源 -3 "
          "| 市场硬排除命中即 EXCLUDE(-100)：LICENSE / .skill-metadata.yaml / source=skillhub / openclaw_plugin / 发布元数据(_meta.json 等) / 官方评测件",
          f"> 磁盘目录 {len(dirs)} → HIGH {len(by_conf.get('HIGH', []))} / MID {len(by_conf.get('MID', []))} "
          f"/ LOW {len(by_conf.get('LOW', []))} / EXCLUDE {len(by_conf.get('EXCLUDE', []))}", ""]
    for k in ("HIGH", "MID", "LOW", "EXCLUDE"):
        lst = by_conf.get(k, [])
        md.append(f"## {k}（{len(lst)}）")
        md.append("")
        if not lst:
            md.append("（无）")
            md.append("")
            continue
        md.append("| skill | 分数 | 注册表uc | disk源 | 版本 | 关键证据 |")
        md.append("|---|---|---|---|---|---|")
        for r in rows:
            if r["conf"] != k:
                continue
            ev = "; ".join(r["evidence"])
            if len(ev) > 160:
                ev = ev[:157] + "..."
            md.append(f"| `{r['skill']}` | {r['score']} | {r['reg_uc']} | {r['disk_src']} | "
                      f"{r['version']} | {ev} |")
        md.append("")

    dmd = ["# 注册表 user_created 标记失真条目", "",
           "> 判定：命名域属自建族（用户澄清口径）但 `unified-skills-index.json` 标 `user_created:false`",
           "> 处置（2026-09-22 修正）：`data-layer-consistency-fix` 已退役 → 改为「先判定是否**真失真**（无市场元数据 ≠ 自建，反证：`canvas-design` 为 Anthropic 市场件却无 `_meta.json`；且 `user_created` 取自 frontmatter 且缺省 false = **未标注**而非标错）→ 确认真失真才改 SKILL.md frontmatter → 跑 `build_registry.py` + `build_indexes.py --apply` + `verify_truth_consistency.py`」",
           f"> 共 {len(distortion)} 条", "",
           "| skill | 前缀 | 注册表uc | 注册表source | disk源 | 版本 |",
           "|---|---|---|---|---|---|"]
    for d0 in distortion:
        dmd.append(f"| `{d0['skill']}` | {d0['prefix']}* | {d0['reg_user_created']} | "
                   f"{d0['reg_source']} | {d0['disk_source']} | {d0['version']} |")

    if args.apply:
        os.makedirs(SCOPE_DIR, exist_ok=True)
        with open(os.path.join(SCOPE_DIR, "自建skill清单.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(md) + "\n")
        with open(os.path.join(SCOPE_DIR, "注册表失真条目.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(dmd) + "\n")
        with open(os.path.join(SCOPE_DIR, "scope_result.json"), "w", encoding="utf-8") as f:
            json.dump({"rows": rows, "distortion": distortion}, f, ensure_ascii=False, indent=1)
        print(f"[write] {SCOPE_DIR} 已写入 3 个文件")
    else:
        print("[dry-run] 未写盘（加 --apply 生效）")
        print("\n".join(md[:20]))


def scan():
    """阶段1：四维扫描（体积 / 触发 / 死链弃用 / 同族聚类）。"""
    scope_json = os.path.join(SCOPE_DIR, "scope_result.json")
    if not os.path.exists(scope_json):
        print("[error] 缺少 scope_result.json，先跑 --stage scope --apply")
        return 2
    data = load_json(scope_json)
    targets = [r["skill"] for r in data["rows"] if r["conf"] in ("HIGH", "MID")]
    print(f"[info] 扫描目标 {len(targets)} 个（HIGH+MID）")

    # 预建全库文件集合，供死链检测用（避免逐次 Test-Path）
    # 2026-09-23 审计：walk 剪枝 SKIP_DIRS——① .git/_trash 等不再进白名单（指向 _trash 的引用
    # 不再被误放行）；② .git 对象库数千文件不再无谓遍历
    all_files = set()
    for root, dirs_, files in os.walk(GS):
        dirs_[:] = [x for x in dirs_ if x not in SKIP_DIRS]
        for fn in files:
            all_files.add(os.path.relpath(os.path.join(root, fn), GS).replace("\\", "/"))
    all_dirs = set()
    for root, dirs_, _f in os.walk(GS):
        dirs_[:] = [x for x in dirs_ if x not in SKIP_DIRS]
        all_dirs |= {os.path.relpath(os.path.join(root, x), GS).replace("\\", "/") for x in dirs_}
    gm_files = set()
    for root, dirs_, files in os.walk(r"D:\global_memory"):
        dirs_[:] = [x for x in dirs_ if x not in SKIP_DIRS and x != "node_modules"]
        for fn in files:
            gm_files.add(os.path.relpath(os.path.join(root, fn), r"D:\global_memory")
                         .replace("\\", "/"))

    rows = []
    for name in targets:
        p = os.path.join(GS, name, "SKILL.md")
        if not os.path.exists(p):
            continue
        raw = open(p, "r", encoding="utf-8-sig", errors="replace").read()
        size_b = os.path.getsize(p)
        entries = os.listdir(os.path.join(GS, name))
        # 2026-09-23 审计：references 可能是同名**文件**（非目录）→ isdir 双重判断防 NotADirectoryError 中断全扫描
        has_refs = "references" in entries and os.path.isdir(os.path.join(GS, name, "references"))
        ref_cnt = len(os.listdir(os.path.join(GS, name, "references"))) if has_refs else 0

        # frontmatter
        fm = {}
        mt = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", raw, re.S)
        if mt:
            cur = None
            for line in mt.group(1).splitlines():
                m3 = re.match(r"^([A-Za-z_][\w\-]*):\s*(.*)$", line)
                if m3 and not line[:1].isspace():
                    cur = m3.group(1)
                    fm[cur] = m3.group(2).strip().lstrip("|").strip()
                elif cur and line[:1].isspace() and line.strip():
                    fm[cur] = (fm[cur] + " " + line.strip()).strip()
        desc = fm.get("description", "")
        trig = 1 if "触发词" in desc else 0

        # 死链：只校验「skill 内部引用」与「全局记忆绝对路径」两类可验证引用
        # （排除跨项目路径：小说项目/部署仓库/焚诀 eval 等，非 skill 死链）
        dead = []
        for m2 in re.finditer(r"`([A-Za-z0-9_\\\-./:一-鿿]+\.(?:md|py|ps1|json|yaml|yml|js|sh))`", raw):
            t = m2.group(1).replace("\\", "/")
            low = t.lower()
            if low.startswith(("references/", "scripts/", "templates/")):
                cand = os.path.join(name, t).replace("\\", "/")
                if cand in all_files or cand in all_dirs:
                    continue
                if any(f.endswith("/" + os.path.basename(t)) for f in all_files):
                    continue
                dead.append(t)
            elif low.startswith("d:/global_memory/"):
                # 2026-09-23 审计（P0-1/P0-2）：原字符类不含 `:` ⇒ 本分支永不可达（全局记忆绝对路径死链全漏报）；
                # 且原 t[3:] 切片留下 global_memory/ 前缀 ⇒ 修好可达性后会全量误报。现按前缀精确切片。
                rel = t[len("d:/global_memory/"):]
                if rel in gm_files or rel in all_files or rel in all_dirs:
                    continue
                if any(f.endswith("/" + os.path.basename(rel)) for f in gm_files):
                    continue
                dead.append(t)
            elif low.startswith("d:/global_skills/"):
                rel = t[len("d:/global_skills/"):]
                if rel in all_files or rel in all_dirs:
                    continue
                if any(f.endswith("/" + os.path.basename(rel)) for f in all_files):
                    continue
                dead.append(t)
        # 通配符引用死链（2026-09-22 第 10 轮补，遗留 #1）
        # 上一条正则的字符类不含 `*` 且要求以扩展名收尾 ⇒ `scripts/wf_*.ps1` 式引用整体漏检
        dead_wild = []
        for m2 in re.finditer(r"`((?:references|scripts|templates|assets)/[^`\s]*\*[^`\s]*)`", raw):
            pat = m2.group(1).replace("\\", "/")
            if glob.glob(os.path.join(GS, name, pat)):
                continue
            dead_wild.append(pat)
        # 判据修复（2026-09-22 第 10 轮）：原实现为 `d in raw`（子串匹配），
        # 而 DEPRECATED_PLATFORMS 含正则项 r"\bCC\b" ⇒ 该字面量永远匹配不到 ⇒ **CC 检测静默失效**
        # （实证：`openclaw-task-supervision:114` 写「OC/WB/CC/TC/HM/CX」却从未被标出）
        # 口径(2026-09-23修)：大小写不敏感（漏“claude code/ClaudeCode”变体）+ CC仍用\b护栏防误伤。
        # 2026-09-23 审计：CC 改为**区分大小写**匹配（IGNORECASE 会命中小写 cc=抄送/变量名，误报）
        dep = []
        for _d in DEPRECATED_PLATFORMS:
            if _d == r"\bCC\b":
                if re.search(_d, raw):
                    dep.append("CC")
            elif re.search(_d, raw, re.IGNORECASE):
                dep.append(_d.strip())

        rows.append(OrderedDict([
            ("skill", name),
            ("size_b", size_b), ("over_4kb", size_b > 4096),
            ("has_refs_dir", has_refs), ("ref_files", ref_cnt),
            ("desc_len", len(desc)), ("has_trigger_words", trig),
            ("desc_short", len(desc) < 40),
            ("has_version", "version" in fm), ("has_name", "name" in fm),
            ("dead_refs", sorted(set(dead))[:8]),
            ("dead_wildcards", sorted(set(dead_wild))[:8]),
            ("deprecated_platform_hits", sorted(set(dep))),
        ]))

    rows.sort(key=lambda r: -r["size_b"])
    md = ["# 四维扫描基线", "", f"> 目标 {len(rows)} 个（HIGH+MID 置信自建）", "",
          "## 体积维度（SKILL.md > 4KB）", "",
          "| skill | 字节 | 超4KB | references 文件数 |",
          "|---|---|---|---|"]
    for r in rows:
        if r["over_4kb"]:
            md.append(f"| `{r['skill']}` | {r['size_b']} | ✅ | {r['ref_files']} |")
    md += ["", "## 触发维度（description 过短 <40 字 = 触发描述弱）", "",
           "| skill | desc 长度 | 显式触发词段 | 有 version | 有 name |", "|---|---|---|---|---|"]
    for r in rows:
        if r["desc_short"] or not r["has_name"]:
            md.append(f"| `{r['skill']}` | {r['desc_len']} | {r['has_trigger_words']} | "
                      f"{r['has_version']} | {r['has_name']} |")
    md += ["", "## 死链 / 弃用平台名", "",
           "| skill | 死链候选 | 通配符死链候选 | 弃用平台名 |", "|---|---|---|---|"]
    for r in rows:
        if r["dead_refs"] or r["dead_wildcards"] or r["deprecated_platform_hits"]:
            md.append(f"| `{r['skill']}` | {', '.join(r['dead_refs']) or '-'} | "
                      f"{', '.join(r['dead_wildcards']) or '-'} | "
                      f"{', '.join(r['deprecated_platform_hits']) or '-'} |")

    if args.apply:
        os.makedirs(SCAN_DIR, exist_ok=True)
        with open(os.path.join(SCAN_DIR, "scan_result.json"), "w", encoding="utf-8") as f:
            # 2026-09-23 r9：改 {"rows":[...]} 包装与 scope_result.json 对齐；
            # ⚠️ 冻结件（09-22 版）仍为裸数组，下次 --apply 重出起才是新形态（README 已标注）
            json.dump({"rows": rows}, f, ensure_ascii=False, indent=1)
        with open(os.path.join(SCAN_DIR, "scan_report.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(md) + "\n")
        print(f"[write] {SCAN_DIR} 已写入 2 个文件")
    else:
        print("[dry-run] 未写盘")
    print(f"[stat] 超4KB {sum(1 for r in rows if r['over_4kb'])} | "
          f"无触发词 {sum(1 for r in rows if not r['has_trigger_words'])} | "
          f"有死链候选 {sum(1 for r in rows if r['dead_refs'])} | "
          f"有通配符死链候选 {sum(1 for r in rows if r['dead_wildcards'])} | "
          f"有弃用平台名 {sum(1 for r in rows if r['deprecated_platform_hits'])}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="自建skill范围裁定+四维扫描（默认dry-run，加--apply写盘；路径默认即现值，可覆盖）")
    ap.add_argument("--stage", choices=["scope", "scan"], default="scope")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--gs", default=GS, help="global_skills根（默认 D:\\global_skills）")
    ap.add_argument("--registry", default=REG_DIR, help="焚诀registry目录")
    ap.add_argument("--ws", default=WS, help="本工作区根")
    args = ap.parse_args()
    GS, REG_DIR, WS = args.gs, args.registry, args.ws
    IDX, POC, MANIFEST = os.path.join(REG_DIR, "unified-skills-index.json"), os.path.join(REG_DIR, "platform-oc.json"), os.path.join(REG_DIR, "disk_manifest.json")
    SCOPE_DIR, SCAN_DIR = os.path.join(WS, "00-scope"), os.path.join(WS, "01-scan")
    if args.stage == "scope":
        triage()
        sys.exit(0)
    sys.exit(scan() or 0)
