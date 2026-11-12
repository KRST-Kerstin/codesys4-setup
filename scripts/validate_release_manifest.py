#!/usr/bin/env python3
"""Validate the manually reviewed CODESYS release manifest without network access."""

import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

MANIFEST = Path(__file__).resolve().parents[1] / "releases" / "codesys4-linux-amd64.json"
EXPECTED_URL = "https://store-archive.codesys.com/ftp_download/3S/CODESYS4/2101000024/1.0.0.0/codesys-4_1.0.0.0_amd64.deb"
EXPECTED_SHA256 = "8f6a614136997c9a1242db16c7a0b735359a5830e7501a14f6407322c0184118"


def validate(document: Any) -> dict[str, Any]:
    if not isinstance(document, dict):
        raise ValueError("manifest must be a JSON object")
    required = {"version", "architecture", "package_format", "channel", "url", "sha256", "artifact_scope", "provenance", "reviewed_at"}
    missing = required - document.keys()
    if missing:
        raise ValueError("missing required fields: " + ", ".join(sorted(missing)))
    if document["channel"] is not None and (not isinstance(document["channel"], str) or not document["channel"].strip()):
        raise ValueError("channel must be null when unapproved or a non-empty approved label")
    for key in required - {"channel"}:
        if not isinstance(document[key], str) or not document[key].strip():
            raise ValueError(f"{key} must be a non-empty string")
    if document["version"] != "1.0.0.0":
        raise ValueError("version is not pinned by this reviewed manifest")
    if document["architecture"] != "amd64" or document["package_format"] != "deb":
        raise ValueError("only the reviewed Linux amd64 DEB artifact is accepted")
    if document["url"] != EXPECTED_URL:
        raise ValueError("URL does not match the exact reviewed artifact URL")
    if not re.fullmatch(r"[0-9a-f]{64}", document["sha256"]):
        raise ValueError("sha256 must be 64 lowercase hexadecimal characters")
    if document["sha256"] != EXPECTED_SHA256:
        raise ValueError("sha256 does not match the user-approved local TOFU pin")
    try:
        date.fromisoformat(document["reviewed_at"])
    except ValueError as exc:
        raise ValueError("reviewed_at must be an ISO-8601 date") from exc
    provenance = document["provenance"].lower()
    if "not vendor-authenticated" not in provenance or "tofu" not in provenance:
        raise ValueError("provenance must identify the TOFU pin as not vendor-authenticated")
    if "1.0.0.0" not in document["artifact_scope"] or "amd64" not in document["artifact_scope"] or "deb" not in document["artifact_scope"].lower():
        raise ValueError("artifact_scope must identify version 1.0.0.0, amd64 and DEB")
    return document


def main() -> int:
    try:
        document = json.loads(MANIFEST.read_text(encoding="utf-8"))
        validate(document)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"::error::Invalid CODESYS release manifest: {exc}", file=sys.stderr)
        return 1
    print(f"Validated pinned CODESYS {document['version']} Linux {document['architecture']} DEB manifest")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
