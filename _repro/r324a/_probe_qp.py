import subprocess
git = r"C:/Program Files/Git/bin/git.exe"
def tree(qp):
    argv = [git] + (["-c","core.quotepath=false"] if qp else []) + ["-C","D:/global_skills","ls-tree","-r","-l","HEAD"]
    r = subprocess.run(argv, capture_output=True)
    rows = 0; quoted = 0; out = {}
    for line in r.stdout.decode("utf-8","replace").splitlines():
        if chr(9) not in line: continue
        meta, rest = line.split(chr(9),1)
        p = meta.split()
        if len(p) != 4: continue
        rows += 1
        if rest.startswith(chr(34)) and rest.endswith(chr(34)): quoted += 1
        s = p[3]; out[rest] = int(s) if s.isdigit() else 0
    return rows, quoted, len(out), r.returncode
print("quotepath_off", tree(True))
print("quotepath_on ", tree(False))