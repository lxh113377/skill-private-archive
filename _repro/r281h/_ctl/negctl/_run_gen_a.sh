PY=/c/Users/37533/.workbuddy/binaries/python/envs/default/Scripts/python.exe
SCRIPTS=/d/global_skills/ui-ux-pro-max/scripts
Q="internal data analytics dashboard admin tables charts metrics filters"
-p
PROJECT="internal-data-dashboard"
echo "=== ATTEMPT A: no PYTHONIOENCODING ==="
"$PY" "$SCRIPTS/search.py" "$Q" --design-system --persist -p "$PROJECT" --page "dashboard" 2>_gen_a.err; echo "RC_A=$?"
echo "--- stderr A (head 20) ---"; head -20 _gen_a.err
