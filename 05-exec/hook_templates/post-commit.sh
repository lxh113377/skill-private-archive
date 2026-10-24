#!/bin/sh
# 自动推送钩子（A-project-handoff #20；本仓 r138_install_hooks.py 从 hook_templates 安装）
# 提交即自动 push；CI/无远端/无凭据场景静默跳过，不阻塞提交。
# 2026-10-16 补字形守卫段：提交信息里的中文串若是项目名的近形变体（编辑距离1，
# 如 公孝心联↔孝心联），跳过本次自动推送并写日志喊话——错字提交不再直上远端。
# 守卫语义 fail-open：py/python 都不在、脚本丢失、超时、异常 ⇒ 一律照常推送。
# 退出码约定：0=放行 3=近形拦截；钩子对其他非零码一律视为守卫故障、放行。
[ -n "$CI" ] && exit 0
git remote get-url origin >/dev/null 2>&1 || exit 0

GUARD="D:/global_skills/A-project-handoff/scripts/git_autopush.py"
if [ -f "$GUARD" ]; then
  PYBIN=py
  command -v "$PYBIN" >/dev/null 2>&1 || PYBIN=python
  # WindowsApps 的 python.exe 是 Store 桩（静默 rc=9009），py 启动器优先；
  # 两个都没有 ⇒ 跳过守卫直接推（fail-open）。
  if command -v "$PYBIN" >/dev/null 2>&1; then
    GRC=0
    "$PYBIN" "$GUARD" --guard-hook --repo "$(git rev-parse --show-toplevel 2>/dev/null)" >/dev/null 2>&1
    GRC=$?
    [ "$GRC" -eq 3 ] && {
      GITDIR=$(git rev-parse --git-dir 2>/dev/null || echo .git)
      # 空 MSG 不写日志：二次调用若意外放行（如并发改坏了钩子），写一行只有时间戳的空记录
      # 会让「有日志」被读成「有拦截」，正是自己立的「取不到数禁当 0」同族。
      MSG=$("$PYBIN" "$GUARD" --guard-hook --repo "$(git rev-parse --show-toplevel 2>/dev/null)" 2>&1 | tr -d '\\r' | tr '\\n' '  ')
      [ -n "$MSG" ] && printf '%s guard=near-miss %s\n' "$(date -Iseconds)" "$MSG" >> "$GITDIR/push-failure.log" 2>/dev/null
      echo "[post-commit] $MSG" >&2
      exit 0   # 拦的是「自动推送」这一步，不是提交本身
    }
    # GRC=0 放行；其他非零=守卫故障 ⇒ 放行（fail-open）
  fi
fi

PRC=0
git push --quiet origin HEAD >/dev/null 2>&1 || PRC=$?
GITDIR=$(git rev-parse --git-dir 2>/dev/null || echo .git)
# r205 结果留痕：自动推送无论成败都在 .git/autopush.log 记一行 rc+ts+head。
# 旧版 `git push ... || true` 成败全吞、零留痕 ⇒ 提交后 origin 没动也无人知晓（需代理网络尤甚）。
# 仍 fail-open：留痕写失败也不挡提交；可见性交第 87 门 r205_push_autopush_face.py 判。
printf "ts=%s rc=%s head=%s\\n" "$(date +%Y-%m-%dT%H:%M:%S)" "$PRC" "$(git rev-parse --short HEAD 2>/dev/null)" >> "$GITDIR/autopush.log" 2>/dev/null
exit 0
exit 0
