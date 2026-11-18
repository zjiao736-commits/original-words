# 参与贡献 / Contributing

欢迎改进平台适配、导入格式、双语界面和安装体验。请用虚构示例描述问题，勿上传账号、原始对话或登录配置。

Contributions to adapters, import formats, translations, and installation are welcome. Use synthetic examples; never submit account sessions or private conversations.

## 贡献新的网页适配器 / Contributing browser adapters

1. `extension/providers.js`：域名、主页、消息解析和历史发现。
2. `collector_v2.py` 与 `extension/manifest.json`：同步声明允许的来源和最小权限。
3. `provider_catalog.py` 与前端：声明真实能力，添加品牌素材来源记录。
4. 用合成记录测试新安装、账号隔离、断联、页面变化、暂停/恢复、原文保留、中英界面。
5. 再用已授权的真实账号验收。不要提交账号、Cookie、原始对话或私有截图。

Add an adapter, declare the minimal allowed hosts, update capability metadata and UI, test failure paths with synthetic data, then verify an authorized real account. Never commit account data or private examples.

## 开发检查 / Development checks

```bash
python3 -m unittest -v test_provider_imports test_first_run_safety
python3 package_release.py --output /tmp/yuanhua-source.zip
```

[开发验收范围 / Verification scope](docs/RELEASE_CHECK.md)
