# Codex-native image execution contract

This is the execution instruction for the fixed work order, not a separate design or permission to expand its quantities.

## Allowed work

Generate only the job IDs explicitly supplied in the launcher message. Use the installed Codex built-in `image_gen` tool, one distinct image per job, never an API-key script, the failing generic image extension or another image service. No subagents.

Read the local system imagegen skill and its applicable prompt guidance. Obtain each exact job and resolved prompt using:

```text
python3 scripts/data/asset_pack.py JOB_ID [JOB_ID ...]
```

Allowed project writes only:

- Actual generated PNGs under `public/generated/frame-assets/JOB_ID.png`.
- Per-job receipts under `data/asset-production/receipts/JOB_ID.json`.
- Exact actual submitted prompt snapshots under `data/asset-production/.history/prompts/JOB_ID-native.txt`.

Use apply_patch for text receipts/snapshots. Binary generation output may be copied from the actual Codex-generated source into its assigned destination. Do not edit shared results.json, plan, guides, code, DB, tests or other history events. Do not overwrite a pre-existing output; report it so the parent can reconcile.

## Before each generation

0. Identify this exact Codex thread ID (the launcher emits `thread.started`; the shell may also expose `CODEX_THREAD_ID`) and emit `FRAME_THREAD THREAD_ID`. Restrict source-file discovery to `$CODEX_HOME/generated_images/THREAD_ID/`. Never choose the newest file across all generated_images directories: other threads and the user's unrelated work may be generating concurrently. If this thread ID cannot be established, stop before generation. Bind each new file against a per-call listing of this owned directory; no global-time-only attribution.
   After a launcher restart, inspect both the assigned output and its receipt before acting. A completed/generated receipt means skip the job. A `started` or uncertain-write receipt means stop that job and report it for parent reconciliation; a missing project PNG alone is not permission to repeat an in-flight image request. Do not overwrite an existing receipt to hide its prior attempt.
1. Read the specific resolved job direction and QA requirements.
2. Resolve `reference_job_ids` to actual existing project PNGs, in their listed order.
   If `control_images` is present, append those exact SHA-bound files after the job references. Role `composition` is an authored count/layout guide; role `edit_base` is a previous generated working image that is explicitly not accepted. Preserve its actual source and rejection reason. Neither auxiliary role is a final delivered photograph or an accepted job. Record the full ordered list in `reference_paths`; the production loader verifies files, hashes and roles. Never count auxiliary images among the 147 accepted photographs.
3. Load those reference images into the native tool context using the image-view tool; explicitly identify their role (identity anchor, same-look parent, hand anchor). Do not rely on an unseen path in the text.
4. Preserve identity and all non-target axes. The exact accepted reference wins over generic descriptions of marks or skin tone.
5. Save the actual tool prompt snapshot. Include concrete reference roles if augmenting the resolved prompt; no unresolved placeholders. This snapshot must match the actual text submitted to native image_gen.
6. Record a receipt with job_id, status `started`, submitted prompt, reference_paths and requested dimensions before submission. Also record `generation_thread_id`, `source_directory` and `before_source_files` (the exact existing filenames in this owned thread directory). These are required for crash-safe attribution: after a launcher restart the parent can identify a unique newly created file without a duplicate image call. A started receipt must be written completely before calling the image tool.

## After each generation

Inspect the actual image. If a target dimension differs, report the actual dimensions and leave for parent review; do not stretch/crop or fabricate metadata. Inspect the job-specific visual distinction, identity and anatomy/contact. Never infer actual emotion, physical angle, force or temporal movement.

Prefer the exact generated filename returned in the native tool's own text output. Do not stringify or print a base64 image result: it can hide the filename behind output truncation. Use the returned image through the native image-display helper and retain the tool's short path metadata. If the launcher stops after the native call, the tool result in its own rollout is authoritative for source-path recovery; do not submit another image merely because a receipt was not finalized.

Copy the real output into the project only when it is the requested artifact. Record:

```text
job_id
status: generated | rejected | failed
path
generation_source_path
sha256
width
height
tool: codex CLI built-in image_gen
model: actual exposed model, or explicitly not exposed
prompt: exact actual submitted text
reference_paths: actual ordered project reference paths
qa: reviewer, provisional decision and concrete visible observations
```

A worker's provisional QA is not the parent's final acceptance or DB application. Record failures honestly. Never create blank/placeholder PNGs, clone an earlier asset as a new condition or count a thumbnail as a new image. If an image call has an uncertain outcome, stop and report without automatically repeating it.

When a job is saved and its receipt is written, emit one short line:

```text
FRAME_JOB_DONE JOB_ID PATH SHA256
```

On failure emit `FRAME_IMAGE_FAILURE JOB_ID REASON` and continue only with independent explicitly assigned jobs. Do not attempt a derivative if its reference output is absent or visually rejected. Parent is responsible for final receipt-to-results acceptance and all normalization.

Initial identity A is already accepted at `public/generated/frame-assets/expression-E00.png`. Its model was not exposed by Codex and must not be relabeled as a specific GPT Image model. Establish B with hair-E01 before B derivatives. Follow dependency order for all subsequent jobs.
