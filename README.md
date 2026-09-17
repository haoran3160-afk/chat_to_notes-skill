# Chat to Notes Skill · 对话转笔记

[English](README.en.md) · [安装与命令](docs/usage.md) · [常见问题](docs/faq.md) · [验证范围](docs/validation.md)

[![Checks](https://github.com/haoran3160-afk/chat_to_notes-skill/actions/workflows/checks.yml/badge.svg)](https://github.com/haoran3160-afk/chat_to_notes-skill/actions/workflows/checks.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**将 Codex、ChatGPT 和其他可读取的聊天记录整理成可理解、可复习的笔记。** 生成前选择六种风格之一，先审阅固定风格 HTML，再从同一版本导出带内部跳转与书签的 PDF。

这是一个 Codex Skill，包含整理规则、HTML 模板和本地 Python 工具。适用于学习笔记、数学推导、代码例题与技术讨论；课件可选。无需浏览器扩展、后端服务或额外模型 API。内容整理使用运行 Skill 的模型，仍会消耗该环境的模型额度。

![六种笔记风格，使用同一份公开合成数学材料，由实际 Skill 模板渲染](docs/images/styles-overview.png)

## 为什么使用它

- 将多轮追问归入知识点，保留前提、机制、关键推导和能追踪的例子。
- 用知识清单区分“完整讲解”“只提及”“材料不足”，避免将出现术语误当成覆盖充分。
- 数学使用静态 MathML，必要图片与关系图内嵌；打印时展开自测答案。
- 同一份笔记固定风格；导出前检查确认哈希、资源、打印溢出、书签与内部链接。
- 保留来源和读取缺口说明，不把对话摘要说成全文，不把排版通过说成内容必然正确。

如果课件已足够清楚，直接批注课件也可能更合适。此工具的价值在于保存对话中新增的解释与理解过程。

## 快速开始

在支持 Skill 安装的 Codex 中输入：

```text
使用 $skill-installer 安装 https://github.com/haoran3160-afk/chat_to_notes-skill
中的 skills/chat-to-notes。
```

也可手动克隆，复制 `skills/chat-to-notes` 到自己的 Skill 目录；[详细说明](docs/usage.md)包含 Windows 与 macOS/Linux 命令、依赖及更新注意事项。

安装后，用自然语言调用：

```text
使用 $chat-to-notes，把当前 Codex 对话整理成笔记。
先让我选择风格，先输出 HTML，等我确认后再导出 PDF。
```

```text
使用 $chat-to-notes，把这份聊天导出文件整理成层级大纲笔记。
保留公式的条件、关键推导与例题，不需要附录。
```

你也可以指定可访问的其他 Codex 任务、ChatGPT 对话引用或聊天文本。能否直接读取某个平台取决于当前工具与权限，不承诺任意链接都能自动取得全文。

## 六种风格

| 风格 | 稳定 ID | 适用方式 |
|---|---|---|
| [康奈尔线索](docs/images/cornell.png) | `cornell` | 左栏回忆问题，右栏完整讲解 |
| [层级大纲](docs/images/outline.png) | `outline` | 按概念和推理依赖分层 |
| [例题与旁批](docs/images/annotated.png) | `annotated` | 完整例题配关键步骤依据 |
| [图解手写](docs/images/sketch.png) | `sketch` | 方格纸、图文邻近、关系可视化 |
| [经典手写](docs/images/handwritten.png) | `handwritten` | 楷体、浅色纸张、通栏讲解 |
| [规范风](docs/images/electronic.png) | `electronic` | 规范字体、白底、清晰层级 |

新文档先选择风格；已指定或继续同一份文档时不重复询问。HTML 没有风格切换按钮。换风格生成新版本，PDF 不临时改风格。字体依赖本地环境，楷体不可用时会回退；不同机器不保证像素完全一致。

## 从聊天到 PDF

1. 选择风格，读取实际可取得的对话与可选附件。
2. 建立知识清单，按依赖组织讲解，核对代码、公式、例题及必要图示。
3. 生成自足 HTML，检查屏幕和打印布局，交给用户审阅。
4. 用户确认后，从该 HTML 导出同风格 PDF，检查跳转、书签并逐页查看。

学习型内容采用“全局关系 → 模块讲解 → 例题 → 变式与反馈”；普通讨论按主题、依据、结论和未解决问题组织，不强加自测。

## 本地运行与示例

需要 Python 3.10+。HTML 组装仅使用标准库；PDF 导出另外需要本机 Chrome/Edge/Chromium、PyMuPDF 和 websocket-client。

```bash
python examples/build_demo.py --style electronic --output-dir outputs/demo
```

这会用仓库内独立编写的合成例题生成 HTML，不读取你的账户或聊天。PDF 示例命令见[使用指南](docs/usage.md#pdf-export)。所有六种公开预览都通过实际 Skill 渲染器生成；[预览生成方法](docs/usage.md#reproduce-previews)可复现。

## 仓库目录

```text
skills/chat-to-notes/   可安装的 Skill：规则、模板、读取与导出脚本
examples/              无私人数据的可复现示例
tests/                 渲染约束、失败路径和浏览器导出测试
docs/                  使用、FAQ、验证范围与预览图片
.github/               CI、Issue 表单、PR 模板和标签定义
requirements-pdf.txt   可选的 PDF 导出依赖
```

仅安装 `skills/chat-to-notes/` 即可加载 Skill。仓库不包含私人会话、课程附件、字体文件或账户凭据。

## 边界与贡献

脚本不自动证明数学命题，也不判断讲解是否足够深入。模型可能遗漏条件；来源与内容审查仍然必要。PDF 适合尝试导入 Goodnotes，但目前没有真实设备导入测试。已验证与未验证内容见[验证范围](docs/validation.md)。

欢迎提交可脱敏复现的问题或改进：[贡献指南](CONTRIBUTING.md)、[安全报告](SECURITY.md)、[变更记录](CHANGELOG.md)。由 [haoran3160-afk](https://github.com/haoran3160-afk) 维护；项目原创代码与文档采用 [MIT](LICENSE) 许可证，第三方依赖沿用各自许可证。
