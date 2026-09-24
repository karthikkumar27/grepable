---
name: tdd
description: Test-driven development driven only by the original requirement document. Lists every rule in a spec section, writes one failing test per testable rule cited to its source line, then the minimum code to pass, and records gaps as NOT IN SPEC instead of inventing tests. Use when asked to do TDD, write tests from the spec, PRD, FSD or requirements, implement a requirement test-first, cover a spec section or the whole spec with tests, or check that code conforms to the spec.
---

# grepable:tdd

Red → green → refactor, where **every test traces to a line of the original requirement document**.
The spec decides what is tested. Code, habit and "common practice" never do.

## Spec location (shared by all grepable skills)
Find the requirement document in this order and use the first that exists:
1. A path the user gives in the request.
2. A `Spec source: <path>` line in the repo's `CLAUDE.md` or `AGENTS.md`.
3. `docs/original-requirement.md` (the default).

If none exists, stop and ask for the path. Never pick a "similar-looking" document yourself.
Shards live in the `Spec shards: <dir>` line if present, otherwise `docs/fsd/`.
If the user points at a shard, `INDEX.md` or the shards folder, the source is the path in the shard's
line-1 marker (`<!-- source: <path>:L<start>-L<end> -->`).

**Reading the spec.** If shards exist and are fresh, use `INDEX.md` and `ID-MAP.md` to find the section,
then read that shard (its content is a byte-exact copy of the source). Shards are stale when the source
changed after `INDEX.md` was generated (compare `git log -1` or file times); then re-run `grepable:shard`
or read the source directly. With no shards, grep the source for the ID or term and read the whole
section around it.

**Citations always point at the source document, never at a shard.**
- With IDs: `LN-03.R2 (docs/original-requirement.md:L103)`. `ID-MAP.md` gives the source line.
- Without IDs: `docs/original-requirement.md:L103`. From a shard, source line = marker start + shard
  line − 2. If the spec has no IDs at all, say so once and suggest adding them; then proceed with lines.

## Steps

1. **Scope and mode.**
   - Scope: the IDs, section(s) or feature the user names. For "the whole spec" or "all sections", work
     one section at a time in `INDEX.md` order and report after each (see *Coverage ledger*).
   - Existing code: check whether the behaviour is already implemented or tested. If it is, ask once:
     *gap-check* (add tests only for rules with no test today) or *full* (one test per rule, ignoring
     existing tests). Record the answer in the ledger.

2. **Rule inventory.** Read the whole section and split it into atomic rules: every sentence in prose,
   **every sentence inside a table cell**, every bullet, every value in a list of allowed values. A cell
   or sentence that states two things is two rules. Give each a label (its ID, or `L<source line>`, with
   `a`/`b` for several rules on one line) and one outcome:

   | Outcome | Meaning |
   |---|---|
   | **TEST** | Observable behaviour the code can be tested for |
   | **NOT TESTABLE** | Operator instructions, setup steps or absence claims with no code path (give the reason) |
   | **DEFERRED** | Depends on a later section; name it (e.g. "→ §10"). It stays open in the ledger |
   | **OPEN** | Marked `Decision pending`, `TBD` or `NOT IN SPEC`, or ambiguous. Becomes a question |

   Before moving on, re-read the section line by line against the inventory. Every normative line must
   appear in it.

3. **Test plan. Show it in chat before the first file write**, even if there is nothing to ask:

   | Rule (source line) | Rule text (verbatim) | Outcome | Test name |
   |---|---|---|---|

   Below it list the **NOT IN SPEC** items: things the code needs but the spec does not state
   (messages, limits, defaults, error handling), plus any conflicts. If there are OPEN items, NOT IN SPEC
   items the tests would depend on, or conflicts, ask before continuing. Otherwise continue.

4. **Red.** Write one test per TEST row with the project's existing test framework and conventions.
   Put the rule label in the test name or docstring and the source line in a short comment.
   - Assert **only values the spec states**, copied verbatim. If the spec names an outcome but no text
     (for example, "refused with a message"), assert the outcome (the error type, the status, the fact
     that nothing was saved) and never the wording the code happens to use.
   - Tests for new code must fail **on the assertion**. An import error or missing function is not red:
     add a stub (the signature, raising "not implemented") so the tests collect, then watch them fail.
   - Tests for code that already exists will pass on the first run. That proves nothing until you show
     the test can fail: break the behaviour temporarily (change the value or condition the rule is about),
     confirm that this test fails, then revert. Mark it "conforms (verified can fail)".

5. **Green.** Write the minimum code that makes the failing tests pass. Add no behaviour the spec does not
   cite. If the code needs something the spec does not state (a message, a limit, a fallback), keep it
   minimal and list it under NOT IN SPEC as a question. Never present an invented value as spec. Run the
   full suite.

6. **Refactor.** Clean up with the suite green. Behaviour must not change.

7. **Report and ledger.**

   | Rule (source line) | Outcome | Test | Status |
   |---|---|---|---|

   Status is one of: red→green, conforms (verified can fail), not testable (reason), deferred (→ §N),
   open. Then list the NOT IN SPEC questions, open items and conflicts for the spec owner. Update the
   ledger.

## Coverage ledger (multi-section runs)
When the scope is more than one section, keep `docs/spec-coverage.md` (outside the shards folder, because
re-sharding deletes files there). Keep one row per section: the section, mode (gap-check or full), rules
inventoried, TEST / NOT TESTABLE / DEFERRED / OPEN counts, test file, and date. Below the table, list
every DEFERRED rule with its target section and every open question. At the start of a run, read the
ledger and continue from the first unfinished section. Pick up the DEFERRED rules when their section comes.

## Don't
- Don't write a test whose expected value you cannot cite. A plausible default is an invented requirement.
- Don't assert existing code behaviour (messages, formats, fallbacks) that the spec does not state.
  Existing code is not the spec.
- Don't infer a rule from a hint ("git-ignored" does not mean "optional"). Make it OPEN and ask.
- Don't cite shard lines. Cite the source.
- Don't edit the requirement document or the shards.
- Don't call a section covered while any inventory row has no outcome or a TEST row has no passing test.
