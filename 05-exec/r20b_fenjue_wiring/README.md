# 转办包（升级版）：把 C31′/C32′/C33′ 接进焚诀 verify —— 编号已二次让号

> 为什么让号：本仓 r18 提出时拟用 C29/C30/C31；r19b 实测焚诀已落地 **C29 = index.md 与派生评分产物对账**；
> r20b 再实测焚诀 `205ed81` 又落地 **C30 = 路由静态表目标存活与覆盖空洞棘轮**
> （取值：`grep -n "('C30'" 焚诀/eval/verify_truth_consistency.py`）。⇒ 本包三项改号 **C31′/C32′/C33′**。
>
> 为什么本仓不代改：项目红线「焚诀 `eval/` 只读调用不改」，且该仓此刻有在途改动（r20b 实测 27 条），
> 代改必然踩本仓刚落地的「写前脏源检测」（受管根 `9a15f4e`）。
> **判据逻辑全部在本仓已测实现里**，本包只给接线位置与口径，不复制未经焚诀运行时验证的代码。

## 一、三项判据的「已测实现」在哪

| 建议判据 | 已测实现（本仓，直接可跑） | 实测现状（2026-09-24 21:3x） |
|---|---|---|
| **C31′ 目录注意力税棘轮** | `05-exec/catalog_attention_tax.py`（枚举 166 纳入 + 1 junction，全库 name+description 合计）| `grand_chars=45,250`（r18 为 45,173，+77 来自他端新增技能 ⇒ 无棘轮则线性恶化） |
| **C32′ 注入区口径合一** | `05-exec/ratchet_gate.py:inject_union_bytes()`（C25 清单 **实测磁盘字节** ∪ 项目注入壳，路径去重） | 并集 **87,878B > 硬顶 65,536B（+22,342）而 C25 判 PASS** |
| **C33′ 计数断言内容级对账** | `05-exec/claim_truth_scan.py`（端数/枚举/退役声明、裸技能计数、版本引用三族 + 历史行豁免 + 真相源不可读 exit 2） | 首跑 10 条候选 → 修完注入面 6 句后 **4 条**（含 2 条语义误报，已登记为工具盲区） |

## 二、接线位置（三处，逐条给锚点）

1. **注册表**：`焚诀/eval/verify_truth_consistency.py` 的 `checks` 元组列表尾部（现最后一项是 `('C30', ...)`）
   追加三行，形状与 C30 一致：`('C31', '<名>', lambda: _check_fn('check_c31_xxx')())`。
   ⚠️ 沿用其既有教训（该文件第 566 行原文注）：**显式关键字传参**——C30 曾因位置参落到别的名参而**恒 PASS**。
2. **实现落点**：`eval/verify_checks/governance_layer.py`（与 C25 同族，注入预算就在这里）
   或 `registry_layer.py`（与 C30 同族）。C33′ 属「正文内容对账」，建议新开 `claim_layer.py` 以免再堆巨石。
3. **口径单一真相源**：`eval/truth_constants.json` 的 `inject_budget` 段
   —— C32′ 的关键不是再写一份清单，而是**让 C25 与 attention_sim 共用同一份 files 列表**，
   并把 `shell_project` 从「按 cwd 解析（实钉焚诀）」改为「按当前项目解析」；
   否则并集口径仍会两套并存（r19b 实测两套定义仅 1 文件重叠）。
   `bytes` 字段建议改为**运行时实测**（本仓实测登记值会滞后于盘上真值：登记 64,472 vs 实测求和不同）。

## 三、交付契约（本仓踩过的坑，别再踩一次）

- **必须补隔离桩并登记**：`eval/stubs/registry.json` 加 `covers: ["C31","C32","C33"]`，
  否则 `eval/gate_stub_runner.py` 会以「新增判据未补桩」判 `stub-fail`（r18/r20 本仓两次实测到该门禁生效）。
- **桩要含对照组**（R238）：正例（现状 PASS）+ 违规样本（人为超阈必须 FAIL）。
  可直接抄本仓 `05-exec/r20b_ratchet_fixtures.py` 的六类样本：全等基线零发现 / +1 字符即拦 /
  超硬顶必须报 / 变好不报 / 非数值记 unknown 不当 0 / 无基线不得放行。
- **棘轮只降不升**：基线写进 `truth_constants`（与 C25 `baseline_bytes` 同形态），
  并拒绝「实测变大就抬基线」（本仓 `ratchet_gate.py --update` 已实现该拒绝，测试用例「现状高于基线时 --update 拒绝」在案）。

## 四、验收判据（本包被采纳后本仓会复跑核验）

```bash
python 焚诀/eval/verify_truth_consistency.py        # 期望：C31/C32/C33 三行 PASS，总 FAIL 数不增
python 焚诀/eval/gate_stub_runner.py                # 期望：[GATE:stub-pass]，未登记判据 0
python 05-exec/catalog_attention_tax.py             # 与本仓基线对齐后，grand_chars 应只降不升
```
