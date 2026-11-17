"""Offline tactile configuration, validation, and freshness tests."""

from __future__ import annotations

import importlib.util
import json
import math
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if not (ROOT / "rl_isaaclab").is_dir() and (ROOT / "code/rl_isaaclab").is_dir():
    ROOT = ROOT / "code"


def load_module(name, relative_path):
    path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


validation = load_module(
    "tactile_validation", "rl_isaaclab/utils/tactile_validation.py"
)
freshness = load_module(
    "tactile_freshness", "rl_isaaclab/utils/tactile_freshness.py"
)
config = load_module("tactile_config", "rl_isaaclab/utils/tactile_config.py")


valid = {"channel": 0, "content": {"F6": [3.0, 4.0, 0.0]}}
assert validation.validate_tactile_frame(valid, hand_side=1) == (0, 5.0)
print("PASS: normal tactile frame")

assert validation.validate_tactile_frame(
    {"channel": 0, "content": {}}, hand_side=1
) is None
print("PASS: missing F6 rejected")

assert validation.validate_tactile_frame(
    {"channel": 8, "content": {"F6": [1, 2, 3]}}, hand_side=1
) is None
print("PASS: illegal channel rejected")

for value in (math.nan, math.inf, -math.inf, "bad"):
    frame = {"channel": 0, "content": {"F6": [value, 0, 0]}}
    assert validation.validate_tactile_frame(frame, hand_side=1) is None
print("PASS: non-finite and non-numeric values rejected")

now = 100.0
status = freshness.check_tactile_freshness(
    {0: now, 1: now, 2: now, 3: now},
    hand_side=1,
    max_age=0.5,
    now=now,
)
assert status == {"ready": False, "missing": [4], "stale": []}

status = freshness.check_tactile_freshness(
    {0: now, 1: now, 2: now - 1.0, 3: now, 4: now},
    hand_side=1,
    max_age=0.5,
    now=now,
)
assert status == {"ready": False, "missing": [], "stale": [2]}
print("PASS: missing and stale channels detected")

source_data = {
    "config_dir": "",
    "left": {"fps": 30, "infer_from_device": True, "other": 1},
    "right": {"fps": 30, "infer_from_device": True, "other": 2},
}
with tempfile.TemporaryDirectory() as temp_dir:
    source = Path(temp_dir) / "source.json"
    output = Path(temp_dir) / "generated" / "tactile_left.json"
    source.write_text(json.dumps(source_data), encoding="utf-8")
    result = config.prepare_tactile_config(source, output, 0, False)
    generated = json.loads(result.read_text(encoding="utf-8"))
    assert generated["left"]["fps"] == 180
    assert generated["left"]["infer_from_device"] is False
    assert generated["right"] == source_data["right"]
print("PASS: SDK v5.0.11 tactile config generated without mutating source")

print("\nALL TACTILE MOCK TESTS PASSED")
