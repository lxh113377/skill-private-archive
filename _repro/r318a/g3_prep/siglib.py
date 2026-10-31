# -*- coding: utf-8 -*-

"""r316c 共享签名库（被 build_evidence.py 与 check_r316c.py 同时引用）。


设计逻辑（#42：把怎么运作写清）：

  - 禁用整行重合率判同族：r315 已证伪——本地把上游内容吸收后改写为中文，行级必然不重合，

    会把同族误判成异族。改用四条签名轴 + 一条块级轴（A5），全是「集合包含」而非「字符串相等」。

  - A1 标题域：标题词元 Jaccard（去掉停用词）。

  - A2 用途动词：动词集 Jaccard。本例中它近乎恒高（read/edit/run 谁都写），过堂多半无牙 => 会被判作废，

    这正是已知答案堂存在的意义：无牙的轴不许参与裁定。

  - A3 工具命令面：长选项旗标 + 正文出现的 CLI 名集合 Jaccard。

  - A4 判别词包含率：上游「带信息词元」（代码块 / 反引号内联 / 旗标 / 文件名 / 标题词）中

    能在本地面找到的比例。方向性包含，天然回答「本地是否覆盖上游」。

  - A5 块级包含率：按上游 ##/### 切块，逐块算 A4，再取均值（对「成块缺失」更敏感，是主判据）。

  - 本地面 = 受管根件内 SKILL.md + 全部子目录 .md（分卷是包的一部分，只比正文必然假报缺块）。

"""

import os, re, json, hashlib


MGD = "D:/global_skills"

HERE = os.path.dirname(os.path.abspath(__file__))

RAW = os.path.join(HERE, "raw")

UPSTREAM_CODING = os.path.join(RAW, "upstream_SKILL.md")

DECLARED_BLOB = "821111317265648bdaa42643d82a5cfc393592ba"

UPSTREAM_BYTES = 10285


STOP = set(( 

"the a an of and or to in for on with that this it is are be as by at from not no nor so "

"you your yours we our us i me my mine them they their its can could should would may might "

"will need needs needed want wants wanted one two three more most other others such same "

"than because before after while during each every too only own up down out over under "

"again further once here there both few many much now when what how where why which who "

"whose use used uses using any all if then else do does did done doing also into about "

"between per via like get got gets getting has have had having make makes making "

"keep keeps kept let lets put puts set sets take takes taken give gives given see sees "

"seen seeing look looks ran running add adds added call calls called ask asks asked "

"tell tells said say say must shall cant wont him hers himself itself something nothing "

"anything everything well done full whole entire just even still yet already ever never "

"always often rarely first second third last next previous current existing above below "

"top bottom side parts part bit lots lot kind sorts sort type types example examples "

"case cases point points thing things way ways number named given ").split())


VERBS = ["create","read","edit","update","delete","manipulate","convert","generate","extract",

    "render","delegate","dispatch","implement","review","commit","land","install","launch","run",

    "test","verify","check","poll","wait","spawn","monitor","fix","refactor","ship","deploy",

    "navigate","screenshot","assert","debug","inspect","patch","merge","queue","resume","notify",

    "open","close","search","build","send","bootstrap","redline","comment","branch","login",

    "approve","bundle","replace","hand","obtain","capture","continue","terminate"]


BINS = ["npx","npm","bash","sh","zsh","node","python","python3","git","codex","claude","opencode",

    "codebuddy","pandoc","soffice","unzip","zip","tar","curl","make","cargo","go","uv","pip","gh",

    "openclaw","rg","grep","mktemp","cat","printf","powershell","pwsh","cmd","start","grok"]


# 每轴最小牙距：两极差量小于此值 => 该轴无判别力，判定时作废（不参与裁定）

MIN_TEETH = {"A1_title_domain": 0.03, "A2_purpose_verbs": 0.05, "A3_tool_cmd_surface": 0.05,

             "A4_distinctive_containment": 0.15, "A5_block_containment": 0.15}

# 主判据 = 块级包含；确认据 = 判别词包含；两者必须同向才出结论

PRIMARY = "A5_block_containment"

CONFIRM = "A4_distinctive_containment"



def txt(path):

    with open(path, encoding="utf-8", errors="replace") as fh:

        return fh.read()



def bytes_of(path):

    with open(path, "rb") as fh:

        return fh.read()



def git_blob_sha(data):

    # 自算 git 对象号，和 gh 报的 sha 对拍 => 钉住「上游没漂移」

    h = hashlib.sha1()

    h.update(b"blob " + str(len(data)).encode() + b"\x00" + data)

    return h.hexdigest()



def toks(s):

    out = set()

    for w in re.findall(r"[a-z][a-z0-9_./+-]{3,}", s.lower()):

        w = w.strip("._+-/")

        if len(w) > 3 and w not in STOP:

            out.add(w)

    return out



def heads(text):

    for line in text.splitlines():

        m = re.match(r"^(#{1,3})[ ]+(.*)$", line)

        if m:

            yield (len(m.group(1)), m.group(2).strip())



def head_set(text):

    s = set()

    for lvl, h in heads(text):

        s |= toks(h)

    return s



def verb_set(text):

    low = " " + text.lower() + " "

    return set(v for v in VERBS if re.search("[^a-z]" + v + "[a-z]*[^a-z]", low))



def cmd_set(text):

    s = set(f.lower() for f in re.findall(r"-{1,2}[A-Za-z][A-Za-z0-9_-]{2,}", text))

    low = " " + text.lower() + " "

    for b in BINS:

        if re.search("[^a-z0-9/]" + b + "[^a-z0-9]", low):

            s.add(b)

    return s



def distinctive(text):

    # 只收「带信息词元」，散文词不入集合：中文改写会让散文词全丢，把它们计入会假报缺块

    s = set()

    for m in re.findall(r"`([^`\n]{2,120})`", text):

        s |= toks(m)

    for m in re.findall(r"```[^`\n]*\n(.*?)```", text, re.S):

        s |= toks(m)

    s |= cmd_set(text)

    s |= head_set(text)

    for m in re.findall(r"[A-Za-z0-9_./-]+\.(?:md|json|sh|mjs|py|js|ts|xml|yaml|yml|txt|docx|dotx|blend)", text):

        s.add(m.lower())

    return set(x for x in s if len(x) > 3)



def skel(text):

    h = list(heads(text))

    return [sum(1 for a, _x in h if a == 1), sum(1 for a, _x in h if a == 2), sum(1 for a, _x in h if a == 3)]



def face(d):

    files = []

    sk = os.path.join(d, "SKILL.md")

    if os.path.exists(sk):

        files.append(sk)

    for root, dirs, names in os.walk(d):

        if os.path.abspath(root) == os.path.abspath(d):

            continue

        for n in sorted(names):

            if n.lower().endswith(".md"):

                files.append(os.path.join(root, n))

    return "\n".join(txt(f) for f in files), files



def jac(a, b):

    if not a or not b:

        return 0.0

    return round(len(a & b) / float(len(a | b)), 4)



def blocks_of(text):

    # 按 ##/### 切上游块；start/end 是 1 基闭区间行号（逐字引用用）

    lines = text.splitlines()

    idx = [i for i, l in enumerate(lines) if re.match(r"^#{2,3}[ ]", l)]

    idx.append(len(lines))

    out = []

    for k in range(len(idx) - 1):

        a, b = idx[k], idx[k + 1]

        body = "\n".join(lines[a:b])

        out.append({"head": lines[a].strip(), "start": a + 1, "end": b, "text": body})

    return out



def blockwise(up_text, local_face):

    low = local_face.lower()

    rows = []

    for b in blocks_of(up_text):

        dt = distinctive(b["text"])

        if not dt:

            continue

        hit = set(t for t in dt if t in low)

        rows.append({"head": b["head"], "start": b["start"], "end": b["end"],

                     "n_distinctive": len(dt), "cov": round(len(hit) / float(len(dt)), 4),

                     "absent": sorted(dt - hit)})

    return rows



def axes(local_dir, up_path):

    lf, used = face(local_dir)

    up = txt(up_path)

    rows = blockwise(up, lf)

    a4 = round(sum(r["cov"] * r["n_distinctive"] for r in rows) /

               float(max(1, sum(r["n_distinctive"] for r in rows))), 4)

    a5 = round(sum(r["cov"] for r in rows) / float(max(1, len(rows))), 4)

    return {"A1_title_domain": jac(head_set(lf), head_set(up)),

            "A2_purpose_verbs": jac(verb_set(lf), verb_set(up)),

            "A3_tool_cmd_surface": jac(cmd_set(lf), cmd_set(up)),

            "A4_distinctive_containment": a4,

            "A5_block_containment": a5,

            "_face_files": len(used), "_local_bytes": len(lf.encode("utf-8")),

            "_skel_local": skel(lf), "_skel_up": skel(up),

            "_blocks": rows, "_lf": lf, "_up": up}
