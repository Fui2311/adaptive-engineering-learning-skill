# 使用说明

可以显式输入 `$adaptive-engineering-learning` 调用本 Skill，也可以直接使用符合其职责描述的自然语言。

## 首次分析项目

示例：

- “分析一下这个项目适合学习什么，先给我计划，不要直接开始。”
- “我想通过这个仓库学习后端，先扫描再规划。”

Skill 会先检查已有状态和仓库证据，然后输出项目学习地图与候选路线。此时计划保持为 `proposed`，不会创建 `progress.json`，也不会直接开始长篇教学。

## 确认或调整计划

示例：

- “计划可以，但把数据库放到后面，先从请求调用链开始。”
- “暂时不要练习，只学习框架机制。”

Skill 会先保存用户调整。只有获得明确确认后，才会激活计划、创建进度并指定第一个学习任务。

## 继续学习与查看状态

- “继续上次的内容。”：读取 `progress.json`，从当前任务和代码位置继续。
- “看看当前进度。”：汇总正式计划、掌握证据、阻塞问题、未解决问题和下一步。
- “今天先到这里。”：执行精简的 Session 收尾，并只更新必要的状态和笔记。

等价的辅助命令：

```text
python <skill-dir>/scripts/learning_state.py show --repo <repo>
python <skill-dir>/scripts/learning_state.py doctor --repo <repo>
```

## 切换学习模式

可以直接说“切换到练习、Review、Debug、结对或代实现模式”，也可以运行：

```text
python <skill-dir>/scripts/learning_state.py set-mode --repo <repo> --mode exercise
```

有效模式值：

- `mentor`：导师模式，默认值。
- `exercise`：练习模式。
- `review`：代码审查模式。
- `debug`：证据驱动的调试模式。
- `pair`：结对模式。
- `implementation`：代实现模式，只能由用户明确启用。

## 配置笔记位置

默认笔记目录：`<repo>/.learning/notes`。

自定义 Obsidian 路径示例：

```text
python <skill-dir>/scripts/learning_state.py set-notes --repo <repo> --location custom --path "D:/Obsidian/MyVault/Engineering/项目名称" --fallback --no-namespace
python <skill-dir>/scripts/learning_state.py resolve-notes --repo <repo>
```

若要关闭全部笔记，将 `notes.enabled` 设为 `false`。若只想关闭 Session 日志，将 `notes.session_logs` 设为 `false`。还可以在 `notes.categories` 中单独关闭某类笔记。关闭功能不会删除已有文件。

## 重新扫描、归档、重置与迁移

- “重新扫描项目，但不要改当前计划。”：重新执行项目发现并生成差异报告，保留当前正式计划。
- 重置前先运行 `archive`：它只复制状态，不删除任何内容。
- 重置时应明确提出要求、验证归档，然后把旧 `.learning/` 移到一旁，再重新开始 Project Discovery。
- 迁移笔记时先复制并验证，再修改 `notes.custom_path`，运行 `resolve-notes`，旧副本应保留到用户确认清理为止。

```text
python <skill-dir>/scripts/learning_state.py archive --repo <repo>
```

## 能力限制

本 Skill 是按交互触发的工作流，不是后台常驻服务。它无法在两次交互之间持续运行，也无法绕过外部路径权限。当前 Codex 没有可依赖的嵌套 Skill 编排 API，因此由主 Skill 读取工作流参考并调用确定性脚本。代码库分析和教学质量仍取决于可访问的源码、工具权限与可验证证据。
