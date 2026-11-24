# Survey Applicability Studio — implementation plan, APPL-X2 to APPL-X6

**Status: PROPOSED 2026-11-23. Nothing here is authorised.** Each checkpoint stops for review; each migration is
proven on the isolated test schema first and applied to development only on separate authorisation.
Depends on the owner's acceptance of APPL-X1 (`56_…`, `57_…`) and on decisions AP-1…AP-10.

---

## Update of 2026-11-23 (after APPL-X1R)

* AP-1…AP-10 are ruled (D-387) and implemented in the evaluator; they are no longer an entry condition.
* **Read-only integration with real published Survey Studio versions already exists** (APPL-X1R: catalogue, exact
  reference, picker, preview, navigation both ways; `56_…` §14.7). APPL-X3 **reuses** it and adds only persistence
  of the reference and a real, indexed "where used". It is not to be rebuilt.
* AP-3: variables, profiles and conditions are governed by three identities, like policies. APPL-X2 therefore
  carries the three-person lifecycle and the permissions `applicability.read / edit / approve / publish` from the
  start, and APPL-X4 reuses it for policies.
* The policy document has `shared_deliveries` and alternatives with `fallback`; it has no `same_survey`.
* The showcase surveys exist in development and are created in the test schema by `scripts/appl_showcase_setup.py`.

## Entry conditions for APPL-X2

| | |
|---|---|
| APPL-X1 design accepted | the document model, three-valued logic and selection semantics of `56_…` |
| AP-1…AP-10 | ruled 2026-11-23 (D-387) |
| Fact contract | the typed fact interface of `56_…` §7 agreed as the input shape (it is also APP-1's) |

## APPL-X2 — Variable Library, Profiles and Condition Lab, persisted — **BUILT, verified on the test schema (2026-11-23)**

Specification `60_…`; report `61_…`. What was planned here and what was built:

| Planned | Built |
|---|---|
| three tables | **four**: a dependency table was added for foreign-key integrity of pins and an indexed "where used" (`60_…` §1.2). No separate draft table (`60_…` §1.1) |
| `applicability.read / edit` and the library approval | all four permissions `applicability.read / edit / approve / publish`, granted to no role; three different people enforced by the service and by `CHECK` constraints |
| `condition-test` on persisted versions | `POST /applicability/test` against the persisted library (published or authoring view) |
| remove the prototype's `analyse` and `condition-test` | **not removed**: the in-memory policy of the prototype still uses them. They go with APPL-X3 / X4, when policies are persisted |
| the three screens on the generated client | done behind `VITE_APPLICABILITY_LIBRARY=1`; without it the prototype behaves as in APPL-X1R |

**Before APPL-X3 can run anywhere but the test schema:** the owner's authorisation to apply `0038` to development,
to create development identities holding the applicability permissions, and to publish the showcase library there
(`60_…` §7.1). None is authorised.

## APPL-X3 — Applicability Policy and Designer, persisted

| | |
|---|---|
| Schema | `applicability_policy`, with its one working draft on the row as for library assets (`60_…` §1.1) — review whether a draft table is needed at all |
| Backend | draft save with expected revision; the published-survey reference of `56_…` §14.7 persisted and checked on save (the read integration exists since APPL-X1R); references to library items resolved to **published library versions** (`60_…` §3.1) — a policy draft may read a library draft, a policy candidate may not; `evaluate` on a saved draft, built from the persisted workspace |
| Frontend | cards, canvas and matrix on saved drafts; real surveys in the palette; autosave state; undo and redo over server revisions |
| Tests | the ten mandatory cases through the API; a survey version that is not published cannot be pinned; a pinned version survives a newer publication; drag and drop and keyboard ordering are covered since APPL-X2 (journey X2.5); deliberate adoption of a newer survey version since APPL-X2 (X2.4) |

## APPL-X4 — Scenario Studio, Impact and Publication

| | |
|---|---|
| Schema | `applicability_scenario`, policy candidates and versions on the pattern of `applicability_asset_version` (reuse its guards and `CHECK`s rather than a second design), `applicability_evaluation` (`record_class = 'SIMULATION'`) |
| Backend | scenarios and suites; generation; impact; submission as an immutable candidate with manifest and fingerprint; **three different identities** enforced by the service and the database, as already done for library assets; the same `applicability.approve / publish`; the D-394 contract for acknowledging or resolving profile mismatches at publication; audit events; supersession |
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
