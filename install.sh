#!/bin/bash

# ORCA Grid Builder Installation Script
# This script handles the netCDF4 compilation issue by using conda for that dependency

echo "🚀 ORCA Grid Builder Installation"
echo "================================"

# Check if conda is available
if command -v conda &> /dev/null; then
    echo "✅ Conda found - using conda for netCDF4"
    
    # Create environment if it doesn't exist
    if conda env list | grep -q "orca_env"; then
        echo "📦 Environment exists - activating"
        source activate orca_env
    else
        echo "🔧 Creating new environment"
        conda create -n orca_env python=3.9 -y
        source activate orca_env
    fi
    
    # Install netCDF4 via conda (avoids compilation)
    echo "📦 Installing netCDF4 via conda"
    conda install -c conda-forge netcdf4 -y
    
    # Install other dependencies via pip
    echo "📦 Installing other dependencies"
    pip install numpy xarray matplotlib
    
    # Install the package
    echo "📦 Installing ORCA Grid Builder"
    pip install -e .
    
    echo "🎉 Installation complete!"
    echo "Activate this environment with: conda activate orca_env"

elif command -v pip &> /dev/null; then
    echo "⚠️  Conda not found - trying pip installation"
    echo "⚠️  Note: You may need to install netCDF4 separately via conda or system packages"
    
    # Try pip installation
    echo "📦 Installing dependencies via pip"
    pip install numpy xarray matplotlib
    
    # Check if netCDF4 is already installed
    if python -c "import netCDF4" 2>/dev/null; then
        echo "✅ netCDF4 already installed"
    else
        echo "❌ netCDF4 not found - please install it via:"
        echo "   conda install -c conda-forge netCDF4"
        echo "   or"
        echo "   sudo apt-get install python3-netcdf4  # Ubuntu/Debian"
        echo "   or"
        echo "   brew install netcdf  # macOS"
    fi
    
    # Install the package
    echo "📦 Installing ORCA Grid Builder"
    pip install -e .
    
    echo "⚠️  Installation may have issues without netCDF4"
    echo "⚠️  For full functionality, install netCDF4 via conda"

else
    echo "❌ Neither conda nor pip found - please install Python first"
    exit 1
fi

echo ""
echo "🧪 Testing installation..."
python -c "
try:
    from orca_grid.validate_grid import validate_grid
    print('✅ Validation module works')
    from orca_grid.plotting import plot_grid_structure
    print('✅ Plotting module works')
    print('🎉 Core functionality is working!')
except Exception as e:
    print(f'❌ Error: {e}')
    print('Please check the installation instructions')
"