# -*- coding: utf-8 -*-
"""_lib.py — 05-exec 可复用工具共用库（2026-09-23 r9 由各脚本重复实现抽取）

背景：stdout UTF-8 包装曾有 5 份逐字拷贝、utf-8-sig JSON 读取 3 份、
BOM/行尾保持读写 2 份**且语义不一致**（repair_lines 旧版不处理 CRLF，
修复过 CRLF 文件会把行尾改写成 LF）——抽到此单一真相源。

  force_utf8_stdout()            stdout 强制 UTF-8（管道/重定向降级不崩）
  load_json(path)                utf-8-sig 读 JSON（BOM 兼容）
  read_text(path)                读文本 → (text_lf, bom, crlf)；CRLF 归一化 LF，
                                 由 write_text 按原行尾整体复原（防 \r\r\n 双重行尾）
  write_text(path, text, bom, crlf)  临时文件 + os.replace 原子写，保持 BOM/行尾
  backup_file(path, backup_dir)  copy2 写前备份（目录不存在则建），返回备份路径
  registry_denominator()         焚诀注册表口径（disk_manifest.json，读不到返回 error 不猜 0）
  denominator(scanned, ...)      技能统计三口径对账（纳入 / 磁盘 glob / 注册表），r19 P1-C 单一真相源
"""
import glob
import json
import os
import shutil
import subprocess
import time
import sys
import re
from datetime import datetime, timedelta


def force_utf8_stdout():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        import io as _io
        try:
            sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        except Exception:
            pass


def load_json(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def read_text(path):
    with open(path, "rb") as f:
        raw = f.read()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    crlf = text.count("\r\n") >= text.count("\n") - text.count("\r\n")
    text = text.replace("\r\n", "\n")
    return text, bom, crlf


def write_text(path, text, bom, crlf):
    if crlf:
        text = text.replace("\n", "\r\n")
    data = text.encode("utf-8")
    if bom:
        data = b"\xef\xbb\xbf" + data
    tmp = os.path.join(os.path.dirname(os.path.abspath(path)), f".tmp_write.{os.getpid()}")
    try:
        with open(tmp, "wb") as f:
            f.write(data)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def backup_file(path, backup_dir):
    os.makedirs(backup_dir, exist_ok=True)
    flat = os.path.abspath(path).replace(":", "").replace("\\", "__").replace("/", "__")
    dest = os.path.join(backup_dir, flat)
    shutil.copy2(path, dest)
    return dest


# ---------------------------------------------------------------------------
# r19 P1-C 分母统一登记（对标 sickn33/agentic-awesome-skills schemas/aas-v1 的
# 「口径契约」思路）。根因：同一件事在本体系有三处口径（r18 报告 N4）——
# 焚诀注册表 167 / 本仓扫描器 166（按设计跳过 junction）/ 历史报告 151。
# 禁再出现「单口径裸数字」：任何技能计数必须三口径并排 + 附取值命令。
# ---------------------------------------------------------------------------

REGISTRY_MANIFEST = os.path.join(
    r"C:\Users\37533\Desktop\workspace\焚诀", "skill", "registry", "disk_manifest.json")
REGISTRY_CMD = (r'python "C:\Users\37533\Desktop\workspace\焚诀\eval\verify_truth_consistency.py"'
                "  # 取 C1 行")


def registry_denominator(manifest_path=None):
    """读焚诀注册表磁盘清单口径。失败时返回 error 字段，禁止用 0 冒充「无技能」。"""
    path = manifest_path or REGISTRY_MANIFEST
    try:
        data = load_json(path)
    except (OSError, ValueError) as e:
        return {"available": False, "error": "%s: %s" % (type(e).__name__, e), "path": path}
    if not isinstance(data, dict):
        return {"available": False, "error": "manifest 非对象（%s）" % type(data).__name__, "path": path}
    count = data.get("count")
    skills = data.get("skills")
    if count is None or not isinstance(skills, list):
        return {"available": False, "error": "缺 count 或 skills 数组", "path": path}
    return {"available": True, "count": count, "skills_len": len(skills),
            "self_consistent": count == len(skills), "schema": data.get("schema"),
            "generated": data.get("generated"), "path": path}


def denominator(scanned, junctions=(), errors=(), glob_total=None, manifest_path=None):
    """三口径对账：本次纳入 / 磁盘 glob / 焚诀注册表。glob 与注册表不等 → 显式判不一致。"""
    if glob_total is None:
        glob_total = scanned + len(junctions) + len(errors)
    reg = registry_denominator(manifest_path)
    d = {"scanned": scanned, "junction_skipped": list(junctions), "parse_errors": len(errors),
         "glob_total": glob_total, "registry": reg,
         "registry_cmd": REGISTRY_CMD}
    if reg.get("available"):
        d["consistent"] = (glob_total == reg["count"])
        d["delta"] = glob_total - reg["count"]
    else:
        d["consistent"] = None
        d["delta"] = None
    return d


def denominator_lines(d):
    """把 denominator() 结果格式化成 stdout/MD 行（缺口径也必须有可见行，禁静默）。"""
    reg = d.get("registry", {})
    lines = ["口径对账: 本次纳入 %d | 磁盘 glob %d（junction 跳过 %d: %s | 解析错误 %d）" % (
        d["scanned"], d["glob_total"], len(d["junction_skipped"]),
        ",".join(d["junction_skipped"]) or "-", d["parse_errors"])]
    if reg.get("available"):
        tag = "一致" if d.get("consistent") else "不一致(Δ=%s)" % d.get("delta")
        lines.append("焚诀注册表口径: count=%s / skills=%s（%s, %s, generated=%s）→ 与磁盘 glob %s" % (
            reg["count"], reg["skills_len"], reg.get("schema"),
            "manifest 自洽" if reg.get("self_consistent") else "manifest 内部分歧",
            reg.get("generated"), tag))
    else:
        lines.append("焚诀注册表口径: 不可用（%s）→ 本表分母仅磁盘 glob，禁止引用为全库分母"
                     % reg.get("error"))
    lines.append("取值命令: %s" % d.get("registry_cmd", REGISTRY_CMD))
    return lines


# ---- gh（GitHub CLI）解析（r163，与第 64 门 gh_path_face 同源口径）-------------
# 存在理由：本机 gh 这个命令名被三方争夺 —— 官方 CLI（Program Files\GitHub CLI）、
# npm 第三方包（D:\npm-global\gh，2.8.9，连 --help 都抛 TypeError 而 rc=0）、
# 以及曾是 0 字节空壳的 C:\Users\37533\.local\bin\gh（r163 已重命名移除）。
# 裸 subprocess.run(["gh", ...]) 在 PATH 序漂移时会静默跑到错的实现上
# ⇒ 取数面一律用 gh_cli() 拿绝对路径。
GH_CANDIDATES = (
    os.path.join(os.environ.get("ProgramFiles", r"C:\\Program Files"),
                 "GitHub CLI", "gh.exe"),
    os.path.join(os.environ.get("ProgramFiles(x86)", r"C:\\Program Files (x86)"),
                 "GitHub CLI", "gh.exe"),
    os.path.expanduser(r"~\\scoop\\shims\\gh.exe"),
)


def gh_cli():
    """返回可用的 gh 可执行文件绝对路径；取不到返回 None（调用方须记 UNVERIFIED）。

    只认存在且非空的官方安装位；不回退裸名 —— 裸名正是被劫持的入口。
    """
    for c in GH_CANDIDATES:
        try:
            if os.path.isfile(c) and os.path.getsize(c) > 0:
                return c
        except OSError:
            continue
    return None


FUTURE_TOLERANCE_SEC = 120  # 卷 mtime 超前当下多少秒即判「基准不可能达成」（容忍 NTP 微漂）

# ---- 账龄件相对新鲜前置再生（r122-1 立，r163 从 run_gates 抽到此处共用）------------
# 为什么抽上来：这份逻辑原先只活在 run_gates._ensure_debt_fresh 里，而**单独直调 ratchet_gate**
#   （以及 r55_note_fixtures / r56_budget_fixtures 这类直调棘轮的夹具）不走 runner ⇒ 件比卷旧时
#   棘轮把 debt 三指标转 unknown，三条夹具腿判红。AGENTS 已知坑第 2 条本轮第 5 次踩。
#   复制一份到 ratchet 会造第二真相源（本仓禁），故抽到共用库，两处同函数同入参。
# 契约：返回 (state, detail)，state ∈ OK / STALE-REGEN / NO-ARTIFACT / NO-VOLUME / REGEN-FAILED。
#   **任何非 OK 都不阻断** —— 本腿是消时序坑，不是新卡点。
def ensure_debt_fresh(repo, exec_dir, sys_executable=None):
    """账龄件相对新鲜前置再生（r122-1 立，r163 从 run_gates 抽到 _lib 共用）。

    连踩 4 轮的根因 = 先跑 r38_debt_aging 后改 07 台账，件比卷旧 ⇒
    `ratchet_gate._debt_artifact_fresh` 把 debt 三指标转 unknown ⇒
    报「指标缺失」+ note fixtures n4 必现 FAIL。

    口径与 ratchet_gate 完全一致（同函数同入参，防两处漂移）：
    卷集 = memory/07-next-steps.md + memory/07-next-steps.part*.md，取最大 mtime；
    件 = 06-benchmark/debt_aging_r*.json 里 mtime 最新那份。件 < 卷 ⇒ 重生一次。

    返回 (state, detail)。state ∈ OK / STALE-REGEN / NO-ARTIFACT / NO-VOLUME /
    REGEN-FAILED。**任何非 OK 都不阻断**（本腿是消时序坑，不是新卡点）。
    """
    import glob as _glob, subprocess as _sp
    vols = _glob.glob(os.path.join(repo, "memory", "07-next-steps.md")) + \
        _glob.glob(os.path.join(repo, "memory", "07-next-steps.part*.md"))
    if not vols:
        return ("NO-VOLUME", "取不到 07 待办卷（memory/07-next-steps*.md）")
    try:
        vol_m = max(os.path.getmtime(v) for v in vols)
    except OSError as e:
        return ("NO-VOLUME", "卷 mtime 取不到：%s" % e)
    arts = _glob.glob(os.path.join(repo, "06-benchmark", "debt_aging_r*.json"))
    if not arts:
        return ("NO-ARTIFACT", "无 debt_aging_r*.json ⇒ 先生成一份")
    # r191 修（R191-2 一手）：此处原先按 **mtime** 选件，而 ratchet_gate._newest_artifact 按
    # 「文件名日期 → 字母序」选件。两套口径 ⇒ 自愈腿判 OK 的那一件，棘轮判据根本不看；
    # 且棘轮看的那份更旧 ⇒ 它永远走 unknown + 重生，自愈则永远认为已 OK，两侧都不自愈。
    # 修法：与 ratchet_gate 同键选件（import 它的实现，不复制第二份）。
    try:
        sys.path.insert(0, exec_dir)
        import ratchet_gate as _rg
        art = _rg._newest_artifact_glob(os.path.join(repo, "06-benchmark", "debt_aging_r*.json"))
    except Exception:
        art = max(arts, key=os.path.getmtime)   # 取不到判据实现时退回 mtime（fail-open 具名）
    if not art:
        return ("NO-ARTIFACT", "选件为空（_newest_artifact 返回 None）")
    try:
        art_m = os.path.getmtime(art)
    except OSError as e:
        return ("NO-ARTIFACT", "件 mtime 取不到：%s" % e)
    if art_m >= vol_m:
        return ("OK", "件 %s 不旧于卷集（差 %.0f 秒）" % (os.path.basename(art), art_m - vol_m))
    # r163 自抓（造陈旧用例时撞出）：卷集 mtime **晚于当下**（时钟漂移，或测试把人造未来戳写进卷）
    #   ⇒ 任何重生出来的件都不可能新于它，稳定落入 STALE-REGEN 且每次白跑两趟 r38（约 2× 耗时）。
    #   这不是「件陈旧」而是「基准不可能达成」，须具名分开，禁混报成重生失败。
    _future = vol_m - time.time()
    if _future > FUTURE_TOLERANCE_SEC:
        return ("FUTURE-VOL", "所测卷集 mtime 晚于当下 %.0f 秒（基准不可能达成）⇒ 不生搬重生；"
                              "先查系统时钟或该卷是否有未来时间戳" % _future)
    # 件比卷旧 ⇒ 重生（r38 自带 --json，输出到带日期的固定名，防并行会话同名互踩）
    # r191 修（R191-2 一手）：stamp 不能只取当前时刻 —— `ratchet_gate._newest_artifact` 的选件键是
    # 「文件名日期 → 同日期比字母后缀 → 按名兜底」，同日候选按**名字字典序**取最大。
    # 若已存在字典序更大的件（如 ..._233000.json），本函数用当前时刻生成的 ..._232040.json
    # 就**永不被选中** ⇒ 自愈白跑（实测：重生后同进程仍读旧件，三指标继续缺失、夹具 g11 判红）。
    # 修法：stamp 取「max(当前时刻, 现有最大 stamp + 1 秒)」，保证新件字典序严格大于一切现存件。
    _existing = []
    for _a in arts:
        _m = re.search(r"debt_aging_r_autoregen_(\d{8}_\d{6})\.json$", os.path.basename(_a))
        if _m:
            _existing.append(_m.group(1))
    _now = datetime.now()
    _stamp = _now.strftime("%Y%m%d_%H%M%S")
    if _existing:
        _mx = max(_existing)
        try:
            _mx_dt = datetime.strptime(_mx, "%Y%m%d_%H%M%S")
            if _stamp <= _mx:
                _stamp = (_mx_dt + timedelta(seconds=1)).strftime("%Y%m%d_%H%M%S")
        except ValueError:
            pass
    stamp = _stamp
    out_json = os.path.join(repo, "06-benchmark", "debt_aging_r_autoregen_%s.json" % stamp)
    try:
        r = _sp.run([(sys_executable or sys.executable), os.path.join(exec_dir, "r38_debt_aging.py"), "--json", out_json],
                     cwd=str(repo), capture_output=True, text=True,
                     encoding="utf-8", errors="replace", timeout=180)
    except Exception as e:
        return ("REGEN-FAILED", "重生调用异常：%s" % e)
    if r.returncode != 0:
        return ("REGEN-FAILED", "重生 rc=%s：%s" % (r.returncode, (r.stderr or "")[-160:]))
    # 复验：新件必须新于卷集（否则说明卷又被 concurrent 写了，如实报）
    try:
        new_m = os.path.getmtime(str(out_json))
    except OSError as e:
        return ("REGEN-FAILED", "新件 mtime 取不到：%s" % e)
    if new_m < vol_m:
        # R124-1（r127 收口）：重生期间卷又被写 ⇒ 再重生一次（上限 2 次防循环）。
        # r127 实测频率低（全程 1 次），重试一次足够覆盖「并行写紧跟」窗口。
        stamp2 = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_json2 = os.path.join(repo, "06-benchmark", "debt_aging_r_autoregen_%s.json" % stamp2)
        try:
            r2 = _sp.run([(sys_executable or sys.executable), os.path.join(exec_dir, "r38_debt_aging.py"), "--json", out_json2],
                         cwd=str(repo), capture_output=True, text=True,
                         encoding="utf-8", errors="replace", timeout=180)
        except Exception as e:
            return ("REGEN-FAILED", "重试调用异常：%s" % e)
        if r2.returncode != 0:
            return ("REGEN-FAILED", "重试 rc=%s：%s" % (r2.returncode, (r2.stderr or "")[-160:]))
        try:
            new_m2 = os.path.getmtime(out_json2)
        except OSError as e:
            return ("REGEN-FAILED", "重试件 mtime 取不到：%s" % e)
        if new_m2 >= vol_m:
            return ("OK", "首次重生遇并发写 ⇒ 重试成功（%s，差 %.0f 秒）" % (os.path.basename(out_json2), new_m2 - vol_m))
        return ("STALE-REGEN", "重试一次后件仍旧于卷（并行写入持续）⇒ 放弃重试，下轮前置腿会再触发")
    return ("OK", "件比卷旧 %.0f 秒 ⇒ 已重生为 %s" % (vol_m - art_m, os.path.basename(out_json)))
