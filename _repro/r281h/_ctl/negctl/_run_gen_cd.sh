PY=/c/Users/37533/.workbuddy/binaries/python/envs/default/Scripts/python.exe
S=/d/global_skills/ui-ux-pro-max/scripts
Q="internal data analytics dashboard admin tables charts metrics filters"
P="internal-data-dashboard"
echo "=== ATTEMPT C: page override via package wrapper ==="
"$PY" _ds_page_wrapper.py "$Q" --design-system --persist -p "$P" --page dashboard -f markdown 2>_gen_c.err; echo "RC_C=$?"
cat _gen_c.err | head -25
echo "=== files now ==="
find design-system -type f | sort
echo "=== ATTEMPT D: raw search.py --page (expect known upstream failure) ==="
"$PY" "$S/search.py" "$Q" --design-system --persist -p "$P" --page dashboard 2>_gen_d.err; echo "RC_D=$?"
tail -3 _gen_d.err
