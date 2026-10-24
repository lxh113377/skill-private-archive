# -*- coding: utf-8 -*-
"""r209_route_truth_measure.py — 路由真值测量器（r209，零外网，只读焚诀 eval）。

为什么需要它（第 88 门自己的窟窿）：第 88 门用「探针词在 SKILL.md 前 CORPUS_CHARS 字符内」
当「会被召回」的代理判据。本轮实跑 unified_router 证伪了这个蕴含关系：
  Q1 用 win-toolchain-pitfalls 自己 description 的原词（即语料本体，必然在窗口内）查询
     -> top1=commit-archaeologist，win-toolchain **连 top-5 都没进**
  Q3「post-commit 钩子推送失败 || true 吞掉 零留痕」 -> win-toolchain 排第 2（未夺冠）
  另测 chaoshi-web-deploy description 原词 -> top1=chaoshi-web-deploy、direct_hit=True、score=1.0
     —— 它过的是 L0.1 直连正则表（eval/direct_map.json），与 BGE 窗口无关
⇒ 窗口命中只是**入场券**（必要非充分）；真正决定召回的是 ① 直连表有没有它的 pattern
   ② BGE 相对同域技能的名次（keyword 分量权重明显） ③ Top-3 并列时交给 LLM 兜底。

本件是**测量器**：把路由真值落盘，判据（第 88 门）只读件不实跑 —— 与
r200_probe_cost_measure.py → r200_probe_cost_face.py 同一范式。理由：router 单次
1–7 s（BGE onnx 冷启动），每轮门里实跑会拖慢全量且把判据绑死在焚诀可用性上。

查询取自 06-benchmark/recall_probe_registry.json 每条的 query 字段（不另立第二份清单）。
红线6：焚诀 eval 只读调用，不改任何派生件。
"""
import argparse
import io
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
EV = "C:/Users/37533/Desktop/workspace/\u711a\u8bc0/eval"
ROUTER = os.path.join(EV, "unified_router.py")
PROBES = os.path.join(ROOT, "06-benchmark", "recall_probe_registry.json")
DEC = json.JSONDecoder()


def route(query, timeout=420):
    """跑一次 router --json，返回 (top1, 是否直连, 候选名次表, 备注)。

    router 在 JSON 之后还打日志行，故必须 raw_decode（整串 json.loads 报 Extra data，
    本轮踩过：一度把这当成 router 的错）。"""
    env = dict(os.environ, NO_COLOR="1",
               PYTHONPYCACHEPREFIX=os.environ.get(
                   "PYTHONPYCACHEPREFIX", os.path.join(os.environ.get("TEMP", "/tmp"), "pyc_route")))
    p = subprocess.run([sys.executable, ROUTER, "--json", query], cwd=EV,
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=timeout, env=env)
    txt = (p.stdout or "") + (p.stderr or "")
    i = txt.find("{")
    if i < 0:
        return None, None, [], "无 JSON 输出（rc=%s）%s" % (p.returncode, txt[:70])
    try:
        d, _ = DEC.raw_decode(txt[i:])
    except Exception as e:
        return None, None, [], "JSON 解析失败 %s" % str(e)[:60]
    cands = []
    for c in (d.get("candidates") or []):
        sd = c.get("score_details") or {}
        cands.append({"name": c.get("name"),
                      "score": round(float(c.get("score") or 0), 4),
                      "keyword": round(float(sd.get("keyword") or 0), 4)})
    return (d.get("top1"), d.get("direct_hit"), cands, (d.get("llm_reason") or "")[:60])


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", dest="out",
                    default=os.path.join("06-benchmark", "route_truth_latest.json"))
    ap.add_argument("--top", type=int, default=8)
    args = ap.parse_args(argv)
    if not os.path.isfile(ROUTER):
        print("[ROUTETRUTH:UNVERIFIED] router 不可达：%s" % ROUTER)
        return 2
    if not os.path.isfile(PROBES):
        print("[ROUTETRUTH:UNVERIFIED] 探针名册缺失")
        return 2
    reg = json.load(io.open(PROBES, encoding="utf-8"))
    rows = []
    for item in reg.get("probes", []):
        q = (item.get("query") or "").strip()
        skill = item.get("skill", "")
        if not q:
            rows.append({"skill": skill, "topic": item.get("topic"), "error": "名册无 query 字段"})
            continue
        t0 = time.time()
        top1, dh, cands, note = route(q)
        rank = next((k + 1 for k, c in enumerate(cands) if c["name"] == skill), None)
        rows.append({"skill": skill, "topic": item.get("topic"), "query": q,
                     "top1": top1, "direct_hit": dh, "rank_of_skill": rank,
                     "candidates": cands[: args.top], "llm_reason": note,
                     "elapsed_s": round(time.time() - t0, 1)})
        print("  %-24s top1=%-24s direct=%s rank=%s %.1fs"
              % (skill[:24], str(top1)[:24], dh, rank, time.time() - t0))
    # 第三层（r210 一手）：真实任务语句的召回率。名册工具一旦有了承载 skill，
    # 决定「下次会不会被想起」的是**用户/我会说出的那句任务话**，不是 skill 的术语。
    # r210 实测 8 条有名册归属的任务查询里只有 3 条把预期件排进前 3（查 D1 额度 top1=
    # wps-knowledgebase；开 R2 桶 top1=libreoffice-headless-win；Workers 调用量 top1=
    # chaoshi-image-optimization；加 Turnstile top1=codebuddy-chat-web；Actions 分钟
    # top1=chaoshi-web-deploy）—— 即「搭配对了但路由认不出来」。
    tasks = []
    for item in reg.get("task_probes", []):
        q = (item.get("query") or "").strip()
        want = item.get("want") or ""
        if not q:
            continue
        t0 = time.time()
        top1, dh, cands, note = route(q)
        names = [c["name"] for c in cands[:3]]
        if not want:
            outcome = "UNOWNED"
        elif item.get("expect") == "disputed":
            # r211：want 本身存疑（如「Turnstile 已按用户要求移除」，只留事实记录、非接入
            # 教程）⇒ 不判召回，但仍记 top1/top3 供观察。此前我只在名册写了 expect 字段、
            # 两处都不读 = 「写了没人读」的装饰，正是第 88 门立起来要防的那族。
            outcome = "DISPUTED"
        elif dh and top1 == want:
            outcome = "HIT_DIRECT"
        elif want in names:
            outcome = "HIT"
        else:
            outcome = "MISS"
        tasks.append({"task": item.get("task"), "want": want, "query": q, "top1": top1,
                      "direct_hit": dh, "top3": names, "outcome": outcome,
                      "elapsed_s": round(time.time() - t0, 1)})
        print("  [task] %-16s want=%-24s top1=%-26s => %s" % (
              str(item.get("task"))[:16], (want or "-")[:24], str(top1)[:26], outcome))
    judged = [x for x in tasks if x["want"] and x["outcome"] != "DISPUTED"]
    hits = sum(1 for x in judged if x["outcome"] in ("HIT", "HIT_DIRECT"))
    doc = {"schema": "route-truth-v2", "readonly": True, "router": ROUTER,
           "measured_at": time.strftime("%Y-%m-%d %H:%M:%S"), "rows": rows,
           "tasks": tasks, "task_judged": len(judged), "task_hits": hits,
           "task_note": ("第三层召回率：真实任务语句能否把预期承载件带进前 3。HIT_DIRECT=走 L0.1 "
                         "直连表；MISS=召不回（不代表知识不存在，代表入口没有）"),
           "note": ("路由真值：窗口命中只是入场券（必要非充分）。rank_of_skill=null 表示"
                    "该 skill 未进 router 返回的候选前列 —— 即实测召不回。"),
           "provenance_cmd": "python 05-exec/r209_route_truth_measure.py --json <件>"}
    op = args.out if os.path.isabs(args.out) else os.path.join(ROOT, args.out)
    with io.open(op, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    print("[ROUTETRUTH:OK] %d 条主题真值 + %d 条任务召回（命中 %d）落盘 -> %s"
          % (len(rows), len(judged), hits, args.out))
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())
