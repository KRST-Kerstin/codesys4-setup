#!/usr/bin/env python3
"""Fail-closed validator for the not-yet-supported optional library input."""

import os
import sys


def main():
    requested = os.environ.get("LIBRARY_IDS", "").strip()
    if not requested:
        print("No libraries requested; continuing with an empty library list.")
        return 0
    if any(token in requested.lower() for token in ("latest", "*")):
        print("::error::Library wildcard/latest versions are not supported or resolved automatically.", file=sys.stderr)
        return 1
    print("::error::Optional library installation is not implemented; no library IDs or versions are currently supported.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
