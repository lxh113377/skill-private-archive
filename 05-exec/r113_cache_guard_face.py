# -*- coding: utf-8 -*-
r'''r113_cache_guard_face.py -- 常驻门（第 33 门）：证据缓存写侧必须声明防覆写守卫。

存在理由（两代一手，同族两形态）：
  r112：r112_upstream_probe.fetch_candidate 一次网络 EOF 把 14KB 好件覆写成 280B 失败桩
    ——单件形态（已修：失败不覆盖已成功缓存，只追加 cache_error 侧痕）。
  r113：r96_twelve_face 写的是整面语料缓存（05-exec/r96_gh_raw.json = 第 19 维 inferred
    身份来源根）。大面积临时失败时整体覆写会把好语料塌成一片 available False，而面内
    不变式照样自洽（X-24 同族：分母静默变小仍全绿）=> 已修：degrade_check 整面防退化闸。
  本门不逐件修，而是把「凡把远端取数结果写进可复用证据路径的脚本必须声明守卫」钉成
  结构判据，防第 3 次同族返工（新增取数脚本裸写缓存，当轮即红）。

判据（逐行口径；r113 一手：首版按 basename 判定被实测证伪——夹具文件名含 baseline
  即误判成证据面，且 .write_text( 零捕获信息，故改为行级三条件）：
  P1 取数面 = 文件含 gh api / gh_get / subprocess.run / urlopen / requests.get
  P2 写点   = 某行同时含写标记（open(...w / .write_text( / json.dump(）
              与**持久路径标记**（args.cache / BENCH / HERE / 06-benchmark / _raw / pins /
              corpus / EVID / registry.json）——正向鉴别，不用 ledger/baseline 泛词
  P3 豁免   = 该行指向临时目录（tmp/temp/mkdtemp/gettempdir/_temp）或每轮新产物
              （args.out / args.json / 日期 / 轮号 rNN / strftime）=> 不进分母
              理由：每轮新产物不存在「上一份同路径证据」，覆写不毁证据
  P4 守卫   = 命中 P2 的文件必须含守卫 token 之一：
              cache_error（单件不覆盖）/ degrade_check（整面防退化）/ merge_note（留账只增不减）
              缺则 FAIL 并逐件点名写点
  扫描面为空 => rc=2 UNVERIFIED（R247：0 件不得读成「全部有守卫」）

写法注（r113 一手，两次失败才收敛）：正则模式串里不出现字面引号字符类，运行时用
  chr(39)/chr(34) 现拼——「含引号或反斜杠的代码落成 .py 再跑」这条坑规的第二型：
  落到文件也照样炸在生成阶段（本仓第八条）。
用法：python 05-exec/r113_cache_guard_face.py [--exec-dir 05-exec] [--quiet]
退出码：0 [CACHEGUARD:PASS] / 1 裸写违规 / 2 面不可用或为空。
'''
import argparse
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# 引号字符类运行时现拼（源码内不写字面引号类，见文件头「写法注」）
_QC = "[" + chr(39) + chr(34) + "]"
_NQ = "[^" + chr(39) + chr(34) + "]"

FETCH_RE = re.compile("gh api|gh_get|subprocess[.]run|urlopen|requests[.]get", re.I)
# r113 一手（本夹具抓到）：写标记首版写成 w[bt]，把最常见的 open(x, "w") 整个滤掉
# ——f3/f4 当时的「绿」并非来自豁免规则，而是来自这条漏匹配（假绿）。故 w 后 b/t 改为可选。
WRITE_MODE = ("open[(]" + _NQ + "{0,140}?" + _QC + _NQ + "*w[bt]?" + _QC
              + "|[.]write_text[(]|json[.]dump[(]")
WRITE_RE = re.compile(WRITE_MODE)
# 正向鉴别 + 大小写敏感（r113 一手二/三，本门两次假阳性后定稿）：
#   一手二：泛词 cache|ledger|baseline 把夹具写进临时目录的 _zero_ledger 也算证据面；
#   一手三：改成 BENCH/HERE 后仍假阳性——r39_debt_ledger_fixtures.py 里小写变量
#            bench = tmp / "bench" 被 re.I 命中 BENCH，于是夹具自建的临时台账被判违规。
# 定稿 = 只认「会被下一轮读回的持久路径标记」且**大小写敏感**（常量/参数名的真实形态）：
#   args.cache / cache_p / BENCH / HERE / EVID / 06-benchmark / upstream_evidence /
#   _raw / pins / corpus / registry.json。小写 bench、ledger、baseline 一律不认。
EVID_RE_STR = ("args[.]cache|cache_p|BENCH|HERE|EVID|06[ -]benchmark"
               + "|upstream_evidence|_raw|pins|corpus|registry[.]json")
EVIDENCE_RE = re.compile(EVID_RE_STR)
TMP_RE = re.compile("tmp|temp|gettempdir|mkdtemp|_temp", re.I)
# 同一行既是临时特征就是临时件（r113：首版判定顺序为 TMP/PERROUND 先跳过，
# 但「行内只有 bench 变量名而无 tmp」的情形必须在 EVIDENCE 侧挡住，故双保险）。
PERROUND_RE = re.compile("args[.]out|args[.]json|out_json|datetime|strftime|now[(]"
                         + "|[rR][0-9]{2,}|%s|%d|20[0-9]{2}-[0-9]{2}-", re.I)
GUARD_TOKENS = ("cache_error", "degrade_check", "merge_note")
TOKEN = "[CACHEGUARD:PASS]"


def evidence_write_lines(text):
    u'''返回该文件里「写进可复用证据路径」的行（已剔除临时件与每轮新产物）。'''
    out = []
    for line in text.splitlines():
        if not WRITE_RE.search(line):
            continue
        if TMP_RE.search(line) or PERROUND_RE.search(line):
            continue
        if EVIDENCE_RE.search(line):
            out.append(line.strip()[:90])
    return out


def classify(paths):
    viol, ok_n, fetch_n, scanned = [], 0, 0, 0
    for p in paths:
        try:
            text = io.open(p, encoding="utf-8-sig", errors="replace").read()
        except OSError:
            continue
        scanned += 1
        if not FETCH_RE.search(text):
            continue
        fetch_n += 1
        hits = evidence_write_lines(text)
        if not hits:
            continue
        if any(tok in text for tok in GUARD_TOKENS):
            ok_n += 1
        else:
            viol.append((os.path.basename(p), hits[:3]))
    return viol, ok_n, fetch_n, scanned


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exec-dir", default=HERE)
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    d = args.exec_dir
    if not os.path.isdir(d):
        print("[CACHEGUARD:UNVERIFIED] 目录取不到: %s" % d)
        return 2
    paths = sorted(os.path.join(d, f) for f in os.listdir(d) if f.endswith(".py"))
    if not paths:
        print("[CACHEGUARD:UNVERIFIED] 扫描面为空（0 件 .py）=> 不得读成全部有守卫（R247）")
        return 2
    viol, ok_n, fetch_n, scanned = classify(paths)
    if not args.quiet:
        print("覆盖根：%s｜.py %d 件，其中取数面 %d 件（本门只盯 05-exec 自家脚本，不含受管根）"
              % (os.path.basename(d.rstrip(os.sep)) or d, scanned, fetch_n))
        print("形态面：写可复用证据且已声明守卫 %d ｜ 裸写违规 %d ｜ 取数但无证据写点 %d"
              % (ok_n, len(viol), fetch_n - ok_n - len(viol)))
        for f, hits in viol:
            print("  FAIL %s :: %s" % (f, hits[0]))
            print("       => 须声明守卫（cache_error 单件 / degrade_check 整面 / merge_note 留账）")
    if viol:
        print("[CACHEGUARD:FAIL] %d 件取数脚本裸写可复用证据缓存" % len(viol))
        return 1
    print(TOKEN + " 取数脚本的证据缓存写点全部声明守卫（%d 在面 / 取数面 %d）" % (ok_n, fetch_n))
    return 0


if __name__ == "__main__":
    sys.exit(main())
