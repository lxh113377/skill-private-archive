# -*- coding: utf-8 -*-
import importlib.util, io, json, os, sys
ROOT = r"C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化"
MOD = os.path.join(ROOT, "05-exec", "r114_replacement_scan.py")
UP = os.path.join(ROOT, "_temp", "r290s", "upstream")
spec = importlib.util.spec_from_file_location("r114", MOD)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
print("IMPORT_OK, module attrs present:", hasattr(m, "classify_body"), hasattr(m, "license_class"), hasattr(m, "parse_sidecar"), hasattr(m, "LICENSE_CAPS"))
lic = io.open(os.path.join(UP, "LICENSE"), encoding="utf-8").read()
print("LICENSE_BYTES", len(lic.encode("utf-8")))
spdx, cls, hits = m.classify_body(lic.upper())
print("CLASSIFY_BODY", spdx, cls, hits)
print("LICENSE_CLASS(MIT,None)", m.license_class("MIT"))
print("LICENSE_CLASS(MIT,cls)", m.license_class("MIT", cls))
print("CAP", m.LICENSE_CAPS.get(m.license_class("MIT", cls)))
for name in sorted(os.listdir(UP)):
    t = io.open(os.path.join(UP, name), encoding="utf-8", errors="replace").read()
    print("SCAN", name, len(t.encode("utf-8")), m.classify_body(t.upper()))
side = io.open(r"D:/global_skills/security-audit/.upstream", encoding="utf-8").read()
print("SIDECAR_NOW", m.parse_sidecar(side))
probe = side + "# absorbed_alt: cloudflare/security-audit-skill @ c1c8a8c1471069fb0e188eeaff69b8e8db6564a8\n"
print("SIDECAR_AFTER", m.parse_sidecar(probe))
print("INERT", m.parse_sidecar(side) == m.parse_sidecar(probe))
bad = side + "path: skills/security-audit\n"
print("SIDECAR_WITH_PATH_LINE", m.parse_sidecar(bad))
import inspect
print("SIG classify_body", str(inspect.signature(m.classify_body)))
print("SIG license_class", str(inspect.signature(m.license_class)))
print("SIG parse_sidecar", str(inspect.signature(m.parse_sidecar)))
