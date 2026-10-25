# -*- coding: utf-8 -*-
'''r221_dead_regex_scan.py - 扫 05-exec 里丢了反斜杠的死正则（r221 新建）。

存在理由（r221 一手）：r201_r2_enable_face.py 的 wrangler 证据解析长期写成一条只含裸
d+ 与 s* 的模式（本应是反斜杠d+ 与反斜杠s*，反斜杠在「用 JS 模板串写 Python」时被吃掉），
于是它**永远匹配不上** —— 产物 wrangler_code 恒为 null，看着像「wrangler 没给码」，实际是
解析器坏了；更糟的是那条被件头称为「客户端侧同码核对」，等于用假证据背书 GAP_SERVICE。
上一轮只修了那一处，同类错误不会只有一处 => 本件按**结构**枚举，不按字面值搜索
（r220 元教训：改同族缺陷要按调用点枚举，不按旧字面值搜）。

⚠ 本文件刻意不含任何反斜杠字面量：需要反斜杠与引号字符处一律 chr() 现拼。理由就是上面
   那条 —— 把带反斜杠的字面量再写一遍，等于把同一个坑再挖一次。

判据（宁漏不误；误报会把人训练成忽略告警）：只看 re.search/match/fullmatch/findall/
finditer/sub/split 之后第一个 r 前缀字面量；其中出现裸 d+ / s* / w+ / S+ / W+ / D+ / b{
（其前不是反斜杠）判嫌疑。变量、拼接、非 r 前缀形态一律跳过（不猜，故不误报）。

三态：PASS（0 命中且自证有牙）/ FAIL（列 file:line:模式）/ UNVERIFIED（分母空或无牙）。
用法: python 05-exec/r221_dead_regex_scan.py [--json 件] [--selftest]
退出码: 0 无命中 / 1 有命中 / 2 面取不到或扫描器无牙（R247 禁按干净记）
'''
import argparse
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BS = chr(92)
DQ = chr(34)
SQ = chr(39)
NL = chr(10)
BARE = ('d+', 's*', 'w+', 'S+', 'W+', 'D+', 'b{')
PREFIXES = ('re.search(', 're.match(', 're.fullmatch(', 're.findall(',
            're.finditer(', 're.sub(', 're.split(')


def raw_first_arg(line):
    '''取 re.*( 之后第一个 r 前缀字面量内容；非该形态返回 None（跳过不猜）。'''
    rest = None
    for pre in PREFIXES:
        k = line.find(pre)
        if k >= 0:
            rest = line[k + len(pre):]
            break
    if not rest:
        return None
    j = 0
    while j < len(rest) and rest[j] in (' ', chr(9)):
        j += 1
    if j + 2 >= len(rest) or rest[j] != 'r':
        return None
    q = rest[j + 1]
    if q not in (DQ, SQ):
        return None
    end = rest.find(q, j + 2)
    if end < 0:
        return None
    return rest[j + 2:end]


def dead_in(pattern):
    '''返回模式里首个裸量词（其前不是反斜杠），否则 None。'''
    if pattern is None:
        return None
    for core in BARE:
        k = 0
        while True:
            j = pattern.find(core, k)
            if j < 0:
                break
            if j == 0 or pattern[j - 1] != BS:
                return core
            k = j + 1
    return None


def wide_scan(exec_dir):
    '''交叉核对口径：不看是否 re 调用，扫文件里**所有** r 前缀字面量。

    为什么要它：窄口径（只看 re.*( 首参）可能恰好放过同类问题，用「扫过且 0 命中」
    自我背书 —— 本件报 0 处时，宽口径给的是独立第二读数（r221 实测宽口径多报 1 处）。
    朴素取字面量（不处理转义），够用且不会因判据复杂而漏。
    '''
    lits = 0
    hits = []
    files = 0
    for f in sorted(os.listdir(exec_dir)):
        if not f.endswith('.py'):
            continue
        try:
            s = io.open(os.path.join(exec_dir, f), encoding='utf-8',
                        errors='replace').read()
        except OSError:
            continue
        files += 1
        i = 0
        while True:
            i = s.find('r', i)
            if i < 0:
                break
            q = s[i + 1:i + 2]
            if q in (DQ, SQ) and (i == 0 or not (s[i - 1].isalnum() or s[i - 1] in ('_', '.'))):
                j = s.find(q, i + 2)
                if j > i + 1:
                    pat = s[i + 2:j]
                    lits += 1
                    core = dead_in(pat)
                    if core:
                        hits.append({'file': f,
                                     'line': s[:i].count(NL) + 1,
                                     'token': core, 'pattern': pat[:90]})
                    i = j + 1
                    continue
            i += 1
    return hits, lits, files


def scan(exec_dir):
    hits = []
    files = 0
    for f in sorted(os.listdir(exec_dir)):
        if not f.endswith('.py'):
            continue
        try:
            s = io.open(os.path.join(exec_dir, f), encoding='utf-8',
                        errors='replace').read()
        except OSError:
            continue
        files += 1
        for i, line in enumerate(s.split(NL), 1):
            if 're.' not in line:
                continue
            pat = raw_first_arg(line)
            core = dead_in(pat)
            if core:
                hits.append({'file': f, 'line': i, 'token': core,
                             'pattern': pat[:90], 'text': line.strip()[:150]})
    return hits, files


def selftest():
    '''双向自证：已知死正则必须被抓、好正则不得误报、本轮修好的 r201 必须干净。

    扫描器没牙比没扫更危险 —— 它会把「扫过且 0 命中」当结论背书（本会话已栽过多次）。
    样本一律用 chr() 拼，避免本文件出现反斜杠（见件头那条自约束）。
    '''
    # 样本必须复刻历史真实形态：外层单引号（内含双引号），否则 r"code" 后跟裸文本
    # 根本不是 r 字面量，raw_first_arg 正确跳过 => 自证会假阴（r221 实测首跑就假阴）。
    bad = 'm = re.search(r' + SQ + DQ + 'code' + DQ + 's*:s*(d+)' + SQ + ', x)'
    good = ('mm = re.search(r' + DQ + BS + '[code:' + BS + 's*(' + BS + 'd+)'
            + BS + ']' + DQ + ', x)')
    ok_bad = dead_in(raw_first_arg(bad)) is not None
    ok_good = dead_in(raw_first_arg(good)) is None
    fixed_clean = True
    real = os.path.join(HERE, 'r201_r2_enable_face.py')
    if os.path.isfile(real):
        s = io.open(real, encoding='utf-8', errors='replace').read()
        for line in s.split(NL):
            if 're.' in line and dead_in(raw_first_arg(line)):
                fixed_clean = False
    print('[DEADRX:SELFTEST] 死正则被抓=%s 好正则不误报=%s 已修件干净=%s' % (
        ok_bad, ok_good, fixed_clean))
    return ok_bad and ok_good and fixed_clean


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', dest='out', default='')
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--wide', action='store_true',
                    help='交叉核对口径：扫全部 r 字面量（不看是否 re 调用）')
    args = ap.parse_args(argv)
    if args.selftest:
        return 0 if selftest() else 2
    if args.wide:
        wh, lits, wf = wide_scan(HERE)
        if wf == 0 or not selftest():
            print('[DEADRX:UNVERIFIED] 宽口径分母空或扫描器无牙')
            return 2
        print('[DEADRX:WIDE] 扫 %d 件 / r 字面量 %d 个 / 裸量词嫌疑 %d 处' % (
            wf, lits, len(wh)))
        for h in wh[:10]:
            print('  %s:%d 裸%s | %s' % (h['file'], h['line'], h['token'],
                                         h['pattern'][:66]))
        return 1 if wh else 0
    hits, files = scan(HERE)
    if files == 0:
        print('[DEADRX:UNVERIFIED] 05-exec 扫到 0 件 = 分母空面，不得判干净')
        return 2
    if not selftest():
        print('[DEADRX:SELFTEST-FAIL] 扫描器无牙，其 0 命中读数不计')
        return 2
    wh, lits, wf = wide_scan(HERE)
    doc = {'schema': 'dead-regex-scan-v2', 'files_scanned': files,
           'provenance_cmd': 'python 05-exec/r221_dead_regex_scan.py --json 件',
           'wide_files': wf, 'wide_literals': lits, 'wide_suspects': wh,
           'hits': hits}
    if args.out:
        op = args.out if os.path.isabs(args.out) else os.path.join(ROOT, args.out)
        io.open(op, 'w', encoding='utf-8', newline=NL).write(
            json.dumps(doc, ensure_ascii=False, indent=1))
    print('[DEADRX] 扫 %d 件 / 死正则嫌疑 %d 处' % (files, len(hits)))
    print('[DEADRX:WIDE-ADVISORY] 交叉核对口径扫 %d 件 / r 字面量 %d 个 / 嫌疑 %d 处'
          '（advisory 不计红；每处需人工定性后再决定是否入红）' % (wf, lits, len(wh)))
    for h in hits[:12]:
        print('  %s:%d 裸%s 模式=%s' % (h['file'], h['line'], h['token'],
                                        h['pattern'][:70]))
    if hits:
        print('[DEADRX:FAIL] 有丢反斜杠的正则：写了等于没写，产物会静默恒 null')
        return 1
    print('[DEADRX:PASS] 无死正则（自证：死正则样本被抓、好正则不误报）')
    return 0


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
    sys.exit(main())
