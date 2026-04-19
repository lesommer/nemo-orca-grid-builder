"""
Main ORCA grid builder module.

This module provides the high-level interface for generating
NEMO-compliant ORCA grids at various resolutions.
"""

import numpy as np
from .grid_generator import ORCAGridGenerator
from .netcdf_writer import NEMONetCDFWriter

class ORCAGridBuilder:
    """
    High-level interface for ORCA grid generation.
    
    This class combines the grid generator and NetCDF writer
    to provide a simple interface for creating NEMO-compliant grids.
    """
    
    def __init__(self, resolution="1deg"):
        """
        Initialize ORCA grid builder.
        
        Args:
            resolution: Grid resolution ('1deg', '0.5deg', etc.)
        """
        self.resolution = resolution
        self.grid_generator = ORCAGridGenerator(resolution)
        self.netcdf_writer = NEMONetCDFWriter(resolution)
    
    def generate_grid(self, use_jax=False):
        """
        Generate the complete ORCA grid with all staggered points.
        
        Args:
            use_jax: Whether to use JAX optimization for GPU acceleration
            
        Returns:
            grid_data: Dictionary containing all grid data
        """
        # Generate spherical grid with all staggered points
        if use_jax:
            spherical_grid = self.grid_generator.generate_spherical_grid_jax()
        else:
            spherical_grid = self.grid_generator.generate_spherical_grid()
        
        # Calculate scale factors for T-points
        if use_jax:
            e1t, e2t = self.grid_generator.calculate_scale_factors_jax(
                spherical_grid['lat_t'], spherical_grid['lon_t']
            )
        else:
            e1t, e2t = self.grid_generator.calculate_scale_factors(
                spherical_grid['lat_t'], spherical_grid['lon_t']
            )
        
        # Calculate scale factors for other point types (simplified for now)
        e1u, e2u = self._calculate_staggered_scale_factors(e1t, e2t, 'u')
        e1v, e2v = self._calculate_staggered_scale_factors(e1t, e2t, 'v')
        e1f, e2f = self._calculate_staggered_scale_factors(e1t, e2t, 'f')
        
        # Create grid data dictionary
        grid_data = {
            'nav_lon': spherical_grid['lon_t'],
            'nav_lat': spherical_grid['lat_t'],
            # T-point coordinates
            'glamt': np.tile(spherical_grid['lon_t'][np.newaxis, :, :], (1, 1, 1)),
            'gphit': np.tile(spherical_grid['lat_t'][np.newaxis, :, :], (1, 1, 1)),
            # U-point coordinates
            'glamu': np.tile(spherical_grid['lon_u'][np.newaxis, :, :], (1, 1, 1)),
            'gphiu': np.tile(spherical_grid['lat_u'][np.newaxis, :, :], (1, 1, 1)),
            # V-point coordinates
            'glamv': np.tile(spherical_grid['lon_v'][np.newaxis, :, :], (1, 1, 1)),
            'gphiv': np.tile(spherical_grid['lat_v'][np.newaxis, :, :], (1, 1, 1)),
            # F-point coordinates
            'glamf': np.tile(spherical_grid['lon_f'][np.newaxis, :, :], (1, 1, 1)),
            'gphif': np.tile(spherical_grid['lat_f'][np.newaxis, :, :], (1, 1, 1)),
            # Scale factors for all point types
            'e1t': np.tile(e1t[np.newaxis, :, :], (1, 1, 1)),
            'e2t': np.tile(e2t[np.newaxis, :, :], (1, 1, 1)),
            'e1u': np.tile(e1u[np.newaxis, :, :], (1, 1, 1)),
            'e2u': np.tile(e2u[np.newaxis, :, :], (1, 1, 1)),
            'e1v': np.tile(e1v[np.newaxis, :, :], (1, 1, 1)),
            'e2v': np.tile(e2v[np.newaxis, :, :], (1, 1, 1)),
            'e1f': np.tile(e1f[np.newaxis, :, :], (1, 1, 1)),
            'e2f': np.tile(e2f[np.newaxis, :, :], (1, 1, 1)),
        }
        
        return grid_data
    
    def _calculate_staggered_scale_factors(self, e1t, e2t, point_type):
        """
        Calculate scale factors for staggered points.
        
        Args:
            e1t, e2t: Scale factors at T-points
            point_type: 'u', 'v', or 'f' for different staggering
            
        Returns:
            (e1, e2): Scale factors at staggered points
        """
        if point_type == 'u':  # U-points
            e1u = (e1t[:, :-1] + e1t[:, 1:]) / 2
            e2u = (e2t[:, :-1] + e2t[:, 1:]) / 2
            e1u = np.hstack([e1u, e1u[:, -1:]])
            e2u = np.hstack([e2u, e2u[:, -1:]])
            return e1u, e2u
            
        elif point_type == 'v':  # V-points
            e1v = (e1t[:-1, :] + e1t[1:, :]) / 2
            e2v = (e2t[:-1, :] + e2t[1:, :]) / 2
            e1v = np.vstack([e1v[0:1, :], e1v])
            e2v = np.vstack([e2v[0:1, :], e2v])
            return e1v, e2v
            
        else:  # point_type == 'f' (F-points)
            e1f = (e1t[:-1, :-1] + e1t[1:, 1:]) / 2
            e2f = (e2t[:-1, :-1] + e2t[1:, 1:]) / 2
            e1f = np.vstack([e1f[0:1, :], e1f])
            e1f = np.hstack([e1f, e1f[:, -1:]])
            e2f = np.vstack([e2f[0:1, :], e2f])
            e2f = np.hstack([e2f, e2f[:, -1:]])
            return e1f, e2f
    
    def write_netcdf(self, filename="domain_cfg.nc", use_jax=False):
        """
        Generate grid and write to NEMO-compliant NetCDF file.
        
        Args:
            filename: Output filename
            use_jax: Whether to use JAX optimization
            
        Returns:
            filename: Path to created file
        """
        # Generate grid data
        grid_data = self.generate_grid(use_jax=use_jax)
        
        # Write to NetCDF
        return self.netcdf_writer.write_netcdf(grid_data, filename)

    def generate_and_validate(self, reference_file=None):
        """
        Generate grid and validate against reference file.
        
        Args:
            reference_file: Optional path to reference NetCDF file
            
        Returns:
            validation_report: Dictionary containing validation results
        """
        # Generate grid data
        grid_data = self.generate_grid()
        
        # Write to temporary file
        temp_file = "temp_generated.nc"
        self.write_netcdf(temp_file)
        
        # Validate using the validation module
        from .validate_grid import validate_grid
        report = validate_grid(temp_file, reference_file)
        
        # Clean up
        import os
        os.remove(temp_file)
        
        return {
            'status': 'generated_and_validated',
            'grid_data': grid_data,
            'validation_report': report
        }