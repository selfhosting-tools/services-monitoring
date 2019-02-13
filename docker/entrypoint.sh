#!/bin/sh
# Author: FL42

set -e

# Check for config files
if [ -z "$(ls -A /config)" ]; then
    echo "ERROR: config directory is empty, exiting!"
    exit 1
fi

# Loop on config files
for config_file in /config/*.yaml
do
    echo "Running with config file $config_file..."
    # -u disables buffering for stdout
    python -u monitoring.py -c $config_file &
done

# Don't exit
sleep infinity
