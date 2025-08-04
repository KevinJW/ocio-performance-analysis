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
    
    # 5. OCIO Version Comparison Chart
    create_ocio_version_comparison_chart(analyzer.data, output_dir)
    
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
    
    # Create side-by-side comparison chart
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Extract data for both OS releases
    aces_versions = improvement_df['ACES Version'].tolist()
    r7_values = improvement_df['r7 Mean (ms)'].tolist()
    r9_values = improvement_df['r9 Mean (ms)'].tolist()
    
    # Calculate shared Y-axis limits (add 10% padding)
    all_values = r7_values + r9_values
    y_min = 0
    y_max = max(all_values) * 1.15
    
    # Left chart: r7 Performance
    bars_r7 = ax1.bar(aces_versions, r7_values, 
                      color=['#FF6B6B', '#FF8E53'], alpha=0.8, width=0.6)
    
    # Add value labels for r7
    for bar, val in zip(bars_r7, r7_values):
        ax1.text(bar.get_x() + bar.get_width()/2., bar.get_height() + y_max*0.02,
                f'{val:.1f} ms', ha='center', va='bottom', 
                fontsize=12, fontweight='bold')
    
    # Add sample counts for r7
    r7_counts = improvement_df['r7 Count'].tolist()
    for i, count in enumerate(r7_counts):
        ax1.text(i, y_max*0.85, f'n={count}', ha='center', va='center',
                fontsize=10, style='italic', 
                bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.7))
    
    ax1.set_xlabel('ACES Version', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Performance (ms)', fontsize=12, fontweight='bold')
    ax1.set_title('r7 Performance\n(Lower is Better)', fontsize=14, fontweight='bold')
    ax1.set_ylim(y_min, y_max)
    ax1.grid(axis='y', alpha=0.3)
    
    # Right chart: r9 Performance  
    bars_r9 = ax2.bar(aces_versions, r9_values,
                      color=['#4ECDC4', '#45B7D1'], alpha=0.8, width=0.6)
    
    # Add value labels for r9
    for bar, val in zip(bars_r9, r9_values):
        ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height() + y_max*0.02,
                f'{val:.1f} ms', ha='center', va='bottom', 
                fontsize=12, fontweight='bold')
    
    # Add sample counts for r9
    r9_counts = improvement_df['r9 Count'].tolist()
    for i, count in enumerate(r9_counts):
        ax2.text(i, y_max*0.85, f'n={count}', ha='center', va='center',
                fontsize=10, style='italic',
                bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.7))
    
    ax2.set_xlabel('ACES Version', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Performance (ms)', fontsize=12, fontweight='bold')
    ax2.set_title('r9 Performance\n(Lower is Better)', fontsize=14, fontweight='bold')
    ax2.set_ylim(y_min, y_max)
    ax2.grid(axis='y', alpha=0.3)
    
    # Add improvement annotations between charts
    for i, (aces_ver, improvement) in enumerate(zip(aces_versions, improvement_df['Improvement %'])):
        # Add improvement arrow and text in the middle
        mid_x = 0.5
        y_pos = 0.7 - (i * 0.2)  # Stagger vertically
        
        fig.text(mid_x, y_pos, f'{aces_ver}\n{improvement:.1f}% faster', 
                ha='center', va='center', fontsize=12, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.5", facecolor='lightgreen' if improvement > 0 else 'lightcoral', alpha=0.8),
                transform=fig.transFigure)
        
        # Add arrow pointing from r7 to r9 using matplotlib.patches.FancyArrowPatch
        from matplotlib.patches import FancyArrowPatch
        arrow = FancyArrowPatch((0.15, y_pos), (0.85, y_pos),
                               arrowstyle='->', mutation_scale=20, 
                               color='darkgreen' if improvement > 0 else 'darkred',
                               linewidth=2, transform=fig.transFigure)
        fig.patches.append(arrow)
    
    # Overall title
    plt.suptitle('OS Release Performance Comparison: r7 vs r9 by ACES Version', 
                 fontsize=16, fontweight='bold', y=0.95)
    
    # Add overall improvement summary
    overall_improvement = improvement_df['Improvement %'].mean()
    fig.text(0.5, 0.02, f'Average Performance Improvement: {overall_improvement:.1f}%', 
             ha='center', va='bottom', fontsize=12, fontweight='bold', style='italic')
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.85, bottom=0.15)
    plt.savefig(output_dir / 'aces_version_impact.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"   ✅ Saved: {output_dir / 'aces_version_impact.png'}")


def create_ocio_version_comparison_chart(data, output_dir):
    """Create OCIO version comparison chart (2.4.1 vs 2.4.2)."""
    
    print("\n📊 Creating OCIO version comparison chart...")
    
    # Calculate improvement by OCIO version
    ocio_improvements = []
    
    for aces_version in ['ACES 1.0', 'ACES 2.0']:
        aces_data = data[data['aces_version'] == aces_version]
        
        # Check if we have data for both OCIO versions
        ocio_241_data = aces_data[aces_data['ocio_version'] == '2.4.1']
        ocio_242_data = aces_data[aces_data['ocio_version'] == '2.4.2']
        
        if len(ocio_241_data) == 0 or len(ocio_242_data) == 0:
            continue
            
        ocio_241_mean = ocio_241_data['avg_time'].mean()
        ocio_242_mean = ocio_242_data['avg_time'].mean()
        improvement = ((ocio_241_mean - ocio_242_mean) / ocio_241_mean) * 100
        
        ocio_241_count = len(ocio_241_data)
        ocio_242_count = len(ocio_242_data)
        
        ocio_improvements.append({
            'ACES Version': aces_version,
            'Improvement %': improvement,
            '2.4.1 Mean (ms)': ocio_241_mean,
            '2.4.2 Mean (ms)': ocio_242_mean,
            '2.4.1 Count': ocio_241_count,
            '2.4.2 Count': ocio_242_count
        })
    
    if not ocio_improvements:
        print("   ⚠️  No data available for both OCIO versions")
        return
        
    improvement_df = pd.DataFrame(ocio_improvements)
    
    # Create side-by-side comparison chart
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Extract data for both OCIO versions
    aces_versions = improvement_df['ACES Version'].tolist()
    ocio_241_values = improvement_df['2.4.1 Mean (ms)'].tolist()
    ocio_242_values = improvement_df['2.4.2 Mean (ms)'].tolist()
    
    # Calculate shared Y-axis limits (add 10% padding)
    all_values = ocio_241_values + ocio_242_values
    y_min = 0
    y_max = max(all_values) * 1.15
    
    # Left chart: OCIO 2.4.1 Performance
    bars_241 = ax1.bar(aces_versions, ocio_241_values, 
                       color=['#9C27B0', '#673AB7'], alpha=0.8, width=0.6)
    
    # Add value labels for 2.4.1
    for bar, val in zip(bars_241, ocio_241_values):
        ax1.text(bar.get_x() + bar.get_width()/2., bar.get_height() + y_max*0.02,
                f'{val:.1f} ms', ha='center', va='bottom', 
                fontsize=12, fontweight='bold')
    
    # Add sample counts for 2.4.1
    ocio_241_counts = improvement_df['2.4.1 Count'].tolist()
    for i, count in enumerate(ocio_241_counts):
        ax1.text(i, y_max*0.85, f'n={count}', ha='center', va='center',
                fontsize=10, style='italic', 
                bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.7))
    
    ax1.set_xlabel('ACES Version', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Performance (ms)', fontsize=12, fontweight='bold')
    ax1.set_title('OCIO 2.4.1 Performance\n(Lower is Better)', fontsize=14, fontweight='bold')
    ax1.set_ylim(y_min, y_max)
    ax1.grid(axis='y', alpha=0.3)
    
    # Right chart: OCIO 2.4.2 Performance  
    bars_242 = ax2.bar(aces_versions, ocio_242_values,
                       color=['#00BCD4', '#009688'], alpha=0.8, width=0.6)
    
    # Add value labels for 2.4.2
    for bar, val in zip(bars_242, ocio_242_values):
        ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height() + y_max*0.02,
                f'{val:.1f} ms', ha='center', va='bottom', 
                fontsize=12, fontweight='bold')
    
    # Add sample counts for 2.4.2
    ocio_242_counts = improvement_df['2.4.2 Count'].tolist()
    for i, count in enumerate(ocio_242_counts):
        ax2.text(i, y_max*0.85, f'n={count}', ha='center', va='center',
                fontsize=10, style='italic',
                bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.7))
    
    ax2.set_xlabel('ACES Version', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Performance (ms)', fontsize=12, fontweight='bold')
    ax2.set_title('OCIO 2.4.2 Performance\n(Lower is Better)', fontsize=14, fontweight='bold')
    ax2.set_ylim(y_min, y_max)
    ax2.grid(axis='y', alpha=0.3)
    
    # Add improvement annotations between charts
    for i, (aces_ver, improvement) in enumerate(zip(aces_versions, improvement_df['Improvement %'])):
        # Add improvement arrow and text in the middle
        mid_x = 0.5
        y_pos = 0.7 - (i * 0.2)  # Stagger vertically
        
        fig.text(mid_x, y_pos, f'{aces_ver}\n{improvement:.1f}% faster', 
                ha='center', va='center', fontsize=12, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.5", facecolor='lightgreen' if improvement > 0 else 'lightcoral', alpha=0.8),
                transform=fig.transFigure)
        
        # Add arrow pointing from 2.4.1 to 2.4.2 using matplotlib.patches.FancyArrowPatch
        from matplotlib.patches import FancyArrowPatch
        arrow = FancyArrowPatch((0.15, y_pos), (0.85, y_pos),
                               arrowstyle='->', mutation_scale=20, 
                               color='darkgreen' if improvement > 0 else 'darkred',
                               linewidth=2, transform=fig.transFigure)
        fig.patches.append(arrow)
    
    # Overall title
    plt.suptitle('OCIO Version Performance Comparison: 2.4.1 vs 2.4.2 by ACES Version', 
                 fontsize=16, fontweight='bold', y=0.95)
    
    # Add overall improvement summary
    overall_improvement = improvement_df['Improvement %'].mean()
    fig.text(0.5, 0.02, f'Average Performance Improvement: {overall_improvement:.1f}%', 
             ha='center', va='bottom', fontsize=12, fontweight='bold', style='italic')
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.85, bottom=0.15)
    plt.savefig(output_dir / 'ocio_version_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"   ✅ Saved: {output_dir / 'ocio_version_comparison.png'}")


if __name__ == "__main__":
    create_os_comparison_bar_charts()
