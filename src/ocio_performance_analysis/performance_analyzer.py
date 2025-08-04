"""
OCIO Performance Analyzer - Refactored

Orchestrates data analysis, chart generation, and report creation
using focused, single-responsibility components.
"""

import concurrent.futures
from pathlib import Path
from typing import Optional, List, Callable, Dict

from .chart_generator import OCIOChartGenerator
from .config import get_config
from .data_analyzer import OCIODataAnalyzer
from .exceptions import AnalysisError, ConfigurationError
from .logging_config import get_logger
from .report_generator import OCIOReportGenerator

logger = get_logger(__name__)


class OCIOPerformanceAnalyzer:
    """
    Main analyzer class that orchestrates the complete OCIO performance analysis pipeline.
    
    This refactored version separates concerns into focused components:
    - OCIODataAnalyzer: Data processing and statistical analysis
    - OCIOChartGenerator: Chart and visualization creation
    - OCIOReportGenerator: Text report generation
    """

    def __init__(self, csv_file: Optional[Path] = None):
        """
        Initialize the performance analyzer.

        Args:
            csv_file: Path to the CSV file containing test results (optional)
            
        Raises:
            FileNotFoundError: If the CSV file doesn't exist
        """
        self.csv_file = csv_file
        self.data_analyzer = OCIODataAnalyzer(csv_file) if csv_file else None
        self.chart_generator = OCIOChartGenerator()
        self.report_generator = OCIOReportGenerator()
        
        # Initialize data
        self.data = None
        self.summary_data = None

    def run_full_analysis(self, output_dir: Path) -> None:
        """
        Run the complete analysis pipeline.

        Args:
            output_dir: Directory to save all output files
            
        Raises:
            AnalysisError: If analysis fails
            ConfigurationError: If no CSV file was provided
        """
        try:
            if not self.data_analyzer:
                raise ConfigurationError("No CSV file provided. Initialize with a CSV file to run analysis.")
                
            logger.info("Starting full OCIO performance analysis")
            
            # Ensure output directory exists
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # 1. Load and analyze data
            logger.info("Step 1: Loading and analyzing data")
            self.data = self.data_analyzer.load_data()
            self.summary_data = self.data_analyzer.summarize_by_filename()
            
            # 2. Generate comparisons
            logger.info("Step 2: Generating performance comparisons")
            cpu_os_comparisons = self.data_analyzer.find_cpu_os_comparisons()
            ocio_comparisons = self.data_analyzer.find_ocio_version_comparisons()
            all_ocio_comparisons = self.data_analyzer.find_all_ocio_version_comparisons()
            performance_stats = self.data_analyzer.get_performance_summary()
            
            # 3. Create visualizations
            logger.info("Step 3: Creating charts and visualizations")
            self._create_all_charts(output_dir, cpu_os_comparisons, 
                                  ocio_comparisons, all_ocio_comparisons)
            
            # 4. Generate reports
            logger.info("Step 4: Generating text reports")
            self._create_all_reports(output_dir, cpu_os_comparisons, 
                                   ocio_comparisons, performance_stats)
            
            logger.info(f"✅ Full analysis complete. Results saved to: {output_dir}")
            
        except Exception as e:
            raise AnalysisError(f"Full analysis failed: {e}")

    def load_csv_file(self, csv_file: Path) -> None:
        """
        Load a CSV file for analysis.
        
        Args:
            csv_file: Path to the CSV file containing test results
            
        Raises:
            FileNotFoundError: If the CSV file doesn't exist
        """
        self.csv_file = csv_file
        self.data_analyzer = OCIODataAnalyzer(csv_file)
        self.data = None
        self.summary_data = None

    def _create_all_charts(self, output_dir: Path, 
                          cpu_os_comparisons, ocio_comparisons, 
                          all_ocio_comparisons) -> None:
        """Create all chart visualizations."""
        try:
            # Summary plot
            summary_plot_path = output_dir / "summary_analysis.png"
            self.chart_generator.create_summary_plot(self.summary_data, summary_plot_path)
            
            # CPU/OS comparison plot
            if not cpu_os_comparisons.empty:
                cpu_os_plot_path = output_dir / "cpu_os_comparison.png"
                self.chart_generator.create_comparison_plot(
                    cpu_os_comparisons, 
                    "CPU/OS Performance Comparison", 
                    cpu_os_plot_path
                )
            
            # OCIO version comparison plot
            if not ocio_comparisons.empty:
                ocio_plot_path = output_dir / "ocio_version_comparison.png"
                self.chart_generator.create_comparison_plot(
                    ocio_comparisons, 
                    "OCIO Version Performance Comparison", 
                    ocio_plot_path
                )
            
            # ACES comparison plot
            if not all_ocio_comparisons.empty:
                aces_plot_path = output_dir / "comprehensive_aces_comparison.png"
                self.chart_generator.create_aces_comparison_plot(
                    all_ocio_comparisons, 
                    aces_plot_path
                )
            
            # Performance heatmap
            heatmap_path = output_dir / "performance_heatmap.png"
            self.chart_generator.create_performance_heatmap(self.summary_data, heatmap_path)
            
        except Exception as e:
            logger.error(f"Chart generation failed: {e}")
            raise

    def _create_all_reports(self, output_dir: Path, 
                           cpu_os_comparisons, ocio_comparisons, 
                           performance_stats) -> None:
        """Create all text reports."""
        try:
            # Summary report
            summary_report_path = output_dir / "analysis_summary.txt"
            self.report_generator.create_summary_report(
                self.summary_data, performance_stats, summary_report_path
            )
            
            # CPU/OS comparison report
            if not cpu_os_comparisons.empty:
                cpu_os_report_path = output_dir / "cpu_os_comparison_report.txt"
                self.report_generator.create_comparison_report(
                    cpu_os_comparisons, 
                    "CPU/OS Performance Comparison Report",
                    cpu_os_report_path
                )
            
            # OCIO version comparison report
            if not ocio_comparisons.empty:
                ocio_report_path = output_dir / "ocio_version_comparison_report.txt"
                self.report_generator.create_comparison_report(
                    ocio_comparisons, 
                    "OCIO Version Performance Comparison Report",
                    ocio_report_path
                )
            
            # Detailed findings report
            findings_report_path = output_dir / "detailed_findings.txt"
            self.report_generator.create_detailed_findings_report(
                cpu_os_comparisons, ocio_comparisons, 
                self.summary_data, findings_report_path
            )
            
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            raise

    def get_quick_summary(self) -> dict:
        """
        Get a quick summary of the analysis for API/programmatic use.

        Returns:
            Dictionary with key analysis results
            
        Raises:
            AnalysisError: If summary generation fails
        """
        try:
            if self.data is None:
                self.data = self.data_analyzer.load_data()
            
            if self.summary_data is None:
                self.summary_data = self.data_analyzer.summarize_by_filename()
            
            performance_stats = self.data_analyzer.get_performance_summary()
            cpu_os_comparisons = self.data_analyzer.find_cpu_os_comparisons()
            ocio_comparisons = self.data_analyzer.find_ocio_version_comparisons()
            
            return {
                'total_results': performance_stats['total_results'],
                'unique_systems': performance_stats['unique_cpus'],
                'ocio_versions': performance_stats['ocio_versions'],
                'aces_versions': performance_stats['aces_versions'],
                'avg_performance': performance_stats['avg_time_stats']['mean'],
                'cpu_os_comparisons_found': len(cpu_os_comparisons),
                'ocio_comparisons_found': len(ocio_comparisons),
                'best_cpu_os_improvement': (
                    cpu_os_comparisons.iloc[0]['improvement_pct'] 
                    if not cpu_os_comparisons.empty else 0
                ),
                'best_ocio_improvement': (
                    ocio_comparisons.iloc[0]['improvement_pct'] 
                    if not ocio_comparisons.empty else 0
                )
            }
            
        except Exception as e:
            raise AnalysisError(f"Quick summary generation failed: {e}")

    def run_parallel_analysis(self, output_dir: Path, max_workers: Optional[int] = None) -> None:
        """
        Run analysis with parallel processing for better performance.
        
        Args:
            output_dir: Directory to save all output files
            max_workers: Maximum number of worker threads (uses config default if None)
        """
        try:
            config = get_config()
            if not config.parallel_processing:
                logger.info("Parallel processing disabled, falling back to sequential analysis")
                return self.run_full_analysis(output_dir)
                
            if not self.data_analyzer:
                raise ConfigurationError("No CSV file provided. Initialize with a CSV file to run analysis.")
                
            max_workers = max_workers or config.max_workers
            logger.info(f"Starting parallel OCIO performance analysis with {max_workers} workers")
            
            # Ensure output directory exists
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Step 1: Load and analyze data (sequential - shared state)
            logger.info("Step 1: Loading and analyzing data")
            self.data = self.data_analyzer.load_data()
            self.summary_data = self.data_analyzer.summarize_by_filename()
            
            # Step 2: Generate comparisons (can be parallelized)
            logger.info("Step 2: Generating performance comparisons (parallel)")
            
            comparison_tasks = [
                ('cpu_os', self.data_analyzer.find_cpu_os_comparisons),
                ('ocio', self.data_analyzer.find_ocio_version_comparisons),
                ('all_ocio', self.data_analyzer.find_all_ocio_version_comparisons)
            ]
            
            comparison_results = {}
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_name = {
                    executor.submit(task): name 
                    for name, task in comparison_tasks
                }
                
                for future in concurrent.futures.as_completed(future_to_name):
                    name = future_to_name[future]
                    try:
                        comparison_results[name] = future.result()
                        logger.info(f"Completed {name} comparisons")
                    except Exception as e:
                        logger.error(f"Failed to generate {name} comparisons: {e}")
                        comparison_results[name] = None
            
            # Step 3: Generate outputs in parallel
            logger.info("Step 3: Generating charts and reports (parallel)")
            
            output_tasks = []
            
            # Chart generation tasks
            chart_tasks = [
                ('summary_chart', self._create_summary_chart, (output_dir,)),
                ('comparison_charts', self._create_comparison_charts, 
                 (output_dir, comparison_results['cpu_os'], comparison_results['ocio'], 
                  comparison_results['all_ocio']))
            ]
            
            # Report generation tasks  
            report_tasks = [
                ('summary_report', self._create_summary_report, (output_dir,)),
                ('comparison_reports', self._create_comparison_reports,
                 (output_dir, comparison_results['cpu_os'], comparison_results['ocio']))
            ]
            
            output_tasks.extend(chart_tasks + report_tasks)
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_task = {
                    executor.submit(task_func, *args): task_name
                    for task_name, task_func, args in output_tasks
                }
                
                for future in concurrent.futures.as_completed(future_to_task):
                    task_name = future_to_task[future]
                    try:
                        future.result()
                        logger.info(f"Completed {task_name}")
                    except Exception as e:
                        logger.error(f"Failed to generate {task_name}: {e}")
            
            logger.info(f"✅ Parallel analysis complete. Results saved to: {output_dir}")
            
        except Exception as e:
            raise AnalysisError(f"Parallel analysis failed: {e}")
    
    def _create_summary_chart(self, output_dir: Path) -> None:
        """Create summary chart (helper for parallel execution)."""
        summary_plot_path = output_dir / "summary_analysis.png"
        self.chart_generator.create_summary_plot(self.summary_data, summary_plot_path)
    
    def _create_comparison_charts(self, output_dir: Path, cpu_os_comparisons, 
                                ocio_comparisons, all_ocio_comparisons) -> None:
        """Create comparison charts (helper for parallel execution)."""
        if cpu_os_comparisons is not None and not cpu_os_comparisons.empty:
            cpu_os_plot_path = output_dir / "cpu_os_comparison.png"
            self.chart_generator.create_comparison_plot(
                cpu_os_comparisons, "CPU/OS Performance Comparison", cpu_os_plot_path
            )
        
        if ocio_comparisons is not None and not ocio_comparisons.empty:
            ocio_plot_path = output_dir / "ocio_version_comparison.png"
            self.chart_generator.create_comparison_plot(
                ocio_comparisons, "OCIO Version Performance Comparison", ocio_plot_path
            )
        
        if all_ocio_comparisons is not None and not all_ocio_comparisons.empty:
            aces_plot_path = output_dir / "comprehensive_aces_comparison.png"
            self.chart_generator.create_aces_comparison_plot(all_ocio_comparisons, aces_plot_path)
    
    def _create_summary_report(self, output_dir: Path) -> None:
        """Create summary report (helper for parallel execution)."""
        summary_report_path = output_dir / "analysis_summary.txt"
        summary_stats = self.data_analyzer.get_performance_summary()
        self.report_generator.create_summary_report(summary_stats, summary_report_path)
    
    def _create_comparison_reports(self, output_dir: Path, cpu_os_comparisons, ocio_comparisons) -> None:
        """Create comparison reports (helper for parallel execution)."""
        if cpu_os_comparisons is not None and not cpu_os_comparisons.empty:
            os_report_path = output_dir / "os_comparison_report.txt"
            self.report_generator.create_comparison_report(
                cpu_os_comparisons, "CPU/OS Comparison Report", os_report_path
            )
        
        if ocio_comparisons is not None and not ocio_comparisons.empty:
            ocio_report_path = output_dir / "ocio_version_comparison_report.txt"
            self.report_generator.create_comparison_report(
                ocio_comparisons, "OCIO Version Comparison Report", ocio_report_path
            )
    
    def batch_process_files(self, csv_files: List[Path], output_base_dir: Path,
                          max_workers: Optional[int] = None) -> Dict[str, bool]:
        """
        Process multiple CSV files in parallel.
        
        Args:
            csv_files: List of CSV files to process
            output_base_dir: Base directory for output (subdirs created per file)
            max_workers: Maximum number of worker threads
            
        Returns:
            Dictionary mapping file names to success status
        """
        try:
            config = get_config()
            max_workers = max_workers or config.max_workers
            
            logger.info(f"Starting batch processing of {len(csv_files)} files with {max_workers} workers")
            
            results = {}
            
            def process_single_file(csv_file: Path) -> tuple:
                """Process a single CSV file."""
                try:
                    file_analyzer = OCIOPerformanceAnalyzer(csv_file)
                    output_dir = output_base_dir / csv_file.stem
                    
                    if config.parallel_processing:
                        file_analyzer.run_parallel_analysis(output_dir)
                    else:
                        file_analyzer.run_full_analysis(output_dir)
                        
                    return (csv_file.name, True, None)
                except Exception as e:
                    return (csv_file.name, False, str(e))
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_file = {
                    executor.submit(process_single_file, csv_file): csv_file
                    for csv_file in csv_files
                }
                
                for future in concurrent.futures.as_completed(future_to_file):
                    csv_file = future_to_file[future]
                    try:
                        file_name, success, error = future.result()
                        results[file_name] = success
                        if success:
                            logger.info(f"✅ Successfully processed {file_name}")
                        else:
                            logger.error(f"❌ Failed to process {file_name}: {error}")
                    except Exception as e:
                        results[csv_file.name] = False
                        logger.error(f"❌ Unexpected error processing {csv_file.name}: {e}")
            
            successful = sum(1 for success in results.values() if success)
            logger.info(f"Batch processing complete: {successful}/{len(csv_files)} files processed successfully")
            
            return results
            
        except Exception as e:
            raise AnalysisError(f"Batch processing failed: {e}")


# Backward compatibility alias
OCIOAnalyzer = OCIOPerformanceAnalyzer
