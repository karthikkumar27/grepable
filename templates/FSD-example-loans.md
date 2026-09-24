# Bookloop — Functional Specification (worked example: Loans)

2026-09-24 · Source: `docs/original-requirement.md` PRD v2.3

<!-- Worked example of FSD-TEMPLATE.md. Bookloop is a fictional neighbourhood book-lending app; the
     PRD, its line numbers and every rule below are invented for illustration. The example shows the
     format: requirement IDs as heading prefixes, prose rules given IDs, and gaps recorded as open
     questions Q4–Q9 instead of assumptions (the PRD already uses Q1–Q3). -->

## 00 Document control

| Field | Value |
|---|---|
| Version | 1.0 |
| Status | In review |
| Source document | `docs/original-requirement.md` PRD v2.3 |
| Buildable when | Q4–Q9 answered |

**Decision log**

| ID | Decision | Replaces | Source |
|---|---|---|---|
| D1 | A loan lasts 14 days; renewal adds 7 days. | 21-day loans, no renewal (PRD v2.1) | L118 |
| D2 | Reservations are first come, first served; members cannot jump the queue. | Priority for new members (PRD v2.2) | L131 |

## 10 Loans

A member borrows a book that a neighbour lists, returns it by hand, and can reserve a book that is out on loan. P0 is required for launch, P1 follows the pilot. (L112)

**Permissions for this module**

| Action | Lender | Borrower | Guest | Source |
|---|---|---|---|---|
| Request a loan | ❌ | ✅ | ❌ | LN-01 (L114) |
| Confirm hand-over | ✅ | ✅ | ❌ | LN-02 (L115) |
| Reserve a book on loan | ❌ | ✅ | ❌ | RSV-01 (L131) |
| Cancel someone else's reservation | NOT IN SPEC | ❌ | ❌ | Q9 |

### LN-01 — Request a loan

| Field | Value |
|---|---|
| Priority | P0 |
| Status | Approved |
| Origin | table |
| Source | `original-requirement.md:L114` |

**Statement (verbatim).** A member requests an available book; the lender accepts or declines within 48 hours, otherwise the request expires.

**Rules**

| Rule ID | Rule (exact) | Source |
|---|---|---|
| LN-01.R1 | Only a book with status Available can be requested. | L114 |
| LN-01.R2 | A request the lender has not answered within 48 hours expires. | L114 |

**Acceptance criteria (verbatim)**

| AC ID | Criterion | Source |
|---|---|---|
| AC-LN-01-1 | A request on a book that is not Available is refused with BLK-001 | L114 |
| AC-LN-01-2 | An unanswered request shows as Expired after 48 hours | L114 |

**Not covered by source** → Q4 (is the borrower notified on expiry?)

### LN-02 — Confirm hand-over

| Field | Value |
|---|---|
| Priority | P0 |
| Status | Approved |
| Origin | table |
| Source | `original-requirement.md:L115` |
| Depends on | LN-01 |

**Statement (verbatim).** The loan starts when both lender and borrower confirm the hand-over in the app.

**Acceptance criteria (verbatim)**

| AC ID | Criterion | Source |
|---|---|---|
| AC-LN-02-1 | The due date is set only after the second confirmation | L115 |

**Not covered by source** → Q5 (what if only one side confirms?)

### LN-03 — Due date and renewal

| Field | Value |
|---|---|
| Priority | P0 |
| Status | Approved |
| Origin | table |
| Source | `original-requirement.md:L118` · D1 |
| Depends on | LN-02, RSV-03 |

**Statement (verbatim).** A loan is due 14 days after hand-over and can be renewed once for 7 days, unless someone has reserved the book.

**Rules**

| Rule ID | Rule (exact) | Source |
|---|---|---|
| LN-03.R1 | A loan is due 14 days after hand-over. | L118 |
| LN-03.R2 | A loan can be renewed once, for 7 days. | L118 |
| LN-03.R3 | A loan cannot be renewed while the book has a reservation. | L118 |

**Acceptance criteria (verbatim)**

| AC ID | Criterion | Source |
|---|---|---|
| AC-LN-03-1 | A second renewal is refused with BLK-002 | L118 |
| AC-LN-03-2 | Renewal of a reserved book is refused with BLK-003 | L118 |

**Not covered by source** → Q6 (time zone of the due date)

### LN-04 — Return

| Field | Value |
|---|---|
| Priority | P0 |
| Status | Approved |
| Origin | table |
| Source | `original-requirement.md:L121` |

**Statement (verbatim).** The lender marks the book as returned; it becomes Available again, or goes to the next reservation.

**Acceptance criteria (verbatim)**

| AC ID | Criterion | Source |
|---|---|---|
| AC-LN-04-1 | A returned book with a reservation is offered to the first member in the queue | L121 |

**Not covered by source** → none

### LN-05 — Overdue reminders

| Field | Value |
|---|---|
| Priority | P1 |
| Status | Decision pending |
| Origin | table |
| Source | `original-requirement.md:L124` |

**Statement (verbatim).** The borrower is reminded before and after the due date.

**Not covered by source** → Q7 (when, how often, which channel). Not buildable until answered.

### RSV — Reservations (prose, v2.3)

| Rule ID | Rule (verbatim) | Parent | Source |
|---|---|---|---|
| RSV-01 | A member can reserve a book that is out on loan. | — | L131 |
| RSV-02 | Reservations form a queue in the order they were made (D2). | D2 | L131 |
| RSV-03 | A reserved book cannot be renewed by the current borrower (LN-03). | LN-03 | L132 |
| RSV-04 | A book holds at most 5 reservations. | — | L132 |
| RSV-05 | When the book is returned, the first member in the queue has 48 hours to request it, otherwise the offer passes to the next member. | LN-04 | L133 |
| RSV-06 | A member can cancel their own reservation at any time. | — | L134 |

**Not covered by source** → Q8 (6th reservation), Q9 (who else may cancel)

## 80 Codes registry (Loans)

| Code | Meaning | Blocks | Overridable | Source |
|---|---|---|---|---|
| BLK-001 | Book is not Available | Loan request | No | L114 |
| BLK-002 | Loan already renewed once | Renewal | No | L118 |
| BLK-003 | Book has a reservation | Renewal | No | L118 |

## 97 Open questions

| ID | Question | Blocks (IDs) | Options (not decisions) | Owner | Needed by | Status |
|---|---|---|---|---|---|---|
| Q4 | Is the borrower told when a request expires, and how? | LN-01.R2 | A) In-app notice B) Email C) Nothing | <PO> | <date> | Open |
| Q5 | What happens if only one side confirms the hand-over? | LN-02 | A) Loan never starts B) Auto-start after N hours | <PO> | <date> | Open |
| Q6 | In which time zone is the due date calculated? | LN-03.R1 | A) Lender's B) Borrower's C) Fixed zone | <PO> | <date> | Open |
| Q7 | When, how often and through which channel are overdue reminders sent? | LN-05 | A) PO supplies schedule | <PO> | <date> | Open |
| Q8 | What happens when a 6th member tries to reserve a book? | RSV-04 | A) Refuse with a new code B) Hide the Reserve button | <PO> | <date> | Open |
| Q9 | Can the lender cancel someone else's reservation? | RSV-06 | A) Yes B) No | <PO> | <date> | Open |
