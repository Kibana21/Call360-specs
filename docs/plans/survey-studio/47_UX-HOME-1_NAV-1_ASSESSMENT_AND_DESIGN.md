# UX-HOME-1 + NAV-1 — Assessment and design

**The assessment (Part A) was made by inspection before the navigation, the explorers and the inspector upgrade were
built; this document was written up while they were being built.** The implementation report is `48_…`. It
supersedes `46_UX-HOME-1_WORKSPACE_REPORT.md`, whose workspace is the starting point of this checkpoint.
**Synthetic data only.** No business, evaluation or rule semantics are added or changed.

---

## 1. Existing navigation and route hierarchy (before)

Sidebar (`src/app/nav.ts`), four groups from the approved mockup (owner decision C-1):

| Group | Items |
|---|---|
| Workspace | Overview `/` · Call Explorer `/calls` · Policy Explorer `/policies` · SBQ Risk Workbench `/risk-assessments` · Work Queues `/queues` · Voice Studio `/voice-studio` · Voice Lab `/voice-lab` · Live Monitor (S4) · Campaigns (S4) |
| Governance | Survey Studio `/survey-studio` (when its setting is on) · Script Studio `/scripts` · Assignment Rules `/assignment-rules` · Simulation Workbench `/simulator` · Finding Rules `/finding-rules` · Review Workbench `/reviews` |
| Intelligence | Search `/search` · Analytics (S4) |
| Platform | Data Intake `/intake` · Administration `/admin/users` |

Everything built since SS-03B lived **inside** `/survey-studio/*` and was reachable only from links on the Survey
Studio first page: `assignment`, `coordinated-simulations/:id`, `evaluations/:id`, `controls`, `journeys…`,
`surveys/:code/…` (composer, `modules/:instance`, `simulate`, `plan`, `validate`, `review`, `candidates/:id`,
`versions/:id`). The sidebar showed none of it. Route guards: `survey.read` for the persisted studio; `script.read`
for Script Studio, Assignment Rules, Simulation Workbench, Finding Rules; `queue.read` for Review Workbench.

## 2. Screens that overlap in user purpose

| Purpose | Screens | Verdict |
|---|---|---|
| "Which survey does an application get?" | Assignment Rules (rule editor) · Survey assignment (bindings, groups, composite plans) | Two halves of one job. Kept as two screens; shown under one sidebar entry |
| "Try it before a call" | Simulation Workbench (script engine) · Survey Simulator · Coordinated simulation | Different engines and contracts. One navigation entry with separate modes; engines untouched |
| "What did the answers mean?" | Review Workbench (operational cases) · Evaluation Workbench (simulated journeys) | **Different capabilities.** Never merged: separate persistence, permissions, findings. Different sidebar groups |
| "What rules exist?" | Assignment Rules · Finding Rules · Control policies · module conditions | Four engines. One read-only explorer that links to each owner |
| "Find a reusable block" | the library drawer inside a survey · (nothing outside a survey) | The workspace gallery and inspector read the same library |

## 3. Which modules remain authoritative

| Concern | Authoritative | What UX-HOME-1 + NAV-1 does with it |
|---|---|---|
| Assignment rules | Assignment Rules (`/assignment-rules`, script-side tables) | lists and links; no editor, no engine |
| Bindings, groups, composite plans | Survey assignment | lists and links |
| Finding rules | Finding Rules (`/finding-rules`) | lists (with its own permission) and links |
| Control policies, mappings | Control policies and evidence | lists and links |
| Survey content, publication | Survey Studio composer, builder, review screens | opens them; changes nothing |
| Reusable blocks | the component library (LIB-1): what a published version pins | reads it; **no second registry** |
| Execution | the Python survey engine; the script engine | links to their simulators |
| Operational review | Review Workbench | a link in its own group |

## 4. Library metadata and dependency relationships available

From `GET /survey-components` and `…/{kind}/{code}/{version}`: title, description, category, counts of questions,
statements and decisions, endings, fingerprint, latest version, every published revision, the published versions
that pin each revision (survey, version label, status), how many surveys and versions pin it, the full document, and
**every dependency document with its exact version and fingerprint** (questions, wordings, answer sets, conditions),
`derived_from`, required customer or policy fields. From `GET /survey-versions/{id}/content` and `/{id}`: how each
consuming survey enters and leaves a module, and who published. From `GET /survey-candidates/{id}`: who submitted and
approved.

**Not available, and therefore not shown or shown as absent:** an owner of a block; a "last updated" time of a block
(a published revision never changes; the time shown is its publication); usage frequency of any kind; a market on a
block (blocks are listed per the reader's markets).

## 5. Existing APIs that power the dashboards and inspectors

`/survey-definitions`, `/survey-definitions/{id}/draft/documents`, `/{id}/history`, `/survey-components…`,
`/survey-versions/{id}`, `/{id}/content`, `/survey-candidates/{id}`, `/survey-assignment/policy`, `/groups`,
`/survey-evaluation/control-policies`, `/mappings`, `/journeys`, `/finding-rule-sets`.

## 6. Missing read-only APIs — and what was added

| Missing | Added |
|---|---|
| counts, recency, "awaiting me" in one read | `GET /survey-definitions/workspace` (UX-HOME-1) |
| what each survey holds without opening it (modules, questions, branching, last saved, last published) | field `surveys[]` on the same read |
| whether a module branches, without fetching every document | `facts.branching` on the library's module summary |
| a cross-kind server search | **not added** — search runs in the browser over the lists (limitation L-1) |
| finding rules for a reader without the Finding Rules permission | **not added** — it would widen who can read them |

No table, no migration, no setting, no permission.

## 7. Limitations affecting the experience

L-1 search is client-side; L-2 a building block cannot be created outside a survey (the owner's question of
2026-11-22; a proposal exists, LIB-2); L-3 a module cannot be simulated alone; L-4 no owner or usage data on blocks;
L-5 the two engines' simulators differ and stay separate; L-6 Survey Studio's assignment, evaluation and journey
screens exist only in persisted mode; L-7 no identity in development holds both survey and script permissions.

## 8. Proposed information architecture (as built)

**Sidebar — five groups.** Every earlier route and label is kept.

| Group | Entry | Pages under it (persisted mode; shown to a person who may open them) |
|---|---|---|
| Workspace | Overview · Search · Call Explorer · Policy Explorer · SBQ Risk Workbench · Work Queues | — |
| Design & Govern | **Survey Studio** | Home · Surveys · Building blocks · Rules explorer |
| | **Assignment Rules** | Rules (`/assignment-rules`) · Survey bindings and groups (`/survey-studio/assignment`) |
| | **Finding Rules** | — |
| Simulate & Analyze | **Simulation & Evaluation** (`/survey-studio/simulation`) | All simulation and evaluation · Application journeys · Controls and evidence · Simulation Workbench (`/simulator`) |
| | Analytics (S4) | — |
| Operations | Review Workbench · Voice Studio · Voice Lab · Live Monitor (S4) · Campaigns (S4) | — |
| Legacy & Administration | Script Studio *(Legacy)* · Data Intake · Administration | — |

Without Survey Studio's persisted setting the same five groups are shown with the same entries and no sub-pages,
and "Simulation Workbench" is the entry under Simulate & Analyze.

**Survey Studio.** Home (counts, your surveys, ways on, a row of modules) · Surveys (cards or table → survey
overview → builder) · Building blocks (modules, questions, conditions, answer sets → inspector) · Rules explorer
(six families → the owning screen). Inspectors are drawers named in the address, so Back returns to the view left.

**Module Inspector.** Eight sections with a tab row: Overview (purpose, market, status, provenance, governance
history) · Questions · Logic (entry, exits, interactive graph; a selected step or branch shows what makes it) ·
Rules · Dependencies · Where used · Versions (compare) · Test.

**Rules explorer.** Assignment rules · Requirement groups · Survey logic · Control applicability · Evidence mappings ·
Finding rules. Each entry: what it is for, scope, when and then, version, status, where used, the owner's screen.
A discovery page: no rule language, no evaluation, no governance of its own.
