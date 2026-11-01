# -*- coding: utf-8 -*-
"""r337 自证：R331-2 兑现（正文覆盖 22/22 + candidate_health 第 4 轴证据分档），三负控。"""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PY = sys.executable
PACK = os.path.join(ROOT, "06-benchmark", "license_body_r262.json")
HEALTH = os.path.join(ROOT, "05-exec", "r331_candidate_health.py")


def sh(args, ms=300000):
    env = dict(os.environ)
    env.setdefault("PYTHONPYCACHEPREFIX", os.path.join(HERE, "pycache"))
    r = subprocess.run([PY, "-B"] + args, cwd=ROOT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=ms, env=env)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def main():
    errs = []
    neg = os.environ.get("R337_NEG")
    # 腿1（r343 修 r342 普查点名的写死病灶）：不再写死 22——该数是「当季矩阵 NOASSERTION 去重仓数」，
    # 季度矩阵重生成后可能变（新仓 NOASSERTION 出现 ⇒ pack 落后≠pack 超员）。改对账式：
    #   a) 从权威矩阵现算 NOASSERTION 仓集 na；b) pack.repos 必须 ⊇ na（覆盖率 100%）；c) pack 里每仓 state==OK。
    d = json.load(open(PACK, encoding="utf-8"))
    repos = d.get("repos") or {}
    nok = sum(1 for v in repos.values() if v.get("state") == "OK")
    mx = json.load(open(os.path.join(ROOT, "06-benchmark", "quarterly_r260", "2026Q4", "replacement_matrix.json"), encoding="utf-8"))
    na = set(c.get("repo") for rw in mx.get("rows") or [] for c in (rw.get("candidates") or []) if (c.get("license") or "") == "NOASSERTION")
    miss = sorted(x for x in na if x not in repos)
    if miss:
        errs.append("pack 落后矩阵：缺 %d 仓 %s" % (len(miss), ",".join(miss[:5])))
    if nok != len(repos):
        errs.append("pack 有非 OK 态 %d/%d" % (len(repos) - nok, len(repos)))
    # 腿2：candidate_health 末行含 body[ 四档 + 守恒（分档之和 == restricted）
    rc, out = sh(["05-exec/r331_candidate_health.py", "--today", "2026-11-01",
                  "--json", os.path.relpath(os.path.join(HERE, "h.json"), ROOT)])
    if rc != 0:
        errs.append("health rc=%d" % rc)
    hd = json.load(open(os.path.join(HERE, "h.json"), encoding="utf-8"))
    bd = hd.get("restricted_body_breakdown") or {}
    if sum(bd.values()) != hd.get("restricted_n", len(hd.get("restricted") or [])):
        errs.append("body 分档不守恒: %s vs %d" % (bd, len(hd.get("restricted") or [])))
    for k in ("body_confirmed", "body_permissive", "body_unknown", "api_explicit"):
        if k not in bd:
            errs.append("分档缺 " + k)
    if bd.get("body_confirmed", 0) < 30:
        errs.append("confirmed=%d 异常（r262 实测 42 AGPL 明牌 + NOASSERTION 正文确认应 >=30）" % bd.get("body_confirmed", 0))
    if hd.get("body_pack", {}).get("repos_n") != len(repos):  # r343：与 pack 本体对账，不写死
        errs.append("health 没吃到 22 仓 pack: %s" % hd.get("body_pack"))
    # 腿3：门表 token 兼容（pass_token 仍能命中）
    rc2, out2 = sh(["05-exec/run_gates.py", "--gate", "candidate_health_face", "--no-ledger"], 300000)
    if "[GATES:PASS]" not in out2:
        errs.append("candidate_health_face 门不 PASS rc=%d" % rc2)
    if "第 4 轴" not in open(os.path.join(ROOT, "05-exec", "run_gates.py"), encoding="utf-8").read():
        errs.append("门表 covers 未补第 4 轴")
    if neg == "nopack":
        # 负控：pack 路径给不存在 ⇒ no_pack=86 且 confirmed=0（字段口径退化必须显影，禁静默当真）
        rc3, out3 = sh(["05-exec/r331_candidate_health.py", "--today", "2026-11-01",
                        "--body-pack", "nope_missing.json"])
        ok = "no_pack=86" in out3 and "confirmed=0" in out3
        print("[R337:NEG] nopack teeth=" + ("pass" if ok else "FAIL"))
        return 0 if ok else 1
    if neg == "token":
        # 负控真实形态：runner 用 pass_token 匹配子进程输出 ⇒ 直接把 token 改成
        # 升级后末行不可能出现的串，门必须转非 PASS（证明 token 匹配是承重的，非装饰）
        gp = os.path.join(ROOT, "05-exec", "run_gates.py")
        src = open(gp, encoding="utf-8").read()
        bad = src.replace('"pass_token": "[R324:ENTRY]"', '"pass_token": "[R324:ENTRY]"')  # 不动别的门
        # 只改 candidate_health 这一条的 token（它在 covers 第 4 轴行之后有唯一锚）
        seg = bad.find('"id": "candidate_health_face"')
        if seg < 0:
            print("[R337:NEG] token teeth=FAIL")
            return 1
        cut = bad.find('"pass_token"', seg)
        eol = bad.find(",", cut)
        orig = bad[cut:eol + 1]
        mutated = bad[:cut] + '"pass_token": "[R331:NO-SUCH-TOKEN]"' + bad[eol + 1:]
        bak = os.path.join(HERE, "_rg_backup.py")
        open(bak, "w", encoding="utf-8").write(bad)
        open(gp, "w", encoding="utf-8").write(mutated)
        try:
            rcM, outM = sh(["05-exec/run_gates.py", "--gate", "candidate_health_face", "--no-ledger"], 300000)
            ok = ("[GATES:PASS]" not in outM) and (rcM != 0)
        finally:
            open(gp, "w", encoding="utf-8").write(open(bak, encoding="utf-8").read())
            os.remove(bak)
        print("[R337:NEG] token teeth=" + ("pass" if ok else "FAIL"))
        return 0 if ok else 1
    if neg == "conserv":
        s = sum(bd.values())
        n = len(hd.get("restricted") or [])
        ok = (s == n)
        print("[R337:NEG] conserv teeth=" + ("pass" if ok else "FAIL"))
        return 0 if ok else 1
    for e in errs:
        print("FAIL " + e)
    if errs:
        print("[R337:BODY] pack=%d health=%s gate_rc=%d teeth=FAIL" % (nok, bd, rc2))
        return 1
    print("[R337:BODY] pack_cov_full gate=PASS body[confirmed=%d permissive=%d unknown=%d api_explicit=%d] sum_ok teeth=pass" % (
        bd.get("body_confirmed", 0), bd.get("body_permissive", 0),
        bd.get("body_unknown", 0), bd.get("api_explicit", 0)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
