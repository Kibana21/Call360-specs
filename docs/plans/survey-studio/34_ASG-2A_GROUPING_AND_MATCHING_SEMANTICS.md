# ASG-2A — Requirement groups: grouping and matching semantics

**Written before implementation**, as the owner's authorisation of 2026-11-22 requires ("Document the proposed
grouping and matching semantics before implementation"). The implementation report is `35_…`.
**Simulation only.** Nothing here assigns a survey to a customer case.

## 1. What exists, and why one winner is not enough

`rule_engine.evaluate` answers one question: *of these candidate rules, which single rule wins?* It ranks every
matching rule by priority, then specificity, and returns one winner, or fails closed (`NO_MATCH`, `AMBIGUOUS`,
`INPUT_MISSING`, `TARGET_NOT_EFFECTIVE`). ASG-1 gives it every published rule of a market, each re-targeted to its
bound survey version, so an application gets **at most one survey**.

An application that needs a main survey *and* a replacement survey has two rules that should both take effect. Under
ASG-1 the one with the better global rank wins and the other is discarded. That is the defect ASG-2A removes.

## 2. The smallest additive extension

The engine is not changed and not copied. It is **called once per requirement**, each time with only the rules that
belong to that requirement. What is added is the governed statement of which rules belong together:

> A **requirement group** is a governed, versioned set of published assignment-rule versions that compete to satisfy
> ONE survey requirement.

Nothing else is new. Conditions, the nine fields, priority, specificity, the fallback flag, effective windows, the
binding of a rule version to a survey version, and every fail-closed outcome are exactly ASG-1's and the engine's.
No Script Studio table is altered: a group refers to rule versions, as a binding does.

## 3. A group

| Field | Meaning |
|---|---|
| `code`, `version` | identity; a change is a new version through the whole lifecycle |
| `market_code` | one market |
| `kind` | `PRIMARY`, `ADD_REQUIRED` or `ALTERNATIVE` |
| `name`, `purpose` | both required: every group states in words which requirement it stands for |
| `sequence` | optional whole number: the group's position in a governed ordering. Absent = no ordering was governed |
| members | one or more exact published rule versions |

Lifecycle and identity rules are those of a binding: `PROPOSED → APPROVED | REJECTED | WITHDRAWN → PUBLISHED →
SUPERSEDED | WITHDRAWN`; proposer, approver and publisher are three different people, enforced by the service and by
a database trigger. Publishing a version of a group supersedes the previous published version of the same code.

## 4. The three kinds

| Kind | It is | How many per market | When no rule in it matches |
|---|---|---|---|
| `PRIMARY` | the main survey of the application | exactly one published | the application has **no primary survey**: unresolved, never "fine" |
| `ADD_REQUIRED` | one additional, complementary survey | any number | the requirement does **not apply** to this application — a normal, stated result |
| `ALTERNATIVE` | one survey chosen from several that compete for the same requirement | any number | the requirement does not apply |

Structural rules that give the kinds their meaning (checked when a group is proposed and again at every selection):

* `ADD_REQUIRED`: every member rule must be bound to the **same survey** (the same survey definition). The rules say
  *when* the survey is required; they do not choose between surveys.
* `ALTERNATIVE`: at least two member rules, bound to at least two different surveys. Otherwise nothing competes.
* `PRIMARY`: one or more member rules; they may be bound to different surveys (products with different main surveys).

## 5. Matching within a group

For one application and one group: `rule_engine.evaluate(members re-targeted through their bindings, inputs, at)`.
The result is the engine's, word for word:

| Engine outcome in the group | The requirement is |
|---|---|
| `SELECTED` | **selected**: the winning rule's bound survey version |
| `SELECTED_BY_FALLBACK` | **selected**, by a member rule that is an explicitly governed fallback rule; stated as such |
| `NO_MATCH` | **not applicable** (`ADD_REQUIRED`, `ALTERNATIVE`) or **unresolved** (`PRIMARY`) |
| `AMBIGUOUS`, `AMBIGUOUS_SAME_TARGET` | **unresolved**: equal precedence is never broken arbitrarily |
| `INPUT_MISSING` | **unresolved**: an input a member rule reads is not known. Not "does not apply" |
| `TARGET_NOT_EFFECTIVE` | **unresolved**: the winner's survey version is superseded, withdrawn or of another market. Not replaced |
| `SURVEY_NOT_BOUND` | **unresolved**: the winner has no published binding. The requirement does not disappear |

Precedence between the alternatives of a group is the rules' own governed priority and specificity. ASG-2A adds no
priority, weight or tie-break of its own.

**Consequences worth stating.**

* A rule's rank matters only against the other rules *of its group*. A high-priority primary rule can no longer
  remove a replacement requirement.
* Fail-closed is per requirement: an unknown input read only by the replacement group leaves the primary selected
  and the replacement **unresolved** — and the whole selection is then unresolved, not silently smaller.

## 6. The policy as a whole — configuration that cannot be trusted fails closed

Checked at every selection, for the application's market:

| Condition | Result |
|---|---|
| no published `PRIMARY` group | `PRIMARY_GROUP_MISSING` — unresolved configuration |
| more than one published `PRIMARY` group | `PRIMARY_GROUP_CONFLICT` |
| a rule version is a member of more than one published group | `RULE_IN_SEVERAL_GROUPS` — its requirement is not determinable |
| a member rule version is no longer published | reported per group by the engine (`not considered: superseded`), and `MEMBER_NOT_PUBLISHED` if the group has no published member left |
| a group breaks its structural rule (§4), for example because a binding changed after it was published | `GROUP_STRUCTURE_INVALID` for that group |
| a rule with a published survey binding is in **no** group, and it **matches** the application | `BOUND_RULE_UNGROUPED` — a survey requirement of unknown role; unresolved, not dropped |
| a rule with a published binding in no group, not matching | listed as information; no effect |
| a rule with no binding and no group | a script rule that takes no part in survey assignment; ignored and counted |

Any of the first six makes the selection `UNRESOLVED_CONFIGURATION`.

## 7. The selection

    selected set = the PRIMARY selection
                 + one selection for each ADD_REQUIRED group that applies
                 + one selection for each ALTERNATIVE group that applies

Each selected survey keeps: the exact published version (id, label, content and manifest fingerprints), the rule
version that selected it, the binding that connects them, the group and its version, and the engine's reason and
full trace. Two groups that select the **same** survey version are kept as two requirements; nothing is merged or
de-duplicated, and no question is removed for resembling another.

`selection_status`: `RESOLVED` when the configuration is sound and every group is selected or not applicable;
`UNRESOLVED_REQUIREMENT` when a group is unresolved; `UNRESOLVED_CONFIGURATION` for §6.

## 8. Ordering

Only what is governed is used: the `sequence` of each group whose requirement was selected.

| Situation | `ordering.status` |
|---|---|
| one survey selected | `NOT_APPLICABLE` |
| every selected group has a `sequence` and they are all different | `GOVERNED` — the order is the ascending sequence |
| none has a `sequence` | `UNRESOLVED`, reason `ABSENT` |
| some have, some have not | `UNRESOLVED`, reason `PARTIAL` |
| two share a `sequence` | `UNRESOLVED`, reason `CONFLICTING` |

When unresolved, the surveys are *listed* in a stable way (kind, then group code) that is explicitly **not** an
order of execution. Kind does not imply order: nothing approved says a primary survey is asked first.

## 9. The composite plan

For each selected survey the existing SS-03B assembler computes that survey's plan, exactly as for a single survey,
and it is stored as its own call plan with its own fingerprint. The composite refers to them; it does not rebuild,
merge or re-route them. There is no new executor and no combined survey definition.

`plan_status`:

| Value | When |
|---|---|
| `READY` | selection `RESOLVED`, ordering `GOVERNED` or `NOT_APPLICABLE`, and every individual plan `READY` |
| `BLOCKED` | selection and ordering resolved, and at least one individual plan `BLOCKED` |
| `UNRESOLVED` | the selection (`UNRESOLVED_REQUIREMENT` or `UNRESOLVED_CONFIGURATION`) or the ordering is unresolved. Individual plans of the surveys that *were* selected are still computed and shown |

`READY` means only: the set of surveys is settled, their order is governed, and each plan can be computed. It says
nothing about whether a call may be made.

**Cross-survey behaviour is not decided.** With more than one survey, `cross_survey_policy.status` is always
`UNRESOLVED`: whether an escalation, a refusal, an incomplete answer or a terminal outcome in one survey lets the next
one proceed is a business decision nobody has made. No coordinated run is built in ASG-2A.

The composite fingerprint is the SHA-256 of the canonical composite: the application fingerprint; the policy (group
versions, rule versions and bindings used); the selected set with each version's fingerprints and each plan's
fingerprint; each requirement's outcome; the ordering; the statuses. The same policy and the same application always
give the same composite fingerprint.

## 10. One application snapshot, two vocabularies

A synthetic application is one object with two parts, fingerprinted together: `assignment_inputs` (the nine rule
fields) and `facts` (catalog fields). Nothing derives one from the other. Every composite carries
`input_consistency: UNVERIFIED` with the reason, and the screen says so. See `35_…` for the data that an approved
mapping would have to settle.

## 11. What ASG-1 keeps

The single-survey operations of ASG-1 (`/evaluations`) are unchanged and give the results they gave. ASG-2A adds
operations beside them.
