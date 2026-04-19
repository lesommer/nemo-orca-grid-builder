# ORCA Grid Builder

A modular Python library for generating global ocean grids following the ORCA grid family conventions, compatible with NEMO and other ocean models.

## Overview

The ORCA Grid Builder implements the semi-analytical method described in Madec & Imbard (1996) for creating global orthogonal curvilinear ocean meshes that avoid the North Pole singularity. The library generates NEMO-compliant NetCDF files and supports extension to other ocean models through a modular architecture.

## Features

- **NEMO ORCA Grid Generation**: Full implementation of the Madec & Imbard (1996) algorithm
- **Multiple Resolutions**: Support for 1°, 0.5°, and other resolutions
- **Optimized NumPy Implementation**: Fast grid generation using vectorized operations
- **Modular Architecture**: Easy extension to other ocean models
- **NEMO Compliance**: Generates NetCDF files compatible with NEMO domain_cfg requirements
- **Comprehensive Validation**: Built-in validation against reference grids

## Installation

```bash
pip install orca-grid-builder
```

Or install from source:

```bash
git clone https://github.com/lesommer/nemo-orca-grid-builder.git
cd orca-grid-builder
pip install .
```

## Quick Start

### Python API

```python
from orca_grid import ORCAGridBuilder

# Create a 1° resolution ORCA grid
builder = ORCAGridBuilder(resolution="1deg")
grid_data = builder.generate_grid()

# Write to NEMO-compliant NetCDF file
builder.write_netcdf("domain_cfg.nc")
```

### Command Line Interface

```bash
# Generate 1° grid
python -m orca_grid 1deg my_grid.nc
```

## License

MIT License

## References

- Madec, G., & Imbard, M. (1996). A global ocean mesh to overcome the North Pole singularity. Climate Dynamics, 12(6), 381-388.
