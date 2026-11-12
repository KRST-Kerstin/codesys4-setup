#!/usr/bin/env python3
"""Fetch, validate and install only the package pinned by the reviewed manifest."""
import argparse
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys
import urllib.request


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest', required=True)
    parser.add_argument('--cache-dir', default=os.path.expanduser('~/.cache/codesys4'))
    parser.add_argument('--version', required=True)
    parser.add_argument('--url', default='')
    parser.add_argument('--sha256', default='')
    args = parser.parse_args()
    release = json.loads(pathlib.Path(args.manifest).read_text())
    version, url, expected = release['version'], release['url'], release['sha256']
    if args.version != version or (args.url and args.url != url) or (args.sha256 and args.sha256 != expected):
        raise ValueError('requested release or override does not match reviewed manifest')
    cache = pathlib.Path(args.cache_dir)
    cache.mkdir(parents=True, exist_ok=True)
    identity = hashlib.sha256(f'{version}\0{url}\0{expected}'.encode()).hexdigest()
    deb = cache / f'{version}-{identity}.deb'
    if not deb.exists():
        request = urllib.request.Request(url, headers={'User-Agent': 'codesys4-setup'})
        with urllib.request.urlopen(request, timeout=60) as response:
            content = response.read()
        tmp = deb.with_suffix('.tmp')
        tmp.write_bytes(content)
        tmp.replace(deb)
    actual = hashlib.sha256(deb.read_bytes()).hexdigest()
    if actual != expected:
        deb.unlink(missing_ok=True)
        raise ValueError(f'SHA-256 mismatch: expected {expected}, got {actual}')
    # Validate archive structure before invoking the package manager.
    subprocess.run(['dpkg-deb', '--info', str(deb)], check=True, stdout=subprocess.DEVNULL)
    subprocess.run(['sudo', 'apt-get', 'update'], check=True)
    subprocess.run(['sudo', 'apt-get', 'install', '-y', str(deb)], check=True)
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as exc:
        print(f'::error::{exc}', file=sys.stderr)
        sys.exit(1)
