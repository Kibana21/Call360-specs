# Call360 — Product terminology and screen/route contract

**Status:** binding for implementation from spec v0.3; amended in CP0.0 (2026-11-15) by ADR-0007 (Script Studio) and ADR-0008 §3 (navigation, owner decision C-1); amended 2026-11-21 by ADR-0010 (Survey Studio, owner decision D-113) | **Owner:** S&C Product Owner (proposed)

## Approved terminology for this project

| Concept | Use in the UI | Do not use as UI label | Domain meaning |
|---|---|---|---|
| Entire platform | **Call360** | Call 360, AIA Callback Platform | Product identity (formal: AIA Call360 pending brand review) |
| Case investigation view | **Call Detail** | Call 360, Call360 Detail, 360 Call | Case-centric investigation across multiple attempts/sessions |
| Searchable all-calls register | **Call Explorer** | Call 360 | Find/filter cases, attempts, sessions |
| Business dashboard | **Overview** (page title **Command Centre**) | Call Detail | Aggregate monitoring and work queues |
| Browser full-duplex simulator | **Voice Studio** | Genesys Call | Browser-only test session at S1 |
| Governed survey authoring product (ADR-0010) | **Survey Studio** | Script Studio (for the new product), AI Prompt Editor | Surveys built from reusable modules; questions, routing, conditions; shown only when its feature setting is on |
| Wording and delivery governance inside Survey Studio (ADR-0010) | **Wording & Delivery** | Script Studio | Customer-facing wording versions and delivery modes; a capability of Survey Studio, not a separate module |
| Existing linear script library and editor (transitional, ADR-0010) | **Script Studio** | AI Prompt Editor | Script families, versions, questions; draft, validation, approval, publish (S2). Label kept until the owner retires these screens |
| Human case handling | **Review Workbench** | AI Verdict, Compliance Reviews | Evidence-backed reviews and disposition |
| Policy register / dossier | **Policy Explorer** / **Policy Detail** | Policy & Sales, Policy 360 | Policy, sale events, parties, risk, script assignment, cases |
| Callback-selection risk view | **SBQ Risk Workbench** | Risk Assessment (as screen label) | SBQ callback-selection risk only; not suitability, not finding severity |
| Intake | **Data Intake** | Data Integrations | Mock API and manual synthetic intake (S0) |

**Never conflate these domain objects:** callback case (obligation), contact attempt (dial/test attempt), conversation session (connected media), survey run (one execution of a frozen script version), structured answer (extraction), compliance decision (controlled review result).

## Primary navigation (owner decision C-1)

The approved HTML mockup's grouped structure and order, with canonical terms (EXC-003). Disabled items are visible and focusable with a stage chip; their routes show a stage notice without data.

| Group | Items in order |
|---|---|
| WORKSPACE | Overview · Call Explorer · Policy Explorer · SBQ Risk Workbench · Work Queues · Voice Studio · Live Monitor *(S4, disabled)* · Campaigns *(S4, disabled)* |
| GOVERNANCE | Survey Studio *(when enabled, ADR-0010)* · Script Studio · Assignment Rules · Review Workbench |
| INTELLIGENCE | Search · Analytics *(S4, disabled)* |
| PLATFORM | Data Intake *(ADMIN)* · Administration *(ADMIN)* |

A persistent global search box (⌘K / Ctrl+K) sits in the top bar. **Call Detail**, Policy Detail and script version pages are reached from records, not from navigation.

## Canonical React routes and deep links

This table must list the same routes as `S0_SCREEN_SPEC.md` §2 (validator check).

| Screen | Route | First live stage | Notes |
|---|---|---|---|
| Login | `/login` | S0 | Local demo identity; OIDC in S5 |
| Session expired | `/session-expired` | S0 | Returns to a validated same-origin path |
| Unauthorized | `/unauthorized` | S0 | 403 for screens the caller lacks permission for |
| Overview | `/` | S0 | KPI links preserve filters |
| Call Explorer | `/calls` | S0 | Case-first register with expandable attempt/session |
| **Call Detail** | `/cases/:caseId` | S0 | Header uses `Call Detail` + case reference, e.g. `CB-2026-10482`. Attempt/session focus: `?attempt=<id>&session=<id>` (S0/S1); validate both belong to the case |
| Policy Explorer | `/policies` | S0 | Faceted, saved views |
| Policy Detail | `/policies/:policyId` | S0 | Workspaces via `?tab=`; Sale Context via `?sale=<saleEventId>` (must belong to the policy) — this is the S0 "Sale Detail" |
| SBQ Risk Workbench | `/risk-assessments` | S0 read-only, S2 overrides | Assessment drawer via `?assessment=<id>` |
| Work Queues | `/queues` | S0 read-only, S4 actions | — |
| Voice Studio | `/voice-studio` | S0 preflight, S1 functional | Browser channel only |
| Voice Lab | `/voice-lab` | S1-E.1 (experimental, mock providers only) | Isolated experiments; never operational |
| Live Monitor | `/monitor` | S4 | Disabled in S0; no non-live preview is built |
| Campaigns | `/campaigns` | S4 | No real dialing before S6 |
| Script Studio | `/scripts` | S0 read-only, S2 editing | Legacy `/surveys` redirects here |
| Script family | `/scripts/:scriptFamilyId` | S0 | Legacy `/surveys/:id` redirects here |
| Script version | `/scripts/:scriptFamilyId/versions/:scriptVersionId` | S0 | Version-specific links |
| Assignment Rules | `/assignment-rules` | S0 read-only, S2 editing | — |
| Review Workbench | `/reviews` | S0 list, S3 action | Drill into Call Detail evidence |
| Search | `/search` | S0 | Results page for the global search box |
| Analytics | `/analytics` | S4 | Definitions reconciled to case/attempt counts |
| Data Intake | `/intake` | S0 | ADMIN; mock API + manual |
| Administration | `/admin` | S0 health/roles; S5 enterprise | Permission controls |
| Admin: Users | `/admin/users` | S0 | — |
| Admin: Groups | `/admin/groups` | S0 | — |
| Admin: Sessions | `/admin/sessions` | S0 | — |
| Admin: Audit | `/admin/audit` | S0 | — |
| Admin: Configuration | `/admin/config` | S0 | — |
| Admin: Integrations | `/admin/integrations` | S0 | — |
| Admin: System health | `/admin/system` | S0 | — |

**Survey Studio routes (ADR-0010).** The new authoring product lives under the `survey-studio` path prefix and is registered only when its feature setting is on. It is outside the Stage 0 route contract in the table above, which is unchanged; its routes are specified in `docs/plans/survey-studio/` and will be added to a stage route contract when the programme's first production phase is authorised.

The `/calls` register is intentionally named for user familiarity, but **`/cases/:caseId` is case-centric**. `GET /api/v1/cases/{case_id}` is independent of UI navigation. Deep links should survive refresh, back navigation and permission checks. Changing public routes requires an ADR, redirects and integration tests.

## Screen acceptance checks

1. Product header and browser title say **Call360**; no screen title or breadcrumb says “Call 360”.
2. Clicking a Call Explorer result, dashboard risk card or review item opens **Call Detail** with preserved source filters.
3. Call Detail displays the case plus **all** attempts (including no-answer) and optional sessions (including partial/disconnected), without fabricated media.
4. A recording/transcript button is disabled with a clear reason when an artifact is absent or unauthorised; no silent empty player.
5. Data availability, dates and KPI denominators come from authenticated backend responses.
6. UX copy uses “AI-flagged concern” or “needs review” until human disposition; never assert final mis-selling from model output alone.
7. The existing linear script area is labelled **Script Studio** everywhere (navigation, titles, breadcrumbs, accessible names, tests). The new authoring product is labelled **Survey Studio** and appears only when its feature setting is on (ADR-0010).
