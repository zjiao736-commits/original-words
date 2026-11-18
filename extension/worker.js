'use strict';
globalThis.createYuanhuaWorker=function(config){
const params=new URLSearchParams(config),platform=params.get('platform'),accountId=params.get('accountId'),runnerId=params.get('runnerId');
const provider=globalThis.YuanhuaProviders[platform],API='http://127.0.0.1:8765';
const stateKey='yh.state.'+accountId,intentKey='yh.intents.'+accountId;
let account,state={queue:[],warnings:[],status:'connecting',stage:'connection',message:'正在检测平台页面',started_at:null,finished_at:null},source=null,busy=false,pauseRequested=false,polling=false,probing=false,ackRequestId=null,lastIntent=null,readTab=null;
const handled=new Set(),sleep=ms=>new Promise(resolve=>setTimeout(resolve,ms));
async function request(path,options={}){const c=new AbortController(),t=setTimeout(()=>c.abort(),15000);try{const r=await fetch(API+path,{...options,signal:c.signal});let data;try{data=await r.json()}catch{throw Error('本地服务返回无效内容')}if(!r.ok)throw Error(data.error||'本地服务错误 '+r.status);return data}finally{clearTimeout(t)}}
async function post(){const payload={...state,handledRequestIds:[...handled],protocol:2,platform,accountId,runnerId,accountLabel:account?.label||provider.name+' · 当前Chrome会话',source,ackRequestId};await chrome.storage.local.set({[stateKey]:payload});try{await request('/api/bridge',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)})}catch(e){await chrome.storage.local.set({['yh.transport.'+accountId]:{error:e.message,at:Date.now()}})}}
async function mark(status,message,stage){state.status=status;state.message=message;if(stage)state.stage=stage;await post()}
function canonical(url){const u=new URL(url);if(platform==='chatgpt'){const m=u.pathname.match(/\/c\/([\w-]+)/);if(m)return u.origin+'/c/'+m[1]}return u.origin+u.pathname.replace(/\/$/,'')}
function isHome(tab){try{return provider.hosts.includes(new URL(tab.url).hostname)}catch{return false}}
async function waitComplete(id,expected){const deadline=Date.now()+45000;while(Date.now()<deadline){const t=await chrome.tabs.get(id);if(t.status==='complete'&&!t.pendingUrl){if(!expected||canonical(t.url)===canonical(expected))return t;throw Error('平台页面发生跳转，请在控制台检查登录或验证状态')}await sleep(400)}throw Error('页面加载超时，任务已暂停，不自动重试')}
async function executeOnce(id,method){await chrome.scripting.executeScript({target:{tabId:id},files:['adapter.js']});const result=await chrome.scripting.executeScript({target:{tabId:id},func:async method=>{try{return {ok:true,data:await window.archiveAdapter[method]()}}catch(e){return {ok:false,error:e.message||String(e)}}},args:[method]});const first=result?.[0];if(first?.error)throw Error(first.error.message||String(first.error));if(!first?.result?.ok)throw Error(first?.result?.error||'页面读取中断，没有写入未完成内容');return first.result.data}
async function execute(id,method){let timer;const read=async()=>{try{return await executeOnce(id,method)}catch(e){if(!/Frame with ID.*removed|context.*destroyed|document.*unloaded/i.test(e.message))throw e;await waitComplete(id);return executeOnce(id,method)}};return Promise.race([read(),new Promise((_,reject)=>{timer=setTimeout(()=>reject(Error('读取超过90秒，已暂停；未确认完整的内容不会算成功')),90000)})]).finally(()=>clearTimeout(timer))}
async function refreshAccount(){const all=(await chrome.storage.local.get('yh.accounts.v2'))['yh.accounts.v2']||{};const latest=all[accountId];if(!latest||latest.runnerId!==runnerId||latest.platform!==platform)throw Error('采集来源已失效，请重新连接');if(account&&latest.scope!==account.scope)throw Error('来源账号会话已变化，请重新连接');if(account&&latest.sourceTabId!==account.sourceTabId)source=null;account=latest;}
function tabScope(t){return platform==='gemini'?(new URL(t.url).pathname.match(/^\/u\/(\d+)\//)?.[1]||'0'):'chrome-session'}
async function sourceTab(){await refreshAccount();let t;try{t=await chrome.tabs.get(account.sourceTabId)}catch{}
 if(!t){const candidates=(await chrome.tabs.query({url:provider.matches})).filter(x=>isHome(x)&&tabScope(x)===account.scope&&x.id!==readTab?.id);t=candidates.find(x=>x.active)||candidates[0];
  if(!t){const home=platform==='gemini'&&account.scope!=='0'?'https://gemini.google.com/u/'+account.scope+'/app':provider.home;t=await chrome.tabs.create({url:home,active:false});}
  const all=(await chrome.storage.local.get('yh.accounts.v2'))['yh.accounts.v2']||{};const latest=all[accountId];if(!latest||latest.runnerId!==runnerId||latest.platform!==platform||latest.scope!==account.scope)throw Error('来源账号会话已变化，请重新连接');account={...latest,sourceTabId:t.id,sourceUrl:t.url};all[accountId]=account;await chrome.storage.local.set({'yh.accounts.v2':all});source=null;
 }
 if(!isHome(t)){source=null;throw Error('平台页面已转到登录或验证地址')}if(tabScope(t)!==account.scope){source=null;throw Error('Google会话已切换，请重新关联对应来源')}return t;
}
async function probe(){if(probing)return false;probing=true;try{
 const t=await sourceTab();await waitComplete(t.id);const info=await execute(t.id,'probe');
 source={tabId:t.id,url:t.url,title:info.title||provider.name,accountLabel:account.label,scope:account.scope,ready:!info.requiresLogin&&!!info.ready};
 if(info.requiresLogin||!info.ready){await mark('requires_login',info.reason||'请在控制台点击“前往登录”，完成平台验证后重新检测','login');return false}
 await mark('ready','已关联 '+provider.name+' 的可读取页面；未读取密码','ready');return true;
 }catch(e){source=null;await mark('disconnected',e.message,'connection');return false}finally{probing=false}}
async function scan(){await mark('discovering','正在扫描历史；目录数量不代表账号全部历史','scan');const t=await sourceTab(),result=await execute(t.id,'discover');const links=new Map((result.links||[]).map(x=>[canonical(x.url),{url:canonical(x.url),title:x.title}]));state.warnings=[...(result.warnings||[])];
 // 目录只在至少3条当前账号链接交叉匹配后合并，不把另一个账号的目录混入。
 if(platform==='chatgpt'){try{const index=await request('/api/history-index?platform=chatgpt');const items=index.items||[],known=new Set(items.map(x=>canonical(x.url)));const overlap=[...links.keys()].filter(x=>known.has(x)).length;if(overlap>=3){for(const x of items)if(!links.has(canonical(x.url)))links.set(canonical(x.url),{url:canonical(x.url),title:x.title});state.warnings.push('与已连接应用目录交叉匹配 '+overlap+' 条，目录合并后 '+links.size+' 条；精确总数仍未核对')}}catch(e){state.warnings.push('目录补充暂不可用，本轮只保存已发现的链接')}}
 let saved=new Set();try{saved=new Set((await request('/api/saved-index?platform='+platform+'&accountId='+encodeURIComponent(accountId))).urls.map(canonical))}catch(e){throw Error('无法核对已有档案，已暂停，避免重复采集')}
 const old=new Map(state.queue.map(x=>[canonical(x.url),x]));for(const [url,x] of links){if(!old.has(url)){const item={...x,status:saved.has(url)?'saved':'pending'};state.queue.push(item);old.set(url,item)}else if(saved.has(url))old.get(url).status='saved';else if(old.get(url).status==='saved')old.get(url).status='pending'}
 if(!links.size){await mark('paused','没有发现可读取的历史条目；未视为采集完成，请检查登录和侧栏','needs_review');return false}
 await post();return true;
}
async function collect(command){if(busy)return;busy=true;state.requestId=command.requestId;state.started_at=Date.now()/1000;state.finished_at=null;let errorOccurred=false;
 try{
  if(pauseRequested)return;if(!source?.ready&&!(await probe()))return;if(pauseRequested)return;
  if(!(await scan()))return;if(pauseRequested)return;
  // 用户明确再次开始时，每个失败项最多重试一次；遇验证/错误仍立即暂停。
  for(const item of state.queue)if(item.status==='failed'||item.status==='partial')item.status='pending';
  const pending=state.queue.filter(x=>x.status==='pending'||x.status==='processing');
  if(!pending.length){await mark('done','本轮发现的记录已经保存，没有新增对话；账号全部历史仍需核对','done');return}
  readTab=await chrome.tabs.create({url:'about:blank',active:false});await chrome.tabs.update(readTab.id,{autoDiscardable:false});await waitComplete(readTab.id);
  for(const item of pending){if(pauseRequested)break;item.status='processing';delete item.error;await mark('collecting','正在保存：'+(item.title||'一条对话'),'read');
   try{
    await refreshAccount();await chrome.tabs.update(readTab.id,{url:item.url,active:false});await waitComplete(readTab.id,item.url);const data=await execute(readTab.id,'extract');await refreshAccount();let liveSource;try{liveSource=await chrome.tabs.get(account.sourceTabId)}catch{}if(liveSource&&(!isHome(liveSource)||tabScope(liveSource)!==account.scope))throw Error('来源登录或账号已变化，已暂停，未保存当前读取');if(pauseRequested&&state.stage==='connection')throw Error('后台读取页面已关闭，未保存当前读取');
    if(canonical(data.url)!==canonical(item.url))throw Error('读取时跳到了其他页面，未保存');
    if(!data.messages?.some(m=>m.role==='user'&&m.text?.trim()))throw Error('未识别到用户原话，未计为保存成功');
    data.metadata={...data.metadata,accountId,sourceAccount:account.label,collectorProtocol:2};if(item.title)data.title=item.title;
    await request('/api/collect',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
    item.status=data.metadata.completeness==='partial'?'partial':'saved';item.warnings=data.metadata.warnings||[];
    if(item.status==='partial')state.warnings.push('有局部快照需要复核；继续处理其余记录，不计入完整保存数量')
   }catch(e){item.error=e.message;if(/本次原话比既有档案短/.test(e.message)){item.status='partial';state.warnings=[...new Set([...state.warnings,'保留较完整的旧档案，本次短快照单列待复核'])];}else{item.status='failed';pauseRequested=true;errorOccurred=true;state.warnings=[...new Set([...state.warnings,e.message])];}}
   await post();if(!pauseRequested)await sleep(2500);
  }
  const partialCount=state.queue.filter(x=>x.status==='partial').length;await mark(pauseRequested?'paused':partialCount?'partial':'done',pauseRequested?(errorOccurred?'读取遇到问题，已暂停。请查看本页问题详情':'已暂停，进度保留'):partialCount?'本轮已处理；'+partialCount+' 条局部快照需要复核，其余记录已保存':'本轮发现的记录已保存，账号全部历史仍需核对',pauseRequested||partialCount?'needs_review':'done');
 }catch(e){errorOccurred=true;state.warnings=[...new Set([...state.warnings,e.message])];await mark('paused',e.message,'needs_review')}
 finally{const owned=readTab;readTab=null;if(owned)await chrome.tabs.remove(owned.id).catch(()=>{});busy=false;state.finished_at=Date.now()/1000;await post()}
}
async function accept(command){if(!command?.requestId||command.runnerId!==runnerId)return;if(handled.has(command.requestId)){ackRequestId=command.requestId;await post();return;}if(busy&&command.action!=='pause')return;const starts=['collect','start','retry','background','discover'].includes(command.action);if(starts){busy=true;pauseRequested=false;}handled.add(command.requestId);ackRequestId=command.requestId;await post();
 if(command.action==='pause'){pauseRequested=true;if(busy)await mark('pausing','正在处理当前一条，随后暂停','pause');else await mark('paused','已暂停，已有档案保留','paused');return}
 if(command.action==='connect'){if(!busy){source=null;await probe();}return}
 if(starts){busy=false;return collect(command);}
}
let readingIntents=false;
async function readIntent(){if(readingIntents)return;readingIntents=true;try{const intents=(await chrome.storage.local.get(intentKey))[intentKey]||[];for(const intent of intents){if(intent.runnerId!==runnerId||handled.has(intent.requestId))continue;if(busy&&intent.action!=='pause')continue;accept(intent).catch(async e=>{await mark('error',e.message,'needs_review')});}}finally{readingIntents=false}}
async function poll(){if(polling)return;polling=true;try{await post();const command=await request('/api/bridge-command?platform='+platform+'&accountId='+encodeURIComponent(accountId)+'&runnerId='+encodeURIComponent(runnerId));if(command.requestId)accept(command).catch(async e=>{busy=false;await mark('error',e.message,'needs_review')});await readIntent()}catch(e){}finally{polling=false}}
async function boot(){if(!provider||!accountId||!runnerId)return;const all=(await chrome.storage.local.get('yh.accounts.v2'))['yh.accounts.v2']||{};account=all[accountId];if(!account||account.runnerId!==runnerId||account.platform!==platform)return;const previous=(await chrome.storage.local.get(stateKey))[stateKey];if(previous){state={...state,...previous};for(const id of previous.handledRequestIds||[])handled.add(id);for(const x of state.queue)if(x.status==='processing')x.status='pending';state.status='paused';state.message='后台页已恢复，进度保留，等待你的操作'}
 chrome.storage.onChanged.addListener((changes,area)=>{if(area==='local'&&changes[intentKey])readIntent().catch(()=>{})});
 chrome.tabs.onRemoved.addListener(async id=>{if(id===readTab?.id){pauseRequested=true;await mark('pausing','后台读取页面已关闭，任务暂停，已有档案保留','connection');return}if(id===account.sourceTabId){source=null;if(busy&&readTab){state.warnings=[...new Set([...state.warnings,'来源页面已关闭，继续处理已扫描队列'])];await post();return}pauseRequested=true;await mark('disconnected','来源页面已关闭；已有档案保留，可重新连接','connection')}});
 setInterval(()=>{if(busy||probing)poll()},4000);await probe();await readIntent();
}
const ready=boot().catch(async e=>{state.status='error';state.message=e.message;await post()});
return {ready,poll,accept,snapshot:()=>state};
};

