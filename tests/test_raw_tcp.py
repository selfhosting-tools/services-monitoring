# Author: FL42

"""
Tests for the raw_tcp probe
"""

import unittest
from probes import raw_tcp


class TestRawTCP(unittest.TestCase):
    """
    See module docstring
    """

    def test_open(self):
        """
        Should work
        """
        result = raw_tcp.test({'host': 'google.fr', 'port': 443})
        self.assertEqual(len(result), 0)

    def test_close(self):
        """
        Should not work (port closed)
        """
        result = raw_tcp.test({'host': 'google.fr', 'port': 444})
        self.assertTrue(len(result) > 0)

    def test_invalid_hostname(self):
        """
        Should not work (invalid hostname)
        """
        result = raw_tcp.test({'host': '', 'port': 443})
        self.assertTrue(len(result) > 0)

    def test_invalid_port(self):
        """
        Should not work (invalid port)
        """
        result = raw_tcp.test({'host': 'google.fr', 'port': 102548})
        self.assertTrue(len(result) > 0)
