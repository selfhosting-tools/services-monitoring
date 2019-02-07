# Author: alex2242

"""
Tests for the ping probe
"""

import unittest
from probes.ping import Ping


class TestPing(unittest.TestCase):
    """
    Unittest class for test on ping
    """

    def test_local(self):
        """
        Tests ping over localhost, should suceed
        """
        ping = Ping("127.0.0.1")
        result = ping.test()
        self.assertEqual(len(result), 0)

    def test_domain(self):
        """
        Test ping google.fr, also tests DNS resolution
        """
        ping = Ping("google.fr")
        result = ping.test()
        self.assertEqual(len(result), 0)
