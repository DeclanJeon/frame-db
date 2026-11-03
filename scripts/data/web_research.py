"""Standalone offline CLI; only stage-reviewed writes accepted metadata files."""
import argparse
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
from web_pack import ROOT, WebPackError, categories, load_pair, read_json, require, stage_reviewed, validate_batch


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("validate-staging", "validate-review", "stage-reviewed"):
        command = commands.add_parser(name)
        command.add_argument("--root", type=Path, default=ROOT / "data/web-research",
                             help="Research directory containing staging/ and reviews/")
        if name == "stage-reviewed":
            selection = command.add_mutually_exclusive_group(required=True)
            selection.add_argument("--categories", help="Comma-separated category IDs")
            selection.add_argument("--all", action="store_true", help="Require every specified category")
        else:
            command.add_argument("--category", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command != "stage-reviewed":
            require(args.category in categories(), "unknown category")
        match args.command:
            case "validate-staging":
                batch = validate_batch(read_json(args.root / "staging" / f"{args.category}.json"), args.category)
                output = {"category_id": args.category, "records": len(batch["records"]), "structural_only": True}
            case "validate-review":
                approved = load_pair(args.root, args.category)
                output = {"category_id": args.category, "accepted_count": approved.review["accepted_count"],
                          "offline_review_contract_valid": True}
            case "stage-reviewed":
                selected = sorted(categories()) if args.all else args.categories.split(",")
                output = stage_reviewed(args.root, selected)
        print(json.dumps(output, ensure_ascii=False, sort_keys=True))
        return 0
    except (WebPackError, OSError, UnicodeError, json.JSONDecodeError) as error:
        print(f"web-research: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
