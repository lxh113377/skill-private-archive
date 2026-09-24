# -*- coding: utf-8 -*-
r"""r20_dirty_source_patchgen.py — 生成 rule_editor「写前脏源检测」补丁 JSON（TDD 绿阶段实现体）。

来源: 受管根 `A-memory-start/references/rule_editor.py` 实测行文本（1364-1365 main 头部 global、
      1379 argparse 循环、80 模块级 flag、1415 flag 赋值、192-196 write_text、
      884-888 `git add -A -- r` 循环）；根因证据 = 两次夹带复现（f6f5b0c 带走他人 1 行、
      4b75d80 他人带走我的 contract.md hunks）。
流向: 本脚本 → `05-exec/r20-patches/patch_ruleeditor.json` → `rule_editor.py replace --patch`
      （先 --dry-run 六处全命中才写盘）→ 受管根工具行为变更 → 由 `05-exec/r20_dirty_source_stub.py`
      层 a（6 例已知答案）+ 层 b′（真实他人在途文件必须被点名 / 本工具链上文件不误报）双向验证。
结构: 纯追加式改动，不改既有 add/commit 语义；写入链落 `BACKUP_DIR/write_chain.jsonl`
      （BACKUP_DIR 自 B4 起在受管根外 = D:\global_memory_archive\_trash\rule_backup，
      不污染 受管根 status）；记录字段仅 rel/pre_sha/post_sha（无时间戳依赖，避免新 import）。
异常: 链文件不可读 → 返回空链（此时若文件确脏会**照报**，宁误报不漏报）；HEAD 不可读或磁盘
      指纹读不到 → 不报（新文件/异常态不猜测）；放行需显式 `--allow-dirty-source` 并留痕 jsonl。
"""

import json
from pathlib import Path

OUT = Path(__file__).resolve().parent / "r20-patches"
OUT.mkdir(exist_ok=True)

HELPERS = '''
# ── 写前脏源检测（r20）：防「动手前文件就带着他人在途改动，被本次 commit 一并带走」────
# 与 R229 的分工：R229 回答「我写完以后有没有被人再改」（进程内指纹 + 提交窗口快照），
# 本检测回答「我**动手以前**它脏不脏」——后者才是 f6f5b0c / 4b75d80 两次整文件夹带的根因。
# 判据可机器化的前提：rule_editor 每次写盘都留下 pre_sha/post_sha，形成「本工具写入链」，
# 于是「脏」可二分：链上（自己前一笔 --no-commit 的中间态，正当）vs 链外（他人/更早会话，须告警）。
WRITE_CHAIN_NAME = "write_chain.jsonl"
DIRTY_SOURCE_OVERRIDE_LOG = "dirty_source_overrides.jsonl"


def _rel_of(path):
    """受管根相对路径（与 git 一致的 / 分隔）。仓外路径返回 basename（不参与脏源判定）。"""
    try:
        rel = os.path.relpath(path, GIT_ROOT)
    except ValueError:
        return os.path.basename(path)
    if rel.startswith(".."):
        return os.path.basename(path)
    return rel.replace("\\\\", "/")


def _write_chain_path():
    return os.path.join(BACKUP_DIR, WRITE_CHAIN_NAME)


def load_write_chain(limit=4000):
    """读本工具历史写入链（append-only JSONL）。不可读 → 空列表（此时确脏仍会告警）。"""
    out = []
    try:
        with open(_write_chain_path(), "r", encoding="utf-8") as fh:
            lines = fh.readlines()[-limit:]
    except OSError:
        return out
    for ln in lines:
        try:
            rec = json.loads(ln)
        except ValueError:
            continue
        if isinstance(rec, dict) and rec.get("rel"):
            out.append(rec)
    return out


def _record_write(rel, pre_sha, post_sha):
    """留一笔写入链；失败静默（链缺失只会多告警不会漏告警，属安全侧）。"""
    try:
        os.makedirs(BACKUP_DIR, exist_ok=True)
        with open(_write_chain_path(), "a", encoding="utf-8") as fh:
            fh.write(json.dumps({"rel": rel, "pre_sha": pre_sha, "post_sha": post_sha},
                                ensure_ascii=False) + "\\n")
    except OSError:
        pass


def _multi_author_findings(rel, head_blob_val, pre_sha, chain):
    """动手前磁盘既 != HEAD、又不在本工具写入链上 ⇒ 判「多源共存」（提交会把他人改动一并带走）。"""
    if not head_blob_val or not pre_sha or pre_sha == head_blob_val:
        return []
    if any(r.get("rel") == rel and r.get("post_sha") == pre_sha for r in chain):
        return []
    return ["%s: 编辑前工作树内容 != HEAD 且不在本工具写入链上（疑似他人在途改动，"
            "整文件提交会一并带走）——先 `git diff -- %s` 逐 hunk 人工归属，或等归属会话自行收口"
            "后再提交；确需放行加 --allow-dirty-source（计入逃生门留痕）" % (rel, rel)]


def _dirty_source_warnings(rels):
    """commit 前批量判定：返回告警列表（空 = 无多源共存）。"""
    chain = load_write_chain()
    out = []
    for rel in rels:
        out += _multi_author_findings(rel, _head_blob(rel),
                                      _file_sha256(os.path.join(GIT_ROOT, rel)), chain)
    return out


def _log_dirty_source_override(rels, desc):
    """逃生门留痕（与 allow_collide 台账同构，便于事后归因与预警）。"""
    try:
        os.makedirs(BACKUP_DIR, exist_ok=True)
        with open(os.path.join(BACKUP_DIR, DIRTY_SOURCE_OVERRIDE_LOG), "a", encoding="utf-8") as fh:
            fh.write(json.dumps({"rels": list(rels), "desc": (desc or "")[:160]},
                                ensure_ascii=False) + "\\n")
    except OSError:
        pass


'''

OLD_WRITE_TEXT = '''def write_text(path, text):
    """UTF-8 写入（无 BOM）。R229：写入后记录本进程写下的内容指纹（提交时归属校验用）。"""
    with open(path, "w", encoding="utf-8", newline="\\n") as f:
        f.write(text)
    _LAST_WRITE[_norm(path)] = _file_sha256(path)'''

NEW_WRITE_TEXT = OLD_WRITE_TEXT.replace(
    '"""UTF-8 写入（无 BOM）。R229：写入后记录本进程写下的内容指纹（提交时归属校验用）。"""',
    '"""UTF-8 写入（无 BOM）。\n\n    R229：写后记本进程指纹；r20 追加：写**前**把 pre_sha/post_sha 记入跨进程写入链，\n'
    '    供 commit 前的「写前脏源检测」二分归属（链上=自己的中间态，链外=他人在途）。\n    """'
).replace(
    "    _LAST_WRITE[_norm(path)] = _file_sha256(path)",
    "    _LAST_WRITE[_norm(path)] = _file_sha256(path)\n"
    "    _record_write(_rel_of(path), pre_sha, _LAST_WRITE[_norm(path)])"
).replace(
    "    with open(path, \"w\", encoding=\"utf-8\", newline=\"\\n\") as f:",
    "    pre_sha = _file_sha256(path)\n"
    "    with open(path, \"w\", encoding=\"utf-8\", newline=\"\\n\") as f:"
)

HUNKS = [
    # 1) 新函数族插在 R229 指纹区之前（锚在 _norm 之后的 read_text 结尾不稳定，改锚 write_text 定义前）
    {"old": OLD_WRITE_TEXT, "new": HELPERS.lstrip("\n") + NEW_WRITE_TEXT},
    # 2) 模块级逃生门 flag
    {"old": 'ALLOW_COLLIDE = False  # R231：编号预检 fail-closed 的显式逃生门（--allow-collide 强行提交）',
     "new": 'ALLOW_COLLIDE = False  # R231：编号预检 fail-closed 的显式逃生门（--allow-collide 强行提交）\n'
            'ALLOW_DIRTY_SOURCE = False  # r20：写前脏源检测 fail-closed 的显式逃生门（--allow-dirty-source）'},
    # 3) main 的 global 声明
    {"old": "    global NO_GIT, FIX_MIRROR, ALLOW_COLLIDE",
     "new": "    global NO_GIT, FIX_MIRROR, ALLOW_COLLIDE, ALLOW_DIRTY_SOURCE"},
    # 4) flag 取值
    {"old": '    ALLOW_COLLIDE = getattr(args, "allow_collide", False)',
     "new": '    ALLOW_COLLIDE = getattr(args, "allow_collide", False)\n'
            '    ALLOW_DIRTY_SOURCE = getattr(args, "allow_dirty_source", False)'},
    # 5) 子命令参数
    {"old": '        sp.add_argument("--no-commit", action="store_true", dest="no_commit", '
            'help="只备份+写盘不提交（批量编辑模式，稍后用 commit 子命令一次收口）")',
     "new": '        sp.add_argument("--no-commit", action="store_true", dest="no_commit", '
            'help="只备份+写盘不提交（批量编辑模式，稍后用 commit 子命令一次收口）")\n'
            '        sp.add_argument("--allow-dirty-source", action="store_true", dest="allow_dirty_source",\n'
            '                        help="r20：放行「编辑前文件已带他人在途改动」的脏源告警（默认 fail-closed 中止提交并留痕）")'},
    # 6) commit 前挂载（staging 之前）
    {"old": '        for r in rels:\n'
            '            subprocess.run(\n'
            '                ["git", "add", "-A", "--", r],\n'
            '                cwd=GIT_ROOT, capture_output=True, timeout=120, check=True,\n'
            '            )',
     "new": '        # r20 写前脏源检测（fail-closed）：动手前文件就带着非本工具产生的改动 ⇒ 中止提交\n'
            '        ds_warns = _dirty_source_warnings(rels)\n'
            '        if ds_warns and not ALLOW_DIRTY_SOURCE:\n'
            '            for _w in ds_warns:\n'
            '                print(_w)\n'
            '            print("[git] \\u26d4 写前脏源检测未通过（fail-closed），提交已中止——"\n'
            '                  "本次 commit 会把他人在途 hunks 一并带走。逐 hunk 归属后再提交；"\n'
            '                  "确需放行加 --allow-dirty-source。")\n'
            '            return\n'
            '        if ds_warns and ALLOW_DIRTY_SOURCE:\n'
            '            for _w in ds_warns:\n'
            '                print(_w)\n'
            '            print("[git] \\u26a0\\ufe0f 已显式放行写前脏源告警（--allow-dirty-source）——本次计入留痕")\n'
            '            _log_dirty_source_override(rels, desc)\n'
            '        for r in rels:\n'
            '            subprocess.run(\n'
            '                ["git", "add", "-A", "--", r],\n'
            '                cwd=GIT_ROOT, capture_output=True, timeout=120, check=True,\n'
            '            )'},
]


def main():
    import sys
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    p = OUT / "patch_ruleeditor.json"
    p.write_text(json.dumps(HUNKS, ensure_ascii=False, indent=1), encoding="utf-8")
    back = json.loads(p.read_text(encoding="utf-8"))
    print("%s hunk=%d 读回=%s" % (p.name, len(back), "OK" if len(back) == len(HUNKS) else "FAIL"))
    print("NEW_WRITE_TEXT 预览:\n" + NEW_WRITE_TEXT[:520])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
