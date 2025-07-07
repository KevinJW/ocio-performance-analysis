"""
OCIO Test Results Analysis Script

This script analyzes OCIO test results CSV data to:
1. Summarize test runs by filename using mean averages
2. Find cases where CPU is same but OS release differs
3. Create visualizations comparing OS performance effects
"""

import logging
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up matplotlib for better plots
plt.style.use("seaborn-v0_8")
sns.set_palette("husl")


class OCIOAnalyzer:
    """Analyzer for OCIO test results data."""

    def __init__(self, csv_file: Path):
        """
        Initialize the analyzer with CSV data.

        Args:
            csv_file: Path to the CSV file containing test results
        """
        self.csv_file = csv_file
        self.df = None
        self.summary_df = None
        self.comparison_data = None

    def load_data(self) -> pd.DataFrame:
        """Load CSV data into DataFrame and add ACES version categorization."""
        try:
            self.df = pd.read_csv(self.csv_file)

            # Add ACES version categorization
            self.df["aces_version"] = self.df["target_colorspace"].apply(
                self._categorize_aces_version
            )

            logger.info(f"Loaded {len(self.df)} records from {self.csv_file}")
            logger.info(
                f"ACES version distribution: {self.df['aces_version'].value_counts().to_dict()}"
            )
            return self.df
        except Exception as e:
            logger.error(f"Error loading CSV file: {e}")
            raise

    def _categorize_aces_version(self, target_colorspace: str) -> str:
        """
        Categorize the ACES version based on target colorspace.

        Args:
            target_colorspace: The target colorspace string

        Returns:
            ACES version category ('ACES 1.0', 'ACES 2.0', or 'Other')
        """
        if "ACES 1.0" in target_colorspace:
            return "ACES 1.0"
        elif "ACES 2.0" in target_colorspace:
            return "ACES 2.0"
        else:
            return "Other"

    def summarize_by_filename(self) -> pd.DataFrame:
        """
        Summarize test runs by filename, OCIO version, and ACES version using mean averages for numerical columns.

        Returns:
            DataFrame with summarized data grouped by filename, OCIO version, and ACES version
        """
        if self.df is None:
            raise ValueError("Data not loaded. Call load_data() first.")

        # Group by filename, OCIO version, AND ACES version to capture all combinations
        summary_data = []

        for (file_name, ocio_version, aces_version), group in self.df.groupby(
            ["file_name", "ocio_version", "aces_version"]
        ):
            # Get the common metadata (should be same for all rows from same file+version+aces)
            metadata = group[["os_release", "cpu_model", "config_version"]].iloc[0]

            # Calculate statistics
            stats = {
                "file_name": file_name,
                "os_release": metadata["os_release"],
                "cpu_model": metadata["cpu_model"],
                "ocio_version": ocio_version,  # Use the version from groupby
                "aces_version": aces_version,  # Use the ACES version from groupby
                "config_version": metadata["config_version"],
                "total_operations": len(group),
                "unique_operations": group["operation"].nunique(),
                "mean_min_time": group["min_time"].mean(),
                "mean_max_time": group["max_time"].mean(),
                "mean_avg_time": group["avg_time"].mean(),
                "std_avg_time": group["avg_time"].std(),
                "median_avg_time": group["avg_time"].median(),
                "total_iterations": group["iteration_count"].sum(),
                "mean_iterations": group["iteration_count"].mean(),
            }

            # Add operation-specific breakdown
            operation_stats = group.groupby("operation")["avg_time"].agg(
                ["mean", "std", "count"]
            )
            for op, data in operation_stats.iterrows():
                stats[f"{op}_mean_time"] = data["mean"]
                stats[f"{op}_std_time"] = data["std"] if not pd.isna(data["std"]) else 0
                stats[f"{op}_count"] = data["count"]

            summary_data.append(stats)

        self.summary_df = pd.DataFrame(summary_data)
        logger.info(f"Created summary with {len(self.summary_df)} file summaries")
        return self.summary_df

    def find_cpu_os_comparisons(self) -> pd.DataFrame:
        """
        Find cases where CPU is the same but OS release differs, split by ACES version.

        Returns:
            DataFrame with comparison data
        """
        if self.summary_df is None:
            raise ValueError(
                "Summary data not available. Call summarize_by_filename() first."
            )

        # Group by CPU model and ACES version, then find cases with multiple OS releases
        comparison_data = []

        for (cpu_model, aces_version), group in self.summary_df.groupby(
            ["cpu_model", "aces_version"]
        ):
            if cpu_model == "Unknown":
                continue

            os_releases = group["os_release"].unique()
            if len(os_releases) > 1:
                logger.info(
                    f"Found CPU '{cpu_model}' with ACES {aces_version} having OS releases: {os_releases}"
                )

                # Create comparison records
                for os_release in os_releases:
                    os_data = group[group["os_release"] == os_release]

                    comparison_data.extend(
                        [
                            {
                                "cpu_model": cpu_model,
                                "aces_version": aces_version,
                                "os_release": os_release,
                                "file_count": len(os_data),
                                "mean_avg_time": os_data["mean_avg_time"].mean(),
                                "std_avg_time": os_data["mean_avg_time"].std(),
                                "median_avg_time": os_data["median_avg_time"].mean(),
                                "total_operations": os_data["total_operations"].sum(),
                                "files": list(os_data["file_name"]),
                            }
                        ]
                    )

        self.comparison_data = pd.DataFrame(comparison_data)
        logger.info(
            f"Found {len(self.comparison_data)} CPU-OS-ACES combinations for comparison"
        )
        return self.comparison_data

    def find_ocio_version_comparisons(self) -> pd.DataFrame:
        """
        Find cases where the same CPU, OS, and ACES version combination has multiple OCIO versions.

        Returns:
            DataFrame with OCIO version comparison data
        """
        if self.summary_df is None:
            raise ValueError(
                "Summary data not available. Call summarize_by_filename() first."
            )

        # Group by CPU model, OS release, and ACES version to find multiple OCIO versions
        ocio_comparison_data = []

        for (cpu_model, os_release, aces_version), group in self.summary_df.groupby(
            ["cpu_model", "os_release", "aces_version"]
        ):
            if cpu_model == "Unknown":
                continue

            ocio_versions = group["ocio_version"].unique()
            if len(ocio_versions) > 1:
                logger.info(
                    f"Found CPU '{cpu_model}' on OS '{os_release}' with ACES {aces_version} having OCIO versions: {ocio_versions}"
                )

                # Create comparison records for each OCIO version
                for ocio_version in ocio_versions:
                    version_data = group[group["ocio_version"] == ocio_version]

                    ocio_comparison_data.extend(
                        [
                            {
                                "cpu_model": cpu_model,
                                "os_release": os_release,
                                "aces_version": aces_version,
                                "ocio_version": ocio_version,
                                "file_count": len(version_data),
                                "mean_avg_time": version_data["mean_avg_time"].mean(),
                                "std_avg_time": version_data["mean_avg_time"].std(),
                                "median_avg_time": version_data[
                                    "median_avg_time"
                                ].mean(),
                                "total_operations": version_data[
                                    "total_operations"
                                ].sum(),
                                "files": list(version_data["file_name"]),
                            }
                        ]
                    )

        self.ocio_comparison_data = pd.DataFrame(ocio_comparison_data)
        logger.info(
            f"Found {len(self.ocio_comparison_data)} CPU-OS-ACES-OCIO combinations for comparison"
        )
        return self.ocio_comparison_data

    def find_all_ocio_version_comparisons(self) -> pd.DataFrame:
        """
        Find all cases where different OCIO versions can be compared, split by ACES version.

        Returns:
            DataFrame with all OCIO version comparison data
        """
        if self.summary_df is None:
            raise ValueError(
                "Summary data not available. Call summarize_by_filename() first."
            )

        # Group by OCIO version and ACES version to calculate overall statistics
        all_ocio_comparison_data = []

        for (ocio_version, aces_version), group in self.summary_df.groupby(
            ["ocio_version", "aces_version"]
        ):
            all_ocio_comparison_data.append(
                {
                    "ocio_version": ocio_version,
                    "aces_version": aces_version,
                    "file_count": len(group),
                    "mean_avg_time": group["mean_avg_time"].mean(),
                    "std_avg_time": group["mean_avg_time"].std(),
                    "median_avg_time": group["median_avg_time"].mean(),
                    "total_operations": group["total_operations"].sum(),
                    "cpu_models": list(group["cpu_model"].unique()),
                    "os_releases": list(group["os_release"].unique()),
                }
            )

        self.all_ocio_comparison_data = pd.DataFrame(all_ocio_comparison_data)
        logger.info(
            f"Found {len(self.all_ocio_comparison_data)} OCIO version-ACES combinations for overall comparison"
        )
        return self.all_ocio_comparison_data

    def create_summary_plots(self, output_dir: Path) -> None:
        """
        Create summary visualization plots with ACES version information.

        Args:
            output_dir: Directory to save plots
        """
        output_dir.mkdir(exist_ok=True)

        if self.summary_df is None:
            raise ValueError(
                "Summary data not available. Call summarize_by_filename() first."
            )

        # Plot 1: Average execution time by OS release and ACES version
        plt.figure(figsize=(15, 12))

        plt.subplot(2, 3, 1)
        # Group by OS release and ACES version
        os_aces_perf = self.summary_df.groupby(["os_release", "aces_version"])[
            "mean_avg_time"
        ].agg(["mean", "std"])
        os_aces_perf = os_aces_perf.reset_index()

        # Create grouped bar chart
        aces_1_data = os_aces_perf[os_aces_perf["aces_version"] == "ACES 1.0"]
        aces_2_data = os_aces_perf[os_aces_perf["aces_version"] == "ACES 2.0"]

        os_releases = sorted(self.summary_df["os_release"].unique())
        x = range(len(os_releases))
        width = 0.35

        # Get data for each OS release
        aces_1_means = []
        aces_2_means = []
        aces_1_stds = []
        aces_2_stds = []

        for os_rel in os_releases:
            aces_1_row = aces_1_data[aces_1_data["os_release"] == os_rel]
            aces_2_row = aces_2_data[aces_2_data["os_release"] == os_rel]

            aces_1_means.append(
                aces_1_row["mean"].iloc[0] if len(aces_1_row) > 0 else 0
            )
            aces_2_means.append(
                aces_2_row["mean"].iloc[0] if len(aces_2_row) > 0 else 0
            )
            aces_1_stds.append(aces_1_row["std"].iloc[0] if len(aces_1_row) > 0 else 0)
            aces_2_stds.append(aces_2_row["std"].iloc[0] if len(aces_2_row) > 0 else 0)

        plt.bar(
            [i - width / 2 for i in x],
            aces_1_means,
            width,
            yerr=aces_1_stds,
            capsize=3,
            alpha=0.7,
            label="ACES 1.0",
        )
        plt.bar(
            [i + width / 2 for i in x],
            aces_2_means,
            width,
            yerr=aces_2_stds,
            capsize=3,
            alpha=0.7,
            label="ACES 2.0",
        )
        plt.title("Average Execution Time by OS Release and ACES Version")
        plt.xlabel("OS Release")
        plt.ylabel("Mean Average Time (ms)")
        plt.xticks(x, os_releases)
        plt.legend()
        plt.grid(True, alpha=0.3)

        # Plot 2: CPU model performance distribution
        plt.subplot(2, 3, 2)
        cpu_data = self.summary_df[self.summary_df["cpu_model"] != "Unknown"]
        if len(cpu_data) > 0:
            cpu_aces_perf = (
                cpu_data.groupby(["cpu_model", "aces_version"])["mean_avg_time"]
                .mean()
                .unstack(fill_value=0)
            )
            cpu_aces_perf.plot(kind="barh", ax=plt.gca(), alpha=0.7)
            plt.title("Average Performance by CPU Model and ACES Version")
            plt.xlabel("Mean Average Time (ms)")
            plt.ylabel("CPU Model")

        # Plot 3: Performance distribution histogram by ACES version
        plt.subplot(2, 3, 3)
        aces_1_times = self.summary_df[self.summary_df["aces_version"] == "ACES 1.0"][
            "mean_avg_time"
        ]
        aces_2_times = self.summary_df[self.summary_df["aces_version"] == "ACES 2.0"][
            "mean_avg_time"
        ]

        plt.hist(aces_1_times, bins=15, alpha=0.7, label="ACES 1.0", edgecolor="black")
        plt.hist(aces_2_times, bins=15, alpha=0.7, label="ACES 2.0", edgecolor="black")
        plt.title("Distribution of Average Execution Times")
        plt.xlabel("Mean Average Time (ms)")
        plt.ylabel("Frequency")
        plt.legend()

        # Plot 4: OS vs CPU heatmap for ACES 1.0
        plt.subplot(2, 3, 4)
        aces_1_data = self.summary_df[
            (self.summary_df["cpu_model"] != "Unknown")
            & (self.summary_df["aces_version"] == "ACES 1.0")
        ]
        if len(aces_1_data) > 0:
            pivot_data = aces_1_data.pivot_table(
                values="mean_avg_time",
                index="cpu_model",
                columns="os_release",
                aggfunc="mean",
            )
            sns.heatmap(
                pivot_data,
                annot=True,
                fmt=".1f",
                cmap="viridis",
                cbar_kws={"label": "ms"},
            )
            plt.title("Performance Heatmap: CPU vs OS (ACES 1.0)")
            plt.xlabel("OS Release")
            plt.ylabel("CPU Model")

        # Plot 5: OS vs CPU heatmap for ACES 2.0
        plt.subplot(2, 3, 5)
        aces_2_data = self.summary_df[
            (self.summary_df["cpu_model"] != "Unknown")
            & (self.summary_df["aces_version"] == "ACES 2.0")
        ]
        if len(aces_2_data) > 0:
            pivot_data = aces_2_data.pivot_table(
                values="mean_avg_time",
                index="cpu_model",
                columns="os_release",
                aggfunc="mean",
            )
            sns.heatmap(
                pivot_data,
                annot=True,
                fmt=".1f",
                cmap="viridis",
                cbar_kws={"label": "ms"},
            )
            plt.title("Performance Heatmap: CPU vs OS (ACES 2.0)")
            plt.xlabel("OS Release")
            plt.ylabel("CPU Model")

        # Plot 6: ACES version comparison summary
        plt.subplot(2, 3, 6)
        overall_aces_1 = self.summary_df[self.summary_df["aces_version"] == "ACES 1.0"][
            "mean_avg_time"
        ].mean()
        overall_aces_2 = self.summary_df[self.summary_df["aces_version"] == "ACES 2.0"][
            "mean_avg_time"
        ].mean()

        bars = plt.bar(
            ["ACES 1.0", "ACES 2.0"],
            [overall_aces_1, overall_aces_2],
            color=["#2E86AB", "#A23B72"],
            alpha=0.7,
        )
        plt.title("Overall ACES Version Performance")
        plt.ylabel("Mean Average Time (ms)")
        plt.grid(True, alpha=0.3)

        # Add value labels
        for bar, value in zip(bars, [overall_aces_1, overall_aces_2]):
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.5,
                f"{value:.1f}ms",
                ha="center",
                va="bottom",
                fontsize=10,
            )

        # Add difference annotation
        diff_pct = (
            ((overall_aces_2 - overall_aces_1) / overall_aces_1) * 100
            if overall_aces_1 > 0
            else 0
        )
        plt.annotate(
            f"Difference: {diff_pct:+.1f}%",
            xy=(0.5, max(overall_aces_1, overall_aces_2) * 1.1),
            xycoords="data",
            ha="center",
            va="bottom",
            fontsize=9,
            color="red" if diff_pct > 0 else "green",
            fontweight="bold",
        )

        plt.tight_layout()
        plt.savefig(output_dir / "summary_analysis.png", dpi=300, bbox_inches="tight")
        plt.close()

        logger.info(f"Summary plots saved to {output_dir / 'summary_analysis.png'}")

    def create_os_comparison_plots(self, output_dir: Path) -> None:
        """
        Create OS comparison plots for same CPU models, split by ACES version.

        Args:
            output_dir: Directory to save plots
        """
        output_dir.mkdir(exist_ok=True)

        if self.comparison_data is None:
            raise ValueError(
                "Comparison data not available. Call find_cpu_os_comparisons() first."
            )

        # Get unique CPU models that have multiple OS releases
        cpu_models = self.comparison_data["cpu_model"].unique()

        for cpu_model in cpu_models:
            cpu_data = self.comparison_data[
                self.comparison_data["cpu_model"] == cpu_model
            ]

            if len(cpu_data) < 2:
                continue

            # Check if we have both ACES versions
            aces_versions = cpu_data["aces_version"].unique()

            # Create comparison plot for this CPU
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle(
                f"OS Performance Comparison by ACES Version\n{cpu_model}",
                fontsize=14,
                fontweight="bold",
            )

            # Plot 1: Bar chart of mean performance by ACES version
            ax1 = axes[0, 0]

            # Create grouped bar chart
            aces_1_data = cpu_data[cpu_data["aces_version"] == "ACES 1.0"]
            aces_2_data = cpu_data[cpu_data["aces_version"] == "ACES 2.0"]

            width = 0.35
            os_releases = sorted(cpu_data["os_release"].unique())
            x = range(len(os_releases))

            # Get data for each OS release for both ACES versions
            aces_1_times = []
            aces_2_times = []
            aces_1_stds = []
            aces_2_stds = []

            for os_rel in os_releases:
                aces_1_os = aces_1_data[aces_1_data["os_release"] == os_rel]
                aces_2_os = aces_2_data[aces_2_data["os_release"] == os_rel]

                aces_1_times.append(
                    aces_1_os["mean_avg_time"].mean() if len(aces_1_os) > 0 else 0
                )
                aces_2_times.append(
                    aces_2_os["mean_avg_time"].mean() if len(aces_2_os) > 0 else 0
                )
                aces_1_stds.append(
                    aces_1_os["std_avg_time"].mean() if len(aces_1_os) > 0 else 0
                )
                aces_2_stds.append(
                    aces_2_os["std_avg_time"].mean() if len(aces_2_os) > 0 else 0
                )

            # Create bars
            bars1 = ax1.bar(
                [i - width / 2 for i in x],
                aces_1_times,
                width,
                yerr=aces_1_stds,
                capsize=5,
                alpha=0.7,
                label="ACES 1.0",
            )
            bars2 = ax1.bar(
                [i + width / 2 for i in x],
                aces_2_times,
                width,
                yerr=aces_2_stds,
                capsize=5,
                alpha=0.7,
                label="ACES 2.0",
            )

            ax1.set_title("Mean Average Execution Time by ACES Version")
            ax1.set_xlabel("OS Release")
            ax1.set_ylabel("Mean Average Time (ms)")
            ax1.set_xticks(x)
            ax1.set_xticklabels(os_releases)
            ax1.legend()
            ax1.grid(True, alpha=0.3)

            # Add value labels on bars
            for bar, value in zip(bars1, aces_1_times):
                if value > 0:
                    ax1.text(
                        bar.get_x() + bar.get_width() / 2,
                        bar.get_height() + 0.01,
                        f"{value:.1f}",
                        ha="center",
                        va="bottom",
                        fontsize=9,
                    )

            for bar, value in zip(bars2, aces_2_times):
                if value > 0:
                    ax1.text(
                        bar.get_x() + bar.get_width() / 2,
                        bar.get_height() + 0.01,
                        f"{value:.1f}",
                        ha="center",
                        va="bottom",
                        fontsize=9,
                    )

            # Plot 2: File count comparison by ACES version
            ax2 = axes[0, 1]

            # Get file counts for each OS release for both ACES versions
            aces_1_files = []
            aces_2_files = []

            for os_rel in os_releases:
                aces_1_os = aces_1_data[aces_1_data["os_release"] == os_rel]
                aces_2_os = aces_2_data[aces_2_data["os_release"] == os_rel]

                aces_1_files.append(
                    aces_1_os["file_count"].sum() if len(aces_1_os) > 0 else 0
                )
                aces_2_files.append(
                    aces_2_os["file_count"].sum() if len(aces_2_os) > 0 else 0
                )

            ax2.bar(
                [i - width / 2 for i in x],
                aces_1_files,
                width,
                alpha=0.7,
                label="ACES 1.0",
            )
            ax2.bar(
                [i + width / 2 for i in x],
                aces_2_files,
                width,
                alpha=0.7,
                label="ACES 2.0",
            )

            ax2.set_title("Number of Test Files by ACES Version")
            ax2.set_xlabel("OS Release")
            ax2.set_ylabel("File Count")
            ax2.set_xticks(x)
            ax2.set_xticklabels(os_releases)
            ax2.legend()
            ax2.grid(True, alpha=0.3)

            # Plot 3: ACES version comparison for each OS
            ax3 = axes[1, 0]

            # Calculate ACES 1.0 vs 2.0 performance differences
            aces_diff_pct = []
            for i, os_rel in enumerate(os_releases):
                if aces_1_times[i] > 0 and aces_2_times[i] > 0:
                    diff_pct = (
                        (aces_2_times[i] - aces_1_times[i]) / aces_1_times[i]
                    ) * 100
                    aces_diff_pct.append(diff_pct)
                else:
                    aces_diff_pct.append(0)

            colors = ["green" if x < 0 else "red" for x in aces_diff_pct]
            bars5 = ax3.bar(os_releases, aces_diff_pct, color=colors, alpha=0.7)
            ax3.set_title("ACES 2.0 vs ACES 1.0 Performance Difference")
            ax3.set_xlabel("OS Release")
            ax3.set_ylabel("Performance Difference (%)")
            ax3.grid(True, alpha=0.3)
            ax3.axhline(y=0, color="black", linestyle="-", alpha=0.5)

            # Add value labels
            for bar, value in zip(bars5, aces_diff_pct):
                if value != 0:
                    ax3.text(
                        bar.get_x() + bar.get_width() / 2,
                        bar.get_height() + (1 if value > 0 else -1),
                        f"{value:.1f}%",
                        ha="center",
                        va="bottom" if value > 0 else "top",
                        fontsize=9,
                    )

            # Plot 4: Summary statistics
            ax4 = axes[1, 1]
            ax4.axis("off")

            # Create summary text
            summary_text = f"CPU: {cpu_model}\n\n"
            summary_text += "OS Releases Found:\n"
            for os_rel in os_releases:
                summary_text += f"  • {os_rel}\n"

            summary_text += "\nACES Versions:\n"
            for aces_ver in aces_versions:
                aces_data = cpu_data[cpu_data["aces_version"] == aces_ver]
                avg_time = aces_data["mean_avg_time"].mean()
                summary_text += f"  • {aces_ver}: {avg_time:.1f}ms avg\n"

            ax4.text(
                0.1,
                0.9,
                summary_text,
                transform=ax4.transAxes,
                fontsize=10,
                verticalalignment="top",
                fontfamily="monospace",
            )

            plt.tight_layout()

            # Save plot with sanitized CPU model name
            safe_cpu_name = (
                cpu_model.replace("(", "")
                .replace(")", "")
                .replace(" ", "_")
                .replace("@", "at")
            )
            plt.savefig(
                output_dir / f"os_comparison_{safe_cpu_name}.png",
                dpi=300,
                bbox_inches="tight",
            )
            plt.close()

            logger.info(f"OS comparison plot saved for {cpu_model}")

    def create_detailed_comparison_report(self, output_dir: Path) -> None:
        """
        Create a detailed comparison report with ACES version information.

        Args:
            output_dir: Directory to save the report
        """
        output_dir.mkdir(exist_ok=True)

        if self.comparison_data is None:
            raise ValueError(
                "Comparison data not available. Call find_cpu_os_comparisons() first."
            )

        report_file = output_dir / "os_comparison_report.txt"

        with open(report_file, "w") as f:
            f.write(
                "OCIO Test Results - OS Performance Comparison Report (by ACES Version)\n"
            )
            f.write("=" * 80 + "\n\n")

            # Summary statistics
            f.write("SUMMARY STATISTICS\n")
            f.write("-" * 20 + "\n")
            f.write(f"Total file summaries analyzed: {len(self.summary_df)}\n")
            f.write(f"Unique CPU models: {self.summary_df['cpu_model'].nunique()}\n")
            f.write(
                f"OS releases found: {list(self.summary_df['os_release'].unique())}\n"
            )
            f.write(
                f"ACES versions found: {list(self.summary_df['aces_version'].unique())}\n"
            )
            f.write(
                f"CPU models with multiple OS releases: {len(self.comparison_data['cpu_model'].unique())}\n\n"
            )

            # Overall ACES version performance
            f.write("OVERALL ACES VERSION PERFORMANCE\n")
            f.write("-" * 35 + "\n")
            for aces_version in sorted(self.summary_df["aces_version"].unique()):
                aces_data = self.summary_df[
                    self.summary_df["aces_version"] == aces_version
                ]
                avg_time = aces_data["mean_avg_time"].mean()
                std_time = aces_data["mean_avg_time"].std()
                f.write(f"{aces_version}: {avg_time:.2f} ± {std_time:.2f} ms\n")

            # ACES version comparison
            aces_1_avg = self.summary_df[self.summary_df["aces_version"] == "ACES 1.0"][
                "mean_avg_time"
            ].mean()
            aces_2_avg = self.summary_df[self.summary_df["aces_version"] == "ACES 2.0"][
                "mean_avg_time"
            ].mean()
            if aces_1_avg > 0:
                aces_diff_pct = ((aces_2_avg - aces_1_avg) / aces_1_avg) * 100
                f.write(f"ACES 2.0 vs ACES 1.0 difference: {aces_diff_pct:+.1f}%\n")
                f.write(
                    f"Better performing ACES version: {'ACES 1.0' if aces_1_avg < aces_2_avg else 'ACES 2.0'}\n\n"
                )

            # Detailed comparisons by CPU and ACES version
            f.write("DETAILED OS COMPARISONS BY CPU MODEL AND ACES VERSION\n")
            f.write("-" * 55 + "\n")

            for cpu_model in sorted(self.comparison_data["cpu_model"].unique()):
                cpu_data = self.comparison_data[
                    self.comparison_data["cpu_model"] == cpu_model
                ]

                f.write(f"\nCPU Model: {cpu_model}\n")
                f.write("=" * (len(cpu_model) + 12) + "\n")

                # Group by ACES version
                for aces_version in sorted(cpu_data["aces_version"].unique()):
                    aces_cpu_data = cpu_data[cpu_data["aces_version"] == aces_version]

                    f.write(f"\n  {aces_version}:\n")
                    f.write(f"  {'-' * (len(aces_version) + 2)}\n")

                    for _, row in aces_cpu_data.iterrows():
                        f.write(f"    OS Release: {row['os_release']}\n")
                        f.write(f"      Files: {row['file_count']}\n")
                        f.write(f"      Mean avg time: {row['mean_avg_time']:.3f} ms\n")
                        f.write(f"      Std dev: {row['std_avg_time']:.3f} ms\n")
                        f.write(f"      Total operations: {row['total_operations']}\n")
                        f.write(f"      Test files: {', '.join(row['files'])}\n\n")

                    # Performance comparison if exactly 2 OS releases for this ACES version
                    if len(aces_cpu_data) == 2:
                        os1, os2 = aces_cpu_data["os_release"].tolist()
                        time1, time2 = aces_cpu_data["mean_avg_time"].tolist()

                        if time1 != 0:
                            pct_change = ((time2 - time1) / time1) * 100
                            better_os = os1 if time1 < time2 else os2
                            f.write(f"    Performance Analysis ({aces_version}):\n")
                            f.write(f"      {os1}: {time1:.3f} ms\n")
                            f.write(f"      {os2}: {time2:.3f} ms\n")
                            f.write(f"      Change: {pct_change:.1f}%\n")
                            f.write(f"      Better performing OS: {better_os}\n\n")

                f.write("\n" + "-" * 60 + "\n")

        logger.info(f"Detailed comparison report saved to {report_file}")

    def create_ocio_version_plots(self, output_dir: Path) -> None:
        """
        Create OCIO version comparison plots split by ACES version.

        Args:
            output_dir: Directory to save plots
        """
        output_dir.mkdir(exist_ok=True)

        if (
            not hasattr(self, "all_ocio_comparison_data")
            or self.all_ocio_comparison_data is None
        ):
            logger.warning("No OCIO version comparison data available")
            return

        # Create OCIO version comparison plot
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(
            "OCIO Version Performance Comparison by ACES Version",
            fontsize=14,
            fontweight="bold",
        )

        # Plot 1: Overall performance by OCIO version and ACES version
        ax1 = axes[0, 0]

        # Create grouped bar chart
        ocio_versions = sorted(self.all_ocio_comparison_data["ocio_version"].unique())

        width = 0.35
        x = range(len(ocio_versions))

        # Get data for each OCIO version for both ACES versions
        aces_1_times = []
        aces_2_times = []
        aces_1_stds = []
        aces_2_stds = []

        for ocio_ver in ocio_versions:
            aces_1_data = self.all_ocio_comparison_data[
                (self.all_ocio_comparison_data["ocio_version"] == ocio_ver)
                & (self.all_ocio_comparison_data["aces_version"] == "ACES 1.0")
            ]
            aces_2_data = self.all_ocio_comparison_data[
                (self.all_ocio_comparison_data["ocio_version"] == ocio_ver)
                & (self.all_ocio_comparison_data["aces_version"] == "ACES 2.0")
            ]

            aces_1_times.append(
                aces_1_data["mean_avg_time"].mean() if len(aces_1_data) > 0 else 0
            )
            aces_2_times.append(
                aces_2_data["mean_avg_time"].mean() if len(aces_2_data) > 0 else 0
            )
            aces_1_stds.append(
                aces_1_data["std_avg_time"].mean() if len(aces_1_data) > 0 else 0
            )
            aces_2_stds.append(
                aces_2_data["std_avg_time"].mean() if len(aces_2_data) > 0 else 0
            )

        bars1 = ax1.bar(
            [i - width / 2 for i in x],
            aces_1_times,
            width,
            yerr=aces_1_stds,
            capsize=5,
            alpha=0.7,
            label="ACES 1.0",
        )
        bars2 = ax1.bar(
            [i + width / 2 for i in x],
            aces_2_times,
            width,
            yerr=aces_2_stds,
            capsize=5,
            alpha=0.7,
            label="ACES 2.0",
        )

        ax1.set_title("Mean Performance by OCIO Version and ACES Version")
        ax1.set_xlabel("OCIO Version")
        ax1.set_ylabel("Mean Average Time (ms)")
        ax1.set_xticks(x)
        ax1.set_xticklabels(ocio_versions)
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Add value labels on bars
        for bar, value in zip(bars1, aces_1_times):
            if value > 0:
                ax1.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.01,
                    f"{value:.1f}",
                    ha="center",
                    va="bottom",
                    fontsize=9,
                )

        for bar, value in zip(bars2, aces_2_times):
            if value > 0:
                ax1.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.01,
                    f"{value:.1f}",
                    ha="center",
                    va="bottom",
                    fontsize=9,
                )

        # Plot 2: File count by OCIO version and ACES version
        ax2 = axes[0, 1]

        # Get file counts for each OCIO version for both ACES versions
        aces_1_files = []
        aces_2_files = []

        for ocio_ver in ocio_versions:
            aces_1_data = self.all_ocio_comparison_data[
                (self.all_ocio_comparison_data["ocio_version"] == ocio_ver)
                & (self.all_ocio_comparison_data["aces_version"] == "ACES 1.0")
            ]
            aces_2_data = self.all_ocio_comparison_data[
                (self.all_ocio_comparison_data["ocio_version"] == ocio_ver)
                & (self.all_ocio_comparison_data["aces_version"] == "ACES 2.0")
            ]

            aces_1_files.append(
                aces_1_data["file_count"].sum() if len(aces_1_data) > 0 else 0
            )
            aces_2_files.append(
                aces_2_data["file_count"].sum() if len(aces_2_data) > 0 else 0
            )

        ax2.bar(
            [i - width / 2 for i in x], aces_1_files, width, alpha=0.7, label="ACES 1.0"
        )
        ax2.bar(
            [i + width / 2 for i in x], aces_2_files, width, alpha=0.7, label="ACES 2.0"
        )

        ax2.set_title("Number of Test Files by OCIO Version and ACES Version")
        ax2.set_xlabel("OCIO Version")
        ax2.set_ylabel("File Count")
        ax2.set_xticks(x)
        ax2.set_xticklabels(ocio_versions)
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        # Plot 3: ACES version comparison for each OCIO version
        ax3 = axes[1, 0]

        # Calculate ACES 1.0 vs 2.0 performance differences
        aces_diff_pct = []
        for i, ocio_ver in enumerate(ocio_versions):
            if aces_1_times[i] > 0 and aces_2_times[i] > 0:
                diff_pct = ((aces_2_times[i] - aces_1_times[i]) / aces_1_times[i]) * 100
                aces_diff_pct.append(diff_pct)
            else:
                aces_diff_pct.append(0)

        colors = ["green" if x < 0 else "red" for x in aces_diff_pct]
        bars5 = ax3.bar(ocio_versions, aces_diff_pct, color=colors, alpha=0.7)
        ax3.set_title("ACES 2.0 vs ACES 1.0 Performance Difference")
        ax3.set_xlabel("OCIO Version")
        ax3.set_ylabel("Performance Difference (%)")
        ax3.grid(True, alpha=0.3)
        ax3.axhline(y=0, color="black", linestyle="-", alpha=0.5)

        # Add value labels
        for bar, value in zip(bars5, aces_diff_pct):
            if value != 0:
                ax3.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + (1 if value > 0 else -1),
                    f"{value:.1f}%",
                    ha="center",
                    va="bottom" if value > 0 else "top",
                    fontsize=9,
                )

        # Plot 4: Overall ACES version performance summary
        ax4 = axes[1, 1]

        # Calculate overall ACES performance
        overall_aces_1 = self.all_ocio_comparison_data[
            self.all_ocio_comparison_data["aces_version"] == "ACES 1.0"
        ]["mean_avg_time"].mean()

        overall_aces_2 = self.all_ocio_comparison_data[
            self.all_ocio_comparison_data["aces_version"] == "ACES 2.0"
        ]["mean_avg_time"].mean()

        overall_diff = (
            ((overall_aces_2 - overall_aces_1) / overall_aces_1) * 100
            if overall_aces_1 > 0
            else 0
        )

        bars6 = ax4.bar(
            ["ACES 1.0", "ACES 2.0"],
            [overall_aces_1, overall_aces_2],
            color=["#2E86AB", "#A23B72"],
            alpha=0.7,
        )
        ax4.set_title("Overall ACES Version Performance")
        ax4.set_ylabel("Mean Average Time (ms)")
        ax4.grid(True, alpha=0.3)

        # Add value labels
        for bar, value in zip(bars6, [overall_aces_1, overall_aces_2]):
            ax4.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.01,
                f"{value:.1f}ms",
                ha="center",
                va="bottom",
                fontsize=10,
            )

        # Add overall difference annotation
        ax4.annotate(
            f"Difference: {overall_diff:+.1f}%",
            xy=(0.5, max(overall_aces_1, overall_aces_2) * 1.1),
            xycoords="data",
            ha="center",
            va="bottom",
            fontsize=10,
            color="red" if overall_diff > 0 else "green",
            fontweight="bold",
        )

        plt.tight_layout()
        plt.savefig(
            output_dir / "ocio_version_comparison.png", dpi=300, bbox_inches="tight"
        )
        plt.close()

        logger.info("OCIO version comparison plot saved")

    def create_detailed_cpu_os_ocio_comparison(self, output_dir: Path) -> None:
        """
        Create detailed CPU+OS comparison chart for OCIO versions 2.4.1 and 2.4.2, with both ACES versions on the same scale.

        Args:
            output_dir: Directory to save plots
        """
        output_dir.mkdir(exist_ok=True)

        if self.summary_df is None:
            raise ValueError(
                "Summary data not available. Call summarize_by_filename() first."
            )

        # Filter data for OCIO versions 2.4.1 and 2.4.2
        ocio_versions = ["2.4.1", "2.4.2"]
        filtered_data = self.summary_df[
            self.summary_df["ocio_version"].isin(ocio_versions)
        ]

        if len(filtered_data) == 0:
            logger.warning("No data found for OCIO versions 2.4.1 and 2.4.2")
            return

        # Create short labels for CPU + OS combinations
        filtered_data = filtered_data.copy()
        filtered_data["short_label"] = filtered_data.apply(
            lambda row: self._create_short_cpu_os_label(
                row["cpu_model"], row["os_release"]
            ),
            axis=1,
        )

        # Group by CPU+OS combination and collect data for both ACES versions and OCIO versions
        comparison_data = []
        for (cpu_model, os_release), group in filtered_data.groupby(
            ["cpu_model", "os_release"]
        ):
            versions_present = group["ocio_version"].unique()
            if len(versions_present) >= 1:  # At least one version present
                group_data = {
                    "cpu_model": cpu_model,
                    "os_release": os_release,
                    "short_label": group["short_label"].iloc[0],
                }

                # Add performance data for each ACES version and OCIO version combination
                for aces_version in ["ACES 1.0", "ACES 2.0"]:
                    for ocio_version in ocio_versions:
                        version_data = group[
                            (group["ocio_version"] == ocio_version)
                            & (group["aces_version"] == aces_version)
                        ]
                        if len(version_data) > 0:
                            group_data[f"{aces_version}_{ocio_version}"] = version_data[
                                "mean_avg_time"
                            ].mean()
                        else:
                            group_data[f"{aces_version}_{ocio_version}"] = None

                comparison_data.append(group_data)

        if not comparison_data:
            logger.warning(
                "No comparison data available for OCIO versions 2.4.1 and 2.4.2"
            )
            return

        # Create single merged chart
        fig, ax = plt.subplots(figsize=(20, 10))

        # Prepare data for plotting
        labels = []
        aces_1_ocio_241_values = []
        aces_1_ocio_242_values = []
        aces_2_ocio_241_values = []
        aces_2_ocio_242_values = []

        for item in comparison_data:
            labels.append(item["short_label"])

            # Handle None values by converting to 0
            val_aces1_241 = item.get("ACES 1.0_2.4.1", None)
            val_aces1_242 = item.get("ACES 1.0_2.4.2", None)
            val_aces2_241 = item.get("ACES 2.0_2.4.1", None)
            val_aces2_242 = item.get("ACES 2.0_2.4.2", None)

            aces_1_ocio_241_values.append(
                val_aces1_241 if val_aces1_241 is not None else 0
            )
            aces_1_ocio_242_values.append(
                val_aces1_242 if val_aces1_242 is not None else 0
            )
            aces_2_ocio_241_values.append(
                val_aces2_241 if val_aces2_241 is not None else 0
            )
            aces_2_ocio_242_values.append(
                val_aces2_242 if val_aces2_242 is not None else 0
            )

        # Create bar positions
        x_pos = range(len(labels))
        bar_width = 0.2

        # Create bars for all combinations
        bars1 = ax.bar(
            [x - 1.5 * bar_width for x in x_pos],
            aces_1_ocio_241_values,
            bar_width,
            label="ACES 1.0 + OCIO 2.4.1",
            alpha=0.8,
            color="#1f77b4",
        )
        bars2 = ax.bar(
            [x - 0.5 * bar_width for x in x_pos],
            aces_1_ocio_242_values,
            bar_width,
            label="ACES 1.0 + OCIO 2.4.2",
            alpha=0.8,
            color="#ff7f0e",
        )
        bars3 = ax.bar(
            [x + 0.5 * bar_width for x in x_pos],
            aces_2_ocio_241_values,
            bar_width,
            label="ACES 2.0 + OCIO 2.4.1",
            alpha=0.8,
            color="#2ca02c",
        )
        bars4 = ax.bar(
            [x + 1.5 * bar_width for x in x_pos],
            aces_2_ocio_242_values,
            bar_width,
            label="ACES 2.0 + OCIO 2.4.2",
            alpha=0.8,
            color="#d62728",
        )

        # Customize the plot
        ax.set_title(
            "OCIO Version Performance Comparison by CPU, OS, and ACES Version\n(Merged Chart: 2.4.1 vs 2.4.2)",
            fontsize=14,
            fontweight="bold",
            pad=20,
        )
        ax.set_xlabel("CPU Model + OS Release", fontsize=12)
        ax.set_ylabel("Mean Average Time (ms)", fontsize=12)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=10)
        ax.legend(fontsize=10, loc="upper right")
        ax.grid(True, alpha=0.3, axis="y")

        # Add value labels on bars
        all_values = (
            aces_1_ocio_241_values
            + aces_1_ocio_242_values
            + aces_2_ocio_241_values
            + aces_2_ocio_242_values
        )
        max_val = max(all_values) if all_values else 1

        for bars, values in [
            (bars1, aces_1_ocio_241_values),
            (bars2, aces_1_ocio_242_values),
            (bars3, aces_2_ocio_241_values),
            (bars4, aces_2_ocio_242_values),
        ]:
            for bar, value in zip(bars, values):
                if value > 0:
                    ax.text(
                        bar.get_x() + bar.get_width() / 2,
                        bar.get_height() + max_val * 0.01,
                        f"{value:.0f}",
                        ha="center",
                        va="bottom",
                        fontsize=8,
                        rotation=90,
                    )

        # Add performance difference annotations between OCIO versions for each ACES version
        for i in range(len(labels)):
            # ACES 1.0 comparison
            if aces_1_ocio_241_values[i] > 0 and aces_1_ocio_242_values[i] > 0:
                diff_pct = (
                    (aces_1_ocio_242_values[i] - aces_1_ocio_241_values[i])
                    / aces_1_ocio_241_values[i]
                ) * 100
                color = "green" if diff_pct < 0 else "red"
                mid_x = i - bar_width
                mid_y = (
                    max(aces_1_ocio_241_values[i], aces_1_ocio_242_values[i])
                    + max_val * 0.08
                )
                ax.annotate(
                    f"{diff_pct:+.1f}%",
                    xy=(mid_x, mid_y),
                    ha="center",
                    va="bottom",
                    fontsize=7,
                    color=color,
                    fontweight="bold",
                )

            # ACES 2.0 comparison
            if aces_2_ocio_241_values[i] > 0 and aces_2_ocio_242_values[i] > 0:
                diff_pct = (
                    (aces_2_ocio_242_values[i] - aces_2_ocio_241_values[i])
                    / aces_2_ocio_241_values[i]
                ) * 100
                color = "green" if diff_pct < 0 else "red"
                mid_x = i + bar_width
                mid_y = (
                    max(aces_2_ocio_241_values[i], aces_2_ocio_242_values[i])
                    + max_val * 0.08
                )
                ax.annotate(
                    f"{diff_pct:+.1f}%",
                    xy=(mid_x, mid_y),
                    ha="center",
                    va="bottom",
                    fontsize=7,
                    color=color,
                    fontweight="bold",
                )

        # Add summary statistics text box
        aces_1_avg_241 = (
            sum(v for v in aces_1_ocio_241_values if v > 0)
            / len([v for v in aces_1_ocio_241_values if v > 0])
            if any(v > 0 for v in aces_1_ocio_241_values)
            else 0
        )
        aces_1_avg_242 = (
            sum(v for v in aces_1_ocio_242_values if v > 0)
            / len([v for v in aces_1_ocio_242_values if v > 0])
            if any(v > 0 for v in aces_1_ocio_242_values)
            else 0
        )
        aces_2_avg_241 = (
            sum(v for v in aces_2_ocio_241_values if v > 0)
            / len([v for v in aces_2_ocio_241_values if v > 0])
            if any(v > 0 for v in aces_2_ocio_241_values)
            else 0
        )
        aces_2_avg_242 = (
            sum(v for v in aces_2_ocio_242_values if v > 0)
            / len([v for v in aces_2_ocio_242_values if v > 0])
            if any(v > 0 for v in aces_2_ocio_242_values)
            else 0
        )

        stats_text = f"""Performance Summary:
ACES 1.0 + OCIO 2.4.1: {aces_1_avg_241:.1f} ms
ACES 1.0 + OCIO 2.4.2: {aces_1_avg_242:.1f} ms
ACES 2.0 + OCIO 2.4.1: {aces_2_avg_241:.1f} ms
ACES 2.0 + OCIO 2.4.2: {aces_2_avg_242:.1f} ms"""

        ax.text(
            0.02,
            0.98,
            stats_text,
            transform=ax.transAxes,
            fontsize=10,
            verticalalignment="top",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.8),
            fontfamily="monospace",
        )

        plt.tight_layout()
        plt.savefig(
            output_dir / "ocio_241_vs_242_cpu_os_aces_comparison.png",
            dpi=300,
            bbox_inches="tight",
        )
        plt.close()

        logger.info(
            "Detailed CPU+OS OCIO version comparison plot (merged ACES versions) saved"
        )

    def create_comprehensive_aces_comparison(self, output_dir: Path) -> None:
        """
        Create a comprehensive single bar chart comparing ACES 1.0 vs 2.0 across all dimensions.

        Args:
            output_dir: Directory to save plots
        """
        output_dir.mkdir(exist_ok=True)

        if self.summary_df is None:
            raise ValueError(
                "Summary data not available. Call summarize_by_filename() first."
            )

        # Prepare data for comprehensive comparison
        comparison_categories = []
        aces_1_values = []
        aces_2_values = []

        # 1. Overall ACES performance
        overall_aces_1 = self.summary_df[self.summary_df["aces_version"] == "ACES 1.0"][
            "mean_avg_time"
        ].mean()
        overall_aces_2 = self.summary_df[self.summary_df["aces_version"] == "ACES 2.0"][
            "mean_avg_time"
        ].mean()

        comparison_categories.append("Overall\nPerformance")
        aces_1_values.append(overall_aces_1)
        aces_2_values.append(overall_aces_2)

        # 2. Performance by OS Release
        for os_release in sorted(self.summary_df["os_release"].unique()):
            os_aces_1 = self.summary_df[
                (self.summary_df["aces_version"] == "ACES 1.0")
                & (self.summary_df["os_release"] == os_release)
            ]["mean_avg_time"].mean()

            os_aces_2 = self.summary_df[
                (self.summary_df["aces_version"] == "ACES 2.0")
                & (self.summary_df["os_release"] == os_release)
            ]["mean_avg_time"].mean()

            if not pd.isna(os_aces_1) and not pd.isna(os_aces_2):
                comparison_categories.append(f"OS {os_release}")
                aces_1_values.append(os_aces_1)
                aces_2_values.append(os_aces_2)

        # 3. Performance by OCIO Version
        for ocio_version in sorted(self.summary_df["ocio_version"].unique()):
            ocio_aces_1 = self.summary_df[
                (self.summary_df["aces_version"] == "ACES 1.0")
                & (self.summary_df["ocio_version"] == ocio_version)
            ]["mean_avg_time"].mean()

            ocio_aces_2 = self.summary_df[
                (self.summary_df["aces_version"] == "ACES 2.0")
                & (self.summary_df["ocio_version"] == ocio_version)
            ]["mean_avg_time"].mean()

            if not pd.isna(ocio_aces_1) and not pd.isna(ocio_aces_2):
                comparison_categories.append(f"OCIO {ocio_version}")
                aces_1_values.append(ocio_aces_1)
                aces_2_values.append(ocio_aces_2)

        # 4. Performance by CPU Model (top performing ones)
        cpu_data = self.summary_df[self.summary_df["cpu_model"] != "Unknown"]
        cpu_models = (
            cpu_data["cpu_model"].value_counts().head(4).index
        )  # Top 4 most tested CPUs

        for cpu_model in cpu_models:
            cpu_aces_1 = self.summary_df[
                (self.summary_df["aces_version"] == "ACES 1.0")
                & (self.summary_df["cpu_model"] == cpu_model)
            ]["mean_avg_time"].mean()

            cpu_aces_2 = self.summary_df[
                (self.summary_df["aces_version"] == "ACES 2.0")
                & (self.summary_df["cpu_model"] == cpu_model)
            ]["mean_avg_time"].mean()

            if not pd.isna(cpu_aces_1) and not pd.isna(cpu_aces_2):
                # Create short CPU name
                cpu_short = self._create_short_cpu_name(cpu_model)
                comparison_categories.append(f"{cpu_short}")
                aces_1_values.append(cpu_aces_1)
                aces_2_values.append(cpu_aces_2)

        # Create the comprehensive bar chart
        fig, ax = plt.subplots(figsize=(16, 10))

        # Set up bar positions
        x_pos = range(len(comparison_categories))
        bar_width = 0.35

        # Create bars
        bars1 = ax.bar(
            [x - bar_width / 2 for x in x_pos],
            aces_1_values,
            bar_width,
            label="ACES 1.0",
            alpha=0.8,
            color="#2E86AB",
        )
        bars2 = ax.bar(
            [x + bar_width / 2 for x in x_pos],
            aces_2_values,
            bar_width,
            label="ACES 2.0",
            alpha=0.8,
            color="#A23B72",
        )

        # Customize the plot
        ax.set_title(
            "Comprehensive ACES Version Performance Comparison\n(ACES 1.0 vs ACES 2.0 across all dimensions)",
            fontsize=14,
            fontweight="bold",
            pad=20,
        )
        ax.set_xlabel("Comparison Categories", fontsize=12)
        ax.set_ylabel("Mean Average Time (ms)", fontsize=12)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(comparison_categories, rotation=45, ha="right", fontsize=10)
        ax.legend(fontsize=12)
        ax.grid(True, alpha=0.3, axis="y")

        # Add value labels on bars
        max_val = max(max(aces_1_values + aces_2_values, default=0), 1)
        for bar, value in zip(bars1, aces_1_values):
            if value > 0:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + max_val * 0.01,
                    f"{value:.0f}",
                    ha="center",
                    va="bottom",
                    fontsize=9,
                    fontweight="bold",
                )

        for bar, value in zip(bars2, aces_2_values):
            if value > 0:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + max_val * 0.01,
                    f"{value:.0f}",
                    ha="center",
                    va="bottom",
                    fontsize=9,
                    fontweight="bold",
                )

        # Add percentage difference annotations above each pair
        for i, (val1, val2) in enumerate(zip(aces_1_values, aces_2_values)):
            if val1 > 0 and val2 > 0:
                diff_pct = ((val2 - val1) / val1) * 100
                color = "green" if diff_pct < 0 else "red"
                ax.annotate(
                    f"{diff_pct:+.0f}%",
                    xy=(i, max(val1, val2) + max_val * 0.08),
                    ha="center",
                    va="bottom",
                    fontsize=10,
                    color=color,
                    fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
                )

        # Add overall statistics text box
        overall_diff = (
            ((overall_aces_2 - overall_aces_1) / overall_aces_1) * 100
            if overall_aces_1 > 0
            else 0
        )
        stats_text = f"""Overall Statistics:
ACES 1.0 Average: {overall_aces_1:.1f} ms
ACES 2.0 Average: {overall_aces_2:.1f} ms
Performance Difference: {overall_diff:+.1f}%
Better Performing: {"ACES 1.0" if overall_aces_1 < overall_aces_2 else "ACES 2.0"}"""

        ax.text(
            0.02,
            0.98,
            stats_text,
            transform=ax.transAxes,
            fontsize=10,
            verticalalignment="top",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.8),
            fontfamily="monospace",
        )

        plt.tight_layout()
        plt.savefig(
            output_dir / "comprehensive_aces_comparison.png",
            dpi=300,
            bbox_inches="tight",
        )
        plt.close()

        logger.info("Comprehensive ACES comparison chart saved")

    def _create_short_cpu_name(self, cpu_model: str) -> str:
        """
        Create a short name for CPU model for display purposes.

        Args:
            cpu_model: Full CPU model name

        Returns:
            Short CPU name
        """
        if cpu_model == "Unknown":
            return "Unknown"

        # Extract key CPU information
        cpu_short = cpu_model

        # Remove common prefixes/suffixes
        cpu_short = cpu_short.replace("Intel(R) ", "")
        cpu_short = cpu_short.replace("(R) ", "")
        cpu_short = cpu_short.replace(" CPU", "")
        cpu_short = cpu_short.replace(" @", "")

        # Simplify specific model names
        if "Core(TM) i9-9900K" in cpu_short:
            return "i9-9900K"
        elif "Core(TM) i9-9900" in cpu_short:
            return "i9-9900"
        elif "Xeon(R) CPU E5-2687W v3" in cpu_short:
            return "E5-2687W v3"
        elif "Xeon(R) CPU E5-2667 v4" in cpu_short:
            return "E5-2667 v4"
        elif "Xeon(R) W-2295" in cpu_short:
            return "W-2295"
        elif "Xeon(R) w5-2465X" in cpu_short:
            return "w5-2465X"
        elif "Xeon(R) w7-2495X" in cpu_short:
            return "w7-2495X"
        else:
            # General simplification for other models
            parts = cpu_short.split()
            if len(parts) >= 2:
                return f"{parts[0]} {parts[1]}"
            elif len(parts) >= 1:
                return parts[0]
            else:
                return "Unknown"

    def _create_short_cpu_os_label(self, cpu_model: str, os_release: str) -> str:
        """
        Create a short label for CPU model and OS release.

        Args:
            cpu_model: Full CPU model name
            os_release: OS release (r7, r9, etc.)

        Returns:
            Short label for display
        """
        if cpu_model == "Unknown":
            return f"Unknown-{os_release}"

        # Get short CPU name
        cpu_short = self._create_short_cpu_name(cpu_model)

        return f"{cpu_short}-{os_release}"

    def create_detailed_ocio_comparison_report(self, output_dir: Path) -> None:
        """
        Create a detailed OCIO version comparison report with ACES version information.

        Args:
            output_dir: Directory to save the report
        """
        output_dir.mkdir(exist_ok=True)

        if (
            not hasattr(self, "all_ocio_comparison_data")
            or self.all_ocio_comparison_data is None
        ):
            logger.warning("No OCIO version comparison data available")
            return

        report_file = output_dir / "ocio_version_comparison_report.txt"

        with open(report_file, "w") as f:
            f.write(
                "OCIO Test Results - OCIO Version Performance Comparison Report (by ACES Version)\n"
            )
            f.write("=" * 85 + "\n\n")

            # Summary statistics
            f.write("SUMMARY STATISTICS\n")
            f.write("-" * 20 + "\n")
            f.write(
                f"Total OCIO-ACES version combinations: {len(self.all_ocio_comparison_data)}\n"
            )
            f.write(
                f"OCIO versions: {list(self.all_ocio_comparison_data['ocio_version'].unique())}\n"
            )
            f.write(
                f"ACES versions: {list(self.all_ocio_comparison_data['aces_version'].unique())}\n"
            )

            # Overall ACES version performance
            f.write("\nOVERALL ACES VERSION PERFORMANCE\n")
            f.write("-" * 35 + "\n")
            for aces_version in sorted(
                self.all_ocio_comparison_data["aces_version"].unique()
            ):
                aces_data = self.all_ocio_comparison_data[
                    self.all_ocio_comparison_data["aces_version"] == aces_version
                ]
                avg_time = aces_data["mean_avg_time"].mean()
                std_time = aces_data["mean_avg_time"].std()
                f.write(f"{aces_version}: {avg_time:.2f} ± {std_time:.2f} ms\n")

            # Get overall performance comparison
            sorted_data = self.all_ocio_comparison_data.sort_values("mean_avg_time")
            fastest_version = sorted_data.iloc[0]
            slowest_version = sorted_data.iloc[-1]

            if fastest_version["mean_avg_time"] != 0:
                perf_diff = (
                    (
                        slowest_version["mean_avg_time"]
                        - fastest_version["mean_avg_time"]
                    )
                    / fastest_version["mean_avg_time"]
                ) * 100
                f.write(
                    f"\nFastest combination: {fastest_version['ocio_version']} + {fastest_version['aces_version']} ({fastest_version['mean_avg_time']:.1f} ms)\n"
                )
                f.write(
                    f"Slowest combination: {slowest_version['ocio_version']} + {slowest_version['aces_version']} ({slowest_version['mean_avg_time']:.1f} ms)\n"
                )
                f.write(f"Performance difference: {perf_diff:.1f}%\n\n")

            # Detailed version comparisons by ACES version
            f.write("DETAILED OCIO VERSION ANALYSIS BY ACES VERSION\n")
            f.write("-" * 50 + "\n")

            for aces_version in sorted(
                self.all_ocio_comparison_data["aces_version"].unique()
            ):
                f.write(f"\n{aces_version}:\n")
                f.write("=" * (len(aces_version) + 2) + "\n")

                aces_data = self.all_ocio_comparison_data[
                    self.all_ocio_comparison_data["aces_version"] == aces_version
                ].sort_values("ocio_version")

                # For detailed listings, sort by version order
                for _, row in aces_data.iterrows():
                    f.write(f"\n  OCIO Version: {row['ocio_version']}\n")
                    f.write(f"  {'-' * (len(row['ocio_version']) + 17)}\n")
                    f.write(f"    Files tested: {row['file_count']}\n")
                    f.write(f"    Mean avg time: {row['mean_avg_time']:.3f} ms\n")
                    f.write(f"    Std deviation: {row['std_avg_time']:.3f} ms\n")
                    f.write(f"    Median time: {row['median_avg_time']:.3f} ms\n")
                    f.write(f"    Total operations: {row['total_operations']}\n")
                    f.write(f"    CPU models tested: {len(row['cpu_models'])}\n")
                    f.write(f"    OS releases tested: {row['os_releases']}\n")
                    f.write(
                        f"    CPU models: {', '.join([cpu for cpu in row['cpu_models'] if cpu != 'Unknown'])}\n"
                    )

                    # Calculate relative performance vs fastest overall
                    if fastest_version["mean_avg_time"] != 0:
                        rel_perf = (
                            row["mean_avg_time"] / fastest_version["mean_avg_time"]
                        ) * 100
                        f.write(
                            f"    Relative performance: {rel_perf:.1f}% of fastest overall\n"
                        )

                # OCIO version comparison within this ACES version
                if len(aces_data) > 1:
                    f.write(f"\n  OCIO Version Comparison within {aces_version}:\n")
                    f.write(f"  {'-' * (35 + len(aces_version))}\n")

                    # Sort by performance for fastest/slowest comparison
                    aces_data_by_perf = aces_data.sort_values("mean_avg_time")
                    fastest_aces = aces_data_by_perf.iloc[0]
                    slowest_aces = aces_data_by_perf.iloc[-1]

                    if fastest_aces["mean_avg_time"] != 0:
                        aces_perf_diff = (
                            (
                                slowest_aces["mean_avg_time"]
                                - fastest_aces["mean_avg_time"]
                            )
                            / fastest_aces["mean_avg_time"]
                        ) * 100
                        f.write(
                            f"    Fastest: {fastest_aces['ocio_version']} ({fastest_aces['mean_avg_time']:.1f} ms)\n"
                        )
                        f.write(
                            f"    Slowest: {slowest_aces['ocio_version']} ({slowest_aces['mean_avg_time']:.1f} ms)\n"
                        )
                        f.write(f"    Performance difference: {aces_perf_diff:.1f}%\n")

                f.write("\n" + "-" * 60 + "\n")

        logger.info(f"Detailed OCIO version comparison report saved to {report_file}")

    def run_full_analysis(self, output_dir: Path) -> None:
        """
        Run the complete analysis pipeline.

        Args:
            output_dir: Directory to save all outputs
        """
        output_dir.mkdir(exist_ok=True)

        logger.info("Starting full OCIO analysis...")

        # Load and process data
        self.load_data()
        self.summarize_by_filename()
        self.find_cpu_os_comparisons()
        self.find_ocio_version_comparisons()
        self.find_all_ocio_version_comparisons()

        # Create visualizations
        self.create_summary_plots(output_dir)
        self.create_os_comparison_plots(output_dir)
        self.create_detailed_comparison_report(output_dir)
        self.create_ocio_version_plots(output_dir)
        self.create_detailed_cpu_os_ocio_comparison(output_dir)
        self.create_comprehensive_aces_comparison(output_dir)
        self.create_detailed_ocio_comparison_report(output_dir)

        # Save summary data
        self.summary_df.to_csv(output_dir / "file_summaries.csv", index=False)
        self.comparison_data.to_csv(output_dir / "os_comparisons.csv", index=False)

        # Save OCIO version comparison data if available
        if (
            hasattr(self, "all_ocio_comparison_data")
            and self.all_ocio_comparison_data is not None
        ):
            self.all_ocio_comparison_data.to_csv(
                output_dir / "ocio_version_comparisons.csv", index=False
            )
        if (
            hasattr(self, "ocio_comparison_data")
            and self.ocio_comparison_data is not None
        ):
            self.ocio_comparison_data.to_csv(
                output_dir / "detailed_ocio_comparisons.csv", index=False
            )

        logger.info(f"Analysis complete! Results saved to {output_dir}")


def main():
    """Main function to run the analysis."""
    # Set up paths
    script_dir = Path(__file__).parent
    csv_file = script_dir / "ocio_test_results.csv"
    output_dir = script_dir / "analysis_results"

    # Create analyzer and run analysis
    analyzer = OCIOAnalyzer(csv_file)

    if not csv_file.exists():
        logger.error(f"CSV file not found: {csv_file}")
        return

    try:
        analyzer.run_full_analysis(output_dir)
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise


if __name__ == "__main__":
    main()
