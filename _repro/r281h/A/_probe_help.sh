PY=/c/Users/37533/.workbuddy/binaries/python/envs/default/Scripts/python.exe
echo "=== [1] doc-literal path (skills/ui-ux-pro-max/...) ==="
python3 skills/ui-ux-pro-max/scripts/design_system.py --help 2>&1; echo "RC_DOC_LITERAL=$?"
echo "=== [2] real path --help ==="
"$PY" /d/global_skills/ui-ux-pro-max/scripts/design_system.py --help 2>&1; echo "RC_HELP=$?"
echo "=== [3] search.py --help ==="
"$PY" /d/global_skills/ui-ux-pro-max/scripts/search.py --help 2>&1; echo "RC_SEARCH_HELP=$?"
