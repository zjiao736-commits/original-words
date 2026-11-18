"""单个后台导入队列；进度只统计已解析/已处理数量，不伪造百分比。"""
from concurrent.futures import ThreadPoolExecutor
import threading,time,uuid,json
from pathlib import Path
from import_chatgpt import import_export
POOL=ThreadPoolExecutor(max_workers=1);LOCK=threading.Lock();JOBS={}
def snapshot():
 with LOCK:return [dict(j) for j in JOBS.values()][-15:]
def submit(raw,platform,root,connect,classify):
 key=uuid.uuid4().hex
 with LOCK:JOBS[key]=dict(id=key,platform=platform,stage='queued',message='已接收，等待后台导入',created=time.time(),done=0,total=None)
 def update(**values):
  with LOCK:JOBS[key].update(values,updated=time.time())
 def run():
  try:
   result=import_export(raw,root,connect,classify,platform=platform,progress=update)
   from export_archives import export_all
   update(stage='exporting',message='正在生成可下载的原话文件')
   export_all(root=root)
   update(stage='done',message='已完成，原始文件与原话均保存在本机',result=result,finished=time.time())
  except Exception as e:update(stage='error',message=str(e),finished=time.time())
 POOL.submit(run);return key
