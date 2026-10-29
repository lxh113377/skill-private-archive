#!/usr/bin/env bash
# r273_interpreter_probe.sh — 解释器健康探针（R272-2）
# 为什么用 bash 写：被探的对象是 Python 本身；若用 Python 写探针，Python 一坏探针也哑。
# 输出：JSONL 一行一条读数（ts/解释器/rc/版本），落在 _temp/interpreter_probe.jsonl。
# 退出码：0 = 至少一个解释器可用；2 = 全部不可用（此时应立刻上报）。
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(dirname "$HERE")"
OUT="$ROOT/_temp/interpreter_probe.jsonl"
mkdir -p "$ROOT/_temp"
TS="$(date '+%Y-%m-%dT%H:%M:%S%z')"
declare -a CAND=(
  "/c/Users/37533/.workbuddy/binaries/python/envs/default/Scripts/python.exe"
  "/d/workbuddy/resources/vendor/python/python.exe"
  "/d/LibreOffice/program/python"
  "/c/Windows/py"
)
ok=0
for p in "${CAND[@]}"; do
  if [ ! -x "$p" ] && [ ! -f "$p" ]; then
    printf '{"ts":"%s","exe":"%s","rc":null,"state":"ABSENT"}\n' "$TS" "$p" >> "$OUT"
    continue
  fi
  ver="$("$p" -c 'import encodings,sys;print(sys.version.split()[0])' 2>/dev/null)"
  rc=$?
  if [ $rc -eq 0 ] && [ -n "$ver" ]; then
    ok=$((ok+1))
    printf '{"ts":"%s","exe":"%s","rc":0,"state":"OK","version":"%s"}\n' "$TS" "$p" "$ver" >> "$OUT"
  else
    printf '{"ts":"%s","exe":"%s","rc":%s,"state":"BROKEN"}\n' "$TS" "$p" "$rc" >> "$OUT"
  fi
done
tail -n 4 "$OUT"
echo "[PROBE] ok=$ok/$(( ${#CAND[@]} )) ts=$TS"
[ $ok -gt 0 ] && exit 0 || exit 2
