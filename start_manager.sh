#!/bin/bash
# Start MT5 Manager as background service

WORKSPACE="/root/workspace/forex"
LOG_FILE="$WORKSPACE/logs/mt5_manager.log"
PID_FILE="$WORKSPACE/mt5_manager.pid"

cd "$WORKSPACE" || exit 1

# Check if already running
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "Manager already running (PID: $OLD_PID)"
        exit 0
    fi
    rm -f "$PID_FILE"
fi

# Start the manager
echo "Starting MT5 Manager..."
nohup python3 mt5_manager_loop.py >> "$LOG_FILE" 2>&1 &
echo $! > "$PID_FILE"
echo "Started with PID: $(cat $PID_FILE)"
