# Architecture decision records — index

Each ADR records one decision, its context, the alternatives considered and its consequences. An ADR changes only through a new ADR that amends or supersedes it. `scripts/validate_specs.py` checks that this index and the `ADR-*.md` files match exactly.

| ADR | Title | Status | Stage scope |
|---|---|---|---|
| [ADR-0001](ADR-0001-three-repositories.md) | Three independent Call360 repositories | Selected by requester; pending internal AIA architecture approval | S0–S6 |
| [ADR-0002](ADR-0002-product-and-detail-terminology.md) | Call360 for product, Call Detail for investigation | Selected by requester; **amended by ADR-0007** (script editor name only) | S0–S6 |
| [ADR-0003](ADR-0003-s0-technical-architecture.md) | S0 technical architecture and local verification | Proposed (CP0.0) | S0 |
| [ADR-0004](ADR-0004-identity-tokens-authorization.md) | Identity provider abstraction, tokens, sessions and authorization | Proposed (CP0.0); owner decisions D-7, C-6 applied | S0 (S5 extends) |
| [ADR-0005](ADR-0005-audit-and-immutability.md) | Append-only audit, immutable records and session pins | Proposed (CP0.0); owner decisions D-6, D-8 applied | S0–S6 |
| [ADR-0006](ADR-0006-api-contract-and-generated-client.md) | API contract ownership, conventions and generated client | Proposed (CP0.0); owner decision D-14 applied | S0–S6 |
| [ADR-0007](ADR-0007-script-studio-naming-and-lifecycle.md) | Script Studio naming and script lifecycle | Proposed (CP0.0); owner decisions D-2, C-4, C-26 applied | S0–S6 |
| [ADR-0008](ADR-0008-s0-scope-boundaries.md) | Stage 0 functional boundaries, holds, navigation and synthetic evidence | Proposed (CP0.0); owner decisions D-4, D-10, C-1, C-12 applied | S0 |
