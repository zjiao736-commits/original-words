# Yuanhua

**Bring the ideas scattered across your AI chats back to your computer.**

Local deployment · No model tokens for collection or archiving · Chinese / English UI

Yuanhua is a local AI conversation collector and archive. Bring work notes, ideas, and personal reflections from different platforms into one place. Keep your original words, search them, and export material you want to use again.

No model API setup or model credits are required for collection, import, search, or keyword categorization. On a Mac with Python 3 installed, download, extract, and double-click to start. Browser collection requires a one-time Chrome extension setup and provider sign-in; supported files can be imported directly.

[Download source](https://github.com/zjiao736-commits/yuanhua/releases/download/v0.10.3/Yuanhua-0.10.3-source.zip) · [中文](README.md) · [Provider support](docs/PROVIDERS.md)

## Product demo

<a href="https://github.com/zjiao736-commits/yuanhua/releases/download/v0.10.3/Yuanhua-demo.mp4"><img src="https://github.com/zjiao736-commits/yuanhua/releases/download/v0.10.3/Yuanhua-cover.png" width="260" alt="Yuanhua product demo"></a>

[Watch the demo](https://github.com/zjiao736-commits/yuanhua/releases/download/v0.10.3/Yuanhua-demo.mp4)

## What you can do

- **Bring scattered records together:** collect through the browser or import files into one local archive.
- **Keep your original words:** your messages come first, with AI replies and raw context available separately. Nothing is rewritten or polished.
- **Find material again:** search titles and text, filter by source, and revisit earlier ideas.
- **Reuse your archive:** export Markdown or JSON for writing, research, or local agents you authorize to read files.
- **Switch interface languages:** Chinese and English UI, with original conversation text preserved.

## Get started in three steps

The source edition requires macOS and Python 3. Browser collection also requires Google Chrome.

### 1. Download and start

[Download the source ZIP](https://github.com/zjiao736-commits/yuanhua/releases/download/v0.10.3/Yuanhua-0.10.3-source.zip), extract it, and double-click `启动.command`.

If macOS blocks direct execution, open a terminal in the extracted `yuanhua` folder and run:

```bash
python3 desktop_launcher.py
```

The local dashboard opens at `http://127.0.0.1:8765/setup`.

### 2. Choose a source

**File import:** select a supported provider export. No extension is required.

**Browser collection:** follow the dashboard instructions to install the Chrome extension once. Sign in to the provider in the same Chrome profile, return to the dashboard, connect, and start collection. Extension installation and provider sign-in require your confirmation.

### 3. Search and export

Search and revisit records in **My words**. Download Markdown or JSON in **Export & backup**. Start the tool again for later use.

## Supported providers

| Source | Available method |
|---|---|
| ChatGPT, Gemini, DeepSeek, Doubao | Browser collection |
| ChatGPT, Gemini, Claude | Corresponding provider-export import |
| Kimi, Grok, other AI / agents | Generic JSON import |

**Add another AI / Agent** is a file-import entry; arbitrary website account binding is not supported. Set `account` in generic JSON to separate accounts, and `source` to distinguish other agents.

[Provider capabilities and import schema](docs/PROVIDERS.md)

## Local storage and scope

Archived records, imported source files, and exported material stay on your computer. Stop tasks and the service before making a full backup of `archive.sqlite3`, `imports/`, and `exports/`.

This is a macOS development preview. Browser collection requires internet and your signed-in account. Provider page changes, verification prompts, or sleep may pause collection; discovered counts are not complete account-history totals. Attachments are not downloaded automatically. Import again to capture new messages in an existing conversation. Windows / Linux desktop startup is not supported yet.

Collection and archiving make no model calls. Later processing with other AI tools has its own costs.

## Open source and license

Code and original documentation use [MIT](LICENSE). Contributions to adapters, import formats, and usability are welcome. [Contributing](CONTRIBUTING.md) · [Media credits](docs/MEDIA.md)

Third-party logos and trademarks remain their owners’ property and imply no endorsement.
