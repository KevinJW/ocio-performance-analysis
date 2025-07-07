# ACES Version Analysis Summary

## Overview

All OCIO test result comparisons have been successfully updated to split data by
ACES version (ACES 1.0 vs ACES 2.0), highlighting the significant performance
differences between these two color space conversion standards.

## Key Findings

### Overall ACES Version Performance

- **ACES 1.0**: 278.07 ± 64.80 ms (much faster)
- **ACES 2.0**: 2004.97 ± 835.67 ms (significantly slower)
- **Performance Difference**: ACES 2.0 is 621.0% slower than ACES 1.0
- **Recommendation**: ACES 1.0 provides much better performance for color space
  conversions

### OCIO Version Performance by ACES Version

- **Fastest combination**: OCIO 2.4.2 + ACES 1.0 (275.5 ms)
- **Slowest combination**: OCIO 2.4.1 + ACES 2.0 (2172.6 ms)
- **Performance spread**: 688.5% difference between fastest and slowest

## Updated Analysis Components

### 1. Enhanced Data Processing

- Added ACES version categorization to all data loading
- Updated grouping logic to include ACES version in all summaries
- Modified comparison methods to split by ACES version

### 2. Updated Visualization Methods

#### Summary Plots (`summary_analysis.png`)

- **6 subplots** showing comprehensive ACES version analysis:
  1. OS release performance by ACES version (grouped bars)
  2. CPU model performance by ACES version (horizontal bars)
  3. Performance distribution histogram (ACES 1.0 vs 2.0)
  4. Performance heatmap for ACES 1.0 (CPU vs OS)
  5. Performance heatmap for ACES 2.0 (CPU vs OS)
  6. Overall ACES version comparison with percentage difference

#### OS Comparison Plots

- **Enhanced CPU-specific plots** with ACES version splitting:
  1. Performance comparison by OS release and ACES version
  2. File count comparison by ACES version
  3. ACES 2.0 vs ACES 1.0 performance difference by OS
  4. Summary statistics panel

#### OCIO Version Comparison Plots

- **4 subplots** showing OCIO version performance split by ACES version:
  1. Mean performance by OCIO version and ACES version
  2. File count by OCIO version and ACES version
  3. ACES 2.0 vs ACES 1.0 performance difference by OCIO version
  4. Overall ACES version performance summary

#### Detailed CPU+OS OCIO Comparison

- **New plot**: `ocio_241_vs_242_cpu_os_aces_comparison.png`
- **Side-by-side comparison** of ACES 1.0 vs ACES 2.0 performance
- **OCIO 2.4.1 vs 2.4.2** comparison within each ACES version
- **Short CPU/OS labels** for easy reading

### 3. Enhanced Reports

#### OS Comparison Report (`os_comparison_report.txt`)

- **ACES version performance overview**
- **CPU model comparisons split by ACES version**
- **Performance analysis within each ACES version**
- **Better performing OS identification per ACES version**

#### OCIO Version Comparison Report (`ocio_version_comparison_report.txt`)

- **Overall ACES version performance summary**
- **Detailed OCIO version analysis by ACES version**
- **Performance comparisons within each ACES version**
- **Fastest/slowest combination identification**

## Data Files Generated

### CSV Files

- `file_summaries.csv`: Updated with ACES version column
- `os_comparisons.csv`: OS comparisons split by ACES version
- `ocio_version_comparisons.csv`: OCIO version comparisons by ACES version
- `detailed_ocio_comparisons.csv`: Detailed OCIO comparisons with ACES info

### Visualization Files

- `summary_analysis.png`: 6-panel comprehensive analysis
- `ocio_version_comparison.png`: 4-panel OCIO version analysis
- `ocio_241_vs_242_cpu_os_aces_comparison.png`: Side-by-side ACES comparison
- `os_comparison_*_CPU_*.png`: Enhanced CPU-specific OS comparisons (3 files)

## Key Insights

### Performance Impact of ACES Version

1. **ACES 1.0 is consistently faster** across all CPU models and OS releases
2. **ACES 2.0 introduces significant overhead** (6x slower on average)
3. **Performance gap is consistent** across different OCIO versions
4. **OS optimization (r7→r9) benefits both ACES versions** but doesn't close the
   gap

### Recommendation

- **For performance-critical applications**: Use ACES 1.0 when possible
- **For compatibility/features**: ACES 2.0 may be required despite performance
  cost
- **OS upgrade benefits**: r9 provides significant improvements for both ACES
  versions
- **OCIO version**: 2.4.2 generally performs better than 2.4.1 in both ACES
  versions

## Technical Implementation

- All comparison methods now group by `['cpu_model', 'os_release',
  'aces_version']`
- Visualization methods create grouped/side-by-side charts for ACES comparison
- Reports include ACES version performance analysis sections
- Data processing maintains backward compatibility while adding ACES insights
