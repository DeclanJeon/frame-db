import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/data'))
from drive_pack import DriveManifestError, apply_drive


class DrivePack(unittest.TestCase):
    def setUp(self):
        self.original = 'https://source.example/img/pose.png'
        self.thumbnail = 'https://source.example/thumbs/pose.jpg'
        self.diagram = '/references/diagrams/camera.svg'
        self.refs = [{
            'id': 'pose-1', 'source': 'pose',
            'thumbnail_url': self.thumbnail, 'display_url': self.original,
            'resources': {'サムネ': self.thumbnail, '原寸': self.original},
        }]
        self.seed = {
            'entries': [{'id': 'pose', 'details': json.dumps({'source': 'preserved'})},
                        {'id': 'camera', 'details': '{}'}],
            'variants': [{'id': 'v-pose', 'attributes': json.dumps({'resources': self.refs[0]['resources']})},
                         {'id': 'v-camera', 'attributes': '{}'}],
            'media_assets': [
                {'entry_id': 'pose', 'variant_id': 'v-pose', 'source_id': 'pose-db',
                 'original_id': 'pose-1', 'availability': 'external_link', 'url': self.original},
                {'entry_id': 'camera', 'variant_id': 'v-camera', 'source_id': 'studio',
                 'original_id': 'camera-1', 'availability': 'owned_diagram', 'url': self.diagram},
            ],
            'sources': [{'id': 'pose-db', 'hosting': 'external_only'}, {'id': 'studio', 'hosting': 'owned'}],
            'import_batches': [{'source_id': 'pose-db', 'report': '{}'}],
        }
        self.manifest = {
            'root_folder_id': 'test-root',
            'files': [
                {'source_url': url, 'asset_id': hashlib.sha256(url.encode()).hexdigest()[:24],
                 'file_id': str(index) * 30, 'bytes': 10,
                 'sha256': hashlib.sha256(url.encode()).hexdigest()}
                for index, url in enumerate([self.original, self.thumbnail, self.diagram], 1)
            ],
        }
        self.audit = {
            'total': 3, 'passed': 3, 'failed': [],
            'files': [{'file_id': file['file_id'], 'bytes': file['bytes'], 'sha256': file['sha256'], 'ok': True}
                      for file in self.manifest['files']],
        }

    def test_verified_mirror_preserves_source_and_connects_all_media(self):
        # Given a complete byte-verified mirror, when applied, all media use the proxy.
        refs_before = copy.deepcopy(self.refs)
        apply_drive(self.seed, self.refs, self.manifest, self.audit)
        self.assertTrue(all(media['url'].startswith('/api/media/') for media in self.seed['media_assets']))
        attributes = json.loads(self.seed['variants'][0]['attributes'])
        self.assertEqual(attributes['original_url'], self.original)
        self.assertEqual(attributes['resources'], self.refs[0]['resources'])
        self.assertEqual(attributes['thumbnail_url'], '/api/media/' + self.manifest['files'][1]['asset_id'])
        self.assertEqual(json.loads(self.seed['entries'][0]['details'])['source'], 'preserved')
        self.assertEqual(self.refs, refs_before)

    def test_owned_diagram_keeps_its_provenance_classification(self):
        apply_drive(self.seed, self.refs, self.manifest, self.audit)
        self.assertEqual(self.seed['media_assets'][1]['availability'], 'owned_diagram')
        self.assertEqual(json.loads(self.seed['variants'][1]['attributes'])['original_url'], self.diagram)
        self.assertEqual(self.seed['media_assets'][0]['availability'], 'google_drive')
        self.assertTrue(all(source['hosting'] == 'google_drive' for source in self.seed['sources']))
        self.assertEqual(json.loads(self.seed['import_batches'][0]['report'])['drive_representations'], 2)
        self.assertEqual(json.loads(self.seed['import_batches'][0]['report'])['media_downloaded'], 1)

    def test_missing_representation_does_not_mutate_seed(self):
        before = copy.deepcopy(self.seed)
        self.manifest['files'].pop(1)
        with self.assertRaises(DriveManifestError):
            apply_drive(self.seed, self.refs, self.manifest, self.audit)
        self.assertEqual(self.seed, before)

    def test_unverified_bytes_do_not_mutate_seed(self):
        before = copy.deepcopy(self.seed)
        self.audit['files'][0]['sha256'] = 'bad'
        with self.assertRaises(DriveManifestError):
            apply_drive(self.seed, self.refs, self.manifest, self.audit)
        self.assertEqual(self.seed, before)

    def test_duplicate_drive_file_ids_do_not_mutate_seed(self):
        before = copy.deepcopy(self.seed)
        self.manifest['files'][1]['file_id'] = self.manifest['files'][0]['file_id']
        with self.assertRaises(DriveManifestError):
            apply_drive(self.seed, self.refs, self.manifest, self.audit)
        self.assertEqual(self.seed, before)


if __name__ == '__main__':
    unittest.main()
