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
F=06-benchmark/free_tool_roster_latest.json
git checkout -- $F
CLEAN=[$(git status --porcelain $F)]
WT=$(sha256sum $F | cut -d' ' -f1)
WTN=$(tr -d '\r' < $F | sha256sum | cut -d' ' -f1)
HB=$(git show HEAD:$F | sha256sum | cut -d' ' -f1)
PB=$(git show HEAD~1:$F | sha256sum | cut -d' ' -f1)
printf 'DRILL-CORRUPT-L1\n' > $F
DAM=$(sha256sum $F | cut -d' ' -f1)
git show HEAD~1:$F > $F
R=$?
AF=$(sha256sum $F | cut -d' ' -f1)
cmp -s <(git show HEAD~1:$F) $F; CMP=$?
git checkout -- $F
POST=[$(git status --porcelain $F)]
echo L1B_CLEAN=$CLEAN
echo L1B_WT=$WT
echo L1B_WTN=$WTN
echo L1B_HB=$HB
echo L1B_PB=$PB
echo L1B_DAM=$DAM
echo L1B_AF=$AF
echo L1B_RC=$R
echo L1B_CMP=$CMP
echo L1B_POST=$POST
