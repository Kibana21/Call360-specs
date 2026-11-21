# SS-01 · Part C — Decision register SS-D-01 … SS-D-20

**Checkpoint:** SS-01. **Date:** 2026-11-21. This register supersedes the decision list in
`02_ARCHITECTURE_AND_DECISIONS.md` §H (SS-00), which is kept as the historical proposal.

**Status values.** **DECIDED** — the owner has ruled (2026-11-21, "Accept SS-00 and Authorize SS-01"); the wording
below records that ruling and how SS-01 applies it. **PROPOSED** — awaits the owner's approval. A decision becomes an
ADR and receives a project D-number (the log currently ends at D-112) only when the owner approves its exact wording.
"Contract" points to where SS-01 specifies it (A = `04_…`, B = `05_…`).

## Owner rulings of 2026-11-21 ("SS-01 Acceptance and SS-02A Authorization")

SS-01 was **accepted** as the documentation and contract-design checkpoint, subject to the refinements below. Each
ruling is recorded with the project decision number assigned to it. The detailed entries further down keep their
original SS-01 wording; where a ruling changes or completes an entry, this table takes precedence.

| D-no. | SS-D | Ruling (owner's words, condensed) | Effect on the contracts |
|---|---|---|---|
| D-113 | SS-D-20 | Approve replacing the old Script Studio naming restriction for the new Survey Studio experience; apply the targeted ADR-0007 amendment, EXC-001, validator terminology, naming document and test documentation; preserve the decision history; no blanket validator exemptions | **Applied 2026-11-21:** ADR-0010 added; ADR-0007 pointer; EXC-001 amended in place; the six allowlist rows moved to a "retired prohibitions" history table; "Survey Studio" removed from the validator's prohibited terms and a new check added that the amendment is present; `SCREEN_NAMING_AND_ROUTES.md` and S0 test matrix E2E-18 updated. Validator: 63 checks pass |
| D-114 | SS-D-02 | Wording Version and binding contract approved in principle: one question master, explicit customer-facing Wording Versions, pinned bindings, one governed approval subject, existing maker-checker authority preserved | Part B §7 stands. The five binding rules W-1…W-5 were re-checked against this ruling and are consistent: W-1 pin, W-2 compatibility by structural signature, W-3 no silent wording change, W-4 no local override, W-5 exact delivery. No change needed |
| D-115 | SS-D-09a | Findings are raised **per executed placement**, with stable identifiers and idempotency; the interface may group related findings without merging their audit records | Part A §6.4 stands (two findings for two failing placements). Added requirement: the finding identifier is derived from (run, rule set, rule, **question instance**, trigger), so a repeat generation produces the same identifiers; grouping is presentation only |
| D-116 | SS-D-18 | `@dnd-kit` authorised for accessible drag-reorder; `@xyflow/react` plus a layout library authorised for the editable graph prototype; assess compatibility and security before installation; use only where they improve authoring | `@dnd-kit` assessed and installed for SS-02A (report `08` §2.1). Graph libraries **not yet installed**: the graph is SS-02C |
| D-117 | SS-D-06 | Ordered normal progression with explicitly configured outcome routing; never silently invent exceptional destinations | Part A §2.2 stands |
| D-118 | SS-D-07 | Every condition binding specifies its UNKNOWN policy; missing data must never silently become FALSE | Part A §5.2–5.3 stands |
| D-119 | SS-D-10 | Deterministic sequential follow-up queues with explicit order, deduplication, escalation **interrupt/resume policy**, validation and a declared rejoin; all execution decisions explainable | Part A §4 stands, with one amendment: an interrupt carries an explicit policy, `STOP` (emit the outcome; remaining follow-ups skipped and traced) or `RESUME` (ask the interrupt's question first, then continue the queue). SS-01 had proposed stop only. The prototype models both and lets the author configure `STOP`; see report `08` gap G5 |
| D-120 | SS-D-02a | No additional wording-owner approval role in P0, provided the existing authorised checker approves the exact immutable wording-and-routing candidate | Part B §7.4 stands |
| D-121 | SS-D-21 | Material publish warnings require an explicit recorded acknowledgement; actual validation blockers may not be waived by acknowledgement | Part B §10.1 stands: `ERROR` issues can never be acknowledged away; the list of warnings that count as "material" is still to be approved |
| — | others | Retained as documented proposals pending the owner's review of their exact wording | SS-D-03, 04, 05, 08, 11, 12, 13, 14, 15, 16, 19 remain PROPOSED. Those that affect the prototype are flagged in report `08` §6 |

## Owner rulings of 2026-11-21 ("AUTHORIZE IMPLEMENT SS-02A.1")

| D-no. | Subject | Ruling (owner's words, condensed) | Effect |
|---|---|---|---|
| D-122 | Interruption governance (proposed as SS-D-22) | An approved question/option **definition** determines whether an interruption is prohibited, optional or mandatory. A module placement configures behaviour only within the permitted set. A mandatory escalation cannot be weakened by a placement. For optional interruptions three governed behaviours: (A) stop the queue and go to an approved escalation/outcome; (B) handle the interrupting follow-up and resume the remaining queue, only when continuation is permitted; (C) stop the queue and route to an explicitly selected permitted destination. No implicit continuation, bypass of mandatory questions, or invented destination | Amends Part A §4: the interrupt policy is `STOP_ESCALATE`, `RESUME` or `STOP_REJOIN` (the two-value `STOP` / `RESUME` of D-119 is superseded), and each answer option carries an interruption class — absent (prohibited), `OPTIONAL`, `MANDATORY`. When several selected answers interrupt, a mandatory escalation takes precedence over everything else. Implemented in the prototype (report `10`) |
| D-123 | Duplicating an answer option | New stable code; editable presentation copied; routing **not** inherited; "Choose destination" until configured; a clear warning; the original and its references preserved; not publish-ready while unresolved | The SS-02A.1 proposal to copy the destination is withdrawn. Implemented (report `10` R3) |
| D-124 | Minimum width | 1024 px is the minimum supported desktop authoring width for the prototype; test at 1440, 1280 and 1024; responsive overlays for the library and inspector where necessary; essential routing controls never inaccessible | Implemented and checked (report `10` R5, §3.3) |

## Owner rulings of 2026-11-21 ("Accept SS-02B.1 and Authorize SS-02B.2")

| D-no. | Subject | Ruling (owner's words, condensed) | Effect |
|---|---|---|---|
| D-125 | Multi-select set operators (proposed as P-1) | Approve multi-select inclusion/exclusion operators based on **stable option codes**, including any/all semantics. Missing unanswered inputs evaluate **UNKNOWN**, not an empty selection | Part A §5.4 (b), (c). Prototype: `INCLUDES_ANY` / `INCLUDES_ALL` / `INCLUDES_NONE` |
| D-126 | First-matching-rule routing (P-2) | Approved, with explicit rule priority, a required fallback, and **no silent skipping of UNKNOWN evaluations** | Part A §3.4. A rule that cannot be evaluated stops evaluation; the next rule is not tried |
| D-127 | Stop and flag for review (P-3) | A governed **REVIEW_REQUIRED** outcome with automated progression halted and the run pending authorised review. Do not mark the survey completed | Part A §5.4 (e). Not author-routable; a survey cannot route past it |
| D-128 | Mandatory escalation (P-4) | Mandatory escalation **always overrides** ordinary routing. Every allowed answer set containing a mandatory-escalation option must lead to an **approved escalation outcome**, not merely any non-Completed outcome | Part A §3.4. The approved escalation outcome set is a governed list (prototype: synthetic, `ESCALATE` only) — **its contents need the owner's decision** |
| D-129 | Condition-version upgrades (P-5) | Approve explicit, independently authorised upgrades for other placements. **No silent propagation** | Part A §5.4 (f). Prototype: a "newer version available · not applied" marker; upgrading is choosing the version on that placement |
| D-130 | Selection limits (mandatory correction 1) | Selection-limit changes must never happen silently. An invalidating edit shows an actionable conflict; the configured limits are preserved until the author explicitly chooses a valid replacement; undo/redo restores the previous state | Part A §3.4. Prototype corrected: no operation other than the author's own changes `selection` |
| D-131 | Condition dependencies (mandatory correction 2) | Stable, typed references. No dependence on mutable display labels. References designed around stable question/answer identity, answer type, available scope and pinned version. Unanswered/missing distinguished from valid empty selections | Part A §5.4 (a), (b). Prototype corrected: typed input declarations, no stored labels |

## Owner rulings of 2026-11-21 ("Accept SS-02B.2 and Authorize SS-02B.3")

| D-no. | Subject | Ruling (owner's words, condensed) | Effect |
|---|---|---|---|
| D-132 | Answer availability (raised as O-1) | Permit conditions to reference answers from the same module that are guaranteed to have been collected **or may have been collected on only some prior paths**. Show availability clearly in the authoring UI. An answer not collected on the executed path evaluates UNKNOWN, not FALSE. Distinguish unanswered, skipped and explicitly answered-with-empty-selection in the evidence trace. Conditions referencing questions that cannot have been executed before the decision are invalid. Require explicit UNKNOWN handling | Part A §5.4 (d), (d-1); **SS-RUL-011 is replaced**. Prototype already allowed "some routes"; the simulator's trace carries the four evidence states |
| D-133 | Escalation outcomes (O-2) | For the prototype, ESCALATE is the only valid mandatory-escalation outcome. Other outcomes, including REVIEW_REQUIRED, are not automatically equivalent to escalation. Create a controlled outcome catalog with stable codes and explicit classifications. The final business-approved catalog is deferred to production governance approval | Part A §5.4 (g). Prototype: `OUTCOME_CATALOG` with classes; escalation outcomes are derived from the class |
| D-134 | Review-required halts (O-4) | REVIEW_REQUIRED halts automated progression. The run remains pending review, not successfully completed. Resume, close and resolution actions require a separately authorised review/operations capability, explicit permitted transitions and complete audit evidence. For this prototype, demonstrate these semantics using synthetic data only. No real review operations or runtime records | Part A §5.4 (h). Simulator: the run ends "Halted — review required", nothing after it is evaluated, and it is not reported as completed |

## Owner rulings of 2026-11-21 ("Accept SS-02B.3 Technical Verification and Authorize SS-02B.3.1")

| D-no. | Subject | Ruling (owner's words, condensed) | Effect |
|---|---|---|---|
| D-135 | Jump versus module entry condition | A jump must not implicitly bypass eligibility; the behaviour is not preserved merely because the reference interpreter implemented it. **Routing/jump** identifies the next candidate module; the **eligibility condition** determines whether that candidate may execute; the **activation trigger** determines when a module is selected through a configured outcome or normal sequence. For a jump target: TRUE → execute; FALSE → skip with an explicit reason and follow a configured skip disposition; UNKNOWN → its explicit UNKNOWN policy, including review halt; missing policy or destination → validation failure, never an invented fallback. Prevent automatic re-entry or loops. Preserve activation by a named earlier outcome | Part A **§2.2a** (withdraws "entering it unconditionally"). New instance member `if_ineligible`; validation `SKIP_DISPOSITION_MISSING`. Simulator, authoring validation, trace and fixtures G1–G3 updated. **Open:** a jump to an `ON_OUTCOME` instance activates it (§2.2a) — to confirm |
| D-136 | Review-required and blocked semantics | Make the migration from BLOCKED_UNKNOWN explicit and versioned. Distinguish: invalid or incomplete draft execution; missing-information review halt; governed REVIEW_REQUIRED outcome; completed run; mandatory escalation. Do not collapse fundamentally different terminal states merely to pass fixture comparisons. Preserve the historical fixtures; document changes through new or versioned expectations | Part A **§2.2b**: six terminal states; module status `HALTED_MISSING_INFORMATION`. Fixture schema `/2` (G1–G6) beside the unchanged `/1` (F1–F8); the `/2`→`/1` mapping is stated once and applied outside the engine |
| D-137 | No-answer behaviour | Record the outstanding requirement for real insurance callbacks (silence/timeout, refusal, retry and repeat limits, escalation or termination policy, explicit evidence that a question was not answered). Do not invent runtime behaviour or implement real voice processing. Identify the contract decisions needed before backend implementation | Part A **§5.5**: requirements NA-1…NA-8 and the six contract decisions needed. Nothing built |

## Owner rulings of 2026-11-21 ("Accept SS-02B.3.1 and Authorize SS-02C")

SS-02B.3.1 accepted as technically verified; formal business-user UX acceptance remains pending.

| D-no. | Subject | Ruling (owner's words, condensed) | Effect |
|---|---|---|---|
| D-138 | A-1 Jump and activation | An explicit jump is a valid activation mechanism. It may select a module even when the module is normally activated after a named outcome. The jump never bypasses eligibility. Explain the distinction in the UI and execution traces | Part A **§2.2c (a)**. Fixture H2. Trace: "It was selected by a jump … an explicit jump also selects it" + the eligibility result |
| D-139 | A-2 Activation and eligibility are independent | Support BOTH an activation trigger (when a module is selected) and an eligibility condition (whether the selected module may execute). Do not overload one entry field. Maintain backward compatibility with existing fixtures and modules | Part A **§2.2c (b)**: new instance member `activation`; `entry` is eligibility only; `entry.mode: ON_OUTCOME` still read. Fixture H1. Condition drawer has two settings |
| D-140 | A-3 Skip disposition | Support a configured skip disposition consistently for modules reached through sequencing or jumps. For sequential modules preserve Continue to next module as the normal default. For jump targets do not invent a fallback. Allow a later module or approved terminal outcome. Forward-only, no loops | Part A **§2.2c (c)**: new member `if_skipped_in_sequence` (default: continue); `if_ineligible` unchanged and still required for a jump target. **Implementation note:** two members rather than one, because a single member would have changed the meaning of accepted fixture G1 (run 4). Fixture H3 |
| D-141 | A-4 Mandatory escalation across the entire survey | A module-level mandatory escalation cannot be overridden by survey-level routing. For the current prototype it must terminate at the governed ESCALATE outcome. Continuation, normal completion and REVIEW_REQUIRED are not equivalent to escalation. Reject invalid mappings at authoring and validation time. A future escalation-handling workflow must not be invented here | Part A **§2.2c (d)**: `MANDATORY_ESCALATION_OVERRIDDEN`; the engine never follows such a route. Fixture H4. **Found while testing:** a mandatory answer under first-matching-rule routing was not treated as mandatory at survey level; corrected |
| D-142 | A-5 No-answer contract | Prepare a decision-ready contract (silence, refusal, optional blank, disconnection, retry limits, wording on repeats, mandatory questions, termination and escalation outcomes, evidence, voice versus non-voice). No arbitrary durations or counts. Record which decisions need business/compliance approval. Build nothing | `17_SS-02C_NO_ANSWER_CONTRACT.md`: 17 decisions D-NA-1…17 and named parameters with owners. Nothing built |

## Prototype decisions taken in SS-02C (mine — for the owner to confirm or change)

| P-no. | Decision | Why |
|---|---|---|
| P-6 | A candidate is identified by a **fingerprint of exactly what the survey uses** (the survey and the module, question and condition versions it pins). A review, an approval and a publication each belong to one fingerprint | So that "a changed candidate invalidates any previous approval" is a fact that can be checked, not a convention. Undoing a change restores the fingerprint and with it the approval |
| P-7 | **Blockers** must be fixed and cannot be acknowledged; **warnings** may be acknowledged only with a written reason, which the reviewer sees. Readiness = no blocker and no unacknowledged warning. Journey coverage can add a finding and can never remove one | Owner requirement: a structurally invalid survey must not be declared ready because a synthetic profile completes it |
| P-8 | **Separation of maker and checker is by identity, not by role.** One invented person holds both roles and still cannot approve her own submission | Workspace rule: "group membership alone does not permit self-approval" |
| P-9 | **Either role may publish an approved candidate** in the simulation | The specifications do not yet say who publishes; in Call360 it would be a server-side permission. To decide in SS-03 |
| P-10 | Wording "approved" with a published version stays approved while unchanged; only new or changed wording is put to the checker | Keeps a review proportionate; all wording in the prototype is synthetic and has no real approval |
| P-11 | The demonstration survey is seeded with a **clearly labelled simulated version 1.0** (an earlier revision) | So that revision comparison can be shown at once |
| P-12 | "Affected journey" in a comparison = the questions asked, the modules that run or the ending differ. A module merely considered and skipped in both is not a difference | A reviewer's meaning of "affected" |

## Owner rulings of 2026-11-21 ("SS-02C Final Closure Corrections")

The SS-02C functional delivery and visual direction are **accepted as the baseline**. The prototype is not closed
until six narrow corrections are made. They supersede the prototype decisions P-6 (in part), P-9 and point 3 of
report 18.

| D-no. | Subject | Ruling (owner's words, condensed) | Effect |
|---|---|---|---|
| D-143 | Immutable submitted candidates | Replace mutable submitted-review behaviour with immutable submitted candidates. Authors may continue editing separate drafts. Approvals bind to the exact candidate ID, revision and pinned dependency manifest. Undo must not transfer or resurrect approval on another draft | A submission freezes a **candidate** (`C-n`) with its revision number, content fingerprint, dependency manifest and manifest hash. Review, approval and publication refer to it **by ID**. The draft is separate: editing it neither voids nor moves an approval; the stages "review void" and "approval void" are removed. Submitting a changed draft creates the next candidate and **supersedes** an open one — its approval is not carried over. A draft made identical to an earlier candidate is **not** approved. **Supersedes P-6's "undoing a change restores the approval"** |
| D-144 | Separate Publisher capability | Introduce a separately authorised Publisher capability in the simulated governance flow. Enforce permission and identity checks. A checker role alone must not automatically grant publishing rights | Three permissions — Author, Checker, Publisher — none implying another. Publishing requires the Publisher permission **and** a different person from the submitter. Four invented people, one of whom holds all three and still cannot approve or publish her own submission. **Supersedes P-9** |
| D-145 | Escalate is terminal | Enforce ESCALATE as terminal across all routing modes and survey-level outcomes, even when escalation was reached without a mandatory-escalation answer | Part A **§2.2d**; `ESCALATION_NOT_TERMINAL`; the route is governed from the moment the outcome appears; fixture J1 (schema /4). **Supersedes** "an ordinary route to Escalate may still be routed by the survey" |
| D-146 | Separate skip dispositions | Retain separate skip dispositions for normal sequencing and jumps, preserving accepted fixture semantics | Confirms `if_ineligible` (after a jump) and `if_skipped_in_sequence` (in sequence, default continue) as specified in §2.2c (c). No change |
| D-147 | Graph menus | Fix collision-aware placement of Graph menus near the bottom of the viewport | Menus in the graph editors are placed against the window: below when it fits, otherwise above, otherwise on the side with more room with their height limited to it (scrolling inside). Tested on short windows |
| D-148 | No-answer contract | Keep unresolved decisions clearly marked. Do not invent policy values. Identify all decisions that block real runtime implementation | `17_…`: an "unresolved" banner; §10 gives every decision a status and two "blocks" columns. 14 decisions block building the runtime; 7 of them before any backend work; 3 decisions and 4 parameter values block real calls only. No value added |

**Found while making these corrections.** Opening a card's side panel scheduled keyboard focus onto the panel a
moment later; if the author had already tabbed into the panel and opened a menu, that late focus closed the menu.
The delayed focus now never takes focus from a control inside the panel.

## Owner rulings of 2026-11-21 ("SS-02 Prototype Technical Closure Accepted")

| D-no. | Subject | Ruling (owner's words, condensed) | Effect |
|---|---|---|---|
| D-149 | SS-02 accepted | I accept SS-02 as TECHNICALLY COMPLETE based on the final closure report. All six closure corrections are accepted. The original Survey Studio prototype story is now closed for feature development. Status: TECHNICALLY ACCEPTED — PROTOTYPE | D-143…D-148 accepted. **Not** formal business-user UX acceptance, **not** screen-reader accessibility sign-off, **not** production readiness, **not** approval of the unresolved no-answer policies, **not** authorisation for backend implementation. Do not reopen SS-02 for optional enhancements. Do not start SS-03 |
| D-150 | Preserve the baseline | Preserve the 19 fixtures, 63 expected runs, regression evidence, UX acceptance matrix and final closure documentation | Listed in `19_…` §8.1. Not to be deleted or overwritten |
| D-151 | Open decisions become gates | Mark unresolved business and governance decisions as explicit future gates | `19_…` §8.2: G-1 business-user UX acceptance · G-2 screen-reader sign-off · G-3 no-answer policy (D-NA-1…17, `NA-P-…`) · G-4 governance rules · G-5 remaining SS-01 proposals · G-6 architecture assessment · G-7 backend implementation (SS-03) · G-8 production readiness. Each needs its own explicit owner decision |
| D-152 | Next architectural direction — **record only** | Survey Studio becomes the single authoritative journey-authoring experience; essential Script Studio features are rebuilt or incorporated into it; redundant Script Studio functionality is eventually retired after safe migration; the execution harness assembles customer-specific call plans from approved survey definitions and application data; live customer answers dynamically select subsequent approved dialogue | **PROPOSED architecture change for the next assessment — not implemented, not authorised.** Recorded in `19_…` §9. SS-D-02, SS-D-17 and SS-D-20 remain in force until an assessment amends them. Script Studio is not modified or removed |

## Summary

| ID | Subject | Status | Needs the owner now? |
|---|---|---|---|
| SS-D-01 | Extend the governed model in place | DECIDED (in principle) | Confirm the compatibility proof (B §8.1) |
| SS-D-02 | Structure versus wording ownership | **DECIDED** (D-114) | No |
| SS-D-03 | Pin, upgrade explicitly, fork | PROPOSED | Yes |
| SS-D-04 | Approval subjects in P0 | PROPOSED | Yes |
| SS-D-05 | Outcome catalog | PROPOSED | Yes (the list) |
| SS-D-06 | Module sequencing | **DECIDED** (D-117) | No |
| SS-D-07 | UNKNOWN policy | **DECIDED** (D-118) | No |
| SS-D-08 | Lifecycle gates stay above the graph | PROPOSED | Yes |
| SS-D-09 | Question reuse and instance identity | **DECIDED**; 09a decided (D-115) | No |
| SS-D-10 | Multi-select and loop policies | **DECIDED** for follow-up queues (D-119); loop and Back/Edit defaults still PROPOSED | Partly |
| SS-D-11 | Roles and permissions | PROPOSED | Yes |
| SS-D-12 | API and vocabulary | PROPOSED | Yes |
| SS-D-13 | Feature flag and rollback | PROPOSED | Yes |
| SS-D-14 | Assignment and pinning | PROPOSED | Yes |
| SS-D-15 | Simulator data | PROPOSED | Yes |
| SS-D-16 | First-release scope limits | PROPOSED | Yes |
| SS-D-17 | Runtime last | DECIDED | No |
| SS-D-18 | Frontend libraries | **DECIDED** (D-116) | No |
| SS-D-19 | Requirements register | PROPOSED | Yes |
| SS-D-20 | Naming | **DECIDED and APPLIED** (D-113, ADR-0010) | No |
| SS-D-02a, 09a, 21 | New sub-decisions raised by SS-01 | **DECIDED** (D-120, D-115, D-121) | Only the list of "material" warnings |

---

## SS-D-01 — Extend the existing governed model in place
**Status:** DECIDED in principle.
**Exact wording.** Survey Studio reuses the existing script families, published versions, question bank, modules,
approvals, evaluation, findings, review and runtime infrastructure wherever their semantics are compatible. A new
requirement is not forced into an existing table whose semantics are incompatible; a new table is created instead.
Schema extensions are additive and happen only in later, separately authorised phases. No historical data is
rewritten.
**Resolution in SS-01.** Compatibility is proven pair by pair in B §8.1: seven structures reused (with additive
columns at most); new tables for node, edge, follow-up plan, survey route, option set, wording version, condition and
module review events, because `module_question`, `question_revision` and the draft-module lock cannot carry those
concepts without bending them.
**Risks.** Storage says "script", product says "survey" (handled by SS-D-12). The two additive relaxations
(draft-module lock, answer-type CHECK) touch guarded tables and need careful migration tests.
**Contract.** A §1.4, B §8.

## SS-D-02 — Survey structure versus approved wording
**Status:** DECIDED as to direction; the binding contract is PROPOSED.
**Exact wording.** Survey Studio owns the canonical survey structure, question identities, answer definitions, module
composition, conditions and routing. Customer-facing wording and delivery remain subject to the existing approved
script governance. There is one authoring experience, one explicitly defined approval and publishing chain, and one
question master.
**Proposed resolution.** A **Wording Version** is a governed facet of a Question (`{question}/{language}/{n}`),
bound to a Question Version by structural signature (answer type + option codes); every Question Instance pins both;
the manifest locks both; the existing maker-checker chain approves structure and wording together in one candidate;
`APPROVED_BY_SC` can be set only by the existing S&C path; no per-instance wording override. Rules W-1 … W-5.
**Risks.** Authors type working text while building, which may be mistaken for approved wording — mitigated by a
visible "not approved" state and the publish gate. Wording-only changes still need a new version of the consumer.
**Contract.** B §7.

### SS-D-02a — Separate wording sign-off (new)
**Status:** PROPOSED. **Wording.** In P0 the checker who approves a candidate approves its wording too; a distinct
wording-owner sign-off is not introduced. **Alternative.** A second sign-off by a wording owner before publication.
**Risk of the proposal.** One checker carries both routing and wording responsibility.

## SS-D-03 — Shared assets: pin by default, upgrade explicitly, fork instead of override
**Status:** PROPOSED.
**Exact wording.** Every consumer pins exact versions of the modules, questions, wording, option sets and conditions
it uses. A new version of a shared asset never reaches a consumer automatically. In a consumer's draft the author
chooses `Upgrade` (after an impact preview and a re-run of the consumer's scenarios), `Keep pinned`, or `Fork`. There
is no local override of shared content.
**Risks.** Stale pins accumulate; mitigated by the `DEPENDENCY_STALE` information issue and the consumers view.
**Contract.** A §6.2, B §10.6.

## SS-D-04 — Approval subjects in P0
**Status:** PROPOSED.
**Exact wording.** In P0 the approval subjects are the Module Version and the Survey Version, both on the existing
maker-checker chain. Questions, option sets, wording and conditions are approved as contents of the first candidate
that pins them; their library status is derived from that. A survey draft may contain local draft modules, approved
with the survey.
**Risks.** No independent curator gate for a question or condition; a weak question can be approved inside a module.
Needs an additive change to the draft-module lock and a module review record.
**Contract.** B §10.2.

## SS-D-05 — Outcome catalog
**Status:** PROPOSED.
**Exact wording.** Module and survey outcomes are chosen from a governed catalog. Authors may set a display label per
module but cannot create codes. Initial catalog: `COMPLETED`, `CLARIFICATION_REQUIRED`, `ESCALATE`,
`CUSTOMER_DECLINED`, `UNABLE_TO_VERIFY`, `RESCHEDULE`, `INCOMPLETE`. Existing termination reasons are kept and mapped
to these codes.
**Risks.** The list is illustrative, not approved business policy; adding a code later is easy, removing one is not.
**Contract.** A §2.1, §2.2.

## SS-D-06 — Module sequencing
**Status:** PROPOSED.
**Exact wording.** A survey is an ordered sequence of module instances. Each instance is considered in order and runs
if its entry mode makes it eligible (`ALWAYS`, `RULE`, `ON_OUTCOME`). Every declared outcome of every instance has
exactly one explicit route: continue, jump forward to a later instance, or stop with a survey outcome. Backward
routes are invalid in P0.
**Risks.** A forward jump skips the instances in between; the composer must make that obvious (they are recorded
`SKIPPED_BY_ROUTE`).
**Contract.** A §2.2; fixture F8.

## SS-D-07 — UNKNOWN policy
**Status:** PROPOSED.
**Exact wording.** There is no global default for UNKNOWN. Every condition binding states its policy: at a module
entry `BLOCK` or `SKIP_WITH_REASON`; at an internal decision `ROUTE_UNKNOWN` (with a mandatory UNKNOWN edge) or
`BLOCK`; at question applicability `ASK` or `BLOCK`. A binding without a policy cannot be submitted.
`SKIP_WITH_REASON` is not allowed on a module that contains a mandatory question. Legacy linear versions keep their
existing "missing is false" behaviour.
**Risks.** `BLOCK` stops runs on poor data quality; this is intended but must be visible in simulation before
publication. Converted legacy versions change behaviour on missing facts (B §8.4).
**Contract.** A §5.2, §5.3; fixtures F6, F8.

## SS-D-08 — Conversation lifecycle and gates stay above the graph
**Status:** PROPOSED.
**Exact wording.** Opening, identity, disclosure, consent and closing remain controller-level rules as accepted in
S2-D.1: stage order is validated; questions that disclose policy information stay blocked until identity is
confirmed; gate failures and reported conversation events terminate the run with their reason, ahead of any route;
closing statements marked for delivery on termination are still delivered. These modules appear as ordinary Lego
modules of their kind; their gate behaviour is not editable as routing.
**Risks.** Authors may expect to "route around" a gate; the UI must explain why they cannot.
**Contract.** A §2.3 (precedence 1), B §10.1 (lifecycle codes).

## SS-D-09 — Question reuse and instance identity
**Status:** DECIDED — the SS-00 restriction ("once per survey") is **rejected** by the owner.
**Exact wording.** A Question Definition may be placed in multiple modules, including modules used in the same
survey. Each placement has a unique, stable Question Instance identity, and each answer, evaluation and finding
references the executed instance and its pinned definition version. One placement is never executed repeatedly by
routing.
**Resolution in SS-01.** Instance key `{module instance}/{node}`; occurrence number only for Back/Edit; evidence shape
keyed by instance; an `execution_key` that equals `question_code` for legacy manifests (so nothing historical changes)
and the instance key for graph manifests; the list of future extensions to the controller, evaluation, findings,
scenarios, validator, operational evidence and review. Finding-rule scope `QUESTION` continues to target the
definition and applies to every instance.
**Risks.** The evaluation and findings code must be touched (key widening only) in SS-04; replay equivalence for
legacy runs is the safeguard.
**Contract.** A §1.3, §6; fixture F7.

### SS-D-09a — Findings per instance (new)
**Status:** PROPOSED. **Wording.** When the same Question Definition fails evaluation in two placements, two findings
are raised, one per instance. **Alternative.** One finding citing both instances. **Risk.** Finding counts rise where
definitions are reused; severity roll-ups should be reviewed when findings are integrated.

## SS-D-10 — Multi-select and loop policies
**Status:** PROPOSED.
**Exact wording.** All three multi-select modes are in P0 and are mutually exclusive per question instance. Queue
order is explicit priority, then declared option order. Dedupe is `ONCE_PER_ANSWER`. An interrupt option stops the
queue and emits its configured outcome, with no resume in P0. An empty queue takes a mandatory fallback. Follow-up
targets are single question nodes of the same module; nested queues and reusable follow-up sets are P1. Editing the
multi-select answer supersedes its follow-up answers and rebuilds the queue. For Back/Edit generally, if the changed
answer alters the route, later answers in that module instance and in later instances are superseded and re-collected.
Cycles are rejected at validation and capped at run time; bounded loops are P1.
**Risks.** The conservative Back/Edit rule re-asks questions that a finer analysis could keep.
**Contract.** A §4; B §9.5; fixture F4.

## SS-D-11 — Roles and permissions
**Status:** PROPOSED.
**Exact wording.** No new role is introduced in P0. Authoring (including library curation and wording drafts) uses
`script.edit`; approval `script.approve`; publication `script.publish`; simulation `script.simulate`; reading
`script.read`. Role holders are unchanged (USER; SC_CHECKER). The runtime service identity is defined in SS-09.
**Risks.** PRD roles "Library Curator" and "Auditor" are not distinct; any author can create reusable assets.
**Contract.** B §7.4.

## SS-D-12 — API and vocabulary
**Status:** PROPOSED.
**Exact wording.** New API routes live under the `survey-studio` prefix of the versioned API and are generated into
the same OpenAPI document. Existing script routes and their consumers are unchanged. The UI vocabulary is Survey,
Module, Question, Option, Condition, Outcome; storage keeps its existing names.
**Risks.** Two vocabularies for one model; documented in the contracts.
**Contract.** B §11.1.

## SS-D-13 — Feature flag and rollback
**Status:** PROPOSED.
**Exact wording.** A server setting, off by default, controls the visibility of Survey Studio routes and navigation.
Every migration is additive and has a tested downgrade. No existing column is dropped or repurposed. Switching the
setting off restores current behaviour at any phase.
**Risks.** Flagged code paths need tests in both states.

## SS-D-14 — Assignment and pinning
**Status:** PROPOSED.
**Exact wording.** Assignment rules, the case pin and the session pin are unchanged. A graph version is assignable
exactly like a linear version. Running and historical sessions never move to another version.
**Risks.** None new.
**Contract.** B §8.1.

## SS-D-15 — Simulator data
**Status:** PROPOSED.
**Exact wording.** Simulation uses synthetic profiles only. Replay of real cases is not provided.
**Risks.** Synthetic profiles may miss real data quirks; the field catalog review in SS-03 mitigates.

## SS-D-16 — First-release scope limits
**Status:** PROPOSED.
**Exact wording.** Size targets are those of SS-NFR-002 and are measured, not promised. No import or export in P0.
Findings and review of customer evidence remain in the existing Finding Rules and Review Workbench.
**Risks.** Large surveys are unmeasured until SS-10.

## SS-D-17 — Runtime last
**Status:** DECIDED.
**Exact wording.** The new graph runtime stays in simulation until operational integration is separately authorised.
Existing published scripts and historical execution records remain valid.
**Resolution in SS-01.** B §9.8 separates simulation from future runtime; B §8.2 states the guarantees.
**Risks.** Operational behaviour is unproven until SS-09.

## SS-D-18 — Frontend libraries
**Status:** PROPOSED — needed before SS-02.
**Exact wording.** No dependency is added without the owner's approval of the specific package and version.
For the SS-02 prototype the recommendation is: `@dnd-kit` (core and sortable) for accessible drag-reorder, and
`@xyflow/react` with a layered layout library (`elkjs` or `@dagrejs/dagre`) for the graph view. If not approved, the
prototype uses keyboard and pointer reorder written in-house and a read-only, in-house layered graph, and the
"real interaction" standard for the graph screen is correspondingly lower.
**Risks.** With libraries: supply chain, bundle size, licence review (both are MIT-licensed open source; to be
verified at the pinned versions). Without: a weaker graph experience and more custom code to maintain.
**Contract.** Part D §4.

## SS-D-19 — Requirements register
**Status:** PROPOSED.
**Exact wording.** The SS-* requirements remain in the Survey Studio PRD as their own namespace and are referenced
from the master register, not copied into it. The master BRD and register are not edited without the owner's explicit
specification-edit authorisation.
**Risks.** Two requirement sources; traceability is kept in the SS-01/SS-03 traceability table.

## SS-D-20 — Naming
**Status:** DECIDED.
**Exact wording.** The new authoring product is called Survey Studio. The old Script Studio may coexist temporarily
during migration. "Wording & Delivery" is the name of the governed capability within Survey Studio. Approved naming
rules are changed only explicitly: by an ADR amending ADR-0007 §1, an update of exception EXC-001, the specs
validator's prohibited-term list, the screen-naming document and the three tests that assert the old rule.
**Resolution in SS-01.** The amendment text, the file list and the test changes are proposed in B §11. **None has
been applied**; the specs validator therefore still fails its terminology check (B §11.5).
**Risks.** Until the amendment is applied the validator is red on one check; two frontend tests will fail as soon as
the label is shown and must change in the same SS-02 step.

### SS-D-21 — Warnings that need checker acknowledgement (new)
**Status:** PROPOSED. **Wording.** The existing acknowledgement of unmapped mandatory questions is kept. Of the new
warnings, `BRANCH_UNTESTED` and `DEPENDENCY_DEPRECATED` (on an existing pin) require the checker's explicit
acknowledgement at approval; other warnings are informational. **Risk.** Acknowledgement fatigue if the list grows.
