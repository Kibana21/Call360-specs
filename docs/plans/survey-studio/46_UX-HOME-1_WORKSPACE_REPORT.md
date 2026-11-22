# UX-HOME-1 — The Survey Studio workspace: assessment, design and implementation report

**Status: BUILT AND TECHNICALLY VERIFIED 2026-11-22, awaiting the owner's UX review. Not accepted.**
**Synthetic data only.** No evaluation or business-rule meaning was added or changed. Technical verification is not
a business UX sign-off or a screen-reader sign-off.

Authorisation: the owner's message of 2026-11-22, "UX-HOME-1: Redesign the Actual Survey Studio Homepage".
Companion: contract `04_…` §21, decisions D-321…D-324.

---

## 1. Assessment before building: what existed, and where a lookup or an aggregate was needed

The persisted Survey Studio first page listed surveys in a table with three text links and a paragraph of notice.
Nothing on it showed that a component library, conditions, rules, governance queues or reuse existed — although all
of them did.

| Needed by the workspace | Already served by | Gap |
|---|---|---|
| Surveys with status | `GET /survey-definitions` | no time of last save or publication → **aggregate** |
| Published modules, questions, conditions, answer sets, with where each is published and how widely pinned | `GET /survey-components?kind=` (LIB-1) | none |
| A block complete: its document, every document it depends on, its revisions, its consumers | `GET /survey-components/{kind}/{code}/{version}` | none — this is everything the inspector needs about the block itself |
| How a consuming survey enters and leaves a module | `GET /survey-versions/{id}/content` | none (a lookup per consuming version) |
| Who published the version a block came with | `GET /survey-versions/{id}` | none (a lookup); who submitted and approved is on the candidate, not read here |
| Counts by kind; reuse | derivable from the lists | **aggregate**, so the numbers are the server's |
| What awaits the signed-in person | candidate restrictions exist per candidate (`store.restrictions`) | **aggregate** over open candidates |
| Assignment rules, bindings, groups | `GET /survey-assignment/policy`, `/groups` | none |
| Control applicability | `GET /survey-evaluation/control-policies` | none |
| Finding rules | `GET /finding-rule-sets` (Finding Rules' own permission) | none added: a reader without that permission is told so |
| Search across kinds | `q` on each component list; none for surveys | done in the browser (§6) |

**One read-only operation was added: `GET /api/v1/survey-definitions/workspace`** — counts, the six most recently
saved drafts and published versions, what awaits the reader, and modules pinned by more than one survey. No table,
migration, setting or permission. Everything else reads operations that already existed.

## 1a. The owner's review during the checkpoint, and what changed

The first version put everything on one long page. The owner's review (2026-11-22): *"Where do I create the building
blocks like modules, questions, conditions and answer sets? I still feel that the screen is very cluttered. Organize
it well."* Two changes followed:

1. **Three views instead of one page** — Overview, Surveys, Building blocks (and a link to the rules explorer), as
   one row of tabs under the header. The overview is now: the five counts, the reader's surveys, the four ways on,
   and one row of at most four modules. "Recently edited" and "Recently published" became one list of surveys, most
   recently saved first; the separate "reused modules" section became the order of that one row; "Awaiting you"
   appears only when something awaits or is waiting on someone else. The surveys grid and the full gallery moved to
   their own views.
2. **"New building block"** beside "New survey" (and "New module / question / condition / answer set" in the gallery
   and in its empty states). Building blocks are not created on their own in Call360: each is authored inside a
   survey — a module in the survey's composer, a question, condition or answer set inside a module — and becomes a
   reusable block when that survey is published by three people. The panel says exactly that for the chosen kind, in
   three steps, and lists the surveys open for editing to make it in. **It creates nothing itself**, and no way of
   creating a block outside a survey was added: that would be a second authoring path beside the governed one.

The table below describes the page as reorganised.

## 2. What was built

| | |
|---|---|
| Backend | the workspace summary operation in `app/api/survey_definitions.py`; `tests/test_survey_workspace.py` |
| Frontend | `persist/Workspace.tsx` (the first page), `persist/Inspector.tsx` (the inspector), `persist/RulesExplorer.tsx`, `persist/workspaceApi.ts`; a deep link into the existing library drawer (`Library.tsx`); routes in `PersistedStudioRoot.tsx`; styles appended to `survey-studio.css` |
| Tests | `workspaceApi.test.ts`; `e2e/persisted/zzzz-uxhome1.persisted.ts` |

The old list page was removed; its test hooks are kept on the new elements, so every earlier browser journey runs
unchanged. Script Studio, the prototype Survey Studio and all engines are untouched.

### The workspace, against the ten required items

| # | Required | Built |
|---|---|---|
| 1 | Workspace header and primary creation actions | "Survey Studio" header; **New survey** (the existing create form) and **New building block** (where each kind is made, and the survey to make it in); a reader sees "read only" instead |
| 2 | Studio-specific search across asset types | one search box: surveys, modules, questions, conditions and answer sets, by name, wording, description, code or the survey a block is published in; results grouped by kind |
| 3 | Live inventory from persisted data | five tiles — surveys (published / draft only / in review), modules, questions (and statements), conditions, answer sets, each with how many are reused — the server's counts; each tile opens its view |
| 4 | Recently edited drafts and published content | "Your surveys": every survey, most recently saved first by the record's own time, each with its draft revision, published version and status |
| 5 | Governance actions awaiting the signed-in user | "Awaiting you", shown when there is something: what the identity rules and the reader's permissions allow now, and what the reader submitted that waits on someone else |
| 6 | Featured or frequently reused modules where verifiable | the overview's row of modules is ordered by how many surveys pin each, and a reused one is tagged; the gallery has a "reused by more than one survey" filter. **No frequency or popularity figure exists, so none is shown** |
| 7 | A visible Building Blocks gallery | a row of module cards on the overview and the full gallery in its own view: tabs for modules, questions, conditions, answer sets; cards, not tables; each module card carries a strip of tiles — one per question, statement and decision, then its endings — drawn from the module's published counts |
| 8 | Entry points to Assignment, Control Policies, Evaluation, Application Journeys | "Go to": four cards with a sentence each, including the rules explorer; shown only to a person who may open them |
| 9 | Compact synthetic-environment notice | one line beside the tabs, with the full text behind "Why"; the market is a chip beside it |
| 10 | Responsive desktop layout using the width | fluid to 1,680 px; five, three or two inventory columns; the side column folds under at 1,180 px; one column at 860 px |

### Asset discovery

Surveys are cards with status filters (all, published, draft only, in review). Blocks have a filter for the latest
published revision of each, those reused by more than one survey, or every published revision; cards show kind,
category or answer type, reuse, where published and version. Market scope is shown on survey cards and in the header.
Dependencies and consumers are in the inspector.

### Rules explorer (`/survey-studio/rules`)

Four families, each from the module that owns it, in words, with a link to that module's screen:

| Family | Read from | Links to |
|---|---|---|
| Assignment rules | Survey assignment's policy: each published rule's conditions, the survey version it is bound to, the requirement group it is in | Assignment Rules (for a person who may open it), Survey assignment |
| Survey logic | the library: published conditions with their rule as a sentence; published modules with their branch counts | the inspector |
| Control applicability | published control policies: each obligation, when it applies, the evidence it needs | Control policies |
| Finding rules | Finding Rules' own list | Finding Rules |

It evaluates nothing and changes nothing. It is not a registry: remove the page and no rule is affected.

## 3. The Module Inspector, against the eleven required items

Clicking a module card opens a drawer over the workspace; the address names the block, so it can be linked.

| Required | Shown |
|---|---|
| Every question and answer type | "Every step": each step with its exact wording and kind of answer |
| Options and response validation | answers (with "cannot be combined", "other, with text"), how many may be chosen, the number or text accepted, whether it must be answered, what an acknowledgement means |
| Every branch and its destination | under each step: each branch in words and where it leads, as a link to that step; rule-ordered routing, follow-ups, interruptions and rejoin points each as their own line |
| Reusable conditions and what they evaluate | each condition as a sentence ("is met when …"), the values supplied, the earlier answers read, what happens when it cannot be decided; "unknown is never read as not met" |
| Module entry and exit behaviour | the first step and the endings; then, for each consuming survey, when it is entered there (always, or under which condition and values) and where each ending leads |
| Exact dependency versions | a table of every pinned document with code, version and fingerprint |
| Consuming surveys and their pinned versions | each survey, the version that pins this revision, with links to that version |
| Version history and governance | every published revision, where it was published, what differs between two (the library's own comparison), and who published the version it came with |
| A visual, interactive execution graph | steps as nodes from the first step downward, branches as labelled arrows, endings as terminals; selecting a node selects its step and highlights its branches; a branch that jumps over steps or goes back runs round the side in its own lane |
| An entry point to test the module | "Test in …" opens the simulator of a published survey that pins it (permission: simulate) |
| Permission-aware reuse and edit actions | "Use in a survey" (permission: edit) opens the chosen survey with its library on this block, where the existing "Add to this survey" and "Edit a copy for this survey" are; a reader is told what is needed instead |

Questions, conditions and answer sets open in the same drawer with their own content, consumers, revisions and
dependencies.

## 4. Primary acceptance test

*"A user opening Survey Studio must be able to discover any available published module, inspect every question and
rule inside it, understand all branches and where it is reused, and launch the next permitted action — all from the
workspace."*

`e2e/persisted/zzzz-uxhome1.persisted.ts`, in a real browser against the real backend and database (test schema, the
content the earlier journeys published). It reads the server's records and asserts the screen against them:

| Step | Asserted |
|---|---|
| Where blocks are made | "New building block" says where each of the four kinds is made and lists the survey to make it in; nothing is created by it |
| Discover | the overview's counts open the views; every latest published module is a card; filters; search finds a module and a survey by name; a search with no match says so |
| Inspect | from the card of the richest published module: as many graph nodes and step rows as the published document has nodes; each step's exact wording; as many branch lines as the document has edges from that step; every ending |
| Understand | selecting a graph node selects its step; conditions in words; each consuming survey with its pinned version and how it is entered |
| History | as many revisions as published; as many dependency rows as documents pinned |
| Next action | "Use in a survey" opens the chosen survey with the library on that block and "Add to this survey" offered — and the survey's draft revision is unchanged by looking |
| Rules | the four families; in-effect assignment rules equal the policy's; a bound rule names its survey; obligations equal the published policies'; the inspector opens from a rule |
| Reader | sees and inspects everything; is offered no create, reuse or test action |
| Sizes | 1440, 1024 and 768 wide; no sideways overflow at 768 |

## 5. Evidence

`docs/acceptance/evidence/UX-HOME-1/`:

| Folder | Content |
|---|---|
| `before/` | the first page as it was, at 1920, 1440, 1024 and 768 wide (development server) |
| `after-development/` | the workspace, the inspector, the rules explorer and a search at the same four sizes (development server, development data) |
| `after/` | twelve screenshots from the browser journey (test schema: more surveys, modules with branches and endings, a reader, 1024 and 768) |

## 6. Limits and deviations, stated

| | |
|---|---|
| Search | done in the browser over lists loaded once. Right for today's volumes; a server search is needed at scale. Unpublished drafts of modules and questions are not searched — only published blocks are reusable; a draft is found inside its survey |
| "Frequently reused" | no usage data exists. Reuse is the number of surveys whose published versions pin a block, and nothing more |
| "Awaiting you" | exact for survey candidates (server rules). For control policies, mappings, bindings and requirement groups it is derived in the browser from status, proposer, approver and permission — the same facts their own screens show; the server still decides when the action is tried |
| Governance of a block | who published the survey version it came with is shown. Who submitted and approved is on the candidate, which is not read here |
| Testing a module | a module cannot be simulated alone; the entry point opens a survey that pins it |
| Follow-up and rule-ordered routing | drawn and described by the inspector (dashed lines, "Rule 1…", "Otherwise", "After the follow-ups"). The modules published in the browser test data use per-answer and "always next" routing, so these two forms are verified by a unit test of the inspector's reading (`Inspector.test.ts`), not by a browser assertion |
| Creating a block | happens in the existing composer and module builder; the panel opens the survey's composer, not the exact control. The wording of the steps describes those screens; it was not checked against every label in them |
| Finding rules | need the existing Finding Rules permission; the survey identities do not hold it and see an explanation |
| Rules explorer | lists published rules; survey-level entry conditions are shown in the inspector under each consuming survey, not as a separate list |
| Inspector as a dialog | closes with Escape and the close button, and takes focus when opened; focus is not trapped inside it |
| Approved HTML mockup | not compared screen by screen. The workspace uses Survey Studio's existing tokens, type and components; no generic dashboard template was introduced. It is an intentional redesign of the persisted first page, recorded here |
| Accessibility | keyboard-operable cards, tabs, graph nodes and drawer; visible focus; reduced motion respected. Not tested with a screen reader |
| Prototype Survey Studio | unchanged; this is the persisted mode's first page |

## 7. Regression

{{REGRESSION}}

## 8. State

{{STATE}}

## 9. Stopped here for UX review

Nothing further was started. I committed and pushed nothing.
