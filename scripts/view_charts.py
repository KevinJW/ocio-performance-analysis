#!/usr/bin/env python3
"""
OCIO Chart Viewer CLI Script

Command-line interface for viewing analysis charts.
"""

import sys
from pathlib import Path


# Add src to path for module imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ocio_performance_analysis import OCIOChartViewer


def main():
    """Main function with command line interface."""
    script_dir = Path(__file__).parent.parent
    analysis_dir = script_dir / "analysis_results"

    viewer = OCIOChartViewer(analysis_dir)

    if len(sys.argv) == 1:
        # No arguments - show all charts
        viewer.view_all_charts()
    elif len(sys.argv) == 2:
        arg = sys.argv[1].lower()
        if arg in ['--help', '-h', 'help']:
            print("📊 OCIO Chart Viewer - Usage:")
            print("  python scripts/view_charts.py                    # View all charts")
            print("  python scripts/view_charts.py <chart_name>       # View specific chart")
            print("  python scripts/view_charts.py --list             # List available charts")
            print("  python scripts/view_charts.py --help             # Show this help")
            print("\\nChart names (partial matching supported):")
            print("  'aces' or 'comprehensive'  - ACES comparison chart")
            print("  'ocio' or 'merged'          - OCIO version comparison chart")
            print("  'summary'                   - Summary analysis overview")
            print("  'version'                   - OCIO version comparison")
        elif arg in ['--list', '-l', 'list']:
            viewer.list_charts()
        else:
            # View specific chart
            viewer.view_specific_chart(sys.argv[1])
    else:
        print("❌ Too many arguments. Use --help for usage information.")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
