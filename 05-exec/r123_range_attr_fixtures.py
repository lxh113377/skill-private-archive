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


def ck(name, cond, detail="", skipped=False):
    # r208 修（第二个 bug，由变异测试暴露）：第三态原先记成 PASS —— 变异跑里 t8 其实
    # 走了 SKIP（哨兵腿未执行），但打印看不出差别，于是「有牙验证」被 SKIP 吞掉、
    # 给出假阴性结论（我差点据此判定守卫丢牙）。第三态必须有独立标记 SKIP。
    st = "SKIP" if skipped else ("PASS" if cond else "FAIL")
    RESULTS.append((bool(cond or skipped), name, str(detail)))
    print("%-4s %s%s" % (st, name,
                       "" if (cond and not skipped) else "  <-- " + str(detail)[:200]))


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


def parse_measured(msg):
    # r208：弃 regex 改纯字符串解析。旧写法在 r"...\\s..." 里被写成双反斜杠 ⇒
    # r-string 里那是「字面反斜杠 + s」，永远匹配不到空白，于是静默走回退分支；
    # 回退取「最后一个整数」恰好也等于实测，才把 bug 掩盖了三轮。文案本身是稳定的：
    # 「--to 与实测现值不符（<传入> vs <实测>）」，直接定位 vs 后取数字最稳。
    key = "实测现值不符"
    i = (msg or "").find(key)
    if i < 0:
        return None
    seg = msg[i:]
    j = seg.find("vs")
    if j < 0:
        return None
    # r208 修（第三态化照出来的真 bug）：文案是「vs 1）」，j+2 处是**空格**，
    # 原先直接从那里开始扫数字 ⇒ 恒返回 None ⇒ t6/t8 长期走 SKIP。而 SKIP 当时又打印
    # PASS（见 ck 的 r208 注），于是「两条腿一直什么都没测」被两层掩盖：解析漏空格 +
    # 第三态伪装成通过。先跳过空白再扫。
    k = j + 2
    while k < len(seg) and seg[k] == " ":
        k += 1
    out = ""
    while k < len(seg) and (seg[k].isdigit() or seg[k] == "-"):
        out += seg[k]
        k += 1
    return int(out) if out else None


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
    SENTINEL = int(cur) + 777000   # 旁观指标哨兵（r208）：与合理实测必不等
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

    # r208 重构（本轮 t6/t8 交替假红、单跑全过的真实根因）：实测面是**活的** 07 台账，
    # 由子进程现读 ⇒ 「探测实测」与「使用该实测」之间有 TOCTOU 窗口。并行会话在窗口内
    # 重算债务（本轮 deferred 2→1）时，拿旧实测当 --to 会被**正确**拒掉：判据没错，
    # 错在夹具把两次调用间的时间差当静态量。第一版给 t8 单独补了现探（于是 t8 过、t6 又红），
    # 说明该修的是公共闭包而不是逐腿打补丁。
    # 修法：探→写→用 封进 attribute_fresh；遇「与实测现值不符」按环境漂移重探重试；
    #       重试耗尽记第三态 SKIP（不记绿也不记红）；**其它失败仍判 FAIL** ——
    #       夹具自己的逻辑错必须现形，绝不借 SKIP 掩盖（本仓立的「禁把跳过当通过」）。
    def attribute_fresh(reason, bystander=None, tries=6):
        for _att in range(tries):
            reset()
            _rc, _fp, _ = run(["--range-attribute", "--metric", M,
                             "--from", str(int(cur)), "--to", FAR,
                             "--commits", "probe",
                             "--range-reason", "probe"], bl)
            if "实测现值不符" not in _fp:
                return ("SKIP", "实测面不可读（账龄件陈旧/缺件）")
            live_x = parse_measured(_fp)
            if live_x is None:
                return ("SKIP", "实测值解析失败：%s" % _fp[:60])
            if live_x <= 0:
                # r212：归属方（并行会话）给 ratchet 新加「to > from（禁把无变化记成归因）」校验
                # （HEAD 已含，非在途）。实测 deferred_debt_items=0 时 low=max(0,0-2)=0 与 to=0
                # 相等 ⇒ 环境里**不存在合法区间**，正控腿无对象可测 —— 这是前置不可满足，
                # 不是夹具逻辑错，也不是判据坏（无债可归因时本就不该有归因）。记第三态；
                # 一旦债务重新长出（live>0）本腿自动恢复判定，不会长期静音。
                return ("SKIP", "实测=%d ⇒ 无 to>from 的合法区间（无债可归因，正控腿无对象）" % live_x)
            doc_x = json.loads(io.open(bl, encoding="utf-8").read())
            # r208 修（变异测试实证的空转守卫）：基准若直接取「模板原值」，一旦该指标的
            # 模板值恰好 == 实测值，全量写入的变异后门把旁观指标刷成实测也**看不出来**
            # ⇒ 守卫恒真、丢牙（本轮变异跑 rc=0、t8 PASS 即此）。正解 = 写入与任何合理
            # 实测都不碰撞的哨兵值，让「搭车上调」必然留下可见差值。
            if bystander:
                doc_x["metrics"][bystander] = SENTINEL
            io.open(bl, "w", encoding="utf-8", newline=chr(10)).write(
                json.dumps(doc_x, ensure_ascii=False, indent=1))
            base_by = (doc_x.get("metrics") or {}).get(bystander) if bystander else None
            low_x = max(0, live_x - 2)
            doc_x["metrics"][M] = low_x
            io.open(bl, "w", encoding="utf-8", newline=chr(10)).write(
                json.dumps(doc_x, ensure_ascii=False, indent=1))
            rc_x, first_x, doc_fin = run(["--range-attribute", "--metric", M,
                                          "--from", str(low_x),
                                          "--to", str(live_x),
                                          "--commits", "c1+c2",
                                          "--range-reason", reason], bl)
            if rc_x == 0 and "RANGE-ATTRIBUTED" in first_x:
                return ("OK", (live_x, low_x, doc_fin, base_by, first_x))
            if "与实测现值不符" in first_x:
                continue          # 环境漂移：重探重试，不猜、不算绿
            return ("FAIL", (rc_x, first_x[:120], live_x))
        return ("SKIP", "重试 %d 次仍被并行会话改动" % tries)

    kind6, pay6 = attribute_fresh("t6 正控：合法区间归因")
    if kind6 == "SKIP":
        ck("t6 正例：合法区间成立且留账递增（kind=range，指标落到 --to）",
           True, "第三态: %s ⇒ 不记绿也不记红" % pay6, skipped=True)
    elif kind6 == "FAIL":
        ck("t6 正例：合法区间成立且留账递增（kind=range，指标落到 --to）",
           False, "非漂移类失败（夹具逻辑错，不许记 SKIP）：%s" % (pay6,))
    else:
        live6, low6, doc6, _b6, first6 = pay6
        led = doc6.get("attributed_raises") or []
        ck("t6 正例：合法区间成立且留账递增（kind=range，指标落到 --to）",
           len(led) == 1 and led[0].get("kind") == "range"
           and int(doc6["metrics"][M]) == live6,
           (len(led), doc6.get("metrics", {}).get(M), live6))

    # t8 搭车守卫（r201 一手）：区间归因只准动被点名的指标。第一版把对照基准
    # bystander0 从「已被 t6 跑过的临时基线」里读 ⇒ 基准自身被污染 ⇒ 守卫恒真、
    # 变异漏检（变异测试抓出来）。现基准 = 本次 reset 后模板原值，且与 t6 共用同一
    # 闭包（自带现探），不再有跨调用的时间差。
    B = "overdue_debt_items"
    kind8, pay8 = attribute_fresh("t8 搭车守卫", bystander=B)
    if kind8 == "SKIP":
        ck("t8 守卫：区间归因后旁观指标保持基线原值（禁搭车上调）",
           True, "第三态: %s" % pay8, skipped=True)
    elif kind8 == "FAIL":
        ck("t8 守卫：区间归因后旁观指标保持基线原值（禁搭车上调）",
           False, "非漂移类失败：%s" % (pay8,))
    else:
        live8, low8, doc8, bystander8, first8 = pay8
        ck("t8 守卫：区间归因后旁观指标保持基线原值（禁搭车上调）",
           (doc8.get("metrics") or {}).get(B) == bystander8,
           ((doc8.get("metrics") or {}).get(B), bystander8))

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
    ok = sum(1 for r in RESULTS if r[0] and "第三态" not in r[2])
    sk = sum(1 for r in RESULTS if "第三态" in r[2])
    total = len(RESULTS)
    fails = total - ok - sk
    print("夹具合计: %d 项，通过 %d，第三态 %d，失败 %d" % (total, ok, sk, fails))
    # r212 修正 rc 口径：第三态**不算通过**（R247 禁把跳过当绿，故单列计数并打 SKIP 标记），
    # 但也不该把判据永久染红 —— rc 只由「失败」驱动。SKIP 始终在 stdout 可见，不静默。
    if fails == 0:
        print("[GATE:fixture-pass]%s" % ("（含第三态 %d 项，见上）" % sk if sk else ""))
        return 0
    print("[GATE:fixture-fail]")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
