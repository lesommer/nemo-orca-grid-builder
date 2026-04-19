# ORCA Grid Builder Installation Guide

## 🚀 Quick Start (Recommended)

### Using Conda (Best for most users)
```bash
# Create and activate a conda environment
conda create -n orca_env python=3.9
conda activate orca_env

# Install dependencies via conda (avoids compilation issues)
conda install -c conda-forge numpy xarray netcdf4 matplotlib

# Install the package
pip install -e .

# Test installation
python -c "from orca_grid import ORCAGridBuilder; print('✓ Installation successful')"
```

### Using Pip (Alternative)
```bash
# Install system dependencies first (Linux/macOS)
# On Ubuntu/Debian:
sudo apt-get install libnetcdf-dev libhdf5-dev

# On macOS (with Homebrew):
brew install netcdf hdf5

# Then install Python packages
pip install numpy xarray matplotlib

# Install netCDF4 via conda to avoid compilation
conda install -c conda-forge netcdf4

# Install the package
pip install -e .
```

## 🛠️ Installation Methods

### Method 1: Conda Environment (Recommended) ✅
```bash
conda create -n orca_env python=3.9
conda activate orca_env
conda install -c conda-forge numpy xarray netcdf4 matplotlib
pip install -e .
```

**Why this works best:**
- Conda provides pre-compiled netCDF4 binaries
- No compilation required
- All dependencies guaranteed compatible
- Works on Windows, macOS, and Linux

### Method 2: Virtual Environment with System Packages
```bash
python -m venv orca_venv
source orca_venv/bin/activate  # Linux/macOS
# or: orca_venv\Scripts\activate  # Windows

# Install system dependencies
# Linux (Ubuntu/Debian):
sudo apt-get install libnetcdf-dev libhdf5-dev

# macOS (Homebrew):
brew install netcdf hdf5

# Install Python packages
pip install numpy xarray matplotlib
conda install -c conda-forge netcdf4  # Use conda just for netCDF4
pip install -e .
```

### Method 3: Docker (For isolated environments)
```bash
# Use the provided Dockerfile
docker build -t orca-grid-builder .
docker run -it orca-grid-builder bash
```

## 🐛 Troubleshooting

### "Building wheel for netCDF4 failed"
**Solution:** Use conda to install netCDF4 instead of pip:
```bash
conda install -c conda-forge netcdf4
```

### "Illegal instruction: 4"
**Solution:** This was caused by JAX (now removed). Update to latest version:
```bash
git pull
pip install -e . --upgrade
```

### "ModuleNotFoundError: No module named 'orca_grid'"
**Solution:** Make sure you activated the environment and installed in development mode:
```bash
conda activate orca_env
pip install -e .
```

### CLI not working
**Solution:** Test the CLI directly:
```bash
python -c "
import sys
sys.path.insert(0, 'src')
from orca_grid.cli import main
sys.argv = ['orca_grid', '1deg', 'my_grid.nc']
main()
"
```

## 📋 Dependency Details

### Required Dependencies
| Package | Version | Purpose |
|---------|---------|---------|
| numpy | >=1.19.0 | Numerical computations |
| xarray | >=0.16.0 | NetCDF file handling |
| netCDF4 | >=1.5.7 | NetCDF file I/O |
| matplotlib | >=3.3.0 | Visualization |

### Optional Dependencies
| Package | Purpose |
|---------|---------|
| pytest | Testing |
| jupyter | Interactive notebooks |
| cartopy | Advanced mapping |

## 🧪 Verification

After installation, verify everything works:

```bash
# Test imports
python -c "from orca_grid import ORCAGridBuilder, validate_grid; print('✓ Imports work')"

# Test grid generation
python -c "
from orca_grid import ORCAGridBuilder
builder = ORCAGridBuilder('1deg')
builder.write_netcdf('test.nc')
print('✓ Grid generation works')
"

# Test validation
python -c "
from orca_grid.validate_grid import validate_grid
report = validate_grid('test.nc')
print(f'✓ Validation works: {report[\"validation_passed\"]}')
"

# Run examples
python examples/validation_example.py
python examples/modular_demo.py
```

## 🎯 Environment-Specific Notes

### Windows
```bash
conda create -n orca_env python=3.9
conda activate orca_env
conda install -c conda-forge numpy xarray netcdf4 matplotlib
pip install -e .
```

### macOS
```bash
# Install XCode command line tools first
xcode-select --install

conda create -n orca_env python=3.9
conda activate orca_env
conda install -c conda-forge numpy xarray netcdf4 matplotlib
pip install -e .
```

### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install libnetcdf-dev libhdf5-dev

conda create -n orca_env python=3.9
conda activate orca_env
conda install -c conda-forge numpy xarray netcdf4 matplotlib
pip install -e .
```

## 🔄 Upgrading

To upgrade to the latest version:
```bash
cd /path/to/orca-grid-builder
git pull origin main
pip install -e . --upgrade
```

## 📚 Additional Resources

- [Conda Documentation](https://docs.conda.io/)
- [netCDF4 Installation Guide](https://unidata.github.io/netcdf4-python/)
- [Python Packaging Guide](https://packaging.python.org/)

---

**Need help?** The most reliable method is **conda installation** as shown in Method 1. This avoids all compilation issues and ensures compatibility.