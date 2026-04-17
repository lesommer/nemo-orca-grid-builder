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
    
    def generate_grid(self):
        """
        Generate the complete ORCA grid.
        
        Returns:
            grid_data: Dictionary containing all grid data
        """
        # Generate spherical grid
        spherical_grid = self.grid_generator.generate_spherical_grid()
        
        # Calculate scale factors
        e1, e2 = self.grid_generator.calculate_scale_factors(
            spherical_grid['lat'], spherical_grid['lon']
        )
        
        # Create grid data dictionary
        grid_data = {
            'nav_lon': spherical_grid['lon'],
            'nav_lat': spherical_grid['lat'],
            # T-point coordinates (same as nav for now)
            'glamt': np.tile(spherical_grid['lon'][np.newaxis, :, :], (1, 1, 1)),
            'gphit': np.tile(spherical_grid['lat'][np.newaxis, :, :], (1, 1, 1)),
            # Scale factors
            'e1t': np.tile(e1[np.newaxis, :, :], (1, 1, 1)),
            'e2t': np.tile(e2[np.newaxis, :, :], (1, 1, 1)),
            # Add other required variables (will be filled by NetCDF writer)
        }
        
        return grid_data
    
    def write_netcdf(self, filename="domain_cfg.nc"):
        """
        Generate grid and write to NEMO-compliant NetCDF file.
        
        Args:
            filename: Output filename
            
        Returns:
            filename: Path to created file
        """
        # Generate grid data
        grid_data = self.generate_grid()
        
        # Write to NetCDF
        return self.netcdf_writer.write_netcdf(grid_data, filename)
    
    def generate_and_validate(self, reference_file="data/domain_cfg.nc"):
        """
        Generate grid and validate against reference file.
        
        Args:
            reference_file: Path to reference NetCDF file
            
        Returns:
            validation_report: Dictionary containing validation results
        """
        # This would be implemented in a future version
        # For now, just generate the grid
        grid_data = self.generate_grid()
        
        return {
            'status': 'generated',
            'grid_data': grid_data,
            'validation': 'not_implemented'
        }