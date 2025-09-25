# 📚 Codebase Consolidator

A powerful tool to consolidate entire codebases into organized markdown files, now with a beautiful GUI!

## 🚀 Features

### CLI Tool
- **Smart file detection**: Automatically identifies text files and respects .gitignore
- **Intelligent distribution**: Splits files across target number of output files
- **Rich metadata**: Includes file sizes, modification dates, and syntax highlighting
- **Comprehensive output**: Generates organized markdown with table of contents

### GUI Application ✨
- **Modern interface**: Beautiful ttkbootstrap-based GUI with theme selection
- **Preview mode**: File tree view showing exactly which files will be processed
- **Code formatting options**: Choose syntax highlighting themes and toggle line numbers
- **Live progress**: Real-time log output during processing
- **Easy navigation**: Tabbed interface with preview and log views

## 📦 Installation

```bash
# Install dependencies
pip install ttkbootstrap

# For development install
pip install -e .
```

## 🎯 Usage

### GUI Application (Recommended)
```bash
python codebase_consolidator_gui.py
```

Or after installation:
```bash
codebase-consolidator-gui
# or
cc-gui
```

### CLI Tool
```bash
python codebase-consolidator.py /path/to/codebase -n 50
```

Or after installation:
```bash
codebase-consolidator /path/to/codebase -n 50
# or
cc /path/to/codebase -n 50
```

## 🎨 GUI Features

### Preview Mode
1. Select your codebase directory
2. Click "🔄 Refresh Preview" to scan files
3. Review the file tree showing:
   - Directory structure
   - File sizes (B/KB/MB)
   - Detected file types
   - Total file count

### Code Formatting Options
- **Syntax Themes**: Choose from 13 popular themes
  - github, monokai, solarized-light, solarized-dark
  - vs, vs-dark, atom-one-light, atom-one-dark
  - default, colorful, emacs, friendly, vim
- **Line Numbers**: Toggle to include/exclude line numbers in code blocks

### Enhanced Output
- Theme information embedded in output
- Line-numbered code blocks (when enabled)
- Improved README with formatting details
- Metadata showing which options were used

## 📁 Output Structure

```
my-project_consolidated_50files_20240925_143022/
├── README.md                    # Index with formatting info
├── codebase_part_001.md        # First batch of files
├── codebase_part_002.md        # Second batch of files
└── ...                         # Additional parts
```

## 🔧 Configuration

### GUI Settings
- **Codebase Directory**: Source code location
- **Output Directory**: Where to save results (optional)
- **Target # of files**: How many markdown files to create
- **Custom Folder Name**: Override auto-generated folder name
- **Syntax Theme**: Choose highlighting theme
- **Line Numbers**: Include line numbers in code blocks
- **Verbose**: Show detailed processing information

### CLI Options
```bash
codebase-consolidator --help
```

## 🎯 Use Cases

- **Code Reviews**: Share entire codebases in readable format
- **Documentation**: Create comprehensive code documentation
- **AI Analysis**: Prepare codebases for LLM processing
- **Archival**: Create readable backups of projects
- **Learning**: Study codebases in organized format

## 🛠️ Development

The project consists of:
- `codebase-consolidator.py`: Original CLI implementation
- `codebase_consolidator.py`: Importable wrapper module
- `codebase_consolidator_gui.py`: GUI application with enhanced features
- `setup.py`: Package configuration with both CLI and GUI entry points

## 📝 License

MIT License - feel free to use and modify!
