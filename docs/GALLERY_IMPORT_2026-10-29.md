# Gallery import — 2026-10-29

## Completed scope

| Source | Original records | Catalog entries | Image files |
| --- | ---: | ---: | ---: |
| POSE-DB-01 | 1,439 | 288 pose groups | 2,878 thumbnails and PNG originals |
| COSTUME-DB-01 | 1,407 | 1,407 outfits | 4,221 thumbnails, WebP images and PNG originals |
| Total | 2,846 | 1,695 | 7,099 |

The existing index already contained all 2,846 IDs. This update preserves the complete source records, gallery metadata, thumbnail URLs, display-image URLs and original URLs, rather than inventing additional poses or outfits. Source fields and every resource URL are also preserved in database variant attributes and entry details, including the existing full JSON export. The full catalog remains 2,485 entries with its previous drafts and production guides.

Every published image representation was downloaded to `.gallery-cache/`, outside `public/` and excluded from Git. The archive contains 2,216,620,096 bytes. It is private reference storage, not a new image hosting service. Source pages prohibit redistribution, reposting and resale of the image data; the website retains direct links to the source originals.

## Reproducible artifacts

- `data/gallery-sources.json`: all source JSON fields, metadata and record-array SHA-256 hashes.
- `data/references.json`: all 2,846 normalized records and all 7,099 resource URLs.
- `data/gallery-media-audit.json`: HTTP and image MIME results for all resource URLs.
- `data/gallery-downloads.json`: every local path, byte count, format and SHA-256.
- `data/database-seed.json`: normalized relational data for dataset `frame-reference-db-20261029-v3.2-gallery-resources`.
- `scripts/data/sync-galleries.mjs`: collect or compare source snapshots.
- `scripts/data/archive-galleries.mjs`: resumable private archive and offline verification.

Use the commands in `README.md` to synchronize, archive, normalize and verify again.

## Verification evidence

- Source snapshot recheck: 1,439 pose records and 1,407 costume records, with no missing IDs or duplicate source IDs.
- Resource URL audit: 7,099 passed, zero unresolved failures. One initial transient HEAD connection failure was rechecked successfully and is identified in the audit.
- Offline archive verification: all 7,099 local files matched their recorded byte sizes and SHA-256 hashes and had PNG, JPEG or WebP signatures.
- Regression suite: six JavaScript collector/archive tests and 14 SQLite/schema/seed integrity tests passed.
- TypeScript check and production build passed, including a final rerun after adding the private-cache development-server deny rule.
- Live local API: completed all 11 bootstrap stages; verified all 2,846 original records and resource maps against the full database export. Source-filtered counts were 288 pose groups and 1,407 outfits.
- Actual browser: desktop pose catalog and pose detail rendered; mobile costume detail displayed all three representation paths. No page or dialog horizontal overflow was observed in those states.
- Private-cache access: ordinary URLs, Vite `/@fs/` URLs and `?raw` requests were denied with HTTP 403. A `.gitignore` entry alone did not prevent development-server access, so `vite.config.ts` now explicitly denies the cache directory.

## Local execution and boundaries

The supplied workspace lacked `.openai/hosting.json`. It now declares the existing `DB` binding and no R2 bucket. A local-only D1 schema and seed were applied to `.wrangler/state` to exercise the real application. No remote database, deployment or Git commit was created.

The Python language server was unavailable and the TypeScript language-server daemon timed out for the database and Vite configuration files. The executed Python regression suite and `tsc --noEmit`/production build are the verification evidence for those files.

This verifies collection, preservation, file integrity and application integration. It does not claim individual visual inspection of every source image, independent validation of source descriptions, or redistribution permission. Imported index reports retain their metadata-ingestion download count; the separate `gallery-downloads.json` is the record of the private binary archive.
