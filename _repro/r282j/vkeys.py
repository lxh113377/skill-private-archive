import io, json, os
o = json.load(io.open('06-benchmark/r282_three_arm_reconcile.json', encoding='utf-8'))
print('TOPKEYS', sorted(o.keys()))
req = ['schema','rows','band_flattening','d6_mapping_check','denominator_explanation','provenance_cmd','measured_at']
print('REQUIRED_PRESENT', all(k in o for k in req), [k for k in req if k not in o])
for r in o['rows']:
    need = ['skill','lead','f_arm','g_arm','divergences','adjudication','adjudication_evidence_cmd']
    print(r['skill'], 'rowkeys_ok', all(k in r for k in need), 'divergences_n', len(r['divergences']), 'leadkeys', sorted(k for k in r['lead'] if k in ('before_ref','after_ref','metrics')), 'f_has_ref' , ('before_ref' in r['f_arm']), 'g_keys', sorted(k for k in r['g_arm'] if k in ('before_ref','after_ref','metrics')))
bf = o['band_flattening']
print('BF keys', sorted(bf.keys()))
print('BF raw/banded', bf['raw_sum_uplift_pct'], bf['banded_uplift_pct'], bf['cases_n'])
print('bytes', os.path.getsize('06-benchmark/r282_three_arm_reconcile.json'))
