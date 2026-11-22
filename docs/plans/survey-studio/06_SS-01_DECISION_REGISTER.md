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
| D-204 | FI-1 conditionally accepted | FI-1 is conditionally technically accepted. The core persisted authoring, atomic saving, conflict handling, backend validation and permissions are accepted. Complete one mandatory correction before formally closing FI-1: fix browser Back navigation so unsaved changes trigger an appropriate leave-page confirmation; staying preserves the complete unsaved Workspace; leaving does not corrupt the saved revision; add a real-browser regression test including the back/forward history path; preserve the accepted UI | Corrected and verified (`29_…` §12). **FI-1 recorded as TECHNICALLY ACCEPTED — PERSISTED AUTHORING.** Not formal business UX acceptance, screen-reader sign-off or production readiness |
| D-205 | Contract additions accepted | Accept into the canonical contract: the atomic batch-save endpoint; the complete draft-document read endpoint; the `SET_DETAILS` draft operation; optional authoring metadata on ITEM, MODULE and CONDITION documents. The authoring metadata may affect content hashes, but must never acquire execution semantics or allow routing or wording rules to bypass validation. Preserve all 27 accepted fixtures, 82 expected runs and the canonical-document round-trip tests | `04_…` §10 is accepted contract. A backend test proves validation findings are identical with and without `authoring`; fixtures unchanged |
| D-206 | Local commits for FI-1 | Commit FI-1 and its narrow correction locally, with separate commits per repository; exclude unrelated Finder `.DS_Store` changes, temporary data, secrets and environment configuration; do not push, force-push, reset or rewrite history. Investigate whether editor Git synchronization settings should be changed; do not modify global editor preferences without approval | FI-1 as reviewed was found already committed and pushed at 04:46 (not by Claude Code). The correction and this record were committed locally; recommendation on editor settings in `29_…` §12.4, nothing changed |
| D-207 | FI2-D-1 Warnings | Server validation is authoritative for any warning whose acknowledgement affects submission. Warnings requiring acknowledgement must have stable server codes and recorded reasons tied to the candidate's content fingerprint. Browser-only warnings remain advisory | See `30_FI-2_IMPLEMENTATION_REPORT.md` |
| D-208 | FI2-D-2 Shared library | Shared-module discovery and cross-survey reuse are deferred to the next dedicated library checkpoint, not removed from the roadmap. Preserve immutable revision pins and copy-on-write behavior | Not built in FI-2; boundary proposed in `30_…` |
| D-209 | FI2-D-3 Makers | Retain the existing conservative maker rule in FI-2. Show the maker identities and the resulting approval restrictions to reviewers. Do not silently weaken governance | Rule unchanged; shown on every candidate |
| D-210 | FI2-D-4 Codes | Retain server-enforced global uniqueness for codes. Plan server-issued codes before implementing operational cross-survey reuse; do not change accepted fixture identities | Unchanged; planned in the library boundary |
| D-211 | FI-2 authorised | AUTHORIZE FI-2 — Real Review and Publication: author submits an immutable candidate after server validation and acknowledged server-governed warnings; checker inspects the frozen candidate and approves or rejects; publisher re-verifies the manifest and publishes an immutable version; the three development identities; synthetic wording stays identified as synthetic and unapproved; no separate Wording Studio; ten regression and security demonstrations | See `30_…` |
| D-212 | FI-2 exclusions | Do not start SS-03B; no live-call execution or server call-plan assembly; no no-answer or consent behavior; do not modify or remove Script Studio; do not reset or re-seed the development database; no cross-survey shared-library reuse in FI-2; do not push commits; no other authoring application | Held |
| D-213 | FI-2 accepted | Accept FI-2 as TECHNICALLY VERIFIED — REAL REVIEW AND PUBLICATION. Accepted: `SYNTHETIC_WORDING_UNAPPROVED` as a development-governance warning; mandatory acknowledgement of server-governed warnings before synthetic candidate submission; the two additive read-only API operations; the documented change to candidate-submission behavior. Acknowledgement of synthetic wording does not constitute Compliance approval and never makes a survey eligible for an operational customer callback | Recorded 2026-11-22. `04_…` §11 is accepted contract |
| D-214 | FI-2 limitation | Record the limitation that the checker currently sees frozen content as a table. A read-only Graph and more intuitive visual comparison should be addressed during future business UX acceptance | Open, for business UX acceptance (gate G-1) |
| D-215 | LIB-D-1 Published asset discovery | Only immutable asset revisions referenced by published survey versions may be discovered for cross-survey reuse. Discovery must respect market scope and permissions. Draft-only, rejected or unpublished assets must not appear in the shared library | `04_…` §12.1; enforced by the server on reading and on saving |
| D-216 | LIB-D-2 Reuse granularity | The reusable library must support modules, individual questions and their wording, conditions and option sets; in two slices (LIB-1A published module reuse; LIB-1B independent question, condition and option-set reuse), with one shared library architecture and user experience | One discovery operation, one detail operation, one selector for the four kinds |
| D-217 | LIB-D-3 Asset identity | New assets must receive globally unique, server-issued codes. Preserve existing asset codes, published versions, references and all accepted golden-fixture identities. Do not rename or renumber historical assets | `04_…` §12.3; migration `0028_survey_library`; nothing historical touched |
| D-218 | LIB-D-4 Maker provenance | An author who places an existing, immutable published asset into another survey does not inherit the original asset authors as makers of the consuming survey. An author who creates or edits a derived local copy becomes its maker. Preserve existing candidate-level maker/checker and publisher identity restrictions | Unchanged maker rule (the makers of a candidate are those who changed that survey's draft); verified |
| D-219 | LIB-D-5 Newer published revisions | If a newer published revision of a pinned asset becomes available, show an informational notice. Do not automatically upgrade the pinned revision. A newer version alone must not invalidate or block an existing candidate | Server finding `NEWER_REVISION_PUBLISHED`, severity INFO; editor notice; no upgrade exists anywhere |
| D-220 | LIB-1 authorised | AUTHORIZE LIB-1 — Reusable Component Library, inside the existing Survey Studio: library discovery, add from library, copy-on-write, usage and version awareness (LIB-1A); reusable questions, conditions, option sets and one unified selector (LIB-1B); server-issued asset identity; security, governance and integrity; sixteen mandatory verifications; full-stack Playwright. If a schema migration is necessary keep it additive and validate upgrade and rollback in the isolated test database; do not migrate or re-seed the development database without separate approval | Built and verified: `31_LIB-1_IMPLEMENTATION_REPORT.md`. Awaiting the owner's review |
| D-221 | LIB-1 exclusions | Do not start SS-03B; no server-side survey execution or call-plan assembly; no non-answer, refusal, retry, consent or voice policies; no real-call eligibility; no Genesys, GPT Live or telephony; do not modify or retire Script Studio; do not automatically upgrade published revision pins; no separate library application; do not rewrite historical asset identities; do not rebuild existing engines unnecessarily | Held |
| D-222 | LIB-1 accepted | LIB-1 is TECHNICALLY ACCEPTED, subject to closing the legacy library-discovery endpoint security gap. Known limitations preserved for later UX work: imported standalone assets that are not placed do not persist; no separate category or purpose filter controls; some condition previews show stored rule syntax; evaluation and control metadata are not yet part of reusable assets. No other library application and no separate authoring system | Recorded; limitations carried in `32_…` §11 |
| D-223 | LIB-1 security correction | `GET /survey-library/{kind}` stays for backward compatibility and is restricted to authorised, published, reusable asset revisions; market-level visibility enforced; another survey's unpublished, rejected or draft-only assets are never discoverable; enforced in the backend regardless of the library setting; negative security tests by direct API calls; the component-library endpoints keep their behaviour; published assets and version references unchanged. The endpoint may change its results; the change is documented | Done: contract §13.1; `32_…` §1 |
| D-224 | Development migration `0028` authorised | Apply `0028_survey_library` to the existing local development database only, under ten conditions (identity and revision 0027 confirmed; inventory; fresh verified backup with restore procedure; additive; only 0028; sequence and table verified; existing tables and data intact; library setting on in local development only; readiness and existing permissions verified; discovery, insertion and copy-on-write tested with synthetic data). No re-seed, truncate, reset or removal. Downgrade may be blocked once issued codes exist; a recovery procedure is kept | Done: `32_…` §2. Downgrade is now blocked (issued codes exist); recovery is a full restore of the verified backup |
| D-225 | SS-03B authorised — simulation only | AUTHORIZE SS-03B — Python Execution and Call-Plan Assembly, SIMULATION ONLY: SS-03B.1 deterministic graph execution of published versions; SS-03B.2 deterministic call-plan assembly; SS-03B.3 server-backed simulator on the existing Simulator and Call plan screens. One authoritative Python engine; no competing operational engine; pure evaluation separate from persistence, API and transport. No real customer call may be enabled | Built and technically verified; awaiting review |
| D-226 | Golden parity is the acceptance test | The Python engine must reproduce all 82 expected runs of the 27 fixtures and all 14 expected plans exactly. Accepted golden expectations are not modified to make the engine pass | Met: 82/82 and 14/14; no fixture changed |
| D-227 | Call-plan rules | Same inputs, same plan; UNKNOWN is never FALSE; missing data is not guessed or defaulted; numbers are never silently rounded or truncated; wording variables resolve deterministically; an undeliverable item blocks the affected plan; uncontrolled conversational delivery is prohibited; a computed plan is not evidence of live-call eligibility. Plan computability and operational eligibility are separate concerns | Implemented: contract §13.3–§13.4 |
| D-228 | Python is authoritative for persisted simulation | During the transition the TypeScript simulator's output is compared with the Python result; any difference is visible, investigated and covered by regression tests. No independently evolving second set of execution semantics in the frontend | Implemented: contract §13.8. One difference found and corrected (absent interrupt policy), `32_…` §6 |
| D-229 | No-answer and refusal in simulation | No unresolved Business/Compliance policy is decided. For simulation only: a question needing an answer may stay pending; an invalid answer is rejected and the same question stays current; a negative acknowledgement is an observation, not a successful answer; where an action needs an unresolved policy the result is the distinct simulation status `POLICY_UNRESOLVED` with the question and reason — not a business terminal outcome; no escalation or completion is synthesised; no repeat limits, silence windows, timeouts or refusal behaviour are invented. D-NA-1…D-NA-17 and their parameters stay open. The mechanism cannot authorise a real call | Implemented: contract §13.2 |
| D-230 | Simulation API and evidence architecture | Minimal authenticated APIs to create an isolated simulation, advance it with typed inputs, inspect state and trace, generate a call plan and read one. Simulation events are kept apart from operational callback evidence; market permissions, immutable version references, input validation and audit are enforced; persistence is isolated from live-call and operational records; additive contracts and migrations; automated tests on the isolated test database | Implemented: contract §13.5–§13.7; migration `0029` (test schema only) |
| D-231 | SS-03B exclusions | No production calls or live survey execution; no Genesys, Asterisk, GPT Live or Azure Speech; no consent, timeout, repeat or non-answer business policies; no live-call eligibility; no assignment of surveys to real customer cases; no operational findings or disposition actions; Script Studio not modified or retired; no legacy Script Studio data migration; protected development data not reset or re-seeded; no other authoring application; accepted golden fixture expectations not modified | Held |
| D-232 | Stop after SS-03B | Stop after SS-03B and present the results for review | Held. Nothing committed or pushed; the development database is not migrated to `0029` |
| D-233 | Choices made in SS-03B that the owner may revise | (a) simulation needs `survey.read` rather than a new permission; (b) migration `0029` and the setting `survey_simulation_enabled`, off by default; (c) a run is not stored — only its inputs, replayed deterministically; (d) the API checks only the shape of an answer, and the engine alone decides validity; (e) the draft is still previewed by the browser engine, labelled as a preview, while the server simulates published versions only; (f) the Python engine's results for the golden fixtures are exported to `python-results/` for the cross-engine test | (a) REPLACED by D-234; (c), (d), (e), (f) CONFIRMED by D-237; (b) stands |
| D-234 | SS-03B accepted; dedicated simulation permission | SS-03B is accepted as TECHNICALLY VERIFIED for its Python execution engine, deterministic call-plan assembly, simulation UI and golden-fixture parity — not production readiness, not authorisation for operational calls. Introduce `survey.simulate` for state-changing simulation operations: `survey.read` keeps reading definitions; creating and advancing simulations needs `survey.simulate`; reads enforce market scope and authorisation; read-only users cannot create simulation records; no existing production role receives it automatically; it is granted only to designated synthetic development identities; all checks server-side; CSRF, rate limiting and audit preserved | Done: migration `0029` creates it, granted to no role; contract §13.6; `33_…` §1 |
| D-235 | Replay records identify their contract and detect drift | Input-only replay records must identify the relevant execution-contract version and detect replay drift after engine changes. A historical simulation must never silently appear unchanged if its recomputed result differs | Done: contract §13.9 |
| OR-1 | Operational readiness: simulation retention and clean-up | The lack of retention and clean-up for simulation records is recorded as a separate operational-readiness item. No retention period is invented | OPEN. No period, expiry or clean-up exists for simulation, call-plan or assignment-selection records |
| D-236 | Development migration `0029` authorised | Apply `0029_survey_simulation` to the local development database after the security correction passes, with the stated preconditions (identity and revision 0028; inventory; fresh verified backup with restore procedure; additive; only the intended revision; Script Studio, Survey Studio and protected synthetic data intact; simulation on in local development only; readiness, permissions, creation, answer, replay and plan verified; no operational case, recording, transcript or finding created). Synthetic surveys and facts only; no reset, re-seed or destructive change | Done: `33_…` §2. Development is at `0029`; `0030` NOT applied |
| D-237 | SS-03B decisions confirmed | One authoritative Python engine; exact parity with 82 runs and 14 plans; deterministic simulation-only `POLICY_UNRESOLVED`; API validates answer shape and the engine decides validity; input-based replay subject to version/drift safeguards; generated Python results as derived regression evidence; browser preview for drafts kept distinct from authoritative published-version simulation. Golden expectations not modified | Recorded |
| D-238 | ASG-1 authorised | AUTHORIZE ASG-1 — Survey Assignment Integration: connect the existing Assignment Rules capability to published Survey Studio versions and the SS-03B plan generator, as a complete simulated workflow: synthetic application → assignment selection → published survey version → customer-specific call plan → simulation | Built and technically verified; awaiting review |
| D-239 | Reuse, not a second engine | Inspect the existing assignment backend and determine the smallest safe extension; reuse existing authoritative components; preserve all Script Studio assignment behaviour; document any contract mismatch before implementing an adapter; no other rule language and no independently maintained assignment engine | Done: contract §14.1; `33_…` §3 |
| D-240 | Governed survey assignment rules | Select only valid published survey versions; exact immutable version references; market and authorisation scope; existing governed condition semantics; rule precedence and matching preserved; matched, no match, ambiguous and unknown input distinguished; never silently select a fallback survey; never replace a pinned version automatically; maker/checker/publisher governance where applicable; an explanation of which rule selected the survey | Done: contract §14.2–§14.3 |
| D-241 | Selection connected to the plan generator | For a synthetic application: evaluate the policy, identify the immutable version, verify its manifest, invoke the SS-03B assembler, return the version, matching rule, plan fingerprint, included modules, missing facts and unresolved branches; plan computability distinct from operational eligibility; simulation-only | Done: contract §14.4 |
| D-242 | Survey Studio integration | Within the existing Survey Studio: inspect the published version, inspect the applicable governed policy, supply or choose a synthetic application, see why a survey was or was not selected, generate its plan, start a server simulation from the selected version, and inspect assignment and execution evidence together. No second Assignment Rules product | Done: one page, `Survey assignment`; `33_…` §5 |
| D-243 | ASG-1 boundaries | No live customer callback; no Genesys or voice provider; no consent, refusal, timeout or non-answer policies; Script Studio not modified or retired; no historical script data migrated; golden fixtures not modified; no parallel assignment rules engine; no new authoring application; no actual survey-to-customer assignment; no new operational outcomes or findings behaviour | Held |
| D-244 | Stop after ASG-1 | Stop after ASG-1 for review | Held. Nothing committed or pushed; development not migrated to `0030` |
| D-245 | Choices made in ASG-1 that the owner may revise | (a) The adapter is a governed **binding** from a published rule version to a published survey version, because a rule cannot target a survey version without altering Script Studio tables; a rule therefore still names a script version as well. (b) A rule with no published binding keeps its precedence and fails closed as `SURVEY_NOT_BOUND`. (c) Only the currently PUBLISHED survey version is selectable; a superseded one is not, and is not replaced automatically. (d) A binding is to one rule *version*; a new rule version needs a new binding. (e) Bindings use the existing survey permissions (`survey.edit` proposes, `survey.approve` decides, `survey.publish` publishes) and are read with `survey.read` — a person can read the published rules of their market on this page without `script.read`. (f) Assignment inputs and call-plan facts are supplied side by side; no mapping between them is assumed. (g) Migration `0030` and the setting `survey_assignment_enabled`, off by default | (a)–(d), (g) APPROVED as interim behaviour by D-246; (e) binding permissions APPROVED for development, read access REPLACED by D-247; (f) stands, made visible by D-254 |
| D-246 | ASG-1 accepted; interim decisions approved | SS-03B security closure and development migration 0029 accepted as technically verified. ASG-1 accepted as TECHNICALLY VERIFIED for SINGLE-SURVEY assignment. The one-to-one binding is an interim adapter, not the final assignment architecture; ASG-1 does not support an application requiring several complementary surveys. Approved interim behaviours: published script assignment rules continue to be evaluated by the existing engine; binding an exact published rule version to an exact published survey version is permitted; a new published rule version requires its own governed binding; superseded or withdrawn survey versions are not automatically replaced; bindings use the existing survey author, checker and publisher permissions for development, with identity separation enforced | Recorded |
| D-247 | Assignment read access | A user with `survey.read` must not gain unrestricted access to sensitive Script Studio rule data. Expose only the market-scoped information necessary for the survey assignment experience, or introduce an explicit assignment-read permission. Preserve existing Script Studio authorisation | Done: permission `survey.assignment.read` (migration `0030`, granted to no role) on every assignment operation; the policy no longer returns the script target; contract §14.4 |
| D-248 | Development migration `0030` conditionally authorised | After: automated test of the downgrade refusal when bindings exist; empty-schema upgrade and downgrade tests; confirmation that all new tables and constraints are additive; a verified fresh backup and inventory; confirmation that Script Studio and Survey Studio records are preserved; authorisation and market-isolation checks. Apply the intended migration only; enable ASG-1 in local development and demonstrate synthetic binding, selection, call plan and simulation; no reset, re-seed or destructive change | Done: `35_…` §2. Development is at `0030`; `0031` NOT applied |
| D-249 | ASG-2A authorised | AUTHORIZE ASG-2A — MULTIPLE APPLICABLE SURVEYS. One application may require several published surveys: a primary survey, additional required surveys, and alternatives that compete for the same requirement. Matching requirements are not forced through the single-winner decision | Built and technically verified; awaiting review |
| D-250 | Assess first; document semantics before implementation | Identify the smallest additive extension that evaluates several distinct survey requirements while preserving the rule language and precedence; do not alter Script Studio rule tables merely for this; document the grouping and matching semantics before implementation | Done: `34_ASG-2A_GROUPING_AND_MATCHING_SEMANTICS.md`, written first |
| D-251 | Governed assignment groups | An explicit, governed distinction of PRIMARY, ADD_REQUIRED and ALTERNATIVE; every group has an explicit purpose and deterministic matching rules; the existing published rule engine is reused within the group; its condition language is not copied or reimplemented; no priority, ordering, exclusion or fallback policy is invented; ambiguous group configuration fails closed | Done: contract §15.1–§15.2 |
| D-252 | Multi-survey selection | One primary, zero or more additional required, one from each applicable alternative group; every selected survey keeps its exact immutable version, its matching rule version, its binding, its reason and its content and manifest fingerprints; a complementary requirement is never silently discarded because another rule has a higher global priority; a pinned version is never replaced; questions are never merged or removed for similar wording | Done |
| D-253 | Composite plan | The SS-03B generator is used separately for each selected survey; the composite holds the application fingerprint, the policy and binding versions, the selected set, each individual plan and fingerprint, each reason, the configured ordering if present, missing facts and unresolved decisions, and a deterministic composite fingerprint; individual evidence and execution identities are preserved; no other graph executor; no combined canonical survey definition | Done: contract §15.3 |
| D-254 | Ordering, cross-survey behaviour and input consistency stay unresolved | Preserve governed ordering; absent or conflicting ordering returns an unresolved status. Do not decide whether one survey's escalation, refusal, incomplete answer or terminal outcome lets another proceed; no operational combined call. Identify the data requirements for deriving both input sets from one snapshot; invent no mapping; make unverified consistency visible and claim nothing is reconciled | Done: `ordering`, `cross_survey_policy: UNRESOLVED`, `input_consistency: UNVERIFIED`; `35_…` §6 |
| D-255 | One screen | Extend the existing Survey assignment screen: the primary survey, additional required surveys, alternative groups and their selected survey, why each matched, unresolved or conflicting requirements, each published version, each individual plan status, a combined overview. No separate Assignment Studio | Done |
| D-256 | ASG-2A exclusions | No real customer assignment; no live callbacks; no Genesys or voice; no cross-survey non-answer, refusal, escalation or consent policies; no automatic merging or de-duplication of surveys; no second rule language or execution engine; no Script Studio retirement; no evaluation and findings integration; no destructive data migrations | Held |
| D-257 | Stop after ASG-2A | Stop after ASG-2A for review | Held. Nothing committed or pushed; development not migrated to `0031` |
| D-258 | Choices made in ASG-2A that the owner may revise | (a) A group is a governed, versioned SET OF RULE VERSIONS; the engine runs once per group. (b) `PRIMARY` with no matching rule is unresolved, not "no survey needed". (c) Structural rules: an additional-required group's rules are bound to one survey; an alternative group has at least two rules and two surveys; one primary group per market; a rule in at most one published group. (d) A bound rule in no group that matches or may match the application makes the configuration unresolved. (e) Ordering is one optional whole number per group; nothing is inferred from kind. (f) The composite is not `READY` while ordering is unresolved, even if every individual plan is. (g) Two groups selecting the same survey version stay two requirements. (h) Migration `0031` and the setting `survey_assignment_groups_enabled`, off by default | (b), (f), (g) APPROVED by D-260 as D-258.1, D-258.2, D-258.3; the others stand as built and accepted by D-259 |
| D-259 | ASG-2A accepted | ASG-2A is accepted as TECHNICALLY VERIFIED — MULTI-SURVEY ASSIGNMENT AND COMPOSITE CALL-PLAN ASSEMBLY: requirement groups PRIMARY, ADD_REQUIRED and ALTERNATIVE; the existing rule engine independently per requirement; three-person governance of groups; immutable version selection and bindings; one SS-03B plan per selected survey; deterministic composite fingerprints; explicit unresolved ordering, input consistency and cross-survey policy; the ASG-1 assignment-read correction and development migration 0030. Simulation-only mechanics. The stand-in replacement and CI-rider demonstrations are NOT proof of real business assignment requirements | Recorded |
| D-260 | ASG-2A decisions confirmed | D-258.1: a primary requirement with no matching rule is unresolved. D-258.2: a multi-survey composite requires an explicit governed order before it is READY. D-258.3: if two requirement groups select the same published survey version, both requirements remain; neither automatic de-duplication nor double execution is authorised. Retained open: OR-2, OR-3, the unverified mapping between assignment inputs and call-plan facts, and all no-answer, refusal, consent and live-call policies | Recorded |
| D-261 | Unambiguous terminology | The UI must distinguish: the call plan is computable; a coordinated simulation is permitted or blocked; operational call eligibility has not been established. A composite READY plan must never imply the other two | Done: `states` on every composite and three separate lines on the screen; contract §15.3; `36_…` §1.1 |
| D-262 | Development migration `0031` authorised | Apply `0031_survey_assignment_groups` to local development after verifying identity and revision 0030, the protected-data inventory, a fresh verified backup with restore instructions, additive changes only, automated up / empty-down / guarded-downgrade tests, preservation of Script Studio and Survey Studio data, and development authorisation and market isolation. Confirm exactly what happens when a governed binding or group is withdrawn and a downgrade is attempted; do not claim withdrawal enables a downgrade unless tested. Enable ASG-2A in local development only; demonstrate with explicitly labelled synthetic conditions; no reset or re-seed | Done: `36_…` §2. Development is at `0031`; `0032` NOT applied. Tested: withdrawal does NOT enable a downgrade |
| D-263 | ASG-2B authorised, with simulation-only continuation rules | AUTHORIZE ASG-2B — COORDINATED MULTI-SURVEY SIMULATION: a thin coordinating layer over the composite plan, the SS-03B engine and the existing simulation APIs; no second engine; references, not merged graphs. Rules solely for technical simulation: begin only when selection and ordering are resolved; run the first survey of the governed order; COMPLETED may advance to the next survey; PENDING stays; POLICY_UNRESOLVED stops with its reason; any other terminal outcome stops with CROSS_SURVEY_POLICY_UNRESOLVED; no completion, escalation or business outcome synthesised for the composite; a duplicate survey version stops with DUPLICATE_SURVEY_REQUIREMENT_UNRESOLVED; unresolved or conflicting order does not start; a blocked individual plan is explained, not run. These rules do not approve continuation behaviour during real customer calls | Built and technically verified; awaiting review. Contract §16 |
| D-264 | No automatic de-duplication | Do not combine or suppress repeated opening statements, identity or consent questions, questions with similar wording, repeated required evidence or closing statements. Each survey runs exactly as approved. Any optimisation needs a future governed policy | Held; tested against the golden runs |
| D-265 | Coordinated simulation record | An isolated SIMULATION-class record referencing the composite and its individual simulations, with the application and composite fingerprints, governed order, selected versions, current survey and question, individual simulation identifiers and run fingerprints, survey states, continuation decisions and reasons, execution contract versions, aggregate progress and a stable replay fingerprint; not confusable with operational records; replay-drift detection and immutable references preserved | Done: contract §16.4; `36_…` §6 |
| D-266 | Simulator coordinated mode | Extend the existing Simulator with a coordinated mode showing the application and composite summary, all surveys in governed order, the current survey and question with exact wording, answers per survey, individual status, overall progress, why continuation was permitted or stopped, individual traces and fingerprints, and a consolidated report. Preserve the single-survey simulator | Done: `36_…` §7 |
| D-267 | Security of coordinated simulation | Appropriate simulation and assignment permissions; market isolation; published-version integrity; CSRF and rate limiting; read/write authorisation; SIMULATION-only persistence; immutable evidence and audit. No operational case, call attempt, survey run or finding | Done: `36_…` §8 |
| D-268 | ASG-2B boundaries and exclusions | Not decided: live cross-survey continuation; consent reuse; omission of repeated questions; whether one survey's escalation ends a callback; refusal and non-answer policies; operational outcomes; real callback eligibility. No replacement or rider attribute invented. OR-2, OR-3 and input mapping stay open. No Genesys, GPT Live or telephony; no customer calls; no real case assignments; Script Studio not modified; no other execution engine; no operational findings; golden expectations unchanged; no destructive migrations | Held |
| D-269 | Stop after ASG-2B | Stop after ASG-2B for review | Held. Nothing committed or pushed; development not migrated to `0032` |
| D-270 | Choices made in ASG-2B that the owner may revise | (a) The coordinated state is computed on reading from the steps and each survey's own replay; only the start of each survey is stored. (b) A composite that cannot be coordinated is refused at the start (409) rather than recorded as a blocked coordinated simulation. (c) `ALL_SURVEYS_COMPLETED` is a progress status of the simulation, with no outcome field. (d) A composite that would no longer be computed the same cannot be started (`COMPOSITE_STALE`). (e) Every survey of one coordinated simulation receives the same facts of the application snapshot. (f) A coordinated simulation only goes forward; another path is another coordinated simulation. (g) Migration `0032` and the setting `survey_coordinated_simulation_enabled`, off by default | PROPOSED for confirmation |
| D-271 | ASG-2B acceptance | "ASG-2B is TECHNICALLY ACCEPTED for simulation-only coordinated multi-survey execution. All previously accepted golden fixture expectations must remain unchanged." Accepted: thin coordination; independent identities, traces and fingerprints; explicit governed ordering; simulation-only COMPLETED→next continuation; no continuation after unresolved or non-completed outcomes; refusal to start stale or uncoordinatable composites; no automatic de-duplication; computed coordinated state; separate call-plan, simulation-permission and operational-eligibility statuses | **Recorded 2026-11-22.** Not a business, UX, production or live-call acceptance. Golden expectations unchanged (82 runs, 14 plans) |
| D-272 | D-270 choices | "Confirm D-270 choices. Preserve all outstanding business policies." | **Confirmed (a)–(d).** Every open policy of D-268 and the table of unresolved policy boundaries stays open |
| D-273 | Development migration `0032` | Authorised on the local development database under the established safeguards; enable coordinated simulation only in local development; demonstrate a synthetic two-survey journey, replay and a blocked scenario; no operational records; no reset or re-seed | **Done 2026-11-22.** `0031` → `0032`; backup `call360_dev_before_0032_20261122.dump` (SHA-256 `b4b87cd9…47d18b7e`), verified row-for-row, restore dry run clean; 124 → 126 tables, 123 of 124 pre-existing tables byte-identical (the other is `alembic_version`); no permission or function added. Evidence: `docs/acceptance/evidence/EVAL-1/dev-migration-0032/` |
| D-274 | Start control when coordinated simulation is unavailable | "When the coordinated simulation feature is unavailable, make the start control unavailable rather than letting the user encounter a predictable server error." | **Done.** A composite now says `states.coordinated_simulation.available` (a property of the server) beside `status` (a property of the composite). The start control is offered only when both hold; otherwise the page says coordinated simulation is not switched on |
| D-275 | EVAL-1 authorised — evaluation grain | "The Evaluation Module must NOT use Survey as its primary evaluation grain." Application → callback journey (evaluation run) → survey execution (evidence-producing) → **control instance (atomic result)** → evidence observation. Synthetic application and simulation contexts only; not linked to operational callback cases | **Built.** `37_…` Part 2 D-A; contract §17.1 |
| D-276 | Mandatory existing-engine assessment before design | Inspect the five modules, control definitions and their governance, materiality/severity, the existing evaluation UI and operational contracts; document ten items; reuse; no competing engine; no duplicate finding-rule language | **Done before design:** `37_EVAL-1_EXISTING_ENGINE_ASSESSMENT_AND_DESIGN.md` Part 1 and the reuse matrix (§7). Central finding: **no control-level result exists anywhere in Call360** |
| D-277 | Governed control mappings | A separate governed mapping, not hardcoded in questions: exact item identity and revision; evidence type; control identity and revision; applicability scope; required evidence; rule-version references; provenance; maker/checker/publisher; immutable published revisions; market authorisation | **Built.** One immutable revision per control and market; three different people (service and database trigger); rule validated by the existing `answer_evaluation.configure`. The control register has no revisions, so a mapping pins a fingerprint of the control row (gap G-E2) |
| D-278 | Applicable-control determination | Use existing governed applicability rules; include controls whose evidence was not collected; preserve unknown applicability; identify missing mappings and policy inputs; do not assert complete coverage without an authoritative applicability policy | **Built, with a stated gap.** No governed applicability rule exists (G-E3). Every control of the register is reported; applicability is the mapping's declaration or a published condition evaluated three-valued; `coverage` is always `NOT_ASSERTED` |
| D-279 | Evidence adapter | Translate SS-03B evidence into the existing engine's input model; never manufacture an answer; never reclassify UNKNOWN as FALSE | **Built.** `control_evaluation.adapt`; table in contract §17.3 |
| D-280 | Journey-level control evaluation | Deterministic; a result per applicable control instance; SATISFIED / NOT_SATISFIED / INSUFFICIENT_EVIDENCE / NOT_APPLICABLE / UNRESOLVED / REQUIRES_REVIEW; preserve the existing vocabulary; no silent reconciliation of contradictory evidence | **Built.** The existing vocabulary is kept unchanged on every observation; the control outcome is new (D-287) |
| D-281 | Findings integration | Reuse the existing Finding Engine and approved rules; every finding references evaluation run, control instance, rule revision, evidence, survey and question identity; no invented severity, remediation, disposition or outcome; SIMULATION-class records only | **Built.** `finding_engine.generate` with the market's published rule set, unchanged. Stored in `survey_evaluation_finding`; the operational `finding` table is never written. Materiality and review routing are operational and not applied |
| D-282 | Incomplete and interrupted simulations | Evaluate available evidence; do not turn POLICY_UNRESOLVED or a refused answer into an invented failure; four processing statuses | **Built.** `COMPLETED` / `INCOMPLETE` / `REQUIRES_REVIEW` / `FAILED_TECHNICALLY`, kept apart from survey completion and from control outcomes |
| D-283 | Evaluation Workbench | Journey-centric view inside the existing experience; survey is a filter and drill-down, not the top-level entity | **Built** at `/survey-studio/evaluations/:evaluationId`, entered from a simulation or a coordinated simulation. Technical verification only; not a UX or screen-reader sign-off |
| D-284 | Persistence and governance | Isolated; immutable or append-only; market- and permission-scoped; reproducible from pinned versions; drift-aware; audited; a revised rule produces a new result; no retention period (OR-1 retained) | **Built.** Migration `0033_survey_control_evaluation` (six insert-only tables, test schema only); two permissions granted to nobody; OR-1 stays open |
| D-285 | EVAL-1 exclusions | No live customer evaluation, operational findings or dispositions, Genesys / GPT Live / telephony, LLM judgements, new compliance policies, scoring or automatic approval, new assignment-rule attributes, Script Studio retirement, correction of answers, destructive migrations | **Held.** |
| D-286 | Stop after EVAL-1 | "Stop after EVAL-1 for review." | **Held.** Nothing committed or pushed; development NOT migrated to `0033` (not authorised) |
| D-287 | **APPROVED with restrictions on 2026-11-22 (see D-290)** — originally proposed: the meaning of a control outcome | The existing engines have no control-level outcome and nothing approved says how a control's evidence combines. EVAL-1 implements ONE combination, `ALL_REQUIRED` ("every placement of every required entry matches or is delivered"), and it takes effect only because each governed mapping **declares** it; any other value gives `UNRESOLVED`. Precedence: conflict → REQUIRES_REVIEW; a required mismatch → NOT_SATISFIED; missing evidence → INSUFFICIENT_EVIDENCE; human assessment → REQUIRES_REVIEW; else SATISFIED | **Closed by D-290.** Approved as an explicitly declared deterministic operator for simulation and technical evaluation only; not an insurance compliance policy |
| D-288 | Choices made in EVAL-1 that the owner may revise | (a) Two new permissions, `survey.evaluation.read` and `survey.evaluate`, rather than reusing `survey.read` / `survey.simulate`: an evaluation shows control and finding-rule data. (b) Mapping governance reuses `survey.edit` / `survey.approve` / `survey.publish`. (c) An evaluation is recomputed from its pins on every read; a difference is `EVALUATION_DRIFT`. (d) Findings are generated only for `APPLICABLE` controls. (e) A survey module left out by the survey's own FALSE condition gives the existing result `NOT_APPLICABLE` for that observation, and the control is then `INSUFFICIENT_EVIDENCE`, not unnecessary. (f) Mapping authoring has an API and no screen. (g) Evaluation needs simulation only (not coordination) to be switched on | **Reconciled one by one in D-291.** |
| D-289 | EVAL-1 acceptance | "Accept EVAL-1 as TECHNICALLY VERIFIED for simulation-only journey-level control evaluation." Accepted: callback journey as the evaluation-run context; applicable control instance as the atomic result grain; survey executions as evidence sources; reuse of the existing answer-evaluation and findings engines; separate governed control mappings; immutable, traceable evaluation records; simulation-only findings; the Evaluation Workbench and its evidence drill-down. "Do not interpret technical acceptance as approval of insurance compliance rules or operational evaluation." | **Recorded 2026-11-22.** Not a business, UX, screen-reader, production or operational acceptance. Golden expectations unchanged |
| D-290 | D-287 ruling — `ALL_REQUIRED` | Approved "as an explicitly declared deterministic evidence-combination operator for simulation and technical evaluation. It is not a universal insurance compliance policy." Rules: (1) all required evidence matches or is delivered → SATISFIED; (2) an unambiguous required mismatch → NOT_SATISFIED; (3) missing required evidence without established mismatch → INSUFFICIENT_EVIDENCE; (4) conflicting evidence → REQUIRES_REVIEW; (5) unknown applicability or missing governed mapping → UNRESOLVED; (6) applicability explicitly false → NOT_APPLICABLE; (7) integrity or replay failure → no trustworthy result asserted. Mismatch and gap together: both explanations kept. An empty required-evidence set never satisfies. SATISFIED never implies application compliance. A comprehensive truth-table test is required | **Done.** Implemented as approved; 27-row truth table and the rules decided before the combination in `tests/test_survey_evaluation.py`. A mapping and a policy both refuse an obligation with no required evidence. Restricted approval: any other combination is still `UNRESOLVED` |
| D-291 | D-288 reconciled, subdecision by subdecision | The owner: "Accept previously authorized architecture-preserving choices, including separated evaluation permissions, isolated simulation persistence and reuse of existing finding rules. Do not treat any policy-changing interpretation as approved merely because it has been implemented." | See the table "D-288 reconciliation" below. **(a), (c) accepted; (f) closed by EVAL-2A; (b), (g) retained as technical choices, not separately ruled; (d), (e) are interpretations with policy effect and are NOT approved** |
| D-292 | Development migration `0033` | Authorised on the local development database, conditional on identity and revision 0032, inventory, verified backup and recovery instructions, additive verification, empty-schema up/down testing, the downgrade guard tested with a published mapping and a recorded evaluation, historical evidence not silently destroyed, no destructive change to Script Studio or operational data, permissions only to the synthetic development identities, evaluation enabled only in local development, one single-survey and one coordinated evaluation demonstrated | **Done 2026-11-22.** `0032` → `0033`; backup `call360_dev_before_0033_20261122.dump` (SHA-256 `349dbbba…98430918`); 126 → 132 tables, 124 of 126 pre-existing byte-identical (the others: `alembic_version`, and `permission` + 2 rows). The downgrade now refuses while a mapping OR a recorded evaluation exists (added and tested). Evidence: `docs/acceptance/evidence/EVAL-2A/dev-migration-0033/` |
| D-293 | EVAL-2A authorised — governed control applicability and coverage | Objective: "Given this application and its approved policy scope, which controls must be assessed, what evidence is required, and which required controls lack sufficient evidence?" Simulation only; the callback journey stays the evaluation context | **Built and verified; awaiting acceptance.** Design `39_…` (written first), report `40_…`, contract §18 |
| D-294 | Control Registry: canonical identity and revision strategy | Assess the existing registry; smallest safe additive extension; reuse existing controls, no second registry; document identity and revisions before implementation | **Done.** The register is not altered. A control is identified by its register code and id and pinned by a fingerprint of its row; a governed **control policy** `(market, code, revision)` says which controls are in scope, their purpose, obligations, applicability and required evidence; a control instance is `(evaluation, control, obligation)` |
| D-295 | Governed control policy | Versioned, three-person governed, independent of survey questions; published, superseded and withdrawn states; immutable published references; no rewriting of existing control definitions | **Built.** `survey_control_policy` + events (guard trigger). There is no effective date: an evaluation names its policy revision (gap G-E8) |
| D-296 | Applicability | Required / not applicable / unknown; missing inputs; missing or inconsistent mappings; deterministic fingerprint; policy version recorded; reuse the three-valued condition evaluation; no invented mappings between rule inputs, call-plan facts and evaluation facts — lineage labelled unverified; an empty applicable set is not full coverage unless a policy expressly says so | **Built.** `policy_evaluation.determine`; `input_lineage: UNVERIFIED` on every determination; `empty_set_is_complete` is false unless the policy sets it |
| D-297 | Coverage | Seven coverage results; four statuses kept apart; full coverage only within a declared, governed scope with a complete applicable set and trustworthy evidence; never inferred from answered questions | **Built.** Instance coverage: the owner's seven plus `HUMAN_ASSESSMENT_PENDING` and `NOT_REQUIRED` (D-300 b). Journey coverage `COMPLETE_WITHIN_POLICY_SCOPE` / `INCOMPLETE` / `NOT_ASSERTED`. Operational compliance eligibility is always `NOT_ESTABLISHED` |
| D-298 | Migration `0034` must not compromise historical evidence | The first draft of `0034` added an `obligation` column to the three EVAL-1 result tables and replaced their keys. The owner: "Prefer an additive migration strategy if a safe one is available." | **Redesigned as purely additive.** Six new tables; no existing table altered; policy-scoped results go to `survey_obligation_result` / `_observation` / `_finding`, linked by `survey_evaluation_policy`. EVAL-1 evaluations are written and read exactly as before. Tested over a schema populated by EVAL-1, with a forced failure and recovery: report `41_…`. **Not applied to development; not authorised there** |
| D-299 | `SET_MATCH` | Approved: a deterministic operator for multiple-choice answers in the existing answer-evaluation engine; modes `INCLUDES_ALL`, `INCLUDES_ANY`, `INCLUDES_NONE`, `EQUALS`; option codes validated against the published option set; order-independent; duplicate handling defined; an explicit empty selection distinct from a missing answer; unanswered and rejected responses distinct; unsupported configurations refused. "Technical answer-matching rules, not an approval of any insurance compliance policy." | **Built** in `app/domain/answer_evaluation.py`. It is in `ALL_METHODS`, not in `METHODS`: Script Studio's list of expected-answer policies is unchanged. Duplicates: refused in a rule, and a selection with a duplicate is `UNRESOLVED` (never collapsed). An empty expected set is refused. 20-row truth table, configuration tests, a persisted-simulation test |
| D-300 | Choices made in EVAL-2A that the owner may revise | (a) A policy *set* with obligations, rather than one policy per control. (b) Two instance-coverage values beyond the owner's seven: `HUMAN_ASSESSMENT_PENDING`, `NOT_REQUIRED`. (c) Coverage `EVIDENCED` includes a control that is `NOT_SATISFIED`: coverage is about evidence. (d) A mapping entry names the policy requirement it supplies; an EVAL-1 mapping without that is "not bound" under a policy and has to be re-proposed. (e) `required` is the policy's, whatever the mapping says. (f) An evaluation names its policy explicitly; without one it is the EVAL-1 evaluation. (g) A superseded or withdrawn policy revision cannot be evaluated under again. (h) An empty expected set is not a supported `SET_MATCH` configuration. (i) Trying a policy or mapping out needs `survey.evaluate`. (j) New setting `survey_control_policy_enabled` | **Open for the owner.** |
| G-E8 | Gap: no effective dating of control policies | Nothing approved says when a policy takes or loses effect, so there is none: an evaluation names an exact revision | Business governance |
| G-E9 | Gap: policy scope is a statement plus one optional condition | Which applications a policy covers in the business sense (products, channels, dates) is not modelled beyond a published condition | Business, Compliance |
| G-E10 | Gap: every control, obligation, condition and mapping is synthetic | A `DECLARED_COMPLETE` synthetic policy is complete only within its own declared scope. It is not regulatory or enterprise coverage, and the screens say so | Compliance |

**D-288 reconciliation (D-291).**

| | Subdecision | Status | Rationale | Still needs |
|---|---|---|---|---|
| a | Two permissions of their own, `survey.evaluation.read` and `survey.evaluate` | **Accepted** — named by the owner ("separated evaluation permissions") | an evaluation shows control and finding-rule data that `survey.read` must not open | who holds them outside development: business governance |
| b | Mapping governance reuses `survey.edit` / `survey.approve` / `survey.publish` | **Retained as a technical choice; not separately ruled** | the owner accepted separately governed mappings and three-person governance; these are the existing three-person permissions | whether control governance should be held by different people than survey governance: business governance |
| c | An evaluation is recomputed from its pins on every read; a difference is `EVALUATION_DRIFT` | **Accepted** — follows from "immutable, traceable evaluation records" and the authorised drift-awareness (D-284) | a historical evaluation never silently appears unchanged | — |
| d | Findings are generated only for `APPLICABLE` controls | **NOT approved — an interpretation with policy effect** | when applicability is unknown, raising a finding would assert an obligation nobody established; not raising one may hide a concern. Implemented as the non-asserting choice | Compliance: whether findings are wanted while applicability is unknown |
| e | A module left out by the survey's own FALSE condition gives `NOT_APPLICABLE` for that observation, and the control is then `INSUFFICIENT_EVIDENCE` | **Consistent with D-290 rule 3; the underlying question is NOT approved** | the survey's condition does not decide whether a control applies — only the governed applicability does — so the evidence is missing | Compliance: whether a survey's own exclusion can ever make a control not applicable |
| f | Mapping authoring has an API and no screen | **Closed by EVAL-2A** | the Controls and evidence builder authors, tries, proposes, approves and publishes mappings | UX sign-off of the builder |
| g | Evaluation needs simulation only (not coordination) to be switched on | **Retained as a technical choice; not separately ruled** | a single-survey journey is a journey; a coordinated one can only exist where coordination was on | — |

| G-E1 | Gap: control satisfaction is not defined anywhere | See D-287 | Business, Compliance |
| G-E2 | Gap: the control register is unversioned and has no lifecycle | A mapping pins a fingerprint of the control row; a control changed afterwards makes its mapping stop speaking for it (`CONTROL_CHANGED_SINCE_MAPPING`) | Owner of the control register |
| G-E3 | Gap: no governed applicability policy for controls | Which controls an application needs is nowhere governed, so complete coverage is never asserted | Business, Compliance |
| G-E4 | Gap: no mapping from catalog facts to evaluation policy facts | The existing fact-based methods (`…_MATCH_POLICY_FACT`) read `premium_term_years`, `premium_amount`, `premium_frequency` from a policy fact snapshot; a synthetic application carries catalog fields. No mapping is approved, so none is applied and such a rule evaluates to `MISSING_EXPECTED_FACT`. Same family as the open input-mapping question of ASG-1/2A | Business, Engineering |
| G-E5 | Gap: no evaluation method for a multiple-choice answer | The existing rule language has none; such evidence is `UNSUPPORTED_EVIDENCE` and cannot be mapped as an answer | Business, Engineering |
| G-E6 | Gap: no finding trigger for an undelivered statement, an unmapped control or an evidence conflict | The existing finding rule language triggers on answer-evaluation results only. These are reported by the evaluation and produce no finding | Business, Compliance |
| G-E7 | Gap: non-answer reasons | A refused input is recorded as refused; whether it means "refused", "did not know" or anything else is undecided, so the existing reasons (`REFUSED`, `UNKNOWN`, `RETRY_LIMIT`) are never claimed | Business, Compliance |
| OR-2 | Rule validation knows one winner only | The existing Assignment Rules validation refuses two rules of equal precedence that can both match (`CONFLICT_SAME_TARGET_TIE`), because for scripts they would be ambiguous. Rules of different requirement groups are meant to match together, so today they must be given different priorities to be publishable, although priority means nothing between groups. Changing that validation is a change to Script Studio and was not made | OPEN |
| OR-3 | The rule language has no replacement or rider attribute | The nine governed rule fields cannot say "this sale replaces a policy" or "this policy has a CI rider". The ASG-2A demonstrations use stand-in conditions. Real replacement and rider requirements need new governed rule attributes (a change to the rule language) or an approved mapping from application facts | OPEN |

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
