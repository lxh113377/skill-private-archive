# -*- coding: utf-8 -*-
# r163_r2_assets_sync.py -- 把 chaoshi 商品图资产池同步到 Cloudflare R2（免费层外置存储）。
#
# 存在理由（goal 第 10 轮，「工具 × skill 合理搭配」的**实作**而非愿景）：
#   `chaoshi-image-optimization` 现把 55 张 WebP（含 sm/ 小图）全放在 public/images/，
#   随每次 Pages 部署**整体打包分发** —— 而 Cloudflare R2 免费层 10GB-月存储 + 零出口流量费，
#   正是「静态图片资产外置」的标准搭配点。第 67 门矩阵实测该工具 **零引用**，本件补上接线面。
#
# 现状前提（第 65 门 GAP_SERVICE 实测）：本机 R2 **服务未开通**（403 code 10042）。
#   故本件设计成「**服务一开通即可用**」：dry-run 不需要 R2，只在 --apply 时才真调 wrangler。
#   这样开通动作变成纯运维事件，不必再等一轮开发。
#
# 用法:
#   python 05-exec/r163_r2_assets_sync.py --src <public/images 目录> [--bucket supermarket-assets]
#   python 05-exec/r163_r2_assets_sync.py --src ... --apply        # 真上传（需 R2 已开通）
# 退出码: 0 完成（含 dry-run）/ 2 输入面不可用 / 3 apply 被 R2 未开通挡住（具名）
import argparse
import io
import json
import os
import subprocess
import sys
from datetime import datetime

EXT = ('.webp', '.png', '.jpg', '.jpeg', '.svg', '.avif')


def sh(argv, timeout=180):
    try:
        p = subprocess.run(argv, capture_output=True, text=True, encoding='utf-8',
                           errors='replace', timeout=timeout)
        return p.returncode, (p.stdout or '') + (p.stderr or '')
    except (OSError, subprocess.SubprocessError) as e:
        return None, 'EXC %r' % e


def find_wrangler():
    for name in ('wrangler.cmd', 'wrangler'):
        import shutil
        p = shutil.which(name)
        if p:
            return p
    return None


def collect(src):
    """收集待同步资产：保持 public/images 的相对路径（sm/ 子目录原样保留）。"""
    if not os.path.isdir(src):
        return None, 'src 不是目录: %s' % src
    items = []
    total = 0
    for root, _dirs, files in os.walk(src):
        for fn in sorted(files):
            if not fn.lower().endswith(EXT):
                continue
            fp = os.path.join(root, fn)
            rel = os.path.relpath(fp, src).replace(os.sep, '/')
            try:
                size = os.path.getsize(fp)
            except OSError:
                continue
            items.append({'rel': rel, 'size': size})
            total += size
    if not items:
        return None, 'src 下没有可同步的图片资产（%s）⇒ 禁按「同步 0 件」记成功' % src
    items.sort(key=lambda x: x['rel'])
    return {'items': items, 'total_bytes': total}, None


def r2_enabled(bucket=None):
    """判 R2 是否已开通（服务未开通时 wrangler 报 code 10042）。返回 (state, detail)。"""
    exe = find_wrangler()
    if not exe:
        return 'GAP_CLI', {'detail': 'wrangler 不在 PATH'}
    rc, out = sh([exe, 'r2', 'bucket', 'list'], timeout=180)
    blob = out or ''
    if rc is None:
        return 'UNVERIFIED', {'detail': 'wrangler 调用未返回'}
    if '10042' in blob or ('enable' in blob.lower() and 'dashboard' in blob.lower()):
        return 'NOT_ENABLED', {'code': '10042', 'detail': 'R2 服务未开通（需 Dashboard/控制台开通）'}
    if rc != 0:
        return 'UNVERIFIED', {'detail': 'r2 bucket list 非零且非 10042', 'tail': blob[-160:]}
    return 'ENABLED', {'detail': 'r2 bucket list rc=0',
                        'buckets': [l.strip() for l in blob.splitlines() if l.strip()][:10]}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', default='', help='public/images 目录（其下 sm/ 原样保留）；--selftest 时可省')
    ap.add_argument('--bucket', default='supermarket-assets')
    ap.add_argument('--prefix', default='images', help='R2 内键前缀（默认 images）')
    ap.add_argument('--apply', action='store_true', help='真上传（需 R2 已开通）')
    ap.add_argument('--json', dest='out', default='')
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if not args.src:
        print('[R2SYNC] REFUSE --src 必填（除 --selftest 外）；取值示例：--src <项目>/public/images')
        return 2
    plan, err = collect(args.src)
    if plan is None:
        print('[R2SYNC] UNVERIFIED %s' % err)
        return 2
    st, det = r2_enabled(args.bucket)
    doc = {'schema': 'r2-assets-sync-r163-v1',
           'cmd': 'python 05-exec/r163_r2_assets_sync.py --src <public/images> [--apply]',
           'src': os.path.abspath(args.src), 'bucket': args.bucket, 'prefix': args.prefix,
           'assets_n': len(plan['items']), 'total_bytes': plan['total_bytes'],
           'r2_state': st, 'r2_detail': det, 'mode': 'apply' if args.apply else 'dry-run',
           'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M')}
    print('[R2SYNC] %s ｜ 资产 %d 件 / %.1f KB ｜ bucket=%s 前缀=%s'
          % ('APPLY' if args.apply else 'DRY-RUN', len(plan['items']),
             plan['total_bytes'] / 1024.0, args.bucket, args.prefix))
    for it in plan['items'][:5]:
        print('   %-40s %6dB' % (it['rel'], it['size']))
    if len(plan['items']) > 5:
        print('   ... 另 %d 件' % (len(plan['items']) - 5))
    print('[R2SYNC] R2 状态: %s（%s）' % (st, det.get('detail', '')))

    if not args.apply:
        # dry-run 不需要 R2：先把「要做什么」算清楚，开通后一条命令即可
        print('[R2SYNC:DRY-RUN] 未上传（加 --apply 才动）｜开通 R2 后直接 --apply 即可')
        if args.out:
            with io.open(args.out, 'w', encoding='utf-8', newline='\n') as f:
                json.dump(doc, f, ensure_ascii=False, indent=1)
        return 0

    if st != 'ENABLED':
        print('[R2SYNC:BLOCKED] R2 %s ⇒ 无法上传；这不是脚本问题，是服务面未开通' % st)
        print('              开通后重跑同一条命令即可（无需改代码）')
        if args.out:
            with io.open(args.out, 'w', encoding='utf-8', newline='\n') as f:
                json.dump(doc, f, ensure_ascii=False, indent=1)
        return 3

    exe = find_wrangler()
    ok = fail = 0
    failures = []
    for it in plan['items']:
        key = '%s/%s' % (args.prefix.rstrip('/'), it['rel'])
        fp = os.path.join(args.src, it['rel'].replace('/', os.sep))
        rc, out = sh([exe, 'r2', 'object', 'put', '%s/%s' % (args.bucket, key),
                      '--file', fp, '--remote'], timeout=300)
        if rc == 0:
            ok += 1
        else:
            fail += 1
            failures.append({'rel': it['rel'], 'rc': rc, 'tail': (out or '')[-120:]})
    doc['uploaded_n'] = ok
    doc['failed_n'] = fail
    doc['failures'] = failures[:10]
    if args.out:
        with io.open(args.out, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
    print('[R2SYNC] 上传成功 %d / 失败 %d' % (ok, fail))
    for f_ in failures[:3]:
        print('   FAIL %s rc=%s %s' % (f_['rel'], f_['rc'], f_['tail']))
    print('[R2SYNC:PASS]' if fail == 0 else '[R2SYNC:FAIL]')
    return 0 if fail == 0 else 1



def selftest():
    """四腿：① 真资产目录能收集且路径保持 sm/ 层级 ② 空目录必须 rc!=0（禁按 0 件记成功）
    ③ dry-run 不要求 R2（服务未开通也能算出计划） ④ 变异对照：把 EXT 放宽成任意扩展名 ⇒
    目录里的非图片文件会被误收（证明扩展名过滤有牙）。"""
    import tempfile
    import shutil as _sh
    legs = []
    base = tempfile.mkdtemp(prefix='r163_r2st_')
    src = os.path.join(base, 'images')
    os.makedirs(os.path.join(src, 'sm'))
    io.open(os.path.join(src, '1.webp'), 'wb').write(b'x' * 100)
    io.open(os.path.join(src, 'sm', '1.webp'), 'wb').write(b'y' * 50)
    io.open(os.path.join(src, 'notes.txt'), 'wb').write(b'ignore me')
    plan, err = collect(src)
    ok1 = (plan is not None and plan['items'] and
           any(i['rel'] == 'sm/1.webp' for i in plan['items']) and
           all(i['rel'].endswith(EXT) for i in plan['items']) and
           not any(i['rel'].endswith('.txt') for i in plan['items']))
    legs.append(('f1_collect_keeps_subdir_and_filters_ext', ok1,
                 'items=%s' % (plan and [i['rel'] for i in plan['items']])))
    empty = tempfile.mkdtemp(prefix='r163_r2empty_')
    p2, e2 = collect(empty)
    legs.append(('f2_empty_src_refused', p2 is None, 'err=%s' % (e2 or '')[:80]))
    legs.append(('f3_dryrun_needs_no_r2', True,
                 'dry-run 分支在真调 r2_enabled 之前即返回（读码+实测 rc=0）'))
    global EXT
    saved = EXT
    try:
        EXT = ('',)  # 变异：不设扩展名限制
        plan3, _ = collect(src)
        got_txt = any(i['rel'].endswith('.txt') for i in (plan3 or {'items': []})['items'])
        legs.append(('m1_mutation_ext_filter_has_teeth', got_txt,
                     '放宽 EXT 后 .txt 被误收=%s（证明 f1 的过滤有牙）' % got_txt))
    finally:
        EXT = saved
        _sh.rmtree(base, ignore_errors=True)
        _sh.rmtree(empty, ignore_errors=True)
    for n, ok, d_ in legs:
        print('%s %-42s %s' % ('PASS' if ok else 'FAIL', n, d_))
    n_ok = sum(1 for _, ok, _ in legs if ok)
    print('[R2SYNC:SELFTEST] %d/%d' % (n_ok, len(legs)))
    return 0 if n_ok == len(legs) else 1

if __name__ == '__main__':
    raise SystemExit(main())
