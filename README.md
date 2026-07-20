# Adaptive Engineering Learning Skill

一套面向 Codex 的自适应工程学习 Skill。它会先分析真实代码库，再根据项目内容、学习目标和用户基础提出候选学习计划；只有用户明确确认后，才会初始化正式课程、任务、进度和笔记。

```text
分析项目
→ 生成项目学习地图
→ 提出候选计划
→ 等待用户确认
→ 推进源码学习、练习、Review 和 Debug
→ 维护进度与 Markdown / Obsidian 笔记
```

## 文档导航

- [项目介绍](INTRODUCTION.md)：背景、目标、整体架构、适用场景和能力边界。
- [状态设计原理](docs/state-design-principles.md)：状态分层、确认门、计划版本和掌握证据。
- [原 Prompt 诊断与架构取舍](docs/adaptive-engineering-learning-design.md)
- [验证场景与结果](docs/validation-scenarios.md)

## 核心特点

- 基于仓库真实内容生成学习路线，不写死统一课程。
- 首次启动先进入 Project Discovery，不立即逐行讲解源码。
- 严格区分候选计划、正式计划、当前任务和掌握证据。
- 候选计划必须由用户明确确认才能变为 `active`。
- 学习过程可以中断和恢复，不依赖单次对话记忆。
- 支持导师、练习、Review、Debug、结对和代实现模式。
- 自动笔记只记录已验证、具有长期价值的内容。
- 默认使用项目内 Markdown 笔记，也支持外部 Obsidian Vault。
- 不把质量较差、过时或不合理的项目实现当作标准答案。
- 默认不修改业务代码，也不自动接管项目开发。

## 仓库结构

```text
adaptive-engineering-learning-skill/
├─ README.md
├─ INTRODUCTION.md
├─ AGENTS.md
├─ .agents/
│  └─ skills/
│     └─ adaptive-engineering-learning/   # Codex 可发现副本
├─ skill-src/
│  └─ adaptive-engineering-learning/      # 可编辑源
└─ docs/
   ├─ state-design-principles.md
   ├─ adaptive-engineering-learning-design.md
   └─ validation-scenarios.md
```

Skill 内部采用“一个主 `SKILL.md` + 按需加载的 references + 标准库 Python 状态脚本”，不依赖不存在的嵌套 Skill 编排能力。

## 安装

Codex 会扫描仓库中从当前工作目录到仓库根目录之间的 `.agents/skills`。

### 方式一：安装到某个项目

先克隆本仓库：

```text
git clone https://github.com/Fui2311/adaptive-engineering-learning-skill.git
```

把其中的 Skill 目录复制到目标项目：

```text
adaptive-engineering-learning-skill/.agents/skills/adaptive-engineering-learning/
→ your-project/.agents/skills/adaptive-engineering-learning/
```

Windows PowerShell：

```powershell
New-Item -ItemType Directory -Force "D:/Code/your-project/.agents/skills"
Copy-Item -Recurse -Force `
  "./adaptive-engineering-learning-skill/.agents/skills/adaptive-engineering-learning" `
  "D:/Code/your-project/.agents/skills/"
```

macOS / Linux：

```bash
mkdir -p /path/to/your-project/.agents/skills
cp -R \
  ./adaptive-engineering-learning-skill/.agents/skills/adaptive-engineering-learning \
  /path/to/your-project/.agents/skills/
```

最终结构应为：

```text
your-project/
└─ .agents/
   └─ skills/
      └─ adaptive-engineering-learning/
         └─ SKILL.md
```

### 方式二：安装为个人 Skill

将同一目录复制到：

```text
~/.agents/skills/adaptive-engineering-learning/
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

## 确认与继续

确认或调整计划：

```text
计划可以，但把数据库放到后面，先从请求调用链开始。
```

只有明确确认后，Skill 才会把计划变为 `active`、创建 `progress.json` 并指定第一个任务。

继续学习：

```text
继续上次的内容。
```

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

Codex 代写的代码不会自动成为学习者的掌握证据。

## 学习状态与笔记

目标项目默认使用：

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

默认笔记位置为 `<repo>/.learning/notes`。可以通过 `notes.custom_path` 指向外部 Obsidian Vault。外部路径不可访问时，Skill 会明确报告原因，并且只在配置允许时回退到项目内目录。

详细状态职责和生命周期见 [状态设计原理](docs/state-design-principles.md)。

## 验证

```text
python skill-src/adaptive-engineering-learning/scripts/test_learning_state.py
```

当前结果：

- 8 项状态行为测试全部通过。
- 官方 `skill-creator/scripts/quick_validate.py` 校验通过。
- 可编辑源与 `.agents/skills` 可发现副本保持一致。

## 能力边界

- Skill 是按交互触发的工作流，不是后台常驻服务。
- 它不能绕过 Codex 沙箱或操作系统文件权限。
- 它不会把仓库中出现的所有依赖都自动加入课程。
- 它不会在重新扫描后自动覆盖已经确认的计划。
- 它不会因为阅读过一次代码就把任务标记为 `mastered`。
- 真实教学质量仍取决于仓库源码、构建环境和可验证证据。
