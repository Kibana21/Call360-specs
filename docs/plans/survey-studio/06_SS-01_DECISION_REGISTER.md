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

## Owner rulings of 2026-11-21 ("Preserve SS-02 Baseline and Authorize G-6 Architecture Assessment")

| D-no. | Subject | Ruling (owner's words, condensed) | Effect |
|---|---|---|---|
| D-153 | Preserve the SS-02 baseline | Commit and preserve the accepted SS-02 baseline in separate local commits in frontend and specs; do not push | Found already committed and level with the remote when inspected: specs `786a7c0`, frontend `d1cdb03` (2026-11-21 21:07); backend unchanged at `7228875`. Verified, not re-committed: 19 fixtures / 63 runs regenerate byte-for-byte; 314 unit tests; types, lint, contract, secret scan clean; Script Studio and backend unaffected |
| D-154 | G-6 authorised | Conduct the Script Studio retirement and Survey Studio consolidation assessment. Analysis and specifications only. Goal: Survey Studio the single authoritative journey-authoring application; eventually remove Script Studio completely, including redundant frontend code, backend APIs, services and database structures. Avoid a separate Wording Studio. Do not silently change previous decisions. Do not start SS-03 or implement the changes | `20_G-6_ARCHITECTURE_CONSOLIDATION_ASSESSMENT.md` — **PROPOSED, presented for review**. Nothing decided or implemented |

### Proposals raised by G-6 (mine — none is decided)

AD-1 meaning of "remove completely" for the governed store · AD-2 whether synthetic history is carried forward ·
AD-3 module graph stored as one document · AD-4 draft → candidate → version publication · AD-5 Publisher separation
on the server · AD-6 one engine · AD-7 statements and gates in Survey Studio · AD-8 controlled variables · AD-9
conversational delivery · AD-10 Simulation Workbench · AD-11 Assignment and Finding Rules stay separate · AD-12
single language · AD-13 scheduled publication and withdraw · AD-14 vocabulary · **AD-15 amend SS-D-01, SS-D-02 and
SS-D-20; retain SS-D-17** (`20_…` §3.5). **SS-D-01, SS-D-02, SS-D-17 and SS-D-20 remain in force as worded until the
owner rules.**

## Owner rulings of 2026-11-21 ("G-6 Architectural Direction Approved: Unified Survey Studio")

**Governing rule (owner):** do not preserve an existing module merely because other modules currently depend on it;
preserve necessary business functionality, replace obsolete dependencies, remove redundant implementations.

| D-no. | Subject | Ruling (owner's words, condensed) | Effect |
|---|---|---|---|
| D-155 | AD-1 — one canonical store | One authoritative Survey Studio definition and publication model. Existing script tables, APIs, service boundaries and UI routes are not automatically entitled to survive: reuse as a genuinely useful primitive, refactor, replace with a simpler design, or delete after dependent functionality has moved. No two long-lived content stores or competing authoring models. Justify by implementation complexity, data dependencies, rollback and long-term maintainability — not merely current imports | `21_UC-01_CONSOLIDATION_MAP.md`: disposition per capability and per structure |
| D-156 | AD-2 — synthetic development data | Re-seed instead of preserving every legacy development record. Before any destructive implementation: inventory the actual development database; identify protected demonstration records and owner restrictions; produce a verified backup; identify exactly what a re-seed would replace; preserve the accepted SS-02 specifications, fixtures, reference interpreters and evidence; do not delete anything until a separate destructive-change checkpoint is approved. Synthetic development records are not production customer evidence | No legacy loader, evaluator or conversion path is to be built. **The five preconditions are not yet met** (no database was read in UC-01) |
| D-157 | AD-15 — previous rulings | Amend SS-D-01, SS-D-02 and SS-D-20 consistent with complete Script Studio retirement. Retain SS-D-17: operational voice/runtime integration remains last. Preserve the strength of existing compliance controls, even when their implementation moves | Amended wording below |
| D-158 | Target product | Survey Studio is the single authoring application, supporting: reusable modules and question definitions; answer routing and conditions; approved spoken wording; statement nodes for introductions, disclosures, transitions and closings; mandatory-question and lifecycle roles; numeric and acknowledgement answers; approved clarification and repeat wording; controlled variables; delivery mode and exact-wording controls; evaluation configuration; control and regulatory mappings; survey assignment configuration; interactive and batch simulation; call-plan preview; immutable candidate approval and publication. No separate Wording Studio; do not replicate Script Studio's six-tab design; inline editing and progressive disclosure | Status of each item after UC-01: `21_…` §5 |
| D-159 | Other Call360 systems | Do not assume Assignment Rules, Simulation Workbench, Finding Rules or Review Workbench must remain separate products. Assess their UI responsibilities by business workflow. Move appropriate design-time configuration into Survey Studio. Retain operational case review, runtime execution and governance enforcement as separate backend responsibilities where justified. Prefer shared reusable engines over duplicated services | `21_…` §2. Withdraws my proposal AD-11 |
| D-160 | UC-01 authorised | Unified Survey Studio Foundation: ten scope items. Do not implement unapproved repeat-count, timeout, refusal, consent or conversational wording policies. Do not delete Script Studio, reset the development database, change operational backend, API, runtime or voice behaviour, start SS-03, or commit or push | `22_UC-01_IMPLEMENTATION_REPORT.md` — BUILT AND TECHNICALLY VERIFIED, presented for review |

### Amended rulings (D-157)

**SS-D-01 — as amended.** Survey Studio has **one** authoritative definition and publication model. Existing
structures are reused where they are genuinely useful primitives, refactored into the new implementation, replaced by
a simpler design, or deleted once the functionality that depends on them has moved; none is kept because it exists.
Migrations are additive until a separately approved destructive checkpoint. **Superseded:** "Survey Studio reuses the
existing script families, published versions, question bank, modules, approvals … wherever their semantics are
compatible" as a default, and "No historical data is rewritten" **as applied to synthetic development data** (D-156).
**Unchanged:** production customer evidence, once it exists, is never rewritten.

**SS-D-02 — as amended.** Survey Studio owns the canonical survey structure, question identities, answer definitions,
module composition, conditions and routing, **and the customer-facing wording and its delivery**. There is one
authoring experience, one approval and publishing chain and one item master. **Superseded:** "Customer-facing wording
and delivery remain subject to the existing approved script governance" as a separate system. **Unchanged and
binding:** wording is governed; a Wording Version is pinned by every placement and locked by the published manifest
(W-1…W-5); the approval state "approved by S&C" can be set only by the S&C approval path; maker and checker are
distinct identities; published versions are immutable.

**SS-D-20 — as amended.** The authoring product is called Survey Studio and is the only authoring product. Script
Studio coexists **only until its retirement checkpoint**, when its label, routes and navigation entry are removed.
"Wording & Delivery" is the name of a capability in documents; it is **not** a screen, workspace, studio or
navigation entry. Naming rules are still changed only explicitly (an ADR amending ADR-0010 and superseding ADR-0007
§1, the screen-naming document, the validator's term list, and the tests) — **at the retirement checkpoint, not
before.**

**SS-D-17 — retained unchanged.** The graph runtime stays in simulation until operational integration is separately
authorised.

### Prototype decisions taken in UC-01 (mine — for the owner to confirm or change)

| No. | Decision | Why | Where it would change |
|---|---|---|---|
| P-13 | A statement is a definition in the **one item master** (kind STATEMENT) placed by a STATEMENT node. It shares identity, versioning, wording, sharing and comparison with questions | "Do not introduce a second question or script model" | Contract §7.1 |
| P-14 | Statement roles: Opening, Transition, Disclosure, Closing. **Transition is new** — the existing lifecycle has no such role | The owner named transitions | UC-D-4 |
| P-15 | A statement, a number question and an acknowledgement have exactly one way on; none can branch | Already-defined semantics for number and acknowledgement (SS-01 §8.1) | UC-D-7 |
| P-16 | A wording with no delivery mode set is delivered as exact text, synthesised. The canonical form of existing surveys is unchanged | The most restrictive mode that needs no recording; consistent with "no uncontrolled wording" | UC-D-1 |
| P-17 | "In the assistant's own words" can be selected and is a **blocker**. An approved recording is a warning; with a variable it is a blocker | AD-9 is undecided; a recording cannot contain a variable | UC-D-2, UC-D-3 |
| P-18 | A variable is written `{{field_code}}`, names one field of the governed catalog, and is rendered in one fixed format per type. Yes/no facts cannot be spoken. A missing or unusable value **stops delivery**: the simulator halts with "information is missing", the call plan is blocked | The owner asked for deterministic rendering and explicit missing-value errors | UC-D-3 |
| P-19 | "Mandatory", identity, consent and recording roles are **declared attributes only**. No gate or non-answer behaviour is implemented. Live eligibility (D-67) is reported as information | The owner prohibited unapproved refusal and consent policies | UC-D-5, UC-D-6 |
| P-20 | The answer to a number question or an acknowledgement cannot be read by a condition | No approved comparison semantics for them in conditions yet | UC-D-7 |
| P-21 | The simulator offers only "acknowledged" for an acknowledgement | "Does not acknowledge" is a non-answer | G-3 |
| P-22 | Clarification and repeat wording, and evaluation and control configuration, are shown on the card as **not available yet**, with the reason | Blocked by D-NA-8; contract only | UC-D-8, UC-D-11 |

## Owner rulings of 2026-11-21 ("Accept UC-01 and Authorize UC-02")

| D-no. | Subject | Ruling (owner's words, condensed) | Effect |
|---|---|---|---|
| D-161 | UC-01 accepted | Accept UC-01 as TECHNICALLY VERIFIED — FRONTEND PROTOTYPE. The unified authoring direction, Statement nodes, Numeric and Acknowledgement questions, wording/delivery controls, deterministic variables and customer-specific Call Plan Preview are accepted as the new prototype baseline. Formal UX acceptance, policy approval, backend implementation and operational readiness remain pending. Do not reopen SS-02 | Prototype baseline is SS-02 + UC-01. P-13…P-22 stand as the baseline, as amended by UC-02 |
| D-162 | AD-3 | Validated, versioned and hashed graph documents, with server-enforced integrity and derived usage indexes | TS-11 |
| D-163 | AD-5 | Separate Publisher permission and independently enforced maker/checker/publisher identity restrictions | TS-14. Who holds Publisher remains G-4a |
| D-164 | AD-12 | Single-language implementation initially | TS-23 |
| D-165 | AD-13 | Scheduled publication and withdrawal represented in lifecycle contracts, without inventing operational behaviour | Contract §8.7; `23_…` §2.1 |
| D-166 | AD-14 | Survey terminology for new APIs; defer destructive legacy renaming | TS-22 |
| D-167 | UC-D-9, UC-D-10 | Assignment rules authored through Survey Studio but independently governed and versioned. Findings policies authored through the Survey Studio Library, with separate Compliance permissions and governance. One authoring application does not imply one enormous editor or one approval event for unrelated artifacts | TS-20, TS-21; `23_…` §2.1 invariant 8 |
| D-168 | UC-02 authorised | Contract and call-plan readiness: schema /5 golden fixtures with an independent Python reference; plan computation separated from live-call eligibility; a recording without an approved asset blocks; compact call-plan UI; decision-ready contracts; minimal interfaces. Specifications, independent fixtures and narrowly scoped prototype correctness improvements only | `24_UC-02_IMPLEMENTATION_REPORT.md` — BUILT AND TECHNICALLY VERIFIED, presented for review |
| D-169 | Standing prohibitions repeated | Do not invent timeout values, retry limits, consent-refusal behaviour or spoken-data permissions. Do not modify or delete Script Studio. Do not touch the development database or re-seed. No backend, API, runtime or voice changes. No SS-03. No commits or pushes | Held |

### Prototype decisions taken in UC-02 (mine — for the owner to confirm or change)

| No. | Decision | Why | Supersedes |
|---|---|---|---|
| P-23 | A recording with no approved asset is an **error** `RECORDING_ASSET_MISSING`. The prototype has no asset concept, so every recording is blocked | Owner: delivery must be blocked; not an acknowledgable warning | P-17 in part |
| P-24 | An explicit "not acknowledged" is rejected with `NON_ANSWER_POLICY_UNRESOLVED`; the run stays pending. Distinct from "no answer was given" | Owner: blocked as unresolved policy, not silently accepted | P-21 |
| P-25 | An unfinished variable also stops delivery at execution (state `MALFORMED`) | It would otherwise be spoken with its braces | — |
| P-26 | A fraction in a whole-number field, or an amount with more than two decimals, is `INVALID`; nothing is rounded | Owner: never silently defaulted; found while writing the reference interpreter | P-18 in part |
| P-27 | Statements are labelled S1, S2 …; questions keep Q1, Q2 … counting questions only. Display only | Owner: distinguish statement labels from question numbering without changing canonical identities | — |
| P-28 | Live eligibility is ten explicit conditions in three states (`MET`, `NOT_MET`, `NOT_AVAILABLE`). In the prototype it can never be "eligible": assignment and channel cannot be established, and a simulated publication does not count | Owner: a successful draft plan must never imply production eligibility | — |
| P-29 | Rules introduced in UC-01 and UC-02 carry stable validation codes; earlier rules are still identified by their message | The fixtures compare codes | — |

## Owner rulings of 2026-11-21 ("UC-02 Review and Backend Decision Closure")

| D-no. | Subject | Ruling (owner's words, condensed) | Effect |
|---|---|---|---|
| D-170 | UC-02 accepted | UC-02 is accepted as technically verified, subject to the contract clarifications. Formal UX acceptance, business policy approval, live-call eligibility and backend authorization remain separate | Prototype baseline is SS-02 + UC-01 + UC-02. Clarifications: `25_UC-02_DECISION_CLOSURE.md` §1 |
| D-171 | Technical decisions recommended | Recommend approval of TS-1, TS-3, TS-5, TS-6, TS-8, TS-11 and TS-13 through TS-23 | 17 decisions **RECOMMENDED FOR APPROVAL** as worded in `23_…` §1.2. I record them as recommended, not as finally approved: the owner's word was "recommend" |
| D-172 | Technical decisions to amend | Amend TS-2, TS-4, TS-7, TS-9, TS-10 and TS-12 before their final approval: preserve future numeric/free-text-driven Decision nodes; exclude uncontrolled conversational wording from publishable surveys; use declared numeric precision, never round or truncate silently; capture explicit negative acknowledgements as evidence without treating them as successful acknowledgements; keep schema-v1 numeric-condition restrictions extensible; make lifecycle decision history append-only while keeping candidate content immutable. Do not make changes that invalidate accepted golden fixtures without an explicitly versioned contract and corresponding new fixtures | Amended wording **PROPOSED** in `25_…` §1.2. No fixture changed; new behaviour is assigned to a future schema `/6` |
| D-173 | Persistence decisions | Prepare exact final rulings and dependency impacts for the 12 identified blockers, with ten recommendations. Do not mark actual permitted customer fields, refusal handling, consent policy, outcome catalog or non-answer rules approved without the appropriate Business/Compliance rulings | Twelve rulings **PROPOSED** as PB-1…PB-12 in `25_…` §2, each split into mechanism (approvable) and content (Business/Compliance). **None of the five named policy areas is marked approved** |
| D-174 | Additional review | Read P-23 through P-29 verbatim and classify each. Clarify in the call-plan eligibility UI that a mandatory gate being present does not establish that its enforcement behaviour is approved | Classification: `25_…` §3. UI: gates read "Present" / "Not present"; a separate condition for gate behaviour, not met; a standing note. Eleven conditions |
| D-175 | Baseline and next boundary | Confirm whether UC-01 and UC-02 were committed locally; report hashes; do not push. Preserve all 27 fixtures, 82 expected runs, 14 expected plans and the independent Python reference interpreters. Prepare a narrowly scoped SS-03A foundation specification; do not begin SS-03A implementation until separately authorized | **Committed by the owner at 23:23: frontend `c575f76`, specs `33fdfce`; both level with their remotes.** 27 fixtures and five interpreters tracked. The changes of this review (eligibility clarification; documents 25, 26 and register updates) came after and are uncommitted; I made no commit (`25_…` §5). Specification: `26_SS-03A_FOUNDATION_SPECIFICATION.md` — not authorised |

### Technical schema decisions: status after D-171 and D-172

| Status | Decisions |
|---|---|
| Recommended for approval as written | TS-1, TS-3, TS-5, TS-6, TS-8, TS-11, TS-13, TS-14, TS-15, TS-16, TS-17, TS-18, TS-19, TS-20, TS-21, TS-22, TS-23 |
| Amended wording proposed, awaiting final approval | TS-2, TS-4, TS-7, TS-9, TS-10, TS-12 (`25_…` §1.2) |

### Persistence rulings proposed (PB-1…PB-12): what is and is not being asked

| Approvable by the owner now (mechanism) | Needs Business/Compliance (content) — **not approved** |
|---|---|
| PB-1 exact-text delivery by default · PB-2 conversational not publishable · PB-4 four statement roles, acknowledgement separate · PB-7 editable draft, immutable candidates · PB-9 activation, eligibility and two skip policies as four fields | — |
| PB-3 a `speakable` allowlist flag, false unless set | The actual permitted customer fields |
| PB-5 `response_obligation` separate from `lifecycle_role`, as a governed catalog | The obligation classes and their meaning (D-NA-5, D-NA-10) |
| PB-6 a separate Publisher permission; most restrictive identity rule until ruled | Who holds Publisher; whether the approver may publish |
| PB-8 an approval record on the Wording Version, set through the candidate decision | Who in S&C approves; what an approval requires |
| PB-10 a governed outcome catalog with fixed classes | The outcome list and each outcome's class |
| PB-11 a non-answer never matches an answer route; an explicit resolution is required | Every non-answer behaviour and parameter; refusal handling; consent policy |
| PB-12 a separate `NON_ANSWER_EXCEPTION` outcome class | The outcome code or codes |

### Prototype decisions P-23…P-29: classification (D-174)

All seven are safe engineering defaults that fail closed and invent no policy. Parts that are not engineering: what a
call does after a non-acknowledgement (P-24: Business/Compliance); the precision each field declares (P-26:
Business) and how a value is spoken (P-26: voice channel); how a recording is produced and approved (P-23: voice
channel); which conditions make a survey eligible for a live call (P-28: Business/Compliance) and what a channel
requires (P-28: voice channel). Verbatim text and reasoning: `25_…` §3.

## Owner rulings of 2026-11-21 ("Approve Decision Closure and Authorize SS-03A")

"The project may now proceed from prototype work to the real Survey Studio backend foundation."

| D-no. | Subject | Ruling (owner's words, condensed) | Effect |
|---|---|---|---|
| D-176 | Technical schema decisions | Approve TS-1 through TS-23, incorporating all six amendments in document 25 | **TS-1…TS-23 APPROVED**, with TS-2, TS-4, TS-7, TS-9, TS-10 and TS-12 as amended in `25_…` §1.2 |
| D-177 | Persistence mechanisms | Approve the technical schema mechanisms PB-1 through PB-12, with six clarifications | **Mechanisms APPROVED** as in `25_…` §2, as clarified in D-178…D-183. **Policy content is not approved** (see "Unresolved policy boundaries" below) |
| D-178 | Wording approval evidence (clarifies PB-8) | A Wording Version's content is immutable. Approval evidence must be append-only, referring to the exact wording version and candidate. Do not update the frozen wording record to mark it approved | Supersedes the "approval record on the Wording Version" of PB-8: approval is an **append-only event** `{wording item, language, wording version, candidate, actor, time}`. The wording row is never updated |
| D-179 | Non-answer resolution (clarifies PB-11) | Reserve a structured non-answer resolution capability, but do not lock in a per-question routing implementation or any behaviour until D-NA-9 and the related business decisions are approved | The contract reserves the capability only. **No route key, node field or behaviour is fixed.** PB-11's "declared for that question" is withdrawn as a commitment |
| D-180 | Non-answer exception category (clarifies PB-12) | A separate non-answer exception category may be represented in the catalog schema. No actual outcome codes, non-answer behaviour or escalation policy are approved | Outcome class `NON_ANSWER_EXCEPTION` exists in the catalog schema, with **no entry** |
| D-181 | Spoken variables (clarifies PB-3) | Spoken-variable permissions are default-deny. No real customer field is authorized for speech by approving the catalog structure | `speakable` is false unless set; SS-03A sets it for no real field |
| D-182 | Publisher (clarifies PB-6) | The Publisher permission is independent of Checker. Until the appropriate governance ruling, enforce the most restrictive distinct-identity checks. Do not grant production roles automatically | Approver ≠ any maker; publisher ≠ submitter; publisher ≠ approver. No production role receives a `survey.*` permission |
| D-183 | Synthetic content | All synthetic catalogs and wording remain explicitly unapproved for operational use | Every catalog entry and wording created by SS-03A is marked synthetic and unapproved |
| D-184 | Open decisions stay open | Keep the existing no-answer and Compliance decisions open | The no-answer register (17 decisions, 4 parameters) and gates G-3, G-4 are unchanged |
| D-185 | Local commits | Authorize local commits for the post-UC-02 review changes in the frontend and specs repositories only; review staged changes; do not push. Verify and document the remote status and provenance of the previous UC-01/UC-02 commits; do not rewrite, revert or force-push history | See the SS-03A report §"Commits and provenance" |
| D-186 | SS-03A authorised | AUTHORIZE SS-03A — Survey Definition Foundation, in three internally verified checkpoints (A.1 pure Python domain; A.2 persistence and governance; A.3 FastAPI and API contract), per document 26 with the approved clarifications. Use `/api/v1/survey-definitions`; preserve the naming ADR. Isolated test database only; do not migrate or re-seed the development database; no Script Studio table modified or removed; all operations disabled by default; no production permissions; no push | `27_SS-03A_IMPLEMENTATION_REPORT.md` |
| D-187 | Exclusions | Do not start SS-03B or survey execution; no server call-plan assembly; no non-answer, refusal, repeat, consent or timeout policy; no telephony, Genesys, GPT Live or Voice Lab; no change to Script Studio; no additional authoring application | Held |
| D-188 | SS-03A accepted | SS-03A is accepted as TECHNICALLY VERIFIED, subject to reconciling the fixture-regeneration discrepancy | Reconciled: the "1" was an untracked `__pycache__` folder created by the regeneration run itself, not a fixture; 27 fixtures and 82 runs unchanged against baselines `33fdfce` and `786a7c0` (`28_…` §1). Not production, UX or screen-reader acceptance |
| D-189 | Technical debt | Record any pre-existing SQLAlchemy transaction warnings as technical debt | TD-SS03A-1 (`tests/conftest.py:87`, seven existing tests), TD-SS03A-2 (evidence wording) — `28_…` §1 |
| D-190 | Commit SS-03A | Commit only SS-03A implementation, generated client, tests, evidence and specifications; separate local commits per repository; do not push | The SS-03A work was found already committed and pushed at 00:33 (backend `a607ff5`, frontend `abb7726`, specs `3ff4df7`), not by Claude Code. Only this checkpoint's additions were committed locally afterwards (`28_…` §2) |
| D-191 | Development database migration | Authorize applying migration `0027_survey_definitions` to the development database only after ten preconditions pass; do not re-seed, truncate, rename or drop | All ten passed; applied with an explicit target; 100 of 102 existing tables byte-identical, the other two being `alembic_version` and `permission` (+4 rows). Backup and restore instructions in `<workspace>/_db_backups/` (`28_…` §3) |
| D-192 | Development permissions | Enable `survey_definitions_enabled` only in the local development environment; separate named synthetic identities for Author, Checker and Publisher; only the permissions their workflows need; no automatic grant to existing roles; do not weaken or bypass permissions to make the UI usable | Three development-only roles and identities; ADMIN, USER and SC_CHECKER hold no survey permission; self-approval, self-publication and approver-publication refused at service and database; unauthorised access refused (`28_…` §4) |
| D-193 | FI-1 recorded | Record FI-1 as the proposed next implementation checkpoint: connect the existing Survey Studio frontend to the persisted Survey Definition APIs; preserve the accepted Lego Composer, Guided Builder and Graph; save, reload and optimistic concurrency; stale revisions without losing user changes; server validation authoritative; canonical document model preserved; synthetic data; no other authoring model. **Do not implement FI-1 yet** | Boundary, five decisions FI-D-1…FI-D-5 and seven acceptance tests proposed in `28_…` §5. NOT AUTHORISED |
| D-194 | Exclusions | Do not begin SS-03B; do not implement non-answer behavior or live-call eligibility; do not modify or remove Script Studio; do not push any repository | Held |
| D-195 | SS-03A enablement accepted | I accept SS-03A development enablement as TECHNICALLY VERIFIED. The migration to 0027, development permissions, fixture reconciliation and readiness checks are accepted based on the reported evidence. This does not constitute production readiness, business-policy approval or authorization for live calls | Recorded 2026-11-22 |
| D-196 | FI-D-1 Route permissions | Persisted Survey Studio uses `survey.read` for access. Editing requires `survey.edit`. Do not give development survey users `script.read` merely to open the application | The persisted route is guarded by `survey.read`; Save needs `survey.edit` (and the server enforces both). The development survey roles are unchanged |
| D-197 | FI-D-2 Save granularity | Retain canonical document-based editing, but ensure a Save operation cannot silently leave a partially saved survey. Investigate whether the existing API supports safe multi-document saving. If not, implement the smallest additive, transactionally atomic batch-save API necessary. Document and test the change before wiring it into the frontend | Investigated: the SS-03A API applied one operation per request, so a multi-document Save could stop half-way. Added `POST …/draft/save` (all operations, one revision, or none) and `GET …/draft/documents`; documented in `04_…` §10 and tested (`tests/test_survey_fi1.py`) before the frontend used them |
| D-198 | FI-D-3 Save timing | Explicit Save button; visible saved, unsaved, saving, failed and conflict states. No autosave | Implemented; a test asserts nothing is sent before Save |
| D-199 | FI-D-4 Feature setting | Provide a separate persisted-mode setting. Preserve the existing in-memory prototype and all 13 prototype journeys. Both frontend modes remain disabled by default in code | `VITE_SURVEY_STUDIO_PERSISTED` (off by default) beside `VITE_SURVEY_STUDIO_PROTOTYPE` (off by default); the prototype and its journeys are unchanged |
| D-200 | FI-D-5 Unsaved work | Keep local edits in memory. Warn before navigating away with unsaved work. Do not use localStorage or sessionStorage for survey data | In memory only; the browser asks before a reload or close, and an in-app dialog before following a link out of the survey; a test asserts both storages are empty |
| D-201 | FI-1 authorised | AUTHORIZE FI-1 — Real Survey Studio Frontend Integration: connect the existing authoring application through the generated client; one verified mapping between the Workspace and the six canonical document types, lossless on all 27 fixtures; reliable saving; explicit conflict resolution; server-authoritative validation; the three development identities; nine acceptance tests and a full-stack Playwright journey | Built and verified: `29_FI-1_IMPLEMENTATION_REPORT.md`. Awaiting the owner's review |
| D-202 | Git safeguards | Before creating another commit, inspect relevant Git hooks, editor integrations and configured automation for possible automatic pushing. Do not claim to know the cause without evidence. Do not push, force-push or rewrite history. No commits without separate authorization | Inspected (`29_…` §9): no hook, no scheduled job, no repository automation. The FI-1 work is uncommitted |
| D-203 | FI-1 exclusions | Do not start FI-2 or SS-03B; no runtime survey execution or server call-plan assembly; no non-answer, refusal, consent, retry or voice policies; do not change or remove Script Studio; do not migrate, reset or re-seed the development database; no operational customer data; do not change the previously accepted Survey Studio UI unnecessarily | Held |

### Unresolved policy boundaries (recorded on the owner's instruction, D-177…D-184)

**Approved:** structures and mechanisms. **Not approved, by anyone, and not to be treated as approved:**

| Area | What stays open | Who rules |
|---|---|---|
| Spoken customer data | Which fields may be spoken; the spoken form of values; what happens when a value is missing | Business, Compliance; voice channel |
| Response obligation | The classes of obligation and what each means (D-NA-5, D-NA-10) | Business, Compliance |
| Lifecycle gates | What a call does on "no", refusal or silence at identity, consent and recording gates | Business, Compliance |
| Non-answer | Everything: reasons, resolution, routing (D-NA-9), repeats, timeouts, precedence, outcome codes, escalation policy | Business, Compliance, Engineering |
| Outcome catalog | The list of outcomes and the class of each | Business, Compliance |
| Wording | Who in S&C approves; what an approval requires; every actual wording | Compliance |
| Publisher | Who holds the permission; whether the approver may publish | Business governance |
| Conversational delivery | Whether any controlled form is ever allowed | Compliance |
| Scheduled publication and withdrawal | Their operational behaviour | Business |

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
