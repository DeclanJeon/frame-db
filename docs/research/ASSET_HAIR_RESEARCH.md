# FRAME DB hairstyle asset expansion research

Research and access date: **2026-10-30**.

## Decision

Produce a bounded first collection of **32 master looks and 12 creative derivatives: 44 usable asset packages, 251 accepted photographic images, 44 illustrated-use guides, 251 resolved image-generation prompts, and 44 resolved use prompts**. These are proposed production deliverables, not assets already made.

The existing category has **47 records, zero linked media assets, and zero entry variants**. Adding more descriptions alone would not meet the user's objective. First turn selected existing records into actual multi-view generated assets, then add specific coverage gaps and controlled derivatives. This research task generates no images and changes no database.

There is no supported universal finite count of hairstyles. The working taxonomy below has eight haircut coverage groups and four arrangement groups for this project, with independent modifiers. It is an editorial production scope, not an industry standard or a claim that twelve hairstyle families exhaust the subject. The category's stored target of 1,400 is a project field, not evidence of 1,400 distinct base hairstyles.

## 1. Local evidence and reproducibility

Read the running local API `http://127.0.0.1:5190/api/export/all` on 2026-10-30. Its `exportedAt` was `2026-10-30T08:06:01.093Z`; `schema` was `frame-reference-database-v2`.

Dataset identifier:

```text
frame-reference-db-20261029-v3.3-verified-drive-web-c9c7b7db80b88cf8411b1eca350a1a5d47fa472090a045e1b8862afc237f7866-creative-eb55dfc72cc16f4bade66dd9aaa7b3f0af43f10966be677a38d18909909f6793
```

Top-level arrays include `categories`, `sources`, `reference_entries`, `entry_variants`, `media_assets`, `prompt_templates`, and relations. Hair records were selected by `reference_entries[].category_id === "hair"`. Media and variants were counted by their `entry_id`, not by global totals.

| Check | Observed result |
| --- | ---: |
| Hair category records | 47 |
| `FS-` records | 14 |
| `CRAFT-hair-` records | 31 |
| `web-hair-` records | 2 |
| Status `text` | 14 |
| Status `guide` | 31 |
| Status `external` | 2 |
| Hair-linked `media_assets` | 0 |
| Hair-linked `entry_variants` | 0 |
| Global media rows, all categories | 2,914 |

The export's scope says it is a reference index and text guidance and does not include image files or personal collections. Thus zero means **no hair media registered in this API snapshot**, not proof that no unregistered image exists anywhere on disk or Drive. Existing `details` may contain creative metadata and source bases; these do not constitute generated media.

The following read-only JavaScript describes the exact join used:

```js
const data = await (await fetch("http://127.0.0.1:5190/api/export/all")).json();
const hair = data.reference_entries.filter(row => row.category_id === "hair");
const ids = new Set(hair.map(row => row.id));
const media = data.media_assets.filter(row => ids.has(row.entry_id));
const variants = data.entry_variants.filter(row => ids.has(row.entry_id));
```

## 2. Exact existing inventory

Titles below are copied exactly from the API. Classification is this researcher's interpretation of title plus description. `C` and `A` refer to section 4; `M` means modifier, not an independently evidenced underlying haircut. Gender words are retained because they are in the stored titles, not imposed as eligibility restrictions.

| # | Exact existing ID | Exact existing title | Classification / collision |
| --- | --- | --- | --- |
| 1 | `FS-0001` | 내추럴 단발 | C5 bob; overlaps chin bob, softer fringe/ear tuck |
| 2 | `FS-0002` | 롱 레이어드 | C7 long layers + S-wave finish |
| 3 | `FS-0003` | 로우 번 | A2 low loose bun |
| 4 | `FS-0004` | 하이 포니테일 | A1 high placement |
| 5 | `FS-0005` | 픽시 커트 | C4 pixie |
| 6 | `FS-0006` | 커튼뱅 미디엄 | M curtain fringe + shoulder length; underlying cut unspecified |
| 7 | `FS-0007` | 내추럴 가르마 | M 6:4 part + volume; underlying cut unspecified |
| 8 | `FS-0008` | 텍스처 크롭 | C3 forward crop + matte texture |
| 9 | `FS-0009` | 슬릭백 | M backward combing + sheen; not a new cut |
| 10 | `FS-0010` | 웨이브 미디엄 | M medium length + loose wave; underlying cut unspecified |
| 11 | `FS-0011` | 버즈 커트 | C1 short uniform clipper silhouette |
| 12 | `FS-0012` | 장발 로우 번 | A2; overlaps FS-0003, longer hair/other presentation |
| 13 | `FS-0013` | 바람에 흐르는 머리 | M wind / transient state |
| 14 | `FS-0014` | 젖은 헤어 질감 | M wet finish, explicitly retain current length |
| 15 | `CRAFT-hair-172e978476d9` | 여성 턱선 블런트 보브 | C5 bob + blunt perimeter |
| 16 | `CRAFT-hair-3c739a641a37` | 여성 프렌치 보브 | C5 bob + shorter perimeter/fringe; not another root family |
| 17 | `CRAFT-hair-fae7b816d152` | 여성 비대칭 보브 | C5 bob + fixed asymmetry |
| 18 | `CRAFT-hair-fcee59be5f4f` | 여성 어깨 길이 로브 | C5 longer bob; length variant |
| 19 | `CRAFT-hair-8c33092484ae` | 여성 허쉬 레이어 | C8 shag-like short crown/long nape brief |
| 20 | `CRAFT-hair-e0695130136f` | 여성 긴 생머리 센터파트 | C6 provisional uniform long silhouette + central part |
| 21 | `CRAFT-hair-9bc2665c1374` | 여성 굵은 배럴 웨이브 | M large waves; underlying cut unspecified |
| 22 | `CRAFT-hair-db6e266cbccc` | 여성 작은 내추럴 컬 | M small curls/density; underlying cut unspecified |
| 23 | `CRAFT-hair-b81cfe2d0898` | 여성 사이드 브레이드 | A3 free three-strand side plait |
| 24 | `CRAFT-hair-2c3c47d0ace7` | 여성 더치 브레이드 | A3 raised scalp braid; row count must be locked |
| 25 | `CRAFT-hair-29e4256f3668` | 여성 시뇽 업스타일 | A2 sleek low knot; distinguish from loose low bun by finish |
| 26 | `CRAFT-hair-6498f9b53824` | 여성 높은 번 | A2 high placement |
| 27 | `CRAFT-hair-4edd794c95e4` | 여성 반묶음 리본 | A4 partial gathering + ribbon |
| 28 | `CRAFT-hair-fab7d6565866` | 여성 픽시 사이드파트 | C4 pixie + longer side-swept top |
| 29 | `CRAFT-hair-4b4ae3ff143b` | 여성 슬릭 웻 룩 | M backward direction + wet finish; overlaps FS-0014/FS-0009 |
| 30 | `CRAFT-hair-da40e02a2fb4` | 남성 아이비리그 커트 | C2 short graduated silhouette + combable top |
| 31 | `CRAFT-hair-95f1771af91c` | 남성 크루 커트 | C2 short graduated silhouette; shorter top than Ivy brief |
| 32 | `CRAFT-hair-2c775fc6ba2b` | 남성 프렌치 크롭 | C3 forward crop; overlaps FS-0008 |
| 33 | `CRAFT-hair-a950f255b69d` | 남성 시저 커트 | C3 forward crop + short continuous fringe |
| 34 | `CRAFT-hair-fbf36354c32d` | 남성 클래식 사이드파트 | M part/direction on short cut |
| 35 | `CRAFT-hair-a880b9e0b707` | 남성 커튼 헤어 | M separated long fringe/part |
| 36 | `CRAFT-hair-cc453bee8e0a` | 남성 텍스처 퀴프 | M front lift/back direction |
| 37 | `CRAFT-hair-394c6f009336` | 남성 클래식 퐁파두르 | M larger swept-back front volume; not a new cutting primitive |
| 38 | `CRAFT-hair-9eb96d64ed83` | 남성 소프트 울프 커트 | C8 shag/mullet-adjacent silhouette; fixed longer nape |
| 39 | `CRAFT-hair-1011c8796893` | 남성 어깨 길이 생머리 | C6 provisional uniform medium-long silhouette |
| 40 | `CRAFT-hair-385eb0bfe856` | 남성 내추럴 컬 탑 | M curly top; side geometry unspecified |
| 41 | `CRAFT-hair-fe251591d0aa` | 남성 로우 테이퍼 | M low transition placement; requires top/base specification |
| 42 | `CRAFT-hair-f008bc9d9553` | 남성 브러시업 | M modest upward styling; overlaps quiff direction |
| 43 | `CRAFT-hair-38b90e4d7b02` | 남성 로우 포니테일 | A1 low placement |
| 44 | `CRAFT-hair-caef0dc686ae` | 바람에 앞머리만 움직이기 | M isolated fringe movement |
| 45 | `CRAFT-hair-4c22870f9fb5` | 후드에서 머리 꺼내기 | M garment occlusion / released compression |
| 46 | `web-hair-df04af7fd49cc3139c8d4d20` | 블런트 앞머리 | M fringe edge |
| 47 | `web-hair-68d919205a8f0c5b8449114f` | 위스피 앞머리 | M fringe density |

Do not delete or merge these IDs merely because their families overlap. Preserve record identity; use an explicit master/derivative relationship in a future production manifest. No relationship or schema migration is implemented here.

## 3. Primary source evidence

All sources below were accessed **2026-10-30**, with readable article/course body text, not just a search result. The URLs are first-party educator or brand publications. Their authority here is hairstyle description and technique, not a neutral census of every hairstyle. Summaries are paraphrases.

| Ref | Primary page and URL | Readable evidence | Consequence for FRAME |
| --- | --- | --- | --- |
| S1 | Sassoon Academy, ABC Complete Cutting. https://academy.sassoon-global.com/course-finder/sassoon-cut.html | Researcher reported modules covering lines, graduation, layering and disconnection. Parent re-fetch on 2026-10-30 found only the course name and structured-description text describing an inclusive cutting/barbering programme across hair types, textures, lengths and identities; the detailed module claims were not independently reproduced. | Use only the inclusive programme description as currently corroborated evidence. The detailed technique list is not relied on for production quantities or a canonical taxonomy. |
| S2 | Hair.com / L'Oreal Professional Products Division, Blunt Bob With Bangs. https://www.hair.com/blunt-bob-with-bangs.html | Definition contrasts the blunt straight, unlayered perimeter with layered or stacked bobs. Body was readable despite generic offline/JavaScript banners. | Blunt is a bob construction attribute, not proof that each marketed bob name is a separate base family. |
| S3 | Hair.com / L'Oreal, French Bob. https://www.hair.com/french-bob.html | Definition describes a chin/jaw-area bob with fringe and allows multiple textures. Comparison discusses shorter length and fringe versus a standard bob. | French bob can have its own useful visual master without being counted as a wholly separate root from bob. |
| S4 | Sam Villa, Julia Textured Pixie. https://www.samvilla.com/pages/textured-pixie | Actual steps describe separated side sections, opening above ears and alternating disconnected top subsections. | Pixie references need ear/nape visibility and top-to-side relationships, not just a front beauty image. |
| S5 | Sam Villa, Christi Disconnected Shag. https://www.samvilla.com/pages/razor-cutting | Instructions establish fringe, sides/back length and remove weight in mids/ends to create airy layered appearance. | Shag-like masters must preserve layer/perimeter geometry; styling texture alone does not establish that geometry. |
| S6 | Davines, How to Get the Wet Hair Look. https://us.davines.com/blogs/news/how-to-get-the-wet-hair-look | Article explains product-created sheen and clumping, applicable across straight/curly and short/long hair, rather than literal dripping hair. | Wet is a finish overlay on an identified master, not another haircut. |
| S7 | L'Oreal Paris, How to Dutch Braid Your Hair. https://www.lorealparisusa.com/beauty-magazine/hair-style/braid-hairstyles/how-to-dutch-braid-hair | Body gives under-middle crossing with progressive scalp pickup; contrasts French over-middle crossing and describes double Dutch sectioning. | Distinguish free plait, French, Dutch and row layout by construction, not generic braid labels. |
| S8 | ghd, Defined Curls Ponytail. https://www.ghdhair.com/au/hairstyles/curly/how-to-ponytail-defined-curls | Steps smooth/gather hair at the nape, secure it, then curl sections of the tail. | Tie placement and tail texture are independent controls; low curly ponytail is a derivative. |
| S9 | Wella, Half Up Top Knot. https://www.wella.com/international/wella-tutorials/how-to-half-up-top-knot | Tutorial gathers only the upper section, then twists and wraps its ponytail around the elastic. | Half-up is a partial-gather arrangement; knot, ribbon and loose lengths are separate attributes. |
| S10 | L'Oreal Paris, How To Do Box Braids at Home. https://www.lorealparisusa.com/beauty-magazine/hair-style/hairstyle-trends/how-to-get-box-braids | Body defines square sectioning and individual root-to-end braids, and distinguishes size/sectioning variations. | Add an actual individual-braid construction master, not merely a curl or generic Dutch-braid tag. |
| S11 | L'Oreal Paris, How To Keep Your 4C Hair Healthy and In Style. https://www.lorealparisusa.com/beauty-magazine/hair-care/all-hair-types/how-to-care-for-4c-hair | Cornrow section describes close-to-scalp rows with configurable paths; separately discusses box braids. | Add a row-layout master with readable scalp topology. Do not treat cornrows as a renamed single Dutch braid. |
| S12 | Wahl Australia, Disconnected Undercut. https://au.wahl.com/how-to-disconnected-undercut | Readable numbered steps distinguish side fading, top layering and a hard part. | The top/side disconnect needs explicit geometry and both profiles; this is a structural modifier, not just shine or combing direction. |
| S13 | Hair.com / L'Oreal, Layered Bob. https://www.hair.com/layered-bob.html | Stacked section describes back-concentrated layers building volume; graduated and asymmetric examples also appear. | Add a posterior weight-build-up master to contrast with the existing blunt bob. |
| S14 | Sam Villa, Noel Textured Coils. https://www.samvilla.com/pages/textured-coils | Readable preparation, separation and diffusing steps preserve curl pattern while controlling volume. | Coils deserve a resolved silhouette/texture master, but texture itself is not a new cutting primitive. |
| S15 | Hair.com / L'Oreal, Rope Braid. https://www.hair.com/rope-braid.html | Two sections twist in the same direction and wrap together in the opposite direction. | A two-strand rope requires a different topology from a three-strand plait. |
| S16 | Wahl UK, Home Hair Cutting Guide. https://www.wahl.co.uk/content-hub/product-guides/home-hair-cutting-guide/ | Separate shaved-head, buzz and crew sections; buzz uses an attachment length, shaved-head instructions finish with a shaver. | Include a near-shaved visual endpoint without claiming it creates a new root family beyond compact clipper shapes. |

Freshness and retrieval limits:

- S2 displayed a 2025 title, a 2026-09-01 update, and older 2023 trend prose. Use its structural definition, **not** its inconsistent trend dating.
- S3 displayed 2024-08-29; S6 2025-12-12; S10 2025-07-17; S15 2024-09-18. Access date is not publication date. No demand or trend ranking is inferred from these dates.
- The server web opener timed out for S7 twice. A direct page fetch subsequently returned the readable full tutorial and its actual crossing instructions; this is not snippet-only evidence.
- Wahl USA's men's-haircuts page returned an error/security block; it is not used as evidence. A ghd bun article redirected to the generic hairstyle index; that article is not used as bun-specific evidence.
- Source pages were read as text. Their photographs were not downloaded, visually measured, licensed or treated as generated assets. This memo does not claim multi-view photographic coverage exists on those pages.

## 4. Bounded taxonomy: structure before styling

### Haircut coverage groups: eight for this collection

These are useful visual retrieval buckets with some overlap, not eight scientifically disjoint primitives. Cutting techniques and recognizable silhouettes such as bob/pixie/crop are different abstraction levels. Do not equate these two levels. The detailed Sassoon module list reported during research was not reproduced in the parent's current fetch, so the eight buckets remain explicit FRAME editorial choices rather than a source-certified taxonomy.

| Group | Base silhouette / structural test | Existing anchors | Variants that do not multiply the root |
| --- | --- | --- | --- |
| C1 | Compact clipper shape: near-uniform short coverage | FS-0011 | Shaved vs buzz length, lineup, hairline shape [S16] |
| C2 | Short graduated top/sides: top length distinct from short sides/nape | CRAFT crew and Ivy League | Part, low taper height, quiff, pomp, brush-up; disconnection is separately recorded [S1, S12] |
| C3 | Forward-fringe crop silhouette | FS-0008; CRAFT French crop and Caesar | Fringe edge, short length and texture treatment; crop/Caesar are distinct masters within one working group |
| C4 | Pixie: short nape/ears with shaped longer top | FS-0005; CRAFT pixie sidepart | Sidepart, top sweep, disconnection, texture [S4] |
| C5 | Bob perimeter around jaw through shoulder; weight construction specified | Four CRAFT bobs/lob; FS-0001 | French, blunt, asymmetric and lob names describe combinations; graduated back is a useful extra structural master [S2, S3, S13] |
| C6 | Medium/long uniform-looking perimeter, minimal visible layering | CRAFT long centerpart and shoulder straight | Length, part, ear tuck, finish; API prose does not prove cutting technique, so classification remains provisional |
| C7 | Distributed layered loose silhouette | FS-0002 | Wave size, coil pattern, part and volume; rounded coily shape must be explicitly art-directed [S1, S14] |
| C8 | Shag / elongated-back layered silhouette with short upper layers | CRAFT hush and soft wolf | Softness, length, fringe, texture; not a claim that Korean hush, shag, wolf and mullet are exact synonyms [S5] |

### Arrangement coverage groups: four, not haircuts

| Group | Construction | Existing coverage | Production boundary |
| --- | --- | --- | --- |
| A1 | Gathered hair with freely hanging tail | High and low ponytail | High/low placement and straight/curled tail are variants [S8] |
| A2 | Wrapped/pinned knot or bun | Low bun, chignon, high bun | Knot location, tension, looseness and pin placement are variants; these are not new underlying cuts |
| A3 | Interlaced/twisted construction | Side three-strand plait and Dutch | Record free vs scalp-attached, crossing, strand count, row count and section map; French, box, cornrow and rope constructions need distinct reference masters [S7, S10, S11, S15] |
| A4 | Upper hair gathered while lower lengths remain loose | Half-up ribbon | Ribbon, upper pony or upper knot modify partial-gather structure [S9] |

Independent modifiers: actual length landmarks; fringe shape/density; part side/ratio; curl pattern and diameter; density; taper location; disconnection boundary; combing direction; front height; matte/gloss/wet finish; accessories; environmental motion; compression/occlusion. Color and gender presentation do not multiply haircut counts.

Not included in this bounded first collection: loc construction, extensions/weave installation systems, specialist historical coiffures, complex braided patterns, and fantasy gravity-defying hair. These are real potential expansion areas, not evidence that the chosen collection is complete. Investigate their own primary techniques before adding them.

## 5. Exact production scope and views

### Master selection: 24 existing looks

`L` = loose/short-hair reference package, six photos. `A` = arranged reference package, seven photos. A master can deliberately demonstrate a modifier; a master count is **not** a haircut-family count.

| Master | Existing ID | Type | Image brief: invariant and distinct test |
| --- | --- | --- | --- |
| E01 | `FS-0011` | L | Uniform visible buzz stubble; intact hairline and scalp curvature |
| E02 | `CRAFT-hair-95f1771af91c` | L | Crew top shorter toward crown, neat short sides |
| E03 | `CRAFT-hair-da40e02a2fb4` | L | Ivy top visibly combable, part stays on subject's left |
| E04 | `CRAFT-hair-2c775fc6ba2b` | L | Textured forward French crop with horizontal fringe |
| E05 | `CRAFT-hair-a950f255b69d` | L | Short continuous Caesar fringe; less broken edge than E04 |
| E06 | `FS-0005` | L | Soft pixie top, short sides and nape |
| E07 | `CRAFT-hair-fab7d6565866` | L | Pixie with longer side-swept top and visible ears |
| E08 | `CRAFT-hair-172e978476d9` | L | Jawline blunt bob, even perimeter, fine fringe |
| E09 | `CRAFT-hair-3c739a641a37` | L | Shorter French bob, above-brow fringe per existing brief |
| E10 | `CRAFT-hair-fae7b816d152` | L | Asymmetric bob, subject's right side longer throughout |
| E11 | `CRAFT-hair-fcee59be5f4f` | L | Shoulder-contact lob, slight outward ends |
| E12 | `CRAFT-hair-e0695130136f` | L | Long straight centerpart, uniform-looking perimeter |
| E13 | `FS-0002` | L | Long layers with soft S bends; retain chest-below length |
| E14 | `CRAFT-hair-8c33092484ae` | L | Hush: short upper/face layers over longer nape |
| E15 | `CRAFT-hair-9eb96d64ed83` | L | Soft wolf: ear clearance and longer textured back |
| E16 | `CRAFT-hair-db6e266cbccc` | L | Small defined natural curls; shoulder-length layered base chosen for production |
| E17 | `CRAFT-hair-385eb0bfe856` | L | Curly top; short blended sides chosen and locked for production |
| E18 | `FS-0004` | A | High ponytail behind crown, fixed tie and tail length |
| E19 | `CRAFT-hair-38b90e4d7b02` | A | Low ponytail at nape, visible attachment and loose tail |
| E20 | `FS-0003` | A | Loose low bun, controlled wisps, visible neck clearance |
| E21 | `CRAFT-hair-6498f9b53824` | A | High round bun with fixed wrap and size |
| E22 | `CRAFT-hair-b81cfe2d0898` | A | Three-strand free braid over subject's left shoulder |
| E23 | `CRAFT-hair-2c3c47d0ace7` | A | Two raised Dutch scalp rows, centerpart and under-crossing |
| E24 | `CRAFT-hair-4edd794c95e4` | A | Upper section tied at occiput with fixed ribbon; lower half loose |

E16, E17 and E23 resolve missing geometry/row-count details editorially; those specifics were not present as full specifications in the API. E03 and E10 similarly resolve unspecified laterality. Store these decisions as production attributes rather than pretending they were source facts.

### Eight proposed additions, not existing DB IDs

`N01`-`N08` are memo-only planning labels. Do not insert them as if already registered.

| Proposal | Type | Image brief / useful coverage gap | Evidence |
| --- | --- | --- | --- |
| N01 Near-shaved scalp | L | Almost no projecting hair; clear distinction from E01 visible stubble. Length endpoint within C1, not a new root family. | S16 |
| N02 Graduated posterior bob | L | Jaw-length front with deliberate rounded weight build-up at occiput and shorter nape; contrast E08's blunt geometry | S1, S13 |
| N03 Disconnected undercut | L | Longer top over visibly disconnected short sides; boundary stays fixed around head, not a smooth all-over blend | S1, S12 |
| N04 Rounded coily loose silhouette | L | Compact round crown/side envelope with tightly coiled strands and clear nape; no straightening or identical corkscrews. Geometry is FRAME art direction, not a newly claimed universal family. | S14 |
| N05 Single French scalp braid | A | One centered scalp-attached over-crossing braid with free tail; contrast raised Dutch E23 | S7 |
| N06 Box braids | A | Individually hanging medium-width braids from a fixed square parting grid; no scalp-length continuous rows | S10 |
| N07 Straight-back cornrows | A | Six close-to-scalp rows with fixed paths and visible separations; six is an editorial choice, not a canonical rule | S11 |
| N08 Two-strand rope tail | A | Two twisted sections wrapping opposite to their individual twists; fixed low attachment and end elastic | S15 |

### Twelve creative derivatives from exact existing records

Each derivative has four new photos, uses a master reference, and changes only its declared attributes. These are FRAME creative recommendations, not names copied from the primary sources. D10-D12 are still sequences, not video promises.

| Derivative | Exact existing basis | Resolved image delta / guide instruction | Use-prompt intent |
| --- | --- | --- | --- |
| D01 Ear-tucked blunt bob | `CRAFT-hair-172e978476d9` + `FS-0001` | Tuck only subject's left side behind ear; preserve blunt jaw perimeter | Dialogue profile with ear visible; do not shorten tucked side |
| D02 Curtain-fringe long layers | `FS-0002` + `FS-0006` | Add split cheekbone-flowing fringe to E13; retain back length and layer structure | Portrait with eyes clear and symmetric split continuity |
| D03 Barrel-wave long hair | `CRAFT-hair-e0695130136f` + `CRAFT-hair-9bc2665c1374` | Apply large outward bends to E12, no recut or recolor | Formal portrait; carry the same wave spacing to reverse angle |
| D04 Sleek chignon interpretation | `FS-0003` + `CRAFT-hair-29e4256f3668` | Tighten E20 into smooth low pinned knot; remove loose wisps | Formal neck/ear silhouette; pin stays on subject's left |
| D05 Curled low ponytail | `CRAFT-hair-38b90e4d7b02` + `FS-0010` | Curl E19 tail only, keep tie at nape [S8] | Movement-ready portrait without moving attachment upward |
| D06 Half-up knot without ribbon | `CRAFT-hair-4edd794c95e4` + `CRAFT-hair-6498f9b53824` | Wrap only gathered upper section into a small knot; lower half remains loose [S9] | Casual back/side view; never turn into a full bun |
| D07 Low-taper textured quiff | `CRAFT-hair-fe251591d0aa` + `CRAFT-hair-cc453bee8e0a` | Use E03 top/sides, apply low ear/nape transition and modest front lift | Editorial short-hair portrait with transition height preserved |
| D08 Soft matte pompadour | `CRAFT-hair-394c6f009336` + `CRAFT-hair-fbf36354c32d` | Use E03 geometry; increase swept-back front envelope, retain subject-left part, matte finish | Three-quarter portrait; do not elongate skull to make height |
| D09 Wet swept-back pixie | `FS-0005` + `FS-0009` + `FS-0014` + `CRAFT-hair-4b4ae3ff143b` | E06 cut unchanged; add backward clumping and gloss [S6] | Wet-look editorial shot, not a longer haircut or dripping water |
| D10 Fringe-only wind | `CRAFT-hair-caef0dc686ae` + `FS-0013` | E14 fixed; move thin fringe strands toward subject's right, then recover | Matched sequence with stable scalp and back silhouette |
| D11 Hood-release hair | `CRAFT-hair-4c22870f9fb5` + `CRAFT-hair-1011c8796893` | Shoulder-length version of E12: show hood contact, release and recovery | Garment continuity; hair must not pass through fabric |
| D12 Light-fringe comparison | `web-hair-df04af7fd49cc3139c8d4d20` + `web-hair-68d919205a8f0c5b8449114f` | E08 same length; compare blunt full edge to sparse wispy edge only | Face-visibility comparison without moving hairline or eyes |

### Photo view rules and arithmetic

Every photo is a separately saved image, not an unlabeled collage. These view requirements and counts are FRAME production choices, not counts supplied by the sources.

| Type | Count | Required individual photos | Total |
| --- | ---: | --- | ---: |
| Existing loose/short masters E01-E17 | 17 | Front; subject-left 45-degree three-quarter; subject-left profile; subject-right profile; rear three-quarter; straight rear | 102 |
| Existing arrangements E18-E24 | 7 | Same six views plus crown/attachment detail | 49 |
| New loose/short masters N01-N04 | 4 | Same six views; scalp/nape must remain legible | 24 |
| New arrangements N05-N08 | 4 | Same six views plus top/parting/crossing detail | 28 |
| Styling derivatives D01-D09 | 9 | Front; changed-side profile; rear; close detail of changed feature | 36 |
| Wind sequence D10 | 1 | Matched front 3/4 framing: rest, onset, peak deflection, recovered | 4 |
| Hood sequence D11 | 1 | Matched rear 3/4 framing: hood on, hood leaving hair, released compression, recovered | 4 |
| Fringe comparison D12 | 1 | Matched front and profile for blunt; matched front and profile for wispy | 4 |
| **Total** | **44 packages** | **203 master photos + 48 derivative photos** | **251** |

For E22 the detail is braid crossing near the shoulder; E23/N05/N07 use crown and scalp paths; E24 uses upper-section boundary/tie; buns use wrap/attachment; N06 uses square partings; N08 uses the two-strand crossing. Never substitute a generic face crop for these diagnostic details. For long styles, frame to include the actual ends even if this means a wider bust/torso crop. Front and rear must not silently hide the perimeter behind clothing.

Incremental delivery: the existing-only tranche is 151 images; additions bring masters to 203; derivatives bring the collection to 251. These are accepted-image targets, not generation-call counts. No retry budget or model capability is assumed.

## 6. Guides and executable prompt recipe

The production objective is actual generated assets with useful guides and both image/use prompts. This memo provides the production specification and reusable text; it is not a claim that the 44 final illustrated guides or images exist.

Each of the 44 packages must eventually contain:

1. Its six/seven/four accepted image files and stable view labels.
2. One guide containing: exact source/basis IDs, family and modifiers, locked length landmarks, part laterality, hairline, visible ears/nape, curl scale, arrangement topology, deliberate changes, forbidden drift, and labeled image references.
3. One fully resolved generation prompt per accepted photo (251 total), with actual view, person/reference identifiers and geometry filled in, plus generation provenance.
4. One resolved use prompt per package (44 total) that applies it to a new scene while preserving identity and hairstyle constraints.

Thus 44 guides + 251 image prompts + 44 use prompts = **339 text items alongside 251 image files**. Guide text without the corresponding accepted image references does not complete a package.

### Shared image prompt

Use this as a template only; production must save the resolved prompt, not unresolved braces. The tables in section 5 supply all look-specific geometry and deltas. Model/provider selection and parameter validation belong to a later image-generation task.

```text
Create one photorealistic hairstyle reference photograph of the same adult
subject as the approved identity reference. Look: {master or derivative label}.
Hair geometry: {the selected section-5 brief, resolved to concrete landmarks}.
View: {one exact required view}, using subject-relative left and right.
Preserve the reference subject's face, head proportions, hairline, hair color,
part side, density, length landmarks and texture except the declared delta.
For this derivative only change: {declared delta, or "none"}.
Neutral gray studio background; soft broad neutral lighting; simple matte
collarless garment; realistic strand detail and scalp separation where visible.
Frame the entire hairstyle, including crown, nape and longest ends, with margin.
No text, collage, watermark, beauty-filter reshaping or hidden attachment.
Do not invent extra braid strands, knots, ties or a different haircut.
```

For the first master no approved hair reference exists: establish one front/three-quarter identity-and-look anchor, review it, then use that accepted image plus the geometry brief for the remaining views. Do not generate each angle as a different person. A single fixed seed is not evidence of identity or hairstyle consistency.

For ordinary loose looks choose the six view literals in section 5. For arrangement detail replace the view with the specified crown/attachment/crossing close view. For D10/D11 use the same camera, crop, identity and lighting for all four states; only the state changes. For D12 keep camera and hair length matched across the two fringe conditions.

### Fully specified example: E10 asymmetric bob, right profile

```text
Create one photorealistic right-profile hairstyle reference photograph of an
adult subject. This first look-definition image establishes an asymmetric
straight dark-brown bob: subject's right front ends 3 cm below the jaw corner,
subject's left front ends at the jaw corner, with a continuous shorter nape
and a subject-left part. Smooth dry finish, no waves, no ear tuck.
Show the subject's right cheek and right ear region in strict profile.
The right side is the longer side; do not mirror the hairstyle.
Neutral gray studio, broad soft neutral light, matte collarless gray top.
Include the entire crown, nape and right front tip with clear margin.
No text, collage, watermark, accessories or face reshaping.
```

The 3 cm asymmetry is a proposed measurable art-direction lock, not a sourced measurement. After approval, reuse the same subject and this geometry for the other E10 views.

### Fully specified derivative example: D05 low curly ponytail, rear

```text
Using the approved E19 low-ponytail reference, create one photorealistic straight
rear reference photograph of the same adult subject. Keep the hairline,
dark-brown color, density, nape-level black elastic and gathered scalp hair
unchanged. Restyle only the free tail into broad defined curls. Keep its
underlying hair length; visible hanging length may shorten naturally with curl.
Keep the ponytail fully visible, including its attachment and ends.
Neutral gray studio, soft broad light, matte collarless top.
No higher ponytail, bun, extra tie, new bangs, color shift or mirrored part.
```

Curl-related visible shortening must not be confused with cutting off the tail. The guide must identify both underlying length and visible curled endpoint.

### Use prompt and guide example

```text
Apply the attached E10 hairstyle references to the same adult character in
a seated dialogue portrait. Retain identity, subject-left part, dark-brown
color, short nape, right front 3 cm below jaw and left front at jaw.
Camera sees the character's right three-quarter view. Keep the longer right
side on the character's right even if screen position changes.
Change only pose, clothing, expression and scene lighting. Do not copy the
studio background, reverse the asymmetry, add curls or change the haircut.
```

E10 guide: use for asymmetric silhouette continuity and profile dialogue; inspect both profiles and rear before accepting. Reject a mirrored long side, a missing rear transition, cropped tips, or identical left/right sides. A new scene may change highlights but not the underlying color. All other guides follow this same structure using their section-5 invariant and diagnostic detail.

Derivative use prompts are resolved from the shared use recipe plus the specific intent in the derivative table: attach its master and derivative reference, name the unchanged geometry, state the one permitted styling/state difference, then name the new scene and viewpoint. Do not paste a modifier name alone into an image request and expect its unspecified underlying cut to remain stable.

## 7. Acceptance and boundaries

Production completion requires visual inspection of every accepted image and matching guide:

- All requested views actually show their named side or state; no mirrored asymmetry or part switching.
- Identity, head shape, hairline, base color, density and length remain consistent within a package.
- Blunt, graduated and disconnected weight boundaries stay distinguishable. Top styling must not change skull proportions.
- Braid crossing, strand count, row count, parting grid and attachment remain coherent in front, rear and detail views.
- Ties, pins, ribbons and bun wraps stay in their declared places; loose lower hair remains loose in half-up looks.
- Wind, wet finish, fringe thinning and hood contact alter the intended state rather than replacing the underlying hairstyle.
- Every package includes actual image files, guide image references and resolved image/use prompts. A URL to a source tutorial or a `guide` status alone is insufficient.

No images, DB writes, media registrations, source-image downloads, schema changes or other file edits were performed for this research. Counts are recommendations based on visible coverage gaps and deduplication, not measured popularity, exhaustive cultural coverage, source-photo availability or guaranteed model output.

**Recommendation:** build the 151-image existing-master tranche first, then the 52-image gap tranche, then the 48-image derivative tranche. Retain all 47 original IDs; the remaining records supply modifier/alias coverage instead of forcing one expensive independent photo collection per title.
