"""Build a source-only archive; personal databases, browser profiles and exports are never included."""
import argparse,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
FILES=['provider_catalog.py','import_providers.py','server.py','collector_v2.py','jobs.py','import_chatgpt.py','import_gemini.py','export_archives.py','desktop_launcher.py','browser_worker.py','setup.html','dashboard.js','dashboard.css','ui-refinement.css','i18n.js','connect.html','connect.js','results.html','extension-id.txt','启动.command','使用说明.md','README.md','README.en.md','CONTRIBUTING.md','LICENSE','.gitignore','package_release.py','docs/PROVIDERS.md','docs/RELEASE_CHECK.md','docs/MEDIA.md','test_provider_imports.py','test_first_run_safety.py']
ASSETS=['yuanhua.svg','yuanhua.icns','chatgpt.svg','deepseek.svg','doubao.png','gemini.png','品牌素材来源.json']
def build(destination):
 paths=[ROOT/name for name in FILES if (ROOT/name).is_file()]
 paths += [ROOT/'assets'/name for name in ASSETS if (ROOT/'assets'/name).is_file()]
 paths += [p for p in (ROOT/'extension').rglob('*') if p.is_file() and not p.is_symlink() and (p.parent==ROOT/'extension' and (p.suffix in {'.js','.html'} or p.name=='manifest.json') or p.parent==ROOT/'extension/icons' and p.suffix in {'.png','.svg'})]
 required=['README.md','LICENSE','server.py','extension/manifest.json']
 if any(p.is_symlink() for p in paths):raise ValueError('Symlinks are not allowed in source releases')
 relative={p.relative_to(ROOT).as_posix() for p in paths}
 missing=[p for p in required if p not in relative]
 if missing:raise ValueError('Release documentation missing: '+', '.join(missing))
 destination=Path(destination).expanduser();destination.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(destination,'w',zipfile.ZIP_DEFLATED) as archive:
  for p in sorted(paths):archive.write(p,'yuanhua/'+p.relative_to(ROOT).as_posix())
 return {'archive':str(destination.resolve()),'files':len(paths),'personal_data_included':False}
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--output',default='/tmp/yuanhua-source.zip');args=parser.parse_args();print(json.dumps(build(args.output),ensure_ascii=False))
