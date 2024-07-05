#!/usr/bin/env bash

set -e

echo "Starting delivery consumer..."
python -m med_sharing_system.launchers.delivery_consumer
