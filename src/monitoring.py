#!/usr/bin/env python3
# Authors: alex2242 & FL42

"""
usage: monitoring.py [-h] [-c CONFIG]

Services Monitoring

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Path to config file
"""
import argparse
import logging
import signal
import threading
from sys import exit as sys_exit
from time import sleep, time

import yaml
from prometheus_client import Counter, Gauge

from src.notification import email
from src.probes import dns, https, ping, raw_tcp, smtp
from src.tools import Message

version = "0.1"


probe_success_total = Counter(
    "probe_success_total", "Number of successful probes", ("probe", "target")
)
probe_failures_total = Counter(
    "probe_failures_total", "Number of failed probes", ("probe", "target")
)
probe_duration = Gauge(
    "probe_duration", "Duration of the probe", ("probe", "target")
)


class ServicesMonitoring(threading.Thread):
    """
    See module docstring.
    """

    # Mapping between strings and python modules
    probe_mapping = {
        'ping': {
            "module": ping,
            "target_type": None
        },
        'raw_tcp': {
            "module": raw_tcp,
            "target_type": "host"
        },
        'smtp': {
            "module": smtp,
            "target_type": "host"
        },
        'https': {
            "module": https,
            "target_type": "url"
        },
        'dns': {
            "module": dns,
            "target_type": "domain"
        }
    }

    def __init__(self, config_path):

        # Init from mother class
        threading.Thread.__init__(self)

        # Set up logger
        self.log = logging.getLogger(config_path)
        self.log.setLevel(logging.INFO)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(
            logging.Formatter(
                fmt="[{}] %(asctime)s:%(levelname)s:%(message)s".format(
                    config_path
                ),
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        )
        self.log.addHandler(stream_handler)

        # Initialize vars
        self.config_path = config_path
        self.config = None
        self.watchdog = time()
        # Store sent messages (prevent duplicate notifications)
        self.down_services = []
        self.exit_event = threading.Event()

    def run(self):
        """
        Run method (see threading module)
        """

        # Parse config
        if self.config_path is not None:
            with open(self.config_path, 'rt') as config_file:
                self.config = yaml.safe_load(config_file)
        else:
            raise Exception('Path to config is required')

        # Set up loglevel
        self.log.setLevel(
            logging.DEBUG if self.config['common'].get('debug', False)
            else logging.INFO
        )

        # Wait for a delay at startup if configured
        delay_at_startup = self.config['common'].get('delay_at_startup', 0)
        if delay_at_startup > 0:
            self.log.info(
                "Waiting for %d seconds before starting...",
                delay_at_startup
            )
            self.exit_event.wait(delay_at_startup)

        # Disable notifications if section is not defined
        send_notification = 'notifications' in self.config

        # Send a test message
        if send_notification \
           and self.config['common'].get('email_at_startup', False):

            email.send_email(
                subject="Services-monitoring started",
                body="This is a message sent at startup",
                smtp_config=self.config['notifications']['email']['config']
            )

        # Call self.monitor every 'delay' sec
        while not self.exit_event.is_set():
            self.monitor(send_notification=send_notification)
            self.log.debug("Waiting...")
            self.exit_event.wait(self.config['common']['delay'])
            self.watchdog = time()
        self.log.info("Exited")

    def watchdog_is_alive(self):
        """
        Return False if the thread has died
        """
        if time() - self.watchdog > self.config['common']['delay'] + 60:
            return False
        return True

    def monitor(self, send_notification):
        """
        Parameter:
        send_notification: (bool) Send notification messages using
                                  self.send_notification
        """

        # Set up a list of notifications to send
        notifications = []

        # Probe configured services
        config_probes = self.config['probes']
        probe_names = config_probes.keys()

        for probe_name in probe_names:
            probe_module = ServicesMonitoring.probe_mapping[probe_name]["module"]
            target_type = ServicesMonitoring.probe_mapping[probe_name]["target_type"]
            for service in config_probes[probe_name]:
                self.log.debug("%s probe for %s", probe_name, str(service))

                # Target refers to the target of the probe (the host, the url, etc)
                if target_type:
                    target = service.get(target_type)
                else:
                    target = service

                # Retry probe 2 times in case of error or warning
                # to avoid notification on one-time error.
                for _ in range(3):
                    try:  # Catch unexpected exception
                        start_time = time()
                        probes_results = probe_module.test(service)
                        probe_duration.labels(
                            probe=probe_name,
                            target=target
                        ).set(time() - start_time)
                    except Exception as probe_exception:
                        self.log.exception(
                            "Exception %s in thread %s",
                            str(probe_exception),
                            self.config_path
                        )
                        probes_results = [
                            Message(
                                probe_name,
                                "Exception: {}".format(probe_exception),
                                Message.ERROR
                            )
                        ]

                    if not probes_results:
                        probe_success_total.labels(
                            probe=probe_name,
                            target=target
                        ).inc()
                        break

                    probe_failures_total.labels(
                        probe=probe_name,
                        target=target
                    ).inc()

                    self.log.info(
                        "%s probe for %s returns %s",
                        probe_name,
                        str(service),
                        str(probes_results)
                    )
                    sleep(1)

                notifications += probes_results

        # Sort notifications by severity
        notifications.sort(key=lambda x: x.severity, reverse=True)

        # Log notifications messages
        if notifications:
            for message in notifications:
                if message.severity == Message.WARNING:
                    self.log.warning("%s: %s", message.service, message.body)
                elif message.severity == Message.ERROR:
                    self.log.error("%s: %s", message.service, message.body)
                else:
                    pass
        else:
            self.log.info("All services are up")

        # Send notifications
        if send_notification:
            self.send_notification(notifications=notifications)

    def manage_notifications(self, notifications):
        """
        This method reorganizes notifications: don't send notification
        already sent and add notification for services back online.

        Parameters:
        notifications: (list of Message object) notifications from self.monitor

        Return:
        (list of Messages object) notification to send
        """

        notifications_to_send = []

        # Check if notification was already sent
        for message in notifications:
            if message not in self.down_services:
                notifications_to_send.append(message)
                self.down_services.append(message)

        # Add notification for services which are back online
        for sent_message in list(self.down_services):
            if sent_message not in notifications:
                notifications_to_send.append(
                    Message(
                        sent_message.service,
                        sent_message.body,
                        sent_message.severity,
                        header='back online'
                    )
                )
                self.down_services.remove(sent_message)
                self.log.info("[service online] %s", str(sent_message))
            else:
                self.log.warning("[service down] %s", str(sent_message))

        return notifications_to_send

    def send_notification(self, notifications):
        """
        This method is called only if send_notification is True
        and notifications is not empty.
        It will send notifications after calling self.manage_notifications.
        """

        # Reorganize notifications (see self.manage_notifications)
        notifications_to_send = self.manage_notifications(notifications)

        if notifications_to_send:

            # Build message body
            message_body = ""

            for message in notifications_to_send:
                message_body += "{}\n---\n".format(message)

            # Send the email
            mail_sent = email.send_email(
                subject="Monitoring alert!",
                body=message_body,
                smtp_config=self.config['notifications']['email']['config']
            )

            if mail_sent:
                self.log.info("Notification mail sent")
            else:
                self.log.error("Fail to send notification mail")

        else:
            self.log.debug("notifications_to_send is empty")


if __name__ == '__main__':

    # Parse arguments
    parser = argparse.ArgumentParser(description="Services Monitoring")
    parser.add_argument(
        '-c', '--config',
        help="Path to config file"
    )
    args = parser.parse_args()

    # Print version at startup
    print("Services Monitoring V{}".format(version))

    # Handle signal
    def exit_gracefully(sigcode, _frame):
        """
        Exit immediately gracefully
        """
        services_monitoring.log.info("Signal %d received", sigcode)
        services_monitoring.log.info("Exiting gracefully now...")
        services_monitoring.exit_event.set()
        sys_exit(0)
    signal.signal(signal.SIGINT, exit_gracefully)
    signal.signal(signal.SIGTERM, exit_gracefully)

    # Start Imap2Smtp thread
    services_monitoring = ServicesMonitoring(
        config_path=args.config
    )
    services_monitoring.start()

    while True:
        if not services_monitoring.is_alive():
            break
        sleep(600)
    sys_exit(1)
