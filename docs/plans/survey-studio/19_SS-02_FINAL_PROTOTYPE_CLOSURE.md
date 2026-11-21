# SS-02 — Survey Studio prototype: final closure

**Prepared:** 2026-11-21, on the owner's instruction "SS-02C Final Closure Corrections".
**Status: TECHNICALLY ACCEPTED — PROTOTYPE** (owner, 2026-11-21, "SS-02 Prototype Technical Closure Accepted",
D-149). All six closure corrections are accepted. **The original Survey Studio prototype story is closed for feature
development.** SS-02 is not to be reopened for optional enhancements.

**This acceptance does NOT mean:**

- Formal business-user UX acceptance.
- Screen-reader accessibility sign-off.
- Production readiness.
- Approval of the unresolved no-answer policies.
- Authorisation for backend implementation.

Each of those is a separate future gate — see §8. The proposed architecture direction the owner asked to have
recorded is in §9; it is a proposal for the next assessment, not implemented and not authorised.

**Scope held.** The original Survey Studio prototype story only. SS-03 not started. Script Studio consolidation not
started. No backend, database, migration, API or runtime change (OpenAPI `221985e7…` unchanged; backend clean at
`7228875`). No new dependency. No paid call. Voice Lab and existing Call360 modules untouched. Survey Studio is off
by default. Nothing staged, committed or pushed. Synthetic data only; no wording is approved AIA or MAS language.
**Every submission, approval and publication in the prototype is simulated.**

**Not claimed.** No moderated usability session and no screen-reader session has been run. Formal business-user UX
acceptance is pending.

The checkpoint record is in reports `07`–`18` of this folder. Where this document differs from report `18` on
candidates, publishing or escalation, **this document governs**.

---

## 1. The six closure corrections

| # | Correction | What changed | Decision |
|---|---|---|---|
| 1 | **Immutable submitted candidates** | Submitting freezes a **candidate** — `C-n` — with a revision number, a content fingerprint, a pinned dependency manifest and that manifest's hash. Review, approval and publication refer to the candidate **by its ID**. The author's draft is a separate thing and may go on changing: that neither voids an approval nor moves one. Submitting a changed draft creates the next candidate and **supersedes** an open one; its approval is not carried over. **Undo cannot resurrect an approval:** a draft made byte-for-byte identical to a superseded, once-approved candidate is not approved and cannot be published | D-143 |
| 2 | **Separate Publisher capability** | Three permissions — Author, Checker, Publisher — and none implies another. Publishing needs the Publisher permission **and** a different person from the submitter. The checker who approved a candidate cannot publish it merely by being a checker. One invented person holds all three permissions and still cannot approve or publish her own submission | D-144 |
| 3 | **Escalate is terminal everywhere** | A module that ends with Escalate ends the call with Escalate — by a mandatory answer, a single-choice route, a first-matching rule, an optional interruption or a decision. The survey's route for that outcome is governed from the moment the outcome appears; the Composer offers only that ending; the survey graph refuses any other connection; validation rejects any other mapping; the engine never follows one. The ending is still labelled truthfully: "mandatory escalation" only when a mandatory answer caused it | D-145 |
| 4 | **Separate skip dispositions retained** | No change. "After a jump" must be chosen explicitly; "in sequence" defaults to continue. Accepted fixture semantics preserved | D-146 |
| 5 | **Graph menus near the bottom** | Menus in both graph editors are placed against the window: below when it fits, otherwise above, otherwise on the side with more room with their height limited to that room, scrolling inside. They can no longer run off the screen | D-147 |
| 6 | **No-answer contract** | Marked UNRESOLVED throughout; every decision has a status and two "blocks" columns. No policy value was added | D-148 |

Two things found and fixed along the way, neither waived:

- **A focus race.** Opening a card's side panel in the graph scheduled keyboard focus onto the panel a moment later.
  If the author had already tabbed into the panel and opened a menu, that late focus closed it. The delayed focus now
  never takes focus from a control inside the panel.
- **Four earlier journeys asserted the old escalation behaviour** (a new Escalate outcome left "undecided", or routed
  to a later module as a parity example). They were updated to the corrected rule; the graph journey now also
  asserts that the survey graph refuses to route an escalation onward and leaves the model untouched.

---

## 2. What is complete

Complete = built in the prototype and exercised by automated tests. It is **not** a statement that a UX requirement
is met; that is §3.

| Area | Complete |
|---|---|
| **Library and survey creation** | Module library with search; create a survey in three decisions; blank survey or start template |
| **Lego Composer** | Start → module cards → end; add at any gap; reorder by drag, keyboard or buttons; activation and eligibility as one readable sentence; one route per named outcome; remove with impact |
| **Guided Module Builder** | Numbered story; insert on any route; yes/no, single-choice, multi-select and free-text questions; options with exclusive, Other-with-text and interruption classes; three routing modes; first-matching rules; follow-up queues with order, de-duplication, interruptions and rejoin; decision points with Match / Otherwise / Unknown; shared questions with "new version" or "separate question"; delete with impact; undo and redo of the model itself |
| **Advanced Graph** | Module graph and survey graph over the same model as Guided; automatic layout; select, connect, re-point and disconnect routes by pointer or keyboard; refusals with reasons; menus that stay on screen |
| **Conditions** | Library and one-off conditions; nested all/any/not; typed, label-free references to earlier answers; an explicit policy for missing information everywhere; no silent version changes |
| **Business rules** | A jump selects a candidate and never bypasses eligibility; activation and eligibility independent; skip dispositions for jumps and for sequence; six distinct terminal states; mandatory escalation precedence; Escalate terminal in every routing mode; forward-only, no re-entry |
| **Journey Simulator** | Eleven synthetic customers; step, back, restart, run all; every decision explained with the values read; two customers compared; clearly marked as not the Call360 runtime |
| **Validation** | Nine areas; blocker / warning / information; where, why and what to do; click-to-fix; warnings acknowledged with a reason; an invalid survey is never "ready" because a customer completes it |
| **Revision comparison** | Modules, wording, routing, conditions, pinned versions; renumbering reported as renumbering; affected journeys; what needs revalidation, wording approval and re-approval |
| **Review and publishing (simulated)** | Immutable candidates; maker ≠ checker by identity; separate publisher; send back with a comment; supersede; withdraw; immutable versions; history; audit trail by candidate ID |
| **One journey** | Library → Compose → Build modules → Simulate → Validate → Review and publish, with the state of each step |
| **Golden fixtures** | 19 fixtures in four schema versions, 63 expected runs, each generated and checked by a reference interpreter and reproduced by the prototype's engine |

---

## 3. What requires business-user testing

None of the following has evidence yet. Each needs real authors, reviewers or assistive-technology users.

| Item | Requirement | What is needed |
|---|---|---|
| First-time author builds a 3-module survey | UX-GATE-01 | Moderated, timed task |
| Single-select with five option routes | UX-GATE-02 | Moderated, timed task |
| Multi-select with Other and two follow-ups | UX-GATE-03 | Moderated, timed task |
| Yes/No question added into an existing branch | UX-GATE-04 | Moderated, timed task |
| Which of six modules runs for a named customer | UX-GATE-05 | Comprehension test |
| Find a question in a 40-question module | UX-GATE-06 | Moderated, timed task (a 40-question sample module exists) |
| Understanding a five-way merge | UX-GATE-07 | Comprehension test |
| A module card is understood in three seconds | SS-UXE-005 | Observation |
| Screen-reader use of authoring, graph, validation and review | UX-GATE-10, SS-UXE-024 | A screen-reader session. Only automated scans and keyboard journeys exist |
| Do reviewers find the comparison and the candidate identity sufficient to approve | SS-UXE-029 | Reviewer walkthrough |
| Is the wording of findings, traces and refusals clear to non-technical staff | SS-UXE-025 | Reviewer walkthrough |
| Design system and visual direction | SS-UXE-028, UX-GATE-12 | Design review and recorded sign-off |
| Usability sign-off, separate from functional sign-off | SS-UXE-030 | Product owner, design and a business representative |
| Before/after feedback on the seven baseline screenshots; performance recordings for a medium and a large survey | §18.7 review evidence | Not produced |

Built only in part, and worth observing in the same sessions: library filters by tag, owner and status (search only);
launching the simulator from a selected question (from the survey only); side-by-side edit and test (the simulator is
its own step). Not built: favourites and recents, a command palette, batch import, "save scenario".

---

## 4. What remains deferred to the backend

Nothing below exists. The prototype shows how each would *look*; none of it is implemented, and none may be assumed.

| Deferred | Why it cannot be a prototype matter |
|---|---|
| **Persistence** — saving, loading, concurrent editing, conflict handling, "Saving / Saved / Offline / Conflict" | The prototype keeps everything in memory and a reload resets it (SS-UXE-021, UX-GATE-11) |
| **Server-side validation** of the exact saved revision and its dependency manifest | Validation runs in the browser by the prototype's own rules. "Ready" must come from the server |
| **Real governance** — candidates, approvals, publications and the audit trail as immutable server records | All simulated. Real records need storage, immutability and audit events |
| **Authorisation** — Author, Checker and Publisher as enforced server-side permissions on every endpoint and object; maker ≠ checker and submitter ≠ publisher enforced on real identities | The prototype's people are invented and the checks run in the browser |
| **The execution engine** — the survey runtime that conducts a call | The simulator is a demonstration evaluator. The real engine is the second, authoritative implementation of the contract |
| **Golden fixtures as contract tests** for that engine | 19 fixtures exist; the engine must reproduce them |
| **Controlled delivery and evidence of approved wording** | A prompt is not evidence that wording was spoken |
| **Non-answer handling** — silence, refusal, disconnection, repeats | Undecided (§5); not in the prototype at all |
| **Pause, resume, back and edit during a real call**; lifecycle gates above the survey | Conversation lifecycle, outside the survey graph |
| **Assignment of a published survey to callback cases**, and pinning per case and session | Depends on real publication |
| **Voice** — browser audio, later Genesys | Later stages; separate adapters |
| **Migration or consolidation with Script Studio** | Explicitly out of scope here |

---

## 5. Decisions that block operational implementation

### 5.1 Block building the survey runtime at all
From `17_SS-02C_NO_ANSWER_CONTRACT.md` — **all unresolved, no value proposed**:

| Decision | Subject | Approver |
|---|---|---|
| **D-NA-1** | The reasons a question is unanswered | Business, Compliance |
| D-NA-3 | Whether unintelligible responses share the silence counter | Business, Engineering |
| D-NA-4 | Whether a refusal is confirmed before it is recorded | Business, Compliance |
| **D-NA-5** | Question classes and where refusal is acceptable | Business, Compliance |
| D-NA-6 | How an optional question is left blank on a voice call | Business, Engineering |
| D-NA-7 | Whether a disconnected run resumes or restarts | Business, Compliance, Engineering |
| D-NA-8 | Wording on repeats | Business, Compliance |
| **D-NA-9** | How a non-answer is routed | Business, Engineering |
| **D-NA-10** | Whether "mandatory" and "required" are one property | Business, Compliance |
| D-NA-11 | Whether a follow-up queue continues past an unanswered follow-up | Business, Compliance |
| D-NA-12 | Refusal or silence on a question with a mandatory-escalation option | Compliance |
| **D-NA-13** | The catalogued outcome for "no answer obtained" | Business, Compliance |
| **D-NA-14** | A terminal state for disconnection | Business, Engineering |
| **D-NA-15** | Precedence of disconnection, escalation, non-answer and routing | Business, Compliance, Engineering |

The seven in bold shape contracts the first backend checkpoint would have to fix, so they are needed **before any
backend work on the runtime**.

### 5.2 Block the first backend checkpoint for governance
| Decision | Why |
|---|---|
| **Who holds the Publisher permission**, and whether the approver of a candidate may also publish it | The prototype enforces "submitter ≠ publisher" only. A real rule is needed |
| **Whether a draft is locked while a candidate is in review** | The prototype lets the author keep editing a separate draft, as instructed. Confirm that is the operational rule |
| **What "approved wording" is in Call360** — who approves, how it is recorded, how it relates to Script Studio's governed artefacts | The prototype's wording approval is simulated; all wording is synthetic |
| **The escalation-handling workflow** — what happens after a call ends with Escalate | Explicitly not invented here (D-141) |
| **Whether a module may carry both an activation trigger and an eligibility condition in the stored schema** as built, and the two skip dispositions as two fields | Built so in the prototype (D-139, D-146); the stored schema must confirm it |
| **The existing AIA/SBQ process** | Still a working hypothesis pending business confirmation, not an approved SOP |

### 5.3 Block any real call (not the build)
D-NA-2, D-NA-16, D-NA-17; the values of `NA-P-RESPONSE-WINDOW`, `NA-P-REPEATS-PER-QUESTION`, `NA-P-REPEATS-PER-CALL`
and `NA-P-REFUSALS-PER-CALL`; approved wording for every question; retention and access rules for evidence.

---

## 6. Final closure evidence

All in `docs/acceptance/evidence/SS-02-closure/`.

| Check | Result | File |
|---|---|---|
| Fixtures /1 — 8 fixtures, 25 runs, 7 rejected answers | reproduced | `fixture_rule_and_parity_verification.txt` |
| Fixtures /2 — 6 fixtures, 18 runs, 2 rejected answers | reproduced | same |
| Fixtures /3 — 4 fixtures, 16 runs | reproduced | same |
| Fixtures /4 (new) — 1 fixture, 4 runs, 3 expected validation errors | reproduced; self-checked by its reference | same |
| All 19 fixture files unchanged on disk | regenerate byte-for-byte from four interpreters | `checks.txt` |
| Guided/Graph parity | pass — 18 model tests, and in the browser journeys | `fixture_rule_and_parity_verification.txt`, `prototype_journeys.txt` |
| Validation, governance (immutable candidates, publisher, undo) and comparison rules | pass — 24 tests | `fixture_rule_and_parity_verification.txt` |
| Frontend unit tests | **314 passed** (195 in the prototype) | `checks.txt` |
| Prototype journeys in Chromium | **11 of 11 passed** | `prototype_journeys.txt` |
| Accessibility scans in those journeys (axe, WCAG 2.2 AA tags) | 0 serious or critical | `prototype_journeys.txt` |
| Standard Playwright suite, prototype **off** | **33 of 33 passed** | `playwright_standard.txt` |
| Type check, lint, dependency audit, secret scan, API contract | clean; 0 vulnerabilities; no leaks; unchanged | `checks.txt` |
| Specs validator | PASS, 63 checks | — |

### The corrected interactions, captured (`screens/`)

| Asked for | Screenshot | What it shows |
|---|---|---|
| Approval | `CL04-candidate-frozen-draft-moves-on` | Candidate C-3 still approved with its ID, revision, fingerprint and manifest, while the draft has moved on; the approval "cannot be moved onto the draft" |
| Approval | `CL05-undo-does-not-resurrect-approval` | After a new candidate was submitted and the edit undone: C-3 is "superseded", the audit trail says its approval was not carried over, and there is nothing to publish |
| Approval | `GV06-reviewer-inspection`, `GV09-no-self-approval`, `GV10-approved` | Inspection of a frozen candidate; no self-approval; approval bound to the candidate |
| Publication | `CL01-checker-cannot-publish` | The approving checker is refused: the Publisher permission is separate |
| Publication | `CL02-submitter-cannot-publish` | A person holding the Publisher permission is refused for a candidate she submitted |
| Publication | `GV12-publication-history-and-audit` | Version 2.0 = candidate C-5, revision 5, with its manifest; three different people; the audit trail by candidate |
| Escalation | `CL03-ordinary-escalation-is-terminal` | An Escalate outcome reached by an ordinary answer: locked, and only "End the call: Escalate" is offered |
| Escalation | `SJ10b-ordinary-escalation-ends-the-call` | The simulator ends the call with Escalate — an ordinary ending, not a "mandatory escalation" |
| Graph menu | `CL06-graph-menu-near-bottom-survey` | Survey graph on a short window: the lowest route's menu stays on screen |
| Graph menu | `CL07-graph-menu-near-bottom-module` | Module graph on a very short window: the route toolbar's menu opens upward and scrolls inside |

The full walkthrough set (`W01`–`W05`, `GV01`–`GV13`) was re-captured in the same run.

---

## 7. To review

Running at `http://localhost:5173/survey-studio` (reload first; a reload resets everything).

1. **Prototype · not saved → Add a demonstration survey and simulate it**, then **Validate**, acknowledge the two
   warnings, and **Review and publish → Submit**. Note candidate **C-2**, its revision and its manifest.
2. Approve it as **Arjun Menon**. Try to publish as Arjun, as **Mei Ling Tan**, then as **Devi Krishnan** (do not
   publish yet).
3. As Mei Ling Tan, change any route in **Compose** and return: C-2 is still approved; the draft is shown separately.
4. Submit the changed draft: **C-3** is in review, C-2 is superseded. **Undo** the change in Compose and return:
   nothing is approved and nothing can be published.
5. In **Build modules**, open *General verification*, edit a copy, and send "No" to *End module: Escalate*. In
   Compose, open the new *Escalate* route.
6. Open a module's **Graph**, make the window short, select a route and choose **Change destination**.

SS-03 has not been started. Script Studio consolidation has not been started.

---

## 8. Owner acceptance, what is preserved, and the future gates

**Accepted 2026-11-21 (D-149):** SS-02 is TECHNICALLY COMPLETE on the basis of this document; all six closure
corrections are accepted; the prototype story is closed for feature development. Nothing was committed or pushed by
this acceptance; committing needs its own authorisation.

### 8.1 Preserved as the SS-02 baseline (D-150) — do not delete, regenerate differently or overwrite

| Item | Where |
|---|---|
| The 19 golden fixtures, 63 expected runs, and their four reference interpreters | `docs/plans/survey-studio/fixtures/` |
| Regression evidence (checks, fixture and parity verification, journeys, standard Playwright, screens) | `docs/acceptance/evidence/SS-02A/` … `SS-02C/`, `SS-02-closure/` |
| The UX acceptance matrix (prototype acceptance checklist against the UX excellence requirements) | `18_SS-02C_FINAL_PROTOTYPE_REPORT.md`; usability gates still without evidence in §3 of this document |
| Final closure documentation | this document; reports `07`–`18`; the no-answer contract `17_…`; the decision register `06_…` |
| The prototype itself and its tests | `Call360-frontend/src/features/surveystudio/`, `e2e/prototype/` (behind `VITE_SURVEY_STUDIO_PROTOTYPE`, off by default) |

### 8.2 Future gates (D-151) — each needs its own explicit owner decision; none is opened by this acceptance

| Gate | What it decides | Status | Source |
|---|---|---|---|
| **G-1 Business-user UX acceptance** | The seven timed usability gates, reviewer walkthroughs, design sign-off | NOT STARTED — no evidence | §3 |
| **G-2 Screen-reader accessibility sign-off** | Use with a screen reader by a person; automated scans are not this | NOT STARTED — no evidence | §3 |
| **G-3 No-answer policy** | D-NA-1…D-NA-17 and the four `NA-P-…` values | UNRESOLVED — 14 block the runtime build, 7 of them before any backend work | §5.1, §5.3, `17_…` §10 |
| **G-4 Governance rules** | Who holds Publisher and whether the approver may publish; draft locking during review; what "approved wording" is; the escalation-handling workflow; stored-schema confirmation of activation + eligibility and the two skip dispositions; the AIA/SBQ process | UNRESOLVED | §5.2 |
| **G-5 Remaining SS-01 proposals** | SS-D-03, 04, 05, 08, 11–16, 19 and prototype decisions P-6…P-12 as amended | PROPOSED, not decided | `06_…` Summary |
| **G-6 Architecture assessment** | The proposed direction in §9 | PROPOSED — recorded only | §9 |
| **G-7 Backend implementation (SS-03)** | Persistence, server-side validation, real governance, the execution engine | NOT AUTHORISED, not started | §4 |
| **G-8 Production readiness** | Everything above, plus security, operations and compliance review | NOT ASSESSED | — |

---

## 9. Proposed architecture direction — RECORDED ONLY (D-152)

**Status: PROPOSED ARCHITECTURE CHANGE, for the next assessment. Not implemented. Not authorised. No requirement,
ADR, contract or code has been changed for it.** Recorded in the owner's words of 2026-11-21:

1. Survey Studio becomes the single authoritative journey-authoring experience.
2. Essential Script Studio features are rebuilt or incorporated into Survey Studio.
3. Redundant Script Studio functionality is eventually retired after safe migration.
4. The execution harness assembles customer-specific call plans from approved survey definitions and application
   data.
5. Live customer answers dynamically select subsequent approved dialogue.

**Constraints that stand until an assessment is authorised and decided:**

- **Script Studio is not modified and not removed.** Its nine S2-A.2 files remain untouched.
- This direction goes further than the current rulings SS-D-02 (wording and delivery stay under the existing
  approved script governance) and SS-D-20 (Script Studio coexists temporarily; "Wording & Delivery" is a capability
  within Survey Studio), and it touches SS-D-17 (runtime last) and the workspace rule that exact wording needs
  controlled delivery and evidence. **Those rulings remain in force**; the assessment must say which of them the
  proposal would amend.
- Points 4 and 5 depend on gates G-3 and G-4: an execution harness cannot be specified while non-answer behaviour
  and approved-wording governance are undecided.
- Nothing here authorises SS-03 or any backend, database, migration, API or runtime work.
