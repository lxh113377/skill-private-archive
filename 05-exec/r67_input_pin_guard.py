# -*- coding: utf-8 -*-
"""R58-1 第 17 维纵深常驻判据：仓外输入固定面（本地面）。

为什么这是「判据输入面」问题，而不是洁癖：
  本仓 26 道门读的全是**本地字节**，而这些字节由仓外三样东西决定 ——
  受管根本体（`D:\\global_skills` / `D:\\global_memory`）、焚诀、以及各端把受管根
  接到自己目录下的 **junction/镜像面**。CI 那一侧 r58 已用「pin 到不可变 SHA」固定了
  checkout；本地面此前**无人固定**：junction 断裂、被替换成真实目录、或被改成指向别处时，
  某端读到的根本不是权威源字节，而所有门禁照绿 —— 与 r58 D-113（未固定 checkout）同族，
  只是入口在本机。

四条不变式（缺一即红）：
  P1 形态/零输入（rc=2）：`paths` / `junction_paths` / `endpoints.active` 任一为空，
     或声明文件读不到 ⇒ UNVERIFIED，禁「没有声明所以全绿」（R247）。
  P2 镜像固定（rc=1）：`endpoints.active` × {skills,memory} 里**非 null** 的声明路径必须
     ① 存在 ② 是 junction/链接 ③ 解析目标 == 对应权威根。声明为 null 的记 `not_declared`
     分档并**逐条列出**（不静默丢，防「分母静默变小而面内全绿」）。
  P3 pin 落账：每次运行把各面 pin（HEAD sha + 未提交集摘要）append 进
     `06-benchmark/input_pins.jsonl`，使每个 verdict 可归因到确定的输入状态
     —— 这是「固定」在本地的等价物。
  P4 本行自洽（rc=1）：本门刚算出的 pin 必须与**同一次运行刚写入台账的那一行**逐字段相等
     （写哪本 / 指哪本 / 比哪本，r53 D-108 同族；防「写一份、判另一份」）。

**advisory（只报不阻断）**：与上一行台账比，列出 pin 变动的面 —— 这是本维度真正的信号，
  但受管根常年被并行会话改（r66 实测 45 条在途），做成硬闸即「消不掉的告警」（W-32 教训）。

用法：`python 05-exec/r67_input_pin_guard.py [--decl F] [--ledger F] [--gate]`
退出码：0 全绿 / 1 有违约 / 2 取数面不完整
"""
import argparse
import hashlib
import io
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DECL = r"C:\Users\37533\Desktop\workspace\焚诀\eval\truth_constants.json"
DEFAULT_LEDGER = os.path.join(os.path.dirname(HERE), "06-benchmark", "input_pins.jsonl")
# 焚诀仓：本仓的已知外部依赖（项目 AGENTS.md「外部依赖」段登记），无法从 truth_constants 反推，
# 故作为**具名常量**列出并写明来源，而不是从别处抄一份清单（X-26）。
FENJUE_ROOT = r"C:\Users\37533\Desktop\workspace\焚诀"


def _no_bom_json(path):
    with io.open(path, encoding="utf-8-sig") as f:
        return json.load(f)


def load_declaration(path):
    """读声明面；失败返回带 error 的空壳（调用方必须判空，不得当通过）。"""
    try:
        d = _no_bom_json(path)
    except (OSError, ValueError) as e:
        return {"error": "%s: %s" % (type(e).__name__, e)}
    if not isinstance(d, dict):
        return {"error": "声明文件根不是对象"}
    return d


# 变异钩子（夹具用它证明「这两条守卫确实在起作用」；生产恒为 True，见 r67 夹具 T9/T10）
REQUIRE_JUNCTION = True
REQUIRE_TARGET_EQ = True


def probe_face(path, canon):
    """实测一个镜像面：返回 {declared, exists, kind, target, ok, why}。

    `kind` 用 `lstat().st_reparse_tag` 判 junction/链接（Windows 下 junction 不是 S_ISLNK，
    只判 `os.path.islink` 会把它读成普通目录 —— 这正是本判据要防的形态之一）。
    """
    if not path:
        return {"declared": False, "exists": False, "kind": "not_declared", "target": "",
                "ok": False, "why": "声明为 null（该端设计上无此面）"}
    ap = os.path.abspath(os.path.expandvars(path))
    if not os.path.exists(ap):
        return {"declared": True, "exists": False, "kind": "missing", "target": "",
                "ok": False, "why": "声明路径不存在"}
    try:
        st = os.lstat(ap)
        is_rep = bool(getattr(st, "st_reparse_tag", 0))
    except OSError:
        is_rep = False
    try:
        target = os.path.realpath(ap)
    except OSError:
        target = ""
    kind = "junction" if is_rep else ("dir" if os.path.isdir(ap) else "file")
    if REQUIRE_JUNCTION and not is_rep:
        return {"declared": True, "exists": True, "kind": kind, "target": target, "ok": False,
                "why": "不是 junction/链接（真实目录 = 各端读到的是自己的副本，与权威源已脱钩）"}
    if not canon:
        return {"declared": True, "exists": True, "kind": kind, "target": target, "ok": False,
                "why": "权威根未声明，无法比对"}
    same = os.path.normcase(os.path.normpath(target)) == os.path.normcase(os.path.normpath(canon))
    return {"declared": True, "exists": True, "kind": kind, "target": target,
            "ok": same or (not REQUIRE_TARGET_EQ),
            "why": "" if same else "解析目标 != 权威源"}


def _git(root, *args):
    try:
        r = subprocess.run(["git", "-C", root] + list(args), capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        return r.returncode, (r.stdout or "")
    except OSError as e:
        return 127, str(e)


def pin_face(root):
    """算一个输入面的 pin：HEAD sha + 未提交集摘要。不可达 ⇒ state=unreachable。"""
    if not root or not os.path.isdir(root):
        return {"root": root, "state": "unreachable"}
    rc, head = _git(root, "rev-parse", "HEAD")
    if rc != 0:
        return {"root": root, "state": "not_a_repo"}
    rc2, st = _git(root, "status", "--porcelain")
    if rc2 != 0:
        return {"root": root, "state": "status_failed"}
    lines = sorted(l for l in st.splitlines() if l.strip())
    digest = hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()[:16]
    return {"root": root, "state": "pinned", "head": head.strip()[:12],
            "dirty_n": len(lines), "dirty_digest": digest}


def judge(decl, faces):
    """纯判定：给声明与「已探好的面表」返回 (rc, report)。faces = [(label, probe_dict)]。"""
    if decl.get("error"):
        return 2, {"reason": "声明面读不到：%s" % decl["error"], "probes": []}
    paths = decl.get("paths") or {}
    jp = decl.get("junction_paths") or {}
    active = (decl.get("endpoints") or {}).get("active") or []
    if not paths or not jp or not active:
        return 2, {"reason": "声明面不完整（paths/junction_paths/endpoints.active 有空项）⇒ 零输入，"
                             "不得判过（R247）", "probes": []}
    viol = [f for f in faces if f["probe"]["declared"] and not f["probe"]["ok"]]
    not_declared = [f for f in faces if not f["probe"]["declared"]]
    return (1 if viol else 0), {"reason": "", "probes": faces, "violations": viol,
                                "not_declared": not_declared}


def build_faces(decl):
    """按声明表逐面实测（不手抄清单：端与路径全部来自 truth_constants）。"""
    canon = {"skills": (decl.get("paths") or {}).get("global_skills"),
             "memory": (decl.get("paths") or {}).get("global_memory")}
    faces = []
    for ep in (decl.get("endpoints") or {}).get("active") or []:
        per_end = (decl.get("junction_paths") or {}).get(ep) or {}
        for kind_name in ("skills", "memory"):
            p = per_end.get(kind_name)
            faces.append({"label": "%s.%s" % (ep, kind_name), "path": p,
                          "probe": probe_face(p, canon.get(kind_name))})
    return faces, canon


def self_consistent(pins, back_faces):
    """P4：刚写入台账的 faces 必须与本次算出的 pin 逐字段相等（写一份判另一份即假绿，D-108 同族）。"""
    return list(back_faces or []) == list(pins or [])


def main(argv=None):
    ap = argparse.ArgumentParser(description="R58-1 仓外输入固定面（本地面）")
    ap.add_argument("--decl", default=DEFAULT_DECL)
    ap.add_argument("--ledger", default=DEFAULT_LEDGER)
    ap.add_argument("--gate", action="store_true")
    a = ap.parse_args(argv)

    decl = load_declaration(a.decl)
    faces, canon = build_faces(decl)
    rc, rep = judge(decl, faces)
    viol = rep.get("violations", [])

    if rc == 2:
        print("[PIN:UNVERIFIED] %s" % rep["reason"])
        return 2

    print("权威根: global_skills=%s ｜ global_memory=%s" % (canon.get("skills"), canon.get("memory")))
    print("镜像面: 共 %d 条（应判 %d 条，声明 null %d 条）"
          % (len(faces), len(faces) - len(rep.get("not_declared", [])), len(rep.get("not_declared", []))))
    for f in faces:
        pr = f["probe"]
        if not pr["declared"]:
            print("  · %-10s %-44s not_declared（%s）" % (f["label"], f["path"] or "-", pr["why"]))
        elif pr["ok"]:
            print("  ✅ %-10s %-44s -> %s" % (f["label"], f["path"], pr["target"]))
        else:
            print("  ❌ %-10s %-44s %s（实测 target=%s）" % (f["label"], f["path"], pr["why"], pr["target"]))

    # ── P3 pin 落账 + P4 本行自洽 + advisory 变动清单
    roots = [canon.get("skills"), canon.get("memory"), FENJUE_ROOT]
    pins = [pin_face(r) for r in roots if r]
    prev = None
    try:
        if os.path.isfile(a.ledger):
            with io.open(a.ledger, encoding="utf-8") as fh:
                rows = [json.loads(l) for l in fh if l.strip()]
            if rows:
                prev = rows[-1]
    except (OSError, ValueError) as e:
        print("  ⚠️ 台账读不到（%s）⇒ 本行仍落账，但变动清单本轮不可比" % e.__class__.__name__)
    row = {"schema": "input-pins-v1", "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
           "decl": os.path.basename(a.decl), "faces": pins,
           "mirror_total": len(faces), "mirror_ok": len(faces) - len(viol) - len(rep.get("not_declared", []))}
    try:
        os.makedirs(os.path.dirname(a.ledger), exist_ok=True)
        with io.open(a.ledger, "a", encoding="utf-8", newline="") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    except OSError as e:
        print("[PIN:UNVERIFIED] 台账写不进去（%s）⇒ 无法固定输入面" % e.__class__.__name__)
        return 2
    back = None
    with io.open(a.ledger, encoding="utf-8") as fh:
        back = [json.loads(l) for l in fh if l.strip()][-1]
    if not self_consistent(pins, back.get("faces")):
        print("[PIN:FAIL] 本行自洽破：刚写入的 pin 与本次算出的不一致（写一份判另一份，D-108 同族）")
        return 1
    if prev:
        changed = [f["root"] for f, p in zip(pins, prev.get("faces") or [])
                   if f.get("state") == "pinned" and p.get("state") == "pinned"
                   and (f.get("head"), f.get("dirty_digest")) != (p.get("head"), p.get("dirty_digest"))]
        print("  ℹ️ 与上一行台账比：pin 变动 %d 个面%s（advisory，只报不阻断）"
              % (len(changed), ("：" + ", ".join(os.path.basename(c) for c in changed)) if changed else ""))

    if a.gate:
        if viol:
            print("[PIN:FAIL] 镜像/克隆面固定被破坏 %d 条：%s"
                  % (len(viol), ", ".join(v["label"] for v in viol)))
            print("   处置：对该端重建 junction 指向权威源（或跑既有 check-skill-mirror 链路）；"
                  "本门只判「镜像面是否钉在权威源」这一项事实")
            return 1
        print("[PIN:PASS] 镜像面 %d 条全部钉在权威源（声明 null %d 条已逐条列出）｜pin 已落账 %d 面"
              % (len(faces) - len(rep.get("not_declared", [])), len(rep.get("not_declared", [])), len(pins)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
