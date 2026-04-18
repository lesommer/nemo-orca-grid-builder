"""
Abstract base classes for ocean grid generation.

This module provides the foundation for a modular grid generation system
that can support multiple ocean models (NEMO, Veros, etc.)
"""

from abc import ABC, abstractmethod
import numpy as np

class OceanGridGenerator(ABC):
    """
    Abstract base class for ocean grid generators.
    
    This class defines the interface that all ocean grid generators must implement
    to ensure compatibility with the modular architecture.
    """
    
    @abstractmethod
    def __init__(self, resolution="1deg"):
        """Initialize the grid generator with specified resolution."""
        pass
    
    @abstractmethod
    def generate_grid(self):
        """
        Generate the ocean grid.
        
        Returns:
            grid_data: Dictionary containing grid coordinates and metrics
        """
        pass
    
    @abstractmethod
    def get_grid_type(self):
        """
        Get the type of grid generated.
        
        Returns:
            str: Grid type (e.g., "ORCA", "tripolar", "regular", etc.)
        """
        pass
    
    @abstractmethod
    def get_resolution(self):
        """
        Get the resolution of the generated grid.
        
        Returns:
            str: Resolution specification
        """
        pass

class OceanModelAdapter(ABC):
    """
    Abstract base class for ocean model adapters.
    
    Adapters convert between the generic grid format and model-specific formats.
    """
    
    @abstractmethod
    def __init__(self, grid_generator):
        """Initialize the adapter with a grid generator."""
        pass
    
    @abstractmethod
    def to_model_format(self, grid_data):
        """
        Convert generic grid data to model-specific format.
        
        Args:
            grid_data: Generic grid data dictionary
            
        Returns:
            model_specific_data: Data in model-specific format
        """
        pass
    
    @abstractmethod
    def from_model_format(self, model_data):
        """
        Convert model-specific data to generic format.
        
        Args:
            model_data: Model-specific grid data
            
        Returns:
            grid_data: Generic grid data dictionary
        """
        pass
    
    @abstractmethod
    def get_model_name(self):
        """
        Get the name of the ocean model.
        
        Returns:
            str: Model name (e.g., "NEMO", "Veros", "MOM6", etc.)
        """
        pass

class GridValidationInterface(ABC):
    """
    Abstract base class for grid validation.
    
    Provides interface for validating generated grids against reference data.
    """
    
    @abstractmethod
    def validate(self, generated_grid, reference_grid=None):
        """
        Validate a generated grid.
        
        Args:
            generated_grid: Grid to validate
            reference_grid: Optional reference grid for comparison
            
        Returns:
            validation_report: Dictionary containing validation results
        """
        pass
    
    @abstractmethod
    def get_validation_criteria(self):
        """
        Get the validation criteria used.
        
        Returns:
            list: List of validation criteria
        """
        pass