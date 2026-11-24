# APPL-X3 — persistent Applicability Policies: readiness assessment

**Status: ASSESSMENT ONLY, 2026-11-24. APPL-X3 is NOT started and NOT authorised.** No table, migration, API or
screen of APPL-X3 exists. This document says what is ready, what must be decided first, and what the checkpoint
would contain. Publication of policies and permanent scenarios remain APPL-X4.

## 1. Verdict

**Ready to specify; four decisions are needed before building (§5).** Everything APPL-X3 stands on exists and is
verified in the test schema and now in local development: the governed library (`0038`), the read-only integration
with published Survey Studio versions, the evaluator, and a designer that already edits exactly the document that
would be stored.

## 2. What already exists and is reused unchanged

| Capability of APPL-X3 | Already there | Gap |
|---|---|---|
| Cards, Graph and Matrix on one document | all three render one in-tab `Policy` document; none keeps a copy | the document lives in the tab |
| Deterministic evaluation | the Python evaluator; same request, same plan, same fingerprint | it is given the documents by the browser; APPL-X3 should evaluate **from the saved draft** |
| Exact published survey-version references | `{code, version, version_id, definition_id, fingerprint, manifest}` in every requirement; picker and preview read Survey Studio | not checked by a server on save |
| Exact published condition references | `{condition, version}`; a new reference names the published version | not checked by a server; no stored pin of the variables a policy reads |
| Version-aware adoption | built and tested for surveys (deliberate, undoable) | not built for library items: a policy that names condition version 1 is not told that version 2 exists, beyond a note on the line |
| Optimistic concurrency, drafts, audit history, market isolation | the pattern is built and tested for library assets (`60_…` §1–4) | to be applied to policies |
| Multi-policy authoring | gallery, switcher, duplicate, compare | in the tab |
| Where used | exact and indexed between library items | for policies: computed from the tab (and Survey Studio's "where used" reads the tab and says so) |

## 3. Proposed scope of APPL-X3

1. **One table for the policy and its working draft**, on the pattern accepted for library assets: stable identity
   (market, code), `draft` document, `draft_revision`, who saved. Review whether anything more is needed — I expect
   not until candidates exist (APPL-X4).
2. **One table of references of the saved draft** (policy → library version or library draft; policy → survey
   version), rewritten on each save. This is what makes "where used" genuine, indexed and shared, and what the
   dependency diagnostics read.
3. **An event table**, or the reuse of `applicability_event` with a nullable policy reference — to be decided on the
   schema review.
4. **API**: list, create, read, save with expected revision, discard, duplicate; `validate` and `evaluate` **on the
   saved draft**, with the workspace built by the server from the persisted library; where-used for a library item
   and for a published survey version.
5. **Dependency diagnostics (D-404).** For each requirement: which library items it reads; whether each is published
   or a draft; whether the version it names is the current one. Shown on the card, the graph and the matrix, and in
   the policy header ("reads 2 unpublished items — not ready for publication"). A draft may be saved in that state;
   it is never called ready.
6. **Adoption of newer library versions**, as for surveys: offered, never applied silently, undoable.
7. **Frontend**: the policy store moves to the server behind the existing save-state bar (Saving · Saved · Unsaved ·
   someone else saved first); the labels "in this tab only" disappear for policies and remain for scenarios until
   APPL-X4; undo and redo stay in the tab over the unsaved edits.
8. **Permissions**: the existing `applicability.read / edit`. No new permission is needed until policy candidates
   (APPL-X4, `approve / publish`).
9. One additive migration, test schema first, with the same tests as `0038`.

## 4. What stays for APPL-X4

Submission of a policy as an immutable candidate; its manifest; three-person approval and publication; **the
enforcement that a policy candidate references only published, exact versions** (D-404); the contract for
acknowledging or resolving profile mismatches at publication (D-394); saved scenarios and regression suites;
recorded evaluations.

## 5. Decisions needed before APPL-X3

| | Question | My recommendation |
|---|---|---|
| X3-1 | Should a policy draft **store the exact version of every variable it reads**, or only of the conditions and surveys it names (variables being resolved when evaluated)? | Store them: record, on each save, the exact library versions the draft was last evaluated against, and show a diagnostic when one has moved. This answers the open part of D-405 for policies. The candidate (APPL-X4) then freezes them |
| X3-2 | The same question for **library drafts** (the open part of D-405): record intended versions between sessions? | Not in APPL-X3. The acknowledged list at submission closes the risk; revisit if authors report surprise |
| X3-3 | **Navigation and the route's permission.** The workspace needs `survey.read` (D-408). Should APPL-X3 keep that, or let a person with only applicability permissions open the library screens? | Keep it. One workspace, one explicit read-only dependency; splitting the screens by permission is a larger change with little benefit |
| X3-4 | The stateless **prototype operations** (`/survey-applicability/prototype/*`): remove when `evaluate` on a saved draft exists? | Keep `evaluate` and `scenarios` for scenarios, which stay in the tab until APPL-X4; remove `analyse` and `condition-test` in APPL-X3, replaced by the persisted ones |
| X3-5 | The showcase **policies** ("ILP and NFTF showcase" and the patterns): publish them into the saved store the way the library was, or keep them as built-in starting points? | Keep the patterns as starting points that create a saved draft; do not seed a "published" policy before policy publication exists |
| X3-6 | A **code for a new item before it is named** (the `new_profile` of D-410): ask for the name first? | Yes, for profiles and policies: a name step before creation, since a code never changes |

## 6. Risks

* **Two stores during the transition.** Scenarios stay in the tab while policies are saved: a saved policy evaluated
  against in-tab scenarios. The labels must stay truthful; APPL-X4 removes the split.
* **Undo across a save.** The tab's undo will cross a server save; the bar must show the draft as unsaved again,
  never pretend to undo a save.
* **Reference rows and the document can disagree** if written separately; they must be written in one transaction
  from the document, and tested for equality.
* **Scale.** The 100-requirement example saves as one document of roughly 60 to 80 kB; saving whole documents is fine at
  this size, and a limit should be stated.
* The carried UX items remain: nested condition readability, graph legibility at 100 requirements, no test with
  people, no screen-reader test.

## 7. Not part of APPL-X3

Operational selection of surveys for cases (APP-1a, OPS-1), voice (VOICE-1), migration or retirement of the legacy
assignment rules, bindings and groups (MIG-2). None is started and none is implied.
