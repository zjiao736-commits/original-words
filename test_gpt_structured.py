"""Same-origin structured account read, synthetic authenticated response only."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless=True)
 page=b.new_page();calls=[];mapping={'a':{'parent':None,'message':{'author':{'role':'user'},'content':{'parts':['  original one  ']}}},'b':{'parent':'a','message':{'author':{'role':'assistant'},'content':{'parts':['reply']}}},'c':{'parent':'b','message':{'author':{'role':'user'},'content':{'parts':['new today',{'type':'image','id':'ignored'}]}}}}
 def route(r):
  url=r.request.url
  if '/api/auth/session' in url:r.fulfill(json={'accessToken':'synthetic-test-session'})
  elif '/backend-api/conversation/' in url:
   calls.append(r.request.headers.get('authorization'));r.fulfill(json={'title':'Synthetic','mapping':mapping,'current_node':'c'})
  else:r.fulfill(content_type='text/html',body='<main>No DOM message markers</main>')
 page.route('https://chatgpt.com/**',route);page.goto('https://chatgpt.com/c/example');page.add_script_tag(path=str(ROOT/'extension/adapter.js'));r=page.evaluate('archiveAdapter.extract()');assert [m['text'] for m in r['messages'] if m['role']=='user']==['  original one  ','new today'];assert 'synthetic-test-session' not in json.dumps(r);assert calls==['Bearer synthetic-test-session'];print('PASS no DOM nodes: structured current-branch text and new messages retained, credentials excluded from archive');b.close()
