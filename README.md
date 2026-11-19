# 原话

**把散在 AI 对话里的想法，收回自己的电脑。**

本地部署 · 采集归档不消耗模型 Token · 中英双语

原话是一款本地 AI 对话采集与归档工具。把不同平台里的工作资料、创作灵感和个人思考汇集到本机，保留你的原始表达，随时搜索、回看和导出。

无需配置模型 API，也无需为采集、导入、搜索和关键词分类购买模型额度。在已安装 Python 3 的 Mac 上，下载解压后可双击启动；首次网页采集需按指引安装 Chrome 扩展并登录平台，也可直接导入已有文件。

[下载源码包](https://github.com/zjiao736-commits/original-words/releases/download/v0.10.4/Original-Words-0.10.4-source.zip) · [English](README.en.md) · [平台支持](docs/PROVIDERS.md)

## 产品演示

<a href="https://github.com/zjiao736-commits/original-words/releases/download/v0.10.4/Yuanhua-demo.mp4"><img src="https://github.com/zjiao736-commits/original-words/releases/download/v0.10.4/Yuanhua-cover.png" width="260" alt="原话产品演示"></a>

[观看演示](https://github.com/zjiao736-commits/original-words/releases/download/v0.10.4/Yuanhua-demo.mp4)

## 你可以用原话做什么

- **汇集分散的记录**：通过浏览器采集或文件导入，把不同平台的对话放进同一个本地资料库。
- **保留原始表达**：优先展示你说过的话，AI 回复与原始上下文另行展开，不改写、不润色。
- **快速找回素材**：搜索标题和正文，按来源筛选，重新找到以前的想法和判断。
- **继续使用资料**：导出 Markdown 或 JSON，供写作、研究和有文件读取权限的本地 Agent 使用。
- **中文、英文随时切换**：界面语言可切换，归档原文保持不变。

## 三步开始使用

当前提供 macOS 源码版，需要 Python 3。网页采集还需要普通 Google Chrome。

### 1. 下载并启动

[下载源码包](https://github.com/zjiao736-commits/original-words/releases/download/v0.10.4/Original-Words-0.10.4-source.zip)，解压到电脑，双击 `启动.command`。

如果 macOS 阻止直接运行，在解压后的 `yuanhua` 文件夹中打开终端，执行：

```bash
python3 desktop_launcher.py
```

启动后打开本地控制台：`http://127.0.0.1:8765/setup`。

### 2. 选择资料来源

**文件导入**：选择平台导出的文件即可，无需安装浏览器扩展。

**浏览器采集**：按控制台指引安装一次 Chrome 扩展，在同一 Chrome 配置中登录平台，回到控制台连接账号并开始采集。扩展安装与平台登录需本人确认。

### 3. 搜索与导出

在“我的原话”搜索和回看记录，在“导出与备份”下载 Markdown 或 JSON。日后再次使用，只需重新启动工具。

## 支持的平台

| 来源 | 使用方式 |
|---|---|
| ChatGPT、Gemini、DeepSeek、豆包 | 浏览器采集 |
| ChatGPT、Gemini、Claude | 对应平台导出文件导入 |
| Kimi、Grok、其他 AI / Agent | 通用 JSON 文件导入 |

“添加其他 AI / Agent”用于文件导入，目前不支持任意网站的账号绑定。不同账号的通用 JSON 可以设置 `account`，其他 Agent 可以设置 `source`，区分资料来源。

[查看支持范围与导入格式](docs/PROVIDERS.md)

## 本地存储与使用范围

归档记录、导入原文件和导出结果均保存在电脑中。完整备份前，请先停止采集和本地服务，再复制 `archive.sqlite3`、`imports/` 和 `exports/`。

当前版本为 macOS 开发预览版。网页采集需要网络和已登录账号；平台页面变化、验证或电脑休眠可能暂停任务，发现的记录数不代表完整历史。附件不自动下载，GPT 再次采集会重新读取已发现的对话，以同步新增消息；其他平台的对话更新可重新导入。Windows / Linux 暂未提供桌面启动支持。

采集和归档不调用大模型；将导出资料交给其他 AI 处理时，费用由所用工具决定。

## 开源与许可

代码与原创文档采用 [MIT 许可](LICENSE)。欢迎贡献平台适配、导入格式与使用体验改进。[参与贡献](CONTRIBUTING.md) · [素材授权](docs/MEDIA.md)

第三方品牌图标和商标归原权利人，不表示品牌背书。
