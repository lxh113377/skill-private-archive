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
ls archive/trash-proof-2026-10-23/ | grep -n '07-next-steps.md.r120_100728' | head -2
git ls-files archive/trash-proof-2026-10-23 | wc -l
T=memory/07-next-steps.md
B=archive/trash-proof-2026-10-23/07-next-steps.md.r120_100728.bak
test -f $B || { echo L3_NO_SOURCE=1; exit 92; }
git checkout -- $T 2>/dev/null || true
BEFORE=$(sha256sum $T | cut -d' ' -f1)
BSRC=$(sha256sum $B | cut -d' ' -f1)
printf 'DRILL-CORRUPT-L3\n' > $T
DAM=$(sha256sum $T | cut -d' ' -f1)
cp -p $B $T
R=$?
AFTER=$(sha256sum $T | cut -d' ' -f1)
cmp -s $B $T; CMP=$?
HB=$(git rev-parse HEAD:$T)
BOB=$(git hash-object --no-filters $T)
FOUND=none
for c in $(git rev-list --max-count=60 --all -- $T); do if [ "$(git rev-parse $c:$T 2>/dev/null)" = "$BOB" ]; then FOUND=$c; break; fi; done
git checkout HEAD -- $T
POST=[$(git status --porcelain $T)]
echo L3_TGT=$T
echo L3_SRC=$B
echo L3_RC=$R
echo L3_BEFORE=$BEFORE
echo L3_SRC_SHA=$BSRC
echo L3_DAMAGED=$DAM
echo L3_AFTER=$AFTER
echo L3_CMP=$CMP
echo L3_HEADBLOB=$HB
echo L3_RESTORED_BLOB=$BOB
echo L3_MATCHED_COMMIT=$FOUND
echo L3_POST=$POST
