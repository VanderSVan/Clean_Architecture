#!/usr/bin/env bash

set -e

echo "Starting matcher consumer..."
python -m med_sharing_system.launchers.match_worker
