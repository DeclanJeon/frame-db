"""Invented offline fixtures, real CLI subprocesses, no live-data writes."""
import copy
from contextlib import closing
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import runpy

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/data"))
from web_pack import (Approved, WebPackError, apply_web, canonical, categories,
                      concept_key, load_approved, parse, sha256, stage_reviewed,
                      validate_batch, validate_review)

STAMP = "2026-10-29T12:00:00Z"

def original_seed():
    """Rebuild original inputs and Drive checks without writing a seed."""
    with patch("web_pack.apply_web", side_effect=lambda seed, approved: seed) as merge, \
         patch("asset_pack.apply_assets", side_effect=lambda seed, pack: seed), \
         patch.object(Path, "write_text"), \
         patch.object(sys, "argv", ["normalize.py", "--drive"]):
        runpy.run_path(str(ROOT / "scripts/data/normalize.py"))
    return merge.call_args.args[0]


def batch_fixture(category="hair"):
    """These examples are test assertions, not collected primary-source facts."""
    return {
        "schema_version": 1, "category_id": category, "collector": "test-collector",
        "collected_at": STAMP, "shortfall_reason": "Only one invented fixture is needed.",
        "sources": [{
            "source_id": "official", "url": "https://primary.example.test/lesson",
            "title": "Invented test lesson", "publisher": "Test publisher", "authors": [],
            "checked_at": STAMP, "access": "public_body", "primary": True, "locator": "Section 1",
            "rights": {"status": "unknown", "evidence_url": None,
                       "scope": "Test only; media rights unverified", "attribution": "Test publisher"},
        }],
        "records": [{
            "concept_key": "test-concept", "title_ko": "테스트 개념", "subtype": "테스트",
            "summary": "실제 연구 사실이 아닌 테스트 데이터입니다.",
            "facts": [{"field": field, "value": "Test fixture value",
                       "evidence": {"source_id": "official", "locator": "Section 1/" + field,
                                    "kind": "source_claim"}}
                      for field in ("technique", "application", "limitation")],
            "proposals": [], "tags": ["test"],
            "media_candidates": [{"source_id": "official",
                                  "url": "https://primary.example.test/example.jpg",
                                  "kind": "image", "rights_status": "unknown",
                                  "role": "Future reference candidate", "conditions": "No acquisition"}],
        }],
    }


def review_fixture(batch, accepted=None):
    keys = [record["concept_key"] for record in batch["records"]]
    accepted = keys if accepted is None else accepted
    return {
        "schema_version": 1, "category_id": batch["category_id"],
        "input_sha256": sha256(canonical(batch).encode()),
        "reviewer": "test-independent-reviewer", "reviewed_at": STAMP,
        "accepted_concept_keys": accepted,
        "rejected": [{"concept_key": key, "reason": "Rejected test fixture"} for key in keys if key not in accepted],
        "source_checks": [
            {"source_id": source["source_id"], "url": source["url"], "checked_at": STAMP,
             "access": "public_body", "locator": "Section 1", "rights_checked": True,
             "notes": "Invented independent check; not an actual source inspection"}
            for source in batch["sources"]
        ],
        "evidence_checks": [
            {"concept_key": record["concept_key"], "field": fact["field"],
             "source_id": fact["evidence"]["source_id"], "locator": fact["evidence"]["locator"],
             "verdict": "supported", "notes": "Invented per-field comparison"}
            for record in batch["records"] if record["concept_key"] in accepted
            for fact in record["facts"] + record["proposals"]
        ],
        "accepted_count": len(accepted), "shortfall": 20 - len(accepted),
        "shortfall_reason": "Test fixture deliberately below population target",
    }


def approval(batch):
    return validate_review(canonical(batch).encode(), review_fixture(batch))


def seed_fixture():
    return {
        "categories": [{"id": "hair"}, {"id": "makeup"}],
        "entries": [{"id": "original", "category_id": "hair", "source_id": "studio",
                     "title": "기존 가이드", "status": "guide", "authorship": "original author",
                     "details": canonical({"original": ["preserve", 1]}), "version": 7}],
        "sources": [{"id": "studio", "hosting": "owned"}],
        "import_batches": [{"id": "drive-import", "report": canonical({"media_downloaded": 2914,
                            "drive_representations": 7167, "drive_verified": True})}],
        "media_assets": [{"id": "media", "url": "/api/media/verified", "entry_id": "original"}],
        "variants": [{"id": "view", "attributes": "verified original bytes"}],
        "prompt_templates": [{"id": "prompt", "entry_id": "original", "authorship": "original author"}],
        "collections": [{"id": "collection", "owner_id": "owner"}],
        "entry_tags": [], "tags": [],
    }


def write_pair(directory, batch, review=None):
    """Runtime fixtures live only under a unique temporary research directory."""
    category = batch["category_id"]
    (directory / "staging").mkdir(exist_ok=True)
    (directory / "reviews").mkdir(exist_ok=True)
    (directory / "staging" / f"{category}.json").write_text(canonical(batch), encoding="utf-8")
    (directory / "reviews" / f"{category}.json").write_text(
        canonical(review if review is not None else review_fixture(batch)), encoding="utf-8")


class BatchValidation(unittest.TestCase):
    def test_partial_batch_when_supported_is_valid(self):
        # Given an honest single-concept batch, when validated, then it remains partial.
        batch = batch_fixture()
        self.assertEqual(len(validate_batch(batch)["records"]), 1)

    def test_malformed_evidence_when_required_information_missing_is_rejected(self):
        # Given malformed evidence variants, when validated, then each fails closed.
        mutations = [
            lambda b: b["records"][0]["facts"][0].pop("evidence"),
            lambda b: b["records"][0]["facts"][0]["evidence"].update(source_id="missing"),
            lambda b: b["records"][0]["facts"][0]["evidence"].update(locator=""),
            lambda b: b["records"][0]["facts"][0]["evidence"].update(kind="measurement"),
            lambda b: b["records"][0]["facts"][0]["evidence"].update(kind="observation"),
            lambda b: b["records"][0]["facts"][0]["evidence"].update(kind="proposal"),
            lambda b: b["records"][0]["facts"].pop(),
            lambda b: b.update(shortfall_reason=""),
            lambda b: b["records"][0]["facts"][0].update(value=123),
            lambda b: b["records"][0]["facts"][0]["evidence"].update(unchecked=True),
        ]
        for mutate in mutations:
            with self.subTest(mutation=mutations.index(mutate)):
                batch = batch_fixture()
                mutate(batch)
                with self.assertRaises(WebPackError):
                    validate_batch(batch)

    def test_source_when_blocked_indexed_nonprimary_or_nocrawl_is_rejected(self):
        # Given inaccessible/restricted collection paths, when validated, then no facts are accepted.
        for updates in ({"access": "blocked"}, {"access": "index_only"}, {"primary": False},
                        {"url": "https://mocap.cs.cmu.edu/search.php"},
                        {"url": "http://kitchen.cs.cmu.edu/"},
                        {"url": "https://sub.mocap.cs.cmu.edu./"},
                        {"url": "file:///etc/passwd"}, {"url": "https://user:secret@primary.test/"}):
            with self.subTest(updates=updates):
                batch = batch_fixture()
                batch["sources"][0].update(updates)
                with self.assertRaises(WebPackError):
                    validate_batch(batch)

    def test_rights_when_claimed_without_evidence_is_rejected(self):
        # Given an unsupported open-rights claim, when validated, then it fails.
        batch = batch_fixture()
        batch["sources"][0]["rights"]["status"] = "explicit_open"
        with self.assertRaises(WebPackError):
            validate_batch(batch)

    def test_unknown_category_when_supplied_is_rejected(self):
        # Given an unregistered category, when validated, then it fails.
        with self.assertRaises(WebPackError):
            validate_batch(batch_fixture("unknown"))

    def test_duplicates_when_normalized_or_attributed_are_rejected(self):
        # Given duplicate concepts/sources/targets/fields, when validated, then they fail.
        for kind in ("key", "title", "source", "url", "target", "field"):
            with self.subTest(kind=kind):
                batch = batch_fixture()
                duplicate = copy.deepcopy(batch["records"][0])
                duplicate.update(concept_key="second", title_ko="두 번째 개념")
                match kind:
                    case "key":
                        duplicate["concept_key"] = " ＴＥＳＴ__concept "
                        batch["records"].append(duplicate)
                    case "title":
                        batch["records"].append(duplicate | {"title_ko": batch["records"][0]["title_ko"]})
                    case "source":
                        batch["sources"].append(copy.deepcopy(batch["sources"][0]))
                    case "url":
                        batch["sources"].append(batch["sources"][0] | {"source_id": "other"})
                    case "target":
                        batch["records"][0]["existing_entry_id"] = "original"
                        duplicate["existing_entry_id"] = "original"
                        batch["records"].append(duplicate)
                    case "field":
                        batch["records"][0]["facts"][1]["field"] = "technique"
                with self.assertRaises(WebPackError):
                    validate_batch(batch)

    def test_media_counter_when_injected_is_rejected(self):
        # Given a candidate trying to become acquired media, when validated, then extra fields fail.
        for location in ("batch", "record", "candidate"):
            batch = batch_fixture()
            target = {"batch": batch, "record": batch["records"][0],
                      "candidate": batch["records"][0]["media_candidates"][0]}[location]
            target["media_downloaded"] = 1
            with self.assertRaises(WebPackError):
                validate_batch(batch)

    def test_observation_measurement_and_proposal_when_explicit_are_distinct(self):
        # Given real-shape sample/method metadata and a labeled proposal, when validated, then kinds survive.
        batch = batch_fixture()
        batch["records"][0]["facts"][0]["evidence"].update(
            kind="measurement", observer="test observer", sample="fixture frame 1",
            method="invented test method", unit="px")
        proposal = copy.deepcopy(batch["records"][0]["facts"][1])
        proposal["field"] = "creative_direction"
        proposal["evidence"]["kind"] = "proposal"
        batch["records"][0]["proposals"].append(proposal)
        self.assertEqual(approval(batch).batch, batch)

    def test_json_when_duplicate_properties_or_nonfinite_is_rejected(self):
        # Given ambiguous JSON, when parsed, then no silent property replacement occurs.
        for raw in (b'{"schema_version":1,"schema_version":2}', b'{"n":NaN}', b'[]'):
            with self.assertRaises(WebPackError):
                parse(raw)

    def test_count_when_more_than_twenty_is_rejected(self):
        # Given 21 distinct fixtures, when validated, then maximum concepts is enforced.
        batch = batch_fixture()
        batch["records"] = [batch["records"][0] | {"concept_key": str(i), "title_ko": f"개념 {i}"}
                            for i in range(21)]
        with self.assertRaises(WebPackError):
            validate_batch(batch)


class ReviewValidation(unittest.TestCase):
    def test_review_when_staging_bytes_change_is_rejected(self):
        # Given a review of exact bytes, when whitespace changes, then the SHA fails.
        batch = batch_fixture()
        with self.assertRaises(WebPackError):
            validate_review((canonical(batch) + "\n").encode(), review_fixture(batch))

    def test_review_when_checks_or_independence_missing_is_rejected(self):
        # Given each broken review invariant, when validated, then it fails.
        mutations = [
            lambda r: r.update(reviewer="test-collector"),
            lambda r: r.update(category_id="makeup"),
            lambda r: r.update(input_sha256="0" * 64),
            lambda r: r["source_checks"].clear(),
            lambda r: r["source_checks"][0].update(rights_checked=False),
            lambda r: r["source_checks"][0].update(url="https://different.example.test/"),
            lambda r: r["evidence_checks"].pop(),
            lambda r: r["evidence_checks"][0].update(locator="wrong section"),
            lambda r: r["evidence_checks"][0].update(verdict="unsupported"),
            lambda r: r["evidence_checks"].append(copy.deepcopy(r["evidence_checks"][0])),
            lambda r: r["accepted_concept_keys"].append("unknown"),
            lambda r: r.update(accepted_count=20),
            lambda r: r.update(shortfall=0),
            lambda r: r.update(shortfall_reason=""),
            lambda r: r["rejected"].append({"concept_key": "test-concept", "reason": "conflicting"}),
        ]
        for index, mutate in enumerate(mutations):
            with self.subTest(mutation=index):
                batch = batch_fixture()
                review = review_fixture(batch)
                mutate(review)
                with self.assertRaises(WebPackError):
                    validate_review(canonical(batch).encode(), review)

    def test_empty_batch_when_shortfall_disclosed_is_valid(self):
        # Given no supported concepts, when reviewed, then no synthetic padding is required.
        batch = batch_fixture()
        batch["records"] = []
        self.assertEqual(approval(batch).review["accepted_count"], 0)

    def test_candidate_when_separate_source_unchecked_is_rejected(self):
        # Given a candidate-only source without a rights recheck, when reviewed, then it fails.
        batch = batch_fixture()
        batch["sources"].append(batch["sources"][0] | {
            "source_id": "media-only", "url": "https://primary.example.test/media"})
        batch["records"][0]["media_candidates"][0]["source_id"] = "media-only"
        review = review_fixture(batch)
        review["source_checks"].pop()
        with self.assertRaises(WebPackError):
            validate_review(canonical(batch).encode(), review)


class MetadataMerge(unittest.TestCase):
    def test_new_reference_when_reviewed_has_no_media_or_generated_authorship(self):
        result = apply_web(seed_fixture(), [approval(batch_fixture())])
        new = result["entries"][-1]
        self.assertEqual(new["status"], "external")
        self.assertEqual(new["source_id"], result["sources"][-1]["id"])
        self.assertEqual(result["sources"][-1]["hosting"], "metadata_only")
        self.assertFalse(any(row.get("entry_id") == new["id"]
                             for key in ("media_assets", "variants", "prompt_templates")
                             for row in result[key]))

    def test_normalization_when_approvals_missing_never_writes_seed(self):
        with patch("web_pack.load_approved", side_effect=FileNotFoundError("missing approval")), \
             patch.object(Path, "write_text") as save, \
             patch.object(sys, "argv", ["normalize.py", "--drive"]):
            with self.assertRaises(FileNotFoundError):
                runpy.run_path(str(ROOT / "scripts/data/normalize.py"))
        save.assert_not_called()

    def test_enrichment_when_explicit_preserves_identity_authorship_and_media(self):
        # Given a guide with original provenance, when enriched, then only details gain research.
        seed = seed_fixture()
        before = copy.deepcopy(seed)
        batch = batch_fixture()
        batch["records"][0]["existing_entry_id"] = "original"
        result = apply_web(seed, [approval(batch)])
        self.assertEqual(seed, before)
        original = result["entries"][0]
        self.assertEqual({k: v for k, v in original.items() if k != "details"},
                         {k: v for k, v in before["entries"][0].items() if k != "details"})
        details = json.loads(original["details"])
        self.assertEqual(details["original"], ["preserve", 1])
        self.assertEqual(details["web_research"]["test-concept"]["sources"], batch["sources"])
        for key in ("media_assets", "variants", "prompt_templates", "collections", "tags", "entry_tags"):
            self.assertEqual(result[key], seed[key])
        self.assertEqual(result["import_batches"][0], seed["import_batches"][0])
        self.assertEqual(json.loads(result["import_batches"][1]["report"])["media_downloaded"], 0)
        self.assertEqual(len(result["entries"]), 1)

    def test_existing_title_when_matching_is_enriched_without_new_identity(self):
        # Given the same title without an explicit ID, when merged, then it enriches.
        seed = seed_fixture()
        batch = batch_fixture()
        batch["records"][0]["title_ko"] = seed["entries"][0]["title"]
        result = apply_web(seed, [approval(batch)])
        self.assertEqual(len(result["entries"]), 1)
        self.assertEqual(result["entries"][0]["id"], "original")

    def test_merge_when_repeated_and_reordered_is_idempotent(self):
        # Given two categories sharing a key, when merged repeatedly/reordered, then bytes are stable.
        seed = seed_fixture()
        hair, makeup = approval(batch_fixture()), approval(batch_fixture("makeup"))
        first = apply_web(seed, [makeup, hair])
        self.assertEqual(first, apply_web(first, [hair, makeup]))
        self.assertEqual(canonical(first), canonical(apply_web(seed, [hair, makeup])))
        self.assertEqual(len(first["entries"]), 3)
        self.assertEqual(len({row["id"] for row in first["entries"]}), 3)
        self.assertEqual(len(first["media_assets"]), 1)

    def test_rejected_record_when_reviewed_never_merges(self):
        # Given a rejected record, when merged, then no entry/source/import is added.
        batch = batch_fixture()
        review = review_fixture(batch, [])
        result = apply_web(seed_fixture(), [validate_review(canonical(batch).encode(), review)])
        self.assertEqual(result, seed_fixture())

    def test_invalid_target_or_duplicate_category_when_merged_preserves_input(self):
        # Given invalid references and duplicate batches, when merged, then the input is intact.
        seed = seed_fixture()
        for target in ("missing", "wrong-category"):
            with self.subTest(target=target):
                bad_seed = copy.deepcopy(seed)
                bad_seed["entries"].append({"id": "wrong-category", "category_id": "makeup",
                                           "title": "다른 분류", "details": "{}"})
                before = copy.deepcopy(bad_seed)
                batch = batch_fixture()
                batch["records"][0]["existing_entry_id"] = target
                with self.assertRaises(WebPackError):
                    apply_web(bad_seed, [approval(batch)])
                self.assertEqual(bad_seed, before)
        item = approval(batch_fixture())
        with self.assertRaises(WebPackError):
            apply_web(seed, [item, item])
        self.assertEqual(seed, seed_fixture())

    def test_ambiguous_titles_when_present_fail_without_mutating_seed(self):
        # Given two originals matching the same title, when merged, then identity is not guessed.
        seed = seed_fixture()
        seed["entries"].append(seed["entries"][0] | {"id": "another"})
        before = copy.deepcopy(seed)
        batch = batch_fixture()
        batch["records"][0]["title_ko"] = seed["entries"][0]["title"]
        with self.assertRaises(WebPackError):
            apply_web(seed, [approval(batch)])
        self.assertEqual(seed, before)

    def test_forged_approval_when_sha_invalid_is_revalidated(self):
        # Given a caller-created approval, when merged, then public merge rechecks it.
        batch = batch_fixture()
        review = review_fixture(batch)
        with self.assertRaises(WebPackError):
            apply_web(seed_fixture(), [Approved(b"{}", review)])

    def test_distinct_batches_when_applied_sequentially_keep_import_attribution_stable(self):
        # Given another concept/source in the same category, when an older batch repeats, then its import is stable.
        first = approval(batch_fixture())
        batch = batch_fixture()
        batch["records"][0].update(concept_key="another-key", title_ko="별도 테스트 개념")
        batch["sources"][0]["title"] = "A different invented primary source"
        second = approval(batch)
        result = apply_web(apply_web(seed_fixture(), [first]), [second])
        self.assertEqual(apply_web(result, [first]), result)

    def test_real_seed_when_enriched_preserves_all_original_rows_and_drive_files(self):
        # Given the real 2,485-entry seed and verified manifest, when merged in memory, then originals survive.
        seed = original_seed()
        manifest = json.loads((ROOT / "data/drive-assets.json").read_bytes())
        audit = json.loads((ROOT / "data/drive-transfer-audit.json").read_bytes())
        before = copy.deepcopy(seed)
        batch = batch_fixture()
        original = next(entry for entry in seed["entries"] if entry["category_id"] == "hair")
        batch["records"][0]["existing_entry_id"] = original["id"]
        result = apply_web(seed, [approval(batch)])
        self.assertEqual(len(seed["entries"]), 2485)
        self.assertEqual(len(manifest["files"]), 7167)
        self.assertEqual((audit["total"], audit["passed"], audit["failed"]), (7167, 7167, []))
        self.assertEqual(len(result["entries"]), 2485)
        for old, new in zip(before["entries"], result["entries"]):
            if old["id"] != original["id"]:
                self.assertEqual(old, new)
            else:
                self.assertEqual({k: v for k, v in old.items() if k != "details"},
                                 {k: v for k, v in new.items() if k != "details"})
                self.assertTrue(json.loads(old["details"]).items() <= json.loads(new["details"]).items())
        for key in seed.keys() - {"entries", "sources", "import_batches"}:
            self.assertEqual(result[key], before[key])
        self.assertEqual(result["import_batches"][:len(before["import_batches"])], before["import_batches"])
        self.assertEqual(seed, before)
        self.assertEqual(apply_web(result, [approval(batch)]), result)

    def test_new_metadata_when_loaded_in_real_relational_schema_has_valid_foreign_keys(self):
        # Given the current SQL schema and a real seed copy, when merged/inserted, then all relations resolve.
        seed = json.loads((ROOT / "data/database-seed.json").read_bytes())
        result = apply_web(seed, [approval(batch_fixture())])
        with closing(sqlite3.connect(":memory:")) as database:
            database.execute("PRAGMA foreign_keys=ON")
            database.executescript((ROOT / "drizzle/0000_yielding_shadowcat.sql").read_text())
            for key, rows in result.items():
                if not rows:
                    continue
                table = {"entries": "reference_entries", "variants": "entry_variants"}.get(key, key)
                columns = [column if column != "group" else "group_name" for column in rows[0]]
                database.executemany(
                    f"INSERT INTO {table} ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})",
                    [[row[column] for column in rows[0]] for row in rows])
            self.assertEqual(database.execute("PRAGMA foreign_key_check").fetchall(), [])
            self.assertEqual(result["media_assets"], seed["media_assets"])
            self.assertEqual(database.execute("SELECT COUNT(*) FROM media_assets").fetchone()[0],
                             len(seed["media_assets"]))
            self.assertEqual(database.execute(
                "SELECT COUNT(*) FROM media_assets WHERE source_id!='frame-generated'").fetchone()[0], 2914)


class StagingCLI(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="frame-web-test-")
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name) / "data/web-research"
        self.directory.mkdir(parents=True)
        write_pair(self.directory, batch_fixture())
        write_pair(self.directory, batch_fixture("makeup"))

    def cli(self, *arguments):
        return subprocess.run(
            ["python3", "scripts/data/web_research.py", *arguments,
             "--root", str(self.directory)],
            cwd=ROOT, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            capture_output=True, text=True, timeout=20, check=False)

    def test_literal_validation_commands_when_valid_pass(self):
        # Given valid temporary fixtures, when literal validation CLIs run, then both succeed.
        for command in ("validate-staging", "validate-review"):
            run = self.cli(command, "--category", "hair")
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(json.loads(run.stdout)["category_id"], "hair")
        self.assertFalse((self.directory / "accepted").exists())

    def test_literal_validation_commands_when_invalid_fail(self):
        # Given a malformed evidence fixture, when both validation CLIs run, then both return failure.
        batch = batch_fixture()
        batch["records"][0]["facts"][0]["evidence"]["source_id"] = "missing"
        write_pair(self.directory, batch)
        for command in ("validate-staging", "validate-review"):
            run = self.cli(command, "--category", "hair")
            self.assertEqual(run.returncode, 1, run.stdout)
            self.assertTrue(run.stderr)

    def test_cli_when_category_unknown_or_input_missing_fails(self):
        # Given invalid identifiers or missing input, when CLI runs, then it fails without output files.
        for category in ("unknown", "../../private", "voice"):
            run = self.cli("validate-staging", "--category", category)
            self.assertEqual(run.returncode, 1)
        self.assertFalse((self.directory / "accepted").exists())

    def test_stage_categories_when_valid_is_deterministic_and_loadable(self):
        # Given reviewed hair/makeup fixtures, when literal stage command runs, then snapshot loads twice identically.
        run = self.cli("stage-reviewed", "--categories", "hair,makeup")
        self.assertEqual(run.returncode, 0, run.stderr)
        revision = json.loads(run.stdout)
        first = {path.relative_to(self.directory): path.read_bytes()
                 for path in self.directory.rglob("*.json")}
        rerun = self.cli("stage-reviewed", "--categories", "makeup,hair")
        self.assertEqual(rerun.returncode, 0, rerun.stderr)
        self.assertEqual(json.loads(rerun.stdout), revision)
        self.assertEqual(first, {path.relative_to(self.directory): path.read_bytes()
                                 for path in self.directory.rglob("*.json")})
        self.assertEqual(len(load_approved(self.directory)), 2)

    def test_revision_when_only_review_or_rejected_content_changes_is_stable(self):
        first = stage_reviewed(self.directory, ["hair", "makeup"])
        batch = batch_fixture()
        rejected = copy.deepcopy(batch["records"][0])
        rejected.update(concept_key="rejected", title_ko="거절된 테스트")
        batch["records"].append(rejected)
        review = review_fixture(batch, ["test-concept"])
        review["reviewed_at"] = "2026-10-29T13:00:00Z"
        write_pair(self.directory, batch, review)
        second = stage_reviewed(self.directory, ["hair"])
        self.assertEqual(first["dataset_revision"], second["dataset_revision"])
        self.assertNotEqual(first["files"], second["files"])
        batch["records"][0]["facts"][0]["value"] = "Changed accepted fixture"
        write_pair(self.directory, batch, review_fixture(batch, ["test-concept"]))
        third = stage_reviewed(self.directory, ["hair"])
        self.assertNotEqual(second["dataset_revision"], third["dataset_revision"])

    def test_revision_when_empty_reviewed_category_added_is_unchanged(self):
        first = stage_reviewed(self.directory, ["hair"])
        batch = batch_fixture("makeup")
        batch["records"] = []
        write_pair(self.directory, batch)
        second = stage_reviewed(self.directory, ["makeup"])
        self.assertEqual(first["dataset_revision"], second["dataset_revision"])
        self.assertEqual(len(second["files"]), 2)

    def test_stage_all_when_all_categories_reviewed_passes(self):
        # Given a fixture for every allowlisted category, when literal --all runs, then all 29 are staged.
        for category in sorted(categories()):
            write_pair(self.directory, batch_fixture(category))
        run = self.cli("stage-reviewed", "--all")
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(len(json.loads(run.stdout)["files"]), 29)
        self.assertEqual(len(load_approved(self.directory)), 29)

    def test_stage_all_when_category_missing_fails_before_any_write(self):
        # Given only pilot fixtures, when --all runs, then missing categories are not skipped.
        run = self.cli("stage-reviewed", "--all")
        self.assertEqual(run.returncode, 1)
        self.assertFalse((self.directory / "accepted").exists())
        self.assertFalse((self.directory / "revision.json").exists())

    def test_stage_when_second_review_invalid_does_not_partially_write(self):
        # Given one changed staging input, when a two-category stage runs, then preflight prevents all writes.
        path = self.directory / "staging/makeup.json"
        path.write_bytes(path.read_bytes() + b"\n")
        run = self.cli("stage-reviewed", "--categories", "hair,makeup")
        self.assertEqual(run.returncode, 1)
        self.assertFalse((self.directory / "accepted").exists())

    def test_load_when_accepted_bytes_tampered_fails(self):
        # Given a staged snapshot, when accepted bytes change, then manifest verification fails.
        stage_reviewed(self.directory, ["hair"])
        path = self.directory / "accepted/hair.json"
        path.write_bytes(path.read_bytes() + b" ")
        with self.assertRaises(WebPackError):
            load_approved(self.directory)

    def test_load_when_source_input_or_review_changes_fails(self):
        # Given a snapshot, when current staging/review changes, then stale acceptance cannot merge.
        for input_kind in ("staging", "reviews"):
            with self.subTest(input_kind=input_kind):
                write_pair(self.directory, batch_fixture())
                stage_reviewed(self.directory, ["hair"])
                path = self.directory / input_kind / "hair.json"
                value = json.loads(path.read_bytes())
                value["collector" if input_kind == "staging" else "reviewer"] = "changed-worker"
                path.write_text(canonical(value), encoding="utf-8")
                with self.assertRaises(WebPackError):
                    load_approved(self.directory)

    def test_stage_when_category_selection_duplicate_is_rejected(self):
        # Given duplicate category selection, when staging, then no accepted files are written.
        run = self.cli("stage-reviewed", "--categories", "hair,hair")
        self.assertEqual(run.returncode, 1)
        self.assertFalse((self.directory / "accepted").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
