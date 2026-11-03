# Web DB population recovery

Verified on 2026-10-29. This is an intermediate recovery record, not a publication
or final acceptance report.

## Failure and recovery

The existing run is `dag_b08d0f3b-1ff6-41f3-9a7e-4ca08ea7013b`, key
`frame-db-web-population-20261029-v1`.

`pilot-publish` failed with provider HTTP 403:
`Upstream request failed: Model access is disabled`.
The first attempt recorded zero tool calls. Direct inspection found no accepted
directory, revision or `pilot-ready.json`; no pilot result was accepted.
A corrective message revived the same node, but it failed with the same error.

The same run was amended, changing only the pilot's route from
`unspecified-high` to `deep-low`, which had successfully run the foundation.
Its original scope and acceptance criteria were preserved. The five completed
upstream nodes were retained; the 56 skipped dependents became pending.
The replacement pilot was directly observed running as `st_01a18974`.
Completion notifications were subscribed again. No duplicate run was started.

Current definition fingerprint:
`007cc42ff4372f8ba438c50849919bd055cd14706d42114c30f2075daab9ac20`.

## Direct verification of the retained inputs

The lead read the six foundation deliverables: `web_pack.py`, `web_research.py`,
`web_pack_test.py`, `schema.json`, the ingestion contract and foundation-ready
record. The staging and review JSON files for both pilot categories were also
read directly, rather than accepted from worker summaries.

The following commands were independently run in one sequence, exiting 0:

- `python3 tests/web_pack_test.py`: 34 tests passed.
- `PYTHONDONTWRITEBYTECODE=1 python3 tests/drive_pack_test.py`: 5 passed.
- `PYTHONDONTWRITEBYTECODE=1 python3 tests/database_integrity.py`: 15 passed.
- `validate-staging --category hair`: 20 records; structural validation only.
- `validate-review --category hair`: 18 accepted; exact input SHA valid.
- `validate-staging --category makeup`: 20 records; structural validation only.
- `validate-review --category makeup`: 20 accepted; exact input SHA valid.

The last four commands use `python3 scripts/data/web_research.py`.
The test sequence was observed completing with exit code 0 through monitor
`mon_6EADSW444QGRFY4X`.

The lead independently reopened the supporting primary sources, read the cited
sections and compared them with the accepted facts. Web-open and public-body
fetch were used as complementary readers; a blocked response, an empty
extraction or an HTTP success alone was not treated as evidence.
Glossier's selected Original descriptor was checked in public HTML because its
plain-text extraction omitted the descriptor. No images or video were acquired.

| Category | Staged | Accepted | Existing targets | New concepts | Shortfall |
| --- | ---: | ---: | ---: | ---: | ---: |
| hair | 20 | 18 | 16 | 2 | 2 |
| makeup | 20 | 20 | 18 | 2 | 0 |

These are approval/input counts, not a claim that the active DB already contains
the changes. Hair's butterfly and bixie records remain rejected because their
exact cited source sections were not independently accessible to the reviewer.
No replacement facts were fabricated to meet the target.

All source reuse-rights statuses remain unknown. Facts describe publisher claims,
not measured or visually inspected media. Existing guide status and authorship
must remain unchanged when these facts are attached.

Before pilot integration, the actual seed contained 2,485 entries and 2,914 media
rows. Its hash and the hashes of the Drive assets, transfer audit, media index,
normalizer, database loader and DB schema matched the foundation's recorded
protected hashes. The original seed was retained in the lead's resident kernel
for direct before/after comparison.

## Still pending

The lead has not yet accepted the replacement pilot's implementation, test,
build, API, source-filter or rendered UI results. Those require direct checks
after the node finishes. The remaining 27 category collections/reviews, final
DB application and runtime verification are also not complete.

JSON diagnostics could not run because the configured Biome executable is not
installed. No package was added to work around this.

## Intermediate seed inspection

While the replacement pilot was still running, the lead read the generated seed
directly. It contained 2,489 entries, with 38 approved knowledge concepts attached
to 38 entries: 34 existing targets and four new metadata-only entries. All 2,485
original entry IDs and every original field were preserved, apart from the
intended addition of `details.web_research`. Detail objects were compared
structurally, not by JSON property order. Every original table other than the
explicitly extensible entries, sources and import batches remained identical,
including all 2,914 media rows.

This was an intermediate file comparison, not API or UI acceptance. The lead also
found a forward-integration defect in the in-progress integrity test: its text
entry count was fixed at the pilot-only total of 214. A precise corrective message
was sent to `pilot-publish`, requiring the count to follow actual approved inputs
while preserving exact original-ID/status/authorship and media checks. The
correction and the pilot's final checks still require direct verification.
