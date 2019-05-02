# Author: FL42

"""
Tests for the message module
"""

import unittest
from tools import Message


class TestMessage(unittest.TestCase):
    """
    See module docstring
    """

    def test_message_creation(self):
        """
        Test message creation
        """
        message = Message('Service name', 'Message body', Message.ERROR)
        self.assertTrue(message.service == 'Service name')
        self.assertTrue(message.body == 'Message body')
        self.assertTrue(message.severity == Message.ERROR)

    def test_message_equality(self):
        """
        Test message equality
        2 Message objects with same values should be equal
        """
        message1 = Message('Service name', 'Message body', Message.ERROR)
        message2 = Message('Service name', 'Message body', Message.ERROR)
        self.assertTrue(message1 == message2)

    def test_message_not_equal(self):
        """
        Test message not equal
        """
        message1 = Message('Service name', 'Message body', Message.ERROR)
        message2 = Message('Service name 2', 'Message body', Message.ERROR)
        self.assertTrue(message1 != message2)

    def test_message_in_list(self):
        """
        Test 'in' primitive in Python is working as expected
        with Message object.
        """
        message = Message('Service name', 'Message body', Message.ERROR)
        messages = [
            Message('Service name', 'Message body', Message.ERROR),
            Message('Service name 2', 'Message body 2', Message.ERROR)
        ]
        self.assertTrue(message in messages)

    def test_message_in_not_list(self):
        """
        Test 'in' primitive in Python is working as expected
        with Message object.
        """
        message = Message('Service name 0', 'Message body', Message.ERROR)
        messages = [
            Message('Service name 1', 'Message body 1', Message.ERROR),
            Message('Service name 2', 'Message body 2', Message.ERROR)
        ]
        self.assertTrue(message not in messages)

    def test_str(self):
        """
        Test __str__ method
        """
        message = Message(
            'Service name 0',
            'Message body',
            Message.ERROR
        )
        self.assertTrue(str(message) == "Service name 0: Message body")

    def test_str_header(self):
        """
        Test __str__ method with header set
        """
        message = Message(
            'Service name 0',
            'Message body',
            Message.ERROR,
            header='Header'
        )
        self.assertTrue(
            str(message) == "[Header] Service name 0: Message body"
        )

    def test_repr(self):
        """
        Test __repr__ method
        """
        message = Message(
            'Service name 0',
            'Message body',
            Message.ERROR
        )
        self.assertTrue(
            repr(message) ==
            "Message: service: Service name 0, body: Message body, "
            "severity: 40, header: None"
        )
