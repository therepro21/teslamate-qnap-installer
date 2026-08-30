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
if __name__=='__main__': unittest.main()
