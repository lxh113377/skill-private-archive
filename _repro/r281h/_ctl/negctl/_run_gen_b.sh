PY=/c/Users/37533/.workbuddy/binaries/python/envs/default/Scripts/python.exe
SCRIPTS=/d/global_skills/ui-ux-pro-max/scripts
echo "=== state after attempt A ==="
find design-system -type f 2>/dev/null | sort; echo "RC_FIND=$?"
echo "=== ATTEMPT B: persist without --page ==="
"$PY" "$SCRIPTS/search.py" "internal data analytics dashboard admin tables charts metrics filters" --design-system --persist -p "internal-data-dashboard" -f markdown 2>_gen_b.err; echo "RC_B=$?"
echo "--- stderr B bytes: $(wc -c < _gen_b.err) ---"
cat _gen_b.err
