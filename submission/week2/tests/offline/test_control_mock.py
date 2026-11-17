"""Offline tests for Standby, Run Policy, and observation gating."""

from __future__ import annotations

import time
from types import SimpleNamespace

from _method_loader import load_env_method


class Flag:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class Hand:
    def __init__(self):
        self.commands = []

    def set_joint_position(self, command):
        self.commands.append(command)

    def get_states(self):
        return SimpleNamespace(angles=[0.0] * 22)


class Action:
    def to(self, device):
        return self


step = load_env_method("step", time=time)
get_tactile_info = load_env_method("get_tactile_info")


env = SimpleNamespace()
env.cfg = SimpleNamespace(keyboard_listen=True, enable_tactile=True)
env.deploy_state_flag = Flag(4)
env.calib_tactile_flag = Flag(0)
env.hand = Hand()
env.device = "cpu"
env._last_step_wall = time.perf_counter()
env.target_dt = 0.0
env.episode_length_buf = 0
env.obs_buf = {"policy": "last-valid"}
env.get_tactile_status = lambda: {
    "ready": False,
    "missing": [0],
    "stale": [],
}
refresh_count = [0]


def forbidden_refresh():
    refresh_count[0] += 1
    raise AssertionError("Standby must not refresh observations")


env._get_observations = forbidden_refresh
env._check_reset_gate = lambda stage: None
env._reset_idx = lambda ids: None
env._pre_physics_step = lambda action: None
env._apply_action = lambda: None
env.calib_tactile = lambda: None

result = step(env, Action())
assert len(result) == 5 and result[0] is env.obs_buf
assert env.hand.commands == []
assert refresh_count[0] == 0
print("PASS: Standby sends no command and keeps the last observation")

env.deploy_state_flag.set(3)
try:
    step(env, Action())
except RuntimeError as exc:
    assert "Tactile data unavailable" in str(exc)
else:
    raise AssertionError("Run Policy accepted unavailable tactile data")
assert env.hand.commands == []
print("PASS: Run Policy rejects unavailable tactile data before control")

gate_env = SimpleNamespace(
    cfg=SimpleNamespace(enable_tactile=True),
    get_tactile_status=lambda: {
        "ready": False,
        "missing": [4],
        "stale": [],
    },
)
try:
    get_tactile_info(gate_env)
except RuntimeError as exc:
    assert "Tactile observation unavailable" in str(exc)
else:
    raise AssertionError("Invalid tactile data entered policy observation")
print("PASS: invalid tactile data is rejected from policy observation")

print("\nALL CONTROL MOCK TESTS PASSED")
