# 桌面引用的只读后备入口

适用于目标对话／任务引用已传入，但本轮工具表中没有 `read_thread` 且官方桌面后备服务实际支持该目标的情况。先检查原生工具及其 schema；原生工具可用就直接调用。当前 Codex 对话的可见内容直接使用上下文，无需为转换格式重新读取。此后备入口不是 Skill 的输入限制；其他聊天记录或导出文件可直接整理。

后备脚本只通过标准 MCP 调用官方 `read_thread`，不访问未公开网页接口，不读取登录凭据，不安装插件，不修改应用包、全局配置或数据库。它复用桌面应用已提供的 `CODEX_APP_TOOLS_PIPE_PATH`。如果此变量不存在或服务拒绝访问，应报告阻碍，不猜测连接地址或绕过拒绝。

需要确认三个输入：

1. 当前正在运行的官方桌面应用随附的 `resources/plugins/openai-bundled/plugins/codex-app-tools/server.mjs`。Windows 可通过 `Get-Process -Name ChatGPT` 的 `Path` 定位应用，再找到相邻 `resources`。不要硬编码旧版本路径，不从未知站点下载替代模块。
2. 已存在的 Node：优先 `CODEX_MCP_NODE_PATH`，否则已验证的本机 Node。
3. 真实的当前 Codex 任务 ID，用作 MCP 调用来源；目标 ID 来自用户指定的 ChatGPT 对话或 Codex 任务引用，二者不能混淆。先确认后备服务的 `read_thread` schema 与目标类型兼容。优先当前任务元数据。缺失时，只读查询本任务工作目录对应的本地任务元数据；匹配不唯一就停止，不随机选其他任务身份。

```powershell
python '<skill-dir>/scripts/read_conversation.py' --server '<official-server.mjs>' --node '<node.exe>' --caller-thread-id '<current-codex-task-id>' --conversation-id '<supported-target-id>' --output '<task-dir>/work/conversation-page-1.json'
```

脚本沿用 `--conversation-id` 参数名，内部传为 `threadId`，并要求 UUID；仅用于与现有参数约定兼容的服务。其他任务 ID 或 schema 使用相应原生读取工具，不将其强行改造成 UUID，也不以转换笔记为由改造应用连接。

有 `page.nextCursor` 时增加 `--cursor '<returned-cursor>'`，保存下一页到不同文件；不要反复请求同一游标。检查 `truncatedMessages` 和原始 JSON 的每条消息标记。即使三轮都返回，某条回答仍可能被截到 20000 字符；不能声称全量读取。

返回的附件路径可能在临时目录。需要使用的附件先复制到当前任务 `work/`，按对应文件技能读取。不要把私人会话或课件放进 Skill、样式示例或可分发压缩包。

正文依然不足时，可以通过受支持的浏览器读取该会话剩余部分，或让用户提供导出文件。若用户只想先看效果，可明确制作“可读取部分的试用稿”，并区分会话整理、课件核对和额外补充。
