#!/bin/sh
# 自动推送钩子（A-project-handoff #20；由 git_autopush.py --install-hook 安装）
# 提交即自动 push；CI/无远端/无凭据场景静默跳过，不阻塞提交。
[ -n "$CI" ] && exit 0
git remote get-url origin >/dev/null 2>&1 || exit 0
git push --quiet origin HEAD >/dev/null 2>&1 || true
exit 0
