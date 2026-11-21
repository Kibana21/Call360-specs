"""Call360 Survey Studio — reference interpreter for fixture schema /3 (SS-02C, owner decisions A-1 … A-4).

Documentation tooling, NOT the engine. It generates the golden fixtures H1–H4 and checks each hand-written expectation
against an independent implementation of the rules. Schemas /1 (F1–F8) and /2 (G1–G6) are untouched; their own
interpreters still generate them byte-for-byte.

What /3 adds to /2 (everything else is identical, and a /2 survey means the same thing under /3):

  instance.activation            {"of": <earlier instance>, "outcomes": [...]} — the ACTIVATION TRIGGER: when the module is
                                 SELECTED in sequence. Independent of `entry`, which is now only the ELIGIBILITY condition
                                 (ALWAYS = none, RULE = a condition). The /1–/2 shape `entry.mode: ON_OUTCOME` is still read
                                 and equals `activation` + `entry: ALWAYS`.
  A-1                            an explicit jump SELECTS a module even when its trigger did not fire; eligibility is still
                                 evaluated — a jump never bypasses it.
  instance.if_skipped_in_sequence  the skip disposition when the module is reached IN SEQUENCE and is not eligible. Absent =
                                 the next module is considered (the normal default). `if_ineligible` (after a JUMP) keeps
                                 its /2 meaning and is still required for a jump target with an eligibility condition.
  A-4                            a MANDATORY escalation always ends the survey with its own escalation outcome. A survey
                                 route for that outcome that says anything else is a validation error
                                 (MANDATORY_ESCALATION_OVERRIDDEN) and is never followed.
  fixture.validation.errors      the authoring-validation errors expected for the survey, as [{"code", "at"}].
  trace                          "<instance>: not eligible in sequence -> <disposition>"
                                 "<instance>: mandatory escalation -> <OUTCOME>[; survey route overridden]"

Usage: python3 reference_interpreter_v3.py <output_dir>
"""
import json
import sys

import reference_interpreter as v1
import reference_interpreter_v2 as v2

SCHEMA = "call360.survey-studio.fixture/3"
OUTCOMES = v2.OUTCOMES
Invalid, Halt = v2.Invalid, v2.Halt
q, w, qn, e, YES_NO = v1.q, v1.w, v1.qn, v1.e, v1.YES_NO
inst, survey, mod, run, exp, C_OLDER = v2.inst, v2.survey, v2.mod, v2.run, v2.exp, v2.C_OLDER
Y, N = v2.Y, v2.N


def activation_of(i):
    """The activation trigger from either shape; None = selected in sequence."""
    if i.get("activation"):
        return i["activation"]
    return {"of": i["entry"]["of"], "outcomes": i["entry"]["outcomes"]} if i["entry"]["mode"] == "ON_OUTCOME" else None


def mandatory_outcomes(lib, module):
    """Outcomes this module can end with BECAUSE a mandatory-escalation answer was given."""
    sets = {x["code"]: x for x in lib["option_sets"]}
    qs = {x["code"]: x for x in lib["questions"]}
    out = set()
    for n in module["nodes"]:
        if n["type"] != "QUESTION":
            continue
        qd = qs[n["question"]["code"]]
        os_ = sets.get(qd.get("option_set", {}).get("code"), {"options": []})
        for o in os_["options"]:
            if o.get("interrupt") != "MANDATORY":
                continue
            for ed in module["edges"]:
                if ed["from"] == n["node"] and ed["on"] == o["code"] and "outcome" in ed["to"]:
                    out.add(ed["to"]["outcome"])
            for it in n["routing"].get("interrupts", []):
                if it["option"] == o["code"] and it.get("outcome"):
                    out.add(it["outcome"])
    return sorted(x for x in out if OUTCOMES[x] == "ESCALATION")


def validate(fx):
    """The authoring-validation errors of the survey that /3 defines (structure only; not a full validator)."""
    lib, sv = fx["library"], fx["survey"]
    mods = {(m["code"], m["revision"]): m for m in lib["modules"]}
    seq, insts = sv["sequence"], {i["instance"]: i for i in sv["instances"]}
    errors, jumped_to = [], set()
    for name in seq:
        i = insts[name]
        for r in i["routes"]:
            if isinstance(r["to"], dict) and "instance" in r["to"]:
                jumped_to.add(r["to"]["instance"])
        for key in ("if_ineligible", "if_skipped_in_sequence"):
            d = i.get(key)
            if isinstance(d, dict) and "instance" in d:
                jumped_to.add(d["instance"])
    for pos, name in enumerate(seq):
        i = insts[name]
        m = mods[(i["module"]["code"], i["module"]["revision"])]
        for r in i["routes"]:
            if isinstance(r["to"], dict) and "instance" in r["to"] and seq.index(r["to"]["instance"]) <= pos:
                errors.append({"code": "BACKWARD_ROUTE", "at": f"{name}:{r['on']}"})
        for o in mandatory_outcomes(lib, m):
            for r in i["routes"]:
                if r["on"] == o and r["to"] != {"survey_outcome": o}:
                    errors.append({"code": "MANDATORY_ESCALATION_OVERRIDDEN", "at": f"{name}:{o}"})
        if i["entry"]["mode"] == "RULE":
            if name in jumped_to and i.get("if_ineligible") is None:
                errors.append({"code": "SKIP_DISPOSITION_MISSING", "at": name})
            for key in ("if_ineligible", "if_skipped_in_sequence"):
                d = i.get(key)
                if isinstance(d, dict) and "instance" in d and seq.index(d["instance"]) <= pos:
                    errors.append({"code": "BACKWARD_ROUTE", "at": f"{name}:{key}"})
        a = activation_of(i)
        if a and (a["of"] not in seq or seq.index(a["of"]) >= pos or not a["outcomes"]):
            errors.append({"code": "ACTIVATION_INVALID", "at": name})
    return errors


def execute(fx, run_):
    lib, sv = fx["library"], fx["survey"]
    mods = {(m["code"], m["revision"]): m for m in lib["modules"]}
    insts = {i["instance"]: i for i in sv["instances"]}
    qs = {x["code"]: x for x in lib["questions"]}
    state = {"asked": [], "answers": {}, "trace": [], "module_outcomes": {}}
    status, seq, pos, jumped = {}, sv["sequence"], 0, False
    terminal = None

    def end(outcome, mandatory):
        if outcome == "COMPLETED":
            return {"state": "COMPLETED", "survey_outcome": outcome}
        if mandatory and OUTCOMES[outcome] == "ESCALATION":
            return {"state": "MANDATORY_ESCALATION", "survey_outcome": outcome}
        return {"state": "ENDED_WITH_OUTCOME", "survey_outcome": outcome}

    def go(name, to, mandatory):
        if to == "@CONTINUE":
            return pos + 1, False, None
        if "survey_outcome" in to:
            return pos, False, end(to["survey_outcome"], mandatory)
        if to["instance"] not in seq:
            raise Invalid("ROUTE_MISSING", name)
        tgt = seq.index(to["instance"])
        if tgt <= pos:  # forward only: no re-entry, no loop
            raise Invalid("BACKWARD_ROUTE", name)
        for skipped in seq[pos + 1:tgt]:
            status[skipped] = {"status": "SKIPPED_BY_ROUTE"}
        return tgt, True, None

    try:
        while pos < len(seq) and terminal is None:
            name = seq[pos]
            i = insts[name]
            arrival = "JUMP" if jumped else "SEQUENCE"
            base = {"profile": run_.get("profile", {}), "answers": state["answers"], "instance": name}
            go_state = "ACTIVATED"
            # 1. ACTIVATION: is the module selected? In sequence, by its trigger, or by an explicit jump (A-1).
            act = activation_of(i)
            if act and not jumped and state["module_outcomes"].get(act["of"]) not in act["outcomes"]:
                go_state = "SKIPPED_PRIOR_OUTCOME"  # not selected: its eligibility is not evaluated
            # 2. ELIGIBILITY: may the selected module execute? Never bypassed, however it was selected.
            elif i["entry"]["mode"] == "RULE":
                res = v2.eval_binding(i["entry"]["binding"], lib, base)
                state["trace"].append(f"{name}: entry {res} via {arrival}")
                policy = i["entry"]["binding"].get("unknown_policy")
                if res == "FALSE":
                    go_state = "SKIPPED_FALSE"
                elif res == "UNKNOWN" and policy is None:
                    raise Invalid("UNKNOWN_POLICY_MISSING", name)
                elif res == "UNKNOWN" and policy == "BLOCK":
                    status[name] = {"status": "HALTED_MISSING_INFORMATION"}
                    raise Halt("MISSING_INFORMATION_HALT", "ELIGIBILITY_UNKNOWN", name)
                elif res == "UNKNOWN":
                    go_state = "SKIPPED_UNKNOWN"
            if go_state != "ACTIVATED":
                status[name] = {"status": go_state}
                if go_state == "SKIPPED_PRIOR_OUTCOME":
                    pos += 1
                    continue
                if jumped:
                    disp = i.get("if_ineligible")
                    if disp is None:  # after a jump nothing is invented
                        raise Invalid("SKIP_DISPOSITION_MISSING", name)
                    state["trace"].append(f"{name}: not eligible after jump -> {json.dumps(disp, sort_keys=True)}")
                else:
                    disp = i.get("if_skipped_in_sequence")
                    if disp is None:  # in sequence the normal default: the next module is considered
                        pos += 1
                        continue
                    state["trace"].append(f"{name}: not eligible in sequence -> {json.dumps(disp, sort_keys=True)}")
                pos, jumped, terminal = go(name, disp, False)
                continue
            jumped = False
            m = mods[(i["module"]["code"], i["module"]["revision"])]
            out, mandatory = v2.run_module(lib, m, name, run_, state)
            status[name] = {"status": "ACTIVATED", "outcome": out}
            state["module_outcomes"][name] = out
            if OUTCOMES[out] == "REVIEW_HALT":
                raise Halt("REVIEW_REQUIRED", "REVIEW_REQUIRED", name)
            routes = [r for r in i["routes"] if r["on"] == out]
            if mandatory:
                # A-4: survey-level routing cannot override a mandatory escalation
                if OUTCOMES[out] != "ESCALATION":
                    raise Invalid("MANDATORY_ESCALATION_WEAKENED", name)
                honoured = len(routes) == 1 and routes[0]["to"] == {"survey_outcome": out}
                state["trace"].append(f"{name}: mandatory escalation -> {out}" + ("" if honoured else "; survey route overridden"))
                terminal = end(out, True)
                continue
            if len(routes) != 1:
                raise Invalid("ROUTE_MISSING", f"{name}:{out}")
            pos, jumped, terminal = go(name, routes[0]["to"], False)
        if terminal is None:
            terminal = end(sv["end"]["survey_outcome"], False)
    except Halt as h:
        terminal = {"state": h.state, "reason": h.reason, "at": h.at}
        if h.state == "REVIEW_REQUIRED":
            terminal["survey_outcome"] = "REVIEW_REQUIRED"
    except Invalid as b:
        terminal = {"state": "DRAFT_INVALID", "reason": b.reason, "at": b.at}
    for name in seq:
        status.setdefault(name, {"status": "NOT_REACHED"})
    evidence = {}
    for name in seq:
        if status[name]["status"] != "ACTIVATED":
            continue
        m = mods[(insts[name]["module"]["code"], insts[name]["module"]["revision"])]
        for n in m["nodes"]:
            if n["type"] != "QUESTION":
                continue
            key = f"{name}/{n['node']}"
            a = state["answers"].get(key)
            evidence[key] = v2.answer_state(qs[n["question"]["code"]], a) if a is not None else "SKIPPED"
    return {"asked": state["asked"], "modules": [{"instance": n, **status[n]} for n in seq], "terminal": terminal,
            "trace": state["trace"], "evidence_states": evidence}


def check(fx):
    assert validate(fx) == fx["validation"]["errors"], (fx["fixture"], "validation", validate(fx), fx["validation"]["errors"])
    for r in fx["expected_runs"]:
        got, want = execute(fx, r), r["expect"]
        for k in ("asked", "modules", "terminal", "trace", "evidence_states"):
            assert got[k] == want[k], (fx["fixture"], r["name"], k, got[k], want[k])
    return len(fx["expected_runs"])


def fixture(fid, title, purpose, option_sets, questions, wordings, conditions, modules, sv, runs, fields=None, errors=None):
    fx = v2.fixture(fid, title, purpose, option_sets, questions, wordings, conditions, modules, sv, runs, fields=fields)
    fx["schema"] = SCHEMA
    fx["validation"] = {"errors": errors or []}
    return fx


def older(minimum, policy):
    return {"mode": "RULE", "binding": {"condition": {"code": "C-OLDER-CUSTOMER", "version": 1}, "params": {"minimum_age": minimum}, "unknown_policy": policy}}


A, S = "ANSWERED", "SKIPPED"
CLAR = "CLARIFICATION_REQUIRED"
DONE = {"state": "COMPLETED", "survey_outcome": "COMPLETED"}
ENDS_CLAR = {"state": "ENDED_WITH_OUTCOME", "survey_outcome": CLAR}


def h1():
    qs_, words, (a, b, s, t, c) = v2.jump_library()
    trig = {"of": "mi-afford", "outcomes": [CLAR]}
    sv = survey("S-ACTIVATION-AND-ELIGIBILITY", [
        inst("mi-afford", a),  # no jump: both outcomes continue in sequence
        inst("mi-benefits", b),
        # BOTH: selected only after Affordability ends with "Clarification required"; and then eligible only for older customers
        {**inst("mi-specialist", s, entry=older(60, "SKIP_WITH_REASON")), "activation": trig},
        # the earlier shape of a trigger with no eligibility condition: still read, unchanged in meaning
        inst("mi-concern", t, entry={"mode": "ON_OUTCOME", **trig}),
        inst("mi-closing", c)])
    full = ["mi-afford/n1", "mi-benefits/n1", "mi-specialist/n1", "mi-concern/n1", "mi-closing/n1"]
    yes = {k: Y for k in full}
    no_first = {**yes, "mi-afford/n1": N}
    part = ["mi-afford/n1", "mi-benefits/n1", "mi-concern/n1", "mi-closing/n1"]
    runs = [
        run("Trigger fired AND eligible: selected by the named outcome, eligibility is true, it runs", no_first,
            exp(full, [("mi-afford", CLAR), ("mi-benefits", "COMPLETED"), ("mi-specialist", "COMPLETED"), ("mi-concern", "COMPLETED"), ("mi-closing", "COMPLETED")],
                DONE, ["mi-specialist: entry TRUE via SEQUENCE"], {k: A for k in full}), profile={"customer.age_years": 67}),
        run("Trigger fired but NOT eligible: being selected is not enough — it is skipped as 'did not match'", no_first,
            exp(part, [("mi-afford", CLAR), ("mi-benefits", "COMPLETED"), ("mi-specialist", "SKIPPED_FALSE"), ("mi-concern", "COMPLETED"), ("mi-closing", "COMPLETED")],
                DONE, ["mi-specialist: entry FALSE via SEQUENCE"], {k: A for k in part}), profile={"customer.age_years": 40}),
        run("Trigger fired, eligibility UNKNOWN with 'skip and record why': skipped as 'information missing', never as 'did not match'", no_first,
            exp(part, [("mi-afford", CLAR), ("mi-benefits", "COMPLETED"), ("mi-specialist", "SKIPPED_UNKNOWN"), ("mi-concern", "COMPLETED"), ("mi-closing", "COMPLETED")],
                DONE, ["mi-specialist: entry UNKNOWN via SEQUENCE"], {k: A for k in part}), profile={"customer.age_years": None}),
        run("Trigger NOT fired: the module is not selected, so its eligibility is not even evaluated — although the customer would be eligible", yes,
            exp(["mi-afford/n1", "mi-benefits/n1", "mi-closing/n1"],
                [("mi-afford", "COMPLETED"), ("mi-benefits", "COMPLETED"), ("mi-specialist", "SKIPPED_PRIOR_OUTCOME"), ("mi-concern", "SKIPPED_PRIOR_OUTCOME"), ("mi-closing", "COMPLETED")],
                DONE, [], {"mi-afford/n1": A, "mi-benefits/n1": A, "mi-closing/n1": A}), profile={"customer.age_years": 67}),
    ]
    return fixture("H1-activation-and-eligibility-are-independent", "Activation and eligibility are independent",
                   "One module carries BOTH an activation trigger (selected only after a named earlier outcome) and an eligibility condition "
                   "(may run only for older customers). The four combinations, plus the earlier ON_OUTCOME shape read unchanged. A-2.",
                   [YES_NO], qs_, words, [C_OLDER], [a, b, s, t, c], sv, runs, fields=["customer.age_years"])


def h2():
    qs_, words, (a, b, s, t, c) = v2.jump_library()
    sv = survey("S-JUMP-IS-AN-ACTIVATION", [
        inst("mi-afford", a, routes=[{"on": "COMPLETED", "to": "@CONTINUE"}, {"on": CLAR, "to": {"instance": "mi-specialist"}}]),
        inst("mi-benefits", b),
        # its trigger waits for Benefits — which the jump passes over, so in a jumped run the trigger can never fire
        {**inst("mi-specialist", s, entry=older(60, "BLOCK"), if_ineligible={"survey_outcome": CLAR}), "activation": {"of": "mi-benefits", "outcomes": ["COMPLETED"]}},
        # the earlier shape, jumped to from the specialist call
        inst("mi-concern", t, entry={"mode": "ON_OUTCOME", "of": "mi-benefits", "outcomes": ["COMPLETED"]}),
        inst("mi-closing", c)])
    sv["instances"][2]["routes"] = [{"on": "COMPLETED", "to": "@CONTINUE"}]
    runs = [
        run("An explicit jump SELECTS a module whose trigger did not fire; eligibility is still checked and is true, so it runs",
            {"mi-afford/n1": N, "mi-specialist/n1": Y, "mi-closing/n1": Y},
            exp(["mi-afford/n1", "mi-specialist/n1", "mi-closing/n1"],
                [("mi-afford", CLAR), ("mi-benefits", "SKIPPED_BY_ROUTE"), ("mi-specialist", "COMPLETED"), ("mi-concern", "SKIPPED_PRIOR_OUTCOME"), ("mi-closing", "COMPLETED")],
                DONE, ["mi-specialist: entry TRUE via JUMP"], {"mi-afford/n1": A, "mi-specialist/n1": A, "mi-closing/n1": A}), profile={"customer.age_years": 67}),
        run("The jump selects it but never bypasses eligibility: not eligible, so the configured skip disposition ends the call",
            {"mi-afford/n1": N},
            exp(["mi-afford/n1"],
                [("mi-afford", CLAR), ("mi-benefits", "SKIPPED_BY_ROUTE"), ("mi-specialist", "SKIPPED_FALSE"), ("mi-concern", "NOT_REACHED"), ("mi-closing", "NOT_REACHED")],
                ENDS_CLAR, ["mi-specialist: entry FALSE via JUMP", 'mi-specialist: not eligible after jump -> {"survey_outcome": "CLARIFICATION_REQUIRED"}'],
                {"mi-afford/n1": A}), profile={"customer.age_years": 40}),
        run("No jump: in sequence the trigger fires (Benefits completed) and the customer is eligible, so it runs; so does the earlier-shape module",
            {"mi-afford/n1": Y, "mi-benefits/n1": Y, "mi-specialist/n1": Y, "mi-concern/n1": Y, "mi-closing/n1": Y},
            exp(["mi-afford/n1", "mi-benefits/n1", "mi-specialist/n1", "mi-concern/n1", "mi-closing/n1"],
                [("mi-afford", "COMPLETED"), ("mi-benefits", "COMPLETED"), ("mi-specialist", "COMPLETED"), ("mi-concern", "COMPLETED"), ("mi-closing", "COMPLETED")],
                DONE, ["mi-specialist: entry TRUE via SEQUENCE"],
                {"mi-afford/n1": A, "mi-benefits/n1": A, "mi-specialist/n1": A, "mi-concern/n1": A, "mi-closing/n1": A}), profile={"customer.age_years": 67}),
        run("No jump, not eligible: in sequence the normal default applies — the next module is considered (the jump disposition is not used)",
            {"mi-afford/n1": Y, "mi-benefits/n1": Y, "mi-concern/n1": Y, "mi-closing/n1": Y},
            exp(["mi-afford/n1", "mi-benefits/n1", "mi-concern/n1", "mi-closing/n1"],
                [("mi-afford", "COMPLETED"), ("mi-benefits", "COMPLETED"), ("mi-specialist", "SKIPPED_FALSE"), ("mi-concern", "COMPLETED"), ("mi-closing", "COMPLETED")],
                DONE, ["mi-specialist: entry FALSE via SEQUENCE"],
                {"mi-afford/n1": A, "mi-benefits/n1": A, "mi-concern/n1": A, "mi-closing/n1": A}), profile={"customer.age_years": 40}),
    ]
    return fixture("H2-a-jump-is-an-activation-but-never-bypasses-eligibility", "An explicit jump is a valid activation; it never bypasses eligibility",
                   "A module with an activation trigger AND an eligibility condition is the target of a jump that passes over the module its trigger waits for. "
                   "The jump selects it; its eligibility still decides. A-1, A-2, D-135.",
                   [YES_NO], qs_, words, [C_OLDER], [a, b, s, t, c], sv, runs, fields=["customer.age_years"])


def h3():
    qs_, words, (a, b, s, t, c) = v2.jump_library()
    sv = survey("S-SKIP-DISPOSITION-IN-SEQUENCE", [
        inst("mi-afford", a),
        # not eligible in sequence -> go to a LATER module (forward only)
        {**inst("mi-specialist", s, entry=older(60, "SKIP_WITH_REASON")), "if_skipped_in_sequence": {"instance": "mi-closing"}},
        inst("mi-benefits", b),
        # not eligible in sequence -> end the call with an approved outcome
        {**inst("mi-concern", t, entry=older(70, "SKIP_WITH_REASON")), "if_skipped_in_sequence": {"survey_outcome": CLAR}},
        inst("mi-closing", c)])
    full = ["mi-afford/n1", "mi-specialist/n1", "mi-benefits/n1", "mi-concern/n1", "mi-closing/n1"]
    yes = {k: Y for k in full}
    to_closing = 'mi-specialist: not eligible in sequence -> {"instance": "mi-closing"}'
    runs = [
        run("Both eligible: nothing is skipped and no disposition is used", yes,
            exp(full, [(n.split("/")[0], "COMPLETED") for n in full], DONE,
                ["mi-specialist: entry TRUE via SEQUENCE", "mi-concern: entry TRUE via SEQUENCE"], {k: A for k in full}), profile={"customer.age_years": 75}),
        run("The later module is not eligible in sequence: its disposition ends the call with the configured outcome", yes,
            exp(full[:3], [("mi-afford", "COMPLETED"), ("mi-specialist", "COMPLETED"), ("mi-benefits", "COMPLETED"), ("mi-concern", "SKIPPED_FALSE"), ("mi-closing", "NOT_REACHED")],
                ENDS_CLAR, ["mi-specialist: entry TRUE via SEQUENCE", "mi-concern: entry FALSE via SEQUENCE", 'mi-concern: not eligible in sequence -> {"survey_outcome": "CLARIFICATION_REQUIRED"}'],
                {k: A for k in full[:3]}), profile={"customer.age_years": 65}),
        run("The earlier module is not eligible in sequence: its disposition goes forward to a later module; the ones between are passed over", yes,
            exp(["mi-afford/n1", "mi-closing/n1"],
                [("mi-afford", "COMPLETED"), ("mi-specialist", "SKIPPED_FALSE"), ("mi-benefits", "SKIPPED_BY_ROUTE"), ("mi-concern", "SKIPPED_BY_ROUTE"), ("mi-closing", "COMPLETED")],
                DONE, ["mi-specialist: entry FALSE via SEQUENCE", to_closing], {"mi-afford/n1": A, "mi-closing/n1": A}), profile={"customer.age_years": 40}),
        run("Eligibility UNKNOWN with 'skip and record why': the same disposition, with the reason kept as 'information missing'", yes,
            exp(["mi-afford/n1", "mi-closing/n1"],
                [("mi-afford", "COMPLETED"), ("mi-specialist", "SKIPPED_UNKNOWN"), ("mi-benefits", "SKIPPED_BY_ROUTE"), ("mi-concern", "SKIPPED_BY_ROUTE"), ("mi-closing", "COMPLETED")],
                DONE, ["mi-specialist: entry UNKNOWN via SEQUENCE", to_closing], {"mi-afford/n1": A, "mi-closing/n1": A}), profile={"customer.age_years": None}),
    ]
    return fixture("H3-skip-disposition-in-sequence", "A configured skip disposition for a module reached in sequence",
                   "Reached in sequence, a module that is not eligible normally lets the next module be considered. Here two modules configure something else: "
                   "a later module, and an approved terminal outcome. Forward only. A-3.",
                   [YES_NO], qs_, words, [C_OLDER], [a, b, s, t, c], sv, runs, fields=["customer.age_years"])


def h4():
    consent = {"code": "OS-CONSENT", "version": 1, "options": [
        {"code": "AGREED", "business_label": "Yes, I agreed", "order": 1},
        {"code": "NEVER_AGREED", "business_label": "I did not agree to this policy", "order": 2, "interrupt": "MANDATORY"}]}
    areas = {"code": "OS-AREAS", "version": 1, "options": [
        {"code": "PREMIUM", "business_label": "Premium", "order": 1},
        {"code": "COMPLAINT", "business_label": "I want to complain", "order": 2, "interrupt": "OPTIONAL"},
        {"code": "FORGED", "business_label": "My signature was forged", "order": 3, "interrupt": "MANDATORY"}]}
    q0 = q("Q-CONSENT", "SINGLE_SELECT", "Customer agreed to the policy", consent)
    q1 = q("Q-AREAS", "MULTI_SELECT", "What the customer raises", areas, selection={"min": 1, "max": 3})
    q2 = q("Q-PREMIUM-CLEAR", "YES_NO", "Premium is clear", YES_NO)
    q3 = q("Q-CLOSING-ACK", "YES_NO", "Customer acknowledges the closing statement", YES_NO)
    mc = mod("M-CONSENT", "Consent", ["COMPLETED", "ESCALATE"], [qn("n1", q0, "PER_CHOICE", normal_answer="AGREED")],
             [e("e1", "n1", "AGREED", outcome="COMPLETED"), e("e2", "n1", "NEVER_AGREED", outcome="ESCALATE")])
    ma = mod("M-AREAS", "Areas", ["COMPLETED", "CUSTOMER_DECLINED", "ESCALATE"],
             [qn("n1", q1, "SEQUENTIAL_FOLLOWUPS", followups=[{"option": "PREMIUM", "nodes": ["n2"]}], no_followup=[],
                 interrupts=[{"option": "COMPLAINT", "policy": "STOP_ESCALATE", "outcome": "CUSTOMER_DECLINED"},
                             {"option": "FORGED", "policy": "STOP_ESCALATE", "outcome": "ESCALATE"}],
                 rejoin={"outcome": "COMPLETED"}),
              qn("n2", q2, role="FOLLOWUP")],
             [e("e1", "n2", "ANY", ret=True)])
    mz = mod("M-CLOSING", "Closing", ["COMPLETED"], [qn("n1", q3)], [e("e1", "n1", "ANY", outcome="COMPLETED")])
    sv = survey("S-MANDATORY-ESCALATION-SURVEY-LEVEL", [
        # INVALID on purpose: the survey tries to JUMP on with the mandatory-escalation outcome of a single-choice question
        inst("mi-consent", mc, routes=[{"on": "COMPLETED", "to": "@CONTINUE"}, {"on": "ESCALATE", "to": {"instance": "mi-closing"}}]),
        # INVALID on purpose: the survey tries to CONTINUE with the mandatory-escalation outcome of a multi-select question
        inst("mi-areas", ma, routes=[{"on": "COMPLETED", "to": "@CONTINUE"}, {"on": "CUSTOMER_DECLINED", "to": {"survey_outcome": "CUSTOMER_DECLINED"}},
                                     {"on": "ESCALATE", "to": "@CONTINUE"}]),
        inst("mi-closing", mz)])
    ok = {"choice": "AGREED"}
    runs = [
        run("Single-choice mandatory answer: the call ends with Escalate although the survey routes that outcome to a later module",
            {"mi-consent/n1": {"choice": "NEVER_AGREED"}},
            exp(["mi-consent/n1"], [("mi-consent", "ESCALATE"), ("mi-areas", "NOT_REACHED"), ("mi-closing", "NOT_REACHED")],
                {"state": "MANDATORY_ESCALATION", "survey_outcome": "ESCALATE"}, ["mi-consent: mandatory escalation -> ESCALATE; survey route overridden"], {"mi-consent/n1": A})),
        run("Multi-select mandatory answer, selected with others: it leads, and the call ends with Escalate although the survey says 'continue'",
            {"mi-consent/n1": ok, "mi-areas/n1": {"choices": ["PREMIUM", "COMPLAINT", "FORGED"]}},
            exp(["mi-consent/n1", "mi-areas/n1"], [("mi-consent", "COMPLETED"), ("mi-areas", "ESCALATE"), ("mi-closing", "NOT_REACHED")],
                {"state": "MANDATORY_ESCALATION", "survey_outcome": "ESCALATE"},
                ["mi-areas/n1: INTERRUPT FORGED -> ESCALATE; skipped ['n2'] (mandatory)", "mi-areas: mandatory escalation -> ESCALATE; survey route overridden"],
                {"mi-consent/n1": A, "mi-areas/n1": A, "mi-areas/n2": S})),
        run("An optional interruption is ordinary routing: it follows the survey's route for its outcome and is NOT a mandatory escalation",
            {"mi-consent/n1": ok, "mi-areas/n1": {"choices": ["PREMIUM", "COMPLAINT"]}},
            exp(["mi-consent/n1", "mi-areas/n1"], [("mi-consent", "COMPLETED"), ("mi-areas", "CUSTOMER_DECLINED"), ("mi-closing", "NOT_REACHED")],
                {"state": "ENDED_WITH_OUTCOME", "survey_outcome": "CUSTOMER_DECLINED"},
                ["mi-areas/n1: INTERRUPT COMPLAINT -> CUSTOMER_DECLINED; skipped ['n2']"], {"mi-consent/n1": A, "mi-areas/n1": A, "mi-areas/n2": S})),
        run("No escalation: the follow-up runs and the call completes",
            {"mi-consent/n1": ok, "mi-areas/n1": {"choices": ["PREMIUM"]}, "mi-areas/n2": Y, "mi-closing/n1": Y},
            exp(["mi-consent/n1", "mi-areas/n1", "mi-areas/n2", "mi-closing/n1"], [("mi-consent", "COMPLETED"), ("mi-areas", "COMPLETED"), ("mi-closing", "COMPLETED")],
                DONE, ["mi-areas/n1: QUEUE ['n2']"], {"mi-consent/n1": A, "mi-areas/n1": A, "mi-areas/n2": A, "mi-closing/n1": A})),
    ]
    return fixture("H4-mandatory-escalation-cannot-be-overridden-by-survey-routing", "A mandatory escalation cannot be overridden by survey-level routing",
                   "Two modules end with Escalate because of a mandatory-escalation answer (one single-choice, one multi-select). The survey routes that outcome "
                   "to a later module and to 'continue'. Both mappings are validation errors, and neither is ever followed: the call ends with Escalate. A-4.",
                   [YES_NO, consent, areas], [q0, q1, q2, q3],
                   [w(q0, "Did you agree to take up this policy?", consent), w(q1, "Is there anything you would like to raise?", areas),
                    w(q2, "Is the premium clear to you now?", YES_NO), w(q3, "Do you acknowledge that this call has been completed?", YES_NO)],
                   [], [mc, ma, mz], sv, runs,
                   errors=[{"code": "MANDATORY_ESCALATION_OVERRIDDEN", "at": "mi-consent:ESCALATE"}, {"code": "MANDATORY_ESCALATION_OVERRIDDEN", "at": "mi-areas:ESCALATE"}])


if __name__ == "__main__":
    out = sys.argv[1]
    total = 0
    builders = (h1, h2, h3, h4)
    for build in builders:
        fx = build()
        n = check(fx)
        total += n
        with open(f"{out}/{fx['fixture']}.json", "w") as fh:
            json.dump(fx, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        print(f"OK {fx['fixture']}: {n} run(s), {len(fx['validation']['errors'])} expected validation error(s) verified")
    print(f"ALL OK: {len(builders)} fixtures (schema /3), {total} expected runs")
