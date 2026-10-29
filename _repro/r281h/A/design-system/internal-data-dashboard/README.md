# README.md - how to pick this design system up in another session (arm A)

Slug: `internal-data-dashboard`  |  Dir: `design-system/internal-data-dashboard/`
Process authority used: `_temp/r281h/A/SKILL.md` (ui-ux-pro-max v1.2.0, arm-local copy).

## Files and who produced them

| File | Producer | Purpose |
|------|----------|---------|
| `MASTER.md` | generator (`search.py --design-system --persist`) | global rules in the shape the skill prescribes |
| `pages/dashboard.md` | generator, through `_ds_page_wrapper.py` | page overrides; beats MASTER.md per MASTER.md:3-5 |
| `TOKENS.md` | arm A | the five required token classes, with a provenance tag on every value |
| `CONTRAST-AUDIT.md` | arm A | 139 measured ratios; the 6 generator values that failed and their replacements |
| `../_evidence*.py`, `../_evidence*_out.txt` | arm A | the judgment scripts and their saved output (recomputable) |
| `../_gen_stdout.txt` | generator | verbatim stdout of every generator/search run, 8 segments, each ending `RC=0` |
| `../_exec_log.md`, `../_triage.md` | arm A | command ledger with rc, and the Triage decisions |

## Read order in a new session

1. `MASTER.md`  2. `pages/dashboard.md` (if building that page)  3. `TOKENS.md` (numbers are authoritative here)
4. `CONTRAST-AUDIT.md` (verification).

**Conflict rule**: where `MASTER.md` and `TOKENS.md` disagree - button fill, focus ring, input border,
delta colors, chart ramp - `TOKENS.md` wins, because those four places are generator values that
measured below the bar and were replaced; the evidence is rows 1-6 of `CONTRAST-AUDIT.md`. This is a
documented, measured override, not an edit for taste.

## Regenerate (read-only on the skill dir, writes land in the arm dir)

```bash
PY=/c/Users/37533/.workbuddy/binaries/python/envs/default/Scripts/python.exe
S=/d/global_skills/ui-ux-pro-max/scripts
cd /c/Users/37533/Desktop/workspace/skill焚诀/_temp/r281h/A
Q="internal data analytics dashboard admin tables charts metrics filters"
"$PY" "$S/search.py" "$Q" --design-system --persist -p internal-data-dashboard -o . -f markdown
"$PY" _ds_page_wrapper.py "$Q" --persist -p internal-data-dashboard --page dashboard -o . -f markdown
```

The second line must go through `_ds_page_wrapper.py`: upstream `design_system.py:925` executes
`from .core import search`, which raises `ImportError: attempted relative import with no known parent
package` whenever `search.py` is launched as a plain script (measured rc=1 twice in _exec_log.md rows 5
and 10), so `--page` output can never be written by the documented command line. The wrapper registers
the scripts directory as a package in `sys.modules` and sets `design_system.__package__` to that name,
so the relative import resolves; it writes zero bytes into `D:/global_skills`.
Gotcha: the path inside the wrapper must be Windows form (`D:/...`) - the MSYS form (`/d/...`) is
invisible to this Windows CPython (measured rc=1, _exec_log.md row 8).

## Acceptance criteria (rerunnable)

```bash
cd /c/Users/37533/Desktop/workspace/skill焚诀/_temp/r281h/A
ls design-system/internal-data-dashboard design-system/internal-data-dashboard/pages
PY=/c/Users/37533/.workbuddy/binaries/python/envs/default/Scripts/python.exe
for f in _evidence.py _evidence2.py _evidence3.py _evidence4.py _evidence5.py; do "$PY" "$f" >/dev/null 2>&1 || echo "FAIL $f"; done; echo ALL_EVIDENCE_OK
grep -c "J]" design-system/internal-data-dashboard/TOKENS.md
```

Expected last line: `ALL_EVIDENCE_OK`, and the `ls` listing must contain `MASTER.md`,
`pages/dashboard.md`, `TOKENS.md`, `CONTRAST-AUDIT.md`, `README.md`.
The `grep -c` line counts values honestly tagged as design judgment (no local source) - it should be
non-zero, because pretending those numbers came from a script is the failure mode this file forbids.

Negative control (proves the gate has teeth, it is not constant green):

```bash
grep -q NO_SUCH_TOKEN_XYZ design-system/internal-data-dashboard/TOKENS.md; echo NEG_RC=$?
```

Expected `NEG_RC=1`. If that returns 0 the gate is broken and the green above means nothing.

## Coverage matrix (the five classes the task requires)

| Class | Present | Location in TOKENS.md |
|-------|---------|------------------------|
| color tokens | yes | 24-129: 1.1 semantic roles (16 tokens), 1.2 status (9), 1.3 chart ramps (10 light + 6 dark + heatmap + waterfall), 1.4 dark theme (7) |
| spacing scale | yes | 131-190: 8 steps (4/8/12/16/24/32/48/64px) + 24 component dimensions + elevation ladder |
| typography (family + type scale) | yes | 192-261: 3.1 primary pair + 3 alternates + weights + CSS import; 3.2 eight-step size scale + leading + numeric formatting |
| component states | yes | 263-389: 4.0 timing/motion, 4.1-4.2 buttons, 4.3 inputs, 4.4 table, 4.5 KPI card, 4.6 chart card, 4.7 modal/toast, 4.8 sidebar - each with default/hover/focus/disabled/loading/error (+empty for containers) |
| breakpoints | yes | 391-429: 8 named min-width stops with column counts and layout contracts, plus layout tokens |

## Known limits (no loose ends)

- `design_system.py` CLI has no `--persist` flag (row 3 of _exec_log.md proves it from `--help`);
  persistence is only reachable through `search.py` or by importing `generate_design_system`.
- No real repo, screenshot or Figma was available to arm A, so the implementation-plan deliverable
  (SKILL.md:31) stops at retrieval order + regeneration + acceptance commands; there is no file-level
  diff against an existing codebase.
- The generator picked a landing-page pattern for an admin dashboard (`MASTER.md:166-170`,
  Before-After Transformation, CTA above the fold). That is a retrieval artifact, not a UX judgment for
  this product; `pages/dashboard.md:16-22` is the part that actually fits, and TOKENS.md 5 is what to build.
