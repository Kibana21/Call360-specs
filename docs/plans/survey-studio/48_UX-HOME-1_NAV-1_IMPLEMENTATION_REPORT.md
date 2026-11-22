# UX-HOME-1 + NAV-1 — Survey Studio workspace and consolidated navigation: implementation report

**Status: ACCEPTED by the owner as TECHNICALLY VERIFIED on 2026-11-22 (D-330) — "This is not final business-user UX
or screen-reader acceptance." Decisions reconciled in D-331; five follow-up UX issues closed in D-332 (`50_…` §2).**
**Synthetic data only.** No survey execution, assignment, evaluation, finding or review semantics were changed; no
published content, revision, fingerprint or golden expectation was touched; no migration was added. Technical
verification is not a business UX sign-off or a screen-reader sign-off.

Authorisation: the owner's message of 2026-11-22, "UX-HOME-1 + NAV-1 — Survey Studio Workspace Redesign and
Enterprise Navigation Consolidation". Companion: `47_…` (assessment and design), contract `04_…` §21, decisions
D-321…D-329, `docs/product/SCREEN_NAMING_AND_ROUTES.md` (navigation amended).
It supersedes `46_UX-HOME-1_WORKSPACE_REPORT.md`.

---

## 1. What changed

### Navigation (NAV-1)

| | |
|---|---|
| Sidebar | five groups — Workspace, Design & Govern, Simulate & Analyze, Operations, Legacy & Administration — instead of four. Entries can open to show their pages; the open entry and page follow the address; a toggle opens or closes a section by mouse or keyboard |
| Nothing removed | every earlier route keeps its label and its guard. A unit test lists the fifteen earlier entries and asserts each is still there in every mode |
| Sub-pages | Survey Studio: Home, Surveys, Building blocks, Rules explorer. Assignment Rules: Rules, Survey bindings and groups. Simulation & Evaluation: all of it, Application journeys, Controls and evidence, Simulation Workbench |
| Permission | a sub-page is listed only for a person who holds its permission. Listing is a convenience: every route's own guard, and the server, still decide. No route or aggregate widens what anyone can read |
| Breadcrumb | the top bar now says the group and, where there is one, the parent entry (a link) and the page |
| Simulation & Evaluation | one page (`/survey-studio/simulation`) that says which simulator and which evaluation screen is for what, and opens it: Survey simulator, Coordinated simulation, Application journeys, Control evaluation, Execution assurance — and the Script Studio Simulation Workbench as a separate mode with its own engine. It runs nothing |
| Script Studio | kept, reachable, tagged "Legacy"; its accessible name is unchanged. Nothing of it was retired, hidden or migrated |
| Review Workbench | in its own group, Operations. Not merged with the Evaluation Workbench in any respect |

### Survey Studio

| | |
|---|---|
| Home | header "Survey Studio — Design, reuse and govern customer journeys"; Create survey, Create module, Explore building blocks; one search; seven live counts (surveys, modules, questions, conditions, answer sets, drafts, awaiting review), each opening its filtered list; your surveys, most recently saved first; "Awaiting you" when something awaits; five capability cards; a row of the most reused modules; a one-line environment notice |
| Building blocks | modules, questions, conditions, answer sets; cards or a list; search; sort by name, reuse or version; latest revision / reused / every revision; 24 to a page. Module cards show category, a strip of tiles for what is inside, question count, whether it branches, endings, how many surveys reuse it, and the published revision |
| Module Inspector | eight sections (below) |
| Surveys | cards with status, published version, draft revision, modules, questions, whether anything branches, last saved — or a table. A survey opens to an **overview** before any editor: its modules in the order they run, how each is entered and where it leads, its dependencies, its versions and submissions; with Open the builder, View published version, Simulate, Review and governance, and Inspect on each published module |
| Rules explorer | six families: Assignment rules, Requirement groups, Survey logic, Control applicability, Evidence mappings, Finding rules |
| Creating a block | "Create module" (and New question / condition / answer set in the gallery) says where that kind is made — inside a survey — and opens the survey to make it in. It creates nothing itself (limitation L-2) |

### Backend — read-only, no migration

| | |
|---|---|
| `GET /api/v1/survey-definitions/workspace` | counts, recents, what awaits the reader, reused modules, and `surveys[]`: what each survey's draft holds |
| `facts.branching` on a module in the library | whether its own document sends different answers or conditions to different places |
| Test setup only | one read-only identity that may read across the platform, for the browser journey |

## 2. What was reused

The component library and its drawer (reuse, "Edit a copy for this survey", revision comparison); the composer,
builder, review, candidate and version screens; the simulators; Survey assignment; Control policies and evidence;
the Evaluation Workbench and Application journeys; Assignment Rules, Finding Rules, Review Workbench and Script
Studio untouched. The candidate restrictions that decide "awaiting you" are the ones the operations enforce.

Not built: a second Survey Studio, a rule engine, a component registry, an evaluation engine, a JavaScript
implementation of survey logic. The graph is drawn from the published document; testing opens the existing
simulator, which runs the authoritative Python engine.

## 3. The Module Inspector, section by section

| Section | Shows | Where the data comes from |
|---|---|---|
| Overview | description; market; status; provenance (the survey version that published it; what it was made from); how widely pinned; **governance history — who submitted, approved and published the version it came with** | library detail; the version and candidate records |
| Questions | every step: exact published wording; kind of answer; answers with special behaviour; how many may be chosen; number and text rules; whether it must be answered; what an invalid answer does; every branch and its destination; the question's own version and wording version | the module document and its dependency documents |
| Logic | entry; that a module has no entry condition of its own, and the conditions surveys set on it; exits; an interactive graph. **Selecting a step** shows its question, validation and branches. **Selecting a branch** shows the exact thing that makes it: the link id and the answer option and answer-set version, or the condition result and condition version, or the routing rule, follow-up, interruption or rejoin | the same document; nothing approximated |
| Rules | each reusable condition: name and version, its rule as a sentence, the values supplied, earlier answers read, where in the module it is used, what happens when met, not met and undecidable | condition documents and their bindings |
| Dependencies | every pinned document, what it is, its exact version and fingerprint; each opens in the inspector | library detail |
| Where used | every survey that pins this revision: version, status, the exact revision pinned, how it is entered and left there, links to the version, the survey and the builder. States that a newer revision changes no survey | library detail; version content |
| Versions | every published revision; comparison in sentences (the library's own comparison: wording, answers, steps, routes, conditions); says so when only one exists | library detail |
| Test | that a module cannot be simulated alone, and the simulator of each survey that pins it | — |

Actions, by permission: Reuse in a survey (which also offers "Edit a copy" — a new draft; the published revision is
never changed), Test in a survey, Open in the builder. A reader sees none of them and is told why.

## 4. The twenty-six browser journeys

`e2e/persisted/zzzz-uxhome1.persisted.ts` — one journey, real browser, real backend and database (isolated test
schema, on everything the 26 earlier journeys published). The screen is asserted against the server's records.

| # | Journey | Result |
|---|---|---|
| 1 | Open the homepage | passes |
| 2 | Actual dashboard inventory | seven counts equal the server's |
| 3 | Modules gallery | from its count; pagination, sort, list layout, reused filter, conditions tab |
| 4 | Search for a published module | found; a survey is found by the same search; no match says so |
| 5 | Open the Module Inspector | from the result; the address names the block |
| 6 | All module questions | one row per node of the document; exact wording; one branch line per link |
| 7 | An actual branching graph | one node per step; every ending; the module chosen is one that really branches |
| 8 | Click a graph node | its question is shown and its step selected |
| 9 | Click a branch | the link id and the answer option that make it |
| 10 | Inspect a reusable condition | in the module when it has one; and from the rules explorer into the inspector |
| 11, 12 | Consuming surveys and pinned revisions | each survey, its version, "pins revision n", how it is entered |
| 13 | Compare revisions | on a module with two published revisions when the data has one; otherwise the inspector says only one exists |
| 14 | Reuse through the existing workflow | the chosen survey opens with its library on the block, with "Add to this survey" and "Edit a copy"; the survey's draft is unchanged |
| 15 | Return without losing context | Back restores the view and the open inspector; Escape closes it |
| 16 | Browse Surveys, open a published survey | cards, table, filter; the overview with its modules; a module inspected from it; the published-version screen |
| 17 | Rules Explorer → an Assignment Rule | the rule's own screen opens |
| 18 | The Finding Rules editor | from the explorer and the sidebar |
| 19 | A coordinated simulation | from Simulation & Evaluation |
| 20 | Control evaluation and Application journeys | both open; a journey opens |
| 21 | Review Workbench separately | under Operations |
| 22 | Script Studio with an authorised identity | under Legacy & Administration |
| 23 | Existing deep links | four addresses open, with the right entry active; a link straight to a block opens it |
| 24 | Permission-restricted actions | a reader has no create, reuse, test or builder action, no assignment entry; the server answers 403; a guarded route stays guarded |
| 25 | Cross-market | another market sees zero surveys and blocks, finds nothing by search, and a block's address says it is not published in a market they can read |
| 26 | Several widths | 1440, 1280 and 900: screenshots; no sideways overflow at 900 |

Keyboard and accessibility checks in the journey: the sidebar toggle is operated with the keyboard and reports its
state; `aria-current` marks the active entry; the inspector closes with Escape; a selected step and branch report
`aria-pressed`. The existing accessibility journey (`a11y.spec.ts`) still passes with five groups.

**What step 13 depends on.** The inspector compares any two published revisions; whether the browser journey
exercises it depends on the test data holding a module with two published revisions. The run recorded in §6 says
which branch it took.

## 5. Evidence

`docs/acceptance/evidence/UX-HOME-1/`:

| Folder | Content |
|---|---|
| `before/` | the first page as it was, four widths |
| `after/` | twenty screenshots from the browser journey: workspace and sidebar; create module; gallery; search; inspector overview and governance; questions; the graph with a branch's routing rule; where used; reuse; surveys gallery; survey overview; consolidated sidebar; rules explorer; a condition inspected; Simulation & Evaluation; 1280 and 900 wide |
| `after-development/` | the six main screens on the development server at 1440, 1280 and 900 wide |

## 6. Regression

| Check | Result |
|---|---|
| Full backend suite (`call360_test` only) | **1,009 passed, 0 failed** (1,008 before; the new test is the workspace summary) |
| 82 golden execution runs, 14 golden call plans | pass; fixture files unmodified in both repositories |
| Frontend unit suite | **624 passed** (612 before; new: navigation, the inspector's reading of routing, plain-language rules) |
| Persisted browser journeys | **27 passed** (26 earlier journeys unchanged + the 26-step UX-HOME-1 + NAV-1 journey) |
| Prototype browser journeys | 13 passed |
| Standard browser journeys | 33 passed — including Script Studio, Assignment Rules, Simulation Workbench, Finding Rules, Review Workbench and the accessibility journey, through the new sidebar |
| `ruff check`, `ruff format --check`, `mypy app` | clean |
| `tsc`, `eslint`, production build | clean |
| OpenAPI | 271 operations, 512 schemas. Against the last committed contract: nothing removed, no existing property changed; one response field added (`surveys` on the workspace read). `facts.branching` is inside an untyped object. SHA-256 `e7aface99882fb28807078d9cb1a1a3cc79e5a9cf650924e60445a9e9c4e3b20` |
| Specs validator | passes |

Order of the final runs: the prototype, standard and backend suites ran on the finished code; one stylesheet-only
change followed (seven count tiles in one row at 1280 px), after which the static checks, the unit suite, the build
and the persisted suite were run again and passed. The prototype, standard and backend suites were not repeated
after that stylesheet change.

Step 13 of the journey took its first branch: the test data holds a module with two published revisions, and the
comparison was exercised in the browser (`UXHOME09`).

Existing tests changed: `App.test.tsx` and `a11y.spec.ts` (the five group names and their count), one test title in
`Studio.test.tsx`. No expectation of behaviour and no golden fixture was changed. Three defects found by the
journeys and fixed during the work: a lost update when two address changes happened in quick succession; a branch
that jumped over steps was drawn behind them (now routed round the side); a "Legacy" tag that changed Script
Studio's accessible name (now decorative).

## 7. Missing capabilities, performance, accessibility, compatibility

**Missing capabilities (none was faked):**

| | |
|---|---|
| L-1 | no cross-kind server search: search runs in the browser over lists loaded once |
| L-2 | a building block cannot be created outside a survey. The owner asked why on 2026-11-22; the answer (a design ruling, LIB-D-1, not a technical limit) and a proposal for independent authoring (LIB-2) are recorded in D-328. Not built |
| L-3 | a module cannot be simulated on its own; Test opens a survey that pins it |
| L-4 | no owner, no usage frequency and no "last updated" exist for a block; none is shown. "Reused" is a count of surveys whose published versions pin it |
| L-5 | finding rules are listed only for a reader holding the existing Finding Rules permission |
| L-6 | the gallery lists published blocks only (that is what makes them reusable); status filters therefore apply to surveys |
| L-7 | "Awaiting you" is exact for survey candidates (server rules) and derived in the browser, from each record's status, proposer and approver, for policies, mappings, bindings and groups |
| L-8 | follow-up and rule-ordered routing are drawn and described; the browser test data has per-answer and "always next" routing, so those two forms are verified by a unit test, not in the browser |

**Performance.** The home page makes ten reads once (one aggregate, the surveys, four library lists, four
governance lists); the inspector one, plus two per consuming survey; the survey overview two. Lists are filtered and
paged in the browser. Fine at today's volumes; a server search and paging are the next step at scale.

**Accessibility.** Keyboard: every card, tab, graph node, branch label, section and toggle is a real control with
visible focus; drawers take focus and close with Escape; reduced motion is respected. Not done: focus is not trapped
inside a drawer; nothing was tested with a screen reader.

**Navigation compatibility.** No route was renamed or removed. Labels are unchanged. Two existing tests that pinned
the group names and count were updated to the five groups (`App.test.tsx`, `a11y.spec.ts`), and one test title. The
protected Script Studio files were not modified. The sidebar's grouping is an intentional, owner-directed deviation
from the approved HTML mockup, recorded in `SCREEN_NAMING_AND_ROUTES.md`.

## 8. State

| | State |
|---|---|
| Development database | `0035_survey_execution_assurance` — unchanged; **no migration in this checkpoint**; not reset or re-seeded |
| `Call360-backend` | `main` at `92aa725` (the owner's commit, which includes the first UX-HOME-1 version); 7 files uncommitted |
| `Call360-frontend` | `main` at `ea8a354` (the owner's commit); 23 files uncommitted |
| `Call360-specs` | `main` at `76d70f2` (the owner's commit); documents and evidence uncommitted |
| Commits or pushes by the assistant | none |

## 9. Stopped here for review

Nothing further was started. I committed and pushed nothing.
