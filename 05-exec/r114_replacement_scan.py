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
from datetime import datetime, timezone, date, timedelta
# date/timedelta 为 r260 §3.1 维护状态过滤所加（maintenance_trim 算 12 个月阈值要用）

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
    # ---- 正文级许可（R261-6 落地，r262）----------------------------------------------
    # 只在 API 字段可疑时多花一次调用：NOASSERTION（含缺失被上游归此值）就是 dify / Imbad0202
    #   两例的共性。取正文走 repos/<full>/license —— GitHub 自己解析 LICENSE 文件，一次调用
    #   即可，不必从树里猜文件名（也省一次 blob 下载）。
    # 离线/取不到 ⇒ license_body_class 留 None（**不得**当成宽松或受限，R247 双向）；
    # 该仓走旧缓存时同样没有此字段 ⇒ 世代回退由 score5 的 use_body=False 表达，不靠造数据。
    lic_api = (doc.get("license") or "").upper()
    if lic_api in ("NOASSERTION", ""):
        lout, lerr = gh(["api", "repos/%s/license" % full])
        bump(stats, "api_calls")
        time.sleep(CORE_SLEEP)
        if lerr:
            doc["license_body"] = "unavailable:%s" % lerr[:80]
        else:
            try:
                ld = json.loads(lout)
                import base64 as _b64
                blob = _b64.b64decode(ld.get("content") or "")[:6144]
                up = blob.decode("utf-8-sig", "replace").upper()
                doc["license_body_path"] = ld.get("path") or ""
                doc["license_body_spdx_api"] = ((ld.get("license") or {}).get("spdx_id") or "")
                # 单源判定：classify_body（抓取脚本、门、夹具都用它），避免两处各写各的（R260-5）
                spdx_b, cls_b, hits_b = classify_body(up)
                doc["license_body_class"] = cls_b
                doc["license_body_spdx"] = spdx_b or ""
                doc["license_body_restricted_phrases"] = hits_b
                doc["license_body"] = "read:%dB" % len(blob)
            except Exception as exc:  # noqa: BLE001
                doc["license_body"] = "parse_failed:%r" % (exc,)
    save_cache(key, doc)
    return doc


# ---- 许可风险/能否合入子腿（R260-1 立，r261 落地）---------------------------------------
# 为什么必须有：compat 原三腿（license 明确 + 非 archived + 有 SKILL.md）对许可证只做**二值**判断
#   （UNLICENSED / 非 UNLICENSED）⇒ AGPL 与 MIT 拿同样 2 分。r260 实测代价具名：48 个 copyleft 候选
#   全部 compat=5、9 行把它们排在 rank0（本仓远端 public + 刻意无 LICENSE = X-2 ⇒ 合入 copyleft 直接
#   产生许可义务冲突，口径见 07 台账 R113-3 自决裁决）⇒ 排序层完全不拦这类风险。
# 做法 = license_class() 归五档 + score5 给 compat 设**上限 cap**（cap 只降不升，其余腿不动）：
#   copyleft=1 / weak-copyleft=2 / unknown=4 / permissive=5 / none=5（none 的 3 分由原二值腿自然产生，
#   不再叠加 cap ⇒ 与 r260 前逐字同分，本改动只影响 copyleft/weak/unknown 三类）。
LICENSE_CAPS = {"copyleft": 1, "weak-copyleft": 2, "restricted": 1, "unknown": 4,
                "permissive": 5, "none": 5}

# ---- 正文级许可指纹（R261-6 立，r262 落地）----------------------------------------------
# 为什么必须有：GitHub API 的 license.spdx_id 会骗人。r261 由 C2 人读实测两例（本仓 gh api 复现）：
#   · langgenius/dify       → API 报 NOASSERTION，正文实为「modified Apache 2.0 + 额外条件」，
#     且明文「多租户服务须取得商业授权」⇒ 名义宽松、实际受限；
#   · Imbad0202/academic-research-skills → API 报 NOASSERTION，正文实为 CC BY-**NC** 4.0（非商业）。
# 我的上一版把 NOASSERTION 归 unknown（cap=4，只是轻罚）⇒ 在正文证据面前**偏松**，而这类仓恰恰
# 最像可用（名字/描述都对得上，会被排到 rank0）。故新增 restricted 档（cap=1，与 copyleft 同级）。
# 表与 05-exec/r260_local_baseline.py 的 LICENSE_TEXT_SIGS 同源扩展（本地侧那份由夹具 t15 对账，
# 防两处定义漂移 —— R263/R280 同族）。
LICENSE_TEXT_SIGS = [
    # 顺序敏感：带额外条件/NC 的必须先判，否则会被下面的宽松档吃掉（modified Apache 含 "Apache
    # License" 子串、CC BY-NC 含 "Creative Commons Attribution" 子串）。
    ("CC-BY-NC-4.0", ("Creative Commons", "Attribution-NonCommercial")),
    ("MODIFIED-APACHE-RESTRICTED", ("Modified Version of the Apache License",)),
    # R275-1（r276 落地）：**源可得但限制商用**的家族 —— 它们不是 OSI 宽松许可，却因为名字里不带
    #   GPL/NC 而完全不进既有名单，后果是判成 unknown(cap=4)、按「不确定」放行。一手：r275 执行 R262-2 时
    #   实测 mksglu/context-mode 正文首行即 Elastic License 2.0 (ELv2)，旧版 classify_body 返回 None。
    #   放在宽松档之前（顺序敏感），并同步进 RESTRICTED_SPDX ⇒ 档位落 restricted 且**家族具名**。
    ("ELASTIC-2.0", ("Elastic License 2.0", "Elastic License")),
    ("SSPL-1.0", ("Server Side Public License",)),
    ("BUSL-1.1", ("Business Source License",)),
    ("COMMONS-CLAUSE", ("Commons Clause",)),
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
# 正文里出现这些措辞 ⇒ 即使 SPDX 看着宽松也算受限（商用/署名/再分发被加条件）。
# ⚠️ 措辞表 r262 二版（我 r262 首版有系统性假阳性，实测抓到）：首版含泛化短语 "MAY NOT USE"，
#   而 Apache-2.0 **标准文件头**本身就写着 "YOU MAY NOT USE THIS FILE EXCEPT IN COMPLIANCE WITH
#   THE LICENSE" ⇒ 命中 kubesphere/kubesphere（真 Apache-2.0）与 op7418/CodePilot。若保留，
#   所有 Apache 仓都会被压到 cap=1 = 把最好的仓误杀。正解 = 只留**确证受限**的措辞：
#   "FOR A COMMERCIAL PURPOSE"（op7418 原文 "YOU MAY NOT USE THE LICENSED WORK FOR A COMMERCIAL
#   PURPOSE"）与 "COMMERCIAL LICENSE MUST BE OBTAINED"（dify 原文），泛化措辞一律不用。
# 判别式取自正文原句（r262 二版，两处都是实测）：
#   · "WITH THE FOLLOWING ADDITIONAL CONDITIONS" = dify 与 kubesphere 共有的句式，而标准
#     Apache-2.0 / MIT / AGPL 正文都没有这句 ⇒ 它精确命中「Apache 名义宽松 + 附加商业条件」这一族。
#     （我第一版用泛化的 "MAY NOT USE" 抓它，会把 Apache 标准文件头自己那句
#      "YOU MAY NOT USE THIS FILE EXCEPT IN COMPLIANCE WITH THE LICENSE" 也拖下水 = 系统性假阳性；
#      删掉该短语后又走偏成假阴：kubesphere 被判 permissive，而它正文实为需商业授权。）
#   · "FOR A COMMERCIAL PURPOSE" 抓 op7418/CodePilot（"YOU MAY NOT USE THE LICENSED WORK FOR A
#     COMMERCIAL PURPOSE"）—— 该短语在原文里被**换行打断**，故必须做空白折叠匹配（见 classify_body）。
RESTRICTED_PHRASES = ("WITH THE FOLLOWING ADDITIONAL CONDITIONS",
                      "COMMERCIAL LICENSE MUST BE OBTAINED", "FOR A COMMERCIAL PURPOSE",
                      "NONCOMMERCIAL", "NON-COMMERCIAL", "ATTRIBUTION-NONCOMMERCIAL")
# 正文识别出的 spdx 里，这些属「名义像宽松、实际带条件/非商业」⇒ 与 copyleft 同级禁合入
RESTRICTED_SPDX = ("CC-BY-NC", "MODIFIED-APACHE-RESTRICTED", "RESTRICTED",
                   # R275-1：源可得但限制商用（非 OSI 认可）⇒ 与 copyleft 同级禁合入。
                   "ELASTIC-2.0", "SSPL-1.0", "BUSL-1.1", "COMMONS-CLAUSE")


def classify_body(text_upper):
    """正文指纹归一（单一口径）：返回 (spdx 或 None, 档位, 命中的受限措辞)。

    为什么必须有这一个函数：r262 首版我在 _temp 抓取脚本里**重复实现**了一遍判定（违 R260-5
    「读实现优先于写探针」），两处各写各的 ⇒ 抓取包与量尺可能给出不同档位而无人发现。
    现在抓取脚本、measure_repo、夹具、门全部调本函数（单源）。

    判序（两条都是实测踩过的假阴）：
      · 受限名单先判：MODIFIED-APACHE-RESTRICTED 含子串 APACHE、CC-BY-NC 含子串 CC-BY，
        若先走宽松档，YaoApp/yao 会被判 permissive（r262 实测首版就是这么漏的）；
      · 措辞命中与 spdx 命中取**更严的一方**（dify 正文同时命中两者）。
    """
    # 空白折叠：法律正文是硬换行的，短语与指纹都可能被 \n 打断。r262 实测一手：
    #   op7418/CodePilot 原文写作 "...FOR A COMMERCIAL\n                      PURPOSE"，
    #   不折叠就匹配不到 ⇒ 判成 permissive（假阴，方向危险：受限仓被放走）。
    #   折叠同时修掉一个潜在假阴：AGPL/GPL 的标题行本身也可能换行。
    up = " ".join((text_upper or "").split())
    spdx = None
    for name, keys in LICENSE_TEXT_SIGS:
        if all(k.upper() in up for k in keys):
            spdx = name
            break
    hits = [ph for ph in RESTRICTED_PHRASES if ph in up]
    restricted_by_name = bool(spdx) and any(tag in spdx for tag in RESTRICTED_SPDX)
    if restricted_by_name or hits:
        return spdx, "restricted", hits
    if spdx is None:
        return None, "unknown", hits
    return spdx, license_class(spdx), hits


# ---- 正文证据包装载（克隆可用，r262）------------------------------------------------------
# 为什么必须有：_temp/ 缓存被 gitignore ⇒ 一次干净克隆里没有任何正文证据，量尺会静默退回
#   「只信 API 字段」，也就是退回 dify / Imbad0202 那类受限仓被判 unknown(cap=4) 的状态 ——
#   证据存在但拿不到，等于没取证。故正文结论落一份**跟踪件**（06-benchmark/license_body_r262.json，
#   由 05-exec/r262_license_body_pack.py 现生成），量尺按仓名装载。
BODY_PACK = os.path.join(BENCH, "license_body_r262.json")


def load_body_pack(path=BODY_PACK):
    """读正文证据包；缺件/解析失败 ⇒ 返回 None（调用方显形，禁当成「全部宽松」）。"""
    if not os.path.isfile(path):
        return None
    try:
        d = json.load(io.open(path, encoding="utf-8-sig"))
    except Exception as exc:
        return {"_error": repr(exc)[:120]}
    if d.get("schema") != "license-body-pack-v1":
        return {"_error": "schema:%s" % d.get("schema")}
    return d


def apply_body_pack(measured, pack):
    """把包里的正文档并进 measured（只补**没有**正文档的件；已有 = 本轮联网现取，优先现取值）。

    返回 (applied, still_without_body, unavailable_in_pack)：第三项 = 包里明写 UNAVAILABLE 的仓，
    即「上游取不到正文」，必须显形而不是静默按 API 字段走。
    """
    repos = (pack or {}).get("repos") or {}
    applied = 0
    still = 0
    unav = 0
    for fn, m in measured.items():
        if not isinstance(m, dict) or m.get("state") != "OK":
            continue
        if m.get("license_body_class"):
            continue
        if (m.get("license") or "").upper() not in ("NOASSERTION", ""):
            continue
        ent = repos.get(fn)
        if not ent:
            still += 1
            continue
        if ent.get("state") != "OK":
            unav += 1
            m["license_body"] = "pack_unavailable:%s" % (ent.get("error") or "")[:60]
            continue
        m["license_body_class"] = ent.get("license_body_class")
        m["license_body_spdx"] = ent.get("license_body_spdx") or ""
        m["license_body_restricted_phrases"] = ent.get("restricted_phrases") or []
        m["license_body_path"] = ent.get("license_body_path") or ""
        m["license_body"] = "pack:%s" % (ent.get("sha8_head") or "")
        applied += 1
    return applied, still, unav

# ---- 声明上游（.upstream 边车）识别（R261-5 立，r263 落地）--------------------------------
# 为什么必须有：r262 实测两件（gstack / ppt-master）的真上游不在候选面里 —— 候选来自关键词搜索，
#   而搜索永远搜不到「我们自己声明的那个上游」。危害不止少一行读数：gstack 因此拿到
#   verdict=NO_OS_CANDIDATE（断言开源侧无对应件），而它的上游 garrytan/gstack 有 138k stars。
#   ⇒ 声明的上游必须能被读到，且**在它存在时不得判「无对应件」**。
UPSTREAM_ROOT = os.environ.get('ZIJIAN_SKILLS_ROOT', 'D:/global_skills')
RE_REPO_LINE = re.compile(r'^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$')


def parse_sidecar(text):
    '''`.upstream` 正文 -> (repo, 子路径)。侧车形态实测三种（1 行纯 repo / 2 行 repo+path / 3-4 行），
    故按内容解析而非按行号：第一个形如 owner/repo 的行即 repo，path: 行给子路径。'''
    repo, subpath = None, None
    for raw in (text or '').splitlines():
        ln = raw.strip()
        if not ln:
            continue
        if ln.lower().startswith('path:'):
            subpath = ln.split(':', 1)[1].strip() or None
            continue
        if repo is None and RE_REPO_LINE.match(ln):
            repo = ln
    return repo, subpath




def parse_version(text):
    '''SKILL.md 头部第一个 version: x.y(.z)（返回 None 表示没有）。

    不写「带引号字符类」的正则，改为 startswith + 去引号 + 纯版本号校验：树里实测两种写法
    （version: 1.3.0 与 version: "6.6.0"），还有一件是缩进在嵌套块里。用这么写既覆盖三形态，
    又不在源码里塞容易出转义错的字符类（r263 首版就栽在这类转义上）。'''
    for line in (text or '').splitlines()[:60]:
        s = line.strip()
        if not s.startswith('version:'):
            continue
        v = s.split(':', 1)[1].strip().strip(chr(34)).strip(chr(39))
        if re.match(r'^[0-9]+(\.[0-9]+){1,3}$', v):
            return v
    return None


def vtuple(v):
    '''版本串 -> 整数元组（None 表示不可比）。'''
    if not v:
        return None
    return tuple(int(x) for x in v.split('.'))


def rel_of(local, upstream):
    '''版本关系：BEHIND / SAME / AHEAD / UNKNOWN_*（缺数据时绝不猜，两个未知方向分开报）。'''
    a, b = vtuple(local), vtuple(upstream)
    if a is None and b is None:
        return 'UNKNOWN_BOTH'
    if a is None:
        return 'UNKNOWN_LOCAL'
    if b is None:
        return 'UNKNOWN_UPSTREAM_RELEASE'
    n = max(len(a), len(b))
    a = a + (0,) * (n - len(a))
    b = b + (0,) * (n - len(b))
    if b > a:
        return 'BEHIND'
    if b < a:
        return 'AHEAD'
    return 'SAME'

def load_declared_upstreams(root=UPSTREAM_ROOT):
    '''件名 -> 声明上游 repo（只读取证，绝不写受管根）。缺目录/读失败 => 返回空表而非抛错：
    调用方据「表里没有」判「没声明」；而「声明了但解析不出」是另一种状态，后者同样禁判无对应件。'''
    out = {}
    if not os.path.isdir(root):
        return out
    for name in sorted(os.listdir(root)):
        side = os.path.join(root, name, '.upstream')
        if not os.path.isfile(side):
            continue
        try:
            repo, _sp = parse_sidecar(io.open(side, encoding='utf-8-sig', errors='replace').read())
        except OSError:
            continue
        if repo:
            out[name] = repo
    return out

def license_class(lic, body_class=None):
    """许可证字符串 → 五档归一（copyleft / weak-copyleft / unknown / permissive / none）。

    判序敏感，三处都是实测踩过的坑（夹具里各钉一条反例）：
      · AGPL 与 LGPL 都含子串 GPL ⇒ 必须先 AGPL、再 LGPL，最后才判 GPL，否则三档全塌成 GPL；
      · CC-BY-SA-4.0 与 CC-BY-4.0 共享前缀 ⇒ 先判带 -SA 的（share-alike 属 copyleft 类）；
      · UNLICENSE（theunlicense，公有领域 dedications，**可合入**）与 UNLICENSED（无任何许可，
        不可合入）只差两个字母 ⇒ 必须全等比较，禁 startswith。
    只按正证据归档：认不出的 SPDX 串 ⇒ unknown（cap=4，比 permissive 低、比真无许可的风险档高），
    禁把「我没认出来」读成「安全」（R247）。
    """
    # body_class（r262）= 读 LICENSE 正文得到的档位。有正文证据时**正文优先**：API 字段
    #   会报 NOASSERTION 把受限仓放进 unknown（cap=4），而正文能证明它是 copyleft / 非商业 /
    #   带商业授权条件（R261-6 两例实测）。正文没有（旧缓存件 / 取不到）时照旧按 API 字段判，
    #   且绝不把「没读到正文」当成宽松（R247 双向）。
    if body_class in LICENSE_CAPS:
        return body_class
    u = (lic or "").strip().upper()
    if not u or u == "UNLICENSED":
        return "none"
    if u == "UNLICENSE":
        return "permissive"
    if "NOASSERTION" in u:
        return "unknown"
    if "AGPL" in u or "AFFERO" in u:
        return "copyleft"
    if "LGPL" in u or "MPL" in u or "EPL" in u or "GPL-2.0+ WITH" in u:
        return "weak-copyleft"
    if "GPL" in u or "CC-BY-SA" in u or "GNU FREE DOC" in u:
        return "copyleft"
    # CC-BY（无 SA）与 CC0 属可合入档：上一行已把 CC-BY-SA 截走，故此处 startswith 安全。
    if any(k in u for k in ("MIT", "APACHE", "BSD", "ISC", "ZLIB", "CC0", "CC-BY", "ARTISTIC", "POSTGRESQL")):
        return "permissive"
    return "unknown"


def score5(m, license_cap=True, use_body=True):
    """五维锚定分（各 0-5，合计 25）。每维锚点可复算，不凭印象。

    license_cap=False = 回滚开关（红线4 要求机制化必须带不改数据的退路）：关掉后 compat 退回
    r260 前的二值口径，既用于对照实验（证明降档确实由这条腿产生、不是别的扰动），也是出问题时退路。
    默认开 ⇒ 所有既有调用方（r260_local_baseline / r220_caliber_flip 等）行为一致，不需各改一遍。

    原五维锚点：

    fc 功能完整性   SKILL.md 件数分档 + 无 SKILL.md 时按 blob 规模
    eff 运行效率    有 tests 与 workflows 为可自动化验证代理（少人工往返）
    compat 兼容性   license 明确 + 非 archived + 有 SKILL.md 约定，**r261 起再按许可档封顶**
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
    # compat 三腿原样保留（license 二值 + 非 archived + 有 SKILL.md），r261 起再套许可档上限：
    #   cap 只降不升 —— permissive 档 cap=5 等于不设限，故 MIT/Apache 等既有分数逐字不变
    #   （这是「不破坏既有结论」的硬约束，夹具 t3 专门钉它）；copyleft 无论其余腿多好都被压到 <=1。
    # use_body=False = 世代回退：正文指纹是 r262 才接进量尺的，关掉后只按 API 字段判档
    #   （用于复现 r261/r225 两代矩阵件，见 r260_local_baseline 的三组合同源自证）。
    _lic = license_class(m.get("license"),
                            m.get("license_body_class") if use_body else None)
    s["compat"] = min(5, (2 if (m.get("license") or "UNLICENSED") != "UNLICENSED" else 0)
                      + (0 if m.get("archived") else 1) + (2 if sm else 0))
    if license_cap:
        s["compat"] = min(s["compat"], LICENSE_CAPS[_lic])
    # ⚠️ 许可档**不得**塞进 s：score5 末尾是 sum(s.values()) 算总分，混入字符串直接把总分算炸
    #   —— 这正是本文件 L387-389 记载的 r225 首版事故（fc_caliber 当年同样被迫移出 s）。
    #   我 r261 首版犯了同一形态，被自己的 AST/求值复跑抓到（见 r261 报告；该文首版节号为 §13，
    #   独立成件后改号为 §1.x ⇒ 引节号前先 grep）。
    # 落盘字段由调用方现算 license_class(lic, body_class)。r262 起该函数**带第二个参数**
    #   （正文指纹优先），所以调用方必须把同一个 use_body 传进去：两处口径不同 ⇒ 落盘的
    #   license_class 与 compat 得分互相打脸（r262 自查抓到，四处调用点已统一）。
    #   仍禁把档位塞进 s（见上），因为总分是 sum(s.values())。
    rn = m.get("readme_n") or 0
    dn = m.get("docs_md_n") or 0
    s["docs"] = min(5, (2 if rn else 0) + (1 if dn > 5 else 0)
                    + (1 if dn > 40 else 0) + (1 if m.get("tree_state") == "OK" else 0))
    st = m.get("stars") or 0
    s["community"] = min(5, sum(1 for th in (100, 1000, 10000, 50000) if st >= th)
                         + (1 if (m.get("pushed_at") or "") >= "2026-07-01" else 0))
    return s, sum(s.values()), fc_caliber


# ---- 维护状态过滤（§3.1 机制化，r260 立）---------------------------------------------
# 为什么必须有：`04-plan/后续维护规范_季度巡检机制_r113` §3.1 早就写着「候选仓 archived=true
#   或 pushed_at 超 12 个月 ⇒ 从该件候选面剔除并具名登记」，但它一直是**规范句** —— 出候选面的
#   代码里没挂这条判据。r260 一手实测两件事：① 生产矩阵 937 个候选 slot 里确有 2 例违规（其一
#   archived=true 且正坐 rank2）；② 把同一条判据打到新补的定向检索面上是 60 slot / 12 例 / 7 件
#   （见 06-benchmark/r260_trim_violations.json 的 directed_search_face_sweep）。⇒ 只补检索不挂
#   过滤，会把违规从 2 例放大到 14 例：越努力检索，越把停摆仓推成 rank0 建议。
# 生效位置（关键，放错就等于没挂）：必须在 score5 之后、**sort 与 verdict 之前** ——
#   skill_relevant_n 决定 MATCHED/FAMILY_ONLY 分档，若只从输出 top5 里删，分档仍按含停摆仓的
#   计数算 ⇒ 假 MATCHED。
# 只按**正证据**剔除：archived 为 True，或 pushed_at 非空且严格早于阈值。字段缺失（旧池件无该列）
#   ⇒ 保留并计入 unknown_field 显形（R247：不许把「没数据」读成「违规」，也不许读成「健康」）。
TWELVE_MONTHS_DAYS = 365
# 评测日 = 本轮 r260 的日期。它是**判据输入**而非硬编码常量：矩阵件里以 maintenance_face.eval_date
# 落盘，下轮巡检复算时以当日重算 ⇒ 阈值随季度滚动（超 12 个月的仓会越来越多地被剔）。
EVAL_DATE = date(2026, 10, 28)


def maintenance_trim(m, eval_date):
    """按 §3.1 判一个候选仓是否停摆。返回 None=保留；否则返回剔除原因字符串。

    eval_date: date 对象（本轮评测日），阈值 = eval_date - 365 天。"""
    if m.get("archived"):
        return "archived"
    pushed = str(m.get("pushed_at") or "")[:10]
    if not pushed or len(pushed) < 10:
        return None                      # 字段缺失：保留，但由调用方计入 unknown_field
    try:
        p_y, p_m, p_d = int(pushed[0:4]), int(pushed[5:7]), int(pushed[8:10])
    except ValueError:
        return None                      # 不可析日期同样不判违规
    threshold = eval_date - timedelta(days=TWELVE_MONTHS_DAYS)
    if date(p_y, p_m, p_d) < threshold:
        return "stale_pushed_at"
    return None

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
    ap.add_argument("--no-license-cap", action="store_true",
                    help="回滚开关（红线4）：关掉 compat 的许可档上限，退回 r260 前的二值口径；仅用于对照实验与应急退路"),
    ap.add_argument("--no-license-body", action="store_true",
                    help="世代回退（红线4）：量尺不看 LICENSE 正文指纹，只按 API 字段判档（复现 r261 代矩阵件用）"),
    ap.add_argument("--no-maintenance-trim", action="store_true",
                    help="回滚开关（红线4）：关掉 §3.1 维护状态过滤，回到 r260 之前的候选面口径。"
                         "默认不关 —— 关掉后停摆仓会重新进入 rank 与分档。")
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

    lf = {r['slug']: r for r in locals_}
    # 声明上游表（r263）：一次装载，逐件查表。表里没有 = 没声明；有 = 必须显形且禁判无对应件。
    DECL_UP = load_declared_upstreams()
    if not args.quiet:
        print('  [UPSTREAM] 声明上游件数 = %d' % len(DECL_UP))
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
    # 量尺口径开关（两个回退开关一次解析，供 score5 与行内现算共用；默认全开）
    use_cap = not args.no_license_cap
    use_body = not args.no_license_body
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

    # ---- 正文证据装载（r262）---------------------------------------------------------
    # 本轮联网 measure_repo 取到的优先（最新）；其余按跟踪包补 => 离线复算与干净克隆也能拿到
    #   R261-6 的结论。包缺失/解析失败 => 具名显形，禁静默退回「只信 API 字段」。
    body_pack = load_body_pack()
    pack_err = (body_pack or {}).get("_error") if body_pack else "missing"
    pack_ok = body_pack is not None and pack_err is None
    pack_stats = {"pack_present": pack_ok, "pack_error": pack_err,
                  "pack_fetched_at": (body_pack or {}).get("fetched_at"),
                  "applied": 0, "still_without_body": 0, "pack_unavailable": 0}
    if pack_ok:
        _pa, _ps, _pu = apply_body_pack(measured, body_pack)
        pack_stats["applied"] = _pa
        pack_stats["still_without_body"] = _ps
        pack_stats["pack_unavailable"] = _pu
        if not args.quiet:
            print("  [LIC-PACK] applied=%d no_evidence=%d pack_unavailable=%d" % (_pa, _ps, _pu))
    elif use_body and not args.quiet:
            print("  [LIC-PACK] UNAVAILABLE (%s) => NOASSERTION repos stay unknown" % pack_err)

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
            # use_body / use_cap 在循环外定义（score5 与行内 license_class 必须同一口径，
            #   两处各算一次而口径不同 = 落盘档与得分档互相打脸）。
            s, tot, fc_cal = score5(m, use_cap, use_body)
            scored.append({"repo": c["full_name"], "rel": rel, "rel_strength": rstrength,
                          "fc_caliber": fc_cal,
                          # 许可档现算落盘（与 score5 同一函数 = 单一口径；不从 s 里取，见 score5 注）。
                          # r262：正文档参与（body 优先，见 license_class），并单列 provenance 字段，
                          #   免得读数的人以为 license_class 只来自 API 字段。
                          "license_class": license_class(m.get("license"),
                                                        m.get("license_body_class") if use_body else None),
                          "license_body_class": m.get("license_body_class"),
                          "license_body_spdx": m.get("license_body_spdx"),
                          "license_evidence": m.get("license_body"),
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
        # ---- §3.1 维护状态过滤（r260 机制化）----
        # 位置就是这条判据的全部意义：必须在 sort 与 verdict 之前，且 skill_n 必须按**过滤后**
        # 的集合算，否则 MATCHED/FAMILY_ONLY 的分档仍把停摆仓算成有效候选（假 MATCHED）。
        # --no-maintenance-trim 是回滚开关（红线4 回滚预案要求：机制化必须同时给不改数据的退路）。
        trimmed = []
        unknown_field = 0
        if args.no_maintenance_trim:
            kept_scored = scored
        else:
            kept_scored = []
            for x in scored:
                why = maintenance_trim(x, EVAL_DATE)
                if why is None:
                    if not str(x.get("pushed_at") or "")[:10]:
                        unknown_field += 1        # 缺字段不判违规，只显形（R247）
                    kept_scored.append(x)
                else:
                    trimmed.append({"repo": x["repo"], "reason": why,
                                    "pushed_at": x.get("pushed_at"),
                                    "archived": bool(x.get("archived")),
                                    "rel": x.get("rel"), "score_total": x.get("score_total")})
        scored = kept_scored
        scored.sort(key=lambda x: (bucket_of(x), -x["score_total"]))
        skill_n = sum(1 for x in scored if x["rel"] == "skill")
        top = [x for x in scored if x["rel"] == "skill"][:5]
        if len(top) < 3:
            top = top + [x for x in scored if x['rel'] != 'skill'][:5 - len(top)]
        # 声明上游表查询必须**在裁决链之前**（r263 首版放在链后，护栏引用它时尚未赋值 = NameError;
        #   静态 AST 检查抓不到这种顺序错，只有真跑才暴露）。'表里没有' 与 '进了候选面没' 是两件事，
        #   分开记，免得下游把「已声明但未被匹配」读成「没声明」。
        _up = DECL_UP.get(slug)
        _up_in_face = bool(_up and any((c.get('repo') == _up) for c in top))
        if fid == 'OTHER':
            verdict = "UNVERIFIED"
            note = "未命中任何族规则 ⇒ 具名列出（禁静默算作已覆盖）"
        elif not scored and trimmed:
            # r260 新增分支：过滤后清空**不等于**取数失败。两种成因必须分开报，否则
            # 「全被 §3.1 剔掉」会被下游读成「GitHub 取数挂了」（措辞错=归因错，#32 同族）。
            verdict = "UNVERIFIED"
            # 多段隐式拼接必须整体括起来：写成 note = "A"\n "B" % (...) 时第二行会被当新语句（IndentationError）。
            note = ("候选全部被 §3.1 维护状态剔除（%d 例：archived %d / 停摆 %d）⇒ 该行需重检，"
                    "不得读成开源侧无件，也不得读成取数失败"
                    % (len(trimmed), sum(1 for t in trimmed if t["reason"] == "archived"),
                       sum(1 for t in trimmed if t["reason"] == "stale_pushed_at")))
        elif not scored:
            verdict = "UNVERIFIED"
            note = "候选仓全部取数失败 ⇒ 禁读成无替代（R247）"
        elif skill_n >= 3:
            verdict = "MATCHED"
            note = ""
        elif skill_n == 0 and ps['pool_n'] > 0 and _up:
            # r263（R261-5）：本件声明了上游 ⇒ 「开源侧无对应件」这句被事实证伪（实测 gstack：
            #   判 NO_OS_CANDIDATE 而其上游 garrytan/gstack 有 138k stars）。禁判该态，改记未取证。
            verdict = 'UNVERIFIED'
            note = ('声明上游 %s 存在但未被族级相关性规则匹配进候选面 => 禁判「无对应件」，'
                    '须以该上游为准走人读或上游面核对（R261-5）' % _up)
        elif skill_n == 0 and ps['pool_n'] > 0:
            verdict = 'NO_OS_CANDIDATE'
            note = ('族池 %d 仓、试过关键词 %s，无一命中 => 开源侧无对应件（本件无声明上游）'
                    % (ps['pool_n'], ','.join(ps['tokens'][:6]) or '（空）'))
        else:
            verdict = "FAMILY_ONLY"
            note = "仅族级候选命中（skill 词命中 %d 个），如实降档" % skill_n
        # r261：许可风险行内显形。cap 只压分数、压不动分桶（桶是硬前置：r114 定「桶只答是不是
                #   同类、桶内才比质量」）⇒ 实测残余 2 行 copyleft 仍坐 rank0（rel_strength=20 压过
        #   total 更高的 permissive 对手）。**不改排序**：重排会二次扰动本轮 13 次 rank0 翻转
        #   与既有证据链，且等于用分数覆盖身份判断。改为把风险 + 具名的可合入替代一起交给
        #   C2 人读腿（那才是决策位），让风险机器可见而不是被静默推荐。
        _r0 = (top or [None])[0]
        # 行内现算必须与 score5 同一口径（含正文档）：两处各自调用而参数不同，
        #   落盘的 license_class 与 compat 得分就会互相打脸（r262 自查抓到）。
        _r0lic = license_class(_r0.get("license"),
                               _r0.get("license_body_class") if use_body else None) if _r0 else None
        # restricted 与 copyleft 同级（cap=1）⇒ 必须一并计入风险面，否则正文证明的非商业/需商用
        #   仓会「拿了 copyleft 的分却不在风险清单里」= 显形面漏一档。
        _risky = _r0lic in ("copyleft", "weak-copyleft", "restricted")
        _perm = [c["repo"] for c in top
                 if c is not _r0 and license_class(
                     c.get("license"), c.get("license_body_class") if use_body else None) == "permissive"]
        tally[verdict] += 1
        rows.append({"slug": slug, "family": fid, "family_name": fam_name.get(fid, "未归族"),
                     "local_bytes": lf[slug].get("local_bytes"),
                     "local_desc_len": lf[slug].get("desc_len"),
                     "keywords": ps["tokens"][:8],
                     "dropped_tokens": ps["dropped"][:8],
                     "family_pool_n": ps["pool_n"],
                     "candidates_n": len(top), "skill_relevant_n": skill_n,
                     "candidates": top, "verdict": verdict, "note": note,
                     # 审计面（§3.1 要求「剔除并具名登记」）：谁被剔、为什么剔、因缺字段而放过几例，
                     # 全部逐件落进矩阵行 —— 只在面级给个总数就等于没登记。
                     "maintenance_trimmed": trimmed,
                     "maintenance_trim_n": len(trimmed),
                     "maintenance_unknown_field_n": unknown_field,
                     # 许可面（r261）：分母 = 该行**已发出**的 top-5 候选，不是剔前全池 ——
                     #   R260-9 纪律：引用必须点名分母，否则与「全池 82 例」互相打脸。
                     "rank0_license_class": _r0lic,
                     "license_risk": bool(_risky),
                     "permissive_alternatives_emitted": _perm,
                     # 声明上游面（r263，R261-5）：repo 具名 + 是否真进了发出的候选面。
                     # 两者分开记：表里没有 = 没声明；声明了但 in_face=False = 被族级规则挡在外面，
                     # 那种情形禁判「开源侧无对应件」（裁决链里同一个 _up 已护栏）。
                     "declared_upstream_repo": _up,
                     "declared_upstream_in_face": _up_in_face})

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
        # §3.1 面级汇总（逐件审计在 rows[].maintenance_trimmed，这里只给总量与开关态）
        "maintenance_face": {
            "rule_source": "04-plan/后续维护规范_季度巡检机制_r113_2026-10-18.md §3.1",
            "eval_date": EVAL_DATE.strftime("%Y-%m-%d"),
            "threshold_date": (EVAL_DATE - timedelta(days=TWELVE_MONTHS_DAYS)).strftime("%Y-%m-%d"),
            "enabled": not bool(args.no_maintenance_trim),
            "trimmed_total": sum(r.get("maintenance_trim_n") or 0 for r in rows),
            "archived_total": sum(1 for r in rows for t in (r.get("maintenance_trimmed") or [])
                                  if t["reason"] == "archived"),
            "stale_total": sum(1 for r in rows for t in (r.get("maintenance_trimmed") or [])
                               if t["reason"] == "stale_pushed_at"),
            "unknown_field_total": sum(r.get("maintenance_unknown_field_n") or 0 for r in rows),
            "rows_affected": sum(1 for r in rows if (r.get("maintenance_trim_n") or 0) > 0),
            "verdict_shift": "过滤在 skill_n 之前生效 ⇒ MATCHED/FAMILY_ONLY 分档按剔后计数"},
        # 许可面子腿（r261 立 R260-1）。分母一律写清楚（R260-9）：
        #   slots_emitted = 各行已发出的 top-5 候选（≠ 剔前全池）；
        #   rank0_* = 行级（分母 191）；cap 开关关掉时全部回到 r260 前的二值行为。
        "license_face": {
            "rule_source": "07 台账 R113-3 自决口径 + R260-1 待办（compat 缺许可风险子腿）",
            "caps": LICENSE_CAPS,
            "enabled": not bool(args.no_license_cap),
            "slots_emitted": len(_cand_all),
            "slots_by_class": {k: sum(1 for c in _cand_all
                                      if license_class(c.get("license"),
                                                             c.get("license_body_class")
                                                             if use_body else None) == k)
                               # restricted 必须在名单里：漏了它 = 新档在面级统计里隐身，
                               #   读数的人以为它不存在（门也失去牙）。
                               for k in ("copyleft", "weak-copyleft", "restricted", "permissive",
                                         "unknown", "none")},
            "rows_at_max": sum(1 for r in _cand_all if r["score5"]["compat"] == 5),
            "body_evidence": {
                "enabled": use_body,
                "candidates_with_body_class": sum(1 for c in _cand_all if c.get("license_body_class")),
                "restricted_by_body": sum(1 for c in _cand_all
                                          if c.get("license_body_class") == "restricted"),
                "api_said_noassertion": sum(1 for c in _cand_all
                                            if (c.get("license") or "") == "NOASSERTION"),
                "note": "restricted = 正文证明的非商业/需商业授权/带额外条件；API 字段一律报 NOASSERTION"
                        "（R261-6 两例：langgenius/dify=modified-Apache+多租户需商用、"
                        "Imbad0202/academic-research-skills=CC BY-NC 4.0）",
            },
            "rows_risky_rank0": sum(1 for r in rows if r.get("license_risk")),
            "risky_rank0_rows": [r["slug"] for r in rows if r.get("license_risk")],
            "why_rank0_may_stay_risky":
                "cap 只压分数；分桶是硬前置（rel_strength 决定桶）⇒ 身份更强的 copyleft 仓仍可占 rank0。"
                "本件不重排（重排会二次扰动 rank0 翻转与证据链），改由 license_risk + "
                "permissive_alternatives_emitted 两字段把风险与具名替代交给 C2 人读腿决策。",
        },
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
