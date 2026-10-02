# -*- coding: utf-8 -*-
"""r103_goal_patch.py — 生成 GM memory/01-goal.md 当前口径行的 old/new 两片。

为什么需要本件：C16 判据拿 `01-goal.md:20` 的 skill 数与注册表实测对账；r103 换装轮
把注册表 173→176，该行必须同步，否则红是本会话自己造出来的。
行是**单条超长行**且他方会话有一处未提交改动落在同一行（172→173 的 codebuddy-chat-web
注记）⇒ 本件只做「在他方文本之后追加本会话注记」，不重排、不删除、不改写既有字面（R241）。

退出码：0=两片生成且锚点命中==1；1=锚点异常（不落片）。
"""
import io
import os
import sys

GOAL = r"D:/global_memory/memory/01-goal.md"
TMP = os.environ.get("TEMP", "/tmp")
OLD_P = os.path.join(TMP, "r103_goal_old.txt")
NEW_P = os.path.join(TMP, "r103_goal_new.txt")

ANCHOR = "三方一致 **173 skill / 13 域**"
NOTE = ("（2026-10-03 r103 GitHub 对标换装轮：X-29 三门槛首次有成立件，装入 "
        "healthcare-cdss-patterns / healthcare-emr-patterns / healthcare-eval-harness "
        "三件（源 affaan-m/ECC@main，MIT，逐件 sha256 读回全等；本地无对应差件 ⇒ 卸载 0 件），"
        "173→176，build_registry --apply + build_indexes 守恒 PASS 176 条；"
        "取值 `python eval/build_registry.py --dry-run`）")


def main():
    raw = io.open(GOAL, encoding="utf-8").read()
    hits = raw.count(ANCHOR)
    if hits != 1:
        print("[GOAL-PATCH:FAIL] 锚点命中 %d 次（须==1），不落片" % hits)
        return 1
    if "r103 GitHub 对标换装轮" in raw:
        print("[GOAL-PATCH:ALREADY] 本会话注记已在盘上，无需改动")
        return 0
    with io.open(OLD_P, "w", encoding="utf-8", newline="") as f:
        f.write(ANCHOR)
    with io.open(NEW_P, "w", encoding="utf-8", newline="") as f:
        f.write(ANCHOR.replace("173 skill", "176 skill") + NOTE)
    print('{"anchor_hits": %d, "delta_chars": %d, "old": "%s", "new": "%s"}'
          % (hits, len(ANCHOR.replace("173 skill", "176 skill") + NOTE) - len(ANCHOR),
             OLD_P, NEW_P))
    return 0


if __name__ == "__main__":
    sys.exit(main())
