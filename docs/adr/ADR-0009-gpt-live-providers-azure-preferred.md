# ADR-0009: GPT-Live providers — one shared protocol adapter, Azure OpenAI preferred

**Status:** Proposed (S1-E.2A), 2026-11-18 — owner instruction "Azure OpenAI must be the primary provider for Call360"
**Scope:** Voice Lab (S1-E); the operational callback integration is out of scope and needs its own decision.

## Context

The owner uses Azure OpenAI, not the direct OpenAI API. S1-E.2 built a GPT-Live adapter for the direct OpenAI endpoint.
The Azure GPT-Live documentation (read 2026-11-18; `docs/integrations/GPT_LIVE_PROTOCOL_NOTES.md`) uses the same event
names and lifecycle, but a different endpoint (`wss://<resource>.openai.azure.com/openai/v1/live/sessions`), Azure
authentication (API key; Microsoft Entra ID / Managed Identity bearer tokens), a deployment, and documents only 24 kHz
PCM16 on the WebSocket path. The Azure pricing page shows no GPT-Live amount ("$-/per 1 unit hour").

## Decision

1. **One protocol adapter, several endpoints.** `app/voice/gpt_live.py` implements the GPT-Live protocol once;
   `app/voice/live_providers.py` resolves the endpoint, authentication headers, wire sample rate and `session.model`
   per provider. Session management, recording, transcription, evaluation, budgets, authorisation and termination are
   shared and unchanged.
2. **Providers:** `MOCK`, `MOCK_METERED`, `GPT_LIVE_MOCK` (loopback mock; Azure profile by default),
   `AZURE_OPENAI_GPT_LIVE` (**preferred**, PAID), `OPENAI_GPT_LIVE` (PAID). `GPT_LIVE` (S1-E.2 code) stays as a hidden
   legacy alias of `OPENAI_GPT_LIVE` so recorded prompt versions resolve; it cannot be used for new prompts.
3. **Azure authentication:** `API_KEY` for local development (`api-key` header) and `ENTRA` for Azure deployment
   (bearer token from `azure-identity`: Managed Identity when a client id is configured, otherwise
   DefaultAzureCredential; scope configurable, default `https://ai.azure.com/.default`). Credentials stay on the backend;
   without the library or a credential the provider is unavailable (fail closed).
4. **Deployment:** `session.model` carries the configured deployment name; a prompt naming another deployment is
   refused (`DEPLOYMENT_MISMATCH`).
5. **Audio:** the browser path stays 16 kHz; the adapter resamples to the provider's wire rate (Azure 24 kHz by default,
   OpenAI 16 kHz) at its boundary.
6. **Pricing:** provider-specific. Azure's rate comes only from the owner's verified configuration (USD per minute,
   source, verification date); without it every Azure session and authorisation is refused (`COST_UNKNOWN`). The
   direct OpenAI price is never reused for Azure.
7. **Network guard:** outside tests only `api.openai.com` (OpenAI) and `*.openai.azure.com` (Azure) are reachable,
   per vendor; in `APP_ENV=test` only loopback.
8. **Spend safeguards unchanged:** paid switch, single-use smoke-test authorisation by another user, PAID budget and
   one concurrent session, emergency stop, server timer, explicit close and conservative handling of unconfirmed
   termination. Azure budgets and cost alerts are notifications, not hard caps.

## Alternatives considered

- A separate Azure adapter or microservice — rejected: duplicated session, budget and termination logic.
- Reusing the OpenAI rate for Azure — rejected: unverified; Azure billing units differ ("unit hour").
- Relying on Azure budget alerts as a cap — rejected: alerts do not stop traffic.

## Consequences

- Azure live validation needs the owner's resource, deployment, credential and verified price, then the S1-E.2 smoke-test
  procedure with the Azure provider.
- Entra ID needs `azure-identity` installed in the deployment image (not installed locally; adding it is a dependency
  change for a later checkpoint).
- Unverified until a live session: whether `session.model` takes the deployment or model name, the API-key header for
  GPT-Live, 16 kHz acceptance, regional availability and exact billing units.
