#!/usr/bin/env python3
"""
OCIO Test Results Parser CLI Script

Command-line interface for parsing OCIO test result files.
"""

import sys
from pathlib import Path


# Add src to path for module imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ocio_performance_analysis import OCIOTestParser


def main():
    """Main function to run the parser."""
    # Set up paths
    script_dir = Path(__file__).parent.parent
    test_dir = script_dir / "data" / "OCIO_tests"
    output_file = script_dir / "data" / "ocio_test_results.csv"

    print("🔍 OCIO Test Results Parser")
    print("=" * 40)

    if not test_dir.exists():
        print(f"❌ Test directory not found: {test_dir}")
        print("Please ensure the OCIO_tests directory exists in data/")
        return 1

    # Create parser and process files
    parser = OCIOTestParser()

    print(f"📁 Parsing files from: {test_dir}")
    print(f"💾 Output file: {output_file}")

    try:
        # Parse all files in the test directory
        results = parser.parse_directory(test_dir)

        if not results:
            print("❌ No test results found")
            return 1

        # Save to CSV
        parser.save_to_csv(results, output_file)

        print(f"✅ Successfully parsed {len(results)} test results")
        print(f"📊 Results saved to: {output_file}")

        return 0

    except Exception as e:
        print(f"❌ Error during parsing: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
