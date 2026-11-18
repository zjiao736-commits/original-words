"""Startup safety checks for published source, without controlling a browser."""
import unittest,io,json,hashlib
from pathlib import Path
from unittest.mock import patch
import desktop_launcher as app
class StartupSafety(unittest.TestCase):
 def test_another_instance_never_opens_or_spawns(self):
  with patch.object(app,'service_status',return_value='other'),patch.object(app.subprocess,'run') as browser,patch.object(app.subprocess,'Popen') as spawn:
   self.assertEqual(app.main(),1);browser.assert_not_called();spawn.assert_not_called()
 def test_identity_matches_current_folder_only(self):
  identity=hashlib.sha256(str(app.ROOT.resolve()).encode()).hexdigest()
  for value,status in [(identity,'same'),('different-folder','other')]:
   with patch.object(app.opener,'open',return_value=io.BytesIO(json.dumps({'app':'yuanhua','instance':value}).encode())):self.assertEqual(app.service_status(),status)
 def test_double_click_uses_launcher(self):
  command=(Path(__file__).parent/'启动.command').read_text();self.assertIn('python3 desktop_launcher.py',command);self.assertNotIn('python3 server.py',command)
if __name__=='__main__':unittest.main()
