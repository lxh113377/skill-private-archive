PY=/c/Users/37533/.workbuddy/binaries/python/envs/default/Scripts/python.exe
Q="internal data analytics dashboard admin tables charts metrics filters"
P="internal-data-dashboard"
echo "=== ATTEMPT E: wrapper with Windows path ==="
"$PY" _ds_page_wrapper.py "$Q" --persist -p "$P" --page dashboard -o . -f markdown 2>_gen_e.err; echo "RC_E=$?"
echo "--- stderr E ---"; head -20 _gen_e.err
echo "=== files now ==="
find design-system -type f | sort
echo "=== page file head ==="
head -40 design-system/internal-data-dashboard/pages/dashboard.md 2>/dev/null
