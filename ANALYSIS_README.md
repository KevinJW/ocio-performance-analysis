# OCIO Test Results Analysis

This directory contains analysis scripts and results for comparing OCIO (OpenColorIO) test performance across different operating system releases.

## 📊 Analysis Overview

The analysis script (`ocio_analysis.py`) processes the OCIO test results CSV file to:

1. **Summarize test runs** by filename using mean averages for numerical columns
2. **Identify CPU models** that were tested on multiple OS releases (r7 and r9)
3. **Generate visualizations** comparing OS performance effects
4. **Create detailed reports** with performance comparisons

## 🔍 Key Findings

### Performance Improvements with r9 OS Release

Our analysis of 3 CPU models tested on both r7 and r9 OS releases shows **consistent and significant performance improvements** with r9:

| CPU Model | r7 Performance | r9 Performance | Improvement |
|-----------|----------------|----------------|-------------|
| Intel(R) Core(TM) i9-9900K CPU @ 3.60GHz | 1341.8 ms | 559.6 ms | **58.3%** |
| Intel(R) Xeon(R) CPU E5-2687W v3 @ 3.10GHz | 1686.5 ms | 767.4 ms | **54.5%** |
| Intel(R) Xeon(R) W-2295 CPU @ 3.00GHz | 1281.3 ms | 530.1 ms | **58.6%** |

### Overall Summary
- **Average r7 performance**: 1436.5 ms
- **Average r9 performance**: 619.0 ms  
- **Overall improvement**: **56.9%**

## 📁 Generated Files

### Analysis Results (`analysis_results/` directory)

1. **`summary_analysis.png`** - Overall performance summary visualizations
2. **`os_comparison_*.png`** - Individual CPU model OS comparisons (3 files)
3. **`os_comparison_report.txt`** - Detailed text report with all findings
4. **`file_summaries.csv`** - Summarized data grouped by filename
5. **`os_comparisons.csv`** - CPU-OS combination comparison data

### Scripts

1. **`ocio_analysis.py`** - Main analysis script
2. **`show_findings.py`** - Quick summary of key findings
3. **`view_plots.py`** - Script to view generated visualizations

## 🚀 Usage

### Run Full Analysis
```bash
python ocio_analysis.py
```

### View Quick Summary
```bash
python show_findings.py
```

### View Generated Plots
```bash
python view_plots.py
```

## 📈 Technical Details

### Analysis Methodology

1. **Data Grouping**: Test results are grouped by filename to calculate mean averages for:
   - Minimum execution time
   - Maximum execution time  
   - Average execution time
   - Standard deviation
   - Median execution time

2. **CPU-OS Mapping**: Files are analyzed to identify:
   - CPU model (extracted from system info in test files)
   - OS release (r7/r9 extracted from filename)
   - Performance metrics for each combination

3. **Comparison Logic**: For each CPU model found on multiple OS releases:
   - Calculate mean performance metrics
   - Compute percentage improvements/regressions
   - Generate comparison visualizations

### Data Quality

- **Total test files analyzed**: 12
- **CPU models with multi-OS data**: 3
- **Total test operations**: 1,236
- **OS releases compared**: r7 vs r9

## 🎯 Conclusions

The analysis reveals **significant and consistent performance improvements** when upgrading from r7 to r9 OS release:

1. **Universal Improvement**: All 3 CPU models showed substantial performance gains with r9
2. **Consistent Range**: Performance improvements range from 54% to 59%
3. **OS-Level Optimizations**: The consistency across different CPU architectures suggests fundamental OS-level optimizations in r9
4. **Practical Impact**: Average performance nearly doubles (56.9% improvement), representing a major performance upgrade

This suggests that upgrading to r9 OS release would provide substantial performance benefits for OCIO-based color processing workflows.
