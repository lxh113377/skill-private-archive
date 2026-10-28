set -u
D=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)  # r260 自定位修：与调用方 cwd 无关
# r260 提升件前置（可复现性修复）：演练用的 clone 副本属**可再生**产物，且必须落在 gitignore 的 _temp/ 下
# （落进 05-exec/ 会把整个仓库副本变成 untracked 噪声）。解析顺序：
#   ① 若脚本同目录已有 clone（开发期留的）⇒ 就地用；② 否则用仓库根现建到 <root>/_temp/r260_drill/clone。
# 建不出副本 ⇒ 具名 CLONE_FAIL 并 exit 92 —— 禁把「没有副本」读成「演练通过」（R247 同向）。
if [ -d "$D/clone" ]; then
  CLONE="$D/clone"
else
  ROOT=$(CDPATH= cd -- "$D/../.." && pwd)
  CLONE="$ROOT/_temp/r260_drill/clone"
  mkdir -p "$(dirname "$CLONE")"
  git clone --no-hardlinks --no-local "$ROOT" "$CLONE" >/dev/null 2>&1 || { echo CLONE_FAIL=1; exit 92; }
  git -C "$CLONE" checkout -q r259 2>/dev/null || true
fi
cd "$CLONE" || exit 90
git config user.name rollback-drill
git config user.email drill@localhost
F=06-benchmark/free_tool_roster_latest.json
git checkout -- $F
echo PROBE_WT=$(sha256sum $F | cut -d' ' -f1)
echo PROBE_WT_LFONLY=$(tr -d '\r' < $F | sha256sum | cut -d' ' -f1)
echo PROBE_HEADBLOB=$(git show HEAD:$F | sha256sum | cut -d' ' -f1)
echo PROBE_CRLF_BYTES=$(grep -c $'\r' $F || echo 0)
echo '=== L2 attempt A: revert feat bda368a ==='
BEFORE_A=$(git rev-parse HEAD)
git revert --no-edit bda368a > /tmp/r260_l2a.out 2>&1
RC_A=$?
echo L2A_RC=$RC_A
tail -3 /tmp/r260_l2a.out | tr '\n' '|'
echo
if [ $RC_A -ne 0 ]; then git revert --abort 2>/dev/null; echo L2A_ABORTED=1; fi
if [ $RC_A -eq 0 ]; then
  F2=05-exec/r215_free_tool_roster.py
  echo L2A_TGT=$F2
  echo L2A_REVERTED_BLOB=$(git show HEAD:$F2 | sha256sum | cut -d' ' -f1)
  echo L2A_PREVSTATE_BLOB=$(git show bda368a^:$F2 | sha256sum | cut -d' ' -f1)
  echo L2A_UPGRADED_BLOB=$(git show bda368a:$F2 | sha256sum | cut -d' ' -f1)
  echo L2A_NEWHEAD=$(git rev-parse HEAD)
fi
echo '=== L2 attempt B (fallback): revert HEAD 9e33cce ==='
if [ $RC_A -ne 0 ]; then
  # r260 父级复跑抓出的判据缺陷（比自述更红 ⇒ 按 D10.2 先怀疑脚本）：旧写法在 revert **之后**才取
  # `git show HEAD~1:$F` 当「升级前态」——而 revert 后 HEAD~1 恰是被撤销的那笔（= 升级态），
  # 于是 PREVSTATE 与 UPGRADED 被打成同一个值，断言退化成恒等式（无牙）。
  # 正解 = 在 revert 之前先把真前态从 HEAD^ 捕获，撤销结果应与它逐字节相等才是「回滚成功」的定义。
  L2B_PREHEAD=$(git rev-parse HEAD)
  L2B_PREV_REAL=$(git show $L2B_PREHEAD^:$F | sha256sum | cut -d' ' -f1)
  git revert --no-edit HEAD > /tmp/r260_l2b.out 2>&1
  RC_B=$?
  echo L2B_RC=$RC_B
  tail -3 /tmp/r260_l2b.out | tr '\n' '|'
  echo
  if [ $RC_B -eq 0 ]; then
    echo L2B_TGT=$F
    echo L2B_REVERTED_BLOB=$(git show HEAD:$F | sha256sum | cut -d' ' -f1)
    echo L2B_PREVSTATE_BLOB=$L2B_PREV_REAL
    echo L2B_UPGRADED_BLOB=$(git show $L2B_PREHEAD:$F | sha256sum | cut -d' ' -f1)
    # 承重断言：撤销后的 blob 必须 == revert 之前捕获的真前态（1 才算 PASS，0 即回滚未复原）。
    echo L2B_ASSERT_EQ=$([ "$(git show HEAD:$F | sha256sum | cut -d' ' -f1)" = "$L2B_PREV_REAL" ] && echo 1 || echo 0)
    echo L2B_NEWHEAD=$(git rev-parse HEAD)
  else git revert --abort 2>/dev/null; fi
fi
