"""
OCIO Performance Analyzer - Refactored

Orchestrates data analysis, chart generation, and report creation
using focused, single-responsibility components.
"""

from pathlib import Path
from typing import Optional

from .chart_generator import OCIOChartGenerator
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


# Backward compatibility alias
OCIOAnalyzer = OCIOPerformanceAnalyzer
