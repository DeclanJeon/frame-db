import mediaIndex from '../../../../data/drive-media-index.json';
import { serveDriveImage } from '../../../../lib/drive-media';

export async function GET(request: Request, { params }: { params: Promise<{ id: string }> }) {
  return serveDriveImage(request, (await params).id, mediaIndex);
}

export const HEAD = GET;
