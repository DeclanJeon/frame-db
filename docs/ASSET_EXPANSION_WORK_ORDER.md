# FRAME DB asset expansion work order

Date: 2026-10-30
Owner: FRAME DB implementation session
Status: complete for this work order. All 147 photographs are accepted and locally integrated; `ASSET_EXPANSION_RESULT.md` and `data/asset-production/verification.json` record the evidence.

Read with `ASSET_EXPANSION_REQUIREMENTS.md`, `ASSET_DB_DESIGN.md` and the three `docs/research/ASSET_*_RESEARCH.md` inventories.

User-facing delivery is image-first: image, brief reference guidance, and optional collapsed source information. Generation recipes and detailed QA are retained for production traceability rather than displayed as usage instructions.

## 1. Current release quantities

| Domain | Base / existing-oriented | Authored creative derivatives | Reference slots | Unique images |
|---|---:|---:|---:|---:|
| Hair | 32 masters: 24 existing anchors + 8 researched coverage gaps | 12 | 44 | 44 |
| Makeup / grooming | 22: 12 complete face looks + 6 grooming + 4 nail | 12 face-look derivatives | 34 | 34 |
| Facial expression | 25: neutral + 12 observable actions at two relative intensities | 12 composed acting states | 37 | 37 |
| Gaze | 9 camera-relative directions with head facing forward | 0 additional directions | 9 | 8, sharing the neutral frontal image |
| Hand gesture | 16 reference actions | 8 controlled creative applications of existing actions | 24 | 24 |
| **Total** | | | **148** | **147** |

These are authored production quantities, not worldwide counts of possible styles or certified research classes. One image means one real, accepted full image file. Thumbnails, prompts, rows, rerenders and reference reuse do not increase the unique-image count.

Each current-release concept/condition gets a single diagnostic representative view. This decision prioritizes useful coverage of all five requested domains over generating many angles of the same look before empty domains are filled. A single view does not establish unseen rear geometry, precise physical angles or temporal motion.

Research recommendations of 251 hair photos, 177 makeup slots and 588 expression/gaze/hand photos are expansion proposals, **not the current release obligation or completed quantities**. Full angle sets, four-person comparisons, temporal clips, additional makeup derivatives and later modalities belong to explicitly separate future batches. Do not silently report them as done.

## 2. Exact production selection

### Hair: 44

Use the exact E01–E24 existing-ID table, N01–N08 gap table and D01–D12 derivative table in `ASSET_HAIR_RESEARCH.md`.

- E01–E17 and N01–N04: front three-quarter showing the defining perimeter, ear/nape and complete ends. Use a more diagnostic side view for structural asymmetry or disconnect.
- E18–E24 and N05–N08: rear three-quarter or attachment/scalp diagnostic view, with complete braid/tail/knot ends. Do not hide the defining attachment behind the head.
- D01–D09: use the same identity as their accepted master, showing the declared delta.
- D10: one fringe-deflection state, not a claimed wind sequence.
- D11: one released-hood compression state with the hood resting behind the neck, not a claimed transition.
- D12: one sparse/wispy-fringe variant of E08. The E08 master supplies the blunt comparison; do not generate an unlabeled two-condition collage or count one output twice.
- Attach matching base media to existing IDs. N gaps and genuinely new combinations get deterministic new IDs and explicit parent/basis links. Keep all original IDs.

### Makeup: 34

Use L01–L12, G01–G06 and N01–N04 from `ASSET_MAKEUP_RESEARCH.md`, then exactly the A derivative in each L01–L12 row of its facial-derivative table.

- Face/grooming: one frontal or shallow three-quarter full face, chosen to reveal the target placement, boundary or finish; enough resolution for skin/eye/lip detail.
- Nail: one oblique top view of a complete adult hand with every nail boundary readable.
- Same identity, lighting and framing within a parent/derivative pair. Preserve original facial proportions, skin tone and marks. Do not substitute product packaging.
- Freeze G02 stubble at the proposal's 1 mm visual target, not an asserted measurement. G03 short box approximately 5 mm and G05 full beard approximately 25 mm are authored appearance targets, not brand standards or verified physical lengths.
- Nail colors: N02 muted translucent taupe matched to the selected hand, N03 muted brick red, N04 translucent neutral with narrow white tips. These are production choices.
- No X tattoo/state recipes or extra body-part jobs in this release.

### Expression: 37

Use E00 plus E01–E12 at `subtle` and `moderate` relative intensity from `ASSET_EXPRESSION_GAZE_GESTURE_RESEARCH.md`, then C01–C12 **arrival state B only**.

Use one frontal controlled adult face. Keep the neutral reference as the actual input for edited states. Candidate AU labels help locate the observable action; do not assert certified FACS coding, exact muscle isolation or an internal-emotion ground truth. Relative intensity must be visually distinguishable within each pair.

C images are authored acting states, not observed psychological evidence. Their guide may describe a suggested transition, but the still does not verify timing, breath, blink, response order or sound.

### Gaze: 9 slots / 8 new files

Use the same E00 identity and frontal head. Horizontal subject-left / center / subject-right crossed with down / level / up. Target offsets are modest and visually readable; the research's 10-degree values are prompt targets, not calibrated measurements. Lens-centered slot reuses E00. Never mirror-copy an image or infer emotion/intent from direction.

### Hand: 24

Use H01–H16 actions as specified in the research, including exact existing IDs and contact relationships.

Use H17–H24 as **authored application derivatives** of their exact existing anchors, with explicit deltas:

- H17: two-handed handover of a thin closed notebook rather than an unspecified object; receiver hands remain identifiable.
- H18: pinch a soft jacket lapel tip, with fabric/skin separation.
- H19: relaxed interlaced hands on a neutral tabletop, subject-right thumb on top.
- H20: right thumb touching left index side in a resting two-hand composition; no repetitive movement claim.
- H21: plain pencil contacting the table instead of a generic pen; same release-state relationship.
- H22: right earbud held just outside the right ear; preserve ear/hand ownership.
- H23: plain unbranded watch on the left wrist, dial turned toward the owner's eyes.
- H24: blank card halfway out of the right jacket pocket, with the seam and right-hand grip visible.

Each is one contact/ownership diagnostic photograph, framed wide enough to trace all participating hands to their arms; hands and objects must remain detailed. Anatomy/contact failures are rejected, not published with a success label.

## 3. Identity, image and provenance specification

Establish synthetic adult identity A with E00 and identity B with the first short-hair master. Use actual accepted reference paths for further images that require the same identity. No web source photograph becomes an identity input. The identities are fictional and not claimed to represent a population.

Default output: 1024×1536 portrait for hair/face and 1536×1024 landscape for contact gestures/nails, PNG, one distinct asset per request. Use the discovered local image extension with explicit effective model and quality parameters. Record actual tool/provider identifiers; the absence of a shell binary named `codex-imagen` is not proof that the image extension is unavailable.

Every job carries: stable job ID, domain, category, entry ID, existing parent/basis IDs, source research references, authored observable direction, view, identity reference, image prompt, usage prompt, guide, requested parameters, actual output path/hash/dimensions, actual generation result, QA state and evidence.

Only real files that pass visual QA may be applied as generated media. Pending, failed and rejected jobs stay in the production ledger. Do not fabricate output files or treat a prompt sheet as image delivery.

## 4. Whole-DB guidance and prompts

Implement the 29-category matrix and additive guide contract in `ASSET_DB_DESIGN.md`.

Every existing and newly created entry must have a practical authored guide and a reusable reference-application prompt. Preserve the original prompt rows. New generation prompts belong only to concrete image jobs, distinguish them from application prompts, and bind the exact submitted text to output provenance.

Guides explain the entry-specific target, when/how to use it, what to preserve, what may change, typical failures and observable checks. Text-only/audio/video categories must disclose asset limits rather than pretending that a still satisfies their modality.

## 5. Execution units and ownership

1. Parent: finalize this work order and baseline evidence before code or generation.
2. Content implementation: author the exact 147-job queue, resolved directions/prompts/guides, parent mapping and category playbooks. Validate uniqueness and counts before generation.
3. Data implementation: reproducible additive production overlay, revision/bootstrap integration and integrity tests. Preserve original data, Drive manifests and old media.
4. Image execution: establish and inspect identity A, then one materially different hair/makeup/hand/gaze recipe before expanding. Use accepted parents for creative comparisons. Record each actual submission/result and inspect every published file.
5. UI implementation: add generated-image preview/figure/source notices using existing design components; expose guide and separate generation/application prompts and original-size assets.
6. Integration: accept real files into the overlay, normalize, build, bootstrap and verify actual local API export and UI.

At most three simultaneous child agents. Disjoint file ownership for concurrent implementations. The parent performs final API/screen checks rather than trusting worker summaries.

## 6. Checks and completion

- Exact 147 accepted unique image files for the current release, 148 slots with the neutral shared once.
- All generated assets have exact prompt/provenance, guide, usable URL and visual QA; no unresolved placeholders.
- All entries across 29 categories have guide/application-prompt coverage.
- Original 2,749 entries, 2,914 media and 7,167 Drive mappings remain preserved as exact baseline subsets.
- Normalization is idempotent; foreign keys and production manifest joins are clean.
- Project data tests, TypeScript and build pass; API/export matches the composed data.
- Desktop/mobile catalog/detail, image access and guide/prompt export are exercised on the actual local application. Do not claim a browser/API limitation was solved without evidence.
- Final report states planned/generated/accepted/applied counts separately, real checks, file locations and unresolved issues. No remote deployment or git commit.
