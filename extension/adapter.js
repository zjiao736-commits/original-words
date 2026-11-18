(() => {
 const wait=ms=>new Promise(r=>setTimeout(r,ms));
 const patterns={'gemini.google.com':/^(?:\/u\/\d+)?\/app\/[\w-]+\/?$/,'chatgpt.com':/^\/(?:g\/[^/]+\/)?c\/[\w-]+\/?$/,'chat.deepseek.com':/^\/a\/chat\/s\/[\w-]+\/?$/,'www.doubao.com':/^\/chat\/\d+\/?$/};
 const host=location.hostname,pattern=patterns[host]||/^$/;
 function links(){return [...new Map([...document.querySelectorAll('a[href]')].flatMap(a=>{let u;try{u=new URL(a.href,location.href)}catch{return []}return u.origin===location.origin&&pattern.test(u.pathname)?[[u.origin+u.pathname,{url:u.origin+u.pathname,title:a.innerText.trim()}]]:[]})).values()]}
 function scrollers(root){return [root,...root.querySelectorAll('*')].filter(e=>e.scrollHeight>e.clientHeight+40&&/auto|scroll/.test(getComputedStyle(e).overflowY))}
 function ancestorScrollers(n){const found=[];for(let e=n?.parentElement;e;e=e.parentElement)if(e.scrollHeight>e.clientHeight+40&&/auto|scroll/.test(getComputedStyle(e).overflowY))found.push(e);return found}
 function nodes(){if(host==='chat.deepseek.com')return [...document.querySelectorAll('.ds-message')];if(host==='www.doubao.com')return [...document.querySelectorAll('[data-message-role="user"],[data-message-role="assistant"]')];if(host==='gemini.google.com')return [...document.querySelectorAll('user-query,model-response')];// 混合布局同时收集新版bubble与旧版角色节点；只按DOM包含关系去重，不按文字去重。
 const candidates=[...document.querySelectorAll('[data-user-message-bubble],[data-turn="user"],[data-turn="assistant"],[data-message-author-role],[data-testid^="conversation-turn-"],[data-testid="conversation-turn"]')];
 return candidates.filter(n=>!candidates.some(child=>child!==n&&n.contains(child)))}
 function read(n){let role,content;if(host==='chatgpt.com'&&n.matches('[data-user-message-bubble]')){const t=(n.querySelector('.whitespace-pre-wrap')||n).innerText;return t?.trim()?{role:'user',text:t}:null;}
  if(host==='chat.deepseek.com'){
   if(n.querySelector('.ds-assistant-message-main-content')){role='assistant';content=n.querySelector('.ds-assistant-message-main-content')}
   else if(n.matches('.d29f3d7d')&&n.querySelector('.fbb737a4')){role='user';content=n.querySelector('.fbb737a4')}
   else return null;
  }else if(host==='www.doubao.com'){role=n.getAttribute('data-message-role');const pieces=[...n.querySelectorAll('[data-testid="message_text_content"]')];content=null;const text=pieces.map(e=>e.innerText).join('\n');return text.trim()?{role,text}:null}
  else if(host==='gemini.google.com'){role=n.matches('user-query')?'user':'assistant';content=n.querySelector(role==='user'?'user-query-content, .query-text, .query-content':'message-content, .markdown')||n}
  else{role=n.getAttribute('data-message-author-role')||n.getAttribute('data-turn');content=n.querySelector(role==='user'?'.whitespace-pre-wrap,.user-message-bubble':'[data-message-content],.markdown')||n;if(!role){const user=n.querySelector('[data-testid="user-message"],.user-message-bubble'),assistant=n.querySelector('[data-testid="assistant-message"],.markdown');if(user){role='user';content=user}else if(assistant){role='assistant';content=assistant}else return null}}

  const text=content?.innerText;return ['user','assistant'].includes(role)&&text?.trim()?{role,text}:null;
 }
 window.archiveAdapter={
  async probe(){
   const labels=[...document.querySelectorAll('a,button')].filter(e=>e.getBoundingClientRect().width>0).map(e=>(e.innerText||'').trim());
   const login=labels.some(t=>/^(log in|sign in|登录|立即登录|登入)$/i.test(t));
   const challenge=/Just a moment|verify you are human|人机验证/i.test(document.title);
   const hasHistory=links().length>0,hasMessages=nodes().some(n=>read(n)?.role==='user');
   const profile=!!document.querySelector('[data-testid="accounts-profile-button"],[data-testid="account-profile-button"],button[aria-label*="Account"],button[aria-label*="个人资料"],.ds-avatar,[data-testid="avatar"]');
   const ready=!challenge&&!login&&(hasHistory||hasMessages||profile);
   return {ready,requiresLogin:challenge||login||!ready,title:document.title,hasHistory,hasMessages,reason:challenge?'平台需要完成访问验证':login?'平台要求登录':!ready?'暂未识别可读取的登录页面，请前往平台确认登录后重新检测':''};
  },
  async discover(){
   const all=new Map();let stable=0,last='',round=0;
   // Gemini 历史项可能是按钮而非 a[href]。只点击明确的历史对话控件，读取真实跳转地址，不猜造链接。
   const buttonItems=()=>host==='gemini.google.com'?[...document.querySelectorAll('[data-test-id="conversation"],[data-test-id="conversation-item"],.conversation-container[role="button"]')].filter(e=>e.innerText.trim()):[];
   if(host==='gemini.google.com'&&!links().length){
    const items=buttonItems();let tried=0;
    for(const item of items.slice(0,30)){
     if(!item.isConnected)continue;
     const title=item.innerText.trim(),before=location.href;item.click();
     for(let n=0;n<20;n++){await wait(250);if(location.href!==before&&pattern.test(location.pathname))break}
     if(pattern.test(location.pathname)&&location.href!==before)all.set(location.origin+location.pathname,{url:location.origin+location.pathname,title});
     tried++;if(tried>=3&&!all.size)break;
    }
    if(all.size)return {links:[...all.values()],rounds:tried,warnings:['已通过历史按钮的真实跳转识别链接；仅覆盖当前加载的条目，请再次扫描补充。']};
   }
   const positions=new Map();let ss=[],atBottom=false;const deadline=Date.now()+60000;
   function historyScrollers(){
    const anchors=[...document.querySelectorAll('a[href]')].filter(a=>a.origin===location.origin&&pattern.test(a.pathname));
    const ancestors=anchors.flatMap(a=>{const out=[];for(let n=a.parentElement;n;n=n.parentElement)if(n.scrollHeight>n.clientHeight+2&&/auto|scroll|overlay/.test(getComputedStyle(n).overflowY))out.push(n);return out});
    if(ancestors.length)return [...new Set(ancestors)];
    const roots=[...document.querySelectorAll('nav,aside,[role="navigation"],[data-testid*="sidebar"],[class*="sidebar"]')];
    const fallback=roots.flatMap(scrollers);if(fallback.length)return [...new Set(fallback)];
    const doc=document.scrollingElement;return doc&&doc.scrollHeight>doc.clientHeight+2?[doc]:[];
   }
   try{for(;round<240&&Date.now()<deadline;round++){
    for(const x of links())all.set(x.url,x);
    ss=historyScrollers();for(const e of ss)if(!positions.has(e))positions.set(e,e.scrollTop);
    atBottom=ss.length>0&&ss.every(e=>e.scrollTop+e.clientHeight>=e.scrollHeight-4);
    const fp=JSON.stringify([...all.keys()])+JSON.stringify(ss.map(e=>[Math.round(e.scrollTop),e.scrollHeight]));
    stable=atBottom&&fp===last?stable+1:0;last=fp;if(stable>=8||!ss.length)break;
    for(const e of ss)e.scrollTop=Math.min(e.scrollHeight,e.scrollTop+Math.max(160,e.clientHeight*.8));
    await wait(600);
   }}finally{for(const [e,pos] of positions)if(e.isConnected)e.scrollTop=pos}
   return {links:[...all.values()],rounds:round,historyComplete:false,scanReachedBottom:atBottom&&stable>=8,warnings:['只确认本轮发现的链接；未与账号服务端总数核对。',...(!(atBottom&&stable>=8)?['扫描未确认列表末尾，不能显示为全量完成。']:[]),...(Date.now()>=deadline?['达到60秒扫描预算，保留已发现链接，可继续扫描。']:[]),...(!ss.length?['未找到可识别的历史滚动区域，需要检查分页按钮或使用历史目录补充。']:[])]};
  },
  async extract(){
   const extractStarted=performance.now();
   if(!pattern.test(location.pathname))throw Error('不是受支持的对话地址');
   const readyDeadline=Date.now()+20000;while(Date.now()<readyDeadline&&!nodes().some(n=>read(n)?.role==='user')){const t=document.title;if(/Just a moment|验证您是人类|Verify you are human/i.test(t))throw Error('GPT显示访问验证页，请在普通Chrome完成验证后再继续');await wait(500)}
   const initial=nodes();if(!initial.length)throw Error('未识别消息节点；诊断：标题='+document.title+'；页面状态='+document.readyState+'；正文字符='+document.body.innerText.length+'；turn='+document.querySelectorAll('[data-testid^="conversation-turn-"],[data-testid="conversation-turn"]').length+'；author='+document.querySelectorAll('[data-message-author-role]').length+'；结构='+JSON.stringify([...document.querySelectorAll('main *')].filter(e=>/user|assistant|message|turn|markdown|whitespace|select-text|conversation|text-start/.test(String(e.className)+' '+e.getAttribute('role'))).slice(0,45).map(e=>({tag:e.tagName,attrs:[...e.attributes].filter(a=>a.name.startsWith('data-')||a.name==='role').map(a=>[a.name,a.value.slice(0,70)]),classes:String(e.className).slice(0,220)})))+'。请核对新打开的GPT对话是否显示正文或验证提示');
   const nodeCounts=()=>{const ns=nodes(),messages=ns.map(read).filter(Boolean);return {nodes:ns.length,user:messages.filter(x=>x.role==='user').length,assistant:messages.filter(x=>x.role==='assistant').length,modern:document.querySelectorAll('[data-user-message-bubble]').length,turnUser:document.querySelectorAll('[data-turn="user"]').length,authorUser:document.querySelectorAll('[data-message-author-role="user"]').length}};
   const describeScroller=e=>({tag:e.tagName,role:e.getAttribute('role'),testid:e.getAttribute('data-testid'),height:e.scrollHeight,viewport:e.clientHeight,top:e.scrollTop,messageNodes:nodes().filter(n=>e.contains(n)).length,overflow:getComputedStyle(e).overflowY});
   const scrollDiagnostics={entry:nodeCounts(),candidates:ancestorScrollers(initial[0]).map(describeScroller),documentScroller:document.scrollingElement?describeScroller(document.scrollingElement):null,head:[],middle:[],tail:[]};
   const candidates=ancestorScrollers(initial[0]).filter(e=>e.contains(initial[0])&&!e.querySelector('a[href*="/chat/s/"]'));
   let scroll=candidates.sort((a,b)=>a.clientHeight-b.clientHeight)[0];
   scrollDiagnostics.selected=scroll?describeScroller(scroll):null;
   const seenNodes=new Map();const collected=[];let round=0,stable=0,last='';
   // 从最早消息开始分段读取；相同的文字不去重，避免删掉用户在不同轮次的重复表达。
   if(scroll){for(let i=0;i<12;i++){const old=scroll.scrollHeight;scroll.scrollTop=0;await wait(250);scrollDiagnostics.head.push({round:i,...nodeCounts(),height:scroll.scrollHeight,top:scroll.scrollTop});if(scroll.scrollHeight===old&&i>1)break}}
   const scrollDeadline=Date.now()+45000;
   for(;round<6000&&Date.now()<scrollDeadline;round++){
    const ns=nodes(),parsed=ns.map(read);
    if(round%10===0&&scrollDiagnostics.middle.length<80)scrollDiagnostics.middle.push({round,...nodeCounts(),top:scroll?.scrollTop,height:scroll?.scrollHeight});
    if(scroll&&!scroll.isConnected){scroll=ancestorScrollers(ns[0]).filter(e=>ns[0]&&e.contains(ns[0])&&!e.querySelector('a[href*="/chat/s/"]')).sort((a,b)=>a.clientHeight-b.clientHeight)[0]}
for(let ni=0;ni<ns.length;ni++){const n=ns[ni],m=parsed[ni];if(m){const fp=m.role+'|'+m.text;if(seenNodes.get(n)!==fp){seenNodes.set(n,fp);collected.push(m)}}}
    const atBottom=!scroll||scroll.scrollTop+scroll.clientHeight>=scroll.scrollHeight-4;
    const fp=JSON.stringify(parsed)+'|'+(scroll?.scrollHeight||0);
    stable=atBottom&&fp===last?stable+1:0;last=fp;if(stable>=3)break;
    if(scroll)scroll.scrollTop=Math.min(scroll.scrollHeight,scroll.scrollTop+Math.max(180,scroll.clientHeight*.9));
    await wait(atBottom?500:50);
   }
   scrollDiagnostics.tail={...nodeCounts(),selected:scroll?describeScroller(scroll):null,round,stable};
   const current=nodes().map(read).filter(Boolean);const warnings=['DOM采集，未验证服务端总轮数；附件未下载。'];if(host==='chatgpt.com'&&document.querySelector('[data-user-message-bubble]'))warnings.push('新版GPT：仅提取明确的用户原话节点，AI回复暂未采集；原始上下文不完整。');
   const partial=round>=6000||Date.now()>=scrollDeadline;if(partial)warnings.push('滚动达到时间或次数上限，已保留局部记录，未确认完整。');
   if(collected.length>current.length)warnings.push('检测到分段加载，消息按首次读取顺序保存，需核对。');
   if(!collected.some(m=>m.role==='user'))throw Error('未识别到用户原话，未保存为成功');
   return {url:location.origin+location.pathname,title:document.title,body:collected.map(m=>m.role+'\n'+m.text).join('\n\n'),messages:collected,metadata:{scrollDiagnostics,adapter:host+'-dom-v2',completeness:partial?'partial':'unverified',warnings,collectedAt:new Date().toISOString(),rounds:round,extractMilliseconds:Math.round(performance.now()-extractStarted),scrollState:scroll?{connected:scroll.isConnected,top:scroll.scrollTop,height:scroll.scrollHeight,viewport:scroll.clientHeight}:null}};
  }
 };
})();
