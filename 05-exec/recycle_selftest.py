# -*- coding: utf-8 -*-
"""D4 回收站自检（R238 两层含对照）

层 a（隔离桩，monkeypatch 掉「系统回收站可用」以走到回落分支）：
  A1 anchor_for 就近命中含 .git 的根
  A2 recycle 不存在路径 → ok=False 且 manifest 不增长（反例：不得静默成功）
  A3 recycle 回落 _trash → 原路径消失 + dest 存在 + method='trash'
  A4 restore 复原 → 原路径回来且 **SHA256 与删除前一致**（判据是哈希，不是「文件回来了」）
  A5 同一 id 二次 restore → ok=False（备份已不在 _trash，不得静默成功）
层 b（真机集成，走真实 CLI 子进程）：
  B1 系统回收站路径：真文件 → `handoff.py recycle <file>` → ok=True、原路径消失、manifest 有记录
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from _lib import force_utf8_stdout

force_utf8_stdout()
HANDOFF = Path(r"D:\global_skills\A-project-handoff\scripts\handoff.py")
sys.path.insert(0, r"D:\global_skills\A-project-handoff\scripts")

import handoff_lib.recycle as R  # noqa: E402

CASES = []


def ck(name, got, want):
    CASES.append((name, got, want, got == want))


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    root = Path(tempfile.mkdtemp(prefix="recycle_probe_"))
    (root / ".git").mkdir()
    work = root / "sub" / "deep"
    work.mkdir(parents=True)
    (root / "memory").mkdir()

    # A1
    ck("A1 anchor_for 就近命中含 .git 的根", str(R.anchor_for(work / "x.txt")), str(root.resolve()))

    # A2 反例：不存在路径
    before = len(R.read_manifest(root))
    r_missing = R.recycle(work / "not-exist.txt", anchor=root)
    ck("A2 不存在路径 → ok=False", r_missing.get("ok"), False)
    ck("A2 manifest 不增长", len(R.read_manifest(root)), before)

    # A3/A4 回落分支（patch 掉回收站可用性）
    f = work / "target.txt"
    f.write_text("RECYCLE-PROBE-αβγ\n", encoding="utf-8")
    h0 = sha(f)
    orig_avail = R.recycle_bin_available
    R.recycle_bin_available = lambda p: False
    try:
        r3 = R.recycle(f, anchor=root, reason="selftest")
    finally:
        R.recycle_bin_available = orig_avail
    ck("A3 ok=True", r3.get("ok"), True)
    ck("A3 method='trash'（回落生效）", r3.get("method"), "trash")
    ck("A3 原路径已消失", f.exists(), False)
    ck("A3 dest 存在", Path(r3.get("dest", "")).exists(), True)
    ck("A3 台账已记录", len(R.read_manifest(root)), before + 1)

    r4 = R.restore(root, r3["id"])
    ck("A4 restore ok=True", r4.get("ok"), True)
    ck("A4 复原后路径存在", f.exists(), True)
    ck("A4 复原后 SHA256 与删除前一致", sha(f), h0)

    r5 = R.restore(root, r3["id"])
    ck("A5 二次 restore → ok=False（不静默成功）", r5.get("ok"), False)

    # B1 真机：系统回收站路径
    b1 = work / "to_bin.txt"
    b1.write_text("BIN-PROBE\n", encoding="utf-8")
    env = dict(os.environ, PYTHONPYCACHEPREFIX=os.environ.get("TEMP", "") + r"\pycache_verify")
    cp = subprocess.run([sys.executable, str(HANDOFF), "recycle", str(b1),
                         "--anchor", str(root), "--reason", "selftest-B1"],
                        capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    # 判据自证（R263）：CLI 是多段输出（JSON + 还原指引行），必须用 raw_decode 从首个 '{' 起解析；
    # 只取首行会得到 "{" → 解析失败 → 误判 ok=None（首版就是这么错的）。
    out = {}
    i = cp.stdout.find("{")
    if i >= 0:
        try:
            out, _ = json.JSONDecoder().raw_decode(cp.stdout[i:])
        except Exception:
            out = {}
    ck("B1 CLI 退出码 0", cp.returncode, 0)
    ck("B1 解析到 JSON（判据非空输入）", bool(out), True)
    ck("B1 ok=True", out.get("ok"), True)
    ck("B1 原路径已消失", b1.exists(), False)
    # 台账条数：A3 回收(1) + A4 复原(1) + B1 回收(1) = before + 3（复原也记账，属设计内）
    ck("B1 台账条数 = before+3", len(R.read_manifest(root)), before + 3)
    b1_method = out.get("method")
    ck("B1 method ∈ {recycle_bin, trash}", b1_method in ("recycle_bin", "trash"), True)

    failed = [c for c in CASES if not c[3]]
    for name, got, want, ok in CASES:
        print(("[PASS] " if ok else "[FAIL] ") + name + " | got=" + repr(got) + " want=" + repr(want))
    print("---- 层a/层b 合计：%d/%d 通过（B1 实际 method=%s）----"
          % (len(CASES) - len(failed), len(CASES), b1_method))
    shutil.rmtree(root, ignore_errors=True)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
