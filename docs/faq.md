# 常见问题 / FAQ

## Chat to Notes Skill 是什么？ / What is it?

它是帮助 Codex 将聊天材料组织成笔记的 Skill，包含讲解规则和本地渲染工具。它不是聊天平台、独立模型服务或浏览器扩展。The model writes the explanation; local scripts assemble HTML and export PDF.

## 只支持网页版 ChatGPT 吗？ / Is it limited to ChatGPT web?

不是。当前 Codex 对话、其他可访问任务、ChatGPT 引用和其他平台的聊天导出均可作为来源。直接读取能力取决于实际工具与权限；提供导出文件也可以。可见上下文与完整原文需要区分。

## 必须提供课件吗？ / Are slides required?

不需要。只有聊天记录也可以整理。附件用于补充依据；没有课件不自动构成缺口。只有被引用且必要、但无法取得的材料才需要单独说明。

## 风格可以在阅读时切换吗？ / Can I switch styles while reading?

不可以。生成前选择风格，同一文档的 HTML 与 PDF 保持该选择。更换风格需要新版本 HTML。自测答案仍可以展开或收起，打印时全部展开。

## 能保证内容没有错误吗？ / Does it guarantee correctness?

不能。代码执行或代数工具能验证具体结果，但一般命题的条件、推导和材料覆盖仍需审查。脚本检查锚点、资源、哈希、部分布局与 PDF 结构，不能判断“讲透了没有”。

## 小模型能达到相同质量吗？ / Can a smaller model match the result?

固定模板有助于保持外观。解释质量取决于模型、材料和审查过程；本仓库没有跨模型等质基准。先用有可靠答案的代表性材料测试，再比较错误率与返工成本。

## 可以导入 Goodnotes 吗？ / Does it work with Goodnotes?

输出是带跳转和书签的 PDF，可用于尝试导入。仓库没有真实 Goodnotes 设备导入验证，也不能保证每个阅读器都保留同样的导航行为。

## 会上传我的聊天吗？ / Does it upload my conversations?

仓库中的渲染与 PDF 导出在本机运行，导出浏览器阻止外部 HTTP 资源。实际对话获取与模型整理遵循你使用的宿主环境和账户的数据处理方式；不能把整个工作流称为离线。不要将私人原文或课件提交到公共 Issue。

## 是否需要 API Key？ / Is another API key required?

这些本地脚本无需单独的模型 API Key。内容整理使用宿主模型，仍受宿主订阅、额度或 API 计费约束。

## 为什么源码含中文？ / Why are the instructions in Chinese?

当前主要工作流以中文维护，仓库提供中英文入口文档。用户可要求英文等输出语言；多语言长篇排版和讲解质量仍需各自验证。
