@echo off
REM Cable Manufacturing AI - Quick Start Script for Windows

echo ========================================
echo 🏭 Cable Manufacturing Predictive Maintenance AI
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo ✅ Python found
python --version
echo.

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment exists
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo 📥 Installing dependencies...
pip install -r requirements.txt --quiet

echo.
echo ✅ Setup complete!
echo.
echo 📊 Next steps:
echo.
echo 1. Run Jupyter Notebook to train the model:
echo    jupyter notebook notebooks\parameter_extraction_and_prediction.ipynb
echo.
echo 2. After training, launch the Streamlit app:
echo    cd app
echo    streamlit run app.py
echo.
echo 3. Navigate to http://localhost:8501 in your browser
echo.
echo For more information, see README.md
echo.
pause
