# Author: FL42

"""
Tests for main file
"""

import unittest

from src.monitoring import ServicesMonitoring
from src.tools import Message


class TestNotificationManagementLogic(unittest.TestCase):
    """
    Test self.manage_notifications()
    """

    def setUp(self):
        """
        Instantiate ServicesMonitoringTest class
        """
        self.services_monitoring = ServicesMonitoring('unittest')

    def test_one_notification(self):
        """
        Test with one notification
        """
        message1 = Message('Service 1', 'Message 1', Message.ERROR)
        notifications = [message1]
        self.services_monitoring.down_services = []

        notifications_to_send = \
            self.services_monitoring.manage_notifications(notifications)

        self.assertTrue(notifications_to_send == [message1])
        self.assertTrue(
            self.services_monitoring.down_services == [message1]
        )

    def test_few_notifications(self):
        """
        Test with few notifications
        """
        message1 = Message('Service 1', 'Message 1', Message.ERROR)
        message2 = Message('Service 2', 'Message 2', Message.ERROR)
        notifications = [message1, message2]
        self.services_monitoring.down_services = []

        notifications_to_send = \
            self.services_monitoring.manage_notifications(notifications)

        self.assertTrue(notifications_to_send == [message1, message2])
        self.assertTrue(
            self.services_monitoring.down_services == [message1, message2]
        )

    def test_back_online(self):
        """
        Test if a service was down but it's now up
        """
        message1 = Message('Service 1', 'Message 1', Message.ERROR)
        expected_notifications = [
            Message(
                'Service 1',
                'Message 1',
                Message.ERROR,
                'back online'
            )
        ]
        notifications = []
        self.services_monitoring.down_services = [message1]

        notifications_to_send = \
            self.services_monitoring.manage_notifications(notifications)

        self.assertTrue(notifications_to_send == expected_notifications)
        self.assertTrue(not self.services_monitoring.down_services)

    def test_back_online_multiple_services(self):
        """
        Test if services were down but are now up
        """
        message1 = Message('Service 1', 'Message 1', Message.ERROR)
        message2 = Message('Service 2', 'Message 2', Message.ERROR)
        message3 = Message('Service 3', 'Message 3', Message.WARNING)
        expected_notifications = [
            Message(
                'Service 1',
                'Message 1',
                Message.ERROR,
                'back online'
            ),
            Message(
                'Service 2',
                'Message 2',
                Message.ERROR,
                'back online'
            )
        ]
        notifications = [message3]
        self.services_monitoring.down_services = [message1, message2, message3]

        notifications_to_send = \
            self.services_monitoring.manage_notifications(notifications)

        self.assertTrue(notifications_to_send == expected_notifications)
        self.assertTrue(
            self.services_monitoring.down_services == [message3]
        )

    def test_still_down(self):
        """
        Test if a service is still down
        """
        message1 = Message('Service 1', 'Message 1', Message.ERROR)
        notifications = [message1]
        self.services_monitoring.down_services = [message1]

        notifications_to_send = \
            self.services_monitoring.manage_notifications(notifications)

        self.assertTrue(not notifications_to_send)
        self.assertTrue(
            self.services_monitoring.down_services == [message1]
        )

    def test_still_down_multiple_services(self):
        """
        Test if a service is still down with multiple services
        """
        message1 = Message('Service 1', 'Message 1', Message.ERROR)
        message2 = Message('Service 2', 'Message 2', Message.ERROR)
        notifications = [message1, message2]
        self.services_monitoring.down_services = [message1]

        notifications_to_send = \
            self.services_monitoring.manage_notifications(notifications)

        self.assertTrue(notifications_to_send == [message2])
        self.assertTrue(
            self.services_monitoring.down_services == [message1, message2]
        )
