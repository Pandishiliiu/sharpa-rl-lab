# Sharpa RL Lab SDK 兼容性适配与部署可靠性验证

## 1. 本周新增可运行能力

完成 Sharpa Wave SDK v5.0.11 触觉 JSON 结构与路径适配，默认使用板端触觉推理；对 F6、通道和数值进行帧级校验，用单调时间戳识别 missing/stale 通道，并阻止异常触觉进入策略观测。控制流程增加 Standby（4）、Reset（2）、Run Policy（3）门禁；Reset 归零、等待和轨迹执行期间持续检查授权与触觉。部署循环对 `RuntimeError`/`KeyboardInterrupt` 统一收敛到 `env.close()`，清理可重复调用。

## 2. 运行环境与验证方式

Windows 11 + WSL2 Ubuntu 22.04.5，Python 3.10.12，虚拟环境 `~/internship/.venv-sharpa`，Sharpa Wave SDK 5.0.11（`/opt/sharpa-wave-sdk`）。当前无实体机械手；采用标准库 Mock 和 AST 提取当前源码方法进行离线验证，未枚举设备、未发送电机指令。

## 3. 测试结果

| 测试 | 验证内容 | 实际结果 |
|---|---|---|
| Python 语法 | 7 个关键代码文件与全部离线测试 | PASS，exit 0 |
| 触觉 Mock | 正常帧、缺 F6、非法通道/数值、missing/stale、v5.0.11 配置 | PASS，exit 0 |
| 控制 Mock | Standby 无新指令/无观测刷新，Run Policy 与观测门禁 | PASS，exit 0 |
| Reset Mock | 初始、归零等待、轨迹阶段异常，未授权拒绝，成功转 Run Policy | PASS，exit 0 |
| 异常清理/Contract | RuntimeError、KeyboardInterrupt、`env.close()`、幂等清理、结构契约 | PASS，exit 0 |

## 4. 一个失败案例

人为 Mock 删除通道或把时间戳设为过期后，原始流程可能读取不完整触觉，或在 Reset/策略控制中继续下发新指令。原因是缓存存在性不等于帧合法且新鲜。修改后以帧校验 + 单调时间戳 + 状态/阶段门禁拒绝该数据；对应 Mock 均 PASS。这是构造故障，不是真实设备故障记录。

## 5. 一个需要讨论的问题

SDK `stop()` 主要停止触觉采集，不等于机械手电机急停。真机部署前需与 SDK/硬件负责人确认：软件 Standby 时电机是保持还是解除使能；通信丢失和进程退出时的固件默认动作；硬件急停的触发、复位和验收方法。

## 6. 验证边界

- **Mock：已验证**—触觉校验/新鲜度、状态门禁、Reset 阶段保护、异常退出与幂等清理。
- **物理仿真：本次未运行**—未启动 Isaac Lab / Omniverse。
- **真机：本次未验证**—无设备连接、无电机指令、无真实触觉帧。
