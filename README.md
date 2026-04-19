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

```python
from orca_grid import ORCAGridBuilder

# Create a 1° resolution ORCA grid
builder = ORCAGridBuilder(resolution="1deg")
grid_data = builder.generate_grid()

# Write to NEMO-compliant NetCDF file
builder.write_netcdf("domain_cfg.nc")
```

## License

MIT License

## References

- Madec, G., & Imbard, M. (1996). A global ocean mesh to overcome the North Pole singularity. Climate Dynamics, 12(6), 381-388.

## Support

For issues and questions, please open a GitHub issue or contact the maintainers.

## Roadmap

- Additional resolution options (0.25°, 0.1°)
- Enhanced validation suite
- More ocean model adapters
- Performance optimization
- Web interface for grid generation

## Visualization

The library includes visualization tools to inspect the generated grids:

### Grid Structure Plots

![1° Grid Longitude](output/plots/1deg_grid_lon.png)
*Longitude coordinates for 1° ORCA grid (generated on-demand)*

![1° Grid Latitude](output/plots/1deg_grid_lat.png)  
*Latitude coordinates for 1° ORCA grid (generated on-demand)*

### Scale Factor Plots

![1° Scale Factor e1t](output/plots/1deg_scale_factors_e1t.png)
*Zonal scale factors for 1° ORCA grid (generated on-demand)*

![1° Scale Factor e2t](output/plots/1deg_scale_factors_e2t.png)
*Meridional scale factors for 1° ORCA grid (generated on-demand)*

### Staggered Grid Points

![Arakawa C-Grid](output/plots/staggered_points.png)
*Arakawa C-grid staggered points (T, U, V, F) (generated on-demand)*

### Resolution Comparison

![Grid Comparison](output/plots/grid_comparison.png)
*Comparison of 1° and 2° ORCA grid resolutions (generated on-demand)*

### Generating Your Own Plots

```python
from orca_grid import plot_grid_structure, plot_scale_factors, plot_staggered_points

# Plot a specific grid
plot_grid_structure('output/grids/my_grid.nc', 'My ORCA Grid', 'output/plots/my_grid_plot')
plot_scale_factors('output/grids/my_grid.nc', 'My ORCA Grid', 'output/plots/my_scale_factors')
```

### Generating Grid Files (On-Demand)

Large grid files are not included in version control due to GitHub's 100MB file size limit. Generate them on-demand:

```bash
# Generate example grids
python output/examples/comprehensive_example.py

# Generate visualization plots  
python output/examples/generate_plots.py
```

The plots help visualize:
- Grid coordinate systems
- Scale factor distributions
- Staggered point locations
- Resolution differences
- Grid quality and orthogonality
