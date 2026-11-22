# LIB-1 — Reusable component library: implementation report (LIB-1A and LIB-1B)

**Checkpoint:** LIB-1, authorised by the owner on 2026-11-22 ("Accept FI-2 and Authorize LIB-1"), decision register
D-213…D-221.
**Status: BUILT AND TECHNICALLY VERIFIED — presented for the owner's review. Not accepted.**
**Prepared:** 2026-11-22.

**Scope held.** SS-03B was not started. No server-side execution or call-plan assembly. No non-answer, refusal,
retry, consent or voice policy; no real-call eligibility; no Genesys, GPT Live or telephony. Script Studio was not
modified or retired. No pin is ever upgraded automatically. No separate library application, second authoring model
or parallel definition store. No historical asset identity was rewritten. **The development database was not
migrated or re-seeded. LIB-1 is uncommitted and nothing was pushed.**

**Not claimed.** Not production readiness; not business-user UX acceptance; not screen-reader sign-off; not
Compliance approval of any wording. No survey is eligible for a live call.

FI-2 was accepted as TECHNICALLY VERIFIED — REAL REVIEW AND PUBLICATION (D-213), with the limitation recorded as
D-214.

---

## 1. What an author can now do

Inside the existing Survey Studio, on every screen, the bar has **Add from library**. It opens one drawer over the
screen the author is on.

| | |
|---|---|
| One selector, four kinds | Tabs: Modules · Questions · Conditions · Answer sets. Same search, list, preview and actions for each |
| Find | Search by name, description, code, or the survey that published it. Each row shows the category, the revision and whether it is the latest, who published it and how many surveys use it |
| Preview before choosing | Everything in the component, in words and one table (§2) |
| **Add to this survey** | The exact published revision, pinned. Shown as shared and locked. Nothing is copied |
| **Edit a copy for this survey** | A local draft the author can change, with its own identity and a record of its source |
| Know about newer revisions | A notice under the bar; "See what changed" opens the comparison. Nothing is upgraded |

No accepted screen was changed. The Lego Composer, Guided Builder and Graph are untouched; the library is reached
from the shared bar, so it is the same in all three. On a module's screen it opens on Questions; elsewhere on
Modules. Escape closes it and focus returns to the button that opened it.

---

## 2. LIB-1A — published module reuse

### Discovery and preview

Only what a **published** survey version pins is listed, in the reader's market. That is decided by the server
(§5), never by the screen.

The module preview shows, as asked:

| Asked for | Shown |
|---|---|
| Purpose and description | The module's name and its stated intent |
| Questions and statements | Every step, with the exact wording, headed "synthetic · unapproved" |
| Answer types and option sets | Per step |
| Conditions and decision points | Decision steps with the condition's name; the conditions it uses |
| Routing and possible outcomes | Where each step leads; the ways the module can end |
| Required inputs and dependencies | The customer or policy information its conditions read |
| Published version and fingerprint | Revision, "latest" or "a newer one is published", the server's SHA-256 |
| Which survey published it; historical revisions | "Published by …"; the list of published revisions |

Only what the documents themselves say is shown. **Filtering by category, purpose and version is by the search box
and the row text**; there are no separate filter controls, and no catalog value or status was invented.

### Add from library

The module's exact revision is referenced; its pinned questions, wording, conditions and answer sets come with it by
the same identities. The journey checks the request that is sent: **one `SET_CONTENT`** — the survey's content.
Nothing of the shared module is sent, copied or rewritten. The author still sets when the module runs (activation,
eligibility) and where each outcome leads.

**Compatibility.** A placement is refused, with the reason in words, when something the module depends on is not
published, or when it reads customer information the survey does not have. The server checks again on saving
(`REFERENCE_NOT_PUBLISHED`) and in validation (the existing condition and routing codes).

### Copy-on-write

"Edit a copy for this survey" derives a local draft module. On saving it receives a **new server-issued code**,
starts at revision 1, and records `derived_from {code, version}`. Changing one of its questions does the same for
that question. The published original, and every survey pinned to it, are verified unchanged.

### Usage and versions

From the existing derived usage index: the number of surveys and of published versions that pin the exact revision.
The pinned revision, whether a newer one is published, and "What differs from this one" — step by step, quoting
both wordings.

---

## 3. LIB-1B — questions, conditions and answer sets on their own

| Kind | Reuse | Change |
|---|---|---|
| Question | "Add to this survey" brings the exact published question and wording in, locked. It is then placed with the editor's own "Reuse a question from the library" control, in Guided or Graph | The editor's existing "Create a new version" / "Make a separate question" on the placed question; saved under a server-issued code with its source recorded |
| Condition | "Add to this survey"; it is then offered wherever a rule is chosen. Each place supplies its own values | The rule drawer's existing "new version" / "copy" |
| Answer set | "Use these answers" for a chosen draft question: the question then refers to the published set | Changing an answer afterwards gives the question its own set; the published set is never changed |

Preserved exactly, because nothing is copied: intent, answer type, option-set reference, wording version, delivery
mode, validation rules, option codes, labels, order, exclusive and "other" options, and the immutable identity and
version. A condition preview shows its parameters with their types, the earlier answers and the facts it reads, and
its three results — met, not met, **unknown**.

**Evaluation and control metadata** are not part of the canonical documents today, so there is nothing of that kind
to preserve or show.

---

## 4. Server-issued identity

| Requirement | How |
|---|---|
| The backend is the authority | With the library on, a new module, question, condition or answer set can only be saved under a code the server issued to that survey for that kind (`CODE_NOT_ISSUED` otherwise) |
| Concurrency-safe | One database sequence. Eight threads asking at once received 48 codes, all different |
| A failed operation leaves no reusable identity | A rolled-back request's numbers are never issued again (tested); every issued code is recorded under a primary key, insert-only |
| Historical codes untouched | The rule concerns only codes that do not exist yet. A number whose code an asset already carries is skipped |
| Existing references valid | No existing row is changed by the migration or by any LIB-1 code path |
| Temporary identities never become permanent | Before a Save, the editor replaces every code it numbered itself with the issued one, everywhere it is referred to. The journey asserts every saved asset code matches the server's form and none contains the editor's `-NEW-` |
| Existing conventions | `M-`, `Q-`, `S-` (statement), `C-`, `OS-`, then a number |
| Fixtures | The 27 golden fixtures, their 82 runs and the canonical export are unchanged |

A code also **belongs** to the survey that owns its versions: another survey cannot add a version to it
(`CODE_OWNED_ELSEWHERE`). That is why a copy of someone else's module needs a code of its own.

---

## 5. Security, governance and integrity

| Rule | Enforced where | Evidence |
|---|---|---|
| Published-source eligibility | Server: the library lists only what a published version's manifest pins; a draft, in-review, rejected or never-published asset is absent and 404 by its exact address | Backend; journey LIB-1.1, 1.5 |
| Market-scoped discovery | Server: a person of another market sees an empty library | Backend; LIB-1.5 |
| A draft cannot acquire a reference to another survey's unpublished asset | Server, on both save operations, and again in validation and at submission | Backend: a draft, a candidate in review and a rejected one are each refused, for a module and for a single question; LIB-1.5 by direct request |
| Immutable pinning | A pin is `{code, version}`; a frozen version cannot be changed; another survey cannot add a version | Backend; LIB-1.1 |
| Manifest verification | Unchanged; the consuming survey's candidate verifies against the same fingerprints | Backend; LIB-1.1 |
| Maker, checker, publisher separation | Unchanged | Backend; LIB-1.1 publishes A and B with three people each |
| Maker provenance (LIB-D-4) | The consuming survey's makers are its own author only; the source's author is not a maker and may review it | Backend; LIB-1.1, 1.3 |
| Audit | Saves, code issuing (`SURVEY.CODES_ISSUED`), submissions, approvals and publications | Backend |
| No way round by direct request | The single-operation endpoint applies the same rules | Backend; LIB-1.5 |

**The reference rule is on whether or not the library is.** That closes a gap that existed since SS-03A: a draft
could name another survey's draft asset by its code and the server resolved it.

---

## 6. The sixteen verifications

| # | Verification | Result | Where |
|--:|---|---|---|
| 1 | Survey A publishes a module through the real workflow | Pass | Journey LIB-1.1 |
| 2 | Survey B discovers it in the library | Pass | LIB-1.1 |
| 3 | Survey B adds it and pins the exact revision | Pass: same code, revision and server fingerprint; not owned; frozen | LIB-1.1; backend |
| 4 | Both surveys reference the same source revision | Pass: the two candidates' manifest entries are identical | LIB-1.1; backend |
| 5 | A newer source revision does not alter Survey B | Pass: draft, pin and published version identical; information only | LIB-1.2; backend |
| 6 | Survey B derives an editable copy without modifying the source | Pass | LIB-1.3; backend |
| 7 | Individual questions discovered and reused | Pass | LIB-1.4; backend |
| 8 | Conditions reused with validated bindings | Pass; a missing value is refused by the server with `CONDITION_PARAM_MISSING` | LIB-1.4; backend |
| 9 | Option sets independently reused | Pass | LIB-1.4; backend |
| 10 | Concurrent creation gives unique identities | Pass | Backend |
| 11 | Existing codes and golden fixtures unchanged | Pass | Backend; fixture export check |
| 12 | Usage indexes and manifests accurate | Pass: 2 surveys, 2 versions; index rows match | LIB-1.1; backend |
| 13 | Maker provenance correct | Pass | LIB-1.1, 1.3; backend |
| 14 | Unauthorised and cross-market access denied | Pass | LIB-1.5; backend |
| 15 | Direct API reference to an unpublished foreign asset refused | Pass | LIB-1.5; backend |
| 16 | FI-1, FI-2, prototype and standard suites pass | Pass | Below |

### Regression results

| Suite | Result |
|---|---|
| Backend (isolated test database) | 688 passed, 0 failed (674 + 14 new) |
| Backend lint, format, strict types, contract check | Clean |
| Frontend unit tests | 513 passed (505 + 8 new) |
| Frontend type check, lint, client drift check | Clean |
| Full-stack persisted journeys | 14 of 14 (6 FI-1, 3 FI-2, 5 LIB-1) |
| Prototype journeys | 13 of 13 |
| Standard Playwright (all settings off) | 33 of 33 |
| Golden fixtures; canonical documents; 27-fixture round trip | Unchanged; current; 88 of 88 |
| Specs validator | PASS |

**The FI-1 and FI-2 journeys now run with the library on**, so their surveys are saved under server-issued codes.
They pass unchanged.

Evidence: `docs/acceptance/evidence/LIB-1/`. Screens: `LB02` discovery · `LB03` search · `LB04` preview · `LB05`
added · `LB06` shared module in the Composer · `LB07` locked · `LB08` usage · `LB09` newer-revision notice · `LB10`
comparison · `LB11`, `LB12` copy-on-write · `LB13`–`LB16` question, answer set, condition and binding.

---

## 7. API and contract changes

Full text: `04_SS-01_CANONICAL_CONTRACTS.md` §12.

| Change | Kind |
|---|---|
| `GET /survey-components` · `GET /survey-components/{kind}/{code}/{version}` | Two new read operations, `survey.read` |
| `POST /survey-definitions/{id}/codes` | New operation, `survey.edit` |
| Server setting `survey_library_enabled` (off by default) | Registers the three operations and enforces issued codes |
| Refusals `REFERENCE_NOT_PUBLISHED`, `CODE_OWNED_ELSEWHERE`, `CODE_NOT_ISSUED` | New, on saving |
| Finding `NEWER_REVISION_PUBLISHED` (INFO) | New, in validation |
| `authoring` accepted on OPTION_SET; `derived_from` key | Optional, no execution meaning |

**OpenAPI** (against the accepted FI-2 contract `29fec70`): operations 218 → 221, 3 added, 0 removed, 0 changed;
schemas 440 → 451, 11 added, 0 removed, 0 changed. SHA-256 `5b81d44f…` → `88baaf2c…`.

**Behaviour changes to existing operations**, both on saving a draft:

1. A reference to another survey's unpublished asset is refused (previously resolved). Always on.
2. Adding a version to a code another survey owns is refused (previously accepted). Always on.

Neither affects anything a survey could legitimately have done; no existing test needed changing for them.

---

## 8. Migration

`0028_survey_library`: one sequence and one insert-only table. Nothing existing is altered.

| Step, isolated test database | Result |
|---|---|
| Upgrade `0027` → `0028` | Sequence and table created |
| Downgrade `0028` → `0027` | Both removed; every other table exactly as it was |
| Upgrade again | Identical |
| Downgrade while an issued code is recorded | Refused: "server-issued survey codes exist" |
| The project's round-trip test over every revision | Passes |

**The development database is still at `0027`** and was not touched: same 111 tables, survey tables identical to
the FI-2 report. The development server stays ready because the library setting is off there, and a schema at
`0027` is accepted in exactly that case. **So the library cannot be used in development until the owner approves
migrating it** and the setting is turned on. Until then development behaves as after FI-2, with one difference: the
reference rule of §5 applies.

One test-support change: the test-schema reset now also drops sequences (this is the first revision with one that
no table owns).

---

## 9. Known limitations

1. **No separate filter controls.** Category, purpose and version are found through search and shown on each row.
2. **A question, condition or answer set is "brought in", then placed with the editor's existing controls.** The
   module is the only kind placed straight from the drawer. This kept the accepted screens unchanged; a direct
   "insert here" from the drawer would need the Guided and Graph insertion points to open it.
3. **A component brought in but not placed is forgotten on reload.** It is not the survey's until something pins it.
4. **"Used by" counts published versions**, from the usage index. Drafts that pin a component are not counted.
5. **The comparison is in sentences**, step by step. It is not a visual diff, and for a question, condition or
   answer set it says only that the settings differ, plus the wording.
6. **A condition's rule is shown in its stored form** in the preview, not as the sentence the rule drawer builds.
7. **Newer-revision notices cover pinned modules** in the editor. The server reports them for every kind, on Validate.
8. **Compatibility is checked for unpublished dependencies and unknown customer information.** Anything subtler is
   left to server validation after placing.
9. **Codes are numbers** (`Q-100123`). They are permanent and unique, not meaningful. The editor shows names.
10. **The library's own screens have no unit tests**; the pure functions do, and the drawer is covered by the five
    journeys.
11. **The existing `GET /survey-library/{kind}`** (SS-03A) still lists every frozen version by code and fingerprint,
    without content, for anyone with `survey.read`. It predates LIB-D-1 and is not used by the editor. It should be
    restricted or retired; I left it because removing an operation is not additive.

## 10. Unresolved business decisions

| | |
|---|---|
| Who may publish to the library | Today anything a published survey pins is reusable by every author in the market. Whether some components should be private to a survey or team is undecided |
| Withdrawal | Nothing withdraws a published version, so nothing can be removed from the library. What happens to surveys pinning a withdrawn component is undecided |
| Deprecation | "Do not use for new surveys" has no representation |
| Approval of shared components | A component is reviewed as part of the survey that first published it. Whether a shared component needs its own review is undecided |
| Evaluation and control metadata | Not in the canonical documents; so not reusable yet |
| Catalog of customer information | Synthetic and unapproved; a component may read only what the catalog has |
| All earlier open items | Non-answer behaviour, real wording approval, live-call eligibility — unchanged |

---

## 11. Proposed SS-03B boundary

**Not authorised.**

**Goal.** The server can execute a published survey version deterministically **in simulation**, and assemble the
call plan for one application, so that what the editor's own simulator shows is confirmed by the authoritative
engine.

| In | Out |
|---|---|
| A pure execution harness on the server for a **published version**: navigation, follow-up queues, ordered rules, decisions, statements, typed answers — specified by all 82 expected runs of the 27 fixtures | Any non-answer, refusal, repeat, consent or timeout behaviour |
| Wording rendering with controlled variables (the mechanism; no field allowlisted for speech) | Any field authorised for speech |
| Call-plan assembly from a version and a fact snapshot — specified by the 14 expected plans | Assignment of a survey to a case |
| Simulation runs recorded apart from operational evidence | Operational runs, voice, telephony, Genesys, GPT Live |
| A read API for a simulation run and a plan; Survey Studio's Simulator and Call plan show the server's result beside the editor's and flag any difference | Live-call eligibility as a decision |
| Parity proof: server results equal the fixtures' expectations, run for run | Changing any fixture |

**Decisions needed first:** D-NA-1, D-NA-9, D-NA-13, D-NA-14, D-NA-15 (how an unanswered or refused question ends
a simulated run — or that a simulated run simply stops there, as the editor does today); the outcome catalog; whether
a simulation may run on an unpublished candidate.

**Before it:** commit LIB-1; decide on migrating the development database to `0028` and turning the library on
there.

---

## 12. Changed-file inventory

### Call360-backend (base `29fec70`; uncommitted)

| File | Change |
|---|---|
| **New** `migrations/versions/0028_survey_library.py` | Sequence and issued-code table |
| `app/domain/survey/store.py` (+424 −10) | Published index; reference rule; identity rule; code issuing; newer-revision finding; component list and detail |
| `app/api/survey_definitions.py` (+164 −7) | `library_router` with three operations and eleven models; saves pass the issued-code rule; validation is survey-aware |
| `app/core/settings.py`, `app/main.py`, `app/domain/catalog.py`, `scripts/export_openapi.py` | The setting; head rule for three cases; router registration; revision registered |
| `app/domain/survey/documents.py` | `authoring` on OPTION_SET |
| `contracts/generated/openapi.json`, `openapi.sha256` | Regenerated |
| **New** `tests/test_survey_lib1.py` | 14 tests |
| **New** `scripts/e2e_publish_fixture.py` | Test-schema-only published source with conditions |
| `tests/support.py` | Reset drops sequences |
| `tests/test_survey_api.py`, `test_survey_store.py`, `test_admin_access.py` | Head name; counts; shared grant helper; head restored after a refusal test |

### Call360-frontend (base `7570972`; uncommitted)

| File | Change |
|---|---|
| **New** `src/features/surveystudio/model/library.ts`, `library.test.ts` | Bringing components in; issued-code replacement; 8 tests |
| **New** `src/features/surveystudio/persist/Library.tsx` | The drawer, the bar button, the newer-revision notice, the comparison |
| **New** `e2e/persisted/lib1.persisted.ts` | Five full-stack journeys |
| `model/types.ts` (+9), `model/documents.ts` (+18 −4) | `derivedFrom` provenance, through the one mapping |
| `persist/Persistence.tsx` (+79 −19), `saving.ts`, `api.ts`, `SaveControl.tsx`, `PersistedStudioRoot.tsx` | Library availability; issued codes before a save; published components held locally; a frozen version is never sent; button and notice in the bar |
| `src/styles/survey-studio.css` (+30) | Drawer |
| `playwright.persisted.config.ts` | Library setting on for the test server |
| `src/api/generated/schema.d.ts`, `openapi.pinned.json`, `contract.lock.json` | Regenerated client |

Not changed: `ComposerPage.tsx`, `BuilderPage.tsx`, `GraphView.tsx`, the Simulator, the Call plan, every Script
Studio file, `src/styles/app.css`, the in-memory prototype and its journeys.

### Call360-specs (base `e8920b0`; uncommitted)

`04_…` §11 status and §12 · `06_…` D-213…D-221 · `30_…` status · `31_…` (this report) · `README.md` ·
`SESSION_HANDOFF.md` · **new** `docs/acceptance/evidence/LIB-1/` (4 files, 17 screens).
