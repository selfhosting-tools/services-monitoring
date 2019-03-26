#!/usr/bin/env python3

# Authors: alex2242 & FL42

"""
usage: monitoring.py [-h] [-d] [-c CONFIG] [-n]

Services monitoring

optional arguments:
  -h, --help            show this help message and exit
  -d, --debug           Set log_level to DEBUG (default to INFO)
  -c CONFIG, --config CONFIG
                        Path to config file
  -n, --no-notification
                        Don't send notification messages
"""

import argparse
import logging as log
from time import sleep

import yaml

from notification import email
from probes import dns, https, ping, raw_tcp, smtp
from tools import Message

version = "0.1"


class ServicesMonitoring():
    """
    See module docstring.
    """

    # Mapping between strings and python modules
    probe_mapping = {
        'ping': ping,
        'raw_tcp': raw_tcp,
        'smtp': smtp,
        'https': https,
        'dns': dns
    }

    def __init__(self, config_path):

        # Parse config
        if config_path is not None:
            with open(config_path, 'rt') as config_file:
                self.config = yaml.safe_load(config_file)
        else:
            raise Exception('Path to config is required')

        # Set up logger
        log.basicConfig(
            format="[{}] %(asctime)s:%(levelname)s:%(message)s".format(
                config_path
            ),
            datefmt='%Y-%m-%d %H:%M:%S',
            level=log.DEBUG if self.config['common'].get('debug', False)
            else log.INFO
        )
        log.debug(self.config)

        # Disable notifications if section is not defined
        send_notification = 'notifications' in self.config

        # Store sent messages (prevent duplicate notifications)
        self.down_services = []

        # Call self.monitor every 'delay' sec
        while True:
            self.monitor(send_notification=send_notification)
            log.debug("Waiting...")
            sleep(self.config['common']['delay'])

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
            probe_module = ServicesMonitoring.probe_mapping[probe_name]
            for service in config_probes[probe_name]:
                log.debug("%s probe for %s", probe_name, str(service))
                # Retry probe one time in case of error or warning
                # to avoid notification on one-time error.
                for _ in range(2):
                    probes_results = probe_module.test(service)
                    if not probes_results:
                        break
                    log.info(
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
                    log.warning("%s: %s", message.service, message.body)
                elif message.severity == Message.ERROR:
                    log.error("%s: %s", message.service, message.body)
                else:
                    pass
        else:
            log.info("All services are up")

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
                log.info("[service online] %s", str(sent_message))
            else:
                log.warning("[service down] %s", str(sent_message))

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
                config=self.config['notifications']['email']['config']
            )

            if mail_sent:
                log.info("Notification mail sent")
            else:
                log.error("Fail to send notification mail")

        else:
            log.debug("notifications_to_send is empty")


if __name__ == '__main__':

    # Parse arguments
    parser = argparse.ArgumentParser(description="Services monitoring")
    parser.add_argument('-c', '--config',
                        help="Path to config file")
    args = parser.parse_args()

    # Print version at startup
    print("Services Monitoring V{}".format(version))

    # Instantiate ServicesMonitoring class
    services_monitoring = ServicesMonitoring(
        config_path=args.config
    )
