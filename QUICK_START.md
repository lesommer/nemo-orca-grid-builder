# 🚀 Quick Start Guide

## The Fastest Way to Get Started

### 1. Install Dependencies (5 minutes)

```bash
# Create and activate conda environment
conda create -n orca_env python=3.9 -y
conda activate orca_env

# Install all dependencies via conda (no compilation!)
conda install -c conda-forge numpy xarray netcdf4 matplotlib -y
```

### 2. Install ORCA Grid Builder (1 minute)

```bash
# Clone the repository (if you haven't already)
git clone https://github.com/lesommer/nemo-orca-grid-builder.git
cd orca-grid-builder

# Install in development mode
pip install -e .
```

### 3. Test It Works (30 seconds)

```bash
# Test basic functionality
python -c "
from orca_grid.validate_grid import validate_grid
print('✅ Validation module works')
"

# Generate a grid
python -c "
from orca_grid import ORCAGridBuilder
builder = ORCAGridBuilder(resolution='1deg')
builder.write_netcdf('my_first_grid.nc')
print('✅ Grid generation works!')
"
```

## 🎯 You're Done!

The library is now ready to use. All JAX dependencies have been removed, so it's stable and fast.

## 📚 Common Tasks

### Generate a Grid
```python
from orca_grid import ORCAGridBuilder

# Create builder for 1° resolution
builder = ORCAGridBuilder(resolution="1deg")

# Generate and save grid
grid_data = builder.generate_grid()
builder.write_netcdf("domain_cfg.nc")
```

### Validate a Grid
```python
from orca_grid.validate_grid import validate_grid

report = validate_grid("domain_cfg.nc")
print(f"Validation passed: {report['validation_passed']}")
```

### Plot a Grid
```python
from orca_grid.plotting import plot_grid_structure

fig = plot_grid_structure("domain_cfg.nc", "My ORCA Grid", "output_plot")
```

### Use CLI
```bash
# Generate 1° grid
python -m orca_grid 1deg my_grid.nc

# Generate 0.5° grid
python -m orca_grid 0.5deg high_res_grid.nc
```

## 🛠 Troubleshooting

### "Building wheel for netCDF4 failed"
**Solution:** Use conda instead of pip for netCDF4:
```bash
conda install -c conda-forge netcdf4
```

### "ModuleNotFoundError: No module named 'orca_grid'"
**Solution:** Activate your conda environment:
```bash
conda activate orca_env
```

### CLI not working
**Solution:** Test it directly:
```bash
python -c "
import sys
sys.path.insert(0, 'src')
from orca_grid.cli import main
sys.argv = ['orca_grid', '1deg', 'test.nc']
main()
"
```

## 📖 What's Changed

- **✅ No more JAX** - Removed all JAX dependencies
- **✅ Faster installation** - Only 4 core dependencies
- **✅ More stable** - No GPU driver issues
- **✅ Better compatibility** - Works on all Python 3.6+ systems

## 🎉 Enjoy!

You now have a fully functional ORCA grid generation library that:
- Generates NEMO-compliant ORCA grids
- Validates grid files
- Creates beautiful visualizations
- Works on any system with Python

**Need help?** Check the [INSTALL_GUIDE.md](INSTALL_GUIDE.md) for detailed instructions.