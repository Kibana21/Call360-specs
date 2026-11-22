# FI-2 — Real review and publication in Survey Studio: implementation report

**Checkpoint:** FI-2, authorised by the owner on 2026-11-22 ("FI-1 Review, Closure Correction and FI-2
Authorization"), decision register D-207…D-212.
**Status: ACCEPTED 2026-11-22 as TECHNICALLY VERIFIED — REAL REVIEW AND PUBLICATION (owner decision D-213).** The
warning code, the mandatory acknowledgement, the two read operations and the change to submission behaviour are
accepted. Recorded limitation (D-214): the checker sees frozen content as a table; a read-only Graph and a more
intuitive visual comparison are for future business UX acceptance. Not production readiness, business UX acceptance,
screen-reader sign-off or Compliance approval of any wording.
**Prepared:** 2026-11-22.

**Scope held.** SS-03B was not started. No live-call execution, no server call-plan assembly, no no-answer or
consent behaviour. Script Studio was not modified or removed. The development database was not reset or re-seeded.
No cross-survey shared-library reuse. No permission was granted to any existing role. No other authoring
application. **FI-2 is uncommitted** (the commit authorisation covered FI-1 only) **and nothing was pushed.**

**Not claimed.** Not production readiness; not business-user UX acceptance; not screen-reader sign-off; **not
Compliance approval of any wording.** No survey is eligible for a live call.

FI-1 closure evidence is in `29_FI-1_IMPLEMENTATION_REPORT.md` §12.

---

## 1. What each person can now do

Everything below runs on the real candidates and versions of the SS-03A backend. Nothing is simulated.

### Author (`survey.read`, `survey.edit`)

| Capability | How it works |
|---|---|
| Edit a persisted survey | As FI-1 |
| Validate the exact saved revision on the server | The Review step shows the server's verdict on the saved revision; unsaved changes are stated as not part of it |
| Resolve authoritative blockers | Listed with the server's codes; Submit stays disabled while any remains |
| Acknowledge server-governed warnings with reasons | One reason per warning, at least 10 characters; recorded with the candidate |
| Submit an immutable candidate | "Submit for review" freezes the saved revision as C-n |
| Continue editing without altering the candidate | The versions the candidate pins become frozen; the editor then requires "Edit a copy" of the module and "Create a new version" of the question — its existing controls. The candidate is never reachable from the draft |
| View submission and candidate history | Candidates and versions tables; each candidate's own timeline |

### Checker (`survey.read`, `survey.approve`)

| Capability | How it works |
|---|---|
| Open a frozen candidate | From the survey's Review step |
| Inspect pinned modules, questions, wording, conditions, routes and content hashes | "Frozen content": every module in order, each step with its item, wording text, answers, routes, and the fingerprint of each pinned version with whether it still matches |
| Review the changes and validation results | "What changed" against the previous published version; the server's validation of exactly this content; the acknowledged warnings with their reasons |
| Approve or reject with an audited decision | Approve; or Send back, which requires a comment. Both are lifecycle events and audit events |
| Be prevented from approving a candidate they made | Shown before they try, and refused by the server and the database |
| Never change candidate content | The candidate screens contain no editing control. A test counts the inputs inside the frozen content: zero |

### Publisher (`survey.read`, `survey.publish`)

| Capability | How it works |
|---|---|
| Open an approved candidate | Same screen |
| Reverify its immutable manifest | The server verifies on reading (shown as "Integrity") and again inside the publish operation |
| Publish through the actual backend | "Publish as an immutable version" |
| Create an immutable Survey Version | Version 1.0, 2.0, … |
| Show version history and published content | Versions table; a version page with the frozen content |
| Independent permission and identity restrictions | `survey.publish` is separate from `survey.approve`; a maker and the approver are refused |

The three development identities were used unchanged; each holds only its own part.

---

## 2. Backend additions

The lifecycle, identity rules, immutability and manifest verification are SS-03A's, unchanged. FI-2 adds:

| Addition | Why it was needed |
|---|---|
| Server-governed warnings and required acknowledgements at submission (`04_…` §11.1) | Owner decision FI2-D-1 |
| `GET /survey-definitions/{id}/history` | There was no way to list a survey's candidates or versions |
| `GET /survey-candidates/{id}/documents` | The candidate read returned only the manifest (codes and hashes), not the documents a checker must inspect; nor the makers by name, nor what the identity rules allow the reader |

**No migration**: the candidate row already had `makers` and `acknowledgements`.
**OpenAPI** (against the accepted FI-1 contract `d808d92`): operations 216 → 218, 2 added, 0 removed, 0 changed;
schemas 431 → 440, 9 added, 0 removed, 0 changed. SHA-256 `5a31269b…` → `5b81d44f…`.

### One behaviour change to an existing operation

`POST …/candidates` now **refuses a draft whose server warnings are not acknowledged**. Before FI-2 it accepted any
acknowledgement list, including none. This is FI2-D-1 as decided, but it is a change in behaviour: every existing
test that submits a candidate was updated to acknowledge, and a script written against the SS-03A behaviour would
now get `ACKNOWLEDGEMENT_REQUIRED`.

### The one warning code — needs the owner's acceptance

`SYNTHETIC_WORDING_UNAPPROVED`, raised whenever a survey pins any wording. FI2-D-1 asked for the mechanism; a
mechanism with no warning cannot be demonstrated or used. I chose the one warning that restates an existing owner
decision (D-183: all wording is synthetic and unapproved) and that the "Wording governance" section of the
authorisation asks to keep visible. It introduces no new business rule. **If the owner would rather the server raise
no warning yet, removing it is one function**; the mechanism stays.

---

## 3. Wording governance

- Every review screen carries the same statement: all wording is synthetic sample text; reviewing, approving or
  publishing a candidate is a development step, not Compliance approval of insurance wording, and makes nothing
  eligible for a live call.
- The frozen-content table heads its wording column "synthetic · unapproved".
- Each submission records the submitter's acknowledgement of exactly that, with their reason, against the
  candidate's fingerprint.
- Approval still writes SS-03A's append-only wording-review evidence. It records that the wording was reviewed in
  that candidate; it does not mark any wording approved for operational use.
- No Wording Studio was introduced: wording is edited where it always was, on the question.

---

## 4. The ten demonstrations

| # | Demonstration | Result | Evidence |
|--:|---|---|---|
| 1 | Author submits C-1 | Pass | Journey FI-2.1 · `FJ01`, `FJ02` |
| 2 | Checker approves C-1 | Pass | FI-2.1 · `FJ03`, `FJ04` |
| 3 | Publisher creates Version 1.0 | Pass | FI-2.1 · `FJ05`, `FJ06`, `FJ07` |
| 4 | The author's later edits do not change C-1 or Version 1.0 | Pass: content, every pinned document, fingerprints and acknowledgements identical; the version page still shows the original wording | FI-2.1 · `FJ08`; backend |
| 5 | A changed draft produces C-2 and cannot inherit C-1's approval | Pass: C-2 is in review with no approver and its own fingerprint; publishing it is refused `NOT_APPROVED` | FI-2.1 · `FJ09`, `FJ10`; backend |
| 6 | Self-review, self-publication and approver-publication denied | Pass, by a person holding **all four** permissions: `SELF_REVIEW_DENIED`, `SELF_PUBLISH_DENIED`, `APPROVER_PUBLISH_DENIED` | FI-2.2 · `FJ13`–`FJ15`; backend |
| 7 | An unauthorised user cannot review or publish | Pass: a reader and an ordinary user get 403 on decision, publish and withdraw; the ordinary user cannot open the screen | FI-2.2 · `FJ16`; backend |
| 8 | Manifest tampering detected and refused | Pass: a candidate written around the application shows "does not match", cannot be approved (`MANIFEST_MISMATCH`, audited), and nothing is published from it | FI-2.3 · `FJ17`; backend |
| 9 | Candidate status and history persist across browser restarts | Pass: new browser contexts read the same statuses, timeline and versions from the server | FI-2.1 · `FJ11` |
| 10 | Existing FI-1 saving and conflict behaviour intact | Pass: the six FI-1 journeys, unchanged apart from two assertions about the Review step | Persisted suite |

Also shown: a submission without the acknowledgement is refused by the server itself (`ACKNOWLEDGEMENT_REQUIRED`); a
checker cannot edit the draft and has no publish control; a publisher has no approve control; sending back requires
a reason, which is recorded (`FJ12`).

### Regression results

| Suite | Result |
|---|---|
| Backend (isolated test database) | 674 passed, 0 failed (668 + 6 new) |
| Backend lint, format, strict types, contract check | Clean |
| Frontend unit tests | 505 passed |
| Frontend type check, lint, client drift check | Clean |
| Full-stack persisted journeys | 9 of 9 (6 FI-1, 3 FI-2) |
| Prototype journeys (prototype setting on) | 13 of 13 |
| Standard Playwright (both settings off) | 33 of 33 |
| Golden fixtures; canonical documents | Unchanged; current |
| Specs validator | PASS |

Evidence: `docs/acceptance/evidence/FI-2/`.

---

## 5. Walkthrough on the development database

With `dev.survey.author`, `dev.survey.checker` and `dev.survey.publisher` on the running development servers.

| Step | Observed |
|---|---|
| Author creates "FI-2 development walkthrough (synthetic)" (`S-DEV-FI2-WALKTHROUGH`), saves, acknowledges, submits | C-1, in review; the author is told they are a maker; they have no approve or publish control |
| Checker opens C-1 | Integrity verified; maker shown as Dev Survey Author; the draft is read-only to them; no publish control. Approves |
| Publisher opens C-1 | No approve control; Publish enabled. Publishes **Version 1.0** |
| Server afterwards | C-1 `PUBLISHED`; Version 1.0 `PUBLISHED`; manifest intact, 4 pinned versions all matching; the acknowledgement carries the candidate's fingerprint; audit chain verifies |

**This wrote to the development database**: one new survey, one candidate, one version, their events and audit
rows. They are synthetic, labelled, and — being frozen — permanent by design. The earlier check survey
`DEV-CHECK-AD5AEA8F` is untouched (revision 10, 2 candidates, 1 version, as before). No table was removed; no
existing role holds a survey permission. Screens `DEVF01`–`DEVF07`; evidence `dev_database_walkthrough.txt`.

---

## 6. Things the owner should know

1. **`SYNTHETIC_WORDING_UNAPPROVED` is my choice of first server warning** (§2). It needs acceptance.
2. **Submission behaviour changed** for anything that submitted without acknowledgements (§2).
3. **Two read operations were added.** "Using the existing SS-03A backend" could not show a checker the documents
   or list a survey's candidates. Both are read-only and additive.
4. **Editor-only warnings are now advisory in a saved survey**, per FI2-D-1: they show "Advisory · editor only" and
   can no longer be "acknowledged" there, because that acknowledgement was a simulation.
5. **"What changed" compares documents, not text within them.** It names each new or dropped version and quotes
   new wording. It does not show a word-level difference.
6. **The frozen content is a table, not the Guided or Graph view.** A checker reads every step, wording, answer,
   route and fingerprint, but does not see the module as a graph. Reusing the Graph read-only is possible later.
7. **The identity rules are shown before they bite.** Buttons are disabled with the server's reason. The server is
   still the authority: the journeys also call it directly and get the same refusals.
8. **Makers accumulate** (D-209, retained). In the two-author case both are makers and neither can approve.
9. **The review screens have no unit tests of their own.** They are covered by the three full-stack journeys and
   the backend tests.
10. **The test server's sign-in limit was raised** for the persisted journeys only (they sign nine different people
    in within a minute). The product's limit is unchanged.
11. **Two synthetic surveys now exist in the development database**, each with a published version.
12. **A newer open candidate supersedes an older open one** (SS-03A behaviour). After C-2 is submitted, an
    unpublished C-1 could no longer be approved.

---

## 7. Proposed next boundary: reusable published modules ("LIB-1")

**Not authorised.** FI2-D-2 defers shared-module discovery and cross-survey reuse to a dedicated checkpoint;
FI2-D-4 asks for server-issued codes before operational reuse.

**Goal.** An author composing a survey can find a module that another survey has published and place it, pinned to
that exact immutable revision, and can later make their own copy without affecting anyone else.

| In | Out |
|---|---|
| A library read: published (frozen) module revisions across surveys in the reader's markets, with their documents, the versions that pin them, and who published them | Execution, call-plan assembly (SS-03B) |
| "Add from library" in the Lego Composer: pins `{code, revision}`; the module shows as shared and locked, as the prototype already draws it | Any non-answer behaviour; live eligibility |
| Copy-on-write, already in the editor: "Edit a copy for this survey" derives a new draft revision owned by this survey; the shared revision is untouched | Editing a shared revision in place — never |
| Usage: "used by N surveys / versions" from the existing derived index | A separate library application |
| **Server-issued codes** for new modules, questions, conditions and option sets, replacing the editor's per-survey number range | Renaming or renumbering any existing code, and any change to fixture identities |
| "A newer revision of this module is published" as a second **server** warning with its own code | Automatic upgrade of a pinned revision — never |

**Decisions needed first**

| ID | Decision |
|---|---|
| LIB-D-1 | Which published revisions are discoverable: every frozen module, or only those in a published version |
| LIB-D-2 | Whether items and conditions are reusable on their own, or only as part of a module in this checkpoint |
| LIB-D-3 | The form of server-issued codes, and whether codes created so far keep theirs (recommended: yes, untouched) |
| LIB-D-4 | Whether placing a module published by someone else makes its makers "makers" of the new survey (recommended: no — a pinned frozen revision was already reviewed) |
| LIB-D-5 | Whether a superseded-revision warning must be acknowledged at submission |

---

## 8. Changed-file inventory

### Call360-backend (base `d808d92`; uncommitted)

| File | Change |
|---|---|
| `app/domain/survey/store.py` (+205 −3) | Governed warnings; acknowledgement check and recording; `restrictions`; `candidate_documents`; `survey_history` |
| `app/api/survey_definitions.py` (+153 −2) | Two read operations and their nine models |
| `contracts/generated/openapi.json`, `openapi.sha256` | Regenerated |
| `scripts/e2e_survey_setup.py` (+5) | Test-schema checker, publisher and all-permissions people |
| **New** `scripts/e2e_forge_candidate.py` | Test-schema-only tampered candidate |
| **New** `tests/test_survey_fi2.py` | 6 tests |
| `tests/survey_support.py`, `test_survey_store.py`, `test_survey_api.py`, `test_survey_fi1.py` | Submissions acknowledge the server's warnings; counts for nineteen operations |

### Call360-frontend (base `63966a9`; uncommitted)

| File | Change |
|---|---|
| **New** `src/features/surveystudio/persist/ReviewPages.tsx` (363 lines) | Review step, candidate page, version page, frozen content, changes |
| **New** `src/features/surveystudio/persist/reviewApi.ts` | Generated-client calls and the wording of the server's reason codes |
| **New** `e2e/persisted/fi2.persisted.ts` | Three full-stack journeys |
| `persist/PersistedStudioRoot.tsx` (+7 −24) | Routes for review, candidate, version; the "not available yet" page removed |
| `persist/Persistence.tsx` (+14 −2) | Re-read the draft after a submission, so frozen versions are locked in the editor |
| `JourneyNav.tsx` (+2 −2), `ValidationPage.tsx` (+5 −4), `StudioRoot.tsx` (+1 −1) | Persisted-mode wording: the server decides; editor warnings are advisory; link to Review |
| `src/styles/survey-studio.css` (+21) | Review screens |
| `e2e/persisted/fi1.persisted.ts` (+4 −4) | Two assertions about the Review step, which is now real |
| `playwright.persisted.config.ts` (+3 −1) | Sign-in limit for the test server |
| `src/api/generated/schema.d.ts`, `openapi.pinned.json`, `contract.lock.json` | Regenerated client |

Not changed: the Lego Composer, Guided Builder, Graph, Simulator and Call plan; every Script Studio file;
`src/styles/app.css`; the in-memory prototype and its journeys.

### Call360-specs (base `f610365`; uncommitted)

`04_…` §11 · `30_…` (this report) · `README.md` · `SESSION_HANDOFF.md` · **new**
`docs/acceptance/evidence/FI-2/` (4 files, 24 screens).

---

## 9. Commit state

| Repository | On origin | Local commits not pushed | Uncommitted |
|---|---|---|---|
| Call360-backend | `d808d92` (FI-1) | none | FI-2 |
| Call360-frontend | `7141926` (FI-1) | `63966a9` FI-1 closure correction | FI-2 |
| Call360-specs | `fa01cda` (FI-1) | `f610365` FI-1 acceptance record | FI-2 record |
