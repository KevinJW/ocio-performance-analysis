# OCIO Performance Analysis

A Python toolkit for parsing and analyzing OCIO (OpenColorIO) performance test
results with comprehensive visualization and reporting capabilities.

## Features

- Parse multiple OCIO test result files in a directory
- Extract timing statistics for different operations
- Support for multiple test runs within each file
- Export results to CSV format with comprehensive data
- Comprehensive performance analysis with statistical insights
- Interactive chart viewing with detailed explanations
- Type-safe implementation with full type annotations
- Comprehensive unit tests with pytest
- Proper error handling and logging

## Installation

### Using pip (recommended)

```bash
pip install -e .
```

### Development installation

```bash
pip install -e ".[dev]"
```

### Manual installation

```bash
pip install -r requirements.txt
```

## Project Structure

```text
ocio-performance-analysis/
├── src/                          # Python package source code
│   └── ocio_performance_analysis/
│       ├── __init__.py
│       ├── parser.py             # OCIO test file parsing
│       ├── analyzer.py           # Performance analysis
│       └── viewer.py             # Chart visualization
├── scripts/                      # Command-line utilities
│   ├── ocio_cli.py              # Main CLI interface
│   ├── parse_ocio_results.py    # Parse test files
│   ├── run_analysis.py          # Run analysis
│   └── view_charts.py           # View charts
├── tests/                        # Unit tests
├── docs/                         # Documentation
├── data/                         # Test data and results
└── analysis_results/             # Generated plots and reports
```

## Usage

### Quick Start (All-in-One)

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
```

### Programmatic Usage

```python
from ocio_performance_analysis import OCIOTestParser, OCIOAnalyzer, OCIOChartViewer

# Parse test files
parser = OCIOTestParser()
results = parser.parse_file("data/OCIO_tests/test_file.txt")

# Run analysis
analyzer = OCIOAnalyzer()
analyzer.analyze_from_csv("data/ocio_test_results.csv", "analysis_results")

# View charts
viewer = OCIOChartViewer()
viewer.view_charts("analysis_results")
```

# Parse all files in a directory
results = parser.parse_directory(Path("OCIO_tests"))

# Save results to CSV
parser.save_to_csv(results, Path("output.csv"))
```

## Data Structure

Each test result contains the following fields:

- `file_name`: Name of the source file
- `ocio_version`: OCIO version used in the test
- `config_version`: OCIO config version
- `source_colorspace`: Source color space
- `target_colorspace`: Target color space
- `operation`: Name of the operation being tested
- `iteration_count`: Number of iterations performed
- `timing_values`: List of individual timing measurements
- `min_time`: Minimum time from all iterations
- `max_time`: Maximum time from all iterations
- `avg_time`: Average time from all iterations

## Testing

Run the test suite:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=ocio_parser
```

## File Format

The parser expects OCIO test result files with the following format:

```text
OCIO Version: 2.4.1

OCIO Config. file:    './config.ocio'
OCIO Config. version: 2.4
OCIO search_path:     

Processing statistics:

Processing from 'ACES2065-1' to '(sRGB - Display, ACES 1.0 - SDR Video)'
Create the config identifier:		For 10 iterations, it took: [11.1952, 0.000477791, 1.11995] ms
Create the context identifier:		For 10 iterations, it took: [0.001487, 0.000249889, 0.0003736] ms
...
```

## Error Handling

The parser includes robust error handling for:

- File encoding issues (tries UTF-8, falls back to Latin-1)
- Malformed timing values (skips invalid values)
- Missing data fields (uses "Unknown" defaults)
- Empty or corrupted files

## Dependencies

- `pandas`: For CSV export functionality
- `pytest`: For testing framework
- `typing-extensions`: For enhanced type annotations

## Viewing Analysis Results

### Unified Chart Viewer

Use the comprehensive chart viewer to display all generated analysis plots:

```bash
# View all charts
python view_plots.py

# View specific chart (partial matching supported)
python view_plots.py comprehensive    # ACES comparison chart
python view_plots.py merged           # OCIO 2.4.1 vs 2.4.2 comparison
python view_plots.py summary          # Summary analysis overview
python view_plots.py version          # OCIO version comparison

# List available charts
python view_plots.py --list

# Show help
python view_plots.py --help
```

The viewer provides detailed descriptions for each chart type and automatically
handles chart sizing and display.

## License

This project is provided as-is for parsing OCIO test results.
