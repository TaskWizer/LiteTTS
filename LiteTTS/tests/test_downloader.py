#!/usr/bin/env python3
"""
Test the downloader functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

try:
    from LiteTTS.downloader import ensure_model_files, get_available_voices
    print("✅ Downloader import successful!")
    
    print("📋 Available voices:", get_available_voices())
    
    print("📦 Checking model files...")
    if ensure_model_files():
        print("✅ Model files ready!")
    else:
        print("❌ Failed to ensure model files")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()