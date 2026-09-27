#!/usr/bin/env bash
set -euo pipefail

# Tantric AI Agent - Swiss Ephemeris Build Script
# Compiles libswe.a for sidereal chart calculations

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
SWEPH_DIR="$PROJECT_DIR/third_party/sweph"

echo "[*] Building Swiss Ephemeris static library..."

mkdir -p "$SWEPH_DIR"
cd "$SWEPH_DIR"

# Check if libswe.a already exists
if [ -f "libswe.a" ]; then
    echo "[✓] libswe.a already exists. Skipping build."
    echo "    Delete third_party/sweph/libswe.a to rebuild."
    exit 0
fi

# Download Swiss Ephemeris source if not present
if [ ! -f "swedate.c" ]; then
    echo "[*] Downloading Swiss Ephemeris source files..."
    # Official Swiss Ephemeris files needed:
    # swedate.c, sweph.c, swephexp.h, sweodef.h, sweph.h
    # Download from: https://www.astro.com/swisseph/
    echo "[-] Please download Swiss Ephemeris source from:"
    echo "    https://www.astro.com/swisseph/"
    echo "    Extract to: $SWEPH_DIR"
    echo ""
    echo "    Required files:"
    echo "    - swedate.c"
    echo "    - sweph.c"
    echo "    - sweodef.h"
    echo "    - sweph.h"
    echo "    - swephexp.h"
    echo ""
    echo "    Or use: wget https://www.astro.com/swisseph/swisseph_2.10.03.tar.gz"
    exit 1
fi

# Compile Swiss Ephemeris to object files
echo "[*] Compiling Swiss Ephemeris sources..."
gcc -O3 -fPIC -fomit-frame-pointer -c swedate.c sweph.c -I.

# Create static archive
echo "[*] Creating static archive libswe.a..."
ar rcs libswe.a swedate.o sweph.o
ranlib libswe.a

# Cleanup object files
rm -f *.o

echo "[✓] libswe.a built successfully."
echo "    Location: $SWEPH_DIR/libswe.a"
echo "    Size: $(du -h libswe.a | cut -f1)"
