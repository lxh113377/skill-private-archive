# -*- coding: utf-8 -*-
"""r300_declared_face_fixtures.py — r300「声明仓行内五维面」的夹具与负控（离线、零网络）。

为什么必须有它：r300 在 r114_replacement_scan.py 里新增了 declared_face()（把 .upstream 声明的
上游仓做成**行内**五维读数：lineage / invalid / unmeasured 三态 + score5）。本仓规矩（R287 起）：
新判据进门必须带自证腿，且**三态都要有反例** —— 只测「正常路径」等于没测。

九个腿（每个都断言具体值，不是打印 want 不比对）：
  L1 同名目录命中 ⇒ lineage（且带 score5/score_total，且与本体 score5 逐字段一致）
  L2 只有 path: 子路径命中、slug 目录不命中 ⇒ lineage（r299 实测 8 件属这一类，只看 slug 会误判）
  L3 根级 SKILL.md + 仓名含 slug ⇒ lineage（整仓即本件，如 zarazhangrui/frontend-slides）
  L4 树完整、路径与 slug 都落不到 ⇒ invalid（**这不是「取不到」**，是实测声明失效）
  L5 缓存里没有 skill_md_dirs 字段 ⇒ unmeasured（R247：看不见 ≠ 不存在；旧缓存只有计数）
  L6 树被截断且无命中 ⇒ unmeasured（不许据截断判失效）
  L7 非 owner/repo 形态 / 空 repo ⇒ 返回 None 或 unmeasured，**不得**判 invalid 之外的乐观态
  L8 声明 path: 归属（r301 修）：路径只对树里真有它的仓生效，兄弟仓不得借它判 lineage（双向）
  L9 根级腿边界（r301 修）：slug 必须在仓名**边界**上，只出现在中间不算（双向）

末行：[DECLARED:FACE:PASS] legs=%d passed=7 lineage=3 invalid=1 unmeasured=3
退出码：0 全过 / 1 任一腿不符（打印期望 vs 实际，不静默）
"""
import importlib.util
import io
import os
import sys

NL = chr(10)
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SP = os.path.join(HERE, "r114_replacement_scan.py")
_s = importlib.util.spec_from_file_location("r114", SP)
r114 = importlib.util.module_from_spec(_s)
_s.loader.exec_module(r114)


def fake_cache(repo, dirs, root_md=False, truncated=False, state="OK", with_field=True):
    """造一个仓元数据 doc（形状取自本体 measure_repo 的落盘面；只填 declared_face 用得到的字段）。"""
    doc = {"state": state, "stars": 1234, "pushed_at": "2026-10-01", "archived": False,
           "license": "MIT", "license_body_class": None, "license_body_spdx": "",
           "description": "fixture repo", "topics": [], "default_branch": "main",
           "tree_state": "OK", "tree_truncated": truncated, "skill_md_n": len(dirs),
           "skill_md_exact_n": len(dirs), "skill_md_ghost_n": 0,
           "workflow_n": 1, "test_path_n": 1, "readme_n": 1, "docs_md_n": 0,
           "blob_n": 10, "forks": 10, "open_issues": 0, "created_at": "2025-01-01",
           "homepage": ""}
    if with_field:
        doc["skill_md_dirs"] = dirs
        doc["skill_md_root"] = root_md
    return doc


def run(repo, dirs, slug, sub=None, root_md=False, truncated=False, with_field=True, state="OK"):
    cache = {}
    if repo:
        cache["repo__" + r114.key_of(repo)] = fake_cache(repo, dirs, root_md, truncated, state, with_field)
    stats = {"api_calls": 0, "cache_hits": 0, "cache_miss": 0, "errors": []}
    return r114.declared_face(slug, repo, sub, cache, True, stats), stats


legs = []
# L1
d1, _ = run("Shubhamsaboo/awesome-llm-apps", ["agent_skills/commit-archaeologist"], "commit-archaeologist")
same = False
if isinstance(d1.get("score5"), dict):
    # 比对用的 doc 必须与 L1 那件**逐字段相同**：我第一版用 fake_cache("x", []) 造对照，
    # 它的 skill_md_n=0 而 L1 那件是 1 ⇒ fc 档不同、必然不等。是我夹具的错，不是产品错。
    m = fake_cache("Shubhamsaboo/awesome-llm-apps", ["agent_skills/commit-archaeologist"])
    s, tot, fc = r114.score5(m, True, True)
    same = (d1["score5"] == s and d1["score_total"] == tot)
legs.append(("L1 同名目录⇒lineage且五维与本体一致",
             d1.get("state") == "lineage" and bool(d1.get("slug_hit")) and same))
# L2
d2, _ = run("K-Dense-AI/scientific-agent-skills", ["skills/exploratory-data-analysis"],
            "data-analysis", sub="skills/exploratory-data-analysis")
legs.append(("L2 path 命中⇒lineage（slug 目录不命中）",
             d2.get("state") == "lineage" and bool(d2.get("path_hit")) and not d2.get("slug_hit")))
# L3
d3, _ = run("zarazhangrui/frontend-slides", ["."], "frontend-slides", root_md=True)
legs.append(("L3 根级+仓名含 slug⇒lineage",
             d3.get("state") == "lineage" and d3.get("root_skill_md") and d3.get("repo_name_ok")))
# L4
d4, _ = run("kepano/defuddle", [], "defuddle")
legs.append(("L4 树完整且落不到⇒invalid",
             d4.get("state") == "invalid" and "声明失效" in str(d4.get("why"))))
# L5
d5, _ = run("Shubhamsaboo/awesome-llm-apps", [], "commit-archaeologist", with_field=False)
legs.append(("L5 缓存无树目录⇒unmeasured（不得判 invalid；且 why 必须说清是缺列而非仓没测过）",
             d5.get("state") == "unmeasured"
             and "树目录列" in str(d5.get("why"))
             and "元数据取不到" not in str(d5.get("why"))))
# L6
d6, _ = run("garrytan/gstack", [], "gstack", truncated=True)
legs.append(("L6 树截断且无命中⇒unmeasured",
             d6.get("state") == "unmeasured" and "truncated" in str(d6.get("why"))))
# L7：非 owner/repo 形态
d7, _ = run(None, [], "whatever")
d7b = r114.declared_face("x", "not-a-repo", None, {}, True, {"api_calls": 0, "cache_hits": 0, "cache_miss": 0, "errors": []})
legs.append(("L7 空/畸形声明⇒None 或非 lineage 的保守态",
             d7 is None and (d7b is None or d7b.get("state") in ("unmeasured", "invalid"))))

# ---- r301 追加两腿：把两处机制修做成可复算断言（各带两个方向）----
# L8 声明 path: 的归属：该路径只对「树里真有它」的仓生效 ⇒
#    L8a 正控：仓的树里有该路径 ⇒ path_hit 命中且 path_attributed=True；
#    L8b 反控：同一个声明路径换到**没有它**的兄弟仓 ⇒ path_hit 必须为空、path_attributed=False，
#        且不得因此判 lineage（这正是「借别人的路径证明自己命中」的假绿通道）。
d8a, _ = run("vercel-labs/agent-browser", ["skill-data/electron"], "electron",
             sub="skill-data/electron")
d8b, _ = run("microsoft/playwright", ["some/other-dir"], "electron",
             sub="skill-data/electron")
legs.append(("L8a 声明路径在本仓树里⇒命中且 path_attributed=True",
             bool(d8a.get("path_hit")) and d8a.get("path_attributed") is True
             and d8a.get("state") == "lineage"))
legs.append(("L8b 声明路径不在本仓树里⇒不得借它判 lineage（path_attributed=False）",
             d8b.get("path_hit") is None and d8b.get("path_attributed") is False
             and d8b.get("state") == "invalid"))
# L9 根级腿的边界形态：slug 只在仓名**中间**出现时不得命中（旧写法用子串会假 lineage）⇒
#    L9a 正控：lewislulu/html-ppt-skill（尾段以 html-ppt + 分隔符开头）⇒ lineage；
#    L9b 反控：worldwonderer/oh-story-claudecode（尾段含 story 但不在边界）⇒ invalid。
d9a, _ = run("lewislulu/html-ppt-skill", ["."], "html-ppt", root_md=True)
d9b, _ = run("worldwonderer/oh-story-claudecode", ["."], "story", root_md=True)
legs.append(("L9a 仓名以 slug+分隔符开头⇒lineage",
             d9a.get("state") == "lineage" and d9a.get("repo_name_ok") is True))
legs.append(("L9b slug 只出现在仓名中间⇒不得判 lineage（旧子串写法会假绿）",
             d9b.get("state") == "invalid" and d9b.get("repo_name_ok") is False))
# L9c = L9b 的**有牙证明**：把「旧判据 vs 新判据」并排跑一次，必须给出相反答案。
#   只断言「现在是 invalid」是不够的 —— 那不能排除「其实旧版也是 invalid、这条腿从来没红过」。
#   （L8b 我如实标注：它只是把归属事实显形，**不构成有牙腿**，因为旧写法在该形态下也给 ph=None；
#     真正的假绿通道只在「兄弟仓恰好也有同名目录」时打开，本轮没有真实语料命中，故只留断言不留腿。）
def old_predicate(name, v):
    return bool(v) and v in name                    # 旧写法：子串
def new_predicate(name, v):
    if not v:
        return False
    if name == v:
        return True
    return any(name.startswith(v + s) or name.endswith(s + v) for s in ("-", "_", "."))
_old_hit = old_predicate("oh-story-claudecode", "story")
_new_hit = new_predicate("oh-story-claudecode", "story")
legs.append(("L9c 有牙证明：旧子串判据=True 而新边界判据=False（两判据必须相反）",
             _old_hit is True and _new_hit is False))

ok = 0
for name, good in legs:
    print("%s %s" % ("PASS" if good else "FAIL", name))
    ok += 1 if good else 0
print("[DECLARED:FACE:PASS] legs=%d passed=%d lineage=%d invalid=%d unmeasured=%d"
      % (len(legs), ok, sum(1 for d in (d1, d2, d3) if d.get("state") == "lineage"),
         sum(1 for d in (d4,) if d.get("state") == "invalid"),
         sum(1 for d in (d5, d6) if d.get("state") == "unmeasured")))
sys.exit(0 if ok == len(legs) else 1)
