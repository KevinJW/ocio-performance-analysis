#!/usr/bin/env python3
"""
Example: OS Release Performance Comparison with Bar Charts

This example demonstrates how to analyze and visualize performance differences
between OS releases (r7 vs r9) using the OCIO performance analysis tools.
Shows clear bar chart comparisons for easy interpretation.
"""

from src.ocio_performance_analysis import OCIODataAnalyzer, OCIOChartGenerator
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def create_os_comparison_bar_charts():
    """
    Create comprehensive bar chart analysis of OS release performance differences.
    
    This example shows:
    1. Overall performance comparison (r7 vs r9)
    2. Individual CPU performance improvements
    3. ACES version specific improvements
    """
    
    print("🚀 OS Release Performance Comparison Example")
    print("=" * 50)
    
    # Initialize the analyzer
    analyzer = OCIODataAnalyzer()
    analyzer.set_csv_file(Path('data/ocio_test_results.csv'))
    analyzer.load_data()
    
    # Find CPUs with data for multiple OS releases
    cpu_os_counts = analyzer.data.groupby('cpu_model')['os_release'].nunique()
    multi_os_cpus = cpu_os_counts[cpu_os_counts >= 2]
    multi_os_data = analyzer.data[analyzer.data['cpu_model'].isin(multi_os_cpus.index)]
    
    print(f"📊 Found {len(multi_os_cpus)} CPUs with multiple OS releases")
    print(f"📈 Analyzing {len(multi_os_data)} test results")
    
    # Create output directory for examples
    output_dir = Path('examples/outputs')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Overall Performance Comparison Bar Chart
    create_overall_comparison_chart(multi_os_data, output_dir)
    
    # 2. Individual CPU Comparison Charts
    create_individual_cpu_charts(multi_os_data, multi_os_cpus, output_dir)
    
    # 3. Performance Improvement Summary Chart
    create_improvement_summary_chart(multi_os_data, multi_os_cpus, output_dir)
    
    # 4. ACES Version Impact Chart
    create_aces_impact_chart(multi_os_data, output_dir)
    
    print("\n✅ All OS comparison bar charts created successfully!")
    print(f"📁 Charts saved to: {output_dir}")


def create_overall_comparison_chart(data, output_dir):
    """Create overall r7 vs r9 performance comparison bar chart."""
    
    print("\n📊 Creating overall performance comparison chart...")
    
    # Calculate mean performance by OS release and ACES version
    performance_summary = data.groupby(['os_release', 'aces_version'])['avg_time'].agg([
        'mean', 'count', 'std'
    ]).round(2)
    
    # Prepare data for plotting
    plot_data = []
    for (os_rel, aces_ver), stats in performance_summary.iterrows():
        plot_data.append({
            'OS Release': os_rel,
            'ACES Version': aces_ver,
            'Mean Performance (ms)': stats['mean'],
            'Count': stats['count'],
            'Std Dev': stats['std']
        })
    
    plot_df = pd.DataFrame(plot_data)
    
    # Create bar chart
    plt.figure(figsize=(12, 8))
    
    # Create grouped bar chart
    aces_versions = plot_df['ACES Version'].unique()
    x_pos = range(len(aces_versions))
    width = 0.35
    
    r7_data = plot_df[plot_df['OS Release'] == 'r7']['Mean Performance (ms)'].values
    r9_data = plot_df[plot_df['OS Release'] == 'r9']['Mean Performance (ms)'].values
    
    bars1 = plt.bar([x - width/2 for x in x_pos], r7_data, width, 
                   label='r7', color='#ff7f7f', alpha=0.8)
    bars2 = plt.bar([x + width/2 for x in x_pos], r9_data, width,
                   label='r9', color='#7f7fff', alpha=0.8)
    
    # Add value labels on bars
    for bar in bars1:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                f'{height:.1f}ms', ha='center', va='bottom', fontweight='bold')
    
    for bar in bars2:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                f'{height:.1f}ms', ha='center', va='bottom', fontweight='bold')
    
    # Calculate and show improvement percentages
    for i, aces_ver in enumerate(aces_versions):
        r7_val = r7_data[i]
        r9_val = r9_data[i]
        improvement = ((r7_val - r9_val) / r7_val) * 100
        
        # Add improvement text above the bars
        max_height = max(r7_val, r9_val)
        plt.text(i, max_height + max_height*0.15, 
                f'{improvement:.1f}% faster', 
                ha='center', va='bottom', fontsize=12, fontweight='bold',
                color='green' if improvement > 0 else 'red')
    
    plt.xlabel('ACES Version', fontsize=12, fontweight='bold')
    plt.ylabel('Mean Performance (ms)', fontsize=12, fontweight='bold')
    plt.title('OS Release Performance Comparison: r7 vs r9\n(Lower is Better)', 
              fontsize=14, fontweight='bold')
    plt.xticks(x_pos, aces_versions)
    plt.legend(fontsize=12)
    plt.grid(axis='y', alpha=0.3)
    
    # Add summary statistics
    total_r7 = plot_df[plot_df['OS Release'] == 'r7']['Count'].sum()
    total_r9 = plot_df[plot_df['OS Release'] == 'r9']['Count'].sum()
    plt.figtext(0.02, 0.02, f'Data points: r7={total_r7}, r9={total_r9}', 
                fontsize=10, style='italic')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'os_comparison_overall.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"   ✅ Saved: {output_dir / 'os_comparison_overall.png'}")


def create_individual_cpu_charts(data, multi_os_cpus, output_dir):
    """Create individual CPU performance comparison charts."""
    
    print("\n📊 Creating individual CPU comparison charts...")
    
    for cpu in multi_os_cpus.index:
        cpu_data = data[data['cpu_model'] == cpu]
        
        # Create safe filename
        safe_cpu_name = (cpu.replace('Intel(R) ', '')
                           .replace('(R)', '')
                           .replace(' CPU', '')
                           .replace('@', 'at')
                           .replace(' ', '_')
                           .replace('(', '')
                           .replace(')', ''))
        
        # Calculate performance by OS and ACES version
        cpu_summary = cpu_data.groupby(['os_release', 'aces_version'])['avg_time'].agg([
            'mean', 'count'
        ]).round(2)
        
        # Prepare data for plotting
        plot_data = []
        for (os_rel, aces_ver), stats in cpu_summary.iterrows():
            plot_data.append({
                'OS Release': os_rel,
                'ACES Version': aces_ver, 
                'Mean Performance (ms)': stats['mean'],
                'Count': stats['count']
            })
        
        if not plot_data:
            continue
            
        plot_df = pd.DataFrame(plot_data)
        
        # Create bar chart
        plt.figure(figsize=(10, 6))
        
        aces_versions = plot_df['ACES Version'].unique()
        x_pos = range(len(aces_versions))
        width = 0.35
        
        try:
            r7_data = plot_df[plot_df['OS Release'] == 'r7']['Mean Performance (ms)'].values
            r9_data = plot_df[plot_df['OS Release'] == 'r9']['Mean Performance (ms)'].values
            
            bars1 = plt.bar([x - width/2 for x in x_pos], r7_data, width,
                           label='r7', color='#ff9999', alpha=0.8)
            bars2 = plt.bar([x + width/2 for x in x_pos], r9_data, width,
                           label='r9', color='#9999ff', alpha=0.8)
            
            # Add value labels
            for bar in bars1:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                        f'{height:.1f}ms', ha='center', va='bottom', fontsize=10)
            
            for bar in bars2:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                        f'{height:.1f}ms', ha='center', va='bottom', fontsize=10)
            
            # Add improvement percentages
            for i, aces_ver in enumerate(aces_versions):
                if i < len(r7_data) and i < len(r9_data):
                    r7_val = r7_data[i]
                    r9_val = r9_data[i]
                    improvement = ((r7_val - r9_val) / r7_val) * 100
                    
                    max_height = max(r7_val, r9_val)
                    plt.text(i, max_height + max_height*0.1,
                            f'{improvement:.1f}%',
                            ha='center', va='bottom', fontsize=11, fontweight='bold',
                            color='green' if improvement > 0 else 'red')
            
            plt.xlabel('ACES Version', fontsize=11, fontweight='bold')
            plt.ylabel('Mean Performance (ms)', fontsize=11, fontweight='bold')
            plt.title(f'Performance Comparison: {cpu[:50]}\nr7 vs r9 (Lower is Better)', 
                      fontsize=12, fontweight='bold')
            plt.xticks(x_pos, aces_versions)
            plt.legend()
            plt.grid(axis='y', alpha=0.3)
            
            plt.tight_layout()
            filename = f'os_comparison_{safe_cpu_name}.png'
            plt.savefig(output_dir / filename, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"   ✅ Saved: {output_dir / filename}")
            
        except Exception as e:
            print(f"   ⚠️  Skipped {cpu}: {e}")
            plt.close()


def create_improvement_summary_chart(data, multi_os_cpus, output_dir):
    """Create performance improvement summary bar chart."""
    
    print("\n📊 Creating improvement summary chart...")
    
    # Calculate improvements for each CPU and ACES version
    improvement_data = []
    
    for cpu in multi_os_cpus.index:
        cpu_data = data[data['cpu_model'] == cpu]
        cpu_stats = cpu_data.groupby(['os_release', 'aces_version'])['avg_time'].mean()
        
        cpu_short = (cpu.replace('Intel(R) ', '')
                       .replace('(R)', '')
                       .replace(' CPU @ 3.60GHz', '')
                       .replace(' CPU @ 3.10GHz', '')
                       .replace(' CPU @ 3.00GHz', ''))
        
        for aces_version in ['ACES 1.0', 'ACES 2.0']:
            try:
                r7_mean = cpu_stats[('r7', aces_version)]
                r9_mean = cpu_stats[('r9', aces_version)]
                improvement_pct = ((r7_mean - r9_mean) / r7_mean) * 100
                
                improvement_data.append({
                    'CPU': cpu_short,
                    'ACES Version': aces_version,
                    'Improvement %': improvement_pct
                })
            except KeyError:
                pass
    
    if not improvement_data:
        print("   ⚠️  No improvement data available")
        return
        
    improvement_df = pd.DataFrame(improvement_data)
    
    # Create grouped bar chart
    plt.figure(figsize=(14, 8))
    
    # Pivot for easier plotting
    pivot_df = improvement_df.pivot(index='CPU', columns='ACES Version', values='Improvement %')
    
    ax = pivot_df.plot(kind='bar', figsize=(14, 8), 
                      color=['#87CEEB', '#FFB6C1'], alpha=0.8, width=0.8)
    
    # Add value labels on bars
    for container in ax.containers:
        ax.bar_label(container, fmt='%.1f%%', fontweight='bold')
    
    plt.xlabel('CPU Model', fontsize=12, fontweight='bold')
    plt.ylabel('Performance Improvement (%)', fontsize=12, fontweight='bold')
    plt.title('OS Release Performance Improvements by CPU\n(r7 → r9, Higher is Better)', 
              fontsize=14, fontweight='bold')
    plt.legend(title='ACES Version', fontsize=11, title_fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', alpha=0.3)
    
    # Add average improvement line
    overall_avg = improvement_df['Improvement %'].mean()
    plt.axhline(y=overall_avg, color='red', linestyle='--', alpha=0.7,
               label=f'Average: {overall_avg:.1f}%')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'os_improvement_summary.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"   ✅ Saved: {output_dir / 'os_improvement_summary.png'}")


def create_aces_impact_chart(data, output_dir):
    """Create ACES version impact comparison chart."""
    
    print("\n📊 Creating ACES version impact chart...")
    
    # Calculate improvement by ACES version
    aces_improvements = []
    
    for aces_version in ['ACES 1.0', 'ACES 2.0']:
        aces_data = data[data['aces_version'] == aces_version]
        
        r7_mean = aces_data[aces_data['os_release'] == 'r7']['avg_time'].mean()
        r9_mean = aces_data[aces_data['os_release'] == 'r9']['avg_time'].mean()
        improvement = ((r7_mean - r9_mean) / r7_mean) * 100
        
        r7_count = len(aces_data[aces_data['os_release'] == 'r7'])
        r9_count = len(aces_data[aces_data['os_release'] == 'r9'])
        
        aces_improvements.append({
            'ACES Version': aces_version,
            'Improvement %': improvement,
            'r7 Mean (ms)': r7_mean,
            'r9 Mean (ms)': r9_mean,
            'r7 Count': r7_count,
            'r9 Count': r9_count
        })
    
    improvement_df = pd.DataFrame(aces_improvements)
    
    # Create bar chart
    plt.figure(figsize=(10, 6))
    
    bars = plt.bar(improvement_df['ACES Version'], improvement_df['Improvement %'],
                   color=['#4CAF50', '#2196F3'], alpha=0.8, width=0.6)
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{height:.1f}%', ha='center', va='bottom', 
                fontsize=14, fontweight='bold')
    
    # Add baseline performance info
    for i, row in improvement_df.iterrows():
        plt.text(i, -5, f'r7: {row["r7 Mean (ms)"]:.0f}ms\nr9: {row["r9 Mean (ms)"]:.0f}ms',
                ha='center', va='top', fontsize=10, style='italic')
    
    plt.xlabel('ACES Version', fontsize=12, fontweight='bold')
    plt.ylabel('Performance Improvement (%)', fontsize=12, fontweight='bold')
    plt.title('OS Release Impact by ACES Version\n(r7 → r9 Improvement)', 
              fontsize=14, fontweight='bold')
    plt.grid(axis='y', alpha=0.3)
    plt.ylim(bottom=-15)  # Make room for baseline info
    
    plt.tight_layout()
    plt.savefig(output_dir / 'aces_version_impact.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"   ✅ Saved: {output_dir / 'aces_version_impact.png'}")


if __name__ == "__main__":
    create_os_comparison_bar_charts()
