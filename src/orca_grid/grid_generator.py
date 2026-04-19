#!/usr/bin/env python3
"""
Grid generator module with reference algorithm support.
"""

import numpy as np
from .reference_algorithm import ReferenceORCAGridGenerator

class ORCAGridGenerator:
    """
    Grid generator with multiple algorithm options.
    """
    
    def __init__(self, resolution="1deg"):
        """Initialize grid generator."""
        self.resolution = resolution
        self.algorithm = "reference"  # Default to reference algorithm
        
        # Initialize reference generator
        self.ref_generator = ReferenceORCAGridGenerator(resolution)
    
    def generate_polar_grid(self):
        """Generate polar grid using reference algorithm."""
        return self.ref_generator.generate_j_curves()
    
    def generate_spherical_grid(self):
        """Generate full spherical grid."""
        # Use reference algorithm
        grid_data = self.ref_generator.generate_grid()
        
        # Add staggered points (simplified for now)
        grid_data['glamt'] = grid_data['nav_lon']
        grid_data['gphit'] = grid_data['nav_lat']
        
        # Add placeholder scale factors
        grid_data['e1t'] = np.ones_like(grid_data['nav_lon']) * 100000
        grid_data['e2t'] = np.ones_like(grid_data['nav_lon']) * 100000
        
        return grid_data
    
    def calculate_scale_factors(self, lat, lon):
        """Calculate scale factors."""
        # Simplified scale factor calculation
        R = 6371000.0
        
        # Meridional scale factor (distance per degree latitude)
        e2 = np.ones_like(lat) * (np.pi * R) / 180.0
        
        # Zonal scale factor (distance per degree longitude)
        lat_rad = np.deg2rad(lat)
        e1 = e2 * np.cos(lat_rad)
        
        return e1, e2
