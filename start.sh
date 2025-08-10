#!/bin/bash

# Voice Agent FastAPI Server Startup Script

echo "Starting Voice Agent FastAPI Server..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Warning: .env file not found. Please create one from env.example"
    echo "cp env.example .env"
    echo "Then edit .env with your API keys"
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment (fish shell)
echo "Activating virtual environment..."
source venv/bin/activate.fish

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Start the server
echo "Starting server on http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo "Press Ctrl+C to stop"

python main.py 