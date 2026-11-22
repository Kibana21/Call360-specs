# E2E-1 — End-to-end non-voice acceptance: implementation report

**Status: BUILT AND TECHNICALLY VERIFIED 2026-11-22, awaiting the owner's review. Not accepted.**
**SIMULATION ONLY. SYNTHETIC DATA ONLY.** No call was made, nothing was spoken, no customer data was used, no
operational finding or disposition was created, and nothing here is a compliance outcome or establishes that a call
may be made. Technical completion is not business readiness.

Authorisation: the owner's message of 2026-11-22, "Accept EVAL-2B, Enable Development and Implement E2E-1".
Companion documents: `44_…` (baseline, handoffs, acceptance matrix), contract `04_…` §20, decisions D-312…D-320.

---

## 1. EVAL-2B acceptance record and D-311 reconciliation

EVAL-2B is recorded as accepted, TECHNICALLY VERIFIED, simulation only (D-312), with the owner's eight points. It is
not production acceptance, Compliance approval or proof of spoken delivery.

**D-311, one by one** (exact wording in the register, D-313):

| | Decision | Status | Business side still unresolved |
|---|---|---|---|
| a | no new permission | accepted as technical semantics | who holds the permissions outside development |
| b | a survey that ended without "completed" and passed every check is `VERIFIED` | **accepted** (owner's point 5) | — |
| c | a survey not started makes the journey `INCOMPLETE`, not a deviation | accepted as technical semantics | whether an unstarted required survey is acceptable on a live call (OR-1…OR-3) |
| d | decisions and entry conditions shown as recorded, not re-evaluated | accepted as technical semantics; kept as limitation TG-2 | — |
| e | naming a control evaluation is optional | accepted as technical semantics | — |
| f | evidence changed after the evaluation → every result shown as not trustworthy | accepted as technical semantics | what a reviewer must then do |
| g | a deviation produces no finding, severity or disposition | **accepted** (owner's point 6) | what a deviation should lead to |
| h | setting `survey_execution_assurance_enabled` | accepted as technical semantics | — |

**Technical gap TG-1, recorded and kept (D-314).** Where follow-up questions are queued from a multiple-choice
answer, assurance does not verify their order or completeness edge by edge: three sub-checks of `BRANCHING` /
`MODULE_SEQUENCE` are not applied inside that module instance, and the check says so in a note. Integrity, exact
wording, "only what the version contains, once", answer validity, module order and termination are still applied.
It affects 7 of the 82 golden runs (fixtures F4, G6, H4, J1). **Full branch-fidelity coverage is not claimed.**
Risk is low for recordings made by the authoritative engine (any other order changes the run fingerprint, which
integrity catches) and material for a recording produced outside it: it must be closed before assurance is relied on
for an externally produced trace.

Every outstanding Compliance and operational policy decision is retained (§9).

## 2. Development migration `0035` (authorised; done)

| Safeguard | Result |
|---|---|
| Identity and revision | database `Call360_db`, schema `call360`, environment `local`; at `0034_survey_control_policy` |
| Inventory | 138 tables, 15,497 rows |
| Fresh backup, verified | `_db_backups/call360_dev_before_0035_20261122.dump`, SHA-256 `c69245f900b942e22cac84e14b6458ef2c5b3816ac6cd7a764a76a20b9189524`; rows in archive = rows in inventory, table by table |
| Restore procedure | restore dry run clean (138 tables, 138 data sets, no error); `RESTORE.md` has "Rolling 0035 back" |
| Exactly two new tables | 138 → 140: `survey_execution_assurance`, `survey_execution_assurance_survey`; two triggers; no function, no permission |
| No existing schema or data change | **every one of the 138 pre-existing tables** fingerprinted before and after for columns, constraints, indexes and triggers: identical. 137 byte-identical in content; the other is `alembic_version` |
| Empty round trip | on development, before any record existed: `0035` → `0034` → `0035`; the structure after the downgrade identical to before |
| Guarded downgrade with a record | with five assurance records: "Refusing to downgrade: recorded execution-assurance results exist"; revision stays `0035` |
| Evaluation, policy, mapping, assignment and Script Studio records | 8 + 4 + 12 + 100 tables: content and structure identical |
| Permissions, CSRF, audit, replay | reader of evaluations reads (200) and cannot verify (403); no CSRF token 403; no session 403; unknown id 404; five `SURVEY.EXECUTION_ASSURED` audit events; every result recomputes; a repeated request returns the same record (200) |
| Market isolation | **not exercised on development** — all development identities are SG. It is tested in the test schema (another market: 404) |
| Enabled in development only | `SURVEY_EXECUTION_ASSURANCE_ENABLED` in the gitignored `.env` |
| Reset or re-seed | none |

**Synthetic assurance runs against existing development evaluations** — all five:

| Existing evaluation | Assurance | Notes |
|---|---|---|
| coordinated, under `POL-DEV-SYNTHETIC` (the conflict) | `VERIFIED`; both surveys verified; five journey checks passed | the conflict stays `REQUIRES_REVIEW`, on verified evidence |
| single survey, unanswered | `INCOMPLETE` | control results marked "execution not finished" |
| single survey, complete (one `NOT_SATISFIED`) | `VERIFIED` | verified and not satisfied, side by side |
| coordinated, EVAL-1 (no policy) | `VERIFIED` | |
| single survey, EVAL-1 | `VERIFIED` | |

In every case the evaluation's result fingerprint is unchanged and assurance created no finding. After the runs, the
only tables whose content changed are the two assurance tables, `audit_event` and four sign-in/session tables.

**`SG-ILP-HIGH-RISK v2` remains bound to `S-DEV-EVAL-SHARED`.** That binding was made for the `0034` walkthrough and
supersedes the binding to `S-DEV-FI2-WALKTHROUGH`. It was not changed back, and no other binding was created.
`RESTORE.md` records it and how to re-bind.

Evidence: `docs/acceptance/evidence/E2E-1/dev-migration-0035/`.

## 3. Baseline (step 1)

`44_…`: the nine modules with their contracts, migrations, settings and permissions; the eleven handoffs and how
each is pinned by id and fingerprint; the browser journeys that are reused; the acceptance matrix; the stand-ins.
The baseline was established by inspection first; the document was written up during the build and says so.

## 4. What E2E-1 added

Deliberately little:

| | Added | Why |
|---|---|---|
| Backend | `app/domain/survey/journey_trace.py`, `app/api/survey_journey_trace.py` — **one read operation**, `GET /api/v1/survey-evaluation/journey-trace` | the consolidated evidence chain (step 3) and the five dimensions (step 4) from the records that own them |
| Backend | `tests/test_zz_e2e1_journey.py` — the thin harness | scenarios A–G through the governed APIs |
| Frontend | `persist/JourneyPage.tsx` — "Application journeys": a list and one journey page | the reviewer's entry point (step 6) |
| Frontend | one link in the Evaluation Workbench, one on the Survey Studio first page | to reach it |
| Frontend | `e2e/persisted/zzz-e2e1.persisted.ts` | the real-browser walkthrough |

**Not added:** a table, a migration, a setting, a permission, an engine, a rule, a status, a business meaning.
The trace computes no outcome, coverage, finding or assurance result; a test asserts the operation is a single GET
and that the evaluation and assurance records are byte-for-byte what they were. No existing screen was redesigned.

## 5. The journey (step 2) and its scenarios (step 5)

Harness **H** = `tests/test_zz_e2e1_journey.py` (real HTTP, real PostgreSQL, isolated test schema, its own clean
schema). Browser **B** = `e2e/persisted/zzz-e2e1.persisted.ts` (Chromium → Vite → FastAPI → PostgreSQL).

**In H everything is created through the governed APIs by distinct identities**: three surveys (one reusing the
published module and question of another), three assignment rules (existing Assignment Rules API, maker and
checker), three bindings, three requirement groups, one control policy with five obligations, three mappings. At
the survey and the policy, self-approval and publication by the approver are attempted and refused. The finding
rule set goes through its existing service lifecycle (it has no HTTP governance of its own in these modules), as in
the accepted EVAL-1 tests. Nothing is written to the database directly.

**In B** steps 1–5 use the same governed operations from the signed-in browser sessions of distinct people (a new
survey reusing a published module; a new rule; a new binding; a new requirement group), and step 11 **selects** the
control policy and mappings that the EVAL-2A journey built and published through the screens. Authoring through the
screens themselves is covered by the FI-1, FI-2 and LIB-1 journeys in the same suite and was not repeated. The
answers of the coordinated simulation are given through its API; evaluation is requested through the API; execution
assurance is run from the workbench; everything is then read on the screens.

**The control policy is named explicitly in every evaluation.** Nothing selects a policy for an application; the
trace says `selected_by: NAMED_EXPLICITLY` and the page says it in words.

| | Scenario | Result (completion · satisfaction · coverage · assurance · eligibility) | Where |
|---|---|---|---|
| A | Complete happy path — three governed surveys (H), six (B); one refused answer recorded | all completed · every required obligation SATISFIED, one NOT_APPLICABLE · COMPLETE_WITHIN_POLICY_SCOPE · VERIFIED · NOT_ESTABLISHED | H, B |
| B | Completed journey, one control not satisfied | all completed · `TERM` NOT_SATISFIED, findings from the existing rule set with their source simulation and observation · COMPLETE · VERIFIED · NOT_ESTABLISHED | H, B |
| B′ | A correctly excluded question leaves an evidence gap | all completed · INSUFFICIENT_EVIDENCE · INCOMPLETE · VERIFIED, the item classed as a valid conditional exclusion, no omission · NOT_ESTABLISHED | H |
| C | Unfinished: a survey pending | RUNNING · evidence missing · INCOMPLETE · INCOMPLETE · NOT_ESTABLISHED; the next survey has no simulation | H, B |
| C′ | Stopped: policy unresolved (a declined acknowledgement) | stopped with a reason · not satisfied · INCOMPLETE · INCOMPLETE; neither downstream survey started | H |
| D | Two surveys, one published question revision, answers 20 and 30 | all completed · REQUIRES_REVIEW, **both observations kept, neither chosen** · INCOMPLETE (evidence conflicting) · VERIFIED | H, B |
| E | Missing or unknown applicability | (i) a missing rule input: requirement UNRESOLVED / INPUT_MISSING, the coordinated simulation refused (409), traceable as an application with no journey; (ii) a missing survey fact: plan BLOCKED, refused; (iii) a missing policy input: applicability **UNKNOWN**, outcome UNRESOLVED, coverage INCOMPLETE, zero NOT_APPLICABLE | H; (i) in B |
| F | Historical integrity | §7 | H, B |
| G | Security and isolation | §8 | H, B |

**The five things the owner asked to see demonstrated:**

| | Shown by |
|---|---|
| A completed journey can contain an unsatisfied control | B: completed, `TERM` NOT_SATISFIED |
| Complete evidence coverage can coexist with NOT_SATISFIED | B: coverage COMPLETE_WITHIN_POLICY_SCOPE with that control EVIDENCED |
| Execution VERIFIED does not imply SATISFIED | B: assurance VERIFIED |
| A correctly excluded question may still leave an evidence gap | B′ |
| A technically successful simulation does not establish compliance | every scenario: eligibility NOT_ESTABLISHED; said on the page |

**No scenario modified an operational record.** H counts callback cases, contact attempts, conversation sessions,
survey runs, script assignments, findings, media, transcripts, review decisions, script versions, the control
register and Script Studio's control mappings before and after: identical. Every record created is of class
`SIMULATION`.

**One existing behaviour worth the owner's attention, not changed:** in scenario C the existing findings engine,
under the synthetic rule set, raises its "not asked" finding for a question the unfinished journey has not reached.
That is the behaviour D-291 (d) is about; it was left exactly as it is.

## 6. Provenance (step 3) and the five dimensions (step 4)

The chain has the owner's fifteen links, in the owner's order (contract §20.2). For each link: the authoritative
record, its version where it has one, its fingerprint and what that fingerprint covers, and where the record comes
from. H asserts each against the module's own record — for instance the rule versions against the rows and checksums
in the rule table, the simulations against the coordinator's run fingerprints, the policy and mappings against the
evaluation's pins.

Stated rather than papered over:

| | |
|---|---|
| The application | has no record of its own; it is stored on the composite plan (or simulation) and identified by its fingerprint |
| A requirement-group revision | has no fingerprint of its own; it is identified by id and version and covered by the composite's fingerprint |
| Control results | have no fingerprint of their own; they are covered by the evaluation's result fingerprint |
| The event trace of a simulation | is not stored; it is recomputed by the authoritative engine and checked against the fingerprint after every input |
| Two surveys that consist of the same pinned module | show the same manifest fingerprint — it is a fingerprint of the pinned content, not of the survey's identity; the version ids differ |

Evidence: `docs/acceptance/evidence/E2E-1/provenance_trace_development_journey.txt` (readable, every link with full
fingerprints) and `.json` — the existing development journey; and the harness for the primary scenario.

Reopening a historical result keeps its meaning: §7.

## 7. Historical integrity (scenario F)

After the happy-path journey was evaluated and verified, three things were published through governance: a newer
mapping revision (the term now expected to be 30), a newer policy revision (one control dropped), and a newer
version of one of the journey's surveys.

| Checked | Result |
|---|---|
| The earlier evaluation | same result fingerprint, same pins (policy revision 1, mapping revisions 1), same outcomes; recomputes to itself; says `MAPPING_REVISED`, `POLICY_REVISED` |
| The earlier assurance result | same fingerprint and pins; `VERIFIED`; recomputes |
| The chain | the same records, versions and fingerprints, the same chain fingerprint; the survey shown is version 1.0, not the newer one |
| The composite plan | unchanged record and fingerprint; reports that composed again now it would differ — the one integrity line that is "no", and it is said |
| A new evaluation of the same journey | a new record, with the new meaning (`TERM` NOT_SATISFIED); both are listed and each can be opened |
| The superseded policy revision | cannot be evaluated under again (`POLICY_NOT_PUBLISHED`) — D-302 (g), still not approved as policy |
| A new application now | the binding still pins version 1.0, which is no longer effective: requirement UNRESOLVED / TARGET_NOT_EFFECTIVE. Nothing newer is substituted |
| **Explicit drift (INJECTED)** | the engine's output is altered inside the test: the simulations, the evaluation and the assurance result all report that they no longer recompute; assurance reads "no longer recomputes" with its recorded status kept; no record is rewritten |

The drift case is injected and named so; the authoritative engine did not produce it.

## 8. Security and isolation (scenario G)

| | Result |
|---|---|
| Three identities at each governance step | survey, binding, group, policy, mapping: proposer, approver, publisher; self-approval and approver-publication refused (H at the survey and policy; B at the survey, binding, group and mapping) |
| No `survey.evaluation.read` | trace 403; the journey page says "you cannot open this journey"; no entry link |
| `survey.evaluation.read` without `survey.assignment.read` | the five assignment links are WITHHELD and carry no record; a composite-plan trace is 403 |
| A reader | 403 on composing, coordinating, evaluating, verifying, proposing |
| Another market | 404 on every trace, evaluation and assurance read and on evaluating |
| No CSRF token | 403 on composing, evaluating, verifying |
| Malformed requests | two journeys named: 422; an evaluation of another journey: 409; unknown journey: 404 |
| Audit chain | verifies |

The trace is read-only and writes no audit event of its own; access denials are audited by the existing mechanism.
No security defect is known. That is not a claim that none exists.

## 9. Reviewer experience (step 6)

"Application journeys", reached from Survey Studio's first page and from "Follow this journey end to end" in the
Evaluation Workbench. One page per journey, read-only:

* **Five statements side by side**, as five questions: did the surveys finish, were the controls satisfied, was the
  required evidence there, was the execution faithful, may a customer be called (always "not established").
* **Seven questions in the reviewer's order** — what was required, which surveys were selected, what happened in
  each survey, what controls were assessed, what evidence was missing or contradictory, what findings arose, was
  execution faithful — each answered by its links of the chain, in plain sentences.
* **Identifiers, versions and full fingerprints on demand**, under "Technical details" on each record, with a link
  to the existing screen that owns it. Call plans and register rows are folded as supporting records.
* **"What this does not show"** — the open points, on the page.
* **Integrity** — whether each record recomputes to itself.

A defect found and fixed while testing: a slower answer to an earlier request could replace the page's newer
content when switching between two evaluations of one journey. Stale responses are now ignored.

Screenshots (real browser, isolated test database): `docs/acceptance/evidence/E2E-1/screens/`.

| File | Shows |
|---|---|
| `E2E101-…` | the journey's own survey, published by three people, reusing a published module |
| `E2E102-…` | the coordinated simulation: six governed surveys, completed |
| `E2E103-…` | the Evaluation Workbench: evaluation, coverage and execution assurance |
| `E2E104a-…` | the five separate statements |
| `E2E104-…` | the journey page: seven questions and the fifteen-link chain |
| `E2E105-…` | drill-down: record, version, full fingerprint, source |
| `E2E106-…` | scenario B: completed, covered, verified — and not satisfied |
| `E2E107-…` | scenario D: conflicting answers, both kept |
| `E2E108-…` | scenario C: unfinished journey, gaps visible |
| `E2E109-…` | scenario E: a missing input; the requirement unresolved; nothing run |
| `E2E110-…` | scenario F: an earlier record keeps its meaning after governance moved on |

Technical verification only; not a business UX or screen-reader sign-off.

## 10. Regression and acceptance evidence (step 8)

Final run, after the last change to any code:

| Check | Result |
|---|---|
| Full backend suite (`call360_test` only) | **1,008 passed, 0 failed** (1,006 before E2E-1; the two new tests are the harness and the read-only check) |
| 82 golden execution runs, 14 golden call plans | pass; fixture files unmodified in both repositories |
| Frontend unit suite | 612 passed |
| Persisted browser journeys | **26 passed** (25 + the E2E-1 walkthrough) |
| Prototype browser journeys | 13 passed |
| Standard browser journeys | 33 passed |
| `ruff check`, `ruff format --check`, `mypy app` | clean (125 source files) |
| `tsc`, `eslint`, production build | clean |
| OpenAPI | 270 operations, 511 schemas. Additive against the contract before this series (221 → 270, none removed) and against the last committed one (266 → 270: three of EVAL-2B, one of E2E-1; none removed; no existing schema changed). SHA-256 `dbc7b00bc49ecc38ca9d0a2c297df6deabfbc4c08fa1259deb00194cdb4edf01` |
| Specs validator | passes |
| Database data preservation | development: §2. Test: the harness's untouched-table counts |
| Security and cross-market | §8 |
| Repeat, replay and historical evidence | §7; reading a trace twice gives the same chain fingerprint |

Existing tests changed: only the contract-size pin in `tests/test_survey_api.py` (71 survey operations, 106 survey
schemas). No expectation of behaviour and no golden fixture was changed.

During the work the browser walkthrough failed three times before it passed, each for a stated reason: the new
requirement group was given an order position already in use (the server correctly refused the coordinated
simulation — `ORDER_UNRESOLVED`); the trace listed selected surveys in selection order instead of the governed order
(corrected in the trace); and the stale-response defect of §9 (corrected in the page).

Evidence: `docs/acceptance/evidence/E2E-1/`.

## 11. Technical gaps versus unresolved business policies

**Technical gaps (engineering can close them):**

| | Gap | Risk |
|---|---|---|
| TG-1 | queued follow-up order and completeness not verified edge by edge (§1) | low for engine-made recordings; material for external ones |
| TG-2 | recorded decisions and entry conditions are shown, not re-evaluated | the same shape as TG-1 |
| TG-3 | the event trace is not stored; assurance verifies the recomputed trace and the stored fingerprints | fine for simulation; a real channel needs stored delivery evidence |
| TG-4 | the application has no record or identity of its own; assignment inputs and facts are two separate entries | blocks any verified lineage |
| TG-5 | requirement-group revisions and control results carry no fingerprint of their own | covered by the enclosing fingerprint; weaker to cite individually |
| TG-6 | market isolation, and the browser journeys, are verified on the test schema; development has SG identities only | none for the code; noted for the evidence |
| TG-7 | the browser walkthrough enters answers and requests evaluation through the API, not by hand on the screens | those screens are exercised by the module journeys |

**Unresolved business or Compliance policy (not engineering's to decide; none was invented):**

| | Question |
|---|---|
| BP-1 | the real assignment attributes (replacement, rider …) and requirement groups — stand-ins are used |
| BP-2 | how assignment inputs map to application and catalog facts (input consistency and lineage: UNVERIFIED) |
| BP-3 | which control policy applies to which application, and who or what selects it (D-302 f) |
| BP-4 | every real control, obligation, applicability condition, mapping, finding rule and severity |
| BP-5 | live cross-survey continuation: after a refusal, an escalation, an incomplete or unstarted survey (OR-1…OR-3; D-313 c) |
| BP-6 | consent reuse, refusal and silence; what a non-answer leads to |
| BP-7 | findings while applicability is unknown; whether a survey's own exclusion can make a control not applicable (D-291 d, e) |
| BP-8 | whether an answer awaiting a person's assessment keeps coverage incomplete (D-302 b); re-evaluation under an earlier policy (D-302 g) |
| BP-9 | what an assurance deviation or integrity failure leads to; what a reviewer does with an untrusted result (D-313 f, g) |
| BP-10 | operational dispositions and operational call eligibility — nothing establishes either |
| BP-11 | who holds each permission in production; whether control governance is separate from survey governance (D-291 b) |

Choices of E2E-1 the owner may revise: D-320.

## 12. State

| | State |
|---|---|
| **Development database** | **`0035_survey_execution_assurance`** (owner-authorised) — the head; no further migration exists |
| **Test schema** | `0035` |
| On in development | survey definitions, library, simulation, assignment, requirement groups, coordinated simulation, evaluation, control policies, **execution assurance** (and with it the journey view) |
| Development content added | five synthetic assurance results. Nothing else |
| `SG-ILP-HIGH-RISK v2` in development | bound to `S-DEV-EVAL-SHARED` (unchanged) |
| `Call360-backend` | `main` at `ed3e51b` (the owner's commit); EVAL-2B and E2E-1 uncommitted on top (23 files) |
| `Call360-frontend` | `main` at `e79c4e0` (the owner's commit); EVAL-2B and E2E-1 uncommitted (12 files) |
| `Call360-specs` | `main` at `c43f4f5` (the owner's commit); later documents and evidence uncommitted |
| Commits or pushes by the assistant | none |

## 13. Proposed next checkpoint (a proposal; nothing is authorised)

E2E-1 shows the parts work together. What stands between this and anything operational is no longer integration:
it is the policy questions of §11 and three technical gaps that matter once evidence is produced outside the
simulator.

**Recommended: DEC-1 — decision closure pack (no application code).** One document per open question BP-1…BP-11,
each with the options, what each option would change in the system, and what evidence already exists — so Business
and Compliance can rule on them. Deliverables are specifications only. This is the shortest path to knowing what to
build next, and it invents nothing.

**In parallel or after, if the owner prefers engineering first: ASSURE-2 — close TG-1 and TG-2 and define stored
execution evidence (TG-3)**, still simulation only: verify queued follow-ups and recorded decisions against the
pinned version, and specify (not yet connect) the evidence record a real channel would have to supply.

Not proposed: any voice, Genesys or live-call work; any operational finding or disposition; Script Studio retirement.

## 14. Does E2E-1 meet its objective?

**Technically, yes, within the limits stated. Acceptance is the owner's.**

| Asked | Met? |
|---|---|
| One complete, governed, synthetic application-to-assurance journey across the existing modules | yes — H through the governed APIs end to end; B in a real browser |
| No new business semantics, second engine or parallel workflow | yes — one read operation and one read-only page |
| Governance not bypassed | yes; the finding rule set uses its existing service lifecycle, as before |
| One consolidated evidence chain, each link with record, version, fingerprint and source | yes; where no fingerprint or record exists it is said (§6) |
| Historical results keep their meaning | yes (§7) |
| Five dimensions shown distinctly; eligibility NOT_ESTABLISHED | yes |
| The five stated non-implications demonstrated | yes |
| Scenarios A–G | yes; drift is injected and named so |
| No operational record modified | yes |
| A reviewer's entry point connecting existing screens, without redesign | yes |
| Nothing invented from the list of known constraints | yes — stand-ins are named as stand-ins, the policy is named explicitly, lineage stays UNVERIFIED |
| Full regression | yes (§10) |

Not met, and said: the walkthrough's answers and evaluation request go through the API rather than by hand on the
screens (TG-7); market isolation is not demonstrated on development (TG-6); branch fidelity is not complete (TG-1,
TG-2). None of this is real-business readiness.

## 15. Stopped here

Nothing further was started. I committed and pushed nothing.
