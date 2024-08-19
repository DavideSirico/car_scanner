#!/bin/bash

# Path to your Python virtual environment
VENV_PATH="/home/david/car_scanner/.venv"

# Path to your Python scripts
SCRIPT_PATH="/home/david/car_scanner"

# Activate the Python virtual environment
source "$VENV_PATH/bin/activate"

# Run the OBD data collection script as root
python "$SCRIPT_PATH/reader.py" &

# Run the Wi-Fi monitoring and data upload script as root
python "$SCRIPT_PATH/sender.py" &

# Wait for all background processes to complete before exiting the script
wait

# Deactivate the Python virtual environment
deactivate
