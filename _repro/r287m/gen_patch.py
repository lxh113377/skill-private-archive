# -*- coding: utf-8 -*-
r"""gen_patch.py — 从「本地逐字切片 + 上游逐字切片」机械生成 rule_editor replace 补丁（R287m）。

存在理由：本仓 4 次「锚点靠记忆」教训（R277-1 起）⇒ old/new 一律由 difflib 在两份实读文本上
取切片，人不手打一个字符；每条 old 落盘时即断言 count==1，把唯一性做成产出自证。

坐标（现取，非记忆）：
  repo=anthropics/skills  ref=main @ ca45fc496a3436251f191354091d557da31c15b5（2026-10-28T19:20:38Z，#2087）
  upstream_path=skills/mcp-builder/（ch3.path，06-benchmark/r275 rows[28] 逐字）
"""
import difflib, hashlib, json, os, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
D = os.path.join(ROOT, "_temp", "r287m")
L = "D:/global_skills/mcp-builder"
REPO = "anthropics/skills"
REF = "main"
REF_SHA = subprocess.run(["gh", "api", "repos/anthropics/skills/commits/main", "--jq", ".sha"],
                         capture_output=True, text=True).stdout.strip()

PAIRS = [
    ("SKILL.md", os.path.join(L, "SKILL.md"), os.path.join(D, "_upstream_SKILL.md"), "skills/mcp-builder/SKILL.md"),
    ("node_mcp_server.md", os.path.join(L, "reference", "node_mcp_server.md"),
     os.path.join(D, "_upstream_node_mcp_server.md"), "skills/mcp-builder/reference/node_mcp_server.md"),
]
NEW_FILE = ("node_mcp_server_v2.md", "skills/mcp-builder/reference/node_mcp_server_v2.md",
            os.path.join(D, "upstream_node_mcp_server_v2.md"))


def lines(p):
    return open(p, encoding="utf-8", newline="").readlines()


def op_of(tags, want):
    """按 (tag,i1,i2,j1,j2) 位置取 opcode —— 位置由 _probe_diff.py 实测打印，不靠记忆。"""
    for t in tags:
        if t == want:
            return t
    raise SystemExit("FATAL: opcode not found: %r（上游/本地漂移，须改走新增独立文件方案）" % (want,))


def mk(tid, target, file_label, up_path, a, b, i1, i2, j1, j2, note, new_override=None):
    old = "".join(a[i1:i2])
    new = new_override if new_override is not None else "".join(b[j1:j2])
    text = open(target, encoding="utf-8", newline="").read()
    n = text.count(old)
    ver = {"target": target.replace("\\", "/"), "file": file_label,
           "count": n, "start": text.find(old), "end": text.find(old) + len(old),
           "target_bytes": len(text.encode("utf-8")),
           "target_sha256_12": hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]}
    if n != 1:
        raise SystemExit("FATAL: %s old 命中 %d 次（应为 1）" % (tid, n))
    return {"id": tid, "target": target.replace("\\", "/"), "old": old, "new": new,
            "_source": {"repo": REPO, "ref": REF, "ref_sha": REF_SHA, "upstream_path": up_path,
                        "upstream_lines_1based": "L%d-L%d" % (j1 + 1, j2),
                        "local_lines_1based": "L%d-L%d" % (i1 + 1, i2)},
            "_note": note, "_verify": ver}


hunks = []
for label, lp, up, up_path in PAIRS:
    a, b = lines(lp), lines(up)
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    tags = [t for t in sm.get_opcodes() if t[0] != "equal"]
    print(label, "opcodes:", [(t[0], t[1], t[2], t[3], t[4]) for t in tags])
    if label == "SKILL.md":
        # 1) 双版本段（上游 L61-72 整块替换本地 L63-64 两行）
        _, i1, i2, j1, j2 = op_of(tags, ("replace", 62, 64, 60, 72))
        hunks.append(mk("SKILL-TS-DUALVERSION", lp, label, up_path, a, b, i1, i2, j1, j2,
                        "上游 v2/v1 双版本段整块落地（本地无领先内容）"))
        # 2) 项目结构指引改指 v2
        _, i1, i2, j1, j2 = op_of(tags, ("replace", 84, 85, 92, 93))
        hunks.append(mk("SKILL-STRUCTURE-PTR", lp, label, up_path, a, b, i1, i2, j1, j2,
                        "Project structure 指引改指 v2，v1 链接保留"))
        # 3) 自检脚本一行（上游 insert；replace 语义下用前一行做锚，old=本地该行切片）
        _, i1, i2, j1, j2 = op_of(tags, ("insert", 142, 142, 150, 151))
        hunks.append(mk("SKILL-V2-SELFCHECK", lp, label, up_path, a, b, i1 - 1, i2, j1, j2,
                        "锚=build 校验行；new=锚 + 上游新增自检行（两段皆为逐字切片）",
                        new_override="".join(a[i1 - 1:i2]) + "".join(b[j1:j2])))
        # 4) SDK 文档索引加 v2 llms.txt + v1.x
        _, i1, i2, j1, j2 = op_of(tags, ("replace", 214, 215, 223, 225))
        hunks.append(mk("SKILL-SDK-DOCINDEX", lp, label, up_path, a, b, i1, i2, j1, j2,
                        "Phase 1/2 文档索引改双版（v2 llms.txt + v1.x README）"))
        # 5) 实现指南书目：v2 全量条目 + v1 条目降级
        _, i1, i2, j1, j2 = op_of(tags, ("replace", 224, 230, 234, 244))
        hunks.append(mk("SKILL-IMPLGUIDE-BLOCK", lp, label, up_path, a, b, i1, i2, j1, j2,
                        "TypeScript Implementation Guide 换成 v2 条 + v1 条（上游整块）"))
        # 6) frontmatter 版本与日期（本地叠加项，上游无此行 ⇒ 不删，只递增）
        _, i1, i2, j1, j2 = op_of(tags, ("delete", 4, 6, 4, 4))
        ver_new = "last_updated: 2026-10-30\nversion: 1.1.0\n"
        hunks.append(mk("SKILL-FM-VERSION", lp, label, up_path, a, b, i1, i2, j1, j2,
                        "保留本地叠加 frontmatter，仅把 version 1.0.0->1.1.0 / last_updated->换装日；"
                        "上游该行不存在（r275 人读：本地叠加项须保留），故 new 为构造串而非上游切片",
                        new_override=ver_new))
        # 7) 版本史（S-15：frontmatter 与版本史必须一致，R271 判据）
        last = len(a) - 1
        hunks.append(mk("SKILL-VERSION-HISTORY", lp, label, up_path, a, b, last, last + 1, last, last + 1,
                        "old=本地末行逐字切片；new=末行 + 版本史小节（与 frontmatter 1.1.0/2026-10-30 对齐）",
                        new_override="".join(a[last:last + 1]) +
                                     "\n---\n\n## Version history\n\n"
                                     "- **1.1.0**（2026-10-30）— R287m 同源拉平 anthropics/skills@" + REF_SHA[:12] +
                                     "（#2087）：并入 reference/node_mcp_server_v2.md（新增独立件）+ TS 双版本段 + v1 横幅；"
                                     "本地叠加项 frontmatter/LICENSE/NOTICE 全保留。\n"))
    else:
        # 上游 insert(1,1 -> 1,3)：old 零长会命中全文 ⇒ old 取本地标题行（实测全文唯一 1 次），
        # new 取上游「标题+空行+横幅」连续切片（先断言两侧标题行逐字相等，防漂移）。
        _, i1, i2, j1, j2 = op_of(tags, ("insert", 1, 1, 1, 3))
        assert a[0] == b[0], "FATAL: 标题行不再逐字相等，insert 锚点失效"
        hunks.append(mk("NODE-V1-BANNER", lp, label, up_path, a, b, 0, 1, 0, 0,
                        "上游在标题后插 v1-only 横幅；old=本地标题行逐字切片（全文唯一），"
                        "new=上游标题+空行+横幅连续切片 b[0:3]",
                        new_override="".join(b[0:3])))

# 顺序敏感：SKILL-V2-SELFCHECK / SKILL-FM-VERSION 的 old 与相邻 hunk 不重叠，
# 但 SKILL-VERSION-HISTORY 的 old = 末行，必须排在最后一条 replace 之后再命中。
patch = [h for h in hunks if h["_verify"]["file"] == "SKILL.md"] + \
        [h for h in hunks if h["_verify"]["file"] != "SKILL.md"]
out = os.path.join(D, "patch.json")
json.dump(patch, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
man = {"schema": "r287m-newfile-manifest-v1", "repo": REPO, "ref": REF, "ref_sha": REF_SHA,
       "upstream_path": NEW_FILE[1], "local_target": L + "/reference/" + NEW_FILE[0],
       "staged_copy": NEW_FILE[2].replace("\\", "/"),
       "bytes": os.path.getsize(NEW_FILE[2]),
       "lines": sum(1 for _ in open(NEW_FILE[2], encoding="utf-8")),
       "sha256_12": hashlib.sha256(open(NEW_FILE[2], "rb").read()).hexdigest()[:12]}
json.dump(man, open(os.path.join(D, "newfile_manifest.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
print("HUNKS", len(patch))
for h in patch:
    print(" ", h["id"], h["_verify"]["file"], "count=", h["_verify"]["count"],
          "oldB=", len(h["old"].encode("utf-8")), "newB=", len(h["new"].encode("utf-8")))
print("REF_SHA", REF_SHA)
print("MANIFEST", json.dumps(man, ensure_ascii=False))