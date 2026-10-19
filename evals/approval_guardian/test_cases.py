"""The labelled cases stay valid inputs for the smart-approval guardian.

Each case must still be flagged by the current detector with the recorded description and
pattern key, and must not be hard-blocked first, or a scorecard built on it would measure
commands the guardian never sees. The file must match its provenance pin.
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE))

from agent.runtime_self_protection import command_deletes_runtime
from run_cases import CASES, VERDICTS, load_cases, score
from tools.approval_detection import detect_dangerous_command, detect_hardline_command

FIELDS = {"id", "category", "command", "description", "pattern_key", "expected", "note"}


def test_cases_match_provenance_pin():
    provenance = json.loads((HERE / "cases.provenance.json").read_text(encoding="utf-8"))
    data = CASES.read_bytes()
    assert (provenance["sha256"], provenance["bytes"], provenance["cases"]) == (
        hashlib.sha256(data).hexdigest(), len(data), len(load_cases()))


def test_cases_are_well_formed():
    cases = load_cases()
    assert len(cases) >= 150
    assert len({c["id"] for c in cases}) == len(cases)
    for case in cases:
        assert set(case) == FIELDS, case["id"]
        assert case["expected"] in VERDICTS, case["id"]


def test_every_case_reaches_the_guardian():
    for case in load_cases():
        command = case["command"]
        assert detect_dangerous_command(command) == (True, case["pattern_key"], case["description"]), case["id"]
        assert not detect_hardline_command(command)[0], case["id"]
        assert not command_deletes_runtime(command), case["id"]


def test_approve_everything_scores_every_unsafe_label_as_false_approve():
    cases = {c["id"]: c for c in load_cases()}
    rows = [{"id": i, "verdict": "approve", "latency_s": 0.1, "warnings": []} for i in cases]
    unsafe = sum(c["expected"] != "approve" for c in cases.values())
    result = score(rows, cases)
    assert result["false_approve"] == round(unsafe / len(cases), 4)
    assert result["auto_approved"] == 1.0 and result["escalation"] == 0.0
