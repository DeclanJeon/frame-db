"""Offline web metadata boundary. Never fetch media or mutate the input seed."""
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
from typing import Final, TypeAlias
import unicodedata
from urllib.parse import urlsplit

JSON: TypeAlias = str | int | float | bool | None | list["JSON"] | dict[str, "JSON"]
Document: TypeAlias = dict[str, JSON]
ROOT: Final = Path(__file__).resolve().parents[2]
SCHEMA: Final = ROOT / "data/web-research/schema.json"
SPEC: Final = ROOT / "data/web-population-spec.json"


class WebPackError(ValueError):
    """A file or metadata contract was not satisfied."""

    def __init__(self, issue: str) -> None:
        self.issue = issue
        super().__init__(issue)


def require(condition: bool, issue: str) -> None:
    if not condition:
        raise WebPackError(issue)


def canonical(value: JSON) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _pairs(pairs: list[tuple[str, JSON]]) -> Document:
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON property: {key}")
        result[key] = value
    return result


def _constant(value: str) -> None:
    raise WebPackError(f"non-finite JSON number: {value}")


def parse(raw: bytes) -> Document:
    value = json.loads(raw, object_pairs_hook=_pairs, parse_constant=_constant)
    require(type(value) is dict, "document must be an object")
    return value


def read_json(path: Path) -> Document:
    return parse(path.read_bytes())


def concept_key(value: str) -> str:
    """NFKC, case folding and equivalent whitespace/underscore/hyphen spelling."""
    return re.sub(r"[\s_-]+", "-", unicodedata.normalize("NFKC", value).casefold()).strip("-")


def _url(value: str) -> None:
    parts = urlsplit(value)
    require(parts.scheme in {"https", "http"} and bool(parts.hostname)
            and not parts.username and not parts.password, "expected public HTTP(S) URL")
    host = parts.hostname.lower().rstrip(".")
    require(not (host == "mocap.cs.cmu.edu" or host.endswith(".mocap.cs.cmu.edu")
                 or host == "kitchen.cs.cmu.edu" or host.endswith(".kitchen.cs.cmu.edu")),
            "no-crawl CMU source is excluded from automated batches")


def _shape(value: JSON, rule: Document, definitions: Document, path: str) -> None:
    """Validate the exact JSON Schema vocabulary used by the shipped contract."""
    if "$ref" in rule:
        return _shape(value, definitions[rule["$ref"].rsplit("/", 1)[1]], definitions, path)
    types = rule.get("type", [])
    types = [types] if type(types) is str else types
    names = {dict: "object", list: "array", str: "string", int: "integer",
             float: "number", bool: "boolean", type(None): "null"}
    require(not types or names[type(value)] in types, f"{path}: wrong type")
    if "const" in rule:
        require(type(value) is type(rule["const"]) and value == rule["const"], f"{path}: wrong constant")
    if "enum" in rule:
        require(value in rule["enum"], f"{path}: invalid enum")
    if type(value) is dict:
        require(set(rule.get("required", [])) <= value.keys(), f"{path}: missing required fields")
        properties = rule.get("properties", {})
        if rule.get("additionalProperties") is False:
            require(value.keys() <= properties.keys(), f"{path}: unknown fields")
        for key in value.keys() & properties.keys():
            _shape(value[key], properties[key], definitions, f"{path}.{key}")
    if type(value) is list:
        require(len(value) >= rule.get("minItems", 0) and len(value) <= rule.get("maxItems", 100000),
                f"{path}: invalid item count")
        if rule.get("uniqueItems"):
            require(len({canonical(x) for x in value}) == len(value), f"{path}: duplicate items")
        for index, item in enumerate(value):
            _shape(item, rule["items"], definitions, f"{path}[{index}]")
    if type(value) is str:
        require(len(value.strip()) >= rule.get("minLength", 0)
                and len(value) <= rule.get("maxLength", 100000), f"{path}: invalid string length")
        if "pattern" in rule:
            require(re.search(rule["pattern"], value) is not None, f"{path}: invalid pattern")
        if rule.get("format") == "uri":
            _url(value)
        if rule.get("format") == "date-time":
            try:
                stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError as error:
                raise WebPackError(f"{path}: invalid timestamp") from error
            require(stamp.tzinfo is not None and "T" in value, f"{path}: timezone required")
    if type(value) is int:
        require(value >= rule.get("minimum", value) and value <= rule.get("maximum", value),
                f"{path}: invalid integer range")


def validate_shape(document: Document, kind: str) -> None:
    schema = read_json(SCHEMA)
    _shape(document, schema["$defs"][kind], schema["$defs"], kind)


def categories() -> set[str]:
    return {category["id"] for category in read_json(SPEC)["categories"]}


def validate_batch(batch: Document, category: str | None = None) -> Document:
    """Validate structure and source references, without claiming factual verification."""
    validate_shape(batch, "batch")
    require(batch["category_id"] in categories(), "unknown category")
    require(category is None or batch["category_id"] == category, "category/file mismatch")
    sources = {source["source_id"]: source for source in batch["sources"]}
    require(len(sources) == len(batch["sources"]), "duplicate source ID")
    require(len({source["url"] for source in sources.values()}) == len(sources), "duplicate source URL")
    for source in sources.values():
        rights = source["rights"]
        require(rights["status"] == "unknown" or rights["evidence_url"] is not None,
                "known rights require evidence URL")
    keys, titles, targets = set(), set(), set()
    for record in batch["records"]:
        key = concept_key(record["concept_key"])
        require(bool(key) and key not in keys, "duplicate or empty category/concept key")
        keys.add(key)
        title = concept_key(record["title_ko"])
        require(title not in titles, "duplicate concept title")
        titles.add(title)
        if record.get("existing_entry_id") is not None:
            require(record["existing_entry_id"] not in targets, "duplicate enrichment target")
            targets.add(record["existing_entry_id"])
        fields = [fact["field"] for fact in record["facts"]]
        require(len(set(fields)) == len(fields), "duplicate fact field")
        for fact in record["facts"] + record["proposals"]:
            evidence = fact["evidence"]
            require(evidence["source_id"] in sources, "unresolved evidence source")
            if fact in record["facts"]:
                require(evidence["kind"] != "proposal", "proposal cannot count as a fact")
            else:
                require(evidence["kind"] == "proposal", "proposal requires proposal evidence kind")
            if evidence["kind"] in {"observation", "measurement"}:
                require(all(evidence.get(k) for k in ("observer", "sample")), "observation requires observer/sample")
            if evidence["kind"] == "measurement":
                require(all(evidence.get(k) for k in ("method", "unit")), "measurement requires method/unit")
        proposal_fields = [fact["field"] for fact in record["proposals"]]
        require(len(set(fields + proposal_fields)) == len(fields + proposal_fields), "duplicate fact/proposal field")
        for candidate in record["media_candidates"]:
            require(candidate["source_id"] in sources, "unresolved media candidate source")
            require(candidate["rights_status"] == sources[candidate["source_id"]]["rights"]["status"],
                    "candidate/source rights mismatch")
    require(len(batch["records"]) == 20 or bool(batch["shortfall_reason"].strip()),
            "partial batch requires honest shortfall reason")
    return batch


@dataclass(frozen=True, slots=True)
class Approved:
    """Exact staging bytes and their independently authored review."""

    staging: bytes
    review: Document

    @property
    def batch(self) -> Document:
        return parse(self.staging)


def validate_review(raw: bytes, review: Document, category: str | None = None) -> Approved:
    batch = validate_batch(parse(raw), category)
    validate_shape(review, "review")
    require(review["category_id"] == batch["category_id"], "review category mismatch")
    require(review["input_sha256"] == sha256(raw), "review input SHA-256 mismatch")
    require(concept_key(review["reviewer"]) != concept_key(batch["collector"]),
            "review must be independent of collector")
    records = {concept_key(r["concept_key"]): r for r in batch["records"]}
    accepted = [concept_key(key) for key in review["accepted_concept_keys"]]
    rejected = [concept_key(item["concept_key"]) for item in review["rejected"]]
    require(len(set(accepted + rejected)) == len(accepted + rejected), "duplicate review decision")
    require(set(accepted + rejected) == records.keys(), "review decisions must cover exact batch keys")
    require(review["accepted_count"] == len(accepted) and review["shortfall"] == 20 - len(accepted),
            "review counts do not match actual decisions")
    require(not review["shortfall"] or bool(review["shortfall_reason"].strip()), "review shortfall reason required")
    sources = {source["source_id"]: source for source in batch["sources"]}
    checked = {}
    for check in review["source_checks"]:
        require(check["source_id"] in sources and check["source_id"] not in checked,
                "unknown or duplicate reviewed source")
        require(check["url"] == sources[check["source_id"]]["url"], "reviewed source URL mismatch")
        checked[check["source_id"]] = check
    required = {}
    for key in accepted:
        require(all(candidate["source_id"] in checked for candidate in records[key]["media_candidates"]),
                "accepted candidate lacks independent source/rights check")
        for fact in records[key]["facts"] + records[key]["proposals"]:
            evidence = fact["evidence"]
            required[(key, fact["field"])] = (evidence["source_id"], evidence["locator"])
            require(evidence["source_id"] in checked, "accepted evidence lacks independent source check")
    actual = {}
    for check in review["evidence_checks"]:
        key = (concept_key(check["concept_key"]), check["field"])
        require(key in required and key not in actual, "unknown or duplicate evidence check")
        actual[key] = (check["source_id"], check["locator"])
    require(actual == required, "review must independently check every accepted evidence locator")
    return Approved(raw, deepcopy(review))


def load_pair(directory: Path, category: str) -> Approved:
    require(category in categories(), "unknown category")
    return validate_review((directory / "staging" / f"{category}.json").read_bytes(),
                           read_json(directory / "reviews" / f"{category}.json"), category)


def _envelope(approved: Approved) -> Document:
    return {"staging_json": approved.staging.decode("utf-8"), "review": approved.review}


def _revision(payloads: dict[str, bytes]) -> Document:
    files = [{"category_id": key, "sha256": sha256(value)} for key, value in sorted(payloads.items())]
    content = []
    for category, payload in sorted(payloads.items()):
        envelope = parse(payload)
        require(set(envelope) == {"staging_json", "review"}
                and type(envelope["staging_json"]) is str, "invalid accepted envelope")
        batch = validate_review(envelope["staging_json"].encode(), envelope["review"], category).batch
        accepted = {concept_key(key) for key in envelope["review"]["accepted_concept_keys"]}
        records = sorted((record for record in batch["records"]
                          if concept_key(record["concept_key"]) in accepted),
                         key=lambda record: concept_key(record["concept_key"]))
        used = {fact["evidence"]["source_id"] for record in records
                for fact in record["facts"] + record["proposals"]}
        used.update(candidate["source_id"] for record in records for candidate in record["media_candidates"])
        if records:
            content.append({"category_id": category, "records": records,
                            "sources": sorted((source for source in batch["sources"] if source["source_id"] in used),
                                              key=lambda source: source["source_id"])})
    return {"schema_version": 1, "dataset_revision": "web-" + sha256(canonical(content).encode()),
            "files": files}


def stage_reviewed(directory: Path, selected: list[str]) -> Document:
    """Preflight the entire union, then write accepted files and revision last."""
    require(bool(selected) and len(set(selected)) == len(selected), "empty or duplicate category selection")
    previous = {path.stem for path in (directory / "accepted").glob("*.json")}
    approved = {key: load_pair(directory, key) for key in sorted(previous | set(selected))}
    payloads = {key: (canonical(_envelope(value)) + "\n").encode() for key, value in approved.items()}
    revision = _revision(payloads)
    (directory / "accepted").mkdir(parents=True, exist_ok=True)
    for key, payload in payloads.items():
        (directory / "accepted" / f"{key}.json").write_bytes(payload)
    (directory / "revision.json").write_text(canonical(revision) + "\n", encoding="utf-8")
    return revision


def load_approved(directory: Path) -> list[Approved]:
    """Verify revision and current inputs; stale or interrupted staging fails closed."""
    revision = read_json(directory / "revision.json")
    payloads = {path.stem: path.read_bytes() for path in (directory / "accepted").glob("*.json")}
    require(bool(payloads) and revision == _revision(payloads), "accepted revision mismatch")
    result = []
    for key, payload in sorted(payloads.items()):
        envelope = parse(payload)
        require(set(envelope) == {"staging_json", "review"}, "invalid accepted envelope")
        current = load_pair(directory, key)
        require(envelope == _envelope(current), "accepted snapshot is stale")
        result.append(current)
    return result


def apply_web(seed: Document, approved: list[Approved]) -> Document:
    """Return a deterministic metadata-only seed copy; existing identity is immutable."""
    for item in approved:
        validate_review(item.staging, item.review)
    ordered = sorted(approved, key=lambda item: item.batch["category_id"])
    require(len({item.batch["category_id"] for item in ordered}) == len(ordered), "duplicate category batch")
    result = deepcopy(seed)
    entries = {entry["id"]: entry for entry in result["entries"]}
    require(len(entries) == len(result["entries"]), "duplicate seed entry ID")
    source_rows = {source["id"]: source for source in result["sources"]}
    import_rows = {row["id"]: row for row in result["import_batches"]}
    for item in ordered:
        batch = item.batch
        category = batch["category_id"]
        require(category in {c["id"] for c in result["categories"]}, "category absent from seed")
        accepted = {concept_key(key) for key in item.review["accepted_concept_keys"]}
        sources = {source["source_id"]: source for source in batch["sources"]}
        used_targets = set()
        batch_sources = set()
        added = enriched = fact_count = 0
        for record in sorted(batch["records"], key=lambda row: concept_key(row["concept_key"])):
            key = concept_key(record["concept_key"])
            if key not in accepted:
                continue
            matches = []
            for entry in entries.values():
                if entry["category_id"] != category:
                    continue
                details = json.loads(entry["details"])
                research = details.get("web_research", {})
                if key in research or concept_key(entry["title"]) in {key, concept_key(record["title_ko"])}:
                    matches.append(entry["id"])
            target = record.get("existing_entry_id")
            require(not target or (target in entries and entries[target]["category_id"] == category),
                    "existing entry is missing or in another category")
            require(len(matches) <= 1 and (not target or not matches or matches == [target]),
                    "ambiguous concept/enrichment target")
            generated = "web-" + category + "-" + sha256(key.encode())[:24]
            require(bool(target or matches) or generated not in entries, "generated entry ID collision")
            target = target or (matches[0] if matches else generated)
            require(target not in used_targets, "multiple concepts target the same entry")
            used_targets.add(target)
            referenced = sorted({fact["evidence"]["source_id"] for fact in record["facts"] + record["proposals"]}
                                | {candidate["source_id"] for candidate in record["media_candidates"]})
            source_ids = {}
            for sid in referenced:
                source = sources[sid]
                source_id = "web-source-" + sha256(canonical(source).encode())[:24]
                row = {"id": source_id, "name": source["publisher"] + " · " + source["title"], "url": source["url"],
                       "license": canonical(source["rights"]), "hosting": "metadata_only",
                       "checked": source["checked_at"]}
                require(source_id not in source_rows or source_rows[source_id] == row, "source ID collision")
                source_rows[source_id] = row
                source_ids[sid] = source_id
                batch_sources.add(source_id)
            if target not in entries:
                entries[target] = {"id": target, "category_id": category, "source_id": source_ids[referenced[0]],
                                   "title": record["title_ko"], "original_title": "", "description": record["summary"],
                                   "gender": "공용", "subtype": record["subtype"], "status": "external",
                                   "details": "{}", "version": 1, "updated": batch["collected_at"][:10],
                                   "search_text": " ".join([target, record["title_ko"], record["summary"], *record["tags"]]).lower()}
                result["entries"].append(entries[target])
            entry = entries[target]
            details = json.loads(entry["details"])
            require(type(details) is dict, "entry details must be an object")
            research = details.setdefault("web_research", {})
            require(type(research) is dict, "reserved web_research details must be an object")
            research[key] = {"record": record, "sources": [sources[sid] for sid in referenced],
                             "source_ids": source_ids, "input_sha256": sha256(item.staging), "review": item.review}
            entry["details"] = canonical(details)
            added += int(target == generated)
            enriched += int(target != generated)
            fact_count += len(record["facts"])
        if accepted:
            # A metadata batch never increments existing Drive/media counters.
            primary = sorted(batch_sources)[0]
            iid = "web-import-" + category + "-" + sha256(canonical(_envelope(item)).encode())[:24]
            report = {"input_sha256": sha256(item.staging), "accepted_concepts": len(accepted),
                      "category_id": category, "added_entries": added, "enriched_entries": enriched,
                      "reviewed_facts": fact_count, "shortfall_reason": item.review["shortfall_reason"],
                      "shortfall": 20 - len(accepted), "media_downloaded": 0, "media_visual_reviewed": 0,
                      "media_candidates_only": True}
            row = {"id": iid, "source_id": primary, "expected": 20, "indexed": len(accepted),
                   "groups": len(accepted), "status": "metadata_reviewed",
                   "report": canonical(report), "checked": item.review["reviewed_at"]}
            require(iid not in import_rows or import_rows[iid] == row, "import ID collision")
            import_rows[iid] = row
    old_sources = {row["id"] for row in seed["sources"]}
    old_imports = {row["id"] for row in seed["import_batches"]}
    result["sources"].extend(source_rows[key] for key in sorted(source_rows.keys() - old_sources))
    result["import_batches"].extend(import_rows[key] for key in sorted(import_rows.keys() - old_imports))
    return result
