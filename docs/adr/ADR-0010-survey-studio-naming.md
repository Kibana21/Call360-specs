# ADR-0010: Survey Studio naming; Script Studio as a transitional name

**Status:** Approved by the owner, 2026-11-21 (decision D-113; proposed as SS-D-20 in the Survey Studio decision register).
**Amends:** ADR-0007 §1 (naming) only. ADR-0007 §2 (script version lifecycle) and §3 (stage application) are unchanged.
**Narrows:** exception EXC-001 in `docs/spec/APPROVED_EXCEPTIONS.md` (the product-name part no longer applies; the legacy path part still does).
**History preserved:** ADR-0007 keeps its original text. Owner decision D-2 (2026-11-15) is not deleted; this ADR records its reversal for the product name.

## Context

ADR-0007 (D-2, 2026-11-15) named the governed script editor **Script Studio** and prohibited "Survey Studio" as a UI
label, because the specification pack then used both names for one screen. On 2026-11-21 the owner commissioned a new
authoring product from the Survey Studio PRD (`docs/product/survey-studio/PRD_v1.1.md`): surveys assembled from
reusable modules, with questions, routing and conditions. Its vocabulary — survey, module, question — is the business
user's vocabulary, and the owner decided that the new product carries the name the BRD originally used.

## Decision

1. The governed authoring product is **Survey Studio**: navigation label, page titles, breadcrumbs, accessible names
   and test names.
2. **Script Studio** remains the label of the existing linear script screens for the transition period only. It is
   removed when the owner retires those screens.
3. **Wording & Delivery** is the name of the capability inside Survey Studio that governs customer-facing wording and
   delivery modes. It is not a separate product and not a second question master.
4. UI routes: `/survey-studio…`. Existing `/scripts…` routes keep working. The legacy survey UI routes named in
   EXC-001 remain client redirects only.
5. API: new routes, when authorised, live under the `survey-studio` prefix of the versioned API. Existing script
   routes are unchanged. The legacy survey API paths named in EXC-001 remain unused and prohibited.
6. Domain and database names (`script_family`, `script_version`, `survey_run`, …) are unchanged. UI vocabulary:
   Survey, Module, Question, Option, Condition, Outcome.
7. `SUR-*` and `SCR-*` requirement IDs are unchanged. `SS-*` requirement IDs live in the Survey Studio PRD.
8. Until Survey Studio is enabled by its feature setting, the label does not appear in the product; the existing
   screens and labels are unchanged.

## Consequences

- `scripts/validate_specs.py` no longer treats "Survey Studio" as a prohibited term. The other four prohibited terms
  are unchanged, and the validator additionally checks that this ADR and the EXC-001 amendment are present. No file or
  directory is exempted from terminology checks.
- `docs/spec/APPROVED_EXCEPTIONS.md`: EXC-001 is amended in place with a dated note; the six allowlist rows for the
  retired term are moved to a history table.
- `docs/product/SCREEN_NAMING_AND_ROUTES.md` and `docs/acceptance/S0_TEST_MATRIX.md` (E2E-18) are updated.
- Frontend tests that assert the absence of the label (`e2e/auth.spec.ts`, `src/App.test.tsx`) stay valid while the
  feature setting is off; a test for the setting-on state is added with the prototype (SS-02A).
- The master BRD and the requirements register are not edited.

## Alternatives considered

- **Keep D-2** and ship the new product as "Script Studio": rejected by the owner; the product is about surveys,
  modules and questions, not scripts.
- **Exempt the Survey Studio documents from the terminology check**: rejected; blanket exemptions hide real
  violations.
