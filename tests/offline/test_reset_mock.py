"""Offline reset warm-up authorization and tactile gate tests."""

from __future__ import annotations

from types import SimpleNamespace

from _method_loader import load_env_method


class Flag:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class Buffer:
    def __init__(self):
        self.writes = []

    def __setitem__(self, key, value):
        self.writes.append((key, value))


class Hand:
    _ALL_INDICES = [0]

    def __init__(self):
        self.positions = []

    def set_speed_coeff(self, value):
        return SimpleNamespace(code=0)

    def set_current_coeff(self, value):
        return SimpleNamespace(code=0)

    def set_joint_position(self, value):
        self.positions.append(value)


class FakeTime:
    def __init__(self):
        self.now = 0.0

    def monotonic(self):
        self.now += 0.1
        return self.now

    def sleep(self, seconds):
        self.now += seconds


class FakeNumpy:
    @staticmethod
    def load(path):
        return [[float(index)] * 22 for index in range(5)]


class FakeTorch:
    float32 = "float32"

    @staticmethod
    def max(value):
        return max(value)

    @staticmethod
    def tensor(value, **kwargs):
        return value


fake_time = FakeTime()
check_gate = load_env_method("_check_reset_gate")
reset_idx = load_env_method(
    "_reset_idx",
    time=fake_time,
    np=FakeNumpy,
    torch=FakeTorch,
    dof_sharpa2isaaclab=lambda value: value,
)


def make_env(status_provider, warm_up=True):
    env = SimpleNamespace()
    env.cfg = SimpleNamespace(
        keyboard_listen=True,
        enable_tactile=True,
        warm_up=warm_up,
        current_coef=0.3,
        speed_coef=0.5,
    )
    env.deploy_state_flag = Flag(2)
    env.get_tactile_status = status_provider
    env.hand = Hand()
    env.device = "cpu"
    env.episode_length_buf = Buffer()
    env.last_contacts = Buffer()
    env.proprio_hist_buf = Buffer()
    env.at_reset_buf = Buffer()
    env.prev_targets = Buffer()
    env.cur_targets = Buffer()
    env.get_tactile_info = lambda: ([2.0], None)
    env._refresh_lab = lambda: None
    env._check_reset_gate = lambda stage: check_gate(env, stage)
    return env


not_ready = lambda: {"ready": False, "missing": [0], "stale": []}
env = make_env(not_ready)
try:
    reset_idx(env, [0])
except RuntimeError as exc:
    assert "Reset:start" in str(exc)
else:
    raise AssertionError("Reset accepted invalid initial tactile data")
assert env.hand.positions == [] and env.deploy_state_flag.get() == 4
print("PASS: Reset rejects invalid initial tactile data")

ready_calls = [0]


def fail_during_home_wait():
    ready_calls[0] += 1
    if ready_calls[0] <= 2:
        return {"ready": True, "missing": [], "stale": []}
    return {"ready": False, "missing": [], "stale": [1]}


fake_time.now = 0.0
env = make_env(fail_during_home_wait)
try:
    reset_idx(env, [0])
except RuntimeError as exc:
    assert "Reset:home_wait" in str(exc)
else:
    raise AssertionError("Reset ignored tactile failure during home wait")
assert len(env.hand.positions) == 1 and env.deploy_state_flag.get() == 4
print("PASS: Reset aborts when tactile becomes stale during home wait")

fake_time.now = 0.0
env = make_env(lambda: {"ready": True, "missing": [], "stale": []})
original_gate = env._check_reset_gate


def fail_during_trajectory(stage):
    if stage == "trajectory_step":
        env.deploy_state_flag.set(4)
        raise RuntimeError("[Reset:trajectory_step] Tactile unavailable")
    original_gate(stage)


env._check_reset_gate = fail_during_trajectory
env.get_tactile_info = lambda: ([0.0], None)
try:
    reset_idx(env, [0])
except RuntimeError as exc:
    assert "Reset:trajectory_step" in str(exc)
else:
    raise AssertionError("Reset ignored tactile failure during trajectory")
assert env.deploy_state_flag.get() == 4
print("PASS: Reset aborts when tactile fails during trajectory")

env = make_env(lambda: {"ready": True, "missing": [], "stale": []}, warm_up=False)
env.deploy_state_flag.set(3)
try:
    reset_idx(env, [0])
except RuntimeError as exc:
    assert "Reset:start" in str(exc) and "control state=3" in str(exc)
else:
    raise AssertionError("Unauthorized Reset was not rejected")
assert env.hand.positions == []
print("PASS: unauthorized Reset is rejected")

fake_time.now = 0.0
env = make_env(lambda: {"ready": True, "missing": [], "stale": []})
reset_idx(env, [0])
assert env.deploy_state_flag.get() == 3
assert len(env.hand.positions) >= 2
print("PASS: successful Reset transitions to Run Policy")

print("\nALL RESET MOCK TESTS PASSED")
