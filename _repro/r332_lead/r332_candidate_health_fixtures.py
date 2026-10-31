# -*- coding: utf-8 -*-
"""r332 候选健康门的夹具（三态）：证明该门不是恒绿。

三腿（全部用临时矩阵，不碰真件）：
  t1 正常面      ⇒ rc=0 且末行含 [R331:HEALTH]
  t2 stale 超顶  ⇒ rc=1 且必须打印 [R331:STALE-OVER]（把阈值调到 0 或造全 stale 矩阵都能触发）
  t3 空候选面    ⇒ rc=2 UNVERIFIED（禁按 0 条记绿，R247）
另加变异腿 m1：把 --max-stale-rate 调到 1.0（100%）⇒ 同一超顶矩阵必须转绿（证明阈值真的在起作用、不是硬编码红）。
"""
import datetime, io, json, os, subprocess, sys, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SCRIPT = os.path.join(ROOT, "05-exec", "r331_candidate_health.py")
PY = sys.executable


def run(args, timeout=180):
    env = dict(os.environ)
    env.setdefault("PYTHONPYCACHEPREFIX", os.path.join(HERE, "pycache"))
    r = subprocess.run([PY, "-B", SCRIPT] + args, cwd=ROOT, capture_output=True,
                       text=True, encoding="utf-8", errors="replace", timeout=timeout, env=env)
    return r.returncode, (r.stdout or ""), (r.stderr or "")


def make_matrix(path, cands, quiet=True):
    row = {"slug": "probe-skill", "candidates": cands}
    io.open(path, "w", encoding="utf-8").write(json.dumps(
        {"generated_at": "2026-11-01T00:00:00+00:00", "rows": [row]}, ensure_ascii=False))


def main():
    d = os.path.join(HERE, "_fixture_m")  # 用仓内固定目录，避开 Windows 临时目录 + 相对化路径的坑
    os.makedirs(d, exist_ok=True)
    fails = []
    passes = []
    # t1 正常面：一个新鲜、未归档、MIT 的候选
    p1 = os.path.join(d, "m1.json")
    make_matrix(p1, [{"repo": "ok/repo", "pushed_at": "2026-10-25", "archived": False,
                      "license": "MIT", "stars": 100}])
    rc, out, err = run(["--matrix", p1, "--today", "2026-11-01"])
    if rc == 0 and "[R331:HEALTH]" in out:
        passes.append("t1 正常面 rc=0")
    else:
        fails.append("t1 正常面异常 rc=%d :: %s" % (rc, out.strip()[:100]))
    # t2 stale 超顶：两个候选全超 365 天 ⇒ 阈值 2% 下必红
    p2 = os.path.join(d, "m2.json")
    make_matrix(p2, [{"repo": "old/a", "pushed_at": "2024-01-01", "archived": False, "license": "MIT"},
                     {"repo": "old/b", "pushed_at": "2023-06-01", "archived": False, "license": "MIT"}])
    rc2, out2, _ = run(["--matrix", p2, "--today", "2026-11-01"])
    if rc2 == 1 and "[R331:STALE-OVER]" in out2:
        passes.append("t2 stale 超顶 rc=1")
    else:
        fails.append("t2 未按超顶判红 rc=%d :: %s" % (rc2, out2.strip()[:100]))
    # m1 变异：同矩阵 + 阈值 100% ⇒ 必须转绿（证明阈值承重）
    rc3, out3, _ = run(["--matrix", p2, "--today", "2026-11-01", "--max-stale-rate", "1.0"])
    if rc3 == 0 and "[R331:STALE-OVER]" not in out3:
        passes.append("m1 阈值放宽必转绿")
    else:
        fails.append("m1 阈值不承重 rc=%d" % rc3)
    # t3 空候选面 ⇒ rc=2
    p3 = os.path.join(d, "m3.json")
    make_matrix(p3, [])
    rc4, out4, _ = run(["--matrix", p3, "--today", "2026-11-01"])
    if rc4 == 2 and "UNVERIFIED" in out4:
        passes.append("t3 空面 rc=2 UNVERIFIED")
    else:
        fails.append("t3 空面未判 UNVERIFIED rc=%d :: %s" % (rc4, out4.strip()[:100]))
    # t4 矩阵不存在 ⇒ rc=2
    rc5, out5, _ = run(["--matrix", os.path.join(d, "nope.json"), "--today", "2026-11-01"])
    if rc5 == 2:
        passes.append("t4 矩阵缺失 rc=2")
    else:
        fails.append("t4 矩阵缺失未判 rc=2（实得 %d）" % rc5)
    for x in passes:
        print("PASS " + x)
    for x in fails:
        print("FAIL " + x)
    shutil.rmtree(d, ignore_errors=True)
    n = len(passes) + len(fails)
    if fails:
        print("[R332:FIXTURE] %d/%d teeth=FAIL" % (len(passes), n))
        return 1
    print("[R332:FIXTURE] %d/%d teeth=pass" % (len(passes), n))
    return 0


if __name__ == "__main__":
    sys.exit(main())
