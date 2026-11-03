/** Read only publicly shared Drive folders; no browser cookies or OAuth tokens. */
const decodeHTML = text => text.replace(/&(?:amp|quot|apos|lt|gt|#39|#(\d+)|#x([a-f0-9]+));/gi,
  (match, decimal, hex) => decimal ? String.fromCodePoint(Number(decimal))
    : hex ? String.fromCodePoint(parseInt(hex, 16))
      : ({ '&amp;': '&', '&quot;': '"', '&apos;': "'", '&#39;': "'", '&lt;': '<', '&gt;': '>' }[match] || match));

export async function listPublicFolder(folderID) {
  if (!/^[\w-]{20,}$/.test(folderID)) throw new Error(`Invalid Drive folder ID: ${folderID}`);
  const response = await fetch(`https://drive.google.com/embeddedfolderview?id=${folderID}`, {
    signal: AbortSignal.timeout(30000),
  });
  if (!response.ok) throw new Error(`Public folder ${folderID}: HTTP ${response.status}`);
  const html = await response.text();
  if (!html.includes('flip-')) throw new Error(`Unexpected public folder response: ${folderID}`);
  const children = [];
  for (const match of html.matchAll(/<a\b[^>]*href="([^"]+)"[^>]*>([\s\S]*?)<\/a>/g)) {
    const href = decodeHTML(match[1]);
    const file = href.match(/^https:\/\/drive\.google\.com\/file\/d\/([\w-]{20,})\/view/);
    const folder = href.match(/^https:\/\/drive\.google\.com\/(?:drive\/(?:u\/\d+\/)?folders\/|folderview\?id=)([\w-]{20,})/);
    if (!file && !folder) continue;
    const name = decodeHTML(match[2].replace(/<[^>]*>/g, '').trim());
    children.push({ id: (file || folder)[1], name, kind: folder ? 'folder' : 'file' });
  }
  return { id: folderID, title: decodeHTML(html.match(/<title>(.*?)<\/title>/s)?.[1] || ''), children };
}
