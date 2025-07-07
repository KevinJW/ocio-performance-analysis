#!/usr/bin/env python3
"""
Script to view the merged OCIO 2.4.1 vs 2.4.2 comparison chart.
"""

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from pathlib import Path

def main():
    """Display the merged OCIO comparison chart."""
    script_dir = Path(__file__).parent
    chart_path = script_dir / "analysis_results" / "ocio_241_vs_242_cpu_os_aces_comparison.png"
    
    if not chart_path.exists():
        print(f"❌ Chart not found at {chart_path}")
        print("Please run ocio_analysis.py first to generate the chart.")
        return
    
    print("🎯 Displaying Merged OCIO 2.4.1 vs 2.4.2 Comparison Chart")
    print("=" * 60)
    print("📊 This chart shows:")
    print("   • OCIO 2.4.1 vs 2.4.2 performance for both ACES versions")
    print("   • All four combinations on the same scale:")
    print("     - ACES 1.0 + OCIO 2.4.1 (blue)")
    print("     - ACES 1.0 + OCIO 2.4.2 (orange)")
    print("     - ACES 2.0 + OCIO 2.4.1 (green)")
    print("     - ACES 2.0 + OCIO 2.4.2 (red)")
    print("   • Performance values labeled on each bar")
    print("   • Percentage differences shown for OCIO version comparisons")
    print("   • Summary statistics for all combinations")
    print("💡 Key insights:")
    print("   • Easy comparison across both ACES and OCIO versions")
    print("   • Same scale allows direct performance comparison")
    print("   • Green percentages indicate OCIO 2.4.2 is faster")
    print("   • Red percentages indicate OCIO 2.4.2 is slower")
    
    # Display the chart
    try:
        img = mpimg.imread(chart_path)
        plt.figure(figsize=(20, 12))
        plt.imshow(img)
        plt.axis('off')
        plt.title('Merged OCIO 2.4.1 vs 2.4.2 Performance Comparison\n(Both ACES Versions on Same Scale)', 
                 fontsize=16, fontweight='bold', pad=20)
        plt.tight_layout()
        plt.show()
    except Exception as e:
        print(f"❌ Error displaying chart: {e}")

if __name__ == "__main__":
    main()
