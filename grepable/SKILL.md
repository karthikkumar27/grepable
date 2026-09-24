---
name: grepable
description: Split a large FSD, PRD or SRS markdown spec into indexed section files with INDEX.md and ID-MAP.md, so the agent reads only the relevant section and cites requirement IDs as file:line instead of guessing. Use when asked to shard, split, chunk, index or re-index a spec or requirements document, make a spec greppable, map requirement IDs, or when docs/original-requirement.md changes.
---

# grepable

Splits one large spec (FSD, PRD, SRS) into one file per section, plus:
- `INDEX.md`: section map (what each file covers, IDs defined, line ranges, open-item count).
- `ID-MAP.md`: every requirement ID / rule / code / decision / question -> shard `file:line` and source line.

Every shard starts with `<!-- source: <path>:L<start>-L<end> -->`, so citations trace back to the original.
The script is deterministic: it never rewrites or summarises spec text. It copies byte ranges and
verifies that the shards join back into the source exactly (lossless check).

## Defaults
- Source: `docs/original-requirement.md` · Output: `docs/fsd/`
- Script: `scripts/grepable.py` **in this skill's own directory** (bundled). Run it with the absolute
  path of this skill directory, e.g. `python3 "$SKILL_DIR/scripts/grepable.py" ...`. If the repo has its
  own `scripts/grepable.py`, prefer that one so the repo pins the version.
- Use the paths the user gives if different. Run commands from the repo root so markers show repo-relative paths.

## Steps

1. **Discover ID families.**
   `python3 <skill-dir>/scripts/grepable.py docs/original-requirement.md --discover`
   Read the candidate families (e.g. `LN-NN`, `BLK-NNN`, `DNN`/`JNN`/`QNN` as table first cells).

2. **Choose ID patterns.** Default patterns cover `AREA-NN`, `CODE-NNN`, `AREA-NN.Rn` and `AC-AREA-NN-n`.
   If the doc also uses bare-letter IDs (D1, J5, Q6), add a pattern for them. Always keep the
   `(?<![\w-])…(?![\w-])` boundaries so `AC-LN-01-1` is not also counted as `LN-01`.
   Typical full set:
   ```
   --id-pattern '(?<![\w-])[A-Z]{1,5}-\d{1,4}(?:\.R\d+)?(?![\w-])'
   --id-pattern '(?<![\w-])AC-[A-Z]{1,5}-\d{1,4}-\d{1,3}(?![\w-])'
   --id-pattern '(?<![\w-])[DJQ]\d{1,2}(?![\w-])'
   ```
   (Passing any `--id-pattern` replaces the defaults, so pass all of them.)

3. **Dry run.** Same command with `docs/fsd --dry-run`. Check:
   - Shard sizes: if one shard is over ~400 lines, re-run with `--max-lines 400` (it re-splits at `###`).
     If the section uses bold pseudo-headings instead of `###`, it cannot be split further; tell the user
     and suggest converting those to `###` headings in the source.
   - `Lossless check: PASS`. If FAIL, stop and report; do not write.
   - Duplicate definitions: report them; they are real spec defects (two places define one ID).

4. **Write.** Re-run without `--dry-run`. Add `--force` only when `docs/fsd/` already holds generated
   shards from this script (it deletes the old `.md` files there first). If `docs/fsd/` contains
   hand-written files, stop and ask before using `--force`.

5. **Report to the user** (short):
   - Number of shards, IDs defined, lossless PASS.
   - Spec defects found:
     - Duplicate IDs.
     - "Referenced but never defined" IDs from `ID-MAP.md`. Split these into (a) IDs owned by another
       document, such as a technical design's ADRs, and (b) IDs that only appear in prose (a real gap: no single definition to grep).
     - Shorthand ranges the script expanded (rows marked "written as `BLK-002 / 003`"). Recommend
       writing each ID in full in the source.
   - Sections with a ⚠ count (Decision pending / TBD / NOT IN SPEC): not buildable yet.

6. **Don't** edit shard files, summarise the spec, or add requirements. If the user wants the spec itself
   improved (atomic rules, IDs for prose), that is a separate conversion task using their FSD template;
   after it, re-run this skill.

## Re-sharding
Whenever the source changes, re-run steps 3–4 with the same patterns (record the command in the repo,
e.g. a `make spec` target or a line in CLAUDE.md). Stale shards are worse than none.
