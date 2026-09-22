# 01-scan — 阶段1 四维机器扫描（产物索引）

> 更新：2026-09-22（第 10 轮补齐） | 目标范围：**77 个**（HIGH 51 + MID 26，口径见 `00-scope/自建skill清单.md` v2）

## 产物清单

| 文件 | 生成方式 | 说明 |
|---|---|---|
| `scan_all.py` | 手写 | 阶段0/阶段1 唯一可复跑工具（`--stage scope\|scan`，默认 dry-run，`--apply` 才写盘） |
| `scan_report.md` | `scan_all.py --stage scan --apply` | 四维扫描基线（体积 / 触发 / 死链·通配符·平台名） |
| `scan_result.json` | 同上 | 逐 skill 结构化明细（含 `dead_refs` / `dead_wildcards` / `deprecated_platform_hits`） |
| `attention_sim_20260922.txt` | `焚诀/audit/attention_sim.py --trials 10000 --seed 42` | 注意力税三件套（上下文税 / 软注意力稀释 / 干草堆检索） |
| `content_snr_20260922.txt` | `焚诀/audit/content_snr.py` | 内容信噪比（M1–M4） |
| `negative_tag_audit_20260922.txt` | `焚诀/audit/negative_tag_audit.py` | 负标签健康检测 |

中间产物 `overlap_raw.txt`（282,977B）已迁 `../archive/overlap_raw.txt`；v1 扫描基线（2026-09-14，102 目标）已归档 `../archive/scan-v1-2026-09-14/`（R241 历史留痕不改写）。

## 复跑命令

```powershell
$env:PYTHONPYCACHEPREFIX="$env:TEMP\pycache_verify"
$py = "C:\Program Files\Python312\python.exe"
$ws = "c:\Users\37533\Desktop\workspace\自建skill优化"
& $py "$ws\01-scan\scan_all.py" --stage scan --apply          # 四维扫描基线
& $py "C:\Users\37533\Desktop\workspace\焚诀\audit\attention_sim.py" --trials 10000 --seed 42
& $py "C:\Users\37533\Desktop\workspace\焚诀\audit\content_snr.py"
& $py "C:\Users\37533\Desktop\workspace\焚诀\audit\negative_tag_audit.py"
```

## 2026-09-22 第 10 轮基线（实测）

| 维度 | 数值 |
|---|---|
| 目标数 | 77（HIGH+MID） |
| 超 4KB | **58 / 77** |
| description 无「触发词」字面量（弱代理指标） | 59 |
| 真死链候选 | **3**（`story-setup` ×2 / `A-get-memory` ×1 / `wps-knowledgebase` ×2 —— **全部为已标注项，无新增**） |
| 通配符死链候选 | **2**（`A-get-memory` 的 `scripts/wf_*.ps1` = 已标注不存在；`prompt-system-audit` 的 `scripts/*.ps1` = glob 文档用法，**误报**） |
| 弃用平台名命中 | **17** 个 skill（**判据修复后**；修前 12） |
| 注意力税 | 本会话上下文税 **9.32%**；软注意力稀释 **0.9x**；干草堆 Top-1 **46.9%** / Top-10 **87.5%** |
| 内容信噪比 | **4.7 / 6**（M3 索引声明失真 0.66、M4 自检金标准陈旧 0.50） |
| 负标签健康率 | **72.5%**（RESULT: **FAIL**） |

### ⚠️ 本轮修掉的两个判据缺陷（R220/R263 族：假通过 / 静默失效）

1. **通配符引用整体漏检**：原死链正则字符类不含 `*` 且要求以扩展名收尾 ⇒ `` `scripts/wf_*.ps1` `` 式引用**永远不进入检测**。已补 `dead_wildcards` 分支（`glob.glob` 实测存在性）。
2. **`CC` 检测静默失效**：`DEPRECATED_PLATFORMS` 含正则项 `r"\bCC\b"`，而匹配用的是 `d in raw`（**子串**）⇒ 该字面量**永不命中**。实证：`openclaw-task-supervision:114` 写「OC/WB/CC/TC/HM/CX」却从未被标出。已改 `re.search` 匹配（修后命中 12 → **17**）。

> 说明：CC 命中 17 个中**多数为正当历史留痕**（如「CC 已弃用 2026-09-08」的说明行），扫描只负责**暴露**，是否改写需逐条判定（见 `05-exec/第10轮执行报告.md` 建议 #4）。
