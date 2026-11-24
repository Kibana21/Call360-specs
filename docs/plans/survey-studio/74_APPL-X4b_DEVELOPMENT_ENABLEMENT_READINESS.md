# 74 — APPL-X4b: development-enablement readiness report

**A readiness report only. Nothing here is authorised. Migration `0041` has not been applied to development.**
Date 2026-11-24. Report for the implementation: `73_…`.

## 1. Where development stands (read-only check, 2026-11-24)

- Revision `0040_applicability_scenarios`; no APPL-X4b table; `applicability_publication_enabled` off.
- Library, policies and Scenario studio on. Six `SHOW-*` scenarios, suite `SHOWCASE-REGRESSION`, three recorded runs,
  policy `SHOWCASE-ILP-NFTF`.
- The backend code already expects head `0041` and accepts a schema at `0040` while the publication setting is off.

## 2. What enablement would consist of

1. **Complete preflight before any mutation** (D-453): revision, table and row counts, protected records, showcase
   surveys and module, group memberships, retention state — compared with the accepted `0040` baseline in `71_…`.
   **Any materially unexpected difference stops the work for the owner's decision, explained or not.**
2. Backup of the development database with a manifest; restore instructions added to `_db_backups/RESTORE.md`.
3. Apply `0041_applicability_publication` only (four tables, four functions; nothing existing altered).
4. Set `APPLICABILITY_PUBLICATION_ENABLED=true`; start the frontend with `VITE_APPLICABILITY_PUBLICATION=1`.
5. Verify: head, integrity, audit chain, every non-applicability table unchanged, existing journeys still pass.
6. Demonstrate the lifecycle on a synthetic showcase policy.

Rollback: the downgrade removes the four tables and is refused once a candidate exists; after that, rollback is the
backup.

## 3. Things the owner would need to decide first

| # | Question | Why |
|---|---|---|
| 1 | Which three development identities submit, approve and publish | `dev.applicability.author`, `.checker`, `.publisher` exist with the right permissions. No new grant is needed and none is proposed |
| 2 | `dev.admin` | Holds `applicability.read` and `.edit` through `LOCAL_DEV_APPL_AUTHOR_SG`, so it could **submit** a candidate; it cannot approve or publish. Keep, or remove the membership — the owner's decision; I change nothing |
| 3 | Existing development suite | `SHOWCASE-REGRESSION` was saved before expectation stamps existed. Its authorship would be read from the suite history and labelled so. If its expectations were proposed from results, the gate will block until they are stated anew — by a person, not by me automatically |
| 4 | Existing recorded runs | The three runs predate run targets and read as "the saved draft at that revision". They stay valid records; whether one still qualifies as evidence depends on the policy's current revision |
| 5 | Which policy to publish as the demonstration | A published version is permanent in development: versions are never deleted |

## 4. Not included

Operational use of a published policy (APP-1a, OPS-1), designer integration steps 2–4, APPL-X5, retirement of
prototype operations, any voice or Genesys work.
