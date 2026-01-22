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
    def __init__(
        self,
        root_path: str,
        target_files: int = 50,
        use_xml: bool = False,
        include_tree: bool = True,
        max_part_size: int = 512000,  # Default 500KB
    ):
        self.root_path = Path(root_path)
        self.target_files = target_files
        self.use_xml = use_xml
        self.include_tree = include_tree
        self.max_part_size = max_part_size
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

        # Add comprehensive patterns to ignore common build artifacts, dependencies, and cache directories
        patterns.update(
            {
                # Version control
                ".git/*",
                ".git/**",
                ".svn/*",
                ".svn/**",
                ".hg/*",
                ".hg/**",
                ".bzr/*",
                ".bzr/**",

                # Python
                "__pycache__/*",
                "__pycache__/**",
                "*.pyc",
                "*.pyo",
                "*.pyd",
                ".pytest_cache/*",
                ".pytest_cache/**",
                ".coverage",
                ".tox/*",
                ".tox/**",
                "venv/*",
                "venv/**",
                ".venv/*",
                ".venv/**",
                "env/*",
                "env/**",
                ".env",
                "ENV/*",
                "ENV/**",
                "env.bak/*",
                "env.bak/**",
                "venv.bak/*",
                "venv.bak/**",
                "pip-log.txt",
                "pip-delete-this-directory.txt",
                ".mypy_cache/*",
                ".mypy_cache/**",
                ".dmypy.json",
                "dmypy.json",

                # Node.js / JavaScript / TypeScript
                "node_modules/*",
                "node_modules/**",
                "npm-debug.log*",
                "yarn-debug.log*",
                "yarn-error.log*",
                "lerna-debug.log*",
                ".pnpm-debug.log*",
                ".npm",
                ".yarn/*",
                ".yarn/**",
                ".pnp",
                ".pnp.js",
                ".yarn/cache",
                ".yarn/unplugged",
                ".yarn/build-state.yml",
                ".yarn/install-state.gz",
                ".pnp.*",

                # Build outputs and dist directories
                "dist/*",
                "dist/**",
                "build/*",
                "build/**",
                "out/*",
                "out/**",
                "target/*",
                "target/**",
                "bin/*",
                "bin/**",
                "obj/*",
                "obj/**",

                # Next.js
                ".next/*",
                ".next/**",
                ".next",

                # Nuxt.js
                ".nuxt/*",
                ".nuxt/**",
                ".output/*",
                ".output/**",

                # Vite
                ".vite/*",
                ".vite/**",

                # Webpack
                ".webpack/*",
                ".webpack/**",

                # Parcel
                ".parcel-cache/*",
                ".parcel-cache/**",

                # Rollup
                ".rollup.cache/*",
                ".rollup.cache/**",

                # SvelteKit
                ".svelte-kit/*",
                ".svelte-kit/**",

                # Gatsby
                ".cache/*",
                ".cache/**",
                "public/*",
                "public/**",

                # React Native
                ".expo/*",
                ".expo/**",
                ".expo-shared/*",
                ".expo-shared/**",

                # Flutter
                ".dart_tool/*",
                ".dart_tool/**",
                ".flutter-plugins",
                ".flutter-plugins-dependencies",
                ".packages",
                ".pub-cache/*",
                ".pub-cache/**",
                ".pub/*",
                ".pub/**",

                # Java / Maven / Gradle
                ".m2/*",
                ".m2/**",
                ".gradle/*",
                ".gradle/**",
                "gradle/*",
                "gradle/**",
                "gradlew",
                "gradlew.bat",

                # .NET
                "packages/*",
                "packages/**",
                "*.nupkg",
                "*.snupkg",
                ".vs/*",
                ".vs/**",

                # Go
                "vendor/*",
                "vendor/**",

                # Rust
                "target/*",
                "target/**",
                "Cargo.lock",

                # Ruby
                ".bundle/*",
                ".bundle/**",
                "vendor/bundle/*",
                "vendor/bundle/**",

                # PHP
                "vendor/*",
                "vendor/**",
                "composer.phar",

                # IDEs and editors
                ".vscode/*",
                ".vscode/**",
                ".idea/*",
                ".idea/**",
                "*.swp",
                "*.swo",
                "*~",
                ".project",
                ".classpath",
                ".c9revisions/*",
                ".c9revisions/**",
                ".settings/*",
                ".settings/**",
                "*.sublime-project",
                "*.sublime-workspace",

                # OS generated files
                ".DS_Store",
                ".DS_Store?",
                "._*",
                ".Spotlight-V100",
                ".Trashes",
                "ehthumbs.db",
                "Thumbs.db",
                "Desktop.ini",

                # Logs and temporary files
                "*.log",
                "*.tmp",
                "*.temp",
                "logs/*",
                "logs/**",
                "log/*",
                "log/**",
                "tmp/*",
                "tmp/**",
                "temp/*",
                "temp/**",

                # Database files
                "*.db",
                "*.sqlite",
                "*.sqlite3",

                # Coverage reports
                "coverage/*",
                "coverage/**",
                ".nyc_output/*",
                ".nyc_output/**",
                "lcov.info",

                # Documentation builds
                "_site/*",
                "_site/**",
                "site/*",
                "site/**",
                "docs/_build/*",
                "docs/_build/**",

                # Backup files
                "*.bak",
                "*.backup",
                "*.old",

                # Lock files (keep some, but exclude others)
                "package-lock.json",
                "yarn.lock",
                "pnpm-lock.yaml",

                # Docker
                ".dockerignore",

                # Terraform
                ".terraform/*",
                ".terraform/**",
                "*.tfstate",
                "*.tfstate.*",
                ".terraform.lock.hcl",

                # Kubernetes
                "*.kubeconfig",

                # Security and secrets
                ".env.local",
                ".env.development.local",
                ".env.test.local",
                ".env.production.local",
                "*.pem",
                "*.key",
                "*.p12",
                "*.p8",
                "*.mobileprovision",

                # Miscellaneous
                "*.pid",
                "*.seed",
                "*.pid.lock",
                ".grunt",
                "bower_components/*",
                "bower_components/**",
                ".lock-wscript",
                ".wafpickle-*",
                ".eslintcache",
                ".stylelintcache",
            }
        )

        return patterns

    def _is_ignored(self, file_path: Path) -> bool:
        """Check if file should be ignored based on .gitignore patterns"""
        relative_path = file_path.relative_to(self.root_path)
        path_str = str(relative_path).replace("\\", "/")  # Normalize path separators

        for pattern in self.ignored_patterns:
            # Handle directory patterns ending with /
            if pattern.endswith("/"):
                dir_name = pattern[:-1]
                if any(part == dir_name for part in relative_path.parts):
                    return True

            # Handle patterns with /* or /** (directory contents)
            elif pattern.endswith("/*") or pattern.endswith("/**"):
                dir_pattern = pattern.split("/")[0]
                if any(part == dir_pattern for part in relative_path.parts):
                    return True

            # Handle exact directory matches (like node_modules, .vite, etc.)
            elif "/" not in pattern and "*" not in pattern:
                if any(part == pattern for part in relative_path.parts):
                    return True

            # Handle glob patterns for filenames
            elif fnmatch.fnmatch(file_path.name, pattern):
                return True

            # Handle full path glob patterns
            elif fnmatch.fnmatch(path_str, pattern):
                return True

            # Handle ** patterns (recursive)
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

    def _generate_file_tree(self, files: List[Path]) -> str:
        """Generate a visual tree structure of the files"""
        if not files:
            return ""

        # Build a nested dictionary structure
        tree = {}
        for file_path in files:
            parts = file_path.relative_to(self.root_path).parts
            current = tree
            for part in parts:
                if part not in current:
                    current[part] = {}
                current = current[part]

        def render_tree(node, prefix=""):
            lines = []
            keys = sorted(node.keys())
            for i, key in enumerate(keys):
                is_last = i == len(keys) - 1
                connector = "└── " if is_last else "├── "

                # Check if it's a leaf (file) or branch (directory)
                if not node[key]:  # Empty dict means it's a file
                    lines.append(f"{prefix}{connector}{key}")
                else:
                    lines.append(f"{prefix}{connector}{key}/")
                    extension = "    " if is_last else "│   "
                    lines.extend(render_tree(node[key], prefix + extension))
            return lines

        return "\n".join(["."] + render_tree(tree))

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
        """Distribute files across target number of output files while respecting max size"""
        if not files:
            return []

        # Calculate total size
        total_size = sum(self._get_file_size(f) for f in files)

        # Determine target size per file (the smaller of total/target or max_part_size)
        target_size_per_file = min(total_size // self.target_files, self.max_part_size)

        # If the project is very small, ensure target_size_per_file isn't zero
        if target_size_per_file == 0:
            target_size_per_file = self.max_part_size

        buckets = []
        current_bucket = []
        current_size = 0

        for file_path in files:
            file_size = self._get_file_size(file_path)

            # If adding this file would exceed target size AND current bucket isn't empty
            # OR if current_size + file_size would exceed the hard limit max_part_size
            if (current_size + file_size > target_size_per_file and current_bucket) or \
               (current_size + file_size > self.max_part_size and current_bucket):
                buckets.append(current_bucket)
                current_bucket = [file_path]
                current_size = file_size
            else:
                current_bucket.append(file_path)
                current_size += file_size

        # Add the last bucket if it has files
        if current_bucket:
            buckets.append(current_bucket)

        # If we have too few buckets and haven't exceeded the target_files, redistribute
        # only if we don't violate max_part_size significantly
        while len(buckets) < self.target_files:
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

        return buckets[:max(self.target_files, len(buckets))]  # Allow exceeding target if needed for size constraints

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

    def _prepare_output_directory(self, output_base_dir: str = None, custom_folder_name: str = None) -> Path:
        """Create and return the output directory path"""
        folder_name = self._generate_output_folder_name(custom_folder_name)

        if output_base_dir:
            output_path = Path(output_base_dir) / folder_name
        else:
            output_path = Path.cwd() / folder_name

        output_path.mkdir(parents=True, exist_ok=True)
        return output_path

    def _write_part_header(self, f, part_num: int, total_parts: int, file_count: int, all_files: List[Path] = None):
        """Write the header for a part file"""
        f.write(f"# Codebase Part {part_num} of {total_parts}\n\n")
        f.write(f"**Source:** `{self.root_path.absolute()}`  \n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n")
        f.write(f"**Files in this part:** {file_count}  \n\n")

        if self.include_tree and all_files:
            f.write("## 🌳 File Tree\n\n")
            f.write("```text\n")
            f.write(self._generate_file_tree(all_files))
            f.write("\n```\n\n---\n\n")

    def _write_toc(self, f, bucket: List[Path]):
        """Write the Table of Contents"""
        f.write("## Table of Contents\n\n")
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

    def _format_code_block(self, content: str, language: str, file_path: Path) -> str:
        """Format the code block (hook for subclasses to override)"""
        if not content.endswith("\n"):
            content += "\n"

        if self.use_xml:
            rel_path = file_path.relative_to(self.root_path).as_posix()
            return f'<file path="{rel_path}" language="{language}">\n{content}</file>'

        return f"```{language}\n{content}```"

    def _write_file_section(self, f, file_path: Path):
        """Write a single file's content and metadata"""
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
        f.write(f"**File Size:** {self._get_file_size(file_path)} bytes  \n")
        f.write(f"**Language:** {language}  \n")
        f.write(
            f"**Last Modified:** {datetime.fromtimestamp(file_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        )

        formatted_code = self._format_code_block(content, language, file_path)
        f.write(f"{formatted_code}\n\n---\n\n")

    def _write_part_file(
        self,
        output_path: Path,
        bucket: List[Path],
        part_num: int,
        total_parts: int,
        all_files: List[Path],
    ):
        """Orchestrate writing a single part file"""
        output_file = output_path / f"codebase_part_{part_num:03d}.md"

        with open(output_file, "w", encoding="utf-8") as f:
            self._write_part_header(f, part_num, total_parts, len(bucket), all_files)
            self._write_toc(f, bucket)

            for file_path in bucket:
                self._write_file_section(f, file_path)

        print(f"   Created: codebase_part_{part_num:03d}.md ({len(bucket)} files)")

    def _create_index(self, output_path: Path, files: List[Path], file_buckets: List[List[Path]], actual_files: int):
        """Generate the README.md index file"""
        index_file = output_path / "README.md"
        with open(index_file, "w", encoding="utf-8") as f:
            f.write("# 📚 Consolidated Codebase\n\n")
            f.write(f"**Source Directory:** `{self.root_path.absolute()}`  \n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n")
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
            f.write(f"This consolidated codebase was generated using the Codebase Consolidator tool.\n")
            f.write(f"Each markdown file contains multiple source files with syntax highlighting and metadata.\n\n")
            f.write(f"**Command used:**\n```bash\n")
            f.write(f"codebase-consolidator {self.root_path.absolute()} -n {self.target_files}\n```\n")

        return index_file

    def consolidate(self, output_base_dir: str = None, custom_folder_name: str = None):
        """Main method to consolidate the codebase"""
        print(f"Scanning codebase in: {self.root_path.absolute()}")

        # Collect files
        files = self._collect_files()
        print(f"Found {len(files)} files to process")

        if not files:
            print("No files found to process!")
            return

        # Prepare output directory
        output_path = self._prepare_output_directory(output_base_dir, custom_folder_name)
        print(f"Output directory: {output_path.absolute()}")

        # Distribute files
        file_buckets = self._distribute_files(files)
        actual_files = len(file_buckets)

        print(f"Creating {actual_files} consolidated markdown files...")

        # Generate consolidated files
        for i, bucket in enumerate(file_buckets):
            self._write_part_file(output_path, bucket, i + 1, actual_files, files)

        # Create index file
        index_file = self._create_index(output_path, files, file_buckets, actual_files)

        print(f"\nConsolidation complete!")
        print(f"Output directory: {output_path.absolute()}")
        print(f"Index file: {index_file}")
        print(f"Summary: {len(files)} files -> {actual_files} markdown files")

        return output_path.absolute()


def main():
    parser = argparse.ArgumentParser(
        prog="codebase-consolidator",
        description="Consolidate your entire codebase into organized markdown files",
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
        "codebase_path", help="Path to the codebase directory to consolidate"
    )
    parser.add_argument(
        "-n",
        "--num-files",
        type=int,
        default=50,
        metavar="N",
        help="Target number of output files (default: 50)",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        metavar="PATH",
        help="Base output directory (default: current directory)",
    )
    parser.add_argument(
        "--folder-name",
        metavar="NAME",
        help="Custom output folder name (overrides auto-generated name)",
    )
    parser.add_argument(
        "--max-size",
        type=int,
        default=512000,
        metavar="BYTES",
        help="Maximum size of each output part in bytes (default: 512000)",
    )
    parser.add_argument(
        "--xml",
        action="store_true",
        help="Use XML tags <file path='...'> instead of markdown code blocks (better for RAG)",
    )
    parser.add_argument(
        "--no-tree",
        action="store_true",
        help="Do not include file tree in the output",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show verbose output during processing",
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

    print("Codebase Consolidator v1.0.0")
    print("=" * 50)

    try:
        # Create consolidator and run
        consolidator = CodebaseConsolidator(
            str(codebase_path),
            args.num_files,
            use_xml=args.xml,
            include_tree=not args.no_tree,
            max_part_size=args.max_size,
        )
        result_path = consolidator.consolidate(output_dir, args.folder_name)

        print("\n" + "=" * 50)
        print("Success! Your codebase has been consolidated.")
        print(f"Find your files at: {result_path}")

    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
