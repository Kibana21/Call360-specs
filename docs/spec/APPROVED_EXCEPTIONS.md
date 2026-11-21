# Call360 — Approved exceptions and legacy-term register

**Status:** CP0.0 draft, 2026-11-15 · **Owner:** S&C Product Owner (proposed)
**Purpose:** The master BRD (`01_MASTER_BRD.md`) and the requirements register (`03_REQUIREMENTS_REGISTER.csv`) are **deliberately not rewritten**. When an owner decision changes how a BRD statement applies, the change is recorded here as an explicit exception rather than by silent edit. `scripts/validate_specs.py` reads the tables below. A legacy term found in a file that has no row for that term fails validation.

## 1. Approved exceptions to unchanged source text

An exception means the source text stays as written, and the decision named here takes precedence over it for the stated scope only. No other BRD statement is overridden.

| Exception | Source text kept unchanged | Location | Precedence decision | Scope of override | Approved |
|---|---|---|---|---|---|
| EXC-001 | "Survey Studio" as the name of the script editing environment; `/surveys` UI routes; `GET /surveys`, `/api/v1/surveys` API paths | BRD "Product identity" bullet 3, BRD §4.4 "Script Library / Script Detail" bullet, BRD §7.3, execution plan §C S0 "Suggested API slices" and §B item 4 | ADR-0007: the UI module is **Script Studio**. Routes are `/scripts…`, with `/surveys…` as redirects. API and domain use `scripts` / `script_*` | Naming and paths only. `SUR-*` requirement IDs, their wording and their acceptance criteria still apply in full, to Script Studio | Owner decision D-2 (2026-11-15); C-26 decision 6 (2026-11-15) **Amended 2026-11-21 by ADR-0010 (owner decision D-113):** the product-name part of this exception is withdrawn — the new authoring product is named Survey Studio, as the BRD says; the existing linear script screens keep the label Script Studio during the transition. The path part is unchanged: legacy survey UI routes are redirects only and the legacy survey API paths remain unused. |
| EXC-002 | Script approval lifecycle `DRAFT → VALIDATION_FAILED/VALIDATED → SUBMITTED → APPROVED → PUBLISHED → RETIRED` | BRD §6.2; execution plan §B "4+ survey versions (including retired and draft)" | ADR-0007: lifecycle is `DRAFT, SUBMITTED_FOR_REVIEW, APPROVED, SCHEDULED, PUBLISHED, SUPERSEDED, WITHDRAWN`. Validation is a draft attribute (`validation_status`), not a state. "Retired" maps to SUPERSEDED (replaced) or WITHDRAWN (pulled) | Lifecycle vocabulary only. BRD §6.2 rules (only drafts editable, publish creates an immutable content-addressed artifact, no retroactive change to old runs) remain binding | Owner decision C-4 (2026-11-15) |
| EXC-003 | Primary navigation list `Overview, Call Explorer, Live Monitor, Work Queues, Surveys, Campaigns, Analytics, Evaluations, Administration` | BRD §4.1 bullet 2; SEARCH_WORKSPACE "Suggested primary navigation" (superseded wording updated in that doc) | ADR-0008 §3 / `SCREEN_NAMING_AND_ROUTES.md`: the approved HTML mockup's grouped navigation structure, with canonical spec terminology | Navigation grouping, order and labels only. Every BRD screen remains reachable or stage-gated | Owner decision C-1 (2026-11-15) |

## 2. Legacy-term allowlist (validator input)

The validator treats each term below as **prohibited**. It may appear only in the files listed in that term's rows. `Kind` is either:
- `EXCEPTION`: the text is deliberately unchanged under an entry in §1;
- `REFERENCE`: the file cites the term as prohibited, legacy or historical (for example "do not use", a changelog, a decision record).

The register file itself is always allowed.

| Term | File | Kind | Basis |
|---|---|---|---|
| `GET /surveys` | docs/spec/01_MASTER_BRD.md | EXCEPTION | EXC-001 |
| `/api/v1/surveys` | docs/spec/02_CLAUDE_CODE_EXECUTION_PLAN.md | EXCEPTION | EXC-001 |
| `/api/v1/surveys` | docs/acceptance/CP0.0.md | REFERENCE | Decision log |
| `/api/v1/surveys` | docs/adr/ADR-0007-script-studio-naming-and-lifecycle.md | REFERENCE | Decision record |
| `VALIDATION_FAILED/VALIDATED` | docs/spec/01_MASTER_BRD.md | EXCEPTION | EXC-002 |
| `VALIDATION_FAILED/VALIDATED` | docs/adr/ADR-0007-script-studio-naming-and-lifecycle.md | REFERENCE | Decision record |
| `Call 360` | docs/spec/01_MASTER_BRD.md | REFERENCE | Binding prohibition statement |
| `Call 360` | docs/adr/ADR-0002-product-and-detail-terminology.md | REFERENCE | Historical ADR |
| `Call 360` | docs/product/SCREEN_NAMING_AND_ROUTES.md | REFERENCE | "Do not use as UI label" column and screen checks |
| `Call 360` | docs/product/SEARCH_WORKSPACE_AND_POLICY_VIEWS.md | REFERENCE | Prohibition statement |
| `Call 360` | docs/product/S0_SCREEN_SPEC.md | REFERENCE | Negative label assertion |
| `Call 360` | docs/acceptance/S0_TEMPLATE.md | REFERENCE | Negative label assertion |
| `Call 360` | docs/acceptance/S0.md | REFERENCE | Negative label assertion |
| `Call 360` | docs/acceptance/S0_TEST_MATRIX.md | REFERENCE | Negative label assertion in E2E-18 |
| `Call 360` | CHANGELOG.md | REFERENCE | Change history |

## 3. Extensions that do not override source text

These add to the BRD without contradicting it, so they need no exception. They are listed so reviewers can see them.

| Extension | Adds | Basis |
|---|---|---|
| EXT-001 | Auditable case holds (`case_hold`; blocking holds prevent a case becoming callable), orthogonal to the BRD §3.1 case states. The case states are unchanged | Owner decision C-12; ADR-0008 |
| EXT-002 | API evidence-availability object (`AVAILABLE`, `NOT_AVAILABLE`, `FAILED`, `RESTRICTED`) alongside the unchanged BRD §3.3 media and transcript enums | C-10; ADR-0006 |
| EXT-003 | Per-KPI eligibility, materiality, SLA-exemption and cohort rules that refine BRD §10 without changing its numerators or denominators | Owner decisions K-1 to K-4; `docs/product/S0_KPI_DEFINITIONS.md` |

## 3. Retired prohibitions (history; not validator input)

Kept so the decision history is not lost. The validator no longer scans for these terms.

| Retired term | Retired on | Basis | Former allowlist (file · kind · basis) |
|---|---|---|---|
| Survey Studio (as a prohibited UI label) | 2026-11-21 | ADR-0010, owner decision D-113, reversing the naming part of D-2 / ADR-0007 §1 | docs/spec/01_MASTER_BRD.md · EXCEPTION · EXC-001; docs/adr/ADR-0002-product-and-detail-terminology.md · REFERENCE · Historical ADR, amended by ADR-0007; docs/adr/ADR-0007-script-studio-naming-and-lifecycle.md · REFERENCE · Decision record; docs/product/SCREEN_NAMING_AND_ROUTES.md · REFERENCE · "Do not use as UI label" column; docs/acceptance/CP0.0.md · REFERENCE · Decision log; docs/acceptance/S0_TEST_MATRIX.md · REFERENCE · Negative label assertion in E2E-18 |
