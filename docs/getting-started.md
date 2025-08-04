# Getting Started

This guide will help you quickly set up and start using the OCIO Performance Analysis tools.

## 📋 Prerequisites

### System Requirements
- Python 3.8 or higher
- Windows, macOS, or Linux
- At least 4GB RAM for large datasets
- 1GB disk space for results and charts

### Required Dependencies
```bash
pip install pandas numpy matplotlib seaborn pytest
```

### Optional Dependencies
```bash
pip install jupyter  # For notebook analysis
pip install ruff     # For code linting
```

## 🚀 Quick Start

### 1. Installation
```bash
# Clone or download the project
cd OCIO_tests-20250704T114759Z-1-001

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "from src.ocio_performance_analysis import OCIODataAnalyzer; print('✅ Ready to go!')"
```

### 2. Prepare Your Data
Place your OCIO test data in the `data/` directory:
```
data/
├── ocio_test_results.csv          # Main dataset
└── OCIO_tests/                    # Raw test files (optional)
    ├── OCIO_2.4_ACES_tests_r7.txt
    └── OCIO_2.4_ACES_tests_r9.txt
```

### 3. Run Your First Analysis
```bash
# Generate comprehensive OS release comparison charts
python examples/os_release_comparison.py

# Analyze CPU performance rankings
python examples/cpu_performance_analysis.py

# Compare ACES version impact
python examples/aces_version_analysis.py
```

### 4. View Results
Charts are saved to `examples/outputs/`:
- `os_comparison_overall.png` - OS release performance comparison
- `cpu_performance_ranking.png` - CPU performance rankings
- `aces_overall_comparison.png` - ACES version analysis
- `ocio_version_comparison.png` - OCIO version comparison

## 📊 Basic Usage Examples

### Load and Analyze Data
```python
from src.ocio_performance_analysis import OCIODataAnalyzer
from pathlib import Path

# Initialize analyzer
analyzer = OCIODataAnalyzer()
analyzer.set_csv_file(Path('data/ocio_test_results.csv'))
analyzer.load_data()

# Basic statistics
print(f"Loaded {len(analyzer.data)} test results")
print(f"CPU models: {analyzer.data['cpu_model'].nunique()}")
print(f"ACES versions: {analyzer.data['aces_version'].unique()}")
```

### Generate Quick Charts
```python
from src.ocio_performance_analysis import OCIOChartGenerator

# Create chart generator
chart_gen = OCIOChartGenerator(analyzer.data)

# Generate performance distribution
chart_gen.create_distribution_chart(
    column='avg_time',
    title='Performance Distribution',
    output_path='performance_dist.png'
)
```

### Create Performance Reports
```python
from src.ocio_performance_analysis import OCIOReportGenerator

# Generate comprehensive report
report_gen = OCIOReportGenerator(analyzer.data)
report_gen.generate_summary_report('performance_summary.txt')
```

## 🎯 Common Use Cases

### Compare OS Releases
```bash
python examples/os_release_comparison.py
```
**Generates:**
- Overall r7 vs r9 comparison
- Per-CPU performance improvements  
- ACES version impact analysis
- OCIO version comparison

### Rank CPU Performance
```bash
python examples/cpu_performance_analysis.py
```
**Generates:**
- CPU performance rankings
- Performance consistency analysis
- ACES version impact by CPU
- Top CPU detailed comparison

### Analyze ACES Versions
```bash
python examples/aces_version_analysis.py
```
**Generates:**
- ACES 1.0 vs 2.0 overall comparison
- CPU-specific ACES impact
- Performance distribution analysis
- Statistical ratio comparisons

## 🔧 Configuration

### Custom Configuration
Create `ocio_config.json`:
```json
{
    "data_source": "data/custom_results.csv",
    "output_directory": "custom_outputs/",
    "chart_settings": {
        "dpi": 300,
        "figure_size": [12, 8],
        "color_palette": "viridis"
    },
    "analysis_settings": {
        "min_sample_size": 10,
        "confidence_level": 0.95,
        "outlier_threshold": 2.5
    }
}
```

### Environment Variables
```bash
export OCIO_DATA_PATH="path/to/your/data"
export OCIO_OUTPUT_PATH="path/to/outputs"
```

## 🐛 Troubleshooting

### Common Issues

**"Module not found" errors:**
```bash
# Ensure you're in the project directory
cd OCIO_tests-20250704T114759Z-1-001

# Add to Python path if needed
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

**"No data found" errors:**
```bash
# Check data file exists
ls -la data/ocio_test_results.csv

# Verify column names match expected format
python -c "import pandas as pd; print(pd.read_csv('data/ocio_test_results.csv').columns.tolist())"
```

**Empty or missing charts:**
```bash
# Check output directory permissions
mkdir -p examples/outputs
chmod 755 examples/outputs

# Verify data filtering isn't too restrictive
python -c "from src.ocio_performance_analysis import OCIODataAnalyzer; a=OCIODataAnalyzer(); a.set_csv_file('data/ocio_test_results.csv'); a.load_data(); print(f'Loaded {len(a.data)} rows')"
```

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run analysis with detailed logging
python examples/os_release_comparison.py
```

## 📚 Next Steps

1. **Explore Examples**: Review the generated charts and understand the insights
2. **Customize Analysis**: Modify the example scripts for your specific needs  
3. **Advanced Features**: Check the [technical reference](technical-reference.md) for advanced capabilities
4. **Create Reports**: Use the reporting tools for automated documentation
5. **Contribute**: See [development](development.md) for contribution guidelines

## 🆘 Getting Help

- **Technical Issues**: Check [technical reference](technical-reference.md)
- **Analysis Questions**: Review [analysis results](analysis-results.md)
- **Development**: See [development](development.md)
- **Examples**: Explore [examples](examples.md)

---

*Ready to start analyzing OCIO performance data! 🚀*
