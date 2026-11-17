# Sharpa RL Lab Week 2 交付包

主题：**Sharpa RL Lab 与 Sharpa Wave SDK v5.0.11 兼容性适配及部署可靠性验证**

## 内容

- `ENVIRONMENT.md`：实际环境、SDK 信息、依赖缺口和验证边界。
- `RUN_COMMANDS.md`：可复制的 WSL 离线检查命令。
- `RESULTS_ONE_PAGE.md`：一页结果记录。
- `CHANGELOG.md`：逐文件变更清单与排除项。
- `code/`：本次 Week 2 功能相关源码，保留仓库内相对路径。
- `tests/offline/`：可重复执行的离线 Mock/契约测试及统一入口。
- `logs/`：2026-11-11 实际运行日志，包含命令、输出、退出码和 PASS/FAIL。

## 复现离线回归

在 ZIP 解压后的 `week2/` 目录直接执行：

```bash
PYTHON_BIN=python3 bash tests/offline/run_week2.sh
```

测试会自动识别原仓库的 `rl_isaaclab/` 或交付包的 `code/rl_isaaclab/`。离线回归仅需 Python 3.10 标准库；它从当前源码提取方法并使用 Mock，不连接 SDK 设备，不发送电机指令。

2026-11-11 的最终完整回归结果为 `WEEK2_RESULT: PASS`、退出码 `0`。详见 `logs/05_week2_full_regression_2026-11-11.log`。

## 安全和验证边界

- Mock：已验证。
- Isaac Lab / Omniverse 物理仿真：本次未运行。
- 实体机械手：本次未连接、未验证。
- `hand.stop()` 不被视为电机急停。本包不提供可直接启动真机的部署命令。
