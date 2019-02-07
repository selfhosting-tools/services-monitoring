# Author: FL42

"""
Tests for the smtp probe
"""

import unittest
from probes import smtp


class Testsmtp(unittest.TestCase):
    """
    See module docstring
    """

    def test_valid_smtp(self):
        """
        Should work
        """
        results = smtp.test({
            'host': 'smtp.gmail.com',
            'port': 25,
            'check_tlsa': False
        })

        self.assertEqual(len(results), 0)

    def test_valid_tlsa(self):
        """
        Should work (TLSA check)
        """
        results = smtp.test({
            'host': 'mail.ietf.org',
            'port': 25,
            'check_tlsa': True
        })

        self.assertEqual(len(results), 0)

    def test_invalid_smtp(self):
        """
        Should not work (invalid domain)
        """
        results = smtp.test({
            'host': 'mail.example.com',
            'port': 25,
            'check_tlsa': False
        })

        self.assertTrue(len(results) > 0)
