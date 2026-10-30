cd /d/global_skills || exit 9
echo '== A: writing-good-tests.md in trees =='  
for r in 87934d48 079b91f3 HEAD; do echo -n "$r: "; git ls-tree -r --name-only $r -- test-driven-development | tr '\n' ' '; echo; done
echo '== B: does the file exist in worktree =='  
ls -l test-driven-development/
echo '== C: bold-template-pack present at 6394cbae tree =='  
git ls-tree -r --name-only 6394cbae -- frontend-slides/bold-template-pack | head -3
echo '== D: pythons =='  
ls -l "$USERPROFILE/.workbuddy/binaries/python/envs/default/Scripts/python.exe" 2>/dev/null || echo NO_MANAGED_VENV
which python python3 2>/dev/null
echo '== E: try --help with managed venv =='  
PV="$USERPROFILE/.workbuddy/binaries/python/envs/default/Scripts/python.exe"
"$PV" -B -c 'import sys;print(sys.version.split()[0])' 2>&1 | head -2
"$PV" -B frontend-slides/scripts/extract-pptx.py --help 2>&1 | head -12
echo '== F: ui-ux scripts count =='  
ls ui-ux-pro-max/scripts/*.py 2>/dev/null | wc -l
"$PV" -B ui-ux-pro-max/scripts/search.py --help 2>&1 | head -12
echo '== G: mirror mtimes =='  
for s in test-driven-development frontend-slides ui-ux-pro-max mcp-builder; do echo -n "$s "; stat -c '%y %s' /c/Users/37533/.agents/skills/$s/SKILL.md 2>/dev/null; done
echo '== H: .agents/skills git remote/junction =='  
git -C /c/Users/37533/.agents/skills log --oneline -3 -- frontend-slides/SKILL.md 2>&1 | head -6