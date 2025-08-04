#!/usr/bin/env python3
"""
Create OS Release Differences Report
"""

from src.ocio_performance_analysis import OCIODataAnalyzer
from pathlib import Path
import pandas as pd

def create_os_differences_report():
    """Create comprehensive OS release differences report"""
    
    analyzer = OCIODataAnalyzer()
    analyzer.set_csv_file(Path('data/ocio_test_results.csv'))
    analyzer.load_data()

    # Get CPUs with multiple OS releases
    cpu_os_counts = analyzer.data.groupby('cpu_model')['os_release'].nunique()
    multi_os_cpus = cpu_os_counts[cpu_os_counts >= 2]
    multi_os_data = analyzer.data[analyzer.data['cpu_model'].isin(multi_os_cpus.index)]

    print('📋 GENERATING OS RELEASE DIFFERENCES REPORT')
    print('=' * 60)

    report_lines = []
    report_lines.append('# OS Release Performance Differences Report')
    report_lines.append('')
    report_lines.append('## Executive Summary')
    report_lines.append(f'- **CPUs Analyzed**: {len(multi_os_cpus)} CPUs with data for multiple OS releases')
    report_lines.append(f'- **Total Data Points**: {len(multi_os_data)} test results')
    report_lines.append(f'- **OS Releases Compared**: r7 vs r9')
    report_lines.append('')

    # Overall comparison
    overall_stats = multi_os_data.groupby(['os_release', 'aces_version'])['avg_time'].agg(['count', 'mean', 'median', 'std']).round(2)
    report_lines.append('## Overall Performance Comparison')
    report_lines.append('')
    report_lines.append('| OS Release | ACES Version | Count | Mean (ms) | Median (ms) | Std Dev |')
    report_lines.append('|------------|--------------|-------|-----------|-------------|---------|')

    for (os_rel, aces_ver), stats in overall_stats.iterrows():
        count = stats['count']
        mean = stats['mean']
        median = stats['median'] 
        std = stats['std']
        report_lines.append(f'| {os_rel} | {aces_ver} | {count} | {mean} | {median} | {std} |')

    report_lines.append('')

    # Performance improvements
    report_lines.append('## Performance Improvements (r7 -> r9)')
    report_lines.append('')

    for aces_version in ['ACES 1.0', 'ACES 2.0']:
        r7_mean = overall_stats.loc[('r7', aces_version), 'mean']
        r9_mean = overall_stats.loc[('r9', aces_version), 'mean']
        improvement_pct = ((r7_mean - r9_mean) / r7_mean) * 100
        
        report_lines.append(f'**{aces_version}:**')
        report_lines.append(f'- r7 Mean: {r7_mean:.2f}ms')
        report_lines.append(f'- r9 Mean: {r9_mean:.2f}ms')
        status = "faster" if improvement_pct > 0 else "slower"
        report_lines.append(f'- **Improvement: {improvement_pct:.1f}%** ({status})')
        report_lines.append('')

    # Individual CPU analysis
    report_lines.append('## Individual CPU Analysis')
    report_lines.append('')

    for cpu in multi_os_cpus.index:
        cpu_data = multi_os_data[multi_os_data['cpu_model'] == cpu]
        report_lines.append(f'### {cpu}')
        report_lines.append('')
        
        cpu_stats = cpu_data.groupby(['os_release', 'aces_version'])['avg_time'].agg(['count', 'mean', 'median']).round(2)
        
        report_lines.append('| OS Release | ACES Version | Count | Mean (ms) | Median (ms) |')
        report_lines.append('|------------|--------------|-------|-----------|-------------|')
        
        for (os_rel, aces_ver), stats in cpu_stats.iterrows():
            count = stats['count']
            mean = stats['mean']
            median = stats['median']
            report_lines.append(f'| {os_rel} | {aces_ver} | {count} | {mean} | {median} |')
        
        # Calculate improvements for this CPU
        report_lines.append('')
        report_lines.append('**Performance Changes:**')
        
        for aces_version in ['ACES 1.0', 'ACES 2.0']:
            try:
                r7_mean = cpu_stats.loc[('r7', aces_version), 'mean']
                r9_mean = cpu_stats.loc[('r9', aces_version), 'mean']
                improvement_pct = ((r7_mean - r9_mean) / r7_mean) * 100
                
                status = "improvement" if improvement_pct > 0 else "regression"
                report_lines.append(f'- {aces_version}: {improvement_pct:.1f}% {status}')
            except KeyError:
                pass
        
        report_lines.append('')

    # Save report
    report_content = '\n'.join(report_lines)
    report_path = Path('analysis_results/os_release_differences_report.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)

    print(f'📄 Report saved to: {report_path}')
    print()
    print('Quick Summary:')
    print(overall_stats)
    
    return report_path

if __name__ == "__main__":
    create_os_differences_report()
