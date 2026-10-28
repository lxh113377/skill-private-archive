#!/usr/bin/env bash
# r260 证据采集器：把「跑前 / 跑后」的 git status --porcelain 与 tracked 写面 sha256 落到 _temp/。
# 为什么要两样都取：porcelain 是任务判据（逐字相同）；sha 是加强判据 ——
# 06-benchmark/local_frontmatter.json 在我开工前已被上一批跑红（基线即 M），
# 只看 status 行会「前后都是 M」看不出是否改写；sha 能区分这两种情形。
set -u
cd "$(dirname "$0")/.." || exit 9
export PYTHONPYCACHEPREFIX=/tmp/pycache_r260b
TAG="$1"
git status --porcelain > "_temp/r260b_status_${TAG}.txt"
{
  echo "STATUS_LINES=$(wc -l < "_temp/r260b_status_${TAG}.txt")"
  echo "RUN_AT=$(date -Iseconds)"
  for f in 06-benchmark/local_frontmatter.json 06-benchmark/pool_cache_r217.json 06-benchmark/replacement_matrix_shadowstrict.json; do
    if [ -f "$f" ]; then echo "SHA $(sha256sum "$f" | cut -c1-64) $f"; else echo "SHA ABSENT $f"; fi
  done
} > "_temp/r260b_meta_${TAG}.txt"
cat "_temp/r260b_meta_${TAG}.txt"
