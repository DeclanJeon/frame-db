/** Classify reference images without copying their bytes or changing originals. */
import { createHash } from 'node:crypto';
import { link, mkdir, readFile, writeFile } from 'node:fs/promises';
import { basename } from 'node:path';

const root = new URL('../../', import.meta.url);
const stage = new URL('.drive-staging/FRAME_DB/', root);
const groups = {
  '全身1人・標準系': '01_full_standard',
  '全身1人・セクシー系': '02_full_editorial',
  '上半身1人': '03_upper_body',
  '2人絡み': '04_pair',
  '春': '01_spring', '夏': '02_summer', '秋': '03_autumn', '冬': '04_winter',
  'ランジェリー': '05_lingerie', 'パーティ': '06_party', '水着': '07_swimwear', 'セクシー': '08_editorial',
};
const roles = { thumbs: '01_thumbnails', img: '02_display', png: '03_originals' };
const references = JSON.parse(await readFile(new URL('data/references.json', root), 'utf8'));
const archive = JSON.parse(await readFile(new URL('data/gallery-downloads.json', root), 'utf8'));
const seed = JSON.parse(await readFile(new URL('data/database-seed.json', root), 'utf8'));
const refByURL = new Map(references.flatMap(record => Object.values(record.resources).map(url => [url, record])));
const entryByID = new Map(seed.entries.map(entry => [entry.id, entry]));
const plan = [];

async function stageImage(localPath, sourceURL, folder, source, role) {
  const bytes = await readFile(new URL(localPath, root));
  const relativePath = `${folder}/${basename(localPath)}`;
  const target = new URL(relativePath, stage);
  await mkdir(new URL('.', target), { recursive: true });
  try {
    await link(new URL(localPath, root), target);
  } catch (error) {
    if (error.code !== 'EEXIST') throw error;
    const existing = await readFile(target);
    if (!existing.equals(bytes)) throw new Error(`Staging conflict: ${relativePath}`);
  }
  plan.push({
    asset_id: createHash('sha256').update(sourceURL).digest('hex').slice(0, 24),
    source, role, source_url: sourceURL, local_path: localPath,
    relative_path: relativePath, bytes: bytes.length,
    sha256: createHash('sha256').update(bytes).digest('hex'),
    md5: createHash('md5').update(bytes).digest('hex'),
  });
}

for (const resource of archive.resources) {
  const reference = refByURL.get(resource.url);
  if (!reference) throw new Error(`Unmapped archived resource: ${resource.url}`);
  const category = groups[reference.original['系統'] || reference.original['カテゴリ']];
  if (!category) throw new Error(`Unmapped source category: ${reference.id}`);
  const sourceRoot = resource.source === 'pose' ? '01_pose' : '02_costume';
  const kind = new URL(resource.url).pathname.split('/')[1];
  const role = kind === 'img' && resource.source === 'pose' ? '03_originals' : roles[kind];
  await stageImage(resource.local_path, resource.url, `${sourceRoot}/${category}/${role}`, resource.source, role);
}
for (const media of seed.media_assets.filter(media => media.availability === 'owned_diagram')) {
  const category = entryByID.get(media.entry_id).category_id;
  await stageImage('public' + media.url, media.url, `03_studio_diagrams/${category}/03_originals`, 'studio', '03_originals');
}
if (plan.length !== 7167 || new Set(plan.map(asset => asset.relative_path)).size !== plan.length) {
  throw new Error(`Incomplete or duplicate staging plan: ${plan.length}`);
}
const manifest = {
  parent_folder_id: '15we6iUFHRL3KMU9Al8uSbHqk0Y4iSsGC',
  root_name: 'FRAME_DB',
  files: plan,
};
await writeFile(new URL('data/drive-upload-plan.json', root), JSON.stringify(manifest, null, 2) + '\n');
await mkdir(new URL('00_manifests/', stage), { recursive: true });
await writeFile(new URL('00_manifests/upload-plan.json', stage), JSON.stringify(manifest, null, 2) + '\n');
console.log(JSON.stringify({
  files: plan.length, folders: new Set(plan.map(asset => asset.relative_path.slice(0, asset.relative_path.lastIndexOf('/')))).size,
  bytes: plan.reduce((sum, asset) => sum + asset.bytes, 0), stage: stage.pathname,
}));
