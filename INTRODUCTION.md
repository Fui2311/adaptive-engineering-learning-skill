# 项目介绍

## 为什么需要这个 Skill

从 GitHub 克隆一个项目后，普通的代码问答往往存在两个极端：

- 从入口开始逐行翻译源码，但没有形成整体工程理解。
- 根据通用技术栈生成固定课程，却没有判断仓库是否真正使用这些技术、实现质量是否值得学习。

`adaptive-engineering-learning` 希望解决的是另一类问题：

> 让 Codex 先理解真实代码库，再和学习者共同确定值得学习的方向，并把源码阅读、练习、Review、Debug、进度和笔记组织成可以中断恢复的长期过程。

## 核心目标

1. 学习内容来自当前仓库，而不是固定课程模板。
2. Codex 可以主动分析和提出路线，但不能未经确认替用户决定完整课程。
3. 项目事实、候选计划、正式计划、当前任务和掌握证据彼此分离。
4. 学习过程可以跨多次对话恢复，不依赖单次上下文记忆。
5. 项目中的不合理实现会被明确标记，而不是被包装成最佳实践。
6. 笔记只沉淀经过验证、具有长期复用价值的内容。

## 完整学习闭环

```text
分析项目
→ 识别可学习内容
→ 判断学习价值与前置知识
→ 生成候选学习计划
→ 等待用户确认
→ 初始化正式任务和进度
→ 分阶段阅读源码
→ 回答上下文问题
→ 完成练习、Review 或 Debug
→ 更新掌握证据与进度
→ 更新结构化笔记
→ 推荐下一步
```

首次启动必须进入 Project Discovery。Skill 会先检查已有状态、README、目录结构、入口、调用链、依赖、测试和部署方式，再输出项目学习地图。

## 不做什么

该 Skill 不会：

- 因为某项技术出现在依赖文件中就自动把它加入核心课程。
- 为普通单体项目强行设计微服务、消息队列或复杂架构。
- 在没有用户确认时把候选计划变成正式任务。
- 因为学习者阅读过一次源码就标记为 `mastered`。
- 默认接管业务代码开发。
- 把 Codex 代写的代码当作学习者的掌握证据。
- 为每个简单问题创建一篇笔记。

## 最小架构

```text
主 Skill
├─ Project Discovery 与候选计划
├─ 源码教学、问答、练习、Review、Debug
├─ 配置、计划、任务和进度模型
├─ 笔记、Session、Obsidian 路径与迁移
└─ 确定性状态管理脚本
```

当前采用“一个主 Skill + 按需加载的 references + 标准库 Python 脚本”，而不是拆成大量相互依赖的子 Skill。

详细规则按需放在 references 中，可以减少主 `SKILL.md` 的上下文占用，也避免依赖当前 Codex 并未提供的嵌套 Skill 调用协议。

## 内容分区

### 给 Codex 执行的内容

位于：

```text
.agents/skills/adaptive-engineering-learning/
```

包括主 `SKILL.md`、工作流 references、状态脚本、示例和模板。

### 给使用者和维护者阅读的内容

位于仓库根目录和 `docs/`：

- `README.md`：安装、快速开始和常用操作。
- `INTRODUCTION.md`：背景、目标、架构和边界。
- `docs/state-design-principles.md`：状态分层与生命周期原理。
- `docs/adaptive-engineering-learning-design.md`：原 Prompt 诊断与架构取舍。
- `docs/validation-scenarios.md`：行为场景和验证结果。

## 适用场景

它适合：

- 希望通过真实 Go、Java、Python、前端或 AI 工程项目学习工程实践。
- 需要梳理请求调用链、数据流、模块边界或架构取舍。
- 希望 Codex 提供引导式练习，而不是直接代写完整答案。
- 希望学习过程能够暂停、继续，并维护 Markdown 或 Obsidian 笔记。

它不限定技术栈。Go、Gin、GORM、数据库、Redis、Docker、RAG、Agent Workflow 等只是可能出现的学习方向，是否进入计划由当前仓库的真实内容决定。

## 进一步阅读

- [返回 README](README.md)
- [状态设计原理](docs/state-design-principles.md)
- [原 Prompt 诊断与最终架构](docs/adaptive-engineering-learning-design.md)
- [验证场景与结果](docs/validation-scenarios.md)
