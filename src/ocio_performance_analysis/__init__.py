"""
OCIO Performance Analysis Package

A Python package for parsing and analyzing OCIO (OpenColorIO) test results.
Provides tools for extracting performance data from test files, generating
comprehensive analysis reports, and creating visualizations for performance
comparisons across different configurations.
"""

__version__ = "1.0.0"
__author__ = "OCIO Performance Analysis Team"

from .analyzer import OCIOAnalyzer
from .parser import OCIOTestParser
from .viewer import OCIOChartViewer


__all__ = ["OCIOTestParser", "OCIOAnalyzer", "OCIOChartViewer"]
