#!/usr/bin/env python3
"""
Test initialization without hanging the terminal
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from app import initialize_model
    print("🔄 Testing initialization...")
    initialize_model()
    print("✅ Initialization successful!")
except Exception as e:
    print(f"❌ Initialization failed: {e}")
    import traceback
    traceback.print_exc()