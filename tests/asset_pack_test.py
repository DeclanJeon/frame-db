"""Offline production fixtures; never normalize or create live seed/media files."""
from copy import deepcopy
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import sqlite3
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch
import zlib

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/data"))
from asset_pack import (COUNTS, PACK_ID, SOURCE_ID, apply_assets, asset_revision,
                        build_generation_prompt, build_usage_guide,
                        generation_parameters, load_asset_pack)
from web_pack import WebPackError, canonical

CATEGORIES = (
    "pose costume hair makeup expression gesture anatomy fashion-items props persona "
    "acting interaction space lighting camera camera-motion look motion voice speech "
    "sound story edit delivery brief ops evidence handoff qa"
).split()


def plan_fixture():
    jobs = []
    for domain, count in COUNTS.items():
        for i in range(count):
            jid = f"{domain}-E{i:02}"
            jobs.append({
                "id": jid, "domain": domain,
                "category_id": "expression" if domain == "gaze" else domain,
                "entry_id": "original" if jid == "hair-E00" else "new-" + jid,
                "title": "Fixture " + jid, "parent_entry_ids": [], "kind": "base",
                "identity": "A", "view": "Diagnostic frontal view",
                "direction": "An invented observable fixture direction " + str(i),
                "preserve": ["Fixture identity"], "change": ["Fixture target"],
                "qa": ["Inspect fixture target"], "reference_job_ids": [],
                "width": 2, "height": 3,
            })
    # Two intensities target one concept rather than inventing a second entry.
    jobs[COUNTS["hair"] + COUNTS["makeup"] + 2]["entry_id"] = "new-expression-E01"
    jobs[1].update(kind="creative", parent_entry_ids=["original"])
    return {"schema_version": 1, "id": PACK_ID, "jobs": jobs,
            "slot_aliases": [{"id": "gaze-center", "job_id": "expression-E00"}]}


def guides_fixture():
    return {"schema_version": 1, "categories": {
        category: {"purpose": "Fixture production decision " + category,
                   **{field: ["Fixture " + category + " " + field] for field in
                      ("apply", "preserve", "change", "avoid", "check", "limitations")}}
        for category in CATEGORIES}}


def seed_fixture():
    entry = {"id": "original", "category_id": "hair", "source_id": "studio",
             "title": "Original fixture", "original_title": "", "description": "Original description",
             "gender": "공용", "subtype": "fixture", "status": "text",
             "search_text": "original", "details": canonical({"original": {"keep": [1, 2]}}),
             "version": 1, "updated": "2026-10-29"}
    return {
        "categories": [{"id": c, "name": c, "group": "fixture", "description": c,
                        "target": 1400, "sort": i} for i, c in enumerate(CATEGORIES)],
        "entries": [entry], "sources": [{"id": "studio", "name": "Original", "url": None,
                                        "license": "Fixture", "hosting": "owned", "checked": "2026-10-29"}],
        "variants": [], "media_assets": [], "entry_relations": [], "import_batches": [],
        "prompt_templates": [{"id": "original-prompt", "entry_id": "original", "text": "Original",
                              "language": "en", "authorship": "Original", "parameters": "{}"}],
        "tags": [], "entry_tags": [], "skill_mappings": [],
    }


def png_fixture(width=2, height=3, value=0):
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress((b"\0" + bytes([value]) * width * 3) * height))
            + chunk(b"IEND", b""))


class AssetPackTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.directory = self.root / "data/asset-production"
        self.directory.mkdir(parents=True)
        self.plan = plan_fixture()
        self.guides = guides_fixture()
        self.results = {"schema_version": 1, "results": []}

    def load(self):
        for name, value in (("plan", self.plan), ("category-guides", self.guides), ("results", self.results)):
            (self.directory / (name + ".json")).write_text(canonical(value))
        return load_asset_pack(self.directory)

    def accept(self, jid="expression-E00", raw=None):
        job = next(j for j in self.plan["jobs"] if j["id"] == jid)
        raw = png_fixture() if raw is None else raw
        relative = f"public/generated/frame-assets/{jid}.png"
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        row = {"job_id": jid, "status": "accepted", "path": relative,
               "sha256": hashlib.sha256(raw).hexdigest(), "width": job["width"], "height": job["height"],
               "tool": "fixture-tool", "model": "fixture-model", "prompt": build_generation_prompt(job),
               "reference_paths": [], "qa": {"reviewer": "fixture-reviewer", "decision": "accepted",
                                              "observations": []}}
        self.results["results"].append(row)
        return row

    def test_pending_plan_adds_all_guides_prompts_and_no_media(self):
        seed = seed_fixture()
        before = deepcopy(seed)
        pack = self.load()
        result = apply_assets(seed, pack)
        self.assertEqual(seed, before)
        self.assertEqual(len(result["entries"]), len({j["entry_id"] for j in self.plan["jobs"]}))
        self.assertEqual(result["media_assets"], [])
        self.assertEqual(result["variants"], [])
        self.assertEqual(result["prompt_templates"][0], seed["prompt_templates"][0])
        original = result["entries"][0]
        self.assertEqual({k: v for k, v in original.items() if k != "details"},
                         {k: v for k, v in seed["entries"][0].items() if k != "details"})
        details = json.loads(original["details"])
        self.assertEqual(details["original"], {"keep": [1, 2]})
        self.assertEqual(details["usage_guide"]["kind"], "authored_guide")
        for entry in result["entries"]:
            details = json.loads(entry["details"])
            self.assertIn("usage_guide", details)
            for job in details["asset_production"]["jobs"]:
                self.assertEqual(job["status"], "pending")
                self.assertFalse(job["submitted"])
            if entry["id"] != "original":
                self.assertEqual((entry["source_id"], entry["status"]), (SOURCE_ID, "guide"))
        kinds = [json.loads(p["parameters"]).get("kind") for p in result["prompt_templates"]]
        self.assertEqual(kinds.count("image_generation"), 147)
        self.assertEqual(kinds.count("reference_application"), len(result["entries"]))
        self.assertEqual(len(result["entry_relations"]), 1)
        revision = asset_revision(pack)
        self.assertEqual((revision["planned_count"], revision["accepted_count"]), (147, 0))
        self.assertEqual(len(revision["pending_job_ids"]), 147)

    def test_idempotent_with_accepted_media_and_shared_alias(self):
        self.accept()
        pack = self.load()
        first = apply_assets(seed_fixture(), pack)
        second = apply_assets(first, pack)
        self.assertEqual(first, second)
        self.assertEqual(len(second["media_assets"]), 1)
        media = second["media_assets"][0]
        self.assertEqual((media["availability"], media["source_id"]), ("generated_image", SOURCE_ID))
        self.assertEqual(media["original_id"], "expression-E00")
        entry = next(e for e in second["entries"] if e["id"] == media["entry_id"])
        self.assertEqual(json.loads(entry["details"])["asset_production"]["slot_aliases"],
                         self.plan["slot_aliases"])

    def test_actual_submitted_prompt_is_preserved_separately(self):
        row = self.accept()
        row["prompt"] = "Actual fixture submission with a different effective recipe."
        pack = self.load()
        result = apply_assets(seed_fixture(), pack)
        generation = next(p for p in result["prompt_templates"] if p["id"] == "asset-generation-expression-E00")
        self.assertEqual(generation["text"], row["prompt"])  # Shipped provenance equality, not pinned prose.
        attrs = json.loads(result["variants"][0]["attributes"])
        self.assertEqual(attrs["prompt"], row["prompt"])
        self.assertEqual(attrs["parameters"], generation_parameters(self.plan["jobs"][78]))

    def test_failed_and_rejected_results_are_not_media(self):
        self.results["results"] = [
            {"job_id": "expression-E00", "status": "failed", "prompt": "Actual failed fixture submission."},
            {"job_id": "hair-E00", "status": "rejected"}]
        pack = self.load()
        result = apply_assets(seed_fixture(), pack)
        self.assertEqual(result["media_assets"], [])
        self.assertEqual(asset_revision(pack)["failed_job_ids"], ["expression-E00"])
        self.assertEqual(asset_revision(pack)["rejected_job_ids"], ["hair-E00"])

    def test_category_playbook_applies_to_an_unplanned_entry(self):
        seed = seed_fixture()
        seed["entries"].append({**deepcopy(seed["entries"][0]), "id": "voice-fixture", "category_id": "voice"})
        result = apply_assets(seed, self.load())
        voice = next(e for e in result["entries"] if e["id"] == "voice-fixture")
        guide = json.loads(voice["details"])["usage_guide"]
        self.assertEqual(guide, build_usage_guide(voice, self.guides["categories"]["voice"]))
        self.assertNotIn("asset_production", json.loads(voice["details"]))

    def test_rejects_missing_input_files_and_duplicate_json_properties(self):
        with self.assertRaises(FileNotFoundError):
            load_asset_pack(self.directory)
        self.load()
        (self.directory / "results.json").unlink()
        with self.assertRaises(FileNotFoundError):
            load_asset_pack(self.directory)
        (self.directory / "results.json").write_text('{"schema_version":1,"results":[],"results":[]}')
        with self.assertRaises(WebPackError):
            load_asset_pack(self.directory)

    def test_rejects_duplicate_and_invalid_plan_jobs(self):
        cases = []
        duplicate = deepcopy(self.plan)
        duplicate["jobs"][1]["id"] = duplicate["jobs"][0]["id"]
        cases.append(duplicate)
        missing = deepcopy(self.plan)
        missing["jobs"].pop()
        cases.append(missing)
        unknown = deepcopy(self.plan)
        unknown["jobs"][0]["reference_job_ids"] = ["missing"]
        cases.append(unknown)
        cyclic = deepcopy(self.plan)
        cyclic["jobs"][0]["reference_job_ids"] = [cyclic["jobs"][1]["id"]]
        cyclic["jobs"][1]["reference_job_ids"] = [cyclic["jobs"][0]["id"]]
        cases.append(cyclic)
        for field, value in (("width", True), ("kind", "invented"), ("identity", "C"),
                             ("category_id", "pose"), ("qa", None)):
            invalid = deepcopy(self.plan)
            invalid["jobs"][0][field] = value
            cases.append(invalid)
        for invalid in cases:
            with self.subTest(plan=invalid["jobs"][0]):
                self.plan = invalid
                with self.assertRaises(WebPackError):
                    self.load()

    def test_rejects_bad_results_hash_dimensions_path_qa_and_missing_file(self):
        for field, value in (("sha256", "0" * 64), ("width", 7), ("path", "../escape.png"),
                             ("qa", {"decision": "accepted", "reviewer": "", "observations": []}),
                             ("model", ""), ("prompt", "")):
            with self.subTest(field=field):
                self.results["results"] = []
                row = self.accept()
                row[field] = value
                with self.assertRaises(WebPackError):
                    self.load()
        self.results["results"] = []
        row = self.accept()
        (self.root / row["path"]).unlink()
        with self.assertRaises(WebPackError):
            self.load()

    def test_rejects_duplicate_unknown_and_invalid_result_status(self):
        row = self.accept()
        self.results["results"].append(deepcopy(row))
        with self.assertRaises(WebPackError):
            self.load()
        self.results["results"] = [{**row, "job_id": "unknown"}]
        with self.assertRaises(WebPackError):
            self.load()
        self.results["results"] = [{**row, "status": "success"}]
        with self.assertRaises(WebPackError):
            self.load()

    def test_rejects_corrupt_png_and_real_dimension_mismatch(self):
        for raw in (b"not PNG", png_fixture()[:-1], png_fixture(width=3)):
            with self.subTest(raw_size=len(raw)):
                self.results["results"] = []
                self.accept(raw=raw)
                with self.assertRaises(WebPackError):
                    self.load()

    def test_rejects_duplicate_image_content(self):
        self.accept()
        self.accept("hair-E00")
        with self.assertRaises(WebPackError):
            self.load()

    def test_references_require_real_accepted_matching_files(self):
        gaze = next(j for j in self.plan["jobs"] if j["domain"] == "gaze")
        gaze["reference_job_ids"] = ["expression-E00"]
        row = self.accept(gaze["id"], png_fixture(value=100))
        with self.assertRaises(WebPackError):
            self.load()
        reference = self.accept()
        with self.assertRaises(WebPackError):
            self.load()
        row["reference_paths"] = [reference["path"]]
        pack = self.load()
        result = apply_assets(seed_fixture(), pack)
        self.assertEqual(len(result["media_assets"]), 2)

    def test_explicit_geometry_and_recipient_roles_keep_primary_identity(self):
        reference = self.plan["jobs"][0]
        reference["identity"] = "B"
        creative = self.plan["jobs"][1]
        creative["reference_job_ids"] = [reference["id"], "expression-E00"]
        creative["reference_roles"] = {reference["id"]: "geometry", "expression-E00": "identity"}
        self.load()
        gesture = next(job for job in self.plan["jobs"] if job["domain"] == "gesture")
        gesture["reference_job_ids"] = [reference["id"], "expression-E00"]
        gesture["reference_roles"] = {reference["id"]: "recipient_identity",
                                      "expression-E00": "identity"}
        self.load()
        creative["reference_roles"][reference["id"]] = "identity"
        with self.assertRaises(WebPackError):
            self.load()
        creative["reference_roles"][reference["id"]] = "geometry"
        creative["reference_job_ids"] = [reference["id"]]
        creative["reference_roles"] = {reference["id"]: "geometry"}
        with self.assertRaises(WebPackError):
            self.load()

    def test_composition_control_requires_real_bound_file_and_recorded_input(self):
        job = next(j for j in self.plan["jobs"] if j["id"] == "expression-E00")
        relative = "public/generated/frame-assets/controls/layout.png"
        raw = png_fixture(value=111)
        job["control_images"] = [{"path": relative, "sha256": hashlib.sha256(raw).hexdigest()}]
        with self.assertRaises(WebPackError):
            self.load()
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        self.load()
        row = self.accept()
        with self.assertRaises(WebPackError):
            self.load()
        row["reference_paths"] = [relative]
        self.load()
        job["control_images"][0]["role"] = "edit_base"
        self.load()
        job["control_images"][0]["role"] = "unverified_identity"
        with self.assertRaises(WebPackError):
            self.load()
        job["control_images"][0]["role"] = "composition"
        path.write_bytes(png_fixture(value=112))
        with self.assertRaises(WebPackError):
            self.load()

    def test_rejects_missing_parents_category_coverage_and_reserved_collisions(self):
        pack = self.load()
        seed = seed_fixture()
        pack.plan["jobs"][1]["parent_entry_ids"] = ["unknown"]
        with self.assertRaises(WebPackError):
            apply_assets(seed, pack)
        pack.plan["jobs"][1]["parent_entry_ids"] = ["original"]
        seed["categories"].pop()
        with self.assertRaises(WebPackError):
            apply_assets(seed, pack)
        seed = seed_fixture()
        seed["entries"][0]["details"] = canonical({"usage_guide": {"wrong": True}})
        with self.assertRaises(WebPackError):
            apply_assets(seed, pack)
        seed = seed_fixture()
        seed["prompt_templates"].append({**seed["prompt_templates"][0], "id": "asset-application-original"})
        with self.assertRaises(WebPackError):
            apply_assets(seed, pack)

    def test_revision_changes_with_plan_guides_and_actual_results(self):
        pack = self.load()
        first = asset_revision(pack)["dataset_revision"]
        changed_plan = deepcopy(pack.plan)
        changed_plan["jobs"][0]["direction"] += " Changed fixture."
        changed_guides = deepcopy(pack.guides)
        changed_guides["categories"]["hair"]["avoid"].append("Another fixture check.")
        for changed in (replace(pack, plan=changed_plan), replace(pack, guides=changed_guides)):
            self.assertNotEqual(asset_revision(changed)["dataset_revision"], first)
        self.accept()
        self.assertNotEqual(asset_revision(self.load())["dataset_revision"], first)

    def test_revision_changes_with_transformer_implementation(self):
        pack = self.load()
        source = self.root / "transformer.py"
        source.write_bytes(b"first implementation")
        with patch("asset_pack.__file__", str(source)):
            first = asset_revision(pack)["dataset_revision"]
            source.write_bytes(b"second implementation")
            self.assertNotEqual(first, asset_revision(pack)["dataset_revision"])

    def test_rows_load_into_existing_sqlite_schema(self):
        self.accept()
        result = apply_assets(seed_fixture(), self.load())
        with sqlite3.connect(":memory:") as db:
            db.execute("PRAGMA foreign_keys=ON")
            db.executescript((ROOT / "drizzle/0000_yielding_shadowcat.sql").read_text())
            mapping = {"entries": "reference_entries", "variants": "entry_variants"}
            for key in ("categories", "sources", "entries", "variants", "media_assets",
                        "prompt_templates", "entry_relations", "import_batches"):
                rows = result[key]
                if not rows:
                    continue
                columns = ["group_name" if name == "group" else name for name in rows[0]]
                db.executemany("INSERT INTO " + mapping.get(key, key) + " (" + ",".join(columns)
                               + ") VALUES (" + ",".join("?" for _ in columns) + ")",
                               [[row[column] for column in rows[0]] for row in rows])
            self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(), [])
            self.assertEqual(db.execute("SELECT COUNT(*) FROM media_assets").fetchone()[0], 1)


if __name__ == "__main__":
    unittest.main()
