# 原话

**把散在 AI 对话里的想法，收回自己的电脑。**

[English](README.en.md) · [平台支持范围](docs/PROVIDERS.md) · [验收记录](docs/RELEASE_CHECK.md) · MIT

原话是一个本地 AI 对话归档工具。保存你说过的话，保留 AI 回复作为上下文，让工作里的判断、创作灵感和个人思考可以再次搜索、导出和使用。

采集、导入、搜索和关键词分类不调用大模型，不需要模型 API Key。访问平台仍需网络和自己的账号；将导出资料交给其他 AI 使用时，费用由所用工具决定。

> **开发预览版 · macOS**。网页采集依赖平台页面结构，不能保证所有历史记录都已发现。其他系统和所有账号环境尚未验证。

## 30 秒演示

无旁白 · 字幕与动效 · 示例数据。点击封面观看或下载视频。

<a href="https://github.com/zjiao736-commits/yuanhua/releases/download/v0.10.2/Yuanhua-demo.mp4"><img src="https://github.com/zjiao736-commits/yuanhua/releases/download/v0.10.2/Yuanhua-cover.png" width="260" alt="Yuanhua demo"></a>

[MP4](https://github.com/zjiao736-commits/yuanhua/releases/download/v0.10.2/Yuanhua-demo.mp4) · [素材与配乐说明 / Media credits](docs/MEDIA.md)

## 能做什么

- 在本机归档对话，优先展示你的原始表达；AI 回复、原始内容另行展开。
- 用普通 Chrome 已登录页面采集，或导入平台导出文件。
- 按来源搜索，导出 Markdown / JSON，供你授权读取文件的本地 Agent 使用。
- 关键词分类不改写原文；无法确认角色的文字保留待识别。
- 界面支持中文 / English，不翻译或润色你的私人语料。

## 支持哪些平台

| 来源 | 当前方式 |
|---|---|
| ChatGPT、Gemini、DeepSeek、豆包 | 浏览器采集适配器；平台验证或页面变化可能导致暂停 |
| ChatGPT | 官方 conversations.json / ZIP 导入 |
| Gemini | Google Takeout JSON / 活动 HTML 导入；仅归档可用文字 |
| Claude | 导出 conversations.json / ZIP 导入；已用结构样例测试 |
| Kimi、Grok、其他 AI / Agent | 文档化通用 JSON 导入；尚无网页采集适配器 |

“添加其他 AI / Agent”是文件导入入口，**不是任意网站的账号绑定或自动全量采集**。不同账号可在通用格式中设置 `account`，其他 Agent 可设置 `source`，避免记录混在一起。详见[格式与能力说明](docs/PROVIDERS.md)。

## 开始使用

需要 macOS、Python 3；网页采集还需要 Google Chrome。日常服务只用 Python 标准库。

1. 下载并解压源码 ZIP，保持文件夹结构完整。
2. 双击 `启动.command` 打开控制台。如果 macOS 阻止直接运行，也可以在文件夹里打开终端，执行：

   ```bash
   python3 desktop_launcher.py
   ```

3. 浏览器打开本地控制台 `http://127.0.0.1:8765/setup`。
4. **文件导入**：在平台卡片中选择导入，或展开“添加其他 AI / Agent”，选择来源及文件。此方式无需安装扩展。
5. **网页采集**：按控制台提示进入 Chrome 扩展管理页，开启开发者模式，选择“加载已解压的扩展程序”，载入本项目的 `extension` 文件夹。这一步须你在浏览器确认。
6. 在同一 Chrome 配置中登录平台，回到控制台连接账号，再开始采集。登录或验证需本人完成。
7. 在“我的原话”搜索，在“导出与备份”下载 Markdown / JSON。

再次使用仍运行同一个启动命令。源码下载不会自动创建桌面应用。采集中请保持 Chrome、本地服务和电脑运行；休眠或验证可能暂停任务，已有资料保留。

## 账号与数据

不同平台的数据按来源区分。已适配浏览器的“添加账号”只在该浏览器可识别的会话范围内工作，不读取其他 Chrome 配置里的登录信息。不要把“发现了多少条”当成平台账号的完整历史总数。

`archive.sqlite3` 保存记录和历史快照；`imports/` 保存导入原文件，`exports/` 保存生成文件。完整备份请先停止任务和服务，再复制这些文件。Markdown / JSON 下载不包含所有历史快照。

默认保留用户原文，附件不自动下载。当前已保存对话会跳过，已有对话里的新增消息需重新导入。不要把含私人资料的工作文件夹直接上传 GitHub。

## 开发与贡献

欢迎贡献新平台适配器、导出格式解析器、中英界面和安装体验。新平台支持必须说明是网页采集、官方导入还是通用 JSON，不应只加一个按钮就宣称支持。

在干净源码目录中运行导入测试：

```bash
python3 -m unittest -v test_provider_imports
```

生成不含私人数据的源码包：

```bash
python3 package_release.py --output /tmp/yuanhua-source.zip
```

[发布检查](docs/RELEASE_CHECK.md)说明了自动测试与真实账号验证的区别。开源包不包含录音、聊天资料、浏览器登录配置、模型和虚拟环境。

## 为什么做原话

我从事市场营销和不动产研究，也是 AI 的长期使用者。工作、想法和反思散在不同对话窗口里，每次寻找都要重新翻一遍。于是从自己的需求出发，借助 AI 做了这个工具，也把过程开源。

它先解决一件具体的事：让你已经说过的话，留在自己手里。

## 许可

项目代码与原创文档采用 [MIT](LICENSE)。第三方品牌图标和商标归原权利人，不表示品牌背书，也不因本项目的 MIT 许可而重新授权。素材来源见 `assets/品牌素材来源.json`。
