#!/usr/bin/env python3
"""Version bumping script for aioplatega."""

import re
import sys
from pathlib import Path

VERSION_PATTERN = re.compile(r'__version__ = "(\d+)\.(\d+)\.(\d+)"')


def bump_version(part: str) -> str:
    meta_path = Path("aioplatega/__meta__.py")
    content = meta_path.read_text()

    version_match = VERSION_PATTERN.search(content)
    if not version_match:
        msg = "Could not find version in aioplatega/__meta__.py"
        raise ValueError(msg)

    major, minor, patch = map(int, version_match.groups())

    if part == "major":
        major += 1
        minor = 0
        patch = 0
    elif part == "minor":
        minor += 1
        patch = 0
    elif part == "patch":
        patch += 1
    elif part.startswith("to:"):
        new_version = part.removeprefix("to:")
        content = VERSION_PATTERN.sub(f'__version__ = "{new_version}"', content)
        meta_path.write_text(content)
        return new_version
    else:
        msg = f"Unknown part: {part}. Use major, minor, patch, or to:X.Y.Z"
        raise ValueError(msg)

    new_version = f"{major}.{minor}.{patch}"
    content = VERSION_PATTERN.sub(f'__version__ = "{new_version}"', content)
    meta_path.write_text(content)
    return new_version


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/bump_version.py [major|minor|patch|to:X.Y.Z]")
        sys.exit(1)

    result = bump_version(sys.argv[1])
    print(f"Bumped version to {result}")
