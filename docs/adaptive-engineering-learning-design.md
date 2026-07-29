# 自适应工程学习 Skill：诊断与架构取舍

## 原始学习 Prompt 中应保留的部分

- 以“为什么、替代方案和 trade-off”为教学核心。
- 默认不代写核心业务代码，强调工程判断和生产级边界。
- 主动识别过度抽象、假微服务、无意义 interface 和不合理分层。
- Review、Debug、技术选型和可维护性意识进入长期工作流。
- AI 工程等方向只有在仓库真实涉及时才进入学习地图。
- 学习计划必须适配项目，而不是固定 Phase 1–6。

## 需要收敛的部分

- “不要代写”“解释为什么”“避免过度设计”重复出现时，只保留核心硬边界。
- “经常反问”容易制造审问式体验，改为只在需要掌握证据时提出高价值问题。
- “每次重要交互都写笔记”会造成文件爆炸，改为价值判断后再沉淀。
- Debug 不能永远禁止修复；证据成立且用户进入 pair/implementation 后可以实现。
- “工业界通常如何处理”不应暗示唯一标准，应结合规模和约束讨论。

## v1 的正确基础

第一版采用：

```text
一个主 SKILL.md
+ 按需 references
+ 标准库 Python 状态脚本
+ 项目内 .learning/
```

这是正确方向，因为：

- 不依赖不存在的 Skill-to-Skill 编排协议。
- 主 SKILL 保持精简。
- JSON 状态可校验和原子更新。
- Markdown 知识适合人工维护。
- `proposed` / `active` 确认门和 mastery evidence 可以确定性执行。

## v1 的限制

v1 把所有运行进度放在一个 `progress.json`：

```text
current_task_id
current_code_locations
tasks
questions
blockers
next_step
```

当学习仅在一个窗口顺序推进时，这很简单。但用户实际场景包含：

- 主线学习窗口
- 临时或长期 Q&A 窗口
- 不同章节并行学习
- 练习、Review、Debug 分开
- 一个或多个功能实现窗口

这些窗口共享一个 `current_task_id` 会互相争夺“当前”，共享一份 task map 会扩大写冲突；仅靠 `os.replace` 无法防止语义覆盖。

## v2 的核心重构

### 1. Task / Workstream 分离

```text
task       = 要学/要做什么
workstream = 哪个 Codex 窗口在做
```

这使同一章节可以被多个窗口引用，又不会把窗口完成误判为学习掌握。

### 2. 拆分写入所有权

```text
tasks/<id>.json
workstreams/<id>.json
inbox/<id>.json
workspace.json
shared.json
```

每个窗口默认只更新自己的 workstream；task 更新受角色和 attachment 限制。

### 3. Append-only Inbox

侧线不直接写共享真源，而是发布独立 contribution：

```text
publish
→ inbox/<unique-id>.json
→ sync
→ shared/task
```

这样可以：

- 降低两个窗口写同一文件的概率
- 对贡献进行类型校验
- 为计划变更设置单独确认门
- 保留来源、任务和 workstream

### 4. 项目级互斥锁

所有变更命令通过 `.state.lock` 串行化，并在锁内重新读取状态。脚本拒绝自动删除锁，避免误伤仍在写入的 Codex 任务。

### 5. Markdown 恢复界面

用户要求跨任务快速恢复，因此由脚本生成：

- `dashboard.md`
- `handoffs/<workstream>.md`
- `sessions/<workstream>/*.md`

它们不承担权威状态，避免 JSON/Markdown 双真源。

### 6. 更严格的 mastery

v1 要求 evidence；v2 默认进一步要求至少一条 `learner_originated` evidence。Codex 的讲解和实现不会再被误判为学习者掌握。

### 7. 可恢复迁移

`migrate-v1` 先完整归档，再拆分状态，并保留旧进度副本。迁移不推断新证据。

## 规则归属

| 内容 | 归属 |
| --- | --- |
| 意图路由、确认门、最小动作、模式边界 | `SKILL.md` |
| 发现/计划 | `references/discovery-and-planning.md` |
| 教学/问答/练习/Review/Debug | `references/learning-workflows.md` |
| 多窗口权限、发布、同步、交接 | `references/multi-workstream-coordination.md` |
| Schema、所有权、不变量、迁移 | `references/state-model.md` |
| 笔记、Session、路径和恢复 | `references/notes-and-operations.md` |
| 用户命令示例 | `references/usage.md` |
| 确定性写入和校验 | `scripts/learning_state.py` |
| 人类可维护知识 | `.learning/notes/` |

## 主要失效模式及应对

| 失效模式 | 应对 |
| --- | --- |
| 依赖出现某技术就强行开课 | 要求真实调用位置和学习价值证据 |
| 自动计划直接变正式课程 | `proposed` / `active` 分离 |
| 读过一次就 mastered | evidence + learner origin |
| 重新扫描覆盖正式计划 | 只更新项目事实，计划另行确认 |
| Q&A 改掉主线进度 | Q&A 禁止直接更新 task status |
| 两个窗口覆盖 current task | task/workstream 分离 |
| 侧线直接改共享真源 | append-only inbox + sync |
| 计划建议自动生效 | plan change 永远 queued |
| Markdown 与 JSON 不一致 | Dashboard/Handoff 明确为派生视图 |
| 崩溃后随意删锁 | 超时报告 metadata，不自动删除 |
| 自动笔记造成文件爆炸 | 先判断稳定性、验证和复用价值 |
| 外部 Vault 写入误报 | 显式 resolve/fallback 原因 |

## 为什么不引入数据库或第三方依赖

目标项目可能运行在 Windows、macOS、Linux，也可能没有 Python 包管理环境。使用标准库 JSON、原子替换、独占锁文件和分文件所有权，可以在不污染目标项目的前提下覆盖主要协作场景。

代价是：

- 不提供数据库级多文件事务
- 不提供跨设备实时同步
- 复杂手工冲突仍需人工恢复

对于个人项目制学习，这个取舍比引入常驻服务或数据库更合适。
