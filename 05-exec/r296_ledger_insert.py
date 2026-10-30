# -*- coding: utf-8 -*-
r"""r296_ledger_insert.py — 往 07 台账插入新条目的**跟踪工具**（r296）。

为什么要有它（三条都是我自己的）：
  ① commit 9e49b0f 里我写过「防空调正则的 assert 已固化进脚本」—— 核查为**假**：那 assert 只活在
     _temp/r295_*.py 一次性脚本里，git ls-files 扫全部跟踪 .py 命中 0。历史不可改写（R241），唯一
     诚实的处置是把它变成真的：做跟踪件。
  ② 插入台账这件事我历轮重写了 8 份一次性脚本（_temp/r291_lg2、r292_i4、r294_lg、r295_i2…），每份
     重新手写正则与断言 ⇒「正则被双重转义成永不匹配」这个坑复发 3 次。重复实现即重复犯错。
  ③ 现存跟踪件不顶用（先查再建）：r29b_stage_07_line.py 只暂存单行且无 argparse；r105_move_todo.py
     只搬移已成条目 —— 都不是「按锚点插入新条目」。

五道内建防线，--selftest 六腿逐条对应：
  A 防空调正则：条目正则命中 0 行 ⇒ REGEX-VACUOUS 非零退出。空集合会让后续每个断言假通过。
  B 幂等：待插 key 已存在 ⇒ 拒写（r289 我造过 R289-3 重复两次）。
  B2 拒隐形插入：待插编号必须能被本工具自己的条目正则认出；否则那一行对查重与账龄都不可见，
     防线被绕过（r296 探针实测：拿不合 R<digits>-<digits> 格式的编号演练时 rows_after 不变）。
  C 整块定位（r296 实战暴露、初版 selftest 抓不到，故补 e 腿）：07 台账有多物理行旧格式条目
     （实测 R132-4 占 221 行、R292-4 占 16 行）。只按标题行定位就往下一行插，会把该条目的正文与
     标题切开 —— 我 r294/r295 三次插入正是这样把 R292-4 的 15 行正文挤成孤儿块。正解 = 跳过锚点
     条目自己的全部续行，插到整块之后；续行判据 = 非空且不以「- [ ] **」或「#」开头。
  D 查重只限本轮号族：别轮既存重复**不**由本工具合并（r290 我全量 dedupe 误合并 R248/249/250-1
     三条并行会话撞号的双行，分句比对证明短版含长版没有的句子 = 有损）。
  E 逐行守恒：除插入块外原文件每行必须原样同序在位，否则拒写；行尾逐字节保持（07 主壳混合行尾）。

期望值一律从 seed/现文件算出，不写常量：我在这件事上连错两次（先凭印象写 rows_before=2，探针实测
改 3，改完 seed 又变 4）⇒ 写死的数本身就是易碎的假证据，与 A 腿防的是同一族。

用法：python 05-exec/r296_ledger_insert.py --items <json> --anchor <既有条目编号> --round <NNN>
退出码：0 成功 / 1 拒写（幂等、隐形插入、族内重复、锚点歧义、守恒失败、空调正则）/ 2 输入不可得。
末行：[LEDGER:INSERT] rows_before=<n> rows_after=<n> added=<n> fam_dup=0 integrity=ok
"""
import argparse
import collections
import io
import json
import os
import re
import sys
import tempfile

NL = chr(10)
KEY = re.compile(r"^- \[[ xX]\] \*\*(R\d+-\d+)")
BLOCK_STOP = re.compile(r"^- \[[ xX]\] \*\*|^#+ ")
ITEM_LINE = "- [ ] **{k}（r{round} 登记，{p}）** **{s}**：{d}"


def read_lines(path):
    """按 NL 切但保留每行自带的 CR，以便逐字节还原（07 主壳是混合行尾）。"""
    return io.open(path, encoding="utf-8", newline="").read().split(NL)


def collect_keys(lines):
    return [KEY.match(x).group(1) for x in lines if KEY.match(x)]


def block_end(lines, title_idx):
    """锚点条目整块的末尾下标（不含）：跳过其续行，停在下一条目/标题/空行之前。"""
    j = title_idx + 1
    while j < len(lines) and lines[j].strip() and not BLOCK_STOP.match(lines[j]):
        j += 1
    return j


def insert(root, items, anchor, round_no, ledger="memory/07-next-steps.md"):
    path = os.path.join(root, ledger)
    if not os.path.isfile(path):
        return 2, {"err": "台账不存在: " + ledger}
    if not items:
        return 2, {"err": "items 为空（无输入不判成功）"}
    lines = read_lines(path)
    keys = collect_keys(lines)
    if not keys:                                     # A 防空调正则
        return 1, {"err": "REGEX-VACUOUS：条目正则命中 0 行，判据自身失效，拒绝继续"}
    want = [x["k"] for x in items]
    probe = ITEM_LINE.format(k=want[0], round=round_no, p="P1", s="s", d="d")
    if not KEY.match(probe):                         # B2 拒隐形插入
        return 1, {"err": "待插编号不合台账条目格式（KEY 认不出），拒绝隐形插入",
                   "keys": want[:3]}
    dup_key = [k for k in want if k in set(keys)]    # B 幂等
    if dup_key:
        return 1, {"err": "key 已存在，拒重复插入", "keys": dup_key}
    idxs = [i for i, x in enumerate(lines) if x.startswith("- [ ] **" + anchor)]
    if not idxs:
        return 2, {"err": "锚点不存在: " + anchor, "entries": len(keys)}
    if len(idxs) > 1:                                # 同 r46：歧义即拒，不猜位置
        return 1, {"err": "锚点命中多行（歧义）", "lines": [i + 1 for i in idxs]}
    pos = idxs[0]
    end = block_end(lines, pos)                      # C 整块定位
    crlf = lines[end - 1].endswith(chr(13))
    blk = [ITEM_LINE.format(k=x["k"], round=round_no, p=x["p"], s=x["s"], d=x["d"]) for x in items]
    if crlf:
        blk = [b + chr(13) for b in blk]
    out = lines[:end] + blk + lines[end:]
    ks2 = collect_keys(out)
    fam = "R%s-" % round_no                          # D 查重只限本轮号族
    fam_dup = [k for k, v in sorted(collections.Counter(ks2).items())
               if v > 1 and k.startswith(fam)]
    if fam_dup:
        return 1, {"err": "本轮号族内出现重复条目", "keys": fam_dup}
    if out[:end] != lines[:end] or out[end + len(blk):] != lines[end:]:   # E 守恒
        return 1, {"err": "守恒失败：非插入块的原行被改动，拒绝写盘"}
    tmp = path + ".r296tmp"
    io.open(tmp, "w", encoding="utf-8", newline="").write(NL.join(out))
    os.replace(tmp, path)
    return 0, {"rows_before": len(keys), "rows_after": len(ks2), "added": len(blk),
               "anchor_line": pos + 1, "inserted_after_line": end,
               "skipped_body_lines": end - pos - 1, "fam_dup": 0, "integrity": "ok",
               "eol": "crlf" if crlf else "lf"}


SEED_DUP = "- [ ] **R200-9（r200 登记，P1）** **别轮既存重复行（本工具不得合并）**：正文"


def mk_ledger(dirpath, extra_body=False):
    """造最小台账。重复行用独立编号 R200-9：若把 R200-1 也做成两条，e 腿就没有唯一锚点了。"""
    os.makedirs(os.path.join(dirpath, "memory"), exist_ok=True)
    seed = ["- [ ] **R200-1（r200 登记，P1）** **甲**：正文甲"]
    if extra_body:                     # 多物理行条目（e 腿用）
        seed += ["   甲的续行第一句", "   甲的续行第二句"]
    seed += [SEED_DUP, SEED_DUP,
             "- [ ] **R240-1（r240 登记，P2）** **乙**：正文", "## 其他节", "普通文本行"]
    io.open(os.path.join(dirpath, "memory", "07-next-steps.md"), "w",
            encoding="utf-8", newline="").write(NL.join(seed) + NL)


def ledger_path(root):
    return os.path.join(root, "memory", "07-next-steps.md")


def selftest():
    it = [{"k": "R296-1", "p": "P1", "s": "丙", "d": "说明"}]
    d = tempfile.mkdtemp(prefix="r296_a_")
    mk_ledger(d)
    n0 = len(collect_keys(read_lines(ledger_path(d))))     # 期望值现算，不写常量
    rc, r1 = insert(d, it, "R240-1", 296)
    leg_a = (rc == 0 and r1.get("rows_before") == n0 and r1.get("rows_after") == n0 + 1
             and r1.get("added") == 1 and n0 >= 2 and r1.get("integrity") == "ok")
    rc2, r2 = insert(d, it, "R240-1", 296)
    leg_b = rc2 == 1 and r2.get("keys") == ["R296-1"]
    rc3, r3 = insert(d, [{"k": "X-1", "p": "P1", "s": "庚", "d": "x"}], "R240-1", 296)
    leg_b2 = rc3 == 1 and "隐形插入" in str(r3.get("err"))
    rc4, r4 = insert(d, [{"k": "R296-8", "p": "P1", "s": "丁", "d": "x"}], "NO_SUCH", 296)
    leg_c = rc4 == 2
    d2 = tempfile.mkdtemp(prefix="r296_vac_")
    os.makedirs(os.path.join(d2, "memory"))
    io.open(ledger_path(d2), "w", encoding="utf-8", newline="").write("没有条目声明的卷" + NL)
    rc5, r5 = insert(d2, [{"k": "R296-2", "p": "P1", "s": "戊", "d": "y"}], "R9", 296)
    leg_d = rc5 == 1 and "REGEX-VACUOUS" in str(r5.get("err"))
    d3 = tempfile.mkdtemp(prefix="r296_ml_")
    mk_ledger(d3, extra_body=True)
    rc6, r6 = insert(d3, [{"k": "R296-3", "p": "P1", "s": "己", "d": "z"}], "R200-1", 296)
    aft = read_lines(ledger_path(d3))
    ti = next(k for k, x in enumerate(aft) if x.startswith("- [ ] **R200-1"))
    leg_e = (rc6 == 0 and r6.get("skipped_body_lines") == 2
             and aft[ti + 1].strip().startswith("甲的续行第一句")
             and aft[ti + 3].startswith("- [ ] **R296-3")
             and r6.get("anchor_line") == ti + 1)
    rows = [("a happy-path（期望从 seed 现算）", leg_a),
            ("b 重复同 key 被拒", leg_b),
            ("b2 不合格式的编号被拒（防隐形插入）", leg_b2),
            ("c 锚点不存在 rc=2", leg_c),
            ("d 空调正则被识破", leg_d),
            ("e 多行锚点不切开正文（跳过 2 续行）", leg_e)]
    ok = 0
    for nm, good in rows:
        print("%s %s" % ("PASS" if good else "FAIL", nm))
        ok += 1 if good else 0
    print("[SELFTEST] legs=%d passed=%d" % (len(rows), ok))
    return 0 if ok == len(rows) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", help="JSON：items 数组，或 {items: [...]}")
    ap.add_argument("--anchor", default="", help="插在哪个既有条目整块之后（须唯一命中）")
    ap.add_argument("--round", default="", help="本轮轮号，如 296")
    ap.add_argument("--root", default=".")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if not (a.items and a.anchor and a.round):
        ap.error("--items/--anchor/--round 三者皆必填（缺输入不猜）")
    if not os.path.isfile(a.items):
        print("[LEDGER:INSERT] err=items 文件不存在: %s" % a.items)
        return 2
    data = json.load(io.open(a.items, encoding="utf-8"))
    items = data["items"] if isinstance(data, dict) else data
    rc, rep = insert(a.root, items, a.anchor, a.round)
    if rc != 0:
        print("[LEDGER:INSERT] REFUSED rc=%d %s" % (rc, json.dumps(rep, ensure_ascii=False)[:240]))
        return rc
    print("   anchor_line=%s inserted_after_line=%s skipped_body_lines=%s eol=%s"
          % (rep["anchor_line"], rep["inserted_after_line"], rep["skipped_body_lines"], rep["eol"]))
    print("[LEDGER:INSERT] rows_before=%d rows_after=%d added=%d fam_dup=%d integrity=%s"
          % (rep["rows_before"], rep["rows_after"], rep["added"], rep["fam_dup"], rep["integrity"]))
    return 0


if __name__ == "__main__":
    main()
