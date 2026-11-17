"""Offline deployment exception and idempotent cleanup tests."""

from __future__ import annotations

from types import SimpleNamespace

from _method_loader import load_deploy_function, load_env_method


class Value:
    def detach(self):
        return self


class LoopEnv:
    def __init__(self, failure):
        self.failure = failure

    def reset(self):
        return {"obs": Value(), "proprio_hist": Value()}

    def step(self, action):
        raise self.failure


class CloseTarget:
    def __init__(self):
        self.close_calls = 0

    def close(self):
        self.close_calls += 1


def make_agent(failure):
    loop_env = LoopEnv(failure)
    return SimpleNamespace(
        env=loop_env,
        running_mean_std=lambda value: value,
        sa_mean_std=lambda value: value,
        model=SimpleNamespace(act_inference=lambda inputs: "action"),
    )


run_policy_loop = load_deploy_function("run_policy_loop")

target = CloseTarget()
try:
    run_policy_loop(make_agent(RuntimeError("mock failure")), target)
except RuntimeError as exc:
    assert str(exc) == "mock failure"
else:
    raise AssertionError("RuntimeError was swallowed")
assert target.close_calls == 1
print("PASS: RuntimeError is re-raised and env.close() is called")

target = CloseTarget()
run_policy_loop(make_agent(KeyboardInterrupt()), target)
assert target.close_calls == 1
print("PASS: KeyboardInterrupt exits and env.close() is called")


class Flag:
    def __init__(self):
        self.values = []

    def set(self, value):
        self.values.append(value)


class Listener:
    def __init__(self):
        self.stop_calls = 0

    def stop(self):
        self.stop_calls += 1


class Hand:
    def __init__(self):
        self.stop_calls = 0

    def stop(self):
        self.stop_calls += 1


class Manager:
    def __init__(self):
        self.disconnect_calls = 0

    def disconnect_all(self):
        self.disconnect_calls += 1


manager = Manager()
manager_type = SimpleNamespace(get_instance=lambda: manager)
close = load_env_method("close", SharpaWaveManager=manager_type)
env = SimpleNamespace(
    deploy_state_flag=Flag(),
    keyboard_proc=Listener(),
    hand=Hand(),
)
close(env)
close(env)
assert env.deploy_state_flag.values == [4]
assert env.keyboard_proc.stop_calls == 1
assert env.hand.stop_calls == 1
assert manager.disconnect_calls == 1
print("PASS: resource cleanup is idempotent and stops tactile acquisition")

print("\nALL CLEANUP MOCK TESTS PASSED")
