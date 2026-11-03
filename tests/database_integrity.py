import sqlite3,json,unittest,hashlib
from pathlib import Path
from web_pack_test import original_seed, load_approved, apply_web
from creative_pack import DETAIL_KEY, apply_creative, creative_revision, load_creative
from asset_pack import SOURCE_ID, apply_assets, asset_revision, load_asset_pack
ROOT=Path(__file__).resolve().parents[1]
class Integrity(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.base=original_seed();cls.approved=load_approved(ROOT/'data/web-research')
  cls.creative=load_creative(ROOT/'data/web-research',cls.approved)
  cls.baseline=apply_creative(apply_web(cls.base,cls.approved),cls.creative)
  cls.pack=None
  revision_path=ROOT/'data/asset-production/revision.json'
  if revision_path.is_file():
   cls.pack=load_asset_pack(ROOT/'data/asset-production')
   cls.expected=apply_assets(cls.baseline,cls.pack)
  else:
   cls.expected=cls.baseline
  cls.seed=json.loads((ROOT/'data/database-seed.json').read_text());cls.db=sqlite3.connect(':memory:');cls.db.execute('PRAGMA foreign_keys=ON');cls.db.executescript((ROOT/'drizzle/0000_yielding_shadowcat.sql').read_text());mapping={'entries':'reference_entries','variants':'entry_variants'}
  for key,rows in cls.seed.items():
   table=mapping.get(key,key)
   if not rows:continue
   columns=[k if k!='group' else 'group_name' for k in rows[0]]
   cls.db.executemany('INSERT INTO '+table+' ('+','.join(columns)+') VALUES ('+','.join('?' for _ in columns)+')',[[r[key] for key in rows[0]] for r in rows])
 def test_source_coverage(self):
  self.assertEqual(self.db.execute("SELECT source_id,COUNT(*) FROM media_assets WHERE source_id!='frame-generated' GROUP BY source_id ORDER BY source_id").fetchall(),[('costume-db',1407),('pose-db',1439),('studio',68)])
  self.assertEqual(self.db.execute("SELECT COUNT(*) FROM media_assets WHERE source_id='frame-generated'").fetchone()[0],0 if self.pack is None else asset_revision(self.pack)['accepted_count'])
 def test_pose_groups(self):
  self.assertEqual(self.db.execute("SELECT COUNT(*) FROM reference_entries WHERE source_id='pose-db'").fetchone()[0],288)
  self.assertEqual(self.db.execute("SELECT COUNT(*) FROM (SELECT entry_id,COUNT(*) n FROM entry_variants WHERE entry_id LIKE 'pose-%' GROUP BY entry_id HAVING n=4)").fetchone()[0],1)
 def test_grouped_total(self):
  self.assertEqual(len(self.base['entries']),2485)
  self.assertEqual(len(self.baseline['entries']),2749)
  self.assertEqual(len(self.baseline['media_assets']),2914)
  self.assertEqual(self.seed,self.expected)
  self.assertEqual(self.db.execute('SELECT COUNT(*) FROM reference_entries').fetchone()[0],len(self.expected['entries']))
  if self.pack is not None:
   self.assertEqual(json.loads((ROOT/'data/asset-production/revision.json').read_text()),asset_revision(self.pack))
   self.assertEqual(apply_assets(self.seed,self.pack),self.seed)
 def test_original_identity_status_authorship_and_media_are_exact(self):
  entries={e['id']:e for e in self.seed['entries']}
  for original in self.base['entries']:
   current=entries[original['id']]
   self.assertEqual({k:v for k,v in original.items() if k!='details'},{k:v for k,v in current.items() if k!='details'})
   details=json.loads(current['details']);details.pop('web_research',None)
   details.pop('usage_guide',None);details.pop('asset_production',None)
   if original['id'] in self.creative.overlays:
    self.assertEqual(details.pop(DETAIL_KEY),self.creative.overlays[original['id']])
   self.assertEqual(details,json.loads(original['details']))
  for key in self.base.keys()-{'entries','sources','import_batches'}:
   if key in {'variants','media_assets','prompt_templates','entry_relations'}:
    ids={row['id'] for row in self.base[key]}
    self.assertEqual([row for row in self.seed[key] if row['id'] in ids],self.base[key])
   else:
    self.assertEqual(self.seed[key],self.base[key])
  self.assertEqual(apply_web(self.seed,self.approved),self.seed)
  self.assertEqual(apply_creative(self.seed,self.creative),self.seed)
 def test_creative_review_ids_revision_and_web_count_are_exact(self):
  applied={entry['id'] for entry in self.seed['entries'] if DETAIL_KEY in json.loads(entry['details'])}
  self.assertEqual(applied,set(self.creative.review['accepted_entry_ids']))
  self.assertEqual(len(applied),16)
  self.assertFalse(applied & set(self.creative.review['rejected_entry_ids']))
  self.assertEqual(json.loads((ROOT/'data/web-research/creative-revision.json').read_text()),creative_revision(self.creative))
  self.assertEqual(sum(len(json.loads(entry['details']).get('web_research',{})) for entry in self.seed['entries']),482)
 def test_all_domains(self):
  self.assertEqual(self.db.execute('SELECT COUNT(DISTINCT category_id) FROM reference_entries').fetchone()[0],29)
  self.assertEqual(self.db.execute('SELECT SUM(target) FROM categories').fetchone()[0],40607)
 def test_no_fake_media(self):
  self.assertEqual(self.db.execute("SELECT COUNT(*) FROM media_assets WHERE availability='owned_diagram'").fetchone()[0],68)
  self.assertEqual(sum(e['status']=='text' for e in self.base['entries']),214)
  expected=apply_web(self.base,self.approved)
  self.assertEqual(self.db.execute("SELECT COUNT(*) FROM reference_entries WHERE status='text'").fetchone()[0],sum(e['status']=='text' for e in expected['entries']))
 def test_foreign_keys(self):
  self.assertEqual(self.db.execute('PRAGMA foreign_key_check').fetchall(),[])
 def test_entry_fields_roundtrip_independent_of_property_order(self):
  actual={row[0]:row[1:] for row in self.db.execute('SELECT id,details,version,updated,search_text FROM reference_entries')}
  for entry in self.seed['entries']:
   self.assertEqual(actual[entry['id']],tuple(entry[key] for key in ('details','version','updated','search_text')))
 def test_id_search_and_angle(self):
  # Original image IDs must resolve to the grouped parent via metadata search.
  e=json.loads((ROOT/'data/references.json').read_text())[0]
  vid=self.db.execute('SELECT entry_id FROM media_assets WHERE original_id=?',(e['id'],)).fetchone()[0]
  text=self.db.execute('SELECT search_text FROM reference_entries WHERE id=?',(vid,)).fetchone()[0]
  self.assertIn('p001',text)
  self.assertEqual(self.db.execute('SELECT COUNT(*) FROM entry_variants WHERE entry_id=? AND angle=?',(vid,'정면')).fetchone()[0],1)
 def test_collections_unique_and_owner_scoped(self):
  self.db.execute("INSERT INTO collections VALUES ('test-a','owner-a','A','2026-10-29')");self.db.execute("INSERT INTO collections VALUES ('test-b','owner-b','B','2026-10-29')")
  self.assertIsNone(self.db.execute('SELECT id FROM collections WHERE id=? AND owner_id=?',('test-a','owner-b')).fetchone())
  self.db.execute("INSERT INTO collection_entries VALUES ('test-a','FS-0001','','2026-10-29')")
  with self.assertRaises(sqlite3.IntegrityError):self.db.execute("INSERT INTO collection_entries VALUES ('test-a','FS-0001','','2026-10-29')")
 def test_structured_content(self):
  baseline_ids={entry['id'] for entry in self.base['entries'] if entry['status']=='guide'}
  rows=[(cat,raw,desc) for eid,cat,raw,desc in self.db.execute("SELECT id,category_id,details,description FROM reference_entries WHERE status='guide'") if eid in baseline_ids]
  self.assertEqual(len(rows),576)
  self.assertEqual(len(set(r[0] for r in rows)),29)
  for cat,raw,desc in rows:
   d=json.loads(raw)
   self.assertGreater(len(desc),40)
   self.assertTrue(all(k in d for k in ['설계 지시','보존할 요소','변경 가능한 요소','오류 포인트','검수 기준']))
   if cat=='voice':self.assertTrue(all(k in d for k in ['voice_identity_direction','speech_style','performance_cue','실제 voice ID','음성 샘플']))
   if cat=='speech':self.assertTrue(all(k in d['performance_cue'] for k in ['exact_text','intent','subtext','pressure','stressed_words','pause','breath','pace']))
 def test_owned_diagram_files(self):
  import xml.etree.ElementTree as ET
  rows=self.db.execute("SELECT m.url,v.attributes FROM media_assets m JOIN entry_variants v ON v.id=m.variant_id WHERE m.availability='owned_diagram'").fetchall()
  self.assertEqual(len(rows),68)
  for url,attributes in rows:
   self.assertRegex(url,r'^/api/media/[a-f0-9]{24}$')
   original=json.loads(attributes)['original_url']
   path=ROOT/'public'/original.lstrip('/')
   self.assertTrue(path.is_file())
   root=ET.parse(path).getroot()
   self.assertEqual(root.attrib['viewBox'],'0 0 720 460')
 def test_all_media_use_complete_verified_drive_manifest(self):
  manifest=json.loads((ROOT/'data/drive-assets.json').read_text())
  audit=json.loads((ROOT/'data/drive-transfer-audit.json').read_text())
  index=json.loads((ROOT/'data/drive-media-index.json').read_text())
  files=manifest['files'];by_url={file['source_url']:file for file in files}
  self.assertEqual(len(files),7167)
  self.assertEqual(len({file['file_id'] for file in files}),7167)
  self.assertEqual(len(index),7167)
  self.assertEqual((audit['total'],audit['passed'],audit['failed']),(7167,7167,[]))
  checks={check['file_id']:check for check in audit['files']}
  self.assertEqual(len(checks),7167)
  for file in files:
   self.assertEqual(file['asset_id'],hashlib.sha256(file['source_url'].encode()).hexdigest()[:24])
   self.assertTrue(checks[file['file_id']]['ok'])
   self.assertEqual((checks[file['file_id']]['bytes'],checks[file['file_id']]['sha256']),(file['bytes'],file['sha256']))
   self.assertEqual(index[file['asset_id']]['file_id'],file['file_id'])
  rows=self.db.execute("SELECT m.url,m.availability,m.source_id,v.attributes FROM media_assets m JOIN entry_variants v ON v.id=m.variant_id WHERE m.source_id!='frame-generated'").fetchall()
  self.assertEqual(len(rows),2914)
  for url,availability,source,raw in rows:
   attributes=json.loads(raw);file=by_url[attributes['original_url']]
   self.assertEqual(url,'/api/media/'+file['asset_id'])
   self.assertEqual(attributes['drive_file_id'],file['file_id'])
   self.assertEqual(availability,'owned_diagram' if source=='studio' else 'google_drive')
   self.assertIn(attributes['thumbnail_url'].removeprefix('/api/media/'),index)
   self.assertIn(attributes['display_url'].removeprefix('/api/media/'),index)
 def test_prompt_authorship(self):
  self.assertEqual(self.db.execute("SELECT COUNT(*) FROM prompt_templates WHERE authorship LIKE '%원본 제작자 프롬프트 아님%'").fetchone()[0],2485)
 def test_gallery_snapshot_has_every_source_record(self):
  snapshot=json.loads((ROOT/'data/gallery-sources.json').read_text())
  expected={(s['source'],r['id']):r for s in snapshot['sources'] for r in s['records']}
  refs=json.loads((ROOT/'data/references.json').read_text())
  self.assertEqual(len(expected),2846)
  self.assertEqual(set(expected),{(r['source'],r['id']) for r in refs})
  for r in refs:self.assertEqual(r['original'],expected[(r['source'],r['id'])])
 def test_gallery_resources_survive_database_normalization(self):
  refs=json.loads((ROOT/'data/references.json').read_text())
  for r in refs:
   attributes=json.loads(self.db.execute('SELECT attributes FROM entry_variants WHERE id=?',('v-'+r['id'],)).fetchone()[0])
   self.assertEqual(attributes['원본 데이터'],r['original'])
   self.assertEqual(attributes['리소스'],r['resources'])
   entry_id=self.db.execute('SELECT entry_id FROM entry_variants WHERE id=?',('v-'+r['id'],)).fetchone()[0]
   details=json.loads(self.db.execute('SELECT details FROM reference_entries WHERE id=?',(entry_id,)).fetchone()[0])
   self.assertIn(r['url'],json.dumps(details,ensure_ascii=False))
 def test_gallery_resource_paths_are_complete(self):
  refs=json.loads((ROOT/'data/references.json').read_text())
  urls={url for r in refs for url in r['resources'].values()}
  self.assertEqual(len(urls),7099)
  for r in refs:
   self.assertEqual(r['thumbnail_url'],r['resources']['サムネ'])
   self.assertEqual(r['display_url'],r['resources'].get('画像',r['resources']['原寸']))
   self.assertEqual(r['url'],r['resources']['原寸'])
   for field,url in r['resources'].items():self.assertEqual(url,r['home']+r['original'][field])
if __name__=='__main__':unittest.main()
