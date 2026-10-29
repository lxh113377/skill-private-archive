import json
d = json.load(open('06-benchmark/r281_execution_ab.json', encoding='utf-8'))
req = ['schema','task_text','arms','blind_note','measured_at','provenance_cmd','uplift_pct','uplift_formula','negative_control','rubric_scope_note','unverified_flags','side_effects_disclosure']
print('schema=', d['schema'], '| keys_present=', sum(1 for k in req if k in d), '/', len(req))
K = ['1_artifact_existence','2_content_completeness','3_executability','4_no_fabrication','5_instruction_following','6_cost_tool_calls']
for k in 'AB':
    a = d['arms'][k]
    print(k, 'files=', a['file_count'], 'bytes=', a['bytes'], 'rubric=', [a['rubric'][x] for x in K], 'tried/ok=', a['commands_tried'], a['commands_ok'], 'Q=', a['quality_index_Q'])
print('uplift_pct=', d['uplift_pct'], 'num=', d['uplift_formula']['numerator'], 'den=', d['uplift_formula']['denominator'])
print('negctl identical=', d['negative_control']['byte_identical_to_A'], 'Q_copy=', d['negative_control']['Q_copy'], 'uplift_copy=', d['negative_control']['uplift_pct_copy_vs_A'])
print('measured_at=', d['measured_at'], 'unverified_flags=', d['unverified_flags'])
print('recompute check: (Q_B-Q_A)/Q_A*100 =', round(100*(d['arms']['B']['quality_index_Q']-d['arms']['A']['quality_index_Q'])/d['arms']['A']['quality_index_Q'], 2))
