# Call360 — Stage 0 screen specification

**Status:** CP0.0 draft, 2026-11-15. Normative for CP0.1A (shell, auth screens, Users and Audit), CP0.1B (remaining admin screens) and CP0.4/CP0.5 (screens)
**Visual reference:** `Call360-frontend/docs/design/reference/Call360_Portal_Mockup.html` and its screenshots. They govern layout, visual hierarchy and interaction patterns (owner decision D-3).
**Binding terminology and routes:** `SCREEN_NAMING_AND_ROUTES.md`. The route table in §2 must equal the route table there; the validator checks this.
**Requirements:** APP-001…006, CASE-001, SUR-001, PARTY-005, POL-004, RISK-002/005, SCR-001…005, ING-002/004, SEARCH-001…007, IAM-001/010, ADMIN-001, REG-001/002

## 1. Rules for every screen

1. **Data.** Every value comes from an authenticated API response; there are no hard-coded metrics or records. Where seeded synthetic evidence is shown, the screen carries the seeded label (ADR-0008 §4).
2. **Five states.** Every data region designs and tests the following (FE-01):
   - **loading:** a skeleton, with a cancellable request;
   - **empty:** an explanation and the next action;
   - **error:** the message, the correlation ID and a retry;
   - **partial:** a badge naming the region that failed while the others render;
   - **forbidden:** a 403 notice, without revealing whether the object exists.

   A 404 from a scoped object shows "Not found or not available to you".
3. **Controls.** Every visible control works against the backend. A later-stage control is disabled, shows a stage chip ("Stage S2 — Script authoring"), and has an `aria-describedby` explanation. No inert buttons (S0-A6).
4. **Permissions.** The UI hides or disables actions the caller lacks permission for (from `/me`). The backend is still authoritative.
5. **Terminology.**
   - The browser title and header say **Call360**.
   - The case investigation screen heading and breadcrumb say **Call Detail**.
   - The script area says **Script Studio**.
   - The label "Call 360" never appears.
6. **Masking.** Party names and contacts are displayed exactly as masked by the server. There is no unmask control in S0.
7. **Navigation state.** Filters, sort and cursor live in the URL. Back, forward and refresh restore the same view. Deep links validate ownership: `?attempt=`, `?session=` and `?sale=` must belong to the parent object, or the screen shows a clear mismatch error.
8. **Accessibility.**
   - Keyboard reachability and visible focus.
   - Headings in order.
   - Labelled controls.
   - Colour is never the only signal; status uses text or icon plus colour.
   - WCAG 2.2 AA contrast.
   - Zero serious or critical axe violations.
9. **Layouts.** Verified at 1280 px and 1440 px desktop widths (S0-A7). Narrower widths degrade gracefully, with no clipped text or scroll traps.
10. **Global banners.**
    - "Synthetic data — local demo" shows in the shell, from `/me.environment`.
    - The disabled-stage chips use one consistent style.

## 2. Route and screen table

| Screen | Route | Nav group | S0 status | Primary APIs | Mockup reference |
|---|---|---|---|---|---|
| Login | `/login` | — | Live | API-003, API-004 | `Call360_Portal_Login.png` |
| Session expired | `/session-expired` | — | Live | API-005 | Login layout |
| Unauthorized | `/unauthorized` | — | Live | — | Mockup notice style |
| Overview (Command Centre) | `/` | WORKSPACE | Live | API-030…034 | `Call360_Portal_Overview.png` |
| Call Explorer | `/calls` | WORKSPACE | Live | API-035, API-036, API-072…075 | Mockup "Call Explorer" |
| Call Detail | `/cases/:caseId` | — (from records) | Live | API-037…047 | `Call360_Portal_Call_Detail.png` |
| Policy Explorer | `/policies` | WORKSPACE | Live | API-050, API-072…075 | Mockup "Policy & Sales" |
| Policy Detail | `/policies/:policyId` | — (from records) | Live | API-051…055, API-037 | `Call360_Portal_Policy_Profile.png` |
| SBQ Risk Workbench | `/risk-assessments` | WORKSPACE | Live (read-only) | API-056…058 | Mockup "Risk Assessment" |
| Work Queues | `/queues` | WORKSPACE | Live (read-only) | API-076 | Mockup "Callback Queue" |
| Voice Studio | `/voice-studio` | WORKSPACE | Preflight (NOT_AVAILABLE) | API-078 | `Call360_Portal_Voice_Demo.png` (layout only) |
| Live Monitor | `/monitor` | WORKSPACE | Disabled (S4) | — | Mockup "Live Monitor" (not built) |
| Campaigns | `/campaigns` | WORKSPACE | Disabled (S4) | — | — |
| Script Studio | `/scripts` | GOVERNANCE | Live (read-only) | API-060 | `Call360_Portal_Script_Studio.png` |
| Script family | `/scripts/:scriptFamilyId` | — | Live (read-only) | API-061, API-062 | Script Studio |
| Script version | `/scripts/:scriptFamilyId/versions/:scriptVersionId` | — | Live (read-only) | API-063, API-066 | `Call360_Portal_Script_Draft.png` (read-only rendering) |
| Assignment Rules | `/assignment-rules` | GOVERNANCE | Live (read-only) | API-064 | Mockup "Assignment Rules" |
| Review Workbench | `/reviews` | GOVERNANCE | Live (list only) | API-077 | Mockup "Compliance Reviews" |
| Search | `/search` | INTELLIGENCE | Live | API-070, API-071 | Mockup "Universal Search" |
| Analytics | `/analytics` | INTELLIGENCE | Disabled (S4) | — | Mockup "Analytics & Reports" (not built) |
| Data Intake | `/intake` | PLATFORM | Live (ADMIN) | API-080…086, API-027 | Mockup "Data Integrations" |
| Administration | `/admin` | PLATFORM | Live (ADMIN) | API-010…026 | Mockup "Administration" |
| Admin: Users | `/admin/users` | — | Live (ADMIN) | API-010…013 | Administration |
| Admin: Groups | `/admin/groups` | — | Live (ADMIN) | API-014…018 | Administration |
| Admin: Sessions | `/admin/sessions` | — | Live (ADMIN) | API-019, API-020 | Administration |
| Admin: Audit | `/admin/audit` | — | Live (ADMIN) | API-021 | Administration "audit" tab |
| Admin: Configuration | `/admin/config` | — | Live (ADMIN) | API-022…025 | Administration |
| Admin: Integrations | `/admin/integrations` | — | Live (ADMIN) | API-027 | Mockup "Data Integrations" |
| Admin: System health | `/admin/system` | — | Live (ADMIN) | API-026 | Overview "Platform health" card |

**Legacy redirects:** `/surveys` → `/scripts` and `/surveys/:id` → `/scripts/:id` (ADR-0007).

## 3. Screen details

### Overview (Command Centre): APP-002, APP-004

- **Interim (CP0.1A until CP0.5):** `/` shows only real authenticated-session information from `/me`: display name, roles, permissions, session expiry and the environment banner. It shows no metrics, charts or sample records.

- **Content:**
  - mockup header;
  - KPI cards OPS-01, OPS-02, KPI-03, OPS-04, OPS-05;
  - callback activity trend (API-031);
  - risk distribution (API-034);
  - priority attention table (API-032);
  - recent activity (API-033);
  - end-to-end recent cases (API-035, limit 5);
  - platform health card (ADMIN: API-026; USER: hidden).
- **Interactions:**
  - Each card and chart segment links to its typed drilldown route, which opens Call Explorer with the identical filter.
  - Each card has an info popover showing the definition, numerator, denominator, exclusions, cohort, time zone and "as of".
  - The `NOT_MEASURED` KPIs (recording and transcript integrity) render as "Not measured until Stage S1".
  - An outcome-distribution panel (KPI-15) shows Verified compliant, Verified with findings, Not verified, Cancelled and Open. SLA breach is shown as a separate timeliness indicator, never as an outcome. The labels never say "non-compliant" (S0_KPI_DEFINITIONS §1).
- **Disabled:**
  - "Export report": Stage S4 — Export.
  - "New callback case": disabled with the note "Cases are created through Data Intake in Stage 0", linking to `/intake` for ADMIN.
- **Deviation:** the mockup's "Survey completion = completed / connected" is relabelled to the BRD definition, completed / started.

### Call Explorer: APP-003…006, SEARCH-002, SEARCH-004, SEARCH-005

- **Register:** case-first, with a grain switch (`case`, `attempt`, `session`).
- **Columns:**
  - case ref, policy ref (masked customer), product (ILP chip), effective risk band;
  - state, plus hold chip(s) and a callable indicator;
  - attempts count, latest attempt status, due date, script version;
  - evidence availability, synthetic badge.
- **Filtering and paging:**
  - Facets as in API-035, with combinable chips.
  - Sortable columns; cursor pagination ("Load more" or next/previous), stable across pages.
  - Saved views: save, rename, delete and apply, own views only. The URL is shareable, but opening it as another user applies only the filters, never that user's view record.
- **Interactions:** a row opens Call Detail and preserves the explorer URL for the breadcrumb back link.
- **Disabled:**
  - "Export": Stage S4;
  - "Bulk assign": Stage S4.

### Call Detail (`/cases/:caseId`): APP-003, CASE-001, PARTY-005, RISK-005, SCR-004

- **Sticky header:**
  - "Call Detail" with the case ref;
  - outcome category and the SLA indicator, shown separately;
  - state, holds, callable status, due, owner, priority;
  - effective SBQ band with origin and version.
- **Left column:**
  - **all attempts timeline**, including no-answer, busy and failed, each with time, status and masked contact snapshot;
  - selecting an attempt or session updates `?attempt=&session=`;
  - question navigator for the selected session's survey run.
- **Centre:**
  - Recording panel: **"Recording not available — no audio is captured before Stage S1"** (`NOT_AVAILABLE`), with no seek bar and no play control.
  - Transcript panel: **"Transcript not available — transcripts are captured from Stage S1"** (`NOT_AVAILABLE`). Seeded answers are shown on the right, labelled as seeded synthetic examples.
- **Right column:**
  - policy fact snapshot (pinned, with hash), contact party and role (masked);
  - pinned script version with manifest hash, plus "Why this script" (rule trace from API-039);
  - per question: expected-answer policy → observed answer → rule result → evidence pointers, all labelled seeded synthetic;
  - findings with severity, status and origin.
- **Bottom:** event timeline (API-040).
- **Disabled:**
  - "Start browser call": Stage S1;
  - "Assign reviewer" and "Add review decision": Stage S3;
  - "Evidence bundle": Stage S3/S4.
- **Deviations:** the mockup's "Pass/Discrepancy" verdict wording becomes "Seeded rule outcome: MATCH / MISMATCH — needs review"; the simulated player is replaced by the explicit NOT_AVAILABLE panel.

### Policy Explorer and Policy Detail: POL-004, PARTY-001/005, RISK-002/005, SCR-004, C-3

- **Explorer:** columns per SEARCH_WORKSPACE (masked owner and insured, product, ILP, premium and currency, FSC, sale date and channel, effective risk, script, latest case state), facets and saved views.
- **Detail header:** policy vs sale identity, source and as-of for each material field (POL-005), market.
- **Workspaces (tabs, `?tab=`):**
  - `sale` (**Sale Context**; a specific sale via `?sale=<saleEventId>`, which must belong to the policy; this view is the "Sale Detail" referenced in S0 acceptance, per C-3);
  - `parties` (Party & Contact: role edges without duplicating a person, masked contact cards, eligibility result and reason);
  - `risk` (SBQ Risk history with supersedes chain);
  - `script` (Script Assignment with rationale);
  - `cases` (Callback History, linking to Call Detail);
  - `source` (Source & Changes: `field_change` lineage).
- **ADMIN actions:** "Correct field" opens a correction form (API-086) with reason and source reference, showing before and after.
- **Disabled:** "Request risk override": Stage S2.

### SBQ Risk Workbench: RISK-001…006

- **List and facets:** band, factor, origin (`SOURCE_ASSIGNED`, `RULE_ASSESSED`, `MANUAL`), rule-set version, product, channel, FSC, status.
- **Detail drawer (`?assessment=`):**
  - factors as typed values with human-readable labels from the code list;
  - input snapshot hash, rule-set version (labelled "Synthetic rule set — not AIA-approved"), source original value, supersedes chain.
- **Separation:** a persistent explainer states that SBQ selection risk is not investment suitability (shown separately in Policy Detail facts) and not finding severity.
- **Score:** shown only when stored (C-17).
- **Disabled:** "Recalculate" and "Override": Stage S2.

### Work Queues

- **Read-only queue tabs:** due today, overdue, awaiting callback, on hold (by reason), each linking to Call Detail.
- **Disabled:** "Launch browser session" (mockup Callback Queue): Stage S1; "Assign": Stage S4.

### Voice Studio

- **Preflight layout from the mockup:**
  - API-078 status `NOT_AVAILABLE` with its reason;
  - the microphone check is **not** requested (Permissions-Policy denies microphone in S0);
  - start, mute and stop are disabled with "Stage S1 — Browser voice";
  - the "TEST MODE" banner is shown.
- **Deviation:** no simulated conversation.

### Script Studio, script family and script version: SUR-001, SCR-001…003, SCR-005, REG-001/002

- **Library:** filters for product, risk band, channel, status (all seven lifecycle statuses), effective date and language. It lists published versus draft revisions (SCR-003).
- **Version view, read-only:**
  - ordered sections (COMMON, PRODUCT, RISK modules), with question count and a question navigator (SUR-001);
  - per question: code, intent, exact wording, delivery mode, answer type, mandatory flag, expected-answer policy with acceptable variants and unacceptable outcomes (SCR-002: YES is not automatically compliant), controls, and optional public regulatory reference, visually distinct from the AIA control (REG-002);
  - manifest hash, status, effective dates, author and reviewer references, change log;
  - a "Synthetic — not approved AIA/MAS wording" banner on every version.
- **Disabled:** "New draft", "Edit", "Submit", "Approve", "Publish", "Diff", "Simulate": Stage S2.
- **Deviation:** the mockup's editable draft screen is rendered read-only.

### Assignment Rules

- **Content:** read-only list of seeded `script_assignment_rule_version` rows (predicate, priority, specificity, target version, effective dates, status), with links to the cases that use each rule.
- **Disabled:** toggles and edits: Stage S2.

### Review Workbench

- **Content:** read-only list of seeded findings awaiting review (API-077), linking to the Call Detail finding.
- **Disabled:** "Confirm", "Reject", "Request info", "Assign" and "Send to checker": Stage S3.

### Search: SEARCH-001, SEARCH-003, SEARCH-006, SEARCH-007

- **Global search box** in the shell (⌘K/Ctrl+K) with typed suggestions (API-071), plus the full results page.
- **Each hit shows:** entity-type icon, masked display, matched field, match kind (exact, prefix or fuzzy), and its typed route.
- **Results:** grouped by entity type, with no counts beyond the caller's scope.

### Data Intake (ADMIN): ING-001…004, POL-007

- **Sources panel:** MOCK_API available; BULK and INTERNAL_API shown as "Not available in Stage 0".
- **Mock sync:** "Run mock sync" triggers a real HTTP import (API-081) and shows reconciliation counts. Running it again shows the idempotent result.
- **Manual intake wizard:**
  1. policy;
  2. sale;
  3. parties and contacts;
  4. source risk (SOURCE or MANUAL, with factors and reason);
  5. preview (API-084): validation errors per field, duplicates, contact eligibility, "Script routing: not evaluated in Stage 0", holds that would apply;
  6. commit with reason and source reference (API-085), which navigates to Policy Detail and the new case's Call Detail.
- **Run history:** list of runs with per-item detail.
- **Deviation:** the mockup's "Simulate API sync" becomes a real mock sync.
- **CP0.4b portal (D-42):** the Manual Intake form (selects from API-087), preview, submit and run history are built first, on one page with a sticky preview/submit panel instead of a step-by-step wizard; mock sync, corrections and saved drafts are deferred. Existing-policy top-ups open from Policy Detail ("Add a sale") prefilled from the stored policy.

### Administration (ADMIN): IAM-010, ADMIN-001…004

- **Dashboard:** counts of users, groups, active sessions and recent audit events, plus system health.
- **Users:** create, enable or disable with reason, password reset.
- **Groups:** memberships, plus role and scope mappings with reason; reserved permissions are visibly not grantable.
- **Sessions:** list and revoke.
- **Audit:** search with before/after diff view.
- **Configuration:** code lists with version history; governed lists are read-only with "Business approval workflow arrives in a later stage"; feature flags with stage gates.
- **Integrations:** connector status.
- **System:** health, data policy, audit chain head, OpenAPI SHA.
- **USER access:** USER receives the Unauthorized screen, and the API returns 403.

### Login, Session expired, Unauthorized: IAM-001, IAM-002

- **Login:** mockup layout with username and password, the provider badge "Local demo identity — not SSO", and the demo-only banner. There is **no** role-switch or passwordless button.
- **Errors:** a single generic error message, and throttling feedback ("Too many attempts, try again later") on 429.
- **Session expired:** offers sign-in again and preserves the return path, as a validated, same-origin relative path.

## 4. Intentional deviations from the mockup (summary)

The frontend repo records them in `docs/design/DEVIATIONS.md` during CP0.5.

| # | Mockup | S0 implementation | Reason |
|---|---|---|---|
| DV-01 | Passwordless "Continue as Admin/User" | Username and password only | C-6 |
| DV-02 | Nav labels Policy & Sales, Risk Assessment, Callback Queue, Compliance Reviews, Universal Search, Analytics & Reports, Data Integrations | Policy Explorer, SBQ Risk Workbench, Work Queues, Review Workbench, Search, Analytics, Data Intake; Voice Studio and Campaigns added | C-1, EXC-003 |
| DV-03 | Numeric risk score "86/100" | Score only if stored with its synthetic rule set; band and factors always | C-17 |
| DV-04 | "Pass", "Discrepancy", "Compliance outcome" verdicts | "Seeded rule outcome — needs review" | C-18, SCREEN_NAMING check 6 |
| DV-05 | Simulated audio player and live voice animation | NOT_AVAILABLE panel; no animation | C-10, D-10 |
| DV-06 | Editable script draft, add question, submit for checker | Read-only version view; actions disabled (Stage S2) | D-4, S0 scope |
| DV-07 | "Simulate API sync" | Real mock HTTP import | ING-001 |
| DV-08 | "Export report", "Evidence bundle", "Create review" | Disabled with stage chip | S0-A6 |
| DV-09 | Survey completion = completed / connected | Completed / started (BRD §10) | D-12 |
| DV-10 | Illustrative KPI numbers | Live SQL values with definitions | APP-002 |
| DV-11 | Light-surface greys at 2.5–4.3:1 contrast | Minimally darkened to ≥ 4.5:1; hierarchy unchanged (recorded at CP0.1A) | WCAG 2.2 AA, rule 8 |
| DV-12 | Topbar search, notification bell, audit shortcut | Omitted until functional (search CP0.3; no notifications in S0) (recorded at CP0.1A) | S0-A6 no inert controls |
