# APPL-X1 — Survey Applicability Studio: experience specification, prototype and evidence

**Status: PROTOTYPE BUILT AND TECHNICALLY VERIFIED 2026-11-23, presented for the product owner's design acceptance.
Not accepted. Not business UX acceptance, not a usability study, not a screen-reader test.**
Synthetic content only. No table, no migration, nothing stored. Uncommitted.

Companions: `56_…` (architecture and contracts), `58_…` (implementation plan). Evidence:
`docs/acceptance/evidence/APPL-X1/` (40 screenshots, test outputs).

---

## 1. What exists to look at

| | |
|---|---|
| Where | Survey Studio → **Survey applicability** (`/survey-studio/applicability`), in local development |
| Sign in | `dev.survey.author` (any identity with `survey.read`) |
| Switches | frontend `VITE_SURVEY_APPLICABILITY=1`; backend `SURVEY_APPLICABILITY_PROTOTYPE_ENABLED=true` — both on in local development, both off by default |
| What is real | every result on screen — true / false / not known, the selection plan, the explanation, validation, generated combinations, the draft-versus-published comparison, fingerprints — is computed by the Python evaluator through four stateless operations |
| What is not | **nothing is saved.** The workspace lives in the browser tab and starts again from a synthetic example on reload. The three people of the governance flow are simulated. The survey catalogue is six synthetic entries, not Survey Studio's published surveys |

The prototype says this itself, on every screen ("Prototype · nothing is saved").

## 2. Design system

It lives inside Survey Studio and reuses its tokens (pale plate, navy for actions, rounded display type for names,
red kept for problems). What it adds:

| Element | Decision | Why |
|---|---|---|
| **The sentence** | every requirement is drawn as *WHEN … THEN …*, on the overview, on the cards and in review | it is how the business states the rule; the same shape everywhere means one thing to learn |
| Three object colours | facts amber, conditions indigo, surveys teal — always with an icon and a word | the two dimensions (condition logic, selection behaviour) stay visibly apart |
| Truth values | *Matches* (check), *Does not match* (dash), *Cannot tell yet* (question mark, dashed outline) | never colour alone; "not known" must look different from "no" |
| Replacement | violet, dashed | a relationship between requirements, not a condition and not a survey |
| Density | cards read as sentences; the builder opens only on "Edit condition" | found in review: showing the full builder on every card was heavy and wrapped badly |
| Type | 13.5px body, 16px sentences, 24–36px page titles; lines under about 72 characters | spacious without wasting the screen |

## 3. Screens

| Screen | Purpose | Key interactions |
|---|---|---|
| **Overview** | what is published, what is being changed, what needs attention | the policy as sentences; three attention items computed by the evaluator (blocking problems, scenarios the draft changes, facts with no source) |
| **Variable library** | every fact, defined once | search; filters by kind, source status and market; cards or table; inspector with source and lineage, draft-versus-published comparison, where used; guided creation in six steps that adapt to the kind chosen; a warning when a name resembles an existing variable |
| **Application profiles** | reusable sets that combine | build on other profiles; sections; required / optional; per-profile allowed values; "the resulting application" with each variable's origin in colour; combine with others and see conflicts; create a sample application |
| **Condition lab** | named, reusable conditions | three levels (simple, grouped, advanced); searchable variable picker that offers only valid comparisons and values; nested all / any / not; saved conditions inside conditions; the sentence updated as you build; a live test with the responsible line marked and "what would settle it"; quality checks; versions; where used |
| **Applicability designer** | the flagship: one policy, three views | **Cards** (default), **Canvas**, **Matrix** over one document; palette (surveys, conditions, facts, profiles) on the left; inspector on the right with the live result always visible; "Add requirement" asks what you want to say (seven starting points); delivery order; undo and redo |
| **Scenario and test lab** | example applications | create from a profile and a template; edit facts with typed controls (value / not known / leave out); live result with reasons; the path that selected a survey; duplicate, variant, suite, regression mark, report; generated combinations with a coverage statement; draft against published |
| **Governance and impact** | review and publish one policy | five-stage bar; who acts next; validation grouped by severity with links to the place; impact on saved scenarios; pinned versions; history |

Shared everywhere: the five-step journey (which is also the navigation), a command palette (Ctrl/⌘-K), undo and
redo with the name of the change, drawers that create a variable or a condition without leaving the page.

## 4. The three views of one policy

| | Cards | Canvas | Matrix |
|---|---|---|---|
| Shows | each requirement as a sentence with its live outcome | facts → conditions → requirements → surveys → plan; a saved condition is one node however often used; replacement as a dashed line | example applications × surveys, with their facts |
| Edits | name, condition, surveys, include / choose one, replaces, order | selecting a node opens it in the inspector | — (it is a result) |
| Scale | builder collapsed; palette and inspector collapse | search, focus on a selection (shows only what leads to and from it), collapse how conditions are built, minimap | filter by suite, search, group by result / what applies / suite, sort, "only undecided" |
| Leads to | a survey → everything that selects it | a node → its inspector | a cell → the requirement responsible |

They cannot diverge: all three draw the same document and the same evaluator response.

## 5. Narrow screens

| Width | Behaviour |
|---|---|
| 1440 | palette (optional), composer, inspector; cards side by side |
| 1280 | inspector moves below the composer; list pages keep two columns |
| 900 | single column; cards stay WHEN → THEN side by side until the composer is under 600px, then stack |
| 390 (phone) | everything stacked; safe to read and navigate; the canvas keeps pan and zoom. Not intended for heavy authoring |

No sideways overflow at 1280, 900 or 390 on any of the six screens (asserted in the browser journey).

## 6. Acceptance demonstrations (the owner's Part 17)

Browser: `Call360-frontend/e2e/applicability/journey.appl.ts` — eight scenarios in one page, real backend. Evaluator:
`Call360-backend/tests/test_survey_applicability.py` — 21 tests.

| # | Demonstration | Result |
|---|---|---|
| 1–2 | a variable from scratch; an enum with values | **shown** (journey .2) |
| 3–4 | a reusable set; a profile from common and specific sets | **shown** (.2), including a variable never added twice and a reported conflict |
| 5–8 | ILP, NFTF, joined, nested AND / OR / NOT | **shown** (.3) |
| 9 | a saved condition reused in several **policies** | **partly**: reused across several requirements and inside other conditions; the prototype has one policy |
| 10–13 | a requirement in a few clear actions; one → one, one → many, many → one | **shown** (.4) |
| 14–16 | two independent; three additive; A and B replaced by C | **shown** (.4, .6; evaluator cases 1, 3, 4) |
| 17 | exclusive alternatives | **shown** (.4; evaluator case 6: list order never decides) |
| 18 | governed order | **shown** (.4; evaluator: order never changes selection) |
| 19 | duplicate / conflicting requirements | **shown** (.4; evaluator case 7 and `DUPLICATE_REQUIREMENT`) |
| 20 | UNKNOWN kept and explained | **shown** (.3, .4, .6) |
| 21–24 | create, reopen, duplicate, template | **shown, within the tab** — nothing is persisted in APPL-X1 |
| 25–30 | ILP only, NFTF only, both, neither, missing, invalid fact | **shown** (.6) |
| 31 | a useful generated matrix | **shown** (.6): every combination of the facts read, one example per distinct result, with what is not covered |
| 32–33 | draft against published; exactly which mapping caused a difference | **shown** (.6) |
| 34–35 | survey → its conditions; variable → its conditions | **shown** (.5, .2) |
| 36–40 | validate; maker submits; a different checker approves; a third publishes; the wrong person is refused | **shown as a simulation** — the three people are a switch in the page; server enforcement is APPL-X4 |
| 41–42 | pinned survey versions; a newer condition version changes nothing published | **shown** (.7; evaluator test) |
| 43 | market isolation | **not demonstrated** — needs persistence and real identities (APPL-X2) |
| 44 | reproducible evaluations and fingerprints | **shown** (.4, .7; evaluator test) |
| 45 | audit history | **not demonstrated** — the prototype shows a history list kept in the tab; audited records are APPL-X4 |
| 46–49 | executor, 82 runs and 14 plans, script assignment, bindings and plans unchanged | see §9 |
| 50 | a multi-survey journey without old assignment objects | **selection only**: the plan is produced with no rule, binding or group. Executing the selected surveys is APPL-X5 |

## 7. UX targets (the owner's Part 18)

**No target is claimed as achieved without a measurement.**

| Target | Status |
|---|---|
| A first-time user creates a simple mapping without training | **not measured** — needs people. Observable: 4 actions (Add requirement → "when a condition matches" → pick the condition → pick the survey) |
| An experienced user configures a three-survey ILP / NFTF policy in under five minutes | **not measured**. The automated journey does more than that in under ten seconds, which says nothing about a person |
| A new user creates an AND condition, runs a scenario and explains the result | **not measured** |
| No unnecessary page change for condition creation and survey linking | **met in the journey**: the new requirement, its condition and its two surveys were made inside the designer. The inline "create a variable" drawer exists; the journey created its variable in the library instead |
| No horizontal overflow at 1440, 1280, 900 | **met** (asserted; also at 390) |
| Complex graphs remain navigable | **built** (search, focus, collapse, minimap); **exercised only on a five-requirement policy** |
| Critical interactions work by keyboard | **partly verified**: command palette, canvas node selection, pickers and the builder are keyboard operable and two of these are exercised in the journey. A full keyboard walkthrough was not done |
| Errors appear beside the relevant configuration | **met**: diagnostics carry the path of the node and are drawn on that line or card |
| Published and draft states clearly differentiated | **met**: tags, the version switch, read-only published view, the stage bar |

## 8. Critique and refinement

Problems found by looking at the running screens and by the browser journey, and what was done:

| Found | Fix |
|---|---|
| Every card showed the whole builder; a single saved condition took fifteen lines and wrapped badly | a card reads as a sentence; the builder opens on "Edit condition" (and at once for a requirement just added) |
| Three panes left the composer too narrow at 1440 | the palette starts open only from 1600px; cards stack by the composer's own width, not the window's |
| The canvas was unreadable beside the inspector | the canvas takes the full width until a node is selected; tighter layout; never zoomed below 55% on opening |
| Selecting a requirement hid the live result | the live result is always in the inspector |
| **Defect:** choosing another condition and typing at once edited the previous one | each condition has its own editor instance |
| **Defect:** selection followed the address bar, which lags | the page changes at once; the address follows |
| **Defect:** Enter in the command palette could run the previous top result | it acts on what is typed |
| A profile could add a variable it already inherits | the picker marks it "already in …" and refuses |
| A worked-out fact showed "…" in a scenario | the evaluator returns its value |
| One accessibility violation (a picker's name did not contain its visible text) | fixed; no serious or critical violation on the six screens |

Still weak, in my own assessment:

* The scenario fact editor is long for a large profile; it needs grouping that collapses, and "only what this policy
  reads" as the default.
* The canvas has not been tried at the scale it is meant for.
* Drag and drop (palette onto a card, reordering cards and the delivery order) is built with keyboard alternatives
  but is **not covered by an automated test**.
* The page headings above the workspace are the application shell's; the breadcrumb is repeated.
* Choose-one starts every alternative as "otherwise", which is immediately a blocker until criteria are added. It is
  correct, but a gentler start is possible.

## 9. Regression

Run on 2026-11-23 against the isolated test schema, after the last source change. Outputs:
`docs/acceptance/evidence/APPL-X1/`.

| Check | Result |
|---|---|
| Backend suite | **1,045 passed, 0 failed** — the 1,024 before and the 21 of the applicability evaluator |
| 46, 47. Survey executor; golden fixtures | the executor is not edited; the 82 expected runs and 14 expected plans pass; **no fixture or expectation file is modified** |
| 48. Legacy operational script assignment | not edited; its tests pass |
| 49. Historical bindings and plans | not touched: the new code reads and writes none of them; the persisted journeys that create and verify them pass unchanged |
| Backend lint, format, types | clean (`ruff` on 268 files, `mypy` on 132) |
| OpenAPI | additive: four operations and six schemas, all under `/survey-applicability/prototype`; SHA-256 `f7a71873…802f480e9`; the frontend client matches |
| Frontend unit tests | **636 passed** (630 before and 6 new) |
| Frontend types, lint, build | clean |
| Playwright — applicability (new) | **8 passed** |
| Playwright — persisted | **34 passed**, unchanged |
| Playwright — prototype | **13 passed**, unchanged |
| Playwright — standard | **33 passed**, unchanged |
| Accessibility | no serious or critical violation (axe, WCAG 2.2 AA rules) on the six applicability screens. Not a screen-reader test |
| Security | the four operations require authentication, `survey.read` and a CSRF token, are rate limited and size bounded, execute no user-supplied code, and write nothing (asserted: every table's row count identical) |
| Specs validator | passes |

Existing tests changed: the two contract-count pins in `tests/test_survey_api.py` (four operations and six schemas
added). Nothing else.

## 10. What APPL-X1 deliberately does not do

No persistence, migration or new permission. No real published surveys. No server-enforced governance, market
isolation or audit. No optimistic concurrency. No execution of the selected surveys. Nothing reads or writes an
assignment rule, a survey binding or a requirement group, and none of those was changed.
