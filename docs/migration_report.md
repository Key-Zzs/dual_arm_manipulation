# Migration Analysis Report: dual_arm_teleop Nero Communication Layer

生成日期：2026-05-18

本报告只基于本轮只读扫描生成，未迁移、删除、重构或修改任何现有代码。外部仓库 `https://github.com/Key-Zzs/agilex_teleop` 在当前环境下未能直接读取到 `nero_interface/nero_interface_server.py`；server 端细节主要来自本仓库 `HEAD` 中已删除的历史文件 `legacy/nero/teleop/interface/nero_interface_server.py`，需要后续与外部仓库人工核对。

## 1. Workspace Overview

- 当前工作空间/LeRobot 总仓库路径：`/home/keyz/Documents/projects/Robot/wbcd/dual_arm_manipulation`
- 当前仓库 `pyproject.toml` 显示顶层项目仍是 `lerobot`，版本 `0.3.4`。
- `dual_arm_teleop` 包路径：`dual_arm_data_collection/lerobot_dual_arm_teleop`
  - 该目录的 `setup.py` 包名是 `dual_arm_teleop`。
  - 当前工作区未发现 `.gitmodules` 文件，因此这次扫描无法确认它是否仍以 git submodule 形式挂载。
- `dual_agilex_nero/` 路径：`dual_arm_data_collection/lerobot_dual_arm_teleop/robots/dual_agilex_nero`
- `nero_dual_arm.py` 路径：`dual_arm_data_collection/lerobot_dual_arm_teleop/robots/dual_agilex_nero/nero_dual_arm.py`
- 同目录文件：
  - `__init__.py`
  - `config_nero.py`
  - `nero_dual_arm.py`
  - `nero_interface_client.py`
- 当前工作空间未发现本地 `dual_arm_data_collection/agilex_teleop/` 目录。
- 当前工作空间未发现当前文件树中的 `nero_interface_server.py`；但 git 历史里有已删除的 `legacy/nero/teleop/interface/nero_interface_server.py`。
- README 中发现外部 server 启动说明：`python nero/teleop/interface/nero_interface_server.py --ip 0.0.0.0 --port 4242`。

## 2. Target Communication Functions

### 2.1 `send_action_cartesian`

- 文件路径：`dual_arm_data_collection/lerobot_dual_arm_teleop/robots/dual_agilex_nero/nero_dual_arm.py`
- 函数签名：`def send_action_cartesian(self, action: dict[str, Any]) -> None`
- 所属类：`NeroDualArm`
- 直接调用者：
  - `NeroDualArm.send_action()` 在 `not self.config.debug` 时调用。
  - `scripts/core/run_record.py` 的混合控制主循环中最终调用 `robot.send_action(sent_action)`。
  - `scripts/core/run_replay.py` 从 dataset 取 action 后调用 `robot.send_action(action)`。
- 参数含义：
  - `action` 是 LeRobot/teleop/dataset 使用的 action dict。
  - 必须包含 12 个 Cartesian delta key：
    - `left_delta_ee_pose.x/y/z/rx/ry/rz`
    - `right_delta_ee_pose.x/y/z/rx/ry/rz`
- 输入 action / pose 格式：
  - 单臂 pose delta 为 6 维 numpy array，顺序为 `[x, y, z, rx, ry, rz]`。
  - 从 client 和 server 注释看，位置单位是 m，姿态单位是 radians。
  - 当前函数使用 `np.array([...])`，没有 `dtype=float` 显式转换。
- 是否区分 left/right arm：
  - 是。左臂 RPC 参数是 `"left_robot"`；右臂 RPC 参数是 `"right_robot"`。
- 是否支持双臂同时发送：
  - 支持在一次 `send_action_cartesian` 调用中依次发送左臂和右臂。
  - 不是真正的单个双臂 RPC；左/右分别调用一次 `servo_p_OL`。
- 内部调用：
  - `_should_send_action()` 做频率限制。
  - `np.linalg.norm(left_delta) >= 0.001` 时发送左臂。
  - `np.linalg.norm(right_delta) >= 0.001` 时发送右臂。
  - `self._robot.servo_p_OL("left_robot", left_delta, delta=True)`
  - `self._robot.servo_p_OL("right_robot", right_delta, delta=True)`
- 最终 RPC 方法名：
  - client wrapper：`NeroDualArmClient.servo_p_OL(robot_arm, pose, delta=False)`
  - zerorpc server 方法：`servo_p_OL(robot_arm, pose, delta)`
- RPC 方法签名：
  - client 端：`servo_p_OL(self, robot_arm: str, pose: np.ndarray, delta: bool = False) -> bool`
  - server 历史版本：`servo_p_OL(self, robot_arm: str, pose: list, delta: bool) -> bool`
- 返回值格式：
  - `send_action_cartesian` 自身返回 `None`。
  - client `servo_p_OL` 返回 server 的 bool，但 `send_action_cartesian` 当前未读取返回值。
  - 如果 `self.server is None`，client wrapper 返回 `True`，这会掩盖未连接状态。
- 异常处理：
  - `send_action_cartesian` 捕获整个左右臂发送块的 `Exception`，只 `logger.warning`，不抛出。
  - `send_action` 外层也捕获 `send_action_cartesian` 的异常并 warning。
  - client wrapper 内部没有 per-RPC try/except。
- timeout / retry 行为：
  - `send_action_cartesian` 无 retry。
  - zerorpc client 初始化使用 `zerorpc.Client(heartbeat=20)`，没有显式 timeout。
  - `_should_send_action` 使用本地时间节流：`action_send_freq = 100.0`，`action_send_dt = 0.01s`。注释写“50Hz”，实际代码是 100Hz。
  - server 历史版本内部有 IK 超时保护：`max_ik_solve_ms = 30.0`，失败后会短暂跳过/衰减 delta，但这是 execution server 端逻辑，不属于当前仓库迁移范围。
- 依赖列表：
  - 标准库：`time`, `logging`, `typing.Any`
  - 第三方：`numpy`
  - 本地：`NeroDualArmClient`
  - LeRobot 强耦合：`Robot`, `DeviceNotConnectedError`, `NeroDualArmConfig`

完整调用链：

1. `OculusDualArmRobot.get_action()` 或 policy/dataset 生成 action。
2. `OculusTeleop.get_action()` 将 Oculus obs 转为 action dict。
3. `run_record.py` 或 `run_replay.py` 调用 `robot.send_action(...)`。
4. `NeroDualArm.send_action()` 在 `debug=False` 时调用 `send_action_cartesian(action)`。
5. `send_action_cartesian()` 拆出 left/right 6D delta。
6. `NeroDualArmClient.servo_p_OL("left_robot" / "right_robot", pose, delta=True)`。
7. `zerorpc.Client.server.servo_p_OL(robot_arm, pose.tolist(), delta)`。
8. 外部 server 历史实现里 `servo_p_OL` 解 IK 后调用 `robot.move_js(q_cmd)`，不是直接调用 `move_p`。

### 2.2 `handle_gripper`

- 文件路径：`dual_arm_data_collection/lerobot_dual_arm_teleop/robots/dual_agilex_nero/nero_dual_arm.py`
- 函数签名：`def handle_gripper(self, arm_side: str, gripper_value: float, is_binary: bool = False) -> None`
- 所属类：`NeroDualArm`
- 直接调用者：
  - `NeroDualArm.send_action()` 在 action 中存在 `left_gripper_cmd` / `right_gripper_cmd` 时调用。
- 参数含义：
  - `arm_side`: `"left"` 或 `"right"`。代码未校验非法值，非 `"left"` 会落入右夹爪分支。
  - `gripper_value`: 归一化夹爪开合值。
  - `is_binary`: 二值模式开关。当前 `send_action` 固定传 `False`。
- gripper command 格式：
  - 当前 action key：
    - `left_gripper_cmd`
    - `right_gripper_cmd`
  - 值范围：期望 `[0.0, 1.0]`。
  - `0.0` 表示闭合，`1.0` 表示打开。
  - 最终 width = `gripper_cmd * self.config.gripper_max_open`。
  - 默认 `gripper_max_open = 0.1`，`gripper_force = 2.0`。
- 是否区分 left/right gripper：
  - 是。`arm_side == "left"` 调 `left_gripper_goto`，否则调 `right_gripper_goto`。
- 内部调用：
  - `_clip_gripper_cmd(value)` 将连续值裁剪到 `[0.0, 1.0]`。
  - binary 模式下用 `close_threshold` 变成 `0.0` 或 `1.0`。
  - `gripper_reverse=True` 时做 `1.0 - gripper_cmd`。
  - 与上次命令差值 `< 1e-3` 时跳过 RPC。
  - 调 `self._robot.left_gripper_goto(width=..., force=...)` 或 `right_gripper_goto(...)`。
- 最终 RPC 方法名：
  - `left_gripper_goto(width, force)`
  - `right_gripper_goto(width, force)`
- RPC 方法签名：
  - client 端：`left_gripper_goto(self, width: float, force: float)` / `right_gripper_goto(self, width: float, force: float)`
  - server 历史版本：`left_gripper_goto(self, width: float, force: float = 1.0)` / `right_gripper_goto(self, width: float, force: float = 1.0)`
- 返回值格式：
  - `handle_gripper` 自身返回 `None`。
  - client wrapper 不返回 server 结果。
  - server 历史版本返回 bool。
- 异常处理：
  - `handle_gripper` 捕获 RPC 异常并 warning。
  - client wrapper 无 per-RPC try/except。
- timeout / retry 行为：
  - 无 retry。
  - 无 client-side timeout。
  - server 历史版本对重复 `(width, force)` 命令去重；左右夹爪各自缓存上次命令。
- 依赖列表：
  - 标准库：`time`, `logging`
  - 本地：`_clip_gripper_cmd`, `NeroDualArmClient`
  - 配置：`use_gripper`, `close_threshold`, `gripper_reverse`, `gripper_max_open`, `gripper_force`

完整调用链：

1. Oculus trigger 或 policy/dataset 给出 `left_gripper_cmd` / `right_gripper_cmd`。
2. `NeroDualArm.send_action()` 调 `handle_gripper("left"/"right", value, is_binary=False)`。
3. `handle_gripper()` 归一化并转换为 width。
4. `NeroDualArmClient.left_gripper_goto(width, force)` / `right_gripper_goto(width, force)`。
5. zerorpc 调 server 同名方法。
6. server 历史实现中最终调用 `left_gripper.move_gripper(width=width, force=force)` 或 `right_gripper.move_gripper(...)`。

## 3. Zerorpc Client Analysis

- zerorpc client 初始化位置：
  - `dual_arm_data_collection/lerobot_dual_arm_teleop/robots/dual_agilex_nero/nero_interface_client.py`
  - `NeroDualArmClient.__init__(ip='127.0.0.1', port=4242)`
- server address 构造：
  - `tcp://{ip}:{port}`
- ip / port 来源：
  - `NeroDualArm.check_nero_connection()` 用 `self.config.robot_ip` 和 `self.config.robot_port` 构造 client。
  - 默认配置来自 `NeroDualArmConfig`：
    - `robot_ip = "192.168.110.114"`
    - `robot_port = 4242`
  - `run_record.py` 会从 YAML 的 `record.robot.robot_ip` / `robot_port` 覆盖，默认 fallback 是 `"localhost"` 和 `4242`。
  - `run_replay.py` 支持 `robot_ip` 和 legacy `ip`，默认 `"localhost"` 和 `4242`。
  - `scripts/config/record_cfg.yaml` 当前 `robot_type` 为 `nero_dual_arm`，但 `robot_ip` 写的是 `"10.10.10.1"`，注释仍写 dobot server ip，需人工确认。
- 是否有默认值：
  - client 默认 `127.0.0.1:4242`。
  - config 默认 `192.168.110.114:4242`。
  - YAML parser 默认 `localhost:4242`。
- timeout：
  - 当前 Nero client 没有显式 `timeout`。
  - 只有 `heartbeat=20`。
- reconnect：
  - 未发现 reconnect / retry 机制。
  - 连接失败时 `self.server = None`，但大部分 wrapper 会返回默认值或 `True`，上层可能误以为成功。
- close：
  - `NeroDualArm.disconnect()` 调 `self._robot.close()`。
  - `NeroDualArmClient.close()` 先调用 `robot_stop("left_robot")` 和 `robot_stop("right_robot")`，再 `server.close()`。
  - 注意：server 历史版本的 `robot_stop` 是 electronic emergency stop。轻量仓库中不建议默认把 close 等同于急停。
- heartbeat / health check：
  - zerorpc heartbeat=20。
  - 没有显式 health check；`check_nero_connection()` 通过读取左右 EE pose 和 joint positions 做弱连通检查。
- 异常捕获：
  - 初始化捕获连接异常。
  - stop/close 捕获异常。
  - 单个 RPC wrapper 大多不捕获异常。
  - `NeroDualArm` 的 cartesian/gripper/get_observation 上层有部分捕获。
- 与 teleop / dataset 耦合：
  - `NeroDualArmClient` 基本不耦合 teleop/dataset。
  - `NeroDualArm` 强耦合 LeRobot `Robot`、camera、action_features、observation_features。
  - `run_record.py` / `run_replay.py` 将 config、dataset、policy、teleop 与 robot client 串在一起，不适合直接迁移到 comm 层。

## 4. Action Format Analysis

- Cartesian action 数据结构：
  - dict，key 为 `{left,right}_delta_ee_pose.{x,y,z,rx,ry,rz}`。
  - 每只手臂转换为 6 维 numpy array `[x, y, z, rx, ry, rz]`。
- 位姿维度：
  - 单臂 6D。
  - 双臂 12D；如果包含 gripper，Oculus 原始 action 是 14D。
- 单臂/双臂格式：
  - `NeroDualArm` 只实现双臂字段，直接索引左右所有 12 个 key，缺 key 会抛 `KeyError`。
  - `send_action_cartesian` 不是 partial action 友好型。
- xyz / rpy / quaternion 使用情况：
  - client/server 接口注释均为 `[x, y, z, rx, ry, rz]`，单位 m/radians。
  - Oculus 端用 `scipy.spatial.transform.Rotation.as_rotvec()` 得到旋转增量向量，然后映射为 `rx/ry/rz`。
  - server 历史版本的 `servo_p_OL` 在 delta 模式下把当前 RPY 与 delta RPY 转为 quaternion 相乘，再转回 RPY 后 IK。
- 单位：
  - 位置：m。
  - 姿态：rad。
  - 需要注意 `config_nero.py` 中 `gripper_max_open: 0.1` 注释写 “10mm”，但 `0.1 m` 是 100mm；server 也 clamp 到 `0.1`。
- delta action 还是 absolute action：
  - `send_action_cartesian` 强制 `delta=True`，所以是增量动作。
  - `NeroDualArmClient.servo_p_OL` 支持 `delta=False`，但当前调用链不用 absolute。
- `send_action_cartesian` 与 server 端 `servo_p_OL` 的对应关系：
  - 当前仓库 client 把 numpy pose `.tolist()` 后 RPC 到 server。
  - server 历史实现中 `servo_p_OL` 先限幅 delta，再由 IK solver 求 `q_cmd`，最终调用 `robot.move_js(q_cmd)`。
  - 用户描述的外部 server “最终调用 `servo_p_OL` 和夹爪控制函数完成执行”与 client 调用名一致；但外部 GitHub 文件尚未核对。
- 坐标系约定：
  - Oculus 端文档写：
    - Oculus: X(right), Y(up), Z(backward/towards user)
    - Robot: X(forward), Y(left), Z(up)
    - position transform matrix:
      - `robot_x = -oculus_z`
      - `robot_y = -oculus_x`
      - `robot_z = oculus_y`
  - 旋转映射为：
    - `robot roll = oculus_rz`
    - `robot pitch = oculus_rx`
    - `robot yaw = oculus_ry`
- 硬编码偏移或限幅：
  - client `send_action_cartesian` 对 delta norm 小于 `0.001` 的单臂命令不发送。
  - client action 发送频率硬编码 `100.0`。
  - server 历史版本硬编码：
    - `track_freq = 50.0`
    - `max_cart_step_m = 0.03`
    - `max_rot_step_rad = 0.35`
    - `max_joint_step_rad = 0.1`
    - `limit_z` CLI 默认 `0.26`，函数默认 `0.07`
    - 可选 `tcp_offset = [0.19, 0, 0, 0, 0, 0]`
- 风险点：
  - `get_observation()` 中 EE pose 写入顺序使用 `["x", "y", "z", "rz", "ry", "rx"]`，与 feature 声明 `["x", "y", "z", "rx", "ry", "rz"]` 不一致，需要确认是否历史补偿还是 bug。
  - client 100Hz 与 server 50Hz 不一致。
  - action key 缺失会直接报错。

## 5. Gripper Format Analysis

- gripper command 数据结构：
  - action dict 中使用 `left_gripper_cmd` / `right_gripper_cmd`。
  - 兼容旧 teleop 输出的 `left_gripper_cmd_bin` / `right_gripper_cmd_bin`，但 `NeroDualArm.send_action()` 当前只读取新 key。
- open / close / goto / force：
  - 当前迁移重点路径只使用 goto：`left_gripper_goto(width, force)` / `right_gripper_goto(width, force)`。
  - client 还有 `left_gripper_grasp(force=1.0, width=0.05)` / `right_gripper_grasp(...)`，但 `handle_gripper` 不调用。
  - client 还有 `left_gripper_get_state()` / `right_gripper_get_state()`，但 `NeroDualArm.get_observation()` 当前没有读取真实夹爪状态，只回填上次命令。
- value 范围：
  - teleop trigger：`trigger=0.0` -> `gripper=1.0` open；`trigger=1.0` -> `gripper=0.0` close。
  - `handle_gripper` 连续模式裁剪到 `[0.0, 1.0]`。
  - binary 模式下 `< close_threshold` -> `0.0`，否则 `1.0`。
  - 最终 width clamp 由 server 历史版本限制在 `[0.0, 0.1]`。
- 左右夹爪区分：
  - action key 区分 left/right。
  - RPC 方法名区分 left/right。
  - server 历史版本左右夹爪分别绑定 `can_left` / `can_right` arm 初始化出的 effector。
- 是否有阻塞等待：
  - client `handle_gripper` 不显式等待。
  - server 历史 `left_gripper_goto` / `right_gripper_goto` 不 sleep，只调用 `move_gripper`。
  - server `_setup_gripper` 初始化时有通信等待和开合 sleep。
  - `left_gripper_grasp` 有 `time.sleep(1.5)`，但当前主路径不用。
- 是否有状态反馈：
  - client 提供 get_state wrapper。
  - `NeroDualArm.get_observation()` 不读 get_state，只返回 `_left_gripper_cmd` / `_right_gripper_cmd`。
  - server 历史版本 get_state 返回 `width`, `force`, `is_moving`, `is_grasped`。
- 错误处理：
  - `handle_gripper` 捕获异常并 warning。
  - client wrapper 不返回 server bool。
  - server 历史版本错误返回 False。

## 6. Minimal Dependencies for Migration

| 原路径 | 名称 | 类型 | 是否必须迁移 | 迁移原因 | 建议新位置 |
|---|---|---|---|---|---|
| `robots/dual_agilex_nero/nero_interface_client.py` | `NeroDualArmClient` | class | 是 | zerorpc client 的最小封装，包含 connect/address/RPC 方法名 | `src/bimanual_rule_control/comm/dual_arm_rpc_client.py` |
| `robots/dual_agilex_nero/nero_interface_client.py` | `__init__(ip, port)` | method | 是 | 构造 `zerorpc.Client(heartbeat=20)` 并连接 `tcp://ip:port` | `src/bimanual_rule_control/comm/dual_arm_rpc_client.py` |
| `robots/dual_agilex_nero/nero_interface_client.py` | `servo_p_OL` | method | 是 | Cartesian delta action 最终 RPC | `src/bimanual_rule_control/comm/dual_arm_rpc_client.py` |
| `robots/dual_agilex_nero/nero_interface_client.py` | `left_gripper_goto` / `right_gripper_goto` | methods | 是 | gripper command 最终 RPC | `src/bimanual_rule_control/comm/dual_arm_rpc_client.py` |
| `robots/dual_agilex_nero/nero_interface_client.py` | `robot_go_home` | method | 建议迁移 | reset/home 常用控制命令 | `src/bimanual_rule_control/comm/dual_arm_rpc_client.py` |
| `robots/dual_agilex_nero/nero_interface_client.py` | `left/right_robot_get_ee_pose`, `left/right_robot_get_joint_positions` | methods | 可选 | 连接检查、debug、dry-run 对照可能需要 | `src/bimanual_rule_control/comm/dual_arm_rpc_client.py` |
| `robots/dual_agilex_nero/nero_interface_client.py` | `close` | method | 需要改造后迁移 | 当前 close 会先 `robot_stop`，可能触发急停，不宜原样迁移 | `src/bimanual_rule_control/comm/dual_arm_rpc_client.py` |
| `robots/dual_agilex_nero/nero_dual_arm.py` | `send_action_cartesian` | method logic | 是 | dict action 到左右 `servo_p_OL` 的核心转换逻辑 | `src/bimanual_rule_control/comm/action_format.py` + `comm/dual_arm_rpc_client.py` |
| `robots/dual_agilex_nero/nero_dual_arm.py` | `handle_gripper` | method logic | 是 | gripper normalized command 到 width/force RPC 的核心转换逻辑 | `src/bimanual_rule_control/comm/action_format.py` |
| `robots/dual_agilex_nero/nero_dual_arm.py` | `_clip_gripper_cmd` | function | 是 | gripper command 裁剪 | `src/bimanual_rule_control/comm/action_format.py` |
| `robots/dual_agilex_nero/nero_dual_arm.py` | `_should_send_action` / `action_send_freq` | logic/config | 建议迁移 | 控制发送频率；但需先确认 50Hz/100Hz | `src/bimanual_rule_control/core/config.py` |
| `robots/dual_agilex_nero/config_nero.py` | `robot_ip`, `robot_port`, `use_gripper`, `gripper_max_open`, `gripper_force`, `gripper_reverse`, `close_threshold` | config fields | 是 | comm 层最小运行配置 | `src/bimanual_rule_control/core/config.py` |
| `robots/dual_agilex_nero/config_nero.py` | `gripper_ip`, `gripper_port` | config fields | 否/待确认 | 当前 Nero 主路径未使用独立 gripper server，配置疑似历史遗留 | `legacy/` 或后续删除 |
| `robots/dual_agilex_nero/nero_dual_arm.py` | action key names | constants | 是 | 需要稳定定义 action schema | `src/bimanual_rule_control/comm/command_types.py` |
| `teleoperators/oculus_teleoperator/oculus/oculus_dual_arm_robot.py` | Oculus 坐标转换 | logic | 否 | 属于 VR teleop，不属于新仓库 comm 最小层 | `legacy/` |
| `legacy/nero/teleop/interface/nero_interface_server.py` | `servo_p_OL` server implementation | external execution | 否 | 新仓库不包含 execution server，只需记录 RPC 契约 | `legacy/` 文档引用 |
| third-party | `zerorpc` | dependency | 是 | RPC 通信必需 | project dependency |
| third-party | `numpy` | dependency | 建议保留 | action array / norm / conversion 简化 | project dependency |
| stdlib | `dataclasses`, `logging`, `time`, `typing` | dependency | 是 | config、日志、频率控制、类型标注 | stdlib |

## 7. Dependencies That Should NOT Be Migrated

- LeRobot core：`lerobot.robots.robot.Robot`, `RobotConfig`, `make_cameras_from_configs`, `DeviceNotConnectedError`, feature schema helpers。原因：轻量规控仓库不应继承 LeRobot robot abstraction。
- dataset / record / replay：`LeRobotDataset`, `run_record.py`, `run_replay.py`, dataset feature conversion。原因：新仓库只保留 comm 最小通信，不做采集回放。
- training / policy / evaluation：ACT、Diffusion、SmolVLA、policy processor、`predict_action`。原因：传统规控仓库不依赖训练推理链。
- DAgger：`scripts/core/run_dagger_*`, `tests/test_dagger_*`。原因：与本轮通信迁移无关。
- Oculus / VR：`teleoperators/oculus_teleoperator/*`, `oculus_reader`, `scipy Rotation`。原因：规划层后续由 perception/planning 生成动作，不从 VR 读动作。
- keyboard/gamepad/phone teleop：原因：非目标输入源。
- cameras / RealSense / visualization / rerun：原因：感知层后续会单独搭 OpenCV/YOLOv8/AprilTag，不应把 LeRobot camera stack 拉入 comm。
- HuggingFace / W&B / datasets / torch / torchvision / diffusers：原因：训练与数据管理依赖，体积大且与 comm 无关。
- `pyAgxArm`, CAN 脚本, IK solver, Pinocchio solver：原因：这些属于外部 execution server，不应进入当前轻量仓库。
- 其他机器人实现：Dobot、Franka、ARX、example robot。原因：本次目标是 Agilex Nero zerorpc client 契约。

## 8. Unclear or Risky Dependencies

| 原路径 | 不确定原因 | 建议人工检查 | 下一轮处理建议 |
|---|---|---|---|
| 外部 `Key-Zzs/agilex_teleop/nero_interface/nero_interface_server.py` | 当前环境无法读取；本报告 server 细节来自本仓库已删除历史版本 | 核对外部 server 是否仍有 `servo_p_OL(robot_arm, pose, delta)`、`left/right_gripper_goto(width, force)` | 迁移前固定一份 RPC contract 文档 |
| `config_nero.py` 的 `robot_ip` vs YAML `record_cfg.yaml` | 默认是 `192.168.110.114`，YAML 是 `10.10.10.1` 且注释写 dobot | 确认实际 Nero server IP | 新仓库用 YAML/env 覆盖，不硬编码生产 IP |
| `gripper_ip` / `gripper_port` | Nero 当前主路径没有独立 gripper client，gripper RPC 走同一个 `robot_port` | 确认外部 server 是否单端口同时控制 arm+gripper | 若单端口，删除独立 gripper port 配置或保留为 legacy |
| `gripper_max_open = 0.1` 注释 | 注释写 10mm，但数值是 0.1m；server 也 clamp 到 0.1 | 确认 Agilex gripper width 单位和最大开口 | 用清晰字段名 `max_width_m`，补 dry-run 测试 |
| `action_send_freq = 100.0` 注释写 50Hz | client 实际 100Hz，server 历史 `track_freq=50Hz` | 确认真实期望控制频率 | 新 config 显式 `command_rate_hz` |
| `get_observation()` pose axis mapping | feature 是 `rx, ry, rz`，写入循环是 `rz, ry, rx` | 确认 server `get_tcp_pose()` 返回顺序 | 暂不迁移 observation 或加明确转换测试 |
| `close()` 先 `robot_stop()` | server 历史 `robot_stop` 是急停 | 确认 disconnect 是否应该停机 | 新 client 把 `close()` 和 `emergency_stop()` 分开 |
| zerorpc timeout/reconnect | 当前无 timeout/retry，连接失败时 wrapper 可能返回默认成功 | 确认规划层对失败的安全策略 | Round 2 增加可配置 timeout、失败返回、可选 reconnect |
| server `limit_z` | 函数默认 0.07，CLI 默认 0.26，README 启动未写 `--limit-z` | 确认真实安全 z limit | 只在文档中记录，不迁移 server safety |
| `debug=True` 默认 | 默认 debug 会阻止 cartesian action，但 gripper 仍可发 | 确认 dry-run 语义 | 新仓库引入 `dry_run`，明确 arm/gripper 是否都禁发 |

## 9. Proposed Lightweight Architecture

只写建议，不在本轮实现。

```text
project_root/
├── configs/
│   ├── task_1.yaml
│   ├── dry_run.yaml
│   ├── debug_perception.yaml
│   └── debug_comm.yaml
│
├── src/
│   └── bimanual_rule_control/
│       ├── core/
│       ├── comm/
│       ├── perception/
│       ├── planning/
│       └── tasks/
│
├── scripts/
├── tests/
├── docs/
└── legacy/
```

- 当前轻量仓库不包含 execution server。
- 当前轻量仓库通过 zerorpc 调外部 `agilex_teleop` server。
- `comm/` 层只迁移最小通信逻辑：
  - `DualArmRpcClient`
  - action/gripper command schema
  - action dict -> RPC pose/list 转换
  - dry-run/mock client
- `perception/` 层后续搭 OpenCV / YOLOv8 / AprilTag。
- `planning/` 层后续写 `task_1`、`task_router`、controllers。
- `legacy/` 只放参考代码或迁移备忘，不参与运行依赖。

## 10. Recommended Migration Plan for Round 2

1. 新建轻量仓库目录结构。
2. 创建 `comm/base.py`，定义 robot client 抽象接口。
3. 创建 `comm/command_types.py`，固定 `ArmSide`, `RobotArmName`, action key 常量和 command dataclass。
4. 从 `nero_interface_client.py` 提取最小 `DualArmRpcClient`，只保留 connect、servo、gripper、home、state query、close。
5. 创建 `comm/action_format.py`，封装 `parse_dual_cartesian_delta_action()` 和 `normalize_gripper_command()`。
6. 创建 `MockRobotClient`，不连接真实 server，只记录 calls。
7. 创建 dry-run 测试：验证 action dict 到 `servo_p_OL("left_robot", [...], True)` / gripper width 的映射。
8. 创建 perception skeleton：camera input、detector interface、AprilTag/YOLO placeholder。
9. 创建 planning skeleton：controller interface、task state、rule output action。
10. 创建 `tasks/task_1.py`、`task_router.py`、`scripts/main.py`。
11. 将 LeRobot、dataset、record、replay、policy、DAgger、Oculus 相关代码留在 `legacy/` 或不迁移。
12. 跑 pytest，重点覆盖 action schema、gripper clipping、dry-run client、RPC failure behavior。

## 11. Exact Questions for Human Confirmation

1. 外部 `agilex_teleop` server 当前版本是否确认仍是 `servo_p_OL(robot_arm, pose, delta)`？
2. `send_action_cartesian` 的 action 是否永远是 delta，而不是 absolute？
3. 姿态字段 `rx/ry/rz` 在外部 server 中是否语义为 RPY radians，而不是 rotation vector？
4. `get_tcp_pose()` 返回顺序到底是 `[x, y, z, rx, ry, rz]` 还是 `[x, y, z, rz, ry, rx]`？
5. 默认是否只用右臂，还是 task_1 必须双臂同时可控？
6. gripper command 的归一化值是否固定 `1=open, 0=closed`？
7. `gripper_max_open=0.1` 的单位是否是 meter？注释“10mm”是否错误？
8. 外部 server 默认端口是否固定为 4242？
9. 是否需要独立 gripper port 4243，还是 arm/gripper 都在同一个 zerorpc server？
10. disconnect 时是否允许调用 `robot_stop`/急停，还是只关闭 zerorpc socket？
11. 控制频率应为 50Hz 还是 100Hz？
12. 是否需要保留任何 camera / rerun / LeRobot observation 代码？
13. `limit_z`、TCP offset、IK 失败衰减是否完全由外部 server 负责？
14. 是否需要在轻量仓库中实现 reconnect / retry，还是失败立即返回给 planning 层？

## Round 2 Migration Result

- 已完整迁移 `dual_arm_data_collection/lerobot_dual_arm_teleop/robots/dual_agilex_nero/` 到 `src/bimanual_rule_control/comm/dual_agilex_nero/`，保留四个文件：
  - `config_nero.py`
  - `__init__.py`
  - `nero_dual_arm.py`
  - `nero_interface_client.py`
- 与第一轮报告不同的处理：
  - 第一轮建议提取最小通信逻辑；第二轮按新策略完整保留已验证 `dual_agilex_nero` 通信接口目录。
  - 新增 `NeroCommAdapter` 作为 planning/tasks 面向的轻量入口，不重写 `send_action_cartesian` / `handle_gripper` 核心语义。
  - `close()` 与 `emergency_stop()` 在 adapter 层拆开，避免普通关闭默认触发旧 client 的 `robot_stop()`。
- 未迁移到主代码的内容：
  - LeRobot framework、teleop/Oculus、record、dataset、replay、train、policy、DAgger、HuggingFace、W&B 等逻辑未进入 `src/bimanual_rule_control` 主包。
  - 旧 LeRobot 代码暂时保留在工作区，不作为新包安装目标。
- legacy 化处理：
  - 本轮没有大规模移动旧文件到 `legacy/`，以降低风险。
  - `pyproject.toml` 已将安装包限制为 `bimanual_rule_control*`，主代码不依赖 legacy。
- optional compatibility：
  - `dual_agilex_nero/config_nero.py` 对 LeRobot `RobotConfig` / `CameraConfig` 做 optional fallback。
  - `dual_agilex_nero/nero_dual_arm.py` 对 LeRobot `Robot` / camera / error classes 做 optional fallback。
  - `dual_agilex_nero/nero_interface_client.py` 对 `zerorpc` 做 optional import，未安装时给出清晰提示。
- 仍需人工确认：
  - 外部 server 当前 RPC 签名是否仍是 `servo_p_OL(robot_arm, pose, delta)`。
  - `rx/ry/rz` 是 RPY radians 还是 rotation vector。
  - `get_tcp_pose()` 返回顺序。
  - `gripper_max_open=0.1` 的单位和真实最大开口。
  - 控制频率最终采用 50Hz 还是 100Hz。
  - disconnect 是否允许急停；当前 adapter 默认不急停。
