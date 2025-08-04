"""
Custom exceptions for OCIO Performance Analysis.
"""


class OCIOAnalysisError(Exception):
    """Base exception for OCIO analysis operations."""
    pass


class ParseError(OCIOAnalysisError):
    """Raised when parsing OCIO test files fails."""
    pass


class DataValidationError(OCIOAnalysisError):
    """Raised when data validation fails."""
    pass


class AnalysisError(OCIOAnalysisError):
    """Raised when analysis operations fail."""
    pass


class ChartGenerationError(OCIOAnalysisError):
    """Raised when chart generation fails."""
    pass


class FileNotFoundError(OCIOAnalysisError):
    """Raised when required files are not found."""
    pass


class ConfigurationError(OCIOAnalysisError):
    """Raised when configuration is invalid."""
    pass
