"""
OCIO Test Results Parser

This module parses OCIO test result files and converts them to CSV format.
Each test run contains multiple iterations with timing statistics.
"""

import re
import csv
from pathlib import Path
from typing import List
from dataclasses import dataclass, asdict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Data class representing a single test result measurement."""
    
    file_name: str
    os_release: str
    cpu_model: str
    ocio_version: str
    config_version: str
    source_colorspace: str
    target_colorspace: str
    operation: str
    iteration_count: int
    timing_values: List[float]
    min_time: float
    max_time: float
    avg_time: float
    
    def __post_init__(self):
        """Calculate min, max, and average times from timing values."""
        if self.timing_values:
            self.min_time = min(self.timing_values)
            self.max_time = max(self.timing_values)
            self.avg_time = sum(self.timing_values) / len(self.timing_values)
        else:
            self.min_time = self.max_time = self.avg_time = 0.0


class OCIOTestParser:
    """Parser for OCIO test result files."""
    
    def __init__(self):
        """Initialize the parser with regex patterns."""
        self.version_pattern = re.compile(r'OCIO Version:\s*(.+)')
        self.config_version_pattern = re.compile(r'OCIO Config\. version:\s*(.+)')
        self.processing_pattern = re.compile(r"Processing from '(.+)' to '(.+)'")
        self.timing_pattern = re.compile(
            r'(.+?):\s+For (\d+) iterations, it took: \[([0-9.,\s]+)\] ms'
        )
        self.os_release_pattern = re.compile(r'_r(\d+)(?:_|\.)')
        self.cpu_model_pattern = re.compile(r'model name\s*:\s*(.+)')
    
    def _extract_os_release(self, file_name: str) -> str:
        """
        Extract OS release (r7, r9, etc.) from file name.
        
        Args:
            file_name: Name of the file
            
        Returns:
            OS release string (e.g., 'r7', 'r9') or 'Unknown' if not found
        """
        match = self.os_release_pattern.search(file_name)
        if match:
            return f"r{match.group(1)}"
        return "Unknown"
    
    def _extract_cpu_model(self, content: str) -> str:
        """
        Extract CPU model name from file content.
        
        Args:
            content: Content of the file
            
        Returns:
            CPU model name or 'Unknown' if not found
        """
        match = self.cpu_model_pattern.search(content)
        if match:
            return match.group(1).strip()
        return "Unknown"
    
    def parse_file(self, file_path: Path) -> List[TestResult]:
        """
        Parse a single OCIO test result file.
        
        Args:
            file_path: Path to the test result file
            
        Returns:
            List of TestResult objects
        """
        results = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
        except UnicodeDecodeError:
            # Try with different encoding if UTF-8 fails
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    content = file.read()
            except Exception as e:
                logger.error(f"Failed to read file {file_path}: {e}")
                return results
        
        # Extract CPU model information from the entire file content
        cpu_model = self._extract_cpu_model(content)
        
        # Split content by test runs (separated by OCIO Version)
        test_runs = re.split(r'\n\nOCIO Version:', content)
        
        for i, test_run in enumerate(test_runs):
            if not test_run.strip():
                continue
                
            # Add back the "OCIO Version:" prefix if it was split
            if i > 0:
                test_run = "OCIO Version:" + test_run
            
            test_results = self._parse_test_run(test_run, file_path.name, cpu_model)
            results.extend(test_results)
        
        return results
    
    def _parse_test_run(self, content: str, file_name: str, cpu_model: str) -> List[TestResult]:
        """
        Parse a single test run within a file.
        
        Args:
            content: Content of the test run
            file_name: Name of the file being parsed
            cpu_model: CPU model name extracted from the file
            
        Returns:
            List of TestResult objects for this test run
        """
        results = []
        
        # Extract OCIO version
        version_match = self.version_pattern.search(content)
        ocio_version = version_match.group(1).strip() if version_match else "Unknown"
        
        # Extract config version
        config_match = self.config_version_pattern.search(content)
        config_version = config_match.group(1).strip() if config_match else "Unknown"
        
        # Extract processing information (source and target colorspaces)
        processing_match = self.processing_pattern.search(content)
        source_colorspace = processing_match.group(1) if processing_match else "Unknown"
        target_colorspace = processing_match.group(2) if processing_match else "Unknown"
        
        # Extract all timing measurements
        timing_matches = self.timing_pattern.findall(content)
        
        for operation, iteration_count, timing_str in timing_matches:
            # Parse timing values
            timing_values = []
            for value_str in timing_str.split(','):
                try:
                    timing_values.append(float(value_str.strip()))
                except ValueError:
                    logger.warning(f"Could not parse timing value: {value_str}")
            
            if timing_values:
                result = TestResult(
                    file_name=file_name,
                    os_release=self._extract_os_release(file_name),
                    cpu_model=cpu_model,
                    ocio_version=ocio_version,
                    config_version=config_version,
                    source_colorspace=source_colorspace,
                    target_colorspace=target_colorspace,
                    operation=operation.strip(),
                    iteration_count=int(iteration_count),
                    timing_values=timing_values,
                    min_time=0.0,  # Will be calculated in __post_init__
                    max_time=0.0,
                    avg_time=0.0
                )
                results.append(result)
        
        return results
    
    def parse_directory(self, directory_path: Path) -> List[TestResult]:
        """
        Parse all OCIO test result files in a directory.
        
        Args:
            directory_path: Path to the directory containing test files
            
        Returns:
            List of all TestResult objects from all files
        """
        all_results = []
        
        # Find all .txt files in the directory
        txt_files = list(directory_path.glob("*.txt"))
        
        logger.info(f"Found {len(txt_files)} .txt files to parse")
        
        for file_path in txt_files:
            logger.info(f"Parsing file: {file_path.name}")
            file_results = self.parse_file(file_path)
            all_results.extend(file_results)
            logger.info(f"Extracted {len(file_results)} test results from {file_path.name}")
        
        return all_results
    
    def save_to_csv(self, results: List[TestResult], output_file: Path) -> None:
        """
        Save test results to a CSV file.
        
        Args:
            results: List of TestResult objects
            output_file: Path to the output CSV file
        """
        if not results:
            logger.warning("No results to save")
            return
        
        logger.info(f"Saving {len(results)} results to {output_file}")
        
        fieldnames = [
            'file_name', 'os_release', 'cpu_model', 'ocio_version', 'config_version', 'source_colorspace',
            'target_colorspace', 'operation', 'iteration_count', 'min_time',
            'max_time', 'avg_time', 'timing_values'
        ]
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in results:
                row = asdict(result)
                # Convert timing_values list to string for CSV
                row['timing_values'] = ','.join(map(str, result.timing_values))
                writer.writerow(row)
        
        logger.info(f"Successfully saved results to {output_file}")


def main():
    """Main function to run the parser."""
    # Set up paths
    script_dir = Path(__file__).parent
    ocio_tests_dir = script_dir / "OCIO_tests"
    output_file = script_dir / "ocio_test_results.csv"
    
    # Create parser and process files
    parser = OCIOTestParser()
    
    if not ocio_tests_dir.exists():
        logger.error(f"OCIO tests directory not found: {ocio_tests_dir}")
        return
    
    # Parse all files
    results = parser.parse_directory(ocio_tests_dir)
    
    # Save to CSV
    parser.save_to_csv(results, output_file)
    
    logger.info(f"Processing complete. Total results: {len(results)}")


if __name__ == "__main__":
    main()
