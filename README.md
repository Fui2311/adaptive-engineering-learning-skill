# Adaptive Engineering Learning Skill

一个面向 Codex 的项目制工程学习系统：先分析真实代码库，再由学习者确认路线；学习可以分布在主线、问答、练习、Review、Debug、结对和功能实现等多个 Codex 任务窗口中，并通过项目内状态与 Markdown 交接文件恢复和同步。

```text
项目发现
→ 候选学习路线
→ 用户明确确认
→ 主线章节 + 侧线 Workstream
→ 共享问答、发现、阻塞与学习者证据
→ Markdown Dashboard / Handoff / Notes
→ 可中断、可迁移、可审计
```

## 为什么是“学习系统”

普通代码问答很容易丢失三个重要东西：

- 项目到底有哪些内容值得学
- 多次对话之间学到哪里、为什么停下
- 问答、练习和实现窗口产生的结论如何回到主线

本 Skill 把这些概念分开：

```text
plan       = 已确认的课程路线
task       = 章节、练习、Review、Debug 或功能目标
workstream = 一个 Codex 任务窗口的角色和续接位置
shared     = 多窗口之间已接受的结论、问题、阻塞和证据
notes      = 长期复习价值的稳定知识
```

## 核心能力

- 根据仓库真实入口、调用链、测试、部署和实现质量生成学习地图。
- 候选计划必须经用户明确确认，不能静默变成正式课程。
- 支持在同一项目下打开多个 Codex 任务窗口：
  - `mainline`：主线章节推进
  - `qa-*`：独立问答
  - `exercise-*`：练习
  - `review-*`：代码审查
  - `debug-*`：证据驱动排障
  - `pair-*`：结对实现
  - `impl-*`：明确授权的功能实现
- 每个窗口拥有独立 JSON 状态和 Markdown 交接卡，避免互相覆盖。
- 通过 append-only inbox 与确定性 `sync` 共享部分状态。
- 计划变更始终排队等待确认；Q&A 窗口不能直接推进主线。
- `mastered` 默认要求学习者本人产生的证据。
- 支持项目内 Markdown 与外部 Obsidian 笔记。
- 提供 schema v1 → v2 的先归档、可恢复迁移。
- 状态写入使用项目级互斥锁和原子替换，适合多个 Codex 任务共享同一工作区。

## 文档导航

- [项目介绍](INTRODUCTION.md)
- [状态设计原理](docs/state-design-principles.md)
- [原 Prompt 诊断与架构取舍](docs/adaptive-engineering-learning-design.md)
- [验证场景与结果](docs/validation-scenarios.md)

## 仓库结构

```text
adaptive-engineering-learning-skill/
├─ README.md
├─ INTRODUCTION.md
├─ AGENTS.md
├─ .agents/
│  └─ skills/adaptive-engineering-learning/   # Codex 仓库级可发现副本
├─ skill-src/
│  └─ adaptive-engineering-learning/          # 可编辑源
│     ├─ SKILL.md
│     ├─ agents/openai.yaml
│     ├─ references/
│     ├─ assets/
│     └─ scripts/
└─ docs/
```

## 安装

克隆仓库：

```text
git clone https://github.com/Fui2311/adaptive-engineering-learning-skill.git
```

### 项目级安装

把 `.agents/skills/adaptive-engineering-learning/` 复制到目标项目的同名位置：

```text
your-project/
└─ .agents/
   └─ skills/
      └─ adaptive-engineering-learning/
         └─ SKILL.md
```

### 个人安装

把 `skill-src/adaptive-engineering-learning/` 复制到 Codex 个人 skills 目录，例如：

```text
$CODEX_HOME/skills/adaptive-engineering-learning/
```

Codex 通常会自动发现更新；未显示时重启 Codex。

## 快速开始

第一次使用：

```text
$adaptive-engineering-learning 分析这个项目适合学习什么，先给候选计划，不要直接开始。
```

确认路线：

```text
确认这个计划，但先学请求调用链，把数据库放到后面。
```

之后 Skill 会创建 `mainline` workstream 和第一批章节任务。

## 多窗口学习

### 主线窗口

```text
$adaptive-engineering-learning 继续 mainline，从上次的代码位置开始。
```

### 问答窗口

新开一个 Codex 任务：

```text
$adaptive-engineering-learning 这是 qa-auth 窗口，关联当前请求链章节。只处理认证问题，不推进主线；把可复用结论同步回去。
```

### 练习和 Review

```text
$adaptive-engineering-learning 这是 exercise-cache 窗口，关联缓存练习，只给分级提示。
```

```text
$adaptive-engineering-learning 这是 review-cache 窗口，检查缓存练习，让我先改重要问题。
```

### Debug

```text
$adaptive-engineering-learning 这是 debug-timeout 窗口，按复现—证据—假设—验证排查超时，并同步验证过的根因。
```

### 功能实现

```text
$adaptive-engineering-learning 这是 impl-auth 窗口。我明确授权你在约定文件内完成认证中间件，并解释关键决策。
```

实现窗口必须保存明确授权。Codex 完成代码不代表学习者掌握。

## 项目学习状态

激活后的 v2 布局：

```text
.learning/
├─ config.json
├─ project.json
├─ project-map.md
├─ plan.json
├─ workspace.json
├─ shared.json
├─ dashboard.md
├─ tasks/
├─ workstreams/
├─ inbox/
├─ handoffs/
├─ notes-index.json
├─ notes/
└─ sessions/
```

重点文件：

- `dashboard.md`：所有章节/任务、窗口、共享问题与阻塞的总览。
- `handoffs/<id>.md`：某个窗口的精确续接卡。
- `tasks/<id>.json`：每个学习任务的权威进度。
- `workstreams/<id>.json`：每个 Codex 窗口的权威状态。

Dashboard 和 handoff 是脚本生成的 Markdown 快照，不是机器状态真源。

## 常用状态命令

```text
python <skill-dir>/scripts/learning_state.py inspect --repo <repo>
python <skill-dir>/scripts/learning_state.py doctor --repo <repo>
python <skill-dir>/scripts/learning_state.py show --repo <repo>
python <skill-dir>/scripts/learning_state.py context --repo <repo> --workstream mainline
python <skill-dir>/scripts/learning_state.py sync --repo <repo> --workstream mainline
python <skill-dir>/scripts/learning_state.py dashboard --repo <repo>
```

查看完整命令面：

```text
python <skill-dir>/scripts/learning_state.py --help
```

## 跨窗口共享规则

侧线窗口通过 `publish` 发送：

- 问题
- 带源码证据的答案/发现
- 阻塞
- 学习者证据
- 计划变更建议

`sync` 会：

- 合并非冲突信息
- 把学习者证据加入相关任务，但不改变状态
- 把计划变更排队为 `needs_confirmation`
- 永不自动标记 `mastered`

## 从 v1 迁移

如果已有项目使用旧版单一 `progress.json`：

```text
python <skill-dir>/scripts/learning_state.py migrate-v1 --repo <repo>
python <skill-dir>/scripts/learning_state.py doctor --repo <repo>
```

迁移会先把完整状态复制到 `.learning-archives/`，再拆分任务、创建主线 workstream，并把旧进度保存在 `.learning/legacy/progress-v1.json`。

## 验证

状态行为测试：

```text
python skill-src/adaptive-engineering-learning/scripts/test_learning_state.py
```

官方 Skill 结构校验（Windows 建议显式启用 UTF-8）：

```powershell
$env:PYTHONUTF8 = "1"
python E:/codex/home/skills/.system/skill-creator/scripts/quick_validate.py `
  skill-src/adaptive-engineering-learning
```

测试覆盖确认门、多窗口隔离、跨窗口同步、计划变更排队、学习者证据、实现授权、Markdown 交接、外部笔记回退和 v1 迁移。

## 能力边界

- Skill 是交互式工作流，不是后台常驻服务。
- 多窗口协作依赖同一项目文件系统，不提供跨设备实时数据库同步。
- Codex 无法自动获得稳定的当前任务窗口 ID，因此侧线窗口应使用明确名称。
- 互斥锁降低并发写冲突，但不能替代人工解决复杂的手工 JSON 三方合并。
- 学习质量仍取决于可访问源码、可运行环境与真实证据。
