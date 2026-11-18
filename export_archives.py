import sqlite3,json
from provider_catalog import PROVIDERS
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def export_all(root=None):
 root=Path(root) if root else ROOT
 results={}
 with sqlite3.connect(root/'archive.sqlite3') as c:
  c.row_factory=sqlite3.Row
  for host,name in [(v['host'],v['name'].replace('/','-')) for v in PROVIDERS.values()]:
   rows=[dict(r) for r in c.execute('SELECT * FROM conversations WHERE platform=?',(host,))];folder=root/'exports'/name;folder.mkdir(parents=True,exist_ok=True)
   for r in rows:
    r['messages']=json.loads(r['messages']);r['tags']=json.loads(r['tags'])
    (folder/(r['id'][:16]+'.md')).write_text('# '+r['title']+'\n\n来源：'+r['url']+'\n\n'+'\n\n'.join(m['text'] for m in r['messages'] if m['role']=='user'))
   (folder/'我的原话汇总.md').write_text('# '+name+' · 我的原话\n\n'+'\n\n---\n\n'.join('## '+r['title']+'\n\n来源：'+r['url']+'\n\n'+'\n\n'.join(m['text'] for m in r['messages'] if m['role']=='user') for r in rows))
   (folder/'全部原始对话.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2));results[name]=len(rows)
 return results
if __name__=='__main__':print(json.dumps(export_all(),ensure_ascii=False))
