#!/bin/bash
# ========================================
# Start Daphne Web Server Only
# ========================================

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

# Activate virtual environment
VENV_PATH="/Users/nick/PulseRx/venv/bin/activate"
if [ -f "$VENV_PATH" ]; then
    echo -e "${GREEN}Activating virtual environment...${NC}"
    source "$VENV_PATH"
else
    echo -e "${RED}Virtual environment not found at $VENV_PATH${NC}"
    exit 1
fi

echo -e "${GREEN}Starting Daphne web server on http://127.0.0.1:8000${NC}"
daphne -b 127.0.0.1 -p 8000 PulseRx.asgi:application
