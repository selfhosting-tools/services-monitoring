#!/bin/bash
# Author: FL42

set -e

# This script expects a directory /config with one file CONFIG which defines
# one path to a config file to run per line (e.g. /config/example.yaml)
# /config should be mounted by Docker at container startup.

CONFIG_FILE="/config/CONFIG"

if [ ! -e $CONFIG_FILE ]
then
    echo "$CONFIG_FILE does not exist"
    exit 1
fi

cat $CONFIG_FILE | while read config_path
do
    # -u disables buffering for stdout
    python -u monitoring.py -c $config_path &
done

# Don't exit
while true
do
    sleep 600
done
