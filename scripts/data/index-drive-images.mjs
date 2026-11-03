/** Match every Drive file to the upload plan and verify its actual public bytes. */
import { createHash } from 'node:crypto';
import { readFile, writeFile } from 'node:fs/promises';
import { dirname, basename, extname } from 'node:path';
import { listPublicFolder } from './drive-public.mjs';

const root = new URL('../../', import.meta.url);
const plan = JSON.parse(await readFile(new URL('data/drive-upload-plan.json', root), 'utf8'));
const state = JSON.parse(await readFile(new URL('data/drive-upload-state.json', root), 'utf8'));
const auditURL = new URL('data/drive-transfer-audit.json', root);
const types = { '.png': 'image/png', '.jpg': 'image/jpeg', '.webp': 'image/webp', '.svg': 'image/svg+xml' };
const folderPaths = [...new Set(plan.files.map(file => dirname(file.relative_path)))];
const files = [];
for (const path of folderPaths) {
  const listing = await listPublicFolder(state.folders[path]);
  const expected = plan.files.filter(file => dirname(file.relative_path) === path);
  for (const file of expected) {
    const matches = listing.children.filter(child => child.kind === 'file' && child.name === basename(file.relative_path));
    if (matches.length !== 1) throw new Error(`Missing or duplicate Drive image: ${file.relative_path} (${matches.length})`);
    files.push({ ...file, file_id: matches[0].id, folder_id: state.folders[path], content_type: types[extname(file.relative_path)] });
  }
  console.log(`INDEXED ${path} ${expected.length}`);
}
if (files.length !== 7167 || new Set(files.map(file => file.file_id)).size !== files.length) {
  throw new Error(`Incomplete or aliased Drive files: ${files.length}`);
}
let previous = { files: [] };
try {
  previous = JSON.parse(await readFile(auditURL, 'utf8'));
} catch (error) {
  if (error.code !== 'ENOENT') throw error;
}
const verified = new Map(previous.files.filter(file => file.ok).map(file => [file.file_id, file]));
const results = [];
let checkpoint = Promise.resolve();
const pending = files.values();
const concurrency = Number(process.env.DRIVE_VERIFY_CONCURRENCY || 4);
await Promise.all(Array.from({ length: concurrency }, async () => {
  for (const file of pending) {
    const old = verified.get(file.file_id);
    if (old?.sha256 === file.sha256 && old.bytes === file.bytes) {
      results.push(old);
      continue;
    }
    const url = new URL('https://drive.usercontent.google.com/download');
    url.searchParams.set('id', file.file_id);
    url.searchParams.set('export', 'download');
    url.searchParams.set('authuser', '0');
    let result;
    try {
      const response = await fetch(url, { redirect: 'follow', signal: AbortSignal.timeout(60000) });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const bytes = Buffer.from(await response.arrayBuffer());
      const sha256 = createHash('sha256').update(bytes).digest('hex');
      result = {
        file_id: file.file_id, relative_path: file.relative_path, status: response.status,
        content_type: response.headers.get('content-type'), bytes: bytes.length, sha256,
        ok: sha256 === file.sha256 && bytes.length === file.bytes,
      };
    } catch (error) {
      result = { file_id: file.file_id, relative_path: file.relative_path, ok: false, error: String(error) };
    }
    results.push(result);
    if (results.length % 100 === 0) {
      checkpoint = checkpoint.then(() => writeFile(auditURL, JSON.stringify({ files: results }, null, 2) + '\n'));
      await checkpoint;
      console.log(`VERIFIED ${results.length}/${files.length}`);
    }
  }
}));
await checkpoint;
const failed = results.filter(result => !result.ok);
await writeFile(auditURL, JSON.stringify({
  checked: new Date().toISOString(), total: files.length, passed: results.length - failed.length,
  failed, files: results,
}, null, 2) + '\n');
if (failed.length) throw new Error(`Drive content verification failed: ${failed.length}; see data/drive-transfer-audit.json`);
await writeFile(new URL('data/drive-assets.json', root), JSON.stringify({
  root_folder_id: state.root_folder_id, files,
}, null, 2) + '\n');
const mediaIndex = Object.fromEntries(files.map(file => [file.asset_id, {
  file_id: file.file_id, content_type: file.content_type, bytes: file.bytes, sha256: file.sha256,
}]));
await writeFile(new URL('data/drive-media-index.json', root), JSON.stringify(mediaIndex) + '\n');
console.log(JSON.stringify({ verified_files: files.length, bytes: files.reduce((sum, file) => sum + file.bytes, 0) }));
