#!/usr/bin/env bash

set -e

echo "Starting notification worker..."
python -m med_sharing_system.launchers.notification_worker