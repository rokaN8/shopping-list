#!/bin/bash

# Shopping List Application Stop Script
# This script stops the Flask shopping list application

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Change to the application directory
cd "$SCRIPT_DIR"

# PID file location
PID_FILE="$SCRIPT_DIR/shopping_list.pid"
LOG_FILE="$SCRIPT_DIR/shopping_list.log"

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

if [ ! -f "$PID_FILE" ]; then
    echo "PID file not found. Application may not be running."
    log_message "Stop requested but PID file not found"
    exit 1
fi

# Read PID from file
APP_PID=$(cat "$PID_FILE")

# Check if process is running
if kill -0 $APP_PID 2>/dev/null; then
    log_message "Stopping Shopping List application (PID: $APP_PID)..."
    kill $APP_PID
    
    # Wait for graceful shutdown
    sleep 2
    
    # Force kill if still running
    if kill -0 $APP_PID 2>/dev/null; then
        log_message "Force killing application..."
        kill -9 $APP_PID
    fi
    
    # Remove PID file
    rm -f "$PID_FILE"
    log_message "Shopping List application stopped"
    echo "Shopping List application stopped successfully!"
else
    echo "Application with PID $APP_PID is not running."
    log_message "Stop requested but process not found (PID: $APP_PID)"
    rm -f "$PID_FILE"
fi