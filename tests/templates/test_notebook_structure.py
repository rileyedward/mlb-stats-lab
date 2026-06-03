"""Structural smoke tests for notebook templates.

Verifies each jupytext ``.py`` template:
- exists,
- converts to a valid notebook,
- has the required cell tags (`parameters`, `setup`, `load`, `summary`).
"""

from __future__ import annotations

import jupytext
import pytest

from mlb_stats_lab.cli.registry import TEMPLATES


@pytest.mark.parametrize("name", list(TEMPLATES))
def test_notebook_template_has_expected_tags(name: str) -> None:
    spec = TEMPLATES[name]
    assert spec.notebook_path.exists(), f"{spec.notebook_path} missing"
    assert spec.notebook_path.suffix == ".py", "templates are jupytext .py source"
    nb = jupytext.read(str(spec.notebook_path))
    all_tags: set[str] = set()
    for cell in nb.cells:
        for t in cell.get("metadata", {}).get("tags", []) or []:
            all_tags.add(t)
    assert "parameters" in all_tags
    assert "setup" in all_tags
    assert "load" in all_tags
    assert "summary" in all_tags
