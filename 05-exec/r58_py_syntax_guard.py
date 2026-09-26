# -*- coding: utf-8 -*-
"""r58 常驻判据：05-exec/*.py 必须能被 ast.parse —— 「工具跑不起来」此前无人看守。

触发实物（两条，都是本轮撞上的）：
  ① `05-exec/evidence_resolvability_measure.py:111` 少了 `print(` 的右括号 ⇒ 该文件**已入库且长期
     不可运行**，它产出的 `06-benchmark/evidence_resolvability_measure.json` 就成了
     「生成器根本跑不起来」的死句柄 —— W-46 只问「有没有生成器」，不问「生成器能不能加载」。
  ② 本轮自己新写的两件也各踩一次同类语法错（少括号），只在被调用时暴露。
⇒ 修法按「修同类不修单例」：不是补那一个括号，而是把「全目录可解析」钉成一道门。

只读、零网络、纯标准库。空面不判过（R247）：一个 .py 都扫不到 ⇒ 判红。
退出码：0 全绿 / 1 有不可解析件 / 2 目录不存在
"""
import argparse
import glob
import io
import os
import sys


def main():
    ap = argparse.ArgumentParser()
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--dir", default=here, help="待检目录（默认 05-exec 自身）")
    args = ap.parse_args()

    files = sorted(glob.glob(os.path.join(args.dir, "*.py")))
    if not os.path.isdir(args.dir):
        print("目录不存在：%s" % args.dir)
        print("[GATE:pysyntax-fail] 输入面不存在")
        return 2
    if not files:
        print("❌ %s 下一个 .py 都没有 ⇒ 空面不得判过（R247）" % args.dir)
        print("[GATE:pysyntax-fail] 零输入")
        return 1
    bad = []
    for p in files:
        try:
            src = io.open(p, encoding="utf-8", errors="replace").read()
        except OSError as e:
            bad.append((p, "OSError: %s" % e, 0))
            continue
        try:
            # 注意：`doraise` 是 ast.parse / py_compile 的参数，compile() **不接受**
            # —— 首版误带该参数，99/99 全被判「TypeError 不可解析」，是一整道门的假红。
            compile(src, p, "exec")
        except SyntaxError as e:
            bad.append((p, "SyntaxError: %s" % (e.msg or ""), e.lineno or 0))
        except Exception as e:  # ValueError（含 NUL）等也按不可加载算
            bad.append((p, "%s: %s" % (type(e).__name__, e), 0))
    print("=== r58 工具面可解析守卫（只读，零网络）===")
    print("  扫描 %s ｜ .py 共 %d 个" % (args.dir, len(files)))
    for p, why, ln in bad:
        loc = ":%d" % ln if ln else ""
        print("  ❌ %s%s  %s" % (os.path.basename(p), loc, why))
    print("-" * 62)
    if bad:
        print("[GATE:pysyntax-fail] 不可解析 %d/%d ⇒ 其产物即死句柄（W-46 的下一层）" % (len(bad), len(files)))
        return 1
    print("[GATE:pysyntax-pass] %d/%d 全部可解析（compile exec 模式，含缩进/括号配对）" % (len(files), len(files)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
