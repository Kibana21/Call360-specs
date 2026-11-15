# CP0.2 — Development-schema deployment runbook (`call360`: 0002 → 0007)

**Status:** prepared 2026-11-15; safety-reviewed and corrected 2026-11-15 (§11). **Not authorised.** Run each step only after the owner explicitly authorises the deployment. The password rotation (step 4) needs its own authorisation.
**Scope:** schema `call360` in `Call360_db` only. `call360_test` is never touched by these steps. Existing ADMIN/USER accounts and the accepted CP0.1B-1 configuration must survive unchanged.
**Conventions:**
- One terminal, zsh or bash; every block starts with its own `cd`.
- No command prints a secret. Commands that need the database password prompt for it.
- `<STAMP>` is fixed once in step 2 and reused everywhere.

## 0. Preconditions

- Backend working tree is the verified CP0.2 build (base `08c139e` + `evidence/CP0.2/ui-fix/manifest_backend.txt`). Frontend contains the audit-table fix (`evidence/CP0.2/ui-fix/`). All checks there are green.
- Stop the development servers: `lsof -ti tcp:8000,5173 | xargs kill`

## 1. Preflight: confirm the target is the development schema (read-only)

```sh
cd ~/Documents/Work/Projects/Call360/Call360/Call360-backend
unset CALL360_ENV_FILE                     # make/CLI must read .env, never .env.test
uv run python -c "from app.core.settings import load_settings as l; s=l('.env'); print(s.app_env, s.target_schema, s.expected_database)"
#   expect: local call360 Call360_db       (no secret is printed)
uv run alembic current                     # expect 0002_config_foundation
uv run call360 audit-verify                # expect "Audit chain OK: 5 events; head 289d4029…"
psql -h localhost -U Call360_db_user -d Call360_db -v ON_ERROR_STOP=1 -c \
  "SELECT (SELECT count(*) FROM pg_tables WHERE schemaname='call360') AS tables,
          (SELECT count(*) FROM call360.principal) AS principals,
          (SELECT count(*) FROM call360.code_value) AS code_values"   # expect 21 / 2 / 2
```

Stop if any value differs. Guards that also apply later:
- Alembic verifies the database, role and schema before every revision.
- The seed refuses `call360` without `--allow-development`, and `make seed` without `CONFIRM=call360`.
- The seed refuses a schema that is not at head.

## 2. Back up the schema and its matching local configuration (one set, one stamp)

The set holds password hashes, refresh-token HMACs, the audit chain and secrets: treat it as a secret.

```sh
cd ~/Documents/Work/Projects/Call360/Call360/Call360-backend
STAMP=$(date +%Y%m%d_%H%M%S); BK=~/call360-backups/pre_cp02_$STAMP
mkdir -p "$BK" && chmod 700 ~/call360-backups "$BK"
pg_dump -h localhost -U Call360_db_user -d Call360_db -n call360 -Fc -f "$BK/call360.dump"
cp .env "$BK/env" && cp .env.local "$BK/env.local" && cp -R .secrets "$BK/secrets"
chmod -R go-rwx "$BK"
(cd "$BK" && find . -type f ! -name SHA256SUMS -exec shasum -a 256 {} + > SHA256SUMS)
pg_restore -l "$BK/call360.dump" | grep -c "TABLE DATA"     # expect 21 (20 tables + alembic_version)
echo "$STAMP"                                               # write it down
```

- **What the set is.** The dump and `env` describe the same moment and are restored together: the schema, plus the `.env` that can read it. `.secrets/` (JWT keys) and `.env.local` (developer account passwords) are not changed by any step, but are kept with the set for completeness.
- **Before rotation.** The original `.env` contains the old database password; it is valid only until step 4.
- **After rotation.** Keep the rotated `.env` and restore only the dump. Database passwords are cluster-level and are not part of the dump.
- **Integrity.** Check the set with `(cd "$BK" && shasum -a 256 -c SHA256SUMS)`.

## 3. What `scripts/make_env.py --force` changes (reviewed 2026-11-15)

| Item | Effect |
|---|---|
| `APP_DATABASE_URL` | Rewritten with the password typed at the prompt (no echo) |
| `REFRESH_TOKEN_PEPPER`, `CSRF_SECRET` | **Regenerated**: every development session and refresh token becomes invalid (users sign in again). No data changes |
| Other settings (`APP_ENV`, schema, role names, JWT key paths, origins, cookie flag) | Rewritten to the same values as today (same 13 names verified) |
| `PII_ENCRYPTION_KEY`, `PII_HMAC_KEY` | **Deleted if present.** After CP0.2 data exists this makes names and contacts unreadable and breaks HMAC lookups. See the rule below |
| Developer login credentials | Unchanged: Argon2 hashes in the database; plaintexts only in `.env.local`, which the script never touches |
| JWT signing keys (`.secrets/`) | Unchanged |

**Rule:** once the PII keys exist, never run `make_env.py --force` on its own. Always follow it with the key-restore command in step 4b, then the key check in step 7.

## 4. Rotate the development database password (separately authorised)

Run this in your own terminal so the new value is never typed into any tool or log.

```sh
cd ~/Documents/Work/Projects/Call360/Call360/Call360-backend
psql -h localhost -U Call360_db_user -d Call360_db
#   \password "Call360_db_user"      -- enter the new value twice (no echo); psql sends only its SCRAM hash
#   \q
uv run python scripts/make_env.py --force   # prompts for the new password; rewrites .env (mode 600)
uv run call360 audit-verify                 # proves the new password works (read-only)
```

- **4b. Only for a later rotation, after the keys exist:** restore the keys from the latest backup, without printing them:
  `grep -E '^PII_(ENCRYPTION|HMAC)_KEY=' "$BK/env.post_keys" >> .env && grep -c '^PII_' .env` → `2`
- **History cleanup:** remove any shell or psql history lines that contain the old password, using an editor, without displaying them. Then run `make secret-scan`.

## 5. Create the data-protection keys (once, never regenerated)

```sh
cd ~/Documents/Work/Projects/Call360/Call360/Call360-backend
uv run python scripts/make_data_keys.py --env-file .env --allow-development
grep -c '^PII_' .env                         # expect 2 (values never shown)
cp .env "$BK/env.post_keys" && chmod 600 "$BK/env.post_keys" && (cd "$BK" && shasum -a 256 env.post_keys >> SHA256SUMS)
```

- The keys are 32 random bytes each, independent of each other and of the test keys, and written only to the gitignored `.env`.
- The script never overwrites existing keys, and refuses a half-present pair.
- `env.post_keys` is the authoritative copy of the keys. **Losing both copies makes the development ciphertext unrecoverable.**

## 6. Migrate and seed

```sh
cd ~/Documents/Work/Projects/Call360/Call360/Call360-backend
make migrate && uv run alembic current        # expect 0007_governed_values (head)
make seed CONFIRM=call360                     # single transaction
make seed CONFIRM=call360                     # must print "Already seeded (no changes)"
uv run call360 seed-digest --allow-development   # record the digest
```

- Each migration revision runs in its own transaction.
- Migration 0007 writes nine `CONFIG.CODE_LIST_VERSION_ACTIVATED` events.
- The development digest differs from the test digest `05ce50c7…` because the HMAC key differs (D-33).
- A seed re-run recomputes the digest and **refuses if the HMAC key or the data changed** (`business data differs from the recorded seed manifest`).

## 7. Verify the keys match the seed (read-only; also after any later `.env` change)

```sh
cd ~/Documents/Work/Projects/Call360/Call360/Call360-backend
uv run python - <<'PY'
from sqlalchemy import text
from app.core.settings import load_settings
from app.db.session import make_engine
from app.domain.protection import DataProtection
s = load_settings(".env"); assert s.target_schema == "call360"
with make_engine(s).connect() as c:
    rec = c.execute(text("SELECT after->'key_ids' FROM call360.audit_event WHERE action='SEED.MANIFEST'")).scalar_one()
print("key ids match seed manifest:", rec == DataProtection.from_settings(s).key_ids)   # identifiers only
PY
```

Expect `True`. On `False`, stop: restore the keys from `"$BK/env.post_keys"` (step 4b).

## 8. Expected record counts (`call360`)

| Table | Rows | Table | Rows |
|---|---|---|---|
| party | 320 | script_section | 20 |
| contact_method | 589 | question_bank_item | 13 |
| policy | 230 | question_revision | 13 |
| policy_party_role | 1028 | module_question | 17 |
| fsc_representative | 24 | script_assignment_rule_version | 4 |
| sale_event | 250 | script_assignment | 245 |
| policy_fact_snapshot | 250 | regulatory_reference | 2 |
| external_reference | 824 | control | 5 |
| risk_rule_set_version | 2 | control_mapping | 11 |
| risk_assessment | 290 | callback_case | 250 |
| risk_factor_result | 490 | case_hold | 12 |
| script_family | 2 | case_contact_selection | 364 |
| script_module | 5 | contact_attempt | 400 |
| script_version | 5 | conversation_session / survey_run | 80 / 80 |
| question_execution / answer_observation | 533 / 533 | rule_evaluation | 417 |
| finding | 24 | case_event | 1607 |

Unchanged:
- **Principals:** 2 (`dev.admin`, `dev.user`).
- **Market:** `SG` and `MY`, still version 1.
- **Feature flags:** 4, all disabled.
- **Tables:** 55, that is 54 plus `alembic_version`.
- **Governed lists:** each has version 1 ACTIVE.

## 9. Audit-chain integrity

```sh
cd ~/Documents/Work/Projects/Call360/Call360/Call360-backend
uv run call360 audit-verify                  # expect OK with 29 events
psql -h localhost -U Call360_db_user -d Call360_db -v ON_ERROR_STOP=1 -c \
  "SELECT row_hash FROM call360.audit_event ORDER BY seq OFFSET 4 LIMIT 1"   # expect 289d4029… (pre-deployment head)
psql -h localhost -U Call360_db_user -d Call360_db -v ON_ERROR_STOP=1 -c \
  "SELECT action, count(*) FROM call360.audit_event GROUP BY action ORDER BY action"
```

The 29 events are the 5 earlier ones unchanged, plus 24 new ones:
- 9 `CONFIG.CODE_LIST_VERSION_ACTIVATED`;
- 12 `CASE.HOLD_PLACED`;
- 2 `CASE.HOLD_RELEASED`;
- 1 `SEED.MANIFEST`.

## 10. Readiness and regression

```sh
cd ~/Documents/Work/Projects/Call360/Call360/Call360-backend && make dev     # terminal A
curl -s http://127.0.0.1:8000/health/ready                                   # terminal B: {"status":"ok"}
cd ~/Documents/Work/Projects/Call360/Call360/Call360-backend && make test lint typecheck contract-check secret-scan   # test schema only
cd ~/Documents/Work/Projects/Call360/Call360/Call360-frontend && npm run lint typecheck test api:check build secret-scan e2e
```

Then sign in as `dev.admin` and `dev.user`:
- **Users:** shows both accounts.
- **Configuration:** shows `market` and the nine governed lists at version 1.
- **Audit:** shows the deployment events, fitting the screen.
- **USER account:** still gets 403 on Administration.

## 11. Recovery

| Failure | Action |
|---|---|
| A migration fails | That revision is rolled back. `uv run alembic current` shows the last good revision; fix and re-run `make migrate`. Before any seed, `uv run alembic downgrade 0002_config_foundation` returns to 0002 (0007's downgrade audits the removal and refuses if CP0.2 rows exist) |
| The seed fails | Single transaction: nothing is written. Fix and re-run `make seed CONFIRM=call360` |
| Keys missing or changed | The app refuses to start, readiness is 503 and the seed refuses (D-34). Restore from `"$BK/env.post_keys"` (step 4b) and re-check step 7. Never generate new keys once data exists |
| Full rollback after seeding (owner decision) | **Non-destructive by design: nothing is dropped.** Stop servers, then set the failed schema aside and restore the backup beside it: (1) `(cd "$BK" && shasum -a 256 -c SHA256SUMS)`; (2) `psql -h localhost -U Call360_db_user -d Call360_db -v ON_ERROR_STOP=1 -c "ALTER SCHEMA call360 RENAME TO call360_failed_<STAMP>"`; (3) `pg_restore -h localhost -U Call360_db_user -d Call360_db -n call360 --exit-on-error "$BK/call360.dump"`; (4) re-run step 1 (expect `0002`, 21 tables, 2 principals, audit head `289d4029…`). The application can only address `call360`/`call360_test`, so the renamed schema is inert. Dropping it later is a separate, explicit owner decision. Keep the current `.env` (it holds the rotated password); the backend at head reports `not_ready` on a 0002 schema, which is expected |
| Rotation problem | Set the password again with `\password` and re-run `make_env.py --force`. If the keys already existed, apply step 4b and step 7 immediately afterwards |

After acceptance:
- delete `"$BK/env"`, which holds the old password;
- keep `env.post_keys`, the dump and `SHA256SUMS` until S0 is accepted.

## 12. Safety review record (2026-11-15)

| Question | Finding | Correction |
|---|---|---|
| Does `make_env.py --force` change developer logins or other secrets? | It does not change logins, JWT keys or `.env.local`. It regenerates the pepper and CSRF secret (sessions sign out) and **deletes PII keys if present** | §3 table and rule; rotation before keys; step 4b restore; step 7 check |
| Could it overwrite configuration the running app needs? | It writes the same 13 settings; the app reads `.env` only at start-up | Servers are stopped in step 0; the restart happens in step 10 |
| Can the backup and original `.env` be recovered together? | The earlier version backed up only the dump and `.env`, with mixed working directories | One stamped set: dump, `env`, `env.local`, `secrets`, `env.post_keys` and `SHA256SUMS`; pairing rules in step 2 |
| Do the keys stay stable after seeding? | `make_data_keys.py` never overwrites; the only risk is `make_env.py --force` | `env.post_keys` copy; step 7 key-id check against the `SEED.MANIFEST`; a seed re-run refuses on an HMAC change |
| Can rollback drop the development schema automatically? | The earlier version used `DROP SCHEMA call360 CASCADE` | Replaced by a rename plus `pg_restore -n call360 --exit-on-error`; nothing is dropped |
| Are the commands protected against the wrong schema? | Alembic and the seed are guarded; the shell environment could point at `.env.test` | `unset CALL360_ENV_FILE` plus a settings preflight (step 1); `-n call360`, `-d Call360_db` and `ON_ERROR_STOP` on every psql/pg command |
