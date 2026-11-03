# Web-source DB population: independent verification

Final parent acceptance: **PASS for the completed local first pass; target coverage remains 482/580 (98 short)**. The original verifier reported FAIL before publication/creative reconciliation; those findings are preserved below as history and resolved by the independent parent checks. No remote deployment was performed.

## Proven result

The real seed and bootstrapped local production DB contain **2,749 entries**: the original **2,485**, plus **264 new entries**. **218 original entries** were enriched. There are **482 accepted concepts in all 29 categories**, against a maximum first-pass target of 580: **98 short**, with 11 categories at 20 and 18 below target. There were 513 submitted concepts, 31 rejected, and 67 target concepts never submitted. These are distinct concepts, not media files.

All 482 accepted record payloads map exactly once to the correct category/concept; explicit existing-entry targets and source-ID/primary-URL mappings match. All 29 paginated category APIs matched seed entry-ID and accepted-concept sets, including a repeat after the concurrent creative revision. The complete runtime export matched all 11 current seed tables. No graph status was used as verification.

The recorded accepted reviews contain 1,484 attributed source-claim facts and one separate web proposal. This verifier did not newly fetch every one of those facts. Four sampled records were fully rechecked against current primary bodies; the makeup sample was partial. There are 312 web source rows (315 sources including three original sources).

## Historical findings (resolved by parent)

These are retained findings from the earlier verifier snapshot, not outstanding failures. The final composed publication version now matches the actual API. Final creative verification and the evidence limits are recorded below.

1. **FAIL — final publication integration, producer `publish-all` plus concurrent creative-supplement integration; cross-category.** `data/web-research/publication.json` still names the web-only dataset version, while `lib/database.ts:5` and observed production APIs append the creative revision below. The publication producer must reconcile its manifest with the actual runtime revision and retain separate web/creative counts. This audit changes only its two reports.

   Publication: `frame-reference-db-20261029-v3.3-verified-drive-web-c9c7b7db80b88cf8411b1eca350a1a5d47fa472090a045e1b8862afc237f7866`

   Observed runtime: `frame-reference-db-20261029-v3.3-verified-drive-web-c9c7b7db80b88cf8411b1eca350a1a5d47fa472090a045e1b8862afc237f7866-creative-eb55dfc72cc16f4bade66dd9aaa7b3f0af43f10966be677a38d18909909f6793`

   A concurrent edit added 16 explicitly separate creative-direction records to existing hair/makeup/voice entries. Entry counts, web accepted counts, media arrays and original prompts did not increase. The final 11-table export matched the current seed including those directions; final required commands passed. These directions are not new web facts, acquired media, tested generation capability or paid output.

2. **PARTIAL — makeup producer `omo-makeup-collector-st_01a18961`, entry `FS-0031`, concept `natural-dewy-complexion`.** The correct M·A·C primary product page opens and its summary supports the two-in-one moisturizer/highlighter claim. The current retrieved body does not expose the cited Product Details / Finish Shimmer section or under-foundation wording. Two of three sample fact fields were not independently re-certified. Supply readable exact primary sections or update evidence and obtain a fresh independent review; do not present the old review as this audit's current fact verification. This does not prove the historical review was false.

3. **Observed preview limitation — production-preview integration, not a category collector.** The default task-owned preview on 8797 served APIs but returned HTTP 404 for CSS and chunks, leaving an unstyled, unhydrated shell. One alternate start exited 1 because generated `dist/server/wrangler.json` was temporarily unavailable; it subsequently existed with mtime 2026-10-30T06:07:24.586Z. Source/seed/build output changed concurrently. The exact cause of this transient failure was not proven. Explicit `--assets` on 8798 returned CSS HTTP 200 and rendered correctly. Reproduce from a stable matching build with the successful command below; no app fix is claimed.

## Actual commands and API checks

Working directory: `/home/declan/Documents/Projects/Products/01_Persnal_Work/FRAME_DB`.

| Command | Actual result |
| --- | --- |
| `pnpm test:data` | Exit 0 initially and on final revision. Final run: 13 Node tests plus Python suites 17, 5, 38 and 13; 86 passed, zero failures. |
| `pnpm exec tsc --noEmit` | Exit 0 initially and on final revision. |
| `pnpm build` | Exit 0 initially and on final revision. |
| `pnpm start --port 8797` | Owned local production preview, API PASS; observed static asset 404. |
| `pnpm start --port 8798 --assets '/home/declan/Documents/Projects/Products/01_Persnal_Work/FRAME_DB/dist/client'` | Owned local production preview; successful rendered evidence. |
| `git status --short` | Exit 128: workspace is not a git repository. No commit/status baseline claimed. |

Resident JavaScript eval used `fetch` against localhost, not a remote database. Actual request patterns:

- `GET /api/bootstrap?step=0` through `step=10`: all HTTP 200; final `{complete:true,step:11,total:11}`. Repeated step 0 returned complete.
- `GET /api/catalog?summary=1`: 2,749 total, 1,959 external, 214 text, 576 guides, `webReviewed=482`, `mediaDrive=2914`. External status does not mean media exists.
- `GET /api/catalog?category={id}&limit=60&page={page}`: exhausted every page for every category (pose six pages; costume 25; other categories one each). Compared IDs and concept keys with seed/accepted files.
- `GET /api/entries/{id}`: the five sample IDs below each returned HTTP 200, zero assets and the correct web source URL.
- `GET /api/export/all`: HTTP 200. Exact canonicalized row-set/count comparison: categories 29; sources 315; entries 2,749; variants 2,914; media 2,914; tags 3,171; entry tags 36,502; prompts 2,485; relations 832; skill mappings 29; import batches 31.

The first export comparison timed out at 300 seconds because this verifier used a quadratic comparison. A linear-time set comparison replaced it and completed successfully; this was audit-tool overhead, not an app failure. No test expectations were edited. JSON language-server diagnostics were unavailable because Biome is not installed; report JSON was produced by JSON.stringify and parsed in memory. No dependency was installed.

## Category results

All category API ID sets and accepted-key sets PASS. New/enriched counts are relative to the original 2,485 entries, including the pilot; not increments beyond the pilot.

| Category | API entries | Accepted | New | Enriched | Rejected | Shortfall |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| pose | 338 | 17 | 14 | 3 | 3 | 3 |
| costume | 1451 | 14 | 4 | 10 | 0 | 6 |
| hair | 47 | 18 | 2 | 16 | 2 | 2 |
| makeup | 42 | 20 | 2 | 18 | 0 | 0 |
| expression | 50 | 16 | 9 | 7 | 1 | 4 |
| gesture | 37 | 13 | 11 | 2 | 1 | 7 |
| anatomy | 31 | 17 | 7 | 10 | 0 | 3 |
| fashion-items | 34 | 20 | 0 | 20 | 0 | 0 |
| props | 34 | 14 | 12 | 2 | 0 | 6 |
| persona | 37 | 16 | 15 | 1 | 4 | 4 |
| acting | 33 | 13 | 11 | 2 | 2 | 7 |
| interaction | 37 | 20 | 15 | 5 | 0 | 0 |
| space | 37 | 14 | 7 | 7 | 0 | 6 |
| lighting | 46 | 16 | 10 | 6 | 4 | 4 |
| camera | 37 | 11 | 5 | 6 | 9 | 9 |
| camera-motion | 32 | 16 | 8 | 8 | 0 | 4 |
| look | 37 | 19 | 11 | 8 | 1 | 1 |
| motion | 41 | 20 | 17 | 3 | 0 | 0 |
| voice | 39 | 8 | 7 | 1 | 4 | 12 |
| speech | 38 | 20 | 14 | 6 | 0 | 0 |
| sound | 43 | 20 | 15 | 5 | 0 | 0 |
| story | 42 | 20 | 16 | 4 | 0 | 0 |
| edit | 32 | 20 | 6 | 14 | 0 | 0 |
| delivery | 41 | 20 | 15 | 5 | 0 | 0 |
| brief | 23 | 20 | 7 | 13 | 0 | 0 |
| ops | 23 | 16 | 5 | 11 | 0 | 4 |
| evidence | 23 | 20 | 9 | 11 | 0 | 0 |
| handoff | 17 | 6 | 1 | 5 | 0 | 14 |
| qa | 27 | 18 | 9 | 9 | 0 | 2 |
| **Total** | **2749** | **482** | **264** | **218** | **31** | **98** |

### Responsible producers for partial categories

- `pose`: 17/20, shortfall 3; producer `pose-collector-st_01a18ad4`. 3 submitted records rejected; 0 target concepts not submitted. Exact rejected keys, reasons and reviewer are in the JSON report and `data/web-research/reviews/pose.json`.
- `costume`: 14/20, shortfall 6; producer `omo-costume-collector-20261030`. 6 target concepts not submitted. Exact rejected keys, reasons and reviewer are in the JSON report and `data/web-research/reviews/costume.json`.
- `hair`: 18/20, shortfall 2; producer `hair-primary-collector-frame-db-444eb549`. 2 submitted records rejected; 0 target concepts not submitted. Exact rejected keys, reasons and reviewer are in the JSON report and `data/web-research/reviews/hair.json`.
- `expression`: 16/20, shortfall 4; producer `omo-expression-collector-20261030`. 1 submitted records rejected; 3 target concepts not submitted. Exact rejected keys, reasons and reviewer are in the JSON report and `data/web-research/reviews/expression.json`.
- `gesture`: 13/20, shortfall 7; producer `gesture-collector-st_01a18ae0`. 1 submitted records rejected; 6 target concepts not submitted. Exact rejected keys, reasons and reviewer are in the JSON report and `data/web-research/reviews/gesture.json`.
- `anatomy`: 17/20, shortfall 3; producer `anatomy-collector-st_01a18ae3`. 3 target concepts not submitted. Exact rejected keys, reasons and reviewer are in the JSON report and `data/web-research/reviews/anatomy.json`.
- `props`: 14/20, shortfall 6; producer `omo-props-collector-20261030-recheck`. 6 target concepts not submitted. Exact rejected keys, reasons and reviewer are in the JSON report and `data/web-research/reviews/props.json`.
- `persona`: 16/20, shortfall 4; producer `omo-persona-collector-st_01a18af9`. 4 submitted records rejected; 0 target concepts not submitted. Exact rejected keys, reasons and reviewer are in the JSON report and `data/web-research/reviews/persona.json`.
- `acting`: 13/20, shortfall 7; producer `acting-collector-st_01a18af8`. 2 submitted records rejected; 5 target concepts not submitted. Exact rejected keys, reasons and reviewer are in the JSON report and `data/web-research/reviews/acting.json`.
- `space`: 14/20, shortfall 6; producer `space-primary-collector-st_01a18b04`. 6 target concepts not submitted. Exact rejected keys, reasons and reviewer are in the JSON report and `data/web-research/reviews/space.json`.
- `lighting`: 16/20, shortfall 4; producer `lighting-primary-collector-frame-db-444eb549-recollection`. 4 submitted records rejected; 0 target concepts not submitted. Exact rejected keys, reasons and reviewer are in the JSON report and `data/web-research/reviews/lighting.json`.
- `camera`: 11/20, shortfall 9; producer `omo-camera-primary-collector-20261030`. 9 submitted records rejected; 0 target concepts not submitted. Exact rejected keys, reasons and reviewer are in the JSON report and `data/web-research/reviews/camera.json`.
- `camera-motion`: 16/20, shortfall 4; producer `camera-motion-collector-st_01a18b0e`. 4 target concepts not submitted. Exact rejected keys, reasons and reviewer are in the JSON report and `data/web-research/reviews/camera-motion.json`.
- `look`: 19/20, shortfall 1; producer `omo-look-collector-st_01a18b12`. 1 submitted records rejected; 0 target concepts not submitted. Exact rejected keys, reasons and reviewer are in the JSON report and `data/web-research/reviews/look.json`.
- `voice`: 8/20, shortfall 12; producer `voice-primary-collector-st_01a18b17`. 4 submitted records rejected; 8 target concepts not submitted. Exact rejected keys, reasons and reviewer are in the JSON report and `data/web-research/reviews/voice.json`.
- `ops`: 16/20, shortfall 4; producer `ops-primary-collector-20261030`. 4 target concepts not submitted. Exact rejected keys, reasons and reviewer are in the JSON report and `data/web-research/reviews/ops.json`.
- `handoff`: 6/20, shortfall 14; producer `handoff-primary-collector-st_01a18b4e`. 14 target concepts not submitted. Exact rejected keys, reasons and reviewer are in the JSON report and `data/web-research/reviews/handoff.json`.
- `qa`: 18/20, shortfall 2; producer `omo-qa-collector-20261030`. 2 target concepts not submitted. Exact rejected keys, reasons and reviewer are in the JSON report and `data/web-research/reviews/qa.json`.

Notable documented rejection causes: camera has nine Nikon-dependent rejections under explicit AI-agent restrictions; voice has four ASHA-dependent records not independently readable; hair has two Redken-dependent records not readable; lighting has four unsupported title/geometry claims. Those rejected concepts were not published. Full review shortfall reasons, exact rejected keys and producer/reviewer identities are preserved in the JSON report, attributed to the reviews rather than claimed as new live inspections. No concepts were invented to fill targets.

## Primary links and rendered evidence

- `hair` / `FS-0002`: https://www.lorealparisusa.com/beauty-magazine/hair-style/hairstyle-trends/haircuts-for-wavy-hair
  - Live check: **PASS**. Section 11 Long layers supports retained length, movement/natural texture, and the attributed 6-8-week trim advice.
- `makeup` / `FS-0031`: https://www.maccosmetics.com/products/strobe-cream
  - Live check: **PARTIAL**. Correct primary product title, two-in-one summary and Pinklite description opened. Current extracted body does not expose the cited Product Details / Finish Shimmer or under-foundation wording. These two facts were not independently re-certified by this audit.
- `space` / `FS-0121`: https://www.weather.gov/lmk/twilight-types
  - Live check: **PASS**. Three Types of Twilight and Civil Twilight support all three sample facts, including the fog limitation.
- `sound` / `CRAFT-sound-eed5b2f3dcec`: https://www.adobe.com/creativecloud/video/post-production/cuts-in-film
  - Live check: **PASS**. J cuts and L cuts using sound transition supports audio lead, track-shape naming and the running/train-whistle example.
- `ops` / `CRAFT-ops-7ed255f8b9e9`: https://www.w3.org/TR/prov-primer/
  - Live check: **PASS**. Markdown extraction was empty. Direct public HTML GET returned HTTP 200, title PROV Model Primer, and section 2.9 backup/location-independent-file paragraph supporting all three facts.

All five detail APIs resolve to these exact primary links. Source pages were read as public text only; linked images/videos/audio were not downloaded or opened as media. W3C's empty Markdown extraction was resolved with a direct public HTML GET and reading section 2.9.

Temporary screenshots: `/tmp/frame-verification-evidence-RipJuy/`. Files follow `{desktop|mobile}-{hair|makeup|space|sound|ops}-{catalog|detail}.png`: **20 captures**, all visually inspected. Additional `desktop-broken.png` and `mobile-broken.png` retain the initial default-preview failure. These temporary files are evidence, not acquired DB media, and are not durable project assets.

Desktop was 1440×1000, DPR 1. True mobile was 390×844, DPR 3 with touch enabled (5 points) and mobile device metrics/user agent, not just a narrow desktop viewport. Final detail captures waited for each exact primary-source anchor using a bounded MutationObserver. All ten details display source attribution, source_claim locators, conservative unknown rights, and explicit “no media” state. No image elements appeared on these sampled metadata-only pages; document width did not overflow. Dialog content scrolls behind a fixed action row. Catalogs show real category counts and text-only cards rather than fabricated source thumbnails. This is representative visual coverage, not a claim that all 2,749 detail pages were inspected.

## Preservation and media boundaries

Passing real integrity tests reconstruct the original baseline and confirm original IDs, status, authored fields, original detail values, prompts, gallery fields and relational data. The separate web/creative additions do not replace original authored instructions. Original gallery coverage remains **1,695 grouped entries / 2,846 source image records**, comprising 288 pose groups and 1,407 costume entries.

There are still **2,914 media rows**: pose 1,439; costume 1,407; original technical diagrams 68. All media row URLs use `/api/media/{24-hex-id}`, and thumbnail/display URLs resolve through the Drive index. Manifest/index retain **7,167 distinct Drive file mappings**; the stored byte-verification audit has total 7,167, passed 7,167, failures 0, with stored byte/SHA-256 checks preserved. This audit did **not** remotely download or rehash those 7,167 files again.

**New web media rows, downloads, uploads, acquired files and visual/audio sample reviews: 0.** Knowledge links and media candidates are not acquired media. The 68 technical diagrams are not filmed lighting/camera/motion results. Public access and source attribution do not grant reproduction, commercial, personality or AI-upload rights. Accepted sources keep conservative rights records. No automated request was made to mocap.cs.cmu.edu, MMAC or the rejected Nikon sources; prohibited/rejected sources were absent from published web source rows.

No paid generation, model execution, login, credential/cookie read, remote deployment/DB write, external message or commit occurred. Only the two requested reports were authored. The task-owned preview monitors `mon_11S7DRDH8HKQAM75` and `mon_Q0WT1FBZTZAWWWGC` were stopped after restart; earlier attempts timed out or exited. Owned browser sessions were closed or ended with kernel/host restart. No user-owned preview/browser was stopped.

Machine-readable counts, exact producer/reviewer names, per-category shortfall reasons, rejected keys, evidence paths and input SHA-256 snapshot: `data/web-research/runtime-verification.json`. The final state is **verified partial metadata population**, **not complete category coverage, fresh media acquisition or remote publication**.



## Final parent acceptance and creative supplementation

The parent directly reran two normalizations with identical output SHA, `pnpm test:data` (86 tests), `pnpm exec tsc --noEmit` and `pnpm build`; every command exited 0. The final seed SHA is `68877da58436ab95a88fc5d78cd1cbff191ee018396dd4701ecf266af0587860`. The final API dataset version equals `publication.json`, which now preserves the original web-only revision separately from the composed web-plus-creative revision.

Actual result: 29 categories, 482 approved/applied web concepts (264 new IDs and 218 existing-ID enrichments), 1,484 attributed facts, 98 target shortfall. Existing entries total 2,749. All 2,485 original IDs and original values, 7,167 verified Drive mappings, 2,914 media rows and 2,485 prompt templates remain preserved. All exported table values match the final seed, and the parent checked all 29 category counts.

Hair/makeup gaps were filled as **16 independently reviewed creative descriptions on existing IDs**, with zero new creative IDs or media. The parent checked every creative detail API against approved directions. Two initial proposals were rejected, corrected and independently re-reviewed against the new exact SHA; all 16 were then accepted. Web facts and creative proposals remain separately labeled and counted.

The parent inspected actual production desktop/390px mobile captures for hair, makeup, space, sound and operations. Additional hair FS-0007 and makeup FS-0033 renders showed the authored directions, proposal label and original attribution at 1440x1000 and 390x844 without horizontal overflow, and searches each returned exactly one existing card. These extra renders used the unchanged original Catalog component and CSS with every data request delegated to the real final local production API, not fixture data. Browser HTTP navigation stalled in this workstation; the temporary data-origin QA document excluded only its artificial history SecurityError and external font import. This does not claim that renewed browser HTTP navigation succeeded. The original production captures and independently checked API remain separate evidence. The fixed light theme is unchanged under dark preference.

The parent also fetched the complete current M.A.C product HTML and confirmed product role, checked Pinklite, explicit Finish Shimmer and usage positions. The precise pearl-pink shade wording remains the dated independent collection evidence; it is not claimed as a new visual observation. There is no claim to re-fetch every attributed source fact at final runtime.

See `data/web-research/parent-final-verification.json` for exact checks, protected hashes, capture hashes and adapter limits, and `runtime-verification.json` for the reconciled final verdict. All 98 missing target concepts remain reported rather than invented. No media acquisition, paid generation, remote DB write, deployment or commit occurred.

