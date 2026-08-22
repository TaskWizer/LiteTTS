#!/usr/bin/env python3
"""
Model Performance Benchmark Runner
Quick script to run comprehensive model benchmarks
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Change to project directory
os.chdir(project_root)

from LiteTTS.benchmark import main

if __name__ == "__main__":
    print("🚀 Starting Kokoro TTS Model Benchmark...")
    print("📊 This will test all available models with comprehensive metrics")
    print("⏱️  Estimated time: 5-15 minutes depending on number of models")
    print()

    exit_code = main()

    if exit_code == 0:
        print("\n✅ Benchmark completed successfully!")
        print("📁 Check docs/benchmark/ for detailed results")
    else:
        print("\n❌ Benchmark failed!")

    sys.exit(exit_code)
