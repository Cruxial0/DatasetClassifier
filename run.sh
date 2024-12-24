#!/bin/bash

# Check if venv exists, if not create it
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate the virtual environment
source .venv/bin/activate

# Check if requirements are installed
pip freeze > temp_requirements.txt
if ! cmp -s requirements.txt temp_requirements.txt; then
    echo "Installing requirements..."
    pip install -r requirements.txt
fi
rm temp_requirements.txt

# Run the main.py script
echo "Running main.py..."
python main.py

# Deactivate the virtual environment
deactivate
