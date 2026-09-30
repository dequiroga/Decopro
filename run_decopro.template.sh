#!/bin/bash
# This line ensures the script uses the correct Python version

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_ROOT"

source "$(conda info --base)/etc/profile.d/conda.sh"
# Activate environment
conda activate decopro_env

export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# Run the application
python3 gui/decopro_app.py
