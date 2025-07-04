"""
OCIO Test Results Analysis Script

This script analyzes OCIO test results CSV data to:
1. Summarize test runs by filename using mean averages
2. Find cases where CPU is same but OS release differs
3. Create visualizations comparing OS performance effects
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up matplotlib for better plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")


class OCIOAnalyzer:
    """Analyzer for OCIO test results data."""
    
    def __init__(self, csv_file: Path):
        """
        Initialize the analyzer with CSV data.
        
        Args:
            csv_file: Path to the CSV file containing test results
        """
        self.csv_file = csv_file
        self.df = None
        self.summary_df = None
        self.comparison_data = None
        
    def load_data(self) -> pd.DataFrame:
        """Load CSV data into DataFrame."""
        try:
            self.df = pd.read_csv(self.csv_file)
            logger.info(f"Loaded {len(self.df)} records from {self.csv_file}")
            return self.df
        except Exception as e:
            logger.error(f"Error loading CSV file: {e}")
            raise
    
    def summarize_by_filename(self) -> pd.DataFrame:
        """
        Summarize test runs by filename using mean averages for numerical columns.
        
        Returns:
            DataFrame with summarized data grouped by filename
        """
        if self.df is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        
        # Group by filename and calculate means for numerical columns
        summary_data = []
        
        for file_name, group in self.df.groupby('file_name'):
            # Get the common metadata (should be same for all rows from same file)
            metadata = group[['os_release', 'cpu_model', 'ocio_version', 'config_version']].iloc[0]
            
            # Calculate statistics
            stats = {
                'file_name': file_name,
                'os_release': metadata['os_release'],
                'cpu_model': metadata['cpu_model'],
                'ocio_version': metadata['ocio_version'],
                'config_version': metadata['config_version'],
                'total_operations': len(group),
                'unique_operations': group['operation'].nunique(),
                'mean_min_time': group['min_time'].mean(),
                'mean_max_time': group['max_time'].mean(),
                'mean_avg_time': group['avg_time'].mean(),
                'std_avg_time': group['avg_time'].std(),
                'median_avg_time': group['avg_time'].median(),
                'total_iterations': group['iteration_count'].sum(),
                'mean_iterations': group['iteration_count'].mean(),
            }
            
            # Add operation-specific breakdown
            operation_stats = group.groupby('operation')['avg_time'].agg(['mean', 'std', 'count'])
            for op, data in operation_stats.iterrows():
                stats[f'{op}_mean_time'] = data['mean']
                stats[f'{op}_std_time'] = data['std'] if not pd.isna(data['std']) else 0
                stats[f'{op}_count'] = data['count']
            
            summary_data.append(stats)
        
        self.summary_df = pd.DataFrame(summary_data)
        logger.info(f"Created summary with {len(self.summary_df)} file summaries")
        return self.summary_df
    
    def find_cpu_os_comparisons(self) -> pd.DataFrame:
        """
        Find cases where CPU is the same but OS release differs.
        
        Returns:
            DataFrame with comparison data
        """
        if self.summary_df is None:
            raise ValueError("Summary data not available. Call summarize_by_filename() first.")
        
        # Group by CPU model and find cases with multiple OS releases
        comparison_data = []
        
        for cpu_model, group in self.summary_df.groupby('cpu_model'):
            if cpu_model == 'Unknown':
                continue
                
            os_releases = group['os_release'].unique()
            if len(os_releases) > 1:
                logger.info(f"Found CPU '{cpu_model}' with OS releases: {os_releases}")
                
                # Create comparison records
                for os_release in os_releases:
                    os_data = group[group['os_release'] == os_release]
                    
                    comparison_data.extend([{
                        'cpu_model': cpu_model,
                        'os_release': os_release,
                        'file_count': len(os_data),
                        'mean_avg_time': os_data['mean_avg_time'].mean(),
                        'std_avg_time': os_data['mean_avg_time'].std(),
                        'median_avg_time': os_data['median_avg_time'].mean(),
                        'total_operations': os_data['total_operations'].sum(),
                        'files': list(os_data['file_name']),
                    }])
        
        self.comparison_data = pd.DataFrame(comparison_data)
        logger.info(f"Found {len(self.comparison_data)} CPU-OS combinations for comparison")
        return self.comparison_data
    
    def create_summary_plots(self, output_dir: Path) -> None:
        """
        Create summary visualization plots.
        
        Args:
            output_dir: Directory to save plots
        """
        output_dir.mkdir(exist_ok=True)
        
        if self.summary_df is None:
            raise ValueError("Summary data not available. Call summarize_by_filename() first.")
        
        # Plot 1: Average execution time by OS release
        plt.figure(figsize=(12, 8))
        
        plt.subplot(2, 2, 1)
        os_perf = self.summary_df.groupby('os_release')['mean_avg_time'].agg(['mean', 'std', 'count'])
        os_perf.plot(kind='bar', y='mean', yerr='std', ax=plt.gca())
        plt.title('Average Execution Time by OS Release')
        plt.xlabel('OS Release')
        plt.ylabel('Mean Average Time (ms)')
        plt.xticks(rotation=45)
        
        # Plot 2: CPU model performance distribution
        plt.subplot(2, 2, 2)
        cpu_data = self.summary_df[self.summary_df['cpu_model'] != 'Unknown']
        if len(cpu_data) > 0:
            cpu_perf = cpu_data.groupby('cpu_model')['mean_avg_time'].mean().sort_values()
            cpu_perf.plot(kind='barh')
            plt.title('Average Performance by CPU Model')
            plt.xlabel('Mean Average Time (ms)')
            plt.ylabel('CPU Model')
        
        # Plot 3: Performance distribution histogram
        plt.subplot(2, 2, 3)
        plt.hist(self.summary_df['mean_avg_time'], bins=20, alpha=0.7, edgecolor='black')
        plt.title('Distribution of Average Execution Times')
        plt.xlabel('Mean Average Time (ms)')
        plt.ylabel('Frequency')
        
        # Plot 4: OS vs CPU heatmap
        plt.subplot(2, 2, 4)
        if len(self.summary_df[self.summary_df['cpu_model'] != 'Unknown']) > 0:
            pivot_data = self.summary_df[self.summary_df['cpu_model'] != 'Unknown'].pivot_table(
                values='mean_avg_time', 
                index='cpu_model', 
                columns='os_release', 
                aggfunc='mean'
            )
            sns.heatmap(pivot_data, annot=True, fmt='.2f', cmap='viridis')
            plt.title('Performance Heatmap: CPU vs OS')
            plt.xlabel('OS Release')
            plt.ylabel('CPU Model')
        
        plt.tight_layout()
        plt.savefig(output_dir / 'summary_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Summary plots saved to {output_dir / 'summary_analysis.png'}")
    
    def create_os_comparison_plots(self, output_dir: Path) -> None:
        """
        Create OS comparison plots for same CPU models.
        
        Args:
            output_dir: Directory to save plots
        """
        output_dir.mkdir(exist_ok=True)
        
        if self.comparison_data is None:
            raise ValueError("Comparison data not available. Call find_cpu_os_comparisons() first.")
        
        # Get unique CPU models that have multiple OS releases
        cpu_models = self.comparison_data['cpu_model'].unique()
        
        for cpu_model in cpu_models:
            cpu_data = self.comparison_data[self.comparison_data['cpu_model'] == cpu_model]
            
            if len(cpu_data) < 2:
                continue
            
            # Create comparison plot for this CPU
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle(f'OS Performance Comparison\n{cpu_model}', fontsize=14, fontweight='bold')
            
            # Plot 1: Bar chart of mean performance
            ax1 = axes[0, 0]
            bars = ax1.bar(cpu_data['os_release'], cpu_data['mean_avg_time'], 
                          yerr=cpu_data['std_avg_time'], capsize=5, alpha=0.7)
            ax1.set_title('Mean Average Execution Time')
            ax1.set_xlabel('OS Release')
            ax1.set_ylabel('Mean Average Time (ms)')
            ax1.grid(True, alpha=0.3)
            
            # Add value labels on bars
            for bar, value in zip(bars, cpu_data['mean_avg_time']):
                ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                        f'{value:.2f}', ha='center', va='bottom')
            
            # Plot 2: File count comparison
            ax2 = axes[0, 1]
            ax2.bar(cpu_data['os_release'], cpu_data['file_count'], alpha=0.7)
            ax2.set_title('Number of Test Files')
            ax2.set_xlabel('OS Release')
            ax2.set_ylabel('File Count')
            ax2.grid(True, alpha=0.3)
            
            # Plot 3: Total operations comparison
            ax3 = axes[1, 0]
            ax3.bar(cpu_data['os_release'], cpu_data['total_operations'], alpha=0.7)
            ax3.set_title('Total Operations Tested')
            ax3.set_xlabel('OS Release')
            ax3.set_ylabel('Total Operations')
            ax3.grid(True, alpha=0.3)
            
            # Plot 4: Performance improvement/regression
            ax4 = axes[1, 1]
            if len(cpu_data) == 2:
                os_releases = cpu_data['os_release'].tolist()
                times = cpu_data['mean_avg_time'].tolist()
                
                # Calculate percentage difference
                if times[0] != 0:
                    pct_change = ((times[1] - times[0]) / times[0]) * 100
                    color = 'green' if pct_change < 0 else 'red'
                    
                    ax4.bar(['Performance Change'], [pct_change], color=color, alpha=0.7)
                    ax4.set_title(f'Performance Change: {os_releases[0]} → {os_releases[1]}')
                    ax4.set_ylabel('Percentage Change (%)')
                    ax4.grid(True, alpha=0.3)
                    ax4.axhline(y=0, color='black', linestyle='-', alpha=0.5)
                    
                    # Add value label
                    ax4.text(0, pct_change + (1 if pct_change > 0 else -1),
                            f'{pct_change:.1f}%', ha='center', va='bottom' if pct_change > 0 else 'top')
            
            plt.tight_layout()
            
            # Save plot with sanitized CPU model name
            safe_cpu_name = cpu_model.replace('(', '').replace(')', '').replace(' ', '_').replace('@', 'at')
            plt.savefig(output_dir / f'os_comparison_{safe_cpu_name}.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"OS comparison plot saved for {cpu_model}")
    
    def create_detailed_comparison_report(self, output_dir: Path) -> None:
        """
        Create a detailed comparison report.
        
        Args:
            output_dir: Directory to save the report
        """
        output_dir.mkdir(exist_ok=True)
        
        if self.comparison_data is None:
            raise ValueError("Comparison data not available. Call find_cpu_os_comparisons() first.")
        
        report_file = output_dir / 'os_comparison_report.txt'
        
        with open(report_file, 'w') as f:
            f.write("OCIO Test Results - OS Performance Comparison Report\n")
            f.write("=" * 60 + "\n\n")
            
            # Summary statistics
            f.write("SUMMARY STATISTICS\n")
            f.write("-" * 20 + "\n")
            f.write(f"Total files analyzed: {len(self.summary_df)}\n")
            f.write(f"Unique CPU models: {self.summary_df['cpu_model'].nunique()}\n")
            f.write(f"OS releases found: {list(self.summary_df['os_release'].unique())}\n")
            f.write(f"CPU models with multiple OS releases: {len(self.comparison_data['cpu_model'].unique())}\n\n")
            
            # Detailed comparisons
            f.write("DETAILED OS COMPARISONS\n")
            f.write("-" * 25 + "\n")
            
            for cpu_model in self.comparison_data['cpu_model'].unique():
                cpu_data = self.comparison_data[self.comparison_data['cpu_model'] == cpu_model]
                
                f.write(f"\nCPU Model: {cpu_model}\n")
                f.write("=" * (len(cpu_model) + 12) + "\n")
                
                for _, row in cpu_data.iterrows():
                    f.write(f"  OS Release: {row['os_release']}\n")
                    f.write(f"    Files: {row['file_count']}\n")
                    f.write(f"    Mean avg time: {row['mean_avg_time']:.3f} ms\n")
                    f.write(f"    Std dev: {row['std_avg_time']:.3f} ms\n")
                    f.write(f"    Total operations: {row['total_operations']}\n")
                    f.write(f"    Test files: {', '.join(row['files'])}\n\n")
                
                # Performance comparison if exactly 2 OS releases
                if len(cpu_data) == 2:
                    os1, os2 = cpu_data['os_release'].tolist()
                    time1, time2 = cpu_data['mean_avg_time'].tolist()
                    
                    if time1 != 0:
                        pct_change = ((time2 - time1) / time1) * 100
                        better_os = os1 if time1 < time2 else os2
                        f.write("  Performance Analysis:\n")
                        f.write(f"    {os1}: {time1:.3f} ms\n")
                        f.write(f"    {os2}: {time2:.3f} ms\n")
                        f.write(f"    Change: {pct_change:.1f}%\n")
                        f.write(f"    Better performing OS: {better_os}\n")
                
                f.write("\n" + "-" * 40 + "\n")
        
        logger.info(f"Detailed comparison report saved to {report_file}")
    
    def run_full_analysis(self, output_dir: Path) -> None:
        """
        Run the complete analysis pipeline.
        
        Args:
            output_dir: Directory to save all outputs
        """
        output_dir.mkdir(exist_ok=True)
        
        logger.info("Starting full OCIO analysis...")
        
        # Load and process data
        self.load_data()
        self.summarize_by_filename()
        self.find_cpu_os_comparisons()
        
        # Create visualizations
        self.create_summary_plots(output_dir)
        self.create_os_comparison_plots(output_dir)
        self.create_detailed_comparison_report(output_dir)
        
        # Save summary data
        self.summary_df.to_csv(output_dir / 'file_summaries.csv', index=False)
        self.comparison_data.to_csv(output_dir / 'os_comparisons.csv', index=False)
        
        logger.info(f"Analysis complete! Results saved to {output_dir}")


def main():
    """Main function to run the analysis."""
    # Set up paths
    script_dir = Path(__file__).parent
    csv_file = script_dir / "ocio_test_results.csv"
    output_dir = script_dir / "analysis_results"
    
    # Create analyzer and run analysis
    analyzer = OCIOAnalyzer(csv_file)
    
    if not csv_file.exists():
        logger.error(f"CSV file not found: {csv_file}")
        return
    
    try:
        analyzer.run_full_analysis(output_dir)
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise


if __name__ == "__main__":
    main()
