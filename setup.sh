#!/bin/bash

# Dagster Example Project - Setup Script
# Run this script to set up the project and start Dagster

set -e  # Exit on error

echo "🚀 Dagster Example Project Setup"
echo "================================"
echo ""

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "   ✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
pip install --upgrade pip > /dev/null
pip install -e "." > /dev/null
echo "   ✓ Dependencies installed"

# Check installation
echo ""
echo "✅ Verifying installation..."
dagster --version

echo ""
echo "================================"
echo "✨ Setup complete!"
echo ""
echo "📚 Next steps:"
echo ""
echo "1. Start Dagster:"
echo "   $ source venv/bin/activate  # If not already activated"
echo "   $ dagster dev"
echo ""
echo "2. Open browser:"
echo "   http://localhost:3000"
echo ""
echo "3. Materialize assets:"
echo "   Click on 'Assets' tab and materialize raw_customers"
echo ""
echo "4. Query results:"
echo "   $ python query_example.py"
echo ""
echo "📖 Documentation:"
echo "   - README.md       - Project overview"
echo "   - QUICKSTART.md   - Step-by-step tutorial"
echo "   - EXAMPLES.md     - Code examples & patterns"
echo "   - ARCHITECTURE.md - Asset dependency graph"
echo ""
echo "Happy learning! 🎓"
