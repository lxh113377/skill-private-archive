# -*- coding: utf-8 -*-
"""r312 n=2 合判执行器（机械面）：task3 双臂用 --named=(订单金额|金额|clean) 判机械四项。
与 task2 的 r310_jrun 同构：人判四项由第三方盲评臂出（键 X3/Y3），本器合分并揭盲。
映射件=r312a/hidden_assignment.json（固定映射，偏差已在该件声明）。输出 n2_merge.json：两题各自 delta + 合并均值。
引用上限：n=2 的合并值只作观测点，禁写成「质量提升 X%」结论（rubric3 归因纪律同款）。"""
import json, os, subprocess, sys
NL2 = chr(10)
PY = sys.executable
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = "C:/Users/37533/Desktop/workspace/skill焚诀/自建skill优化"
JF = A + "/_temp/r309a/anchor_judge.py"
t3 = A + "/_temp/r312a"
NAMED3 = "(订单金额|金额|clean)"
def judge_task(task_dir, xs, ys, xlog, ylog, manual, hs, out_json):
    cmd = [PY, "-B", JF, "--x-prompt", xs, "--x-log", xlog, "--y-prompt", ys, "--y-log", ylog,
           "--manual", json.dumps(manual), "--json", out_json, "--named", NAMED3] if task_dir.endswith("r312a") else \
          [PY, "-B", JF, "--x-prompt", xs, "--x-log", xlog, "--y-prompt", ys, "--y-log", ylog,
           "--manual", json.dumps(manual), "--json", out_json]
    import shutil
    # 判据从 HERE 读 hidden_assignment：HERE=判据所在目录 ⇒ 每任务先临时换映射件（备份恢复），或给判据加 --assign。
    # 取轻方案：临时复制判据到任务目录跑（它用 __file__ 的 dirname 找映射件与写 json）。
    local_j = os.path.join(task_dir, "anchor_judge.py")
    shutil.copyfile(JF, local_j)
    cmd[2] = local_j
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=400, cwd=task_dir)
    return r

def main():
    # task3 就绪检查：两臂四件齐才跑（不齐 ⇒ UNVERIFIED 退出，禁按 0 计）
    need = [t3 + "/out_X3/optimized_prompt.md", t3 + "/out_X3/process_log.md",
            t3 + "/out_Y3/optimized_prompt.md", t3 + "/out_Y3/process_log.md"]
    miss = [p for p in need if not os.path.isfile(p)]
    if miss:
        print("[R312:N2] UNVERIFIED task3 交付缺件：%s（禁按 0 分计）" % ", ".join(os.path.basename(m) for m in miss))
        return 2
    # 人判四项等第三方盲评臂（score_C3.json）；没有 ⇒ 本器只出机械四项 + blind 状态
    sc3 = t3 + "/score/score_C3.json"
    manual = {}
    if os.path.isfile(sc3):
        try:
            d = io_open(sc3)  # io_open 已含 json.loads（上一版 json.load(dict) 抛 TypeError 被下面 except 吞掉=静默假 0 分，r312 实锤）
            for side in ("X3", "Y3"):
                manual[side] = {k: d[side]["items"][k] for k in ("1", "2", "3", "7")}
        except Exception as e:
            print("[R312:N2] manual 装载失败（禁静默吞）:", repr(e)[:90])
            manual = {}
    else:
        manual = {"X3": {"1": 0, "2": 0, "3": 0, "7": 0}, "Y3": {"1": 0, "2": 0, "3": 0, "7": 0}}
        print("[R312:N2] 人判四项暂缺第三方件：manual 传 0 占位，**只引用机械四项**直至 score_C3.json 到达")
    r = main3(manual)
    return r

def io_open(p):
    import io
    return json.loads(io.open(p, encoding="utf-8").read())

def main3(manual):
    keymap = {"X3": "X", "Y3": "Y"}  # 判据的 manual 键是 X/Y（映射件 r312a 的键也是 X/Y）
    m = {keymap[k]: v for k, v in manual.items()}
    r = judge_task(t3, t3 + "/out_X3/optimized_prompt.md", t3 + "/out_Y3/optimized_prompt.md",
                   t3 + "/out_X3/process_log.md", t3 + "/out_Y3/process_log.md", m,
                   t3 + "/hidden_assignment.json", t3 + "/mech_task3.json")
    print("[task3 rc=%d]" % r.returncode)
    for l in (r.stdout or "").strip().splitlines():
        print("  " + l[:165])
    if (r.stderr or "").strip():
        print("  ERR:", r.stderr.strip().splitlines()[-1][:140])
    return r.returncode

if __name__ == "__main__":
    sys.exit(main())

