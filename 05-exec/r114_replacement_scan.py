# -*- coding: utf-8 -*-
r"""r114_replacement_scan.py — 需求2 字面缺口收口：为 182 件每一件建 3-5 个替代候选面。

存在理由（R113-7 一手，禁读成已完成）：
  r113 明写「需求2 部分达标：8/8 族有 3-5 候选，但每一个 skill 字面仍未覆盖（仅 39/182 进同源判定面）」
  ⇒ 上一轮只答了「同名的上游是不是我这份的旧版」（内容寻址），没有答「有没有别的更好」（异名替代）。

为什么不「一个 slug 打一条 query」（r114 一手，两次实测）：
  1) GitHub search 的 q 是 AND 语义：pdf manipulation cli stars:>500 五个词同时出现在
     name/description 的仓约等于 0 ⇒ 24 条查询里 11 条 total=0。0 命中会被读成「无替代」，
     而真相是查询写坏了（R247 同族：0 件不得读成无缺口）。
  2) search 配额 30 次/分；182 条 query 既不划算也无法保证召回。
  ⇒ 改池化两段式：先用 topic/范围查询建大候选池（每查询 100 条），
     再按「族 -> 技能关键词」两级过滤把池里的仓分派给每一件。族与归属都由规则复算，不手抄名单。

判据（四态，全部禁静默）：
  MATCHED         该件有 >=3 个候选，且候选与该件技能关键词相关（rel=skill）
  FAMILY_ONLY     该件只有族级候选（同族但技能词没打中）—— 如实降档，禁冒充 MATCHED
  NO_OS_CANDIDATE 该件所在族池非空但无任何候选命中其技能词 ⇒ 结论是「开源侧无对应件」，
                  这是答案不是失败；必须带 searched 证据（族池大小 + 试过的关键词）
  UNVERIFIED      取数面不可用（限流/网络/族零查询）⇒ 禁读成「无替代」
守恒断言：sum(四态) == 本地件数（X-7 自洽）。

反「取数失败销毁证据」（r112 cache_error 范式）：
  候选池缓存 _temp/r114_search_cache/；单条查询失败不覆写已成功缓存，只追加 cache_error 侧痕；
  整轮限流不足 ⇒ rc=2 且不写主产物（保留上一份好产物）。

用法：
  python 05-exec/r114_replacement_scan.py
  python 05-exec/r114_replacement_scan.py --offline
  python 05-exec/r114_replacement_scan.py --json <件>
退出码：0 出件且守恒 / 2 取数面不可用（零输入禁记绿）。
"""
import argparse
import io
import json
import os
import re
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BENCH = os.path.join(ROOT, "06-benchmark")
AUTHORITY = r"D:\global_skills"
GH = os.environ.get("GH_BIN") or r"C:\Program Files\GitHub CLI\gh.exe"
CACHE_DIR = os.path.join(ROOT, "_temp", "r114_search_cache")
MIN_RATE = 8
SEARCH_SLEEP = 2.2
CORE_SLEEP = 0.35
PER_PAGE = 100

POOL_QUERIES = [
    ("agent-skills-topic", "topic:agent-skills"),
    ("claude-skills-topic", "topic:claude-skills"),
    ("claude-code-topic", "topic:claude-code"),
    ("skills-topic", "topic:skills"),
    ("agent-skills-desc", "agent skills in:description stars:>1000"),
    ("anthropic-skills-desc", "anthropic skills in:description stars:>50"),
    ("mcp-server-desc", "mcp server in:description stars:>800"),
    ("skill-md-path", "skill.md in:path stars:>200"),
    ("ai-agent-desc", "ai agent skills in:description stars:>3000"),
    ("awesome-claude", "awesome claude in:name,description stars:>200"),
    ("automation-skill", "automation skill in:description stars:>500"),
    ("document-skills", "docx xlsx pdf pptx in:description stars:>30"),
    ("browser-automation", "browser automation in:description stars:>800"),
    ("design-ui-skills", "design ui skills in:description stars:>500"),
    # r211 补（R114-3 同族第二次实证，带取证）：原 14 条查询**没有任何一条能打到 blender 生态**。
    # 实测（_temp/r114_search_cache 的 14 份池件逐仓反查）：EL4CTEO/blender-skills ★462、
    # arjun988/blender-skills ★397、XliuXjianX/blender-production-skills ★268、
    # achimala/dream-loop ★1734、ahujasid/mcp-for-blender ★32230（push 2026-10-24）
    # ⇒ 5 个候选仓 **全部 NOT IN ANY POOL QUERY**；后果是 blender-pipeline 落 family=OTHER、
    # 族池 0、判 UNVERIFIED —— 即需求 2「每个 skill 3-5 个候选」对它字面未覆盖。
    # 禁读成「开源无对应件」（那是 NO_OS_CANDIDATE 的语义，必须有族池非空做前提）。
    ("blender-3d-skill", "blender skill in:name,description stars:>50"),
]

FAMILIES = [
    ("a-meta", "A-族：记忆/交接/技能治理/编排",
     r"skill|agent|memory|context|prompt|workflow|orchestrat|plugin|harness|framework|registry|claude|anthropic",
     r"^a-(memory|get-memory|project|skill|prompt|dynamic|ask|java)|fenjue-|^vp-perspective|^_my-skills|^天眼|^workflow-preflight|^no-manual-steps"),
    ("office", "文档办公族：docx/xlsx/pdf/ppt/办公自动化",
     r"docx|xlsx|office|pdf|spreadsheet|presentation|pptx|slide|word|excel|document",
     r"docx|xlsx|^pdf|nano-pdf|ppt|slides|office|spreadsheet|presentation|html-to-docx|internal-comms|doc-coauthoring"),
    ("frontend", "前端/UI/设计族",
     r"frontend|front-end|ui|ux|design|figma|shadcn|react|css|tailwind|component|theme|brand|canvas|diagram|slide",
     r"frontend|ui-ux|shadcn|figma|brand-guidel|canvas-design|theme-factory|web-design|design-guideline|react-best|static-site|diagram-maker|html-ppt"),
    ("browser", "浏览器/桌面自动化族",
     r"browser|chrome|cdp|playwright|selenium|electron|automation|screenshot|scraping|crawl",
     r"agent-browser|browser-cdp|browser-voice|electron|gstack|computer-use|dogfood|screenshot|web-access|discover-agent-cli"),
    ("quality", "调试/测试/评审/计划族",
     r"test|debug|review|audit|lint|security|refactor|ci|quality|verif|plan|spec|brainstorm|skill|agent",
     r"debug|testing|test-driven|verification-before|code-review|security-audit|refactor|scope-creep|commit-archaeolog|ci-pipeline|audit-runner|^spike|grill-me|brainstorming|writing-plans|executing|spec-to-impl|python-debugpy|node-inspect|openclaw|oc-dispatch|taskflow"),
    ("media", "视频/音频/图像/图表族",
     r"video|audio|image|tts|speech|media|render|animation|chart|visual|ocr|whisper|diffusion|gpt-image|seedream|seedance",
     r"video|audio|tts|asr|whisper|hyperframes|gsap|seedance|seedream|mediakit|img2img|txt2img|ocr|mineru|algorithmic-art|hook-analyzer|report-generator|chart-visualization|data-visualization|data-analysis|ai-video|story-cover"),
    ("local-ai", "本地 AI 能力族（Intel AIPC / 离线模型）",
     r"local|offline|openvino|onnx|npu|whisper|ollama|llama|aipc|intel",
     r"^local-|hermes-installer|pixelle-api|9b-light"),
    ("cloud", "云平台/部署/数据库族",
     r"cloud|deploy|serverless|database|pages|functions|cdn|docker|kubernetes|tencent|cloudflare|d1|sql",
     r"cloudbase|byted-|ican-deploy|ican-frontend|chaoshi|wps-knowledge|workbuddy|docker-e2e|sqlalchemy|rag-eval"),
    ("im", "IM/协同办公族（钉钉/微信/Notion/知识）",
     r"dingtalk|wechat|notion|slack|discord|telegram|feishu|lark|calendar|mail|knowledge|meeting|note",
     r"dingtalk|wechat|notion|meeting-intelligence|knowledge-capture|research-documentation|knowledge"),
    ("story", "网文/创意写作族",
     r"novel|story|writing|obsidian|markdown|creative|fiction|canvas",
     r"^story|^obsidian|json-canvas|elon-musk|first-principles|consulting-analysis|prompt-consolidation|prompt-system|defuddle|grill-me"),
    ("win", "Windows 本机运维族",
     r"windows|powershell|win32|cli|terminal|cleanup|disk|encoding|shell",
     r"win-|windows-|c-cleanup|sq-cleanmgr|shell-encoding|utf8-encoding|^screenshot|wechat-voice"),
    ("knowledge", "MCP/工程基建/发现族",
     r"mcp|builder|github|rag|agent|skill|tool|framework|cli",
     r"rag-eval|mcporter|mcp-builder|^github|^oracle|coding-agent|find-skills|bigfile-split|discover-agent-cli|codebuddy-chat-web|healthcare|cross-platform"),
    ("3d", "3D/Blender 生产族（建模/渲染/装配/交付）",
     r"blender|\bbpy\b|gltf|\b3d\b|mesh|sculpt|cycles|optix|render",
     # 追加在表尾 = 最低冲击位：classify() 取**首个** spat 命中，实测前置 12 族的 spat
     # 均不匹配 blender-pipeline ⇒ 本族只接它一件（全 191 件里正则命中本族 spat 的也只有它）。
     r"^blender-|blendermcp|blender-modeling"),
]


def gh(args, timeout=120):
    try:
        p = subprocess.run([GH] + args, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout)
    except Exception as exc:  # noqa: BLE001
        return None, "exc:%r" % (exc,)
    if p.returncode != 0:
        return None, "rc=%d:%s" % (p.returncode, (p.stderr or "").strip()[:180])
    return p.stdout, None


def rate_search():
    out, err = gh(["api", "rate_limit"])
    if err:
        return None, err
    try:
        return int(json.loads(out)["resources"]["search"]["remaining"]), None
    except Exception as exc:  # noqa: BLE001
        return None, "parse:%r" % (exc,)


def key_of(s):
    return re.sub(r"[^A-Za-z0-9]+", "_", s)[:90]


POOL_PACK = os.path.join(BENCH, "pool_cache_r217.json")


def load_cache(cache_dir=None, pack_path=None, prov=None):
    """候选池缓存 = 入库包（POOL_PACK）+ 活散件，且**散件覆盖包**。

    存在理由（r217，解 R213-1）：本函数原先只读 _temp/r114_search_cache/ —— 那目录被 gitignore
    且并行会话按扩展名清过场（R189-2 实测 212 件），清场当天 --offline 的第 ⑥ 段会判红。
    池散件 414 个 > cache_file_max=200 ⇒ 不能整目录入库；改由 r217_pool_pack.py 打成单件
    （762,502B < any_file_max=1,048,576B）入 06-benchmark，这里在内存里合并读，不回写散件
    ⇒ 不新增 cache_file_max 压力。
    合并方向 = 散件后写覆盖包 ⇒ 联网跑出的新结果永远优先，包陈旧不会造成假绿；
    包不可读或缺件时仅用散件（= 回到旧行为），不报错也不静默造命中。
    """
    cache_dir = cache_dir or CACHE_DIR
    pack_path = POOL_PACK if pack_path is None else pack_path
    d = {}
    if prov is None:
        prov = {}
    prov.setdefault("pack_path", os.path.relpath(pack_path, ROOT).replace(os.sep, "/") if pack_path else None)
    prov.setdefault("pack_entries", 0)
    prov.setdefault("pack_generated_at", None)
    prov.setdefault("loose_files", 0)
    prov.setdefault("loose_dir_exists", os.path.isdir(cache_dir))
    if pack_path and os.path.isfile(pack_path):
        try:
            _pk = json.load(io.open(pack_path, encoding="utf-8-sig", errors="replace"))
            if isinstance(_pk, dict) and isinstance(_pk.get("entries"), dict):
                d.update(_pk["entries"])
                # 新鲜度随读数同列（r120 trace_face 同族范式）：包陈旧而散件被清时，
                # 离线跑仍会成功出件，但读的是旧池 —— 那一刻必须看得见出处，不得静默。
                prov["pack_entries"] = len(_pk["entries"])
                prov["pack_generated_at"] = _pk.get("generated_at")
        except Exception:  # noqa: BLE001 - 包坏了退回散件面，不把整段判死
            pass
    if not os.path.isdir(cache_dir):
        return d
    for f in sorted(os.listdir(cache_dir)):
        if f.endswith(".json"):
            prov["loose_files"] += 1
            try:
                d[f[:-5]] = json.load(io.open(os.path.join(cache_dir, f), encoding="utf-8"))
            except Exception:  # noqa: BLE001 - 坏缓存条目跳过（按 miss 处理，不静默当命中）
                continue
    return d


_CACHE_LOCK = threading.Lock()


def save_cache(key, doc):
    """只写成功结果：调用方保证失败不进来（cache_error 单件不覆写）。

    加锁（r114 一手）：测量阶段改成线程池后，两个线程同时 os.replace 同名临时件
    会把对方半写的文件顶掉。锁的是「写这一个 key」，不是整轮。
    """
    os.makedirs(CACHE_DIR, exist_ok=True)
    stamp = "%d_%d" % (os.getpid(), threading.get_ident())
    tmp = os.path.join(CACHE_DIR, key + ".%s.tmp" % stamp)
    with _CACHE_LOCK:
        with io.open(tmp, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(doc, fh, ensure_ascii=False, indent=1)
        os.replace(tmp, os.path.join(CACHE_DIR, key + ".json"))


def row_of(it):
    return {"full_name": it.get("full_name") or "",
            "stars": it.get("stargazers_count") or 0,
            "forks": it.get("forks_count") or 0,
            "pushed_at": (it.get("pushed_at") or "")[:10],
            "created_at": (it.get("created_at") or "")[:10],
            "archived": bool(it.get("archived")),
            "license": ((it.get("license") or {}).get("spdx_id") or "UNLICENSED"),
            "open_issues": it.get("open_issues_count") or 0,
            "description": (it.get("description") or "")[:240],
            "topics": (it.get("topics") or [])[:12]}


_STATS_LOCK = threading.Lock()


def bump(stats, key, n=1):
    """线程安全的计数器自增（r114 一手：并行测量下裸 += 会丢计数，令 api_calls 报少）。"""
    with _STATS_LOCK:
        stats[key] = stats.get(key, 0) + n


def note_error(stats, item):
    with _STATS_LOCK:
        stats["errors"].append(item)


def search(q, cache, offline, stats):
    key = "q__" + key_of(q)
    if key in cache:
        stats["cache_hits"] += 1
        return cache[key]
    if offline:
        stats["cache_miss"] += 1
        return {"q": q, "state": "SKIPPED_OFFLINE", "rows": []}
    out, err = gh(["api", "-X", "GET", "search/repositories",
                   "-f", "q=" + q, "-f", "sort=stars", "-f", "order=desc",
                   "-f", "per_page=%d" % PER_PAGE])
    bump(stats, "api_calls")
    time.sleep(SEARCH_SLEEP)
    if err:
        note_error(stats, {"q": q, "error": err})
        return {"q": q, "state": "UNVERIFIED", "error": err, "rows": []}
    try:
        d = json.loads(out)
    except ValueError as exc:
        note_error(stats, {"q": q, "error": "json:%r" % (exc,)})
        return {"q": q, "state": "UNVERIFIED", "error": "json:%r" % (exc,), "rows": []}
    rows = []
    for it in d.get("items") or []:
        r = row_of(it)
        if "/" in r["full_name"]:
            rows.append(r)
    doc = {"q": q, "state": "OK", "total": d.get("total_count"), "rows": rows,
           "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    save_cache(key, doc)
    return doc


def tree_counts(paths):
    """树形态计数（纯函数，离线可验）。

    抽出理由（r218）：这些计数原先埋在 measure_repo 的 gh 调用之后 ⇒ 唯一验证方式是联网重测 243 仓，
    于是「严格口径」这一尺子写完就没人能证它算得对（本仓 X-18：判据写完不当场跑 = 无效）。
    纯函数化后可直接喂合成路径自证，与 r211_fc_caliber 的三条样本路径对账。

    口径（R211-9）：
      skill_md_n        = 旧口径 endswith("skill.md") —— 会把 docs/agent-skill.md、
                          distribution/.../create-skill.md、BOOTSTRAP_SKILL.md 计入（高估）；
      skill_md_exact_n  = 严格口径：路径末段正是 skill.md；
      skill_md_ghost_n  = 两者之差 = 被旧口径多计的非技能入口。
    旧口径**保留不动**：它是 C1 硬分桶前置（r116 / r125 都读），改它即作废全部历史候选面。
    """
    low = [p.lower() for p in (paths or [])]
    return {
        "skill_md_n": sum(1 for x in low if x.endswith("skill.md")),
        "skill_md_exact_n": sum(1 for x in low if x.rsplit("/", 1)[-1] == "skill.md"),
        "skill_md_ghost_n": (sum(1 for x in low if x.endswith("skill.md"))
                             - sum(1 for x in low if x.rsplit("/", 1)[-1] == "skill.md")),
        "workflow_n": sum(1 for x in low
                          if x.startswith(".github/workflows/")
                          and (x.endswith(".yml") or x.endswith(".yaml"))),
        "test_path_n": sum(1 for x in low if re.search(r"(^|/)(tests?|spec|__tests__)/", x)),
        "readme_n": sum(1 for x in low if re.match(r"(^|/)readme(\.md|\.rst|\.txt)?$", x)),
        "docs_md_n": sum(1 for x in low if x.startswith("docs/") and x.endswith(".md")),
    }


def measure_repo(full, cache, offline, stats, remeasure=False):
    """仓元数据 + 树形态；remeasure=True 时**跳过该仓缓存**重取（严格口径字段靠它补）。"""
    key = "repo__" + key_of(full)
    if not remeasure and key in cache:
        stats["cache_hits"] += 1
        return cache[key]
    if offline:
        stats["cache_miss"] += 1
        return {"state": "SKIPPED_OFFLINE"}
    out, err = gh(["api", "repos/" + full])
    bump(stats, "api_calls")
    time.sleep(CORE_SLEEP)
    if err:
        note_error(stats, {"repo": full, "step": "meta", "error": err})
        return {"state": "UNVERIFIED", "error": err}
    try:
        d = json.loads(out)
    except ValueError as exc:
        note_error(stats, {"repo": full, "step": "meta", "error": "json:%r" % (exc,)})
        return {"state": "UNVERIFIED", "error": "json:%r" % (exc,)}
    doc = {"state": "OK",
           "stars": d.get("stargazers_count") or 0,
           "forks": d.get("forks_count") or 0,
           "pushed_at": (d.get("pushed_at") or "")[:10],
           "created_at": (d.get("created_at") or "")[:10],
           "archived": bool(d.get("archived")),
           "license": ((d.get("license") or {}).get("spdx_id") or "UNLICENSED"),
           "open_issues": d.get("open_issues_count") or 0,
           "description": (d.get("description") or "")[:240],
           "topics": d.get("topics") or [],
           "default_branch": d.get("default_branch") or "main",
           "homepage": (d.get("homepage") or "")[:160]}
    br = doc["default_branch"]
    tout, terr = gh(["api", "repos/%s/git/trees/%s?recursive=1" % (full, br)], timeout=180)
    bump(stats, "api_calls")
    time.sleep(CORE_SLEEP)
    if terr:
        doc["tree_state"] = "UNAVAILABLE"
        doc["tree_error"] = terr
        for k in ("skill_md_n", "workflow_n", "test_path_n", "readme_n", "docs_md_n"):
            doc[k] = None
    else:
        try:
            t = json.loads(tout)
        except ValueError as exc:
            doc["tree_state"] = "UNAVAILABLE"
            doc["tree_error"] = "json:%r" % (exc,)
            for k in ("skill_md_n", "workflow_n", "test_path_n", "readme_n", "docs_md_n"):
                doc[k] = None
        else:
            paths = [x.get("path") or "" for x in (t.get("tree") or [])
                     if x.get("type") == "blob"]
            doc["tree_state"] = "OK"
            doc["tree_truncated"] = bool(t.get("truncated"))
            doc["blob_n"] = len(paths)
            # R211-9（r218）：口径计数全部走 tree_counts() 纯函数（双口径同列的说明在该函数 docstring）。
            # 旧口径 skill_md_n 保留不动 = C1 硬分桶前置（r116 / r125 读它），切判据须另行单独裁。
            doc.update(tree_counts(paths))
    save_cache(key, doc)
    return doc


def score5(m):
    """五维锚定分（各 0-5，合计 25）。每维锚点可复算，不凭印象。

    fc 功能完整性   SKILL.md 件数分档 + 无 SKILL.md 时按 blob 规模
    eff 运行效率    有 tests 与 workflows 为可自动化验证代理（少人工往返）
    compat 兼容性   license 明确 + 非 archived + 有 SKILL.md 约定
    docs 文档完善   根 README + docs/*.md 规模
    community 社区  stars 对数档 + 最近推送新鲜度
    """
    s = {}
    # r225：fc / compat 两维改用**严格口径**的 SKILL.md 件数（skill_md_exact_n），
    # 旧口径 skill_md_n 仅作缺字段时的回退（池缓存旧件没有 exact 字段）。
    # 为什么必须换：旧口径 endswith("skill.md") 会把 docs/…/xxx-skill.md 这类**文档**计成技能入口，
    # 于是「功能完整性」这个对外分数能被一篇介绍文章刷高 —— 本轮实测 937 个候选里有 1 例
    # （Snailclimb/JavaGuide：prod=1 / exact=0，那唯一命中是一篇 drawio-chart Skill 的发布文章），
    # 它因此拿到 fc=2 并成为 A-java-problem 的 rank0 候选。
    # ⚠️ 边界：本改动只修**五维评分**的量尺，不改迁移方案 §4 的 C1 判据（那里写的是 skill_md_n > 0，
    # 属对用户的验收承诺，改它须单独裁定并留 R241 校正注）—— 两件事不夹带。
    sm = m.get("skill_md_exact_n")
    # fc_caliber 不能放进 s：score5 末尾是 sum(s.values()) 算五维总分，
    # 混入字符串会直接把总分算炸（r225 首版就这么炸的，TypeError 当场暴露）。
    # 放到调用方可见的地方：矩阵行 candidates[].fc_caliber（见 main 里取用点）。
    fc_caliber = "legacy_fallback" if sm is None else "strict"
    if sm is None:
        sm = m.get("skill_md_n")
    if sm is None:
        s["fc"] = 0
    elif sm == 0:
        s["fc"] = 1 if (m.get("blob_n") or 0) > 50 else 0
    elif sm <= 2:
        s["fc"] = 2
    elif sm <= 10:
        s["fc"] = 3
    elif sm <= 100:
        s["fc"] = 4
    else:
        s["fc"] = 5
    tn = m.get("test_path_n") or 0
    wn = m.get("workflow_n") or 0
    s["eff"] = min(5, (min(3, 1 + (tn > 20) + (tn > 200)) if tn else 0)
                   + (min(2, 1 + (wn > 3)) if wn else 0))
    s["compat"] = min(5, (2 if (m.get("license") or "UNLICENSED") != "UNLICENSED" else 0)
                      + (0 if m.get("archived") else 1) + (2 if sm else 0))
    rn = m.get("readme_n") or 0
    dn = m.get("docs_md_n") or 0
    s["docs"] = min(5, (2 if rn else 0) + (1 if dn > 5 else 0)
                    + (1 if dn > 40 else 0) + (1 if m.get("tree_state") == "OK" else 0))
    st = m.get("stars") or 0
    s["community"] = min(5, sum(1 for th in (100, 1000, 10000, 50000) if st >= th)
                         + (1 if (m.get("pushed_at") or "") >= "2026-07-01" else 0))
    return s, sum(s.values()), fc_caliber


def classify(slug, desc):
    hay = (slug + " " + (desc or "")).lower()
    for fid, name, fpat, spat in FAMILIES:
        if re.search(spat, hay):
            return fid
    return "OTHER"


STOP = {"the", "and", "for", "with", "skill", "skills", "agent", "agents", "a", "an", "of",
        "to", "in", "on", "by", "my", "self", "web", "based", "tool", "cli", "api"}
SYNONYM = {
    "docx": "docx|word|document", "xlsx": "xlsx|excel|spreadsheet",
    "pdf": "pdf", "ppt": "ppt|slide|presentation|deck", "pptx": "pptx|powerpoint|slide",
    "tts": "tts|text-to-speech|speech|voice", "asr": "asr|whisper|transcri|speech-to-text",
    "ocr": "ocr|text-recognition|tesseract", "memory": "memory|context|remember",
    "handoff": "handoff|memory|context|session", "npu": "npu|openvino|intel",
    "vram": "vram|gpu|memory", "browser": "browser|chrome|playwright|cdp",
    "cdp": "cdp|chrome|devtools", "git": "git|commit|version-control",
    "test": "test|pytest|spec", "review": "review|lint|audit",
    "notion": "notion", "obsidian": "obsidian", "dingtalk": "dingtalk|dingding",
    "wechat": "wechat|weixin", "figma": "figma", "shadcn": "shadcn|ui-component",
    "gsap": "gsap|animation", "mcp": "mcp|model-context-protocol", "rag": "rag|retrieval",
    "hyperframes": "hyperframes|video|composition", "seedance": "seedance|video",
    "seedream": "seedream|image", "whisper": "whisper|asr|speech-to-text",
}


def build_tokens(slug, desc):
    """从 slug + 英文描述取**候选**判别词（未过滤），返回 [(token, 来源)]。

    只取英文词：本地 179/182 描述含中文，中文词打不中英文仓描述（r114 一手）。
    来源标 'slug' / 'desc'，供 df 过滤区别对待 —— slug 词是本件身份，
    desc 词是补充上下文，前者比后者更该保留。
    """
    out = []
    for part in re.split(r"[-_\s]+", slug.lower()):
        if len(part) >= 3 and part not in STOP:
            out.append((SYNONYM.get(part, re.escape(part)), "slug"))
    eng = re.findall(r"[A-Za-z][A-Za-z0-9+#.]{2,}", desc or "")
    for w in eng:
        lw = w.lower().strip(".")
        if len(lw) >= 4 and lw not in STOP and not lw.isdigit():
            out.append((re.escape(lw), "desc"))
    uniq, seen = [], set()
    for t, src in out:
        if t in seen:
            continue
        seen.add(t)
        uniq.append((t, src))
    return uniq


def df_filter(cands, toks, max_df=0.35):
    """按池内文档频率剔除无鉴别力的词（r105/r111 教训的**正确用法**）。

    r105 词面尺 / r111 BGE 尺的失败是把「相似度」当**结论**；本处只把 df 当
    **过滤器**：一个词若出现在 >max_df 比例的池内仓描述里（如 get/ask/agent），
    它对「这仓是不是这件 skill 的替代」没有鉴别力，剔除后重算；
    slug 来源的词放宽到 0.80（身份词，即使常见也代表本件本身）。
    被剔除的词落进产物 dropped_tokens，禁静默丢。
    """
    pool_n = max(1, len(cands))
    hays = [" ".join([c.get("full_name") or "", c.get("description") or "",
                      " ".join(c.get("topics") or [])]) for c in cands]
    kept, dropped = [], []
    for t, src in toks:
        try:
            cre = re.compile(word_bound(t), re.I)
        except re.error:
            continue
        hits = sum(1 for h in hays if cre.search(h))
        df = hits / float(pool_n)
        if df > max_df and src == "desc":
            dropped.append({"token": t, "df": round(df, 3), "why": "desc 词过泛"})
        elif df > 0.80 and src == "slug":
            dropped.append({"token": t, "df": round(df, 3), "why": "slug 词在池内无鉴别力"})
        else:
            kept.append(t)
    return kept, dropped


def word_bound(pattern):
    """给正则片段加 ASCII 词边界（r114 一手：不加边界时 ask 会命中 t-ask-s / multi-task）。

    'ask' 这类短词在英文语料里几乎总是**别的词的子串**；无边界匹配把
    「任务管理仓」判成「提问 skill 的替代」，正是 r105 词面尺被证伪的同一个坑
    （把「出现过这个词」当成「是同一件事」）。加 \b 后只认整词。
    多分支（a|b|c）逐支加边界，不整体加 —— 否则只在首尾生效，中间分支仍裸匹配。
    """
    parts = []
    for alt in pattern.split("|"):
        if not alt:
            continue
        lead = r"\b" if re.match(r"[A-Za-z0-9]", alt) else ""
        trail = r"\b" if re.search(r"[A-Za-z0-9]$", alt) else ""
        parts.append(lead + alt + trail)
    return "|".join(parts) if parts else pattern


def skill_tokens(slug, desc, cands=None):
    """返回 (regex, kept_tokens, dropped)。cands 为空则不做 df 过滤（夹具用）。"""
    toks = build_tokens(slug, desc)
    dropped = []
    if cands:
        kept, dropped = df_filter(cands, toks)
    else:
        kept = [t for t, _s in toks]
    if not kept:
        return None, [], dropped
    return re.compile(word_bound("|".join(kept)), re.I), kept, dropped


def rel_strength(cand, slug_toks, desc_toks, fam_re):
    """相关性**强度**（不是二值）。返回 (rel_score, rel_label)。

    为什么不用二值（r114 一手，两次排序实测）：
      二值 rel 下，只要 desc 里出现一个 'text'/'file' 就把仓标 skill，再按 score5
      （仓的通用质量）排序 ⇒ 通用大仓恒压过真上游。实测 agent-browser 的前二名是
      invisible_dots / taste-skill，而真上游 vercel-labs/agent-browser 排第三。
      ⇒ 改按「命中了多少**身份词**（来自 slug/name）> 多少 desc 词」排序。

    权重：身份词命中记 10（本件之所以是它自己），desc 词命中记 1（上下文补充）；
    name 面命中比 description 面命中更硬（slug 同形 = 同名件，最可能是真对应物）。
    """
    name_hay = (cand.get("full_name") or "").lower()
    body_hay = " ".join([cand.get("description") or "",
                         " ".join(cand.get("topics") or [])]).lower()
    score = 0
    hits = 0
    for t in slug_toks:
        try:
            cre = re.compile(word_bound(t), re.I)
        except re.error:
            continue
        if cre.search(name_hay):
            score += 20
            hits += 1
        elif cre.search(body_hay):
            score += 10
            hits += 1
    for t in desc_toks:
        try:
            cre = re.compile(word_bound(t), re.I)
        except re.error:
            continue
        if cre.search(name_hay) or cre.search(body_hay):
            score += 1
            hits += 1
    if score > 0:
        return score, "skill"
    if fam_re is not None and fam_re.search(name_hay + " " + body_hay):
        return 0, "family"
    return 0, "none"


def bucket_of(row):
    """相关性分桶（0 = 最强）。桶定义与实测依据见 rel_strength 的 docstring。

    r114 一手（第四次排序实测）：前三版都把「通用仓」排在真 skill 仓前面——
    pdf 的首名一度是 genspark-ai/genoffice（通用 office 工具），而 agent-browser 的
    真上游 vercel-labs/agent-browser 被挤到第三。根因是我只用「文本有没有撞词」判相关，
    没有用**这个仓到底是不是一个 skill 仓**这个硬事实。
    ⇒ 引入 skill_md_n > 0 作为**硬分桶前置**：带 SKILL.md 的仓才可能进 0/1 桶，
      不带的一律降到 2 桶以下。这不是加权而是换判据 —— 与 R263「修机制不修数据」同向。

    0 = 真 skill 仓（skill_md_n>0）且身份词命中仓名
    1 = 真 skill 仓且身份词命中描述
    2 = 有相关性但不是真 skill 仓（通用工具/框架，须由人判是否可用）
    3 = 仅族级命中（family）
    4 = 无相关性（不该出现；出现即具名登记，禁静默吞）
    """
    if row.get("rel") != "skill":
        return 3 if row.get("rel") == "family" else 4
    s = row.get("rel_strength") or 0
    sm = row.get("skill_md_n")
    is_skill_repo = bool(sm) and sm > 0
    if not is_skill_repo:
        return 2
    if s >= 10:
        return 0 if s >= 20 else 1
    return 2


def require_sig(n):
    """一个件至少要有几个 skill 相关候选才算 MATCHED（默认 3 = 需求原文的 3-5）。
    r114 一手：阈值不按「有几个词命中」而按「有几**个仓**命中」——前者可被一个仓多词刷高。"""
    return max(3, min(5, n))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--json", dest="json_out", default=None)
    # r211 修（需求 5 长效机制实测断裂）：原缺省指 _temp/local_fm_r114.json —— 那份件
    # 全史零入库、全仓无生成器（W-46 死句柄），且 _temp 会被并行会话按扩展名清场
    # （R189-2 实测 212 件）。现缺省改指**入库面**的产物，由 r211_local_fm.py 生成；
    # 季度巡检已把它接成第 ⑥ 段的前置步，不再依赖任何人手工产物。
    ap.add_argument("--local-fm", default=os.path.join(BENCH, "local_frontmatter.json"))
    ap.add_argument("--max-cand-per-family", type=int, default=12)
    ap.add_argument("--workers", type=int, default=8,
                    help="候选仓测量的并发度（1 = 串行；GitHub core 5000/h 足够）")
    ap.add_argument("--cache-dir", default=None,
                    help="池散件目录（缺省 _temp/r114_search_cache；可指空目录以模拟被清场）")
    ap.add_argument("--pool-pack", default=None,
                    help="入库池包（缺省 06-benchmark/pool_cache_r217.json；传 none = 只用散件）")
    ap.add_argument("--remeasure", action="store_true",
                    help="跳过仓级缓存重新取树（严格口径 skill_md_exact_n 靠它补；须联网，离线时该路走不通）")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

    if not os.path.exists(args.local_fm):
        print("[REPL:UNVERIFIED] 本地 frontmatter 面缺失: %s ⇒ 先跑 "
              "python 05-exec/r211_local_fm.py 生成（禁再手工造件）" % args.local_fm)
        return 2
    _doc = json.load(io.open(args.local_fm, encoding="utf-8"))
    # r211：生成器 r211_local_fm.py 写的是带 schema/generated_at 的**自描述件**（入库面需要出处），
    # 而 r114 当年的手工件是裸 list。两种形态都收，缺任一侧都会把判据读成 0 件（R247）。
    locals_ = _doc.get("rows") if isinstance(_doc, dict) else _doc
    if not locals_:
        print("[REPL:UNVERIFIED] 本地面 0 件 ⇒ 不得读成无缺口（R247）｜件内 keys=%s"
              % (",".join(sorted(_doc.keys())[:6]) if isinstance(_doc, dict) else "裸件"))
        return 2

    if not args.offline:
        rem, err = rate_search()
        if err or rem is None or rem < MIN_RATE:
            print("[REPL:UNVERIFIED] search 配额不足/取不到（rem=%s err=%s）⇒ 整轮不可用，"
                  "不写主产物（禁半截面）" % (rem, err))
            return 2

    # r217：--pool-pack none 退回「只读散件」的旧行为（有牙验证用）。
    # 注意 None 与 "" 的区别：None 在 load_cache 里表示「用缺省包」，所以显式关包必须传 ""，
    # 首版写成 None 会让这个开关静默失效（= 想证明「包起作用」时两边都读了包）。
    if (args.pool_pack or "").lower() == "none":
        _pack_arg = ""
    else:
        _pack_arg = args.pool_pack
    _cache_prov = {}
    cache = load_cache(args.cache_dir, _pack_arg, _cache_prov)
    stats = {"api_calls": 0, "cache_hits": 0, "cache_miss": 0, "errors": []}

    pool = {}
    qmeta = []
    for qid, q in POOL_QUERIES:
        doc = search(q, cache, args.offline, stats)
        qmeta.append({"id": qid, "q": q, "state": doc.get("state"),
                      "total": doc.get("total"), "rows_n": len(doc.get("rows") or [])})
        for r in doc.get("rows") or []:
            prev = pool.get(r["full_name"])
            if prev is None or (r.get("stars") or 0) > (prev.get("stars") or 0):
                pool[r["full_name"]] = dict(r)
    pool_n = len(pool)
    if pool_n == 0:
        print("[REPL:UNVERIFIED] 候选池 0 仓（查询全失败或全空）⇒ 不得读成无替代（R247）")
        return 2

    fam_pool = {}
    fam_re_of = {}
    for fid, name, fpat, spat in FAMILIES:
        fre = re.compile(fpat, re.I)
        fam_re_of[fid] = fre
        cands = []
        for fn, r in pool.items():
            hay = " ".join([fn, r.get("description") or "",
                            " ".join(r.get("topics") or [])])
            if fre.search(hay):
                cands.append(r)
        cands.sort(key=lambda x: -(x.get("stars") or 0))
        fam_pool[fid] = cands

    lf = {r["slug"]: r for r in locals_}
    per_skill = []
    need_measure = set()
    for r in locals_:
        slug = r["slug"]
        fid = classify(slug, r.get("desc"))
        cand = fam_pool.get(fid, [])
        sre, toks, dropped = skill_tokens(slug, r.get("desc"), cand)
        # 身份词（来自 slug）与上下文词（来自 desc）分开，用于相关性强度加权
        slug_toks = [t for t, src in build_tokens(slug, r.get("desc")) if src == "slug"]
        desc_toks = [t for t, src in build_tokens(slug, r.get("desc")) if src == "desc"]
        kept_set = set(toks)
        slug_toks = [t for t in slug_toks if t in kept_set]
        desc_toks = [t for t in desc_toks if t in kept_set]
        fam_re = fam_re_of.get(fid)
        rel_rows = []
        for c in cand[:200]:
            rs, rel = rel_strength(c, slug_toks, desc_toks, fam_re)
            rel_rows.append((rel, rs, c))
        # 排序键：先 skill/family/none，再相关性强度降序，最后 stars 降序
        rel_rows.sort(key=lambda x: (0 if x[0] == "skill" else 1, -x[1],
                                     -(x[2].get("stars") or 0)))
        picked = []
        for rel, rstrength, c in rel_rows:
            if len(picked) >= args.max_cand_per_family:
                break
            picked.append((rel, rstrength, c))
            need_measure.add(c["full_name"])
        per_skill.append({"slug": slug, "family": fid, "tokens": toks,
                          "dropped": dropped, "picked": picked, "pool_n": len(cand)})

    # 并行测量（r114 一手：串行 311 仓 × ~16s ≈ 83 分钟，实测半小时才走完 57 仓）。
    # workers 默认 8：GitHub core 配额 5000/h，8 并发 × 2 请求/仓远低于限流；
    # 缓存写已加锁；stats 计数走 bump/note_error 加锁，禁裸 +=（会丢计数）。
    measured = {}
    todo = [fn for fn in sorted(need_measure) if fn not in measured]
    if args.workers <= 1 or args.offline:
        for fn in todo:
            measured[fn] = measure_repo(fn, cache, args.offline, stats, args.remeasure)
    else:
        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            futs = {ex.submit(measure_repo, fn, cache, args.offline, stats, args.remeasure): fn
                    for fn in todo}
            done = 0
            for fut in as_completed(futs):
                fn = futs[fut]
                try:
                    measured[fn] = fut.result()
                except Exception as exc:  # noqa: BLE001
                    note_error(stats, {"repo": fn, "step": "measure", "error": repr(exc)})
                    measured[fn] = {"state": "UNVERIFIED", "error": repr(exc)}
                done += 1
                if not args.quiet and done % 25 == 0:
                    print("  measured %d/%d" % (done, len(todo)))

    fam_name = dict((f[0], f[1]) for f in FAMILIES)
    rows = []
    tally = {"MATCHED": 0, "FAMILY_ONLY": 0, "NO_OS_CANDIDATE": 0, "UNVERIFIED": 0}
    for ps in per_skill:
        slug, fid, picked = ps["slug"], ps["family"], ps["picked"]
        scored = []
        for rel, rstrength, c in picked:
            m = measured.get(c["full_name"])
            if not m or m.get("state") != "OK":
                continue
            s, tot, fc_cal = score5(m)
            scored.append({"repo": c["full_name"], "rel": rel, "rel_strength": rstrength,
                          "fc_caliber": fc_cal,
                           "score5": s, "score_total": tot,
                           "stars": m.get("stars"), "pushed_at": m.get("pushed_at"),
                           "license": m.get("license"), "archived": m.get("archived"),
                           "skill_md_n": m.get("skill_md_n"),
                           # R211-9 双口径同列（见 compute_tree 处注释）。**取不到必须显形为 None**，
                           # 不得补 0：池缓存里 399 个仓是 r218 之前测的、根本没有这两个字段
                           # ⇒ 缓存命中路径原样返回旧件（r184 行实测），补 0 会读成「严格口径 = 0 个 SKILL.md」，
                           #   那是用缺字段造假阴性（R247 反面）。
                           "skill_md_exact_n": m.get("skill_md_exact_n"),
                           "skill_md_ghost_n": m.get("skill_md_ghost_n"),
                           "docs_md_n": m.get("docs_md_n"),
                           "test_path_n": m.get("test_path_n"),
                           "workflow_n": m.get("workflow_n"),
                           "description": (m.get("description") or "")[:150]})
        # 排序 = 「相关性**分桶**，桶内按五维总分」（r114 三次排序实测的定稿）
        # 一手：纯按 rel_strength 排 ⇒ 52 星的小仓因名字撞词压过 32k 星的正主；
        #       纯按 score_total 排 ⇒ 通用大仓压过真上游。
        #       分桶后两者各归其位：桶只回答「是不是同一类东西」，桶内才比质量。
        scored.sort(key=lambda x: (bucket_of(x), -x["score_total"]))
        skill_n = sum(1 for x in scored if x["rel"] == "skill")
        top = [x for x in scored if x["rel"] == "skill"][:5]
        if len(top) < 3:
            top = top + [x for x in scored if x["rel"] != "skill"][:5 - len(top)]
        if fid == "OTHER":
            verdict = "UNVERIFIED"
            note = "未命中任何族规则 ⇒ 具名列出（禁静默算作已覆盖）"
        elif not scored:
            verdict = "UNVERIFIED"
            note = "候选仓全部取数失败 ⇒ 禁读成无替代（R247）"
        elif skill_n >= 3:
            verdict = "MATCHED"
            note = ""
        elif skill_n == 0 and ps["pool_n"] > 0:
            verdict = "NO_OS_CANDIDATE"
            note = ("族池 %d 仓、试过关键词 %s，无一命中 ⇒ 开源侧无对应件"
                    % (ps["pool_n"], ",".join(ps["tokens"][:6]) or "（空）"))
        else:
            verdict = "FAMILY_ONLY"
            note = "仅族级候选命中（skill 词命中 %d 个），如实降档" % skill_n
        tally[verdict] += 1
        rows.append({"slug": slug, "family": fid, "family_name": fam_name.get(fid, "未归族"),
                     "local_bytes": lf[slug].get("local_bytes"),
                     "local_desc_len": lf[slug].get("desc_len"),
                     "keywords": ps["tokens"][:8],
                     "dropped_tokens": ps["dropped"][:8],
                     "family_pool_n": ps["pool_n"],
                     "candidates_n": len(top), "skill_relevant_n": skill_n,
                     "candidates": top, "verdict": verdict, "note": note})

    total = sum(tally.values())
    ok = (total == len(locals_))
    # 严格口径覆盖率（必显形）：新字段只在**联网重测**时产生，池缓存里的旧件没有 ⇒
    # 若离线跑，双口径列会几乎全空。不报覆盖率就会让人以为「严格口径 ≈ 生产口径」。
    _cand_all = [c for ps in rows for c in (ps.get("candidates") or [])]
    _exact_have = sum(1 for c in _cand_all if isinstance(c.get("skill_md_exact_n"), int))
    _ghost_n = sum(1 for c in _cand_all if (c.get("skill_md_ghost_n") or 0) > 0)
    doc = {
        "schema": "replacement-matrix-r114-v1",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00"),
        "cmd": "python 05-exec/r114_replacement_scan.py",
        "face": {"local_n": len(locals_), "pool_n": pool_n,
                 "queries_n": len(POOL_QUERIES), "families_n": len(FAMILIES),
                 "candidates_measured": len(measured),
                 "strict_caliber_coverage": {"candidates_total": len(_cand_all),
                                              "with_exact_field": _exact_have,
                                              "repos_with_ghosts": _ghost_n,
                                              # 覆盖率 < 1 是**已知且如实**的状态：旧池件无该字段
                                              "coverage_note": "skill_md_exact_n / skill_md_ghost_n 只在**重取树**时产生"
                                                               "（--remeasure，须联网）；池缓存旧件无该字段 ⇒ 读成 None。"
                                                               "禁补 0，禁把「无字段」读成「严格口径=0」（R247）。"},
                 "api_calls": stats["api_calls"], "cache_hits": stats["cache_hits"],
                 "cache_miss": stats["cache_miss"], "offline": bool(args.offline),
                 "cache_provenance": _cache_prov,
                 # 包陈旧告警：离线跑且散件目录空/不存在，全靠包 ⇒ 读数出自哪一天必须显形
                 "pool_from_stale_pack": bool(args.offline and not _cache_prov.get("loose_files")
                                              and _cache_prov.get("pack_entries"))},
        "conservation": {"sum_verdicts": total, "local_n": len(locals_),
                         "ok": ok, "by_verdict": tally},
        "queries": qmeta,
        "families": [{"id": f[0], "name": f[1], "family_pattern": f[2],
                      "slug_pattern": f[3],
                      "slugs_n": sum(1 for ps in per_skill if ps["family"] == f[0]),
                      "pool_n": len(fam_pool.get(f[0], []))} for f in FAMILIES],
        "errors": stats["errors"][:40],
        "rows": rows,
    }
    out = args.json_out or os.path.join(
        BENCH, "replacement_matrix_r114_%s.json" % datetime.now().strftime("%Y-%m-%d"))
    tmp = out + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, out)

    # 故意放在 --quiet 门之外（r217）：巡检以 --quiet 跑本步，stdout_tail 会进 audit.json，
    # 所以「读数出自哪天」必须连静默跑也印得出来 —— 只写进 JSON 字段等于把告警藏进没人打开的件里。
    if doc["face"]["pool_from_stale_pack"]:
        print("[POOL:FRESHNESS] ⚠️ 本轮离线且散件缓存为空/不存在 ⇒ 候选面全部取自入库池包："
              "pack=%s（%d 条，生成于 %s）｜禁把该读数当「今日池」引用（r120 trace_face 同族范式）"
              % (_cache_prov.get("pack_path"), _cache_prov.get("pack_entries"),
                 _cache_prov.get("pack_generated_at")))

    if not args.quiet:
        print("池：%d 仓（%d 条查询，api=%d cache=%d）｜ 候选实测 %d 仓"
              % (pool_n, len(POOL_QUERIES), stats["api_calls"], stats["cache_hits"],
                 len(measured)))
        print("四态：MATCHED=%d FAMILY_ONLY=%d NO_OS_CANDIDATE=%d UNVERIFIED=%d ｜ "
              "守恒 %d==%d %s"
              % (tally["MATCHED"], tally["FAMILY_ONLY"], tally["NO_OS_CANDIDATE"],
                 tally["UNVERIFIED"], total, len(locals_), "OK" if ok else "BROKEN"))
        for f in doc["families"]:
            print("  %-12s %-28s 件=%3d 族池=%3d" % (f["id"], f["name"][:28],
                                                    f["slugs_n"], f["pool_n"]))
        if stats["errors"]:
            print("取数失败 %d 条（首条：%s）" % (len(stats["errors"]), stats["errors"][0]))
    print("JSON -> %s" % out)
    if not ok:
        print("[REPL:FAIL] 守恒破坏：四态之和 %d != 本地 %d" % (total, len(locals_)))
        return 1
    print("[REPL:PASS] 逐件候选面守恒 %d==%d ｜ MATCHED=%d FAMILY_ONLY=%d "
          "NO_OS_CANDIDATE=%d UNVERIFIED=%d"
          % (total, len(locals_), tally["MATCHED"], tally["FAMILY_ONLY"],
             tally["NO_OS_CANDIDATE"], tally["UNVERIFIED"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
