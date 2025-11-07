#!/bin/bash

# Installation script for Query Automation Agent FastAPI

set -e

echo "Setting up Query Automation Agent FastAPI..."

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "ERROR: Python $required_version or higher required. Found: $python_version"
    exit 1
fi

echo "Python $python_version found"

# Install FastAPI dependencies
echo "Installing FastAPI dependencies..."
pip install fastapi uvicorn[standard] requests

# Install the project
echo "Installing query automation agent..."
pip install -e .

# Check if Ollama is running (optional for HuggingFace mode)
echo "Checking Ollama availability..."
if ! command -v ollama &> /dev/null; then
    echo "WARNING: Ollama not found. You can either:"
    echo "   1. Install Ollama: https://ollama.ai/"
    echo "   2. Use HuggingFace mode: USE_HUGGINGFACE=true python run_api.py"
else
    echo "Ollama found"
fi

# Test the installation
echo "Testing installation..."
if python -c "from agent_pipeline.api.fastapi_app import app; print('FastAPI app import successful')" 2>/dev/null; then
    echo "FastAPI installation successful!"
else
    echo "ERROR: FastAPI installation failed"
    exit 1
fi

echo ""
echo "Setup complete! You can now:"
echo "   - Start the API server: python run_api.py"
echo "   - Test with client: python example_client.py 'your query'"
echo "   - View interactive docs: http://127.0.0.1:8000/docs"
echo "   - View alternative docs: http://127.0.0.1:8000/redoc"
echo ""
echo "API will be available at: http://127.0.0.1:8000"
echo "Interactive documentation at: http://127.0.0.1:8000/docs"
echo "Alternative documentation at: http://127.0.0.1:8000/redoc"
