# r312 debug：Y3/X3 log 提及段名的每一行 + SKIPCTX/INCLAIM 匹配（判 fake 是豁免 bug 还是真失真）。
import io, re
SK = re.compile(r"(跳过|未使用|未用|没写|不新增|省去|未硬套|无真实示例|避免双写|重合|不适用|确无该段|不可见|改由|功能不丢|合并为一套|不自欺)")
IN = re.compile(r"(新增|均落|落在|位于|写了|包含|使用)")
for arm in ('Y3', 'X3'):
    g = io.open('_temp/r312a/out_%s/process_log.md' % arm, encoding='utf-8').read()
    p = io.open('_temp/r312a/out_%s/optimized_prompt.md' % arm, encoding='utf-8').read()
    tags = sorted(set(re.findall(r'<([a-z][a-z_]{2,19})>', g)))
    fake = []
    for tag in tags:
        if ('<' + tag + '>') in p:
            continue
        rows = [r for r in g.split(chr(10)) if ('<' + tag + '>') in r]
        exempt = rows and all(SK.search(r) and not IN.search(r) for r in rows)
        if not exempt:
            fake.append(tag)
        print('  [%s] <%-16s> prompt含=%s 提及=%d 豁免=%s' % (arm, tag, ('<' + tag + '>') in p, len(rows), exempt))
        if not exempt:
            for r in rows[:2]:
                print('       行: SK=%s IN=%s | %s' % (bool(SK.search(r)), bool(IN.search(r)), r.strip()[:110]))
    print('== %s fake=%s' % (arm, fake))
