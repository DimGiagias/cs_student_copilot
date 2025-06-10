#!/usr/bin/env bash

# Usage:
#   ./setup.sh        # Installs dependencies using pip and requirements.txt
#   ./setup.sh --uv   # Installs dependencies using uv
#

set -e

VENV_DIR=".venv"
USE_UV=false

if [[ "$1" == "--uv" ]]; then
  USE_UV=true
fi

echo "🚀 Setting up project environment..."

if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creating Python virtual environment in '$VENV_DIR'..."
    python3 -m venv "$VENV_DIR"
else
    echo "✅ Virtual environment already exists."
fi

if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
else
    source "$VENV_DIR/Scripts/activate"
fi

if [ "$USE_UV" = true ]; then
    if [ ! -f "pyproject.toml" ]; then
        echo "❌ Error: pyproject.toml not found."
        echo "   Please run this script from the root directory of the project."
        exit 1
    fi
    echo "🔗 Installing dependencies using uv..."
    if ! command -v uv &> /dev/null; then
        echo "🔍 uv not found, installing it first..."
        pip install -q uv
    fi
    uv pip sync
    echo "⚡️ Dependencies installed with uv."
else
    echo "📜 Installing dependencies using pip..."
    python3 -m pip install --upgrade pip
    pip install -r requirements.txt
    echo "✅ Dependencies installed with pip."
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "👉 To activate your virtual environment in your shell, run:"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" || "$OS" == "Windows_NT" ]]; then
    echo "   $VENV_DIR\\Scripts\\activate"
else
    echo "   source $VENV_DIR/bin/activate"
fi
