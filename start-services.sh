#!/bin/bash
# ========================================
# Start Background Services (Redis + Celery)
# ========================================

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
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

# Start Redis if not running
if ! pgrep -x "redis-server" > /dev/null
then
    echo -e "${YELLOW}Starting Redis server...${NC}"
    redis-server &
    sleep 2
else
    echo -e "${BLUE}Redis already running.${NC}"
fi

# Start Celery worker
echo -e "${GREEN}Starting Celery worker...${NC}"
celery -A PulseRx worker --loglevel=info
