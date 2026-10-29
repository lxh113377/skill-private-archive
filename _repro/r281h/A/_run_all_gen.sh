PY=/c/Users/37533/.workbuddy/binaries/python/envs/default/Scripts/python.exe
S=/d/global_skills/ui-ux-pro-max/scripts
Q="internal data analytics dashboard admin tables charts metrics filters"
P="internal-data-dashboard"
echo "########## A) generator verbatim: search.py --design-system --persist (no --page) ##########"
"$PY" "$S/search.py" "$Q" --design-system --persist -p "$P" -o . -f markdown; echo "RC=$?"
echo ""
echo "########## B) generator verbatim: wrapper with --page dashboard ##########"
"$PY" _ds_page_wrapper.py "$Q" --persist -p "$P" --page dashboard -o . -f markdown; echo "RC=$?"
echo ""
for D in style ux chart color typography web; do
  echo "########## C) search --domain $D ##########"
  "$PY" "$S/search.py" "dashboard data table filter loading empty focus" --domain "$D" -n 3; echo "RC=$?"
done
