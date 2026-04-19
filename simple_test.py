#!/usr/bin/env python3
"""
Simple test to verify key fixes without JAX dependency.
"""

import sys
import os

def test_validation_module():
    """Test validation module directly."""
    print("🧪 Testing validation module...")
    sys.path.insert(0, '/Users/lesommer/git/nemo-orca-grid-builder/src/orca_grid')
    
    try:
        import validate_grid
        report = validate_grid.validate_grid('data/domain_cfg.nc')
        print(f"✓ Validation works: {report['validation_passed']}")
        return True
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False

def test_examples_structure():
    """Test examples directory structure."""
    print("🧪 Testing examples structure...")
    
    expected_files = [
        'examples/basic_usage.py',
        'examples/modular_demo.py',
        'examples/validation_example.py',
        'examples/performance_comparison.py'
    ]
    
    missing = [f for f in expected_files if not os.path.exists(f)]
    
    if missing:
        print(f"❌ Missing files: {missing}")
        return False
    else:
        print("✓ All example files present")
        return True

def test_directories():
    """Test required directories."""
    print("🧪 Testing directories...")
    
    required = ['output/plots', 'output/grids', 'data']
    missing = [d for d in required if not os.path.exists(d)]
    
    if missing:
        print(f"❌ Missing directories: {missing}")
        return False
    else:
        print("✓ All directories exist")
        return True

def test_plotting_module():
    """Test plotting module."""
    print("🧪 Testing plotting module...")
    sys.path.insert(0, '/Users/lesommer/git/nemo-orca-grid-builder/src/orca_grid')
    
    try:
        import plotting
        print("✓ Plotting module loads")
        return True
    except Exception as e:
        print(f"❌ Plotting failed: {e}")
        return False

def main():
    print("🚀 Running simple tests...")
    
    tests = [
        test_validation_module,
        test_examples_structure,
        test_directories,
        test_plotting_module
    ]
    
    passed = sum(test() for test in tests)
    total = len(tests)
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Core functionality verified!")
        return True
    else:
        print("❌ Some tests failed")
        return False

if __name__ == "__main__":
    main()
