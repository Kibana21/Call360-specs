#!/usr/bin/env python3
"""Deterministic evidence manifest for uncommitted work (ADR-0003 §6, owner decision C-23).

Usage: python3 scripts/evidence_manifest.py <repo-path> [--exclude <repo-relative-prefix> ...]

Prints the repository's base SHA, one line per changed/new/deleted file
(`status<TAB>sha256<TAB>path`, sorted by path; deleted files hash as `-`) and a
SHA-256 over the canonical manifest lines. Read-only: runs `git rev-parse` and
`git status`, reads files, writes nothing.
"""
from __future__ import annotations
import hashlib
import subprocess
import sys
from pathlib import Path


def git(repo: Path, *args: str) -> bytes:
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True).stdout


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    repo = Path(argv[0]).resolve()
    excludes = [argv[i + 1] for i, a in enumerate(argv) if a == "--exclude" and i + 1 < len(argv)]
    base = git(repo, "rev-parse", "HEAD").decode().strip()
    entries = []
    raw = git(repo, "status", "--porcelain=v1", "-z", "--untracked-files=all").split(b"\0")
    i = 0
    while i < len(raw):
        item = raw[i]
        i += 1
        if not item:
            continue
        code, path = item[:2].decode(), item[3:].decode()
        if code[0] in "RC":  # rename/copy: next field is the original path
            i += 1
        if any(path.startswith(e) for e in excludes):
            continue
        status = "??" if code == "??" else ("D" if "D" in code else ("A" if "A" in code else "M"))
        f = repo / path
        digest = hashlib.sha256(f.read_bytes()).hexdigest() if f.is_file() else "-"
        entries.append(f"{status}\t{digest}\t{path}")
    entries.sort(key=lambda line: line.split("\t", 2)[2])
    body = "\n".join(entries) + "\n"
    print(f"repository\t{repo.name}")
    print(f"base_sha\t{base}")
    print(f"files\t{len(entries)}")
    if excludes:
        print(f"excluded_prefixes\t{','.join(sorted(excludes))}")
    sys.stdout.write(body)
    print(f"manifest_sha256\t{hashlib.sha256(body.encode()).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
