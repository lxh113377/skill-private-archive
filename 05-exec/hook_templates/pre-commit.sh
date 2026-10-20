#!/bin/sh
# pre-commit：按「本次提交该过哪道门」分级阻断（R137 落地，承接 r130 的 r130_gate_table_reconcile）。
#
# 为什么改成有阻断（R137 一手）：r136 盘点发现本仓 5 条强制条目
#   （#30 落盘 / #31 处方 / #32 判据面 / #33 结论层 / #34 纪律自用）**全部没有流程强制点**
#   —— 门只跑不阻断，hook 全部 exit 0。而 r130 的 pre-commit 刻意不阻断，理由正当：
#   并行会话也在改同一个仓，无差别阻断 = 把我的判据变成「别人的活干不下去」（R269 反面）。
#
# 解法 = **分级**：只跑「本次变更触发的门」，只阻断这些门的红。
#   ① 判定（05-exec/r137_commit_gate_map.py）按暂存文件算出该过哪些门；
#   ② 逐门跑（run_gates.py --gate <id> --no-ledger，--no-ledger 免污染新鲜度台账）；
#   ③ 本次变更**不在纪律面**（in_scope=0）⇒ 不阻断（不挡并行会话的活）；
#   ④ 逃生阀：SKIP_COMMIT_GATES=1 时只打印不阻断（供「已知红、必须先落盘」的场景）。
#
# r137 自抓：初版把「门表对账闸」也纳入阻断，但 r130 的 pre-commit 已跑它且从不阻断；
#   门表闸在「改了 run_gates.py」时才成为阻断项 —— 由判定面统一裁决，不在 hook 里写死。
#
# ⚠️ 门禁台账不写（--no-ledger）：门禁新鲜度门读的是 run_gates 完整跑的台账，
#   pre-commit 的试跑不该被算作「本机门禁已跑」。

cd "$(git rev-parse --show-toplevel)" || exit 0

PY=""
for c in "$PYTHON" python python3 py; do
  [ -z "$c" ] && continue
  if command -v "$c" >/dev/null 2>&1; then PY="$c"; break; fi
done
if [ -z "$PY" ]; then
  for c in "$HOME/.workbuddy/binaries/python/envs/default/Scripts/python.exe" \
           "$LOCALAPPDATA/fj-actions-runner/_work/_tool/Python/3.12.10/x64/python.exe" \
           "/d/fj-actions-runner/_work/_tool/Python/3.12.10/x64/python.exe"; do
    [ -x "$c" ] && { PY="$c"; break; }
  done
fi
[ -z "$PY" ] && exit 0

mkdir -p _temp
MAPJ=_temp/commit_gate_map.json
MAPOUT=$("$PY" 05-exec/r137_commit_gate_map.py --json "$MAPJ" 2>&1)
MAPRC=$?
printf '%s\n' "$MAPOUT" > _temp/commit_gate_map.log
if [ "$MAPRC" -ne 0 ]; then
  echo "[pre-commit] 取不到本次提交该过哪些门（判据面不可用）—— 按不阻断处理，但读数留痕："
  printf '%s\n' "$MAPOUT" | sed 's/^/[pre-commit]   /'
  exit 0
fi

GATES=$("$PY" -c "import io,json,sys;d=json.loads(io.open('$MAPJ',encoding='utf-8-sig').read());print(' '.join(d.get('required_gate_ids') or []))" 2>/dev/null)
INS=$("$PY" -c "import io,json,sys;d=json.loads(io.open('$MAPJ',encoding='utf-8-sig').read());print(d.get('in_scope_n',0))" 2>/dev/null)

if [ -z "$GATES" ] || [ "$INS" = "0" ]; then
  echo "[pre-commit] 本次提交不在纪律面（in_scope=${INS:-0}）⇒ 不阻断。"
  exit 0
fi

FAILED=""
for g in $GATES; do
  case "$g" in
    debt_aging)
      # 账龄件须重生：改 07 后不重生会让三门假红（AGENTS.md 已知坑）
      OUT=$("$PY" 05-exec/r38_debt_aging.py --json _temp/precommit_debt.json 2>&1); RC=$?
      ;;
    *)
      OUT=$("$PY" 05-exec/run_gates.py --gate "$g" --no-ledger --json _temp/precommit_gate.json 2>&1); RC=$?
      ;;
  esac
  printf '%s\n' "$OUT" > "_temp/precommit_$g.log"
  if [ "$RC" -ne 0 ]; then
    FAILED="$FAILED $g"
    echo "[pre-commit] 门 $g 未过（rc=$RC）："
    printf '%s\n' "$OUT" | tail -3 | sed 's/^/[pre-commit]   /'
  else
    echo "[pre-commit] 门 $g 通过"
  fi
done

if [ -n "$FAILED" ]; then
  if [ "$SKIP_COMMIT_GATES" = "1" ]; then
    echo "[pre-commit] SKIP_COMMIT_GATES=1 ⇒ 不阻断（本次已过门：$FAILED）"
    exit 0
  fi
  echo "[pre-commit] 阻断：本次提交涉及的纪律门未过 ⇒$FAILED"
  echo "[pre-commit] 逃生阀：SKIP_COMMIT_GATES=1 git commit ...（须在提交说明里写明为何先落盘）"
  exit 1
fi
echo "[pre-commit] 纪律门全过：$GATES"
exit 0