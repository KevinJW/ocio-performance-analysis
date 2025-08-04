# Technical Reference

Complete technical documentation for the OCIO Performance Analysis package.

## 🏗️ Architecture Overview

The OCIO Performance Analysis package follows a modular architecture with clear separation of concerns:

```
src/ocio_performance_analysis/
├── __init__.py              # Package initialization and exports
├── analyzer.py              # Core data analysis (OCIODataAnalyzer)
├── chart_generator.py       # Visualization tools (OCIOChartGenerator) 
├── report_generator.py      # Report generation (OCIOReportGenerator)
├── config.py               # Configuration management
├── exceptions.py           # Custom exception classes
└── utils.py               # Utility functions
```

## 📚 Core Classes

### OCIODataAnalyzer

**Purpose**: Core data loading, validation, and statistical analysis

**Key Methods**:

```python
class OCIODataAnalyzer:
    def __init__(self, config=None)
    def set_csv_file(self, file_path: Path)
    def load_data(self) -> pd.DataFrame
    def validate_data(self) -> bool
    def filter_data(self, **filters) -> pd.DataFrame
    def get_performance_stats(self, group_by=None) -> Dict
    def detect_outliers(self, column='avg_time', method='iqr') -> pd.DataFrame
    def compare_groups(self, group_col, value_col='avg_time') -> Dict
    def get_percentiles(self, column='avg_time', percentiles=[25, 50, 75, 95]) -> Dict
```

**Key Features**:

- **LRU Caching**: Automatic caching of expensive operations
- **Data Validation**: Comprehensive schema validation
- **Statistical Methods**: Built-in outlier detection and group comparisons
- **Flexible Filtering**: Dynamic data filtering with multiple criteria
- **Performance Optimization**: Lazy loading and memory-efficient processing

**Usage Example**:

```python
from src.ocio_performance_analysis import OCIODataAnalyzer

# Initialize with custom configuration
analyzer = OCIODataAnalyzer(config=custom_config)

# Load and validate data
analyzer.set_csv_file(Path('data/ocio_test_results.csv'))
analyzer.load_data()
analyzer.validate_data()

# Get performance statistics
stats = analyzer.get_performance_stats(group_by=['os_release', 'cpu_model'])

# Detect outliers
outliers = analyzer.detect_outliers(column='avg_time', method='zscore')

# Compare groups
comparison = analyzer.compare_groups('os_release', 'avg_time')
```

### OCIOChartGenerator

**Purpose**: Advanced visualization and chart generation

**Key Methods**:

```python
class OCIOChartGenerator:
    def __init__(self, data: pd.DataFrame, config=None)
    def create_distribution_chart(self, column, title, output_path, **kwargs)
    def create_scatter_chart(self, x_col, y_col, title, output_path, **kwargs)
    def create_violin_chart(self, x_col, y_col, title, output_path, **kwargs)
    def create_box_chart(self, x_col, y_col, title, output_path, **kwargs)
    def create_time_series_chart(self, date_col, value_col, title, output_path, **kwargs)
    def create_professional_bar_chart(self, data, x_col, y_col, title, output_path, **kwargs)
```

**Key Features**:

- **Multiple Chart Types**: Distribution, scatter, violin, box, time series, bar charts
- **Professional Styling**: Consistent, publication-ready aesthetics
- **Customizable Colors**: Support for custom color palettes and themes
- **High-Resolution Output**: 300 DPI default with configurable resolution
- **Statistical Annotations**: Automatic significance testing and annotations

**Usage Example**:

```python
from src.ocio_performance_analysis import OCIOChartGenerator

# Initialize chart generator
chart_gen = OCIOChartGenerator(data, config=chart_config)

# Create distribution chart
chart_gen.create_distribution_chart(
    column='avg_time',
    title='Performance Distribution by OS Release',
    output_path='performance_dist.png',
    group_by='os_release',
    show_stats=True
)

# Create professional bar chart
chart_gen.create_professional_bar_chart(
    data=summary_data,
    x_col='cpu_model',
    y_col='avg_performance',
    title='CPU Performance Comparison',
    output_path='cpu_comparison.png',
    color_palette='viridis'
)
```

### OCIOReportGenerator

**Purpose**: Automated report generation and documentation

**Key Methods**:

```python
class OCIOReportGenerator:
    def __init__(self, data: pd.DataFrame, config=None)
    def generate_summary_report(self, output_path: str)
    def generate_detailed_report(self, output_path: str, include_charts=True)
    def generate_comparison_report(self, group_by, output_path: str)
    def export_to_csv(self, output_path: str, include_metadata=True)
    def export_to_json(self, output_path: str, include_metadata=True)
```

**Key Features**:

- **Multiple Formats**: Text, CSV, JSON export capabilities
- **Automated Analysis**: Statistical summaries and insights
- **Customizable Templates**: Configurable report templates
- **Chart Integration**: Embed charts in reports
- **Metadata Tracking**: Comprehensive analysis metadata

**Usage Example**:

```python
from src.ocio_performance_analysis import OCIOReportGenerator

# Initialize report generator
report_gen = OCIOReportGenerator(data, config=report_config)

# Generate comprehensive summary
report_gen.generate_summary_report('analysis_summary.txt')

# Generate detailed comparison report
report_gen.generate_comparison_report(
    group_by=['os_release', 'cpu_model'],
    output_path='detailed_comparison.txt'
)

# Export structured data
report_gen.export_to_csv('results.csv', include_metadata=True)
report_gen.export_to_json('results.json', include_metadata=True)
```

## ⚙️ Configuration System

### OCIOConfig Class

**Purpose**: Centralized configuration management

```python
@dataclass
class OCIOConfig:
    # Data settings
    data_source: str = "data/ocio_test_results.csv"
    required_columns: List[str] = field(default_factory=lambda: [
        'test_name', 'cpu_model', 'os_release', 'aces_version', 'avg_time'
    ])
    
    # Chart settings  
    output_directory: str = "analysis_results/"
    figure_size: Tuple[int, int] = (12, 8)
    dpi: int = 300
    color_palette: str = "viridis"
    
    # Analysis settings
    min_sample_size: int = 5
    confidence_level: float = 0.95
    outlier_threshold: float = 2.0
    
    # Performance settings
    enable_caching: bool = True
    cache_size: int = 128
    parallel_processing: bool = True
    max_workers: int = 4
```

**Configuration Loading**:

```python
# Load from JSON file
config = OCIOConfig.from_json('ocio_config.json')

# Load from environment variables
config = OCIOConfig.from_env()

# Programmatic configuration
config = OCIOConfig(
    data_source='custom_data.csv',
    output_directory='custom_outputs/',
    dpi=600,
    parallel_processing=True
)
```

### Environment Variables

```bash
# Data configuration
export OCIO_DATA_SOURCE="path/to/data.csv"
export OCIO_OUTPUT_DIR="path/to/outputs/"

# Analysis configuration  
export OCIO_MIN_SAMPLE_SIZE=10
export OCIO_CONFIDENCE_LEVEL=0.99
export OCIO_OUTLIER_THRESHOLD=2.5

# Performance configuration
export OCIO_ENABLE_CACHING=true
export OCIO_CACHE_SIZE=256
export OCIO_MAX_WORKERS=8
```

## 🛠️ Utility Functions

### Data Processing Utilities

```python
from src.ocio_performance_analysis.utils import (
    clean_column_names,
    standardize_cpu_names,
    parse_test_metadata,
    calculate_improvement_percentage,
    format_performance_stats
)

# Clean and standardize data
cleaned_data = clean_column_names(raw_data)
standardized_data = standardize_cpu_names(cleaned_data)

# Parse metadata from test names
metadata = parse_test_metadata(test_name)

# Calculate performance improvements
improvement = calculate_improvement_percentage(old_value, new_value)

# Format statistics for reporting
formatted_stats = format_performance_stats(stats_dict)
```

### Statistical Utilities

```python
from src.ocio_performance_analysis.utils import (
    calculate_cohens_d,
    perform_t_test,
    calculate_confidence_interval,
    detect_outliers_iqr,
    normalize_data
)

# Effect size calculation
effect_size = calculate_cohens_d(group1, group2)

# Statistical testing
t_stat, p_value = perform_t_test(group1, group2)

# Confidence intervals
ci_lower, ci_upper = calculate_confidence_interval(data, confidence=0.95)

# Outlier detection
outliers = detect_outliers_iqr(data, column='avg_time')

# Data normalization
normalized_data = normalize_data(data, method='zscore')
```

## 🎨 Visualization Customization

### Color Palettes

```python
# Built-in palettes
PALETTES = {
    'corporate': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'],
    'accessible': ['#000080', '#FFA500', '#008000', '#FF0000', '#800080'],
    'scientific': ['#0173B2', '#DE8F05', '#029E73', '#CC78BC', '#CA9161'],
    'grayscale': ['#2d3748', '#4a5568', '#718096', '#a0aec0', '#cbd5e0']
}

# Custom palette usage
chart_gen = OCIOChartGenerator(data)
chart_gen.set_color_palette('corporate')
```

### Styling Options

```python
# Professional styling configuration
STYLE_CONFIG = {
    'font_family': 'Arial',
    'title_size': 16,
    'label_size': 12,
    'tick_size': 10,
    'legend_size': 10,
    'grid_alpha': 0.3,
    'spine_width': 0.8,
    'figure_facecolor': 'white',
    'axes_facecolor': 'white'
}

# Apply custom styling
chart_gen.apply_style_config(STYLE_CONFIG)
```

### Chart Annotations

```python
# Add statistical annotations
def add_significance_annotation(ax, x1, x2, y, p_value):
    """Add statistical significance annotation to chart"""
    
    # Determine significance level
    if p_value < 0.001:
        sig_text = '***'
    elif p_value < 0.01:
        sig_text = '**'
    elif p_value < 0.05:
        sig_text = '*'
    else:
        sig_text = 'ns'
    
    # Add annotation
    ax.annotate(sig_text, xy=((x1+x2)/2, y), ha='center', va='bottom')
```

## 🔍 Error Handling

### Custom Exceptions

```python
from src.ocio_performance_analysis.exceptions import (
    OCIODataError,
    OCIOConfigError,
    OCIOAnalysisError,
    OCIOVisualizationError
)

# Data validation errors
try:
    analyzer.validate_data()
except OCIODataError as e:
    logger.error(f"Data validation failed: {e}")
    
# Configuration errors
try:
    config = OCIOConfig.from_json('invalid_config.json')
except OCIOConfigError as e:
    logger.error(f"Configuration error: {e}")

# Analysis errors
try:
    results = analyzer.compare_groups('invalid_column')
except OCIOAnalysisError as e:
    logger.error(f"Analysis failed: {e}")

# Visualization errors
try:
    chart_gen.create_distribution_chart(invalid_params)
except OCIOVisualizationError as e:
    logger.error(f"Chart generation failed: {e}")
```

### Error Recovery

```python
# Robust data loading with fallbacks
def load_data_with_fallbacks(primary_path, fallback_paths):
    """Load data with multiple fallback options"""
    
    paths_to_try = [primary_path] + fallback_paths
    
    for path in paths_to_try:
        try:
            analyzer = OCIODataAnalyzer()
            analyzer.set_csv_file(path)
            analyzer.load_data()
            return analyzer
        except OCIODataError:
            continue
    
    raise OCIODataError("No valid data sources found")
```

## 🚀 Performance Optimization

### Caching Strategy

```python
from functools import lru_cache
from src.ocio_performance_analysis.analyzer import OCIODataAnalyzer

class OptimizedAnalyzer(OCIODataAnalyzer):
    
    @lru_cache(maxsize=128)
    def get_cached_stats(self, group_by_tuple):
        """Cache expensive statistical calculations"""
        return self.get_performance_stats(group_by=list(group_by_tuple))
    
    @lru_cache(maxsize=64)
    def get_cached_comparison(self, group_col, value_col):
        """Cache group comparisons"""
        return self.compare_groups(group_col, value_col)
```

### Memory Management

```python
# Memory-efficient data processing
def process_large_dataset(file_path, chunk_size=10000):
    """Process large datasets in chunks"""
    
    results = []
    
    for chunk in pd.read_csv(file_path, chunksize=chunk_size):
        # Process chunk
        processed = analyze_chunk(chunk)
        
        # Store only essential results
        results.append(processed.summarize())
        
        # Clear chunk from memory
        del chunk, processed
        
    return pd.concat(results)
```

### Parallel Processing

```python
from concurrent.futures import ProcessPoolExecutor
import multiprocessing as mp

def parallel_analysis(data_groups, analysis_func, max_workers=None):
    """Run analysis in parallel across data groups"""
    
    if max_workers is None:
        max_workers = mp.cpu_count() - 1
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(analysis_func, group) 
            for group in data_groups
        ]
        
        results = [future.result() for future in futures]
    
    return results
```

## 🧪 Testing Framework

### Unit Testing

```python
import unittest
from src.ocio_performance_analysis import OCIODataAnalyzer

class TestOCIODataAnalyzer(unittest.TestCase):
    
    def setUp(self):
        self.analyzer = OCIODataAnalyzer()
        self.test_data = create_test_data()
    
    def test_data_loading(self):
        """Test data loading functionality"""
        self.analyzer.data = self.test_data
        self.assertTrue(self.analyzer.validate_data())
    
    def test_statistical_analysis(self):
        """Test statistical analysis methods"""
        stats = self.analyzer.get_performance_stats()
        self.assertIn('mean', stats)
        self.assertIn('std', stats)
    
    def test_group_comparison(self):
        """Test group comparison functionality"""
        comparison = self.analyzer.compare_groups('os_release')
        self.assertIn('effect_size', comparison)
```

### Integration Testing

```python
def test_end_to_end_analysis():
    """Test complete analysis pipeline"""
    
    # Setup
    analyzer = OCIODataAnalyzer()
    analyzer.set_csv_file('test_data.csv')
    analyzer.load_data()
    
    # Analysis
    chart_gen = OCIOChartGenerator(analyzer.data)
    chart_gen.create_distribution_chart(
        column='avg_time',
        title='Test Chart',
        output_path='test_output.png'
    )
    
    # Validation
    assert Path('test_output.png').exists()
    assert Path('test_output.png').stat().st_size > 0
```

## 📊 Data Schema

### Expected CSV Format

```csv
test_name,cpu_model,os_release,aces_version,ocio_version,avg_time,std_dev,sample_size
OCIO_ACES_test_001,Intel i9-9900K,r7,1.0,2.4.1,2.45,0.12,100
OCIO_ACES_test_002,Intel i9-9900K,r9,1.0,2.4.1,2.02,0.08,100
...
```

### Required Columns

- **test_name**: Unique identifier for each test
- **cpu_model**: CPU model identifier
- **os_release**: Operating system release (r7, r9, etc.)
- **aces_version**: ACES version (1.0, 2.0)
- **ocio_version**: OCIO library version
- **avg_time**: Average execution time (seconds)
- **std_dev**: Standard deviation of timing
- **sample_size**: Number of samples in test

### Optional Columns

- **test_date**: Date of test execution
- **memory_usage**: Peak memory usage (MB)
- **cpu_usage**: Average CPU utilization (%)
- **test_category**: Test category/type
- **environment**: Test environment details

## 🔧 API Reference

### Complete Method Signatures

```python
# OCIODataAnalyzer
class OCIODataAnalyzer:
    def __init__(self, config: Optional[OCIOConfig] = None)
    def set_csv_file(self, file_path: Union[str, Path]) -> None
    def load_data(self) -> pd.DataFrame
    def validate_data(self) -> bool
    def filter_data(self, **filters) -> pd.DataFrame
    def get_performance_stats(self, group_by: Optional[List[str]] = None) -> Dict[str, Any]
    def detect_outliers(self, column: str = 'avg_time', method: str = 'iqr') -> pd.DataFrame
    def compare_groups(self, group_col: str, value_col: str = 'avg_time') -> Dict[str, Any]
    def get_percentiles(self, column: str = 'avg_time', percentiles: List[int] = [25, 50, 75, 95]) -> Dict[int, float]

# OCIOChartGenerator  
class OCIOChartGenerator:
    def __init__(self, data: pd.DataFrame, config: Optional[OCIOConfig] = None)
    def create_distribution_chart(self, column: str, title: str, output_path: Union[str, Path], **kwargs) -> None
    def create_scatter_chart(self, x_col: str, y_col: str, title: str, output_path: Union[str, Path], **kwargs) -> None
    def create_violin_chart(self, x_col: str, y_col: str, title: str, output_path: Union[str, Path], **kwargs) -> None
    def create_box_chart(self, x_col: str, y_col: str, title: str, output_path: Union[str, Path], **kwargs) -> None
    def create_time_series_chart(self, date_col: str, value_col: str, title: str, output_path: Union[str, Path], **kwargs) -> None
    def create_professional_bar_chart(self, data: pd.DataFrame, x_col: str, y_col: str, title: str, output_path: Union[str, Path], **kwargs) -> None

# OCIOReportGenerator
class OCIOReportGenerator:
    def __init__(self, data: pd.DataFrame, config: Optional[OCIOConfig] = None)
    def generate_summary_report(self, output_path: Union[str, Path]) -> None
    def generate_detailed_report(self, output_path: Union[str, Path], include_charts: bool = True) -> None
    def generate_comparison_report(self, group_by: List[str], output_path: Union[str, Path]) -> None
    def export_to_csv(self, output_path: Union[str, Path], include_metadata: bool = True) -> None
    def export_to_json(self, output_path: Union[str, Path], include_metadata: bool = True) -> None
```

---

*Complete technical reference for advanced usage and development! 🔧*
