export type DriveMediaFile = {
  readonly file_id: string;
  readonly content_type: string;
  readonly bytes: number;
  readonly sha256: string;
};
export type DriveMediaIndex = Readonly<Record<string, DriveMediaFile>>;

/** Serve only verified manifest files, never a caller-supplied remote URL. */
export async function serveDriveImage(
  request: Request,
  assetID: string,
  index: DriveMediaIndex,
  fetcher: typeof fetch = fetch,
): Promise<Response> {
  const file = /^[a-f0-9]{24}$/.test(assetID) ? index[assetID] : undefined;
  if (!file) return Response.json({ error: '이미지가 없습니다.' }, { status: 404 });
  const etag = `"${file.sha256}"`;
  const headers = new Headers({
    'Content-Type': file.content_type,
    'Cache-Control': 'public, max-age=86400, stale-while-revalidate=604800',
    'ETag': etag,
    'X-Content-Type-Options': 'nosniff',
    'Content-Security-Policy': "default-src 'none'; style-src 'unsafe-inline'; sandbox",
  });
  if (request.headers.get('if-none-match') === etag) {
    return new Response(null, { status: 304, headers });
  }
  const url = new URL('https://drive.usercontent.google.com/download');
  url.searchParams.set('id', file.file_id);
  url.searchParams.set('export', 'download');
  url.searchParams.set('authuser', '0');
  let upstream: Response;
  try {
    upstream = await fetcher(url, {
      method: request.method === 'HEAD' ? 'HEAD' : 'GET',
      redirect: 'follow',
      signal: AbortSignal.timeout(30000),
    });
  } catch (error) {
    if (!(error instanceof TypeError) && !(error instanceof DOMException)) throw error;
    return Response.json({ error: 'Drive 이미지에 연결하지 못했습니다.' }, { status: 502 });
  }
  const contentType = upstream.headers.get('content-type')?.split(';')[0] || '';
  if (!upstream.ok || (!contentType.startsWith('image/') && contentType !== 'application/octet-stream')) {
    await upstream.body?.cancel();
    return Response.json({ error: 'Drive 이미지 접근 권한 또는 응답을 확인해 주세요.' }, { status: 502 });
  }
  return new Response(request.method === 'HEAD' ? null : upstream.body, { headers });
}
