#!/bin/bash
# This line ensures the script uses the correct Python version

# Set an environment variable for the root path
export ENV_ROOT_PATH="/home/david/python_envs"
echo "Root path to environment: $ENV_ROOT_PATH"

# Activate the python environment
source "$ENV_ROOT_PATH/decopro_env/bin/activate"

# Run decopro
python3 decompaction.py
