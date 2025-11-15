#!/bin/bash
#
# Cron script to sync Crown Land data to Mapbox
# This script should be run on a schedule via cron
#
# Example cron entry (runs daily at 2 AM):
# 0 2 * * * /path/to/crown-sync/automation/sync_cron.sh >> /var/log/crown-sync.log 2>&1

set -e  # Exit on error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="$PROJECT_DIR/config.json"
VENV_DIR="$PROJECT_DIR/venv"
LOG_DIR="$PROJECT_DIR/logs"

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Logging
LOG_FILE="$LOG_DIR/sync_$(date +%Y%m%d_%H%M%S).log"
echo "Starting Crown Land sync at $(date)" | tee -a "$LOG_FILE"

# Activate virtual environment if it exists
if [ -d "$VENV_DIR" ]; then
    echo "Activating virtual environment..." | tee -a "$LOG_FILE"
    source "$VENV_DIR/bin/activate"
fi

# Change to project directory
cd "$PROJECT_DIR"

# Run the sync script
echo "Running sync script..." | tee -a "$LOG_FILE"
if python3 sync_to_mapbox.py --config "$CONFIG_FILE" >> "$LOG_FILE" 2>&1; then
    echo "Sync completed successfully at $(date)" | tee -a "$LOG_FILE"
    EXIT_CODE=0
else
    echo "Sync failed at $(date)" | tee -a "$LOG_FILE"
    EXIT_CODE=1
fi

# Clean up old logs (keep last 30 days)
echo "Cleaning up old logs..." | tee -a "$LOG_FILE"
find "$LOG_DIR" -name "sync_*.log" -mtime +30 -delete

# Deactivate virtual environment
if [ -d "$VENV_DIR" ]; then
    deactivate
fi

echo "Script finished at $(date)" | tee -a "$LOG_FILE"
exit $EXIT_CODE
