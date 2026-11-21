# UC-02 — Contract and call-plan readiness: implementation and verification report

**Checkpoint:** UC-02, authorised by the owner on 2026-11-21 ("Accept UC-01 and Authorize UC-02").
**Status: ACCEPTED 2026-11-21 as technically verified, subject to contract clarifications (D-170).** One addition was
made after review, on the owner's instruction: the eligibility panel now has **eleven** conditions, the gates read
"Present" / "Not present", and gate behaviour is its own condition (`25_UC-02_DECISION_CLOSURE.md` §4). Where this
report says "ten conditions" or "Met" for a gate, that document governs. Original status: BUILT AND TECHNICALLY
VERIFIED — presented for the owner's review.
**Prepared:** 2026-11-21.

**Scope held.** Specifications, independent fixtures and narrowly scoped prototype correctness improvements only.
Script Studio was not modified or deleted. The development database was not read, reset, re-seeded or touched. No
production backend, API, runtime or voice change (OpenAPI `221985e7…` unchanged; backend clean at `7228875`). No
SS-03 implementation. No new dependency. No paid model or voice call. Survey Studio remains off by default.
Synthetic data only; no wording is approved AIA or MAS language. SS-02 was not reopened. **Nothing is committed or
pushed.**

**Not claimed.** No moderated usability session and no screen-reader session has been run. Nothing in this
checkpoint makes any survey eligible for a real call.

---

## 1. The seven scope items

| # | Scope item | Result | Where |
|--:|---|---|---|
| 1 | Independent golden fixtures, schema /5, with a Python reference interpreter, compared with the prototype engine | Done: 8 fixtures; the interpreter and the prototype agree on every expectation | §2 |
| 2 | Separate plan computation from live-call eligibility | Done | §3 |
| 3 | Correct delivery validation | Done: a recording without an approved asset blocks | §4 |
| 4 | Keep the call-plan UI lightweight | Done: about a third of its former length, sections open on demand | §5 |
| 5 | Decision-ready contracts | Done | `23_…` Part 1 |
| 6 | Implementation-readiness design: six minimal interfaces | Done | `23_…` Part 2 |
| 7 | Verification | Done | §7 |

Acceptance of UC-01 and the architecture decisions AD-3, AD-5, AD-12, AD-13, AD-14, UC-D-9 and UC-D-10 are recorded
as D-161…D-167.

---

## 2. Schema /5 golden fixtures and the Python reference

`fixtures/reference_interpreter_v5.py` and `fixtures/K1…K8*.json`.

**How independence was kept.** The interpreter imports nothing from the four earlier interpreters and shares no code
with the prototype. It was written from the contract (`04_…` §7 and §8). **Every expected value is written by hand**
in that file — each delivered sentence, each module status, each plan item — and the interpreter refuses to write a
fixture unless it reproduces all of them. The prototype's TypeScript engine is then run against the same files by a
test that only translates shapes and contains no expected values.

| Fixture | Covers (owner's list) | Runs | Plans | Validation errors |
|---|---|---:|---:|---:|
| K1 | Statement delivery and ordering; opening, transition, disclosure and closing roles; statements never require answers | 3 | 1 | 0 |
| K2 | Statements never branch and cannot be answered | 0 | 0 | 6 |
| K3 | Numeric validation: valid, invalid, whole-number, minimum and maximum | 3 | 1 | 0 |
| K4 | Acknowledgement accepted; **not given → blocked as unresolved policy**, not silently accepted | 3 | 1 | 0 |
| K5 | Deterministic variable substitution; missing and invalid variables; correct delivered wording and evidence | 4 | 5 | 0 |
| K6 | Unknown variable codes; conversational delivery; a recording without an asset | 1 | 1 | 6 |
| K7 | Repeated Question Instances with distinct execution identities | 1 | 1 | 0 |
| K8 | Application-specific module inclusion and exclusion; conditional branches left unresolved in the pre-call plan | 4 | 4 | 0 |
| **Total** | | **19** | **14** | **12** |

**Plan/simulator consistency** is checked on every one of the 19 runs, by both implementations: each delivered
item's text and values equal the plan's for the same facts.

**Result of the comparison.** On the first full comparison the prototype engine matched the reference on 41 of 43
checks. The two differences were both in my test's translation (a sort order and a miscounted total), not in either
engine. After correcting the translation: **43 of 43**.

**The 19 historical fixtures and their 63 expected runs are preserved**: unchanged in git, byte-identical on
regeneration from their own four interpreters, and still reproduced by the prototype. All fixtures together: 27
files, 82 expected runs, 14 expected plans.

**What writing the reference found.** Three gaps in the prototype as accepted in UC-01, all corrected (§4):

1. An amount with more than two decimals was rounded, and a fraction in a whole-number field was truncated, before
   being spoken.
2. An unfinished variable — `{{policy.plan_name` — was an authoring error but, if run anyway, would have been
   delivered with its braces.
3. A statement, number question or acknowledgement given a second route was not reported by validation.

**Not covered by schema /5** (stated in the contract §8.8): decisions, follow-up queues, rules, interruptions, jumps
and activation triggers in combination with statements, variables or the plan; any non-answer.

---

## 3. Plan computation is separate from live-call eligibility

The call-plan screen now answers two questions in two panels, side by side, and never merges them.

**A · Can a plan be computed from this data?** A technical answer. "Yes — a plan can be computed", or "No — the plan
cannot be completed" with each reason. The panel states: *"This is a technical answer only. It says nothing about
whether the survey may be used on a call."*

**B · May this be used on an operational callback?** Ten explicit readiness conditions, each **Met**, **Not met** or
**Cannot be established here**, with its reason one step away:

| Condition | In the demonstration |
|---|---|
| A plan can be computed for this application | Met (not met for the missing-data application) |
| The plan is built from a published, approved survey version | Not met — it is a draft |
| Every item uses approved wording | Not met — all wording is synthetic |
| Every item can be delivered as approved | Met; not met once a recording or conversational delivery is chosen |
| A mandatory identity check is in the survey | Met |
| A mandatory consent to proceed is in the survey | Not met |
| A mandatory recording consent is in the survey | Met |
| An approved assignment selects this version for this case | Cannot be established here |
| The requirements of the call channel are met | Cannot be established here |
| What a call does when a customer does not answer is decided | Not met |

**The answer to B is always "No — not eligible for a real call" in the prototype**, by construction: assignment and
channel cannot be established, and a publication simulated in the prototype does not count as a Call360 publication.
A plan that computes perfectly leaves B at "no".

**No policy was invented.** A gate condition is structural only: it says a mandatory question with that role exists.
Its reason reads: *"What a call does when the customer says no, refuses or does not answer is not decided."*

---

## 4. Corrected delivery validation

| Rule | Before UC-02 | Now |
|---|---|---|
| A recording is chosen and no approved recording is attached | A warning that could be acknowledged | **A blocker** (`RECORDING_ASSET_MISSING`). The survey cannot be submitted; the delivery condition for live calls is not met. The prototype cannot attach a recording, so every recording is blocked |
| A recording whose wording contains a variable | A blocker | A blocker (`RECORDING_WITH_VARIABLE`), unchanged |
| Delivery in the assistant's own words | A blocker | A blocker (`DELIVERY_CONVERSATIONAL_BLOCKED`), unchanged; also fails the delivery condition |
| A variable with no value | Not delivered | Not delivered, unchanged. Nothing is defaulted |
| An amount with more than two decimals; a fraction in a whole-number field | Rounded or truncated | **Not usable** — the item is not delivered |
| An unfinished variable | Authoring error only | Authoring error **and** not deliverable |
| An acknowledgement explicitly not given | Refused as "required" | **Refused as unresolved policy** (`NON_ANSWER_POLICY_UNRESOLVED`); the run stays at that question |
| A single-route item given a second route | Not reported | **A blocker** (`SINGLE_ROUTE_ITEM_BRANCHES`) |

---

## 5. A lighter call-plan screen

| | UC-01 | UC-02 |
|---|---|---|
| Height of the page for the demonstration survey, as first shown | about 4,200 px | **under 1,500 px** (asserted in the journey) |
| Wording of every item | Always shown | Shown when a module is opened; "Show all wording" opens them all |
| Open branches | Always listed | One line with the count; opens on demand |
| Simulated run | Always listed | One line with the count and how the call ended; opens on demand |
| Application data | Always a table | One line ("5 fields · all present"); opens on demand |

The first screen shows, in order: survey and application identity with the plan fingerprint; the two verdicts; six
counts (modules included, excluded, conditional or undecided; missing inputs; wording issues; unresolved answer
branches); then the three sections, closed:

1. **Settled before the call** — one row per module with its status and reason.
2. **Still conditional — decided by answers during the call.**
3. **Actually delivered — one simulated run.**

No new Studio, workspace or top-level navigation entry was added: the screen is still reached from Simulate.

**Statement labels.** Statements are labelled **S1, S2 …**; questions keep **Q1, Q2 …** and count questions only.
The demonstration module now reads S1, Q1, Q2, S2, Q3, Q4, S3. These are display labels: node ids and execution keys
are unchanged, nothing sorts on a label, and a module without statements is numbered exactly as before.

---

## 6. Screenshots

In `docs/acceptance/evidence/UC-02/screens/`, all on synthetic data:

| File | Shows |
|---|---|
| `UC20-plan-two-verdicts-as-seen-on-screen` | The two verdicts as the screen opens: a plan can be computed; not eligible for a real call |
| `UC21-plan-overview-two-verdicts-compact` | The whole compact overview on one page |
| `UC22-live-eligibility-conditions-with-reasons` | The ten readiness conditions with the reason for each |
| `UC23-one-module-opened-on-demand` | One module opened: exact wording; statements S1, S2 beside questions Q1, Q2 |
| `UC24-three-sections-opened` | Settled, still conditional, and actually delivered, all opened |
| `UC25-plan-not-computable-missing-value` | A missing value: the plan cannot be completed, and why |
| `UC26-recording-without-asset-blocks` | A recording chosen with none attached: blocked on the card |
| `UC27-validation-recording-is-a-blocker` | The same in Validate: a blocker with no way to acknowledge it |

Full-page captures show the application's fixed header and side bar overlaid part-way down the page. That is how a
full-page capture renders a fixed header; it is not how the screen looks. `UC20` is the screen as seen.

---

## 7. Verification

`docs/acceptance/evidence/UC-02/checks.txt`, `prototype_journeys.txt`, `playwright_standard.txt`.

| Check | Result |
|---|---|
| Historical golden fixtures: 19 files, 63 expected runs | all reproduced; unchanged in git; byte-identical on regeneration |
| New golden fixtures: 8 files, 19 runs, 14 plans, 12 validation errors | all reproduced by the Python reference **and** by the prototype engine (43 of 43 checks) |
| Frontend unit tests | **403 passed** (347 after UC-01) |
| Survey Studio unit tests | **284 passed** (228 after UC-01: +43 fixture checks, +13 UC-02 tests) |
| Guided/Graph parity tests | pass, unchanged |
| Simulator and call-plan journeys in Chromium, prototype on | **13 of 13 passed** (11 from SS-02, UC-01, and the new UC-02 journey) |
| Accessibility scans in the journeys | 0 serious or critical |
| Prototype-off regression (standard Playwright suite) | **33 of 33 passed** |
| Type check | 0 errors |
| Lint | 0 problems |
| Dependency audit | 0 vulnerabilities; no dependency added |
| Secret scan | clean for history, for the changes and for the new files |
| Specs validator | pass |
| API contract; backend repository | unchanged; clean |
| Files changed outside Survey Studio | none |

**Tests changed, and why.** Two UC-01 unit expectations were updated to the corrected rules (a recording is now a
blocker; an open point now carries its canonical form). The plan assertions of the UC-01 journey moved to the UC-02
journey, because the screen they tested was rebuilt. No SS-02 test was changed.

**What is not verified.**
- No test with real users, and none with a screen reader.
- The plan's "on every path" marking is specified and fixture-verified for modules without decisions or follow-up
  queues only.
- Rules that predate UC-01 are still identified by their message, not by a stable code.
- The reference interpreter and the prototype were both written by me, from the same contract. They are independent
  in code; they are not independent in authorship. A reading of the contract by a second person would add assurance
  that the contract says what the business intends.

---

## 8. Decisions

`23_UC-02_DECISION_READY_CONTRACTS.md` Part 1 sorts every remaining decision. In short:

- **23 technical schema decisions (TS-1…TS-23) can be approved now**, as a set. None contains a policy.
- **Blocking backend persistence — 12:** the default delivery mode; conversational delivery; permitted variable
  fields; the statement role list; what "mandatory" is (D-NA-5, D-NA-10); who holds Publisher; draft locking; what
  "approved wording" is; the stored form of activation and skip dispositions; the outcome catalog; how a non-answer
  is routed (D-NA-9); the outcome for "no answer" (D-NA-13).
- **Blocking runtime execution — 13, plus three voice-channel decisions:** including gate behaviour, the
  missing-value policy and repeat wording.
- **Blocking real calls:** all of the above, plus the parameter values, approved wording and recordings, the spoken
  form of values, and UX and accessibility sign-off.
- **Voice-channel decisions that can wait:** eleven, listed in §1.4.

The no-answer register is preserved unchanged: 17 decisions and 4 parameters, all unresolved, no value proposed.

---

## 9. Files changed in UC-02

**Call360-frontend** (uncommitted; base `d1cdb03`), all under `src/features/surveystudio/` unless stated:

- New: `model/fixtures5.test.ts`, `model/uc02.test.ts`, `e2e/prototype/uc02.proto.ts`.
- Changed: `model/plan.ts` (stable issue codes, canonical open points, `liveEligibility`), `model/flow.ts`
  (validation codes, single-route rule, recording blocks, statement labels), `model/wording.ts` (exact formats,
  unfinished variable), `model/sim.ts` (non-acknowledgement code), `model/types.ts` (issue code),
  `model/contract.ts` (reading order), `CallPlanPage.tsx` (rebuilt), `model/uc01.test.ts` (two expectations),
  `e2e/prototype/uc01.proto.ts` (plan assertions moved), `src/styles/survey-studio.css`.
- Not changed: every file outside Survey Studio.

**Call360-specs** (uncommitted; base `b5bae20`): `fixtures/reference_interpreter_v5.py`, `fixtures/K1…K8*.json`,
`fixtures/README.md`, `04_…` (§8), `06_…` (D-161…D-169, P-23…P-29), `23_…`, `24_…` (this report), `README.md`,
`SESSION_HANDOFF.md`, `docs/acceptance/evidence/UC-02/`.

**Call360-backend:** nothing.

---

## 10. To review

1. Reload the prototype. **Prototype · not saved → Add a survey with statements and a call plan.**
2. Read the two panels: A says yes, B says no. Choose **Show the reason for each**.
3. Open *Welcome and checks*: S1, Q1, Q2, S2 … with the exact wording. Open sections 2 and 3.
4. Switch the application to *Missing-data customer*: A becomes "No", with the reason.
5. **Build modules** → open "Wording and delivery" on the last statement → choose **Approved recording**: blocked.
   **Validate**: it is a blocker and cannot be acknowledged.
6. To re-run the fixtures: `python3 reference_interpreter_v5.py <an empty folder>` in
   `docs/plans/survey-studio/fixtures/`.

Stopped at UC-02. SS-03 has not been started.
