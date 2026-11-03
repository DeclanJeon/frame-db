/** Private, resumable local archive. Nothing here is served from public/. */
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';

const root = new URL('../../', import.meta.url);
const manifestURL = new URL('data/gallery-downloads.json', root);

export function imageFormat(bytes) {
  if (bytes.subarray(0, 8).equals(Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]))) return 'png';
  if (bytes[0] === 255 && bytes[1] === 216 && bytes[2] === 255) return 'jpeg';
  if (bytes.toString('ascii', 0, 4) === 'RIFF' && bytes.toString('ascii', 8, 12) === 'WEBP') return 'webp';
  throw new Error('Response body is not PNG, JPEG, or WebP');
}

export function resourceList(references) {
  const resources = new Map();
  for (const record of references) {
    for (const url of Object.values(record.resources)) {
      const parsed = new URL(url);
      if (parsed.origin !== new URL(record.home).origin) throw new Error(`Unexpected host: ${url}`);
      const relative = parsed.pathname.slice(1);
      if (!/^(thumbs|img|png)\/[A-Za-z0-9_-]+\.(png|jpg|webp)$/.test(relative)) {
        throw new Error(`Unexpected image path: ${relative}`);
      }
      resources.set(url, { url, source: record.source, local_path: `.gallery-cache/${record.source}/${relative}` });
    }
  }
  return [...resources.values()];
}

async function main() {
  const references = JSON.parse(await readFile(new URL('data/references.json', root), 'utf8'));
  const resources = resourceList(references);
  let saved = { resources: [] };
  try {
    saved = JSON.parse(await readFile(manifestURL, 'utf8'));
  } catch (error) {
    if (error.code !== 'ENOENT') throw error;
  }
  const previous = new Map(saved.resources.map(resource => [resource.url, resource]));
  const verified = [];
  const verifyOnly = process.argv.includes('--verify');
  for (let offset = 0; offset < resources.length; offset += 8) {
    const chunk = await Promise.all(resources.slice(offset, offset + 8).map(async resource => {
      const prior = previous.get(resource.url);
      if (prior) {
        const bytes = await readFile(new URL(resource.local_path, root));
        const sha256 = createHash('sha256').update(bytes).digest('hex');
        if (sha256 !== prior.sha256 || bytes.length !== prior.bytes) {
          throw new Error(`Local file integrity mismatch: ${resource.local_path}`);
        }
        imageFormat(bytes);
        return prior;
      }
      if (verifyOnly) throw new Error(`Not archived: ${resource.url}`);
      const response = await fetch(resource.url, { signal: AbortSignal.timeout(120000) });
      if (!response.ok) throw new Error(`${resource.url}: HTTP ${response.status}`);
      const bytes = Buffer.from(await response.arrayBuffer());
      const format = imageFormat(bytes);
      const mime = response.headers.get('content-type')?.split(';')[0];
      if (mime !== `image/${format}`) throw new Error(`Image MIME mismatch: ${resource.url}: ${mime}`);
      const expected = response.headers.get('content-length');
      if (expected !== null && Number(expected) !== bytes.length) throw new Error(`Truncated image: ${resource.url}`);
      const target = new URL(resource.local_path, root);
      await mkdir(new URL('.', target), { recursive: true });
      await writeFile(target, bytes);
      return { ...resource, bytes: bytes.length, sha256: createHash('sha256').update(bytes).digest('hex'), format };
    }));
    verified.push(...chunk);
    if (!verifyOnly) {
      const completed = new Map([...previous, ...verified.map(resource => [resource.url, resource])]);
      await writeFile(manifestURL, JSON.stringify({
        storage: 'private_local_not_served', resources: [...completed.values()],
      }, null, 2) + '\n');
    }
    if (verified.length % 400 === 0) console.log(`ARCHIVED ${verified.length}/${resources.length}`);
  }
  console.log(JSON.stringify({
    mode: verifyOnly ? 'verified' : 'archived', files: verified.length,
    bytes: verified.reduce((total, resource) => total + resource.bytes, 0),
    storage: '.gallery-cache/ (private; excluded from public assets)',
  }));
}

if (process.argv[1] === fileURLToPath(import.meta.url)) await main();
