【数据流假设】
本次标识: 轮103
来源: 06-benchmark/twelve_face_r103_2026-10-03.json（本会话 01:09 联网实跑产物）；独立通道对账 = curl `repos/mukul975/Anthropic-Cybersecurity-Skills` 得 default_branch=main、trees/main?recursive=1 返回 7286 blob / 818 个 SKILL.md / truncated=false，与产物记录的 d1=0、skill_bearing=false 直接冲突
流向: 05-exec/r96_twelve_face.py 的 gh_get()→fetch_remote() 写 raw["repos"][slug] → score_dims() 按 skill_bearing 决定 d1/d8/d9/d12 是否取该仓为分母 → 06-benchmark 证据件 → r103 报告总览表与换装判定；改后「tree 未取到」面转入 UNAVAILABLE 并从技能分母剔除，剔除数必须显名落盘
结构: rec 增 tree_state(ok|failed) 与 tree_error（rc + stderr 摘要）；skill_bearing 由二值 bool 改三态 True/False/None；face_role 增 unknown；夹具 --selftest 由 45 腿增至 47 腿（两条新反例腿：tree 失败必须 UNAVAILABLE、UNAVAILABLE 必须带 reason）；schema 串 bump 至 twelve-face-r103-v6
异常: tree 取不到 → 记 reason 且不得记 0；reason 取不到仍判 UNAVAILABLE（禁静默当洁净）；gh 退出码非 0 → stderr 截 200B 入 tree_error；本地面取不到 → 整件 rc=2 不产出结论；补丁锚点命中数 != 1 → 立即停手不改判据
