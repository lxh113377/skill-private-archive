# Mimosa 校准工单：路径穿越规则误报 + 修复循环死锁（13 项，附完整证据链）

> 提交日期：2026-09-24 ｜ 提交方：自建skill优化 项目（workspace `C:\Users\37533\Desktop\workspace\自建skill优化`）
> 目标组件：Mimosa for ZCode 插件 v1.0.3（protected-build，variantId `af8b4e5393f28ec0b00d678d`）
> 请求类别：规则校准（规则降级/白名单）+ 产品缺陷修复（adjudication 命令 / 编辑锁解除）
> 证据状态：全部结论附本机实测命令与行级证据；项目侧已尽力配合（消毒加固 + 策略声明），详见 §5

## 1. 一句话摘要

`mimosa audit --deep` 在本项目报 **13 项 CWE-22 高危「路径穿越」**，逐行核验**全部为误报**（源码常量字面量 join + open 写、无任何外部输入面、其中 3 处已按 finding 自身建议完成 realpath+commonpath 消毒仍被 flag）；且项目侧陷入**修复循环死锁**（含 blocked finding 的文件无法通过 Edit 修复）。请维护者校准规则并补裁定通道。

## 2. 环境与复现

```bash
CLI="C:/Users/37533/.zcode/cli/plugins/cache/zcode-plugins-official/mimosa/1.0.3/payload/dist/cli.js"
node "$CLI" doctor          # Node v24.16.0；规则 p/default,p/security-audit,p/secrets,p/bandit；Semgrep 进程不可用
node "$CLI" audit "C:/Users/37533/Desktop/workspace/自建skill优化" --deep
# → 13 高危（0 中低危/污点/依赖/业务逻辑）：路径穿越 ×13
node "$CLI" status --project "C:/Users/37533/Desktop/workspace/自建skill优化"
# → blocked=7（ledger 口径，全部 security/ direct / stable）
```

命中分布（`audit --deep` 实时行号，已与实况对齐）：

| 文件 | 行 | sink 形态 |
|---|---|---|
| `01-scan/scan_all.py` | 330/332/334 | `open(_out(SCOPE_DIR, "字面量"), "w")` —— **已消毒**（见 §3.2） |
| `01-scan/scan_all.py` | 484/488 | `open(os.path.join(SCAN_DIR, "字面量"), "w")` —— 常量 join |
| `05-exec/_lib.py` | 55 | `open(tmp, "wb")` 原子写，tmp 固定落在目标文件同目录 |
| `archive/one-shot-scripts-2026-09/`×6 文件 | 140/142/132/115/84/156/120 | 同族常量 join/变量写，**已退役不再执行** |

## 3. 误报依据（逐层）

**3.1 路径两端均为编译期字面量，无 `../`，无外部输入**
`SCOPE_DIR = os.path.join(WS, "00-scope")`，`WS` 为源码 raw-string 字面量（scan_all.py:29）；文件名全部为字面量。攻击者不可控输入集合为空——本地单人分析工具，参数仅操作者本人可传。

**3.2 消毒已按 finding 自身建议落地，仍被 flag**
- `_out()`（scan_all.py:34-41）：`os.path.realpath` 规范化 + `os.path.commonpath` 包含校验，逃出即 `SystemExit` 拒写——即 finding 建议的「规范化并校验路径，限制在允许目录内」的完整实现；330/332/334 三处已切换至该封装，**官方复扫 ×2（seal `279ae14b` / `140aab56`）照旗不误**。
- 运行时第二道防线：`__main__` 中 `--ws` 钉死本仓根（不等即拒）、`--gs/--registry` 存在性校验（正反例 4/4 实测），先于任何写阶段执行。
- `05-exec/_lib.py` 原子写：tmp = 目标文件同目录 + 固定前缀名，由调用方传入的项目内路径派生，无输入面。

**3.3 项目策略与威胁模型声明不作用于该规则（另见 §4 缺陷②）**
`.mimosa/security-policy.json` 已声明 `path.allowedWriteRoots`（9 目录）与 `threatModel.exclusions`（3 项字符串数组），`policy check` / `threat-model check` 双通过，`audit --deep` 计数不变。

## 4. 工具缺陷清单（5 项，均附实测）

| # | 缺陷 | 实测证据 |
|---|---|---|
| ① | **路径穿越规则不识别任何消毒形态**：函数封装（realpath+commonpath+raise）与裸常量 join 一律 flag；内联 `os.path.realpath(os.path.join(...))` 因缺陷③无法落地验证 | 复扫 ×2 计数恒 13，命中点即 `_out` 调用点 |
| ② | **policy / threatModel 不作用于确定性规则**：`allowedWriteRoots`、`exclusions` 校验通过但 audit 不变 | `policy check` ✓ / `threat-model check` ✓ → audit 13 不变 |
| ③ | **修复循环死锁：含 blocked finding 的文件编辑全锁**，且 deny 行号锚 stale（scan_all 恒指 474——已漂移至 484，该行现为 markdown 表头；_lib 恒指 10——docstring 行，从未是 sink） | PreToolUse Edit 连续 4 次 deny（3×scan_all + 1×_lib），候选内容即修复代码仍被拒 |
| ④ | **blocked finding 不随内容收敛**：`ledger checkpoint`（covered=8）折叠后 blocked 反 6→7（含已消毒行对应的 finding），无自动转 `fixed_static` 机制 | `status` 前后对比 |
| ⑤ | **`validate` 前置死循环**：仅收 `fixed_static`，而 finding 因缺陷③④永远到不了 `fixed_static` | `validate --help` 边界说明 + status |

**净效果**：一旦某文件产生 blocked finding，该项目侧不存在任何合法通道将其收敛——修不了（③）、清不掉（④）、验不了（⑤）、豁免不了（②）。

## 5. 项目侧已尽的配合（供复核）

1. 代码消毒：scan_all.py `_out` 封装 + 3/5 sink 转换 + CLI 注入路径 guard（正反例 4/4；dry-run 基线 56/21/31/43 不变）；py_compile 通过。
2. 策略声明：`.mimosa/security-policy.json`（allowedWriteRoots + exclusions，双 check 通过）。
3. 复扫配合：官方 `security_scan_start` deep ×2（seal `279ae14b` / `140aab56`）+ `mimosa audit --deep` ×4 + `ledger checkpoint` ×1。
4. 未采用的旁路（应属设计禁区）：Bash 直写、`--no-verify`、手造 ledger batch。

## 6. 校准请求（按优先级）

**R1 规则层（解 13 项误报）**——任选其一或组合：
- a) 常量传播豁免：`os.path.join(<源码字面量/字面量链>, <字面量>)` 且 open 写目标为固定文件名 → 降级 info 或不报；
- b) sanitizer 识别：`os.path.realpath`（内联或经函数封装）+ `commonpath` 包含校验 + 失败即中断的数据流 → 判定已消毒；
- c) 信任策略接入：`path.allowedWriteRoots` 声明内的写、或 `threatModel.exclusions` 命中的文件，确定性规则降级/跳过。

**R2 产品层（解修复死锁）**：
- a) 补 **adjudication 命令**：`mimosa ledger record` 支持 `false_positive`（含理由与证据哈希），CLI 出 `mimosa dismiss <finding-id> --reason ...`；
- b) 修 edit 钩子 stale 锚：deny 行号应取**当前候选**重扫结果，且当候选相对基线**减少** finding 时应放行；
- c) blocked → fixed_static 自动收敛：checkpoint 折叠时按 `codeEvidenceHash` 在当前内容中不复现即转 resolved（保留 reopen 能力）。

## 7. 验收判据

1. `mimosa audit "C:/Users/37533/Desktop/workspace/自建skill优化" --deep` 高危 13 → **0**（R1 生效）；
2. 对含 blocked finding 的文件可提交修复性 Edit（R2-b），checkpoint 后 blocked 清零（R2-c）；
3. 对照组不放宽：用户可控输入到达 sink 的真阳性样本仍报 high（请用贵方既有判据集回归）。

## 8. 关联留痕（本项目侧）

- 项目记忆 `memory/07-next-steps.md` P0 r10-r12 条（时间线 + 全部命令输出摘要）
- 全局 lessons `D:/global_memory/lessons/lessons.part39.md`（钩子行为两则）
- git 状态：加固与策略改动已 staged 未提交（commit 被 §4① 闸门拦），HEAD `d0ac826`
