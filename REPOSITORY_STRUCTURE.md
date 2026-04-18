# ORCA Grid Builder - Repository Structure

## Organized Repository Layout

```
orca-grid-builder/
├── src/
│   └── orca_grid/
│       ├── __init__.py          # Main package
│       ├── cli.py               # Command-line interface
│       ├── __main__.py           # Main grid builder
│       ├── grid_generator.py     # Core generation algorithms
│       ├── stereographic.py      # Projection utilities
│       ├── netcdf_writer.py      # NetCDF output
│       ├── plotting.py           # Visualization tools
│       ├── abstract_base.py      # Modular architecture
│       ├── nemo_implementation.py # NEMO-specific
│       ├── veros_adapter.py      # Veros adapter
│       └── modular_factory.py    # Factory pattern
│
├── output/
│   ├── grids/                  # Generated grid files
│   │   ├── 2deg_grid.nc         # 2° resolution grid
│   │   ├── 1deg_grid.nc         # 1° resolution grid
│   │   ├── 0.5deg_grid.nc        # 0.5° resolution grid
│   │   ├── 0.25deg_grid.nc       # 0.25° resolution grid
│   │   └── ...                   # Other example grids
│   │
│   ├── plots/                  # Visualization plots
│   │   ├── 1deg_grid_lon.png    # Longitude plot
│   │   ├── 1deg_grid_lat.png    # Latitude plot
│   │   ├── 1deg_scale_factors_e1t.png  # Zonal scale factors
│   │   ├── 1deg_scale_factors_e2t.png  # Meridional scale factors
│   │   ├── staggered_points.png  # Staggered grid visualization
│   │   ├── grid_comparison.png   # Resolution comparison
│   │   └── ...                   # Plots for all resolutions
│   │
│   ├── validation/              # Validation outputs
│   │   ├── validation_report.json  # Validation results
│   │   └── ...                   # Other validation files
│   │
│   └── examples/               # Example scripts
│       ├── comprehensive_example.py  # Full feature demo
│       ├── example.py                # Basic usage example
│       └── generate_plots.py          # Plot generation script
│
├── pdf/                        # Reference documents
│   ├── Madec-Imbard-1996.pdf    # Original paper
│   └── NEMO_manual.pdf          # NEMO reference
│
├── data/                       # Reference data
│   └── domain_cfg.nc            # NEMO reference grid
│
├── docs/                       # Documentation
│   ├── specs.md                # Technical specifications
│   ├── plan.md                 # Development plan
│   └── IMPLEMENTATION_SUMMARY.md # Final summary
│
├── README.md                   # Main documentation
├── .gitignore                  # Git ignore rules
└── .opencode/                   # Development tools
```

## Key Features of the Organization

### 1. Clean Source Code Structure
- All Python modules in `src/orca_grid/`
- Clear separation of concerns
- Modular design for easy extension

### 2. Organized Output Directory
- **`output/grids/`**: All generated NetCDF grid files
- **`output/plots/`**: All visualization plots
- **`output/validation/`**: Validation reports and outputs
- **`output/examples/`**: Example scripts and demonstrations

### 3. Separate Data and Documentation
- **`pdf/`**: Reference papers and manuals
- **`data/`**: Reference grid files
- **`docs/`**: Technical documentation

### 4. Professional Documentation
- Comprehensive `README.md` with examples
- Technical specifications
- Development plan
- Implementation summary

## Benefits of This Structure

1. **Clean Repository**: No clutter in root directory
2. **Easy Navigation**: Clear separation of code, outputs, and docs
3. **Professional**: Follows best practices for Python projects
4. **Maintainable**: Easy to add new features and outputs
5. **Scalable**: Can handle many grid files and plots

## Usage with Organized Structure

```python
# Generate grids (saved to output/grids/)
from orca_grid import ORCAGridBuilder
builder = ORCAGridBuilder(resolution="1deg")
builder.write_netcdf("output/grids/my_grid.nc")

# Generate plots (saved to output/plots/)
from orca_grid.plotting import plot_grid_structure
plot_grid_structure("output/grids/my_grid.nc", 
                   "My Grid", 
                   "output/plots/my_grid")

# Run examples
python output/examples/comprehensive_example.py
```

## Repository Size Management

The organized structure helps manage repository size:
- Generated files are in `output/` (can be excluded from version control if needed)
- Source code remains clean and lightweight
- Easy to clean up outputs: `rm -rf output/*`

## Best Practices Followed

1. **Separation of Concerns**: Code, data, outputs, and docs are separate
2. **Consistent Naming**: Clear and descriptive file names
3. **Logical Grouping**: Related files are grouped together
4. **Documentation**: Comprehensive docs at all levels
5. **Maintainability**: Easy to understand and navigate structure