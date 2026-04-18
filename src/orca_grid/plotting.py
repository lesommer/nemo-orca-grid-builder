"""
Plotting utilities for ORCA grid visualization.

This module provides functions to visualize ORCA grid structure,
scale factors, and other properties.
"""

import numpy as np
import matplotlib.pyplot as plt
import xarray as xr

def plot_grid_structure(grid_file, title="ORCA Grid", output_file=None):
    """
    Plot the basic grid structure (latitude/longitude).
    
    Args:
        grid_file: Path to NetCDF grid file
        title: Plot title
        output_file: Optional output file path (without extension)
        
    Returns:
        fig: matplotlib figure object
    """
    ds = xr.open_dataset(grid_file)
    
    # Create figure with subplots
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle(title, y=1.05)
    
    # Plot longitude
    lon = ds['nav_lon']
    im1 = axes[0].imshow(lon, cmap='viridis', aspect='auto')
    axes[0].set_title('Longitude')
    axes[0].set_xlabel('X (zonal)')
    axes[0].set_ylabel('Y (meridional)')
    plt.colorbar(im1, ax=axes[0], label='Longitude (°E)')
    
    # Plot latitude
    lat = ds['nav_lat']
    im2 = axes[1].imshow(lat, cmap='plasma', aspect='auto')
    axes[1].set_title('Latitude')
    axes[1].set_xlabel('X (zonal)')
    axes[1].set_ylabel('Y (meridional)')
    plt.colorbar(im2, ax=axes[1], label='Latitude (°N)')
    
    plt.tight_layout()
    
    if output_file:
        plt.savefig(f'{output_file}.png', dpi=300, bbox_inches='tight')
    
    return fig

def plot_scale_factors(grid_file, title="Scale Factors", output_file=None):
    """
    Plot the scale factors (e1t, e2t).
    
    Args:
        grid_file: Path to NetCDF grid file
        title: Plot title
        output_file: Optional output file path (without extension)
        
    Returns:
        fig: matplotlib figure object
    """
    ds = xr.open_dataset(grid_file)
    
    # Create figure with subplots
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle(title, y=1.05)
    
    # Plot e1t (zonal scale factor)
    e1t = ds['e1t'][0, :, :]  # Remove time dimension
    im1 = axes[0].imshow(e1t, cmap='magma', aspect='auto')
    axes[0].set_title('Zonal Scale Factor (e1t)')
    axes[0].set_xlabel('X (zonal)')
    axes[0].set_ylabel('Y (meridional)')
    plt.colorbar(im1, ax=axes[0], label='Scale factor (m)')
    
    # Plot e2t (meridional scale factor)
    e2t = ds['e2t'][0, :, :]  # Remove time dimension
    im2 = axes[1].imshow(e2t, cmap='magma', aspect='auto')
    axes[1].set_title('Meridional Scale Factor (e2t)')
    axes[1].set_xlabel('X (zonal)')
    axes[1].set_ylabel('Y (meridional)')
    plt.colorbar(im2, ax=axes[1], label='Scale factor (m)')
    
    plt.tight_layout()
    
    if output_file:
        plt.savefig(f'{output_file}.png', dpi=300, bbox_inches='tight')
    
    return fig

def plot_staggered_points(grid_data, title="Staggered Grid Points"):
    """
    Plot the staggered grid points (T, U, V, F).
    
    Args:
        grid_data: Dictionary containing grid data
        title: Plot title
        
    Returns:
        fig: matplotlib figure object
    """
    # Extract coordinates
    lat_t = grid_data['gphit'][0, :, :]
    lat_u = grid_data['gphiu'][0, :, :]
    lat_v = grid_data['gphiv'][0, :, :]
    lat_f = grid_data['gphif'][0, :, :]
    
    # Create figure
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    fig.suptitle(title, y=1.02)
    
    # Plot T-points
    im1 = axes[0, 0].imshow(lat_t, cmap='viridis', aspect='auto')
    axes[0, 0].set_title('T-points (Tracer)')
    axes[0, 0].set_xlabel('X')
    axes[0, 0].set_ylabel('Y')
    plt.colorbar(im1, ax=axes[0, 0])
    
    # Plot U-points
    im2 = axes[0, 1].imshow(lat_u, cmap='viridis', aspect='auto')
    axes[0, 1].set_title('U-points (Zonal Velocity)')
    axes[0, 1].set_xlabel('X')
    axes[0, 1].set_ylabel('Y')
    plt.colorbar(im2, ax=axes[0, 1])
    
    # Plot V-points
    im3 = axes[1, 0].imshow(lat_v, cmap='viridis', aspect='auto')
    axes[1, 0].set_title('V-points (Meridional Velocity)')
    axes[1, 0].set_xlabel('X')
    axes[1, 0].set_ylabel('Y')
    plt.colorbar(im3, ax=axes[1, 0])
    
    # Plot F-points
    im4 = axes[1, 1].imshow(lat_f, cmap='viridis', aspect='auto')
    axes[1, 1].set_title('F-points (Vortex)')
    axes[1, 1].set_xlabel('X')
    axes[1, 1].set_ylabel('Y')
    plt.colorbar(im4, ax=axes[1, 1])
    
    plt.tight_layout()
    return fig