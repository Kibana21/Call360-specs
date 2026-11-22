# LIB-2 — Independent reusable building blocks: assessment, architecture decisions and contract

**Status: LIB-2 was ACCEPTED by the owner as technically verified on 2026-11-22 (D-344).** Authorisation: the owner's message of 2026-11-22,
"Accept UX-HOME-1 + NAV-1 and Implement LIB-2: Independent LEGO Building Block Authoring". Companion:
`50_LIB-2_IMPLEMENTATION_REPORT.md` (what was built and the evidence), contract `04_…` §22, decisions D-330…D-343.
**Synthetic data only.** Nothing here is approved business policy, and no module is eligible for a call.

---

## 1. What existed (assessment)

| Area | As it stood after LIB-1 |
|---|---|
| Identity | every option set, question, wording, condition and module version is a row of `survey_asset_version`, keyed `(kind, code, version)`, with `owner_definition_id` naming the **survey** whose draft wrote it. A code belongs to the survey that owns its versions (`CODE_OWNED_ELSEWHERE`); new codes are issued by the server to a survey (`survey_issued_code`) |
| Draft | one mutable `survey_draft` per survey: a content document (`sequence` of module placements) and the asset versions it owns. Saved atomically under an optimistic revision |
| Governance | `survey_candidate` (immutable submission: content, manifest of every pinned version, both fingerprinted) → `survey_version` (immutable publication). Status is derived from the append-only `survey_lifecycle_event`. A database trigger enforces the three-person rule whatever permissions a person holds: a maker cannot decide or publish; the approver cannot publish |
| Freezing | submitting freezes every asset version the content pins. A frozen version can never change (trigger); a change is a new version |
| Reuse (LIB-D-1, D-215) | an asset version is reusable across surveys **if and only if a published survey version pins it** (`published_index`). Drafts, rejected and unpublished candidates are never in the library |
| Pinning | a consumer's content names an exact `(code, revision)`; its manifest records the SHA-256. A newer revision is reported as information only (LIB-D-5) and never applied |
| Copy | "Edit a copy for this survey" derives a local revision under a code of the survey's own, with `derived_from` provenance |
| Execution | `execution.execute_inputs(bundle, facts, inputs)` — the one Python engine. It executes a **survey content**: a module's endings mean something only through the placement's `routes` |
| Simulation | only of a **published survey version**; recorded (`survey_simulation`) |

**Why a module could not be authored alone** (D-328): not a technical limit of the documents — a module document is
complete on its own — but three structural facts: (1) the only draft container is a survey; (2) the only thing that
goes through review is a survey candidate; (3) the engine needs a content around a module to say where its endings
lead.

## 2. The three decisions proposed with D-328, and what LIB-2 did with each

D-328 recorded the proposal but not the three decisions in full; they were put to the owner in conversation on
2026-11-22. They are recorded here in full, with their resolution.

| | Proposed decision | Resolution in LIB-2 |
|---|---|---|
| 1 | A building block is published **on its own** by the same three-person rule as a survey (maker, a different approver, a third publisher) | **Implemented, by reuse.** The owner's brief requires "Maker-checker-publisher separation" and "Reuse existing governance mechanisms". No new rule was written: the existing candidate lifecycle and its database trigger govern a standalone module unchanged |
| 2 | A standalone module must be **simulated before it can be published** | **NOT implemented as a rule — left open (P-2).** The brief requires a genuine test to exist; it does not say a test must precede submission, and no approved policy says so. Testing is available at every stage; submission requires what a survey's does (no blocker, warnings acknowledged). Making a test a precondition would be a new governance rule and was not invented |
| 3 | Blocks already written inside surveys **stay as they are** | **Held.** "Existing survey-extracted library components must continue working unchanged." No existing asset, candidate, version, manifest or fingerprint is touched; a survey-owned module is not converted, re-owned or re-coded |

## 3. Options considered

| | Option | Assessment |
|---|---|---|
| A | **A standalone module is a definition of kind `MODULE`** in the existing `survey_definition` table, with the existing draft, candidate, version and lifecycle rows | **Chosen.** One governance, one library, one document format, one save path. One additive column. The existing reuse rule works unchanged: the module's own publication record pins the module, so `published_index` already lists it. Cost: everything that treats a published version as a *survey* must refuse a module's — done in one place in the application (`store.version` defaults to surveys) and by a database trigger |
| B | New tables: `module_draft`, `module_candidate`, `module_version`, `module_lifecycle_event` | Rejected. A second lifecycle with a second copy of the identity trigger, a second review screen and a second library index — the "second registry" the brief forbids, and two governance mechanisms to keep equal for ever |
| C | A hidden survey created behind the scenes for each module | Rejected. It is the "temporary survey" the brief rules out, it would appear in survey lists, counts, assignment and simulation, and it would be a fake published customer survey |
| D | No schema change: mark module containers by a code prefix | Rejected. No database guarantee; a survey could be named into the namespace; nothing could stop a simulation or binding at the database |

## 4. Architecture decisions (AD-L2-*)

- **AD-L2-1 — One definition table, two kinds.** `survey_definition.artifact_kind` is `SURVEY` (default; every
  existing row) or `MODULE`. It never changes (trigger). A `MODULE` definition's code **is** the module's code,
  issued by the server (`M-<n>`).
- **AD-L2-2 — The fixed frame.** A standalone module's draft content is exactly one placement of its own module:
  instance `module`, always entered, and **every ending of the module ends the run as itself**
  (`routes[o] = {survey_outcome: o}`). It carries no decision of an author. The server refuses any other content for
  a `MODULE` definition (`MODULE_FRAME_INVALID`): a second module, another module's code, an entry condition, a skip
  disposition, or a route an author chose. The frame is what the candidate freezes and the engine executes; it is not
  a survey and is never listed, simulated, planned, assigned, coordinated or evaluated as one.
- **AD-L2-3 — One governance.** Draft documents, atomic save, code issuing, validation, submission, candidates,
  decision, withdrawal, publication and history are the **existing operations, addressed by the module's id**. The
  identity rules, freezing, manifest verification, supersession and audit are the existing ones.
- **AD-L2-4 — LIB-D-1 is unchanged in mechanism and widened in reading.** "Reusable iff a published version pins it"
  still decides the library. The published version may now be a module's own publication record. A module's own
  record is **not counted as a survey that uses it** (`used_by` counts surveys only). *The owner's confirmation of
  this reading of D-215 is requested (P-7).*
- **AD-L2-5 — Never a survey.** `store.version()` returns survey versions unless both kinds are asked for; only the
  governance reads ask. The database refuses a `survey_simulation`, `survey_call_plan` or
  `survey_assignment_binding` row naming a `MODULE` definition (`survey_module_not_a_survey`).
- **AD-L2-6 — Testing is a replay, and records nothing.** `POST /survey-module-tests` gives the Python engine the
  frame of one module revision, the synthetic facts and the ordered answers, and returns the run. No row is written
  anywhere. The same request gives the same run and the same fingerprint. It tests a standalone module's working
  draft (or any of its revisions) and **any published module**, however it was authored. A module with a blocker is
  reported as not testable and is not executed.
- **AD-L2-7 — The schema behind the head still serves.** Every statement that reads the kind does so through
  `to_jsonb`, so it also runs on a schema without the column, where every definition is a survey. Development at
  `0035` is unaffected while the setting is off.
- **AD-L2-8 — The same editor.** The Module Builder is the existing guided builder and graph on the module's own
  draft. The editor keeps the frame (`keepFrame`) so what it saves is what the server requires; the name and
  description are the module document's own.

## 5. Lifecycle and authoring contract

| Step | What happens | By which operation |
|---|---|---|
| Create | a `MODULE` definition, its issued code, an empty draft revision 1 and the frame. No survey | `POST /survey-modules` (`survey.edit`) |
| Edit | questions, statements, answer sets, conditions, routing — the existing documents; new identities are issued by the server to the module | `…/survey-definitions/{id}/codes`, `…/draft/save` |
| Validate | the existing validator on the frame; findings by stable code | `…/draft/validate` |
| Test | the Python engine, nothing recorded | `POST /survey-module-tests` (`survey.simulate`) |
| Submit | blockers refuse; server-governed warnings acknowledged with a reason; everything pinned is frozen; an immutable candidate | `…/candidates` |
| Decide | a person who is not a maker approves or sends back | `/survey-candidates/{id}/decision` (`survey.approve`) |
| Publish | a third person publishes; the earlier publication is superseded and stays | `/survey-candidates/{id}/publish` (`survey.publish`) |
| Reuse | the revision is in the library; a survey pins `(code, revision)` and its manifest records the fingerprint | existing library and composer |
| Next revision | a copy one revision on, in the module's own draft; the frozen revision is untouched; consumers are told (information only) and not changed | editor, then save |

Dependencies: a standalone module may place questions, conditions and answer sets it writes itself, or published ones
from the library (the existing rule: its own, or published). An unpublished asset of another definition is refused at
save (`REFERENCE_NOT_PUBLISHED`), and a missing dependency is a validation blocker — publication is refused either way.

## 6. Migration assessment — `0036_survey_module_authoring`

| | |
|---|---|
| Why existing tables could not represent it | nothing distinguished a definition that is a survey from one that is not, so a module's container would have been a survey everywhere. One column is the minimum that makes the difference a database fact |
| What it adds | `survey_definition.artifact_kind varchar(8) NOT NULL DEFAULT 'SURVEY'` with a CHECK; a trigger that the kind never changes; one guard function and three INSERT triggers (simulation, call plan, assignment binding) |
| What it does not touch | no row is updated; no asset, candidate, version, manifest, fingerprint or lifecycle event changes. Every existing definition reads `SURVEY` |
| Populated schema | tested: with a published survey present, down to `0035` and up again leaves every governed row byte-identical (asset fingerprints, candidate and manifest fingerprints, versions, lifecycle events) |
| Destructive downgrade | refused while a standalone module exists ("standalone modules exist; downgrade would turn them into surveys") |
| Setting | `survey_module_authoring_enabled`, off by default; on only with the library. With it off no module route exists |
| Development | **NOT applied.** Development stays at `0035`. Applying it needs the owner's explicit authorisation |

## 7. Unresolved policy and identity questions — recorded, not invented

| | Question | What is in place meanwhile |
|---|---|---|
| P-1 | Who may **test** a module? | the existing rule: running the engine needs `survey.simulate`, which `survey.edit` does not imply. An author without it sees why. Whether module authors should hold it is a governance decision |
| P-2 | Must a module be tested before it is submitted or published? | no such rule. Testing is offered, not required |
| P-3 | Should publishing to the shared library need a **different authority** from publishing a survey? | the same three permissions and the same three-person rule cover both. No library-specific role exists |
| P-4 | Who **owns** a module? | nobody is recorded as owner. Makers, the approver and the publisher are recorded per candidate, as for a survey |
| P-5 | Can a published module revision be **withdrawn or deprecated**? | no — as for every published asset today. A newer revision supersedes; the older stays pinned where it is pinned |
| P-6 | May a module published for one market be reused in another? | no. A module belongs to one market (Singapore-only development); the library is market-scoped |
| P-7 | Is D-215 (LIB-D-1) amended to read "…referenced by a published survey version **or published on their own**"? | implemented as AD-L2-4; the owner's confirmation of the wording is requested |
| P-8 | Should a survey be notified, or required to act, when a module it pins is superseded? | information only (LIB-D-5), unchanged |

**Owner rulings of 2026-11-22 (D-345).** P-1 ruled — testing keeps needing `survey.simulate`, not granted to every
author. P-2 ruled — testing is available, not a prerequisite. P-3 — the existing permissions and three-person rule
continue; a separate library authority stays open. P-4 open. P-5 open; not to be invented. P-6 ruled — cross-market
reuse is prohibited. P-7 ruled — "An asset is reusable when its exact revision is pinned by a published survey
version or published independently through the governed module lifecycle." P-8 ruled — a superseded revision stays
pinned; newer revisions are informational and never applied automatically. The implementation already matched each.

## 8. Questions, conditions and answer sets — staged extension

The brief allows prioritising modules when the other kinds "would require substantial new lifecycle architecture".
They would: each needs its own container kind, its own frame or none (an answer set and a condition do not execute
on their own; a question needs a one-question module to be tested), its own validation scope and its own review
content. What LIB-2 delivers instead, without a redirect that pretends:

- A question, a condition and an answer set are written **inside a module** — and a module no longer needs a survey.
  Published with the module, each is in the library as a reusable block of its own kind, owned by the module.
- The workspace says exactly that. Its buttons for those kinds read "How questions are made" (not "New question"),
  and the panel offers "Create a module".

**Proposed LIB-3** (not authorised): definitions of kind `ITEM`, `CONDITION`, `OPTION_SET` on the same column and the
same governance; a condition tester (the existing `survey-conditions/evaluate`); a one-question frame for testing a
question. Decisions needed: whether a question may be published without any module using it; whether an answer set
is reviewed on its own or only with a question.

## 9. Constraints kept

No second registry, document format, branching model, engine or lifecycle. No JavaScript execution. No published
asset modified in place. No rule, evaluation, finding or assignment semantics changed. Script Studio untouched. No
callback, voice or Genesys work. No golden fixture or expectation changed.
