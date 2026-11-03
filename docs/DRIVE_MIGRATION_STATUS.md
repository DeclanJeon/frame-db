# Drive migration status

Completed image migration and local production verification: 2026-10-29.
Dataset: `frame-reference-db-20261029-v3.3-verified-drive`.

## Result

- Parent: `15we6iUFHRL3KMU9Al8uSbHqk0Y4iSsGC` (Studio_DB).
- Library: `1e0QV0bF5qH4Ol8uTdBvxnPtGeSKxPRKz` (FRAME_DB).
- 55 classified folders, including 35 image leaves and `00_manifests`.
- All **7,167 images / 2,216,742,850 bytes** uploaded and anonymously downloaded again with exact SHA-256 and byte-size matches. No missing, duplicate or aliased image file IDs.
- Pose: 2,878 representations for 1,439 images / 288 grouped poses.
- Costume: 4,221 representations for 1,407 outfits.
- Authored diagrams: 68 SVG originals. Their provenance remains `owned_diagram`, not photographic reference.
- Four additional mapping/audit JSON files are stored in `00_manifests`; their actual public bytes were separately verified.
- The seed has 2,485 entries, 2,914 variants and 2,914 media rows. Every media URL uses `/api/media/{asset_id}`; thumbnails and display images use their corresponding verified Drive files.

## Mapping and evidence

| File | Purpose |
| --- | --- |
| `data/drive-upload-plan.json` | Original URL, local/staging path, category, SHA-256, MD5 and stable asset ID |
| `data/drive-upload-state.json` | Exact classified folder IDs |
| `data/drive-assets.json` | All 7,167 actual Drive file IDs and source mappings |
| `data/drive-media-index.json` | Image API allowlist with MIME, size and SHA-256 |
| `data/drive-transfer-audit.json` | Full public response audit: 7,167 passed, zero failed |
| `data/drive-metadata-audit.json` | Four Drive metadata-file IDs and verified hashes |

The original gallery records, URLs and source terms are retained as provenance. File integrity verification does not mean all image contents were visually reviewed. The concept assessment inspected twelve representative thumbnails and the migration QA inspected the actual website surfaces.

## Website delivery

`app/api/media/[id]/route.ts` serves only manifest-listed assets through `lib/drive-media.ts`. It fetches Drive download bodies, rejects HTML/sign-in/error responses, and has no original-host fallback. It sends explicit gateway failures, image MIME, caching, SHA-based ETags, nosniff and an SVG-safe CSP.

Cards show actual thumbnail images. Details show display-size images, angle thumbnails and Drive-backed original links. Missing media and authored diagrams remain distinct from reference imagery. Image failures have visible status text.

Real local production checks passed:

- HTTP 200 on `/api/status`, with 2,914 Drive media rows, 2,846 imported image references and 68 authored diagrams.
- A real image proxy response exactly matched the stored original hash.
- HEAD 200, conditional GET 304 and unknown asset 404. One initial development HEAD request hit a transient gateway failure; the same route and the production route subsequently returned 200 without changing the handler.
- Desktop pose/costume cards, pose detail and all five angle thumbnails; mobile costume detail and pose angle grid at 390 CSS pixels / DPR 3; authored SVG through Drive. Images decoded and no horizontal modal overflow was observed.
- Visible image-failure state was exercised rather than silently using another host.
- 33 unique regression tests passed (6 gallery, 7 Drive response, 15 SQLite/seed, 5 Drive seed-conversion), TypeScript passed, and `pnpm build` exited 0.

LSP diagnostics were unavailable: the daemon timed out, and Biome/basedpyright were not installed. The real compiler, executable tests, production build and browser checks above were used; no diagnostics were suppressed. Remote deployment and remote D1 changes were not performed.

## Re-run

The uploader uses agbrowse's existing local Chrome; it neither copies credentials nor changes the parent sharing settings. It waits for active FRAME_DB upload queues before resuming and only submits exact missing destination/name pairs.

```sh
agbrowse start --headed
AGBROWSE_PACKAGE_JSON=/home/declan/.local/opt/flucto-cli/lib/node_modules/agbrowse/package.json bun scripts/data/agbrowse-drive-upload.mjs
bun scripts/data/index-drive-images.mjs
python3 scripts/data/normalize.py --drive
pnpm test:data
pnpm exec tsc --noEmit
pnpm build
```

Use `DRIVE_UPLOAD_METADATA=1` with the uploader to select the four mapping/audit JSON files. Existing filenames are skipped, not overwritten. Public metadata backups are verified separately from the image manifest.

## Recovery history

The old BrowserSkill file-URL restriction was avoided by using the user-requested agbrowse Chrome. The first SVG initially landed in My Drive; the user explicitly approved its move to the exact shared diagram folder. Anonymous download then matched all 1,892 original bytes and its SHA-256.

Remote Playwright payload delivery hit a 50MB aggregate limit. The co-located Chrome now receives native local file paths via CDP. A one-hour monitor deadline interrupted the observer while Chrome continued uploading; resumption waited for the existing queue before submitting missing files. One later Node public-read timeout was checked through Bun before resuming. No blind duplicate batch was submitted.

## User-requested next phase

The existing media concept/empty-DB design is `docs/REFERENCE_DB_EXPANSION_PLAN.md`. After this migration and verification, the user additionally requested a web-sourced DB-population design and actual per-category execution reservations for all 29 categories.

The follow-up design and source research are now in `docs/WEB_DB_POPULATION_PLAN.md` and `docs/WEB_DB_SOURCE_RESEARCH.md`. Actual one-shot dependency run `dag_b08d0f3b-1ff6-41f3-9a7e-4ca08ea7013b` registered 62 nodes, including collection and independent review for all 29 categories. The real reservation ledger is `data/web-research/schedule.json`. This is execution registration, not a claim that future DB population or new media acquisition has already completed.
