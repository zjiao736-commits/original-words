# 平台与导入 / Providers and imports

| 来源 / Source | 网页采集 / Browser collection | 文件导入 / File import |
|---|---|---|
| ChatGPT | 已有适配器；平台页面变化可能导致失败 / Existing adapter, subject to page changes | 官方 JSON / ZIP |
| Gemini | 已有适配器；仅采集平台提供的文字 / Existing adapter, text only | Takeout JSON / HTML |
| DeepSeek / 豆包 | 已有适配器 / Existing adapters | 通用 JSON / Generic JSON |
| Claude | 未适配 / Not available | conversations.json / ZIP |
| Kimi / Grok | 未适配 / Not available | 仅下述通用 JSON；不能直接导入未知官方格式 / Generic JSON only |
| 其他 AI / 本地 Agent | 未适配 / Not available | 下述通用 JSON / Generic JSON below |

“支持文件导入”不代表“支持网页全量自动采集”。网页发现数不是账号完整历史数。浏览器采集受平台页面及账号可访问内容影响，不保证覆盖完整历史。

File import does not imply browser collection. Discovered history is not a verified complete account history. Browser collection depends on provider pages and accessible account content; complete history is not guaranteed.

在控制台展开“添加其他 AI / Agent”，选择来源，导入文件。新增来源与四个原有网页采集来源分开。资料库支持按平台筛选；导出页面按来源提供 Markdown 和 JSON。

Expand **Add another AI / Agent**, select a source, and import a file. Imported sources are distinct from browser collectors. Filter by source in My words; export Markdown and JSON in Export & backup.

## 通用格式 / Generic format

```json
[
  {
    "id": "unique-conversation-id",
    "title": "A thought to keep",
    "account": "personal",
    "source": "My local agent",
    "messages": [
      {"role": "user", "text": "My original expression, unchanged."},
      {"role": "assistant", "text": "Assistant context, kept separately."}
    ]
  }
]
```

也接受外层 `{"conversations": [...]}`。`account` 用于隔离同平台不同账号；`source` 用于区分“其他 Agent”。同一来源、账号和对话 id 重复导入会更新同一条记录。原文件按内容哈希保存；消息文字不润色。未知角色保持 unknown，不混入用户原话。仅处理明确的文字字段，不下载附件。单文件及 ZIP 解压后的 conversations.json 限制 100MB；不提取 ZIP 路径到磁盘。

An outer `{"conversations": [...]}` object is also accepted. Use `account` to separate accounts and `source` to separate other agents. Reimporting the same source/account/conversation ID updates that record; source files and snapshots are retained. Unknown roles remain unknown. Text only; attachments are not downloaded. The file and expanded JSON limits are 100 MB. ZIP paths are never extracted.

## 扩展平台支持 / Extending provider support

[参与贡献 / Contributing](../CONTRIBUTING.md)
