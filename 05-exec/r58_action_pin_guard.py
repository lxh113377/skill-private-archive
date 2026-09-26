# -*- coding: utf-8 -*-
"""r58 第 17 维常驻判据：CI 动作必须钉到不可变 SHA，且必须有更新器推它。

为什么这是**判据输入面**问题而不是「安全洁癖」：
  本仓 21 道门全部读工作树。`actions/checkout` 在门禁之前决定工作树里有什么字节，
  它按 tag 引用 ⇒ tag 在 GitHub 侧可被重新指向 ⇒ 一次上游账号失陷就让 21 道门在
  **被改写过的源码**上判绿。与 r49「三处劫持根因修」、r56「声明要被机器校验」同族。

三条不变式（缺一即红）：
  P1 形态：每个 `uses:` 引用必须 pin 到 40 位十六进制 commit SHA（`@main`/`@v4`/`@master` 一律算浮动）
  P2 配对：存在 action 引用时，`.github/dependabot.yml` 必须声明 `github-actions` 生态
     —— pin 而无人推进 = 固定点腐烂，比浮动更坏（拿不到上游安全修复）
  P3 空面不判过（R247）：无 workflow 目录 / 无 `uses:` 引用 ⇒ UNVERIFIED 判红，
     禁「没有引用所以全绿」——那正是判据被搬家后静默失效的入口

用法：python 05-exec/r58_action_pin_guard.py [--workflows DIR] [--dependabot FILE]
退出码：0 全绿 / 1 有红项
"""
import argparse
import glob
import io
import os
import re
import sys

USES_RX = re.compile(r"^\s*(?:-\s*)?uses:\s*([^#\s]+)")
SHA_REF_RX = re.compile(r"@[0-9a-f]{40}$")
HEXISH_RX = re.compile(r"[0-9a-fA-F]{8,}$")
LOCAL_REF_RX = re.compile(r"^\./")
FLOATING_HINT = ("@main", "@master", "@trunk")
YML = re.compile(r"\.ya?ml$", re.I)


def collect(workflows_dir):
    """返回 (refs, floating, sha_like_but_bad, local_refs)。refs = [(file, ref)]。"""
    refs, floating, malformed, local = [], [], [], []
    for path in sorted(glob.glob(os.path.join(workflows_dir, "*.yml"))
                       + glob.glob(os.path.join(workflows_dir, "*.yaml"))):
        try:
            text = io.open(path, encoding="utf-8", errors="replace").read()
        except OSError as e:
            print("  ❌ 读不到 %s：%s" % (os.path.basename(path), e))
            floating.append((os.path.basename(path), "<unreadable>"))
            continue
        for ln in text.splitlines():
            m = USES_RX.match(ln)
            if not m:
                continue
            ref = m.group(1)
            base = os.path.basename(path)
            refs.append((base, ref))
            if LOCAL_REF_RX.match(ref):
                local.append((base, ref))
            elif SHA_REF_RX.search(ref):
                pass  # 正确的 40 位固定引用，无需登记
            elif HEXISH_RX.match(ref.rsplit("@", 1)[-1] if "@" in ref else ref):
                # 像 SHA 却不够 40 位（截断/多一位/大小写混写）——比 `@v4` 更危险，
                # 因为它**看起来**已固定，人和工具都容易放过
                malformed.append((base, ref))
            else:
                floating.append((base, ref))
    return refs, floating, malformed, local


def dependabot_ok(dep_file):
    if not os.path.isfile(dep_file):
        return False, "文件不存在"
    text = io.open(dep_file, encoding="utf-8", errors="replace").read()
    if "github-actions" not in text:
        return False, "存在但未声明 github-actions 生态"
    return True, "已声明 github-actions"


def main():
    ap = argparse.ArgumentParser()
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument("--workflows", default=os.path.join(here, ".github", "workflows"))
    ap.add_argument("--dependabot", default=os.path.join(here, ".github", "dependabot.yml"))
    args = ap.parse_args()

    print("=== r58 动作固定面守卫（只读，零网络）===")
    if not os.path.isdir(args.workflows):
        print("  ❌ workflow 目录不存在：%s（空面不得判过 R247）" % args.workflows)
        print("[GATE:actionpin-fail] 输入面为空")
        return 1
    refs, floating, malformed, local = collect(args.workflows)
    if not refs:
        print("  ❌ 未发现任何 `uses:` 引用 ⇒ 要么仓真没 CI，要么引用被搬家（判据须随搬家移动）")
        print("[GATE:actionpin-fail] 零引用面不可判绿")
        return 1
    for base, ref in floating + malformed:
        print("  ❌ 未固定: %s :: %s" % (base, ref))
    for base, ref in local:
        print("  ℹ️ 仓内本地 action（不经 Marketplace，无供应链面）: %s :: %s" % (base, ref))
    external = [r for r in refs if not LOCAL_REF_RX.match(r[1])]
    pinned = len(external) - len(floating) - len(malformed)
    print("  引用合计 %d 处（外部 %d / 本地 %d）｜ 已 pin 到 SHA %d ｜ 浮动或形态非法 %d" % (
        len(refs), len(external), len(local), pinned, len(floating) + len(malformed)))
    dep, why = dependabot_ok(args.dependabot)
    print("  P2 更新器配对: %s ｜ %s" % ("OK" if dep else "缺失", why))
    hints = [r for _b, r in floating if r.endswith(FLOATING_HINT)]
    if hints:
        print("  ⚠️ 其中 %d 处指向**分支**而非版本 tag（每次运行内容可变，风险最高一档）" % len(hints))
    bad = bool(floating or malformed) or not dep
    print("-" * 62)
    if bad:
        print("[GATE:actionpin-fail] P1 浮动/非法 %d 处 ｜ P2 配对 %s ｜ P3 输入面 %d 引用" % (
            len(floating) + len(malformed), "OK" if dep else "缺失", len(external)))
        return 1
    print("[GATE:actionpin-pass] P1 外部引用 %d/%d 全 pin ｜ P2 dependabot 已配 ｜ P3 输入面非空" % (
        pinned, len(external)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
