#!/bin/bash

# Cable Manufacturing AI - Quick Start Script

echo "🏭 Cable Manufacturing Predictive Maintenance AI"
echo "================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📥 Installing dependencies..."
pip install -r requirements.txt --quiet

echo ""
echo "✅ Setup complete!"
echo ""
echo "📊 Next steps:"
echo ""
echo "1. Run Jupyter Notebook to train the model:"
echo "   jupyter notebook notebooks/parameter_extraction_and_prediction.ipynb"
echo ""
echo "2. After training, launch the Streamlit app:"
echo "   cd app && streamlit run app.py"
echo ""
echo "3. Navigate to http://localhost:8501 in your browser"
echo ""
echo "For more information, see README.md"
echo ""
