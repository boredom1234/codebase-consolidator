# Runbook

This document outlines operations and deployment procedures for the Codebase Consolidator tool.

## Deployment Procedures

## Common Issues and Fixes

### GUI Not Starting

*   **Issue**: `ModuleNotFoundError: No module named 'ttkbootstrap'`.
*   **Fix**: Ensure all dependencies are installed using `pip install -r requirements.txt` or `pip install .`.
*   **Issue**: (Linux) `_tkinter.TclError: no display name and no $DISPLAY environment variable`.
*   **Fix**: The GUI requires an active X11/Wayland session. Use the CLI version (`cc`) if working in a headless environment.

### Large Codebase Performance

*   **Issue**: Consolidation takes a long time or creates very large files.
*   **Fix**: Use the `--max-size` parameter to cap the size of each output part (e.g., `--max-size 256000` for 250KB).

## Rollback Procedures

If a release is found to be faulty:
1. Revert the changes in the main branch.
2. Publish a new patch version (e.g., from `1.0.1` to `1.0.2`) with the stable code.
3. If necessary, yank the faulty version from PyPI using the web interface.
