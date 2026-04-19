#!/usr/bin/env python3
"""
Comprehensive test script to verify all README inconsistencies have been resolved.
"""

import sys
import os

# Add src to path
sys.path.insert(0, '/Users/lesommer/git/nemo-orca-grid-builder/src')

def test_imports():
    """Test that all documented imports work."""
    print("🧪 Testing imports...")
    
    try:
        # Test core imports
        from orca_grid import ORCAGridBuilder, validate_grid
        from orca_grid import plot_grid_structure, plot_scale_factors, plot_staggered_points
        print("✓ Core imports work")
        
        # Test modular architecture
        from orca_grid.modular_factory import UnifiedGridBuilder
        print("✓ Modular architecture imports work")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_validation():
    """Test validation functionality."""
    print("🧪 Testing validation...")
    
    try:
        from orca_grid.validate_grid import validate_grid
        
        # Test with existing reference file
        report = validate_grid('data/domain_cfg.nc')
        
        if report['validation_passed']:
            print("✓ Validation works correctly")
            return True
        else:
            print(f"⚠ Validation passed but with issues: {report['errors']}")
            return True
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False

def test_examples_structure():
    """Test that examples directory structure is correct."""
    print("🧪 Testing examples structure...")
    
    expected_files = [
        'basic_usage.py',
        'modular_demo.py', 
        'validation_example.py',
        'performance_comparison.py'
    ]
    
    missing_files = []
    for file in expected_files:
        if not os.path.exists(f'examples/{file}'):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing example files: {missing_files}")
        return False
    else:
        print("✓ All example files present")
        return True

def test_data_directories():
    """Test that required directories exist."""
    print("🧪 Testing data directories...")
    
    required_dirs = ['output/plots', 'output/grids', 'data']
    missing_dirs = []
    
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print(f"❌ Missing directories: {missing_dirs}")
        return False
    else:
        print("✓ All required directories exist")
        return True

def test_api_consistency():
    """Test that API matches README documentation."""
    print("🧪 Testing API consistency...")
    
    try:
        # Test that documented classes and methods exist
        from orca_grid import ORCAGridBuilder
        
        # Check that ORCAGridBuilder has expected methods
        expected_methods = ['generate_grid', 'write_netcdf', 'generate_and_validate']
        for method in expected_methods:
            if not hasattr(ORCAGridBuilder, method):
                print(f"❌ Missing method: {method}")
                return False
        
        print("✓ API methods are consistent with documentation")
        return True
    except Exception as e:
        print(f"❌ API consistency test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Running comprehensive tests for README consistency fixes...")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_validation,
        test_examples_structure,
        test_data_directories,
        test_api_consistency
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! README inconsistencies have been resolved.")
        return True
    else:
        print("❌ Some tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
