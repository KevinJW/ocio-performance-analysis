"""
Quick analysis of OCIO 2.4.1 vs 2.4.2 performance differences
"""

from pathlib import Path

import pandas as pd


def analyze_ocio_241_vs_242():
    """Analyze the performance differences between OCIO 2.4.1 and 2.4.2."""

    # Load the data
    script_dir = Path(__file__).parent.parent
    csv_file = script_dir / "data" / "ocio_test_results.csv"
    if not csv_file.exists():
        print("❌ CSV file not found.")
        return

    df = pd.read_csv(csv_file)

    print("🔧 OCIO 2.4.1 vs 2.4.2 Performance Analysis")
    print("=" * 50)

    # Filter for just these two versions
    ocio_versions = ['2.4.1', '2.4.2']
    filtered_df = df[df['ocio_version'].isin(ocio_versions)]

    print(f"📊 Total test records: {len(filtered_df)}")
    print(f"   • OCIO 2.4.1: {len(filtered_df[filtered_df['ocio_version'] == '2.4.1'])} records")
    print(f"   • OCIO 2.4.2: {len(filtered_df[filtered_df['ocio_version'] == '2.4.2'])} records")

    # Summarize by filename and OCIO version
    summary_data = []
    for (file_name, ocio_version), group in filtered_df.groupby(['file_name', 'ocio_version']):
        metadata = group[['os_release', 'cpu_model']].iloc[0]
        summary_data.append({
            'file_name': file_name,
            'os_release': metadata['os_release'],
            'cpu_model': metadata['cpu_model'],
            'ocio_version': ocio_version,
            'mean_avg_time': group['avg_time'].mean(),
            'operation_count': len(group),
        })

    summary_df = pd.DataFrame(summary_data)

    print("\n📈 Performance by CPU and OS combination:")
    print("-" * 60)

    # Group by CPU+OS and compare versions
    comparisons = []
    for (cpu_model, os_release), group in summary_df.groupby(['cpu_model', 'os_release']):
        versions = group['ocio_version'].unique()
        if len(versions) == 2:  # Both versions present
            v241_data = group[group['ocio_version'] == '2.4.1']
            v242_data = group[group['ocio_version'] == '2.4.2']

            if len(v241_data) > 0 and len(v242_data) > 0:
                v241_time = v241_data['mean_avg_time'].iloc[0]
                v242_time = v242_data['mean_avg_time'].iloc[0]

                # Calculate percentage difference
                if v241_time != 0:
                    pct_diff = ((v242_time - v241_time) / v241_time) * 100
                else:
                    pct_diff = 0

                comparisons.append({
                    'cpu_model': cpu_model,
                    'os_release': os_release,
                    'ocio_241_time': v241_time,
                    'ocio_242_time': v242_time,
                    'pct_difference': pct_diff,
                    'faster_version': '2.4.1' if v241_time < v242_time else '2.4.2'
                })

    if comparisons:
        for comp in comparisons:
            cpu_short = comp['cpu_model'].replace('Intel(R) ', '').replace('(R) ', '').replace(' CPU', '')
            if len(cpu_short) > 30:
                cpu_short = cpu_short[:30] + "..."

            print(f"\n🖥️  {cpu_short} (OS: {comp['os_release']})")
            print(f"   📈 OCIO 2.4.1: {comp['ocio_241_time']:.1f} ms")
            print(f"   📈 OCIO 2.4.2: {comp['ocio_242_time']:.1f} ms")

            if abs(comp['pct_difference']) < 1:
                print(f"   ⚖️  Performance difference: {comp['pct_difference']:+.1f}% (virtually identical)")
            elif comp['pct_difference'] < -5:
                print(f"   🚀 Performance improvement: {comp['pct_difference']:+.1f}% (2.4.2 is faster)")
            elif comp['pct_difference'] > 5:
                print(f"   🐌 Performance regression: {comp['pct_difference']:+.1f}% (2.4.1 is faster)")
            else:
                print(f"   📊 Performance difference: {comp['pct_difference']:+.1f}% (minor difference)")
    else:
        print("❌ No CPU+OS combinations found with both OCIO versions.")

    # Overall summary
    if comparisons:
        avg_improvement = sum(comp['pct_difference'] for comp in comparisons) / len(comparisons)
        faster_242_count = sum(1 for comp in comparisons if comp['faster_version'] == '2.4.2')

        print("\n🎯 OVERALL SUMMARY:")
        print(f"   🔢 Comparisons made: {len(comparisons)}")
        print(f"   📊 Average performance change: {avg_improvement:+.1f}%")
        print(f"   🏆 OCIO 2.4.2 faster in: {faster_242_count}/{len(comparisons)} cases")
        print(f"   🏆 OCIO 2.4.1 faster in: {len(comparisons)-faster_242_count}/{len(comparisons)} cases")

        if abs(avg_improvement) < 2:
            print("   ✅ Performance is very similar between versions")
        elif avg_improvement < -5:
            print("   🚀 OCIO 2.4.2 shows meaningful improvement")
        elif avg_improvement > 5:
            print("   ⚠️  OCIO 2.4.1 performs better on average")
        else:
            print("   📊 Minor performance differences between versions")

if __name__ == "__main__":
    analyze_ocio_241_vs_242()
