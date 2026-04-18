"""
NEMO-specific implementation of the ocean grid generator.

This module implements the NEMO ORCA grid generator using the
modular architecture defined in abstract_base.py
"""

import numpy as np
from .abstract_base import OceanGridGenerator, OceanModelAdapter, GridValidationInterface
from .grid_generator import ORCAGridGenerator
from .netcdf_writer import NEMONetCDFWriter

class NEMOGridGenerator(OceanGridGenerator):
    """
    NEMO-specific implementation of the ORCA grid generator.
    
    This class implements the OceanGridGenerator interface for NEMO ORCA grids.
    """
    
    def __init__(self, resolution="1deg"):
        """Initialize NEMO ORCA grid generator."""
        self.resolution = resolution
        self.orca_generator = ORCAGridGenerator(resolution)
        self.netcdf_writer = NEMONetCDFWriter(resolution)
    
    def generate_grid(self, use_jax=False):
        """
        Generate NEMO ORCA grid.
        
        Args:
            use_jax: Whether to use JAX optimization
            
        Returns:
            grid_data: Dictionary containing NEMO grid data
        """
        # Generate the grid using the ORCA generator
        if use_jax:
            spherical_grid = self.orca_generator.generate_spherical_grid_jax()
        else:
            spherical_grid = self.orca_generator.generate_spherical_grid()
        
        # Calculate scale factors
        if use_jax:
            e1t, e2t = self.orca_generator.calculate_scale_factors_jax(
                spherical_grid['lat_t'], spherical_grid['lon_t']
            )
        else:
            e1t, e2t = self.orca_generator.calculate_scale_factors(
                spherical_grid['lat_t'], spherical_grid['lon_t']
            )
        
        # Create NEMO-specific grid data structure
        grid_data = {
            'model': 'NEMO',
            'grid_type': 'ORCA',
            'resolution': self.resolution,
            'coordinates': {
                't': {'lat': spherical_grid['lat_t'], 'lon': spherical_grid['lon_t']},
                'u': {'lat': spherical_grid['lat_u'], 'lon': spherical_grid['lon_u']},
                'v': {'lat': spherical_grid['lat_v'], 'lon': spherical_grid['lon_v']},
                'f': {'lat': spherical_grid['lat_f'], 'lon': spherical_grid['lon_f']}
            },
            'scale_factors': {
                'e1t': e1t, 'e2t': e2t
            },
            'metadata': {
                'jpiglo': 362,
                'jpjglo': 332,
                'jpkglo': 75,
                'jperio': 6
            }
        }
        
        return grid_data
    
    def get_grid_type(self):
        """Get the type of grid generated."""
        return "ORCA"
    
    def get_resolution(self):
        """Get the resolution of the generated grid."""
        return self.resolution
    
    def write_netcdf(self, filename="domain_cfg.nc"):
        """
        Write grid to NEMO-compliant NetCDF file.
        
        Args:
            filename: Output filename
            
        Returns:
            filename: Path to created file
        """
        # Generate grid data in the format expected by NetCDF writer
        grid_data = self.generate_grid()
        
        # Convert to NetCDF writer format
        netcdf_data = {
            'nav_lon': grid_data['coordinates']['t']['lon'],
            'nav_lat': grid_data['coordinates']['t']['lat'],
            'glamt': np.tile(grid_data['coordinates']['t']['lon'][np.newaxis, :, :], (1, 1, 1)),
            'gphit': np.tile(grid_data['coordinates']['t']['lat'][np.newaxis, :, :], (1, 1, 1)),
            'glamu': np.tile(grid_data['coordinates']['u']['lon'][np.newaxis, :, :], (1, 1, 1)),
            'gphiu': np.tile(grid_data['coordinates']['u']['lat'][np.newaxis, :, :], (1, 1, 1)),
            'glamv': np.tile(grid_data['coordinates']['v']['lon'][np.newaxis, :, :], (1, 1, 1)),
            'gphiv': np.tile(grid_data['coordinates']['v']['lat'][np.newaxis, :, :], (1, 1, 1)),
            'glamf': np.tile(grid_data['coordinates']['f']['lon'][np.newaxis, :, :], (1, 1, 1)),
            'gphif': np.tile(grid_data['coordinates']['f']['lat'][np.newaxis, :, :], (1, 1, 1)),
            'e1t': np.tile(grid_data['scale_factors']['e1t'][np.newaxis, :, :], (1, 1, 1)),
            'e2t': np.tile(grid_data['scale_factors']['e2t'][np.newaxis, :, :], (1, 1, 1))
        }
        
        return self.netcdf_writer.write_netcdf(netcdf_data, filename)

class NEMOAdapter(OceanModelAdapter):
    """
    Adapter for converting between generic grid format and NEMO format.
    """
    
    def __init__(self, grid_generator=None):
        """Initialize NEMO adapter."""
        if grid_generator is None:
            grid_generator = NEMOGridGenerator()
        self.grid_generator = grid_generator
    
    def to_model_format(self, grid_data):
        """
        Convert generic grid data to NEMO format.
        
        Args:
            grid_data: Generic grid data dictionary
            
        Returns:
            nemo_data: Data in NEMO-specific format
        """
        # This would convert from a generic grid format to NEMO format
        # For now, we assume the input is already in a compatible format
        return {
            'model': 'NEMO',
            'grid_data': grid_data,
            'format': 'NEMO_ORCA'
        }
    
    def from_model_format(self, nemo_data):
        """
        Convert NEMO-specific data to generic format.
        
        Args:
            nemo_data: NEMO-specific grid data
            
        Returns:
            grid_data: Generic grid data dictionary
        """
        # This would convert from NEMO format to generic format
        return nemo_data.get('grid_data', {})
    
    def get_model_name(self):
        """Get the name of the ocean model."""
        return "NEMO"

class NEMOValidator(GridValidationInterface):
    """
    Validation interface for NEMO grids.
    """
    
    def __init__(self):
        """Initialize NEMO validator."""
        self.criteria = [
            'dimension_consistency',
            'variable_presence', 
            'coordinate_range',
            'scale_factor_positivity',
            'nemo_attribute_compliance'
        ]
    
    def validate(self, generated_grid, reference_grid=None):
        """
        Validate a NEMO grid.
        
        Args:
            generated_grid: Grid to validate
            reference_grid: Optional reference grid for comparison
            
        Returns:
            validation_report: Dictionary containing validation results
        """
        report = {
            'model': 'NEMO',
            'validation_passed': False,
            'checks': {},
            'errors': [],
            'warnings': []
        }
        
        # Check that required coordinates are present
        required_coords = ['t', 'u', 'v', 'f']
        for coord_type in required_coords:
            if coord_type in generated_grid.get('coordinates', {}):
                report['checks'][f'coordinates_{coord_type}'] = True
            else:
                report['checks'][f'coordinates_{coord_type}'] = False
                report['errors'].append(f'Missing {coord_type}-point coordinates')
        
        # Check scale factors
        if 'scale_factors' in generated_grid:
            report['checks']['scale_factors_present'] = True
            # Check that scale factors are positive
            e1t = generated_grid['scale_factors'].get('e1t')
            e2t = generated_grid['scale_factors'].get('e2t')
            if e1t is not None and e2t is not None:
                if np.all(e1t > 0) and np.all(e2t > 0):
                    report['checks']['scale_factors_positive'] = True
                else:
                    report['checks']['scale_factors_positive'] = False
                    report['errors'].append('Scale factors contain non-positive values')
        else:
            report['checks']['scale_factors_present'] = False
            report['errors'].append('Scale factors missing')
        
        # Overall validation result
        report['validation_passed'] = len(report['errors']) == 0
        
        return report
    
    def get_validation_criteria(self):
        """Get the validation criteria used."""
        return self.criteria