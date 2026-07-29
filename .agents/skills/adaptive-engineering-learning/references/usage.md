# 使用说明

可以显式输入 `$adaptive-engineering-learning`，也可以直接使用符合其职责的自然语言。

## 首次分析项目

示例：

- “分析这个项目适合学习什么，先给计划，不要直接开始。”
- “我想通过这个仓库学习后端，先扫描再规划。”

Skill 会检查已有状态和仓库证据，输出项目学习地图与候选路线。此时计划保持 `proposed`，不会创建正式任务、workstream 或进度，也不会直接开始长篇教学。

## 确认或调整计划

示例：

- “计划可以，但把数据库放到后面，先从请求调用链开始。”
- “确认这个路线，暂时关闭练习。”

只有明确确认后，Skill 才会激活计划，创建章节任务、`mainline` workstream、Dashboard 和主线交接卡。

```text
python <skill-dir>/scripts/learning_state.py activate \
  --repo <repo> \
  --confirmation "用户确认先学请求调用链，数据库后置"
```

## 主线学习窗口

在主线 Codex 任务中说：

- “继续主线学习。”
- “从上次停下的位置继续。”
- “查看主线进度。”

Skill 会同步共享信息，再读取主线的紧凑上下文：

```text
python <skill-dir>/scripts/learning_state.py sync --repo <repo> --workstream mainline
python <skill-dir>/scripts/learning_state.py context --repo <repo> --workstream mainline
```

主线负责章节推进、主任务切换、掌握判断和计划级决策。

## 独立问答窗口

新开一个 Codex 任务后，可以说：

```text
$adaptive-engineering-learning 这是 qa-auth 问答窗口，关联当前请求链章节。只回答认证问题，不推进主线；把可复用结论同步回去。
```

首次会创建：

```text
python <skill-dir>/scripts/learning_state.py open-workstream \
  --repo <repo> \
  --id qa-auth \
  --kind qa \
  --title "认证问答" \
  --task request-flow-chapter \
  --focus "解决认证问题，不改变主线进度"
```

问答窗口不能直接修改任务状态。它通过 `publish` 提交问题、带源码位置的答案、发现、阻塞或学习者证据，再由 `sync` 合并。

## 练习、Review、Debug 和实现窗口

可以为同一项目并行打开：

- `exercise-cache`：缓存练习
- `review-cache`：检查练习实现
- `debug-timeout`：超时问题排查
- `impl-auth`：经明确授权的认证功能实现

示例请求：

```text
$adaptive-engineering-learning 这是 exercise-cache 窗口。关联缓存练习任务，只给分级提示，完成后保存交接状态。
```

```text
$adaptive-engineering-learning 这是 debug-timeout 窗口。按证据链排查超时，把验证过的根因同步给主线。
```

实现窗口必须有明确授权：

```text
$adaptive-engineering-learning 这是 impl-auth 实现窗口。我明确授权你在约定文件内完成认证中间件，同时解释每个关键决策。
```

Skill 会把这段授权摘要记录在实现任务/workstream 中。Codex 写完代码不等于学习者已经掌握。

## 创建独立学习任务

当一项练习、Debug 或功能实现有独立目标和完成条件时，创建任务：

```text
python <skill-dir>/scripts/learning_state.py create-task \
  --repo <repo> \
  --workstream mainline \
  --id exercise-auth-errors \
  --stage request-flow \
  --kind exercise \
  --title "认证错误映射练习" \
  --objective "实现并解释认证失败的 HTTP 映射" \
  --criterion "测试通过" \
  --criterion "学习者解释每个状态码选择"
```

短问题不需要创建独立任务。

## 跨窗口同步

发布一个已验证答案：

```text
python <skill-dir>/scripts/learning_state.py publish \
  --repo <repo> \
  --workstream qa-auth \
  --kind answer \
  --task request-flow-chapter \
  --summary "过期 Token 在进入 Handler 前被认证中间件拒绝" \
  --verification verified \
  --source internal/http/auth.go:47
```

合并共享信息：

```text
python <skill-dir>/scripts/learning_state.py sync --repo <repo> --workstream mainline
```

同步会自动合并不冲突的问答、发现、阻塞和学习者证据，但：

- 不自动标记 `mastered`
- 不自动调整计划
- 所有计划变更请求保持待确认

## 查看总览和窗口状态

项目级 Markdown 总览：

```text
<repo>/.learning/dashboard.md
```

某个窗口的 Markdown 交接卡：

```text
<repo>/.learning/handoffs/qa-auth.md
```

机器状态与紧凑上下文：

```text
python <skill-dir>/scripts/learning_state.py show --repo <repo>
python <skill-dir>/scripts/learning_state.py context --repo <repo> --workstream qa-auth
python <skill-dir>/scripts/learning_state.py doctor --repo <repo>
```

Dashboard 和 handoff 是脚本生成的视图；不要在其中手工维护权威状态。

## 暂停与结束

在某个窗口说“今天先到这里”，Skill 会：

1. 保存精确续接位置和下一步
2. 发布可复用的结论、问题、阻塞或证据
3. 按需写一份精简 Session 日志
4. 更新该窗口的 Markdown 交接卡

不会因为结束当天学习就自动完成任务或标记掌握。

## 配置笔记位置

默认笔记目录：`<repo>/.learning/notes`。

```text
python <skill-dir>/scripts/learning_state.py set-notes \
  --repo <repo> \
  --location custom \
  --path "D:/Obsidian/MyVault/Engineering/项目名称" \
  --fallback \
  --no-namespace
```

外部路径不可访问时，Skill 会报告原因；只有允许 fallback 时才回退项目目录。

## 从旧版迁移

若 `inspect` 显示 schema v1，先查看迁移说明并确认。然后运行：

```text
python <skill-dir>/scripts/learning_state.py migrate-v1 --repo <repo>
python <skill-dir>/scripts/learning_state.py doctor --repo <repo>
```

迁移会先完整归档，把旧 `progress.json` 拆成独立任务文件，创建主线 workstream，并保留旧进度副本。

## 能力限制

- Skill 是按交互触发的工作流，不是后台服务。
- 多个 Codex 任务通过共享文件和互斥锁协作，不是实时数据库。
- 它不能绕过文件系统权限，也不能自动识别当前 Codex 任务 ID；请给侧线窗口稳定名称。
- 计划变更、实现授权和掌握判断仍需明确的人类意图或证据。
