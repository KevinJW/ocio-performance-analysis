#!/usr/bin/env python3
"""
Example: CPU Performance Analysis with Bar Charts

This example demonstrates how to analyze and compare CPU performance
across different models using bar charts for clear visualization.
Shows performance rankings, ACES version impacts, and statistical insights.
"""

from src.ocio_performance_analysis import OCIODataAnalyzer
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


def create_cpu_performance_analysis():
    """
    Create comprehensive CPU performance analysis with bar charts.
    
    This example demonstrates:
    1. CPU performance ranking by mean performance
    2. CPU performance by ACES version comparison  
    3. Performance distribution analysis
    4. Statistical significance testing
    """
    
    print("🖥️  CPU Performance Analysis Example")
    print("=" * 50)
    
    # Initialize the analyzer
    analyzer = OCIODataAnalyzer()
    analyzer.set_csv_file(Path('data/ocio_test_results.csv'))
    analyzer.load_data()
    
    print(f"📊 Analyzing {len(analyzer.data)} test results")
    print(f"🖥️  Found {analyzer.data['cpu_model'].nunique()} unique CPU models")
    
    # Create output directory
    output_dir = Path('examples/outputs')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Overall CPU Performance Ranking
    create_cpu_ranking_chart(analyzer.data, output_dir)
    
    # 2. CPU Performance by ACES Version
    create_cpu_aces_comparison(analyzer.data, output_dir)
    
    # 3. Performance Variability Analysis
    create_performance_variability_chart(analyzer.data, output_dir)
    
    # 4. Top CPU Models Detailed Comparison
    create_top_cpus_comparison(analyzer.data, output_dir)
    
    print("\n✅ All CPU performance analysis charts created successfully!")
    print(f"📁 Charts saved to: {output_dir}")


def create_cpu_ranking_chart(data, output_dir):
    """Create CPU performance ranking bar chart."""
    
    print("\n📊 Creating CPU performance ranking chart...")
    
    # Calculate performance statistics by CPU
    cpu_stats = data.groupby('cpu_model')['avg_time'].agg([
        'count', 'mean', 'median', 'std'
    ]).round(2)
    
    # Filter CPUs with sufficient data (at least 10 test results)
    cpu_stats = cpu_stats[cpu_stats['count'] >= 10]
    cpu_stats = cpu_stats.sort_values('mean')
    
    # Create shorter CPU names for display
    cpu_stats.index = [
        cpu.replace('Intel(R) ', '').replace('(R)', '').replace(' CPU', '')[:30] 
        for cpu in cpu_stats.index
    ]
    
    # Create horizontal bar chart (better for long CPU names)
    plt.figure(figsize=(12, 8))
    
    colors = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(cpu_stats)))
    bars = plt.barh(range(len(cpu_stats)), cpu_stats['mean'], color=colors, alpha=0.8)
    
    # Add value labels
    for i, (bar, mean_val) in enumerate(zip(bars, cpu_stats['mean'])):
        plt.text(bar.get_width() + max(cpu_stats['mean']) * 0.01, bar.get_y() + bar.get_height()/2,
                f'{mean_val:.0f}ms', ha='left', va='center', fontweight='bold')
    
    # Add sample count information
    for i, count in enumerate(cpu_stats['count']):
        plt.text(max(cpu_stats['mean']) * 0.02, i - 0.3,
                f'n={count}', ha='left', va='center', fontsize=9, style='italic', alpha=0.7)
    
    plt.yticks(range(len(cpu_stats)), cpu_stats.index)
    plt.xlabel('Mean Performance (ms) - Lower is Better', fontsize=12, fontweight='bold')
    plt.ylabel('CPU Model', fontsize=12, fontweight='bold')
    plt.title('CPU Performance Ranking\n(Based on Average Execution Time)', 
              fontsize=14, fontweight='bold')
    plt.grid(axis='x', alpha=0.3)
    
    # Add performance tiers
    best_perf = cpu_stats['mean'].min()
    worst_perf = cpu_stats['mean'].max()
    tier_size = (worst_perf - best_perf) / 3
    
    plt.axvline(x=best_perf + tier_size, color='green', linestyle='--', alpha=0.5, label='High Performance')
    plt.axvline(x=best_perf + 2*tier_size, color='orange', linestyle='--', alpha=0.5, label='Medium Performance')
    plt.legend(loc='lower right')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'cpu_performance_ranking.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"   ✅ Saved: {output_dir / 'cpu_performance_ranking.png'}")


def create_cpu_aces_comparison(data, output_dir):
    """Create CPU performance comparison by ACES version."""
    
    print("\n📊 Creating CPU vs ACES version comparison...")
    
    # Get CPUs with sufficient data for both ACES versions
    cpu_aces_stats = data.groupby(['cpu_model', 'aces_version']).agg({
        'avg_time': ['count', 'mean']
    }).round(2)
    
    # Flatten column names
    cpu_aces_stats.columns = ['count', 'mean']
    cpu_aces_stats = cpu_aces_stats.reset_index()
    
    # Filter CPUs with data for both ACES versions and sufficient samples
    cpu_counts = cpu_aces_stats.groupby('cpu_model')['aces_version'].nunique()
    multi_aces_cpus = cpu_counts[cpu_counts == 2].index
    
    filtered_data = cpu_aces_stats[
        (cpu_aces_stats['cpu_model'].isin(multi_aces_cpus)) &
        (cpu_aces_stats['count'] >= 5)
    ]
    
    if filtered_data.empty:
        print("   ⚠️  No CPUs with sufficient data for both ACES versions")
        return
    
    # Create shorter CPU names
    filtered_data['cpu_short'] = filtered_data['cpu_model'].apply(
        lambda x: x.replace('Intel(R) ', '').replace('(R)', '').replace(' CPU', '')[:25]
    )
    
    # Pivot for plotting
    pivot_data = filtered_data.pivot(index='cpu_short', columns='aces_version', values='mean')
    
    # Create grouped bar chart
    plt.figure(figsize=(14, 8))
    
    ax = pivot_data.plot(kind='bar', figsize=(14, 8), 
                        color=['#1f77b4', '#ff7f0e'], alpha=0.8, width=0.8)
    
    # Add value labels
    for container in ax.containers:
        ax.bar_label(container, fmt='%.0f ms', rotation=90, fontsize=9)
    
    # Calculate and display ACES 2.0 vs 1.0 ratio
    for i, cpu in enumerate(pivot_data.index):
        if not pd.isna(pivot_data.loc[cpu, 'ACES 1.0']) and not pd.isna(pivot_data.loc[cpu, 'ACES 2.0']):
            ratio = pivot_data.loc[cpu, 'ACES 2.0'] / pivot_data.loc[cpu, 'ACES 1.0']
            color = 'red' if ratio > 2 else 'orange' if ratio > 1.5 else 'green'
            ax.text(i, max(pivot_data.loc[cpu]) * 1.1, f'{ratio:.1f}x',
                   ha='center', va='bottom', fontweight='bold', color=color, fontsize=10)
    
    plt.xlabel('CPU Model', fontsize=12, fontweight='bold')
    plt.ylabel('Mean Performance (ms)', fontsize=12, fontweight='bold')
    plt.title('CPU Performance by ACES Version\n(Numbers above bars show ACES 2.0/1.0 ratio)', 
              fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.legend(title='ACES Version', fontsize=11)
    plt.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'cpu_aces_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"   ✅ Saved: {output_dir / 'cpu_aces_comparison.png'}")


def create_performance_variability_chart(data, output_dir):
    """Create CPU performance variability analysis."""
    
    print("\n📊 Creating performance variability chart...")
    
    # Calculate coefficient of variation for each CPU
    cpu_variability = data.groupby('cpu_model')['avg_time'].agg([
        'count', 'mean', 'std'
    ])
    
    # Filter CPUs with sufficient data
    cpu_variability = cpu_variability[cpu_variability['count'] >= 15]
    
    # Calculate coefficient of variation (CV = std/mean * 100)
    cpu_variability['cv'] = (cpu_variability['std'] / cpu_variability['mean'] * 100).round(1)
    cpu_variability = cpu_variability.sort_values('cv')
    
    # Create shorter names
    cpu_variability.index = [
        cpu.replace('Intel(R) ', '').replace('(R)', '').replace(' CPU', '')[:25]
        for cpu in cpu_variability.index
    ]
    
    # Create bar chart
    plt.figure(figsize=(12, 8))
    
    colors = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(cpu_variability)))
    bars = plt.bar(range(len(cpu_variability)), cpu_variability['cv'], 
                   color=colors, alpha=0.8)
    
    # Add value labels
    for bar, cv_val in zip(bars, cpu_variability['cv']):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'{cv_val:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    plt.xticks(range(len(cpu_variability)), cpu_variability.index, rotation=45, ha='right')
    plt.xlabel('CPU Model', fontsize=12, fontweight='bold')
    plt.ylabel('Coefficient of Variation (%)', fontsize=12, fontweight='bold')
    plt.title('CPU Performance Consistency\n(Lower CV = More Consistent Performance)', 
              fontsize=14, fontweight='bold')
    plt.grid(axis='y', alpha=0.3)
    
    # Add consistency interpretation
    plt.axhline(y=50, color='red', linestyle='--', alpha=0.7, label='High Variability (>50%)')
    plt.axhline(y=25, color='orange', linestyle='--', alpha=0.7, label='Medium Variability (25-50%)')
    plt.axhline(y=10, color='green', linestyle='--', alpha=0.7, label='Low Variability (<25%)')
    plt.legend(loc='upper right')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'cpu_performance_variability.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"   ✅ Saved: {output_dir / 'cpu_performance_variability.png'}")


def create_top_cpus_comparison(data, output_dir):
    """Create detailed comparison of top performing CPUs."""
    
    print("\n📊 Creating top CPUs detailed comparison...")
    
    # Get top 5 CPUs by performance (lowest mean time)
    cpu_performance = data.groupby('cpu_model')['avg_time'].agg(['count', 'mean'])
    cpu_performance = cpu_performance[cpu_performance['count'] >= 20]  # Sufficient data
    top_cpus = cpu_performance.nsmallest(5, 'mean').index
    
    top_cpu_data = data[data['cpu_model'].isin(top_cpus)]
    
    # Calculate detailed statistics
    detailed_stats = top_cpu_data.groupby('cpu_model')['avg_time'].agg([
        'count', 'mean', 'median', 'std', 'min', 'max'
    ]).round(2)
    
    # Create shorter names
    detailed_stats.index = [
        cpu.replace('Intel(R) ', '').replace('(R)', '').replace(' CPU', '')[:25]
        for cpu in detailed_stats.index
    ]
    
    # Create subplot with multiple metrics
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Mean Performance
    bars1 = ax1.bar(range(len(detailed_stats)), detailed_stats['mean'], 
                    color='skyblue', alpha=0.8)
    for bar, val in zip(bars1, detailed_stats['mean']):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + val*0.02,
                f'{val:.1f}', ha='center', va='bottom', fontweight='bold')
    ax1.set_xticks(range(len(detailed_stats)))
    ax1.set_xticklabels(detailed_stats.index, rotation=45, ha='right')
    ax1.set_ylabel('Mean Time (ms)')
    ax1.set_title('Mean Performance')
    ax1.grid(axis='y', alpha=0.3)
    
    # 2. Median Performance
    bars2 = ax2.bar(range(len(detailed_stats)), detailed_stats['median'], 
                    color='lightcoral', alpha=0.8)
    for bar, val in zip(bars2, detailed_stats['median']):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + val*0.02,
                f'{val:.1f}', ha='center', va='bottom', fontweight='bold')
    ax2.set_xticks(range(len(detailed_stats)))
    ax2.set_xticklabels(detailed_stats.index, rotation=45, ha='right')
    ax2.set_ylabel('Median Time (ms)')
    ax2.set_title('Median Performance')
    ax2.grid(axis='y', alpha=0.3)
    
    # 3. Standard Deviation
    bars3 = ax3.bar(range(len(detailed_stats)), detailed_stats['std'], 
                    color='lightgreen', alpha=0.8)
    for bar, val in zip(bars3, detailed_stats['std']):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + val*0.02,
                f'{val:.1f}', ha='center', va='bottom', fontweight='bold')
    ax3.set_xticks(range(len(detailed_stats)))
    ax3.set_xticklabels(detailed_stats.index, rotation=45, ha='right')
    ax3.set_ylabel('Standard Deviation (ms)')
    ax3.set_title('Performance Variability')
    ax3.grid(axis='y', alpha=0.3)
    
    # 4. Sample Count
    bars4 = ax4.bar(range(len(detailed_stats)), detailed_stats['count'], 
                    color='gold', alpha=0.8)
    for bar, val in zip(bars4, detailed_stats['count']):
        ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + val*0.02,
                f'{int(val)}', ha='center', va='bottom', fontweight='bold')
    ax4.set_xticks(range(len(detailed_stats)))
    ax4.set_xticklabels(detailed_stats.index, rotation=45, ha='right')
    ax4.set_ylabel('Number of Tests')
    ax4.set_title('Sample Size')
    ax4.grid(axis='y', alpha=0.3)
    
    plt.suptitle('Top 5 CPU Models - Detailed Performance Analysis', 
                 fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_dir / 'top_cpus_detailed_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"   ✅ Saved: {output_dir / 'top_cpus_detailed_comparison.png'}")


if __name__ == "__main__":
    create_cpu_performance_analysis()
