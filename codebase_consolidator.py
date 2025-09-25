#!/usr/bin/env python3
"""
Wrapper module to expose the existing CLI (stored in codebase-consolidator.py)
with a proper, importable module name and symbols:
- CodebaseConsolidator
- main()

This allows setup.py console_scripts and other modules (like the GUI) to import
`codebase_consolidator` cleanly, while keeping the original CLI file intact.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Optional


def _load_cli_module() -> ModuleType:
    """Dynamically load the sibling `codebase-consolidator.py` as a module."""
    here = Path(__file__).resolve().parent
    cli_path = here / "codebase-consolidator.py"

    if not cli_path.exists():
        raise FileNotFoundError(
            f"Cannot locate '{cli_path}'. Ensure the CLI file exists alongside this module."
        )

    spec = importlib.util.spec_from_file_location("_codebase_consolidator_cli", str(cli_path))
    if spec is None or spec.loader is None:
        raise ImportError("Unable to create spec for codebase-consolidator.py")

    module = importlib.util.module_from_spec(spec)
    # Ensure relative imports (if any) inside the CLI work relative to its file location
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    return module


# Load once at import time so that attributes are bound for consumers
_cli_module = _load_cli_module()

# Re-export the main symbols expected by consumers
CodebaseConsolidator = getattr(_cli_module, "CodebaseConsolidator")


def main() -> Optional[int]:
    """Delegate to the CLI's main()."""
    return getattr(_cli_module, "main")()
