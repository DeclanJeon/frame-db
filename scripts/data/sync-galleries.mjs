/**
 * Collect every public gallery record and every published image URL.
 * Images remain on the source hosts; this command never downloads image bodies.
 */
import { createHash } from 'node:crypto';
import { readFile, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';

const root = new URL('../../', import.meta.url);
const sources = ['pose', 'costume'];
const translated = {
  '立ち': '서기', '座り': '앉기', '寝そべり': '눕기', '寝': '눕기',
  '膝立ち': '무릎 꿇기', 'しゃがみ': '쪼그리기',
  '正面': '정면', '上から': '하이앵글', '下から': '로우앵글',
  '横': '측면', '斜め': '사선',
  '春': '봄', '夏': '여름', '秋': '가을', '冬': '겨울',
  'ランジェリー': '란제리', 'パーティ': '파티', '水着': '수영복', 'セクシー': '섹시',
};

export function extractJSON(html, name) {
  const match = html.match(new RegExp(`^const ${name}\\s*=\\s*(.+);\\s*$`, 'm'));
  if (!match) throw new Error(`Missing JSON declaration: ${name}`);
  return JSON.parse(match[1]);
}

export function normalizeRecord(source, record, home) {
  const pose = source === 'pose';
  const title = pose ? record['ポーズ名'] : record['キーワード'];
  const sub = pose
    ? [record['分類'], record['アングル']].map(x => translated[x] || x).join(' · ')
    : translated[record['カテゴリ']] || record['カテゴリ'];
  for (const key of pose
    ? ['id', '系統', 'ポーズ番号', '分類', 'ポーズ名', 'アングル', 'サムネ', '原寸']
    : ['id', 'カテゴリ', 'キーワード', 'サムネ', '画像', '原寸']) {
    if (typeof record[key] !== 'string' || !record[key]) {
      throw new Error(`Invalid ${source} field ${key}: ${record.id}`);
    }
  }
  const resources = Object.fromEntries(['サムネ', '画像', '原寸']
    .filter(key => record[key])
    .map(key => {
      const url = new URL(record[key], home);
      if (url.origin !== new URL(home).origin) throw new Error(`Unexpected resource host: ${url}`);
      return [key, url.href];
    }));
  return {
    id: record.id, title, category: pose ? '포즈' : '의상', sub,
    tags: pose ? [record['系統'], sub] : [sub, title], gender: '여성',
    source, url: resources['原寸'], home,
    prompt: pose
      ? `Use the original pose reference to guide body posture and camera angle. Preserve the chosen adult character identity, clothing and scene. ${title}`
      : `Dress the chosen adult character in this outfit: ${title}. Preserve face identity, body proportions and the selected pose.`,
    thumbnail_url: resources['サムネ'],
    display_url: resources['画像'] || resources['原寸'],
    resources,
    original: record,
  };
}

export async function collect() {
  const snapshot = { sources: [] };
  const references = [];
  for (const source of sources) {
    const home = `https://ai-${source}-gallery.pages.dev/`;
    const response = await fetch(home, { signal: AbortSignal.timeout(30000) });
    if (!response.ok) throw new Error(`${home}: HTTP ${response.status}`);
    const html = await response.text();
    const meta = extractJSON(html, 'META');
    const records = extractJSON(html, 'D');
    if (!Array.isArray(records) || records.length === 0) throw new Error(`Empty source: ${source}`);
    const ids = new Set(records.map(record => record.id));
    if (ids.size !== records.length) throw new Error(`Duplicate source IDs: ${source}`);
    if (meta.total !== undefined && meta.total !== records.length) throw new Error(`Total mismatch: ${source}`);
    if (meta.counts) {
      for (const [category, expected] of Object.entries(meta.counts)) {
        if (records.filter(record => record['カテゴリ'] === category).length !== expected) {
          throw new Error(`Category count mismatch: ${source}/${category}`);
        }
      }
    }
    references.push(...records.map(record => normalizeRecord(source, record, home)));
    snapshot.sources.push({
      source, home, meta, records,
      records_sha256: createHash('sha256').update(JSON.stringify(records)).digest('hex'),
      license: '画像データそのもの（元サイズ・加工後を含む）の再配布・転載・再販は禁止です。',
    });
  }
  return { snapshot, references };
}

export async function verifyMedia(references) {
  const urls = [...new Set(references.flatMap(record => Object.values(record.resources)))];
  const pending = urls.entries();
  const results = new Array(urls.length);
  await Promise.all(Array.from({ length: 8 }, async () => {
    for (const [index, url] of pending) {
      try {
        const response = await fetch(url, { method: 'HEAD', signal: AbortSignal.timeout(30000) });
        const contentType = response.headers.get('content-type') || '';
        results[index] = {
          url, status: response.status, content_type: contentType,
          content_length: response.headers.get('content-length'),
          ok: response.ok && contentType.startsWith('image/'),
        };
      } catch (error) {
        results[index] = { url, ok: false, error: String(error) };
      }
    }
  }));
  return {
    checked: new Date().toISOString(), method: 'HEAD', image_bodies_downloaded: 0,
    total: urls.length, passed: results.filter(result => result.ok).length,
    failed: results.filter(result => !result.ok), results,
  };
}

async function main() {
  const update = process.argv.includes('--update');
  const { snapshot, references } = await collect();
  const current = JSON.parse(await readFile(new URL('data/references.json', root), 'utf8'));
  const keys = new Set(references.map(record => `${record.source}:${record.id}`));
  const removed = current.filter(record => !keys.has(`${record.source}:${record.id}`));
  if (removed.length) throw new Error(`Upstream removed ${removed.length} records; review before replacing the snapshot`);
  const files = [
    ['data/gallery-sources.json', snapshot],
    ['data/references.json', references],
  ];
  for (const [path, value] of files) {
    if (update) {
      await writeFile(new URL(path, root), JSON.stringify(value, null, 2) + '\n');
    } else {
      const saved = JSON.parse(await readFile(new URL(path, root), 'utf8'));
      if (JSON.stringify(saved) !== JSON.stringify(value)) throw new Error(`Out-of-date snapshot: ${path}`);
    }
  }
  const summary = snapshot.sources.map(({ source, records }) => ({
    source, records: records.length,
    resources: new Set(references.filter(record => record.source === source)
      .flatMap(record => Object.values(record.resources))).size,
  }));
  console.log(JSON.stringify({ mode: update ? 'updated' : 'checked', sources: summary }));
  if (process.argv.includes('--verify-media')) {
    const audit = await verifyMedia(references);
    if (update) await writeFile(new URL('data/gallery-media-audit.json', root), JSON.stringify(audit, null, 2) + '\n');
    console.log(JSON.stringify({ total: audit.total, passed: audit.passed, failed: audit.failed }));
    if (audit.failed.length) process.exitCode = 1;
  }
}

if (process.argv[1] === fileURLToPath(import.meta.url)) await main();
