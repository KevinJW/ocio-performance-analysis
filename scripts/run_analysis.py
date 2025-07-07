#!/usr/bin/env python3
"""
OCIO Performance Analysis CLI Script

Command-line interface for running comprehensive performance analysis.
"""

import sys
from pathlib import Path


# Add src to path for module imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ocio_performance_analysis import OCIOAnalyzer


def main():
    """Main function to run the analysis."""
    # Set up paths
    script_dir = Path(__file__).parent.parent
    csv_file = script_dir / "data" / "ocio_test_results.csv"
    output_dir = script_dir / "analysis_results"

    print("📊 OCIO Performance Analysis")
    print("=" * 40)

    if not csv_file.exists():
        print(f"❌ CSV file not found: {csv_file}")
        print("Please run parse_ocio_results.py first to generate the CSV file")
        return 1

    # Create analyzer and run analysis
    analyzer = OCIOAnalyzer(csv_file)

    print(f"📁 Input file: {csv_file}")
    print(f"📁 Output directory: {output_dir}")

    try:
        print("🔄 Running full analysis...")
        analyzer.run_full_analysis(output_dir)

        print("✅ Analysis complete!")
        print(f"📊 Results saved to: {output_dir}")
        print("\\n🎯 To view results:")
        print("   python scripts/view_charts.py")

        return 0

    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
