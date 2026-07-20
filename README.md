# Adaptive Engineering Learning Skill

一套面向 Codex 的自适应工程学习 Skill。它会先分析真实代码库，再根据项目内容、学习目标和用户基础提出候选学习计划；只有用户明确确认后，才会初始化正式课程、任务、进度和笔记。

它适合这样的使用方式：

```text
克隆一个 GitHub 项目
→ 让 Codex 分析项目的学习价值
→ 查看并调整候选计划
→ 明确确认计划
→ 分阶段阅读源码、练习、Review 和 Debug
→ 持续维护进度与 Markdown / Obsidian 笔记
```

## 核心特点

- 基于仓库真实内容生成学习路线，不使用固定课程模板。
- 首次启动先进入 Project Discovery，不立即逐行讲解代码。
- 严格区分候选计划、正式计划、当前任务和已经掌握的内容。
- 候选计划必须经过用户明确确认才能变为 `active`。
- 掌握状态默认需要学习者提供实际证据。
- 支持中断后继续，不依赖单次对话记忆。
- 支持导师、练习、Review、Debug、结对和代实现模式。
- 自动笔记只记录经过验证、具有长期复用价值的内容。
- 默认使用项目内笔记，也支持外部 Obsidian Vault。
- 不把质量较差、过时或不合理的项目实现当作标准答案。
- 默认不修改业务代码，也不自动接管项目开发。

## Skill 架构

```text
adaptive-engineering-learning/
├─ SKILL.md
├─ agents/
│  └─ openai.yaml
├─ references/
│  ├─ discovery-and-planning.md
│  ├─ learning-workflows.md
│  ├─ state-model.md
│  ├─ notes-and-operations.md
│  └─ usage.md
├─ scripts/
│  ├─ learning_state.py
│  └─ test_learning_state.py
└─ assets/
   ├─ examples/
   │  ├─ minimal-config.json
   │  └─ minimal-session.json
   └─ templates/
      ├─ concept-note.md
      └─ debug-note.md
```

采用“一个主 Skill + 按需加载的工作流参考 + 确定性状态脚本”，不依赖不存在的嵌套 Skill 编排能力。

## 安装

本仓库根目录就是完整 Skill 包，可以直接克隆到 Codex 的 Skill 发现目录。Codex 会扫描仓库中从当前工作目录到仓库根目录之间的 `.agents/skills`。

### 方式一：安装到目标项目

在目标项目根目录运行：

```text
git clone https://github.com/Fui2311/adaptive-engineering-learning-skill.git .agents/skills/adaptive-engineering-learning
```

最终结构为：

```text
your-project/
└─ .agents/
   └─ skills/
      └─ adaptive-engineering-learning/
         └─ SKILL.md
```

### 方式二：安装为个人 Skill

macOS / Linux：

```text
git clone https://github.com/Fui2311/adaptive-engineering-learning-skill.git ~/.agents/skills/adaptive-engineering-learning
```

Windows PowerShell：

```text
git clone https://github.com/Fui2311/adaptive-engineering-learning-skill.git "$HOME/.agents/skills/adaptive-engineering-learning"
```

Codex 通常会自动发现新增或更新的 Skill；如果没有显示，请重启 Codex。

## 快速开始

显式调用：

```text
$adaptive-engineering-learning 分析一下这个项目适合学习什么，先给我计划，不要直接开始。
```

也可以直接使用自然语言：

```text
我想通过这个仓库学习后端，先扫描项目再给我学习计划。
```

首次分析会：

1. 检查 `AGENTS.md`、已有 Skill、学习状态、笔记和 Git 改动。
2. 扫描 README、目录结构、入口、调用链、依赖、测试和部署方式。
3. 输出项目学习地图和实现质量判断。
4. 生成状态为 `proposed` 的候选学习计划。
5. 等待用户确认，不创建正式进度，也不开始长篇教学。

## 确认或调整计划

例如：

```text
计划可以，但把数据库放到后面，先从请求调用链开始。
```

Skill 会保存调整、递增计划版本，然后在明确确认后：

- 把计划状态改为 `active`。
- 创建 `progress.json`。
- 初始化适量任务。
- 只指定第一个当前任务，不一次讲完整个项目。

没有明确确认时，状态脚本会拒绝激活计划。

## 继续学习

```text
继续上次的内容。
```

Skill 会读取当前任务、代码位置、未解决问题和下一步，不会在项目没有明显变化时重新扫描整个仓库。

其他常用入口：

```text
带我看这个模块。
这个请求是怎么走的？
为什么这里需要中间件？
给我一个小练习，只给提示。
我写完了，帮我 Review，但不要直接改代码。
今天先到这里。
看看当前进度。
```

## 学习模式

| 模式 | 配置值 | 行为 |
| --- | --- | --- |
| 导师模式 | `mentor` | 默认模式，以讲解、源码阅读和引导提问为主 |
| 练习模式 | `exercise` | 提供任务、边界、验收标准和分级提示 |
| Review 模式 | `review` | 分类指出问题，默认让学习者先修改 |
| Debug 模式 | `debug` | 以复现、证据、假设和验证为中心 |
| 结对模式 | `pair` | 与学习者共同完成局部实现并解释决策 |
| 代实现模式 | `implementation` | 只有用户明确要求时才完整实现 |

切换示例：

```text
切换到 Debug 模式。
```

Codex 代写的代码不会自动成为学习者的掌握证据。

## 持久化状态

默认在目标项目中使用：

```text
.learning/
├─ config.json
├─ project.json
├─ project-map.md
├─ plan.json
├─ progress.json
├─ notes-index.json
├─ notes/
└─ sessions/
```

各文件职责：

- `config.json`：学习偏好、权限、笔记路径和关注方向。
- `project.json`：最近一次项目扫描得到的仓库事实。
- `project-map.md`：面向学习者的项目学习地图。
- `plan.json`：候选或正式学习路线及版本记录。
- `progress.json`：当前阶段、任务、证据、问题和下一步。
- `notes-index.json`：笔记位置、类型和验证状态。
- `notes/`：稳定知识笔记。
- `sessions/`：精简学习会话日志。

配置和状态使用 JSON，便于脚本跨平台可靠解析和原子写入；知识笔记使用 Markdown，兼容普通编辑器和 Obsidian。

## Obsidian 配置

默认笔记位置：

```text
<repo>/.learning/notes
```

自定义路径示例：

```json
{
  "notes": {
    "location": "custom",
    "custom_path": "D:/Obsidian/MyVault/Engineering/ProjectName",
    "fallback_to_project": true,
    "namespace_by_project": false
  }
}
```

也可以直接说：

```text
把笔记放到 D:/Obsidian/MyVault/Engineering/ProjectName。
```

如果外部路径不存在、不可写或超出当前权限，Skill 会明确报告失败原因，并且只在配置允许时回退到项目内目录。

## 状态辅助脚本

脚本只负责确定性的状态转换，不负责替 Codex 分析或讲解仓库。

```text
python <skill-dir>/scripts/learning_state.py inspect --repo <repo>
python <skill-dir>/scripts/learning_state.py show --repo <repo>
python <skill-dir>/scripts/learning_state.py doctor --repo <repo>
python <skill-dir>/scripts/learning_state.py set-mode --repo <repo> --mode debug
python <skill-dir>/scripts/learning_state.py resolve-notes --repo <repo>
python <skill-dir>/scripts/learning_state.py archive --repo <repo>
```

执行以下命令查看全部子命令：

```text
python <skill-dir>/scripts/learning_state.py --help
```

## 重置与迁移

重置学习状态前先创建可恢复归档：

```text
python <skill-dir>/scripts/learning_state.py archive --repo <repo>
```

默认归档到：

```text
.learning-archives/<timestamp>/
```

归档命令只复制，不删除原状态。完整重置应在确认归档后把旧 `.learning/` 移到一旁，而不是直接递归删除。

迁移外部笔记时遵循：复制、校验、修改路径、验证访问、保留旧副本，直到用户确认清理。

## 验证

状态测试：

```text
python scripts/test_learning_state.py
```

当前测试覆盖：

- 候选计划不会创建正式进度。
- 激活必须具有明确确认记录。
- 继续学习读取已有任务而不重新扫描。
- 中途提问只更新当前任务。
- `mastered` 默认必须包含学习证据。
- Session 日志保持精简。
- 自定义笔记路径失败时正确回退或保留原配置。
- 首次提案不会覆盖已有用户配置。

当前结果：8 项测试全部通过，官方 `quick_validate.py` 校验通过。

## 仓库目录说明

本仓库是独立的 Skill 发布包，仓库根目录即 Skill 根目录。克隆到 `.agents/skills/adaptive-engineering-learning` 后即可被 Codex 发现，不包含原设计工作区、内部维护副本或项目过程文件。

## 能力边界

- Skill 是按交互触发的工作流，不是后台常驻服务。
- 它不能绕过 Codex 沙箱或操作系统文件权限。
- 它不会把仓库中出现的所有依赖都自动加入课程。
- 它不会把项目中的错误实现当作标准实践。
- 它不会在重新扫描后自动覆盖已经确认的计划。
- 它不会因为阅读过一次代码就把任务标记为 `mastered`。
- 真实教学质量仍取决于仓库源码、构建环境和可验证证据。
