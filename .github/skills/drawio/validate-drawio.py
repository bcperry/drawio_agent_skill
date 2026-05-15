#!/usr/bin/env python3
import argparse
import sys
import xml.etree.ElementTree as ET


def validate(path: str) -> int:
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as error:
        print(f"xml-invalid: {error}", file=sys.stderr)
        return 1

    missing_label_background = []
    for cell in root.iter("mxCell"):
        value = cell.get("value")
        style = cell.get("style") or ""
        if value and value.strip() and "labelBackgroundColor=none;" not in style:
            missing_label_background.append(cell.get("id") or "<missing id>")

    if missing_label_background:
        print(
            "cells missing labelBackgroundColor=none;: "
            + ", ".join(missing_label_background),
            file=sys.stderr,
        )
        return 1

    print("drawio-validation-ok")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate draw.io XML well-formedness and required skill conventions."
    )
    parser.add_argument("path", help="Path to the .drawio file to validate")
    args = parser.parse_args()
    return validate(args.path)


if __name__ == "__main__":
    raise SystemExit(main())
