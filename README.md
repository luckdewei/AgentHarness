# AgentHarness

渐进式 Agent Harness 学习项目，对齐 [Claude Code 学习路径](https://claude.docs-hub.com/zh/timeline/)（s01–s20）。

核心理念：**最小可用 Agent 就是一个循环**——调用模型、执行工具、回传结果；其余能力（权限、钩子、计划、子 Agent、技能……）挂在循环周围，而不是缠进循环内部。

当前进度：**已完成 s01–s07（至技能加载）**。

---

## 快速开始

```bash
# 依赖
uv sync

# 配置 .env
OPENAI_BASE_URL=...
OPENAI_API_KEY=...
MODEL_ID=...

# 运行
uv run python main.py
```

输入问题回车发送，`q` / `exit` 退出。

---

## 已实现：s01 → s07

### s01 · Agent 循环

> 一个循环就够了

`agent.py` 中的 `agent_loop`：调模型 → 若有 tool_calls 则执行 → 把结果写回 messages → 继续，直到模型不再调工具。

入口在 `main.py`：维护对话历史，每轮用户输入后进入该循环。

### s02 · 工具使用

> 循环保持稳定，新能力通过分发表注册

| 层       | 文件                | 职责                               |
| -------- | ------------------- | ---------------------------------- |
| Schema   | `tools/schema.py`   | 工具名、描述、参数定义（发给模型） |
| Handler  | `tools/handlers.py` | 实际执行逻辑                       |
| Dispatch | `tools/executor.py` | 按名称分发，按签名过滤参数         |

当前工具：`bash`、`read_file`、`write_file`、`glob`、`todo_write`、`spawn_subagent`、`load_skill`。

### s03 · 权限控制

> 危险操作需要在 shell 执行前由 harness 做决策

`hooks.py` 的 `permission_hook`（`PreToolUse`）：

- **禁止列表**：`rm -rf /`、`sudo`、`shutdown` 等直接拒绝
- **破坏性命令**：`rm `、`del ` 等需用户确认
- **工作区外写入**：`write_file` 路径越界时询问

权限在 harness 层拦截，模型侧无需反复询问。

### s04 · Hooks

> 横切行为应围绕循环挂载，而非缠进循环内部

事件与内置钩子：

| 事件               | 钩子                           | 作用               |
| ------------------ | ------------------------------ | ------------------ |
| `UserPromptSubmit` | `workspace_inject_hook`        | 注入当前工作目录   |
| `PreToolUse`       | `permission_hook` / `log_hook` | 权限门控、调用日志 |
| `PostToolUse`      | `large_output_hook`            | 超大输出告警       |
| `Stop`             | `summary_hook`                 | 会话结束统计       |

用 `register_hook` / `trigger_hooks` 挂载；循环只负责在关键点触发，不内嵌横切逻辑。

### s05 · TodoWrite

> 没有计划的 Agent，做着做着就偏了

- 工具 `todo_write`：维护 `pending` / `in_progress` / `completed` 任务列表并打印
- 系统提示要求多步骤任务先规划
- `agent_loop` 中若连续多轮未更新 todo，注入 `<reminder>` 催促更新

### s06 · Subagent

> 大任务拆小，每个拿到的都是干净上下文

`spawn_subagent`（`tools/executor.py`）：

- 独立消息历史 + 精简系统提示（`SUB_SYSTEM`）
- 仅暴露 `base_tools`，不可再委派
- 跑完后只把摘要结果回传主 Agent，主线程上下文不被子任务细节污染

### s07 · 技能加载

> 只在任务实际需要时注入专业知识

按需加载，避免把全部技能塞进系统提示：

1. 启动时扫描 `skills/*/SKILL.md`，注册 name / description（`skills.py`）
2. 系统提示只列出技能清单（`prompt.py`）
3. 模型需要完整说明时调用 `load_skill(name)` 再注入正文

示例技能：`skills/code-review/SKILL.md`（只读代码审查，只建议不改代码）。

新增技能：在 `skills/<name>/` 下放置带 frontmatter 的 `SKILL.md` 即可。

---

## 项目结构

```text
AgentHarness/
├── main.py              # REPL 入口
├── agent.py             # Agent 主循环
├── llm.py               # 模型调用
├── prompt.py            # 系统提示运行时组装
├── hooks.py             # 生命周期钩子 + 权限
├── skills.py            # 技能扫描与按需加载
├── config.py            # 环境与工作目录
├── utils.py             # 消息/路径等工具
├── tools/
│   ├── schema.py        # 工具定义
│   ├── handlers.py      # 工具实现
│   └── executor.py      # 分发 + Subagent
└── skills/
    └── code-review/
        └── SKILL.md     # 示例技能
```

---

## Todo（s08 → s20）

后续将继续实现：

### 记忆管理

- [ ] **s08 上下文压缩** — 窗口拥挤时摘要/腾挪，对话仍可用
- [ ] **s09 持久记忆** — 压缩会丢细节，重要事实跨会话保留

### 规划与协调（续）

- [ ] **s10 系统提示词** — 运行时组装策略/工具/技能/上下文（当前已有雏形，可继续深化）
- [ ] **s11 错误恢复** — 分类失败并决定值得重试的路径

### 多 Agent 平台 / 任务

- [ ] **s12 任务系统** — 任务图把大目标拆成可观察的工作
- [ ] **s13 后台任务** — 慢操作放后台，主循环继续推理
- [ ] **s14 定时调度** — 周期性工作由 harness 创建，不靠模型记忆

### 团队与隔离

- [ ] **s15 Agent 团队** — 持久队友并行，避免单上下文塞满
- [ ] **s16 团队协议** — 显式消息契约，而非默契
- [ ] **s17 自主 Agent** — 队友自发现、自认领任务
- [ ] **s18 Worktree 隔离** — 并行 Agent 隔离文件系统

### 集成

- [ ] **s19 MCP 工具** — 标准协议发现与调用外部工具
- [ ] **s20 综合 Agent** — 全部机制仍归到一个循环

---
