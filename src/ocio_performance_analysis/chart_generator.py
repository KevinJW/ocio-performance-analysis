"""
OCIO Chart Generation Module

Handles creation of various charts and visualizations
for OCIO performance analysis.
"""

from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from .exceptions import ChartGenerationError
from .logging_config import get_logger

logger = get_logger(__name__)


class OCIOChartGenerator:
    """Handles chart and visualization generation for OCIO performance data."""

    def __init__(self):
        """Initialize the chart generator with default styling."""
        # Set up matplotlib and seaborn styling
        plt.style.use('default')
        sns.set_palette("husl")
        self._setup_plot_defaults()

    def _setup_plot_defaults(self):
        """Configure default plot settings."""
        plt.rcParams.update({
            'figure.figsize': (12, 8),
            'font.size': 10,
            'axes.titlesize': 14,
            'axes.labelsize': 12,
            'xtick.labelsize': 10,
            'ytick.labelsize': 10,
            'legend.fontsize': 10,
            'figure.titlesize': 16
        })

    def create_summary_plot(self, summary_data: pd.DataFrame, output_path: Path) -> None:
        """
        Create summary analysis plot.

        Args:
            summary_data: DataFrame with summary statistics
            output_path: Path to save the plot
            
        Raises:
            ChartGenerationError: If chart creation fails
        """
        try:
            logger.info("Creating summary analysis plot")
            
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle('OCIO Performance Analysis Summary', fontsize=16, fontweight='bold')

            # 1. Performance by ACES Version
            if 'aces_version' in summary_data.columns and 'mean_avg_time' in summary_data.columns:
                aces_perf = summary_data.groupby('aces_version')['mean_avg_time'].mean()
                ax1.bar(aces_perf.index, aces_perf.values, color=['skyblue', 'lightcoral'])
                ax1.set_title('Average Performance by ACES Version')
                ax1.set_ylabel('Average Time (ms)')
                ax1.tick_params(axis='x', rotation=45)

            # 2. Performance by OS Release
            if 'os_release' in summary_data.columns:
                os_perf = summary_data.groupby('os_release')['mean_avg_time'].mean()
                ax2.bar(os_perf.index, os_perf.values, color='lightgreen')
                ax2.set_title('Average Performance by OS Release')
                ax2.set_ylabel('Average Time (ms)')

            # 3. OCIO Version Distribution
            if 'ocio_version' in summary_data.columns:
                ocio_counts = summary_data['ocio_version'].value_counts()
                ax3.pie(ocio_counts.values, labels=ocio_counts.index, autopct='%1.1f%%')
                ax3.set_title('OCIO Version Distribution')

            # 4. Performance Distribution
            if 'mean_avg_time' in summary_data.columns:
                ax4.hist(summary_data['mean_avg_time'], bins=20, alpha=0.7, color='orange')
                ax4.set_title('Performance Time Distribution')
                ax4.set_xlabel('Average Time (ms)')
                ax4.set_ylabel('Frequency')

            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Summary plot saved to {output_path}")
            
        except Exception as e:
            raise ChartGenerationError(f"Failed to create summary plot: {e}")

    def create_comparison_plot(self, comparison_data: pd.DataFrame, 
                             title: str, output_path: Path) -> None:
        """
        Create comparison plot for CPU/OS or OCIO version comparisons.

        Args:
            comparison_data: DataFrame with comparison data
            title: Title for the plot
            output_path: Path to save the plot
            
        Raises:
            ChartGenerationError: If chart creation fails
        """
        try:
            logger.info(f"Creating comparison plot: {title}")
            
            if comparison_data.empty:
                logger.warning("No comparison data available for plotting")
                return

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
            fig.suptitle(title, fontsize=16, fontweight='bold')

            # 1. Performance improvements
            if 'improvement_pct' in comparison_data.columns:
                top_improvements = comparison_data.head(10)
                bars = ax1.barh(range(len(top_improvements)), 
                               top_improvements['improvement_pct'])
                ax1.set_yticks(range(len(top_improvements)))
                
                # Create labels based on available columns
                if 'cpu_model' in comparison_data.columns:
                    labels = [self._create_short_cpu_name(cpu) 
                             for cpu in top_improvements['cpu_model']]
                else:
                    labels = [f"Item {i}" for i in range(len(top_improvements))]
                    
                ax1.set_yticklabels(labels)
                ax1.set_xlabel('Performance Improvement (%)')
                ax1.set_title('Top Performance Improvements')

                # Color bars based on improvement level
                for i, bar in enumerate(bars):
                    improvement = top_improvements.iloc[i]['improvement_pct']
                    if improvement > 10:
                        bar.set_color('green')
                    elif improvement > 5:
                        bar.set_color('orange')
                    else:
                        bar.set_color('red')

            # 2. Performance times scatter plot
            if 'faster_time' in comparison_data.columns and 'slower_time' in comparison_data.columns:
                ax2.scatter(comparison_data['faster_time'], 
                           comparison_data['slower_time'], alpha=0.6)
                
                # Add diagonal line for reference
                min_time = min(comparison_data['faster_time'].min(), 
                              comparison_data['slower_time'].min())
                max_time = max(comparison_data['faster_time'].max(), 
                              comparison_data['slower_time'].max())
                ax2.plot([min_time, max_time], [min_time, max_time], 
                        'r--', alpha=0.5, label='Equal Performance')
                
                ax2.set_xlabel('Faster Time (ms)')
                ax2.set_ylabel('Slower Time (ms)')
                ax2.set_title('Performance Comparison Scatter')
                ax2.legend()

            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Comparison plot saved to {output_path}")
            
        except Exception as e:
            raise ChartGenerationError(f"Failed to create comparison plot: {e}")

    def create_aces_comparison_plot(self, data: pd.DataFrame, 
                                   output_path: Path) -> None:
        """
        Create comprehensive ACES version comparison plot.

        Args:
            data: DataFrame with ACES comparison data
            output_path: Path to save the plot
            
        Raises:
            ChartGenerationError: If chart creation fails
        """
        try:
            logger.info("Creating ACES comparison plot")
            
            if data.empty:
                logger.warning("No ACES comparison data available")
                return

            fig, axes = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle('Comprehensive ACES Version Performance Comparison', 
                        fontsize=16, fontweight='bold')

            # Group data by ACES version
            aces_1_data = data[data['aces_version'] == 'ACES 1.0']
            aces_2_data = data[data['aces_version'] == 'ACES 2.0']

            # 1. Box plot comparison
            if not aces_1_data.empty and not aces_2_data.empty:
                box_data = [aces_1_data['mean_avg_time'], aces_2_data['mean_avg_time']]
                axes[0, 0].boxplot(box_data, labels=['ACES 1.0', 'ACES 2.0'])
                axes[0, 0].set_title('Performance Distribution by ACES Version')
                axes[0, 0].set_ylabel('Average Time (ms)')

            # 2. OCIO version comparison within ACES versions
            if 'ocio_version' in data.columns:
                aces_ocio = data.groupby(['aces_version', 'ocio_version'])['mean_avg_time'].mean().unstack()
                aces_ocio.plot(kind='bar', ax=axes[0, 1])
                axes[0, 1].set_title('Performance by ACES and OCIO Version')
                axes[0, 1].set_ylabel('Average Time (ms)')
                axes[0, 1].tick_params(axis='x', rotation=45)
                axes[0, 1].legend(title='OCIO Version')

            # 3. Performance improvement histogram
            if len(data) > 1:
                aces_1_mean = aces_1_data['mean_avg_time'].mean() if not aces_1_data.empty else 0
                aces_2_mean = aces_2_data['mean_avg_time'].mean() if not aces_2_data.empty else 0
                
                if aces_1_mean > 0 and aces_2_mean > 0:
                    improvement = ((aces_1_mean - aces_2_mean) / aces_1_mean) * 100
                    axes[1, 0].bar(['ACES 1.0 vs 2.0'], [improvement], 
                                  color='green' if improvement > 0 else 'red')
                    axes[1, 0].set_title('Overall ACES Performance Improvement')
                    axes[1, 0].set_ylabel('Improvement (%)')

            # 4. System count comparison
            if 'cpu_model' in data.columns:
                aces_systems = data.groupby('aces_version')['cpu_model'].nunique()
                axes[1, 1].bar(aces_systems.index, aces_systems.values, 
                              color=['skyblue', 'lightcoral'])
                axes[1, 1].set_title('Number of Systems Tested by ACES Version')
                axes[1, 1].set_ylabel('Number of Systems')

            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"ACES comparison plot saved to {output_path}")
            
        except Exception as e:
            raise ChartGenerationError(f"Failed to create ACES comparison plot: {e}")

    def _create_short_cpu_name(self, cpu_model: str) -> str:
        """
        Create a shortened CPU name for display purposes.

        Args:
            cpu_model: Full CPU model name

        Returns:
            Shortened CPU name
        """
        if pd.isna(cpu_model) or cpu_model == "Unknown":
            return "Unknown"

        # Remove common prefixes and suffixes
        cpu_short = cpu_model.replace("Intel(R) ", "").replace("(R)", "")
        cpu_short = cpu_short.replace("Core(TM) ", "").replace("(TM)", "")
        cpu_short = cpu_short.replace("Xeon(R) ", "Xeon ")
        cpu_short = cpu_short.replace("CPU ", "")
        
        # Remove @ frequency part
        cpu_short = cpu_short.split(" @")[0]
        cpu_short = cpu_short.replace(" @", "")
        
        # Limit length
        if len(cpu_short) > 20:
            cpu_short = cpu_short[:17] + "..."
            
        return cpu_short.strip()

    def create_performance_heatmap(self, data: pd.DataFrame, 
                                  output_path: Path) -> None:
        """
        Create performance heatmap showing relationships between variables.

        Args:
            data: DataFrame with performance data
            output_path: Path to save the plot
            
        Raises:
            ChartGenerationError: If chart creation fails
        """
        try:
            logger.info("Creating performance heatmap")
            
            if data.empty:
                logger.warning("No data available for heatmap")
                return

            # Create pivot table for heatmap
            numeric_cols = data.select_dtypes(include=['float64', 'int64']).columns
            if len(numeric_cols) < 2:
                logger.warning("Insufficient numeric data for heatmap")
                return

            # Calculate correlation matrix
            corr_matrix = data[numeric_cols].corr()

            plt.figure(figsize=(10, 8))
            sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0,
                       square=True, fmt='.2f')
            plt.title('Performance Metrics Correlation Heatmap')
            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Performance heatmap saved to {output_path}")
            
        except Exception as e:
            raise ChartGenerationError(f"Failed to create performance heatmap: {e}")
