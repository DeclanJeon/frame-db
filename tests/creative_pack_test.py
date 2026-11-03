"""Deterministic, invented creative-review fixtures; no live input writes."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from web_pack_test import batch_fixture, review_fixture
from web_pack import WebPackError, canonical, sha256, validate_review
from creative_pack import (DETAIL_KEY, apply_creative, creative_revision,
                           load_creative, validate_creative)


class CreativePackTests(unittest.TestCase):
    def setUp(self):
        batch = batch_fixture()
        self.approved = [validate_review(canonical(batch).encode(), review_fixture(batch))]
        self.supplement = {
            "schema_version": 1, "kind": "proposal", "authorship": "Test creative author",
            "scope": "Invented creative directions only", "basis_policy": "Adaptation, not source facts",
            "records": [
                {"entry_id": target, "category_id": "hair", "basis": ["hair/test-concept"],
                 "directions": ["Choose a creative variable."]}
                for target in ("accepted", "rejected")
            ],
        }
        self.review = {
            "schema_version": 1, "kind": "independent_creative_metadata_review",
            "status": "reviewed_with_rejections", "reviewer": "Independent test reviewer",
            "accepted_entry_ids": ["accepted"], "rejected_entry_ids": ["rejected"],
            "decisions": [
                {"entry_id": record["entry_id"], "category_id": "hair",
                 "basis": record["basis"], "decision": decision, "reason": "Test reason"}
                for record, decision in zip(self.supplement["records"], ("accepted", "rejected"))
            ],
        }
        self.seed = {
            "entries": [
                {"id": target, "category_id": "hair", "source_id": "studio",
                 "title": target, "description": "Keep original.", "status": "text",
                 "details": json.dumps({"original": {"nested": [1, None, "preserve"]}})}
                for target in ("accepted", "rejected", "untargeted")
            ],
            "media_assets": [{"id": "existing-media", "url": "/api/media/original"}],
            "prompt_templates": [{"entry_id": "accepted", "text": "Unchanged prompt"}],
            "sources": [{"id": "studio"}], "import_batches": [{"indexed": 482}],
        }

    def validate(self):
        raw = canonical(self.supplement).encode()
        return validate_creative(raw, {**self.review, "input_sha256": sha256(raw)}, self.approved)

    def test_accepted_only_preserves_original_fields_and_media(self):
        before = copy.deepcopy(self.seed)
        creative = self.validate()
        result = apply_creative(self.seed, creative)
        self.assertEqual(self.seed, before)
        self.assertEqual(set(result), set(before))
        for key in before.keys() - {"entries"}:
            self.assertEqual(result[key], before[key])
        self.assertEqual(result["entries"][1:], before["entries"][1:])
        current = result["entries"][0]
        self.assertEqual({k: v for k, v in current.items() if k != "details"},
                         {k: v for k, v in before["entries"][0].items() if k != "details"})
        details = json.loads(current["details"])
        self.assertEqual(details.pop(DETAIL_KEY), creative.overlays["accepted"])
        self.assertEqual(details, json.loads(before["entries"][0]["details"]))
        self.assertNotIn("web_research", json.loads(current["details"]))
        self.assertEqual(creative.overlays["accepted"]["basis"][0]["key"], "hair/test-concept")
        self.assertEqual(creative.overlays["accepted"]["basis"][0]["sources"],
                         [{"source_id": "official", "url": "https://primary.example.test/lesson"}])

    def test_repeat_is_exactly_idempotent(self):
        creative = self.validate()
        result = apply_creative(self.seed, creative)
        self.assertEqual(canonical(apply_creative(result, creative)), canonical(result))

    def test_rejected_only_is_exact_noop(self):
        self.review["accepted_entry_ids"] = []
        self.review["rejected_entry_ids"] = ["accepted", "rejected"]
        self.review["decisions"][0]["decision"] = "rejected"
        self.assertEqual(apply_creative(self.seed, self.validate()), self.seed)

    def test_duplicate_target(self):
        self.supplement["records"].append(copy.deepcopy(self.supplement["records"][0]))
        with self.assertRaisesRegex(WebPackError, "duplicate creative target"):
            self.validate()

    def test_missing_or_wrong_category_targets_including_rejected(self):
        for index in (0, 1):
            for change in ("missing", "wrong-category"):
                with self.subTest(index=index, change=change):
                    seed = copy.deepcopy(self.seed)
                    if change == "missing":
                        seed["entries"].pop(index)
                    else:
                        seed["entries"][index]["category_id"] = "makeup"
                    with self.assertRaisesRegex(WebPackError, "missing or wrong category"):
                        apply_creative(seed, self.validate())
                    self.assertNotIn(DETAIL_KEY, self.seed["entries"][0]["details"])

    def test_duplicate_seed_id(self):
        self.seed["entries"].append(copy.deepcopy(self.seed["entries"][0]))
        with self.assertRaisesRegex(WebPackError, "duplicate seed"):
            apply_creative(self.seed, self.validate())

    def test_stale_sha_even_for_whitespace_only_change(self):
        raw = canonical(self.supplement).encode()
        review = {**self.review, "input_sha256": sha256(raw)}
        with self.assertRaisesRegex(WebPackError, "stale creative input SHA"):
            validate_creative(raw + b"\n", review, self.approved)

    def test_invalid_and_unapproved_basis(self):
        for reference in ("hair/unknown", "unknown/test-concept", "HAIR/test-concept"):
            with self.subTest(reference=reference):
                self.supplement["records"][0]["basis"] = [reference]
                self.review["decisions"][0]["basis"] = [reference]
                with self.assertRaisesRegex(WebPackError, "unapproved creative basis"):
                    self.validate()
        self.setUp()
        batch = batch_fixture()
        self.approved = [validate_review(canonical(batch).encode(), review_fixture(batch, accepted=[]))]
        with self.assertRaisesRegex(WebPackError, "unapproved creative basis"):
            self.validate()

    def test_full_partition_no_overlap_duplicates_or_unknown_ids(self):
        for accepted, rejected in [([], ["rejected"]), (["accepted"], ["accepted", "rejected"]),
                                   (["accepted", "accepted"], ["rejected"]),
                                   (["accepted", "unknown"], ["rejected"])]:
            with self.subTest(accepted=accepted, rejected=rejected):
                self.review["accepted_entry_ids"] = accepted
                self.review["rejected_entry_ids"] = rejected
                with self.assertRaises(WebPackError):
                    self.validate()

    def test_complete_matching_decisions_and_reasons_required(self):
        for change in ("missing", "duplicate", "partition", "reason", "category", "basis"):
            with self.subTest(change=change):
                review = copy.deepcopy(self.review)
                if change == "missing":
                    self.review["decisions"].pop()
                elif change == "duplicate":
                    self.review["decisions"].append(copy.deepcopy(self.review["decisions"][0]))
                else:
                    field, value = {"partition": ("decision", "rejected"), "reason": ("reason", ""),
                                    "category": ("category_id", "makeup"), "basis": ("basis", [])}[change]
                    self.review["decisions"][0][field] = value
                with self.assertRaises(WebPackError):
                    self.validate()
                self.review = review

    def test_missing_review_never_implies_approval(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(FileNotFoundError):
                load_creative(Path(directory), self.approved)

    def test_revision_tracks_content_and_review_not_web_count(self):
        first = creative_revision(self.validate())
        self.assertEqual(first, creative_revision(self.validate()))
        self.supplement["records"][0]["directions"].append("Another creative choice.")
        self.assertNotEqual(first["dataset_revision"], creative_revision(self.validate())["dataset_revision"])
        self.assertEqual(first["applied_count"], 1)
        self.assertEqual(first["accepted_entry_ids"], ["accepted"])
        self.assertEqual(first["rejected_entry_ids"], ["rejected"])

    def test_reserved_metadata_collision_fails_closed(self):
        self.seed["entries"][0]["details"] = canonical({DETAIL_KEY: {"unexpected": True}})
        with self.assertRaisesRegex(WebPackError, "collision"):
            apply_creative(self.seed, self.validate())


if __name__ == "__main__":
    unittest.main()
