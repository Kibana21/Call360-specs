"""SS-02B.3.1 fixture builder + reference interpreter, fixture schema /2 (scratch tool; not application code).

Builds the `G*` golden fixtures and runs every expected run through a minimal, independent interpreter of the
contracts as amended by owner decisions D-125 … D-137. Usage: python3 reference_interpreter_v2.py <output_dir>

It does NOT replace `reference_interpreter.py`: the historical fixtures F1–F8 (schema /1) are kept unchanged and are
still generated and checked by that script. What is different in /2 (see README.md, "Versions"):

  * A JUMP names the next CANDIDATE module; the target's eligibility condition is still evaluated (D-135).
    Not eligible after a jump -> the instance's `if_ineligible` disposition; none configured -> DRAFT_INVALID.
  * Terminal states are kept apart (D-136): COMPLETED, ENDED_WITH_OUTCOME, MANDATORY_ESCALATION, REVIEW_REQUIRED,
    MISSING_INFORMATION_HALT, DRAFT_INVALID. /1 had one halted state, `blocked: BLOCKED_UNKNOWN`.
  * ORDERED_RULES (first matching rule), set operators over option codes, typed answer inputs, the four evidence
    states, the outcome catalog with classes, and a decision's "stop and flag" as the outcome REVIEW_REQUIRED.
"""
import json
import sys
from decimal import Decimal

import reference_interpreter as v1  # helpers only: q, w, qn, e, YES_NO, validate_answer, Reject

SCHEMA = "call360.survey-studio.fixture/2"
# The controlled outcome catalog (D-133): stable codes with an explicit class. Prototype values, synthetic.
OUTCOMES = {"COMPLETED": "NORMAL_COMPLETION", "CLARIFICATION_REQUIRED": "EXCEPTION", "ESCALATE": "ESCALATION",
            "CUSTOMER_DECLINED": "EXCEPTION", "UNABLE_TO_VERIFY": "EXCEPTION", "REVIEW_REQUIRED": "REVIEW_HALT"}
FIELDS = {**v1.FIELDS}
q, w, qn, e, YES_NO = v1.q, v1.w, v1.qn, v1.e, v1.YES_NO


class Invalid(Exception):
    """The draft is incomplete or invalid at this point: nothing is decided and nothing is guessed."""
    def __init__(self, reason, at):
        self.reason, self.at = reason, at


class Halt(Exception):
    def __init__(self, state, reason, at):
        self.state, self.reason, self.at = state, reason, at


def tri_and(v): return "FALSE" if "FALSE" in v else "UNKNOWN" if "UNKNOWN" in v else "TRUE"
def tri_or(v): return "TRUE" if "TRUE" in v else "UNKNOWN" if "UNKNOWN" in v else "FALSE"


def operand(o, ctx):
    if "literal" in o:
        return "KNOWN", o["literal"]
    if "param" in o:
        return "KNOWN", ctx["params"][o["param"]]
    if "field" in o:
        v = ctx["profile"].get(o["field"])
        return ("UNKNOWN", None) if v is None else ("KNOWN", v)
    src = ctx["inputs"][o["input"]]
    a = ctx["answers"].get(f"{ctx['instance']}/{src['answer']['node']}")
    if a is None:  # not collected on the executed route: UNKNOWN — never FALSE, never an empty selection
        return "UNKNOWN", None
    return "KNOWN", a["choice"] if "choice" in a else a.get("choices", [])


def evaluate(ast, ctx):
    op = ast["op"]
    if op == "AND":
        return tri_and([evaluate(a, ctx) for a in ast["args"]])
    if op == "OR":
        return tri_or([evaluate(a, ctx) for a in ast["args"]])
    if op == "NOT":
        return {"TRUE": "FALSE", "FALSE": "TRUE", "UNKNOWN": "UNKNOWN"}[evaluate(ast["arg"], ctx)]
    (ls, lv), (rs, rv) = operand(ast["left"], ctx), operand(ast["right"], ctx)
    if ls != "KNOWN" or rs != "KNOWN":
        return "UNKNOWN"
    if op in ("GT", "GTE", "LT", "LTE"):
        a, b = Decimal(str(lv)), Decimal(str(rv))
        r = {"GT": a > b, "GTE": a >= b, "LT": a < b, "LTE": a <= b}[op]
    elif op == "EQ":
        r = lv == rv
    elif op == "NEQ":
        r = lv != rv
    elif op == "CONTAINS_ANY":
        r = any(x in lv for x in rv)
    elif op == "CONTAINS_ALL":
        r = all(x in lv for x in rv)
    elif op == "CONTAINS_NONE":
        r = not any(x in lv for x in rv)  # TRUE for a known empty selection; UNKNOWN (above) when not answered
    else:
        raise ValueError(op)
    return "TRUE" if r else "FALSE"


def eval_binding(b, lib, base):
    c = next(x for x in lib["conditions"] if x["code"] == b["condition"]["code"] and x["version"] == b["condition"]["version"])
    return evaluate(c["ast"], {**base, "params": b.get("params", {}), "inputs": b.get("inputs", {})})


def answer_state(qd, a):
    if qd["answer_type"] == "FREE_TEXT":
        return "ANSWERED" if (a.get("text") or "").strip() else "UNANSWERED"
    if qd["answer_type"] == "MULTI_SELECT" and not a.get("choices"):
        return "ANSWERED_EMPTY"
    return "ANSWERED"


def rule_matches(rule, chosen):
    opts, kind = rule["when"]["options"], rule["when"]["kind"]
    if not opts:
        return False
    return {"ANY": any(c in chosen for c in opts), "ALL": all(c in chosen for c in opts), "NONE": not any(c in chosen for c in opts)}[kind]


def run_module(lib, module, instance, run, state):
    """Returns (outcome, mandatory). `mandatory` = the step that ended the module was a mandatory-escalation answer."""
    nodes = {n["node"]: n for n in module["nodes"]}
    edges = module["edges"]
    qs = {x["code"]: x for x in lib["questions"]}
    sets = {x["code"]: x for x in lib["option_sets"]}
    base = {"profile": run.get("profile", {}), "answers": state["answers"], "instance": instance}

    def follow(node, code):
        cands = [x for x in edges if x["from"] == node and x["on"] == code] or [x for x in edges if x["from"] == node and x["on"] == "ANY"]
        if len(cands) != 1:
            raise Invalid("ROUTE_MISSING" if not cands else "AMBIGUOUS_ROUTE", f"{instance}/{node}")
        return cands[0]["to"]

    def ask(node):
        n = nodes[node]
        key = f"{instance}/{node}"
        if key in state["asked"]:
            raise Invalid("REPEATED_EXECUTION", key)
        qd = qs[n["question"]["code"]]
        a = run["answers"][key]
        v1.validate_answer(qd, sets.get(qd.get("option_set", {}).get("code")), a)
        state["asked"].append(key)
        state["answers"][key] = a
        return n, qd, a

    def option(qd, code):
        return next(o for o in sets[qd["option_set"]["code"]]["options"] if o["code"] == code)

    cur, mandatory = {"node": module["entry"]}, False
    while True:
        if "outcome" in cur:
            return cur["outcome"], mandatory
        n = nodes[cur["node"]]
        if n["type"] == "DECISION":
            res = eval_binding(n["binding"], lib, base)
            state["trace"].append(f"{instance}/{n['node']}: {res}")
            code = {"TRUE": "MATCH", "FALSE": "NO_MATCH", "UNKNOWN": "UNKNOWN"}[res]
            specific = [x for x in edges if x["from"] == n["node"] and x["on"] == code]
            if len(specific) != 1:  # a decision has no "any" route: UNKNOWN never falls through to OTHERWISE
                raise Invalid("ROUTE_MISSING", f"{instance}/{n['node']}")
            cur = specific[0]["to"]
            continue
        n, qd, a = ask(cur["node"])
        mandatory = False
        r = n["routing"]
        if r["mode"] == "SEQUENTIAL_FOLLOWUPS":
            chosen = a.get("choices", [])
            order = [o["code"] for o in sets[qd["option_set"]["code"]]["options"]]
            ints = r.get("interrupts", [])
            # a MANDATORY escalation leads whatever the configured order; then configured order; then option order
            hit = sorted((i for i in ints if i["option"] in chosen),
                         key=lambda i: (0 if option(qd, i["option"]).get("interrupt") == "MANDATORY" else 1, ints.index(i), order.index(i["option"])))
            queue, deduped = [], []
            for f in (f for f in r["followups"] if f["option"] in chosen):
                for t in f["nodes"]:
                    (deduped if t in queue else queue).append(t)
            if hit:
                is_mandatory = option(qd, hit[0]["option"]).get("interrupt") == "MANDATORY"
                state["trace"].append(f"{instance}/{n['node']}: INTERRUPT {hit[0]['option']} -> {hit[0]['outcome']}; skipped {queue}" + (" (mandatory)" if is_mandatory else ""))
                return hit[0]["outcome"], is_mandatory
            state["trace"].append(f"{instance}/{n['node']}: QUEUE {queue}" + (f"; deduped {deduped}" if deduped else ""))
            for t in queue:
                fn, fq, fa = ask(t)
                to = follow(t, fa.get("choice", "AFTER_CAPTURE"))
                if "outcome" in to:
                    return to["outcome"], False
                if not to.get("return"):
                    raise Invalid("FOLLOWUP_MUST_RETURN", f"{instance}/{t}")
            cur = r["rejoin"]
            continue
        if r["mode"] == "ORDERED_RULES":
            chosen = a.get("choices", [])
            hits = [x for x in r["rules"] if rule_matches(x, chosen)]
            if hits:  # exactly one winner: the FIRST that fits. Later fits are reported, never run.
                state["trace"].append(f"{instance}/{n['node']}: RULE {hits[0]['rule']}" + (f"; also {[x['rule'] for x in hits[1:]]}" if hits[1:] else ""))
                cur = hits[0]["to"]
            else:
                state["trace"].append(f"{instance}/{n['node']}: FALLBACK")
                cur = r["fallback"]
            if cur is None:
                raise Invalid("ROUTE_MISSING", f"{instance}/{n['node']}")
            continue
        if qd["answer_type"] == "FREE_TEXT":
            code = "AFTER_CAPTURE"
        elif qd["answer_type"] == "MULTI_SELECT":
            code = "ANY"
        else:
            code = a["choice"]
            mandatory = option(qd, code).get("interrupt") == "MANDATORY"
        cur = follow(n["node"], code)


def execute(fx, run):
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
        """Moves on from `name`. Returns (pos, jumped, terminal)."""
        if to == "@CONTINUE":
            return pos + 1, False, None
        if "survey_outcome" in to:
            return pos, False, end(to["survey_outcome"], mandatory)
        if to["instance"] not in seq:
            raise Invalid("ROUTE_MISSING", name)
        tgt = seq.index(to["instance"])
        if tgt <= pos:  # forward only: a module is never considered twice, so there is no re-entry and no loop
            raise Invalid("BACKWARD_ROUTE", name)
        for skipped in seq[pos + 1:tgt]:
            status[skipped] = {"status": "SKIPPED_BY_ROUTE"}
        return tgt, True, None

    try:
        while pos < len(seq) and terminal is None:
            name = seq[pos]
            i = insts[name]
            entry, arrival = i["entry"], "JUMP" if jumped else "SEQUENCE"
            base = {"profile": run.get("profile", {}), "answers": state["answers"], "instance": name}
            if entry["mode"] == "ALWAYS":
                go_state = "ACTIVATED"
            elif entry["mode"] == "ON_OUTCOME":
                # an ACTIVATION trigger, not an eligibility condition; a jump is another activation
                got = state["module_outcomes"].get(entry["of"])
                go_state = "ACTIVATED" if jumped or got in entry["outcomes"] else "SKIPPED_PRIOR_OUTCOME"
            else:
                # ELIGIBILITY: evaluated however the module was reached. A jump does not bypass it.
                res = eval_binding(entry["binding"], lib, base)
                state["trace"].append(f"{name}: entry {res} via {arrival}")
                policy = entry["binding"].get("unknown_policy")
                if res == "TRUE":
                    go_state = "ACTIVATED"
                elif res == "FALSE":
                    go_state = "SKIPPED_FALSE"
                elif policy is None:
                    raise Invalid("UNKNOWN_POLICY_MISSING", name)
                elif policy == "BLOCK":
                    status[name] = {"status": "HALTED_MISSING_INFORMATION"}
                    raise Halt("MISSING_INFORMATION_HALT", "ELIGIBILITY_UNKNOWN", name)
                else:
                    go_state = "SKIPPED_UNKNOWN"
            if go_state != "ACTIVATED":
                status[name] = {"status": go_state}
                if not jumped:
                    pos += 1
                    continue
                disp = i.get("if_ineligible")
                if disp is None:  # never an invented fallback
                    raise Invalid("SKIP_DISPOSITION_MISSING", name)
                state["trace"].append(f"{name}: not eligible after jump -> {json.dumps(disp, sort_keys=True)}")
                pos, jumped, terminal = go(name, disp, False)
                continue
            jumped = False
            m = mods[(i["module"]["code"], i["module"]["revision"])]
            out, mandatory = run_module(lib, m, name, run, state)
            status[name] = {"status": "ACTIVATED", "outcome": out}
            state["module_outcomes"][name] = out
            if OUTCOMES[out] == "REVIEW_HALT":  # the governed outcome: the module RAN and ended with it
                raise Halt("REVIEW_REQUIRED", "REVIEW_REQUIRED", name)
            routes = [r for r in i["routes"] if r["on"] == out]
            if len(routes) != 1:
                raise Invalid("ROUTE_MISSING", f"{name}:{out}")
            pos, jumped, terminal = go(name, routes[0]["to"], mandatory)
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
    # every question of every module that ran: answered / answered-empty / unanswered / skipped — never merged
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
            evidence[key] = answer_state(qs[n["question"]["code"]], a) if a is not None else "SKIPPED"
    return {"asked": state["asked"], "modules": [{"instance": n, **status[n]} for n in seq], "terminal": terminal,
            "trace": state["trace"], "evidence_states": evidence}


def check(fx):
    lib = fx["library"]
    qs = {x["code"]: x for x in lib["questions"]}
    sets = {x["code"]: x for x in lib["option_sets"]}
    for run in fx["expected_runs"]:
        for bad in run.get("rejected", []):
            module = next(m for m in lib["modules"] for i in fx["survey"]["instances"]
                          if i["instance"] == bad["at"].split("/")[0] and i["module"]["code"] == m["code"])
            n = next(n for n in module["nodes"] if n["node"] == bad["at"].split("/")[1])
            qd = qs[n["question"]["code"]]
            try:
                v1.validate_answer(qd, sets.get(qd.get("option_set", {}).get("code")), bad["answer"])
            except v1.Reject as r:
                assert str(r) == bad["error"], (fx["fixture"], run["name"], str(r), bad["error"])
            else:
                raise AssertionError((fx["fixture"], run["name"], "answer was accepted", bad))
        got, exp = execute(fx, run), run["expect"]
        for k in ("asked", "modules", "terminal", "trace", "evidence_states"):
            assert got[k] == exp[k], (fx["fixture"], run["name"], k, got[k], exp[k])
    return len(fx["expected_runs"])


# ------------------------------------------------------------------------------------------------------- builders
def fixture(fid, title, purpose, option_sets, questions, wordings, conditions, modules, survey, runs, fields=None):
    return {"schema": SCHEMA, "fixture": fid, "title": title, "purpose": purpose, "notice": v1.NOTICE,
            "catalog": {"fields": {k: FIELDS[k] for k in (fields or [])}, "outcomes": OUTCOMES},
            "library": {"option_sets": option_sets, "questions": questions, "wordings": wordings,
                        "conditions": conditions, "modules": modules},
            "survey": survey, "expected_runs": runs}


def inst(instance, module, entry=None, routes=None, if_ineligible=None):
    d = {"instance": instance, "module": {"code": module["code"], "revision": module["revision"]},
         "entry": entry or {"mode": "ALWAYS"}, "routes": routes or [{"on": o, "to": "@CONTINUE"} for o in module["outcomes"]]}
    if if_ineligible is not None:
        d["if_ineligible"] = if_ineligible
    return d


def survey(code, instances):
    return {"code": code, "version_label": "1.0", "language": "en", "sequence": [i["instance"] for i in instances],
            "instances": instances, "end": {"survey_outcome": "COMPLETED"}}


def mod(code, name, outcomes, nodes, edges):
    return {"code": code, "revision": 1, "name": name, "kind": "COMMON", "entry": nodes[0]["node"], "outcomes": outcomes, "nodes": nodes, "edges": edges}


def run(name, answers, expect, profile=None, rejected=None):
    d = {"name": name, "answers": answers, "expect": expect}
    if profile is not None:
        d["profile"] = profile
    if rejected:
        d["rejected"] = rejected
    return d


def exp(asked, modules, terminal, trace=None, evidence=None):
    return {"asked": asked, "modules": [{"instance": i, "status": "ACTIVATED", "outcome": o} if o in OUTCOMES else {"instance": i, "status": o} for i, o in modules],
            "terminal": terminal, "trace": trace or [], "evidence_states": evidence or {}}


Y, N = {"choice": "YES"}, {"choice": "NO"}
C_OLDER = {"code": "C-OLDER-CUSTOMER", "version": 1, "name": "Older customer", "summary": "Customer age is at least {minimum_age}",
           "params": {"minimum_age": {"type": "INTEGER", "unit": "years"}}, "inputs": {}, "fields": ["customer.age_years"],
           "ast": {"op": "GTE", "left": {"field": "customer.age_years"}, "right": {"param": "minimum_age"}}}


def jump_library():
    qa = q("Q-PREMIUM-COMFORTABLE", "YES_NO", "Customer is comfortable with the premium", YES_NO)
    qb = q("Q-BENEFITS-EXPLAINED", "YES_NO", "Benefits were explained", YES_NO)
    qsp = q("Q-CALLBACK-CONSENT", "YES_NO", "Customer agrees to a call from a specialist", YES_NO)
    qt = q("Q-NOTE-CONCERN", "YES_NO", "Customer's concern is noted for follow-up", YES_NO)
    qc = q("Q-CLOSING-ACK", "YES_NO", "Customer acknowledges the closing statement", YES_NO)
    a = mod("M-AFFORDABILITY", "Affordability", ["COMPLETED", "CLARIFICATION_REQUIRED"],
            [qn("n1", qa, "PER_CHOICE", normal_answer="YES")],
            [e("e1", "n1", "YES", outcome="COMPLETED"), e("e2", "n1", "NO", outcome="CLARIFICATION_REQUIRED")])
    b = mod("M-BENEFITS", "Benefits", ["COMPLETED"], [qn("n1", qb)], [e("e1", "n1", "ANY", outcome="COMPLETED")])
    s = mod("M-SPECIALIST", "Specialist call", ["COMPLETED"], [qn("n1", qsp)], [e("e1", "n1", "ANY", outcome="COMPLETED")])
    t = mod("M-CONCERN-NOTE", "Concern note", ["COMPLETED"], [qn("n1", qt)], [e("e1", "n1", "ANY", outcome="COMPLETED")])
    c = mod("M-CLOSING", "Closing", ["COMPLETED"], [qn("n1", qc)], [e("e1", "n1", "ANY", outcome="COMPLETED")])
    words = [w(qa, "Are you comfortable with the premium you are paying?", YES_NO), w(qb, "Did your representative explain the benefits?", YES_NO),
             w(qsp, "May one of our specialists call you?", YES_NO), w(qt, "May we note your concern for follow-up?", YES_NO),
             w(qc, "Do you acknowledge that this call has been completed?", YES_NO)]
    return [qa, qb, qsp, qt, qc], words, [a, b, s, t, c]


def jump_survey(code, policy, if_ineligible):
    qs_, words, (a, b, s, t, c) = jump_library()
    binding = {"condition": {"code": "C-OLDER-CUSTOMER", "version": 1}, "params": {"minimum_age": 60}, "unknown_policy": policy}
    sv = survey(code, [
        # the jump: "Clarification required" of Affordability names the Specialist call as the next candidate
        inst("mi-afford", a, routes=[{"on": "COMPLETED", "to": "@CONTINUE"}, {"on": "CLARIFICATION_REQUIRED", "to": {"instance": "mi-specialist"}}]),
        inst("mi-benefits", b),
        inst("mi-specialist", s, entry={"mode": "RULE", "binding": binding}, if_ineligible=if_ineligible),
        # activation by a named earlier outcome is preserved
        inst("mi-concern", t, entry={"mode": "ON_OUTCOME", "of": "mi-afford", "outcomes": ["CLARIFICATION_REQUIRED"]}),
        inst("mi-closing", c)])
    return qs_, words, [a, b, s, t, c], sv


EV = lambda **kw: {k.replace("__", "/").replace("_", "-"): v for k, v in kw.items()}  # noqa: E731


def g1():
    qs_, words, mods_, sv = jump_survey("S-JUMP-ELIGIBILITY", "BLOCK", {"survey_outcome": "CLARIFICATION_REQUIRED"})
    A = "ANSWERED"
    runs = [
        run("Jump to an ELIGIBLE module: age 67 — the jump selects it, its condition is true, it runs",
            {"mi-afford/n1": N, "mi-specialist/n1": Y, "mi-concern/n1": Y, "mi-closing/n1": Y},
            exp(["mi-afford/n1", "mi-specialist/n1", "mi-concern/n1", "mi-closing/n1"],
                [("mi-afford", "CLARIFICATION_REQUIRED"), ("mi-benefits", "SKIPPED_BY_ROUTE"), ("mi-specialist", "COMPLETED"), ("mi-concern", "COMPLETED"), ("mi-closing", "COMPLETED")],
                {"state": "COMPLETED", "survey_outcome": "COMPLETED"}, ["mi-specialist: entry TRUE via JUMP"],
                {"mi-afford/n1": A, "mi-specialist/n1": A, "mi-concern/n1": A, "mi-closing/n1": A}), profile={"customer.age_years": 67}),
        run("Jump to an INELIGIBLE module: age 40 — the jump does not bypass its condition; the skip disposition ends the call",
            {"mi-afford/n1": N},
            exp(["mi-afford/n1"],
                [("mi-afford", "CLARIFICATION_REQUIRED"), ("mi-benefits", "SKIPPED_BY_ROUTE"), ("mi-specialist", "SKIPPED_FALSE"), ("mi-concern", "NOT_REACHED"), ("mi-closing", "NOT_REACHED")],
                {"state": "ENDED_WITH_OUTCOME", "survey_outcome": "CLARIFICATION_REQUIRED"},
                ["mi-specialist: entry FALSE via JUMP", 'mi-specialist: not eligible after jump -> {"survey_outcome": "CLARIFICATION_REQUIRED"}'],
                {"mi-afford/n1": A}), profile={"customer.age_years": 40}),
        run("Jump to a module with UNKNOWN eligibility: age missing, policy BLOCK — a missing-information halt, not a skip and not a module outcome",
            {"mi-afford/n1": N},
            exp(["mi-afford/n1"],
                [("mi-afford", "CLARIFICATION_REQUIRED"), ("mi-benefits", "SKIPPED_BY_ROUTE"), ("mi-specialist", "HALTED_MISSING_INFORMATION"), ("mi-concern", "NOT_REACHED"), ("mi-closing", "NOT_REACHED")],
                {"state": "MISSING_INFORMATION_HALT", "reason": "ELIGIBILITY_UNKNOWN", "at": "mi-specialist"}, ["mi-specialist: entry UNKNOWN via JUMP"],
                {"mi-afford/n1": A}), profile={"customer.age_years": None}),
        run("No jump: in sequence the same module is skipped and the next one is considered; activation by outcome does not fire",
            {"mi-afford/n1": Y, "mi-benefits/n1": Y, "mi-closing/n1": Y},
            exp(["mi-afford/n1", "mi-benefits/n1", "mi-closing/n1"],
                [("mi-afford", "COMPLETED"), ("mi-benefits", "COMPLETED"), ("mi-specialist", "SKIPPED_FALSE"), ("mi-concern", "SKIPPED_PRIOR_OUTCOME"), ("mi-closing", "COMPLETED")],
                {"state": "COMPLETED", "survey_outcome": "COMPLETED"}, ["mi-specialist: entry FALSE via SEQUENCE"],
                {"mi-afford/n1": A, "mi-benefits/n1": A, "mi-closing/n1": A}), profile={"customer.age_years": 40}),
    ]
    return fixture("G1-jump-to-module-with-eligibility", "A jump selects a candidate; eligibility still decides",
                   "An outcome route jumps over one module to a module with an eligibility condition (UNKNOWN policy BLOCK, skip disposition: end the call). "
                   "Eligible, ineligible, unknown, and the same module reached in sequence. Activation by a named earlier outcome is preserved. D-135, D-136.",
                   [YES_NO], qs_, words, [C_OLDER], mods_, sv, runs, fields=["customer.age_years"])


def g2():
    qs_, words, mods_, sv = jump_survey("S-JUMP-SKIP-CONTINUE", "SKIP_WITH_REASON", "@CONTINUE")
    A = "ANSWERED"
    tail = {"mi-afford/n1": A, "mi-concern/n1": A, "mi-closing/n1": A}
    mods_exp = [("mi-afford", "CLARIFICATION_REQUIRED"), ("mi-benefits", "SKIPPED_BY_ROUTE"), None, ("mi-concern", "COMPLETED"), ("mi-closing", "COMPLETED")]
    runs = [
        run("Ineligible after a jump, disposition CONTINUE: the next module in sequence is considered (and is activated by the earlier outcome)",
            {"mi-afford/n1": N, "mi-concern/n1": Y, "mi-closing/n1": Y},
            exp(["mi-afford/n1", "mi-concern/n1", "mi-closing/n1"], [x or ("mi-specialist", "SKIPPED_FALSE") for x in mods_exp],
                {"state": "COMPLETED", "survey_outcome": "COMPLETED"},
                ["mi-specialist: entry FALSE via JUMP", 'mi-specialist: not eligible after jump -> "@CONTINUE"'], tail), profile={"customer.age_years": 40}),
        run("UNKNOWN after a jump, policy SKIP_WITH_REASON: skipped as 'information missing', then the same disposition",
            {"mi-afford/n1": N, "mi-concern/n1": Y, "mi-closing/n1": Y},
            exp(["mi-afford/n1", "mi-concern/n1", "mi-closing/n1"], [x or ("mi-specialist", "SKIPPED_UNKNOWN") for x in mods_exp],
                {"state": "COMPLETED", "survey_outcome": "COMPLETED"},
                ["mi-specialist: entry UNKNOWN via JUMP", 'mi-specialist: not eligible after jump -> "@CONTINUE"'], tail), profile={"customer.age_years": None}),
    ]
    return fixture("G2-jump-skip-disposition-continue", "Skip disposition: continue",
                   "The same survey with the UNKNOWN policy 'skip and record why' and the skip disposition 'continue'. D-135.",
                   [YES_NO], qs_, words, [C_OLDER], mods_, sv, runs, fields=["customer.age_years"])


def g3():
    qs_, words, mods_, sv = jump_survey("S-JUMP-NO-DISPOSITION", "BLOCK", None)
    A = "ANSWERED"
    runs = [
        run("A structurally invalid draft cannot run: ineligible after a jump with NO skip disposition — nothing is invented",
            {"mi-afford/n1": N},
            exp(["mi-afford/n1"],
                [("mi-afford", "CLARIFICATION_REQUIRED"), ("mi-benefits", "SKIPPED_BY_ROUTE"), ("mi-specialist", "SKIPPED_FALSE"), ("mi-concern", "NOT_REACHED"), ("mi-closing", "NOT_REACHED")],
                {"state": "DRAFT_INVALID", "reason": "SKIP_DISPOSITION_MISSING", "at": "mi-specialist"}, ["mi-specialist: entry FALSE via JUMP"],
                {"mi-afford/n1": A}), profile={"customer.age_years": 40}),
        run("The same draft still runs for a customer who is eligible: the gap is a validation error, not a run-time default",
            {"mi-afford/n1": N, "mi-specialist/n1": Y, "mi-concern/n1": Y, "mi-closing/n1": Y},
            exp(["mi-afford/n1", "mi-specialist/n1", "mi-concern/n1", "mi-closing/n1"],
                [("mi-afford", "CLARIFICATION_REQUIRED"), ("mi-benefits", "SKIPPED_BY_ROUTE"), ("mi-specialist", "COMPLETED"), ("mi-concern", "COMPLETED"), ("mi-closing", "COMPLETED")],
                {"state": "COMPLETED", "survey_outcome": "COMPLETED"}, ["mi-specialist: entry TRUE via JUMP"],
                {"mi-afford/n1": A, "mi-specialist/n1": A, "mi-concern/n1": A, "mi-closing/n1": A}), profile={"customer.age_years": 67}),
    ]
    return fixture("G3-jump-without-skip-disposition-is-invalid", "No skip disposition: an invalid draft, not a default",
                   "The jump target can be ineligible and has no skip disposition. Authoring validation must reject this draft "
                   "(SKIP_DISPOSITION_MISSING); executed anyway it ends DRAFT_INVALID — distinct from every outcome of a call. D-135, D-136.",
                   [YES_NO], qs_, words, [C_OLDER], mods_, sv, runs, fields=["customer.age_years"])


def g4():
    docs = {"code": "OS-CONCERNS", "version": 1, "options": [
        {"code": "PRICE", "business_label": "Price", "order": 1}, {"code": "COVER", "business_label": "Cover", "order": 2},
        {"code": "CLAIMS", "business_label": "Claims", "order": 3}, {"code": "NONE", "business_label": "None of these", "order": 4, "exclusive": True}]}
    q1 = q("Q-CONCERNS", "MULTI_SELECT", "What the customer is concerned about", docs, selection={"min": 1, "max": 3})
    q2 = q("Q-PRICE-AND-COVER", "YES_NO", "Customer wants price and cover explained together", YES_NO)
    m = mod("M-CONCERNS", "Concerns", ["COMPLETED", "CLARIFICATION_REQUIRED"],
            [qn("n1", q1, "ORDERED_RULES", rules=[
                {"rule": "r1", "when": {"kind": "ALL", "options": ["PRICE", "COVER"]}, "to": {"node": "n2"}},
                {"rule": "r2", "when": {"kind": "ANY", "options": ["PRICE", "CLAIMS"]}, "to": {"outcome": "CLARIFICATION_REQUIRED"}}],
                fallback={"outcome": "COMPLETED"}), qn("n2", q2)],
            [e("e1", "n2", "ANY", outcome="COMPLETED")])
    sv = survey("S-ORDERED-RULES", [inst("mi-c", m, routes=[{"on": "COMPLETED", "to": "@CONTINUE"}, {"on": "CLARIFICATION_REQUIRED", "to": {"survey_outcome": "CLARIFICATION_REQUIRED"}}])])
    A, S = "ANSWERED", "SKIPPED"
    done = {"state": "COMPLETED", "survey_outcome": "COMPLETED"}
    runs = [
        run("PRICE and COVER: rule 1 is the first that fits; rule 2 also fits and is NOT run",
            {"mi-c/n1": {"choices": ["COVER", "PRICE"]}, "mi-c/n2": Y},
            exp(["mi-c/n1", "mi-c/n2"], [("mi-c", "COMPLETED")], done, ["mi-c/n1: RULE r1; also ['r2']"], {"mi-c/n1": A, "mi-c/n2": A}),
            rejected=[{"at": "mi-c/n1", "answer": {"choices": []}, "error": "TOO_FEW_SELECTED"},
                      {"at": "mi-c/n1", "answer": {"choices": ["NONE", "PRICE"]}, "error": "EXCLUSIVE_OPTION_CONFLICT"}]),
        run("CLAIMS only: rule 1 does not fit, rule 2 decides", {"mi-c/n1": {"choices": ["CLAIMS"]}},
            exp(["mi-c/n1"], [("mi-c", "CLARIFICATION_REQUIRED")], {"state": "ENDED_WITH_OUTCOME", "survey_outcome": "CLARIFICATION_REQUIRED"},
                ["mi-c/n1: RULE r2"], {"mi-c/n1": A, "mi-c/n2": S})),
        run("COVER only: no rule fits, the required fallback decides", {"mi-c/n1": {"choices": ["COVER"]}},
            exp(["mi-c/n1"], [("mi-c", "COMPLETED")], done, ["mi-c/n1: FALLBACK"], {"mi-c/n1": A, "mi-c/n2": S})),
        run("The exclusive answer on its own: fallback", {"mi-c/n1": {"choices": ["NONE"]}},
            exp(["mi-c/n1"], [("mi-c", "COMPLETED")], done, ["mi-c/n1: FALLBACK"], {"mi-c/n1": A, "mi-c/n2": S})),
    ]
    return fixture("G4-first-matching-rule-routing", "First-matching-rule routing for a multi-select answer",
                   "Explicit priority, one winner, later matches reported not run, a required fallback; an invalid selection is rejected and never routed. D-126.",
                   [YES_NO, docs], [q1, q2], [w(q1, "Which of these concern you?", docs), w(q2, "Shall we explain price and cover together?", YES_NO)], [], [m], sv, runs)


def g5():
    docs = {"code": "OS-DOCUMENTS", "version": 1, "options": [
        {"code": "POLICY", "business_label": "Policy contract", "order": 1}, {"code": "SUMMARY", "business_label": "Product summary", "order": 2}]}
    q1 = q("Q-RECEIVED-ANYTHING", "YES_NO", "Customer received documents", YES_NO)
    q2 = q("Q-DOCUMENTS", "MULTI_SELECT", "Which documents the customer received", docs, selection={"min": 0, "max": 2})
    q3 = q("Q-REMARK", "FREE_TEXT", "Customer's own remark", text={"required": False, "min_length": 0, "max_length": 300}, mandatory=False)
    cond = {"code": "C-NO-POLICY-CONTRACT", "version": 1, "name": "Policy contract not received",
            "summary": "The documents received include none of: Policy contract", "params": {},
            "inputs": {"documents": {"kind": "ANSWER", "question": {"code": "Q-DOCUMENTS", "version": 1}, "answer_type": "MULTI_SELECT", "value_type": "OPTION_CODE_SET", "scope": "MODULE"}},
            "fields": [], "ast": {"op": "CONTAINS_NONE", "left": {"input": "documents"}, "right": {"literal": ["POLICY"]}}}
    m = mod("M-DOCUMENTS", "Documents", ["COMPLETED", "CLARIFICATION_REQUIRED", "REVIEW_REQUIRED"],
            [qn("n1", q1, "PER_CHOICE", normal_answer="YES"), qn("n2", q2), qn("n3", q3),
             {"node": "d1", "type": "DECISION", "binding": {"condition": {"code": "C-NO-POLICY-CONTRACT", "version": 1}, "params": {},
                                                            "inputs": {"documents": {"answer": {"node": "n2"}}}, "unknown_policy": "BLOCK"}}],
            [e("e1", "n1", "YES", node="n2"), e("e2", "n1", "NO", node="n3"), e("e3", "n2", "ANY", node="n3"), e("e4", "n3", "AFTER_CAPTURE", node="d1"),
             e("e5", "d1", "MATCH", outcome="CLARIFICATION_REQUIRED"), e("e6", "d1", "NO_MATCH", outcome="COMPLETED"),
             e("e7", "d1", "UNKNOWN", outcome="REVIEW_REQUIRED")])  # "stop and flag for review" is the governed outcome
    sv = survey("S-EVIDENCE-AND-REVIEW", [inst("mi-d", m, routes=[{"on": "COMPLETED", "to": "@CONTINUE"}, {"on": "CLARIFICATION_REQUIRED", "to": {"survey_outcome": "CLARIFICATION_REQUIRED"}},
                                                                 {"on": "REVIEW_REQUIRED", "to": {"survey_outcome": "REVIEW_REQUIRED"}}])])
    runs = [
        run("Answered: the policy contract was received — the condition is FALSE",
            {"mi-d/n1": Y, "mi-d/n2": {"choices": ["POLICY"]}, "mi-d/n3": {"text": "All fine."}},
            exp(["mi-d/n1", "mi-d/n2", "mi-d/n3"], [("mi-d", "COMPLETED")], {"state": "COMPLETED", "survey_outcome": "COMPLETED"}, ["mi-d/d1: FALSE"],
                {"mi-d/n1": "ANSWERED", "mi-d/n2": "ANSWERED", "mi-d/n3": "ANSWERED"})),
        run("A VALID EMPTY selection is known: 'none of' is TRUE. The optional remark left blank is UNANSWERED",
            {"mi-d/n1": Y, "mi-d/n2": {"choices": []}, "mi-d/n3": {"text": ""}},
            exp(["mi-d/n1", "mi-d/n2", "mi-d/n3"], [("mi-d", "CLARIFICATION_REQUIRED")], {"state": "ENDED_WITH_OUTCOME", "survey_outcome": "CLARIFICATION_REQUIRED"}, ["mi-d/d1: TRUE"],
                {"mi-d/n1": "ANSWERED", "mi-d/n2": "ANSWERED_EMPTY", "mi-d/n3": "UNANSWERED"})),
        run("A question NOT ASKED on this route is UNKNOWN — not an empty selection: the decision stops for review inside the module",
            {"mi-d/n1": N, "mi-d/n3": {"text": "Nothing arrived."}},
            exp(["mi-d/n1", "mi-d/n3"], [("mi-d", "REVIEW_REQUIRED")], {"state": "REVIEW_REQUIRED", "reason": "REVIEW_REQUIRED", "at": "mi-d", "survey_outcome": "REVIEW_REQUIRED"},
                ["mi-d/d1: UNKNOWN"], {"mi-d/n1": "ANSWERED", "mi-d/n2": "SKIPPED", "mi-d/n3": "ANSWERED"})),
    ]
    return fixture("G5-evidence-states-and-review-halt-in-module", "Four evidence states; missing versus empty; review halt inside a module",
                   "One decision reads a multi-select answer that is asked on some routes only (D-132). Answered, answered-empty, unanswered and skipped are "
                   "kept apart; a missing answer is UNKNOWN while a valid empty selection is known; the decision's stop is the governed REVIEW_REQUIRED outcome. "
                   "D-125, D-127, D-131, D-132, D-134, D-136.",
                   [YES_NO, docs], [q1, q2, q3],
                   [w(q1, "Did you receive any documents?", YES_NO), w(q2, "Which documents did you receive?", docs), w(q3, "Is there anything you would like to add?")],
                   [cond], [m], sv, runs)


def g6():
    areas = {"code": "OS-AREAS", "version": 1, "options": [
        {"code": "PREMIUM", "business_label": "Premium", "order": 1},
        {"code": "COMPLAINT", "business_label": "I want to complain", "order": 2, "interrupt": "OPTIONAL"},
        {"code": "NEVER_AGREED", "business_label": "I did not agree to this policy", "order": 3, "interrupt": "MANDATORY"}]}
    q1 = q("Q-AREAS", "MULTI_SELECT", "What the customer raises", areas, selection={"min": 1, "max": 3})
    q2 = q("Q-PREMIUM-CLEAR", "YES_NO", "Premium is clear", YES_NO)
    q3 = q("Q-PROCEED", "YES_NO", "Customer is content to proceed", YES_NO)
    m = mod("M-AREAS", "Areas", ["COMPLETED", "CUSTOMER_DECLINED", "ESCALATE"],
            [qn("n1", q1, "SEQUENTIAL_FOLLOWUPS", followups=[{"option": "PREMIUM", "nodes": ["n2"]}], no_followup=[],
                # the optional interruption is configured FIRST; the mandatory escalation must still lead
                interrupts=[{"option": "COMPLAINT", "policy": "STOP_ESCALATE", "outcome": "CUSTOMER_DECLINED"},
                            {"option": "NEVER_AGREED", "policy": "STOP_ESCALATE", "outcome": "ESCALATE"}],
                rejoin={"node": "n3"}),
             qn("n2", q2, role="FOLLOWUP"), qn("n3", q3)],
            [e("e1", "n2", "ANY", ret=True), e("e2", "n3", "ANY", outcome="COMPLETED")])
    sv = survey("S-MANDATORY-ESCALATION", [inst("mi-a", m, routes=[{"on": "COMPLETED", "to": "@CONTINUE"}, {"on": "CUSTOMER_DECLINED", "to": {"survey_outcome": "CUSTOMER_DECLINED"}},
                                                                  {"on": "ESCALATE", "to": {"survey_outcome": "ESCALATE"}}])])
    A, S = "ANSWERED", "SKIPPED"
    runs = [
        run("Mandatory escalation takes precedence over an interruption configured before it, and over the follow-ups",
            {"mi-a/n1": {"choices": ["PREMIUM", "COMPLAINT", "NEVER_AGREED"]}},
            exp(["mi-a/n1"], [("mi-a", "ESCALATE")], {"state": "MANDATORY_ESCALATION", "survey_outcome": "ESCALATE"},
                ["mi-a/n1: INTERRUPT NEVER_AGREED -> ESCALATE; skipped ['n2'] (mandatory)"], {"mi-a/n1": A, "mi-a/n2": S, "mi-a/n3": S})),
        run("An optional interruption ends the call with its outcome — an ordinary ending, NOT a mandatory escalation",
            {"mi-a/n1": {"choices": ["PREMIUM", "COMPLAINT"]}},
            exp(["mi-a/n1"], [("mi-a", "CUSTOMER_DECLINED")], {"state": "ENDED_WITH_OUTCOME", "survey_outcome": "CUSTOMER_DECLINED"},
                ["mi-a/n1: INTERRUPT COMPLAINT -> CUSTOMER_DECLINED; skipped ['n2']"], {"mi-a/n1": A, "mi-a/n2": S, "mi-a/n3": S})),
        run("No interruption: the follow-up queue runs and the module completes", {"mi-a/n1": {"choices": ["PREMIUM"]}, "mi-a/n2": Y, "mi-a/n3": Y},
            exp(["mi-a/n1", "mi-a/n2", "mi-a/n3"], [("mi-a", "COMPLETED")], {"state": "COMPLETED", "survey_outcome": "COMPLETED"},
                ["mi-a/n1: QUEUE ['n2']"], {"mi-a/n1": A, "mi-a/n2": A, "mi-a/n3": A})),
    ]
    return fixture("G6-mandatory-escalation-precedence", "Mandatory escalation precedence",
                   "A mandatory-escalation answer leads whatever else is selected and whatever the configured order; the terminal state says so. "
                   "An exception outcome is not an escalation. D-122, D-128, D-133, D-136.",
                   [YES_NO, areas], [q1, q2, q3],
                   [w(q1, "Is there anything you would like to raise?", areas), w(q2, "Is the premium clear to you now?", YES_NO), w(q3, "Are you content to proceed?", YES_NO)],
                   [], [m], sv, runs)


if __name__ == "__main__":
    out = sys.argv[1]
    total = rejected_total = 0
    builders = (g1, g2, g3, g4, g5, g6)
    for build in builders:
        fx = build()
        n = check(fx)
        total += n
        with open(f"{out}/{fx['fixture']}.json", "w") as fh:
            json.dump(fx, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        rejected = sum(len(r.get("rejected", [])) for r in fx["expected_runs"])
        rejected_total += rejected
        print(f"OK {fx['fixture']}: {n} run(s), {rejected} rejected answer(s) verified")
    print(f"ALL OK: {len(builders)} fixtures (schema /2), {total} expected runs, {rejected_total} rejected answers")
