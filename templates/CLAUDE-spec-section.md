## Specs & Source Documents

### Where things live
- `docs/fsd/INDEX.md`: map of every spec section. **Start here.** Never read a whole spec file blindly.
- `docs/fsd/ID-MAP.md`: every requirement ID, rule ID, code, decision (D), journey (J) and open question (Q), with the shard `file:line` where it is defined.
- `docs/fsd/*.md`: spec sections, one topic per file. **Generated** by the `grepable` skill (`scripts/grepable.py`) from the source below. Never edit shards; edit the source and re-shard.
- `docs/original-requirement.md`: business source of truth.
- Line 1 of every shard is `<!-- source: docs/original-requirement.md:L<start>-L<end> -->`. Shard line N = source line start + N − 2.
- The FSD is the implementation contract. When sources disagree, **never pick a winner yourself**. Report it as a CONFLICT (see below). Priority for proposing a resolution: original-requirement > FSD > existing code.

### Requirement IDs used in this repo
- Requirements: `<AREA>-NN` (e.g. `LN-03`, `LN-05`). Atomic rules: `<AREA>-NN.Rn` or `<GRP>-NN` (e.g. `RSV-04`). Acceptance: `AC-<ID>-n`.
- Codes: `<CODE>-NNN` (e.g. `BLK-001`, `BLK-002`). Decisions `D<n>`, journeys `J<n>`, open questions `Q<n>`, TSD decisions `ADR-NNN`.
- An ID that is not in `ID-MAP.md` does not exist in the spec. Never invent one, and never infer a code from a neighbouring number.

### Reading protocol
1. Open `INDEX.md` and pick the section(s) relevant to the task. Sections with a ⚠ count contain `Decision pending` / `TBD` / `NOT IN SPEC` items, which are not buildable.
2. For a known ID, grep `ID-MAP.md` and jump to that `file:line`. Otherwise grep the shards for exact terms, field names or enum values.
3. Read the matching range with `offset`/`limit`. Read the **whole section**, not just the first chunk.
4. If a file is longer than one Read returns, keep paging until the section ends. Don't assume the rest.
5. Markdown tables with very long rows may be truncated. If a row looks cut off, grep for it directly.
6. For broad sweeps across many spec files, delegate to a subagent. Ask it to return only the extracted rules with `file:line` references, not file dumps.

### Citation rules (non-negotiable)
- Never state a requirement, field name, enum, validation rule or business rule from memory.
- Every requirement you rely on must cite its source as `ID (shard-file:line)`, e.g. `LN-03 (02-loans.md:12)`. For text without an ID, cite `shard-file:line`.
- If the spec is stale (source changed but shards were not regenerated), say so and re-run the `grepable` skill before continuing.
- If you can't cite it, treat it as unverified and say so.
- If the spec doesn't cover something, write **`NOT IN SPEC`** and ask. Do not invent a plausible default.
- Quote exact values (codes, field names, limits) verbatim from the source. Don't paraphrase them.

### Zero Assumption Policy (strict FSD mode)
The FSD is the contract. If it isn't written in the FSD, it isn't a requirement.

**Never assume or invent:**
- Default values, fallbacks, limits, timeouts, or thresholds.
- Validation rules, required/optional status, formats, lengths, or allowed values.
- Business logic, calculations, rounding, time zones, or date handling.
- Error messages, error codes, or error-handling behaviour.
- Field names, enum values, API paths, or payload shapes. Use the FSD's exact spelling.
- Status transitions, permissions, roles, or who can do what.
- UI labels, layouts, ordering, sorting, or empty states.
- Extra features, "nice to have" improvements, or edge-case handling the FSD doesn't mention.

**Never fill gaps using:**
- "Industry standard", "common practice", or "typically".
- Domain knowledge (e.g., how other systems in the same industry usually work).
- Existing code behaviour, unless the FSD explicitly says to keep it.
- Similar sections of the FSD. Rules don't carry over between modules unless the FSD says so.

**When the FSD is silent, ambiguous, or contradictory:**
1. Stop work on that item. Continue only with parts that are fully specified.
2. Log it in this format:
   ```
   QUESTION Q-<n>: <topic>
   - FSD reference: <file:line or "not covered">
   - What's missing/unclear: <...>
   - Options (not decisions): A) <...> B) <...>
   - Blocked items: <what can't be built until answered>
   ```
3. Domain knowledge may be offered **only** as a labelled suggestion inside the options, never implemented.
4. Do not leave TODO stubs that encode a guess. Leave the item unbuilt and listed.

**What you may decide without the FSD:**
Only internal implementation details that change no observable behaviour. This covers local variable names, private helper structure, file organisation within existing conventions, and test scaffolding. Anything a user, API consumer, database, or downstream system can observe needs an FSD citation.

**Self-check before every change:**
> "Can I point to the FSD line that requires this behaviour?"
> If no, it's an assumption. Remove it or raise a QUESTION.

### Before implementing
In plan mode, list the requirements you will implement as:

| REQ-ID / source | Rule (exact) | Where it lands in code |
|---|---|---|

Also list any `NOT IN SPEC` gaps and any conflicts found. Wait for confirmation if gaps or conflicts exist.

### Conflicts
When sources disagree, stop and report:
```
CONFLICT: <topic>
- original-requirement.md:<line>: <what it says>
- fsd/<file>.md:<line>: <what it says>
- code <path>:<line>: <what it does>
Proposed resolution: <...>. Awaiting confirmation.
```

### Long sessions & compaction
- After any context compaction, **re-read the source sections** before continuing. Summaries lose exact values.
- Don't trust earlier-turn recollection of a spec detail. Re-grep it.
- When compacting, preserve: all REQ-IDs in scope, exact field names/enums, open conflicts and `NOT IN SPEC` items.

### Definition of done
Before reporting a task complete:
- [ ] Every implemented rule traces to a cited REQ-ID or `file:line`.
- [ ] Tests cover each acceptance criterion from the cited sections.
- [ ] No unresolved `NOT IN SPEC`, `QUESTION`, or `CONFLICT` items remain, or they're listed explicitly in the summary.
- [ ] No observable behaviour exists without an FSD citation (Zero Assumption Policy).
- [ ] For critical changes: a fresh subagent that hasn't seen the work has checked the implementation against the cited spec sections and found no mismatches.
