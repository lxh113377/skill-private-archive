# r312 · task3 出厂校准记录（双臂执行前的双向压样，含一次「压样抓到样本自己失真」的实录）

跑法：python -B _temp/r312_calib.py（判据 _temp/r309a/anchor_judge.py 的 r312 参数化版，--named 传 task3 红线词表
「(订单金额|金额|clean)」）。结果逐字：
```
[CALIB3-NAIVE] 4=0(frac=0.784) 5=0(hits=['Tree of Thought', 'Mixture of Experts']) 6=0
[CALIB3-GOOD] 4=1(frac=0.0) 5=1 6=1 8=1(fake=[])
[R312:CALIB] PASS
```
三向：naive3 掉分=有牙；compliant3 全过=无假红；新领域跳过申报（<production_write> 未硬套）豁免仍生效。

**中间抓到的是我自己样本的失真**：第一版 compliant3 的 prompt 是散文版（没有段名），log 却声称 <hard_boundaries>/
<deliverables> 两段 ⇒ fake 判定把它们记 0——**判据是对的、样本是错的**（真实 compliant 交付本来就带 XML 段，
skill 就这么要求的）。修样本重跑三向全过。⇒ §5.8 双向压样不但压判据，也压「压样本身」——坏样本会把好判据冤枉成假红。

参数化动因（防第三次「没覆盖」）：item4 词表原是 task2 专属（价格|assets）⇒ 同尺直接换题会看不见 task3 的
金额/clean 红线。现 --named 随题传入，默认值=task2 原样（历史读数复现不受影响，selftest rc=0 + task2 终判 
delta=+14.29% 参数化后逐字复跑一致）。映射本轮为固定 X=before/Y=after（与 r309 抛硬币不同）——偏差如实记在
hidden_assignment.json；评分仍走第三方盲评臂。双臂（04a1591b/27e4c40b）执行中，交付后合判 n=2。
