"""
OCIO Report Generation Module

Handles creation of text reports and analysis summaries
for OCIO performance data.
"""

from pathlib import Path
from typing import Dict, List

import pandas as pd

from .exceptions import AnalysisError
from .logging_config import get_logger

logger = get_logger(__name__)


class OCIOReportGenerator:
    """Handles text report generation for OCIO performance analysis."""

    def __init__(self):
        """Initialize the report generator."""
        pass

    def create_summary_report(self, summary_data: pd.DataFrame, 
                            performance_stats: Dict, 
                            output_path: Path) -> None:
        """
        Create a comprehensive summary report.

        Args:
            summary_data: DataFrame with summary statistics
            performance_stats: Dictionary with performance statistics
            output_path: Path to save the report
            
        Raises:
            AnalysisError: If report creation fails
        """
        try:
            logger.info("Creating summary report")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("OCIO Performance Analysis Summary Report\n")
                f.write("=" * 50 + "\n\n")
                
                # Overall statistics
                f.write("OVERALL STATISTICS\n")
                f.write("-" * 20 + "\n")
                f.write(f"Total test results: {performance_stats.get('total_results', 0)}\n")
                f.write(f"Unique files analyzed: {performance_stats.get('unique_files', 0)}\n")
                f.write(f"Unique CPU models: {performance_stats.get('unique_cpus', 0)}\n")
                f.write(f"Unique OS releases: {performance_stats.get('unique_os_releases', 0)}\n")
                
                ocio_versions = performance_stats.get('ocio_versions', [])
                f.write(f"OCIO versions tested: {', '.join(map(str, ocio_versions))}\n")
                
                aces_versions = performance_stats.get('aces_versions', [])
                f.write(f"ACES versions: {', '.join(aces_versions)}\n\n")
                
                # Performance statistics
                avg_stats = performance_stats.get('avg_time_stats', {})
                if avg_stats:
                    f.write("PERFORMANCE STATISTICS\n")
                    f.write("-" * 25 + "\n")
                    f.write(f"Mean execution time: {avg_stats.get('mean', 0):.3f} ms\n")
                    f.write(f"Median execution time: {avg_stats.get('median', 0):.3f} ms\n")
                    f.write(f"Standard deviation: {avg_stats.get('std', 0):.3f} ms\n")
                    f.write(f"Minimum time: {avg_stats.get('min', 0):.3f} ms\n")
                    f.write(f"Maximum time: {avg_stats.get('max', 0):.3f} ms\n\n")
                
                # Top performing systems
                if not summary_data.empty and 'mean_avg_time' in summary_data.columns:
                    f.write("TOP PERFORMING SYSTEMS\n")
                    f.write("-" * 25 + "\n")
                    top_systems = summary_data.nsmallest(5, 'mean_avg_time')
                    
                    for idx, system in top_systems.iterrows():
                        f.write(f"{idx + 1}. {system.get('file_name', 'Unknown')}\n")
                        f.write(f"   CPU: {system.get('cpu_model', 'Unknown')}\n")
                        f.write(f"   OS: {system.get('os_release', 'Unknown')}\n")
                        f.write(f"   OCIO: {system.get('ocio_version', 'Unknown')}\n")
                        f.write(f"   ACES: {system.get('aces_version', 'Unknown')}\n")
                        f.write(f"   Avg Time: {system.get('mean_avg_time', 0):.3f} ms\n\n")
                
                f.write(f"Report generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            logger.info(f"Summary report saved to {output_path}")
            
        except Exception as e:
            raise AnalysisError(f"Failed to create summary report: {e}")

    def create_comparison_report(self, comparison_data: pd.DataFrame,
                               report_title: str,
                               output_path: Path) -> None:
        """
        Create a detailed comparison report.

        Args:
            comparison_data: DataFrame with comparison data
            report_title: Title for the report
            output_path: Path to save the report
            
        Raises:
            AnalysisError: If report creation fails
        """
        try:
            logger.info(f"Creating comparison report: {report_title}")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"{report_title}\n")
                f.write("=" * len(report_title) + "\n\n")
                
                if comparison_data.empty:
                    f.write("No comparison data available.\n")
                    return
                
                f.write(f"Total comparisons found: {len(comparison_data)}\n\n")
                
                # Top improvements
                if 'improvement_pct' in comparison_data.columns:
                    f.write("TOP PERFORMANCE IMPROVEMENTS\n")
                    f.write("-" * 35 + "\n")
                    
                    top_improvements = comparison_data.nlargest(10, 'improvement_pct')
                    
                    for idx, comparison in top_improvements.iterrows():
                        f.write(f"{idx + 1}. Improvement: {comparison['improvement_pct']:.1f}%\n")
                        
                        if 'cpu_model' in comparison:
                            f.write(f"   CPU: {self._truncate_text(comparison['cpu_model'], 50)}\n")
                        
                        if 'faster_time' in comparison and 'slower_time' in comparison:
                            f.write(f"   Faster: {comparison['faster_time']:.3f} ms\n")
                            f.write(f"   Slower: {comparison['slower_time']:.3f} ms\n")
                        
                        # Add specific comparison details based on columns
                        if 'faster_os' in comparison:
                            f.write(f"   Faster OS: {comparison['faster_os']}\n")
                            f.write(f"   Slower OS: {comparison['slower_os']}\n")
                        
                        if 'faster_ocio_version' in comparison:
                            f.write(f"   Faster OCIO: {comparison['faster_ocio_version']}\n")
                            f.write(f"   Slower OCIO: {comparison['slower_ocio_version']}\n")
                        
                        f.write("\n")
                
                # Summary statistics
                if 'improvement_pct' in comparison_data.columns:
                    f.write("IMPROVEMENT STATISTICS\n")
                    f.write("-" * 25 + "\n")
                    improvements = comparison_data['improvement_pct']
                    f.write(f"Average improvement: {improvements.mean():.1f}%\n")
                    f.write(f"Median improvement: {improvements.median():.1f}%\n")
                    f.write(f"Maximum improvement: {improvements.max():.1f}%\n")
                    f.write(f"Minimum improvement: {improvements.min():.1f}%\n")
                    f.write(f"Standard deviation: {improvements.std():.1f}%\n\n")
                
                f.write(f"Report generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            logger.info(f"Comparison report saved to {output_path}")
            
        except Exception as e:
            raise AnalysisError(f"Failed to create comparison report: {e}")

    def create_detailed_findings_report(self, 
                                      cpu_os_comparisons: pd.DataFrame,
                                      ocio_comparisons: pd.DataFrame,
                                      summary_data: pd.DataFrame,
                                      output_path: Path) -> None:
        """
        Create a detailed findings report with key insights.

        Args:
            cpu_os_comparisons: DataFrame with CPU/OS comparison data
            ocio_comparisons: DataFrame with OCIO version comparison data
            summary_data: DataFrame with summary statistics
            output_path: Path to save the report
            
        Raises:
            AnalysisError: If report creation fails
        """
        try:
            logger.info("Creating detailed findings report")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("OCIO Performance Analysis - Detailed Findings\n")
                f.write("=" * 50 + "\n\n")
                
                # Key Findings Section
                f.write("KEY FINDINGS\n")
                f.write("-" * 15 + "\n")
                
                findings = []
                
                # CPU/OS Analysis
                if not cpu_os_comparisons.empty:
                    best_cpu_os = cpu_os_comparisons.iloc[0]
                    findings.append(
                        f"• Best CPU/OS performance improvement: "
                        f"{best_cpu_os['improvement_pct']:.1f}% "
                        f"(OS {best_cpu_os['faster_os']} vs {best_cpu_os['slower_os']})"
                    )
                    
                    avg_improvement = cpu_os_comparisons['improvement_pct'].mean()
                    findings.append(
                        f"• Average OS performance improvement: {avg_improvement:.1f}%"
                    )
                
                # OCIO Version Analysis
                if not ocio_comparisons.empty:
                    best_ocio = ocio_comparisons.iloc[0]
                    findings.append(
                        f"• Best OCIO version improvement: "
                        f"{best_ocio['improvement_pct']:.1f}% "
                        f"(OCIO {best_ocio['faster_ocio_version']} vs "
                        f"{best_ocio['slower_ocio_version']})"
                    )
                
                # ACES Version Analysis
                if not summary_data.empty and 'aces_version' in summary_data.columns:
                    aces_perf = summary_data.groupby('aces_version')['mean_avg_time'].mean()
                    if len(aces_perf) > 1:
                        fastest_aces = aces_perf.idxmin()
                        slowest_aces = aces_perf.idxmax()
                        improvement = ((aces_perf[slowest_aces] - aces_perf[fastest_aces]) / 
                                     aces_perf[slowest_aces]) * 100
                        findings.append(
                            f"• ACES version performance: {fastest_aces} is "
                            f"{improvement:.1f}% faster than {slowest_aces}"
                        )
                
                if not findings:
                    findings.append("• No significant performance differences found")
                
                for finding in findings:
                    f.write(f"{finding}\n")
                
                f.write("\n")
                
                # Recommendations Section
                f.write("RECOMMENDATIONS\n")
                f.write("-" * 18 + "\n")
                
                recommendations = []
                
                if not cpu_os_comparisons.empty:
                    top_os = cpu_os_comparisons.iloc[0]['faster_os']
                    recommendations.append(
                        f"• Consider using OS release {top_os} for optimal performance"
                    )
                
                if not ocio_comparisons.empty:
                    top_ocio = ocio_comparisons.iloc[0]['faster_ocio_version']
                    recommendations.append(
                        f"• OCIO version {top_ocio} shows the best performance characteristics"
                    )
                
                if not summary_data.empty:
                    # Find best performing CPU
                    if 'cpu_model' in summary_data.columns and 'mean_avg_time' in summary_data.columns:
                        best_cpu_idx = summary_data['mean_avg_time'].idxmin()
                        best_cpu = summary_data.loc[best_cpu_idx, 'cpu_model']
                        recommendations.append(
                            f"• Top performing CPU: {self._truncate_text(best_cpu, 60)}"
                        )
                
                if not recommendations:
                    recommendations.append("• Further analysis recommended with more data")
                
                for rec in recommendations:
                    f.write(f"{rec}\n")
                
                f.write("\n")
                f.write(f"Report generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            logger.info(f"Detailed findings report saved to {output_path}")
            
        except Exception as e:
            raise AnalysisError(f"Failed to create detailed findings report: {e}")

    def _truncate_text(self, text: str, max_length: int) -> str:
        """
        Truncate text to specified length with ellipsis.

        Args:
            text: Text to truncate
            max_length: Maximum length

        Returns:
            Truncated text
        """
        if pd.isna(text) or len(str(text)) <= max_length:
            return str(text)
        return str(text)[:max_length-3] + "..."
