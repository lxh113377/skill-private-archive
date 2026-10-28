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
B=$(git rev-parse HEAD)
git revert --no-edit 0000000000000000000000000000000000000000 > /tmp/r260_neg.out 2>&1; echo NEG1_RC=$?
tail -2 /tmp/r260_neg.out | tr '\n' '|'
echo
git revert --no-edit deadbeefcafebabe1234567890abcdef12345678 > /tmp/r260_neg2.out 2>&1; echo NEG2_RC=$?
tail -2 /tmp/r260_neg2.out | tr '\n' '|'
echo
A=$(git rev-parse HEAD)
echo NEG_HEAD_UNCHANGED=$([ "$B" = "$A" ] && echo 1 || echo 0)
test -e .git/REVERT_HEAD && echo NEG_REVERT_HEAD_LEAK=1 || echo NEG_REVERT_HEAD_LEAK=0
echo NEG_HEAD=$A
