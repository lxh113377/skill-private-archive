#!/usr/bin/env bash
# r278c_drive.sh -- one-shot evidence driver for the before/after control arm.
# Read-only on the managed root: only git log / show / cat-file / rev-parse / ls-tree / find.
# Everything it writes lands under _repro/r278c/ (its own scratch), nowhere else.
set -u
cd "C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化/_repro/r278c" || exit 1
PY=/c/Users/37533/.workbuddy/binaries/python/envs/default/Scripts/python.exe
export PYTHONPYCACHEPREFIX=/tmp/pycache_r278c
REPO=/d/global_skills
echo "== step1: shas taken from git log by me =="
git -C "$REPO" log --oneline -- frontend-slides/SKILL.md | head -6
echo "--"
git -C "$REPO" log --oneline -- test-driven-development/SKILL.md | head -4
echo "--"
echo "HEAD_SHA=$(git -C "$REPO" rev-parse HEAD)"
echo "TDD_BEFORE_PARENT=$(git -C "$REPO" rev-parse 079b91f3~1)"
echo "FS_BEFORE_PARENT=$(git -C "$REPO" rev-parse 6394cbae~1)"
echo "TDD_HEAD_BLOB=$(git -C "$REPO" rev-parse HEAD:test-driven-development/SKILL.md)"
echo "TDD_R266_BLOB=$(git -C "$REPO" rev-parse 079b91f3:test-driven-development/SKILL.md)"
echo "FS_HEAD_BLOB=$(git -C "$REPO" rev-parse HEAD:frontend-slides/SKILL.md)"
echo "FS_R277_BLOB=$(git -C "$REPO" rev-parse 89efb3e6:frontend-slides/SKILL.md)"
echo "== step2: on-disk sibling listings (reference-rate denominator) =="
find /d/global_skills/test-driven-development -type f | sed "s#^/d/global_skills/##" | sort > sibs_tdd.txt
find /d/global_skills/frontend-slides -type f | sed "s#^/d/global_skills/##" | sort > sibs_fs.txt
echo "sibs_tdd=$(wc -l < sibs_tdd.txt) sibs_fs=$(wc -l < sibs_fs.txt)"
echo "== step3: fail-closed fetch of four states =="
bash r278c_fetch.sh 079b91f3~1 test-driven-development/SKILL.md tdd_before.md; echo "rc_tdd_before=$?"
bash r278c_fetch.sh HEAD test-driven-development/SKILL.md tdd_after.md; echo "rc_tdd_after=$?"
bash r278c_fetch.sh 6394cbae~1 frontend-slides/SKILL.md fs_before.md; echo "rc_fs_before=$?"
bash r278c_fetch.sh HEAD frontend-slides/SKILL.md fs_after.md; echo "rc_fs_after=$?"
echo "== step4: negative control on the fetch step =="
bash r278c_fetch.sh deadbeef1234567 test-driven-development/SKILL.md tdd_neg.md; echo "rc_neg_bogus_sha=$?"
bash r278c_fetch.sh 079b91f3 nosuchdir/NOPE.md tdd_neg2.md; echo "rc_neg_bad_path=$?"
echo "neg_artifact_written=$(test -f tdd_neg.md && echo YES || echo NO)"
echo "== step5: measure four states with own yardstick =="
$PY -B r278c_metrics.py --md tdd_before.md --siblings sibs_tdd.txt --label tdd_before; echo "rc_m1=$?"
$PY -B r278c_metrics.py --md tdd_after.md --siblings sibs_tdd.txt --label tdd_after; echo "rc_m2=$?"
$PY -B r278c_metrics.py --md fs_before.md --siblings sibs_fs.txt --label fs_before; echo "rc_m3=$?"
$PY -B r278c_metrics.py --md fs_after.md --siblings sibs_fs.txt --label fs_after; echo "rc_m4=$?"
echo "== step6: negative control on the measure step =="
$PY -B r278c_metrics.py --md does_not_exist.md --siblings sibs_tdd.txt --label neg_missing; echo "rc_m_neg_missing=$?"
: > empty_probe.md
$PY -B r278c_metrics.py --md empty_probe.md --siblings sibs_tdd.txt --label neg_empty; echo "rc_m_neg_empty=$?"
echo "== step7: rollback evidence =="
for s in 079b91f3~1 079b91f3 6394cbae~1 6394cbae 9aaa9214 294e3ac6 89efb3e6 HEAD; do
  if git -C "$REPO" cat-file -e "$s" 2>/dev/null; then
    echo "CATFILE_OK $s -> $(git -C "$REPO" rev-parse "$s")"
  else
    echo "CATFILE_FAIL $s"
  fi
done
BK=/d/global_memory_archive/_trash/rule_backup
echo "BK_DIR_EXISTS=$(test -d "$BK" && echo yes || echo no)"
ls -1 "$BK" | grep -E "test-driven-development" | sed "s#^#BK_TDD #"
ls -1 "$BK" | grep -E "frontend-slides" | sed "s#^#BK_FS #"
echo "== done =="
