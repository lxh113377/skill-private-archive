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
echo V_HEAD=$(git rev-parse HEAD)
echo V_HEAD_IS_R259=$([ "$(git rev-parse HEAD)" = "$R259" ] && echo 1 || echo 0)
echo V_DESCRIBE=$(git describe --tags)
echo V_DIFF_EXIT_CODE=[$(git diff --exit-code r259 >/dev/null 2>&1; echo $?)
git diff --quiet r259; echo V_DIFF_QUIET_RC=$?
git diff --cached --quiet r259; echo V_DIFF_CACHED_QUIET_RC=$?
IT=$(git write-tree 2>/dev/null)
RT=$(git rev-parse r259^{tree})
echo V_INDEX_TREE=$IT
echo V_R259_TREE=$RT
echo V_FULLTREE_MATCH=$([ "$IT" = "$RT" ] && echo 1 || echo 0)
echo V_FILES=$(git ls-files | wc -l)
echo V_DIRTY_TRACKED=$(git status --porcelain | grep -vc '^??')
echo V_REVERT_OBJ_ALIVE=$([ "$(git cat-file -t e8e092651a04d2801a6bddd2594444deb92e2bd7 2>/dev/null)" = commit ] && echo 1 || echo 0)
git reflog --format=%h | head -6 | tr '\n' '|'
echo
echo '=== NEG L1: git show HEAD~1:<nonexistent> ==='
git show HEAD~1:no/such/file_r260.txt > /tmp/r260_neg_l1.out 2>&1; echo NEGL1_RC=$?
head -1 /tmp/r260_neg_l1.out
echo '=== NEG L3: cp from nonexistent archive copy ==='
cp -p archive/trash-proof-2026-10-23/no_such_copy.bak memory/01-goal.md > /tmp/r260_neg_l3.out 2>&1; echo NEGL3_RC=$?
head -1 /tmp/r260_neg_l3.out
echo NEGL3_GOAL_INTACT=$(sha256sum memory/01-goal.md | cut -c1-12)
git status --porcelain memory/01-goal.md | wc -l
echo '=== NEG L3b: sha 判据自证 —— 还原后故意拿错目标比 ==='
cmp -s archive/trash-proof-2026-10-23/07-next-steps.md.r120_103101.bak memory/07-next-steps.md; echo NEGL3B_CMP=$?
echo '=== 主仓只读复核（不写） ==='
cd "$D/../.." || exit 91  # = 项目根 自建skill优化
echo MAIN_HEAD=$(git rev-parse HEAD)
echo MAIN_DESCRIBE=$(git describe --tags)
echo MAIN_DIRTY_TRACKED=$(git status --porcelain | grep -vc '^??')
git rev-parse HEAD:r260nonexistent.txt >/dev/null 2>&1; echo MAIN_NO_NEW_COMMITS_RC=$?
echo '=== 演练脚本内不含 global_skills 写操作 ==='
# r260 修（自我指涉）：旧式 `grep -c global_skills *.sh` 把「这一行自身」与只读的 ls/find 检查
# 全算成命中（读数 2/5 却不等于「有写操作」，是假红方向）。只匹配真实写形态：重定向进受管根、
# cp/mv/rm 到受管根、在受管根跑 git 写子命令。
grep -nE '(>|>>)[[:space:]]*/d/global_skills|(cp|mv|rm)[^|]*[[:space:]]/d/global_skills|git -C[^\n]*global_skills[^
]*(commit|checkout|reset|add)' *.sh 2>/dev/null | wc -l
echo
