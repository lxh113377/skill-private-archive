# -*- coding: utf-8 -*-
r"""r20b_ratchet_fixtures.py — 「注入面棘轮」夹具（TDD：先看红，再实现 ratchet_gate.py）。

为什么要有它：r18/r19 两次实测出「目录注意力税 45,173 字符/轮」与「注入区并集 69,494B
> C25 硬顶 65,536B 而 C25 判 PASS」，但落地门禁要写进焚诀 `eval/`（项目红线：只读调用不改），
转办至今未回收。⇒ 在**本仓权限内**先把同等约束变成会拦人的东西：
只降不升的棘轮基线 + 缺指标即失败（R247）+ 真实超限样本必须被拦（对照）。

被测对象：`05-exec/ratchet_gate.py`，契约：
    evaluate(metrics: dict, baseline: dict, hard_caps: dict) -> (findings, unknown)
    · metrics 键 ⊂ 已知指标集；值必须是 int/float，否则记 unknown（不得当作 0）
    · 任一指标 > baseline 中记录的棘轮值 ⇒ finding（"超棘轮"）
    · 任一指标 > hard_caps ⇒ finding（"超硬顶"）
    · baseline 缺该指标 ⇒ finding（"无基线，禁止放行"）
退出码：0 全过 / 1 有失败 / 2 环境不满足
"""

import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

R = []


def ck(name, cond, detail=""):
    R.append(bool(cond))
    print("%s %-56s %s" % ("PASS" if cond else "FAIL", name, detail if not cond else ""))


def load_mod():
    fp = HERE / "ratchet_gate.py"
    if not fp.exists():
        return None
    spec = importlib.util.spec_from_file_location("rg", str(fp))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


METRICS = {"catalog_grand_chars": 45173, "inject_union_bytes": 69494,
           "claim_candidates": 4, "drift_ruleish_candidates": 10, "desc_over_cap": 0}
BASELINE = dict(METRICS)
CAPS = {"inject_union_bytes": 65536}   # C25 硬顶（真实值，用于「超顶仍 PASS」病灶的对照组）


def main():
    rg = load_mod()
    if rg is None:
        ck("RED 前置：ratchet_gate.py 存在", False,
           "文件不存在 —— 本次运行即 TDD 红阶段（先看失败，再写实现）")
        print("\n合计 %d 项，失败 %d" % (len(R), len(R)))
        print("[GATE:fixture-fail]")
        return 1
    ck("可导入且暴露 evaluate/load_baseline",
       hasattr(rg, "evaluate") and hasattr(rg, "load_baseline"))

    f, u = rg.evaluate(METRICS, BASELINE, {})
    ck("m1 全等基线 → 零发现", f == [] and u == [], json.dumps({"f": f, "u": u}, ensure_ascii=False))
    m = dict(METRICS); m["catalog_grand_chars"] = 45174
    f, _ = rg.evaluate(m, BASELINE, {})
    ck("m2 超棘轮 1 字符即拦（只降不升）", any("catalog_grand_chars" in x for x in f), f)
    m = dict(METRICS); m["inject_union_bytes"] = 70000
    f, _ = rg.evaluate(m, BASELINE, CAPS)
    ck("m3 超硬顶必须报「超硬顶」而非静默", any("硬顶" in x for x in f), f)
    m = dict(METRICS); m["claim_candidates"] = 0
    f, _ = rg.evaluate(m, BASELINE, {})
    ck("m4 变好（低于棘轮）不报，应提示可收紧基线", f == [], f)
    m = dict(METRICS); m["desc_over_cap"] = None
    f, u = rg.evaluate(m, BASELINE, {})
    ck("m5 非数值指标不得当 0（记 unknown）", u == ["desc_over_cap"] or "desc_over_cap" in u, u)
    f, u = rg.evaluate(METRICS, {"catalog_grand_chars": 1}, {})
    ck("m6 基线缺指标 → 报「无基线」不得放行", any("inject_union_bytes" in x for x in f), f)
    f, _ = rg.evaluate({"totally_unknown_metric": 999}, BASELINE, {})
    ck("m7 未知指标名不误报（也不参与判定）", f == [], f)

    # 层 b 真机接线：先用「现状」建基线（--update），再以该基线复跑
    #   预期：不出现「超棘轮」（棘轮面自身不报警 = 生效路径），
    #   但**允许且只允许**出现「超硬顶」——本仓注入区并集实测已超 C25 硬顶，属真阳性，
    #   禁止为了让测试变绿而放宽硬顶或删指标（R263：先修判据表达，不改数据凑绿）。
    tmp = Path(tempfile.mkdtemp(prefix="r20b_ratchet_"))
    bl = tmp / "fresh.json"
    pu = subprocess.run([sys.executable, str(HERE / "ratchet_gate.py"), "--baseline", str(bl),
                         "--update"], capture_output=True, text=True,
                        encoding="utf-8", errors="replace", timeout=600)
    ck("层b --update 建基线 exit 0", pu.returncode == 0, (pu.stdout + pu.stderr)[-200:])
    fresh = json.loads(bl.read_text(encoding="utf-8")) if bl.exists() else {}
    ck("层b 基线含 5 项且全为整数", len(fresh.get("metrics", {})) == 5
       and all(isinstance(v, int) for v in fresh.get("metrics", {}).values()),
       json.dumps(fresh.get("metrics"), ensure_ascii=False))
    out = tmp / "out.json"
    p = subprocess.run([sys.executable, str(HERE / "ratchet_gate.py"), "--baseline", str(bl),
                        "--json", str(out)], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=600)
    data = json.loads(out.read_text(encoding="utf-8")) if out.exists() else {}
    allt = "\n".join(data.get("findings", []))
    ck("层b 生效路径：以现状为基线后不再报「超棘轮」", "超棘轮" not in allt,
       json.dumps(data.get("findings"), ensure_ascii=False)[:220])
    ck("层b 缺失指标为空（R247）", data.get("unknown") == [], json.dumps(data.get("unknown")))
    ck("层b 真阳性：注入区并集超 C25 硬顶必须报（实测面）", "超硬顶" in allt,
       json.dumps(data.get("findings"), ensure_ascii=False)[:220])
    ck("层b 两级判定：现状未长大 ⇒ 默认非阻断 exit 0（超顶只告警）", p.returncode == 0,
       "rc=%s findings=%s" % (p.returncode, json.dumps(data.get("findings"), ensure_ascii=False)[:160]))
    ck("层b 阻断/告警分列", data.get("advisory") and not data.get("blocking"),
       json.dumps({k: data.get(k) for k in ("blocking", "advisory")}, ensure_ascii=False)[:200])
    ps = subprocess.run([sys.executable, str(HERE / "ratchet_gate.py"), "--baseline", str(bl),
                         "--strict-cap"], capture_output=True, text=True,
                        encoding="utf-8", errors="replace", timeout=600)
    ck("层b --strict-cap：同一实测面升级为阻断 exit 1", ps.returncode == 1,
       "rc=%s %s" % (ps.returncode, (ps.stdout or "")[-160:]))
    ck("层b 指标名与契约一致", set(data.get("metrics", {})) == set(rg.METRIC_NAMES),
       json.dumps(sorted(data.get("metrics", {}))))
    # 对照组：基线整体收紧 1 ⇒ 必须冒出「超棘轮」且 exit != 0
    bl2 = tmp / "tight.json"
    bl2.write_text(json.dumps({"schema": "zijian-inject-ratchet-v1",
                               "metrics": dict((k, v - 1) for k, v in data["metrics"].items()),
                               "note": "对照"}, ensure_ascii=False), encoding="utf-8")
    p2 = subprocess.run([sys.executable, str(HERE / "ratchet_gate.py"), "--baseline", str(bl2)],
                        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
    ck("层b 对照组：基线收紧 1 即 exit!=0", p2.returncode != 0, "rc=%s" % p2.returncode)
    ck("层b 对照组：冒出「超棘轮」并点名指标", "超棘轮" in (p2.stdout or "")
       and "inject_union_bytes" in (p2.stdout or ""), (p2.stdout or "")[-200:])
    # 反抬基线：现状**高于**既有基线时 --update 必须拒绝（棘轮只降不升）；
    # 反向（现状低于基线）必须允许——那正是「收紧基线」的正常路径。
    bl3 = tmp / "grown.json"
    bl3.write_text(json.dumps({"schema": "zijian-inject-ratchet-v1",
                               "metrics": dict((k, v - 5000) for k, v in data["metrics"].items()
                                               if k != "inject_union_bytes"),
                               "note": "既有基线比现状低 5000 = 现状已长大"}, ensure_ascii=False),
                   encoding="utf-8")
    p3 = subprocess.run([sys.executable, str(HERE / "ratchet_gate.py"), "--baseline", str(bl3),
                         "--update"], capture_output=True, text=True,
                        encoding="utf-8", errors="replace", timeout=600)
    ck("层b 反抬基线：现状高于基线时 --update 拒绝", p3.returncode != 0
       and "拒绝抬基线" in (p3.stdout or ""), "rc=%s %s" % (p3.returncode, (p3.stdout or "")[-160:]))
    bl4 = tmp / "shrunk.json"
    bl4.write_text(json.dumps({"schema": "zijian-inject-ratchet-v1",
                               "metrics": dict((k, v + 5000) for k, v in data["metrics"].items()),
                               "note": "既有基线偏高 ⇒ 允许下调"}, ensure_ascii=False), encoding="utf-8")
    p4 = subprocess.run([sys.executable, str(HERE / "ratchet_gate.py"), "--baseline", str(bl4),
                         "--update"], capture_output=True, text=True,
                        encoding="utf-8", errors="replace", timeout=600)
    ck("层b 只降不升：现状低于基线时允许收紧", p4.returncode == 0, (p4.stdout or "")[-160:])

    bad = [i for i, ok in enumerate(R, 1) if not ok]
    print("\n合计 %d 项，通过 %d，失败 %d" % (len(R), len(R) - len(bad), len(bad)))
    print("[GATE:fixture-pass]" if not bad else "[GATE:fixture-fail] 用例 %s" % bad)
    return 0 if not bad else 1


if __name__ == "__main__":
    raise SystemExit(main())
