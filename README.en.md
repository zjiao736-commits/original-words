# Yuanhua

**Bring the ideas scattered across your AI chats back to your computer.**

[中文](README.md) · [Provider capabilities](docs/PROVIDERS.md) · [Verification scope](docs/RELEASE_CHECK.md) · MIT

Yuanhua is a local archive for your AI conversations. Keep your original words, retain AI replies as context, and search or export ideas you want to use again.

Collection, import, search, and keyword categorization make no model calls and require no model API key. Provider access still needs internet and your own account. Any later AI use has its own costs.

> **macOS development preview.** Browser collection depends on provider page structure and cannot guarantee a complete account history. Other operating systems and all account environments have not been verified.

## 30-second demo

No narration · Captions and motion · Example data. Click the cover to watch or download.

<a href="https://github.com/zjiao736-commits/yuanhua/releases/download/v0.10.2/Yuanhua-demo.mp4"><img src="https://github.com/zjiao736-commits/yuanhua/releases/download/v0.10.2/Yuanhua-cover.png" width="260" alt="Yuanhua demo"></a>

[MP4](https://github.com/zjiao736-commits/yuanhua/releases/download/v0.10.2/Yuanhua-demo.mp4) · [素材与配乐说明 / Media credits](docs/MEDIA.md)

## Features

- Local storage with your original words first; AI replies and raw context expand separately.
- Collection from signed-in Chrome pages or file imports.
- Source filtering, search, and Markdown / JSON export for local agents you authorize to read files.
- Keyword categorization without rewriting; unclear roles remain unidentified.
- Chinese / English interface without translating your private material.

## Provider support

| Source | Available method |
|---|---|
| ChatGPT, Gemini, DeepSeek, Doubao | Browser adapters, subject to verification prompts and page changes |
| ChatGPT | Official conversations.json / ZIP import |
| Gemini | Google Takeout JSON / activity HTML, available text only |
| Claude | conversations.json / ZIP import, tested with structural fixtures |
| Kimi, Grok, other AI / agents | Documented generic JSON import; no browser adapter yet |

**Add another AI / Agent** is a file-import entry, not arbitrary website account binding or verified full-history collection. Set `account` to separate accounts and `source` to distinguish other agents. See the [supported schema](docs/PROVIDERS.md).

## First run

Requires macOS and Python 3. Browser collection also needs Google Chrome. The everyday service uses the Python standard library.

1. Download and extract the source ZIP, preserving the directory structure.
2. Double-click `启动.command` to open the dashboard. If macOS blocks direct execution, open a terminal in the extracted folder and run:

   ```bash
   python3 desktop_launcher.py
   ```

3. The launcher opens `http://127.0.0.1:8765/setup` locally.
4. **File import:** use the provider import option or expand **Add another AI / Agent**. No browser extension is needed for this method.
5. **Browser collection:** follow the dashboard instructions to open Chrome extensions, enable Developer mode, choose **Load unpacked**, and select the `extension` folder. Chrome requires your confirmation.
6. Sign in to your provider in the same Chrome profile. Return to the dashboard, connect the account, and start collection. Complete sign-in or verification yourself.
7. Search in **My words** and download Markdown / JSON in **Export & backup**.

Run the launcher again for later use. A source download does not install a desktop app. Keep Chrome, the service, and the computer running during collection. Sleep or provider verification may pause tasks; saved data remains available.

## Accounts and privacy

Sources are stored separately. Browser **Add account** works only within sessions the current Chrome profile can identify; it does not read other browser profiles. Discovered counts are not verified complete account-history counts.

`archive.sqlite3` contains records and snapshots; `imports/` holds source files, and `exports/` holds generated documents. Stop tasks and the service before making a full backup. Markdown / JSON downloads do not contain every historical snapshot.

Attachments are not downloaded automatically. Saved conversations are skipped; import again to capture messages added to an existing conversation. Never publish your personal working folder.

## Contributing

New adapters, import parsers, translations, and installation improvements are welcome. Declare whether a provider supports browser collection, official export import, or only generic JSON.

```bash
python3 -m unittest -v test_provider_imports
python3 package_release.py --output /tmp/yuanhua-source.zip
```

See [verification scope](docs/RELEASE_CHECK.md). Source releases exclude personal chats, recordings, browser profiles, downloaded models, and virtual environments.

## Why I built it

I work in marketing and real estate research and use AI extensively. My ideas and reflections were scattered across chat windows. I built Yuanhua with AI around that everyday problem and am sharing the work openly.

## License

Project code and original documentation use [MIT](LICENSE). Third-party logos and trademarks remain their owners’ property, imply no endorsement, and are not relicensed by this project. See `assets/品牌素材来源.json` for sources.
