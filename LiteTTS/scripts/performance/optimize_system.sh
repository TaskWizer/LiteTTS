#!/bin/bash
# Performance optimization startup script

echo "Applying CPU performance optimizations..."

# Set CPU governor to performance mode (if available)
if [ -d "/sys/devices/system/cpu/cpu0/cpufreq" ]; then
    echo "Setting CPU governor to performance mode..."
    for cpu in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
        if [ -w "$cpu" ]; then
            echo performance > "$cpu" 2>/dev/null || true
        fi
    done
fi

# Disable CPU frequency scaling (if available)
if command -v cpupower >/dev/null 2>&1; then
    echo "Configuring CPU power settings..."
    cpupower frequency-set -g performance 2>/dev/null || true
fi

# Set process priority
echo "Setting process priority..."
renice -n -10 $$ 2>/dev/null || true

# Apply memory optimizations
echo "Applying memory optimizations..."
echo 1 > /proc/sys/vm/drop_caches 2>/dev/null || true

echo "Performance optimizations applied!"
