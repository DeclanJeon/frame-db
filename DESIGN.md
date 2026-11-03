# FRAME DB existing interface contract

This records the existing interface for the Drive migration. It does not authorize a redesign.

## 1. Atmosphere and identity

A quiet reference library on warm paper with muted purple controls. Real reference images replace classification icons only where a verified media record exists. Technical diagrams remain explicitly labeled diagrams.

## 2. Color

Existing `app/globals.css` tokens: `--bg:#faf9f6`, `--paper:#fff`, `--ink:#262834`, `--muted:#8b8b95`, `--line:#e6e4df`, `--accent:#66589b`, `--soft:#eeebf6`, `--green:#628772`. This change introduces no new palette or dark theme.

## 3. Typography

Preserve the current DM Sans / Noto Sans KR stack and existing heading, body, caption and source-ID classes. Source IDs and multilingual source descriptions must wrap without hiding data.

## 4. Spacing and layout

Preserve the existing 245px desktop sidebar, responsive card grid, 143px card media area, detail dialog and mobile rules. The card preview uses `object-fit:contain`; source images must not be cropped to fill the frame. The detail dialog owns its scroll. Native image aspect ratios are retained in the detail figure.

## 5. Components

- Reference card: existing `EntryCard`, `.reference-block`, `.diagram-preview` and `.ref-base`. The same media surface can show a source image or an owned diagram. Labels distinguish those cases.
- Reference image: native lazy-loaded `<img>` with meaningful alternative text. A failed request produces visible failure text, not an unrelated icon or a silent source-host fallback.
- Detail figure: existing `.technical-figure` container and caption styling; the caption identifies Drive references versus authored diagrams.
- Variant grid: existing `.variant-grid` links, now with thumbnail images and the existing angle/original-ID labels. Links open the corresponding Drive-backed original.
- Controls: retain existing button styles, focus behavior, modal focus management, collection and export actions.

### Generated-reference extension (2026-10-30)

- Reuse the same card, detail figure and variant grid for accepted synthetic reference photographs. Keep `object-fit:contain`, original aspect ratios and the existing typography/spacing; no redesign or new visual tokens.
- Generated images must be labeled `AI 생성 참조`, distinct from Drive originals and technical diagrams. Labels describe the selected media, not the entry's preserved historical status.
- Reuse the detail section/title/list primitives for `활용 가이드`. Separate image-generation instructions from reference-application instructions through descriptive text using existing caption/prompt styles.
- A planned job without an accepted file remains a text/planned state. Do not replace it with a stock icon that implies image completion, and do not state that an accepted generated reference is still missing all media.
- Original-size links and exported guides/prompts remain keyboard accessible. Error states keep the existing visible failure notice.

## 6. Motion and interaction

No new animations or gestures. Preserve the existing click, keyboard and dialog behavior. Real images use lazy loading and async decoding. Thumbnails are used in grids; full originals are not fetched for every card.

## 7. Depth and shape

Preserve the existing paper surfaces, thin borders, card/dialog radii and modal overlay. Do not restyle unrelated navigation, forms or collection screens.

## 8. Accessibility constraints and existing debt

Image content must have descriptive alt text, failures must be announced as status, links retain keyboard access, and mobile layouts must not overflow horizontally. Existing small typography and the lack of a dedicated dark theme predate this migration; they are not claimed to have been audited or redesigned here. Verify actual catalog and detail surfaces at desktop and mobile widths after the media connection changes.
