#!/usr/bin/env bash
# run.sh - Helper script to auto-activate the virtual environment and run the scraper

# Ensure we're in the project directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

# Check if the virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found at ${DIR}/venv"
    echo "Please create one using: python3 -m venv venv"
    exit 1
fi

# Activate the virtual environment
source venv/bin/activate

# Execute the python script with whatever arguments were passed to this script
python3 main.py "$@"
