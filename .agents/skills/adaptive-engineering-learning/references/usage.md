# 日常使用

安装后直接说目标，不需要记模式名或命令。自动发现取决于宿主环境；首次可显式调用 `$adaptive-engineering-learning`。由 Skill 创建的问答任务会自动携带调用方式和源项目路径。

| 你说 | 行为 |
| --- | --- |
| 带我学这个项目，先给路线 | 检查真实代码，提出候选路线，等明确确认后激活 |
| 路线可以，从请求入口开始 | 激活并开始指定内容；若你要求仅恢复状态则等待 |
| 继续上次的学习 | 恢复主线断点并直接讲解 |
| 这段为什么要传 context？ | 结合源码直接回答，补齐所需基础，不强制反问 |
| 把这个问题单独开个问答任务 | 自动打包原问题、相关讲解、代码位置和断点，交接到问答任务 |
| 继续这个问答 | 在已识别的问答任务中继续，不跳回主线 |
| 给我一个练习，先只给提示 | 给边界与验收标准，一次一个分级提示 |
| 今天先到这里 | 保存真实断点、待解问题和下一步，按配置整理笔记 |

主线只需要说一句“把这个问题单独开个问答任务”，不用复制长语境。相关问题可复用问答任务；明确要求新任务时创建新的问答目标。详细记录在问题页和答案页，可从 dashboard 回看。

没有任务工具时，Skill 会保存上下文包并给一句带路径的启动消息，说明需要你手动开任务。它不能替换侧边栏功能，也不能知道尚未提交或完全无来源的问题。

## 维护命令（由代理执行）

```text
python <skill-dir>/scripts/learning_state.py resume --repo <repo> --workstream mainline
python <skill-dir>/scripts/learning_state.py checkpoint --repo <repo> --workstream mainline --resume-at "<code location>" --next-step "<next>" --explanation "<relevant teaching passage>"
python <skill-dir>/scripts/learning_state.py prepare-qa --repo <repo> --source mainline --id q-context --packet <input.json>
python <skill-dir>/scripts/learning_state.py bind-thread --repo <repo> --workstream <qa-id> --thread <actual-thread-id> --host <actual-host-id>
```

`resume` 是只读入口：未规划时返回发现/直接答疑，已有草案时返回待确认/直接答疑，已激活时返回恢复上下文。它不会自动建课程。问答包格式与工具衔接见 [question-handoff](question-handoff.md)。

笔记路径先用 `resolve-notes` 确认，写入后用 `index-note` 更新索引。对主线有用的结论通过 `publish` / `sync` 分享；不要同步整个问答记录。

查看、诊断与旧状态迁移：

```text
python <skill-dir>/scripts/learning_state.py doctor --repo <repo>
python <skill-dir>/scripts/learning_state.py dashboard --repo <repo>
python <skill-dir>/scripts/learning_state.py archive --repo <repo>
python <skill-dir>/scripts/learning_state.py migrate-v1 --repo <repo>
```

v2 直接兼容；v1 迁移前需明确说明并获得许可，脚本会归档旧状态，迁移后运行 doctor。不要为了一个问题自动迁移或重建课程。完整字段见 [state-model](state-model.md)，异常恢复见 [notes-and-operations](notes-and-operations.md)。
