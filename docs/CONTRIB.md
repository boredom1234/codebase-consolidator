# Contribution Guide

Thank you for your interest in contributing to Codebase Consolidator!

## Development Workflow

1. **Clone the repository**:
   ```bash
   git clone https://github.com/boredom1234/codebase-consolidator
   cd codebase-consolidator
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install in editable mode**:
   ```bash
   pip install -e .
   ```

## Available Scripts

The project provides the following command-line entry points:

| Script | Alias | Description |
|--------|-------|-------------|
| `codebase-consolidator` | `cc` | Main CLI tool for consolidation |
| `codebase-consolidator-gui` | `cc-gui` | Graphical interface version |

## Testing Procedures

This project uses `pytest` for testing.

1. **Install test dependencies** (if any are added in the future):
   ```bash
   pip install pytest
   ```

2. **Run tests**:
   ```bash
   pytest
   ```

3. **Verify coverage**:
   Ensure all new features or bug fixes include corresponding tests in the `tests/` directory.
