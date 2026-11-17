import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if not (ROOT / "rl_isaaclab").is_dir() and (ROOT / "code/rl_isaaclab").is_dir():
    ROOT = ROOT / "code"

ENV = ROOT / "rl_isaaclab/tasks/inhand_rotate/sharpa_wave_deploy_env.py"
DEPLOY = ROOT / "rl_isaaclab/scripts/deploy.py"

MODULES = [
    ROOT / "rl_isaaclab/utils/tactile_config.py",
    ROOT / "rl_isaaclab/utils/tactile_validation.py",
    ROOT / "rl_isaaclab/utils/tactile_freshness.py",
    ENV,
    DEPLOY,
]


def find_method(cls, name):
    matches = [
        node for node in cls.body
        if isinstance(node, ast.FunctionDef)
        and node.name == name
    ]
    assert len(matches) == 1, f"方法不存在或重复: {name}"
    return matches[0]


# 1. 所有关键模块必须存在，且能够解析
for path in MODULES:
    assert path.exists(), f"缺失模块: {path}"
    ast.parse(path.read_text(encoding="utf-8"))

print("PASS: 五个核心模块语法检查")


# 2. 检查环境类结构
env_tree = ast.parse(ENV.read_text(encoding="utf-8"))

cls = next(
    node for node in env_tree.body
    if isinstance(node, ast.ClassDef)
    and node.name == "SharpaWaveInhandRotateDeployEnv"
)

for name in (
    "step",
    "_reset_idx",
    "_check_reset_gate",
    "get_tactile_status",
    "get_tactile_info",
    "close",
):
    find_method(cls, name)

print("PASS: 控制、触觉和资源管理方法完整")


# 3. Standby 门禁
step_code = ast.unparse(find_method(cls, "step"))
step_method = find_method(cls, "step")

assert "deploy_state != 4" in step_code
assert "get_tactile_status" in step_code
five_value_returns = [
    node
    for node in ast.walk(step_method)
    if isinstance(node, ast.Return)
    and isinstance(node.value, ast.Tuple)
    and len(node.value.elts) == 5
]
assert len(five_value_returns) == 1

print("PASS: Standby与触觉检查分离且始终返回五元组")


# 4. Reset 检查
reset_code = ast.unparse(find_method(cls, "_reset_idx"))

for stage in (
    "start",
    "before_home",
    "home_wait",
    "before_trajectory",
    "trajectory_start",
    "trajectory_step",
    "trajectory_read",
    "finish",
):
    assert stage in reset_code, f"缺少Reset检查阶段: {stage}"

print("PASS: Reset关键检查阶段完整")


# 5. 异常退出清理
deploy_tree = ast.parse(
    DEPLOY.read_text(encoding="utf-8")
)

run_policy_loop = next(
    node for node in deploy_tree.body
    if isinstance(node, ast.FunctionDef)
    and node.name == "run_policy_loop"
)

try_blocks = [
    node for node in run_policy_loop.body
    if isinstance(node, ast.Try)
]

assert try_blocks, "缺少部署异常处理"

finally_code = "\n".join(
    ast.unparse(node)
    for node in try_blocks[0].finalbody
)

assert "env.close()" in finally_code

print("PASS: 部署退出调用环境close")

main = next(
    node for node in deploy_tree.body
    if isinstance(node, ast.FunctionDef)
    and node.name == "main"
)
assert "run_policy_loop(agent, env)" in ast.unparse(main)
print("PASS: 部署主函数使用可测试的策略循环")


# 6. CLI配置
deploy_code = DEPLOY.read_text(encoding="utf-8")

assert "--enable_host_tactile" in deploy_code
assert "parser.set_defaults(enable_on_board=True)" in deploy_code

print("PASS: 板端触觉推理默认配置")

print("\nALL TESTS PASSED")
