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
    DOWNLOAD_URL = f"https://zenodo.org/records/{ZENODO_RECORD}/files/data_repository.zip"
    TMP_DIR = "tmp_download"
    DATA_DIR = "data"
    TARGET_FILE = os.path.join(DATA_DIR, "domain_cfg.nc")
    ZIP_FILE = os.path.join(TMP_DIR, "data_repository.zip")
    
    # Check if file already exists
    if os.path.exists(TARGET_FILE):
        print(f"✅ Reference grid already exists: {TARGET_FILE}")
        return True
    
    # Check if zip file already downloaded
    if os.path.exists(ZIP_FILE):
        print(f"✅ Found existing download: {ZIP_FILE}")
    else:
        print("📥 Downloading reference ORCA1 grid from Zenodo...")
        try:
            # Create directories
            os.makedirs(TMP_DIR, exist_ok=True)
            os.makedirs(DATA_DIR, exist_ok=True)
            
            # Download the zip file
            print("Downloading zip file (this may take a while for 1.3GB file)...")
            response = requests.get(DOWNLOAD_URL, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(ZIP_FILE, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print("✅ Download completed")
        except Exception as e:
            print(f"❌ Error downloading: {e}")
            if os.path.exists(TMP_DIR):
                shutil.rmtree(TMP_DIR)
            return False
    
    try:
        # Extract domain_cfg.nc from input_fields/
        print("Extracting domain_cfg.nc...")
        with zipfile.ZipFile(ZIP_FILE, 'r') as zip_ref:
            # Check if file exists in input_fields/
            file_found = False
            for file in zip_ref.namelist():
                if 'domain_cfg.nc' in file:
                    # Extract the file
                    zip_ref.extract(file, path=TMP_DIR)
                    # Move to final location
                    extracted_path = os.path.join(TMP_DIR, file)
                    shutil.move(extracted_path, TARGET_FILE)
                    file_found = True
                    print(f"✅ Reference grid saved to: {TARGET_FILE}")
                    break
            
            if not file_found:
                print("❌ domain_cfg.nc not found in the zip file")
                print("Available files:")
                for file in zip_ref.namelist():
                    print(f"  - {file}")
                return False
        
        # Clean up
        shutil.rmtree(TMP_DIR)
        print("✅ Temporary files cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Error extracting: {e}")
        if os.path.exists(TMP_DIR):
            shutil.rmtree(TMP_DIR)
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
