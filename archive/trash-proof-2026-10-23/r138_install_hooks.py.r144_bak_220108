# -*- coding: utf-8 -*-
# r138_install_hooks.py -- 把 git hooks 从「手工写、易丢失」变成「一条命令重装且自证」。
#
# 存在理由（r137 一手）：r137 装了分级阻断的 pre-commit，但收尾发现 .git/hooks/ 不在 git 里
#   （tracked hooks = 0）=> 换机 / clone / 重装即全丢，而当时没有任何判据能发现这件事。
#   r130 与 r137 两次装 hook，装完都没再核过 —— 「阻断机制不可恢复」比「没有阻断机制」更危险，
#   因为它让人以为有。
#
# 本件做两件事：
#   1) 从 git 跟踪的模板（05-exec/hook_templates/*.sh）安装到 .git/hooks/；
#   2) 装完立刻自证（跑 r138_hook_health.py），不通则判红。
#
# 用法: python 05-exec/r138_install_hooks.py [--dry-run] [--json <件>]
# 退出码: 0 安装且自证通过 / 1 自证不通过 / 2 输入面不可用
import argparse
import io
import json
import os
import shutil
import stat
import subprocess
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TPL = os.path.join(HERE, 'hook_templates')
HOOKS = os.path.join(ROOT, '.git', 'hooks')
HEALTH = os.path.join(HERE, 'r138_hook_health.py')
TARGETS = [('pre-commit.sh', 'pre-commit'), ('post-commit.sh', 'post-commit')]


def sha256_json(obj):
    # r143：对 stamp 的规范化 JSON 求 sha256（keys 排序，保证可复算）
    import hashlib as _hl
    payload = json.dumps(obj, ensure_ascii=False, sort_keys=True)
    return _hl.sha256(payload.encode("utf-8")).hexdigest()


def last_line_hash(dst):
    # r143：取 .installed.log 末行的 line_hash；无文件/无行/无该字段 => GENESIS
    logp = dst + '.installed.log'
    try:
        last = ''
        with io.open(logp, encoding='utf-8', errors='replace') as f:
            for line in f:
                if line.strip():
                    last = line
        if last:
            o = json.loads(last)
            return o.get('line_hash') or 'GENESIS'
        return 'GENESIS'
    except Exception:
        return 'GENESIS'


def next_seq(dst):
    # r142：从 .installed.log 现有行数推下一个序号（单调增，删日志会重排 —— 见 R142-4）
    logp = dst + '.installed.log'
    try:
        n = 0
        with io.open(logp, encoding='utf-8', errors='replace') as f:
            for line in f:
                if line.strip():
                    n += 1
        return n + 1
    except Exception:
        return 1


def invoker_info():
    # r141：取「谁调的安装」三个可自动获得的标识（R140-4 落地）。
    # 原则：全部自动取，取不到留空并显式说明，禁猜、禁硬编码。
    info = {}
    try:
        info["git_user"] = subprocess.run(
            ["git", "config", "user.name"], cwd=ROOT,
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=60).stdout.strip()
    except Exception:
        info["git_user"] = ""
    try:
        info["git_email"] = subprocess.run(
            ["git", "config", "user.email"], cwd=ROOT,
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=60).stdout.strip()
    except Exception:
        info["git_email"] = ""
    info["session"] = (os.environ.get("DSH_SESSION_ID")
                        or os.environ.get("CLAUDE_SESSION_ID")
                        or os.environ.get("TERM_SESSION_ID")
                        or "")
    info["pid"] = str(os.getpid())
    return info


def install(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copyfile(src, dst)
    try:
        mode = os.stat(dst).st_mode
        os.chmod(dst, mode | stat.S_IEXEC | stat.S_IREAD | stat.S_IWRITE)
    except Exception:
        pass
    # r140 加印记（R139-4 落地）：把「模板 sha + 安装时间」写进实装件旁的 .installed 印记。
    # 没有它，漂移时只能看到两个 sha 和两个 mtime，无法回答：
    #   ① 实装件是哪个模板版本装的？② 装完之后有没有被改？
    # （实装件不在 git 内，无历史可查 —— 这是 R139-4 的核心缺口）
    try:
        import hashlib as _hl
        h = _hl.sha256()
        with io.open(src, 'rb') as f:
            for chunk in iter(lambda: f.read(65536), b''):
                h.update(chunk)
        # r141 加 invoker（R140-4 落地）：印记原先只有模板 sha + 安装时间，
        # 多会话/多人装 hook 时无法归因到「哪次安装、谁装的」。
        # 取三个可自动获得的标识：git user.name / git user.email / 会话标识；
        # 都不硬编码 —— 取不到就留空并显式说明，禁猜。
        stamp = {
            "schema": "hook-installed-stamp-r141-v1",
            "hook": os.path.basename(dst),
            "template": os.path.basename(src),
            "template_sha256": h.hexdigest(),
            "installed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "invoker": invoker_info(),
            "reason": os.environ.get("HOOK_INSTALL_REASON") or "(未说明)",
            "note": "本印记由 r138_install_hooks.py 写入；漂移判定见 r140_hook_trace.py",
        }
        # r142 追加安装历史（R141-4 落地）：.installed 快照每装一次就被覆盖，
        # 只能归因到最近一次安装，更早的记录彻底丢失（r142 量化坐实：装 2 次后
        # 第 1 次的 reason 在整套 .git/hooks/ 里搜不到）。
        # 解法 = 快照保留（兼容第 52/53 门）+ 追加 JSONL 历史（本项新增）。
        with io.open(dst + '.installed', 'w', encoding='utf-8', newline=chr(10)) as f:
            json.dump(stamp, f, ensure_ascii=False, indent=1)
        # r143 哈希链（R142-4 落地）：prev_hash = 上一行的 line_hash（首行 = GENESIS）。
        # 篡改/重排任意一行 => 该行 line_hash 变 => 后续行的 prev_hash 对不上 => 链断。
        # ⚠ 载荷约定（r143 自抓：初版把 line_hash 算在 seq 赋值之前，且验证端排除
        #   载荷 = 除 line_hash 外的全部字段（**含 seq**，seq 必须先定）。
        #   写入顺序 = seq 先定 => prev_hash 再定 => line_hash 最后算。
        stamp["seq"] = next_seq(dst)
        prev_hash = last_line_hash(dst)
        stamp["prev_hash"] = prev_hash
        stamp["line_hash"] = sha256_json(stamp)
        with io.open(dst + '.installed.log', 'a', encoding='utf-8', newline=chr(10)) as f:
            f.write(json.dumps(stamp, ensure_ascii=False) + chr(10))
    except Exception:
        pass
    return os.path.getsize(dst)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--json', dest='out')
    args = ap.parse_args()
    if not os.path.isdir(TPL):
        print('[INSTALL] UNVERIFIED 模板目录不存在: %s' % TPL)
        return 2
    if not os.path.isfile(HEALTH):
        print('[INSTALL] UNVERIFIED 自证工具不存在: %s' % os.path.basename(HEALTH))
        return 2
    rows = []
    for tpl, name in TARGETS:
        s = os.path.join(TPL, tpl)
        d = os.path.join(HOOKS, name)
        if not os.path.isfile(s):
            rows.append({'hook': name, 'template': tpl, 'installed': False,
                          'note': '模板缺失（跳过，非致命）'})
            continue
        if args.dry_run:
            rows.append({'hook': name, 'template': tpl, 'installed': False,
                          'note': 'dry-run', 'size': os.path.getsize(s)})
            continue
        try:
            sz = install(s, d)
            rows.append({'hook': name, 'template': tpl, 'installed': True, 'size': sz})
        except Exception as e:
            rows.append({'hook': name, 'template': tpl, 'installed': False,
                          'note': repr(e)})
    if args.dry_run:
        n = len([r for r in rows if r.get('note') == 'dry-run'])
        print('[INSTALL] dry-run：将安装 %d 个 hook（未实际写入）' % n)
        for r in rows:
            print('  WOULD-INSTALL %s <- %s (%s B)' % (r['hook'], r['template'], r.get('size', '?')))
        return 0
    rc = 2
    hout = ''
    try:
        p = subprocess.run([sys.executable, HEALTH], cwd=ROOT, capture_output=True,
                           text=True, encoding='utf-8', errors='replace', timeout=300)
        rc = p.returncode
        hout = (p.stdout or '') + (p.stderr or '')
    except Exception as e:
        hout = repr(e)
    line = ''
    for l in hout.splitlines():
        if l.startswith('[HOOKHEALTH]'):
            line = l.strip()
            break
    # r139 接入（R138-4）：装完除了健在性自检，还要跑「恢复源与实装件逐字节一致」自检。
    # 只跑前者会出现「自检绿但模板与实装已漂移」—— r139 实测坐实过。
    SYNC = os.path.join(HERE, 'r139_hook_sync.py')
    src_rc = 2
    sout = ''
    if os.path.isfile(SYNC):
        try:
            q = subprocess.run([sys.executable, SYNC], cwd=ROOT, capture_output=True,
                               text=True, encoding='utf-8', errors='replace', timeout=300)
            src_rc = q.returncode
            sout = (q.stdout or '') + (q.stderr or '')
        except Exception as e:
            sout = repr(e)
    sline = ''
    for l in sout.splitlines():
        if l.startswith('[HOOKSYNC]'):
            sline = l.strip()
            break
    doc = {'schema': 'install-hooks-r138-v1',
           'cmd': 'python 05-exec/r138_install_hooks.py --json <out>',
           'face': {'installed_n': sum(1 for r in rows if r.get('installed')),
                     'rows_n': len(rows),
                     'self_check_rc': rc,
                     'self_check_line': line,
                     'sync_check_rc': src_rc,
                     'sync_check_line': sline,
                     'reading': {
                         'self_check_rc': '装完立刻跑 hook 健在性自检的退出码；非 0 = 装好了但缺件，须判红',
                         'sync_check_rc': '装完再跑「恢复源与实装件逐字节一致」自检的退出码；非 0 = 模板与实装已漂移，须判红（r139 接入）',
                         'installed_n': '实际安装成功的 hook 数',
                     }},
           'rows': rows}
    if args.out:
        with io.open(args.out, 'w', encoding='utf-8', newline=chr(10)) as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
    fa = doc['face']
    print('[INSTALL] 安装 %d/%d | 健在性自证 rc=%d | 同步自证 rc=%d'
          % (fa['installed_n'], fa['rows_n'], fa['self_check_rc'], fa['sync_check_rc']))
    if line:
        print('  ' + line)
    if sline:
        print('  ' + sline)
    for r in rows:
        print('  %-12s %s %s' % (r['hook'], 'INSTALLED' if r.get('installed') else 'SKIPPED', r.get('note', '')))
    if args.out:
        print('[INSTALL] JSON -> %s' % args.out)
    return 0 if (rc == 0 and src_rc == 0) else 1


if __name__ == '__main__':
    raise SystemExit(main())