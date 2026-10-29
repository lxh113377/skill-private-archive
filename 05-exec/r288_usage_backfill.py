# -*- coding: utf-8 -*-
'''r288_usage_backfill.py - 把 GM 日件 footer 的真实 skill 调用回填进 skill_usage 表（R281-2 续）。

能回填什么、不能回填什么（2318 份日件实测，不是推测）：
  可回填：1135 份日件的 [skill清单] footer 带可解析的 skill 名，形如
          「本轮调用=2 个 (A-memory-start, A-project-handoff)」，且同文件多有 session= / ts= 键。
  不可回填：任务级结果。结果词出现在 footer 行内的只有 PASS 3 / FAIL 1 / 失败 4 / 落地 4（约 0.2%）
          ⇒ 历史行 outcome 一律 unknown，绝不猜（unknown 是表设计里的显式合法值）。

五条硬约束（每一条都来自本会话真实踩过的坑）：
  1) 幂等：键必须由**行自身字段唯一决定**，且读取侧与生成侧共用同一个 key_of()。上一版就是
     两侧各算各的（读侧 sha1(evidence+task)、写侧 'fb:'+文件名），永不相撞 => 第二次跑会把
     全部 3108 行再加一遍（6218 行）。是 --dry-run 的幂等断言把它拦下的，盘未受害。
  2) 在册名校验：只接受受管根现读的 skill 目录名，其余计数上报不静默（首跑丢弃 74 个不 recogniz 的名字）。
  3) 不覆盖真凭据：真凭据行的键含 'evid:' 前缀、与回填键 'gmfooter:' 形式不同；且 unknown 不得覆盖非 unknown。
  4) 原子写：内存拼全串 -> .tmp -> os.replace（本会话两次崩在非原子写留下 0 字节壳）。
  5) 写前备份 + git 可回滚（红线 7 双前提），由调用方 _temp/r288_apply.py 负责并复验。
'''
import argparse
import glob
import hashlib
import io
import json
import os
import re
import sys

TABLE = 'D:/global_memory/meta/skill_usage.jsonl'
GM = 'D:/global_memory/memory'
SKILLS_ROOT = 'D:/global_skills'
FOOTER = re.compile(r'\[skill清单[^\]]*\][^\n]*')
PAREN = re.compile(r'\(([^)]+)\)')
SESSION = re.compile(r'session=([0-9a-f]{6,64})')
TS = re.compile(r'ts=([0-9T:+.\-]{8,40})')


def registry_names():
    """在册 skill 名：现读受管根目录名（不抄硬编码数字）。"""
    out = set()
    for n in os.listdir(SKILLS_ROOT):
        if os.path.isdir(os.path.join(SKILLS_ROOT, n)) and not n.startswith(('_', '.')):
            out.add(n)
    return out


def key_of(row):
    """唯一的幂等键来源：读写两侧必须都走这里（见 docstring 约束 1）。

    回填行 => 'gmfooter:日件名:skill'，一份日件里同一 skill 天然只有一行；
    真凭据行 => 'evid:sha1(evidence+task)'，与回填键前缀不同，互不覆盖。
    """
    uid = row.get('uid')
    if uid:
        return str(uid)
    ev = str(row.get('evidence', ''))
    try:
        j = json.loads(ev)
    except Exception:
        j = {}
    if j.get('source') == 'GM footer' and j.get('file'):
        return 'gmfooter:' + str(j['file']) + ':' + str(row.get('skill'))
    blob = (ev + '|' + str(row.get('task', ''))).encode('utf-8', 'replace')
    return 'evid:' + hashlib.sha1(blob).hexdigest()[:16]


def parse_footer(text):
    m = FOOTER.search(text)
    if not m:
        return None, None, []
    line = m.group(0)
    names = []
    pm = PAREN.search(line)
    if pm:
        names = [x.strip() for x in pm.group(1).split(',') if x.strip()]
    sm = SESSION.search(text)
    tm = TS.search(text)
    return (sm.group(1) if sm else None), (tm.group(1) if tm else None), names


def load_existing():
    rows = {}
    if not os.path.isfile(TABLE):
        return rows
    for ln in io.open(TABLE, encoding='utf-8').read().splitlines():
        ln = ln.strip()
        if not ln:
            continue
        try:
            j = json.loads(ln)
        except Exception:
            continue
        k = key_of(j)
        prev = rows.get(k)
        # 同键重复时保留带真 outcome 的那条：unknown 不得覆盖 pass/fail/partial
        if prev is not None and prev.get('outcome') != 'unknown':
            continue
        rows[k] = j
    return rows


def build(dry=True):
    reg = registry_names()
    rows = load_existing()
    existing = len(rows)
    files = sorted(glob.glob(os.path.join(GM, '2*.md')))
    footered = dropped = no_session = added = 0
    for f in files:
        t = io.open(f, encoding='utf-8', errors='replace').read()
        sess, ts, names = parse_footer(t)
        if not names:
            continue
        footered += 1
        base = os.path.basename(f)
        if not sess:
            no_session += 1
        for n in names:
            if n not in reg:
                dropped += 1
                continue
            uid = 'gmfooter:' + base + ':' + n
            if uid in rows:
                continue
            rows[uid] = {'schema': 'skill-usage-v1', 'uid': uid,
                         'ts': ts or ('file-date:' + base),
                         'session': sess or ('unkeyed:' + base),
                         'skill': n,
                         'task': 'historical backfill; task text is not in the footer, so left unset',
                         'outcome': 'unknown',
                         'evidence': json.dumps({'source': 'GM footer', 'file': base}, ensure_ascii=False),
                         'evidence_cmd': 'grep -A2 skill清单 D:/global_memory/memory/' + base}
            added += 1
    body = ''.join(json.dumps(v, ensure_ascii=False) + chr(10)
                   for k, v in sorted(rows.items(), key=lambda x: str(x[0])))
    unk = len([v for v in rows.values() if v.get('outcome') == 'unknown'])
    rep = {'schema': 'usage-backfill-v1',
           'provenance_cmd': 'python 05-exec/r288_usage_backfill.py --dry-run --json <件>',
           'registry_names': len(reg), 'gm_dated_files': len(files),
           'files_with_footer_list': footered, 'rows_existing': existing,
           'rows_added': added, 'rows_total': len(rows),
           'dropped_not_in_registry': dropped,
           'footer_files_without_session_key': no_session,
           'skills_covered': len({v.get('skill') for v in rows.values()}),
           'outcome_known_rows': len(rows) - unk,
           'outcome_unknown_share_pct': round(100.0 * unk / max(1, len(rows)), 2),
           'idempotence': 'a second run must report rows_added=0 (key_of is shared by reader/writer)'}
    return rows, body, rep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--json')
    a = ap.parse_args()
    rows, body, rep = build()
    print('[USAGE:BACKFILL] existing=%d added=%d total=%d footered=%d dropped=%d skills=%d unknown=%.1f%%' % (
          rep['rows_existing'], rep['rows_added'], rep['rows_total'], rep['files_with_footer_list'],
          rep['dropped_not_in_registry'], rep['skills_covered'], rep['outcome_unknown_share_pct']))
    if a.dry_run:
        print('[DRY-RUN] not written')
    else:
        tmp = TABLE + '.tmp'
        io.open(tmp, 'w', encoding='utf-8', newline='').write(body)
        os.replace(tmp, TABLE)
        print('[WROTE]', TABLE, os.path.getsize(TABLE), 'bytes')
    if a.json:
        io.open(a.json, 'w', encoding='utf-8', newline='').write(json.dumps(rep, ensure_ascii=False, indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main())
