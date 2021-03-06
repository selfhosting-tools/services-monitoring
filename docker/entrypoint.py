"""
Docker entrypoint
"""

import logging
import signal
from os import listdir
from os.path import isdir, isfile, join
from sys import exit as sys_exit
from time import sleep

from prometheus_client import Counter, Gauge, start_http_server
from src.monitoring import ServicesMonitoring

config_directory = '/config'


# Basic logging
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(
    logging.Formatter(
        fmt="[entrypoint] %(asctime)s:%(levelname)s:%(message)s",
        datefmt='%Y-%m-%d %H:%M:%S'
    )
)
log.addHandler(stream_handler)

# Depreciation notice
log.warning("*** This tool is no longer maintained ***")


# Stop threads and exit
def exit_gracefully(sigcode, _frame):
    """
    Exit immediately gracefully
    """
    log.info("Signal %d received", sigcode)
    log.info("Exiting gracefully now...")
    for key in threads:
        threads[key].exit_event.set()
    sys_exit(0)


# Handle signals
signal.signal(signal.SIGINT, exit_gracefully)
signal.signal(signal.SIGTERM, exit_gracefully)  # issued by docker stop


# Check for config dir
if not isdir(config_directory):
    log.fatal("No config found")
    sys_exit(2)

# Start web server for prometheus metrics
start_http_server(8000)

# Create threads
threads = {}  # key is path to config file, value is Thread object
for config_file in listdir(config_directory):
    config_path = join(config_directory, config_file)
    if isfile(config_path) and config_path.endswith(".yaml"):
        log.info("Starting thread for %s...", config_path)
        threads[config_file] = ServicesMonitoring(config_path)
        threads[config_file].daemon = True
        threads[config_file].start()
        log.info("Thread started")
        sleep(5)  # Sleep 5s to avoid mixed logs
    else:
        log.debug("%s not a valid config file: ignored", config_path)


# Check that all threads are running, else exit with error
while True:
    for config_file in threads:
        if not threads[config_file].watchdog_is_alive():
            log.error("Exiting because thread for %s is dead", config_file)
            exit_gracefully(15, None)
            sys_exit(1)
    sleep(30)
