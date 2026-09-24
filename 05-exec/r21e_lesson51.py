# -*- coding: utf-8 -*-
r"""r21e_lesson51.py — lessons 新卷 part51（part50 已被并行会话占用且接近 4,096B 上限）。"""
import io
import os
import sys

P50 = r"D:\global_memory\lessons\lessons.part50.md"
P51 = r"D:\global_memory\lessons\lessons.part51.md"
CAP = 4096
ENTRY = """# lessons.part51

> 2026-09-24 r21e 新建。换卷理由 = 拟写入卷 `lessons.part50.md` 现 **3,923B**（上限 4,096B），本批条目 **~1,180B**，追加即破硬上限；part50 由并行会话同日新建，**不改写不搬移其条目** ⇒ 另起一卷。part49（3,243B）同样放不下本批。

### [2026-09-24] 🔴 门禁只校验「证据长得像证据」，等于把自证交给运气
trigger: 97 条已闭环声明 38.1% 解析不到 | 写footer,门禁判据,锚点校验 | 记忆系统,门禁,python
- **问题：** 门禁要求 `绝对路径 + #版本行:Vx.y.z`，但**从不验证路径是否存在、token 是否真在文件里**。近 3 日 97 条已闭环声明实测 37 条解析不到，含引用根本不存在的文件与凭空写的 backup ID
- **原因：** 形状校验只花一次正则，可解析性要读盘 + 查 git 对象，历史上一直只做前者；且形状层强制 `V` 前缀，而真实文件写的是裸值 `version: 10.70.0` ⇒ **诚实引用反被判不合规，随手加个 V 就能过**（判据在奖励美化而非真实）
- **解法：** ① 按「**能否事后合理化**」分三级：路径不存在 / 回滚件与 git 对象全无 = 阻断（4/97）、版本 token 被后续提交推走 = 只告警（18/97，声明当时可为真，追溯拦人即误伤）、体系外绝对路径 = 不判；② 前缀改可选，真伪交给可解析性；③ **收严前先量误伤面**（输出四类计数），按数据定阻断级别，不按感觉——同仓另有一次因未测量而误建判据的前例（TP 恒 0 / FP 1~3 ⇒ 当场否决）
- **元：** 来源=自建skill优化 r21e | 版本=upgrade_footer_gate 可解析性补丁 3466bb3 | 置信度=0.7（97 条实测样本） | 日期=2026-09-24 | 适用范围=记忆系统, 门禁, python, 多agent
"""


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if os.path.exists(P51):
        print("[SKIP] part51 已存在")
        return 0
    if "长得像证据" in io.open(P50, encoding="utf-8-sig").read():
        print("[SKIP] 条目已在 part50")
        return 0
    n = len(ENTRY.encode("utf-8"))
    if n > CAP:
        print("[停手] 新卷 %dB > %dB" % (n, CAP))
        return 1
    with open(P51, "wb") as f:
        f.write(ENTRY.encode("utf-8"))
    b = io.open(P51, encoding="utf-8").read()
    ok = b.count("### [") == 1 and all(c not in b for c in (chr(8), chr(0), chr(127)))
    print("[lessons] part51=%s | %dB | 控制符自检通过=%s" % (ok, os.path.getsize(P51), ok))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
