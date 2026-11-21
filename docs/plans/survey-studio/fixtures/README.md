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

## Versions

Two fixture schemas live side by side. **The historical fixtures are never edited**; a change of rule is expressed by
new fixtures in a new schema version.

| Schema | Files | Generated and checked by | Status |
|---|---|---|---|
| `call360.survey-studio.fixture/1` | `F1` … `F8` — 25 runs, 7 rejected answers | `reference_interpreter.py` | Historical, unchanged. Valid for everything they cover (they contain no jump) |
| `call360.survey-studio.fixture/2` | `G1` … `G6` — 18 runs, 2 rejected answers | `reference_interpreter_v2.py` | Added in SS-02B.3.1 for owner decisions D-125 … D-137 |

```text
python3 reference_interpreter.py <output_dir>      → ALL OK: 8 fixtures, 25 expected runs
python3 reference_interpreter_v2.py <output_dir>   → ALL OK: 6 fixtures (schema /2), 18 expected runs, 2 rejected answers
```

### What schema /2 adds

| Fixture | Golden cases | Runs | Rejected |
|---|---|---:|---:|
| `G1-jump-to-module-with-eligibility.json` | **Jump to an eligible module**; **jump to an ineligible module** (skip disposition: end the call); **jump to a module with UNKNOWN eligibility** (policy BLOCK → missing-information halt); the same module reached in sequence; activation by a named earlier outcome preserved | 4 | 0 |
| `G2-jump-skip-disposition-continue.json` | Skip disposition `@CONTINUE` after FALSE and after UNKNOWN with `SKIP_WITH_REASON` | 2 | 0 |
| `G3-jump-without-skip-disposition-is-invalid.json` | A structurally invalid draft: no skip disposition → `DRAFT_INVALID`; the same draft still runs for an eligible customer | 2 | 0 |
| `G4-first-matching-rule-routing.json` | **First-matching-rule routing**: first match wins, later matches reported not run, fallback, exclusive answer; invalid selections rejected | 4 | 2 |
| `G5-evidence-states-and-review-halt-in-module.json` | **The four answer-evidence states**; **missing versus a valid empty multi-select answer** (`CONTAINS_NONE` is TRUE for an empty selection and UNKNOWN for a question not asked); **review halt inside a module** (the governed `REVIEW_REQUIRED` outcome) | 3 | 0 |
| `G6-mandatory-escalation-precedence.json` | **Mandatory escalation precedence** over an interruption configured before it and over follow-ups; an optional interruption is an ordinary ending, not a mandatory escalation | 3 | 0 |

Differences in shape from /1 (everything else is identical):

```text
catalog.outcomes     a map code → class (NORMAL_COMPLETION | EXCEPTION | ESCALATION | REVIEW_HALT), not a list
option               "interrupt": "OPTIONAL" | "MANDATORY"  (the governed class, on the option definition)
condition.inputs     {"kind": "ANSWER", "question": {code, version}, "answer_type", "value_type", "scope"}   (typed, no labels)
condition operators  CONTAINS_ANY | CONTAINS_ALL | CONTAINS_NONE over a list of option codes
routing              "mode": "ORDERED_RULES", "rules": [{"rule", "when": {"kind": ANY|ALL|NONE, "options"}, "to"}], "fallback"
routing.interrupts   {"option", "policy": "STOP_ESCALATE", "outcome"}   (no priority: a MANDATORY option leads, then configured order)
decision             "unknown_policy": "BLOCK" with an UNKNOWN edge to {"outcome": "REVIEW_REQUIRED"}
instance             "if_ineligible": "@CONTINUE" | {"instance"} | {"survey_outcome"}   (the skip disposition of a jump target)
expect               asked · modules (status HALTED_MISSING_INFORMATION replaces BLOCKED_UNKNOWN)
                     terminal {"state": COMPLETED | ENDED_WITH_OUTCOME | MANDATORY_ESCALATION | REVIEW_REQUIRED |
                                        MISSING_INFORMATION_HALT | DRAFT_INVALID, "survey_outcome"?, "reason"?, "at"?}
                     trace   "<instance>: entry <TRUE|FALSE|UNKNOWN> via <SEQUENCE|JUMP>" · "<instance>: not eligible after jump -> <disposition>"
                             "<key>: RULE <id>; also [...]" · "<key>: FALLBACK" · decision, queue and interrupt lines as in /1
                             (an interrupt by a mandatory option ends " (mandatory)")
                     evidence_states {"<instance>/<node>": ANSWERED | ANSWERED_EMPTY | UNANSWERED | SKIPPED}  for every question of every module that ran
```

### The /2 → /1 vocabulary mapping (stated once; see `04` §2.2b)

| Schema /2 | Schema /1 |
|---|---|
| `terminal.state: MISSING_INFORMATION_HALT` | `blocked.reason: BLOCKED_UNKNOWN` |
| module status `HALTED_MISSING_INFORMATION` | module status `BLOCKED_UNKNOWN` |
| `terminal.state: DRAFT_INVALID` (reason R) | `blocked.reason: R` |
| `COMPLETED` / `ENDED_WITH_OUTCOME` / `MANDATORY_ESCALATION` | `survey_outcome` |
| `terminal.state: REVIEW_REQUIRED` | no equivalent |

`reference_interpreter_v2.py` is, like the first, documentation tooling and not the engine. It implements the jump
rule of D-135; `reference_interpreter.py` still implements the withdrawn "enter unconditionally" rule, which none of
its fixtures exercises. Neither implements non-answers (`04` §5.5), Back/Edit, pause or lifecycle gates.

## Schema /3 (SS-02C, owner decisions D-138 … D-141)

| Schema | Files | Generated and checked by | Status |
|---|---|---|---|
| `call360.survey-studio.fixture/3` | `H1` … `H4` — 16 runs, 2 expected validation errors | `reference_interpreter_v3.py` | Added in SS-02C. F1–F8 and G1–G6 are unchanged and regenerate byte-for-byte |

```text
python3 reference_interpreter_v3.py <output_dir>   → ALL OK: 4 fixtures (schema /3), 16 expected runs
```

| Fixture | Golden cases | Runs |
|---|---|---:|
| `H1-activation-and-eligibility-are-independent.json` | One module with BOTH a trigger and an eligibility condition: fired + eligible; fired + not eligible; fired + UNKNOWN (skip and record why); not fired (eligibility not even evaluated). The earlier `ON_OUTCOME` shape read unchanged | 4 |
| `H2-a-jump-is-an-activation-but-never-bypasses-eligibility.json` | A jump selects a module whose trigger did not fire; eligibility still decides; in sequence the trigger and the default apply | 4 |
| `H3-skip-disposition-in-sequence.json` | `if_skipped_in_sequence` to a later module and to an approved terminal outcome; FALSE and UNKNOWN; nothing skipped | 4 |
| `H4-mandatory-escalation-cannot-be-overridden-by-survey-routing.json` | A single-choice and a multi-select mandatory escalation against survey routes that jump on and continue: both are validation errors and neither is followed; an optional interruption stays ordinary routing | 4 |

Differences in shape from /2 (everything else is identical, and a /2 survey means the same under /3):

```text
instance   "activation": {"of": <earlier instance>, "outcomes": [...]}     the activation trigger; "entry" is eligibility only
           "entry": {"mode": "ON_OUTCOME", …}                              still read = activation + entry ALWAYS
           "if_skipped_in_sequence": {"instance"} | {"survey_outcome"}     absent = the next instance is considered
           "if_ineligible"                                                 unchanged: after a jump only; required for a jump target
fixture    "validation": {"errors": [{"code", "at"}]}                      MANDATORY_ESCALATION_OVERRIDDEN · SKIP_DISPOSITION_MISSING ·
                                                                           BACKWARD_ROUTE · ACTIVATION_INVALID
trace      "<instance>: not eligible in sequence -> <disposition>"
           "<instance>: mandatory escalation -> <OUTCOME>[; survey route overridden]"
```

`reference_interpreter_v3.py` imports the module interpreter of `/2` unchanged and replaces only the survey-level
executor. Like the others it is documentation tooling, written by the same author as the prototype engine: independent
code, not an independent reviewer. None of the three implements non-answers (`17_SS-02C_NO_ANSWER_CONTRACT.md`).

## Schema /4 (SS-02 closure, owner decision D-145)

| Schema | Files | Generated and checked by | Status |
|---|---|---|---|
| `call360.survey-studio.fixture/4` | `J1` — 4 runs, 3 expected validation errors | `reference_interpreter_v4.py` | Added at SS-02 closure. F, G and H are unchanged and regenerate byte-for-byte |

```text
python3 reference_interpreter_v4.py <output_dir>   → ALL OK: 1 fixture (schema /4), 4 expected runs
```

`J1-escalate-is-terminal-in-every-routing-mode.json` — three modules end with Escalate **without** a
mandatory-escalation answer: by a single-choice route, by a first-matching rule, and by an optional interruption. The
survey routes each one onward differently (continue; jump to a later module; end as Completed). All three mappings
are the validation error `ESCALATION_NOT_TERMINAL`, and none is followed: the call ends with Escalate, in terminal
state `ENDED_WITH_OUTCOME` (not `MANDATORY_ESCALATION`). A fourth run has no escalation and completes.

The only difference from /3 is that one rule. All fixtures together: **19 files, 63 expected runs** (25 + 18 + 16 + 4).
