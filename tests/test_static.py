import json, pathlib, unittest
ROOT=pathlib.Path(__file__).parents[1]
class StaticTests(unittest.TestCase):
  def test_template(self):
    data=json.loads((ROOT/'list.json').read_text())
    self.assertEqual({x['platform'] for x in data['templates']},{'linux/amd64','linux/arm64'})
    self.assertTrue(all(x['type']==1 for x in data['templates']))
  def test_no_secret_placeholders(self):
    compose=(ROOT/'docker-compose.yml').read_text().lower()
    self.assertNotIn('database_password',compose)
    self.assertNotIn('encryption_key',compose)
  def test_update_backs_up_before_recreate(self):
    source=(ROOT/'manager'/'app.py').read_text()
    block=source[source.index('def update():'):source.index('@app.post("/backup")')]
    self.assertLess(block.index('backup(cfg)'),block.index('deploy(cfg,pull=True)'))
  def test_every_configuration_field_has_bilingual_help(self):
    html=(ROOT/'manager'/'templates'/'index.html').read_text()
    fields=('internal_ip','domain','teslamate_port','grafana_port','timezone','teslamate_image','grafana_image','postgres_image','mosquitto_image')
    for field in fields:
      self.assertIn(f'id="{field}"',html)
    self.assertEqual(html.count('class="help"'),10)
    self.assertEqual(html.count('data-de='),10)
    self.assertEqual(html.count('data-en='),10)
  def test_beginner_guides_exist_in_both_languages(self):
    de=(ROOT/'docs'/'INSTALLATION.de.md').read_text()
    en=(ROOT/'docs'/'INSTALLATION.en.md').read_text()
    self.assertIn('Anwendungsvorlagen',de)
    self.assertIn('App Templates',en)
    self.assertIn('https://raw.githubusercontent.com/',de)
    self.assertIn('https://raw.githubusercontent.com/',en)
if __name__=='__main__': unittest.main()
