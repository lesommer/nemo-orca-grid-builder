"""
Grid validation example.

NOTE: This example demonstrates validation functionality but may require
additional setup or dependencies to run successfully.
"""
from orca_grid import ORCAGridBuilder
from orca_grid.validate_grid import validate_grid

def validation_example():
    # Generate grid
    builder = ORCAGridBuilder(resolution="1deg")
    builder.write_netcdf("generated_grid.nc")
    
    # Validate (without reference for now)
    report = validate_grid("generated_grid.nc")
    print(f"Validation passed: {report['validation_passed']}")
    print(f"Checks: {report['checks']}")
    if report['errors']:
        print(f"Errors: {report['errors']}")
    if report['warnings']:
        print(f"Warnings: {report['warnings']}")

if __name__ == "__main__":
    validation_example()
