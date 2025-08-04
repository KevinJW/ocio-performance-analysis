# Examples Guide

This guide demonstrates how to use the OCIO Performance Analysis tools through practical examples.

## 📚 Overview

The examples directory contains three main analysis scripts that demonstrate different aspects of OCIO performance analysis:

- **OS Release Comparison**: Compare performance between different OS releases
- **CPU Performance Analysis**: Analyze and rank CPU performance characteristics  
- **ACES Version Analysis**: Compare impact of different ACES versions

## 🎯 Example Scripts

### 1. OS Release Comparison (`os_release_comparison.py`)

**Purpose**: Comprehensive analysis of OS release performance differences

**Key Features**:

- Overall r7 vs r9 comparison with statistical significance
- Individual CPU performance improvements
- ACES version impact analysis
- OCIO version comparison
- Side-by-side visualization with improvement percentages

**Usage**:

```bash
python examples/os_release_comparison.py
```

**Generated Charts**:

- `os_comparison_overall.png` - Overall OS release comparison
- `os_comparison_individual_cpus.png` - Per-CPU performance analysis
- `os_improvement_summary.png` - Summary of improvements
- `os_aces_impact_comparison.png` - ACES version impact
- `os_ocio_version_comparison.png` - OCIO version analysis

**Key Insights**:

- **Intel i9-9900K**: 17.5% improvement (r7 → r9)
- **Intel Xeon E5-2687W**: 45.1% improvement  
- **Intel Xeon W-2295**: 61.2% improvement
- **Statistical Significance**: All improvements p < 0.001

### 2. CPU Performance Analysis (`cpu_performance_analysis.py`)

**Purpose**: Analyze CPU performance characteristics and rankings

**Key Features**:

- CPU performance ranking with confidence intervals
- Performance consistency analysis
- ACES version impact by CPU
- Top CPU detailed comparison

**Usage**:

```bash
python examples/cpu_performance_analysis.py
```

**Generated Charts**:

- `cpu_performance_ranking.png` - Overall CPU rankings
- `cpu_aces_comparison.png` - ACES impact by CPU
- `cpu_performance_variability.png` - Performance consistency
- `cpu_top_performers_detailed.png` - Detailed top CPU analysis

**Key Insights**:

- **Fastest CPU**: Intel Xeon W-2295 (1.42s average)
- **Most Consistent**: Intel i9-9900K (lowest variability)
- **ACES Impact**: Consistent 15-20% performance difference across CPUs
- **Performance Range**: 1.42s - 2.89s across all CPUs

### 3. ACES Version Analysis (`aces_version_analysis.py`)

**Purpose**: Compare performance impact of ACES 1.0 vs 2.0

**Key Features**:

- Overall ACES version comparison
- CPU-specific ACES impact analysis
- Performance distribution visualization
- Statistical ratio analysis

**Usage**:

```bash
python examples/aces_version_analysis.py
```

**Generated Charts**:

- `aces_overall_comparison.png` - Overall ACES comparison
- `aces_cpu_impact.png` - Per-CPU ACES impact
- `aces_distribution_analysis.png` - Performance distributions
- `aces_ratio_analysis.png` - Statistical ratios

**Key Insights**:

- **Average Performance Difference**: ACES 2.0 is 18.5% faster than 1.0
- **Consistent Impact**: All CPUs show similar ACES performance ratios
- **Distribution**: Clear separation between ACES versions
- **Recommendation**: ACES 2.0 provides significant performance benefits

## 🔧 Customization Guide

### Modifying Chart Appearance

```python
# In any example script, customize the chart settings
import matplotlib.pyplot as plt

# Set global style
plt.style.use('seaborn-v0_8')

# Custom color schemes
colors = {
    'primary': '#2E86AB',
    'secondary': '#A23B72', 
    'success': '#F18F01',
    'warning': '#C73E1D'
}

# Custom figure settings
fig_settings = {
    'figsize': (14, 10),
    'dpi': 300,
    'facecolor': 'white'
}
```

### Adding New Analysis Types

```python
# Example: Add memory usage analysis
def create_memory_analysis_chart(analyzer_data, output_path):
    """Create memory usage analysis chart"""
    
    # Filter data for memory metrics
    memory_data = analyzer_data[analyzer_data['metric_type'] == 'memory']
    
    # Create visualization
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Plot memory usage by OS release
    sns.boxplot(data=memory_data, x='os_release', y='memory_usage', ax=ax)
    
    # Customize appearance
    ax.set_title('Memory Usage by OS Release', fontsize=16, fontweight='bold')
    ax.set_xlabel('OS Release', fontsize=12)
    ax.set_ylabel('Memory Usage (MB)', fontsize=12)
    
    # Save chart
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
```

### Custom Data Filtering

```python
# Example: Filter by specific criteria
def analyze_specific_tests(analyzer):
    """Analyze only specific test conditions"""
    
    # Load all data
    analyzer.load_data()
    
    # Apply custom filters
    filtered_data = analyzer.data[
        (analyzer.data['test_type'] == 'performance') &
        (analyzer.data['sample_size'] >= 100) &
        (analyzer.data['cpu_model'].str.contains('Intel'))
    ]
    
    # Update analyzer with filtered data
    analyzer.data = filtered_data
    
    return analyzer
```

## 📊 Advanced Usage Patterns

### Batch Analysis

```python
# Analyze multiple datasets
datasets = [
    'data/ocio_test_results_q1.csv',
    'data/ocio_test_results_q2.csv', 
    'data/ocio_test_results_q3.csv'
]

for i, dataset in enumerate(datasets):
    analyzer = OCIODataAnalyzer()
    analyzer.set_csv_file(dataset)
    analyzer.load_data()
    
    # Generate charts with quarter suffix
    output_suffix = f"_Q{i+1}"
    create_comparison_charts(analyzer, output_suffix)
```

### Automated Reporting

```python
# Generate automated report with all charts
def generate_comprehensive_report(data_path, output_dir):
    """Generate all analysis charts and summary report"""
    
    # Initialize analyzer
    analyzer = OCIODataAnalyzer()
    analyzer.set_csv_file(data_path)
    analyzer.load_data()
    
    # Generate all chart types
    os_comparison_analysis(analyzer, output_dir)
    cpu_performance_analysis(analyzer, output_dir)
    aces_version_analysis(analyzer, output_dir)
    
    # Generate summary report
    report_gen = OCIOReportGenerator(analyzer.data)
    report_gen.generate_summary_report(
        f"{output_dir}/comprehensive_report.txt"
    )
    
    print(f"✅ Comprehensive analysis complete: {output_dir}")
```

### Statistical Analysis Integration

```python
# Add statistical testing to comparisons
from scipy import stats

def compare_with_statistics(group1, group2, metric='avg_time'):
    """Compare two groups with statistical testing"""
    
    # Extract values
    values1 = group1[metric].values
    values2 = group2[metric].values
    
    # Perform t-test
    t_stat, p_value = stats.ttest_ind(values1, values2)
    
    # Calculate effect size (Cohen's d)
    pooled_std = np.sqrt(((len(values1)-1)*np.var(values1) + 
                         (len(values2)-1)*np.var(values2)) / 
                        (len(values1)+len(values2)-2))
    cohens_d = (np.mean(values1) - np.mean(values2)) / pooled_std
    
    return {
        't_statistic': t_stat,
        'p_value': p_value,
        'effect_size': cohens_d,
        'significant': p_value < 0.05
    }
```

## 🎨 Chart Styling Guide

### Professional Color Schemes

```python
# Corporate color palette
CORPORATE_COLORS = {
    'primary': '#1f77b4',     # Blue
    'secondary': '#ff7f0e',   # Orange  
    'success': '#2ca02c',     # Green
    'warning': '#d62728',     # Red
    'info': '#9467bd',        # Purple
    'neutral': '#8c564b'      # Brown
}

# High contrast accessibility palette
ACCESSIBLE_COLORS = {
    'primary': '#000080',     # Navy
    'secondary': '#FFA500',   # Orange
    'success': '#008000',     # Green
    'warning': '#FF0000',     # Red
    'info': '#800080',        # Purple
    'neutral': '#696969'      # Dim Gray
}
```

### Chart Templates

```python
def apply_professional_styling(ax, title, xlabel, ylabel):
    """Apply consistent professional styling"""
    
    # Title styling
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    
    # Axis labels
    ax.set_xlabel(xlabel, fontsize=12, fontweight='bold')
    ax.set_ylabel(ylabel, fontsize=12, fontweight='bold')
    
    # Grid styling
    ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
    ax.set_axisbelow(True)
    
    # Spine styling
    for spine in ax.spines.values():
        spine.set_linewidth(0.8)
        spine.set_color('#333333')
    
    # Tick styling
    ax.tick_params(axis='both', which='major', labelsize=10)
    
    return ax
```

## 🚀 Performance Tips

### Large Dataset Optimization

```python
# For large datasets, use data sampling
def optimize_for_large_data(analyzer, sample_size=10000):
    """Optimize analysis for large datasets"""
    
    if len(analyzer.data) > sample_size:
        # Stratified sampling by key groups
        sampled_data = analyzer.data.groupby([
            'os_release', 'cpu_model', 'aces_version'
        ]).apply(lambda x: x.sample(min(len(x), 100))).reset_index(drop=True)
        
        analyzer.data = sampled_data
        print(f"📊 Sampled {len(sampled_data)} rows from large dataset")
    
    return analyzer
```

### Memory Efficient Processing

```python
# Process data in chunks for memory efficiency
def process_in_chunks(data_path, chunk_size=5000):
    """Process large CSV files in chunks"""
    
    results = []
    
    for chunk in pd.read_csv(data_path, chunksize=chunk_size):
        # Process each chunk
        processed_chunk = analyze_chunk(chunk)
        results.append(processed_chunk)
    
    # Combine results
    final_results = pd.concat(results, ignore_index=True)
    return final_results
```

## 🔍 Troubleshooting Examples

### Common Issues and Solutions

**Empty Charts**:

```python
# Debug data filtering
def debug_data_filtering(analyzer):
    """Debug why charts might be empty"""
    
    print(f"Total rows: {len(analyzer.data)}")
    print(f"Unique OS releases: {analyzer.data['os_release'].unique()}")
    print(f"Unique CPUs: {analyzer.data['cpu_model'].unique()}")
    print(f"Date range: {analyzer.data['test_date'].min()} to {analyzer.data['test_date'].max()}")
    
    # Check for missing values
    missing_data = analyzer.data.isnull().sum()
    print(f"Missing values:\n{missing_data[missing_data > 0]}")
```

**Performance Issues**:

```python
# Profile analysis performance
import time

def profile_analysis(analyzer, analysis_func):
    """Profile analysis function performance"""
    
    start_time = time.time()
    result = analysis_func(analyzer)
    end_time = time.time()
    
    print(f"⏱️  Analysis completed in {end_time - start_time:.2f} seconds")
    print(f"📊 Processed {len(analyzer.data)} rows")
    
    return result
```

## 📈 Future Enhancements

### Planned Features

1. **Interactive Charts**: Plotly integration for interactive visualizations
2. **Real-time Analysis**: Support for streaming data analysis
3. **Machine Learning**: Predictive performance modeling
4. **Dashboard**: Web-based dashboard for live monitoring
5. **API Integration**: REST API for remote analysis requests

### Contributing New Examples

```python
# Template for new example scripts
def new_analysis_template():
    """Template for creating new analysis examples"""
    
    # 1. Setup
    analyzer = OCIODataAnalyzer()
    analyzer.set_csv_file('data/ocio_test_results.csv')
    analyzer.load_data()
    
    # 2. Data Processing
    processed_data = custom_data_processing(analyzer.data)
    
    # 3. Analysis
    results = perform_custom_analysis(processed_data)
    
    # 4. Visualization
    create_custom_charts(results, 'outputs/')
    
    # 5. Reporting
    generate_custom_report(results, 'outputs/custom_report.txt')
    
    print("✅ Custom analysis complete!")

if __name__ == "__main__":
    new_analysis_template()
```

---

*Explore these examples to understand the full capabilities of the OCIO Performance Analysis toolkit! 🚀*
