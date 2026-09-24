---
name: tdd
description: Test-driven development driven only by the original requirement document. Writes one failing test per acceptance criterion or rule cited from the spec (ID and source line), then the minimum code to pass, and lists spec gaps as NOT IN SPEC instead of inventing tests. Use when asked to do TDD, write tests from the spec, PRD, FSD or requirements, implement a requirement ID test-first, or cover acceptance criteria with tests.
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

**Reading the spec.** If shards exist and are fresh, use `INDEX.md` and `ID-MAP.md` to find the section,
then read that shard (its content is a byte-exact copy of the source). Shards are stale when the source
changed after `INDEX.md` was generated (compare `git log -1` or file times); then re-run `grepable:shard` or read the source directly. With no
shards, grep the source for the ID or term and read the whole section around it.

**Citations** always point at the source: `LN-03.R2 (docs/original-requirement.md:L103)`. `ID-MAP.md`
gives the source line for every ID.

## Steps

1. **Scope.** Take the IDs, section or feature the user names. Map it to spec IDs (requirements, rules
   `.Rn`, acceptance criteria `AC-…`, codes). If the user names a feature with no ID, find the section
   that covers it and confirm the ID list with the user.

2. **Test plan.** Before writing any test, show:

   | Spec ID (source line) | Rule / criterion (verbatim) | Test name |
   |---|---|---|

   Below it list:
   - **NOT IN SPEC**: behaviour the feature obviously needs but the spec does not state (limits, messages,
     time zones, error handling). No test is written for these.
   - **Open items**: in-scope IDs marked `Decision pending`, `TBD` or `NOT IN SPEC`. Not testable yet.
   - **Conflicts**: the spec contradicts itself or existing code.

   If there are gaps, open items or conflicts, ask the user before continuing. Otherwise proceed.

3. **Red.** Write one test per row, using the project's existing test framework and conventions (do not
   add a new one). Put the spec ID in the test name and the source line in a short comment:
   `test("LN-03.R2 renews a loan only once", …) // docs/original-requirement.md:L103`.
   Assert exact values copied from the spec (numbers, codes, messages). Run the tests and confirm each
   fails **because the behaviour is missing**, not because of a syntax or import error.

4. **Green.** Write the minimum code that makes the tests pass. Add no behaviour the spec does not cite:
   no extra validation, defaults, fallbacks or messages. Run the full suite.

5. **Refactor.** Clean up with the suite green. Behaviour must not change.

6. **Report.**

   | Spec ID (source line) | Test | Status |
   |---|---|---|

   Then the NOT IN SPEC gaps, open items and conflicts still unresolved, each as a question for the
   spec owner.

## Don't
- Don't write a test whose expected value you cannot cite. A plausible default is an invented requirement.
- Don't test existing code behaviour that the spec does not require. Existing code is not the spec.
- Don't edit the requirement document or the shards.
- Don't mark the task done while a cited criterion has no passing test.
