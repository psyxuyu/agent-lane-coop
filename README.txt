Agent Lane Coop
================

Agent Lane Coop 是一个用于 Codex 多线程/多 Agent 协作的技能包。它通过项目内的共享 lane/ 目录，记录各个 Agent 的职责、工作日志、任务认领、状态汇报、交接信息和父子线程协作关系，帮助多个 Codex 会话在同一个项目中有序协作。


功能概览
--------

- 注册当前 Codex 线程为一个协作 lane
- 维护项目级公共 Agent 索引：lane/agent_lane.json
- 维护公共进度日志：lane/work_log.md
- 为每个角色创建独立工作区：lane/<role>/work_space/
- 支持任务认领、心跳刷新、消息轮询、状态广播和任务关闭
- 支持父线程与子线程之间的结果汇报、阻塞汇报和交接
- 可选使用 SQLite 作为轻量消息和任务状态注册表


目录结构
--------

agent-lane-coop/
  SKILL.md
  agents/
    openai.yaml
  references/
    coordination-patterns.md
    message-schema.md
    protocol.md
    thread-tools.md
  scripts/
    lane_register.py
    lane_report.py
    lane_claim.py
    lane_post.py
    lane_poll.py
    lane_heartbeat.py
    lane_close.py
    lane_store.py


使用场景
--------

适合以下情况：

- 一个项目中需要多个 Codex 线程分工协作
- 需要创建规划、实现、审核、检索、测试等不同角色的 Agent
- 需要让子线程向父线程汇报结果或阻塞
- 需要避免多个 Agent 同时修改同一任务
- 需要保留项目级协作日志和工作记录
- 需要在没有线程工具时，通过文件系统进行轻量协作


基本工作流
----------

1. 在项目根目录下注册当前 Agent lane。
2. 读取 lane/agent_lane.json，了解已有协作线程。
3. 读取 lane/work_log.md，了解项目整体进展。
4. 在开始修改或输出前认领任务。
5. 工作过程中按阶段写入状态消息和工作日志。
6. 长任务中定期刷新心跳。
7. 完成、阻塞或交接时写入报告，并通知父线程。


示例命令
--------

注册一个规划 Agent：

python scripts/lane_register.py --root <project_root> --role 规划 --lane 规划Agent --purpose "负责拆解任务、协调子线程和汇总结果"

认领任务：

python scripts/lane_claim.py --lane 规划Agent --task-id task-001 --title "拆解项目协作任务"

发送状态消息：

python scripts/lane_post.py --from-lane 规划Agent --topic status --type status --body "已完成任务拆解，准备分配实现和审核线程。"

刷新心跳：

python scripts/lane_heartbeat.py --lane 规划Agent

生成汇报：

python scripts/lane_report.py --root <project_root> --role 规划 --status completed --task task-001 --summary "任务拆解和协作计划已完成。"


生成的协作目录
--------------

使用后，项目中会生成类似结构：

<project_root>/lane/
  agent_lane.json
  work_log.md
  coordination_log.md
  inbox/
  <role>/
    agent_lane.json
    work_log.md
    work_space/

其中：

- lane/agent_lane.json 是项目级公共 Agent 索引
- lane/work_log.md 是项目级公共进度日志
- lane/coordination_log.md 记录跨角色协调事件
- lane/<role>/work_log.md 记录某个角色的详细工作过程
- lane/<role>/work_space/ 用于存放该角色产生的中间成果或输出


SQLite 注册表
-------------

该技能默认以项目内 lane/ 文件夹作为权威协作记录。

SQLite 注册表是可选功能，用于轻量存储消息、任务认领和 lane 状态。默认路径为：

<home>/.codex/agent-lanes/agent_lanes.sqlite

可以通过环境变量或命令行参数覆盖：

AGENT_LANE_DB=<path>

或：

python scripts/lane_register.py --db <path> ...


Lane 命名规则
-------------

lane 名称要求使用 XXAgent 格式，其中 XX 为中文角色名，例如：

规划Agent
检索Agent
写作Agent
审核Agent
测试Agent


注意事项
--------

- 不要把运行生成的 lane/ 目录提交到仓库。
- 不要提交 SQLite 数据库文件。
- 多个 Agent 协作前应先读取公共索引和公共日志。
- 修改文件前应先认领任务，避免重复工作或冲突。
- 子线程完成任务后，应向父线程汇报结果、阻塞或交接状态。
- 如果线程工具不可用，可以只依赖项目内 lane/ 文件夹完成协作记录。


许可证
------

请根据你的发布需求自行选择许可证，例如 MIT、Apache-2.0 或其他许可证。
