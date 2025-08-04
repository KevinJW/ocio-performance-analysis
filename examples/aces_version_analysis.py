#!/usr/bin/env python3
"""
Example: ACES Version Performance Analysis with Bar Charts

This example demonstrates how to analyze the performance impact
of different ACES versions using clear bar chart visualizations.
Shows version comparisons, impact ratios, and statistical insights.
"""

from src.ocio_performance_analysis import OCIODataAnalyzer
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


def create_aces_version_analysis():
    """
    Create comprehensive ACES version analysis with bar charts.
    
    This example demonstrates:
    1. Overall ACES version performance comparison
    2. ACES performance impact by CPU type
    3. Performance distribution analysis by ACES version
    4. Statistical significance of version differences
    """
    
    print("🎨 ACES Version Performance Analysis Example")
    print("=" * 55)
    
    # Initialize the analyzer
    analyzer = OCIODataAnalyzer()
    analyzer.set_csv_file(Path('data/ocio_test_results.csv'))
    analyzer.load_data()
    
    print(f"📊 Analyzing {len(analyzer.data)} test results")
    aces_counts = analyzer.data['aces_version'].value_counts()
    print(f"🎨 ACES Version Distribution:")
    for version, count in aces_counts.items():
        print(f"   • {version}: {count} tests")
    
    # Create output directory
    output_dir = Path('examples/outputs')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Overall ACES Version Comparison
    create_aces_overall_comparison(analyzer.data, output_dir)
    
    # 2. ACES Performance by CPU Family
    create_aces_cpu_impact(analyzer.data, output_dir)
    
    # 3. Performance Distribution Analysis
    create_aces_distribution_analysis(analyzer.data, output_dir)
    
    # 4. ACES Version Performance Ratios
    create_aces_performance_ratios(analyzer.data, output_dir)
    
    print("\n✅ All ACES version analysis charts created successfully!")
    print(f"📁 Charts saved to: {output_dir}")


def create_aces_overall_comparison(data, output_dir):
    """Create overall ACES version performance comparison."""
    
    print("\n📊 Creating overall ACES version comparison...")
    
    # Calculate statistics by ACES version
    aces_stats = data.groupby('aces_version')['avg_time'].agg([
        'count', 'mean', 'median', 'std', 'min', 'max'
    ]).round(2)
    
    # Create figure with subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Mean Performance
    colors = ['#2E8B57', '#FF6347']  # Green for ACES 1.0, Red for ACES 2.0
    bars1 = ax1.bar(aces_stats.index, aces_stats['mean'], color=colors, alpha=0.8)
    for bar, val in zip(bars1, aces_stats['mean']):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + val*0.02,
                f'{val:.1f} ms', ha='center', va='bottom', fontweight='bold', fontsize=12)
    ax1.set_ylabel('Mean Time (ms)', fontweight='bold')
    ax1.set_title('Mean Performance by ACES Version', fontweight='bold', fontsize=14)
    ax1.grid(axis='y', alpha=0.3)
    
    # Add improvement percentage
    if len(aces_stats) == 2:
        improvement = ((aces_stats.loc['ACES 2.0', 'mean'] - aces_stats.loc['ACES 1.0', 'mean']) / 
                      aces_stats.loc['ACES 1.0', 'mean'] * 100)
        ax1.text(0.5, max(aces_stats['mean']) * 0.9, 
                f'ACES 2.0 is {abs(improvement):.1f}% {"slower" if improvement > 0 else "faster"}',
                ha='center', va='center', fontweight='bold', fontsize=12,
                bbox=dict(boxstyle="round,pad=0.3", facecolor='yellow', alpha=0.7))
    
    # 2. Median Performance
    bars2 = ax2.bar(aces_stats.index, aces_stats['median'], color=colors, alpha=0.8)
    for bar, val in zip(bars2, aces_stats['median']):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + val*0.02,
                f'{val:.1f} ms', ha='center', va='bottom', fontweight='bold', fontsize=12)
    ax2.set_ylabel('Median Time (ms)', fontweight='bold')
    ax2.set_title('Median Performance by ACES Version', fontweight='bold', fontsize=14)
    ax2.grid(axis='y', alpha=0.3)
    
    # 3. Standard Deviation (Consistency)
    bars3 = ax3.bar(aces_stats.index, aces_stats['std'], color=colors, alpha=0.8)
    for bar, val in zip(bars3, aces_stats['std']):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + val*0.02,
                f'{val:.1f} ms', ha='center', va='bottom', fontweight='bold', fontsize=12)
    ax3.set_ylabel('Standard Deviation (ms)', fontweight='bold')
    ax3.set_title('Performance Consistency\n(Lower = More Consistent)', fontweight='bold', fontsize=14)
    ax3.grid(axis='y', alpha=0.3)
    
    # 4. Sample Count
    bars4 = ax4.bar(aces_stats.index, aces_stats['count'], color=colors, alpha=0.8)
    for bar, val in zip(bars4, aces_stats['count']):
        ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + val*0.02,
                f'{int(val)}', ha='center', va='bottom', fontweight='bold', fontsize=12)
    ax4.set_ylabel('Number of Tests', fontweight='bold')
    ax4.set_title('Sample Size by ACES Version', fontweight='bold', fontsize=14)
    ax4.grid(axis='y', alpha=0.3)
    
    plt.suptitle('ACES Version Performance Overview', fontsize=18, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_dir / 'aces_overall_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"   ✅ Saved: {output_dir / 'aces_overall_comparison.png'}")


def create_aces_cpu_impact(data, output_dir):
    """Create ACES performance impact by CPU type."""
    
    print("\n📊 Creating ACES performance impact by CPU...")
    
    # Get CPUs with data for both ACES versions
    cpu_aces_data = data.groupby(['cpu_model', 'aces_version'])['avg_time'].agg(['count', 'mean']).reset_index()
    
    # Filter CPUs with sufficient data for both versions
    cpu_counts = cpu_aces_data.groupby('cpu_model')['aces_version'].nunique()
    both_versions_cpus = cpu_counts[cpu_counts == 2].index
    
    filtered_data = cpu_aces_data[
        (cpu_aces_data['cpu_model'].isin(both_versions_cpus)) &
        (cpu_aces_data['count'] >= 5)
    ]
    
    if filtered_data.empty:
        print("   ⚠️  No CPUs with sufficient data for both ACES versions")
        return
    
    # Calculate performance ratios
    pivot_data = filtered_data.pivot(index='cpu_model', columns='aces_version', values='mean')
    pivot_data['ratio'] = pivot_data['ACES 2.0'] / pivot_data['ACES 1.0']
    pivot_data = pivot_data.sort_values('ratio')
    
    # Create shorter CPU names
    pivot_data.index = [
        cpu.replace('Intel(R) ', '').replace('(R)', '').replace(' CPU', '')[:30]
        for cpu in pivot_data.index
    ]
    
    # Create ratio bar chart
    plt.figure(figsize=(14, 8))
    
    # Color bars based on ratio (green if <1.0, red if >1.0)
    colors = ['green' if ratio < 1.0 else 'red' for ratio in pivot_data['ratio']]
    
    bars = plt.bar(range(len(pivot_data)), pivot_data['ratio'], color=colors, alpha=0.7)
    
    # Add value labels
    for bar, ratio in zip(bars, pivot_data['ratio']):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                f'{ratio:.2f}x', ha='center', va='bottom', fontweight='bold')
    
    # Add reference line at 1.0
    plt.axhline(y=1.0, color='black', linestyle='--', alpha=0.8, linewidth=2)
    plt.text(len(pivot_data)/2, 1.05, 'No Performance Change', ha='center', va='bottom',
             fontweight='bold', bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
    
    plt.xticks(range(len(pivot_data)), pivot_data.index, rotation=45, ha='right')
    plt.xlabel('CPU Model', fontweight='bold', fontsize=12)
    plt.ylabel('ACES 2.0 / ACES 1.0 Ratio', fontweight='bold', fontsize=12)
    plt.title('ACES Version Performance Impact by CPU\n(Values < 1.0 = ACES 2.0 is faster)', 
              fontweight='bold', fontsize=14)
    plt.grid(axis='y', alpha=0.3)
    
    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor='green', alpha=0.7, label='ACES 2.0 Faster'),
                      Patch(facecolor='red', alpha=0.7, label='ACES 2.0 Slower')]
    plt.legend(handles=legend_elements, loc='upper right')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'aces_cpu_impact.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"   ✅ Saved: {output_dir / 'aces_cpu_impact.png'}")


def create_aces_distribution_analysis(data, output_dir):
    """Create ACES performance distribution analysis."""
    
    print("\n📊 Creating ACES performance distribution analysis...")
    
    # Calculate percentile statistics
    aces_percentiles = data.groupby('aces_version')['avg_time'].quantile([0.25, 0.5, 0.75, 0.9, 0.95]).unstack()
    
    # Create percentile comparison chart
    plt.figure(figsize=(12, 8))
    
    x = np.arange(len(aces_percentiles.columns))
    width = 0.35
    
    colors = ['#2E8B57', '#FF6347']  # Green and Red
    
    for i, (version, color) in enumerate(zip(aces_percentiles.index, colors)):
        offset = (i - 0.5) * width
        bars = plt.bar(x + offset, aces_percentiles.loc[version], width, 
                      label=version, color=color, alpha=0.8)
        
        # Add value labels
        for bar, val in zip(bars, aces_percentiles.loc[version]):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + val*0.01,
                    f'{val:.0f}', ha='center', va='bottom', fontweight='bold')
    
    plt.xlabel('Percentile', fontweight='bold', fontsize=12)
    plt.ylabel('Time (ms)', fontweight='bold', fontsize=12)
    plt.title('ACES Version Performance Percentiles\n(Distribution Comparison)', 
              fontweight='bold', fontsize=14)
    plt.xticks(x, ['25th', '50th (Median)', '75th', '90th', '95th'])
    plt.legend(fontsize=12)
    plt.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'aces_distribution_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"   ✅ Saved: {output_dir / 'aces_distribution_analysis.png'}")


def create_aces_performance_ratios(data, output_dir):
    """Create detailed ACES performance ratio analysis."""
    
    print("\n📊 Creating ACES performance ratio analysis...")
    
    # Calculate ratios by different groupings
    groupings = {
        'Overall': data.groupby('aces_version')['avg_time'].mean(),
        'By OS': data.groupby(['os_release', 'aces_version'])['avg_time'].mean().unstack().dropna(),
        'By OCIO': data.groupby(['ocio_version', 'aces_version'])['avg_time'].mean().unstack().dropna()
    }
    
    # Create subplot for different ratio analyses
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    # 1. Overall ratio
    if 'ACES 1.0' in groupings['Overall'] and 'ACES 2.0' in groupings['Overall']:
        overall_ratio = groupings['Overall']['ACES 2.0'] / groupings['Overall']['ACES 1.0']
        color = 'green' if overall_ratio < 1.0 else 'red'
        bar = axes[0].bar(['Overall'], [overall_ratio], color=color, alpha=0.8)
        axes[0].text(0, overall_ratio + 0.05, f'{overall_ratio:.2f}x', 
                    ha='center', va='bottom', fontweight='bold', fontsize=12)
        axes[0].axhline(y=1.0, color='black', linestyle='--', alpha=0.8)
        axes[0].set_ylabel('ACES 2.0 / ACES 1.0 Ratio', fontweight='bold')
        axes[0].set_title('Overall Performance Ratio', fontweight='bold')
        axes[0].grid(axis='y', alpha=0.3)
    
    # 2. By OS Release
    if len(groupings['By OS']) > 0:
        os_ratios = groupings['By OS']['ACES 2.0'] / groupings['By OS']['ACES 1.0']
        colors = ['green' if ratio < 1.0 else 'red' for ratio in os_ratios]
        bars = axes[1].bar(range(len(os_ratios)), os_ratios, color=colors, alpha=0.8)
        
        for bar, ratio in zip(bars, os_ratios):
            axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                        f'{ratio:.2f}x', ha='center', va='bottom', fontweight='bold')
        
        axes[1].axhline(y=1.0, color='black', linestyle='--', alpha=0.8)
        axes[1].set_xticks(range(len(os_ratios)))
        axes[1].set_xticklabels(os_ratios.index, rotation=45, ha='right')
        axes[1].set_ylabel('ACES 2.0 / ACES 1.0 Ratio', fontweight='bold')
        axes[1].set_title('Ratio by OS Release', fontweight='bold')
        axes[1].grid(axis='y', alpha=0.3)
    
    # 3. By OCIO Version
    if len(groupings['By OCIO']) > 0:
        ocio_ratios = groupings['By OCIO']['ACES 2.0'] / groupings['By OCIO']['ACES 1.0']
        colors = ['green' if ratio < 1.0 else 'red' for ratio in ocio_ratios]
        bars = axes[2].bar(range(len(ocio_ratios)), ocio_ratios, color=colors, alpha=0.8)
        
        for bar, ratio in zip(bars, ocio_ratios):
            axes[2].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                        f'{ratio:.2f}x', ha='center', va='bottom', fontweight='bold')
        
        axes[2].axhline(y=1.0, color='black', linestyle='--', alpha=0.8)
        axes[2].set_xticks(range(len(ocio_ratios)))
        axes[2].set_xticklabels(ocio_ratios.index, rotation=45, ha='right')
        axes[2].set_ylabel('ACES 2.0 / ACES 1.0 Ratio', fontweight='bold')
        axes[2].set_title('Ratio by OCIO Version', fontweight='bold')
        axes[2].grid(axis='y', alpha=0.3)
    
    plt.suptitle('ACES Version Performance Ratios Across Different Categories', 
                 fontweight='bold', fontsize=16)
    plt.tight_layout()
    plt.savefig(output_dir / 'aces_performance_ratios.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"   ✅ Saved: {output_dir / 'aces_performance_ratios.png'}")


if __name__ == "__main__":
    create_aces_version_analysis()
