# -*- coding: utf-8 -*-
r"""r21e_lesson52.py — 把「证据可解析性」教训落到 lessons.part52（50/51 均已被并行会话占满）。"""
import io
import os
import sys

DIR = r"D:\global_memory\lessons"
P52 = os.path.join(DIR, "lessons.part52.md")
CAP = 4096
SIZES = {f: os.path.getsize(os.path.join(DIR, f))
         for f in ("lessons.part49.md", "lessons.part50.md", "lessons.part51.md")
         if os.path.exists(os.path.join(DIR, f))}
ENTRY = """# lessons.part52

> 2026-09-24 r21e 新建。换卷理由 = 现有活跃卷 PLACEHOLDER_VOLS 均接近或超过 4,096B 上限，本批条目 **~1,180B** 无处可塞；**不改写不搬移他人在这些卷里的条目** ⇒ 另起新卷。旧卷字节数：PLACEHOLDER_SIZES。

### [2026-09-24] 🔴 门禁只校验「证据长得像证据」，等于把自证交给运气
trigger: 97 条已闭环声明 38.1% 解析不到 | 写footer,门禁判据,锚点校验 | 记忆系统,门禁,python
- **问题：** 门禁要求 `绝对路径 + #版本行:Vx.y.z`，但**从不验证路径是否存在、token 是否真在文件里**。近 3 日 97 条已闭环声明实测 37 条解析不到（38.1%），含引用根本不存在的文件与凭空写的 backup ID
- **原因：** 形状校验只花一次正则，可解析性要读盘 + 查 git 对象，历史上一直只做前者；且形状层强制 `V` 前缀，而真实文件里写的是裸值 `version: 10.70.0` ⇒ **诚实引用反被判不合规，随手加个 V 就能过**（判据在奖励美化而非真实）
- **解法：** ① 按「**能否事后合理化**」分三级：路径不存在 / 回滚件与 git 对象全无 = 阻断（4/97）；版本 token 被后续提交推走 = 只告警（18/97，声明当时可为真，追溯拦人即误伤）；体系外绝对路径 = 不判。② 前缀改可选，真伪交给可解析性。③ **收严前先量误伤面**（四类计数），按数据定阻断级别：同仓另有一次未测量就造判据的前例（TP 恒 0 / FP 1~3 ⇒ 当场否决）
- **元：** 来源=自建skill优化 r21e | 版本=upgrade_footer_gate 可解析性补丁 3466bb3 | 置信度=0.7（97 条实测样本） | 日期=2026-09-24 | 适用范围=记忆系统, 门禁, python, 多agent
"""


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if os.path.exists(P52):
        t = io.open(P52, encoding="utf-8-sig").read()
        print("[SKIP] part52 已存在（%dB，条目 %d，我的在位=%s）"
              % (os.path.getsize(P52), t.count("### ["), "长得像证据" in t))
        return 0
    head = ", ".join("%s=%dB" % (k, v) for k, v in sorted(SIZES.items()))
    txt = ENTRY.replace("PLACEHOLDER_SIZES", head).replace("PLACEHOLDER_VOLS", "49/50/51")
    n = len(txt.encode("utf-8"))
    if n > CAP:
        print("[停手] 新卷 %dB > %dB" % (n, CAP))
        return 1
    with open(P52, "wb") as f:
        f.write(txt.encode("utf-8"))
    b = io.open(P52, encoding="utf-8").read()
    ok = (b.count("### [") == 1 and "长得像证据" in b
          and all(c not in b for c in (chr(8), chr(0), chr(127))))
    print("[lessons] part52=%s | %dB | 控制符自检=0x08/0x00/0x7f 全无" % (ok, os.path.getsize(P52)))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
