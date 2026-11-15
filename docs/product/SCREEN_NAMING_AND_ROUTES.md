# Call360 — Product terminology and screen/route contract

**Status:** binding for implementation from spec v0.3 | **Owner:** S&C Product Owner (proposed)

## Approved terminology for this project

| Concept | Use in the UI | Do not use as UI label | Domain meaning |
|---|---|---|---|
| Entire platform | **Call360** | Call 360, AIA Callback Platform | Product identity (formal: AIA Call360 pending brand review) |
| Case investigation view | **Call Detail** | Call 360, Call360 Detail, 360 Call | Case-centric investigation across multiple attempts/sessions |
| Searchable all-calls register | **Call Explorer** | Call 360 | Find/filter cases, attempts, sessions |
| Business dashboard | **Overview** or **Command Centre** | Call Detail | Aggregate monitoring and work queues |
| Browser full-duplex simulator | **Voice Studio** | Genesys Call | Browser-only test session at S1 |
| Governed survey editor | **Survey Studio** | AI Prompt Editor | Draft, validation, approval, publish |
| Human case handling | **Review Workbench** | AI Verdict | Evidence-backed reviews and disposition |

**Never conflate these domain objects:** callback case (obligation), contact attempt (dial/test attempt), conversation session (connected media), survey run (script execution), structured answer (extraction), compliance decision (controlled review result).

## Canonical React navigation and deep links

| Screen | Canonical route | First live stage | Notes |
|---|---|---|---|
| Overview | `/` | S0 | KPI links preserve filters |
| Call Explorer | `/calls` | S0 | Case-first register with expandable attempt/session |
| **Call Detail** | `/cases/:caseId` | S0 | Header uses `Call Detail` + case reference, e.g. `CB-10242` |
| Call Detail attempt/session focus | `/cases/:caseId?attempt=<id>&session=<id>` | S0/S1 | Deep link to a sub-record; validate both belong to case |
| Voice Studio | `/voice-studio` | S0 preflight, S1 functional | Browser channel only |
| Surveys / Survey Studio | `/surveys` and `/surveys/:surveyId` | S0 read-only, S2 editing | Version-specific links |
| Review Workbench | `/reviews` | S0 list, S3 action | Drill into Call Detail evidence |
| Live Monitor | `/monitor` | S4 | Earlier stage may provide clearly labelled non-live preview only |
| Campaigns | `/campaigns` | S4 | No real dialing before S6 |
| Analytics | `/analytics` | S4 | Definitions reconciled to case/attempt counts |
| Administration | `/admin` | S0 health/roles; S5 enterprise | Permission controls |

The `/calls` register is intentionally named for user familiarity, but **`/cases/:caseId` is case-centric**. `GET /api/v1/cases/{case_id}` is independent of UI navigation. Deep links should survive refresh, back navigation and permission checks. Changing public routes requires an ADR, redirects and integration tests.

## Screen acceptance checks

1. Product header and browser title say **Call360**; no screen title or breadcrumb says “Call 360”.
2. Clicking a Call Explorer result, dashboard risk card or review item opens **Call Detail** with preserved source filters.
3. Call Detail displays the case plus **all** attempts (including no-answer) and optional sessions (including partial/disconnected), without fabricated media.
4. A recording/transcript button is disabled with a clear reason when an artifact is absent or unauthorised; no silent empty player.
5. Data availability, dates and KPI denominators come from authenticated backend responses.
6. UX copy uses “AI-flagged concern” or “needs review” until human disposition; never assert final mis-selling from model output alone.
