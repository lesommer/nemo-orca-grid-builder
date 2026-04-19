#!/usr/bin/env python3
"""
Add diagnostic logging to grid generation for troubleshooting.
"""

import sys
import logging
import numpy as np
from datetime import datetime

# Set up detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('grid_generation_debug.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('grid_diagnostics')

def test_with_logging():
    """Test grid generation with detailed logging."""
    
    logger.info("Starting grid generation diagnostic test")
    logger.info(f"Timestamp: {datetime.now()}")
    
    try:
        sys.path.insert(0, 'src')
        from orca_grid import ORCAGridBuilder
        
        logger.info("Creating ORCAGridBuilder instance")
        builder = ORCAGridBuilder(resolution="1deg")
        
        logger.info("Generating grid data")
        grid_data = builder.generate_grid()
        
        logger.info(f"Grid data keys: {list(grid_data.keys())}")
        
        for key, value in grid_data.items():
            if hasattr(value, 'shape'):
                logger.info(f"{key}: shape={value.shape}, min={np.min(value):.2f}, max={np.max(value):.2f}")
            else:
                logger.info(f"{key}: {value}")
        
        logger.info("Writing to NetCDF")
        result = builder.write_netcdf("diagnostic_test.nc")
        logger.info(f"Result: {result}")
        
        logger.info("✅ Grid generation completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Error during grid generation: {e}", exc_info=True)
        return False
    
    return True

if __name__ == "__main__":
    success = test_with_logging()
    if success:
        print("\n🎉 Diagnostic test completed. Check grid_generation_debug.log for details.")
    else:
        print("\n❌ Diagnostic test failed. Check logs for details.")
