# Survey Applicability Studio — implementation plan, APPL-X2 to APPL-X6

**Status: PROPOSED 2026-11-23. Nothing here is authorised.** Each checkpoint stops for review; each migration is
proven on the isolated test schema first and applied to development only on separate authorisation.
Depends on the owner's acceptance of APPL-X1 (`56_…`, `57_…`) and on decisions AP-1…AP-10.

---

## Entry conditions for APPL-X2

| | |
|---|---|
| APPL-X1 design accepted | the document model, three-valued logic and selection semantics of `56_…` |
| AP-1…AP-10 ruled | or explicitly left at the proposed value |
| Fact contract | the typed fact interface of `56_…` §7 agreed as the input shape (it is also APP-1's) |

## APPL-X2 — Variable Library, Profiles and Condition Lab, persisted

| | |
|---|---|
| Schema | `applicability_asset`, `applicability_asset_version` (insert-only versions; kind VARIABLE / PROFILE / CONDITION), `applicability_event`. One migration, test schema first |
| Backend | store with optimistic concurrency; validation through the existing `analysis` module; `condition-test` on persisted versions; permissions `applicability.read / edit` and the library approval of AP-3; market isolation on every operation |
| Frontend | the three screens on the generated client; the in-memory store replaced screen by screen; conflict handling when someone else saved first ("your change and theirs", never a silent overwrite) |
| Removed | the prototype's `analyse` and `condition-test` operations once their persisted equivalents exist |
| Tests | versions immutable; a published version never changes; cycles refused; market isolation; migration up, down and partial failure; the evaluator's 21 tests unchanged |
| Not in X2 | policies, scenarios, publication of policies |

## APPL-X3 — Applicability Policy and Designer, persisted

| | |
|---|---|
| Schema | `applicability_policy`, `applicability_policy_draft` |
| Backend | draft save with expected revision; survey picker over **real published survey versions** (read-only); pinning by version and content fingerprint; `evaluate` on a saved draft |
| Frontend | cards, canvas and matrix on saved drafts; real surveys in the palette; autosave state; undo and redo over server revisions |
| Tests | the ten mandatory cases through the API; a survey version that is not published cannot be pinned; a pinned version survives a newer publication; drag and drop covered by browser tests |

## APPL-X4 — Scenario Studio, Impact and Publication

| | |
|---|---|
| Schema | `applicability_scenario`, `applicability_policy_candidate`, `applicability_policy_version`, `applicability_evaluation` (`record_class = 'SIMULATION'`) |
| Backend | scenarios and suites; generation; impact; submission as an immutable candidate with manifest and fingerprint; **three different identities** enforced by the service and the database; `applicability.approve / publish`; audit events; supersession |
| Frontend | governance on real candidates and real identities; pending-action lists; regression scenarios in review |
| Tests | self-approval, publication by the approver and by the maker refused; a blocker stops submission; a candidate is immutable; published versions reproduce their fingerprint from their own row; audit trail |

## APPL-X5 — Survey Studio integration

| | |
|---|---|
| Scope | a versioned **selection-plan interface** consumed by coordinated simulation, survey execution, journey evaluation, findings, execution assurance and Application Journeys |
| Rule | each simulated journey records its selection source: `LEGACY_ASSIGNMENT` or `APPLICABILITY`. Historical records stay distinguishable and unchanged |
| Not allowed | translating a plan into bindings or groups; any write to legacy assignment objects |
| Also | the five-item Survey Studio navigation (AP-9); facts from the APP-1a application view where authorised |
| Tests | a whole synthetic journey — selection, coordinated simulation, evaluation, assurance, trace — with **no** rule, binding or group created; every existing journey and the 82 runs and 14 plans unchanged |

## APPL-X6 — Legacy survey-assignment retirement

Only after the owner accepts X5 and decides, explicitly, what happens to legacy records.

| | |
|---|---|
| Does | removes legacy survey-assignment **authoring** from navigation; refuses new legacy survey-assignment writes where authorised; keeps every historical reader |
| Proves | no active survey workflow calls the old selection; recorded composite plans, bindings and groups still read and still verify |
| Does not | drop tables; touch Script Studio's operational assignment, which has its own APP / OPS dependencies |

## Risks

| Risk | Mitigation |
|---|---|
| Two selection mechanisms live for a long time | the source is recorded on every journey; no hidden bridge between them |
| A variable library grows without sources | source status is on every variable and on the overview; a policy reading an unmapped fact says so |
| Enumeration limits hide interactions in large policies | the analysis reports "not checked" and the coverage statement says what was left out |
| Governance of library items differs from policies (AP-3) | a policy pins exact versions, so a library change can never alter a published policy |
| The prototype's memory store is mistaken for the product | it is replaced screen by screen in X2–X4; the prototype notice stays until then |
