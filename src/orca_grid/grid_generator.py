"""
ORCA grid generation using the Madec & Imbard (1996) method.

This module implements the semi-analytical approach for creating
global orthogonal curvilinear ocean meshes that avoid the North Pole
singularity by using a tripolar grid configuration.
"""

import numpy as np
import jax.numpy as jnp
from jax import jit, grad
from .stereographic import StereographicProjection

class ORCAGridGenerator:
    """
    ORCA grid generator implementing the Madec & Imbard (1996) algorithm.
    
    The grid construction involves:
    1. Defining mesh parallels as embedded circles in stereographic plane
    2. Computing orthogonal mesh meridians numerically
    3. Projecting onto sphere
    4. Calculating scale factors and metrics
    """
    
    def __init__(self, resolution="1deg"):
        """
        Initialize ORCA grid generator.
        
        Args:
            resolution: Grid resolution ('1deg', '0.5deg', '0.25deg', etc.)
        """
        self.resolution = resolution
        self.projection = StereographicProjection()
        self.grid_params = self._get_resolution_params()
        
    def _get_resolution_params(self):
        """Get parameters for different resolutions."""
        params = {
            "1deg": {
                "nx": 360,      # Zonal points
                "ny": 331,      # Meridional points  
                "equator_lat": 0.0,  # Equator latitude
                "npole_lat": 80.0,   # Approximate north pole latitude
                "npole_lon": -60.0,  # North pole longitude (Canada)
                "spole_lat": -80.0,  # South pole latitude
                "spole_lon": 120.0   # South pole longitude (Russia)
            },
            "0.5deg": {
                "nx": 720,
                "ny": 661,
                "equator_lat": 0.0,
                "npole_lat": 80.0,
                "npole_lon": -60.0,
                "spole_lat": -80.0,
                "spole_lon": 120.0
            }
        }
        return params.get(self.resolution, params["1deg"])
    
    def _generate_j_curves(self):
        """
        Generate J-curves (mesh parallels) as embedded circles.
        
        Returns:
            j_curves: Array of (x, y) coordinates for each J-curve
        """
        # Parameters for embedded circles
        nx, ny = self.grid_params["nx"], self.grid_params["ny"]
        
        # Create J-curve parameters - this is simplified for now
        # In the full implementation, this would use the analytical functions
        # f(j) and g(j) from Madec & Imbard (1996)
        j_values = np.linspace(0, ny-1, ny)
        
        # Simplified: create concentric circles for demonstration
        # Real implementation would use the proper embedded circle equations
        radii = np.linspace(1.0, 0.1, ny) * 1e6  # Scaled for demonstration
        
        j_curves = []
        for radius in radii:
            theta = np.linspace(0, 2*np.pi, nx)
            x = radius * np.cos(theta)
            y = radius * np.sin(theta)
            j_curves.append(np.column_stack((x, y)))
        
        return np.array(j_curves)
    
    def _compute_i_curves(self, j_curves):
        """
        Compute I-curves (mesh meridians) orthogonal to J-curves.
        
        Args:
            j_curves: Array of J-curve coordinates
            
        Returns:
            i_curves: Array of (x, y) coordinates for each I-curve
        """
        # This is a simplified version - the real implementation would
        # solve the differential equation numerically
        nx, ny = self.grid_params["nx"], self.grid_params["ny"]
        
        # For now, create radial lines as placeholder
        i_curves = []
        for i in range(nx):
            theta = 2 * np.pi * i / nx
            r_values = np.linspace(0.1, 1.0, ny) * 1e6
            x = r_values * np.cos(theta)
            y = r_values * np.sin(theta)
            i_curves.append(np.column_stack((x, y)))
        
        return np.array(i_curves)
    
    def generate_polar_grid(self):
        """
        Generate the grid in stereographic polar coordinates.
        
        Returns:
            grid: Dictionary containing polar coordinates for all grid points
        """
        # Generate J-curves (parallels)
        j_curves = self._generate_j_curves()
        
        # Compute I-curves (meridians) 
        i_curves = self._compute_i_curves(j_curves)
        
        # Create full grid by intersecting I and J curves
        nx, ny = self.grid_params["nx"], self.grid_params["ny"]
        grid_points = np.zeros((ny, nx, 2))
        
        # This is simplified - real implementation would properly intersect curves
        for j in range(ny):
            for i in range(nx):
                # Use average of nearby points for demonstration
                grid_points[j, i, 0] = (i_curves[i][j, 0] + j_curves[j][i, 0]) / 2
                grid_points[j, i, 1] = (i_curves[i][j, 1] + j_curves[j][i, 1]) / 2
        
        return {
            'x_polar': grid_points[..., 0],
            'y_polar': grid_points[..., 1],
            'j_curves': j_curves,
            'i_curves': i_curves
        }
    
    def polar_to_spherical(self, x_polar, y_polar):
        """
        Convert polar plane coordinates to spherical coordinates.
        
        Args:
            x_polar: X-coordinates in stereographic plane
            y_polar: Y-coordinates in stereographic plane
            
        Returns:
            (lat, lon): Latitude and longitude in degrees
        """
        # Use the inverse stereographic projection
        lat, lon = self.projection.inverse(x_polar, y_polar)
        return lat, lon
    
    def generate_spherical_grid(self):
        """
        Generate the complete spherical grid.
        
        Returns:
            grid: Dictionary containing spherical coordinates and metrics
        """
        # Generate polar grid
        polar_grid = self.generate_polar_grid()
        
        # Convert to spherical coordinates
        lat, lon = self.polar_to_spherical(polar_grid['x_polar'], polar_grid['y_polar'])
        
        return {
            'lat': lat,
            'lon': lon,
            'x_polar': polar_grid['x_polar'],
            'y_polar': polar_grid['y_polar']
        }
    
    def calculate_scale_factors(self, lat, lon):
        """
        Calculate grid scale factors (e1, e2).
        
        Args:
            lat: Latitude coordinates (2D array)
            lon: Longitude coordinates (2D array)
            
        Returns:
            (e1, e2): Zonal and meridional scale factors
        """
        # This is a placeholder - real implementation would calculate
        # proper scale factors based on grid spacing
        ny, nx = lat.shape
        
        # Create simplified scale factors (constant for now)
        e1 = np.ones((ny, nx)) * 111000.0  # Approx 1° in meters
        e2 = np.ones((ny, nx)) * 111000.0  # Approx 1° in meters
        
        # Add some variation to simulate real grid
        lat_rad = np.deg2rad(lat)
        e1 *= 1.0 + 0.1 * np.sin(lat_rad)
        e2 *= 1.0 + 0.1 * np.cos(lat_rad)
        
        return e1, e2
    
    @staticmethod
    @jit
    def jax_coriolis(lat):
        """
        Calculate Coriolis parameter using JAX for GPU acceleration.
        
        Args:
            lat: Latitude in degrees
            
        Returns:
            f: Coriolis parameter (s⁻¹)
        """
        omega = 7.2921e-5  # Earth's angular velocity (rad/s)
        return 2 * omega * jnp.sin(jnp.deg2rad(lat))