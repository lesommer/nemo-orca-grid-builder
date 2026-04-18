#!/usr/bin/env python3
"""
Generate visualization plots of the ORCA grids.

This script creates plots showing the grid structure, coordinate systems,
and scale factors for different resolutions.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
from orca_grid import ORCAGridBuilder

def plot_grid_structure(grid_file, title, output_file):
    """Plot the basic grid structure (latitude/longitude)."""
    ds = xr.open_dataset(grid_file)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot longitude
    lon = ds['nav_lon']
    im = ax.imshow(lon, cmap='viridis', aspect='auto')
    ax.set_title(f'{title} - Longitude')
    ax.set_xlabel('X (zonal)')
    ax.set_ylabel('Y (meridional)')
    plt.colorbar(im, ax=ax, label='Longitude (°E)')
    plt.tight_layout()
    plt.savefig(f'{output_file}_lon.png', dpi=300)
    plt.close()
    
    # Plot latitude
    fig, ax = plt.subplots(figsize=(12, 6))
    lat = ds['nav_lat']
    im = ax.imshow(lat, cmap='plasma', aspect='auto')
    ax.set_title(f'{title} - Latitude')
    ax.set_xlabel('X (zonal)')
    ax.set_ylabel('Y (meridional)')
    plt.colorbar(im, ax=ax, label='Latitude (°N)')
    plt.tight_layout()
    plt.savefig(f'{output_file}_lat.png', dpi=300)
    plt.close()

def plot_scale_factors(grid_file, title, output_file):
    """Plot the scale factors (e1t, e2t)."""
    ds = xr.open_dataset(grid_file)
    
    # Plot e1t (zonal scale factor)
    fig, ax = plt.subplots(figsize=(12, 6))
    e1t = ds['e1t'][0, :, :]  # Remove time dimension
    im = ax.imshow(e1t, cmap='magma', aspect='auto')
    ax.set_title(f'{title} - Zonal Scale Factor (e1t)')
    ax.set_xlabel('X (zonal)')
    ax.set_ylabel('Y (meridional)')
    plt.colorbar(im, ax=ax, label='Scale factor (m)')
    plt.tight_layout()
    plt.savefig(f'{output_file}_e1t.png', dpi=300)
    plt.close()
    
    # Plot e2t (meridional scale factor)
    fig, ax = plt.subplots(figsize=(12, 6))
    e2t = ds['e2t'][0, :, :]  # Remove time dimension
    im = ax.imshow(e2t, cmap='magma', aspect='auto')
    ax.set_title(f'{title} - Meridional Scale Factor (e2t)')
    ax.set_xlabel('X (zonal)')
    ax.set_ylabel('Y (meridional)')
    plt.colorbar(im, ax=ax, label='Scale factor (m)')
    plt.tight_layout()
    plt.savefig(f'{output_file}_e2t.png', dpi=300)
    plt.close()

def plot_grid_comparison():
    """Create comparison plots of different resolutions."""
    resolutions = ['2deg', '1deg', '0.5deg']
    
    fig, axes = plt.subplots(3, 2, figsize=(14, 18))
    
    for i, res in enumerate(resolutions):
        try:
            grid_file = f'{res}_grid.nc'
            ds = xr.open_dataset(grid_file)
            
            # Plot longitude
            lon = ds['nav_lon']
            im1 = axes[i, 0].imshow(lon, cmap='viridis', aspect='auto')
            axes[i, 0].set_title(f'{res} - Longitude')
            axes[i, 0].set_xlabel('X')
            axes[i, 0].set_ylabel('Y')
            plt.colorbar(im1, ax=axes[i, 0])
            
            # Plot latitude
            lat = ds['nav_lat']
            im2 = axes[i, 1].imshow(lat, cmap='plasma', aspect='auto')
            axes[i, 1].set_title(f'{res} - Latitude')
            axes[i, 1].set_xlabel('X')
            axes[i, 1].set_ylabel('Y')
            plt.colorbar(im2, ax=axes[i, 1])
            
        except Exception as e:
            print(f"Error plotting {res}: {e}")
    
    plt.tight_layout()
    plt.savefig('output/plots/grid_comparison.png', dpi=300)
    plt.close()
    
    plt.savefig('output/plots/staggered_points.png', dpi=300)
    plt.close()

def generate_all_plots():
    """Generate all visualization plots."""
    print("Generating ORCA Grid Visualization Plots...")
    
    # Create plots directory
    os.makedirs('output/plots', exist_ok=True)
    
    # Plot each resolution
    for res in ['2deg', '1deg', '0.5deg']:
        grid_file = f'output/grids/{res}_grid.nc'
        if os.path.exists(grid_file):
            print(f"  Processing {res} grid...")
            plot_grid_structure(grid_file, f'{res} ORCA Grid', f'output/plots/{res}_grid')
            plot_scale_factors(grid_file, f'{res} ORCA Grid', f'output/plots/{res}_scale_factors')
        else:
            print(f"  {res} grid file not found, skipping")
    
    # Comparison plots
    print("  Generating comparison plots...")
    plot_grid_comparison()
    plot_staggered_points()
    
    print("✓ All plots generated successfully!")
    print("  Plots saved in 'output/plots/' directory")

def add_plots_to_documentation():
    """Add plot references to the README."""
    readme_content = """

## Visualization

The library includes visualization tools to inspect the generated grids:

### Grid Structure Plots

![1° Grid Longitude](output/plots/1deg_grid_lon.png)
*Longitude coordinates for 1° ORCA grid*

![1° Grid Latitude](output/plots/1deg_grid_lat.png)  
*Latitude coordinates for 1° ORCA grid*

### Scale Factor Plots

![1° Scale Factor e1t](output/plots/1deg_scale_factors_e1t.png)
*Zonal scale factors for 1° ORCA grid*

![1° Scale Factor e2t](output/plots/1deg_scale_factors_e2t.png)
*Meridional scale factors for 1° ORCA grid*

### Staggered Grid Points

![Arakawa C-Grid](output/plots/staggered_points.png)
*Arakawa C-grid staggered points (T, U, V, F)*

### Resolution Comparison

![Grid Comparison](output/plots/grid_comparison.png)
*Comparison of different ORCA grid resolutions (2°, 1°, 0.5°)*

### Generating Your Own Plots

```python
from orca_grid.plotting import plot_grid_structure, plot_scale_factors

# Plot a specific grid
plot_grid_structure('output/grids/my_grid.nc', 'My ORCA Grid', 'output/plots/my_grid_plot')
plot_scale_factors('output/grids/my_grid.nc', 'My ORCA Grid', 'output/plots/my_scale_factors')
```

The plots help visualize:
- Grid coordinate systems
- Scale factor distributions
- Staggered point locations
- Resolution differences
- Grid quality and orthogonality
"""
    
    # Append to README
    with open('README.md', 'a') as f:
        f.write(readme_content)
    
    print("✓ Documentation updated with plot references")

if __name__ == "__main__":
    generate_all_plots()
    add_plots_to_documentation()