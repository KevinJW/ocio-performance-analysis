"""
Simple script to view the generated analysis plots
"""

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from pathlib import Path

def view_plots():
    """Display the generated analysis plots."""
    analysis_dir = Path("analysis_results")
    
    if not analysis_dir.exists():
        print("Analysis results directory not found. Run ocio_analysis.py first.")
        return
    
    # Find all PNG files
    plot_files = list(analysis_dir.glob("*.png"))
    
    if not plot_files:
        print("No plot files found in analysis_results directory.")
        return
    
    print(f"Found {len(plot_files)} plot files:")
    for i, plot_file in enumerate(plot_files):
        print(f"  {i+1}. {plot_file.name}")
    
    # Display plots one by one
    for plot_file in plot_files:
        print(f"\nDisplaying: {plot_file.name}")
        
        img = mpimg.imread(plot_file)
        plt.figure(figsize=(15, 10))
        plt.imshow(img)
        plt.axis('off')
        plt.title(plot_file.stem.replace('_', ' ').title())
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    view_plots()
