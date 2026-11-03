"""Offline authored production overlay; only verified, accepted PNGs become media."""
from collections import Counter, defaultdict
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
import re
import struct
from typing import Final
import zlib

from web_pack import Document, WebPackError, canonical, parse, read_json, require, sha256

PACK_ID: Final = "frame-assets-20261030-v1"
SOURCE_ID: Final = "frame-generated"
COUNTS: Final = {"hair": 44, "makeup": 34, "expression": 37, "gaze": 8, "gesture": 24}
GUIDE_LISTS: Final = ("apply", "preserve", "change", "avoid", "check", "limitations")
STAMP: Final = "2026-10-30"


@dataclass(frozen=True, slots=True)
class AssetPack:
    plan: Document
    guides: Document
    results: Document
    root: Path


def _text(value: str, label: str) -> None:
    require(type(value) is str and bool(value.strip()), f"missing {label}")


def _strings(value: list[str], label: str) -> None:
    require(type(value) is list and all(type(v) is str and bool(v.strip()) for v in value),
            f"invalid {label}")
    require(len(value) == len(set(value)), f"duplicate {label}")


def generation_parameters(job: Document) -> Document:
    """Requested parameters; actual tool/model identifiers belong to accepted results."""
    return {"width": job["width"], "height": job["height"], "format": "png"}


def build_generation_prompt(job: Document) -> str:
    """Return the complete resolved text to submit, not a reusable placeholder."""
    return "\n".join([
        f"FRAME authored synthetic reference. Job: {job['id']}; concept: {job['title']}.",
        f"Class: {job['kind']}; domain: {job['domain']}; entry: {job['entry_id']}.",
        "Parent entry IDs: " + canonical(job["parent_entry_ids"]),
        f"One fictional adult subject, identity {job['identity']}. No web photograph identity inputs.",
        "Use actual accepted reference files for these jobs: " + canonical(job["reference_job_ids"]),
        "Reference roles: " + canonical(job.get("reference_roles", {
            reference: "identity" for reference in job["reference_job_ids"]})),
        *(["Auxiliary image inputs with explicit roles (not accepted output jobs): " +
           canonical(job["control_images"])] if job.get("control_images") else []),
        f"Observable direction: {job['direction']}",
        f"Camera / visible region: {job['view']}. Keep every defining feature inside the frame.",
        "Neutral background, controlled soft neutral lighting, detailed diagnostic photograph.",
        "Preserve: " + "; ".join(job["preserve"]),
        "Change only: " + "; ".join(job["change"]),
        "No collage, labels, watermark, packaging substitution, mirrored duplicate or invented motion.",
        "A still does not verify timing, physical measurements, emotion or unseen geometry.",
        "Acceptance checks (not yet performed): " + "; ".join(job["qa"]),
        "Output: " + canonical(generation_parameters(job)),
    ])


def build_usage_guide(entry: Document, playbook: Document,
                      jobs: list[Document] | None = None,
                      accepted_job_ids: list[str] | None = None) -> Document:
    """Combine the category playbook with this entry's own authored target and limits."""
    jobs = jobs or []
    accepted_job_ids = accepted_job_ids or []
    target = {"pose": "포즈를", "costume": "의상을", "hair": "헤어스타일을",
              "makeup": "메이크업을", "expression": "표정과 시선을",
              "gesture": "손동작을"}.get(entry["category_id"], "특징을")
    return {
        "kind": "authored_guide",
        "purpose": entry["title"] + " — " + playbook["purpose"],
        "apply": [f"이 자료의 {target} 그대로 참조해 적용하세요.",
                  f"유지할 부분: {playbook['preserve'][0]}"],
        "preserve": list(dict.fromkeys(playbook["preserve"] + [v for j in jobs for v in j["preserve"]])),
        "change": list(dict.fromkeys(playbook["change"] + [v for j in jobs for v in j["change"]])),
        "avoid": deepcopy(playbook["avoid"]),
        "check": list(dict.fromkeys(playbook["check"] + [v for j in jobs for v in j["qa"]])),
        "limitations": [*playbook["limitations"],
                         "Authored guidance, not a verified observation or completed QA.",
                         "Accepted synthetic still jobs: " + canonical(accepted_job_ids)
                         if accepted_job_ids else
                         "No accepted generated image for this entry; existing assets retain their own provenance.",
                         "A still/text guide cannot establish audio, temporal motion or unseen geometry."],
    }


def _png_dimensions(raw: bytes) -> tuple[int, int]:
    """Validate PNG structure/CRCs and a decodable scanline stream using only stdlib."""
    require(raw[:8] == b"\x89PNG\r\n\x1a\n", "not a PNG")
    offset = 8
    chunks = []
    compressed = bytearray()
    dimensions = None
    while offset < len(raw):
        require(offset + 12 <= len(raw), "truncated PNG")
        size = struct.unpack(">I", raw[offset:offset + 4])[0]
        kind = raw[offset + 4:offset + 8]
        end = offset + 8 + size
        require(end + 4 <= len(raw), "truncated PNG chunk")
        payload = raw[offset + 8:end]
        require(zlib.crc32(kind + payload) & 0xffffffff == struct.unpack(">I", raw[end:end + 4])[0],
                "PNG CRC mismatch")
        if not chunks:
            require(kind == b"IHDR" and size == 13, "invalid PNG header")
            width, height, depth, color, compression, filtering, interlace = struct.unpack(">IIBBBBB", payload)
            require(width > 0 and height > 0 and depth == 8 and color in {0, 2, 4, 6}
                    and compression == filtering == interlace == 0, "unsupported PNG encoding")
            dimensions = (width, height)
            channels = {0: 1, 2: 3, 4: 2, 6: 4}[color]
        if kind == b"IDAT":
            compressed.extend(payload)
        chunks.append(kind)
        offset = end + 4
        if kind == b"IEND":
            require(size == 0 and offset == len(raw), "invalid PNG end")
            break
    require(dimensions is not None and chunks[-1] == b"IEND" and bool(compressed), "incomplete PNG")
    try:
        decoder = zlib.decompressobj()
        stride = dimensions[0] * channels + 1
        expected = dimensions[1] * stride
        pixels = decoder.decompress(compressed, expected + 1)
    except zlib.error as error:
        raise WebPackError("invalid PNG pixels") from error
    require(len(pixels) == expected and decoder.eof and not decoder.unused_data
            and not decoder.unconsumed_tail, "invalid PNG scanline length")
    require(all(pixels[i] <= 4 for i in range(0, expected, stride)), "invalid PNG scanline filter")
    return dimensions


def load_asset_pack(directory: Path) -> AssetPack:
    """Require all three explicit inputs; a missing results file is never implicit acceptance."""
    plan = read_json(directory / "plan.json")
    guides = read_json(directory / "category-guides.json")
    results = read_json(directory / "results.json")
    require(plan.get("schema_version") == 1 and plan.get("id") == PACK_ID, "invalid production plan")
    jobs = plan.get("jobs")
    require(type(jobs) is list and all(type(j) is dict for j in jobs), "invalid production jobs")
    require(Counter(j.get("domain") for j in jobs) == COUNTS, "invalid production domain counts")
    by_id = {}
    for job in jobs:
        for field in ("id", "domain", "category_id", "entry_id", "title", "view", "direction"):
            _text(job.get(field), field)
        require(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", job["id"]) is not None, "invalid job ID")
        require(job["id"] not in by_id, "duplicate job ID")
        require(job.get("kind") in {"base", "creative"} and job.get("identity") in {"A", "B"},
                "invalid production kind or identity")
        require(job["category_id"] == ("expression" if job["domain"] == "gaze" else job["domain"]),
                "domain/category mismatch")
        for field in ("parent_entry_ids", "preserve", "change", "qa", "reference_job_ids"):
            _strings(job.get(field), field)
        controls = job.get("control_images", [])
        require(type(controls) is list and all(type(control) is dict for control in controls),
                "invalid composition controls")
        _strings([control.get("path") for control in controls], "composition control paths")
        for control in controls:
            _text(control.get("sha256"), "composition control hash")
            require(control.get("role", "composition") in {"composition", "edit_base"},
                    "invalid auxiliary image role")
        roles = job.get("reference_roles")
        if roles is not None:
            require(type(roles) is dict and set(roles) == set(job["reference_job_ids"])
                    and all(role in {"identity", "geometry", "recipient_identity"}
                            for role in roles.values()), "invalid reference roles")
            require("geometry" not in roles.values() or job["kind"] == "creative",
                    "geometry role requires a creative job")
            require("recipient_identity" not in roles.values() or job["domain"] == "gesture",
                    "recipient identity requires a gesture job")
        require(job["kind"] != "creative" or bool(job["parent_entry_ids"]), "creative job needs parents")
        require(all(type(job.get(k)) is int and 0 < job[k] <= 8192 for k in ("width", "height")),
                "invalid output dimensions")
        by_id[job["id"]] = job
    require(plan.get("slot_aliases") == [{"id": "gaze-center", "job_id": "expression-E00"}]
            and "expression-E00" in by_id, "invalid neutral gaze alias")
    visited = set()
    active = set()

    def visit(job_id: str) -> None:
        require(job_id in by_id, "unknown reference job")
        require(job_id not in active, "cyclic reference jobs")
        if job_id in visited:
            return
        active.add(job_id)
        for reference in by_id[job_id]["reference_job_ids"]:
            role = by_id[job_id].get("reference_roles", {}).get(reference, "identity")
            if role == "identity":
                require(by_id.get(reference, {}).get("identity") == by_id[job_id]["identity"],
                        "reference identity mismatch")
            visit(reference)
        roles = by_id[job_id].get("reference_roles", {})
        if any(role != "identity" for role in roles.values()):
            require(any(roles.get(reference, "identity") == "identity"
                        and by_id[reference]["identity"] == by_id[job_id]["identity"]
                        for reference in by_id[job_id]["reference_job_ids"]),
                    "secondary reference needs a primary identity reference")
        active.remove(job_id)
        visited.add(job_id)

    for job_id in by_id:
        visit(job_id)
    require(guides.get("schema_version") == 1 and type(guides.get("categories")) is dict
            and len(guides["categories"]) == 29, "invalid category guides")
    for guide in guides["categories"].values():
        require(type(guide) is dict, "invalid category guide")
        _text(guide.get("purpose"), "guide purpose")
        for field in GUIDE_LISTS:
            _strings(guide.get(field), "guide " + field)
    require(results.get("schema_version") == 1 and type(results.get("results")) is list,
            "invalid production results")
    root = directory.resolve().parents[1]
    for job in jobs:
        for control in job.get("control_images", []):
            path = (root / control["path"]).resolve()
            require(path.is_relative_to(root / "public/generated/frame-assets/controls")
                    and path.is_file(), "missing or escaped composition control")
            raw = path.read_bytes()
            require(sha256(raw) == control["sha256"], "composition control hash mismatch")
            _png_dimensions(raw)
    seen = {}
    paths = set()
    hashes = set()
    for row in results["results"]:
        require(type(row) is dict and row.get("job_id") in by_id, "unknown result job")
        jid = row["job_id"]
        require(jid not in seen, "duplicate result job")
        require(row.get("status") in {"accepted", "pending", "failed", "rejected"}, "invalid result status")
        if "prompt" in row:
            _text(row["prompt"], "actual submitted prompt")
        seen[jid] = row
        if row["status"] != "accepted":
            continue
        job = by_id[jid]
        expected_path = f"public/generated/frame-assets/{jid}.png"
        require(row.get("path") == expected_path, "invalid generated asset path")
        path = (root / expected_path).resolve()
        require(path.is_relative_to(root / "public/generated/frame-assets")
                and path.is_file(), "missing or escaped generated file")
        raw = path.read_bytes()
        require(row.get("sha256") == sha256(raw), "generated hash mismatch")
        require((row.get("width"), row.get("height")) == (job["width"], job["height"])
                == _png_dimensions(raw), "generated dimension mismatch")
        _text(row.get("prompt"), "actual submitted prompt")
        for field in ("tool", "model"):
            _text(row.get(field), field)
        qa = row.get("qa")
        require(type(qa) is dict and qa.get("decision") == "accepted", "missing accepted visual QA")
        _text(qa.get("reviewer"), "QA reviewer")
        _strings(qa.get("observations"), "QA observations")
        _strings(row.get("reference_paths"), "reference paths")
        require(expected_path not in paths and row["sha256"] not in hashes, "duplicate generated file")
        paths.add(expected_path)
        hashes.add(row["sha256"])
    for jid, row in seen.items():
        if row["status"] != "accepted":
            continue
        references = by_id[jid]["reference_job_ids"]
        require(all(seen.get(ref, {}).get("status") == "accepted" for ref in references),
                "missing accepted reference job")
        require(row["reference_paths"] == [seen[ref]["path"] for ref in references] +
                [control["path"] for control in by_id[jid].get("control_images", [])],
                "reference paths do not match accepted jobs")
    return AssetPack(plan, guides, results, root)


def asset_revision(pack: AssetPack) -> Document:
    """Hash all authored inputs/results and prompt recipe, including pending production."""
    payload = {"plan": pack.plan, "guides": pack.guides, "results": pack.results,
               "transformer_sha256": sha256(Path(__file__).read_bytes()),
               "prompts": [{"job_id": j["id"], "text": build_generation_prompt(j),
                            "parameters": generation_parameters(j)} for j in pack.plan["jobs"]]}
    accepted = sorted(r["job_id"] for r in pack.results["results"] if r["status"] == "accepted")
    statuses = {r["job_id"]: r["status"] for r in pack.results["results"]}
    return {"schema_version": 1, "id": pack.plan["id"],
            "dataset_revision": "assets-" + sha256(canonical(payload).encode()),
            "planned_count": len(pack.plan["jobs"]), "accepted_count": len(accepted),
            "accepted_job_ids": accepted,
            "pending_job_ids": sorted(j["id"] for j in pack.plan["jobs"]
                                      if statuses.get(j["id"], "pending") == "pending"),
            "failed_job_ids": sorted(jid for jid, status in statuses.items() if status == "failed"),
            "rejected_job_ids": sorted(jid for jid, status in statuses.items() if status == "rejected"),
            "slot_aliases": deepcopy(pack.plan["slot_aliases"])}


def _add(rows: list[Document], row: Document) -> None:
    matches = [current for current in rows if current["id"] == row["id"]]
    require(not matches or matches == [row], f"asset row ID collision: {row['id']}")
    if not matches:
        rows.append(row)


def apply_assets(seed: Document, pack: AssetPack) -> Document:
    """Copy the seed, preserving originals and adding deterministic guides/prompts/media."""
    result = deepcopy(seed)
    entries = {entry["id"]: entry for entry in result["entries"]}
    require(len(entries) == len(result["entries"]), "duplicate seed entries")
    require(set(pack.guides["categories"]) == {c["id"] for c in seed["categories"]},
            "category guide coverage mismatch")
    _add(result["sources"], {"id": SOURCE_ID, "name": "FRAME authored synthetic references",
                            "url": None, "license": "Synthetic authored production; not source photography.",
                            "hosting": "local_generated", "checked": STAMP})
    jobs_by_entry = defaultdict(list)
    results = {row["job_id"]: row for row in pack.results["results"]}
    for job in sorted(pack.plan["jobs"], key=lambda j: j["id"]):
        eid = job["entry_id"]
        jobs_by_entry[eid].append(job)
        if eid not in entries:
            entries[eid] = {"id": eid, "category_id": job["category_id"], "source_id": SOURCE_ID,
                            "title": job["title"], "original_title": "", "description": job["change"][0],
                            "gender": "공용", "subtype": job["domain"], "status": "guide",
                            "search_text": " ".join([eid, job["title"], job["direction"]]).lower(),
                            "details": "{}", "version": 1, "updated": STAMP}
            result["entries"].append(entries[eid])
        require(entries[eid]["category_id"] == job["category_id"], "planned entry category mismatch")
    for job in pack.plan["jobs"]:
        for parent in job["parent_entry_ids"]:
            require(parent in entries and parent != job["entry_id"], "missing or self parent entry")
            relation_id = "asset-parent-" + sha256(canonical([job["entry_id"], parent]).encode())[:24]
            _add(result["entry_relations"],
                 {"id": relation_id, "from_id": job["entry_id"], "to_id": parent,
                  "type": "derived_from", "reason": "Authored production parent/basis; not measured similarity."})
    for entry in result["entries"]:
        jobs = jobs_by_entry[entry["id"]]
        accepted = [job["id"] for job in jobs if results.get(job["id"], {}).get("status") == "accepted"]
        guide = build_usage_guide(entry, pack.guides["categories"][entry["category_id"]], jobs, accepted)
        details = parse(entry["details"].encode())
        require("usage_guide" not in details or details["usage_guide"] == guide, "usage guide collision")
        details["usage_guide"] = guide
        if jobs:
            production = {
                "kind": "authored_production", "plan_id": pack.plan["id"],
                "parent_entry_ids": sorted({p for job in jobs for p in job["parent_entry_ids"]}),
                "jobs": [{**deepcopy(job), "status": results.get(job["id"], {}).get("status", "pending"),
                          "prompt": results.get(job["id"], {}).get("prompt", build_generation_prompt(job)),
                          "requested_prompt": build_generation_prompt(job),
                          "submitted": "prompt" in results.get(job["id"], {}),
                          "parameters": generation_parameters(job),
                          "result": deepcopy(results.get(job["id"]))} for job in jobs],
                "slot_aliases": [a for a in pack.plan["slot_aliases"]
                                 if a["job_id"] in {j["id"] for j in jobs}],
            }
            require("asset_production" not in details or details["asset_production"] == production,
                    "asset production collision")
            details["asset_production"] = production
        entry["details"] = canonical(details)
        application = {"kind": "reference_application", "reference_id": entry["id"],
                       "intended_output": "Apply the selected reference to your own character/scene.",
                       "target_direction": entry["title"] + ": " + entry["description"],
                       "controls": guide["purpose"], "preserve": guide["preserve"],
                       "change": guide["change"], "exclusions": guide["avoid"],
                       "qa": guide["check"],
                       "identity_policy": "Preserve the supplied character identity; do not transplant reference identity."}
        _add(result["prompt_templates"],
             {"id": "asset-application-" + entry["id"], "entry_id": entry["id"],
              "text": canonical(application), "language": "mixed",
              "authorship": "FRAME authored reference application", "parameters": canonical(application)})
        for job in jobs:
            parameters = {"kind": "image_generation", "job_id": job["id"],
                          "status": results.get(job["id"], {}).get("status", "pending"),
                          "submitted": "prompt" in results.get(job["id"], {}),
                          **generation_parameters(job)}
            _add(result["prompt_templates"],
                 {"id": "asset-generation-" + job["id"], "entry_id": entry["id"],
                  "text": results.get(job["id"], {}).get("prompt", build_generation_prompt(job)),
                  "language": "mixed",
                  "authorship": "FRAME authored image generation", "parameters": canonical(parameters)})
            row = results.get(job["id"])
            if row is None or row["status"] != "accepted":
                continue
            vid = "asset-variant-" + job["id"]
            _add(result["variants"], {"id": vid, "entry_id": entry["id"], "label": job["title"],
                                     "angle": job["view"], "attributes": canonical({
                                         "kind": "synthetic_generated", "job_id": job["id"],
                                         "parameters": generation_parameters(job), **row})})
            _add(result["media_assets"],
                 {"id": "asset-media-" + job["id"], "entry_id": entry["id"], "variant_id": vid,
                  "kind": "image", "url": "/" + row["path"].removeprefix("public/"),
                  "availability": "generated_image", "source_id": SOURCE_ID, "original_id": job["id"]})
    revision = asset_revision(pack)
    _add(result["import_batches"],
         {"id": "asset-import-" + pack.plan["id"], "source_id": SOURCE_ID,
          "expected": len(pack.plan["jobs"]), "indexed": revision["accepted_count"],
          "groups": len(jobs_by_entry), "status": "accepted" if revision["accepted_count"] == 147 else "pending",
          "report": canonical(revision), "checked": STAMP})
    return result


if __name__ == "__main__":
    import sys

    requested = sys.argv[1:]
    require(bool(requested) and len(requested) == len(set(requested)),
            "provide unique production job IDs")
    directory = Path(__file__).resolve().parents[2] / "data/asset-production"
    plan = read_json(directory / "plan.json")
    selected = {job["id"]: job for job in plan["jobs"] if job["id"] in requested}
    require(set(selected) == set(requested), "unknown requested production job")
    print(canonical([{"job": selected[jid],
                      "prompt": build_generation_prompt(selected[jid]),
                      "parameters": generation_parameters(selected[jid])}
                     for jid in requested]))
