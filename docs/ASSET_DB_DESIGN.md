# FRAME DB usable-asset design

Date: 2026-10-30
Status: implemented and locally verified. Final counts and evidence: `ASSET_EXPANSION_RESULT.md`.
Requirements: `ASSET_EXPANSION_REQUIREMENTS.md`.

Latest user direction: follow the existing pose/costume reference workflow. The default detail view shows the image and a brief two-line usage guide. Long generation prompts and production provenance remain internal records, not default user-facing instructions.

## Unit of completion

One usable reference is a concept plus an actual accepted asset, a practical guide, a reference-application prompt and reproducible provenance. The image-generation prompt is a separate artifact. Neither an entry, a prompt, an angle nor a source URL is counted as a completed image.

The first image-production scope is hair, makeup, facial expression, gaze and hand gesture. Gaze remains a distinct production domain within the existing `expression` DB category; creating another category would fragment existing searches unnecessarily. Existing action-transition guides stay guides: a still can illustrate a state, not prove a blink, transition, handover or camera movement.

## Whole-DB asset and guide matrix

| DB category | Useful asset | Guide must specify | Main verification |
|---|---|---|---|
| pose | body reference / angle views | weight, support, joint positions, framing | contact, balance, identity |
| costume | garment / outfit views | garment layers, material cues, fit, coverage | garment continuity, overlap |
| hair | controlled head/shoulder photographs | silhouette, length, part, texture, fixed vs variable axes | hairline, length, curl direction |
| makeup | face/detail application photographs | placement, edge, finish, skin preservation | no identity/geometry change |
| expression | face-state images / later transition clips | observable brow/eye/mouth action, intensity, target eyeline | no emotion diagnosis, stable face |
| gesture | hands/contact photographs / later motion clips | handedness, digits, grip, contact, support | anatomy, occlusion, object penetration |
| anatomy | proportion / silhouette reference | fixed identity anchors, scale, view | proportions, silhouette consistency |
| fashion-items | item and worn reference | placement, size relative to body, attachment | attachment and left/right consistency |
| props | prop/use-state reference | object geometry, acting hand, initial/final state | grip, ownership, state changes |
| persona | authored character brief / performed example | motives, decision rules, behavioral context | coherent behavior, no real-person typing |
| acting | blocking diagram / performance clip | action purpose, beats, body route, timing | complete action and motivated response |
| interaction | blocking diagram / interaction clip | roles, distance, eyelines, turn-taking | mutual contact and spatial continuity |
| space | wide / layout / matching-angle reference | layout, entrances, scale, time/weather | spatial consistency and usable coverage |
| lighting | setup diagram plus matched result | source direction, size, contrast, color, exposure | result differs only on intended axis |
| camera | shot example and framing diagram | shot size, viewpoint, subject placement, depth | stable framing and subject scale |
| camera-motion | route diagram plus motion clip | path, speed, lens vs translation, start/end frames | actual continuous movement |
| look | matched style / palette / surface examples | palette, tone, medium, texture, protected skin/subject | distinguish styling from geometry |
| motion | timed clip / state breakdown | anticipation, weight, force, delay, contact | timing, gravity, temporal continuity |
| voice | licensed or original voice sample | timbre identity, resonance, articulation, fixed voice ID | actual listening, no still-image substitute |
| speech | exact script plus speech sample | intent, stress, pause, breath, pace, lip-sync target | exact spoken text and timing |
| sound | playable sound and contextual example | event, perspective, distance, duration, mix role | actual listening, clipping, loop seam |
| story | annotated beats / screenplay example | scene purpose, conflict, reveal, consequences | causal and factual coherence |
| edit | before/after sequence and timeline | cut intention, screen direction, rhythm, continuity | actual playback across the cut |
| delivery | export example / subtitle sample | destination, dimensions, rate, color, text-safe regions | inspect exported artifact |
| brief | filled brief / decision example | audience, purpose, constraints, success criterion | distinguish known facts from assumptions |
| ops | manifest / handoff example | owner, revision, lineage, dependencies, status | trace real files and versions |
| evidence | claim/source/rights ledger | fact vs observation vs proposal, scope of permissions | inspect source and rights evidence |
| handoff | executable generation input packet | reference roles, protected axes, variable axes, input order | packet references actual accepted assets |
| qa | checked example plus failure example | observable acceptance, evidence, exclusions, unresolved risks | fail closed on unperformed checks |

This matrix specifies the complete system. It does not claim audio/video or all future category assets are produced in the first five-domain image batch. Existing numerical category targets are legacy targets, not researched counts of real-world types.

## Practical guide contract

Every entry receives an additive `usage_guide` object:

- `kind`: `authored_guide`, not a sourced factual observation.
- `purpose`: the concrete production decision this exact entry helps make.
- `apply`: ordered steps referencing the entry's actual title and descriptive content.
- `preserve`: identity, shape, geometry, contact, text or other domain-specific invariants.
- `change`: the domain-specific variables permitted by this reference.
- `avoid`: specific common errors relevant to the domain.
- `check`: observable acceptance checks, with no claim that checks were already performed.
- `limitations`: asset availability and what a still/text reference cannot establish.

Category playbooks are authored once and reused as the domain layer, but each entry's purpose and target direction use its own existing content. Guidance must not convert unsourced prose into verified facts or pretend every entry has a generated asset.

## Prompt contract

Keep all original prompts intact. Add an explicitly authored application prompt to every entry, including the 264 web-added entries previously lacking a template. Add exact generation prompts only to planned image jobs.

Application prompt fields: selected reference ID, intended output, target direction, what the reference controls, protected attributes, allowed changes, exclusions, requested QA. The reusable form instructs the user to supply their own character/scene and does not transplant the reference model's identity.

Generation prompt fields: concept/job ID, original or creative class, parent ID when creative, observable distinguishing features, synthetic adult subject specification, camera/framing, lighting, background, visible region, exclusions, output dimensions and acceptance criteria. Store actual submitted text and effective model parameters.

## Reproducible additive integration

1. Leave original catalog, references, source snapshots and verified Drive manifests unchanged.
2. Store source research separately from the authored production manifest.
3. Add a production module after the existing reviewed web and creative composition in normalization.
4. Attach base examples to existing matching IDs. A genuinely new creative concept receives a deterministic new ID and a parent relation; do not relabel an existing concept.
5. New generated media use a separate source and availability class such as `generated_image`. They are not `google_drive`, `external_link` or `owned_diagram`.
6. Publish accepted files under a local static asset path supported by the app build. Existing Drive routes remain unchanged.
7. Include production content in the dataset revision so local bootstrap cannot silently retain an older seed.
8. Catalog previews, detail figures, source labels and statistics must recognize generated images. Do not retain the contradictory notice “no acquired image” on an entry that now has an accepted synthetic image.
9. Detail and JSON/Markdown export must include the guide, application prompt, exact image prompt, media URL, parent and synthetic provenance.
10. Normalization is idempotent. Pending jobs are visible in the production ledger but never create fake media rows.

## Visual and content controls

- Use adult synthetic subjects and neutral backgrounds; do not use unrelated web photographs as identity references.
- Keep identity and framing consistent within controlled comparison sets; use an actual generated reference file for follow-up image edits when consistency is required.
- Hair: enough headroom for the complete silhouette. Describe frontal/side/rear visibility honestly; do not count imagined unseen geometry as verified.
- Makeup: retain pores, facial proportions and distinct skin markings. Show the applied result rather than product packaging.
- Expression: name observable facial actions and intended acting context. A synthetic example is not physiological or psychological evidence.
- Gaze: distinguish subject-left from viewer-left, head orientation from eyeball direction, and direct lens gaze from an off-camera target.
- Hands: specify which hand and object; inspect every visible finger, thumb, joint, contact and occlusion. A cropped hidden finger is not automatically an anatomical defect.
- Reject duplicate-looking variants that fail their specified distinction, broken anatomy, cropped defining features and unreadable target details.
- Record each QA decision against the actual file hash. Generation success alone does not imply acceptance.

## Validation

Check baseline row preservation separately from additive production rows. Existing tests that asserted global totals must be updated to assert the original subset remains exact and the new subset matches the approved production manifest, not weakened to minimum-count checks.

Verify all local generated files exist and are valid images, every accepted job has its guide/prompts, no pending/rejected job appears as media, IDs and parents are unique/resolvable, source claims remain unchanged and every existing entry has guide/application-prompt coverage.

Run normalization twice and compare hashes, run the project's data suite and type/build checks, bootstrap the real local DB and compare export with the composed seed. Inspect representative accepted images in catalog/detail on desktop and mobile, verify original-size access and export content, and report exact counts.
