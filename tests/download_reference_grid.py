#!/usr/bin/env python3
"""
Download reference ORCA1 domain_cfg.nc file if not available locally.
"""

import os
import zipfile
import requests
import shutil
from urllib.parse import urljoin

def download_reference_grid():
    """Download reference ORCA1 domain_cfg.nc file."""
    
    # Configuration
    ZENODO_RECORD = "14041098"
    DOWNLOAD_URL = f"https://zenodo.org/records/{ZENODO_RECORD}/files/orca1_grid_files.zip"
    TMP_DIR = "tmp_download"
    DATA_DIR = "data"
    TARGET_FILE = os.path.join(DATA_DIR, "domain_cfg.nc")
    
    # Check if file already exists
    if os.path.exists(TARGET_FILE):
        print(f"✅ Reference grid already exists: {TARGET_FILE}")
        return True
    
    print("📥 Downloading reference ORCA1 grid from Zenodo...")
    
    try:
        # Create directories
        os.makedirs(TMP_DIR, exist_ok=True)
        os.makedirs(DATA_DIR, exist_ok=True)
        
        # Download the zip file
        print("Downloading zip file...")
        zip_path = os.path.join(TMP_DIR, "orca1_grid_files.zip")
        
        response = requests.get(DOWNLOAD_URL, stream=True)
        response.raise_for_status()
        
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print("✅ Download completed")
        
        # Extract only domain_cfg.nc
        print("Extracting domain_cfg.nc...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            if 'domain_cfg.nc' in zip_ref.namelist():
                zip_ref.extract('domain_cfg.nc', path=TMP_DIR)
                shutil.move(
                    os.path.join(TMP_DIR, 'domain_cfg.nc'),
                    TARGET_FILE
                )
                print(f"✅ Reference grid saved to: {TARGET_FILE}")
            else:
                print("❌ domain_cfg.nc not found in the zip file")
                return False
        
        # Clean up
        shutil.rmtree(TMP_DIR)
        print("✅ Temporary files cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Error downloading reference grid: {e}")
        # Clean up on error
        if os.path.exists(TMP_DIR):
            shutil.rmtree(TMP_DIR)
        return False

if __name__ == "__main__":
    success = download_reference_grid()
    if success:
        print("\n🎉 Reference grid ready for use!")
        print("You can now use it for validation:")
        print("  from orca_grid.validate_grid import validate_grid")
        print("  report = validate_grid('data/domain_cfg.nc')")
    else:
        print("\n❌ Failed to download reference grid")
        print("The library will still work, but validation against reference will be limited")
