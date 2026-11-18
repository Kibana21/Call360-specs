# GPT-Live protocol notes (S1-E.2) — what the official documentation states

Accessed 2026-11-18 (no publication date or version is shown on the pages). Read only; no API call was made. Pages:
`/api/docs/guides/live`, `/api/docs/guides/live-conversations`, `/api/docs/guides/live-prompting`,
`/api/docs/guides/live-delegation`, `/api/docs/guides/voice-websockets?api=live`,
`/api/docs/guides/voice-server-controls?api=live`, `/api/docs/guides/voice-latency-cost?api=live`,
`/api/docs/guides/live-migration`, `/api/docs/models/gpt-live-1`, `/api/docs/pricing`,
`/api/docs/guides/spend-limits` and `/api/reference/resources/live/primary-websocket` (read in full), all on
`developers.openai.com`. Items marked **not documented** were absent from every page read; the adapter does not rely on
them. GPT-Live is **not** the Realtime API: event names, startup and turn handling differ (migration guide).

## Model, price and limits

- Model `gpt-live-1` (only snapshot); full-duplex voice; input audio and text, output audio and text; endpoint
  `v1/live/sessions`; function calling supported; Free tier unsupported; rate limits measured in concurrent sessions
  (Build 50, Launch 300, Grow 500).
- **Price (verified):** "Voice sessions cost $0.05 per minute, billed per second", "not rounded up to the next whole
  minute"; one voice rate (input and output are not billed separately). "Backend model and tool usage is billed
  separately" (Responses delegation only — Call360 uses client delegation and makes no backend model call). Whether
  instruction tokens, live transcription line items or the 10 % regional uplift apply to GPT-Live is **not stated**.
- Maximum session duration: **not documented** (a close reason `expired` exists; `session.started.session.expires_at`
  is returned). No session.start field sets a duration — Call360 enforces its own timer and closes the session.

## Primary WebSocket (server-side; the API key never leaves the backend)

- URL `wss://api.openai.com/v1/live/sessions` (no query parameters); header `Authorization: Bearer <key>`. Beta /
  version headers and ephemeral secrets for the Live WebSocket: **not documented**.
- First message `session.start` with `session` = `{model, instructions (≤ 16,384 tokens), audio: {format: {type:
  "audio/pcm", rate: 16000|24000} | pcmu/pcma 8000, output: {voice}}, delegation: {type: "client",
  acknowledgement_delay_ms 0–800} | responses | decisions | null, input (≤ 128 messages), store (default false),
  safety_identifier, triggers}`; wait for `session.started` (`session.id`, `expires_at`, `model`, `status`). Model,
  instructions, audio format and voice are immutable afterwards.
- Audio: client `session.input_audio.append {audio: base64 raw PCM}` (no acknowledgement, whole 16-bit samples);
  server `session.output_audio.delta {delta}` (primary: no `event_id`, no timing, **no output-audio-done event**).
  Mute: `session.input_audio.mute` / `unmute` → `…muted` / `…unmuted`.
- Transcripts: `session.input_transcript.delta` / `session.output_transcript.delta` (`delta`, `start_ms`, `end_ms`);
  no completed-transcript event.
- Instructions mid-session: `session.instructions.append {content ≤ 500 tokens, delegation_id: null | id}` → `…appended
  {start_ms, end_ms}` (context injection, not proof of speech; appending can interrupt speech in progress). Also
  `session.thinking.append` (quiet) and `session.commentary.append` (spoken) with the same shape.
- Client delegation: server `session.delegation.created {offset_ms, delegation: {id, type: "delegation", target:
  "client"}}` — metadata only, **no task text**; the application reconstructs the request from transcripts and answers
  with `session.commentary.append` (spoken) or `session.thinking.append` (quiet) carrying `delegation_id`. Delegation
  completed / cancelled events, a client function-call event and `call_id` in client mode: **not documented**.
- Usage: `session.usage.updated {usage: {seconds}}` cumulative (replace, never sum); `session.closed {reason, session,
  usage: {seconds}}` final. Reasons: `close_requested`, `expired`, `content`, `remote_hangup`, `connection_lost`.
  "A connection closing without it does not confirm successful finalization."
- Close: `session.close`; keep reading until `session.closed`.
- Errors: `error {error: {type, code, message, param?, client_event_id?}}`; codes seen: `unknown_parameter`,
  `immutable_field_update`, `tool_outputs_required`, `function_call_outputs_required`; full list **not documented**;
  some moderation errors end the session. `info {code, message}` also exists.
- Interruption: **no** speech-started, turn, cancel, truncate or clear events. The docs say the model is full-duplex,
  "may keep speaking briefly after an interruption", and that clients mute/drop output and discard queued audio.
- Sideband: `wss://api.openai.com/v1/live/sessions/{session_id}/attach` (same auth; no `session.start`; replays the last
  3 s of events) — used by Call360 only for a manager's explicit close of an orphaned session.

## Spend limits (provider side)

Project and organisation **hard spend limits** make requests fail with `429` (`project_spend_limit_exceeded` /
`organization_spend_limit_exceeded`); limits are monthly; "Enforcement is not instantaneous, so recorded spend can
slightly exceed the configured amount." Steps are quoted in `docs/acceptance/S1.md` (S1-E.2 runbook).

## How Call360 maps this (adapter `app/voice/gpt_live.py`)

| Need | GPT-Live mechanism used | Call360 behaviour where the protocol is silent |
|---|---|---|
| Audio format | `audio/pcm` 16 kHz both ways (supported) — no resampling; browser frames are 20 ms PCM16 | — |
| Barge-in | none in the protocol | the S1-A local VAD on the caller's audio clears browser playback and drops provider audio until the caller's turn ends (documented client-side policy) |
| Response boundaries | none | a new "response" starts when provider audio resumes after ≥ 600 ms of silence or after a barge-in; "done" after 800 ms without audio |
| Dynamic instructions | `session.instructions.append` (`delegation_id: null`) | per-turn instructions after each caller turn; ad-hoc instructions from the Playground |
| Delegation | `delegation: {type: "client"}`; reply with `session.commentary.append` | deterministic Python responder (no LLM, no tool, no backend model) |
| Duration | none configurable | server timer; `session.close` on timeout, stop, emergency stop, browser disconnect or error |
| Usage | `session.usage.updated`, `session.closed.usage.seconds` | reservation reconciled only from a confirmed `session.closed`; otherwise retained (uncertain) |

## Azure OpenAI GPT-Live (S1-E.2A) — what the Microsoft documentation states

Read 2026-11-18 (no API call): `learn.microsoft.com/en-us/azure/foundry/openai/how-to/gpt-live`, `…/concepts/gpt-live`,
`…/gpt-live-reference` (ms.date 2026-09-04), `…/how-to/gpt-live-delegation`, `…/quotas-limits`, the classic
managed-identity page, and `azure.microsoft.com/en-us/pricing/details/azure-openai/`.

| Item | Azure documentation | Call360 |
|---|---|---|
| Endpoint | `wss://<resource>.openai.azure.com/openai/v1/live/sessions`; no `api-version` stated | derived from `VOICE_LAB_AZURE_OPENAI_ENDPOINT`; host must be `*.openai.azure.com` |
| Model / deployment | `model` in `session.start` (example `gpt-live-1`); prerequisite "a deployment of the gpt-live-1 model"; whether `model` takes the deployment or model name **not stated** | sends the configured deployment name; recommend naming the deployment `gpt-live-1` to remove the ambiguity |
| Auth | sample `Authorization: Bearer <Entra token>`; "API key or Microsoft Entra ID"; API-key header **not stated** on the GPT-Live pages; managed-identity page: scope `https://ai.azure.com/.default`, roles Cognitive Services OpenAI User / Contributor, custom subdomain needed for Entra | `api-key` header (Azure OpenAI convention — to be confirmed live) or Entra bearer token (`azure-identity`) |
| Audio | how-to and reference: raw mono PCM16 **24 kHz**, base64, even byte count; concepts page also mentions 16 kHz and G.711 | 24 kHz by default (`VOICE_LAB_AZURE_AUDIO_RATE`), resampled from/to the browser's 16 kHz |
| Events | same names as OpenAI's GPT-Live: `session.start`/`started`, `session.update`/`updated`, `session.input_audio.append`/`mute`/`unmute`, `session.output_audio.delta` (with `start_ms`/`end_ms`), transcript deltas, `session.instructions/thinking/commentary.append` (+ `.appended`), `session.delegation.created`, `response.event`, `session.usage.updated` (cumulative, "approximately once per minute"), `session.closed` (reasons close_requested, expired, content, remote_hangup, connection_lost), `error`; strict session config rejects unknown fields; no output-audio-done or interruption event | the shared adapter, unchanged (the reference does not mention `store`; Call360 sends `store: false` — to be confirmed live, the strict config may reject it) |
| Delegation | `{type: "client"}` or `{type: "responses"}`; client: reply with commentary/thinking append using `delegation.id` | client delegation, deterministic Python responder |
| Sideband | `wss://<resource>.openai.azure.com/openai/v1/live/sessions/{session_id}/attach`; no `session.start` | used for a manager's close of an orphan |
| Usage | cumulative seconds; final usage on `session.closed`; "a transport close without that event leaves final usage unconfirmed" | settle only on confirmed `session.closed` |
| Regions | **not stated** on the pages read | owner records region and deployment type |
| Quotas | concurrent sessions by tier (summary): default 10, tier 1 25, tier 2 50, tier 3 200, tier 4 300, tier 5 500 | Call360 allows one paid session |
| Pricing | the pricing page lists "GPT-Live Global" and "GPT-Live Data Zone" at "$-/per 1 unit hour" — **no amount rendered**; WebRTC has a 15 s minimum that "doesn't apply to WebSocket sessions"; backend/tool usage billed separately | **unknown** → Azure fails closed until the owner configures a verified price |

