"""
Grid generator factory and modular architecture demonstration.

This module shows how to use the modular architecture to support
multiple ocean models through a unified interface.
"""

import numpy as np
from .abstract_base import OceanGridGenerator, OceanModelAdapter
from .nemo_implementation import NEMOGridGenerator, NEMOAdapter
from .veros_adapter import VerosAdapter

class GridGeneratorFactory:
    """
    Factory for creating grid generators for different ocean models.
    
    This demonstrates the modular architecture that allows the same
    core grid generation code to be used with different ocean models.
    """
    
    @staticmethod
    def create_generator(model_name="nemo", resolution="1deg"):
        """
        Create a grid generator for the specified ocean model.
        
        Args:
            model_name: Name of the ocean model ('nemo', 'veros', etc.)
            resolution: Grid resolution
            
        Returns:
            grid_generator: Grid generator instance
        """
        model_name = model_name.lower()
        
        if model_name == "nemo":
            return NEMOGridGenerator(resolution=resolution)
        elif model_name == "veros":
            # For Veros, we can use the NEMO generator and adapt the output
            nemo_generator = NEMOGridGenerator(resolution=resolution)
            return VerosAdapter(grid_generator=nemo_generator)
        else:
            raise ValueError(f"Unsupported ocean model: {model_name}")
    
    @staticmethod
    def get_available_models():
        """Get list of available ocean models."""
        return ["nemo", "veros"]

class UnifiedGridBuilder:
    """
    Unified interface for generating grids for different ocean models.
    
    This class demonstrates how the modular architecture provides
    a consistent interface regardless of the target ocean model.
    """
    
    def __init__(self, model_name="nemo", resolution="1deg"):
        """Initialize the unified grid builder."""
        self.model_name = model_name.lower()
        self.resolution = resolution
        self.generator = GridGeneratorFactory.create_generator(model_name, resolution)
    
    def generate_grid(self, **kwargs):
        """
        Generate grid for the specified ocean model.
        
        Args:
            **kwargs: Additional arguments passed to the generator
            
        Returns:
            grid_data: Grid data in model-specific format
        """
        if hasattr(self.generator, 'generate_grid'):
            return self.generator.generate_grid(**kwargs)
        else:
            # For adapters, we might need to call a different method
            return self.generator.to_model_format(
                NEMOGridGenerator(self.resolution).generate_grid(**kwargs)
            )
    
    def write_output(self, filename, **kwargs):
        """
        Write grid to output file in model-specific format.
        
        Args:
            filename: Output filename
            **kwargs: Additional arguments
            
        Returns:
            filename: Path to created file
        """
        if self.model_name == "nemo":
            return self.generator.write_netcdf(filename, **kwargs)
        elif self.model_name == "veros":
            # For Veros, we would write to a different format
            grid_data = self.generate_grid(**kwargs)
            return self._write_veros_grid(grid_data, filename)
        else:
            raise NotImplementedError(f"Output writing not implemented for {self.model_name}")
    
    def _write_veros_grid(self, grid_data, filename):
        """Write grid in Veros format (simplified for demonstration)."""
        # In a real implementation, this would write to Veros-specific format
        import json
        
        # Convert numpy arrays to lists for JSON serialization
        def convert_to_serializable(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {k: convert_to_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_serializable(item) for item in obj]
            else:
                return obj
        
        serializable_data = convert_to_serializable(grid_data)
        
        with open(filename, 'w') as f:
            json.dump(serializable_data, f, indent=2)
        return filename
    
    def get_model_info(self):
        """Get information about the target ocean model."""
        if hasattr(self.generator, 'get_model_name'):
            model_name = self.generator.get_model_name()
        else:
            model_name = self.model_name.upper()
        
        return {
            'model': model_name,
            'resolution': self.resolution,
            'grid_type': 'ORCA' if model_name == 'NEMO' else 'Regular',
            'generator': self.generator.__class__.__name__
        }

def demonstrate_modular_architecture():
    """
    Demonstrate the modular architecture with examples.
    
    This function shows how the same core grid generation
    can be used for different ocean models.
    """
    print("Modular Ocean Grid Generator - Architecture Demonstration")
    print("=" * 60)
    
    # Example 1: Generate grid for NEMO
    print("\n1. Generating grid for NEMO ocean model:")
    nemo_builder = UnifiedGridBuilder(model_name="nemo", resolution="1deg")
    nemo_grid = nemo_builder.generate_grid()
    print(f"   Generated NEMO grid with resolution: {nemo_builder.get_model_info()}")
    
    # Example 2: Generate grid for Veros
    print("\n2. Generating grid for Veros ocean model:")
    veros_builder = UnifiedGridBuilder(model_name="veros", resolution="1deg")
    veros_grid = veros_builder.generate_grid()
    print(f"   Generated Veros grid with resolution: {veros_builder.get_model_info()}")
    
    # Example 3: Show available models
    print("\n3. Available ocean models:")
    available_models = GridGeneratorFactory.get_available_models()
    for model in available_models:
        print(f"   - {model.upper()}")
    
    # Example 4: Write outputs
    print("\n4. Writing output files:")
    nemo_output = nemo_builder.write_output("nemo_grid_output.nc")
    veros_output = veros_builder.write_output("veros_grid_output.json")
    print(f"   NEMO output: {nemo_output}")
    print(f"   Veros output: {veros_output}")
    
    print("\n✓ Modular architecture demonstration complete!")
    print("  The same core ORCA grid generation code can be used")
    print("  to generate grids for different ocean models.")

if __name__ == "__main__":
    demonstrate_modular_architecture()