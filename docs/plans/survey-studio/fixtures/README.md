# Survey Studio — canonical JSON fixtures (SS-01)

Worked examples of the SS-01 contracts (`../04_SS-01_CANONICAL_CONTRACTS.md`, `../05_…`). **Synthetic and
illustrative:** wording, thresholds and outcomes are examples for contract design, not approved AIA/MAS language or
business policy. The JSON shape is the proposed *logical* contract (`call360.survey-studio.fixture/1`); it is not an
API schema and is frozen only after the owner approves SS-01 and the server contract is reviewed in SS-03.

| Fixture | Shows | Expected runs | Rejected answers |
|---|---|---:|---:|
| `F1-simple-linear-survey.json` | The degenerate graph: explicit `ANY` default edges; an optional free text | 1 | 0 |
| `F2-yes-no-branch-shared-rejoin.json` | Yes/No per-choice routes; one node with two inbound edges | 2 | 1 |
| `F3-single-choice-per-option-routes.json` | Four option codes, four routes, a four-way merge | 2 | 1 |
| `F4-multi-select-ordered-followups.json` | Sequential follow-up queue: order, dedupe, interrupt, empty fallback, exclusivity | 4 | 2 |
| `F5-other-specify-with-validation.json` | `OTHER` as an option with required text; no phantom text; evidence shape | 2 | 3 |
| `F6-internal-condition-with-unknown.json` | Reusable parameterised condition at a Decision node; three-valued logic; boundary value | 6 | 0 |
| `F7-two-placements-one-question-definition.json` | One Question Definition, two Question Instances in one survey, different routing, evidence per instance | 1 | 0 |
| `F8-survey-with-conditional-lego-modules.json` | Six module instances: always, three entry rules with different UNKNOWN policies, one activated by a prior outcome | 7 | 0 |

## File layout

```text
schema, fixture, title, purpose, notice
catalog      fields used (type, unit) and the outcome catalog
library      option_sets, questions (structure), wordings (customer-facing text), conditions, modules (nodes + edges)
survey       sequence, instances (entry, outcome routes), end outcome
expected_runs[]  profile, answers keyed by Question Instance (`{instance}/{node}`), optional `rejected` answers,
                 and `expect`: asked (in order), module statuses, survey outcome or blocked state,
                 and where given: edges taken, trace lines, evidence records
```

## Checking the fixtures

`reference_interpreter.py` is a small, dependency-free Python script that **generates** these files and runs every
expected run through a minimal interpreter of the SS-01 contracts, failing on any difference:

```text
python3 reference_interpreter.py <output_dir>
→ ALL OK: 8 fixtures, 25 expected runs
```

It is documentation tooling, **not application code and not the engine**: it exists so the examples are checked
rather than hand-asserted, and so the contracts are shown to be executable. It implements only what the fixtures use
(it does not implement `ORDERED_RULES`, `ON_SKIP`, non-answers, Back/Edit, pause or lifecycle gates). The fixtures —
not this script — become the golden tests of the server engine in SS-03/SS-04. It can be deleted without loss of any
contract.

Lifecycle modules (opening, identity, disclosure, consent) are deliberately omitted so each fixture isolates one
routing idea; real surveys keep them (decision SS-D-08).
