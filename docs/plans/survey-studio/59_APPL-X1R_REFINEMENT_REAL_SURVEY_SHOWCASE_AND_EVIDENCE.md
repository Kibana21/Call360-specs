# APPL-X1R — UX refinement, owner rulings and the real Survey Studio showcase

**Status: BUILT AND TECHNICALLY VERIFIED 2026-11-23, presented for the product owner's design review. Not accepted.
Not a usability study and not a screen-reader test.** Uncommitted.

Authorisation: the owner's message of 2026-11-23, "APPL-X1R: world-class Survey Applicability experience, real
survey showcase and end-to-end design validation". APPL-X1 is accepted as a technically verified prototype and
architectural direction (D-386); final design acceptance depends on this checkpoint.

**The one thing persisted by this checkpoint:** six clearly synthetic Survey Studio artefacts — one reusable module
and five surveys — created and published in local development **through Survey Studio's existing governed API**, by
three different identities. No table, no migration, no applicability record. Development stays at `0037`.

Companions: `56_…` §14 (rulings and contracts), `57_…` (APPL-X1 specification), `58_…` (plan, updated). Evidence:
`docs/acceptance/evidence/APPL-X1R/`.

---

## 1. Outcome against the eight absolute criteria

| | Criterion | Result |
|---|---|---|
| A | The surveys are real | **Met.** Five surveys and one shared module are published versions in Survey Studio, with modules, questions, branching and immutable fingerprints; listed in Survey Studio's normal survey listing; opened in its composer, module builder, review page and simulator (§3) |
| B | The linkage is real | **Met.** The applicability workspace reads Survey Studio's own catalogue of published versions through its API; the fake catalogue is deleted. A requirement holds the exact version id and both fingerprints. Users preview and open the survey (§4) |
| C | The policy experience is intuitive | **Built and exercised; not measured with people.** A blank policy reaches "condition → published survey → result" in the browser journey with no legacy vocabulary on screen (asserted) |
| D | Complex logic works | **Met.** AND, OR, NOT, additive, joined, explicit replacement, choose-one, unknown — evaluator tests and browser journey (§6) |
| E | Scenario testing is convincing | **Met technically.** Create, variant, reset, live results with reasons and paths, generated combinations, comparison (§5.5) |
| F | The visual designer is excellent | **Substantially improved; my own assessment in §8.** Cards read as sentences; the canvas scales by overview and neighbourhood; verified at 20, 50 and 100 requirements |
| G | No legacy regression | see §9 |
| H | Scope respected | **Met.** The only persisted content is the governed synthetic showcase. 126 of 140 development tables are untouched; rules, bindings, groups, cases, sessions and assignments are byte-identical (§3.3) |

## 2. Owner rulings AP-1 … AP-10 — recorded and implemented

| | Ruling | Implemented |
|---|---|---|
| AP-1 | No chained replacement | A chain is a **blocker**, shown on the requirement with the fix ("name everything it should replace on itself"), and refused by the evaluator (`REPLACEMENT_CHAIN`). Cycles, self-replacement and unknown targets likewise. A circle is reported on every requirement in it |
| AP-2 | No silent deduplication | The policy-wide switch is **removed**. A collision is reported for the specific requirements (`DUPLICATE_SURVEY`), leaves the plan unresolved, and is a blocker in validation with an example. The author resolves it **for those requirements** with a stated shared delivery; the plan keeps every contributing requirement. A statement for A and B never covers a later collision with C. Different versions of one survey: always an error |
| AP-3 | Three identities for variables, profiles, conditions and policies | Recorded in the design (`56_…` §14.3). In this prototype the applicability lifecycle is **simulated and labelled so on every state**; only Survey Studio's publication is server-enforced |
| AP-4 | Boolean derived variables through validated expressions | As built; no arithmetic, no code |
| AP-5 | No implicit currency conversion | A different currency is invalid |
| AP-6 | Unresolved plans show definite and pending separately | As built; pending surveys now follow the delivery order too |
| AP-7 | Several policies in scope stay unresolved | As built (`resolve_policy`); no priority, no first match |
| AP-8 | Choose-one: no implicit fallback | An alternative needs its own criterion **or** an explicit "fallback" mark. One with neither is incomplete (`MISSING_CRITERION`, blocker) and is never chosen. More than one fallback is a blocker |
| AP-9 | Keep the navigation | Only the "Survey applicability" entry exists; regrouping deferred to APPL-X5 |
| AP-10 | Independent permissions | Unchanged: the prototype needs only `survey.read`; no permission was widened |
| — | Profiles never decide applicability | A policy's profiles no longer affect evaluation at all; only its explicit **scope** does. A fact given from outside an application's profiles is still read and marked "outside the profile" — it is no longer ignored |

## 3. The real showcase

### 3.1 Inspected first

Ten published surveys existed in development before this checkpoint (walkthrough and enablement content of earlier
checkpoints). None was suitable to reuse: they are named for other checkpoints, two are protected, and none forms an
ILP / NFTF / combined set. A dedicated collection was created instead, and nothing existing was changed.

Confirmed before creating: the authoring, validation, candidate, approval and publication contracts; that a survey
published through them appears in the normal listing; that a published version has a stable id, content hash and
manifest hash; that the module library (LIB-2) can publish a module on its own and pin it by exact revision.

### 3.2 What was created — "Applicability Showcase — Synthetic Demo"

Every purpose begins "SYNTHETIC DEMONSTRATION — NOT APPROVED FOR CUSTOMER CALLS." Every wording ends "(synthetic
demonstration question)" or "(… statement)". NFTF is used as a label only; no meaning is given to it.

| Code | Name | Version | Content fingerprint | Manifest fingerprint |
|---|---|---|---|---|
| `M-100019` | Showcase welcome and understanding check (synthetic) — reusable module | 1.0 | `3b55d1929614e920…` | `6c2afad47b16898e…` |
| `S-APPL-DEMO-ILP` | A · ILP product understanding | 1.0 | `dc1effc4925fd57f…` | `4dc6080ab147f471…` |
| `S-APPL-DEMO-NFTF` | B · NFTF additional questions | 1.0 | `086b9b1d7e4c2516…` | `b5766c06095d1a8f…` |
| `S-APPL-DEMO-COMBINED` | C · Combined ILP + NFTF | 1.0 | `cd14fdc85902e2e5…` | `6a977cb552dd447d…` |
| `S-APPL-DEMO-REPLACEMENT` | D · Replacement scenario | 1.0 | `c2e24c7de04a5dd0…` | `9d2a6d44a4764204…` |
| `S-APPL-DEMO-RIDER` | E · Rider scenario | 1.0 | `689a0b44d398325f…` | `dc2f236ea21dbb68…` |

Full identities: `evidence/APPL-X1R/showcase_report.json`. Author `dev.survey.author`, approver
`dev.survey.checker`, publisher `dev.survey.publisher` for every item. A sixth survey was not added: it would have
shown nothing the five do not.

| Survey | Modules | Questions (answer kinds) | Branching |
|---|---|---|---|
| all five | the shared welcome module, pinned at revision 1 | a statement, a yes / no, a free text | "No" leads to a follow-up and ends the survey as *clarification required* |
| A | ILP understanding; closing | free text, yes / no, choose one | "No" reaches a follow-up question |
| B | NFTF additional; closing | choose one, yes / no, choose several, free text | "video" reaches an extra question; an exclusive "nothing" answer reaches a follow-up |
| C | combined ILP; combined NFTF; closing | choose one, free text, choose several, yes / no | "not sure" skips a whole module; a decision point on the selected answers |
| D | replacement; closing | yes / no, choose several, free text | "Yes" reaches two follow-ups |
| E | rider; closing | yes / no, choose one, free text | two nested branches |

Supported and used: yes / no, single choice, multi-select, free text, conditional next question, routing between
modules, straight-through flow, a reusable published module. Limits met and respected: free text cannot branch at
its own node; only controlled text-to-speech wording is publishable for synthetic content.

### 3.3 How, and what changed in the database

`Call360-backend/scripts/appl_showcase_setup.py` — HTTP only, three signed-in people, no SQL, imports nothing from
the application. Idempotent: a second run reused everything and changed no row; `--verify-only` creates nothing.
It never overwrites: anything in an unexpected state is reported as a conflict.

| | |
|---|---|
| Test schema first | `tests/test_appl_showcase.py`, 4 tests: creation; self-approval, publication by the approver and by the author all refused; second run changes nothing; 13 simulated answer paths reach an end; resume and conflict handling; no password in any output |
| Development preflight | database `Call360_db`, schema `call360`, revision `0037`; 140 tables, 16,545 rows |
| Backup | `_db_backups/call360_dev_before_appl_showcase_20261123.dump`, SHA-256 `08484a08…5b27dde5`; row counts equal the inventory; restore-to-SQL dry run clean |
| After | revision unchanged; no table, trigger, function, permission or column added. **126 of 140 tables untouched.** Changed: nine Survey Studio content tables (definitions 8→14, versions 7→13, candidates 8→14, asset versions 41→117, …) and five sign-in / audit tables |
| Legacy and operational | rule versions, publications, change events, script families and versions, script assignments, cases, sessions, runs, findings, review records, bindings, groups, composite plans: **identical digests** |

Recovery: the published showcase cannot be un-published (versions are immutable by design). It is inert: nothing
selects it operationally. To remove every trace, restore the backup above (`_db_backups/RESTORE.md`).

### 3.4 Seen in Survey Studio's own screens

| Shown | Where |
|---|---|
| In the normal survey listing | screenshot 05 |
| Composer with its LEGO modules (A, B, C) | 06, 07, 08 |
| Module builder: questions and where each answer leads | 09 |
| The same published module in several surveys | 10, and the preview in 12 |
| Review page with its publication history | 33 |
| Simulator, on the published version: a branching path run to its end | 37, 37b (journey X1R.9) and `37-development-…` |

## 4. Applicability on real published surveys

| | |
|---|---|
| Catalogue | `src/features/applicability/surveys.ts` reads `GET /survey-definitions`, then `GET /survey-versions/{id}` for each published version. The hard-coded list is gone. A draft cannot appear. The header says how many published surveys Survey Studio lists |
| Reference | `{code, version, label, version_id, definition_id, fingerprint, manifest, market}` — never a bare name |
| Picker | search, market filter, name, description, published version, market, code; multi-select; "already in this requirement"; preview from inside the picker; meaningful empty states |
| Preview | exact identity and both fingerprints; modules in order; each question with its answer kind and options; each branch in words; who submitted, approved and published it ("enforced by Survey Studio"); which requirements in this workspace use it; links to the published version and to the survey in Survey Studio |
| Both directions | applicability → preview → Survey Studio, with a "Back to … in Survey applicability" bar that returns to the same policy and view; Survey Studio → survey overview → **Where used in Survey applicability** → the requirement |
| Honest scope | "where used" covers the policies open in this browser tab and says so: applicability policies are not saved in Call360 yet |
| Pinning | a reference never moves by itself. When Survey Studio publishes a newer version, the ticket says so and offers "Adopt version N" — a deliberate, undoable edit. **Built; not exercised**, because no showcase survey has a second published version |
| Missing | a reference whose survey Survey Studio does not list is shown as "not pinned", cannot be previewed, and is a blocker (`SURVEY_NOT_PINNED`). Nothing is substituted |

No new read operation was needed: the existing Survey Studio API was sufficient.

## 5. Experience refinements

### 5.1 Policies

A gallery replaces the single seeded policy: **create from scratch**, **start with a pattern** (five, all on the
showcase surveys), **explore the showcase**, duplicate, compare two policies side by side, and a policy switcher in
the header on every screen. States are told apart everywhere: *draft · in this tab*, *unsaved*, *published ·
simulated*, and — on survey tickets — *Published in Survey Studio*, which is the only real publication.

### 5.2 Card composer

| Before (APPL-X1) | Now |
|---|---|
| the full condition builder inside every card | a card is one sentence: WHEN … THEN …, with the live outcome |
| inline editing in a narrow column | **Edit** opens a focused editor: when, then (include / choose exactly one), replaces, live result, validation beside each part |
| surveys as text chips from a fake list | tickets marked as published Survey Studio objects, with the pin and the exact version; click to preview |
| one long wall | above eight requirements every card is one line; search, filter (applies / not decided / to fix), group by survey or outcome, collapse / expand all |
| replacement by a small picker | a checklist of the other requirements, with a sentence saying which surveys disappear and why |
| choose-one silently "otherwise" | every alternative needs a criterion or an explicit fallback |

### 5.3 Canvas

Full width until something is selected; legible on opening (never below 55%). For more than twelve requirements it
opens as an **overview by survey** — how many requirements can select each survey — and shows **one neighbourhood at
a time**: select a survey to see only its requirements and their conditions; "Go to a requirement" for one
requirement and everything that leads to and from it; search; "Back to the overview". Verified at 20, 50 and 100.

### 5.4 Variables, profiles, conditions

A profile cannot add a variable it already inherits. Each condition has its own editor instance. Conditions shown as
used across several policies. Inline creation of a variable from inside a requirement returns to the same
requirement with the new fact joined by AND (journey X1R.5).

### 5.5 Scenario lab

The fact editor now shows **only the facts this policy reads** by default (toggle for the whole profile), with
search, filters (not known or invalid / left out / changed from the baseline), collapsible groups, and "Reset to
baseline" for a variant. A fact the policy reads is always offered. The result stays beside it.

### 5.6 Smaller things

The workspace's own breadcrumb is removed (the shell already has one) in favour of the policy switcher. The command
palette finds policies and acts on what is typed. Undo names the change ("Undo: State that one delivery…").

## 6. Demonstrations

Browser: `e2e/applicability/journey.appl.ts`, nine scenarios in one page against the real backend, with the showcase
published by the governed API in the global setup. Evaluator: `tests/test_survey_applicability.py`.

| Owner's journey / scenario | Result |
|---|---|
| A — build and link from a blank policy; open Survey A; return to the same context | **shown** (X1R.2) |
| B — NFTF → B, joined → C; both true selects all three with exact versions | **shown** (X1R.3) |
| C — C explicitly replaces A and B | **shown** (X1R.4) |
| D — ILP true, NFTF unknown: A definite, B and C pending, unresolved | **shown** (X1R.3) |
| E — a LEGO module reused across surveys; applicability references whole surveys | **shown** (X1R.1, preview in X1R.2) |
| F — a published showcase survey run in Survey Studio's simulator, then back | **shown** (X1R.9; also on development, screenshot 37). This is the survey's own simulation, **not** a journey selected by an applicability plan — that is APPL-X5 |
| G — from zero: missing variable, condition, real survey, several surveys, new scenario, graph, matrix | **shown** (X1R.5, X1R.4) |
| Scenarios 1–5, 9 | shown in the browser and in evaluator tests |
| 6 duplicate, resolved explicitly | **shown** (X1R.3) |
| 7 OR, 8 NOT | evaluator tests; available as the pattern "Either condition, and but not". Not driven in the browser journey |
| 10 choose one: one, none, several, unknown, fallback, no fallback | evaluator test (all six); browser: one eligible, fallback, unknown, incomplete (X1R.6) |
| 11 invalid replacement | circle blocked in the browser (X1R.4); chain and self-replacement in evaluator tests |
| 12 several policies in scope | evaluator test only |
| Large policy (Task 7) | found, edited and regrouped among fifty (X1R.7) |
| Error recovery (Task 8) | an invalid replacement and an incomplete alternative made and corrected (X1R.4, X1R.6) |

## 7. Usability

Tasks 1–8 were walked through by the automated journey. **No task was performed by a person, so no usability goal is
reported as met.** What can be stated:

| Goal | Status |
|---|---|
| A first-time user understands WHEN → THEN | not measured |
| An experienced user configures the three-survey scenario in under five minutes | not measured (the journey does it in seconds, which says nothing about a person) |
| A user can explain why each survey was selected | not measured; the explanation, the path and "what would settle it" are on screen |
| A user can open the source survey without losing work | **verified mechanically**: the draft survives the round trip |
| A user can identify unresolved facts quickly | not measured; the missing fact is named and marked in the editor |
| A large policy remains navigable | **verified mechanically** at 20, 50, 100; not measured with people |
| No routine workflow needs the legacy vocabulary | **verified**: the words do not appear in the workspace |

## 8. Critique

What I think is good now: the sentence card; real surveys with a preview that shows branches in words; the round
trip; the canvas overview; the per-collision resolution, which makes AP-2 concrete.

What is still weak:

* **The header is crowded** at 1440: the policy switcher, three status chips, undo, redo, the persona and search
  share one row.
* **The scenario lab is long** when "every fact of the profile" is shown.
* **Drag and drop** (palette to card, card order, delivery order) has keyboard alternatives but **still no automated
  test**.
* **The canvas neighbourhood for one survey in a 100-requirement policy** still shows twenty requirement nodes with
  their conditions; it is navigable, not elegant.
* **Screenshots are from the isolated test environment** (the journey), where the showcase was published by the same
  script; one screenshot (37) is from development. The development content was checked separately by a script.
* **"Adopt a newer version"** is untested for lack of a second published version.
* Governance of applicability remains a simulation; I have labelled it rather than improved it.

## 9. Regression

Run on 2026-11-23 against the isolated test schema. Outputs: `docs/acceptance/evidence/APPL-X1R/`.

| Check | Result |
|---|---|
| Backend suite | **1,049 passed, 0 failed** — 1,045 before, plus the 4 showcase tests; the 21 evaluator tests updated for the rulings |
| Golden fixtures | the 82 expected runs and 14 expected plans pass; **no fixture or expectation file is modified** |
| Backend lint, format, types | clean (`ruff` on 270 files, `mypy` on 132) |
| OpenAPI | unchanged since APPL-X1 (SHA-256 `f7a71873…802f480e9`); no operation or schema added; the frontend client matches |
| Frontend unit tests | **636 passed** |
| Frontend types, lint, build | clean |
| Playwright — applicability | **9 passed** |
| Playwright — persisted | **34 passed**, unchanged |
| Playwright — prototype | **13 passed**, unchanged |
| Playwright — standard | **33 passed**, unchanged |
| Accessibility | no serious or critical violation (axe, WCAG 2.2 AA rules) on the six screens, the designer, the requirement editor and the survey picker. Not a screen-reader test |
| Widths | no sideways overflow at 1280, 900 and 390 on six screens and the designer; cards and canvas checked at 20, 50 and 100 requirements |
| Specs validator | passes |

Honest notes on the runs:

* The first full run had three failures. Two were mine: a unit test still naming the old fake survey code, and an
  accessibility scan taken while the page was scrolled under the sticky header. Both were corrected and re-run.
  The third was `voice.spec.ts` (S1-B, a timing assertion on a stored session record) in the standard suite; nothing
  in this checkpoint touches voice, and the whole standard suite passed on the re-run (33 of 33). I regard it as a
  timing flake but have not investigated its cause.
* The persisted, standard and applicability suites and the static checks were re-run after the last frontend change.
  The prototype suite and the backend suite ran before the last frontend-only edits (a preview link, styles and the
  journey file), which they do not load or test.
* Existing tests changed in this checkpoint: none outside the applicability evaluator's own test file.

## 10. Not done, and not authorised

No applicability table, migration or persisted policy or scenario. No operational assignment, voice integration or
Script Studio change. No permission widened. The legacy assignment rules, survey bindings and requirement groups
were neither read nor written by the new code. APPL-X2 was not started.
