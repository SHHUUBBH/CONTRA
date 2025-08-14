#!/bin/bash

# Netlify Build Script for CONTRA

echo "Starting CONTRA build process..."

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements-netlify.txt

# Verify installation
echo "Verifying installation..."
python -c "import flask; print('Flask installed successfully')"
python -c "import requests; print('Requests installed successfully')"

echo "Build completed successfully!"
