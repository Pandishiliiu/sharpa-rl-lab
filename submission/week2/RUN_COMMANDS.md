# Week 2 运行命令

以下命令均在 WSL Ubuntu 22.04 终端执行。本次已实际执行的命令不会发现、连接或控制机械手。

## 已实际执行成功

### 1. 进入项目并激活虚拟环境

```bash
cd /mnt/d/Internship/workspace/02_代码与环境/sharpa-rl-lab
source "$HOME/internship/.venv-sharpa/bin/activate"
```

### 2. 检查 SDK Python 接口（仅导入，不获取 Manager）

```bash
PYTHONPATH=/opt/sharpa-wave-sdk/python \
python -c "import sharpa; print(sharpa.__file__)"
```

### 3. Python 语法检查

```bash
python -m py_compile \
  rl_isaaclab/scripts/deploy.py \
  rl_isaaclab/tasks/inhand_rotate/sharpa_wave_deploy_env.py \
  rl_isaaclab/tasks/inhand_rotate/sharpa_wave_deploy_env_cfg.py \
  rl_isaaclab/utils/keyboard_listener.py \
  rl_isaaclab/utils/tactile_config.py \
  rl_isaaclab/utils/tactile_validation.py \
  rl_isaaclab/utils/tactile_freshness.py \
  tests/offline/*.py
```

### 4. 触觉 Mock 测试

```bash
python tests/offline/test_tactile_mock.py
```

### 5. Reset Mock 测试

```bash
python tests/offline/test_reset_mock.py
```

### 6. 完整 Week 2 离线回归

```bash
PYTHON_BIN="$HOME/internship/.venv-sharpa/bin/python" \
bash tests/offline/run_week2.sh
```

成功时末行为 `WEEK2_RESULT: PASS`，且 shell 退出码为 `0`。异常清理用例会打印人为构造的 `RuntimeError: mock failure` traceback，该用例的 `RESULT: PASS` 和最终退出码才是判定依据。

### 7. 查看已保存日志

```bash
ls -lh reports/week2/
sed -n '1,240p' reports/week2/05_week2_full_regression_2026-11-11.log
```

## 仅供后续真机部署前参考，本次未验证

本次不提供可直接启动真机部署的命令。在任何真机运行前，需先由设备负责人人工确认：完整 Python 依赖、checkpoint 路径、手型与 IP、SDK 控制源、电机使能/保持逻辑、软件 Standby 与硬件急停的区别，并在有物理急停和专人监护的环境中单独制定部署命令。
