#!/bin/bash

# Exit on error
set -e

# ========================================================
# Configuration
# ========================================================
# Default virtual environment name
VENV_NAME="okx_research"

# Check if a custom VENV name is provided in .env file
if [ -f .env ]; then
    # Extract VENV_NAME from .env if it exists
    ENV_VENV=$(grep "^VENV_NAME=" .env | cut -d '=' -f2 | tr -d '\r')
    if [ ! -z "$ENV_VENV" ]; then
        VENV_NAME="$ENV_VENV"
    fi
fi
# ========================================================

echo "========================================================"
echo "      OKX Research Analyst - Startup Script (Linux/Mac)"
echo "      Virtual Environment: $VENV_NAME"
echo "========================================================"

# 1. Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] python3 could not be found. Please install Python 3.8+"
    exit 1
fi

# Check for existing process
EXISTING_PID=$(pgrep -f "python src/main.py" || true)
if [ ! -z "$EXISTING_PID" ]; then
    YELLOW='\033[1;33m'
    NC='\033[0m'
    echo -e "${YELLOW}[WARNING] Found existing instance(s) of OKX Research Analyst running (PID: $EXISTING_PID).${NC}"
    read -p "Do you want to stop them and start a new one? (y/n): " choice
    case "$choice" in 
      y|Y ) 
        echo "[INFO] Stopping existing processes..."
        kill $EXISTING_PID
        sleep 1
        ;;
      * ) 
        echo "[INFO] Aborting startup. Existing process is kept running."
        exit 0
        ;;
    esac
fi

# 2. Check/Create Virtual Environment
# Check if we are already in a virtual environment (VIRTUAL_ENV env var is set)
if [ -z "$VIRTUAL_ENV" ]; then
    if [ ! -d "$VENV_NAME" ]; then
        echo "[INFO] Virtual environment '$VENV_NAME' not found. Creating..."
        python3 -m venv "$VENV_NAME"
        echo "[INFO] Virtual environment created successfully."
    fi
    
    # 3. Activate Virtual Environment
    source "$VENV_NAME/bin/activate"
else
    echo "[INFO] Already inside a virtual environment ($VIRTUAL_ENV). Skipping activation."
fi

# 4. Install/Update Dependencies
echo "[INFO] Installing/Updating dependencies..."
pip install -r requirements.txt -q

# 4.1 Clean __pycache__ to prevent ImportError
echo "[INFO] Cleaning Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} +

# 5. Run the Application
mkdir -p logs

if [[ "$1" == "-d" ]] || [[ "$1" == "--daemon" ]]; then
    # Shift arguments to remove the flag
    shift
    
    echo "[INFO] Starting application in BACKGROUND mode..."
    echo "[INFO] Logs will be written to logs/nohup.log"
    
    # Run with nohup
    nohup python src/main.py "$@" > logs/nohup.log 2>&1 &
    
    PID=$!
    # Colors
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    NC='\033[0m'

    echo -e "${GREEN}[INFO] Application started successfully (PID: $PID)${NC}"
    echo "--------------------------------------------------------"
    echo -e "🔍 Check Status : ${YELLOW}ps -ef | grep main.py${NC}"
    echo -e "🛑 Stop Process : ${YELLOW}kill $PID${NC}"
    echo -e "📄 Watch Logs   : ${YELLOW}tail -f logs/okx_research.log${NC}"
    echo "--------------------------------------------------------"
else
    echo "[INFO] Starting application in FOREGROUND mode..."
    echo "--------------------------------------------------------"
    python src/main.py "$@"
fi

# 6. Deactivate
if [ -z "$VIRTUAL_ENV" ]; then
    deactivate
fi
echo ""
echo "[INFO] Done."
