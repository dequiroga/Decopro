#!/bin/bash

set -e

# Project root
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_ROOT"

APP_NAME="Decopro"
ICON="$PROJECT_ROOT/assets/decopro.png"
EXECUTABLE="$PROJECT_ROOT/dist/$APP_NAME/$APP_NAME"
DESKTOP_FILE="$HOME/Desktop/$APP_NAME.desktop"

echo "========================================"
echo "Building $APP_NAME"
echo "========================================"

# Check icon exists
if [ ! -f "$ICON" ]; then
    echo "ERROR: Icon not found:"
    echo "$ICON"
    exit 1
fi

# Initialize conda
source "$(conda info --base)/etc/profile.d/conda.sh"

# Activate environment
conda activate decopro_env

# Make project root available for Python imports
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# Clean previous build
echo "Cleaning previous build..."
rm -rf build
rm -rf dist

# Build
echo "Building executable..."

pyinstaller \
    --noconfirm \
    --clean \
    --name "$APP_NAME" \
    --add-data "$ICON:assets" \
    gui/decopro_app.py

# Check executable
if [ ! -f "$EXECUTABLE" ]; then
    echo "ERROR: Executable was not created:"
    echo "$EXECUTABLE"
    exit 1
fi

chmod +x "$EXECUTABLE"

echo "Copying icon..."

# Put a copy next to the executable so the desktop launcher
# can reference it reliably.
cp "$ICON" "$PROJECT_ROOT/dist/$APP_NAME/decopro.png"

# Create desktop shortcut
echo "Creating desktop shortcut..."

mkdir -p "$HOME/Desktop"

cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=$APP_NAME
Comment=Decopro Application
Exec=$EXECUTABLE
Path=$PROJECT_ROOT/dist/$APP_NAME
Icon=$PROJECT_ROOT/dist/$APP_NAME/decopro.png
Terminal=false
Categories=Utility;
EOF

chmod +x "$DESKTOP_FILE"

# Mark launcher as trusted
gio set "$DESKTOP_FILE" metadata::trusted true 2>/dev/null || true

echo ""
echo "========================================"
echo "Build successful!"
echo "========================================"
echo ""
echo "Executable:"
echo "  $EXECUTABLE"
echo ""
echo "Icon:"
echo "  $PROJECT_ROOT/dist/$APP_NAME/decopro.png"
echo ""
echo "Desktop shortcut:"
echo "  $DESKTOP_FILE"
echo ""
