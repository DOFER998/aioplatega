"""Sphinx configuration for aioplatega documentation."""

import os
import sys

sys.path.insert(0, os.path.abspath(".."))

from aioplatega.__meta__ import __version__

project = "aioplatega"
copyright = "2026, c0mrade"
author = "c0mrade"
release = __version__

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_autodoc_typehints",
    "sphinx_copybutton",
    "sphinx_design",
    "myst_parser",
]

templates_path = ["_templates"]
exclude_patterns = ["_build"]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "fieldlist",
    "tasklist",
]

autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
    "member-order": "bysource",
}
autodoc_typehints = "description"
autodoc_class_signature = "separated"

suppress_warnings = ["autodoc"]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "aiohttp": ("https://docs.aiohttp.org/en/stable/", None),
    "pydantic": ("https://docs.pydantic.dev/latest/", None),
}

html_theme = "shibuya"
html_title = "aioplatega"

html_theme_options = {
    "accent_color": "blue",
    "color_mode": "light",
    "dark_code": True,
    "github_url": "https://github.com/DOFER998/aioplatega",
    "nav_links": [
        {"title": "Getting Started", "url": "getting-started"},
        {"title": "API Reference", "url": "api/index"},
    ],
}

html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_js_files = ["custom.js"]
