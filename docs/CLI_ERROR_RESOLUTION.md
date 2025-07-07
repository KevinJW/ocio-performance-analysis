# CLI Error Resolution

## Issue Description

The `scripts/ocio_cli.py` script was failing with a `TypeError` when running any command:

```
TypeError: OCIOTestParser.parse_directory() takes 2 positional arguments but 3 were given
```

## Root Cause

The issue was caused by incorrect method calls in the CLI script after the code restructuring:

1. **Parser Method Signature Mismatch**: The `parse_directory` method in `OCIOTestParser` only accepts one parameter (`directory_path`) but was being called with two parameters (`test_dir` and `output_file`).

2. **Analyzer Constructor Missing Parameter**: The `OCIOAnalyzer` class constructor requires a `csv_file` parameter, but was being instantiated without any arguments.

3. **Incorrect Method Names**: The CLI was calling non-existent methods:
   - `analyzer.analyze_from_csv()` instead of `analyzer.run_full_analysis()`
   - `viewer.view_charts()` instead of `viewer.view_all_charts()`

## Solution

### 1. Fixed Parser Method Call

**Before:**
```python
parser.parse_directory(test_dir, output_file)
```

**After:**
```python
results = parser.parse_directory(test_dir)
parser.save_to_csv(results, output_file)
```

The `parse_directory` method returns a list of results, which must then be saved using the separate `save_to_csv` method.

### 2. Fixed Analyzer Constructor

**Before:**
```python
analyzer = OCIOAnalyzer()
```

**After:**
```python
analyzer = OCIOAnalyzer(csv_file)
```

The `OCIOAnalyzer` constructor requires the CSV file path as a parameter.

### 3. Fixed Method Names

**Before:**
```python
analyzer.analyze_from_csv(csv_file, output_dir)
viewer = OCIOChartViewer()
viewer.view_charts(output_dir)
```

**After:**
```python
analyzer.run_full_analysis(output_dir)
viewer = OCIOChartViewer(output_dir)
viewer.view_all_charts()
```

Used the correct method names and constructor parameters.

## Testing

All CLI commands now work correctly:

- `python scripts/ocio_cli.py parse` - Parses OCIO test files to CSV
- `python scripts/ocio_cli.py analyze` - Runs comprehensive analysis
- `python scripts/ocio_cli.py view` - Views generated charts
- `python scripts/ocio_cli.py all` - Runs complete pipeline
- `python scripts/ocio_cli.py --help` - Shows help information

## Files Modified

- `scripts/ocio_cli.py` - Fixed method calls and constructor parameters

## Validation

- All CLI commands execute without errors
- All unit tests continue to pass
- No linting issues remain in the fixed file
