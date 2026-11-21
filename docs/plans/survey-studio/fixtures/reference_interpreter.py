"""SS-01 fixture builder + reference interpreter (scratch tool; not application code).

Builds the eight canonical JSON fixtures, runs every expected run through a minimal interpreter of the SS-01
contracts and fails if any expectation differs. Usage: python3 build_fixtures.py <output_dir>
"""
import json
import sys
from decimal import Decimal

SCHEMA = "call360.survey-studio.fixture/1"
NOTICE = ("Synthetic and illustrative. Wording, thresholds and outcomes are examples for contract design only; "
          "nothing here is approved AIA/MAS language or business policy.")

FIELDS = {
    "policy.product_family": {"type": "ENUM", "values": ["PROTECTION", "ILP", "ENDOWMENT"], "label": "Product family"},
    "policy.annual_premium": {"type": "MONEY", "unit": "SGD", "label": "Annual premium"},
    "policy.sum_assured": {"type": "MONEY", "unit": "SGD", "label": "Sum assured"},
    "policy.is_replacement": {"type": "BOOLEAN", "label": "Policy replacement"},
    "customer.age_years": {"type": "INTEGER", "unit": "years", "label": "Customer age"},
}
OUTCOMES = ["COMPLETED", "CLARIFICATION_REQUIRED", "ESCALATE", "CUSTOMER_DECLINED", "UNABLE_TO_VERIFY"]

YES_NO = {"code": "OS-YES-NO", "version": 1, "options": [
    {"code": "YES", "business_label": "Yes", "order": 1}, {"code": "NO", "business_label": "No", "order": 2}]}


def q(code, answer_type, intent, option_set=None, selection=None, text=None, mandatory=True):
    d = {"code": code, "version": 1, "answer_type": answer_type, "intent": intent, "mandatory": mandatory}
    if option_set:
        d["option_set"] = {"code": option_set["code"], "version": option_set["version"]}
    if selection:
        d["selection"] = selection
    if text:
        d["text"] = text
    return d


def w(question, text, option_set=None, option_texts=None, other_prompt=None):
    d = {"question": question["code"], "wording_version": 1, "language": "en",
         "binds_to": {"answer_type": question["answer_type"],
                      "option_codes": [o["code"] for o in option_set["options"]] if option_set else []},
         "text": text, "delivery_mode": "CONVERSATIONAL", "approval": "SYNTHETIC_UNAPPROVED"}
    if option_set:
        d["option_texts"] = option_texts or {o["code"]: o["business_label"] for o in option_set["options"]}
    if other_prompt:
        d["other_prompt"] = other_prompt
    return d


def qn(node, question, mode="ALL_TO_NEXT", role=None, **routing):
    d = {"node": node, "type": "QUESTION",
         "question": {"code": question["code"], "version": 1, "wording_version": 1},
         "routing": {"mode": mode, **routing}}
    if role:
        d["role"] = role
    return d


def e(edge, frm, on, node=None, outcome=None, ret=False):
    to = {"node": node} if node else {"outcome": outcome} if outcome else {"return": True}
    return {"edge": edge, "from": frm, "on": on, "to": to}


def fixture(fid, title, purpose, option_sets, questions, wordings, conditions, modules, survey, runs, fields=None):
    return {"schema": SCHEMA, "fixture": fid, "title": title, "purpose": purpose, "notice": NOTICE,
            "catalog": {"fields": {k: FIELDS[k] for k in (fields or [])}, "outcomes": OUTCOMES},
            "library": {"option_sets": option_sets, "questions": questions, "wordings": wordings,
                        "conditions": conditions, "modules": modules},
            "survey": survey, "expected_runs": runs}


def inst(instance, module, entry=None, routes=None):
    return {"instance": instance, "module": {"code": module["code"], "revision": module["revision"]},
            "entry": entry or {"mode": "ALWAYS"},
            "routes": routes or [{"on": o, "to": "@CONTINUE"} for o in module["outcomes"]]}


def survey(code, instances):
    return {"code": code, "version_label": "1.0", "language": "en", "sequence": [i["instance"] for i in instances],
            "instances": instances, "end": {"survey_outcome": "COMPLETED"}}


# ------------------------------------------------------------------------------------------- reference interpreter
class Reject(Exception):
    pass


class Blocked(Exception):
    def __init__(self, reason, at):
        self.reason, self.at = reason, at


def tri_and(vals):
    return "FALSE" if "FALSE" in vals else "UNKNOWN" if "UNKNOWN" in vals else "TRUE"


def tri_or(vals):
    return "TRUE" if "TRUE" in vals else "UNKNOWN" if "UNKNOWN" in vals else "FALSE"


def tri_not(v):
    return {"TRUE": "FALSE", "FALSE": "TRUE", "UNKNOWN": "UNKNOWN"}[v]


def operand(o, ctx):
    """Returns (state, value)."""
    if "literal" in o:
        return "KNOWN", o["literal"]
    if "param" in o:
        return "KNOWN", ctx["params"][o["param"]]
    if "field" in o:
        v = ctx["profile"].get(o["field"])
        return ("UNKNOWN", None) if v is None else ("KNOWN", v)
    if "input" in o:
        src = ctx["inputs"][o["input"]]
        if "answer" in src:
            key = f"{src['answer'].get('instance', ctx['instance'])}/{src['answer']['node']}"
            a = ctx["answers"].get(key)
            if a is None:
                return "UNKNOWN", None
            return "KNOWN", a.get("choice") if "choice" in a else a.get("choices")
        if "module_outcome" in src:
            v = ctx["module_outcomes"].get(src["module_outcome"]["instance"])
            return ("UNKNOWN", None) if v is None else ("KNOWN", v)
    raise ValueError(o)


def num(v):
    return Decimal(str(v))


def evaluate(ast, ctx):
    op = ast["op"]
    if op == "AND":
        return tri_and([evaluate(a, ctx) for a in ast["args"]])
    if op == "OR":
        return tri_or([evaluate(a, ctx) for a in ast["args"]])
    if op == "NOT":
        return tri_not(evaluate(ast["arg"], ctx))
    (ls, lv), (rs, rv) = operand(ast["left"], ctx), operand(ast["right"], ctx)
    if ls != "KNOWN" or rs != "KNOWN":
        return "UNKNOWN"
    if op in ("GT", "GTE", "LT", "LTE"):
        a, b = num(lv), num(rv)
        r = {"GT": a > b, "GTE": a >= b, "LT": a < b, "LTE": a <= b}[op]
    elif op == "EQ":
        r = lv == rv
    elif op == "NEQ":
        r = lv != rv
    elif op == "IN":
        r = lv in rv
    elif op == "CONTAINS":
        r = rv in lv
    else:
        raise ValueError(op)
    return "TRUE" if r else "FALSE"


def eval_binding(b, lib, base):
    c = next(x for x in lib["conditions"] if x["code"] == b["condition"]["code"] and x["version"] == b["condition"]["version"])
    ctx = {**base, "params": b.get("params", {}), "inputs": b.get("inputs", {})}
    return evaluate(c["ast"], ctx)


def validate_answer(question, option_set, a):
    t = question["answer_type"]
    if t == "FREE_TEXT":
        text, rule = (a.get("text") or "").strip(), question.get("text", {})
        if rule.get("required", True) and not text:
            raise Reject("TEXT_REQUIRED")
        if len(text) < rule.get("min_length", 0):
            raise Reject("TEXT_TOO_SHORT")
        if len(text) > rule.get("max_length", 2000):
            raise Reject("TEXT_TOO_LONG")
        return
    opts = {o["code"]: o for o in option_set["options"]}
    chosen = [a["choice"]] if t in ("YES_NO", "SINGLE_SELECT") else list(a.get("choices", []))
    if t in ("YES_NO", "SINGLE_SELECT") and "choice" not in a:
        raise Reject("CHOICE_REQUIRED")
    for c in chosen:
        if c not in opts:
            raise Reject("UNKNOWN_OPTION")
    if len(set(chosen)) != len(chosen):
        raise Reject("DUPLICATE_OPTION")
    if t == "MULTI_SELECT":
        sel = question.get("selection", {})
        if len(chosen) < sel.get("min", 0):
            raise Reject("TOO_FEW_SELECTED")
        if len(chosen) > sel.get("max", len(opts)):
            raise Reject("TOO_MANY_SELECTED")
        if len(chosen) > 1 and any(opts[c].get("exclusive") for c in chosen):
            raise Reject("EXCLUSIVE_OPTION_CONFLICT")
    other = next((opts[c] for c in chosen if opts[c].get("is_other")), None)
    text = (a.get("other_text") or "").strip()
    if other is None:
        if "other_text" in a:
            raise Reject("OTHER_TEXT_NOT_ALLOWED")
        return
    rule = other.get("other_text", {})
    if rule.get("required") and not text:
        raise Reject("OTHER_TEXT_REQUIRED")
    if text and len(text) < rule.get("min_length", 0):
        raise Reject("OTHER_TEXT_TOO_SHORT")
    if len(text) > rule.get("max_length", 500):
        raise Reject("OTHER_TEXT_TOO_LONG")


def run_module(lib, module, instance, run, state):
    """Returns the module outcome. Appends to state['asked'], state['trace']; fills state['answers']."""
    nodes = {n["node"]: n for n in module["nodes"]}
    edges = module["edges"]
    qs = {x["code"]: x for x in lib["questions"]}
    sets = {x["code"]: x for x in lib["option_sets"]}
    base = {"profile": run.get("profile", {}), "answers": state["answers"], "module_outcomes": state["module_outcomes"],
            "instance": instance}

    def follow(node, code):
        cands = [x for x in edges if x["from"] == node and x["on"] == code] or \
                [x for x in edges if x["from"] == node and x["on"] == "ANY"]
        if len(cands) != 1:
            raise Blocked("ROUTE_MISSING" if not cands else "AMBIGUOUS_ROUTE", f"{instance}/{node}")
        state["edges"].append(f"{instance}/{cands[0]['edge']}")
        return cands[0]["to"]

    def ask(node):
        n = nodes[node]
        key = f"{instance}/{node}"
        if key in state["asked"]:
            raise Blocked("REPEATED_EXECUTION", key)
        if len(state["asked"]) > 200:
            raise Blocked("TRAVERSAL_LIMIT", key)
        qd = qs[n["question"]["code"]]
        a = run["answers"][key]
        validate_answer(qd, sets.get(qd.get("option_set", {}).get("code")), a)
        state["asked"].append(key)
        state["answers"][key] = a
        state["evidence"].append({"question_instance": key, "question": f"{qd['code']}@{n['question']['version']}",
                                  "wording_version": n["question"]["wording_version"], "answer": a})
        return n, qd, a

    cur = {"node": module["entry"]}
    while True:
        if "outcome" in cur:
            return cur["outcome"]
        n = nodes[cur["node"]]
        if n["type"] == "DECISION":
            res = eval_binding(n["binding"], lib, base)
            state["trace"].append(f"{instance}/{n['node']}: {res}")
            code = {"TRUE": "MATCH", "FALSE": "NO_MATCH", "UNKNOWN": "UNKNOWN"}[res]
            if res == "UNKNOWN" and n["binding"]["unknown_policy"] == "BLOCK":
                raise Blocked("BLOCKED_UNKNOWN", f"{instance}/{n['node']}")
            cur = follow(n["node"], code)
            continue
        n, qd, a = ask(cur["node"])
        r = n["routing"]
        if r["mode"] == "SEQUENTIAL_FOLLOWUPS":
            chosen = set(a.get("choices", []))
            order = {o["code"]: o["order"] for o in sets[qd["option_set"]["code"]]["options"]}
            hit = sorted((i for i in r.get("interrupts", []) if i["option"] in chosen), key=lambda i: (i["priority"], order[i["option"]]))
            plan = sorted((f for f in r["followups"] if f["option"] in chosen), key=lambda f: (f["priority"], order[f["option"]]))
            queue, skipped = [], []
            for f in plan:
                for t in f["nodes"]:
                    (skipped if t in queue else queue).append(t)
            if hit:
                state["trace"].append(f"{instance}/{n['node']}: INTERRUPT {hit[0]['option']} -> {hit[0]['outcome']}; skipped {queue}")
                return hit[0]["outcome"]
            state["trace"].append(f"{instance}/{n['node']}: QUEUE {queue}" + (f"; deduped {skipped}" if skipped else ""))
            early = None
            for t in queue:
                fn, fq, fa = ask(t)
                to = follow(t, fa.get("choice", "AFTER_CAPTURE"))
                if "outcome" in to:
                    early = to["outcome"]
                    break
                if not to.get("return"):
                    raise Blocked("FOLLOWUP_MUST_RETURN", f"{instance}/{t}")
            if early:
                return early
            cur = r["rejoin"] if queue else r["empty_fallback"]
            continue
        if qd["answer_type"] == "FREE_TEXT":
            code = "AFTER_CAPTURE"
        elif qd["answer_type"] == "MULTI_SELECT":
            code = "ANY"
        else:
            code = a["choice"]
        cur = follow(n["node"], code)


def execute(fx, run):
    lib, sv = fx["library"], fx["survey"]
    mods = {(m["code"], m["revision"]): m for m in lib["modules"]}
    insts = {i["instance"]: i for i in sv["instances"]}
    state = {"asked": [], "answers": {}, "evidence": [], "trace": [], "edges": [], "module_outcomes": {}}
    status = {}
    seq, pos, forced = sv["sequence"], 0, None
    result = {}
    try:
        while pos < len(seq):
            name = seq[pos]
            i = insts[name]
            entry, go = i["entry"], None
            base = {"profile": run.get("profile", {}), "answers": state["answers"],
                    "module_outcomes": state["module_outcomes"], "instance": name}
            if forced == name:
                go, forced = "ACTIVATED", None
            elif entry["mode"] == "ALWAYS":
                go = "ACTIVATED"
            elif entry["mode"] == "ON_OUTCOME":
                got = state["module_outcomes"].get(entry["of"])
                go = "ACTIVATED" if got in entry["outcomes"] else "SKIPPED_PRIOR_OUTCOME"
            elif entry["mode"] == "RULE":
                res = eval_binding(entry["binding"], lib, base)
                state["trace"].append(f"{name}: entry {res}")
                if res == "TRUE":
                    go = "ACTIVATED"
                elif res == "FALSE":
                    go = "SKIPPED_FALSE"
                elif entry["binding"]["unknown_policy"] == "BLOCK":
                    status[name] = {"status": "BLOCKED_UNKNOWN"}
                    raise Blocked("BLOCKED_UNKNOWN", name)
                else:
                    go = "SKIPPED_UNKNOWN"
            if go != "ACTIVATED":
                status[name] = {"status": go}
                pos += 1
                continue
            m = mods[(i["module"]["code"], i["module"]["revision"])]
            out = run_module(lib, m, name, run, state)
            status[name] = {"status": "ACTIVATED", "outcome": out}
            state["module_outcomes"][name] = out
            routes = [r for r in i["routes"] if r["on"] == out]
            if len(routes) != 1:
                raise Blocked("ROUTE_MISSING", f"{name}:{out}")
            to = routes[0]["to"]
            if to == "@CONTINUE":
                pos += 1
            elif "survey_outcome" in to:
                result["survey_outcome"] = to["survey_outcome"]
                break
            else:
                tgt = seq.index(to["instance"])
                if tgt <= pos:
                    raise Blocked("BACKWARD_ROUTE", name)
                for skipped in seq[pos + 1:tgt]:
                    status[skipped] = {"status": "SKIPPED_BY_ROUTE"}
                pos, forced = tgt, to["instance"]
        else:
            result["survey_outcome"] = sv["end"]["survey_outcome"]
    except Blocked as b:
        result["blocked"] = {"reason": b.reason, "at": b.at}
    for name in seq:
        status.setdefault(name, {"status": "NOT_REACHED"})
    result.update({"asked": state["asked"], "modules": [{"instance": n, **status[n]} for n in seq]})
    return result, state


def check(fx):
    lib = fx["library"]
    qs = {x["code"]: x for x in lib["questions"]}
    sets = {x["code"]: x for x in lib["option_sets"]}
    # referential integrity
    for m in lib["modules"]:
        nodes = {n["node"] for n in m["nodes"]}
        assert m["entry"] in nodes, (fx["fixture"], m["code"], "entry")
        assert len({x["edge"] for x in m["edges"]}) == len(m["edges"]), "duplicate edge ids"
        for x in m["edges"]:
            assert x["from"] in nodes
            assert ("node" in x["to"] and x["to"]["node"] in nodes) or x["to"].get("outcome") in m["outcomes"] or x["to"].get("return")
        for n in m["nodes"]:
            if n["type"] == "QUESTION":
                qd = qs[n["question"]["code"]]
                assert any(wd["question"] == qd["code"] and wd["wording_version"] == n["question"]["wording_version"] for wd in lib["wordings"])
                if "option_set" in qd:
                    assert qd["option_set"]["code"] in sets
    for wd in lib["wordings"]:
        qd = qs[wd["question"]]
        codes = [o["code"] for o in sets[qd["option_set"]["code"]]["options"]] if "option_set" in qd else []
        assert wd["binds_to"] == {"answer_type": qd["answer_type"], "option_codes": codes}, wd["question"]
    for run in fx["expected_runs"]:
        for bad in run.get("rejected", []):
            module = next(m for m in lib["modules"] for i in fx["survey"]["instances"]
                          if i["instance"] == bad["at"].split("/")[0] and i["module"]["code"] == m["code"])
            n = next(n for n in module["nodes"] if n["node"] == bad["at"].split("/")[1])
            qd = qs[n["question"]["code"]]
            try:
                validate_answer(qd, sets.get(qd.get("option_set", {}).get("code")), bad["answer"])
            except Reject as r:
                assert str(r) == bad["error"], (fx["fixture"], run["name"], str(r), bad["error"])
            else:
                raise AssertionError((fx["fixture"], run["name"], "answer was accepted", bad))
        got, state = execute(fx, run)
        exp = run["expect"]
        for k in ("asked", "modules", "survey_outcome", "blocked"):
            assert got.get(k) == exp.get(k), (fx["fixture"], run["name"], k, got.get(k), exp.get(k))
        if "evidence" in exp:
            assert state["evidence"] == exp["evidence"], (fx["fixture"], run["name"], state["evidence"])
        if "trace" in exp:
            assert state["trace"] == exp["trace"], (fx["fixture"], run["name"], state["trace"])
        if "edges_taken" in exp:
            assert state["edges"] == exp["edges_taken"], (fx["fixture"], run["name"], state["edges"])
    return len(fx["expected_runs"])


def mods(*pairs):
    return [{"instance": i, "status": "ACTIVATED", "outcome": o} if o in OUTCOMES else {"instance": i, "status": o} for i, o in pairs]


# ------------------------------------------------------------------------------------------------------- fixtures
def f1():
    q1 = q("Q-CONFIRM-PURCHASE", "YES_NO", "Customer confirms the purchase", YES_NO)
    q2 = q("Q-REP-EXPLAINED", "YES_NO", "Representative explained the plan", YES_NO)
    q3 = q("Q-ANYTHING-ELSE", "FREE_TEXT", "Customer's own remarks", text={"required": False, "max_length": 500}, mandatory=False)
    q4 = q("Q-CLOSING-ACK", "YES_NO", "Customer acknowledges the closing statement", YES_NO)
    general = {"code": "M-GENERAL", "revision": 1, "kind": "COMMON", "name": "General verification", "entry": "n1",
               "outcomes": ["COMPLETED"],
               "nodes": [qn("n1", q1), qn("n2", q2), qn("n3", q3)],
               "edges": [e("e1", "n1", "ANY", node="n2"), e("e2", "n2", "ANY", node="n3"),
                         e("e3", "n3", "AFTER_CAPTURE", outcome="COMPLETED")]}
    closing = {"code": "M-CLOSING", "revision": 1, "kind": "CLOSING", "name": "Closing", "entry": "n1",
               "outcomes": ["COMPLETED"], "nodes": [qn("n1", q4)], "edges": [e("e1", "n1", "ANY", outcome="COMPLETED")]}
    sv = survey("S-LINEAR", [inst("mi-general", general), inst("mi-closing", closing)])
    runs = [{"name": "Every answer continues to the next question",
             "answers": {"mi-general/n1": {"choice": "YES"}, "mi-general/n2": {"choice": "NO"},
                         "mi-general/n3": {"text": ""}, "mi-closing/n1": {"choice": "YES"}},
             "expect": {"asked": ["mi-general/n1", "mi-general/n2", "mi-general/n3", "mi-closing/n1"],
                        "modules": mods(("mi-general", "COMPLETED"), ("mi-closing", "COMPLETED")),
                        "survey_outcome": "COMPLETED",
                        "edges_taken": ["mi-general/e1", "mi-general/e2", "mi-general/e3", "mi-closing/e1"]}}]
    return fixture("F1-simple-linear-survey", "A simple linear survey",
                   "The degenerate graph: every answer follows one explicit default edge (ANY). This is exactly what a "
                   "legacy linear script becomes; an optional free-text answer may be empty.",
                   [YES_NO], [q1, q2, q3, q4],
                   [w(q1, "Can you confirm that you purchased this policy?", YES_NO),
                    w(q2, "Did your representative explain how the plan works?", YES_NO),
                    w(q3, "Is there anything else you would like to tell us?"),
                    w(q4, "Thank you. Do you acknowledge that this call has been completed?", YES_NO)],
                   [], [general, closing], sv, runs)


def f2():
    q1 = q("Q-BENEFITS-EXPLAINED", "YES_NO", "Benefits were explained", YES_NO)
    q2 = q("Q-RISKS-UNDERSTOOD", "YES_NO", "Customer understands the key risks", YES_NO)
    q3 = q("Q-WHAT-TO-CLARIFY", "FREE_TEXT", "What the customer wants clarified", text={"required": True, "min_length": 5, "max_length": 500})
    m = {"code": "M-SUITABILITY", "revision": 1, "kind": "PRODUCT", "name": "Suitability", "entry": "n1",
         "outcomes": ["COMPLETED", "CLARIFICATION_REQUIRED"],
         "nodes": [qn("n1", q1, "PER_CHOICE", normal_answer="YES"), qn("n2", q2, "PER_CHOICE", normal_answer="YES"), qn("n3", q3)],
         "edges": [e("e1", "n1", "YES", node="n2"), e("e2", "n1", "NO", node="n3"),
                   e("e3", "n3", "AFTER_CAPTURE", node="n2"),
                   e("e4", "n2", "YES", outcome="COMPLETED"), e("e5", "n2", "NO", outcome="CLARIFICATION_REQUIRED")]}
    sv = survey("S-BRANCH-REJOIN", [inst("mi-suit", m, routes=[
        {"on": "COMPLETED", "to": "@CONTINUE"},
        {"on": "CLARIFICATION_REQUIRED", "to": {"survey_outcome": "CLARIFICATION_REQUIRED"}}])])
    runs = [
        {"name": "Yes path goes straight to the shared question",
         "answers": {"mi-suit/n1": {"choice": "YES"}, "mi-suit/n2": {"choice": "YES"}},
         "expect": {"asked": ["mi-suit/n1", "mi-suit/n2"], "modules": mods(("mi-suit", "COMPLETED")),
                    "survey_outcome": "COMPLETED", "edges_taken": ["mi-suit/e1", "mi-suit/e4"]}},
        {"name": "No path detours through clarification and rejoins the same node (asked once)",
         "answers": {"mi-suit/n1": {"choice": "NO"}, "mi-suit/n3": {"text": "The surrender charges"}, "mi-suit/n2": {"choice": "NO"}},
         "rejected": [{"at": "mi-suit/n3", "answer": {"text": "abc"}, "error": "TEXT_TOO_SHORT"}],
         "expect": {"asked": ["mi-suit/n1", "mi-suit/n3", "mi-suit/n2"], "modules": mods(("mi-suit", "CLARIFICATION_REQUIRED")),
                    "survey_outcome": "CLARIFICATION_REQUIRED", "edges_taken": ["mi-suit/e2", "mi-suit/e3", "mi-suit/e5"]}}]
    return fixture("F2-yes-no-branch-shared-rejoin", "A Yes/No branch with a shared rejoin",
                   "Node n2 is stored once and has two incoming edges (e1 from n1:YES, e3 from n3). SS-AT-006.",
                   [YES_NO], [q1, q2, q3],
                   [w(q1, "Did your representative explain the benefits of this plan?", YES_NO),
                    w(q2, "Do you understand the key risks and exclusions?", YES_NO),
                    w(q3, "What would you like us to clarify?")], [], [m], sv, runs)


def f3():
    concern = {"code": "OS-MAIN-CONCERN", "version": 1, "options": [
        {"code": "PREMIUM", "business_label": "Premium affordability", "order": 1},
        {"code": "BENEFITS", "business_label": "Product benefits", "order": 2},
        {"code": "CLAIMS", "business_label": "Claims process", "order": 3},
        {"code": "NONE", "business_label": "No concern", "order": 4}]}
    q1 = q("Q-MAIN-CONCERN", "SINGLE_SELECT", "The customer's most important concern", concern)
    qp = q("Q-PREMIUM-DETAIL", "YES_NO", "Premium is affordable for the full term", YES_NO)
    qb = q("Q-BENEFITS-DETAIL", "YES_NO", "Benefits match what was explained", YES_NO)
    qc = q("Q-CLAIMS-DETAIL", "YES_NO", "Claims process was explained", YES_NO)
    qf = q("Q-CONFIRM-PROCEED", "YES_NO", "Customer is content to proceed", YES_NO)
    m = {"code": "M-CONCERNS", "revision": 1, "kind": "COMMON", "name": "Customer concerns", "entry": "n1",
         "outcomes": ["COMPLETED", "CLARIFICATION_REQUIRED"],
         "nodes": [qn("n1", q1, "PER_CHOICE"), qn("n-prem", qp), qn("n-ben", qb), qn("n-claims", qc),
                   qn("n-confirm", qf, "PER_CHOICE", normal_answer="YES")],
         "edges": [e("e1", "n1", "PREMIUM", node="n-prem"), e("e2", "n1", "BENEFITS", node="n-ben"),
                   e("e3", "n1", "CLAIMS", node="n-claims"), e("e4", "n1", "NONE", node="n-confirm"),
                   e("e5", "n-prem", "ANY", node="n-confirm"), e("e6", "n-ben", "ANY", node="n-confirm"),
                   e("e7", "n-claims", "ANY", node="n-confirm"),
                   e("e8", "n-confirm", "YES", outcome="COMPLETED"), e("e9", "n-confirm", "NO", outcome="CLARIFICATION_REQUIRED")]}
    sv = survey("S-SINGLE-CHOICE", [inst("mi-concerns", m, routes=[
        {"on": "COMPLETED", "to": "@CONTINUE"},
        {"on": "CLARIFICATION_REQUIRED", "to": {"survey_outcome": "CLARIFICATION_REQUIRED"}}])])
    runs = [
        {"name": "BENEFITS takes its own route, then merges",
         "answers": {"mi-concerns/n1": {"choice": "BENEFITS"}, "mi-concerns/n-ben": {"choice": "YES"}, "mi-concerns/n-confirm": {"choice": "YES"}},
         "rejected": [{"at": "mi-concerns/n1", "answer": {"choice": "PRICE"}, "error": "UNKNOWN_OPTION"}],
         "expect": {"asked": ["mi-concerns/n1", "mi-concerns/n-ben", "mi-concerns/n-confirm"],
                    "modules": mods(("mi-concerns", "COMPLETED")), "survey_outcome": "COMPLETED",
                    "edges_taken": ["mi-concerns/e2", "mi-concerns/e6", "mi-concerns/e8"]}},
        {"name": "NONE goes directly to the merge point",
         "answers": {"mi-concerns/n1": {"choice": "NONE"}, "mi-concerns/n-confirm": {"choice": "YES"}},
         "expect": {"asked": ["mi-concerns/n1", "mi-concerns/n-confirm"], "modules": mods(("mi-concerns", "COMPLETED")),
                    "survey_outcome": "COMPLETED", "edges_taken": ["mi-concerns/e4", "mi-concerns/e8"]}}]
    return fixture("F3-single-choice-per-option-routes", "Single-choice with distinct per-option routes",
                   "Four stable option codes, each with its own edge; three branches and the direct route merge at "
                   "n-confirm, which has four incoming edges. Routing uses codes, never labels. SS-AT-009.",
                   [YES_NO, concern], [q1, qp, qb, qc, qf],
                   [w(q1, "Which of these is most important to you?", concern,
                      {"PREMIUM": "Whether I can afford the premium", "BENEFITS": "What the plan pays", "CLAIMS": "How to claim", "NONE": "None of these"}),
                    w(qp, "Are you comfortable paying this premium for the full term?", YES_NO),
                    w(qb, "Do the benefits match what was explained to you?", YES_NO),
                    w(qc, "Was the claims process explained to you?", YES_NO),
                    w(qf, "Are you content to proceed with this policy?", YES_NO)], [], [m], sv, runs)


def f4():
    areas = {"code": "OS-CLARIFY-AREAS", "version": 1, "options": [
        {"code": "PREMIUM", "business_label": "Premium", "order": 1},
        {"code": "BENEFITS", "business_label": "Benefits", "order": 2},
        {"code": "CLAIMS", "business_label": "Claims", "order": 3},
        {"code": "CRITICAL_RISK", "business_label": "I did not agree to this policy", "order": 4},
        {"code": "NONE", "business_label": "None of the above", "order": 5, "exclusive": True}]}
    q1 = q("Q-CLARIFY-AREAS", "MULTI_SELECT", "Areas the customer wants clarified", areas, selection={"min": 1, "max": 4})
    qp = q("Q-PREMIUM-CLARIFY", "YES_NO", "Premium amount and term are understood", YES_NO)
    qc = q("Q-COVER-CLARIFY", "YES_NO", "Cover and claims are understood", YES_NO)
    qf = q("Q-CONFIRM-PROCEED", "YES_NO", "Customer is content to proceed", YES_NO)
    m = {"code": "M-CLARIFICATIONS", "revision": 1, "kind": "COMMON", "name": "Clarifications", "entry": "n1",
         "outcomes": ["COMPLETED", "CLARIFICATION_REQUIRED", "ESCALATE"],
         "nodes": [qn("n1", q1, "SEQUENTIAL_FOLLOWUPS",
                      followups=[{"option": "PREMIUM", "priority": 10, "nodes": ["n-prem"]},
                                 {"option": "BENEFITS", "priority": 20, "nodes": ["n-cover"]},
                                 {"option": "CLAIMS", "priority": 30, "nodes": ["n-cover"]}],
                      no_followup=["NONE"],
                      interrupts=[{"option": "CRITICAL_RISK", "priority": 1, "outcome": "ESCALATE"}],
                      order="PRIORITY_THEN_OPTION_ORDER", dedupe="ONCE_PER_ANSWER",
                      rejoin={"node": "n-confirm"}, empty_fallback={"node": "n-confirm"}),
                   qn("n-prem", qp, role="FOLLOWUP"), qn("n-cover", qc, role="FOLLOWUP"),
                   qn("n-confirm", qf, "PER_CHOICE", normal_answer="YES")],
         "edges": [e("e1", "n-prem", "ANY", ret=True), e("e2", "n-cover", "ANY", ret=True),
                   e("e3", "n-confirm", "YES", outcome="COMPLETED"), e("e4", "n-confirm", "NO", outcome="CLARIFICATION_REQUIRED")]}
    sv = survey("S-MULTI-FOLLOWUPS", [inst("mi-clar", m, routes=[
        {"on": "COMPLETED", "to": "@CONTINUE"},
        {"on": "CLARIFICATION_REQUIRED", "to": {"survey_outcome": "CLARIFICATION_REQUIRED"}},
        {"on": "ESCALATE", "to": {"survey_outcome": "ESCALATE"}}])])
    k = "mi-clar/"
    runs = [
        {"name": "BENEFITS then PREMIUM ticked: follow-ups run in configured order, not click order",
         "answers": {k + "n1": {"choices": ["BENEFITS", "PREMIUM"]}, k + "n-prem": {"choice": "YES"}, k + "n-cover": {"choice": "YES"}, k + "n-confirm": {"choice": "YES"}},
         "expect": {"asked": [k + "n1", k + "n-prem", k + "n-cover", k + "n-confirm"], "modules": mods(("mi-clar", "COMPLETED")),
                    "survey_outcome": "COMPLETED", "trace": ["mi-clar/n1: QUEUE ['n-prem', 'n-cover']"]}},
        {"name": "BENEFITS and CLAIMS share one follow-up: asked once",
         "answers": {k + "n1": {"choices": ["CLAIMS", "BENEFITS"]}, k + "n-cover": {"choice": "NO"}, k + "n-confirm": {"choice": "NO"}},
         "expect": {"asked": [k + "n1", k + "n-cover", k + "n-confirm"], "modules": mods(("mi-clar", "CLARIFICATION_REQUIRED")),
                    "survey_outcome": "CLARIFICATION_REQUIRED", "trace": ["mi-clar/n1: QUEUE ['n-cover']; deduped ['n-cover']"]}},
        {"name": "CRITICAL_RISK interrupts: queue is not run, skipped items are traced",
         "answers": {k + "n1": {"choices": ["PREMIUM", "CRITICAL_RISK"]}},
         "expect": {"asked": [k + "n1"], "modules": mods(("mi-clar", "ESCALATE")), "survey_outcome": "ESCALATE",
                    "trace": ["mi-clar/n1: INTERRUPT CRITICAL_RISK -> ESCALATE; skipped ['n-prem']"]}},
        {"name": "NONE: empty queue takes the mandatory fallback; invalid sets are rejected",
         "answers": {k + "n1": {"choices": ["NONE"]}, k + "n-confirm": {"choice": "YES"}},
         "rejected": [{"at": k + "n1", "answer": {"choices": ["NONE", "PREMIUM"]}, "error": "EXCLUSIVE_OPTION_CONFLICT"},
                      {"at": k + "n1", "answer": {"choices": []}, "error": "TOO_FEW_SELECTED"}],
         "expect": {"asked": [k + "n1", k + "n-confirm"], "modules": mods(("mi-clar", "COMPLETED")),
                    "survey_outcome": "COMPLETED", "trace": ["mi-clar/n1: QUEUE []"]}}]
    return fixture("F4-multi-select-ordered-followups", "Multi-select with two ordered follow-up paths",
                   "SEQUENTIAL_FOLLOWUPS: one cursor, one question at a time, explicit order, dedupe ONCE_PER_ANSWER, "
                   "an interrupt, an exclusive option and one rejoin. SS-AT-038…042, 046 (contrast), 045 (validation).",
                   [YES_NO, areas], [q1, qp, qc, qf],
                   [w(q1, "Which of these would you like us to clarify? You may choose more than one.", areas),
                    w(qp, "Is the premium amount and payment term clear to you now?", YES_NO),
                    w(qc, "Is it clear to you what the plan covers and how to claim?", YES_NO),
                    w(qf, "Are you content to proceed with this policy?", YES_NO)], [], [m], sv, runs)


def f5():
    reason = {"code": "OS-PURCHASE-REASON", "version": 1, "options": [
        {"code": "PROTECTION", "business_label": "Protection for family", "order": 1},
        {"code": "SAVINGS", "business_label": "Savings", "order": 2},
        {"code": "OTHER", "business_label": "Other — please specify", "order": 3, "is_other": True,
         "other_text": {"required": True, "min_length": 5, "max_length": 200}, "allow_with_others": False}]}
    q1 = q("Q-PURCHASE-REASON", "SINGLE_SELECT", "Main reason for buying", reason)
    q2 = q("Q-REASON-MATCHES-ADVICE", "YES_NO", "Stated reason matches the advice given", YES_NO)
    q3 = q("Q-CONFIRM-PROCEED", "YES_NO", "Customer is content to proceed", YES_NO)
    m = {"code": "M-PURCHASE-REASON", "revision": 1, "kind": "COMMON", "name": "Reason for purchase", "entry": "n1",
         "outcomes": ["COMPLETED"],
         "nodes": [qn("n1", q1, "PER_CHOICE_WITH_DEFAULT"), qn("n2", q2), qn("n3", q3)],
         "edges": [e("e1", "n1", "OTHER", node="n2"), e("e2", "n1", "ANY", node="n3"),
                   e("e3", "n2", "ANY", node="n3"), e("e4", "n3", "ANY", outcome="COMPLETED")]}
    sv = survey("S-OTHER-SPECIFY", [inst("mi-reason", m)])
    k = "mi-reason/"
    runs = [
        {"name": "OTHER with valid text: code and text stored, Other-specific route taken",
         "answers": {k + "n1": {"choice": "OTHER", "other_text": "To fund my child's education"}, k + "n2": {"choice": "YES"}, k + "n3": {"choice": "YES"}},
         "rejected": [{"at": k + "n1", "answer": {"choice": "OTHER"}, "error": "OTHER_TEXT_REQUIRED"},
                      {"at": k + "n1", "answer": {"choice": "OTHER", "other_text": "abc"}, "error": "OTHER_TEXT_TOO_SHORT"}],
         "expect": {"asked": [k + "n1", k + "n2", k + "n3"], "modules": mods(("mi-reason", "COMPLETED")), "survey_outcome": "COMPLETED",
                    "evidence": [
                        {"question_instance": k + "n1", "question": "Q-PURCHASE-REASON@1", "wording_version": 1,
                         "answer": {"choice": "OTHER", "other_text": "To fund my child's education"}},
                        {"question_instance": k + "n2", "question": "Q-REASON-MATCHES-ADVICE@1", "wording_version": 1, "answer": {"choice": "YES"}},
                        {"question_instance": k + "n3", "question": "Q-CONFIRM-PROCEED@1", "wording_version": 1, "answer": {"choice": "YES"}}]}},
        {"name": "SAVINGS: default route; no phantom Other text may be submitted",
         "answers": {k + "n1": {"choice": "SAVINGS"}, k + "n3": {"choice": "YES"}},
         "rejected": [{"at": k + "n1", "answer": {"choice": "SAVINGS", "other_text": "left over"}, "error": "OTHER_TEXT_NOT_ALLOWED"}],
         "expect": {"asked": [k + "n1", k + "n3"], "modules": mods(("mi-reason", "COMPLETED")), "survey_outcome": "COMPLETED",
                    "edges_taken": ["mi-reason/e2", "mi-reason/e4"]}}]
    return fixture("F5-other-specify-with-validation", "Other + specify with validation",
                   "OTHER is a stable option code with a companion text schema, not a question type. Text is required "
                   "only when OTHER is chosen and is rejected otherwise. SS-AT-033…035.",
                   [YES_NO, reason], [q1, q2, q3],
                   [w(q1, "What was your main reason for buying this policy?", reason, other_prompt="Please tell us the reason"),
                    w(q2, "Does that match the advice your representative gave you?", YES_NO),
                    w(q3, "Are you content to proceed with this policy?", YES_NO)], [], [m], sv, runs)


def f6():
    q1 = q("Q-RISKS-UNDERSTOOD", "YES_NO", "Customer understands the key risks", YES_NO)
    q2 = q("Q-AFFORDABILITY", "YES_NO", "Premium remains affordable after retirement", YES_NO)
    cond = {"code": "C-ENHANCED-REVIEW", "version": 1, "name": "Enhanced review needed",
            "summary": "Age is at least {minimum_age} AND (annual premium is above {premium_threshold} OR risks were not understood)",
            "params": {"minimum_age": {"type": "INTEGER", "unit": "years"}, "premium_threshold": {"type": "MONEY", "unit": "SGD"}},
            "inputs": {"risk_understood": {"type": "OPTION_CODE", "option_set": {"code": "OS-YES-NO", "version": 1}}},
            "fields": ["customer.age_years", "policy.annual_premium"],
            "ast": {"op": "AND", "args": [
                {"op": "GTE", "left": {"field": "customer.age_years"}, "right": {"param": "minimum_age"}},
                {"op": "OR", "args": [
                    {"op": "GT", "left": {"field": "policy.annual_premium"}, "right": {"param": "premium_threshold"}},
                    {"op": "EQ", "left": {"input": "risk_understood"}, "right": {"literal": "NO"}}]}]}}
    m = {"code": "M-ENHANCED", "revision": 1, "kind": "RISK", "name": "Enhanced review", "entry": "n1",
         "outcomes": ["COMPLETED", "CLARIFICATION_REQUIRED", "UNABLE_TO_VERIFY"],
         "nodes": [qn("n1", q1),
                   {"node": "d1", "type": "DECISION", "binding": {
                       "condition": {"code": "C-ENHANCED-REVIEW", "version": 1},
                       "params": {"minimum_age": 60, "premium_threshold": 12000},
                       "inputs": {"risk_understood": {"answer": {"node": "n1"}}},
                       "unknown_policy": "ROUTE_UNKNOWN"}},
                   qn("n2", q2, "PER_CHOICE", normal_answer="YES")],
         "edges": [e("e1", "n1", "ANY", node="d1"),
                   e("e2", "d1", "MATCH", node="n2"), e("e3", "d1", "NO_MATCH", outcome="COMPLETED"),
                   e("e4", "d1", "UNKNOWN", outcome="UNABLE_TO_VERIFY"),
                   e("e5", "n2", "YES", outcome="COMPLETED"), e("e6", "n2", "NO", outcome="CLARIFICATION_REQUIRED")]}
    sv = survey("S-INTERNAL-CONDITION", [inst("mi-enh", m, routes=[
        {"on": "COMPLETED", "to": "@CONTINUE"},
        {"on": "CLARIFICATION_REQUIRED", "to": {"survey_outcome": "CLARIFICATION_REQUIRED"}},
        {"on": "UNABLE_TO_VERIFY", "to": {"survey_outcome": "UNABLE_TO_VERIFY"}}])])
    k = "mi-enh/"

    def run(name, age, premium, n1, asked_n2, outcome, res):
        answers = {k + "n1": {"choice": n1}}
        if asked_n2:
            answers[k + "n2"] = {"choice": "YES"}
        return {"name": name, "profile": {"customer.age_years": age, "policy.annual_premium": premium}, "answers": answers,
                "expect": {"asked": [k + "n1"] + ([k + "n2"] if asked_n2 else []), "modules": mods(("mi-enh", outcome)),
                           "survey_outcome": outcome, "trace": [f"mi-enh/d1: {res}"]}}
    runs = [
        run("Age 65, premium 15,000: TRUE AND (TRUE OR FALSE) = MATCH", 65, 15000, "YES", True, "COMPLETED", "TRUE"),
        run("Premium exactly 12,000 with '>': FALSE, not an accidental '>='", 65, 12000, "YES", False, "COMPLETED", "FALSE"),
        run("Age 45, premium missing: FALSE AND UNKNOWN = FALSE (a known FALSE decides)", 45, None, "YES", False, "COMPLETED", "FALSE"),
        run("Age 65, premium missing, risks understood: TRUE AND (UNKNOWN OR FALSE) = UNKNOWN", 65, None, "YES", False, "UNABLE_TO_VERIFY", "UNKNOWN"),
        run("Age 65, premium missing, risks NOT understood: TRUE AND (UNKNOWN OR TRUE) = MATCH", 65, None, "NO", True, "COMPLETED", "TRUE"),
        run("Age missing, premium 15,000: UNKNOWN AND TRUE = UNKNOWN (never treated as false)", None, 15000, "YES", False, "UNABLE_TO_VERIFY", "UNKNOWN")]
    return fixture("F6-internal-condition-with-unknown", "An internal condition with UNKNOWN",
                   "A reusable, parameterised condition bound at a Decision node. Three-valued logic: a missing input "
                   "gives UNKNOWN unless a known operand already decides the result; UNKNOWN has its own explicit edge. "
                   "The prior answer is supplied through a named input mapped by the binding. SS-AT-004, 005, 013.",
                   [YES_NO], [q1, q2],
                   [w(q1, "Do you understand the key risks and exclusions?", YES_NO),
                    w(q2, "Will you still be able to afford this premium after you retire?", YES_NO)],
                   [cond], [m], sv, runs, fields=["customer.age_years", "policy.annual_premium"])


def f7():
    shared = q("Q-UNDERSTOOD", "YES_NO", "Customer understood what was just explained", YES_NO)
    qb = q("Q-BENEFITS-EXPLAINED", "YES_NO", "Benefits were explained", YES_NO)
    qr = q("Q-RISKS-EXPLAINED", "YES_NO", "Risks were explained", YES_NO)
    qc = q("Q-WHAT-TO-CLARIFY", "FREE_TEXT", "What the customer wants clarified", text={"required": True, "min_length": 5, "max_length": 500})
    benefits = {"code": "M-BENEFITS", "revision": 1, "kind": "PRODUCT", "name": "Benefits", "entry": "n1",
                "outcomes": ["COMPLETED"],
                "nodes": [qn("n1", qb), qn("n2", shared, "PER_CHOICE", normal_answer="YES"), qn("n3", qc)],
                "edges": [e("e1", "n1", "ANY", node="n2"), e("e2", "n2", "YES", outcome="COMPLETED"),
                          e("e3", "n2", "NO", node="n3"), e("e4", "n3", "AFTER_CAPTURE", outcome="COMPLETED")]}
    risks = {"code": "M-RISKS", "revision": 1, "kind": "RISK", "name": "Risks", "entry": "n1",
             "outcomes": ["COMPLETED", "CLARIFICATION_REQUIRED"],
             "nodes": [qn("n1", qr), qn("n2", shared, "PER_CHOICE", normal_answer="YES")],
             "edges": [e("e1", "n1", "ANY", node="n2"), e("e2", "n2", "YES", outcome="COMPLETED"),
                       e("e3", "n2", "NO", outcome="CLARIFICATION_REQUIRED")]}
    sv = survey("S-SHARED-QUESTION", [inst("mi-benefits", benefits), inst("mi-risks", risks, routes=[
        {"on": "COMPLETED", "to": "@CONTINUE"},
        {"on": "CLARIFICATION_REQUIRED", "to": {"survey_outcome": "CLARIFICATION_REQUIRED"}}])])
    runs = [{"name": "The same Question Definition is answered twice, once per placement, with different routing",
             "answers": {"mi-benefits/n1": {"choice": "YES"}, "mi-benefits/n2": {"choice": "YES"},
                         "mi-risks/n1": {"choice": "YES"}, "mi-risks/n2": {"choice": "NO"}},
             "expect": {"asked": ["mi-benefits/n1", "mi-benefits/n2", "mi-risks/n1", "mi-risks/n2"],
                        "modules": mods(("mi-benefits", "COMPLETED"), ("mi-risks", "CLARIFICATION_REQUIRED")),
                        "survey_outcome": "CLARIFICATION_REQUIRED",
                        "evidence": [
                            {"question_instance": "mi-benefits/n1", "question": "Q-BENEFITS-EXPLAINED@1", "wording_version": 1, "answer": {"choice": "YES"}},
                            {"question_instance": "mi-benefits/n2", "question": "Q-UNDERSTOOD@1", "wording_version": 1, "answer": {"choice": "YES"}},
                            {"question_instance": "mi-risks/n1", "question": "Q-RISKS-EXPLAINED@1", "wording_version": 1, "answer": {"choice": "YES"}},
                            {"question_instance": "mi-risks/n2", "question": "Q-UNDERSTOOD@1", "wording_version": 1, "answer": {"choice": "NO"}}]}}]
    return fixture("F7-two-placements-one-question-definition", "Two placements referencing one reusable Question Definition",
                   "Q-UNDERSTOOD@1 is placed in two modules used by the same survey. Each placement is a distinct "
                   "Question Instance (mi-benefits/n2, mi-risks/n2) with its own routing; evidence is keyed by the "
                   "instance and names the pinned definition version. Each instance executes once. SS-AT-028, SS-D-09.",
                   [YES_NO], [shared, qb, qr, qc],
                   [w(shared, "Did you understand what was just explained?", YES_NO),
                    w(qb, "Did your representative explain the benefits of this plan?", YES_NO),
                    w(qr, "Did your representative explain the risks of this plan?", YES_NO),
                    w(qc, "What would you like us to clarify?")], [], [benefits, risks], sv, runs)


def f8():
    def one(code, kind, name, question, outcomes=("COMPLETED",), no=None):
        edges = [e("e1", "n1", "ANY", outcome="COMPLETED")] if not no else \
                [e("e1", "n1", "YES", outcome="COMPLETED"), e("e2", "n1", "NO", outcome=no)]
        return {"code": code, "revision": 1, "kind": kind, "name": name, "entry": "n1", "outcomes": list(outcomes),
                "nodes": [qn("n1", question, "PER_CHOICE" if no else "ALL_TO_NEXT", **({"normal_answer": "YES"} if no else {}))],
                "edges": edges}
    qg = q("Q-IDENTITY-CONFIRMED", "YES_NO", "Customer confirms they are the policyholder", YES_NO)
    qs_ = q("Q-ILP-RISK-UNDERSTOOD", "YES_NO", "Customer understands investment risk", YES_NO)
    qh = q("Q-SOURCE-OF-FUNDS", "YES_NO", "Customer confirms the source of funds", YES_NO)
    qr = q("Q-REPLACEMENT-COSTS", "YES_NO", "Customer was told the costs of replacing a policy", YES_NO)
    qe = q("Q-CALLBACK-CONSENT", "YES_NO", "Customer agrees to a follow-up from a specialist", YES_NO)
    qc = q("Q-CLOSING-ACK", "YES_NO", "Customer acknowledges the closing statement", YES_NO)
    general = one("M-GENERAL", "COMMON", "General verification", qg, ("COMPLETED", "UNABLE_TO_VERIFY"), "UNABLE_TO_VERIFY")
    suit = one("M-SUITABILITY", "PRODUCT", "Suitability", qs_, ("COMPLETED", "CLARIFICATION_REQUIRED"), "CLARIFICATION_REQUIRED")
    high = one("M-HIGH-VALUE", "RISK", "High value review", qh)
    repl = one("M-REPLACEMENT", "PRODUCT", "Policy replacement", qr)
    esc = one("M-ESCALATION", "COMMON", "Escalation and follow-up", qe)
    closing = one("M-CLOSING", "CLOSING", "Closing", qc)
    c_ilp = {"code": "C-IS-ILP", "version": 1, "name": "Product is ILP", "summary": "Product family is ILP",
             "params": {}, "inputs": {}, "fields": ["policy.product_family"],
             "ast": {"op": "EQ", "left": {"field": "policy.product_family"}, "right": {"literal": "ILP"}}}
    c_high = {"code": "C-HIGH-VALUE", "version": 1, "name": "High value sale",
              "summary": "Annual premium is at least {premium_threshold} OR sum assured is at least {sum_assured_threshold}",
              "params": {"premium_threshold": {"type": "MONEY", "unit": "SGD"}, "sum_assured_threshold": {"type": "MONEY", "unit": "SGD"}},
              "inputs": {}, "fields": ["policy.annual_premium", "policy.sum_assured"],
              "ast": {"op": "OR", "args": [
                  {"op": "GTE", "left": {"field": "policy.annual_premium"}, "right": {"param": "premium_threshold"}},
                  {"op": "GTE", "left": {"field": "policy.sum_assured"}, "right": {"param": "sum_assured_threshold"}}]}}
    c_repl = {"code": "C-IS-REPLACEMENT", "version": 1, "name": "Policy replacement", "summary": "This sale replaces an existing policy",
              "params": {}, "inputs": {}, "fields": ["policy.is_replacement"],
              "ast": {"op": "EQ", "left": {"field": "policy.is_replacement"}, "right": {"literal": True}}}
    sv = survey("S-NEW-BUSINESS", [
        inst("mi-general", general, routes=[{"on": "COMPLETED", "to": "@CONTINUE"},
                                             {"on": "UNABLE_TO_VERIFY", "to": {"survey_outcome": "UNABLE_TO_VERIFY"}}]),
        inst("mi-suitability", suit, {"mode": "RULE", "binding": {"condition": {"code": "C-IS-ILP", "version": 1}, "unknown_policy": "BLOCK"}},
             [{"on": "COMPLETED", "to": "@CONTINUE"}, {"on": "CLARIFICATION_REQUIRED", "to": "@CONTINUE"}]),
        inst("mi-high-value", high, {"mode": "RULE", "binding": {
            "condition": {"code": "C-HIGH-VALUE", "version": 1},
            "params": {"premium_threshold": 12000, "sum_assured_threshold": 500000}, "unknown_policy": "BLOCK"}}),
        inst("mi-replacement", repl, {"mode": "RULE", "binding": {"condition": {"code": "C-IS-REPLACEMENT", "version": 1},
                                                                  "unknown_policy": "SKIP_WITH_REASON"}}),
        inst("mi-escalation", esc, {"mode": "ON_OUTCOME", "of": "mi-suitability", "outcomes": ["CLARIFICATION_REQUIRED"]}),
        inst("mi-closing", closing)])

    def run(name, profile, answers, statuses, asked, outcome=None, blocked=None, trace=None):
        exp = {"asked": asked, "modules": mods(*statuses)}
        if outcome:
            exp["survey_outcome"] = outcome
        if blocked:
            exp["blocked"] = blocked
        if trace:
            exp["trace"] = trace
        return {"name": name, "profile": profile, "answers": {k: {"choice": v} for k, v in answers.items()}, "expect": exp}
    P = "policy."
    runs = [
        run("Term life, low premium: only General and Closing run",
            {P + "product_family": "PROTECTION", P + "annual_premium": 3000, P + "sum_assured": 200000, P + "is_replacement": False},
            {"mi-general/n1": "YES", "mi-closing/n1": "YES"},
            [("mi-general", "COMPLETED"), ("mi-suitability", "SKIPPED_FALSE"), ("mi-high-value", "SKIPPED_FALSE"),
             ("mi-replacement", "SKIPPED_FALSE"), ("mi-escalation", "SKIPPED_PRIOR_OUTCOME"), ("mi-closing", "COMPLETED")],
            ["mi-general/n1", "mi-closing/n1"], "COMPLETED"),
        run("ILP, high premium, replacement: every conditional module runs",
            {P + "product_family": "ILP", P + "annual_premium": 24000, P + "sum_assured": 300000, P + "is_replacement": True},
            {"mi-general/n1": "YES", "mi-suitability/n1": "YES", "mi-high-value/n1": "YES", "mi-replacement/n1": "YES", "mi-closing/n1": "YES"},
            [("mi-general", "COMPLETED"), ("mi-suitability", "COMPLETED"), ("mi-high-value", "COMPLETED"),
             ("mi-replacement", "COMPLETED"), ("mi-escalation", "SKIPPED_PRIOR_OUTCOME"), ("mi-closing", "COMPLETED")],
            ["mi-general/n1", "mi-suitability/n1", "mi-high-value/n1", "mi-replacement/n1", "mi-closing/n1"], "COMPLETED"),
        run("Low premium but sum assured 600,000: either side of the OR activates High value",
            {P + "product_family": "PROTECTION", P + "annual_premium": 3000, P + "sum_assured": 600000, P + "is_replacement": False},
            {"mi-general/n1": "YES", "mi-high-value/n1": "YES", "mi-closing/n1": "YES"},
            [("mi-general", "COMPLETED"), ("mi-suitability", "SKIPPED_FALSE"), ("mi-high-value", "COMPLETED"),
             ("mi-replacement", "SKIPPED_FALSE"), ("mi-escalation", "SKIPPED_PRIOR_OUTCOME"), ("mi-closing", "COMPLETED")],
            ["mi-general/n1", "mi-high-value/n1", "mi-closing/n1"], "COMPLETED"),
        run("ILP customer does not understand the risk: Suitability emits CLARIFICATION_REQUIRED, which activates Escalation",
            {P + "product_family": "ILP", P + "annual_premium": 3000, P + "sum_assured": 100000, P + "is_replacement": False},
            {"mi-general/n1": "YES", "mi-suitability/n1": "NO", "mi-escalation/n1": "YES", "mi-closing/n1": "YES"},
            [("mi-general", "COMPLETED"), ("mi-suitability", "CLARIFICATION_REQUIRED"), ("mi-high-value", "SKIPPED_FALSE"),
             ("mi-replacement", "SKIPPED_FALSE"), ("mi-escalation", "COMPLETED"), ("mi-closing", "COMPLETED")],
            ["mi-general/n1", "mi-suitability/n1", "mi-escalation/n1", "mi-closing/n1"], "COMPLETED"),
        run("Premium missing and sum assured low: UNKNOWN blocks; it is never read as 'not high value'",
            {P + "product_family": "PROTECTION", P + "annual_premium": None, P + "sum_assured": 200000, P + "is_replacement": False},
            {"mi-general/n1": "YES"},
            [("mi-general", "COMPLETED"), ("mi-suitability", "SKIPPED_FALSE"), ("mi-high-value", "BLOCKED_UNKNOWN"),
             ("mi-replacement", "NOT_REACHED"), ("mi-escalation", "NOT_REACHED"), ("mi-closing", "NOT_REACHED")],
            ["mi-general/n1"], blocked={"reason": "BLOCKED_UNKNOWN", "at": "mi-high-value"},
            trace=["mi-suitability: entry FALSE", "mi-high-value: entry UNKNOWN"]),
        run("Premium missing but sum assured 600,000: UNKNOWN OR TRUE = TRUE; replacement flag missing is skipped with a reason",
            {P + "product_family": "PROTECTION", P + "annual_premium": None, P + "sum_assured": 600000, P + "is_replacement": None},
            {"mi-general/n1": "YES", "mi-high-value/n1": "YES", "mi-closing/n1": "YES"},
            [("mi-general", "COMPLETED"), ("mi-suitability", "SKIPPED_FALSE"), ("mi-high-value", "COMPLETED"),
             ("mi-replacement", "SKIPPED_UNKNOWN"), ("mi-escalation", "SKIPPED_PRIOR_OUTCOME"), ("mi-closing", "COMPLETED")],
            ["mi-general/n1", "mi-high-value/n1", "mi-closing/n1"], "COMPLETED"),
        run("Identity not confirmed: General ends the survey; later modules are not reached",
            {P + "product_family": "ILP", P + "annual_premium": 24000, P + "sum_assured": 300000, P + "is_replacement": True},
            {"mi-general/n1": "NO"},
            [("mi-general", "UNABLE_TO_VERIFY"), ("mi-suitability", "NOT_REACHED"), ("mi-high-value", "NOT_REACHED"),
             ("mi-replacement", "NOT_REACHED"), ("mi-escalation", "NOT_REACHED"), ("mi-closing", "NOT_REACHED")],
            ["mi-general/n1"], "UNABLE_TO_VERIFY")]
    return fixture("F8-survey-with-conditional-lego-modules", "A survey with multiple conditional Lego modules",
                   "Six module instances: one always, three with entry rules (each with its own UNKNOWN policy), one "
                   "activated by a prior module outcome, one closing. Every skip has a recorded reason. "
                   "SS-AT-001…005, 015, 026, 032.",
                   [YES_NO], [qg, qs_, qh, qr, qe, qc],
                   [w(qg, "Can you confirm that you are the policyholder?", YES_NO),
                    w(qs_, "Do you understand that the value of this plan can go down as well as up?", YES_NO),
                    w(qh, "Can you confirm the funds for this policy are your own?", YES_NO),
                    w(qr, "Were you told about the costs of replacing your existing policy?", YES_NO),
                    w(qc, "Thank you. Do you acknowledge that this call has been completed?", YES_NO),
                    w(qe, "May one of our specialists call you to explain this further?", YES_NO)],
                   [c_ilp, c_high, c_repl], [general, suit, high, repl, esc, closing], sv, runs,
                   fields=["policy.product_family", "policy.annual_premium", "policy.sum_assured", "policy.is_replacement"])


if __name__ == "__main__":
    out = sys.argv[1]
    total = 0
    for build in (f1, f2, f3, f4, f5, f6, f7, f8):
        fx = build()
        n = check(fx)
        total += n
        with open(f"{out}/{fx['fixture']}.json", "w") as fh:
            json.dump(fx, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        rejected = sum(len(r.get("rejected", [])) for r in fx["expected_runs"])
        print(f"OK {fx['fixture']}: {n} run(s), {rejected} rejected answer(s) verified")
    print(f"ALL OK: 8 fixtures, {total} expected runs")
