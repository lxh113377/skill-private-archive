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
echo CFG_AUTOCRLF=$(git config --get core.autocrlf || echo none)
echo STATUS_CLEAN=[$(git status --porcelain $F)]
HEADBLOB=$(git show HEAD:$F | sha256sum | cut -d' ' -f1)
PREVBLOB=$(git show HEAD~1:$F | sha256sum | cut -d' ' -f1)
WT=$(sha256sum $F | cut -d' ' -f1)
WT_CRLFSIM=$(git show HEAD:$F | sed -e 's/$/\r/' | sha256sum | cut -d' ' -f1)
git checkout -- $F
printf 'DRILL-CORRUPT-L1\n' > $F
DAMAGED=$(sha256sum $F | cut -d' ' -f1)
git show HEAD~1:$F > $F
R=$?
AFTER=$(sha256sum $F | cut -d' ' -f1)
DIFRC=$?
git checkout -- $F
RESTORECLEAN=[$(git status --porcelain $F)]
echo L1_RC=$R
echo L1_HEADBLOB=$HEADBLOB
echo L1_PREVBLOB=$PREVBLOB
echo L1_WT=$WT
echo L1_WT_CRLFSIM=$WT_CRLFSIM
echo L1_DAMAGED=$DAMAGED
echo L1_AFTER=$AFTER
echo L1_RESTORECLEAN=$RESTORECLEAN
