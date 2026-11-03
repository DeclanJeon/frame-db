import { test } from 'node:test';
import assert from 'node:assert/strict';
import { serveDriveImage } from '../lib/drive-media.ts';

const key = 'a'.repeat(24);
const file = { file_id: 'B'.repeat(33), content_type: 'image/png', bytes: 3, sha256: 'c'.repeat(64) };
const index = { [key]: file };
const request = new Request(`https://frame.example/api/media/${key}`);

test('serves a manifest image from Drive without forwarding cookies', async () => {
  let upstreamURL;
  let upstreamOptions;
  const response = await serveDriveImage(request, key, index, async (url, options) => {
    upstreamURL = new URL(url);
    upstreamOptions = options;
    return new Response(new Uint8Array([1, 2, 3]), { headers: { 'Content-Type': 'image/png' } });
  });
  assert.equal(upstreamURL.origin, 'https://drive.usercontent.google.com');
  assert.equal(upstreamURL.searchParams.get('id'), file.file_id);
  assert.equal(upstreamOptions.headers, undefined);
  assert.equal(response.status, 200);
  assert.equal(response.headers.get('content-type'), 'image/png');
  assert.deepEqual(new Uint8Array(await response.arrayBuffer()), new Uint8Array([1, 2, 3]));
});

test('does not fetch unknown or malformed asset IDs', async () => {
  const neverFetch = () => { throw new Error('Unexpected fetch'); };
  assert.equal((await serveDriveImage(request, 'https://example.com/a.png', index, neverFetch)).status, 404);
  assert.equal((await serveDriveImage(request, 'd'.repeat(24), index, neverFetch)).status, 404);
});

test('does not serve a Drive sign-in HTML response as an image', async () => {
  const response = await serveDriveImage(request, key, index,
    async () => new Response('<html>sign in</html>', { headers: { 'Content-Type': 'text/html' } }));
  assert.equal(response.status, 502);
  assert.equal(response.headers.get('content-type'), 'application/json');
});

test('reports Drive rate limiting without an original-host fallback', async () => {
  let calls = 0;
  const response = await serveDriveImage(request, key, index, async () => {
    calls++;
    return new Response('limited', { status: 429 });
  });
  assert.equal(response.status, 502);
  assert.equal(calls, 1);
});

test('returns a conditional cache response without fetching Drive', async () => {
  const conditional = new Request(request, { headers: { 'If-None-Match': `"${file.sha256}"` } });
  const response = await serveDriveImage(conditional, key, index, () => { throw new Error('Unexpected fetch'); });
  assert.equal(response.status, 304);
  assert.equal(await response.text(), '');
});

test('returns an explicit gateway error on a connection failure', async () => {
  const response = await serveDriveImage(request, key, index, async () => { throw new TypeError('network'); });
  assert.equal(response.status, 502);
});

test('forwards HEAD and returns image headers without a response body', async () => {
  let method;
  const head = new Request(request, { method: 'HEAD' });
  const response = await serveDriveImage(head, key, index, async (_, options) => {
    method = options.method;
    return new Response(null, { headers: { 'Content-Type': 'image/png' } });
  });
  assert.equal(method, 'HEAD');
  assert.equal(response.status, 200);
  assert.equal(response.headers.get('content-type'), 'image/png');
  assert.equal((await response.arrayBuffer()).byteLength, 0);
});
