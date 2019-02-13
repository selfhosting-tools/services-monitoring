# Author: FL42

"""
Tests for the ping probe
"""

import unittest
from probes import ping


class TestPing(unittest.TestCase):
    """
    Unittest class for test on ping
    """

    def test_ping_local(self):
        """
        Should work
        """
        results = ping.test("127.0.0.1")
        self.assertTrue(not results)

    def test_ping_ip(self):
        """
        Test ping an IP (Google public DNS)
        """
        results = ping.test("8.8.8.8")
        self.assertTrue(not results)

    def test_ping_domain(self):
        """
        Test ping google.fr (needs a working system DNS resolution)
        """
        results = ping.test("google.fr")
        self.assertTrue(not results)

    def test_ping_invalid_ip(self):
        """
        Test invalid IP
        """
        results = ping.test("500.500.500.500")
        self.assertTrue(results)

    def test_ping_not_reachable_ip(self):
        """
        "10.255.10.255" is unlikely alive
        """
        results = ping.test("10.255.10.255")
        self.assertTrue(results)
