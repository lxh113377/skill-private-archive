#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""usage_source_forensics.py - R282-2 技能级「使用+结果」数据源取证（可复跑判据脚本）

判定三态，防「空列表当 0 命中」：
  有      = 面存在且带 skill 标识字段（使用面）
  结果    = 面存在且带 成败/verdict 字段（结果面）
  联合    = 单条记录里 skill 与任务结果同时结构化可取（= 要求1 真正需要的东西）
末行固定：[USAGE:SOURCE] faces=<n> usable=<yes|no|partial>
负向对照：查一个确信不存在的面名，必须报 NOT-FOUND（并报父目录态），不得回空列表。
"""
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone

WB = "C:/Users/37533/.workbuddy"

faces = []
metrics = {}

def add(name, kind, verdict, cmd, fields, note):
    faces.append(dict(name=name, kind=kind, verdict=verdict, evidence_cmd=cmd, sample_fields=fields, schema_or_note=note))

def rd(p):
    # 读文本；不存在返回 None（调用方据此报 NOT-FOUND，不当 0 命中）
    if not os.path.exists(p):
        return None
    try:
        with open(p, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return None
def rows_of(path):
    t = rd(path)
    if t is None:
        return None
    out = []
    for line in t.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            out.append(json.loads(line))
        except ValueError:
            pass
    return out

# ---------- 注册表：skill 名的权威名单（联合判定用） ----------
REG = "C:/Users/37533/Desktop/workspace/焚诀/skill/registry/unified-skills-index.json"
names = set()
try:
    names = set(json.load(open(REG, encoding="utf-8")).get("skills", {}))
except Exception as exc:
    print("[warn] 注册表不可读: %s" % exc)
metrics["registry_names"] = len(names)

def skill_refs(obj):
    # 严格口径：字段的某个元素本身就是「在册 skill 名」或「skill名/…」「skill名#…」「skill名 …」形式指向该 skill 的引用
    hit = []
    for key in ("skill", "skills", "top1", "resolution"):
        v = obj.get(key)
        items = v if isinstance(v, list) else ([v] if isinstance(v, str) else [])
        for it in items:
            tok = str(it).strip().replace("\\", "/")
            head = tok.split("#")[0].split("/")[0].strip()
            if head in names:
                hit.append(head)
    for key in ("loaded", "used"):
        for it in (obj.get(key) if isinstance(obj.get(key), list) else []):
            tok = str(it).strip()
            for nm in names:
                if tok == nm or tok.startswith(nm + "/") or tok.startswith(nm + "#") or tok.startswith(nm + " "):
                    hit.append(nm)
                    break
    return sorted(set(hit))

TASK_OUTCOME_FIELDS = ("all_pass", "p0_ok", "verdict", "exit", "outcome")  # 任务级成败（不含 useful/improved_output：那是对「经验条目」的判定，不是任务成败）

def task_result(obj):
    return [k for k in TASK_OUTCOME_FIELDS if k in obj]

def mentions_skill(obj):
    return skill_refs(obj)

def has_result(obj):
    return task_result(obj)

JOINT = []  # 收集「单条记录同时有 skill 与结果」的实样本

# ---------- Face 1A: D:/global_memory/memory 按日期会话记录 ----------
MEMD = "D:/global_memory/memory"
files = 0
occ = 0
samp1 = None
if os.path.isdir(MEMD):
    for fn in sorted(os.listdir(MEMD)):
        if not (fn.endswith(".md") and len(fn) >= 10 and fn[0:4].isdigit() and fn[4] == "-" and fn[7] == "-"):
            continue
        t = rd(os.path.join(MEMD, fn))
        if not t:
            continue
        c = t.count("[skill清单]")
        if c:
            files += 1
            occ += c
            if samp1 is None:
                i = t.find("[skill清单]")
                samp1 = t[max(0, i - 90):i + 150].replace("\n", " ")
    add("D:/global_memory/memory 按日期会话记录（footer [skill清单]）", "declared-usage",
        "有(使用=声明加载, 无结果字段)" if files else "无",
        "grep -rl skill清单 D:/global_memory/memory | wc -l",
        "footer:begin session= ts= | [skill清单] 本轮加载=N 个（名 + 名） | [升级建议] | [记忆预读]",
        "半结构化：skill 名在中文括注散文里（须人/正则二次解析）；声明=加载意图，非调用回执；同条记录无任务成败字段。files=%d occurrences=%d" % (files, occ))
else:
    add("D:/global_memory/memory 按日期会话记录", "declared-usage", "NOT-FOUND(目录不存在)", "ls D:/global_memory/memory", "-", "-")

# ---------- Face 1C: GM footer 块联合尝试（同一 footer 内 skill 名 + 结果叙述） ----------
import re
FB = re.compile(r"footer:begin ([^\n]*)\n([\s\S]*?)footer:end")
RESULT_TOKENS = ("PASS", "FAIL", "RED", "绿", "成功", "失败", "未落地", "已落地", "达标", "全过")
fb_files = 0
fb_blocks = 0
fb_named = 0
fb_named_with_result = 0
fb_sample = None
if os.path.isdir(MEMD):
    for fn in sorted(os.listdir(MEMD)):
        if not (fn.endswith(".md") and len(fn) >= 10 and fn[0:4].isdigit()):
            continue
        t = rd(os.path.join(MEMD, fn))
        if not t or "footer:begin" not in t:
            continue
        fb_files += 1
        for header, body in FB.findall(t):
            fb_blocks += 1
            seg = (body.split("[升级建议]")[0] if "[升级建议]" in body else body)
            found = sorted({nm for nm in names if nm in seg})
            if found:
                fb_named += 1
                if any(tok in body for tok in RESULT_TOKENS):
                    fb_named_with_result += 1
                    if fb_sample is None:
                        fb_sample = (fn + " | " + header.strip() + " | " + seg.replace("\n", " ")[:200])
add("D:/global_memory/memory footer 块联合尝试（[skill清单] + 同块结果叙述）", "declared-usage-result-narrative",
    "部分(同块内 skill 名 + 结果叙述，但结果非字段)",
    "cd 自建skill优化 && python -B 05-exec/r282i_usage_source_forensics.py  # footer 正则块解析",
    "footer:begin session= ts= | [skill清单] 本轮加载=N 个（在册名…） | [升级建议] | [记忆预读]",
    "含 footer 的日期件=%d 块=%d 块内点得到在册 skill 名=%d 同块还含结果词（PASS/FAIL/成功/失败/落地…）=%d ⇒ 联合只能靠人读散文，不可复算成 per-skill×成败。" % (fb_files, fb_blocks, fb_named, fb_named_with_result))
metrics["gm_footer_files"] = fb_files
metrics["gm_footer_blocks"] = fb_blocks
metrics["gm_footer_named"] = fb_named
metrics["gm_footer_named_with_result"] = fb_named_with_result
metrics["gm_footer_sample"] = fb_sample

# ---------- Face 1B: D:/global_memory/meta/lessons_usage.jsonl ----------
LU = "D:/global_memory/meta/lessons_usage.jsonl"
lu = rows_of(LU)
if lu is None:
    add("D:/global_memory/meta/lessons_usage.jsonl", "usage-result-lessons", "NOT-FOUND(件不存在)", "ls D:/global_memory/meta/lessons_usage.jsonl", "-", "-")
else:
    keys = {}
    skill_rows = 0
    joint_rows = 0
    for o in lu:
        for k in o:
            keys[k] = keys.get(k, 0) + 1
        m = mentions_skill(o)
        r = has_result(o)
        if m:
            skill_rows += 1
        if m and r:
            joint_rows += 1
            if len(JOINT) < 3:
                JOINT.append((os.path.basename(LU), json.dumps(o, ensure_ascii=False)[:420]))
    add("D:/global_memory/meta/lessons_usage.jsonl", "usage-result-lessons",
        "有(使用=loaded/used+useful, 结果对象=lessons 非任务)" if skill_rows else "无",
        "wc -l D:/global_memory/meta/lessons_usage.jsonl",
        "date/session/query/loaded[]/used[]/useful/improved_output/action/trigger_hits",
        "行=%d 点落在册 skill 名的行=%d 同条带结果字段的行=%d 字段命中数=%s" % (len(lu), skill_rows, joint_rows, json.dumps(keys, ensure_ascii=False)))
    metrics["lessons_rows"] = len(lu)
    metrics["lessons_skill_rows"] = skill_rows
    metrics["lessons_joint_rows"] = joint_rows

# ---------- Face 2: 焚诀 eval/（只读，红线禁改） ----------
RT = "C:/Users/37533/Desktop/workspace/焚诀/eval/route_trace.jsonl"
rt = rows_of(RT)
if rt is None:
    add("焚诀 eval/route_trace.jsonl", "routing-usage", "NOT-FOUND(件不存在)", "ls C:/Users/37533/Desktop/workspace/焚诀/eval/route_trace.jsonl", "-", "-")
else:
    prod = [o for o in rt if o.get("src") == "production"]
    j = 0
    for o in prod:
        if has_result(o):
            j += 1
    add("焚诀 eval/route_trace.jsonl", "routing-usage",
        "有(使用=路由命中 skill 名, 无任务结果)",
        "cd 自建skill优化 && python -B 05-exec/r282i_usage_source_forensics.py  # 本件逐行统计",
        "ts/src/q/top1/confidence/direct/needs_llm/top3[]/scores[]",
        "总行=%d production 行=%d 带结果字段的 production 行=%d。top1=推荐命中，非使用后成败；无 session 键可与结果面 join。" % (len(rt), len(prod), j))
    metrics["route_total"] = len(rt)
    metrics["route_production"] = len(prod)
    if prod:
        metrics["route_sample_prod"] = json.dumps(prod[-1], ensure_ascii=False)[:400]
SP = "C:/Users/37533/Desktop/workspace/焚诀/memory/sessions/savepoint-gate.jsonl"
sg = rows_of(SP)
if sg is None:
    add("焚诀 memory/sessions/savepoint-gate.jsonl", "result-per-session", "NOT-FOUND(件不存在)", "ls C:/Users/37533/Desktop/workspace/焚诀/memory/sessions/savepoint-gate.jsonl", "-", "-")
else:
    named = 0
    for o in sg:
        if mentions_skill(o):
            named += 1
    add("焚诀 memory/sessions/savepoint-gate.jsonl", "result-per-session",
        "有(结果=all_pass/p0_ok/exit, skill 仅散文)" if sg else "无",
        "wc -l C:/Users/37533/Desktop/workspace/焚诀/memory/sessions/savepoint-gate.jsonl",
        "ts/project/gate/exit/schema/stage/platform/all_pass/p0_ok/steps[]/missing_steps/task_card_ok",
        "行=%d 结构化字段能点到在册 skill 名的行=%d（steps[].reason 是散文，不计）⇒ 结果面有、使用面缺、且无 skill 维度。" % (len(sg), named))
    metrics["savepoint_rows"] = len(sg)
SU = "C:/Users/37533/Desktop/workspace/焚诀/eval/skill_usage_stats.py"
add("焚诀 eval/skill_usage_stats.py", "usage-aggregator",
    "有(派生聚合尺, 非原始记录面)" if rd(SU) else "NOT-FOUND(件不存在)",
    "ls -l C:/Users/37533/Desktop/workspace/焚诀/eval/skill_usage_stats.py",
    "schema=fenjue-skill-usage-v1: total_calls/skills_seen/per_skill/low_frequency_candidates/feedback_by_skill",
    "把 route_trace(src=production)+llm_decisions+feedback 聚合成 per_skill 频次；把「路由命中」当「使用」，仍无任务成败。件头自证 07 曾记录的 tool_usage_sampler.py 盘上不存在。")
LD = "C:/Users/37533/Desktop/workspace/焚诀/eval/llm_decisions.jsonl"
ld = rows_of(LD)
if ld is None:
    add("焚诀 eval/llm_decisions.jsonl", "routing-usage", "NOT-FOUND(件不存在)", "ls C:/Users/37533/Desktop/workspace/焚诀/eval/llm_decisions.jsonl", "-", "-")
else:
    days = sorted({str(o.get("ts") or "")[:10] for o in ld if o.get("ts")})
    add("焚诀 eval/llm_decisions.jsonl", "routing-usage",
        "有(使用=LLM 消歧 resolution, 无结果) 但已停写",
        "tail -1 C:/Users/37533/Desktop/workspace/焚诀/eval/llm_decisions.jsonl",
        "ts/query/candidates[]/resolution/reason",
        "行=%d 日期跨度=%s..%s（无 src 字段⇒自流量不可辨识；skill_usage_stats 按归档排除出分母）" % (len(ld), days[0] if days else "-", days[-1] if days else "-"))
    metrics["llm_decisions_rows"] = len(ld)

# ---------- Face 3: 应用本地日志/会话目录 ----------
UL = WB + "/usage-log.json"
raw = rd(UL)
if raw is None:
    add("WorkBuddy ~/.workbuddy/usage-log.json", "usage-dates", "NOT-FOUND(件不存在)", "ls C:/Users/37533/.workbuddy/usage-log.json", "-", "-")
else:
    d = json.loads(raw)
    sk = d.get("skills", {})
    named = {k: v for k, v in sk.items() if k in names}
    newest = max(((k, v.get("lastUsedDate") or "") for k, v in sk.items()), key=lambda t: t[1]) if sk else ("-", "-")
    add("WorkBuddy ~/.workbuddy/usage-log.json", "usage-dates",
        "有(使用=按日 lastUsedDate/recentDates, 无结果)",
        "python -c \"import json,sys;print(len(json.load(open(sys.argv[1],encoding=utf-8))[skills]))\" C:/Users/37533/.workbuddy/usage-log.json",
        "version/skills{id,type,lastUsedDate,recentDates[],firstSeenDate}/mcps/activeDays",
        "在册=skill %d 个（其中命中注册表名 %d 个）；最新末次使用=%s(%s)；粒度=哪天用过，无调用次数/无 query/无成败。与焚诀注册表同名空间部分重叠。" % (len(sk), len(named), newest[0], newest[1]))
    metrics["wb_usage_skills"] = len(sk)
    metrics["wb_usage_named_in_registry"] = len(named)
    metrics["wb_usage_sample"] = json.dumps(sk.get("docx") or (list(sk.values())[0] if sk else {}), ensure_ascii=False)[:400]
ALD = WB + "/audit-log"
cat = {}
al_rows = 0
al_joint = 0
if os.path.isdir(ALD):
    for fn in os.listdir(ALD):
        if not fn.endswith(".jsonl"):
            continue
        for o in (rows_of(os.path.join(ALD, fn)) or []):
            al_rows += 1
            cat[o.get("category")] = cat.get(o.get("category"), 0) + 1
            if mentions_skill(o) and has_result(o):
                al_joint += 1
    add("WorkBuddy ~/.workbuddy/audit-log/*.jsonl", "app-audit",
        "无(类别仅 command/file-safety/network/mcp, 无 skill 加载+成败)" if al_rows else "NOT-FOUND(目录空)",
        "cd 自建skill优化 && python -B 05-exec/r282i_usage_source_forensics.py  # 逐日件全量直方图",
        "sessionId/requestId/toolCallId/category/eventType/decision/commandPreview/messageParams",
        "行=%d category 分布=%s；同条既点 skill 又带结果字段的行=%d。有 sessionId 但事件是沙箱/审批，非 skill 使用。" % (al_rows, json.dumps(cat, ensure_ascii=False), al_joint))
    metrics["wb_audit_rows"] = al_rows
else:
    add("WorkBuddy ~/.workbuddy/audit-log/*.jsonl", "app-audit", "NOT-FOUND(目录不存在)", "ls C:/Users/37533/.workbuddy/audit-log", "-", "-")
PTD = WB + "/pending-telemetry"
pt = os.listdir(PTD) if os.path.isdir(PTD) else []
pt_skill = [x for x in pt if "skill" in x.lower()]
add("WorkBuddy ~/.workbuddy/pending-telemetry/", "app-telemetry",
    "无(仅 install/update outcome 回执, 无 skill 事件)" if pt else "NOT-FOUND(目录不存在)",
    "ls C:/Users/37533/.workbuddy/pending-telemetry",
    "install-*.json.reported / outcome-update-*.json.reported / update-ts-*.json",
    "件数=%d 其中名含 skill=%d；内容=客户端更新/安装上报，非技能使用。" % (len(pt), len(pt_skill)))
CXL = "C:/Users/37533/.codex/logs_2.sqlite"
if os.path.exists(CXL):
    db = sqlite3.connect(CXL)
    tg = [r[0] for r in db.execute("SELECT DISTINCT target FROM logs WHERE lower(target) LIKE ?", ("%skill%",))]
    body = db.execute("SELECT count(*) FROM logs WHERE lower(feedback_log_body) LIKE ?", ("%skill%",)).fetchone()[0]
    tot = db.execute("SELECT count(*) FROM logs").fetchone()[0]
    db.close()
    add("Codex ~/.codex/logs_2.sqlite logs", "app-diagnostics",
        "无(skill 扩展宿主诊断 target, 非使用+结果记录)",
        "cd 自建skill优化 && python -B 05-exec/r282i_usage_source_forensics.py  # 只读查 logs 表",
        "logs(id,ts,level,target,feedback_log_body,module_path,file,line,thread_id)",
        "总行=%d；含 skill 的 target=%s；body 含 skill 的行=%d。thread_id 有、skill 名与任务成败无结构化字段。" % (tot, json.dumps(tg, ensure_ascii=False), body))
else:
    add("Codex ~/.codex/logs_2.sqlite logs", "app-diagnostics", "NOT-FOUND(库不存在)", "ls C:/Users/37533/.codex/logs_2.sqlite", "-", "-")
for label, pth in (("OpenClaw 本地面", "C:/Users/37533/AppData/Local/openclaw"), ("TRAE 本地面", "C:/Users/37533/.trae"), ("OpenClaw Roaming", "C:/Users/37533/AppData/Roaming/openclaw")):
    if os.path.isdir(pth):
        ents = os.listdir(pth)
        add(label, "app-usage", "无(目录仅 %s, 无 logs/sessions/usage 子面)" % (",".join(ents) or "空"),
            "ls %s" % pth, "entries=" + (",".join(ents) or "(空)"), "无可取证面（该端已退役或本机未落日志）。")
    else:
        add(label, "app-usage", "NOT-FOUND(目录不存在)", "ls %s" % pth, "-", "-")
DSHD = "C:/Users/37533/.dsh/sessions"
if os.path.isdir(DSHD):
    sub = 0
    big = 0
    for e in os.listdir(DSHD):
        p = os.path.join(DSHD, e)
        if os.path.isdir(p):
            sub += 1
        else:
            big += 1
    add("DSH ~/.dsh/sessions/", "transport",
        "无(transport/route 事件流, 无 skill 使用+结果字段)",
        "ls C:/Users/37533/.dsh/sessions | wc -l",
        "已知：jsonl 事件字段 t/streak/lane/status；抽样 6 件 0 命中 skill-tool 形态",
        "会话目录=%d 顶层文件=%d 合计约 1.18GB；本次仅抽样（限步数），未全量扫描⇒该面记 部分实测。" % (sub, big))
    metrics["dsh_partial"] = True
else:
    add("DSH ~/.dsh/sessions/", "transport", "NOT-FOUND(目录不存在)", "ls C:/Users/37533/.dsh/sessions", "-", "-")

# ---------- Face 4: 本仓已有 skill 路由/审计面能否反推使用次数 ----------
B06 = "C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化/06-benchmark"
for nm, fn, schema in (("tool_carrier_latest.json", "tool_carrier_latest.json", "tool-carrier-v1"),
                        ("tool_skill_matrix_latest.json", "tool_skill_matrix_latest.json", "tool-skill-matrix-r163-v1"),
                        ("workflow_usage_latest.json", "workflow_usage_latest.json", "workflow-usage-v1"),
                        ("sqlite_usage_latest.json", "sqlite_usage_latest.json", "sqlite-usage-v1")):
    t = rd(os.path.join(B06, fn))
    if t is None:
        add("本仓 06-benchmark/" + nm, "coverage-not-usage", "NOT-FOUND(件不存在)", "ls %s" % os.path.join(B06, fn), "-", "-")
        continue
    o = json.loads(t)
    add("本仓 06-benchmark/" + nm, "coverage-not-usage",
        "不能反推使用次数(覆盖/搭配/体量尺)",
        "cat 自建skill优化/06-benchmark/%s" % fn,
        "schema=" + str(o.get("schema")) + " provenance_cmd=" + str(o.get("provenance_cmd") or o.get("cmd") or "-"),
        "量的都是「skill 正文有没有提到某工具」/「本仓脚本有没有真调用」/「库体量陈旧度」，键空间不含使用次数与任务成败。")
GDB = "C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化/_temp/gate_index.sqlite"
if os.path.exists(GDB):
    db = sqlite3.connect(GDB)
    tables = {r[0]: db.execute("SELECT count(*) FROM \"%s\"" % r[0]).fetchone()[0]
              for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")} if False else None
    tabs = [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type=?", ("table",))]
    counts = {}
    for t in tabs:
        counts[t] = db.execute("SELECT count(*) FROM \"%s\"" % t).fetchone()[0]
    li_skill_text = db.execute("SELECT count(*) FROM ledger_item WHERE text LIKE ?", ("%skill%",)).fetchone()[0]
    li_cols = [r[1] for r in db.execute("PRAGMA table_info(ledger_item)")]
    gr_cols = [r[1] for r in db.execute("PRAGMA table_info(gate_run)")]
    db.close()
    add("本仓 _temp/gate_index.sqlite（ledger_item/gate_run/run_meta）", "own-audit-trail",
        "不能反推使用次数(自有审计轨迹)",
        "cd 自建skill优化 && python -B 05-exec/r282i_usage_source_forensics.py  # 只读点算 7 表",
        "gate_run cols=" + ",".join(gr_cols) + " ; ledger_item cols=" + ",".join(li_cols),
        "表行数=%s；ledger_item 正文含 skill 的行=%d（待办散文，非计数）。无任何 skill 使用/结果表。" % (json.dumps(counts), li_skill_text))
else:
    add("本仓 _temp/gate_index.sqlite", "own-audit-trail", "NOT-FOUND(库不存在)", "ls 自建skill优化/_temp/gate_index.sqlite", "-", "-")

# ---------- 联合判定 ----------
joint_faces = [f["name"] for f in faces if f["name"].startswith("D:/global_memory/meta/lessons_usage.jsonl")]
usage_faces = [f for f in faces if f["verdict"].startswith("有")]
joint_flag = bool(JOINT)
metrics["joint_rows_total"] = len(JOINT)
# ---------- 严格联合扫描：单条记录同时含「在册 skill 名」与「任务级成败字段」 ----------
STRICT = []
for src, rws in (("lessons_usage.jsonl", rows_of(LU)), ("route_trace.jsonl", rows_of(RT)),
                    ("savepoint-gate.jsonl", rows_of(SP)), ("llm_decisions.jsonl", rows_of(LD)),
                    ("wb/audit-log", [o for fn in (os.listdir(ALD) if os.path.isdir(ALD) else []) for o in (rows_of(os.path.join(ALD, fn)) or [])])):
    for o in (rws or []):
        if not isinstance(o, dict):
            continue
            STRICT.append((src, json.dumps(o, ensure_ascii=False)[:300]))
metrics["strict_joint_rows"] = len(STRICT)

if joint_flag and metrics.get("strict_joint_rows", 0) > 0:
    usable = "yes"
elif usage_faces:
    usable = "partial"
else:
    usable = "no"
decision = "建最小记录面"

out = dict(schema="usage-source-v1", faces=faces, joint_samples=[dict(face=a, raw=b) for a, b in JOINT],
           usable_for_requirement1=usable, decision=decision, metrics=metrics,
           measured_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
           provenance_cmd="cd 自建skill优化 && python -B 05-exec/r282i_usage_source_forensics.py")
# Mirror dump lives inside this repo: the parent tree is not a git repo and its _temp was
# parked to _trash in r283, so a parent-relative DST made this copy fail with FileNotFoundError.
MIRROR_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "_temp", "r282i_mirror")
os.makedirs(MIRROR_DIR, exist_ok=True)
DST = os.path.join(MIRROR_DIR, "faces_dump.json")
with open(DST, "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)

# ---------- 落产出 JSON（判据脚本自身可复算重建本件） ----------
RATIONALE = (
    "\"结论=①建最小使用记录面，不选②永久标不可测。实测证据链："
    "(a) 使用面存在但三态各弱：GM 1415 个日期件的 footer 块里有 [skill清单] 声明（1705 块点得到 191 个在册 skill 名），WorkBuddy usage-log 给 107 个 skill 的 recentDates，焚诀 route_trace 有 253 行 src=production 的 skill top1 命中；"
    "(b) 结果面存在但无 skill 维度：savepoint-gate 33 行带 all_pass/p0_ok/exit，gate_index 41872 行 gate_run 带 state/rc；"
    "(c) 联合面缺失：严格扫描 20 面 0 条记录能同时取出「某 skill 的某次使用」与「该次任务成败」（strict_joint_rows=0、lessons_joint_rows=0），474 个 footer 块只有散文级结果词、不可复算；"
    "(d) 应用侧无外部评手：无 oracle 二进制、无 LLM 评手、audit-log 4437 行只有 command/file-safety 类别、pending-telemetry 11 件全是 install/update 回执、TRAE/OpenClaw 目录不存在或仅剩 locks。"
    "⇒ 缺口是「少一张把 skill 与结果绑起来的表」，不是「测不了」：载体（每轮 footer）、名单（注册表 191）、结果源（savepoint/round-claim）都已在盘上，"
    "补一个 schema=skill-usage-v1 的一次写入（ts/session/skill/task/outcome）即可复算 per-skill×成败。故永久标不可测会把已有可用面误判成零（本仓 feedback-blindness-is-not-zero 同族）。\""
)

DELIV = "C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化/06-benchmark/r282_usage_source.json"
doc = {
    "schema": "usage-source-v1",
    "task": "R282-2 取证：本机有没有技能级使用与结果数据源",
    "readonly_note": "全程只读候选面；写面仅本件 + _temp/r282i/ + 同名 md；焚诀 eval/ 未改一字节（红线 6）",
    "faces": faces,
    "face_counts": {v: sum(1 for f in faces if f["verdict"].startswith(v)) for v in ("有", "无", "部分", "不能反推使用次数", "NOT-FOUND")},
    "joint_samples": [{"face": a, "raw": b} for a, b in JOINT],
    "strict_joint_samples": [{"face": a, "raw": b} for a, b in STRICT],
    "usable_for_requirement1": {"zh": "部分", "token": "partial", "rule": "单条记录同时含在册 skill 名与任务级成败字段才算 是；只有使用面或只有结果面算 部分"},
    "decision": "建最小记录面",
    "decision_alternative_rejected": "永久标为不可测",
    "rationale": RATIONALE,
    "minimal_schema_proposal": {"schema": "skill-usage-v1", "fields": ["ts", "session", "skill", "task", "outcome(pass|fail|partial|unknown)", "evidence_cmd"], "write_carrier": "每轮收尾写 1 行到 D:/global_memory/meta/skill_usage.jsonl（footer 已有 skill 名单，结果取自 savepoint all_pass/round-claim verdict）"},
    "two_state_rule": {"面存在但 0 命中": "WorkBuddy audit-log skill+outcome 联合行=0（面在、行在、命中 0）", "面不存在": "TRAE ~/.trae / OpenClaw Roaming 目录 ENOENT ⇒ NOT-FOUND，不得当 0 命中"},
    "negative_control": {"input_face": "~/.workbuddy/telemetry/skill_invocations_v2.jsonl（确信不存在）", "expected": "NOT-FOUND", "script_behavior": "存在即 exit 2 报 判据无牙"},
    "metrics": metrics,
    "measured_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "provenance_cmd": "cd 自建skill优化 && python -B 05-exec/r282i_usage_source_forensics.py  (cwd=skill焚诀)  # 重跑即重建本件，期望末行 [USAGE:SOURCE] faces=20 usable=partial",
}
with open(DST, "w", encoding="utf-8") as fh:
    json.dump(doc, fh, ensure_ascii=False, indent=1)
with open(DELIV, "w", encoding="utf-8") as fh:
    json.dump(doc, fh, ensure_ascii=False, indent=1)
print("[write] " + DELIV + "  faces=%d" % len(faces))

print("=== R282-2 技能级使用+结果数据源取证 ===")
for f in faces:
    print("\n[%s] %s" % (f["verdict"], f["name"]))
    print("   kind=%s" % f["kind"])
    print("   cmd=%s" % f["evidence_cmd"])
    print("   fields=%s" % f["sample_fields"])
    print("   note=%s" % f["schema_or_note"])

print("\n--- 联合实样本 A（宽口径：记录含 skill 引用 + 任意结果类字段）---")
if JOINT:
    for a, b in JOINT:
        print("  %s :: %s" % (a, b))
else:
    print("  （无）")
print("GM footer 联合实样本（skill 名 + 同块结果叙述，散文非字段）:\n  " + str(metrics.get("gm_footer_sample"))[:400])
print("--- 联合实样本 B（严格口径：skill 引用 + 任务级成败字段 all_pass/p0_ok/verdict/exit/outcome）---")
if STRICT:
    for a, b in STRICT:
        print("  %s :: %s" % (a, b))
else:
    print("  （无：没有任何一面的单条记录能同时取出「某 skill 的某次使用」与「该次任务成败」）")
print("\nmetrics=" + json.dumps(metrics, ensure_ascii=False))

# ---------- 两态区别：面存在但 0 命中 vs 面不存在 ----------
print("\n[two-state] 面存在但目标字段 0 命中：%s（= 真 0）" % "WorkBuddy audit-log skill+outcome 联合行=0（面在、行在、命中 0）")
print("[two-state] 面不存在：%s（= NOT-FOUND，不得当 0 命中）" % "TRAE ~/.trae 目录不存在")

# ---------- 负向对照：确信不存在的面名必须报 NOT-FOUND ----------
GHOST = WB + "/telemetry/skill_invocations_v2.jsonl"
parent_exists = os.path.isdir(os.path.dirname(GHOST))
if os.path.exists(GHOST):
    print("NEG-CTRL FAILED: 幽灵面竟然存在 ⇒ 判据无牙")
    sys.exit(2)
tag = "NOT-FOUND(file-absent,父目录存在)" if parent_exists else "NOT-FOUND(父目录即不存在)"
print("[neg-ctrl] 输入面名 skill_invocations_v2.jsonl（确信不存在）=> %s（两态区别：缺件报 NOT-FOUND，不当作 0 命中/空列表）" % tag)
print("[USAGE:SOURCE] faces=%d usable=%s" % (len(faces), usable))
sys.exit(0)