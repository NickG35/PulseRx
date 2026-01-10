#!/bin/bash
# ========================================
# PulseRx Full Dev Startup Script
# ========================================

# ---------- Colors for logs ----------
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ---------- Activate virtual environment ----------
VENV_PATH="/Users/nick/PulseRx/venv/bin/activate"
if [ -f "$VENV_PATH" ]; then
    echo -e "${GREEN}Activating virtual environment...${NC}"
    source "$VENV_PATH"
else
    echo -e "${RED}Virtual environment not found at $VENV_PATH${NC}"
    exit 1
fi

# ---------- Start Redis if not running ----------
if ! pgrep -x "redis-server" > /dev/null
then
    echo -e "${YELLOW}Starting Redis server...${NC}"
    redis-server &
    sleep 2
else
    echo -e "${BLUE}Redis already running.${NC}"
fi

# ---------- Optional: auto-reload Celery ----------
# If you want Celery to restart on code changes, ensure 'watchdog' is installed:
# pip install watchdog

CELERY_CMD="celery -A PulseRx worker --loglevel=info"
if command -v watchmedo &> /dev/null
then
    CELERY_CMD="watchmedo auto-restart --patterns='*.py' -- celery -A PulseRx worker --loglevel=info"
    echo -e "${BLUE}Celery auto-reload enabled.${NC}"
else
    echo -e "${BLUE}Celery auto-reload not enabled (install watchdog to enable).${NC}"
fi

# ---------- Start all processes using Honcho ----------
echo -e "${GREEN}Starting development environment...${NC}"
honcho start
