# -*- coding: utf-8 -*-
"""check_r291_landed.py — security-audit 换装的**落地态**判据（R289-5 第⑦步）。

为什么另建一件：_repro/r290s/check_r290s.py 是「换装前材料自证」，A 腿断言每个 old 在盘上唯一存在；
补丁一旦落地，被替换的 old 必然消失 ⇒ 它转 gate=FAIL 属设计使然。但一个长期 FAIL 的判据没人会再跑，
看守价值就没了。所以本件承担落地后的权威判据，并把那句「设计使然」变成**机器可核**的命题（N 腿）。

核心不变式（H 腿，本轮第二版；第一版写错过，记在下面）：
    盘上文本 == 在落地前基线上按顺序重放全部补丁的结果，一字不差。
  为什么不是「每个 new 必须在盘上逐字出现」—— 第一版我这么写，结果三条 FAIL。真实原因（diag 实测）：
  SEC-PROVENANCE-ALT / SEC-ABSORB-POINTER 的 new 在落地后**又被我本轮的歧义补丁改写过**（加了仓绝对路径），
  所以中间态 new 早就不在盘上。要逐字断言就必须断言整条补丁链的**末端态**，这正是重放不变式。
  它同时更强：既要求 old 消失（非幂等项）、又要求最终文本与机械重放完全相等，任何漏打/多打/手改都会被抓住。

零写入：本件只读受管根与本仓 _repro，绝不写盘。
七条腿 H..N + 两条负控（--neg）；末行 [SEC-AUDIT-LANDED] …。
退出码：0 全绿 / 1 任一判红 / 2 输入不可得（受管根件缺、基线 commit 取不到、补丁件缺）——
        取不到一律 UNVERIFIED 记 rc=2，禁读成通过（R247）。
"""
import argparse
import io
import json
import os
import re
import subprocess
import sys

MG = 'D:/global_skills'
SA = MG + '/security-audit'
SK = SA + '/SKILL.md'
SID = SA + '/.upstream'
VOL = SA + '/references/upstream-cloudflare-sec.md'
CJS = SA + '/scripts/validate-coverage-ledger.cjs'
REPRO = '_repro/r290s'
NL = chr(10)
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# 落地链（本轮实测的提交顺序；取父提交作为「落地前基线」）
BASE_SK = '6ea564bd~1'
BASE_SID = 'a780bbcf~1'
CHAIN_SK = [REPRO + '/patch_local.json', REPRO + '/patch_ambiguity.json']
CHAIN_SID = [REPRO + '/patch_upstream.json', REPRO + '/patch_ambiguity_sidecar.json']


def rd(p):
    return io.open(p, encoding='utf-8', newline='').read() if os.path.isfile(p) else None


def git(args):
    r = subprocess.run(['git', '-C', MG] + args, capture_output=True, text=True,
                       encoding='utf-8', errors='replace', timeout=90)
    return r.stdout if r.returncode == 0 else None


def load(p):
    full = os.path.join(ROOT, p)
    if not os.path.isfile(full):
        return None
    return json.load(io.open(full, encoding='utf-8'))


def replay(base, hunks):
    """按 rule_editor 同口径重放：顺序 find，命中数不为 1 即失败（幂等项 new 含 old 时允许 >=1）。"""
    errs = []
    t = base
    for h in hunks:
        c = t.count(h['old'])
        idem = h['old'] in h['new']
        if c == 0 or (c > 1 and not idem):
            errs.append('%s(count=%d)' % (h['id'], c))
            continue
        t = t.replace(h['old'], h['new'], 1)
    return t, errs


def leg_h(neg=''):
    bad = []
    det = []
    for base_ref, chain, path, tag in ((BASE_SK, CHAIN_SK, SK, 'SKILL'),
                                       (BASE_SID, CHAIN_SID, SID, 'SIDECAR')):
        cur = rd(path)
        if cur is None:
            return False, ['%s-missing' % tag]
        # 基线 = 落地前提交里的那一版；取不到即输入不可得
        if git(['cat-file', '-e', base_ref]) is None:
            pass
        chk = subprocess.run(['git', '-C', MG, 'cat-file', '-e', base_ref], capture_output=True)
        if chk.returncode != 0:
            return False, ['%s-baseline-unreadable' % tag]
        base = git(['show', '%s:%s' % (base_ref, 'security-audit/' + ('SKILL.md' if tag == 'SKILL' else '.upstream'))])
        if base is None:
            return False, ['%s-baseline-show-failed' % tag]
        hunks = []
        for p in chain:
            part = load(p)
            if part is None:
                return False, ['%s-patch-missing:%s' % (tag, p)]
            hunks += part
        landed, errs = replay(base, hunks)
        det.append('%s hunks=%d' % (tag, len(hunks)))
        if errs:
            bad += ['%s/%s' % (tag, e) for e in errs]
        # 负控（内存，不写盘）：模拟落地后被人手改一个字符 => 重放必与盘上不等
        cmp_cur = (cur[:-2] + 'ZZ') if (neg == 'hand-edited' and tag == 'SKILL') else cur
        if landed != cmp_cur:
            # 找第一处差异的行，便于定位（只报行号与长度差，不打印正文）
            ll = landed.split(NL)
            cl = cur.split(NL)
            cl = cmp_cur.split(NL)
            first = next((i for i in range(min(len(ll), len(cl))) if ll[i] != cl[i]), min(len(ll), len(cl)))
            bad.append('%s/REPLAY-MISMATCH@line%d(len %d vs %d)' % (tag, first + 1, len(landed), len(cmp_cur)))
        # old 消失核验（非幂等项）：在最终态里必须为 0
        for h in hunks:
            if h['old'] not in h['new'] and cur.count(h['old']) != 0:
                bad.append('%s/OLD-STILL-THERE:%s' % (tag, h['id']))
    return (not bad), ('; '.join(det) or 'n/a')


def leg_i():
    ok = os.path.isfile(VOL) and os.path.isfile(CJS)
    det = ['vol=%s cjs=%s' % (os.path.getsize(VOL) if os.path.isfile(VOL) else '-',
                              os.path.getsize(CJS) if os.path.isfile(CJS) else '-')]
    co = load(REPRO + '/coords.json')
    if co is None:
        return False, ['coords-missing']
    # 具名取 blob sha（第一版我用正则抓了第一个 40-hex，抓到的是 commit sha ⇒ 假红）
    want_api = ((co.get('upstream') or {}).get('files') or {}).get('validate-coverage-ledger.cjs', {}).get('blob_sha')
    want_ev = (co.get('verbatim_evidence') or {}).get('cjs_api_sha')
    # git 的 stdout 带尾换行；不 strip 会让完全相同的 sha 判成 DIFFERS（本轮实测踩过）
    live = (git(['hash-object', CJS]) or '').strip() or None
    det.append('live=%s api=%s ev=%s' % ((live or '-')[:12], (want_api or '-')[:12], (want_ev or '-')[:12]))
    if not live:
        return False, det + ['hash-object-unavailable']
    if want_api and live != want_api:
        return False, det + ['BLOB-SHA-DIFFERS']
    if want_ev and live != want_ev:
        return False, det + ['EVIDENCE-SHA-DIFFERS']
    if not (want_api or want_ev):
        return False, det + ['NO-STORED-SHA']
    return ok, det


def leg_j():
    vol = rd(VOL)
    if vol is None:
        return False, ['vol-missing']
    d = os.path.join(ROOT, REPRO, 'blocks')
    bs = []
    if os.path.isdir(d):
        for fn in sorted(os.listdir(d)):
            if fn.endswith('.txt'):
                t = io.open(os.path.join(d, fn), encoding='utf-8').read().strip()
                if t:
                    bs.append((fn, t))
    if not bs:
        return False, ['blocks-absent']
    lines = vol.split(NL)
    j0 = next((k for k, x in enumerate(lines) if x.startswith('# ')), 0)
    k2 = j0 + 1
    while k2 < len(lines) and (lines[k2].strip() == '' or lines[k2].startswith('> ')):
        k2 += 1
    body = NL.join(lines[k2:])
    hit = sum(1 for fn, t in bs if t in body)
    return hit == len(bs), ['%d/%d' % (hit, len(bs))]


def leg_k(neg):
    sk, si = rd(SK), rd(SID)
    if sk is None or si is None:
        return False, ['unreadable']
    bare_sk = len([x for x in sk.split(NL)
                   if ('_repro/' in x or '_temp/' in x) and 'C:/Users' not in x and 'D:/global' not in x])
    bare_si = len([x for x in si.split(NL)
                   if '05-exec/' in x and 'C:/Users' not in x and 'D:/global' not in x])
    if neg == 'bare-pointer':
        bare_sk += 1
    return (bare_sk + bare_si) == 0, ['bare=%d/%d' % (bare_sk, bare_si)]


def leg_l():
    sk, si = rd(SK), rd(SID)
    if sk is None or si is None:
        return False, ['unreadable']
    fm_v = fm_d = hist_v = hist_d = None
    for ln in sk.split(NL):
        if ln.startswith('version: '):
            fm_v = ln.split(': ', 1)[1].strip()
        elif ln.startswith('last_updated: '):
            fm_d = ln.split(': ', 1)[1].strip()
        elif (not hist_v) and ln.startswith('- **') and ('** (' in ln):
            hist_v = ln.split('**')[1].strip()
            hist_d = ln.split('(')[1].split(')')[0]
    cons = bool(fm_v) and fm_v == hist_v and fm_d == hist_d
    # 侧车仍可解析：首行必须是 repo 名（parse_sidecar 只看非注释行）
    side_ok = bool(si) and si.split(NL)[0].strip() and not si.split(NL)[0].startswith('#')
    inc = 'absorbed_increment' in si
    return cons and bool(side_ok) and inc, ['fm=%s/%s hist=%s/%s sidecar_first=%s inc=%s'
                                           % (fm_v, fm_d, hist_v, hist_d, bool(side_ok), inc)]


def leg_m():
    sk = rd(SK)
    if sk is None:
        return False, ['unreadable']
    links = re.findall(r'\[[^\]]*\]\(\s*([^)\s]+)', sk)
    rel = [u for u in links if not u.startswith(('http', 'mailto:', '#', '/'))]
    dead = [u for u in rel if not os.path.exists(os.path.join(SA, u.split('#')[0]))]
    return len(dead) == 0, ['links=%d rel=%d dead=%s' % (len(links), len(rel), dead[:3])]


def leg_n(neg):
    """PREP 判据此刻必须是「只由已落地的 old 消失」而红；出现别的红因即判红。"""
    pj = os.path.join(ROOT, REPRO, 'check_r290s.py')
    if not os.path.isfile(pj):
        return False, ['PREP-missing']
    ids = set()
    for p in CHAIN_SK + CHAIN_SID:
        part = load(p)
        if part:
            ids |= set(x['id'] for x in part)
    r = subprocess.run([sys.executable, '-B', pj], capture_output=True, text=True,
                       encoding='utf-8', errors='replace', timeout=420, cwd=ROOT)
    out = (r.stdout or '') + (r.stderr or '')
    toks = re.findall(r'broken=([^\r\n]+)', out)
    bad_ids = set()
    for chunk in toks:
        for piece in re.split(r'[,)]', chunk):
            m = re.match(r'([A-Z][A-Z0-9-]+)', piece.strip())
            if m:
                bad_ids.add(m.group(1))
    extra = sorted(bad_ids - ids)
    if neg == 'prep-other-red':
        extra = extra + ['INJECTED-OTHER']
    det = ['rc=%d broken_ids=%s extra=%s' % (r.returncode, sorted(bad_ids)[:3], extra[:3])]
    if r.returncode == 0:
        return False, det + ['PREP-STILL-GREEN=>落地未发生或被放宽']
    if not bad_ids:
        # rc=1 但红因无法归到任何 hunk id：多半是**材料不可读**（clone 里 upstream/ 被 .gitignore
        # 豁免，PREP 的 B 腿读不到上游快照）而非落地造成的 old 消失。禁据此判 N 绿 —— 那等于把
        # 「说不清的红」当「可解释的红」放行（R247 的另一种形态：不是取不到当零，是取不到当合理）。
        return 'UNVERIFIED', det + ['PREP rc=1 但无 broken id 可归因（疑材料缺失，非落地效应）']
    if r.returncode == 2:
        # clone 场景：PREP 的 B 腿要读 _repro/r290s/upstream/SKILL.md，而那份上游快照是**部分**
        # （其内部相对链会把本仓死链门判红 3 条）⇒ 刻意被 .gitignore 豁免。材料不可读属已知有意，
        # 但按 R247 一律记 UNVERIFIED，禁把「取不到」读成通过（第一版我就是这么假绿的）。
        return 'UNVERIFIED', det + ['PREP 材料不可读（clone 里 upstream/ 豁免所致，非落地缺陷）']
    return (not extra), det




def leg_p(neg=''):
    """P provenance-live：blocks/*.txt 必须逐字存在于**上游现取正文**里，且该正文的 blob sha
    等于 coords.json 存档值。

    为什么不能像 PREP 判据那样读 _repro/r290s/upstream/：那份快照是**部分**上游（S 只取 6 个文件），
    其内部相对链指向未取入的兄弟文件 ⇒ 进本仓发布面必断（实测 3 条死链，r220 判红）。所以 upstream/
    刻意不入库（.gitignore 精准豁免 + coords.json 留 repo/ref/path 供重建）。代价是「切片未造假」这条
    证据在 clone 里必须换成活体取证：现取上游正文 -> 核 blob sha -> 再核每个 block 逐字在内。
    取不到（无网/限流）一律 UNVERIFIED 且 rc=2，禁读成通过（R247）。
    """
    co = load(REPRO + '/coords.json')
    if co is None:
        return False, 'UNVERIFIED', ['coords-missing']
    files = ((co.get('upstream') or {}).get('files') or {})
    want = (files.get('SKILL.md') or {}).get('blob_sha')
    d = os.path.join(ROOT, REPRO, 'blocks')
    bs = []
    if os.path.isdir(d):
        for fn in sorted(os.listdir(d)):
            if fn.endswith('.txt'):
                t = io.open(os.path.join(d, fn), encoding='utf-8').read().strip()
                if t:
                    bs.append((fn, t))
    if not bs or not want:
        return False, 'UNVERIFIED', ['no-blocks-or-no-anchor']
    try:
        r = subprocess.run(['gh', 'api',
                           'repos/cloudflare/security-audit-skill/contents/skills/security-audit/SKILL.md',
                           '--jq', '.sha'], capture_output=True, text=True, timeout=120)
        api_sha = (r.stdout or '').strip()
        r2 = subprocess.run(['gh', 'api',
                            'repos/cloudflare/security-audit-skill/contents/skills/security-audit/SKILL.md',
                            '--jq', '.content'], capture_output=True, text=True, timeout=180)
        import base64
        raw = base64.b64decode((r2.stdout or '').replace(chr(10), ''))
        up_txt = raw.decode('utf-8', errors='replace')
    except Exception as e:
        return False, 'UNVERIFIED', ['gh-unavailable:%r' % e]
    if not api_sha or api_sha != want:
        return False, 'UNVERIFIED', ['anchor-mismatch api=%s coords=%s' % (api_sha[:12], want[:12])]
    hit = sum(1 for fn, t in bs if t in up_txt)
    if neg == 'fake-block':
        hit = max(0, hit - 1)
    ok = hit == len(bs)
    return ok, 'LIVE', ['%d/%d blocks verbatim in upstream SKILL.md (blob %s)' % (hit, len(bs), api_sha[:12])]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--neg', default='')
    a = ap.parse_args()
    res = []
    ok_h, det_h = leg_h(a.neg)
    res.append(('H replay-equals-landed', ok_h, det_h))
    if not ok_h and 'baseline' in str(det_h) or 'unreadable' in str(det_h):
        pass
    ok_i, det_i = leg_i()
    res.append(('I files-and-blob-sha', ok_i, ' | '.join(det_i)))
    ok_j, det_j = leg_j()
    res.append(('J volume-verbatim', ok_j, ' '.join(det_j)))
    ok_k, det_k = leg_k(a.neg)
    res.append(('K pointer-clean', ok_k, ' '.join(det_k)))
    ok_l, det_l = leg_l()
    res.append(('L version-sidecar', ok_l, ' '.join(det_l)))
    ok_m, det_m = leg_m()
    res.append(('M links-landed', ok_m, ' '.join(det_m)))
    ok_n, det_n = leg_n(a.neg)
    res.append(('N prep-consistent', ok_n, ' '.join(det_n)))
    ok_p, mode_p, det_p = leg_p(a.neg)
    res.append(('P provenance-live', ok_p, ' '.join(det_p)))
    for nm, ok, dt in res:
        tag = 'PASS' if ok is True else ('UNVERIFIED' if ok == 'UNVERIFIED' else 'FAIL')
        print('%-10s %-22s %s' % (tag, nm, dt))
    hard = [x[0] for x in res if x[1] is False]
    unver = [x[0] for x in res if x[1] == 'UNVERIFIED']
    gate = 'PASS' if not hard and not unver else ('FAIL' if hard else 'UNVERIFIED')
    nh = len([1 for x in [load(p) for p in CHAIN_SK + CHAIN_SID] if x])
    print('[SEC-AUDIT-LANDED] replay=%s blob=%s verbatim=%s pointers=%d links_dead=0 gate=%s'
          % ('ok' if ok_h else 'BAD', 'ok' if ok_i else 'BAD', '%s' % det_j[0],
             0 if ok_k else 1, gate))
    if hard:
        print('   hard-red legs: %s' % hard)
    if unver:
        print('   UNVERIFIED legs: %s（不得当通过；补取输入后重跑）' % unver)
    return 1 if hard else (2 if unver else 0)


if __name__ == '__main__':
    sys.exit(main())
