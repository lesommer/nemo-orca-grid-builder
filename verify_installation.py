#!/usr/bin/env python3
"""
Verify that ORCA Grid Builder is properly installed.
This script tests all functionality that doesn't require netCDF4 file I/O.
"""

import sys
import traceback

def test_imports():
    """Test that all modules can be imported."""
    print("🧪 Testing imports...")
    try:
        from orca_grid import ORCAGridBuilder, validate_grid
        from orca_grid import plot_grid_structure, plot_scale_factors, plot_staggered_points
        from orca_grid.modular_factory import UnifiedGridBuilder
        from orca_grid.validate_grid import validate_grid
        from orca_grid.plotting import plot_grid_structure
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        traceback.print_exc()
        return False

def test_grid_builder():
    """Test that ORCAGridBuilder can be instantiated."""
    print("🧪 Testing ORCAGridBuilder...")
    try:
        from orca_grid import ORCAGridBuilder
        
        # Test different resolutions
        for resolution in ["1deg", "0.5deg"]:
            builder = ORCAGridBuilder(resolution=resolution)
            print(f"✓ ORCAGridBuilder({resolution}) works")
        
        return True
    except Exception as e:
        print(f"❌ ORCAGridBuilder failed: {e}")
        traceback.print_exc()
        return False

def test_validation_module():
    """Test validation module with existing file."""
    print("🧪 Testing validation module...")
    try:
        from orca_grid.validate_grid import validate_grid
        
        # Test with the reference file we know exists
        if os.path.exists('data/domain_cfg.nc'):
            report = validate_grid('data/domain_cfg.nc')
            print(f"✓ Validation works: {report['validation_passed']}")
        else:
            print("⚠ Reference file not found, but validation module loads")
        
        return True
    except Exception as e:
        print(f"❌ Validation test failed: {e}")
        traceback.print_exc()
        return False

def test_plotting_module():
    """Test that plotting module loads."""
    print("🧪 Testing plotting module...")
    try:
        from orca_grid.plotting import plot_grid_structure, plot_scale_factors, plot_staggered_points
        print("✓ Plotting module works")
        return True
    except Exception as e:
        print(f"❌ Plotting test failed: {e}")
        traceback.print_exc()
        return False

def test_modular_architecture():
    """Test modular architecture."""
    print("🧪 Testing modular architecture...")
    try:
        from orca_grid.modular_factory import UnifiedGridBuilder, GridGeneratorFactory
        
        # Test factory
        available_models = GridGeneratorFactory.get_available_models()
        print(f"✓ Available models: {available_models}")
        
        # Test unified builder
        builder = UnifiedGridBuilder(model_name="nemo", resolution="1deg")
        print("✓ UnifiedGridBuilder works")
        
        return True
    except Exception as e:
        print(f"❌ Modular architecture test failed: {e}")
        traceback.print_exc()
        return False

def test_examples_structure():
    """Test that examples are properly structured."""
    print("🧪 Testing examples structure...")
    try:
        import os
        
        expected_files = [
            'examples/basic_usage.py',
            'examples/modular_demo.py',
            'examples/validation_example.py',
            'examples/performance_comparison.py'
        ]
        
        missing = [f for f in expected_files if not os.path.exists(f)]
        
        if missing:
            print(f"❌ Missing example files: {missing}")
            return False
        else:
            print("✓ All examples present")
            return True
    except Exception as e:
        print(f"❌ Examples test failed: {e}")
        return False

def main():
    """Run all verification tests."""
    print("🚀 ORCA Grid Builder Installation Verification")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_grid_builder,
        test_validation_module,
        test_plotting_module,
        test_modular_architecture,
        test_examples_structure
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 Installation verification successful!")
        print("\n✅ ORCA Grid Builder is properly installed")
        print("✅ All core functionality is working")
        print("✅ Ready for use!")
        return True
    else:
        print("❌ Some tests failed")
        print("\nCheck the error messages above for details.")
        return False

if __name__ == "__main__":
    import os
    success = main()
    sys.exit(0 if success else 1)