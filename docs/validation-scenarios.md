# 验证场景

自动测试覆盖状态不变量和主要多窗口协作路径。自然语言教学质量还需要使用新鲜上下文进行前向测试。

## 1. 候选计划确认门

- `propose` 创建 config/project/plan。
- 断言不创建 workspace、task、workstream 或旧 `progress.json`。
- `activate` 拒绝空确认。

## 2. 主线激活

- 明确确认后创建一个 `mainline` workstream。
- 每个阶段创建一个 chapter task。
- 仅第一任务进入 `learning`。
- 生成 Dashboard 和主线 Handoff。

## 3. 多窗口隔离

- 打开 `qa-http` 后保存独立 resume point/code locations。
- 断言 `mainline` 的续接位置未被改写。
- Dashboard 同时显示两个窗口。

## 4. Q&A 权限边界

- Q&A 尝试直接将任务标为 mastered 时被拒绝。
- Q&A 只能 publish 问题、答案、发现、阻塞或证据候选。

## 5. 跨窗口问答同步

- Q&A 发布带源码的 verified answer。
- Q&A 发布 task question。
- Mainline `sync` 后答案进入 shared knowledge，问题进入 shared 和相关 task。
- 仅同步答案时不触碰关联 task revision，保持窄写入。

## 6. 纯共享答案的窄写入

- 只包含 answer/finding 的同步更新 shared/workspace/workstream。
- 不修改没有语义变化的关联 task，也不递增其 revision。

## 7. 计划变更排队

- 侧线发布 `plan_change`。
- `sync` 把 contribution 标记为 queued。
- `plan.json` 顺序不变。
- 输出明确 `plan_changes_auto_applied == false`。

## 8. 学习者证据跨窗口

- Q&A 发布 learner-originated evidence。
- `sync` 将证据加入 task，但保持原 task status。
- 主线显式判断后才能标记 mastered。

## 9. Codex-only 证据

- Codex 生成的实现/讲解即使作为 evidence 写入，也不能满足 learner-origin 要求。
- 无学习者证据的 mastered 被拒绝。

## 10. 独立功能任务和实现授权

- 创建 implementation task 时空确认被拒绝。
- 保存明确用户确认后可创建。
- implementation workstream 同样要求确认记录。

## 11. 紧凑上下文包

- `context --workstream qa-http` 只返回该窗口、attached task、相关 shared 项和 peer 摘要。
- 避免每次加载所有聊天历史。

## 12. Session 与 Handoff

- Session 日志写入 `sessions/<workstream>/`。
- resume point 和 next step 更新到该 workstream。
- Handoff Markdown 可直接恢复窗口。

## 13. 外部笔记路径

- 自定义路径缺失且允许 fallback 时返回明确原因并回退。
- 禁止 fallback 时配置写入失败，原配置保持不变。

## 14. Doctor

- 校验 plan/workspace version、task/workstream 引用、枚举、mastery evidence 和 inbox。
- 完整多窗口 fixture 返回 ok。

## 15. 并发写入锁

- 第一个 writer 持有项目锁时，第二个 writer 在超时后收到明确错误。
- 第二个 writer 不会删除第一个 writer 的锁。
- 第一个 writer 正常结束后锁被释放。

## 16. v1 → v2 迁移

- 迁移前完整归档。
- 旧 progress tasks 拆成 `tasks/*.json`。
- 创建 mainline workspace/workstream。
- 旧进度复制到 `legacy/progress-v1.json`。
- 根 `progress.json` 移除。
- 迁移后 `doctor` 通过。

## 运行命令

```text
python skill-src/adaptive-engineering-learning/scripts/test_learning_state.py
```

Skill 结构校验：

```text
PYTHONUTF8=1 python <skill-creator>/scripts/quick_validate.py \
  skill-src/adaptive-engineering-learning
```

Windows PowerShell 使用：

```powershell
$env:PYTHONUTF8 = "1"
python E:/codex/home/skills/.system/skill-creator/scripts/quick_validate.py `
  skill-src/adaptive-engineering-learning
```

## 当前结果

- 2026-07-30：16 项状态行为测试全部通过。
- 官方 `quick_validate.py` 应在 UTF-8 模式运行；Windows 默认 GBK 读取中文 UTF-8 Skill 可能报 `UnicodeDecodeError`。
- 发布前需要同步 `skill-src/` 与 `.agents/skills/`，再进行逐文件哈希比对。

## 独立前向测试

2026-07-30 使用三个隔离的 Tiny Token API 副本和三个无既有对话上下文的 Codex 任务验证：

1. **Project Discovery**
   - 生成基于真实 200/401/404 调用链的三阶段候选路线。
   - 只创建 config/project/project-map/plan。
   - 保持 `proposed`，没有创建任何 runtime state。

2. **Q&A Workstream**
   - 创建 `qa-auth`，回答认证异常与 HTTP 映射边界。
   - 发布带源码位置的 verified answer 并同步。
   - 主线 task status、evidence 和 mastery 保持不变。
   - 前向测试发现纯答案同步会无意义递增 task revision；实现已收紧为窄写入并增加独立回归。

3. **Implementation Workstream**
   - 在明确授权下创建 implementation task/workstream。
   - 实现 revoked token 的 401 行为并新增回归测试。
   - 4 项 fixture 测试通过。
   - 任务停在 `needs_review`，Codex 代码没有被记为学习者证据或 mastery。

三个场景的 `doctor` 均通过。
