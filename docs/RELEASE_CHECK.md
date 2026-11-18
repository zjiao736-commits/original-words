# 开源预览验收 / Open-source preview checks

本版本适合发布为 **macOS 开发预览版**，不能标为跨平台、所有账号全量采集均已验证的稳定版。

This version is a **macOS development preview**, not a universally verified cross-platform or full-history collector.

- 标准库服务；普通 Chrome + 手动确认扩展安装。Windows / Linux 桌面启动未验证。
- 中英切换包括新增来源导入、动态状态、搜索占位和无障碍标签；用户原话保持原文。
- Claude 新导入仅经过官方结构的合成样例测试；Kimi/Grok 支持文档化通用 JSON，不代表官方格式或网页自动采集已适配。
- 浏览器测试使用无账号的临时上下文与模拟接口；不代表全部真实平台账号已重新采集。
- 发布采用 package_release.py 白名单，排除数据库、导入导出、浏览器配置、日志、录音、视频、模型与虚拟环境。
- MIT 仅覆盖项目代码和原创文档；第三方商标/图标不重新授权。宣传素材与配乐不在源码包中。
- 不保证零风控；用户须正常登录并遵循平台提示。出现验证应暂停。

Use `python3 package_release.py --output /tmp/yuanhua-preview.zip` to build a source-only ZIP. Review its contents before publishing. Do not run `git add .` on a personal-data working folder; start from the clean source archive.

## 2026-11-18 验收记录 / Verification record

- 49 项 Python 隔离测试通过，包括新增来源、账号隔离、原文保护、空目录首次保存与发布排除规则。
- 3 组浏览器测试通过：发布包换路径、中英切换、手机宽度下的更多来源导入。
- 5 组当前扩展契约测试通过：四平台请求、暂停恢复、来源变化、多账号路由与 service worker 恢复。
- 56 个白名单文件的源码包已检查：不含私人数据、个人绝对路径、密钥特征；解压后导入测试通过。
- 旧的 v0.7 runner 测试桩已替换为当前 service worker 复用/隔离契约入口。
- 未用新的真实 Claude/Kimi/Grok 账号验证网页采集；本次未执行 GitHub 发布。

- 2026-11-18：另用真实本机 HTTP 服务测试 Claude/Kimi/Grok/其他 Agent 各两份合成账号记录，从文件上传、后台任务、搜索到 Markdown/JSON 下载均通过；没有将导入误报为浏览器账号连接。
