# -*- coding: utf-8 -*-
"""
validate_harness.py — schema + gate validator for workplace-safety-drill-evaluator.

Validates the JSON payloads emitted by each harness stage against the documented
schemas (see skills/*.md) and runs the cross-stage quality-gate checks. Used by the
test harness and CI to detect regressions in skill output.

Usage:
    python tools/validate_harness.py path/to/payload.json
    python tools/validate_harness.py stage1.json stage2.json ...   # chained check
    cat payload.json | python tools/validate_harness.py -
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

DIMENSIONS = {
    "regulatory_compliance", "response_time", "communication",
    "evacuation_effectiveness", "gap_closure",
}

REQUIRED = {
    "sub-stakeholder-mapper": {
        "schema_version": str, "stage": str, "request_summary": str,
        "facility": dict, "drill": dict, "roles": list,
        "missing_roles": list, "assumptions": list, "confidence": str,
        "frameworks_applied": list,
    },
    "sub-requirements-gatherer": {
        "schema_version": str, "stage": str, "inherited_from": str,
        "hazards": list, "jurisdiction": str, "frameworks": list,
        "requirements": list, "scoring_weights": dict,
        "assumptions": list, "confidence": str, "limitations": list,
    },
    "sub-scoring-engine": {
        "schema_version": str, "stage": str, "inherited_from": str,
        "evidence_sources": list, "scores": list, "composite_index": (int, float),
        "top_findings": dict, "roadmap": list,
        "assumptions": list, "confidence": str, "limitations": list,
    },
    "sub-quality-reviewer": {
        "schema_version": str, "stage": str, "inherited_from": str,
        "revisions": list, "attacks": list, "gate_checklist": dict,
        "final_scores": list, "final_composite_index": (int, float),
        "final_roadmap": list, "evidence_sources": list,
        "assumptions": list, "confidence": str, "limitations": list,
    },
}


class ValidationError(Exception):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise ValidationError(msg)


def _is_str_list(x: Any) -> bool:
    return isinstance(x, list) and all(isinstance(i, str) for i in x)


def validate_required_keys(payload: dict, stage: str) -> list[str]:
    errs = []
    schema = REQUIRED[stage]
    for k, typ in schema.items():
        if k not in payload:
            errs.append(f"{stage}: missing required key '{k}'")
            continue
        if isinstance(typ, tuple):
            if not isinstance(payload[k], typ):
                errs.append(f"{stage}: '{k}' must be one of {typ}, got {type(payload[k]).__name__}")
        elif not isinstance(payload[k], typ):
            errs.append(f"{stage}: '{k}' must be {typ.__name__}, got {type(payload[k]).__name__}")
    return errs


def validate_stakeholder_mapper(p: dict) -> list[str]:
    errs = validate_required_keys(p, "sub-stakeholder-mapper")
    if not p.get("roles"):
        errs.append("sub-stakeholder-mapper: 'roles' must be non-empty")
    for r in p.get("roles", []):
        for k in ("name", "role_type", "responsibilities", "raci_phases", "framework_ref"):
            if k not in r:
                errs.append(f"sub-stakeholder-mapper: role missing '{k}'")
        if "present_in_drill" not in r:
            errs.append("sub-stakeholder-mapper: role missing 'present_in_drill'")
    if p.get("confidence") not in {"high", "medium", "low"}:
        errs.append("sub-stakeholder-mapper: 'confidence' must be high|medium|low")
    return errs


def validate_requirements_gatherer(p: dict) -> list[str]:
    errs = validate_required_keys(p, "sub-requirements-gatherer")
    fw = p.get("frameworks", [])
    if not fw:
        errs.append("sub-requirements-gatherer: 'frameworks' must be non-empty")
    for f in fw:
        if not all(f.get(k) for k in ("name", "justification", "citation")):
            errs.append("sub-requirements-gatherer: framework entry missing name/justification/citation")
    reqs = p.get("requirements", [])
    dims_present = {r.get("dimension") for r in reqs if isinstance(r, dict)}
    missing = DIMENSIONS - dims_present
    if missing:
        errs.append(f"sub-requirements-gatherer: requirements missing dimensions {sorted(missing)}")
    w = p.get("scoring_weights", {})
    if set(w) != DIMENSIONS:
        errs.append(f"sub-requirements-gatherer: scoring_weights keys must be {sorted(DIMENSIONS)}")
    else:
        total = sum(float(v) for v in w.values())
        if abs(total - 1.0) > 0.001:
            errs.append(f"sub-requirements-gatherer: scoring_weights sum to {total}, must be 1.0")
    if p.get("confidence") not in {"high", "medium", "low"}:
        errs.append("sub-requirements-gatherer: 'confidence' must be high|medium|low")
    return errs


def validate_scoring_engine(p: dict) -> list[str]:
    errs = validate_required_keys(p, "sub-scoring-engine")
    scores = p.get("scores", [])
    dims = [s.get("dimension") for s in scores]
    if len(scores) != 5 or set(dims) != DIMENSIONS:
        errs.append(f"sub-scoring-engine: scores must cover all 5 dimensions exactly once, got {dims}")
    for s in scores:
        if not all(s.get(k) for k in ("score", "justification", "citation")):
            errs.append("sub-scoring-engine: score entry missing score/justification/citation")
        try:
            v = float(s.get("score"))
            if not 0 <= v <= 100:
                errs.append(f"sub-scoring-engine: score {v} out of 0-100 for {s.get('dimension')}")
        except (TypeError, ValueError):
            errs.append(f"sub-scoring-engine: score not numeric for {s.get('dimension')}")
    rm = p.get("roadmap", [])
    if not rm:
        errs.append("sub-scoring-engine: 'roadmap' must be non-empty")
    for item in rm:
        for k in ("action", "effort", "impact", "owner", "expected_effect", "rationale"):
            if not item.get(k):
                errs.append(f"sub-scoring-engine: roadmap item missing '{k}'")
    if p.get("confidence") not in {"high", "medium", "low"}:
        errs.append("sub-scoring-engine: 'confidence' must be high|medium|low")
    if not _is_str_list(p.get("limitations", [])):
        errs.append("sub-scoring-engine: 'limitations' must be a list of strings")
    return errs


def validate_quality_reviewer(p: dict) -> list[str]:
    errs = validate_required_keys(p, "sub-quality-reviewer")
    gc = p.get("gate_checklist", {})
    for k in ("framework_selection_justified", "every_score_cited",
             "roadmap_has_effort_impact_rationale", "assumptions_confidence_limitations_stated",
             "devils_advocate_completed"):
        if gc.get(k) not in {"pass", "fail"}:
            errs.append(f"sub-quality-reviewer: gate_checklist[{k}] must be pass|fail")
        elif gc.get(k) == "fail":
            errs.append(f"sub-quality-reviewer: gate '{k}' FAILED")
    attacks = p.get("attacks", [])
    if len(attacks) < 3:
        errs.append(f"sub-quality-reviewer: must produce >=3 attacks, got {len(attacks)}")
    for a in attacks:
        if a.get("resolution") not in {"rebutted", "revised"}:
            errs.append("sub-quality-reviewer: attack resolution must be rebutted|revised")
    ci = p.get("final_composite_index")
    try:
        if not (0 <= float(ci) <= 100):
            errs.append("sub-quality-reviewer: final_composite_index out of 0-100")
    except (TypeError, ValueError):
        errs.append("sub-quality-reviewer: final_composite_index not numeric")
    return errs


VALIDATORS = {
    "sub-stakeholder-mapper": validate_stakeholder_mapper,
    "sub-requirements-gatherer": validate_requirements_gatherer,
    "sub-scoring-engine": validate_scoring_engine,
    "sub-quality-reviewer": validate_quality_reviewer,
}


def validate_payload(payload: dict) -> list[str]:
    stage = payload.get("stage")
    if stage not in VALIDATORS:
        return [f"unknown or missing stage: {stage!r}"]
    return VALIDATORS[stage](payload)


def _load(path: str) -> dict:
    if path == "-":
        return json.load(sys.stdin)
    # utf-8-sig tolerates optional BOM written by some editors/PowerShell encodings.
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Validate harness stage payloads.")
    ap.add_argument("paths", nargs="+", help="payload JSON file(s) or '-' for stdin")
    args = ap.parse_args(argv)

    all_errs: list[str] = []
    for path in args.paths:
        try:
            payload = _load(path)
        except Exception as e:
            all_errs.append(f"{path}: cannot load JSON: {e}")
            continue
        errs = validate_payload(payload)
        for e in errs:
            all_errs.append(f"{path}: {e}")

    if all_errs:
        for e in all_errs:
            print(f"FAIL: {e}", file=sys.stderr)
        return 1
    print("OK: all payloads valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
