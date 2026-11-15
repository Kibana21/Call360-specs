# Call360 — Global Search, Policy 360 and Operational Workspaces

**Version 0.3 · UX + API business contract**

## Navigation and screen identity

**Product:** Call360. **Individual callback case investigation page:** **Call Detail** (`/cases/:caseId`), not “Call 360.” Policy context is displayed in `Policy Detail` (`/policies/:policyId`); never mix a policy identifier with a callback case identifier. Crosslinks preserve state and access checks.

Suggested primary navigation: **Overview**, **Call Explorer**, **Policy Explorer**, **SBQ Risk**, **Survey Studio**, **Data Intake**, **Review Workbench**, **Analytics**, **Administration**; Voice Studio and Live Monitor appear by applicable stage. The app has one persistent global search box with keyboard shortcut, recent authorized records and clear entity-type icons.

## Global Search coverage

| Entity | Search keys | Drilldown |
|---|---|---|
| Policy | Full or partial policy number, source ref, product type/subtype, status | Policy Detail |
| Customer/party | Permitted name, masked contact and authorized party ref | Policy Detail or Party Detail as approved |
| Sale | Sale event ref/date, channel/location, FSC ID, campaign | Sale tab within Policy Detail |
| SBQ risk | Band, factors, source, assessed period, overrides, rule version | Risk Workbench and associated policy |
| Callback case | Case ID, state, due date, owner, script, disposition, priority | Call Detail |
| Contact attempt/session | Attempt ID, session ID, channel, outcome, start/end, provider ID | Call Detail selected attempt/session |
| Script/question | Family/code/name, version, status, effective period, regulated-change ref | Script Library/version details |
| Findings/transcripts | Finding type/severity, approved full-text search over redacted transcript | Call Detail evidence interval |
| Operations | Import runs, exception IDs, failed media, audit actor/action and report | Matching workbench |

## Search behavior

- Default uses entity-filtered scoped matching; exact IDs highest rank, then prefix/substring and configured fuzzy matches. No user-visible unmasked sensitive data without policy authorization. Full contact numbers should not be generally searchable; if permitted, search via exact match over protected normalized token rather than exposing full values.
- Filter by market, product/ILP, risk band, selling channel/location, FSC, date range, case status, script family/version, contact status, evidence completeness, reviewer, outcome, provider and exception category.
- Search must apply object-level and attribute-based auth **before returning results, highlights, facets or counts**; malicious wildcard, SQL injection or unapproved transcript search cannot bypass scope.
- Server pagination, stable deterministic sort/cursor, total counts when authorized, 'as-of' time, filter chips, export-with-permission, saved search and deep-link navigation.
- Highlight matches only with safe escaped text; no rendering arbitrary HTML or raw transcripts. Audit sensitive searches/exports with principal, purpose, scope and correlation.
- Search can begin using PostgreSQL indexed keys and `pg_trgm`/full-text search with permission-aware joins; dedicated search engine is optional after real performance measurement. Avoid premature Elasticsearch dependency.

## Screen contracts

### Policy Explorer / Policy Detail

- List: policy reference, customer/insured masked labels, product subtype including ILP, premium band/currency, FSC, selling date/channel/location, callback-selection risk, assigned script and latest verification status.
- Detail header: policy vs sale identity, source and as-of, owner/insured/payer/contact roles, contact eligibility, history of sale events, versioned risk assessments and rationale, all verification cases.
- Lower workspaces: `Sale Context`, `Party & Contact`, `SBQ Risk`, `Script Assignment`, `Callback History`, `Source & Changes`.
- Show source/manual discrepancies side by side and who resolved them; never silently overwrite source facts. Distinguish risk assessment from final compliance finding.

### Call Detail

- Case header: sale ID, policy, verified contact party, callback reason, risk, risk reason, selected immutable script bundle and case state.
- Attempts: every attempt (including no-answer) with dispositions, timing, actor/channel and contact snapshot; sessions selectable without losing case context.
- Script: actual question execution status and exact script version. Present `expected answer rule → raw utterance → structured extraction → deterministic evaluation → human override` with independent provenance.
- Evidence: audio player with recording completeness state, aligned transcript and precise/approximate timestamp markers, applied redactions, technical timeline, artifacts and audit.
- Review: findings, severity, assigned reviewer, corrective actions, closure and approval history. Search hit deep-links to correct record and transcript segment.

### SBQ Risk Workbench

- Filters: risk band, contributing factors, products, FSC/channel/location, source/manual, scorer version, pending exception. Allow permissioned factor explanation and manual proposal with checker.
- Show risk assignment **before** survey, not merely inferred from the conversation. Select-risk view must include source data gaps, explanation and status.

### Admin

- Users, provider identity bindings, groups, group mappings, role permissions, auth sessions, script/risk governance approvals, integration adapters and audit events.
- `ADMIN`/`USER` group determines base navigation/access, not permission to approve own script or play any recording; enforce per-operation rights.

## Nonfunctional search acceptance

- Multi-tenant/market scope test: a restricted USER receives **zero matching rows and no leaked count or facet** for unauthorized policy and phone references.
- Stable paging: add new record while traversing pages; cursor or snapshot strategy prevents duplicate/omitted rows.
- Search across 250+ synthetic cases and linked policy/party/risk/script; median query target can be set after profiling but UX displays loading and cancellation immediately.
- Every result click lands in correct details with filter provenance and browser back/forward working.
