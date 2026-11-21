# FI-1 — Survey Studio on the persisted survey-definition API: implementation report

**Checkpoint:** FI-1, authorised by the owner on 2026-11-22 ("Accept SS-03A Enablement and Authorize FI-1"),
decision register D-195…D-203.
**Status: BUILT AND TECHNICALLY VERIFIED — presented for the owner's review. Not accepted.**
**Prepared:** 2026-11-22.

**Scope held.** FI-2 and SS-03B were not started. No survey execution, no server call-plan assembly. No non-answer,
refusal, consent, retry or voice policy. Script Studio was not changed or removed. The development database was not
migrated, reset or re-seeded, and its synthetic published survey was not written to. Synthetic data only.
**Nothing is committed and nothing was pushed.**

**Not claimed.** Not production readiness; not business-user UX acceptance; not screen-reader sign-off. No survey is
eligible for a live call. Review and publication on real candidates are not connected.

---

## 1. What an author can now do

With the persisted-mode setting on, a person who holds `survey.read` opens **Survey Studio** and works on surveys
that are saved in PostgreSQL:

| Capability | How |
|---|---|
| List existing surveys | Name, code, draft revision, latest published version, review status |
| Create a new survey | Name, purpose, permanent code |
| Open a saved survey | The draft is loaded with the server's hash of every document |
| Edit modules, questions, statements, conditions and routing | The accepted Lego Composer, Guided Builder and Graph, unchanged |
| Save to PostgreSQL | One explicit **Save**: one request, one new revision |
| Reload an existing draft | After a page reload or a browser restart: the same content, the same identities |
| See persisted revision information | "Saved · Revision 4 · 22 Nov, 04:17 · E2E Survey Author", always in the bar |

The Composer, Builder, Graph, Simulator, Call plan and Validation screens are the prototype's own components.
Nothing was redesigned. In a saved survey three things differ, each behind one condition in the shared code:

1. The bar shows the save state and the **Save** button where the prototype shows "Prototype · not saved".
2. The journey strip has no simulated "Acting as" people, and its last step says review is not available yet.
3. Validation shows the **server's** result first, and labels the browser's own checks as not authoritative.

---

## 2. One canonical model

`Call360-frontend/src/features/surveystudio/model/documents.ts` is the only mapping between the editor's Workspace
and the six canonical document kinds. There is no second question model and no alternative backend representation:
the Workspace is the editing shape of exactly those documents. Its rules are in `04_…` §10.4.

### Proof on all 27 golden fixtures

The 27 fixtures were exported **by the backend** as canonical documents with the server's SHA-256
(`docs/plans/survey-studio/canonical-documents/`; a backend test keeps them current). The golden fixtures
themselves were not touched.

| Property, for each of the 27 fixtures | Result |
|---|---|
| Documents → Workspace → documents is exact: every document equals the one the server hashed | 27 of 27 |
| Opening and saving without an edit sends nothing | 27 of 27 |
| Workspace → documents → Workspace is exact | 27 of 27 |
| Node, edge, instance and execution identities (`<instance>/<node>`) are unchanged | 27 of 27 |
| The same simulated journey runs identically before and after | 27 of 27 |

Also proved: every survey of the prototype's sample library converts, and converting again changes nothing; what an
author types that had no field (module intent, kind, parameter labels) survives; a frozen version is never in a Save;
a draft the editor cannot represent is **refused, not opened**.

**Server hashes are authoritative.** The frontend computes no hash. It keeps the server's hash of every loaded
document, compares documents by content, and the journey asserts the hashes are identical after a restart.

---

## 3. Reliable saving

### Investigation (owner decision D-197)

The SS-03A API applied **one operation per request**. A Save of one edited question touches four documents, so it
needed several requests, and a failure between them left a partly saved survey. It could not be made safe from the
client without compensation logic, which was ruled out. **The smallest additive change was made, documented and
tested before the frontend used it** (`04_…` §10; `tests/test_survey_fi1.py`).

### API changes

| Change | Kind |
|---|---|
| `GET /survey-definitions/{id}/draft/documents` — everything needed to open a draft | New operation, `survey.read` |
| `POST /survey-definitions/{id}/draft/save` — every operation as one revision, or none | New operation, `survey.edit` |
| Draft operation `SET_DETAILS` (name, purpose) | New operation kind |
| Optional `authoring` object on ITEM, MODULE and CONDITION documents — no execution meaning | New optional field |

**OpenAPI additivity** (against the accepted SS-03A contract `a607ff5`): operations 214 → 216, 2 added, 0 removed;
schemas 427 → 431, 4 added, 0 removed, 0 changed. **One existing operation differs, in its description text only**
(`…/draft/operations` now names `SET_DETAILS`). SHA-256 `725fee2c…` → `5a31269b…`. No migration: no table changed.

### How a Save behaves

| Requirement | Behaviour | Evidence |
|---|---|---|
| Starts from an explicitly known revision | Sends the revision it loaded as `expected_revision` | Unit and journey |
| Persists the survey and assets consistently | One request; the server applies all operations in one transaction | Backend: a save that fails at operation 7 of 10, at a removal, or at an unknown operation leaves the draft row, every asset, the name and the audit trail exactly as they were |
| Success only after the server confirms the complete save | "Saved" is shown only when the server's reply holds every document that was sent | Unit: a reply that does not is reported as not saved |
| Unsaved work retained on failure | The workspace is never replaced or cleared by a failed save | Unit and journey |
| Network errors and retry without duplicating | "Try again" first asks the server what it has. If the earlier save had arrived, it is recognised and nothing is sent again | Journey FI-1.3: reply dropped after the server saved → one revision, zero re-sends |
| Never silently overwrites another author | A stale revision is refused by the server | §4 |
| No client-side compensation | None exists: there is no partial state to compensate for | — |

There is **no autosave**: the journey asserts the server is still at revision 0 after editing in both views.

---

## 4. Conflict resolution

When a save is refused as stale, the author sees one panel. Nothing has been sent, merged or lost at that point.

| Shown | Content |
|---|---|
| What happened | "You started from revision 1. The server now has revision 2, saved by E2E Survey Author at …" |
| Changed on the server only | Named documents |
| Changed by you only | Named documents |
| Changed by both | Named documents, highlighted |

| Choice | Effect |
|---|---|
| Keep editing — decide later | Closes the panel. Local work stays, unsaved. Save asks again |
| Discard my changes and load revision N | Explicit reload of the server's draft |
| Save my changes on top of revision N | Controlled retry against the newer revision. Documents only the other session changed are kept; the author's changed documents are applied. If both changed the same document, the panel says beforehand that the author's version replaces theirs, and lists them |

**On "never silently merge".** Saving on top combines two sessions' changes **per document**, only after the author
has seen which documents each side changed and has chosen it. It never combines changes inside one document.

Evidence: journey FI-1.2 (two real browser sessions, two people) and six unit tests.

---

## 5. Server-authoritative validation

- The Validate step shows the server's verdict on the **saved revision**, with the server's stable codes.
- The browser's checks remain, under the heading "Editor checks — immediate, in your browser — not authoritative".
  Warnings and information items come only from there, and say so.
- With unsaved changes the panel states that the server has not seen them.
- "Submit" is not available. The journey also asks the server directly: it refuses a candidate with
  `VALIDATION_BLOCKED`.
- The standing restrictions are on the list and on Validate: synthetic and unapproved wording; non-answer behaviour
  undecided; no survey eligible for a live call.

---

## 6. Access

| Person | Result | Evidence |
|---|---|---|
| Holds `survey.read` and `survey.edit` only | Reaches Survey Studio from the navigation; `/scripts` and `/assignment-rules` send them to "unauthorised"; the Script Studio API answers 403 | Journey FI-1.5; development walkthrough |
| Holds `survey.read` only | Opens surveys; "Read only"; Save disabled; the server refuses a save with 403 | Journey FI-1.5 |
| Ordinary user, no survey permission | Route → unauthorised; API 403 | Journey FI-1.5; backend |
| Every survey permission, another market | Empty list; a direct link says there is no such survey; API 404 | Journey FI-1.5; backend |

The three development identities were used unchanged. `script.read` was given to nobody.

**Read-only walkthrough on the development database** (as `dev.survey.author`, running dev servers): the list shows
the synthetic published survey; it opens as saved at revision 10 with its three modules shown as locked shared
versions; Save is disabled; **no write request was made**; the survey tables are identical to the enablement
report. Evidence: `dev_database_walkthrough.txt`, screens `DEV01…DEV03`.

---

## 7. Acceptance tests

| # | Owner's test | Result | Where |
|--:|---|---|---|
| 1 | Create → edit in Guided → edit in Graph → Save → reload | Pass | Journey FI-1.1 |
| 2 | Exact content and identity preservation across a browser restart | Pass: revision, content hash and every asset hash and document identical | Journey FI-1.1 |
| 3 | All 27 fixture documents round-trip without loss | Pass | `documents.test.ts` |
| 4 | Two concurrent sessions, stale-revision refusal, explicit resolution | Pass | Journey FI-1.2 |
| 5 | Partial-save failure produces no misleading success | Pass: server untouched, "Not saved" shown, work kept | Journey FI-1.3; backend |
| 6 | Server validation blocks an invalid submission path | Pass | Journey FI-1.4 |
| 7 | Unauthorized and cross-market access denied | Pass | Journey FI-1.5; backend |
| 8 | Existing frontend tests, 13 prototype journeys, 33 standard journeys | Pass: 403 existing unit tests, 13 of 13, 33 of 33 | `frontend_checks.txt` |
| 9 | Existing backend and Script Studio behaviour unchanged | Pass: 657 earlier tests pass; one SS-03A test file updated for the two added operations | `backend_tests.txt` |

### Regression results

| Check | Result |
|---|---|
| Backend suite (isolated test database) | 668 passed, 0 failed (657 + 11 new) |
| Backend lint, format, strict types, contract check | Clean |
| Frontend unit tests | 505 passed (403 + 102 new) |
| Frontend type check, lint, client drift check | Clean |
| Persisted journeys (full stack, new) | 5 of 5 |
| Prototype journeys | 13 of 13 |
| Standard Playwright | 33 of 33 |
| Golden fixtures | Unchanged; canonical export current |
| Specs validator | PASS |

Evidence: `docs/acceptance/evidence/FI-1/`. Screens: `FI01` loading · `FI03`, `FI04` unsaved · `FI05` saved ·
`FI07` after restart · `FI08`–`FI10` conflict · `FI11` failed · `FI12`–`FI14` server validation · `FI15` leave
warning · `FI16` read only · `FI17` other market.

---

## 8. Things the owner should know

1. **Three backend changes go beyond "a batch save".** The documents read (needed to open a draft at all),
   `SET_DETAILS` (so a rename is saved) and the `authoring` field (so module intent, kind and labels are not lost on
   reload). Each is additive, documented and tested. `authoring` is an addition to the canonical document contract
   and needs the owner's acceptance as such.
2. **One existing operation's description changed** in the published contract (text only).
3. **A saved survey shows only its own library.** Its modules, questions and conditions are those it owns or pins.
   Re-using another survey's published modules needs a library-content read the API does not have. Not built.
4. **New codes are numbered in a per-survey range** (for example `Q-NEW-453897002`), because asset codes are unique
   across the server and the editor numbers new items from a counter. A collision between two surveys is very
   unlikely, not impossible; the server would refuse the save and say so. Server-issued codes would remove this.
5. **The conflict panel names documents by kind and code**, not by the question's text. Accurate, not friendly.
6. **Leaving with unsaved work.** The browser asks before a reload or close. An in-app dialog asks before following
   a link out of the survey. The browser's Back button is not intercepted; the edits stay in memory while the page
   lives, so coming back shows them still unsaved.
7. **Server validation needs `survey.edit`** (as built in SS-03A). A read-only person sees that stated.
8. **The draft label** reads "Draft v1.0+" after a published version 1.0, and "Draft v0.1" before any.
9. **One wording per item version.** A draft where one item version is placed with two wording versions cannot be
   opened in this editor and says why. The server permits such drafts; nothing creates them today.
10. **The frontend dev server now runs in persisted mode** (`VITE_SURVEY_STUDIO_PERSISTED=1`). To see the in-memory
    prototype again, start it with `VITE_SURVEY_STUDIO_PROTOTYPE=1` alone. Both are off by default in code.
11. **Makers accumulate.** Both people in the two-session test are makers of the draft, so neither could later
    approve or publish a candidate of it. That is the rule as approved; it will matter in FI-2.
12. **A finder file changed in the specs working tree** (`docs/acceptance/evidence/.DS_Store`). Not mine; left alone.

---

## 9. Git safeguards (owner's section H)

Inspected before any commit; **no commit was made**. Evidence: `git_automation.txt`.

| Checked | Found |
|---|---|
| Active hooks in the three repositories | None |
| `core.hooksPath`, global hooks, template directory | Unset |
| Push configuration, aliases | None |
| Husky, Lefthook, pre-commit files; scripts that run git | None |
| Scheduled jobs (crontab, launch agents) mentioning git or Call360 | None |
| Claude Code hooks | None |
| Editor settings | VS Code and Cursor user settings have `git.enableSmartCommit: true` and `git.confirmSync: false`; each repository's git config carries a VS Code key (`branch.main.vscode-merge-base`) |

**What the evidence supports.** Nothing in the repositories or on a schedule pushes automatically. My own local
commits of 23:40 and 00:42 stayed unpushed until a later commit from the owner's identity, which rules out a
push-on-commit mechanism. Every pushed commit carries the message "commit" (once "comit"), covers all three
repositories within about ten seconds, and is recorded with its push at the same second.

**What it does not establish.** The cause. The pattern is consistent with a "commit and sync" action in an editor
that has confirmation switched off, but I have no record of the action itself and do not claim it.

---

## 10. Proposed FI-2 boundary

**Not authorised.**

**Goal.** Review and publication of a saved survey on the real, immutable candidates of SS-03A.

| In | Out |
|---|---|
| Submit the saved draft as a candidate (server validation must pass) | Execution, simulation or call-plan assembly on the server (SS-03B) |
| Candidate view: frozen content, manifest, history, integrity | Any non-answer behaviour; live-call eligibility |
| Approve or reject by a different person; withdraw by the submitter | Assignment of surveys to cases |
| Publish by a third person; version view | Granting permissions to existing roles |
| Editing after submission: a frozen question or module becomes a new version, through the editor's existing "new version" and "derive" actions | Changes to Script Studio |
| The three development identities, each doing only their part | Re-use of other surveys' published modules, unless ruled in (FI2-D-2) |
| Warnings and acknowledgements: where they live once review is real | — |

**Decisions needed first**

| ID | Decision |
|---|---|
| FI2-D-1 | Acknowledgements: server validation has blockers only. Either the server gains warnings, or acknowledgements of editor-only warnings are recorded with the candidate as stated by the author |
| FI2-D-2 | Whether the shared library (re-using published modules across surveys) is part of FI-2 — it needs one more read operation |
| FI2-D-3 | Whether "makers" stays "everyone who ever changed the draft", which with two authors and three identities can leave nobody able to approve |
| FI2-D-4 | Whether codes become server-issued before more surveys are created |

---

## 11. Modified files

### Call360-backend (base `4ae7875`; uncommitted)

| File | Change |
|---|---|
| `app/domain/survey/store.py` | Operation step shared by single and batch; `apply_batch`; `draft_documents`; `SET_DETAILS`; `STALE_DRAFT` carries the current revision |
| `app/domain/survey/documents.py` | Optional `authoring` on ITEM, MODULE, CONDITION |
| `app/api/survey_definitions.py` | Two operations and their four models |
| `contracts/generated/openapi.json`, `openapi.sha256` | Regenerated |
| `scripts/dev_survey_identities.py` | The creation function accepts a list of people and a market (used by the test setup) |
| `tests/test_survey_api.py` | Counts and matrix updated for the two operations |
| **New** `tests/test_survey_fi1.py` | 11 tests |
| **New** `scripts/export_survey_fixture_documents.py` | The canonical fixture export and its drift check |
| **New** `scripts/e2e_survey_setup.py` | Test-schema-only identities for the browser journey |

### Call360-frontend (base `abb7726`; uncommitted)

| File | Change |
|---|---|
| **New** `src/features/surveystudio/model/documents.ts`, `documents.test.ts` | The mapping (332 lines) and its proof |
| **New** `src/features/surveystudio/persist/` — `api.ts`, `saving.ts`, `Persistence.tsx`, `SaveControl.tsx`, `ServerValidationPanel.tsx`, `PersistedStudioRoot.tsx`, `standing.ts`, `Persistence.test.tsx` | Generated-client calls; save rules; save state and conflict; list, create, load |
| **New** `e2e/persisted/fi1.persisted.ts`, `global-setup.ts`, `playwright.persisted.config.ts` | The full-stack journey |
| `src/features/surveystudio/flag.ts`, `src/vite-env.d.ts` | The separate persisted-mode setting |
| `src/App.tsx`, `src/app/AppShell.tsx` | Route guarded by `survey.read` in persisted mode; navigation entry for either mode |
| `src/features/surveystudio/store.tsx` | The provider can hold a saved survey; `replace`; `persisted` |
| `src/features/surveystudio/StudioRoot.tsx` (+9 −4), `JourneyNav.tsx` (+5 −4), `ValidationPage.tsx` (+8 −3) | The three persisted-mode differences of §1 |
| `src/features/surveystudio/model/types.ts` | Three optional fields: option-set reference, obligation code, per-answer texts |
| `src/styles/survey-studio.css` | 37 lines appended for the new states |
| `src/api/generated/schema.d.ts`, `openapi.pinned.json`, `contract.lock.json` | Regenerated client |

Not changed: every Script Studio file; `src/styles/app.css`; the prototype's pages, model, engine and journeys.

### Call360-specs (base `cab99e5`; uncommitted)

`04_…` §10 · `06_…` D-195…D-203 · `29_…` (this report) · `README.md` · `SESSION_HANDOFF.md` ·
**new** `canonical-documents/` (27 generated files) · **new** `docs/acceptance/evidence/FI-1/` (5 files, 20 screens).
