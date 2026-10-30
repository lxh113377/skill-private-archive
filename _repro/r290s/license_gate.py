# -*- coding: utf-8 -*-
"""license_gate.py — R290 security-audit 换装许可门（只读判定；不联网、不改受管根）。

单源纪律（R260-5「读实现优先于写探针」）：许可档位只由 05-exec/r114_replacement_scan.py 的
classify_body / license_class / LICENSE_CAPS 产生，本件**不重复实现**任何指纹表或名单 ——
重复实现 = 两处口径可能给出不同档位而无人发现（r262 一手踩过）。

签名现读（inspect 实测，非猜）：
    classify_body(text_upper)            -> (spdx 或 None, 档位, 受限措辞命中 list)
    license_class(lic, body_class=None)  -> 档位（有正文证据时正文优先于 API 字段）
    LICENSE_CAPS = {copyleft:1, weak-copyleft:2, restricted:1, unknown:4, permissive:5, none:5}

入参形态：classify_body 内部只做空白折叠、不再 .upper()，故调用方必须传**已大写**正文。
判据：api_spdx=MIT 且正文判出 MIT/permissive 且 cap=5 且受限措辞命中 0 ⇒ 允许并入。
退出码：0 允许并入 / 1 禁并入 / 2 取证失败（单源件或 LICENSE 正文不可读 ⇒ 禁读成「无限制」，R247）。
"""
import hashlib
import importlib.util
import io
import json
import os
import sys

ROOT = "C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化"
MOD = os.path.join(ROOT, "05-exec", "r114_replacement_scan.py")
UP = os.path.join(ROOT, "_temp", "r290s", "upstream")
OUT = os.path.join(ROOT, "_temp", "r290s", "license_scan.json")
# API 字段取值命令（实测输出见 coords.json）：
#   gh api repos/cloudflare/security-audit-skill --jq "{spdx:(.license.spdx_id // "NONE")}"
API_SPDX = "MIT"


def sha256(path):
    """整文件 sha256（逐字节等值证据；不是摘要前缀）。"""
    return hashlib.sha256(io.open(path, "rb").read()).hexdigest()


def load_module():
    """按文件路径加载单源模块取判定函数。

    import 只触发顶层常量与函数定义：该件 main() 在 __main__ 守卫内（实测 :231-232 同款结构），
    故不联网、不写盘、不读受管根以外的东西。
    """
    spec = importlib.util.spec_from_file_location("r114_single_source", MOD)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    if not os.path.exists(MOD):
        print("[LICENSE] UNVERIFIED: 单源判据不可读 %s" % MOD)
        return 2
    lic_path = os.path.join(UP, "LICENSE")
    if not os.path.exists(lic_path):
        print("[LICENSE] UNVERIFIED: 上游 LICENSE 正文不可读（禁据此判「无限制」）")
        return 2
    m = load_module()
    lic = io.open(lic_path, encoding="utf-8").read()
    spdx, body_class, hits = m.classify_body(lic.upper())
    final = m.license_class(API_SPDX, body_class)
    cap = m.LICENSE_CAPS.get(final)
    print("[LICENSE] api_spdx=%s body_spdx=%s body_class=%s final_class=%s cap=%s restricted_hits=%d"
          % (API_SPDX, spdx, body_class, final, cap, len(hits)))
    print("[LICENSE] hits=%s bytes=%d sha256=%s"
          % (json.dumps(hits), len(lic.encode("utf-8")), sha256(lic_path)))
    # 逐个拟并入正文再扫一遍：防「LICENSE 宽松但正文自带 NC/商业条件」（dify / Imbad0202 同族）
    risky = []
    rows = []
    for name in sorted(os.listdir(UP)):
        p = os.path.join(UP, name)
        if not os.path.isfile(p):
            continue
        t = io.open(p, encoding="utf-8", errors="replace").read()
        s2, c2, h2 = m.classify_body(t.upper())
        rows.append({"file": name, "bytes": len(t.encode("utf-8")), "sha256": sha256(p),
                     "spdx": s2, "class": c2, "hits": h2})
        # unknown 在这里=「正文里没有许可指纹」（散文/代码本就不该有），不是受限证据；
        # 真正禁并入的档位是 restricted/copyleft/weak-copyleft/none 或命中受限措辞。
        if c2 in ("restricted", "copyleft", "weak-copyleft", "none") or h2:
            risky.append(name)
    for r in rows:
        print("[SCAN] %s bytes=%d class=%s spdx=%s hits=%s"
              % (r["file"], r["bytes"], r["class"], r["spdx"], json.dumps(r["hits"])))
    io.open(OUT, "w", encoding="utf-8", newline="").write(json.dumps(
        {"single_source": "05-exec/r114_replacement_scan.py::classify_body/license_class/LICENSE_CAPS",
         "api_spdx": API_SPDX, "body_spdx": spdx, "body_class": body_class,
         "final_class": final, "cap": cap, "restricted_hits": hits,
         "risky_files": risky, "rows": rows}, ensure_ascii=False, indent=1, sort_keys=True))
    ok = (spdx == "MIT" and final == "permissive" and cap == 5 and not hits and not risky)
    print("[LICENSE-PREP] spdx=%s class=%s cap=%s restricted=0 gate=%s"
          % (spdx, final, cap, "PASS" if ok else "FAIL"))
    return 0 if ok else 1


sys.exit(main())
