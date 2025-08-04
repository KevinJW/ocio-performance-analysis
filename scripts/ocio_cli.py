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

from ocio_performance_analysis import (
    OCIOAnalyzer, 
    OCIOChartViewer, 
    OCIOTestParser, 
    setup_logging, 
    get_logger,
    FileNotFoundError as OCIOFileNotFoundError,
    ParseError,
    AnalysisError,
)


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

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging output'
    )

    args = parser.parse_args()

    # Set up logging
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(level=log_level)
    logger = get_logger(__name__)

    # Set up paths
    script_dir = Path(__file__).parent.parent
    data_dir = script_dir / args.data_dir
    output_dir = script_dir / args.output_dir

    if args.command in ['parse', 'all']:
        logger.info("🔄 Parsing OCIO test files...")
        try:
            parser = OCIOTestParser()
            test_dir = data_dir / "OCIO_tests"
            output_file = data_dir / "ocio_test_results.csv"

            results = parser.parse_directory(test_dir)
            parser.save_to_csv(results, output_file)
            logger.info(f"✅ Results saved to: {output_file}")
            
        except OCIOFileNotFoundError as e:
            logger.error(f"❌ {e}")
            sys.exit(1)
        except ParseError as e:
            logger.error(f"❌ Parsing failed: {e}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"❌ Unexpected error during parsing: {e}")
            sys.exit(1)

    if args.command in ['analyze', 'all']:
        logger.info("📊 Running performance analysis...")
        try:
            csv_file = data_dir / "ocio_test_results.csv"

            if not csv_file.exists():
                logger.error(f"❌ CSV file not found: {csv_file}")
                logger.info("Run parsing first: python -m scripts.ocio_cli parse")
                sys.exit(1)

            analyzer = OCIOAnalyzer(csv_file)
            analyzer.run_full_analysis(output_dir)
            logger.info(f"✅ Analysis complete. Results in: {output_dir}")
            
        except AnalysisError as e:
            logger.error(f"❌ Analysis failed: {e}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"❌ Unexpected error during analysis: {e}")
            sys.exit(1)

    if args.command in ['view', 'all']:
        logger.info("📈 Launching chart viewer...")
        try:
            viewer = OCIOChartViewer(output_dir)
            viewer.view_all_charts()
        except Exception as e:
            logger.error(f"❌ Error viewing charts: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
