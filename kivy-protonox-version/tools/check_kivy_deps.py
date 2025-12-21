#!/usr/bin/env python3
"""
Utility to inspect or install local kivy-dependencies for building
(protonox-kivy). Usage:

  python tools/check_kivy_deps.py --list
  python tools/check_kivy_deps.py --install path/to/archive.tar.gz

The script extracts archives into `kivy-dependencies/` in the package root
and reports basic layout so `setup.py` can pick it up via KIVY_DEPS_ROOT.
"""
from pathlib import Path
import argparse
import tarfile
import zipfile
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
DEPS_DIR = ROOT / 'kivy-dependencies'


def list_contents():
    if not DEPS_DIR.exists():
        print('No local kivy-dependencies directory found at', DEPS_DIR)
        return 1
    print('Listing contents of', DEPS_DIR)
    for p in sorted(DEPS_DIR.rglob('*')):
        print('-', p.relative_to(DEPS_DIR))
    return 0


def install_archive(archive_path: Path):
    if not archive_path.exists():
        print('Archive not found:', archive_path)
        return 2
    DEPS_DIR.mkdir(exist_ok=True)
    if tarfile.is_tarfile(str(archive_path)):
        with tarfile.open(str(archive_path)) as tf:
            tf.extractall(path=str(DEPS_DIR))
    elif zipfile.is_zipfile(str(archive_path)):
        with zipfile.ZipFile(str(archive_path)) as zf:
            zf.extractall(path=str(DEPS_DIR))
    else:
        print('Unknown archive format. You can also place files manually into', DEPS_DIR)
        return 3
    print('Extracted', archive_path, 'to', DEPS_DIR)
    return 0


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--list', action='store_true')
    p.add_argument('--install', type=Path)
    args = p.parse_args()
    if args.list:
        return list_contents()
    if args.install:
        return install_archive(args.install)
    p.print_help()
    return 0


if __name__ == '__main__':
    sys.exit(main())
