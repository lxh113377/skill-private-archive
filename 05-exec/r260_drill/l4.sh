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
R259=$(git rev-list -n1 r259)
HB=$(git rev-parse HEAD)
echo L4_R259=$R259
echo L4_HEAD_BEFORE=$HB
echo L4_DESCRIBE_BEFORE=$(git describe --tags 2>/dev/null || echo UNRESOLVED)
F1=06-benchmark/roster_audit_latest.json
F2=memory/01-goal.md
F3=05-exec/r237_roster_audit.py
printf 'DRILL-CORRUPT-L4-A\n' > $F1
printf 'DRILL-CORRUPT-L4-B\n' > $F2
printf 'DRILL-CORRUPT-L4-C\n' > $F3
rm -f 06-benchmark/gate_reconcile_registry.json
DIRTY=$(git status --porcelain | wc -l)
DAMSHA=$(cat $F1 $F2 $F3 | sha256sum | cut -d' ' -f1)
echo L4_DIRTY_AFTER_POLLUTE=$DIRTY
echo L4_POLLUTED_SHA=$DAMSHA
git checkout r259 -- .
RC_A=$?
CMPA=$(git diff --name-only r259 -- . | wc -l)
STGA=$(git status --porcelain | grep -v '^??' | wc -l)
NEW.sha=$(cat $F1 $F2 $F3 2>/dev/null | sha256sum | cut -d' ' -f1)
echo L4A_RC=$RC_A
echo L4A_DIFF_TO_R259=$CMPA
echo L4A_TRACKED_DIRTY=$STGA
echo L4A_RESTORED_SHA=$(cat $F1 $F2 $F3 | sha256sum | cut -d' ' -f1)
echo L4A_EXIST_GATE_REG=$([ -f 06-benchmark/gate_reconcile_registry.json ] && echo 1 || echo 0)
echo L4_DESCRIBE_AFTER=$(git describe --tags 2>/dev/null || echo UNRESOLVED)
TIDX=$(git ls-files -s | git hash-object --stdin)
TREF=$(git ls-tree -r r259 | git hash-object --stdin)
echo L4A_INDEX_TREE=$TIDX
echo L4B_FULLTREE_MATCH_1=$([ "$TIDX" = "$TREF" ] && echo 1 || echo 0)
git reset --hard r259 > /tmp/r260_l4b.out 2>&1
RC_B=$?
echo L4B_RC=$RC_B
echo L4B_HEAD=$(git rev-parse HEAD)
echo L4B_HEAD_IS_R259=$([ "$(git rev-parse HEAD)" = "$R259" ] && echo 1 || echo 0)
echo L4B_DIRTY=$(git status --porcelain | grep -v '^??' | wc -l)
TIDX2=$(git ls-files -s | git hash-object --stdin)
echo L4C_INDEX_TREE_AFTER_RESET=$TIDX2
echo L4C_FULLTREE_MATCH_2=$([ "$TIDX2" = "$TREF" ] && echo 1 || echo 0)
git checkout --detach r259 >/dev/null 2>&1
echo L4_FILES_TOTAL=$(git ls-files | wc -l)
echo '=== L4 NEG: nonexistent tag ==='
git checkout nosuchtag_r260 -- . >/tmp/r260_l4neg.out 2>&1; echo L4NEG_RC=$?
tail -2 /tmp/r260_l4neg.out | tr '\n' '|'
echo
git reset --hard nosuchtag_r260 >/tmp/r260_l4neg2.out 2>&1; echo L4NEG2_RC=$?
tail -2 /tmp/r260_l4neg2.out | tr '\n' '|'
echo
echo L4NEG_HEAD_STILL=$(git rev-parse HEAD)
