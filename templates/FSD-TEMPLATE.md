# <Product name> — Functional Specification v<X.Y>

<YYYY-MM-DD> · Owner: <name> · Source: `docs/original-requirement.md` v<X.Y>

<!--
HOW TO USE THIS TEMPLATE
- One `##` heading = one shard file after running grepable.py. Keep each `##` section under ~400 lines.
- One `###` heading = one requirement, and the heading MUST start with its ID: `### LN-03 — Title`.
- Atomic rules live in a table whose FIRST column is the rule ID. The sharder treats headings and
  first table cells as definitions, so every ID below becomes greppable in ID-MAP.md.
- Write IDs out in full. Never `BLK-002 / 003`; write `BLK-002`, `BLK-003` on separate rows.
- Copy business wording verbatim from the source. Rewording is where meaning drifts.
- Anything the source does not say goes in Open questions, never in a rule.
- Delete these comments when done.
-->

## 00 Document control

| Field | Value |
|---|---|
| Version | <X.Y> |
| Status | Draft / In review / Approved |
| Source document | `docs/original-requirement.md` v<X.Y> (business source of truth) |
| Companion | <TSD vX.Y — shares IDs> |
| Buildable when | <gate / sign-off> |

**Precedence.** 1) Original requirement → 2) this FSD → 3) TSD → 4) existing code. A conflict is reported, never resolved silently.

**Revision history** (every change lists the IDs it touched, so a developer can re-read only those)

| Version | Date | Change | IDs touched |
|---|---|---|---|
| <X.Y> | <date> | <what changed> | <LN-03, RSV-04> |

**Decision log**

| ID | Decision | Replaces | Source |
|---|---|---|---|
| D1 | <decision> | <what it replaces> | `original-requirement.md:L<n>` |

## 01 Conventions

**ID scheme**

| Family | Meaning | Format | Example |
|---|---|---|---|
| `<AREA>-NN` | Requirement (from source) | Area prefix + 2 digits; never renumbered, never reused | `LN-03` |
| `<GRP>-NN` | Atomic rule extracted from source prose | 3-letter group + 2 digits | `RSV-04` |
| `<AREA>-NN.Rn` | Atomic rule inside a single requirement | Parent ID + `.R` + n | `LN-03.R1` |
| `AC-<ID>-n` | Acceptance criterion | Parent ID + n | `AC-LN-03-1` |
| `<CODE>-NNN` | Failure / validation / error code | 3 digits | `BLK-002` |
| `D<n>` / `J<n>` / `Q<n>` | Decision / user journey / open question | Number | `Q4` |

**Keywords.** **must** = mandatory. **must not** = prohibited. **may** = allowed, not required. The spec uses no "should": decide it or move it to Open questions.

**Status values.** `Approved` (buildable) · `Draft` (do not build) · `Decision pending` (not buildable; linked to a Q) · `Deferred P1/P2` (do not build).

**Origin values.** `table` (ID existed in source) · `prose` (rule extracted from source paragraph; new ID, needs owner confirmation).

## 02 Glossary

| Term | Definition (verbatim) | Source |
|---|---|---|
| <Term> | <definition> | `original-requirement.md:L<n>` |

## 03 Roles and permissions

| Action | <Role A> | <Role B> | <Role C> | Source |
|---|---|---|---|---|
| <action> | ✅ | ✅ | ❌ | <ID> |

A blank cell is **NOT IN SPEC**, not "no". Raise a Q for it.

## 04 Data model

### <Entity>

| Field | Type | Required | Allowed values / limits | Default | Source |
|---|---|---|---|---|---|
| <field> | <type> | Yes / No / NOT IN SPEC | <exact values> | <value or NOT IN SPEC> | <ID or L<n>> |

## 10 <Module name>

<One-paragraph purpose of the module, verbatim or near-verbatim from source.>

### <AREA>-NN — <Requirement title>

| Field | Value |
|---|---|
| Priority | P0 / P1 / P2 |
| Status | Approved / Draft / Decision pending / Deferred |
| Origin | table / prose |
| Source | `original-requirement.md:L<n>` · <TSD ADR-nnn> |
| Since / changed | v<X.Y> / v<X.Y> |
| Depends on | <IDs> |

**Statement (verbatim).** <The requirement text exactly as the source states it.>

**Rules**

| Rule ID | Rule (verbatim or exact) | Source |
|---|---|---|
| <AREA>-NN.R1 | <one testable rule> | L<n> |

**Acceptance criteria (verbatim)**

| AC ID | Criterion | Source |
|---|---|---|
| AC-<AREA>-NN-1 | <criterion exactly as source> | L<n> |

**Messages and errors**

| Condition | Code | User message | Source |
|---|---|---|---|
| <condition> | <code or NOT IN SPEC> | <exact text or NOT IN SPEC> | <L<n>> |

**Not covered by source** → <Q-refs, or "none">

<!-- Repeat ### blocks. For prose-only rules, use a group heading and a rules table: -->

### <GRP> — <Rule group title> (prose, v<X.Y>, <ADR>)

| Rule ID | Rule (verbatim) | Parent | Source |
|---|---|---|---|
| <GRP>-01 | <one sentence from source> | <ID or —> | L<n> |

## 80 Codes registry

| Code | Meaning | Severity / critical | Blocks | Overridable | Source |
|---|---|---|---|---|---|
| <CODE>-001 | <meaning> | <Yes/No> | <what it blocks> | <Yes/No/NOT IN SPEC> | L<n> |

## 90 Non-functional requirements

| ID | Area | Requirement | Target | Source |
|---|---|---|---|---|
| NFR-01 | <area> | <requirement> | <exact target> | L<n> |

## 97 Open questions

| ID | Question | Blocks (IDs) | Options (not decisions) | Owner | Needed by | Status |
|---|---|---|---|---|---|---|
| Q<n> | <what the source does not say> | <IDs> | A) … B) … | <name> | <date> | Open / Answered vX.Y |

## 99 Traceability

| Source (line / §) | FSD IDs | TSD / ADR | Tests |
|---|---|---|---|
| L<n> | <IDs> | <ADR-nnn> | <test file or suite> |
