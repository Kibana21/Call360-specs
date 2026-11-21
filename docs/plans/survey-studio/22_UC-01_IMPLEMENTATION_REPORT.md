# UC-01 — Unified Survey Studio Foundation: implementation report

**Checkpoint:** UC-01, authorised by the owner on 2026-11-21 ("G-6 Architectural Direction Approved: Unified Survey
Studio"). The first implementation checkpoint after the accepted SS-02 prototype.
**Status: BUILT AND TECHNICALLY VERIFIED — presented for the owner's review. Not accepted.**
**Prepared:** 2026-11-21 22:15.

**Scope held.** Frontend prototype and specification documents only. Script Studio was not modified or deleted. The
development database was not read, reset or touched. No operational backend, API, runtime or voice behaviour changed
(OpenAPI `221985e7…` unchanged; backend clean at `7228875`). SS-03 not started. No new dependency. No paid call.
Survey Studio remains off by default. Synthetic data only; no wording is approved AIA or MAS language. **Nothing is
committed or pushed.**

**Not claimed.** No moderated usability session and no screen-reader session has been run. No golden fixture with an
independent reference interpreter was added for the new elements (see §7).

---

## 1. Scope item by item

| # | Scope item | Result | Where |
|--:|---|---|---|
| 1 | Update the G-6 decision record and architecture contracts | Done | `20_…` §10; decision register D-155…D-160, amended SS-D-01/02/20, P-13…P-22; contract `04_…` §7 |
| 2 | Capability-level consolidation map with current consumers and replacement interfaces | Done | `21_UC-01_CONSOLIDATION_MAP.md` |
| 3 | Extend the existing question and module cards with the small missing capabilities that have defined semantics | Done: mandatory flag, lifecycle role, number rule, delivery mode, wording version line | Guided card; same card in the Graph side panel |
| 4 | Statement nodes with opening, transition, disclosure and closing roles | Done | §2.1 |
| 5 | Typed Numeric and Acknowledgement question support | Done | §2.2 |
| 6 | A progressively disclosed wording and delivery section on question cards | Done | §2.3 |
| 7 | Controlled variable placeholders on synthetic data, deterministic rendering, explicit missing-value errors | Done | §2.4 |
| 8 | Interface contracts for evaluation and control mappings, without replacing those engines | Done, as types and a tested projection; **not authorable** | `model/contract.ts`; `21_…` §4 |
| 9 | Customer-specific Call Plan Preview from a synthetic application and the prototype's deterministic model | Done | §3 |
| 10 | Identify unresolved policy-dependent behaviour and block it rather than invent rules | Done | §5 |

---

## 2. What was built

### 2.1 Statement nodes

A statement is approved wording that is **delivered** and takes no answer. It is an item in the **one item master**
— the same identity, versions, wording, sharing and comparison as a question — placed by a node of type `STATEMENT`.
There is no second model.

- **Roles:** Opening, Transition, Disclosure, Closing. The role is declared; it changes no routing.
- **Routing:** exactly one way on. The model refuses any attempt to make a statement branch.
- **Guided:** added from the same menu as a question ("Statement — something the customer is told. It takes no
  answer"); the same card, marked as a statement.
- **Graph:** the same node, named by its role; the same card in the side panel.
- **Simulator:** delivered automatically on the way to the next question; shown in the journey as "opening
  delivered: …"; never counted as asked.
- **Validation:** missing statement text; a node and its item of different kinds.
- **Comparison:** added, removed, reworded, role changed.

### 2.2 Number and acknowledgement questions

| | Number | Acknowledgement |
|---|---|---|
| Answer | A number, checked against whole-number, lowest, highest; a unit label | "Acknowledged" |
| Routing | One way on | One way on |
| Rejections | Required; not whole; too low; too high — the question is asked again | Not acknowledged is **not accepted** |
| Why | | "Does not acknowledge" is a non-answer; what a call does then is undecided |

Neither answer can yet be read by a condition (prototype decision P-20).

### 2.3 Wording and delivery, on the card

One section on every question and statement card, **closed by default**. Closed, it is one line: how the wording is
delivered, how many variables it uses, and that it is not approved. Open, it holds:

- **How it is delivered** — exact text spoken by the system; approved recording; in the assistant's own words. The
  third is selectable and immediately **blocked**.
- **Customer details in the wording** — the variables used, "Insert a variable" from the field catalog, and a
  preview of what a chosen synthetic customer would hear, or the reason it cannot be delivered.
- **Role** — for a statement, what it is for; for a question, mandatory and, on a yes/no question, a lifecycle role.
- **Not available yet** — repeat and clarification wording (blocked), expected answer and control mapping (contract
  only), each with its reason.

A section with a problem opens itself, so nothing is hidden behind the fold. There is no separate wording screen,
workspace or navigation entry.

### 2.4 Controlled variables

- Written `{{field_code}}`; each names one field of the governed catalog. Two fields were added to the synthetic
  catalog for the demonstration: plan name and policy term.
- **Deterministic:** the same wording and the same customer data always give the same sentence. One fixed format per
  type, with no dependence on the machine's locale (for example `SGD 3,000`).
- **Explicit errors.** At authoring time: unknown field, a yes/no fact, an unfinished variable. For a customer:
  missing, or not usable. In either case **the wording is not delivered** — nothing is defaulted or improvised. The
  simulator halts with "information is missing"; the call plan is marked blocked.
- **Evidence:** every delivered item records the wording version, the exact sentence and each value put into it.

### 2.5 Declared attributes and live eligibility

"Mandatory", identity check, consent to proceed, recording consent and cloud-processing consent are recorded on the
question and carried into the content contract. **They change no routing.** Validation reports, as information,
whether a survey contains the three mandatory gates the owner requires for live calls (D-67). It never makes a survey
eligible.

### 2.6 Interface contracts for evaluation and controls

`EvaluationConfig`, `ControlLink`, the methods allowed per item kind, and `toContent(survey)` — the content document
the existing engines would read, produced from the one canonical model — are defined and tested. Every item's
`evaluation` is null and its `controls` empty: **nothing is configured and no engine is replaced.** `legacyGaps`
lists what today's engines could not read (multiple choice; choices by code; statements; the Transition role;
variables).

---

## 3. A synthetic application-to-call-plan walkthrough

Reload `http://localhost:5173/survey-studio` (a reload resets everything). **Prototype · not saved → Add a survey
with statements and a call plan.** The Call plan preview opens for the synthetic application "Normal policyholder".

| Stage (G-6 §4) | What the screen shows for this application |
|---|---|
| Application data | Five fields the survey uses — annual premium `SGD 3,000`, sum assured `SGD 150,000`, replaces a policy `No`, plan name `SecureLife Protect`, policy term `20 years` — each **Present**, each with what it is used for |
| Input validation | Each value is Present, Missing or Not usable. Nothing is defaulted |
| Approved survey selection | **Not shown: assignment is not in Survey Studio yet.** The survey is chosen by hand, and it is a draft |
| Customer data binding | Each variable and each condition field is listed against the item or module that reads it |
| Module eligibility | *Welcome and checks* — in. *Reason for purchase* — in. *High value review* — **not in** (premium below 12,000 and sum assured below 500,000). *Policy replacement* — **not in**. *Wrap-up* — in |
| Call-plan assembly | Verdict "A call plan can be built for this customer"; 3 modules in, 2 not in; a plan fingerprint |
| Approved wording selection | Each item with the exact sentence: "Good day. This is a service call about your SecureLife Protect plan." · "Our records show an annual premium of SGD 3,000, payable for 20 years." — with delivery mode, wording version, "not approved", and the values used |
| Dynamic routing | **Section 2 · Still open**: "The answer to Q2 — Yes → Q3; No → the module ends: Unable to verify", and how each module's ending leads on. The plan lists alternatives and chooses none. Items are marked "On every path" or "Only on some paths" |
| Evidence | **Section 3 · Actually said**: one simulated call for this customer, labelled as not part of the plan |

Then change the application:

- **High-premium customer** — *High value review* moves into the plan; the fingerprint changes. Same survey,
  different plan.
- **Missing-data customer** — the verdict becomes "A call plan cannot be completed for this customer". The reason is
  stated: the disclosure cannot be delivered because "Annual premium" is missing from the record. The simulated call
  halts at that point. *Policy replacement* is not in the plan, because the survey says to skip it when the
  replacement flag is missing.

**The three things kept apart on the page:** what is settled before the call; what is still open; what was actually
said. The plan and the simulator are verified to agree: every sentence the simulator delivers is the sentence the
plan showed for that item.

**Limits of the preview.** It is a browser demonstration on invented data. It is not the Call360 runtime, assembles
no real call and approves nothing. Survey selection, non-answer handling and delivery evidence from a voice provider
are not part of it.

---

## 4. Guided/Graph parity and the other surfaces

| Capability | Guided | Graph | Simulator | Validation | Comparison | Call plan |
|---|:-:|:-:|:-:|:-:|:-:|:-:|
| Statement node and role | ● | ● | ● delivered | ● | ● | ● |
| Number question | ● | ● | ● validated | ● limits | ● | ● |
| Acknowledgement | ● | ● | ● | — | ● | ● |
| Delivery mode | ● | ● same card | recorded | ● blocked / warned | ● | ● |
| Controlled variables | ● | ● same card | ● rendered; halts if missing | ● | ● wording | ● |
| Mandatory, lifecycle role | ● | ● same card | not enforced, by design | ● live eligibility | ● | ● |

The Graph editor edits through the same card and the same operations as Guided, so there is one code path. A unit
test asserts the graph shows the same items as the model, and the journey adds a statement in Guided and finds it in
Graph and back.

**The existing model is unchanged.** The sample library and the first demonstration survey contain none of the new
fields; choosing the default delivery mode leaves the canonical form byte-for-byte as it was. All 19 fixtures
reproduce.

---

## 5. Policy-dependent behaviour: identified and blocked

| Behaviour | How it is blocked in UC-01 | Decision needed |
|---|---|---|
| Delivery in the assistant's own words | Selectable; a blocker in validation; the survey cannot be submitted | AD-9 |
| A variable inside an approved recording | A blocker | AD-8 |
| Approved recording | A warning: no recording can be attached | SCR-019, audio assets |
| A value missing for a variable | Delivery stops; the call halts; the plan is blocked. No fallback wording exists | AD-8 (per-variable policy) |
| The customer does not acknowledge | Not accepted as an answer; cannot be simulated; the screen says why | G-3 |
| A mandatory question not answered | Not implemented. "Mandatory" is a recorded attribute only | D-NA-5, D-NA-10 |
| Identity or consent refused | Not implemented. A "No" follows the route the author set, nothing more | Lifecycle gate rules |
| How often and how a question is repeated | Shown on the card as "Not available yet", with the reason | D-NA-8, `NA-P-…` |
| Response timeouts | Not present anywhere | `NA-P-RESPONSE-WINDOW` |
| Clarification wording | Shown as "Not available yet" | D-NA-8 |
| Expected answer, control mapping | Contract only; shown as "Not available yet" | Backend; UC-D-8 |
| Reading a number in a condition | Not offered | UC-D-7 |
| Standing warning "What happens when a customer does not answer is not decided yet" | Kept on every survey | G-3 |

No repeat count, timeout, refusal, consent or conversational-wording policy was implemented.

---

## 6. Screenshots

In `docs/acceptance/evidence/UC-01/screens/`, all on synthetic data:

| File | Shows |
|---|---|
| `UC01-guided-statements-and-questions` | The unified authoring experience: statements and questions in one module, wording section closed |
| `UC02-wording-and-delivery-open-on-a-statement` | The section opened on an opening statement |
| `UC03-variable-missing-value-error` | A second variable inserted; the preview for a customer without the value shows an explicit error |
| `UC04-conversational-delivery-blocked` | The undecided delivery mode, blocked on the card |
| `UC05-call-plan-normal-customer` | The full call plan |
| `UC06-call-plan-high-premium-customer` | The same survey, a different application, a different plan |
| `UC07-call-plan-missing-value-blocked` | A blocked plan and its reason |
| `UC08-simulator-acknowledgement-after-number` | A rejected number, then an acknowledgement |
| `UC09-simulator-statements-delivered` | A completed journey with the statements delivered |
| `UC10-graph-shows-the-same-statements` | The same module in the Graph view |
| `UC11-validation` | Live eligibility and the standing no-answer warning |

---

## 7. Test evidence

`docs/acceptance/evidence/UC-01/checks.txt`, `prototype_journeys.txt`, `playwright_standard.txt`.

| Check | Result |
|---|---|
| Type check | 0 errors |
| Lint | 0 problems |
| Unit tests, whole frontend | **347 passed** (314 before UC-01) |
| Unit tests, Survey Studio | **228 passed** (195 before; 33 new in `model/uc01.test.ts`) |
| The 19 golden fixtures, 63 expected runs | all reproduced by the prototype engine; files byte-identical on regeneration from the four reference interpreters |
| Guided/Graph parity tests | pass, unchanged |
| Prototype journeys in Chromium, prototype on | **12 of 12 passed** (the 11 existing, unchanged, plus the UC-01 journey) |
| Accessibility scans inside the journeys | 0 serious or critical (call plan, simulator, guided builder, validation) |
| Standard Playwright suite, prototype off | **33 of 33 passed** |
| API contract | unchanged |
| Dependency audit | 0 vulnerabilities; no dependency added |
| Secret scan | clean for history, for the changes and for the new files |
| Files changed outside Survey Studio | none |
| Backend repository | clean, unchanged |

**What the tests do not cover.**

- **No independent reference interpreter for the new elements.** Every earlier rule change came with golden fixtures
  generated by a separate Python interpreter. UC-01's statements, number and acknowledgement answers and variable
  rendering are covered by 33 unit tests against the TypeScript engine only. A schema `/5` fixture set should be
  added before any server engine is built against §7 of the contract.
- **No test with real users, and none with a screen reader.**
- **The call plan's "on every path" marking** is tested on two demonstration surveys, not exhaustively.

**Found and fixed while building.** The simulator screen showed the raw wording, with `{{…}}` in it, as "the
customer hears"; it now shows the rendered sentence and, beneath it, the approved source.

---

## 8. Exact remaining decisions needed before backend implementation

### 8.1 Preconditions of AD-2 (before any destructive change) — none met yet

1. Read and inventory the actual development database.
2. Identify protected demonstration records and owner restrictions.
3. Produce a verified backup.
4. State exactly what a re-seed would replace.
5. Approve a separate destructive-change checkpoint.

### 8.2 Architecture decisions still open

| No. | Decision | My recommendation |
|---|---|---|
| AD-3 | Store a module graph as one validated, hashed document per version, with a usage index | Yes |
| AD-5 | Publisher separation on the server (today the checker role holds both approve and publish) | A separate grant; who holds it is G-4 |
| AD-12 | Single language through consolidation | Yes |
| AD-13 | Scheduled publication and withdraw in the publication model | Build the states now |
| AD-14 | "survey" vocabulary for the API and the store | Yes |
| UC-D-9 | Assignment configuration inside Survey Studio: is a rule approved with the survey version, or as its own artefact? | Its own artefact, same publication service, edited from the survey |
| UC-D-10 | Findings policy authored in the Survey Studio library, with its own permission | Yes |

### 8.3 Decisions raised or sharpened by UC-01

| No. | Decision | Blocks |
|---|---|---|
| UC-D-1 | The delivery mode when none is chosen (prototype: exact text) | Item schema |
| UC-D-2 | Conversational delivery: remove, or restrict to items Compliance classes as low-risk (AD-9) | Item schema; harness |
| UC-D-3 | Variables: which fields may be spoken (a customer's name is personal data); the spoken form of amounts, dates and names; the policy for a missing value; variables in recordings (AD-8) | Wording schema; plan assembly |
| UC-D-4 | The statement role list. "Transition" is new. May a statement require acknowledgement? | Item schema; lifecycle |
| UC-D-5 | Identity, consent and recording gates: confirm or replace the existing on-failure assumptions; "discloses policy information only after identity"; "deliver on termination" | Harness |
| UC-D-6 | What "mandatory" means when a question is not answered (D-NA-5, D-NA-10) | Item schema; evaluation |
| UC-D-7 | May a number or an acknowledgement be read by a condition or choose a route (for example a threshold)? | Condition contract |
| UC-D-8 | Evaluation configuration: who may set it; matching choices by code; tolerance approval | Item schema; evaluation adapter |
| UC-D-11 | Clarification and repeat wording: which phrases exist, verbatim or approved alternative, how many times (D-NA-8, `NA-P-…`) | Survey schema; harness |
| UC-D-12 | Confirm prototype decisions P-13…P-22 | Contract §7 |

### 8.4 Gates carried forward, unchanged

- **G-3 no-answer policy.** The seven needed before backend work on the runtime: D-NA-1, 5, 9, 10, 13, 14, 15.
- **G-4 governance.** Who holds Publisher and whether the approver may publish; whether a draft is locked during
  review; what "approved wording" is in Call360; the stored form of activation, eligibility and the two skip
  dispositions.
- **G-1, G-2.** Business-user UX acceptance and screen-reader sign-off, before Survey Studio is on by default.

---

## 9. Files changed

**Call360-frontend** (uncommitted; base `d1cdb03`), all under `src/features/surveystudio/` unless stated:

- New: `model/wording.ts`, `model/plan.ts`, `model/contract.ts`, `model/uc01.test.ts`, `CallPlanPage.tsx`,
  `labels.ts`, `e2e/prototype/uc01.proto.ts`.
- Changed: `model/types.ts`, `model/ops.ts`, `model/flow.ts`, `model/sim.ts`, `model/graph.ts`, `model/diff.ts`,
  `model/governance.ts`, `model/demo.ts`, `model/sample.ts`, `model/sim.test.ts` (one type cast), `BuilderPage.tsx`,
  `GraphView.tsx`, `SimulatorPage.tsx`, `EntryRuleDrawer.tsx`, `HomePage.tsx`, `StudioRoot.tsx`, `ui.tsx`,
  `src/styles/survey-studio.css`.
- Not changed: every file outside Survey Studio, including all of Script Studio.

**Call360-specs** (uncommitted; base `b5bae20`): `20_…` (§10 added), `21_…` (new), `22_…` (this report), `04_…`
(§7 added), `06_…` (D-155…D-160, amended rulings, P-13…P-22), `README.md`, `SESSION_HANDOFF.md`,
`docs/acceptance/evidence/UC-01/`.

**Call360-backend:** nothing.

---

## 10. To review

1. Reload the prototype. **Prototype · not saved → Add a survey with statements and a call plan.**
2. Read the call plan; switch the synthetic application to *High-premium customer*, then *Missing-data customer*.
3. **Run this customer in the simulator** as *Normal policyholder*: watch the statements be delivered; give 500 for
   the number, then 20; acknowledge; skip to the end.
4. **Build modules**: open "Wording and delivery" on the opening statement; insert a variable; preview it for the
   missing-data customer; choose "In the assistant's own words"; undo.
5. Add a statement from any "Add a question here"; switch to **Graph**.
6. **Validate**: read the live-eligibility note and the standing no-answer warning.

Stopped at UC-01. SS-03 has not been started.
