"""
OCIO Data Analysis Module

Handles data processing, comparisons, and statistical analysis
for OCIO performance test results.
"""

from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd

from .exceptions import AnalysisError, DataValidationError, FileNotFoundError as OCIOFileNotFoundError
from .logging_config import get_logger

logger = get_logger(__name__)


class OCIODataAnalyzer:
    """Handles data analysis and comparison operations for OCIO performance data."""

    def __init__(self, csv_file: Path):
        """
        Initialize the data analyzer.

        Args:
            csv_file: Path to the CSV file containing test results
            
        Raises:
            FileNotFoundError: If the CSV file doesn't exist
        """
        if not csv_file.exists():
            raise OCIOFileNotFoundError(f"CSV file not found: {csv_file}")
            
        self.csv_file = csv_file
        self.data = None

    def load_data(self) -> pd.DataFrame:
        """
        Load test results from CSV file.

        Returns:
            DataFrame containing the test results
            
        Raises:
            AnalysisError: If data loading fails
            DataValidationError: If data is invalid
        """
        try:
            logger.info(f"Loading data from {self.csv_file}")
            self.data = pd.read_csv(self.csv_file)
            
            if self.data.empty:
                raise DataValidationError("CSV file contains no data")
                
            logger.info(f"Loaded {len(self.data)} test results")
            
            # Add ACES version categorization
            self.data['aces_version'] = self.data['target_colorspace'].apply(
                self._categorize_aces_version
            )
            
            return self.data
            
        except Exception as e:
            if isinstance(e, (DataValidationError, OCIOFileNotFoundError)):
                raise
            raise AnalysisError(f"Failed to load data from {self.csv_file}: {e}")

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

            return summary.reset_index()
            
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
