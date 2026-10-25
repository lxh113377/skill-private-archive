# -*- coding: utf-8 -*-
'''r215_free_tool_roster.py - 免费工具 x 工作流 x skill 搭配名册（生成器，r215）。

为什么需要它：目标要的是把免费工具与工作流、相关 skill 合理搭配。五道门各量一个切面
（163 能不能跑 / 93 有没有 skill 承载 / 92 入口会不会派到写着答案的卷 / 88 召回 / 86 指针），
但没有任何产物把三者按工具拼在一起 —— 于是『某个工具搭到哪一步、还差什么、凭什么说差』只能
靠我在对话里临时回忆。本件把那份回忆变成可复算产物，且全部数字取自源证据件：缺任一源件即 rc=2
不出册（r214 我刚因按印象写分母产出过一条假发现，故此处禁手抄、禁按记忆补，R247）。
'''
import argparse
import glob
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
B = os.path.join(ROOT, '06-benchmark')
sys.path.insert(0, HERE)
import r214_tool_carrier_face as TF
import r215_claim_check as CC
import r215_gate_check as GC

SRC = {
    'roster': 'free_tools_latest.json',
    'patterns': 'tool_carrier_patterns.json',
    # 两把尺的权威源 = 第 67 门产物（per_tool 提到 / per_tool_exec 代码真调用）。
    # r216 自抓：我 r214 造的 tool_skill_matrix_probe 是它的弱化重造（只有「提到」一尺），
    # 故本件不再读自己那份 probe —— 避免第二真相源；按 glob 取最新且含 per_tool_exec 的 67 产物。
    'matrix*': 'tool_skill_matrix_r*.json',
    'truth': 'route_truth_latest.json',
    'ingress': 'ingress_latest.json',
    'recall': 'recall_latest.json',
    'carrier': 'tool_carrier_latest.json',
    # r227：第三层与第二把工作流尺。名册此前只有「skill 目录」一层，而目标的搭配是三层：
    #   ① skill 目录两把尺（第 67 门）② 我的工作流脚本真调用（第 94 门 r222 第二把尺，排除探针件）
    #   ③ skill 手册指向的项目仓（第 67 门 r226 third_face，已剪 vendored 外来面）。
    #   三层都带 None≠0 语义：源件里没有该工具 ⇒ None（「没被量」），绝不记 0（「量到零」）。
    'workflow': 'workflow_usage_latest.json',
}

# 任务 -> 工具：从既有名册读，不另立第二份清单
TASK2TOOL = {
    'Pages 部署': 'Cloudflare-Pages',
    'D1 查额度': 'Cloudflare-D1',
    'R2 开桶': 'Cloudflare-R2',
    'Workers 调用量': 'Cloudflare-Workers',
    'Turnstile': 'Cloudflare-Turnstile',
    'Actions 分钟': 'GitHub',
    'CI 红了': 'GitHub',
    '钩子静默推送': 'GitHub',
    'Resend 发邮': 'Resend',
    'Upstash 限流': 'Upstash-Redis',
}

# 触点只写「已经在用的」，不写「打算怎么用」；缺证据的不填
TOUCH = {
    'GitHub': 'A-project-handoff 的 git_autopush 钩子模板（本仓 post-commit 即其落地）+ 第 87 门读 autopush 末行 rc；私有仓分钟用满是已付代价',
    'Cloudflare-D1': 'A-memory-start 的 quickref 额度专章（r196_quota_face 现读行数/写入）+ chaoshi-web-deploy 的 d1 execute 部署链',
    'Cloudflare-Pages': 'chaoshi-web-deploy 部署权威入口（direct_map 10 pattern，任务话术直连命中）',
    'Cloudflare-Workers': 'A-memory-start 的 quickref 额度专章（r199_workers_face 现读调用数）；跨 zone 聚合分母差异已写 §9.16',
    'Cloudflare-R2': 'chaoshi-image-optimization 的 R2 外置专章（干跑读数 + 阻断现状）',
    'Cloudflare-Turnstile': 'r163_turnstile_face 与 r163_turnstile_admin 曾全链接通，后按老大要求移除 = 决定而非待搭缺口',
    'SQLite': 'r203_ledger_index 用 SQLite 做门禁台账派生索引（读面与盲区均实测）',
    'VS Code': 'r163_free_tools_face 的 probe_vscode（which + 非 0 字节 + 真跑 --version）',
    'Resend': 'r163_tool_skill_matrix 已把它列入零引用核查面；仅 HTTP API 无 CLI，凭据缺 ⇒ 尚未接入任何工作流',
    'Upstash-Redis': 'r163_tool_skill_matrix 报其零引用（唯一 ADVISORY 项）；仅 REST 无 CLI，凭据缺 ⇒ 未接入',
}


# r228：零层归因（每条必须是「有证据的类别」，不是形容词）。
#   为什么需要它：名册此前只印三层读数，读者看到某个工具三层全零，**分不清是「被卡住」还是
#     「不适用」** —— 前者要推进，后者要接受。零层归因把这两类分开，且带可复算证据。
#   允许的类别词（机检白名单，写别的词即 FAIL）：
#     '平台能力缺口' / '外部凭据缺口' / '口径盲区' / '按用户要求移除' / '未入尺' / '无使用场景'
#   触发条件（牙腿 b1）：某工具既无 skill 代码级引用、又无工作流真调用 ⇒ 必须有一条归因；
#     缺归因或类别不在白名单或证据为空 ⇒ rc=1 不出册（禁让「没说清为什么零」的册子当交付）。
BLOCKER = {
    'Cloudflare-R2': {
        'class': '平台能力缺口',
        # r233：档位 2（浏览器自动化）也实测过了 —— 打开 Dashboard 直接命中 CF 安全质询页，
        #   在到达登录之前就被挡住 ⇒ 不是「我没试」，是两条档位都到不了启用那一步。
        'why': ('R2 未在账号启用（wrangler 与 REST 同回 10042，官方提示需 Dashboard 启用）；'
                '档位 2 实测打开 dash.cloudflare.com 即命中 CF 安全质询页（「正在进行安全验证」+ 质询 iframe），'
                '在登录前被挡 ⇒ 属平台+条款同意缺口 ∧ 自动化通道被平台自身反机器人质询拦截，'
                '非本机凭据问题（对照 /accounts=200 已证 API 凭据活着）'),
        'evidence': ('python 05-exec/r201_r2_enable_face.py --json 06-benchmark/r2_enable_latest.json'
                     '（state=GAP_SERVICE / code=10042）；浏览器档位取证：'
                     '06-benchmark/r2_dashboard_probe_2026-10-25.txt（agent-browser 只读快照）'),
    },
    'Upstash-Redis': {
        'class': '外部凭据缺口',
        'why': '仅有 REST 无 CLI，且本机未配 UPSTASH_* 凭据 ⇒ 无法接入；这是凭据缺口，不是搭配意愿问题',
        'evidence': 'python 05-exec/r163_free_tools_face.py --json 06-benchmark/free_tools_latest.json（该工具 state=GAP_CRED）',
    },
    'Cloudflare-Workers': {
        'class': '口径盲区',
        'why': '我的真实用法是**读数型**：走 CF GraphQL analytics 读调用数（token 见证据件），而形态级正则只认部署形态的三类写法 ⇒ 它看不见读数型搭配（不为此写假调用凑数）',
        'evidence': 'python 05-exec/r199_workers_face.py --json 06-benchmark/workers_quota_latest.json（真跑 MEASURED）；token workersInvocationsAdaptive 见该件 L50/L108',
    },
    'VS Code': {
        # r244：入尺后重写。原记「未入尺（第 67 门无该工具正则）」——那是**我这边没有尺**，不是它不适用；
        #   实测它有真实承载：技能 A-java-problem 把「交付前在 VS Code GUI 里真跑」写成验收步骤
        #   （Ctrl+Shift+B 出 exe → F5 停 main() 退出码 0；并记下 preLaunchTask label 须与 tasks.json 逐字相同、
        #   任务终端失焦时 stdin 被吞两个 GUI-only 坑），另有 .vscode / IDEA 对照的提法。
        #   归因改为『桌面 GUI 承载（非调用面）』：它被当**人工验证环境**用，而无头工作流没有调用面
        #   （#29 的 UIA 档位留给「必须自动化的 GUI 步骤」，此处人跑 F5 本身就是验收的一部分）。
        'class': '桌面 GUI 承载（非调用面）',
        'why': ('已入尺（第 67 门现含 VS Code 模式）。承载点在技能手册层：A-java-problem 的验收步骤要求人跑',
                'VS Code GUI（Ctrl+Shift+B → F5 停 main() 退出码 0），并沉淀了两个 GUI-only 坑；',
                '工作流侧本就无调用面 —— 我的产出是文件与提交，不需要开编辑器。CLI（code）在机，',
                '但可用不等于该用：不为把计数做非零而写假调用。'),
        # r244 自抓：首版两串之间**多了个逗号** ⇒ evidence 成了二元组，渲染处 `'...%s' % 元组` 报
        #   「not all arguments converted during string formatting」。相邻字面量拼接**不能带逗号**。
        'evidence': ('python 05-exec/r163_tool_skill_matrix.py --json 件（per_tool[\'VS Code\'] = 提到/代码级两把尺）；'
                     '承载原文：D:/global_skills/A-java-problem/log/iteration-log.md 的 2026-10-12 C++ 条目'),
    },
}

# r244：新增『桌面 GUI 承载（非调用面）』—— VS Code 入尺后，它的零调用不再能记成「未入尺」（已入尺），
#   也不是「无使用场景」（技能 A-java-problem 真把它当交付前验证环境用），而是**它的用法本身就是 GUI 人工步骤**：
#   无头工作流没有调用面（#29 的 UIA 档位只适用于必须自动化的 GUI 步骤，而这里人跑 F5 正是验收的一部分）。
#   同族还有 '未入尺'（r244 后暂空置 —— VS Code 已入尺；保留该项以防将来再有未入尺的工具）。
BLOCKER_CLASSES = ('平台能力缺口', '外部凭据缺口', '口径盲区', '按用户要求移除', '未入尺', '无使用场景',
                   '桌面 GUI 承载（非调用面）')
# r229：第 4 层 —— 读数型真调用（读得到数）。
#   为什么需要它：r228 给 Workers 的归因是「口径盲区」——它的真实用法是走 API 读调用数，而形态级正则
#     只认部署形态。只留归因，读者仍会把它读成「没在用」。把「读数面真跑出数」单列一层，
#     就能把「能读」与「形态层看不见」同时摆出来（R2 也有读数面，但它读不到 ⇒ 这一层是 0，区分得开）。
#   登记口径（只登记**我核实过产物名与状态路径**的读数面；产物名不可靠的一律记 None=未量，不猜）：
#     script  = 产生读数的脚本；artifact = 其产物件；path = 取 state 的路径（'rows' 段表示按 tool 键查行）。
READ_FACE = {
    'Cloudflare-Workers': {'script': 'r199_workers_face.py',
                           'artifact': 'workers_quota_latest.json',
                           'path': ['row', 'state'],
                           # r239：第 5 项 —— 用量。第 4 层只说「读得到数」，没说**多少**；
                           #   而这三个免费工具的额度是真会触顶的东西（5GiB / 2000 分钟 / 免费调用量），
                           #   不把量印出来，「搭配得合不合理」就少一半依据。
                           'usage': ['row', 'invocations_month'], 'unit': '次',
                           'window': ['row', 'window']},
    'Cloudflare-D1': {'script': 'r196_quota_face.py',
                      'artifact': 'quota_face_latest.json',
                      'path': ['rows', 'cloudflare_d1', 'state'],
                      'usage': ['rows', 'cloudflare_d1', 'mib'], 'unit': 'MiB',
                      'extra': ['rows', 'cloudflare_d1', 'pct_of_roster_limit'],
                      'extra_label': '占名册声称上限',
                      'window': ['rows', 'cloudflare_d1', 'limit_label']},
    # r241：GitHub 的读数面换成**官方计费端点**（/users/{u}/settings/billing/usage）。
    #   为什么换：quota_face 的 447.92 是「本仓墙钟分钟」，它自己写明「墙钟 != billable、作用域是本仓
    #   != 账号级、且官方免费分钟数当时未取到可靠出处 ⇒ 不折算百分比」。r241 实测到官方端点直接给
    #   计费项（quantity/unitType/gross/discount/net/repositoryName）⇒ 这才是权威用量。
    #   ⚠ 口径差异要写清：官方面是**账号级、端点默认窗口**（现值 2026-08-01~10-01，3 个月），
    #     不是「本月」；名册第 ⑤ 列单位里注明，窗口随读数一起印。墙钟数仍留在 quota_face 里做交叉核对。
    'GitHub': {'script': 'r241_gh_billing_face.py',
               'artifact': 'gh_billing_latest.json',
               'path': ['state'],
               'usage': ['minutes_total'],
               'unit': '分钟（官方计费·账号级·端点默认窗口）',
               'extra': ['net_total'], 'extra_label': '折后净额 $',
               'window': ['window_items_dates']},
    'Cloudflare-R2': {'script': 'r201_r2_enable_face.py',
                      'artifact': 'r2_enable_latest.json',
                      'path': ['state']},
    # r230：Pages 的产物名从权威源取（run_gates.GATES 的 argv），不猜：
    #   pages_http_face → pages_http_latest.json（row.state）。
    # r242：Turnstile 的「无读数面」被实测推翻 —— 官方数据集 account.turnstileAdaptiveGroups 存在，
    #   参数名由读数面在**运行时自省**得到（不猜）。实测窗口 2026-09-30~10-25 校验请求 0 次。
    'Cloudflare-Turnstile': {'script': 'r242_turnstile_usage_face.py',
                              'artifact': 'turnstile_usage_latest.json',
                              'path': ['state'],
                              'usage': ['count_total'], 'unit': '次（校验请求）',
                              'window': ['window']},
    # r243：SQLite 本地体量面（体量非额度；陈旧度 = 库 mtime vs 最新输入件）
    'SQLite': {'script': 'r243_sqlite_usage_face.py',
               'artifact': 'sqlite_usage_latest.json',
               'path': ['state'],
               'usage': ['size_mib'], 'unit': 'MiB（本地库体量·非额度）',
               'extra': ['rows_total'], 'extra_label': '合计行数',
               'window': ['db_mtime']},
    'Cloudflare-Pages': {'script': 'r200_pages_face.py',
                         'artifact': 'pages_http_latest.json',
                         'path': ['row', 'state'],
                         'usage': ['row', 'requests_total'], 'unit': '次',
                         'window': ['row', 'window']},
}

# r230：无读数面的工具 —— 逐个核实后**具名说明为什么没有**，不留「未量」这种含糊态。
#   与 READ_FACE 的关系：两者必须覆盖全部入册工具（牙 r4 锁死），否则说明我没逐个核实。
NO_READ_FACE = {
    # r243：SQLite 原记「本地嵌入库，无平台额度面 ⇒ 无读数面」——与 Turnstile 同病：把**没有额度**
    #   读成**没有可读的数**。实测本机库 11.79 MiB / 7 表 / 42488 行 / 陈旧度可测 ⇒ 已改为读数面。
    #   该条已删。
    'VS Code': '编辑器本体，无平台额度概念 ⇒ 无读数面（用量 = 装机与扩展，属桌面侧，未入本尺）',

    # r242：Turnstile 原记「无读数面（该门 argv 不带 --json）」，实测其官方数据集存在 ⇒ 该条已删。
    # r234：两档各证（与 R2 同标准）。档位 1 全机探查无凭据；档位 2 通道可达但需建号+条款 ⇒ 例外类。
    #   证据件 = 06-benchmark/free_tool_credential_probe_2026-10-25.txt（含键名清单与 grep 结果）。
    'Resend': ('有月度额度（免费 3000 封）但**全机无凭据**（env 0 命中、.env/.dev.vars 键名与它无关、'
               '全 workspace grep 只命中我自己的旧门产物）；档位 2 可打开发 signup 但需账号持有人建号+条款同意 '
               '⇒ #29 例外类（凭据缺口 ∧ 第三方账号授权），不是没有读数面'),
    'Upstash-Redis': ('有月度额度（免费 50 万命令）但**全机无凭据**（同上探查）；档位 2 console 探查挂起后已终止，'
                      '该通道结论不依赖它 ⇒ 凭据缺口，不是没有读数面'),
}
READ_STATES = ('MEASURED', 'PARTIAL', 'GAP_SERVICE', 'GAP_CRED', 'GAP_PLATFORM', 'UNVERIFIED')


def _pick(data, path):
    """按路径取值；'rows' 段表示「按下一段作为 tool 键查行」再继续。取不到返回 (None, why)。"""
    cur = data
    i = 0
    while i < len(path):
        k = path[i]
        if k == 'rows':
            if i + 1 >= len(path):
                return None, '路径写法错（rows 后缺行键）'
            want = path[i + 1]
            rows = cur.get('rows') if isinstance(cur, dict) else None
            m = None
            for x in (rows or []):
                if isinstance(x, dict) and x.get('tool') == want:
                    m = x
                    break
            if m is None:
                return None, '产物里找不到行 tool=%s' % want
            cur = m
            i += 2
            continue
        if not isinstance(cur, dict) or k not in cur:
            return None, '路径取不到：%s' % '/'.join(path)
        cur = cur[k]
        i += 1
    return cur, None


def read_face_usage(tool):
    """r239：取用量（第 5 项）。未登记 / 取不到 ⇒ (None, why)，禁记 0。"""
    spec = READ_FACE.get(tool) or {}
    up = spec.get('usage')
    if not up:
        return None, None, '未登记用量路径'
    fp = os.path.join(B, spec.get('artifact') or '')
    if not os.path.isfile(fp):
        return None, None, '产物缺失：' + str(spec.get('artifact'))
    try:
        d = json.load(io.open(fp, encoding='utf-8'))
    except (OSError, ValueError):
        return None, None, '产物不可析'
    v, why = _pick(d, up)
    if v is None or why:
        return None, None, why or '用量字段为空'
    extra = None
    if spec.get('extra'):
        ev, _e = _pick(d, spec['extra'])
        extra = ev
    win = None
    if spec.get('window'):
        wv, _w = _pick(d, spec['window'])
        win = wv
    return v, {'unit': spec.get('unit'), 'extra': extra,
               'extra_label': spec.get('extra_label'), 'window': win}, None


def read_face_state(tool):
    """取某工具读数面的真状态。未登记读数面 / 产物缺失 / 路径取不到 ⇒ (None, why)。

    禁把「取不到」记成 0（R247 同族）：未量是未量，零是零。
    """
    spec = READ_FACE.get(tool)
    if not spec:
        why = NO_READ_FACE.get(tool)
        return None, None, ('无读数面：' + why) if why else '未登记读数面（未量：我还没核实）'
    fp = os.path.join(B, spec['artifact'])
    if not os.path.isfile(fp):
        return None, spec, '产物缺失：' + spec['artifact']
    try:
        d = json.load(io.open(fp, encoding='utf-8'))
    except (OSError, ValueError):
        return None, spec, '产物不可析：' + spec['artifact']
    path = spec['path']
    cur = d
    i = 0
    while i < len(path):
        k = path[i]
        if k == 'rows':
            # 取 rows 后面那个元素作为行键（r229 自抓：我先写成取最后一个元素 = state，
            # 于是 rows/github_actions_minutes_proxy/state 被解成「按 tool=state 查行」⇒ 取不到；
            # 牙 r1 当场红了才看见）。
            if i + 1 >= len(path):
                return None, spec, '路径写法错（rows 后缺行键）'
            want = path[i + 1]
            rows = cur.get('rows') if isinstance(cur, dict) else None
            m = None
            for x in (rows or []):
                if isinstance(x, dict) and x.get('tool') == want:
                    m = x
                    break
            if m is None:
                return None, spec, '产物里找不到行 tool=%s' % want
            cur = m
            i += 2
            continue
        if not isinstance(cur, dict) or k not in cur:
            return None, spec, '路径取不到：%s' % '/'.join(path)
        cur = cur[k]
        i += 1
    return (str(cur) if cur is not None else None), spec, None

GATES = {
    'GitHub': '163 + 87 + 93',
    'Cloudflare-D1': '163 + 88 任务层 + 93',
    'Cloudflare-Pages': '163 + 92 + 93',
    'Cloudflare-Workers': '163 + 88 任务层 + 93',
    'Cloudflare-R2': '163 + 88 任务层 + 93',
    'Cloudflare-Turnstile': '163 + 88 任务层(DISPUTED) + 93',
    'SQLite': '163 + 85 + 93',
    'VS Code': '163 + 93',
    'Resend': '163 + 93',
    'Upstash-Redis': '163 + 93',
}


def load(n):
    """n 含 * 时按 mtime 取最新一份（且必须是第 67 门产物：含 per_tool_exec）。

    返回 (数据, 实际文件名)。取不到返回 (None, n) —— 调用方据此 UNVERIFIED，
    不得退回去读我那份弱化 probe（第二真相源）。
    """
    def one(f):
        q = os.path.join(B, f)
        if not os.path.isfile(q):
            return None
        try:
            return json.load(io.open(q, encoding='utf-8'))
        except (OSError, ValueError):
            return None
    if '*' in n:
        fs = [f for f in sorted(glob.glob(os.path.join(B, n)), key=os.path.getmtime)
              if 'probe' not in os.path.basename(f)]
        for f in reversed(fs):
            v = one(os.path.basename(f))
            if isinstance(v, dict) and v.get('per_tool_exec') is not None:
                return v, os.path.basename(f)
        return None, n
    return one(n), n


def build():
    src = {}
    used = {}
    for k, fn in SRC.items():
        v, real = load(fn)
        if v is None:
            return None, '源件缺失或不可析：' + fn
        src[k.rstrip('*')] = v
        used[k.rstrip('*')] = real
    pat_map = {k.lower(): v for k, v in (src['patterns'].get('patterns') or {}).items()}
    skills = CC.all_skills()
    rows = src['roster'].get('rows') or []
    if not rows:
        return None, '名册 rows 为空 = 空面不得出册（R247）'
    # 两把尺直接用第 67 门产物（工具名两边一致，无需映射）；probe 那份已停读
    per_t = src['matrix'].get('per_tool') or {}
    per_e = src['matrix'].get('per_tool_exec') or {}
    # r227：工作流真调用（第 94 门第二把尺）与项目仓面（third_face）也进册。
    W = {}
    for x in (src['workflow'].get('tools') or []):
        W[x.get('tool')] = x
    TF_ALL = src['matrix'].get('third_face')
    THIRD = (TF_ALL or {}).get('per_tool') or {}
    # r227 自抓（None/0 第四次同族）：third_face 的 per_tool **只记 n>0 的工具** ⇒
    #   「工具不在字典里」= 扫过但零命中（0），不是「没量」。若整块 third_face 为 None，
    #   才是真的没量（None）。两者必须分开，否则 R2 这种真零会显示成「未量」而躲过审视。
    tasks = src['truth'].get('tasks') or []
    items = []
    for r in rows:
        tool = r.get('tool')
        in67 = tool in per_t or tool in per_e
        linked = []
        for x in tasks:
            want = x.get('want')
            tk = x.get('task')
            if want and TASK2TOOL.get(tk) == tool:
                linked.append({'task': tk, 'outcome': x.get('outcome'),
                               'top1': x.get('top1'), 'skill': want})
        _rs = read_face_state(tool)
        _us = read_face_usage(tool)
        items.append({
            'tool': tool,
            'state': r.get('state'),
            # 两把尺（第 67 门口径）：提到 = 文档或代码出现该工具；可执行 = 代码真调用。
            # 关键：工具不在第 67 门名册时记 None，不记 0 —— 0 会把「它没被这道门量」
            # 冒充成「零提到」（R216-2 那处集合差正是此形，VS Code 就命中这一支）。
            'mention_skills': (sorted(per_t.get(tool)) if tool in per_t else None),
            'exec_skills': (sorted(per_e.get(tool)) if tool in per_e else None),
            'yardstick_absent': tool not in per_t and tool not in per_e,
            # r227 三层补齐（None≠0：源件缺该工具 ⇒ None，不记 0）
            'wf_real_hits': ((W.get(tool) or {}).get('real_hits') if tool in W else None),
            'wf_real_files': ((W.get(tool) or {}).get('real_files') if tool in W else None),
            'third_hits': (((THIRD.get(tool) or {}).get('hits') or 0) if TF_ALL is not None else None),
            'third_files': (((THIRD.get(tool) or {}).get('files') or []) if TF_ALL is not None else None),
            # r231：第三层的质量拆分 —— 命中里有几行是注释，以及「整块只有注释」的判定。
            'third_lines': (((THIRD.get(tool) or {}).get('lines') or 0) if TF_ALL is not None else None),
            'third_comment_lines': (((THIRD.get(tool) or {}).get('comment_lines') or 0) if TF_ALL is not None else None),
            'third_comment_share': ((THIRD.get(tool) or {}).get('comment_share') if TF_ALL is not None else None),
            'third_comment_only': ((THIRD.get(tool) or {}).get('comment_only') if TF_ALL is not None else None),
            'gates': GATES.get(tool, ''),
            'touchpoint': TOUCH.get(tool, ''),
            'claims': (CC.claims_for(TOUCH.get(tool, ''),
                            pat_map.get(TF.norm(tool)) or [], skills)
                       + GC.claims_for(TOUCH.get(tool, ''),
                                         pat_map.get(TF.norm(tool)) or [])),
            'patterns_n': len(pat_map.get(TF.norm(tool)) or []),
            'tasks': linked,
            # r228：零层归因（None = 该工具不需要归因：至少有一层在干真活）
            'blocker': BLOCKER.get(tool),
            # r229 第 4 层：读数型真调用（读得到数）。None = 未量（未登记读数面/产物缺），不记 0。
            'read_state': _rs[0],
            'read_face': _rs[1],
            'read_why': _rs[2],
            # r239 第 5 项：用量（数值 + 单位 + 窗口 + 可选占比）。None = 未量，禁记 0。
            'usage_value': _us[0],
            'usage_meta': _us[1],
            'usage_why': _us[2],
        })
    c = src['carrier']
    i = src['ingress']
    rc = src['recall']
    gates = {
        'carrier': {'tools': c.get('tools'), 'vols': c.get('vols'),
                    'uncarried': len(c.get('gaps') or []), 'k5': c.get('k5_teeth')},
        'ingress': {'checked': i.get('checked'), 'gaps': len(i.get('gaps') or []),
                    'k5': i.get('k5')},
        'recall': {'window': rc.get('checked'), 'truth': rc.get('truth_judged'),
                   'task': rc.get('task_judged'), 'hits': rc.get('task_hits'),
                   'gaps': len(rc.get('gaps') or [])},
        # 两把尺的出处随读数一起落盘：源件名 + 该件生成时间 ⇒ 陈旧可见，不静默沿用旧矩阵
        'matrix_src': {'file': used.get('matrix'),
                       'generated_at': src['matrix'].get('generated_at'),
                       'cmd': src['matrix'].get('cmd')},
        # r227：新增两层的出处也随读数落盘（源件名 + 生成时间 + 剪掉的外来面清单长度）
        'workflow_src': {'file': used.get('workflow'),
                         'generated_at': src['workflow'].get('generated_at'),
                         'face_files': src['workflow'].get('face_files'),
                         'real_face_files': src['workflow'].get('real_face_files'),
                         'real_total_hits': src['workflow'].get('real_total_hits')},
        'third_src': {'files_scanned': (src['matrix'].get('third_face') or {}).get('files_scanned'),
                      'roots': (src['matrix'].get('third_face') or {}).get('roots'),
                      'pruned_foreign_n': len((src['matrix'].get('third_face') or {}).get('pruned_foreign') or []),
                      'files': used.get('matrix')},
    }
    return {'items': items, 'gates_reading': gates}, None


def render_md(doc):
    L = []
    L.append('# 免费工具 x 工作流 x skill 搭配名册（生成物，勿手改）')
    L.append('')
    L.append('生成命令：python 05-exec/r215_free_tool_roster.py --json <件>')
    L.append('')
    g = doc['gates_reading']
    L.append('## 依据面（五道判据当前读数）')
    L.append('')
    L.append('| 判据 | 量什么 | 读数 |')
    L.append('|---|---|---|')
    L.append('| 163 | 工具在本机能不能跑 | 名册 %d 项 |' % len(doc['items']))
    L.append('| 93 | 每个工具是否至少被一个 skill 承载 | 工具 %s / 扫描 %s 卷 / 未承载 %s |' % (
        g['carrier']['tools'], g['carrier']['vols'], g['carrier']['uncarried']))
    L.append('| 92 | 每轮入口会不会把话术派到写着答案的卷 | 判 %s / 缺口 %s |' % (
        g['ingress']['checked'], g['ingress']['gaps']))
    L.append('> 依据面取值：163 见 free_tools_latest.json；93 见 tool_carrier_latest.json 与 '
             'tool_skill_matrix_probe.json；92 见 ingress_latest.json；88 见 recall_latest.json '
             '与 route_truth_latest.json。再生命令见文件头。')

    L.append('| 88 | 窗口 / BGE 真值 / 任务语句三层 | 窗口 %s、真值 %s、任务 %s 命中 %s、缺口 %s |' % (
        g['recall']['window'], g['recall']['truth'], g['recall']['task'],
        g['recall']['hits'], g['recall']['gaps']))
    L.append('')
    # r235：搭配总表（一眼可读）。理由：逐工具长节共 20KB，读者要想知道「十个工具到底搭到哪一步、
    #   被卡的是哪几个」，得自己滚完十节 —— 交付物缺一个执行视图。总表全部由 items 计算得出，
    #   禁手写（手写必漂）。牙 r6 锁死：总表行数必须等于 items 数，且每个工具恰好出现一次。
    L.append('## 搭配总表（一眼版）')
    L.append('')
    L.append('| 工具 | ① skill 提到/代码 | ② 工作流真调用 | ③ 项目仓（剪后·含注释占比） | ④ 读数面 | ⑤ 用量 | 卡点/状态 |')
    L.append('|---|---|---|---|---|---|---|')
    _full = _real = _blocked = _noread = 0
    for it in doc['items']:
        ms, es = it['mention_skills'], it['exec_skills']
        wf = it.get('wf_real_hits')
        th = it.get('third_hits')
        cs = it.get('third_comment_share')
        rq = it.get('read_state')
        bl = it.get('blocker') or {}
        c1 = ('%s / %s' % (len(ms) if ms is not None else '未量',
                           len(es) if es is not None else '未量'))
        c2 = ('未量' if wf is None else str(wf))
        if th is None:
            c3 = '未量'
        elif th == 0:
            c3 = '0'
        else:
            c3 = '%s（注释占比 %s%s）' % (th, cs, '·仅注释' if it.get('third_comment_only') else '')
        c4 = rq if rq else '无读数面'
        note = ('[%s]' % bl.get('class')) if bl else it['state']
        if (es or []) and (wf or 0) > 0 and (th or 0) > 0 and rq == 'MEASURED':
            _full += 1
        if (wf or 0) > 0 or (es or []):
            _real += 1
        if bl:
            _blocked += 1
        if not rq:
            _noread += 1
        um5 = it.get('usage_meta') or {}
        c5 = ('未量' if it.get('usage_value') is None else
              '%s %s' % (it.get('usage_value'), um5.get('unit') or ''))
        L.append('| %s | %s | %s | %s | %s | %s | %s |' % (
            it['tool'], c1, c2, c3, c4, c5, note))
    L.append('')
    L.append('汇总：四层齐备（有代码级/有工作流调用/项目仓有命中/读数 MEASURED）= **%d** 项；'
             '有真调用（工作流或代码级任一）= %d 项；带卡点归因 = %d 项；无读数面 = %d 项。' % (
                 _full, _real, _blocked, _noread))
    L.append('')
    L.append('（总表取值：同下各节；每行都由 items 计算，禁手写 —— 牙 r6 校验行数与工具集合。）')
    L.append('')
    L.append('## 逐工具搭配态')
    L.append('')
    for it in doc['items']:
        L.append('### %s - %s' % (it['tool'], it['state']))
        L.append('')
        ms, es = it['mention_skills'], it['exec_skills']
        if it.get('yardstick_absent'):
            L.append('- 两把尺：该工具不在第 67 门名册内 = 未被量（None，不等于 0）')
        else:
            L.append('- 两把尺：提到 %d 件 ｜ 代码真调用 %d 件' % (len(ms or []), len(es or [])))
            L.append('    提到 = %s' % (', '.join(ms or []) or '无'))
            L.append('    可执行 = %s' % (', '.join(es or []) or '无'))
        L.append('    （取值：%s 的 per_tool / per_tool_exec[%s]；该件 generated_at=%s）' % (
            doc['gates_reading']['matrix_src'].get('file'), it['tool'],
            doc['gates_reading']['matrix_src'].get('generated_at')))
        # r227：三层一起印（禁把任一层读成「没搭配」）
        wfh, thh = it.get('wf_real_hits'), it.get('third_hits')
        L.append('- 三层读数：')
        L.append('    ① skill 目录（第 67 门）：提到 %s ｜ 代码真调用 %s' % (
            (len(ms) if ms is not None else '未量'), (len(es) if es is not None else '未量')))
        L.append('    ② 工作流脚本（第 94 门 r222 第二把尺，探针件不计入）：真调用 %s' % (
            wfh if wfh is not None else '未量（该工具不在第 94 门名册 = None，不等于 0）'))
        if wfh:
            L.append('        调用它的非探针件 = %s' % (', '.join(it.get('wf_real_files') or []) or '无'))
        L.append('    ③ 项目仓（第 67 门 r226 third_face，已剪 vendored 外来面）：%s' % (
            thh if thh is not None else '未量（整块 third_face 缺失 = 项目仓没被扫，不等于 0）'))
        if thh:
            L.append('        命中所在件 = %s' % (', '.join(it.get('third_files') or []) or '无'))
        if thh and it.get('third_lines'):
            _co = it.get('third_comment_only')
            L.append('        质量拆分：命中行 %s，其中注释行 %s（占比 %s）%s' % (
                it.get('third_lines'), it.get('third_comment_lines'),
                it.get('third_comment_share'),
                '⇒ **仅注释提及，不是在跑它**' if _co else ''))
        gs_ = doc['gates_reading']
        L.append('    （② 取值：%s 的 tools[].real_hits，窗口面 %s/%s 件、真调用合计 %s；' % (
            gs_.get('workflow_src', {}).get('file'),
            gs_.get('workflow_src', {}).get('real_face_files'),
            gs_.get('workflow_src', {}).get('face_files'),
            gs_.get('workflow_src', {}).get('real_total_hits')))
        L.append('     ③ 取值：%s 的 third_face.per_tool，%s 件 / %s 仓 / 剪外来面 %s 个）' % (
            gs_.get('third_src', {}).get('files'),
            gs_.get('third_src', {}).get('files_scanned'),
            len(gs_.get('third_src', {}).get('roots') or []),
            gs_.get('third_src', {}).get('pruned_foreign_n')))
        bl = it.get('blocker')
        if bl:
            L.append('- **零层归因：[%s]** %s' % (bl['class'], bl['why']))
            L.append('    （取值：%s）' % bl['evidence'])
        rstate = it.get('read_state')
        rf = it.get('read_face') or {}
        if rstate:
            rd_note = '读得到数' if rstate == 'MEASURED' else '读数面真实状态（未读到数）'
            L.append('- 读数型真调用（第 4 层）：**%s**（%s）' % (rstate, rd_note))
            L.append('    （取值：%s --json %s 的 %s）' % (
                rf.get('script'), rf.get('artifact'), '/'.join(rf.get('path') or [])))
        else:
            _w = (it.get('read_why') or '未登记读数面').replace('无读数面：', '').replace('无读数面', '')
            L.append('- 读数型真调用（第 4 层）：无读数面 —— %s（无读数面 ≠ 0）' % (_w or '未登记读数面'))
        uv, um = it.get('usage_value'), it.get('usage_meta') or {}
        if uv is None:
            L.append('- 本月/当前用量：未量（%s；未量不等于 0）' % (it.get('usage_why') or '未登记用量面'))
        else:
            extra = ''
            if um.get('extra') is not None:
                extra = '（%s %s）' % (um.get('extra_label') or '占比', um.get('extra'))
            L.append('- 本月/当前用量：**%s %s**%s%s' % (
                uv, um.get('unit') or '', extra,
                ('　窗口：%s' % um.get('window')) if um.get('window') else ''))
            L.append('    （取值：%s --json %s 的 %s）' % (
                (it.get('read_face') or {}).get('script'), (it.get('read_face') or {}).get('artifact'),
                '/'.join([str(z) for z in (READ_FACE.get(it['tool'], {}).get('usage') or [])])))
        L.append('- 守它的判据：' + it['gates'])
        L.append('- 工作流触点：' + it['touchpoint'])
        cs = it.get('claims') or []
        if cs:
            for c in cs:
                who = c.get('skill') or (str(c.get('gate_file')) + '（判据件）')
                L.append('- 触点在位核验（在位≠已接入）：%s -> %s' % (who, c['verdict']))
        else:
            L.append('- 触点在位核验（在位≠已接入）：本行未点名可核对象（勿当已核）')
        ts = it['tasks'] or []
        if ts:
            L.append('- 任务语句实测：')
            for x in ts:
                L.append('    - %s -> %s（top1=%s，期望件=%s）' % (
                    x['task'], x['outcome'], x['top1'], x['skill']))
        else:
            L.append('- 任务语句实测：名册无对应条目（不编造）')
        L.append('')
    return L


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', dest='out',
                    default='06-benchmark/free_tool_roster_latest.json')
    ap.add_argument('--md', dest='md',
                    default='06-benchmark/free_tool_roster_latest.md')
    args = ap.parse_args(argv)
    doc, err = build()
    src_workflow_tools = None
    try:
        import json as _json
        _wf = _json.load(io.open(os.path.join(B, 'workflow_usage_latest.json'), encoding='utf-8'))
        src_workflow_tools = _wf.get('tools') or []
    except (OSError, ValueError):
        src_workflow_tools = None
    if doc is None:
        print('[ROSTER:UNVERIFIED] ' + str(err) + ' = 不出册（R247 禁按旧记忆补面）')
        return 2
    NL = chr(10)
    op = args.out if os.path.isabs(args.out) else os.path.join(ROOT, args.out)
    mp = args.md if os.path.isabs(args.md) else os.path.join(ROOT, args.md)
    io.open(op, 'w', encoding='utf-8', newline=NL).write(json.dumps(
        {'schema': 'free-tool-roster-v1', 'readonly': True,
         'provenance_cmd': 'python 05-exec/r215_free_tool_roster.py --json <件>',
         **doc}, ensure_ascii=False, indent=1))
    # r227 牙：三层的 None/0 语义必须自洽，否则册子会把「真零」印成「未量」（或反之）。
    #   ① third_face 存在 ⇒ 每个入册工具的 third_hits 必须是 int（扫过就有数，零也记 0）
    #   ② workflow 那层的 None 只允许出现在 state=NO_PATTERN（无正则=没量）的工具上
    # 牙腿 b1（r228）：零层工具必须带**有证据的**归因 —— 「没说清为什么零」不得当交付。
    teeth_b = []
    need_block = []
    for it in doc['items']:
        no_exec = not (it.get('exec_skills') or [])
        no_wf = not it.get('wf_real_hits')
        if no_exec and no_wf:
            need_block.append(it['tool'])
    missing = [t for t in need_block if not doc['items'][[x['tool'] for x in doc['items']].index(t)].get('blocker')]
    teeth_b.append(('b1_zero_tools_have_blocker', not missing,
                    '需归因的工具=%s / 缺归因=%s（期望缺为空）' % (need_block, missing)))
    bad_cls = [it['tool'] for it in doc['items']
               if it.get('blocker') and it['blocker'].get('class') not in BLOCKER_CLASSES]
    teeth_b.append(('b2_blocker_class_whitelisted', not bad_cls,
                    '类别不在白名单的工具=%s（期望空）' % bad_cls))
    bad_ev = [it['tool'] for it in doc['items']
              if it.get('blocker') and not (it['blocker'].get('evidence') and it['blocker'].get('why'))]
    teeth_b.append(('b3_blocker_has_evidence', not bad_ev,
                    '缺 why 或 evidence 的工具=%s（期望空）' % bad_ev))
    # 牙 r1/r2/r3（r229）：读数面这一层必须真取到数、状态在册，且与归因不矛盾。
    teeth_r = []
    unresolved = []
    for it in doc['items']:
        rf = READ_FACE.get(it['tool'])
        if rf and not it.get('read_state'):
            unresolved.append('%s（%s）' % (it['tool'], it.get('read_why')))
    teeth_r.append(('r1_registered_read_face_resolves', not unresolved,
                    '登记了读数面却取不到状态的工具=%s（期望空：产物改名会当场红）' % unresolved))
    bad_state = [it['tool'] for it in doc['items']
                 if it.get('read_state') and it['read_state'] not in READ_STATES]
    teeth_r.append(('r2_read_state_whitelisted', not bad_state,
                    '状态不在册的工具=%s（期望空）' % bad_state))
    # r3 交叉一致性：读数面 MEASURED（读得到数）而该工具又带归因 ⇒ 归因只允许是「口径盲区」，
    #   因为「能读却形态层看不见」正是口径盲区的定义。写成平台/凭据缺口就是归因写错了。
    bad_pair = []
    for it in doc['items']:
        if it.get('read_state') == 'MEASURED' and it.get('blocker'):
            if it['blocker'].get('class') != '口径盲区':
                bad_pair.append('%s(读数=MEASURED, 归因=%s)' % (it['tool'], it['blocker'].get('class')))
    teeth_r.append(('r3_measured_state_vs_blocker_class', not bad_pair,
                    '读数MEASURED但归因非口径盲区的工具=%s（期望空）' % bad_pair))
    # 牙 r4（r230）：第 4 层必须**逐个工具**都有交代 —— 要么登记了读数面，要么具名说明无读数面；
    #   「未量」这种含糊态一律算红（它正是 r229 留下的尾巴：6 项没核实就记未量）。
    teeth_n = []
    # 牙 r8（r245）：第 ① 层列出的**技能 slug 必须都还在盘上**（带 SKILL.md 的真技能目录）。
    #   动因：名册把技能名写进交付物，但技能会被改名/退役 —— 那时名册就是**幽灵引用**：
    #   数还在、读起来像证据，实际指向一个不存在的技能（与 r1「登记了读数面却取不到状态」同族）。
    #   实测 r245：34 个被引 slug 全在盘（191 真技能）⇒ 当前零缺失；本牙防的是它下次改名。
    _gs = 'D:/global_skills'
    _cited = set()
    for it in doc['items']:
        for _s in (it.get('mention_skills') or []):
            _cited.add(_s)
        for _s in (it.get('exec_skills') or []):
            _cited.add(_s)
    _ghost = sorted(s for s in _cited
                    if not os.path.isfile(os.path.join(_gs, s, 'SKILL.md')))
    teeth_n.append(('r8_mention_slugs_resolve', not _ghost,
                    '第①层引用了盘上不存在的技能=%s（期望空：技能改名/退役后名册即成幽灵引用）' % _ghost))
    # 牙 r7（r239）：第 ④ 层判 MEASURED（读得到数）的工具**必须带出用量数值** ——
    #   否则说明第 ⑤ 层的取值路径写错/漂了（读面在跑却拿不到量，等于仪器接了线却没读数）。
    no_usage = [it['tool'] for it in doc['items']
                if it.get('read_state') == 'MEASURED' and it.get('usage_value') is None]
    teeth_n.append(('r7_measured_implies_usage_number', not no_usage,
                    'MEASURED 却无用量数值的工具=%s（期望空）' % no_usage))
    # 牙 r6（r235）：总表必须覆盖每个工具且不重不漏 —— 禁让「一眼版」漏掉某个工具（那比没有总表更糟）。
    md_lines = render_md(doc)
    # 只取「搭配总表（一眼版）」那一节的行（r235 自抓：首版把「依据面」表的 5 行也算进来 ⇒ 多出判据/163/93/92/88）
    try:
        s0 = next(i for i, l in enumerate(md_lines) if l.startswith('## 搭配总表'))
    except StopIteration:
        s0 = None
    s1 = None
    if s0 is not None:
        for i in range(s0 + 1, len(md_lines)):
            if md_lines[i].startswith('## '):
                s1 = i
                break
    section = md_lines[s0:s1] if s0 is not None else []
    row_tools = []
    for l in section:
        if not (l.startswith('| ') and ' | ' in l):
            continue
        cells = [c.strip() for c in l.strip('|').split('|')]
        if cells and cells[0] and cells[0] not in ('工具',) and not set(cells[0]) <= set('-:'):
            row_tools.append(cells[0])
    all_tools = [it['tool'] for it in doc['items']]
    miss = [t for t in all_tools if t not in row_tools]
    dup = [t for t in set(row_tools) if row_tools.count(t) > 1]
    extra = [t for t in row_tools if t not in all_tools]
    teeth_n.append(('r6_summary_covers_all_tools', not (miss or dup or extra),
                    '总表 %d 行 / 工具 %d 个；漏=%s 重=%s 多=%s（期望全空）' % (
                        len(row_tools), len(all_tools), miss, dup, extra)))
    # 牙 r5（r231）：第三层的注释拆分必须逐工具传到位（赛源：matrix 产物的 third_face.per_tool）
    _mfile = doc['gates_reading'].get('third_src', {}).get('files')
    src_th = ((json.load(io.open(os.path.join(B, _mfile), encoding='utf-8'))
               .get('third_face') or {}).get('per_tool') or {}) if _mfile else {}
    bad_q = []
    for it in doc['items']:
        v = src_th.get(it['tool'])
        if v is None:
            continue
        if it.get('third_comment_only') != bool(v.get('comment_only')):
            bad_q.append('%s(%s!=%s)' % (it['tool'], it.get('third_comment_only'), v.get('comment_only')))
    teeth_n.append(('r5_third_comment_split_propagated', not bad_q,
                    '注释only标记与源件不一致的工具=%s（期望空）' % bad_q))
    unclear = [it['tool'] for it in doc['items']
               if not READ_FACE.get(it['tool']) and not NO_READ_FACE.get(it['tool'])]
    teeth_n.append(('r4_every_tool_has_read_face_or_reason', not unclear,
                    '既无读数面也无具名理由的工具=%s（期望空：含糊态即红）' % unclear))
    teeth = []
    third_present = doc['gates_reading'].get('third_src', {}).get('files_scanned') is not None
    bad_third = [it['tool'] for it in doc['items']
                 if third_present and not isinstance(it.get('third_hits'), int)]
    teeth.append(('third_layer_zero_vs_unmeasured', not bad_third,
                  'third_face 存在时非 int 的工具=%s（期望空）' % bad_third))
    wfmap = {x.get('tool'): x for x in (src_workflow_tools or [])}
    bad_wf = [it['tool'] for it in doc['items']
              if it.get('wf_real_hits') is None
              and (wfmap.get(it['tool']) or {}).get('state') not in ('NO_PATTERN', None)]
    teeth.append(('workflow_none_only_when_no_pattern', not bad_wf,
                  'wf=None 但 state 不是 NO_PATTERN 的工具=%s（期望空）' % bad_wf))
    for n, ok, d_ in teeth + teeth_b + teeth_r + teeth_n:
        print('%s %-38s %s' % ('PASS' if ok else 'FAIL', n, d_))
        if not ok:
            print('[ROSTER:TEETH-FAIL] 三层语义不自洽 ⇒ 不出册（禁把不自洽的册子当交付）')
            return 1
    txt = NL.join(render_md(doc)) + NL
    assert chr(13) not in txt, 'introduced CR'
    io.open(mp, 'w', encoding='utf-8', newline=NL).write(txt)
    print('[ROSTER:OK] %d 工具入册；未承载 %s；md %dB' % (
          len(doc['items']), doc['gates_reading']['carrier']['uncarried'],
          len(txt.encode('utf-8'))))
    return 0


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
    sys.exit(main())