// Parent-only production QA. Images are displayed before the caller records a decision.
export function createAssetReview({ tool, read, display, print, parallel }) {
  const reviewed = new Map();
  const root = '/home/declan/Documents/Projects/Products/01_Persnal_Work/FRAME_DB/';
  return {
    async inspect(ids) {
      const plan = JSON.parse(await read('data/asset-production/plan.json'));
      const jobs = new Map(plan.jobs.map(job => [job.id, job]));
      const listing = await tool.glob({ pattern: '*.json', path: 'data/asset-production/receipts', limit: 300 });
      const names = listing.text.split('\n').filter(name => name.endsWith('.json') && !name.includes('/'));
      const receipts = await parallel(names.map(name => async () =>
        JSON.parse(await read(`data/asset-production/receipts/${name}`))));
      const byJob = new Map();
      for (const receipt of receipts) {
        if (byJob.has(receipt.job_id)) throw Error(`Multiple current receipts: ${receipt.job_id}`);
        byJob.set(receipt.job_id, receipt);
      }
      const packets = await parallel(ids.map(id => async () => ({
        id,
        image: await tool.read({ path: `public/generated/frame-assets/${id}.png` }),
        receipt: byJob.get(id),
      })));
      for (const packet of packets) {
        if (packet.receipt?.status !== 'generated') throw Error(`No completed receipt: ${packet.id}`);
        const image = packet.image.images?.[0];
        if (!image || image.mimeType !== 'image/png') throw Error(`No actual PNG: ${packet.id}`);
        const bytes = Buffer.from(image.dataBase64, 'base64');
        const actual = {
          ...packet.receipt,
          sha256: new Bun.CryptoHasher('sha256').update(bytes).digest('hex'),
          width: bytes.readUInt32BE(16),
          height: bytes.readUInt32BE(20),
          path: `public/generated/frame-assets/${packet.id}.png`,
        };
        reviewed.set(packet.id, actual);
        const job = jobs.get(packet.id);
        print({
          id: packet.id, title: job.title, change: job.change, qa: job.qa,
          shaMatches: packet.receipt.sha256 === actual.sha256,
          dimensions: [actual.width, actual.height],
        });
        display(image);
      }
    },
    async approve(observations, { replaceRejected = false } = {}) {
      const before = await read('data/asset-production/results.json');
      const current = JSON.parse(before);
      const approved = Object.entries(observations).map(([id, notes]) => {
        const existing = current.results.find(row => row.job_id === id);
        if (existing && !(replaceRejected && existing.status === 'rejected')) {
          throw Error(`Result already recorded: ${id}`);
        }
        const row = reviewed.get(id);
        if (!row) throw Error(`Image not directly displayed in this review: ${id}`);
        if (!notes.length) throw Error(`Missing visual observations: ${id}`);
        return {
          ...row, status: 'accepted',
          native_reference_paths: row.reference_paths,
          reference_paths: (row.reference_paths || []).map(path =>
            path.startsWith(root) ? path.slice(root.length) : path),
          worker_qa: row.qa,
          qa: {
            reviewer: 'parent direct full-image read and byte-hash calculation',
            decision: 'accepted', observations: notes,
          },
        };
      });
      let patch;
      if (replaceRejected) {
        const ids = new Set(approved.map(row => row.job_id));
        current.results = current.results.filter(row => !ids.has(row.job_id)).concat(approved);
        const after = JSON.stringify(current, null, 2);
        patch = '*** Begin Patch\n*** Update File: data/asset-production/results.json\n@@\n' +
          before.trimEnd().split('\n').map(line => '-' + line).join('\n') + '\n' +
          after.split('\n').map(line => '+' + line).join('\n') + '\n*** End Patch\n';
      } else {
        const lines = approved.map(row => JSON.stringify(row, null, 2)
          .split('\n').map(line => '    ' + line).join('\n')).join(',\n');
        patch = '*** Begin Patch\n*** Update File: data/asset-production/results.json\n@@\n' +
          '-    }\n-  ]\n-}\n+    },\n' +
          lines.split('\n').map(line => '+' + line).join('\n') +
          '\n+  ]\n+}\n*** End Patch\n';
      }
      const result = await tool.apply_patch({ input: patch });
      const applied = result.details?.result;
      if (result.hasError || !applied || applied.failures?.length || applied.hasPartialSuccess ||
          !applied.appliedFiles?.includes('data/asset-production/results.json')) {
        throw Error(result.text);
      }
      print({ accepted: approved.map(row => row.job_id) });
    },
  };
}
