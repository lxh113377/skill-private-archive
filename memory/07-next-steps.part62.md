# 07-next-steps.part62.md

<!-- 本卷为 07-next-steps.md 的延续（r109 I-7 人工重切，零增减） -->

> 上一卷：`07-next-steps.part61.md`；本组首卷 `07-next-steps.part57.md` 含路由。

- **2026-10-02（第 100 轮 r100，同一指令逐字重发⇒完整再整跑；对手名册改测量派生 + 两件真换装）** — ① **本轮翻转 r99 结论**：ROSTER 原为源码手抄 10 仓，而同工具同轮 search_face 实测前 25 名里 **15 仓从未进面**（140497★ awesome-llm-apps、108698★ caveman、63335★ last30days-skill 皆在外）⇒ X-26 禁把手抄清单当扫描分母在对手面复发，「换装 0 件」实际只在约四成人口上成立。② 名册改由 derive_roster 现算 top-20 + roster_face 四态（含 UNVERIFIED_stale_cache 防旧缓存冒充派生面），夹具 25 腿→**38 腿全过**（取值：python 05-exec/r96_twelve_face.py --selftest）。③ 扩面后本地缺失 123 个 slug 逐族过 X-29 三门槛 ⇒ **装入 commit-archaeologist 与 scope-creep-detector**（各 4 文件齐装：SKILL.md、README、scripts、references；两脚本 ast.parse 过；无 shell=True；平台当轮即列出=可加载行为回执）；**卸载 0 件**（属缺口补件，无更差的对应本地件，不做无对象删除）。④ 两次自抓假干净：审计用 glob 大括号不展开⇒取到 0 文件却报 0 命中（改 os.walk 并印 scanned_face=8）；补丁一漏清 ROSTER 使用点⇒fetch_remote NameError 而夹具 35/35 全绿（补 3 条主链接线腿，Step 2.7 第 11 条第三次现形）。⑤ 注册表 rebuild 判 **BLOCKED（实测非推断）**：受管根 ?? 计 26 条含 24 个他人未入库件，全量重生必致注册表⇄BGE⇄skill_content 三方脱节；前提=可复算命令 python C:/Users/37533/Desktop/workspace/焚诀/eval/build_registry.py --dry-run。⑥ **回流节律实测**：executing-plans 与 slides 距上轮清零约 47 分钟第三次回到盘面 ⇒ 每小时重清不是自愈型收口，本轮清一次并把它降级为看守项（复算 python 05-exec/r59_retired_face.py），下轮起以节律而非单次绿为准。⑦ 27 门 FAIL=5 与 r99 同因（外部 +12 棘轮 + 元门延迟，不动基线）；焚诀 verify 42 PASS/1 FAIL=C25 同条。报告=06-benchmark/全量对标报告_r100_名册派生与两件换装_2026-10-02.md
  PASS 正例 red_flags 命中(body) got=True want=True
  PASS 正例 verification 命中(body) got=True want=True
  PASS 反例 process 不命中 got=False want=False
  PASS 反例 rationalizations 不命中 got=False want=False
  PASS 正例 fm 含 name+desc got=True want=True
  PASS 正例 fm both got=True want=True
  PASS 反例 无围栏判 fence=False got=False want=False
  PASS 反例 缺 description 判 False got=False want=False
  PASS 反例 缺 description 不得混进 both got=False want=False
  PASS 正例 slug 取父目录 got='foo-bar' want='foo-bar'
  PASS 反例 裸 SKILL.md 无 slug got=None want=None
  PASS 接线 d4 缺本地侧判 PARTIAL 不判 MEASURED got='PARTIAL' want='PARTIAL'
  PASS 接线 mismatched 清单必须点名缺侧维度 got=True want=True
  PASS 接线 双侧齐的维判 MEASURED got='MEASURED' want='MEASURED'
  PASS 接线 本地技能数>0 got=True want=True
  PASS 接线 入口注入字节>0 got=True want=True
  PASS 接线 本地 d4 schema 面被读到（>0 或显式 0 但总文件>0） got=True want=True
  PASS 接线 本地 d12 全量分母==技能数 got=True want=True
  PASS 接线 插件根被枚举且实到>0 got=True want=True
  PASS 接线 各根之和 == 去重后 + 跨根重复（分母自洽） got=320 want=320
  PASS 反例 跨根重复若被静默吞则该项必红 got=True want=True
  PASS 反例 只看权威源会低估 d1 got=True want=True
