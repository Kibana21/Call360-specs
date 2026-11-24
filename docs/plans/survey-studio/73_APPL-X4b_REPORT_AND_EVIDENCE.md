# 73 — APPL-X4b report and evidence

**Built and verified on the isolated test schema, 2026-11-24. Awaiting owner acceptance. Nothing committed.**
Synthetic data only. Local development is untouched: still at `0040_applicability_scenarios`, no APPL-X4b table, the
publication setting off (checked, §11).
Architecture and contracts: `72_…`. Specification implemented: `70_…`.

---

## 1. The final acceptance criterion, part by part

| The owner's criterion | Shown by |
|---|---|
| An author submits an exact persisted policy with a qualifying, independently supported, passing suite | X4b.1: readiness clear only after the author chooses the run; fingerprints confirmed; candidate frozen |
| A separate checker inspects the immutable candidate and approves or returns it | X4b.1 (approve), X4b.2 (return with a reason) — a second signed-in person |
| A third person publishes the approved candidate | X4b.1, X4b.4 — a third signed-in person, after server revalidation |
| The published version preserves document, manifest, evidence fingerprint, selection behaviour and audit history | X4b.1: version equals its candidate, not the draft edited meanwhile; verified from its own content |
| A newer publication supersedes the older without destroying it | X4b.4: version 2 published; version 1 superseded, readable, verified |
| No publication bypasses validation, evidence, dependency integrity or three-person separation | X4b.3 (every blocker), X4b.4 (evidence changed after approval), X4b.6 (every crossover); backend tests |
| No operational record or legacy assignment object created or changed | backend: every non-applicability table byte-identical except `audit_event` |

## 2. What was built

- **Backend:** migration `0041_applicability_publication`; `app/domain/survey/applicability/publication.py`
  (`readiness`, `independence`, `provenance`, `submit`, `revalidate`, `decide`, `withdraw`, `publish`, `refused`,
  `verify_version`, `targets`, `run_subject`, `impact`, `usage`); `app/api/applicability_publication.py` (13
  operations); setting `applicability_publication_enabled`; `tests/test_applicability_publication.py` (7 tests).
- **In the accepted scenario service** (`scenarios.py`), additive: server stamps `stated_by` / `stated_at` on a changed
  expectation; a frozen evaluator for candidates and versions; the run target recorded in each run. The evaluator
  (`logic.py`, `evaluator.py`, `analysis.py`) and `policies.py` are **unchanged**.
- **Frontend:** `publicationApi.ts`, `Publication.tsx`; the run-target chooser in the suite builder; what each run
  evaluated in the run history; setting `VITE_APPLICABILITY_PUBLICATION`; Playwright configuration
  `playwright.publication.config.ts` with `e2e/publication/governance.pub.ts` (7 journeys).
- **Shared shell:** three changed lines in `AppShell.tsx`, one rule in `app.css`, and `e2e/shell-narrow.spec.ts` (§8).
- **OpenAPI:** 13 operations and 19 schemas added; two optional fields and one field added to existing scenario
  schemas (`target`, `expectation_stated_by`, `expectation_stated_at`); nothing removed.

## 3. Journeys (real browser, real backend, test database, three signed-in people)

| Journey | Test | Result |
|---|---|---|
| A full valid lifecycle | X4b.1 | pass |
| B return and resubmit | X4b.2 | pass |
| C every blocker | X4b.3 | pass |
| D evidence mutation after approval | X4b.4 | pass |
| E supersession | X4b.4 | pass |
| F impact | X4b.2, X4b.5 | pass |
| G three-person controls | X4b.6 (+ backend identity test) | pass |
| H negative integration | backend tests | pass |
| four widths, keyboard, accessibility | X4b.7 | pass |

Screens: `docs/acceptance/evidence/APPL-X4b/screens/` (`01`–`20` follow the journeys; `30-*` the four widths).

### 3.1 What each journey shows

- **A.** Without evidence the page says **Not ready** with one blocker (`SUITE_REQUIRED`) and nothing is preselected.
  After the author chooses the run: ready; "6 of 6 expected outcomes were stated independently"; a provenance row per
  scenario with who stated it and when. Submit is disabled until the three fingerprints are confirmed. The candidate's
  document, manifest and evidence fingerprints equal what the author was shown. The author sees "You submitted this
  candidate. Someone else must approve or return it" and no approve control. The draft is then edited; the candidate
  is unchanged. The checker approves by fingerprint; the publisher confirms fingerprint and "version 1" and
  publishes. The version's document equals the candidate's and **not** the edited draft; three different people are
  named; "Verify" succeeds.
- **B.** After the policy changes, the earlier run is `EVIDENCE_OUT_OF_DATE`. A suite run now needs an explicit target:
  the chooser is empty, Run is disabled, and the API refuses a run with no target (`TARGET_REQUIRED`). The checker
  sees what changes from version 1 on the same six scenarios, returns the candidate with a reason; the author sees
  the reason, edits, runs against the named draft revision, and submits candidate 3. Candidates 1 (published), 2
  (returned) and 3 (submitted) are all listed and readable.
- **C.** Each blocker on the screen, with its remedy, and submission refused by the server:

  | Case | Blockers reported |
  |---|---|
  | no suite chosen | `SUITE_REQUIRED` |
  | every expectation copied from a result (the run itself PASSED) | `EXPECTATIONS_NOT_INDEPENDENT` |
  | one material behaviour covered only by a copied result | `BEHAVIOUR_ONLY_RESULT_DERIVED` — "No independently stated scenario makes 'ILP with NFTF needs Survey C' apply" |
  | a failing suite | `SUITE_FAILED` |
  | an exploratory suite | `SUITE_REQUIRED`, `COVERAGE_NOT_MEANINGFUL` |
  | a scenario changed after the run | `EVIDENCE_OUT_OF_DATE` |
  | an unpublished dependency; then that draft changed | `UNPUBLISHED_DEPENDENCY`; `DEPENDENCY_STALE` |
  | a condition against another fact version | `PIN_DIFFERS` — "There is no override" |
  | a profile mismatch in a gating scenario | `PROFILE_MISMATCH`, `SUITE_FAILED` — "no acknowledgement for a publication-gating scenario" |
  | same person | `403` in the browser (the author holds no approval permission); `409 SAME_PERSON` in the backend identity test |
  | invalid survey reference | cannot be created through the product: saving one is refused (`INVALID_SURVEY_REFERENCE`); the gate's own check is exercised in the backend test by altering the stored document directly |

- **D.** After approval a scenario of the evidence suite is edited. The publisher's screen shows the revalidation
  problem and keeps Publish disabled; the API answers `409 PUBLICATION_BLOCKED` with `EVIDENCE_CHANGED`. The
  candidate is byte-identical afterwards, still `APPROVED`, and its history ends with the refused attempt. No version
  was created.
- **E.** With the scenario put back exactly, revalidation is clear and the publisher publishes **version 2**,
  "superseding version 1". Version 1 is `SUPERSEDED`, still opens, and verifies.
- **F.** Version 1 → version 2 on the same six recorded scenarios: two select differently — "ILP with NFTF" loses A
  and B ("was active and is now replaced"), "NFTF not known" has A newly pending — and "requirement changed: ILP with
  NFTF needs Survey C". The same suite run against published version 1 is recorded as exactly that ("published
  version 1 (superseded)"), with version 1's document fingerprint, and is not evidence for the draft.
- **G.** Thirteen crossovers with real sign-ins, each refused: author, second author and publisher approving; the
  publisher before approval; a second author withdrawing; the checker submitting; the checker publishing what they
  approved; the author publishing; a wrong fingerprint; a wrong version number; no CSRF token; `PUT` and `DELETE` on a
  version. The candidate did not move; the refused attempts are in its history.

## 4. Three-person separation — evidence at three levels

| Level | Evidence |
|---|---|
| Permission | least-privilege identities: each step refused (`403`) for the two other roles (backend lifecycle test; X4b.6) |
| **Identity** | three people who each hold **all four** permissions: the submitter cannot approve or return (`SAME_PERSON`), the submitter and the checker cannot publish, a non-submitter cannot withdraw; a third person publishes; four refused attempts recorded as `REFUSED` events and four `DENIED` audit records |
| Database | CHECK constraints refuse a row whose checker is its submitter, or whose publisher is either — tried directly |

## 5. Immutability and "the version is its candidate"

- Guards tried directly, each refused: change a candidate's document or fingerprint; move it back to `SUBMITTED`;
  delete it; rewrite a recorded decision; delete a manifest row; edit an event; change or delete a version; supersede
  a version without a newer publication.
- The version insert is refused by its guard unless document, manifest, evidence and fingerprints equal the
  candidate's.
- `verify_version`: fingerprints intact, identical to the candidate, evidence reproduced from the run's own record
  (5 of 5 in the backend test; 6 of 6 in the browser).

## 6. Independent expectations and provenance

- Rule as specified (`72_…` §4), a pure function over the recorded run; tests cover all three blockers, the
  satisfied case, and a suite whose **run passes and is "meaningful"** yet is rejected as evidence.
- The server never upgrades a source; stored sources read back unchanged (`AUTHORED` ×4, `PROPOSED_FROM_RESULT` ×1).
- Stamps: `stated_by` / `stated_at` written when stated content changes, kept when it does not.
- Older expectations: with the stamps removed from stored members, authorship is read from the suite's append-only
  history and labelled `SUITE_HISTORY`; with no history, `UNKNOWN` and no name. Nobody is invented.
- On the screen a coverage panel beside rejected evidence says "Covered — but not by independently stated
  expectations", never "Meaningful for publication" (found from a screenshot and corrected, §10).

## 7. Migration `0041` — test-schema evidence

`test_zz_migration_0041_…`, on a schema holding a published library, three published surveys, a saved policy, five
scenarios, a suite and a recorded run:

1. head `0041`; exactly 4 tables and 4 functions; 11 validated foreign keys; still 4 applicability permissions;
2. downgrade while empty: all removed; every other table identical in count and digest — **including the scenario,
   suite and run tables**;
3. forced failure at the last statement: nothing left behind;
4. upgrade again: identical objects, everything else identical;
5. with a submitted candidate: downgrade refused; with a published version: refused; the version still verifies;
6. publication changed no scenario, suite or run row; only `audit_event` differs elsewhere; the audit chain verifies.

The three older migration tests (`0038`, `0039`, `0040`) were adjusted for the revision above them. No behavioural
assertion was weakened.

## 8. Shared-shell accessibility correction (D-456)

- **Cause:** at 760 px and below the navigation links' text is hidden with `display: none`, which also removes it
  from the accessibility tree, so the links had no accessible name; the account button likewise.
- **Change — the shell only, nothing else:**
  - `AppShell.tsx`: the link's label carries a class (`navlabel`); the account button contains a visually-hidden
    "Account menu" text. Three lines.
  - `app.css`: one rule — at 760 px and below the label is *visually hidden* instead of removed. Each link's
    accessible name is therefore its own visible label, the destination, identical at every width.
- **Two earlier attempts, withdrawn — both were my errors and were caught by tests:**
  1. `aria-label` on the account button and ARIA names on the not-yet-available entries: failed the automated
     "visible label must be in the accessible name" check. The not-yet-available entries are left exactly as they
     were; their `title` already names them.
  2. `aria-label` on the navigation links: passed my new test, then **failed the existing standard suite** — the
     "Script Studio" link also shows a "Legacy" tag, so the override name no longer matched the visible text. My new
     test also signed in four times and **used up the suite's sign-in allowance**, which made three later tests
     (review workbench, two voice tests) fail at sign-in. The final version overrides no name and signs in once.
- **Test** (`e2e/shell-narrow.spec.ts`, standard suite, one sign-in): at **761, 760 and 390 px** — every navigation
  link is found by role and name; the label is shown above the breakpoint and visually hidden, never removed, at it;
  the account button is named; automated link, button and label-in-name checks are clean; the link boxes and page
  width are identical with the label visually hidden and with it removed (nothing visible moves); a link and the
  account menu are operated from the keyboard.
- **Effect:** the publication journeys' accessibility scan passes over the whole page at 390 px, shell included.
- **Not claimed:** WCAG conformance of the application. These are automated checks; no screen reader was used.

## 9. Security and isolation

- Another market: readiness, versions, run targets, a candidate, a version, verify, withdraw and impact all `404`;
  its candidate list and usage are empty.
- CSRF: decision, publication and withdrawal without the token are `403` whoever asks.
- Read-only people read everything and are offered nothing; a run against any target needs the edit permission.
- No operation changes a candidate's content or a version (`405` for `PUT`, `PATCH`, `DELETE`).

## 10. Defects found and fixed while building

| Found by | Defect | Fix |
|---|---|---|
| backend tests | an SQL parameter used with two types in the decision update | separate parameter |
| contract test | two operation ids and one schema name collided with the library's | renamed `…policy_candidate…`, `ApplicabilityPolicyWithdrawIn` |
| X4b.2 | my journey read the run list before the run was recorded | the test now waits for the recorded run |
| X4b.7, standard suite | my first two shell corrections broke the label-in-name check, and my shell test exhausted the sign-in allowance | reworked as in §8 |
| screenshot | "Meaningful for publication" shown beside rejected evidence | the panel states the conflict |
| screenshot | the dependency toggle was unstyled outside the Scenario studio | style generalised |
| my own test | I assumed restoring a scenario's exact content would still block publication | it does not, by design: the check is on content (`72_…` §5.1) — the test now asserts that explicitly |

## 11. Development — untouched; access review

- Revision `0040_applicability_scenarios`; 0 APPL-X4b tables; `applicability_publication_enabled` false; no
  publication route served.
- **Access review of `dev.admin` (read-only; nothing changed):**

  | Item | Finding |
  |---|---|
  | Memberships | `LOCAL_ADMIN` (since 2026-11-15) and `LOCAL_DEV_APPL_AUTHOR_SG` (added 2026-11-24 09:13 by `dev.admin`, audit reason "adding this role"), both open-ended |
  | Effective applicability permissions | `applicability.read`, `applicability.edit` — **not** `approve`, **not** `publish` |
  | Effective survey permissions through that membership | includes `survey.read` (the role's declared dependency); its other survey permissions come from its administrator membership |
  | Applicability actions on record | one: saved policy `SHOWCASE-DEPENDENCIES` (revision 6) |
  | Consequence for APPL-X4b | `dev.admin` could author and **submit** a policy candidate in development; it could not approve or publish one, and could not act twice on one candidate |
  | Status | **open item for the owner** — the membership is neither altered nor relied upon by anything here |

## 12. Regression — final source, 2026-11-24

| Check | Result |
|---|---|
| Backend suite (test schema) | **1095 passed**, 0 failed, exit 0 |
| ruff · ruff format · mypy (140 files) | clean |
| OpenAPI | regeneration changes nothing; SHA-256 `078ad52f8eded9bbc389b28edd029f961ce234494d984c46d9347fc6c75a259d` |
| Frontend contract check · lint · unit (636) · build | pass |
| Playwright publication | 7 passed |
| Playwright scenarios | 11 passed |
| Playwright applicability | 26 passed |
| Playwright persisted | 34 passed |
| Playwright prototype | 13 passed |
| Playwright standard (with the shell test) | 34 passed |
| Specs validator | pass |

The backend suite and static checks ran before the final shell rework; the rework touched `AppShell.tsx`, `app.css`
and one test file only, after which lint, unit tests, build and all six browser suites were run again.

**Failures seen on the way, not concealed:**

- **Standard suite, first run: 5 failed.** Caused by my second shell attempt (§8). Fixed; 34 pass. Log kept:
  `test-output/playwright-standard-FIRST-RUN-5-failed.log`.
- **Applicability suite, first run: 1 failed** — X3.8, "the whole canvas of 100 is on the screen". It passed on the
  next full run with no change to that screen or its test. I did not find the cause. **Treat it as an intermittent
  failure under watch, not as fixed.** Log kept: `test-output/playwright-applicability-FIRST-RUN-1-failed.log`.
- The Voice Studio reliability defect remains open; the voice tests passing here does not close it.

No test was weakened, no timeout raised, no golden fixture changed.

## 13. Not done, not measured, not claimed

- Migration `0041` on development; any use of a published policy by operations.
- Designer integration steps 2–4 (D-454).
- Usability targets that need people; screen-reader testing; WCAG conformance.
- The readiness blocker for an invalid survey reference is shown only in a backend test (the product refuses to save
  one).
- Repositories at backend `e061b72`, frontend `9b86470`, specs `001058f`, each with uncommitted work. Nothing
  committed or pushed.
