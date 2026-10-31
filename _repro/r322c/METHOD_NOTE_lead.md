# r322c 方法注（Lead 预研，供臂与判据共用；命中判定 = (pattern, target) 对 (query, expected) 二元组）

- 规则表现值：`_DIRECT_MAP_FALLBACK` = **273** 条（Python tuple (regex_pattern, target_slug)，'NONE' 目标也是规则 ⇒ 命中 NONE 同样算 hit_direct_map，必须剔除）。
- 命中测试 = `re.search(pattern, query)`；matched target 是 `expected_skill` 之外的 slug 或 NONE ⇒ 仍算命中（防泄漏）；expected 与 target 相同才算 clean。
- 现有题面去重来源：layered_testset.json（291）/ frozen_blind_test*.json / blindset_query_pool.json（20）—— 以 query 归一化（去空白/标点/全半角）前 60 字为 dedup_key。
- 供给面：GM memory 2637 卷 + lessons 690 + 本仓 06-benchmark 218 md ⇒ 原料充足，卡点只在一手摘录的成本。
