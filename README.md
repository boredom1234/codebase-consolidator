# Codebase Consolidator for NotebookLM

Transform sprawling codebases into NotebookLM-ready study packs. The project combines a CLI (`codebase-consolidator.py`) and a modern GUI (`codebase_consolidator_gui.py`) that distill source trees into richly annotated Markdown bundles tailor-made for [NotebookLM](https://notebooklm.google.com/) sessions.

![image](https://raw.githubusercontent.com/boredom1234/codebase-consolidator/refs/heads/master/assets/screenshot.png)

## Why This?

- **Purpose-built pipeline**: Consolidate thousands of source files into conversational chunks that NotebookLM ingests without context loss.
- **Curated metadata**: Every Markdown carries file sizes, timestamps, language tags, and optional line numbers to help NotebookLM anchor citations.
- **Notebook-friendly structure**: Table-of-contents anchors and consistent headings make it easy to quote specific files mid-conversation.
- **Rapid iteration**: The asynchronous preview keeps the GUI responsive while scanning large repositories, and double-click previews open files instantly in your editor.

## Quick Start Workflow

1. **Install dependencies**
   ```bash
   pip install -e .
   ```
2. **Launch the GUI**
   ```bash
   python codebase_consolidator_gui.py
   ```
3. **Attach your repository** via the "Codebase Directory" picker and tap **"Refresh Preview"**.
4. **Fine-tune formatting** (syntax theme, line numbers) so NotebookLM gets the context you want.
5. **Run consolidation**; the tool emits versioned Markdown parts plus an index README.
6. **Upload the generated folder** (or a ZIP of it) into NotebookLM as a new source.
7. **Reference file anchors** (e.g., `codebase_part_003.md#src-utils-tokens-py`) during NotebookLM chats to retrieve precise code spans.

## Feature Highlights

- **NotebookLM-optimized Markdown**
  - **Structured navigation**: Auto-generated tables of contents on every part help you and NotebookLM scan quickly.
  - **File metadata blocks**: Each code sample includes language tags to reinforce semantic cues for NotebookLM.
  - **Theme markers**: Custom syntax theme notes enable downstream renderers to respect your preferred palette.
- **Productive GUI**
  - **Non-blocking preview**: Repository scans run on a worker thread, eliminating "Not Responding" freezes.
  - **Explorable file tree**: Double-click any file entry to open it locally before you commit to consolidation.
  - **Config presets-ready**: State variables are organized for future profile storage (bring your own persistence layer).
- **Dependable CLI**
  - **Headless operation**: Scriptable consolidation for CI pipelines that publish NotebookLM packets nightly.
  - **Git-aware filtering**: Respects `.gitignore` patterns and comprehensive framework-specific exclusions.
  - **Size-balanced buckets**: Files are distributed to maintain roughly even context windows per Markdown part.

## Installation & Requirements

- **Python**: 3.9+
- **Dependencies**: `ttkbootstrap` (installed automatically via `pip install -e .`)
- **Platforms**: Windows, macOS, Linux (GUI uses Tkinter + ttkbootstrap themes)

```bash
# clone and enter the repo first
pip install -e .
```

## Operating Modes

### GUI (`codebase_consolidator_gui.py`)

- **Launch**: `python codebase_consolidator_gui.py`
- **Recommended for**: curating NotebookLM source packs interactively, experimenting with formatting, quick validation via preview.
- **Key panels**:
  - **Settings**: select codebase directory, output base, desired Markdown count, custom folder names.
  - **Formatting Options**: choose one of 13 syntax themes and toggle line numbers for NotebookLM-friendly references.
  - **Preview**: asynchronous tree explorer with file size/type columns and direct-open support.
  - **Log**: live stream of consolidation progress, perfect for verifying large runs.

### CLI (`codebase-consolidator.py`)

- **Launch**: `python codebase-consolidator.py /path/to/project -n 80`
- **Flags**:
  - `-n / --num-files`: target Markdown parts (NotebookLM handles many smaller files better than a few giant ones).
  - `-o / --output-dir`: base directory for generated packets.
  - `--folder-name`: override the timestamped default for deterministic NotebookLM uploads.
  - `-v / --verbose`: emit stack traces when debugging complex repos.
- **Integration tip**: wire into CI to publish fresh NotebookLM packs whenever the default branch changes.

## Preparing NotebookLM Sources

- **Curate part size**: Start with `-n 80`–`120` for medium repos so each Markdown stays comfortably under NotebookLM's per-file limits.
- **Preserve structure**: Upload the entire output directory; NotebookLM will ingest each Markdown as an individual source while keeping relative links intact.
- **Annotate sessions**: Use the generated `README.md` inside the output folder to remind future you (and NotebookLM) how the pack was built.
- **Refresh cycle**: Re-run consolidation after major refactors; the timestamped folder names ensure NotebookLM sees them as discrete uploads.

## Advanced Tips

- **Ignore tuning**: Add project-specific patterns to `.gitignore`; the consolidator inherits them automatically and caches an extended ignore set in `CodebaseConsolidator._load_gitignore()`.
- **Preflight checks**: Use the preview tree and built-in "Open File" action to vet large binaries or generated artifacts before they sneak into your NotebookLM context.
- **Line numbers vs. tokens**: NotebookLM can reference code by range numbers, but enabling line numbers increases token counts. Toggle per audience.
- **Theming strategy**: Set syntax theme to match your NotebookLM conversation tone (e.g., `solarized-dark` for dark-mode transcripts).

## Troubleshooting

- **GUI feels idle**: The status label shows "Scanning codebase..." while the worker thread runs. For massive repos, expect a short delay before the tree populates.
- **Markdown too large**: Increase `--num-files` (CLI) or "Target # of files" (GUI) to reduce individual document size before uploading to NotebookLM.
- **Missing files**: Check `.gitignore` and the extended ignore list in `CodebaseConsolidator._load_gitignore()`; add exceptions if needed.
- **NotebookLM citations off**: Ensure line numbers remain enabled, and mention anchors (e.g., `#src-app-main-py`) explicitly in NotebookLM prompts.

## Project Structure

- **`codebase-consolidator.py`**: CLI engine with NotebookLM-friendly Markdown emitters.
- **`codebase_consolidator.py`**: Import shim that exposes `CodebaseConsolidator` for the GUI and packaging entry points.
- **`codebase_consolidator_gui.py`**: ttkbootstrap interface with asynchronous preview, log streaming, and formatting controls.
- **`setup.py`**: Package metadata; defines console scripts for both CLI and GUI launchers.

## License

MIT License — build, tweak, and ship NotebookLM workflows freely.
