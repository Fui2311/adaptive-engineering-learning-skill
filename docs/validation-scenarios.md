# 验证场景

自动测试覆盖五个要求场景的状态不变量，并增加三项状态安全测试；自然语言输出质量仍需在真实仓库中前向测试。

## 场景一：首次分析

- `propose` 保存 `project.json`、`plan.json(status=proposed)` 和可选项目地图。
- 断言不创建 `progress.json`。
- 发现与计划参考明确禁止开始长篇教学和生成大量任务。

## 场景二：确认并调整

- `revise-plan` 保存调整、递增计划版本并保持 `proposed`。
- `activate` 拒绝空确认，接受明确调整摘要后改为 `active`。
- 仅把第一个阶段任务设为 `learning`，其他任务保持 `not_started`。

## 场景三：继续学习

- `show` 返回当前 task、stage 和 code locations；无需重新扫描。
- 源码教学参考要求从当前位置推进一个小目标。

## 场景四：中途提问

- `update-task` 可只在当前任务记录问题并切换 `questioning`。
- 其他阶段和计划顺序不变；笔记是否写入由价值判断决定。

## 场景五：结束学习

- 无证据的 `mastered` 被拒绝。
- 有证据后可更新任务；`record-session` 只记录目标、完成、文件、认知、练习、问题和下一步。
- `doctor` 校验计划/进度版本和掌握证据。

## 额外异常

- 自定义笔记路径不存在时，测试断言返回明确原因并回退项目路径。
- 禁止回退的自定义路径配置失败时，测试断言原配置保持不变。
- 已有用户配置在首次保存候选计划时保持不变。
- `archive` 只复制，不删除源状态。
- `propose` 拒绝覆盖 active/paused/completed 计划或已有进度。

## 实际结果

- 2026-07-20：`test_learning_state.py` 共 8 项，全部通过。
- 2026-07-20：`skill-creator/scripts/quick_validate.py` 返回 `Skill is valid!`。
- 源目录与 `.agents/skills` 可发现副本在最终同步后执行 SHA-256 清单比对。
