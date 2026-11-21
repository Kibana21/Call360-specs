"""Call360 Survey Studio — reference interpreter for fixture schema /5 (UC-02, owner decision D-161…).

Documentation tooling, NOT the engine, and NOT derived from the prototype's TypeScript. It is written from the contract
(04_SS-01_CANONICAL_CONTRACTS.md §7 and §8) and stands alone: it imports nothing from the earlier interpreters, whose
schemas /1–/4 (fixtures F, G, H, J) are untouched and still regenerate byte-for-byte from their own files.

What /5 specifies — and nothing else. Follow-up queues, rules, interruptions, jumps, activation triggers and decisions
are already specified by /1–/4 and do not appear here.

  ITEMS        One item master. An item is a QUESTION (YES_NO, SINGLE_SELECT, FREE_TEXT, NUMERIC, ACKNOWLEDGEMENT) or a
               STATEMENT. A node places an item; a STATEMENT node places a STATEMENT item and nothing else does.
  STATEMENT    Delivered, never asked: it consumes no answer, has exactly one route, and cannot branch.
  NUMERIC      {"number": n} checked against number_rule {integer, min?, max?}.
  ACKNOWLEDGEMENT  {"acknowledged": true} is the only accepted answer. An explicit {"acknowledged": false} is BLOCKED
               as unresolved policy (NON_ANSWER_POLICY_UNRESOLVED): never an answer, never a refusal, never a default.
  WORDING      Text may contain controlled variables {{field_code}}. Rendering is a pure function of the text and the
               facts. A variable that is unknown, missing or unusable means the wording is NOT delivered: the run ends in
               MISSING_INFORMATION_HALT / WORDING_VALUE_MISSING. Nothing is defaulted.
  EXECUTION ID Every placement is `<instance>/<node>`; the same item placed twice is two executions with two records.
  PLAN         A pure function of (survey, facts): modules IN / OUT / HALTS from application data alone; every item of
               the modules that may run with its exact wording; the points an ANSWER will decide left OPEN with their
               alternatives; READY or BLOCKED. A plan contains no answer and no chosen path.
  CONSISTENCY  Every item a run delivers is delivered with exactly the text the plan gave for it.

Expected values below are WRITTEN BY HAND; the interpreter must reproduce every one of them or it refuses to write files.

Usage: python3 reference_interpreter_v5.py <output_dir>
"""
import json
import re
import sys
from decimal import Decimal, InvalidOperation

SCHEMA = "call360.survey-studio.fixture/5"
NOTICE = ("Synthetic and illustrative. Wording, fields, limits and outcomes are examples for contract design only; "
          "nothing here is approved AIA/MAS language or business policy.")

FIELDS = {
    "policy.product_family": {"type": "ENUM", "values": ["PROTECTION", "ILP", "ENDOWMENT"], "label": "Product family"},
    "policy.annual_premium": {"type": "MONEY", "unit": "SGD", "label": "Annual premium"},
    "policy.sum_assured": {"type": "MONEY", "unit": "SGD", "label": "Sum assured"},
    "policy.is_replacement": {"type": "BOOLEAN", "label": "Replaces an existing policy"},
    "customer.age_years": {"type": "INTEGER", "unit": "years", "label": "Customer age"},
    "policy.plan_name": {"type": "TEXT", "label": "Plan name"},
    "policy.term_years": {"type": "INTEGER", "unit": "years", "label": "Policy term"},
}
OUTCOMES = ["COMPLETED", "CLARIFICATION_REQUIRED", "ESCALATE", "CUSTOMER_DECLINED", "UNABLE_TO_VERIFY"]
SINGLE_ROUTE = ("FREE_TEXT", "NUMERIC", "ACKNOWLEDGEMENT", "STATEMENT")
YES_NO = {"code": "OS-YES-NO", "version": 1, "options": [{"code": "YES", "label": "Yes"}, {"code": "NO", "label": "No"}]}


# ------------------------------------------------------------------------------------------------ wording and variables
TOKEN = re.compile(r"\{\{\s*([^{}]*?)\s*\}\}")


def variables_of(text):
    out = []
    for m in TOKEN.finditer(text):
        if m.group(1) not in out:
            out.append(m.group(1))
    return out


def group3(digits):
    out = ""
    while len(digits) > 3:
        out = "," + digits[-3:] + out
        digits = digits[:-3]
    return digits + out


def format_value(field, v):
    """One stated format per type. None = the value cannot be used in wording (INVALID). Never rounds or truncates."""
    t = field["type"]
    if t in ("MONEY", "INTEGER"):
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            return None
        try:
            d = Decimal(str(v))
        except InvalidOperation:
            return None
        if not d.is_finite():
            return None
        if t == "INTEGER":
            if d != d.to_integral_value():
                return None
            return ("-" if d < 0 else "") + group3(str(abs(int(d))))
        if (d * 100) != (d * 100).to_integral_value():
            return None  # more than two decimal places: not rounded, refused
        whole, cents = divmod(int(abs(d) * 100), 100)
        body = ("-" if d < 0 else "") + group3(str(whole)) + (f".{cents:02d}" if cents else "")
        return f"{field.get('unit', '')} {body}".strip()
    if t == "ENUM":
        if not isinstance(v, str) or v not in field.get("values", [v]):
            return None
        return v if len(v) <= 3 else v[0] + v[1:].lower().replace("_", " ")
    if t == "TEXT":
        return v.strip() if isinstance(v, str) and v.strip() else None
    return None  # BOOLEAN: a yes/no fact has no spoken form


def render(text, facts, fields):
    """Returns (rendered text or None, [{variable, value, state}])."""
    values = []
    for var in variables_of(text):
        f = fields.get(var)
        if f is None or f["type"] == "BOOLEAN":
            values.append({"variable": var, "value": None, "state": "UNKNOWN_VARIABLE"})
            continue
        raw = facts.get(var)
        if raw is None or raw == "":
            values.append({"variable": var, "value": None, "state": "MISSING"})
            continue
        val = format_value(f, raw)
        values.append({"variable": var, "value": val, "state": "INVALID" if val is None else "PRESENT"})
    rest = TOKEN.sub("", text)
    if "{{" in rest or "}}" in rest:
        # an unfinished variable is never spoken with its braces: the wording cannot be delivered at all
        values.append({"variable": "", "value": None, "state": "MALFORMED"})
    if any(v["state"] != "PRESENT" for v in values):
        return None, values
    by = {v["variable"]: v["value"] for v in values}
    return TOKEN.sub(lambda m: by[m.group(1)], text), values


def variable_problems(text, fields):
    out = []
    for var in variables_of(text):
        f = fields.get(var)
        if f is None:
            out.append("UNKNOWN_VARIABLE")
        elif f["type"] == "BOOLEAN":
            out.append("VARIABLE_TYPE_NOT_ALLOWED")
    if "{{" in TOKEN.sub("", text) or "}}" in TOKEN.sub("", text):
        out.append("VARIABLE_MALFORMED")
    return out


# --------------------------------------------------------------------------------------------------------- conditions
def tri(ast, params, facts):
    op = ast["op"]
    if op in ("AND", "OR"):
        vals = [tri(a, params, facts) for a in ast["args"]]
        if op == "AND":
            return "FALSE" if "FALSE" in vals else "UNKNOWN" if "UNKNOWN" in vals else "TRUE"
        return "TRUE" if "TRUE" in vals else "UNKNOWN" if "UNKNOWN" in vals else "FALSE"
    if op == "NOT":
        return {"TRUE": "FALSE", "FALSE": "TRUE", "UNKNOWN": "UNKNOWN"}[tri(ast["arg"], params, facts)]

    def val(o):
        if "literal" in o:
            return True, o["literal"]
        v = params.get(o["param"]) if "param" in o else facts.get(o["field"])
        return (False, None) if v is None or v == "" else (True, v)
    (lk, lv), (rk, rv) = val(ast["left"]), val(ast["right"])
    if not lk or not rk:
        return "UNKNOWN"  # a missing value is UNKNOWN — never FALSE
    if op in ("GT", "GTE", "LT", "LTE"):
        a, b = Decimal(str(lv)), Decimal(str(rv))
        r = {"GT": a > b, "GTE": a >= b, "LT": a < b, "LTE": a <= b}[op]
    else:
        r = (lv == rv) if op == "EQ" else (lv != rv)
    return "TRUE" if r else "FALSE"


def fields_of(ast, acc=None):
    acc = [] if acc is None else acc
    if ast["op"] in ("AND", "OR"):
        for a in ast["args"]:
            fields_of(a, acc)
    elif ast["op"] == "NOT":
        fields_of(ast["arg"], acc)
    else:
        for o in (ast["left"], ast["right"]):
            if "field" in o and o["field"] not in acc:
                acc.append(o["field"])
    return acc


def eligibility(inst, lib, facts):
    """Returns (status, condition-or-None): ACTIVATED | SKIPPED_FALSE | SKIPPED_UNKNOWN | HALTED_MISSING_INFORMATION."""
    e = inst["entry"]
    if e["mode"] == "ALWAYS":
        return "ACTIVATED", None
    b = e["binding"]
    c = next(x for x in lib["conditions"] if x["code"] == b["condition"]["code"] and x["version"] == b["condition"]["version"])
    r = tri(c["ast"], b.get("params", {}), facts)
    if r == "TRUE":
        return "ACTIVATED", c
    if r == "FALSE":
        return "SKIPPED_FALSE", c
    return ("SKIPPED_UNKNOWN" if b["unknown_policy"] == "SKIP_WITH_REASON" else "HALTED_MISSING_INFORMATION"), c


# ------------------------------------------------------------------------------------------------------------ lookups
def index(fx):
    lib = fx["library"]
    return {
        "items": {(i["code"], i["version"]): i for i in lib["items"]},
        "wordings": {(w["item"], w["wording_version"]): w for w in lib["wordings"]},
        "sets": {s["code"]: s for s in lib["option_sets"]},
        "modules": {(m["code"], m["revision"]): m for m in lib["modules"]},
        "fields": fx["catalog"]["fields"],
    }


def item_of(ix, node):
    it = ix["items"][(node["item"]["code"], node["item"]["version"])]
    return it, ix["wordings"][(it["code"], node["item"]["wording_version"])]


def edge_for(module, node_id, code):
    """Edge resolution: specific, then ANY, else none."""
    cands = [x for x in module["edges"] if x["from"] == node_id and x["on"] == code] or \
            [x for x in module["edges"] if x["from"] == node_id and x["on"] == "ANY"]
    return cands[0] if len(cands) == 1 else None


# --------------------------------------------------------------------------------------------------------- validation
def validate(fx):
    """Authoring-time errors, as [{code, at}] with at = `<module code>/<node>`. Order: modules, then nodes, as declared."""
    ix, errors = index(fx), []
    for m in fx["library"]["modules"]:
        for n in m["nodes"]:
            it, wd = item_of(ix, n)
            at = f"{m['code']}/{n['node']}"
            stmt = it["answer_type"] == "STATEMENT"
            if (n["type"] == "STATEMENT") != stmt:
                errors.append({"code": "NODE_ITEM_KIND_MISMATCH", "at": at})
            if stmt and (it.get("mandatory") or it.get("role")):
                errors.append({"code": "STATEMENT_NOT_A_QUESTION", "at": at})
            if it["answer_type"] in SINGLE_ROUTE:
                outs = [x for x in m["edges"] if x["from"] == n["node"]]
                if n["routing"]["mode"] != "ALL_TO_NEXT" or len(outs) > 1 or any(x["on"] != "AFTER_CAPTURE" for x in outs):
                    errors.append({"code": "SINGLE_ROUTE_ITEM_BRANCHES", "at": at})
            for p in variable_problems(wd["text"], ix["fields"]):
                errors.append({"code": p, "at": at})
            mode = wd.get("delivery_mode", "CONTROLLED_TTS")
            if mode == "CONVERSATIONAL":
                errors.append({"code": "DELIVERY_CONVERSATIONAL_BLOCKED", "at": at})
            elif mode == "EXACT_AUDIO":
                # no fixture can carry a usable, approved recording asset, so a recording always blocks
                errors.append({"code": "RECORDING_WITH_VARIABLE" if variables_of(wd["text"]) else "RECORDING_ASSET_MISSING", "at": at})
            rule = it.get("number_rule")
            if rule and "min" in rule and "max" in rule and rule["min"] > rule["max"]:
                errors.append({"code": "NUMBER_RULE_INVALID", "at": at})
    return errors


def answer_error(item, option_set, a):
    """The stable rejection code for an answer, or None when it is accepted."""
    t = item["answer_type"]
    if t == "NUMERIC":
        rule, n = item.get("number_rule", {"integer": False}), a.get("number")
        if isinstance(n, bool) or not isinstance(n, (int, float)):
            return "NUMBER_REQUIRED"
        d = Decimal(str(n))
        if not d.is_finite():
            return "NUMBER_REQUIRED"
        if rule.get("integer") and d != d.to_integral_value():
            return "NUMBER_NOT_WHOLE"
        if "min" in rule and d < Decimal(str(rule["min"])):
            return "NUMBER_TOO_LOW"
        if "max" in rule and d > Decimal(str(rule["max"])):
            return "NUMBER_TOO_HIGH"
        return None
    if t == "ACKNOWLEDGEMENT":
        if a.get("acknowledged") is True:
            return None
        return "NON_ANSWER_POLICY_UNRESOLVED" if a.get("acknowledged") is False else "ACKNOWLEDGEMENT_REQUIRED"
    if t == "FREE_TEXT":
        text, rule = (a.get("text") or "").strip(), item.get("text", {})
        if rule.get("required", True) and not text:
            return "TEXT_REQUIRED"
        if len(text) < rule.get("min_length", 0):
            return "TEXT_TOO_SHORT"
        if len(text) > rule.get("max_length", 2000):
            return "TEXT_TOO_LONG"
        return None
    if "choice" not in a:
        return "CHOICE_REQUIRED"
    return None if a["choice"] in [o["code"] for o in option_set["options"]] else "UNKNOWN_OPTION"


# ---------------------------------------------------------------------------------------------------------- execution
class Halt(Exception):
    def __init__(self, state, reason, at):
        self.state, self.reason, self.at = state, reason, at


class Pending(Exception):
    def __init__(self, key):
        self.key = key


def execute(fx, run):
    ix, lib, sv, facts = index(fx), fx["library"], fx["survey"], run.get("facts", {})
    insts = {i["instance"]: i for i in sv["instances"]}
    asked, delivered, rejections, answers = [], [], [], {}
    status, visited = {}, set()
    bad = {}
    for b in run.get("rejected", []):
        bad.setdefault(b["at"], []).append(b)
    terminal, pending = None, None

    def deliver(inst, module, node):
        it, wd = item_of(ix, node)
        key = f"{inst}/{node['node']}"
        if key in visited:
            raise Halt("DRAFT_INVALID", "REPEATED_EXECUTION", key)
        text, values = render(wd["text"].strip(), facts, ix["fields"])
        if text is None:
            raise Halt("MISSING_INFORMATION_HALT", "WORDING_VALUE_MISSING", key)
        stmt = it["answer_type"] == "STATEMENT"
        record = {"key": key, "item": f"{it['code']}@{it['version']}", "statement": stmt, "wording_version": wd["wording_version"],
                  "delivery_mode": wd.get("delivery_mode", "CONTROLLED_TTS"), "text": text, "values": values}
        if stmt:
            visited.add(key)
            delivered.append(record)
            answers[key] = {}
            return it, {}
        # a question: every answer that must be refused is offered first, in order; then the answer, if there is one
        for b in bad.get(key, []):
            err = answer_error(it, ix["sets"].get(it.get("option_set", {}).get("code")), b["answer"])
            assert err is not None, ("a rejected answer was accepted", key, b)
            rejections.append({"at": key, "error": err})
        if key not in run.get("answers", {}):
            raise Pending(key)
        a = run["answers"][key]
        err = answer_error(it, ix["sets"].get(it.get("option_set", {}).get("code")), a)
        assert err is None, ("the run's answer is not acceptable", key, a, err)
        visited.add(key)
        asked.append(key)
        delivered.append(record)
        answers[key] = a
        return it, a

    try:
        for name in sv["sequence"]:
            inst = insts[name]
            st, _ = eligibility(inst, lib, facts)
            if st != "ACTIVATED":
                status[name] = {"status": st}
                if st == "HALTED_MISSING_INFORMATION":
                    raise Halt("MISSING_INFORMATION_HALT", "ELIGIBILITY_UNKNOWN", name)
                continue
            module = ix["modules"][(inst["module"]["code"], inst["module"]["revision"])]
            nodes = {n["node"]: n for n in module["nodes"]}
            status[name] = {"status": "RUNNING"}
            cur = {"node": module["entry"]}
            while "outcome" not in cur:
                node = nodes[cur["node"]]
                it, a = deliver(name, module, node)
                code = "AFTER_CAPTURE" if it["answer_type"] in SINGLE_ROUTE else a["choice"]
                edge = edge_for(module, node["node"], code)
                if edge is None:
                    raise Halt("DRAFT_INVALID", "ROUTE_MISSING", f"{name}/{node['node']}")
                cur = edge["to"]
            out = cur["outcome"]
            status[name] = {"status": "ACTIVATED", "outcome": out}
            to = next(r["to"] for r in inst["routes"] if r["on"] == out)
            if to != "@CONTINUE":
                o = to["survey_outcome"]
                terminal = {"state": "COMPLETED" if o == "COMPLETED" else "ENDED_WITH_OUTCOME", "survey_outcome": o}
                break
        else:
            terminal = {"state": "COMPLETED", "survey_outcome": "COMPLETED"}
    except Halt as h:
        terminal = {"state": h.state, "reason": h.reason, "at": h.at}
    except Pending as p:
        pending = p.key

    # how every item of every module that started stands at the end of the run
    states = {}
    for name in sv["sequence"]:
        s = status.get(name, {}).get("status")
        if s not in ("ACTIVATED", "RUNNING"):
            continue
        module = ix["modules"][(insts[name]["module"]["code"], insts[name]["module"]["revision"])]
        for n in module["nodes"]:
            it, _ = item_of(ix, n)
            key = f"{name}/{n['node']}"
            if key in answers:
                a = answers[key]
                states[key] = "DELIVERED" if it["answer_type"] == "STATEMENT" else \
                    ("UNANSWERED" if it["answer_type"] == "FREE_TEXT" and not (a.get("text") or "").strip() else "ANSWERED")
            else:
                states[key] = "NOT_REACHED" if s == "RUNNING" else "SKIPPED"
    return {"asked": asked, "delivered": delivered, "rejections": rejections,
            "modules": [{"instance": n, **status.get(n, {"status": "NOT_REACHED"})} for n in sv["sequence"]],
            "terminal": terminal, "pending": pending, "evidence_states": states}


# --------------------------------------------------------------------------------------------------------------- plan
def on_every_path(module, node_id):
    """True when every path from the module's entry to any ending passes through `node_id`."""
    if module["entry"] == node_id:
        return True
    seen, stack = {node_id}, [module["entry"]]
    while stack:
        cur = stack.pop()
        if cur in seen:
            continue
        seen.add(cur)
        for x in module["edges"]:
            if x["from"] != cur:
                continue
            if "outcome" in x["to"]:
                return False
            stack.append(x["to"]["node"])
    return True


def plan(fx, facts):
    ix, lib, sv = index(fx), fx["library"], fx["survey"]
    insts = {i["instance"]: i for i in sv["instances"]}
    used, issues, modules, items, opens = [], [], [], {}, {}

    def note(code):
        if code in ix["fields"] and code not in used:
            used.append(code)

    for name in sv["sequence"]:
        inst = insts[name]
        st, cond = eligibility(inst, lib, facts)
        if cond:
            for f in fields_of(cond["ast"]):
                note(f)
        status = {"ACTIVATED": "IN", "SKIPPED_FALSE": "OUT", "SKIPPED_UNKNOWN": "OUT", "HALTED_MISSING_INFORMATION": "HALTS"}[st]
        modules.append({"instance": name, "status": status})
        if status == "HALTS":
            issues.append({"code": "ELIGIBILITY_UNKNOWN", "at": name})
        if status == "OUT":
            continue  # nothing of a module that will not run is planned, rendered or reported
        module = ix["modules"][(inst["module"]["code"], inst["module"]["revision"])]
        for n in module["nodes"]:
            it, wd = item_of(ix, n)
            key = f"{name}/{n['node']}"
            text, values = render(wd["text"].strip(), facts, ix["fields"])
            for v in variables_of(wd["text"]):
                note(v)
            if text is None:
                issues.append({"code": "WORDING_VALUE_MISSING", "at": key})
            stmt = it["answer_type"] == "STATEMENT"
            items[key] = {"statement": stmt, "role": it.get("statement_role") if stmt else it.get("role"), "mandatory": bool(it.get("mandatory")) and not stmt,
                          "delivery_mode": wd.get("delivery_mode", "CONTROLLED_TTS"), "wording_version": wd["wording_version"], "text": text, "values": values,
                          "certainty": "ALWAYS" if on_every_path(module, n["node"]) else "SOME"}
            if n["routing"]["mode"] == "PER_CHOICE":
                alts = [{"on": o["code"], "to": (edge_for(module, n["node"], o["code"]) or {}).get("to")}
                        for o in ix["sets"][it["option_set"]["code"]]["options"]]
                if len({json.dumps(a["to"], sort_keys=True) for a in alts}) > 1:  # open only when the answer really chooses
                    opens[key] = {"kind": "ANSWER", "alternatives": alts}
        if len(module["outcomes"]) > 1:
            opens[f"{name}:outcome"] = {"kind": "OUTCOME", "alternatives": [
                {"on": o, "to": next(r["to"] for r in inst["routes"] if r["on"] == o)} for o in module["outcomes"]]}

    def state(code):
        v = facts.get(code)
        if v is None or v == "":
            return "MISSING"
        f = ix["fields"][code]
        if f["type"] == "BOOLEAN":
            return "PRESENT" if isinstance(v, bool) else "INVALID"
        return "PRESENT" if format_value(f, v) is not None else "INVALID"
    return {"status": "BLOCKED" if issues else "READY", "issues": sorted(issues, key=lambda i: (i["at"], i["code"])),
            "inputs": {c: state(c) for c in used}, "modules": modules, "items": items, "open": opens}


# -------------------------------------------------------------------------------------------------------------- check
def check(fx):
    assert validate(fx) == fx["validation"]["errors"], (fx["fixture"], "validation", validate(fx), fx["validation"]["errors"])
    for p in fx["expected_plans"]:
        got = plan(fx, p.get("facts", {}))
        for k in ("status", "issues", "inputs", "modules", "items", "open"):
            assert got[k] == p["expect"][k], (fx["fixture"], "plan", p["name"], k, got[k], p["expect"][k])
    for r in fx["expected_runs"]:
        got = execute(fx, r)
        for k in ("asked", "delivered", "rejections", "modules", "terminal", "pending", "evidence_states"):
            assert got[k] == r["expect"][k], (fx["fixture"], "run", r["name"], k, got[k], r["expect"][k])
        # CONSISTENCY: whatever a run delivers, it delivers with exactly the text the plan gave for that item
        planned = plan(fx, r.get("facts", {}))["items"]
        for d in got["delivered"]:
            assert planned[d["key"]]["text"] == d["text"], (fx["fixture"], r["name"], "plan and run disagree", d["key"])
            assert planned[d["key"]]["values"] == d["values"], (fx["fixture"], r["name"], "plan and run disagree on values", d["key"])
    return len(fx["expected_plans"]), len(fx["expected_runs"])


# ------------------------------------------------------------------------------------------------------------ builders
def item(code, answer_type, intent, option_set=None, **extra):
    d = {"code": code, "version": 1, "answer_type": answer_type, "intent": intent}
    if option_set:
        d["option_set"] = {"code": option_set["code"], "version": option_set["version"]}
    d.update(extra)
    return d


def stmt(code, role, intent):
    return item(code, "STATEMENT", intent, statement_role=role)


def w(it, text, delivery_mode="CONTROLLED_TTS"):
    return {"item": it["code"], "wording_version": 1, "language": "en", "text": text, "delivery_mode": delivery_mode, "approval": "SYNTHETIC_UNAPPROVED"}


def nd(node, it, mode="ALL_TO_NEXT"):
    return {"node": node, "type": "STATEMENT" if it["answer_type"] == "STATEMENT" else "QUESTION",
            "item": {"code": it["code"], "version": 1, "wording_version": 1}, "routing": {"mode": mode}}


def e(edge, frm, on, node=None, outcome=None):
    return {"edge": edge, "from": frm, "on": on, "to": {"node": node} if node else {"outcome": outcome}}


def chain(nodes, last_outcome="COMPLETED"):
    """n1 → n2 → … → outcome, each by AFTER_CAPTURE: the edges of a module in which nothing branches."""
    return [e(f"e{k + 1}", a, "AFTER_CAPTURE", node=b) for k, (a, b) in enumerate(zip(nodes, nodes[1:]))] + \
           [e(f"e{len(nodes)}", nodes[-1], "AFTER_CAPTURE", outcome=last_outcome)]


def mod(code, name, outcomes, nodes, edges):
    return {"code": code, "revision": 1, "name": name, "outcomes": outcomes, "entry": nodes[0]["node"], "nodes": nodes, "edges": edges}


def inst(instance, module, entry=None, routes=None):
    return {"instance": instance, "module": {"code": module["code"], "revision": 1}, "entry": entry or {"mode": "ALWAYS"},
            "routes": routes or [{"on": o, "to": "@CONTINUE" if o == "COMPLETED" else {"survey_outcome": o}} for o in module["outcomes"]]}


def rule(cond, unknown_policy, **params):
    return {"mode": "RULE", "binding": {"condition": {"code": cond["code"], "version": 1}, "params": params, "unknown_policy": unknown_policy}}


def survey(code, instances):
    return {"code": code, "version_label": "1.0", "language": "en", "sequence": [i["instance"] for i in instances], "instances": instances}


def fixture(fid, title, purpose, items, wordings, modules, sv, plans, runs, errors=None, conditions=None, option_sets=None, fields=None):
    return {"schema": SCHEMA, "fixture": fid, "title": title, "purpose": purpose, "notice": NOTICE,
            "catalog": {"fields": {k: FIELDS[k] for k in (fields or [])}, "outcomes": OUTCOMES},
            "library": {"option_sets": option_sets or [], "items": items, "wordings": wordings, "conditions": conditions or [], "modules": modules},
            "survey": sv, "validation": {"errors": errors or []}, "expected_plans": plans, "expected_runs": runs}


def dv(key, it, text, values=None, statement=None):
    """One delivery record, written out by hand in each expectation."""
    return {"key": key, "item": f"{it['code']}@1", "statement": it["answer_type"] == "STATEMENT" if statement is None else statement,
            "wording_version": 1, "delivery_mode": "CONTROLLED_TTS", "text": text, "values": values or []}


def pi(it, text, certainty, values=None, role=None, mandatory=False):
    """One planned item, written out by hand in each expectation."""
    s = it["answer_type"] == "STATEMENT"
    return {"statement": s, "role": it.get("statement_role") if s else role, "mandatory": mandatory, "delivery_mode": "CONTROLLED_TTS",
            "wording_version": 1, "text": text, "values": values or [], "certainty": certainty}


def present(variable, value):
    return {"variable": variable, "value": value, "state": "PRESENT"}


def run(name, answers, expect, facts=None, rejected=None):
    d = {"name": name, "facts": facts or {}, "answers": answers}
    if rejected:
        d["rejected"] = rejected
    d["expect"] = expect
    return d


def exp(asked, delivered, modules, terminal, states, rejections=None, pending=None):
    return {"asked": asked, "delivered": delivered, "rejections": rejections or [],
            "modules": [{"instance": i, "status": s, **({"outcome": o} if o else {})} for i, s, o in modules],
            "terminal": terminal, "pending": pending, "evidence_states": states}


def planx(name, facts, status, modules, items, opens=None, inputs=None, issues=None):
    return {"name": name, "facts": facts, "expect": {"status": status, "issues": issues or [], "inputs": inputs or {},
                                                      "modules": [{"instance": i, "status": s} for i, s in modules], "items": items, "open": opens or {}}}


DONE = {"state": "COMPLETED", "survey_outcome": "COMPLETED"}
Y, N = {"choice": "YES"}, {"choice": "NO"}


# ============================================================================================================ fixtures
def k1():
    """Statements are delivered in order, take no answer, and are not delivered on a path that does not reach them."""
    s_open = stmt("S-OPENING", "OPENING", "Opens the call")
    q_id = item("Q-POLICYHOLDER", "YES_NO", "Customer confirms they are the policyholder", YES_NO)
    s_disc = stmt("S-DISCLOSURE", "DISCLOSURE", "States that the call is a verification call")
    s_tran = stmt("S-TRANSITION", "TRANSITION", "Moves on to the questions")
    q_expl = item("Q-EXPLAINED", "YES_NO", "Representative explained the plan", YES_NO)
    s_close = stmt("S-CLOSING", "CLOSING", "Closes the call")
    T = {"n1": "Good day. This is a service call about your policy.", "n2": "Can you confirm that you are the policyholder?",
         "n3": "This call is to verify how your policy was sold to you.", "n4": "I will now ask two short questions.",
         "n5": "Did your representative explain how the plan works?", "n6": "Thank you. This call is now complete."}
    its = [s_open, q_id, s_disc, s_tran, q_expl, s_close]
    m = mod("M-CALL", "Call", ["COMPLETED", "UNABLE_TO_VERIFY"],
            [nd("n1", s_open), nd("n2", q_id, "PER_CHOICE"), nd("n3", s_disc), nd("n4", s_tran), nd("n5", q_expl), nd("n6", s_close)],
            [e("e1", "n1", "AFTER_CAPTURE", node="n2"), e("e2", "n2", "YES", node="n3"), e("e3", "n2", "NO", outcome="UNABLE_TO_VERIFY"),
             e("e4", "n3", "AFTER_CAPTURE", node="n4"), e("e5", "n4", "AFTER_CAPTURE", node="n5"), e("e6", "n5", "ANY", node="n6"),
             e("e7", "n6", "AFTER_CAPTURE", outcome="COMPLETED")])
    sv = survey("S-STATEMENTS", [inst("mi-call", m)])
    k = lambda n: f"mi-call/{n}"  # noqa: E731
    by = dict(zip(["n1", "n2", "n3", "n4", "n5", "n6"], its))
    plans = [planx("No application data is needed: every customer gets the same plan", {}, "READY", [("mi-call", "IN")],
                   {k("n1"): pi(s_open, T["n1"], "ALWAYS"), k("n2"): pi(q_id, T["n2"], "ALWAYS"), k("n3"): pi(s_disc, T["n3"], "SOME"),
                    k("n4"): pi(s_tran, T["n4"], "SOME"), k("n5"): pi(q_expl, T["n5"], "SOME"), k("n6"): pi(s_close, T["n6"], "SOME")},
                   opens={k("n2"): {"kind": "ANSWER", "alternatives": [{"on": "YES", "to": {"node": "n3"}}, {"on": "NO", "to": {"outcome": "UNABLE_TO_VERIFY"}}]},
                          "mi-call:outcome": {"kind": "OUTCOME", "alternatives": [{"on": "COMPLETED", "to": "@CONTINUE"}, {"on": "UNABLE_TO_VERIFY", "to": {"survey_outcome": "UNABLE_TO_VERIFY"}}]}})]
    runs = [
        run("Every statement is delivered in its place; only the two questions are asked", {k("n2"): Y, k("n5"): Y},
            exp([k("n2"), k("n5")], [dv(k(n), by[n], T[n]) for n in ["n1", "n2", "n3", "n4", "n5", "n6"]], [("mi-call", "ACTIVATED", "COMPLETED")], DONE,
                {k("n1"): "DELIVERED", k("n2"): "ANSWERED", k("n3"): "DELIVERED", k("n4"): "DELIVERED", k("n5"): "ANSWERED", k("n6"): "DELIVERED"})),
        run("The module ends early: the statements after that point are not delivered", {k("n2"): N},
            exp([k("n2")], [dv(k("n1"), s_open, T["n1"]), dv(k("n2"), q_id, T["n2"])], [("mi-call", "ACTIVATED", "UNABLE_TO_VERIFY")],
                {"state": "ENDED_WITH_OUTCOME", "survey_outcome": "UNABLE_TO_VERIFY"},
                {k("n1"): "DELIVERED", k("n2"): "ANSWERED", k("n3"): "SKIPPED", k("n4"): "SKIPPED", k("n5"): "SKIPPED", k("n6"): "SKIPPED"})),
        run("A statement needs no answer: with no answers supplied, the opening is delivered and the first QUESTION is pending", {},
            exp([], [dv(k("n1"), s_open, T["n1"])], [("mi-call", "RUNNING", None)], None,
                {k("n1"): "DELIVERED", k("n2"): "NOT_REACHED", k("n3"): "NOT_REACHED", k("n4"): "NOT_REACHED", k("n5"): "NOT_REACHED", k("n6"): "NOT_REACHED"}, pending=k("n2"))),
    ]
    return fixture("K1-statements-are-delivered-in-order-and-take-no-answer", "Statements are delivered in order and take no answer",
                   "An opening, a disclosure, a transition and a closing statement around two questions. Statements are delivered, never asked; "
                   "they consume no answer; they appear in `delivered` and never in `asked`; a path that ends early does not deliver the rest.",
                   its, [w(i, T[n]) for n, i in by.items()], [m], sv, plans, runs, option_sets=[YES_NO])


def k2():
    """A statement can neither branch nor be answered; a question that has one way on cannot branch either."""
    s_a = stmt("S-TWO-WAYS", "TRANSITION", "A statement given two routes")
    s_b = stmt("S-AS-QUESTION", "DISCLOSURE", "A statement placed by a QUESTION node")
    q_c = item("Q-AS-STATEMENT", "YES_NO", "A question placed by a STATEMENT node", YES_NO)
    s_d = stmt("S-MANDATORY", "OPENING", "A statement marked mandatory with a question role")
    s_d.update({"mandatory": True, "role": "IDENTITY_CHECK"})
    q_n = item("Q-NUMBER-BRANCH", "NUMERIC", "A number question given a per-choice route", number_rule={"integer": True})
    q_r = item("Q-BAD-LIMITS", "NUMERIC", "A number question whose lowest is above its highest", number_rule={"integer": True, "min": 10, "max": 5})
    nb, nc = nd("n2", s_b), nd("n3", q_c)
    nb["type"], nc["type"] = "QUESTION", "STATEMENT"
    m = mod("M-INVALID", "Invalid on purpose", ["COMPLETED", "ESCALATE"],
            [nd("n1", s_a), nb, nc, nd("n4", s_d), nd("n5", q_n, "PER_CHOICE"), nd("n6", q_r)],
            [e("e1", "n1", "AFTER_CAPTURE", node="n2"), e("e1b", "n1", "ANY", outcome="ESCALATE"), e("e2", "n2", "AFTER_CAPTURE", node="n3"),
             e("e3", "n3", "ANY", node="n4"), e("e4", "n4", "AFTER_CAPTURE", node="n5"), e("e5", "n5", "AFTER_CAPTURE", node="n6"),
             e("e6", "n6", "AFTER_CAPTURE", outcome="COMPLETED")])
    its = [s_a, s_b, q_c, s_d, q_n, q_r]
    errors = [{"code": "SINGLE_ROUTE_ITEM_BRANCHES", "at": "M-INVALID/n1"}, {"code": "NODE_ITEM_KIND_MISMATCH", "at": "M-INVALID/n2"},
              {"code": "NODE_ITEM_KIND_MISMATCH", "at": "M-INVALID/n3"}, {"code": "STATEMENT_NOT_A_QUESTION", "at": "M-INVALID/n4"},
              {"code": "SINGLE_ROUTE_ITEM_BRANCHES", "at": "M-INVALID/n5"}, {"code": "NUMBER_RULE_INVALID", "at": "M-INVALID/n6"}]
    return fixture("K2-a-statement-cannot-branch-or-be-answered", "A statement cannot branch or be answered",
                   "Six authoring errors, one per node: a statement with two routes; a statement placed as a question; a question placed as a "
                   "statement; a statement marked mandatory with a question role; a number question routed per choice; a number rule whose lowest is "
                   "above its highest. Validation only: an invalid draft is not run.",
                   its, [w(i, f"Synthetic wording for {i['code']}.") for i in its], [m], survey("S-INVALID", [inst("mi-invalid", m)]), [], [],
                   errors=errors, option_sets=[YES_NO])


def k3():
    """Numeric validation: required, whole number, lowest, highest; a decimal where decimals are allowed."""
    q_years = item("Q-YEARS", "NUMERIC", "Years the customer was told they would pay", number_rule={"integer": True, "min": 1, "max": 99, "unit": "years"}, mandatory=True)
    q_share = item("Q-SHARE", "NUMERIC", "Share of income the premium takes, in percent", number_rule={"integer": False, "min": 0, "max": 100, "unit": "percent"})
    q_open = item("Q-ANY-NUMBER", "NUMERIC", "A number with no limits", number_rule={"integer": False})
    T = {"n1": "For how many years did your representative say you would pay premiums?", "n2": "Roughly what share of your income goes to this premium, in percent?",
         "n3": "How many other policies do you hold?"}
    m = mod("M-NUMBERS", "Numbers", ["COMPLETED"], [nd("n1", q_years), nd("n2", q_share), nd("n3", q_open)], chain(["n1", "n2", "n3"]))
    k = lambda n: f"mi-numbers/{n}"  # noqa: E731
    its = [q_years, q_share, q_open]
    all_states = {k("n1"): "ANSWERED", k("n2"): "ANSWERED", k("n3"): "ANSWERED"}
    full = [dv(k("n1"), q_years, T["n1"]), dv(k("n2"), q_share, T["n2"]), dv(k("n3"), q_open, T["n3"])]
    runs = [
        run("Valid numbers are accepted: a whole number, a decimal where decimals are allowed, and a negative number where nothing forbids it",
            {k("n1"): {"number": 20}, k("n2"): {"number": 12.5}, k("n3"): {"number": -3}},
            exp([k("n1"), k("n2"), k("n3")], full, [("mi-numbers", "ACTIVATED", "COMPLETED")], DONE, all_states)),
        run("The limits themselves are accepted: lowest and highest are inclusive",
            {k("n1"): {"number": 1}, k("n2"): {"number": 100}, k("n3"): {"number": 0}},
            exp([k("n1"), k("n2"), k("n3")], full, [("mi-numbers", "ACTIVATED", "COMPLETED")], DONE, all_states)),
        run("Each invalid number is refused with its own code, and the same question is asked again",
            {k("n1"): {"number": 20}, k("n2"): {"number": 30}, k("n3"): {"number": 2}},
            exp([k("n1"), k("n2"), k("n3")], full, [("mi-numbers", "ACTIVATED", "COMPLETED")], DONE, all_states,
                rejections=[{"at": k("n1"), "error": "NUMBER_REQUIRED"}, {"at": k("n1"), "error": "NUMBER_REQUIRED"}, {"at": k("n1"), "error": "NUMBER_NOT_WHOLE"},
                            {"at": k("n1"), "error": "NUMBER_TOO_LOW"}, {"at": k("n1"), "error": "NUMBER_TOO_HIGH"},
                            {"at": k("n2"), "error": "NUMBER_TOO_LOW"}, {"at": k("n2"), "error": "NUMBER_TOO_HIGH"}]),
            rejected=[{"at": k("n1"), "answer": {}, "error": "NUMBER_REQUIRED"}, {"at": k("n1"), "answer": {"number": "twenty"}, "error": "NUMBER_REQUIRED"},
                      {"at": k("n1"), "answer": {"number": 2.5}, "error": "NUMBER_NOT_WHOLE"}, {"at": k("n1"), "answer": {"number": 0}, "error": "NUMBER_TOO_LOW"},
                      {"at": k("n1"), "answer": {"number": 100}, "error": "NUMBER_TOO_HIGH"},
                      {"at": k("n2"), "answer": {"number": -0.5}, "error": "NUMBER_TOO_LOW"}, {"at": k("n2"), "answer": {"number": 100.5}, "error": "NUMBER_TOO_HIGH"}]),
    ]
    plans = [planx("A number question is planned like any other: its wording is settled, its answer is not", {}, "READY", [("mi-numbers", "IN")],
                   {k("n1"): pi(q_years, T["n1"], "ALWAYS", mandatory=True), k("n2"): pi(q_share, T["n2"], "ALWAYS"), k("n3"): pi(q_open, T["n3"], "ALWAYS")})]
    return fixture("K3-numeric-answers-are-validated", "Numeric answers are validated",
                   "Three number questions: whole numbers from 1 to 99; decimals from 0 to 100; no limits. Accepted values, the inclusive limits, and each "
                   "rejection code. A rejected answer is never recorded and the question is asked again.",
                   its, [w(i, T[n]) for n, i in zip(["n1", "n2", "n3"], its)], [m], survey("S-NUMBERS", [inst("mi-numbers", m)]), plans, runs)


def k4():
    """An acknowledgement accepts only "acknowledged". "Not acknowledged" is blocked as unresolved policy."""
    s_sum = stmt("S-SUMMARY", "DISCLOSURE", "States what the customer is asked to acknowledge")
    q_ack = item("Q-ACK", "ACKNOWLEDGEMENT", "Customer acknowledges the summary")
    s_close = stmt("S-CLOSE", "CLOSING", "Closes the call")
    T = {"n1": "Your policy has a fourteen-day free-look period.", "n2": "Please confirm that you have heard this.", "n3": "Thank you. This call is now complete."}
    m = mod("M-ACK", "Acknowledgement", ["COMPLETED"], [nd("n1", s_sum), nd("n2", q_ack), nd("n3", s_close)], chain(["n1", "n2", "n3"]))
    k = lambda n: f"mi-ack/{n}"  # noqa: E731
    its = [s_sum, q_ack, s_close]
    waiting = {k("n1"): "DELIVERED", k("n2"): "NOT_REACHED", k("n3"): "NOT_REACHED"}
    runs = [
        run("Acknowledged: the call continues", {k("n2"): {"acknowledged": True}},
            exp([k("n2")], [dv(k("n1"), s_sum, T["n1"]), dv(k("n2"), q_ack, T["n2"]), dv(k("n3"), s_close, T["n3"])], [("mi-ack", "ACTIVATED", "COMPLETED")], DONE,
                {k("n1"): "DELIVERED", k("n2"): "ANSWERED", k("n3"): "DELIVERED"})),
        run("NOT acknowledged: blocked as unresolved policy. Nothing is recorded, nothing is assumed, and the call does not continue", {},
            exp([], [dv(k("n1"), s_sum, T["n1"])], [("mi-ack", "RUNNING", None)], None, waiting,
                rejections=[{"at": k("n2"), "error": "NON_ANSWER_POLICY_UNRESOLVED"}], pending=k("n2")),
            rejected=[{"at": k("n2"), "answer": {"acknowledged": False}, "error": "NON_ANSWER_POLICY_UNRESOLVED"}]),
        run("No answer at all, or an answer of another kind, is refused; it is never read as an acknowledgement", {},
            exp([], [dv(k("n1"), s_sum, T["n1"])], [("mi-ack", "RUNNING", None)], None, waiting,
                rejections=[{"at": k("n2"), "error": "ACKNOWLEDGEMENT_REQUIRED"}, {"at": k("n2"), "error": "ACKNOWLEDGEMENT_REQUIRED"}], pending=k("n2")),
            rejected=[{"at": k("n2"), "answer": {}, "error": "ACKNOWLEDGEMENT_REQUIRED"}, {"at": k("n2"), "answer": {"choice": "YES"}, "error": "ACKNOWLEDGEMENT_REQUIRED"}]),
    ]
    plans = [planx("The acknowledgement is planned; what happens if it is not given is not part of any plan", {}, "READY", [("mi-ack", "IN")],
                   {k("n1"): pi(s_sum, T["n1"], "ALWAYS"), k("n2"): pi(q_ack, T["n2"], "ALWAYS"), k("n3"): pi(s_close, T["n3"], "ALWAYS")})]
    return fixture("K4-acknowledgement-accepted-or-blocked-as-unresolved-policy", "An acknowledgement is accepted, or blocked as unresolved policy",
                   "The only accepted answer is `acknowledged: true`. An explicit `acknowledged: false` is refused with NON_ANSWER_POLICY_UNRESOLVED and the "
                   "run stays pending at that question: what a call does when a customer does not acknowledge has not been decided, so no route, outcome "
                   "or default is invented for it.",
                   its, [w(i, T[n]) for n, i in zip(["n1", "n2", "n3"], its)], [m], survey("S-ACK", [inst("mi-ack", m)]), plans, runs)


def k5():
    """Controlled variables: deterministic substitution; a missing or unusable value stops delivery."""
    s_plan = stmt("S-PLAN", "OPENING", "Names the plan")
    s_prem = stmt("S-PREMIUM", "DISCLOSURE", "States the premium, the term and the product family")
    q_ok = item("Q-CORRECT", "YES_NO", "Customer confirms the details", YES_NO)
    s_end = stmt("S-END", "CLOSING", "Closes the call, naming the plan again")
    T = {"n1": "Good day. This call is about your {{policy.plan_name}} plan.",
         "n2": "Our records show a premium of {{policy.annual_premium}} a year for {{policy.term_years}} years. It is a {{ policy.product_family }} plan.",
         "n3": "Are these details correct?", "n4": "Thank you for confirming your {{policy.plan_name}} plan."}
    m = mod("M-DETAILS", "Details", ["COMPLETED"], [nd("n1", s_plan), nd("n2", s_prem), nd("n3", q_ok), nd("n4", s_end)],
            [e("e1", "n1", "AFTER_CAPTURE", node="n2"), e("e2", "n2", "AFTER_CAPTURE", node="n3"), e("e3", "n3", "ANY", node="n4"), e("e4", "n4", "AFTER_CAPTURE", outcome="COMPLETED")])
    k = lambda n: f"mi-details/{n}"  # noqa: E731
    its = [s_plan, s_prem, q_ok, s_end]
    flds = ["policy.plan_name", "policy.annual_premium", "policy.term_years", "policy.product_family"]
    a = {"policy.plan_name": "SecureLife Protect", "policy.annual_premium": 3000, "policy.term_years": 20, "policy.product_family": "PROTECTION"}
    b = {"policy.plan_name": "  GrowthLink Invest ", "policy.annual_premium": 1234567.5, "policy.term_years": 5, "policy.product_family": "ILP"}
    missing = {**a, "policy.annual_premium": None}
    invalid = {**a, "policy.annual_premium": 3000.005, "policy.term_years": 20}
    wrong_kind = {**a, "policy.product_family": "UNLISTED"}
    pn = lambda v: [present("policy.plan_name", v)]  # noqa: E731
    va = [present("policy.annual_premium", "SGD 3,000"), present("policy.term_years", "20"), present("policy.product_family", "Protection")]
    vb = [present("policy.annual_premium", "SGD 1,234,567.50"), present("policy.term_years", "5"), present("policy.product_family", "ILP")]
    A = {"n1": "Good day. This call is about your SecureLife Protect plan.",
         "n2": "Our records show a premium of SGD 3,000 a year for 20 years. It is a Protection plan.", "n3": T["n3"], "n4": "Thank you for confirming your SecureLife Protect plan."}
    B = {"n1": "Good day. This call is about your GrowthLink Invest plan.",
         "n2": "Our records show a premium of SGD 1,234,567.50 a year for 5 years. It is a ILP plan.", "n3": T["n3"], "n4": "Thank you for confirming your GrowthLink Invest plan."}
    ok = {c: "PRESENT" for c in flds}
    bad_n2 = lambda vals: {"statement": True, "role": "DISCLOSURE", "mandatory": False, "delivery_mode": "CONTROLLED_TTS", "wording_version": 1, "text": None, "values": vals, "certainty": "ALWAYS"}  # noqa: E731
    v_missing = [{"variable": "policy.annual_premium", "value": None, "state": "MISSING"}, present("policy.term_years", "20"), present("policy.product_family", "Protection")]
    v_invalid = [{"variable": "policy.annual_premium", "value": None, "state": "INVALID"}, present("policy.term_years", "20"), present("policy.product_family", "Protection")]
    v_kind = [present("policy.annual_premium", "SGD 3,000"), present("policy.term_years", "20"), {"variable": "policy.product_family", "value": None, "state": "INVALID"}]
    halt = {"state": "MISSING_INFORMATION_HALT", "reason": "WORDING_VALUE_MISSING", "at": k("n2")}
    stopped = {k("n1"): "DELIVERED", k("n2"): "NOT_REACHED", k("n3"): "NOT_REACHED", k("n4"): "NOT_REACHED"}
    plans = [
        planx("Every value present: every sentence is settled, with the values that went into it", a, "READY", [("mi-details", "IN")],
              {k("n1"): pi(s_plan, A["n1"], "ALWAYS", pn("SecureLife Protect")), k("n2"): pi(s_prem, A["n2"], "ALWAYS", va),
               k("n3"): pi(q_ok, A["n3"], "ALWAYS"), k("n4"): pi(s_end, A["n4"], "ALWAYS", pn("SecureLife Protect"))}, inputs=ok),
        planx("Other values, other sentences: cents are shown only when there are any; text is trimmed; a short code is spoken as it is", b, "READY", [("mi-details", "IN")],
              {k("n1"): pi(s_plan, B["n1"], "ALWAYS", pn("GrowthLink Invest")), k("n2"): pi(s_prem, B["n2"], "ALWAYS", vb),
               k("n3"): pi(q_ok, B["n3"], "ALWAYS"), k("n4"): pi(s_end, B["n4"], "ALWAYS", pn("GrowthLink Invest"))}, inputs=ok),
        planx("A missing value: the plan is BLOCKED at that item; the other items are still settled", missing, "BLOCKED", [("mi-details", "IN")],
              {k("n1"): pi(s_plan, A["n1"], "ALWAYS", pn("SecureLife Protect")), k("n2"): bad_n2(v_missing),
               k("n3"): pi(q_ok, A["n3"], "ALWAYS"), k("n4"): pi(s_end, A["n4"], "ALWAYS", pn("SecureLife Protect"))},
              inputs={**ok, "policy.annual_premium": "MISSING"}, issues=[{"code": "WORDING_VALUE_MISSING", "at": k("n2")}]),
        planx("An amount with more than two decimals is not rounded: it is unusable", invalid, "BLOCKED", [("mi-details", "IN")],
              {k("n1"): pi(s_plan, A["n1"], "ALWAYS", pn("SecureLife Protect")), k("n2"): bad_n2(v_invalid),
               k("n3"): pi(q_ok, A["n3"], "ALWAYS"), k("n4"): pi(s_end, A["n4"], "ALWAYS", pn("SecureLife Protect"))},
              inputs={**ok, "policy.annual_premium": "INVALID"}, issues=[{"code": "WORDING_VALUE_MISSING", "at": k("n2")}]),
        planx("A value outside the field's list is unusable", wrong_kind, "BLOCKED", [("mi-details", "IN")],
              {k("n1"): pi(s_plan, A["n1"], "ALWAYS", pn("SecureLife Protect")), k("n2"): bad_n2(v_kind),
               k("n3"): pi(q_ok, A["n3"], "ALWAYS"), k("n4"): pi(s_end, A["n4"], "ALWAYS", pn("SecureLife Protect"))},
              inputs={**ok, "policy.product_family": "INVALID"}, issues=[{"code": "WORDING_VALUE_MISSING", "at": k("n2")}]),
    ]
    d = lambda texts, v1, v2: [dv(k("n1"), s_plan, texts["n1"], v1), dv(k("n2"), s_prem, texts["n2"], v2), dv(k("n3"), q_ok, texts["n3"]), dv(k("n4"), s_end, texts["n4"], v1)]  # noqa: E731
    done = {k("n1"): "DELIVERED", k("n2"): "DELIVERED", k("n3"): "ANSWERED", k("n4"): "DELIVERED"}
    runs = [
        run("The same wording and the same facts give the same sentences, and the evidence records the values used", {k("n3"): Y},
            exp([k("n3")], d(A, pn("SecureLife Protect"), va), [("mi-details", "ACTIVATED", "COMPLETED")], DONE, done), facts=a),
        run("The same survey, another application: different sentences from the same approved wording", {k("n3"): N},
            exp([k("n3")], d(B, pn("GrowthLink Invest"), vb), [("mi-details", "ACTIVATED", "COMPLETED")], DONE, done), facts=b),
        run("A missing value: the opening is delivered, then the call HALTS before the disclosure. Nothing is defaulted or left out", {k("n3"): Y},
            exp([], [dv(k("n1"), s_plan, A["n1"], pn("SecureLife Protect"))], [("mi-details", "RUNNING", None)], halt, stopped), facts=missing),
        run("An unusable value halts in the same way: it is not rounded to make it fit", {k("n3"): Y},
            exp([], [dv(k("n1"), s_plan, A["n1"], pn("SecureLife Protect"))], [("mi-details", "RUNNING", None)], halt, stopped), facts=invalid),
    ]
    return fixture("K5-controlled-variables-render-deterministically-or-halt", "Controlled variables render deterministically, or the call halts",
                   "Four variables of four types (text, money, whole number, enumerated value), one used twice. Rendering is a pure function of the "
                   "wording and the facts: one fixed format per type. A value that is missing, has more than two decimals, or is not in the field's list "
                   "is never defaulted, rounded or skipped — the item is not delivered, the plan is BLOCKED and the run halts.",
                   its, [w(i, T[n]) for n, i in zip(["n1", "n2", "n3", "n4"], its)], [m], survey("S-VARIABLES", [inst("mi-details", m)]), plans, runs,
                   option_sets=[YES_NO], fields=flds)


def k6():
    """Wording that cannot be approved as written: unknown and unusable variables, and delivery that is blocked."""
    s_unknown = stmt("S-UNKNOWN-FIELD", "OPENING", "Names a field that is not in the catalog")
    s_bool = stmt("S-YES-NO-FACT", "DISCLOSURE", "Tries to speak a yes/no fact")
    s_broken = stmt("S-UNFINISHED", "TRANSITION", "Has an unfinished variable")
    s_conv = stmt("S-OWN-WORDS", "TRANSITION", "Left to the assistant's own words")
    s_rec = stmt("S-RECORDING", "DISCLOSURE", "An approved recording, with no recording attached")
    s_recvar = stmt("S-RECORDING-VARIABLE", "CLOSING", "A recording that would have to contain a variable")
    T = {"n1": "Good day {{customer.nickname}}.", "n2": "This policy replaces another: {{policy.is_replacement}}.", "n3": "Your plan is {{policy.plan_name.",
         "n4": "Explain the next part in your own words.", "n5": "This call may be recorded.", "n6": "Goodbye, and thank you for choosing {{policy.plan_name}}."}
    its = [s_unknown, s_bool, s_broken, s_conv, s_rec, s_recvar]
    modes = {"n4": "CONVERSATIONAL", "n5": "EXACT_AUDIO", "n6": "EXACT_AUDIO"}
    m = mod("M-WORDING", "Wording that cannot be approved", ["COMPLETED"], [nd(f"n{i + 1}", it) for i, it in enumerate(its)], chain([f"n{i + 1}" for i in range(6)]))
    k = lambda n: f"mi-wording/{n}"  # noqa: E731
    errors = [{"code": "UNKNOWN_VARIABLE", "at": "M-WORDING/n1"}, {"code": "VARIABLE_TYPE_NOT_ALLOWED", "at": "M-WORDING/n2"},
              {"code": "VARIABLE_MALFORMED", "at": "M-WORDING/n3"}, {"code": "DELIVERY_CONVERSATIONAL_BLOCKED", "at": "M-WORDING/n4"},
              {"code": "RECORDING_ASSET_MISSING", "at": "M-WORDING/n5"}, {"code": "RECORDING_WITH_VARIABLE", "at": "M-WORDING/n6"}]
    facts = {"policy.plan_name": "SecureLife Protect", "policy.is_replacement": True}
    unknown = lambda v: [{"variable": v, "value": None, "state": "UNKNOWN_VARIABLE"}]  # noqa: E731

    def p(it, text, values=None, mode="CONTROLLED_TTS"):
        return {"statement": True, "role": it["statement_role"], "mandatory": False, "delivery_mode": mode, "wording_version": 1, "text": text, "values": values or [], "certainty": "ALWAYS"}
    plans = [planx("An unknown variable can never be rendered, whatever the customer's data: the plan is BLOCKED at each one", facts, "BLOCKED", [("mi-wording", "IN")],
                   {k("n1"): p(s_unknown, None, unknown("customer.nickname")), k("n2"): p(s_bool, None, unknown("policy.is_replacement")),
                    k("n3"): p(s_broken, None, [{"variable": "", "value": None, "state": "MALFORMED"}]), k("n4"): p(s_conv, T["n4"], mode="CONVERSATIONAL"), k("n5"): p(s_rec, T["n5"], mode="EXACT_AUDIO"),
                    k("n6"): p(s_recvar, "Goodbye, and thank you for choosing SecureLife Protect.", [present("policy.plan_name", "SecureLife Protect")], mode="EXACT_AUDIO")},
                   inputs={"policy.is_replacement": "PRESENT", "policy.plan_name": "PRESENT"},
                   issues=[{"code": "WORDING_VALUE_MISSING", "at": k("n1")}, {"code": "WORDING_VALUE_MISSING", "at": k("n2")}, {"code": "WORDING_VALUE_MISSING", "at": k("n3")}])]
    runs = [run("If such a draft were run, it halts at the first sentence that cannot be built — it is never spoken with the variable left in", {},
                exp([], [], [("mi-wording", "RUNNING", None)], {"state": "MISSING_INFORMATION_HALT", "reason": "WORDING_VALUE_MISSING", "at": k("n1")},
                    {k(f"n{i}"): "NOT_REACHED" for i in range(1, 7)}), facts=facts)]
    return fixture("K6-wording-that-cannot-be-approved-is-an-error", "Wording that cannot be approved is an error",
                   "Six authoring errors, one per statement: a variable that is not a catalog field; a yes/no fact, which has no spoken form; an "
                   "unfinished variable; delivery in the assistant's own words, which is blocked; an approved recording with no recording attached, "
                   "which blocks delivery and is not a warning; and a recording that would have to contain a variable. Run anyway, the draft halts.",
                   its, [w(i, T[n], modes.get(n, "CONTROLLED_TTS")) for n, i in zip([f"n{j}" for j in range(1, 7)], its)], [m], survey("S-WORDING", [inst("mi-wording", m)]),
                   plans, runs, errors=errors, fields=["policy.plan_name", "policy.is_replacement"])


def k7():
    """The same question placed more than once: every placement has its own execution identity and its own evidence."""
    q_clear = item("Q-CLEAR", "YES_NO", "Customer finds what was just said clear", YES_NO)
    s_one = stmt("S-FIRST-TOPIC", "TRANSITION", "Introduces the first topic")
    s_two = stmt("S-SECOND-TOPIC", "TRANSITION", "Introduces the second topic")
    T = {"clear": "Is that clear to you?", "one": "First, the premium is paid once a year.", "two": "Second, the cover lasts for the whole term."}
    m1 = mod("M-TWO-TOPICS", "Two topics", ["COMPLETED"], [nd("n1", s_one), nd("n2", q_clear), nd("n3", s_two), nd("n4", q_clear)],
             [e("e1", "n1", "AFTER_CAPTURE", node="n2"), e("e2", "n2", "ANY", node="n3"), e("e3", "n3", "AFTER_CAPTURE", node="n4"), e("e4", "n4", "ANY", outcome="COMPLETED")])
    m2 = mod("M-RECAP", "Recap", ["COMPLETED"], [nd("n1", q_clear)], [e("e1", "n1", "ANY", outcome="COMPLETED")])
    sv = survey("S-REPEATED", [inst("mi-topics", m1), inst("mi-recap", m2), inst("mi-recap-2", m2)])
    keys = ["mi-topics/n2", "mi-topics/n4", "mi-recap/n1", "mi-recap-2/n1"]
    plans = [planx("Four placements of one question are four planned items", {}, "READY", [("mi-topics", "IN"), ("mi-recap", "IN"), ("mi-recap-2", "IN")],
                   {"mi-topics/n1": pi(s_one, T["one"], "ALWAYS"), "mi-topics/n2": pi(q_clear, T["clear"], "ALWAYS"), "mi-topics/n3": pi(s_two, T["two"], "ALWAYS"),
                    "mi-topics/n4": pi(q_clear, T["clear"], "ALWAYS"), "mi-recap/n1": pi(q_clear, T["clear"], "ALWAYS"), "mi-recap-2/n1": pi(q_clear, T["clear"], "ALWAYS")})]
    order = [("mi-topics/n1", s_one, T["one"]), ("mi-topics/n2", q_clear, T["clear"]), ("mi-topics/n3", s_two, T["two"]), ("mi-topics/n4", q_clear, T["clear"]),
             ("mi-recap/n1", q_clear, T["clear"]), ("mi-recap-2/n1", q_clear, T["clear"])]
    runs = [run("One question, four placements, four different answers kept apart: twice in one module, and once in each of two placements of another module",
                {"mi-topics/n2": Y, "mi-topics/n4": N, "mi-recap/n1": N, "mi-recap-2/n1": Y},
                exp(keys, [dv(key, it, text) for key, it, text in order],
                    [("mi-topics", "ACTIVATED", "COMPLETED"), ("mi-recap", "ACTIVATED", "COMPLETED"), ("mi-recap-2", "ACTIVATED", "COMPLETED")], DONE,
                    {"mi-topics/n1": "DELIVERED", "mi-topics/n2": "ANSWERED", "mi-topics/n3": "DELIVERED", "mi-topics/n4": "ANSWERED", "mi-recap/n1": "ANSWERED", "mi-recap-2/n1": "ANSWERED"}))]
    return fixture("K7-one-question-placed-four-times-has-four-execution-identities", "One question placed four times has four execution identities",
                   "The item Q-CLEAR is placed twice in one module and once in a module that is itself placed twice. Each placement is `<instance>/<node>`: "
                   "four planned items, four deliveries, four answers. An answer to one placement is never read as the answer to another.",
                   [q_clear, s_one, s_two], [w(q_clear, T["clear"]), w(s_one, T["one"]), w(s_two, T["two"])], [m1, m2], sv, plans, runs, option_sets=[YES_NO])


def k8():
    """The plan is specific to the application: modules in, out or halting; what an answer decides stays open."""
    s_open = stmt("S-HELLO", "OPENING", "Opens the call")
    q_id = item("Q-IDENTITY", "YES_NO", "Customer confirms they are the policyholder", YES_NO, mandatory=True, role="IDENTITY_CHECK")
    q_hv = item("Q-FUNDS", "YES_NO", "Customer confirms the source of funds", YES_NO)
    s_hv = stmt("S-HIGH-VALUE", "DISCLOSURE", "States the premium that triggered the extra check")
    q_repl = item("Q-REPLACEMENT-COSTS", "YES_NO", "Customer was told the costs of replacing a policy", YES_NO)
    q_sen = item("Q-SENIOR", "ACKNOWLEDGEMENT", "Older customer acknowledges the cooling-off period")
    s_bye = stmt("S-BYE", "CLOSING", "Closes the call")
    T = {"hello": "Good day. This is a service call about your policy.", "id": "Can you confirm that you are the policyholder?",
         "hv": "Because your annual premium is {{policy.annual_premium}}, I have one more question.", "funds": "Can you confirm that the funds for this policy are your own?",
         "repl": "Were you told about the costs of replacing your existing policy?", "sen": "Please confirm that you know you may cancel within fourteen days.",
         "bye": "Thank you. This call is now complete."}
    c_high = {"code": "C-HIGH-PREMIUM", "version": 1, "name": "High premium", "params": {"threshold": {"type": "MONEY", "unit": "SGD"}},
              "ast": {"op": "GTE", "left": {"field": "policy.annual_premium"}, "right": {"param": "threshold"}}}
    c_repl = {"code": "C-REPLACEMENT", "version": 1, "name": "Policy replacement", "params": {}, "ast": {"op": "EQ", "left": {"field": "policy.is_replacement"}, "right": {"literal": True}}}
    c_old = {"code": "C-OLDER", "version": 1, "name": "Older customer", "params": {"minimum_age": {"type": "INTEGER", "unit": "years"}},
             "ast": {"op": "GTE", "left": {"field": "customer.age_years"}, "right": {"param": "minimum_age"}}}
    m_open = mod("M-OPENING", "Opening", ["COMPLETED", "UNABLE_TO_VERIFY"], [nd("n1", s_open), nd("n2", q_id, "PER_CHOICE")],
                 [e("e1", "n1", "AFTER_CAPTURE", node="n2"), e("e2", "n2", "YES", outcome="COMPLETED"), e("e3", "n2", "NO", outcome="UNABLE_TO_VERIFY")])
    m_hv = mod("M-HIGH-VALUE", "High value review", ["COMPLETED", "ESCALATE"], [nd("n1", s_hv), nd("n2", q_hv, "PER_CHOICE")],
               [e("e1", "n1", "AFTER_CAPTURE", node="n2"), e("e2", "n2", "YES", outcome="COMPLETED"), e("e3", "n2", "NO", outcome="ESCALATE")])
    m_repl = mod("M-REPLACEMENT", "Policy replacement", ["COMPLETED"], [nd("n1", q_repl)], [e("e1", "n1", "ANY", outcome="COMPLETED")])
    m_sen = mod("M-SENIOR", "Senior customer", ["COMPLETED"], [nd("n1", q_sen)], [e("e1", "n1", "AFTER_CAPTURE", outcome="COMPLETED")])
    m_bye = mod("M-CLOSING", "Closing", ["COMPLETED"], [nd("n1", s_bye)], [e("e1", "n1", "AFTER_CAPTURE", outcome="COMPLETED")])
    sv = survey("S-APPLICATION", [
        inst("mi-opening", m_open), inst("mi-high-value", m_hv, entry=rule(c_high, "BLOCK", threshold=12000)),
        inst("mi-replacement", m_repl, entry=rule(c_repl, "SKIP_WITH_REASON")), inst("mi-senior", m_sen, entry=rule(c_old, "BLOCK", minimum_age=60)), inst("mi-closing", m_bye)])
    normal = {"policy.annual_premium": 3000, "policy.is_replacement": False, "customer.age_years": 40}
    high = {"policy.annual_premium": 25000, "policy.is_replacement": True, "customer.age_years": 67}
    partial = {"policy.annual_premium": 3000, "policy.is_replacement": None, "customer.age_years": None}
    no_premium = {"policy.annual_premium": None, "policy.is_replacement": False, "customer.age_years": 40}
    P = "PRESENT"
    opening = {"mi-opening/n1": pi(s_open, T["hello"], "ALWAYS"), "mi-opening/n2": pi(q_id, T["id"], "ALWAYS", role="IDENTITY_CHECK", mandatory=True)}
    closing = {"mi-closing/n1": pi(s_bye, T["bye"], "ALWAYS")}
    open_id = {"mi-opening/n2": {"kind": "ANSWER", "alternatives": [{"on": "YES", "to": {"outcome": "COMPLETED"}}, {"on": "NO", "to": {"outcome": "UNABLE_TO_VERIFY"}}]},
               "mi-opening:outcome": {"kind": "OUTCOME", "alternatives": [{"on": "COMPLETED", "to": "@CONTINUE"}, {"on": "UNABLE_TO_VERIFY", "to": {"survey_outcome": "UNABLE_TO_VERIFY"}}]}}
    open_hv = {"mi-high-value/n2": {"kind": "ANSWER", "alternatives": [{"on": "YES", "to": {"outcome": "COMPLETED"}}, {"on": "NO", "to": {"outcome": "ESCALATE"}}]},
               "mi-high-value:outcome": {"kind": "OUTCOME", "alternatives": [{"on": "COMPLETED", "to": "@CONTINUE"}, {"on": "ESCALATE", "to": {"survey_outcome": "ESCALATE"}}]}}
    hv_text = "Because your annual premium is SGD 25,000, I have one more question."
    hv_items = {"mi-high-value/n1": pi(s_hv, hv_text, "ALWAYS", [present("policy.annual_premium", "SGD 25,000")]), "mi-high-value/n2": pi(q_hv, T["funds"], "ALWAYS")}
    plans = [
        planx("An ordinary application: two modules are in, three are out. The identity answer stays open", normal, "READY",
              [("mi-opening", "IN"), ("mi-high-value", "OUT"), ("mi-replacement", "OUT"), ("mi-senior", "OUT"), ("mi-closing", "IN")],
              {**opening, **closing}, opens=open_id, inputs={"policy.annual_premium": P, "policy.is_replacement": P, "customer.age_years": P}),
        planx("A high-premium replacement sale to an older customer: every module is in, and two answers stay open", high, "READY",
              [("mi-opening", "IN"), ("mi-high-value", "IN"), ("mi-replacement", "IN"), ("mi-senior", "IN"), ("mi-closing", "IN")],
              {**opening, **hv_items, "mi-replacement/n1": pi(q_repl, T["repl"], "ALWAYS"), "mi-senior/n1": pi(q_sen, T["sen"], "ALWAYS"), **closing},
              opens={**open_id, **open_hv}, inputs={"policy.annual_premium": P, "policy.is_replacement": P, "customer.age_years": P}),
        planx("Missing data, two policies: the replacement module is skipped with the reason recorded; the senior module HALTS, so the plan is BLOCKED", partial, "BLOCKED",
              [("mi-opening", "IN"), ("mi-high-value", "OUT"), ("mi-replacement", "OUT"), ("mi-senior", "HALTS"), ("mi-closing", "IN")],
              {**opening, "mi-senior/n1": pi(q_sen, T["sen"], "ALWAYS"), **closing}, opens=open_id,
              inputs={"policy.annual_premium": P, "policy.is_replacement": "MISSING", "customer.age_years": "MISSING"}, issues=[{"code": "ELIGIBILITY_UNKNOWN", "at": "mi-senior"}]),
        planx("The premium is missing: whether the high-value review applies cannot be decided, and its own wording cannot be built either", no_premium, "BLOCKED",
              [("mi-opening", "IN"), ("mi-high-value", "HALTS"), ("mi-replacement", "OUT"), ("mi-senior", "OUT"), ("mi-closing", "IN")],
              {**opening, "mi-high-value/n1": {"statement": True, "role": "DISCLOSURE", "mandatory": False, "delivery_mode": "CONTROLLED_TTS", "wording_version": 1, "text": None,
                                               "values": [{"variable": "policy.annual_premium", "value": None, "state": "MISSING"}], "certainty": "ALWAYS"},
               "mi-high-value/n2": pi(q_hv, T["funds"], "ALWAYS"), **closing}, opens={**open_id, **open_hv},
              inputs={"policy.annual_premium": "MISSING", "policy.is_replacement": P, "customer.age_years": P},
              issues=[{"code": "ELIGIBILITY_UNKNOWN", "at": "mi-high-value"}, {"code": "WORDING_VALUE_MISSING", "at": "mi-high-value/n1"}]),
    ]
    d_open = [dv("mi-opening/n1", s_open, T["hello"]), dv("mi-opening/n2", q_id, T["id"])]
    runs = [
        run("The ordinary application, identity confirmed: exactly the two modules the plan put in are run", {"mi-opening/n2": Y},
            exp(["mi-opening/n2"], d_open + [dv("mi-closing/n1", s_bye, T["bye"])],
                [("mi-opening", "ACTIVATED", "COMPLETED"), ("mi-high-value", "SKIPPED_FALSE", None), ("mi-replacement", "SKIPPED_FALSE", None), ("mi-senior", "SKIPPED_FALSE", None), ("mi-closing", "ACTIVATED", "COMPLETED")],
                DONE, {"mi-opening/n1": "DELIVERED", "mi-opening/n2": "ANSWERED", "mi-closing/n1": "DELIVERED"}), facts=normal),
        run("The same plan, the other answer at the open point: the call ends there. The plan was right to leave it open", {"mi-opening/n2": N},
            exp(["mi-opening/n2"], d_open,
                [("mi-opening", "ACTIVATED", "UNABLE_TO_VERIFY"), ("mi-high-value", "NOT_REACHED", None), ("mi-replacement", "NOT_REACHED", None), ("mi-senior", "NOT_REACHED", None), ("mi-closing", "NOT_REACHED", None)],
                {"state": "ENDED_WITH_OUTCOME", "survey_outcome": "UNABLE_TO_VERIFY"}, {"mi-opening/n1": "DELIVERED", "mi-opening/n2": "ANSWERED"}), facts=normal),
        run("The high-premium application: every module runs, and the disclosure carries this customer's premium",
            {"mi-opening/n2": Y, "mi-high-value/n2": Y, "mi-replacement/n1": Y, "mi-senior/n1": {"acknowledged": True}},
            exp(["mi-opening/n2", "mi-high-value/n2", "mi-replacement/n1", "mi-senior/n1"],
                d_open + [dv("mi-high-value/n1", s_hv, hv_text, [present("policy.annual_premium", "SGD 25,000")]), dv("mi-high-value/n2", q_hv, T["funds"]),
                          dv("mi-replacement/n1", q_repl, T["repl"]), dv("mi-senior/n1", q_sen, T["sen"]), dv("mi-closing/n1", s_bye, T["bye"])],
                [(n, "ACTIVATED", "COMPLETED") for n in ["mi-opening", "mi-high-value", "mi-replacement", "mi-senior", "mi-closing"]], DONE,
                {"mi-opening/n1": "DELIVERED", "mi-opening/n2": "ANSWERED", "mi-high-value/n1": "DELIVERED", "mi-high-value/n2": "ANSWERED",
                 "mi-replacement/n1": "ANSWERED", "mi-senior/n1": "ANSWERED", "mi-closing/n1": "DELIVERED"}), facts=high),
        run("Missing data: the call runs as far as the module that cannot be decided, and halts there, as the plan said it would", {"mi-opening/n2": Y},
            exp(["mi-opening/n2"], d_open,
                [("mi-opening", "ACTIVATED", "COMPLETED"), ("mi-high-value", "SKIPPED_FALSE", None), ("mi-replacement", "SKIPPED_UNKNOWN", None), ("mi-senior", "HALTED_MISSING_INFORMATION", None), ("mi-closing", "NOT_REACHED", None)],
                {"state": "MISSING_INFORMATION_HALT", "reason": "ELIGIBILITY_UNKNOWN", "at": "mi-senior"}, {"mi-opening/n1": "DELIVERED", "mi-opening/n2": "ANSWERED"}), facts=partial),
    ]
    its = [s_open, q_id, s_hv, q_hv, q_repl, q_sen, s_bye]
    texts = [T["hello"], T["id"], T["hv"], T["funds"], T["repl"], T["sen"], T["bye"]]
    return fixture("K8-the-call-plan-is-specific-to-the-application", "The call plan is specific to the application",
                   "Five modules, three with eligibility conditions on application data. Four applications give four plans from one survey: modules "
                   "IN, OUT (does not apply, or cannot be decided and the survey says skip) or HALTS (cannot be decided and the survey says stop). What "
                   "an answer will decide stays OPEN in every plan, with its alternatives. Each run delivers exactly what its plan settled.",
                   its, [w(i, t) for i, t in zip(its, texts)], [m_open, m_hv, m_repl, m_sen, m_bye], sv, plans, runs,
                   conditions=[c_high, c_repl, c_old], option_sets=[YES_NO], fields=["policy.annual_premium", "policy.is_replacement", "customer.age_years"])


if __name__ == "__main__":
    out = sys.argv[1]
    plans = runs = 0
    built = [f() for f in (k1, k2, k3, k4, k5, k6, k7, k8)]
    for fx in built:
        p, r = check(fx)
        plans, runs = plans + p, runs + r
        with open(f"{out}/{fx['fixture']}.json", "w") as fh:
            json.dump(fx, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        print(f"OK {fx['fixture']}: {r} run(s), {p} plan(s), {len(fx['validation']['errors'])} expected validation error(s) verified")
    print(f"ALL OK: {len(built)} fixtures (schema /5), {runs} expected runs, {plans} expected plans")
