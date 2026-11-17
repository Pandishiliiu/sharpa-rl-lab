# Week 2 代码变更清单

## 功能代码

- `rl_isaaclab/scripts/deploy.py`
  - 板端触觉推理改为默认，保留 `--enable_host_tactile` 显式切换。
  - 将策略循环收敛为可测试的 `run_policy_loop()`；`RuntimeError` 记录后重新抛出，`KeyboardInterrupt` 正常退出，两者均在 `finally` 调用 `env.close()`。
- `rl_isaaclab/tasks/inhand_rotate/sharpa_wave_deploy_env.py`
  - 调用 v5.0.11 配置生成器，将生成路径传给 `SharpaWaveConfig`。
  - 触觉回调先校验帧，仅合法数据更新缓存和单调时间戳。
  - `get_tactile_status()` 报告 missing/stale，`get_tactile_info()` 拒绝异常缓存进入观测。
  - Standby 不发送新关节位置、不刷新观测，但保持标准五元组返回；初始 Standby `reset()` 返回预置零观测。
  - Reset 开始、归零前/等待中、轨迹前/执行中/读取时及完成时检查授权和触觉，成功后转入 Run Policy。
  - `close()` 设置软件 Standby、停止键盘监听/触觉采集并断开 SDK，且重复调用无副作用。
  - 修复整理时发现的未定义 `deploy_state` 和 Standby 分支无返回值问题；删除已失效的旧回调、旧配置与旧控制注释块。
- `rl_isaaclab/tasks/inhand_rotate/sharpa_wave_deploy_env_cfg.py`
  - 保留本次部署所依赖的控制频率、触觉、接触阈值和板端开关配置；当前 Git diff 仅为注释补充，无行为变更。
- `rl_isaaclab/utils/keyboard_listener.py`
  - 增加 Standby（4）语义，Standby 中按 `w` 不转入保持控制。
  - `stop()` 设置终止事件后限时等待线程，便于确认资源清理。
- `rl_isaaclab/utils/tactile_config.py`
  - 新增 SDK v5.0.11 顶层 `left`/`right` JSON 适配，分别生成板端 30 FPS 或主机端 180 FPS 配置，不改写 SDK 原文件。
- `rl_isaaclab/utils/tactile_validation.py`
  - 新增手型通道范围、F6 存在性、数值长度/类型/有限性和力模长校验。
- `rl_isaaclab/utils/tactile_freshness.py`
  - 新增按策略手指到 SDK 通道的映射、禁用手指排除及 missing/stale 分类。

## 离线测试与交付材料

- `tests/offline/test_tactile_mock.py`：触觉帧、freshness 和 SDK JSON 生成。
- `tests/offline/test_control_mock.py`：Standby、Run Policy 与策略观测门禁。
- `tests/offline/test_reset_mock.py`：Reset 初始/归零等待/轨迹阶段故障、未授权拒绝和成功转态。
- `tests/offline/test_cleanup_mock.py`：RuntimeError、KeyboardInterrupt、`env.close()` 及幂等清理。
- `tests/offline/test_week2_contracts.py`：保留并增强现有 AST/静态契约。
- `tests/offline/_method_loader.py`：在不导入硬件依赖的情况下执行当前源码方法。
- `tests/offline/run_week2.sh`：统一入口，逐项检查进程退出码。
- `tests/offline/run_logged.sh`：记录时间、命令、输出、退出码与 PASS/FAIL。
- `ENVIRONMENT.md`、`RUN_COMMANDS.md`、`RESULTS_ONE_PAGE.md`：环境、复现命令与一页结果。
- `reports/week2/`：保留首次测试脚本失败说明与最终实际 PASS 日志。

## 未纳入 Week 2 提交代码

工作区中 `rl_isaaclab/tasks/inhand_rotate/sharpa_wave_env_cfg.py`、`rl_isaaclab/utils/misc.py`、`test_callback_local.py`、`test_joint_mapping.py` 存在与本次交付无关或无功能影响的用户原有修改/文件。本次未回退它们，也未收入提交 ZIP。`.venv-dryrun/`、`.bak*`、`__pycache__/`、`*.pyc` 同样被排除。
