'use strict';
importScripts('providers.js','worker.js');
const controllers=new Map();
const PROVIDERS=globalThis.YuanhuaProviders;
const nonce=()=>crypto.randomUUID();
const accountsKey='yh.accounts.v2';
const locks=new Map();
async function queueIntent(account,action,requestId){const key='yh.intents.'+account.id;const items=(await chrome.storage.local.get(key))[key]||[];items.push({action,requestId,runnerId:account.runnerId,at:Date.now()});await chrome.storage.local.set({[key]:items});}
function validatePlatform(platform){const p=PROVIDERS[platform];if(!p)throw Error('暂不支持该平台');return p}
function scopeOf(platform,url){if(platform!=='gemini')return 'chrome-session';return new URL(url).pathname.match(/^\/u\/(\d+)\//)?.[1]||'0'}
function sourceMatches(platform,tab){try{return PROVIDERS[platform].hosts.includes(new URL(tab.url).hostname)}catch{return false}}
async function accounts(){return (await chrome.storage.local.get(accountsKey))[accountsKey]||{}}
async function sourceChoices(platform){const p=validatePlatform(platform),tabs=(await chrome.tabs.query({url:p.matches})).filter(t=>sourceMatches(platform,t));const groups=new Map();for(const tab of tabs){const scope=scopeOf(platform,tab.url);const old=groups.get(scope);if(!old||tab.active)groups.set(scope,tab)}return [...groups].map(([scope,tab])=>({scope,tabId:tab.id,title:tab.title||p.name,url:tab.url,label:p.name+(platform==='gemini'?' · Google会话 '+(Number(scope)+1):' · 当前Chrome会话')}))}
async function getSource(account,platform,sourceTabId){
 const p=validatePlatform(platform);const choices=await sourceChoices(platform);
 if(sourceTabId){const match=choices.find(x=>x.tabId===sourceTabId);if(!match)throw Error('所选平台页面已关闭，请重新检测来源');return match}
 if(account){const match=choices.find(x=>x.scope===account.scope);if(match)return match}
 if(choices.length>1&&!account)return {needsAccountSelection:true,choices};
 if(choices.length===1&&!account)return choices[0];
 const home=platform==='gemini'&&account?.scope&&account.scope!=='0'?'https://gemini.google.com/u/'+account.scope+'/app':p.home;
 const tab=await chrome.tabs.create({url:home,active:false});return {scope:account?.scope||(platform==='gemini'?'0':'chrome-session'),tabId:tab.id,title:p.name,url:home,label:account?.label||p.name+' · 当前Chrome会话'};
}
async function ensureRunner(account){
 let controller=controllers.get(account.id);
 if(!controller){const legacy=(await chrome.tabs.query({})).filter(t=>t.url?.startsWith(chrome.runtime.getURL('worker.html'))||t.url?.startsWith(chrome.runtime.getURL('runner.html')));for(const tab of legacy)await chrome.tabs.remove(tab.id).catch(()=>{});controller=globalThis.createYuanhuaWorker({platform:account.platform,accountId:account.id,runnerId:account.runnerId});controllers.set(account.id,controller);}
 return controller;
}
async function pollStoredAccounts(){await Promise.allSettled(Object.values(await accounts()).map(async account=>{const c=await ensureRunner(account);await c.ready;await c.poll();}));}
if(chrome.alarms){chrome.alarms.create('yh-poll',{periodInMinutes:.5});chrome.alarms.onAlarm.addListener(alarm=>{if(alarm.name==='yh-poll')pollStoredAccounts().catch(()=>{})});}
async function requestImpl(message){
 const p=validatePlatform(message.platform),platform=message.platform,requestId=message.requestId||nonce();
 if(message.action==='sources')return {ok:true,requestId,choices:await sourceChoices(platform)};
 const all=await accounts();let account=message.accountId?all[message.accountId]:null;
 if(message.accountId&&!account)return {ok:false,requestId,needsConnection:true,error:'此来源不属于当前Chrome配置，请在对应Chrome中连接'};
 if(account&&account.platform!==platform)throw Error('平台来源不匹配');
 if(!account){const known=Object.values(all).filter(a=>a.platform===platform);if(message.sourceTabId){const chosen=(await sourceChoices(platform)).find(x=>x.tabId===message.sourceTabId);if(!chosen)throw Error('所选平台页面已关闭，请重新检测来源');account=known.find(a=>a.scope===chosen.scope)||null;}else if(known.length===1)account=known[0]}
 if(message.action==='pause'){
  if(!account)return {ok:false,requestId,needsConnection:true,error:'没有可暂停的连接'};
  await queueIntent(account,'pause',requestId);return {ok:true,requestId,accountId:account.id,runnerId:account.runnerId};
 }
 const source=await getSource(account,platform,message.sourceTabId);
 if(source.needsAccountSelection)return {ok:false,requestId,needsAccountSelection:true,choices:source.choices,error:'检测到多个Google会话，请在控制台选择来源'};
 if(!account){account={id:nonce(),runnerId:nonce(),platform,scope:source.scope,label:source.label,createdAt:Date.now()}}
 if(account.scope!==source.scope)throw Error('来源会话不匹配，请选择对应账号');
 account.sourceTabId=source.tabId;account.sourceUrl=source.url;account.label=message.accountLabel?.trim()||account.label||source.label;
 all[account.id]=account;await chrome.storage.local.set({[accountsKey]:all});
 if(message.action==='login'){
  await chrome.tabs.update(source.tabId,{active:true});const tab=await chrome.tabs.get(source.tabId);if(tab.windowId!=null)await chrome.windows.update(tab.windowId,{focused:true});
  return {ok:true,requestId,accountId:account.id,runnerId:account.runnerId,loginOpened:true};
 }
 if(!['connect','collect','launch'].includes(message.action))throw Error('不支持的操作');
 const action=message.action==='launch'?'connect':message.action;
 await queueIntent(account,action,requestId);
 await ensureRunner(account);
 return {ok:true,accepted:true,requestId,accountId:account.id,runnerId:account.runnerId,accountLabel:account.label,background:true};
}
async function route(message){
 const key='account-registry';const before=locks.get(key)||Promise.resolve();const next=before.catch(()=>{}).then(()=>requestImpl(message));locks.set(key,next);try{return await next}finally{if(locks.get(key)===next)locks.delete(key)}
}
function receive(message,sender,reply,external){
 if(external){let origin;try{origin=new URL(sender.url).origin}catch{return false}if(!['http://127.0.0.1:8765','http://localhost:8765'].includes(origin))return false;}
 if(message?.action==='ping'){reply({ok:true,version:chrome.runtime.getManifest().version,id:chrome.runtime.id,protocol:2});return false}
 if(!['connect','collect','pause','login','sources','launch'].includes(message?.action)){reply({ok:false,requestId:message?.requestId,error:'不支持的操作'});return false}
 route(message).then(reply).catch(e=>reply({ok:false,requestId:message.requestId,error:e.message||String(e)}));return true;
}
chrome.runtime.onMessageExternal.addListener((m,s,r)=>receive(m,s,r,true));
chrome.runtime.onMessage.addListener((m,s,r)=>receive(m,s,r,false));

chrome.storage.local.get('yh.openAfterUpdate').then(async x=>{if(x['yh.openAfterUpdate']){await chrome.storage.local.set({'yh.openAfterUpdate':false});await chrome.tabs.create({url:'http://127.0.0.1:8765/setup',active:true});}}).catch(()=>{});
