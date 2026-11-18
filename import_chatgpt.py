"""读取官方导出 JSON/ZIP，保留原文件与全部消息分支，不调用模型。"""
import json, io, zipfile, hashlib, re
LIMIT=100*1024*1024

def parse_export(raw):
 payloads=[]
 if zipfile.is_zipfile(io.BytesIO(raw)):
  with zipfile.ZipFile(io.BytesIO(raw)) as z:
   files=[f for f in z.infolist() if re.fullmatch(r'conversations(?:[_-]\d+)?\.json',f.filename.split('/')[-1])]
   if not files:raise ValueError('压缩包中没有 conversations.json 或编号对话JSON；尚未支持此导出格式')
   if sum(f.file_size for f in files)>LIMIT:raise ValueError('对话JSON合计超过100MB，请分批导入')
   payloads=[json.loads(z.read(f).decode('utf-8-sig')) for f in files]
 else:payloads=[json.loads(raw.decode('utf-8-sig'))]
 records=[]
 for payload in payloads:
  if not isinstance(payload,list):raise ValueError('需要ChatGPT官方对话列表JSON')
  for conv in payload:
   if not isinstance(conv,dict) or not isinstance(conv.get('mapping'),dict):raise ValueError('对话格式不匹配，已停止导入')
   mapping=conv['mapping'];messages=[]
   for node_id,node in mapping.items():
    if not isinstance(node,dict):continue
    msg=node.get('message')
    if not isinstance(msg,dict):continue
    role=(msg.get('author') or {}).get('role')
    if role not in {'user','assistant'}:continue
    content=msg.get('content') or {};parts=content.get('parts',[])
    # 只处理字符串或明确的文字字段，附件引用不伪装成用户说过的话。
    texts=[p if isinstance(p,str) else p.get('text','') if isinstance(p,dict) else '' for p in parts]
    text='\n'.join(t for t in texts if isinstance(t,str) and t)
    if text:messages.append(dict(role=role,text=text,selected=False,node_id=node_id,parent=node.get('parent'),timestamp=msg.get('create_time')))
   # 当前分支按父链排序。其他分支单独保存，不混入原话阅读顺序。
   active=[];cursor=conv.get('current_node');seen=set()
   while cursor in mapping and cursor not in seen:
    seen.add(cursor);active.append(cursor);cursor=mapping[cursor].get('parent')
   active.reverse();index={m['node_id']:m for m in messages}
   ordered=[index[i] for i in active if i in index]
   warnings=[]
   if not ordered:
    ordered=sorted(messages,key=lambda m:(m.get('timestamp') is None,m.get('timestamp') or 0));warnings.append('没有可识别的当前分支，按时间展示；请核对顺序')
   cid=str(conv.get('id') or conv.get('conversation_id') or hashlib.sha256(json.dumps(conv,sort_keys=True).encode()).hexdigest())
   records.append(dict(url='https://chatgpt.com/c/'+cid,title=conv.get('title') or '未命名对话',platform='chatgpt.com',messages=ordered,branches=messages,raw=conv,warnings=warnings))
 return records

def import_export(raw,root,connect,classify,platform="chatgpt",progress=None):
 if len(raw)>LIMIT:raise ValueError('文件超过100MB，请分批导入')
 if progress:progress(stage='parsing',message='正在读取导出结构')
 if platform=='gemini':
  from import_gemini import parse_gemini
  records=parse_gemini(raw)
 elif platform=='chatgpt': records=parse_export(raw)
 else:
  from import_providers import parse_provider
  records=parse_provider(raw,platform)
 if progress:progress(stage='saving',total=len(records),done=0,message='正在保存原话和来源')
 folder=root/'imports';folder.mkdir(exist_ok=True)
 digest=hashlib.sha256(raw).hexdigest();target=folder/(digest+('.zip' if zipfile.is_zipfile(io.BytesIO(raw)) else '.json' if raw.lstrip().startswith((b'[',b'{')) else '.html'))
 if not target.exists():target.write_bytes(raw);target.chmod(0o600)
 with connect() as c:
  for number,r in enumerate(records,1):
   key=hashlib.sha256(r['url'].encode()).hexdigest();old=c.execute('SELECT tags,messages FROM conversations WHERE id=?',(key,)).fetchone()
   chosen={m['text'] for m in json.loads(old['messages']) if m.get('selected')} if old else set()
   for m in r['messages']:m['selected']=m['role']=='assistant' and m['text'] in chosen
   body='\n\n'.join(m['role']+'\n'+m['text'] for m in r['messages']);user='\n'.join(m['text'] for m in r['messages'] if m['role']=='user')
   tags=json.loads(old['tags']) if old else classify(user) if user else ['待识别角色']
   c.execute('INSERT INTO conversations(id,title,url,platform,body,messages,tags) VALUES(?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET title=excluded.title,body=excluded.body,messages=excluded.messages,tags=excluded.tags,updated=CURRENT_TIMESTAMP',(key,r['title'],r['url'],r['platform'],body,json.dumps(r['messages'],ensure_ascii=False),json.dumps(tags,ensure_ascii=False)))
   c.execute('INSERT INTO snapshots(conversation_id,payload) VALUES(?,?)',(key,json.dumps(r,ensure_ascii=False)))
   if progress and (number%10==0 or number==len(records)):progress(done=number,total=len(records))
 return {'ok':True,'conversations':len(records),'user_messages':sum(m['role']=='user' for r in records for m in r['messages']),'warnings':[w for r in records for w in r['warnings']], 'unidentified':sum(m['role']=='unknown' for r in records for m in r['messages'])}
