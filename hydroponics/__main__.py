"""Inspect design inputs; no hydraulic simulation or hardware control yet."""
import argparse
import json
from pathlib import Path


def unknowns(value, prefix=""):
    if isinstance(value, dict):
        for key, item in value.items():
            yield from unknowns(item, f"{prefix}.{key}" if prefix else key)
    elif value is None:
        yield prefix


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path, help="Path to the tower JSON inputs")
    args = parser.parse_args()
    try:
        config = json.loads(args.config.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    if not isinstance(config, dict):
        parser.error("The configuration must be a JSON object")
    print("Hydroponic tower: design input review")
    print(json.dumps(config, indent=2))
    missing = list(unknowns(config))
    print(f"\nUnspecified inputs: {len(missing)}")
    for field in missing:
        print(f"  - {field}")
    print("\nInput report only: no flow prediction or watering schedule has been validated.")


if __name__ == "__main__":
    main()
