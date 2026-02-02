#!/bin/bash

# Check if venv is available, and install it if necessary
if ! python3 -m venv --help > /dev/null 2>&1; then
    echo "venv is not installed. Installing venv..."
    sudo apt install -y python3-venv
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if pip is installed in the virtual environment
if ! command -v pip &> /dev/null
then
    echo "pip is not installed in the virtual environment. Installing pip..."
    curl https://bootstrap.pypa.io/get-pip.py | python
fi

# Install Python in the virtual environment if necessary
if ! command -v python &> /dev/null
then
    echo "Python is not installed in the virtual environment. Installing Python..."
    pip install python
fi

# Run the Python script
echo "Running main.py..."
python main.py
