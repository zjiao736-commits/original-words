"""Claude export and documented generic JSON import. Pure standard library; no network."""
import hashlib,io,json,zipfile
from provider_catalog import PROVIDERS
LIMIT=100*1024*1024

def payload(raw):
 if len(raw)>LIMIT:raise ValueError('File exceeds 100 MB')
 if zipfile.is_zipfile(io.BytesIO(raw)):
  with zipfile.ZipFile(io.BytesIO(raw)) as z:
   files=[f for f in z.infolist() if f.filename.split('/')[-1]=='conversations.json' and not f.is_dir()]
   if len(files)!=1:raise ValueError('Expected one conversations.json in ZIP')
   if files[0].file_size>LIMIT:raise ValueError('Expanded JSON exceeds 100 MB')
   raw=z.read(files[0])
 return json.loads(raw.decode('utf-8-sig'))

def parse_provider(raw,platform):
 if platform not in PROVIDERS:raise ValueError('Unsupported provider')
 data=payload(raw)
 if isinstance(data,dict):data=data.get('conversations')
 if not isinstance(data,list) or not data:raise ValueError('Expected a non-empty conversations list')
 records=[]
 for conv in data:
  if not isinstance(conv,dict):raise ValueError('Invalid conversation')
  claude=platform=='claude' and 'chat_messages' in conv
  values=conv.get('chat_messages' if claude else 'messages')
  if not isinstance(values,list) or not values:raise ValueError('No recognized messages; use the documented JSON schema')
  messages=[]
  for m in values:
   if not isinstance(m,dict):raise ValueError('Invalid message')
   role=m.get('sender' if claude else 'role','unknown');role={'human':'user','model':'assistant'}.get(role,role)
   if role not in {'user','assistant','unknown'}:role='unknown'
   text=m.get('text')
   if not isinstance(text,str):
    content=m.get('content')
    if isinstance(content,str):text=content
    elif isinstance(content,list):text='\n'.join(b['text'] for b in content if isinstance(b,dict) and b.get('type')=='text' and isinstance(b.get('text'),str))
    else:raise ValueError('Message has no recognized text')
   if text:messages.append({'role':role,'text':text,'selected':False})
  if not messages:raise ValueError('No text messages found')
  # Explicit source/account labels separate local Agent and multi-account imports.
  account=conv.get('account','');source=conv.get('source','') if platform=='other' else ''
  if not isinstance(account,str) or len(account)>120 or not isinstance(source,str) or len(source)>120:raise ValueError('Invalid source/account label')
  identity=str(conv.get('uuid') or conv.get('id') or hashlib.sha256(json.dumps(conv,sort_keys=True,ensure_ascii=False).encode()).hexdigest())
  host=PROVIDERS[platform]['host'];cid=hashlib.sha256((platform+'|'+source+'|'+account+'|'+identity).encode()).hexdigest()
  url='https://'+host+'/import/'+cid if platform!='other' else 'local-agent://import/'+cid
  title=conv.get('name') if claude else conv.get('title');title=title or 'Untitled conversation'
  if not isinstance(title,str):raise ValueError('Invalid title')
  if source:title=source+' · '+title
  records.append(dict(url=url,title=title,platform=host,messages=messages,branches=messages,raw=conv,warnings=['Attachment content is not imported'] if any(m.get('attachments') for m in values) else []))
 return records
