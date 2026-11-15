#!/usr/bin/env python3
"""Self-contained Call360 specification/register consistency checker.

Part 1 is the original v0.3 baseline check (unchanged). Part 2 adds the CP0.0
specification-foundation checks: unchanged source baselines, exception-aware
terminology, S0 traceability, catalogue/route/ADR/security consistency.
Standard library only; no runtime secrets.
"""
from __future__ import annotations
import csv
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRD = (ROOT / "docs/spec/01_MASTER_BRD.md").read_text(encoding="utf-8")
PLAN = (ROOT / "docs/spec/02_CLAUDE_CODE_EXECUTION_PLAN.md").read_text(encoding="utf-8")
COUNTS = json.loads((ROOT / "docs/spec/REQUIREMENT_COUNTS.json").read_text(encoding="utf-8"))
with (ROOT / "docs/spec/03_REQUIREMENTS_REGISTER.csv").open(encoding="utf-8-sig", newline="") as fh:
    rows = list(csv.DictReader(fh))
ids = [r["requirement_id"] for r in rows]
assert len(rows) == 237 == COUNTS["total_count"], "Expected 237 requirements"
assert len(set(ids)) == len(ids), "Duplicate requirement IDs"
assert COUNTS["baseline_count"] == 99 and COUNTS["new_count"] == 138
assert all(re.fullmatch(r"[A-Z]+-\d{3}", x) for x in ids)
assert sum(Counter(x.split("-")[0] for x in ids)[k] for k in COUNTS["categories"]) == 138
for r in rows:
    rid = r["requirement_id"]
    assert re.search(r"\|\s*" + re.escape(rid) + r"\s*\|", BRD), f"Missing BRD {rid}"
    assert r["stage"] in {f"S{i}" for i in range(7)}, rid
    assert r["implementing_repositories"], f"No repo owner: {rid}"
    assert r["acceptance_evidence"] == f"docs/acceptance/{r['stage']}.md", rid
scenario_ids = re.findall(r"^\| (T-\d{2}) \|", BRD, flags=re.M)
assert len(scenario_ids) == 55 and len(set(scenario_ids)) == 55, "Expected 55 distinct business tests"
assert "# Call360" in BRD and "Call Detail" in BRD and "Call Detail" in PLAN
assert "v0.3 staging overlay" in PLAN
for n in ["Call360-specs", "Call360-backend", "Call360-frontend"]:
    assert n in BRD and n in PLAN
for key in ["SBQ", "SaleEvent", "script", "risk", "Okta", "manual", "token"]:
    assert key.lower() in BRD.lower(), key
print(f"PASS: {len(ids)} requirements, {len(scenario_ids)} tests, staged three-repo Call360 v0.3 pack")

# ---------------------------------------------------------------------------
# Part 2 — CP0.0 specification-foundation checks
# ---------------------------------------------------------------------------

# Frozen baselines. Change only together with an approved, reviewed requirement change.
BASELINE_SHA256 = {
    "docs/spec/01_MASTER_BRD.md": "8b1b0cd72e311b5091704775d1c6b6053d83863c67a44bb29ebc8e0d04a4c004",
    "docs/spec/03_REQUIREMENTS_REGISTER.csv": "0815fdad6ef8e27ce033a2e59c28f2bc33972b9230737ec3a6868353469bb495",
    "docs/spec/REQUIREMENT_COUNTS.json": "887893e2b6127baa619a78906394b3ec547635fef7b55052487058d850871887",
}
BASELINE_ID_SET_SHA256 = "6cd7a348d628ed756694bd507f32e514a3a42262fa37ba00aa1848549251dd07"
PROHIBITED_TERMS = ["Survey Studio", "Call 360", "GET /surveys", "/api/v1/surveys", "VALIDATION_FAILED/VALIDATED"]
SCANNED_SUFFIXES = {".md", ".csv", ".json"}
TEST_ID_RE = re.compile(r"\b(BE-[A-Z]+-\d{2}|FE-\d{2}|E2E-\d{2}|SCAN-\d{2}|DOC-\d{2}|SPEC-\d{2})\b")
CP_RE = r"CP0\.(1A|1B|[2-6])"  # implementation checkpoints (CP0.1 split per D-21)
SPECIAL_PERMISSIONS = {"PUBLIC", "AUTHENTICATED", "AUTHENTICATED (LOCAL)", "SERVICE_TOKEN", "PUBLIC (refresh cookie)"}

errors: list[str] = []
passed: list[str] = []


def doc(rel: str) -> str:
    path = ROOT / rel
    if not path.exists():
        errors.append(f"missing document: {rel}")
        return ""
    return path.read_text(encoding="utf-8")


def table_rows(text: str, first_cell: str) -> list[list[str]]:
    """Markdown table rows whose first cell matches the regex `first_cell`."""
    out = []
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]
        if cells and re.fullmatch(first_cell, cells[0]):
            out.append(cells)
    return out


def section(text: str, heading_prefix: str) -> str:
    """Text from a heading starting with `heading_prefix` up to the next heading of same or higher level."""
    lines = text.splitlines()
    start = None
    level = 0
    for i, line in enumerate(lines):
        m = re.match(r"^(#+)\s+(.*)", line)
        if m and start is None and m.group(2).startswith(heading_prefix):
            start, level = i, len(m.group(1))
            continue
        if m and start is not None and len(m.group(1)) <= level:
            return "\n".join(lines[start:i])
    return "\n".join(lines[start:]) if start is not None else ""


def check(name: str, ok: bool, detail: str = "") -> None:
    if ok:
        passed.append(name)
    else:
        errors.append(f"{name}: {detail}")


def scanned_files() -> list[Path]:
    files = []
    for p in ROOT.rglob("*"):
        rel = p.relative_to(ROOT).as_posix()
        if not p.is_file() or rel.startswith(".git/") or rel.startswith("docs/acceptance/evidence/"):
            continue
        if p.suffix in SCANNED_SUFFIXES:
            files.append(p)
    return files


# 1. Unchanged source baselines (BRD, register, counts) and requirement ID set.
for rel, digest in BASELINE_SHA256.items():
    actual = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
    check(f"baseline unchanged {rel}", actual == digest, f"sha256 {actual} != frozen {digest}")
id_digest = hashlib.sha256("\n".join(sorted(ids)).encode()).hexdigest()
check("requirement ID set equals 237-ID baseline", id_digest == BASELINE_ID_SET_SHA256, id_digest)

# 2. Exception-aware terminology.
exc_text = doc("docs/spec/APPROVED_EXCEPTIONS.md")
exc_ids = {r[0] for r in table_rows(exc_text, r"EXC-\d{3}")}
allow: dict[str, set[str]] = {t: set() for t in PROHIBITED_TERMS}
for r in table_rows(exc_text, r"`[^`]+`"):
    if len(r) < 4:
        continue
    term, rel, kind, basis = r[0].strip("`"), r[1], r[2], r[3]
    if term not in allow:
        errors.append(f"exceptions register: unknown term {term!r}")
        continue
    if kind not in {"EXCEPTION", "REFERENCE"}:
        errors.append(f"exceptions register: bad kind {kind!r} for {term} in {rel}")
    if kind == "EXCEPTION" and basis not in exc_ids:
        errors.append(f"exceptions register: EXCEPTION row {term} / {rel} cites undefined {basis!r}")
    if not (ROOT / rel).exists():
        errors.append(f"exceptions register: file not found {rel}")
    allow[term].add(rel)
term_violations, stale = [], []
contents = {p.relative_to(ROOT).as_posix(): p.read_text(encoding="utf-8", errors="replace") for p in scanned_files()}
for term in PROHIBITED_TERMS:
    for rel, text in contents.items():
        if rel == "docs/spec/APPROVED_EXCEPTIONS.md":
            continue
        if term in text and rel not in allow[term]:
            term_violations.append(f"{term!r} in {rel}")
    for rel in allow[term]:
        if rel in contents and term not in contents[rel]:
            stale.append(f"{term!r} allowlisted for {rel} but absent")
check("terminology: prohibited terms only in approved files", not term_violations, "; ".join(term_violations))
check("terminology: no stale allowlist rows", not stale, "; ".join(stale))

# 3. S0 requirement-to-test matrix.
matrix = doc("docs/acceptance/S0_TEST_MATRIX.md")
reg_s0 = {r["requirement_id"]: r for r in rows if r["stage"] == "S0"}
mrows = {r[0]: r for r in table_rows(section(matrix, "1. Requirement matrix"), r"[A-Z]+-\d{3}")}
check("S0 matrix covers exactly the S0 register rows", set(mrows) == set(reg_s0),
      f"missing {sorted(set(reg_s0) - set(mrows))}, extra {sorted(set(mrows) - set(reg_s0))}")
catalogue = {r[0] for r in table_rows(section(matrix, "2. Test catalogue"), TEST_ID_RE.pattern.replace(r"\b", ""))}
class_count = Counter()
for rid, r in mrows.items():
    if len(r) < 6:
        errors.append(f"S0 matrix row {rid} malformed")
        continue
    pri, cls, cp, tests = r[1], r[2], r[4], r[5]
    class_count[cls] += 1
    if rid in reg_s0 and pri != reg_s0[rid]["priority"]:
        errors.append(f"S0 matrix {rid} priority {pri} != register {reg_s0[rid]['priority']}")
    if cls not in {"F", "P", "D"}:
        errors.append(f"S0 matrix {rid} bad class {cls}")
    if not re.search(r"CP0\.[0-6]", cp):
        errors.append(f"S0 matrix {rid} has no checkpoint")
    tids = TEST_ID_RE.findall(tests)
    if not tids:
        errors.append(f"S0 matrix {rid} has no test ID")
    for t in tids:
        if t not in catalogue:
            errors.append(f"S0 matrix {rid} references undefined test {t}")
totals = re.search(r"\*\*F: (\d+)\*\*.*?\*\*P: (\d+)\*\*.*?\*\*D: (\d+)\*\*", matrix, flags=re.S)
check("S0 matrix totals match rows", bool(totals) and (int(totals.group(1)), int(totals.group(2)), int(totals.group(3)))
      == (class_count["F"], class_count["P"], class_count["D"]), f"rows give {dict(class_count)}")
check("S0 matrix test catalogue non-empty", len(catalogue) > 50, f"{len(catalogue)} tests")

# 4. Every test ID referenced by CP0.0 documents is defined.
TRACE_DOCS = [
    "docs/security/THREAT_MODEL_S0.md", "docs/security/ASVS_S0_CONTROL_MATRIX.md",
    "docs/product/S0_KPI_DEFINITIONS.md", "docs/data/S0_DATA_MODEL.md",
    "docs/plans/S0_IMPLEMENTATION_PLAN.md", "docs/acceptance/S0_TEST_MATRIX.md",
]
undefined = sorted({f"{t} ({rel})" for rel in TRACE_DOCS for t in TEST_ID_RE.findall(doc(rel)) if t not in catalogue})
check("all referenced test IDs defined in catalogue", not undefined, ", ".join(undefined))

# 5. Threat model: each threat has a defined test or residual risk.
tm = doc("docs/security/THREAT_MODEL_S0.md")
rr_defined = {r[0] for r in table_rows(tm, r"RR-\d{2}")}
tm_bad = []
for r in table_rows(tm, r"TM-\d{2}"):
    verification = r[-1]
    rrs = re.findall(r"RR-\d{2}", verification)
    if not TEST_ID_RE.findall(verification) and not rrs:
        tm_bad.append(r[0])
    tm_bad += [f"{r[0]}→{x}" for x in rrs if x not in rr_defined]
check("threat model traceability", bool(table_rows(tm, r"TM-\d{2}")) and not tm_bad, ", ".join(tm_bad))
asvs = doc("docs/security/ASVS_S0_CONTROL_MATRIX.md")
asvs_bad = [r[0] for r in table_rows(asvs, r"V\d+ .*")
            if not TEST_ID_RE.findall(r[3]) and "Not applicable" not in r[1]]
check("ASVS matrix traceability", bool(table_rows(asvs, r"V\d+ .*")) and not asvs_bad, ", ".join(asvs_bad))

# 6. Data model: every catalogued table maps to the grain doc or is justified NEW.
dm = doc("docs/data/S0_DATA_MODEL.md")
grain = doc("docs/data/CANONICAL_GRAIN_AND_RELATIONSHIPS.md")
dm_bad = []
dm_tables = table_rows(section(dm, "4. Table catalogue"), r"`[a-z_]+`")
for r in dm_tables:
    mapping = r[2] if len(r) > 2 else ""
    if mapping.startswith("NEW:"):
        continue
    names = [n.split(".")[0] for n in re.findall(r"`([a-z_.]+)`", mapping)]
    if not names or not any(f"`{n}`" in grain for n in names):
        dm_bad.append(r[0])
check("data model tables mapped to grain doc", len(dm_tables) >= 50 and not dm_bad, f"{len(dm_tables)} tables; unmapped {dm_bad}")
check("data model script lifecycle equals approved list",
      "`DRAFT`, `SUBMITTED_FOR_REVIEW`, `APPROVED`, `SCHEDULED`, `PUBLISHED`, `SUPERSEDED`, `WITHDRAWN`" in dm, "enum mismatch")

# 6b. Physical build scope (D-19): Build column per table; 59 built in S0; named deferrals.
build = {r[0].strip("`"): r[-1] for r in dm_tables}
built_s0 = [t for t, b in build.items() if re.fullmatch(CP_RE, b)]
deferred = {t: b for t, b in build.items() if "not built in S0" in b}
check("data model Build column on every table", all(re.fullmatch(CP_RE, b) or "not built in S0" in b for b in build.values()),
      str({t: b for t, b in build.items() if not (re.fullmatch(CP_RE, b) or "not built in S0" in b)}))
check("Stage 0 builds exactly 59 tables", len(build) == 63 and len(built_s0) == 59, f"{len(build)} tables, {len(built_s0)} built")
check("deferred tables are the approved four", set(deferred) == {"transcript_segment", "media_asset", "risk_override", "review_decision"}, str(deferred))
plan_txt = doc("docs/plans/S0_IMPLEMENTATION_PLAN.md")
for cp, n in Counter(build[t] for t in built_s0).items():
    check(f"plan table count matches data model for {cp}", f"the {n} tables with Build = {cp}" in plan_txt or n < 5, f"{cp}: {n}")

# 6c. CP0.1A / CP0.1B allocation consistent across documents (D-21, D-22).
cp1a_tables = sorted(t for t, b in build.items() if b == "CP0.1A")
cp1b_tables = sorted(t for t, b in build.items() if b == "CP0.1B")
check("CP0.1A builds 15 tables, CP0.1B builds 6", (len(cp1a_tables), len(cp1b_tables)) == (15, 6), f"{len(cp1a_tables)}/{len(cp1b_tables)}")
cp1a_doc = doc("docs/acceptance/CP0.1A.md")
check("CP0.1A checklist lists exactly the CP0.1A tables",
      set(re.findall(r"`([a-z_]+)`", re.search(r"\| Tables \(15\) \|([^\n]*)", cp1a_doc).group(1))) == set(cp1a_tables) if "| Tables (15) |" in cp1a_doc else False,
      "table list mismatch")
check("no table still allocated to undivided CP0.1", "CP0.1" not in [b for b in build.values()], "found CP0.1")
iam_doc = doc("docs/security/S0_IDENTITY_ACCESS_DESIGN.md")
for token in ["call360_test_user", "`call360_test`", "has_schema_privilege", "REFRESH_REUSE_GRACE_SECONDS", "Web Locks"]:
    check(f"identity design specifies {token}", token in iam_doc, "missing")

# 7. API catalogue: permission + checkpoint per endpoint; permissions exist in the matrix.
api = doc("docs/contracts/S0_API_CATALOGUE.md")
iam = doc("docs/security/S0_IDENTITY_ACCESS_DESIGN.md")
perm_defined = set()
for r in table_rows(section(iam, "6. Permission catalogue"), r"`[a-z_.]+`.*"):
    perm_defined.update(re.findall(r"`([a-z_.]+)`", r[0]))
api_rows = table_rows(api, r"API-\d{3}")
api_ids = [r[0] for r in api_rows]
api_bad = []
for r in api_rows:
    if len(r) < 8:
        api_bad.append(f"{r[0]} malformed")
        continue
    perm, cp = r[3].strip("`"), r[7]
    if perm not in SPECIAL_PERMISSIONS and perm not in perm_defined:
        api_bad.append(f"{r[0]} permission {perm!r} not in matrix")
    if not re.fullmatch(CP_RE, cp):
        api_bad.append(f"{r[0]} checkpoint {cp!r}")
check("API catalogue rows complete", len(api_rows) > 60 and len(set(api_ids)) == len(api_ids) and not api_bad,
      "; ".join(api_bad) or "duplicate IDs")
reserved_in_admin = [p for p in ["script.approve", "risk.override.approve", "recording.read", "evidence.export", "pii.unmasked"]
                     if re.search(r"`" + re.escape(p) + r"`[^\n]*\|\s*✓", iam)]
check("ADMIN lacks reserved permissions in matrix", not reserved_in_admin, ", ".join(reserved_in_admin))

cp1a_api = sorted(r[0] for r in api_rows if len(r) >= 8 and r[7] == "CP0.1A")
check("CP0.1A implements 10 endpoints, matching the checklist",
      len(cp1a_api) == 10 and all(a in cp1a_doc for a in cp1a_api), str(cp1a_api))
check("no endpoint still allocated to undivided CP0.1", not [r[0] for r in api_rows if len(r) >= 8 and r[7] == "CP0.1"], "found CP0.1")

# 8. Route parity: screen spec route table == SCREEN_NAMING route table.
spec = doc("docs/product/S0_SCREEN_SPEC.md")
naming = doc("docs/product/SCREEN_NAMING_AND_ROUTES.md")
def routes(text: str, heading: str) -> set[str]:
    return {re.findall(r"`([^`]+)`", r[1])[0] for r in table_rows(section(text, heading), r"[^|-].*")
            if len(r) > 1 and r[1].startswith("`/")}
spec_routes = routes(spec, "2. Route and screen table")
naming_routes = routes(naming, "Canonical React routes")
check("route parity screen spec vs SCREEN_NAMING", spec_routes and spec_routes == naming_routes,
      f"only spec {sorted(spec_routes - naming_routes)}, only naming {sorted(naming_routes - spec_routes)}")
missing_api = sorted({a for a in re.findall(r"API-\d{3}", spec) if a not in api_ids})
check("screen spec API references exist", not missing_api, ", ".join(missing_api))

# 9. ADR index equals ADR files; referenced ADRs exist.
adr_files = {p.name for p in (ROOT / "docs/adr").glob("ADR-*.md")}
adr_index = set(re.findall(r"\]\((ADR-[^)]+\.md)\)", doc("docs/adr/README.md")))
check("ADR index matches files", adr_files == adr_index, f"files {sorted(adr_files ^ adr_index)}")
adr_nums = {f.split("-")[0] + "-" + f.split("-")[1] for f in adr_files}
missing_adr = sorted({m for t in contents.values() for m in re.findall(r"ADR-\d{4}", t) if m not in adr_nums})
check("referenced ADRs exist", not missing_adr, ", ".join(missing_adr))

# 10. Contradiction register complete and summary consistent.
cp00 = doc("docs/acceptance/CP0.0.md")
crow = table_rows(section(cp00, "2. Contradiction register"), r"C-\d+")
cnums = [int(r[0][2:]) for r in crow]
allowed = {"RESOLVED-OWNER", "RESOLVED-ENG", "DEFERRED", "MOOT"}
statuses = Counter()
c_bad = []
for r in crow:
    st = r[-1]
    key = next((a for a in allowed if st.startswith(a)), None)
    if not key:
        c_bad.append(f"{r[0]} status {st!r}")
        continue
    statuses[key] += 1
    if key == "DEFERRED" and "owner" not in st.lower():
        c_bad.append(f"{r[0]} DEFERRED without owner")
check("contradiction register contiguous and classified", cnums == list(range(1, len(cnums) + 1)) and len(cnums) >= 27 and not c_bad,
      "; ".join(c_bad) or f"numbers {cnums}")
summ = re.search(r"RESOLVED-OWNER (\d+) · RESOLVED-ENG (\d+) · DEFERRED (\d+).*?MOOT (\d+)", cp00)
check("contradiction summary matches rows", bool(summ) and tuple(map(int, summ.groups())) ==
      (statuses["RESOLVED-OWNER"], statuses["RESOLVED-ENG"], statuses["DEFERRED"], statuses["MOOT"]), f"rows give {dict(statuses)}")
acs = re.findall(r"^\| (AC-0\.0-\d{2}) \|", cp00, flags=re.M)
check("CP0.0 acceptance criteria AC-0.0-01..12 present", acs == [f"AC-0.0-{i:02d}" for i in range(1, 13)], str(acs))

# 11. KPI catalogue covers every BRD §10 KPI.
kpi = doc("docs/product/S0_KPI_DEFINITIONS.md")
brd_kpis = [r[0] for r in table_rows(section(BRD, "10. Reference KPIs"), r"[A-Z][A-Za-z ]+") if r[0] != "KPI"]
kpi_rows = table_rows(kpi, r"KPI-\d{2}")
kpi_names = {r[1] for r in kpi_rows}
missing_kpi = [k for k in brd_kpis if k not in kpi_names]
check("KPI catalogue covers BRD §10", len(brd_kpis) == 12 and not missing_kpi, f"missing {missing_kpi}")
kpi_incomplete = [r[0] for r in kpi_rows if len(r) < 7 or any(c == "" for c in r[:7])]
check("KPI rows complete", not kpi_incomplete, ", ".join(kpi_incomplete))
for rule in ["Held cases (K-1)", "Cancelled cases (K-1, K-3)", "SLA exemptions (K-3)", "Materiality (K-2)", "Cohort basis (K-4)"]:
    check(f"KPI rule present: {rule}", rule in kpi, "missing")

# 11b. Outcome model and SLA exemption (D-17, D-18).
for token in ["VERIFIED_COMPLIANT", "VERIFIED_WITH_FINDINGS", "NOT_VERIFIED", "`CANCELLED`", "`OPEN`", "VERIFIED_CONTROL_EVIDENCE_INCOMPLETE",
              "SLA-EX-001", "sla_exempt_eligible", "cancellation_authorized_by", "cancelled_recorded_at", "do not pause the SLA clock"]:
    check(f"KPI outcome/SLA rule present: {token}", token in kpi, "missing")
check("data model has cancellation authorisation fields", all(f in dm for f in ["cancellation_reason", "cancelled_recorded_at", "cancellation_authorized_by", "cancellation_authorization_ref"]), "missing")
check("ASVS matrix states plan-not-certification", "not evidence of completed security certification" in asvs, "missing statement")

# 12. Relative Markdown links resolve.
broken = []
for rel, text in contents.items():
    if not rel.endswith(".md"):
        continue
    for target in re.findall(r"\]\(([^)#\s]+)(?:#[^)]*)?\)", text):
        if re.match(r"[a-z]+:", target):
            continue
        if not (ROOT / rel).parent.joinpath(target).resolve().exists():
            broken.append(f"{rel} → {target}")
check("relative Markdown links resolve", not broken, "; ".join(broken))

if errors:
    print(f"FAIL: {len(errors)} CP0.0 check(s) failed ({len(passed)} passed)")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
print(f"PASS: {len(passed)} CP0.0 specification checks "
      f"(S0 matrix {len(mrows)} requirements, {len(catalogue)} tests; {len(api_rows)} endpoints; "
      f"{len(dm_tables)} tables; {len(spec_routes)} routes; {len(crow)} contradictions; {len(adr_files)} ADRs)")
