# OCIO Test Results Parser

A Python tool to parse OCIO (OpenColorIO) test result files and convert them
to CSV format for analysis.

## Features

- Parse multiple OCIO test result files in a directory
- Extract timing statistics for different operations
- Support for multiple test runs within each file
- Export results to CSV format with comprehensive data
- Type-safe implementation with full type annotations
- Comprehensive unit tests with pytest
- Proper error handling and logging

## Installation

1. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Run the parser on the OCIO_tests directory:

```bash
python ocio_parser.py
```

This will:

1. Parse all `.txt` files in the `OCIO_tests` directory
2. Extract test results including timing statistics
3. Save results to `ocio_test_results.csv`

### Programmatic Usage

```python
from pathlib import Path
from ocio_parser import OCIOTestParser

# Create parser instance
parser = OCIOTestParser()

# Parse a single file
results = parser.parse_file(Path("OCIO_tests/test_file.txt"))

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
