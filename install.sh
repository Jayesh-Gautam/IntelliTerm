#!/usr/bin/env bash
set -e

echo "============================================"
echo " IntelliTerm Installer"
echo "============================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed."
    echo "Please install Python 3.8+ first."
    exit 1
fi

echo "[1/2] Installing IntelliTerm..."
pip3 install .

echo ""
echo "[2/2] Setup complete."
echo ""
echo "============================================"
echo " IntelliTerm has been installed."
echo "============================================"
echo ""
echo "Next steps:"
echo "  1. Get a free API key from: https://console.groq.com/keys"
echo "  2. Run: turn config set-key YOUR_API_KEY"
echo "  3. Try:  turn list all files in this directory"
echo "  4. Or:   turn shell   (for interactive mode)"
