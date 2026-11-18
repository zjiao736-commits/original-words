"""Google Takeout Gemini 活动导入。未明确角色的内容保留待识别，不猜作用户原话。"""
import io,json,zipfile,hashlib
from html.parser import HTMLParser
LIMIT=100*1024*1024
class ActivityHTML(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.blocks=[];self.depth=0;self.buf=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='div':
   if self.depth:self.depth+=1
   elif 'outer-cell' in a.get('class','').split():self.depth=1;self.buf=[]
  if self.depth and tag in {'br','p'}:self.buf.append('\n')
 def handle_endtag(self,tag):
  if self.depth and tag=='div':
   self.depth-=1
   if not self.depth:self.blocks.append(''.join(self.buf))
 def handle_data(self,text):
  if self.depth:self.buf.append(text)
def parse_gemini(raw):
 files=[]
 if zipfile.is_zipfile(io.BytesIO(raw)):
  with zipfile.ZipFile(io.BytesIO(raw)) as z:
   infos=[f for f in z.infolist() if ('gemini' in f.filename.lower() or 'bard' in f.filename.lower()) and f.filename.lower().endswith(('.json','.html'))]
   if sum(f.file_size for f in infos)>LIMIT:raise ValueError('活动文字超过100MB，请分批导入')
   files=[(f.filename,z.read(f)) for f in infos]
 else:files=[('activity.json' if raw.lstrip().startswith((b'[',b'{')) else 'activity.html',raw)]
 if not files:raise ValueError('未找到Gemini活动文件。请导出“我的活动 → Gemini Apps”，不要只选择“Gemini”。')
 records=[]
 for path,content in files:
  if path.endswith('.html'):
   parser=ActivityHTML();parser.feed(content.decode('utf-8-sig'));entries=[{'raw_html_text':t} for t in parser.blocks]
  else:
   value=json.loads(content.decode('utf-8-sig'));entries=value if isinstance(value,list) else value.get('activities',[]) if isinstance(value,dict) else []
  for e in entries:
   if not isinstance(e,dict):continue
   messages=[];warnings=[]
   explicit=e.get('messages',[])
   for m in explicit if isinstance(explicit,list) else []:
    if isinstance(m,dict) and m.get('role') in {'user','assistant'} and isinstance(m.get('text'),str):messages.append(dict(role=m['role'],text=m['text'],selected=False))
   title=e.get('title','')
   if not messages and isinstance(title,str):
    for prefix in ('Prompted ','已提问：','已提问:','询问了 '):
     if title.startswith(prefix):messages=[dict(role='user',text=title[len(prefix):],selected=False)];break
   if not messages:
    text=e.get('raw_html_text') or title or json.dumps(e,ensure_ascii=False)
    messages=[dict(role='unknown',text=text,selected=False)];warnings.append('该活动未提供可确认的角色，原始内容已保留待识别，不纳入个人原话。')
   digest=hashlib.sha256(json.dumps(e,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
   records.append(dict(url='https://gemini.google.com/import/'+digest,title=(title[:100] if isinstance(title,str) and title else 'Gemini活动记录'),platform='gemini.google.com',messages=messages,raw=e,source_file=path,source_time=e.get('time'),warnings=warnings))
 if not records:raise ValueError('没有识别到Gemini活动条目；原文件格式需要适配。')
 # 同一活动同时出现在HTML/JSON或多个重叠导出文件中时，按源活动身份去重。
 return list({r['url']:r for r in records}.values())
