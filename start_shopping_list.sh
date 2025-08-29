#!/bin/bash

# Shopping List Application Startup Script
# This script starts the Flask shopping list application with proper environment setup

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Change to the application directory
cd "$SCRIPT_DIR"

# Set production environment variables
export SECRET_KEY="${SECRET_KEY:-$(openssl rand -hex 32)}"
export ADMIN_USERNAME="${ADMIN_USERNAME:-admin}"
export ADMIN_PASSWORD="${ADMIN_PASSWORD:-admin}"
export FORCE_HTTPS="${FORCE_HTTPS:-false}"

# Log file location
LOG_FILE="$SCRIPT_DIR/shopping_list.log"

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

log_message "Starting Shopping List application..."

# Check if virtual environment exists, create if it doesn't
if [ ! -d "venv" ]; then
    log_message "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        log_message "ERROR: Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment
source venv/bin/activate
if [ $? -ne 0 ]; then
    log_message "ERROR: Failed to activate virtual environment"
    exit 1
fi

# Install/upgrade dependencies
log_message "Installing dependencies..."
pip install -r requirements.txt >> "$LOG_FILE" 2>&1
if [ $? -ne 0 ]; then
    log_message "ERROR: Failed to install dependencies"
    exit 1
fi

# Start the application
log_message "Starting Flask application..."
python3 app.py >> "$LOG_FILE" 2>&1 &

# Get the PID of the background process
APP_PID=$!
echo $APP_PID > "$SCRIPT_DIR/shopping_list.pid"

log_message "Shopping List application started with PID: $APP_PID"

# Wait a moment and check if the process is still running
sleep 2
if kill -0 $APP_PID 2>/dev/null; then
    log_message "Application is running successfully"
    echo "Shopping List application started successfully!"
    echo "PID: $APP_PID"
    echo "Log file: $LOG_FILE"
    echo "Access the application at: http://localhost:5000"
else
    log_message "ERROR: Application failed to start"
    echo "ERROR: Application failed to start. Check log file: $LOG_FILE"
    exit 1
fi