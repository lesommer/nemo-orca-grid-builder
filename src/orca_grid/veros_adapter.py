"""
Veros ocean model adapter.

This module demonstrates how to extend the grid generator
to support the Veros ocean model.
"""

import numpy as np
from .abstract_base import OceanModelAdapter

class VerosAdapter(OceanModelAdapter):
    """
    Adapter for converting between generic grid format and Veros format.
    
    This is a simplified demonstration adapter. A full implementation
    would need to handle Veros-specific grid requirements.
    """
    
    def __init__(self, grid_generator=None):
        """Initialize Veros adapter."""
        self.grid_generator = grid_generator
    
    def to_model_format(self, grid_data):
        """
        Convert generic grid data to Veros format.
        
        Args:
            grid_data: Generic grid data dictionary
            
        Returns:
            veros_data: Data in Veros-specific format
        """
        # Convert to Veros format
        # Veros typically uses simpler grid structures than NEMO
        veros_data = {
            'model': 'Veros',
            'grid': {
                'latitude': grid_data['coordinates']['t']['lat'],
                'longitude': grid_data['coordinates']['t']['lon'],
                'depth': self._create_veros_depth_levels(),
                'dx': grid_data['scale_factors']['e1t'],  # Zonal spacing
                'dy': grid_data['scale_factors']['e2t']   # Meridional spacing
            },
            'metadata': {
                'grid_type': 'regular',  # Veros typically uses regular grids
                'source': 'ORCA_grid_builder',
                'resolution': grid_data.get('resolution', '1deg')
            }
        }
        
        return veros_data
    
    def from_model_format(self, veros_data):
        """
        Convert Veros-specific data to generic format.
        
        Args:
            veros_data: Veros-specific grid data
            
        Returns:
            grid_data: Generic grid data dictionary
        """
        # Convert from Veros format to generic format
        grid_data = {
            'model': 'Veros',
            'grid_type': veros_data['metadata'].get('grid_type', 'regular'),
            'resolution': veros_data['metadata'].get('resolution', '1deg'),
            'coordinates': {
                't': {
                    'lat': veros_data['grid']['latitude'],
                    'lon': veros_data['grid']['longitude']
                }
            },
            'scale_factors': {
                'e1t': veros_data['grid']['dx'],
                'e2t': veros_data['grid']['dy']
            }
        }
        
        return grid_data
    
    def get_model_name(self):
        """Get the name of the ocean model."""
        return "Veros"
    
    def _create_veros_depth_levels(self):
        """
        Create typical Veros depth levels.
        
        Returns:
            depth_levels: Array of depth levels
        """
        # Create a simple set of depth levels typical for Veros
        surface_layers = np.linspace(0, 100, 11)  # 10m resolution near surface
        deep_layers = np.linspace(120, 5000, 50)   # Coarser resolution at depth
        return np.concatenate([surface_layers, deep_layers])