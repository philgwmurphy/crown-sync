#!/bin/bash
#
# Setup cron job for automatic Crown Land data sync
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SYNC_SCRIPT="$SCRIPT_DIR/sync_cron.sh"

# Make sync script executable
chmod +x "$SYNC_SCRIPT"

echo "Crown Land Sync - Cron Setup"
echo "=============================="
echo ""
echo "This script will help you set up automatic syncing of Crown Land data."
echo ""

# Ask for schedule
echo "How often would you like to sync?"
echo "1) Daily at 2 AM"
echo "2) Every 6 hours"
echo "3) Weekly (Sunday at 2 AM)"
echo "4) Custom schedule"
echo ""
read -p "Enter choice (1-4): " choice

case $choice in
    1)
        CRON_SCHEDULE="0 2 * * *"
        DESCRIPTION="Daily at 2 AM"
        ;;
    2)
        CRON_SCHEDULE="0 */6 * * *"
        DESCRIPTION="Every 6 hours"
        ;;
    3)
        CRON_SCHEDULE="0 2 * * 0"
        DESCRIPTION="Weekly on Sunday at 2 AM"
        ;;
    4)
        echo ""
        echo "Enter cron schedule (e.g., '0 2 * * *' for daily at 2 AM):"
        read -p "Schedule: " CRON_SCHEDULE
        DESCRIPTION="Custom: $CRON_SCHEDULE"
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

# Create cron entry
CRON_ENTRY="$CRON_SCHEDULE $SYNC_SCRIPT >> $SCRIPT_DIR/../logs/crown-sync.log 2>&1"

echo ""
echo "The following cron job will be added:"
echo "$CRON_ENTRY"
echo ""
echo "Description: $DESCRIPTION"
echo ""
read -p "Continue? (y/n): " confirm

if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "Cancelled"
    exit 0
fi

# Add to crontab
(crontab -l 2>/dev/null || echo "") | grep -v "$SYNC_SCRIPT" | { cat; echo "$CRON_ENTRY"; } | crontab -

echo ""
echo "✓ Cron job added successfully!"
echo ""
echo "To view your cron jobs:"
echo "  crontab -l"
echo ""
echo "To edit your cron jobs:"
echo "  crontab -e"
echo ""
echo "To remove this cron job:"
echo "  crontab -e"
echo "  (then delete the line containing: $SYNC_SCRIPT)"
echo ""
echo "Logs will be saved to: $SCRIPT_DIR/../logs/"
echo ""
