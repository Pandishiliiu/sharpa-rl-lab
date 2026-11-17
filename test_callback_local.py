"""
Sharpa 触觉接口本地测试

测试目标：
1. 正常左手触觉数据
2. 正常右手触觉数据
3. F6 字段缺失
4. 非法通道编号
5. content 字段缺失

无需安装 Isaac Lab、PyTorch 或连接真实机器人。

注意：
使用 AST 从 Sharpa 官方源代码提取 tactile_callback，
然后使用 Mock 对象替代外部依赖。
"""

import ast
import math
from pathlib import Path
from types import SimpleNamespace

# ============================================================
# 1. 定位 Sharpa 原始代码
# ============================================================

SOURCE_FILE = Path("rl_isaaclab/tasks/inhand_rotate/sharpa_wave_deploy_env.py")

if not SOURCE_FILE.exists():
    raise FileNotFoundError(
        f"找不到源文件: {SOURCE_FILE}\n" "请确保在 sharpa-rl-lab 项目根目录运行。"
    )

print("=" * 55)
print("Sharpa Wave 触觉接口测试")
print("=" * 55)

print(f"源文件: {SOURCE_FILE}")


# ============================================================
# 2. 从源代码提取 tactile_callback
# ============================================================

source = SOURCE_FILE.read_text(encoding="utf-8")

tree = ast.parse(source)

# 找到原始类
target_class = next(
    node
    for node in tree.body
    if isinstance(node, ast.ClassDef) and node.name == "SharpaWaveInhandRotateDeployEnv"
)

# 找到原始函数
target_function = next(
    node
    for node in target_class.body
    if isinstance(node, ast.FunctionDef) and node.name == "tactile_callback"
)

print("成功定位原始 tactile_callback 函数")


# ============================================================
# 3. 模拟 PyTorch 的少量功能
# ============================================================


class MockTorch:

    float32 = "float32"

    @staticmethod
    def tensor(x):
        if x is None:
            raise TypeError("MockTorch: 不能将 None 转换为 tensor")
        return list(x)

    @staticmethod
    def norm(x):
        return math.sqrt(
            sum(float(v) ** 2 for v in x)
        )

    @staticmethod
    def zeros(shape, dtype=None, device=None):
        if isinstance(shape, int):
            n = shape
        else:
            n = shape[0]

        return [0.0] * n
# ============================================================
# 4. 编译原始函数
# ============================================================

module = ast.Module(body=[target_function], type_ignores=[])

namespace = {"torch": MockTorch}

exec(compile(ast.fix_missing_locations(module), str(SOURCE_FILE), "exec"), namespace)

callback = namespace["tactile_callback"]

print("成功加载触觉处理函数")


# ============================================================
# 5. 创建模拟机器人环境
# ============================================================


class MockHand:

    def __init__(self, side):

        # 与当前官方部署代码保持一致
        # hand_side = 0 -> 通道 5~9
        # hand_side = 1 -> 通道 0~4

        self.cfg = SimpleNamespace(hand_side=side)

        self.device = "cpu"

        start_channel = 5 * (1 - side)

        self.frames = {
            ch: [None, None, None, None]
            for ch in range(start_channel, start_channel + 5)
        }


# ============================================================
# 6. 测试函数
# ============================================================


def run_test(name, side, frame):

    print("\n" + "-" * 55)

    print(f"测试项目: {name}")

    print(f"hand_side: {side}")

    print(f"输入数据: {frame}")

    hand = MockHand(side)

    original_channels = set(hand.frames.keys())

    try:

        # 调用真正的 Sharpa tactile_callback
        callback(hand, frame)

        print("执行状态: SUCCESS")

        channel = frame.get("channel")

        if channel in hand.frames:

            data = hand.frames[channel]

            print(f"通道: {channel}")
            print(f"力的模长: {data[1]}")
            print(f"接触位置: {data[3]}")

        # 检查有没有创建非法通道
        new_channels = set(hand.frames.keys()) - original_channels

        if new_channels:

            print(f"警告: 创建了额外通道 {new_channels}")

    except Exception as e:

        print("执行状态: ERROR")

        print(f"异常类型: {type(e).__name__}")

        print(f"异常信息: {e}")


# ============================================================
# 7. 开始测试
# ============================================================

# 测试1：正常左手
run_test(
    name="正常左手", side=0, frame={"channel": 5, "content": {"F6": [3, 4, 0, 0, 0, 0]}}
)


# 测试2：正常右手
run_test(
    name="正常右手", side=1, frame={"channel": 0, "content": {"F6": [3, 4, 0, 0, 0, 0]}}
)


# 测试3：F6 缺失
run_test(name="F6 字段缺失", side=0, frame={"channel": 5, "content": {}})


# 测试4：非法通道
run_test(
    name="非法通道 99",
    side=0,
    frame={"channel": 99, "content": {"F6": [3, 4, 0, 0, 0, 0]}},
)


# 测试5：content 缺失
run_test(name="content 字段缺失", side=0, frame={"channel": 5})


print("\n" + "=" * 55)

print("所有测试用例执行结束")

print("=" * 55)
