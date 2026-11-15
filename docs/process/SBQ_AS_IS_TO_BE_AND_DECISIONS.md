# Call360 — SBQ post-sale callback operating model

**Document:** CALL360-PROC-003 | **Version:** 0.3 | **Status:** Proposed; not an independently verified AIA SBQ SOP.

## Source of knowledge and validation boundary

The user described an existing process where the SBQ team assigns a sale risk using sales location, premium magnitude, ILP status and other factors; selects a risk/product-specific callback script; a human contacts the eligible party, follows mandatory questions, notes yes/no and narrative answers, and records outcomes. **Exact current AIA risk scores, eligibility, roles, due dates, scripts, approvals, and interfaces have not been supplied and must not be invented.** Obtain sample de-identified workflow artefacts and approved SOP from SBQ/S&C to convert assumptions to approved rules.

## Proposed AS-IS process to validate

| Seq | Current manual step (hypothesis) | Actor/source | Output to confirm |
|---|---|---|---|
| 01 | New sale/policy information made available | Policy administration / distribution | Policy number, customer, product, FSC, premium, sales context |
| 02 | SBQ evaluates the sale for verification priority | SBQ risk assessor or upstream engine | Risk band + reasons + assessment version |
| 03 | A callback obligation is identified and allocated | SBQ queue/manager | Work item, due date, eligible contact, assigned caller |
| 04 | Caller selects a script for the risk/product context | Script register / SBQ procedure | Script name, version, selection conditions |
| 05 | Caller tries to contact person; may retry | Agent | Each attempt, dialed/contacted party, disposition |
| 06 | Caller follows script, collects yes/no and explanations | Agent and customer | Per-question answers, notes, consent, potential concerns |
| 07 | Exception handling / quality review | SBQ/S&C checker | Findings, contact retry, follow-up, final disposition |
| 08 | Records retained for audit and reporting | Internal systems | Provenance, content, outcome, performance summary |

## TO-BE process and system boundaries

1. **Intake**: canonicalize policy/parties/sale and policyholder contact relationships. Support MOCK_API and MANUAL in Stage 0; real INTERNAL_API and BULK in Stage 4.
2. **Risk**: accept upstream source risk OR calculate using a versioned SBQ-configured rule set. Never merge callback-selection risk with investment suitability risk tolerance or with findings. Record inputs, thresholds source, factors, author, effective time, override and conflict resolution.
3. **Eligibility**: determine whether a verification case exists and whether/whom it is permitted to contact. Suppression, legal basis, blocked contact and consent are independent from risk priority.
4. **Script assignment**: resolve published script bundle using market, product subtype, ILP, risk band, selling channel, contact role, language and effective-at. Combine common questions with specialized modules; generate version checksum and decision trace. Ambiguous/missing script => `AWAITING_SCRIPT` hold, not generic unapproved script.
5. **Attempt**: one record per attempt even if never connected. Browser test user is labelled operator/test; Genesys real dialing deferred. Attempt is linked to selected contact and case.
6. **Conversation**: one or more session records tied to attempt as warranted by provider lifecycle; session pins script manifest and policy fact snapshot. Verification and recording consent precede applicable questions.
7. **Response capture**: store every question execution, spoken question as delivered, customer raw utterance, revised transcript versions and typed extraction. Separate model hypothesis from deterministic rule disposition.
8. **Review**: reviewer examines question-level provenance, human annotation and discrepancies, actions, finding severity, follow-up. Maker/checker for material decisions; never overwrite evidence.
9. **Closure**: explicit verified/unverified/waived/incomplete/refused/unreachable/withdrawn reasons, case plus attempt/reporting grain, auditable outcome.

## Example synthetic mapping (NOT approved AIA call script)

| Hypothetical sale context | Risk example | Script bundle | Example controls, not prescribed phrases |
|---|---|---|---|
| Protection, standard band | Standard | `COMMON_SALES_CONDUCT` + `PROTECTION` | Did FSC identify AIA relationship? Was financial needs/gap analysis discussed? What is premium term? |
| ILP, standard band | Standard | `COMMON_SALES_CONDUCT` + `ILP` | Were financial circumstances and affordability discussed? Investment risks, charges, liquidity, surrender effects? |
| ILP, elevated SBQ band | Elevated | `COMMON_SALES_CONDUCT` + `ILP` + `ELEVATED_RISK` | Additional customer understanding and prior-sale context checks approved by S&C |
| Any sale with missing risk fields | Unknown | Hold for SBQ triage | No auto-assignment and no callable status until resolved |

**Regulatory interpretation:** MAS Fair Dealing guidance discusses fact-find, financial objectives and risk profiling for advice. It does NOT mean every example question is mandated verbatim in a callback. AIA must identify approved policies, market applicability and legal basis. Changes based on MAS go through proposed-regulatory-change → impact → script draft → checker approval → release.

## AS-IS discovery checklist (must be answered before production)

- What triggers a callback case? New issuance, proposal, replacement, high premium, campaign, complaint, spot check, all sales?
- At what grain does SBQ work: policy, application, sale, rider, FSC transaction or sample-selection batch?
- Which sources own policy premium, customer identity, FSC, risk, physical/remote sales channel, authorized contact, and contact consent?
- Who assigns risk today? What are exact factors, weight, bands, manual override rules and effective dating? Where are source assessments retained?
- Are there separate respondent / policy owner / insured / proposer / payer rules? How is authority verified and recorded?
- What existing scripts exist by product, risk, market and language? Are they effective-dated and controlled? Does a completed script differ from an approved script?
- Which questions are compulsory and which are conditional? Which may be paraphrased? What makes YES, NO, unclear, refusal, or narrative acceptable?
- What are escalation triggers, reviewer roles, target SLAs, dispositions, retry limits and evidence-retention policies?
- What exact system integration exists for risk/party/policy/sale data? Batch delivery, service APIs, subscription or manual worklist?
- Which Okta / AD / Entra provider and authoritative group IDs will be used, and are there specific privileged-permission groups?

## Operations invariants

- A policy is not the same as a sale. One policy may generate multiple sale events and callback obligations.
- No algorithmic risk update may change an earlier recorded SBQ decision without preserving both versions.
- Case allocation, script selection and contact eligibility decisions are deterministic, versioned and explainable.
- No two active overlapping callback obligations for the same unique source event/purpose unless explicitly authorized.
- No finished survey means no claim that customer verified; absence of evidence is not affirmative evidence.
- All dates stored UTC with source timezone and local contact window information; currency includes currency code.
