"""
OCIO Chart Viewer Module

Provides a unified interface to view all generated analysis plots
with detailed descriptions and explanations for each chart type.
"""

from pathlib import Path
from typing import Any, Dict

import matplotlib.image as mpimg
import matplotlib.pyplot as plt


class OCIOChartViewer:
    """Unified viewer for all OCIO analysis charts."""

    def __init__(self, analysis_dir: Path = None):
        """
        Initialize the chart viewer.
        
        Args:
            analysis_dir: Directory containing analysis results.
                         Defaults to "analysis_results" in current directory.
        """
        self.analysis_dir = analysis_dir or Path("analysis_results")
        self.charts = {
            'comprehensive_aces_comparison.png': {
                'name': 'Comprehensive ACES Comparison',
                'description': self._get_aces_comparison_description(),
                'size': (16, 10)
            },
            'ocio_241_vs_242_cpu_os_aces_comparison.png': {
                'name': 'Merged OCIO 2.4.1 vs 2.4.2 Comparison',
                'description': self._get_merged_ocio_description(),
                'size': (20, 12)
            },
            'summary_analysis.png': {
                'name': 'Summary Analysis Overview',
                'description': self._get_summary_analysis_description(),
                'size': (15, 12)
            },
            'ocio_version_comparison.png': {
                'name': 'OCIO Version Performance Comparison',
                'description': self._get_ocio_version_description(),
                'size': (15, 10)
            }
        }

    def _get_aces_comparison_description(self) -> str:
        """Get description for ACES comparison chart."""
        return """Comprehensive ACES Version Comparison Chart
This chart shows ACES 1.0 vs ACES 2.0 performance across:
   • Overall performance
   • OS releases (r7, r9)
   • OCIO versions (2.4.0, 2.4.1, 2.4.2)
   • Top CPU models

Key features:
   • Side-by-side bars for easy comparison
   • Performance values labeled on each bar
   • Percentage differences shown above each pair
   • Summary statistics in the corner

Look for:
   • Red percentages indicate ACES 2.0 is slower
   • Green percentages indicate ACES 2.0 is faster
   • Overall performance difference in the stats box"""

    def _get_merged_ocio_description(self) -> str:
        """Get description for merged OCIO chart."""
        return """Merged OCIO 2.4.1 vs 2.4.2 Comparison Chart
This chart shows:
   • OCIO 2.4.1 vs 2.4.2 performance for both ACES versions
   • All four combinations on the same scale:
     - ACES 1.0 + OCIO 2.4.1 (blue)
     - ACES 1.0 + OCIO 2.4.2 (orange)
     - ACES 2.0 + OCIO 2.4.1 (green)
     - ACES 2.0 + OCIO 2.4.2 (red)
   • Performance values labeled on each bar
   • Percentage differences shown for OCIO version comparisons
   • Summary statistics for all combinations

Key insights:
   • Easy comparison across both ACES and OCIO versions
   • Same scale allows direct performance comparison
   • Green percentages indicate OCIO 2.4.2 is faster
   • Red percentages indicate OCIO 2.4.2 is slower"""

    def _get_summary_analysis_description(self) -> str:
        """Get description for summary analysis chart."""
        return """Summary Analysis Overview
This multi-panel chart shows:
   • Performance by OS release and ACES version
   • CPU model performance distribution
   • Performance distribution histograms
   • CPU vs OS performance heatmaps (separate for each ACES version)
   • Overall ACES version performance comparison

Key insights:
   • Comprehensive overview of all performance dimensions
   • Heatmaps reveal CPU-OS performance patterns
   • Histograms show performance distribution patterns
   • Direct ACES version comparison"""

    def _get_ocio_version_description(self) -> str:
        """Get description for OCIO version comparison chart."""
        return """OCIO Version Performance Comparison
This multi-panel chart shows:
   • Performance by OCIO version and ACES version
   • File count distributions
   • ACES version performance differences
   • Overall performance summary

Key insights:
   • Shows how different OCIO versions perform
   • Compares performance across ACES versions
   • Reveals version-specific performance patterns
   • Includes overall performance statistics"""

    def view_all_charts(self) -> None:
        """Display all available charts."""
        if not self.analysis_dir.exists():
            print("❌ Analysis results directory not found.")
            print("Please run the analysis first to generate the charts.")
            return

        available_charts = []
        for chart_file, chart_info in self.charts.items():
            chart_path = self.analysis_dir / chart_file
            if chart_path.exists():
                available_charts.append((chart_file, chart_info))

        if not available_charts:
            print("❌ No charts found in analysis_results directory.")
            print("Please run the analysis first to generate the charts.")
            return

        print(f"📊 Found {len(available_charts)} charts to display:")
        for i, (chart_file, chart_info) in enumerate(available_charts):
            print(f"  {i+1}. {chart_info['name']}")

        print("\\n" + "=" * 70)

        # Display each chart
        for chart_file, chart_info in available_charts:
            self._display_chart(chart_file, chart_info)

    def view_specific_chart(self, chart_name: str) -> None:
        """
        Display a specific chart by name.
        
        Args:
            chart_name: Name or partial name of the chart to display
        """
        if not self.analysis_dir.exists():
            print("❌ Analysis results directory not found.")
            print("Please run the analysis first to generate the charts.")
            return

        # Find chart by partial name match
        matching_charts = []
        for chart_file, chart_info in self.charts.items():
            if (chart_name.lower() in chart_file.lower() or
                chart_name.lower() in chart_info['name'].lower()):
                chart_path = self.analysis_dir / chart_file
                if chart_path.exists():
                    matching_charts.append((chart_file, chart_info))

        if not matching_charts:
            print(f"❌ Chart '{chart_name}' not found.")
            self._list_available_charts()
            return

        if len(matching_charts) > 1:
            print(f"🔍 Multiple charts found matching '{chart_name}':")
            for i, (chart_file, chart_info) in enumerate(matching_charts):
                print(f"  {i+1}. {chart_info['name']}")
            print("Please be more specific.")
            return

        chart_file, chart_info = matching_charts[0]
        self._display_chart(chart_file, chart_info)

    def _display_chart(self, chart_file: str, chart_info: Dict[str, Any]) -> None:
        """
        Display a single chart with description.
        
        Args:
            chart_file: Filename of the chart
            chart_info: Chart information dictionary
        """
        chart_path = self.analysis_dir / chart_file

        print(f"\\n{chart_info['description']}")
        print("=" * 60)

        try:
            img = mpimg.imread(chart_path)
            plt.figure(figsize=chart_info['size'])
            plt.imshow(img)
            plt.axis('off')
            plt.title(chart_info['name'], fontsize=16, fontweight='bold', pad=20)
            plt.tight_layout()
            plt.show()
        except Exception as e:
            print(f"❌ Error displaying chart: {e}")

    def _list_available_charts(self) -> None:
        """List all available charts."""
        print("\\n📋 Available charts:")
        for chart_file, chart_info in self.charts.items():
            chart_path = self.analysis_dir / chart_file
            status = "✅" if chart_path.exists() else "❌"
            print(f"  {status} {chart_info['name']}")

    def list_charts(self) -> None:
        """List all charts with their availability status."""
        print("📊 OCIO Performance Analysis Charts")
        print("=" * 50)
        self._list_available_charts()
        print("\\nTo generate missing charts, run the analysis script")
        print("To view a specific chart, use view_specific_chart(<chart_name>)")
        print("To view all charts, use view_all_charts()")
