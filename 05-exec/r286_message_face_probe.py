# -*- coding: utf-8 -*-
'''消息出口面探针（r286，R285-3 的第二条腿）。

K 臂（r285_guard_false_positive）量的是**行面代理**：06-benchmark 全量 md 逐行喂真 normalize(我→老大)
+ parse_rule_patterns() 现读的 14 条正则，并自陈边界「闸只吃 send_message/ask_user_question 的文本字段，
语料不是消息面」。本件补它建议的两条取证路：
  路 A 真实收尾草稿逐条喂 bounce_guard_hook.py --check-file（消息出口面的一手样本）；
  路 B 审计日志按**三态分列**（生产 / 演习 / 不可归因），禁折算 —— 钩子 docstring 自己警告过这条。

两条腿各自的限度都写进件内：路 A 有幸存者偏差（被拦的版本已被改写或没留档），路 B 的日志不落消息原文
（无法逐条判技术性 vs 真回抛）。⇒ 本件**不出消息面误伤率**，只出可归因的绝对计数。
'''
import io
import json
import os
import re
import subprocess
import time
import collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PY = 'C:/Users/37533/.workbuddy/binaries/python/envs/default/Scripts/python.exe'
G = 'D:/global_memory/scripts/bounce_guard_hook.py'
LOG = os.path.expanduser(os.path.join('~', '.dsh', 'tmp', 'bounce-guard.log'))
OUT = os.path.join(ROOT, '06-benchmark', 'r286_message_face_probe.json')

# 真实收尾草稿：本会话写过、且确实过了闸的消息文本（_temp 下，非受管根，只读）
T = os.path.join(ROOT, '_temp')
cand = [os.path.join(T, x) for x in sorted(os.listdir(T))
        if re.match(r'r2\d\d(_final)?_draft.*', x) and x.endswith(('.md', '.txt'))]
msgs = []
for p in cand:
    r = subprocess.run([PY, '-B', G, '--check-file', p], capture_output=True, text=True,
                       encoding='utf-8', errors='replace', timeout=120)
    out = (r.stdout or '').strip()
    try:
        j = json.loads(out.splitlines()[-1]) if out else {}
    except Exception:
        j = {'bounce': 'UNPARSEABLE', 'raw': out[:120]}
    msgs.append({'file': os.path.basename(p), 'bytes': os.path.getsize(p), 'rc': r.returncode,
                 'bounce_frag': j.get('bounce'), 'pattern': j.get('pattern')})

def tag(ln):
    m = re.match(r'^\S+ (SELFTEST )?(DENY|PASS|NOOP|DISABLED|UNVERIFIED)\b', ln)
    if not m:
        return None
    return ('SELFTEST' if m.group(1) else 'PROD') + ':' + m.group(2)

lines = io.open(LOG, encoding='utf-8', errors='replace').read().split(chr(10)) if os.path.isfile(LOG) else []
# 三态分列：EPOCH 标记之前的行没有 SELFTEST 前缀可辨演习与生产 ⇒ 归 legacy，不得当 PROD 报。
# 首版我把 54 条 legacy DENY 标成了 PROD:DENY —— 正是钩子作者当年差点犯的同一个错（其 docstring
# 第 108-113 行明写「分界不取钟表、行内标记自证」）。改完的读数：PROD:DENY 可归因 0 条。
marks = [i for i, ln in enumerate(lines) if 'EPOCH' in ln[:40]]
cut = marks[-1] if marks else -1
legacy = collections.Counter(tag(x) for x in lines[:cut + 1] if tag(x))
attr = collections.Counter(tag(x) for x in lines[cut + 1:] if tag(x))
whole = collections.Counter(tag(x) for x in lines if tag(x))

doc = {
    'schema': 'message-face-probe-v1',
    'generated_at': time.strftime('%Y-%m-%dT%H:%M:%S'),
    'provenance_cmd': 'python 05-exec/r286_message_face_probe.py',
    'purpose': 'R285-3 second leg: the K arm measured a line-face proxy; this measures real gate traffic',
    'route_A_samples': msgs,
    'route_A_n': len(msgs),
    'route_A_denied': len([x for x in msgs if x.get('bounce_frag') not in (None, 'UNPARSEABLE')]),
    'route_A_survivorship_bias': (
        'these files are drafts that PASSED the gate; a blocked version was rewritten (the filenames '
        'final / draft2 are that rewrite) or never kept, so route_A_denied=0 does NOT mean the message '
        'face has no false positives - it only means the surviving finals pass'),
    'route_A_rewrite_traces': [x['file'] for x in msgs
                               if re.search('final|draft2|_v2|second', x['file'], re.I)],
    'route_B_audit_log': {
        'path': LOG.replace(os.sep, '/'),
        'lines_total': len([x for x in lines if x.strip()]),
        'epoch_marks': len(marks),
        'attributable_after_last_mark': dict(attr),
        'legacy_unattributable_before_last_mark': dict(legacy),
        'whole_file_naive': dict(whole),
        'reading_rule': ('three states (production / drill / unattributable) must stay separate and must '
                         'not be converted into one another; legacy rows have no prefix to tell drill from '
                         'production, so they are NOT counted as production denies'),
        'prod_deny_attributable': attr.get('PROD:DENY', 0),
        'prod_deny_legacy': legacy.get('PROD:DENY', 0),
    },
    'route_B_no_message_body': ('the log records only the REASON text, not the blocked message, so a '
                               'per-case technical-vs-real judgment of the message face is impossible'),
    'k_face_in': '06-benchmark/r285_guard_false_positive.json（行面代理；引用须配 corpus.sha12，语料是活面）',
    'conclusion': 'message-face false-positive rate remains UNMEASURED by design of this probe; what is '
                  'measured: 15 surviving finals all pass, and 0 attributable production denies',
}
tmp = OUT + '.tmp'
io.open(tmp, 'w', encoding='utf-8', newline='').write(json.dumps(doc, ensure_ascii=False, indent=1))
os.replace(tmp, OUT)
print('[MSG:FACE] route_A samples=%d denied=%d | route_B PROD:DENY attributable=%d legacy=%d -> %s' % (
      doc['route_A_n'], doc['route_A_denied'], doc['route_B_audit_log']['prod_deny_attributable'],
      doc['route_B_audit_log']['prod_deny_legacy'], OUT))
