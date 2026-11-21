"""Call360 Survey Studio — reference interpreter for fixture schema /4 (SS-02 closure correction 3, owner decision D-145).

Documentation tooling, NOT the engine. Schemas /1 (F), /2 (G) and /3 (H) are untouched and still regenerate byte-for-byte
from their own interpreters.

What /4 adds to /3 — one rule, and nothing else:

  ESCALATE IS TERMINAL   A module outcome of class ESCALATION ends the survey with that same outcome, HOWEVER the module
                         reached it: a mandatory-escalation answer (already so under /3), or an ordinary route — a
                         single-choice edge, a first-matching rule, an optional interruption, a decision. A survey route
                         for such an outcome that says anything else is the validation error ESCALATION_NOT_TERMINAL
                         (MANDATORY_ESCALATION_OVERRIDDEN when a mandatory answer can produce it) and is never followed.
                         The terminal state tells the two apart: MANDATORY_ESCALATION, or ENDED_WITH_OUTCOME.

A /3 survey whose escalation outcomes all end the call as themselves means the same under /4.

Usage: python3 reference_interpreter_v4.py <output_dir>
"""
import copy
import json
import sys

import reference_interpreter as v1
import reference_interpreter_v2 as v2
import reference_interpreter_v3 as v3

SCHEMA = "call360.survey-studio.fixture/4"
OUTCOMES = v2.OUTCOMES
q, w, qn, e, YES_NO = v1.q, v1.w, v1.qn, v1.e, v1.YES_NO
inst, survey, mod, run, exp, Y = v2.inst, v2.survey, v2.mod, v2.run, v2.exp, v2.Y


def validate(fx):
    lib, sv = fx["library"], fx["survey"]
    mods = {(m["code"], m["revision"]): m for m in lib["modules"]}
    errors = v3.validate(fx)
    for i in sv["instances"]:
        m = mods[(i["module"]["code"], i["module"]["revision"])]
        mandatory = v3.mandatory_outcomes(lib, m)
        for r in i["routes"]:
            if OUTCOMES[r["on"]] == "ESCALATION" and r["on"] not in mandatory and r["to"] != {"survey_outcome": r["on"]}:
                errors.append({"code": "ESCALATION_NOT_TERMINAL", "at": f"{i['instance']}:{r['on']}"})
    return errors


def execute(fx, run_):
    """Escalate is terminal: whatever the survey says for an escalation outcome, the call ends with that outcome."""
    governed = copy.deepcopy(fx)
    for i in governed["survey"]["instances"]:
        for r in i["routes"]:
            if OUTCOMES[r["on"]] == "ESCALATION":
                r["to"] = {"survey_outcome": r["on"]}
    return v3.execute(governed, run_)


def check(fx):
    assert validate(fx) == fx["validation"]["errors"], (fx["fixture"], "validation", validate(fx), fx["validation"]["errors"])
    for r in fx["expected_runs"]:
        got, want = execute(fx, r), r["expect"]
        for k in ("asked", "modules", "terminal", "trace", "evidence_states"):
            assert got[k] == want[k], (fx["fixture"], r["name"], k, got[k], want[k])
    return len(fx["expected_runs"])


A, S = "ANSWERED", "SKIPPED"
DONE = {"state": "COMPLETED", "survey_outcome": "COMPLETED"}
ESCALATED = {"state": "ENDED_WITH_OUTCOME", "survey_outcome": "ESCALATE"}  # an ordinary escalation: terminal, but not "mandatory"


def j1():
    help_ = {"code": "OS-HELP", "version": 1, "options": [
        {"code": "FINE", "business_label": "No, everything is fine", "order": 1},
        {"code": "SENIOR", "business_label": "Yes, I would like someone senior to call me", "order": 2}]}  # NOT a mandatory escalation
    topics = {"code": "OS-TOPICS", "version": 1, "options": [
        {"code": "PREMIUM", "business_label": "Premium", "order": 1}, {"code": "BENEFITS", "business_label": "Benefits", "order": 2},
        {"code": "DISPUTE", "business_label": "I dispute this sale", "order": 3},
        {"code": "UPSET", "business_label": "I am unhappy with the service", "order": 4, "interrupt": "OPTIONAL"}]}
    q1 = q("Q-HELP", "SINGLE_SELECT", "Customer asks for a senior call", help_)
    q2 = q("Q-TOPICS", "MULTI_SELECT", "Topics the customer raises", topics, selection={"min": 1, "max": 4})
    q3 = q("Q-RAISE", "MULTI_SELECT", "What the customer raises", topics, selection={"min": 1, "max": 4})
    q4 = q("Q-PREMIUM-CLEAR", "YES_NO", "Premium is clear", YES_NO)
    q5 = q("Q-CLOSING-ACK", "YES_NO", "Customer acknowledges the closing statement", YES_NO)
    # 1. a single-choice answer routed to Escalate by an ordinary edge
    m1 = mod("M-HELP", "Help", ["COMPLETED", "ESCALATE"], [qn("n1", q1, "PER_CHOICE", normal_answer="FINE")],
             [e("e1", "n1", "FINE", outcome="COMPLETED"), e("e2", "n1", "SENIOR", outcome="ESCALATE")])
    # 2. a first-matching rule that ends the module with Escalate
    m2 = mod("M-TOPICS", "Topics", ["COMPLETED", "ESCALATE"],
             [qn("n1", q2, "ORDERED_RULES", rules=[{"rule": "r1", "when": {"kind": "ANY", "options": ["DISPUTE"]}, "to": {"outcome": "ESCALATE"}}], fallback={"outcome": "COMPLETED"})], [])
    # 3. an OPTIONAL interruption configured to stop the follow-ups and escalate
    m3 = mod("M-RAISE", "Raise", ["COMPLETED", "ESCALATE"],
             [qn("n1", q3, "SEQUENTIAL_FOLLOWUPS", followups=[{"option": "PREMIUM", "nodes": ["n2"]}], no_followup=["BENEFITS", "DISPUTE"],
                 interrupts=[{"option": "UPSET", "policy": "STOP_ESCALATE", "outcome": "ESCALATE"}], rejoin={"outcome": "COMPLETED"}),
              qn("n2", q4, role="FOLLOWUP")],
             [e("e1", "n2", "ANY", ret=True)])
    mz = mod("M-CLOSING", "Closing", ["COMPLETED"], [qn("n1", q5)], [e("e1", "n1", "ANY", outcome="COMPLETED")])
    sv = survey("S-ESCALATE-IS-TERMINAL", [
        # each survey route for Escalate is INVALID on purpose, in a different way: continue, jump on, end as something else
        inst("mi-help", m1, routes=[{"on": "COMPLETED", "to": "@CONTINUE"}, {"on": "ESCALATE", "to": "@CONTINUE"}]),
        inst("mi-topics", m2, routes=[{"on": "COMPLETED", "to": "@CONTINUE"}, {"on": "ESCALATE", "to": {"instance": "mi-closing"}}]),
        inst("mi-raise", m3, routes=[{"on": "COMPLETED", "to": "@CONTINUE"}, {"on": "ESCALATE", "to": {"survey_outcome": "COMPLETED"}}]),
        inst("mi-closing", mz)])
    fine, calm = {"choice": "FINE"}, {"choices": ["BENEFITS"]}
    runs = [
        run("Single choice, ordinary route to Escalate: the call ends with Escalate although the survey says 'continue'",
            {"mi-help/n1": {"choice": "SENIOR"}},
            exp(["mi-help/n1"], [("mi-help", "ESCALATE"), ("mi-topics", "NOT_REACHED"), ("mi-raise", "NOT_REACHED"), ("mi-closing", "NOT_REACHED")],
                ESCALATED, [], {"mi-help/n1": A})),
        run("First-matching rule to Escalate: the call ends with Escalate although the survey jumps on to a later module",
            {"mi-help/n1": fine, "mi-topics/n1": {"choices": ["PREMIUM", "DISPUTE"]}},
            exp(["mi-help/n1", "mi-topics/n1"], [("mi-help", "COMPLETED"), ("mi-topics", "ESCALATE"), ("mi-raise", "NOT_REACHED"), ("mi-closing", "NOT_REACHED")],
                ESCALATED, ["mi-topics/n1: RULE r1"], {"mi-help/n1": A, "mi-topics/n1": A})),
        run("Optional interruption set to escalate: the call ends with Escalate although the survey would end it as Completed",
            {"mi-help/n1": fine, "mi-topics/n1": calm, "mi-raise/n1": {"choices": ["PREMIUM", "UPSET"]}},
            exp(["mi-help/n1", "mi-topics/n1", "mi-raise/n1"], [("mi-help", "COMPLETED"), ("mi-topics", "COMPLETED"), ("mi-raise", "ESCALATE"), ("mi-closing", "NOT_REACHED")],
                ESCALATED, ["mi-topics/n1: FALLBACK", "mi-raise/n1: INTERRUPT UPSET -> ESCALATE; skipped ['n2']"],
                {"mi-help/n1": A, "mi-topics/n1": A, "mi-raise/n1": A, "mi-raise/n2": S})),
        run("No escalation anywhere: every module completes and the call completes",
            {"mi-help/n1": fine, "mi-topics/n1": calm, "mi-raise/n1": {"choices": ["PREMIUM"]}, "mi-raise/n2": Y, "mi-closing/n1": Y},
            exp(["mi-help/n1", "mi-topics/n1", "mi-raise/n1", "mi-raise/n2", "mi-closing/n1"],
                [("mi-help", "COMPLETED"), ("mi-topics", "COMPLETED"), ("mi-raise", "COMPLETED"), ("mi-closing", "COMPLETED")],
                DONE, ["mi-topics/n1: FALLBACK", "mi-raise/n1: QUEUE ['n2']"],
                {"mi-help/n1": A, "mi-topics/n1": A, "mi-raise/n1": A, "mi-raise/n2": A, "mi-closing/n1": A})),
    ]
    fx = v2.fixture("J1-escalate-is-terminal-in-every-routing-mode", "Escalate is terminal, however the module reached it",
                    "Three modules end with Escalate WITHOUT a mandatory-escalation answer — by a single-choice route, a first-matching rule and an optional "
                    "interruption. The survey routes each onward in a different way. All three mappings are validation errors and none is followed: the call "
                    "ends with Escalate, as an ordinary ending (not a 'mandatory escalation'). D-145.",
                    [YES_NO, help_, topics], [q1, q2, q3, q4, q5],
                    [w(q1, "Would you like someone senior to call you?", help_), w(q2, "Which topics would you like to go through?", topics),
                     w(q3, "Is there anything you would like to raise?", topics), w(q4, "Is the premium clear to you now?", YES_NO),
                     w(q5, "Do you acknowledge that this call has been completed?", YES_NO)],
                    [], [m1, m2, m3, mz], sv, runs)
    fx["schema"] = SCHEMA
    fx["validation"] = {"errors": [{"code": "ESCALATION_NOT_TERMINAL", "at": f"{n}:ESCALATE"} for n in ("mi-help", "mi-topics", "mi-raise")]}
    return fx


if __name__ == "__main__":
    out = sys.argv[1]
    fx = j1()
    n = check(fx)
    with open(f"{out}/{fx['fixture']}.json", "w") as fh:
        json.dump(fx, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(f"OK {fx['fixture']}: {n} run(s), {len(fx['validation']['errors'])} expected validation error(s) verified")
    print(f"ALL OK: 1 fixture (schema /4), {n} expected runs")
