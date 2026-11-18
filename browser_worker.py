"""后台增量采集：独立配置、可暂停、最多两条并发、不调用模型。"""
import asyncio,json,time,urllib.request,sys,os
from pathlib import Path
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parent;STATE=ROOT/'browser-state.json';COMMANDS=ROOT/'commands'
PLATFORMS={'deepseek':'https://chat.deepseek.com/','doubao':'https://www.doubao.com/chat/'}
initial=(ROOT/'browser-platform.txt').read_text().strip() if (ROOT/'browser-platform.txt').exists() else 'deepseek'
if initial not in PLATFORMS:initial='deepseek'
HEADLESS='--background' in sys.argv
state={'status':'starting','message':'正在启动后台采集器','headless':HEADLESS,'pid':os.getpid(),'queue':[],'platforms':{k:{'status':'idle','message':'尚未连接'} for k in PLATFORMS}}
def save():
 tmp=STATE.with_suffix('.tmp');tmp.write_text(json.dumps(state,ensure_ascii=False));tmp.replace(STATE)
def mark(k,status,message,**extra):state['platforms'][k].update(status=status,message=message,updated=time.time(),**extra);save()
def send(data):
 req=urllib.request.Request('http://127.0.0.1:8765/api/collect',data=json.dumps(data,ensure_ascii=False).encode(),headers={'Content-Type':'application/json'})
 with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(req,timeout=30) as r:return json.load(r)
async def main():
 if STATE.exists():
  try:state['queue']=json.loads(STATE.read_text()).get('queue',[])
  except ValueError:pass
 for x in state['queue']:
  if x['status']=='processing':x['status']='pending'
 COMMANDS.mkdir(exist_ok=True);save()
 async with async_playwright() as p:
  context=await p.chromium.launch_persistent_context(str(ROOT/'browser-profile'),executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless=HEADLESS,accept_downloads=False)
  if HEADLESS:
   async def lightweight(route):
    if route.request.resource_type in {'image','media','font'}:await route.abort()
    else:await route.continue_()
   await context.route('**/*',lightweight)
  pages={};tasks={};paused=set();background=set();slots=asyncio.Semaphore(2)
  def launch(coro):
   t=asyncio.create_task(coro);background.add(t);t.add_done_callback(background.discard);return t
  async def open_platform(k,focus=True):
   page=pages.get(k)
   if page is None or page.is_closed():
    mark(k,'opening','正在连接平台')
    page=await context.new_page();pages[k]=page
    await page.goto(PLATFORMS[k],wait_until='domcontentloaded',timeout=45000)
   if focus and not HEADLESS:await page.bring_to_front()
   mark(k,'ready','已打开页面。首次连接请完成登录，之后可后台同步。')
   return page
  async def collect(page,method):
   await page.add_script_tag(path=str(ROOT/'extension/adapter.js'));return await page.evaluate('(m)=>archiveAdapter[m]()',method)
  async def discover(k):
   page=await open_platform(k,False);mark(k,'discovering','正在扫描历史列表；数量未知时不显示百分比',started_at=time.time(),finished_at=None)
   data=await collect(page,'discover');seen={x['url'] for x in state['queue']}
   for x in data['links']:
    if x['url'] not in seen:state['queue'].append(dict(x,status='pending',platform=k));seen.add(x['url'])
   mark(k,'ready','历史扫描完成',warnings=data['warnings'],discovered=sum(x.get('platform')==k for x in state['queue']))
  async def harvest(k,mode='gentle',retry=False):
   if retry:
    for x in state['queue']:
     if x.get('platform')==k and x['status']=='failed':x['status']='pending'
   targets=[x for x in state['queue'] if x.get('platform')==k and x['status']=='pending'];work=asyncio.Queue()
   for x in targets:work.put_nowait(x)
   paused.discard(k);started=time.time();mark(k,'collecting','正在后台保存新对话',started_at=started,total=len(targets),completed=0,saved=0,failed=0,finished_at=None,mode=mode)
   def progress(message):
    finished=[x for x in targets if x['status'] in {'saved','failed'}]
    mark(k,'collecting',message,completed=len(finished),saved=sum(x['status']=='saved' for x in targets),failed=sum(x['status']=='failed' for x in targets),elapsed=time.time()-started)
   async def consume():
    page=await context.new_page()
    try:
     while not work.empty() and k not in paused:
      x=work.get_nowait();x['status']='processing';progress('正在读取：'+(x.get('title') or '一条历史对话'));begin=time.time()
      try:
       async with slots:
        await page.goto(x['url'],wait_until='domcontentloaded',timeout=45000)
        data=await collect(page,'extract')
        if data['url']!=x['url']:raise ValueError('登录状态失效或页面跳转，请重新连接')
        if x.get('title'):data['title']=x['title']
        await asyncio.to_thread(send,data)
       x.update(status='saved',warnings=data['metadata']['warnings'],duration=time.time()-begin);x.pop('error',None)
      except Exception as e:x.update(status='failed',error=str(e).split('\n')[0])
      progress('已保存 '+str(sum(x['status']=='saved' for x in targets))+' 条');await asyncio.sleep(.5 if mode=='gentle' else .15)
    finally:await page.close()
   await asyncio.gather(*(consume() for _ in range(1 if mode=='gentle' else 2)))
   mark(k,'paused' if k in paused else 'done','已暂停，进度已保存' if k in paused else ('没有新对话，已跳过重复采集' if not targets else '本轮同步完成，可查看档案'),finished_at=time.time(),elapsed=time.time()-started)
  async def run(k,action,mode):
   try:
    if action=='discover':await discover(k)
    elif action=='background':await discover(k);await harvest(k,mode)
    else:await open_platform(k,False);await harvest(k,mode,action=='retry')
   except asyncio.CancelledError:
    for x in state['queue']:
     if x.get('platform')==k and x['status']=='processing':x['status']='pending'
    mark(k,'paused','已暂停，未完成对话将在下次重读',finished_at=time.time())
   except Exception as e:mark(k,'error',str(e).split('\n')[0],finished_at=time.time())
  state.update(status='ready',message='后台任务与操作页独立，关闭页面不会中断采集');save()
  if not HEADLESS:
   async def initial_open():
    try:await open_platform(initial)
    except Exception as e:mark(initial,'error',str(e).split('\n')[0])
   launch(initial_open())
  closing=False;idle_exit=False;last_work=time.monotonic()
  while not closing:
   legacy=ROOT/'browser-command.json';files=([legacy] if legacy.exists() else [])+sorted(COMMANDS.glob('*.json'))
   for f in files:
    last_work=time.monotonic()
    try:command=json.loads(f.read_text());f.unlink()
    except (OSError,ValueError):continue
    action=command.get('action');k=command.get('platform',initial)
    if action=='close':closing=True;break
    if k not in PLATFORMS:continue
    if action in {'open','switch'}:
     async def safe_open(k=k):
      try:await open_platform(k)
      except Exception as e:mark(k,'error',str(e).split('\n')[0])
     launch(safe_open())
    elif action=='pause':
     paused.add(k)
     if k in tasks and not tasks[k].done():tasks[k].cancel()
     else:mark(k,'paused','已暂停，进度保留',finished_at=time.time())
    elif action in {'discover','start','background','retry'}:
     if k in tasks and not tasks[k].done():continue
     tasks[k]=launch(run(k,action,command.get('mode','gentle')))
   if any(not t.done() for t in background):last_work=time.monotonic()
   if HEADLESS and time.monotonic()-last_work>120:idle_exit=True;break
   await asyncio.sleep(.2)
  for t in list(background):t.cancel()
  await asyncio.gather(*list(background),return_exceptions=True);await context.close();state.update(status='done' if idle_exit else 'closed',message='任务完成，后台已自动休眠' if idle_exit else '已停止，进度保留');save()
try:asyncio.run(main())
except Exception as e:state.update(status='error',message=str(e));save()
