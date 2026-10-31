# -*- coding: utf-8 -*-
# r314b 证据复核件：哈希/字节双向复算 + verbatim 逐字回归 + 内嵌负控两腿
# 判据 = 末行 [R314B:EVID]；--selftest 加跑 NEG-A（改一字必判 false）与 NEG-B（删一条必 -1）
import copy, hashlib, json, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))
EV = os.path.join(BASE, "evidence")
NL = chr(10)

def load_pair():
    with open(os.path.join(BASE, "absorb_evidence.json"), encoding="utf-8") as fh:
        data = json.load(fh)
    with open(os.path.join(EV, "upstream_SKILL.md"), "rb") as fh:
        up = fh.read()
    with open(os.path.join(EV, "local_SKILL.md"), "rb") as fh:
        lo = fh.read()
    return data, up, lo

def blob_sha(buf):
    # git blob 哈希 = sha1("blob <字节数>" + NUL + 内容)，与 git rev-parse 口径一致
    head = b"blob " + str(len(buf)).encode("ascii") + bytes([0])
    return hashlib.sha1(head + buf).hexdigest()

def verify(data, up, lo):
    # 全量复算：sha256/bytes/blob_sha 双件 + 每节 verbatim 按行区间回切重比
    errs = []
    upl = up.decode("utf-8").split(NL)
    lol = lo.decode("utf-8").split(NL)
    u, l = data["upstream"], data["local"]
    if hashlib.sha256(up).hexdigest() != u["sha256"]:
        errs.append("upstream-sha256")
    if hashlib.sha256(lo).hexdigest() != l["sha256"]:
        errs.append("local-sha256")
    if blob_sha(up) != u["blob_sha"]:
        errs.append("upstream-blob-sha")
    if blob_sha(lo) != l["blob_sha"]:
        errs.append("local-blob-sha")
    if len(up) != u["bytes"]:
        errs.append("upstream-bytes")
    if len(lo) != l["bytes"]:
        errs.append("local-bytes")
    for inc in data["increments"]:
        a, b = inc["src_lines"]
        if NL.join(upl[a - 1:b]) != inc["verbatim"]:
            errs.append("verbatim-" + inc["id"])
    for item in data["local_only"]:
        a, b = item["dst_lines"]
        if NL.join(lol[a - 1:b]) != item["verbatim"]:
            errs.append("verbatim-" + item["id"])
    return errs

def main():
    data, up, lo = load_pair()
    errs = verify(data, up, lo)
    ok = not errs
    if "--selftest" in sys.argv:
        # 腿A：增量 verbatim 改一个字 -> 复核必须出非空错误（即 verbatim_all_reverified=false）
        d2 = copy.deepcopy(data)
        v0 = d2["increments"][0]["verbatim"]
        tail = v0[-1]
        d2["increments"][0]["verbatim"] = v0[:-1] + ("X" if tail != "X" else "Y")
        errs_mut = verify(d2, up, lo)
        leg_a = ok and bool(errs_mut)
        # 腿B：删一条本地独有 -> 计数必须 -1 且剩余仍全绿
        d3 = copy.deepcopy(data)
        removed = d3["local_only"].pop()
        errs_del = verify(d3, up, lo)
        n0 = len(data["local_only"])
        n1 = len(d3["local_only"])
        leg_b = (n1 == n0 - 1) and (not errs_del)
        print("[R314B:NEG-A] INC-01 verbatim last-char flip -> reverified=false expected=false -> " + ("PASS" if leg_a else "FAIL"))
        print("[R314B:NEG-B] dropped " + removed["id"] + " -> local_only " + str(n0) + " -> " + str(n1) + " expected-minus-one -> " + ("PASS" if leg_b else "FAIL"))
        if not (leg_a and leg_b):
            print("[R314B:SELFTEST] FAIL")
            sys.exit(1)
    for e in (errs if not ok else [])[:24]:
        print("[R314B:ERR] " + e)
    print("[R314B:EVID] increments=" + str(len(data["increments"])) + " local_only=" + str(len(data["local_only"])) + " upstream_blob=" + data["upstream"]["blob_sha"][:12] + " verbatim_all_reverified=" + ("true" if ok else "false") + " unknown=" + str(len(data["unknown"])))
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
