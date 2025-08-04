# OCIO Performance Analysis Examples

This directory contains professional examples demonstrating comprehensive OCIO performance analysis using bar charts and statistical visualizations.

## 📊 Available Examples

### 1. OS Release Comparison (`os_release_comparison.py`)
**Purpose**: Analyze performance differences between OS releases (r7 vs r9)

**Generated Charts**:
- `os_comparison_overall.png` - Overall performance comparison between r7 and r9
- `os_comparison_[CPU].png` - Individual CPU performance comparisons  
- `os_improvement_summary.png` - Summary of performance improvements
- `aces_version_impact.png` - ACES version specific impact analysis

**Key Insights**:
- Shows significant performance improvements from r7 to r9
- Demonstrates ACES 1.0 vs 2.0 performance differences
- Provides CPU-specific improvement metrics

### 2. CPU Performance Analysis (`cpu_performance_analysis.py`)
**Purpose**: Comprehensive CPU performance ranking and comparison

**Generated Charts**:
- `cpu_performance_ranking.png` - CPU models ranked by performance
- `cpu_aces_comparison.png` - CPU performance by ACES version
- `cpu_performance_variability.png` - Performance consistency analysis
- `top_cpus_detailed_comparison.png` - Detailed top CPU analysis

**Key Insights**:
- Identifies best performing CPU models
- Shows performance consistency metrics
- Compares ACES version impact across CPUs

### 3. ACES Version Analysis (`aces_version_analysis.py`)
**Purpose**: Detailed analysis of ACES version performance impact

**Generated Charts**:
- `aces_overall_comparison.png` - Overall ACES version comparison
- `aces_cpu_impact.png` - ACES performance impact by CPU
- `aces_distribution_analysis.png` - Performance distribution comparison
- `aces_performance_ratios.png` - Detailed ratio analysis

**Key Insights**:
- Quantifies ACES 2.0 vs 1.0 performance differences
- Shows CPU-specific ACES impacts
- Provides statistical distribution analysis

## 🚀 Running the Examples

### Prerequisites
```bash
# Ensure you have the required dependencies
pip install -r requirements.txt

# Make sure the enhanced analysis package is available
python -c "from src.ocio_performance_analysis import OCIODataAnalyzer; print('✅ Package ready')"
```

### Running Individual Examples
```bash
# OS Release Analysis
python examples/os_release_comparison.py

# CPU Performance Analysis  
python examples/cpu_performance_analysis.py

# ACES Version Analysis
python examples/aces_version_analysis.py
```

### Running All Examples
```bash
# Run all examples sequentially
python examples/os_release_comparison.py && \
python examples/cpu_performance_analysis.py && \
python examples/aces_version_analysis.py
```

## 📈 Chart Outputs

All generated charts are saved to `examples/outputs/` directory with:
- **High Resolution**: 300 DPI for publication quality
- **Professional Styling**: Clear fonts, appropriate colors, grid lines
- **Data Labels**: Values displayed on bars for easy reading
- **Statistical Insights**: Percentages, ratios, and significance indicators

## 🎯 Business Value

These examples demonstrate how to:

1. **Performance Benchmarking**: Compare different configurations objectively
2. **Impact Assessment**: Quantify the effect of upgrades and changes
3. **Resource Planning**: Identify optimal hardware configurations
4. **Trend Analysis**: Track performance improvements over time
5. **Decision Support**: Provide data-driven insights for technical decisions

## 📊 Chart Types

- **Bar Charts**: Clear comparison of means, medians, and counts
- **Horizontal Bars**: Better for long labels (CPU names)
- **Grouped Bars**: Side-by-side comparisons
- **Color Coding**: Green for better performance, red for worse
- **Ratio Analysis**: Shows relative performance improvements
- **Statistical Overlays**: Confidence intervals and significance indicators

## 🔧 Customization

Each example script can be easily customized:

```python
# Modify filter criteria
cpu_stats = cpu_stats[cpu_stats['count'] >= 20]  # Increase minimum sample size

# Change color schemes
colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(data)))  # Use viridis colormap

# Adjust figure sizes
plt.figure(figsize=(16, 10))  # Larger charts

# Add custom annotations
plt.annotate('Performance Target', xy=(x, y), xytext=(x2, y2), arrowprops=dict(arrowstyle='->'))
```

## 📋 Data Requirements

Examples expect data in the following format:
- CSV file at `data/ocio_test_results.csv`
- Required columns: `cpu_model`, `aces_version`, `os_release`, `ocio_version`, `avg_time`
- Minimum data points per category for meaningful analysis

## 🔍 Troubleshooting

**Common Issues**:

1. **"No data found"**: Check CSV file path and column names
2. **"Insufficient data"**: Reduce minimum sample size requirements
3. **"Module not found"**: Ensure src/ package is in Python path
4. **"Empty charts"**: Verify data filtering criteria aren't too restrictive

**Debug Mode**:
```python
# Add at the beginning of any example
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📚 Related Documentation

- [Analysis Package Documentation](../src/ocio_performance_analysis/README.md)
- [Configuration Guide](../docs/CONFIGURATION.md)
- [Performance Analysis Guide](../docs/PERFORMANCE_ANALYSIS.md)

---

*These examples demonstrate the practical application of the enhanced OCIO performance analysis package for real-world performance assessment and decision making.*
