---
name: code-review
description: Review code changes only against the original requirement document. Finds code that contradicts the spec, behaviour the spec never asked for, in-scope rules that are missing or untested, and code built on open decisions, each cited as spec ID and source line. Use when asked to review code or a PR against the spec, PRD, FSD or requirements, check requirement coverage, or verify that a change implements a requirement ID.
---

# grepable:code-review

A review with one question: **does this code do what the original requirement document says, and nothing
else?** Style, performance and general best practice are out of scope. Leave them to other reviewers.

## Spec location (shared by all grepable skills)
Find the requirement document in this order and use the first that exists:
1. A path the user gives in the request.
2. A `Spec source: <path>` line in the repo's `CLAUDE.md` or `AGENTS.md`.
3. `docs/original-requirement.md` (the default).

If none exists, stop and ask for the path. Never pick a "similar-looking" document yourself.
Shards live in the `Spec shards: <dir>` line if present, otherwise `docs/fsd/`.

**Reading the spec.** If shards exist and are fresh, use `INDEX.md` and `ID-MAP.md` to find the section,
then read that shard (its content is a byte-exact copy of the source). Shards are stale when the source
changed after `INDEX.md` was generated (compare `git log -1` or file times); then re-run `grepable:shard` or read the source directly. With no
shards, grep the source for the ID or term and read the whole section around it.

**Citations** always point at the source: `LN-03.R2 (docs/original-requirement.md:L103)`. `ID-MAP.md`
gives the source line for every ID.

## Steps

1. **What to review.** Use the target the user gives (PR, branch, commit, files). Otherwise review the
   uncommitted changes plus the current branch against its base (`git diff <base>...HEAD` and
   `git diff`). Read changed files in full where needed to understand behaviour.

2. **Map code to spec.** For each observable behaviour in the change (inputs accepted or refused, values,
   limits, messages, codes, state changes, permissions), find the spec ID that governs it. Also list the
   spec IDs in scope for this change (from the PR description, commit messages, test names, or the
   section the code clearly implements), so missing work is visible.

3. **Classify findings.**

   | Type | Meaning |
   |---|---|
   | **MISMATCH** | Code contradicts the spec (a different limit, code, message, rule or permission). |
   | **UNSPECIFIED** | Observable behaviour with no spec citation: an invented default, limit, fallback, message or rule. |
   | **MISSING** | An in-scope rule or acceptance criterion that the change does not implement. |
   | **UNTESTED** | Implemented, but no test exercises that rule or criterion. |
   | **OPEN ITEM** | Code built on a spec item marked `Decision pending`, `TBD` or `NOT IN SPEC`. |

   Only report what you can show: quote the spec text verbatim and point at the code line. If the spec is
   ambiguous, report it as a question, not as a defect in the code.

4. **Report.**

   | # | Type | Code (file:line) | Spec ID (source line) | Spec says (verbatim) | Code does |
   |---|---|---|---|---|---|

   Then:
   - **Coverage**: each in-scope spec ID with ✅ implemented and tested / ⚠ untested / ❌ missing.
   - **Questions for the spec owner**: ambiguities and gaps found while reviewing.
   - **Verdict**: *Matches spec*, *Matches spec with gaps* or *Does not match spec*.

## Don't
- Don't report style, naming, performance or security issues here unless the spec states the rule.
- Don't treat existing code as the spec. If old code and the spec disagree, it is a MISMATCH.
- Don't fix the code unless the user asks. This skill reviews.
- Don't edit the requirement document or the shards.
