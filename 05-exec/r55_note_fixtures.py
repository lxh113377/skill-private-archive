# -*- coding: utf-8 -*-
"""r55 基线留账夹具：--update 不得刷掉「这个基线值凭什么是它」的逐轮归因。

存在理由（r55 实跑自抓）：我跑了一次 `ratchet_gate.py --update`，它把
`inject_ratchet_baseline.json` 的 note 从 **496 字刷成 33 字** —— r38「真实敞口 22 而非 0」、
r40「真值直取证据件，未做人工削减」、r45「W-14 新指标」三条人工核定依据一次性蒸发，
且当时没有任何门禁变红。指标面（只降不升）有牙齿，留账面以前完全没牙齿 ⇒ 本锁补齐。
n1-n3 单测 merge_note；n4 走真实 CLI 派发形态（X-28）；n5/n6 是零输入与现件常驻回归锁。
"""
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BASE = os.path.join(ROOT, "06-benchmark", "inject_ratchet_baseline.json")
sys.path.insert(0, HERE)
import ratchet_gate as rg  # noqa: E402

RESULTS = []


def ck(name, cond, detail=""):
    RESULTS.append((bool(cond), name, detail))
    print("%-4s %s%s" % ("PASS" if cond else "FAIL", name,
                         ("  ← " + str(detail)[:200]) if detail and not cond else ""))


def main():
    base_note = "只降不升棘轮；缺项/超顶/无基线一律 exit 非 0（R247）"
    trail = "｜r38 人工核定 overdue_debt_items=22（真实敞口 22 而非 0）"

    # n1 正例：带留账 + 本轮有指标变化 ⇒ 两段都在，且没缩短
    prev = base_note + " " + trail
    new, shrunk = rg.merge_note(prev, base_note, "2026-09-25 18:40",
                                {"deferred_debt_items": (23, 0)})
    ck("n1 正例：历史留账 + 本轮归因段同时在场，且只增不减",
       (not shrunk) and trail in new and "deferred_debt_items 23→0" in new and new.startswith(base_note),
       "new=%s" % new[:160])

    # n2 反例（防误删）：人工改过、不以 base_note 开头的 note 必须整条保住，禁按长度切片
    hand = "完全手写的说明 r31 授权代际列表" 
    new2, shr2 = rg.merge_note(hand, base_note, "2026-09-25 18:40", {})
    ck("n2 反例：不以 base_note 开头的人工 note 不得被按长度切掉前缀",
       hand in new2 and not shr2, "new2=%s" % new2[:160])

    # n3 边界：零输入（无指标变化）⇒ 不凭空造归因段，也不判绿成"有归因"
    new3, shr3 = rg.merge_note(base_note, base_note, "2026-09-25 18:40", {})
    ck("n3 边界：changed 为空 ⇒ 不追加空归因段（零输入不得写成有留账）",
       new3 == base_note and "自动核定" not in new3 and not shr3, repr(new3[:120]))

    _N4_UNVERIFIED = False
    # n4 真实派发形态：临时基线跑 CLI --update，留账与 attributed_raises 都必须活下来
    # r208 修（接线腿与现状腿解耦，照 r54/r56 先例）：--update 遇到「实测 > 基线」会
    # **正确地**拒绝写入（[RATCHET:REFUSE]）⇒ rc=1 ⇒ n4 恒红。那不是写入缺陷，是夹具把
    # 「本项目此刻有没有超基线债」焊进「--update 会不会保留留账」。
    # 修法：临时基线的指标先对齐现测值（无增长面 ⇒ 拒写分支不触发），
    # 再断言留账与 attributed_raises 在写入路径上存活。拒写语义由 ratchet_gate 自身
    # 与 r123 区间归因夹具看守，此处不重复断言。
    _tmpd = tempfile.mkdtemp(prefix="r55_note_")
    tmp = os.path.join(_tmpd, "r55_note_baseline.json")
    shutil.copyfile(BASE, tmp)
    with io.open(tmp, encoding='utf-8-sig') as f:
        d = json.load(f)
    d["note"] = base_note + " " + trail
    d["attributed_raises"] = [{"metric": "inject_union_bytes", "reason": "夹具哨兵",
                               "from_value": 1, "to_value": 2, "commit": "x", "path": "p",
                               "delta": 1, "at": "2026-09-25 00:00"}]
    with io.open(tmp, 'w', encoding='utf-8', newline='') as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    env = dict(os.environ, PYTHONPYCACHEPREFIX=os.path.join(_tmpd, "pyc_r55"))
    subprocess.run([sys.executable, os.path.join(HERE, "ratchet_gate.py"),
                    "--baseline", tmp, "--json", os.path.join(_tmpd, "live.json")],
                   capture_output=True, text=True, encoding="utf-8",
                   errors="replace", env=env, cwd=ROOT)
    try:
        with io.open(os.path.join(_tmpd, "live.json"), encoding="utf-8-sig") as f:
            _live = json.load(f)
        if isinstance(_live.get("metrics"), dict) and _live["metrics"]:
            d["metrics"] = dict(_live["metrics"])
            with io.open(tmp, 'w', encoding='utf-8', newline='') as f:
                json.dump(d, f, ensure_ascii=False, indent=1)
    except Exception:
        pass
    p = subprocess.run([sys.executable, os.path.join(HERE, "ratchet_gate.py"),
                        "--baseline", tmp, "--update"],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", env=env, cwd=ROOT)
    with io.open(tmp, encoding='utf-8-sig') as f:
        after = json.load(f)
    _o4 = (p.stdout or "") + (p.stderr or "")
    # r209 修 R113-5 同族第四种形态：--update 在有算不出的指标时会**正确地**拒绝写基线
    # （[RATCHET:REFUSE] 禁止把算不出的项写成 0）⇒ rc=2 ⇒ n4 恒红，而红因与
    # 「留账与 attributed_raises 是否存活」无关。三态分流，第三态不算通过。
    if "缺失指标" in _o4 or "拒绝写基线" in _o4:
        print("SKIP %-56s %s" % ("n4 真实 CLI（--update）：指标缺失面触发拒写（UNVERIFIED，非写入缺陷）",
                                 "  <-- " + (_o4.strip().splitlines()[-1][:150] if _o4.strip() else "无输出")))
        _N4_UNVERIFIED = True
    else:
        ck("n4 真实 CLI（--update）：留账 trail 与 attributed_raises 均须存活且 rc=0",
           p.returncode == 0 and trail in str(after.get("note")) and len(after.get("attributed_raises") or []) == 1,
           "rc=%s note=%s ar=%s out=%s" % (p.returncode, str(after.get("note"))[:100],
                                           len(after.get("attributed_raises") or []), p.stdout[-160:]))
    shutil.rmtree(_tmpd, ignore_errors=True)

    # r125 自抓（输入面与被写面重叠 ⇒ 假红）：n5 与 n6 原各独立 json.loads 读真基线件，
    # runner 跑 38 门耗时数分钟，期间并行会话改棘轮 note（r124 即在改 debt 指标与留账），
    # 两次读之间文件被换掉 ⇒ n5 通过而 n6 读到半写状态 ⇒ 假红（已连续三轮出现）。
    # 修法：单次读取 + 重试到拿到**自洽**内容（note 非空且三条依据齐全），
    # 仍不满足才判红 —— 这是读取侧重试，不是放宽判据（判据本身一条没动）。
    _doc = None
    for _try in range(6):
        try:
            _cand = json.loads(io.open(BASE, encoding="utf-8-sig").read()) or {}
        except Exception:
            _cand = None
        if isinstance(_cand, dict) and isinstance(_cand.get("note"), str) and _cand["note"]:
            _doc = _cand
            break
    _note = (_doc or {}).get("note") or ""

    # n5 零输入不得记 PASS：读不到 note 就当失败，不许默认"没有留账=正常"
    ck("n5 零输入：现件 note 必须非空（空 note 不得被当成合格基线）",
       bool(_note) is True,
       "note 缺失（重试 6 次仍读不到自洽内容）")

    # n6 常驻回归锁：本轮恢复的三条人工核定依据必须仍在（将来任何再刷留账的行为当场红）
    ck("n6 常驻锁：现件留账须仍含 r38/r40/r45 三条人工核定依据（防再次被 --update 刷掉）",
       all(k in _note for k in ("r38 人工核定", "r40 核定", "r45 核定")),
       "len=%d note=%s" % (len(_note), _note[:180]))

    fails = [r for r in RESULTS if not r[0]]
    print("\n夹具合计: %d 项，通过 %d，失败 %d"
          % (len(RESULTS), len(RESULTS) - len(fails), len(fails)))
    if fails:
        print("[GATE:fixture-fail]")
        return 1
    if _N4_UNVERIFIED:
        print("[GATE:fixture-unverified] n4 因本机指标缺失面未验证（非判据红，R247 不按绿记）")
        return 2
    print("[GATE:fixture-pass]")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())
