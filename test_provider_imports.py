"""Provider imports in a new temporary database. No real accounts or archives."""
import io,json,sqlite3,tempfile,unittest,zipfile,hashlib
from pathlib import Path
from import_providers import parse_provider
from import_chatgpt import import_export
from export_archives import export_all
class ProviderImports(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
  def connect():
   c=sqlite3.connect(self.root/'archive.sqlite3');c.row_factory=sqlite3.Row;return c
  self.connect=connect
  with connect() as c:
   c.execute("CREATE TABLE conversations(id TEXT PRIMARY KEY,title TEXT,url TEXT,platform TEXT,body TEXT,messages TEXT,tags TEXT,updated TEXT DEFAULT CURRENT_TIMESTAMP)")
   c.execute('CREATE TABLE snapshots(conversation_id TEXT,payload TEXT)')
 def tearDown(self):self.tmp.cleanup()
 def generic(self,**extra):
  return dict(id='one',title='Original',account='A',messages=[{'role':'user','text':'  Keep\nmy original words.  '},{'role':'assistant','text':'AI reply'},{'role':'tool','text':'unknown context'}],**extra)
 def encode(self,rows):return json.dumps(rows,ensure_ascii=False).encode()
 def test_claude_official_json_and_zip(self):
  raw=self.encode([{'uuid':'c1','name':'Claude export','chat_messages':[{'sender':'human','text':'My exact words'},{'sender':'assistant','content':[{'type':'text','text':'Reply'},{'type':'image','source':'ignored'}]}]}]);z=io.BytesIO()
  with zipfile.ZipFile(z,'w') as f:f.writestr('data/conversations.json',raw)
  for b in [raw,z.getvalue()]:
   r=parse_provider(b,'claude')[0];self.assertEqual([m['role'] for m in r['messages']],['user','assistant']);self.assertEqual(r['messages'][0]['text'],'My exact words')
 def test_generic_sources_and_account_separation(self):
  a=self.generic(source='Agent A');b={**a,'account':'B'};c={**a,'source':'Agent B'}
  rows=parse_provider(self.encode([a,b,c]),'other');self.assertEqual(len({r['url'] for r in rows}),3);self.assertEqual(rows[0]['messages'][0]['text'],a['messages'][0]['text']);self.assertEqual(rows[0]['messages'][2]['role'],'unknown')
 def test_dedup_local_save_and_exports(self):
  for provider in ['claude','kimi','grok','other']:
   raw=self.encode([self.generic()])
   for _ in range(2):import_export(raw,self.root,self.connect,lambda t:['test'],platform=provider)
  with self.connect() as c:self.assertEqual(c.execute('SELECT COUNT(*) FROM conversations').fetchone()[0],4)
  counts=export_all(self.root);self.assertEqual(counts['Claude'],1);self.assertEqual(counts['Kimi'],1)
  text=(self.root/'exports/Claude/我的原话汇总.md').read_text();self.assertIn('  Keep\nmy original words.  ',text);self.assertNotIn('AI reply',text);self.assertNotIn('unknown context',text)
 def test_invalid_and_zip_limits(self):
  for data in [{},[],[{'messages':'invalid'}],[{'messages':[{'role':'user','image':'x'}]}]]:
   with self.assertRaises(ValueError):parse_provider(self.encode(data),'kimi')
  with self.assertRaises(ValueError):parse_provider(self.encode([self.generic()]),'unknown')
 def test_same_conversation_different_platforms_do_not_collide(self):
  rows=[parse_provider(self.encode([self.generic()]),key)[0] for key in ['claude','kimi','grok','other']];self.assertEqual(len({r['url'] for r in rows}),4)
if __name__=='__main__':unittest.main()
