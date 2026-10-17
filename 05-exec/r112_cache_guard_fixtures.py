# -*- coding: utf-8 -*-
r"""r112_cache_guard_fixtures.py — cache-guard 双腿夹具（W-47 双向证据）。

被测缺陷（r112 一手，2026-10-17 22:13 实测）：
  r112_upstream_probe.fetch_candidate 原先**无论取数成功与否都写缓存**，一次网络 EOF 就把
  已有的 14KB 好件覆写成 280B 的 {ok:false,error:...}，随后 --offline 复算把「已升级」的件
  读成 UNVERIFIED（ok_n 24→18，UNVERIFIED 15→21）。
  这是「取数失败不得销毁已有证据」，与 R247「零输入不得当绿」互为反向。

腿：
  g1 应绿的绿：成功件在盘 ⇒ 之后取数失败，旧件字节与内容不变，且失败痕迹记进 cache_error
  g2 应红的红：变异体（把守卫摘掉、恢复成无条件写）⇒ g1 必须转红，证明夹具真有鉴别力
  g3 成功仍覆盖：成功后缓存内容必须换成新件（防修过头变成「永不更新」）
  g4 无旧件时失败照写失败件：不得因为守卫把「本来就没证据」也当成有证据
"""
import io
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import r112_upstream_probe as P  # noqa: E402


def _write(path, obj):
    io.open(path, "w", encoding="utf-8", newline="\n").write(json.dumps(obj, ensure_ascii=False))


def leg_g1():
    tmp = tempfile.mkdtemp(prefix="cg1_")
    try:
        p = os.path.join(tmp, "r_x__s.json")
        good = {"repo": "r/x", "path": "a/SKILL.md", "slug": "s", "ok": True,
                "fetched_epoch": 1.0, "from_cache": False, "sha256": "h",
                "bytes": 2, "content_b64": "aGk="}
        _write(p, good)
        before = io.open(p, "rb").read()
        orig = P.gh_api
        P.gh_api = lambda path: (None, "rc=1:simulated EOF")
        try:
            rec = P.fetch_candidate("r/x", "a/SKILL.md", "s", tmp, 0, True)
        finally:
            P.gh_api = orig
        on_disk = json.load(io.open(p, encoding="utf-8"))
        ok = (on_disk.get("ok") is True
              and on_disk.get("content_b64") == "aGk="
              and bool(on_disk.get("cache_error"))
              and rec.get("ok") is True
              and rec.get("from_cache") is False
              and len(before) < 1000)
        return ok, "旧件内容保留=%s 失败留痕=%s" % (on_disk.get("content_b64") == "aGk=",
                                                     bool(on_disk.get("cache_error")))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def leg_g3():
    tmp = tempfile.mkdtemp(prefix="cg3_")
    try:
        good = {"repo": "r/x", "path": "a/SKILL.md", "slug": "s", "ok": True,
                "fetched_epoch": 1.0, "content_b64": "b2xk", "sha256": "h1", "bytes": 3}
        _write(os.path.join(tmp, "r_x__s.json"), good)
        import base64
        newraw = b"new content"
        payload = json.dumps({"content": base64.b64encode(newraw).decode("ascii"),
                              "sha": "blobnew"})
        orig = P.gh_api
        def fake(path):
            if path.startswith("repos/r/x/contents/"):
                return payload, None
            return "[]", None
        P.gh_api = fake
        try:
            rec = P.fetch_candidate("r/x", "a/SKILL.md", "s", tmp, 0, True)
        finally:
            P.gh_api = orig
        return (rec.get("ok") is True and rec.get("sha256") == __import__("hashlib").sha256(newraw).hexdigest(),
                "成功路径仍覆盖：sha256=%s" % (rec.get("sha256") or "None")[:12])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def leg_g4():
    tmp = tempfile.mkdtemp(prefix="cg4_")
    try:
        orig = P.gh_api
        P.gh_api = lambda path: (None, "rc=1:simulated EOF")
        try:
            rec = P.fetch_candidate("r/x", "a/SKILL.md", "s", tmp, 0, True)
        finally:
            P.gh_api = orig
        p = os.path.join(tmp, "r_x__s.json")
        on_disk = json.load(io.open(p, encoding="utf-8")) if os.path.isfile(p) else None
        return (rec.get("ok") is False and on_disk is not None and on_disk.get("ok") is False,
                "无旧件时失败照样落失败件（不得凭空当成已有证据）")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _legacy_fetch_candidate(repo, path, slug, cache_dir, ttl_sec, refresh):
    """修复前的旧实现（照抄 r112 改前源码语义）：无论成功与否都写缓存。"""
    import base64
    cache_p = os.path.join(cache_dir, "%s__%s.json" % (repo.replace("/", "_"), slug))
    rec = {"repo": repo, "path": path, "slug": slug, "ok": False,
           "fetched_epoch": 1.0, "from_cache": False}
    out, err = P.gh_api("repos/%s/contents/%s" % (repo, path))
    if err:
        rec["error"] = err
    else:
        d = json.loads(out)
        raw = base64.b64decode(d["content"])
        rec.update({"ok": True,
                    "sha256": __import__("hashlib").sha256(raw).hexdigest(),
                    "bytes": len(raw), "blob_sha": d.get("sha"),
                    "content_b64": base64.b64encode(raw).decode("ascii")})
    os.makedirs(cache_dir, exist_ok=True)
    io.open(cache_p, "w", encoding="utf-8", newline="\n").write(
        json.dumps(rec, ensure_ascii=False, sort_keys=True))
    return rec


def _g1_assertion_on(fetch_fn):
    """在临时目录里跑「好件 + 随后失败」序列，返回该实现是否守住了旧证据。"""
    tmp = tempfile.mkdtemp(prefix="cgm_")
    try:
        p = os.path.join(tmp, "r_x__s.json")
        good = {"repo": "r/x", "path": "a/SKILL.md", "slug": "s", "ok": True,
                "fetched_epoch": 1.0, "from_cache": False, "sha256": "h",
                "bytes": 2, "content_b64": "aGk="}
        _write(p, good)
        orig = P.gh_api
        P.gh_api = lambda path: (None, "rc=1:simulated EOF")
        try:
            fetch_fn("r/x", "a/SKILL.md", "s", tmp, 0, True)
        finally:
            P.gh_api = orig
        on_disk = json.load(io.open(p, encoding="utf-8"))
        return (on_disk.get("ok") is True and on_disk.get("content_b64") == "aGk=")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def leg_g2_mutation():
    """变异腿：把守卫摘掉（用旧实现替换）⇒ g1 的同一断言必须失败，证明鉴别力来自该守卫。

    双向：现行实现下断言通过（绿），旧实现下断言失败（红）。两侧都要成立，缺一即本腿红。
    """
    current_ok = _g1_assertion_on(P.fetch_candidate)
    legacy_ok = _g1_assertion_on(_legacy_fetch_candidate)
    passed = bool(current_ok) and not bool(legacy_ok)
    return (passed, "现行=%s 旧实现=%s（旧实现须不守住旧证据）" % (current_ok, legacy_ok))

def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    legs = [("g1", leg_g1), ("g3", leg_g3), ("g4", leg_g4), ("g2", leg_g2_mutation)]
    n_pass = 0
    for name, fn in legs:
        ok, detail = fn()
        print("%s %-4s %s" % ("PASS" if ok else "FAIL", name, detail))
        if ok:
            n_pass += 1
    print("夹具合计: %d 项，通过 %d，失败 %d" % (len(legs), n_pass, len(legs) - n_pass))
    if n_pass == len(legs):
        print("[GATE:fixture-pass] cache-guard 双向自证（应绿的绿 + 变异体被抓住）")
        return 0
    print("[GATE:fixture-fail]")
    return 1


if __name__ == "__main__":
    sys.exit(main())