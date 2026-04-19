"""
Modular architecture demonstration.

NOTE: This example demonstrates the modular architecture but may require
additional setup or dependencies to run successfully.
"""
from orca_grid.modular_factory import UnifiedGridBuilder

def demonstrate_modular_architecture():
    # NEMO example
    nemo_builder = UnifiedGridBuilder(model_name="nemo", resolution="1deg")
    nemo_grid = nemo_builder.generate_grid()
    print(f"Generated NEMO grid: {nemo_builder.get_model_info()}")
    
    # Veros example
    veros_builder = UnifiedGridBuilder(model_name="veros", resolution="1deg")
    veros_grid = veros_builder.generate_grid()
    print(f"Generated Veros grid: {veros_builder.get_model_info()}")

if __name__ == "__main__":
    demonstrate_modular_architecture()
