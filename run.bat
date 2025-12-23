@echo off
echo 🚀 Starting Omni-Video Agent Setup...

:: 1. Environment Check
IF NOT EXIST ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

echo Activating virtual environment...
CALL .venv\Scripts\activate

:: 2. Dependencies
echo Installing dependencies...
pip install -r requirements.txt

:: 3. Model Download
echo Checking model weights...
python scripts\download_models.py

:: 4. Launch App
echo Starting GUI...
streamlit run app.py
