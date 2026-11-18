"""Declared provider capabilities. Import support does not imply browser collection."""
PROVIDERS = {
 'chatgpt': {'name':'ChatGPT','host':'chatgpt.com','browser':True,'format':'official'},
 'gemini': {'name':'Gemini','host':'gemini.google.com','browser':True,'format':'official'},
 'deepseek': {'name':'DeepSeek','host':'chat.deepseek.com','browser':True,'format':'generic'},
 'doubao': {'name':'豆包','host':'www.doubao.com','browser':True,'format':'generic'},
 'claude': {'name':'Claude','host':'claude.ai','browser':False,'format':'claude'},
 'kimi': {'name':'Kimi','host':'www.kimi.com','browser':False,'format':'generic'},
 'grok': {'name':'Grok','host':'grok.com','browser':False,'format':'generic'},
 'other': {'name':'其他 AI / Agent','host':'local-agent','browser':False,'format':'generic'},
}
