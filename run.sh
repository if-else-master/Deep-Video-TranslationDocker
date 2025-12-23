#!/bin/bash
set -e

echo "🚀 Starting Omni-Video Agent Setup..."

# 1. Environment Check
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

echo "Activating virtual environment..."
source .venv/bin/activate

# 2. Dependencies
echo "Installing dependencies (this may take a while)..."
pip install -r requirements.txt

# 3. Model Download
echo "Checking model weights..."
python3 scripts/download_models.py

# 4. Launch App
echo "Starting GUI..."
streamlit run app.py
