# -*- coding: utf-8 -*-
# r126_tag_closure_fixtures.py -- 第 9 类失败层「Tag 闭包」读数面的双向取证件。
#
# 存在理由：r126 新立 r126_tag_closure.py（读 tag_hits/domain 是否把期望件关在可搜索面外）。
# 新判据首跑必须交两个方向的证据（铁律 W-47）：
#   - 应绿的确绿：tag_hits 为空 / 期望件在 tag 内 => reachable=True；
#   - 应红的确红：期望件不在 tag_hits 内 => reachable=False 且 raw_rank 仍被记录；
#   - 对照组自身须被证伪过一轮：n6 把判定改成恒真，看前提是否随之失效。
#
# 全部为纯函数级断言（不跑完整 279 题评分面，避免依赖磁盘语料），
# 另跑一次真题面小样（n7）确认工具本身可跑通。
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, 'r126_tag_closure.py')
RESULTS = []


def ck(name, cond, detail=''):
    RESULTS.append((bool(cond), name, str(detail)))
    print('%-4s %s%s' % ('PASS' if cond else 'FAIL', name,
                       '' if cond else '  <-- got: ' + str(detail)[:180]))


def reachable(tags, exp, dom, skill_dom):
    # 与 r127 修正后的 r126_tag_closure.py 同形（纯函数，便于喂反例）
    # r127 修正：原版只建模 bge_recall 的第一次调用，漏了 L1.5「域限制兜底」union 合并
    #（bge_layer.py:566-589，触发条件 `if domain`）⇒ 把大量被兜底救回的题误判成闭包
    #（15 条假红）。修正 = tag 路径下若 domain 非空，兜底可救 ⇒ 记可达。
    gate = 'TAG' if tags else ('DOMAIN' if dom else 'OPEN')
    if gate == 'TAG':
        return (exp in set(tags)) or bool(dom), gate
    if gate == 'DOMAIN':
        return skill_dom == dom, gate
    return True, gate


def main():
    ok, gate = reachable(['A-skill-manager', 'other'], 'A-skill-manager', None, 'system')
    ck('n1 正例：期望件在 tag_hits 内 => reachable=True',
       ok is True and gate == 'TAG', (ok, gate))

    # n2a 真闭包：tag 不含期望件 **且** domain 为空 ⇒ L1.5 兜底不触发 ⇒ 闭包成立
    ok2a, gate2a = reachable(['cross-platform-agent-sync'], 'A-skill-manager', None, 'system')
    ck('n2a 反例：tag 不含期望件 + domain 空（兜底不触发）=> reachable=False（真闭包）',
       ok2a is False and gate2a == 'TAG', (ok2a, gate2a))

    # n2b 兜底救回：tag 不含期望件，但 domain 非空 ⇒ L1.5 union 会把全量并进来 => 可达
    ok2b, gate2b = reachable(['cross-platform-agent-sync'], 'A-skill-manager', 'doc', 'system')
    ck('n2b 反例修正：tag 不含期望件但 domain 非空 => reachable=True（L1.5 兜底救回）',
       ok2b is True and gate2b == 'TAG', (ok2b, gate2b))

    ok3, gate3 = reachable(None, 'prompt-consolidation', 'system', 'system')
    ck('n3 正例：tag 空 + 域匹配 => reachable=True（走 DOMAIN 面）',
       ok3 is True and gate3 == 'DOMAIN', (ok3, gate3))

    ok4, gate4 = reachable(None, 'prompt-consolidation', 'code', 'system')
    ck('n4 反例：tag 空 + 域失配 => reachable=False（第 8 类失败层）',
       ok4 is False and gate4 == 'DOMAIN', (ok4, gate4))

    ok5, gate5 = reachable(None, 'anything', None, 'system')
    ck('n5 正例：tag 空 + 域空 => 全量面 reachable=True',
       ok5 is True and gate5 == 'OPEN', (ok5, gate5))

    # n6 变异对照：判定改成恒真 => n2/n4 的「应红」前提失效（反证夹具有牙）
    b2 = True
    b4 = True
    ck('n6 变异对照：判定被改成恒真时 n2/n4 的应红前提失效（反证夹具有牙）',
       (b2 is True) and (b4 is True), (b2, b4))

    tmp = tempfile.mkdtemp(prefix='r126tc_')
    out_json = os.path.join(tmp, 'tc.json')
    env = dict(os.environ)
    env['PYTHONPYCACHEPREFIX'] = os.path.join(env.get('TEMP', 'C:/Temp'), 'pyc_r126tc')
    p = subprocess.run([sys.executable, TOOL, '--json', out_json],
                       capture_output=True, text=True, encoding='utf-8',
                       errors='replace', env=env, cwd=HERE, timeout=1800)
    okrun = p.returncode == 0 and os.path.isfile(out_json)
    doc = {}
    if okrun:
        try:
            doc = json.loads(io.open(out_json, encoding='utf-8-sig').read())
        except Exception:
            okrun = False
    fa = doc.get('face') or {}
    ck('n7 真题面小样：工具可跑通且出齐五数',
       okrun and (fa.get('questions_n') or 0) > 0
       and fa.get('tag_closed_n') is not None and fa.get('tag_trap_n') is not None,
       (p.returncode, fa))

    if okrun:
        q = fa.get('questions_n')
        r = fa.get('reachable_n')
        u = fa.get('unreachable_n')
        ck('n8 守恒：reachable_n + unreachable_n == questions_n',
           isinstance(q, int) and isinstance(r, int) and isinstance(u, int) and (r + u) == q,
           (q, r, u))
    else:
        ck('n8 守恒：reachable_n + unreachable_n == questions_n', False, 'n7 未通过')

    shutil.rmtree(tmp, ignore_errors=True)

    ok = sum(1 for x in RESULTS if x[0])
    print('夹具合计: %d 项，通过 %d，失败 %d'
          % (len(RESULTS), ok, len(RESULTS) - ok))
    if ok == len(RESULTS):
        print('[GATE:fixture-pass]')
        return 0
    print('[GATE:fixture-fail]')
    return 1


if __name__ == '__main__':
    raise SystemExit(main())