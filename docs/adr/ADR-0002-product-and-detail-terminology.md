# ADR-0002: Use Call360 for product and Call Detail for investigation

**Status:** Project naming selected by requester; formal AIA brand clearance pending  
**Amended by:** ADR-0007 (2026-11-15) — the script editor is named **Script Studio**; all other decisions below stand.  
**Date:** 2026-11-15

## Context

The original spec used “Call 360” for the central call-investigation screen. The selected application brand is **Call360**. Using the same phrase for both creates confusing navigation and ambiguous acceptance criteria.

## Decision

- Product name: **Call360**.
- Case investigation screen heading/menu/breadcrumb: **Call Detail** (not “Call 360”).
- Call list: **Call Explorer**; browser conversation: **Voice Studio**; survey builder: **Survey Studio**.
- Canonical Call Detail React route: `/cases/:caseId`; may deep-link attempt/session focus by validated query parameters. Domain `CallbackCase`, `ContactAttempt`, `ConversationSession` names are unchanged.

## Consequences and verification

Update all requirement descriptions, UI copy, tests, menus, documentation, sample screenshots and Claude Code prompts. Test both application brand and detail screen label. Do not rename persisted tables simply because the UI screen name changed. See `docs/product/SCREEN_NAMING_AND_ROUTES.md`.
