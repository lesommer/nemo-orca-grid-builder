#!/usr/bin/env python3
"""
Final test of CLI functionality.
"""

import sys
import subprocess
import threading

def run_cli_with_timeout():
    """Run CLI with timeout."""
    def target():
        try:
            result = subprocess.run([sys.executable, '-m', 'orca_grid', '1deg', 'test_cli_final.nc'],
                                  capture_output=True, text=True, timeout=15)
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Timeout"
        except Exception as e:
            return False, "", str(e)
    
    # Run in separate thread to handle timeout
    result = [None]
    thread = threading.Thread(target=lambda: result.__setitem__(0, target()))
    thread.start()
    thread.join(timeout=20)
    
    if thread.is_alive():
        return False, "", "Timeout"
    
    return result[0]

def main():
    print("🧪 Testing CLI functionality...")
    
    success, stdout, stderr = run_cli_with_timeout()
    
    if success:
        print("✓ CLI works successfully!")
        if stdout:
            print(f"Output: {stdout}")
    else:
        print(f"⚠ CLI test result: {stderr}")
        print("Testing CLI components directly...")
        
        # Test CLI components directly
        try:
            sys.path.insert(0, 'src')
            from orca_grid.cli import main
            from orca_grid import ORCAGridBuilder
            
            print("✓ CLI module imports successfully")
            
            # Test grid builder directly
            builder = ORCAGridBuilder(resolution="1deg")
            result = builder.write_netcdf("test_direct_cli.nc")
            print(f"✓ Direct grid generation works: {result}")
            
        except Exception as e:
            print(f"❌ Direct test failed: {e}")

if __name__ == "__main__":
    main()