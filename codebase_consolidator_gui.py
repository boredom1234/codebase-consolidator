#!/usr/bin/env python3
"""
Codebase Consolidator - GUI (Tkinter + ttkbootstrap)

This GUI wraps the existing CodebaseConsolidator logic and presents a simple
interface to:
- select codebase directory
- choose target number of output files
- choose output directory (optional)
- set a custom folder name (optional)
- run consolidation in a background thread
- stream logs to the UI
"""

from __future__ import annotations

import os
import queue
import subprocess
import sys
import threading
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

import ttkbootstrap as tb
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.constants import (
    LEFT,
    RIGHT,
    BOTTOM,
    X,
    Y,
    BOTH,
    YES,
    NORMAL,
    DISABLED,
    SUCCESS,
    DANGER,
    INFO,
    SECONDARY,
    END,
)
from ttkbootstrap.scrolled import ScrolledText
from tkinter import filedialog
from tkinter import ttk

from codebase_consolidator import CodebaseConsolidator


class EnhancedCodebaseConsolidator(CodebaseConsolidator):
    """Extended consolidator with GUI formatting options."""

    def __init__(
        self,
        root_path: str,
        target_files: int = 50,
        syntax_theme: str = "github",
        line_numbers: bool = True,
        use_xml: bool = False,
        include_tree: bool = True,
        max_part_size: int = 512000,
    ):
        super().__init__(
            root_path,
            target_files,
            use_xml=use_xml,
            include_tree=include_tree,
            max_part_size=max_part_size,
        )
        self.syntax_theme = syntax_theme
        self.line_numbers = line_numbers

    def _write_part_header(self, f, part_num: int, total_parts: int, file_count: int, all_files: List[Path] = None):
        """Override to add GUI-specific metadata to the header"""
        super()._write_part_header(f, part_num, total_parts, file_count, all_files)
        f.write(f"**Syntax Theme:** {self.syntax_theme}  \n")
        f.write(
            f"**Line Numbers:** {'Enabled' if self.line_numbers else 'Disabled'}  \n"
        )
        f.write(f"**Format:** {'XML Tags' if self.use_xml else 'Markdown Code Blocks'}  \n\n")

    def _format_code_block(self, content: str, language: str, file_path: Path) -> str:
        """Format code block with optional line numbers and syntax theme info."""
        # For RAG optimization: skip line numbers if using XML
        effective_line_numbers = self.line_numbers and not self.use_xml

        # Add syntax theme as a comment if it's not the default (only for markdown)
        theme_comment = ""
        if self.syntax_theme != "github" and not self.use_xml:
            theme_comment = f"<!-- Syntax theme: {self.syntax_theme} -->\n"

        # Add line numbers if enabled
        if effective_line_numbers:
            lines = content.split("\n")
            # Handle case where split produces an empty string at the end if content ends with newline
            if lines and not lines[-1]:
                lines.pop()

            numbered_lines = []
            for i, line in enumerate(lines, 1):
                numbered_lines.append(f"{i:4d} | {line}")
            content = "\n".join(numbered_lines)

            # Re-add newline if it was there (to match original behavior mostly)
            content += "\n"

        if self.use_xml:
            rel_path = file_path.relative_to(self.root_path).as_posix()
            return f'<file path="{rel_path}" language="{language}">\n{content}</file>'

        return f"{theme_comment}```{language}\n{content}```"

    def _create_index(self, output_path: Path, files: List[Path], file_buckets: List[List[Path]], actual_files: int):
        """Override to add formatting options to the index file"""
        # Call the parent implementation to generate the base file, but we'll overwrite it
        # because the parent writes the whole file at once.
        # Actually, since the parent writes the WHOLE file, calling super() just to overwrite it is wasteful.
        # We'll reimplement it with the extra section.

        index_file = output_path / "README.md"
        with open(index_file, "w", encoding="utf-8") as f:
            f.write("# 📚 Consolidated Codebase\n\n")
            f.write(f"**Source Directory:** `{self.root_path.absolute()}`  \n")
            f.write(
                f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n"
            )
            f.write(f"**Total Files Processed:** {len(files)}  \n")
            f.write(f"**Target Output Files:** {self.target_files}  \n")
            f.write(f"**Actual Output Files:** {actual_files}  \n")
            f.write(f"**Syntax Theme:** {self.syntax_theme}  \n")
            f.write(
                f"**Line Numbers:** {'Enabled' if self.line_numbers else 'Disabled'}  \n"
            )
            f.write(f"**XML Format:** {'Yes' if self.use_xml else 'No'}  \n")
            f.write(f"**File Tree:** {'Included' if self.include_tree else 'Excluded'}  \n\n")

            f.write("## 🎨 Formatting Options\n\n")
            f.write(f"- **Syntax Highlighting Theme:** `{self.syntax_theme}`\n")
            f.write(
                f"- **Line Numbers:** {'✅ Enabled' if self.line_numbers else '❌ Disabled'}\n"
            )
            f.write(f"- **XML Tags:** {'✅ Enabled' if self.use_xml else '❌ Disabled'}\n")
            f.write(
                f"- **File Tree:** {'✅ Included' if self.include_tree else '❌ Excluded'}\n\n"
            )

            f.write("## 📋 File Structure\n\n")
            f.write("| Part | Files | Description |\n")
            f.write("|------|-------|-------------|\n")

            for i, bucket in enumerate(file_buckets):
                file_list = ", ".join(
                    [f"`{f.relative_to(self.root_path)}`" for f in bucket[:3]]
                )
                if len(bucket) > 3:
                    file_list += f" and {len(bucket) - 3} more..."
                f.write(
                    f"| [Part {i + 1}](./codebase_part_{i + 1:03d}.md) | {len(bucket)} | {file_list} |\n"
                )

            f.write("\n## 🚀 Usage\n\n")
            f.write(
                "This consolidated codebase was generated using the Codebase Consolidator GUI.\n"
            )
            f.write(
                "Each markdown file contains multiple source files with enhanced formatting:\n\n"
            )
            f.write(
                f"- **Syntax highlighting** optimized for `{self.syntax_theme}` theme\n"
            )
            f.write(
                f"- **Line numbers** {'included' if self.line_numbers else 'excluded'} for easier reference\n"
            )
            f.write(
                "- **Metadata** for each file including size and modification date\n\n"
            )

        return index_file


class QueueWriter:
    """A file-like object that writes to a Queue for GUI consumption."""

    def __init__(self, q: queue.Queue[str]):
        self.q = q

    def write(self, s: str) -> int:
        if s:
            self.q.put(s)
        return len(s)

    def flush(self) -> None:  # for compatibility
        pass


class ConsolidatorGUI(tb.Window):
    def __init__(self):
        super().__init__(title="Codebase Consolidator", themename="solar")
        self.geometry("1280x200")
        self.minsize(1280, 900)

        # state
        self._worker: Optional[threading.Thread] = None
        self._stop_flag = threading.Event()
        self._log_queue: queue.Queue[str] = queue.Queue()
        self._stdout_backup = sys.stdout
        self._stderr_backup = sys.stderr
        self._last_output_path: Optional[Path] = None
        self._tree_item_paths: dict[str, Path] = {}
        self._preview_worker: Optional[threading.Thread] = None
        # build UI
        self._build_header()
        self._build_form()
        self._build_formatting_options()
        self._build_main_content()
        self._build_actions()

        # start polling log queue
        self.after(100, self._drain_log_queue)

    def _build_header(self) -> None:
        header = tb.Frame(self, padding=(15, 10))
        header.pack(fill=X)

        title = tb.Label(
            header,
            text="📚 Codebase Consolidator",
            font=("Segoe UI", 16, "bold"),
        )
        title.pack(side=LEFT)

        # Get current theme name and available themes
        current_theme = getattr(self.style.theme, "name", "flatly")
        self.theme_var = tb.StringVar(value=current_theme)

        # Get theme names using the correct API
        try:
            # Try the newer API first
            theme_names = sorted(self.style.theme_names())
        except AttributeError:
            # Fallback to a default list of common ttkbootstrap themes
            theme_names = sorted(
                [
                    "cosmo",
                    "flatly",
                    "journal",
                    "litera",
                    "lumen",
                    "minty",
                    "pulse",
                    "sandstone",
                    "united",
                    "yeti",
                    "morph",
                    "simplex",
                    "cerculean",
                    "solar",
                    "superhero",
                    "darkly",
                    "cyborg",
                    "vapor",
                ]
            )

        theme_cb = tb.Combobox(
            header,
            textvariable=self.theme_var,
            values=theme_names,
            width=18,
            state="readonly",
        )
        theme_cb.pack(side=RIGHT, padx=(10, 0))
        theme_cb.bind("<<ComboboxSelected>>", self._on_theme_change)

        theme_lbl = tb.Label(header, text="Theme:")
        theme_lbl.pack(side=RIGHT)

    def _build_form(self) -> None:
        frm = tb.Labelframe(self, text="Settings", padding=10)
        frm.pack(fill=X, padx=12, pady=(0, 8))

        # Codebase directory
        row1 = tb.Frame(frm)
        row1.pack(fill=X, pady=5)
        tb.Label(row1, text="Codebase Directory:", width=20).pack(side=LEFT)
        self.codebase_var = tb.StringVar()
        self.codebase_entry = tb.Entry(row1, textvariable=self.codebase_var)
        self.codebase_entry.pack(side=LEFT, fill=X, expand=YES)
        tb.Button(
            row1, text="Browse", bootstyle=SECONDARY, command=self._browse_codebase
        ).pack(side=LEFT, padx=(8, 0))

        # Output directory
        row2 = tb.Frame(frm)
        row2.pack(fill=X, pady=5)
        tb.Label(row2, text="Output Directory:", width=20).pack(side=LEFT)
        self.output_var = tb.StringVar()
        self.output_entry = tb.Entry(row2, textvariable=self.output_var)
        self.output_entry.pack(side=LEFT, fill=X, expand=YES)
        tb.Button(
            row2, text="Browse", bootstyle=SECONDARY, command=self._browse_output
        ).pack(side=LEFT, padx=(8, 0))

        # Number of files
        row3 = tb.Frame(frm)
        row3.pack(fill=X, pady=5)
        tb.Label(row3, text="Target # of files:", width=20).pack(side=LEFT)
        self.num_files_var = tb.IntVar(value=50)
        self.num_files_spin = tb.Spinbox(
            row3,
            from_=1,
            to=5000,
            textvariable=self.num_files_var,
            width=10,
        )
        self.num_files_spin.pack(side=LEFT)

        # Max Part Size (KB)
        tb.Label(row3, text="Max Part Size (KB):", width=20).pack(side=LEFT, padx=(20, 0))
        self.max_size_var = tb.IntVar(value=500)
        self.max_size_spin = tb.Spinbox(
            row3,
            from_=10,
            to=10000,
            textvariable=self.max_size_var,
            width=10,
        )
        self.max_size_spin.pack(side=LEFT)

        # Custom folder name
        row4 = tb.Frame(frm)
        row4.pack(fill=X, pady=5)
        tb.Label(row4, text="Custom Folder Name:", width=20).pack(side=LEFT)
        self.folder_var = tb.StringVar()
        self.folder_entry = tb.Entry(row4, textvariable=self.folder_var)
        self.folder_entry.pack(side=LEFT, fill=X, expand=YES)

        # Verbose
        row5 = tb.Frame(frm)
        row5.pack(fill=X, pady=5)
        self.verbose_var = tb.BooleanVar(value=False)
        tb.Checkbutton(
            row5, text="Verbose", variable=self.verbose_var, bootstyle="round-toggle"
        ).pack(side=LEFT)

    def _build_formatting_options(self) -> None:
        frm = tb.Labelframe(self, text="Code Formatting Options", padding=10)
        frm.pack(fill=X, padx=12, pady=(0, 8))

        # Syntax highlighting theme
        row1 = tb.Frame(frm)
        row1.pack(fill=X, pady=5)
        tb.Label(row1, text="Syntax Theme:", width=20).pack(side=LEFT)
        self.syntax_theme_var = tb.StringVar(value="github")
        syntax_themes = [
            "github",
            "monokai",
            "solarized-light",
            "solarized-dark",
            "vs",
            "vs-dark",
            "atom-one-light",
            "atom-one-dark",
            "default",
            "colorful",
            "emacs",
            "friendly",
            "vim",
        ]
        self.syntax_theme_cb = tb.Combobox(
            row1,
            textvariable=self.syntax_theme_var,
            values=syntax_themes,
            width=20,
            state="readonly",
        )
        self.syntax_theme_cb.pack(side=LEFT)

        # Line numbers toggle
        row2 = tb.Frame(frm)
        row2.pack(fill=X, pady=5)
        self.line_numbers_var = tb.BooleanVar(value=True)
        tb.Checkbutton(
            row2,
            text="Include Line Numbers",
            variable=self.line_numbers_var,
            bootstyle="round-toggle",
        ).pack(side=LEFT)

        # XML Tags toggle
        self.xml_var = tb.BooleanVar(value=False)
        tb.Checkbutton(
            row2,
            text="Use XML Tags (Better for RAG)",
            variable=self.xml_var,
            bootstyle="round-toggle",
        ).pack(side=LEFT, padx=(20, 0))

        # File Tree toggle
        self.tree_var = tb.BooleanVar(value=True)
        tb.Checkbutton(
            row2,
            text="Include File Tree",
            variable=self.tree_var,
            bootstyle="round-toggle",
        ).pack(side=LEFT, padx=(20, 0))

    def _build_main_content(self) -> None:
        # Create a notebook (tabbed interface) for preview and log
        self.notebook = tb.Notebook(self)
        self.notebook.pack(fill=BOTH, expand=YES, padx=12, pady=(0, 8))

        # Preview tab
        self.preview_frame = tb.Frame(self.notebook)
        self.notebook.add(self.preview_frame, text="📋 File Preview")

        # Preview controls
        preview_controls = tb.Frame(self.preview_frame, padding=5)
        preview_controls.pack(fill=X)

        self.refresh_btn = tb.Button(
            preview_controls,
            text="🔄 Refresh Preview",
            bootstyle=INFO,
            command=self._refresh_preview,
        )
        self.refresh_btn.pack(side=LEFT)

        self.file_count_label = tb.Label(preview_controls, text="No files loaded")
        self.file_count_label.pack(side=LEFT, padx=(10, 0))

        # File tree
        tree_frame = tb.Frame(self.preview_frame)
        tree_frame.pack(fill=BOTH, expand=YES, padx=5, pady=5)

        # Create treeview with scrollbars
        self.file_tree = ttk.Treeview(
            tree_frame, columns=("size", "type"), show="tree headings"
        )
        self.file_tree.heading("#0", text="File Path")
        self.file_tree.heading("size", text="Size")
        self.file_tree.heading("type", text="Type")
        self.file_tree.column("#0", width=400)
        self.file_tree.column("size", width=80)
        self.file_tree.column("type", width=100)

        # Scrollbars for treeview
        tree_scroll_y = tb.Scrollbar(
            tree_frame, orient="vertical", command=self.file_tree.yview
        )
        tree_scroll_x = tb.Scrollbar(
            tree_frame, orient="horizontal", command=self.file_tree.xview
        )
        self.file_tree.configure(
            yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set
        )

        # Pack scrollbars first, then treeview
        tree_scroll_y.pack(side=RIGHT, fill=Y)
        tree_scroll_x.pack(side=BOTTOM, fill=X)
        self.file_tree.pack(side=LEFT, fill=BOTH, expand=YES)
        self.file_tree.bind("<Double-1>", self._on_tree_item_double_click)

        # Log tab
        self.log_frame = tb.Frame(self.notebook)
        self.notebook.add(self.log_frame, text="📝 Processing Log")

        self.log = ScrolledText(
            self.log_frame, autohide=True, height=18, width=80, padding=2
        )
        self.log.pack(fill=BOTH, expand=YES, padx=5, pady=5)
        self._append_log(
            "Welcome! Configure your options and click 'Refresh Preview' to see which files will be processed.\n"
        )

    def _build_actions(self) -> None:
        act = tb.Frame(self, padding=(12, 0))
        act.pack(fill=X)

        self.run_btn = tb.Button(
            act, text="Run Consolidation", bootstyle=SUCCESS, command=self._on_run
        )
        self.run_btn.pack(side=LEFT)

        self.stop_btn = tb.Button(
            act, text="Stop", bootstyle=DANGER, state=DISABLED, command=self._on_stop
        )
        self.stop_btn.pack(side=LEFT, padx=(8, 0))

        self.open_btn = tb.Button(
            act,
            text="Open Output Folder",
            bootstyle=INFO,
            state=DISABLED,
            command=self._open_output,
        )
        self.open_btn.pack(side=LEFT, padx=(8, 0))

        self.prog = tb.Progressbar(act, mode="indeterminate")
        self.prog.pack(side=RIGHT, fill=X, expand=YES)

    # UI callbacks
    def _on_theme_change(self, _evt=None):
        self.style.theme_use(self.theme_var.get())

    def _browse_codebase(self):
        path = filedialog.askdirectory(title="Select Codebase Directory")
        if path:
            self.codebase_var.set(path)

    def _browse_output(self):
        path = filedialog.askdirectory(title="Select Output Base Directory")
        if path:
            self.output_var.set(path)

    def _refresh_preview(self):
        """Refresh the file preview tree."""
        codebase = self.codebase_var.get().strip()
        if not codebase:
            Messagebox.show_error(
                "Please select a codebase directory first.", "Missing Input"
            )
            return

        codebase_path = Path(codebase).expanduser()
        if not codebase_path.exists() or not codebase_path.is_dir():
            Messagebox.show_error(
                "The selected codebase directory is invalid.", "Invalid Input"
            )
            return

        if self._preview_worker and self._preview_worker.is_alive():
            Messagebox.show_info(
                "A preview refresh is already running. Please wait.",
                "Refresh In Progress",
            )
            return

        self.refresh_btn.configure(state=DISABLED)
        self.file_count_label.configure(text="Scanning codebase...")

        self._preview_worker = threading.Thread(
            target=self._run_preview_worker,
            args=(codebase_path,),
            daemon=True,
        )
        self._preview_worker.start()

    def _run_preview_worker(self, codebase_path: Path):
        try:
            consolidator = CodebaseConsolidator(str(codebase_path), 1)
            files = consolidator._collect_files()
            file_data: List[Tuple[Path, int, str]] = []
            for file_path in files:
                size = consolidator._get_file_size(file_path)
                language = consolidator._get_language_from_extension(file_path)
                file_data.append((file_path, size, language))
        except Exception as e:
            self.after(0, lambda err=e: self._handle_preview_error(err))
            return

        self.after(
            0,
            lambda: self._populate_preview_tree(codebase_path, file_data),
        )

    def _handle_preview_error(self, error: Exception):
        Messagebox.show_error(f"Error scanning directory:\n{error}", "Preview Error")
        self.refresh_btn.configure(state=NORMAL)
        self.file_count_label.configure(text="Preview unavailable")
        self._preview_worker = None

    def _populate_preview_tree(
        self, codebase_path: Path, file_data: List[Tuple[Path, int, str]]
    ):
        # Clear existing tree
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        self._tree_item_paths.clear()

        dir_nodes: dict[str, str] = {}

        for file_path, file_size, file_type in file_data:
            rel_path = file_path.relative_to(codebase_path)
            parts = rel_path.parts

            # Create directory nodes if they don't exist
            current_path = ""
            parent = ""

            for part in parts[:-1]:
                current_path = str(Path(current_path) / part) if current_path else part

                if current_path not in dir_nodes:
                    node_id = self.file_tree.insert(
                        parent,
                        "end",
                        text=f"📁 {part}",
                        values=("", "Directory"),
                        open=True,
                    )
                    dir_nodes[current_path] = node_id
                    node_path = codebase_path / Path(current_path)
                    self._tree_item_paths[node_id] = node_path
                parent = dir_nodes[current_path]

            # Format file size string
            if file_size < 1024:
                size_str = f"{file_size} B"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size / 1024:.1f} KB"
            else:
                size_str = f"{file_size / (1024 * 1024):.1f} MB"

            item_id = self.file_tree.insert(
                parent,
                "end",
                text=f"📄 {parts[-1]}",
                values=(size_str, file_type),
            )
            self._tree_item_paths[item_id] = file_path

        file_count = len(file_data)
        self.file_count_label.configure(
            text=f"Found {file_count} file{'s' if file_count != 1 else ''} to process"
        )
        self.notebook.select(self.preview_frame)
        self.refresh_btn.configure(state=NORMAL)
        self._preview_worker = None

    def _on_tree_item_double_click(self, event):
        item_id = self.file_tree.identify_row(event.y)
        if not item_id:
            return

        path = self._tree_item_paths.get(item_id)
        if not path or not path.is_file():
            return

        try:
            if sys.platform.startswith("win"):
                os.startfile(str(path))  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                subprocess.run(["open", str(path)], check=False)
            else:
                subprocess.run(["xdg-open", str(path)], check=False)
        except Exception as e:
            Messagebox.show_error(f"Could not open file:\n{e}", "Open File Error")

    def _on_run(self):
        if self._worker and self._worker.is_alive():
            return

        codebase = self.codebase_var.get().strip()
        if not codebase:
            Messagebox.show_error(
                "Please select a codebase directory.", "Missing Input"
            )
            return

        codebase_path = Path(codebase).expanduser()
        if not codebase_path.exists() or not codebase_path.is_dir():
            Messagebox.show_error(
                "The selected codebase directory is invalid.", "Invalid Input"
            )
            return

        try:
            n_files = int(self.num_files_var.get())
            if n_files <= 0:
                raise ValueError
        except Exception:
            Messagebox.show_error(
                "Target number of files must be a positive integer.", "Invalid Input"
            )
            return

        output_dir = self.output_var.get().strip() or None
        if output_dir:
            out_path = Path(output_dir).expanduser()
            try:
                out_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                Messagebox.show_error(
                    f"Cannot create output directory:\n{e}", "Output Error"
                )
                return

        folder_name = self.folder_var.get().strip() or None
        max_size = self.max_size_var.get() * 1024  # Convert KB to bytes

        # Prepare run
        self._stop_flag.clear()
        self._last_output_path = None
        self.open_btn.configure(state=DISABLED)
        self.run_btn.configure(state=DISABLED)
        self.stop_btn.configure(state=NORMAL)
        self.prog.start(10)

        # Get formatting options
        syntax_theme = self.syntax_theme_var.get()
        line_numbers = self.line_numbers_var.get()
        use_xml = self.xml_var.get()
        include_tree = self.tree_var.get()

        # Switch to log tab
        self.notebook.select(self.log_frame)

        # Start worker thread
        args = (
            str(codebase_path.resolve()),
            n_files,
            output_dir,
            folder_name,
            self.verbose_var.get(),
            syntax_theme,
            line_numbers,
            use_xml,
            include_tree,
            max_size,
        )
        self._worker = threading.Thread(target=self._run_worker, args=args, daemon=True)
        self._worker.start()

    def _on_stop(self):
        if self._worker and self._worker.is_alive():
            self._stop_flag.set()
            self._append_log(
                "\n❌ Stop requested. Waiting for current step to finish...\n"
            )

    def _open_output(self):
        if not self._last_output_path:
            return
        path = str(self._last_output_path)
        try:
            if sys.platform.startswith("win"):
                os.startfile(path)  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                subprocess.run(["open", path], check=False)
            else:
                subprocess.run(["xdg-open", path], check=False)
        except Exception as e:
            Messagebox.show_error(f"Could not open folder:\n{e}", "Open Error")

    # Worker logic
    def _run_worker(
        self,
        codebase_path: str,
        n_files: int,
        output_dir: Optional[str],
        folder_name: Optional[str],
        verbose: bool,
        syntax_theme: str,
        line_numbers: bool,
        use_xml: bool,
        include_tree: bool,
        max_size: int,
    ):
        # Redirect stdout/stderr to GUI queue
        qwriter = QueueWriter(self._log_queue)
        sys.stdout = qwriter
        sys.stderr = qwriter

        try:
            print("🚀 Codebase Consolidator GUI")
            print("=" * 50)
            print(f"🎨 Using syntax theme: {syntax_theme}")
            print(f"🔢 Line numbers: {'enabled' if line_numbers else 'disabled'}")
            print(f"🏷️ XML Output: {'enabled' if use_xml else 'disabled'}")
            print(f"🌳 File Tree: {'enabled' if include_tree else 'disabled'}")
            print(f"📏 Max Part Size: {max_size / 1024:.1f} KB")

            consolidator = EnhancedCodebaseConsolidator(
                codebase_path,
                n_files,
                syntax_theme,
                line_numbers,
                use_xml=use_xml,
                include_tree=include_tree,
                max_part_size=max_size,
            )
            result = consolidator.consolidate(output_dir, folder_name)

            self._last_output_path = Path(result) if result else None

        except KeyboardInterrupt:
            print("\n❌ Operation cancelled by user")
        except Exception as e:
            print(f"❌ Error: {e}")
            if verbose:
                import traceback

                traceback.print_exc()
        finally:
            # Restore stdout/stderr
            sys.stdout = self._stdout_backup
            sys.stderr = self._stderr_backup
            self.after(0, self._on_worker_done)

    def _on_worker_done(self):
        self.prog.stop()
        self.run_btn.configure(state=NORMAL)
        self.stop_btn.configure(state=DISABLED)
        if self._last_output_path:
            self.open_btn.configure(state=NORMAL)

    # Logging helpers
    def _append_log(self, text: str) -> None:
        self.log.insert(END, text)
        self.log.see(END)

    def _drain_log_queue(self):
        try:
            while True:
                chunk = self._log_queue.get_nowait()
                self._append_log(chunk)
        except queue.Empty:
            pass
        self.after(100, self._drain_log_queue)


def main():
    app = ConsolidatorGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
