# SS-02C — Final prototype checkpoint: rule corrections, validation, comparison, review and publishing

**Checkpoint:** SS-02C, authorised by the owner on 2026-11-21 ("Accept SS-02B.3.1 and Authorize SS-02C — final
prototype checkpoint").
**Status:** IMPLEMENTED AND TECHNICALLY VERIFIED — **presented for the owner's end-to-end acceptance review.**
SS-02B.3.1 was accepted as technically verified. **Formal business-user UX acceptance remains pending. No moderated
usability session and no screen-reader session has been run; none is claimed. SS-03 and all backend implementation
are not started and not authorised.**

> **Superseded in part on 2026-11-21 by `19_SS-02_FINAL_PROTOTYPE_CLOSURE.md`** (owner's closure corrections D-143…D-148):
> submitted candidates are immutable and approvals bind to a candidate ID — undo no longer restores an approval;
> publishing needs a separate Publisher permission; Escalate is terminal in every routing mode. Where this report
> says otherwise, report 19 governs.

Frontend prototype and specification work only. No backend, database, migration, API or operational-runtime change
(OpenAPI `221985e7…` unchanged; backend clean at `7228875`). No new dependency. No paid model or voice call; Voice
Lab and existing Call360 modules untouched. Survey Studio is off by default. Nothing staged, committed or pushed.
Synthetic data only; no wording here is approved AIA or MAS language.

**Every submission, approval and publication in this prototype is simulated**, held in memory in one browser tab,
between invented people. None is a governance act and no survey is published to Call360.

---

## Part A — The remaining decisions, resolved

| Ruling | What was built | Contract | Fixture |
|---|---|---|---|
| **A-1** A jump is a valid activation; it never bypasses eligibility (D-138) | A jump selects a module even when its trigger did not fire; its eligibility is still checked. Trace: "It was selected by a jump … In sequence it is selected only after X ends with Y; an explicit jump also selects it. A jump does not bypass eligibility: it is eligible when …" | `04` §2.2c (a) | H2 |
| **A-2** Activation and eligibility are independent (D-139) | A module instance now has two separate settings: `activation` (when it is selected) and `entry` (whether it may run). Both can be set together. The earlier shape is still read and means the same. The condition drawer shows them as "1 · When it is selected" and "2 · Whether it may run", each with a plain explanation; the card reads "after X ends with Y, and only when …" | `04` §2.2c (b) | H1 |
| **A-3** Skip disposition for sequence and jumps (D-140) | A module reached **in sequence** that does not apply continues with the next module by default; a later module or an approved terminal outcome can be configured instead (in the drawer; shown on the card once set). A **jump target** must still have its disposition chosen — nothing is invented. Forward only; a removed destination becomes undecided, never re-pointed | `04` §2.2c (c) | H3 |
| **A-4** Mandatory escalation across the whole survey (D-141) | A module that ends because of a mandatory-escalation answer **always** ends the call with Escalate, whatever the survey's route for that outcome says. Any other mapping is a blocker; the Composer offers only the governed ending for that outcome and the survey graph refuses any other connection with the reason | `04` §2.2c (d) | H4 |
| **A-5** No-answer contract (D-142) | A decision-ready document; nothing built | `17_SS-02C_NO_ANSWER_CONTRACT.md` | — |

**One implementation choice to confirm (A-3).** I used **two** members — the existing "after a jump" disposition and
a new "in sequence" one that defaults to *continue* — rather than a single one. A single member would have changed
the meaning of an accepted fixture (G1: a module with a jump disposition, skipped in sequence, continues). With two,
every accepted fixture keeps its expectation and both behaviours you asked for exist.

**A defect found and fixed by the A-4 tests.** A mandatory-escalation answer under *first-matching-rule* routing ended
the module correctly but was not flagged as mandatory at survey level, so a survey route could have continued. It is
now mandatory under every routing mode (single choice, rules, follow-up queue), and tested for each.

**A-4 is tested across:** graph edits (the survey graph refuses to connect a mandatory outcome anywhere but its own
ending); rule-based routing; multi-select priority (the mandatory answer leads over an interruption configured
before it); module outcomes; and five wrong survey-level transitions — continue, jump, normal completion, another
exception, review halt — each rejected by validation and never followed by the engine.

**A-5 in brief.** `17_…` covers silence and timeouts, explicit refusal, optional blank answers, call disconnection,
retry and repeat limits, approved wording on repeats, mandatory questions, termination and escalation outcomes,
evidence and audit events, and voice versus non-voice semantics. It proposes **no** duration and **no** count: each
is a named parameter with an owner. It lists **17 decisions** (D-NA-1…17) with who must approve each, and separates
the seven needed before any backend work from those needed before any real call.

---

## Part B — Validation experience

A new step, **Validate**, replaces the readiness popover as the place to see what stands between a draft and review.

| Asked for | Where |
|---|---|
| Survey-level structural validity | Group **Structure**; the verdict banner |
| Unresolved routes and unreachable nodes | Groups **Routes** and **Structure** |
| Invalid or missing eligibility policies | Group **Activation and eligibility** |
| Mandatory escalation violations | Group **Mandatory escalation** (module level and survey level) |
| Question and option validation | Group **Questions and options** |
| Reusable dependency versions | Group **Reusable versions** + the *Pinned versions* table; a newer approved version raises a warning and is never applied |
| Wording approval requirements | Group **Wording approval** + the list of wording the checker must read |
| Missing governance decisions | Group **Governance decisions** (for example: no-answer behaviour is undecided) |
| Readiness for review and publishing | The verdict banner; the journey strip; the checklist on the Review step |

- **Severity** is stated in words and by an icon, never by colour alone: **Blocker** (must be fixed), **Warning**
  (fix or acknowledge), **For information**.
- Each finding gives its **area, module and question**, **why it matters** in plain English, **what to do**, and a
  **Go to it** button that opens the exact card, drawer or question.
- A **blocker cannot be acknowledged**. A **warning** can, only with a written reason, which is shown to the
  reviewer and kept in the audit trail.
- **A structurally invalid survey is never "ready" because a synthetic customer completes it.** Readiness is decided
  by the rules alone; journey coverage is shown as evidence, can add a finding (a draft that cannot run for a
  customer; a module no customer reaches) and can never remove one. Tested directly: a survey with an unrouted
  outcome that the ordinary customer never takes still completes for that customer — and is still refused.

---

## Part C — Version comparison

On the Review step, **Compare revisions** compares any two of: a published version, a submitted candidate, the
current draft.

| Asked for | Shown as |
|---|---|
| Added, removed and modified modules | **Modules** — added / removed / order changed |
| Question wording changes | **Questions and wording** — before and after, marked *Needs wording approval* |
| Routing changes | **Routing** — survey-level routes, skip dispositions, and where each question leads |
| Condition changes | **Activation and eligibility conditions** — in sentences, including the missing-information policy |
| Shared dependency version changes | **Pinned versions** — module, question and condition versions |
| Impacted journeys | The same synthetic customers played through both revisions; *affected* = the questions asked, the modules run or the ending differ |
| What requires revalidation or reapproval | **What this change requires** — revalidation; wording approval (count); re-approval; journeys to simulate again |

**Display numbers are not identities.** A question is matched by its place in the module and its question code.
Inserting a question renumbers the ones after it; those appear as "*N questions were only renumbered (Q2 → Q3 …)* —
a display number is not a question's identity", not as changes. Tested: an insertion yields exactly one added
question, one routing change and two renumberings.

---

## Part D — Maker-checker and publishing (simulated)

| Step | Demonstrated |
|---|---|
| 1 Draft | The draft and its fingerprint; "Draft with changes since version 1.0" |
| 2 Validate | Part B |
| 3 Submit for review | Author only; refused with the reason when not ready; a change note is required; a frozen copy becomes the candidate |
| 4 Reviewer inspection | Who submitted and why; what changed since the last version; the wording to approve; pinned versions; acknowledged warnings with their reasons; links to simulate and to the validation result |
| 5 Approve or reject | Approval requires confirming the wording was read; sending back requires a comment, which the author then sees |
| 6 Revision comparison | Part C |
| 7 Publish an immutable version | Version *n*.0: an exact copy of the approved candidate with its versions pinned. Editing the draft afterwards does not change it (asserted) |
| 8 Publication history and audit | Each version with submitter, approver, publisher, fingerprint, pinned versions and wording as approved; an audit trail of every step, who took it and the candidate it applied to |

- **Separation of author and checker** is by identity, not only by role. Three invented people: an author, a checker,
  and a team lead who holds **both** roles — and still cannot approve her own submission ("Holding the checker role is
  not enough: the maker and the checker must be different people").
- **A changed candidate invalidates a previous approval.** An approval belongs to one fingerprint. After any edit the
  Review step says "The earlier approval no longer applies", shows what changed, withdraws the Publish action and
  asks for a fresh review. Undoing the edit restores the approved candidate and with it the approval.
- **Labelling.** A standing banner on the Review step; "(simulated)" on Submit, Approve, Publish and on each audit
  action; "Simulated" on every published version; "Acting as — simulated" on the role switch. The demonstration
  survey's earlier version 1.0 is marked "Seeded with the demonstration".

---

## Part E — One coherent journey

A strip on every survey screen: **Library → Compose → Build modules → Simulate → Validate → Review and publish**,
showing where you are and the state of each step (blockers, "Ready for review", "In review", "Published").

**Two screens were added, not more:** *Validate*, and *Review and publish* (with comparison and history as tabs).
On the editing screens the strip is one slim row and the role switch is omitted, to keep the canvas height.

### The nine storyboard screens

| Screen | Where it is | Changes or omissions |
|---|---|---|
| A · Studio Home and Library | Survey Studio home | As accepted in SS-02A. **Not built:** favourites, recents, an "assigned reviews" list, filters by tag/owner/status |
| B · Survey Lego Composer | Compose | + journey strip; + lock mark and single choice on a mandatory-escalation outcome; + "In sequence, but does not apply" row once configured |
| C · Entry Condition Drawer | Compose → the "Runs …" chip | **Changed:** now two settings — activation, then eligibility — and the in-sequence disposition |
| D · Guided Module Builder | Build modules | + journey strip (slim). Otherwise as accepted |
| E · Choice and Follow-up Designer | Inside a question card | As accepted |
| F · Internal Condition Drawer | A decision card | As accepted |
| G · Advanced Graph | Build modules → Graph; Compose → Graph | + mandatory-escalation routes labelled and protected in the survey graph |
| H · What-if Lab | Simulate | **Deviation (accepted in SS-02B.3):** a full page, not a panel over the editor. **Not built:** "Save scenario" |
| I · Validation and Publish | Validate; Review and publish | **Split in two steps.** Groups differ from the storyboard list: *Scenario coverage* is "Journey coverage"; there is **no "Accessibility" group** (the prototype has nothing to check about a survey's accessibility); *Approval* is the Review step |

### The ten interaction stories

| Story | Automated journey |
|---|---|
| 01 Add Suitability after General | `survey-studio.proto.ts` |
| 02 Five-choice single-select | `survey-studio.proto.ts` |
| 03 Add "Other — please specify" | `survey-studio.proto.ts` |
| 04 Premium + Benefits follow-ups | `survey-studio.proto.ts`, `refinements.proto.ts` |
| 05 An answer that interrupts the follow-ups and escalates | `refinements.proto.ts` (interruptions), `simulator.proto.ts` (the mandatory-escalation customer) |
| 06 Compound entry rule | `survey-studio.proto.ts`, `conditions.proto.ts` |
| 07 Delete a question with inbound routes | `survey-studio.proto.ts`, `refinements.proto.ts` |
| 08 Guided → Graph → Guided | `graph.proto.ts`, `connections.proto.ts` |
| 09 Two customer profiles | `simulator.proto.ts` |
| 10 Submit an invalid draft | **`governance.proto.ts` (new)** — blockers grouped and navigable, click-to-fix, Submit disabled with the reason |

### The demonstration questionnaire
"New business callback (demonstration)": **eight reusable modules** from the shared library (general verification,
suitability, high-value review, policy replacement, affordability, clarifications, specialist call, closing);
**conditional modules** (product is ILP; high value; replacement; older customer) and **conditional questions**
(two decision points in the affordability module); a **multi-select with follow-ups** and interruptions
(clarifications); a **shared question** ("Are you content to proceed with this policy?", the same definition in
Clarifications and in the specialist call — added in this checkpoint so the demonstration shows one); and a
**mandatory escalation** ("I did not agree to this policy"). Eleven synthetic customers.

---

## Part F — Evidence

| Check | Result | Evidence (`docs/acceptance/evidence/SS-02C/`) |
|---|---|---|
| Fixtures schema /1 — 8 fixtures, 25 runs, 7 rejected answers | all reproduced by the simulator | `fixture_and_rule_verification.txt` |
| Fixtures schema /2 — 6 fixtures, 18 runs, 2 rejected answers | all reproduced | same |
| Fixtures schema /3 (new) — 4 fixtures, 16 runs, 2 expected validation errors | all reproduced; self-checked by the Python reference | same; `checks.txt` |
| All 18 fixtures unchanged on disk | F, G and H regenerate byte-for-byte from their three interpreters | `checks.txt` |
| Mandatory escalation paths; skip dispositions; activation × eligibility | unit tests pass | `fixture_and_rule_verification.txt` |
| Validation, lifecycle and comparison rules | 21 unit tests pass | same |
| Guided/Graph parity and deterministic simulation | pass | `checks.txt` |
| Frontend unit tests | **305 passed** (186 in the prototype) | `checks.txt` |
| Prototype journeys in Chromium | **10 of 10 passed** (the new end-to-end walkthrough plus the nine earlier ones) | `prototype_journeys.txt` |
| Accessibility scans (axe, WCAG 2.2 AA tags) on validation, reviewer inspection, comparison, history | 0 serious or critical | `prototype_journeys.txt` |
| Standard Playwright suite, prototype **off** | **33 of 33 passed** | `playwright_standard.txt` |
| Type check, lint, dependency audit, secret scan, API contract | clean; 0 vulnerabilities; no leaks; unchanged | `checks.txt` |
| Specs validator | PASS, 63 checks | — |

**Walkthrough screenshots** (`screens/`): `W01`–`W05` library, compose, guided builder, graph, simulate;
`GV01`–`GV13` validation with warnings, validation with blockers, submit refused, ready, pinned versions, reviewer
inspection, sent back, comparison, no self-approval, approved, approval voided by a change, history and audit,
activation and eligibility; `BR1`–`BR6` the business-rule cases of SS-02B.3.1, re-captured.

---

## Prototype acceptance checklist — against the UX excellence requirements

**Shown** = present in the prototype and exercised by an automated journey. **Partly** = present in part; the gap is
stated. **Not shown** = not in the prototype. **Owner** = needs evidence only people can give. This is a statement
of what exists, not a claim that a requirement is *met*: each P0 "observable acceptance" still needs your review.

| ID | Requirement | Status | Note |
|---|---|---|---|
| SS-UXE-001 | Lego blocks are the primary metaphor | Shown | At 8 modules; 20 modules not exercised |
| SS-UXE-002 | Create survey in at most three decisions | Shown | |
| SS-UXE-003 | Library search, tags, type, owner, status, reuse | Partly | Search-as-you-type and add from the composer; no tag/owner/status filters |
| SS-UXE-004 | "+ Add here" at every gap | Shown | |
| SS-UXE-005 | Card shows eligibility, outcomes, version, count | Shown | "Understood in three seconds" is a usability claim — Owner |
| SS-UXE-006 | Inline question insertion on every route | Shown | |
| SS-UXE-007 | Routing mode chosen on the card | Shown | |
| SS-UXE-008 | Option editor in context | Shown | |
| SS-UXE-009 | Multi-select modes with example and preview | Shown | |
| SS-UXE-010 | Follow-up queue: reorder, dedupe, rejoin | Shown | |
| SS-UXE-011 | Collapsed branches never hide a blocker | Shown | |
| SS-UXE-012 | Shared destination badge and "view incoming" | Shown | |
| SS-UXE-013 | Searchable routing picker with "create here" | Shown | |
| SS-UXE-014 | Contextual inspector, canvas stays visible | Shown | |
| SS-UXE-015 | Conditions as short sentences | Shown | Now also "after X ends with Y, and only when …" |
| SS-UXE-016 | Use existing / create new / fork is explicit | Shown | |
| SS-UXE-017 | What-if test launched from any module or question | Partly | From the survey and the journey strip; not focused on a selected question |
| SS-UXE-018 | Simulator explains every decision | Shown | |
| SS-UXE-019 | Undo/redo restores the canonical state | Shown | Review state is deliberately outside undo; undoing an edit restores an approval |
| SS-UXE-020 | Delete/change shows impact first | Shown | |
| SS-UXE-021 | Saving / Saved / Offline / Conflict states | Not shown | The prototype saves nothing; needs the server (SS-03) |
| SS-UXE-022 | Graph lays out automatically and keeps semantics | Shown | |
| SS-UXE-023 | Graph usable with many choice ports | Shown | |
| SS-UXE-024 | Full keyboard parity; screen reader | Partly | Keyboard journeys automated for authoring and graph editing; the new screens use native controls; **no screen-reader session** |
| SS-UXE-025 | High-signal errors, one-click fix destination | Shown | The validation workspace |
| SS-UXE-026 | Side-by-side edit and test | Partly | Simulator is its own step; nothing is mutated by a test; not side by side |
| SS-UXE-027 | Instructional empty states | Shown | |
| SS-UXE-028 | Consistent design system | Shown | Formal design approval — Owner |
| SS-UXE-029 | Publish review uses human-readable change summaries | Shown | Comparison: rule truth, option routing and queues in sentences, no JSON |
| SS-UXE-030 | Usability sign-off separate from functional sign-off | Owner | Not done; not claimed |
| SS-UXE-031 (P1) | Command palette | Not shown | F8 "next issue" only |
| SS-UXE-032 (P1) | Compare two profiles | Shown | |
| SS-UXE-033 (P1) | Batch import and templates | Not shown | One start template only |

| Gate | Measure | Status |
|---|---|---|
| UX-GATE-01 … 07 | Timed tasks and comprehension rates with test authors | **Owner — no moderated test has been run** |
| UX-GATE-08 | Every blocker on its card and in the issues view; link focuses the control | Partly — true for the blockers exercised; not proven for all of them exhaustively |
| UX-GATE-09 | Guided/Graph/Simulator parity on golden fixtures | Shown — 18 fixtures, 59 runs reproduced; canonical-model parity tests pass |
| UX-GATE-10 | Keyboard-only journey, screen-reader verification, WCAG 2.2 AA | Partly — keyboard journeys and automated scans only; **no screen-reader evidence** |
| UX-GATE-11 | No draft loss across interrupted saves | Not applicable to an in-memory prototype |
| UX-GATE-12 | Design system, key screens, prototype, moderated tests, recorded sign-off | Partly — screens and clickable prototype exist; moderated tests and sign-off — Owner |

**Mandatory review evidence still outstanding:** user-testing notes; before/after feedback on the seven baseline
screenshots; performance recordings for a medium and a large survey; signed business, design and engineering
acceptance. The prohibited anti-patterns of §18.8 were reviewed: none is present to my knowledge, with one
qualification — "claiming a survey is ready without evaluating the exact server-saved revision" cannot be satisfied
by a prototype, and the Validate screen says so on its face.

---

## Points for your decision

| # | Point |
|---|---|
| 1 | **Two skip-disposition settings instead of one** (Part A). Confirm, or direct a single setting and a new version of fixture G1's expectation |
| 2 | **Who may publish.** In the simulation either role may publish an approved candidate. Call360 needs a rule (P-9) |
| 3 | **An ordinary route to Escalate** (no mandatory answer) may still be routed by the survey. If every Escalate outcome should end the call, say so |
| 4 | **Editing during review.** The draft stays editable while in review or approved; a change voids the review. The alternative is to lock the draft |
| 5 | **The no-answer decisions** D-NA-1…17 in `17_…`; seven are needed before any backend work |
| 6 | The prototype decisions P-6…P-12 in the decision register |

## Remaining gaps

| # | Gap |
|---|---|
| 1 | Validation runs in the browser. Server validation of the saved revision and its dependency lock is SS-03 |
| 2 | The review state lives in memory and is reset by a reload; it is outside undo by design |
| 3 | Not built: favourites and recents; library filters; command palette; batch import; "save scenario"; simulate from a selected question; a non-answer turn in the simulator |
| 4 | The in-sequence skip disposition is set in the condition drawer and appears on the card only once set; in the survey graph it is drawn only once set |
| 5 | A module pinned at an older version raises a warning, but there is no one-click "move to the newer version" in the Composer |
| 6 | On a short window, a menu opened low in the module graph can extend below the screen. The slim strip avoids it at the tested size; the menu should flip upwards |
| 7 | Comparison matches questions by their place in a module. A question moved to another module shows as removed and added |
| 8 | The three reference interpreters are independent code by the same author, not an independent review. The server engine remains the real second implementation |
| 9 | Seeded version 1.0 exists only for the demonstration survey; a survey you create starts with no version to compare with |
| 10 | No moderated usability test, no screen-reader session, no formal UX sign-off |

---

## For your end-to-end review

Running at `http://localhost:5173/survey-studio` (reload first; a reload resets everything).

1. **Prototype · not saved → Add a demonstration survey and simulate it.** Note the strip of six steps.
2. **Compose.** On *Clarifications*, open the *Escalate* route: only one ending is offered. On *Escalation and
   follow-up*, click the "Runs when …" chip and try *After an outcome* together with the condition.
3. **Validate.** Read the two warnings. Then in Compose set "Jumped to, but does not apply" to *Leave undecided* and
   come back: two blockers, and Submit unavailable although most customers still complete. Use **Go to it**, fix it.
4. Acknowledge each warning with a reason. The verdict becomes "Ready to submit for review".
5. **Review and publish.** Submit with a note. Try to approve as the author. Switch "Acting as" to Arjun Menon and
   send it back with a comment.
6. As Mei Ling Tan: **Build modules** → open *Closing* → *Edit a copy for this survey* → change a question's wording.
   Open **Compare revisions**.
7. Submit again as **Farah Ismail** (both roles) and try to approve. Then approve as Arjun Menon.
8. As the author, change any route in Compose and return: the approval no longer applies. **Undo**, return, **Publish**.
9. **Publication history and audit.**

SS-03 has not been started.
