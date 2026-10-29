import io, json, sys
sys.path.insert(0,'_repro/r282j')
from denoms import lead_caliber, lead_strict_unreferenced, hit_path_or_base, rule_flip
from measures import git_bytes, read_worktree
lead=json.load(io.open('06-benchmark/r278_landing_effect.json',encoding='utf-8'))
for row in lead['rows']:
    s=row['skill']; rel=s+'/SKILL.md'
    bref=row['before_sha_used']; braw,tb=git_bytes(bref,rel); ta=read_worktree(s)
    counted,exempt,pruned = lead_caliber(s)
    for side,t in (('before',tb),('after',ta)):
        pub=row['metrics_'+side]['unreferenced_strict_n']
        mine=len(lead_strict_unreferenced(t,counted))
        print('%-24s %-7s present=%3d pub_strict_unref=%3d mine=%3d match=%s' % (s,side,len(counted),pub,mine,pub==mine))
    fl=rule_flip(ta,counted)
    print('   flip between rules (after text): %d  %s' % (fl['flipped_n'], fl['only_unreferenced_under_f_rule'][:4]))
