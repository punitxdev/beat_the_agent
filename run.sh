#!/bin/bash

# Navigate to the project directory
cd "$(dirname "$0")"

# Check if venv exists, if not, create it
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate the virtual environment
source venv/bin/activate

# Install dependencies if they are not present
echo "Installing dependencies..."
pip install -q tensorflow flask Flask-CORS numpy

# Start the Flask server
echo "Starting Flask server..."
python app.py
