"""
OCIO Data Analysis Module

Handles data processing, comparisons, and statistical analysis
for OCIO performance test results.
"""

from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd

from .exceptions import AnalysisError, DataValidationError, FileNotFoundError as OCIOFileNotFoundError
from .logging_config import get_logger

logger = get_logger(__name__)


class OCIODataAnalyzer:
    """Handles data analysis and comparison operations for OCIO performance data."""

    def __init__(self, csv_file: Optional[Path] = None):
        """
        Initialize the data analyzer.

        Args:
            csv_file: Path to the CSV file containing test results (optional)
            
        Raises:
            FileNotFoundError: If the CSV file doesn't exist
        """
        self.csv_file = csv_file
        self.data = None
        self._summary_cache = None
        
        # Validate CSV file if provided
        if csv_file and not csv_file.exists():
            raise OCIOFileNotFoundError(f"CSV file not found: {csv_file}")

    def set_csv_file(self, csv_file: Path) -> None:
        """
        Set the CSV file for analysis.
        
        Args:
            csv_file: Path to the CSV file containing test results
            
        Raises:
            FileNotFoundError: If the CSV file doesn't exist
        """
        if not csv_file.exists():
            raise OCIOFileNotFoundError(f"CSV file not found: {csv_file}")
            
        self.csv_file = csv_file
        # Clear cached data when CSV changes
        self.data = None
        self._summary_cache = None

    def load_data(self) -> pd.DataFrame:
        """
        Load test results from CSV file.

        Returns:
            DataFrame containing the test results
            
        Raises:
            AnalysisError: If data loading fails
            DataValidationError: If data is invalid
            ConfigurationError: If no CSV file is set
        """
        if not self.csv_file:
            from .exceptions import ConfigurationError
            raise ConfigurationError("No CSV file set. Use set_csv_file() first.")
            
        # Return cached data if available
        if self.data is not None:
            logger.debug("Using cached data")
            return self.data
            
        try:
            logger.info(f"Loading data from {self.csv_file}")
            self.data = pd.read_csv(self.csv_file)
            
            if self.data.empty:
                raise DataValidationError("CSV file contains no data")
                
            logger.info(f"Loaded {len(self.data)} test results")
            
            # Validate data quality
            self._validate_data_quality()
            
            # Add ACES version categorization
            self.data['aces_version'] = self.data['target_colorspace'].apply(
                self._categorize_aces_version
            )
            
            logger.info("Data loading and validation completed successfully")
            return self.data
            
        except Exception as e:
            if isinstance(e, (DataValidationError, OCIOFileNotFoundError)):
                raise
            raise AnalysisError(f"Failed to load data from {self.csv_file}: {e}")

    def _validate_data_quality(self) -> None:
        """
        Validate the quality and completeness of loaded data.
        
        Raises:
            DataValidationError: If data quality issues are found
        """
        required_columns = ['avg_time', 'min_time', 'max_time', 'file_name', 'cpu_model']
        missing_columns = [col for col in required_columns if col not in self.data.columns]
        
        if missing_columns:
            raise DataValidationError(f"Missing required columns: {missing_columns}")
        
        # Check for negative timing values
        timing_columns = ['avg_time', 'min_time', 'max_time']
        for col in timing_columns:
            if col in self.data.columns:
                negative_count = (self.data[col] < 0).sum()
                if negative_count > 0:
                    logger.warning(f"Found {negative_count} negative values in {col}")
        
        # Check for reasonable timing ranges (not too large)
        max_reasonable_time = 100000  # 100 seconds in ms
        for col in timing_columns:
            if col in self.data.columns:
                large_values = (self.data[col] > max_reasonable_time).sum()
                if large_values > 0:
                    logger.warning(f"Found {large_values} unusually large values in {col} (>{max_reasonable_time}ms)")
        
        # Check data completeness
        total_rows = len(self.data)
        for col in required_columns:
            null_count = self.data[col].isnull().sum()
            if null_count > 0:
                null_pct = (null_count / total_rows) * 100
                if null_pct > 10:  # More than 10% missing
                    logger.warning(f"Column '{col}' has {null_pct:.1f}% missing values")
                else:
                    logger.debug(f"Column '{col}' has {null_count} missing values ({null_pct:.1f}%)")
        
        logger.debug(f"Data quality validation completed for {total_rows} rows")

    def _categorize_aces_version(self, target_colorspace: str) -> str:
        """
        Categorize target colorspace into ACES version.

        Args:
            target_colorspace: The target colorspace string

        Returns:
            ACES version ("ACES 1.0" or "ACES 2.0")
        """
        if pd.isna(target_colorspace):
            return "Unknown"
            
        target_lower = target_colorspace.lower()
        if "aces 1.0" in target_lower or "aces 1" in target_lower:
            return "ACES 1.0"
        elif "aces 2.0" in target_lower or "aces 2" in target_lower:
            return "ACES 2.0"
        else:
            return "Unknown"

    def summarize_by_filename(self) -> pd.DataFrame:
        """
        Create summary statistics grouped by filename.

        Returns:
            DataFrame with summary statistics by file
            
        Raises:
            AnalysisError: If summarization fails
        """
        if self.data is None:
            raise AnalysisError("Data not loaded. Call load_data() first.")
            
        # Return cached summary if available
        if self._summary_cache is not None:
            logger.debug("Using cached summary data")
            return self._summary_cache
            
        try:
            summary = self.data.groupby([
                'file_name', 'os_release', 'cpu_model', 'ocio_version', 
                'aces_version'
            ]).agg({
                'avg_time': ['count', 'mean', 'std', 'min', 'max'],
                'min_time': 'min',
                'max_time': 'max'
            }).round(3)

            # Flatten column names
            summary.columns = [
                'operation_count', 'mean_avg_time', 'std_avg_time', 
                'min_avg_time', 'max_avg_time', 'global_min_time', 'global_max_time'
            ]

            result = summary.reset_index()
            
            # Cache the result for future use
            self._summary_cache = result
            logger.debug("Summary data cached for future use")
            
            return result
            
        except Exception as e:
            raise AnalysisError(f"Failed to create summary: {e}")

    def find_cpu_os_comparisons(self) -> pd.DataFrame:
        """
        Find CPU/OS combinations that appear in both r7 and r9 releases.

        Returns:
            DataFrame with comparison data
            
        Raises:
            AnalysisError: If comparison analysis fails
        """
        if self.data is None:
            raise AnalysisError("Data not loaded. Call load_data() first.")
            
        try:
            logger.info("Finding CPU/OS combinations with both r7 and r9 data")
            
            # Group by CPU model, ACES version, and OS release
            grouped = self.data.groupby([
                'cpu_model', 'aces_version', 'os_release'
            ]).agg({
                'avg_time': 'mean',
                'file_name': 'first',
                'ocio_version': 'first'
            }).reset_index()

            # Find CPUs that have both r7 and r9 data for each ACES version
            comparisons = []
            
            for cpu_model in grouped['cpu_model'].unique():
                for aces_version in grouped['aces_version'].unique():
                    cpu_aces_data = grouped[
                        (grouped['cpu_model'] == cpu_model) & 
                        (grouped['aces_version'] == aces_version)
                    ]
                    
                    os_releases = cpu_aces_data['os_release'].unique()
                    
                    if len(os_releases) > 1:
                        logger.info(
                            f"Found CPU '{cpu_model}' with ACES {aces_version} "
                            f"having OS releases: {os_releases}"
                        )
                        
                        # Create all pairwise comparisons
                        for i, os1 in enumerate(os_releases):
                            for os2 in os_releases[i+1:]:
                                data1 = cpu_aces_data[cpu_aces_data['os_release'] == os1].iloc[0]
                                data2 = cpu_aces_data[cpu_aces_data['os_release'] == os2].iloc[0]
                                
                                # Calculate performance difference
                                if data1['avg_time'] > 0 and data2['avg_time'] > 0:
                                    if data1['avg_time'] < data2['avg_time']:
                                        faster_time, slower_time = data1['avg_time'], data2['avg_time']
                                        faster_os, slower_os = os1, os2
                                        faster_file, slower_file = data1['file_name'], data2['file_name']
                                    else:
                                        faster_time, slower_time = data2['avg_time'], data1['avg_time']
                                        faster_os, slower_os = os2, os1
                                        faster_file, slower_file = data2['file_name'], data1['file_name']
                                    
                                    improvement_pct = ((slower_time - faster_time) / slower_time) * 100
                                    
                                    comparisons.append({
                                        'cpu_model': cpu_model,
                                        'aces_version': aces_version,
                                        'faster_os': faster_os,
                                        'slower_os': slower_os,
                                        'faster_time': faster_time,
                                        'slower_time': slower_time,
                                        'improvement_pct': improvement_pct,
                                        'faster_file': faster_file,
                                        'slower_file': slower_file,
                                        'ocio_version': data1['ocio_version']
                                    })

            if not comparisons:
                logger.warning("No CPU/OS comparisons found")
                return pd.DataFrame()
                
            result = pd.DataFrame(comparisons)
            logger.info(f"Found {len(result)} CPU/OS performance comparisons")
            
            return result.sort_values('improvement_pct', ascending=False)
            
        except Exception as e:
            raise AnalysisError(f"Failed to find CPU/OS comparisons: {e}")

    def find_ocio_version_comparisons(self) -> pd.DataFrame:
        """
        Find systems with multiple OCIO versions for comparison.

        Returns:
            DataFrame with OCIO version comparison data
            
        Raises:
            AnalysisError: If comparison analysis fails
        """
        if self.data is None:
            raise AnalysisError("Data not loaded. Call load_data() first.")
            
        try:
            logger.info("Finding OCIO version comparisons")
            
            # Group by system configuration
            grouped = self.data.groupby([
                'cpu_model', 'os_release', 'aces_version', 'ocio_version'
            ]).agg({
                'avg_time': 'mean',
                'file_name': 'first'
            }).reset_index()

            comparisons = []
            
            # Find systems with multiple OCIO versions
            for cpu_model in grouped['cpu_model'].unique():
                for os_release in grouped['os_release'].unique():
                    for aces_version in grouped['aces_version'].unique():
                        system_data = grouped[
                            (grouped['cpu_model'] == cpu_model) & 
                            (grouped['os_release'] == os_release) &
                            (grouped['aces_version'] == aces_version)
                        ]
                        
                        ocio_versions = system_data['ocio_version'].unique()
                        
                        if len(ocio_versions) > 1:
                            logger.info(
                                f"Found system CPU '{cpu_model}', OS '{os_release}', "
                                f"ACES {aces_version} with OCIO versions: {ocio_versions}"
                            )
                            
                            # Create pairwise comparisons
                            for i, ver1 in enumerate(ocio_versions):
                                for ver2 in ocio_versions[i+1:]:
                                    data1 = system_data[system_data['ocio_version'] == ver1].iloc[0]
                                    data2 = system_data[system_data['ocio_version'] == ver2].iloc[0]
                                    
                                    if data1['avg_time'] > 0 and data2['avg_time'] > 0:
                                        if data1['avg_time'] < data2['avg_time']:
                                            faster_time, slower_time = data1['avg_time'], data2['avg_time']
                                            faster_ver, slower_ver = ver1, ver2
                                            faster_file, slower_file = data1['file_name'], data2['file_name']
                                        else:
                                            faster_time, slower_time = data2['avg_time'], data1['avg_time']
                                            faster_ver, slower_ver = ver2, ver1
                                            faster_file, slower_file = data2['file_name'], data1['file_name']
                                        
                                        improvement_pct = ((slower_time - faster_time) / slower_time) * 100
                                        
                                        comparisons.append({
                                            'cpu_model': cpu_model,
                                            'os_release': os_release,
                                            'aces_version': aces_version,
                                            'faster_ocio_version': faster_ver,
                                            'slower_ocio_version': slower_ver,
                                            'faster_time': faster_time,
                                            'slower_time': slower_time,
                                            'improvement_pct': improvement_pct,
                                            'faster_file': faster_file,
                                            'slower_file': slower_file
                                        })

            if not comparisons:
                logger.warning("No OCIO version comparisons found")
                return pd.DataFrame()
                
            result = pd.DataFrame(comparisons)
            logger.info(f"Found {len(result)} OCIO version performance comparisons")
            
            return result.sort_values('improvement_pct', ascending=False)
            
        except Exception as e:
            raise AnalysisError(f"Failed to find OCIO version comparisons: {e}")

    def find_all_ocio_version_comparisons(self) -> pd.DataFrame:
        """
        Find all OCIO version comparisons regardless of system configuration.

        Returns:
            DataFrame with comprehensive OCIO version comparison data
            
        Raises:
            AnalysisError: If comparison analysis fails
        """
        if self.data is None:
            raise AnalysisError("Data not loaded. Call load_data() first.")
            
        try:
            logger.info("Finding all OCIO version comparisons")
            
            # Group by OCIO version and ACES version
            grouped = self.data.groupby(['ocio_version', 'aces_version']).agg({
                'avg_time': 'mean',
                'cpu_model': 'nunique',
                'os_release': 'nunique',
                'file_name': 'nunique'
            }).reset_index()

            grouped.columns = [
                'ocio_version', 'aces_version', 'mean_avg_time',
                'cpu_count', 'os_count', 'file_count'
            ]
            
            logger.info(f"Found {len(grouped)} OCIO version/ACES combinations")
            
            return grouped.sort_values(['aces_version', 'mean_avg_time'])
            
        except Exception as e:
            raise AnalysisError(f"Failed to find all OCIO version comparisons: {e}")

    def get_performance_summary(self) -> Dict[str, any]:
        """
        Get overall performance summary statistics.

        Returns:
            Dictionary with summary statistics
            
        Raises:
            AnalysisError: If summary generation fails
        """
        if self.data is None:
            raise AnalysisError("Data not loaded. Call load_data() first.")
            
        try:
            summary = {
                'total_results': len(self.data),
                'unique_files': self.data['file_name'].nunique(),
                'unique_cpus': self.data['cpu_model'].nunique(),
                'unique_os_releases': self.data['os_release'].nunique(),
                'ocio_versions': sorted(self.data['ocio_version'].unique()),
                'aces_versions': sorted(self.data['aces_version'].unique()),
                'avg_time_stats': {
                    'mean': self.data['avg_time'].mean(),
                    'median': self.data['avg_time'].median(),
                    'std': self.data['avg_time'].std(),
                    'min': self.data['avg_time'].min(),
                    'max': self.data['avg_time'].max()
                }
            }
            
            return summary
            
        except Exception as e:
            raise AnalysisError(f"Failed to generate performance summary: {e}")

    # Statistical utility methods
    
    def get_outliers(self, column: str = 'avg_time', threshold: float = 2.0) -> pd.DataFrame:
        """
        Identify outliers in performance data using z-score method.
        
        Args:
            column: Column to analyze for outliers
            threshold: Z-score threshold for outlier detection
            
        Returns:
            DataFrame containing outlier records
            
        Raises:
            AnalysisError: If outlier detection fails
        """
        if self.data is None:
            raise AnalysisError("Data not loaded. Call load_data() first.")
            
        try:
            if column not in self.data.columns:
                raise AnalysisError(f"Column '{column}' not found in data")
                
            # Calculate z-scores
            mean_val = self.data[column].mean()
            std_val = self.data[column].std()
            
            if std_val == 0:
                logger.warning(f"Standard deviation is zero for column '{column}', no outliers detected")
                return pd.DataFrame()
                
            z_scores = abs((self.data[column] - mean_val) / std_val)
            outlier_mask = z_scores > threshold
            
            outliers = self.data[outlier_mask].copy()
            outliers['z_score'] = z_scores[outlier_mask]
            
            logger.info(f"Found {len(outliers)} outliers in '{column}' with z-score > {threshold}")
            
            return outliers.sort_values('z_score', ascending=False)
            
        except Exception as e:
            raise AnalysisError(f"Failed to detect outliers: {e}")
    
    def get_performance_percentiles(self, column: str = 'avg_time') -> Dict[str, float]:
        """
        Calculate performance percentiles for the specified column.
        
        Args:
            column: Column to analyze
            
        Returns:
            Dictionary with percentile values
            
        Raises:
            AnalysisError: If percentile calculation fails
        """
        if self.data is None:
            raise AnalysisError("Data not loaded. Call load_data() first.")
            
        try:
            if column not in self.data.columns:
                raise AnalysisError(f"Column '{column}' not found in data")
                
            percentiles = {
                'p5': self.data[column].quantile(0.05),
                'p10': self.data[column].quantile(0.10),
                'p25': self.data[column].quantile(0.25),
                'p50': self.data[column].quantile(0.50),  # median
                'p75': self.data[column].quantile(0.75),
                'p90': self.data[column].quantile(0.90),
                'p95': self.data[column].quantile(0.95),
                'p99': self.data[column].quantile(0.99)
            }
            
            return percentiles
            
        except Exception as e:
            raise AnalysisError(f"Failed to calculate percentiles: {e}")
    
    def compare_groups(self, group_column: str, value_column: str = 'avg_time') -> pd.DataFrame:
        """
        Compare performance across different groups.
        
        Args:
            group_column: Column to group by
            value_column: Column to analyze
            
        Returns:
            DataFrame with group comparison statistics
            
        Raises:
            AnalysisError: If group comparison fails
        """
        if self.data is None:
            raise AnalysisError("Data not loaded. Call load_data() first.")
            
        try:
            if group_column not in self.data.columns:
                raise AnalysisError(f"Group column '{group_column}' not found in data")
            if value_column not in self.data.columns:
                raise AnalysisError(f"Value column '{value_column}' not found in data")
                
            comparison = self.data.groupby(group_column)[value_column].agg([
                'count', 'mean', 'median', 'std', 'min', 'max'
            ]).round(3)
            
            # Add coefficient of variation (CV)
            comparison['cv'] = (comparison['std'] / comparison['mean'] * 100).round(2)
            
            # Calculate relative performance (percentage of overall mean)
            overall_mean = self.data[value_column].mean()
            comparison['relative_performance'] = (comparison['mean'] / overall_mean * 100).round(1)
            
            return comparison.sort_values('mean')
            
        except Exception as e:
            raise AnalysisError(f"Failed to compare groups: {e}")
    
    @lru_cache(maxsize=128)
    def _cached_categorize_aces_version(self, target_colorspace: str) -> str:
        """
        Cached version of ACES version categorization for better performance.
        
        Args:
            target_colorspace: The target colorspace string

        Returns:
            ACES version ("ACES 1.0" or "ACES 2.0")
        """
        return self._categorize_aces_version(target_colorspace)
    
    def get_data_info(self) -> Dict[str, any]:
        """
        Get comprehensive information about the loaded data.
        
        Returns:
            Dictionary with data information
        """
        if self.data is None:
            return {"status": "No data loaded"}
            
        info = {
            "status": "Data loaded",
            "shape": self.data.shape,
            "columns": list(self.data.columns),
            "memory_usage_mb": round(self.data.memory_usage(deep=True).sum() / 1024**2, 2),
            "null_counts": self.data.isnull().sum().to_dict(),
            "data_types": self.data.dtypes.to_dict(),
            "csv_file": str(self.csv_file) if self.csv_file else None,
            "cached_summary": self._summary_cache is not None
        }
        
        return info
