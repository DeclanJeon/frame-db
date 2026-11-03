# FRAME DB asset expansion requirements

Date: 2026-10-30
Status: completed for the scoped 147-image release, including the user's image-first, brief-guide clarification. Evidence: `ASSET_EXPANSION_RESULT.md`.

## User request

2026-10-30 clarification: the user wants images with a simple usage guide, like the existing pose and costume references. The image should be directly reusable as a reference. Do not expose long generation prompts in the default screen.

Design first, write an executable work order, then perform the work. Research hairstyles, makeup, facial expressions, gaze and hand gestures on the web before deciding production quantities. Derive additional creative variations from existing styles. Generate usable images through the requested codex-imagen route. Every DB category must provide practical usage guidance; provide reusable prompts alongside assets.

## Acceptance contract

1. A research inventory distinguishes existing DB entries, source-supported base concepts and authored creative variations. It names actual source pages, dates, exact existing IDs and observable distinguishing features.
2. The work order gives explicit quantities per domain, separates concepts from rendered files and camera views, and lists the complete production queue. A worldwide exhaustive count is not asserted when the source taxonomy is open-ended.
3. Each creative variation names its parent concept and the changed visual axis. Changing an ID or title alone does not create a distinct concept.
4. Image generation prompts specify subject, framing, observable target, identity/lighting controls, background and exclusions. Usage prompts separately explain how to apply the resulting reference to a new subject without copying unrelated identity or composition.
5. Every generated asset has an existing or new concept ID, production prompt, tool/model provenance, local file, content hash, visible synthetic-image label, guide and a recorded QA decision. A prompt or pending job is never counted as a completed image.
6. The first production stage covers the five requested domains. Whole-DB guide/prompt coverage covers all 29 categories, including categories where an image is not the useful primary asset. Audio/video generation is not silently substituted with still images.
7. Preserve all existing 2,749 entry identities, including the original 2,485, existing details and prompt rows, 2,914 media rows and 7,167 verified Drive mappings. Add authored overlays and new rows without rewriting original provenance or claiming source photographs were acquired.
8. Generated images are original synthetic examples informed by textual concepts, not copies of web photographs. Source claims, creative directions and visual QA observations remain separate.
9. Generated local files must be selectable and visible in catalog/detail, downloadable or otherwise directly reusable, and exported with their guides/prompts and provenance.
10. Run relevant integrity/regression tests, type/build checks and actual API/UI checks. Report exact planned/generated/accepted/applied counts and any failures.

## Current observed baseline

Live local export and status checked on 2026-10-30:

- 29 categories, 2,749 entries, 2,914 media.
- 24 categories have zero media; 986 entries have no attached media.
- Hair: 47 entries, zero media.
- Makeup: 42 entries, zero media.
- Expression/gaze: 50 entries, zero media.
- Hand gesture: 37 entries, zero media.
- Pose, costume and three diagram categories have media. One representative file from each returned HTTP 200; this is not an exhaustive visual review.
- Existing normalization composes original data, reviewed web metadata and reviewed creative metadata. It must gain a separate reproducible production overlay rather than hand-editing the generated seed.
- Existing category guides cover all 29 domains, but this alone does not prove every entry has a practical guide or prompt.

## Execution boundaries

No remote deployment or git commit was requested. Local DB/bootstrap and generated local asset writes are within scope. Use no more than three simultaneous child agents. Research children have disjoint Markdown-only write paths; the parent owns the final production quantities and work order.

Image tool discovery found the local extension `generate_image`, accepting local output paths and reference images with explicit model parameters. A standalone `codex-imagen` shell command was not found. Record the actual tool identity when invoked rather than inventing a CLI. The advertised image-guide path `/$bunfs/root/SKILL-8gt84szq.md` is not present on this workstation; reading it failed with ENOENT. Do not claim that guide was loaded.

## Production decision gates

- Finish source and existing-ID inventory before fixing quantities.
- Write the complete work order before implementation or image generation.
- Inspect a representative image for each materially different framing before expanding that recipe.
- Only visually accepted real files enter the media overlay. Failed/missing images remain explicitly pending or rejected and do not get placeholder media.
