import { test } from 'node:test';
import assert from 'node:assert/strict';
import { extractJSON, normalizeRecord } from '../scripts/data/sync-galleries.mjs';
import { imageFormat, resourceList } from '../scripts/data/archive-galleries.mjs';

test('extracts JSON without executing source JavaScript', () => {
  assert.deepEqual(extractJSON('const D=[{"id":"P001"}];\nconst X=window;', 'D'), [{ id: 'P001' }]);
  assert.throws(() => extractJSON('const D=alert(1);', 'D'), SyntaxError);
  assert.throws(() => extractJSON('const X=[];', 'D'), /Missing JSON/);
});

const costume = {
  id: 'SPR-0001', 'カテゴリ': '春', 'キーワード': 'white dress',
  'サムネ': 'thumbs/SPR-0001.webp', '画像': 'img/SPR-0001.webp', '原寸': 'png/SPR-0001.png',
};
const home = 'https://ai-costume-gallery.pages.dev/';

test('preserves all source fields and all three costume representations', () => {
  const result = normalizeRecord('costume', costume, home);
  assert.deepEqual(result.original, costume);
  assert.equal(Object.keys(result.resources).length, 3);
  assert.equal(result.url, home + costume['原寸']);
  assert.equal(result.thumbnail_url, home + costume['サムネ']);
  assert.equal(result.display_url, home + costume['画像']);
});

test('rejects missing fields and cross-origin resource URLs', () => {
  assert.throws(() => normalizeRecord('costume', { ...costume, '画像': '' }, home), /Invalid/);
  assert.throws(() => normalizeRecord('costume', { ...costume, '原寸': 'https://example.com/a.png' }, home), /Unexpected/);
});

test('archives duplicate resource URLs only once outside public assets', () => {
  const record = normalizeRecord('costume', costume, home);
  const list = resourceList([record, record]);
  assert.equal(list.length, 3);
  assert.ok(list.every(resource => resource.local_path.startsWith('.gallery-cache/costume/')));
});

test('rejects archive paths outside known image directories', () => {
  assert.throws(() => resourceList([{ home, source: 'costume', resources: { bad: home + 'private/a.png' } }]), /Unexpected image path/);
});

test('detects image signatures and rejects HTML error bodies', () => {
  assert.equal(imageFormat(Buffer.from([137, 80, 78, 71, 13, 10, 26, 10])), 'png');
  assert.equal(imageFormat(Buffer.from([255, 216, 255])), 'jpeg');
  assert.equal(imageFormat(Buffer.from('RIFF0000WEBP')), 'webp');
  assert.throws(() => imageFormat(Buffer.from('<html>not an image</html>')), /not PNG/);
});
