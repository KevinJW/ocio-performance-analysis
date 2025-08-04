# Development Guide

This guide covers development practices, contribution guidelines, and technical details for working with the OCIO Performance Analysis codebase.

## 🏗️ Development Environment Setup

### Prerequisites

```bash
# Python version
python --version  # Requires 3.8+

# Development dependencies
pip install -r requirements.txt
pip install pytest pytest-cov ruff black isort mypy

# Optional development tools
pip install jupyter ipython pre-commit
```

### Project Structure

```
OCIO_tests-20250704T114759Z-1-001/
├── src/                           # Main package source
│   └── ocio_performance_analysis/
│       ├── __init__.py           # Package exports
│       ├── analyzer.py           # Data analysis core
│       ├── chart_generator.py    # Visualization tools
│       ├── report_generator.py   # Report generation
│       ├── config.py            # Configuration management
│       ├── exceptions.py        # Custom exceptions
│       └── utils.py             # Utility functions
├── examples/                     # Usage examples
│   ├── os_release_comparison.py # OS comparison analysis
│   ├── cpu_performance_analysis.py # CPU analysis
│   ├── aces_version_analysis.py # ACES comparison
│   └── outputs/                 # Generated charts
├── tests/                       # Test suite
│   ├── test_parser.py          # Core functionality tests
│   └── __pycache__/            # Test cache
├── data/                        # Data files
│   ├── ocio_test_results.csv   # Main dataset
│   └── OCIO_tests/             # Raw test files
├── docs/                        # Documentation
├── analysis_results/            # Analysis outputs
└── pyproject.toml              # Project configuration
```

### Environment Configuration

```bash
# Set up development environment
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
export OCIO_DEV_MODE=true
export OCIO_LOG_LEVEL=DEBUG

# Development data paths
export OCIO_DATA_PATH="$(pwd)/data"
export OCIO_OUTPUT_PATH="$(pwd)/analysis_results"
```

## 🧪 Testing Framework

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=src/ocio_performance_analysis --cov-report=html

# Run specific test
python -m pytest tests/test_parser.py::TestOCIOParser::test_parse_file -v

# Run with detailed output
python -m pytest tests/ -v -s --tb=long
```

### Test Structure

```python
# Example test file: tests/test_analyzer.py
import unittest
import pandas as pd
from pathlib import Path
from src.ocio_performance_analysis import OCIODataAnalyzer, OCIOConfig

class TestOCIODataAnalyzer(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures once for all tests"""
        cls.test_data_path = Path('data/test_ocio_results.csv')
        cls.analyzer = OCIODataAnalyzer()
    
    def setUp(self):
        """Set up before each test"""
        self.analyzer.data = None
    
    def test_data_loading(self):
        """Test data loading functionality"""
        self.analyzer.set_csv_file(self.test_data_path)
        self.analyzer.load_data()
        self.assertIsNotNone(self.analyzer.data)
        self.assertGreater(len(self.analyzer.data), 0)
    
    def test_data_validation(self):
        """Test data validation"""
        # Test with valid data
        self.analyzer.data = create_valid_test_data()
        self.assertTrue(self.analyzer.validate_data())
        
        # Test with invalid data
        self.analyzer.data = create_invalid_test_data()
        self.assertFalse(self.analyzer.validate_data())
    
    def tearDown(self):
        """Clean up after each test"""
        if hasattr(self.analyzer, 'data'):
            self.analyzer.data = None

def create_valid_test_data():
    """Helper function to create valid test data"""
    return pd.DataFrame({
        'test_name': ['test_001', 'test_002'],
        'cpu_model': ['Intel i9-9900K', 'Intel i9-9900K'],
        'os_release': ['r7', 'r9'],
        'aces_version': ['1.0', '1.0'],
        'avg_time': [1.5, 1.2]
    })
```

### Test Coverage Goals

- **Unit Tests**: 90%+ coverage for all core modules
- **Integration Tests**: End-to-end workflow validation
- **Performance Tests**: Benchmark critical operations
- **Regression Tests**: Prevent performance degradation

## 🔧 Code Quality Standards

### Linting and Formatting

```bash
# Code formatting with Black
black src/ tests/ examples/

# Import sorting with isort
isort src/ tests/ examples/

# Linting with Ruff
ruff check src/ tests/ examples/

# Type checking with mypy
mypy src/ocio_performance_analysis/
```

### Pre-commit Hooks

```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run manually
pre-commit run --all-files
```

### Configuration Files

#### `.pre-commit-config.yaml`
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.8
  
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]
  
  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.0.270
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
```

#### `pyproject.toml` (relevant sections)
```toml
[tool.black]
line-length = 88
target-version = ['py38']
include = '\.pyi?$'

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88

[tool.ruff]
line-length = 88
target-version = "py38"
select = ["E", "F", "W", "C90", "I", "N", "UP", "YTT", "S", "B", "A", "COM", "C4", "DTZ", "T10", "EM", "EXE", "ISC", "ICN", "G", "INP", "PIE", "T20", "PYI", "PT", "Q", "RSE", "RET", "SLF", "SIM", "TID", "TCH", "ARG", "PTH", "ERA", "PD", "PGH", "PL", "TRY", "NPY", "RUF"]

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

## 🚀 Adding New Features

### Feature Development Workflow

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/new-analysis-type
   ```

2. **Implement Feature**
   - Add core functionality to appropriate module
   - Add comprehensive tests
   - Update documentation
   - Add example usage

3. **Quality Checks**
   ```bash
   # Run tests
   python -m pytest tests/ -v
   
   # Check code quality
   ruff check src/
   black --check src/
   mypy src/
   ```

4. **Integration Testing**
   ```bash
   # Test example scripts
   python examples/os_release_comparison.py
   python examples/cpu_performance_analysis.py
   python examples/aces_version_analysis.py
   ```

5. **Documentation Update**
   - Update relevant documentation files
   - Add to examples if appropriate
   - Update README if needed

### Adding New Analysis Methods

```python
# Example: Add memory analysis to OCIODataAnalyzer
class OCIODataAnalyzer:
    
    def analyze_memory_usage(self, group_by: Optional[List[str]] = None) -> Dict[str, Any]:
        """Analyze memory usage patterns across test results.
        
        Args:
            group_by: Optional columns to group analysis by
            
        Returns:
            Dictionary containing memory usage statistics
            
        Raises:
            OCIOAnalysisError: If memory data is not available
        """
        if 'memory_usage' not in self.data.columns:
            raise OCIOAnalysisError("Memory usage data not found in dataset")
        
        if group_by:
            grouped = self.data.groupby(group_by)['memory_usage']
            results = {
                'mean': grouped.mean().to_dict(),
                'std': grouped.std().to_dict(),
                'max': grouped.max().to_dict(),
                'min': grouped.min().to_dict()
            }
        else:
            memory_data = self.data['memory_usage']
            results = {
                'mean': memory_data.mean(),
                'std': memory_data.std(),
                'max': memory_data.max(),
                'min': memory_data.min(),
                'percentiles': memory_data.quantile([0.25, 0.5, 0.75, 0.95]).to_dict()
            }
        
        return results
```

### Adding New Chart Types

```python
# Example: Add heatmap chart to OCIOChartGenerator
class OCIOChartGenerator:
    
    def create_correlation_heatmap(self, 
                                 numeric_columns: List[str],
                                 title: str,
                                 output_path: Union[str, Path],
                                 **kwargs) -> None:
        """Create correlation heatmap for numeric columns.
        
        Args:
            numeric_columns: List of numeric columns to correlate
            title: Chart title
            output_path: Path to save chart
            **kwargs: Additional matplotlib parameters
        """
        import seaborn as sns
        
        # Calculate correlation matrix
        corr_data = self.data[numeric_columns].corr()
        
        # Create heatmap
        fig, ax = plt.subplots(figsize=kwargs.get('figsize', (10, 8)))
        
        sns.heatmap(
            corr_data,
            annot=True,
            cmap='coolwarm',
            center=0,
            square=True,
            ax=ax
        )
        
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        
        # Save chart
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
```

## 📊 Performance Optimization

### Profiling Tools

```python
# Performance profiling
import cProfile
import pstats
from functools import wraps

def profile_performance(func):
    """Decorator to profile function performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()
        result = func(*args, **kwargs)
        profiler.disable()
        
        # Print top 10 time-consuming functions
        stats = pstats.Stats(profiler)
        stats.sort_stats('cumulative')
        stats.print_stats(10)
        
        return result
    return wrapper

# Usage
@profile_performance
def expensive_analysis():
    analyzer = OCIODataAnalyzer()
    analyzer.load_data()
    return analyzer.get_performance_stats()
```

### Memory Optimization

```python
# Memory-efficient data processing
import gc
from memory_profiler import profile

@profile
def memory_efficient_analysis(data_path: Path, chunk_size: int = 10000):
    """Process large datasets with minimal memory usage"""
    
    results = []
    
    # Process in chunks
    for chunk in pd.read_csv(data_path, chunksize=chunk_size):
        # Process chunk
        processed = analyze_chunk(chunk)
        
        # Store only summary statistics
        summary = {
            'mean': processed['avg_time'].mean(),
            'count': len(processed),
            'std': processed['avg_time'].std()
        }
        results.append(summary)
        
        # Force garbage collection
        del chunk, processed
        gc.collect()
    
    return results
```

### Caching Strategies

```python
# Advanced caching with TTL
from functools import lru_cache
import time
from typing import Any, Callable

class TTLCache:
    """Time-based LRU cache for expensive operations"""
    
    def __init__(self, maxsize: int = 128, ttl: int = 3600):
        self.cache = {}
        self.maxsize = maxsize
        self.ttl = ttl
    
    def __call__(self, func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            key = str(args) + str(kwargs)
            now = time.time()
            
            if key in self.cache:
                value, timestamp = self.cache[key]
                if now - timestamp < self.ttl:
                    return value
                else:
                    del self.cache[key]
            
            # Compute new value
            result = func(*args, **kwargs)
            
            # Store with timestamp
            if len(self.cache) >= self.maxsize:
                # Remove oldest entry
                oldest_key = min(self.cache.keys(), 
                               key=lambda k: self.cache[k][1])
                del self.cache[oldest_key]
            
            self.cache[key] = (result, now)
            return result
        
        return wrapper

# Usage
@TTLCache(maxsize=64, ttl=1800)  # 30 minutes
def expensive_statistical_analysis(data_subset):
    return perform_complex_analysis(data_subset)
```

## 🔄 Version Control Practices

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**: feat, fix, docs, style, refactor, test, chore

**Examples**:
```
feat(analyzer): add memory usage analysis methods

- Implement analyze_memory_usage() method
- Add memory-specific statistical calculations  
- Update data validation for memory columns
- Add comprehensive tests for memory analysis

Closes #42
```

### Branch Management

```bash
# Feature branches
git checkout -b feature/memory-analysis
git checkout -b fix/chart-rendering-bug
git checkout -b docs/api-reference-update

# Release branches
git checkout -b release/v1.2.0

# Hotfix branches
git checkout -b hotfix/critical-performance-fix
```

### Git Hooks

```bash
#!/bin/sh
# .git/hooks/pre-commit
# Run quality checks before commit

# Run tests
python -m pytest tests/ -x

# Check code quality
ruff check src/ tests/
black --check src/ tests/
mypy src/

# Check for large files
git diff --cached --name-only | xargs ls -la | awk '$5 > 100000 { print $9 " is " $5 " bytes" }'
```

## 📚 Documentation Standards

### Docstring Format

```python
def analyze_performance_trends(self, 
                             date_column: str,
                             value_column: str = 'avg_time',
                             trend_method: str = 'linear') -> Dict[str, Any]:
    """Analyze performance trends over time.
    
    This method performs time series analysis on performance data to identify
    trends, seasonality, and anomalies in OCIO test results.
    
    Args:
        date_column: Name of column containing date/time information
        value_column: Name of column with performance values to analyze
        trend_method: Method for trend analysis ('linear', 'polynomial', 'seasonal')
    
    Returns:
        Dictionary containing trend analysis results:
            - trend_slope: Linear trend coefficient
            - r_squared: Goodness of fit measure
            - seasonal_component: Seasonal decomposition if applicable
            - anomalies: List of detected anomalous data points
    
    Raises:
        OCIOAnalysisError: If date column is not found or cannot be parsed
        ValueError: If trend_method is not supported
    
    Example:
        >>> analyzer = OCIODataAnalyzer()
        >>> analyzer.load_data()
        >>> trends = analyzer.analyze_performance_trends(
        ...     date_column='test_date',
        ...     value_column='avg_time',
        ...     trend_method='linear'
        ... )
        >>> print(f"Trend slope: {trends['trend_slope']:.4f}")
    
    Note:
        Requires pandas datetime parsing capability. Date column should be
        in ISO format or parseable by pd.to_datetime().
    """
```

### README Updates

When adding new features, update README sections:

```markdown
### New Feature: Memory Analysis

```python
# Analyze memory usage patterns
memory_stats = analyzer.analyze_memory_usage(group_by=['cpu_model'])
print(f"Average memory usage: {memory_stats['mean']:.2f} MB")

# Generate memory usage charts
chart_gen.create_memory_usage_chart(
    title='Memory Usage by CPU Model',
    output_path='memory_analysis.png'
)
```

## 🧩 Extension Points

### Plugin Architecture

```python
# Base plugin interface
from abc import ABC, abstractmethod

class OCIOAnalysisPlugin(ABC):
    """Base class for OCIO analysis plugins"""
    
    @abstractmethod
    def get_name(self) -> str:
        """Return plugin name"""
        pass
    
    @abstractmethod
    def get_version(self) -> str:
        """Return plugin version"""
        pass
    
    @abstractmethod
    def analyze(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Perform plugin-specific analysis"""
        pass
    
    @abstractmethod
    def create_visualizations(self, data: pd.DataFrame, output_dir: Path) -> List[str]:
        """Generate plugin-specific charts"""
        pass

# Example plugin implementation
class MemoryAnalysisPlugin(OCIOAnalysisPlugin):
    
    def get_name(self) -> str:
        return "Memory Usage Analysis"
    
    def get_version(self) -> str:
        return "1.0.0"
    
    def analyze(self, data: pd.DataFrame) -> Dict[str, Any]:
        # Implement memory analysis
        pass
    
    def create_visualizations(self, data: pd.DataFrame, output_dir: Path) -> List[str]:
        # Generate memory-specific charts
        pass

# Plugin registry
class PluginRegistry:
    def __init__(self):
        self.plugins = {}
    
    def register(self, plugin: OCIOAnalysisPlugin):
        self.plugins[plugin.get_name()] = plugin
    
    def get_plugin(self, name: str) -> OCIOAnalysisPlugin:
        return self.plugins.get(name)
    
    def list_plugins(self) -> List[str]:
        return list(self.plugins.keys())
```

### Custom Configuration Extensions

```python
# Extend base configuration
from dataclasses import dataclass, field
from src.ocio_performance_analysis.config import OCIOConfig

@dataclass
class ExtendedOCIOConfig(OCIOConfig):
    # Memory analysis settings
    memory_analysis_enabled: bool = False
    memory_threshold_mb: int = 1000
    
    # GPU analysis settings
    gpu_analysis_enabled: bool = False
    gpu_models: List[str] = field(default_factory=list)
    
    # Advanced visualization settings
    interactive_charts: bool = False
    chart_theme: str = "default"
    export_formats: List[str] = field(default_factory=lambda: ["png", "svg"])
```

## 🚀 Release Process

### Version Bumping

```bash
# Update version in pyproject.toml
# Update CHANGELOG.md
# Commit version bump
git add pyproject.toml CHANGELOG.md
git commit -m "chore: bump version to 1.2.0"

# Create release tag
git tag -a v1.2.0 -m "Release version 1.2.0"

# Push changes and tags
git push origin main
git push origin v1.2.0
```

### Release Checklist

- [ ] All tests passing
- [ ] Documentation updated
- [ ] Version bumped in pyproject.toml
- [ ] CHANGELOG.md updated
- [ ] Examples tested with new version
- [ ] Performance benchmarks run
- [ ] Git tag created
- [ ] Release notes prepared

### Changelog Format

```markdown
# Changelog

## [1.2.0] - 2024-01-15

### Added
- Memory usage analysis functionality
- Interactive chart generation options
- Plugin architecture for extensibility
- Advanced statistical methods

### Changed
- Improved performance of data loading by 40%
- Updated chart styling for better accessibility
- Refactored configuration system for better modularity

### Fixed
- Fixed memory leak in large dataset processing
- Corrected statistical calculations for edge cases
- Fixed chart rendering issues with missing data

### Deprecated
- Old configuration format (will be removed in v2.0)

### Security
- Updated dependencies to address security vulnerabilities
```

## 🤝 Contributing

### Contribution Types

1. **Bug Reports**: Use GitHub issues with bug template
2. **Feature Requests**: Use GitHub issues with feature template  
3. **Code Contributions**: Follow pull request template
4. **Documentation**: Improve existing or add new documentation
5. **Examples**: Add new example scripts or improve existing ones

### Pull Request Process

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Update documentation
5. Ensure all checks pass
6. Submit pull request

### Code Review Guidelines

- **Functionality**: Does the code work as intended?
- **Tests**: Are there adequate tests?
- **Documentation**: Is the code well-documented?
- **Performance**: Any performance implications?
- **Style**: Follows project coding standards?

---

*Ready to contribute to the OCIO Performance Analysis project! 🚀*
