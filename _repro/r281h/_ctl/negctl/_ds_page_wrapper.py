"""Arm-A harness wrapper for the read-only bundled generator scripts.
Why this exists: upstream design_system.py:925 does `from .core import search`; when
search.py is launched as a top-level script that relative import raises ImportError
(measured rc=1 in _exec_log.md ATTEMPT A / ATTEMPT D), so `--page` overrides never get
written. Fix without touching D:/global_skills (contract: read-only): register the scripts
directory as an importable package in sys.modules, set design_system.__package__ so the
relative import resolves to scripts.core, then call generate_design_system directly.
Paths must be Windows form - the MSYS form (/d/...) is invisible to this Windows CPython.
"""
import sys
import types
import argparse
S = "D:/global_skills/ui-ux-pro-max/scripts"
sys.path.insert(0, S)
import core
import design_system
pkg = types.ModuleType("scripts")
pkg.__path__ = [S]
sys.modules["scripts"] = pkg
sys.modules["scripts.core"] = core
sys.modules["scripts.design_system"] = design_system
design_system.__package__ = "scripts"
from design_system import generate_design_system
ns = argparse.ArgumentParser()
ns.add_argument("query")
ns.add_argument("-p", "--project-name", default=None)
ns.add_argument("-f", "--format", default="markdown")
ns.add_argument("--persist", action="store_true")
ns.add_argument("--page", default=None)
ns.add_argument("-o", "--output-dir", default=None)
a = ns.parse_args()
print(generate_design_system(a.query, a.project_name, a.format, persist=a.persist, page=a.page, output_dir=a.output_dir))
