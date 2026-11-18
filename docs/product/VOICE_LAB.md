# Voice Lab (S1-E.1) — functional specification

Status: S1-E.1 accepted 2026-11-18; S1-E.2 GPT-Live adapter implemented and offline-verified (awaiting live validation
and acceptance). Records: `docs/acceptance/S1.md` (S1-E.1, S1-E.2); decisions D-87…D-102. Route `/voice-lab`; API
`/api/v1/voice-lab/*`. GPT-Live protocol: `docs/integrations/GPT_LIVE_PROTOCOL_NOTES.md`.

## Purpose

A module of Call360 for experimenting with and evaluating voice providers **before** any provider is integrated into the
operational callback process. It reuses the voice-provider protocol, the mock provider, the browser audio client,
encrypted local storage, WAV playback and the local faster-whisper engine. It does not run the S2-D question
controller and changes no compliance logic.

## Isolation

Experimental records only (`lab_*` tables, no foreign key to operational tables, separate encrypted audio root,
`LAB.*` audit actions). Nothing in the lab is a contact attempt, conversation session, finding or review, so KPIs,
queues, Call Detail and compliance never include it. Synthetic content only.

## Sections

| Section | Contents |
|---|---|
| Playground | Provider, model and voice; system prompt; per-turn instructions; versioned prompts (history kept); estimated session cost; Start / Mute / Stop (full duplex, interruption); duration; optional server-side recording and playback; independent transcript; provider event trace; reconciled cost |
| Golden Dataset | Datasets of test cases (name, description, system prompt, test instruction, expected spoken statement, synthetic customer response, expected structured answer, expected behaviour, evaluation criteria, optional mock output, optional synthetic WAV fixture); insert-only revisions; import of synthetic questions and statements from Script Studio (records the source question revision) |
| Experiments | Dataset, prompt version (with provider / model / voice), selected tests, repetitions (1–5), maximum duration per trial (5–120 s), maximum authorised spend; estimated maximum cost shown before creation and fixed by the server; metered experiments need spend authorisation by another user (Voice Lab manager) confirming the exact amount; every run reserves first and runs once (no retries, no schedules) |
| Evaluation Results | Per trial: provider text vs independent transcript wording (exact match, added / omitted / substituted words, WER), deviation attribution (suspected speech deviation / suspected transcription error / unattributed), structured-answer accuracy, first-audio and interruption latency, duration, cost, failures, criteria results, audio fixture for human assessment; expected behaviour always for human assessment |
| Session History | Playground sessions and experiment trials with their evidence |
| Budget and Settings | Spend evidence (paid USD, paid reservations / sessions / experiments), paid / retry / schedule switches (disabled), emergency stop, per-class budgets with usage, provider catalogue and rate cards, change history |

## Cost controls (server-enforced)

Spend classes NONE (keyless mock), SIMULATED (mock with synthetic rates; no money) and PAID (refused; cannot be stored
in this build). Before a metered session or experiment starts: emergency stop, per-experiment, daily (Singapore day)
and overall limits and maximum concurrent sessions are checked under a per-class lock, and the estimated maximum is
reserved; it is reconciled with the measured cost at the end. Unknown cost is refused (fail closed). Interactive
sessions end at the maximum duration, after the idle timeout, on Stop or on the emergency stop. Initial limits are the
owner's proposal (USD 10 overall, USD 2 daily, USD 1 per experiment, one concurrent session, 5 minutes, 15 s idle) and
are not authorisation to spend. Real provider rates must be taken from the provider's current official price list
before a real provider is configured; GPT-Live needs the owner's separate explicit authorisation.

## Roles

`voicelab.use` (USER, S&C checker) — playground, datasets, experiments. `voicelab.manage` (ADMIN) — budgets, emergency
stop, spend authorisation of another user's experiment; cannot run sessions or experiments.

## GPT-Live (S1-E.2)

Providers `GPT_LIVE` (PAID; real endpoint; available only with `VOICE_LAB_GPT_LIVE_MODE=LIVE` and a backend-only key)
and `GPT_LIVE_MOCK` (SIMULATED; the same adapter on a loopback mocked protocol server). A paid session needs the
manager's paid switch and a single-use smoke-test authorisation (≤ 120 s, own USD maximum, expiry) issued by a manager
and started by a different user, plus the PAID budget. The server timer, `session.close` on every exit and settlement
only from a confirmed `session.closed` protect spend; unconfirmed sessions keep their reservation until a manager
records the provider-reported usage or closes the orphan over the sideband. Retention (168 h) applies to lab audio and
session transcripts. Trials report an automated speech result and may carry a human-confirmed result; transcription is
never presented as proof of verbatim delivery.

