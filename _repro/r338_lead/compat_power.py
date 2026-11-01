# -*- coding: utf-8 -*-
"""r338 分析（只读，不改尺）：compat 维在「现行量尺」（r261 许可封顶 + r262 正文指纹）下的判别力实测。

背景（一手）：r260 的 compat 腿只有二值 license 判定 ⇒ 三子腿 95% 恒真、删它 rank0 换面 0/191（零排序贡献，
R326-3 挂账）。r261 之后 score5 里加了 `license_cap`（LICENSE_CAPS: copyleft/restricted=1、unknown=4、
permissive=5），r262 又接进正文指纹 ⇒ **现行尺已带许可档**，但 2026Q4 矩阵是 r260 生成的、存的是旧分。
本分析 = 拿现尺把这 937 个候选的 compat 重算一遍，看判别力是否已经回来（给 R263 评审包出真数，不改任何判据本体）。

口径纪律：
  · 复用 r114 的 `license_class()` 与 `LICENSE_CAPS` 与 compat 公式（单源，禁复刻）；
  · body_class 从 `license_body_r262.json` 取（22/22 正文），取不到 ⇒ None ⇒ 退回字段口径（与 use_body 语义一致）；
  · rank0 换面对照在「同池 5 候选」内做：新总合 = score_total - 旧compat + 新compat（其余四维不动）。
"""
import importlib.util, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
spec = importlib.util.spec_from_file_location("r114", os.path.join(ROOT, "05-exec", "r114_replacement_scan.py"))
R = importlib.util.module_from_spec(spec)
sys.modules["r114"] = R
spec.loader.exec_module(R)

MATRIX = os.path.join(ROOT, "06-benchmark", "quarterly_r260", "2026Q4", "replacement_matrix.json")
PACK = os.path.join(ROOT, "06-benchmark", "license_body_r262.json")
OUT = os.path.join(ROOT, "_repro", "r338_lead", "compat_power.json")


def compat_now(cand, body):
    """现尺 compat：三子腿原样 + LICENSE_CAPS 封顶（照 r114 score5 的实现算，不另造）。"""
    sm = cand.get("skill_md_exact_n")
    if sm is None:
        sm = cand.get("skill_md_n")
    base = min(5, (2 if (cand.get("license") or "UNLICENSED") != "UNLICENSED" else 0)
               + (0 if cand.get("archived") else 1) + (2 if sm else 0))
    _lic = R.license_class(cand.get("license"), body)
    return min(base, R.LICENSE_CAPS[_lic]), _lic


def main():
    m = json.load(open(MATRIX, encoding="utf-8"))
    pack = (json.load(open(PACK, encoding="utf-8")).get("repos") or {}) if os.path.isfile(PACK) else {}
    rows = m.get("rows") or []
    dist_new, dist_old = {}, {}
    flips = []
    capped = 0
    exonerated = 0
    body_used = 0
    total_c = 0
    for r in rows:
        cs = r.get("candidates") or []
        scored = []
        for c in cs:
            total_c += 1
            e = pack.get(c.get("repo") or "")
            body = (e.get("license_body_class") or "") if (e and e.get("state") == "OK") else None
            if body:
                body_used += 1
            cn, lic = compat_now(c, body)
            co = (c.get("score5") or {}).get("compat")
            dist_old[co] = dist_old.get(co, 0) + 1
            dist_new[cn] = dist_new.get(cn, 0) + 1
            if cn < (co or 0):
                capped += 1
            if lic == "permissive" and (c.get("license") or "").upper() in ("NOASSERTION", ""):
                exonerated += 1
            scored.append((c, (c.get("score_total") or 0) - (co or 0) + cn))
        if len(scored) > 1:
            old0 = max(scored, key=lambda x: x[0].get("score_total") or 0)[0].get("repo")
            new0 = max(scored, key=lambda x: x[1])[0].get("repo")
            if old0 != new0:
                flips.append({"slug": r.get("slug"), "old_rank0": old0, "new_rank0": new0})
    uniq = len(set(dist_new.values() and dist_new))
    out = {
        "schema": "r338-compat-power-1",
        "generated_at": m.get("generated_at"),
        "face": "937 candidates / 191 slugs (r260 matrix body) rescored with the CURRENT scale",
        "compat_dist_old_stored": dist_old,
        "compat_dist_new_scale": dist_new,
        "candidates_total": total_c,
        "capped_count": capped,
        "body_fingerprint_used": body_used,
        "permissive_body_exonerating_NOASSERTION": exonerated,
        "rank0_flips_n": len(flips),
        "rank0_flips": flips[:40],
    }
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    on5_old = dist_old.get(5, 0) * 100.0 / total_c
    on5_new = dist_new.get(5, 0) * 100.0 / total_c
    print("[R338:COMPAT] cands=%d 恒5占比 old=%.1f%% new=%.1f%% capped=%d body_used=%d exonerated=%d rank0_flips=%d/191"
          % (total_c, on5_old, on5_new, capped, body_used, exonerated, len(flips)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
