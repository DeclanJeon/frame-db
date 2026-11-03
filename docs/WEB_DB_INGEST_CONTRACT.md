# Offline web ingestion contract v1

This foundation does not collect sources or change the active website. It uses
Python 3.10+ standard-library code and the existing standalone unittest convention.
No network, credentials, paid services, media IO, database IO or normalization runs
are part of validation, staging or merging. Source facts must be collected and
independently reviewed by separate workers. Offline validation verifies their
recorded contract, not the truth of an inaccessible page or a reviewer's identity.

## Commands and paths

Run from the project root:

```sh
python3 scripts/data/web_research.py validate-staging --category hair
python3 scripts/data/web_research.py validate-review --category hair
python3 scripts/data/web_research.py stage-reviewed --categories hair,makeup
python3 scripts/data/web_research.py stage-reviewed --all
python3 tests/web_pack_test.py
```

All CLI commands accept `--root /absolute/research-directory` after the command.
The default is this repository's `data/web-research`, independent of working
directory. The category allowlist is the 29 IDs in `data/web-population-spec.json`;
paths in that specification are equivalent to the fixed conventions below.

| Path under research root | Owner / purpose |
| --- | --- |
| `staging/{category_id}.json` | Collector batch, UTF-8 JSON |
| `reviews/{category_id}.json` | Separate review of the exact staging bytes |
| `accepted/{category_id}.json` | Generated approved snapshot, not a seed |
| `revision.json` | Generated accepted-file hashes and dataset revision |

Validation is read-only and returns JSON with exit 0 on success, exit 1 with a
diagnostic on invalid JSON/contract or missing files. Usage errors exit 2.
`validate-staging` reports `records` and `structural_only: true`;
`validate-review` reports `accepted_count` and
`offline_review_contract_valid: true`. Neither result is a factual-verification
claim. `stage-reviewed` returns the revision object.

`--categories` requires a nonempty comma-separated list with no duplicates.
`--all` means **all 29 categories must have valid staging and review files**;
it never silently skips missing categories. Staging preflights the requested
categories plus every previously accepted category against their current inputs.
It writes deterministic accepted files, then the revision last. Invalid input
causes no writes. A process failure during writing can leave a partial snapshot;
`load_approved` detects that by exact manifest equality and refuses to load it.
Rerunning staging repairs the snapshot from valid current inputs. One staging
writer and one seed writer at a time are required. These are local filesystem
writes only, not active DB ingestion.

## Exact JSON fields

`data/web-research/schema.json` is a Draft 2020-12 batch/review schema.
Every object rejects extra fields. Required fields below are literal JSON keys;
only fields explicitly called optional may be omitted. Strings are nonempty
unless stated otherwise. Times are ISO timestamps containing `T` and a timezone.
URLs are absolute HTTP(S), with no embedded credentials. No-crawl CMU mocap and
MMAC hosts (including subdomains) are rejected anywhere a URL is recorded.
Other sites' no-crawl and access restrictions remain the collector's obligation;
there is no crawler or robots bypass here.

### Batch

| Field | Type / meaning |
| --- | --- |
| `schema_version` | Integer `1` |
| `category_id` | Exact allowlisted ID, matching file and review |
| `collector` | Collector worker identity, different from reviewer |
| `collected_at` | Timestamp |
| `sources` | Array of source objects below; unique IDs and exact URLs |
| `records` | Array of 0..20 distinct supported concept records |
| `shortfall_reason` | String, nonempty when records <20; honest reason, no padding |

Each **source** has:

| Field | Type / meaning |
| --- | --- |
| `source_id` | Batch-local nonempty identifier |
| `url` | Actual primary-source page URL |
| `title` | Original page/document title |
| `publisher` | Responsible institution, manufacturer or original publisher |
| `authors` | Array of known credited authors; empty when not identified |
| `checked_at` | Actual timestamp when collector read source |
| `access` | Literal `public_body`, not search index, blocked response or HTTP status alone |
| `primary` | Literal boolean `true` |
| `locator` | Page, section, heading, paragraph or other precise source location |
| `rights` | Rights object below, media rights distinct from public text access |

**Rights** fields are `status` (`unknown`, `restricted`, `explicit_open`, `owned`),
`evidence_url` (URL or null), `scope` (permitted/unknown actions and limitations),
and `attribution` (credits and license/change-notice obligations, or explicit
unknown). All four fields are required. A status other than `unknown` requires a
non-null evidence URL. Open media status never authorizes acquiring media in this
pipeline. Copyright, personality, commercial and third-party rights are not
inferred from a page being public. Replace blocked/index-only sources with a
readable primary source or report the shortfall.

Each **record** has:

| Field | Type / meaning |
| --- | --- |
| `concept_key` | Stable semantic key, scoped by category |
| `title_ko` | Korean title, 1..160 characters, containing Korean text |
| `subtype` | Specific subcategory |
| `summary` | Short attributed Korean summary, 1..800 characters |
| `facts` | 3..30 distinct category-specific fact fields, not proposals |
| `proposals` | 0..20 separately labeled creative proposals |
| `tags` | Array of unique text labels |
| `existing_entry_id` | Optional existing same-category entry ID or null |
| `media_candidates` | Array of metadata-only candidates, never media rows |

Each **fact/proposal** has `field` (field name), `value` (short text), and
`evidence` (object). Evidence fields are `source_id`, `locator`, and `kind`.
`kind` is `source_claim`, `observation`, `measurement`, or `proposal`. A source's
numeric statement remains a `source_claim`, not a collector measurement.
Observations require additional `observer` and `sample` fields (actual inspected
file/frame/time range); measurements also require `method` and `unit`.
These four additional fields are optional for source claims/proposals.
Proposals must use `proposal`; facts cannot use it. Field names are unique across
both arrays. Values and evidence strings are limited to 2,000 characters.
Never use an unobserved image, unheard clip or unmeasured sample as a fact.

Each **media candidate** has `source_id`, `url`, `kind` (`image`, `video`, `audio`,
`dataset`, `diagram`), `rights_status` (same as the referenced source's status),
`role`, and `conditions`. Candidates stay nested under the record, including
when merged. They do not create variants, media_assets, external image sources,
Drive rows or media acquisition/review counters.

Concept matching uses Unicode NFKC, case folding, and whitespace/underscore/hyphen
normalization. Duplicate keys and normalized titles within a category fail.
Explicit duplicate existing IDs fail. URL spelling or a translated label is not
permission to manufacture a second concept. The reviewer must identify semantic
aliases beyond mechanical normalization and supply `existing_entry_id`.
The merge also matches normalized existing titles and previously stored keys.
Ambiguous matches, cross-category IDs and multiple records targeting one entry
fail instead of guessing. The same key in different categories is allowed.

### Review

| Field | Type / meaning |
| --- | --- |
| `schema_version` | Integer `1` |
| `category_id` | Exact batch category |
| `input_sha256` | Lowercase 64-character SHA-256 of **exact staging file bytes**, including whitespace |
| `reviewer` | Independent worker identity, different from batch collector |
| `reviewed_at` | Actual review timestamp |
| `accepted_concept_keys` | Unique accepted key strings; only these can merge |
| `rejected` | Array of `{concept_key, reason}` objects |
| `source_checks` | Array of independently reopened source checks below |
| `evidence_checks` | Array of per-accepted-field checks below |
| `accepted_count` | Actual length of accepted keys, 0..20 |
| `shortfall` | Integer `20 - accepted_count` |
| `shortfall_reason` | String, nonempty whenever shortfall >0 |

Accepted plus rejected normalized keys must partition the exact staging record
set, without unknown keys, duplicate decisions or overlap. A zero-record batch
and zero-accepted review are valid with an honest shortfall.

Each **source check** has `source_id`, `url` (exact source URL), `checked_at`,
`access` (literal `public_body`), `locator`, `rights_checked` (literal `true`),
and `notes` (what the reviewer actually rechecked, including rights limitations).
IDs must resolve uniquely to batch sources. Each source used by an accepted fact,
proposal or media candidate must have a check.

Each **evidence check** has `concept_key`, `field`, `source_id`, `locator`,
`verdict` (literal `supported`), and `notes` (the reviewer's independent
comparison). There must be exactly one check for every accepted fact and proposal
field, referencing its exact source and locator. Unsupported fields require
rejecting the record or revising staging and producing a new SHA-bound review.
Missing inline evidence, checks or locators cannot pass. The offline tool does
not turn a reviewer's assertion into a fetched/byte-verified source artifact.
Collectors/reviewers must actually read the public source and accurately record
what was checked; no synthetic source claims or invented review results.

## Accepted format and deterministic merge

An accepted file contains exactly `staging_json` (the exact UTF-8 staging bytes
decoded to a string) and `review` (the review object). Revalidation reconstructs
the bytes and checks the SHA, checks current staging/review equality and checks
the accepted revision manifest. A changed review or staging file requires
restaging; changing staging also requires a new review SHA.

`revision.json` contains `schema_version: 1`, `dataset_revision`, and `files`.
`files` is sorted by category and contains `{category_id, sha256}` for every
accepted file's exact bytes. `dataset_revision` is `web-` plus SHA-256 of a
separate canonical content array. Each nonempty accepted category contributes its
category ID, accepted records sorted by normalized concept key, and only their
referenced sources sorted by source ID. Empty categories, rejected records and
review-only changes do not enter that content projection. The exact envelope
hashes in `files` still detect changed staging or reviews and require restaging.
Canonical JSON is UTF-8, sorted keys, no insignificant
whitespace, unescaped Unicode, no NaN/Infinity. Accepted files and revision end
in a newline. Neither current time nor input argument order affects output.

`apply_web(seed, approved)` returns a deep copy; failures never mutate the input.
Duplicate category batches fail. All approvals are revalidated. Existing entries
retain **every original top-level field**, including ID, category, source,
title, status, timestamps, version and authorship. Only JSON `details` gains the
reserved `web_research` mapping keyed by normalized concept. Existing details
keys remain unchanged. Each value stores the original `record`, referenced full
`sources`, local-to-relational `source_ids`, `input_sha256` and `review`.
Original prompt templates/authorship and all other existing rows remain intact.

New metadata-only entries use `web-{category}-{sha256(normalized_key)[:24]}`,
`status: external`, `gender: 공용`, the record's title/summary/subtype, version 1,
the collection date and text-only search terms. Source IDs use
`web-source-{sha256(canonical(source))[:24]}` and `hosting: metadata_only`.
Imported source rights are serialized into `license`; their full attribution
also remains in details. Only accepted records' referenced sources are added.
Imports use `web-import-{category}-{sha256(canonical(accepted_envelope))[:24]}`;
their report explicitly records zero downloaded/reviewed media and actual
accepted concepts. Existing import reports, including verified Drive counters,
are not changed. New entries and sources are deterministically ordered.
Applying the same approvals again is idempotent. Sources/imports from older
approved inputs remain as provenance, not additional concept/media counts.

## Active application hook

The pilot installs this after
`apply_drive(result, refs, *drive_inputs)` and before saving the result in
`scripts/data/normalize.py`:

```python
from web_pack import apply_web, load_approved
research = data / "web-research"
result = apply_web(result, load_approved(research))
```

Run `stage-reviewed --categories hair,makeup` before
`python3 scripts/data/normalize.py --drive`. Normalization requires `--drive`
and fails before seed writes on missing/stale/invalid accepted evidence. The
explicit pilot authorization activates web ingestion on that existing command.
`lib/database.ts` imports the revision, giving bootstrap a new version only when
accepted records or their used sources change. Reordering records, review-only
changes and rejected concepts do not change that content revision; exact file
hashes still detect stale or tampered envelopes and require restaging.
The seed retains only relational arrays. Existing IDs, statuses, prompts,
authorship, collection tables and all Drive mappings remain unchanged.

Source filtering follows both the entry's original source and the attributable
source IDs nested in reviewed enrichment. Source links and facts are exposed in
catalog/detail; no acquired media is explicitly labeled, and candidates never
become image elements. Import reports separate added/enriched entries, reviewed
facts, concept shortfall, downloaded media and visually reviewed media.
No remote deployment or remote DB writes are part of this hook.

## Verification scope

`tests/web_pack_test.py` uses temporary fixture directories and real CLI
subprocesses, no sleeps, network, media transfer or active seed writes. Fixtures
are explicitly invented test data, not research facts. It covers malformed
structures/evidence, duplicate JSON properties and concepts, unknown categories,
source rights/access restrictions, exact SHA binding, independent source/field
checks, accepted-only staging, stale snapshots, literal CLI success/failure,
all-category staging, metadata counter protection, real original-entry
preservation and deterministic/idempotent merges. `foundation-ready.json` is
written only after the real test command passes and records the actual checks.
