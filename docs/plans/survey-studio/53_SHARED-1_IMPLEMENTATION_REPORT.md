# SHARED-1 — Assignment Rules and Finding Rules on their own: implementation report

**Status: BUILT AND TECHNICALLY VERIFIED 2026-11-23, awaiting the owner's review. Not accepted.**
**Synthetic data only.** The rule engine, the condition language, the evaluation engine and the finding engine were
not changed. No existing rule, script, assignment, session, finding, review or audit record was modified, apart from
one new column on existing rule versions that is filled from their own script family and verified. Migration `0037`
exists and is tested on the test schema; **it is not applied to development**, which stays at `0036`. Not started:
MIG-2, operational case assignment, Script Studio retirement, voice.

Authorisation: the owner's message of 2026-11-23, "Accept MIG-1 and Implement SHARED-1" (D-356…D-360). Companion:
`52_SHARED-1_ASSESSMENT_AND_DESIGN.md` (assessment, dependency inventory, design, data-preservation plan — written
before the schema was edited), contract `04_…` §23, decisions D-361…D-369.

---

## 1. The acceptance criterion

> A business user can create and govern an assignment rule, bind it to published Survey Studio content and execute a
> synthetic multi-survey journey without creating or depending on a dummy published Script Studio script.
> At the same time, every existing Script Studio operational assignment, Finding Rule, historical reference and Review
> Workbench workflow must continue functioning unchanged.

Met, in one real-browser run against the real backend and database (§4). Two people holding **only** the new
assignment-rule permissions created, reviewed and published a rule that names no script; survey people bound it to a
published survey and put it in the primary requirement group; an invented application was given a composite plan of
two surveys, each selected by a survey-only rule, and a coordinated simulation was started from it. The number of
scripts did not change. Operational assignment, its simulation, holds and history were compared before and after and
are identical.

## 2. Owner decisions recorded first

B-1 → D-357, in the owner's six sentences, with what is superseded in D-154 and D-156 and what stays in force.
B-2 → D-358. M-1…M-5 and B-3…B-7 stay open → D-359. MIG-1 accepted → D-356. Recorded before any implementation.

## 3. What was built

### Schema — migration `0037_shared_rule_services` (test schema only)

| | |
|---|---|
| `script_assignment_rule_version.market_code` | the rule's own market; back-filled from its script family and verified in the migration; NOT NULL; governed market list; immutable with the version |
| `target_kind` on the rule version and the draft | `SCRIPT_VERSION` (default) or `SURVEY_BINDING`; `CHECK ((target_kind = 'SCRIPT_VERSION') = (target IS NOT NULL))`; fixed at creation |
| Five guards | a script-backed rule and its script share a market (and a rule written without a market takes its script family's); a draft's kind never changes; **a `script_assignment` can never be matched by a rule that is not script-backed**; a survey binding, its rule and its survey share a market; a requirement group holds rules of its own market |
| Eight permissions | `assignment_rule.*` and `finding_rule.*` (read, edit, approve, publish); granted to no role |
| Setting | `shared_rule_services_enabled`, off by default |

### Backend

| | |
|---|---|
| `rule_inputs.py` | a rule's market and kind are read from the rule; `published_candidates(…, kinds)` — **default script-backed only**; a survey-only candidate has `target_effective = False` |
| `rule_authoring.py` | create by kind; a copy and a new version keep the kind; validation, manifest, checksum and publication for a rule with no script; conflict scope by kind; refusal to simulate a survey-only draft over cases |
| `api/assignment_rules.py`, `api/finding_rules.py` | `require_any(legacy, dedicated)` on every operation except the simulation over cases; `target_kind`, `market`, `survey_only_rules` returned |
| `survey/assignment.py` | the rule's market from the rule; survey selection considers both kinds |
| `security/authz.py` | `require_any` |
| **Not edited** | `rule_engine.py`, `answer_evaluation.py`, `finding_engine.py`, `finding_rules.py`, `script_assignment.py`, `question_controller.py`, intake, voice, Script Studio authoring, the Review Workbench |

### Frontend

| | |
|---|---|
| Navigation and guards | Assignment Rules and Finding Rules stay under Design & Govern and now open for a holder of the dedicated read permission as well |
| Assignment Rules | new rule asks "What does this rule select?" — a script for cases, or a survey through a binding (only where the server offers it); the registry has a "Selects" column and each rule's market; a survey-only rule reads "Survey binding · no script — never assigns a script to a case"; the builder shows that statement in place of the script picker, with a link to Survey bindings and groups; the rule page shows market, kind, "Cases assigned: none, and never"; the Simulate tab explains where a survey-only rule is tried |
| Without the script permission | no button into Script Studio, no simulation over cases and no batch assignment are offered; the page says why |
| Finding Rules | actions offered to a holder of the dedicated permission |
| Survey assignment | a survey-only rule is tagged "Survey only · names no script" |
| **Not edited** | Script Studio's library and editor, the Simulation Workbench, the Review Workbench, Call Detail |

## 4. The twenty demonstrations

Browser: `e2e/persisted/zzzzzz-shared1.persisted.ts` (three serial journeys). Backend: `tests/test_shared1_rules.py`
(four tests). Screenshots: `docs/acceptance/evidence/SHARED-1/screens/`.

| # | Demonstration | Browser | Backend | Shot |
|---|---|---|---|---|
| 1 | Existing script-backed rules continue to work | seeded rule shown with its script; a legacy user's page unchanged | a script-backed rule authored and published as before; the whole existing rule suite | 05, 11 |
| 2 | Operational case assignment unchanged | the simulation over cases and a case preview do not mention the new rules | preview and baseline simulation identical before and after; fingerprint of assignments, case states and holds identical | — |
| 3 | Existing published script targets intact | registry shows `SALES_VERIFICATION_SG v1.1` | every pre-existing column of every rule identical | 05 |
| 4 | Survey-only rule without a dummy script | created in the browser; the number of scripts unchanged | the same; `script_version` count unchanged | 02, 03 |
| 5 | Governance | rules: two people, as their existing contract requires — the author's review and publish are refused. Bindings and groups: three people | maker refused review; author ≠ checker in the row | 04, 06 |
| 6 | Market authoritative and immutable | "SG" on the published rule | market from the author's scope; another market refused; update of market or kind refused by the database | 04 |
| 7 | Cross-market binding refused | a rule of another market is not found | the database refuses a binding whose market differs | — |
| 8 | Bound to a published survey | proposed, approved and published on the Survey assignment screen by three people | bound | 06 |
| 9 | Requirement groups select several surveys | the primary group gains the rule; an additional group holds the second | primary and additional groups | 07 |
| 10 | Composite plan and coordinated simulation | resolved and ready; both surveys selected by the survey-only rules; coordinated simulation opened | the same | 07, 08 |
| 11 | A survey-only rule cannot assign a real case | absent from the simulation over cases and from a case preview | not loaded by the operational loader; refused by the database on `script_assignment`; refused for case simulation | — |
| 12 | Assignment history readable | rule history read by a legacy user | history and a case's assignment read | — |
| 13 | Finding Rules through dedicated permissions | a finding-rule author and checker with nothing else draft, submit, approve and publish a rule set | the same | 09, 10 |
| 14 | Existing script users keep their access | Script Studio, Assignment Rules, Finding Rules, the simulator | legacy user and checker publish a rule | 11 |
| 15 | Nobody gains access | survey people and a reader: 403 and "unauthorised"; one rule capability does not open the other | seven combinations refused; the eight permissions held by no role | 12 |
| 16 | Published finding-rule semantics unchanged | the earlier published set: same rules and fingerprint, now superseded | engine untouched; `test_findings_api`, `test_finding_engine` | 10 |
| 17 | Survey Studio evaluations and findings unchanged | the earlier persisted journeys (EVAL-1, EVAL-2A, EVAL-2B, E2E-1) pass unchanged | `test_survey_evaluation`, `…_control_policy`, `…_execution_assurance`, `test_zz_e2e1_journey` | — |
| 18 | Script Studio functional | opened by a legacy user | `test_script_authoring` and the standard browser suite | 11 |
| 19 | No operational record modified | — | row counts of eight operational tables and their fingerprint identical | — |
| 20 | Historical fingerprints and golden fixtures unchanged | — | 82 runs and 14 plans; rule checksums identical through down and up | — |

## 5. Migration and rollback evidence

`tests/test_shared1_rules.py::test_zz_migration_0037_…`, on a populated schema (seeded rules for two markets, plus a
rule published through the API):

| Step | Result |
|---|---|
| Down to `0036` | the two columns are gone; every rule, publication, change event, script, assignment, session, run, execution, finding, finding-rule set, binding and group identical; the immutability trigger enabled; the application still lists the rules with their market |
| **Forced failure part-way** (a conflicting function pre-created, so the migration fails after the back-fill) | the migration raises; the schema is at `0036`; no column was added; every row identical; the immutability trigger **enabled** — one transaction |
| Up to `0037` | every rule's market equals its script family's (SG and MY both present); kind `SCRIPT_VERSION`; nothing else changed |
| Downgrade with a survey-only rule present | refused: "survey-only assignment rules exist; they cannot be expressed without the columns"; nothing changed |

Inside the migration itself the back-fill is verified before it can commit: no rule without a market, none differing
from its script family, the same number of rules, and an identical digest of every pre-existing column.

**Development is not migrated.** The new code was run read-only against it at `0036`: the same eight rule versions,
the same three bindings, survey selection and operational loading see the same rules
(`evidence/SHARED-1/development_unmigrated_smoke.txt`).

## 6. Regression — all run after the last source change

| Check | Result |
|---|---|
| Backend suite (`call360_test`) | **1,024 passed, 0 failed** — the 1,020 before and the 4 of `test_shared1_rules.py` |
| Golden fixtures | the 82 expected runs and 14 expected plans pass inside that suite; **no fixture or expectation file is modified** |
| Backend lint, format, types | clean (`ruff` on 261 files, `mypy` on 127) |
| Frontend unit tests | **630 passed** |
| Frontend types, lint, build | clean |
| Playwright — persisted | **34 passed** (31 before and the 3 of SHARED-1) |
| Playwright — prototype | **13 passed** |
| Playwright — standard | **33 passed** — with the setting off, including the existing Assignment Rules, Script Studio, assignment, simulation, findings and Review Workbench journeys, unchanged |
| OpenAPI | additive: 275 operations (none added), 521 schemas (none added); new fields only; the frontend's generated client matches |
| Security checks | the permission matrix of the survey API and the route inventory tests pass; every rule operation still reports a required permission; denied access is audited |
| Specs validator | passes |

Order: unit tests, build, prototype, standard and the backend suite ran after the last application source change.
The first full persisted run then showed two failures, both in test files: an earlier journey (ASG-1) pinned the exact
list of fields of an assignment-policy rule, which gained `target_kind`; and the new finding-rule step added a rule
that an earlier journey had already published an equivalent of, which the server correctly refused as ambiguous. Both
tests were corrected — no application code — and the whole persisted suite re-run: 34 passed.

Existing tests changed, and why: the migration head pinned in seven backend tests; the acceptable-heads test gained
the new setting; two stubs of the rule loader in survey tests accept its new optional argument; one pinned field set
of the assignment policy gained `target_kind`; one structure comparison ignores the columns and constraints `0037`
adds; the LIB-2 downgrade test expects `0037` to roll back first; and one existing browser journey (ASG-1) gained
`target_kind` in the same pinned field list. **No golden fixture or expectation was changed.**

## 7. Outstanding gaps

| | Gap |
|---|---|
| T-1 | **DEP-FR-1** — a finding rule of scope `QUESTION` names a script question code and does not reach a survey item. No identity mapping was invented. Rules of scope `CONTROL` and `ANY_QUESTION` serve both |
| T-2 | No operational path from a survey to a case (OPS-1). A survey-only rule is, by construction, never operational |
| T-3 | A survey-only rule cannot be tried against cases; it is tried against synthetic applications in Survey assignment |
| T-4 | The dedicated permissions are held by nobody until granted. Who should hold them is a governance decision (D-369) |
| T-5 | The legacy permission alternative is still accepted everywhere; removing it is a later, deliberate step |
| T-6 | The control register still has no maintenance of its own |
| T-7 | The Assignment Rules page's headings still speak of scripts ("Policy-to-script mapping", "How script assignment works"). Left as they are: they describe the script side accurately, and renaming is a business UX decision |
| T-8 | Rule governance stays two-person (its existing contract); survey bindings and groups are three-person. Whether rules should move to three is not decided |
| T-9 | No screen-reader test; not business UX acceptance |
| B | M-1…M-5 and B-3…B-7 of MIG-1 remain open (D-359) |

## 8. State

| | |
|---|---|
| Development database | `0036`, unchanged by SHARED-1. `0037` not applied; the setting off |
| Repositories | uncommitted. Nothing staged, committed or pushed by the assistant |
| OpenAPI | SHA-256 `2f98a3f925131944f78b3fd2d4b8eeeb7fef4bd2ee14fdc14fe911146074a4a8`; 275 operations, 521 schemas |
| To enable in development | the owner's separate authorisation: backup, `0037` as one revision, `SHARED_RULE_SERVICES_ENABLED=true`, and who receives the dedicated permissions (D-369) |

## 9. Stopped here for review

Nothing further is authorised. Open with the owner: D-367 (ten choices), D-368 (gaps), D-369 (development
enablement), and from MIG-1 the open decisions of D-359.
