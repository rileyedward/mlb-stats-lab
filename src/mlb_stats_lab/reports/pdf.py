"""HTML → PDF rendering via WeasyPrint.

On Apple Silicon macOS, ``ctypes.util.find_library`` does not search
``/opt/homebrew/lib`` by default, so cffi (used by WeasyPrint) cannot locate
pango/cairo/glib. We monkey-patch ``find_library`` at import time so that any
homebrew-installed dylib is discoverable.
"""

from __future__ import annotations

import ctypes.util
import sys
from pathlib import Path

_BREW_LIB_DIRS = ["/opt/homebrew/lib", "/usr/local/lib"]


def _patch_find_library() -> None:
    if sys.platform != "darwin":
        return

    original = ctypes.util.find_library

    def _try_paths(name: str) -> str | None:
        candidates = [
            f"{name}.dylib",
            f"lib{name}.dylib" if not name.startswith("lib") else None,
        ]
        # Names like ``libgobject-2.0-0`` mean ``libgobject-2.0.0.dylib`` on macOS.
        if "-" in name:
            head, tail = name.rsplit("-", 1)
            candidates.append(f"{head}.{tail}.dylib")
            if not head.startswith("lib"):
                candidates.append(f"lib{head}.{tail}.dylib")
        for base in _BREW_LIB_DIRS:
            for cand in filter(None, candidates):
                p = Path(base) / cand
                if p.exists():
                    return str(p)
        return None

    def patched(name: str) -> str | None:
        result = original(name)
        if result:
            return result
        return _try_paths(name)

    ctypes.util.find_library = patched


_patch_find_library()


def html_to_pdf(html_str: str, output_path: Path, base_url: Path | None = None) -> Path:
    """Render an HTML string to PDF using WeasyPrint."""
    from weasyprint import HTML  # type: ignore[import-untyped]

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=html_str, base_url=str(base_url) if base_url else None).write_pdf(
        target=str(output_path)
    )
    return output_path
