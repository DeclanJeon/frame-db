"""Reviewed creative proposals only; never facts, media, or new entries."""
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from web_pack import (Approved, Document, canonical, concept_key, parse,
                      read_json, require, sha256, validate_review)

DETAIL_KEY: Final = "creative_metadata"
SCOPE: Final = "Creative proposals; not verified web facts/media."


@dataclass(frozen=True, slots=True)
class Creative:
    supplement: Document
    review: Document
    overlays: dict[str, Document]


def _strings(value: list[str], label: str) -> None:
    require(type(value) is list and bool(value)
            and all(type(item) is str and bool(item.strip()) for item in value),
            f"{label} must be a nonempty string list")
    require(len(value) == len(set(value)), f"duplicate {label}")


def validate_creative(raw: bytes, review: Document, approved: list[Approved]) -> Creative:
    """Bind exact supplement bytes, full decisions, and current accepted source concepts."""
    supplement = parse(raw)
    require(supplement.get("schema_version") == 1 and supplement.get("kind") == "proposal",
            "invalid creative supplement")
    for field in ("authorship", "scope", "basis_policy"):
        require(type(supplement.get(field)) is str and bool(supplement[field].strip()),
                f"missing creative {field}")
    require(review.get("schema_version") == 1
            and review.get("kind") == "independent_creative_metadata_review"
            and review.get("status") in {"reviewed", "reviewed_with_rejections"},
            "invalid creative review")
    require(review.get("input_sha256") == sha256(raw), "stale creative input SHA")
    require(type(review.get("reviewer")) is str and bool(review["reviewer"].strip()),
            "missing independent creative reviewer")
    records = supplement.get("records")
    require(type(records) is list, "creative records must be a list")
    targets = {}
    for record in records:
        require(type(record) is dict
                and set(record) == {"entry_id", "category_id", "basis", "directions"},
                "invalid creative record fields")
        for field in ("entry_id", "category_id"):
            require(type(record[field]) is str and bool(record[field].strip()),
                    f"invalid creative {field}")
        require(record["entry_id"] not in targets, "duplicate creative target ID")
        _strings(record["basis"], "basis")
        _strings(record["directions"], "directions")
        targets[record["entry_id"]] = record
    partitions = []
    for field in ("accepted_entry_ids", "rejected_entry_ids"):
        values = review.get(field)
        require(type(values) is list and all(type(value) is str for value in values),
                f"invalid {field}")
        require(len(values) == len(set(values)), f"duplicate {field}")
        partitions.append(set(values))
    accepted, rejected = partitions
    require(not accepted & rejected and accepted | rejected == set(targets),
            "creative review must fully partition targets without overlap")
    decisions = review.get("decisions")
    require(type(decisions) is list, "creative review decisions must be a list")
    by_target = {}
    for decision in decisions:
        require(type(decision) is dict and type(decision.get("entry_id")) is str,
                "invalid creative decision")
        target = decision["entry_id"]
        require(target in targets and target not in by_target, "unknown or duplicate decision target")
        require(decision.get("category_id") == targets[target]["category_id"]
                and decision.get("basis") == targets[target]["basis"],
                "decision category or basis mismatch")
        require(decision.get("decision") == ("accepted" if target in accepted else "rejected"),
                "decision partition mismatch")
        require(type(decision.get("reason")) is str and bool(decision["reason"].strip()),
                "missing per-target review reason")
        by_target[target] = decision
    require(set(by_target) == set(targets), "incomplete creative decisions")
    basis = {}
    for item in approved:
        validate_review(item.staging, item.review)
        batch = item.batch
        keys = {concept_key(key) for key in item.review["accepted_concept_keys"]}
        sources = {source["source_id"]: source for source in batch["sources"]}
        for record in batch["records"]:
            key = concept_key(record["concept_key"])
            if key not in keys:
                continue
            reference = batch["category_id"] + "/" + key
            require(reference not in basis, "duplicate approved basis concept")
            source_ids = sorted({fact["evidence"]["source_id"]
                                 for fact in record["facts"] + record["proposals"]})
            basis[reference] = {
                "concept_key": key, "category_id": batch["category_id"],
                "input_sha256": sha256(item.staging),
                "sources": [{"source_id": sid, "url": sources[sid]["url"]} for sid in source_ids],
            }
    overlays = {}
    for target, record in targets.items():
        require(all(reference in basis for reference in record["basis"]),
                "invalid or unapproved creative basis")
        if target in accepted:
            overlays[target] = {
                "kind": "proposal", "authorship": supplement["authorship"], "scope": SCOPE,
                "supplement_scope": supplement["scope"], "basis_policy": supplement["basis_policy"],
                "directions": record["directions"],
                "basis": [{"key": reference, **basis[reference]} for reference in record["basis"]],
                "input_sha256": sha256(raw), "reviewer": review["reviewer"],
                "review": by_target[target],
            }
    return Creative(deepcopy(supplement), deepcopy(review), deepcopy(overlays))


def load_creative(directory: Path, approved: list[Approved]) -> Creative:
    """Missing review is an error, never implicit approval."""
    return validate_creative((directory / "creative-supplement.json").read_bytes(),
                             read_json(directory / "creative-supplement-review.json"), approved)


def creative_revision(creative: Creative) -> Document:
    """Version creative content separately without changing web revision machinery."""
    return {
        "schema_version": 1,
        "dataset_revision": "creative-" + sha256(canonical(creative.overlays).encode()),
        "input_sha256": creative.review["input_sha256"],
        "accepted_entry_ids": sorted(creative.review["accepted_entry_ids"]),
        "rejected_entry_ids": sorted(creative.review["rejected_entry_ids"]),
        "applied_count": len(creative.overlays),
    }


def apply_creative(seed: Document, creative: Creative) -> Document:
    """Preserve every value except this reviewed nested metadata on accepted targets."""
    entries = {entry["id"]: entry for entry in seed["entries"]}
    require(len(entries) == len(seed["entries"]), "duplicate seed entry ID")
    for record in creative.supplement["records"]:
        target = entries.get(record["entry_id"])
        require(target is not None and target["category_id"] == record["category_id"],
                "creative target missing or wrong category")
    result = deepcopy(seed)
    for entry in result["entries"]:
        overlay = creative.overlays.get(entry["id"])
        if overlay is None:
            continue
        details = parse(entry["details"].encode())
        require(DETAIL_KEY not in details or details[DETAIL_KEY] == overlay,
                "creative metadata collision")
        details[DETAIL_KEY] = deepcopy(overlay)
        entry["details"] = canonical(details)
    return result
