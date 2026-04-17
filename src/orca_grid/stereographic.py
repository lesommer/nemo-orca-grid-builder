"""
Stereographic projection utilities for ORCA grid generation.

This module implements the stereographic polar projection used in the
Madec & Imbard (1996) method for creating orthogonal curvilinear ocean meshes.
"""

import numpy as np
import jax.numpy as jnp
from jax import jit

class StereographicProjection:
    """
    Stereographic polar projection for ORCA grid construction.
    
    The stereographic projection is a conformal mapping that preserves angles.
    It maps the sphere to a plane, with the North Pole as the projection center.
    """
    
    def __init__(self):
        """Initialize stereographic projection parameters."""
        self.R = 6371000.0  # Earth radius in meters
        
    def forward(self, lat, lon):
        """
        Forward stereographic projection: sphere -> plane.
        
        Args:
            lat: Latitude in degrees
            lon: Longitude in degrees
            
        Returns:
            (x, y): Projected coordinates in stereographic plane
        """
        # Convert to radians
        lat_rad = np.deg2rad(lat)
        lon_rad = np.deg2rad(lon)
        
        # Stereographic projection formulas
        k = 2 * self.R / (1 + np.sin(lat_rad))
        x = k * np.cos(lat_rad) * np.cos(lon_rad)
        y = k * np.cos(lat_rad) * np.sin(lon_rad)
        
        return x, y
    
    def inverse(self, x, y):
        """
        Inverse stereographic projection: plane -> sphere.
        
        Args:
            x: X-coordinate in stereographic plane
            y: Y-coordinate in stereographic plane
            
        Returns:
            (lat, lon): Latitude and longitude in degrees
        """
        # Inverse stereographic projection formulas
        rho = np.sqrt(x**2 + y**2)
        c = 2 * np.arctan2(rho, 2 * self.R)
        
        lat = 90 - np.rad2deg(c)
        lon = np.rad2deg(np.arctan2(y, x))
        
        return lat, lon
    
    @staticmethod
    @jit
    def jax_forward(lat, lon, R=6371000.0):
        """JAX-optimized forward projection for GPU acceleration."""
        lat_rad = jnp.deg2rad(lat)
        lon_rad = jnp.deg2rad(lon)
        
        k = 2 * R / (1 + jnp.sin(lat_rad))
        x = k * jnp.cos(lat_rad) * jnp.cos(lon_rad)
        y = k * jnp.cos(lat_rad) * jnp.sin(lon_rad)
        
        return x, y
    
    @staticmethod
    @jit  
    def jax_inverse(x, y, R=6371000.0):
        """JAX-optimized inverse projection for GPU acceleration."""
        rho = jnp.sqrt(x**2 + y**2)
        c = 2 * jnp.arctan2(rho, 2 * R)
        
        lat = 90 - jnp.rad2deg(c)
        lon = jnp.rad2deg(jnp.arctan2(y, x))
        
        return lat, lon