#!/usr/bin/env python3
"""
OCIO Performance Analysis CLI

Main command-line interface for the OCIO performance analysis toolkit.
"""

import argparse
import sys
from pathlib import Path


# Add src to path for module imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ocio_performance_analysis import OCIOAnalyzer, OCIOChartViewer, OCIOTestParser


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="OCIO Performance Analysis Toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s parse            # Parse OCIO test files to CSV
  %(prog)s analyze          # Run comprehensive analysis
  %(prog)s view             # View generated charts
  %(prog)s all              # Run complete pipeline
        """
    )

    parser.add_argument(
        'command',
        choices=['parse', 'analyze', 'view', 'all'],
        help='Command to execute'
    )

    parser.add_argument(
        '--data-dir',
        default='data',
        help='Directory containing OCIO test files (default: data)'
    )

    parser.add_argument(
        '--output-dir',
        default='analysis_results',
        help='Directory for output files (default: analysis_results)'
    )

    args = parser.parse_args()

    # Set up paths
    script_dir = Path(__file__).parent.parent
    data_dir = script_dir / args.data_dir
    output_dir = script_dir / args.output_dir

    if args.command in ['parse', 'all']:
        print("🔄 Parsing OCIO test files...")
        parser = OCIOTestParser()
        test_dir = data_dir / "OCIO_tests"
        output_file = data_dir / "ocio_test_results.csv"

        if not test_dir.exists():
            print(f"❌ Test directory not found: {test_dir}")
            sys.exit(1)

        parser.parse_directory(test_dir, output_file)
        print(f"✅ Results saved to: {output_file}")

    if args.command in ['analyze', 'all']:
        print("📊 Running performance analysis...")
        analyzer = OCIOAnalyzer()
        csv_file = data_dir / "ocio_test_results.csv"

        if not csv_file.exists():
            print(f"❌ CSV file not found: {csv_file}")
            print("Run parsing first: python -m scripts.ocio_cli parse")
            sys.exit(1)

        analyzer.analyze_from_csv(csv_file, output_dir)
        print(f"✅ Analysis complete. Results in: {output_dir}")

    if args.command in ['view', 'all']:
        print("📈 Launching chart viewer...")
        viewer = OCIOChartViewer()
        viewer.view_charts(output_dir)


if __name__ == "__main__":
    main()
