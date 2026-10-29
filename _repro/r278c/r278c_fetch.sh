#!/usr/bin/env bash
# r278c_fetch.sh -- fail-closed pre-change text fetcher (read-only git plumbing)
# usage: r278c_fetch.sh <ref> <relpath> <outfile>
# gates, in order: ref resolves to a commit; path exists in that tree;
#                    git show exits 0; output file is non-empty.
# any failing gate => print UNVERIFIED + exit non-zero.
# This is what keeps a bad sha from being read as "before = 0 lines".
set -u
REPO=/d/global_skills
ref="${1:-}"
rel="${2:-}"
out="${3:-}"
if [ -z "$ref" ] || [ -z "$rel" ] || [ -z "$out" ]; then
  echo "UNVERIFIED reason=usage ref/rel/out required"; exit 2
fi
resolved=$(git -C "$REPO" rev-parse --verify "${ref}^{commit}" 2>/dev/null)
if [ $? -ne 0 ] || [ -z "$resolved" ]; then
  echo "UNVERIFIED reason=ref-not-found ref=${ref}"; exit 3
fi
if ! git -C "$REPO" cat-file -e "${ref}:${rel}" 2>/dev/null; then
  echo "UNVERIFIED reason=path-not-in-tree target=${ref}:${rel}"; exit 4
fi
tmp=$(mktemp)
git -C "$REPO" show "${ref}:${rel}" > "$tmp" 2>/dev/null
rc=$?
if [ $rc -ne 0 ]; then
  echo "UNVERIFIED reason=git-show-rc-nonzero rc=${rc} target=${ref}:${rel}"; rm -f "$tmp"; exit 5
fi
if [ ! -s "$tmp" ]; then
  echo "UNVERIFIED reason=empty-output target=${ref}:${rel}"; rm -f "$tmp"; exit 6
fi
mkdir -p "$(dirname "$out")"
mv "$tmp" "$out"
blob=$(git -C "$REPO" rev-parse "${ref}:${rel}")
bytes=$(wc -c < "$out")
bytes=${bytes// /}
echo "OK ref=${ref} commit=${resolved} target=${rel} out=${out} bytes=${bytes} blobsha=${blob}"
