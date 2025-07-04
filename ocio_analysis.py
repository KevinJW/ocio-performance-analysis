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
        Summarize test runs by filename and OCIO version using mean averages for numerical columns.
        
        Returns:
            DataFrame with summarized data grouped by filename and OCIO version
        """
        if self.df is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        
        # Group by filename AND OCIO version to capture all combinations
        summary_data = []
        
        for (file_name, ocio_version), group in self.df.groupby(['file_name', 'ocio_version']):
            # Get the common metadata (should be same for all rows from same file+version)
            metadata = group[['os_release', 'cpu_model', 'config_version']].iloc[0]
            
            # Calculate statistics
            stats = {
                'file_name': file_name,
                'os_release': metadata['os_release'],
                'cpu_model': metadata['cpu_model'],
                'ocio_version': ocio_version,  # Use the version from groupby
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
    
    def find_ocio_version_comparisons(self) -> pd.DataFrame:
        """
        Find cases where the same CPU and OS combination has multiple OCIO versions.
        
        Returns:
            DataFrame with OCIO version comparison data
        """
        if self.summary_df is None:
            raise ValueError("Summary data not available. Call summarize_by_filename() first.")
        
        # Group by CPU model and OS release to find multiple OCIO versions
        ocio_comparison_data = []
        
        for (cpu_model, os_release), group in self.summary_df.groupby(['cpu_model', 'os_release']):
            if cpu_model == 'Unknown':
                continue
                
            ocio_versions = group['ocio_version'].unique()
            if len(ocio_versions) > 1:
                logger.info(f"Found CPU '{cpu_model}' on OS '{os_release}' with OCIO versions: {ocio_versions}")
                
                # Create comparison records for each OCIO version
                for ocio_version in ocio_versions:
                    version_data = group[group['ocio_version'] == ocio_version]
                    
                    ocio_comparison_data.extend([{
                        'cpu_model': cpu_model,
                        'os_release': os_release,
                        'ocio_version': ocio_version,
                        'file_count': len(version_data),
                        'mean_avg_time': version_data['mean_avg_time'].mean(),
                        'std_avg_time': version_data['mean_avg_time'].std(),
                        'median_avg_time': version_data['median_avg_time'].mean(),
                        'total_operations': version_data['total_operations'].sum(),
                        'files': list(version_data['file_name']),
                    }])
        
        self.ocio_comparison_data = pd.DataFrame(ocio_comparison_data)
        logger.info(f"Found {len(self.ocio_comparison_data)} CPU-OS-OCIO combinations for comparison")
        return self.ocio_comparison_data
    
    def find_all_ocio_version_comparisons(self) -> pd.DataFrame:
        """
        Find all cases where different OCIO versions can be compared.
        
        Returns:
            DataFrame with all OCIO version comparison data
        """
        if self.summary_df is None:
            raise ValueError("Summary data not available. Call summarize_by_filename() first.")
        
        # Group by OCIO version and calculate overall statistics
        all_ocio_comparison_data = []
        
        for ocio_version, group in self.summary_df.groupby('ocio_version'):
            all_ocio_comparison_data.append({
                'ocio_version': ocio_version,
                'file_count': len(group),
                'mean_avg_time': group['mean_avg_time'].mean(),
                'std_avg_time': group['mean_avg_time'].std(),
                'median_avg_time': group['median_avg_time'].mean(),
                'total_operations': group['total_operations'].sum(),
                'cpu_models': list(group['cpu_model'].unique()),
                'os_releases': list(group['os_release'].unique()),
            })
        
        self.all_ocio_comparison_data = pd.DataFrame(all_ocio_comparison_data)
        logger.info(f"Found {len(self.all_ocio_comparison_data)} OCIO versions for overall comparison")
        return self.all_ocio_comparison_data
    
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
    
    def create_ocio_version_plots(self, output_dir: Path) -> None:
        """
        Create OCIO version comparison plots.
        
        Args:
            output_dir: Directory to save plots
        """
        output_dir.mkdir(exist_ok=True)
        
        if not hasattr(self, 'all_ocio_comparison_data') or self.all_ocio_comparison_data is None:
            logger.warning("No OCIO version comparison data available")
            return
        
        # Create OCIO version comparison plot
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('OCIO Version Performance Comparison', fontsize=14, fontweight='bold')
        
        # Plot 1: Overall performance by OCIO version
        ax1 = axes[0, 0]
        ocio_data = self.all_ocio_comparison_data.sort_values('ocio_version')
        bars1 = ax1.bar(ocio_data['ocio_version'], ocio_data['mean_avg_time'], 
                       yerr=ocio_data['std_avg_time'], capsize=5, alpha=0.7)
        ax1.set_title('Mean Performance by OCIO Version')
        ax1.set_xlabel('OCIO Version')
        ax1.set_ylabel('Mean Average Time (ms)')
        ax1.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bar, value in zip(bars1, ocio_data['mean_avg_time']):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{value:.1f}', ha='center', va='bottom')
        
        # Plot 2: File count by OCIO version
        ax2 = axes[0, 1]
        ax2.bar(ocio_data['ocio_version'], ocio_data['file_count'], alpha=0.7, color='orange')
        ax2.set_title('Number of Test Files by OCIO Version')
        ax2.set_xlabel('OCIO Version')
        ax2.set_ylabel('File Count')
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Total operations by OCIO version
        ax3 = axes[1, 0]
        ax3.bar(ocio_data['ocio_version'], ocio_data['total_operations'], alpha=0.7, color='green')
        ax3.set_title('Total Operations by OCIO Version')
        ax3.set_xlabel('OCIO Version')
        ax3.set_ylabel('Total Operations')
        ax3.grid(True, alpha=0.3)
        
        # Plot 4: Performance improvement between versions
        ax4 = axes[1, 1]
        if len(ocio_data) >= 2:
            versions = ocio_data['ocio_version'].tolist()
            times = ocio_data['mean_avg_time'].tolist()
            
            # Calculate relative performance (normalize to first version)
            if times[0] != 0:
                relative_perf = [(time / times[0]) * 100 for time in times]
                colors = ['blue' if perf <= 100 else 'red' for perf in relative_perf]
                
                bars4 = ax4.bar(versions, relative_perf, color=colors, alpha=0.7)
                ax4.set_title('Relative Performance (% of First Version)')
                ax4.set_xlabel('OCIO Version')
                ax4.set_ylabel('Relative Performance (%)')
                ax4.grid(True, alpha=0.3)
                ax4.axhline(y=100, color='black', linestyle='--', alpha=0.5, label='Baseline')
                ax4.legend()
                
                # Add value labels
                for bar, value in zip(bars4, relative_perf):
                    ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                            f'{value:.1f}%', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(output_dir / 'ocio_version_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info("OCIO version comparison plot saved")
    
    def create_detailed_cpu_os_ocio_comparison(self, output_dir: Path) -> None:
        """
        Create detailed CPU+OS comparison chart for OCIO versions 2.4.1 and 2.4.2.
        
        Args:
            output_dir: Directory to save plots
        """
        output_dir.mkdir(exist_ok=True)
        
        if self.summary_df is None:
            raise ValueError("Summary data not available. Call summarize_by_filename() first.")
        
        # Filter data for OCIO versions 2.4.1 and 2.4.2
        ocio_versions = ['2.4.1', '2.4.2']
        filtered_data = self.summary_df[self.summary_df['ocio_version'].isin(ocio_versions)]
        
        if len(filtered_data) == 0:
            logger.warning("No data found for OCIO versions 2.4.1 and 2.4.2")
            return
        
        # Create short labels for CPU + OS combinations
        filtered_data = filtered_data.copy()
        filtered_data['short_label'] = filtered_data.apply(
            lambda row: self._create_short_cpu_os_label(row['cpu_model'], row['os_release']), 
            axis=1
        )
        
        # Group by CPU+OS combination and check for both OCIO versions
        comparison_data = []
        for (cpu_model, os_release), group in filtered_data.groupby(['cpu_model', 'os_release']):
            versions_present = group['ocio_version'].unique()
            if len(versions_present) >= 1:  # At least one version present
                group_data = {
                    'cpu_model': cpu_model,
                    'os_release': os_release,
                    'short_label': group['short_label'].iloc[0]
                }
                
                # Add performance data for each version
                for version in ocio_versions:
                    version_data = group[group['ocio_version'] == version]
                    if len(version_data) > 0:
                        group_data[f'ocio_{version}'] = version_data['mean_avg_time'].mean()
                    else:
                        group_data[f'ocio_{version}'] = None
                
                comparison_data.append(group_data)
        
        if not comparison_data:
            logger.warning("No CPU+OS combinations found with OCIO version data")
            return
        
        # Create the comparison chart
        fig, ax = plt.subplots(figsize=(16, 10))
        
        # Prepare data for plotting
        labels = []
        ocio_241_values = []
        ocio_242_values = []
        
        for item in comparison_data:
            labels.append(item['short_label'])
            # Handle None values by converting to 0
            val_241 = item.get('ocio_2.4.1', None)
            val_242 = item.get('ocio_2.4.2', None)
            ocio_241_values.append(val_241 if val_241 is not None else 0)
            ocio_242_values.append(val_242 if val_242 is not None else 0)
        
        # Create bar positions
        x_pos = range(len(labels))
        bar_width = 0.35
        
        # Create bars
        bars1 = ax.bar([x - bar_width/2 for x in x_pos], ocio_241_values, 
                      bar_width, label='OCIO 2.4.1', alpha=0.8, color='#2E86AB')
        bars2 = ax.bar([x + bar_width/2 for x in x_pos], ocio_242_values, 
                      bar_width, label='OCIO 2.4.2', alpha=0.8, color='#A23B72')
        
        # Customize the plot
        ax.set_title('OCIO Version Performance Comparison by CPU and OS\n(2.4.1 vs 2.4.2)', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('CPU Model + OS Release', fontsize=12)
        ax.set_ylabel('Mean Average Time (ms)', fontsize=12)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(labels, rotation=45, ha='right')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar, value in zip(bars1, ocio_241_values):
            if value > 0:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(ocio_241_values)*0.01,
                       f'{value:.0f}', ha='center', va='bottom', fontsize=9)
        
        for bar, value in zip(bars2, ocio_242_values):
            if value > 0:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(ocio_242_values)*0.01,
                       f'{value:.0f}', ha='center', va='bottom', fontsize=9)
        
        # Add performance difference annotations
        for i, (val1, val2) in enumerate(zip(ocio_241_values, ocio_242_values)):
            if val1 > 0 and val2 > 0:
                diff_pct = ((val2 - val1) / val1) * 100
                color = 'green' if diff_pct < 0 else 'red'
                ax.annotate(f'{diff_pct:+.1f}%', 
                          xy=(i, max(val1, val2) + max(max(ocio_241_values), max(ocio_242_values))*0.05),
                          ha='center', va='bottom', fontsize=8, color=color, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(output_dir / 'ocio_241_vs_242_cpu_os_comparison.png', 
                   dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info("Detailed CPU+OS OCIO version comparison plot saved")
    
    def _create_short_cpu_os_label(self, cpu_model: str, os_release: str) -> str:
        """
        Create a short label for CPU model and OS release.
        
        Args:
            cpu_model: Full CPU model name
            os_release: OS release (r7, r9, etc.)
            
        Returns:
            Short label for display
        """
        if cpu_model == 'Unknown':
            return f'Unknown-{os_release}'
        
        # Extract key CPU information
        cpu_short = cpu_model
        
        # Remove common prefixes/suffixes
        cpu_short = cpu_short.replace('Intel(R) ', '')
        cpu_short = cpu_short.replace('(R) ', '')
        cpu_short = cpu_short.replace(' CPU', '')
        
        # Simplify specific model names
        if 'Core(TM) i9-9900K' in cpu_short:
            cpu_short = 'i9-9900K'
        elif 'Core(TM) i9-9900' in cpu_short:
            cpu_short = 'i9-9900'
        elif 'Xeon(R) CPU E5-2687W v3' in cpu_short:
            cpu_short = 'E5-2687W-v3'
        elif 'Xeon(R) CPU E5-2667 v4' in cpu_short:
            cpu_short = 'E5-2667-v4'
        elif 'Xeon(R) W-2295' in cpu_short:
            cpu_short = 'W-2295'
        elif 'Xeon(R) w5-2465X' in cpu_short:
            cpu_short = 'w5-2465X'
        elif 'Xeon(R) w7-2495X' in cpu_short:
            cpu_short = 'w7-2495X'
        else:
            # General simplification for other models
            parts = cpu_short.split()
            if len(parts) > 2:
                cpu_short = f"{parts[0]}-{parts[1]}"
            elif len(parts) > 1:
                cpu_short = f"{parts[0]}-{parts[1]}"
            else:
                cpu_short = parts[0] if parts else 'Unknown'
        
        return f"{cpu_short}-{os_release}"

    def create_detailed_ocio_comparison_report(self, output_dir: Path) -> None:
        """
        Create a detailed OCIO version comparison report.
        
        Args:
            output_dir: Directory to save the report
        """
        output_dir.mkdir(exist_ok=True)
        
        if not hasattr(self, 'all_ocio_comparison_data') or self.all_ocio_comparison_data is None:
            logger.warning("No OCIO version comparison data available")
            return
        
        report_file = output_dir / 'ocio_version_comparison_report.txt'
        
        with open(report_file, 'w') as f:
            f.write("OCIO Test Results - OCIO Version Performance Comparison Report\n")
            f.write("=" * 70 + "\n\n")
            
            # Summary statistics
            f.write("SUMMARY STATISTICS\n")
            f.write("-" * 20 + "\n")
            f.write(f"Total OCIO versions found: {len(self.all_ocio_comparison_data)}\n")
            f.write(f"OCIO versions: {list(self.all_ocio_comparison_data['ocio_version'].unique())}\n")
            
            # Get overall performance comparison
            sorted_data = self.all_ocio_comparison_data.sort_values('mean_avg_time')
            fastest_version = sorted_data.iloc[0]
            slowest_version = sorted_data.iloc[-1]
            
            if fastest_version['mean_avg_time'] != 0:
                perf_diff = ((slowest_version['mean_avg_time'] - fastest_version['mean_avg_time']) / 
                           fastest_version['mean_avg_time']) * 100
                f.write(f"Fastest OCIO version: {fastest_version['ocio_version']} ({fastest_version['mean_avg_time']:.1f} ms)\n")
                f.write(f"Slowest OCIO version: {slowest_version['ocio_version']} ({slowest_version['mean_avg_time']:.1f} ms)\n")
                f.write(f"Performance difference: {perf_diff:.1f}%\n\n")
            
            # Detailed version comparisons
            f.write("DETAILED OCIO VERSION ANALYSIS\n")
            f.write("-" * 35 + "\n")
            
            for _, row in self.all_ocio_comparison_data.sort_values('ocio_version').iterrows():
                f.write(f"\nOCIO Version: {row['ocio_version']}\n")
                f.write("=" * (len(row['ocio_version']) + 15) + "\n")
                f.write(f"  Files tested: {row['file_count']}\n")
                f.write(f"  Mean avg time: {row['mean_avg_time']:.3f} ms\n")
                f.write(f"  Std deviation: {row['std_avg_time']:.3f} ms\n")
                f.write(f"  Median time: {row['median_avg_time']:.3f} ms\n")
                f.write(f"  Total operations: {row['total_operations']}\n")
                f.write(f"  CPU models tested: {len(row['cpu_models'])}\n")
                f.write(f"  OS releases tested: {row['os_releases']}\n")
                f.write(f"  CPU models: {', '.join([cpu for cpu in row['cpu_models'] if cpu != 'Unknown'])}\n")
                
                # Calculate relative performance vs fastest
                if fastest_version['mean_avg_time'] != 0:
                    rel_perf = (row['mean_avg_time'] / fastest_version['mean_avg_time']) * 100
                    f.write(f"  Relative performance: {rel_perf:.1f}% of fastest version\n")
                
                f.write("\n" + "-" * 50 + "\n")
        
        logger.info(f"Detailed OCIO version comparison report saved to {report_file}")
    
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
        self.find_ocio_version_comparisons()
        self.find_all_ocio_version_comparisons()
        
        # Create visualizations
        self.create_summary_plots(output_dir)
        self.create_os_comparison_plots(output_dir)
        self.create_detailed_comparison_report(output_dir)
        self.create_ocio_version_plots(output_dir)
        self.create_detailed_cpu_os_ocio_comparison(output_dir)
        self.create_detailed_ocio_comparison_report(output_dir)
        
        # Save summary data
        self.summary_df.to_csv(output_dir / 'file_summaries.csv', index=False)
        self.comparison_data.to_csv(output_dir / 'os_comparisons.csv', index=False)
        
        # Save OCIO version comparison data if available
        if hasattr(self, 'all_ocio_comparison_data') and self.all_ocio_comparison_data is not None:
            self.all_ocio_comparison_data.to_csv(output_dir / 'ocio_version_comparisons.csv', index=False)
        if hasattr(self, 'ocio_comparison_data') and self.ocio_comparison_data is not None:
            self.ocio_comparison_data.to_csv(output_dir / 'detailed_ocio_comparisons.csv', index=False)
        
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
