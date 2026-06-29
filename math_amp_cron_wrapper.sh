#!/bin/bash
# Cron wrapper for MATH_AMP scanner
# Runs every 30 minutes during market hours

WORKSPACE="/root/workspace/forex"
LOG_FILE="$WORKSPACE/logs/math_amp_cron.log"

cd "$WORKSPACE" || exit 1

echo "=== $(date) ===" >> "$LOG_FILE"
python3 mATH_AMP_scanner.py 2>&1 | head -50 >> "$LOG_FILE"

# Also check for high-impact news
echo "--- News check ---" >> "$LOG_FILE"
python3 news_scanner.py --kill-check 2>&1 | head -20 >> "$LOG_FILE"
