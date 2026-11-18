"""本地桌面入口：先确认服务，再明确使用普通 Chrome。"""
import urllib.request, subprocess, sys, time, webbrowser
from pathlib import Path
ROOT=Path(__file__).resolve().parent
CHROME=Path('/Applications/Google Chrome.app')
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
def healthy():
 try:
  with opener.open('http://127.0.0.1:8765/api/browser',timeout=2) as response:return response.status==200
 except Exception:return False

def main():
 if not healthy():
  with (ROOT/'service.log').open('a') as log:
   subprocess.Popen([sys.executable,str(ROOT/'server.py')],cwd=ROOT,stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True)
  for _ in range(30):
   if healthy():break
   time.sleep(.25)
  else:
   print('原话本地服务未启动。请查看工具文件夹中的 service.log，已有资料保留。',file=sys.stderr)
   return 1
 if CHROME.exists():
  subprocess.run(['open','-a',str(CHROME),'http://127.0.0.1:8765/setup'],check=True)
 else:
  # 降级页直接说明限制，而不是让用户在不支持扩展的浏览器反复连接。
  notice=ROOT/'chrome-required.html'
  notice.write_text('''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>原话 · 选择浏览器</title><body style="max-width:640px;margin:12vh auto;padding:24px;font:18px/1.8 system-ui;color:#30302e;background:#fdfcf9"><h1>本机未找到 Google Chrome</h1><p>自动采集需要普通 Google Chrome 和原话扩展。安装 Chrome 后，再双击“我的语料库”。</p><p>你也可以先进入控制台，导入平台的官方文件、查看已有原话。当前浏览器无法连接 Chrome 扩展。</p><a href="http://127.0.0.1:8765/setup">进入控制台，查看或导入资料</a></body></html>''',encoding='utf-8')
  webbrowser.open(notice.as_uri())
 return 0
if __name__=='__main__':sys.exit(main())
