"""本地采集协议：账号/后台页隔离、命令ACK、状态与操作分开。"""
import time,threading,uuid,re,copy
from urllib.parse import urlparse
PLATFORMS={'chatgpt':{'host':'chatgpt.com','home':'https://chatgpt.com/'},'gemini':{'host':'gemini.google.com','home':'https://gemini.google.com/app'},'deepseek':{'host':'chat.deepseek.com','home':'https://chat.deepseek.com/'},'doubao':{'host':'www.doubao.com','home':'https://www.doubao.com/'}}
class CollectorRegistry:
 def __init__(self,ttl=180):self.ttl=ttl;self.lock=threading.RLock();self.bridges={};self.commands={};self.requests={}
 def identity(self,platform,account_id,runner_id=None):
  if platform not in PLATFORMS:raise ValueError('unsupported platform')
  for value in [account_id]+([runner_id] if runner_id is not None else []):
   if not isinstance(value,str) or not re.fullmatch(r'[\w.:-]{1,120}',value):raise ValueError('invalid collector identity')
  return (platform,account_id)
 def upsert(self,x):
  key=self.identity(x.get('platform'),x.get('accountId'),x.get('runnerId'))
  if not isinstance(x.get('queue',[]),list):raise ValueError('invalid queue')
  source=x.get('source')
  if source is not None:
   if not isinstance(source,dict):raise ValueError('invalid source')
   u=urlparse(source.get('url',''));allowed={PLATFORMS[key[0]]['host']}
   if key[0]=='doubao':allowed.add('doubao.com')
   if u.scheme!='https' or u.hostname not in allowed:raise ValueError('invalid source URL')
  with self.lock:
   old=self.bridges.get(key)
   if old and old['runnerId']!=x['runnerId'] and time.time()-old['last_seen']<self.ttl and old.get('status') in {'collecting','discovering'}:raise ValueError('该账号已有任务运行，不能由另一个后台页接管')
   record=copy.deepcopy(old or {});record.update(copy.deepcopy(x));record.setdefault('queue',[])
   if old and old['runnerId']!=x['runnerId']:
    stale=[v for v in self.commands.get(key,[]) if v['runnerId']!=x['runnerId']]
    for command in stale:self.requests[command['requestId']]={'status':'cancelled','platform':key[0],'accountId':key[1],'runnerId':command['runnerId'],'reason':'后台页已更新，旧指令未执行，请重新开始'}
    self.commands[key]=[v for v in self.commands.get(key,[]) if v['runnerId']==x['runnerId']]
    if stale:record['warnings']=list(dict.fromkeys(record.get('warnings',[])+['后台页已更新，此前未执行的旧指令已取消，请重新开始']))
   record['last_seen']=time.time();self.bridges[key]=record
   ack=x.get('ackRequestId')
   if ack:
    commands=self.commands.get(key,[])
    for command in commands[:]:
     if command['requestId']==ack and command['runnerId']==x['runnerId']:
      commands.remove(command);self.requests[ack]={'status':'acknowledged','platform':key[0],'accountId':key[1],'runnerId':x['runnerId']}
   return self.state(record)
 def state(self,x):
  fresh=time.time()-x.get('last_seen',0)<self.ttl
  source=x.get('source');status=x.get('status','idle')
  connected=bool(fresh and source and source.get('ready',True) and status not in {'requires_login','connecting','disconnected','error'})
  q=x.get('queue',[])
  return dict(platform=x['platform'],accountId=x['accountId'],runnerId=x['runnerId'],accountLabel=x.get('accountLabel','当前浏览器会话'),source=source,connected=connected,online=fresh,status=status if fresh else 'disconnected',message=x.get('message','') if fresh else '后台连接暂未响应，已有档案保留',saved=sum(v.get('status')=='saved' for v in q),failed=sum(v.get('status')=='failed' for v in q),completed=sum(v.get('status')=='saved' for v in q),total=len(q),queue=copy.deepcopy(q),warnings=x.get('warnings',[]),stage=x.get('stage'),requestId=x.get('requestId'),ackRequestId=x.get('ackRequestId'),started_at=x.get('started_at'),finished_at=x.get('finished_at'),bridge=True,protocol=2)
 def states(self):
  with self.lock:return [self.state(x) for x in self.bridges.values()]
 def find(self,platform,account_id=None):
  with self.lock:
   values=[x for k,x in self.bridges.items() if k[0]==platform and (not account_id or k[1]==account_id)]
   if not values:return None
   if not account_id and len(values)>1:return None
   return self.state(max(values,key=lambda x:x['last_seen']))
 def enqueue(self,platform,action,account_id=None,runner_id=None,request_id=None):
  if action not in {'connect','collect','pause','discover','start','retry'}:raise ValueError('invalid collector action')
  request_id=request_id or uuid.uuid4().hex
  if not isinstance(request_id,str) or not re.fullmatch(r'[\w.:-]{1,120}',request_id):raise ValueError('invalid requestId')
  with self.lock:
   state=self.find(platform,account_id)
   if not state or not state['online'] or (action not in {'pause','connect'} and not state['connected']):return {'ok':False,'requestId':request_id,'needsConnection':True,'error':'请先连接账号；开始采集不会自动跳转平台主页'}
   if runner_id and runner_id!=state['runnerId']:return {'ok':False,'requestId':request_id,'needsConnection':True,'error':'后台页面已经变化，请重新检测连接'}
   key=(platform,state['accountId'])
   if request_id in self.requests:
    previous=self.requests[request_id]
    if (previous['platform'],previous['accountId'],previous['runnerId'])!=(platform,key[1],state['runnerId']):return {'ok':False,'requestId':request_id,'error':'requestId已属于另一个账号或后台会话，请生成新请求'}
    return {'ok':True,'requestId':request_id,'accountId':key[1],'runnerId':state['runnerId'],'duplicate':True,'requestStatus':previous['status']}
   if action!='pause' and state['status'] in {'collecting','discovering','pausing'}:return {'ok':False,'requestId':request_id,'busy':True,'error':'该账号已有任务进行中'}
   command=dict(action=action,platform=platform,accountId=key[1],runnerId=state['runnerId'],requestId=request_id,createdAt=time.time())
   commands=self.commands.setdefault(key,[])
   if len(commands)>=20:raise ValueError('待处理指令过多，请等待现有任务')
   commands.insert(0,command) if action=='pause' else commands.append(command)
   self.requests[request_id]={'status':'queued','platform':platform,'accountId':key[1],'runnerId':state['runnerId']}
   return {'ok':True,'requestId':request_id,'accountId':key[1],'runnerId':state['runnerId'],'queued':True}
 def poll(self,platform,account_id,runner_id):
  key=self.identity(platform,account_id,runner_id)
  with self.lock:
   bridge=self.bridges.get(key)
   if not bridge or bridge['runnerId']!=runner_id:return {}
   if time.time()-bridge['last_seen']>=self.ttl:return {}
   commands=self.commands.get(key,[])
   return copy.deepcopy(commands[0]) if commands and commands[0]['runnerId']==runner_id else {}
