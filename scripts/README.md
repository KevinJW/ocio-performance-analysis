# OCIO Performance Analysis Scripts

This directory contains command-line utilities for the OCIO performance analysis toolkit.

## Available Scripts

### Main CLI Tool

- `ocio_cli.py` - Main command-line interface with integrated workflow

### Individual Components

- `parse_ocio_results.py` - Parse OCIO test result files to CSV
- `run_analysis.py` - Run comprehensive performance analysis
- `view_charts.py` - View generated analysis charts

### Utility Scripts

- `analyze_ocio_versions.py` - Quick OCIO version comparison
- `show_findings.py` - Display key analysis findings

## Usage

### All-in-One CLI

```bash
# Run complete analysis pipeline
python scripts/ocio_cli.py all

# Run individual steps
python scripts/ocio_cli.py parse
python scripts/ocio_cli.py analyze
python scripts/ocio_cli.py view
```

### Individual Scripts

```bash
# Parse test files
python scripts/parse_ocio_results.py

# Run analysis
python scripts/run_analysis.py

# View charts
python scripts/view_charts.py

# Show findings
python scripts/show_findings.py
```

## Directory Structure

Scripts expect the following project structure:

```text
project/
├── scripts/           # CLI scripts (this directory)
├── src/              # Python package source code
├── data/             # Test data and results
├── analysis_results/ # Generated plots and reports
├── tests/            # Unit tests
└── docs/             # Documentation
```

## Dependencies

All scripts use the core `ocio_performance_analysis` module located in `src/`.
Make sure to install dependencies with:

```bash
pip install -e .
```

Or install in development mode:

```bash
pip install -e ".[dev]"
```
