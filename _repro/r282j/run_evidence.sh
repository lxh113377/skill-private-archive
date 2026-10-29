set -u
cd "C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化" || exit 1
export PYTHONPYCACHEPREFIX=/tmp/py_r282j
PY="C:/Users/37533/.workbuddy/binaries/python/envs/default/Scripts/python.exe"
echo "=== 1 test-driven-development"
echo "$PY -B _repro/r282j/emit_r282.py --check | grep -aF '[FLAT]'"
"$PY" -B _repro/r282j/emit_r282.py --check | grep -aF '[FLAT]'
echo "rc=$?"
echo "=== 2 test-driven-development"
echo "$PY -B _repro/r282j/emit_r282.py --check | grep -aF '[D]'"
"$PY" -B _repro/r282j/emit_r282.py --check | grep -aF '[D]'
echo "rc=$?"
echo "=== 3 test-driven-development"
echo "$PY -B _repro/r282j/emit_r282.py --check | grep -aF '[IDENT]'"
"$PY" -B _repro/r282j/emit_r282.py --check | grep -aF '[IDENT]'
echo "rc=$?"
echo "=== 4 test-driven-development/TDD-1"
echo "$PY -B _repro/r282j/emit_r282.py --check | grep -aF '[FLAT]'"
"$PY" -B _repro/r282j/emit_r282.py --check | grep -aF '[FLAT]'
echo "rc=$?"
echo "=== 5 test-driven-development/TDD-2"
echo "$PY -B _repro/r282j/emit_r282.py --check | grep -aF '[D]'"
"$PY" -B _repro/r282j/emit_r282.py --check | grep -aF '[D]'
echo "rc=$?"
echo "=== 6 test-driven-development/TDD-3"
echo "$PY -B _repro/r282j/emit_r282.py --check | grep -aF '[IDENT]'"
"$PY" -B _repro/r282j/emit_r282.py --check | grep -aF '[IDENT]'
echo "rc=$?"
echo "=== 7 frontend-slides"
echo "$PY -B _repro/r282j/emit_r282.py --check | grep -aF '[D]'"
"$PY" -B _repro/r282j/emit_r282.py --check | grep -aF '[D]'
echo "rc=$?"
echo "=== 8 frontend-slides"
echo "$PY -B _repro/r282j/emit_r282.py --check | grep -aF '[D]'"
"$PY" -B _repro/r282j/emit_r282.py --check | grep -aF '[D]'
echo "rc=$?"
echo "=== 9 frontend-slides"
echo "$PY -B _repro/r282j/emit_r282.py --check | grep -aF '[RECOMPUTE]'"
"$PY" -B _repro/r282j/emit_r282.py --check | grep -aF '[RECOMPUTE]'
echo "rc=$?"
echo "=== 10 frontend-slides"
echo "$PY -B _repro/r282j/emit_r282.py --check | grep -aF '[IDENT]'"
"$PY" -B _repro/r282j/emit_r282.py --check | grep -aF '[IDENT]'
echo "rc=$?"
echo "=== 11 frontend-slides/FS-1"
echo "$PY -B _repro/r282j/emit_r282.py --check | grep -aF '[D]'"
"$PY" -B _repro/r282j/emit_r282.py --check | grep -aF '[D]'
echo "rc=$?"
echo "=== 12 frontend-slides/FS-2"
echo "$PY -B _repro/r282j/emit_r282.py --check | grep -aF '[D]'"
"$PY" -B _repro/r282j/emit_r282.py --check | grep -aF '[D]'
echo "rc=$?"
echo "=== 13 frontend-slides/FS-3"
echo "$PY -B _repro/r282j/emit_r282.py --check | grep -aF '[RECOMPUTE]'"
"$PY" -B _repro/r282j/emit_r282.py --check | grep -aF '[RECOMPUTE]'
echo "rc=$?"
echo "=== 14 frontend-slides/FS-4"
echo "$PY -B _repro/r282j/emit_r282.py --check | grep -aF '[IDENT]'"
"$PY" -B _repro/r282j/emit_r282.py --check | grep -aF '[IDENT]'
echo "rc=$?"
echo "=== 15 ui-ux-pro-max"
echo "$PY -B _repro/r282j/emit_r282.py --check | grep -aF '[A2]'"
"$PY" -B _repro/r282j/emit_r282.py --check | grep -aF '[A2]'
echo "rc=$?"
echo "=== 16 ui-ux-pro-max"
echo "$PY -B -c import json,io;d=json.load(io.open('06-benchmark/r278_before_after_control.json',encoding='utf-8'));print(sorted(d['items']))   # run from 自建skill优化/"
"$PY" -B -c "import json,io;d=json.load(io.open('06-benchmark/r278_before_after_control.json',encoding='utf-8'));print(sorted(d['items']))"   # run from 自建skill优化/
echo "rc=$?"
echo "=== 17 ui-ux-pro-max"
echo "$PY -B _repro/r282j/emit_r282.py --check | grep -aF '[FLAT]'"
"$PY" -B _repro/r282j/emit_r282.py --check | grep -aF '[FLAT]'
echo "rc=$?"
echo "=== 18 ui-ux-pro-max"
echo "$PY -B _repro/r282j/emit_r282.py --check | grep -aF '[A2]'"
"$PY" -B _repro/r282j/emit_r282.py --check | grep -aF '[A2]'
echo "rc=$?"
echo "=== 19 ui-ux-pro-max"
echo "$PY -B _repro/r282j/emit_r282.py --check | grep -aF '[C]'"
"$PY" -B _repro/r282j/emit_r282.py --check | grep -aF '[C]'
echo "rc=$?"
echo "=== 20 ui-ux-pro-max"
echo "$PY -B _repro/r282j/emit_r282.py --check | grep -aF '[D]'"
"$PY" -B _repro/r282j/emit_r282.py --check | grep -aF '[D]'
echo "rc=$?"
echo "=== 21 ui-ux-pro-max/UX-1"
echo "$PY -B _repro/r282j/emit_r282.py --check | grep -aF '[A2]'"
"$PY" -B _repro/r282j/emit_r282.py --check | grep -aF '[A2]'
echo "rc=$?"
echo "=== 22 ui-ux-pro-max/UX-2"
echo "$PY -B -c import json,io;d=json.load(io.open('06-benchmark/r278_before_after_control.json',encoding='utf-8'));print(sorted(d['items']))   # run from 自建skill优化/"
"$PY" -B -c "import json,io;d=json.load(io.open('06-benchmark/r278_before_after_control.json',encoding='utf-8'));print(sorted(d['items']))"   # run from 自建skill优化/
echo "rc=$?"
echo "=== 23 ui-ux-pro-max/UX-3"
echo "$PY -B _repro/r282j/emit_r282.py --check | grep -aF '[FLAT]'"
"$PY" -B _repro/r282j/emit_r282.py --check | grep -aF '[FLAT]'
echo "rc=$?"
echo "=== 24 ui-ux-pro-max/UX-4"
echo "$PY -B _repro/r282j/emit_r282.py --check | grep -aF '[A2]'"
"$PY" -B _repro/r282j/emit_r282.py --check | grep -aF '[A2]'
echo "rc=$?"
echo "=== 25 ui-ux-pro-max/UX-5"
echo "$PY -B _repro/r282j/emit_r282.py --check | grep -aF '[C]'"
"$PY" -B _repro/r282j/emit_r282.py --check | grep -aF '[C]'
echo "rc=$?"
echo "=== 26 ui-ux-pro-max/UX-6"
echo "$PY -B _repro/r282j/emit_r282.py --check | grep -aF '[D]'"
"$PY" -B _repro/r282j/emit_r282.py --check | grep -aF '[D]'
echo "rc=$?"
