#!/usr/bin/env python3
"""
Codebase Consolidator - CLI tool to combine multiple code files into organized markdown files
"""

import argparse
import fnmatch
from pathlib import Path
from typing import List, Set
import sys
from datetime import datetime


class CodebaseConsolidator:
    def __init__(self, root_path: str, target_files: int = 50):
        self.root_path = Path(root_path)
        self.target_files = target_files
        self.ignored_patterns = self._load_gitignore()

    def _load_gitignore(self) -> Set[str]:
        """Load patterns from .gitignore file"""
        patterns = set()
        gitignore_path = self.root_path / ".gitignore"

        if gitignore_path.exists():
            with open(gitignore_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        patterns.add(line)

        # Add common patterns to ignore
        patterns.update(
            {
                ".git/*",
                ".git/**",
                "__pycache__/*",
                "__pycache__/**",
                "*.pyc",
                "*.pyo",
                "*.pyd",
                ".DS_Store",
                "Thumbs.db",
                "node_modules/*",
                "node_modules/**",
                ".env",
                ".venv/*",
                ".venv/**",
                "*.log",
                "*.tmp",
                ".next/*",
                ".next/**",
                ".next",
            }
        )

        return patterns

    def _is_ignored(self, file_path: Path) -> bool:
        """Check if file should be ignored based on .gitignore patterns"""
        relative_path = file_path.relative_to(self.root_path)
        path_str = str(relative_path)

        for pattern in self.ignored_patterns:
            # Handle directory patterns
            if pattern.endswith("/"):
                if any(part == pattern[:-1] for part in relative_path.parts):
                    return True
            # Handle glob patterns
            elif fnmatch.fnmatch(path_str, pattern) or fnmatch.fnmatch(
                file_path.name, pattern
            ):
                return True
            # Handle ** patterns
            elif "**" in pattern:
                if fnmatch.fnmatch(path_str, pattern):
                    return True

        return False

    def _is_text_file(self, file_path: Path) -> bool:
        """Determine if a file is likely a text file"""
        text_extensions = {
            ".py",
            ".js",
            ".ts",
            ".jsx",
            ".tsx",
            ".html",
            ".css",
            ".scss",
            ".sass",
            ".java",
            ".cpp",
            ".c",
            ".h",
            ".hpp",
            ".cs",
            ".php",
            ".rb",
            ".go",
            ".rs",
            ".swift",
            ".kt",
            ".scala",
            ".sh",
            ".bash",
            ".zsh",
            ".fish",
            ".sql",
            ".json",
            ".xml",
            ".yaml",
            ".yml",
            ".toml",
            ".ini",
            ".cfg",
            ".md",
            ".txt",
            ".rst",
            ".tex",
            ".vue",
            ".svelte",
            ".dart",
            ".r",
            ".pl",
            ".pm",
            ".lua",
            ".vim",
            ".el",
            ".clj",
            ".hs",
            ".ml",
            ".fs",
            ".dockerfile",
            ".makefile",
            ".cmake",
            ".gradle",
            ".maven",
        }

        # Check extension
        if file_path.suffix.lower() in text_extensions:
            return True

        # Check for files without extensions that are commonly text
        if not file_path.suffix:
            text_names = {"dockerfile", "makefile", "readme", "license", "changelog"}
            if file_path.name.lower() in text_names:
                return True

        # Try to read a small portion to check if it's text
        try:
            with open(file_path, "r", encoding="utf-8", errors="strict") as f:
                f.read(1024)  # Try to read first 1KB
            return True
        except (UnicodeDecodeError, IOError):
            return False

    def _collect_files(self) -> List[Path]:
        """Collect all text files that should be processed"""
        files = []

        for file_path in self.root_path.rglob("*"):
            if file_path.is_file() and not self._is_ignored(file_path):
                if self._is_text_file(file_path):
                    files.append(file_path)

        return sorted(files)

    def _get_file_size(self, file_path: Path) -> int:
        """Get file size in bytes"""
        try:
            return file_path.stat().st_size
        except OSError:
            return 0

    def _distribute_files(self, files: List[Path]) -> List[List[Path]]:
        """Distribute files across target number of output files"""
        if not files:
            return []

        # Calculate total size
        total_size = sum(self._get_file_size(f) for f in files)
        target_size_per_file = total_size // self.target_files

        buckets = []
        current_bucket = []
        current_size = 0

        for file_path in files:
            file_size = self._get_file_size(file_path)

            # If adding this file would exceed target size and we have files in current bucket
            if current_size + file_size > target_size_per_file and current_bucket:
                buckets.append(current_bucket)
                current_bucket = [file_path]
                current_size = file_size
            else:
                current_bucket.append(file_path)
                current_size += file_size

        # Add the last bucket if it has files
        if current_bucket:
            buckets.append(current_bucket)

        # If we have too few buckets, redistribute
        while len(buckets) < self.target_files and len(buckets) > 1:
            # Find the largest bucket and split it
            largest_idx = max(range(len(buckets)), key=lambda i: len(buckets[i]))
            largest_bucket = buckets[largest_idx]

            if len(largest_bucket) >= 2:
                mid = len(largest_bucket) // 2
                bucket1 = largest_bucket[:mid]
                bucket2 = largest_bucket[mid:]
                buckets[largest_idx] = bucket1
                buckets.append(bucket2)
            else:
                break

        return buckets[: self.target_files]  # Ensure we don't exceed target

    def _read_file_content(self, file_path: Path) -> str:
        """Read file content safely"""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except IOError as e:
            return f"Error reading file: {e}"

    def _get_language_from_extension(self, file_path: Path) -> str:
        """Get language identifier for syntax highlighting"""
        ext_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".jsx": "jsx",
            ".tsx": "tsx",
            ".html": "html",
            ".css": "css",
            ".scss": "scss",
            ".sass": "sass",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
            ".h": "c",
            ".hpp": "cpp",
            ".cs": "csharp",
            ".php": "php",
            ".rb": "ruby",
            ".go": "go",
            ".rs": "rust",
            ".swift": "swift",
            ".kt": "kotlin",
            ".scala": "scala",
            ".sh": "bash",
            ".bash": "bash",
            ".zsh": "zsh",
            ".sql": "sql",
            ".json": "json",
            ".xml": "xml",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".toml": "toml",
            ".md": "markdown",
            ".txt": "text",
            ".vue": "vue",
            ".dart": "dart",
            ".r": "r",
            ".pl": "perl",
            ".lua": "lua",
        }

        return ext_map.get(file_path.suffix.lower(), "text")

    def _generate_output_folder_name(self, custom_name: str = None) -> str:
        """Generate a descriptive output folder name"""
        if custom_name:
            return custom_name

        # Get the codebase folder name
        codebase_name = self.root_path.name
        if codebase_name == "." or codebase_name == "":
            codebase_name = Path.cwd().name

        # Add timestamp and file count
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{codebase_name}_consolidated_{self.target_files}files_{timestamp}"

    def consolidate(self, output_base_dir: str = None, custom_folder_name: str = None):
        """Main method to consolidate the codebase"""
        print(f"🔍 Scanning codebase in: {self.root_path.absolute()}")

        # Collect files
        files = self._collect_files()
        print(f"📁 Found {len(files)} files to process")

        if not files:
            print("❌ No files found to process!")
            return

        # Generate output folder name
        folder_name = self._generate_output_folder_name(custom_folder_name)

        # Determine output directory
        if output_base_dir:
            output_path = Path(output_base_dir) / folder_name
        else:
            # Default to current working directory
            output_path = Path.cwd() / folder_name

        # Create output directory
        output_path.mkdir(parents=True, exist_ok=True)
        print(f"📂 Output directory: {output_path.absolute()}")

        # Distribute files
        file_buckets = self._distribute_files(files)
        actual_files = len(file_buckets)

        print(f"📝 Creating {actual_files} consolidated markdown files...")

        # Generate consolidated files
        for i, bucket in enumerate(file_buckets):
            output_file = output_path / f"codebase_part_{i + 1:03d}.md"

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(f"# Codebase Part {i + 1} of {actual_files}\n\n")
                f.write(f"**Source:** `{self.root_path.absolute()}`  \n")
                f.write(
                    f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n"
                )
                f.write(f"**Files in this part:** {len(bucket)}  \n\n")
                f.write("## Table of Contents\n\n")

                # Write table of contents
                for j, file_path in enumerate(bucket):
                    rel_path = file_path.relative_to(self.root_path)
                    anchor = (
                        rel_path.as_posix()
                        .replace("/", "-")
                        .replace(".", "-")
                        .replace("_", "-")
                        .lower()
                    )
                    f.write(f"{j + 1}. [{rel_path}](#{anchor})\n")

                f.write("\n---\n\n")

                # Write file contents
                for file_path in bucket:
                    rel_path = file_path.relative_to(self.root_path)
                    content = self._read_file_content(file_path)
                    language = self._get_language_from_extension(file_path)
                    anchor = (
                        rel_path.as_posix()
                        .replace("/", "-")
                        .replace(".", "-")
                        .replace("_", "-")
                        .lower()
                    )

                    f.write(f"## {rel_path} {{#{anchor}}}\n\n")
                    f.write(f"**File Path:** `{rel_path}`  \n")
                    f.write(
                        f"**File Size:** {self._get_file_size(file_path)} bytes  \n"
                    )
                    f.write(f"**Language:** {language}  \n")
                    f.write(
                        f"**Last Modified:** {datetime.fromtimestamp(file_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                    )

                    f.write(f"```{language}\n")
                    f.write(content)
                    if not content.endswith("\n"):
                        f.write("\n")
                    f.write(f"```\n\n---\n\n")

            print(f"   ✅ Created: codebase_part_{i + 1:03d}.md ({len(bucket)} files)")

        # Create index file
        index_file = output_path / "README.md"
        with open(index_file, "w", encoding="utf-8") as f:
            f.write("# 📚 Consolidated Codebase\n\n")
            f.write(f"**Source Directory:** `{self.root_path.absolute()}`  \n")
            f.write(
                f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n"
            )
            f.write(f"**Total Files Processed:** {len(files)}  \n")
            f.write(f"**Target Output Files:** {self.target_files}  \n")
            f.write(f"**Actual Output Files:** {actual_files}  \n\n")

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

            f.write(f"\n## 🚀 Usage\n\n")
            f.write(
                f"This consolidated codebase was generated using the Codebase Consolidator tool.\n"
            )
            f.write(
                f"Each markdown file contains multiple source files with syntax highlighting and metadata.\n\n"
            )
            f.write(f"**Command used:**\n```bash\n")
            f.write(
                f"codebase-consolidator {self.root_path.absolute()} -n {self.target_files}\n```\n"
            )

        print(f"\n🎉 Consolidation complete!")
        print(f"📂 Output directory: {output_path.absolute()}")
        print(f"📋 Index file: {index_file}")
        print(f"📊 Summary: {len(files)} files → {actual_files} markdown files")

        return output_path.absolute()


def main():
    parser = argparse.ArgumentParser(
        prog="codebase-consolidator",
        description="🚀 Consolidate your entire codebase into organized markdown files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/my-project                    # Consolidate into 50 files
  %(prog)s /path/to/my-project -n 300             # Consolidate into 300 files  
  %(prog)s ~/code/my-app -o ~/Desktop             # Output to Desktop
  %(prog)s . --folder-name my-analysis           # Custom folder name
  
The tool will create a timestamped folder with descriptive naming like:
  my-project_consolidated_50files_20240925_143022/
        """,
    )

    parser.add_argument(
        "codebase_path", help="📁 Path to the codebase directory to consolidate"
    )
    parser.add_argument(
        "-n",
        "--num-files",
        type=int,
        default=50,
        metavar="N",
        help="🔢 Target number of output files (default: 50)",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        metavar="PATH",
        help="📂 Base output directory (default: current directory)",
    )
    parser.add_argument(
        "--folder-name",
        metavar="NAME",
        help="📝 Custom output folder name (overrides auto-generated name)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="📋 Show verbose output during processing",
    )
    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")

    args = parser.parse_args()

    # Validate inputs
    if args.num_files <= 0:
        print("❌ Error: Number of files must be positive")
        sys.exit(1)

    codebase_path = Path(args.codebase_path).expanduser().resolve()
    if not codebase_path.exists():
        print(f"❌ Error: Path '{codebase_path}' does not exist")
        sys.exit(1)

    if not codebase_path.is_dir():
        print(f"❌ Error: Path '{codebase_path}' is not a directory")
        sys.exit(1)

    # Validate output directory if provided
    if args.output_dir:
        output_base = Path(args.output_dir).expanduser().resolve()
        if not output_base.exists():
            try:
                output_base.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                print(f"❌ Error: Cannot create output directory '{output_base}': {e}")
                sys.exit(1)
        output_dir = str(output_base)
    else:
        output_dir = None

    print("🚀 Codebase Consolidator v1.0.0")
    print("=" * 50)

    try:
        # Create consolidator and run
        consolidator = CodebaseConsolidator(str(codebase_path), args.num_files)
        result_path = consolidator.consolidate(output_dir, args.folder_name)

        print("\n" + "=" * 50)
        print("✨ Success! Your codebase has been consolidated.")
        print(f"📁 Find your files at: {result_path}")

    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
