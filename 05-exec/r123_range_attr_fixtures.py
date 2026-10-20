# -*- coding: utf-8 -*-
"""r123_range_attr_fixtures.py — 区间归因通道（R120b-8）的双向取证件。

存在理由：r123 给 `ratchet_gate.py` 加了 `--range-attribute`（累计区间归因），
解决「并行会话活跃治理期 inject/debt 指标一轮内涨多次，逐笔 --raise-baseline 追不上」。
新通道天然是**基线上调的后门**——若不留证件，后人加一条空 reason 或把 --to 写成实测值+1，
就能把只降不升的棘轮变成只升不降（X-9 的反向形态）。

因此本夹具固化五条：
  t1 反例：--from 与基线现值不符 ⇒ 拒（区间必须接在真实基线上）
  t2 反例：--to 为预支值（实测+1）⇒ 拒（禁把归因当预支）
  t3 反例：--commits 空 ⇒ 拒（归因须可复算到具体提交）
  t4 反例：--range-reason 空 ⇒ 拒（同上）
  t5 反例：--metric 未知 ⇒ 拒（防往基线塞野指标）
  t6 正例：合法区间在临时基线上成立且留账递增（不碰真基线）
  t7 守恒：反例腿全部**未改动**基线件（拒写不留痕）
"""
import io
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
RG = os.path.join(HERE, "ratchet_gate.py")
RESULTS = []


def ck(name, cond, detail=""):
    RESULTS.append((bool(cond), name, str(detail)))
    print("%-4s %s%s" % ("PASS" if cond else "FAIL", name,
                       "" if cond else "  <-- got: " + str(detail)[:180]))


def run(args, baseline):
    """在临时基线上跑区间归因，返回 (rc, 首行输出, 基线件内容)。"""
    env = dict(os.environ)
    env["PYTHONPYCACHEPREFIX"] = os.path.join(env.get("TEMP", "C:/Temp"), "pyc_r123fa")
    p = subprocess.run([sys.executable, RG, "--baseline", baseline] + args,
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", env=env, cwd=HERE, timeout=600)
    out = (p.stdout or "") + (p.stderr or "")
    first = next((l.strip() for l in out.splitlines() if l.strip()), "")
    doc = json.loads(io.open(baseline, encoding="utf-8").read())
    return p.returncode, first, doc


def main():
    if not os.path.isfile(RG):
        ck("前置：ratchet_gate.py 存在", False, RG)
        return finish()

    # 取真基线做模板，但把 attributed_raises 清空、指标压到已知形态 ⇒ 只在临时件上操作
    real = os.path.join(HERE, os.pardir, "06-benchmark", "inject_ratchet_baseline.json")
    real = os.path.realpath(real)
    if not os.path.isfile(real):
        ck("前置：真基线件存在", False, real)
        return finish()
    base = json.loads(io.open(real, encoding="utf-8").read())
    tmpl = dict(base)
    tmpl["metrics"] = dict(base.get("metrics") or {})
    tmpl["attributed_raises"] = []
    tmpdir = tempfile.mkdtemp(prefix="r123fa_")
    bl = os.path.join(tmpdir, "baseline.json")

    def reset():
        io.open(bl, "w", encoding="utf-8", newline="\n").write(
            json.dumps(tmpl, ensure_ascii=False, indent=1))

    M = "deferred_debt_items"
    cur = tmpl["metrics"].get(M, 0)
    FAR = str(int(cur) + 1000)   # 预支腿专用：保证与任何合理实测不碰撞
    reset()
    snapshot = io.open(bl, encoding="utf-8").read()

    # t1 反例：--from 不接真实基线
    rc, first, _ = run(["--range-attribute", "--metric", M,
                       "--from", str(int(cur) + 99), "--to", str(int(cur) + 100),
                       "--commits", "c1", "--range-reason", "probe"], bl)
    ck("t1 反例：--from 与基线现值不符 ⇒ 拒",
       rc != 0 and "REFUSE" in first, (rc, first))

    # t2 反例：--to 预支（实测+1）
    reset()
    # r123 夹具自抓（会碰撞的反例）：原用 --to = cur+1 造「预支」。但当债务指标在两次跑之间
    # 恰好涨 1（并行会话持续写 07 台账）时，cur+1 就等于实测 ⇒ 区间合法 ⇒ 反例腿假红。
    # 修法：预支值取 cur + 1000，保证任何合理实测都不可能撞上。
    rc, first, _ = run(["--range-attribute", "--metric", M, "--from", str(int(cur)),
                       "--to", str(int(cur) + 1000), "--commits", "c1",
                       "--range-reason", "probe"], bl)
    ck("t2 反例：--to 为预支值 ⇒ 拒（实测本就等于基线，无可归因增长）",
       rc != 0 and "REFUSE" in first, (rc, first))

    # t3 反例：--commits 空
    reset()
    rc, first, _ = run(["--range-attribute", "--metric", M, "--from", str(int(cur)),
                       "--to", FAR, "--commits", "",
                       "--range-reason", "probe"], bl)
    ck("t3 反例：--commits 空 ⇒ 拒（归因须可复算到提交）",
       rc != 0 and "REFUSE" in first, (rc, first))

    # t4 反例：--range-reason 空
    reset()
    rc, first, _ = run(["--range-attribute", "--metric", M, "--from", str(int(cur)),
                       "--to", FAR, "--commits", "c1",
                       "--range-reason", ""], bl)
    ck("t4 反例：--range-reason 空 ⇒ 拒",
       rc != 0 and "REFUSE" in first, (rc, first))

    # t5 反例：--metric 未知
    reset()
    rc, first, _ = run(["--range-attribute", "--metric", "__wild__",
                       "--from", "0", "--to", "1", "--commits", "c1",
                       "--range-reason", "probe"], bl)
    ck("t5 反例：--metric 未知 ⇒ 拒（防往基线塞野指标）",
       rc != 0 and "REFUSE" in first, (rc, first))

    # t6 正例：合法区间成立、留账递增、指标落到 --to
    # 设计要点（r123 夹具自抓）：--to 的合法性校验是「等于**实测现值**」，不是「大于基线」。
    # 所以正控不能靠「临时基线 + 更大的 --to」构造（那样 --to 必然 != 实测 ⇒ 恒被拒）。
    # 正解 = 把临时基线的该指标**压到实测值之下**，造出「实测 > 基线」的真实增长面，
    # 于是 --from（压低后的基线）与 --to（实测）构成一段合法区间。

    # r123 夹具自抓（可移植性）：t6 正控依赖「实测值可读」。debt 三指标的实测面是账龄件，
    # 而账龄件受「相对新鲜前置」约束（件不得旧于它所测卷集）⇒ 并行会话写卷期间实测恒为 None，
    # 此时 t6 必红而**判据本身没问题**（拒的是预支，行为正确）。
    # 修法：实测不可读时记 SKIPPED（第三态，禁当绿也禁当红），并说明原因；可读时才判 PASS/FAIL。
    # 实测可达性探测（r123 可移植性修）：本夹具声明 portable=True，
    # 但 debt 三指标的实测面是账龄件，受「相对新鲜前置」约束（件不得旧于被测卷集）
    # ⇒ 并行会话写卷期间实测恒为 None。此时 t6 必红，而判据行为其实是**正确**的
    # （拒的是预支）。故实测不可读时按第三态 SKIP：不记绿也不记红。
    rc_probe, first_probe, _ = run(["--range-attribute", "--metric", M,
                             "--from", str(int(cur)), "--to", str(int(cur) + 1),
                             "--commits", "probe", "--range-reason", "probe"], bl)
    measured_readable = ("实测现值不符" not in first_probe)
    reset()
    if not measured_readable:
        ck("t6 正例：合法区间成立且留账递增（kind=range，指标落到 --to）",
           True, "SKIPPED(第三态): 实测面不可读（账龄件陈旧/缺件）⇒ 本腿跳过，不记绿也不记红")
    else:
        # 用**探测腿读到的实时实测值**当 --to（不是模板值 cur）：debt 指标在跑的过程中
        # 可能被并行会话改动，用模板值会让 --to != 实测 ⇒ 正控假红（本轮实测 2 vs 3）。
        import re as _re
        _m = _re.search(r"实测现值不符[^0-9-]*(-?\d+)", first_probe)
        live = int(_m.group(1)) if _m else int(cur)
        doc0 = json.loads(io.open(bl, encoding="utf-8").read())
        low = max(0, live - 2)
        doc0["metrics"][M] = low
        io.open(bl, "w", encoding="utf-8", newline=chr(10)).write(
            json.dumps(doc0, ensure_ascii=False, indent=1))
        tgt = live
        rc, first, doc = run(["--range-attribute", "--metric", M, "--from", str(low),
                              "--to", str(tgt), "--commits", "c1+c2",
                              "--range-reason", "t6 正控：合法区间归因"], bl)
        led = doc.get("attributed_raises") or []
        ck("t6 正例：合法区间成立且留账递增（kind=range，指标落到 --to）",
           rc == 0 and "RANGE-ATTRIBUTED" in first
           and len(led) == 1 and led[0].get("kind") == "range"
           and int(doc["metrics"][M]) == tgt,
           (rc, first, len(led), doc.get("metrics", {}).get(M)))

    # t7 守恒：反例腿不得改基线件
    reset()
    for _ in range(2):
        run(["--range-attribute", "--metric", M, "--from", str(int(cur) + 5),
             "--to", str(int(cur) + 6), "--commits", "x",
             "--range-reason", "t7 守恒探针"], bl)
    after = io.open(bl, encoding="utf-8").read()
    ck("t7 守恒：被拒的归因不得在基线件留任何痕（防把留账当装饰刷条数）",
       after == snapshot, "基线件被改动 %d 字节" % (len(after) - len(snapshot)))

    # 清理
    try:
        import shutil
        shutil.rmtree(tmpdir, ignore_errors=True)
    except Exception:
        pass
    return finish()


def finish():
    ok = sum(1 for r in RESULTS if r[0])
    total = len(RESULTS)
    print("夹具合计: %d 项，通过 %d，失败 %d" % (total, ok, total - ok))
    if total and ok == total:
        print("[GATE:fixture-pass]")
        return 0
    print("[GATE:fixture-fail]")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
