# 07-next-steps.part63.md

<!-- 本卷为 07-next-steps.md 的延续（r109 I-7 人工重切，零增减） -->

> 上一卷：`07-next-steps.part62.md`；本组首卷 `07-next-steps.part57.md` 含路由。

  PASS 正例 派生按星标降序取前 N got=['b/y', 'a/x'] want=['b/y', 'a/x']
  PASS 接线 不可解析行不进面但必须计数 got=1 want=1
  PASS 反例 截断必须可见（top_n 小于可用行数） got=True want=True
  PASS 正例 pinned 追加且去重保序 got=['b/y', 'a/x', 'd/w'] want=['b/y', 'a/x', 'd/w']
  PASS 反例 空面不得静默判过 got=[] want=[]
  PASS 反例 空面判据必须给独立态不是 matched got='UNVERIFIED_empty_face' want='UNVERIFIED_empty_face'
  PASS 反例 陈旧缓存不得冒充 matched got='UNVERIFIED_stale_cache' want='UNVERIFIED_stale_cache'
  PASS 接线 同失效形态由缺键派生，不靠调用方传标记 got='UNVERIFIED_stale_cache' want='UNVERIFIED_stale_cache'
  PASS 正例 默认无人 pin 而派生面有仓 = 修好了，判 matched got='matched' want='matched'
  PASS 反例 pin 了却没进面=漏扫，必须 mismatched 并点名 got='mismatched' want='mismatched'
  PASS 接线 score_dims 吃真缓存不抛（CLI 主链可达） got=True want=True
  PASS 反例 旧缓存无派生键必须显 UNVERIFIED 不是 matched got='matched' want='matched'
  PASS 接线 打分产物逐维自证在场 got=True want=True
  PASS 接线 双单位并报且 toplevel<=alllayers got=True want=True
  PASS 接线 并集 slug 数>=权威源 slug 数 got=True want=True
