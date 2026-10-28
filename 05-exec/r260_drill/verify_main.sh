set -u
cd "$D/../.." || exit 91  # = 项目根 自建skill优化
echo MAIN_HEAD=$(git rev-parse HEAD)
echo MAIN_DESCRIBE=$(git describe --tags)
echo MAIN_DIRTY_TRACKED=$(git status --porcelain | grep -vc "^??")
echo MAIN_ROSTER_SHA=$(sha256sum 06-benchmark/free_tool_roster_latest.json | cut -d" " -f1)
echo MAIN_07NEXT_SHA=$(sha256sum memory/07-next-steps.md | cut -d" " -f1)
echo MAIN_GOAL_SHA=$(sha256sum memory/01-goal.md | cut -d" " -f1)
echo MAIN_RUN_GATES_MTIME=$(stat -c %y 05-exec/run_gates.py | cut -d. -f1)
git diff --quiet HEAD -- 05-exec/run_gates.py; echo MAIN_RUN_GATES_UNCHANGED_RC=$?
echo '=== 演练脚本是否含 global_skills 写操作 ==='
grep -c global_skills _temp/rollback_drill/*.sh 2>/dev/null | tr "\n" "|"
echo
echo '=== 副本内 git 写痕迹（证明写只发生在副本） ==='
git -C _temp/r260_drill/clone reflog --format=%gd:%gs 2>/dev/null | head -8 | tr "\n" "|"
echo
echo '=== D:\global_skills 未被本任务触碰（只读列举，不写） ==='
ls -d /d/global_skills >/dev/null 2>&1 && echo GS_EXISTS=1 || echo GS_EXISTS=0
find /d/global_skills -maxdepth 1 -newer 06-benchmark/r260_rollback_drill.json -type f 2>/dev/null | wc -l
