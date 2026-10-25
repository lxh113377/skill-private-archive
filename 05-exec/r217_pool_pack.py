# -*- coding: utf-8 -*-
r"""r217_pool_pack.py — 把候选池缓存从 _temp 打包成入库资产（解 R213-1：离线复算不再站在会被清场的目录上）。

存在理由（r217 一手，含对我自己上轮一条待办的实测否证）：
  R213-1 记「第 ⑥ 段 --offline 靠 _temp/r114_search_cache/ 的池缓存；并行会话按扩展名清过 212 件（R189-2），
  清场那天离线复算会在第 ⑥ 段重新判红」。该条原写「须先量 family_bytes_max=491,520 与 repo_max=10,485,760」
  ⇒ **本轮实测发现那条前提引用错了预算面**：family_* 属 T1（记忆卷族，见 r150_volume_tiers.TIER_KEYS），
  缓存池属 T2 的 cache_*（cache_file_max=200 件 / cache_dir_max=52,428,800B）与产物级 artifact_max / any_file_max。
  按错预算算会得出「0.9MB 超 491KB ⇒ 不能入库」的错误结论；按真预算实测：
    · 散件形态 **不可入库** —— 池现有 414 件 > cache_file_max=200（该限正是为「827 个几十 KB .pyc」设的件数闸）；
    · 打包单件形态 **可入库** —— 明文 JSON 762,072B < any_file_max=1,048,576B（deflate 后 208,165B 更省，
      但二进制不可 diff / 不可 grep，故选明文）；
    · 消费方在**内存里合并读包**，不回写 414 个散件 ⇒ 不新增 cache_file_max 压力。

判据（三态，禁静默）：
  建包 rc=0 印条目数与字节；--check rc=0 包与活缓存一致 / rc=1 DRIFT（同名条目内容变了或包缺条目）；
  活缓存目录不存在或为空 ⇒ rc=2 且不写包（禁把零输入当「无需打包」）。

口径红线：
  · 包只是**只读输入面**：联网时新结果仍写散件目录（增量），包不自动更新 ⇒ 包陈旧不会造成假绿，
    因为 load_cache 合并时**散件覆盖包**（新数据优先），且 replacement_scan 的 api_calls/cache_hits 仍如实入产物；
  · 本件不新增凭据、不放宽任何判据、不改 r114 的判定逻辑（只在 load_cache 多读一个面）；
  · 包内容 = 缓存原样 JSON，不含凭据；生成前逐条 json 解析，坏条目跳过并计数（不把坏件塞进包）。

用法：
  python 05-exec/r217_pool_pack.py                 # 建包并入库
  python 05-exec/r217_pool_pack.py --check          # 比对包与活缓存（只读，不写）
  python 05-exec/r217_pool_pack.py --out 件         # 指定包路径
"""
import argparse
import glob
import io
import json
import os
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CACHE_DIR = os.path.join(ROOT, "_temp", "r114_search_cache")
PACK_DEFAULT = os.path.join(ROOT, "06-benchmark", "pool_cache_r217.json")
TOK_OK = "[POOLPACK:PASS]"
TOK_DRIFT = "[POOLPACK:DRIFT]"
TOK_UNV = "[POOLPACK:UNVERIFIED]"


def read_entries(cache_dir=CACHE_DIR):
    """散件目录 -> {key: doc}；坏条目跳过并计数（不把坏件塞进包，也不静默当命中）。"""
    out, bad = {}, 0
    if not os.path.isdir(cache_dir):
        return out, 0, 0
    files = sorted(glob.glob(os.path.join(cache_dir, "*.json")))
    for f in files:
        key = os.path.basename(f)[:-5]
        try:
            out[key] = json.load(io.open(f, encoding="utf-8-sig", errors="replace"))
        except (OSError, ValueError):
            bad += 1
    return out, len(files), bad


def load_pack(path):
    try:
        d = json.loads(io.open(path, encoding="utf-8-sig", errors="replace").read())
    except (OSError, ValueError):
        return None
    return d if isinstance(d, dict) else None


def main(argv=None):
    ap = argparse.ArgumentParser(description="候选池缓存打包入库（解离线复算对 _temp 的依赖）")
    ap.add_argument("--out", default=PACK_DEFAULT)
    ap.add_argument("--check", action="store_true", help="只比对包与活缓存，不写")
    ap.add_argument("--cache-dir", default=CACHE_DIR)
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass
    live, nfiles, bad = read_entries(args.cache_dir)
    if not live:
        print("%s 活缓存目录无可用条目（%s；文件 %d 个、坏件 %d）⇒ 零输入不建包也不判绿（R247）"
              % (TOK_UNV, os.path.relpath(args.cache_dir, ROOT), nfiles, bad))
        return 2
    if args.check:
        pk = load_pack(args.out)
        if not pk or "entries" not in pk:
            print("%s 包不可读或缺 entries ⇒ 离线面不可用（禁读成「无需包」）：%s"
                  % (TOK_UNV, os.path.relpath(args.out, ROOT)))
            return 2
        pe = pk["entries"]
        missing = [k for k in live if k not in pe]
        changed = [k for k in live if k in pe and json.dumps(pe[k], sort_keys=True) != json.dumps(live[k], sort_keys=True)]
        if missing or changed:
            print("%s 包缺条目 %d｜内容不一致 %d｜例：%s"
                  % (TOK_DRIFT, len(missing), len(changed), ",".join((missing + changed)[:4]) or "（无）"))
            return 1
        print("%s 包与活缓存逐条一致（活 %d 条 / 包 %d 条，包内额外条目 %d 条属正常——缓存被清后包仍留着历史命中）"
              % (TOK_OK, len(live), len(pe), len([k for k in pe if k not in live])))
        return 0
    doc = {
        "schema": "pool-cache-r217-v1",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00"),
        "cmd": "python 05-exec/r217_pool_pack.py",
        "source_dir": os.path.relpath(args.cache_dir, ROOT).replace(os.sep, "/"),
        "entries_n": len(live), "skipped_bad_n": bad,
        "note": "只读输入面：消费方（r114_replacement_scan.load_cache）在内存里合并「包 + 散件」，散件覆盖包；"
                "本件不新增凭据、不改判定逻辑；缓存被清场后离线复算仍可用即靠本件。",
        "entries": live,
    }
    tmp = args.out + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    os.replace(tmp, args.out)
    size = os.path.getsize(args.out)
    if not args.quiet:
        print("入册条目 %d（散件 %d 个，坏件跳过 %d 个）" % (len(live), nfiles, bad))
        print("包字节 %d｜any_file_max=1,048,576 未超=%s｜散件形态若入库会撞 cache_file_max=200（现 %d 件）"
              % (size, size < 1048576, nfiles))
    print("%s 包 -> %s" % (TOK_OK, os.path.relpath(args.out, ROOT)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
