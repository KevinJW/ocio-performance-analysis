"""
View the Comprehensive ACES Comparison Chart

This script opens the new comprehensive ACES 1.0 vs 2.0 comparison chart
that shows all data on a single bar chart.
"""

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from pathlib import Path

def view_comprehensive_aces_chart():
    """Display the comprehensive ACES comparison chart."""
    
    # Path to the chart
    chart_path = Path("analysis_results") / "comprehensive_aces_comparison.png"
    
    if not chart_path.exists():
        print(f"❌ Chart not found: {chart_path}")
        print("Please run the analysis first with: python ocio_analysis.py")
        return
    
    # Load and display the image
    img = mpimg.imread(chart_path)
    
    plt.figure(figsize=(16, 10))
    plt.imshow(img)
    plt.axis('off')
    plt.title('Comprehensive ACES Version Comparison Chart', 
              fontsize=16, fontweight='bold', pad=20)
    
    print("🎯 Displaying Comprehensive ACES Comparison Chart")
    print("=" * 50)
    print("📊 This chart shows ACES 1.0 vs ACES 2.0 performance across:")
    print("   • Overall performance")
    print("   • OS releases (r7, r9)")
    print("   • OCIO versions (2.4.0, 2.4.1, 2.4.2)")
    print("   • Top CPU models")
    print("\n💡 Key features:")
    print("   • Side-by-side bars for easy comparison")
    print("   • Performance values labeled on each bar")
    print("   • Percentage differences shown above each pair")
    print("   • Summary statistics in the corner")
    print("\n🔍 Look for:")
    print("   • Red percentages indicate ACES 2.0 is slower")
    print("   • Green percentages indicate ACES 2.0 is faster")
    print("   • Overall performance difference in the stats box")
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    view_comprehensive_aces_chart()
