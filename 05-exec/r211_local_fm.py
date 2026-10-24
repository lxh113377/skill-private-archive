# -*- coding: utf-8 -*-
r"""r211_local_fm.py — 第 ⑥ 段（替代候选面）的本地输入面生成器（W-46 死句柄补口）。

存在理由（r211 一手，需求 5 的长效机制实测断裂）：
  `r114_replacement_scan.py` 读 `--local-fm`（缺省 `_temp/local_fm_r114.json`）作为
  「本地在册件 + 其 description」的输入面。该件全仓实测：
    · `git log --all -- "**/local_fm_r114.json"` 零命中 ⇒ **从未入库**；
    · `git grep -n local_fm` 只有读侧三行，**没有任何生成器**；
    · 它落在 `_temp/`，而 _temp 是多会话共用目录，已被并行会话按扩展名无差别清场
      过 212 件（本仓 R189-2 自登）。
  ⇒ 三重叠加的结果：季度巡检第 ⑥ 段**永久跑不起来**（实测 `--offline` 报
  `[REPL:UNVERIFIED] 本地 frontmatter 面缺失`，rc=2）。这就是本仓 W-46
  「pattern 必须有生成器」管的形态：一次性内联脚本产出的证据件 = 死句柄。

口径（单源，禁第二套枚举）：
  权威源枚举 = `D:\global_skills\<dir>\SKILL.md` 存在为准（与 r112_provenance_scan
  同一谓词）；description 解析**复用** r112_provenance_scan.fm_field（同一函数同一入参），
  不另写一份 frontmatter 解析器（两份算法必漂移 —— 本仓 r191b 刚为此立过同键选件）。

产物字段（消费方 r114_replacement_scan 逐字段要求，多一个不写、少一个即红）：
  slug / desc / desc_len / local_bytes

零输入不得记绿（R247）：权威源不可读、或扫出 0 件 ⇒ rc=2 且不写主产物。

用法：
  python 05-exec/r211_local_fm.py [--json <件>]
  python 05-exec/r211_local_fm.py --check          # 只验现存件是否仍与盘上一致（零写）
退出码：0 出件 / 2 输入面或产物不可用。
"""
import argparse
import hashlib
import io
import json
import os
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BENCH = os.path.join(ROOT, "06-benchmark")
DEFAULT_OUT = os.path.join(BENCH, "local_frontmatter.json")
AUTHORITY = r"D:\global_skills"
TOKEN = "[LOCALFM:PASS]"


def _import_fm_field():
    """复用 provenance 扫描件的 frontmatter 解析器（单源；取不到即 UNVERIFIED，不自写副本）。"""
    sys.path.insert(0, HERE)
    try:
        import r112_provenance_scan as prov
    except Exception as exc:  # noqa: BLE002
        return None, "import_fail:%r" % (exc,)
    fn = getattr(prov, "fm_field", None)
    if not callable(fn):
        return None, "fm_field_missing"
    return fn, None


def scan_authority(authority):
    """枚举在册件。返回 (rows, note)。note 非空即面不可用。"""
    if not os.path.isdir(authority):
        return [], "authority_missing:%s" % authority
    fm_field, err = _import_fm_field()
    if fm_field is None:
        return [], err
    rows = []
    unreadable = []
    for name in sorted(os.listdir(authority)):
        md = os.path.join(authority, name, "SKILL.md")
        if not os.path.isfile(md):
            continue
        try:
            raw = io.open(md, "rb").read()
        except OSError:
            unreadable.append(name)
            continue
        text = raw.decode("utf-8-sig", "replace")
        desc = fm_field(text, "description") or ""
        rows.append({"slug": name,
                     "desc": desc,
                     "desc_len": len(desc),
                     "local_bytes": len(raw)})
    if unreadable:
        return rows, "unreadable:%d:%s" % (len(unreadable), ",".join(unreadable[:6]))
    return rows, None


def atomic_write(path, doc):
    tmp = path + ".%d.tmp" % os.getpid()
    with io.open(tmp, "w", encoding="utf-8", newline="") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", dest="out", default=DEFAULT_OUT)
    ap.add_argument("--authority", default=AUTHORITY)
    ap.add_argument("--check", action="store_true",
                    help="只校验现存产物与盘上一致（零写）")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE002
        pass

    rows, note = scan_authority(args.authority)
    if not rows:
        print("[LOCALFM:UNVERIFIED] 本地面不可用/零件 ⇒ 禁按无缺口记绿（R247）｜%s" % (note or "零命中"))
        return 2
    doc = {"schema": "local-frontmatter-r211-v1",
           "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00"),
           "cmd": "python 05-exec/r211_local_fm.py",
           "authority": args.authority.replace("\\", "/"),
           "n": len(rows),
           "face_note": note,
           "parser_source": "r112_provenance_scan.fm_field",
           "rows": rows}
    if args.check:
        if not os.path.isfile(args.out):
            print("[LOCALFM:UNVERIFIED] --check 但产物不存在: %s" % args.out)
            return 2
        old = json.load(io.open(args.out, encoding="utf-8"))
        same = (old.get("rows") == rows)
        print("[LOCALFM:%s] 产物 %d 件 ⇄ 盘上现扫 %d 件（一致=%s）｜面注=%s"
              % ("PASS" if same else "DRIFT", len(old.get("rows") or []), len(rows), same, note or "-"))
        return 0 if same else 1
    atomic_write(args.out, doc)
    if not args.quiet:
        print("本地在册面 %d 件（权威源 %s）｜desc 均取自 frontmatter｜解析器单源=provenance 件"
              % (len(rows), args.authority))
        if note:
            print("  ⚠️ 面注（不静默吞）：%s" % note)
    print("%s n=%d -> %s" % (TOKEN, len(rows), os.path.relpath(args.out, ROOT)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
