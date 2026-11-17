# Week 2 环境说明

## 已核对的本地环境

| 项目 | 实际值 | 验证状态 |
|---|---|---|
| 宿主系统 | Windows 11 家庭中文版，版本 `10.0.26200` | 已查询 |
| WSL | Ubuntu 22.04.5 LTS，WSL2 kernel `6.18.33.2` | 已查询 |
| Python | `3.10.12` | 已运行 |
| Python 虚拟环境 | `~/internship/.venv-sharpa` | 已用于本次测试 |
| Sharpa Wave SDK | `5.0.11`，Build ID `5.0.11.6` | 已读取 `/opt/sharpa-wave-sdk/VERSION` |
| SDK 安装目录 | `/opt/sharpa-wave-sdk` | 已存在 |
| SDK Python 搜索路径 | `/opt/sharpa-wave-sdk/python` | 设置 `PYTHONPATH` 后已导入 `sharpa` |
| GPU | NVIDIA GeForce RTX 4060 Laptop GPU，WSL 驱动 `610.60` | 仅查询，本次测试未使用 |
| 实体机械手 | 当前无 | 未连接、未控制 |

## 依赖情况

`tests/offline/` 中的 Week 2 回归仅依赖 Python 3.10 标准库。行为测试从当前源码 AST 提取控制方法，并使用内存 Mock 替代设备、Torch、NumPy 和 Gym，不进行设备枚举或电机指令下发。

完整部署代码还需要以下 Python 包：

- `sharpa`（由 SDK 提供，本地导入成功）
- `torch`
- `numpy`
- `gymnasium`
- `omegaconf`
- `rl_games`
- `pynput`

对 `~/internship/.venv-sharpa` 的实际查询结果为：`sharpa` 在设置 SDK `PYTHONPATH` 后可用；其余上述包当前均未安装。因此本次没有导入完整部署环境、加载策略权重或运行 Isaac Lab。

## 尚未验证的组件

- Isaac Lab / Omniverse 物理仿真未运行。
- 模型 checkpoint 未加载，GPU 推理未运行。
- SDK 设备发现、触觉采集、关节控制和机械手使能均未验证。
- `hand.stop()` 仅按 SDK 接口用于停止触觉采集；本次不将其视为电机急停。
