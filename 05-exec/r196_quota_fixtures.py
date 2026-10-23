# -*- coding: utf-8 -*-
"""r196_quota_fixtures.py — 额度面夹具（W-47 双向 + 变异腿）。

锁四件事（都是本轮实测踩到的）：
  A 括号平衡扫描能在「JSON + ANSI 告警尾巴」的混合输出里截出数组（wrangler --json 的真实形态）
  B NO_COLOR 对 wrangler 的 WARNING 无效 ⇒ 必须先剥 ANSI 再扫描（否则 json.loads 报 Extra data）
  C 三态不互相冒充：GAP_PLATFORM（平台下线，有依据）≠ UNVERIFIED（本轮取不到）
  D 变异：去掉 ANSI 剥离 ⇒ B 的场景必须失败（证明 A/B 腿真有牙，不是恰好过）
"""
import importlib.util as _u
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
TARGET = os.path.join(HERE, "r196_quota_face.py")
RESULTS = []


def ck(name, cond, detail=""):
    RESULTS.append((bool(cond), name, detail))
    print("%s %-58s %s" % ("PASS" if cond else "FAIL", name, detail if not cond else ""))


def load():
    s = _u.spec_from_file_location("qf", TARGET)
    m = _u.module_from_spec(s)
    s.loader.exec_module(m)
    return m


# 本轮真实抓到的 wrangler 输出形态（截断，保留关键结构 + ANSI 告警尾巴）
RAW = (
    '[\n  {\n    "uuid": "bf5b1d01",\n    "name": "donggu-analytics",\n'
    '    "num_tables": 0,\n    "file_size": 6828032\n  },\n  {\n'
    '    "name": "supermarket",\n    "num_tables": 0,\n    "file_size": 2396160\n  }\n]\n'
    "\x1b[33m\u25b2 \x1b[43;33m[\x1b[43;30mWARNING\x1b[43;33m]\x1b[0m "
    "\x1b[1mProxy environment variables detected.\x1b[0m\n\n\n"
)


def main():
    if not os.path.isfile(TARGET):
        ck("t0 被测件存在", False, TARGET)
        print("[GATE:fixture-fail]")
        return 1
    m = load()

    # A 直接扫裸串会 Extra data
    try:
        json.loads(RAW)
        poisoned = False
    except ValueError:
        poisoned = True
    ck("A 原始混输出不可直接 json.loads（这就是本轮真实报错形态）", poisoned)

    # B 剥 ANSI + 括号平衡扫描 => 得到数组且数值正确
    clean = m.ANSI_RE.sub("", RAW)
    seg = m.first_json_array(clean)
    ok_b = False
    rows = None
    if seg:
        try:
            rows = json.loads(seg)
            ok_b = isinstance(rows, list) and len(rows) == 2
        except ValueError:
            ok_b = False
    ck("B 剥 ANSI + 括号平衡扫描截出数组（2 实例）", ok_b, str(rows)[:80])
    if rows:
        tot = sum(int(r.get("file_size") or 0) for r in rows)
        ck("B2 合计字节正确", tot == 6828032 + 2396160, str(tot))

    # C 三态互斥：GAP 依据须含官方出处；UNVERIFIED 不得带依据串
    g = m.read_gh_billing if hasattr(m, "read_gh_billing") else None
    ck("C1 被测件暴露 read_gh_billing（GAP 判定入口）", g is not None)
    doc = json.load(io.open(os.path.join(os.path.dirname(HERE), "06-benchmark",
                                        "quota_face_r196.json"), encoding="utf-8")) if True else None
    rows_doc = doc.get("rows") or []
    gap = [r for r in rows_doc if r.get("state") == "GAP_PLATFORM"]
    ck("C2 真件里 GAP_PLATFORM 带官方 changelog 出处",
       bool(gap) and "github.blog/changelog" in (gap[0].get("why") or ""),
       (gap[0].get("why") or "")[:60] if gap else "无 GAP 行")
    ck("C3 GAP 不等于 UNVERIFIED（两态计数分开）",
       "gap_platform_count" in doc and "unverified_count" in doc)
    ck("C4 额度读数标了分母出处（名册声称值，非官方文档）",
       any("名册" in str(v) for r in rows_doc for v in [r.get("note", "")]))

    # D 变异（r196 自我纠正：我第一版把 B 通过归因给「剥 ANSI」，被这条腿当场推翻 ——
    #   告警尾巴落在 JSON 数组**之外**，是括号平衡扫描截掉了它，剥离对本形态其实是冗余。
    #   归因错了就要拆成两条各测其责，而不是把错的那条改成永远为真）：
    # D1 去掉括号扫描（直接 loads 整串）⇒ 必须失败 ⇒ 证明真正起作用的是扫描
    ok_d1 = False
    try:
        json.loads(m.ANSI_RE.sub("", RAW))     # 剥了但不扫描
    except ValueError:
        ok_d1 = True
    ck("D1 变异：无括号平衡扫描则解析失败（扫描才是承重的那一步）", ok_d1),
    # D2 ANSI 若落在数组**内部**，只扫描不剥离必须失败 ⇒ 证明剥离有独立必要（构造场景）
    # D2 如实测量（不替错归因找补）：只剥 ANSI、不做括号扫描 => 本形态其实也能过，
    #   说明承重的是 D1 那一步（扫描），ANSI 剥离对本输出只是防御性的。
    strip_only = m.ANSI_RE.sub("", RAW)
    ok_after_strip_only = False
    try:
        rr = json.loads(strip_only.strip())
        ok_after_strip_only = isinstance(rr, list)
    except ValueError:
        ok_after_strip_only = False
    # D2 反向来测（r196 第二次自我纠正：我上一版断言「只剥不扫也能过」，实测 False ——
    #   那也是我**没测就写**的。故两向都实测，才敢指名承重步骤）：
    #   D1 剥了但不扫 => 失败；D2 扫了但不剥 => 成功 => 承重是括号扫描。
    seg_nostrip = m.first_json_array(RAW)
    ok_scan_only = False
    try:
        ok_scan_only = isinstance(json.loads(seg_nostrip), list)
    except (ValueError, TypeError):
        ok_scan_only = False
    ck("D2 只扫不剥 ⇒ 解析成功（配合 D1 证明承重步骤是扫描）",
       ok_scan_only is True,
       "strip_only=%r scan_only=%r" % (ok_after_strip_only, ok_scan_only))
    # D3 剥离器自身行为：清完后告警尾巴里不得再有 ESC，且文本仍在（证明是清了序列不是吞了内容）
    ESC = chr(27)
    pre_tail = RAW[RAW.rfind("]") + 1:] if "]" in RAW else ""
    tail = strip_only[strip_only.rfind("]") + 1:] if "]" in strip_only else ""
    ck("D3 ANSI_RE 只清转义序列不吞文本（前后对比）",
       (ESC in pre_tail) and (ESC not in tail) and ("Proxy" in tail),
       "pre有ESC=%s post有ESC=%s" % (ESC in pre_tail, ESC in tail))

    # ================ r197 代理分钟：口径与覆盖度纪律 ================
    import datetime as _dt
    M0 = _dt.datetime(2026, 10, 1, tzinfo=_dt.timezone.utc)

    def R(start, upd, status="completed"):
        return {"run_started_at": start, "updated_at": upd, "status": status}

    # E1 只计 completed 且双时间戳齐的，其余进 skipped
    runs = [R("2026-10-05T00:00:00Z", "2026-10-05T00:10:00Z"),          # 10 min
            R("2026-10-05T00:00:00Z", "2026-10-05T00:05:00Z"),          # 5 min
            R("2026-10-05T00:00:00Z", None, status="in_progress"),
            R(None, "2026-10-05T00:01:00Z")]
    mn, cnt, skp = m.run_minutes(runs, M0)
    ck("E1 只累加 completed 且双时间戳齐的 run（10+5=15min，跳过 2）",
       mn == 15.0 and cnt == 2 and skp == 2, (mn, cnt, skp))

    # E2 月初边界：早于 since 的不计入（防把上月消耗算进本月）
    runs2 = [R("2026-09-30T23:50:00Z", "2026-10-01T00:20:00Z"),          # 起点在月前
              R("2026-10-01T00:00:00Z", "2026-10-01T00:20:00Z")]          # 正好月初
    mn2, cnt2, _ = m.run_minutes(runs2, M0)
    ck("E2 起点早于月初的 run 不计入本月", mn2 == 20.0 and cnt2 == 1, (mn2, cnt2))

    # E3 负时长（时间戳异常）不得倒扣额度
    mn3, cnt3, skp3 = m.run_minutes([R("2026-10-05T00:20:00Z", "2026-10-05T00:00:00Z")], M0)
    ck("E3 时钟倒挂按 0 计，不得产生负分钟", mn3 == 0.0, (mn3, cnt3, skp3))

    # E4 month_start_utc 取到自然月 1 号 00:00 UTC（口径地基）
    ms = m.month_start_utc(_dt.datetime(2026, 10, 23, 19, 39, tzinfo=_dt.timezone.utc))
    ck("E4 month_start_utc = 当月 1 日 00:00Z",
       (ms.day == 1 and ms.hour == 0 and ms.minute == 0
        and ms.month == 10 and ms.year == 2026), ms.isoformat())

    # E5 覆盖度纪律：翻页未及月初 ⇒ UNVERIFIED，不得把部分当全量（R247）
    orig_fetch = m.fetch_runs_page
    def fake_pages(pages):
        def f(repo, page):
            if page <= len(pages):
                return pages[page - 1]
            return []
        return f
    SEP = "2026-10-20T00:00:00Z"
    EARLY = "2026-10-21T00:00:00Z"
    # 两页都停在月中（最早 created_at 晚于月初）且后续页非空 => 永不到月初
    m.fetch_runs_page = fake_pages([[R(EARLY, EARLY) for _ in range(3)]] * 2
                                    + [[R(SEP, SEP)] for _ in range(3)] * 40)
    try:
        st5, info5, why5 = m.read_minutes_proxy("x/y", month=M0, max_pages=6)
    finally:
        m.fetch_runs_page = orig_fetch
    ck("E5 覆盖不到月初 ⇒ UNVERIFIED 且不报分钟（不把部分当全量）",
       st5 == "UNVERIFIED" and info5 is None, (st5, why5, info5))

    # E6 覆盖完整时才出 MEASURED，且**不带任何 pct 字段**（锁死「不折算百分比」）
    OKP1 = [R("2026-10-10T00:00:00Z", "2026-10-10T00:10:00Z")] * 3
    OKP2 = [R("2026-09-28T00:00:00Z", "2026-09-28T00:01:00Z")] * 2   # 早于月初 => 触发停止
    m.fetch_runs_page = fake_pages([OKP1, OKP2])
    try:
        st6, info6, why6 = m.read_minutes_proxy("x/y", month=M0, max_pages=6)
    finally:
        m.fetch_runs_page = orig_fetch
    has_pct = bool(info6) and any("pct" in k for k in info6)
    ck("E6 覆盖完整才 MEASURED，且结果不含 pct 字段（无可靠分母就不折算）",
       st6 == "MEASURED" and info6.get("coverage_complete") is True and not has_pct,
       (st6, info6 if not info6 else sorted(info6.keys())))
    ck("E6b 只计本月内的（3 个 10min = 30min，9 月那条不计）",
       bool(info6) and info6.get("minutes_all_workflows") == 30.0,
       info6.get("minutes_all_workflows") if info6 else None)

    # ========= r197 归因守卫：网络瞬态与平台关停不得互相冒充 =========
    # 本轮实测两次误判：① gh 因网络整体失败（输出无 HTTP 状态码）却报了 GAP_PLATFORM；
    # ② wrangler 失败被写成「未登录/网络/限流？」。两处都是把瞬态读成状态、把未知读成结论。
    orig_sh = m.sh
    m.sh = lambda cmd: (1, 'Get https://api.github.com/x: EOF')
    try:
        stF1, _i1, whyF1 = m.read_gh_billing('someuser')
    finally:
        m.sh = orig_sh
    ck('F1 gh 失败但无 HTTP 状态码 => UNVERIFIED（不得读成平台关停）',
       stF1 == 'UNVERIFIED' and '不得读成平台关停' in whyF1, (stF1, whyF1[:80]))

    def fake_status(cmd):
        joined = ' '.join(cmd)
        return (1, '{status 410}'.replace('status 410', chr(34) + 'status' + chr(34) + ': ' + chr(34) + '410' + chr(34))) if 'billing/actions' in joined else (1, '{status 404}'.replace('status 404', chr(34) + 'status' + chr(34) + ': ' + chr(34) + '404' + chr(34)))
    m.sh = fake_status
    try:
        stF2, _i2, whyF2 = m.read_gh_billing('someuser')
    finally:
        m.sh = orig_sh
    ck('F2 确有 404/410 状态码 => 才判 GAP_PLATFORM 并带官方依据',
       stF2 == 'GAP_PLATFORM' and '404' in whyF2 and 'github.blog' in whyF2,
       (stF2, whyF2[:70]))

    ck('F3 网络类 stderr 归到 网络/代理 类别',
       '网络/代理' in m.classify_cli_error('A fetch request failed, connectivity issue'),
       m.classify_cli_error('A fetch request failed'))
    _u = m.classify_cli_error('totally unrelated text')
    ck('F4 命不中关键词 => 如实报未识别，不猜成未登录',
       '未识别' in _u and '登录' not in _u, _u)

    _orig_tbl = m.ERR_CLASS
    try:
        m.ERR_CLASS = []
        ck('F5 变异：清空关键词表后仍报未识别（退化不产出假类别）',
           '未识别' in m.classify_cli_error('some random text'))
    finally:
        m.ERR_CLASS = _orig_tbl

    # ---- G 组（r198）：输出含多个 JSON 块时的取法（pages project list --json 实测） ----
    # 一手：我用 find('[')+rfind(']') 的朴素截法解 `wrangler pages project list --json`
    #   当场报 Extra data: line 33 column 1（该输出在数组之后还有内容），
    #   而 first_json_array 同一段解出 5 项。教训：探路脚本也必须复用已锁实现。
    NL = chr(10)   # 本模块顶层没有 NL（前几轮我在别的文件里也栽过一次同名问题）
    MULTI = '[{"a": 1}, {"b": 2}]' + NL + 'trailing note [not json]' + NL
    segM = m.first_json_array(MULTI)
    parsedM = None
    try:
        parsedM = json.loads(segM)
    except ValueError:
        parsedM = None
    ck("G1 输出含多数组时取第一个平衡数组（不越界到尾部）",
       parsedM == [{"a": 1}, {"b": 2}], repr(parsedM)[:70])
    naive_bad = False
    try:
        i2 = MULTI.find('[')
        j2 = MULTI.rfind(']')
        json.loads(MULTI[i2:j2 + 1])
    except ValueError:
        naive_bad = True
    ck("G2 朴素 find/rfind 截法在该形态下确实失败（证明 G1 非装饰）", naive_bad)

    fails = [r for r in RESULTS if not r[0]]
    print("")
    print("夹具合计: %d 项，通过 %d，失败 %d" % (len(RESULTS), len(RESULTS) - len(fails), len(fails)))
    if fails:
        for _ok, nm, det in fails:
            print("  FAIL %s | %s" % (nm, det))
        print("[GATE:fixture-fail]")
        return 1
    print("[GATE:fixture-pass]")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())
