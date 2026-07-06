# -*- coding: utf-8 -*-
"""Tests for tools/validate_harness.py — schema + gate validation.

Run:  python -m pytest tests/test_validate_harness.py -q
"""
import os
import sys
import json
import subprocess

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
FIX = os.path.join(HERE, "fixtures")

VALIDATOR = os.path.join(TOOLS, "validate_harness.py")


def _run(files):
    proc = subprocess.run([sys.executable, VALIDATOR] + files,
                          capture_output=True, text=True, cwd=ROOT)
    return proc.returncode, proc.stdout, proc.stderr


def _load_fixture(name):
    with open(os.path.join(FIX, name), "r", encoding="utf-8-sig") as f:
        return json.load(f)


def test_valid_stage_fixtures_pass():
    files = [
        os.path.join(FIX, "stage1_stakeholder_mapper.json"),
        os.path.join(FIX, "stage2_requirements_gatherer.json"),
        os.path.join(FIX, "stage3_scoring_engine.json"),
        os.path.join(FIX, "stage4_quality_reviewer.json"),
    ]
    for f in files:
        rc, out, err = _run([f])
        assert rc == 0, f"{f} should be valid:\n{err}"


def test_missing_dimension_fails(tmp_path):
    bad = {
        "schema_version": "1.0", "stage": "sub-scoring-engine", "inherited_from": "x",
        "evidence_sources": [], "scores": [
            {"dimension": "regulatory_compliance", "score": 50, "justification": "j", "citation": "c", "confidence": "low"}
        ],
        "composite_index": 50.0, "top_findings": {"positives": [], "negatives": []},
        "roadmap": [{"action": "a", "dimension": "d", "effort": 1, "impact": 2, "owner": "o", "expected_effect": "e", "rationale": "r"}],
        "assumptions": [], "confidence": "low", "limitations": [],
    }
    p = tmp_path / "bad.json"
    p.write_text(json.dumps(bad), encoding="utf-8")
    rc, out, err = _run([str(p)])
    assert rc != 0
    assert "all 5 dimensions" in err


def test_weights_must_sum_to_one(tmp_path):
    bad = {
        "schema_version": "1.0", "stage": "sub-requirements-gatherer", "inherited_from": "x",
        "hazards": [], "jurisdiction": "US-OSHA",
        "frameworks": [{"name": "NFPA 101", "justification": "j", "citation": "c", "role": "primary"}],
        "requirements": [
            {"id": "R1", "dimension": d, "criterion": "c", "framework_ref": "f", "pass_condition": "p", "benchmark": None}
            for d in ["regulatory_compliance", "response_time", "communication", "evacuation_effectiveness", "gap_closure"]
        ],
        "scoring_weights": {"regulatory_compliance": 0.2, "response_time": 0.2, "communication": 0.2,
                             "evacuation_effectiveness": 0.2, "gap_closure": 0.1},
        "assumptions": [], "confidence": "low", "limitations": [],
    }
    p = tmp_path / "w.json"
    p.write_text(json.dumps(bad), encoding="utf-8")
    rc, out, err = _run([str(p)])
    assert rc != 0 and "sum to" in err


def test_gate_failure_flagged(tmp_path):
    bad = _load_fixture("stage4_quality_reviewer.json")
    bad["gate_checklist"]["every_score_cited"] = "fail"
    p = tmp_path / "g.json"
    p.write_text(json.dumps(bad), encoding="utf-8")
    rc, out, err = _run([str(p)])
    assert rc != 0 and "every_score_cited" in err


def test_score_out_of_range_fails(tmp_path):
    bad = _load_fixture("stage3_scoring_engine.json")
    bad["scores"][0]["score"] = 120
    p = tmp_path / "r.json"
    p.write_text(json.dumps(bad), encoding="utf-8")
    rc, out, err = _run([str(p)])
    assert rc != 0 and "out of 0-100" in err


def test_unknown_stage_rejected(tmp_path):
    bad = {"schema_version": "1.0", "stage": "not-a-stage"}
    p = tmp_path / "u.json"
    p.write_text(json.dumps(bad), encoding="utf-8")
    rc, out, err = _run([str(p)])
    assert rc != 0 and "unknown or missing stage" in err


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
