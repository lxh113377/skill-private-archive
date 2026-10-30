# 上游吸收分卷 — cloudflare/security-audit-skill（R290，2026-10-30）

> 受控吸收：整卷正文**逐字**取自上游 `SKILL.md` 的下列行区间（谱系=独立实现，非本地 Trail of Bits 谱系的旧版 ⇒ 按 R265-3 走替换类、以本地为壳并入增量）。
> 上游坐标：`cloudflare/security-audit-skill` @ `c1c8a8c1471069fb0e188eeaff69b8e8db6564a8`（main，committer date 2026-09-14T19:28:54Z，license.spdx_id=MIT）—— 取值命令与输出见 `skill焚诀/自建skill优化 仓的 `_repro/r290s/coords.json``。
> 吸收理由 = 换装前实测「三词命中 0」：`OS-enforced sandbox` / `write isolation` / `coverage-ledger`（复算（在 skill焚诀/自建skill优化 仓根）`python -B _repro/r290s/capability_probe.py`）。
> 相对链接纪律：本卷正文不含 markdown 相对链接（选取区间时实测 mdlinks=0；上游其余章节引用 RECONNAISSANCE.md / ATTACK-CLASSES.md 等未随本件引入 ⇒ 引用必成死链，故不并入），见 R285-1 / R289-5 第⑧步。

## 吸收块与上游行区间对照

| 本地节 | 上游 SKILL.md 行区间 | 行数 | 字节 |
|--------|----------------------|------|------|
| Universal execution safety | 31-42 | 12 | 2077 |
| Full audit setup / Write isolation | 54-81 + 84-86 | 31 | 3788 |
| Coverage and prior runs | 92-93 + 96-105 | 12 | 1959 |

---

## Universal execution safety（上游 L31-42 逐字）

## Universal execution safety

These rules apply in both operating modes. Source inspection is read-only. Run target-controlled builds, tests, processes, browsers, emulators, fuzzers, and fixture processing only inside an OS-enforced sandbox that provides all of these controls:

- no external network; use only an isolated loopback namespace when the check needs local client/server traffic;
- an empty environment populated from an explicit allowlist with safe values, with scratch-local `HOME`, temporary directories, and caches;
- a read-only target and toolchain, with the target-controlled process able to write only inside its assigned `scratch/` directory; and
- explicit low CPU, memory, process, file-size, disk, and wall-clock limits.

The agent, outside the target-controlled process, may make a disposable source copy in an assigned `scratch/` directory when a build must write beside source. In guidance mode, do not retain target-controlled files. In full audit mode, only trusted parent-side code may promote the minimum non-secret result to retained `artifacts/` using the procedure under Write isolation. Never expose a retained output directory (other than the agent's own assigned `scratch/`), another agent's directory, the host home directory, credentials, sockets, or shared services to target code. Do not install dependencies or let builds fetch them. Use only tools and dependencies already available locally. If every control cannot be enforced, do not execute target code: report the missing sandbox capability as a needs-validation blocker and give a safe validation plan.

Use dummy principals, fixtures, and secrets. Do not probe deployed endpoints, external services, shared infrastructure, production identities, other users' data, or live control planes. Do not test availability against a live or shared process, publish artifacts, alter releases, spend paid API quota, or continue beyond the minimum local effect needed to establish a defect. If the decisive fact is outside source or the sandboxed fixture, report it as needing validation.

## Full audit setup — Write isolation（上游 L54-81 逐字）

### Write isolation

The parent creates and is the only writer of shared run files:

- `run-metadata.json`
- `architecture.md`
- `coverage-ledger.json`
- `findings.json`
- `REPORT.md`
- `FINDINGS-DETAIL.md`
- `NEEDS-VALIDATION.md`

Each hunter or verifier receives a unique root under `<output-dir>/agents/<agent-id>/`, with separate `scratch/` and `artifacts/` directories. Canonical agent IDs match `^[a-z0-9][a-z0-9_-]{0,63}$` and must not equal a Windows device name such as `con`, `prn`, `aux`, `nul`, `com1` through `com9`, or `lpt1` through `lpt9`. Lowercase IDs prevent case-fold collisions. The agent and every target-controlled process may write only to `scratch/`; retained `artifacts/` is parent-owned, is never exposed to the sandbox, and is writable only by trusted parent-side promotion code. Agents may not change shared files, target source, retained artifacts, or another agent's directory. Do not use `/tmp` or the host home directory as a writable fallback.

Before execution, the parent opens and retains trusted, non-inheritable directory descriptors for the agent's `scratch/` and `artifacts/` roots, and records an allowlist of expected scratch-relative artifact files plus explicit per-file and cumulative byte limits. Never pass those descriptors to the agent or sandbox. After the sandbox and all its processes terminate, trusted parent-side code promotes each allowlisted file separately:

1. Validate the declared relative path: reject absolute, empty, `.`, `..`, or symlinked components.
2. Walk each parent component from the retained scratch-root descriptor with no-follow directory-relative operations; never reopen by path.
3. Open the leaf no-follow and nonblocking.
4. Verify with `fstat` that it is a regular file with link count exactly one and within the recorded per-file and cumulative byte limits.
5. Enforce those limits again while reading from that descriptor.
6. Copy exactly the verified size, repeat `fstat`, and reject a changed identity, type, link count, or size.
7. For the destination, walk every parent component from the retained artifacts-root descriptor with no-follow directory-relative operations; require each existing component to be a real directory, and create any missing directory exclusively before reopening and verifying it no-follow.
8. Create the leaf exclusively without following links, verify that the opened destination is a regular file with link count exactly one, and copy from the verified source descriptor without reopening either path.
9. Use equivalent race-safe APIs on non-POSIX systems.
10. Never recursively copy or glob scratch, extract an archive into artifacts, or open or promote a symlink, FIFO, socket, device, directory, hard-linked file, changing file, or file that exceeds its bound.
11. If any check is unavailable, cannot be enforced, or fails, discard the scratch entry; if it is decisive evidence, retain `needs_validation` with the exact promotion blocker.


For a reproduced check, record the command, exact test input, sandbox limits, and only the allowlisted environment variable names plus safe non-secret values needed to reproduce it. Never capture or copy the ambient environment, inherited variables, credential values, authentication state, or unrelated host paths. Launch from an empty environment rather than trying to redact one after execution.

Before delegation, the parent writes `run-metadata.json` with at least `run_id`, `repo`, `target`, `source_ref`, `profile`, `scope_paths`, `budget` (null if unset), `execution_policy: "sandboxed-source-and-local-only"`, selected companion files, prior-run paths, shared-file owners, and `run_status: "in_progress"`. Update metadata only when those facts change; candidate state belongs in the coverage ledger and `findings.json`.

## Coverage and prior runs（上游 L92-93 与 L96-105 逐字）

### Coverage and prior runs

If prior runs exist, read every compatible `coverage-ledger.json` and `findings.json` before planning the current run:

1. Compare the relevant current source with each prior record and unit. A prior source ref alone is not evidence that a path is unchanged.
2. Carry a prior `confirmed` record into the current candidate set only when its relevant source and conditions are unchanged and its evidence still meets the current contract. Link it to a current ledger unit seeded `planned`, preserve its fingerprint, exclude only that carried root cause from hunters, and send the carried record through the current final verification path; the Phase 3 verifier that re-checks it becomes that unit's assignment owner and moves it to `candidate`.
3. When relevant source for a prior `confirmed` record changed, create a current planned revalidation unit. Do not put that record on the hunter exclusion list. It remains confirmed only if current independent validation establishes the current path and result.
4. Make prior `needs_validation`, `deferred`, `blocked`, `out_of_scope`, and any changed-source unit current work. A still-external `needs_validation` record may be carried only after the current source trace is checked and linked by fingerprint to a current `planned` unit whose verifier re-check supplies its owner and evidence; the record keeps the unresolved blocker. These prior states never suppress a current unit.
5. A prior same-source covered unit may inform priority, but it remains visible in the current ledger. A prior `rejected` record suppresses only the unchanged failed claim, not coverage of its unit; changed evidence creates current work.
6. Read the prior profile and scope. A prior `quick` or scoped ledger contributes only its recorded evidence and gaps, never an implied "rest is fine."

If no prior ledger exists, say so in the final coverage statement. Never imply that one run exhausts the target.

## Version history (cont.)

- **V2.1.0** (2026-10-30) — 本卷新建：逐字吸收上述三段；未并入的其余上游章节理由见上表纪律行。
