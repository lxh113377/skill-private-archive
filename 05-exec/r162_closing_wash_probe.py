# -*- coding: utf-8 -*-
# r162_closing_wash_probe.py -- 探针：旧 CLOSING_PAT 是否把纪律面洗成 closing（假 SKIP）。
#
# 存在理由：R159-1 第二面（旧正则过宽）当时只是推理；本探针把它变成可复算读数。
# 用法: python 05-exec/r162_closing_wash_probe.py
# 退出码: 0 完成 / 2 输入面不可用
import re
import sys

# 旧正则（r137 修复前，逐字复制自 git show HEAD:05-exec/r137_commit_gate_map.py）
OLD = re.compile(r'^(\?\?|.M|M.|MM) (06-benchmark/[^ ]+\.(json|jsonl)|05-exec/_r55probe_tmp/.*)$')

# TRIGGERS 里的纪律面路径（同样逐字取自 HEAD 版）
TRIGGER_PATHS = [
    '05-exec/',
    '06-benchmark/transmit_proposals.json',
    '06-benchmark/全量对标报告_',
    'AGENTS.md',
    'memory/07-next-steps.md',
    '05-exec/run_gates.py',
]


def main():
    washed = []
    for t in TRIGGER_PATHS:
        sample = (' M ' + t + 'r150_x.py') if t.endswith('/') else (' M ' + t)
        if OLD.match(sample):
            washed.append(t)
    print('[WASHPROBE] 纪律面 %d 条，被旧正则洗成 closing 的 %d 条：%s'
          % (len(TRIGGER_PATHS), len(washed), ', '.join(washed) or '(无)'))
    if washed:
        print('[WASHPROBE] 这些路径未 add 时会被判假 SKIP，击穿 r133 第4形态（禁按 0 记绿）')
        return 1
    print('[WASHPROBE:PASS] 无纪律面被洗成 closing')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())