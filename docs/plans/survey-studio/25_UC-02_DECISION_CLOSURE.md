# UC-02 — Review outcome and backend decision closure

**Authority:** owner, 2026-11-21, "UC-02 Review and Backend Decision Closure" (decision register D-170…D-175).
**Status of this document:** the owner's acceptance and direction are recorded as given. **Every ruling text below is
PROPOSED wording prepared for the owner's final approval** — the owner asked for the rulings to be *prepared* and for
recommendations, not for them to be taken as decided. Where a ruling needs the business or Compliance, it says so and
is **not** marked approved.

**UC-02 is ACCEPTED as technically verified, subject to the contract clarifications in §1** (D-170). Formal UX
acceptance, business policy approval, live-call eligibility and backend authorisation remain separate. Nothing in
this document authorises backend work.

**No accepted golden fixture is invalidated by anything below.** Where an amendment adds behaviour the 27 fixtures do
not specify, it is assigned to a new, explicitly versioned schema (`/6`) with its own fixtures, to be written when
that behaviour is authorised. Schemas /1–/5 keep their meaning.

---

## 1. Technical schema decisions

### 1.1 Recommended for approval as written (17)

TS-1 · TS-3 · TS-5 · TS-6 · TS-8 · TS-11 · TS-13 · TS-14 · TS-15 · TS-16 · TS-17 · TS-18 · TS-19 · TS-20 · TS-21 ·
TS-22 · TS-23, as worded in `23_UC-02_DECISION_READY_CONTRACTS.md` §1.2 (owner's recommendation, D-171).

### 1.2 Amended before final approval (6)

| No. | Owner's instruction | Was (`23_…` §1.2) | **Amended wording, proposed** | Fixtures |
|---|---|---|---|---|
| **TS-2** | Preserve future numeric/free-text-driven Decision nodes | A statement, a number question, an acknowledgement and a free-text question have exactly one route and cannot branch | **An item that has no enumerated answers — a statement, a number question, an acknowledgement, a free-text question — has exactly one route out of its own node. This restricts the item node only. It does not restrict a Decision node: a Decision placed after such an item may, in a later schema version, read its answer and choose a route.** No rule may be written that would make that impossible | /5 unchanged (K2) |
| **TS-4** | Exclude uncontrolled conversational wording from publishable surveys | Delivery mode is an explicit field with three values | **Delivery mode is an explicit field of every stored Wording Version. The publishable values are `CONTROLLED_TTS` and `EXACT_AUDIO`. `CONVERSATIONAL` is not publishable: a draft may hold it so that it can be seen and corrected, but a candidate can never contain it — the server refuses at submission and again at publication.** A controlled form of conversational delivery, if ever wanted, is a Compliance ruling and a new schema version | /5 unchanged (K6 already expects the error) |
| **TS-7** | Use declared numeric precision; never round or truncate silently | A fraction in a whole-number field, or an amount with more than two decimals, is `INVALID` | **Every numeric catalog field declares its precision as a number of decimal places (`scale`). A value with more decimal places than its field declares is `INVALID`. No value is ever rounded, truncated or padded to make it fit; a value is rendered exactly as it is held.** The same holds for a number question: when its rule declares a `scale`, an answer with more decimal places is rejected. In schema /5 the declared precision is 0 for a whole-number field and 2 for money | /5 unchanged (K5). Per-field `scale` and a rejection code for an over-precise answer: **schema /6** |
| **TS-9** | Capture explicit negative acknowledgements as evidence without treating them as successful acknowledgements | `{acknowledged: true}` is the only accepted value; an explicit `false` is rejected and is not an answer value | **`{acknowledged: true}` is the only successful acknowledgement. An explicit `{acknowledged: false}` is captured as evidence — an observation that the customer did not acknowledge, with its execution key and time — and is never a successful acknowledgement: it is not recorded as the answer, it satisfies nothing, and it does not advance the run.** What the call then does is a non-answer decision | /5 unchanged: K4's `rejections` entry `NON_ANSWER_POLICY_UNRESOLVED` **is** that observation in /5 terms. The stored evidence record: **schema /6**, with D-NA-1 |
| **TS-10** | Keep schema-v1 numeric-condition restrictions extensible | Number and acknowledgement answers are not condition inputs in schema version 1 | **In schema version 1 a condition may read yes/no and choice answers only. This is a restriction of version 1, not of the model: every input declaration carries its answer type, and an unsupported type is refused with an explicit error, never ignored. Adding numeric (or other) inputs later must not change the meaning of any version-1 condition.** | /5 unchanged |
| **TS-12** | Make lifecycle decision history append-only while keeping candidate content immutable | Draft → Candidate → Version as three entities; Candidate and Version are insert-only | **Draft, Candidate and Version are three entities. A candidate's content record — content, manifest, hashes, submitter, time — is written once and never changed. Its lifecycle is not a column that is updated: every decision (submitted, approved, rejected, withdrawn, superseded, published, scheduled, version withdrawn) is an append-only event that refers to the candidate or version by id, and the current status is derived from that history.** The same holds for a version | No fixture (governance is verified by prototype tests) |

**Consequence for the prototype.** None of the six amendments requires a prototype change now, and none was made.
TS-12's append-only history is how the prototype's audit list already behaves; its `status` field is a convenience of
the in-memory model and is not a storage design.

---

## 2. The twelve persistence blockers: proposed final rulings and dependency impacts

For each: the owner's recommendation, the exact ruling proposed, what it changes, and — in the last column — **who
must still rule**. "Mechanism" is the part engineering can fix now. "Content" is the part that is policy.

| # | Blocker | Owner's recommendation | **Proposed ruling (mechanism)** | Dependency impact | Still needs |
|--:|---|---|---|---|---|
| PB-1 | UC-D-1 — default delivery mode | Controlled exact-text delivery by default | A new Wording Version is created with delivery mode `CONTROLLED_TTS`. The value is always stored explicitly (TS-4) | Wording schema: required field. Authoring: the default in the card. Prototype and /5 already behave so | **Owner's approval only** |
| PB-2 | UC-D-2 — conversational delivery | (TS-4) Excluded from publishable surveys | As TS-4 amended: not publishable; refused at submission and at publication | Validator rule; publication gate; live-eligibility condition | Owner's approval. *A future controlled form: Compliance* |
| PB-3 | UC-D-3a — permitted variable fields | Allowlisted customer fields for spoken variables | Each catalog field carries `speakable`, **false unless set**. A wording may use only fields whose `speakable` is true; any other is a validation error. In schema /5 the fields a fixture lists are treated as allowlisted for that fixture | Catalog schema: one flag. Validator: one rule (new code, schema /6). Call plan: unchanged | **Business and Compliance: the actual list. NOT approved here.** No field is allowlisted by this ruling |
| PB-4 | UC-D-4 — statement roles | Four statement roles with acknowledgement separate | Statement roles are `OPENING`, `TRANSITION`, `DISCLOSURE`, `CLOSING`. A statement never takes an answer. Where the customer must acknowledge something, that is a separate acknowledgement question placed after the statement | Item schema: enum of four. Lifecycle mapping: `TRANSITION` has no counterpart in the existing lifecycle | Owner's approval only |
| PB-5 | UC-D-6 (D-NA-5, D-NA-10) — "mandatory" | Question-response obligation distinct from lifecycle gates | Two separate attributes of a question: **`response_obligation`** (how far an answer is required) and **`lifecycle_role`** (identity, consent, recording, cloud processing). Neither implies the other. `response_obligation` holds a code from a governed catalog, so its classes can be added or renamed without a schema change | Item schema: two fields. Content document: both carried. Evaluation, KPIs, review: read `response_obligation`. The prototype's `mandatory` flag maps to one catalog code | **Business and Compliance: the classes and what each means (D-NA-5), and whether "mandatory" and "required" are one (D-NA-10). NOT approved here** |
| PB-6 | G-4a — Publisher | Separate Publisher permission | A permission to publish exists apart from the permission to approve and is never granted by it. Publisher ≠ submitter (D-144). Until ruled otherwise the most restrictive rule applies: the approver of a candidate may not publish it | Permission catalog: one new permission. Publication service: two identity checks | **Business: who holds Publisher, and whether the approver may publish.** No role is granted the permission by this ruling |
| PB-7 | G-4b — draft locking | Editable draft with immutable submitted candidates | A draft is never locked by a review. Submitting creates an immutable candidate; the draft stays editable; a later submission supersedes an open candidate (D-143) | Draft and candidate tables; no lock table or lock state | Owner's approval only |
| PB-8 | G-4c — approved wording | S&C-governed wording in one Survey Studio approval experience | The approval state of a Wording Version is recorded on it with who approved, when and in which candidate. It can be set only by an identity authorised by S&C, through the candidate decision. Wording is reviewed in the same review as structure, as its own section; there is no second approval chain and no second product | Wording schema: an approval record. Review: a wording section. Publication gate: every pinned wording approved, for live use | **Compliance: who in S&C may approve, what evidence an approval needs, and what counts as approved for regulated wording. NOT approved here** |
| PB-9 | G-4e — activation, eligibility, skip dispositions | Separate activation and eligibility; separate sequence/jump skip policies | Four separate stored fields on a module instance: `activation`, `eligibility`, `if_ineligible` (after a jump; required when a jump can arrive and the module can be skipped; never defaulted), `if_skipped_in_sequence` (default: continue) | Survey schema as built and as fixtures G, H specify | Owner's approval only (confirms D-139, D-146) |
| PB-10 | SS-D-05 — outcome catalog | Governed outcome catalog | Outcomes are entries of a governed, versioned catalog: `{code, class, label, routable}`. A definition refers to an outcome by code. The classes are fixed in the schema: `NORMAL_COMPLETION`, `EXCEPTION`, `ESCALATION`, `REVIEW_HALT`, and `NON_ANSWER_EXCEPTION` (PB-12) | Catalog table; module and survey documents hold codes; validator checks membership | **Business and Compliance: the list of outcomes and the class of each. NOT approved here.** The prototype's six outcomes remain synthetic |
| PB-11 | D-NA-9 — non-answer routing | Explicit non-answer resolution | A non-answer never matches an answer route — not a specific one and not `ANY`. It is resolved only by an explicit non-answer resolution declared for that question. A question reached on a live call with no such resolution is a blocker for live eligibility. The route contract reserves the place for it now | Route contract: one reserved key, unused by every existing fixture. Harness: no behaviour yet | **Business and Compliance: every behaviour — what counts as a non-answer, after how many attempts, and what each resolution may be (D-NA-1, 3, 4, 8, 11, 12, 15 and the parameters). NOT approved here** |
| PB-12 | D-NA-13 — outcome for "no answer" | A separate non-answer exception outcome | "No answer obtained" ends with an outcome of its own class, `NON_ANSWER_EXCEPTION`. It is never recorded as an ordinary exception, an escalation, or a completion | Outcome catalog: one class. Terminal states: unchanged until D-NA-14 | **Business and Compliance: the outcome code or codes, and their labels. NOT approved here** |

### 2.1 What these rulings unblock, and what they do not

**If the owner approves the mechanisms above**, the definition store's schema can be fixed without waiting for the
policy content, because each open list becomes **data in a governed catalog** rather than part of the schema:
permitted fields (PB-3), obligation classes (PB-5), outcomes (PB-10, PB-12).

**They do not approve** — and this document does not mark approved — any actual permitted customer field, any
refusal handling, any consent policy, any outcome, or any non-answer rule. A backend built on these mechanisms holds
empty or synthetic catalogs until the business and Compliance fill them, and no survey can be eligible for a live
call until they do.

---

## 3. Prototype decisions P-23 to P-29: read verbatim and classified

Classes: **E** = safe engineering default (fails closed, invents no policy) · **B** = Business/Compliance decision ·
**V** = voice-channel decision. Several have parts of more than one class; each part is named.

| No. | Verbatim (decision register) | Class | Reasoning |
|---|---|:-:|---|
| P-23 | "A recording with no approved asset is an **error** `RECORDING_ASSET_MISSING`. The prototype has no asset concept, so every recording is blocked" | **E**; one part **V** | Blocking what cannot be delivered is fail-closed. *How a recording is produced, approved and attached is a voice-channel decision.* |
| P-24 | "An explicit "not acknowledged" is rejected with `NON_ANSWER_POLICY_UNRESOLVED`; the run stays pending. Distinct from "no answer was given"" | **E** for the block; **B** for what follows | Refusing to proceed without a rule is fail-closed. Amended by TS-9: the observation is kept as evidence. *What the call does next is a no-answer decision.* |
| P-25 | "An unfinished variable also stops delivery at execution (state `MALFORMED`)" | **E** | Otherwise text with braces would be spoken. No policy involved |
| P-26 | "A fraction in a whole-number field, or an amount with more than two decimals, is `INVALID`; nothing is rounded" | **E**; one part **B**, one part **V** | Never rounding is fail-closed; generalised by TS-7 to declared precision. *The precision each field declares is a catalog (business) matter; how a value is spoken is a voice-channel decision.* |
| P-27 | "Statements are labelled S1, S2 …; questions keep Q1, Q2 … counting questions only. Display only" | **E** | A display label; no identity, storage or behaviour depends on it. Subject to UX acceptance like any label |
| P-28 | "Live eligibility is ten explicit conditions in three states (`MET`, `NOT_MET`, `NOT_AVAILABLE`). In the prototype it can never be "eligible": assignment and channel cannot be established, and a simulated publication does not count" | **E** for the structure; **B** for the list; **V** for the channel condition | Keeping eligibility apart from plan computation, and never reporting "eligible" in a prototype, is fail-closed. *Which conditions make a survey eligible for a live call is a Business/Compliance ruling; what a channel requires is a voice-channel decision.* Now eleven conditions (§4) |
| P-29 | "Rules introduced in UC-01 and UC-02 carry stable validation codes; earlier rules are still identified by their message" | **E** | Engineering hygiene. The earlier rules receive codes in SS-03A |

**None of the seven invents a policy.** Each of the parts marked B or V is already in the open-decision lists of
`23_…` Part 1.

---

## 4. Call-plan eligibility: a present gate is not an approved enforcement

Changed in the prototype as instructed (D-174):

- The three gate conditions now read **"Present"** or **"Not present"**, not "Met".
- A new, separate condition was added: **"What each gate does when the customer says no, refuses or does not answer
  is approved"** — **Not met**. Its reason: *"Not decided. A gate being present shows only that the question is
  asked. Whether the call ends, continues or escalates afterwards is a business and compliance ruling that has not
  been made, and nothing here assumes one."*
- A note stands under the list: *"“Present” means only that the gate question is in the survey. It does not mean
  that what the call does after a “no”, a refusal or silence is approved — that is a separate condition, and it is
  not met."*
- Each gate's own reason now ends: *"This does not establish that its enforcement — what the call does on “no”,
  refusal or silence — is approved."*

Eligibility is now eleven conditions. With all three gates present a survey is still not eligible.

**Verified:** 403 unit tests and 13 of 13 prototype journeys pass with the change; type check and lint clean. The
standard suite (prototype off) was not re-run for this change: it touches only Survey Studio files, which that suite
does not load, and it passed 33 of 33 on the preceding build. Screenshots `UC20`–`UC27` in
`docs/acceptance/evidence/UC-02/screens/` were regenerated and show the new wording.

---

## 5. Baseline preservation

**UC-01 and UC-02 ARE committed.** While this document was being prepared, both repositories received a commit at
2026-11-21 23:23. I did not make them; I verified them.

| Repository | Commit | Contains | State against the remote |
|---|---|---|---|
| **Call360-frontend** | **`c575f76`** (28 files) | UC-01 and UC-02: all Survey Studio model, screens, tests and the two journeys | Level with `origin/main` — the commit is on the remote |
| **Call360-specs** | **`33fdfce`** (49 files) | G-6, UC-01 and UC-02: documents 20–24, fixtures K1–K8, `reference_interpreter_v5.py`, the UC-01 and UC-02 evidence, the contract, the register and the handoff as they stood at that time | Level with `origin/main` — the commit is on the remote |
| Call360-backend | `7228875` | unchanged | Level; clean |

**Preserved in the specs commit, verified:** all **27 fixture files** and all **five reference interpreters** are
tracked. On disk they regenerate byte-for-byte: 82 expected runs, 14 expected plans.

**Made after those commits, and therefore NOT committed** — the work of this review:

| Repository | Uncommitted |
|---|---|
| Call360-frontend | 5 files: the eligibility clarification of §4 (`model/plan.ts`, `CallPlanPage.tsx`, `model/uc02.test.ts`, `e2e/prototype/uc02.proto.ts`, `survey-studio.css`) |
| Call360-specs | This document and `26_SS-03A_FOUNDATION_SPECIFICATION.md` (new); the register, the contract (§8.6, §8.9), documents 23 and 24 (status notes), the index, the handoff; regenerated UC-02 screenshots and check records |

Nothing is staged. **I made no commit and no push.** Committing the items in the second table needs the owner's
authorisation, or the owner's own commit.

---

## 6. Next backend boundary

`26_SS-03A_FOUNDATION_SPECIFICATION.md` — a narrowly scoped specification. **Not authorised for implementation.**
