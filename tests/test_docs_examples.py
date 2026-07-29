"""The documentation's code examples must reference an API that exists.

A Sphinx build that succeeds says only that the markup parses. It cannot
notice that an example reads a field the models no longer have — which is
exactly how the conversions example went on printing ``.content`` after that
field was removed.
"""

from __future__ import annotations

import ast
import pathlib
import re

import pytest

import aioplatega
from aioplatega import PayoutClient, Platega, methods, types

ROOT = pathlib.Path(__file__).resolve().parent.parent
SOURCES = [
    *sorted((ROOT / "docs").rglob("*.md")),
    *sorted((ROOT / "docs").rglob("*.rst")),
    ROOT / "README.rst",
]

# Attribute names that belong to Python, a web framework or a docstring's
# prose rather than to this library.
FOREIGN = {
    "append",
    "body",
    "decode",
    "encode",
    "format",
    "get",
    "get_data",
    "headers",
    "items",
    "json",
    "keys",
    "print",
    "route",
    "run",
    "rstrip",
    "sleep",
    "strip",
    "values",
    "META",
    "model_validate",
    "model_dump",
    "root",
    "status_code",
    "message",
    "trace_id",
    "code",
    "errors",
}


def _code_blocks() -> list[tuple[pathlib.Path, str]]:
    blocks: list[tuple[pathlib.Path, str]] = []
    for path in SOURCES:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        blocks += [(path, m.group(1)) for m in re.finditer(r"```python\n(.*?)```", text, re.S)]
        for m in re.finditer(r"code-block:: python\n\n((?:[ ]+\S.*\n|\n)+)", text):
            raw = m.group(1)
            indent = min(
                (len(line) - len(line.lstrip()) for line in raw.splitlines() if line.strip()),
                default=0,
            )
            blocks.append((path, "\n".join(line[indent:] for line in raw.splitlines())))
    return blocks


def _known_names() -> set[str]:
    names = set(aioplatega.__all__) | set(types.__all__) | set(methods.__all__)
    for name in types.__all__:
        model = getattr(types, name)
        if hasattr(model, "model_fields"):
            names |= set(model.model_fields)
    names |= {m for m in dir(Platega) if not m.startswith("_")}
    names |= {m for m in dir(PayoutClient) if not m.startswith("_")}
    for enum_name in ("PaymentStatus", "PaymentMethodInt", "SubscriptionInterval"):
        names |= {m.name for m in getattr(aioplatega, enum_name)}
    return names | FOREIGN


BLOCKS = _code_blocks()


def test_documentation_contains_examples():
    assert len(BLOCKS) > 15


@pytest.mark.parametrize(
    ("path", "code"), BLOCKS, ids=[f"{p.name}:{i}" for i, (p, _) in enumerate(BLOCKS)]
)
def test_example_parses(path, code):
    source = code.strip()
    try:
        ast.parse(source)
    except SyntaxError:
        # Fragments using `await` outside a function are still valid examples.
        ast.parse("async def _():\n" + "\n".join(f"    {line}" for line in source.split("\n")))


@pytest.mark.parametrize(
    ("path", "code"), BLOCKS, ids=[f"{p.name}:{i}" for i, (p, _) in enumerate(BLOCKS)]
)
def test_example_only_touches_real_attributes(path, code):
    source = code.strip()
    try:
        tree = ast.parse(source)
    except SyntaxError:
        tree = ast.parse(
            "async def _():\n" + "\n".join(f"    {line}" for line in source.split("\n"))
        )

    known = _known_names()
    used = {
        node.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Attribute) and not node.attr.startswith("_")
    }
    unknown = sorted(used - known)
    assert unknown == [], f"{path.name}: {unknown}"
