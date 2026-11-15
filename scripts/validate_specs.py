#!/usr/bin/env python3
"""Self-contained Call360 0.3 specification/register consistency checker."""
from __future__ import annotations
import csv
import json
import re
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
